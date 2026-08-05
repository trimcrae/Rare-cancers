#!/usr/bin/env python3
"""The EMC systems model — invariant checker and view generator. ($0, pure stdlib)

    python3 systems/systems_check.py --check         run every invariant; fail red
    python3 systems/systems_check.py --write-views   regenerate systems/views/**

⛔ WHY THE VIEWS ARE GENERATED AND NOT WRITTEN. Prose drifts and cannot be checked. A generated view
cannot drift without failing the build, because `--check` re-renders every view IN MEMORY and compares
it to what is committed. This is the pattern `emc_systems_map_check.py` already proved here; this module
extends it from one registry to the whole navigational surface.

⛔ WHY THIS FAILS RED AND NEVER QUIET. Several parsers in this repository print a message and exit 0
when they cannot find what they parse. A guard that fails open leaves no trace, and during a restructure
it is the most dangerous behaviour there is: the model would silently stop being read and every build
would stay green. Every failure here is an ERROR and every ERROR sets the exit code.

THE GRAPH IS THE SOURCE. systems/graph/*.json is the one home of every fact this module renders. It
asserts no grade and no number of its own -- it records where each already lives, checks the pointer
resolves, and refuses the combinations the register's own rules forbid.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GRAPH = os.path.join(HERE, "graph")
SCHEMA = os.path.join(HERE, "schema")
VIEWS = os.path.join(HERE, "views")

COLLECTIONS = [
    "strategies", "routes", "requirements", "blockers", "technologies", "forecasts",
    "instruments", "objects", "evidence", "artifacts", "claims", "roadmap",
    # ⭐ LANES — the level the model was missing. A ROUTE is a strategic option ("could we do X?"),
    # a REQUIREMENT is "what must be TRUE", and a LANE is "we RAN X, and here is how it ended".
    # Executed work had no object, so its state lived only as ~~strikethrough~~ in roadmap prose.
    # Prose is not queryable: that is how an artifact belonging to a lane which CLOSED on 2026-07-30
    # was read as a gap to fill on 2026-08-05, at a cost of 88.5 minutes of CI.
    "lanes",
]

# A blocker of this kind is a fact about what the objects ARE. It is not waiting on anything,
# so it may carry no technology dependency and must appear on no watch list.
PERMANENT_KINDS = {"fundamental_biological_limit"}

# An instrument in any of these control states may never be listed as SUPPORT. `none` is included
# deliberately: "no control exists" and "the control failed" are different facts, and neither is support.
#
# ⭐ `mixed` ADDED 2026-08-05, and it ADDS a warning rather than removing one. It was the only value of
# `known_answer_control.state` never enumerated in a schema, and it silently counted as SUPPORTING. Its
# two instances are V19 — "PARTIAL — the arm that addresses the GENERATIVE step is unrun" — and V15 —
# "one of the five nulls does not support it". Neither has returned a usable answer, and a repository
# whose stated rule is ⛔ NO VAGUE STATES cannot keep a control state that means "partly". R1 (V13
# fails, V14 none, V15 mixed) consequently gains the [Q4] it should always have carried.
NON_SUPPORTING_CONTROL = {"fails", "none", "inconclusive", "mixed"}

#: Requirement ids sort numerically (R2 before R13), not lexically. Anything unrecognised sorts last
#: rather than raising — a sort key is not the place to discover a malformed id, the schema is.
def _req_sort(x):
    return (0, int(x[1:])) if x[:1] == "R" and x[1:].isdigit() else (1, 0)


#: Instrument ids across BOTH namespaces: `V\d+` numerically first, then `INS-*` alphabetically.
#: The two namespaces are real — `V*` are the program-map instrument table's, `INS-*` the systems
#: map's — and mixing their sort orders is what makes a stored list disagree with a regenerated one.
def _req_sort_inst(x):
    return (0, int(x[1:]), "") if x[:1] == "V" and x[1:].isdigit() else (1, 0, x)


# ───────────────────────────── findings ─────────────────────────────

class Findings:
    """Three severities, and the third one is the point.

    ⭐ WHY `info` EXISTS (2026-08-05). A check that reports a STATED SCOPE BOUNDARY as a warning is
    miscalibrated, and the cost is not cosmetic: [Q3] warned identically about R6 (a computable term
    nobody has computed -- a work item) and about R4, whose own note reads "⛔ none -- needs a bench"
    against a program that has no wet lab. A permanent warning for a decision already taken is how a
    reader learns to skim the warning list, which is exactly what the 88.5-minute valB incident cost.
    So a finding that is TRUE, DELIBERATE and CLOSED is reported once, visibly, and does not accrue.

    ⚠ `info` is NOT a quieter warning. Nothing may be demoted to it because it is inconvenient -- the
    only qualifying findings are ones the model can point at a recorded decision for.
    """

    def __init__(self):
        self.errors: list[str] = []
        self.warns: list[str] = []
        self.infos: list[str] = []

    def err(self, code, msg):
        self.errors.append(f"{code}  {msg}")

    def warn(self, code, msg):
        self.warns.append(f"{code}  {msg}")

    def info(self, code, msg):
        self.infos.append(f"{code}  {msg}")

    @property
    def ok(self):
        return not self.errors


class SchemaSet:
    """Every schema in `systems/schema/`, validated with the reference implementation.

    ⛔ THIS REPLACED A HAND-ROLLED SUBSET VALIDATOR, AND THE REASON IS THE ONE THIS REPO CARES MOST
    ABOUT. The previous `MiniValidator` implemented fourteen JSON Schema keywords — exactly the fourteen
    our schemas happened to use — and SILENTLY IGNORED the rest. It was not under-validating anything on
    the day it was written. It was a trap: the first time anyone wrote `oneOf`, `minimum`, `uniqueItems`,
    `maxItems`, `format` or any of ten others, the constraint would be accepted, LOOK enforced, and do
    nothing, with no error and no warning.

    That is the same shape as every other defect this model has had to fix — a check that reports success
    while not covering what a reader assumes it covers. `parser_guard.py` exists because a parser that
    exits 0 on input it cannot read is invisible from CI. A validator that accepts a keyword it does not
    implement is worse: it does not even report its own blindness.

    ⚠ THE ARGUMENTS FOR HAND-ROLLING IT WERE BOTH WRONG, and are recorded because the reasoning was
    plausible. (1) "Pure stdlib" was never a repository constraint — CI already installs pytest, numpy,
    scipy, pymbar, rdkit, pyyaml and boto3, so `jsonschema` is one word on an existing line. (2)
    CLAUDE.md §6 was cited about not building environments on machines we pay for. Schema validation runs
    on a free CI runner and in a free sandbox. Invoking a COST rule against a ZERO-COST operation is the
    same misapplied-rule error the §6 rewrite itself was written to stop.

    ⛔ A MISSING DEPENDENCY FAILS LOUDLY. There is deliberately no fallback to a weaker validator: a
    silent downgrade is the fail-open pattern this file spends thirty checks removing.
    """

    def __init__(self, schema_dir):
        try:
            from jsonschema import Draft202012Validator
        except ImportError as e:                                   # pragma: no cover - env only
            raise SystemExit(
                "systems_check needs `jsonschema` (the reference implementation of the standard the "
                "schemas in systems/schema/ are written against).\n"
                "    pip install jsonschema\n"
                "⛔ There is no fallback on purpose. A hand-rolled subset validator silently ignores "
                "every keyword it does not implement, which is worse than not validating at all — the "
                "schema still reads as enforced. (%s)" % e)
        self._V = Draft202012Validator
        self.docs = {}
        for fn in sorted(os.listdir(schema_dir)):
            if fn.endswith(".json"):
                with open(os.path.join(schema_dir, fn), encoding="utf-8") as fh:
                    self.docs[fn] = json.load(fh)
        # ⚠ Resolve $ref ACROSS files. The schemas genuinely cross-reference — every route/strategy/
        # blocker $refs research-object.schema.json — so a registry is required, not optional.
        from referencing import Registry, Resource
        self._registry = Registry().with_resources(
            [(d.get("$id", fn), Resource.from_contents(d)) for fn, d in self.docs.items()]
            + [(fn, Resource.from_contents(d)) for fn, d in self.docs.items()])

    def check_schemas_are_themselves_valid(self, f):
        """⭐ THE CHECK THE HAND-ROLLED ONE COULD NOT DO AT ALL: is the SCHEMA itself well-formed?

        A typo in a schema — `"minimun"`, `"enum"` spelled as a list where an object was meant — used to
        be accepted in silence, because an unknown keyword was simply skipped. The reference
        implementation checks a schema against the metaschema, so a malformed constraint is now an error
        rather than an inert line that reads as a rule.
        """
        # ⚠ `check_schema` RAISES on the first problem. A checker that dies on a malformed schema tells
        # you about one file and nothing about the rest, so the metaschema is applied as an ordinary
        # validation and every problem is COLLECTED — the same reason this whole file reports findings
        # instead of asserting.
        meta = self._V(self._V.META_SCHEMA)
        for fn, doc in sorted(self.docs.items()):
            for err in meta.iter_errors(doc):
                where = "/".join(str(x) for x in err.absolute_path) or "(root)"
                f.err("[S0]", f"{fn} is not a valid JSON Schema at {where}: {err.message[:160]}")

    def validate(self, instance, schema, doc=None):
        """Every violation, as a stable sorted list of human-readable strings.

        ⚠ `doc` IS THE RESOLUTION SCOPE AND IT IS NOT OPTIONAL FOR A SUBSCHEMA. Several of our schemas
        are validated at a `$defs` member — `technology.schema.json#/$defs/forecast` — and that member
        contains its own `#/$defs/scenario` refs. Handing the member to a validator as its ROOT makes
        those refs point at nowhere inside it. So the validator is built on the whole document and then
        `evolve`d onto the member, which keeps the document as the base for every internal `$ref`.
        (The hand-rolled validator hid this by resolving refs against a separately-passed doc, which
        worked and taught nobody that the scope mattered.)
        """
        v = self._V(doc if doc is not None else schema, registry=self._registry).evolve(schema=schema)
        out = []
        for e in v.iter_errors(instance):
            where = "/".join(str(x) for x in e.absolute_path) or "(root)"
            out.append(f"{where}: {e.message}")
        return sorted(set(out))


def load_graph():
    g = {}
    for name in COLLECTIONS:
        path = os.path.join(GRAPH, f"{name}.json")
        if not os.path.exists(path):
            g[name] = []
            continue
        with open(path, encoding="utf-8") as fh:
            g[name] = json.load(fh)
    plan = os.path.join(GRAPH, "plan.json")
    g["plan"] = json.load(open(plan, encoding="utf-8")) if os.path.exists(plan) else {}
    integ = os.path.join(GRAPH, "integrity.json")
    g["integrity"] = json.load(open(integ, encoding="utf-8")) if os.path.exists(integ) else {}
    return g


def by_id(rows):
    return {r["id"]: r for r in rows}


# ───────────────────────────── derivations ─────────────────────────────
# Everything here is COMPUTED from the graph and never stored, so the same edge can never be
# written in two places and disagree with itself.

def derive(g):
    routes, blockers = g["routes"], g["blockers"]
    techs, strategies = g["technologies"], g["strategies"]

    # strategy -> its routes
    fam = defaultdict(list)
    for r in routes:
        if r.get("strategy"):
            fam[r["strategy"]].append(r["id"])
    for s in strategies:
        s["routes"] = sorted(fam.get(s["id"], []))

    # blocker -> routes that inherit / retire it
    inh, ret = defaultdict(list), defaultdict(list)
    for r in routes:
        for b in r.get("blockers_inherited", []):
            inh[b].append(r["id"])
        for b in r.get("blockers_retired", []):
            ret[b].append(r["id"])

    # blocker -> technologies that would retire it
    tech_for = defaultdict(list)
    for t in techs:
        for b in t.get("unblocks", {}).get("blockers", []):
            tech_for[b].append(t["id"])

    for b in blockers:
        b["inherited_by"] = sorted(inh.get(b["id"], []))
        b["retired_by"] = sorted(ret.get(b["id"], []))
        b["retired_by_technology"] = sorted(tech_for.get(b["id"], []))
        b["permanent"] = b.get("kind") in PERMANENT_KINDS

    # technology fan-out: how much comes back if it lands
    for t in techs:
        u = t.get("unblocks", {})
        t["fan_out"] = len(set(u.get("routes", []))) + len(set(u.get("requirements", []))) \
            + len(set(u.get("instruments", []))) + len(set(u.get("blockers", [])))

    # ── the SysML `verify` relation: ONE asserted direction, ONE derived inverse ──────────────
    #
    # ⭐ WHY THIS SHAPE, AND WHAT IT REPLACED (2026-08-05). The model used to carry THREE fields for
    # this one relation: `requirement.served_by` (asserted), `instrument.serves` (asserted, the same
    # edge written from the other end) and `instrument.serves_derived` (computed here, and read
    # NOWHERE). Two asserted homes for one fact is rule 1's exact failure mode, and it had already
    # failed: 11 of 30 instruments disagreed with the requirement register, six of them holding free
    # PROSE rather than identifiers. The visible symptom was a warning the model itself contradicted
    # — [Q3] reported "R13 has NO instrument at all" while two instruments claimed to serve R13 and
    # R13's own note said "an instrument EXISTS and is staged".
    #
    # SysML's `verify` (a test case verifies a requirement) has exactly one asserted direction and one
    # derived inverse, which is why adopting it is the fix rather than a rename. The requirement
    # register keeps the assertion because the roadmap's §2.1 table mirrors it and
    # check_requirement_source_agreement parses it; `verifies` is derived and may never be written.
    inst_verifies = defaultdict(list)
    for r in g.get("requirements", []):
        for v in r.get("verified_by", []):
            inst_verifies[v].append(r["id"])
    # ⚠ `allocate` — instrument → route — is likewise DERIVED, from the edge routes already assert.
    # The six prose values deleted from `serves` were paraphrases of THIS edge, in a second file,
    # where nothing read them; the route edge is a better home because it distinguishes support from
    # disclosed failure, which the prose managed for only one of the six.
    inst_alloc = defaultdict(dict)
    for r in routes:
        for kind, vals in (r.get("instruments") or {}).items():
            for v in vals:
                inst_alloc[v].setdefault(kind, []).append(r["id"])
    for i in g["instruments"]:
        i["verifies"] = sorted(inst_verifies.get(i["id"], []), key=_req_sort)
        i["allocated_to"] = {k: sorted(v) for k, v in sorted(inst_alloc.get(i["id"], {}).items())}

    # ⭐ USABILITY IS TRANSITIVE, AND THE CONTROL STATE ALONE DOES NOT SETTLE IT (found 2026-08-05
    # during the reconciliation). INS-MONOVALENT-REACH PASSES its own known-answer control — its
    # bivalent half replicates the committed artifact cell-for-cell — and its own note still says it
    # "can refute a route and cannot license one", because it inherits V3's INCONCLUSIVE site question
    # and V17's defective exposure cutoff. A usability test that read only `known_answer_control.state`
    # would have called it supporting and silently cleared R8's [Q4]. So the inheritance is modelled
    # (`inherits_limits_from`, SysML `derive`) and usability is computed through it.
    inst = by_id(g["instruments"])

    def _usable(iid, seen=None):
        i = inst.get(iid)
        if i is None:
            return False
        seen = seen or set()
        if iid in seen:                       # a cycle cannot license anything
            return False
        if (i.get("known_answer_control") or {}).get("state") in NON_SUPPORTING_CONTROL:
            return False
        return all(_usable(p, seen | {iid}) for p in i.get("inherits_limits_from", []))

    for i in g["instruments"]:
        i["usable"] = _usable(i["id"])

    # family-level blocker structure
    rid = by_id(routes)
    for s in strategies:
        sets = [set(rid[r].get("blockers_inherited", [])) for r in s["routes"] if r in rid]
        s["shared_blockers"] = sorted(set.intersection(*sets)) if sets else []
        s["distinguishing_blockers"] = sorted(
            {b for r in s["routes"] if r in rid for b in rid[r].get("blockers_retired", [])})
        st = [rid[r].get("state", {}).get("status") for r in s["routes"] if r in rid]
        s["summary_state"] = {
            "n_routes": len(s["routes"]),
            "n_open": sum(1 for x in st if x in ("active", "ready", "blocked")),
            "n_parked": sum(1 for x in st if x == "parked"),
            "n_closed": sum(1 for x in st if x == "closed"),
        }
    return g


# ───────────────────────────── invariants ─────────────────────────────

def check_schemas(g, f):
    mv = SchemaSet(SCHEMA)
    mv.check_schemas_are_themselves_valid(f)
    pairs = [("strategies", "strategy.schema.json"),
             ("routes", "route.schema.json"),
             ("blockers", "blocker.schema.json")]
    for coll, sch in pairs:
        schema = mv.docs[sch]
        for row in g[coll]:
            for msg in mv.validate(row, schema, schema):
                f.err("[S1]", f"{coll}/{row.get('id','?')} {msg}")

    # ⛔ `requirements` AND `instruments` WERE THE UNSCHEMA'D PAIR UNTIL 2026-08-05, and that is not a
    # coincidence — it is where the untyped relation between them lived. `instrument.serves` held
    # "R13" beside "the ATR route's structural precondition" and nothing could tell them apart.
    for coll, key in [("lanes", "lane"), ("requirements", "requirement"), ("instruments", "instrument")]:
        doc = mv.docs[f"{key}.schema.json"]
        for row in g[coll]:
            for msg in mv.validate(row, doc["$defs"][key], doc):
                f.err("[S3]", f"{coll}/{row.get('id','?')} {msg}")

    tech_schema = mv.docs["technology.schema.json"]["$defs"]["technology"]
    for row in g["technologies"]:
        for msg in mv.validate(row, tech_schema, mv.docs["technology.schema.json"]):
            f.err("[S2]", f"technologies/{row.get('id','?')} {msg}")

    fc_schema = mv.docs["technology.schema.json"]["$defs"]["forecast"]
    for row in g["forecasts"]:
        for msg in mv.validate(row, fc_schema, mv.docs["technology.schema.json"]):
            f.err("[S3]", f"forecasts/{row.get('id','?')} {msg}")


def check_ids_unique(g, f):
    seen = {}
    for coll in COLLECTIONS:
        for row in g[coll]:
            rid = row.get("id")
            if rid in seen:
                f.err("[I1]", f"id {rid} appears in both {seen[rid]} and {coll}")
            seen[rid] = coll


def check_hierarchy(g, f):
    """L1 must partition L2: every route in exactly one family, both directions agreeing."""
    sid = {s["id"] for s in g["strategies"]}
    claimed = defaultdict(list)
    for r in g["routes"]:
        s = r.get("strategy")
        if not s:
            f.err("[H1]", f"{r['id']} has no strategy -- every route belongs to exactly one L1 family")
        elif s not in sid:
            f.err("[H1]", f"{r['id']} claims unknown strategy {s}")
        else:
            claimed[s].append(r["id"])
    for s in g["strategies"]:
        listed, actual = set(s.get("routes", [])), set(claimed.get(s["id"], []))
        if listed != actual:
            f.err("[H2]", f"{s['id']} route set disagrees with routes' own claims: "
                          f"only-in-family={sorted(listed-actual)} only-in-routes={sorted(actual-listed)}")
        if not actual:
            f.err("[H3]", f"{s['id']} has no routes -- an empty family is a category, not a strategy")


def check_blockers(g, f):
    for b in g["blockers"]:
        perm, tech = b["permanent"], b["retired_by_technology"]
        act = b.get("retired_by_action")
        if perm and tech:
            f.err("[B1]", f"{b['id']} is permanent ({b['kind']}) but {tech} claims to retire it -- "
                          f"a fact about what the objects ARE is not waiting on a capability")
        if not perm and not tech and not act:
            f.err("[B2]", f"{b['id']} ({b['kind']}) is not permanent and names neither a technology nor "
                          f"an action that would retire it -- it is mis-typed or under-analysed, and both need saying")
        if not b["inherited_by"] and not perm:
            f.warn("[B3]", f"{b['id']} holds down no route -- it may be retired or mis-scoped")

    known = {b["id"] for b in g["blockers"]}
    for r in g["routes"]:
        for b in r.get("blockers_inherited", []) + r.get("blockers_retired", []):
            if b not in known:
                f.err("[B4]", f"{r['id']} references unknown blocker {b}")
    for t in g["technologies"]:
        for b in t.get("unblocks", {}).get("blockers", []):
            if b not in known:
                f.err("[B5]", f"{t['id']} claims to unblock unknown blocker {b}")


def check_technologies(g, f):
    fc = by_id(g["forecasts"])
    for t in g["technologies"]:
        ref = t.get("forecast")
        if ref not in fc:
            f.err("[T1]", f"{t['id']} names forecast {ref} which does not exist")
        elif fc[ref].get("tech_ref") != t["id"]:
            f.err("[T1]", f"{t['id']} <-> {ref} back-reference disagrees")
        if t.get("current_state") != "absent" and not t.get("evidence"):
            f.err("[T2]", f"{t['id']} is {t.get('current_state')} with no evidence -- a state that is not "
                          f"`absent` is a claim about the world and needs its basis")
        # ⛔ `not_scannable_because` IS AN ANSWER, NOT AN ESCAPE HATCH. Some dependencies genuinely
        # cannot be seen by a literature search -- the price of a GPU-hour is measured from a market
        # board, not read in a paper -- and pressing for a query anyway would produce a fabricated one
        # that reports nothing forever while being credited as coverage. That is strictly worse than a
        # declared gap: the credit is what stops anyone checking (MAINTENANCE.md section 4).
        if not t.get("scan_trigger") and not t.get("not_scannable_because"):
            f.warn("[T3]", f"{t['id']} has no scan trigger -- nothing is searching for it, so it could "
                           f"land without anyone noticing. If it genuinely cannot be found by a "
                           f"literature search, say so in `not_scannable_because` and name what "
                           f"watches it instead")
        if not t.get("fan_out"):
            f.warn("[T4]", f"{t['id']} unblocks nothing -- why is it registered?")

    for c in g["forecasts"]:
        if c.get("tech_ref") not in by_id(g["technologies"]):
            f.err("[T5]", f"{c['id']} points at unknown technology {c.get('tech_ref')}")
        sc = c.get("scenarios", {})
        bands = [sc.get(k, {}).get("date_band") for k in ("conservative", "expected", "optimistic")]
        if len(set(b for b in bands if b)) == 1:
            f.warn("[T6]", f"{c['id']} has all three scenarios in the same band -- either the capability "
                           f"is nearly here or the forecast has not been thought about; both need saying")


def _owner_blocks(node, path=()):
    """Every `{file, anchor}` pair anywhere in a row, at any depth.

    ⛔ IT USED TO LOOK IN EXACTLY TWO PLACES — `row["owner"]` and `row["provenance"]["owner"]` — and
    the model puts them in more than two. `RT-FAP-RLT.grade.owner` asserts
    `emerging-modalities-scan-emc.md#2`; the real heading is "## 2. FAP-targeted radioligand therapy
    (FAPI-RLT) — emerging, plausibly applies", whose slug is nothing like `2`. [P2] never looked, and
    the generated L2 view rendered the bad anchor into a link that [K1] then declared fine because it
    stripped the fragment. THREE checks in a row each verified the half they could see.
    """
    if isinstance(node, dict):
        if isinstance(node.get("file"), str):
            yield "/".join(path), node
        for k, v in node.items():
            yield from _owner_blocks(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _owner_blocks(v, path + (str(i),))


def check_pointers(g, f):
    """Every {file} exists on disk, and every anchor beside one is a real slug in it."""
    for coll in COLLECTIONS:
        for row in g[coll]:
            for where, owner in _owner_blocks(row):
                path = owner["file"]
                full = os.path.join(REPO, path)
                if not os.path.exists(full):
                    f.err("[P1]", f"{row['id']} {where or 'owner'} file does not exist: {path}")
                    continue
                anchor = owner.get("anchor")
                if anchor and path.endswith(".md") and not anchor_resolves(full, anchor):
                    f.err("[P2]", f"{row['id']} {where or 'owner'} anchor does not resolve: "
                                  f"{path}{anchor}")


_ANCHOR_CACHE: dict[str, set[str]] = {}


def slugify(heading: str) -> str:
    """GitHub's heading-anchor rule, closely enough for pointer checking.

    ⚠ It strips its own leading `#` marks. Without that, passing a raw heading line yields a leading
    hyphen and every anchor silently fails to match — a checker that reports everything broken gets
    switched off just as fast as one that reports nothing broken.

    ⚠ A stripped glyph leaves its surrounding spaces behind, so each becomes a hyphen. Adding a `⭐` to
    a heading therefore changes its anchor without changing a word of it. That is not a quirk to work
    around — it is the exact drift this check exists to catch, and it found one on its first run.
    """
    s = heading.lstrip("#").strip().lower()
    # ⛔ A MARKDOWN LINK IN A HEADING: GITHUB KEEPS THE TEXT AND DROPS THE URL. Stripping the brackets
    # instead kept BOTH, so `## GPU economics (full provenance in [pricing.md](../compute/pricing.md))`
    # slugified to `…-in-pricingmdcomputepricingmd` while the real anchor is `…-in-pricingmd`. The
    # roadmap's own §0.7 index linked to it correctly and the checker called the link broken — and a
    # checker that reports a correct link as broken is one that gets switched off, which this file's
    # own docstrings say twice.
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"`|\*|_|\[|\]|\(|\)", "", s)
    # ⛔ SUPERSCRIPT DIGITS: PYTHON KEEPS THEM, GITHUB DROPS THEM. `\w` under re.UNICODE matches U+2076
    # because `'⁶'.isalnum()` is True and its category is `No` — but github-slugger deletes it, so
    # `10⁶ ARTIFACT` anchors as `10-artifact`. Measured against github-slugger@2.0.0 itself rather than
    # reasoned about. Categories `No`/`Nl` cover ⁶ ² ³ ½ and the Roman numerals; `Lm` (ⁿ, ʰ) is a
    # LETTER modifier and GitHub keeps those, so it is deliberately not in this set.
    s = "".join(c for c in s if unicodedata.category(c) not in ("No", "Nl"))
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = s.replace(" ", "-")
    return s


def anchor_resolves(path: str, anchor: str) -> bool:
    """⚠ `#heading|row-selector` IS A REPOSITORY CONVENTION, not a malformed anchor.

    Several `grade.owner` pointers address a ROW inside a section — `#2--the-ranked-list|tier1-rank2` —
    because a heading alone is too coarse to say which ranked entry a grade came from. Only the part
    before the `|` is a GitHub anchor; the selector is ours and there is nothing in the document for it
    to match. Validating the whole string reported nine live pointers as broken on the first run of the
    widened check, which is how a correct check earns a reputation for crying wolf.
    """
    want = anchor.lstrip("#").split("|", 1)[0]
    if path not in _ANCHOR_CACHE:
        slugs = set()
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    slugs.add(slugify(line.lstrip("#")))
        _ANCHOR_CACHE[path] = slugs
    return want in _ANCHOR_CACHE[path]


def check_instrument_support(g, f):
    """An instrument whose known-answer control failed, or that has none, may not be listed as SUPPORT."""
    inst = by_id(g["instruments"])
    for r in g["routes"]:
        for v in r.get("instruments", {}).get("support", []):
            i = inst.get(v)
            if not i:
                f.err("[V1]", f"{r['id']} cites unknown instrument {v}")
                continue
            state = (i.get("known_answer_control") or {}).get("state")
            if state in NON_SUPPORTING_CONTROL:
                f.err("[V2]", f"{r['id']} lists {v} as SUPPORT but its known-answer control is "
                              f"'{state}' -- a claim can never be stronger than the instrument underneath it")
            # ⚠ A PASSING CONTROL IS NOT THE WHOLE ANSWER. An instrument that passes its own control can
            # still be unable to license a claim, because it inherits another instrument's limits --
            # INS-MONOVALENT-REACH replicates the committed bivalent artifact cell-for-cell and its own
            # note still says it "can refute a route and cannot license one". `usable` is computed
            # through `inherits_limits_from`; reading only the control state is what missed this.
            elif not i.get("usable"):
                bad = [p for p in i.get("inherits_limits_from", []) if not inst.get(p, {}).get("usable")]
                f.err("[V3]", f"{r['id']} lists {v} as SUPPORT and its own control passes, but it "
                              f"INHERITS the limits of {', '.join(bad)}, which cannot support anything -- "
                              f"so neither can it. Cite it as `disclosed_failing`, or drop the inheritance "
                              f"if it is not real")


NON_SUPPORTING_LABEL = {"fails": "its control FAILED", "none": "it has NO control",
                        "inconclusive": "its control was INCONCLUSIVE",
                        "mixed": "its control was MIXED -- partly, which is not a pass"}

#: Why a requirement has NO instrument. Asserted only where `verified_by` is empty and the requirement
#: is not dead, because everything else here is derivable and must not be typed twice.
#:
#: ⭐ THE POINT IS THAT [Q3] WAS MISCALIBRATED, NOT THAT IT WAS NOISY. It said "there is nothing built
#: that could answer it" about four requirements that were in two entirely different situations: R6 is a
#: computable term nobody has computed (a work item), while R4's own note reads "⛔ none -- needs a bench"
#: and CLAUDE.md §5 puts a self-funded wet-lab program off the table, and R16's own claim_ceiling says the
#: paper's contribution "is the target's computational druggability/selectivity, not EMC efficacy". Those
#: last two are STATED SCOPE BOUNDARIES. Warning about them forever trains the reader to skip the check.
COVERAGE_GAPS = {
    "buildable":     ("WARN", "nothing built yet, and it could be built in this program"),
    "needs_wet_lab": ("INFO", "no instrument can be built here -- CLAUDE.md §5, no wet lab"),
    "out_of_scope":  ("INFO", "not this paper's question, by its own claim ceiling"),
}


def check_requirements(g, f):
    """The requirement register, and the coverage question it exists to answer.

    Invariant 2 lives here: read down a requirement's column and THE WEAKEST CELL SETS ITS CEILING.
    A requirement served only by instruments that have not recovered a known answer has no usable
    answer available -- which is a different and more actionable statement than "not done yet".
    """
    inst = by_id(g["instruments"])
    for r in g.get("requirements", []):
        vb = r.get("verified_by", [])
        for v in vb:
            if v not in inst:
                f.err("[Q1]", f"{r['id']} is verified by unknown instrument {v}")
        if not r.get("claim_ceiling"):
            f.err("[Q2]", f"{r['id']} states no claim ceiling -- a requirement with no stated ceiling "
                          f"cannot bound what may be claimed from it, which is the register's whole job")

        if not vb and r["state"]["work_state"] not in ("dead",):
            gap = r.get("coverage_gap")
            if gap not in COVERAGE_GAPS:
                # ⛔ NOT A WARNING. An uninstrumented requirement that will not say WHY is the vague
                # state this register exists to forbid, and omitting the field must not be the quiet
                # way to avoid answering.
                f.err("[Q3]", f"{r['id']} has no instrument and no `coverage_gap` -- 'nothing built yet' "
                              f"and 'nothing CAN be built here' license opposite actions, so the model "
                              f"must say which. One of: {', '.join(sorted(COVERAGE_GAPS))}")
            elif COVERAGE_GAPS[gap][0] == "WARN":
                f.warn("[Q3]", f"{r['id']} has NO instrument at all -- {COVERAGE_GAPS[gap][1]}. "
                               f"{_clip(r.get('coverage_gap_why', ''), 200)}")
            else:
                # A stated scope boundary is a FINDING, not a defect. It is reported once, in the
                # register view, and does not sit in the warning list forever.
                f.info("[Q3]", f"{r['id']} has no instrument -- {COVERAGE_GAPS[gap][1]}")

        unusable = [v for v in vb if not inst.get(v, {}).get("usable")]
        if vb and len(unusable) == len(vb):
            why = ", ".join(
                f"{v} ({NON_SUPPORTING_LABEL.get((inst.get(v, {}).get('known_answer_control') or {}).get('state'), 'it inherits limits it cannot clear')})"
                for v in vb)
            f.warn("[Q4]", f"{r['id']} has instruments but NONE has returned a usable answer -- {why}. "
                           f"That is a different and more actionable failure than having none")


def check_compute_case(g, f):
    for r in g["routes"]:
        if r.get("recommends_compute") and not r.get("compute_case"):
            f.err("[C1]", f"{r['id']} recommends compute with no compute_case -- reasoning must be shown "
                          f"exhausted before money is spent")


LEGACY = os.path.join(REPO, "research", "manuscripts", "emc-systems-map.json")

# The fields the legacy registry and the graph BOTH carry. The graph adds lifecycle, readiness and
# timing on top; those are new and have no legacy counterpart to disagree with.
SHARED_ROUTE_FIELDS = ["display_name", "grade", "closure_kind", "blockers_retired",
                       "objects", "evidence", "artifacts"]


def check_legacy_agreement(g, f):
    """The legacy registry and the graph must not disagree about a fact they both carry.

    ⚠ WHY THIS IS A CHECK AND NOT A MIGRATION. Eleven consumers still read the legacy registry,
    including the weekly scan interop, so it cannot simply be deleted. But two files carrying the same
    fact is precisely the one-fact-many-places bug this whole architecture exists to fix, and leaving
    it unguarded for the length of a migration is how a duplicate becomes a divergence.

    So the duplication is TEMPORARY AND POLICED: the graph is the source, the legacy file is a
    projection, and any disagreement on a shared field fails the build. `blockers_inherited` is
    deliberately excluded -- the graph adds blockers the legacy file predates, which is a superset
    rather than a conflict, and flagging it would train the reader to ignore this check.
    """
    if not os.path.exists(LEGACY):
        f.err("[L1]", "the legacy registry is missing; eleven consumers read it")
        return
    with open(LEGACY, encoding="utf-8") as fh:
        legacy = json.load(fh)

    # ⚠ `serves` DROPPED FROM THE COMPARED FIELDS 2026-08-05, and this is a deletion rather than a
    # rename on purpose. The graph no longer asserts it anywhere -- `verifies` is derived from the
    # requirement register and `allocated_to` from the route register -- so there is nothing on the
    # graph side for the legacy copy to agree or disagree WITH. Reprojecting a derived value into the
    # legacy file would recreate the exact duplication this migration removed, one file further out.
    # Verified before dropping: no consumer reads `instruments[].serves`, and emc-systems-map.md
    # never rendered it. The legacy rows keep the field; nothing compares it.
    for coll, fields in [("routes", SHARED_ROUTE_FIELDS),
                         ("blockers", ["name", "statement_about", "owner"]),
                         ("instruments", ["name", "known_answer_control"])]:
        lg, gr = by_id(legacy.get(coll, [])), by_id(g[coll])
        for rid, lrow in lg.items():
            grow = gr.get(rid)
            if grow is None:
                f.err("[L2]", f"{coll}/{rid} is in the legacy registry but not in the graph")
                continue
            for key in fields:
                if key in lrow and lrow[key] != grow.get(key):
                    f.err("[L3]", f"{coll}/{rid}.{key} disagrees between the graph and the legacy "
                                  f"registry — the graph is the source; reproject the legacy file")
        for rid in set(gr) - set(lg):
            f.warn("[L4]", f"{coll}/{rid} is new in the graph and absent from the legacy registry "
                           f"(expected while the legacy file is still hand-maintained)")



MAP_DOC = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")
_R_ROW = re.compile(r"^\|\s*\*\*(R\d+)\*\*\s*\|")


LANE_MENTION = re.compile(r"\bLANE[- ](\d+)\b")


def check_lanes(g, f):
    """Every lane the documents name is registered, and every registered lane is honest about its state.

    ⭐ WHY THIS COLLECTION EXISTS AT ALL. The model could say what work COULD be done (routes) and what
    must be TRUE (requirements), but had no object for work that HAS RUN. So "this lane closed" lived
    only as a struck-through row in roadmap prose — and prose is not queryable. On 2026-08-05 an artifact
    belonging to a lane that closed on 2026-07-30 was therefore read as a gap to fill, and 88.5 minutes
    of CI went at it. The fix is not a better regex over the prose; it is that the state is modelled.

    ⚠ ENUMERATED, NOT TRUSTED. The register is checked against every `LANE n` mention in the repository,
    so it cannot silently stop covering the namespace — the failure mode of every hand-maintained list.
    """
    reg = {l["id"] for l in g["lanes"]}
    seen = defaultdict(set)
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if _is_transient(rel_root):
            dirs[:] = []
            continue
        for fn in sorted(files):
            if not fn.endswith((".md", ".py", ".json", ".yml")):
                continue
            rel = f"{rel_root}/{fn}" if rel_root != "." else fn
            if rel.startswith(("systems/views/", "systems/graph/lanes.json", "archive/")):
                continue
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="ignore") as fh:
                for m in LANE_MENTION.finditer(fh.read()):
                    seen[f"LANE-{m.group(1)}"].add(rel)
    for lid in sorted(set(seen) - reg):
        where = sorted(seen[lid])
        f.err("[W1]", f"{lid} is named in {len(where)} file(s) ({', '.join(where[:3])}) and is not in "
                      f"the lane register — executed work whose state is not modelled is exactly what "
                      f"made an artifact's absence unreadable")
    for lid in sorted(reg - set(seen)):
        f.warn("[W2]", f"{lid} is registered but no document mentions it — either it is finished with "
                       f"its record elsewhere, or the register has outlived its subject")

    # ⭐ THE TWO ARTIFACT NAMESPACES MUST MEET SOMEWHERE, AND UNTIL 2026-08-05 THEY DID NOT.
    # `lane.produces[]` names a FILENAME (deliberately — check_artifacts asks "does this file exist on
    # this branch?", a filesystem question, and branch drift is what it guards). `artifacts.json` names
    # `ART-*` ids with a path, a producer and a workflow. The two registers covered DISJOINT SETS: 12
    # artifacts registered, none of the six a lane produced.
    #
    # ⚠ AND THAT WAS WRITTEN DOWN AND WALKED PAST. relations.json recorded it as "a real and stated
    # gap … registering them would need a path, producer and workflow per row — real data, not a
    # rename." Every field was findable in minutes. A recorded observation with no owner is the
    # "watching" costume CLAUDE.md §4 forbids, so it is now a check rather than a sentence.
    by_path = {os.path.basename(a.get("path", "")): a["id"] for a in g.get("artifacts", [])}
    for l in g["lanes"]:
        for p in l.get("produces", []):
            # An artifact the lane never produced has no path to register — its absence is the fact,
            # and `check_artifacts` derives the disposition from `produced: false`.
            if p["produced"] and p["artifact"] not in by_path:
                f.warn("[W5]", f"{l['id']} produced `{p['artifact']}` and systems/graph/artifacts.json "
                               f"does not register it — so nothing records its producer, its workflow "
                               f"or which ref it was published to, which is exactly what makes branch "
                               f"drift invisible")

    for l in g["lanes"]:
        if l["state"] in ("held", "parked") and not l.get("gate"):
            f.err("[W3]", f"{l['id']} is `{l['state']}` and names no gate — a pause with nothing that "
                          f"would restart it is indistinguishable from an abandonment, and the two have "
                          f"very different consequences for anything waiting on it")
        if l["state"] == "complete" and not l.get("closed_on") and "closed_on" in l:
            f.warn("[W4]", f"{l['id']} is complete with no date — recoverable, but it means nothing can "
                           f"say how stale its verdict is")


def check_requirement_source_agreement(g, f):
    """The roadmap's register table and the graph must not disagree, in either direction.

    ⭐ THIS IS WHAT MAKES THE DECOMPOSITION SAFE. The register was lifted into the graph LOSSLESSLY —
    every claim-ceiling cell is stored verbatim — so the graph can be the machine home while the roadmap
    stays the narrative home. Without this check that is just a duplicate waiting to diverge; with it,
    a hand-edit to either side fails the build and says which.

    ⚠ It re-parses the roadmap rather than trusting a stored copy. A guard that compares the graph to a
    snapshot of the document is guarding the snapshot, not the document.
    """
    if not os.path.exists(MAP_DOC):
        f.err("[M1]", "the roadmap is missing; the requirement register has no narrative home")
        return
    with open(MAP_DOC, encoding="utf-8") as fh:
        rows = {}
        for ln in fh:
            m = _R_ROW.match(ln)
            if m:
                cells = [c.strip() for c in ln.split("|")[1:]]
                rows[m.group(1)] = cells
    gr = by_id(g.get("requirements", []))

    missing_in_graph = set(rows) - set(gr)
    missing_in_map = set(gr) - set(rows)
    for rid in sorted(missing_in_graph):
        f.err("[M2]", f"{rid} is in the roadmap's register and not in the graph — run the extractor")
    for rid in sorted(missing_in_map):
        f.err("[M3]", f"{rid} is in the graph and not in the roadmap's register")

    for rid in sorted(set(rows) & set(gr)):
        cells = rows[rid]
        if len(cells) > 5 and cells[5] != gr[rid].get("claim_ceiling_raw"):
            f.err("[M4]", f"{rid} claim ceiling differs between the roadmap and the graph — one of them "
                          f"was hand-edited. The roadmap owns the wording; re-run the extractor.")
        # ⚠ THE PATTERN MUST MATCH EVERY INSTRUMENT NAMESPACE, NOT JUST `V\d+`. It read only V-ids
        # until 2026-08-05, so an `INS-`-prefixed instrument could be named in the roadmap and be
        # invisible to the agreement check — which is half of how R13 came to report "NO instrument at
        # all" in the graph while the roadmap's own cell said one exists and is staged.
        verified = sorted(set(re.findall(r"`(V\d+|INS-[A-Z0-9-]+)`", cells[4])), key=_req_sort_inst)
        if verified != gr[rid].get("verified_by"):
            f.err("[M5]", f"{rid} verified-by disagrees: roadmap {verified} vs graph "
                          f"{gr[rid].get('verified_by')} — the roadmap owns the wording, the graph owns "
                          f"the relation; make the cell name every instrument the graph carries")



SCAN_TRIGGERS = os.path.join(REPO, "research", "method-watch-triggers.json")


def check_scan_interop(g, f):
    """TECH-* <-> TRG-* in BOTH directions, plus the ungraded-signal queue.

    The scan file is the ONE HOME of the search queries and this register never copies one -- it
    references them by id. Two files sharing one vocabulary is exactly the shape that rots silently,
    so the reference is checked rather than trusted.

    ⭐ The reverse direction was called uncheckable in trigger_scan.py's own docstring as recently as
    2026-08-03, because the field it needed did not exist. It does now.
    """
    if not os.path.exists(SCAN_TRIGGERS):
        f.err("[X1]", "research/method-watch-triggers.json is missing; the capability scan has no config")
        return
    with open(SCAN_TRIGGERS, encoding="utf-8") as fh:
        rows = json.load(fh).get("triggers", [])
    known = {t["id"] for t in rows}
    # ⚠ An `internal_work` trigger legitimately has no TECH-*: it is work THIS program can do, not a
    # capability to wait for. Warning on those would be the exact conflation the technology taxonomy
    # exists to prevent -- and it is how four of them ended up on a watch list in the first place.
    kind_of = {t["id"]: t.get("trigger_kind", "external_capability") for t in rows}
    # ⛔ A DISABLED TRIGGER IS NOT AN UNWATCHED ONE, AND SAYING IT IS WAS A FACTUAL ERROR IN THIS
    # CHECK'S OWN MESSAGE. It printed "is scanned weekly" for TRG-PERSES-RDKIT-PATH, which has
    # `scan_enabled: false` and a `not_searchable_because` explaining that reopening it buys nothing
    # while pmx serves the avenue. A check that misdescribes what it found is the failure mode
    # MAINTENANCE.md section 4 is about: it costs a real investigation to dismiss a fake finding.
    enabled = {t["id"] for t in rows if t.get("scan_enabled")}
    stated = {t["id"] for t in rows if t.get("not_searchable_because")}

    watched = set()
    for t in g["technologies"]:
        for ref in t.get("scan_trigger") or []:
            watched.add(ref)
            if ref not in known:
                f.err("[X2]", f"{t['id']} names scan trigger {ref}, which does not exist in "
                              f"research/method-watch-triggers.json")
    for trg in sorted(known - watched):
        if kind_of.get(trg) == "internal_work":
            continue  # not a capability; it belongs on a route's best_next_action, not in the register
        if trg not in enabled:
            if trg in stated:
                continue  # a recorded decision not to search, with its reason next to it
            f.warn("[X5]", f"{trg} is neither scanned (`scan_enabled: false`) nor watched by any "
                           f"TECH-*, and gives no `not_searchable_because` — so nothing looks for it "
                           f"and nothing says why")
            continue
        f.warn("[X3]", f"{trg} is scanned weekly but no TECH-* watches it — it fires into nothing, "
                       f"so a hit has no recorded consequence")

    for t in g["technologies"]:
        ungraded = [s for s in t.get("pending_signals", []) if not s.get("graded")]
        if ungraded:
            f.warn("[X4]", f"{t['id']} has {len(ungraded)} UNGRADED scan signal(s) — a human must read "
                           f"them and either promote to `evidence` or mark graded; the scan deliberately "
                           f"cannot change `current_state` itself")



FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
GEN_BANNER = re.compile(r"GENERATED FILE\s*[—-]?\s*do not edit|^<!--\s*GENERATED", re.M | re.I)
DOC_SKIP = ("systems/views/", "archive/", "node_modules/", ".git/", ".pytest_cache/")


def _frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return None
    out = {}
    for ln in m.group(1).splitlines():
        if ln.startswith((" ", "\t", "-")) or ":" not in ln:
            continue
        k, _, v = ln.partition(":")
        out[k.strip()] = v.strip()
    return out


#: ⚠ WIDER THAN `DOC_SKIP` ON PURPOSE — see check_doc_ids.
ID_SKIP = ("systems/views/", "node_modules/", ".git/", ".pytest_cache/")


def _walk_md(skip):
    """Every Markdown file under REPO whose path does not start with one of `skip`."""
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if rel_root == ".":
            rel_root = ""
        if "__pycache__" in rel_root or (rel_root and (rel_root + "/").startswith(skip)):
            dirs[:] = []
            continue
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            rel = f"{rel_root}/{fn}" if rel_root else fn
            if rel.startswith(skip):
                continue
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="ignore") as fh:
                yield rel, fh.read()


def check_doc_ids(g, f):
    """A DOC id resolves to exactly ONE file.

    ⛔ THIS EXISTS BECAUSE THE BULK BACKFILL BROKE IT. `slug()` derived ids from basenames, so
    `METHODOLOGY.md` and `research/hypotheses/METHODOLOGY.md` — two different contracts, cited for
    different things — both became `DOC-METHODOLOGY`, and five READMEs became `DOC-README`. Seven
    files, two ids. `check_ids_unique` did not catch it: that covers the twelve GRAPH collections,
    and document ids live in frontmatter, which nothing checked.

    ⚠ THE SCAN IS WIDER THAN `DOC_SKIP`: it includes `archive/`. Frontmatter *enforcement* rightly
    stops at the archive — an archived document is not maintained — but UNIQUENESS is a property of
    the namespace, not of the live set. An archived document keeps its id, so a new file taking the
    old name would silently mint a duplicate that only ever showed up as a broken cross-reference.
    """
    homes = defaultdict(list)
    for rel, text in _walk_md(ID_SKIP):
        fmv = _frontmatter(text)
        if fmv and fmv.get("id"):
            homes[fmv["id"]].append(rel)
    for did, paths in sorted(homes.items()):
        if len(paths) > 1:
            f.err("[D6]", f"document id {did} is claimed by {len(paths)} files ({', '.join(paths)}) "
                          f"— an id must resolve to exactly one document")


PINNED = os.path.join(REPO, "research", "manuscripts", "pinned-figures.json")
INSTRUCTION_DOCS = ("CLAUDE.md", "AGENTS.md")
INSTRUCTION_REF = re.compile(r"[\(\[`]([A-Za-z0-9_./-]+\.md)")


def _pinned_targets():
    """Markdown files `lint_consistency.py` is contractually required to find.

    ⚠ RAISES rather than returning an empty set. A helper that answers "nothing depends on anything"
    when its input moved would silently switch [D8] off, which is the fail-open shape `parser_guard`
    exists to catch — and switching a guard off is worse than never having written it.
    """
    with open(PINNED, encoding="utf-8") as fh:
        d = json.load(fh)
    out = {t for t in d.get("targets", []) if t.endswith(".md")}
    if not out:
        raise RuntimeError("pinned-figures.json declares no Markdown targets — [D8] would be inert")
    return out


def _instruction_paths():
    """Markdown files the standing project instructions tell a reader to go and read.

    A path quoted inside CLAUDE.md or AGENTS.md is an instruction to consult it NOW. Deliberately
    literal: it does not try to distinguish "read this" from "this is retired", because the
    `history_only: true` acknowledgement is how a genuine history reference declares itself. Over-
    flagging costs one frontmatter line; under-flagging is how a live document gets archived.
    """
    out = set()
    for doc in INSTRUCTION_DOCS:
        p = os.path.join(REPO, doc)
        if not os.path.exists(p):
            raise RuntimeError(f"{doc} is missing — [D8]'s instruction half would be inert")
        with open(p, encoding="utf-8") as fh:
            for m in INSTRUCTION_REF.finditer(fh.read()):
                t = m.group(1).lstrip("./")
                if os.path.exists(os.path.join(REPO, t)):
                    out.add(t)
    return out


#: Directories that are machinery rather than content, matched on any path COMPONENT.
#:
#: ⛔ THE PREFIX FORM WAS A BUG AND IT TURNED THE BUILD RED (2026-08-05). Three walks tested
#: `rel_root.startswith((".git", "node_modules", ".pytest_cache"))`, which only ever matched at the
#: REPOSITORY ROOT. Running pytest from `research/modalities` creates
#: `research/modalities/.pytest_cache/README.md` — a file pytest writes, that no human authored — and
#: [D4] duly failed the build for its missing frontmatter. A checker that goes red because a test run
#: left a cache behind is a checker people learn to work around.
TRANSIENT_DIRS = {".git", "node_modules", ".pytest_cache", "__pycache__", ".mypy_cache",
                  ".ruff_cache", ".ipynb_checkpoints", ".venv", "venv", ".tox", "node_modules"}


def _is_transient(rel_root):
    return bool(TRANSIENT_DIRS & set(rel_root.split("/")))


def check_documents(g, f):
    """Every hand-written Markdown file declares purpose, scope, audience, status and freshness.

    ⚠ FILESYSTEM DATES CARRY NO INFORMATION HERE — the history is a squashed import and every file
    reports the same date — so freshness is declared or it does not exist.

    ⛔ `last_verified: unverified` IS AN HONEST VALUE, NOT A HOLE. The bulk backfill read none of these
    documents; stamping them with its own run date would have claimed a verification nobody performed,
    in the one field whose entire job is to say how stale something is. The count below is meant to
    fall as people read them, and it is reported rather than hidden.
    """
    allowed_status = {"live", "generated", "historical", "superseded", "immutable"}
    retired = {"historical", "superseded"}
    # ⚠ TWO SOURCES, REPORTED SEPARATELY. A refusal that does not name which dependency it hit is
    # unactionable: "it is a pinned figure target" and "CLAUDE.md tells agents to read it" have
    # different remedies (repoint the numeric contract vs. rewrite an instruction).
    depends_on = {}
    for rel in _pinned_targets():
        depends_on.setdefault(rel, []).append("pinned-figures.json `targets`")
    for rel in _instruction_paths():
        depends_on.setdefault(rel, []).append("the project instructions (CLAUDE.md / AGENTS.md)")
    missing, unverified, bad = [], [], 0
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if _is_transient(rel_root):
            dirs[:] = []
            continue
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            rel = os.path.normpath(os.path.join(rel_root, fn)).replace(os.sep, "/")
            if rel.startswith(DOC_SKIP):
                continue
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            fmv = _frontmatter(text)
            if fmv is None:
                # A generated file's header is owned by its generator; adding frontmatter would make
                # it differ from a fresh render and turn ITS drift check red.
                if GEN_BANNER.search("\n".join(text.splitlines()[:20])):
                    continue
                missing.append(rel)
                continue
            for key in ("id", "title", "kind", "status", "purpose", "scope", "audience", "last_verified"):
                if key not in fmv:
                    f.err("[D1]", f"{rel} frontmatter is missing `{key}`")
                    bad += 1
            if fmv.get("status") and fmv["status"] not in allowed_status:
                f.err("[D2]", f"{rel} has status {fmv['status']!r}, outside the closed set")
                bad += 1
            if fmv.get("kind") == "prereg" and fmv.get("status") != "immutable":
                f.err("[D3]", f"{rel} is a preregistration but is not `immutable` — a prereg's whole "
                              f"value is that it was written before the result")
                bad += 1
            # ⛔ AND THE INVERSE, WHICH IS THE DANGEROUS DIRECTION. [D3] alone let the bulk backfill mark a
            # DRAFT preregistration `immutable` on the strength of "prereg" appearing in its filename —
            # while the document's own H1 read "⚠ DRAFT, NOT FROZEN". A frozen prereg is the repository's
            # strongest evidentiary claim (this design was fixed BEFORE that result), so a draft wearing
            # that status is the one thing that could erode it. The repo's own convention is that the
            # FILENAME carries the freeze state: freezing is a separate dated commit that renames the file.
            declared_draft = ("-draft" in rel.lower()
                              or str(fmv.get("frozen", "")).lower() in ("false", "no")
                              or re.search(r"NOT FROZEN|\bDRAFT\b", "\n".join(text.splitlines()[:40])))
            if fmv.get("status") == "immutable" and declared_draft:
                f.err("[D10]", f"{rel} declares `immutable` while calling itself a DRAFT — `immutable` is "
                               f"reserved for a FROZEN preregistration, and a draft carrying it is exactly "
                               f"the confusion that would undermine every real one")
                bad += 1
            if fmv.get("status") == "superseded" and not fmv.get("superseded_by"):
                f.err("[D7]", f"{rel} declares `superseded` but names no successor — a supersession "
                              f"with nothing to redirect to is unfalsifiable, and the reader who "
                              f"needs it most is the one who arrived here by accident")
                bad += 1
            if rel in depends_on and fmv.get("status") in retired \
                    and str(fmv.get("history_only", "")).lower() not in ("true", "yes"):
                f.err("[D8]", f"{rel} declares `{fmv['status']}` but is depended on by "
                              f"{' and '.join(depends_on[rel])} — a document something reads TODAY "
                              f"is live by definition. If the combination is deliberate (a correction "
                              f"register has to stay reachable to do its job), say so with "
                              f"`history_only: true`")
                bad += 1
            if fmv.get("last_verified") == "unverified":
                unverified.append(rel)
    for rel in missing:
        f.err("[D4]", f"{rel} has no frontmatter — purpose, scope, audience and freshness are undeclared")
    if unverified:
        # ⭐ BUCKETED, NOT JUST COUNTED (2026-08-05). "163 documents are unverified" is true and
        # unactionable — nobody reads 163 documents, so the number sat unchanged and the warning became
        # furniture. ⛔ Mass-stamping them would be the exact dishonesty this field exists to prevent:
        # `last_verified` means someone READ it and confirmed it is still true, and a bulk date claims a
        # verification nobody performed. So the count stays and the warning says WHICH ONES MATTER —
        # the ones something already depends on, which is the same `depends_on` [D8] is built from.
        hot = sorted(r for r in unverified if r in depends_on)
        f.warn("[D5]", f"{len(unverified)} document(s) carry `last_verified: unverified` — nobody has "
                       f"confirmed their content is still true. This is honest, not a defect; the count "
                       f"is meant to fall. ⭐ **{len(hot)} of them are LOAD-BEARING** — pinned or named "
                       f"by the project instructions, so something reads them today: "
                       f"{', '.join(hot) if hot else '(none — the rest are reference and history)'}")



#: A bare artifact citation: a backticked `something-like-this.json` / `.png` / `.csv`, which is how
#: this repository actually cites results in prose. Deliberately NOT a Markdown link — see check_artifacts.
ARTIFACT_CITE = re.compile(r"`([a-z0-9][a-z0-9._-]*\.(?:json|jsonl|png|csv))`", re.I)

#: A backticked CODE citation — a module or a workflow this repository claims to have.
#:
#: ⛔ THESE WERE OUTSIDE EVERY CHECK, AND THE GAP LANDED IN THE RULES FILE. `check_artifacts` scopes
#: itself to RESULT extensions, so a backticked `.py` or `.yml` was cited by nobody's checker. Measured
#: 2026-08-05: CLAUDE.md §6 — the rule telling every session how to route work it cannot do in the
#: sandbox — named `atlas-data.yml`, `expression_reprocess.py` and `fulltext_verify.py` as its
#: exemplars, and NONE of the three exists on this branch, on `main`, on `modalities-cache`, or anywhere
#: in history. A reader following that rule finds nothing and concludes the escape hatch is fiction.
CODE_CITE = re.compile(r"`([a-z0-9][a-z0-9._-]*\.(?:py|yml|yaml|mjs|sh))`", re.I)

#: Directories a backticked code name may live in. A citation is only checkable if we know where to
#: look; anything outside these is somebody else's repository and is not this check's business.
CODE_DIRS = ("research", "systems", "scripts", ".github/workflows", "sagemaker_src", "deploy", "tests")
ARTIFACT_DIRS = ("research/modalities", "research/manuscripts", "research/data", "research/compute",
                 "research/hypotheses", "research/meta", "systems/graph", "results")


def _artifacts_elsewhere(f):
    """Artifacts that deliberately live on another ref — a CHECKED claim, not a silencer.

    ⛔ EVERY FIELD IS REQUIRED, AND THAT IS THE WHOLE DESIGN. An entry with no `ref`, no `written_by`
    or no `why_not_ported` is indistinguishable from "we did not get round to porting it" — which is
    drift, and drift belongs in the port. Refusing the incomplete entry is what stops this register
    becoming the place warnings go to die.
    """
#: The three things "cited and absent" can mean. ⛔ NAMING ONLY TWO IS WHAT CAUSED THE 2026-08-05 ERROR.
#: Each requires its own evidence, because each licenses a DIFFERENT action and they are not
#: interchangeable: `elsewhere` means go and fetch it, `expected` means go and run something,
#: `withdrawn` means go and delete the citation. Guessing between them wastes either compute or a fact.
DISPOSITIONS = {
    "elsewhere": ("ref", "written_by"),      # it exists, on another ref
    "expected":  ("produced_by",),           # the work is OPEN and would produce it
    "withdrawn": ("closed_by",),             # the work is CLOSED — the citation is what is wrong
}


def _artifact_dispositions(f):
    """Cited-but-absent artifacts that have been CLASSIFIED, and the classification's evidence.

    ⛔ EVERY ENTRY IS A CHECKED CLAIM, NOT A SILENCER — an entry with no reason is indistinguishable
    from "we did not get round to it", which is the state this register exists to make visible.
    """
    path = os.path.join(GRAPH, "artifact-refs.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = doc.get("dispositions") or doc.get("elsewhere") or []
    out = {}
    for r in rows:
        art, dis = r.get("artifact"), r.get("disposition")
        if not art:
            f.err("[K2]", "an artifact-refs entry names no artifact")
            continue
        if dis not in DISPOSITIONS:
            f.err("[K2]", f"artifact-refs entry {art} has disposition {dis!r}, outside "
                          f"{sorted(DISPOSITIONS)} — 'absent' is an OBSERVATION and each of those three "
                          f"licenses a different action, so it has to be chosen rather than implied")
            continue
        need = ("why", "checked_on") + DISPOSITIONS[dis]
        gaps = [k for k in need if not r.get(k)]
        if gaps:
            f.err("[K2]", f"artifact-refs entry {art} is `{dis}` but is missing {gaps} — that "
                          f"disposition is unsupported, and an unsupported disposition is a silencer")
            continue
        if len(r["why"]) < 60:
            f.err("[K2]", f"artifact-refs entry {art} gives a one-line reason. Each disposition is a "
                          f"claim someone has to be able to check later: `elsewhere` says a second copy "
                          f"would be HARMFUL, `expected` says the work is OPEN, `withdrawn` says it is "
                          f"CLOSED. One line cannot carry any of those")
            continue
        out[art] = r
    return out


#: What a lane's state means for an artifact it owes but has not produced. ⭐ THIS IS THE MODELLED
#: ANSWER, and it replaces reading struck-through prose. `complete` means the lane ENDED, so an artifact
#: it never produced is never coming — the citation is what is wrong. `held`/`parked` mean it may yet
#: resume behind a named gate. `running` means it is coming.
LANE_STATE_DISPOSITION = {
    "complete": "withdrawn",
    "held": "expected",
    "parked": "expected",
    "running": "expected",
}


def _clip(s, n):
    """Trim at a sentence or word boundary — a message that cuts mid-clause reads as a bug."""
    s = re.sub(r"\s+", " ", s or "").strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    stop = max(cut.rfind(". "), cut.rfind(" — "), cut.rfind("; "))
    return (cut[:stop + 1] if stop > n // 2 else cut.rsplit(" ", 1)[0]) + " …"


def _lane_verdict_for(name, g):
    """(disposition, lane, entry) for an artifact some lane owes — or (None, None, None).

    ⛔ THIS IS WHY LANES ARE MODELLED. The previous version of this answer was a regex hunting for
    struck-through rows in the roadmap: it worked, and it was still prose-matching, so it could only ever
    be *evidence for a human* rather than a fact the model knows. A lane's `produces[]` names every
    artifact it was responsible for AND whether it was produced, so an absence resolves by lookup.
    """
    for lane in g.get("lanes", []):
        for p in lane.get("produces", []):
            if p["artifact"] == name and not p["produced"]:
                return LANE_STATE_DISPOSITION.get(lane["state"]), lane, p
    return None, None, None


def check_artifacts(g, f):
    """An artifact cited BY NAME must exist on this branch.

    ⭐ WHY A LINK CHECKER IS NOT ENOUGH, MEASURED 2026-08-05. `check_links` validates the shape of a
    relative Markdown link. But this repository cites results the way researchers actually do — a bare
    backticked filename in a sentence, a `--out` default in a docstring, a path inside a JSON note —
    and none of those is a link. When 41 artifacts were found living only on the `modalities-cache`
    branch, **24 were cited from here and the link checker had caught exactly one.** It was not
    broken; it was measuring a different thing.

    ⛔ THE FAILURE MODE IS SPECIFICALLY BRANCH DRIFT, AND IT IS SILENT. A workflow that checks out its
    own branch writes its outputs there. A manuscript on another branch then cites those outputs as
    though they were beside it. Nothing errors: the file exists, just not on the ref anyone is reading.
    CLAUDE.md calls this a data-loss bug rather than an inconvenience, and this check is what makes it
    visible without needing anyone to remember which branch a lane runs from.

    ⚠ SCOPED TO NAMES THAT LOOK LIKE THIS REPO'S ARTIFACTS, and to citations inside its own
    directories, because the alternative is flagging every filename ever mentioned — a checker that
    cries wolf gets switched off, which is how the SMILES-as-links problem was handled in `check_links`.
    """
    known = set()
    for d in ARTIFACT_DIRS:
        p = os.path.join(REPO, d)
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                known.update(files)
    # ⛔ THE LINK BASELINE IS **NOT** AN EXEMPTION FROM CLASSIFICATION, AND TREATING IT AS ONE IS THE
    # ACTUAL ROOT CAUSE OF THE 2026-08-05 ERROR — deeper than the missing third disposition.
    #
    # Two registers were describing overlapping sets under different rules. `link-baseline.json` answers
    # "is this Markdown link known-broken?" and carries a FREE-PROSE `why`; this check answers "what does
    # this absence MEAN?" and requires a disposition. `valb-triangle-chem.json` was in BOTH — so the
    # baseline's skip silently exempted it from the requirement, and the only thing describing it was a
    # prose field with no rules. That prose said "clears when the mapper is given a larger budget",
    # which is what sent 88.5 minutes of CI at a lane that had closed a week earlier.
    #
    # ⭐ THE TWO QUESTIONS ARE DIFFERENT AND BOTH MUST BE ANSWERED. A grandfathered link stops [K0]
    # failing the build on the LINK. It says nothing about whether the ARTIFACT should ever exist — and
    # that is precisely the question whose wrong answer costs compute. So the baseline no longer skips
    # anything here: an artifact that is cited and absent gets classified, however its absence surfaced.
    classified = _artifact_dispositions(f)

    # ⛔ A DERIVED ANSWER OUTRANKS A WRITTEN ONE, AND A WRITTEN ONE THAT DUPLICATES IT IS A SECOND HOME.
    # This is the same shadowing bug as the link baseline, one layer up: if a hand-written disposition
    # short-circuits the lane lookup, the two can drift and the stale one wins silently. So any artifact
    # a lane already answers for is REMOVED from the written register's authority and flagged.
    for art in sorted(classified):
        verdict, lane, _e = _lane_verdict_for(art, g)
        if verdict:
            f.err("[K2]", f"artifact-refs asserts a disposition for `{art}`, but {lane['id']} already "
                          f"DERIVES it (`{verdict}`, because the lane is `{lane['state']}`). Two homes "
                          f"for one fact, and the written one would win — delete it and let the lane "
                          f"answer, or correct the lane if the lane is what is wrong")
            classified.pop(art, None)

    missing = defaultdict(set)
    for rel, text in _walk_md(DOC_SKIP):
        for m in ARTIFACT_CITE.finditer(text):
            name = m.group(1)
            if name in known or name in classified:
                continue
            # A name nothing anywhere produces is a typo or a plan, not drift. Only flag a citation
            # whose producer exists here — that is what says "this was meant to have been generated".
            stem = os.path.splitext(name)[0].replace("-", "_")
            if f"{stem}.py" in known or f"{stem}.mjs" in known:
                missing[name].add(rel)
    for name in sorted(missing):
        cites = sorted(missing[name])
        # ⭐ ASK THE MODEL FIRST. If a lane owes this artifact and never produced it, its state ANSWERS
        # the question — no human assertion, no prose matching, no third register to keep in step.
        verdict, lane, entry = _lane_verdict_for(name, g)

        # ⛔ A MENTION IS NOT A CITATION, AND THE CHECK COULD NOT TELL THEM APART (2026-08-05).
        # `valb-closure-triangle-pregate-2026-07-25.md` says in three places that this citation IS
        # withdrawn; `systems/MAINTENANCE.md` names the artifact only to describe the incident it
        # caused. Both counted as citations, so [K1] warned — at two documents that had already done
        # exactly what it was asking for. A warning nobody can close is a warning everyone learns to
        # skip, which is the failure this whole register exists to prevent.
        #
        # ⚠ THE LIST IS NOT AN EXEMPTION. It is subtracted from the ENUMERATED citers, so a document
        # that starts citing the artifact tomorrow still fires. Silencing it would need someone to add
        # that document to the lane's `produces[]` by hand, which is the visible, reviewable act.
        if verdict == "withdrawn" and entry:
            done = set(entry.get("withdrawn_in", []))
            live = [c for c in cites if c not in done]
            if not live:
                f.info("[K1]", f"`{name}` is absent and {lane['id']} derives `withdrawn`; all "
                               f"{len(cites)} document(s) naming it record the withdrawal "
                               f"({', '.join(sorted(done & set(cites)))}). Closed, not pending")
                continue
            cites = live

        if verdict:
            f.warn("[K1]", f"`{name}` is cited by {len(cites)} document(s) and is absent. "
                           f"⭐ **THE MODEL ANSWERS THIS: `{verdict}`.** {lane['id']} — {lane['title']} "
                           f"— is `{lane['state']}`, and this artifact is registered as one it owed and "
                           f"never produced.\n           {_clip(lane['terminus'], 180)}"
                           + (f"\n           {_clip(entry['note'], 240)}" if entry.get("note") else "")
                           + (". ⛔ A `complete` lane produces nothing further, so the CITATION is what "
                              "is wrong — withdraw it rather than running anything."
                              if verdict == "withdrawn" else
                              f". The lane can still resume"
                              f"{' behind: ' + lane['gate'] if lane.get('gate') else ''}, so the "
                              f"citation is a forward reference rather than a defect."))
            continue
        f.warn("[K1]", f"`{name}` is cited by {len(cites)} document(s) ({', '.join(cites[:3])}"
                       f"{', …' if len(cites) > 3 else ''}) and its producer is in this repo, but the "
                       f"artifact is NOT here. ⛔ THAT IS AN OBSERVATION, NOT A GAP — it has THREE "
                       f"possible meanings and they license opposite actions: `elsewhere` (it exists on "
                       f"another ref — fetch it), `expected` (the work is OPEN and would produce it — "
                       f"run it), or `withdrawn` (the work CLOSED — the citation is what is wrong, "
                       f"delete it). ⚠ NO LANE CLAIMS THIS ARTIFACT, which is itself worth fixing: add "
                       f"it to the owing lane's `produces[]` in systems/graph/lanes.json and the answer "
                       f"becomes derivable. Failing that, record a disposition in "
                       f"systems/graph/artifact-refs.json")


#: Phrases that make a dead-looking code citation legitimate, checked on the line that names it.
#:
#: ⚠ TWO GENUINELY DIFFERENT CASES, AND BOTH MUST BE SAYABLE. A name can be absent because the file was
#: DELETED OR RENAMED — and a document recording that is doing its job, not carrying a dead pointer —
#: or because it belongs to an EXTERNAL repository, where the whole point of naming it is that we do
#: not own it. The first draft recognised only "superseded"/"retired"/"does not exist" and so flagged
#: a row whose own text read "`alarm_issue.py` deleted".
#:
#: ⛔ THIS IS NOT A SILENCER. The phrase has to be ON THE LINE, which means a human wrote the reason
#: next to the citation — exactly the sentence a reader needs. What it cannot do is clear a name that
#: nobody has explained.
CODE_CITE_CLEARED = (
    "uperseded", "etired", "does not exist", "delete", "renamed", "no longer exists",
    "upstream", "not ours", "external repo", "third-party", "generated at runtime",
)


def check_code_citations(g, f):
    """A backticked `.py` / `.yml` this repository names must be a file it has.

    ⚠ SCOPED THE SAME WAY check_artifacts IS, and for the same reason: only a name that looks like this
    repo's own code, cited from its own directories. A checker that flags every filename anyone ever
    typed gets switched off, and then it protects nothing.
    """
    known = set()
    for d in CODE_DIRS:
        p = os.path.join(REPO, d)
        if os.path.isdir(p):
            for _root, _dirs, files in os.walk(p):
                known.update(files)
    missing = defaultdict(set)
    for rel, text in _walk_md(DOC_SKIP):
        for m in CODE_CITE.finditer(text):
            name = m.group(1)
            # ⚠ A SUPERSEDED-MARKER LINE IS A RECORD OF A DEAD NAME, NOT A LIVE CITATION. Rule 1.2 says
            # a correction keeps the old value; flagging the retention would make the discipline
            # impossible to follow.
            line = text[text.rfind("\n", 0, m.start()) + 1: text.find("\n", m.end())]
            if any(ph in line.lower() for ph in CODE_CITE_CLEARED):
                continue
            if name not in known:
                missing[name].add(rel)
    for name in sorted(missing):
        cites = sorted(missing[name])
        f.warn("[K3]", f"`{name}` is named by {len(cites)} document(s) "
                       f"({', '.join(cites[:3])}{', …' if len(cites) > 3 else ''}) and is in none of "
                       f"{'/'.join(CODE_DIRS[:4])}/… — either a DEAD POINTER (an instruction the reader "
                       f"cannot follow, which is how CLAUDE.md §6 came to name three exemplar files that "
                       f"exist on no ref) or a file in an EXTERNAL repository, which is fine and should "
                       f"say so in the sentence that names it")


#: ⚠ THE FRAGMENT IS CAPTURED NOW, NOT DISCARDED. This pattern read `(?:#[^)\s]*)?` — matching the
#: anchor and throwing it away — so [K1] proved the FILE existed and said nothing whatever about the
#: section. Measured 2026-08-05: the roadmap carried 35 links to four headings that a plan-extraction
#: commit had deleted, including 24 to `#open-decisions`, whose numbering §0.7 of that same document
#: calls FROZEN and "cited by number in 30 files". Every one passed the link checker.
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]*)(#[^)\s]*)?\)")
LINK_SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "data:")

#: ⚠ A LINK TARGET MUST LOOK LIKE A PATH. Without this, SMILES strings are read as Markdown links —
#: `[nH]` followed by `(C(=O)...` is syntactically a link — and the first run reported 184 "broken
#: links", of which the overwhelming majority were chemistry. A checker that cries wolf gets switched
#: off, so it recognises a path: a slash, or a real file extension.
LOOKS_LIKE_PATH = re.compile(r"/|\.(md|json|py|yml|yaml|mjs|sh|txt|csv|png|svg|pdf|cff|html)$", re.I)


LINK_BASELINE = os.path.join(GRAPH, "link-baseline.json")


def check_links(g, f):
    """Every relative Markdown link resolves to a file that exists. No exemptions.

    ⭐ WHY THIS EXISTS. The repository had NO repo-wide link checker — `verify-refs.yml` validates
    external DOIs, and the only path check in CI inspected `provenance.owner.file`, which for every
    graph row points at one document. So a document could be moved and every link to it would rot in
    silence until someone clicked one.

    That is not hypothetical: this class of breakage is precisely what stopped the archive sweep the
    first time it was attempted, and three of the hazards found then were not links at all but
    runtime reads — which this check deliberately does NOT cover, and cannot. It catches the easy
    class so that attention is free for the hard one.

    ⭐ THE GRANDFATHER LIST IS GONE — IT REACHED ZERO AND WAS DELETED, WHICH IS WHAT IT SAID IT WAS FOR.
    `link-baseline.json` opened at 120 known-broken links and closed at none on 2026-08-05. Keeping an
    empty exemption register would have been strictly worse than deleting it: nothing to exempt, an
    invitation to add, and its loader guarded on `os.path.exists` — so deleting the file by accident
    would have switched the exemption logic to "everything passes" without a word. The two entries it
    ever explained are the reason to be glad it is gone: both carried a plausible FREE-PROSE reason that
    nothing checked, and both were wrong. The first blamed a probe that had never run, when the probe
    had run and committed to `modalities-cache`. The second said rung 5b-T was NOT STARTED, when it had
    run on 2026-08-03 and its signature step had failed silently behind a `|| true`. Full accounting:
    systems/MIGRATION.md §3.8. A broken link is now an error, and an artifact's absence is answered by
    the lane register or systems/graph/artifact-refs.json — which demand evidence, not prose.
    """
    if os.path.exists(LINK_BASELINE):
        f.err("[K0]", "systems/graph/link-baseline.json is back. It reached zero and was deleted on "
                      "2026-08-05 — a link is either fine or an error, and an artifact's absence is "
                      "answered by a lane's `produces[]` or by artifact-refs.json, both of which "
                      "require evidence. This file's `why` was free prose, and both entries it ever "
                      "held carried a confident explanation that turned out to be wrong")
    checked = broken = anchors_checked = 0
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if _is_transient(rel_root):
            dirs[:] = []
            continue
        # ⚠ archive/ is skipped BY DESIGN. Its files moved, so their relative links point at former
        # neighbours — and the directory's own README says nothing in it is live. Checking links in
        # declared-dead documents would generate noise that trains a reader to ignore this check.
        if rel_root.startswith("archive"):
            dirs[:] = []
            continue
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            src = os.path.normpath(os.path.join(rel_root, fn)).replace(os.sep, "/")
            with open(os.path.join(REPO, src), encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            for m in MD_LINK.finditer(text):
                target, frag = m.group(1).strip(), (m.group(2) or "").lstrip("#").strip()
                # A bare `#section` link — the same document. Its file trivially exists; the anchor is
                # the whole content of the link, and is exactly what went unchecked.
                if not target:
                    if frag:
                        anchors_checked += 1
                        if not anchor_resolves(os.path.join(REPO, src), frag):
                            broken += 1
                            f.err("[K2]", f"{src} links to `#{frag}` in ITSELF and no heading makes that "
                                          f"anchor — the section was renamed or deleted")
                    continue
                if target.startswith(LINK_SKIP_PREFIX):
                    continue
                if not LOOKS_LIKE_PATH.search(target):
                    continue
                checked += 1
                dest = os.path.normpath(os.path.join(os.path.dirname(os.path.join(REPO, src)), target))
                if not os.path.exists(dest):
                    broken += 1
                    f.err("[K1]", f"{src} links to {target!r}, which does not exist")
                elif frag and dest.endswith(".md"):
                    anchors_checked += 1
                    if not anchor_resolves(dest, frag):
                        broken += 1
                        f.err("[K2]", f"{src} links to {target}#{frag} — the FILE exists and the SECTION "
                                      f"does not. A link checker that strips the fragment proves the "
                                      f"cheaper half and reports the expensive half as fine")
    # ⛔ INFO, NOT WARN, AND THAT IS THE POINT (2026-08-05). This warned unconditionally — it printed
    # counts whether or not anything was wrong, which is precisely the pattern scripts/preflight.sh's
    # own header calls out: "a check that reports while measuring nothing actionable". A warning list
    # that always contains a line nobody can act on is how the actionable lines get skimmed past. The
    # count still prints, because a link checker silently checking ZERO links is the fail-open shape
    # this repository keeps paying for — the number is what proves it ran.
    f.info("[K0]", f"relative links checked: {checked} (+{anchors_checked} anchors), broken: {broken} — "
                   f"no grandfather list exists; a broken link is an error")


RELATIONS = os.path.join(GRAPH, "relations.json")


def _id_refs(v):
    """Every whole string inside a value, at any nesting depth.

    ⚠ WHOLE STRINGS ONLY, WHICH IS THE WHOLE TRICK. An id quoted INSIDE a sentence -- and this model is
    full of prose that names ids -- is not a reference, it is a mention. Matching substrings would make
    every `why`, `rationale` and `claim_ceiling` look like an edge.
    """
    if isinstance(v, str):
        yield v
    elif isinstance(v, list):
        for x in v:
            yield from _id_refs(x)
    elif isinstance(v, dict):
        for x in v.values():
            yield from _id_refs(x)


def check_relations(g, f):
    """Every edge in the model is declared, with its SysML stereotype or an explicit `domain` reason.

    ⭐ WHY A REGISTER RATHER THAN A COMMENT. Asked on 2026-08-05 whether to re-express the whole model
    in SysML, the measurement was that one relationship family is genuinely SysML's and most of the rest
    are domain relations with no honest counterpart. That conclusion is worth keeping, and a conclusion
    in a session transcript is not kept -- so it is data, per edge, with the reason. [X1] is what stops
    the register falling quietly behind the model.

    ⚠ THE LOAD-BEARING COLUMN IS `asserted`, NOT `sysml`. A derived key written into a source file is a
    second home for a computed fact -- which is how `instrument.serves` came to disagree with the
    requirement register in 11 of 30 rows while a third field computed the same thing and nothing read
    it. [X2] makes that failure impossible to reintroduce.

    ⛔ AN EDGE IS DETECTED STRUCTURALLY, NOT BY NAME. The first draft enumerated non-edge keys by hand
    and produced 30 false errors on its first run -- `path`, `workflow`, `statement_about`, `citation`.
    A checker that cries wolf gets switched off (the same reasoning that keeps SMILES strings out of
    check_links), and a hand-list of exclusions is also the thing that silently stops covering the
    model. So: a key is an edge when one of its values IS an id. Prose is invisible to it, and a new
    relation cannot hide by being named something the author did not think of.
    """
    if not os.path.exists(RELATIONS):
        f.err("[X1]", "systems/graph/relations.json is missing — every edge in the model is declared "
                      "there, and without it nothing stops a new relation appearing unnamed")
        return
    with open(RELATIONS, encoding="utf-8") as fh:
        reg = json.load(fh)
    declared = {(coll, r["key"]): r for r in reg["relations"] for coll in r["on"]}

    ids = {row["id"] for coll in COLLECTIONS for row in g.get(coll, []) if "id" in row}

    # ⚠ ENUMERATED FROM THE SOURCE FILES, NOT FROM THE DERIVED GRAPH. derive() adds the derived keys to
    # the in-memory objects, so checking `g` would find every derived key present everywhere and [X2]
    # could never fire. The question [X2] asks is precisely what is WRITTEN.
    seen = set()
    for coll in COLLECTIONS:
        path = os.path.join(GRAPH, f"{coll}.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
        for row in (rows if isinstance(rows, list) else []):
            for k, v in row.items():
                if k in ("id",) or k.startswith("_"):
                    continue
                if not any(s in ids for s in _id_refs(v)):
                    continue
                seen.add((coll, k))
                rel = declared.get((coll, k))
                if rel is None:
                    f.err("[X1]", f"{coll}.json writes `{k}`, whose values are ids of modelled objects — "
                                  f"so it is an EDGE — and systems/graph/relations.json does not declare "
                                  f"it. Declare it with its SysML stereotype, or with `domain` and the "
                                  f"reason no stereotype fits. An undeclared edge is how a vocabulary "
                                  f"drifts back into twelve ad-hoc names")
                elif not rel["asserted"]:
                    f.err("[X2]", f"{coll}.json WRITES `{k}`, which relations.json declares DERIVED. A "
                                  f"computed fact with a hand-written copy is rule 1's failure mode: the "
                                  f"two drift and the written one wins silently. Delete it — derive() "
                                  f"computes it")

    # A register entry for an edge the model no longer has is the same defect one direction out: it
    # documents a relation nobody can find, and the next reader trusts it.
    for (coll, k), rel in sorted(declared.items()):
        # `id_valued: false` marks an edge whose targets are FILENAMES rather than modelled ids
        # (`lane.produces`), which the structural detector above cannot see by construction. Skipping
        # it here is honest; pretending the detector found it would not be.
        if rel.get("id_valued", True) is False:
            continue
        if rel["asserted"] and (coll, k) not in seen:
            f.warn("[X4]", f"relations.json declares `{coll}.{k}` as an asserted edge and no row in "
                           f"{coll}.json carries it — either the edge was removed and this entry is "
                           f"stale, or it is derived and mis-declared")

    # ⚠ `lane.serves` is prose ON PURPOSE (a lane's target is a rung as often as a requirement, and
    # rungs are not modelled). That licence is bounded HERE: the moment it names a requirement, the
    # relation it wants is `verified_by`, and leaving it as prose recreates the exact two-homes problem
    # the reconciliation removed.
    for lane in g.get("lanes", []):
        for s in lane.get("serves", []):
            if re.fullmatch(r"R\d+", s):
                f.err("[X6]", f"{lane['id']} `serves` names requirement {s} as free text. `lane.serves` "
                              f"is prose for rungs, which are not modelled — a requirement IS modelled, "
                              f"so this belongs in {s}'s `verified_by` or in the lane's `produces[]`")


def run_checks(g, f):
    check_relations(g, f)
    check_schemas(g, f)
    check_legacy_agreement(g, f)
    check_ids_unique(g, f)
    check_hierarchy(g, f)
    check_blockers(g, f)
    check_requirements(g, f)
    check_lanes(g, f)
    check_requirement_source_agreement(g, f)
    check_technologies(g, f)
    check_scan_interop(g, f)
    check_doc_ids(g, f)
    check_documents(g, f)
    check_links(g, f)
    check_artifacts(g, f)
    check_code_citations(g, f)
    check_pointers(g, f)
    check_instrument_support(g, f)
    check_compute_case(g, f)
    return f


# ───────────────────────────── rendering ─────────────────────────────

def _watch_cell(t):
    """How this dependency is watched — three states, because two would lie about one of them."""
    if t.get("scan_trigger"):
        return "yes"
    if t.get("not_scannable_because"):
        return "n/a — watched another way"
    return "⚠ **no**"


GLYPH = {"complete": "✓", "in_work": "◐", "future": "○", "parked": "⏸", "dead": "✕"}
BANNER = ("<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:\n"
          "     python3 systems/systems_check.py --write-views\n"
          "     Source of truth: systems/graph/*.json -->\n")


def fm(**kw):
    lines = ["---"]
    for k, v in kw.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(json.dumps(x, ensure_ascii=False) for x in v)}]")
        else:
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}" if isinstance(v, str) and (":" in v or "#" in v) else f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def route_slug(rid):
    return rid.lower()


# ───────────────────────────── diagrams ─────────────────────────────
#
# ⭐ WHY THESE EXIST. 57 of the 58 generated views were tables. A table is the right instrument for a
# VALUE and the wrong one for a SHAPE — and the most important fact about this portfolio is a shape:
# `BLK-NO-WET-LAB` and `BLK-NOT-FUSION-SELECTIVE` each hold down SIX of the nine strategy families. Every
# route page states its own blockers correctly and none of them can show that convergence; reading it off
# the tables means opening forty pages and counting, which is exactly the re-derivation this model exists
# to end.
#
# ⛔ A DIAGRAM THAT REDRAWS ITS OWN TABLE IS WASTE. Each one below shows something structural that the
# table beside it cannot, and each states what it left out — an omission a reader cannot see is a lie by
# composition.
#
# ⚠ THEY ARE GENERATED, so `check_views` re-renders and diffs them like every other view. That is also
# why every list here is SORTED: a dict-ordering dependence would turn CI red on an unrelated commit.

#: Mermaid node ids must be bare identifiers. `-` terminates one in several contexts and `BLK-NO-WET-LAB`
#: is full of them, so ids are sanitised rather than interpolated raw.
_MM_ID_BAD = re.compile(r"[^A-Za-z0-9_]")

#: ⛔ NEVER ENCODE MEANING IN COLOUR ALONE. These render on GitHub in both light and dark themes, and
#: readers are not all trichromatic. Meaning is carried by NODE SHAPE and EDGE STYLE; the classDefs below
#: set stroke weight only and deliberately set NO `fill`, because a fill chosen for one theme disappears
#: in the other. Shapes used, consistently across all three levels:
#:     ["…"]      a family or a route          — a thing we are doing
#:     {{"…"}}    a blocker that CAN be retired — a thing in the way, with a way out
#:     [["…"]]    a PERMANENT blocker           — a fact about the world, double-walled, no way out
#:     (["…"])    a technology                  — a capability we are waiting for
#: and edges:  `-->` holds down (real, today)   `-.->` would retire (hypothetical, has not landed)
MM_CLASSDEF = [
    "  classDef fam stroke-width:2px;",
    "  classDef blk stroke-width:2px;",
    "  classDef perm stroke-width:4px;",
    "  classDef tech stroke-width:1px,stroke-dasharray:4 3;",
]


def mm_id(x):
    """A mermaid-safe node id derived from a graph id. Injective over this graph's id namespace."""
    return _MM_ID_BAD.sub("_", str(x))


def plural(n, one, many=None):
    """`1 blocker`, `2 blockers` — never `1 blocker(s)`.

    Small, and it earns its place: these strings sit under a diagram a reader is already squinting at,
    and `(s)` is the tell of generated prose nobody proof-read.
    """
    return f"{n} {one}" if n == 1 else f"{n} {many or one + 's'}"


def mermaid_label(s, width=46):
    """Text that is safe inside a mermaid node label.

    ⛔ `esc()` IS WRONG HERE AND SILENTLY SO. It escapes table pipes; mermaid cares about entirely
    different characters. An unescaped `"` or `(` TERMINATES the node, and the resulting parse error
    renders on GitHub as a BLANK SPACE where the diagram should be — no error, no warning, nothing that
    any check in this repository would have caught. The graph is full of the hazardous characters
    already: route display names carry `(`, `)` and `/`, and strategy titles carry `—` and `·`.

    So the label is always emitted wrapped in `["…"]` by the callers, and this function guarantees the
    inside of those quotes is inert: `"` becomes the `#quot;` entity, brackets are stripped rather than
    escaped (mermaid's escaping of them is version-dependent and this needs to be boring), and newlines
    and pipes cannot survive at all.
    """
    t = re.sub(r"\s+", " ", str(s or "")).strip()
    t = t.replace('"', "#quot;")
    t = re.sub(r"[\[\]{}()<>|\\]", "", t)
    if len(t) > width:
        t = t[: width - 1].rstrip() + "…"
    return t


def _families_per_blocker(g):
    """{blocker id -> sorted set of strategy ids whose routes inherit it}. DERIVED, never typed."""
    fam = {r["id"]: r.get("strategy") for r in g["routes"]}
    out = defaultdict(set)
    for b in g["blockers"]:
        for rid in b.get("inherited_by") or []:
            if fam.get(rid):
                out[b["id"]].add(fam[rid])
    return {k: sorted(v) for k, v in out.items()}


def _blk_node(b, ident=None):
    """A blocker node. A PERMANENT blocker is drawn differently, and that is not decoration.

    `PERMANENT_KINDS` blockers are facts about what the objects ARE. `[B1]` already refuses any technology
    claiming to retire one; drawing them identically to a retirable blocker would reintroduce exactly that
    conflation visually, in the one artifact a reader takes in at a glance rather than reads.
    """
    i = ident or mm_id(b["id"])
    lab = mermaid_label(f"{b['id']} — {b['name']}", 58)
    return (f'  {i}[["{lab}"]]:::perm' if b["permanent"] else f'  {i}{{{{"{lab}"}}}}:::blk')


def diagram_l0(g):
    """The landscape: nine families, and ONLY the blockers that cut across two or more of them."""
    fams = _families_per_blocker(g)
    blk = by_id(g["blockers"])
    cross = sorted((b for b, f in fams.items() if len(f) >= 2),
                   key=lambda b: (-len(fams[b]), b))
    local = sorted(b for b, f in fams.items() if len(f) == 1)
    if not cross:
        return ["*No blocker holds down more than one family — the portfolio has no shared chokepoint, "
                "which would itself be the finding.*", ""]

    out = ["```mermaid", "flowchart LR"]
    for b in cross:
        # ⭐ THE FAMILY COUNT GOES IN THE LABEL, not only in the edge fan. A reader who scans rather than
        # traces still has to be able to see that two of these hold down six families each — which is the
        # single fact this diagram exists to deliver.
        # ⚠ THE UNIT IS IN THE LABEL BECAUSE THE TABLE BELOW COUNTS A DIFFERENT ONE. This diagram ranks
        # by FAMILIES spanned; "What holds the portfolio down" ranks by ROUTES held. Both are correct and
        # they disagree — BLK-NO-EMC-DATA leads on routes (15) and is third on families (5) — so a bare
        # number here reads as a contradiction with the table three inches below it, and a reader who
        # spots a contradiction stops trusting the page rather than looking for the unit.
        n = len(fams[b])
        lab = mermaid_label(f"{b} — {plural(n, 'family', 'families')}", 52)
        out.append(f'  {mm_id(b)}[["{lab}"]]:::perm' if blk[b]["permanent"]
                   else f'  {mm_id(b)}{{{{"{lab}"}}}}:::blk')
    out.append("")
    for s in sorted(g["strategies"], key=lambda x: (-len(x["routes"]), x["id"])):
        ss = s["summary_state"]
        lab = mermaid_label(f"{s['id']} {GLYPH.get(s['state']['work_state'], '?')} · "
                            f"{plural(ss['n_routes'], 'route')}", 40)
        out.append(f'  {mm_id(s["id"])}["{lab}"]:::fam')
    out.append("")
    for b in cross:
        for sid in fams[b]:
            out.append(f"  {mm_id(b)} --> {mm_id(sid)}")
    out += MM_CLASSDEF + ["```", ""]
    out += [f"**Reading it.** A hexagon is a blocker with a named way out; a double-walled box is a "
            f"**permanent** one — a fact about the biology that no technology retires. An arrow means "
            f"*holds down*.\n",
            f"⚠ **{len(local)} further blocker(s) are NOT drawn here**, because each holds down exactly "
            f"one family and belongs on that family's page. Drawing all "
            f"{len(cross) + len(local)} would render the portfolio as a hairball and bury the "
            f"{len(cross)} that shape it. Every one of them is in "
            f"[registers/blockers.md](registers/blockers.md).\n"]
    return out


def diagram_l1(s, g):
    """One family: its routes, and whether it is blocked as a UNIT or route-by-route."""
    rt, blk = by_id(g["routes"]), by_id(g["blockers"])
    routes = [rt[r] for r in sorted(s["routes"]) if r in rt]
    if not routes:
        return []
    shared = set(s.get("shared_blockers") or [])
    per = defaultdict(set)
    for r in routes:
        for b in r.get("blockers_inherited") or []:
            if b not in shared:
                per[b].add(r["id"])

    out = ["```mermaid", "flowchart LR"]
    fid = mm_id(s["id"])
    out.append(f'  {fid}["{mermaid_label(s["id"], 40)}"]:::fam')
    for r in routes:
        lab = mermaid_label(f"{GLYPH.get(r.get('state', {}).get('work_state'), '?')} {r['id']}", 40)
        out.append(f'  {mm_id(r["id"])}["{lab}"]:::fam')
        out.append(f"  {fid} --> {mm_id(r['id'])}")
    out.append("")
    for b in sorted(shared):
        if b in blk:
            out.append(_blk_node(blk[b]))
            out.append(f"  {mm_id(b)} --> {fid}")
    for b in sorted(per):
        if b in blk:
            out.append(_blk_node(blk[b]))
            for rid in sorted(per[b]):
                out.append(f"  {mm_id(b)} --> {mm_id(rid)}")
    out += MM_CLASSDEF + ["```", ""]

    if shared:
        out.append(f"**Reading it.** {plural(len(shared), 'blocker')} point at the FAMILY node: every route "
                   f"here inherits {'it' if len(shared) == 1 else 'them'}, so the family stands or "
                   f"falls as a unit on that. The rest point at individual routes.\n")
    else:
        out.append("**Reading it.** ⭐ **No blocker points at the family node**, and that is the finding: "
                   "the routes here are *not* held down by one shared thing. They are blocked "
                   "individually, for different reasons — so retiring any one blocker frees some routes "
                   "and not others, and there is no single unlock for the family.\n")
    out.append("*What this family RETIRES for the portfolio is listed below rather than drawn — it is a "
               "property of the family, not an edge between these nodes.*\n")
    return out


def diagram_l2(r, g):
    """One route: the path from blocked to unblocked, and what it has already cleared."""
    blk, tk, fc = by_id(g["blockers"]), by_id(g["technologies"]), by_id(g["forecasts"])
    inherited = sorted(r.get("blockers_inherited") or [])
    retired = sorted(r.get("blockers_retired") or [])
    if not inherited and not retired:
        return ["*This route inherits no blocker and retires none — there is no dependency structure to "
                "draw. Its state is decided by the evidence on this page alone.*", ""]

    out = ["```mermaid", "flowchart LR"]
    rid = mm_id(r["id"])
    r_gly = GLYPH.get((r.get("state") or {}).get("work_state"), "?")
    r_lab = mermaid_label(f"{r_gly} {r['id']}", 40)
    out.append(f'  {rid}["{r_lab}"]:::fam')
    for b in inherited:
        if b not in blk:
            continue
        out.append(_blk_node(blk[b]))
        out.append(f"  {mm_id(b)} --> {rid}")
        # ⛔ A permanent blocker gets NO incoming technology edge — see _blk_node.
        if blk[b]["permanent"]:
            continue
        for t in sorted(blk[b].get("retired_by_technology") or []):
            if t not in tk:
                continue
            band = ((fc.get(tk[t].get("forecast")) or {}).get("scenarios", {})
                    .get("expected", {}).get("date_band", "—"))
            # ⚠ TWO LINES, NOT ONE TRUNCATED ONE. On a single line the longest technology ids run past
            # the width and the FORECAST BAND — the only reason this node is on the diagram — is what
            # gets cut. `<br/>` is legal inside a quoted mermaid label and keeps both readable.
            lab = f"{mermaid_label(t, 44)}<br/>expected {mermaid_label(band, 18)}"
            out.append(f'  {mm_id(t)}(["{lab}"]):::tech')
            out.append(f"  {mm_id(t)} -.-> {mm_id(b)}")
    out += MM_CLASSDEF + ["```", ""]

    unresolved = [b for b in inherited if b in blk and not blk[b]["permanent"]
                  and not blk[b].get("retired_by_technology")]
    perm = [b for b in inherited if b in blk and blk[b]["permanent"]]
    note = ["**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a "
            "capability that WOULD retire a blocker — dashed because it has not landed, and the date "
            "beside it is a forecast, not a schedule.\n"]
    if perm:
        note.append(f"⛔ **{plural(len(perm), 'of these is permanent', 'of these are permanent')}** "
                    f"({', '.join('`' + b + '`' for b in perm)}) "
                    f"— a fact about the biology, drawn double-walled, with no way out by definition. No "
                    f"technology arrives to fix it.\n")
    if unresolved:
        note.append(f"⚠ **{plural(len(unresolved), 'blocker')} here {'has' if len(unresolved) == 1 else 'have'}"
                    f" no technology named at all** "
                    f"({', '.join('`' + b + '`' for b in unresolved)}) — not *waiting*, **unaddressed**. "
                    f"A blocker with no named way out is the most expensive kind, because nothing is "
                    f"being watched for it.\n")
    if retired:
        note.append(f"✓ Already cleared by this route: {', '.join('`' + b + '`' for b in retired)}.\n")
    return out + note


def render_l0(g):
    st, rt = g["strategies"], by_id(g["routes"])
    blk = by_id(g["blockers"])
    out = [fm(id="DOC-VIEW-L0", title="L0 — the EMC research ecosystem", level="L0", kind="generated",
              status="generated", generator="systems/systems_check.py",
              purpose="The complete landscape in one screen: every strategy family, its state, and what holds it down.",
              scope="Level 0. Detail appears on drill-down, never here.",
              audience=["maintainers", "autonomous research agents", "external reviewers"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER,
           "# L0 — the EMC research ecosystem\n",
           "> Extraskeletal myxoid chondrosarcoma, driven by the EWSR1::NR4A3 fusion. One researcher, no wet",
           "> lab, no funding for one — so every advance is either in-silico or publish-to-convince.",
           "> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.**\n",
           f"**{len(g['strategies'])} strategy families · {len(g['routes'])} routes · "
           f"{len(g['blockers'])} blockers · {len(g['technologies'])} technology dependencies.**\n",
           "## The shape of the portfolio\n",
           "What one screen has to carry is not the list — it is the **convergence**. Each family page"
           " states its own blockers correctly; only this shows how many families they span.\n",
           "⚠ **This ranks by FAMILIES spanned. [What holds the portfolio down](#what-holds-the-portfolio-down)"
           " below ranks by ROUTES held, and the two orders differ** — a blocker can sit on many routes"
           " inside one family, or on one route in each of many. Both are real and they answer different"
           " questions: *how much work is stuck* versus *how much of the strategy is stuck*.\n"]
    out += diagram_l0(g)
    out += ["## The landscape\n",
            "| family | thesis | routes | state | role |",
            "|---|---|---:|---|---|"]
    for s in st:
        ss = s["summary_state"]
        gly = GLYPH.get(s["state"]["work_state"], "?")
        out.append(f"| **[{s['id']}](L1-{s['id'].lower()}.md)**<br/>{esc(s['title'])} | {esc(s['thesis'][:150])}… "
                   f"| {ss['n_routes']} | {gly} {s['state']['status']} · {s['state']['maturity']} "
                   f"| {s['portfolio_role']} |")

    out += ["", "## What holds the portfolio down\n",
            "A blocker on one route is a risk. A blocker on fifteen is the portfolio's shape.\n",
            "⚠ **Ranked by ROUTES held — a different axis from the diagram above**, which ranks by families"
            " spanned. The top of this list and the top of that one are not the same blocker, and neither"
            " is wrong: `BLK-NO-EMC-DATA` holds the most ROUTES while sitting in fewer FAMILIES than"
            " `BLK-NO-WET-LAB`. Read the diagram for *how much of the strategy is stuck* and this table"
            " for *how much work is stuck*.\n",
            "| blocker | kind | routes held | families | retired by |", "|---|---|---:|---:|---|"]
    fam_span = _families_per_blocker(g)
    for b in sorted(g["blockers"], key=lambda x: -len(x["inherited_by"])):
        if not b["inherited_by"]:
            continue
        out_by = ", ".join(f"`{t}`" for t in b["retired_by_technology"]) or \
            ("*permanent — nothing*" if b["permanent"] else "*an action we can take*")
        out.append(f"| **{b['id']}** | `{b['kind']}` | {len(b['inherited_by'])} "
                   f"| {len(fam_span.get(b['id'], []))} | {out_by} |")

    out += ["", "## Highest-leverage things to wait for\n",
            "Ordered by how much comes back if they land. Full register: "
            "[registers/technologies.md](registers/technologies.md).\n",
            "| fan-out | technology | state | expected | basis |", "|---:|---|---|---|---|"]
    fc = by_id(g["forecasts"])
    for t in sorted(g["technologies"], key=lambda x: -x["fan_out"])[:10]:
        c = fc.get(t.get("forecast"), {})
        exp = c.get("scenarios", {}).get("expected", {}).get("date_band", "—")
        out.append(f"| {t['fan_out']} | **{t['id']}** | `{t['current_state']}` | {exp} | `{c.get('basis','—')}` |")

    out += ["", "## Drill down\n",
            "- **L1** — a strategy family: `L1-<family>.md`",
            "- **L2** — a single route: `L2-<route>.md`",
            "- **Registers** — [lanes](registers/lanes.md) *(executed work and how it ended)* · "
            "[blockers](registers/blockers.md) · [technologies](registers/technologies.md) · "
            "[instruments](registers/instruments.md)",
            "- **Cross-cutting** — [methods index](methods-index.md) · [readiness](readiness.md) · "
            "[requirements](registers/requirements.md)",
            "- **Multi-year** — [the roadmap](roadmap-5yr.md): scientific, technology, AI-capability and "
            "lab-capability milestones, and when blocked work becomes revisitable",
            "- **Architecture** — [../ARCHITECTURE.md](../ARCHITECTURE.md) · "
            "[../CONVENTIONS.md](../CONVENTIONS.md) · [../MAINTENANCE.md](../MAINTENANCE.md) · "
            "[../MIGRATION.md](../MIGRATION.md)",
            ""]
    return "\n".join(out)


def render_l1(s, g):
    rt = by_id(g["routes"])
    out = [fm(id=f"DOC-VIEW-{s['id']}", title=f"{s['id']} — {s['title']}", level="L1", kind="generated",
              status="generated", generator="systems/systems_check.py",
              purpose=s["purpose"], scope=f"Level 1. {len(s['routes'])} routes.",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER,
           f"# {s['id']} — {s['title']}\n",
           f"**Thesis.** {s['thesis']}\n",
           f"**Portfolio role:** `{s['portfolio_role']}` · "
           f"**state:** {GLYPH.get(s['state']['work_state'],'?')} {s['state']['status']} · "
           f"{s['state']['maturity']} · confidence {s['state']['confidence']}\n"]
    if s.get("purpose_note"):
        out.append(f"> {s['purpose_note']}\n")
    if s.get("limitations"):
        out += ["## What this family may NOT be used to claim\n"] + \
               [f"- {x}" for x in s["limitations"]] + [""]

    out += ["## Is this family blocked as a unit, or route by route?\n"]
    out += diagram_l1(s, g)
    out += ["## Routes\n", "| route | state | maturity | readiness today | next action |", "|---|---|---|---|---|"]
    for rid in s["routes"]:
        r = rt[rid]
        st = r.get("state", {})
        rd = (r.get("readiness") or {}).get("attainable_today", "—")
        na = (r.get("next") or {}).get("best_next_action", "—")
        out.append(f"| **[{rid}](L2-{route_slug(rid)}.md)**<br/>{esc(r.get('display_name', r.get('title','')))} "
                   f"| {GLYPH.get(st.get('work_state'),'?')} {st.get('status','—')} | {st.get('maturity','—')} "
                   f"| `{rd}` | {esc(na[:110])} |")

    if s.get("shared_blockers"):
        out += ["", "## Family-level bets — blockers EVERY route here inherits\n",
                "If one of these is never retired, the whole family is dead. That is a different risk from any",
                "single route failing, and it is only visible at this level.\n"]
        bk = by_id(g["blockers"])
        for b in s["shared_blockers"]:
            out.append(f"- **{b}** (`{bk[b]['kind']}`) — {esc(bk[b]['name'])}")
        out.append("")
    if s.get("distinguishing_blockers"):
        out += ["## What this family buys the portfolio — blockers it RETIRES\n"]
        bk = by_id(g["blockers"])
        for b in s["distinguishing_blockers"]:
            out.append(f"- **{b}** (`{bk[b]['kind']}`) — {esc(bk[b]['name'])}")
        out.append("")
    nx = s.get("next", {})
    if nx:
        out += ["## Best next action\n", f"{nx.get('best_next_action','—')}\n",
                f"*Cost:* {nx.get('cost','—')}\n"]
    out.append("[← L0](L0-ecosystem.md)\n")
    return "\n".join(out)


def render_l2(r, g):
    bk, tk, fc = by_id(g["blockers"]), by_id(g["technologies"]), by_id(g["forecasts"])
    st = r.get("state", {})
    name = r.get("display_name") or r.get("title") or r["id"]
    out = [fm(id=f"DOC-VIEW-{r['id']}", title=f"{r['id']} — {name}", level="L2", kind="generated",
              status="generated", generator="systems/systems_check.py",
              purpose=r.get("purpose", name), scope="Level 2 — one route.",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER,
           f"# {r['id']} — {name}\n",
           f"**Family:** [{r['strategy']}](L1-{r['strategy'].lower()}.md) · "
           f"**state:** {GLYPH.get(st.get('work_state'),'?')} {st.get('status','—')} · "
           f"{st.get('maturity','—')} · confidence {st.get('confidence','—')} · "
           f"verified {st.get('last_verified','—')}\n"]
    if r.get("grade"):
        gv = r["grade"]
        own = gv.get("owner", {})
        # ⚠ The anchor may be null, and it may carry a disambiguating `|` suffix the target file has no
        # heading for. Concatenating either produced links like `...IDEAS.mdroute-board|af3` — caught by
        # the link checker on its first run, in output this module generates.
        anchor = own.get("anchor") or ""
        if anchor and "|" not in anchor:
            anchor = anchor if anchor.startswith("#") else "#" + anchor
        else:
            anchor = ""
        rel_target = os.path.relpath(os.path.join(REPO, own.get("file", ".")), VIEWS)
        out.append(f"**Grade** (owned by [`{own.get('file','?')}`]({rel_target}{anchor})): "
                   f"{esc(gv.get('value',''))}\n")
    out += ["## What has to land for this route to move\n"]
    out += diagram_l2(r, g)
    if r.get("rationale"):
        out += ["## Scientific rationale\n", r["rationale"], ""]
    if r.get("supporting_evidence"):
        out += ["## Supporting evidence\n", "| ref | supports | strength |", "|---|---|---|"]
        for e in r["supporting_evidence"]:
            out.append(f"| `{e['ref']}` | {esc(e['what_it_supports'])} | `{e.get('strength','—')}` |")
        out.append("")
    if r.get("remaining_unknowns"):
        out += ["## Remaining unknowns\n"] + [f"- {x}" for x in r["remaining_unknowns"]] + [""]
    if r.get("required_validation"):
        out += ["## Required validation\n", "| what | instrument | feasible today | blocked by |", "|---|---|---|---|"]
        for v in r["required_validation"]:
            out.append(f"| {esc(v['what'])} | {v.get('instrument') or '⛔ none built'} "
                       f"| {'yes' if v['feasible_today'] else '**no**'} "
                       f"| {', '.join(v.get('blocked_by', [])) or '—'} |")
        out.append("")
    if r.get("blockers_inherited"):
        out += ["## Blockers\n", "| blocker | kind | what would retire it |", "|---|---|---|"]
        for b in r["blockers_inherited"]:
            row = bk.get(b, {})
            outs = ", ".join(f"`{t}`" for t in row.get("retired_by_technology", []))
            if not outs:
                outs = row.get("retired_by_action") or ("*permanent*" if row.get("permanent") else "—")
            out.append(f"| **{b}** | `{row.get('kind','?')}` | {esc(outs)} |")
        out.append("")
    if r.get("blockers_retired"):
        out += ["## Blockers this route RETIRES\n"] + \
               [f"- **{b}** — {esc(bk.get(b,{}).get('name',''))}" for b in r["blockers_retired"]] + [""]

    rd = r.get("readiness")
    if rd:
        out += ["## Readiness — what this could become today\n",
                f"**`{rd['attainable_today']}`**\n"]
        if rd.get("why_not_higher"):
            out.append(f"{rd['why_not_higher']}\n")
        for key, label in [("missing", "Missing"), ("evidence_required", "Evidence required"),
                           ("experiment_required", "Experiment required")]:
            if rd.get(key):
                out += [f"**{label}:**"] + [f"- {x}" for x in rd[key]] + [""]

    tm = r.get("timing")
    if tm:
        out += ["## Strategic timing — the wait equation\n",
                f"**Recommendation: `{tm['recommendation']}`**\n", tm["rationale"], ""]
        rows = [("Six months", tm.get("six_month_delta")), ("Two years", tm.get("two_year_delta")),
                ("Cost trend", tm.get("cost_trend")), ("Automation outlook", tm.get("automation_outlook"))]
        rows = [(k, v) for k, v in rows if v]
        if rows:
            out += ["| horizon | effect |", "|---|---|"] + [f"| {k} | {esc(str(v))} |" for k, v in rows] + [""]
        if tm.get("revisit_trigger"):
            out += ["**Revisit when:**"]
            for t in tm["revisit_trigger"]:
                c = fc.get(tk.get(t, {}).get("forecast"), {})
                exp = c.get("scenarios", {}).get("expected", {}).get("date_band", "—")
                out.append(f"- **{t}** — {esc(tk.get(t,{}).get('name','')[:130])} "
                           f"*(expected {exp}, basis `{c.get('basis','—')}`)*")
            out.append("")

    if r.get("compute_case"):
        cc = r["compute_case"]
        out += ["## Compute case\n",
                f"- **Why compute rather than more reasoning:** {cc['why']}",
                f"- **Expected value:** {cc['expected_value']}",
                f"- **Resources:** {cc['resources']}",
                f"- **Uncertainty:** {cc['uncertainty']}",
                f"- **Decision criteria (fixed before the run):** {cc['decision_criteria']}",
                f"- **Reasoning already exhausted:** {', '.join(cc['reasoning_exhausted'])}", ""]

    if r.get("closure_kind") and r["closure_kind"] != "open":
        out += ["## Closure\n", f"`{r['closure_kind']}` — {esc(r.get('closure_note',''))}\n"]
    nx = r.get("next", {})
    if nx.get("best_next_action"):
        out += ["## Best next action\n", nx["best_next_action"], "", f"*Cost:* {nx.get('cost','—')}\n"]
    out.append(f"[← {r['strategy']}](L1-{r['strategy'].lower()}.md) · [← L0](L0-ecosystem.md)\n")
    return "\n".join(out)


def render_lanes(g):
    """Executed work, with its lifecycle — the level the model was missing until 2026-08-05."""
    order = {"running": 0, "held": 1, "parked": 2, "complete": 3}
    lanes = sorted(g["lanes"], key=lambda l: (order.get(l["state"], 9), l["id"]))
    live = [l for l in lanes if l["state"] != "complete"]
    out = [fm(id="DOC-VIEW-LANES", title="Lane register — executed work and how it ended",
              level="cross-cutting", kind="generated", status="generated",
              generator="systems/systems_check.py",
              purpose="Every unit of work that has RUN, its state, how it ended, and the artifacts it "
                      "owed — so that an artifact's absence is answerable by lookup rather than by "
                      "reading prose.",
              scope="All lanes named anywhere in the repository. Enumerated, not curated.",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER,
           "# Lane register — executed work and how it ended\n",
           "> **Role:** a ROUTE is a strategic option (*could we do X?*); a REQUIREMENT is *what must be "
           "TRUE*; a **LANE is *we ran X, and here is how it ended*.**\n",
           "⛔ **WHY THIS EXISTS.** Executed work had no object in the model, so *\"this lane closed\"* "
           "lived only as a struck-through row in roadmap prose. Prose is not queryable — which is how, "
           "on 2026-08-05, an artifact belonging to a lane that had closed on 2026-07-30 was read as a "
           "gap to fill, and **88.5 minutes of CI went at it**. A state the model holds cannot be missed "
           "that way.\n",
           f"**{len(g['lanes'])} lanes · {len(live)} not yet complete.**\n",
           "⚠ **A null result is `complete`, not a separate state.** The state answers exactly one "
           "question — *will this lane still produce what it owes?* — so a lane that ended with its gate "
           "FAILING is finished, with the verdict in its terminus. Collapsing those would make a settled "
           "negative look like an outstanding task, which is how dead work gets re-run.\n",
           "| lane | state | how it ended / what it waits on | owed artifacts |",
           "|---|---|---|---|"]
    for l in lanes:
        owed = l.get("produces") or []
        art = "<br/>".join(
            f"{'✓' if p['produced'] else '✕'} `{p['artifact']}`" for p in owed) or "—"
        gate = f"<br/>⏸ **gate:** {esc(l['gate'])}" if l.get("gate") else ""
        out.append(f"| **{l['id']}**<br/>{esc(l['title'][:70])} | `{l['state']}`"
                   f"{'<br/>' + l['closed_on'] if l.get('closed_on') else ''} "
                   f"| {esc(l['terminus'][:230])}{gate} | {art} |")
    never = [(l, p) for l in lanes for p in (l.get("produces") or []) if not p["produced"]]
    if never:
        out += ["", "## Artifacts a lane owed and never produced\n",
                "⭐ **This table is the one that stops an absence being read as a gap.** A `complete` "
                "lane produces nothing further, so anything it never produced is a **withdrawn "
                "citation** — the document is what needs fixing, not the artifact. `check_artifacts` "
                "derives exactly that, which is why no human has to assert it.\n",
                "| artifact | lane | lane state | ⇒ disposition |", "|---|---|---|---|"]
        for l, p in never:
            out.append(f"| `{p['artifact']}` | {l['id']} | `{l['state']}` "
                       f"| **{LANE_STATE_DISPOSITION.get(l['state'], '?')}** |")
        out.append("")
    out.append("[← L0](../L0-ecosystem.md)\n")
    return "\n".join(out)


def render_blockers(g):
    out = [fm(id="DOC-VIEW-BLOCKERS", title="Blocker register", level="cross-cutting", kind="generated",
              status="generated", generator="systems/systems_check.py",
              purpose="Every reason work is stalled, typed, ordered by how much of the portfolio it holds down.",
              scope="All blockers. Vocabulary and selection rules: systems/taxonomy/blockers.md",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Blocker register\n",
           "Typed with [`taxonomy/blockers.md`](../../taxonomy/blockers.md). The kinds are **never conflated**:",
           "*the biology forbids it*, *today's method cannot resolve it*, *nobody has run the assay* and",
           "*we have not been given the decision* are four situations with four different remedies.\n"]
    counts = defaultdict(int)
    for b in g["blockers"]:
        counts[b["kind"]] += 1
    out += ["## By kind\n", "| kind | n | permanent |", "|---|---:|---|"]
    for k in sorted(counts):
        out.append(f"| `{k}` | {counts[k]} | {'**yes**' if k in PERMANENT_KINDS else 'no'} |")
    out += ["", "## By fan-out — the portfolio's shape\n",
            "| blocker | kind | routes held | routes that retire it | what would retire it |",
            "|---|---|---:|---:|---|"]
    for b in sorted(g["blockers"], key=lambda x: -len(x["inherited_by"])):
        outs = ", ".join(f"`{t}`" for t in b["retired_by_technology"])
        if not outs:
            outs = ("**permanent — nothing**" if b["permanent"]
                    else (b.get("retired_by_action", "—")[:120] + "…" if b.get("retired_by_action") else "—"))
        out.append(f"| **{b['id']}**<br/>{esc(b['name'][:90])} | `{b['kind']}` | {len(b['inherited_by'])} "
                   f"| {len(b['retired_by'])} | {esc(outs)} |")
    out += ["", "## Detail\n"]
    for b in sorted(g["blockers"], key=lambda x: -len(x["inherited_by"])):
        out += [f"### {b['id']}\n", f"**{esc(b['name'])}**\n",
                f"- **kind:** `{b['kind']}`{' · **PERMANENT**' if b['permanent'] else ''}",
                f"- **a statement about:** {b['statement_about']}",
                f"- **held by ({len(b['inherited_by'])}):** " + (", ".join(b["inherited_by"]) or "—"),
                f"- **retired by route ({len(b['retired_by'])}):** " + (", ".join(b["retired_by"]) or "—")]
        if b["retired_by_technology"]:
            out.append(f"- **retired by technology:** " + ", ".join(b["retired_by_technology"]))
        if b.get("retired_by_action"):
            out.append(f"- **⭐ retired by an action we can take:** {b['retired_by_action']}")
        if b.get("evidence"):
            out.append("- **evidence:** " + " / ".join(b["evidence"]))
        own = b.get("owner", {})
        out += [f"- **owner:** `{own.get('file','—')}{own.get('anchor','')}`", ""]
    out.append("[← L0](../L0-ecosystem.md)\n")
    return "\n".join(out)


def render_technologies(g):
    fc = by_id(g["forecasts"])
    out = [fm(id="DOC-VIEW-TECHNOLOGIES", title="Technology-dependency register and forecasts",
              level="cross-cutting", kind="generated", status="generated",
              generator="systems/systems_check.py",
              purpose="What would unblock the work, how much comes back if it lands, and when it is expected.",
              scope="All technology dependencies and their forecasts. Vocabulary: systems/taxonomy/technology.md",
              audience=["maintainers", "autonomous research agents", "external reviewers"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Technology-dependency register\n",
           "> **A coming capability justifies waiting and re-running. It never licences claiming the result",
           "> before the method can support it.**\n",
           "Every forecast declares its `basis` — `evidence_based`, `extrapolated` or `speculative`. An",
           "unlabelled forecast is indistinguishable from a measurement.\n",
           "## Ordered by fan-out\n",
           "| fan-out | technology | category | state | conservative | expected | optimistic | basis | impact | scanned |",
           "|---:|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(g["technologies"], key=lambda x: -x["fan_out"]):
        c = fc.get(t.get("forecast"), {})
        s = c.get("scenarios", {})
        out.append(f"| {t['fan_out']} | **{t['id']}** | `{t['category']}` | `{t['current_state']}` "
                   f"| {s.get('conservative',{}).get('date_band','—')} "
                   f"| **{s.get('expected',{}).get('date_band','—')}** "
                   f"| {s.get('optimistic',{}).get('date_band','—')} "
                   f"| `{c.get('basis','—')}` | `{c.get('expected_impact','—')}` "
                   f"| {_watch_cell(t)} |")
    # ⚠ THREE STATES, NOT TWO. "scanned", "deliberately not scanned, watched another way" and
    # "nobody is looking" are different facts, and collapsing the middle one into ⚠ **no** is what
    # made the register read as having a hole where it has a stated decision.
    unscanned = [t["id"] for t in g["technologies"]
                 if not t.get("scan_trigger") and not t.get("not_scannable_because")]
    other = [t["id"] for t in g["technologies"]
             if not t.get("scan_trigger") and t.get("not_scannable_because")]
    if unscanned:
        out += ["", f"⚠ **{len(unscanned)} dependencies have no literature scan**, so they could land without",
                "anyone noticing: " + ", ".join(f"`{x}`" for x in unscanned) + ".\n"]
    if other:
        out += ["", f"**{len(other)} dependency(ies) cannot be seen by a literature search and are watched",
                "another way** — each says how, under `not_scannable_because` in its Detail entry: "
                + ", ".join(f"`{x}`" for x in other) + ". ⛔ This is a recorded decision, not a gap; the",
                "alternative was a fabricated query that reports nothing forever while being credited",
                "as coverage.\n"]
    out += ["## Detail\n"]
    for t in sorted(g["technologies"], key=lambda x: -x["fan_out"]):
        c = fc.get(t.get("forecast"), {})
        u = t.get("unblocks", {})
        out += [f"### {t['id']} — fan-out {t['fan_out']}\n", f"**{esc(t['name'])}**\n",
                f"*Category:* `{t['category']}` · *state:* `{t['current_state']}` · "
                f"*confidence in that state:* `{t['confidence']}`\n",
                f"**Why it matters.** {t['why_it_matters']}\n"]
        ungraded = [x for x in t.get("pending_signals", []) if not x.get("graded")]
        if ungraded:
            out += [f"> ⏳ **{len(ungraded)} UNGRADED SCAN SIGNAL(S) — read and grade these.** The weekly "
                    f"scan matched them on this dependency's own queries. ⚠ **They are unvalidated "
                    f"leads, machine-matched on a title and not read** — the scan deliberately cannot "
                    f"change `current_state`, so nothing below reflects them yet.", ">"]
            for x in ungraded[:8]:
                out.append(f"> - `{x['trg']}` · *{esc(x.get('title',''))}* "
                           f"({esc(x.get('venue',''))}, {x.get('date','')}) — seen {x.get('seen_on','')}")
            if len(ungraded) > 8:
                out.append(f"> - …and {len(ungraded) - 8} more")
            out.append("")
        if t.get("evidence"):
            out += ["**What the state assessment rests on:**"] + [f"- {e}" for e in t["evidence"]] + [""]
        parts = [f"{k}: {', '.join(v)}" for k, v in u.items() if v]
        if parts:
            out += ["**Unblocks.** " + " · ".join(parts) + "\n"]
        if c:
            out += ["**Forecast.**\n", "| scenario | band | confidence | rationale |", "|---|---|---|---|"]
            for k in ("conservative", "expected", "optimistic"):
                sc = c["scenarios"][k]
                out.append(f"| {k} | `{sc['date_band']}` | {sc['confidence']} | {esc(sc['rationale'])} |")
            out += ["", f"*Basis:* `{c['basis']}` · *impact here:* `{c['expected_impact']}` · "
                        f"*last reviewed:* {c['last_reviewed']}\n"]
            if c.get("what_would_move_this"):
                out.append(f"**What would move this.** {c['what_would_move_this']}\n")
            if c.get("adoption_note"):
                out.append(f"**⚠ Adoption note.** {c['adoption_note']}\n")
        if t.get("scan_trigger"):
            out.append(f"*Scanned by:* {', '.join('`' + x + '`' for x in t['scan_trigger'])}\n")
        elif t.get("not_scannable_because"):
            out.append(f"*Not scannable — watched another way.* {t['not_scannable_because']}\n")
        else:
            out.append("*Scanned by:* ⚠ **nothing**\n")
    out.append("[← L0](../L0-ecosystem.md)\n")
    return "\n".join(out)


def render_instruments(g):
    out = [fm(id="DOC-VIEW-INSTRUMENTS", title="Instrument register", level="cross-cutting", kind="generated",
              status="generated", generator="systems/systems_check.py",
              purpose="Every method that produces evidence here, and whether it has recovered a known answer.",
              scope="All instruments. An instrument that has not recovered a known answer cannot support a claim.",
              audience=["maintainers", "autonomous research agents", "external reviewers"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Instrument register\n",
           "> **An instrument that has never recovered a known answer cannot support a claim, however good",
           "> its output looks.** An instrument whose control FAILED and one that has NO control are different",
           "> facts — and neither is support.\n",
           "> ⭐ **`verifies` is DERIVED from the requirement register and `allocated_to` from the route",
           "> register.** Neither is written on an instrument. Until 2026-08-05 an instrument asserted its own",
           "> `serves` list as well, and 11 of 30 disagreed with the requirements they claimed — six of them",
           "> holding prose rather than an identifier. One asserted direction, one derived inverse.\n",
           "| id | instrument | known-answer control | state | usable | verifies |",
           "|---|---|---|---|---|---|"]
    for i in g["instruments"]:
        kac = i.get("known_answer_control") or {}
        # ⚠ `usable` is NOT `state == passes`. INS-MONOVALENT-REACH passes and still cannot license a
        # claim, because it inherits V3's and V17's limits — so the column shows the computed answer
        # and names the inheritance, rather than letting a green control speak for a red instrument.
        inh = i.get("inherits_limits_from") or []
        use = "✓" if i.get("usable") else ("⛔ inherits " + ", ".join(f"`{p}`" for p in inh)
                                           if inh and kac.get("state") not in NON_SUPPORTING_CONTROL
                                           else "✕")
        out.append(f"| **{i['id']}** | {esc(i['name'])} | {esc(kac.get('description','—'))} "
                   f"| `{kac.get('state','—')}` | {use} "
                   f"| {', '.join(f'`{r}`' for r in i.get('verifies', [])) or '—'} |")
    out += ["", "## Which routes cite each instrument — the `allocate` relation\n",
            "| id | cited as SUPPORT by | disclosed failing on | characterises |", "|---|---|---|---|"]
    for i in g["instruments"]:
        al = i.get("allocated_to") or {}
        out.append(f"| **{i['id']}** | {', '.join(al.get('support', [])) or '—'} "
                   f"| {', '.join(al.get('disclosed_failing', [])) or '—'} "
                   f"| {', '.join(f'`{o}`' for o in i.get('characterises', [])) or '—'} |")
    scoped = [i for i in g["instruments"] if i.get("scope_note")]
    if scoped:
        out += ["", "## Scope notes\n",
                "> ⚠ **Prose, and explicitly NOT a relation.** These are what survived the 2026-08-05",
                "> reconciliation as genuine scope statements rather than edges — everything else that was",
                "> written as prose turned out to be a paraphrase of an edge the model already carried.\n"]
        out += [f"- **{i['id']}** — {esc(i['scope_note'])}" for i in scoped]
    out.append("\n[← L0](../L0-ecosystem.md)\n")
    return "\n".join(out)


def render_readiness(g):
    ORDER = ["experimental_proposal", "journal_submission", "chemrxiv", "preprint",
             "reproducible_workflow", "internal_note"]
    out = [fm(id="DOC-VIEW-READINESS", title="Readiness — what each route could become today",
              level="cross-cutting", kind="generated", status="generated",
              generator="systems/systems_check.py",
              purpose="For every route: the highest output it could reach now, and what is missing for more.",
              scope="All routes carrying a readiness assessment.",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Readiness\n",
           "The ladder is ordered but is **not** a quality ranking — `experimental_proposal` is not better",
           "than `journal_submission`; they are different outputs and a route can be ready for one and not",
           "the other. Where a route cannot reach an output, the missing items are a work list.\n",
           "| route | family | attainable today | what is missing |", "|---|---|---|---|"]
    rows = [r for r in g["routes"] if r.get("readiness")]
    rows.sort(key=lambda r: (ORDER.index(r["readiness"]["attainable_today"])
                             if r["readiness"]["attainable_today"] in ORDER else 99, r["id"]))
    for r in rows:
        rd = r["readiness"]
        miss = "; ".join(rd.get("missing", [])) or "—"
        out.append(f"| [{r['id']}](L2-{route_slug(r['id'])}.md) | {r['strategy']} "
                   f"| `{rd['attainable_today']}` | {esc(miss[:180])} |")
    out.append("\n[← L0](L0-ecosystem.md)\n")
    return "\n".join(out)


def render_methods_index(g):
    out = [fm(id="DOC-VIEW-METHODS", title="Methods index — instrument to routes served",
              level="cross-cutting", kind="generated", status="generated",
              generator="systems/systems_check.py",
              purpose="The method axis, which is deliberately an index rather than a level of the hierarchy.",
              scope="Every instrument and the routes it serves, plus the technologies that would improve it.",
              audience=["maintainers", "autonomous research agents"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Methods index\n",
           "**Why this is an index and not a level.** A method serves many routes at once — the same pose",
           "instrument is cited by three routes in two different families. If method were a level of the",
           "hierarchy, every shared instrument would be duplicated into each family and its status would",
           "have several homes, which is the one-fact-many-places bug in a new costume. Modality partitions",
           "the routes cleanly; method cuts across them, so it gets this view.\n",
           "| instrument | control state | routes served | technology that would improve it |",
           "|---|---|---|---|"]
    tech_for_inst = defaultdict(list)
    for t in g["technologies"]:
        for v in t.get("unblocks", {}).get("instruments", []):
            tech_for_inst[v].append(t["id"])
    served = defaultdict(set)
    for r in g["routes"]:
        ins = r.get("instruments", {})
        for v in ins.get("support", []) + ins.get("disclosed_failing", []):
            served[v].add(r["id"])
    for i in g["instruments"]:
        kac = (i.get("known_answer_control") or {}).get("state", "—")
        out.append(f"| **{i['id']}** {esc(i['name'][:70])} | `{kac}` "
                   f"| {', '.join(sorted(served.get(i['id'], []))) or '—'} "
                   f"| {', '.join('`'+x+'`' for x in tech_for_inst.get(i['id'], [])) or '—'} |")
    out.append("\n[← L0](L0-ecosystem.md)\n")
    return "\n".join(out)



def render_requirements(g):
    """The requirement register, the R x V coverage matrix, and the dependency graph.

    ⭐ ALL THREE ARE DERIVED FROM ONE SOURCE, which is the point of moving them here. In prose they
    were three separate hand-maintained sections that could disagree with each other, and the coverage
    matrix in particular is a pure function of the register above it.
    """
    inst = by_id(g["instruments"])
    reqs = sorted(g.get("requirements", []), key=lambda r: int(r["id"][1:]))
    out = [fm(id="DOC-VIEW-REQUIREMENTS", title="Requirement register and instrument coverage",
              level="cross-cutting", kind="generated", status="generated",
              generator="systems/systems_check.py",
              purpose="What must be TRUE for the program's claims to stand, which instrument could answer each, and what may be claimed today.",
              scope="All requirements. The narrative that argues each one lives in the roadmap.",
              audience=["maintainers", "autonomous research agents", "external reviewers"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# Requirement register\n",
           "> **The weakest cell sets the ceiling.** A requirement can never be claimed more strongly than",
           "> the instrument underneath it supports — and an instrument whose known-answer control FAILED",
           "> and one that has NO control are different facts, neither of which is support.\n",
           "| id | requirement | work | auth | verified by | usable answer? |",
           "|---|---|---|---|---|---|"]
    for r in reqs:
        vb = r.get("verified_by", [])
        usable = [v for v in vb if inst.get(v, {}).get("usable")]
        if not vb:
            gap = r.get("coverage_gap")
            verdict = (f"⛔ **no instrument** — {COVERAGE_GAPS[gap][1]}" if gap in COVERAGE_GAPS
                       else "⛔ **no instrument at all**")
        elif not usable:
            verdict = "⛔ **none has returned one**"
        else:
            verdict = " · ".join(usable)
        out.append(f"| **{r['id']}** | {esc(r['statement'][:150])} "
                   f"| {GLYPH.get(r['state']['work_state'],'?')} "
                   f"| {'🔒' if r['state']['authorization']=='needs_decision' else '—'} "
                   f"| {' '.join('`'+v+'`' for v in vb) or '—'} | {verdict} |")

    holes = [r for r in reqs if not r.get("verified_by")]
    unusable = [r for r in reqs if r.get("verified_by")
                and not [v for v in r["verified_by"] if inst.get(v, {}).get("usable")]]
    # ⭐ THE HOLES SPLIT AGAIN, AND THE SPLIT IS THE 2026-08-05 CORRECTION. "No instrument exists" was
    # one bucket and it held two entirely different situations: R6 is a computable term nobody has
    # computed, while R4 needs a bench this program does not have and R16 is not this paper's question
    # at all. Reporting them together made two stated scope boundaries look like unfinished work, and
    # a permanent warning for a decision already taken is how a reader learns to skim the list.
    buckets = defaultdict(list)
    for r in holes:
        buckets[r.get("coverage_gap") or ("dead" if r["state"]["work_state"] == "dead" else "?")].append(r)
    out += ["", "## The kinds of gap — which must never be filed together\n",
            "⛔ **Filing these under one word is how the cheap one stays invisible.** A requirement with",
            "nothing built needs something BUILT; one that needs a bench cannot be answered here at all;",
            "one whose instruments have all failed needs a better METHOD. Opposite work items, opposite costs.\n"]
    for key, label in [("buildable", "**Nothing built, and it COULD be built here**"),
                       ("needs_wet_lab", "**No instrument can be built here — CLAUDE.md §5, no wet lab**"),
                       ("out_of_scope", "**Not this paper's question, by its own claim ceiling**"),
                       ("dead", "**Dead — the requirement itself is refuted or retired**")]:
        rows = buckets.get(key, [])
        out.append(f"*{label} ({len(rows)}):* " +
                   (", ".join(f"**{r['id']}** — {esc(r['statement'][:70])}" for r in rows) or "none") + "\n")
    out += [f"**An instrument exists but none has returned a usable answer ({len(unusable)}):** " +
            (", ".join(f"**{r['id']}** ({', '.join(r['verified_by'])})" for r in unusable) or "none") + "\n"]

    # ⚠ EVERY INSTRUMENT THAT VERIFIES SOMETHING, NOT EVERY `V*`. The column set was `id.startswith("V")`,
    # which silently excluded the `INS-` namespace — so an `INS-` instrument could verify a requirement
    # and leave its row looking empty. Two namespaces are real here; a matrix that renders one of them
    # is a coverage view that under-reports coverage.
    vids = sorted({v for r in reqs for v in r.get("verified_by", [])}, key=_req_sort_inst)
    out += ["## Requirement × instrument coverage matrix\n",
            "Read down a column: the weakest cell sets the ceiling. A column with no cell is a hole.\n",
            "| requirement | " + " | ".join(f"`{v}`" for v in vids) + " |",
            "|---|" + "---|" * len(vids)]
    # ⚠ `mixed` is rendered DISTINCTLY rather than collapsed into pass or fail — but as of 2026-08-05 it
    # is NON-SUPPORTING, not citable. It was the one control state no schema ever enumerated, and it
    # silently counted as a pass; "partly" is not an answer a claim can rest on.
    CELL = {"passes": "✓", "fails": "✕", "inconclusive": "⚠", "none": "○", "mixed": "◐"}
    for r in reqs:
        row = []
        for v in vids:
            if v in r.get("verified_by", []):
                i = inst.get(v, {})
                st = (i.get("known_answer_control") or {}).get("state", "none")
                # A passing control that cannot license anything gets its own glyph, or the matrix
                # would show a ✓ for the instrument whose own note says it cannot support a claim.
                row.append("⊘" if st == "passes" and not i.get("usable") else CELL.get(st, "·"))
            else:
                row.append("")
        out.append(f"| **{r['id']}** | " + " | ".join(row) + " |")
    out += ["", "*Legend: ✓ recovered a known answer · ⊘ its own control passes but it INHERITS limits it "
            "cannot clear · ◐ mixed — its controls do not all support it · ⚠ inconclusive · ✕ its control "
            "failed · ○ no control exists. An empty cell means the instrument does not verify that "
            "requirement.*\n"]

    out += ["## The dependency graph\n",
            "Read upward: a box can only be claimed once everything feeding it holds. Node state is the",
            "requirement's work state, so the graph reads the same without colour.\n",
            "```mermaid", "graph BT"]
    node_of = {r["graph_node"]: r for r in reqs if r.get("graph_node")}
    for n, r in node_of.items():
        label = esc(r["statement"][:60]).replace('"', "'")
        out.append(f'  {n}["{GLYPH.get(r["state"]["work_state"],"?")} {r["id"]} · {label}"]')
    EDGES = [("PO","L"),("L","PS"),("PS","B"),("DGO","B"),("PS","LK"),("LK","T"),
             ("ARCH","T"),("T","TS"),("T","UB"),("UB","P"),("B","P"),("TS","P")]
    out.append('  P["○ PAPER — a defensible NR4A-paralogue-selective degrader candidate"]')
    for a, b in EDGES:
        if a in node_of or a == "P":
            if b in node_of or b == "P":
                out.append(f"  {a} --> {b}")
    if "TG" in node_of:
        out.append("  TG -.delegated.-> P")
    out += ["```", "",
            "⚠ **Not every requirement is drawable here, and that is a property of the graph rather than of",
            "them.** A requirement that BOUNDS every node — a scope or submission condition — cannot be shown",
            "as an ordinary box without implying it can be discharged in sequence, which it cannot. Those",
            "appear in the register above and nowhere in this diagram.\n",
            "## Detail\n"]
    for r in reqs:
        out += [f"### {r['id']} — {esc(r['statement'][:120])}\n",
                f"- **work state:** {GLYPH.get(r['state']['work_state'],'?')} {esc(r['work_state_note'])}",
                f"- **authorization:** {esc(r['authorization_note']) or '—'}",
                f"- **verified by:** {' '.join('`'+v+'`' for v in r.get('verified_by', [])) or '⛔ nothing'}"
                + (f" — {esc(_clip(r['verified_by_note'], 300))}" if r.get("verified_by_note") else ""),
                *([f"- **why there is no instrument:** `{r['coverage_gap']}` — "
                   f"{esc(r.get('coverage_gap_why',''))}"] if r.get("coverage_gap") else []),
                f"- **⛔ claim ceiling today:** {esc(r['claim_ceiling'][:600])}", ""]
    out.append("[← L0](../L0-ecosystem.md) · [instrument register](instruments.md)\n")
    return "\n".join(out)



HORIZONS = ["2026H2", "2027", "2028", "2029", "2030+", "standing"]
MS_KIND = {"scientific": "science", "technology": "technology", "ai_capability": "AI capability",
           "lab_capability": "lab capability", "data": "data", "decision": "decision",
           "process": "process", "capability": "capability"}


def render_roadmap(g):
    """The multi-year roadmap — a PROJECTION of the technology register, not an independent plan.

    ⭐ That is the design decision that matters here. A hand-maintained multi-year roadmap describes the
    year it was written; this one changes when the register changes, so a landed capability re-orders the
    portfolio without anyone remembering to.
    """
    ms = g.get("roadmap", [])
    tk, fc = by_id(g["technologies"]), by_id(g["forecasts"])
    out = [fm(id="DOC-VIEW-ROADMAP", title="The multi-year roadmap", level="cross-cutting",
              kind="generated", status="generated", generator="systems/systems_check.py",
              purpose="Scientific, technology, AI-capability and lab-capability milestones over roughly five years, and when blocked work becomes revisitable.",
              scope="Horizon milestones only. The near-term spend-gated plan is the roadmap document's ordered plan.",
              audience=["maintainers", "autonomous research agents", "external reviewers"],
              date="2026-08-05", last_verified="2026-08-05"),
           BANNER, "# The multi-year roadmap\n",
           "> **This is a projection of the technology register, not an independent plan.** It changes when",
           "> the register changes, which is what stops it describing the year it was written. Every arrival",
           "> band comes from a forecast that declares its `basis` — `evidence_based`, `extrapolated` or",
           "> `speculative` — because an unlabelled forecast is indistinguishable from a measurement.\n",
           "> ⚠ **A coming capability justifies waiting and re-running. It never licences claiming a result",
           "> before the method can support it.**\n"]

    for h in HORIZONS:
        rows = [m for m in ms if m.get("horizon") == h]
        if not rows:
            continue
        label = "Standing" if h == "standing" else h
        out += [f"## {label}\n"]
        for m in rows:
            out += [f"### {m['id']} — {esc(m['title'])}\n",
                    f"*{MS_KIND.get(m.get('kind'), m.get('kind'))} · confidence {m.get('confidence','unknown')}*\n",
                    m["note"], ""]
            if m.get("depends_on"):
                out.append("**Depends on:** " + ", ".join(m["depends_on"]) + "\n")
            if m.get("unblocks"):
                out.append("**Unblocks:** " + ", ".join(f"`{x}`" for x in m["unblocks"]) + "\n")

    out += ["## Every technology dependency, by expected arrival\n",
            "Derived from the forecast register. The conservative and optimistic bands, the rationale for",
            "each, and what would move them are in [registers/technologies.md](registers/technologies.md).\n",
            "| expected | fan-out | technology | impact here | basis | state |",
            "|---|---:|---|---|---|---|"]
    ordered = sorted(g["technologies"],
                     key=lambda t: (fc.get(t.get("forecast"), {}).get("scenarios", {})
                                    .get("expected", {}).get("date_band", "9999"), -t["fan_out"]))
    for t in ordered:
        c = fc.get(t.get("forecast"), {})
        exp = c.get("scenarios", {}).get("expected", {}).get("date_band", "—")
        out.append(f"| **{exp}** | {t['fan_out']} | {t['id']} | `{c.get('expected_impact','—')}` "
                   f"| `{c.get('basis','—')}` | `{t['current_state']}` |")

    stale = [c["id"] for c in g["forecasts"] if c.get("last_reviewed", "") < "2026-02-05"]
    out += ["", "## Forecast freshness\n"]
    if stale:
        out.append(f"⚠ **{len(stale)} forecast(s) older than two quarters and due a re-grade:** "
                   + ", ".join(f"`{x}`" for x in stale) + "\n")
    else:
        out.append("Every forecast has been reviewed within the last two quarters.\n")
    out.append("[← L0](L0-ecosystem.md)\n")
    return "\n".join(out)



def render_plan_body(plan):
    """Reconstruct the plan text from the graph. Inverse of systems/extract_plan.py.

    ⚠ EVERY CHARACTER OUTSIDE A MARKER IS VERBATIM. Only `marker` is a field, because it is the one
    thing that must be machine-settable: once this view is generated, ticking an item happens in
    systems/graph/plan.json and a hand-edit here fails the build.
    """
    out = []
    for b in plan.get("blocks", []):
        if b["kind"] == "raw":
            out.append(b["text"])
        elif b["kind"] == "item":
            out.append(f"{b['indent']}- **`[{b['marker']}]`{b['text']}")
    # ⛔ VERBATIM, DELIBERATELY. This function IS the round-trip proof's subject: extract_plan.py
    # refuses to write unless its render matches the source byte for byte. Anchor re-homing happens in
    # render_plan below, on the way into the VIEW — doing it here would silently make the losslessness
    # proof prove something weaker while still passing, which is the shape of every defect in this file.
    return "".join(out)


#: A bare `](#section)` link — a same-DOCUMENT reference.
#: ⚠ A LEADING HYPHEN IS LEGAL AND COMMON HERE. A heading opening with a glyph — `## ⭐ WHAT THE
#: LANDED RESULTS CHANGE…` — slugifies to `-what-the-landed-…`, so a pattern anchored on
#: `[a-z0-9]` misses exactly the headings this repository writes most.
_SAME_DOC_ANCHOR = re.compile(r"\]\(#(-?[a-z0-9][a-z0-9-]*)\)")


def _rehome_same_doc_anchors(body):
    """`](#x)` inside the plan means a ROADMAP heading, not a heading of this generated view.

    ⛔ THE EXTRACTION MOVED THE TEXT AND SILENTLY BROKE ITS LINKS. THE ORDERED PLAN was lifted out of
    `nr4a3-program-map.md` verbatim -- which is the point, the move is provably lossless character for
    character -- but a link that read `](#101--open-rows-...)` meant *this document, further down*, and
    "this document" changed. 26 links in the generated view pointed at headings it does not have, and
    every one of them passed the link checker because that checker stripped the fragment before
    testing. Two blind spots that only fail when combined, which is why neither was noticed.

    ⚠ REWRITTEN AT RENDER TIME, NOT IN THE SOURCE. plan.json holds the roadmap's text VERBATIM and
    `extract_plan.py` proves the round trip byte for byte; editing the anchors there would break that
    proof and make the migration lossy in the one way MIGRATION.md §2.1 says never to make it.
    """
    return _SAME_DOC_ANCHOR.sub(r"](../../research/manuscripts/nr4a3-program-map.md#\1)", body)


def render_plan(g):
    plan = g.get("plan") or {}
    body = _rehome_same_doc_anchors(render_plan_body(plan))
    items = [b for b in plan.get("blocks", []) if b["kind"] == "item"]
    open_n = sum(1 for b in items if b["marker"] in " ~!")
    head = [fm(id="DOC-VIEW-PLAN", title="THE ORDERED PLAN, the spend ladder and the dependency spine",
               level="cross-cutting", kind="generated", status="generated",
               generator="systems/systems_check.py",
               purpose="What to do next, in order, with each step's gate and cost — and the money rules and cumulative chain the order depends on.",
               scope="The near-term spend-gated plan. The multi-year horizon is views/roadmap-5yr.md.",
               audience=["maintainers", "autonomous research agents"],
               date="2026-08-05", last_verified="2026-08-05"),
            BANNER,
            "<!-- ⛔ TICKING AN ITEM HAPPENS IN systems/graph/plan.json, NOT HERE.",
            "     A hand-edit to this file fails the build. That is the cost of one-fact-one-home,",
            "     and it is deliberate: `marker` is a field precisely so it can be set by machine.",
            "",
            f"     {len(items)} items · {open_n} still open.",
            "",
            "     ⚠ THE SKIPPED MARKER IS AN EN DASH (U+2013), NOT AN ASCII HYPHEN.",
            "     ⚠ `Cum. ~$N` (the plan) and `Cum ~$N` (the spine) are DELIBERATELY different and must",
            "        both stay in THIS file — pinned-figures.json subset_checks/strategy_spine_cum",
            "        asserts one is a subset of the other WITHIN A SINGLE FILE. -->",
            ""]
    return "\n".join(head) + "\n" + body


def all_views(g):
    v = {"L0-ecosystem.md": render_l0(g),
         "registers/lanes.md": render_lanes(g),
         "registers/blockers.md": render_blockers(g),
         "registers/technologies.md": render_technologies(g),
         "registers/instruments.md": render_instruments(g),
         "registers/requirements.md": render_requirements(g),
         "methods-index.md": render_methods_index(g),
         "readiness.md": render_readiness(g),
         "roadmap-5yr.md": render_roadmap(g),
         "plan.md": render_plan(g)}
    for s in g["strategies"]:
        v[f"L1-{s['id'].lower()}.md"] = render_l1(s, g)
    for r in g["routes"]:
        v[f"L2-{route_slug(r['id'])}.md"] = render_l2(r, g)
    return v


def write_views(g):
    n = 0
    for rel, body in all_views(g).items():
        path = os.path.join(VIEWS, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        n += 1
    return n


def check_views(g, f):
    """A generated view that has been hand-edited, or has drifted from the graph, is a defect."""
    for rel, body in all_views(g).items():
        path = os.path.join(VIEWS, rel)
        if not os.path.exists(path):
            f.err("[G1]", f"generated view missing: systems/views/{rel} — run --write-views")
            continue
        with open(path, encoding="utf-8") as fh:
            if fh.read() != body:
                f.err("[G2]", f"systems/views/{rel} differs from what the graph renders — it was "
                              f"hand-edited or the graph moved. Run --write-views.")


# ───────────────────────────── cli ─────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="run the invariants (default)")
    ap.add_argument("--write-views", action="store_true", help="regenerate systems/views/**")
    ap.add_argument("--no-view-check", action="store_true", help="skip the view-drift comparison")
    ap.add_argument("--json", action="store_true", help="machine-readable findings")
    a = ap.parse_args(argv)

    g = derive(load_graph())

    if a.write_views:
        n = write_views(g)
        print(f"systems_check: wrote {n} view(s) to systems/views/")
        if not a.check:
            return 0

    f = Findings()
    run_checks(g, f)
    if not a.no_view_check and not a.write_views:
        check_views(g, f)

    if a.json:
        print(json.dumps({"errors": f.errors, "warns": f.warns, "infos": f.infos},
                         indent=2, ensure_ascii=False))
    else:
        # ⚠ INFOS PRINT FIRST AND ARE NOT HIDDEN BEHIND A FLAG. They are findings the model is
        # deliberately reporting as closed -- a scope boundary, a link baseline at zero -- and burying
        # them would turn "we decided this" into "nobody checked".
        for i in f.infos:
            print("INFO ", i)
        for w in f.warns:
            print("WARN ", w)
        for e in f.errors:
            print("ERROR", e)
        total = sum(len(g[c]) for c in COLLECTIONS)
        print(f"\nsystems_check: {total} objects across {len(COLLECTIONS)} collections · "
              f"{len(f.errors)} ERROR · {len(f.warns)} WARN · {len(f.infos)} INFO")
    return 0 if f.ok else 1


if __name__ == "__main__":
    sys.exit(main())
