#!/usr/bin/env python3
"""`C25` — THE CROSS-SYSTEM DECOY NULL FOR THE STERIC-EXCLUSION AXIS (`S3` / `M3` / `M4`).

★★ WHY THIS EXISTS, AND WHY IT IS THE DECISIVE TEST FOR `S3` RIGHT NOW.

`S3` reports a paralogue-only clash rate of **0.923** at the three Pocket-5 positions where NR4A3's residue
is paralogue-unique AND both paralogue side chains are strictly bulkier, against **0.173** at conserved or
shared positions — an enrichment of 5.34x. That null is WITHIN THE SYSTEM: it is measured on NR4A3, against
NR4A1 and NR4A2, on one superposition. There is no decoy, no cross-system background, nothing that answers

        "does an ARBITRARY close paralogue pair, pushed through the IDENTICAL pipeline,
         also produce a ~5x contrast?"

⛔ THAT IS EXACTLY THE GAP THE CATEGORICAL AXIS HAD UNTIL 2026-08-03, AND CLOSING IT CHANGED THE READING.
`C24`'s cross-system background found `frac_exactly_zero = 0.56` at the cysteine level, so the categorical
screen's clean `P = 0` on C397 sat at roughly the 56th percentile of a background whose MODAL OUTCOME WAS
ALSO ZERO. The headline was not distinctive; it was ordinary. This file asks the same question of `S3`
before anyone writes the same sentence about it.

★ WHAT IS HELD IDENTICAL, AND WHY THAT IS THE WHOLE POINT. A background computed by a RE-IMPLEMENTATION is
a different instrument and its distribution means nothing. So:

  * the CLASH DEFINITION is `selectivity_mechanism_options.HARD_CLASH_A` (3.0 A), imported;
  * the SUPERPOSITION is `nr4a3_basin_search.superpose_paralogue`, the same iterative-core-refinement fit
    `M3` uses, called with the same (mobile, ref) contract;
  * the STATISTIC is `steric_design_rule.score_pose`, called unchanged — which is why this module builds its
    `geometry` blocks with the ROLE keys `NR4A1` / `NR4A2` that `score_pose` iterates. Those keys are ROLES
    in a decoy arm, never gene claims, and every row carries its `role_map`;
  * the VOLUME treatment is `steric_design_rule.denied_lobe`, called unchanged, at the same `GRID_A`, and
    the design-target bar stays each arm's OWN null-class largest lobe — never NR4A3's 11.78 A^3, which
    would import NR4A3's scale into the background;
  * the POSES are the same 13 committed selectivity-matrix molecules;
  * the CLASS RULE is `nr4a_paralogue_unique_residues.classify_positions` (two independent aligners, both
    must agree) plus the strictly-bulkier side-chain heavy-atom test — the same two predicates `M3` uses;
  * the STRUCTURE SOURCE, TRIM and PAIR-SELECTION rules are `categorical_decoy_null`'s, imported and run at
    `--scope lbd`, i.e. `C24`'s reference-anchored LBD window and `C24`'s answer-blind ranking.

⛔ THE ONE THING THAT CANNOT BE HELD IDENTICAL, STATED UP FRONT RATHER THAN DISCOVERED LATER. The 13 poses
were DOCKED INTO NR4A3's opened model. No such docked set exists for a decoy, and re-docking with a
different engine would be a different instrument. So `full_trio` arms carry the poses into the decoy
target's frame by the same superposition, and every arm — INCLUDING the index arm — then drops any pose that
clashes with its own target. That makes "the target does not clash" true by construction everywhere, which
is the property NR4A3's docked poses have and the property `score_pose`'s predicate assumes. `n_poses_used`
is reported per arm and is a gradeability quantity, never a silent filter.

⚠ AND THE `M4` CEILING TRAVELS WITH EVERY CONTRAST IN THIS FILE, because it caps what any of them can mean:
the paralogue RELOCATES these molecules by a median ~5.3 A rather than refusing them, so `S3` constrains a
POSE and never "the paralogue cannot bind this molecule". The transfer is RIGID (side chains held in their
own conformer), and NR4A3's absence of clash is GUARANTEED BY CONSTRUCTION and carries no information — only
the between-class contrast is gradeable, which is why `score_pose` refuses to emit a signal without its null.

CLI:  python3 steric_decoy_null.py plan       # the PRE-REGISTRATION — no network, no statistic
      python3 steric_decoy_null.py smoke      # the full_trio code path, committed models, no network
      python3 steric_decoy_null.py fetch      # AlphaFold DB models (network; CI)
      python3 steric_decoy_null.py pairs      # trim + all-vs-all identity + answer-blind selection
      python3 steric_decoy_null.py selfcheck  # known-answer: reproduce the committed M3 rates
      python3 steric_decoy_null.py run        # the two backgrounds + the percentiles
      python3 steric_decoy_null.py remap      # re-anchor the committed artifact's map edits ($0, no recompute)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import categorical_decoy_null as CDN          # noqa: E402  fetch/trim/select/percentile — C24's own code
import map_edits as ME                        # noqa: E402
import nr4a3_basin_search as B                # noqa: E402  load_paralogue / superpose_paralogue
import nr4a_differential_atlas as ATLAS       # noqa: E402  nw_align
import nr4a_paralogue_dynamics as PD          # noqa: E402  wilson95
import nr4a_paralogue_unique_residues as U    # noqa: E402  classify_positions / _read_sdf_coords
import selectivity_mechanism_options as S     # noqa: E402  HARD_CLASH_A / POCKET5 / _sidechain / STRUCT
import steric_design_rule as SDR              # noqa: E402  score_pose / denied_lobe — reused UNCHANGED

OUT_JSON = os.path.join(HERE, "steric-decoy-null.json")
OUT_MD = os.path.join(HERE, "steric-decoy-null.md")
PLAN_JSON = os.path.join(HERE, "steric-decoy-null-plan.json")

#: The two partner ROLE keys `steric_design_rule.score_pose` iterates. In a decoy arm these are ROLES filled
#: by two arbitrary receptors, and every arm carries a `role_map` saying which. Naming them anything else
#: would mean forking `score_pose`, which is the one thing this file must not do.
ROLES = S.PARALOGUES                          # ("NR4A1", "NR4A2")

ALL_AA = tuple("ACDEFGHIKLMNPQRSTVWY")

CONFIG_ID = "C25"


# =============================================================================================================
# THE PRE-REGISTRATION. Emitted by `plan`, with no network call and no statistic in scope.
# =============================================================================================================
PREREG = {
    "_frozen": (
        "Design fixed BEFORE any structure was fetched under this rule and before any statistic under it "
        "existed. `plan` emits this block from constants alone — it reads no model, no alignment and no "
        "result, so a plan file and a result file cannot disagree about what was registered."),
    "_configuration_id": CONFIG_ID,
    "question": (
        "The steric-exclusion axis `S3` reports 0.923 paralogue-only clash at bulkier-in-both positions "
        "against a 0.173 null at conserved/shared positions (5.34x), and it has a WITHIN-SYSTEM null only. "
        "Does an ARBITRARY close paralogue pair, pushed through the IDENTICAL pipeline, also produce that "
        "contrast? If most do, the contrast is a property of the METHOD, not of NR4A3."),
    "★_why_this_is_asked_now": (
        "Because the same gap was closed on the categorical axis hours earlier and the answer was NOT "
        "flattering: `C24` measured `frac_exactly_zero = 0.56` at the cysteine level, so a clean P = 0 sat "
        "at roughly the 56th percentile — zero was the MODAL outcome. A headline with no cross-system "
        "background is a headline nobody can grade, in either direction."),

    "two_backgrounds_never_pooled": {
        "⛔_rule": (
            "These are two separate tests answering two different questions. Their rows are NEVER merged "
            "into one background, neither supersedes the other, and every percentile names which one it "
            "came from. Same discipline as `C24`'s two scopes."),
        "partner_swap": {
            "role": "PRIMARY",
            "what_varies": "the PARTNER PAIR only",
            "construction": (
                "target = the committed NR4A3 opened model (`results/nr4a3-matrix/nr4a3-opened.pdb`), poses "
                "= the 13 committed docked molecules, positions = Pocket-5 (`C5`). The two proteins playing "
                "the paralogue ROLES are an arbitrary close pair from the universe, superposed onto NR4A3 "
                "by the same `superpose_paralogue` call `M3` makes."),
            "★_why_it_is_the_primary": (
                "It is the only construction in which EVERYTHING except the swapped pair is byte-identical "
                "to `M3`: same target, same poses, same frame, same by-construction absence of target "
                "clash. It therefore isolates the question exactly — is the NR4A1/NR4A2 pair special, or "
                "would any close homologue pair produce this contrast?"),
            "⚠_what_it_cannot_answer": (
                "It never varies the TARGET or the POSES, so it cannot say whether an arbitrary close "
                "paralogue SYSTEM produces the contrast. That is what `full_trio` is for."),
        },
        "full_trio": {
            "role": "SECONDARY",
            "what_varies": "the target AND both partners",
            "construction": (
                "a trio {T, A, B} from the universe. T is superposed into the NR4A3 pose frame by "
                "`superpose_paralogue(T, nr4a3_opened)`; A and B are then superposed onto T-as-placed by the "
                "same function, so the partners are fitted to THEIR OWN target exactly as in `M3`. "
                "Positions = Pocket-5 mapped onto T through the same `corr_from_ref` chain. Poses = the "
                "same 13 molecules, unmoved."),
            "⚠_the_asymmetry_it_carries_and_the_reading_that_follows": (
                "The poses were docked into NR4A3, not into T. The per-arm pose filter below removes the "
                "resulting bias in the FIRING statistic (a pose that clashes with its own target is dropped "
                "in every arm, index included), but it cannot remove the SELECTION effect: an arm whose "
                "target fills the pocket keeps fewer poses and may fall below the gradeability floor. "
                "PRE-REGISTERED READING, asymmetric on purpose: a HIGH `full_trio` background is decisive "
                "against distinctiveness; a LOW one is UNINTERPRETABLE, because pose attrition and a real "
                "absence of contrast are not separable here. `partner_swap` carries no such asymmetry."),
            "⛔_A_MEASURED_PREDICTION_MADE_BEFORE_ANY_DECOY_WAS_FETCHED": (
                "The `smoke` mode runs this exact construction on the three COMMITTED opened models with "
                "NR4A1 as target — a trio whose answer is meaningless and whose plumbing is the decoys' — "
                "and it returns **0 of 13 poses surviving the target-clash filter**. That is not a "
                "surprise once stated: `M3`'s own per-pose table shows NR4A1's side chains clashing at "
                "2-5 of the 10 Pocket-5 positions for EVERY pose, which is the whole reason the steric "
                "signal exists. So it is registered HERE, in advance and with its evidence, that "
                "`full_trio`'s CLASH contrasts are EXPECTED TO BE UNGRADEABLE, and that this is a property "
                "of transporting a docked pose set, not a finding about any decoy. ⭑ What `full_trio` "
                "therefore contributes is its POSE-FREE half — the denied-lobe VOLUME axis, which needs no "
                "ligand at all and is unaffected by pose attrition. Predicting this before the run is the "
                "difference between a limitation and an excuse."),
        },
    },

    "universe_and_structures": {
        "universe": (
            "`research/modalities/nr4a-superfamily-selectivity.json` -> `ranking[]` — 47 human nuclear "
            "receptors with UniProt accessions, a COMMITTED artifact. The same universe `C24` used; not "
            "re-picked here."),
        "decoy_roles_exclude_the_NR4A_family": (
            "NR4A1, NR4A2 and NR4A3 are removed from the decoy candidate pool. They are the INDEX arm; a "
            "decoy row containing one of them would not be a decoy."),
        "models": (
            "AlphaFold DB model of each accession, fetched by `categorical_decoy_null.fetch_af` — the same "
            "function, the same URL template, the same version fallback."),
        "trim": (
            "`categorical_decoy_null.trim_one` at `--scope lbd`, i.e. `C24`'s REFERENCE-ANCHORED LBD WINDOW "
            "(Smith-Waterman local alignment to the committed NR4A3 LBD construct). Imported, not restated: "
            "`C24` is the home of that rule and this file inherits it rather than freezing a second one."),
        "⚠_index_arm_partner_source": (
            "The decoys' partners are AlphaFold models, so the MATCHED index row uses AlphaFold models of "
            "NR4A1 and NR4A2 too — `C24`'s discipline, which refused 8XTT for exactly this reason. The "
            "committed OPENED NR4A1/NR4A2 models are also scored, as the reference row that must reproduce "
            "`M3`. Both are reported; the percentile is quoted for the matched row and the mixed-source "
            "percentile is reported beside it, labelled."),
        "⚠_index_arm_target_source": (
            "The target stays the committed NR4A3 OPENED model in both backgrounds, because the poses were "
            "docked into it and a pose set is meaningless in another frame. In `full_trio` the decoy "
            "targets are AlphaFold models, so the target SOURCE is not matched there. Stated, not hidden — "
            "and it is the reason `full_trio` is secondary."),
    },

    "selection_rule": {
        "⛔_answer_blind": (
            "Pairs and trios are chosen on SEQUENCE IDENTITY and STRUCTURE AVAILABILITY alone, both of "
            "which are fixed before any clash, lobe or rate exists. No arm is ever selected, dropped or "
            "re-ranked on what it scored."),
        "pairs": (
            "`categorical_decoy_null.select_pairs`, imported unchanged: identity band [0.35, 0.90], "
            "alignment coverage >= 0.6, ranked by |identity - reference identity| ASCENDING, taken greedily "
            "subject to `max_per_protein = 2`. The reference identity is the mean of the measured "
            "NR4A3-vs-NR4A1 and NR4A3-vs-NR4A2 trimmed-window identities, computed by the same code."),
        "max_pairs": 20,
        "_why_20": (
            "Held identical to `C24`'s budget, which is itself on record with its reason: a percentile "
            "against 8 points cannot resolve finer than 1/8 = 0.125. 20 gives 0.05. Chosen as an "
            "inheritance, not as a fresh number, so it cannot be read as tuned."),
        "pair_orientation": (
            "an unordered pair contributes ONE arm. `score_pose`'s predicate is symmetric in the two "
            "partners (`all(...)` over both), so A-as-first and B-as-first are the SAME measurement — "
            "emitting both would double-count, which is the opposite of `C24`'s situation where the "
            "target/paralogue roles are asymmetric."),
        "trios": (
            "unordered triples whose three pairwise identities all clear the same band and coverage floor, "
            "ranked by |mean pairwise identity - the NR4A trio's own mean pairwise identity| ASCENDING, "
            "taken greedily subject to `max_per_protein = 2`. Each selected trio contributes THREE arms — "
            "each member as target once — because choosing which member is 'the target' would be a choice "
            "with no answer-blind rule behind it."),
        "max_trios": 12,
        "⚠_clustering": (
            "the three arms of one trio share proteins and the pairs share proteins under "
            "`max_per_protein = 2`, so the effective n is below `n_graded`. Every background summary "
            "reports `n_distinct_proteins` beside `n`, and the Wilson interval is, if anything, optimistic."),
    },

    "statistic": {
        "computed_by": "steric_design_rule.score_pose(heavy_xyz, geometry, HARD_CLASH_A) — UNCHANGED",
        "per_pose_per_position_predicate": (
            "FIRED = both partner side chains come within HARD_CLASH_A (3.0 A) of a pose heavy atom AND the "
            "target's side chain does not. Identical to `M3`."),
        "classes": {
            "unique_and_both_bulkier": (
                "the target's residue TYPE is absent from both partners at the aligned position, "
                "alignment-robust under two independent aligners, AND both partner side chains carry "
                "strictly more heavy atoms than the target's. THE SIGNAL CLASS."),
            "unique_not_bulkier": (
                "unique but not strictly bulkier in both. On NR4A3 this class fires at 0.000, which is the "
                "discriminating behaviour: uniqueness alone creates no steric exclusion. THE SECOND "
                "CONTRAST, and it is a separate claim from the first — never pooled with it."),
            "conserved_or_shared": "the target's residue type appears in at least one partner. THE NULL.",
        },
        "contrast_a": {
            "primary": "signal_rate - null_rate (`score_pose`'s own `signal_minus_null`, which the module's "
                       "`how_to_score_a_new_candidate` names as the quantity to accept on)",
            "secondary": "signal_rate / null_rate — the 5.34x enrichment as usually quoted",
            "⚠_undefined_ratios": (
                "an arm whose null rate is exactly 0 has an UNDEFINED ratio. It is reported as null and "
                "counted in `n_enrichment_undefined` — never set to infinity, never dropped, and never "
                "silently excluded from the difference background where it IS defined."),
        },
        "contrast_b": {
            "primary": "the unique_not_bulkier rate. NR4A3 = 0.000.",
            "⛔_the_modal_value_trap": (
                "if NR4A3's value equals the background's modal value then its percentile IS that modal "
                "frequency — ONE measurement, not two — and the artifact must say so in those words. This "
                "is the sentence `C24` got right and it is the single most useful line in that artifact."),
        },
        "volume_axis": {
            "computed_by": "steric_design_rule.denied_lobe(...) — UNCHANGED, same GRID_A",
            "bar": (
                "each arm's OWN null-class largest lobe, exactly as `steric_design_rule` measures it for "
                "NR4A3. ⛔ NOT NR4A3's 11.78 A^3 — importing the index arm's scale into the background "
                "would make the bar a property of NR4A3 rather than of the arm."),
            "statistic": "fraction of that arm's signal-class positions whose lobe exceeds its own bar",
            "gradeability": (
                "an arm's volume axis is GRADED only when it has >= 1 unique_and_both_bulkier position AND "
                ">= 1 conserved_or_shared position, because without the second there is no MEASURED bar and "
                "the absolute sanity floor is a chosen number."),
            "★_why_this_axis_matters_most_for_full_trio": (
                "it needs no ligand, so it is untouched by the pose attrition registered above. It is the "
                "half of `S3` that a transported pose set cannot damage."),
        },
    },

    "poses": {
        "set": "the 13 committed selectivity-matrix molecules, results/nr4a3-matrix/docked_nr4a3.sdf",
        "per_arm_filter": (
            "a pose is DROPPED from an arm if it clashes with that arm's TARGET side chain at any mapped "
            "position. Applied identically to every arm, index included."),
        "_why": (
            "`score_pose`'s predicate requires the target NOT to clash, and on NR4A3 that is true by "
            "construction because the poses were docked in. Applying the filter everywhere makes the same "
            "property hold by construction in every arm instead of quietly depressing the decoys."),
        "⚠_it_costs_the_index_arm_a_pose": (
            "one committed pose clashes with NR4A3 at two Pocket-5 positions, so the filtered index row is "
            "NOT the committed 0.923/0.173. The committed value is reported beside it as the reference, and "
            "the unfiltered rates are reported for every arm as a declared sensitivity."),
    },

    "gradeability": {
        "min_conditioning_events": 20,
        "_source": (
            "held byte-identical to `C24`'s `gradeability_min_conditioning_events = 20`. Not a fresh "
            "choice — an inheritance, so it cannot have been set by looking at these rows."),
        "definition": (
            "a class is GRADED when it has >= 20 (pose x position) cells in that arm, i.e. "
            "`n_poses_used * n_positions_in_class >= 20`. Contrast (a) needs BOTH the signal class and the "
            "null class graded; contrast (b) needs the unique_not_bulkier class graded."),
        "⛔_the_floor_does_not_move": (
            "`C24`'s NR4A3 arm reached 12 conditioning events against this same floor of 20 and could not "
            "be graded. Raising or lowering the floor after seeing which rows bind is the same class of act "
            "as widening a scope after seeing a residue fall outside it. The floor is fixed here; the count "
            "of rows that clear it is a RESULT."),
        "min_graded_for_a_verdict": 5,
    },

    "verdict_rule": {
        "DISTINCTIVE_requires_all_of": [
            "n_graded >= 5 in the background being quoted",
            "NR4A3's percentile >= 0.75 — i.e. at most a quarter of the background reaches its contrast",
            "for contrast (b): the background's frac_exactly_zero <= 0.5, because in a background where "
            "most arms also return 0 a 0 from NR4A3 means nothing — the `C24` failure mode exactly",
        ],
        "otherwise": "NOT DISTINGUISHED, or UNGRADEABLE when n_graded < the floor",
        "⛔_both_halves_are_needed": (
            "a favourable percentile computed against a background whose modal value equals NR4A3's own is "
            "not evidence. `grade()` is the one home of this rule and the SAME thresholds grade both "
            "backgrounds and both contrasts; only the numbers going in differ."),
    },

    "what_a_favourable_result_licenses": {
        "★_it_licenses": (
            "that the steric-exclusion CONTRAST is larger on NR4A3/NR4A1/NR4A2 than on an arbitrary close "
            "human nuclear-receptor pair pushed through the identical geometry — on one opened NR4A3 "
            "conformer, one superposition, 13 poses, at a 3.0 A hard-clash radius, inside a "
            "NUCLEAR-RECEPTOR universe."),
        "⛔_it_does_NOT_license": [
            "no statement about binding, affinity, a selectivity ratio or any free energy — none is "
            "computed anywhere in this file",
            "⛔ NOT that the paralogue fails to bind these molecules. `M4` measures that it RELOCATES them "
            "by a median 5.31 A (NR4A1) / 5.26 A (NR4A2), so the rule constrains a POSE and nothing more",
            "nothing about degradation, efficacy, safety, a therapeutic window or clinical readiness",
            "no claim of proteome-wide selectivity: a nuclear-receptor background does not bound the rate "
            "over the proteome",
            "⚠ no escape from `R5` — the whole axis is conditional on the cryptic pocket being the right "
            "site, and the pose known-answer test `V3` returned INCONCLUSIVE on site selection",
            "⚠ RIGID TRANSFER throughout: partner side chains are held in their own conformer and could "
            "rotate away. 'Denied in this conformer' is never 'denied'",
        ],
    },

    "⛔_no_tuning": [
        "no re-picking of pairs or trios after seeing a score",
        "no adjustment of HARD_CLASH_A, GRID_A or the design-target volume bar",
        "no dropping of a decoy arm because it scored high",
        "no moving of the gradeability floor in either direction",
        "if the contrast is not distinctive, that IS the finding and it is reported as directly as `C24` "
        "reported its own",
    ],
}


# =============================================================================================================
# small pure helpers
# =============================================================================================================
def _r(x, n=4):
    return None if x is None else round(float(x), n)


def _stamp():
    return {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "et": time.strftime("%Y-%m-%d %I:%M %p ET", time.localtime(time.time() - 4 * 3600)),
            "generator": "research/modalities/steric_decoy_null.py"}


def seq_index_of_rid(model, rid):
    """1-based index of local residue id `rid` in `model['seq']`, or None. PURE.

    ⛔ THE BRIDGE, AND IT IS ARM-SPECIFIC — GETTING IT WRONG IS SILENT. `classify_positions` works in the
    coordinates of the SEQUENCE IT WAS HANDED, and the structure works in residue ids. When the sequence
    handed over is the full UniProt sequence the bridge is `rid + LOCAL_OFFSET`; when it is the MODEL's own
    sequence the bridge is this function. Using one where the other belongs mis-keys every class lookup and
    the result still looks like a plausible set of rates — measured here on 2026-08-03: it turned `M3`'s
    0.923 / 0.000 / 0.173 into 0.769 / 0.115 / 0.446 with no error raised anywhere. That is exactly the
    "a populated field is not a measured one" failure, so the bridge is now passed in explicitly by every
    caller rather than assumed.
    """
    try:
        return model["ids"].index(rid) + 1
    except ValueError:
        return None


def uniprot_index_of_rid(_model, rid):
    """The other bridge: local residue id -> UniProt position, for arms handed FULL UniProt sequences."""
    return None if rid is None else rid + U.LOCAL_OFFSET


def mode_of(xs, ndigits=3):
    """Most common rounded value of a background column, with its frequency. PURE.

    ⛔ WHY THIS EXISTS. `C24`'s most useful sentence is the one that says a percentile computed against a
    background whose MODAL value equals the target's own value is one measurement wearing the costume of
    two. That check has to be mechanical, not remembered.
    """
    vals = [round(float(x), ndigits) for x in xs if x is not None]
    if not vals:
        return None
    counts = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.items(), key=lambda kv: (kv[1], -abs(kv[0])))
    return {"value": top[0], "count": top[1], "frac": top[1] / len(vals), "n": len(vals)}


def grade(n_graded, percentile, frac_exactly_zero, min_graded=None):
    """THE PRE-REGISTERED VERDICT RULE. PURE, and the ONE HOME of these thresholds.

    The same rule and the same thresholds grade both backgrounds and both contrasts; only the numbers going
    in differ. Both halves are needed: in a background where most arms return the same value NR4A3 returns,
    a favourable percentile is not evidence — that is precisely the `C24` failure mode.
    """
    floor = PREREG["gradeability"]["min_graded_for_a_verdict"] if min_graded is None else min_graded
    if not n_graded or n_graded < floor:
        return "UNGRADEABLE_too_few_graded_rows"
    if percentile is None:
        return "UNGRADEABLE_no_index_value"
    if frac_exactly_zero is not None and frac_exactly_zero > 0.5:
        return "NOT DISTINGUISHED"
    return "DISTINCTIVE" if percentile >= 0.75 else "NOT DISTINGUISHED"


def percentile_above(value, background):
    """Fraction of `background` STRICTLY BELOW `value`, i.e. how far up the background `value` sits. PURE.

    ⚠ Deliberately NOT `categorical_decoy_null.percentile_of`, which counts `<=`. Here a HIGH contrast is
    the favourable direction, so ties must not be counted as beaten — a background arm that equals NR4A3
    is a background arm that reproduced NR4A3, and calling that a win is the exact over-reading this file
    exists to prevent. `frac_at_or_above` is reported beside it so both conventions are visible.
    """
    xs = [b for b in background if b is not None]
    if not xs:
        return None
    return sum(1 for b in xs if b < value) / len(xs)


# =============================================================================================================
# ARM CONSTRUCTION — one function, used by the index arm and by every decoy arm alike
# =============================================================================================================
def build_geometry(target_model, partner_models, positions_target_rid, seqs, seq_names, seq_index_of):
    """The `geometry` block `score_pose` consumes, plus the class of every position. PURE-ish (no I/O).

    `partner_models` : {ROLE: fitted model} — already superposed onto `target_model`.
    `positions_target_rid` : {label -> target local residue id}.
    `seqs` / `seq_names` : the sequences for the class call — {name: seq} and (target_name, roleA, roleB).
    `seq_index_of(model, rid) -> int` : the arm's own bridge from a residue id to a position in the TARGET
        sequence that was handed to `classify_positions`. Passed in, never assumed — see `seq_index_of_rid`.

    ⛔ The class rule is `classify_positions` + strictly-bulkier, exactly `M3`'s two predicates. Nothing here
    re-implements either.
    """
    tname, pnames = seq_names[0], seq_names[1:]
    rows = {r["resnum"]: r for r in U.classify_positions(
        {k: seqs[k] for k in seq_names}, ref=tname, others=tuple(pnames), residue_types=ALL_AA)}

    geometry, detail = {}, {}
    for label, rid_t in positions_target_rid.items():
        sc_t = S._sidechain(target_model, rid_t) if rid_t is not None else []
        idx = seq_index_of(target_model, rid_t) if rid_t is not None else None
        row = rows.get(idx) if idx else None
        n_heavy = {"target": len(sc_t)}
        par_sc, bulkier, aligned = {}, [], True
        for role, pname in zip(ROLES, pnames):
            pm = partner_models[role]
            rid_p = pm["corr_from_ref"].get(rid_t) if rid_t is not None else None
            sc_p = S._sidechain(pm, rid_p) if rid_p else []
            par_sc[role] = sc_p
            n_heavy[role] = len(sc_p)
            bulkier.append(len(sc_p) > len(sc_t))
            if rid_p is None:
                aligned = False
        unique = bool(row and row["unique_vs_both"] and row["alignment_robust"])
        cls = ("unique_and_both_bulkier" if unique and all(bulkier)
               else "unique_not_bulkier" if unique else "conserved_or_shared")
        geometry[label] = {"class": cls, "NR4A3_sidechain": sc_t, "paralogue_sidechain": par_sc}
        detail[label] = {
            "class": cls,
            "target_residue": (target_model["aa_of"].get(rid_t) if rid_t is not None else None),
            "partner_residues": {role: partner_models[role]["aa_of"].get(
                partner_models[role]["corr_from_ref"].get(rid_t)) for role in ROLES},
            "n_side_chain_heavy": n_heavy,
            "categorically_unique_vs_both": unique,
            "alignment_robust": bool(row and row["alignment_robust"]) if row else None,
            "both_partner_side_chains_bulkier": bool(all(bulkier)),
            "all_positions_aligned": aligned,
            "post_fit_deviation_A": {
                role: _r(partner_models[role]["deviation_by_res"].get(
                    partner_models[role]["corr_from_ref"].get(rid_t)), 2) for role in ROLES},
        }
    return geometry, detail


def score_arm(geometry, ligands, clash_a=None):
    """Run `score_pose` over the pose set, with the per-arm target-clash filter. Returns the pooled rates.

    ⛔ `score_pose` is called UNCHANGED. Everything here is bookkeeping around it: which poses survive the
    filter, and how the per-pose class counts are pooled — the same pooling `steric_design_rule.build`'s
    `_pooled` does over its worked example.
    """
    clash_a = S.HARD_CLASH_A if clash_a is None else clash_a
    kept, dropped, per_pose, per_pose_unfiltered = [], [], [], []
    for title, coords in ligands:
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        # the target-clash test, on the SAME quantity `score_pose` uses
        clashing = [lab for lab, g in geometry.items()
                    if SDR._min_dist_or_none(pts, g["NR4A3_sidechain"]) is not None
                    and SDR._min_dist_or_none(pts, g["NR4A3_sidechain"]) < clash_a]
        sc = SDR.score_pose(pts, geometry, clash_a)
        sc["pose"] = title
        sc["n_heavy_atoms"] = len(pts)
        sc["target_clashing_positions"] = clashing
        per_pose_unfiltered.append(sc)
        if clashing:
            dropped.append({"pose": title, "target_clashing_positions": clashing})
        else:
            kept.append(title)
            per_pose.append(sc)

    def pooled(records):
        out = {}
        for cls in ("unique_and_both_bulkier", "unique_not_bulkier", "conserved_or_shared"):
            fired = sum(r["by_position_class"].get(cls, {}).get("fired", 0) for r in records)
            trials = sum(r["by_position_class"].get(cls, {}).get("n_positions", 0) for r in records)
            out[cls] = {"fired": fired, "conditioning_events": trials,
                        "rate": _r(fired / trials, 3) if trials else None,
                        "graded": trials >= PREREG["gradeability"]["min_conditioning_events"]}
        return out

    return {
        "n_poses_total": len(ligands),
        "n_poses_used": len(kept),
        "n_poses_dropped_target_clash": len(dropped),
        "poses_dropped": dropped,
        "by_position_class": pooled(per_pose),
        "by_position_class_UNFILTERED_sensitivity": pooled(per_pose_unfiltered),
        "per_pose": per_pose,
    }


def lobe_axis(target_model, partner_models, positions_target_rid):
    """The pose-free half: `denied_lobe` per position, and each arm's OWN measured design-target bar.

    ⛔ `denied_lobe` is called UNCHANGED at the module's own `GRID_A`, and the bar is the arm's own
    null-class largest lobe — never NR4A3's, which would import the index arm's scale into the background.
    """
    heavy = [tuple(p) for p in target_model["heavy_xyz"]]
    lobes = {}
    for label, rid_t in positions_target_rid.items():
        sc = [partner_models[role]["corr_from_ref"].get(rid_t) if rid_t is not None else None
              for role in ROLES]
        par = [S._sidechain(partner_models[role], rp) if rp else []
               for role, rp in zip(ROLES, sc)]
        lobe = SDR.denied_lobe(heavy, par, target_model["cb"].get(rid_t), S.HARD_CLASH_A)
        lobes[label] = lobe
    return lobes


def summarise_lobes(lobes, detail):
    """Per-arm volume readout: the arm's own null ceiling, and how many signal positions clear it. PURE."""
    def vol(lab):
        return lobes.get(lab, {}).get("volume_A3", 0.0) or 0.0
    null = [lab for lab in lobes if detail[lab]["class"] == "conserved_or_shared"]
    sig = [lab for lab in lobes if detail[lab]["class"] == "unique_and_both_bulkier"]
    unb = [lab for lab in lobes if detail[lab]["class"] == "unique_not_bulkier"]
    ceiling = max((vol(l) for l in null), default=None)
    bar = max(ceiling if ceiling is not None else 0.0, SDR.MIN_LOBE_VOLUME_A3)
    clearing = [l for l in sig if vol(l) > bar]
    return {
        "n_null_positions": len(null), "n_signal_positions": len(sig),
        "n_unique_not_bulkier_positions": len(unb),
        "null_volume_ceiling_A3": _r(ceiling, 2),
        "null_volume_ceiling_at": (max(null, key=vol) if null else None),
        "bar_A3": _r(bar, 2),
        "max_signal_lobe_A3": _r(max((vol(l) for l in sig), default=None), 2),
        "max_unique_not_bulkier_lobe_A3": _r(max((vol(l) for l in unb), default=None), 2),
        "signal_positions_clearing_own_bar": clearing,
        "graded": bool(sig and null),
        "⛔_why_both_are_required": (
            "the bar IS this arm's largest conserved-or-shared lobe. An arm with no null-class position has "
            "no bar of its own, and `MIN_LOBE_VOLUME_A3` is an absolute sanity floor rather than a measured "
            "ceiling — grading against it would be grading against a chosen number, which is the one thing "
            "the measured bar exists to avoid."),
        "frac_signal_positions_clearing_own_bar": (_r(len(clearing) / len(sig), 3)
                                                   if (sig and null) else None),
        "signal_over_null_volume": (_r(max(vol(l) for l in sig) / ceiling, 3)
                                    if sig and ceiling else None),
        "volumes_A3": {lab: _r(vol(lab), 2) for lab in lobes},
        "⛔_the_bar_is_this_arms_own": (
            "the bar is this arm's largest conserved-or-shared lobe, measured on this arm's own "
            "superposition — never NR4A3's 11.78 A^3."),
    }


def arm_result(name, kind, target_model, partner_models, positions, seqs, seq_names,
               ligands, role_map, extra=None, with_lobes=True, seq_index_of=seq_index_of_rid):
    """ONE arm, index or decoy, through the identical path."""
    geometry, detail = build_geometry(target_model, partner_models, positions, seqs, seq_names,
                                      seq_index_of)
    scored = score_arm(geometry, ligands)
    cls = scored["by_position_class"]
    sig, nul, unb = (cls["unique_and_both_bulkier"], cls["conserved_or_shared"],
                     cls["unique_not_bulkier"])
    row = {
        "arm": name, "kind": kind, "role_map": role_map,
        "n_positions_by_class": {k: sum(1 for lab in detail if detail[lab]["class"] == k)
                                 for k in ("unique_and_both_bulkier", "unique_not_bulkier",
                                           "conserved_or_shared")},
        "positions": detail,
        **{k: v for k, v in scored.items() if k != "per_pose"},
        "signal_rate": sig["rate"], "null_rate": nul["rate"], "unique_not_bulkier_rate": unb["rate"],
        "signal_minus_null": (_r(sig["rate"] - nul["rate"], 3)
                              if sig["rate"] is not None and nul["rate"] is not None else None),
        "enrichment_signal_over_null": (_r(sig["rate"] / nul["rate"], 3)
                                        if sig["rate"] is not None and nul["rate"] else None),
        "graded_contrast_a": bool(sig["graded"] and nul["graded"]),
        "graded_contrast_b": bool(unb["graded"]),
        "superposition": {role: {k: partner_models[role]["superposition"].get(k)
                                 for k in ("n_ca_pairs", "n_core", "core_fraction", "core_rmsd_A")}
                          for role in ROLES},
    }
    if with_lobes:
        row["volume_axis"] = summarise_lobes(lobe_axis(target_model, partner_models, positions), detail)
    if extra:
        row.update(extra)
    return row


# =============================================================================================================
# THE INDEX ARM — and the known-answer test that decides whether any of this is readable
# =============================================================================================================
def committed_models():
    ref = B.load_paralogue(os.path.join(S.STRUCT, "nr4a3-opened.pdb"))
    raw = {sp: B.load_paralogue(os.path.join(S.STRUCT, f"{sp.lower()}-opened.pdb")) for sp in ROLES}
    fit = {sp: B.superpose_paralogue(raw[sp], ref) for sp in ROLES}
    return ref, raw, fit


def ligand_set():
    return U._read_sdf_coords(os.path.join(S.STRUCT, "docked_nr4a3.sdf"))


def pocket5_positions(ref):
    return {u: (u - U.LOCAL_OFFSET) for u in S.POCKET5}


def index_committed_arm(ref, fit, ligands, seqs_cache):
    """The reference row: committed opened models, committed poses, `M3`'s own inputs.

    ⛔ THIS IS THE KNOWN-ANSWER TEST. A background measured by a harness that cannot reproduce the
    measurement it claims to calibrate is worse than no background — `nr4a1_sparing_axis.forward_self_check`
    made the same argument for the inverse direction and it is the reason that null was readable at all.
    """
    positions = pocket5_positions(ref)
    seq_names = ("NR4A3", "NR4A1", "NR4A2")
    return arm_result(
        "index_committed", "index",
        ref, fit, positions, seqs_cache, seq_names, ligands,
        role_map={r: r for r in ROLES},
        extra={"_what": ("the committed opened NR4A1/NR4A2 models and the FULL UniProt sequences — i.e. "
                         "`M3`'s own inputs, through this file's code path")},
        seq_index_of=uniprot_index_of_rid)


def selfcheck(verbose=True):
    """Reproduce `M3`'s committed rates through THIS file's arm builder. Returns the comparison."""
    ref, _raw, fit = committed_models()
    ligands = ligand_set()
    seqs = json.load(open(os.path.join(REPO, "research/modalities/nr4a-sequences-cache.json")))
    row = index_committed_arm(ref, fit, ligands, seqs)

    committed = json.load(open(os.path.join(HERE, "selectivity-mechanism-options.json")))
    m3 = committed["measurements"]["M3"]["by_position_class"]
    want = {k: m3.get(k, {}).get("rate") for k in
            ("unique_and_both_bulkier", "unique_not_bulkier", "conserved_or_shared")}
    got_unfiltered = {k: row["by_position_class_UNFILTERED_sensitivity"][k]["rate"] for k in want}
    got_filtered = {k: row["by_position_class"][k]["rate"] for k in want}

    sdr = json.load(open(os.path.join(HERE, "steric-design-rule.json")))
    want_lobes = {int(u): v.get("volume_A3") for u, v in sdr["denied_lobes"].items()}
    got_lobes = row["volume_axis"]["volumes_A3"]
    lobes_match = all(abs((got_lobes.get(u) or 0.0) - (want_lobes.get(u) or 0.0)) < 1e-6
                      for u in want_lobes)

    out = {
        "_why": ("a background computed by a harness that cannot reproduce the committed measurement is "
                 "worse than no background. This runs THIS file's arm builder on `M3`'s own inputs — the "
                 "committed opened models, the committed 13 poses, the full UniProt sequences — and "
                 "compares every rate and every denied-lobe volume against the committed artifacts."),
        "committed_M3_rates": want,
        "recomputed_UNFILTERED": got_unfiltered,
        "reproduces_committed_M3": got_unfiltered == want,
        "recomputed_after_the_per_arm_pose_filter": got_filtered,
        "n_poses_used_after_filter": row["n_poses_used"],
        "poses_dropped_by_the_filter": row["poses_dropped"],
        "committed_denied_lobe_volumes_A3": want_lobes,
        "recomputed_denied_lobe_volumes_A3": got_lobes,
        "reproduces_committed_lobes": lobes_match,
        "committed_null_volume_ceiling_A3": sdr.get("null_volume_ceiling_A3"),
        "recomputed_null_volume_ceiling_A3": row["volume_axis"]["null_volume_ceiling_A3"],
        "_if_false": ("the backgrounds in this file MUST be discarded — the code, not the biology, would "
                      "be the finding."),
        "PASS": bool(got_unfiltered == want and lobes_match),
    }
    if verbose:
        print("[steric-decoy-null] selfcheck: rates %s  lobes %s -> %s"
              % (out["reproduces_committed_M3"], out["reproduces_committed_lobes"],
                 "PASS" if out["PASS"] else "FAIL"))
    return out, row, (ref, fit, ligands, seqs)


# =============================================================================================================
# MODES
# =============================================================================================================
def mode_smoke(_args):
    """★ THE SHAKEOUT THAT NEEDS NO NETWORK — the `full_trio` code path, on the committed models.

    CLAUDE.md §6: smoke -> one real leg -> fleet. The `full_trio` arm is the only construction in this file
    that chains two superpositions and two `corr_from_ref` maps, and it is the only one that cannot be
    exercised by `selfcheck`. So it is exercised HERE, on the three committed opened models with NR4A1 as
    the target — a trio whose answer is meaningless (it contains the index system) and whose PLUMBING is
    exactly the decoys'. It is a plumbing test and it says so; no number from it is reported anywhere.
    """
    ref, raw, _fit = committed_models()
    ligands = ligand_set()
    positions_nr4a3 = pocket5_positions(ref)
    tm = raw["NR4A1"]
    fitT = B.superpose_paralogue(tm, ref)
    pm, sq = {}, {"TARGET": tm["seq"]}
    for role, m in zip(ROLES, (raw["NR4A2"], ref)):
        pm[role] = B.superpose_paralogue(m, fitT)
        sq[role] = m["seq"]
    pos = {u: fitT["corr_from_ref"].get(rid) for u, rid in positions_nr4a3.items()}
    row = arm_result("SMOKE:NR4A1<-NR4A2+NR4A3", "smoke_not_a_result", fitT, pm, pos, sq,
                     ("TARGET",) + ROLES, ligands,
                     role_map={"TARGET": "NR4A1", ROLES[0]: "NR4A2", ROLES[1]: "NR4A3"})
    print("[steric-decoy-null] SMOKE (plumbing only, NOT a result)")
    print("  positions mapped        : %d of %d" % (sum(1 for v in pos.values() if v is not None),
                                                    len(pos)))
    print("  n_positions_by_class    : %s" % row["n_positions_by_class"])
    print("  poses used / dropped    : %d / %d" % (row["n_poses_used"],
                                                   row["n_poses_dropped_target_clash"]))
    print("  signal / null / not-blk : %s / %s / %s"
          % (row["signal_rate"], row["null_rate"], row["unique_not_bulkier_rate"]))
    print("  graded a / b            : %s / %s" % (row["graded_contrast_a"], row["graded_contrast_b"]))
    print("  volume axis             : %s" % {k: row["volume_axis"][k] for k in
                                              ("null_volume_ceiling_A3", "max_signal_lobe_A3",
                                               "frac_signal_positions_clearing_own_bar")})
    ok = sum(1 for v in pos.values() if v is not None) >= 8
    print("  PLUMBING %s" % ("OK" if ok else "FAILED — position mapping collapsed"))
    return 0 if ok else 2


def mode_plan(_args):
    """Emit the PRE-REGISTRATION. No network, no structure, no statistic."""
    plan = {
        "_title": ("`C25` — cross-system decoy null for the STERIC-EXCLUSION axis (`S3`): "
                   "PRE-REGISTRATION. No statistic under this design exists yet."),
        "_status": ("INSTRUMENT CALIBRATION. $0 CPU/CI. Nothing here is a claim about binding, affinity, "
                    "reactivity, degradation, efficacy, safety or clinical readiness."),
        "_reading": ("This calibrates the STERIC SCREEN, not NR4A3. It converts 'the steric rule fired at "
                     "5.34x its own within-system null' into 'it fired at 5.34x, against a measured "
                     "cross-system background of X'."),
        "_generated": _stamp(),
        "_configuration": configuration_declaration(),
        "preregistration": PREREG,
        "inherited_verbatim": {
            "_what": ("these are NOT restated here — they are read out of the modules that own them at "
                      "generation time, so this plan cannot drift from the code it registers."),
            "hard_clash_A": S.HARD_CLASH_A,
            "_hard_clash_source": "selectivity_mechanism_options.HARD_CLASH_A "
                                  "(= nr4a3-orientation-basins.json parameters.hard_clash_A)",
            "grid_A": SDR.GRID_A,
            "absolute_sanity_floor_A3": SDR.MIN_LOBE_VOLUME_A3,
            "pocket5_lining": list(S.POCKET5),
            "_pocket5_source": "selectivity_mechanism_options.POCKET5 (= `C5`, the prespecified site)",
            "identity_band": CDN.PREREG["pair_formation"]["identity_band"],
            "alignment_coverage_min": CDN.PREREG["pair_formation"]["alignment_coverage_min"],
            "max_per_protein": CDN.PREREG["pair_formation"]["max_per_protein"],
            "_selection_source": "categorical_decoy_null.PREREG.pair_formation (`C24`/`C16`)",
            "gradeability_min_conditioning_events":
                PREREG["gradeability"]["min_conditioning_events"],
        },
        "⛔_what_is_still_unmeasured_at_plan_time": (
            "everything. No model has been fetched, no pair selected, no clash computed. The pair and trio "
            "lists are written by `pairs`, which is also answer-blind, and the statistics by `run`."),
    }
    with open(PLAN_JSON, "w") as fh:
        json.dump(plan, fh, indent=1, ensure_ascii=False)
    print("[steric-decoy-null] pre-registration written: %s" % os.path.relpath(PLAN_JSON, REPO))
    return plan


def mode_fetch(_args):
    CDN.set_scope("lbd")
    uni = CDN.universe()
    accs = [u["accession"] for u in uni] + [CDN.NR4A3_ACC, CDN.NR4A1_ACC, CDN.NR4A2_ACC]
    seen, got, failed = set(), [], []
    for acc in accs:
        if acc in seen:
            continue
        seen.add(acc)
        try:
            got.append(CDN.fetch_af(acc))
        except Exception as ex:                                        # noqa: BLE001
            failed.append({"accession": acc, "reason": f"{type(ex).__name__}: {ex}"})
    print("[steric-decoy-null] fetched %d, failed %d" % (len(got), len(failed)))
    for f in failed:
        print("   FAILED %s: %s" % (f["accession"], f["reason"]))
    return {"fetched": len(got), "failed": failed}


def _trim_universe():
    """Trim every fetched model to `C24`'s LBD window. Returns (trimmed, refusals, seqs)."""
    CDN.set_scope("lbd")
    ref_seq = CDN.lbd_reference()["seq"]
    uni = CDN.universe()
    trimmed, refused = {}, []
    for u in uni:
        acc = u["accession"]
        if not os.path.exists(CDN.af_path(acc)):
            refused.append({"accession": acc, "gene": u["gene"], "reason": "no AlphaFold model fetched"})
            continue
        try:
            meta = CDN.trim_one(acc, CDN.MIN_PLDDT, CDN.MIN_DOMAIN_LEN, ref_seq=ref_seq)
            meta.update(gene=u["gene"], in_nr4a_family=u["in_nr4a_family"])
            trimmed[acc] = meta
        except Exception as ex:                                        # noqa: BLE001
            refused.append({"accession": acc, "gene": u["gene"], "reason": f"{type(ex).__name__}: {ex}"})
    seqs = {acc: B.load_paralogue(CDN.trimmed_path(acc))["seq"] for acc in trimmed}
    return trimmed, refused, seqs


def _identities(seqs, accs):
    out = {}
    for i in range(len(accs)):
        for j in range(i + 1, len(accs)):
            a, b = accs[i], accs[j]
            idn, cov = CDN.alignment_identity(seqs[a], seqs[b], ATLAS.nw_align(seqs[a], seqs[b]))
            out[(a, b)] = {"identity": round(idn, 4), "coverage": round(cov, 4)}
    return out


def select_trios(accs, ident, ref_mean, band, coverage_min, max_trios, max_per_protein):
    """THE PRE-REGISTERED TRIO SELECTION. PURE, deterministic and answer-blind.

    A trio qualifies when all THREE of its pairwise identities sit inside the band and clear the coverage
    floor. Ranked by |mean pairwise identity - the NR4A trio's own mean| ASCENDING, then greedy under
    `max_per_protein`, exactly the shape `select_pairs` uses for pairs.
    """
    lo, hi = band
    accs = sorted(accs)
    cand = []
    for i in range(len(accs)):
        for j in range(i + 1, len(accs)):
            for k in range(j + 1, len(accs)):
                t = (accs[i], accs[j], accs[k])
                pairs = [ident.get((t[0], t[1])), ident.get((t[0], t[2])), ident.get((t[1], t[2]))]
                if any(p is None for p in pairs):
                    continue
                if any(not (lo <= p["identity"] <= hi) for p in pairs):
                    continue
                if any(p["coverage"] < coverage_min for p in pairs):
                    continue
                mean_id = sum(p["identity"] for p in pairs) / 3.0
                cand.append({"members": list(t), "mean_identity": round(mean_id, 4),
                             "pairwise_identity": [p["identity"] for p in pairs],
                             "rank_key": round(abs(mean_id - ref_mean), 5)})
    cand.sort(key=lambda c: (c["rank_key"], c["members"]))
    used, selected = {}, []
    for c in cand:
        if len(selected) >= max_trios:
            break
        if any(used.get(m, 0) >= max_per_protein for m in c["members"]):
            continue
        for m in c["members"]:
            used[m] = used.get(m, 0) + 1
        selected.append(c)
    return selected, len(cand)


def mode_pairs(_args):
    """Trim, all-vs-all identity, and the answer-blind pair/trio selection. Still no statistic."""
    trimmed, refused, seqs = _trim_universe()
    print("  [sdn] trimmed %d, refused %d" % (len(trimmed), len(refused)))

    fam = {CDN.NR4A1_ACC: "NR4A1", CDN.NR4A2_ACC: "NR4A2", CDN.NR4A3_ACC: "NR4A3"}
    have_fam = [a for a in fam if a in seqs]
    ref_pairs = {}
    for other in (CDN.NR4A1_ACC, CDN.NR4A2_ACC):
        if CDN.NR4A3_ACC in seqs and other in seqs:
            i, c = CDN.alignment_identity(seqs[CDN.NR4A3_ACC], seqs[other],
                                          ATLAS.nw_align(seqs[CDN.NR4A3_ACC], seqs[other]))
            ref_pairs[fam[other]] = {"identity": round(i, 4), "coverage": round(c, 4)}
    ref_identity = (sum(v["identity"] for v in ref_pairs.values()) / len(ref_pairs)) if ref_pairs else 0.6

    # the NR4A trio's own mean pairwise identity — the trio ranking's reference, measured not typed
    nr4a_ident = _identities(seqs, sorted(have_fam)) if len(have_fam) == 3 else {}
    ref_trio_mean = (sum(v["identity"] for v in nr4a_ident.values()) / len(nr4a_ident)
                     if nr4a_ident else ref_identity)

    cand = sorted(a for a in trimmed if not trimmed[a]["in_nr4a_family"])
    ident = _identities(seqs, cand)
    entries = [{"a": a, "b": b, "gene_a": trimmed[a]["gene"], "gene_b": trimmed[b]["gene"],
                **v} for (a, b), v in sorted(ident.items())]

    selected_pairs, rejected = CDN.select_pairs(
        entries, ref_identity, CDN.PREREG["pair_formation"]["identity_band"],
        CDN.PREREG["pair_formation"]["alignment_coverage_min"],
        PREREG["selection_rule"]["max_pairs"], CDN.PREREG["pair_formation"]["max_per_protein"])

    selected_trios, n_cand_trios = select_trios(
        cand, ident, ref_trio_mean, CDN.PREREG["pair_formation"]["identity_band"],
        CDN.PREREG["pair_formation"]["alignment_coverage_min"],
        PREREG["selection_rule"]["max_trios"], CDN.PREREG["pair_formation"]["max_per_protein"])
    for t in selected_trios:
        t["genes"] = [trimmed[m]["gene"] for m in t["members"]]

    plan = json.load(open(PLAN_JSON)) if os.path.exists(PLAN_JSON) else mode_plan(None)
    plan.update({
        "_generated": _stamp(),
        "nr4a3_reference_identities": ref_pairs,
        "nr4a3_reference_identity_used_for_pair_ranking": round(ref_identity, 4),
        "nr4a_trio_mean_pairwise_identity_used_for_trio_ranking": round(ref_trio_mean, 4),
        "trimmed": trimmed,
        "trim_refusals": refused,
        "n_candidate_pairs": len(entries),
        "n_rejected_pairs": len(rejected),
        "rejected_pairs_sample": rejected[:30],
        "selected_pairs": selected_pairs,
        "n_candidate_trios": n_cand_trios,
        "selected_trios": selected_trios,
        "window_size_spread": CDN.window_spread(trimmed),
        "⛔_still_no_statistic": ("selection above is a function of SEQUENCE IDENTITY and STRUCTURE "
                                 "AVAILABILITY only. No clash, lobe or rate has been computed."),
    })
    with open(PLAN_JSON, "w") as fh:
        json.dump(plan, fh, indent=1, ensure_ascii=False)
    print("  [sdn] %d pairs, %d trios (of %d candidate trios); ref identity %.4f, trio mean %.4f"
          % (len(selected_pairs), len(selected_trios), n_cand_trios, ref_identity, ref_trio_mean))
    return plan


def _decoy_model(acc):
    return B.load_paralogue(CDN.trimmed_path(acc))


def mode_run(_args):
    """The two backgrounds, the index arms, and the percentiles."""
    CDN.set_scope("lbd")
    plan = json.load(open(PLAN_JSON))
    trimmed = plan["trimmed"]
    ligands = ligand_set()
    ref, _raw, fit_committed = committed_models()
    seqs_cache = json.load(open(os.path.join(REPO, "research/modalities/nr4a-sequences-cache.json")))
    positions_nr4a3 = pocket5_positions(ref)

    check, index_committed, _ = selfcheck(verbose=True)

    # ── index arm, MATCHED partner source (AlphaFold NR4A1/NR4A2) ────────────────────────────────────────
    index_af = None
    if CDN.NR4A1_ACC in trimmed and CDN.NR4A2_ACC in trimmed:
        pm, sq = {}, {"NR4A3": ref["seq"]}
        for role, acc in zip(ROLES, (CDN.NR4A1_ACC, CDN.NR4A2_ACC)):
            m = _decoy_model(acc)
            pm[role] = B.superpose_paralogue(m, ref)
            sq[role] = m["seq"]
        index_af = arm_result(
            "index_alphafold_partners", "index", ref, pm, positions_nr4a3, sq,
            ("NR4A3",) + ROLES, ligands, role_map={ROLES[0]: CDN.NR4A1_ACC, ROLES[1]: CDN.NR4A2_ACC},
            extra={"_what": ("the MATCHED index row: NR4A1 and NR4A2 as AlphaFold models trimmed by the "
                             "same rule as every decoy, on the same committed NR4A3 target and poses. "
                             "This is the row the percentile is quoted for.")})

    # ── background A: partner swap ───────────────────────────────────────────────────────────────────────
    swap_rows, refusals = [], []
    for p in plan["selected_pairs"]:
        a, b = p["a"], p["b"]
        try:
            pm, sq = {}, {"NR4A3": ref["seq"]}
            for role, acc in zip(ROLES, (a, b)):
                m = _decoy_model(acc)
                pm[role] = B.superpose_paralogue(m, ref)
                sq[role] = m["seq"]
            row = arm_result("%s|%s" % (p["gene_a"], p["gene_b"]), "decoy_partner_swap",
                             ref, pm, positions_nr4a3, sq, ("NR4A3",) + ROLES, ligands,
                             role_map={ROLES[0]: a, ROLES[1]: b},
                             extra={"pair_identity": p["identity"], "genes": [p["gene_a"], p["gene_b"]],
                                    "accessions": [a, b]})
            swap_rows.append(row)
            print("  [sdn] swap %-18s sig %-6s null %-6s unb %-6s poses %d"
                  % (row["arm"], row["signal_rate"], row["null_rate"],
                     row["unique_not_bulkier_rate"], row["n_poses_used"]), flush=True)
        except Exception as ex:                                        # noqa: BLE001
            refusals.append({"background": "partner_swap", "pair": [a, b],
                             "reason": f"{type(ex).__name__}: {ex}"})

    # ── background B: full trio ──────────────────────────────────────────────────────────────────────────
    trio_rows = []
    for t in plan["selected_trios"]:
        members, genes = t["members"], t["genes"]
        for ti in range(3):
            tacc = members[ti]
            pacc = [members[k] for k in range(3) if k != ti]
            try:
                tm = _decoy_model(tacc)
                fitT = B.superpose_paralogue(tm, ref)          # target into the NR4A3 pose frame
                pm, sq = {}, {"TARGET": tm["seq"]}
                for role, acc in zip(ROLES, pacc):
                    m = _decoy_model(acc)
                    pm[role] = B.superpose_paralogue(m, fitT)  # partners fitted to THEIR OWN target
                    sq[role] = m["seq"]
                pos = {}
                for u, rid3 in positions_nr4a3.items():
                    pos[u] = fitT["corr_from_ref"].get(rid3)
                row = arm_result("%s<-%s+%s" % (genes[ti], genes[(ti + 1) % 3], genes[(ti + 2) % 3]),
                                 "decoy_full_trio", fitT, pm, pos, sq, ("TARGET",) + ROLES, ligands,
                                 role_map={"TARGET": tacc, ROLES[0]: pacc[0], ROLES[1]: pacc[1]},
                                 extra={"trio_mean_identity": t["mean_identity"],
                                        "genes": genes, "target_gene": genes[ti],
                                        "n_pocket5_positions_mapped":
                                            sum(1 for v in pos.values() if v is not None),
                                        "target_superposition_onto_NR4A3": {
                                            k: fitT["superposition"].get(k) for k in
                                            ("n_ca_pairs", "n_core", "core_fraction", "core_rmsd_A")}})
                trio_rows.append(row)
                print("  [sdn] trio %-22s sig %-6s null %-6s unb %-6s poses %d"
                      % (row["arm"], row["signal_rate"], row["null_rate"],
                         row["unique_not_bulkier_rate"], row["n_poses_used"]), flush=True)
            except Exception as ex:                                    # noqa: BLE001
                refusals.append({"background": "full_trio", "target": tacc, "partners": pacc,
                                 "reason": f"{type(ex).__name__}: {ex}"})

    art = assemble(plan, check, index_committed, index_af, swap_rows, trio_rows, refusals)
    with open(OUT_JSON, "w") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
    with open(OUT_MD, "w") as fh:
        fh.write(to_markdown(art))
    print("[steric-decoy-null] %s" % art["headline"])
    return art


# =============================================================================================================
# REDUCTION — the backgrounds, the percentiles, the verdict
# =============================================================================================================
def background_block(rows, index_row, key, direction="high", clustering=None, min_graded=None):
    """One background column, its distribution, and the index arm's position in it.

    `direction`: 'high' when a LARGER value is the favourable one (contrast a), 'low' when a SMALLER value
    is (contrast b, where NR4A3 returns 0.000).
    """
    graded = [r for r in rows if r.get(key) is not None]
    vals = [r[key] for r in graded]
    summ = CDN.summarise_background([{key: v} for v in vals], key) if vals else None
    idx = index_row.get(key) if index_row else None
    out = {
        "n_graded": len(vals),
        "n_distinct_proteins": len({a for r in graded for a in (r.get("accessions") or r.get("genes") or [])}),
        "distribution": summ,
        "modal_value": mode_of(vals),
        "index_value": idx,
        "index_arm": (index_row or {}).get("arm"),
        "graded_rows": [{"arm": r["arm"], key: r[key], "n_poses_used": r["n_poses_used"],
                         "n_positions_by_class": r["n_positions_by_class"]} for r in graded],
    }
    if vals and idx is not None:
        out["percentile_of_the_background_BELOW_the_index"] = _r(percentile_above(idx, vals), 4)
        out["frac_of_the_background_at_or_above_the_index"] = _r(
            sum(1 for v in vals if v >= idx) / len(vals), 4)
        out["frac_of_the_background_at_or_below_the_index"] = _r(CDN.percentile_of(idx, vals), 4)
        out["percentile_resolution"] = _r(1.0 / len(vals), 4)
        m = out["modal_value"]
        if m and abs(m["value"] - round(float(idx), 3)) < 1e-9:
            out["⚠_index_equals_the_background_mode"] = (
                "⛔ THE INDEX ARM'S VALUE IS EXACTLY THE BACKGROUND'S MODAL VALUE (%s, %d of %d rows). Its "
                "percentile IS that modal frequency — ONE measurement, not two. Do not quote them as "
                "independent evidence." % (m["value"], m["count"], m["n"]))
        else:
            out["⚠_index_equals_the_background_mode"] = None
        favourable = (out["percentile_of_the_background_BELOW_the_index"] if direction == "high"
                      else _r(sum(1 for v in vals if v > idx) / len(vals), 4))
        out["favourable_direction"] = direction
        out["percentile_in_the_favourable_direction"] = favourable
        out["verdict"] = grade(len(vals), favourable,
                               (summ or {}).get("frac_exactly_zero"), min_graded=min_graded)
    else:
        out["verdict"] = "UNGRADEABLE_no_index_value" if vals else "UNGRADEABLE_empty_background"
    if clustering:
        out["⚠_clustering"] = clustering
    return out


CLUSTER_SWAP = ("pairs share proteins under `max_per_protein = 2`, so the rows are not fully independent "
                "and the effective n is below `n_graded`. `n_distinct_proteins` is reported beside it.")
CLUSTER_TRIO = ("the three arms of one trio share all three proteins, so within a trio the rows are STRONGLY "
                "dependent — `n_graded / 3` is closer to the number of independent systems than `n_graded` "
                "is. `n_distinct_proteins` is reported beside it.")


def unfiltered_row(r):
    """The same arm read off its UNFILTERED class counts — the declared sensitivity.

    ⚠ ITS BIAS DIRECTION IS KNOWN AND IS NAMED WHEREVER IT IS QUOTED: on an arm whose target is not the
    protein the poses were docked into, the target-clash term suppresses firing in EVERY class, so these
    rates are biased DOWNWARD relative to the index arm. A background that is HIGH despite that bias is
    evidence; a background that is LOW under it is not.
    """
    cls = r["by_position_class_UNFILTERED_sensitivity"]
    sig, nul, unb = (cls["unique_and_both_bulkier"], cls["conserved_or_shared"],
                     cls["unique_not_bulkier"])
    out = dict(r)
    out["signal_minus_null"] = (_r(sig["rate"] - nul["rate"], 3)
                                if sig["rate"] is not None and nul["rate"] is not None else None)
    out["enrichment_signal_over_null"] = (_r(sig["rate"] / nul["rate"], 3)
                                          if sig["rate"] is not None and nul["rate"] else None)
    out["unique_not_bulkier_rate"] = unb["rate"]
    out["graded_contrast_a"] = bool(sig["graded"] and nul["graded"])
    out["graded_contrast_b"] = bool(unb["graded"])
    return out


def assemble(plan, check, index_committed, index_af, swap_rows, trio_rows, refusals):
    idx = index_af or index_committed
    graded_a_swap = [r for r in swap_rows if r["graded_contrast_a"]]
    graded_b_swap = [r for r in swap_rows if r["graded_contrast_b"]]
    graded_a_trio = [r for r in trio_rows if r["graded_contrast_a"]]
    graded_b_trio = [r for r in trio_rows if r["graded_contrast_b"]]
    graded_v_swap = [r for r in swap_rows if (r.get("volume_axis") or {}).get("graded")]
    graded_v_trio = [r for r in trio_rows if (r.get("volume_axis") or {}).get("graded")]

    def vol_rows(rows):
        return [dict(r, **{"_vol_frac": r["volume_axis"]["frac_signal_positions_clearing_own_bar"],
                           "_vol_ratio": r["volume_axis"]["signal_over_null_volume"]}) for r in rows]

    idx_v = dict(idx, **{
        "_vol_frac": (idx.get("volume_axis") or {}).get("frac_signal_positions_clearing_own_bar"),
        "_vol_ratio": (idx.get("volume_axis") or {}).get("signal_over_null_volume")}) if idx else None

    backgrounds = {
        "partner_swap": {
            "_what": PREREG["two_backgrounds_never_pooled"]["partner_swap"]["construction"],
            "role": "PRIMARY",
            "n_rows_attempted": len(swap_rows),
            "n_graded_contrast_a": len(graded_a_swap),
            "n_graded_contrast_b": len(graded_b_swap),
            "contrast_a_signal_minus_null": background_block(
                graded_a_swap, idx, "signal_minus_null", "high", CLUSTER_SWAP),
            "contrast_a_enrichment_ratio": background_block(
                [r for r in graded_a_swap if r["enrichment_signal_over_null"] is not None],
                idx, "enrichment_signal_over_null", "high", CLUSTER_SWAP),
            "n_enrichment_undefined": sum(1 for r in graded_a_swap
                                          if r["enrichment_signal_over_null"] is None),
            "contrast_b_unique_not_bulkier_rate": background_block(
                graded_b_swap, idx, "unique_not_bulkier_rate", "low", CLUSTER_SWAP),
            "volume_axis_frac_signal_clearing_own_bar": background_block(
                vol_rows(graded_v_swap), idx_v, "_vol_frac", "high", CLUSTER_SWAP),
        },
        "full_trio": {
            "_what": PREREG["two_backgrounds_never_pooled"]["full_trio"]["construction"],
            "role": "SECONDARY",
            "⚠_asymmetric_reading":
                PREREG["two_backgrounds_never_pooled"]["full_trio"][
                    "⚠_the_asymmetry_it_carries_and_the_reading_that_follows"],
            "n_rows_attempted": len(trio_rows),
            "n_graded_contrast_a": len(graded_a_trio),
            "n_graded_contrast_b": len(graded_b_trio),
            "contrast_a_signal_minus_null": background_block(
                graded_a_trio, idx, "signal_minus_null", "high", CLUSTER_TRIO),
            "contrast_a_enrichment_ratio": background_block(
                [r for r in graded_a_trio if r["enrichment_signal_over_null"] is not None],
                idx, "enrichment_signal_over_null", "high", CLUSTER_TRIO),
            "n_enrichment_undefined": sum(1 for r in graded_a_trio
                                          if r["enrichment_signal_over_null"] is None),
            "contrast_b_unique_not_bulkier_rate": background_block(
                graded_b_trio, idx, "unique_not_bulkier_rate", "low", CLUSTER_TRIO),
            "volume_axis_frac_signal_clearing_own_bar": background_block(
                vol_rows(graded_v_trio), idx_v, "_vol_frac", "high", CLUSTER_TRIO),
            "⚠_UNFILTERED_sensitivity_because_the_filtered_contrast_was_predicted_ungradeable": {
                "_what": ("the same arms read off their UNFILTERED class counts, i.e. with the target-clash "
                          "term left in `score_pose`'s predicate exactly as it stands. Reported because "
                          "the pre-registration PREDICTED, with the smoke as evidence, that the filtered "
                          "clash contrast would be ungradeable here."),
                "⚠_bias_direction": ("biased DOWNWARD on decoys — the decoy target's own side chains "
                                     "suppress firing in every class. A HIGH background under this bias is "
                                     "evidence against distinctiveness; a LOW one is not evidence for it."),
                "⛔_the_index_is_read_UNFILTERED_here_too": (
                    "a filtered index against an unfiltered background would not be like-for-like, and the "
                    "difference is not cosmetic — the index arm's own value moves when its one "
                    "target-clashing pose is put back."),
                "contrast_a_signal_minus_null": background_block(
                    [u for u in (unfiltered_row(r) for r in trio_rows) if u["graded_contrast_a"]],
                    unfiltered_row(idx) if idx else None, "signal_minus_null", "high", CLUSTER_TRIO),
                "contrast_b_unique_not_bulkier_rate": background_block(
                    [u for u in (unfiltered_row(r) for r in trio_rows) if u["graded_contrast_b"]],
                    unfiltered_row(idx) if idx else None, "unique_not_bulkier_rate", "low", CLUSTER_TRIO),
            },
            "pose_attrition": {
                "_what": ("how many of the 13 poses survived each decoy target's own clash filter. This is "
                          "the quantity that decides whether a LOW `full_trio` background means 'no "
                          "contrast' or 'not enough poses to see one'."),
                "n_poses_used": sorted(r["n_poses_used"] for r in trio_rows),
                "n_arms_with_zero_poses": sum(1 for r in trio_rows if r["n_poses_used"] == 0),
            },
        },
    }

    prim_a = backgrounds["partner_swap"]["contrast_a_signal_minus_null"]
    prim_b = backgrounds["partner_swap"]["contrast_b_unique_not_bulkier_rate"]
    verdict_a, verdict_b = prim_a.get("verdict"), prim_b.get("verdict")
    headline = ("contrast (a) %s · contrast (b) %s — primary background `partner_swap`, n = %s / %s"
                % (verdict_a, verdict_b, prim_a.get("n_graded"), prim_b.get("n_graded")))

    art = {
        "_title": ("`C25` — CROSS-SYSTEM DECOY NULL FOR THE STERIC-EXCLUSION AXIS (`S3`). Two "
                   "independently constructed backgrounds, never pooled, both computed by the code that "
                   "produced the committed measurement."),
        "_status": ("INSTRUMENT CALIBRATION. $0 CPU/CI. Nothing here is a claim about binding, affinity, "
                    "reactivity, degradation, efficacy, safety or clinical readiness."),
        "_reading": ("This calibrates the STERIC SCREEN, not NR4A3. A contrast is only evidence about "
                     "NR4A3 to the extent that an arbitrary close paralogue pair does NOT reproduce it."),
        "_generated": _stamp(),
        "_configuration": configuration_declaration(),
        "headline": headline,
        "preregistration": PREREG,
        "⛔_the_ceiling_that_travels_with_every_number_here": {
            "_source": "M4 / selectivity-mechanism-options.md, quoted not re-derived",
            "median_centroid_shift_A": committed_m4_shift(),
            "✅_what_a_high_contrast_licenses": "this POSE is denied in the partner's modelled conformer",
            "⛔_what_it_is_not": (
                "NOT that the paralogue fails to bind the molecule — it binds it somewhere else (`M4`, "
                "median ~5.3 A relocation). NOT an affinity, a selectivity ratio, a degradation statement "
                "or any energy: none is computed here. NOT independent of `R5` — the whole axis is "
                "conditional on the cryptic pocket being the right site, and `V3` returned INCONCLUSIVE on "
                "site selection."),
            "⚠_rigid_transfer": (
                "every partner side chain is held in its own conformer and could rotate away; every lobe "
                "and every clash is 'denied in this conformer', never 'denied'"),
            "⚠_target_absence_of_clash_is_by_construction": (
                "the poses were docked INTO NR4A3, so the target's lack of clash carries no information in "
                "ANY arm — which is why only the between-class contrast is gradeable, and why the per-arm "
                "pose filter exists at all"),
        },
        "harness_known_answer_check": check,
        "index_arms": {
            "index_committed": index_committed,
            "index_alphafold_partners": index_af,
            "⚠_which_one_the_percentile_uses": (
                "`index_alphafold_partners` — the MATCHED row, whose partners come from the same source "
                "and the same trim as every decoy. `index_committed` is the reference row and is what "
                "reproduces the committed `M3` rates; quoting a percentile for it would compare a "
                "committed opened-model arm against an AlphaFold background, which is the mixed-source "
                "comparison `C24` refused."),
            "both_percentiles_are_reported": True,
        },
        "backgrounds": backgrounds,
        "index_percentile_under_the_committed_row_MIXED_SOURCE": {
            "_warning": ("reported for completeness ONLY. The committed row's partners are opened models "
                         "built by this program; the background's are AlphaFold models. A percentile "
                         "across that boundary is not like-for-like."),
            "contrast_a_signal_minus_null": _r(percentile_above(
                index_committed["signal_minus_null"],
                [r["signal_minus_null"] for r in graded_a_swap]), 4) if graded_a_swap else None,
            "contrast_b_unique_not_bulkier_rate": _r(
                sum(1 for r in graded_b_swap
                    if r["unique_not_bulkier_rate"] > index_committed["unique_not_bulkier_rate"])
                / len(graded_b_swap), 4) if graded_b_swap else None,
        },
        "decoy_rows": {"partner_swap": swap_rows, "full_trio": trio_rows},
        "refusals": refusals,
        "plan": {"selected_pairs": plan.get("selected_pairs"),
                 "selected_trios": plan.get("selected_trios"),
                 "window_size_spread": plan.get("window_size_spread"),
                 "nr4a3_reference_identities": plan.get("nr4a3_reference_identities"),
                 "trim_refusals": plan.get("trim_refusals")},
        "limits": LIMITS,
    }
    art["verdict"] = {
        "contrast_a_bulkier_in_both_vs_conserved_null": verdict_a,
        "contrast_b_unique_but_not_bulkier": verdict_b,
        "primary_background": "partner_swap",
        "secondary_background_contrast_a":
            backgrounds["full_trio"]["contrast_a_signal_minus_null"].get("verdict"),
        "secondary_background_contrast_b":
            backgrounds["full_trio"]["contrast_b_unique_not_bulkier_rate"].get("verdict"),
        "rule": PREREG["verdict_rule"],
        "★_plain_reading": plain_reading(prim_a, prim_b, backgrounds, idx),
    }
    art["map_edits_required"] = map_edits(art)
    return art


def committed_m4_shift():
    try:
        d = json.load(open(os.path.join(HERE, "steric-design-rule.json")))
        return d["⛔_control"]["median_centroid_shift_A"]
    except Exception:                                                  # noqa: BLE001
        return None


def plain_reading(prim_a, prim_b, backgrounds, idx):
    """The verdict in words a reader cannot mis-scan. Deliberately blunt in the unfavourable direction."""
    bits = []
    na, nb = prim_a.get("n_graded"), prim_b.get("n_graded")
    if not na:
        bits.append("⛔ CONTRAST (a) IS UNGRADEABLE: the primary background produced no row clearing the "
                    "pre-registered floor of %d conditioning events per class. That is a POWER failure, "
                    "not a result, and the floor was not moved to repair it."
                    % PREREG["gradeability"]["min_conditioning_events"])
    else:
        pa = prim_a.get("percentile_in_the_favourable_direction")
        dist = prim_a.get("distribution") or {}
        bits.append(
            "CONTRAST (a) — bulkier-in-both vs the conserved/shared null. NR4A3 (matched index row) "
            "signal_minus_null = %s. Background over %d graded arms: median %s, q75 %s, max %s. NR4A3 sits "
            "above %s of the background (resolution %s). VERDICT: %s."
            % (prim_a.get("index_value"), na, _r(dist.get("median"), 3), _r(dist.get("q75"), 3),
               _r(dist.get("max"), 3), pa, prim_a.get("percentile_resolution"), prim_a.get("verdict")))
        if prim_a.get("⚠_index_equals_the_background_mode"):
            bits.append(prim_a["⚠_index_equals_the_background_mode"])
    if not nb:
        bits.append("⛔ CONTRAST (b) IS UNGRADEABLE at the pre-registered floor.")
    else:
        dist = prim_b.get("distribution") or {}
        bits.append(
            "CONTRAST (b) — the unique-but-NOT-bulkier class, which fires at 0.000 on NR4A3. Background "
            "over %d graded arms: frac_exactly_zero = %s (Wilson 95%% %s), median %s. VERDICT: %s."
            % (nb, _r(dist.get("frac_exactly_zero"), 3), dist.get("frac_exactly_zero_wilson95"),
               _r(dist.get("median"), 3), prim_b.get("verdict")))
        if prim_b.get("⚠_index_equals_the_background_mode"):
            bits.append(prim_b["⚠_index_equals_the_background_mode"])
    ft = backgrounds["full_trio"]["contrast_a_signal_minus_null"]
    ftu = backgrounds["full_trio"][
        "⚠_UNFILTERED_sensitivity_because_the_filtered_contrast_was_predicted_ungradeable"][
        "contrast_a_signal_minus_null"]
    ftv = backgrounds["full_trio"]["volume_axis_frac_signal_clearing_own_bar"]
    bits.append(
        "SECONDARY (`full_trio`, target and both partners swapped): filtered clash contrast %d graded arms, "
        "verdict %s — and the pre-registration PREDICTED this from the smoke, because transporting a pose "
        "set docked into NR4A3 into another target's frame drops the poses (attrition: %s). The unfiltered "
        "sensitivity, biased DOWNWARD on decoys, graded %d arms at verdict %s. ⭑ The half that is immune "
        "to all of this is the POSE-FREE volume axis: %d graded arms, index %s, verdict %s."
        % (ft.get("n_graded") or 0, ft.get("verdict"),
           backgrounds["full_trio"]["pose_attrition"]["n_poses_used"],
           ftu.get("n_graded") or 0, ftu.get("verdict"),
           ftv.get("n_graded") or 0, ftv.get("index_value"), ftv.get("verdict")))
    bits.append(
        "⛔ AND THE CEILING IS UNCHANGED BY ANY OF THIS: the paralogue RELOCATES these molecules by a "
        "median ~5.3 A rather than refusing them (`M4`), so `S3` constrains a POSE and never 'the "
        "paralogue cannot bind this molecule'. The transfer is rigid, and the target's absence of clash is "
        "guaranteed by construction and carries no information in any arm.")
    return bits


LIMITS = [
    "⛔ This calibrates the SCREEN, not the protein. A distinctive contrast would say the steric predicate "
    "separates NR4A3 from an arbitrary close nuclear-receptor pair; it would still say nothing about "
    "binding, affinity, degradation, efficacy or safety, none of which is computed anywhere here.",
    "⚠ RIGID TRANSFER, every arm. Partner side chains are held in their own modelled conformer and could "
    "rotate away. Every rate and every lobe is 'denied in this conformer', never 'denied'.",
    "⚠ The target's absence of clash is guaranteed by construction (the poses were docked into NR4A3) and "
    "carries no information. Only the between-class contrast is gradeable — which is why `score_pose` "
    "refuses to emit a signal without its matched null, and why this file always reports both.",
    "⚠ The decoy arms are ALPHAFOLD models trimmed to `C24`'s reference-anchored LBD window; the index "
    "target is the committed metadynamics-OPENED NR4A3 conformer. The partner source is matched (the "
    "index row's partners are AlphaFold models too); the TARGET source is not matched in `full_trio`.",
    "⚠ A nuclear-receptor universe is not the proteome. Nothing here bounds the rate over the proteome, "
    "and no proteome-wide selectivity claim is made or implied.",
    "⚠ Clustering: pairs and trios share proteins under `max_per_protein = 2`, and the three arms of one "
    "trio share all three proteins. The effective n is below `n_graded` and every Wilson interval here is, "
    "if anything, optimistic.",
    "⚠ One superposition per partner, by iterative core refinement. Post-fit deviation is carried on every "
    "position so a reader can down-weight the worst ones, exactly as `M3` does.",
    "⛔ Conditional on `R5`. The whole steric axis assumes the cryptic pocket is the right site, and the "
    "pose known-answer test `V3` returned INCONCLUSIVE on site selection. A background cannot repair that.",
    "⛔ `C5`'s Pocket-5 lining set is mapped onto every decoy target by sequence alignment, so a decoy "
    "position is 'NR4A3's site, mapped', never 'this protein's own pocket'. That is the same convention "
    "the committed paralogue contrast uses and it has the same reading.",
    "⚠ 13 poses is a small pose set and it is the committed selectivity-matrix library, not the carried "
    "candidate. The per-arm filter can only shrink it.",
]


# =============================================================================================================
# Configuration declaration + roadmap edits
# =============================================================================================================
def configuration_declaration():
    """§3b's declaration rule, applied to this file's own numbers."""
    return {
        "_rule": ("roadmap §3b: a number whose value depends on a frozen definitional choice must NAME that "
                  "choice, inline, where the number is written. Declared here so every percentile in this "
                  "artifact carries its conditions."),
        "items": {
            CONFIG_ID: {
                "what_it_fixes": ("the STERIC decoy-null construction — which proteins may play the "
                                  "paralogue roles, how a decoy arm is built, how poses are carried and "
                                  "filtered, and the gradeability floor a background row must clear"),
                "value": ("two backgrounds never pooled (`partner_swap` PRIMARY, `full_trio` SECONDARY); "
                          "decoy roles drawn from the committed 47-receptor nuclear-receptor universe minus "
                          "the NR4A family; AlphaFold models trimmed by `C24`'s LBD window; pairs/trios "
                          "ranked answer-blind on identity; 20 conditioning events per class"),
                "frozen_by": ("this file's `PREREG`, emitted by `plan` before any model was fetched under "
                              "it and before any statistic under it existed"),
                "home": "research/modalities/steric_decoy_null.py -> PREREG; plan file "
                        "research/modalities/steric-decoy-null-plan.json",
                "what_moves_if_it_moves": ("every percentile this artifact quotes for `S3`'s 0.923 / 0.173 "
                                           "/ 0.000, and therefore whether the 5.34x contrast is reported "
                                           "as distinctive or as ordinary"),
                "status": "frozen",
            },
            "C24": "the LBD window trim and the pair-selection rule, INHERITED here rather than re-frozen",
            "C5": "the Pocket-5 lining set, mapped onto every arm's target",
            "C16": "the sibling decoy-null trim; cited, never used here",
        },
        "⛔_none_of_these_is_altered_by_this_run": (
            "they are cited, not edited. Changing any of them is trimcrae's decision, per §3b."),
    }


def last_register_row_anchor(text):
    """The `| **C<n>** |` row with the HIGHEST n in §3b.1, so a new row lands at the END of the register.

    ⛔ WHY THIS IS COMPUTED AND NOT TYPED. A sibling artifact (`C24`) carries its own unapplied register-row
    edit, so whether the last row is `C23` or `C24` depends on whether that routing has happened yet — and
    an anchor typed against one of those states inserts this row in the MIDDLE of the register in the other.
    Scanning for the maximum is correct in both, and stays correct when the next `C*` lands. PURE.
    """
    import re as _re
    best, anchor = None, None
    for m in _re.finditer(r"^\| \*\*C(\d+)\*\* \|", text or "", _re.M):
        n = int(m.group(1))
        if best is None or n > best:
            best, anchor = n, m.group(0)
    return anchor


def map_edits(art):
    """Roadmap edits this result requires — DESCRIBED, with anchors read out of the LIVE map."""
    text = ME.load_map()
    v = art["verdict"]
    prim_a = art["backgrounds"]["partner_swap"]["contrast_a_signal_minus_null"]
    prim_b = art["backgrounds"]["partner_swap"]["contrast_b_unique_not_bulkier_rate"]
    dist_b = (prim_b.get("distribution") or {})
    entries = []

    tag = ("⭑ **AND IT NOW HAS A CROSS-SYSTEM BACKGROUND (`C25`, 2026-08-03, $0):** arbitrary close "
           "nuclear-receptor pairs pushed through the identical `score_pose` path — contrast (a) "
           "**%s**, contrast (b) **%s**, `n` = %s / %s graded arms, `frac_exactly_zero` = %s on the "
           "unique-but-not-bulkier class. Numbers: [`steric-decoy-null.json`](../modalities/steric-decoy-null.json)."
           % (v["contrast_a_bulkier_in_both_vs_conserved_null"], v["contrast_b_unique_but_not_bulkier"],
              prim_a.get("n_graded"), prim_b.get("n_graded"), _r(dist_b.get("frac_exactly_zero"), 3)))

    entries.append(ME.edit(
        text, "§3b.1 configuration register — the new `C25` row",
        last_register_row_anchor(text) or "| **C23** |",
        "`C25` is a NEW frozen definitional choice and §3b's rule is that a number depending on one must "
        "name it. Every percentile this run quotes is conditional on it.",
        "research/modalities/steric-decoy-null.json",
        ME.append_after_line(
            "| **C25** | **the STERIC decoy-null construction** — which proteins may play the paralogue "
            "roles, how a decoy arm is built, how poses are carried and filtered | two backgrounds **never "
            "pooled** (`partner_swap` PRIMARY, `full_trio` SECONDARY); decoy roles = the committed "
            "47-receptor nuclear-receptor universe **minus the NR4A family**; AlphaFold models trimmed by "
            "`C24`'s LBD window; pairs/trios ranked **answer-blind** on identity; **20** conditioning "
            "events per class (inherited from `C24`, not re-chosen) | this run's `PREREG`, emitted by "
            "`plan` **before any model was fetched under it and before any statistic under it existed** | "
            "[`steric_decoy_null.PREREG`](../modalities/steric_decoy_null.py); plan in "
            "[`steric-decoy-null-plan.json`](../modalities/steric-decoy-null-plan.json) | ⛔ **whether "
            "`S3`'s 5.34× is reported as DISTINCTIVE or as ORDINARY.** Contrast (a) **%s**, contrast (b) "
            "**%s** | ✅ frozen |"
            % (v["contrast_a_bulkier_in_both_vs_conserved_null"], v["contrast_b_unique_but_not_bulkier"])),
        kind="insert"))

    entries.append(ME.edit(
        text, "§3b.1 register — the item count (DERIVED)",
        "⚠ **This list is a floor, not a census.**",
        "The register states how many items it holds and `C25` changes it. ⛔ A COUNT IS DERIVED — "
        "regenerate it from the table's own rows, never type it. Left unapplied on purpose.",
        "research/modalities/steric-decoy-null.json",
        lambda cur: cur, kind="derived-count"))
    entries[-1].pop("proposed_text", None)
    entries[-1]["proposed_text"] = None
    entries[-1]["flag"] = ("DERIVED COUNT — do not hand-edit. Recount the `| **C\\d+** |` rows of §3b.1 "
                           "after this row and `C24`'s land.")

    entries.append(ME.edit(
        text, "§10.1 row 24 — the steric-exclusion design rule",
        "| **24** | **The steric-exclusion DESIGN RULE**",
        "Row 24 is the design rule's home and it currently quotes the 0.923-vs-0.173 contrast with a "
        "WITHIN-SYSTEM null only. The cross-system background is what decides how that contrast may be read.",
        "research/modalities/steric-decoy-null.json",
        ME.append_to_line(" " + tag)))

    entries.append(ME.edit(
        text, "§8 — the steric bullet's 0.923/0.173 statement",
        "matters: paralogue-only clash **0.923** at those three positions against **0.173** at conserved/shared",
        "This is the sentence a reader takes the headline from. A contrast with a measured cross-system "
        "background reads differently from one without.",
        "research/modalities/steric-decoy-null.json",
        ME.append_to_line(" " + tag)))

    entries.append(ME.edit(
        text, "§10.1a option queue — the `Q1` steric row",
        "| **Q1** | **Score the committed construct set through the steric design rule**",
        "`Q1` is the steric axis's queue row and the calibration it lacked is now measured.",
        "research/modalities/steric-decoy-null.json",
        ME.append_to_line(" " + tag)))

    checked, summary = ME.verify(entries, text) if text else (entries, {})
    return {
        "_what": ("Roadmap edits this result requires. DESCRIBED, NOT APPLIED — every `current_text` is "
                  "READ out of the live map by `map_edits.locate`, so it is a byte-exact substring of the "
                  "map as it stood at generation time. Route with "
                  "`python3 research/manuscripts/route_map_edits.py <artifact> --apply`."),
        "configuration_id": CONFIG_ID,
        "verdict_contrast_a": v["contrast_a_bulkier_in_both_vs_conserved_null"],
        "verdict_contrast_b": v["contrast_b_unique_but_not_bulkier"],
        "⛔_not_filed_in_section_6": ("A null that fails to reject closes nothing, and a null that DOES "
                                     "reject does not close the axis either — it calibrates it. Nothing "
                                     "here is proposed for §6 in either direction."),
        "entries": entries,
        "verification": summary,
    }


# =============================================================================================================
# Markdown
# =============================================================================================================
def to_markdown(d):
    L = []
    A = L.append
    A("# `C25` — the cross-system decoy null for the steric-exclusion axis (`S3`)\n")
    A("**%s**\n" % d["headline"])
    A("%s\n" % d["_status"])
    A("> %s\n" % d["_reading"])
    A("## The plain reading\n")
    for b in d["verdict"]["★_plain_reading"]:
        A("- %s" % b)
    A("")
    A("## The known-answer check\n")
    c = d["harness_known_answer_check"]
    A("| check | committed | recomputed here | agrees |")
    A("|---|---|---|---|")
    A("| `M3` class rates | `%s` | `%s` | **%s** |"
      % (c["committed_M3_rates"], c["recomputed_UNFILTERED"], c["reproduces_committed_M3"]))
    A("| denied-lobe volumes | `%s` | `%s` | **%s** |"
      % (c["committed_null_volume_ceiling_A3"], c["recomputed_null_volume_ceiling_A3"],
         c["reproduces_committed_lobes"]))
    A("")
    A("⛔ %s\n" % c["_if_false"])
    for name in ("partner_swap", "full_trio"):
        b = d["backgrounds"][name]
        A("## Background `%s` (%s)\n" % (name, b["role"]))
        A("%s\n" % b["_what"])
        for key, label in (("contrast_a_signal_minus_null", "contrast (a) · signal − null"),
                           ("contrast_a_enrichment_ratio", "contrast (a) · enrichment ratio"),
                           ("contrast_b_unique_not_bulkier_rate", "contrast (b) · unique-not-bulkier rate"),
                           ("volume_axis_frac_signal_clearing_own_bar",
                            "volume axis · fraction of signal positions clearing the arm's own bar")):
            blk = b.get(key) or {}
            dist = blk.get("distribution") or {}
            A("**%s** — index `%s`, n = %s, resolution %s, percentile (favourable direction) **%s**, "
              "verdict **%s**. Background: min %s / median %s / max %s, `frac_exactly_zero` %s."
              % (label, blk.get("index_value"), blk.get("n_graded"), blk.get("percentile_resolution"),
                 blk.get("percentile_in_the_favourable_direction"), blk.get("verdict"),
                 _r(dist.get("min"), 3), _r(dist.get("median"), 3), _r(dist.get("max"), 3),
                 _r(dist.get("frac_exactly_zero"), 3)))
            if blk.get("⚠_index_equals_the_background_mode"):
                A("  - %s" % blk["⚠_index_equals_the_background_mode"])
            A("")
    A("## ⛔ Limits\n")
    for x in d["limits"]:
        A("- %s" % x)
    A("")
    A("*Generated %s by `steric_decoy_null.py`.*" % d["_generated"]["et"])
    return "\n".join(L) + "\n"


def mode_remap(_args):
    """Regenerate ONLY the committed artifact's `map_edits_required`, against the map as it stands NOW.

    ★ WHY THIS EXISTS, and it is the same argument the `C02` lane's `decoy_reduce_only` job makes: an anchor
    is a property of the DOCUMENT, not of the measurement, so a document that moved underneath a committed
    artifact must not cost a recompute. Nothing measured is touched — the rows, rates, percentiles and
    verdict are read back from the artifact and written out unchanged; only the anchors and their
    `current_text` are rebuilt.
    """
    art = json.load(open(OUT_JSON))
    art["map_edits_required"] = map_edits(art)
    art["map_edits_required"]["_regenerated"] = _stamp()
    with open(OUT_JSON, "w") as fh:
        json.dump(art, fh, indent=1, ensure_ascii=False)
    v = art["map_edits_required"]["verification"]
    print("[steric-decoy-null] map edits re-anchored: %s" % v)
    return art


def main(argv=None):
    ap = argparse.ArgumentParser(description="C25 — cross-system decoy null for the steric axis")
    ap.add_argument("mode", choices=["plan", "smoke", "fetch", "pairs", "selfcheck", "run", "remap"])
    args = ap.parse_args(argv)
    if args.mode == "smoke":
        return mode_smoke(args)
    if args.mode == "plan":
        mode_plan(args)
    elif args.mode == "fetch":
        mode_fetch(args)
    elif args.mode == "pairs":
        mode_pairs(args)
    elif args.mode == "remap":
        mode_remap(args)
    elif args.mode == "selfcheck":
        out, _row, _ = selfcheck()
        print(json.dumps({k: v for k, v in out.items() if not k.startswith("_")},
                         indent=1, ensure_ascii=False)[:4000])
        return 0 if out["PASS"] else 2
    else:
        mode_run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
