#!/usr/bin/env python3
"""C02 — THE CROSS-SYSTEM DECOY NULL FOR THE CATEGORICAL COVALENT AXIS.

THE PROBLEM THIS EXISTS TO FIX
------------------------------
`nr4a-paralogue-dynamics.json -> categorical_verdict` reports
`P(paralogue also labelled | NR4A3 labelled)` = 0.0 / 0.00124 / 0.00290 at the 12-atom design gate over
73,867 matched E3 placements — and every null in this repo is WITHIN-system (`term_b_background_null` is a
placement null; `V19` is a generation-matched null). Neither asks how often an ARBITRARY close paralogue pair
produces the same "no collision" answer. **So the categorical result is currently an enrichment over an
unmeasured background.**

The precedent is exact. `V20` — single-snapshot MM-GBSA `margin > 0` — looked like a clean selectivity signal
until 38 unrelated marketed drugs went through the identical funnel and 22 of them scored a positive margin
(`selectivity_calibration.DECOY_2026_06_30`). That retracted a headline. The categorical axis has never had
its equivalent test, and this module is that test.

WHAT IT DOES
------------
Pushes UNRELATED human paralogue PAIRS through the IDENTICAL categorical pipeline — the same E3 arm registry,
the same pose construction, the same placement sampler, the same prolate-spheroid reach rule, the same
12-atom gate, the same RSA 0.25 exposure cutoff, the same Shrake-Rupley SASA, the same BLOSUM62 aligner — and
asks how often a pair with no reason to be discriminable returns "0 collision".

Every scientific function is IMPORTED, never re-implemented:
  * `nr4a3_basin_search`      — model loading, superposition, pose ensemble, placement sampling, PARAMS
  * `nr4a_paralogue_dynamics` — `align_map`, `matched_reach_hits_multi`, `wilson95`
  * `nr4a_differential_atlas` — Needleman-Wunsch, Shrake-Rupley SASA, RSA
  * `nr4a3-e3-arm-registry-native.json` — the SAME two staged E3 arms (VHL, CRBN) with the SAME observed
    9UUM E2 geometry
What is NEW here is only the DRIVER: which pairs, which pocket, and the background arithmetic.

⚠ WHAT THIS CALIBRATES. The SCREEN, not the target. A low background rate says the categorical GO is
informative; a high one says it is not. Neither is a statement about NR4A3's chemistry, binding, reactivity,
degradation, efficacy or safety.

THE PRE-REGISTRATION IS IN `PREREG` BELOW AND IS WRITTEN INTO THE ARTIFACT AHEAD OF ANY RESULT. It was fixed
before a single structure was fetched. Mode `plan` emits it on its own so the git history carries the design
before the numbers.

★ TWO SCOPES, AND THE SECOND IS NOT A WIDENING OF THE FIRST (added 2026-08-03)
------------------------------------------------------------------------------
`--scope plddt` (default, configuration item `C16`) is the run that is already committed. Its
pre-registered domain trim — largest contiguous pLDDT >= 70 run — keeps UniProt 427-570 of the NR4A3
AlphaFold model, so of the committed unique set {397, 420, 559} **only 559 was ever scored**. The reported
percentile is a real measurement of a different residue's question, and the program's headline residue has
no measured background at all.

⛔ THE FIX IS NOT TO RELAX `C16`. Widening a pre-registered window after seeing what fell outside it is
exactly the tuning the pre-registration exists to prevent, and the committed run refuses it in its own
artifact. `--scope lbd` (configuration item `C24`) is a SECOND, INDEPENDENTLY PRE-REGISTERED run whose
scope is chosen on a structural rationale — see `PREREG_LBD`. The first run is not edited, re-reduced or
superseded by it; both stand, and the artifacts are separate files.

Usage
    python categorical_decoy_null.py plan                       # $0, no network: emit the prereg + pair plan
    python categorical_decoy_null.py probe                      # raw AlphaFold API/file answers (diagnostic)
    python categorical_decoy_null.py fetch                      # AlphaFold DB models for the universe (CI)
    python categorical_decoy_null.py pairs                      # trim + all-vs-all identity + pair selection
    python categorical_decoy_null.py run --shard 0 --nshards 8  # the statistic, sharded BY TARGET
    python categorical_decoy_null.py selfcheck                  # driver vs the COMMITTED static verdict
    python categorical_decoy_null.py reduce                     # background distribution + NR4A3 percentile

    ...and every mode takes `--scope {plddt,lbd}` (default `plddt`, byte-identical to the committed run).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import random
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                        # noqa: E402
import nr4a_differential_atlas as ATLAS       # noqa: E402
import nr4a3_basin_search as B                # noqa: E402
import nr4a_paralogue_dynamics as PD          # noqa: E402

CACHE = os.environ.get("DECOY_CACHE", os.path.join(REPO, "results", "categorical-decoy-null"))
OUT = os.path.join(HERE, "categorical-decoy-null.json")
PLAN = os.path.join(HERE, "categorical-decoy-null-plan.json")   # COMMITTED: the prereg lands in git first
SHARD_DIR = os.path.join(CACHE, "shards")
TRIMMED_DIR = os.path.join(CACHE, "trimmed")
# ⭑ The AlphaFold model cache is SHARED BY EVERY SCOPE ON PURPOSE. The models are the same files; only the
#   trim differs. Sharing them means the second scope re-uses the first's `fetch` when both run in one job,
#   and — more importantly — it makes it impossible for the two scopes to silently disagree about which
#   model an accession has.
AF_DIR = os.path.join(CACHE, "af")
SCOPE = "plddt"
UNIVERSE_SRC = os.path.join(HERE, "nr4a-superfamily-selectivity.json")
NATIVE_REGISTRY = PD.NATIVE_REGISTRY
DYNAMICS = os.path.join(HERE, "nr4a-paralogue-dynamics.json")

NR4A3_ACC = "Q92570"
NR4A1_ACC = "P22736"
NR4A2_ACC = "P43354"
NR4A_FAMILY = {NR4A3_ACC, NR4A1_ACC, NR4A2_ACC}

# =========================================================================================================
# ★ THE PRE-REGISTRATION. Fixed before any structure was fetched, any identity computed or any statistic
#   evaluated. Every threshold below is stated as a RULE with a reason, not tuned to an outcome. Changing any
#   of these after seeing results makes the percentile meaningless, so they live here as constants and the
#   artifact records them verbatim.
# =========================================================================================================
PREREG = {
    "_frozen": "Design fixed before any AlphaFold model was fetched and before any statistic was computed. "
               "Mode `plan` emits this block with no results at all, so git history carries the design "
               "ahead of the numbers.",
    "question": "How often does an ARBITRARY close human paralogue pair, pushed through the identical "
                "categorical pipeline, return P(paralogue also labelled | target-unique cysteine labelled) "
                "= 0 at the 12-backbone-atom design gate?",
    "universe": {
        "source": "research/modalities/nr4a-superfamily-selectivity.json -> ranking[] — 47 human nuclear "
                  "receptors with UniProt accessions, a COMMITTED artifact generated for a different "
                  "purpose months earlier. Using an existing on-disk list rather than curating one is what "
                  "keeps the universe answer-blind.",
        "exclusions": "the NR4A family (NR4A1 P22736, NR4A2 P43354, NR4A3 Q92570) — that is the test case, "
                      "not the background.",
        "why_nuclear_receptors": "The null must be the RIGHT null: close paralogue pairs in the same fold "
                                 "class, with the same domain size and the same kind of buried ligand "
                                 "pocket. A random-protein null would confound 'no collision' with 'wrong "
                                 "fold'. ⚠ The price is that the background measured here is a "
                                 "NUCLEAR-RECEPTOR background, not a proteome background — stated as a "
                                 "limit, not hidden.",
    },
    "structures": {
        "source": "AlphaFold DB, one model per accession, resolved through the prediction API (the file "
                  "URL's version number is NOT guessed — measured 2026-08-02, a hard-wired v4/v3/v2 file URL "
                  "404'd on all 48). The resolved URL, model version and SHA-256 are recorded per model.",
        "domain_trim": "largest CONTIGUOUS run of residues with pLDDT >= MIN_PLDDT (70.0), minimum length "
                       "MIN_DOMAIN_LEN (120) residues. "
                       "Mechanical, identical for every protein, and it removes the disordered tails whose "
                       "spurious cysteines would INFLATE the decoy collision rate — i.e. the trim is in the "
                       "direction that makes the NR4A3 result look WORSE, not better.",
    },
    "pair_formation": {
        "identity_band": [0.35, 0.90],
        "why": "'close pairs, not random proteins'. The band brackets the measured NR4A3-vs-NR4A1 and "
               "NR4A3-vs-NR4A2 trimmed-domain identities, which are computed by this same code and "
               "recorded in the artifact.",
        "alignment_coverage_min": 0.60,
        "max_pairs": 10,
        "max_per_protein": 2,
        "ranking_rule": "qualifying unordered pairs ranked by |identity - NR4A3_reference_identity| "
                        "ASCENDING (closest to the NR4A3 case first), then taken greedily subject to "
                        "max_per_protein. Answer-blind: identity is a property of the sequences, computed "
                        "before any reach statistic exists.",
        "orientations": "each unordered pair contributes TWO ordered decoys (A as target/B as paralogue, "
                        "and B as target/A as paralogue). Both are reported; neither is chosen.",
    },
    "pocket_rule": "fpocket's HIGHEST-DRUGGABILITY cavity on the target's trimmed domain supplies the pocket "
                   "lining set, hence the pocket centroid the warhead exit-vector poses are built around. "
                   "Family-agnostic and mechanical. ⚠ It is NOT the same rule as NR4A3's prespecified "
                   "Pocket-5 — which is exactly why NR4A3 is ALSO run through this harness under this same "
                   "rule, and why the percentile is taken against THAT row rather than against the "
                   "committed one.",
    "statistic": {
        "gate_atoms": 12,
        "also_reported": [14, 16, 20],
        "definition": "P(any paralogue cysteine is inside the same linker budget | the same placement puts "
                      "the electrophile on a TARGET-UNIQUE cysteine), over one matched placement set.",
        "target_unique_cysteine": "a cysteine in the target whose BLOSUM62-aligned position in the "
                                  "paralogue is not a cysteine (or has no aligned partner) — the same rule "
                                  "that produces NR4A3's {C397, C420, C559}.",
        "both_filters": "computed BOTH reach-only and reach-AND-exposed (RSA >= 0.25). ⚠ The audit "
                        "established that at the 12-atom gate the reach-only numbers already carry the "
                        "result, so a null that tested only the exposure-filtered form would miss the "
                        "load-bearing case.",
        "uncertainty": "Wilson 95 % on the conditional, using the SAME `nr4a_paralogue_dynamics.wilson95`.",
    },
    "placements": {
        "target_n_placements": 45000,
        "why": "the committed NR4A3 run accepted 73,867 placements; 45,000 keeps every row inside one CI "
               "job while staying the same order. The sampler budget is chosen ADAPTIVELY per target from a "
               "pilot so that every row gets a comparable placement set rather than a comparable raw sample "
               "count — an acceptance rate is a property of the pocket, and matching samples would silently "
               "un-match the statistics.",
        "pilot_samples_per_arm_pose": 25000,
        "max_samples_per_arm_pose": 6000000,
        "n_poses": 12,
        "seed": 20260802,
    },
    "gradeability": {
        "min_conditioning_events": 20,
        "rule": "an ordered decoy is GRADED only if >= 20 placements put the electrophile on a "
                "target-unique cysteine at the 12-atom gate. Below that the conditional has no power and "
                "the row is reported as UNDERPOWERED with its counts and EXCLUDED from the percentile.",
        "⚠_selection_effect": "excluding underpowered rows biases the graded set toward pairs whose unique "
                              "cysteines are reachable at all — i.e. toward pairs with MORE opportunity to "
                              "collide, which makes the background HARDER for NR4A3 to beat, not easier. "
                              "The count of underpowered rows is reported so the reader can see the size of "
                              "the effect.",
        "undefined": "a pair with zero target-unique cysteines has no conditional at all. Recorded as "
                     "UNDEFINED with its count, never as a zero.",
    },
    "readout": {
        "percentile": "the fraction of GRADED decoy rows whose collision probability is <= NR4A3's "
                      "harness-matched row, plus the fraction that are EXACTLY zero. Reported for both the "
                      "reach-only and the exposure-filtered statistic.",
        "what_a_pass_means": "if few decoys reach 0, the categorical GO carries information and becomes "
                             "quotable WITH this background beside it. If most decoys reach 0, the "
                             "categorical GO is a property of the METHOD and the axis must be re-graded. "
                             "A pass is not the goal; a measured background is.",
    },
    "not_claimed": [
        "Nothing here is a claim about binding, reactivity, degradation, selectivity in vivo, efficacy, "
        "safety, a therapeutic window or clinical readiness.",
        "Reach and exposure are NECESSARY, not sufficient: no thiol pKa, nucleophilicity, adduct stability "
        "or promiscuity is modelled, for the decoys any more than for NR4A3.",
        "This calibrates the SCREEN. It says nothing about NR4A3 specifically that the screen does not.",
    ],
}

LENGTHS = (12, 14, 16, 20)
GATE = 12
EXPOSED_RSA = PD.EXPOSED_RSA
MIN_PLDDT = 70.0            # PREREG.structures.domain_trim — one home, referenced there in words
MIN_DOMAIN_LEN = 120        # PREREG.structures.domain_trim


# =========================================================================================================
# ★★ THE SECOND PRE-REGISTRATION — configuration item `C24`, the reference-anchored LBD window.
#
# ⛔ READ THIS BEFORE READING ANY NUMBER UNDER IT. This is NOT a relaxation of `C16`. `C16` is not edited,
#    not re-reduced and not superseded; its run stands with its own artifact and its own caveat. This is a
#    SEPARATE test with its own scope, its own plan file and its own result file, and it was written and
#    committed to git BEFORE any structure had been trimmed under it and before any statistic under it
#    existed — `plan --scope lbd` emits this block with no results at all, exactly as `C16`'s did.
#
# ⚠ AND THE ONE THING THAT CANNOT BE UNDONE, STATED RATHER THAN HIDDEN: `C16`'s RESULT WAS KNOWN WHEN THIS
#    SCOPE WAS DESIGNED. Pretending otherwise would be worse than saying it. Three mitigations, all
#    structural rather than promissory:
#      (a) the scope rule below is stated entirely in terms of WHAT THE SCOPE IS FOR — the region of the
#          fold the categorical screen actually interrogates — and references no collision statistic,
#          no percentile and no decoy's answer. It is a rule that would have been written the same way
#          before anyone looked at an outcome, and the defect it repairs (below) is visible in `C16`'s
#          PLAN file, which contains no statistic;
#      (b) EVERY other pre-registered constant is held byte-identical to `C16` — gate, lengths, exposure
#          cutoff, identity band, coverage floor, ranking rule, orientations, pocket rule, gradeability
#          floor, placement budget, pose count and seed — so exactly ONE variable moves, plus one stated
#          budget change (`max_pairs`), and neither was chosen on an answer;
#      (c) the artifact reports both scopes side by side and never merges them.
# =========================================================================================================
LBD_REFERENCE_MODEL = PD.STATIC_MODEL["NR4A3"]      # results/nr4a3-matrix/nr4a3-opened.pdb — COMMITTED
LBD_MIN_REF_COVERAGE = 0.60                         # = PREREG.pair_formation.alignment_coverage_min
LBD_MIN_WINDOW_LEN = MIN_DOMAIN_LEN                 # = C16's floor, so the two scopes' floors are the same
LBD_MAX_PAIRS = 20                                  # the ONE budget change — PREREG_LBD.pair_formation

_LBD_INHERITED = ("statistic", "gradeability", "readout", "not_claimed")

PREREG_LBD = {
    "_frozen": "Design fixed before any model was trimmed under this rule and before any statistic under "
               "it existed. Mode `plan --scope lbd` emits this block with no results at all, so git "
               "history carries the design ahead of the numbers — the same discipline `C16`'s run used.",
    "_configuration_id": "C24",
    "⛔_this_is_not_a_widening_of_C16": (
        "`C16` (largest contiguous pLDDT >= 70 run, min 120 residues) is a PRE-REGISTERED choice and it "
        "STANDS. It is not edited, not re-reduced, not superseded and not quoted less. Relaxing it to "
        "admit C397 after seeing that C397 fell outside it would be precisely the outcome-tuning the "
        "pre-registration exists to prevent, and `C16`'s own artifact refuses it in those words. This is "
        "a SECOND run under a DIFFERENT scope, published as a separate file, and the two are reported "
        "side by side and never merged."),
    "question": "Same question as `C16`, asked over the region of the fold the categorical screen actually "
                "interrogates: how often does an ARBITRARY close human paralogue pair, pushed through the "
                "identical categorical pipeline over its LIGAND-BINDING DOMAIN, return P(paralogue also "
                "labelled | target-unique cysteine labelled) = 0 at the 12-backbone-atom design gate?",
    "★_what_this_scope_is_FOR": (
        "The categorical screen is a screen over the LIGAND-BINDING DOMAIN. Everything it does happens "
        "there: the E3 placements are built around a cavity of the LBD, the frozen site definition `C5` is "
        "an LBD lining set (NR4A3 Pocket-5, span 406-534) mapped onto each structure by alignment, and "
        "every cysteine the screen adjudicates — the committed unique set {397, 420, 559} and every "
        "paralogue cysteine they are compared against — is an LBD cysteine. A scope for this screen is "
        "therefore THE LBD, taken as the same structural region in every protein. That is a statement "
        "about what the instrument is pointed at. It is not a statement about what any protein will "
        "return, and no collision statistic, percentile or decoy answer appears anywhere in this rule."),
    "★_the_defect_in_C16_this_repairs_is_NOT_C397": (
        "C397 is the visible symptom; the defect underneath it is that a CONFIDENCE criterion is not a "
        "STRUCTURAL one. pLDDT is a per-model property, so 'largest contiguous pLDDT >= 70 run' returns a "
        "DIFFERENT REGION OF THE FOLD in every protein, and the background is then pooled over windows "
        "that are not the same thing. ⚠ MEASURED FROM `C16`'s OWN PLAN FILE, which contains no statistic "
        "of any kind: across the 39 proteins it trimmed the window length runs 122 to 247 residues — a "
        "2.0x spread on a family whose LBD is one conserved ~250-residue fold — and NR4A3's own window is "
        "144. A larger window carries more cysteines, i.e. more opportunity for the screen to fire, so "
        "window size is a confound on the background quite apart from which residues survive. ⚠ And the "
        "criterion REFUSES proteins outright for a confidence dip: 9 of the 48 fetched accessions, "
        "including NR3C1 (the glucocorticoid receptor), NR1D1, NR1D2, NR1I3, NR2E1, NR2E3, NR5A2, NR0B1 "
        "and NR0B2 — all real LBD-bearing human nuclear receptors, excluded by their model's confidence "
        "rather than by anything about their fold."),
    "scope_rule": {
        "name": "reference-anchored LBD window",
        "reference": "the COMMITTED NR4A3 LBD construct — the sequence of "
                     "`results/nr4a3-matrix/nr4a3-opened.pdb`, the very model the committed categorical "
                     "verdict was computed on. Its UniProt span is DERIVED from the file at run time "
                     "(local residue 1 == UniProt 373 via `nr4a3_basin_search.UNIPROT_OFFSET`), never "
                     "typed, and is recorded in the plan.",
        "procedure": "for EVERY protein, including NR4A3 and including every decoy: (1) SMITH-WATERMAN "
                     "LOCAL alignment of the AlphaFold model's sequence to the reference, using the SAME "
                     "BLOSUM62 matrix and the SAME affine gap penalties (open -11, extend -1) as the "
                     "frozen `nr4a_differential_atlas.nw_align`; (2) the window is the residue-number SPAN "
                     "[first, last] of the model residues aligned to a reference position; (3) the model "
                     "is trimmed to that span by the same `trim_pdb_text` the other scope uses.",
        "why_local_and_not_global": "the query is a full-length chain and the reference is one domain. A "
                                    "GLOBAL aligner pays end-gap penalties proportional to the query's "
                                    "length — 919 residues for AR against a 254-residue reference — which "
                                    "is the wrong instrument for 'find this domain inside this protein'. "
                                    "Local alignment is the textbook answer and adds no threshold.",
        "refusals": {
            "reference_coverage_min": LBD_MIN_REF_COVERAGE,
            "min_window_len": LBD_MIN_WINDOW_LEN,
            "rule": "a protein is REFUSED, with its reason recorded, if fewer than "
                    f"{LBD_MIN_REF_COVERAGE:.2f} of the reference's residues align (the LBD is not "
                    f"confidently locatable in it) or the window is shorter than {LBD_MIN_WINDOW_LEN} "
                    "residues. Both numbers are BORROWED, not invented: the coverage floor is the "
                    "pair-formation coverage floor `C16` already uses, and the length floor is `C16`'s own "
                    "`MIN_DOMAIN_LEN`, so the two scopes' floors are the same numbers.",
        },
        "⭑_no_confidence_criterion_at_all": "pLDDT does not enter this scope. It is REPORTED per window "
                                            "(mean, and the fraction of residues at >= 70) as an "
                                            "observable, so a reader can see exactly what `C16` would have "
                                            "removed and judge the models for themselves — but it decides "
                                            "nothing. ⚠ That is a real cost and it is stated: this scope "
                                            "admits lower-confidence residues than `C16` does, in the "
                                            "decoys exactly as in NR4A3.",
        "⚠_the_reference_is_NR4A3s_own_LBD_and_that_is_asymmetric": (
            "NR4A3 aligns to the reference at identity 1.000 and coverage 1.000, so it gets the most "
            "complete window; a decoy's window is the region homologous to it. That asymmetry is the "
            "SAME construction `C5` already uses — NR4A3's Pocket-5 lining mapped onto each structure by "
            "alignment — one level up, and it is what makes the region MATCHED rather than merely "
            "similarly-sized. ⚠ Its direction is conservative for the headline: the most complete window "
            "carries the most cysteines, hence the most opportunity for the screen to fire on NR4A3 "
            "itself, so it makes NR4A3's own zero HARDER to obtain, not easier."),
    },
    "_held_identical_to_C16": {
        "_what": "everything except the scope rule and one stated budget. Listed so a reader can check "
                 "rather than trust.",
        "gate_atoms": GATE, "also_reported": list(LENGTHS),
        "exposure_cutoff_EXPOSED_RSA": EXPOSED_RSA,
        "identity_band": PREREG["pair_formation"]["identity_band"],
        "alignment_coverage_min": PREREG["pair_formation"]["alignment_coverage_min"],
        "max_per_protein": PREREG["pair_formation"]["max_per_protein"],
        "ranking_rule": PREREG["pair_formation"]["ranking_rule"],
        "orientations": PREREG["pair_formation"]["orientations"],
        "pocket_rule": PREREG["pocket_rule"],
        "universe": PREREG["universe"]["source"],
        "placements": PREREG["placements"],
        "gradeability_min_conditioning_events": PREREG["gradeability"]["min_conditioning_events"],
        "statistic_definition": PREREG["statistic"]["definition"],
        "target_unique_cysteine_rule": PREREG["statistic"]["target_unique_cysteine"],
    },
    "pair_formation": {
        "max_pairs": LBD_MAX_PAIRS,
        "⚠_the_one_budget_change_and_why_it_is_not_tuning": (
            f"`C16` capped selection at 10 pairs and graded 8 rows. A percentile against 8 points has a "
            f"resolution of 1/8 = 0.125 and CANNOT report anything finer — `C16`'s own NR4A3 percentile of "
            f"0.125 is at that floor. Raising the cap to {LBD_MAX_PAIRS} takes MORE OF THE SAME RANKED "
            "LIST under the SAME rule: it is a budget, not a criterion, and it cannot select on an answer "
            "because the ranking is on sequence identity, computed before any statistic exists. ⭑ And it "
            "is CHECKABLE: the greedy selection is deterministic, so the first 10 pairs chosen at a cap of "
            f"{LBD_MAX_PAIRS} are exactly the 10 that a cap of 10 would choose. The reduce therefore "
            "reports the background over the nested top-10 subset ALONGSIDE the full set, and a reader can "
            "see whether widening moved it."),
    },
    "comparability": {
        "★_the_question_this_answers": "a background measured on one structure source against a target "
                                       "measured on another is not a background. This is the check that "
                                       "must pass before any percentile below may be read.",
        "how": "EVERY arm — all decoys and NR4A3 alike — is an AlphaFold DB model of a UniProt accession, "
               "fetched by the same code, trimmed by the same rule to the same structural region, given a "
               "pocket by the same fpocket top-druggability rule, sampled by the same placement sampler at "
               "the same budget with the same seed, and scored by the same reach rule at the same gate. "
               "There is exactly one structure source in this run.",
        "⛔_why_8XTT_IS_NOT_USED_FOR_NR4A3": (
            "8XTT is the experimental NR4A3 NMR ensemble and it has no pLDDT problem at all, so it is the "
            "obvious candidate — and it is REFUSED here, deliberately. The decoys have no experimental "
            "structures; a background measured on AlphaFold models against a target measured on an NMR "
            "ensemble differs from its background in structure source, in conformer count and in whether "
            "hydrogens are present, and any percentile from it would be uninterpretable. The choice was "
            "therefore between changing the target's structure source and changing the trim, and only the "
            "trim can be changed for BOTH arms at once. So the trim is what changed."),
        "⚠_the_price_of_that_choice_stated_plainly": (
            "the NR4A3 row here is an ALPHAFOLD-MODEL row, not the committed opened-model row and not an "
            "8XTT row. It calibrates the SCREEN under one identical rule on one identical structure "
            "source. It is NOT a re-derivation of the committed C397-led verdict, which keeps its own home "
            "in `nr4a-paralogue-dynamics.json` and is quoted here, never recomputed."),
    },
    "readout_additions": {
        "per_unique_cysteine": "⭑ NEW IN THIS SCOPE, and it is what makes a C397 percentile possible at "
                               "all. `C16` reported ONE conditional per ordered row, pooled over that "
                               "target's unique cysteines. This scope ALSO reports the conditional per "
                               "INDIVIDUAL target-unique cysteine — conditioned on placements that reach "
                               "THAT cysteine — for the decoys exactly as for NR4A3, using the same "
                               "gradeability floor. The C397 percentile is taken against the "
                               "cysteine-level background; the pooled row-level percentile is reported "
                               "beside it under the identical rule `C16` used, so the two designs can be "
                               "compared.",
        "both_filters": "as in `C16`: reach-only AND reach-and-exposed. ⛔ THE REACH-ONLY COLUMN IS THE "
                        "LOAD-BEARING ONE — the exposure cutoff is `C7`, which is registered "
                        "KNOWN-DEFECTIVE because it fails its own positive control (NR4A1 C551 at RSA "
                        "0.165, 0 of 25 frames). Both are reported; neither is chosen on its answer.",
        "precondition": "the fraction of ordered decoys with NO target-unique cysteine is re-derived under "
                        "this scope. It is a result in its own right — a pair with no target-unique "
                        "cysteine is one on which this screen could never fire — and `C16` measured it at "
                        "10 of 20.",
    },
    "what_a_favourable_result_licenses": {
        "★_it_licenses": "that the categorical SCREEN fires on NR4A3 more rarely-by-chance than on an "
                         "arbitrary close human paralogue pair, over the LBD, at the 12-atom gate, on "
                         "AlphaFold models, within a nuclear-receptor universe.",
        "⛔_it_does_NOT_license": [
            "binding, affinity or any free energy",
            "reactivity, thiol pKa, nucleophilicity or adduct formation",
            "degradation, efficacy, safety, a therapeutic window or clinical readiness",
            "proteome-wide selectivity — this is a NUCLEAR-RECEPTOR background, not a proteome one",
            "that a linker exists: linker length and exit vector remain conditional on the docked-pose "
            "anchors, i.e. on `R5`. ⭑ Cysteine UNIQUENESS and paralogue BURIAL are pose-independent, "
            "which is the split the categorical audit established and the reason this test is not blocked "
            "by the second-pose-method work.",
        ],
    },
}
# ⚠ MEASURED, NOT ASSUMED (run 30773302930, 2026-08-02 7:56 PM ET): the hard-wired file URL
# `files/AF-{acc}-F1-model_v4.pdb` returned **HTTP 404 for all 48 accessions**, at v4, v3 and v2 alike — so
# the model-version number is not a thing to guess. The DOCUMENTED lookup is the prediction API, which
# returns the current `pdbUrl` for an accession whatever its version; the versioned file URLs stay only as a
# fallback and now span a wider range. `probe` mode prints the raw API answer so a future failure is
# diagnosed rather than re-guessed.
AF_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"
AF_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{v}.pdb"
AF_VERSIONS = (6, 5, 4, 3, 2)


# =========================================================================================================
# SCOPES. `plddt` is the committed `C16` run and its paths are unchanged, byte for byte. `lbd` is `C24`.
# Nothing here is shared state between the two: separate trimmed dirs, separate shard dirs, separate plan
# and result files. A reduce can therefore never mix rows measured under different scopes — which is the
# one failure that would turn two honest tests into one dishonest number.
# =========================================================================================================
SCOPES = {
    "plddt": {
        "slug": "",
        "configuration_id": "C16",
        "label": "largest contiguous pLDDT >= 70 run, min 120 residues (the committed C02 run)",
        "prereg": lambda: PREREG,
        "max_pairs": PREREG["pair_formation"]["max_pairs"],
    },
    "lbd": {
        "slug": "lbd",
        "configuration_id": "C24",
        "label": "reference-anchored LBD window (Smith-Waterman local alignment to the committed NR4A3 "
                 "LBD construct)",
        "prereg": lambda: prereg_lbd(),
        "max_pairs": LBD_MAX_PAIRS,
    },
}


def prereg_lbd():
    """`PREREG_LBD` with the blocks it INHERITS spliced in from `PREREG` by reference, never copied — so a
    reader of either plan file sees the same words and there is exactly one home for each. PURE."""
    out = dict(PREREG_LBD)
    out["_inherited_verbatim_from_the_C16_preregistration"] = {
        "_what": "these blocks are not restated for this scope. They are the SAME objects, read out of "
                 "`PREREG` at emit time, so the two pre-registrations cannot drift apart in wording or in "
                 "value.",
        **{k: PREREG[k] for k in _LBD_INHERITED},
    }
    return out


def set_scope(name):
    """Point every scope-dependent path at `name`. Called once, from `main`, before any mode runs."""
    global SCOPE, OUT, PLAN, SHARD_DIR, TRIMMED_DIR
    if name not in SCOPES:
        raise SystemExit(f"  ABORT: unknown scope {name!r}; known: {sorted(SCOPES)}")
    SCOPE = name
    slug = SCOPES[name]["slug"]
    suffix = f"-{slug}" if slug else ""
    OUT = os.path.join(HERE, f"categorical-decoy-null{suffix}.json")
    PLAN = os.path.join(HERE, f"categorical-decoy-null{suffix}-plan.json")
    SHARD_DIR = os.path.join(CACHE, f"shards{suffix}")
    TRIMMED_DIR = os.path.join(CACHE, f"trimmed{suffix}")
    return SCOPES[name]


def active_prereg():
    return SCOPES[SCOPE]["prereg"]()


# =========================================================================================================
# PURE helpers (unit-tested in tests/test_categorical_decoy_null.py)
# =========================================================================================================
def parse_plddt(pdb_text):
    """[(resSeq, plddt)] in file order, one entry per residue, from an AlphaFold PDB's CA B-factor. PURE."""
    out, seen = [], set()
    for line in pdb_text.splitlines():
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        try:
            rid = int(line[22:26])
            b = float(line[60:66])
        except (ValueError, IndexError):
            continue
        if rid in seen:
            continue
        seen.add(rid)
        out.append((rid, b))
    return out


def largest_confident_segment(plddt, min_plddt=70.0, min_len=120):
    """Largest CONTIGUOUS residue-number run with pLDDT >= min_plddt. Returns (first, last) or None. PURE.

    Contiguity is on the residue NUMBER, so a numbering break also breaks the segment — which is the correct
    behaviour for a domain trim."""
    best, cur = None, None
    prev = None
    for rid, b in plddt:
        ok = b >= min_plddt
        if ok and cur is not None and prev is not None and rid == prev + 1:
            cur[1] = rid
        elif ok:
            cur = [rid, rid]
        else:
            cur = None
        if cur is not None and (best is None or (cur[1] - cur[0]) > (best[1] - best[0])):
            best = list(cur)
        prev = rid
    if best is None or (best[1] - best[0] + 1) < min_len:
        return None
    return (best[0], best[1])


def trim_pdb_text(pdb_text, first, last):
    """Keep ATOM/TER records whose residue number is in [first, last]. PURE (text in, text out)."""
    keep = []
    for line in pdb_text.splitlines():
        if line.startswith(("ATOM", "TER")):
            try:
                rid = int(line[22:26])
            except (ValueError, IndexError):
                continue
            if first <= rid <= last:
                keep.append(line)
    keep.append("END")
    return "\n".join(keep) + "\n"


_SW_NEG = -10 ** 9


def sw_align(seq_a, seq_b, go=-11, ge=-1):
    """SMITH-WATERMAN local alignment with affine gaps. Returns (aln, score) where `aln` is the same
    [(i_a|None, i_b|None), ...] shape `nr4a_differential_atlas.nw_align` returns, over the single
    highest-scoring local segment. PURE.

    WHY THIS IS NEW CODE IN A MODULE WHOSE RULE IS 'IMPORT, NEVER RE-IMPLEMENT'. The repo's frozen aligner
    is GLOBAL (`nw_align`), and `C24`'s scope rule needs to locate ONE DOMAIN INSIDE A FULL-LENGTH CHAIN —
    919 residues of AR against a 254-residue reference. A global aligner charges end gaps proportional to
    the query's length for that, which is the wrong instrument, not a tunable. Two things keep this honest:
    the SUBSTITUTION MATRIX is imported (`ATLAS.blosum`, the same BLOSUM62 every other alignment in this
    program uses) and the GAP PENALTIES are `nw_align`'s own defaults, so nothing scoring-related is new.
    Only the recurrence's zero-floor and the local traceback are.

    ⚠ This function decides SCOPE, never a statistic. No reach, exposure, uniqueness or collision number is
    computed here or downstream of it other than through the window it returns."""
    n, m = len(seq_a), len(seq_b)
    M = [[0] * (m + 1) for _ in range(n + 1)]           # best local alignment ending in a match at (i, j)
    X = [[_SW_NEG] * (m + 1) for _ in range(n + 1)]     # ...ending in a gap in seq_b
    Y = [[_SW_NEG] * (m + 1) for _ in range(n + 1)]     # ...ending in a gap in seq_a
    best, bi, bj = 0, 0, 0
    for i in range(1, n + 1):
        ai = seq_a[i - 1]
        Mi, Mp, Xi, Xp, Yi, Yp = M[i], M[i - 1], X[i], X[i - 1], Y[i], Y[i - 1]
        for j in range(1, m + 1):
            v = max(Mp[j - 1], Xp[j - 1], Yp[j - 1], 0) + ATLAS.blosum(ai, seq_b[j - 1])
            Mi[j] = v if v > 0 else 0
            Xi[j] = max(Mp[j] + go, Xp[j] + ge)
            Yi[j] = max(Mi[j - 1] + go, Yi[j - 1] + ge)
            if Mi[j] > best:
                best, bi, bj = Mi[j], i, j
    aln, i, j, state = [], bi, bj, "M"
    while i > 0 and j > 0:
        if state == "M":
            if M[i][j] == 0:
                break
            aln.append((i - 1, j - 1))
            prev = M[i][j] - ATLAS.blosum(seq_a[i - 1], seq_b[j - 1])
            i -= 1
            j -= 1
            if prev <= 0:
                break
            state = "M" if prev == M[i][j] else ("X" if prev == X[i][j] else "Y")
        elif state == "X":
            aln.append((i - 1, None))
            state = "M" if X[i][j] == M[i - 1][j] + go else "X"
            i -= 1
        else:
            aln.append((None, j - 1))
            state = "M" if Y[i][j] == M[i][j - 1] + go else "Y"
            j -= 1
    aln.reverse()
    return aln, best


def lbd_window(residues, seq, ref_seq):
    """THE `C24` SCOPE RULE. Locate the reference LBD inside one model and return its residue-number span.
    PURE — `residues` is `[(resid, one_letter)]` and `seq` is the matching one-letter string.

    Returns a dict that ALWAYS carries the alignment observables (score, identity, reference coverage,
    window length) whether or not the window is accepted, so a refusal is diagnosable from the artifact
    rather than only from a message."""
    aln, score = sw_align(seq, ref_seq)
    cols = [(i, j) for i, j in aln if i is not None and j is not None]
    ref_cov = (len(cols) / len(ref_seq)) if ref_seq else 0.0
    out = {"sw_score": score, "n_aligned_columns": len(cols),
           "reference_coverage": round(ref_cov, 4),
           "identity_to_reference": (round(sum(1 for i, j in cols if seq[i] == ref_seq[j]) / len(cols), 4)
                                     if cols else 0.0)}
    if not cols:
        out.update(accepted=False, reason="Smith-Waterman found no local alignment to the reference")
        return out
    rids = [residues[i][0] for i, _j in cols]
    first, last = min(rids), max(rids)
    out.update(first=first, last=last, window_len=last - first + 1)
    if ref_cov < LBD_MIN_REF_COVERAGE:
        out.update(accepted=False,
                   reason=f"reference coverage {ref_cov:.3f} < {LBD_MIN_REF_COVERAGE} — the reference LBD "
                          f"is not confidently locatable in this chain")
        return out
    if out["window_len"] < LBD_MIN_WINDOW_LEN:
        out.update(accepted=False,
                   reason=f"window {out['window_len']} residues < {LBD_MIN_WINDOW_LEN}")
        return out
    out["accepted"] = True
    return out


def plddt_profile(plddt, first, last):
    """What `C16` WOULD have seen inside a `C24` window — reported as an observable, never as a criterion.
    PURE. Returns None when the window holds no CA record (which is itself worth seeing)."""
    xs = [b for rid, b in plddt if first <= rid <= last]
    if not xs:
        return None
    return {"n_residues_with_plddt": len(xs), "mean_plddt": round(sum(xs) / len(xs), 2),
            "min_plddt": round(min(xs), 2), "max_plddt": round(max(xs), 2),
            "frac_at_or_above_70": round(sum(1 for b in xs if b >= MIN_PLDDT) / len(xs), 4),
            "_reading": "REPORTED, NOT APPLIED. `C24` has no confidence criterion; this is here so a reader "
                        "can see exactly which residues `C16` would have removed and judge the models "
                        "rather than take the scope on trust."}


def alignment_identity(seq_a, seq_b, aln):
    """(identity, coverage) over an `ATLAS.nw_align` pairing. identity = matched positions / aligned columns;
    coverage = aligned columns / len(shorter sequence). PURE."""
    cols = [(i, j) for i, j in aln if i is not None and j is not None]
    if not cols:
        return 0.0, 0.0
    same = sum(1 for i, j in cols if seq_a[i] == seq_b[j])
    shorter = min(len(seq_a), len(seq_b)) or 1
    return same / len(cols), len(cols) / shorter


def select_pairs(entries, ref_identity, band, coverage_min, max_pairs, max_per_protein):
    """THE PRE-REGISTERED PAIR SELECTION. PURE.

    `entries`: [{"a","b","identity","coverage"}] for every unordered candidate pair.
    Returns (selected, rejected) — selected in ranked order, each carrying why it was kept."""
    lo, hi = band
    qualifying, rejected = [], []
    for e in entries:
        why = None
        if not (lo <= e["identity"] <= hi):
            why = f"identity {e['identity']:.3f} outside band [{lo}, {hi}]"
        elif e["coverage"] < coverage_min:
            why = f"alignment coverage {e['coverage']:.3f} < {coverage_min}"
        if why:
            rejected.append({**e, "rejected_because": why})
        else:
            qualifying.append(e)
    qualifying.sort(key=lambda e: (abs(e["identity"] - ref_identity), e["a"], e["b"]))
    used, selected = {}, []
    for e in qualifying:
        if len(selected) >= max_pairs:
            break
        if used.get(e["a"], 0) >= max_per_protein or used.get(e["b"], 0) >= max_per_protein:
            continue
        used[e["a"]] = used.get(e["a"], 0) + 1
        used[e["b"]] = used.get(e["b"], 0) + 1
        selected.append({**e, "rank_key": round(abs(e["identity"] - ref_identity), 5)})
    return selected, rejected


def window_spread(trimmed):
    """The scope's own size distribution. PURE.

    ⭑ THIS IS A DESIGN OBSERVABLE, NOT A RESULT — it is computed from the trim alone, before any placement
    is sampled, and it is what makes 'is this scope MATCHED across proteins?' answerable instead of
    assumed. `C16`'s own plan file records 122-247 residues over 39 proteins."""
    ns = sorted(v["n_residues"] for v in trimmed.values() if v.get("n_residues"))
    if not ns:
        return None
    return {"n_proteins": len(ns), "min": ns[0], "median": ns[len(ns) // 2], "max": ns[-1],
            "max_over_min": round(ns[-1] / ns[0], 3) if ns[0] else None,
            "_reading": "a scope whose windows differ by a large factor is not one structural region "
                        "measured in many proteins; it is many regions pooled. Window size drives how many "
                        "cysteines the screen can see, so it is a confound on the background."}


def nr4a3_scope_check(trimmed, scope=None):
    """⛔ WHICH NR4A3-UNIQUE CYSTEINES THIS SCOPE CAN SEE — measured from the trim, not narrated.

    ★ ONE HOME. The reduce and the plan both call this, so the plan cannot promise a window the reduce then
    contradicts. Written for `C16` after its harness was found not to score C397; kept as the standing
    check every scope must pass before any percentile under it is readable."""
    scope = scope or SCOPE
    tr = (trimmed or {}).get(NR4A3_ACC) or {}
    lo, hi = tr.get("first"), tr.get("last")
    inside = [c for c in sorted(PD.NR4A3_UNIQUE_CYS) if lo is not None and lo <= c <= hi]
    outside = [c for c in sorted(PD.NR4A3_UNIQUE_CYS) if c not in inside]
    out = {
        "scope": scope,
        "configuration_id": SCOPES.get(scope, {}).get("configuration_id"),
        "trimmed_window_uniprot": [lo, hi],
        "n_residues": tr.get("n_residues"),
        "committed_nr4a3_unique_cysteines": sorted(PD.NR4A3_UNIQUE_CYS),
        "inside_the_trimmed_window": inside,
        "⛔_outside_and_therefore_INVISIBLE_to_this_harness": outside,
        "headline_residue_C397_in_scope": 397 in inside,
    }
    if outside:
        out["★_reading"] = (
            f"This scope keeps UniProt {lo}-{hi} of the NR4A3 AlphaFold model, so of the committed unique "
            f"set {sorted(PD.NR4A3_UNIQUE_CYS)} only {inside} is inside it. ⛔ THE HARNESS-MATCHED NR4A3 ROW "
            f"THEREFORE DOES NOT INTERROGATE THE PROGRAM'S HEADLINE C397 — it interrogates {inside}. The "
            "percentile still answers the question it was built to answer (does an arbitrary close "
            "paralogue pair, under this IDENTICAL rule, return 0?), because NR4A3 goes through the same "
            "rule as every decoy. But it is a statement about the SCREEN, and it is a weaker statement "
            "about the program's actual construct than it would be with C397 in the window. The committed "
            "C397-led result keeps its own home in nr4a-paralogue-dynamics.json and is NOT re-derived here.")
        out["_why_the_trim_is_not_relaxed_after_the_fact"] = (
            "It is pre-registered. Widening it to admit C397 AFTER seeing that C397 fell outside would be "
            "exactly the tuning the pre-registration exists to prevent. The honest move is to report the "
            "scope and, if it matters, re-run with a DIFFERENT pre-registered trim as a separate test.")
    else:
        out["★_reading"] = (
            f"✅ Every committed NR4A3-unique cysteine {sorted(PD.NR4A3_UNIQUE_CYS)} is inside this scope's "
            f"window (UniProt {lo}-{hi}), C397 included. A percentile from this run therefore CAN be quoted "
            "for the program's headline residue — with every other caveat this artifact carries still "
            "attached, and with the reminder that this is an ALPHAFOLD-MODEL row, not the committed "
            "opened-model row and not an 8XTT row.")
    return out


def percentile_of(value, background):
    """Fraction of `background` <= `value`. PURE. None if the background is empty."""
    xs = [b for b in background if b is not None]
    if not xs:
        return None
    return sum(1 for b in xs if b <= value) / len(xs)


def summarise_background(rows, key):
    """Distribution summary of a graded background column. PURE."""
    xs = sorted(r[key] for r in rows if r.get(key) is not None)
    if not xs:
        return None
    n = len(xs)

    def q(p):
        if n == 1:
            return xs[0]
        k = p * (n - 1)
        lo = int(math.floor(k))
        hi = min(lo + 1, n - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)
    n_zero = sum(1 for x in xs if x == 0.0)
    return {"n": n, "min": xs[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": xs[-1],
            "mean": sum(xs) / n, "n_exactly_zero": n_zero,
            "frac_exactly_zero": n_zero / n,
            # ⭑ ADDED 2026-08-03, and it is not decoration. `frac_exactly_zero` IS the headline of this
            #   whole exercise — "how often does an arbitrary close paralogue pair produce the same
            #   0-collision answer?" — and it was being reported as a bare point estimate over a
            #   single-digit n. A point estimate with no interval invites exactly the over-reading this
            #   module exists to prevent. Uses the SAME `PD.wilson95` as every other interval here.
            "frac_exactly_zero_wilson95": PD.wilson95(n_zero, n),
            "percentile_resolution": 1.0 / n,
            "★_what_this_n_can_and_cannot_exclude": what_n_excludes(n, n_zero)}


def what_n_excludes(n, n_zero):
    """★ THE POWER STATEMENT, written next to the number rather than left to the reader. PURE.

    A background of n points supports exactly two kinds of statement, and being explicit about which is
    which matters because the second is the one that gets over-read:
      * a Wilson 95 % interval on the background's zero-rate — outside it is excluded, inside it is not;
      * a percentile whose RESOLUTION is 1/n and which cannot report anything finer however extreme the
        target is. ⚠ `C16`'s NR4A3 percentile of 0.125 sat exactly at that floor at n = 8, so it carried
        no information about how far below the background NR4A3 actually was — the number was a statement
        about n as much as about NR4A3.
    """
    if not n:
        return None
    lo, hi = PD.wilson95(n_zero, n)
    return {
        "n_graded": n, "n_exactly_zero": n_zero,
        "zero_rate_wilson95": [lo, hi],
        "CAN_exclude": f"a true background zero-rate outside [{lo:.3f}, {hi:.3f}] at 95 %",
        "CANNOT_exclude": (f"any zero-rate inside [{lo:.3f}, {hi:.3f}] — at n = {n} that interval is wide, "
                           "and two backgrounds differing by less than its width are indistinguishable "
                           "here"),
        "CANNOT_report": (f"a percentile finer than {1.0 / n:.4f} (= 1/n). A target that beats every "
                          f"background point still reports {1.0 / n:.4f} if one point ties it, so a "
                          "percentile sitting at that floor is a statement about n as much as about the "
                          "target"),
        "⚠_effective_n": "the points are not fully independent — see the clustering note beside whichever "
                         "background this summarises — so the interval above is, if anything, optimistic.",
    }


# =========================================================================================================
# I/O: the universe and the AlphaFold models
# =========================================================================================================
def universe():
    """The decoy universe, read from the COMMITTED superfamily artifact. Never hand-typed."""
    d = json.load(open(UNIVERSE_SRC))
    seen, out = set(), []
    for r in d.get("ranking", []):
        acc, gene = r.get("accession"), r.get("gene")
        if not acc or acc in seen:
            continue
        seen.add(acc)
        out.append({"gene": gene, "accession": acc,
                    "in_nr4a_family": acc in NR4A_FAMILY})
    return out


def af_path(acc):
    return os.path.join(AF_DIR, f"AF-{acc}.pdb")


def _af_urls(acc, timeout=60):
    """Candidate model URLs for one accession, API answer FIRST. Returns (urls, api_note)."""
    urls, note = [], None
    try:
        with urllib.request.urlopen(AF_API.format(acc=acc), timeout=timeout) as fh:
            recs = json.loads(fh.read().decode())
        for r in (recs if isinstance(recs, list) else [recs]):
            for key in ("pdbUrl", "cifUrl"):
                if r.get(key) and str(r[key]).endswith(".pdb"):
                    urls.append(r[key])
        note = f"api ok, {len(urls)} pdb url(s)"
    except Exception as ex:  # noqa: BLE001
        note = f"api unusable: {type(ex).__name__}: {ex}"
    urls += [AF_URL.format(acc=acc, v=v) for v in AF_VERSIONS]
    return urls, note


def fetch_af(acc, timeout=120):
    """Download one AlphaFold model. Returns metadata; raises on total failure, carrying EVERY URL tried and
    its error, so a repeat of the 2026-08-02 all-404 failure is diagnosed from the artifact instead of
    re-guessed."""
    os.makedirs(AF_DIR, exist_ok=True)
    dest = af_path(acc)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        text = open(dest).read()
        return {"accession": acc, "path": os.path.relpath(dest, REPO), "cached": True,
                "sha256": hashlib.sha256(text.encode()).hexdigest()[:16],
                "model_version": _recorded_version(dest)}
    urls, api_note = _af_urls(acc)
    tried = []
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as fh:
                text = fh.read().decode()
            if "ATOM" not in text:
                raise ValueError("no ATOM records")
            with open(dest, "w") as out:
                out.write(f"REMARK   1 SOURCE {url}\n")
                out.write(text)
            return {"accession": acc, "path": os.path.relpath(dest, REPO), "cached": False,
                    "model_version": _recorded_version(dest), "url": url, "api": api_note,
                    "sha256": hashlib.sha256(text.encode()).hexdigest()[:16]}
        except Exception as ex:  # noqa: BLE001
            tried.append(f"{url} -> {type(ex).__name__}: {ex}")
    raise RuntimeError(f"AlphaFold fetch failed for {acc} [{api_note}]; tried: " + " | ".join(tried))


def mode_probe(args):
    """$0 diagnostic. Print the RAW AlphaFold API answer for one accession + one file-URL attempt, so a fetch
    failure is root-caused from evidence rather than by trying version numbers (CLAUDE.md §4)."""
    acc = os.environ.get("PROBE_ACC", NR4A1_ACC)
    try:
        with urllib.request.urlopen(AF_API.format(acc=acc), timeout=60) as fh:
            body = fh.read().decode()
        print(f"  [cdn] API {AF_API.format(acc=acc)} -> {len(body)} bytes")
        print("  [cdn] " + body[:1200])
    except Exception as ex:  # noqa: BLE001
        print(f"  [cdn] API FAILED: {type(ex).__name__}: {ex}")
    for v in AF_VERSIONS:
        url = AF_URL.format(acc=acc, v=v)
        try:
            with urllib.request.urlopen(url, timeout=60) as fh:
                n = len(fh.read())
            print(f"  [cdn] FILE {url} -> OK ({n} bytes)")
        except Exception as ex:  # noqa: BLE001
            print(f"  [cdn] FILE {url} -> {type(ex).__name__}: {ex}")
    return {}


def _recorded_version(path):
    with open(path) as fh:
        head = fh.readline()
    for v in AF_VERSIONS:
        if f"model_v{v}" in head:
            return v
    return None


def trimmed_path(acc):
    return os.path.join(TRIMMED_DIR, f"{acc}-domain.pdb")


def lbd_reference():
    """The `C24` reference: sequence + DERIVED UniProt span of the committed NR4A3 LBD construct. The span
    is read off the file (local id + `nr4a3_basin_search.UNIPROT_OFFSET`), never typed."""
    m = B.load_paralogue(LBD_REFERENCE_MODEL)
    rids = [r for r, _aa in m["residues"]]
    return {"seq": m["seq"], "path": os.path.relpath(LBD_REFERENCE_MODEL, REPO),
            "n_residues": len(rids),
            "uniprot_span": [min(rids) + B.UNIPROT_OFFSET, max(rids) + B.UNIPROT_OFFSET],
            "uniprot_offset": B.UNIPROT_OFFSET,
            "cysteines_uniprot": sorted(r + B.UNIPROT_OFFSET for r, aa in m["residues"] if aa == "C")}


def trim_one(acc, min_plddt=70.0, min_len=120, ref_seq=None):
    """Trim one fetched model to this SCOPE's window. Returns metadata or raises.

    `plddt` (`C16`): the largest contiguous pLDDT >= min_plddt run.
    `lbd`   (`C24`): the reference-anchored LBD window — see `PREREG_LBD.scope_rule`.
    """
    os.makedirs(TRIMMED_DIR, exist_ok=True)
    text = open(af_path(acc)).read()
    out = trimmed_path(acc)
    if SCOPE == "lbd":
        if not ref_seq:
            raise ValueError("the lbd scope needs the reference sequence")
        full = B.load_paralogue(af_path(acc))
        win = lbd_window(full["residues"], full["seq"], ref_seq)
        if not win.get("accepted"):
            raise ValueError(win.get("reason", "no LBD window"))
        first, last = win["first"], win["last"]
        extra = {"scope_alignment": {k: v for k, v in win.items() if k != "accepted"},
                 "plddt_in_window_REPORTED_NOT_APPLIED": plddt_profile(parse_plddt(text), first, last)}
    else:
        seg = largest_confident_segment(parse_plddt(text), min_plddt, min_len)
        if seg is None:
            raise ValueError(f"no contiguous pLDDT>={min_plddt} segment of >= {min_len} residues")
        first, last = seg
        extra = {}
    with open(out, "w") as fh:
        fh.write(trim_pdb_text(text, first, last))
    model = B.load_paralogue(out)
    return {"accession": acc, "first": first, "last": last, "n_residues": len(model["residues"]),
            "path": os.path.relpath(out, REPO), "seq_len": len(model["seq"]), **extra}


# =========================================================================================================
# The pipeline for ONE ordered decoy — every scientific step imported, none re-implemented
# =========================================================================================================
def fpocket_top_pocket(pdb_path, workroot):
    """The pre-registered pocket rule: fpocket's HIGHEST-DRUGGABILITY cavity. Returns its lining residues
    (structure numbering) + druggability. Raises if fpocket cannot run — recorded as a refusal, never as an
    empty pocket."""
    import shutil
    import subprocess
    import tempfile
    import nr4a3_structure as NS
    d = tempfile.mkdtemp(prefix="cdn_fp_", dir=workroot)
    try:
        local = os.path.join(d, "prot.pdb")
        shutil.copyfile(pdb_path, local)
        subprocess.run(["fpocket", "-f", local], check=True, capture_output=True, text=True, timeout=900)
        resids_by_num, info = NS.pocket_residues_by_number(os.path.join(d, "prot_out"), "prot")
        best = max(info.items(), key=lambda kv: (kv[1].get("druggability") or 0.0))
        num = best[0]
        return {"pocket_number": num, "druggability": best[1].get("druggability"),
                "alpha_spheres": best[1].get("alpha_spheres"),
                "residues": sorted(int(r) for r in resids_by_num.get(num, [])),
                "n_pockets": len(info)}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def pocket_centroid_of(model, pocket_residues):
    """Side-chain centroid of the pocket lining — the SAME construction the committed lane uses to place the
    warhead exit-vector poses (`nr4a_paralogue_dynamics.sample_transfer_anchors`)."""
    side = []
    for rid in pocket_residues:
        for a in model["atoms_by_res"].get(rid, []):
            if a["name"] not in B.BACKBONE:
                side.append((a["x"], a["y"], a["z"]))
    if not side:
        raise ValueError("pocket lining has no side-chain atoms in this model")
    return G.centroid(side)


def registry_params(registry_path):
    """The SAME parameter override the committed lane applies from the observed 9UUM geometry."""
    reg = json.load(open(registry_path))
    e2 = reg.get("e2_geometry") or {}
    params = dict(B.PARAMS)
    cal = (e2.get("substrate_lysine_calibration") or {})
    if cal.get("nearest_lysine_to_catalytic_cys_A"):
        params["lysine_transfer_A"] = cal["nearest_lysine_to_catalytic_cys_A"]
    if e2.get("measured"):
        params["ring_to_e2_cys_A"] = e2["ring_to_catalytic_cys_A"]
    return reg, params


_UNIT_CTX = {}


def _sample_unit(job):
    """One (arm, pose) sampling unit. Reads the fork-inherited context so nothing heavy is pickled INTO the
    worker; only the accepted placements come back. Each unit carries its OWN seed derived from the base
    seed and the unit index, so the placement set is DETERMINISTIC and independent of the process count."""
    aid, pose_i, n_samples, seed = job
    ctx = _UNIT_CTX
    arm = ctx["arms"][aid]
    pose = ctx["poses"][pose_i]
    rng = random.Random(seed)
    pls, _stats = B.sample_placements(arm, pose, ctx["field"], rng, n_samples, ctx["params"])
    at = tuple(pose["anchor_xyz"])
    return [{"arm": aid, "pose": pose["pose_id"], "xyz": pl["tanchor"], "a_t": at, "a_e": pl["anchor_e3"]}
            for pl in pls if pl.get("tanchor")]


def sample_anchors(model, pocket_residues, registry_path, n_poses, seed, n_samples, nproc=None):
    """Sample E3 placements on ONE target, EXACTLY as `nr4a_paralogue_dynamics.sample_transfer_anchors`
    does — same arms, same pose construction, same sampler, same params. Two differences, both stated:
      (1) the pocket comes from the PRE-REGISTERED fpocket rule rather than NR4A3's hard-wired Pocket-5;
      (2) the (arm x pose) units are independently seeded so they can run in parallel. Engineering is free
          and a CI runner has more than one core; the result is deterministic either way.
    Returns (anchors, per_arm, params, n_arm_pose, n_poses, centroid)."""
    reg, params = registry_params(registry_path)
    centroid = pocket_centroid_of(model, pocket_residues)
    field = G.SquaredDistanceField(model["heavy_xyz"], cell=0.9, clamp=8.0)
    poses = B.build_pose_ensemble(model, {"pocket_centroid": centroid}, field, n_poses,
                                  random.Random(seed))
    arms = {}
    for aid, rec in reg.get("arms", {}).items():
        if rec.get("status") != "OK":
            continue
        arm = B.load_arm_from_registry(rec)
        if arm.get("tanchor"):
            arms[aid] = arm
    jobs = [(aid, i, n_samples, seed * 1000003 + k)
            for k, (aid, i) in enumerate((a, i) for a in sorted(arms) for i in range(len(poses)))]
    _UNIT_CTX.update(arms=arms, poses=poses, field=field, params=params)
    nproc = int(os.environ.get("DECOY_NPROC", nproc or (os.cpu_count() or 1)))
    if nproc > 1 and len(jobs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(nproc, len(jobs))) as pool:
            chunks = pool.map(_sample_unit, jobs)
    else:
        chunks = [_sample_unit(j) for j in jobs]
    anchors, per_arm = [], {}
    for (aid, _i, _n, _s), got in zip(jobs, chunks):
        anchors.extend(got)
        per_arm.setdefault(aid, {"recruiter": arms[aid]["recruiter"],
                                 "n_accepted_with_transfer_anchor": 0})
        per_arm[aid]["n_accepted_with_transfer_anchor"] += len(got)
    return anchors, per_arm, params, len(jobs), len(poses), centroid


def cysteines_in_frame(path, ref_model=None, aligned_partner=None):
    """Every cysteine with an SG, with RSA, in the REFERENCE frame.

    `ref_model is None` -> the protein IS the reference (no superposition).
    `ref_model` given   -> `B.superpose_paralogue` into that frame, exactly as the committed lane does.
    `aligned_partner`   -> a model to align against so `partner_has_cys_here` can be filled (the
                           target-unique rule). Uses `PD.align_map`, the same BLOSUM62 NW aligner."""
    model = B.load_paralogue(path)
    frame = model if ref_model is None else B.superpose_paralogue(model, ref_model)
    residues, atoms = ATLAS.parse_pdb(path)
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    m2p = PD.align_map(model, aligned_partner) if aligned_partner is not None else {}
    p_aa = aligned_partner["aa_of"] if aligned_partner is not None else {}
    out = []
    for rid, aa in frame["residues"]:
        if aa != "C":
            continue
        for a in frame["atoms_by_res"].get(rid, []):
            if a["name"] != "SG":
                continue
            dev = frame.get("deviation_by_res", {}).get(rid) if ref_model is not None else 0.0
            pr = m2p.get(rid)
            out.append({"label": f"C{rid}", "local_resid": rid, "xyz": (a["x"], a["y"], a["z"]),
                        "rsa": round(rsa.get(rid, 0.0), 4),
                        "partner_aligned_resid": pr,
                        "partner_has_cys_here": (p_aa.get(pr) == "C") if pr is not None else False,
                        "fit_deviation_A": (round(dev, 2) if dev is not None else None)})
            break
    sup = frame["superposition"] if ref_model is not None else None
    return out, sup, model


def ordered_decoy_statistic(anchors, target_cys, para_cys, params):
    """THE STATISTIC. With one conformer per species `categorical_verdict`'s f3/fP are 0/1 indicators, so the
    conditional reduces exactly to (# placements hitting BOTH) / (# placements hitting a target-unique Cys).
    Uses `PD.matched_reach_hits_multi` — the committed prolate-spheroid reach rule, not a new one."""
    unique = [c for c in target_cys if not c["partner_has_cys_here"]]
    res = {"n_target_cysteines": len(target_cys), "n_target_unique_cysteines": len(unique),
           "target_unique_labels": [c["label"] for c in unique],
           "n_paralogue_cysteines": len(para_cys), "n_placements": len(anchors), "by_linker_atoms": {}}
    if not unique:
        res["status"] = "UNDEFINED_no_target_unique_cysteine"
        return res
    for tag, min_rsa in (("", 0.0), ("_EXPOSED", EXPOSED_RSA)):
        u_hits = PD.matched_reach_hits_multi(anchors, unique, LENGTHS, params=params, min_rsa=min_rsa)
        p_hits = PD.matched_reach_hits_multi(anchors, para_cys, LENGTHS, params=params, min_rsa=min_rsa)
        for n in LENGTHS:
            uh, uper = u_hits[n]
            ph, pper = p_hits[n]
            den = sum(uh)
            coll = sum(1 for i in range(len(anchors)) if uh[i] and ph[i])
            cell = res["by_linker_atoms"].setdefault(str(n), {})
            cell[f"n_conditioning_events{tag}"] = int(den)
            cell[f"n_collisions{tag}"] = int(coll)
            cell[f"P_paralogue_also_labelled{tag}"] = (coll / den) if den else None
            cell[f"P_paralogue_also_labelled{tag}_wilson95"] = PD.wilson95(coll, den) if den else None
            cell[f"mean_P_target_unique{tag}"] = (den / len(anchors)) if anchors else None
            cell[f"mean_P_any_paralogue_cys{tag}"] = (sum(ph) / len(anchors)) if anchors else None
            cell[f"per_target_unique_cys{tag}"] = {k: v for k, v in uper.items() if v}
            cell[f"per_paralogue_cys{tag}"] = {k: v for k, v in pper.items() if v}
    gate = res["by_linker_atoms"][str(GATE)]
    n_ev = gate["n_conditioning_events"]
    res["status"] = ("GRADED" if n_ev >= PREREG["gradeability"]["min_conditioning_events"]
                     else "UNDERPOWERED_too_few_conditioning_events")
    res["gate_atoms"] = GATE
    res["P_gate"] = gate["P_paralogue_also_labelled"]
    res["P_gate_EXPOSED"] = gate["P_paralogue_also_labelled_EXPOSED"]
    res["n_conditioning_events_gate"] = n_ev
    res["per_unique_cysteine"] = per_cysteine_statistic(anchors, unique, para_cys, params)
    return res


def per_cysteine_statistic(anchors, unique, para_cys, params):
    """★ THE CYSTEINE-LEVEL CONDITIONAL — one row per INDIVIDUAL target-unique cysteine.

    `ordered_decoy_statistic` pools a target's unique cysteines into one conditional, which is the design
    `C16` used and it is kept unchanged. But a pooled row cannot answer *"what is the background for THIS
    residue?"* — and that is the whole question for NR4A3's C397. So each unique cysteine also gets its own
    conditional, conditioned on the placements that reach THAT cysteine, using the SAME
    `PD.matched_reach_hits_multi`, the SAME gate and the SAME gradeability floor. Decoys and NR4A3 alike.

    ⚠ These rows are NOT independent of each other: two cysteines of one target share a placement set and can
    be reached by the same placement. The reduce says so where it uses them."""
    floor = PREREG["gradeability"]["min_conditioning_events"]
    out = {}
    p_hits = {tag: PD.matched_reach_hits_multi(anchors, para_cys, LENGTHS, params=params, min_rsa=rsa)
              for tag, rsa in (("", 0.0), ("_EXPOSED", EXPOSED_RSA))}
    for c in unique:
        row = {"rsa": c.get("rsa"), "by_linker_atoms": {}}
        for tag, min_rsa in (("", 0.0), ("_EXPOSED", EXPOSED_RSA)):
            u = PD.matched_reach_hits_multi(anchors, [c], LENGTHS, params=params, min_rsa=min_rsa)
            for n in LENGTHS:
                uh = u[n][0]
                ph = p_hits[tag][n][0]
                den = sum(uh)
                coll = sum(1 for i in range(len(anchors)) if uh[i] and ph[i])
                cell = row["by_linker_atoms"].setdefault(str(n), {})
                cell[f"n_conditioning_events{tag}"] = int(den)
                cell[f"n_collisions{tag}"] = int(coll)
                cell[f"P_paralogue_also_labelled{tag}"] = (coll / den) if den else None
                cell[f"P_paralogue_also_labelled{tag}_wilson95"] = PD.wilson95(coll, den) if den else None
        g = row["by_linker_atoms"][str(GATE)]
        row["n_conditioning_events_gate"] = g["n_conditioning_events"]
        row["P_gate"] = g["P_paralogue_also_labelled"]
        row["P_gate_EXPOSED"] = g["P_paralogue_also_labelled_EXPOSED"]
        row["status"] = ("GRADED" if g["n_conditioning_events"] >= floor
                         else "UNDERPOWERED_too_few_conditioning_events")
        out[c["label"]] = row
    return out


# =========================================================================================================
# modes
# =========================================================================================================
def mode_plan(args):
    """$0, no network. Emit the pre-registration on its own so the design is committed BEFORE any number."""
    os.makedirs(CACHE, exist_ok=True)
    uni = universe()
    sc = SCOPES[SCOPE]
    title = ("C02 — cross-system decoy null for the categorical covalent axis: PRE-REGISTRATION"
             if SCOPE == "plddt" else
             "C02-L — cross-system decoy null over the REFERENCE-ANCHORED LBD WINDOW: PRE-REGISTRATION. "
             "A SECOND, INDEPENDENT scope, not a widening of C02's")
    plan = {
        "_title": title,
        "_status": "PRE-REGISTRATION ONLY. No structure has been fetched and no statistic computed at the "
                   "time this file is written.",
        "_scope": {"name": SCOPE, "configuration_id": sc["configuration_id"], "rule": sc["label"],
                   "sibling_scopes": {k: v["configuration_id"] for k, v in SCOPES.items() if k != SCOPE},
                   "⛔": "the two scopes are separate tests with separate artifacts. Neither supersedes the "
                        "other and their rows are never pooled."},
        "_generated": _stamp(),
        "preregistration": active_prereg(),
        "lbd_reference": (lbd_reference_summary() if SCOPE == "lbd" else None),
        "universe": {"source": os.path.relpath(UNIVERSE_SRC, REPO), "n_total": len(uni),
                     "n_after_nr4a_exclusion": sum(1 for u in uni if not u["in_nr4a_family"]),
                     "members": uni},
        "pipeline_provenance": {
            "reach_rule": "nr4a_paralogue_dynamics.matched_reach_hits_multi -> "
                          "nr4a3_basin_search.electrophile_reach (the committed prolate-spheroid criterion)",
            "placement_sampler": "nr4a3_basin_search.sample_placements",
            "pose_ensemble": "nr4a3_basin_search.build_pose_ensemble",
            "superposition": "nr4a3_basin_search.superpose_paralogue",
            "sasa": "nr4a_differential_atlas.shrake_rupley / residue_rsa",
            "aligner": "nr4a_differential_atlas.nw_align (BLOSUM62 Needleman-Wunsch)",
            "scope_aligner": ("categorical_decoy_null.sw_align (BLOSUM62 Smith-Waterman, nw_align's own "
                              "affine gap defaults) — SCOPE ONLY, no statistic passes through it"
                              if SCOPE == "lbd" else None),
            "e3_arms": os.path.relpath(NATIVE_REGISTRY, REPO),
            "params": {k: B.PARAMS[k] for k in ("linker_gate_atoms", "linker_rise_per_atom_A",
                                                "electrophile_arm_A", "hard_clash_A", "soft_clash_A",
                                                "contact_A", "min_contact_residues")},
        },
    }
    with open(PLAN, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(f"  [cdn] wrote pre-registration {PLAN} ({plan['universe']['n_after_nr4a_exclusion']} candidates)")
    return plan


def mode_fetch(args):
    uni = universe()
    accs = [u["accession"] for u in uni] + [NR4A3_ACC]
    got, failed = [], []
    for acc in accs:
        try:
            got.append(fetch_af(acc))
            print(f"  [cdn] fetched {acc}", flush=True)
        except Exception as ex:  # noqa: BLE001
            failed.append({"accession": acc, "error": str(ex)})
            print(f"  [cdn] FETCH FAILED {acc}: {ex}", flush=True)
    out = {"_generated": _stamp(), "fetched": got, "failed": failed}
    with open(os.path.join(CACHE, "fetch.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"  [cdn] {len(got)} models, {len(failed)} failures")
    if not got:
        raise SystemExit("  ABORT: 0 AlphaFold models fetched. Every downstream step would then run on an "
                         "empty universe and emit a plan with 0 pairs over 0 targets — a green artifact "
                         "produced by measuring nothing. Run `probe` for the raw API/file answers.")
    if len(failed) > 0.25 * len(accs):
        raise SystemExit(f"  ABORT: {len(failed)}/{len(accs)} AlphaFold fetches failed — the universe would "
                         "be silently re-defined by whatever happened to download.")
    return out


def lbd_reference_summary():
    """The `C24` reference, minus the sequence itself (which belongs in the model file, not in every plan)."""
    ref = lbd_reference()
    return {k: v for k, v in ref.items() if k != "seq"} | {
        "_reading": "the committed NR4A3 LBD construct — the SAME model the committed categorical verdict "
                    "was computed on. Its UniProt span is DERIVED from the file, never typed, and it "
                    "contains every cysteine of the committed unique set.",
        "committed_nr4a3_unique_cysteines": sorted(PD.NR4A3_UNIQUE_CYS),
        "unique_cysteines_inside_the_reference": sorted(
            c for c in PD.NR4A3_UNIQUE_CYS
            if ref["uniprot_span"][0] <= c <= ref["uniprot_span"][1]),
    }


def mode_pairs(args):
    """Trim, all-vs-all identity, pre-registered pair selection. Deterministic and answer-blind."""
    uni = universe()
    prereg = active_prereg()
    ref_seq = lbd_reference()["seq"] if SCOPE == "lbd" else None
    trimmed, refused = {}, []
    for u in uni + [{"gene": "NR4A3", "accession": NR4A3_ACC, "in_nr4a_family": True}]:
        acc = u["accession"]
        if not os.path.exists(af_path(acc)):
            refused.append({"accession": acc, "reason": "no AlphaFold model fetched"})
            continue
        try:
            meta = trim_one(acc, MIN_PLDDT, MIN_DOMAIN_LEN, ref_seq=ref_seq)
            meta.update(gene=u["gene"], in_nr4a_family=u["in_nr4a_family"])
            trimmed[acc] = meta
        except Exception as ex:  # noqa: BLE001
            refused.append({"accession": acc, "gene": u["gene"], "reason": f"{type(ex).__name__}: {ex}"})
    print(f"  [cdn] trimmed {len(trimmed)}, refused {len(refused)}", flush=True)

    seqs = {acc: B.load_paralogue(trimmed_path(acc))["seq"] for acc in trimmed}

    def ident(a, b):
        return alignment_identity(seqs[a], seqs[b], ATLAS.nw_align(seqs[a], seqs[b]))

    ref_pairs = {}
    for other in (NR4A1_ACC, NR4A2_ACC):
        if NR4A3_ACC in seqs and other in seqs:
            i, c = ident(NR4A3_ACC, other)
            ref_pairs[other] = {"identity": round(i, 4), "coverage": round(c, 4)}
    ref_identity = (sum(v["identity"] for v in ref_pairs.values()) / len(ref_pairs)) if ref_pairs else 0.6

    cand = [a for a in trimmed if not trimmed[a]["in_nr4a_family"]]
    cand.sort()
    entries = []
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            a, b = cand[i], cand[j]
            idn, cov = ident(a, b)
            entries.append({"a": a, "b": b, "gene_a": trimmed[a]["gene"], "gene_b": trimmed[b]["gene"],
                            "identity": round(idn, 4), "coverage": round(cov, 4)})
    # ⭑ The SELECTION RULE is `PREREG`'s, for both scopes — band, coverage floor, ranking and
    #   max_per_protein are held byte-identical, per `PREREG_LBD._held_identical_to_C16`. Only the BUDGET
    #   (`max_pairs`) is per-scope, and the greedy loop is deterministic, so the first `PREREG.max_pairs`
    #   pairs chosen here are exactly the ones a cap of that size would have chosen.
    max_pairs = SCOPES[SCOPE]["max_pairs"]
    selected, rejected = select_pairs(
        entries, ref_identity, PREREG["pair_formation"]["identity_band"],
        PREREG["pair_formation"]["alignment_coverage_min"], max_pairs,
        PREREG["pair_formation"]["max_per_protein"])
    nested = [p for p in selected[:PREREG["pair_formation"]["max_pairs"]]]

    ordered = []
    for p in selected:
        ordered.append({"target": p["a"], "paralogue": p["b"], "gene_target": p["gene_a"],
                        "gene_paralogue": p["gene_b"], "identity": p["identity"], "arm": "decoy"})
        ordered.append({"target": p["b"], "paralogue": p["a"], "gene_target": p["gene_b"],
                        "gene_paralogue": p["gene_a"], "identity": p["identity"], "arm": "decoy"})
    for other, gene in ((NR4A1_ACC, "NR4A1"), (NR4A2_ACC, "NR4A2")):
        if NR4A3_ACC in trimmed and other in trimmed:
            ordered.append({"target": NR4A3_ACC, "paralogue": other, "gene_target": "NR4A3",
                            "gene_paralogue": gene,
                            "identity": ref_pairs.get(other, {}).get("identity"), "arm": "reference"})

    plan = json.load(open(PLAN)) if os.path.exists(PLAN) else {"preregistration": prereg}
    plan.update({
        "_title": ("C02 — cross-system decoy null: PRE-REGISTRATION + the selected pair plan (still no "
                   "statistic computed)" if SCOPE == "plddt" else
                   "C02-L — cross-system decoy null over the reference-anchored LBD window: "
                   "PRE-REGISTRATION + the selected pair plan (still no statistic computed)"),
        "_generated": _stamp(),
        "nr4a3_reference_identities": ref_pairs,
        "nr4a3_reference_identity_used_for_ranking": round(ref_identity, 4),
        "trimmed": trimmed,
        "trim_refusals": refused,
        "n_candidate_pairs": len(entries),
        "selected_pairs": selected,
        "nested_top_pairs_matching_the_C16_budget": [f"{p['gene_a']}|{p['gene_b']}" for p in nested],
        "rejected_pairs_sample": rejected[:40],
        "n_rejected_pairs": len(rejected),
        "ordered_decoys": ordered,
        "n_ordered_decoys": len(ordered),
        "targets": sorted({o["target"] for o in ordered}),
        "window_size_spread": window_spread(trimmed),
        "⛔_nr4a3_scope_check": nr4a3_scope_check(trimmed),
    })
    with open(PLAN, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(f"  [cdn] {len(selected)} pairs -> {len(ordered)} ordered rows over "
          f"{len(plan['targets'])} targets; ref identity {ref_identity:.3f}")
    return plan


def mode_run(args):
    """Evaluate every ordered decoy whose TARGET falls in this shard. Sharding by target reuses the one
    expensive step (placement sampling) across that target's rows."""
    import tempfile
    plan = json.load(open(PLAN))
    targets = plan["targets"]
    mine = [t for k, t in enumerate(targets) if k % args.nshards == args.shard]
    os.makedirs(SHARD_DIR, exist_ok=True)
    workroot = tempfile.mkdtemp(prefix="cdn_root_")
    pl = PREREG["placements"]
    out_path = os.path.join(SHARD_DIR, f"shard-{args.shard}-of-{args.nshards}.json")
    results, refusals = [], []
    if os.path.exists(out_path):                       # resume: never re-buy finished work
        prev = json.load(open(out_path))
        results, refusals = prev.get("rows", []), prev.get("refusals", [])
    done = {(r["target"], r["paralogue"]) for r in results}
    print(f"  [cdn] shard {args.shard}/{args.nshards}: targets {mine} ({len(done)} rows already done)",
          flush=True)

    for tacc in mine:
        rows = [o for o in plan["ordered_decoys"] if o["target"] == tacc]
        if all((o["target"], o["paralogue"]) in done for o in rows):
            continue
        t0 = time.time()
        try:
            tmodel = B.load_paralogue(trimmed_path(tacc))
            pocket = fpocket_top_pocket(trimmed_path(tacc), workroot)
            if len(pocket["residues"]) < 3:
                raise ValueError(f"top pocket has {len(pocket['residues'])} lining residues")
            # pilot -> acceptance rate -> the budget that lands on target_n_placements
            _a, _pa, params, n_ap, n_poses, centroid = sample_anchors(
                tmodel, pocket["residues"], NATIVE_REGISTRY, pl["n_poses"], pl["seed"],
                pl["pilot_samples_per_arm_pose"])
            rate = len(_a) / max(1, n_ap * pl["pilot_samples_per_arm_pose"])
            if rate <= 0:
                raise ValueError("pilot accepted 0 placements — no feasible E3 placement on this pocket")
            budget = int(min(pl["max_samples_per_arm_pose"],
                             max(pl["pilot_samples_per_arm_pose"],
                                 math.ceil(pl["target_n_placements"] / (rate * max(1, n_ap))))))
            anchors, per_arm, params, n_ap, n_poses, centroid = sample_anchors(
                tmodel, pocket["residues"], NATIVE_REGISTRY, pl["n_poses"], pl["seed"] + 1, budget)
            print(f"  [cdn] {tacc}: pocket drugg={pocket['druggability']} lining={len(pocket['residues'])} "
                  f"pilot_rate={rate:.5f} budget={budget} -> {len(anchors)} placements "
                  f"({time.time()-t0:.0f}s)", flush=True)
        except Exception as ex:  # noqa: BLE001
            refusals.append({"target": tacc, "stage": "target_setup", "reason": f"{type(ex).__name__}: {ex}"})
            print(f"  [cdn] REFUSED target {tacc}: {ex}", flush=True)
            _save_shard(out_path, args, results, refusals)
            continue

        for o in rows:
            if (o["target"], o["paralogue"]) in done:
                continue
            try:
                pmodel = B.load_paralogue(trimmed_path(o["paralogue"]))
                tcys, _s, _m = cysteines_in_frame(trimmed_path(tacc), None, pmodel)
                pcys, sup, _m2 = cysteines_in_frame(trimmed_path(o["paralogue"]), tmodel, tmodel)
                stat = ordered_decoy_statistic(anchors, tcys, pcys, params)
                row = {**o, **stat, "pocket": pocket, "n_poses": n_poses,
                       "pocket_centroid": [round(c, 3) for c in centroid],
                       "placement_budget_per_arm_pose": budget,
                       "per_arm": per_arm, "superposition": sup,
                       "elapsed_s": round(time.time() - t0, 1)}
                results.append(row)
                print(f"  [cdn]   {o['gene_target']}|{o['gene_paralogue']}: {stat['status']} "
                      f"events={stat.get('n_conditioning_events_gate')} P={stat.get('P_gate')} "
                      f"P_exp={stat.get('P_gate_EXPOSED')}", flush=True)
            except Exception as ex:  # noqa: BLE001
                refusals.append({"target": o["target"], "paralogue": o["paralogue"], "stage": "row",
                                 "reason": f"{type(ex).__name__}: {ex}"})
                print(f"  [cdn]   REFUSED {o['target']}|{o['paralogue']}: {ex}", flush=True)
            _save_shard(out_path, args, results, refusals)      # checkpoint after EVERY unit
    _save_shard(out_path, args, results, refusals)
    print(f"  [cdn] shard {args.shard} wrote {out_path}: {len(results)} rows, {len(refusals)} refusals")
    return {"rows": results, "refusals": refusals}


def _save_shard(path, args, rows, refusals):
    with open(path, "w") as fh:
        json.dump({"_generated": _stamp(), "shard": args.shard, "nshards": args.nshards,
                   "rows": rows, "refusals": refusals}, fh, indent=2)


SELFCHECK = os.path.join(CACHE, "selfcheck.json")


def mode_selfcheck(args):
    """★ THE HARNESS'S OWN KNOWN-ANSWER TEST, and the reason this null can be believed at all.

    Run THIS driver on the COMMITTED NR4A3 / NR4A1 / NR4A2 opened models with the COMMITTED Pocket-5 lining
    (no fpocket, no AlphaFold) and compare against
    `nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope.static_opened_model`. If the driver's
    uniqueness rule, superposition, placement sampling or reach arithmetic were wrong, it would not land on
    the committed answer — and a background measured by a broken harness would be worse than no background.

    ⚠ The 12-atom cell is deliberately NOT the discriminating comparison: the committed run has 77
    conditioning events out of 73,867 placements, so a cheap re-run has a handful and can only agree
    trivially at 0. The 20-atom cell has thousands of events on both sides and is where a real disagreement
    would show. Both are recorded."""
    seed = PREREG["placements"]["seed"]
    n_samples = int(os.environ.get("SELFCHECK_SAMPLES", "200000"))
    u = json.load(open(PD.UNIQUE_JSON))
    pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    t = B.load_paralogue(PD.STATIC_MODEL["NR4A3"])
    anchors, _pa, params, _nap, n_poses, _c = sample_anchors(
        t, pocket_local, NATIVE_REGISTRY, PREREG["placements"]["n_poses"], seed, n_samples)
    out = {"_what": "the C02 driver re-run on the committed opened models + committed Pocket-5, against the "
                    "committed static verdict",
           "n_placements": len(anchors), "n_poses": n_poses, "samples_per_arm_pose": n_samples,
           "rows": {}}
    paras = {sp: B.load_paralogue(PD.STATIC_MODEL[sp]) for sp in ("NR4A1", "NR4A2")}
    tcys = {sp: cysteines_in_frame(PD.STATIC_MODEL["NR4A3"], None, paras[sp])[0] for sp in paras}
    pcys = {sp: cysteines_in_frame(PD.STATIC_MODEL[sp], t, t)[0] for sp in paras}
    for sp in paras:
        st = ordered_decoy_statistic(anchors, tcys[sp], pcys[sp], params)
        out["rows"][sp] = {"target_unique_uniprot": sorted(int(c[1:]) + B.UNIPROT_OFFSET
                                                           for c in st["target_unique_labels"]),
                           "n_paralogue_cysteines": st["n_paralogue_cysteines"],
                           "by_linker_atoms": st["by_linker_atoms"]}
    joint_labels = {c["label"] for c in tcys["NR4A1"] if not c["partner_has_cys_here"]} \
        & {c["label"] for c in tcys["NR4A2"] if not c["partner_has_cys_here"]}
    joint = ordered_decoy_statistic(
        anchors, [dict(c, partner_has_cys_here=False) for c in tcys["NR4A1"] if c["label"] in joint_labels],
        pcys["NR4A1"] + pcys["NR4A2"], params)
    out["rows"]["JOINT_both_paralogues"] = {
        "target_unique_uniprot": sorted(int(c[1:]) + B.UNIPROT_OFFSET for c in joint["target_unique_labels"]),
        "by_linker_atoms": joint["by_linker_atoms"]}
    cv = json.load(open(DYNAMICS))["categorical_verdict"]["by_scope"]["static_opened_model"]
    out["committed_static_opened_model"] = {
        "_source": "research/modalities/nr4a-paralogue-dynamics.json (the ONE home; quoted, not re-derived)",
        "n_placements": cv.get("n_placements"),
        "by_linker_atoms": {n: cv["by_linker_atoms"][n] for n in ("12", "20")}}
    out["committed_nr4a3_unique_cysteines"] = sorted(PD.NR4A3_UNIQUE_CYS)
    jb = out["rows"]["JOINT_both_paralogues"]["by_linker_atoms"]

    def _cmp(n, key):
        """abs difference against the committed cell, or None when THIS run had no conditioning events —
        an absent reading is not a reading of agreement (CLAUDE.md §4)."""
        mine = jb[n]["P_paralogue_also_labelled"]
        if mine is None or jb[n]["n_conditioning_events"] == 0:
            return None
        return round(abs(mine - cv["by_linker_atoms"][n][key]), 5)
    out["checks"] = {
        "unique_set_reproduced": out["rows"]["JOINT_both_paralogues"]["target_unique_uniprot"]
        == sorted(PD.NR4A3_UNIQUE_CYS),
        "n_paralogue_cysteines": {sp: out["rows"][sp]["n_paralogue_cysteines"] for sp in paras},
        "n_conditioning_events": {n: jb[n]["n_conditioning_events"] for n in ("12", "20")},
        "committed_n_conditioning_events": {
            n: cv["by_linker_atoms"][n]["n_placements_with_any_nr4a3_hit"] for n in ("12", "20")},
        "gate12_collision_abs_diff": _cmp("12", "P_paralogue_also_labelled_given_nr4a3"),
        "atoms20_collision_abs_diff": _cmp("20", "P_paralogue_also_labelled_given_nr4a3"),
        "atoms20_mean_P_any_paralogue_cys": {
            "harness_NR4A1": out["rows"]["NR4A1"]["by_linker_atoms"]["20"]["mean_P_any_paralogue_cys"],
            "committed_NR4A1": cv["by_linker_atoms"]["20"]["mean_P_any_cysteine_NR4A1"],
            "harness_NR4A2": out["rows"]["NR4A2"]["by_linker_atoms"]["20"]["mean_P_any_paralogue_cys"],
            "committed_NR4A2": cv["by_linker_atoms"]["20"]["mean_P_any_cysteine_NR4A2"]},
        "_reading": "`atoms20_collision_abs_diff` is the DISCRIMINATING number — thousands of conditioning "
                    "events on both sides, so a driver that disagreed with the committed pipeline would "
                    "show it here. The 12-atom cell agrees trivially at 0 on a cheap re-run (77 events in "
                    "73,867 committed placements) and is recorded for completeness, not as evidence. A "
                    "`None` means this run produced no conditioning events at that length and the "
                    "comparison could not be made — not that it agreed.",
    }
    os.makedirs(CACHE, exist_ok=True)
    with open(SELFCHECK, "w") as fh:
        json.dump(out, fh, indent=2)
    # ⚠ `.get`, NOT `[...]`. This print crashed the whole selfcheck STEP on run 30773415505 with
    # KeyError: 'gate12_collision_reproduced' — a key I had renamed above and not here. The artifact was
    # already on disk; only the summary line was stale, and it still took the Reduce and Publish steps down
    # with it. A cosmetic line must never be able to fail a measured step.
    c = out["checks"]
    print(f"  [cdn] selfcheck: unique_set_reproduced={c.get('unique_set_reproduced')} "
          f"events={c.get('n_conditioning_events')} "
          f"|d12|={c.get('gate12_collision_abs_diff')} |d20|={c.get('atoms20_collision_abs_diff')}")
    return out


def cysteine_level_background(decoys, refs):
    """★ THE CYSTEINE-LEVEL BACKGROUND — and the ONLY construction in this module that can give C397 a
    percentile of its own.

    The row-level statistic pools a target's unique cysteines, so it answers *"does this PAIR collide?"*.
    C397's question is *"does THIS RESIDUE collide, and how does that compare to an arbitrary
    target-unique cysteine in an arbitrary close paralogue pair?"* — a different unit of analysis, and it
    needs a background of the same unit. Every decoy's target-unique cysteine that clears the SAME
    gradeability floor is one background point.

    ⚠ TWO NON-INDEPENDENCES, STATED HERE BECAUSE THEY BOUND WHAT THE PERCENTILE MEANS:
      (a) cysteines within one target share a placement set, so background points are CLUSTERED by target
          — the effective n is smaller than the count, and the count is reported next to the number of
          distinct targets contributing;
      (b) an ordered pair and its reverse orientation are both present by design (`C16`'s rule, held), so
          the same protein appears as target and as paralogue.
    Neither is a defect; both make the background LESS independent than n suggests, which is the direction
    that should make a reader more cautious, not less. PURE."""
    floor = PREREG["gradeability"]["min_conditioning_events"]
    points, ref_points = [], []
    for r in decoys:
        for label, row in (r.get("per_unique_cysteine") or {}).items():
            points.append({"gene_target": r.get("gene_target"), "gene_paralogue": r.get("gene_paralogue"),
                           "target": r.get("target"), "cysteine": label, "status": row.get("status"),
                           "rsa": row.get("rsa"),
                           "n_conditioning_events_gate": row.get("n_conditioning_events_gate"),
                           "P_gate": row.get("P_gate"), "P_gate_EXPOSED": row.get("P_gate_EXPOSED")})
    for r in refs:
        for label, row in (r.get("per_unique_cysteine") or {}).items():
            ref_points.append({"gene_paralogue": r.get("gene_paralogue"), "cysteine": label,
                               "status": row.get("status"), "rsa": row.get("rsa"),
                               "n_conditioning_events_gate": row.get("n_conditioning_events_gate"),
                               "P_gate": row.get("P_gate"), "P_gate_EXPOSED": row.get("P_gate_EXPOSED")})
    graded = [p for p in points if p.get("status") == "GRADED"]
    bg = {
        "_what": "one point per (ordered decoy pair x target-unique cysteine) clearing the same "
                 f"gradeability floor of {floor} conditioning events at the {GATE}-atom gate.",
        "n_cysteine_points_attempted": len(points),
        "n_graded": len(graded),
        "n_underpowered": sum(1 for p in points if str(p.get("status", "")).startswith("UNDERPOWERED")),
        "n_distinct_targets_contributing": len({p["target"] for p in graded}),
        "⚠_clustering": "background points are CLUSTERED BY TARGET (cysteines of one protein share a "
                        "placement set), so the effective n is below `n_graded`. "
                        "`n_distinct_targets_contributing` is the honest lower bound on independence.",
        "reach_only": summarise_background(graded, "P_gate"),
        "exposed": summarise_background(graded, "P_gate_EXPOSED"),
        "points": sorted(points, key=lambda p: (p.get("P_gate") is None, p.get("P_gate") or 0.0)),
    }
    nr4a3 = {}
    for p in ref_points:
        key = f"{p['cysteine']}_vs_{p['gene_paralogue']}"
        nr4a3[key] = {
            **p,
            "percentile_reach_only": (percentile_of(p["P_gate"], [g["P_gate"] for g in graded])
                                      if p.get("P_gate") is not None and graded else None),
            "percentile_exposed": (percentile_of(p["P_gate_EXPOSED"],
                                                 [g["P_gate_EXPOSED"] for g in graded])
                                   if p.get("P_gate_EXPOSED") is not None and graded else None),
            "⚠_percentile_resolution": (round(1.0 / len(graded), 4) if graded else None),
        }
    return bg, nr4a3


def placement_budget_saturation(rows):
    """⛔ DID THE PLACEMENT SETS ACTUALLY REACH THEIR PRE-REGISTERED SIZE? PURE.

    ★ WHY THIS IS A BLOCK AND NOT A FOOTNOTE (measured 2026-08-03, in the first `C24` shard to finish).
    The pre-registration asks for `target_n_placements` per row and gets there ADAPTIVELY: a pilot measures
    the acceptance rate, and the budget is set to whatever reaches the target — bounded by
    `max_samples_per_arm_pose`, which exists so one awkward pocket cannot run forever.

    That bound was observed BINDING on the first `C24` shard to land: `P62508` (ESRRG) reported
    `pilot_rate=0.00104`, `budget=6000000` (the cap) and **13,091 placements against a 45,000 target**.
    Nothing is wrong and nothing was tuned — the cap is pre-registered and held identical to `C16`'s. But
    the consequence is invisible unless it is counted: a row with a third of the placements has a third of
    the conditioning events, so it is likelier to fall below the gradeability floor and drop out of the
    graded background. ⚠ **A background that shrank because the SAMPLER ran out of budget must never read
    like one that shrank because the BIOLOGY was uniform.**

    ⛔ WHAT CAUSES IT — MEASURED, AND IT IS NOT THE OBVIOUS ANSWER. The natural story is "bigger windows,
    more protein to clash against, lower acceptance". **That story was tested and does not hold.** On the
    committed NR4A3 opened model with the committed pocket lining, acceptance is **0.001521** over the full
    254-residue construct and **0.001435** over a 144-residue truncation of it — i.e. the same rate at
    `C24`-sized and `C16`-sized windows, so window size alone does not explain the saturation. The
    remaining measured difference between the scopes is WHICH CAVITY the pre-registered fpocket rule picks
    inside a different window, and acceptance is a property of that cavity. (Also tested and refuted as a
    cause: the new per-cysteine statistic, which cost **0.00 s** on the same placement set.)
    """
    pl = PREREG["placements"]
    target, cap = pl["target_n_placements"], pl["max_samples_per_arm_pose"]
    per_target = {}
    for r in rows:
        t = r.get("target")
        if t is None or t in per_target:
            continue
        per_target[t] = {"gene": r.get("gene_target"), "n_placements": r.get("n_placements"),
                         "budget_per_arm_pose": r.get("placement_budget_per_arm_pose"),
                         "n_poses": r.get("n_poses")}
    ns = sorted(v["n_placements"] for v in per_target.values() if v.get("n_placements") is not None)
    at_cap = [k for k, v in per_target.items() if v.get("budget_per_arm_pose") == cap]
    short = [k for k, v in per_target.items()
             if v.get("n_placements") is not None and v["n_placements"] < target]
    if not per_target:
        return None
    return {
        "preregistered_target_n_placements": target,
        "preregistered_max_samples_per_arm_pose": cap,
        "n_targets": len(per_target),
        "n_targets_at_the_sampler_cap": len(at_cap),
        "n_targets_below_the_placement_target": len(short),
        "placements_min": (ns[0] if ns else None),
        "placements_median": (ns[len(ns) // 2] if ns else None),
        "placements_max": (ns[-1] if ns else None),
        "targets_at_cap": sorted(per_target[k]["gene"] or k for k in at_cap),
        "per_target": per_target,
        "★_reading": (
            "A row that did not reach the pre-registered placement count has proportionally fewer "
            "conditioning events and is likelier to fall below the gradeability floor. That makes the "
            "graded background SMALLER, not biased in a known direction — and it is a property of the "
            "sampler's pre-registered cost bound meeting a lower acceptance rate, not of the proteins. "
            "⛔ It is reported here so a background that shrank for a MECHANICAL reason is never read as "
            "one that shrank for a BIOLOGICAL one."),
        "⛔_not_repaired_after_the_fact": (
            "The cap and the adaptive rule are pre-registered and held byte-identical to `C16`'s. Raising "
            "the cap now — after seeing which rows it bound — is the same class of act as widening `C16`'s "
            "trim after seeing that C397 fell outside it. It stays where it was registered; if a future "
            "run wants more placements it registers that in advance."),
    }


def compare_scopes(scope, bg, cys_bg, nr4a3, precondition, nr4a3_scope, n_graded):
    """★ WHAT CHANGED VERSUS THE OTHER SCOPE — read out of the sibling's COMMITTED artifact, never typed.

    The deliverable of a second scope is not a second number; it is the DIFFERENCE, stated plainly enough
    that a reader can see whether the scope decided the answer. If the sibling artifact is not on disk this
    says so rather than emitting an empty comparison — an absent reading is not a reading of absence."""
    other = next((v for k, v in SCOPES.items() if k != scope), None)
    if other is None:
        return None
    slug = other["slug"]
    path = os.path.join(HERE, f"categorical-decoy-null{('-' + slug) if slug else ''}.json")
    out = {"_what": f"this run ({SCOPES[scope]['configuration_id']}, {SCOPES[scope]['label']}) against "
                    f"{other['configuration_id']} ({other['label']}).",
           "other_artifact": os.path.relpath(path, REPO),
           "⛔_not_a_supersession": "both runs stand. This block reports a DIFFERENCE, not a correction, "
                                   "and the rows are never pooled."}
    if not os.path.exists(path):
        out["status"] = ("SIBLING ARTIFACT NOT ON DISK — no comparison was made. This is a missing "
                         "observation, not a finding of no difference.")
        return out
    try:
        o = json.load(open(path))["results"]
    except Exception as ex:  # noqa: BLE001
        out["status"] = f"SIBLING ARTIFACT UNREADABLE: {type(ex).__name__}: {ex}"
        return out
    obg = (o.get("background_at_gate_12") or {}).get("reach_only") or {}
    on3 = o.get("nr4a3_harness_matched") or {}
    oscope = o.get("⛔_nr4a3_harness_scope") or {}
    out["status"] = "COMPARED"
    out["row_level_background_reach_only"] = {
        "this_scope": {k: (bg.get("reach_only") or {}).get(k) for k in
                       ("n", "min", "q25", "median", "q75", "max", "n_exactly_zero", "frac_exactly_zero",
                        "frac_exactly_zero_wilson95", "percentile_resolution",
                        "★_what_this_n_can_and_cannot_exclude")},
        "other_scope": {k: obg.get(k) for k in
                        ("n", "min", "q25", "median", "q75", "max", "n_exactly_zero", "frac_exactly_zero",
                        "frac_exactly_zero_wilson95", "percentile_resolution",
                        "★_what_this_n_can_and_cannot_exclude")},
    }
    out["nr4a3_row_percentiles_reach_only"] = {
        "this_scope": {k: v.get("percentile_reach_only") for k, v in nr4a3.items()},
        "other_scope": {k: v.get("percentile_reach_only") for k, v in on3.items()},
    }
    out["what_the_NR4A3_row_actually_scored"] = {
        "this_scope": {"window_uniprot": nr4a3_scope.get("trimmed_window_uniprot"),
                       "unique_cysteines_in_scope": nr4a3_scope.get("inside_the_trimmed_window"),
                       "C397_in_scope": nr4a3_scope.get("headline_residue_C397_in_scope")},
        "other_scope": {"window_uniprot": oscope.get("trimmed_window_uniprot"),
                        "unique_cysteines_in_scope": oscope.get("inside_the_trimmed_window"),
                        # ⚠ AN ABSENT FIELD IS NOT AN UNKNOWN ANSWER. `headline_residue_C397_in_scope` was
                        # added with this scope, so the older artifact does not carry it — but the answer is
                        # right there in `inside_the_trimmed_window` and rendering it `null` would print a
                        # KNOWN fact as an open question. Derived when absent, and the derivation says so.
                        "C397_in_scope": (
                            oscope["headline_residue_C397_in_scope"]
                            if "headline_residue_C397_in_scope" in oscope
                            else (397 in (oscope.get("inside_the_trimmed_window") or [])
                                  if oscope.get("inside_the_trimmed_window") is not None else None)),
                        "_C397_in_scope_source": ("recorded in that artifact"
                                                  if "headline_residue_C397_in_scope" in oscope else
                                                  "DERIVED here from that artifact's "
                                                  "`inside_the_trimmed_window` — the field predates this "
                                                  "scope, and printing `null` for a knowable fact would be "
                                                  "an absent reading masquerading as an unknown")},
    }
    op = o.get("precondition_has_a_target_unique_cysteine") or {}
    out["precondition_no_target_unique_cysteine"] = {
        "this_scope": {k: precondition.get(k) for k in
                       ("n_ordered_decoys", "n_with_no_target_unique_cysteine",
                        "frac_with_no_target_unique_cysteine")},
        "other_scope": {k: op.get(k) for k in
                        ("n_ordered_decoys", "n_with_no_target_unique_cysteine",
                         "frac_with_no_target_unique_cysteine")},
    }
    out["cysteine_level_background"] = {
        "this_scope": {"n_graded": (cys_bg or {}).get("n_graded"),
                       "reach_only": (cys_bg or {}).get("reach_only")},
        "other_scope": ((o.get("★_cysteine_level_background_at_gate_12") or {}).get("reach_only")
                        if o.get("★_cysteine_level_background_at_gate_12") else
                        "NOT COMPUTED in that run — the cysteine-level statistic was added with this scope, "
                        "so there is no matched figure to compare against. Stated rather than left blank."),
    }
    out["⚠_reading"] = (
        "Differences here are the JOINT effect of the scope AND of everything the scope changed downstream "
        "— which proteins survive the trim, which pairs the identity ranking then selects, which cavity "
        "fpocket calls top-druggability inside a different window, and how many cysteines are in frame. "
        "They are NOT a decomposition. Reading one number's movement as caused by the trim alone would be "
        "over-reading this block.")
    return out


def mode_reduce(args):
    plan = json.load(open(PLAN))
    rows, refusals = [], []
    for p in sorted(glob.glob(os.path.join(SHARD_DIR, "shard-*.json"))):
        d = json.load(open(p))
        rows.extend(d.get("rows", []))
        refusals.extend(d.get("refusals", []))
    decoys = [r for r in rows if r.get("arm") == "decoy"]
    refs = [r for r in rows if r.get("arm") == "reference"]
    graded = [r for r in decoys if r.get("status") == "GRADED"]
    underpowered = [r for r in decoys if r.get("status", "").startswith("UNDERPOWERED")]
    undefined = [r for r in decoys if r.get("status", "").startswith("UNDEFINED")]

    bg = {"reach_only": summarise_background(graded, "P_gate"),
          "exposed": summarise_background(graded, "P_gate_EXPOSED")}
    cys_bg, cys_nr4a3 = cysteine_level_background(decoys, refs)

    nr4a3 = {}
    for r in refs:
        nr4a3[r["gene_paralogue"]] = {
            "status": r.get("status"), "n_conditioning_events_gate": r.get("n_conditioning_events_gate"),
            "P_gate": r.get("P_gate"), "P_gate_EXPOSED": r.get("P_gate_EXPOSED"),
            "n_target_unique_cysteines": r.get("n_target_unique_cysteines"),
            "target_unique_labels": r.get("target_unique_labels"),
            "n_placements": r.get("n_placements"),
            "percentile_reach_only": (percentile_of(r["P_gate"], [g["P_gate"] for g in graded])
                                      if r.get("P_gate") is not None else None),
            "percentile_exposed": (percentile_of(r["P_gate_EXPOSED"],
                                                 [g["P_gate_EXPOSED"] for g in graded])
                                   if r.get("P_gate_EXPOSED") is not None else None),
        }

    committed = None
    if os.path.exists(DYNAMICS):
        d = json.load(open(DYNAMICS))
        cv = d.get("categorical_verdict", {})
        committed = {"_source": "research/modalities/nr4a-paralogue-dynamics.json -> categorical_verdict "
                                "(the ONE home of these figures; quoted, not re-derived)",
                     "gate_atoms": cv.get("gate_atoms"),
                     "by_scope": {k: {"P_paralogue_also_labelled_given_nr4a3":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("P_paralogue_also_labelled_given_nr4a3"),
                                      "P_paralogue_also_labelled_given_nr4a3_EXPOSED":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("P_paralogue_also_labelled_given_nr4a3_EXPOSED"),
                                      "n_placements_with_any_nr4a3_hit":
                                      v.get("by_linker_atoms", {}).get("12", {})
                                       .get("n_placements_with_any_nr4a3_hit")}
                                  for k, v in cv.get("by_scope", {}).items()}}

    # ★ WHICH NR4A3 CYSTEINES THE HARNESS COULD EVEN SEE — measured from the trim, not narrated. This is
    # the single most load-bearing caveat on the percentile, so it is computed and published rather than
    # left to prose. One home: `nr4a3_scope_check`, which the PLAN calls too, so a plan cannot promise a
    # window the reduce then contradicts.
    nr4a3_scope = nr4a3_scope_check(plan.get("trimmed"))
    undef_rows = [r for r in decoys if r.get("status", "").startswith("UNDEFINED")]
    precondition = {
        "_what": "How often a close paralogue pair even HAS a target-unique cysteine — the categorical "
                 "screen's FIRST precondition, before any reach question is asked.",
        "n_ordered_decoys": len(decoys),
        "n_with_no_target_unique_cysteine": len(undef_rows),
        "frac_with_no_target_unique_cysteine": (len(undef_rows) / len(decoys)) if decoys else None,
        "wilson95": PD.wilson95(len(undef_rows), len(decoys)) if decoys else None,
        "★_reading": "This is a result in its own right, not bookkeeping: a pair with no target-unique "
                     "cysteine is a pair on which the categorical screen could never fire at all. It "
                     "belongs beside the collision statistic, because the two together are what 'how "
                     "special is the NR4A3 configuration' actually decomposes into.",
    }
    sc = SCOPES[SCOPE]
    res = {
        "_title": ("C02 — cross-system decoy null for the categorical covalent axis" if SCOPE == "plddt"
                   else "C02-L — cross-system decoy null for the categorical covalent axis, over the "
                        "REFERENCE-ANCHORED LBD WINDOW (`C24`). A SECOND, INDEPENDENTLY PRE-REGISTERED "
                        "scope — NOT a widening of C02's"),
        "_status": "INSTRUMENT CALIBRATION. $0 CPU/CI. Nothing here is a claim about binding, reactivity, "
                   "degradation, efficacy or safety.",
        "_reading": "This calibrates the SCREEN, not NR4A3. It converts 'the categorical gate fired' into "
                    "'the categorical gate fired, against a measured background of X'.",
        "_scope": {
            "name": SCOPE, "configuration_id": sc["configuration_id"], "rule": sc["label"],
            "sibling": {k: {"configuration_id": v["configuration_id"],
                            "artifact": f"research/modalities/categorical-decoy-null"
                                        f"{('-' + v['slug']) if v['slug'] else ''}.json"}
                        for k, v in SCOPES.items() if k != SCOPE},
            "⛔_never_pooled": "the two scopes are separate tests. Their rows are never merged into one "
                              "background, neither supersedes the other, and a percentile always names "
                              "which scope produced it.",
        },
        "_generated": _stamp(),
        "preregistration": plan.get("preregistration", active_prereg()),
        "lbd_reference": plan.get("lbd_reference"),
        "pair_plan": {k: plan.get(k) for k in ("nr4a3_reference_identities",
                                               "nr4a3_reference_identity_used_for_ranking",
                                               "selected_pairs", "n_candidate_pairs", "n_rejected_pairs",
                                               "n_ordered_decoys", "targets", "trim_refusals",
                                               "window_size_spread",
                                               "nested_top_pairs_matching_the_C16_budget")},
        "results": {
            "n_decoy_rows_attempted": len(decoys),
            "n_graded": len(graded), "n_underpowered": len(underpowered), "n_undefined": len(undefined),
            "precondition_has_a_target_unique_cysteine": precondition,
            "⛔_nr4a3_harness_scope": nr4a3_scope,
            "⛔_placement_budget_saturation": placement_budget_saturation(rows),
            "n_refusals": len(refusals),
            "background_at_gate_12": bg,
            "nr4a3_harness_matched": nr4a3,
            "★_cysteine_level_background_at_gate_12": cys_bg,
            "★_nr4a3_per_cysteine_vs_that_background": cys_nr4a3,
            "nr4a3_committed_for_reference": committed,
            "comparison_to_the_other_scope": compare_scopes(SCOPE, bg, cys_bg, nr4a3, precondition,
                                                            nr4a3_scope, len(graded)),
            "decoy_rows": [{k: r.get(k) for k in
                            ("gene_target", "gene_paralogue", "target", "paralogue", "identity", "status",
                             "n_placements", "n_target_cysteines", "n_target_unique_cysteines",
                             "target_unique_labels", "n_paralogue_cysteines",
                             "n_conditioning_events_gate", "P_gate", "P_gate_EXPOSED")}
                           for r in sorted(decoys, key=lambda r: (r.get("P_gate") is None,
                                                                  r.get("P_gate") or 0))],
            "refusals": refusals,
        },
        "harness_known_answer_check": (json.load(open(SELFCHECK)) if os.path.exists(SELFCHECK) else
                                       {"status": "NOT RUN — the driver's own reproduction of the committed "
                                                  "static verdict was not available to this reduce"}),
        "limits": [
            "The background is a NUCLEAR-RECEPTOR background: every decoy pair is drawn from the committed "
            "47-receptor human NR list. It does not bound the rate over the whole proteome.",
            "One static AlphaFold conformer per protein. The committed NR4A3 verdict has three scopes "
            "(static / unbiased-release / metad-biased); only the STATIC scope is comparable to these rows, "
            "and the harness-matched NR4A3 row is provided precisely so the percentile is not taken against "
            "a differently-produced number.",
            "The pocket rule differs from NR4A3's prespecified Pocket-5 (fpocket top-druggability cavity), "
            "which is why NR4A3 is run through the SAME rule here rather than compared across rules.",
            "AlphaFold models are heavy-atom only; the committed NR4A3 opened models carry hydrogens, so "
            "the Shrake-Rupley RSA is not numerically identical between the two arms. The exposure-filtered "
            "column is affected; the reach-only column, which the audit shows carries the 12-atom result, "
            "is not.",
            ("⛔ THE HARNESS-MATCHED NR4A3 ROW DOES NOT COVER C397. The pre-registered pLDDT trim leaves "
             "only part of the NR4A3 LBD, so the row rests on whichever unique cysteines survive it — see "
             "`results.⛔_nr4a3_harness_scope`, which measures exactly which. The percentile calibrates the "
             "SCREEN under one identical rule; it is not a re-derivation of the committed C397-led result."
             if SCOPE == "plddt" else
             "⛔ THIS IS STILL AN ALPHAFOLD-MODEL ROW FOR NR4A3, NOT THE COMMITTED OPENED-MODEL ROW AND NOT "
             "AN 8XTT ROW. C397 is in scope here, which is the whole point of this run — but the structure "
             "it is scored on is the AlphaFold model, chosen so that NR4A3 and the decoys share ONE "
             "structure source. A percentile from this run calibrates the SCREEN on that source. The "
             "committed C397-led verdict keeps its own home in `nr4a-paralogue-dynamics.json` and is quoted "
             "here, never recomputed."),
            "The EXPOSURE-FILTERED percentile for NR4A3 may be undefined (P_gate_EXPOSED = null) when its "
            "surviving unique cysteine is buried in the AlphaFold model. An undefined conditional is "
            "reported as null and excluded, never as a zero — but it means the exposed column can have no "
            "NR4A3 point even while the reach-only column does. The audit establishes reach-only as the "
            "load-bearing case at the 12-atom gate, which is why that is the column the verdict uses.",
            "Reach and exposure are necessary, not sufficient — for the decoys exactly as for NR4A3.",
            "Underpowered and undefined rows are excluded from the percentile and counted separately; that "
            "exclusion biases the graded background toward pairs with MORE collision opportunity.",
        ] + ([] if SCOPE == "plddt" else [
            "⭑ THIS SCOPE APPLIES NO CONFIDENCE CRITERION, by design — which means it admits residues "
            "`C16` would have removed, in the decoys exactly as in NR4A3. `plddt_in_window_REPORTED_NOT_"
            "APPLIED` in the plan's `trimmed` block records what those residues look like per protein so a "
            "reader can weigh it. A low-confidence side chain has an uncertain rotamer, and a cysteine's "
            "SG position is exactly what the reach rule uses.",
            "⚠ THE CYSTEINE-LEVEL BACKGROUND IS CLUSTERED BY TARGET and both orientations of every pair "
            "are present, so its effective n is below `n_graded`. "
            "`★_cysteine_level_background_at_gate_12.n_distinct_targets_contributing` is the honest lower "
            "bound, and a percentile's resolution is 1/n_graded — reported beside every percentile.",
            "⚠ THE PAIR BUDGET DIFFERS FROM `C16`'s (20 pairs against 10). The selection RULE is identical "
            "and the greedy order is deterministic, so the wider set NESTS the narrower one — but the "
            "background summary is over a different number of rows and the two `n`s must not be compared "
            "as if they were the same design. The nested top-10 subset is named in the plan for exactly "
            "that comparison.",
            "⛔ COMPARING THE TWO SCOPES' NUMBERS IS COMPARING TWO WHOLE PIPELINES, not two trims. The "
            "trim changes which proteins survive, which pairs the identity ranking then selects, which "
            "cavity fpocket calls top-druggability, and how many cysteines are in frame. "
            "`results.comparison_to_the_other_scope` says this at the point of use.",
        ]),
        "runtime_note": "produced by research/modalities/categorical_decoy_null.py (modes plan/probe/fetch/"
                        f"pairs/selfcheck/run/reduce) at --scope {SCOPE}",
    }
    res["map_edits_required"] = build_map_edits(res)
    # ⛔ A background of zero rows is not a background. Publishing one would turn "we measured nothing"
    # into a green artifact that reads as "the screen was calibrated" — the exact failure §4 warns about.
    if not decoys:
        raise SystemExit("  ABORT: no decoy rows reached reduce. Nothing was measured, so there is no "
                         "background to publish. Check the shard artifacts and the refusal list.")
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"  [cdn] wrote {args.out}: graded={len(graded)} underpowered={len(underpowered)} "
          f"undefined={len(undefined)} refusals={len(refusals)}")
    for k, v in nr4a3.items():
        print(f"  [cdn] NR4A3|{k}: P={v['P_gate']} pct={v['percentile_reach_only']} "
              f"P_exp={v['P_gate_EXPOSED']} pct_exp={v['percentile_exposed']}")
    if bg["reach_only"]:
        print(f"  [cdn] background reach-only: n={bg['reach_only']['n']} "
              f"median={bg['reach_only']['median']:.4f} frac_zero={bg['reach_only']['frac_exactly_zero']:.3f}")
    cbg = (cys_bg or {}).get("reach_only") or {}
    if cbg:
        print(f"  [cdn] cysteine-level background reach-only: n={cbg.get('n')} "
              f"median={cbg.get('median')} frac_zero={cbg.get('frac_exactly_zero')} "
              f"(targets={cys_bg.get('n_distinct_targets_contributing')})")
    for k, v in (cys_nr4a3 or {}).items():
        print(f"  [cdn] NR4A3 {k}: P={v.get('P_gate')} pct={v.get('percentile_reach_only')} "
              f"events={v.get('n_conditioning_events_gate')} status={v.get('status')}")
    print(f"  [cdn] scope={SCOPE} ({SCOPES[SCOPE]['configuration_id']}) "
          f"C397_in_scope={nr4a3_scope.get('headline_residue_C397_in_scope')}")
    return res


def grade(res):
    """THE PRE-REGISTERED VERDICT RULE, and its inputs. PURE (dict in, dict out).

    ★ ONE HOME. Both scopes are graded by the SAME rule and the SAME thresholds — the rule was written for
    `C16` and is not re-tuned for `C24`, because a second scope graded by a second rule would tell you
    nothing about the first. What differs is only which numbers go in."""
    r = res["results"]
    bg = (r.get("background_at_gate_12") or {}).get("reach_only") or {}
    bge = (r.get("background_at_gate_12") or {}).get("exposed") or {}
    n3 = r.get("nr4a3_harness_matched") or {}
    pct = [v.get("percentile_reach_only") for v in n3.values() if v.get("percentile_reach_only") is not None]
    n_graded = r.get("n_graded", 0)
    frac0 = bg.get("frac_exactly_zero")
    # DISTINGUISHED = NR4A3 sits at/near the bottom of the background AND zero is not the common answer.
    # Both halves are needed: a background where most decoys also return 0 makes a 0th-percentile NR4A3
    # meaningless, which is precisely the V20 failure mode.
    distinguished = (n_graded >= 5 and frac0 is not None and frac0 <= 0.5
                     and pct and max(pct) <= 0.25)
    verdict = ("UNDERPOWERED" if n_graded < 5 else
               "DISTINGUISHED" if distinguished else "NOT DISTINGUISHED")
    # ★ THE CYSTEINE-LEVEL VERDICT — the same rule, applied to the unit of analysis C397 lives in. It is
    #   reported SEPARATELY and never merged into the row-level one: they answer different questions and a
    #   single blended grade would hide which.
    cbg = (r.get("★_cysteine_level_background_at_gate_12") or {})
    cbgr = cbg.get("reach_only") or {}
    cn = cbg.get("n_graded", 0)
    cfrac0 = cbgr.get("frac_exactly_zero")
    c397 = {k: v for k, v in (r.get("★_nr4a3_per_cysteine_vs_that_background") or {}).items()
            if k.startswith("C397")}
    cpct = [v.get("percentile_reach_only") for v in c397.values()
            if v.get("percentile_reach_only") is not None]
    c_verdict = (
        "NOT MEASURED — C397 was not in this scope" if not c397 else
        "UNDERPOWERED" if cn < 5 or not cpct else
        "DISTINGUISHED" if (cfrac0 is not None and cfrac0 <= 0.5 and max(cpct) <= 0.25) else
        "NOT DISTINGUISHED")
    return {"verdict": verdict, "n_graded": n_graded, "frac0": frac0,
            "frac0_exposed": bge.get("frac_exactly_zero"), "percentiles": pct,
            "percentiles_exposed": {k: v.get("percentile_exposed") for k, v in n3.items()},
            "percentiles_reach_only": {k: v.get("percentile_reach_only") for k, v in n3.items()},
            "c397_verdict": c_verdict, "c397_n_graded": cn, "c397_frac0": cfrac0,
            "c397_percentiles": cpct, "c397_rows": c397,
            "summary": (f"n_graded={n_graded}, frac_exactly_zero={frac0}, "
                        f"NR4A3 percentile(s)={sorted(pct) if pct else None}"),
            "c397_summary": (f"cysteine-level n_graded={cn}, frac_exactly_zero={cfrac0}, "
                             f"C397 percentile(s)={sorted(cpct) if cpct else None}")}


def build_map_edits(res):
    """The roadmap edits this result requires — DESCRIBED, never applied (sibling agents are editing
    `nr4a3-program-map.md`). Anchors are resolved against the LIVE map by `map_edits`, so a `current_text`
    here is a byte-exact substring of the map at generation time and an entry that cannot be targeted says so
    instead of being silently wrong.

    ⚠ THE EDIT SET DEPENDS ON THE ANSWER, and both directions are filed with equal weight. A background that
    leaves NR4A3 unremarkable changes Route B's argument and `R8`'s grade; one that does not changes only the
    instrument's status — and per §0's strict bar, a null that FAILS TO REJECT closes nothing in §6."""
    import map_edits as ME
    text = ME.load_map()
    g = grade(res)
    if SCOPE == "lbd":
        entries = _map_edits_lbd(ME, text, res, g)
    else:
        entries = _map_edits_plddt(ME, text, res, g)
    return {
        "_what": "Roadmap edits this result requires. DESCRIBED, NOT APPLIED — `nr4a3-program-map.md` is "
                 "being edited by sibling agents and this run does not touch it. Route them with "
                 "`python3 research/manuscripts/route_map_edits.py <artifact> --apply`.",
        "_how_anchors_are_kept_live": "Every `current_text` is READ out of the map at generation time by "
                                      "`map_edits.locate`, so it is a byte-exact substring of the map as it "
                                      "stood. An anchor that is missing or ambiguous yields "
                                      "`status: ANCHOR_NOT_FOUND` / `ANCHOR_NOT_UNIQUE` with no "
                                      "`proposed_text` — a visible refusal, never a mis-targeted edit. "
                                      "Measured reason: the categorical audit emitted nine verbatim edits "
                                      "and all nine failed to apply against a restructured map.",
        "scope": SCOPE,
        "configuration_id": SCOPES[SCOPE]["configuration_id"],
        "verdict": g["verdict"],
        "c397_verdict": g["c397_verdict"],
        "verdict_basis": {
            "n_graded": g["n_graded"], "frac_exactly_zero_reach_only": g["frac0"],
            "frac_exactly_zero_exposed": g["frac0_exposed"],
            "nr4a3_percentiles_reach_only": g["percentiles_reach_only"],
            "nr4a3_percentiles_exposed": g["percentiles_exposed"],
            "cysteine_level_n_graded": g["c397_n_graded"],
            "cysteine_level_frac_exactly_zero": g["c397_frac0"],
            "c397_percentiles_reach_only": g["c397_percentiles"],
            "rule": "DISTINGUISHED requires n_graded >= 5 AND frac_exactly_zero <= 0.5 AND every NR4A3 "
                    "percentile <= 0.25. Both halves are needed: in a background where most decoys also "
                    "return 0, a 0th-percentile NR4A3 means nothing — that is precisely the V20 failure "
                    "mode. ⭑ The SAME rule and the SAME thresholds grade both scopes and both units of "
                    "analysis; only the numbers going in differ. `grade()` is its one home.",
        },
        "⛔_not_filed_in_section_6": "A null that FAILS TO REJECT closes nothing. Nothing here is proposed "
                                    "for §6 (dead / parked / held) in either direction.",
        "entries": entries,
        "verification": ME.verify(entries, text),
    }


def _map_edits_plddt(ME, text, res, g):
    """`C16`'s edit set — the one the committed C02 run emitted. Unchanged."""
    verdict, summary = g["verdict"], g["summary"]
    art = "research/modalities/categorical-decoy-null.json -> results.background_at_gate_12 / " \
          "results.nr4a3_harness_matched"
    entries = [
        ME.edit(text, "§3.1 instrument table — row V17", "| **V17** | The exposure criterion",
                "The categorical screen this row adjudicates now has a CROSS-SYSTEM background: unrelated "
                "close human paralogue pairs pushed through the identical pipeline. Until now every null in "
                "the repo was within-system, so the categorical result was an enrichment over an unmeasured "
                "background — the exact shape that cost the program `V20`. The background does not change "
                "V17's own positive-control failure; it changes what a 0 from the screen is worth.",
                art,
                ME.replace_in_line(
                    "behind NR4A3's C397 and C420",
                    "behind NR4A3's C397 and C420. ★ And the SCREEN this criterion sits inside now has a "
                    "CROSS-SYSTEM background — "
                    "[`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json) — so a 0 "
                    "from it can be read against a measured rate instead of an unmeasured one")),
        ME.edit(text, "§3.4 instrument facts", "### 3.4 · Three instrument facts this page used to be missing",
                "§3.4 is the section that exists to carry scope facts about instruments, and the largest one "
                "now missing is that the categorical screen has a measured cross-system background. Adding "
                "it here requires retitling the section, which is why the heading is the anchor.",
                art,
                ME.replace_in_line("Three instrument facts", "Four instrument facts")),
        ME.edit(text, "§3.2 R×V coverage matrix — row R8", "| `R8` linker reach |",
                "The `R8` cell reads `rank-only, and conditional on R5`. That is still true of the exposure "
                "criterion, but the SCREEN as a whole is no longer uncalibrated: it now has a decoy "
                "background at the 12-atom gate, reported both reach-only and exposure-filtered.",
                art,
                ME.replace_in_line(
                    "rank-only, and conditional on `R5`",
                    "rank-only, and conditional on `R5` — but the screen now has a measured cross-system "
                    "background at the 12-atom gate, reach-only AND exposure-filtered "
                    "([`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json))")),
        ME.edit(text, "§10.1 open rows", "### 10.1 · Open rows, ordered by what unblocks the most",
                "The decoy null was on no ranked list — it existed only as a limit in the categorical "
                "audit. §10.3's own lesson is that a caveat with nowhere to go is how work gets silently "
                "dropped, so it needs a row whether it passed or failed. ⚠ When the run is UNDERPOWERED a "
                "SECOND row is added in the same edit: an underpowered reading is neither a pass nor a "
                "failure, and what it needs is more pairs, which is $0.",
                art,
                ME.append_after_line(
                    "| **C02** | **Cross-system decoy null for the categorical axis** — unrelated close "
                    "human paralogue pairs through the identical pipeline | `R8` `R15` | ✓ **complete** | "
                    "— ($0) | **$0** — CPU/CI | ✅ **RAN.** Verdict **" + verdict + "**. " + summary +
                    ". Numbers: [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json); "
                    "design and pairs: [`categorical-decoy-null-plan.json`]"
                    "(../modalities/categorical-decoy-null-plan.json). The harness reproduces the committed "
                    "static verdict (`harness_known_answer_check`) |" +
                    ("" if verdict != "UNDERPOWERED" else
                     "\n| **C02b** | **Widen the decoy null** — too few pairs graded for a percentile | "
                     "`R8` | \u25cb | \u2014 | **$0** | " + summary + ". Raise `max_pairs` / relax the "
                     "gradeability floor in [`categorical_decoy_null.py`]"
                     "(../modalities/categorical_decoy_null.py) `PREREG` |"))),
    ]

    scope = (res.get("results") or {}).get("\u26d4_nr4a3_harness_scope") or {}
    outside = scope.get("\u26d4_outside_and_therefore_INVISIBLE_to_this_harness") or []
    if outside:
        entries.append(ME.edit(
            text, "\u00a73.4 instrument facts",
            "### 3.4 · Three instrument facts this page used to be missing",
            "\u26a0 THE CAVEAT THAT MUST TRAVEL WITH THE PERCENTILE. The pre-registered pLDDT trim leaves "
            f"{outside} outside the NR4A3 window, so the harness-matched row does NOT interrogate the "
            "program's headline C397. A roadmap that quotes the percentile without this reads as if the "
            "committed claim had been calibrated, and it has not been \u2014 the percentile calibrates the "
            "SCREEN under one identical rule.",
            art + " -> results.\u26d4_nr4a3_harness_scope",
            ME.replace_in_line("Three instrument facts", "Four instrument facts"),
            kind="same-anchor-as-the-fourth-fact-entry; apply once, carrying BOTH notes"))

    if verdict == "NOT DISTINGUISHED":
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "⛔ The decoy background does NOT separate the NR4A3 result from an arbitrary close paralogue "
            "pair at the 12-atom gate. That is a blocker on the argument, not on the chemistry: the "
            "categorical GO may not be reported as an enrichment until it is. This is the V20 shape and it "
            "must be filed as one.",
            art, ME.append_after_line(
                "\n⛔ **The categorical GO is not distinguished from a cross-system background.** " + summary +
                " — see [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json). Until "
                "that changes, the categorical result may be reported as a *screen output*, never as an "
                "*enrichment*.")))
    elif verdict == "DISTINGUISHED":
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "The categorical GO now stands against a MEASURED background rather than an unmeasured one, "
            "which is what makes it quotable. The background belongs next to the claim, not in a footnote.",
            art, ME.append_after_line(
                "\n★ **The categorical GO now has a measured cross-system background.** " + summary +
                " — see [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json). ⚠ The "
                "background is a NUCLEAR-RECEPTOR background, not a proteome background, and it calibrates "
                "the SCREEN, not the target.")))
    return entries


def _map_edits_lbd(ME, text, res, g):
    """`C24`'s edit set. Different anchors from `C16`'s, because `C16`'s edits have already been applied and
    the map now carries their text — an edit set that re-targeted them would either no-op or double-write.

    ⚠ EVERY ENTRY HERE NAMES `C24` AND SAYS IT IS A SECOND SCOPE. The one failure this must not permit is a
    roadmap sentence that reads as if the ORIGINAL background had been re-run to include C397. It was not,
    and the two runs are never merged."""
    r = res["results"]
    art = ("research/modalities/categorical-decoy-null-lbd.json -> "
           "results.★_cysteine_level_background_at_gate_12 / results.★_nr4a3_per_cysteine_vs_that_background")
    scope = r.get("⛔_nr4a3_harness_scope") or {}
    win = scope.get("trimmed_window_uniprot")
    inside = scope.get("inside_the_trimmed_window")
    spread = ((res.get("pair_plan") or {}).get("window_size_spread") or {})
    link = "[`categorical-decoy-null-lbd.json`](../modalities/categorical-decoy-null-lbd.json)"
    plink = "[`categorical-decoy-null-lbd-plan.json`](../modalities/categorical-decoy-null-lbd-plan.json)"
    both = (f"row-level {g['summary']}; {g['c397_summary']}")
    c397_line = (f"**{g['c397_verdict']}** for C397 — {g['c397_summary']}")

    entries = [
        # ---- §3b.1: the new configuration item, and the count that names how many there are -------------
        ME.edit(text, "§3b.1 configuration register — the C24 row",
                '| **C23** | **the co-fold "ordered interface" criterion**',
                "`C24` is a NEW frozen definitional choice and §3b's own rule is that a number depending on "
                "one must name it inline. The percentile for C397 depends entirely on this scope, so the "
                "scope needs an id before the number may be quoted anywhere.",
                art,
                ME.append_after_line(
                    "| **C24** | **the SECOND decoy-null domain trim** — the reference-anchored LBD window "
                    "| the residue-number span aligned to the **committed NR4A3 LBD construct** "
                    f"(UniProt **{(res.get('lbd_reference') or {}).get('uniprot_span')}**) by "
                    "**Smith-Waterman local** alignment, BLOSUM62, gaps −11/−1; refusals at reference "
                    f"coverage < **{LBD_MIN_REF_COVERAGE}** or window < **{LBD_MIN_WINDOW_LEN}** residues. "
                    "⭑ **No pLDDT criterion at all** | **pre-registered 2026-08-03** in "
                    f"{plink}, before any model was trimmed under it and before any statistic under it "
                    "existed, and committed to git ahead of the numbers — the same registering act as "
                    "`C14`/`C15`/`C17`, and like every item here **changing it is trimcrae's** | "
                    "[`categorical_decoy_null.PREREG_LBD` / `lbd_window`]"
                    "(../modalities/categorical_decoy_null.py) | ⛔ **whether a percentile may be quoted for "
                    f"C397 at all.** It keeps UniProt {win} of the NR4A3 model, so the committed unique set "
                    f"{inside} is in scope, C397 included. ⚠ It is **NOT** a widening of `C16` — `C16` "
                    "stands, both runs stand, and their rows are never pooled | ✅ frozen |")),
        ME.edit(text, "§3b.1 register — the item count", "**23 items.** Status:",
                "The register states how many items it holds and `C24` makes it 24. ⚠ A count that "
                "disagrees with the table below it is exactly the drift §3b exists to stop.",
                art, ME.replace_in_line("**23 items.**", "**24 items.**")),
        ME.edit(text, "§3b.1 register — the C16 row", "| **C16** | **the decoy-null domain trim**",
                "`C16`'s row currently ends with *'no percentile may be quoted for C397'* and *'the trim "
                "must not be widened after the fact'*. BOTH remain true of `C16` and neither is edited. "
                "What the row is missing is that a SECOND scope now exists — a reader who stops at this row "
                "would conclude the gap is still open.",
                art,
                ME.append_to_line(
                    " ⭑ **A SECOND, INDEPENDENTLY PRE-REGISTERED scope now covers C397 — `C24`, not a "
                    f"widening of this one.** {link}. `C16` stands unchanged and the two backgrounds are "
                    "never pooled.")),

        # ---- §3.4 fact 4: the caveat's one home ----------------------------------------------------------
        ME.edit(text, "§3.4 fact 4 — the caveat that travels with the percentile",
                "⛔ **BUT THE PERCENTILE MAY NOT BE QUOTED FOR C397, AND THIS IS NOT A DETAIL.**",
                "§3.4 fact 4 is the caveat's ONE HOME and it currently ends by naming the honest repair — a "
                "separate test with its own pre-registered trim. That test has now been run, so this is the "
                "line that must carry its result or the caveat will be quoted after it has been addressed.",
                art,
                ME.append_to_line(
                    f" ⭑ **AND THAT SEPARATE TEST HAS NOW BEEN RUN ({SCOPES['lbd']['configuration_id']}, "
                    f"2026-08-03, $0 CPU/CI):** {link}. It is a SECOND scope, not a widened one — `C16` is "
                    f"untouched and the two are never pooled. Its NR4A3 window is UniProt {win}, so C397 IS "
                    f"in scope, and it adds a **cysteine-level** background (one point per decoy "
                    f"target-unique cysteine) because a pooled per-pair row cannot give one residue a "
                    f"percentile. Result: {c397_line}. ⚠ Still an **AlphaFold-model** row, not the committed "
                    "opened-model row and not an 8XTT row — 8XTT was refused precisely because the decoys "
                    "have no experimental structures and a background must share its target's structure "
                    "source.")),

        # ---- §3.1 V17 and §3.2 R8: the two places the 'does not contain C397' sentence is quoted ---------
        ME.edit(text, "§3.1 instrument table — row V17",
                "the NR4A3 arm of that background does not contain C397",
                "`V17`'s row states the C397 gap as a live limit. It is still true OF `C16`, and it is no "
                "longer the whole picture — leaving it bare would have the instrument table contradict "
                "§3.4 fact 4.",
                art,
                ME.replace_in_line(
                    "the NR4A3 arm of that background does not contain C397**, so no percentile may be "
                    "quoted for the program's headline residue",
                    "the NR4A3 arm of that background does not contain C397**, so no percentile may be "
                    "quoted for the program's headline residue *from that run*. ⭑ **A SECOND, "
                    f"independently pre-registered scope (`C24`) does contain it** — {link}, "
                    f"{c397_line}")),
        ME.edit(text, "§3.2 R×V coverage matrix — row R8", "its NR4A3 arm does **not** contain C397",
                "The `R8` coverage cell carries the same limit and must move with it, or the matrix and "
                "§3.4 will disagree about whether the gap is open.",
                art,
                ME.replace_in_line(
                    "its NR4A3 arm does **not** contain C397",
                    "`C16`'s NR4A3 arm does **not** contain C397, and the second scope `C24` does — "
                    f"{link}, {c397_line}")),

        # ---- §10.1 row 29 and Q2: the ranked rows this job belongs to ------------------------------------
        ME.edit(text, "§10.1 row 29 — the C02 row",
                "| **29** | **The categorical axis's cross-system decoy null (`C02`)**",
                "Row 29 records the C397 gap as WHAT IS STILL OPEN and names the repair. The repair is now "
                "done, so the row must say so — §10.3's own lesson is that a caveat with nowhere to go is "
                "how work gets silently dropped, and a repair with nowhere to land is the same defect "
                "inverted.",
                art,
                ME.append_to_line(
                    f" ⭑ **THE REPAIR IS DONE, 2026-08-03 ($0 CPU/CI): `C02-L` under a SECOND "
                    f"pre-registered scope (`C24`, the reference-anchored LBD window), which contains C397.** "
                    f"{both}. ⛔ It is **not** a widening of `C16` and does **not** supersede this row's "
                    f"result — both runs stand and their rows are never pooled. Numbers: {link}; design and "
                    f"pairs: {plink}")),
        ME.edit(text, "§10.1a option queue — the `Q2` calibration-gap row",
                "| **Q2** | **Close the categorical axis's calibration gap**",
                "`Q2` IS this job, stated in the roadmap's own words: *'re-run the NR4A3 arm of the decoy "
                "background under a separately pre-registered trim that contains C397'*. It has been done "
                "exactly that way — a separate pre-registration, committed before the numbers, with `C16` "
                "left untouched.",
                art,
                ME.append_to_line(
                    f" ⭑ **ANSWERED 2026-08-03 ($0 CPU/CI), by the first branch and not the second:** a "
                    f"separately pre-registered scope `C24` that contains C397, with `C16` unwidened and "
                    f"both runs standing. {both}. {link}")),
    ]

    # ---- §8 Route B — the direction the result actually points --------------------------------------
    if g["c397_verdict"] == "DISTINGUISHED":
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "The categorical GO's headline residue now has a measured background of its own. That belongs "
            "next to the claim, with its limits, not in a footnote.",
            art, ME.append_after_line(
                f"\n★ **C397 now has a measured cross-system background of its own (`C24`, 2026-08-03).** "
                f"{g['c397_summary']} — {link}. ⛔ **What this licenses and nothing more:** that the "
                "categorical SCREEN fires on NR4A3 more rarely-by-chance than on an arbitrary close human "
                "paralogue pair, over the LBD, at the 12-atom gate, on AlphaFold models, inside a "
                "NUCLEAR-RECEPTOR universe. **Not** binding, reactivity, adduct formation, degradation, "
                "efficacy or safety; and linker length and exit vector remain conditional on the "
                "docked-pose anchors (`R5`) — cysteine uniqueness and paralogue burial are the "
                "pose-independent half.")))
    elif g["c397_verdict"] in ("NOT DISTINGUISHED", "UNDERPOWERED"):
        entries.append(ME.edit(
            text, "§8 Route B", "### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine",
            "⛔ With C397 finally IN scope, the background does not separate it (or cannot, at this n). "
            "That is a blocker on the argument, not on the chemistry, and it is the V20 shape — it must be "
            "filed as one rather than left to the reader to infer from an artifact.",
            art, ME.append_after_line(
                f"\n⛔ **C397's own cross-system background is `{g['c397_verdict']}` (`C24`, 2026-08-03).** "
                f"{g['c397_summary']} — {link}. Until that changes the categorical result may be reported "
                "as a *screen output*, never as an *enrichment*, and the headline residue carries no "
                "percentile claim.")))
    return entries


def _stamp():
    return {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "et": time.strftime("%Y-%m-%d %I:%M %p ET", time.localtime(time.time() - 4 * 3600)),
            "generator": "research/modalities/categorical_decoy_null.py"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["plan", "probe", "fetch", "pairs", "selfcheck", "run", "reduce"])
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    # ⚠ `--scope` must be resolved BEFORE `--out`'s default is read, or a scoped run would silently write
    #   over the other scope's artifact. That is the one mistake here that would produce a wrong file with
    #   no error at all, so the default is deliberately None and filled in after `set_scope`.
    ap.add_argument("--scope", default=os.environ.get("DECOY_SCOPE", "plddt"), choices=sorted(SCOPES),
                    help="plddt = the committed C02 run (C16). lbd = the reference-anchored LBD window "
                         "(C24), a SECOND pre-registered scope, never a widening of the first.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    sc = set_scope(args.scope)
    if args.out is None:
        args.out = OUT
    print(f"  [cdn] scope={args.scope} ({sc['configuration_id']}) plan={os.path.basename(PLAN)} "
          f"out={os.path.basename(args.out)}")
    return {"plan": mode_plan, "probe": mode_probe, "fetch": mode_fetch, "pairs": mode_pairs,
            "selfcheck": mode_selfcheck, "run": mode_run, "reduce": mode_reduce}[args.mode](args)


if __name__ == "__main__":
    main()
