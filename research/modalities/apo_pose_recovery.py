#!/usr/bin/env python3
"""KNOWN-ANSWER TEST: can this program's docking pipeline recover a pose that is already known? ($0 CPU)

★★ WHY. Everything downstream of `denovo_401` — the ternary, the selectivity argument, the ABFE work —
is anchored to a PREDICTED pose in the NR4A3 ligand-binding domain, produced by docking into a
metadynamics-opened AF2 frame and re-docking into the cavity-bearing conformers of the apo NMR ensemble
8XTT. Nobody has ever asked whether that pipeline can recover a pose that is KNOWN. Until someone does,
every claim resting on the pose rests on the assumption that it can.

This is the same discipline that `selcal_interface_signature.py` applied to the paralogue-selectivity
descriptor: do not trust a readout until it reproduces an answer published before this program existed.

★ THE REGIME MATTERS MORE THAN THE SCORE. Docking a ligand back into the receptor conformation that was
solved WITH it ("self-docking") is a much easier problem than the one this program actually solves, which
is: start from an APO structure whose pocket is not shaped around any ligand, and find the bound pose. So
the benchmark is a cross-dock from apo, and the self-dock appears only as a CONTROL (below) that tells you
whether a failure came from the induced-fit gap or from the docking protocol itself.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ PRE-REGISTERED CRITERION — FIXED IN WRITING BEFORE THE FIRST RUN. DO NOT TUNE.
──────────────────────────────────────────────────────────────────────────────────────────────────────
PRIMARY ENDPOINT. Dock the holo ligand into the APO receptor using the pipeline's own settings — the box,
exhaustiveness and `num_modes` are read at run time out of `nr4a3_warhead.dock_into`, never re-typed —
and measure the symmetry-corrected heavy-atom RMSD of the TOP-RANKED pose to the crystallographic ligand,
after sequence-matched Ca superposition of the apo receptor onto the holo receptor over the pocket-lining
residues.

    RECOVERED      RMSD <= 2.00 A       (`RECOVER_RMSD_A`)
    PARTIAL        2.00 A < RMSD <= 4.00 A  — right region of the protein, wrong pose (`PARTIAL_RMSD_A`)
    NOT RECOVERED  RMSD > 4.00 A

2.00 A is not chosen here: it is the field's standard redocking-success boundary, the same number used by
the Astex/CASF/PDBbind pose-prediction evaluations. 4.00 A is the conventional "wrong pose" boundary in the
same literature. SECONDARY endpoint: fraction of native ligand-contacting receptor residues recovered
(`fnat`), success at >= 0.50 — reported always, and never used to overturn the primary.

CONTROLS, ALSO FIXED IN ADVANCE, because a bare number here would not be interpretable:
  C1 SELF-DOCK into the HOLO receptor, identical settings. **If C1 does not clear 2.00 A the whole
     experiment is INCONCLUSIVE**, not a failure of the apo pipeline: a protocol that cannot recover the
     pose when handed the very conformer the ligand was solved in is being measured on the protocol, not
     on induced fit. Stated this way before running so it cannot become an excuse afterwards.
  C2 RANDOM-IN-BOX NULL, `N_NULL` random rigid placements of the same ligand inside the same box. This is
     the POWER of the criterion: if a random placement clears 2.00 A with non-negligible probability, then
     passing means nothing. `selcal_interface_signature.py` records the opposite failure — a check so
     strict it reported a real recovery as a miss — and both are the same bug, a criterion whose power was
     never measured.
  C3 BLIND vs ORACLE BOX. The pipeline picks its pocket with fpocket and never sees the ligand, so the
     primary endpoint uses the BLIND box. An ORACLE box centred on the crystallographic ligand is run
     alongside **purely as a decomposition**: blind-fails-while-oracle-succeeds means pocket DETECTION
     failed; both failing means pose PLACEMENT failed. The oracle number is never the headline and can
     never turn a NOT RECOVERED into a pass.
  C1b ONE CONTROL PER BLIND ARM (added 2026-08-02 after the first scored panel; the primary endpoint is
     UNCHANGED). C1 as written self-docks through the pipeline's transferred site only. When that site is
     not where the ligand actually binds — 4REF is "TR3 LBD_L449W in complex with Molecule 2", an
     engineered tryptophan mutant whose ligand sits ~19 A from the canonical nuclear-receptor cavity — C1
     fails for a reason that says nothing about whether the DOCKING works, and it drags the independent
     fpocket arm down with it. So each blind arm now carries a self-dock through its own site-selection
     route and is reported against that. This ADDS reporting; it moves no threshold and cannot turn a
     failure into a pass.

──────────────────────────────────────────────────────────────────────────────────────────────────────
★★ SITE AND DOCKING ARE TWO QUESTIONS, AND THE FIRST PANEL COULD NOT TELL THEM APART (added 2026-08-02,
   second revision. NOTHING PRE-REGISTERED MOVES: the primary endpoint, its bands, C1/C2/C3 and the
   verdict function are byte-identical in intent. What follows are ADDED endpoints and ADDED controls.)
──────────────────────────────────────────────────────────────────────────────────────────────────────
The first scored panel returned INCONCLUSIVE on 6 of 6 pairs because C1 failed, and the decomposition read
as "the docking is fine, the SITE SELECTION missed". That reading has a confound the panel could not see,
and the confound has to be settled before the site number means anything:

  ⛔ THE PIPELINE'S BOX IS NR4A3'S OWN POCKET-5 DRAGGED ACROSS BY A GLOBAL BLOSUM62 SEQUENCE ALIGNMENT
  (`nr4a3_warhead.map_pocket_to_paralogue`). The pipeline itself only ever performs that transfer onto
  `nr4a3_warhead.PARALOGUES` — NR4A1 and NR4A2 — and onto NR4A3's own 8XTT. The benchmark additionally
  performed it onto PPARG and RORC. Finding that an NR4A3 cryptic pocket does not land on PPARG's
  orthosteric cavity is close to expected and is NOT evidence that site selection is broken for NR4A3.
  So `site_transfer_regime.in_pipeline_regime` is now computed per pair FROM `nr4a3_warhead.PARALOGUES`
  (never re-typed here), and an out-of-regime pair's site arm is reported as NOT EVIDENCE about the
  pipeline rather than folded into a panel-level site claim.

The two questions, each now answered on its own arm and its own control:

  Q-DOCKING — GIVEN THE CORRECT SITE, does blind apo->holo docking recover the pose? Arm: `C3_oracle_box_apo`
     (apo receptor, box centred on the crystallographic ligand). Its control is `C1c_self_dock_holo_oracle_box`
     (holo receptor, same box) — the protocol ceiling. Same 2.00/4.00 A bands, unchanged. If the ceiling
     itself misses, this pair cannot answer the docking question and says so.
  Q-SITE — does a site-selection route put the crystallographic ligand INSIDE the box it draws? This is a
     GEOMETRIC endpoint with no docking in it: `SITE FOUND` iff the ligand's centroid lies inside the
     axis-aligned box of the pipeline's own `size_x/y/z`. That is the necessary condition for the docking
     to be able to return the right answer at all, it is free, and it is deterministic — where an RMSD
     through a stochastic search is neither. Fraction of ligand heavy atoms in the box, centre-to-ligand
     distance and native-contact recall of the box residues are reported beside it, always.
  C4 STRUCTURE-TRANSFERRED POCKET-5 (the confound control). Pocket-5 is carried onto the same receptor a
     second time by CE structural superposition (`Bio.PDB.cealign`) instead of by sequence. If the
     STRUCTURAL transfer lands on the ligand and the sequence transfer does not, the pipeline's alignment
     is what failed. If BOTH land far away, the crystallographic ligand is not in this receptor's
     Pocket-5-equivalent site at all, and "the pipeline missed the site" was the benchmark's design and
     not a defect. Those are opposite conclusions and no RMSD can separate them.
  C5 WHAT THE DEPOSIT ITSELF DECLARES, read from the file, never inferred: SEQADV engineered mutations
     (with the answer to "is the mutated residue one of the ligand's own contacts?"), and whether the holo
     title declares the ligand ALLOSTERIC. A benchmark whose ligand binds a declared allosteric site
     cannot test an orthosteric site-transfer, and a pocket that exists because of a point mutation is not
     the wild-type site any transfer is aiming at.
──────────────────────────────────────────────────────────────────────────────────────────────────────
★★ AND THE THIRD QUESTION, ADDED 2026-08-03: IS THE NUMBER WE QUOTE A MEASUREMENT AT ALL? (AGAIN NOTHING
   PRE-REGISTERED MOVES. C6 is a new control on existing arms; `verdict()` does not read it.)
──────────────────────────────────────────────────────────────────────────────────────────────────────
The pipeline's dock is an unseeded Monte-Carlo search, so every arm here returns ONE DRAW. Five CI runs
of this same benchmark have committed the blind-apo fpocket arm at 3.122, 3.437, 3.464, 3.503 and 3.04 A,
and the roadmap quotes the last as though it were the measurement. A conclusion drawn from one draw is
only safe if the pre-registered BAND is the same on every draw — which is a fact about this system that
had never been checked.

  C6 SEED REPLICATES. Re-run `blind_apo_fpocket_top_box`, `C3_oracle_box_apo` and
     `C1c_self_dock_holo_oracle_box` on the PRIMARY pair at `SEED_REPLICATES` explicit `--seed`s, every
     other setting still read out of `nr4a3_warhead.dock_into`. Report median, min-max, spread and — the
     ENDPOINT — whether all replicates fall in ONE pre-registered band. It cannot narrow a number and
     cannot turn a NOT RECOVERED into a pass; it can only say whether the digits are quotable.
     ⛔ `nr4a3_warhead` IS NOT SEEDED BY THIS. The pipeline stays as it is, because the unseeded search
     is the behaviour under test.
     The first seed is run TWICE as a determinism self-check: if smina does not reproduce at a fixed seed
     on this system then the spread is not seed-to-seed variation, and the artifact must say so instead
     of presenting it as one.
──────────────────────────────────────────────────────────────────────────────────────────────────────

★ A PANEL, NOT A PICK. `PANEL_SIZE` candidate pairs are attempted in the pre-registered rank order — one
per distinct crystallographic answer, at most `MAX_PER_PROTEIN` per protein — and EVERY one is reported,
including the ones R2b throws out. There is no early exit on "enough good ones", because an exit conditioned
on results is a way of choosing which results to have. The panel-level answer applies the same C1 rule one
level up: a pair whose control fails is uninterpretable, and the count of those is reported beside the
aggregate rather than averaged into it.

BOTH OUTCOMES, WRITTEN DOWN NOW:
  · RECOVERED  → the pipeline has been shown, once, to recover a crystallographic pose from an apo
    receptor in a nuclear-receptor LBD. That removes one specific reason to disbelieve the NR4A3 pose.
    It does NOT make the NR4A3 pose correct, and it says nothing about selectivity or efficacy.
  · NOT RECOVERED → the assumption under everything anchored to the denovo_401 pose has been tested and
    failed in a comparable regime. That does not prove the NR4A3 pose wrong. It removes the presumption
    that it is right, and the manuscript has to say so wherever "the pose" is currently singular.
  · INCONCLUSIVE → only via C1 or C2, and the reason must be named in the artifact.

⛔ NO THRESHOLD IN THIS MODULE MAY BE CHANGED AFTER THE FIRST RUN. A changed threshold goes in an appendix
with the superseded value retained (CLAUDE.md §1.2), never edited in place.
──────────────────────────────────────────────────────────────────────────────────────────────────────

★ THE BENCHMARK IS SOURCED, NEVER ASSUMED. `mode=source` runs a real RCSB query over a pre-declared list
of nuclear-receptor UniProt accessions, classifies every deposited entry as apo or holo from its own
non-polymer entities, and writes the whole considered set — including the rejects and why — into the
artifact. Selection then applies `SELECTION_RULES` in order. **If nothing passes, that is the finding**:
this module reports "no suitable benchmark exists" and stops, rather than substituting an easy globular
pocket and calling it a control.

⚠ AN INPUT WE COULD NOT READ IS UNREAD, NOT ABSENT — every network or parse failure is recorded in
`refusals` with the URL or path that produced it.

⛔ Claims nothing about NR4A3 selectivity, efficacy or a therapeutic window. Re-scores no leg, moves no
verdict, amends no preregistration.

Output: apo-pose-recovery.json.  MODE=source|select|run (default run). No GPU, no rental.

★★ TWO IN-REGIME SUPPLEMENTS, EACH IN ITS OWN FILE, NEITHER EVER SUMMED INTO THE PANEL ABOVE. The
pre-registered panel's rank order picked receptors the pipeline does not target, so its site arm carries
an OUT-OF-REGIME disqualifier on most pairs. These two ask the same questions where they actually bite:

  MODE=site        -> apo-pose-site-in-regime.json  · geometric containment, NO dock, covalent pairs
                      readable (R2b is a rule about docking). "Does a site route box the ligand at all?"
  MODE=regime_dock -> apo-pose-regime-dock.json     · the FULL arm set, R2b enforced. "On the NR4A fold,
                      blind from apo, does the protocol recover a KNOWN pose — and through which box?"

`MODE=regime_dock` is the family positive control the program repeatedly recorded as non-existent. See
`OUT_REGIME` for why that record was wrong: no NR4A3 holo structure exists, but NR4A1 and NR4A2 carry
deposited ones at ~60 % / ~66 % aligned identity, and they had never been docked into.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "apo-pose-recovery.json")
OUT_MD = os.path.join(HERE, "apo-pose-recovery.md")
#: MODE=site's own artifact. A separate question (geometric, docking-free, in-regime only) gets a
#: separate file so it can never be mistaken for — or written over — the pre-registered panel's result.
OUT_SITE = os.path.join(HERE, "apo-pose-site-in-regime.json")
#: ★★ MODE=regime_dock's own artifact (added 2026-08-03). THE FAMILY POSITIVE CONTROL.
#:
#: WHY IT EXISTS. This module already had both halves of the question and never put them together:
#: `MODE=run` DOCKS, but its pre-registered rank order picked 6 pairs across 3 receptors of which most
#: are OUT of the pipeline's regime (PPARG, RXRA), and `pair_questions` says so in every one of their
#: `disqualifiers`. `MODE=site` is IN regime — 14 NR4A1/NR4A2 pairs — but it is geometric containment
#: only and runs no dock at all. So the program has been saying, in the roadmap and the manuscript, that
#: **no positive control exists for pose prediction on this target**, while holding 14 crystallographic
#: ligand positions on the two closest paralogues (60.0 % / 65.6 % aligned identity to NR4A3) that had
#: never been docked into.
#:
#: THE QUESTION IT ANSWERS, which neither existing mode can: on the NR4A fold itself, blind from apo,
#: does this docking protocol recover a pose that is already known — and does the answer depend on which
#: site-selection route drew the box? Every arm is reported against ITS OWN control, so "the site was
#: wrong" and "the search was wrong" can never borrow each other's evidence.
#:
#: ⛔ IT IS NOT THE PRE-REGISTERED PANEL AND CANNOT BECOME IT. Different candidate list, different file,
#: no `verdict()` call — `apo-pose-recovery.json`'s INCONCLUSIVE stands untouched, and nothing here is
#: ever summed into its counts. R2b still excludes covalent ligands, because this mode DOES dock and a
#: non-covalent dock still cannot reproduce a covalent pose; that is what keeps it honest rather than
#: what makes it convenient (it costs the three NR4A2 pairs, the closest paralogue).
OUT_REGIME = os.path.join(HERE, "apo-pose-regime-dock.json")
WORK = os.environ.get("APO_RECOVERY_WORK", os.path.join(HERE, "_apo_recovery_work"))

# ---------------------------------------------------------------------------------- fixed thresholds
RECOVER_RMSD_A = 2.00      # field-standard redocking-success boundary
PARTIAL_RMSD_A = 4.00      # field-standard "wrong pose" boundary
FNAT_SUCCESS = 0.50        # secondary endpoint
N_NULL = 200               # random-in-box placements for the power control
NULL_POWER_MAX = 0.05      # if P(random <= RECOVER_RMSD_A) exceeds this, the criterion has no power

# ------------------------------------------------- ADDED 2026-08-02 (second revision). NONE OF THESE
# ------------------------------------------------- REPLACES A PRE-REGISTERED THRESHOLD; they are new
# ------------------------------------------------- endpoints on new arms. Registered in `_appendix`.
#: A pair is more than a rigid-receptor re-dock above this much apo->holo Ca movement AT THE LIGAND SITE.
#: 1.00 A is the conventional line between "same conformation" and a real conformational change in the
#: cross-docking literature; it is a REPORTING band here and gates nothing.
LARGE_INDUCED_FIT_A = 1.00
#: A Pocket-5 residue counts as carried across by the STRUCTURAL transfer when a receptor Ca lies within
#: this of its superposed Ca. 6.0 A is roughly two Ca-Ca steps — loose enough that a shifted loop still
#: maps, tight enough that "mapped" means the same position in the fold.
STRUCT_TRANSFER_MAX_CA_A = 6.00
#: Words in a holo title that DECLARE the ligand's site is allosteric. Reported, never filtering — but a
#: pair whose crystallographic ligand is declared allosteric cannot test an ORTHOSTERIC site transfer.
ALLOSTERIC_MARKERS = ("ALLOSTERIC", "NON-ORTHOSTERIC", "SECOND SITE")

# ------------------------------------------------- ADDED 2026-08-03 (third revision). AGAIN NOTHING
# ------------------------------------------------- PRE-REGISTERED MOVES: this is a new control on an
# ------------------------------------------------- existing arm, and it cannot change any verdict.
# ★★ C6 — IS THE NUMBER WE QUOTE A MEASUREMENT, OR ONE DRAW FROM A STOCHASTIC SEARCH?
#
# `nr4a3_warhead.dock_into` passes smina no `--seed`, so every arm in this module is a Monte-Carlo
# search re-seeded from the clock on each run. That is the pipeline's own behaviour and this module
# must not change it — but it means a single RMSD is a SAMPLE, not a constant, and the repo has
# already been bitten by treating one as the other: the blind-apo fpocket arm has been committed at
# 3.122, 3.437, 3.464, 3.503 and 3.04 A across five CI runs of this same benchmark, and the roadmap
# quotes the last of those as if it were the measurement.
#
# So C6 re-runs the three DECISION-CARRYING arms with distinct explicit `--seed`s and reports the
# spread. ⛔ THE ENDPOINT IS NOT A TIGHTER NUMBER — it is whether the pre-registered BAND
# (RECOVERED / PARTIAL / NOT RECOVERED) is stable across replicates. A band that holds means the
# conclusion survives the search noise even though the digits do not; a band that flips means no
# single-draw statement of this arm is quotable at all. Neither outcome can move `verdict()`, which
# still reads the pre-registered unseeded arms and nothing else.
#: Replicate docks per arm, on the PRIMARY pair only (the pair whose numbers are quoted downstream).
SEED_REPLICATES = int(os.environ.get("APO_SEED_REPLICATES", "5"))
#: Fixed, declared before the run so the replicate set cannot be chosen after seeing an answer. The
#: first seed is deliberately used TWICE (see `_determinism_selfcheck`): smina is only reproducible at
#: a fixed seed if its parallel search is, and asserting that rather than assuming it is the whole
#: point of a control on reproducibility.
REPLICATE_SEEDS = (20260803, 20260804, 20260805, 20260806, 20260807, 20260808, 20260809, 20260810)
#: Arms C6 replicates, and why each is decision-carrying:
#:   blind_apo_fpocket_top_box    — the arm the roadmap quotes (3.04 A), the only blind arm that lands
#:   C3_oracle_box_apo            — Q-DOCKING's own arm
#:   C1c_self_dock_holo_oracle_box— Q-DOCKING's ceiling; whether a pair is gradeable at all turns on it
REPLICATED_ARMS = ("blind_apo_fpocket_top_box", "C3_oracle_box_apo", "C1c_self_dock_holo_oracle_box")

# ------------------------------------------------- ADDED 2026-08-03 (fourth revision). A HOOK, NOT AN
# ------------------------------------------------- ARM. Default None; nothing in this module sets it.
# ★★ THE SECOND-METHOD HOOK. `pose_second_method.py` needs the EXACT prepared inputs this module builds
# — the same receptors, the same `bench_ligand.sdf`, the same boxes and the same `score_pose` — because a
# cross-method comparison whose two halves were prepared differently measures the preparation. Rebuilding
# that prep in a second module would be a silent fork of it; passing it out is not.
#
# ⛔ WHAT THIS HOOK MAY NOT DO, held by tests/test_pose_second_method.py:
#   · it is called AFTER `R_["arms"]` is complete and BEFORE `pair_questions`/`verdict`, and its return
#     value lands under the single key `second_method` — which `verdict()` does not read (it reads
#     `arms` and `C2_random_in_box_null` only). No added arm can turn a NOT RECOVERED into a pass.
#   · it moves no threshold, draws no box, and is OFF unless another module assigns it.
#   · an exception inside it is caught and recorded; it can never take down a pre-registered pair.
SECOND_METHOD_HOOK = None
# ★★ C6b — AND THE THING C6's FIRST RUN REVEALED, WHICH IS WORSE THAN DRIFTING DIGITS (2026-08-03).
# `Q_DOCKING`'s `n_gradeable` moved **3 -> 4** between two runs of the identical code, because
# `C1c_self_dock_holo_oracle_box` on 2QMV->9V8H drew 6.809 A one run and 1.916 A the next. The ceiling
# is what decides whether a pair may be graded AT ALL, so an unseeded draw is silently choosing the
# DENOMINATOR of the headline count — not just its digits. C6b re-seeds that one arm on EVERY pair and
# reports, per pair, on how many seeds the pair would have been gradeable. A pair that is gradeable on
# some seeds and not others is a pair whose inclusion is a coin flip, and the artifact must say so.
#: Ceiling replicates per pair. Smaller than SEED_REPLICATES because it runs on all pairs, not one.
CEILING_REPLICATES = int(os.environ.get("APO_CEILING_REPLICATES", "3"))

# ------------------------------------------------------------------- what counts as a real ligand
#: Non-polymer components that are crystallisation/cryo/buffer matter, not ligands. A structure carrying
#: only these is APO. Standard list; it is the reason a glycerol does not make a structure "holo".
ADDITIVES = {
    "HOH", "DOD", "SO4", "PO4", "GOL", "EDO", "PEG", "PG4", "PGE", "1PE", "2PE", "P6G", "MPD", "ACT",
    "ACY", "FMT", "CIT", "FLC", "TRS", "EPE", "MES", "IMD", "DMS", "TLA", "MLI", "OXL", "BME", "DTT",
    "IOD", "BR", "CL", "NA", "K", "MG", "CA", "ZN", "MN", "FE", "NI", "CO", "CU", "CD", "HG", "PT",
    "AU", "CS", "RB", "SR", "BA", "NH4", "AZI", "NO3", "CO3", "SCN", "UNX", "UNL", "PLM", "MYR",
    "BOG", "LDA", "C8E", "OCT", "HEZ", "BU3", "IPA", "EOH", "MOH", "ACE", "NH2", "SIN", "MRD",
}
LIG_MIN_MW = 200.0         # below this a "ligand" is an additive by another name
LIG_MAX_MW = 800.0         # above this it is a peptide/cofactor/lipid, not the regime being tested
LIG_MIN_HEAVY = 15

# ------------------------------------------------------------------- the family the search runs over
#: Human nuclear-receptor ligand-binding domains, declared BEFORE looking at what is deposited, so the
#: search cannot be steered toward a convenient answer. NR4A2/NR4A1 lead because they are NR4A3's own
#: subfamily and share its defining problem (an LBD reported to lack a classical ligand cavity), which is
#: precisely the regime the NR4A3 work is in.
NR_ACCESSIONS = [
    ("P43354", "NR4A2 / Nurr1",  "NR4A3's closest paralogue; LBD reported to have no classical cavity"),
    ("P22736", "NR4A1 / Nur77",  "NR4A subfamily; the other paralogue this program scores against"),
    ("Q92570", "NR4A3 / NOR-1",  "the target itself — included so its own deposits are counted, not to test on"),
    ("P19793", "RXRA",           "canonical apo LBD with a large holo-vs-apo helix-12 rearrangement"),
    ("P37231", "PPARG",          "apo and holo LBD both deposited; large, plastic pocket"),
    ("P10276", "RARA",           "classic NR apo/holo pair literature"),
    ("P51449", "RORC / RORgt",   "inverse-agonist chemistry with induced-fit pocket changes"),
    ("Q96RI1", "NR1H4 / FXR",    "well-populated apo and holo sets"),
    ("O75469", "NR1I2 / PXR",    "notoriously plastic pocket"),
    ("P11473", "VDR",            "apo/holo pair literature"),
    ("P10828", "THRB",           "apo/holo pair literature"),
    ("P04150", "NR3C1 / GR",     "apo LBD is unstable — included to test the search, not because it will win"),
]

RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_GRAPHQL = "https://data.rcsb.org/graphql"

#: Selection rules, applied IN ORDER. Recorded in the artifact so the choice is auditable.
SELECTION_RULES = [
    "R1 HARD  — apo and holo must be the same UniProt accession.",
    "R2 HARD  — the holo ligand must be drug-like: %.0f <= MW <= %.0f, >= %d heavy atoms, not an additive."
    % (LIG_MIN_MW, LIG_MAX_MW, LIG_MIN_HEAVY),
    "R3 HARD  — the apo entry must carry NO drug-like non-polymer entity at all (ions/buffers allowed).",
    "R4 HARD  — apo and holo sequences must align at >= 95 % identity over the common region (same "
    "protein, not a chimera or a distant ortholog).",
    "R5 HARD  — the apo receptor must yield at least one fpocket pocket, or there is nothing to dock into.",
    "R6 RANK  — prefer NR4A subfamily (NR4A2 > NR4A1 > others), because that is NR4A3's own regime.",
    "R7 RANK  — prefer an apo solved by SOLUTION NMR with multiple models, which mirrors 8XTT exactly.",
    "R8 RANK  — prefer better holo resolution, then better apo resolution.",
    "R9 REPORT — measure, do not assume, the apo->holo induced fit (pocket Ca RMSD) and record it.",
    "R2b HARD — the holo ligand must NOT be covalently linked to the receptor (no LINK record joining it "
    "to a protein atom). A non-covalent docking protocol cannot in principle reproduce a covalent pose, so "
    "scoring one would measure the wrong thing. ADDED 2026-08-02 AFTER SOURCING BUT BEFORE ANY RMSD "
    "EXISTED — the first run's primary arm errored at the site transfer, so no recovery number had been "
    "computed when this rule was written. Recorded here rather than edited in silently (CLAUDE.md §1.2).",
]

#: How many distinct benchmark pairs to run. ONE case is thin and invites the reading that the pair was
#: chosen for its answer, so the panel is fixed at three DISTINCT crystallographic answers and every member
#: is reported whatever it returns. The PRIMARY verdict is still the rank-1 pair; the rest are supporting
#: cases, never a menu to pick from.
N_BENCHMARKS = 3

#: At most this many pairs from any one protein, so the panel is not one protein N times.
MAX_PER_PROTEIN = 2

#: How many candidate pairs the panel ATTEMPTS. Every one of them is reported, whatever it returns — there
#: is no early exit on "enough good ones", because an early exit conditioned on results is a way of
#: choosing which results to have. The list is fixed by SELECTION_RULES before any structure is fetched.
PANEL_SIZE = 12

#: ⛔ CLAUDE.md §1.2 — CHANGES GO IN AN APPENDIX, WITH THE SUPERSEDED VALUE RETAINED. Emitted into the
#: artifact as `_appendix` so a reader of the JSON alone can see exactly what moved and what did not.
#: The pre-registered PRIMARY endpoint, its 2.00/4.00 A bands, C1, C2 and C3 are UNCHANGED — every entry
#: below either ADDS an arm/endpoint or corrects a sentence that over-claimed.
APPENDIX = {
    "unchanged": [
        "PRIMARY endpoint: symmetry-corrected heavy-atom RMSD of the top pose from the APO receptor, "
        "through the pipeline's own site transfer, after site-Ca superposition. Bands 2.00 / 4.00 A.",
        "C1 (self-dock into holo through the pipeline's box) still makes a pair INCONCLUSIVE when it fails.",
        "C2 random-in-box null and its 0.05 power line.",
        "C3 oracle box remains a decomposition and never a headline.",
        "`verdict()` is unchanged: no added arm can turn a NOT RECOVERED into a pass.",
    ],
    "added_2026_08_02_second_revision": [
        "Q-SITE: a GEOMETRIC site endpoint — SITE FOUND iff the crystallographic ligand's centroid lies "
        "inside the box the route drew. No docking in it, so it is deterministic.",
        "Q-DOCKING: the docking question asked with the site handed over (C3 arm) against its own ceiling "
        "control (C1c), so a docking answer never borrows the site arm's evidence.",
        "C4 structural transfer: NR4A3 Pocket-5 carried onto the same receptor a second time by CE "
        "structural superposition (Bio.PDB.cealign) instead of by BLOSUM62, plus its blind arm and its "
        "own self-dock control. This is the confound control: only two independent transfers can "
        "separate 'the alignment failed' from 'the ligand is not in the Pocket-5-equivalent site'.",
        "C5 declared facts read from the deposit: SEQADV engineered substitutions (and whether any is one "
        "of the ligand's own contact residues) and a holo-title allosteric declaration.",
        "A regime gate on the site question, computed from `nr4a3_warhead.PARALOGUES` rather than typed: "
        "a receptor the pipeline never transfers onto is not evidence about the pipeline's site step.",
        "LARGE_INDUCED_FIT_A = 1.00 A: a REPORTING band on the apo->holo site Ca RMSD, gating nothing.",
    ],
    "added_2026_08_03_third_revision": [
        "C6 SEED REPLICATES on the primary pair: the three decision-carrying arms "
        "(`blind_apo_fpocket_top_box`, `C3_oracle_box_apo`, `C1c_self_dock_holo_oracle_box`) are re-run "
        "at SEED_REPLICATES explicit `--seed`s. Its endpoint is whether the PRE-REGISTERED BAND survives "
        "re-seeding, not a tighter number, and `verdict()` does not read it.",
        "A determinism self-check inside C6: the first seed is run twice, so a spread cannot be "
        "attributed to seeding unless smina is shown to reproduce at a fixed seed on this system.",
        "`reproducibility`: the panel-level rollup of C6, carrying `all_bands_stable` and `max_spread_A`. "
        "An absent replicate set records `measured: false` rather than an empty summary.",
        "C6b SEED REPLICATES ON THE CEILING ARM, on EVERY pair. `Q_DOCKING.n_gradeable` moved 3 -> 4 "
        "between two runs of identical code because `C1c_self_dock_holo_oracle_box` on 2QMV->9V8H drew "
        "6.809 A one run and 1.916 A the next; the ceiling decides whether a pair may be graded at all, "
        "so an unseeded draw was choosing the headline count's DENOMINATOR. C6b reports, per pair, on how "
        "many seeds the pair would have been gradeable, and `reproducibility.gradeability` rolls it up.",
        "MODE=site — the IN-REGIME SITE SUPPLEMENT. The geometric site endpoint, run over every apo/holo "
        "pair on a protein `nr4a3_warhead.PARALOGUES` says the pipeline actually transfers Pocket-5 onto, "
        "with no per-protein cap and NO DOCK. It writes its own artifact (`apo-pose-site-in-regime.json`) "
        "and is never summed into the pre-registered panel, which is unchanged. Reason: the panel could "
        "offer only TWO in-regime pairs, both against the same apo structure (4RZF) and both NR4A1.",
        "R2b is not applied in `site_only` mode, and that is a scope correction rather than a loosening: "
        "R2b exists because a NON-COVALENT DOCK cannot reproduce a covalent pose, and the site endpoint "
        "contains no dock. It had removed BOTH NR4A2 pairs (5Y41/RPG, 5YD6/8SU, each LINK SG CYS 566 -> "
        "ligand C11) — NR4A3's closest paralogue — from a question they can answer. The pre-registered "
        "DOCKING panel still excludes them; every covalent pair read by the supplement is flagged.",
        "★★ MODE=regime_dock — THE FAMILY POSITIVE CONTROL. The same in-regime candidate list as "
        "MODE=site, but DOCKED: every pair runs the full arm set (pipeline box, fpocket box, oracle box) "
        "each against the self-dock control that goes through the SAME site route, and the panel answer "
        "is a COUNT of pre-registered bands over the pairs whose own control passed. It writes "
        "`apo-pose-regime-dock.json`, calls no panel-level `verdict()`, and cannot change the "
        "pre-registered panel's INCONCLUSIVE. R2b IS enforced here — this mode docks — which costs the "
        "three NR4A2 pairs and is the honest price of the question. Reason it exists: the roadmap, the "
        "manuscript and every status report state that no positive control exists for pose prediction on "
        "this target. That is true of NR4A3 (no holo structure) and FALSE for the family — NR4A1 and "
        "NR4A2 carry deposited holo structures at ~60 % / ~66 % aligned identity, i.e. real "
        "crystallographic answers on the same fold, which had never been docked into.",
        "APO_REGIME_PANEL_BUDGET_S = 12000 s — regime_dock's own wall-clock guard. Reusing the "
        "pre-registered panel's 4500 s (sized for ~6 pairs) would have recorded the tail of an ~11-pair "
        "panel as UNRUN and reported a family control over whichever pairs happened to fit.",
        "C5b — the APO deposit's engineered substitutions are now graded too, and the two SEQADV sets are "
        "compared: `apo_and_holo_are_the_same_construct`. C5 read the holo side only, which silently "
        "assumed a pair is two states of ONE construct; on the headline pair (4RZF S441W / 4REF L449W) it "
        "is two different NR4A1 tryptophan mutants, so the cross-dock is cross-CONSTRUCT as well as "
        "apo->holo and the induced-fit number is not pure conformational change. Reported, never "
        "filtering.",
    ],
    "corrected_2026_08_03": [
        {"what": "`_dedup_pairs` — the panel pool's projected key list",
         "superseded": "dropped `apo_chains` and `holo_chains`, so the accession-scoped receptor-chain "
                       "restriction ran against None on EVERY panel pair — the repair for the 1DSZ "
                       "RXR/RAR heterodimer was written, landed, and was inert. Evidence on CI run "
                       "30764845241: result.chains = {holo_declared: null, apo_declared: null}, "
                       "considered_top carries both fields and panel_pool carries neither, and "
                       "1DSZ->9GFE / 1DSZ->3KMR still refused at identity 0.321 — the number the code's "
                       "own comment names as that bug's symptom",
         "now": "both fields are carried into the panel pool. This can only ADD interpretable pairs; it "
                "moves no threshold and changes no arm's definition."},
        {"what": "the `alignment` refusal text",
         "superseded": "passed `map_uniprot_to_pdb`'s message through unchanged, which hard-codes "
                       "'Q92570 and 8XTT' — so an RXRA pair was reported as failing to align against "
                       "NR4A3's NMR structure, naming two proteins neither of which is in the pair",
         "now": "the refusal names the actual apo/holo entries, the chains compared, the declared chain "
                "sets, and says a low identity between two deposits of the SAME accession is a "
                "CHAIN-SELECTION symptom first. The upstream function is untouched — other lanes call it."},
    ],
    "corrected_2026_08_02": [
        {"what": "`boxes.pipeline_box_fpocket_rank._reads`",
         "superseded": "asserted 'the site the pipeline's Pocket-5 transfer selected IS a cavity on this "
                       "receptor' whenever the transferred residues touched a pocket by even one residue — "
                       "printed beside `n_shared_residues: 1` on the headline pair",
         "now": "the rank is unchanged and still reported; the SENTENCE is conditioned on the share, and "
                "the share itself (`frac_transferred_residues_in_that_pocket`) is now emitted"},
        {"what": "PAIR_BUDGET_S / PANEL_BUDGET_S",
         "superseded": "420 s per pair / 2700 s per panel",
         "now": "900 s / 4500 s — a wall-clock hang-guard raised for the added arms. It can only decide "
                "whether an arm RUNS (recorded UNRUN if not), never what an arm returns."},
    ],
}

#: Wall-clock budget per candidate pair, and for the panel as a whole. CLAUDE.md §6: the per-unit timeout
#: is the real hang-guard. One pathological ligand — a substructure match that goes exponential, an RCSB
#: fetch that stalls — must cost that pair and no more, and must surface as a REFUSAL with its elapsed
#: time rather than as a killed job with nothing written.
#: ⚠ RAISED 2026-08-02 (420 -> 900, 2700 -> 4500) when the site/docking split added two docking arms and a
#: structural superposition per pair. This is a WALL-CLOCK HANG-GUARD, not a scientific threshold: it can
#: only decide whether an arm RUNS, never what it returns, and a pair that exceeds it is recorded UNRUN.
#: The superseded values are registered in `_appendix` exactly like any other corrected number.
PAIR_BUDGET_S = int(os.environ.get("APO_PAIR_BUDGET_S", "900"))
PANEL_BUDGET_S = int(os.environ.get("APO_PANEL_BUDGET_S", "4500"))
#: ★ MODE=regime_dock's own wall-clock guard, and it is DELIBERATELY NOT `PANEL_BUDGET_S`. That budget is
#: sized for the pre-registered panel's ~6 pairs; the regime panel has ~11 gradeable pairs after R2b, so
#: reusing it would silently record the tail as UNRUN and then report a family control over whichever
#: pairs happened to fit — the exact "silent cap" failure CLAUDE.md forbids. Same nature as the others:
#: a hang-guard that can only decide whether a pair RUNS, never what it returns. `PAIR_BUDGET_S` stays
#: the per-pair guard, so 11 x 900 s is the worst case this must accommodate.
REGIME_PANEL_BUDGET_S = int(os.environ.get("APO_REGIME_PANEL_BUDGET_S", "12000"))


# ==================================================================================================
# NETWORK — every failure becomes a refusal with its URL.
# ==================================================================================================

def _get(url, data=None, timeout=60):
    req = urllib.request.Request(url, data=data,
                                 headers={"Accept": "application/json",
                                          "Content-Type": "application/json",
                                          "User-Agent": "Rare-cancers/apo_pose_recovery"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.loads(fh.read().decode("utf-8"))


def entries_for_accession(acc):
    """[pdb_id] deposited for this UniProt accession, or (None, why). A real query, not a memory."""
    q = {
        "query": {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers."
                         "reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": acc}},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": 500}, "results_verbosity": "compact"},
    }
    url = RCSB_SEARCH + "?json=" + urllib.parse.quote(json.dumps(q))
    try:
        doc = _get(url)
    except Exception as e:                                    # noqa: BLE001
        return None, "%s: %s (%s)" % (type(e).__name__, e, RCSB_SEARCH)
    return [str(x) for x in doc.get("result_set", [])], None


ENTRY_QUERY = """
query($ids:[String!]!){
  entries(entry_ids:$ids){
    rcsb_id
    struct { title }
    exptl { method }
    rcsb_entry_info { resolution_combined polymer_entity_count_protein nonpolymer_entity_count
                      deposited_model_count }
    polymer_entities {
      entity_poly { pdbx_seq_one_letter_code_can }
      rcsb_polymer_entity_container_identifiers {
        auth_asym_ids
        reference_sequence_identifiers { database_accession database_name }
      }
    }
    nonpolymer_entities {
      rcsb_nonpolymer_entity_container_identifiers { auth_asym_ids }
      nonpolymer_comp {
        chem_comp { id name formula_weight type }
        rcsb_chem_comp_descriptor { SMILES_stereo }
      }
    }
  }
}
"""


def entry_details(ids, batch=40):
    """Full metadata for a list of entry ids, or (None, why). One GraphQL call per batch."""
    out, why = [], None
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        body = json.dumps({"query": ENTRY_QUERY, "variables": {"ids": chunk}}).encode()
        try:
            doc = _get(RCSB_GRAPHQL, data=body)
        except Exception as e:                                # noqa: BLE001
            why = "%s: %s (%s, batch starting %s)" % (type(e).__name__, e, RCSB_GRAPHQL, chunk[0])
            continue
        if doc.get("errors"):
            why = "GraphQL errors: %s" % json.dumps(doc["errors"])[:300]
        out.extend([e for e in (doc.get("data") or {}).get("entries") or [] if e])
    return out, why


# ==================================================================================================
# PURE CLASSIFICATION — no network. Unit-tested in tests/test_apo_pose_recovery.py.
# ==================================================================================================

def drug_like(comp):
    """Is this chem-comp record a real ligand rather than crystallisation matter? (bool, why)."""
    cid = (comp or {}).get("id") or ""
    if not cid:
        return False, "no comp id"
    if cid.upper() in ADDITIVES:
        return False, "%s is on the crystallisation-additive list" % cid
    mw = comp.get("formula_weight")
    if mw is None:
        return False, "%s has no formula weight" % cid
    if mw < LIG_MIN_MW:
        return False, "%s MW %.1f < %.0f" % (cid, mw, LIG_MIN_MW)
    if mw > LIG_MAX_MW:
        return False, "%s MW %.1f > %.0f" % (cid, mw, LIG_MAX_MW)
    ctype = (comp.get("type") or "").upper()
    if "PEPTIDE" in ctype or "SACCHARIDE" in ctype or "RNA" in ctype or "DNA" in ctype:
        return False, "%s type %r is not a small molecule" % (cid, comp.get("type"))
    return True, "%s MW %.1f, type %s" % (cid, mw, comp.get("type"))


def classify_entry(entry, accession):
    """{pdb, method, resolution, n_models, ligands[], apo(bool), seq, ...} from one GraphQL record."""
    info = entry.get("rcsb_entry_info") or {}
    res = (info.get("resolution_combined") or [None])
    ligands, rejected = [], []
    for ne in entry.get("nonpolymer_entities") or []:
        comp = ((ne.get("nonpolymer_comp") or {}).get("chem_comp")) or {}
        desc = ((ne.get("nonpolymer_comp") or {}).get("rcsb_chem_comp_descriptor")) or {}
        ok, why = drug_like(comp)
        rec = {"comp_id": comp.get("id"), "name": comp.get("name"),
               "mw": comp.get("formula_weight"), "type": comp.get("type"),
               "smiles": desc.get("SMILES_stereo"),
               "chains": (ne.get("rcsb_nonpolymer_entity_container_identifiers") or {})
               .get("auth_asym_ids") or [], "why": why}
        (ligands if ok else rejected).append(rec)
    seq, chains = None, []
    for pe in entry.get("polymer_entities") or []:
        ids = (pe.get("rcsb_polymer_entity_container_identifiers") or {})
        accs = [(r or {}).get("database_accession")
                for r in (ids.get("reference_sequence_identifiers") or [])]
        if accession in accs:
            seq = ((pe.get("entity_poly") or {}).get("pdbx_seq_one_letter_code_can") or "").replace("\n", "")
            chains = ids.get("auth_asym_ids") or []
            break
    return {
        "pdb": entry.get("rcsb_id"),
        "title": ((entry.get("struct") or {}).get("title") or "")[:180],
        "method": ((entry.get("exptl") or [{}])[0] or {}).get("method"),
        "resolution_A": res[0] if res else None,
        "n_models": info.get("deposited_model_count"),
        "ligands": ligands,
        "non_ligand_components": [r["comp_id"] for r in rejected],
        "apo": not ligands,
        "sequence": seq,
        "chains": chains,
    }


def pair_candidates(by_acc):
    """[(score, candidate)] apo/holo pairs, ranked by SELECTION_RULES. Pure — takes classified entries."""
    prio = {a: i for i, (a, _n, _w) in enumerate(NR_ACCESSIONS)}
    out = []
    for acc, rec in by_acc.items():
        apos = [e for e in rec["entries"] if e["apo"] and e["sequence"]]
        holos = [e for e in rec["entries"] if e["ligands"] and e["sequence"]]
        if not apos or not holos:
            continue
        for apo in apos:
            for holo in holos:
                lig = max(holo["ligands"], key=lambda l: l.get("mw") or 0)
                cand = {
                    "accession": acc, "protein": rec["name"], "apo": apo["pdb"], "holo": holo["pdb"],
                    "apo_chains": apo.get("chains") or [], "holo_chains": holo.get("chains") or [],
                    "apo_method": apo["method"], "apo_models": apo["n_models"],
                    "apo_resolution_A": apo["resolution_A"], "holo_resolution_A": holo["resolution_A"],
                    "ligand": {k: lig.get(k) for k in ("comp_id", "name", "mw", "smiles")},
                    "apo_title": apo["title"], "holo_title": holo["title"],
                }
                nmr = 1 if (apo["method"] or "").upper().startswith("SOLUTION NMR") else 0
                score = (
                    prio.get(acc, 99),                                    # R6
                    -nmr,                                                 # R7
                    holo["resolution_A"] if holo["resolution_A"] is not None else 9.9,   # R8
                    apo["resolution_A"] if apo["resolution_A"] is not None else 9.9,
                )
                out.append((score, cand))
    out.sort(key=lambda t: t[0])
    return out


# ==================================================================================================
# STRUCTURE HANDLING
# ==================================================================================================

def fetch_pdb(pdb_id, dest):
    import nr4a3_8xtt_benchmark as bm
    return bm.fetch_rcsb(pdb_id, dest)


def protein_only(pdb_text, chain=None):
    """ATOM records of one chain (the largest if unspecified) + END. First MODEL only."""
    lines, cur_chain_counts = [], {}
    for line in pdb_text.splitlines(keepends=True):
        if line.startswith("ENDMDL"):
            break
        if line.startswith("ATOM"):
            cur_chain_counts[line[21]] = cur_chain_counts.get(line[21], 0) + 1
            lines.append(line)
    if not lines:
        return ""
    want = chain or max(cur_chain_counts, key=lambda c: cur_chain_counts[c])
    keep = [l for l in lines if l[21] == want and l[16] in (" ", "A")]
    return "".join(keep) + "END\n"


def ligand_hetatms(pdb_text, comp_id):
    """HETATM lines of the largest copy of `comp_id` (first model), grouped by (chain, resseq)."""
    groups = {}
    for line in pdb_text.splitlines(keepends=True):
        if line.startswith("ENDMDL"):
            break
        if line.startswith("HETATM") and line[17:20].strip().upper() == comp_id.upper():
            if line[16] not in (" ", "A"):
                continue
            groups.setdefault((line[21], line[22:26]), []).append(line)
    if not groups:
        return None, None
    key = max(groups, key=lambda k: len(groups[k]))
    return groups[key], key


#: Words in a deposit title that declare an engineered construct. ⛔ REPORTED, NEVER FILTERED — a rule that
#: removed structures until the benchmark passed would be exactly the tuning this module forbids. But a
#: reader has to SEE it: 4REF ("Crystal Structure of TR3 LBD_L449W in complex with Molecule 2") is a
#: tryptophan point mutant whose ligand sits ~19 A from the canonical nuclear-receptor cavity, and that is
#: what its arms are measuring.
MUTANT_MARKERS = ("MUTANT", "MUTATION", " MUT ", "_L4", "_S4", "_W4", "_F4")


def engineered_flag(*titles):
    """(bool, evidence) — does any deposit title declare an engineered construct? Reported, never gating."""
    hits = [t for t in titles if any(m in (t or "").upper() for m in MUTANT_MARKERS)]
    return bool(hits), hits


def allosteric_flag(*titles):
    """(bool, evidence) — does any deposit title DECLARE the ligand's site allosteric? Never gating.

    ⛔ THIS IS READ, NOT JUDGED. The depositor wrote "in complex with allosteric ligand FM156" into the
    title of 7NPC; nothing here decides from chemistry or from a pocket ranking whether a site is
    allosteric. A pair that carries this flag cannot test an ORTHOSTERIC site transfer, because the
    crystallographic answer is somewhere the transfer was never aiming."""
    hits = [t for t in titles if any(m in (t or "").upper() for m in ALLOSTERIC_MARKERS)]
    return bool(hits), hits


def seqadv_mutations(pdb_text, chain=None):
    """Engineered mutations DECLARED BY THE DEPOSITOR, parsed from the deposit's own SEQADV records.

    ⛔ THE DEPOSIT IS THE ONLY HONEST SOURCE FOR THIS. `engineered_flag` reads the TITLE, which is prose:
    it says "L449W" without saying which residue number the file uses, and 4REF's own chain is not
    numbered the way the title is. SEQADV states the substitution in the FILE's numbering against the
    UniProt residue it replaced, plus the depositor's reason string — so "is the engineered residue one of
    the ligand's own contacts?" becomes a lookup rather than an assumption.

    Format is the wwPDB fixed-column SEQADV record."""
    out = []
    for line in pdb_text.splitlines():
        if not line.startswith("SEQADV"):
            continue
        try:
            ch = line[16]
            if chain and ch != chain:
                continue
            resseq = int(line[18:22])
        except (ValueError, IndexError):
            continue
        out.append({"chain": ch, "resseq": resseq,
                    "deposit_residue": line[12:15].strip(),
                    "db": line[24:28].strip(), "db_accession": line[29:38].strip(),
                    "db_residue": line[39:42].strip(),
                    "reason": line[49:70].strip()})
    return out


def box_containment(center, size, points):
    """Is the crystallographic answer INSIDE the box a site-selection route drew? Pure geometry.

    ⛔ THIS IS THE SITE ENDPOINT AND IT CONTAINS NO DOCKING. smina cannot return a pose outside its own
    box, so a ligand outside the box is a site failure with probability 1 and no search, scoring, seed or
    force field enters the answer. Reporting the site question through an RMSD — as the first panel had
    to — mixes a deterministic fact with a stochastic one and then cannot say which moved."""
    if center is None or not points:
        return None
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    inside = [p for p in points
              if abs(p[0] - center[0]) <= hx and abs(p[1] - center[1]) <= hy
              and abs(p[2] - center[2]) <= hz]
    cen = centroid(points)
    return {"ligand_centroid_in_box": (abs(cen[0] - center[0]) <= hx and abs(cen[1] - center[1]) <= hy
                                       and abs(cen[2] - center[2]) <= hz),
            "frac_ligand_heavy_atoms_in_box": round(len(inside) / float(len(points)), 3),
            "n_ligand_heavy_atoms": len(points),
            "box_center_to_ligand_centroid_A": round(math.dist(center, cen), 3),
            "_box_size_A": [round(s, 2) for s in size]}


def site_answer(center, size, lig_points_same_frame, box_residues, res_map, native, site_label):
    """The Q-SITE readout for ONE site-selection route. `res_map` carries box residue numbers into the
    holo numbering `native` is expressed in (identity map for a holo-frame box)."""
    if center is None:
        return {"answer": "UNREAD", "_site": site_label}
    geom = box_containment(center, size, lig_points_same_frame) or {}
    row = {"_site": site_label, **geom}
    if box_residues:
        mapped = {res_map.get(r, r) for r in box_residues} if res_map else set(box_residues)
        nat = set(native or [])
        row["n_box_residues"] = len(set(box_residues))
        row["n_box_residues_that_are_native_contacts"] = len(mapped & nat)
        row["native_contact_recall_of_box_residues"] = (round(len(mapped & nat) / len(nat), 3)
                                                        if nat else None)
    row["answer"] = ("SITE FOUND" if geom.get("ligand_centroid_in_box") else "SITE MISSED")
    return row


def covalent_links(pdb_text, comp_id):
    """LINK records joining `comp_id` to anything else — R2b's evidence, read from the deposit itself.

    A LINK record is how the PDB states a covalent bond between residues, so a ligand appearing in one is
    covalently attached and a non-covalent dock cannot reproduce its pose by construction. Read from the
    file rather than inferred from the ligand's chemistry, because only the depositor knows."""
    out = []
    want = comp_id.upper()
    for line in pdb_text.splitlines():
        if not line.startswith("LINK"):
            continue
        if line[17:20].strip().upper() == want or line[47:50].strip().upper() == want:
            out.append(line.rstrip())
    return out


def het_coords(lines):
    out = []
    for l in lines:
        elem = (l[76:78].strip() or l[12:16].strip()[:1]).upper()
        if elem == "H" or elem == "D":
            continue
        out.append((float(l[30:38]), float(l[38:46]), float(l[46:54])))
    return out


def centroid(points):
    n = float(len(points))
    return tuple(sum(p[i] for p in points) / n for i in range(3))


def residues_near(pdb_text, points, cutoff):
    """{resseq} of protein residues with a heavy atom within `cutoff` of any of `points`."""
    c2 = cutoff * cutoff
    hit = set()
    for line in pdb_text.splitlines():
        if not line.startswith("ATOM"):
            continue
        elem = (line[76:78].strip() or line[12:16].strip()[:1]).upper()
        if elem == "H":
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            r = int(line[22:26])
        except ValueError:
            continue
        for (px, py, pz) in points:
            if (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2 <= c2:
                hit.add(r)
                break
    return hit


# ==================================================================================================
# THE RUN
# ==================================================================================================

def pipeline_dock_params():
    """The docking settings THE PIPELINE uses, read out of its own source — never re-typed here.

    `nr4a3_warhead.dock_into` hard-codes the box size, exhaustiveness and num_modes in the smina command
    it builds. Parsing them out means this benchmark cannot drift away from the pipeline it is testing;
    if someone changes the pipeline's exhaustiveness, this module changes with it and says so."""
    import inspect
    import nr4a3_warhead as wh
    src = inspect.getsource(wh.dock_into)
    out = {}
    for key in ("size_x", "size_y", "size_z", "exhaustiveness", "num_modes"):
        marker = '"--%s", "' % key
        i = src.find(marker)
        if i >= 0:
            out[key] = src[i + len(marker):src.find('"', i + len(marker))]
    out["_read_from"] = "nr4a3_warhead.dock_into source"
    return out


def dock(receptor_pdb, center, ligand_sdf, tag, work, num_modes=None):
    """The pipeline's own dock. `num_modes` override is used ONLY by the diagnostic multi-pose run."""
    import nr4a3_warhead as wh
    wh.OUT = work
    if num_modes is None:
        return wh.dock_into(receptor_pdb, center, ligand_sdf, tag)
    # diagnostic variant: same command, more modes retained
    import nr4a3_dock as ndock
    smina = ndock._which("smina")
    out_sdf = os.path.join(work, "docked_%s.sdf" % tag)
    p = pipeline_dock_params()
    subprocess.run([smina, "-r", receptor_pdb, "-l", ligand_sdf,
                    "--center_x", str(center[0]), "--center_y", str(center[1]),
                    "--center_z", str(center[2]),
                    "--size_x", p.get("size_x", "24"), "--size_y", p.get("size_y", "24"),
                    "--size_z", p.get("size_z", "24"),
                    "--exhaustiveness", p.get("exhaustiveness", "8"),
                    "--num_modes", str(num_modes), "-o", out_sdf],
                   capture_output=True, text=True)
    return {}, out_sdf


def dock_seeded(receptor_pdb, center, ligand_sdf, tag, work, seed):
    """The pipeline's own dock command with an explicit `--seed`. C6 only.

    ⛔ EVERY SETTING EXCEPT THE SEED IS READ OUT OF `nr4a3_warhead.dock_into` BY `pipeline_dock_params`,
    exactly as the pre-registered arms do. This is the same search with its randomness pinned, not a
    different protocol — the whole value of the control depends on that, because a replicate run at a
    different exhaustiveness would measure the settings rather than the noise.

    ⚠ It does NOT touch `nr4a3_warhead`. The pipeline stays unseeded, which is the behaviour under test;
    adding a seed there would silently change every downstream number this program has ever produced."""
    import nr4a3_dock as ndock
    smina = ndock._which("smina")
    if not smina:
        return None, "smina not on PATH"
    out_sdf = os.path.join(work, "docked_%s.sdf" % tag)
    p = pipeline_dock_params()
    subprocess.run([smina, "-r", receptor_pdb, "-l", ligand_sdf,
                    "--center_x", str(center[0]), "--center_y", str(center[1]),
                    "--center_z", str(center[2]),
                    "--size_x", p.get("size_x", "24"), "--size_y", p.get("size_y", "24"),
                    "--size_z", p.get("size_z", "24"),
                    "--exhaustiveness", p.get("exhaustiveness", "8"),
                    "--num_modes", p.get("num_modes", "1"),
                    "--seed", str(seed), "-o", out_sdf],
                   capture_output=True, text=True)
    return out_sdf, None


def crystal_mol(lines, smiles):
    """The crystallographic ligand as an RDKit molecule with the reference bond graph, or (None, why).

    ⛔ CORRESPONDENCE IS CHEMICAL. The crystal copy carries CCD atom names and the docked copy carries
    RDKit's own; matching by name or by proximity would report a small deviation for a flipped molecule
    (the failure documented in `selcal_cofold_decompose.py`). So the crystal coordinates are posed onto a
    molecule built from the CCD SMILES, and RMSD is then a graph match with automorphisms enumerated."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    ref = Chem.MolFromSmiles(smiles) if smiles else None
    if ref is None:
        return None, "CCD SMILES unparseable: %r" % (smiles,)
    ref = Chem.RemoveHs(ref)
    xyz = het_coords(lines)
    if len(xyz) != ref.GetNumAtoms():
        # a partially-occupied or alternate-conformer copy; refuse rather than guess a correspondence
        return None, ("crystal copy has %d heavy atoms but the CCD graph has %d — refusing to guess an "
                      "atom correspondence" % (len(xyz), ref.GetNumAtoms()))
    order = _pdb_order_to_ccd(lines, ref)
    if order is None:
        return None, "could not order the crystal atoms onto the CCD graph"
    conf = Chem.Conformer(ref.GetNumAtoms())
    from rdkit.Geometry import Point3D
    for ccd_i, pdb_i in enumerate(order):
        x, y, z = xyz[pdb_i]
        conf.SetAtomPosition(ccd_i, Point3D(x, y, z))
    m = Chem.Mol(ref)
    m.RemoveAllConformers()
    m.AddConformer(conf, assignId=True)
    try:
        Chem.SanitizeMol(m)
    except Exception as e:                                    # noqa: BLE001
        return None, "sanitize failed: %s" % e
    AllChem.AssignStereochemistryFrom3D(m)
    return m, None


def _pdb_order_to_ccd(lines, ref):
    """Index map CCD-atom -> line index, by element-matched graph isomorphism on the distance geometry.

    Both copies are the same component, so a correspondence exists; it is found by building a molecule
    from the crystal coordinates with RDKit's connectivity perception and substructure-matching the CCD
    skeleton onto it — a GRAPH match, so a flipped or mis-ordered deposit still maps correctly."""
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds
    heavy = [l for l in lines if (l[76:78].strip() or l[12:16].strip()[:1]).upper() not in ("H", "D")]
    block = ["%d" % len(heavy), "crystal"]
    for l in heavy:
        elem = (l[76:78].strip() or l[12:16].strip()[:1]).title()
        block.append("%s %s %s %s" % (elem, l[30:38].strip(), l[38:46].strip(), l[46:54].strip()))
    try:
        raw = Chem.MolFromXYZBlock("\n".join(block) + "\n")
        if raw is None:
            return None
        rdDetermineBonds.DetermineConnectivity(raw)
    except Exception:                                         # noqa: BLE001
        return None
    skel = Chem.Mol(ref)
    for b in skel.GetBonds():
        b.SetBondType(Chem.BondType.SINGLE)
        b.SetIsAromatic(False)
    for a in skel.GetAtoms():
        a.SetIsAromatic(False)
        a.SetNoImplicit(True)
        a.SetNumExplicitHs(0)
        a.SetFormalCharge(0)
    try:
        Chem.SanitizeMol(skel, Chem.SanitizeFlags.SANITIZE_SYMMRINGS |
                         Chem.SanitizeFlags.SANITIZE_ADJUSTHS, catchErrors=True)
    except Exception:                                         # noqa: BLE001
        pass
    match = raw.GetSubstructMatch(skel, useChirality=False)
    if match and len(match) == ref.GetNumAtoms():
        return list(match)
    return None


def random_in_box_null(mol, center, size, n=N_NULL, seed=20260802):
    """RMSD distribution of `n` random rigid placements of `mol` inside the docking box.

    The POWER of the 2 A criterion. Rotations are drawn from a uniform quaternion so orientations are not
    biased toward the identity, and translations uniformly inside the box, which is exactly the space the
    docking search is allowed to explore."""
    import random
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign
    from rdkit.Geometry import Point3D
    rng = random.Random(seed)
    conf = mol.GetConformer()
    pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(mol.GetNumAtoms())]
    c = centroid(pts)
    local = [(p[0] - c[0], p[1] - c[1], p[2] - c[2]) for p in pts]
    half = [s / 2.0 for s in size]
    vals = []
    for _ in range(n):
        u1, u2, u3 = rng.random(), rng.random(), rng.random()
        q = (math.sqrt(1 - u1) * math.sin(2 * math.pi * u2), math.sqrt(1 - u1) * math.cos(2 * math.pi * u2),
             math.sqrt(u1) * math.sin(2 * math.pi * u3), math.sqrt(u1) * math.cos(2 * math.pi * u3))
        x, y, z, w = q
        R = [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
             [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
             [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]
        t = (center[0] + rng.uniform(-half[0], half[0]),
             center[1] + rng.uniform(-half[1], half[1]),
             center[2] + rng.uniform(-half[2], half[2]))
        cand = Chem.Mol(mol)
        cc = cand.GetConformer()
        for i, (lx, ly, lz) in enumerate(local):
            cc.SetAtomPosition(i, Point3D(
                R[0][0] * lx + R[0][1] * ly + R[0][2] * lz + t[0],
                R[1][0] * lx + R[1][1] * ly + R[1][2] * lz + t[1],
                R[2][0] * lx + R[2][1] * ly + R[2][2] * lz + t[2]))
        try:
            vals.append(float(rdMolAlign.CalcRMS(cand, mol)))
        except Exception:                                     # noqa: BLE001
            continue
    vals.sort()
    if not vals:
        return {"n": 0, "p_within_criterion": None}
    return {"n": len(vals), "min_A": round(vals[0], 2), "median_A": round(vals[len(vals) // 2], 2),
            "max_A": round(vals[-1], 2),
            "p_within_criterion": round(sum(1 for v in vals if v <= RECOVER_RMSD_A) / len(vals), 4),
            "_criterion_A": RECOVER_RMSD_A,
            "_note": "uniform random rigid placements of the same ligand in the same box; this is the "
                     "probability that the success criterion is met by chance"}


# ==================================================================================================
# BOX PLACEMENT — three, one of them primary, all declared before the run.
# ==================================================================================================
# ⛔ WHICH BOX IS THE PRIMARY ENDPOINT IS A PRE-REGISTERED CHOICE, and it is the one that mirrors what the
# NR4A3 pipeline actually did. That pipeline did NOT take fpocket's top-ranked pocket: it took the
# ORTHOSTERIC NR cavity ("Pocket 5", nr4a3_dock.py) and used fpocket to confirm it was druggable, then
# transferred that site onto every other receptor — onto 8XTT by sequence alignment
# (nr4a3_8xtt_redock.py) and onto NR4A1/NR4A2 by BLOSUM62 alignment (nr4a3_warhead.py). Granting the
# benchmark the same prior knowledge, by the same transfer, is what makes this a test OF THE PIPELINE
# rather than a test of fpocket's ranking. The fully-agnostic top-druggability box is reported alongside
# it, and the oracle box only as the C3 decomposition.

def nr4a3_lbd_reference(af2_reference_pdb, work):
    """The AF2 NR4A3 LBD window as a standalone PDB, or (None, why).

    ⚠ THE WINDOW MATTERS. `AF-Q92570.pdb` is the FULL-LENGTH model; a global BLOSUM62 alignment of 626
    residues against a ~250-residue LBD construct pays end-gap penalties that can shift the mapping. The
    pipeline never aligns the full-length model either — `nr4a3_matrix`/`nr4a3_warhead` work on the
    LBD-trimmed receptor. So the reference written here is the same window
    (`nr4a3_8xtt_benchmark.LBD_FIRST..LBD_LAST`), and the identity that comes out is REPORTED, not assumed.
    """
    import nr4a3_8xtt_benchmark as bm
    if not os.path.exists(af2_reference_pdb):
        return None, "AF2 reference not on disk: %s" % af2_reference_pdb
    keep = []
    for line in open(af2_reference_pdb, errors="replace"):
        if not line.startswith("ATOM"):
            continue
        try:
            r = int(line[22:26])
        except ValueError:
            continue
        if bm.LBD_FIRST <= r <= bm.LBD_LAST:
            keep.append(line)
    if not keep:
        return None, "no residues in the LBD window %d-%d of %s" % (bm.LBD_FIRST, bm.LBD_LAST,
                                                                    af2_reference_pdb)
    return _write(os.path.join(work, "nr4a3_lbd_reference.pdb"), "".join(keep) + "END\n"), None


def transfer_identity(ref_pdb, receptor_pdb):
    """Aligned-column identity between the two chains, for the record. NEVER a gate here — see below."""
    import nr4a3_8xtt_benchmark as bm
    try:
        _c, _rn, sa, _ca = bm.chain_ca(_read(ref_pdb))
        _c2, _rn2, sb, _ca2 = bm.chain_ca(_read(receptor_pdb))
        ba, bb = bm._biopython_align(sa, sb)
        return round(bm.identity_from_blocks(ba, bb, sa, sb), 4)
    except Exception:                                         # noqa: BLE001
        return None


def pipeline_box(receptor_pdb, af2_reference_pdb, work):
    """PRIMARY box: NR4A3's own Pocket-5 transferred onto this receptor, then Ca centroid.

    ⛔ THE TRANSFER KERNEL IS `nr4a3_warhead.map_pocket_to_paralogue`, NOT `map_uniprot_to_pdb`, and the
    difference is load-bearing — it is the bug the first CI run died on. `map_uniprot_to_pdb` RAISES below
    80 % identity (`MIN_ALIGN_IDENTITY`) because it exists to map Q92570 onto a deposit of the SAME
    protein, where a low identity means a corrupt download. The benchmark receptor is a DIFFERENT protein
    (NR4A2 measured at 0.656 against NR4A3), so that guard fired on the very best candidate and returned
    an error with no science attached. `map_pocket_to_paralogue` is the kernel the pipeline ACTUALLY uses
    to carry Pocket-5 onto NR4A1 and NR4A2 — this identical operation, at this identical identity — and it
    has no such gate. Boxing is then `nr4a3_warhead.pocket_box`, so "the site" means here what it means
    everywhere else in the pipeline.

    Returns (center, detail) or (None, why). Uses NO ligand information."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_warhead as wh
    ref, why = nr4a3_lbd_reference(af2_reference_pdb, work)
    if ref is None:
        return None, why
    try:
        mapped = wh.map_pocket_to_paralogue(ref, receptor_pdb, list(bm.POCKET5))
    except Exception as e:                                    # noqa: BLE001
        return None, "Pocket-5 transfer failed: %s: %s" % (type(e).__name__, e)
    ident = transfer_identity(ref, receptor_pdb)
    if not mapped:
        return None, ("no NR4A3 Pocket-5 residue mapped onto this receptor (aligned identity %s) — the "
                      "site transfer the pipeline relies on does not reach this protein" % ident)
    try:
        center, nbox = wh.pocket_box(receptor_pdb, mapped)
    except Exception as e:                                    # noqa: BLE001
        return None, "pocket_box failed on the mapped residues: %s" % e
    return center, {"mapped_residues": sorted(set(mapped)), "n_box_ca": nbox,
                    "nr4a3_aligned_identity": ident,
                    "n_pocket5_transferred": len(set(mapped)), "n_pocket5_source": len(bm.POCKET5),
                    "_source": "NR4A3 Pocket-5 (nr4a3_8xtt_benchmark.POCKET5) carried across by "
                               "nr4a3_warhead.map_pocket_to_paralogue — the pipeline's own transfer"}

def pocket5_structure_transfer(ref_pdb, receptor_pdb):
    """C4 — Pocket-5 carried onto this receptor by STRUCTURAL superposition, not by sequence.

    ⛔ WHY THIS EXISTS, AND WHY IT IS THE ONLY ARM THAT CAN SETTLE THE ARGUMENT. `pipeline_box` transfers
    Pocket-5 with a global BLOSUM62 alignment of the two Ca sequences. On NR4A1 that runs at ~0.60 aligned
    identity; on PPARG and RORC it runs at ~0.24-0.27, which is the twilight zone where a global sequence
    alignment of a 250-residue domain is not reliable. So a pipeline box that misses the ligand has TWO
    possible causes with OPPOSITE meanings:
        (a) the alignment put Pocket-5 in the wrong place  -> the pipeline's site step is broken;
        (b) the alignment was right and the ligand simply is not in this receptor's Pocket-5-equivalent
            site -> the benchmark asked the transfer to find something it was never aiming at.
    A docking RMSD cannot separate them, because both give the same big number. A SECOND, INDEPENDENT
    transfer can: CE structural alignment (`Bio.PDB.cealign`) matches the two folds without ever looking
    at the sequence. Agreement between the two transfers rules out (a); disagreement localises it.

    Uses NO ligand information. Returns (center, detail) or (None, why)."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_warhead as wh
    try:
        from Bio.PDB import PDBParser
        from Bio.PDB.cealign import CEAligner
    except Exception as e:                                    # noqa: BLE001
        return None, "Bio.PDB.cealign unavailable: %s: %s" % (type(e).__name__, e)
    try:
        parser = PDBParser(QUIET=True)
        rec = parser.get_structure("rec", receptor_pdb)
        ref = parser.get_structure("ref", ref_pdb)
        aligner = CEAligner()
        aligner.set_reference(rec)
        aligner.align(ref)                                    # moves `ref` into the receptor's frame
    except Exception as e:                                    # noqa: BLE001
        return None, "CE structural alignment failed: %s: %s" % (type(e).__name__, e)

    def ca_by_resnum(structure):
        d = {}
        for res in structure.get_residues():
            if "CA" in res:
                d[res.id[1]] = tuple(float(v) for v in res["CA"].coord)
        return d

    rec_ca, ref_ca = ca_by_resnum(rec), ca_by_resnum(ref)
    if not rec_ca or not ref_ca:
        return None, "no CA atoms after the structural superposition"
    mapped, unmapped, n_carried = [], [], 0
    for r in bm.POCKET5:
        p = ref_ca.get(r)
        if p is None:
            unmapped.append({"pocket5_residue": r, "why": "absent from the NR4A3 LBD reference"})
            continue
        best, bestd = None, None
        for rr, q in rec_ca.items():
            d = math.dist(p, q)
            if bestd is None or d < bestd:
                best, bestd = rr, d
        if bestd is not None and bestd <= STRUCT_TRANSFER_MAX_CA_A:
            mapped.append(best)
            n_carried += 1
        else:
            unmapped.append({"pocket5_residue": r,
                             "why": "nearest receptor CA %.2f A away, past the %.2f A cutoff"
                                    % (bestd if bestd is not None else float("nan"),
                                       STRUCT_TRANSFER_MAX_CA_A)})
    if not mapped:
        return None, ("CE superposition placed no NR4A3 Pocket-5 residue within %.1f A of any receptor CA "
                      "(CE RMSD %s A over the guide atoms)" % (STRUCT_TRANSFER_MAX_CA_A, aligner.rms))
    try:
        center, nbox = wh.pocket_box(receptor_pdb, mapped)
    except Exception as e:                                    # noqa: BLE001
        return None, "pocket_box failed on the structurally-transferred residues: %s" % e
    return center, {"mapped_residues": sorted(set(mapped)), "n_box_ca": nbox,
                    "ce_rms_A": round(float(aligner.rms), 3) if aligner.rms is not None else None,
                    # ⚠ TWO DIFFERENT COUNTS, both reported, because they answer different questions:
                    # how many Pocket-5 residues found a partner (`n_pocket5_transferred`), and how many
                    # DISTINCT receptor residues that landed on (`n_unique_receptor_residues`). Two
                    # Pocket-5 residues collapsing onto one receptor residue is normal and is not a loss.
                    "n_pocket5_transferred": n_carried, "n_pocket5_source": len(bm.POCKET5),
                    "n_unique_receptor_residues": len(set(mapped)),
                    "unmapped": unmapped, "_max_ca_A": STRUCT_TRANSFER_MAX_CA_A,
                    "_source": "NR4A3 Pocket-5 carried across by CE STRUCTURAL superposition "
                               "(Bio.PDB.cealign) — sequence-independent, the control on the pipeline's "
                               "BLOSUM62 transfer"}


def fpocket_boxes(receptor_pdb):
    """([pocket...] ranked by druggability, why) from fpocket on this receptor. No ligand information."""
    import nr4a3_8xtt_benchmark as bm
    import shutil
    if not shutil.which("fpocket"):
        return None, "fpocket not on PATH"
    try:
        pockets = bm.fpocket_pockets_with_residues(receptor_pdb)
    except Exception as e:                                    # noqa: BLE001
        return None, "fpocket failed: %s: %s" % (type(e).__name__, e)
    pockets.sort(key=lambda p: (-(p.get("druggability") or 0), -(p.get("alpha_spheres") or 0)))
    return pockets, None


# ==================================================================================================
# ORCHESTRATION
# ==================================================================================================

def _largest_of(pdb_text, allowed=None):
    """The chain with the most ATOM records, restricted to `allowed` when the deposit declares them."""
    counts = {}
    for line in pdb_text.splitlines():
        if line.startswith("ENDMDL"):
            break
        if line.startswith("ATOM"):
            counts[line[21]] = counts.get(line[21], 0) + 1
    if allowed:
        keep = {c: n for c, n in counts.items() if c in set(allowed)}
        counts = keep or counts
    return max(counts, key=lambda c: counts[c]) if counts else None


def _chain_nearest(pdb_text, points, cutoff=6.0, allowed=None):
    """The protein chain with the most heavy atoms near `points` — the chain the ligand actually binds.

    `allowed` restricts the answer to the chains the deposit assigns to the UniProt entity under test, so a
    heterodimer cannot hand back the partner protein."""
    c2 = cutoff * cutoff
    counts = {}
    for line in pdb_text.splitlines():
        if line.startswith("ENDMDL"):
            break
        if not line.startswith("ATOM"):
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        for (px, py, pz) in points:
            if (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2 <= c2:
                counts[line[21]] = counts.get(line[21], 0) + 1
                break
    if allowed:
        keep = {c: n for c, n in counts.items() if c in set(allowed)}
        counts = keep or counts
    return max(counts, key=lambda c: counts[c]) if counts else None


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    return path


def _read(path):
    with open(path, errors="replace") as fh:
        return fh.read()


def _contact_a():
    import inspect
    import nr4a3_warhead as wh
    return float(inspect.signature(wh.handle_contacts).parameters["cutoff"].default)


def _heavy_coords(mol):
    conf = mol.GetConformer()
    return [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
            for i, a in enumerate(mol.GetAtoms()) if a.GetAtomicNum() > 1]


def _transform_mol(mol, R, t):
    import nr4a3_8xtt_benchmark as bm
    from rdkit import Chem
    from rdkit.Geometry import Point3D
    out = Chem.Mol(mol)
    conf = out.GetConformer()
    pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(out.GetNumAtoms())]
    for i, (x, y, z) in enumerate(bm.apply_transform(pts, R, t)):
        conf.SetAtomPosition(i, Point3D(x, y, z))
    return out


def _top_pose(sdf_path, label):
    from rdkit import Chem
    if not os.path.exists(sdf_path):
        return None, "no pose file at %s" % sdf_path
    for m in Chem.SDMolSupplier(sdf_path, removeHs=True, sanitize=True):
        if m is not None:
            return m, None
    return None, "pose file %s held no readable molecule" % os.path.basename(sdf_path)


def seed_replicates(n, work, sdf, comp, score_pose, arms, plan, out_of_time):
    """C6: re-run the decision-carrying arms at explicit seeds and report the SPREAD and the BAND.

    ⛔ THIS FUNCTION OWNS NO THRESHOLD. It re-uses `score_pose` — the same scorer the pre-registered
    arms use — so a replicate is graded by the same rule as the arm it replicates, and `_band` is the
    pre-registered 2.00/4.00 A banding untouched.

    ⚠ AN UNRUN REPLICATE IS RECORDED AS UNRUN, never dropped: an arm whose box was never drawn, or a
    pair that ran out of wall clock, produces `n_replicates: 0` with the reason attached. Averaging
    over "the ones that happened to finish" is how a spread gets quietly narrowed."""
    out = {"_endpoint": ("does the pre-registered BAND survive re-seeding? The spread is reported "
                         "beside it; neither can change `verdict()`."),
           "_why": ("nr4a3_warhead.dock_into passes smina no --seed, so each pre-registered arm is ONE "
                    "draw from a Monte-Carlo search. This measures how wide that draw is."),
           "n_requested": n, "seeds": list(REPLICATE_SEEDS[:n]), "arms": {}}
    for name in REPLICATED_ARMS:
        recv, center, transform = plan.get(name, (None, None, True))
        row = {"unseeded_rmsd_A": (arms.get(name) or {}).get("rmsd_A"),
               "unseeded_band": _band((arms.get(name) or {}).get("rmsd_A"))}
        if center is None or recv is None:
            row.update({"n_replicates": 0,
                        "why": "this arm drew no box on this pair, so there is nothing to re-seed"})
            out["arms"][name] = row
            continue
        if out_of_time("C6_seed_replicates:" + name):
            row.update({"n_replicates": 0, "why": "pair budget spent — the replicates are UNRUN"})
            out["arms"][name] = row
            continue
        # The first seed is run TWICE. If smina is reproducible at a fixed seed the two agree exactly;
        # if they do not, every "replicate" below is confounded by non-determinism and the artifact has
        # to say so rather than presenting the spread as seed-to-seed variation.
        seeds = list(REPLICATE_SEEDS[:n]) + [REPLICATE_SEEDS[0]]
        vals, rows = [], []
        for i, sd in enumerate(seeds):
            sdf_out, why = dock_seeded(recv, center, sdf, "%s_seed%d_%d" % (name, sd, i), work, sd)
            if not sdf_out:
                rows.append({"seed": sd, "rmsd_A": None, "why": why})
                continue
            mol, why = _top_pose(sdf_out, comp)
            sc = score_pose(mol, transform=transform) if mol else {"rmsd_A": None, "why": why}
            rows.append({"seed": sd, "rmsd_A": sc.get("rmsd_A"), "fnat": sc.get("fnat"),
                         "band": sc.get("verdict"), "_repeat_of_first": i == len(seeds) - 1})
            if sc.get("rmsd_A") is not None and i < len(seeds) - 1:
                vals.append(sc["rmsd_A"])
        first = next((r for r in rows if not r.get("_repeat_of_first")), None)
        rep = rows[-1] if rows and rows[-1].get("_repeat_of_first") else None
        row["_determinism_selfcheck"] = {
            "seed": REPLICATE_SEEDS[0],
            "first_rmsd_A": (first or {}).get("rmsd_A"), "repeat_rmsd_A": (rep or {}).get("rmsd_A"),
            "identical": (first is not None and rep is not None
                          and first.get("rmsd_A") == rep.get("rmsd_A")),
            "_reads": ("smina at a fixed seed is reproducible here, so the spread below is seed-to-seed "
                       "search variation and nothing else"
                       if (first is not None and rep is not None
                           and first.get("rmsd_A") == rep.get("rmsd_A")) else
                       "⚠ THE SAME SEED DID NOT REPRODUCE — the spread below is search variation PLUS "
                       "non-determinism, and no part of it may be attributed to seeding alone")}
        row["replicates"] = rows
        if vals:
            srt = sorted(vals)
            bands = sorted({_band(v) for v in vals})
            row.update({
                "n_replicates": len(vals), "min_A": min(srt), "max_A": max(srt),
                "median_A": round(srt[len(srt) // 2] if len(srt) % 2
                                  else (srt[len(srt) // 2 - 1] + srt[len(srt) // 2]) / 2.0, 3),
                "spread_A": round(max(srt) - min(srt), 3),
                "bands_seen": bands, "band_stable": len(bands) == 1,
                "_reads": ("the pre-registered band is %s on every replicate, so the CONCLUSION survives "
                           "the search noise even though the digits do not — quote the band, never the "
                           "3-figure RMSD" % bands[0] if len(bands) == 1 else
                           "⛔ THE BAND FLIPS ACROSS SEEDS (%s). No single-draw statement of this arm is "
                           "quotable; the arm reports a distribution or it reports nothing"
                           % ", ".join(bands))})
        else:
            row.update({"n_replicates": 0, "why": "no replicate returned a scorable pose"})
        out["arms"][name] = row
    return out


def run_benchmark(cand, work, af2_reference_pdb, replicates=0, site_only=False,
                  ceiling_replicates=0):
    """The whole known-answer test for ONE apo/holo pair. Returns a result dict (never raises).

    `site_only=True` runs the GEOMETRIC site question and stops before any dock. It is used by the
    in-regime site supplement (`MODE=site`) and never by the pre-registered panel; nothing it produces
    is summed into the panel's counts, and it emits no `verdict`."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_dock as ndock
    from rdkit.Chem import rdMolAlign
    os.makedirs(work, exist_ok=True)
    cutoff = _contact_a()
    R_ = {"candidate": cand, "refusals": [], "params": pipeline_dock_params(), "contact_A": cutoff,
          "criterion": {"recovered_rmsd_A": RECOVER_RMSD_A, "partial_rmsd_A": PARTIAL_RMSD_A,
                        "fnat_success": FNAT_SUCCESS, "n_null": N_NULL,
                        "null_power_max": NULL_POWER_MAX}}

    deadline = time.time() + PAIR_BUDGET_S

    def refuse(stage, why):
        R_["refusals"].append({"stage": stage, "evidence": why})
        return R_

    def out_of_time(stage):
        if time.time() > deadline:
            R_["refusals"].append({"stage": stage, "evidence":
                                   "pair exceeded its %ds budget; the arms after this point are UNRUN, "
                                   "not failed" % PAIR_BUDGET_S})
            return True
        return False

    # 1) structures
    try:
        apo_txt = _read(fetch_pdb(cand["apo"], os.path.join(work, cand["apo"] + ".pdb")))
        holo_txt = _read(fetch_pdb(cand["holo"], os.path.join(work, cand["holo"] + ".pdb")))
    except Exception as e:                                    # noqa: BLE001
        extra = ""
        if "404" in str(e):
            extra = (" — files.rcsb.org serves no legacy PDB-format file for this entry (large or recent "
                     "depositions are mmCIF-only), so this pair is UNREAD for a FILE-FORMAT reason, not a "
                     "scientific one. It biases the panel toward older entries and is recorded so that bias "
                     "is visible.")
        return refuse("fetch", "%s: %s%s" % (type(e).__name__, e, extra))

    # 2) the crystallographic answer
    comp = (cand["ligand"] or {}).get("comp_id")
    links = covalent_links(holo_txt, comp)
    R_["covalent_links"] = links
    # ★★ R2b IS A RULE ABOUT DOCKING, AND THE SITE QUESTION CONTAINS NO DOCKING (added 2026-08-03).
    # A covalent ligand's crystallographic position is still the crystallographic answer; what a
    # non-covalent dock cannot do is REPRODUCE it. `Q_SITE` asks only whether a site-selection route
    # draws a box the ligand's centroid falls inside — geometry, no search, no scoring. So in
    # `site_only` mode R2b is RECORDED and does not exclude.
    # ⛔ WHY THIS MATTERS AND IS NOT A LOOPHOLE: R2b threw out BOTH NR4A2 pairs (5Y41/RPG and 5YD6/8SU,
    # each LINKed SG CYS 566 -> ligand C11), and NR4A2 is NR4A3's CLOSEST paralogue and one of only two
    # proteins the pipeline ever transfers Pocket-5 onto. The pre-registered docking panel keeps
    # excluding them; the site supplement can read them, and it is reported separately so the two can
    # never be summed.
    if links and not site_only:
        R_["excluded_by"] = "R2b"
        return refuse("R2b", "%s is COVALENTLY linked in %s (%d LINK record(s)); a non-covalent dock "
                             "cannot reproduce a covalent pose. First: %s"
                             % (comp, cand["holo"], len(links), links[0][:80]))
    if links:
        R_["covalent_but_site_gradeable"] = (
            "%s is COVALENTLY linked in %s (%d LINK record(s)) and is therefore excluded from the "
            "pre-registered DOCKING panel by R2b. It is read here because the site endpoint is geometric "
            "and contains no dock. First: %s" % (comp, cand["holo"], len(links), links[0][:80]))
    lines, key = ligand_hetatms(holo_txt, comp)  # noqa: E501  (see the R2b note above)
    if not lines:
        return refuse("crystal_ligand", "no HETATM copy of %s in %s" % (comp, cand["holo"]))
    xtal_pts = het_coords(lines)
    xtal, why = crystal_mol(lines, (cand["ligand"] or {}).get("smiles"))
    if xtal is None:
        return refuse("crystal_ligand", why)
    R_["crystal"] = {"comp_id": comp, "copy": "chain %s resseq %s" % key, "n_heavy": len(xtal_pts)}
    flag, ev = engineered_flag(cand.get("apo_title"), cand.get("holo_title"))
    R_["engineered_construct"] = {"declared_in_title": flag, "evidence": ev,
                                  "_note": "reported, never filtered — a mutant designed to create or "
                                           "probe a pocket is not the wild-type site the pipeline targets, "
                                           "and a reader must be able to see that from the artifact"}
    aflag, aev = allosteric_flag(cand.get("holo_title"))
    R_["declared_allosteric"] = {"declared_in_holo_title": aflag, "evidence": aev,
                                 "_reads": "the DEPOSITOR says this ligand occupies an allosteric site. "
                                           "An orthosteric site transfer cannot be graded on it — the "
                                           "crystallographic answer is somewhere the transfer never aimed"}

    # 3) receptors — the holo chain the ligand actually touches, and the apo's largest chain
    # ⛔ THE RECEPTOR CHAIN MUST FOLLOW THE ACCESSION, NOT ATOM COUNT. 1DSZ is an RXR/RAR heterodimer on
    # DNA; taking "the largest chain" handed the RARA pair an RXR chain and the apo<->holo alignment then
    # returned 0.321 identity and refused — a real pair thrown away by a chain-picking bug, not by science.
    # The auth_asym_ids for THIS UniProt entity come from the same GraphQL record that classified the entry.
    holo_chain = _chain_nearest(holo_txt, xtal_pts, allowed=cand.get("holo_chains"))
    holo_rec = _write(os.path.join(work, "holo_rec.pdb"), protein_only(holo_txt, holo_chain))
    apo_rec = _write(os.path.join(work, "apo_rec.pdb"),
                     protein_only(apo_txt, _largest_of(apo_txt, cand.get("apo_chains"))))
    R_["chains"] = {"holo_used": holo_chain, "holo_declared": cand.get("holo_chains"),
                    "apo_declared": cand.get("apo_chains")}
    try:
        _hc, holo_resnums, holo_seq, holo_ca = bm.chain_ca(_read(holo_rec))
        _ac, apo_resnums, apo_seq, apo_ca = bm.chain_ca(_read(apo_rec))
    except Exception as e:                                    # noqa: BLE001
        return refuse("receptor", "chain_ca failed: %s" % e)

    # 4) R4 — apo and holo must be the same protein, measured not assumed
    try:
        apo_to_holo, ident = bm.map_uniprot_to_pdb(apo_seq, apo_resnums, holo_seq, holo_resnums)
    except Exception as e:                                    # noqa: BLE001
        # ⚠ `map_uniprot_to_pdb` HARD-CODES "Q92570" AND "8XTT" IN ITS MESSAGE, because it was written for
        # that one mapping. Passed through unchanged it told the reader an RXRA pair had failed to align
        # against NR4A3's NMR structure — a refusal naming two proteins neither of which is in the pair.
        # The refusal is re-stated here with the pair and the chains that were actually compared, so the
        # NEXT diagnosis of it starts from the truth. The upstream function's semantics are untouched.
        return refuse("alignment",
                      "apo<->holo alignment failed for %s (chain %s, %d Ca) -> %s (chain %s, %d Ca), "
                      "declared chains apo=%s holo=%s. Underlying: %s ⚠ that message names Q92570/8XTT "
                      "because `nr4a3_8xtt_benchmark.map_uniprot_to_pdb` hard-codes them; NEITHER is in "
                      "this pair. A low identity between two deposits of the SAME accession is a "
                      "CHAIN-SELECTION symptom before it is a data problem."
                      % (cand["apo"], _largest_of(apo_txt, cand.get("apo_chains")), len(apo_resnums),
                         cand["holo"], holo_chain, len(holo_resnums),
                         cand.get("apo_chains"), cand.get("holo_chains"), e))
    R_["apo_holo_alignment"] = {"identity": round(ident, 4), "n_mapped": len(apo_to_holo)}
    if ident < 0.95:
        return refuse("R4", "apo<->holo sequence identity %.3f < 0.95" % ident)

    # 5) native contacts + the induced fit, measured (R9)
    native = sorted(residues_near(_read(holo_rec), xtal_pts, cutoff))
    R_["native_contact_residues_holo"] = native
    site_apo = [a for a, h in apo_to_holo.items() if h in set(native)]
    try:
        fit = bm.superpose_and_score(apo_ca, {a: holo_ca[h] for a, h in apo_to_holo.items() if h in holo_ca},
                                     list(apo_to_holo.keys()), site_apo, [])
        site_rms = round(fit["pocket_rmsd"], 3) if fit["pocket_rmsd"] else None
        R_["induced_fit"] = {"global_ca_rmsd_A": round(fit["global_rmsd"], 3),
                             "site_ca_rmsd_A": site_rms,
                             "n_fit": fit["n_fit"], "n_site": fit["n_pocket"],
                             # ★ HOW HARD A TEST IS THIS, ACTUALLY? A cross-dock across 0.14 A of Ca
                             # movement is a re-dock with extra steps: it is passed or failed on almost
                             # nothing. The band is stated on every pair so no single pair's number can be
                             # read as "apo->holo transfer works" when there was no transfer to make.
                             "large_rearrangement": (site_rms is not None
                                                     and site_rms >= LARGE_INDUCED_FIT_A),
                             "_large_rearrangement_A": LARGE_INDUCED_FIT_A,
                             "_note": "apo->holo Ca movement at the ligand site. This is the size of the "
                                      "problem the cross-dock has to solve; it is measured, not assumed."}
    except Exception as e:                                    # noqa: BLE001
        R_["refusals"].append({"stage": "induced_fit", "evidence": str(e)})

    # the evaluation transform: apo frame -> holo frame, fitted on the site Ca (standard practice; it
    # gives the docking no information, because the docking has already happened by the time it is used)
    # ⚠ THE INVERSE IS HOISTED HERE because the SITE endpoint needs it before any docking happens: the
    # apo-frame boxes must be tested against the crystallographic ligand carried into the APO frame, not
    # the other way round. Rotating a box is not the same operation as rotating the thing inside it.
    try:
        common = [a for a in site_apo if a in apo_ca and apo_to_holo[a] in holo_ca]
        Rm, tm = bm.kabsch_transform([apo_ca[a] for a in common],
                                     [holo_ca[apo_to_holo[a]] for a in common])
        Ri, ti = bm.kabsch_transform([holo_ca[apo_to_holo[a]] for a in common],
                                     [apo_ca[a] for a in common])
        xtal_pts_apo = bm.apply_transform(xtal_pts, Ri, ti)
        R_["evaluation_frame"] = {"fitted_on": "site Ca", "n": len(common)}
    except Exception as e:                                    # noqa: BLE001
        return refuse("evaluation_frame", "site superposition failed: %s" % e)

    # 6) the ligand, prepared exactly as the pipeline prepares one
    sdf = os.path.join(work, "bench_ligand.sdf")
    kept = ndock.make_sdf([(comp, comp, (cand["ligand"] or {}).get("smiles"))], sdf)
    if not kept:
        return refuse("ligand_prep", "RDKit could not build a 3D conformer of %s" % comp)

    # 7) boxes
    boxes = {}
    c, det = pipeline_box(apo_rec, af2_reference_pdb, work)
    boxes["pipeline_apo"] = {"center": c, "detail": det} if c else {"center": None, "why": det}
    ch, deth = pipeline_box(holo_rec, af2_reference_pdb, work)
    boxes["pipeline_holo"] = {"center": ch, "detail": deth} if ch else {"center": None, "why": deth}
    pockets, pwhy = fpocket_boxes(apo_rec)
    if pockets:
        import nr4a3_warhead as wh
        top = pockets[0]
        try:
            tc, _n = wh.pocket_box(apo_rec, top["residues"])
        except Exception as e:                                # noqa: BLE001
            tc = None
            pwhy = "pocket_box on the top fpocket pocket failed: %s" % e
        boxes["fpocket_top_apo"] = {"center": tc, "druggability": top.get("druggability"),
                                    "pocket": top.get("pocket"), "n_pockets": len(pockets)}
        # pocket DETECTION diagnostic: where does the native site rank among the apo's own pockets?
        site_apo_set = set(site_apo)
        ranks = [(i + 1, p) for i, p in enumerate(pockets) if site_apo_set & set(p["residues"])]
        # ⛔ THE DISCRIMINATING OBSERVATION for a pipeline-box failure, and it is free. If the transferred
        # site is itself a well-ranked cavity that simply does not hold THIS ligand, the pipeline looked in
        # a real pocket and the crystal ligand is elsewhere. If it is no cavity at all, the transfer is
        # broken. Those have opposite meanings and must never be reported as one "it failed".
        pl = set((boxes.get("pipeline_apo", {}).get("detail") or {}).get("mapped_residues") or [])
        pranks = [(i + 1, p) for i, p in enumerate(pockets) if pl & set(p["residues"])]
        # ⚠ CORRECTED 2026-08-02: this row used to assert "the transferred site IS a cavity" on ANY overlap
        # at all, and the first panel then printed that sentence beside `n_shared_residues: 1` — one residue
        # out of ten touching a pocket is not the transferred site sitting in that pocket. The rank is kept
        # (it is the real observable) and the SENTENCE is now conditioned on the share.
        _nshare = len(pl & set(pranks[0][1]["residues"])) if pranks else 0
        _frac = round(_nshare / float(len(pl)), 3) if pl else None
        boxes["pipeline_box_fpocket_rank"] = (
            {"rank_by_druggability": pranks[0][0], "druggability": pranks[0][1].get("druggability"),
             "n_shared_residues": _nshare, "n_transferred_residues": len(pl),
             "frac_transferred_residues_in_that_pocket": _frac,
             "_reads": ("the site the pipeline's Pocket-5 transfer selected IS substantially that cavity; "
                        "if the primary arm still missed, the crystal ligand is not in it"
                        if (_frac or 0) >= 0.5 else
                        "the transferred site only CLIPS this pocket (%s of %d residues) — the rank is a "
                        "contact, not a coincidence of sites, and must not be read as one"
                        % (_nshare, len(pl)))}
            if pranks else
            {"rank_by_druggability": None, "n_transferred_residues": len(pl),
             "_reads": "the site the pipeline's Pocket-5 transfer selected is not a cavity fpocket finds "
                       "on this receptor at all"})
        boxes["native_site_fpocket_rank"] = (
            {"rank_by_druggability": ranks[0][0], "druggability": ranks[0][1].get("druggability"),
             "n_shared_residues": len(site_apo_set & set(ranks[0][1]["residues"]))}
            if ranks else {"rank_by_druggability": None,
                           "_note": "no fpocket pocket on the APO receptor touches the native ligand site"})
    else:
        boxes["fpocket_top_apo"] = {"center": None, "why": pwhy}

    # C4 — the SAME site transfer done a second way, without the sequence alignment. See
    # `pocket5_structure_transfer`: this is the only arm that can tell a broken alignment from a ligand
    # that simply is not in this receptor's Pocket-5-equivalent site.
    ref_lbd, ref_why = nr4a3_lbd_reference(af2_reference_pdb, work)
    if ref_lbd is None:
        boxes["struct_transfer_apo"] = {"center": None, "why": ref_why}
        boxes["struct_transfer_holo"] = {"center": None, "why": ref_why}
    else:
        sc, sdet = pocket5_structure_transfer(ref_lbd, apo_rec)
        boxes["struct_transfer_apo"] = ({"center": sc, "detail": sdet} if sc
                                        else {"center": None, "why": sdet})
        sch, sdeth = pocket5_structure_transfer(ref_lbd, holo_rec)
        boxes["struct_transfer_holo"] = ({"center": sch, "detail": sdeth} if sch
                                         else {"center": None, "why": sdeth})
    R_["boxes"] = boxes
    size = tuple(float(R_["params"].get(k, 24)) for k in ("size_x", "size_y", "size_z"))

    # ==============================================================================================
    # Q-SITE — DOES THE SITE-SELECTION ROUTE PUT THE CRYSTALLOGRAPHIC LIGAND INSIDE ITS OWN BOX?
    # No docking, no scoring, no random seed: a deterministic geometric fact about site selection alone.
    # Apo-frame boxes are judged against the crystal ligand carried INTO the apo frame; holo-frame boxes
    # against the crystal ligand where it was solved.
    # ==============================================================================================
    ident_map = {a: h for a, h in apo_to_holo.items()}
    site_rows = {
        "pipeline_sequence_transfer_apo": site_answer(
            boxes["pipeline_apo"].get("center"), size, xtal_pts_apo,
            ((boxes["pipeline_apo"].get("detail") or {}).get("mapped_residues")), ident_map, native,
            "NR4A3 Pocket-5 carried across by the pipeline's own BLOSUM62 transfer (apo receptor)"),
        "pipeline_sequence_transfer_holo": site_answer(
            boxes["pipeline_holo"].get("center"), size, xtal_pts,
            ((boxes["pipeline_holo"].get("detail") or {}).get("mapped_residues")), None, native,
            "the same transfer onto the HOLO receptor — the site C1 self-docks through"),
        "pocket5_structure_transfer_apo": site_answer(
            boxes["struct_transfer_apo"].get("center"), size, xtal_pts_apo,
            ((boxes["struct_transfer_apo"].get("detail") or {}).get("mapped_residues")), ident_map, native,
            "NR4A3 Pocket-5 carried across by CE STRUCTURAL superposition (apo receptor) — C4"),
        "fpocket_top_pocket_apo": site_answer(
            (boxes.get("fpocket_top_apo") or {}).get("center"), size, xtal_pts_apo,
            (pockets[0]["residues"] if pockets else None), ident_map, native,
            "the highest-druggability fpocket pocket, no NR4A3 information used (apo receptor)"),
    }
    # ★ THE GEOMETRY'S OWN POSITIVE CONTROL. The oracle box is centred ON the ligand, so `SITE FOUND` with
    # essentially every heavy atom inside is the only answer `box_containment` can be allowed to give. A
    # different answer means the containment arithmetic or a frame is wrong, and every other row above is
    # then unreadable — so it is computed and reported rather than assumed.
    site_rows["C3_oracle_box_apo_geometry_selfcheck"] = site_answer(
        tuple(bm.apply_transform([centroid(xtal_pts)], Ri, ti)[0]), size, xtal_pts_apo, None, None, native,
        "oracle box, apo frame — a self-check on the containment arithmetic, never a result")
    R_["Q_SITE_does_site_selection_find_the_ligand"] = {
        "_endpoint": ("SITE FOUND iff the crystallographic ligand's centroid lies inside the axis-aligned "
                      "%s A box the route drew. ADDED 2026-08-02; it replaces no pre-registered endpoint "
                      "and cannot change the primary verdict." % "x".join(str(s) for s in size)),
        "routes": site_rows}

    # ★ SITE-ONLY STOPS HERE, BEFORE THE FIRST DOCK. Everything above is fetch, chain selection,
    # alignment, native contacts, induced fit and the three site transfers — all deterministic and all
    # free. Nothing below this line runs, so this path emits NO `arms` and NO `verdict` and cannot be
    # mistaken for a panel result.
    if site_only:
        R_["_site_only"] = True
        R_["questions"] = pair_questions(R_, cand)
        R_["_site_only_note"] = (
            "GEOMETRIC SITE ENDPOINT ONLY — no dock ran on this pair, so it carries no RMSD, no arms and "
            "no verdict, and it is NOT part of the pre-registered panel or any of its counts.")
        return R_

    def score_pose(mol_in_apo_frame, transform=True):
        m = _transform_mol(mol_in_apo_frame, Rm, tm) if transform else mol_in_apo_frame
        try:
            rms = round(float(rdMolAlign.CalcRMS(m, xtal)), 3)
        except Exception as e:                                # noqa: BLE001
            return {"rmsd_A": None, "why": "%s: %s" % (type(e).__name__, e)}
        got = residues_near(_read(holo_rec), _heavy_coords(m), cutoff)
        nat = set(native)
        return {"rmsd_A": rms,
                "fnat": round(len(got & nat) / len(nat), 3) if nat else None,
                "n_native_contacts": len(nat), "n_recovered": len(got & nat),
                "centroid_distance_A": round(math.dist(centroid(_heavy_coords(m)), centroid(xtal_pts)), 3),
                "verdict": ("RECOVERED" if rms <= RECOVER_RMSD_A else
                            "PARTIAL" if rms <= PARTIAL_RMSD_A else "NOT RECOVERED")}

    # 8) PRIMARY — blind cross-dock from the apo receptor, pipeline box, pipeline settings
    arms = {}
    if boxes["pipeline_apo"].get("center"):
        _s, out_sdf = dock(apo_rec, boxes["pipeline_apo"]["center"], sdf, "apo_pipeline", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["PRIMARY_blind_apo_pipeline_box"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    else:
        arms["PRIMARY_blind_apo_pipeline_box"] = {"rmsd_A": None,
                                                  "why": boxes["pipeline_apo"].get("why")}
    # 9) secondary blind arm — fully agnostic site choice
    if not out_of_time("blind_apo_fpocket_top_box") and boxes.get("fpocket_top_apo", {}).get("center"):
        _s, out_sdf = dock(apo_rec, boxes["fpocket_top_apo"]["center"], sdf, "apo_fpocket", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["blind_apo_fpocket_top_box"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    # 10) C3 ORACLE — decomposition only, never the headline
    #     centre the box on the crystallographic ligand, still docking into the APO receptor.
    oracle_center_holo = centroid(xtal_pts)
    oracle_center_apo = None
    try:
        oracle_center_apo = bm.apply_transform([oracle_center_holo], Ri, ti)[0]
        _s, out_sdf = dock(apo_rec, oracle_center_apo, sdf, "apo_oracle", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C3_oracle_box_apo"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    except Exception as e:                                    # noqa: BLE001
        arms["C3_oracle_box_apo"] = {"rmsd_A": None, "why": "oracle box failed: %s" % e}
    # 11) C1 SELF-DOCK into the holo receptor (same frame as the crystal — no transform).
    #     ★ ONE CONTROL PER BLIND ARM. A single C1 on the pipeline box cannot interpret the fpocket arm:
    #     if the pipeline's transferred site is simply not where this ligand binds, its C1 fails for a
    #     reason that says nothing about whether the DOCKING works. So each blind arm gets a self-dock
    #     through its own site-selection route, and each is then judged against its own control.
    if boxes["pipeline_holo"].get("center"):
        _s, out_sdf = dock(holo_rec, boxes["pipeline_holo"]["center"], sdf, "holo_self", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C1_self_dock_holo"] = (score_pose(mol, transform=False) if mol
                                     else {"rmsd_A": None, "why": why})
    else:
        arms["C1_self_dock_holo"] = {"rmsd_A": None, "why": boxes["pipeline_holo"].get("why")}
    hp, hwhy = (None, "pair budget spent") if out_of_time("C1_self_dock_holo_fpocket") \
        else fpocket_boxes(holo_rec)
    if hp:
        import nr4a3_warhead as _wh
        try:
            hc, _n = _wh.pocket_box(holo_rec, hp[0]["residues"])
            _s, out_sdf = dock(holo_rec, hc, sdf, "holo_self_fpocket", work)
            mol, why = _top_pose(out_sdf, comp)
            arms["C1_self_dock_holo_fpocket"] = (score_pose(mol, transform=False) if mol
                                                 else {"rmsd_A": None, "why": why})
            boxes["fpocket_top_holo"] = {"center": hc, "druggability": hp[0].get("druggability")}
        except Exception as e:                                # noqa: BLE001
            arms["C1_self_dock_holo_fpocket"] = {"rmsd_A": None, "why": "fpocket self-dock failed: %s" % e}
    else:
        arms["C1_self_dock_holo_fpocket"] = {"rmsd_A": None, "why": hwhy}
    # ★ C1c — THE MAXIMALLY-FAVOURABLE PROTOCOL CONTROL, and the one that ends the argument. Same receptor
    # the ligand was solved in, AND a box centred exactly on the crystallographic ligand. Nothing about site
    # selection is left to fail. If this clears 2 A the earlier misses are about WHERE the pipeline looks;
    # if it does not, the search/scoring settings themselves cannot reproduce a known pose and every arm
    # above was measuring that. Added 2026-08-02 after the first full panel; it can only make the pipeline
    # look BETTER than the pre-registered primary, so it cannot be a way of tuning toward a pass.
    if not out_of_time("C1c_self_dock_holo_oracle_box"):
        _s, out_sdf = dock(holo_rec, oracle_center_holo, sdf, "holo_self_oracle", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C1c_self_dock_holo_oracle_box"] = (score_pose(mol, transform=False) if mol
                                                 else {"rmsd_A": None, "why": why})
    # C4 — the structural-transfer blind arm and its own self-dock control, so the sequence-transfer and
    # structure-transfer routes are graded the same way as each other and as every other blind arm.
    if not out_of_time("blind_apo_struct_transfer_box") and boxes["struct_transfer_apo"].get("center"):
        _s, out_sdf = dock(apo_rec, boxes["struct_transfer_apo"]["center"], sdf, "apo_struct", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C4_blind_apo_struct_transfer_box"] = (score_pose(mol) if mol
                                                    else {"rmsd_A": None, "why": why})
    else:
        arms["C4_blind_apo_struct_transfer_box"] = {
            "rmsd_A": None, "why": boxes["struct_transfer_apo"].get("why") or "pair budget spent"}
    if not out_of_time("C4_self_dock_holo_struct_transfer") and boxes["struct_transfer_holo"].get("center"):
        _s, out_sdf = dock(holo_rec, boxes["struct_transfer_holo"]["center"], sdf, "holo_struct", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C4_self_dock_holo_struct_transfer"] = (score_pose(mol, transform=False) if mol
                                                     else {"rmsd_A": None, "why": why})
    else:
        arms["C4_self_dock_holo_struct_transfer"] = {
            "rmsd_A": None, "why": boxes["struct_transfer_holo"].get("why") or "pair budget spent"}
    R_["arms"] = arms

    # 11a) ★★ C6b — IS THIS PAIR'S GRADEABILITY A COIN FLIP? Runs on EVERY pair, ceiling arm only.
    if ceiling_replicates and not out_of_time("C6b_ceiling_replicates"):
        vals, rows = [], []
        for sd in REPLICATE_SEEDS[:ceiling_replicates]:
            sdf_out, why = dock_seeded(holo_rec, oracle_center_holo, sdf, "ceil_seed%d" % sd, work, sd)
            mol, why2 = _top_pose(sdf_out, comp) if sdf_out else (None, why)
            sc = score_pose(mol, transform=False) if mol else {"rmsd_A": None, "why": why2}
            rows.append({"seed": sd, "rmsd_A": sc.get("rmsd_A"),
                         "gradeable": (sc.get("rmsd_A") is not None
                                       and sc["rmsd_A"] <= RECOVER_RMSD_A)})
            if sc.get("rmsd_A") is not None:
                vals.append(sc["rmsd_A"])
        n_pass = sum(1 for r in rows if r["gradeable"])
        unseeded_gradeable = (arms.get("C1c_self_dock_holo_oracle_box") or {}).get("rmsd_A")
        unseeded_gradeable = (unseeded_gradeable is not None
                              and unseeded_gradeable <= RECOVER_RMSD_A)
        R_["C6b_ceiling_replicates"] = {
            "_asks": ("does this pair's GRADEABILITY survive re-seeding? The ceiling arm decides whether "
                      "Q-DOCKING may grade the pair at all, so an unstable ceiling moves the headline "
                      "count's DENOMINATOR, not only its digits."),
            "_criterion_A": RECOVER_RMSD_A,
            "seeds": list(REPLICATE_SEEDS[:ceiling_replicates]),
            "replicates": rows, "n_seeds": len(rows), "n_seeds_gradeable": n_pass,
            "min_A": min(vals) if vals else None, "max_A": max(vals) if vals else None,
            "unseeded_gradeable": unseeded_gradeable,
            "gradeability_stable": bool(rows) and n_pass in (0, len(rows)),
            "_reads": ("gradeability is the same on every seed, so this pair's inclusion in (or exclusion "
                       "from) the Q-DOCKING count is not an artefact of the search"
                       if rows and n_pass in (0, len(rows)) else
                       "⛔ THIS PAIR IS GRADEABLE ON %d OF %d SEEDS — its inclusion in the Q-DOCKING "
                       "count is a coin flip, and `n_gradeable` must be reported with that range, never "
                       "as a single integer" % (n_pass, len(rows)) if rows else
                       "UNRUN — no ceiling replicate returned a scorable pose")}

    # 11b) ★★ C6 — SEED REPLICATES. Added 2026-08-03. Reporting only; `verdict()` never reads it.
    if replicates:
        R_["C6_seed_replicates"] = seed_replicates(
            replicates, work, sdf, comp, score_pose, arms,
            {"blind_apo_fpocket_top_box":
                (apo_rec, (boxes.get("fpocket_top_apo") or {}).get("center"), True),
             "C3_oracle_box_apo":
                (apo_rec, oracle_center_apo, True),
             "C1c_self_dock_holo_oracle_box":
                (holo_rec, oracle_center_holo, False)},
            out_of_time)

    # 12) C2 power
    R_["C2_random_in_box_null"] = random_in_box_null(xtal, oracle_center_holo, size)

    # 13) C5 — what the DEPOSIT declares, read from the files already on disk. Never a filter.
    R_["engineered_construct"]["seqadv_holo"] = seqadv_mutations(holo_txt, holo_chain)
    R_["engineered_construct"]["seqadv_apo"] = seqadv_mutations(apo_txt)
    eng_holo = [m for m in R_["engineered_construct"]["seqadv_holo"]
                if "ENGINEERED" in (m.get("reason") or "").upper()]
    in_site = [m for m in eng_holo if m["resseq"] in set(native)]
    R_["engineered_construct"]["engineered_residues_holo"] = eng_holo
    R_["engineered_construct"]["engineered_residues_in_native_ligand_site"] = in_site
    # ⛔ THIS IS THE QUESTION THE TITLE FLAG COULD NOT ANSWER. "Declared in title" says a mutant was used;
    # it does not say whether the mutation touches the pocket being benchmarked. A tryptophan that is one
    # of the ligand's own contacts means the site the benchmark grades exists in a protein this program is
    # not targeting, and no site transfer from wild-type NR4A3 can be scored against it.
    R_["engineered_construct"]["_reads"] = (
        "%d engineered substitution(s) declared in the HOLO deposit, of which %d is/are among the ligand's "
        "own contact residues — %s"
        % (len(eng_holo), len(in_site),
           ("the benchmarked pocket is shaped by the engineered residue(s) %s, so it is not the wild-type "
            "site any transfer is aiming at" % ", ".join("%s%d->%s" % (m["db_residue"], m["resseq"],
                                                                       m["deposit_residue"]) for m in in_site))
           if in_site else
           ("the engineered residue(s) are outside the ligand's contact shell, so the benchmarked pocket "
            "is not one the mutation built" if eng_holo else
            # ⚠ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). "No engineered mutation" and
            # "this file carries no SEQADV block at all" are different facts with different weights, and a
            # single sentence covering both would make an unread file look like a clean wild-type deposit.
            "SEQADV records ARE present (%d) and none of them declares an engineered mutation"
            % len(R_["engineered_construct"]["seqadv_holo"])
            if R_["engineered_construct"]["seqadv_holo"] else
            "⚠ THE HOLO DEPOSIT CARRIES NO SEQADV RECORDS AT ALL — the substitutions are UNREAD here, not "
            "absent. The title flag above is the only evidence for this pair.")))
    # ★★ C5b — AND THE APO SIDE, ADDED 2026-08-03. The block above graded the HOLO construct only, which
    # silently assumes the pair is two STATES OF ONE CONSTRUCT. On the headline pair it is not: 4RZF is
    # "NUR77 LBD, S441W mutant" and 4REF is "TR3 LBD_L449W" — two DIFFERENT engineered tryptophan mutants
    # of NR4A1. A cross-dock between them is therefore a cross-CONSTRUCT dock as well as an apo->holo one,
    # and the apo->holo Ca RMSD reported as "induced fit" contains whatever the substitution did too.
    # ⛔ THE POINT IS NOT TO FILTER THE PAIR. It is that a reader must not be able to take the induced-fit
    # number as pure conformational change when the two deposits are not the same molecule.
    eng_apo = [m for m in R_["engineered_construct"]["seqadv_apo"]
               if "ENGINEERED" in (m.get("reason") or "").upper()]
    R_["engineered_construct"]["engineered_residues_apo"] = eng_apo
    # apo numbering -> holo numbering through the same map every other apo-frame quantity uses, so
    # "is it in the ligand's contact shell" is asked in ONE frame and never by comparing raw resseqs.
    apo_in_site = sorted({apo_to_holo[m["resseq"]] for m in eng_apo
                          if m["resseq"] in apo_to_holo and apo_to_holo[m["resseq"]] in set(native)})
    R_["engineered_construct"]["engineered_apo_residues_in_native_ligand_site"] = apo_in_site
    _key = lambda ms: sorted((m["resseq"], m.get("db_residue"), m.get("deposit_residue")) for m in ms)
    same = _key(eng_apo) == _key(eng_holo)
    R_["engineered_construct"]["apo_and_holo_are_the_same_construct"] = same
    R_["engineered_construct"]["_construct_reads"] = (
        "the apo and holo deposits declare the SAME engineered substitution set, so this is an apo/holo "
        "pair of ONE construct and the apo->holo Ca RMSD is conformational change" if same else
        "⚠ THE APO AND HOLO DEPOSITS ARE DIFFERENT CONSTRUCTS — apo declares %s, holo declares %s. This "
        "cross-dock is cross-CONSTRUCT as well as apo->holo, so the induced-fit number contains the "
        "substitution's effect too and must not be quoted as pure conformational change. %s"
        % (", ".join("%s%d->%s" % (m.get("db_residue"), m["resseq"], m.get("deposit_residue"))
                     for m in eng_apo) or "none",
           ", ".join("%s%d->%s" % (m.get("db_residue"), m["resseq"], m.get("deposit_residue"))
                     for m in eng_holo) or "none",
           ("⛔ AND %d of the apo substitutions map INTO the ligand's own contact shell (holo residues "
            "%s), so the apo pocket the blind arm docks into is one the mutation helped build."
            % (len(apo_in_site), apo_in_site)) if apo_in_site else
           "Neither apo substitution maps into the ligand's contact shell, so the benchmarked pocket is "
           "not one either mutation built."))

    # 13b) THE SECOND-METHOD HOOK. OFF by default (SECOND_METHOD_HOOK is None); `verdict()` never reads
    #      what it returns. See the constant's own comment for the invariants this must keep.
    if SECOND_METHOD_HOOK is not None:
        try:
            R_["second_method"] = SECOND_METHOD_HOOK({
                "cand": cand, "work": work, "sdf": sdf, "comp": comp,
                "apo_rec": apo_rec, "holo_rec": holo_rec,
                "boxes": boxes, "size": size,
                "oracle_center_apo": oracle_center_apo, "oracle_center_holo": oracle_center_holo,
                "score_pose": score_pose, "native": native, "xtal": xtal, "xtal_pts": xtal_pts,
                "arms": arms, "out_of_time": out_of_time, "contact_A": cutoff,
                "induced_fit": R_.get("induced_fit"),
            })
        except Exception as e:                                # noqa: BLE001 — a refusal, never a crash
            R_["second_method"] = {"_error": "%s: %s" % (type(e).__name__, e)}

    # 14) THE TWO QUESTIONS, SEPARATED. Added 2026-08-02. Neither changes `verdict()`.
    R_["questions"] = pair_questions(R_, cand)
    R_["verdict"] = verdict(R_)
    return R_


def _band(rms):
    if rms is None:
        return None
    return ("RECOVERED" if rms <= RECOVER_RMSD_A else
            "PARTIAL" if rms <= PARTIAL_RMSD_A else "NOT RECOVERED")


def pair_questions(res, cand):
    """The site question and the docking question, each answered on its own arm and its own control.

    ⛔ THE POINT OF THIS FUNCTION IS THAT NEITHER ANSWER CAN BORROW THE OTHER'S EVIDENCE. The first panel
    reported one number — a blind RMSD through the pipeline's box — that moved if EITHER the site or the
    docking was wrong, so a 19 A miss was equally consistent with a broken search and with a box in the
    wrong half of the protein. Here the docking question is only ever asked with the site handed over, and
    the site question is only ever answered from geometry with no docking in it at all."""
    import nr4a3_warhead as wh
    arms = res.get("arms") or {}
    sites = (res.get("Q_SITE_does_site_selection_find_the_ligand") or {}).get("routes") or {}
    oracle = arms.get("C3_oracle_box_apo") or {}
    ceiling = arms.get("C1c_self_dock_holo_oracle_box") or {}
    o_rms, c_rms = oracle.get("rmsd_A"), ceiling.get("rmsd_A")
    ceiling_ok = c_rms is not None and c_rms <= RECOVER_RMSD_A

    docking = {
        "_asks": "GIVEN THE CORRECT SITE, does blind apo->holo docking reproduce the crystallographic pose?",
        "arm": "C3_oracle_box_apo — apo receptor, box centred on the crystallographic ligand",
        "control": "C1c_self_dock_holo_oracle_box — same box, the receptor the ligand was solved in",
        "apo_rmsd_A": o_rms, "apo_fnat": oracle.get("fnat"), "apo_band": _band(o_rms),
        "control_rmsd_A": c_rms, "control_band": _band(c_rms), "control_passed": ceiling_ok,
        "answer": (_band(o_rms) if ceiling_ok else
                   ("INCONCLUSIVE — the protocol ceiling itself missed (%s A), so this pair cannot grade "
                    "the docking" % c_rms) if c_rms is not None else
                   "INCONCLUSIVE — the protocol ceiling produced no pose"),
        "_thresholds": {"recovered_A": RECOVER_RMSD_A, "partial_A": PARTIAL_RMSD_A},
    }

    # ⛔ THE REGIME GATE — and it is READ FROM THE PIPELINE, NOT TYPED HERE. `nr4a3_warhead.PARALOGUES` is
    # the complete set of proteins the pipeline ever carries Pocket-5 onto; NR4A3's own accession is added
    # because the pipeline also transfers onto 8XTT. A benchmark receptor outside that set is being asked a
    # question the pipeline never asks, and its site arm is NOT evidence about the pipeline's site step.
    in_regime_accessions = set(wh.PARALOGUES.values()) | {"Q92570"}
    acc = cand.get("accession")
    seq_row = sites.get("pipeline_sequence_transfer_apo") or {}
    str_row = sites.get("pocket5_structure_transfer_apo") or {}
    fp_row = sites.get("fpocket_top_pocket_apo") or {}
    allosteric = bool((res.get("declared_allosteric") or {}).get("declared_in_holo_title"))
    eng_in_site = res.get("engineered_construct", {}).get("engineered_residues_in_native_ligand_site") or []
    ident = ((res.get("boxes", {}).get("pipeline_apo") or {}).get("detail") or {}).get(
        "nr4a3_aligned_identity")

    disqualifiers = []
    if acc not in in_regime_accessions:
        disqualifiers.append(
            "OUT OF THE PIPELINE'S REGIME: %s is not one of the proteins the pipeline transfers Pocket-5 "
            "onto (nr4a3_warhead.PARALOGUES = %s, plus NR4A3's own 8XTT). The transfer ran here at %s "
            "aligned identity. Finding that an NR4A3 cryptic pocket does not land on this receptor's "
            "ligand site is close to expected and is NOT evidence that site selection is broken for NR4A3."
            % (acc, sorted(wh.PARALOGUES.values()), ident))
    if allosteric:
        disqualifiers.append(
            "THE DEPOSITOR DECLARES THE LIGAND ALLOSTERIC (%s). An orthosteric site transfer cannot be "
            "graded against a ligand in a declared allosteric pocket."
            % "; ".join((res.get("declared_allosteric") or {}).get("evidence") or []))
    if eng_in_site:
        disqualifiers.append(
            "THE BENCHMARKED POCKET IS SHAPED BY AN ENGINEERED RESIDUE (%s), so it is not the wild-type "
            "site a transfer from wild-type NR4A3 is aiming at."
            % ", ".join("%s%d->%s" % (m["db_residue"], m["resseq"], m["deposit_residue"])
                        for m in eng_in_site))

    site = {
        "_asks": "Does the site-selection route put the crystallographic ligand INSIDE the box it draws?",
        "_endpoint": "geometric containment — no docking, no scoring, no seed",
        "pipeline_sequence_transfer": {k: seq_row.get(k) for k in
                                       ("answer", "ligand_centroid_in_box",
                                        "frac_ligand_heavy_atoms_in_box",
                                        "box_center_to_ligand_centroid_A",
                                        "native_contact_recall_of_box_residues")},
        "pocket5_structure_transfer": {k: str_row.get(k) for k in
                                       ("answer", "ligand_centroid_in_box",
                                        "frac_ligand_heavy_atoms_in_box",
                                        "box_center_to_ligand_centroid_A",
                                        "native_contact_recall_of_box_residues")},
        "fpocket_top_pocket": {k: fp_row.get(k) for k in
                               ("answer", "ligand_centroid_in_box", "frac_ligand_heavy_atoms_in_box",
                                "box_center_to_ligand_centroid_A",
                                "native_contact_recall_of_box_residues")},
        "nr4a3_aligned_identity": ident,
        "interpretable_as_evidence_about_the_pipeline": not disqualifiers,
        "disqualifiers": disqualifiers,
    }
    # ★ DO THE TWO TRANSFERS EVEN AGREE WITH EACH OTHER? A single number, and the cheapest possible check
    # on the pipeline's alignment: if sequence and structure put Pocket-5 in the same place, the alignment
    # is not what is failing, whatever the ligand turns out to be near.
    bx = res.get("boxes") or {}
    seq_c = (bx.get("pipeline_apo") or {}).get("center")
    str_c = (bx.get("struct_transfer_apo") or {}).get("center")
    site["sequence_vs_structure_transfer_center_distance_A"] = (
        round(math.dist(seq_c, str_c), 3) if seq_c and str_c else None)
    site["structure_transfer_detail"] = {
        k: ((bx.get("struct_transfer_apo") or {}).get("detail") or {}).get(k)
        for k in ("ce_rms_A", "n_pocket5_transferred", "n_pocket5_source", "n_unique_receptor_residues")}
    # ⛔ THE CONFOUND VERDICT. Two transfers of the SAME site by two independent methods; only their
    # agreement or disagreement can say whether a miss is the alignment or the benchmark.
    s_ans, t_ans = seq_row.get("answer"), str_row.get("answer")
    if s_ans == "SITE FOUND" and t_ans == "SITE FOUND":
        site["confound_reading"] = ("both transfers land on the ligand — the site step worked and any "
                                    "miss on this pair is the docking")
    elif s_ans == "SITE MISSED" and t_ans == "SITE FOUND":
        site["confound_reading"] = ("the STRUCTURAL transfer finds the site and the pipeline's SEQUENCE "
                                    "transfer does not — this is a real defect in the pipeline's "
                                    "alignment step, not a property of the benchmark")
    elif s_ans == "SITE FOUND" and t_ans == "SITE MISSED":
        site["confound_reading"] = ("the pipeline's sequence transfer finds the site and the structural "
                                    "transfer does not — the fold superposition, not the pipeline, is "
                                    "what failed here")
    elif s_ans == "SITE MISSED" and t_ans == "SITE MISSED":
        site["confound_reading"] = ("BOTH an independent structural transfer and the pipeline's sequence "
                                    "transfer put NR4A3's Pocket-5 somewhere this ligand is not. The "
                                    "crystallographic answer is not in this receptor's Pocket-5-equivalent "
                                    "site, so 'the pipeline missed the site' is the benchmark's design "
                                    "and not a demonstrated defect")
    else:
        site["confound_reading"] = ("one or both transfers are UNREAD (%s / %s) — no confound reading"
                                    % (s_ans, t_ans))
    return {"Q_DOCKING_given_the_correct_site": docking,
            "Q_SITE_does_site_selection_find_the_site": site}


def verdict(res):
    """The pre-registered decision, applied mechanically to what was measured."""
    arms = res.get("arms") or {}
    primary = arms.get("PRIMARY_blind_apo_pipeline_box") or {}
    c1 = arms.get("C1_self_dock_holo") or {}
    null = res.get("C2_random_in_box_null") or {}
    p_rms, c1_rms = primary.get("rmsd_A"), c1.get("rmsd_A")
    p_null = null.get("p_within_criterion")

    if p_rms is None:
        return {"outcome": "INCONCLUSIVE", "reason": "the primary arm produced no pose",
                "detail": primary.get("why")}
    if c1_rms is None:
        return {"outcome": "INCONCLUSIVE",
                "reason": "C1 self-dock produced no pose, so a primary failure cannot be attributed",
                "detail": c1.get("why"), "primary_rmsd_A": p_rms}
    if c1_rms > RECOVER_RMSD_A:
        fp = arms.get("blind_apo_fpocket_top_box") or {}
        fp_c1 = arms.get("C1_self_dock_holo_fpocket") or {}
        return {"outcome": "INCONCLUSIVE",
                "blind_arms_each_against_its_own_control": {
                    "pipeline_site_transfer": {
                        "blind_apo_rmsd_A": p_rms, "own_control_rmsd_A": c1_rms,
                        "control_passed": False,
                        "_reads": "the protocol cannot recover this ligand even from the receptor it was "
                                  "solved in, THROUGH THIS SITE — so this arm is measuring the site, not "
                                  "the docking"},
                    "fpocket_top_pocket": {
                        "blind_apo_rmsd_A": fp.get("rmsd_A"), "own_control_rmsd_A": fp_c1.get("rmsd_A"),
                        "control_passed": (fp_c1.get("rmsd_A") is not None
                                           and fp_c1["rmsd_A"] <= RECOVER_RMSD_A),
                        "blind_apo_fnat": fp.get("fnat")},
                    "C1c_protocol_ceiling": {
                        "self_dock_holo_oracle_box_rmsd_A":
                            (arms.get("C1c_self_dock_holo_oracle_box") or {}).get("rmsd_A"),
                        "_reads": "same receptor the ligand was solved in, box centred on the ligand "
                                  "itself. This is the best this docking protocol can possibly do on this "
                                  "system; a miss here is the search and scoring, not the site."}},
                "reason": "C1 FAILED: the protocol could not recover the pose even from the HOLO receptor "
                          "(%.2f A > %.2f A), so the primary result measures the docking protocol, not the "
                          "apo->holo induced-fit gap. Pre-registered: this outcome is INCONCLUSIVE, not a "
                          "failure of the apo pipeline." % (c1_rms, RECOVER_RMSD_A),
                "primary_rmsd_A": p_rms, "c1_rmsd_A": c1_rms}
    if p_null is not None and p_null > NULL_POWER_MAX:
        return {"outcome": "INCONCLUSIVE",
                "reason": "C2 FAILED: a random placement in the same box clears %.2f A with probability "
                          "%.3f > %.3f, so the criterion has no power here."
                          % (RECOVER_RMSD_A, p_null, NULL_POWER_MAX),
                "primary_rmsd_A": p_rms}

    band = primary.get("verdict")
    # ★ EACH BLIND ARM AGAINST ITS OWN CONTROL. The primary endpoint is unchanged and stays the pipeline
    # box — moving it after seeing a number would be the tuning this module forbids. But a single verdict
    # line cannot say what the run actually found when one arm's SITE is wrong and another's is right, so
    # every blind arm is also reported beside the self-dock that goes through the same site-selection route.
    fp = arms.get("blind_apo_fpocket_top_box") or {}
    fp_c1 = arms.get("C1_self_dock_holo_fpocket") or {}
    out_arms = {
        "pipeline_site_transfer": {
            "blind_apo_rmsd_A": p_rms, "own_control_rmsd_A": c1_rms,
            "control_passed": c1_rms is not None and c1_rms <= RECOVER_RMSD_A,
            "_site": "NR4A3 Pocket-5 carried across by the pipeline's own paralogue transfer"},
        "fpocket_top_pocket": {
            "blind_apo_rmsd_A": fp.get("rmsd_A"), "own_control_rmsd_A": fp_c1.get("rmsd_A"),
            "control_passed": (fp_c1.get("rmsd_A") is not None
                               and fp_c1["rmsd_A"] <= RECOVER_RMSD_A),
            "blind_apo_fnat": fp.get("fnat"),
            "_site": "the highest-druggability fpocket pocket on the receptor, no NR4A3 information used"},
        "C1c_protocol_ceiling": {
            "self_dock_holo_oracle_box_rmsd_A":
                (arms.get("C1c_self_dock_holo_oracle_box") or {}).get("rmsd_A"),
            "_reads": "same receptor the ligand was solved in, box centred on the ligand itself — the best "
                      "this protocol can do on this system"},
    }
    out = {"outcome": "RECOVERED" if band == "RECOVERED" else "NOT RECOVERED",
           "blind_arms_each_against_its_own_control": out_arms,
           "band": band, "primary_rmsd_A": p_rms, "primary_fnat": primary.get("fnat"),
           "c1_self_dock_rmsd_A": c1_rms, "null_p_within_criterion": p_null,
           "oracle_rmsd_A": (arms.get("C3_oracle_box_apo") or {}).get("rmsd_A"),
           "fpocket_top_rmsd_A": (arms.get("blind_apo_fpocket_top_box") or {}).get("rmsd_A")}
    if out["outcome"] == "RECOVERED":
        out["sentence"] = (
            "KNOWN-ANSWER RECOVERED: docking into the APO receptor with the pipeline's own site transfer "
            "and smina settings put the ligand %.2f A from the crystallographic pose (criterion <= %.2f A), "
            "recovering %s of the native contacts. The protocol control passed (%.2f A) and a random "
            "placement in the same box clears the criterion with probability %s. This is ONE case: it "
            "removes a specific reason to disbelieve the NR4A3 pose and makes no claim that it is correct."
            % (p_rms, RECOVER_RMSD_A, primary.get("fnat"), c1_rms, p_null))
    else:
        # name which stage failed, using the decomposition — never leave it as a bare number
        oracle = out["oracle_rmsd_A"]
        if oracle is not None and oracle <= RECOVER_RMSD_A:
            stage = ("SITE TRANSFER. Handed the correct site (C3 oracle box) the same docking recovers the "
                     "pose at %.2f A, so what failed is the step that decides WHERE to dock — the same "
                     "sequence transfer of NR4A3's Pocket-5 that boxes 8XTT and the paralogues." % oracle)
        else:
            stage = ("POSE PLACEMENT. Even handed the correct site (C3 oracle box: %s A) the docking does "
                     "not reproduce the crystallographic pose, so the failure is in the search/scoring, "
                     "not in site selection." % oracle)
        out["failing_stage"] = stage
        out["sentence"] = (
            "KNOWN-ANSWER NOT RECOVERED: the pipeline placed the ligand %.2f A from the crystallographic "
            "pose (criterion <= %.2f A; %s band), recovering %s of the native contacts, while the protocol "
            "control passed at %.2f A and the criterion had power (random p=%s). Failing stage: %s "
            "This does not prove the NR4A3 denovo_401 pose wrong. It removes the presumption that it is "
            "right: the pipeline that produced it has now been asked to recover a pose that is known, in a "
            "comparable apo/induced-fit regime, and did not."
            % (p_rms, RECOVER_RMSD_A, band, primary.get("fnat"), c1_rms, p_null, stage))
    return out


# ==================================================================================================
# MODES
# ==================================================================================================

def mode_source():
    """Real RCSB queries -> the full considered set, apo/holo classified, nothing assumed."""
    doc = {"_mode": "source", "_query": {"search": RCSB_SEARCH, "graphql": RCSB_GRAPHQL},
           "accessions_declared": [{"accession": a, "protein": n, "why": w} for a, n, w in NR_ACCESSIONS],
           "selection_rules": SELECTION_RULES, "refusals": [], "by_accession": {}}
    for acc, name, why in NR_ACCESSIONS:
        ids, err = entries_for_accession(acc)
        if ids is None:
            doc["refusals"].append({"accession": acc, "stage": "search", "evidence": err})
            continue
        details, derr = entry_details(ids)
        if derr:
            doc["refusals"].append({"accession": acc, "stage": "entry_details", "evidence": derr})
        entries = [classify_entry(e, acc) for e in details]
        doc["by_accession"][acc] = {
            "name": name, "why_considered": why, "n_entries": len(ids),
            "n_classified": len(entries),
            "n_apo": sum(1 for e in entries if e["apo"]),
            "n_holo": sum(1 for e in entries if e["ligands"]),
            "entries": entries,
        }
    return doc


def mode_select(src):
    ranked = pair_candidates(src.get("by_accession") or {})
    considered = [{"rank": i + 1, "score": list(s), **{k: v for k, v in c.items() if k != "ligand"},
                   "ligand": c["ligand"]} for i, (s, c) in enumerate(ranked[:40])]
    return {"n_pairs_found": len(ranked),
            # ⚠ THE PANEL POOL IS BUILT FROM THE FULL RANKED LIST, NOT FROM `considered_top`. That field is
            # a 40-row excerpt kept for the record, and building the panel from it silently capped the run
            # at four candidates — every one of them NR4A subfamily — so the panel could never reach a
            # nuclear receptor with a canonical orthosteric ligand complex. Measured on CI run 30762378689.
            "panel_pool": _dedup_pairs([c for _s, c in ranked]),
            # ★ THE COMPLETE IN-REGIME SLICE, kept whole. `considered_top` is a 40-row excerpt and
            # `panel_pool` is capped at MAX_PER_PROTEIN, so neither can tell you how many pairs exist on
            # the only two proteins the pipeline actually transfers Pocket-5 onto. That count IS the
            # answer to "how much in-regime evidence about the site step could ever exist", so it is
            # recorded rather than re-derived. Bounded by construction: the regime is 3 accessions.
            "_all_ranked_in_regime": [c for _s, c in ranked
                                      if c.get("accession") in _REGIME_ACCESSIONS()],
            "considered_top": considered,
            "chosen": ranked[0][1] if ranked else None,
            "selection_rules": SELECTION_RULES,
            "_finding_if_empty": ("No nuclear-receptor LBD in the declared list has BOTH an apo deposit "
                                  "and a drug-like holo deposit that pass the hard rules. That is the "
                                  "finding — no substitute benchmark is used.")}


def main():
    mode = os.environ.get("MODE", "run").strip().lower()
    # MODE=report re-renders the written finding from the artifact ALREADY ON DISK. No network, no smina,
    # no docking — so the prose can be regenerated without re-running the experiment, which is the only
    # way a summary and its artifact can be guaranteed to agree.
    if mode == "report":
        with open(OUT) as fh:
            _write(OUT_MD, render_markdown(json.load(fh)))
        print("[apo-pose-recovery] wrote %s from the committed artifact" % OUT_MD)
        return
    # The AF2 reference is only needed to TRANSFER NR4A3's Pocket-5 onto the benchmark receptor. The repo
    # already carries the exact model the pipeline used, so the default reads that rather than re-fetching
    # a model that might have been re-predicted since.
    repo_af2 = os.path.join(HERE, "..", "..", "results", "nr4a3-metad-r2", "ckpt", "AF-Q92570.pdb")
    af2 = os.environ.get("AF2_REFERENCE_PDB") or (os.path.abspath(repo_af2)
                                                  if os.path.exists(repo_af2)
                                                  else os.path.join(WORK, "AF-Q92570.pdb"))
    os.makedirs(WORK, exist_ok=True)
    doc = {"_module": "apo_pose_recovery", "_mode": mode,
           "_preregistered_criterion": {
               "primary": "symmetry-corrected heavy-atom RMSD of the top smina pose from the APO receptor "
                          "to the crystallographic ligand, after site-Ca superposition",
               "recovered_A": RECOVER_RMSD_A, "partial_A": PARTIAL_RMSD_A,
               "secondary_fnat": FNAT_SUCCESS,
               "controls": ["C1 self-dock into holo (failure => INCONCLUSIVE)",
                            "C2 random-in-box null (no power => INCONCLUSIVE)",
                            "C3 oracle box (decomposition only, never the headline)"],
               "_frozen": "fixed in the module docstring before the first run; changes go to an appendix"},
           "selection_rules": SELECTION_RULES}
    src = mode_source()
    doc["sourcing"] = {k: v for k, v in src.items() if k != "by_accession"}
    doc["sourcing"]["census"] = {
        a: {"name": r["name"], "n_entries": r["n_entries"], "n_apo": r["n_apo"], "n_holo": r["n_holo"]}
        for a, r in (src.get("by_accession") or {}).items()}
    if mode == "source":
        doc["by_accession"] = src.get("by_accession")
        _emit(doc)
        return
    sel = mode_select(src)
    doc["selection"] = sel
    if mode == "select" or not sel["chosen"]:
        if not sel["chosen"]:
            doc["verdict"] = {"outcome": "NO SUITABLE BENCHMARK",
                              "reason": sel["_finding_if_empty"]}
        _emit(doc)
        return
    if not os.path.exists(af2):
        try:
            import nr4a3_8xtt_redock as rd
            rd._fetch_af2(af2)
        except Exception as e:                                # noqa: BLE001
            doc["verdict"] = {"outcome": "INCONCLUSIVE",
                              "reason": "the AF-Q92570 reference needed for the pipeline's own site "
                                        "transfer could not be fetched: %s" % e}
            _emit(doc)
            return
    # ★★ MODE=site — THE IN-REGIME SITE SUPPLEMENT, ADDED 2026-08-03. It runs the GEOMETRIC site question
    # over every pair on a protein the pipeline actually transfers Pocket-5 onto, and it runs NO DOCK, so
    # it is fast, deterministic and free. It writes its own artifact key and is never summed into the
    # pre-registered panel. Reason it exists: the panel offered only TWO in-regime pairs, both against the
    # same apo structure (4RZF) and both on NR4A1, while BOTH NR4A2 pairs — NR4A3's closest paralogue —
    # were removed by R2b, a rule about docking that has no bearing on a geometric containment test.
    if mode == "site":
        rows, cands = [], in_regime_pairs(sel)
        doc["_in_regime_candidates"] = cands
        for pair in cands:
            t0 = time.time()
            r = run_benchmark(pair, os.path.join(WORK, "site_%s_%s" % (pair["apo"], pair["holo"])),
                              af2, site_only=True)
            r["elapsed_s"] = round(time.time() - t0, 1)
            print("[apo-pose-recovery/site] %s -> %s (%s): seq=%s struct=%s fpocket=%s in %.0fs"
                  % (pair["apo"], pair["holo"], (pair.get("ligand") or {}).get("comp_id"),
                     *[((r.get("Q_SITE_does_site_selection_find_the_ligand") or {})
                        .get("routes", {}).get(k, {}) or {}).get("answer", "UNREAD")
                       for k in ("pipeline_sequence_transfer_apo", "pocket5_structure_transfer_apo",
                                 "fpocket_top_pocket_apo")], r["elapsed_s"]), flush=True)
            rows.append(r)
        doc["site_panel_in_regime"] = panel_site_supplement(rows, len(cands))
        doc["site_panel_rows"] = rows
        doc["_appendix"] = APPENDIX
        doc["verdict"] = {"outcome": "SITE SUPPLEMENT — NOT A PANEL VERDICT",
                          "reason": ("MODE=site runs the geometric site endpoint only. It emits no RMSD "
                                     "and cannot change the pre-registered panel's INCONCLUSIVE.")}
        _emit(doc)
        return
    # ★★ MODE=regime_dock — THE FAMILY POSITIVE CONTROL (added 2026-08-03; rationale at `OUT_REGIME`).
    # Same in-regime candidate list as MODE=site, but `site_only=False`, so every pair runs the full arm
    # set: the pipeline's own box, the fpocket box, and the oracle box, each beside the self-dock control
    # that goes through the SAME site-selection route. That pairing is the whole design — 14 pairs graded
    # through one box would repeat the original panel's mistake of reporting a number that moves if either
    # the site or the search is wrong.
    if mode == "regime_dock":
        rows, cands = [], in_regime_pairs(sel)
        doc["_in_regime_candidates"] = cands
        panel_start = time.time()
        for pair in cands:
            if time.time() - panel_start > REGIME_PANEL_BUDGET_S:
                rows.append({"candidate": pair, "refusals": [
                    {"stage": "panel_budget",
                     "evidence": "the regime panel's %ds wall-clock budget was already spent when this "
                                 "pair came up; it is UNRUN, not excluded" % REGIME_PANEL_BUDGET_S}]})
                continue
            t0 = time.time()
            r = run_benchmark(pair, os.path.join(WORK, "rd_%s_%s" % (pair["apo"], pair["holo"])), af2,
                              ceiling_replicates=CEILING_REPLICATES)
            # ⛔ `verdict()` IS CALLED PER PAIR AND NEVER PANEL-WIDE HERE. Its outcome string is what makes
            # each row readable on its own; the panel-level answer is a COUNT over rows whose control
            # passed, computed in `panel_regime_dock`, never an average of RMSDs across pairs.
            if not r.get("excluded_by") and (r.get("arms") or {}):
                r["verdict"] = verdict(r)
                r["questions"] = pair_questions(r, pair)
            r["elapsed_s"] = round(time.time() - t0, 1)
            a = r.get("arms") or {}
            print("[apo-pose-recovery/regime_dock] %s -> %s (%s): pipeline=%s fpocket=%s oracle=%s "
                  "ceiling=%s in %.0fs"
                  % (pair["apo"], pair["holo"], (pair.get("ligand") or {}).get("comp_id"),
                     (a.get("PRIMARY_blind_apo_pipeline_box") or {}).get("rmsd_A"),
                     (a.get("blind_apo_fpocket_top_box") or {}).get("rmsd_A"),
                     (a.get("C3_oracle_box_apo") or {}).get("rmsd_A"),
                     (a.get("C1c_self_dock_holo_oracle_box") or {}).get("rmsd_A"),
                     r["elapsed_s"]), flush=True)
            rows.append(r)
        doc["regime_dock_panel"] = panel_regime_dock(rows, cands)
        doc["regime_dock_rows"] = rows
        doc["induced_fit_panel"] = panel_induced_fit([r for r in rows if r.get("verdict")])
        doc["_appendix"] = APPENDIX
        doc["verdict"] = {
            "outcome": "FAMILY POSITIVE CONTROL — NOT THE PRE-REGISTERED PANEL",
            "reason": ("MODE=regime_dock docks the in-regime NR4A pairs. It is a separate candidate list "
                       "in a separate file and cannot change apo-pose-recovery.json's INCONCLUSIVE."),
            "headline": doc["regime_dock_panel"].get("headline")}
        _emit(doc)
        return
    # ⛔ A PANEL, NOT A PICK. Candidates are taken in the pre-registered rank order and every one that is
    # attempted is reported, including the ones R2b throws out. The PRIMARY verdict is the first pair that
    # actually runs; the rest are supporting cases. Nothing here can be re-ordered by its answer, because
    # the order is fixed by SELECTION_RULES before any structure is fetched.
    panel, attempted = [], 0
    panel_start = time.time()
    # ★ C6 RUNS ON THE PRIMARY PAIR AND ONLY THE PRIMARY PAIR. That is the pair whose numbers the roadmap
    # and the manuscript quote, and it is the one whose reproducibility therefore decides whether those
    # quotes are legitimate. Replicating all six would multiply the panel's wall clock by ~4 to answer a
    # question about pairs nothing downstream cites. `replicated` is set from the RESULT, not from the
    # loop index, so a rank-1 pair that R2b throws out hands the replicates to the pair that actually runs.
    replicated = False
    for pair in _panel_candidates(sel):
        attempted += 1
        if time.time() - panel_start > PANEL_BUDGET_S:
            panel.append({"candidate": pair, "refusals": [
                {"stage": "panel_budget",
                 "evidence": "the panel's %ds wall-clock budget was already spent when this pair came up; "
                             "it is UNRUN, not excluded" % PANEL_BUDGET_S}]})
            break
        t0 = time.time()
        res = run_benchmark(pair, os.path.join(WORK, "%s_%s" % (pair["apo"], pair["holo"])), af2,
                            replicates=0 if replicated else SEED_REPLICATES,
                            ceiling_replicates=CEILING_REPLICATES)
        if res.get("C6_seed_replicates"):
            replicated = True
        res["elapsed_s"] = round(time.time() - t0, 1)
        print("[apo-pose-recovery] %s -> %s (%s): %s in %.0fs"
              % (pair["apo"], pair["holo"], (pair.get("ligand") or {}).get("comp_id"),
                 (res.get("verdict") or {}).get("outcome")
                 or [r["stage"] for r in (res.get("refusals") or [])], res["elapsed_s"]), flush=True)
        panel.append(res)
        if attempted >= PANEL_SIZE:            # bounded: never grind the whole 5-figure candidate list
            break
    doc["panel"] = panel
    ran = [r for r in panel if r.get("verdict")]
    doc["result"] = ran[0] if ran else (panel[0] if panel else None)
    doc["verdict"] = (ran[0]["verdict"] if ran else
                      {"outcome": "INCONCLUSIVE",
                       "reason": "no candidate pair reached a scored arm",
                       "refusals": [r.get("refusals") for r in panel]})
    doc["verdict"]["panel_summary"] = {
            "n_pairs_scored": len(ran),
            "pairs": [{"apo": r["candidate"]["apo"], "holo": r["candidate"]["holo"],
                       "ligand": r["candidate"]["ligand"]["comp_id"],
                       "outcome": r["verdict"]["outcome"],
                       "primary_rmsd_A": r["verdict"].get("primary_rmsd_A")} for r in ran],
            "n_recovered": sum(1 for r in ran if r["verdict"]["outcome"] == "RECOVERED"),
        # ★ THE PANEL-LEVEL ANSWER APPLIES THE SAME PRE-REGISTERED C1 RULE ONE LEVEL UP: a pair whose
        # protocol control fails is uninterpretable, so the panel's answer is over the INTERPRETABLE pairs
        # and the count of uninterpretable ones is reported beside it rather than averaged in.
        "n_interpretable": sum(1 for r in ran
                               if (r["verdict"].get("c1_rmsd_A") is not None
                                   and r["verdict"]["c1_rmsd_A"] <= RECOVER_RMSD_A)),
        "n_uninterpretable_control_failed": sum(1 for r in ran
                                                if r["verdict"]["outcome"] == "INCONCLUSIVE"),
        "n_excluded_covalent_R2b": sum(1 for r in panel if r.get("excluded_by") == "R2b"),
            "_note": "the PRIMARY verdict is the rank-1 pair; these are supporting cases, reported "
                     "whatever they returned",
        }
    doc["site_vs_docking"] = panel_site_vs_docking(ran)
    doc["induced_fit_panel"] = panel_induced_fit(ran)
    doc["reproducibility"] = panel_reproducibility(panel)
    doc["_appendix"] = APPENDIX
    _emit(doc)


def _REGIME_ACCESSIONS():
    """The proteins the pipeline actually carries Pocket-5 onto. READ FROM THE PIPELINE, never typed."""
    import nr4a3_warhead as wh
    return set(wh.PARALOGUES.values()) | {"Q92570"}


def in_regime_pairs(sel, limit=None):
    """Every apo/holo pair on an accession the pipeline ACTUALLY transfers Pocket-5 onto, one per holo.

    ⛔ THE REGIME SET IS READ FROM THE PIPELINE, NEVER TYPED — `nr4a3_warhead.PARALOGUES` plus NR4A3's own
    accession, the same source `pair_questions` uses for its disqualifier. No per-protein cap: the cap
    exists to stop one protein dominating a DOCKING panel's wall clock, and there is no dock here.

    ⚠ THIS DOES NOT TOUCH `panel_pool`. The pre-registered panel, its rank order, its caps and its R2b
    exclusion are all unchanged; this is a separate list for a separate, docking-free question."""
    regime = _REGIME_ACCESSIONS()
    seen, out = set(), []
    for r in (list(sel.get("_all_ranked_in_regime") or []) + (sel.get("panel_pool") or [])
              + list(sel.get("considered_top") or [])):
        if r.get("accession") not in regime or not r.get("apo") or not r.get("holo"):
            continue
        if (r["apo"], r["holo"]) in seen or r["holo"] in {h for _a, h in seen}:
            continue
        seen.add((r["apo"], r["holo"]))
        out.append(dict(r))
        if limit and len(out) >= limit:
            break
    return out


def panel_site_supplement(rows, attempted):
    """The in-regime site question, counted over what it could actually read.

    ⚠ EVERY ATTEMPTED PAIR IS REPORTED, including the ones that refused, and the refusal reasons are
    tallied — a supplement that shows only the pairs that worked would understate exactly the thing it
    exists to measure (how little in-regime evidence about the site step there is)."""
    import nr4a3_warhead as wh
    graded = [r for r in rows if (r.get("Q_SITE_does_site_selection_find_the_ligand") or {}).get("routes")]

    def _found(r, route):
        return ((r.get("Q_SITE_does_site_selection_find_the_ligand") or {})
                .get("routes", {}).get(route, {}).get("ligand_centroid_in_box"))
    refusals = {}
    for r in rows:
        for f in (r.get("refusals") or []):
            refusals[f.get("stage")] = refusals.get(f.get("stage"), 0) + 1
    return {
        "_asks": ("Over EVERY apo/holo pair on a protein the pipeline actually transfers Pocket-5 onto: "
                  "does a site-selection route put the crystallographic ligand inside its own box?"),
        "_why_separate": ("this supplement is NOT the pre-registered panel and is never summed into it. "
                          "It exists because the panel could only offer 2 in-regime pairs, both from one "
                          "apo structure, and a site claim on n=2 is not a claim."),
        "_regime": sorted(set(wh.PARALOGUES.values()) | {"Q92570"}),
        "_no_docking": "geometric containment only — no smina, no seed, no scoring, deterministic",
        "n_attempted": attempted, "n_gradeable": len(graded),
        "refusal_stages": refusals,
        "pipeline_sequence_transfer_found": sum(1 for r in graded
                                                if _found(r, "pipeline_sequence_transfer_apo")),
        "pocket5_structure_transfer_found": sum(1 for r in graded
                                                if _found(r, "pocket5_structure_transfer_apo")),
        "fpocket_top_pocket_found": sum(1 for r in graded if _found(r, "fpocket_top_pocket_apo")),
        "n_covalent_read_here_but_excluded_from_the_docking_panel":
            sum(1 for r in graded if r.get("covalent_but_site_gradeable")),
        "pairs": [{
            "accession": r["candidate"].get("accession"), "protein": r["candidate"].get("protein"),
            "apo": r["candidate"].get("apo"), "holo": r["candidate"].get("holo"),
            "ligand": (r["candidate"].get("ligand") or {}).get("comp_id"),
            "covalent": bool(r.get("covalent_but_site_gradeable")),
            "site_ca_rmsd_A": (r.get("induced_fit") or {}).get("site_ca_rmsd_A"),
            "nr4a3_aligned_identity": ((r.get("boxes", {}).get("pipeline_apo") or {}).get("detail")
                                       or {}).get("nr4a3_aligned_identity"),
            "pipeline_sequence_transfer": ("SITE FOUND" if _found(r, "pipeline_sequence_transfer_apo")
                                           else "SITE MISSED"),
            "pocket5_structure_transfer": ("SITE FOUND" if _found(r, "pocket5_structure_transfer_apo")
                                           else "SITE MISSED"),
            "fpocket_top_pocket": ("SITE FOUND" if _found(r, "fpocket_top_pocket_apo")
                                   else "SITE MISSED"),
        } for r in graded],
        "unreadable": [{"apo": r["candidate"].get("apo"), "holo": r["candidate"].get("holo"),
                        "why": [f.get("stage") for f in (r.get("refusals") or [])]}
                       for r in rows if r not in graded],
    }


#: The three blind arms of `run_benchmark`, each with the self-dock control that goes through the SAME
#: site-selection route. Read as (arm, its own control, what a pass would mean).
REGIME_ARMS = (
    ("pipeline_site_transfer", "PRIMARY_blind_apo_pipeline_box", "C1_self_dock_holo",
     "NR4A3's Pocket-5 carried onto this receptor by the pipeline's own transfer — the box every "
     "downstream NR4A3 number was computed in"),
    ("fpocket_top_pocket", "blind_apo_fpocket_top_box", "C1_self_dock_holo_fpocket",
     "the receptor's own highest-druggability fpocket cavity, using NO NR4A3 information at all"),
    ("oracle_box", "C3_oracle_box_apo", "C1c_self_dock_holo_oracle_box",
     "a box centred on the crystallographic ligand — the site handed over for free, so a miss here is "
     "the search and scoring and nothing else"),
)


def panel_regime_dock(rows, cands):
    """The family positive control, counted per arm over the pairs that arm could actually grade.

    ⛔ THREE COUNTING RULES, EACH ONE A MISTAKE THIS MODULE HAS ALREADY MADE ONCE.

    1. **Every arm is counted against ITS OWN control, and a pair whose control missed is counted OUT,
       never averaged in.** This is the pre-registered C1 rule applied per arm instead of once for the
       whole pair — which is exactly what the original panel could not do, and why a 19 A miss there was
       equally consistent with a broken search and a box in the wrong half of the protein.
    2. **No RMSD is averaged across pairs.** The panel-level statistic is a COUNT of pairs in each
       pre-registered band (`C14`). A mean RMSD over a set containing one 19 A miss is not a summary of
       anything, and `C6` already measured that a single arm's RMSD moves 3.04-3.50 A between runs of
       this same benchmark — so a count of BANDS is the only stable readout, which is `C6`'s own finding
       applied rather than restated.
    3. **Refusals and exclusions are reported, never dropped.** `n_attempted` is the candidate count and
       every gap between it and `n_graded` carries its stage. A family control that quietly reported only
       the pairs that worked would overstate precisely the thing it exists to measure.
    """
    import nr4a3_warhead as wh
    graded = [r for r in rows if (r.get("arms") or {})]
    out_arms, refusals = {}, {}
    for r in rows:
        for f in (r.get("refusals") or []):
            refusals[f.get("stage")] = refusals.get(f.get("stage"), 0) + 1

    for label, arm_key, ctrl_key, what in REGIME_ARMS:
        per_pair = []
        for r in graded:
            a = (r.get("arms") or {})
            blind, ctrl = a.get(arm_key) or {}, a.get(ctrl_key) or {}
            c_rms = ctrl.get("rmsd_A")
            per_pair.append({
                "apo": r["candidate"].get("apo"), "holo": r["candidate"].get("holo"),
                "protein": r["candidate"].get("protein"),
                "ligand": (r["candidate"].get("ligand") or {}).get("comp_id"),
                "blind_apo_rmsd_A": blind.get("rmsd_A"), "blind_apo_fnat": blind.get("fnat"),
                "band": _band(blind.get("rmsd_A")),
                "own_control_rmsd_A": c_rms,
                "control_passed": c_rms is not None and c_rms <= RECOVER_RMSD_A,
            })
        ok = [p for p in per_pair if p["control_passed"] and p["blind_apo_rmsd_A"] is not None]
        out_arms[label] = {
            "_site": what,
            "arm": arm_key, "control": ctrl_key,
            "n_pairs": len(per_pair),
            "n_gradeable_control_passed": len(ok),
            "n_recovered": sum(1 for p in ok if p["band"] == "RECOVERED"),
            "n_partial": sum(1 for p in ok if p["band"] == "PARTIAL"),
            "n_not_recovered": sum(1 for p in ok if p["band"] == "NOT RECOVERED"),
            "n_fnat_at_or_above_criterion": sum(1 for p in ok if (p["blind_apo_fnat"] or 0) >= FNAT_SUCCESS),
            "pairs": per_pair,
        }

    fp, pl = out_arms["fpocket_top_pocket"], out_arms["pipeline_site_transfer"]
    if fp["n_gradeable_control_passed"] == 0 and pl["n_gradeable_control_passed"] == 0:
        headline = ("NO ARM IS GRADEABLE — every pair's self-dock control missed, so this panel measures "
                    "the docking protocol and says nothing about apo->holo recovery on the NR4A fold. "
                    "Same pre-registered outcome as the original panel, one level up.")
    else:
        headline = (
            "On the NR4A fold, blind from apo: the fpocket box recovered %d of %d gradeable pairs "
            "(%d partial, %d not recovered); the pipeline's own Pocket-5 transfer recovered %d of %d "
            "(%d partial, %d not recovered)."
            % (fp["n_recovered"], fp["n_gradeable_control_passed"], fp["n_partial"], fp["n_not_recovered"],
               pl["n_recovered"], pl["n_gradeable_control_passed"], pl["n_partial"],
               pl["n_not_recovered"]))
    return {
        "_asks": ("On the protein family the pipeline actually targets, using ligand positions that are "
                  "already known from crystallography: can this docking protocol recover a pose blind "
                  "from apo — and does the answer depend on which route drew the box?"),
        "_why_this_is_the_positive_control_the_program_said_it_lacked": (
            "the roadmap and the manuscript both state that no known answer exists for pose prediction "
            "here. That is true of NR4A3 ITSELF — no ligand-bound NR4A3 structure exists — and it is "
            "FALSE for the family: NR4A1 and NR4A2 carry deposited holo structures at %s aligned "
            "identity to NR4A3, and this mode grades against them."
            % sorted({p.get("nr4a3_aligned_identity") for p in
                      [((r.get("boxes", {}).get("pipeline_apo") or {}).get("detail") or {})
                       for r in graded]} - {None})),
        "_regime": sorted(set(wh.PARALOGUES.values()) | {"Q92570"}),
        "_never_summed_into": ("apo-pose-recovery.json — that panel's candidate list, rank order and "
                               "INCONCLUSIVE verdict are untouched by this mode"),
        "n_attempted": len(cands), "n_graded": len(graded),
        "n_excluded_covalent_R2b": sum(1 for r in rows if r.get("excluded_by") == "R2b"),
        "refusal_stages": refusals,
        "criterion": {"recovered_A": RECOVER_RMSD_A, "partial_A": PARTIAL_RMSD_A,
                      "fnat_success": FNAT_SUCCESS,
                      "_source": "C14, unchanged — this mode adds pairs, never a threshold"},
        "arms": out_arms,
        "headline": headline,
    }


def panel_reproducibility(panel):
    """C6 one level up: is a quoted single-draw RMSD from this benchmark a quotable number?

    ⚠ AN ABSENT REPLICATE SET IS RECORDED AS ABSENT (CLAUDE.md §4). A run made before C6 existed, or one
    whose primary pair spent its wall clock, gets `measured: false` and the reason — never an empty
    summary that reads as "no variation found"."""
    rep = next((r.get("C6_seed_replicates") for r in panel if r.get("C6_seed_replicates")), None)
    if not rep:
        return {"measured": False,
                "_reads": "no pair carried a C6 replicate set in this run, so the run-to-run spread of "
                          "these arms is UNMEASURED here — not zero"}
    arms = rep.get("arms") or {}
    graded = {k: v for k, v in arms.items() if v.get("n_replicates")}
    # C6b, one level up — how much of `Q_DOCKING.n_gradeable` is a coin flip?
    ceil = [(r["candidate"]["apo"], r["candidate"]["holo"], r["C6b_ceiling_replicates"])
            for r in panel if r.get("C6b_ceiling_replicates")]
    flippy = [{"apo": a, "holo": h, "n_seeds_gradeable": c["n_seeds_gradeable"],
               "n_seeds": c["n_seeds"], "min_A": c["min_A"], "max_A": c["max_A"]}
              for a, h, c in ceil if c.get("gradeability_stable") is False]
    n_always = sum(1 for _a, _h, c in ceil if c["n_seeds"] and c["n_seeds_gradeable"] == c["n_seeds"])
    unstable = sorted(k for k, v in graded.items() if v.get("band_stable") is False)
    nondet = sorted(k for k, v in graded.items()
                    if (v.get("_determinism_selfcheck") or {}).get("identical") is False)
    return {
        "measured": True,
        "n_arms_replicated": len(graded),
        "n_arms_unrun": len(arms) - len(graded),
        "seeds": rep.get("seeds"),
        "max_spread_A": max((v["spread_A"] for v in graded.values()), default=None),
        "arms_whose_band_flips": unstable,
        "arms_that_did_not_reproduce_at_a_fixed_seed": nondet,
        "all_bands_stable": bool(graded) and not unstable,
        "gradeability": {
            "_asks": ("how much of Q-DOCKING's `n_gradeable` is decided by the search rather than by the "
                      "data? Measured because it moved 3 -> 4 between two runs of identical code."),
            "n_pairs_with_ceiling_replicates": len(ceil),
            "n_pairs_gradeable_on_every_seed": n_always,
            "pairs_whose_gradeability_flips": flippy,
            "gradeable_count_is_stable": bool(ceil) and not flippy,
            "_reads": ("every pair's gradeability is the same on every seed, so `n_gradeable` is a "
                       "property of the panel and not of the random number generator"
                       if ceil and not flippy else
                       "⛔ %d PAIR(S) ARE GRADEABLE ON SOME SEEDS AND NOT OTHERS, so `n_gradeable` is "
                       "itself a range and must never be quoted as a single integer" % len(flippy)
                       if flippy else
                       "UNMEASURED — no pair carried ceiling replicates in this run")},
        "_reads": (
            "every replicated arm stays in one pre-registered band across the seeds, so the panel's "
            "CONCLUSIONS are reproducible even though its 3-figure RMSDs are not. ⛔ Quote the band and "
            "the spread; a bare RMSD from this benchmark is one draw and must not be cited as a "
            "measurement." if graded and not unstable else
            "⛔ at least one replicated arm changes pre-registered band across seeds (%s). Any statement "
            "of that arm from a single run is not supportable." % ", ".join(unstable) if unstable else
            "no arm produced a gradeable replicate set; the spread is UNMEASURED, not zero")}


# ==================================================================================================
# PANEL-LEVEL READOUTS FOR THE TWO SEPARATED QUESTIONS
# ==================================================================================================

def panel_induced_fit(ran):
    """R9 one level up: how hard a test IS this panel, measured on every pair rather than argued.

    ⛔ THE HEADLINE PAIR IS A WEAK TEST OF THE THING THE PANEL CLAIMS TO TEST, and that has to be visible
    without reading six nested blocks. 4RZF->4REF moves 0.14 A of Ca at the ligand site; an apo->holo
    cross-dock across 0.14 A is a re-dock, so it can neither demonstrate nor refute apo->holo transfer.
    Whether ANY pair in the panel carries a genuinely large rearrangement is therefore a property of the
    whole experiment, and if the answer were no, the experiment could not support its own headline."""
    rows = []
    for r in ran:
        fit = r.get("induced_fit") or {}
        rows.append({"apo": r["candidate"]["apo"], "holo": r["candidate"]["holo"],
                     "protein": r["candidate"].get("protein"),
                     "site_ca_rmsd_A": fit.get("site_ca_rmsd_A"),
                     "global_ca_rmsd_A": fit.get("global_ca_rmsd_A"),
                     "n_site_residues": fit.get("n_site"),
                     "large_rearrangement": fit.get("large_rearrangement")})
    vals = [x["site_ca_rmsd_A"] for x in rows if x["site_ca_rmsd_A"] is not None]
    n_large = sum(1 for x in rows if x.get("large_rearrangement"))
    return {
        "_threshold_A": LARGE_INDUCED_FIT_A,
        "pairs": rows,
        "n_pairs": len(rows), "n_with_large_rearrangement": n_large,
        "max_site_ca_rmsd_A": max(vals) if vals else None,
        "min_site_ca_rmsd_A": min(vals) if vals else None,
        "panel_contains_a_large_rearrangement": n_large > 0,
        "_reads": ("%d of %d pairs move at least %.2f A of Ca at the ligand site, so the panel is not "
                   "only near-rigid re-docks. Any pair below that line is a weak test of apo->holo "
                   "transfer and must not be quoted as one." % (n_large, len(rows), LARGE_INDUCED_FIT_A)
                   if n_large else
                   "⛔ NO pair in this panel moves as much as %.2f A of Ca at the ligand site. The whole "
                   "experiment is then a set of near-rigid re-docks and CANNOT speak to apo->holo "
                   "transfer, whatever any single RMSD says. This is a limitation of the test, not a "
                   "result." % LARGE_INDUCED_FIT_A),
        "_caveat": ("the induced fit is measured AT THE NATIVE LIGAND SITE. Where a blind arm's box is "
                    "somewhere else, the rearrangement that arm actually faced is not this number."),
    }


def panel_site_vs_docking(ran):
    """The panel answer to each question separately, with the uninterpretable pairs named, never averaged."""
    doc_rows, site_rows = [], []
    for r in ran:
        q = r.get("questions") or {}
        d = q.get("Q_DOCKING_given_the_correct_site") or {}
        s = q.get("Q_SITE_does_site_selection_find_the_site") or {}
        tag = {"apo": r["candidate"]["apo"], "holo": r["candidate"]["holo"],
               "protein": r["candidate"].get("protein"),
               "ligand": (r["candidate"].get("ligand") or {}).get("comp_id")}
        doc_rows.append({**tag, "apo_rmsd_A": d.get("apo_rmsd_A"), "apo_fnat": d.get("apo_fnat"),
                         "answer": d.get("answer"), "control_rmsd_A": d.get("control_rmsd_A"),
                         "control_passed": d.get("control_passed")})
        site_rows.append({**tag,
                          "pipeline_sequence_transfer": (s.get("pipeline_sequence_transfer") or {}).get("answer"),
                          "pocket5_structure_transfer": (s.get("pocket5_structure_transfer") or {}).get("answer"),
                          "fpocket_top_pocket": (s.get("fpocket_top_pocket") or {}).get("answer"),
                          "nr4a3_aligned_identity": s.get("nr4a3_aligned_identity"),
                          "interpretable": s.get("interpretable_as_evidence_about_the_pipeline"),
                          "disqualifiers": s.get("disqualifiers"),
                          "confound_reading": s.get("confound_reading")})
    gradeable = [x for x in doc_rows if x["control_passed"]]
    interp = [x for x in site_rows if x["interpretable"]]
    return {
        "Q_DOCKING_given_the_correct_site": {
            "_asks": "GIVEN THE CORRECT SITE, does blind apo->holo docking reproduce the pose?",
            "pairs": doc_rows,
            "n_pairs": len(doc_rows), "n_gradeable": len(gradeable),
            "n_recovered": sum(1 for x in gradeable if x["answer"] == "RECOVERED"),
            "n_partial": sum(1 for x in gradeable if x["answer"] == "PARTIAL"),
            "n_not_recovered": sum(1 for x in gradeable if x["answer"] == "NOT RECOVERED"),
            "_note": ("a pair whose protocol ceiling (C1c) missed cannot grade the docking and is counted "
                      "out, not averaged in — the same pre-registered rule C1 applies to the primary"),
        },
        "Q_SITE_does_site_selection_find_the_site": {
            "_asks": "Does a site-selection route put the crystallographic ligand inside its own box?",
            "pairs": site_rows,
            "n_pairs": len(site_rows),
            "n_interpretable_about_the_pipeline": len(interp),
            "pipeline_sequence_transfer_found": sum(1 for x in interp
                                                    if x["pipeline_sequence_transfer"] == "SITE FOUND"),
            "pocket5_structure_transfer_found": sum(1 for x in interp
                                                    if x["pocket5_structure_transfer"] == "SITE FOUND"),
            "fpocket_top_pocket_found": sum(1 for x in interp if x["fpocket_top_pocket"] == "SITE FOUND"),
            # ⛔ THE COUNT THAT MATTERS IS OVER THE INTERPRETABLE PAIRS ONLY. Pairs disqualified by the
            # regime gate, a declared allosteric ligand or an engineered pocket are reported with their
            # reason and excluded from the count, because including them would let the benchmark's own
            # design decide the pipeline's grade.
            "_note": ("counted over interpretable pairs only; every excluded pair carries the reason it "
                      "was excluded in its `disqualifiers`"),
        },
    }


def _dedup_pairs(cands):
    """ONE PAIR PER DISTINCT HOLO, at most `MAX_PER_PROTEIN` per protein, in rank order.

    ⚠ THE HOLO RULE IS A BUG FIX, NOT A RE-TUNING. It was stated in this module before the first run —
    "three pairs sharing one crystal would be one known answer measured three times" — but the first
    implementation skipped a row only when BOTH its apo and its holo had been seen, so five different apo
    structures against the single holo 5Y41 all entered and the three that scored were three apo receptors
    against ONE crystal (4REF). The per-protein cap exists for the same reason one level up. Neither rule
    can be steered by an answer: both act on a rank order fixed by SELECTION_RULES before any fetch."""
    seen_holo, per_protein, out = set(), {}, []
    for r in cands:
        acc, holo = r.get("accession"), r.get("holo")
        if not r.get("apo") or not holo or holo in seen_holo:
            continue
        if per_protein.get(acc, 0) >= MAX_PER_PROTEIN:
            continue
        seen_holo.add(holo)
        per_protein[acc] = per_protein.get(acc, 0) + 1
        # ⛔ `apo_chains` / `holo_chains` MUST BE CARRIED. Dropping them here made the accession-scoped
        # chain restriction INERT on every panel pair — the fix was written, landed, and then ran against
        # `None` for the whole panel. Measured on CI run 30764845241 (2026-08-03): `result.chains` reads
        # `{"holo_declared": null, "apo_declared": null}`, `selection.considered_top[0]` carries both
        # fields and `selection.panel_pool[0]` carries neither, and 1DSZ->9GFE and 1DSZ->3KMR still
        # refused at identity **0.321** — the exact number the comment at step 3 names as the symptom of
        # the chain-picking bug it claims to have fixed. Four observations, one mechanism.
        out.append({k: r[k] for k in ("accession", "protein", "apo", "holo", "ligand", "apo_method",
                                      "apo_models", "apo_resolution_A", "holo_resolution_A",
                                      "apo_title", "holo_title",
                                      "apo_chains", "holo_chains") if k in r})
        if len(out) >= PANEL_SIZE:
            break
    return out


def _panel_candidates(sel):
    """The pre-registered panel: the pool built in `mode_select`, or a de-dup of the excerpt as a fallback."""
    pool = sel.get("panel_pool")
    if pool:
        return pool
    rows = list(sel.get("considered_top") or [])
    if sel.get("chosen"):
        rows = [dict(sel["chosen"])] + rows
    return _dedup_pairs(rows)


def _emit(doc):
    # ⛔ THE SUPPLEMENT MUST NEVER WRITE OVER THE PANEL'S ARTIFACT. MODE=site produces a docking-free
    # document with no arms and no RMSDs; emitting it to `apo-pose-recovery.json` would silently replace
    # the pre-registered panel's result with something that cannot be mistaken for it only if you read
    # it. Different question, different file — and `MODE=report` still renders the panel's.
    out = {"site": OUT_SITE, "regime_dock": OUT_REGIME}.get(doc.get("_mode"), OUT)
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=2)
    print(json.dumps({k: doc[k] for k in ("_mode", "verdict") if k in doc}, indent=2))
    print("[apo-pose-recovery] wrote %s" % out)
    # ⛔ ONLY THE PRE-REGISTERED PANEL RENDERS THE MARKDOWN. `render_markdown` reads panel keys that the
    # supplements do not produce, and writing it from either of them would leave apo-pose-recovery.md
    # describing a run that is not the one its own JSON holds.
    if doc.get("_mode") in ("site", "regime_dock"):
        return
    try:
        _write(OUT_MD, render_markdown(doc))
        print("[apo-pose-recovery] wrote %s" % OUT_MD)
    except Exception as e:                                    # noqa: BLE001
        print("[apo-pose-recovery] markdown render failed: %s: %s" % (type(e).__name__, e))


def _f(v, nd=3, dash="—"):
    return dash if v is None else ("%.*f" % (nd, v) if isinstance(v, float) else str(v))


def render_markdown(doc):
    """The written finding, DERIVED from the artifact rather than typed beside it (CLAUDE.md §1.1).

    ⛔ NOTHING IN THIS FUNCTION MAY CARRY A NUMBER OF ITS OWN. Every figure below is read out of `doc`, so
    a prose summary cannot drift away from the JSON it summarises — which is the exact failure the
    one-fact-one-place rule exists to stop. If a value is missing it renders as an em dash and says
    UNREAD; it is never filled in."""
    v = doc.get("verdict") or {}
    svd = doc.get("site_vs_docking") or {}
    dq = svd.get("Q_DOCKING_given_the_correct_site") or {}
    sq = svd.get("Q_SITE_does_site_selection_find_the_site") or {}
    fit = doc.get("induced_fit_panel") or {}
    L = []
    L.append("# Known-answer pose recovery — the SITE question and the DOCKING question, separated\n")
    L.append("⛔ **GENERATED FILE — do not edit.** Every number here is rendered from "
             "[`apo-pose-recovery.json`](./apo-pose-recovery.json) by "
             "`apo_pose_recovery.render_markdown`, which owns none of them. Edit the module or re-run "
             "(`MODE=report`), never this file.\n")
    L.append("Pre-registered verdict, **unchanged by anything below**: **%s** — %s\n"
             % (v.get("outcome"), v.get("reason", "")))
    # ⚠ AN ABSENT SECTION IS RECORDED AS ABSENT, NEVER RENDERED AS ZEROES. An artifact written before the
    # site/docking split carries no `site_vs_docking`, and a table of `None`s would read as "measured, and
    # the answer was nothing" — which is the reading CLAUDE.md §4 exists to forbid.
    missing = [k for k in ("site_vs_docking", "induced_fit_panel") if not doc.get(k)]
    if missing:
        L.append("\n⚠ **THIS ARTIFACT DOES NOT CONTAIN %s.** It predates the site/docking split, so the "
                 "sections below are UNREAD, not empty. Re-run `MODE=run` to produce them; nothing here "
                 "may be quoted as a measurement.\n" % " or ".join("`%s`" % m for m in missing))
    L.append("\n## 1 · Q-DOCKING — given the correct site, does blind apo→holo docking recover the pose?\n")
    L.append("Arm: `C3_oracle_box_apo` (apo receptor, box on the crystallographic ligand). "
             "Control: `C1c_self_dock_holo_oracle_box`. Bands are the pre-registered %.2f / %.2f Å.\n"
             % (RECOVER_RMSD_A, PARTIAL_RMSD_A))
    L.append("\n| pair | protein | ligand | apo RMSD (Å) | fnat | answer | ceiling (Å) | ceiling passed |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in dq.get("pairs") or []:
        L.append("| %s→%s | %s | %s | %s | %s | %s | %s | %s |"
                 % (r.get("apo"), r.get("holo"), r.get("protein"), r.get("ligand"),
                    _f(r.get("apo_rmsd_A")), _f(r.get("apo_fnat")), r.get("answer"),
                    _f(r.get("control_rmsd_A")), r.get("control_passed")))
    L.append("\n**%s of %s pairs gradeable; %s RECOVERED, %s PARTIAL, %s NOT RECOVERED.** %s\n"
             % (dq.get("n_gradeable"), dq.get("n_pairs"), dq.get("n_recovered"), dq.get("n_partial"),
                dq.get("n_not_recovered"), dq.get("_note", "")))
    L.append("\n## 2 · Q-SITE — does site selection put the ligand inside the box it draws?\n")
    L.append("Geometric endpoint, no docking in it. `SITE FOUND` iff the crystallographic ligand's "
             "centroid lies inside the box.\n")
    L.append("\n| pair | protein | NR4A3 aligned identity | pipeline (sequence) | structure transfer | "
             "fpocket top | interpretable |")
    L.append("|---|---|---|---|---|---|---|")
    for r in sq.get("pairs") or []:
        L.append("| %s→%s | %s | %s | %s | %s | %s | %s |"
                 % (r.get("apo"), r.get("holo"), r.get("protein"),
                    _f(r.get("nr4a3_aligned_identity"), 4),
                    r.get("pipeline_sequence_transfer"), r.get("pocket5_structure_transfer"),
                    r.get("fpocket_top_pocket"), r.get("interpretable")))
    L.append("\n**Over the %s pair(s) that are evidence about the pipeline at all:** pipeline sequence "
             "transfer found the site on %s, the independent structural transfer on %s, fpocket's own top "
             "pocket on %s. %s\n"
             % (sq.get("n_interpretable_about_the_pipeline"), sq.get("pipeline_sequence_transfer_found"),
                sq.get("pocket5_structure_transfer_found"), sq.get("fpocket_top_pocket_found"),
                sq.get("_note", "")))
    L.append("\n### Why pairs are excluded, and what the confound control says\n")
    for r in sq.get("pairs") or []:
        L.append("- **%s→%s (%s)** — %s" % (r.get("apo"), r.get("holo"), r.get("protein"),
                                            r.get("confound_reading")))
        for d in r.get("disqualifiers") or []:
            L.append("  - ⛔ %s" % d)
    L.append("\n## 3 · How hard a test is this panel? (the caveat, measured)\n")
    L.append("Apo→holo Cα movement **at the ligand site**. A pair below %.2f Å is a re-dock with extra "
             "steps and cannot demonstrate apo→holo transfer.\n" % (fit.get("_threshold_A") or 0.0))
    L.append("\n| pair | protein | site Cα RMSD (Å) | global Cα RMSD (Å) | n site residues | large? |")
    L.append("|---|---|---|---|---|---|")
    for r in fit.get("pairs") or []:
        L.append("| %s→%s | %s | %s | %s | %s | %s |"
                 % (r.get("apo"), r.get("holo"), r.get("protein"), _f(r.get("site_ca_rmsd_A")),
                    _f(r.get("global_ca_rmsd_A")), r.get("n_site_residues"),
                    "**yes**" if r.get("large_rearrangement") else "no"))
    L.append("\n%s\n" % fit.get("_reads", ""))
    L.append("⚠ %s\n" % fit.get("_caveat", ""))
    L.append("\n## 4 · What the deposits themselves declare\n")
    L.append("\n| pair | engineered (apo) | engineered (holo) | same construct? | any in the ligand's "
             "contact shell | ligand declared allosteric |")
    L.append("|---|---|---|---|---|---|")
    mismatched = []
    for r in doc.get("panel") or []:
        if not r.get("verdict"):
            continue
        c, ec = r["candidate"], (r.get("engineered_construct") or {})
        al = (r.get("declared_allosteric") or {})
        eng = ec.get("engineered_residues_holo")
        apo_eng = ec.get("engineered_residues_apo")
        ins = ec.get("engineered_residues_in_native_ligand_site")
        same = ec.get("apo_and_holo_are_the_same_construct")
        if same is False:
            mismatched.append((c, ec))
        fmt = lambda ms: (", ".join("%s%s→%s" % (m.get("db_residue"), m["resseq"],
                                                 m.get("deposit_residue")) for m in ms) or "none")
        L.append("| %s→%s | %s | %s | %s | %s | %s |"
                 % (c.get("apo"), c.get("holo"),
                    "UNREAD" if apo_eng is None else fmt(apo_eng),
                    "UNREAD" if eng is None else fmt(eng),
                    "UNREAD" if same is None else ("yes" if same else "**NO**"),
                    ("UNREAD" if ins is None else
                     ", ".join("**%s%s→%s**" % (m["db_residue"], m["resseq"], m["deposit_residue"])
                               for m in ins) or "no"),
                    "**yes**" if al.get("declared_in_holo_title") else "no"))
    if mismatched:
        L.append("")
        for c, ec in mismatched:
            L.append("- ⚠ **%s→%s** — %s" % (c.get("apo"), c.get("holo"),
                                             ec.get("_construct_reads", "")))
        L.append("")
    elif any((r.get("engineered_construct") or {}).get("apo_and_holo_are_the_same_construct") is None
             for r in doc.get("panel") or [] if r.get("verdict")):
        L.append("\n⚠ *The apo-side construct comparison is UNREAD in this artifact — it predates C5b. "
                 "Absent, not \"the constructs match\".*\n")
    # ⚠ AN ABSENT SECTION IS RECORDED AS ABSENT. An artifact written before C6 existed carries no
    # `reproducibility`, and a heading with nothing under it would read as "no variation was found".
    L.append("\n## 4b · Is a single-run RMSD from this benchmark quotable? (C6, seed replicates)\n")
    rp = doc.get("reproducibility")
    if not rp:
        L.append("⚠ **UNMEASURED in this artifact** — it predates C6. Absent, not zero.\n")
    elif not rp.get("measured"):
        L.append("⚠ **UNMEASURED in this run** — %s\n" % rp.get("_reads"))
    else:
        L.append("Seeds: `%s`. The endpoint is the pre-registered BAND, not a tighter number.\n"
                 % ", ".join(str(s) for s in rp.get("seeds") or []))
        L.append("\n| arm | unseeded (the quoted draw) | median | min–max | spread | bands seen | "
                 "band stable |")
        L.append("|---|---|---|---|---|---|---|")
        c6 = next((r.get("C6_seed_replicates") for r in (doc.get("panel") or [])
                   if r.get("C6_seed_replicates")), {}) or {}
        for name, row in (c6.get("arms") or {}).items():
            if not row.get("n_replicates"):
                L.append("| `%s` | %s | — | — | — | — | ⚠ UNRUN — %s |"
                         % (name, _f(row.get("unseeded_rmsd_A")), row.get("why")))
                continue
            L.append("| `%s` | %s Å (%s) | %s | %s–%s | %s Å | %s | %s |"
                     % (name, _f(row.get("unseeded_rmsd_A")), row.get("unseeded_band"),
                        _f(row.get("median_A")), _f(row.get("min_A")), _f(row.get("max_A")),
                        _f(row.get("spread_A")), ", ".join(row.get("bands_seen") or []),
                        "yes" if row.get("band_stable") else "**NO**"))
        L.append("\n%s\n" % rp.get("_reads"))
        gr = rp.get("gradeability") or {}
        if gr:
            L.append("\n**Gradeability (C6b) — %s**\n" % gr.get("_reads", ""))
            for p in gr.get("pairs_whose_gradeability_flips") or []:
                L.append("- ⛔ **%s→%s** gradeable on **%s of %s** seeds (ceiling %s–%s Å against the "
                         "2.00 Å criterion)" % (p["apo"], p["holo"], p["n_seeds_gradeable"],
                                                p["n_seeds"], _f(p["min_A"]), _f(p["max_A"])))
        nd = rp.get("arms_that_did_not_reproduce_at_a_fixed_seed")
        if nd:
            L.append("⚠ **Did not reproduce at a fixed seed:** %s — the spread above is search variation "
                     "PLUS non-determinism.\n" % ", ".join(nd))
    L.append("\n## 5 · What moved and what did not\n")
    ap = doc.get("_appendix") or APPENDIX
    for label, key in (("Unchanged (pre-registered)", "unchanged"),
                       ("Added 2026-08-02 (second revision)", "added_2026_08_02_second_revision"),
                       ("Added 2026-08-03 (third revision)", "added_2026_08_03_third_revision")):
        L.append("\n**%s**\n" % label)
        # ⚠ An artifact written before a revision existed carries no entry for it. Saying so is the
        # point; an empty bullet list under a heading reads as "this revision changed nothing".
        for row in ap.get(key) or ["⚠ *not present in this artifact — it predates this revision.*"]:
            L.append("- %s" % row)
    L.append("\n**Corrected — superseded values retained (CLAUDE.md §1.2)**\n")
    # every `corrected_*` block, not one hard-coded date — a new correction list must never be able to
    # exist in the artifact and be invisible in the page rendered from it.
    for key in sorted(k for k in ap if k.startswith("corrected_")):
        for row in ap.get(key) or []:
            L.append("- `%s` — was: %s. Now: %s" % (row["what"], row["superseded"], row["now"]))
    L.append("\n⛔ This page claims nothing about NR4A3 selectivity, efficacy, safety or clinical "
             "readiness. It grades an instrument, not a molecule.\n")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
