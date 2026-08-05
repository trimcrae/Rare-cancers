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
    "strategies", "routes", "blockers", "technologies", "forecasts",
    "instruments", "objects", "evidence", "artifacts", "claims",
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
        if not t.get("scan_trigger"):
            f.warn("[T3]", f"{t['id']} has no scan trigger -- nothing is searching for it, so it could "
                           f"land without anyone noticing")
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


def run_checks(g, f):
    check_schemas(g, f)
    check_legacy_agreement(g, f)
    check_ids_unique(g, f)
    check_hierarchy(g, f)
    check_blockers(g, f)
    check_technologies(g, f)
    check_pointers(g, f)
    check_instrument_support(g, f)
    check_compute_case(g, f)
    return f


# ───────────────────────────── rendering ─────────────────────────────

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
           "## The landscape\n",
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
            "- **Cross-cutting** — [methods index](methods-index.md) · [readiness](readiness.md)",
            "- **Architecture** — [../ARCHITECTURE.md](../ARCHITECTURE.md) · [../CONVENTIONS.md](../CONVENTIONS.md)",
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
        out.append(f"**Grade** (owned by [`{own.get('file','?')}`]({os.path.relpath(os.path.join(REPO, own.get('file','.')), VIEWS)}{own.get('anchor','')})): {esc(gv.get('value',''))}\n")
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
           "Typed with [`taxonomy/blockers.md`](../taxonomy/blockers.md). The kinds are **never conflated**:",
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
    out.append("[← L0](../views/L0-ecosystem.md)\n")
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
                   f"| {'yes' if t.get('scan_trigger') else '⚠ **no**'} |")
    unscanned = [t["id"] for t in g["technologies"] if not t.get("scan_trigger")]
    if unscanned:
        out += ["", f"⚠ **{len(unscanned)} dependencies have no literature scan**, so they could land without",
                "anyone noticing: " + ", ".join(f"`{x}`" for x in unscanned) + ".\n"]
    out += ["## Detail\n"]
    for t in sorted(g["technologies"], key=lambda x: -x["fan_out"]):
        c = fc.get(t.get("forecast"), {})
        u = t.get("unblocks", {})
        out += [f"### {t['id']} — fan-out {t['fan_out']}\n", f"**{esc(t['name'])}**\n",
                f"*Category:* `{t['category']}` · *state:* `{t['current_state']}` · "
                f"*confidence in that state:* `{t['confidence']}`\n",
                f"**Why it matters.** {t['why_it_matters']}\n"]
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
        out.append(f"*Scanned by:* {', '.join('`'+x+'`' for x in t.get('scan_trigger', [])) or '⚠ **nothing**'}\n")
    out.append("[← L0](L0-ecosystem.md)\n")
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
    out.append("\n[← L0](L0-ecosystem.md)\n")
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


def all_views(g):
    v = {"L0-ecosystem.md": render_l0(g),
         "registers/blockers.md": render_blockers(g),
         "registers/technologies.md": render_technologies(g),
         "registers/instruments.md": render_instruments(g),
         "methods-index.md": render_methods_index(g),
         "readiness.md": render_readiness(g)}
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
