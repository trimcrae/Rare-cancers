#!/usr/bin/env python3
"""THE POSE-CONDITIONALITY CENSUS — discharge the debt the `R5` falsifier created.

★★ WHY THIS EXISTS. `path-family-synthesis.md` §2 Tier-1 row 2 pre-registered a falsifier in writing:

    "independent methods disagree as widely as the six existing poses ⇒ 'the predicted pose' is not an
     object this program is entitled to, and every pose-conditional row above must be restated as
     marginalised-over-poses."

On 2026-08-06 that falsifier FIRED (`pose-second-method.json` → `verdict`). A pre-registered consequence
that fires and is then not carried out is worse than no pre-registration at all: it converts a discipline
into a decoration. This module is the carrying-out, and its output is the ONE HOME of the answer to
"which claims were conditional on a singular pose, and what does each become?"

⛔ THREE RULES THIS FILE OBEYS, EACH FOR A MEASURED REASON:

1. **NO NUMBER IS TYPED.** Every figure below is READ from a committed artifact by key path, or MEASURED
   off the committed coordinate files. The claim rows are authorship — the analysis — but their figures
   are not, so a re-run cannot leave a stale number behind (CLAUDE.md §1 rule 1).

2. **A MARGINALISATION IS NEVER INVENTED.** Where a quantity was computed on exactly one pose and the
   evidence to spread it over the census does not exist, the grade is `NOT-MARGINALISABLE` and the
   restated form says so in those words. "Computed on a single pose; not marginalisable without a re-run"
   is the honest answer and it is the right one — a fabricated spread would be worse than the original
   over-claim, because it would look like it had been checked.

3. **THE ALREADY-WORKED CASE IS THE TEMPLATE, NOT A COMPETITOR.** `steric-carrier-audit.json` graded one
   claim across all six poses and found the WEAK form pose-robust and the VECTOR-SPECIFIC form not. That
   grading shape is imported here verbatim rather than re-derived, and nothing in this file may contradict
   it.

⚠ AND THE HALF EVERYONE WILL FORGET, so it is stated at the top of the artifact as well as here: the
second method **also brought no known-answer calibration**. Part B returned `n_gradeable: 0` — and that is
an UNRUN arm, not a measured absence of recovery (CLAUDE.md §4: an absent reading is not a reading of
absence). The per-pair `_status` records why, and this module reads that status rather than reporting the
zero on its own.

$0 — pure stdlib, CPU. Nothing here is a claim about binding, affinity, degradation, selectivity, efficacy
or safety, and no molecule named here is a hit.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]
MOD = REPO / "research" / "modalities"
MAN = REPO / "research" / "manuscripts"

OUT = MOD / "pose-conditionality-census.json"
MAP_EDITS_OUT = MAN / "pose-conditionality-map-edits.json"

LIGAND = "denovo_401"

# ── the grade vocabulary ────────────────────────────────────────────────────────────────────────────
# Four grades, and the boundary between the middle two is the whole point of the exercise: a claim that
# has been LOOKED AT across poses is a different object from one that has not, even when both are
# uncomfortable.
GRADES = {
    "POSE-ROBUST": (
        "evaluated on TWO OR MORE of the committed poses and it holds on all of them. The claim survives "
        "the marginalisation and may be stated — at the strength the spread supports, never stronger."
    ),
    "POSE-DEPENDENT": (
        "evaluated on two or more committed poses and THE ANSWER CHANGES between them. ⛔ The claim may "
        "not be stated in its singular form at all; what may be stated is the distribution over poses."
    ),
    "NOT-MARGINALISABLE": (
        "computed on exactly ONE pose, and spreading it over the census needs compute that has not been "
        "spent. ⛔ This is an honest terminal grade, not a to-do: the claim stands as "
        "'computed on a single docked pose; not marginalisable without a re-run', and the re-run is named."
    ),
    "ALREADY-MARGINALISED": (
        "never rested on a singular pose in the first place — it was computed over a pose ensemble, or "
        "over a receptor-derived quantity that no ligand pose enters. ⭑ These rows are the template the "
        "rest of the program should have followed, and listing them is how a reader can tell that the "
        "blast radius was bounded by measurement rather than by assertion."
    ),
}


def load(rel: str) -> dict:
    return json.loads((REPO / rel).read_text())


def dig(doc, dotted, default=None):
    """Read a value by key path. Raises on a missing intermediate so a renamed field is LOUD.

    ⚠ A LIST is accepted as well as a dotted string, because real artifact keys contain dots
    (`n_pairs_within_2.0A`) and a splitter that assumed otherwise silently pointed at nothing.
    """
    parts = dotted if isinstance(dotted, (list, tuple)) else dotted.split(".")
    cur = doc
    for part in parts:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            if part not in cur:
                if default is not None:
                    return default
                raise KeyError(f"{dotted!r}: {part!r} is not in the artifact — the field moved, fix the read")
            cur = cur[part]
    return cur


# ── measured, not assumed: what coordinates does the repository actually hold? ───────────────────────
def committed_pose_inventory() -> dict:
    """Count the committed poses of the ligand, by engine, off the real files.

    ⚠ This is the check that turned a memory into a measurement: the paper's §2.7 selection margin was
    computed in the unbiased RELEASE frame, and NO release-frame pose of this ligand is committed
    anywhere — `results/PROVENANCE.md` records its S3 prefix as LOST. So the headline selection number
    cannot be re-marginalised over the census even in principle, because its own pose is not in it.
    """
    # ⛔ EVERY COUNT BELOW IS COUNTED, NEVER DEFAULTED. An earlier draft of this function carried an
    #    `or 1` fallback for the re-dock files; it happened to be right, and that is exactly the shape
    #    CLAUDE.md §4(b) warns about — a populated field is not a measured one. A file that does not
    #    contain the ligand is reported with the count it actually has, which is zero.
    rec = re.compile(rf"(?m)^{re.escape(LIGAND)}\s*$")

    def count(path: pathlib.Path) -> dict:
        body = path.read_text(errors="ignore")
        return {
            "file": str(path.relative_to(REPO)),
            "n_ligand_title_records": len(rec.findall(body)),
            "n_sdf_records": sum(1 for ln in body.splitlines() if ln.strip() == "$$$$"),
        }

    smina, rdock = [], []
    for sdf in sorted((REPO / "results").rglob("docked_nr4a3.sdf")):
        row = count(sdf)
        if row["n_ligand_title_records"]:
            smina.append(dict(row, engine="smina"))
    for sdf in sorted((MOD / "_pose_convergence_inputs").glob("docked_nr4a3_*.sdf")):
        smina.append(dict(count(sdf), engine="smina"))
    for sd in sorted((MOD / "_pose_second_method_poses").glob("cross_dock_*.sd")):
        rdock.append(dict(count(sd), engine="rDock"))

    prov = (REPO / "results" / "PROVENANCE.md").read_text(errors="ignore")
    lost_rows = [ln.strip() for ln in prov.splitlines() if "**LOST**" in ln and "nr4a3-matrix" in ln]
    return {
        "_asks": "how many poses of the carried candidate does this repository actually hold, and where?",
        "_measured_from": "the committed coordinate files themselves, not from any artifact's summary",
        "first_method_smina": smina,
        "second_method_rdock": rdock,
        "n_first_method_pose_files": len(smina),
        "n_second_method_pose_files": len(rdock),
        "n_first_method_poses_of_the_ligand": sum(r["n_ligand_title_records"] for r in smina),
        "n_second_method_poses_on_disk": sum(r["n_sdf_records"] for r in rdock),
        "⭑_a_pose_ensemble_ALREADY_EXISTS_ON_DISK_AND_HAS_NEVER_BEEN_USED": (
            "⚠ FOUND BY COUNTING RATHER THAN BY READING A SUMMARY, and it changes what the cheapest next "
            "step is. The first method contributes exactly ONE pose per receptor — that is the whole of "
            "the six-pose census `R5` rests on. The second method's committed output is not one pose per "
            "receptor: each file holds the engine's full run set, and every one of those poses is already "
            "in the repository. So the program's only *within-method* pose ensemble for this ligand "
            "exists, is committed, and has been read for its single best member only. ⛔ This does NOT "
            "make the pose singular and does not soften anything above — an ensemble whose members "
            "disagree is the problem, not the fix. What it does is price the next honest step: reporting "
            "the second method's own spread over its committed run set is $0 CPU on files already here, "
            "not a new docking campaign."
        ),
        "⛔_the_selection_stage_pose_is_not_among_them": {
            "_why_it_matters": (
                "the paper's §2.7 advancement margin — the number that SELECTED this candidate — was "
                "computed in the unbiased release/design frame. Every committed pose above is either a "
                "metadynamics-opened frame or an 8XTT experimental conformer. The release-frame pose is "
                "not held anywhere."
            ),
            "provenance_rows_recording_it_lost": lost_rows,
            "pose_convergence_calls_it": dig(
                load("research/modalities/pose-convergence-401.json"), "known_absent.1.why"
            ),
            "_consequence": (
                "⛔ NOT-MARGINALISABLE IN THE STRONGEST SENSE — the marginalisation cannot be performed "
                "even with unlimited compute on what is committed, because the pose that produced the "
                "number no longer exists. Re-deriving it means re-docking into a re-selected release "
                "frame and re-running the tier, which is a NEW measurement, not a marginalisation of "
                "this one."
            ),
        },
    }


# ── the evidence block: read, never restated ────────────────────────────────────────────────────────
def evidence() -> dict:
    conv = load("research/modalities/pose-convergence-401.json")
    two = load("research/modalities/pose-second-method.json")
    cav = load("research/modalities/r5-cross-method-cavity-attribution.json")

    pb_status = Counter(p["second_method"].get("_status") for p in dig(two, "part_b.pairs"))
    unrun = {k: v for k, v in pb_status.items() if k}
    n_excluded = sum(1 for p in dig(two, "part_b.pairs") if p.get("excluded_by"))

    return {
        "first_method_pose_spread": {
            "_home": "research/modalities/pose-convergence-401.json → verdict",
            "_engine": "smina (top pose), one method across six receptor conformers",
            "n_poses": dig(conv, "verdict.n_usable_sources"),
            "n_pairs": dig(conv, "verdict.n_pairs"),
            "pocket_superposed_ligand_rmsd_A": dig(conv, "verdict.pocket_fit_ligand_rmsd_spread_A"),
            "n_pairs_within_2.0A": dig(conv, ["verdict", "n_pairs_within_2.0A"]),
            "scale_reference": dig(conv, "scale_reference"),
            "score_did_not_choose_among_them": dig(conv, "score_cannot_tell_these_poses_apart.pairwise_score_delta_kcalmol"),
            "receptor_agreement_does_not_predict_ligand_agreement": dig(
                conv, ["verdict", "receptor_agreement_does_not_predict_ligand_agreement",
                       "n_pairs_with_pocket_fit_within_1.0A"]
            ),
        },
        "second_method_part_a_the_falsifier_firing": {
            "_home": "research/modalities/pose-second-method.json → verdict",
            "second_method": dig(two, "verdict.second_method"),
            "tooling": dig(two, "tooling.rdock_version"),
            "cross_method_evidence": dig(two, "verdict.cross_method_evidence"),
            "n_systems": dig(two, "verdict.part_a_n_systems"),
            "n_agreeing_within_recovered_A": dig(two, "verdict.part_a_agreement_within_recovered_A"),
            "recovered_A": dig(two, "criterion.recovered_A"),
            "partial_A": dig(two, "criterion.partial_A"),
            "median_inter_method_rmsd_A": dig(two, "verdict.part_a_median_inter_method_rmsd_A"),
            "bands": dig(two, "part_a.cross_method_same_frame.bands"),
            "centroid_distance_A": dig(two, "part_a.cross_method_same_frame.centroid_distance_A"),
            "internal_conformer_rmsd_A": dig(two, "part_a.cross_method_same_frame.internal_conformer_rmsd_A"),
            "decomposition": dig(two, "part_a.orientation_or_location._reads"),
            "R5_resolved": dig(two, "verdict.R5_resolved"),
            "outcome": dig(two, "verdict.outcome"),
            "sentence": dig(two, "verdict.sentence"),
            "second_method_is_no_better_converged": {
                "_asks": "does the SECOND method converge across receptor conformers any better than the first?",
                "n_pairs": dig(two, "part_a.within_second_method_spread.n_pairs"),
                "ligand_rmsd_A": dig(two, "part_a.within_second_method_spread.ligand_rmsd_A"),
                "n_pairs_within_recovered_A": dig(two, "part_a.within_second_method_spread.n_pairs_within_recovered_A"),
                "n_pairs_within_partial_A": dig(two, "part_a.within_second_method_spread.n_pairs_within_partial_A"),
                "_reads": (
                    "⛔ NO. The second method's own spread across the same six receptors is WIDER than the "
                    "first's, with zero pairs inside either band. So the disagreement is not 'one method is "
                    "noisy and the other is tight' — neither engine produces a singular pose on this fold."
                ),
            },
        },
        "⛔_the_half_that_gets_forgotten__no_known_answer_calibration": {
            "_asks": "on systems where the crystallographic answer IS known, what did the second method recover?",
            "_answer": "NOTHING — the arm did not run.",
            "n_pairs_attempted": dig(two, "part_b.n_pairs_attempted"),
            "n_gradeable": dig(two, "verdict.part_b_n_gradeable"),
            "n_with_protocol_ceiling": dig(two, "part_b.rollup.n_with_ceiling"),
            "n_excluded_by_a_pre_registered_rule": n_excluded,
            "per_pair_status": unrun,
            "n_pairs_carrying_an_unrun_status": sum(unrun.values()),
            "⛔_an_absent_reading_is_not_a_reading_of_absence": (
                "CLAUDE.md §4. `n_gradeable: 0` here is NOT 'the second method failed to recover any known "
                "answer'. The per-pair `_status` says the arm never executed, and a zero produced by an "
                "unrun protocol must never be quoted as a measured failure. What it DOES mean is equally "
                "load-bearing and is the sentence people drop: **the second method arrived with no "
                "known-answer calibration of its own**, so the disagreement in Part A is a statement about "
                "TWO UNCALIBRATED METHODS. Neither is graded correct; they simply do not agree."
            ),
            "_and_the_first_method_is_no_better_off": (
                "`V3`'s own pre-registered panel returned INCONCLUSIVE. So there is no calibrated pose "
                "instrument on either side of this comparison, which is why the census below grades "
                "AGREEMENT and never CORRECTNESS."
            ),
            "cost_to_repair": "$0 — CPU/CI. The named cause is a protocol file the run could not read.",
        },
        "which_sub_cavity__the_disagreement_is_not_only_orientation": {
            "_home": "research/modalities/r5-cross-method-cavity-attribution.json",
            "n_systems": dig(cav, "rollup.n_systems"),
            "n_gradeable": dig(cav, "rollup.n_gradeable"),
            "n_same_cavity": dig(cav, "rollup.n_same_cavity"),
            "n_different_cavity": dig(cav, "rollup.n_different_cavity"),
            "first_method_cavity_calls": dig(cav, "rollup.first_method_cavity_calls"),
            "second_method_cavity_calls": dig(cav, "rollup.second_method_cavity_calls"),
            "cavity_chosen_by_the_frozen_rule": dig(cav, "rollup.cavity_chosen_by_the_frozen_rule"),
            "_reads": dig(cav, "rollup._reads"),
        },
        "the_already_worked_case__imported_verbatim": {
            "_home": "research/modalities/steric-carrier-audit.json → verdict.carried_candidate",
            "_why_verbatim": (
                "⭑ THIS IS THE TEMPLATE FOR EVERY GRADE BELOW, and re-deriving it would create a second "
                "home for it. One claim, two forms, two different answers across the same six poses."
            ),
            "record": dig(load("research/modalities/steric-carrier-audit.json"),
                          "verdict.carried_candidate.★_what_survives_the_pose_spread_and_what_does_not"),
        },
        "committed_pose_inventory": committed_pose_inventory(),
    }


# ── the census itself ───────────────────────────────────────────────────────────────────────────────
# Each row: what the claim is, where it lives, what it was computed ON, its grade, and its restated form.
# ⛔ `restated_as` is the sentence that should appear in the live document. It is authorship, and it is
#    deliberately written at the strength the evidence supports and no higher.
CLAIMS = [
    {
        "id": "PC-01",
        "claim": "\"The predicted docked pose of denovo_401\" — Figure 5(d) names a singular pose as the program's pose.",
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.7, Figure 5 caption panel (d)",
        ],
        "computed_on": "one smina top pose in one metadynamics-opened NR4A3 LBD frame",
        "grade": "POSE-DEPENDENT",
        "why_that_grade": (
            "six committed poses of this molecule exist in this receptor; they disagree by more than the "
            "cost of turning the molecule end-for-end, and a scoring-independent second method disagrees "
            "with the first by about the same amount. The definite article is the claim, and it is the "
            "part that fails."
        ),
        "restated_as": (
            "ONE OF SIX committed docked poses of denovo_401 in a metadynamics-opened NR4A3 LBD model. "
            "The six do not converge and a scoring-independent second method does not reproduce any of "
            "them, so this panel illustrates a member of a pose ensemble, not \"the\" predicted pose."
        ),
        "action": "EDITED — the live caption now carries the restated form.",
        "marginalisation_cost": "$0 — already done; the census is the marginalisation.",
    },
    {
        "id": "PC-02",
        "claim": (
            "The §2.7 advancement margin that SELECTED the candidate — multi-snapshot MM-GBSA mean ± SD "
            "and margin − SD in the unbiased release/design frame."
        ),
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.7 candidate table row `denovo_401`",
            "research/manuscripts/nr4a3-degrader-paper.md — §2.7 Figure 5 panels (a) and (b)",
        ],
        "computed_on": (
            "one docked pose in the release/design frame, relaxed and averaged over 10 MD frames. ⚠ Frame "
            "averaging around ONE pose is not marginalisation over poses and must never be reported as if "
            "it were."
        ),
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "⛔ THE STRONGEST FORM OF THIS GRADE, and it was found by looking rather than remembered: the "
            "release-frame pose is not among the six committed poses and `results/PROVENANCE.md` records "
            "its S3 prefix as LOST. The number cannot be spread over the census because its own pose is "
            "not in the census and no longer exists."
        ),
        "restated_as": (
            "computed on a single docked pose in a release-frame receptor whose pose coordinates are not "
            "committed anywhere and are recorded LOST; not marginalisable over the pose census, and not "
            "re-derivable from this repository without re-docking and re-running the tier."
        ),
        "action": "EDITED — the live text now carries the single-pose condition; the number is unchanged.",
        "marginalisation_cost": "GPU — a re-dock plus a re-run of the multi-snapshot tier per pose. Not a free step.",
    },
    {
        "id": "PC-03",
        "claim": "The metad-opened-frame MM-GBSA margin and its percentile against the frame-matched decoy null.",
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.7 (the honest narrowing paragraph)"],
        "computed_on": "one smina top pose in the metadynamics-opened frame",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "the pose it was computed on IS committed (two metad-opened poses exist), so unlike PC-02 the "
            "marginalisation is physically possible — but it has not been run, and MM-GBSA is a GPU step. "
            "An unrun marginalisation is not a marginalisation."
        ),
        "restated_as": (
            "computed on a single docked pose in that frame; not marginalisable without re-running the "
            "endpoint tier on each committed pose."
        ),
        "action": "EDITED — single-pose condition added; the numbers are unchanged.",
        "marginalisation_cost": "GPU — endpoint MM-GBSA per pose. Physically possible; not yet run.",
    },
    {
        "id": "PC-04",
        "claim": (
            "The ABFE block — per-receptor ΔG_bind against NR4A3 / NR4A1 / NR4A2 and both selectivity "
            "ΔΔG contrasts."
        ),
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.8 Result block (conditional ABFE)",
            "research/manuscripts/nr4a3-degrader-paper-SI.md — §S7",
        ],
        "computed_on": "one docked starting pose per receptor, propagated by explicit-solvent double decoupling",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "the starting complex geometry is a single pose per receptor and `results/nr4a3-abfe/` holds "
            "diagnostics only — no starting coordinates are committed. A Boresch-restrained absolute leg "
            "is anchored to its starting geometry, so a different pose is a different calculation, not a "
            "re-analysis. ⚠ The paper already discloses conditionality on the RECEPTOR FRAME and on "
            "\"pose errors\"; what it did not carry is that the pose is one of a non-convergent set."
        ),
        "restated_as": (
            "conditional on a single docked starting pose per receptor as well as on the selected opened "
            "conformer; not marginalisable without re-running the ABFE legs from each committed pose, "
            "which is multi-leg GPU spend and is not authorised."
        ),
        "action": "EDITED — the pose condition now travels beside the conformer condition in §2.8.",
        "marginalisation_cost": "multi-leg GPU, past the >$50 review gate. trimcrae's call, not an agent's.",
    },
    {
        "id": "PC-05",
        "claim": "The 8XTT-anchored NR4A3 ABFE leg and the receptor-model sensitivity reading built on it.",
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.8 8XTT-anchored recalculation"],
        "computed_on": "one docked pose in an 8XTT-seeded release-MD frame (\"denovo_401 docked identically\")",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "same mechanism as PC-04. ⭑ And there is a second-order point worth stating rather than "
            "leaving implicit: this leg's own finding is that the choice of receptor CONFORMER moves the "
            "absolute by more than the whole selectivity margin. The pose census now shows a second, "
            "independent axis of the same kind that has never been swept at all."
        ),
        "restated_as": (
            "computed on a single docked pose in one 8XTT-anchored frame; not marginalisable without a "
            "re-run. The conformer-sensitivity reading it supports is unaffected — that comparison is "
            "between frames — but it must not be read as bounding the pose sensitivity, which is unmeasured."
        ),
        "action": "EDITED — the pose condition added; the conformer-sensitivity reading left intact.",
        "marginalisation_cost": "multi-leg GPU. Same gate as PC-04.",
    },
    {
        "id": "PC-06",
        "claim": "The lead-optimization ABFE cross-check (`lo_m0_NCCO`) — an FEP tie, no resolved improvement.",
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.8 lead-optimization cross-check",
            "research/manuscripts/nr4a3-degrader-paper-SI.md — §S5",
        ],
        "computed_on": "one docked pose per molecule in one opened NR4A3 frame",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "a paired comparison inherits the pose condition of BOTH legs. ⚠ It is also the row where a "
            "pose difference could most easily masquerade as a chemistry difference, since the two "
            "molecules differ by one substituent and were docked independently."
        ),
        "restated_as": (
            "both legs were started from a single docked pose each; the tie is not marginalisable over "
            "poses, and a pose difference between the two legs cannot be excluded from it."
        ),
        "action": "EDITED — the pose condition added in the SI where the comparison is stated in full.",
        "marginalisation_cost": "GPU — two ABFE legs per pose pair.",
    },
    {
        "id": "PC-07",
        "claim": "The stereochemical species resolution — 16 stereoisomers docked and MM-GBSA-scored, resolving the diastereomer carried forward.",
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.7 species resolution"],
        "computed_on": "one top pose per stereoisomer",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "the ranking that picked the diastereomer is a comparison of 16 single poses. If the pose is "
            "not a singular object for one stereoisomer it is not for any of them, and the ranking is "
            "between quantities each conditional on its own unmarginalised pose."
        ),
        "restated_as": (
            "a ranking of single-pose scores, one pose per stereoisomer; not marginalisable without "
            "re-docking and re-scoring each stereoisomer across a pose ensemble."
        ),
        "action": "CENSUS ONLY — the live text already reads as a docking+MM-GBSA triage, and the "
                  "single-pose condition is now carried once, in §2.7, covering the tier.",
        "marginalisation_cost": "GPU — 16 × ensemble re-scores.",
    },
    {
        "id": "PC-08",
        "claim": "The anti-target counter-screen statements about the candidate — the panel maximum and the every-survivor clause.",
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.5 counter-screen sentence",
            "research/manuscripts/nr4a3-degrader-paper-SI.md — §S1",
        ],
        "computed_on": "one top pose per anti-target receptor",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "⛔ AND IT CARRIES TWO INDEPENDENT BLOCKS, WHICH MUST NOT BE COLLAPSED INTO ONE. (a) The pose "
            "block, new here: every score is a single top pose. (b) The instrument block, already on "
            "record: the panel's cognate-ligand self-control fails on three receptors, so "
            "`panel_readable: false`. Repairing the panel would NOT discharge (a), and marginalising over "
            "poses would NOT discharge (b)."
        ),
        "restated_as": (
            "single-pose docking scores across the panel; not marginalisable without re-docking every "
            "target over a pose ensemble — and separately not currently readable at all, for the "
            "unrelated self-control reason already stated."
        ),
        "action": "CENSUS ONLY — the live text already refuses these numbers on the instrument ground; "
                  "adding a second refusal to a sentence that may not be quoted would be noise.",
        "marginalisation_cost": "CPU/CI for the re-dock; the instrument repair is separately $0.",
    },
    {
        "id": "PC-09",
        "claim": (
            "The pre-committed advancement criterion \"persistence of the modeled pose over the short "
            "screening trajectory\"."
        ),
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.7 (what the program pre-committed to)"],
        "computed_on": "one pose, watched over one short trajectory",
        "grade": "POSE-DEPENDENT",
        "why_that_grade": (
            "⭑ THE SHARPEST ROW ON THE PAGE, because the criterion's own wording presupposes the thing "
            "that failed. \"The modeled pose\" persisting says nothing about whether it was the right one "
            "of six; a pose can be locally stable and still be one of several mutually-inconsistent "
            "placements. Six poses exist, they disagree, and the persistence test was applied to one."
        ),
        "restated_as": (
            "persistence of ONE modelled pose over one short trajectory. Local persistence is evidence "
            "that a placement is a local minimum, not evidence that it is the placement — and the pose "
            "census shows at least six such placements, of which this criterion examined one."
        ),
        "action": "EDITED — the criterion is restated in the live text at this strength.",
        "marginalisation_cost": "GPU — a short trajectory per committed pose. Cheap, but not free, and not run.",
    },
    {
        "id": "PC-10",
        "claim": "The steric design rule's WEAK form — the carried candidate reaches at least one design-target lobe.",
        "where": ["research/modalities/steric-carrier-audit.json → verdict.carried_candidate"],
        "computed_on": "all six committed poses",
        "grade": "POSE-ROBUST",
        "why_that_grade": (
            "measured across the whole census and it holds in every pose. ⭑ This is the one row that "
            "already had the work done, and it is why the grade vocabulary has a POSE-ROBUST band at all: "
            "the falsifier firing does not delete pose-conditional claims, it demands they be graded."
        ),
        "restated_as": (
            "holds in every committed pose of the carried candidate. ⛔ Its ceiling is unchanged and "
            "travels with it: the paralogue RELOCATES this molecule rather than refusing it, so a lobe "
            "reach licenses a statement about a POSE, never \"the paralogue cannot bind this molecule\"."
        ),
        "action": "CENSUS ONLY — already correctly stated in its own artifact; imported, not re-derived.",
        "marginalisation_cost": "$0 — done.",
    },
    {
        "id": "PC-11",
        "claim": "The steric design rule's VECTOR-SPECIFIC form — which of the two design-target lobes the candidate occupies.",
        "where": ["research/modalities/steric-carrier-audit.json → verdict.carried_candidate"],
        "computed_on": "all six committed poses",
        "grade": "POSE-DEPENDENT",
        "why_that_grade": (
            "the answer changes with the pose: the pose in the rule's own frame reaches one lobe and not "
            "the other, and an experimental-conformer re-dock reaches the other and not the first. A "
            "design brief naming one vector for this molecule would be resting on a choice of pose."
        ),
        "restated_as": (
            "not stateable in singular form. What may be stated is the distribution over the six poses, "
            "which the audit reports per lobe; a single-vector design brief for this molecule is not "
            "supported."
        ),
        "action": "CENSUS ONLY — already correctly stated in its own artifact.",
        "marginalisation_cost": "$0 — done.",
    },
    {
        "id": "PC-12",
        "claim": "Which sub-cavity of the split prespecified site the candidate occupies.",
        "where": ["research/modalities/r5-cross-method-cavity-attribution.json → verdict"],
        "computed_on": "both methods, all six systems (five gradeable)",
        "grade": "POSE-DEPENDENT",
        "why_that_grade": (
            "⛔ AND THIS IS THE ROW THAT BOUNDS THE COMFORTING READING. The second-method artifact reads "
            "the disagreement as \"same location, different orientation\", which sounds survivable. That "
            "reading assumes one pocket, and the prespecified site is split across two. Per receptor the "
            "cavity call is itself conformer-dependent, and the two methods land in different cavities on "
            "one gradeable system — so neither the orientation reading nor a pure location reading holds "
            "across the census."
        ),
        "restated_as": (
            "the cavity assignment is pose- and receptor-conformer-dependent; the program may not state "
            "which sub-cavity the candidate occupies, and any claim that reads the disagreement as "
            "orientation-only must carry this row beside it."
        ),
        "action": "CENSUS ONLY — the artifact is the one home; the census points at it.",
        "marginalisation_cost": "$0 — done.",
    },
    {
        "id": "PC-13",
        "claim": "The ternary geometric-feasibility reading for the representative candidate-PROTAC, and its CRBN-proximity proxy.",
        "where": [
            "research/manuscripts/nr4a3-degrader-paper.md — §2.5 (representative candidate-PROTAC ternary)",
            "research/manuscripts/nr4a3-degrader-paper-SI.md — §S2",
        ],
        "computed_on": "a single predicted ternary pose per paralogue (a co-fold, not a docking search)",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "⚠ A DIFFERENT POSE OBJECT, AND THE DISTINCTION IS LOAD-BEARING. This is not the docked "
            "warhead pose — it is a generatively predicted complex, which fails differently. But it is "
            "still a singular pose, the paper already says so in those words, and the pose census does "
            "not reach it: no second ternary-pose method has been run, so nothing here is graded by "
            "agreement."
        ),
        "restated_as": (
            "read from a single predicted ternary pose per paralogue; not marginalised, and not "
            "marginalisable without a second, scoring-independent complex predictor."
        ),
        "action": "CENSUS ONLY — the live text already states \"a single Boltz pose\" and reads the result "
                  "as geometric feasibility only.",
        "marginalisation_cost": "GPU — a second complex predictor over the same constructs.",
    },
    {
        "id": "PC-14",
        "claim": "Rung `5b-T`'s site 1 — the target-side site the ternary assembly is built on.",
        "where": [
            "research/manuscripts/nr4a3-program-map.md — rung `5b-T`",
            "research/modalities/nr4a3-5bt-gate.json → inherited_limits_that_travel_with_every_result",
        ],
        "computed_on": "the docked pose",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "the rung's own gate artifact already declares that site 1 inherits an unresolved `R5` and "
            "that \"the warhead sub-pose is conditional\". ✅ What changes today is only the REASON: the "
            "blocker was \"no second opinion exists\", and a second opinion now exists and disagrees. The "
            "inherited limit was right and is now measured."
        ),
        "restated_as": (
            "site 1 is one docked pose of a non-convergent set; the rung's structural output is "
            "conditional on that pose and is not marginalisable without assembling the ternary from each "
            "committed pose."
        ),
        "action": "ROUTED — the roadmap edit updates the reason, not the verdict.",
        "marginalisation_cost": "GPU per pose — the rung's own cost multiplied by the census size.",
    },
    {
        "id": "PC-15",
        "claim": "The paralogue ABFE follow-up legs and the downstream ternary rungs anchored on the carried candidate.",
        "where": [
            "research/manuscripts/nr4a3-program-map.md — the crystal-seeded paralogue ABFE follow-up; rungs 5c and 5d",
        ],
        "computed_on": "not yet run — each would be anchored on one docked pose",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "⭑ FLAGGED BEFORE THE MONEY IS SPENT, WHICH IS THE ONLY TIME THIS FLAG IS WORTH ANYTHING. "
            "These rungs are priced and unrun. Buying them as designed would purchase a new "
            "pose-conditional number that inherits exactly the condition this census exists to record, "
            "and it would inherit it silently unless the rung's own scope says otherwise."
        ),
        "restated_as": (
            "any of these rungs, run as currently scoped, returns a quantity conditional on one docked "
            "pose. That is not a reason to refuse them — it is a scope line their result must carry from "
            "the moment it exists."
        ),
        "action": "ROUTED — the rungs' scope lines now carry the pose condition in advance.",
        "marginalisation_cost": "GPU, multi-leg. The point of the row is that the condition is cheaper to "
                                "declare now than to retrofit later.",
    },
    {
        "id": "PC-16",
        "claim": "The computational alanine scan of the handle residues (per-residue MM-GBSA ΔΔG of the candidate).",
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.4 conservation paragraph"],
        "computed_on": "not run — stated as something that \"could estimate\" ligand-binding sensitivity",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "a per-residue ΔΔG of a ligand is defined only relative to a placement, so this instrument is "
            "pose-conditional by construction. It has not been run, so nothing is retracted — but a "
            "future run must not present per-residue sensitivities as properties of the molecule."
        ),
        "restated_as": (
            "would be conditional on the pose it was computed in; not a property of the molecule, and it "
            "must be reported per pose if it is ever run."
        ),
        "action": "CENSUS ONLY — nothing is claimed today; the row exists so the condition is not "
                  "discovered after the fact.",
        "marginalisation_cost": "GPU per pose, if ever run.",
    },
    {
        "id": "PC-17",
        "claim": (
            "The generated-library quality statistic — the fraction of generated molecules contacting at "
            "least four of the five engageable handles."
        ),
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.6 generation-quality sentence"],
        "computed_on": "one generated pose per molecule",
        "grade": "NOT-MARGINALISABLE",
        "why_that_grade": (
            "a generative model emits a molecule WITH a placement, so the contact count is a property of "
            "that emitted placement. `results/PROVENANCE.md` additionally records the generation pool's S3 "
            "prefix as LOST, so as with PC-02 the poses behind the statistic are not held."
        ),
        "restated_as": (
            "a property of the single pose each molecule was generated in, not of the molecules; the "
            "generation pool is recorded LOST, so it is not re-derivable from this repository."
        ),
        "action": "CENSUS ONLY — the statistic is a generation-quality descriptor and is not load-bearing "
                  "for any claim in the paper.",
        "marginalisation_cost": "GPU — regeneration, not marginalisation.",
    },
    {
        "id": "PC-18",
        "claim": "The warhead exit vector and the basin/meta-basin enumeration built on it.",
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.10 and its limitations"],
        "computed_on": "an ensemble of warhead exit-vector poses, with the pose-surviving fraction reported per basin",
        "grade": "ALREADY-MARGINALISED",
        "why_that_grade": (
            "⭑ THE TEMPLATE, AND IT IS ALREADY IN THE PAPER. This section marginalises over a pose "
            "ensemble by construction and reports what fraction of poses each result survives, precisely "
            "because no pose of its ligand exists in the matched frame. The falsifier changes nothing "
            "here. ⚠ Note it is a different ligand from the carried candidate — this is not a claim that "
            "the candidate's geometry was handled this way."
        ),
        "restated_as": "unchanged — it was already stated as marginalised over poses.",
        "action": "NONE — listed so the blast radius is bounded by measurement rather than by assertion.",
        "marginalisation_cost": "$0 — done, before the falsifier existed.",
    },
    {
        "id": "PC-19",
        "claim": (
            "Sequence-level uniqueness of the NR4A3-unique cysteine and lysines, and the per-frame reach "
            "of the unique cysteine to the pocket exit vector."
        ),
        "where": ["research/manuscripts/nr4a3-degrader-paper.md — §2.10 categorical handles"],
        "computed_on": (
            "an alignment (no structure) for the uniqueness half; a receptor-derived exit vector over 75 "
            "unbiased conformers for the reach half — no ligand pose enters either"
        ),
        "grade": "ALREADY-MARGINALISED",
        "why_that_grade": (
            "the paper already states this distinction in its own words — sequence-level uniqueness is "
            "pose-independent — and the reach statistic is marginalised over conformers, using an exit "
            "vector defined from the pocket rather than from a docked ligand. ⚠ It is still conditional "
            "on the SITE being right, which is the other half of `R5` and is separately unresolved."
        ),
        "restated_as": "unchanged — pose-independent, conformer-marginalised, and site-conditional as already stated.",
        "action": "NONE.",
        "marginalisation_cost": "n/a.",
    },
]


def build() -> dict:
    ev = evidence()
    counts = Counter(c["grade"] for c in CLAIMS)
    edited = [c["id"] for c in CLAIMS if c["action"].startswith("EDITED")]
    routed = [c["id"] for c in CLAIMS if c["action"].startswith("ROUTED")]
    return {
        "_module": "pose_conditionality_census",
        "_title": (
            "THE POSE-CONDITIONALITY CENSUS — every claim conditional on a singular pose of "
            f"{LIGAND}, its grade, and its restated form"
        ),
        "_owns": (
            "the ONE HOME of which claims in this repository are pose-conditional and how each is graded. "
            "Every figure is READ from the artifacts named per block; no number is typed here."
        ),
        "_answers": (
            "research/manuscripts/path-family-synthesis.md §2 Tier-1 row 2 — the pre-registered falsifier, "
            "which FIRED on 2026-08-06"
        ),
        "_status": (
            "$0 — stdlib on CPU over committed artifacts and committed coordinates. Nothing here is a "
            "claim about binding, affinity, degradation, selectivity, efficacy or safety, and no molecule "
            "named here is a hit."
        ),
        "_generated": {"generator": "research/modalities/pose_conditionality_census.py", "date": "2026-08-07"},
        "_does_not_license": [
            "that any pose is correct — no experimental structure of this complex exists, and neither "
            "method carries a passing known-answer calibration",
            "that anything binds — `R4` still needs a bench and nothing here touches it",
            "that a POSE-ROBUST grade rescues a claim: robust across a non-convergent ensemble means the "
            "claim does not depend on which member is right, never that any member IS right",
            "reading a grade as a quality score for the underlying science",
        ],
        "the_falsifier": {
            "text": (
                "independent methods disagree as widely as the six existing poses ⇒ \"the predicted pose\" "
                "is not an object this program is entitled to, and every pose-conditional row above must "
                "be restated as marginalised-over-poses"
            ),
            "pre_registered_in": "research/manuscripts/path-family-synthesis.md §2 Tier-1 row 2",
            "fired": True,
            "fired_on": "2026-08-06",
            "verdict_artifact": "research/modalities/pose-second-method.json",
            "⭑_why_this_file_exists": (
                "a pre-registered consequence that fires and is then not carried out converts a discipline "
                "into a decoration. The falsifier named the remedy — restatement — and this is the "
                "restatement, itemised so that a reader can check it claim by claim rather than trusting "
                "that it happened."
            ),
        },
        "evidence": ev,
        "grades": GRADES,
        "claims": CLAIMS,
        "rollup": {
            "n_claims": len(CLAIMS),
            "by_grade": dict(sorted(counts.items())),
            "n_live_documents_edited": len(edited),
            "claims_whose_live_text_was_edited": edited,
            "claims_routed_as_map_edits": routed,
            "⭑_the_one_sentence": (
                f"{counts['POSE-ROBUST']} claim(s) survive the marginalisation, "
                f"{counts['POSE-DEPENDENT']} may not be stated in singular form at all, "
                f"{counts['NOT-MARGINALISABLE']} were computed on one pose and cannot be spread without "
                f"new compute, and {counts['ALREADY-MARGINALISED']} never rested on a singular pose. "
                "⛔ The largest band is the one that needs money, which is the honest shape of this result "
                "and not a reason to soften it."
            ),
            "⛔_what_the_census_does_NOT_do": (
                "it does not retract a number. Not one figure in the manuscript changes value here — what "
                "changes is the condition each figure is stated under. A census that quietly moved numbers "
                "would be a second failure on top of the first."
            ),
        },
        "what_would_discharge_each_grade": [
            {
                "grade": "NOT-MARGINALISABLE",
                "what_discharges_it": (
                    "re-running the quantity from each committed pose and reporting the distribution. For "
                    "the endpoint and free-energy rows this is GPU spend, and for the selection-stage row "
                    "it is not possible at all — that pose is recorded LOST, so only a NEW measurement can "
                    "replace it."
                ),
                "cost": "GPU; the largest rows sit behind the >$50 review gate",
            },
            {
                "grade": "POSE-DEPENDENT",
                "what_discharges_it": (
                    "nothing discharges it — it is an answer, not a gap. The claim is stated as a "
                    "distribution over poses or it is not stated."
                ),
                "cost": "$0",
            },
            {
                "grade": "the pose question itself",
                "what_discharges_it": (
                    "read from the second-method artifact rather than restated: "
                    + json.dumps(dig(load("research/modalities/pose-second-method.json"),
                                     "verdict.what_would_resolve_R5"), ensure_ascii=False)
                ),
                "cost": "see each item's own `cost` field in that list",
            },
        ],
    }


def map_edits(census: dict) -> dict:
    """Roadmap edits, emitted for `route_map_edits.py`. Anchors are verified before routing."""
    ev = census["evidence"]
    two = ev["second_method_part_a_the_falsifier_firing"]
    nk = ev["⛔_the_half_that_gets_forgotten__no_known_answer_calibration"]
    roll = census["rollup"]
    n_pose_dep = roll["by_grade"].get("POSE-DEPENDENT", 0)
    n_not_marg = roll["by_grade"].get("NOT-MARGINALISABLE", 0)
    n_robust = roll["by_grade"].get("POSE-ROBUST", 0)
    n_already = roll["by_grade"].get("ALREADY-MARGINALISED", 0)
    cav = ev["which_sub_cavity__the_disagreement_is_not_only_orientation"]

    discharged = (
        " ✅ **THE RESTATEMENT DEBT IS DISCHARGED, AND IT IS ITEMISED RATHER THAN ASSERTED "
        f"([`pose-conditionality-census.json`](../modalities/pose-conditionality-census.json), {census['rollup']['n_claims']} claims): "
        f"{n_robust} POSE-ROBUST · {n_pose_dep} POSE-DEPENDENT · {n_not_marg} NOT-MARGINALISABLE · "
        f"{n_already} ALREADY-MARGINALISED.** ⛔ **No figure changed value** — what changed is the "
        "condition each is stated under. ⚠ **And the half that gets dropped: the second method brought "
        f"NO known-answer calibration either** — Part B is `n_gradeable: {nk['n_gradeable']}` of "
        f"{nk['n_pairs_attempted']} attempted, and that zero is an **UNRUN arm**, not a measured failure "
        "to recover, so the Part A disagreement is between **two uncalibrated methods**. ⭑ The strongest "
        "single row is the selection-stage margin: the release-frame pose it was computed on is **not "
        "among the committed poses and is recorded LOST**, so it is not marginalisable even in principle."
    )

    edits = [
        {
            "id": "PCC-1",
            "serves": "R5",
            "section": "§21 · the requirement register, row R5",
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "⇒ **every pose-conditional claim must be stated as marginalised over poses, not as \"the predicted pose\"**",
            "current_text": "⇒ **every pose-conditional claim must be stated as marginalised over poses, not as \"the predicted pose\"** — and stated against `C14`, since \"agrees\" here means the 2.0 Å line and **1 of 15** pairs meets it",
            "proposed_text": "⇒ **every pose-conditional claim must be stated as marginalised over poses, not as \"the predicted pose\"** — and stated against `C14`, since \"agrees\" here means the 2.0 Å line and **1 of 15** pairs meets it"
            + discharged,
            "why": "the roadmap already carried the instruction; it did not carry the fact that it had been carried out, "
                   "which is exactly how a pre-registered consequence quietly lapses.",
        },
        {
            "id": "PCC-2",
            "serves": "R5 · §10.3 prerequisite table",
            "section": "§10.3 · what row 4 unblocks",
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "`cross_method_evidence` is **NONE** — every pose the program holds is one method's top pose, so the 6-pose disagreement cannot currently be attributed to anything",
            "current_text": "`cross_method_evidence` is **NONE** — every pose the program holds is one method's top pose, so the 6-pose disagreement cannot currently be attributed to anything",
            "proposed_text": (
                "⚠ **THE PREREQUISITE HAS BEEN MET AND THE ROW SURVIVES IN A CHANGED FORM.** "
                "*Superseded, retained: \"`cross_method_evidence` is **NONE** — every pose the program "
                "holds is one method's top pose, so the 6-pose disagreement cannot currently be attributed "
                f"to anything.\"* A second method was run ({two['second_method']}) and "
                f"`cross_method_evidence` is now **{str(two['cross_method_evidence']).split('—')[0].strip()}** — "
                f"and it **DISAGREES**: {two['n_agreeing_within_recovered_A']} of {two['n_systems']} systems "
                f"agree inside the {two['recovered_A']} Å recovery line, median "
                f"{two['median_inter_method_rmsd_A']} Å. ⛔ So the disagreement is no longer "
                "*unattributable*; it is attributed, and the attribution is that neither engine produces a "
                "singular pose on this fold. ⚠ Read with its other half: the second method brought no "
                "known-answer calibration of its own, so this is two uncalibrated methods disagreeing and "
                "not a demonstration that either is wrong"
            ),
            "why": (
                "this cell states the second method as UNRUN, in the table that tells a session what row 4 "
                "unblocks. A prerequisite recorded as outstanding after it has been met sends the next "
                "session to buy something it already owns."
            ),
        },
        {
            "id": "PCC-3",
            "serves": "R5 · §10.3 why row 4 takes the top",
            "section": "§10.3 · reason 2",
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "A second engine is the only\n   observation that distinguishes",
            "current_text": (
                "A second engine is the only\n   observation that distinguishes *\"the method is uncertain\"* from *\"the site is wrong\"*, and the site half is\n"
                "   already **0 of 14** on two independent transfer routes."
            ),
            "proposed_text": (
                "A second engine is the only\n   observation that distinguishes *\"the method is uncertain\"* from *\"the site is wrong\"*, and the site half is\n"
                "   already **0 of 14** on two independent transfer routes.\n"
                "   ✅ **THAT OBSERVATION HAS NOW BEEN TAKEN, and it did not resolve the fork — it moved it.** "
                f"The second engine agrees with the first on {two['n_agreeing_within_recovered_A']} of "
                f"{two['n_systems']} systems inside the {two['recovered_A']} Å line, and the cavity-attribution "
                f"follow-up finds the two engines in the SAME sub-cavity on {cav['n_same_cavity']} of "
                f"{cav['n_gradeable']} gradeable systems and in DIFFERENT ones on {cav['n_different_cavity']}. "
                "⛔ So *\"the method is uncertain\"* and *\"the site is wrong\"* are **both** live, and the "
                "reading that the disagreement is orientation-only does not hold across the census."
            ),
            "why": (
                "the sentence claims an observation has not been taken. It has. Leaving it stated as "
                "outstanding is the same failure class as PCC-2, in the paragraph that ranks the board."
            ),
        },
        {
            "id": "PCC-4",
            "serves": "R9 · rung 5b-T",
            "section": "§10.3 · what picking row 4 costs",
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "because the largest $0 item on the board has now been spent on a pose the program cannot yet call singular.",
            "current_text": "because the largest $0 item on the board has now been spent on a pose the program cannot yet call singular.",
            "proposed_text": (
                "because the largest $0 item on the board has now been spent on a pose the program cannot "
                "yet call singular. ⭑ **AND THE REASON HAS CHANGED WHILE THE VERDICT HAS NOT.** *\"Cannot "
                "YET call singular\"* read as a gap awaiting a second opinion; the second opinion exists "
                "and disagrees, so site 1 is one member of a measured non-convergent ensemble and the "
                "rung's `NO-GO` is conditional on that member. ⛔ Nothing about the `NO-GO` is softened — "
                "arm C still failed on geometry registered at risk in advance and arm B still returned "
                "zero passing columns. What changes is that re-reading the rung on another pose is now a "
                "named, priced consequence rather than a hypothetical: it is the rung's own cost, once per "
                "committed pose"
            ),
            "why": (
                "the rung's inherited limit was written when the blocker was 'no second opinion exists'. "
                "The blocker is now 'the second opinion disagrees', which is a different claim about the "
                "same verdict and must not be left reading as the old one."
            ),
        },
        {
            "id": "PCC-5",
            "serves": "R12 · rung 5c",
            "section": "§10.1 · open rows, row 21",
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "| **21** | **5c — explicit ternary-ensemble refinement** |",
            "current_text": "which lysine the ubiquitin actually reaches, per construct, as a distribution over unique-vs-conserved sites |",
            "proposed_text": (
                "which lysine the ubiquitin actually reaches, per construct, as a distribution over "
                "unique-vs-conserved sites. ⛔ **SCOPE LINE, DECLARED BEFORE THE SPEND RATHER THAN "
                "RETROFITTED AFTER IT:** as currently scoped this rung is anchored on ONE docked pose of "
                "the carried candidate, so whatever distribution it returns is conditional on that pose "
                "and inherits `R5` unresolved. That is not a reason to refuse the rung — it is a line its "
                "result must carry from the moment it exists "
                "([`pose-conditionality-census.json`](../modalities/pose-conditionality-census.json) "
                "`PC-15`) |"
            ),
            "why": (
                "priced-and-unrun rungs are the only place where a pose condition can be declared before "
                "it costs anything. Retrofitting it after the number exists is how the manuscript acquired "
                "the debt this census is discharging."
            ),
        },
    ]
    return {
        "_what": "Roadmap edits discharging the R5 restatement debt — the pose-conditionality census.",
        "_rule": (
            "⛔ NO NUMBER IS TYPED IN THIS FILE. Every figure in every `proposed_text` is derived by "
            "pose_conditionality_census.py from the census it writes in the same run, which in turn reads "
            "pose-second-method.json / pose-convergence-401.json / steric-carrier-audit.json / "
            "r5-cross-method-cavity-attribution.json. Regenerate rather than edit."
        ),
        "_fence": (
            "This pass owns the RESTATEMENT of pose-conditional claims. It changes no gate, no price, no "
            "rung status, no criterion and no verdict — `R5` stays unresolved and `V22`'s reading is "
            "untouched. It adds the census and says the debt is paid."
        ),
        "generated_from": "research/modalities/pose-conditionality-census.json",
        "n_edits": len(edits),
        "map_edits_required": edits,
    }


def main() -> int:
    census = build()
    OUT.write_text(json.dumps(census, indent=1, ensure_ascii=False) + "\n")
    MAP_EDITS_OUT.write_text(json.dumps(map_edits(census), indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"wrote {MAP_EDITS_OUT.relative_to(REPO)}")
    print(census["rollup"]["★_the_one_sentence" if "★_the_one_sentence" in census["rollup"] else "⭑_the_one_sentence"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
