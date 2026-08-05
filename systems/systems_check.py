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
]

# A blocker of this kind is a fact about what the objects ARE. It is not waiting on anything,
# so it may carry no technology dependency and must appear on no watch list.
PERMANENT_KINDS = {"fundamental_biological_limit"}

# An instrument in any of these control states may never be listed as SUPPORT. `none` is included
# deliberately: "no control exists" and "the control failed" are different facts, and neither is support.
NON_SUPPORTING_CONTROL = {"fails", "none", "inconclusive"}


# ───────────────────────────── findings ─────────────────────────────

class Findings:
    def __init__(self):
        self.errors: list[str] = []
        self.warns: list[str] = []

    def err(self, code, msg):
        self.errors.append(f"{code}  {msg}")

    def warn(self, code, msg):
        self.warns.append(f"{code}  {msg}")

    @property
    def ok(self):
        return not self.errors


# ──────────────────── a stdlib subset of JSON Schema ────────────────────
# Enough of draft 2020-12 to make the schemas in systems/schema/ ENFORCED rather than decorative:
# type · required · properties · additionalProperties:false · enum · const · pattern · minLength ·
# minItems · items · allOf · if/then · not · $ref (local $defs and cross-file).

_TYPES = {
    "object": dict, "array": list, "string": str, "integer": int,
    "number": (int, float), "boolean": bool, "null": type(None),
}


class MiniValidator:
    def __init__(self, schema_dir):
        self.docs = {}
        for fn in sorted(os.listdir(schema_dir)):
            if fn.endswith(".json"):
                with open(os.path.join(schema_dir, fn), encoding="utf-8") as fh:
                    self.docs[fn] = json.load(fh)

    def _resolve(self, ref, cur):
        if ref.startswith("#/"):
            node = cur
            for part in ref[2:].split("/"):
                node = node[part]
            return node, cur
        file_part, _, frag = ref.partition("#")
        doc = self.docs[os.path.basename(file_part)]
        node = doc
        if frag:
            for part in frag.strip("/").split("/"):
                node = node[part]
        return node, doc

    def validate(self, inst, schema, cur=None, path="$", out=None, _top=True):
        # A schema that both declares `required` and $refs a base declaring the same field reports it
        # twice. Dedupe at the top call rather than teaching every branch about it.
        if _top:
            inner: list[str] = []
            self.validate(inst, schema, cur, path, inner, _top=False)
            seen, uniq = set(), []
            for m in inner:
                if m not in seen:
                    seen.add(m)
                    uniq.append(m)
            if out is None:
                return uniq
            out.extend(uniq)
            return out
        out = [] if out is None else out
        cur = schema if cur is None else cur

        if "$ref" in schema:
            sub, subcur = self._resolve(schema["$ref"], cur)
            self.validate(inst, sub, subcur, path, out, _top=False)
            return out

        t = schema.get("type")
        if t:
            want = _TYPES[t] if isinstance(t, str) else tuple(_TYPES[x] for x in t)
            # bool is a subclass of int in Python; JSON Schema does not agree
            if t in ("integer", "number") and isinstance(inst, bool):
                out.append(f"{path}: expected {t}, got boolean")
                return out
            if not isinstance(inst, want):
                out.append(f"{path}: expected {t}, got {type(inst).__name__}")
                return out

        if "const" in schema and inst != schema["const"]:
            out.append(f"{path}: must be {schema['const']!r}, got {inst!r}")
        if "enum" in schema and inst not in schema["enum"]:
            out.append(f"{path}: {inst!r} not in enum {schema['enum']}")

        if isinstance(inst, str):
            if "pattern" in schema and not re.search(schema["pattern"], inst):
                out.append(f"{path}: {inst!r} does not match {schema['pattern']}")
            if "minLength" in schema and len(inst) < schema["minLength"]:
                out.append(f"{path}: shorter than minLength {schema['minLength']}")

        if isinstance(inst, list):
            if "minItems" in schema and len(inst) < schema["minItems"]:
                out.append(f"{path}: fewer than minItems {schema['minItems']}")
            if "items" in schema:
                for i, v in enumerate(inst):
                    self.validate(v, schema["items"], cur, f"{path}[{i}]", out, _top=False)

        if isinstance(inst, dict):
            for k in schema.get("required", []):
                if k not in inst:
                    out.append(f"{path}: missing required field {k!r}")
            props = schema.get("properties", {})
            for k, v in inst.items():
                if k in props:
                    self.validate(v, props[k], cur, f"{path}.{k}", out, _top=False)
                elif schema.get("additionalProperties") is False and not k.startswith("_"):
                    out.append(f"{path}: unexpected field {k!r}")

        for sub in schema.get("allOf", []):
            self.validate(inst, sub, cur, path, out, _top=False)
        if "if" in schema:
            probe = []
            self.validate(inst, schema["if"], cur, path, probe, _top=False)
            branch = "then" if not probe else "else"
            if branch in schema:
                self.validate(inst, schema[branch], cur, path, out, _top=False)
        if "not" in schema:
            probe = []
            self.validate(inst, schema["not"], cur, path, probe, _top=False)
            if not probe:
                out.append(f"{path}: must NOT match the `not` subschema")
        return out


# ───────────────────────────── loading ─────────────────────────────

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

    # requirement <-> instrument coverage, both directions, derived from the requirement register only
    inst_serves = defaultdict(list)
    for r in g.get("requirements", []):
        for v in r.get("served_by", []):
            inst_serves[v].append(r["id"])
    for i in g["instruments"]:
        i["serves_derived"] = sorted(inst_serves.get(i["id"], []), key=lambda x: int(x[1:]))

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
    mv = MiniValidator(SCHEMA)
    pairs = [("strategies", "strategy.schema.json"),
             ("routes", "route.schema.json"),
             ("blockers", "blocker.schema.json")]
    for coll, sch in pairs:
        schema = mv.docs[sch]
        for row in g[coll]:
            for msg in mv.validate(row, schema, schema):
                f.err("[S1]", f"{coll}/{row.get('id','?')} {msg}")

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


def check_pointers(g, f):
    """Every owner{file} exists on disk, and every anchor is a plausible slug in it."""
    for coll in COLLECTIONS:
        for row in g[coll]:
            owner = (row.get("owner") or row.get("provenance", {}).get("owner") or {})
            path = owner.get("file")
            if not path:
                continue
            full = os.path.join(REPO, path)
            if not os.path.exists(full):
                f.err("[P1]", f"{row['id']} owner file does not exist: {path}")
                continue
            anchor = owner.get("anchor")
            if anchor and path.endswith(".md"):
                if not anchor_resolves(full, anchor):
                    f.err("[P2]", f"{row['id']} owner anchor does not resolve: {path}{anchor}")


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
    s = re.sub(r"`|\*|_|\[|\]|\(|\)", "", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = s.replace(" ", "-")
    return s


def anchor_resolves(path: str, anchor: str) -> bool:
    want = anchor.lstrip("#")
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


NON_SUPPORTING_LABEL = {"fails": "its control FAILED", "none": "it has NO control",
                        "inconclusive": "its control was INCONCLUSIVE"}


def check_requirements(g, f):
    """The requirement register, and the coverage question it exists to answer.

    Invariant 2 lives here: read down a requirement's column and THE WEAKEST CELL SETS ITS CEILING.
    A requirement served only by instruments that have not recovered a known answer has no usable
    answer available -- which is a different and more actionable statement than "not done yet".
    """
    inst = by_id(g["instruments"])
    for r in g.get("requirements", []):
        for v in r.get("served_by", []):
            if v not in inst:
                f.err("[Q1]", f"{r['id']} is served by unknown instrument {v}")
        if not r.get("claim_ceiling"):
            f.err("[Q2]", f"{r['id']} states no claim ceiling -- a requirement with no stated ceiling "
                          f"cannot bound what may be claimed from it, which is the register's whole job")
        if not r.get("served_by") and r["state"]["work_state"] not in ("dead",):
            f.warn("[Q3]", f"{r['id']} has NO instrument at all -- it is not 'not done yet', there is "
                           f"nothing built that could answer it")
        usable = [v for v in r.get("served_by", [])
                  if (inst.get(v, {}).get("known_answer_control") or {}).get("state")
                  not in NON_SUPPORTING_CONTROL]
        if r.get("served_by") and not usable:
            f.warn("[Q4]", f"{r['id']} has instruments but NONE has returned a usable answer "
                           f"({', '.join(r['served_by'])}) -- a different failure from having none")


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

    for coll, fields in [("routes", SHARED_ROUTE_FIELDS),
                         ("blockers", ["name", "statement_about", "owner"]),
                         ("instruments", ["name", "known_answer_control", "serves"])]:
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
        served = sorted(set(re.findall(r"`(V\d+)`", cells[4])), key=lambda x: int(x[1:]))
        if served != gr[rid].get("served_by"):
            f.err("[M5]", f"{rid} served-by disagrees: roadmap {served} vs graph {gr[rid].get('served_by')}")



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
    missing, unverified, bad = [], 0, 0
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if rel_root.startswith((".git", "node_modules", ".pytest_cache")) or "__pycache__" in rel_root:
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
                unverified += 1
    for rel in missing:
        f.err("[D4]", f"{rel} has no frontmatter — purpose, scope, audience and freshness are undeclared")
    if unverified:
        f.warn("[D5]", f"{unverified} document(s) carry `last_verified: unverified` — nobody has "
                       f"confirmed their content is still true. This is honest, not a defect; the "
                       f"count is meant to fall.")



#: A bare artifact citation: a backticked `something-like-this.json` / `.png` / `.csv`, which is how
#: this repository actually cites results in prose. Deliberately NOT a Markdown link — see check_artifacts.
ARTIFACT_CITE = re.compile(r"`([a-z0-9][a-z0-9._-]*\.(?:json|jsonl|png|csv))`", re.I)
ARTIFACT_DIRS = ("research/modalities", "research/manuscripts", "research/data", "research/compute",
                 "research/hypotheses", "research/meta", "systems/graph", "results")


def _artifacts_elsewhere(f):
    """Artifacts that deliberately live on another ref — a CHECKED claim, not a silencer.

    ⛔ EVERY FIELD IS REQUIRED, AND THAT IS THE WHOLE DESIGN. An entry with no `ref`, no `written_by`
    or no `why_not_ported` is indistinguishable from "we did not get round to porting it" — which is
    drift, and drift belongs in the port. Refusing the incomplete entry is what stops this register
    becoming the place warnings go to die.
    """
    path = os.path.join(GRAPH, "artifact-refs.json")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh).get("elsewhere", [])
    out = set()
    for r in rows:
        missing_fields = [k for k in ("artifact", "ref", "written_by", "why_not_ported", "checked_on")
                          if not r.get(k)]
        if missing_fields:
            f.err("[K2]", f"artifact-refs entry {r.get('artifact', '?')} is missing "
                          f"{missing_fields} — an off-branch home is a checked claim, and an entry "
                          f"that does not name the ref and why a copy would be WRONG is a silencer")
            continue
        if len(r["why_not_ported"]) < 60:
            f.err("[K2]", f"artifact-refs entry {r['artifact']} gives a one-line reason — the default "
                          f"is to PORT, so an exemption has to argue that a second copy would be "
                          f"actively harmful, not merely unnecessary")
            continue
        out.add(r["artifact"])
    return out


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
    baseline = {row["to"].rsplit("/", 1)[-1] for row in _link_baseline_rows()}
    baseline |= _artifacts_elsewhere(f)

    missing = defaultdict(set)
    for rel, text in _walk_md(DOC_SKIP):
        for m in ARTIFACT_CITE.finditer(text):
            name = m.group(1)
            if name in known or name in baseline:
                continue
            # A name nothing anywhere produces is a typo or a plan, not drift. Only flag a citation
            # whose producer exists here — that is what says "this was meant to have been generated".
            stem = os.path.splitext(name)[0].replace("-", "_")
            if f"{stem}.py" in known or f"{stem}.mjs" in known:
                missing[name].add(rel)
    for name in sorted(missing):
        cites = sorted(missing[name])
        f.warn("[K1]", f"`{name}` is cited by {len(cites)} document(s) ({', '.join(cites[:3])}"
                       f"{', …' if len(cites) > 3 else ''}) and its producer is in this repo, but the "
                       f"artifact is NOT on this branch — check whether the lane that makes it writes "
                       f"to a different ref before concluding it was never run")


MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)\s]*)?\)")
LINK_SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "data:")

#: ⚠ A LINK TARGET MUST LOOK LIKE A PATH. Without this, SMILES strings are read as Markdown links —
#: `[nH]` followed by `(C(=O)...` is syntactically a link — and the first run reported 184 "broken
#: links", of which the overwhelming majority were chemistry. A checker that cries wolf gets switched
#: off, so it recognises a path: a slash, or a real file extension.
LOOKS_LIKE_PATH = re.compile(r"/|\.(md|json|py|yml|yaml|mjs|sh|txt|csv|png|svg|pdf|cff|html)$", re.I)


def _link_baseline_rows():
    path = os.path.join(GRAPH, "link-baseline.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("known_broken", [])


def _link_baseline():
    """Known-broken links that predate this check. Anything NOT here is an error."""
    return {(r["from"], r["to"]) for r in _link_baseline_rows()}


def check_links(g, f):
    """Every relative Markdown link resolves to a file that exists.

    ⭐ WHY THIS EXISTS. The repository had NO repo-wide link checker — `verify-refs.yml` validates
    external DOIs, and the only path check in CI inspected `provenance.owner.file`, which for every
    graph row points at one document. So a document could be moved and every link to it would rot in
    silence until someone clicked one.

    That is not hypothetical: this class of breakage is precisely what stopped the archive sweep the
    first time it was attempted, and three of the hazards found then were not links at all but
    runtime reads — which this check deliberately does NOT cover, and cannot. It catches the easy
    class so that attention is free for the hard one.
    """
    baseline = _link_baseline()
    checked = broken = grandfathered = 0
    for root, dirs, files in os.walk(REPO):
        rel_root = os.path.relpath(root, REPO).replace(os.sep, "/")
        if rel_root.startswith((".git", "node_modules", ".pytest_cache")) or "__pycache__" in rel_root:
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
                target = m.group(1).strip()
                if not target or target.startswith(LINK_SKIP_PREFIX):
                    continue
                if not LOOKS_LIKE_PATH.search(target):
                    continue
                checked += 1
                dest = os.path.normpath(os.path.join(os.path.dirname(os.path.join(REPO, src)), target))
                if not os.path.exists(dest):
                    if (src, target) in baseline:
                        grandfathered += 1
                        continue
                    broken += 1
                    f.err("[K1]", f"{src} links to {target!r}, which does not exist")
    f.warn("[K0]", f"relative links checked: {checked}, new breakage: {broken}, "
                   f"grandfathered: {grandfathered} (systems/graph/link-baseline.json — that list is "
                   f"meant to reach zero and must never grow)")


def run_checks(g, f):
    check_schemas(g, f)
    check_legacy_agreement(g, f)
    check_ids_unique(g, f)
    check_hierarchy(g, f)
    check_blockers(g, f)
    check_requirements(g, f)
    check_requirement_source_agreement(g, f)
    check_technologies(g, f)
    check_scan_interop(g, f)
    check_doc_ids(g, f)
    check_documents(g, f)
    check_links(g, f)
    check_artifacts(g, f)
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
        n = len(fams[b])
        lab = mermaid_label(f"{b} — {n} families", 52)
        out.append(f'  {mm_id(b)}[["{lab}"]]:::perm' if blk[b]["permanent"]
                   else f'  {mm_id(b)}{{{{"{lab}"}}}}:::blk')
    out.append("")
    for s in sorted(g["strategies"], key=lambda x: (-len(x["routes"]), x["id"])):
        ss = s["summary_state"]
        lab = mermaid_label(f"{s['id']} {GLYPH.get(s['state']['work_state'], '?')} · "
                            f"{ss['n_routes']} routes", 40)
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
           "What one screen has to carry is not the list — it is the **convergence**. The table below states"
           " each family correctly; only this shows that two blockers hold down two-thirds of them.\n"]
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
            "| blocker | kind | routes held | retired by |", "|---|---|---:|---|"]
    for b in sorted(g["blockers"], key=lambda x: -len(x["inherited_by"])):
        if not b["inherited_by"]:
            continue
        out_by = ", ".join(f"`{t}`" for t in b["retired_by_technology"]) or \
            ("*permanent — nothing*" if b["permanent"] else "*an action we can take*")
        out.append(f"| **{b['id']}** | `{b['kind']}` | {len(b['inherited_by'])} | {out_by} |")

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
            "- **Registers** — [blockers](registers/blockers.md) · [technologies](registers/technologies.md) · "
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
           "| id | instrument | known-answer control | state | serves |", "|---|---|---|---|---|"]
    for i in g["instruments"]:
        kac = i.get("known_answer_control") or {}
        out.append(f"| **{i['id']}** | {esc(i['name'])} | {esc(kac.get('description','—'))} "
                   f"| `{kac.get('state','—')}` | {', '.join(i.get('serves', [])) or '—'} |")
    out += ["", "## Which routes cite each instrument\n",
            "| id | cited as SUPPORT by | disclosed failing on |", "|---|---|---|"]
    sup, dis = defaultdict(list), defaultdict(list)
    for r in g["routes"]:
        ins = r.get("instruments", {})
        for v in ins.get("support", []):
            sup[v].append(r["id"])
        for v in ins.get("disclosed_failing", []):
            dis[v].append(r["id"])
    for i in g["instruments"]:
        out.append(f"| **{i['id']}** | {', '.join(sup.get(i['id'], [])) or '—'} "
                   f"| {', '.join(dis.get(i['id'], [])) or '—'} |")
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
           "| id | requirement | work | auth | served by | usable answer? |",
           "|---|---|---|---|---|---|"]
    for r in reqs:
        served = r.get("served_by", [])
        usable = [v for v in served
                  if (inst.get(v, {}).get("known_answer_control") or {}).get("state")
                  not in NON_SUPPORTING_CONTROL]
        if not served:
            verdict = "⛔ **no instrument at all**"
        elif not usable:
            verdict = "⛔ **none has returned one**"
        else:
            verdict = " · ".join(usable)
        out.append(f"| **{r['id']}** | {esc(r['statement'][:150])} "
                   f"| {GLYPH.get(r['state']['work_state'],'?')} "
                   f"| {'🔒' if r['state']['authorization']=='needs_decision' else '—'} "
                   f"| {' '.join('`'+v+'`' for v in served) or '—'} | {verdict} |")

    holes = [r for r in reqs if not r.get("served_by")]
    unusable = [r for r in reqs if r.get("served_by") and not
                [v for v in r["served_by"]
                 if (inst.get(v, {}).get("known_answer_control") or {}).get("state")
                 not in NON_SUPPORTING_CONTROL]]
    out += ["", "## The two kinds of gap — which must never be filed together\n",
            "⛔ **Filing these under one word is how the cheap one stays invisible.** A requirement with no",
            "instrument needs something BUILT or a bench; one whose instruments have all failed needs a",
            "better METHOD. Opposite work items, opposite costs.\n",
            f"**No instrument exists at all ({len(holes)}):** " +
            (", ".join(f"**{r['id']}** — {esc(r['statement'][:70])}" for r in holes) or "none") + "\n",
            f"**An instrument exists but none has returned a usable answer ({len(unusable)}):** " +
            (", ".join(f"**{r['id']}** ({', '.join(r['served_by'])})" for r in unusable) or "none") + "\n"]

    out += ["## R x V coverage matrix\n",
            "Read down a column: the weakest cell sets the ceiling. A column with no cell is a hole.\n",
            "| requirement | " + " | ".join(f"`{i['id']}`" for i in g["instruments"]
                                            if i["id"].startswith("V")) + " |",
            "|---|" + "---|" * sum(1 for i in g["instruments"] if i["id"].startswith("V"))]
    vids = [i["id"] for i in g["instruments"] if i["id"].startswith("V")]
    # ⚠ `mixed` is a real fifth state (an instrument whose nulls do not all support it) and it is
    # rendered DISTINCTLY rather than collapsed into pass or fail. The repository's existing
    # convention treats it as citable, so this view does not overrule that -- it makes it visible.
    CELL = {"passes": "✓", "fails": "✕", "inconclusive": "⚠", "none": "○", "mixed": "◐"}
    for r in reqs:
        row = []
        for v in vids:
            if v in r.get("served_by", []):
                st = (inst.get(v, {}).get("known_answer_control") or {}).get("state", "none")
                row.append(CELL.get(st, "·"))
            else:
                row.append("")
        out.append(f"| **{r['id']}** | " + " | ".join(row) + " |")
    out += ["", "*Legend: ✓ recovered a known answer · ◐ mixed — its controls do not all support it · "
            "⚠ inconclusive · ✕ its control failed · ○ no control exists. An empty cell means the "
            "instrument does not serve that requirement.*\n"]

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
                f"- **served by:** {' '.join('`'+v+'`' for v in r.get('served_by', [])) or '⛔ nothing'}",
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
    return "".join(out)


def render_plan(g):
    plan = g.get("plan") or {}
    body = render_plan_body(plan)
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
        print(json.dumps({"errors": f.errors, "warns": f.warns}, indent=2, ensure_ascii=False))
    else:
        for w in f.warns:
            print("WARN ", w)
        for e in f.errors:
            print("ERROR", e)
        total = sum(len(g[c]) for c in COLLECTIONS)
        print(f"\nsystems_check: {total} objects across {len(COLLECTIONS)} collections · "
              f"{len(f.errors)} ERROR · {len(f.warns)} WARN")
    return 0 if f.ok else 1


if __name__ == "__main__":
    sys.exit(main())
