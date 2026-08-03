#!/usr/bin/env python3
"""
The EMC systems-map checker — invariants over `emc-systems-map.json`, plus the generator for its
human view `emc-systems-map.md`.

WHY THIS EXISTS. Four integrity failures were found in this repo on 2026-08-03, and a prose map
prevents none of them, because prose cannot be run:

  1. ONE PIECE OF EVIDENCE UNDER TWO NAMES. Five files cited the NOR-1 druggability result under a
     wrong author name with no PMID, while other places cited it correctly as Zaienne et al.,
     ChemMedChem 2022, PMID 35704774 -- so a route was graded while its own supporting evidence sat
     in another file, unfindable. (That specific attribution was measured, corrected and RETIRED on
     2026-08-03; the superseded name is retained and quotable, its correction has one home in
     `research/modalities/nr4a3-druggability-reconciliation.md` §5b, and its repo-wide enforcement
     belongs to `research/modalities/tests/test_munck_attribution_retired.py`. What is checked HERE
     is the structural half: that every name a source travels under resolves to exactly one evidence
     item, so the CLASS of error cannot recur under a new name.)  ->  E1, E2, E3, E4
  2. ONE OBJECT UNDER TWO INCOMPATIBLE DEFINITIONS. "EWSR1 e7 :: NR4A3 e3" is called "the canonical
     EMC fusion" and is not a reported fusion type at all; reported type 2 additionally carries 59
     UTR-encoded residues that `fusion_cofold.py`'s protein-level model does not have.  ->  O1, O2
  3. ONE GRADE OVER TWO DIFFERENT ROUTES. The covalent probe at C397 and a monovalent reversible
     pocket modulator were carried as one row and one demotion, though they fail on OPPOSITE
     blockers.  ->  R1, R2, R3
  4. A NUMBER QUOTED FROM AN ARTIFACT THAT IS A STUB ON THE REF A READER WOULD OPEN.
     `emc-fet-idr-census.json` is a 161-byte "cannot compute" placeholder on `main` while a document
     on `main` prints a full results table out of it.  ->  C1, C2, C3

SCOPE. This is a NAVIGATION AND INTEGRITY layer. It checks that pointers resolve and that names are
unambiguous. It grades nothing and re-derives nothing (CLAUDE.md §1 and §5).

Pure stdlib. Usage:

    python3 research/manuscripts/emc_systems_map_check.py --check      # CI mode (default)
    python3 research/manuscripts/emc_systems_map_check.py --write-view # regenerate the .md

`--check` also regenerates the view in memory and fails if the committed `.md` differs, because a
DERIVED view that can drift from its source is exactly the bug this registry exists to catch
(CLAUDE.md §1: a total is derived, never typed).
"""

import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAP_PATH = os.path.join(REPO, "research/manuscripts/emc-systems-map.json")
VIEW_PATH = os.path.join(REPO, "research/manuscripts/emc-systems-map.md")

# The ref a reader following a link from the default branch would actually open. Claim artifacts are
# checked THERE, not in the working tree -- checking the working tree is what let failure 4 survive.
#
# ⚠ THE REMOTE-TRACKING REF COMES FIRST, AND THAT ORDER IS THE WHOLE POINT. The first version of
# this list tried local `main` first and was measured, minutes later, reading a local `main` that
# was 183 commits stale -- so it reported nine claim artifacts as absent/stubbed when they had just
# been merged and pushed. A stale local branch reporting as the publish ref is EXACTLY the failure
# this checker exists to catch, committed by the checker itself. What a reader opens is the ref on
# the remote; a local branch of the same name is a convenience, not the publish ref, so it is the
# LAST resort and says so when it is used.
#
# `actions/checkout` fetches one branch, so on a feature-branch CI run neither may exist until the
# workflow's explicit fetch runs; the check then falls back to the working tree, loudly.
PUBLISH_REF_CANDIDATES = ("origin/main", "refs/remotes/origin/main", "main")

# An instrument whose own known-answer control is in one of these states may not be listed as
# SUPPORT for a route. `none` is included deliberately: "no control exists" and "the control failed"
# are different facts, but neither of them is support.
NON_SUPPORTING_CONTROL_STATES = {"fails", "none", "inconclusive"}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, code, msg):
        self.errors.append((code, msg))

    def warn(self, code, msg):
        self.warnings.append((code, msg))


def git_show(ref, path):
    """Bytes of `path` at `ref`, or None if git cannot produce it (absent file, no repo, no ref)."""
    try:
        return subprocess.run(
            ["git", "-C", REPO, "show", f"{ref}:{path}"],
            capture_output=True, check=True,
        ).stdout
    except Exception:  # noqa: BLE001 -- absent file and absent git are the same answer here
        return None


def ref_exists(ref):
    try:
        subprocess.run(["git", "-C", REPO, "rev-parse", "--verify", f"{ref}^{{commit}}"],
                       capture_output=True, check=True)
        return True
    except Exception:  # noqa: BLE001
        return False


def is_stub_bytes(raw):
    """True if `raw` is a JSON object carrying only `_`-prefixed meta keys.

    The same test as `research/modalities/artifact_stub_guard.py::is_stub`, deliberately: one rule,
    one meaning. Every real artifact in these folders has data keys; the provenance keys the modules
    write are `_`-prefixed by convention. Unparseable JSON counts as a stub -- a truncated write is
    not something to quote from either.
    """
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception:  # noqa: BLE001
        return True
    if not isinstance(doc, dict):
        return False
    if not doc:
        return True
    return all(str(k).startswith("_") for k in doc)


def resolve_field(doc, pointer):
    """Resolve a slash-separated field path against a parsed artifact.

    Not RFC-6901: keys in these artifacts contain characters that would need escaping and the point
    is legibility in the registry, not standards compliance. Returns (found, value).
    """
    cur = doc
    for part in [p for p in pointer.split("/") if p]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return False, None
    return True, cur


def load_map(path=MAP_PATH):
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# invariants
# ---------------------------------------------------------------------------

def check_ids_unique(m, f):
    """S1 -- every registry section has unique, non-empty IDs, and cross-references resolve."""
    for section in ("blockers", "evidence", "objects", "instruments", "artifacts", "routes",
                    "claims", "open_conflicts"):
        seen = {}
        for i, item in enumerate(m.get(section, [])):
            iid = item.get("id")
            if not iid:
                f.error("S1", f"{section}[{i}] has no id")
                continue
            if iid in seen:
                f.error("S1", f"{section}: duplicate id {iid!r}")
            seen[iid] = True


def check_evidence_names(m, f):
    """E1/E2/E3 -- the Munck/Zaienne class of error, made structurally impossible.

    E1  an evidence item cited under a name that is neither a canonical identifier nor a registered
        alias (including a registered MISATTRIBUTION -- a wrong name that is known and recorded is
        not the failure; a wrong name that nothing resolves is).
    E2  two evidence entries sharing a PMID / PMCID / DOI -- the same source entered twice under
        different names, which is how one piece of evidence becomes two.
    E3  one name resolving to two different evidence entries.
    """
    by_ident = {}
    name_owner = {}

    for ev in m.get("evidence", []):
        eid = ev["id"]
        canon = ev.get("canonical", {}) or {}
        if not any(canon.get(k) for k in ("pmid", "pmcid", "doi")):
            if not ev.get("provenance_flag"):
                f.error("E2", f"{eid}: no PMID/PMCID/DOI and no provenance_flag explaining the gap")
            else:
                f.warn("E2", f"{eid}: no canonical identifier -- registered with a provenance_flag; "
                             f"it cannot be verified through verify-refs until one exists")
        for kind in ("pmid", "pmcid", "doi"):
            val = canon.get(kind)
            if not val:
                continue
            key = (kind, str(val).strip().lower())
            if key in by_ident:
                f.error("E2", f"{kind.upper()} {val} is on BOTH {by_ident[key]} and {eid} -- "
                              f"one source entered twice under different names")
            by_ident[key] = eid

        names = set(ev.get("aliases", [])) | set(ev.get("misattributed_as", []))
        names |= {str(v) for v in canon.values() if v}
        names |= {f"PMID {canon['pmid']}"} if canon.get("pmid") else set()
        for n in names:
            prior = name_owner.get(n)
            if prior and prior != eid:
                f.error("E3", f"the name {n!r} resolves to BOTH {prior} and {eid}")
            name_owner[n] = eid

        for occ in ev.get("cited_in", []):
            name = occ.get("as")
            if name not in names:
                f.error("E1", f"{eid} is cited in {occ.get('file')} as {name!r}, which is neither "
                              f"its canonical identifier nor a registered alias")

    # E4 -- a registered occurrence that is no longer in its file is a STALE REGISTRY, and a stale
    # registry is worse than none: it reads as a survey of where a name lives while pointing at
    # places it no longer does.
    #
    # ⚠ WHAT THIS DELIBERATELY DOES NOT DO: sweep the repository for stray misattributions. That is
    # a real check and it already has an owner --
    # `research/modalities/tests/test_munck_attribution_retired.py` -- which permits a retired name
    # wherever it is marked superseded/retained (CLAUDE.md §1.2) and forbids it as a live citation.
    # Re-implementing it here would be a second home for one rule, with a different and slightly
    # wrong definition, which is the exact bug this registry exists to catch. So instead: an
    # evidence item that carries a misattribution must NAME the guard that enforces it, and the
    # guard must exist.
    for ev in m.get("evidence", []):
        for occ in ev.get("cited_in", []):
            path = occ.get("file")
            name = occ.get("as")
            full = os.path.join(REPO, path or "")
            if not os.path.exists(full):
                f.warn("E4", f"{ev['id']}: registered occurrence file {path} is not in this checkout")
                continue
            try:
                with open(full, encoding="utf-8", errors="ignore") as fh:
                    body = fh.read()
            except OSError:
                continue
            if name not in body:
                f.error("E4", f"{ev['id']}: registered as cited in {path} as {name!r}, and that "
                              f"string is no longer there -- the registry is stale")

        if ev.get("misattributed_as"):
            guard = ev.get("retired_by")
            if not guard:
                f.error("E1", f"{ev['id']} registers a misattribution but names no guard "
                              f"(`retired_by`) that keeps it from returning as a live citation")
            elif not os.path.exists(os.path.join(REPO, guard)):
                f.error("E1", f"{ev['id']}: its named guard {guard} does not exist")
            if not ev.get("correction_home"):
                f.error("E1", f"{ev['id']} registers a misattribution with no `correction_home` -- "
                              f"the correction must have exactly one home to point at")


def check_objects(m, f):
    """O1/O2 -- the fusion-junction class of error.

    O1  a name that maps to more than one object definition. Two routes here: a name appearing in
        two objects' `aliases`, and a name on the explicit `contested_names` list appearing in ANY
        object's aliases (a name known to be ambiguous may not be quietly attached to one reading).
    O2  an object whose definition is incomplete in the way that let the incompatible models coexist
        -- a reported fusion with no exon-level statement, or with no provenance.
    """
    contested = {c["name"]: c for c in m.get("contested_names", [])}
    owner = {}
    for obj in m.get("objects", []):
        oid = obj["id"]
        for name in obj.get("aliases", []) + [obj.get("display_name", "")]:
            if not name:
                continue
            if name in contested:
                f.error("O1", f"{oid} claims the CONTESTED name {name!r} as an alias -- a name "
                              f"registered as mapping to {contested[name]['maps_to']} may not be "
                              f"attached to one reading")
            prior = owner.get(name)
            if prior and prior != oid:
                f.error("O1", f"the object name {name!r} maps to BOTH {prior} and {oid}")
            owner[name] = oid

        d = obj.get("definition", {}) or {}
        if obj.get("status") == "reported":
            if not d.get("exon_level"):
                f.error("O2", f"{oid} is status=reported but carries no exon-level definition")
            if not d.get("provenance"):
                f.error("O2", f"{oid} is status=reported but cites no evidence for its junction")
        if obj.get("status") == "modelled_not_reported" and not obj.get("distinct_from"):
            f.error("O2", f"{oid} is a MODEL that is not a reported object and names nothing it "
                          f"must not be confused with")

    for c in m.get("contested_names", []):
        if len(c.get("maps_to", [])) < 2:
            f.error("O1", f"contested name {c['name']!r} maps to fewer than two objects -- it is "
                          f"not contested and should be an alias")
        if not c.get("conflict"):
            f.error("O1", f"contested name {c['name']!r} names no open conflict that owns it")


def check_routes(m, f):
    """R1/R2/R3 -- the one-grade-two-routes class of error.

    R1  two routes sharing a grade-owning (file, anchor). A memo owns many routes' grades; a
        SECTION owns exactly one, so the owner is the pair and the pair must be unique.
    R2  a route whose grade is asserted in more than one place. Other files may point at the grade
        (`asserts_grade: false`); a second assertion is a second home for the same fact.
    R3  two routes declared distinct from one another while carrying the SAME grade with no
        separate justification -- i.e. no differing `fails_on` blocker sets. This is the covalent
        probe / monovalent modulator case: distinctness that is asserted but not grounded is what
        lets the two collapse back into one row at the next edit.
    """
    routes = {r["id"]: r for r in m.get("routes", [])}
    blockers = {b["id"] for b in m.get("blockers", [])}

    owners = {}
    for rid, r in routes.items():
        g = r.get("grade", {}) or {}
        own = g.get("owner", {}) or {}
        if not own.get("file"):
            f.error("R2", f"{rid} has no grade-owning file")
            continue
        key = (own["file"], own.get("anchor"))
        if key in owners:
            f.error("R1", f"{rid} and {owners[key]} both own their grade at {own['file']}"
                          f"{'#' + str(own.get('anchor')) if own.get('anchor') else ''} -- "
                          f"one section cannot be the one home of two grades")
        owners[key] = rid

        extra = [p for p in r.get("grade_pointers", []) if p.get("asserts_grade")]
        if extra:
            f.error("R2", f"{rid}: grade asserted in {len(extra) + 1} places "
                          f"({own['file']} plus {[p['file'] for p in extra]}) -- one fact, one place")

        for b in r.get("blockers_inherited", []) + r.get("blockers_retired", []):
            if b not in blockers:
                f.error("R2", f"{rid} references unregistered blocker {b!r}")

    for rid, r in routes.items():
        for df in r.get("distinct_from", []):
            other = df.get("route")
            if other not in routes:
                f.error("R3", f"{rid} is declared distinct from unregistered route {other!r}")
                continue
            if not df.get("fails_on"):
                f.error("R3", f"{rid} vs {other}: distinctness asserted with no `fails_on` blocker "
                              f"set -- an ungrounded distinction collapses at the next edit")
                continue
            for b in df["fails_on"]:
                if b not in blockers:
                    f.error("R3", f"{rid} vs {other}: unregistered blocker {b!r} in fails_on")

            mine = set(df["fails_on"])
            back = next((d for d in routes[other].get("distinct_from", [])
                         if d.get("route") == rid), None)
            theirs = set(back.get("fails_on", [])) if back else None

            same_grade = ((r.get("grade", {}) or {}).get("value")
                          == (routes[other].get("grade", {}) or {}).get("value"))
            if same_grade and theirs is not None and mine == theirs:
                f.error("R3", f"{rid} and {other} carry the SAME grade and are declared distinct on "
                              f"the SAME blockers -- either the distinction or the shared grade is "
                              f"wrong. This is the covalent-probe / monovalent-modulator shape")
            if back is None:
                f.warn("R3", f"{rid} declares distinctness from {other}, which does not declare it "
                             f"back -- distinctness is symmetric and should be recorded both ways")


def check_instruments(m, f):
    """I1/I2 -- an instrument may not be cited as SUPPORT while its own control is failing/absent.

    An instrument that has never recovered a known answer cannot support a claim, however good its
    output looks -- that is the roadmap's own instrument-table rule, and this is the machine form of
    it. A route may still LIST such an instrument, under `disclosed_failing`, which is how the
    honest memos already write it.
    """
    instruments = {i["id"]: i for i in m.get("instruments", [])}
    for i in m.get("instruments", []):
        st = ((i.get("known_answer_control") or {}).get("state"))
        if st not in {"passes", "fails", "none", "inconclusive", "mixed", "parked"}:
            f.error("I2", f"{i['id']}: unknown known_answer_control.state {st!r}")

    for r in m.get("routes", []):
        cited = r.get("instruments", {}) or {}
        for iid in cited.get("support", []):
            if iid not in instruments:
                f.error("I2", f"{r['id']} cites unregistered instrument {iid!r} as support")
                continue
            st = (instruments[iid].get("known_answer_control") or {}).get("state")
            if st in NON_SUPPORTING_CONTROL_STATES:
                f.error("I1", f"{r['id']} cites {iid} as SUPPORT while that instrument's own "
                              f"known-answer control is recorded as {st!r} -- move it to "
                              f"`disclosed_failing` or the route rests on an unvalidated readout")
        for iid in cited.get("disclosed_failing", []):
            if iid not in instruments:
                f.error("I2", f"{r['id']} lists unregistered instrument {iid!r} as disclosed_failing")


def check_claims(m, f):
    """C1/C2/C3 -- a quoted figure must resolve to a real field of a real artifact ON `main`.

    C1  the artifact is absent on the publish ref.
    C2  the artifact is present but is a STUB there (all-meta-keys) -- the failure-4 shape: a
        document reads as current while the thing it quotes carries no data.
    C3  the artifact resolves but the named field does not exist in it.
    """
    artifacts = {a["id"]: a for a in m.get("artifacts", [])}
    publish_ref = next((r for r in PUBLISH_REF_CANDIDATES if ref_exists(r)), None)
    have_ref = publish_ref is not None
    if publish_ref == "main":
        f.warn("C1", "no remote-tracking origin/main in this checkout, so claim artifacts were "
                     "checked against the LOCAL `main`, which can be arbitrarily stale -- fetch "
                     "origin/main before trusting a C1/C2 result")
    if not have_ref:
        f.warn("C1", f"none of {PUBLISH_REF_CANDIDATES} is present in this checkout -- claim "
                     f"artifacts were checked in the WORKING TREE, which is weaker than the "
                     f"invariant intends. Fetch the publish ref before running this in CI")

    for c in m.get("claims", []):
        aid = c.get("artifact")
        art = artifacts.get(aid)
        if art is None:
            f.error("C1", f"{c['id']} points at unregistered artifact {aid!r}")
            continue
        path = art["path"]

        raw = git_show(publish_ref, path) if have_ref else None
        where = f"on `{publish_ref}`"
        if raw is None and not have_ref:
            try:
                with open(os.path.join(REPO, path), "rb") as fh:
                    raw = fh.read()
                where = "in the working tree"
            except OSError:
                raw = None

        if raw is None:
            f.error("C1", f"{c['id']}: {c['document']} quotes {path}, which is ABSENT {where}")
            continue
        if is_stub_bytes(raw):
            f.error("C2", f"{c['id']}: {c['document']} quotes {path}, which is a STUB {where} "
                          f"(every top-level key is meta) -- the figure reads as current and is "
                          f"backed by nothing on the ref a reader would open")
            continue
        if c.get("field"):
            try:
                doc = json.loads(raw.decode("utf-8"))
            except Exception as exc:  # noqa: BLE001
                f.error("C2", f"{c['id']}: {path} is unparseable {where}: {exc}")
                continue
            found, _ = resolve_field(doc, c["field"])
            if not found:
                f.error("C3", f"{c['id']}: field {c['field']!r} does not resolve in {path} {where}")


def check_artifact_paths(m, f):
    """A1 -- every registered artifact and producing module exists somewhere in this checkout."""
    for a in m.get("artifacts", []):
        if not os.path.exists(os.path.join(REPO, a["path"])):
            f.warn("A1", f"{a['id']}: {a['path']} is not in this checkout (it may live only on "
                         f"another ref -- {a.get('published_to')})")
        mod = a.get("produced_by")
        if mod and not os.path.exists(os.path.join(REPO, mod)):
            f.warn("A1", f"{a['id']}: producing module {mod} is not in this checkout")


def check_conflicts(m, f):
    """X1 -- an open conflict must name files, at least two positions, and an owner.

    A conflict logged without an owner is a decision deferred to nobody, which is the status-shaped
    unanswered question CLAUDE.md §4 is about.
    """
    for c in m.get("open_conflicts", []):
        if not c.get("files"):
            f.error("X1", f"{c['id']}: no files")
        if len(c.get("positions", [])) < 2:
            f.error("X1", f"{c['id']}: fewer than two positions recorded -- a conflict needs the "
                          f"sides that disagree, or it is a note")
        if not c.get("owner"):
            f.error("X1", f"{c['id']}: no owner -- a conflict with no owner is deferred to nobody")
        if not c.get("why_not_decided"):
            f.error("X1", f"{c['id']}: no why_not_decided")


# ---------------------------------------------------------------------------
# closure kind and revival triggers
# ---------------------------------------------------------------------------
#
# WHY THIS IS A FIRST-CLASS FIELD AND NOT A NOTE (trimcrae, 2026-08-03). AI methods are advancing
# fast, so many currently-closed paths WILL be unblocked. A register that files
#
#     "a residue the paralogues SHARE cannot discriminate between them"   (true forever)
#
# beside
#
#     "sequence-only co-folding assembles the two halves wrongly, DockQ 0.023-0.046"   (true today)
#
# under one word -- "closed" -- has destroyed the only distinction that matters for deciding what to
# watch for. `instrument_limit` is the most revivable category and is where most of this program's
# failures actually sit; that is precisely why it must be nameable.
#
# `permanently_closed` and `revival_would_reopen` are DERIVED here and rendered into the view. They
# are never written into the registry, and Z6 fails if they are -- CLAUDE.md §1: a derived value is
# regenerated, not hand-maintained.

# A trigger must be usable verbatim as a literature-search query: a sibling agent's weekly field
# scan searches for these strings by name. "Better methods" is not searchable, so it is refused.
VAGUE_TOKENS = re.compile(
    r"\b(better|improved|improve|more accurate|more reliable|newer|advances? in|"
    r"state[- ]of[- ]the[- ]art|next[- ]gen(?:eration)?|when the field|as methods mature)\b", re.I)

# A trigger must NAME something. One of: a named thing (an acronym or CamelCase token such as DockQ,
# AlphaFlow, CRL, PROTAC, RNF114, NR4A1), or a quantity with a unit.
NAMED_THING = re.compile(r"\b(?:[A-Z]{2,}[A-Za-z0-9-]*|[A-Z][a-z]+[A-Z][A-Za-z0-9]*|[A-Za-z]+-?\d+)\b")
QUANTITY = re.compile(r"\d+(?:\.\d+)?\s*(?:kcal/mol|Angstrom|Å|%|atom|atoms|ns|µM|uM|nM|residues?)\b", re.I)
# ...and a CAPABILITY: what has to be demonstrated, not merely what would be nice.
CAPABILITY = re.compile(
    r"\b(validat\w*|benchmark\w*|reach\w*|resolv\w*|recover\w*|reproduc\w*|"
    r"deposit\w*|report\w*|demonstrat\w*|regenerat\w*|execut\w*|authoriz\w*|"
    r"access\w*|evaluat\w*|predict\w*|passes|pass\w*|contradict\w*)\b", re.I)

MIN_TRIGGER_CHARS = 60


def closure_model(m):
    return (m.get("_closure_model") or {}).get("kinds", {})


def is_permanent(m, kind):
    """DERIVED, never typed: permanence is a property of the KIND, read from the closure model."""
    return bool(closure_model(m).get(kind, {}).get("permanent"))


def would_reopen(m, item):
    """DERIVED, never typed: the union of what this item's triggers would reopen."""
    by_id = {t["id"]: t for t in m.get("revival_triggers", [])}
    out = []
    for tid in item.get("revival_trigger", []) or []:
        for r in by_id.get(tid, {}).get("would_reopen", []):
            if r not in out:
                out.append(r)
    return out


def check_closures(m, f):
    """Z1-Z7 -- which KIND of closure each dead end is, and what would revive it.

    Z1  every route and instrument carries a `closure_kind` from the registered enumeration.
    Z2  a NON-permanent closure must name a `revival_trigger`. "Closed, and nothing says what would
        change that" is the state this field exists to abolish.
    Z3  a PERMANENT closure (`definitional`, `arithmetic_over_fixed_fact`) may NOT carry a revival
        trigger. That is a category error in either direction: a fact about a sequence filed as
        temporary, or a method limitation filed as a law of nature.
    Z4  a trigger must be SPECIFIC enough to be a literature-search query -- it must name a method,
        artifact, measurable quantity or capability, and must not lean on a bare comparative.
    Z5  (WARN) a trigger that no watch list carries is a trigger nobody is watching for.
    Z6  `permanently_closed` and `revival_would_reopen` are derived; typing them is the bug.
    Z7  every trigger must resolve, and must say what it would reopen.
    """
    kinds = closure_model(m)
    if not kinds:
        f.error("Z1", "no `_closure_model.kinds` -- the enumeration has no home")
        return
    triggers = {t["id"]: t for t in m.get("revival_triggers", [])}

    try:
        with open(os.path.join(REPO, "research/method-watch.md"), encoding="utf-8") as fh:
            watch = fh.read().lower()
    except OSError:
        watch = ""

    for t in m.get("revival_triggers", []):
        s = t.get("trigger", "")
        tid = t["id"]
        if len(s) < MIN_TRIGGER_CHARS:
            f.error("Z4", f"{tid}: trigger is {len(s)} chars, under the {MIN_TRIGGER_CHARS}-char "
                          f"floor -- too short to be a search query")
        bad = VAGUE_TOKENS.search(s)
        if bad and not QUANTITY.search(s):
            f.error("Z4", f"{tid}: trigger leans on the bare comparative {bad.group(0)!r} with no "
                          f"measurable quantity beside it -- say what must be demonstrated, "
                          f"not that it must be better")
        if not (NAMED_THING.search(s) or QUANTITY.search(s)):
            f.error("Z4", f"{tid}: trigger names no method, artifact or measurable quantity")
        if not CAPABILITY.search(s):
            f.error("Z4", f"{tid}: trigger states no capability that must be demonstrated")
        if not t.get("would_reopen"):
            f.error("Z7", f"{tid}: names nothing it would reopen -- a trigger nobody benefits from "
                          f"is not a trigger")
        if not t.get("why_this_string"):
            f.error("Z7", f"{tid}: no `why_this_string` -- a search query with no rationale cannot "
                          f"be re-graded when it fires")
        # Z5 -- watch-list membership is EVIDENCED, not asserted. A typed `on_watch_list: true` with
        # nothing behind it is exactly the "populated field is not a measured one" failure
        # (CLAUDE.md §4), so the claim must quote a verbatim row from the watch list.
        if t.get("on_watch_list"):
            ev = t.get("watch_list_evidence")
            if not ev:
                f.error("Z5", f"{tid}: claims to be on the watch list with no "
                              f"`watch_list_evidence` -- an asserted field is not a measured one")
            elif watch and ev.lower() not in watch:
                f.error("Z5", f"{tid}: its `watch_list_evidence` {ev[:50]!r} is not in "
                              f"research/method-watch.md -- the claim is stale or was never true")
        else:
            f.warn("Z5", f"{tid} is not carried by research/method-watch.md -- it is a trigger "
                         f"nobody is scanning for")

    # Z8 -- the cross-check with the sibling SCAN registry, which owns the search queries and
    # explicitly defers the route<->trigger graph to this file. A `TRG-*` id that does not exist
    # there is a scan nobody runs; a scannable trigger with no `TRG-*` at all is a capability
    # nobody is looking for. The file is checked only if present, so neither repo is hard-wired to
    # the other's landing order.
    scan_path = (m.get("_scan_interop") or {}).get("_scan_registry")
    scan_ids, scan_present = set(), False
    if scan_path and os.path.exists(os.path.join(REPO, scan_path)):
        try:
            with open(os.path.join(REPO, scan_path)) as fh:
                scan_ids = {t.get("id") for t in json.load(fh).get("triggers", [])}
            scan_present = True
        except Exception as exc:  # noqa: BLE001
            f.warn("Z8", f"{scan_path} is present but unreadable ({exc}) -- cross-check skipped")
    scannable = {"external_capability", "external_measurement", "external_data"}
    for t in m.get("revival_triggers", []):
        kind = t.get("trigger_kind")
        if kind is None:
            f.error("Z8", f"{t['id']}: no `trigger_kind` -- without it there is no way to say "
                          f"whether a literature scan could ever detect this trigger")
            continue
        refs = t.get("scan_trigger") or []
        if scan_present:
            for ref in refs:
                if ref not in scan_ids:
                    f.error("Z8", f"{t['id']}: scan_trigger {ref!r} is not in {scan_path} -- "
                                  f"it points at a query that does not exist")
        if kind in scannable and not refs:
            f.warn("Z8", f"{t['id']} is {kind} but has no `scan_trigger` -- it is detectable in "
                         f"principle and nothing is searching for it")

    known_ids = ({r["id"] for r in m.get("routes", [])}
                 | {i["id"] for i in m.get("instruments", [])})
    for t in m.get("revival_triggers", []):
        for target in t.get("would_reopen", []):
            if target not in known_ids and not re.fullmatch(r"R\d+", target):
                f.error("Z7", f"{t['id']}: would_reopen names {target!r}, which is neither a "
                              f"registered route/instrument nor an `R*` requirement")

    for section in ("routes", "instruments"):
        for item in m.get(section, []):
            iid = item["id"]
            for derived in ("permanently_closed", "revival_would_reopen"):
                if derived in item:
                    f.error("Z6", f"{iid}: `{derived}` is DERIVED and must not be typed into the "
                                  f"registry -- it is regenerated from `closure_kind` and the "
                                  f"trigger registry")
            kind = item.get("closure_kind")
            if kind not in kinds:
                f.error("Z1", f"{iid}: closure_kind {kind!r} is not in the registered enumeration "
                              f"{sorted(kinds)}")
                continue
            trigs = item.get("revival_trigger", []) or []
            for tid in trigs:
                if tid not in triggers:
                    f.error("Z2", f"{iid}: unregistered revival_trigger {tid!r}")
            if is_permanent(m, kind) and trigs:
                f.error("Z3", f"{iid}: closure_kind {kind!r} is PERMANENT and yet carries revival "
                              f"trigger(s) {trigs} -- a category error. Either the fact is not "
                              f"permanent, or the trigger belongs to a different row")
            if kinds[kind].get("needs_trigger") and not trigs:
                f.error("Z2", f"{iid}: closure_kind {kind!r} is not permanent and names no "
                              f"`revival_trigger` -- 'closed, and nothing says what would change "
                              f"that' is the state this field abolishes")


ALL_CHECKS = (
    check_ids_unique,
    check_evidence_names,
    check_objects,
    check_routes,
    check_instruments,
    check_claims,
    check_artifact_paths,
    check_conflicts,
    check_closures,
)


# ---------------------------------------------------------------------------
# the derived view
# ---------------------------------------------------------------------------

def _md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def _link(file_, anchor=None):
    if not file_:
        return "—"
    rel = os.path.relpath(os.path.join(REPO, file_), os.path.dirname(VIEW_PATH))
    frag = ""
    if anchor:
        frag = anchor if str(anchor).startswith("#") else "#" + str(anchor)
        if "|" in frag:  # a disambiguating suffix the file itself has no anchor for
            frag = frag.split("|")[0]
    return f"[`{os.path.basename(file_)}`]({rel}{frag})"


def render_view(m):
    routes = m["routes"]
    blockers = {b["id"]: b for b in m["blockers"]}
    instruments = {i["id"]: i for i in m["instruments"]}
    out = []
    w = out.append

    w("# The EMC systems map — routes, objects, evidence, instruments, artifacts, claims")
    w("")
    w("> ⛔ **GENERATED FILE — DO NOT EDIT.** Its one home is "
      "[`emc-systems-map.json`](./emc-systems-map.json); regenerate with "
      "`python3 research/manuscripts/emc_systems_map_check.py --write-view`. "
      "CI fails if this file and the registry disagree (CLAUDE.md §1 — a derived view is "
      "regenerated, never hand-maintained).")
    w(">")
    w("> **Role: navigation and integrity, not analysis.** This page grades nothing, re-derives "
      "nothing and restates no figure that has a home elsewhere. Every grade cell names the file "
      "that owns it; every claim names the artifact field that owns it. To change a grade, edit "
      "the owning file — changing it here changes nothing and will be overwritten.")
    w(">")
    w("> **$0.** No GPU, no rental, no purchase, no contact, no wet lab. No efficacy, potency, "
      "safety, therapeutic-window or clinical-readiness claim is made for any route or molecule, "
      "and none follows from anything below.")
    w("")
    w("## Why it exists")
    w("")
    for reason in m["_why_it_exists"]:
        w(f"- {reason}")
    w("")
    w(f"**Registry contents:** {len(routes)} routes · {len(m['objects'])} objects · "
      f"{len(m['evidence'])} evidence items · {len(instruments)} instruments · "
      f"{len(m['artifacts'])} artifacts · {len(m['claims'])} claims · "
      f"{len(blockers)} blockers · {len(m['open_conflicts'])} open conflicts.")
    w("")
    w("---")
    w("")

    # ---- routes -----------------------------------------------------------
    w("## 1 · Every route, its grade, and where that grade lives")
    w("")
    w("One route, one grade, one owning section. Other files may **point** at a grade; a second "
      "assertion is a second home for the same fact and the checker fails on it.")
    w("")
    w("| route | id | grade (as the owner words it) | ⚠ the grade lives HERE | also mentioned in |")
    w("|---|---|---|---|---|")
    for r in sorted(routes, key=lambda x: x["id"]):
        g = r.get("grade", {}) or {}
        own = g.get("owner", {}) or {}
        ptrs = ", ".join(_link(p["file"]) for p in r.get("grade_pointers", [])) or "—"
        w(f"| **{_md_escape(r['display_name'])}** | `{r['id']}` | {_md_escape(g.get('value', '—'))} "
          f"| {_link(own.get('file'), own.get('anchor'))} | {ptrs} |")
    w("")

    # ---- aliases ----------------------------------------------------------
    w("### 1a · Route aliases — the same route under every number the repo has given it")
    w("")
    w("Route numbers are stable identifiers *inside* each memo and they are **not** the same "
      "numbering. This table is what stops \"route 5\" in one file being read as \"route 5\" in "
      "another.")
    w("")
    w("| id | also called |")
    w("|---|---|")
    for r in sorted(routes, key=lambda x: x["id"]):
        al = ", ".join(f"`{a}`" for a in r.get("aliases", [])) or "—"
        w(f"| `{r['id']}` | {al} |")
    w("")

    # ---- distinctness -----------------------------------------------------
    w("## 2 · What must never be conflated — and what each pair actually fails on")
    w("")
    w("A distinctness that is asserted but not grounded collapses at the next edit, so every row "
      "carries the blockers that make the two routes different. **Two routes carrying the same "
      "grade and the same blockers are not two routes** — the checker fails on that shape, which "
      "is the covalent-probe / monovalent-modulator failure.")
    w("")
    w("| route | must not be conflated with | axis | it fails on | why |")
    w("|---|---|---|---|---|")
    for r in sorted(routes, key=lambda x: x["id"]):
        for df in r.get("distinct_from", []):
            fo = ", ".join(f"`{b}`" for b in df.get("fails_on", [])) or "—"
            w(f"| `{r['id']}` | `{df['route']}` | {_md_escape(df.get('axis', '—'))} | {fo} "
              f"| {_md_escape(df.get('why', ''))} |")
    w("")

    # ---- load-bearing blockers -------------------------------------------
    w("## 3 · Load-bearing blockers — which one failure holds down how many routes")
    w("")
    w("Read this as *redundancy*: a blocker on one route is a risk, a blocker on eleven is the "
      "portfolio's shape. A route that **retires** a blocker is the portfolio's answer to it.")
    w("")
    w("| blocker | it is a statement about | one home | inherited by | retired by |")
    w("|---|---|---|---|---|")
    rows = []
    for bid, b in blockers.items():
        inh = [r["id"] for r in routes if bid in r.get("blockers_inherited", [])]
        ret = [r["id"] for r in routes if bid in r.get("blockers_retired", [])]
        rows.append((len(inh), bid, b, inh, ret))
    for _, bid, b, inh, ret in sorted(rows, key=lambda t: (-t[0], t[1])):
        own = b.get("owner", {}) or {}
        w(f"| **{_md_escape(b['name'])}** (`{bid}`) | {_md_escape(b.get('statement_about', '—'))} "
          f"| {_link(own.get('file'), own.get('anchor'))} | **{len(inh)}** — "
          f"{', '.join('`' + i + '`' for i in inh) or '—'} | "
          f"{', '.join('`' + i + '`' for i in ret) or '—'} |")
    w("")

    # ---- instruments ------------------------------------------------------
    w("## 4 · Instruments — and which of them have no passing control")
    w("")
    w("An instrument that has never recovered a known answer cannot support a claim, however good "
      "its output looks. A route may still *list* such an instrument — under **disclosed failing** "
      "— which is how the honest memos already write it. Citing one as **support** is a checker "
      "failure.")
    w("")
    w("| instrument | known-answer control | state | cited as SUPPORT by | disclosed-failing on |")
    w("|---|---|---|---|---|")
    for i in m["instruments"]:
        k = i.get("known_answer_control", {}) or {}
        st = k.get("state", "?")
        glyph = {"passes": "✓ passes", "fails": "⛔ FAILS", "none": "⚠ no control",
                 "inconclusive": "⚠ inconclusive", "mixed": "⚠ mixed", "parked": "⏸ parked"}.get(st, st)
        sup = [r["id"] for r in routes if i["id"] in (r.get("instruments", {}) or {}).get("support", [])]
        dis = [r["id"] for r in routes if i["id"] in (r.get("instruments", {}) or {}).get("disclosed_failing", [])]
        w(f"| **`{i['id']}`** {_md_escape(i['name'])} | {_md_escape(k.get('description', '—'))} "
          f"| {glyph} | {', '.join('`' + s + '`' for s in sup) or '—'} "
          f"| {', '.join('`' + d + '`' for d in dis) or '—'} |")
    w("")
    no_control = [i["id"] for i in m["instruments"]
                  if (i.get("known_answer_control") or {}).get("state") in NON_SUPPORTING_CONTROL_STATES]
    w(f"⛔ **{len(no_control)} of {len(m['instruments'])} instruments have no passing known-answer "
      f"control:** {', '.join('`' + i + '`' for i in no_control)}. That is decision-relevant and "
      f"is the reason this column exists.")
    w("")

    # ---- objects ----------------------------------------------------------
    w("## 5 · Objects — every biological entity, at exon and residue level")
    w("")
    w("Each fusion type is a **separate object**. The modelled construct that is not a reported "
      "type is registered as one too, because it is what several modules actually compute on.")
    w("")
    w("| object | status | exon level | residue level | provenance |")
    w("|---|---|---|---|---|")
    for o in m["objects"]:
        d = o.get("definition", {}) or {}
        prov = ", ".join(f"`{p}`" for p in d.get("provenance", [])) or "—"
        w(f"| **{_md_escape(o['display_name'])}** (`{o['id']}`) | {o.get('status', '—')} "
          f"| {_md_escape(d.get('exon_level') or '—')} | {_md_escape(d.get('residue_level') or '—')} "
          f"| {prov} |")
    w("")
    if m.get("contested_names"):
        w("### 5a · ⚠ Contested names — a name that maps to more than one object")
        w("")
        w("A name on this list may **not** appear in any object's aliases. That is enforced.")
        w("")
        w("| name | maps to | conflict |")
        w("|---|---|---|")
        for c in m["contested_names"]:
            w(f"| **{_md_escape(c['name'])}** | {', '.join('`' + x + '`' for x in c['maps_to'])} "
              f"| `{c['conflict']}` — {_md_escape(c.get('note', ''))} |")
        w("")

    # ---- evidence ---------------------------------------------------------
    w("## 6 · Evidence — keyed by a canonical identifier, with every name it travels under")
    w("")
    w("This is the table that makes the *Munck / Zaienne* class of error structurally impossible: "
      "a wrong name is registered as a **misattribution of one evidence item**, so both names "
      "resolve to the same source and the checker fails if the wrong one spreads to a new file.")
    w("")
    w("| evidence | canonical id | aliases | ⚠ misattributed as | cited in |")
    w("|---|---|---|---|---|")
    for ev in m["evidence"]:
        canon = ev.get("canonical", {}) or {}
        cid = " · ".join(f"{k.upper()} {v}" for k, v in canon.items() if v) or "⚠ none"
        al = ", ".join(f"`{a}`" for a in ev.get("aliases", [])) or "—"
        mis = ", ".join(f"**`{a}`**" for a in ev.get("misattributed_as", [])) or "—"
        files = ", ".join(sorted({os.path.basename(o["file"]) for o in ev.get("cited_in", [])})) or "—"
        w(f"| `{ev['id']}` {_md_escape(ev['citation'][:110])}… | {cid} | {al} | {mis} | {files} |")
    w("")

    # ---- artifacts --------------------------------------------------------
    w("## 7 · Artifacts — which module writes them, which workflow runs it, which ref they land on")
    w("")
    w("⚠ **The ref matters.** An artifact on the wrong branch is a stale fact that reads as a "
      "current one (CLAUDE.md §7). Claims are checked against **`" + "main" + "`**, "
      "not against the working tree.")
    w("")
    w("| artifact | produced by | workflow | published to | note |")
    w("|---|---|---|---|---|")
    for a in m["artifacts"]:
        w(f"| `{a['id']}` `{a['path']}` | {'`' + a['produced_by'] + '`' if a.get('produced_by') else '—'} "
          f"| {'`' + a['workflow'] + '`' if a.get('workflow') else '—'} "
          f"| {', '.join(a.get('published_to', [])) or '—'} | {_md_escape(a.get('note', ''))} |")
    w("")

    # ---- claims -----------------------------------------------------------
    w("## 8 · Claims — a quoted figure and the one field that is its home")
    w("")
    w("The registry records **where** each figure lives, never the figure. The checker resolves "
      "each field against the artifact **on `" + "main" + "`** and fails if it "
      "is absent, a stub, or missing the field.")
    w("")
    w("| claim | document | what it quotes | its one home |")
    w("|---|---|---|---|")
    for c in m["claims"]:
        w(f"| `{c['id']}` | {_link(c['document'])} | {_md_escape(c['locator'])} "
          f"| `{c['artifact']}` → `{c.get('field', '—')}` |")
    w("")

    # ---- the watch list ---------------------------------------------------
    kinds = closure_model(m)
    trig_by_id = {t["id"]: t for t in m.get("revival_triggers", [])}

    items = [("route", r) for r in routes] + [("instrument", i) for i in m["instruments"]]

    w("## 9 · ⭐ THE WATCH LIST — what would revive what, highest-leverage first")
    w("")
    w("**Why this section is the point of the whole registry.** Many of these paths will be "
      "unblocked, and a register that files *a fact about a sequence* beside *a limitation of "
      "today's free-energy engine* under one word — \"closed\" — has destroyed the only distinction "
      "that decides what to watch for. So `closure_kind` is an enumerated field, and every "
      "non-permanent closure names, in searchable words, what has to land.")
    w("")
    w("⭐ **Ordered by how many routes and instruments each trigger revives** — the top rows are the "
      "highest-leverage advances to watch for. Each `trigger` string is written to be usable "
      "**verbatim as a literature-search query**.")
    w("")
    w("| # revived | trigger | what it would reopen | on the watch list? |")
    w("|---|---|---|---|")
    trig_rows = []
    for t in m.get("revival_triggers", []):
        users = [i["id"] for _, i in items if t["id"] in (i.get("revival_trigger") or [])]
        reopen = t.get("would_reopen", [])
        trig_rows.append((len(set(users) | set(reopen)), t, users, reopen))
    for n, t, users, reopen in sorted(trig_rows, key=lambda x: (-x[0], x[1]["id"])):
        watch = "✅ yes" if t.get("on_watch_list") else "⚠ **no — nobody is scanning for it**"
        w(f"| **{n}** | **{_md_escape(t['trigger'])}** <br>*{_md_escape(t.get('why_this_string', ''))}* "
          f"| {', '.join('`' + x + '`' for x in reopen)} | {watch} |")
    w("")

    w("### 9a · Every closure, by KIND — and which are permanent")
    w("")
    w("⛔ **A `definitional` or `arithmetic_over_fixed_fact` closure is permanent and may carry NO "
      "revival trigger** — a fact about what the objects *are* is not waiting on a method. "
      "⭐ **`instrument_limit` is the most revivable kind and is where most of this program's "
      "failures actually sit.** `permanently closed` below is DERIVED from the kind, never typed.")
    w("")
    for kind, spec in kinds.items():
        rows = [(sec, i) for sec, i in items if i.get("closure_kind") == kind]
        if not rows:
            continue
        perm = "⛔ **PERMANENT — never revivable**" if spec.get("permanent") else "revivable"
        w(f"**`{kind}`** — {perm}. {_md_escape(spec.get('meaning', ''))}")
        w("")
        w("| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |")
        w("|---|---|---|---|---|")
        for sec, i in sorted(rows, key=lambda x: x[1]["id"]):
            trigs = ", ".join(f"`{t}`" for t in (i.get("revival_trigger") or [])) or "—"
            reopen = would_reopen(m, i)
            w(f"| `{i['id']}` {_md_escape(i.get('display_name') or i.get('name', ''))[:70]} "
              f"| {kind} | {'**yes**' if spec.get('permanent') else 'no'} | {trigs} "
              f"| {', '.join('`' + x + '`' for x in reopen) or '—'} |")
        w("")
        for sec, i in sorted(rows, key=lambda x: x[1]["id"]):
            if i.get("closure_note"):
                w(f"- `{i['id']}` — {i['closure_note']}")
        w("")

    # ---- conflicts --------------------------------------------------------
    w("## 10 · OPEN CONFLICTS — logged rather than decided")
    w("")
    w("Each of these is a genuine disagreement in the record that this registry could not resolve "
      "from what is committed. Deciding them is the owning file's call, not a navigation layer's.")
    w("")
    for c in m["open_conflicts"]:
        w(f"### `{c['id']}` · {c['what']}")
        w("")
        w("**Files:** " + ", ".join(f"`{x}`" for x in c["files"]))
        w("")
        for p in c["positions"]:
            w(f"- {p}")
        w("")
        w(f"**Why it is not decided here:** {c['why_not_decided']}")
        w("")
        w(f"**Owner:** {c['owner']}")
        w("")

    w("---")
    w("")
    w("## Limits")
    w("")
    for lim in m["_limits"]:
        w(f"- {lim}")
    w("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def run_checks(m):
    f = Findings()
    for chk in ALL_CHECKS:
        chk(m, f)
    return f


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="run the invariants (default)")
    ap.add_argument("--write-view", action="store_true", help="regenerate emc-systems-map.md")
    ap.add_argument("--map", default=MAP_PATH)
    args = ap.parse_args(argv)

    m = load_map(args.map)

    if args.write_view:
        with open(VIEW_PATH, "w") as fh:
            fh.write(render_view(m))
        print(f"wrote {os.path.relpath(VIEW_PATH, REPO)}")
        if not args.check:
            return 0

    f = run_checks(m)

    # The derived view must not be able to drift from its source.
    rendered = render_view(m)
    try:
        with open(VIEW_PATH) as fh:
            committed = fh.read()
    except OSError:
        committed = None
    if committed is None:
        f.error("V1", f"{os.path.relpath(VIEW_PATH, REPO)} is missing -- regenerate with "
                      f"--write-view")
    elif committed != rendered:
        f.error("V1", f"{os.path.relpath(VIEW_PATH, REPO)} differs from what the registry "
                      f"generates -- it was hand-edited or the registry moved. Regenerate with "
                      f"--write-view; never edit the view")

    for code, msg in f.warnings:
        print(f"WARN  [{code}] {msg}")
    for code, msg in f.errors:
        print(f"ERROR [{code}] {msg}")

    n_items = sum(len(m.get(s, [])) for s in
                  ("routes", "objects", "evidence", "instruments", "artifacts", "claims",
                   "blockers", "open_conflicts"))
    print(f"\nemc_systems_map_check: {n_items} registry items · "
          f"{len(f.errors)} ERROR · {len(f.warnings)} WARN")
    return 1 if f.errors else 0


if __name__ == "__main__":
    sys.exit(main())
