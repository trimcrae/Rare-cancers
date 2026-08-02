#!/usr/bin/env python3
"""Where does every lane's starting geometry COME FROM, and has it ever been compared to anything? ($0 CPU)

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ WHY THIS EXISTS: THE PROGRAM VALIDATED ITS STATISTICS AND NEVER VALIDATED ITS INPUTS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
The sensitivity control's co-folds were measured (2026-08-02, two independent instruments agreeing) at
DockQ **0.023-0.046** on the target↔VHL interface with **fnat 0.000** — while reproducing the internal
VHL/EloB/EloC machinery at DockQ 0.89-0.97. The panel simulated something that was not the complex whose
selectivity was measured, and nobody knew, because **no lane in this repo had ever scored its starting
structures against a reference.** The pair had even been CHOSEN to make that possible (`selcal_panel`:
*"each arm's co-fold can be VALIDATED against a real structure of the very complex it models"*) and the
check was never implemented.

Enormous care went into preregistration, exact permutation reference sets, blinding, LOMO, registered MDEs
and claim ceilings — all downstream of a structure nobody had looked at. This module is the missing
inventory: for every lane that stages geometry for GPU work, **what class of object is the input, is a
reference even possible, and has anyone checked.**

⛔ IT SCORES NOTHING AND GATES NOTHING. It is an inventory, not a verdict: it re-scores no leg, moves no
threshold, amends no preregistration and blocks no launch. What it produces is the list of places the
selcal defect could be hiding, ranked by whether anyone could tell.

★ EVERY CLAIM CARRIES QUOTED EVIDENCE FROM THE SOURCE, AND THE QUOTE IS VERIFIED AT RUNTIME. A census
assembled from memory is exactly the artifact this program keeps getting burned by — a plausible record is
more dangerous than an empty one (CLAUDE.md §4b). So each row names a file and a substring, `_verify()`
reads the file and confirms the substring is really there, and a row whose evidence no longer matches is
emitted as `EVIDENCE_STALE` rather than as a fact. If a lane is refactored, this census breaks loudly
instead of quietly describing a repo that no longer exists.

Pure stdlib. No network, no S3, no GPU.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "structural-provenance-census.json")

#: Source classes, worst-to-best for "could a wrong input hide here".
#:   PREDICTED    — a co-fold / generative model. Nothing anchors it to reality; the selcal defect's home.
#:   SUBSTITUTED  — a real crystal frame with a different sequence threaded into it. The frame is real, the
#:                  arm is not, and an interface inherited from the donor complex is an assumption.
#:   COMPOSED     — assembled from two or more real structures. Real atoms, invented relative placement.
#:   DEPOSITED    — coordinates straight from the PDB. Nothing to validate; it IS the reference.
#:   DERIVED      — built from an already-staged structure by a local edit (mutation, protonation).
CLASS_PREDICTED = "PREDICTED (co-fold / generative)"
CLASS_SUBSTITUTED = "SUBSTITUTED (real frame, modelled sequence)"
CLASS_COMPOSED = "COMPOSED (real parts, modelled placement)"
CLASS_DEPOSITED = "DEPOSITED (crystal coordinates)"
CLASS_DERIVED = "DERIVED (local edit of a staged structure)"

#: One row per lane that stages geometry a GPU then integrates. `evidence` is (file, substring) and is READ,
#: never trusted. `validated_by` names the artifact holding a comparison against a reference, or None.
LANES = [
    {
        "lane": "selcal (SMARCA2/4 sensitivity control)",
        "stager": "selcal_stage.py",
        "source_class": CLASS_PREDICTED,
        "evidence": ("selcal_stage.py",
                     "the deposited ternaries are used to VALIDATE the\nco-folds rather than to supply them"),
        "reference_available": ["9DTY", "9DTX"],
        "validated_by": ["selcal-cofold-vs-crystal.json", "selcal-cofold-dockq.json"],
        "finding": "MEASURED 2026-08-02, two independent instruments agreeing: target↔VHL DockQ 0.023-0.046, "
                   "fnat 0.000, while the internal VHL/EloB/EloC interfaces score 0.89-0.97. The co-folds "
                   "reproduce the E3 machinery and not the complex under test.",
        "could_a_wrong_input_hide_here": "NO LONGER — this is the lane the defect was found in.",
    },
    {
        "lane": "valB / ternary calibration (cooperativity)",
        "stager": "ternary_pdb_stage.py",
        "source_class": CLASS_DEPOSITED,
        "evidence": ("ternary_pdb_stage.py", "every atom is from 6HAX (RCSB); nothing is fabricated"),
        "reference_available": ["6HAX", "8G1Q"],
        "validated_by": None,
        "finding": "Coordinates come straight from the crystal, so valB's wrong-sign result is NOT an "
                   "input-quality artifact of the kind found in selcal and stands as measured. The two "
                   "failed controls have DIFFERENT causes.",
        "could_a_wrong_input_hide_here": "NO for the deposited chains — they are the reference. See the "
                                         "SMARCA2 arm row below, which is a different object.",
    },
    {
        "lane": "valB — the SMARCA2 arm specifically",
        "stager": "smarca2_model.py",
        "source_class": CLASS_SUBSTITUTED,
        "evidence": ("smarca2_model.py",
                     "Build a relaxed SMARCA2 bromodomain model from the 8G1Q SMARCA4 bromodomain"),
        "reference_available": ["9DTY", "6HAX", "6HAY", "7S4E"],
        "validated_by": None,
        "finding": "★ THE ONE LIVE CASE. SMARCA2 is threaded into a 3.73 Å SMARCA4 ternary frame, so its "
                   "ternary INTERFACE is inherited from the donor complex rather than observed. Deposited "
                   "SMARCA2 ternaries exist, so this is checkable — and has not been checked.",
        "could_a_wrong_input_hide_here": "YES — and a reference exists, so it is answerable for $0.",
        "confound_if_scored": "8G1Q carries Wurz compound 1 and 9DTY carries PRT3789, so a measured interface "
                              "difference conflates PARALOGUE, LIGAND and RESOLUTION (3.73 Å vs 3.19 Å). It "
                              "bounds model fidelity; it does not cleanly measure it, and must be reported "
                              "that way. 6HAX is the better comparator — a SMARCA2 ternary the lane already "
                              "stages from — because it removes the paralogue term.",
    },
    {
        "lane": "NR-V04 retrospective (Arm E)",
        "stager": "nrv04_ternary.py + nrv04_covalent_stage.py",
        "source_class": CLASS_PREDICTED,
        # ⚠ THIS QUOTE WAS WRONG ON THE FIRST PASS AND THE VERIFIER CAUGHT IT. I had quoted the PREREG's
        # wording ("no solved NR-V04 ternary structure") against the BENCHMARK json, which does not contain
        # it — the row rendered EVIDENCE_STALE instead of as a fact. That is the whole point of reading the
        # quote back rather than trusting it.
        "evidence": ("nrv04-ternary-benchmark.json", "no solved ternary structure"),
        "reference_available": [],
        "validated_by": None,
        "finding": "⛔ NO DEPOSITED NR-V04 TERNARY EXISTS, so no crystal comparison is possible and none may "
                   "be manufactured. The honest analogue already measured is internal consistency with the "
                   "lane's own assumed mechanism: celastrol C6 sits 28.42-39.11 Å from Cys551 across every "
                   "clean model, against an 8.0 Å limit — a REFUSAL, not a score.",
        "could_a_wrong_input_hide_here": "YES, AND IT IS UNFALSIFIABLE BY THIS METHOD. Same generator and "
                                         "same E3 as selcal, where the co-folds were measured wrong; but "
                                         "with no reference, 'unchecked' here can never become 'checked'.",
    },
    {
        "lane": "5a-KS (CRBN ternary FEP)",
        "stager": "nr4a3_5aks_stage.py",
        "source_class": CLASS_PREDICTED,
        "evidence": ("nr4a3_5aks_stage.py", "turn the two co-folded ternaries into the FEP engine"),
        "reference_available": [],
        "validated_by": None,
        "finding": "Co-folded CRBN ternaries of NR4A3 and NR4A1. No deposited NR4A-CRBN ternary exists, so "
                   "the same unfalsifiability applies as for NR-V04.",
        "could_a_wrong_input_hide_here": "YES, and no reference exists to settle it. ⚠ A CRBN co-fold is "
                                         "additionally the arm DeepTernary's own qualification found WEAKEST "
                                         "(6BOY failed at DockQ 0.06/0.15 while its VHL cases reached "
                                         "0.62-0.83), so this is the least-supported generator on the "
                                         "least-checkable lane.",
    },
    {
        "lane": "E3 recruiter staging",
        "stager": "nr4a3_e3_stage.py",
        "source_class": CLASS_COMPOSED,
        "evidence": ("nr4a3_e3_stage.py", "bridge"),
        "reference_available": [],
        "validated_by": "an internal known-answer check inside the module itself",
        "finding": "Composes an E3 body, a ligand exit vector and a RING domain from SEPARATE RCSB entries, "
                   "with a bridge-RMSD refusal. Real atoms, modelled relative placement — but it is the one "
                   "lane that already carries its own known-answer check on its own composition.",
        "could_a_wrong_input_hide_here": "PARTLY GUARDED — alone among these lanes it checks itself.",
    },
    {
        "lane": "step-1 fan-out (cmpd19 congeneric RBFE)",
        "stager": "congeneric_pose_stage.py",
        "source_class": CLASS_DERIVED,
        "evidence": ("congeneric_pose_stage.py", "COMMON-MODE assumption"),
        "reference_available": [],
        "validated_by": None,
        "finding": "NOT A TERNARY LANE and not the same risk: it stages BINARY ligand poses onto a shared "
                   "scaffold so an RBFE edge's common mode holds geometrically. Its exposure is the assumed "
                   "cmpd19 binding mode, which the paper already carries as an explicit double conditionality "
                   "— a declared assumption, not an unexamined input.",
        "could_a_wrong_input_hide_here": "DIFFERENT RISK, ALREADY DECLARED.",
    },
]


def _verify(row):
    """Read the file and confirm the quoted evidence is really there. Returns (ok, detail).

    Whitespace is normalised before matching so a re-wrapped comment does not read as a deleted one — the
    census must break on a lane that CHANGED, not on one that was reflowed."""
    fn, needle = row["evidence"]
    path = os.path.join(HERE, fn)
    if not os.path.exists(path):
        return False, "file absent: %s" % fn
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except Exception as e:                                  # noqa: BLE001
        return False, "unreadable: %s" % e
    norm = " ".join(text.split())
    if " ".join(needle.split()) in norm:
        return True, "quote found in %s" % fn
    return False, ("quote NOT found in %s — the lane may have been refactored; this row is EVIDENCE_STALE "
                   "and must be re-derived from the source, not trusted" % fn)


def build():
    rows, stale = [], 0
    for row in LANES:
        ok, detail = _verify(row)
        r = {k: v for k, v in row.items() if k != "evidence"}
        r["evidence_file"] = row["evidence"][0]
        r["evidence_quote"] = " ".join(row["evidence"][1].split())
        r["evidence_verified"] = ok
        r["evidence_detail"] = detail
        if not ok:
            r["status"] = "EVIDENCE_STALE"
            stale += 1
        rows.append(r)

    checkable = [r for r in rows if r.get("reference_available") and not r.get("validated_by")]
    unfalsifiable = [r for r in rows if not r.get("reference_available") and r["source_class"].startswith("PRED")]
    return {
        "_what": "Where every lane's starting geometry comes from, and whether it has ever been compared to "
                 "a reference. AN INVENTORY, NOT A VERDICT.",
        "_why": "The selcal co-folds were measured at DockQ 0.023-0.046 / fnat 0.000 on the interface under "
                "test by two independent instruments, and nobody knew, because no lane in this repo had ever "
                "scored its starting structures against anything. This is the list of places the same defect "
                "could still be hiding.",
        "_licenses": "NOTHING. It scores nothing, gates nothing, re-scores no leg and blocks no launch.",
        "_evidence_is_verified_not_remembered": "every row names a file and a quote, and the quote is read "
                                                "back from that file at build time; a row whose quote no "
                                                "longer matches is emitted as EVIDENCE_STALE rather than as "
                                                "a fact",
        "source_classes": {
            "PREDICTED": "a co-fold or generative model — nothing anchors it to reality",
            "SUBSTITUTED": "a real crystal frame with a different sequence threaded in — the frame is real, "
                           "the arm is not, and an inherited interface is an assumption",
            "COMPOSED": "assembled from two or more real structures — real atoms, modelled placement",
            "DEPOSITED": "crystal coordinates — nothing to validate, it IS the reference",
            "DERIVED": "a local edit of an already-staged structure",
        },
        "lanes": rows,
        "n_lanes": len(rows),
        "n_evidence_stale": stale,
        "checkable_but_unchecked": [r["lane"] for r in checkable],
        "unfalsifiable_by_this_method": [r["lane"] for r in unfalsifiable],
        "_the_uncomfortable_row": ("Two lanes stage PREDICTED ternaries with NO deposited reference at all "
                                   "(NR-V04, 5a-KS). For those, 'unchecked' can never become 'checked' by "
                                   "this method — the selcal result raises the prior that they are wrong and "
                                   "supplies no way to find out. That is a limit to state, not to solve."),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Structural-provenance census ($0, pure stdlib, no network).")
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)
    doc = build()
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1)
    print("[provenance] wrote %s — %d lanes, %d evidence-stale\n" % (args.out, doc["n_lanes"],
                                                                     doc["n_evidence_stale"]), flush=True)
    hdr = "%-42s %-38s %-12s %s" % ("LANE", "SOURCE CLASS", "REFERENCE", "CHECKED?")
    print(hdr, flush=True)
    print("-" * len(hdr), flush=True)
    for r in doc["lanes"]:
        refs = ",".join(r["reference_available"]) if r["reference_available"] else "— none exists"
        checked = "yes" if r["validated_by"] else "NO"
        print("%-42s %-38s %-12s %s%s" % (r["lane"][:42], r["source_class"][:38], refs[:12], checked,
                                          "" if r["evidence_verified"] else "   ⚠ EVIDENCE_STALE"), flush=True)
    print("\nCHECKABLE BUT UNCHECKED: %s" % (doc["checkable_but_unchecked"] or "none"), flush=True)
    print("UNFALSIFIABLE BY THIS METHOD: %s" % (doc["unfalsifiable_by_this_method"] or "none"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
