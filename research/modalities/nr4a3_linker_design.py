#!/usr/bin/env python3
"""
RUNG 5b — INVERSE LINKER DESIGN. $0 CPU, pure stdlib.

WHAT nr4a3-program-map.md ASKS FOR (ladder item 5b): "For each confirmed basin, derive linker requirements (endpoint
distance, exit-vector dihedral, strain, reach), enumerate a virtual library, filter by basin fidelity,
annotate exact structures + synthetic feasibility -> ~12-20 virtual constructs. For basins carrying the
covalent handle, the library enumerates the ELECTROPHILE POSITION ON THE LINKER as a design variable, and
PREFERS REVERSIBLE-COVALENT chemistry."

Inputs, all committed artifacts of earlier rungs — nothing here is invented:
  * `nr4a3-orientation-basins.json`  (RUNG 5a) — the nominated basins, their placements, spans and term-(a)
    reach records. The five CONFIRMED meta-basins are read from it, not hard-coded.
  * `nr4a3-e3-arm-registry.json`     (RUNG 5a staging) — each E3 arm's rigid body, its ligand exit atom and
    the observed E2 catalytic-cysteine transfer anchor.
  * `nr4a3-differential-surface-atlas.json` (RUNG 4) — per-residue NR4A3-vs-NR4A1/NR4A2 divergence, in the
    same local numbering, which is what makes a LIGAND-side wedge element locatable.
  * `congeneric-warhead-series.json` — the exit-vector handles on the cmpd19 anchor. The warhead-side
    chemistry is TAKEN FROM that staged series rather than drawn fresh.
  * `results/nr4a3-matrix/nr4a3-opened.pdb` — the matched opened NR4A3 LBD the whole rung is framed in.

THREE THINGS THIS RUNG FOUND THAT CHANGE HOW RUNG 5a's NUMBERS READ. All three are measurements, and each is
reproduced in the output JSON with the observation that forced it.

1. ★ `min_linker_atoms` IS A BEST-OF-N OVER A BASIN'S MEMBERS, AND THE MEMBER THAT ACHIEVES IT IS NOT THE
   BASIN'S PUBLISHED REPRESENTATIVE. At the representative placement of all five confirmed meta-basins the
   C397 requirement is 16-33 backbone atoms, against a reported 8-12. Nothing is wrong with the reported
   figure — it is the minimum over a few hundred sampled placements, exactly as documented, and the reach
   FRACTIONS (0.019-0.057) already say only 2-6 % of placements achieve it. But a chemist cannot build at a
   statistic. The search now emits the achieving placement itself (`exemplar_placement`), and this rung
   designs on it, reporting it as the OPTIMISTIC end of the basin.

2. ★ RUNG 5a's REACH CRITERION IS A LOWER BOUND, BECAUSE IT CREDITS THE PENDANT ARM WITH SHORTENING THE SPAN.
   `|q-a| + |q-b| <= L + 2e` reduces, for a nucleophile on the anchor-anchor segment, to `span <= L + 2e` —
   but the linker must physically connect a to b and needs `L >= span` however long the pendant is. The exact
   requirement (three balls, integer branch positions) is never shorter and is up to 2e ~ 5 backbone atoms
   longer. Audited over all 576 (basin x unique cysteine) records, no reported figure is internally
   impossible, so this is a bound, not an error — but 5b quotes the exact rule, and reports both.

3. ★ `best_linker_atoms = 19` ON 188 OF 192 BASINS IS A GRID EDGE, NOT AN OPTIMUM. 19 is the last point of
   the accessibility scan, and the mean-density profile is still rising there: for a 20 A span the true argmax
   is ~53 backbone atoms. Accessibility is recomputed here as `P(end-to-end distance in the basin's span
   window)` — dimensionless, comparable across basins, and with a genuine interior optimum.

WHAT A CONSTRUCT IN THE OUTPUT IS, AND IS NOT. It is a *predicted selective candidate*: an exact structure
with an exit-vector chemistry, a linker length and class, an electrophile position where one is carried, and a
retrosynthetic annotation. It is NOT a modelled complex, NOT an affinity, NOT a degradation prediction, and
carries no efficacy, safety, therapeutic-window or clinical claim. Everything is conditional on the
hypothesised cmpd19 binary pose x the chosen receptor frame — a double conditionality — and on one static
opened conformer per paralogue. The covalent handle is an unresolved liability, not an upgrade: electrophile
promiscuity cannot be checked without chemoproteomics, and it must be reported alongside the parent warhead's
published MYC induction.

Usage:
    python nr4a3_linker_design.py                 # writes research/modalities/nr4a3-linker-design.json
    python nr4a3_linker_design.py --self-test     # geometry-free consistency checks on the enumerator
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
sys.path.insert(0, HERE)

import basin_geom as G           # noqa: E402
import linker_design as LD       # noqa: E402
import nr4a3_basin_search as BS  # noqa: E402

UNIPROT_OFFSET = 372
RISE = LD.RISE_PER_ATOM_A

# The five meta-basins RUNG 5a confirmed on the definitive 12-pose run. Listed by ID because the artifact
# ranks 58 and the confirmed set is a decision, not a threshold — but every property used below is read from
# the artifact, never restated here.
CONFIRMED = ["crbn|M0", "vhl|M3", "vhl|M2", "vhl|M4", "vhl|M14"]

# ★★ AND THE IDS ARE POSITIONAL, WHICH MAKES THE LIST ABOVE A SILENT-WRONG-ANSWER PATH ON ITS OWN.
# A meta-basin's `Mn` index is its rank in a leader clustering of that run's accepted placements, so it is
# NOT stable across runs with different sampling: re-running the same search at 250 000 samples instead of
# 10^6 produced a `crbn|M0` whose interface patch shares almost nothing with the published one, and RUNG 5b
# designed against it without a murmur — 21.9 A exemplar span instead of 13.4, and the recommended matched
# pair silently moved from `crbn|M0` to `vhl|M2` (observed 2026-07-25). Nothing crashed; the answer was just
# a different basin's.
#
# The fix is an IDENTITY CHECK, not a re-selection. Each confirmed basin's published interface patch is
# recorded below, verbatim from `nr4a3-orientation-basins.json` as committed on 2026-07-25 (the definitive
# 12-pose, 10^6-sample run), and `run()` refuses if the artifact's basin of that name is not the same patch
# under the SAME Jaccard threshold the search itself uses to call two placements one meta-basin
# (`meta_basin_jaccard_cutoff` = 0.6). An id that resolves to a different surface patch is not the basin the
# confirmation decision was made about, and designing on it is worse than failing.
CONFIRMED_PATCH = {
    "crbn|M0": [389, 390, 391, 393, 394, 396, 400, 404, 407, 408, 412, 532, 572],
    "vhl|M3": [373, 390, 391, 393, 394, 396, 400, 404, 408, 572, 574],
    "vhl|M2": [391, 393, 394, 396, 400, 403, 404, 407, 412, 530, 531, 532, 572],
    "vhl|M4": [400, 487, 525, 528, 530, 531, 532, 572, 573, 574],
    "vhl|M14": [400, 403, 404, 407, 412, 530, 531, 532, 572, 573, 574],
}
CONFIRMED_PATCH_MIN_JACCARD = 0.6      # = BS.PARAMS["meta_basin_jaccard_cutoff"], asserted in the test suite

# Half-width of the accessibility window, in Angstrom, about the mechanism-carrying placement's span. Stated
# as a constant rather than tuned: 3.0 A is roughly one C-C bond either side of taut, i.e. the tolerance a
# linker has before it is either straining or slack. Every fidelity number below scales with it, so it is
# reported in the output and swept in the test suite rather than buried.
FIDELITY_WINDOW_A = 3.0

# ★ PREREGISTERED DOWNSELECT. Fixed BEFORE the library was enumerated and never tuned to a result — the same
# discipline the E3 downselect and the Tier-2 gate were held to. Thresholds, not a scalar score, because a
# tunable scalar is exactly what nr4a3-program-map.md's load-bearing piece 5 forbids.
MAX_STRAIN_KT = 3.0        # ~3 kT is the boundary between a slack chain and one fighting to reach
CHEM_MAX_ATOMS = 24        # chemically routine upper bound on a PROTAC linker backbone (PEG6-diacid scale)

FILTER = {
    "must_span_the_floor": True,      # hard: a linker shorter than the anchor-anchor distance is not a
                                      # candidate, it is an impossibility
    "min_member_fraction_comfortable": 0.25,   # must comfortably hold at least a quarter of the basin
    "max_strain_kT_at_placement": MAX_STRAIN_KT,
    "max_backbone_atoms": CHEM_MAX_ATOMS,
    "max_per_basin_per_kind": 2,      # diversity cap: no basin may flood the library with one pendant class
    "max_per_basin_per_control": 1,   # ... and each CONTROL gets its own slot, keyed on the pendant itself,
                                      # so the irreversible comparator cannot be crowded out by the
                                      # reversible electrophiles it exists to be compared against
    "controls_retained_when_matched": True,    # a control (irreversible comparator, saturated non-
                                      # electrophile, aza-scan phenyl) is kept when a DESIGN construct of the
                                      # same basin/warhead/body was kept — controls exist to match designs,
                                      # so keeping an unmatched one is noise and dropping a matched one
                                      # would leave the library unable to falsify itself
    "failing_basin_kept_as_labelled_negative": True,   # exactly one construct for the weak-control basin is
                                      # retained WITH its rejection reasons attached, so "the filter selects
                                      # good basins" is a testable claim rather than a tautology
}
# vhl|M14 does NOT exceed the term-(b) background and persists in only 3/12 poses. It is carried as a
# LABELLED WEAK CONTROL so the library contains a construct designed against a basin that failed the gate —
# without one, "the filter selects good basins" is unfalsifiable.
WEAK_CONTROL = "vhl|M14"

# ★★ BACKBONE LENGTH IS A SELECTIVITY COST, NOT ONLY A SYNTHESIS COST (LANE 13, 2026-07-25/26, $0).
# The matched-construct test — same placement, same warhead exit anchor, same E3 anchor, same budget, 5 657
# placements — measured P(a paralogue cysteine is ALSO reached | an NR4A3-unique one is) as a function of the
# linker's backbone length. It is 0 at the 12-atom gate and climbs steeply above it. Source:
# research/manuscripts/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md §3.3.
#
# ⚠ THREE THINGS THAT MUST TRAVEL WITH THESE NUMBERS, or they will be over-read:
#   1. FOUR MEASURED POINTS, NOTHING BETWEEN THEM. A construct at 13 atoms sits "between 0 and 0.000"; one at
#      18 sits "between 0.081 and 0.258". The bracket is the honest statement; interpolating a curve through
#      four points and quoting a value at 17 is not.
#   2. THIS IS THE REACH-ONLY PROBABILITY. Requiring the paralogue cysteine to be EXPOSED as well (RSA >= 0.25)
#      gives 0.000 at every length in these static models — so what currently holds the axis is exposure, and
#      exposure is one number per residue from one conformer. The matched paralogue MD ensembles that turn it
#      into a distribution were still in flight when this was written.
#   3. IT IS A COST, NOT A GATE. Nothing here is filtered on it; it is reported per construct so the trade is
#      visible where the design is made instead of being re-derived from prose.
PARALOGUE_COLLISION_BY_LINKER_ATOMS = {
    12: {"reach_only": 0.000, "reach_and_exposed": 0.000},
    14: {"reach_only": 0.000, "reach_and_exposed": 0.000},
    16: {"reach_only": 0.081, "reach_and_exposed": 0.000},
    20: {"reach_only": 0.258, "reach_and_exposed": 0.000},
}


def collision_bracket(n_atoms):
    """The measured paralogue-collision bracket for a construct of `n_atoms` backbone atoms.

    Returns the two MEASURED points the length falls between, never an interpolated value — see the warning
    on `PARALOGUE_COLLISION_BY_LINKER_ATOMS`. Below the shortest measured point the bracket is closed at that
    point; above the longest it is open, because the measurement stops there and the trend is rising.
    """
    xs = sorted(PARALOGUE_COLLISION_BY_LINKER_ATOMS)
    if n_atoms <= xs[0]:
        v = PARALOGUE_COLLISION_BY_LINKER_ATOMS[xs[0]]["reach_only"]
        return {"lo": v, "hi": v, "at": [xs[0], xs[0]], "reading": "at or below the %d-atom gate" % xs[0]}
    if n_atoms > xs[-1]:
        v = PARALOGUE_COLLISION_BY_LINKER_ATOMS[xs[-1]]["reach_only"]
        return {"lo": v, "hi": None, "at": [xs[-1], None],
                "reading": "beyond the longest measured point (%d atoms, %.3f) and the trend is rising — "
                           "UNBOUNDED above, not %.3f" % (xs[-1], v, v)}
    lo_x = max(x for x in xs if x <= n_atoms)
    hi_x = min(x for x in xs if x >= n_atoms)
    lo = PARALOGUE_COLLISION_BY_LINKER_ATOMS[lo_x]["reach_only"]
    hi = PARALOGUE_COLLISION_BY_LINKER_ATOMS[hi_x]["reach_only"]
    return {"lo": lo, "hi": hi, "at": [lo_x, hi_x],
            "reading": ("exactly %.3f (a measured point)" % lo if lo_x == hi_x else
                        "between %.3f (%d atoms) and %.3f (%d atoms) — NOT interpolated"
                        % (lo, lo_x, hi, hi_x))}

# Pendant reach: ONE definition, in `linker_design.PENDANT_REACH_A`, shared with the RUNG-5a term-(a) gate
# (CLAUDE.md 1: one fact, one place). It was duplicated here and in the gate, at which point the two rungs
# could have drifted apart silently. Read that table for what each entry is and why a sweep over NAMED
# building blocks is a sensitivity rather than a knob.
PENDANT_REACH = LD.PENDANT_REACH_A

# ---------------------------------------------------------------------------------------------------------
# Chemistry: fragments taken from staged artifacts and standard, named reagents.
# Every SMILES here is VERIFIED IN CI by RDKit (`--chem-check`, run inside triskit23/ternary-fep) against the
# reference cores below; the enumerator does not trust its own string concatenation.
# ---------------------------------------------------------------------------------------------------------

REFERENCE_CORES = {
    # the anchor warhead, verbatim from congeneric-warhead-series.json -> anchor.smiles
    "cmpd19": "COC(=O)c1c[nH]c2ccc(Br)cc12",
    "cmpd19_core": "COC(=O)c1c[nH]c2ccccc12",
    # VH032, the standard VHL PROTAC handle; the linker replaces its acetyl, which is the MZ1/ARV-771 vector
    "vh032": "CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)NC(=O)C)O",
    # pomalidomide, the standard CRBN handle; the linker goes on the 4-amino nitrogen
    "pomalidomide": "C1CC(=O)NC(=O)C1N2C(=O)C3=C(C2=O)C(=CC=C3)N",
}

# E3 handle: (prefix written from the handle outward, suffix that closes it, chemical anchor atom).
E3_HANDLE = {
    "vhl": {
        "name": "VH032 (des-acetyl), linker on the tert-leucine nitrogen",
        # ends at the tert-leucine NITROGEN; the assembler supplies the amide carbonyl. An earlier version
        # ended at `NC(=O)` and the assembler added a second one, silently producing an ALPHA-KETOAMIDE
        # instead of an amide in every construct — caught by reading the emitted SMILES, which is why the
        # emitted SMILES are read and RDKit-verified rather than assumed.
        "pre": "CC1=C(SC=N1)C2=CC=C(C=C2)CNC(=O)[C@@H]3C[C@H](CN3C(=O)[C@H](C(C)(C)C)N",
        "post": ")O",
        "anchor_atom": "tert-leucine amide N",
        "precedent": "the MZ1 / ARV-771 exit vector; the most-used VHL PROTAC attachment point",
        "coupling": "HATU or T3P amide coupling of the linker acid to the des-acetyl VH032 amine",
    },
    "crbn": {
        "name": "pomalidomide, linker on the 4-amino nitrogen",
        "pre": "C1CC(=O)NC(=O)C1N2C(=O)C3=C(C2=O)C(=CC=C3)N",
        "post": "",
        "anchor_atom": "4-amino N",
        "precedent": "the dBET/ARV-110-class CRBN attachment point",
        "coupling": "amide coupling of the linker acid to the 4-amino aniline (or SNAr on 4-fluorothalidomide)",
    },
}

# Warhead exit-vector handle: taken from the STAGED congeneric series, with the number of backbone atoms it
# contributes on the warhead side (counted from, and excluding, the C5 substituent atom, which IS the anchor).
WARHEAD_HANDLE = {
    "5amide": {
        "series_id": "cw_ev_5nh2",
        "name": "5-amino indole, linker acylates the aniline",
        "tail": "C(=O)Nc4ccc5[nH]cc(C(=O)OC)c5c4",
        "tail_atoms": 1,                       # the acyl carbon; the aniline N is the anchor
        "anchor_atom": "C5 aniline N",
        "coupling": "HATU amide coupling; 5-aminoindole esters are commercial",
    },
    "5triazole": {
        "series_id": "cw_ev_5opropargyl",
        "name": "5-O-propargyl indole, CuAAC to a linker azide (1,4-triazole)",
        "tail": "n4cc(COc5ccc6[nH]cc(C(=O)OC)c6c5)nn4",
        "tail_atoms": 4,                       # triazole N1,C5,C4 + the propargylic CH2; the C5-O is the anchor
        "anchor_atom": "C5 ether O",
        "coupling": "CuAAC (CuSO4/NaAsc); the propargyl ether is one O-alkylation from 5-hydroxyindole",
    },
    "5piperazine": {
        "series_id": "cw_ev_5piperazine",
        "name": "5-piperazinyl indole, linker acylates N4",
        "tail": "C(=O)N4CCN(c5ccc6[nH]cc(C(=O)OC)c6c5)CC4",
        "tail_atoms": 4,                       # acyl C + N4 + 2 ring carbons; the N1 on the ring is the anchor
        "anchor_atom": "C5 piperazine N1",
        "coupling": "Buchwald or SNAr to install the piperazine, then amide coupling",
    },
}

# Linker bodies, between the E3-side amide carbonyl and the warhead-side tail. Each is a catalogue-level
# building-block class; `n` is the number of backbone atoms it contributes.
#
# A construct is assembled as a short peptide-like chain, which is what makes both the branch node and the
# route honest:
#     E3-NH -C(=O)- [SEG1] -C(=O)-NH- CH(R) -C(=O)-NH- [SEG2] - <warhead tail>
# with the branch node omitted when there is no pendant. Writing the branch as an AMINO-ACID RESIDUE rather
# than as a substituent on an arbitrary backbone carbon fixes three things at once: the stereocentre becomes
# a defined (S) centre inherited from a catalogue L-amino acid instead of an unspecified one; the pendant is
# installed by standard orthogonal-protection chemistry rather than a bespoke route; and it avoids the
# alpha-alkoxy stereocentre the first version produced by branching a PEG carbon, which would have been both
# hard to make and configurationally fragile.
LINKER_SEGMENT = {
    "s0": {"smi": "", "n": 0, "class": "direct", "block": "-"},
    "a2": {"smi": "CC", "n": 2, "class": "alkyl", "block": "succinyl / beta-alanine unit"},
    "a3": {"smi": "CCC", "n": 3, "class": "alkyl", "block": "glutaryl / GABA unit"},
    "a5": {"smi": "CCCCC", "n": 5, "class": "alkyl", "block": "pimelic-type unit"},
    "a7": {"smi": "CCCCCCC", "n": 7, "class": "alkyl", "block": "azelaic-type unit"},
    "a9": {"smi": "CCCCCCCCC", "n": 9, "class": "alkyl", "block": "undecanedioic-type unit"},
    "a11": {"smi": "CCCCCCCCCCC", "n": 11, "class": "alkyl", "block": "tridecanedioic-type unit"},
    # ACYL-side PEG (SEG1 only): begins alpha to the amide carbonyl, i.e. a diglycolamide — a standard,
    # stable PROTAC linker motif.
    "e2": {"smi": "COCC", "n": 4, "class": "peg", "block": "PEG2 diglycolic unit", "acyl_only": True},
    "e3": {"smi": "COCCOCC", "n": 7, "class": "peg", "block": "PEG3 diglycolic unit", "acyl_only": True},
    "e4": {"smi": "COCCOCCOCC", "n": 10, "class": "peg", "block": "PEG4 diglycolic unit", "acyl_only": True},
    "e5": {"smi": "COCCOCCOCCOCC", "n": 13, "class": "peg", "block": "PEG5 diglycolic unit",
           "acyl_only": True},
    "e6": {"smi": "COCCOCCOCCOCCOCC", "n": 16, "class": "peg", "block": "PEG6 diglycolic unit",
           "acyl_only": True},
    "e7": {"smi": "COCCOCCOCCOCCOCCOCC", "n": 19, "class": "peg", "block": "PEG7 diglycolic unit",
           "acyl_only": True},
    # AMINE-side PEG (SEG2): two carbons before the first ether oxygen. Written this way deliberately —
    # placing an oxygen beta to an amide NITROGEN would make an N,O-acetal (N-CH2-O-), which is
    # hydrolytically labile and which the first version of this enumerator emitted in every branched
    # construct. Caught by reading the SMILES, not by the code.
    "m2": {"smi": "CCOCC", "n": 5, "class": "peg", "block": "2-(2-aminoethoxy)ethyl unit",
           "amine_only": True},
    "m3": {"smi": "CCOCCOCC", "n": 8, "class": "peg", "block": "PEG3 amino-acid unit", "amine_only": True},
    "m4": {"smi": "CCOCCOCCOCC", "n": 11, "class": "peg", "block": "PEG4 amino-acid unit",
           "amine_only": True},
}

# The branch node, when a pendant is carried: a single L-amino-acid residue contributing 3 backbone atoms
# (N, C-alpha, carbonyl C). The pendant hangs off C-alpha.
BRANCH_NODE_ATOMS = 3

# Pendant groups. The electrophiles are the design variable nr4a3-program-map.md names; the wedge groups are the
# matched-pair element for RUNG 5a-KS.
PENDANT = {
    # --- electrophiles, on the side chain of an L-2,4-diaminobutanoyl (Dab) branch residue, so the branch is
    #     Fmoc-L-Dab(Boc)-OH -- a catalogue building block with a DEFINED (S) centre -- and the electrophile
    #     is installed on its side-chain amine after Boc removal.
    "cyac_me": {
        "smi": "CCNC(=O)/C(C#N)=C/C",
        "kind": "electrophile",
        "reversible": True,
        "name": "beta-methyl alpha-cyanoacrylamide (reversible-covalent)",
        "reach_key": "dab_branch",
        "why": "REVERSIBLE-covalent by design (nr4a3-program-map.md 5b). The alpha-cyano group acidifies the adduct's "
               "alpha-proton so retro-Michael is fast; a beta-substituent slows the forward addition and "
               "speeds the reverse, which is what makes the class tunable. Reversibility is what preserves "
               "CATALYTIC TURNOVER — an irreversible adduct makes the degrader stoichiometric and forfeits "
               "the one property that makes a degrader worth building.",
        "route": "Knoevenagel condensation of the cyanoacetamide with acetaldehyde; the cyanoacetamide comes "
                 "from cyanoacetic acid and the branch amine.",
    },
    "cyac_ph": {
        "smi": "CCNC(=O)/C(C#N)=C/c1ccccc1",
        "kind": "electrophile",
        "reversible": True,
        "name": "beta-phenyl alpha-cyanoacrylamide (reversible-covalent, slower on-rate)",
        "reach_key": "dab_branch",
        "why": "The beta-aryl variant of the same class: more reversible and less reactive than beta-alkyl, "
               "so it is the residence-time tuning axis rather than a second mechanism.",
        "route": "Knoevenagel with benzaldehyde.",
    },
    "acrylamide": {
        "smi": "CCNC(=O)C=C",
        "kind": "electrophile",
        "reversible": False,
        "name": "acrylamide (IRREVERSIBLE — comparator only)",
        "reach_key": "dab_branch",
        "why": "Carried ONLY as the irreversible comparator the reversible design is argued against. An "
               "irreversible adduct converts the degrader into a stoichiometric binder. It is in the library "
               "so the reversible preference is a tested choice rather than an assertion.",
        "route": "acryloyl chloride or acrylic acid + coupling agent on the branch amine.",
    },
    "cyanoprop": {
        # ★ THE (S) TAG IS NOT COSMETIC. Reducing the Michael acceptor turns its sp2 alpha-carbon into an sp3
        # centre bearing four different groups — nitrile, amide, ethyl, H — so **the saturated control has a
        # stereocentre the electrophile does not have.** That is an unavoidable property of saturated
        # controls for Michael acceptors, not a flaw in this one, and it is the reason the pair is matched in
        # CONSTITUTION but not in STEREOCHEMISTRY. It is declared as a single (S) diastereomer rather than
        # left unspecified, because an unspecified centre would make the "control" two compounds; the (R)
        # epimer is an available second control and would be the obvious check that the centre does not
        # matter. RDKit refuses an unassigned centre, which is how this surfaced.
        "smi": "CCNC(=O)[C@@H](C#N)CC",
        "kind": "control",
        "reversible": None,
        "name": "2-cyanobutanamide (SATURATED, non-electrophilic control for cyac_me)",
        "reach_key": "dab_branch",
        "why": "The matched non-electrophilic control: cyac_me with the Michael acceptor reduced, and NOTHING "
               "ELSE changed. Same heavy atoms, same net charge, same nitrile, same amide, no electrophile — "
               "so any difference attributable to the warhead is attributable to the C=C and nothing else.",
        "route": "hydrogenation of cyac_me, or direct coupling of 2-cyanobutanoic acid.",
        "_correction": "this was alpha-cyano-PROPANamide (`CCNC(=O)C(C#N)C`) until a test compared its "
                       "skeleton to cyac_me's and found it ONE CARBON SHORT — it was missing the "
                       "beta-methyl, so it was not a matched control at all, and a difference between the "
                       "two would have been partly a methyl group rather than the alkene.",
    },
    # --- wedge elements for the RUNG 5a-KS matched pair, as the side chain of the branch residue. The pair
    #     is 3-(3-pyridyl)-L-alanine vs L-phenylalanine: two catalogue amino acids differing by ONE ATOM.
    "pyr3": {
        "smi": "Cc1cccnc1",
        "kind": "wedge",
        "reversible": None,
        "name": "3-(3-pyridyl)-L-alanine side chain (H-bond ACCEPTOR at the wedge site)",
        "reach_key": "aryl_branch_residue",
        "why": "The 'd' member of the matched pair. Its ring nitrogen is an acceptor for the Arg412 "
               "guanidinium that NR4A3 has and NR4A1 (Ala) and NR4A2 (Thr) do not.",
        "route": "Fmoc-3-(3-pyridyl)-L-alanine, a standard unnatural-amino-acid building block, coupled in "
                 "place of the Fmoc-L-Phe of the control.",
    },
    "ph": {
        "smi": "Cc1ccccc1",
        "kind": "wedge_control",
        "reversible": None,
        "name": "L-phenylalanine side chain (aza-scan CONTROL — same size, same charge, no acceptor)",
        "reach_key": "aryl_branch_residue",
        "why": "The 'd0' member. An aza-scan is the cleanest available matched pair: exactly one atom "
               "differs (an aromatic C-H becomes N), net charge, heavy-atom count and rotatable-bond count "
               "are identical, the stereocentre is the same (S), and the only property changed is the "
               "H-bond acceptor at the wedge site.",
        "route": "Fmoc-L-Phe-OH — as ordinary a building block as exists.",
    },
}


# ---------------------------------------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------------------------------------


def load_context(basins_path, registry_path, atlas_path, struct_path, series_path):
    basins = json.load(open(basins_path))
    registry = json.load(open(registry_path))
    atlas = json.load(open(atlas_path))
    series = json.load(open(series_path))
    model = BS.load_paralogue(struct_path)

    arms = {}
    for aid in ("vhl", "crbn"):
        rec = registry["arms"].get(aid)
        if rec is None:
            continue
        arm = BS.load_arm_from_registry(rec)
        arm["_landmarks"] = [arm["ca"][i] for i in G.farthest_point_sample(arm["ca"], 10)]
        arm["_e3_moiety_centroid"] = tuple(rec["ligand"]["e3_moiety_centroid"])
        arms[aid] = arm

    poses = {p["pose_id"]: p for p in basins["pose_ensemble"]}
    atlas_by_local = {r["local_resid"]: r for r in atlas["residues"]}
    return {"basins": basins, "registry": registry, "atlas": atlas_by_local, "series": series,
            "model": model, "arms": arms, "poses": poses}


def recover_transform(arm, landmarks, expect_anchor, tol=0.05):
    """Recover a placement's rigid transform from its 10 stored landmarks, and REFUSE if the recovery does not
    reproduce the placement's own recorded E3 anchor.

    This is the self-check that makes every exit-vector angle below trustworthy: the landmarks are E3 CA atoms
    and the anchor is the ligand exit atom, so reproducing the anchor from a fit to the landmarks is an
    independent confirmation that the recovered rotation is the one the search actually used. Measured on the
    committed artifact it reproduces to 0.002-0.008 A, limited only by the two-decimal rounding of the stored
    coordinates.
    """
    R, t, rms = G.horn_superpose(arm["_landmarks"], [tuple(p) for p in landmarks])
    got = G.apply_superpose([arm["anchor"]], R, t)[0]
    err = G.dist(got, tuple(expect_anchor))
    if err > tol:
        raise ValueError("landmark transform recovery failed: anchor off by %.3f A (tol %.3f). The stored "
                         "landmarks and anchor disagree; refusing rather than computing angles on a wrong "
                         "rotation." % (err, tol))
    return R, t, rms, err


# ---------------------------------------------------------------------------------------------------------
# Stage A — linker requirements per basin
# ---------------------------------------------------------------------------------------------------------


def reactive_sites(ctx):
    tf = ctx["basins"]["target_frame"]
    model = ctx["model"]
    out = {"unique_cysteines": {}, "unique_lysines": {}, "conserved_cysteines": {}}
    for c in tf["unique_cysteines"]:
        p = BS.atom_xyz(model, c["local_resid"], "SG")
        if p:
            out["unique_cysteines"]["C%d" % c["uniprot_resid"]] = {"xyz": p, "rsa": c["rsa"],
                                                                  "nr4a1": c["nr4a1_partner"],
                                                                  "nr4a2": c["nr4a2_partner"]}
    for k in tf["unique_lysines"]:
        p = BS.atom_xyz(model, k["local_resid"], "NZ")
        if p:
            out["unique_lysines"]["K%d" % k["uniprot_resid"]] = {"xyz": p, "rsa": k["rsa"]}
    unique = {c["local_resid"] for c in tf["unique_cysteines"]}
    for rid, aa in model["residues"]:
        if aa == "C" and rid not in unique:
            p = BS.atom_xyz(model, rid, "SG")
            if p:
                out["conserved_cysteines"]["C%d" % (rid + UNIPROT_OFFSET)] = {"xyz": p}
    return out


def wedge_sites(ctx, a, b, n_atoms, arm_reach):
    """Divergent, solvent-exposed target residues a LINKER SUBSTITUENT could touch at this placement.

    This is where a LIGAND-side wedge element can live, and it is a different set from the basin's interface
    patch: the patch is where the E3 BODY sits (the home of the marginal induced-interface wedge), whereas
    this is where the linker passes. RUNG 5a-KS's primary test is ligand-side, so it needs this set.
    """
    model, atlas = ctx["model"], ctx["atlas"]
    hits = []
    for rid, aa in model["residues"]:
        rec = atlas.get(rid)
        q = model["cb"].get(rid)
        if rec is None or q is None or not rec["exposed"] or not rec["divergent_vs_both"]:
            continue
        w = LD.branch_position_window(a, b, q, n_atoms, arm_reach)
        if w["n_feasible"]:
            hits.append({"uniprot_resid": rid + UNIPROT_OFFSET, "nr4a3": aa,
                         "nr4a1": rec["nr4a1"], "nr4a2": rec["nr4a2"],
                         "rsa": round(rec["rsa"], 3), "nonconservative": rec["nonconservative"],
                         "branch_k_min": w["k_min"], "branch_k_max": w["k_max"]})
    return hits


# Side chains that can donate an H-bond to a pyridyl-type acceptor. The wedge element in the matched pair is
# an H-BOND ACCEPTOR (an aza-scan), so the site it engages has to have a DONOR in NR4A3 and no donor in
# either paralogue — otherwise the pair is asking a nitrogen lone pair to discriminate two hydrocarbons,
# which it cannot do, and the wedge would be paying a desolvation penalty for nothing.
SIDECHAIN_HBOND_DONORS = set("STYNQKRHW")


def _wedge_chemistry_ok(site):
    """Is this site the right KIND of difference for an H-bond-acceptor wedge?

    Geometry alone picked Ile396 (Ile -> Ala/Val at 12.6 A of clearance) as the best site, which is the most
    E3-clear position available and the wrong chemistry: a pyridyl nitrogen against an isoleucine is a
    desolvation cost with no compensating interaction, in NR4A3 *and* in both paralogues, so the double
    difference would be near zero by construction. The rule is preregistered and it is one line of chemistry:
    NR4A3 must present a donor and BOTH paralogues must not.
    """
    return (site["nr4a3"] in SIDECHAIN_HBOND_DONORS
            and site["nr4a1"] not in SIDECHAIN_HBOND_DONORS
            and site["nr4a2"] not in SIDECHAIN_HBOND_DONORS)


def select_wedge_site(sites):
    """★★ THE ONE PLACE THE WEDGE SITE IS CHOSEN — for the ENUMERATOR and for the PAIR SELECTOR alike.

    ⚠ THIS FUNCTION EXISTS BECAUSE THE TWO DISAGREED, AND THE DISAGREEMENT REACHED THE RECOMMENDED PAIR
    (found 2026-07-26, LANE 14, on the corrected 10^6 artifact). The preregistered wedge chemistry rule was
    made binding in `matched_pair` but NOT in `enumerate_library`, which went on selecting the site with the
    most E3 clearance. The result was a pair record whose `wedge_target_residue` said **T407** while its own
    `d`/`d0` molecules had been built with the pyridyl aimed at **C397** — a residue that is ASPARAGINE in
    NR4A1 and SERINE in NR4A2, i.e. both paralogues keep an H-bond partner, which is exactly the "S is ~0 by
    construction" trap the rule was written to prevent (and worse: the paralogue may make the BETTER contact).
    Nothing failed; the metadata simply described a different molecule from the one emitted. Measured over the
    corrected artifact, the two selections disagreed on **8 of 10** (basin x placement) records.

    The fix is one selector, not two agreeing conventions — an agreeing convention is what just drifted.

    Two filters, both preregistered:
      * `e3_clear_enough_for_a_matched_pair` — the wedge must not touch the E3, or the shared ligand-E3 leg
        stops cancelling and `S` stops isolating a target-side interaction;
      * `_wedge_chemistry_ok` — NR4A3 presents a side-chain H-bond donor and BOTH paralogues do not.
    Among survivors, the most E3-clear site wins. C397 is excluded explicitly as well: it is the CATEGORICAL
    handle's cysteine, and putting the marginal wedge on it would conflate the two mechanisms the program is
    at pains to keep separable. (Cys is not in `SIDECHAIN_HBOND_DONORS`, so the chemistry rule already
    excludes it; the explicit test states the intent rather than relying on that coincidence.)
    """
    clean = [s for s in sites
             if s.get("e3_clear_enough_for_a_matched_pair")
             and s["uniprot_resid"] != 397
             and _wedge_chemistry_ok(s)]
    return max(clean, key=lambda s: s["e3_clearance_A"]) if clean else None


def e3_clearance(arm, R, t, point):
    """Distance from `point` to the nearest atom of the placed E3 body (CA + side-chain centroids).

    THE LOAD-BEARING CHECK FOR THE MATCHED PAIR. `S` is meant to isolate a TARGET-side interaction. If the
    wedge element sits close enough to touch the E3, then d and d0 differ in their ligand-E3 contact as well,
    the shared binary leg no longer cancels, and the double difference stops answering the design question.
    """
    pts = G.apply_superpose(arm["query"], R, t)
    return min(G.dist(point, p) for p in pts)


def _member_basin(ctx, aid, basin_id):
    """The per-pose member basin a placement came from — it carries that basin's span distribution.

    ★ WHY THIS IS LOOKED UP PER PLACEMENT AND NOT ONCE PER META-BASIN. The representative and the term-(a)
    exemplar routinely come from DIFFERENT member basins, in different poses, with different span deciles. The
    first version of this rung read the representative's member basin and reused its span distribution for the
    exemplar's accessibility, which quietly mixed one placement's geometry with another placement's basin.
    """
    for pp in ctx["basins"]["arms"][aid]["per_pose"]:
        for bb in pp["basins"]:
            if bb["basin_id"] == basin_id:
                return bb
    return None


def requirements_at_placement(ctx, meta, sites, placement, label):
    """Everything a chemist needs about ONE PLACEMENT of one confirmed basin, before any molecule is drawn.

    `placement` is a dict carrying at least {basin_id, pose_id, anchor_e3_xyz, landmarks} — the shape both the
    basin's `representative` and its `term_a_union.C397.exemplar_placement` already have. Running the identical
    derivation at either is the point: RUNG 5b's own finding was that the placement achieving a basin's
    reported minimum is NOT its representative, so the requirements have to be derivable at both and the two
    have to be comparable line for line.

    `label` is either "representative" (a typical member of the basin) or "term_a_exemplar" (the member with
    the shortest EXACT C397 requirement — a best-of-N, so the OPTIMISTIC end of the basin). Neither may be
    quoted without saying which, and the caller enumerates a separate library against each.
    """
    aid = meta["arm_id"]
    arm = ctx["arms"][aid]
    basin_id = placement["basin_id"]
    pose_id = placement["pose_id"]
    pose = ctx["poses"][pose_id]
    a = tuple(pose["anchor_xyz"])
    u = tuple(pose["exit_direction"])
    R, t, rms, err = recover_transform(arm, placement["landmarks"], placement["anchor_e3_xyz"])
    b = G.apply_superpose([arm["anchor"]], R, t)[0]
    # The E3 ligand leaves its own moiety heading away from that moiety's centroid; rotate that direction into
    # the target frame. Directions rotate; they do not translate.
    v = G.matvec(R, G.sub(arm["anchor"], arm["_e3_moiety_centroid"]))

    geo = LD.exit_vector_geometry(a, u, b, v)
    floor = LD.span_floor_atoms(a, b)

    member = _member_basin(ctx, aid, basin_id)
    spans = member["span_A"] if member else {"min": geo["span_A"], "median": geo["span_A"],
                                             "max": geo["span_A"]}
    deciles = (member or {}).get("span_A_deciles")

    # ★ ACCESSIBILITY, GOT RIGHT ON THE THIRD ATTEMPT. Two wrong framings were tried and are recorded here
    # because each was wrong for a different, instructive reason.
    #   (1) The mean WLC DENSITY over the basin's member spans (RUNG 5a's own quantity) is the right FORM —
    #       it is the likelihood of the basin's spans under the linker's end-to-end distribution — but its
    #       argmax was censored at the top of a scan that stopped at 19 atoms.
    #   (2) A PROBABILITY integrated over the basin's [min, max] span range fixes the units and the censoring
    #       but is nearly vacuous: a basin is an INTERFACE PATCH, not a span class, so its members' spans run
    #       from ~5 to ~25 A, and integrating over that window just rewards long chains. It returned an
    #       "optimum" of 34-39 atoms for every basin, which is not a design answer.
    # What a chemist needs is neither: it is the fraction of the basin's members a linker of length n can
    # actually reach WITHOUT STRAINING, plus the strain at the specific placement being designed on. Both are
    # reported below. The unconstrained entropic optimum is ALSO reported, precisely so it can be seen to be
    # a bad design target — for a 23 A span it is 74 backbone atoms.
    tol = FIDELITY_WINDOW_A
    centre = geo["span_A"]
    n_best, p_best, meta_acc = LD.wlc_best_length(max(0.5, centre - tol), centre + tol, range(4, 81))
    # ★ THE SPAN DISTRIBUTION IS THE DECILES WHEN THE ARTIFACT CARRIES THEM. The 3-point {min, median, max}
    # stand-in below is a fallback for pre-decile artifacts ONLY, and it is a bad one: repeating the median
    # four times makes every coverage number a step function with three risers, so a length that clears the
    # median jumps from 0.3 to 0.7 with nothing in between. It is kept so an old artifact still runs, and it
    # labels itself in the output.
    span_dist = deciles if deciles else [spans["min"], spans["min"], spans["min"], spans["median"],
                                         spans["median"], spans["median"], spans["median"],
                                         spans["max"], spans["max"], spans["max"]]
    n_comfortable = next((n for n in range(4, 81) if LD.wlc_strain_kt(centre, n) <= MAX_STRAIN_KT), None)

    reach = {}
    for lab, cys in sites["unique_cysteines"].items():
        per_e = {}
        for ename, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
            per_e[ename] = {
                "arm_reach_A": e,
                "relaxed_rung5a_atoms": LD.min_linker_atoms_relaxed(a, b, cys["xyz"], e),
                "exact_atoms": LD.min_linker_atoms_exact(a, b, cys["xyz"], e, n_max=80),
            }
        reach[lab] = {
            "dist_to_warhead_anchor_A": round(G.dist(cys["xyz"], a), 2),
            "dist_to_e3_anchor_A": round(G.dist(cys["xyz"], b), 2),
            "focal_sum_A": round(G.dist(cys["xyz"], a) + G.dist(cys["xyz"], b), 2),
            "detour_over_span_A": round(G.dist(cys["xyz"], a) + G.dist(cys["xyz"], b) - geo["span_A"], 2),
            "by_pendant": per_e,
            "reported_by_rung5a": meta["term_a_union"].get(lab, {}).get("min_linker_atoms"),
            "reported_by_rung5a_relaxed_superseded": meta["term_a_union"].get(lab, {}).get(
                "min_linker_atoms_relaxed_superseded"),
        }

    # conserved-cysteine chemoselectivity counter-check: a longer pendant relaxes reach to EVERY cysteine
    conserved = {}
    for ename, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
        n_probe = floor + 6
        conserved[ename] = sorted(
            lab for lab, c in sites["conserved_cysteines"].items()
            if LD.pendant_contactable(a, b, c["xyz"], n_probe, e))

    n_design = floor + 4
    wedges = wedge_sites(ctx, a, b, n_design, PENDANT_REACH["aryl_branch_residue"])
    for w in wedges:
        q = ctx["model"]["cb"][w["uniprot_resid"] - UNIPROT_OFFSET]
        k = max(1, (w["branch_k_min"] + w["branch_k_max"]) // 2)
        _, p = LD.three_ball_min_margin([a, b, q], [k * RISE, (n_design - k) * RISE,
                                                    PENDANT_REACH["aryl_branch_residue"]])
        w["e3_clearance_A"] = round(e3_clearance(arm, R, t, p), 2)
        w["e3_clear_enough_for_a_matched_pair"] = w["e3_clearance_A"] >= 6.0

    return {
        "meta_basin_id": meta["meta_basin_id"],
        "arm_id": aid,
        "placement_label": label,
        "role": ("LABELLED WEAK CONTROL — does NOT exceed the term-(b) background and persists in only "
                 "%d/%d poses; carried so the filter has something it should reject"
                 % (meta["n_poses_present"], meta["n_poses_total"])
                 if meta["meta_basin_id"] == WEAK_CONTROL else "design target"),
        "pose_surviving_fraction": meta["pose_surviving_fraction"],
        "term_b_exceeds_background": meta["term_b_exceeds_background"],
        "term_b_max_enrichment_over_background": meta["term_b_max_enrichment_over_background"],
        "term_b_mean_fraction_paralogues_bare": meta["term_b_mean_fraction_paralogues_bare"],
        "designed_on": {
            "placement": label,
            "basin_id": basin_id,
            "pose_id": pose_id,
            "transform_recovery_rms_A": round(rms, 4),
            "anchor_reproduction_error_A": round(err, 4),
            "_caveat": ("the representative is the highest-scoring member of the largest member basin, NOT "
                        "the member that achieves the basin's reported minimum linker length — so the "
                        "requirements here are those of a TYPICAL member of the basin."
                        if label == "representative" else
                        "the term-(a) exemplar is the member needing the SHORTEST EXACT linker to C397. It "
                        "is a best-of-N over the basin's sampled members, so these requirements are the "
                        "OPTIMISTIC end of the basin. The truth for any real molecule lies between this and "
                        "the representative, and neither may be quoted without saying which."),
        },
        "endpoint_distance": {
            "placement_span_A": geo["span_A"],
            "representative_span_A": geo["span_A"],   # legacy alias; the label above says which placement
            "member_span_A": spans,
            "member_span_deciles_A": deciles,
            "span_floor_atoms": floor,
            "_reading": "the span floor is the number of backbone atoms needed merely to CONNECT the two "
                        "anchors. No pendant, and no electrophile, can substitute for it.",
        },
        "exit_vector_geometry": geo,
        "accessibility": {
            "window_centre_A": centre,
            "window_half_width_A": tol,
            "span_distribution_used": ("member span deciles" if deciles else
                                       "3-POINT APPROXIMATION from {min, median, max} — the artifact "
                                       "predates the decile field; re-run against a basin file carrying "
                                       "`span_A_deciles` to replace it"),
            "n_atoms_for_comfortable_span": n_comfortable,
            "_comfortable_definition": "smallest backbone-atom count whose worm-like-chain strain at this "
                                       "placement's span is <= %.1f kT" % MAX_STRAIN_KT,
            "member_coverage_by_n": {
                str(n): {
                    "fraction_spannable": round(sum(1 for s in span_dist if s <= n * RISE)
                                                / len(span_dist), 2),
                    "fraction_comfortable": round(
                        sum(1 for s in span_dist if LD.wlc_strain_kt(s, n) <= MAX_STRAIN_KT)
                        / len(span_dist), 2),
                }
                for n in range(6, 41, 2)
            },
            "_member_coverage_reading": "the fraction of THIS basin's member placements a linker of that "
                                        "length can reach. A basin is a region, so a short linker does not "
                                        "fail it outright — it accesses the small-span tail of it. This is "
                                        "the honest form of 'can the linker hold this basin'.",
            "strain_kT_at_placement_span": {
                str(n): round(LD.wlc_strain_kt(centre, n), 2)
                for n in range(max(4, floor), min(41, floor + 20))
            },
            "unconstrained_entropic_optimum": {
                "n_atoms": n_best,
                "probability": round(p_best, 4),
                "at_scan_boundary": meta_acc["at_boundary"],
                "_warning": "NOT a design recommendation. Maximising chain accessibility alone drives the "
                            "linker to 40-80 backbone atoms, because the entropically optimal chain is the "
                            "one whose most probable end-to-end distance equals the span. It is reported so "
                            "the trade-off against permeability, synthetic tractability and the ternary "
                            "assembly's own entropy is visible rather than implicit.",
            },
            "rung5a_reported_best_linker_atoms": meta["best_linker_atoms"],
            "_correction": "RUNG 5a's `best_linker_atoms` is the argmax of a mean DENSITY over a scan that "
                           "stops at 19, and it reads 19 on 188 of 192 basins because the profile is still "
                           "rising there — a grid edge, not an optimum.",
        },
        "electrophile_reach": reach,
        "conserved_cysteine_reach_by_pendant": {
            "_reading": "a longer pendant relaxes reach to EVERY cysteine, not only the unique one. The "
                        "paralogue argument is unaffected (NR4A1/NR4A2 carry no nucleophile at the aligned "
                        "positions at all, by sequence), but INTRA-NR4A3 chemoselectivity degrades, and that "
                        "is a liability of a long pendant that has to be stated with the reach it buys.",
            "by_pendant": conserved,
            "probe_linker_atoms": floor + 6,
        },
        "wedge_element_sites": {
            "_reading": "solvent-exposed residues that differ from BOTH paralogues and lie within pendant "
                        "reach of the linker path — i.e. where a LIGAND-side wedge element can sit. Distinct "
                        "from the basin's interface patch, which is where the E3 BODY sits. Recomputed at "
                        "THIS placement: nothing guarantees the residues a linker substituent can touch are "
                        "the same at the representative and at the exemplar.",
            "probe_linker_atoms": n_design,
            "sites": wedges,
        },
        "interface_patch_uniprot": meta["interface_patch_uniprot"],
        "_a": a,
        "_b": b,
        # ★ THE PLACED E3 BODY, KEPT SO CLEARANCE CAN BE RE-MEASURED AT A CONSTRUCT'S OWN (n, k).
        # `wedge_element_sites[*].e3_clearance_A` is a PROBE value: it is measured at `n_design = floor + 4`
        # with k at the middle of that site's window, because the sites are derived before any molecule
        # exists. The molecule finally proposed has its own length and its own branch position, and the
        # clearance is a property of where THAT branch atom lands. Reporting the probe value against a
        # different molecule is the same class of mismatch as the wedge-site drift above, so the pair now
        # re-measures. Popped before serialisation (it is a closure).
        "_clearance_at": lambda p: e3_clearance(arm, R, t, p),
    }


def basin_requirements(ctx, meta, sites):
    """The two requirement records for one confirmed basin: at its representative, and at its term-(a)
    exemplar. Returns (representative_record, exemplar_record_or_None).

    ★★ WHY BOTH, AND WHY THE EXEMPLAR IS THE ONE THE LIBRARY IS BUILT ON. The representative is the
    highest-scoring member of the largest member basin; the member that achieves the basin's reported C397
    minimum is a different placement entirely, in a different pose, and it is the one a covalent construct has
    to be built on. Designing at the representative produced 16-33-atom requirements that were an artifact of
    the wrong placement, not a property of the basin. Designing ONLY at the exemplar would be the opposite
    error — it is a best-of-N, so its requirements are optimistic. Both records are emitted, a full library is
    enumerated against each under the identical preregistered filter, and the difference between the two
    libraries is itself the honest measure of how much the answer depends on which member you design at.
    """
    rep = dict(meta["representative"])
    rep["basin_id"] = meta["representative_basin_id"]
    rep["pose_id"] = meta["representative_basin_id"].split("|")[1]
    rec_rep = requirements_at_placement(ctx, meta, sites, rep, "representative")

    ex_rec = (meta["term_a_union"].get("C397") or {}).get("exemplar_placement")
    rec_ex = None
    if ex_rec:
        rec_ex = requirements_at_placement(ctx, meta, sites, ex_rec, "term_a_exemplar")
        rec_ex["exemplar_source"] = {
            "exact_atoms_reported_by_rung5a": ex_rec.get("exact_atoms"),
            "focal_sum_A": ex_rec.get("focal_sum_A"),
            "span_A": ex_rec.get("span_A"),
            "_what": "the sampled member of this basin needing the shortest EXACT linker to C397. A "
                     "best-of-N member, so the OPTIMISTIC end of the basin, and it must be quoted as such.",
        }
        # The branch-position window for a Dab-type pendant onto C397, at the lengths a chemist would consider
        # — the design variable nr4a3-program-map.md's RUNG 5b asks for by name, at the placement that carries the
        # mechanism.
        floor_e = rec_ex["endpoint_distance"]["span_floor_atoms"]
        cys = sites["unique_cysteines"]["C397"]["xyz"]
        rec_ex["branch_window_dab_pendant"] = {
            str(n): (lambda w: {"k_min": w["k_min"], "k_max": w["k_max"], "best_k": w["best_k"]})(
                LD.branch_position_window(rec_ex["_a"], rec_ex["_b"], cys, n, PENDANT_REACH["dab_branch"]))
            for n in range(max(4, floor_e), floor_e + 9, 2)
        }
    return rec_rep, rec_ex


# ---------------------------------------------------------------------------------------------------------
# Stage B — the virtual library
# ---------------------------------------------------------------------------------------------------------


def build_smiles(e3_key, wh_key, seg1_key, seg2_key=None, pendant=None):
    """Assemble one construct as the peptide-like chain

        E3-NH -C(=O)- [SEG1] -C(=O)-NH- CH(pendant) -C(=O)-NH- [SEG2] - <warhead tail>

    with the branch residue and SEG2 omitted when there is no pendant, giving the plain

        E3-NH -C(=O)- [SEG1] - <warhead tail>.

    Returns (smiles, n_backbone_atoms, k_from_warhead_of_the_branch_alpha_carbon).

    Written E3-first so both E3 handles can be pasted verbatim from their reference SMILES; ring-closure
    digits are partitioned (E3 1-3, warhead 4-6, pendant 7-9) so no fragment can capture another's ring bond.
    """
    e3, wh = E3_HANDLE[e3_key], WARHEAD_HANDLE[wh_key]
    s1 = LINKER_SEGMENT[seg1_key]
    if pendant is None:
        if s1.get("amine_only"):
            raise ValueError("segment %r is amine-side only" % seg1_key)
        smi = e3["pre"] + "C(=O)" + s1["smi"] + wh["tail"] + e3["post"]
        return smi, 1 + s1["n"] + wh["tail_atoms"], None
    s2 = LINKER_SEGMENT[seg2_key]
    if s1["n"] == 0:
        raise ValueError("a branch residue needs an acyl segment on its N-terminal side")
    if s1.get("amine_only"):
        raise ValueError("segment %r is amine-side only; on the acyl side it would not be a diglycolamide"
                         % seg1_key)
    if s2.get("acyl_only"):
        raise ValueError("segment %r placed after an amide N would make an N,O-acetal (N-CH2-O-)"
                         % seg2_key)
    if s2["n"] == 0:
        # the branch residue's C-terminal amide N would sit directly on the warhead tail's own carbonyl,
        # making an ACYLUREA (C(=O)-N-C(=O)-N) rather than two amides. A third motif the assembler emitted
        # silently before the SMILES were read.
        raise ValueError("the branch residue needs at least one atom between its C-terminal amide and the "
                         "warhead tail, or the two carbonyls form an acylurea")
    node = "C(=O)N[C@@H](%s)C(=O)N" % _renumber(PENDANT[pendant]["smi"], 7)
    smi = e3["pre"] + "C(=O)" + s1["smi"] + node + s2["smi"] + wh["tail"] + e3["post"]
    n = 1 + s1["n"] + 1 + BRANCH_NODE_ATOMS + 1 + s2["n"] + wh["tail_atoms"]
    # Index of the branch alpha-carbon counted from the E3 end: the E3 acyl C (1), SEG1, the second acyl C,
    # then the residue's N, then C-alpha.
    k_e3 = 1 + s1["n"] + 1 + 2
    # ★ AND THE CONVERSION TO THE WAREHEAD-END INDEX IS n + 1 - k_e3, NOT n - k_e3. Both indices count the
    # branch atom ITSELF, so an atom that is the i-th from one end is the (n + 1 - i)-th from the other; the
    # first version dropped the +1 and put every electrophile one backbone atom too close to the warhead.
    # The self-test now asserts k_warhead + k_e3 == n + 1, which is an identity no formula error can satisfy
    # by accident, rather than restating the formula being tested.
    return smi, n, n + 1 - k_e3


def _renumber(frag, base):
    """Shift a fragment's ring-closure digits into a private range so it cannot capture another fragment's
    ring bond. Only single-digit closures appear in this module's fragments; anything else is refused rather
    than silently mangled."""
    out = []
    for ch in frag:
        if ch.isdigit():
            d = int(ch) + base - 1
            if d > 9:
                raise ValueError("ring-closure digit overflow renumbering %r" % frag)
            out.append(str(d))
        else:
            out.append(ch)
    return "".join(out)


def enumerate_library(reqs, ctx):
    """Enumerate constructs against each basin's derived requirements, then filter by basin fidelity.

    ENUMERATION IS PER BASIN, NOT A BLIND CROSS-PRODUCT. A construct only exists if its length is compatible
    with the basin it was drawn for; a molecule that cannot span its own basin is not a candidate, it is
    noise, and enumerating it and then filtering it would inflate the library's apparent size.
    """
    by_id = {r["meta_basin_id"]: r for r in reqs}
    lib = []
    for r in reqs:
        aid = r["arm_id"]
        floor = r["endpoint_distance"]["span_floor_atoms"]
        # ★ THE SPAN WINDOW CARRIED ON EVERY CONSTRUCT IS THE DECILES, NOT {min, median, max} (2026-07-25).
        # The 3-point form was a stand-in from before the basin search emitted deciles, and it is the one
        # place in this rung where a construct's reported span window disagreed with the distribution its own
        # fidelity numbers were computed over. Deciles when the artifact has them; the 3-point summary is
        # kept alongside so nothing that read it breaks.
        spans = {"deciles_A": r["endpoint_distance"].get("member_span_deciles_A"),
                 "summary_A": r["endpoint_distance"]["member_span_A"],
                 "_source": r["accessibility"]["span_distribution_used"]}
        # Every length the body x handle grid can actually produce, between the basin's span floor and the
        # chemically routine cap. No hand-picked ladder: the filter, not the enumerator, decides what is
        # viable, so the rejected set stays informative.
        wanted = set(range(floor, CHEM_MAX_ATOMS + 1))
        # The wedge site this basin can carry, if any. ★ SELECTED BY THE SHARED `select_wedge_site`, which
        # applies the PREREGISTERED chemistry rule as well as the clearance test — see its docstring for the
        # defect that made sharing mandatory. A basin with no chemistry-valid site now enumerates NO pyr3/ph
        # constructs at all, which is the correct answer: an aza-scan aimed at a site where both paralogues
        # keep the same partner is not a weak wedge, it is a wedge that cannot report.
        wedge_site = select_wedge_site(r["wedge_element_sites"]["sites"])
        wedge_xyz = (ctx["model"]["cb"][wedge_site["uniprot_resid"] - UNIPROT_OFFSET]
                     if wedge_site else None)

        for wh_key, wh in WARHEAD_HANDLE.items():
            # --- unbranched constructs
            for s1 in LINKER_SEGMENT:
                if LINKER_SEGMENT[s1]["n"] == 0 or LINKER_SEGMENT[s1].get("amine_only"):
                    continue
                smi, n_bb, _ = build_smiles(aid, wh_key, s1)
                if n_bb not in wanted:
                    continue
                lib.append(_record(r, aid, wh_key, s1, None, "none", None, None, smi, n_bb, spans,
                                   basin_fidelity(n_bb, r, by_id), None))
            # --- branched constructs: the branch residue's alpha-carbon must land inside the geometric
            #     window for the site the pendant is meant to touch.
            for pkey, target, reach_key in (
                    [(p, ctx["_c397"], "dab_branch") for p in
                     ("cyac_me", "cyac_ph", "acrylamide", "cyanoprop")]
                    + ([(p, wedge_xyz, "aryl_branch_residue") for p in ("pyr3", "ph")] if wedge_xyz else [])):
                reach = PENDANT_REACH[reach_key]
                for s1 in LINKER_SEGMENT:
                    if LINKER_SEGMENT[s1]["n"] == 0 or LINKER_SEGMENT[s1].get("amine_only"):
                        continue
                    for s2 in LINKER_SEGMENT:
                        if LINKER_SEGMENT[s2].get("acyl_only") or LINKER_SEGMENT[s2]["n"] == 0:
                            continue
                        try:
                            smi, n_bb, k = build_smiles(aid, wh_key, s1, s2, pkey)
                        except ValueError:
                            continue
                        if n_bb not in wanted or k is None or k < 1 or k >= n_bb:
                            continue
                        w = LD.branch_position_window(r["_a"], r["_b"], target, n_bb, reach)
                        if k not in w["feasible_k"]:
                            continue
                        lib.append(_record(r, aid, wh_key, s1, s2, pkey, k, w, smi, n_bb, spans,
                                           basin_fidelity(n_bb, r, by_id),
                                           wedge_site if reach_key == "aryl_branch_residue" else None))
    return lib


def _record(r, aid, wh_key, s1, s2, pkey, k, window, smi, n_bb, spans, fid, wedge_site):
    cls = LINKER_SEGMENT[s1]["class"] if s2 is None else "%s+%s" % (
        LINKER_SEGMENT[s1]["class"], LINKER_SEGMENT[s2]["class"])
    return {
        # The placement is part of the identity: the same basin yields DIFFERENT molecules at its
        # representative and at its term-(a) exemplar, and two constructs that differ in geometry must not
        # collide on one id.
        "construct_id": "%s@%s_%s_%s%s_%s" % (r["meta_basin_id"].replace("|", ""),
                                              "ex" if r["placement_label"] == "term_a_exemplar" else "rep",
                                              wh_key, s1, "" if s2 is None else "-" + s2, pkey),
        "designed_for_basin": r["meta_basin_id"],
        "designed_at_placement": r["placement_label"],
        "placement_basin_id": r["designed_on"]["basin_id"],
        "placement_pose_id": r["designed_on"]["pose_id"],
        "basin_role": r["role"],
        "e3_handle": aid, "warhead_handle": wh_key,
        "linker_segments": [s1] if s2 is None else [s1, s2],
        "linker_class": cls,
        "n_backbone_atoms_intended": n_bb,
        "pendant": pkey,
        "pendant_kind": PENDANT[pkey]["kind"] if pkey != "none" else "none",
        "branch_residue": (None if pkey == "none" else
                           ("Fmoc-L-Dab(Boc)-OH" if PENDANT[pkey]["reach_key"] == "dab_branch"
                            else "Fmoc-L-Phe-OH / Fmoc-3-(3-pyridyl)-L-Ala-OH")),
        "stereocentre": (None if pkey == "none" else
                         "(S) at the branch alpha-carbon, inherited from the L-amino-acid building block"),
        "branch_k_from_warhead": k,
        "branch_target": ("C397 SG" if pkey in ("cyac_me", "cyac_ph", "acrylamide", "cyanoprop")
                          else ("%s%d" % (wedge_site["nr4a3"], wedge_site["uniprot_resid"])
                                if wedge_site else None)),
        "branch_window": ({"k_min": window["k_min"], "k_max": window["k_max"], "best_k": window["best_k"]}
                          if window else None),
        "smiles": smi,
        "span_window_A": spans,
        "basin_fidelity": fid,
        "synthetic_route": synthetic_annotation(aid, wh_key, s1, s2, pkey),
    }


def _coverage(req, n_atoms):
    cov = req["accessibility"]["member_coverage_by_n"]
    key = str(min(40, max(6, n_atoms - (n_atoms % 2))))
    return cov.get(key, {"fraction_spannable": 0.0, "fraction_comfortable": 0.0})


def basin_fidelity(n_atoms, req, by_id):
    """Does this linker length reach THIS basin, and does it reach it PREFERENTIALLY?

    Four numbers, kept separate on purpose (nr4a3-program-map.md load-bearing piece 4 says accessibility and stability
    must not be merged; the same logic applies inside accessibility itself):

      * `member_fraction_comfortable` — the fraction of the basin's member placements this length can hold at
                        <= MAX_STRAIN_KT. The primary accessibility number, because a basin is a REGION: a
                        short linker does not fail a wide basin outright, it accesses its small-span tail.
      * `strain_kT_at_placement_span` — the chain cost at the specific placement being designed on.
      * `selectivity_vs_other_confirmed_basins` — comfortable coverage of THIS basin divided by the mean over
                        the others. **The number that decides whether the LENGTH is doing any discriminating
                        work at all.** A linker that fits every basin equally nominates none of them, and
                        without this column a library would look basin-specific merely because it was
                        labelled that way. Capped and accompanied by the raw coverages, because when the
                        other basins are genuinely unreachable the ratio diverges and a divergent ratio is
                        not a finding.
      * `P_reach_normalised` — coverage relative to the best any enumerable length achieves for this basin.
    """
    here = _coverage(req, n_atoms)
    cov = here["fraction_comfortable"]
    floor = req["endpoint_distance"]["span_floor_atoms"]
    best = max(_coverage(req, n)["fraction_comfortable"] for n in range(6, 41, 2))
    others = []
    for oid, o in by_id.items():
        if oid != req["meta_basin_id"]:
            others.append(_coverage(o, n_atoms)["fraction_comfortable"])
    mean_other = sum(others) / len(others) if others else 0.0
    if mean_other > 0:
        sel = round(cov / mean_other, 2)
        sel_note = None
    elif cov > 0:
        sel = None
        sel_note = "no other confirmed basin is reachable at this length at all"
    else:
        sel = None
        sel_note = "this length reaches no confirmed basin comfortably"
    return {
        "member_fraction_spannable": here["fraction_spannable"],
        "member_fraction_comfortable": cov,
        "P_reach_normalised": round(cov / best, 3) if best > 0 else 0.0,
        "selectivity_vs_other_confirmed_basins": sel,
        "selectivity_note": sel_note,
        "other_basin_mean_coverage": round(mean_other, 3),
        "strain_kT_at_placement_span": round(LD.wlc_strain_kt(req["accessibility"]["window_centre_A"],
                                                              n_atoms), 2),
        "spans_the_floor": n_atoms >= floor,
    }


def apply_filter(lib):
    """Apply the preregistered basin-fidelity downselect. Returns (kept, rejected-with-reasons).

    Every rejection carries the rule that rejected it and the value that failed, so the library's size is a
    consequence of stated thresholds rather than of a judgement made after seeing the answer.
    """
    def is_control(c):
        return c["pendant_kind"] in ("control", "wedge_control") or c["pendant"] == "acrylamide"

    def failures(c):
        f, why = c["basin_fidelity"], []
        if not f["spans_the_floor"]:
            why.append("shorter than the anchor-anchor span floor")
        if f["member_fraction_comfortable"] < FILTER["min_member_fraction_comfortable"]:
            why.append("comfortably holds only %.0f%% of the basin's members (< %.0f%%)"
                       % (100 * f["member_fraction_comfortable"],
                          100 * FILTER["min_member_fraction_comfortable"]))
        if f["strain_kT_at_placement_span"] > FILTER["max_strain_kT_at_placement"]:
            why.append("%.1f kT of chain strain at the designed placement's span (> %.1f)"
                       % (f["strain_kT_at_placement_span"], FILTER["max_strain_kT_at_placement"]))
        if c["n_backbone_atoms_intended"] > FILTER["max_backbone_atoms"]:
            why.append("%d backbone atoms exceeds the chemically routine cap of %d"
                       % (c["n_backbone_atoms_intended"], FILTER["max_backbone_atoms"]))
        return why

    # ★ PARSIMONY FIRST, among constructs that pass. Comfortable coverage increases monotonically with linker
    # length, so ranking on it alone drives every construct to the length cap — which it did, until this was
    # fixed: the first filtered library was 16 constructs all at exactly 24 backbone atoms. Length is a real
    # cost (permeability, synthetic steps, the entropic price the ternary assembly pays), so among constructs
    # that clear the thresholds the SHORTEST wins.
    ordered = sorted(lib, key=lambda c: (c["n_backbone_atoms_intended"],
                                         c["basin_fidelity"]["strain_kT_at_placement_span"],
                                         -c["basin_fidelity"]["member_fraction_comfortable"]))
    # pass 1 — designs only
    kept, counts, design_slots = [], {}, set()
    for c in ordered:
        if is_control(c):
            continue
        why = failures(c)
        key = (c["designed_for_basin"], c["pendant_kind"])
        if not why and counts.get(key, 0) < FILTER["max_per_basin_per_kind"]:
            counts[key] = counts.get(key, 0) + 1
            design_slots.add((c["designed_for_basin"], c["warhead_handle"], tuple(c["linker_segments"])))
            kept.append(dict(c, role="design"))
    # pass 2 — controls, retained only where they MATCH a kept design
    # ★ CONTROLS GET THEIR OWN CAP BUCKET, KEYED ON THE PENDANT ITSELF. Sharing the design bucket
    # (basin x pendant_kind) crowded them out: the two reversible electrophiles filled the "electrophile"
    # slot for every basin, and the IRREVERSIBLE comparator — the one construct that makes "prefer
    # reversible" a tested choice rather than an assertion — was filtered to ZERO. A filter that silently
    # deletes the comparator it is being judged against is worse than no filter.
    ccounts = {}
    for c in ordered:
        if not is_control(c):
            continue
        slot = (c["designed_for_basin"], c["warhead_handle"], tuple(c["linker_segments"]))
        key = (c["designed_for_basin"], c["pendant"])
        if slot in design_slots and ccounts.get(key, 0) < FILTER["max_per_basin_per_control"]:
            ccounts[key] = ccounts.get(key, 0) + 1
            kept.append(dict(c, role="control", matched_to_design_slot=[slot[0], slot[1], "+".join(slot[2])]))
    kept_ids = {c["construct_id"] for c in kept}
    # ★ pass 2b — NO CONFIRMED BASIN MAY SILENTLY VANISH. crbn|M0 is RUNG 5a's strongest nomination (0.92
    # pose persistence, 7.5x term-(b) enrichment) and its representative span of 23.3 A needs ~29 backbone
    # atoms to be held comfortably — beyond the chemically routine cap. Dropping it would leave a
    # library that looks clean while omitting the best basin for a reason no reader could see. So the
    # best-available construct is retained for every confirmed basin, WITH the thresholds it fails, and the
    # shortfall becomes a reported result instead of an absence.
    for bid in CONFIRMED:
        if any(c["designed_for_basin"] == bid for c in kept):
            continue
        cands = [c for c in ordered if c["designed_for_basin"] == bid and c["pendant"] == "none"]
        if not cands:
            continue
        c = min(cands, key=lambda c: (c["basin_fidelity"]["strain_kT_at_placement_span"],
                                      c["n_backbone_atoms_intended"]))
        kept.append(dict(c, role="best available within the chemically routine linker cap — RETAINED "
                                 "DESPITE FAILING the filter, so the shortfall is visible",
                         retained_despite_failing=failures(c)))
        kept_ids.add(c["construct_id"])
    # pass 3 — the labelled negative: one construct for the basin that FAILED the RUNG-5a term-(b) gate,
    # kept with its rejection reasons attached so the filter's own selectivity is falsifiable
    if FILTER["failing_basin_kept_as_labelled_negative"]:
        neg = [c for c in ordered if c["designed_for_basin"] == WEAK_CONTROL and c["pendant"] == "none"]
        if neg and not any(c["designed_for_basin"] == WEAK_CONTROL for c in kept):
            c = neg[0]
            kept.append(dict(c, role="labelled negative — designed against the basin that does NOT exceed "
                                     "the term-(b) background and persists in only 3/12 poses",
                             would_have_been_rejected_because=failures(c)))
            kept_ids.add(c["construct_id"])
    rejected = [dict(c, rejected_because=(failures(c) or ["diversity cap or unmatched control"]))
                for c in ordered if c["construct_id"] not in kept_ids]
    return kept, rejected


def synthetic_annotation(e3_key, wh_key, s1, s2, pkey):
    e3, wh = E3_HANDLE[e3_key], WARHEAD_HANDLE[wh_key]
    steps = ["1. %s  [warhead side: %s]" % (wh["coupling"], wh["name"]),
             "2. linker: %s" % LINKER_SEGMENT[s1]["block"]]
    if pkey != "none":
        steps.append("3. couple the orthogonally protected branch residue (%s); the (S) centre comes from "
                     "the building block, so the construct's stereochemistry is defined, not assumed"
                     % ("Fmoc-L-Dab(Boc)-OH" if PENDANT[pkey]["reach_key"] == "dab_branch"
                        else "Fmoc-L-Phe-OH or Fmoc-3-(3-pyridyl)-L-Ala-OH"))
        steps.append("4. selective side-chain deprotection, then %s" % PENDANT[pkey]["route"])
        if s2:
            steps.append("5. extend with %s" % LINKER_SEGMENT[s2]["block"])
    steps.append("%d. %s  [E3 side: %s]" % (len(steps) + 1, e3["coupling"], e3["name"]))
    return {
        "steps": steps,
        "convergent": True,
        "_scope": "a ROUTE ANNOTATION, not a validated synthesis. Building-block availability was not "
                  "checked against a live commercial catalogue, no step was attempted, and no yield is "
                  "implied. The earned phrase is 'a computationally prioritized, structure-defined, "
                  "retrosynthetically annotated candidate matrix for synthesis and experimental testing'.",
    }


def _selectivity_vs_length(reqs, lib):
    """★★ THE RANKING THE NEWLY-PRICED TRADE IMPLIES — shortest first, with what each length costs.

    Until 2026-07-25 backbone length was a SYNTHESIS cost in this rung: permeability, steps, the entropic
    price the ternary assembly pays. LANE 13's matched-construct test priced it as a SELECTIVITY cost as well
    (`PARALOGUE_COLLISION_BY_LINKER_ATOMS`): a construct that reaches C397 at 13 atoms is not merely more
    tractable than one that reaches it at 16, it is MORE SELECTIVE, because the longer chain is measurably
    more likely to put the same electrophile within reach of a paralogue cysteine at the same placement.

    ★ WHY THIS IS A REPORT AND NOT A NEW FILTER. The preregistered downselect was fixed before enumeration and
    is not being edited after seeing a result — that is the discipline the whole rung is held to. What is
    added is the axis, computed per construct, so the trade is legible where the design is made. The ranking
    key is (backbone atoms, then basin evidence): length first, because that is what the new measurement
    prices, and basin evidence second, because that is what Tier 2 measured.

    ⚠ AND THE ORDERING IS NOT A RECOMMENDATION ON ITS OWN. A short construct on a weak basin is short and
    weak. Every row therefore carries its basin's pose persistence and term-(b) enrichment beside its length,
    and the weak control is labelled, so a reader ranking on length alone can see what they are giving up.
    """
    ev = {r["meta_basin_id"]: r for r in reqs}
    rows = []
    for c in lib:
        r = ev.get(c["designed_for_basin"], {})
        n = c["n_backbone_atoms_intended"]
        rows.append({
            "construct_id": c["construct_id"],
            "basin": c["designed_for_basin"],
            "placement": c["designed_at_placement"],
            "n_backbone_atoms": n,
            "pendant": c["pendant"],
            "pendant_kind": c["pendant_kind"],
            "branch_target": c["branch_target"],
            "carries_the_covalent_handle": c["pendant_kind"] in ("electrophile", "control")
                                           and c["branch_target"] == "C397 SG",
            "carries_the_wedge": c["pendant_kind"] in ("wedge", "wedge_control"),
            "paralogue_collision_at_this_length": collision_bracket(n),
            "basin_pose_surviving_fraction": r.get("pose_surviving_fraction"),
            "basin_term_b_enrichment": r.get("term_b_max_enrichment_over_background"),
            "basin_is_the_labelled_weak_control": c["designed_for_basin"] == WEAK_CONTROL,
            "strain_kT_at_placement_span": c["basin_fidelity"]["strain_kT_at_placement_span"],
            "member_fraction_comfortable": c["basin_fidelity"]["member_fraction_comfortable"],
        })
    rows.sort(key=lambda x: (x["n_backbone_atoms"],
                             -(x["basin_pose_surviving_fraction"] or 0.0),
                             -(x["basin_term_b_enrichment"] or 0.0),
                             x["construct_id"]))
    gate = 12
    at_or_below = [x for x in rows if x["n_backbone_atoms"] <= gate]
    clean = [x for x in rows if x["paralogue_collision_at_this_length"]["hi"] == 0.0]
    return {
        "_what": "every retained construct at both placements, ranked SHORTEST FIRST, with the measured "
                 "paralogue-collision bracket at its own backbone length beside it.",
        "_how_to_read_the_bracket_on_a_non_covalent_construct": (
            "the collision measurement is about an ELECTROPHILE reaching a paralogue cysteine, so on a "
            "construct carrying no electrophile (`carries_the_covalent_handle: false`) the bracket is not a "
            "liability of that molecule as drawn — it is the price its LENGTH would carry if the covalent "
            "handle were installed on the same chain, which is the design the library exists to enable. "
            "Reported on every row for that reason, and flagged per row so the two readings cannot merge."),
        "_why": "LANE 13 priced backbone length as a SELECTIVITY cost, not only a synthesis cost. Before that "
                "measurement, ranking on length was a chemist's preference; after it, a shorter construct is "
                "a more selective one and the ranking is an evidence-based ordering.",
        "collision_profile_used": PARALOGUE_COLLISION_BY_LINKER_ATOMS,
        "collision_profile_source": "research/manuscripts/nr4a3-paralogue-dynamics-categorical-test-"
                                    "2026-07-25.md §3.3 — matched-construct test, 5 657 placements, same "
                                    "placement / warhead exit anchor / E3 anchor / budget. FOUR measured "
                                    "points; brackets are reported, never an interpolated value.",
        "n_at_or_below_the_12_atom_gate": len(at_or_below),
        "n_in_the_measured_zero_collision_band": len(clean),
        "honest_cutoff": (
            "★ THE HONEST CUT-OFF IS **14 BACKBONE ATOMS**, and it is read off the measurement rather than "
            "chosen. The collision probability is measured at 0.000 at 12 and 0.000 at 14, and 0.081 by 16 — "
            "so 14 is the longest length at which the reach-only collision probability is still a MEASURED "
            "zero. Above it the design is trading the categorical axis for reach, and the trade should be "
            "made explicitly. Two things stop this being a gate: (i) no construct in this library reaches "
            "C397 at or below the 12-atom term-(a) gate at ANY placement, so a cut-off at 12 would empty the "
            "covalent series; (ii) the 0.000 is the REACH-AND-EXPOSURE figure at every length, so what is "
            "actually being bounded here is the reach-only number, and it is bounded by four points from "
            "static models."),
        "ranked": rows,
    }


# ---------------------------------------------------------------------------------------------------------
# Stage C — the matched pair for RUNG 5a-KS
# ---------------------------------------------------------------------------------------------------------


def matched_pair(reqs, lib, placement_label="representative", ctx_cb=None):
    """Propose d / d0 for `S = ddG_coop(d0->d | NR4A3) - ddG_coop(d0->d | NR4A1)`.

    THE PROPERTY THAT HAS TO HOLD, AND THE ARGUMENT THAT IT DOES.

    `S` is a DOUBLE difference, and that is what buys it its power: the ligand's solvation, its internal
    strain, and its entire interaction with the E3 are IDENTICAL in the two paralogue legs, so they cancel
    exactly, leaving only the target-side interaction of the element that differs. For that cancellation to be
    real, three things must be true of the pair, and each is checked rather than asserted:

      (i)  d and d0 must differ in ONE element only. The pair below is an AZA-SCAN — 3-pyridyl vs phenyl —
           so net charge, heavy-atom count, rotatable bonds and shape are identical and exactly one property
           changes: the H-bond acceptor at the wedge site. A charged wedge (a carboxylate on Arg412) would
           have been a stronger interaction and a worse experiment: a net-charge change under PME needs a
           finite-size correction that does not cancel between differently-sized boxes, and the repo's own
           `assert_charge_consistency` refuses such a wedge outright.
      (ii) the wedge element must engage a TARGET-side difference of the RIGHT KIND. The preregistered rule
           (`_wedge_chemistry_ok`) is one line of chemistry: NR4A3 must present an H-bond DONOR and BOTH
           paralogues must not. Geometry alone selects Ile396, the most E3-clear site available, where a
           pyridyl nitrogen faces an isoleucine in every paralogue and `S` would be ~0 by construction. The
           site actually chosen, and its paralogue partners, are emitted in `wedge_target_residue`.
      (iii) the wedge element must NOT touch the E3, or the shared ligand-E3 leg stops being shared. The
           basin is chosen on measured E3 clearance at the wedge position, and the clearance is reported.

    WHAT REMAINS CONFOUNDED — stated here because it belongs with the proposal, not in a footnote:
      * Arg412's side chain is RIGID in this model. A pendant designed against one modelled rotamer is
        conditional on it, and an Arg at RSA 0.78 is exactly the kind of side chain that samples widely.
      * NR4A1 carries ALANINE at the aligned position, so the wedge does not meet an unfavourable partner
        there — it meets a solvent-exposed gap. The expected effect is therefore an NR4A3 GAIN rather than an
        NR4A1 PENALTY, and its magnitude is bounded by a single solvent-exposed H-bond: roughly 0.5-1.5
        kcal/mol against a best-case resolvable difference of 1.12. **A null result is the likely outcome and
        must not be read as a refutation of the CATEGORICAL mechanism.**
      * the whole construct sits on a hypothesised cmpd19 pose in one receptor frame, and the basin it is
        designed into is a rigid-body nomination, not a modelled complex.

    ★ AND THE THING THE ORCHESTRATOR MOST NEEDS TO SEE: a non-covalent alchemical double difference CANNOT
    test the categorical mechanism. Term (a)'s selectivity is that NR4A1/NR4A2 have NO nucleophile at the
    aligned position — a bond that forms in one paralogue and cannot form in the other. `S` is a
    non-covalent relative free energy; it sees the PRE-covalent complex only. So RUNG 5a-KS as specified
    tests the MARGINAL axis, while RUNG 5a's Tier-2 GO was taken on the CATEGORICAL one. A NO-GO from this
    test therefore falsifies the marginal wedge, NOT the program.

    ★★ CALLED ONCE PER PLACEMENT (2026-07-25). It used to run only against the representative-geometry
    library, with a second, SMILES-free function proposing the exemplar pair from geometry alone. Now the
    exemplar has its own enumerated, filtered library, so the identical selection runs against it and returns
    a real construct pair — the caller passes `placement_label` and reports both. Two consequences worth
    stating: the exemplar pair is no longer a design target without a molecule, and the two pairs are
    selected by the SAME code, so a difference between them is a difference in the geometry, not in the rule.

    ★ THE PREREGISTERED CHEMISTRY RULE IS NOW BINDING HERE TOO. Candidate wedge sites are filtered through
    `_wedge_chemistry_ok` (NR4A3 presents a donor, BOTH paralogues do not) as well as on E3 clearance. It was
    previously applied only on the exemplar path, so the representative pair satisfied it by luck rather than
    by construction — geometry alone selects Ile396, where a pyridyl nitrogen faces an isoleucine in every
    paralogue and `S` would be ~0 by construction.
    """
    def _alternative_block(rs):
        """The strongest basin that CANNOT host the pair, with its best wedge site — read from the data, not
        transcribed. Transcribed numbers in prose are exactly what `lint_consistency.py` exists to catch."""
        cant = [r for r in rs if r["meta_basin_id"] != WEAK_CONTROL
                and not any(c["designed_for_basin"] == r["meta_basin_id"] and c["pendant"] == "pyr3"
                            for c in lib)]
        if not cant:
            return None
        r = max(cant, key=lambda r: (r["pose_surviving_fraction"],
                                     r["term_b_max_enrichment_over_background"]))
        site = select_wedge_site(r["wedge_element_sites"]["sites"])
        return {
            "basin": r["meta_basin_id"],
            "pose_surviving_fraction": r["pose_surviving_fraction"],
            "term_b_enrichment_over_background": r["term_b_max_enrichment_over_background"],
            "best_wedge_site": site,
            "why_it_is_attractive": (
                "the strongest nomination RUNG 5a produced (%.2f pose persistence, %.1fx over the term-(b) "
                "null)%s"
                % (r["pose_surviving_fraction"], r["term_b_max_enrichment_over_background"],
                   ("" if site is None else
                    ", and it carries a wedge site at %s%d — %s in NR4A1 and %s in NR4A2 — with %.1f A of E3 "
                    "clearance" % (site["nr4a3"], site["uniprot_resid"], site["nr4a1"], site["nr4a2"],
                                   site["e3_clearance_A"])))),
            "what_it_costs": ("a ~%s backbone-atom linker against the %d-atom routine cap used here. Long, "
                              "but not unprecedented for a PROTAC, and the cap is a stated convention rather "
                              "than a law."
                              % (r["accessibility"]["n_atoms_for_comfortable_span"], CHEM_MAX_ATOMS)),
            "the_trade": "a stronger basin and, where the site differs, a stronger wedge residue — paid for "
                         "in linker length and therefore in permeability and in the ternary assembly's own "
                         "entropy. Surfaced rather than filtered away, because it is a judgement that should "
                         "be made explicitly instead of made silently by a threshold.",
        }

    # The pair must EXIST IN THE FILTERED LIBRARY — a proposal naming a construct the filter rejected would
    # be a proposal to run FEP on a linker that cannot hold its own basin. Candidates are therefore drawn
    # from `lib`, and only then ranked by the two properties that make a pair readable: how many poses the
    # basin survives, and how far the wedge element sits from the E3 body.
    cands = []
    for r in reqs:
        if r["meta_basin_id"] == WEAK_CONTROL:
            continue
        ds = [c for c in lib if c["designed_for_basin"] == r["meta_basin_id"] and c["pendant"] == "pyr3"]
        for d_ in ds:
            d0_ = next((c for c in lib
                        if c["designed_for_basin"] == r["meta_basin_id"] and c["pendant"] == "ph"
                        and c["warhead_handle"] == d_["warhead_handle"]
                        and c["linker_segments"] == d_["linker_segments"]), None)
            if d0_ is None:
                continue
            s_ = select_wedge_site(r["wedge_element_sites"]["sites"])
            if s_ is None:
                continue
            # ★ AND THE MOLECULE MUST ACTUALLY CARRY THE WEDGE AT THAT SITE. `d_` was enumerated against a
            # site chosen by the same selector, so this holds by construction — but "by construction" is
            # precisely what silently stopped holding once, so it is asserted against the emitted record
            # rather than trusted. A mismatch is a REFUSAL, not a warning.
            want = "%s%d" % (s_["nr4a3"], s_["uniprot_resid"])
            if d_.get("branch_target") != want or d0_.get("branch_target") != want:
                raise SystemExit(
                    "[5b] REFUSING: the matched pair's wedge site (%s) is not the site its molecules were "
                    "built against (d=%s, d0=%s). The enumerator and the pair selector must both go through "
                    "`select_wedge_site`." % (want, d_.get("branch_target"), d0_.get("branch_target")))
            # ★ CLEARANCE RE-MEASURED AT THIS MOLECULE'S OWN (n, k), not at the site's probe geometry.
            # A pair is only readable if the wedge cannot touch the E3, and that is a property of where THIS
            # construct's branch atom lands — not of the probe length the site list was derived at. The
            # candidate is ranked, and reported, on the re-measured value; the probe value is kept beside it.
            q_w = ctx_cb[s_["uniprot_resid"] - UNIPROT_OFFSET]
            _, p_w = LD.three_ball_min_margin(
                [r["_a"], r["_b"], q_w],
                [d_["branch_k_from_warhead"] * RISE,
                 (d_["n_backbone_atoms_intended"] - d_["branch_k_from_warhead"]) * RISE,
                 PENDANT_REACH["aryl_branch_residue"]])
            clr = round(r["_clearance_at"](p_w), 2)
            cands.append((r["pose_surviving_fraction"], clr, r, s_, d_, d0_, clr, s_["e3_clearance_A"]))
    if not cands:
        return {"status": "NO PAIR PROPOSED",
                "reason": "no confirmed basin has BOTH a divergent, exposed, linker-reachable residue with "
                          ">= 6 A of E3 clearance AND a matched pyridyl/phenyl construct pair that survives "
                          "the basin-fidelity filter"}
    # ★ AND THE RE-MEASURED CLEARANCE IS A HARD FILTER, not only a ranking key. The 6.0 A test that produced
    # `e3_clear_enough_for_a_matched_pair` was applied at the probe geometry; a construct whose own branch
    # atom lands closer than that fails the property the pair exists to have, and is not a candidate.
    cands = [c for c in cands if c[6] >= 6.0]
    if not cands:
        return {"status": "NO PAIR PROPOSED",
                "reason": "every matched pyridyl/phenyl pair surviving the fidelity filter places its wedge "
                          "element within 6 A of the E3 body at its OWN length and branch position, so the "
                          "shared ligand-E3 leg would not cancel and S would not isolate a target-side "
                          "interaction"}
    # ★ LENGTH IS NOW THE SECOND KEY, AHEAD OF CLEARANCE (2026-07-26). Basin evidence still leads — that is
    # what Tier 2 measured and it is not being re-weighted. But below it the old key was "more E3 clearance is
    # better", and clearance above the 6 A validity threshold buys very little, whereas LANE 13's
    # matched-construct measurement makes every extra backbone atom a measured selectivity cost
    # (`PARALOGUE_COLLISION_BY_LINKER_ATOMS`). Parsimony was already this rung's stated tie-break inside the
    # filter; applying the same tie-break here is consistency, not a retune — and clearance is retained as the
    # third key so it still separates otherwise identical candidates.
    cands.sort(key=lambda c: (-c[0], c[4]["n_backbone_atoms_intended"], -c[1]))
    persist, clear, req, site, d, d0, clr_construct, clr_probe = cands[0]

    # ★ WHY THIS ARM, STATED EXPLICITLY, BECAUSE THE OBVIOUS WRONG REASON IS AVAILABLE. An earlier framing of
    # the RUNG-5a result held that "CRBN's null is 0.81-0.96, so the discrimination lives on VHL". That claim
    # has been RETRACTED: 0.81-0.96 is the ANY-lysine null, whereas term (b)'s enrichment is over the
    # UNIQUE-lysine null, and the number was itself an exit-vector artefact that halves (0.858 -> 0.399) when
    # the CRBN arm is restaged assembly-native. CRBN remains the sole Pareto-front member; VHL is a labelled
    # backfill and an E3-choice sensitivity control. **No CRBN-vs-VHL preference is asserted here.** The arm
    # below was selected on basin evidence only — pose persistence, then measured E3 clearance at the wedge —
    # among the basins that can actually host a matched pair, and the per-basin reasons are emitted so the
    # selection can be audited rather than trusted.
    audit = []
    for r in reqs:
        site_ok = select_wedge_site(r["wedge_element_sites"]["sites"])
        clean = [site_ok] if site_ok else []
        has_pair = any(c["designed_for_basin"] == r["meta_basin_id"] and c["pendant"] == "pyr3" for c in lib)
        blockers = []
        if r["meta_basin_id"] == WEAK_CONTROL:
            blockers.append("labelled weak control: does not exceed the term-(b) background")
        if not clean:
            blockers.append("no divergent, exposed, linker-reachable residue with >= 6 A of E3 clearance "
                            "that also satisfies the preregistered wedge chemistry rule (NR4A3 donor, "
                            "BOTH paralogues not)")
        if not has_pair:
            blockers.append("no matched pyridyl/phenyl construct survives the basin-fidelity filter — its "
                            "representative span needs %s backbone atoms to be held at <= %.1f kT, against "
                            "a chemically routine cap of %d"
                            % (r["accessibility"]["n_atoms_for_comfortable_span"], MAX_STRAIN_KT,
                               CHEM_MAX_ATOMS))
        audit.append({
            "meta_basin_id": r["meta_basin_id"],
            "pose_surviving_fraction": r["pose_surviving_fraction"],
            "term_b_enrichment": r["term_b_max_enrichment_over_background"],
            "best_wedge_site": site_ok,
            "can_host_the_pair": bool(clean) and has_pair and r["meta_basin_id"] != WEAK_CONTROL,
            "blockers": blockers,
        })
    return {
        "status": "PROPOSED" if (d and d0) else "NO MATCHING CONSTRUCT PAIR IN THE LIBRARY",
        "test": "S = ddG_coop(d0->d | NR4A3) - ddG_coop(d0->d | NR4A1); ternary legs only (the shared "
                "ligand-E3 binary leg and the solvent leg are paralogue-independent and cancel exactly)",
        "placement": placement_label,
        "placement_basin_id": req["designed_on"]["basin_id"],
        "placement_pose_id": req["designed_on"]["pose_id"],
        "placement_span_A": req["endpoint_distance"]["placement_span_A"],
        "basin": req["meta_basin_id"],
        "basin_pose_surviving_fraction": persist,
        "arm_selection_audit": audit,
        # DERIVED, not transcribed. The previous version stated in prose which basin was excluded and why,
        # naming a length; that sentence went stale the moment the geometry changed, which is exactly the
        # class of drift `lint_consistency.py` exists to catch. The excluded basins and their blockers are
        # now read off `arm_selection_audit`.
        "arm_selection_note": (
            "Selected on basin evidence only — pose persistence, then measured E3 clearance at the wedge — "
            "among basins that can host a matched pair AND satisfy the preregistered wedge chemistry rule. "
            "NOT on any CRBN-vs-VHL preference: CRBN is the sole Pareto-front member and VHL is a labelled "
            "backfill / E3-choice sensitivity control. Basins that could NOT host the pair at this "
            "placement, with the reason each was blocked: %s"
            % ("; ".join("%s [%s]" % (a["meta_basin_id"], " + ".join(a["blockers"]))
                         for a in audit if not a["can_host_the_pair"]) or "none")),
        "alternative_pair_on_the_strongest_basin": _alternative_block(reqs),
        "wedge_element": "3-pyridyl (d) vs phenyl (d0) — an aza-scan",
        "wedge_target_residue": site,
        # ★ MEASURED ON THE PROPOSED MOLECULE, at its own length and branch position — see the comment where
        # it is computed. `..._site_probe_A` is the older quantity (the site list's probe geometry) and is
        # kept beside it so the two can never be confused for one another again.
        "e3_clearance_at_wedge_A": clr_construct,
        "e3_clearance_at_wedge_site_probe_A": clr_probe,
        "_e3_clearance_reading": (
            "the load-bearing check for the pair: `S` isolates a TARGET-side interaction only because the "
            "ligand's entire interaction with the E3 is identical in the two paralogue legs and cancels. "
            "`e3_clearance_at_wedge_A` is measured at the PROPOSED CONSTRUCT's own (n, k); "
            "`e3_clearance_at_wedge_site_probe_A` is the site-derivation probe value at n = span floor + 4 "
            "and the middle of that site's window, which is what the site list carries. The construct value "
            "is the one that governs — it is filtered on (>= 6 A) and ranked on."),
        "d": d, "d0": d0,
        "differs_only_in_the_wedge_element": {
            "net_charge": "identical (both neutral)",
            "heavy_atoms": "identical (C-H -> N)",
            "rotatable_bonds": "identical",
            "shape": "isosteric aryl ring",
            "electrophile": "identical in both members (absent, or the SAME reversible-covalent handle at "
                            "the SAME branch position) — the categorical handle is held constant so it "
                            "cannot contribute to S",
            "e3_contact": "the wedge element is %.1f A from the nearest E3 atom in the modelled placement, "
                          "so it cannot be re-tuning the ligand-E3 interface" % clear,
        },
        "remaining_confounds": [
            "%s%d's side chain is rigid in this model; the pair is conditional on the modelled rotamer."
            % (site["nr4a3"], site["uniprot_resid"]),
            "NR4A1 carries %s at the aligned position and NR4A2 carries %s — neither is an H-bond donor, so "
            "the expected signal is an NR4A3 GAIN against an absence, not a paralogue penalty. It is bounded "
            "by one partly-buried H-bond (~0.5-1.5 kcal/mol) against a best-case resolvable 1.12, so a NULL "
            "is the likely outcome and is recorded here BEFORE the run."
            % (site["nr4a1"], site["nr4a2"]),
            "the construct rests on the hypothesised cmpd19 pose x one receptor frame (double conditionality)",
            "the basin is a rigid-body nomination, not a modelled complex; the linker conformer that places "
            "the wedge on Arg412 is one of many the chain can adopt, and its population is unmeasured.",
            "★ a non-covalent double difference cannot test the CATEGORICAL mechanism (a bond that forms in "
            "NR4A3 and cannot form in NR4A1). S tests the MARGINAL wedge; a null falsifies that wedge, not "
            "the program.",
        ],
        "second_pair_if_the_first_is_read": {
            "purpose": "the pre-covalent half of the CATEGORICAL axis",
            "d": "cyac_me (beta-methyl alpha-cyanoacrylamide) at the C397 branch position",
            "d0": "cyanoprop (2-cyanobutanamide, the saturated analogue), same branch position",
            "what_it_measures": "whether the electrophile-bearing arm's NON-COVALENT recognition already "
                                "discriminates Cys397 (NR4A3) from Asn363 (NR4A1). In reversible-covalent "
                                "chemistry, selectivity is K_i x k_inact; this test addresses K_i only, and "
                                "a null leaves the categorical (k_inact) argument standing.",
            "why_this_d0": "the saturated analogue is the standard non-electrophilic control: same heavy "
                           "atoms, same charge, same nitrile, same amide, no Michael acceptor — so the "
                           "alchemical change is the C=C and nothing else.",
            "the_caveat_that_comes_with_it": "reducing the acceptor creates an sp3 stereocentre the "
                                             "electrophile does not have, so this pair is matched in "
                                             "CONSTITUTION but not in STEREOCHEMISTRY. It is declared as a "
                                             "single (S) diastereomer; the (R) epimer is the obvious second "
                                             "control if the centre has to be shown not to matter.",
        },
    }


# ---------------------------------------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------------------------------------


def run(args):
    t0 = time.time()
    ctx = load_context(args.basins, args.registry, args.atlas, args.struct, args.series)
    sites = reactive_sites(ctx)
    ctx["_c397"] = sites["unique_cysteines"]["C397"]["xyz"]

    metas = {m["meta_basin_id"]: m for m in ctx["basins"]["meta_basins_ranked"]}
    missing = [b for b in CONFIRMED if b not in metas]
    if missing:
        raise SystemExit("confirmed basins absent from the artifact: %s" % missing)
    # ★ IDENTITY CHECK — see CONFIRMED_PATCH. Present-by-name is not the same as being the same basin.
    identity = []
    for bid in CONFIRMED:
        got = set(metas[bid]["interface_patch_uniprot"])
        want = set(CONFIRMED_PATCH[bid])
        j = 1.0 - G.jaccard_distance(got, want)
        identity.append({"meta_basin_id": bid, "patch_jaccard_vs_published": round(j, 3),
                         "ok": j >= CONFIRMED_PATCH_MIN_JACCARD,
                         "published_patch": sorted(want), "artifact_patch": sorted(got)})
    bad = [i for i in identity if not i["ok"]]
    if bad:
        raise SystemExit(
            "REFUSING: the artifact's meta-basin IDs do not denote the confirmed basins.\n"
            + "\n".join("  %s: patch Jaccard %.3f < %.2f\n    published: %s\n    artifact:  %s"
                        % (i["meta_basin_id"], i["patch_jaccard_vs_published"],
                           CONFIRMED_PATCH_MIN_JACCARD, i["published_patch"], i["artifact_patch"])
                        for i in bad)
            + "\n  Meta-basin indices are POSITIONAL — a rank in that run's clustering — so they move when the "
              "sampling changes. Designing against an id that resolves to a different surface patch produces a "
              "library for a basin nobody confirmed, with no symptom. Re-run the basin search at the settings "
              "the confirmation was made on (12 poses, 1e6 samples), or update CONFIRMED/CONFIRMED_PATCH "
              "together and say why.")
    print("[5b] confirmed-basin identity OK: patch Jaccard %s"
          % ", ".join("%s=%.2f" % (i["meta_basin_id"], i["patch_jaccard_vs_published"]) for i in identity))

    # ★★ TWO PLACEMENTS, TWO FULL LIBRARIES, ONE CODE PATH. The requirements, the enumeration and the
    # preregistered filter are identical; only the placement they are derived at differs. That is what makes
    # the two libraries comparable, and the comparison IS the finding: how much of a construct's shape is a
    # property of the basin, and how much of it is a property of which member of the basin you designed at.
    reqs_rep, reqs_ex = [], []
    for bid in CONFIRMED:
        r_rep, r_ex = basin_requirements(ctx, metas[bid], sites)
        reqs_rep.append(r_rep)
        if r_ex is not None:
            reqs_ex.append(r_ex)

    def _build(reqs, label):
        if not reqs:
            return [], [], [], {"status": "NO REQUIREMENTS AT THIS PLACEMENT"}
        enumerated = enumerate_library(reqs, ctx)
        lib, rejected = apply_filter(enumerated)
        lib.sort(key=lambda c: (-c["basin_fidelity"]["P_reach_normalised"],
                                -(c["basin_fidelity"]["selectivity_vs_other_confirmed_basins"] or 0.0)))
        return enumerated, lib, rejected, matched_pair(reqs, lib, label, ctx["model"]["cb"])

    enum_rep, lib_rep, rej_rep, pair_rep = _build(reqs_rep, "representative")
    enum_ex, lib_ex, rej_ex, pair_ex = _build(reqs_ex, "term_a_exemplar")

    def _filter_control_reading(reqs, lib):
        """★ WHAT THE FILTER'S OWN CONTROL SAYS AT THIS PLACEMENT — computed, not asserted.

        The library carries a LABELLED WEAK CONTROL (`vhl|M14`, which does not exceed the term-(b)
        background) so that "the filter selects good basins" is falsifiable rather than tautological. It has
        to be READ, and at representative geometry it reads badly for the filter: the strongest basin
        (`crbn|M0`) is retained only as a labelled failure too, for the same reason the weak control is — a
        long representative span. So the filter was discriminating on SPAN, not on basin quality, and the
        two are not the same thing. This block reports, per basin, whether its constructs passed on their
        merits or were retained despite failing, so the reading is in the artifact rather than in prose.
        """
        by_basin = {}
        for r in reqs:
            cs = [c for c in lib if c["designed_for_basin"] == r["meta_basin_id"]]
            passed = [c for c in cs if c.get("role") in ("design", "control")]
            by_basin[r["meta_basin_id"]] = {
                "is_the_labelled_weak_control": r["meta_basin_id"] == WEAK_CONTROL,
                "term_b_exceeds_background": r["term_b_exceeds_background"],
                "pose_surviving_fraction": r["pose_surviving_fraction"],
                "n_kept_on_merit": len(passed),
                "n_kept_despite_failing": len(cs) - len(passed),
                "placement_span_A": r["endpoint_distance"]["placement_span_A"],
            }
        weak = by_basin.get(WEAK_CONTROL, {})
        strong = [b for b in by_basin.values() if b["term_b_exceeds_background"]]
        return {
            "per_basin": by_basin,
            "_reading": (
                "the fidelity filter tests whether a LINKER can hold a basin. It does NOT test basin "
                "quality, so it cannot be expected to reject the weak control on term-(b) grounds and must "
                "not be credited when it happens to. At this placement the weak control kept %d construct(s) "
                "on merit, against %d..%d for the term-(b)-positive basins."
                % (weak.get("n_kept_on_merit", 0),
                   min([b["n_kept_on_merit"] for b in strong], default=0),
                   max([b["n_kept_on_merit"] for b in strong], default=0))),
        }

    def _summary(reqs, enumerated, lib, rejected):
        return {
            "n_enumerated": len(enumerated),
            "n_rejected": len(rejected),
            "n_constructs": len(lib),
            "by_basin": {r["meta_basin_id"]: sum(1 for c in lib
                                                 if c["designed_for_basin"] == r["meta_basin_id"])
                         for r in reqs},
            "n_reversible_covalent": sum(1 for c in lib if PENDANT.get(c["pendant"], {}).get("reversible")),
            "n_irreversible_comparator": sum(1 for c in lib if c["pendant"] == "acrylamide"),
            "n_controls": sum(1 for c in lib if c["pendant_kind"] in ("control", "wedge_control")),
        }

    ranking = _selectivity_vs_length(reqs_ex + reqs_rep, lib_ex + lib_rep)

    # The two C397 ranges quoted in `_corrections_to_rung_5a`, READ OFF the records rather than typed.
    _rep_exact = [r["electrophile_reach"]["C397"]["by_pendant"]["rung5a_convention"]["exact_atoms"]
                  for r in reqs_rep]
    _reported = [r["electrophile_reach"]["C397"]["reported_by_rung5a"] for r in reqs_rep]

    def _pair_alternatives():
        """★ EVERY VALID d/d0 PAIR IN THE LIBRARY, SHORTEST FIRST — because the recommendation is no longer
        the shortest one, and that is a trade the orchestrator has to be able to see rather than infer.

        A pair is a pyr3 construct and the ph construct that matches it in basin, placement, warhead handle
        and linker segments — the same matching `matched_pair` uses. The `S` test can be run on any of them;
        which one to run is a judgement between BASIN EVIDENCE (pose persistence, term-(b) enrichment) and
        BACKBONE LENGTH (now a measured selectivity cost), and both are on every row.
        """
        alts = []
        for lib, reqs in ((lib_ex, reqs_ex), (lib_rep, reqs_rep)):
            ev = {r["meta_basin_id"]: r for r in reqs}
            for d_ in [c for c in lib if c["pendant"] == "pyr3"]:
                d0_ = next((c for c in lib
                            if c["designed_for_basin"] == d_["designed_for_basin"]
                            and c["pendant"] == "ph"
                            and c["warhead_handle"] == d_["warhead_handle"]
                            and c["linker_segments"] == d_["linker_segments"]), None)
                if d0_ is None:
                    continue
                r = ev[d_["designed_for_basin"]]
                n = d_["n_backbone_atoms_intended"]
                alts.append({
                    "d": d_["construct_id"], "d0": d0_["construct_id"],
                    "basin": d_["designed_for_basin"],
                    "placement": d_["designed_at_placement"],
                    "n_backbone_atoms": n,
                    "branch_k_from_warhead": d_["branch_k_from_warhead"],
                    "wedge_target": d_["branch_target"],
                    "basin_pose_surviving_fraction": r["pose_surviving_fraction"],
                    "basin_term_b_enrichment": r["term_b_max_enrichment_over_background"],
                    "paralogue_collision_at_this_length": collision_bracket(n),
                    "strain_kT_at_placement_span": d_["basin_fidelity"]["strain_kT_at_placement_span"],
                })
        alts.sort(key=lambda x: (x["n_backbone_atoms"], -x["basin_pose_surviving_fraction"]))
        return alts

    pair_alternatives = _pair_alternatives()

    for r in reqs_rep + reqs_ex:
        r.pop("_a", None)
        r.pop("_b", None)
        r.pop("_clearance_at", None)

    out = {
        "_title": "RUNG 5b — inverse linker design for the confirmed NR4A3 orientation basins",
        "_status": "DESIGN PRIORITISATION. Not a result about binding, degradation, efficacy or safety. "
                   "Every construct is a PREDICTED SELECTIVE CANDIDATE, never a selective hit.",
        "_method": "For each confirmed meta-basin, TWO placements are carried — the basin's representative "
                   "(a typical member) and its term-(a) EXEMPLAR (the member needing the shortest exact "
                   "linker to C397, a best-of-N and therefore optimistic). Each placement's rigid transform "
                   "is "
                   "recovered from its stored landmarks (verified by reproducing the placement's own E3 "
                   "anchor to <0.01 A) and used to derive the linker requirements: endpoint distance and its "
                   "span floor, the exit-vector angles and dihedral with the turn cost in backbone atoms, "
                   "worm-like-chain strain and accessibility as a probability over the basin's span window, "
                   "and the EXACT (three-ball, integer-branch-position) reach to each paralogue-unique "
                   "cysteine over a sweep of named pendant building blocks. A virtual library is then "
                   "enumerated per basin — never as a blind cross-product — with the electrophile position "
                   "on the linker as an explicit design variable, and filtered on basin fidelity. The SAME "
                   "enumeration and the SAME preregistered filter run at both placements, so a difference "
                   "between the two libraries is a difference in the geometry and not in the rule.",
        "_limits": [
            "DOUBLE CONDITIONALITY: everything is conditional on the hypothesised cmpd19 binary pose x the "
            "chosen receptor frame. No cmpd19 pose exists in the matched-model frame.",
            "Designed on RIGID-BODY placements with rigid side chains, no solvation and no induced fit. A "
            "basin is a NOMINATION of a region of orientation space, not a modelled complex, so a construct "
            "is a hypothesis about where a linker could go, not a prediction that it will.",
            "The geometric anchors are the pose's pocket-mouth exit point and the crystal ligand's derived "
            "exit atom; the CHEMICAL anchors are the warhead's C5 substituent atom and the E3 handle's "
            "attachment heteroatom. These are within one to two bonds of each other, so every backbone-atom "
            "count carries about +/-2 atoms of definitional slack — comparable to the differences being "
            "resolved, which is why lengths are enumerated as a ladder and not asserted as a value.",
            "The WLC strain is an ideal semi-flexible-chain estimate with no excluded volume, no solvent and "
            "no torsional preferences. It is NOT a force-field strain energy and no ranking turns on a small "
            "difference in it.",
            "Synthetic annotations are ROUTES, not validated syntheses: building-block availability was not "
            "checked against a live commercial catalogue and no step was attempted.",
            "★ THE CHEMISTRY AXIS IS ONE RESIDUE DEEP, AND THERE IS NO GEOMETRIC FALLBACK. C397 is robust "
            "— over a 100-conformer MD ensemble its RSA median is 0.416 (the committed 0.395 sits at the "
            "median) and it reaches the 12-atom gate in 96 % of unbiased frames. But C420 and C559 reach "
            "that gate in 0 of 75 frames (C420 needs 16 backbone atoms, C559 needs 20, both paid out of the "
            "same contour that must also span to the E3). So if C397 fails CHEMICALLY — an unreactive "
            "microenvironment, a competing conserved cysteine, an unacceptable promiscuity profile — no "
            "other NR4A3-unique cysteine can take its place, and the categorical chemistry axis closes. "
            "The hedge this library carries is NOT a second cysteine, because there is none: it is that the "
            "library is not all-covalent. Constructs with no electrophile at all, and the paralogue-unique "
            "LYSINE axis (term b) they are designed against, are independent of C397 entirely.",
            "A covalent handle is an unresolved liability, not an upgrade. Electrophile promiscuity cannot "
            "be checked without chemoproteomics, and it must be reported alongside the parent cmpd19 "
            "warhead's published MYC induction. REVERSIBLE-covalent chemistry is preferred throughout so "
            "catalytic turnover survives; an irreversible adduct makes the degrader stoichiometric.",
            "A longer pendant relaxes reach to CONSERVED NR4A3 cysteines as well as the unique one. The "
            "paralogue argument is unaffected (it is a sequence fact), but intra-NR4A3 chemoselectivity is "
            "not, and the trade-off is reported per basin.",
            "No efficacy, safety, therapeutic-window or clinical claim is made or implied.",
        ],
        "_corrections_to_rung_5a": [
            # ★ DERIVED FROM THE ARTIFACT, NOT TYPED. This sentence carried the numbers "16-33 against a
            # reported 8-12" as literals; the "8-12" silently became wrong the moment the reach rule was
            # corrected upstream, because the artifact's reported figure is now the EXACT one. A sentence
            # that restates a number it does not own is the drift class `lint_consistency.py` exists for.
            "`min_linker_atoms` is a BEST-OF-N over a basin's sampled members and the achieving member is "
            "NOT the published representative: at the representative of all five confirmed meta-basins the "
            "exact C397 requirement is %d-%d backbone atoms, against the artifact's reported (exemplar) "
            "%d-%d. The reported figure is correct as defined; it is a statistic, not a buildable geometry."
            % (min(_rep_exact), max(_rep_exact), min(_reported), max(_reported)),
            "✅ RESOLVED UPSTREAM 2026-07-25 (LANE 10). RUNG 5a's reach criterion `|q-a| + |q-b| <= L + 2e` "
            "credited the pendant arm with shortening the anchor-to-anchor SPAN, which no pendant can do, so "
            "every published term-(a) figure was a LOWER BOUND by up to ~5 backbone atoms. The basin search "
            "now calls the same exact three-ball kernel this rung has always used, so the repo holds ONE "
            "reach rule; the superseded relaxed values are carried per record as `*_relaxed_superseded`. "
            "★ NOTE FOR ANYONE RE-READING THE LIBRARY AGAINST THAT CORRECTION: the constructs were never "
            "built on the relaxed rule. Branch positions and lengths here come from "
            "`linker_design.branch_position_window` / `min_linker_atoms_exact`, which pre-date the "
            "correction — the defect lived in `basin_geom.linker_can_visit`, which only the basin search "
            "consumed. Re-enumerating against the corrected artifact changes which PLACEMENTS are designed "
            "on, not the rule the molecules were drawn with.",
            "`best_linker_atoms = 19` on 188 of 192 basins is the last point of the accessibility scan, not "
            "an optimum; the mean-density profile is still rising there (for a 20 A span the true argmax is "
            "~53 backbone atoms). Accessibility is recomputed here as a probability over the span window.",
            "RUNG 5a's electrophile arm reach of 3.0 A is shorter than every real pendant: an aryl bonded to "
            "a backbone carbon reaches ~4 A, a directly N-acylated acrylamide ~5 A, and a Dab-type branch "
            "carrying a cyanoacrylamide ~8.75 A. The gate is therefore CONSERVATIVE on term (a), and the "
            "sweep over named building blocks is reported per basin.",
        ],
        "inputs": {
            "basins": os.path.relpath(args.basins, REPO),
            "e3_registry": os.path.relpath(args.registry, REPO),
            "differential_surface_atlas": os.path.relpath(args.atlas, REPO),
            "warhead_series": os.path.relpath(args.series, REPO),
            "structure": os.path.relpath(args.struct, REPO),
            "confirmed_basins": CONFIRMED,
            "weak_control_basin": WEAK_CONTROL,
        },
        "reference_cores": REFERENCE_CORES,
        "pendant_reach_A": PENDANT_REACH,
        "chemistry": {"e3_handles": E3_HANDLE, "warhead_handles": WARHEAD_HANDLE,
                      "linker_segments": LINKER_SEGMENT, "pendants": PENDANT},
        "basin_fidelity_filter": FILTER,
        "confirmed_basin_identity_check": {
            "_what": "meta-basin IDs are POSITIONAL (a rank in that run's clustering), so `CONFIRMED` alone "
                     "cannot guarantee the artifact's `crbn|M0` is the basin that was confirmed. Each id's "
                     "interface patch is matched against the published one under the SAME Jaccard threshold "
                     "the search uses to call two placements one meta-basin; a miss is a refusal, not a note.",
            "min_jaccard": CONFIRMED_PATCH_MIN_JACCARD,
            "per_basin": identity,
        },
        "basin_requirements": reqs_ex,
        "basin_requirements_at_representative_geometry": reqs_rep,
        # ★ `virtual_library` IS BOTH LIBRARIES, TAGGED. The RDKit verifier consumes this key, and verifying
        # only one placement's molecules would leave the other's SMILES unchecked — the exact gap that let an
        # alpha-ketoamide through once already. Every retained construct carries `designed_at_placement`.
        "virtual_library": lib_ex + lib_rep,
        "virtual_library_at_the_term_a_exemplar": lib_ex,
        "virtual_library_at_representative_geometry": lib_rep,
        "rejected_by_the_filter": rej_ex,
        "rejected_by_the_filter_at_representative_geometry": rej_rep,
        "library_summary": _summary(reqs_ex, enum_ex, lib_ex, rej_ex),
        "library_summary_at_representative_geometry": _summary(reqs_rep, enum_rep, lib_rep, rej_rep),
        "filter_control_reading": _filter_control_reading(reqs_ex, lib_ex),
        "filter_control_reading_at_representative_geometry": _filter_control_reading(reqs_rep, lib_rep),
        # The RECOMMENDED pair is the exemplar one and it now carries real, RDKit-verified d/d0 SMILES rather
        # than a design target without molecules. The representative pair is kept beside it, unchanged in
        # role: the honest bracket on a best-of-N.
        "matched_pair_for_rung_5a_ks": pair_ex,
        "matched_pair_at_representative_geometry": pair_rep,
        "selectivity_vs_length_ranking": ranking,
        "matched_pair_alternatives_by_length": {
            "_what": "every d/d0 pair the filtered libraries can host, at BOTH placements, shortest first. "
                     "The recommendation above leads on BASIN EVIDENCE; this list leads on LENGTH, which "
                     "LANE 13 priced as a selectivity cost. Where the two disagree, the disagreement is the "
                     "finding and it is left visible rather than resolved by a threshold.",
            "pairs": pair_alternatives,
        },
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("[5b] wrote %s  (%d exemplar + %d representative constructs across %d basins) in %.1f s"
          % (os.path.relpath(args.out, REPO), len(lib_ex), len(lib_rep), len(reqs_rep), out["runtime_s"]))
    for label, reqs in (("EXEMPLAR", reqs_ex), ("representative", reqs_rep)):
        for r in reqs:
            ed = r["endpoint_distance"]
            c = r["electrophile_reach"].get("C397", {})
            print("[5b] %-14s %-9s span %.1f A (floor %d, comfortable at %s atoms) alpha %.0f beta %.0f "
                  "dih %s | C397 exact %s | wedge sites %d"
                  % (label, r["meta_basin_id"], ed["placement_span_A"], ed["span_floor_atoms"],
                     r["accessibility"]["n_atoms_for_comfortable_span"],
                     r["exit_vector_geometry"]["alpha_deg"], r["exit_vector_geometry"]["beta_deg"],
                     r["exit_vector_geometry"]["dihedral_deg"],
                     {k: v["exact_atoms"] for k, v in c.get("by_pendant", {}).items()},
                     len(r["wedge_element_sites"]["sites"])))
    for label, p in (("EXEMPLAR (recommended)", pair_ex), ("representative", pair_rep)):
        print("[5b] matched pair %-22s: %s  basin=%s wedge=%s clearance=%s  d=%s"
              % (label, p.get("status"), p.get("basin"),
                 (p.get("wedge_target_residue") or {}).get("uniprot_resid"),
                 p.get("e3_clearance_at_wedge_A"),
                 (p.get("d") or {}).get("construct_id")))
    return 0


def self_test():
    """Consistency checks that need no structures — run in CI and by the test suite."""
    for wh_key, wh in WARHEAD_HANDLE.items():
        for s1 in LINKER_SEGMENT:
            for e3 in ("vhl", "crbn"):
                if LINKER_SEGMENT[s1]["n"] == 0 or LINKER_SEGMENT[s1].get("amine_only"):
                    continue
                smi, n, k = build_smiles(e3, wh_key, s1)
                assert n == 1 + LINKER_SEGMENT[s1]["n"] + wh["tail_atoms"], (e3, wh_key, s1)
                assert k is None
                assert smi.count("(") == smi.count(")"), (e3, wh_key, s1)
                # no alpha-ketoamide, and no N,O-acetal: two motifs an earlier version emitted silently
                assert "NC(=O)C(=O)" not in smi, smi
                assert "C(=O)NCO" not in smi and "C(=O)NCCO" not in smi.replace("C(=O)NCCOC", "@"), smi
                for s2 in LINKER_SEGMENT:
                    if LINKER_SEGMENT[s2].get("acyl_only") or LINKER_SEGMENT[s2]["n"] == 0:
                        continue
                    smi2, n2, k2 = build_smiles(e3, wh_key, s1, s2, "cyac_me")
                    assert n2 == 1 + LINKER_SEGMENT[s1]["n"] + 1 + BRANCH_NODE_ATOMS + 1 \
                        + LINKER_SEGMENT[s2]["n"] + wh["tail_atoms"]
                    assert 1 <= k2 < n2, (e3, wh_key, s1, s2, k2, n2)
                    assert smi2.count("(") == smi2.count(")")
                    assert "NC(=O)C(=O)" not in smi2, smi2
                    assert "C(=O)NCO" not in smi2, smi2          # the N,O-acetal that was emitted before
                    assert "C(=O)NC(=O)N" not in smi2, smi2      # the acylurea that was emitted before
                    # ★ the identity: an atom that is the i-th from one end is the (n+1-i)-th from the other
                    k_e3 = 1 + LINKER_SEGMENT[s1]["n"] + 1 + 2
                    assert k2 + k_e3 == n2 + 1, (e3, wh_key, s1, s2, k2, k_e3, n2)
                    # and it must be strictly interior — a branch AT either anchor is not a branch
                    assert 1 <= k2 <= n2 - 1
    # a branch residue with no acyl segment on its N-side must REFUSE (it would make an amine, not an amide)
    try:
        build_smiles("vhl", "5amide", "s0", "a2", "pyr3")
    except ValueError:
        pass
    else:
        raise AssertionError("a branch residue with a bare N-terminus was accepted")
    # ring-digit renumbering must not collide and must refuse on overflow
    assert _renumber("c1ccccc1", 7) == "c7ccccc7"
    try:
        _renumber("c1ccc2ccccc2c1", 9)
    except ValueError:
        pass
    else:
        raise AssertionError("ring-closure digit overflow was not refused")
    print("[5b] self-test OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--basins", default=os.path.join(HERE, "nr4a3-orientation-basins.json"))
    ap.add_argument("--registry", default=os.path.join(HERE, "nr4a3-e3-arm-registry.json"))
    ap.add_argument("--atlas", default=os.path.join(HERE, "nr4a3-differential-surface-atlas.json"))
    ap.add_argument("--series", default=os.path.join(HERE, "congeneric-warhead-series.json"))
    ap.add_argument("--struct", default=os.path.join(REPO, "results", "nr4a3-matrix", "nr4a3-opened.pdb"))
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-linker-design.json"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
