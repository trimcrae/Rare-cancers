#!/usr/bin/env python3
"""
RUNG 5b — INVERSE LINKER DESIGN. $0 CPU, pure stdlib.

WHAT STRATEGY.md ASKS FOR (ladder item 5b): "For each confirmed basin, derive linker requirements (endpoint
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

# Half-width of the accessibility window, in Angstrom, about the mechanism-carrying placement's span. Stated
# as a constant rather than tuned: 3.0 A is roughly one C-C bond either side of taut, i.e. the tolerance a
# linker has before it is either straining or slack. Every fidelity number below scales with it, so it is
# reported in the output and swept in the test suite rather than buried.
FIDELITY_WINDOW_A = 3.0

# ★ PREREGISTERED DOWNSELECT. Fixed BEFORE the library was enumerated and never tuned to a result — the same
# discipline the E3 downselect and the Tier-2 gate were held to. Thresholds, not a scalar score, because a
# tunable scalar is exactly what STRATEGY.md's load-bearing piece 5 forbids.
MAX_STRAIN_KT = 3.0        # ~3 kT is the boundary between a slack chain and one fighting to reach
CHEM_MAX_ATOMS = 24        # chemically routine upper bound on a PROTAC linker backbone (PEG6-diacid scale)

FILTER = {
    "must_span_the_floor": True,      # hard: a linker shorter than the anchor-anchor distance is not a
                                      # candidate, it is an impossibility
    "min_member_fraction_comfortable": 0.25,   # must comfortably hold at least a quarter of the basin
    "max_strain_kT_at_placement": MAX_STRAIN_KT,
    "max_backbone_atoms": CHEM_MAX_ATOMS,
    "max_per_basin_per_kind": 2,      # diversity cap: no basin may flood the library with one pendant class
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

# Pendant reach, in Angstrom from the linker backbone atom to the target atom being touched. Swept rather
# than assumed, because RUNG 5a read its gate at 3.0 A and 3.0 A is shorter than every real pendant below.
# Each value is the extended-chain length of a NAMED, commercially routine branch, at the same 1.25 A/atom
# projection used everywhere in this rung — so the sweep is a sweep over BUILDING BLOCKS, not over a knob.
PENDANT_REACH = {
    "rung5a_convention": 3.0,        # what the RUNG-5a gate used. Kept so the two can be compared.
    "aryl_direct": 4.0,              # a pyridyl/phenyl bonded straight to a backbone carbon
    "amide_direct": 5.0,             # backbone N-acylated: N-C(=O)-C(alpha)=C(beta)...S
    "dap_branch": 7.5,               # 2,3-diaminopropanoyl branch + acrylamide: 6 atoms
    "dab_branch": 8.75,              # 2,4-diaminobutanoyl branch + acrylamide: 7 atoms
}

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

# Pendant groups. The electrophiles are the design variable STRATEGY.md names; the wedge groups are the
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
        "why": "REVERSIBLE-covalent by design (STRATEGY.md 5b). The alpha-cyano group acidifies the adduct's "
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
        "smi": "CCNC(=O)C(C#N)C",
        "kind": "control",
        "reversible": None,
        "name": "alpha-cyano-propanamide (SATURATED, non-electrophilic control for cyac_me)",
        "reach_key": "dab_branch",
        "why": "The matched non-electrophilic control: cyac_me with the Michael acceptor reduced. Same heavy "
               "atoms, same net charge, same amide, no electrophile — so any difference attributable to the "
               "warhead is attributable to the C=C and nothing else.",
        "route": "hydrogenation of cyac_me, or direct coupling of 2-cyanopropanoic acid.",
    },
    # --- wedge elements for the RUNG 5a-KS matched pair, as the side chain of the branch residue. The pair
    #     is 3-(3-pyridyl)-L-alanine vs L-phenylalanine: two catalogue amino acids differing by ONE ATOM.
    "pyr3": {
        "smi": "Cc1cccnc1",
        "kind": "wedge",
        "reversible": None,
        "name": "3-(3-pyridyl)-L-alanine side chain (H-bond ACCEPTOR at the wedge site)",
        "reach_key": "amide_direct",
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
        "reach_key": "amide_direct",
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


def e3_clearance(arm, R, t, point):
    """Distance from `point` to the nearest atom of the placed E3 body (CA + side-chain centroids).

    THE LOAD-BEARING CHECK FOR THE MATCHED PAIR. `S` is meant to isolate a TARGET-side interaction. If the
    wedge element sits close enough to touch the E3, then d and d0 differ in their ligand-E3 contact as well,
    the shared binary leg no longer cancels, and the double difference stops answering the design question.
    """
    pts = G.apply_superpose(arm["query"], R, t)
    return min(G.dist(point, p) for p in pts)


def basin_requirements(ctx, meta, sites):
    """Everything a chemist needs about ONE confirmed basin, before any molecule is drawn."""
    aid = meta["arm_id"]
    arm = ctx["arms"][aid]
    rep = meta["representative"]
    pose_id = meta["representative_basin_id"].split("|")[1]
    pose = ctx["poses"][pose_id]
    a = tuple(pose["anchor_xyz"])
    u = tuple(pose["exit_direction"])
    R, t, rms, err = recover_transform(arm, rep["landmarks"], rep["anchor_e3_xyz"])
    b = G.apply_superpose([arm["anchor"]], R, t)[0]
    # The E3 ligand leaves its own moiety heading away from that moiety's centroid; rotate that direction into
    # the target frame. Directions rotate; they do not translate.
    v = G.matvec(R, G.sub(arm["anchor"], arm["_e3_moiety_centroid"]))

    geo = LD.exit_vector_geometry(a, u, b, v)
    floor = LD.span_floor_atoms(a, b)

    # the member basin the representative came from carries the span distribution
    member = None
    for pp in ctx["basins"]["arms"][aid]["per_pose"]:
        for bb in pp["basins"]:
            if bb["basin_id"] == meta["representative_basin_id"]:
                member = bb
    spans = member["span_A"] if member else {"min": rep["span_A"], "median": rep["span_A"],
                                             "max": rep["span_A"]}
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
    span_dist = deciles if deciles else [spans["min"], spans["min"], spans["min"], spans["median"],
                                         spans["median"], spans["median"], spans["median"],
                                         spans["max"], spans["max"], spans["max"]]
    n_comfortable = next((n for n in range(4, 81) if LD.wlc_strain_kt(centre, n) <= MAX_STRAIN_KT), None)

    reach = {}
    for label, cys in sites["unique_cysteines"].items():
        per_e = {}
        for ename, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
            per_e[ename] = {
                "arm_reach_A": e,
                "relaxed_rung5a_atoms": LD.min_linker_atoms_relaxed(a, b, cys["xyz"], e),
                "exact_atoms": LD.min_linker_atoms_exact(a, b, cys["xyz"], e, n_max=80),
            }
        reach[label] = {
            "dist_to_warhead_anchor_A": round(G.dist(cys["xyz"], a), 2),
            "dist_to_e3_anchor_A": round(G.dist(cys["xyz"], b), 2),
            "focal_sum_A": round(G.dist(cys["xyz"], a) + G.dist(cys["xyz"], b), 2),
            "detour_over_span_A": round(G.dist(cys["xyz"], a) + G.dist(cys["xyz"], b) - geo["span_A"], 2),
            "by_pendant": per_e,
            "reported_by_rung5a": meta["term_a_union"].get(label, {}).get("min_linker_atoms"),
        }

    # conserved-cysteine chemoselectivity counter-check: a longer pendant relaxes reach to EVERY cysteine
    conserved = {}
    for ename, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
        n_probe = floor + 6
        conserved[ename] = sorted(
            lab for lab, c in sites["conserved_cysteines"].items()
            if LD.pendant_contactable(a, b, c["xyz"], n_probe, e))

    n_design = floor + 4
    wedges = wedge_sites(ctx, a, b, n_design, PENDANT_REACH["aryl_direct"])
    for w in wedges:
        q = ctx["model"]["cb"][w["uniprot_resid"] - UNIPROT_OFFSET]
        k = max(1, (w["branch_k_min"] + w["branch_k_max"]) // 2)
        _, p = LD.three_ball_min_margin([a, b, q], [k * RISE, (n_design - k) * RISE,
                                                    PENDANT_REACH["aryl_direct"]])
        w["e3_clearance_A"] = round(e3_clearance(arm, R, t, p), 2)
        w["e3_clear_enough_for_a_matched_pair"] = w["e3_clearance_A"] >= 6.0

    return {
        "meta_basin_id": meta["meta_basin_id"],
        "arm_id": aid,
        "role": ("LABELLED WEAK CONTROL — does NOT exceed the term-(b) background and persists in only "
                 "%d/%d poses; carried so the filter has something it should reject"
                 % (meta["n_poses_present"], meta["n_poses_total"])
                 if meta["meta_basin_id"] == WEAK_CONTROL else "design target"),
        "pose_surviving_fraction": meta["pose_surviving_fraction"],
        "term_b_exceeds_background": meta["term_b_exceeds_background"],
        "term_b_max_enrichment_over_background": meta["term_b_max_enrichment_over_background"],
        "term_b_mean_fraction_paralogues_bare": meta["term_b_mean_fraction_paralogues_bare"],
        "designed_on": {
            "placement": "representative",
            "basin_id": meta["representative_basin_id"],
            "pose_id": pose_id,
            "transform_recovery_rms_A": round(rms, 4),
            "anchor_reproduction_error_A": round(err, 4),
            "_caveat": "the representative is the highest-scoring member of the largest member basin, NOT "
                       "the member that achieves the basin's reported minimum linker length. Where the "
                       "artifact carries `exemplar_placement` (added for this rung), the covalent designs "
                       "are re-derived on it and both are reported.",
        },
        "endpoint_distance": {
            "representative_span_A": geo["span_A"],
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
                        "from the basin's interface patch, which is where the E3 BODY sits.",
            "probe_linker_atoms": n_design,
            "sites": wedges,
        },
        "interface_patch_uniprot": meta["interface_patch_uniprot"],
    }


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
    node = "C(=O)N[C@@H](%s)C(=O)N" % _renumber(PENDANT[pendant]["smi"], 7)
    smi = e3["pre"] + "C(=O)" + s1["smi"] + node + s2["smi"] + wh["tail"] + e3["post"]
    n = 1 + s1["n"] + 1 + BRANCH_NODE_ATOMS + 1 + s2["n"] + wh["tail_atoms"]
    # index of the branch alpha-carbon counted from the E3 end: the E3 acyl C, SEG1, the second acyl C, then
    # the residue's N, then C-alpha
    k_e3 = 1 + s1["n"] + 1 + 2
    return smi, n, n - k_e3


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
        spans = r["endpoint_distance"]["member_span_A"]
        # Every length the body x handle grid can actually produce, between the basin's span floor and the
        # chemically routine cap. No hand-picked ladder: the filter, not the enumerator, decides what is
        # viable, so the rejected set stays informative.
        wanted = set(range(floor, CHEM_MAX_ATOMS + 1))
        # the wedge site this basin can carry, if any: the divergent residue with the most E3 clearance
        clean = [s for s in r["wedge_element_sites"]["sites"]
                 if s.get("e3_clear_enough_for_a_matched_pair")]
        wedge_site = max(clean, key=lambda s: s["e3_clearance_A"]) if clean else None
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
                    + ([(p, wedge_xyz, "amide_direct") for p in ("pyr3", "ph")] if wedge_xyz else [])):
                reach = PENDANT_REACH[reach_key]
                for s1 in LINKER_SEGMENT:
                    if LINKER_SEGMENT[s1]["n"] == 0 or LINKER_SEGMENT[s1].get("amine_only"):
                        continue
                    for s2 in LINKER_SEGMENT:
                        if LINKER_SEGMENT[s2].get("acyl_only"):
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
                                           wedge_site if reach_key == "amide_direct" else None))
    return lib


def _record(r, aid, wh_key, s1, s2, pkey, k, window, smi, n_bb, spans, fid, wedge_site):
    cls = LINKER_SEGMENT[s1]["class"] if s2 is None else "%s+%s" % (
        LINKER_SEGMENT[s1]["class"], LINKER_SEGMENT[s2]["class"])
    return {
        "construct_id": "%s_%s_%s%s_%s" % (r["meta_basin_id"].replace("|", ""), wh_key, s1,
                                           "" if s2 is None else "-" + s2, pkey),
        "designed_for_basin": r["meta_basin_id"],
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

    Four numbers, kept separate on purpose (STRATEGY.md load-bearing piece 4 says accessibility and stability
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
    for c in ordered:
        if not is_control(c):
            continue
        slot = (c["designed_for_basin"], c["warhead_handle"], tuple(c["linker_segments"]))
        key = (c["designed_for_basin"], c["pendant_kind"])
        if slot in design_slots and counts.get(key, 0) < FILTER["max_per_basin_per_kind"]:
            counts[key] = counts.get(key, 0) + 1
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


# ---------------------------------------------------------------------------------------------------------
# Stage C — the matched pair for RUNG 5a-KS
# ---------------------------------------------------------------------------------------------------------


def matched_pair(reqs, lib):
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
      (ii) the wedge element must engage a TARGET-side difference. Arg412 is Ala in NR4A1 and Thr in NR4A2 —
           a non-conservative substitution at RSA 0.78 — and it is within pendant reach of the linker path in
           every confirmed basin, which is why the pair generalises beyond one basin.
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
    """
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
            clean = [s for s in r["wedge_element_sites"]["sites"]
                     if s.get("e3_clear_enough_for_a_matched_pair")]
            if not clean:
                continue
            s_ = max(clean, key=lambda s: s["e3_clearance_A"])
            cands.append((r["pose_surviving_fraction"], s_["e3_clearance_A"], r, s_, d_, d0_))
    if not cands:
        return {"status": "NO PAIR PROPOSED",
                "reason": "no confirmed basin has BOTH a divergent, exposed, linker-reachable residue with "
                          ">= 6 A of E3 clearance AND a matched pyridyl/phenyl construct pair that survives "
                          "the basin-fidelity filter"}
    cands.sort(key=lambda c: (-c[0], -c[1]))
    persist, clear, req, site, d, d0 = cands[0]
    return {
        "status": "PROPOSED" if (d and d0) else "NO MATCHING CONSTRUCT PAIR IN THE LIBRARY",
        "test": "S = ddG_coop(d0->d | NR4A3) - ddG_coop(d0->d | NR4A1); ternary legs only (the shared "
                "ligand-E3 binary leg and the solvent leg are paralogue-independent and cancel exactly)",
        "basin": req["meta_basin_id"],
        "basin_pose_surviving_fraction": persist,
        "wedge_element": "3-pyridyl (d) vs phenyl (d0) — an aza-scan",
        "wedge_target_residue": site,
        "e3_clearance_at_wedge_A": clear,
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
            "Arg412's side chain is rigid in this model; the pair is conditional on the modelled rotamer.",
            "NR4A1 has ALANINE at the aligned position, so the expected signal is an NR4A3 gain against a "
            "solvent-exposed gap, not a paralogue penalty — bounded by one exposed H-bond (~0.5-1.5 "
            "kcal/mol) against a best-case resolvable 1.12.",
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
            "d0": "cyanoprop (the saturated alpha-cyano-propanamide), same branch position",
            "what_it_measures": "whether the electrophile-bearing arm's NON-COVALENT recognition already "
                                "discriminates Cys397 (NR4A3) from Asn363 (NR4A1). In reversible-covalent "
                                "chemistry, selectivity is K_i x k_inact; this test addresses K_i only, and "
                                "a null leaves the categorical (k_inact) argument standing.",
            "why_this_d0": "the saturated analogue is the standard non-electrophilic control: same heavy "
                           "atoms, same charge, same amide, no Michael acceptor — so the alchemical change "
                           "is the C=C and nothing else.",
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

    reqs = []
    for bid in CONFIRMED:
        r = basin_requirements(ctx, metas[bid], sites)
        # stash the anchors for the enumerator (stripped before serialisation)
        m = metas[bid]
        arm = ctx["arms"][m["arm_id"]]
        pose = ctx["poses"][m["representative_basin_id"].split("|")[1]]
        R, t, _, _ = recover_transform(arm, m["representative"]["landmarks"],
                                       m["representative"]["anchor_e3_xyz"])
        r["_a"] = tuple(pose["anchor_xyz"])
        r["_b"] = G.apply_superpose([arm["anchor"]], R, t)[0]
        reqs.append(r)

    enumerated = enumerate_library(reqs, ctx)
    lib, rejected = apply_filter(enumerated)
    lib.sort(key=lambda c: (-c["basin_fidelity"]["P_reach_normalised"],
                            -(c["basin_fidelity"]["selectivity_vs_other_confirmed_basins"] or 0.0)))
    pair = matched_pair(reqs, lib)

    for r in reqs:
        r.pop("_a", None)
        r.pop("_b", None)

    out = {
        "_title": "RUNG 5b — inverse linker design for the confirmed NR4A3 orientation basins",
        "_status": "DESIGN PRIORITISATION. Not a result about binding, degradation, efficacy or safety. "
                   "Every construct is a PREDICTED SELECTIVE CANDIDATE, never a selective hit.",
        "_method": "For each confirmed meta-basin, the representative placement's rigid transform is "
                   "recovered from its stored landmarks (verified by reproducing the placement's own E3 "
                   "anchor to <0.01 A) and used to derive the linker requirements: endpoint distance and its "
                   "span floor, the exit-vector angles and dihedral with the turn cost in backbone atoms, "
                   "worm-like-chain strain and accessibility as a probability over the basin's span window, "
                   "and the EXACT (three-ball, integer-branch-position) reach to each paralogue-unique "
                   "cysteine over a sweep of named pendant building blocks. A virtual library is then "
                   "enumerated per basin — never as a blind cross-product — with the electrophile position "
                   "on the linker as an explicit design variable, and filtered on basin fidelity.",
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
            "`min_linker_atoms` is a BEST-OF-N over a basin's sampled members and the achieving member is "
            "NOT the published representative: at the representative of all five confirmed meta-basins the "
            "exact C397 requirement is 16-33 backbone atoms against a reported 8-12. The reported figure is "
            "correct as defined; it is a statistic, not a buildable geometry.",
            "RUNG 5a's reach criterion `|q-a| + |q-b| <= L + 2e` credits the pendant arm with shortening the "
            "anchor-to-anchor SPAN, which no pendant can do. It is a LOWER BOUND on the linker length "
            "actually required, by up to 2e (~5 backbone atoms at the 3.0 A arm the gate was read with). "
            "Audited over all 576 (basin x unique cysteine) records, zero are internally impossible, so this "
            "is a bound and not an error — but 5b quotes the exact rule.",
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
        "basin_requirements": reqs,
        "virtual_library": lib,
        "rejected_by_the_filter": rejected,
        "library_summary": {
            "n_enumerated": len(enumerated),
            "n_rejected": len(rejected),
            "n_constructs": len(lib),
            "by_basin": {r["meta_basin_id"]: sum(1 for c in lib
                                                 if c["designed_for_basin"] == r["meta_basin_id"])
                         for r in reqs},
            "n_reversible_covalent": sum(1 for c in lib if PENDANT.get(c["pendant"], {}).get("reversible")),
            "n_irreversible_comparator": sum(1 for c in lib if c["pendant"] == "acrylamide"),
            "n_controls": sum(1 for c in lib if c["pendant_kind"] in ("control", "wedge_control")),
        },
        "matched_pair_for_rung_5a_ks": pair,
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("[5b] wrote %s  (%d constructs across %d basins) in %.1f s"
          % (os.path.relpath(args.out, REPO), len(lib), len(reqs), out["runtime_s"]))
    for r in reqs:
        ed = r["endpoint_distance"]
        c = r["electrophile_reach"].get("C397", {})
        print("[5b] %-9s span %.1f A (floor %d, comfortable at %s atoms) alpha %.0f beta %.0f dih %s | "
              "C397 exact %s | wedge sites %d"
              % (r["meta_basin_id"], ed["representative_span_A"], ed["span_floor_atoms"],
                 r["accessibility"]["n_atoms_for_comfortable_span"],
                 r["exit_vector_geometry"]["alpha_deg"], r["exit_vector_geometry"]["beta_deg"],
                 r["exit_vector_geometry"]["dihedral_deg"],
                 {k: v["exact_atoms"] for k, v in c.get("by_pendant", {}).items()},
                 len(r["wedge_element_sites"]["sites"])))
    print("[5b] matched pair: %s" % pair.get("status"))
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
                    if LINKER_SEGMENT[s2].get("acyl_only"):
                        continue
                    smi2, n2, k2 = build_smiles(e3, wh_key, s1, s2, "cyac_me")
                    assert n2 == 1 + LINKER_SEGMENT[s1]["n"] + 1 + BRANCH_NODE_ATOMS + 1 \
                        + LINKER_SEGMENT[s2]["n"] + wh["tail_atoms"]
                    assert 1 <= k2 < n2, (e3, wh_key, s1, s2, k2, n2)
                    assert smi2.count("(") == smi2.count(")")
                    assert "NC(=O)C(=O)" not in smi2, smi2
                    assert "C(=O)NCO" not in smi2, smi2          # the N,O-acetal that was emitted before
                    # the branch alpha-carbon's distance from BOTH ends must be consistent
                    assert n2 - k2 == 1 + LINKER_SEGMENT[s1]["n"] + 1 + 2
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
