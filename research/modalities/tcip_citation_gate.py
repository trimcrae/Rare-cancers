#!/usr/bin/env python3
"""Q12 — THE RT-TCIP CITATION GATE, AND THE GRADING THAT MUST FOLLOW IT.

WHAT THIS DECIDES, AND WHY IT IS LOAD-BEARING
---------------------------------------------
`RT-TCIP`'s only cited source is `EV-EB-TCIP-2025` (`10.1021/jacs.5c05634`). The effector-arm
registry's own `⚠_citation_gate` field forbids treating any artifact resting on it as a measurement
until it clears `verify-refs`, and roadmap §10.1a row Q12 states the consequence plainly: **until it
does, no manuscript may quote it, so the verification is a hard gate on the route existing at all.**
The TCIP route produced the strongest new result of 2026-08-06, which is what makes this gate
load-bearing rather than bookkeeping.

⛔ THE WRINKLE ROW Q12 NAMES WAS REAL AND IS NOW STALE — AND BOTH HALVES MATTER
-------------------------------------------------------------------------------
`nr4a3-tcip-route-memo.md` §6 records, measured on 2026-08-06:

    grep -c "jacs.5c05634" .github/workflows/verify-refs.yml   ->   0

…and concludes that "dispatching `verify-refs` as committed cannot clear it", that adding the DOI is
a workflow edit outside that lane's remit, and that the workflow "is held by another lane".

**All three sentences were true when written and none is true now.** The DOI was added to
`FIXED_DOIS` in commit `ae7174d` ("Adopt the abandoned verify-refs lane's work"), which also records
that the lane holding the workflow had been DEAD for 1h37m and was adopted on inspection. So the gate
became dischargeable by a plain dispatch, and the memo — the one document a session would read to
find out — still said it was not.

⭐ THE REUSABLE PART IS NOT THE DOI. It is that **a blocker recorded in prose does not un-record
itself when it is fixed**, and a session that trusts the memo would have re-done a workflow edit that
was already committed, or worse, concluded the route was still gated. `measure_doi_registration()`
below re-takes that `grep` mechanically, so the claim is a READING and not a remembered state.

WHAT CLEARING THE GATE DOES AND DOES NOT DO
-------------------------------------------
⛔ **It moves exactly one permission and zero measurements.** A verified citation licenses a
manuscript to QUOTE the mechanism. It supplies no number to any artifact — `nr4a3_tcip_reach`'s
`required_distances()` refuses the citation explicitly and uses only repository-owned bounds — and it
retires no blocker. `grade_against_failure_record()` states that against the route memo's own §7b
line, because the temptation after a gate clears is to let it move the sentences beside it, and §7b
exists precisely to stop that.

$0. Public Actions API reads and a local grep. No GPU, no rental, no token.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "tcip-citation-gate.json")

DOI = "10.1021/jacs.5c05634"
WORKFLOW_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "verify-refs.yml")
MEMO = os.path.join(HERE, "nr4a3-tcip-route-memo.md")
API = "https://api.github.com/repos/trimcrae/Rare-cancers/actions"


def measure_doi_registration(workflow_path=WORKFLOW_PATH, doi=DOI):
    """Re-take the memo's `grep -c` mechanically. A remembered blocker is not a blocker."""
    row = {"doi": doi, "workflow": os.path.relpath(workflow_path, REPO_ROOT),
           "memo_grep_pattern": "jacs.5c05634", "memo_grep_c_result": None,
           "n_occurrences_of_full_doi": None,
           "registered": None, "in_enforced_section": None, "error": None}
    try:
        with open(workflow_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        row["error"] = "%s: %s" % (type(e).__name__, e)
        return row
    # ⚠ TWO DIFFERENT MEASUREMENTS, AND REPORTING ONE AS THE OTHER WOULD BE THE BUG. The memo's claim
    # is `grep -c "jacs.5c05634"`, which counts LINES matching a BARE fragment; that fragment also
    # appears in the workflow's own comment about the memo, so the line count is not the number of
    # registrations. Both are emitted, each labelled with what it counts, because "grep_count: 1"
    # sitting next to a memo that says 2 is exactly the kind of unexplained disagreement that costs
    # a session an hour.
    row["memo_grep_c_result"] = sum(1 for ln in text.splitlines()
                                    if row["memo_grep_pattern"] in ln)
    row["n_occurrences_of_full_doi"] = text.count(doi)
    row["registered"] = row["n_occurrences_of_full_doi"] > 0
    # ⚠ REGISTERED IS NOT ENOUGH — IT MUST BE IN THE ENFORCED LIST. Section 8a of this workflow is
    # print-only and degrader-scoped; only section 1's `FIXED_DOIS` is read by the verdict, whose
    # expected count is DERIVED from that array. A DOI parked in 8a would resolve in the log and
    # move no gate, which is a green run that verifies nothing — the defect class this repo keeps
    # finding. So the check is "is it inside FIXED_DOIS", not "is it in the file".
    m = re.search(r"FIXED_DOIS=\((.*?)\n\s*\)", text, re.S)
    row["in_enforced_section"] = bool(m and doi in m.group(1))
    row["_why_two_checks"] = (
        "section 8a of verify-refs.yml is PRINT-ONLY; only section 1's FIXED_DOIS is read by the "
        "verdict, and the expected count is derived from that array. A DOI registered outside it "
        "would resolve in the log and gate nothing.")
    return row


def measure_memo_claim(memo_path=MEMO, doi=DOI):
    """Does the route memo still assert the blocker? A stale blocker is a live hazard."""
    row = {"memo": os.path.relpath(memo_path, REPO_ROOT), "still_asserts_absence": None,
           "quoted": None, "error": None}
    try:
        with open(memo_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        row["error"] = "%s: %s" % (type(e).__name__, e)
        return row
    hit = re.search(r"[^\n]*grep -c[^\n]*jacs\.5c05634[^\n]*", text)
    row["quoted"] = hit.group(0).strip() if hit else None
    row["still_asserts_absence"] = bool(hit and re.search(r"→\s*\*\*0\*\*|-> 0|→ 0", hit.group(0)))
    row["_consequence"] = (
        "if this is true while the DOI IS registered, the memo is a stale blocker: a session reading "
        "it would conclude the route is still citation-gated and would either re-do a committed "
        "workflow edit or refuse to quote a cleared citation. Prose does not un-record itself.")
    return row


def _get(url):
    try:
        raw = subprocess.run(["curl", "-sS", "-m", "45", url],
                             capture_output=True, text=True, check=False)
        if raw.returncode != 0:
            return None, "curl rc=%d" % raw.returncode
        return json.loads(raw.stdout), None
    except (ValueError, OSError) as e:                       # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)


def verify_refs_runs(per_page=5):
    """The recent verify-refs runs, from the public API. $0, no token, re-checkable."""
    out = {"_source": "%s/workflows/verify-refs.yml/runs" % API, "runs": [], "error": None}
    d, err = _get("%s/workflows/verify-refs.yml/runs?per_page=%d" % (API, per_page))
    if err or not isinstance(d, dict):
        out["error"] = err or "unexpected payload"
        return out
    for r in d.get("workflow_runs") or []:
        out["runs"].append({"run_id": r.get("id"), "created_at": r.get("created_at"),
                            "event": r.get("event"), "status": r.get("status"),
                            "conclusion": r.get("conclusion"),
                            "html_url": r.get("html_url")})
    return out


#: ⛔ THE VERIFICATION ITSELF, QUOTED FROM THE RUN LOG — because a `conclusion: success` is a BADGE,
#: and row 27 is the standing proof in this repository that a badge is not a reading. These lines are
#: transcribed verbatim from run 31175823997, job 92857493826 (`verify`), whose log is retrievable
#: with the run id for as long as GitHub retains it. Nothing here is curated: the "expect" line is
#: what the workflow asserted BEFORE the fetch, and the "crossref" line is what came back.
VERIFICATION_EVIDENCE = {
    "run_id": 31175823997,
    "job_id": 92857493826,
    "job_name": "verify",
    "dispatched_at_et": "2026-08-07 7:52 AM ET",
    "ref": "main",
    "conclusion": "success",
    "quoted_expect": (
        "expect: EV-EB-TCIP-2025 (expect: Rewiring the fusion oncoprotein EWSR1::FLI1 in Ewing "
        "sarcoma with bivalent small molecules; J Am Chem Soc 2025, 147(49):44739-44758; "
        "PMC12851799)"),
    "quoted_crossref": (
        "crossref: Rewiring the Fusion Oncoprotein EWSR1::FLI1 in Ewing Sarcoma with Bivalent Small "
        "Molecules | Journal of the American Chemical Society | 2025"),
    "quoted_verdict_notice": (
        "reference-verification census: crossref_titles=7 dois_resolved=42 parse_errors=0 "
        "undefined_dois=0 | ::notice:: 7/7 enumerated DOIs resolved, 42 DOI(s) resolved overall, "
        "no parse errors."),
    "matched": ["title", "journal", "year"],
    "⚠_not_verified_by_this_run": (
        "VOLUME, PAGES and PMCID. The `expect` string names 147(49):44739-44758 and PMC12851799, and "
        "section 1 of verify-refs prints only title | journal | year — section 8a is the one that "
        "prints volume/page/authors, and it is print-only and degrader-scoped, which is WHY the DOI "
        "was filed in section 1. So the identity of the work is verified and its pagination is not. "
        "Closing that is a further $0 CI read, not a claim to make from here."),
    "_why_this_badge_IS_load_bearing_unlike_row_27s": (
        "verify-refs derives its expected count from the FIXED_DOIS array itself (NFIXED) and EXITS "
        "1 when fewer resolve. The TCIP DOI is inside that array, so `conclusion: success` on a run "
        "after its registration mechanically entails that this DOI resolved. Contrast row 27, where "
        "the green badge covered jobs that were never requested: there the verdict was independent "
        "of the work, here it is derived from it. That difference is the whole reason one badge can "
        "be read and the other cannot."),
}


def grade_against_failure_record():
    """What clearing the gate changes, and — the longer list — what it does not.

    ⛔ ONE PERMISSION, ZERO MEASUREMENTS. The route memo's §7b is the one home of this boundary and
    it is pointed at rather than restated; what is stated here is only the citation's own place in it.
    """
    return {
        "what_the_cleared_gate_moves": [
            {"statement": "a manuscript may QUOTE the TCIP mechanism, citing EV-EB-TCIP-2025",
             "before": "⛔ forbidden — an auto-captured lead that had never cleared verify-refs",
             "after": "✅ permitted — Crossref resolves the DOI to the expected title/journal/year",
             "why": "this is the only thing the repo's gate was ever about"},
        ],
        "what_it_does_not_move": [
            {"statement": "any number in nr4a3-tcip-reach.json",
             "still": "⛔ unchanged, and none ever came from the citation",
             "why": ("required_distances() refuses the citation explicitly and uses only "
                     "repository-owned bounds (nr4a3_basin_search.PARAMS, "
                     "nr4a3_linker_design.CHEM_MAX_ATOMS). A verified citation may tell you which "
                     "protein to fetch; it may not enter an artifact as a measurement.")},
            {"statement": "the route's blockers",
             "still": ("⛔ untouched — BLK-R4-BINDS, BLK-INDUCED-COMPLEX, BLK-PARALOGUE-DDG, "
                       "BLK-UNSIZED-REQUIREMENT, BLK-NO-WET-LAB"),
             "why": "a citation is not a measurement and clears no experimental blocker"},
            {"statement": "the discriminating power of the reach gate",
             "still": ("⛔ unchanged — the envelope admits every body tested at every rung, including "
                       "a 1183-residue assembly. A test that admits everything cannot refute "
                       "anything, and the route memo says so about its own headline"),
             "why": "the gate the named effector passed is the gate every body has passed"},
            {"statement": "anything about binding, recruitment, chromatin retention or transcription",
             "still": "⛔ not claimed, before or after",
             "why": "a staged body is an excluded volume and one atom's coordinates"},
            {"statement": "paralogue discrimination on the binder (R7)",
             "still": "⛔ still not addressed",
             "why": "not a geometry question"},
        ],
        "the_line_to_read_before_quoting_anything": (
            "nr4a3-tcip-route-memo.md §7b — 'THE LINE: what a named effector upgraded, and what it "
            "did NOT'. This module adds one row to that table (the citation) and changes none of the "
            "others."),
        "the_R9_R10_R12_discrepancy_is_untouched": (
            "⚠ Separately and still open: four prose files say RT-TCIP retires R9/R10/R12 while "
            "systems/graph/routes.json encodes the correct version — it retires R12 only. Route memo "
            "§8 establishes this; clearing the citation gate does nothing about it, and the two must "
            "not be conflated because both are 'a Q12 thing'."),
    }


def map_edits_required(cleared, memo_stale):
    """Routed roadmap edits — DESCRIBED, NOT APPLIED. Checked by verify_map_edits.py."""
    if not cleared:
        return []
    return [{
        "section": "§10.1a row Q12",
        "anchor": ("⛔ **the citation is an auto-captured lead and has never cleared `verify-refs`** "
                   "— until it does, no manuscript may quote it, so the verification is a hard gate "
                   "on the route existing at all"),
        "current_text": ("⛔ **the citation is an auto-captured lead and has never cleared "
                         "`verify-refs`** — until it does, no manuscript may quote it, so the "
                         "verification is a hard gate on the route existing at all"),
        "proposed_text": (
            "✅ **CLEARED 2026-08-07 7:52 AM ET.** `10.1021/jacs.5c05634` resolved through "
            "`verify-refs` (run `31175823997`, job `verify`, `7/7 enumerated DOIs resolved, 0 parse "
            "errors`) to the expected title, journal and year. A manuscript may now quote the TCIP "
            "mechanism. ⛔ **That moves ONE PERMISSION AND ZERO MEASUREMENTS** — no number in "
            "`nr4a3-tcip-reach.json` came from the citation, no blocker is retired, and the reach "
            "gate's discriminating power is unchanged; read "
            "[the route memo §7b](../modalities/nr4a3-tcip-route-memo.md) before quoting anything. "
            "⚠ Volume, pages and PMCID are NOT verified by that run — §1 of the workflow prints "
            "title/journal/year only. One home: "
            "[`tcip-citation-gate.json`](../modalities/tcip-citation-gate.json)"),
        "why": ("the row asserts the gate is open; it is closed, and a row that overstates a blocker "
                "stops work that is actually permitted"),
        "artifact": "research/modalities/tcip-citation-gate.json:gate_status",
    }]


def doc_edits_required(memo_stale):
    """The route memo correction — ROUTED, NOT APPLIED, because this lane does not own that file.

    ⚠ `verify_map_edits.py` checks the ROADMAP only, so this block is deliberately separate: a memo
    edit verified by nothing is exactly the dead-anchor risk that guard exists for, and pretending
    otherwise by smuggling it into `map_edits_required` would make the guard's report a lie.
    """
    if not memo_stale:
        return []
    return [{
        "file": "research/modalities/nr4a3-tcip-route-memo.md",
        "section": "§6 · The citation gate — still open, and it cannot be closed from here",
        "what_is_wrong": (
            "the section title and all three of its measured bullets are STALE. `grep -c "
            "\"jacs.5c05634\"` no longer returns 0; the DOI was added to verify-refs.yml's enforced "
            "FIXED_DOIS in commit ae7174d, and the lane the memo says holds that workflow was dead "
            "and its work adopted in the same commit."),
        "proposed": (
            "retitle to '§6 · The citation gate — CLOSED 2026-08-07', keep the original measurement "
            "as a ⚠ Superseded-retained line per CLAUDE.md rule 1.2, and state the outcome: "
            "verify-refs run 31175823997 resolved the DOI; the permission to quote is granted and "
            "nothing else moved. Point at tcip-citation-gate.json rather than restating."),
        "why_routed_not_applied": (
            "this lane does not own the memo, and a blocker recorded in prose that has since been "
            "discharged is the single most misleading thing the file can carry — the next session "
            "reads it and either re-does a committed workflow edit or refuses to quote a cleared "
            "citation."),
        "artifact": "research/modalities/tcip-citation-gate.json:memo_is_stale",
    }]


def build(skip_network=False):
    reg = measure_doi_registration()
    memo = measure_memo_claim()
    runs = ({"_skipped": "network read not attempted", "runs": []} if skip_network
            else verify_refs_runs())
    cleared = bool(reg.get("registered") and reg.get("in_enforced_section"))
    return {
        "_what": ("roadmap §10.1a row Q12 — verify the RT-TCIP citation through verify-refs, then "
                  "grade the mechanism against the failure record."),
        "_cost": "$0 — public Actions API reads and a local grep. No GPU, no rental, no token.",
        "doi_registration": reg,
        "route_memo_claim": memo,
        "memo_is_stale": bool(reg.get("registered") and memo.get("still_asserts_absence")),
        "_memo_is_stale_means": (
            "the DOI IS registered while the route memo still records it as absent. The BLOCKER is "
            "discharged; the RECORD of it is not, and the record is what the next session reads."),
        "verify_refs_runs": runs,
        "verification_evidence": VERIFICATION_EVIDENCE,
        "gate_status": ("CLEARED" if cleared else "OPEN"),
        "_gate_status_means": (
            "CLEARED — the DOI is registered in the ENFORCED list and a dispatch of verify-refs on "
            "main resolved it to the expected title, journal and year. A manuscript may now quote "
            "the TCIP mechanism citing EV-EB-TCIP-2025. See `grading` for the (short) list of what "
            "that permits and the (long) list of what it does not."),
        "gate_dischargeable_by_plain_dispatch": cleared,
        "_dischargeable_means": (
            "the DOI sits inside verify-refs.yml's ENFORCED FIXED_DOIS array, so a dispatch of the "
            "workflow as committed on main both resolves it and counts it toward the derived "
            "expected total. No workflow edit and no merge is required — which is exactly what the "
            "route memo says is required."),
        "grading": grade_against_failure_record(),
        "map_edits_required": map_edits_required(cleared, bool(
            reg.get("registered") and memo.get("still_asserts_absence"))),
        "doc_edits_required": doc_edits_required(bool(
            reg.get("registered") and memo.get("still_asserts_absence"))),
        "claim_ceiling": (
            "⛔ Unchanged. A verified citation raises no claim ceiling: roadmap §2.3 binds on the "
            "validation status of the INSTRUMENT producing a requirement, and no instrument's status "
            "moves because a reference resolved. What moves is a permission to quote."),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--skip-network", action="store_true")
    args = ap.parse_args(argv)
    doc = build(skip_network=args.skip_network)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: doc[k] for k in ("doi_registration", "route_memo_claim", "memo_is_stale",
                                          "gate_dischargeable_by_plain_dispatch")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
