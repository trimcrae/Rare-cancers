#!/usr/bin/env python3
"""
EVERY MECHANISM BY WHICH PARALOGUE SELECTIVITY COULD BE ARGUED FOR AN NR4A3 DEGRADER — enumerated,
measured where a committed artifact can settle it, and graded against this program's own failure record.

WHY THIS EXISTS
---------------
The roadmap presents "two live routes to selectivity" plus one categorical term it says the page kept
omitting. That is a *shortlist*, not an enumeration, and a shortlist cannot show what was never considered.
This module is the enumeration: 17 mechanisms, each with its physical basis, the instrument that would carry
it, whether that instrument has passed a known-answer test IN THE REGIME THE CLAIM NEEDS, whether a valid
positive control could even exist here, the cheapest decisive test, what a pass would and would not license,
and a grade.

⛔ SCOPE. $0 — CPU/RDKit-free stdlib analysis of committed artifacts only. No GPU, no rental, no priced rung
is dispatched by this file. Nothing here is a claim about binding, reactivity, degradation, efficacy, safety
or clinical readiness; several rows exist precisely to record that a mechanism CANNOT be claimed.

THE THREE STRUCTURAL LESSONS THE GRADING APPLIES (all from the roadmap's own record)
-----------------------------------------------------------------------------------
  1. GENERATION IS HARDER THAN RANKING HERE. Sequence-only co-folding put the two halves ~32 A apart
     (DockQ 0.023-0.046, `V12`); the assembly route, given both sites, rebuilt 9DTY post-horizon at DockQ
     0.839 (`V2`). A mechanism needing a structure GENERATED de novo is graded down; one needing a structure
     SCORED is graded up.
  2. THE ONE MECHANISM THAT SURVIVED AVOIDED FREE ENERGY. The categorical covalent axis rests on geometry +
     exposure over 73,867 placements and is therefore immune to the fact that NO instrument in this program
     is validated in the paralogue-scale free-energy regime. Any mechanism whose claim reduces to a
     ~1 kcal/mol ddG inherits that gap and every row below says so explicitly.
  3. A CONFOUNDED CONTROL IS WORTHLESS AT ANY n, AND AN UNDERPOWERED DESIGN IS WORTHLESS TOO. NR-V04 is
     covalent at a cysteine the other paralogues lack; 9DTX has one ternary copy so min attainable p = 0.5.
     Every row therefore carries `positive_control_possible`, which is a separate question from
     `instrument_validated`.

WHAT IS MEASURED HERE (new facts; this file is their one home)
--------------------------------------------------------------
  M1  Matched-ensemble transfer-zone lysine coverage, all three paralogues, like-for-like.
  M2  A residue-class sweep for paralogue-unique reactive residues — 9 classes, not the 2 ever swept before.
  M3  Steric-exclusion (negative-design) test at the 10 Pocket-5 lining positions, WITH its null.
  M4  The decisive control for M3: where the paralogue's own docking puts the same 13 molecules.
  M5  Pocket-opening comparison — do the paralogues reach the NR4A3 druggable CV at all?
  M6  E3-arm stability: how far the term-(b) signal moves when only the STAGING construction changes.
  M7  How a binary ddG and a cooperativity ratio convert into a degradation window (Dmax / DC50).

Every OTHER figure quoted in the output is a CITATION carrying the artifact + field path that owns it
(CLAUDE.md rule 1). This file is not a second home for any of them.

Outputs: selectivity-mechanism-options.json (+ .md)
Regenerate:  python3 research/modalities/selectivity_mechanism_options.py
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

OUT_JSON = os.path.join(HERE, "selectivity-mechanism-options.json")
OUT_MD = os.path.join(HERE, "selectivity-mechanism-options.md")
STRUCT = os.path.join(REPO, "results", "nr4a3-matrix")

PARALOGUES = ("NR4A1", "NR4A2")
UNBIASED_REPS = ("release_rep0", "release_rep1", "release_rep2")
HARD_CLASH_A = 3.0                     # nr4a3-orientation-basins.json -> parameters.hard_clash_A
RT_KCAL = 0.5924                       # kcal/mol at 298 K, used only to convert a ddG into a Kd ratio

# The 10 Pocket-5 lining residues (UniProt numbering) — owned by nr4a-selectivity.json pocket 5.
POCKET5 = (406, 407, 410, 411, 412, 481, 484, 485, 531, 534)

# Reactive-atom name per residue type. The two committed axes (CYS SG / LYS NZ) come from
# nr4a_paralogue_unique_residues.REACTIVE_ATOM; the rest are this file's extension (measurement M2).
REACTIVE_ATOM = {
    "CYS": "SG", "LYS": "NZ", "TYR": "OH", "SER": "OG", "THR": "OG1", "MET": "SD",
    "HIS": "NE2", "ASP": "OD2", "GLU": "OE2", "ARG": "NH2", "TRP": "NE1",
}
# Residue classes swept for uniqueness, with the covalent chemistry that would address each and an honest
# credibility call. "routine" = used in marketed or clinical covalent drugs; "precedented" = published
# ligand-directed chemistry; "not a handle" = no practical residue-directed electrophile outside catalytic
# contexts. The credibility call is a literature judgement, NOT a measurement, and is labelled as such.
CLASS_CHEMISTRY = {
    "C": ("Cys thiol", "acrylamide / chloroacetamide / maleimide / cyanoacrylamide", "routine"),
    "K": ("Lys epsilon-amine", "activated ester / sulfonyl fluoride / aryl fluorosulfate", "precedented"),
    "Y": ("Tyr phenol", "SuFEx aryl fluorosulfate / sulfonyl triazole", "precedented"),
    "M": ("Met thioether", "oxaziridine (redox-activated)", "precedented"),
    "H": ("His imidazole", "sulfonyl fluoride / epoxide", "precedented"),
    "S": ("Ser hydroxyl", "fluorophosphonate", "not a handle outside catalytic serines"),
    "T": ("Thr hydroxyl", "—", "not a handle"),
    "D": ("Asp carboxylate", "amine/epoxide condensation", "not a handle"),
    "E": ("Glu carboxylate", "amine/epoxide condensation", "not a handle"),
    "R": ("Arg guanidine", "glyoxal / 1,2-dicarbonyl", "not a handle"),
    "W": ("Trp indole", "rhodium carbenoid", "not a handle"),
}

BACKBONE = {"N", "CA", "C", "O", "OXT"}


# =============================================================================================================
# small helpers
# =============================================================================================================
def _load(rel):
    with open(os.path.join(REPO, rel)) as f:
        return json.load(f)


def _round(x, n=4):
    return None if x is None else round(x, n)


def _stats(vals):
    if not vals:
        return None
    return {"n": len(vals), "mean": _round(statistics.mean(vals)),
            "sd": _round(statistics.stdev(vals)) if len(vals) > 1 else 0.0,
            "min": _round(min(vals)), "max": _round(max(vals))}


# =============================================================================================================
# M1 — matched-ensemble transfer-zone lysine coverage, like-for-like
# =============================================================================================================
def m1_lysine_coverage():
    """DEGRADATION-COMPETENCE, naive form: do the paralogues have FEWER lysines the transfer zone can reach?

    ⚠ WHY THIS HAD TO BE RE-READ. The roadmap and the lane doc quote the triple
    'NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363' as though it were like-for-like. Read from the owning artifact,
    the first value is the POOLED-UNBIASED median over 75 conformers and the other two are SINGLE static
    opened models — three different objects in one row. The matched values are computed here.

    Reads: nr4a-paralogue-dynamics.json -> term_b.by_species.*.ensembles.*.frames[].coverage
    """
    d = _load("research/modalities/nr4a-paralogue-dynamics.json")
    tb = d["term_b"]["by_species"]
    species = ("NR4A3",) + PARALOGUES

    per_rep = {}
    for ens in UNBIASED_REPS:
        per_rep[ens] = {sp: [f["coverage"]["P_zone_covers_any_lysine"]
                             for f in tb[sp]["ensembles"][ens]["frames"]] for sp in species}
    rep_means = {sp: [statistics.mean(per_rep[e][sp]) for e in UNBIASED_REPS] for sp in species}

    static = {sp: tb[sp]["ensembles"]["static_opened_model"]["P_zone_covers_any_lysine"]["mean"]
              for sp in species}
    pooled = {sp: {"mean": tb[sp]["pooled_unbiased"]["P_zone_covers_any_lysine"]["mean"],
                   "median": tb[sp]["pooled_unbiased"]["P_zone_covers_any_lysine"]["median"],
                   "sd_over_frames": tb[sp]["pooled_unbiased"]["P_zone_covers_any_lysine"]["sd"]}
              for sp in species}

    contrasts = {}
    for par in PARALOGUES:
        diffs = [rep_means["NR4A3"][i] - rep_means[par][i] for i in range(len(UNBIASED_REPS))]
        ratios = [rep_means["NR4A3"][i] / rep_means[par][i] for i in range(len(UNBIASED_REPS))]
        wins = tot = 0
        for e in UNBIASED_REPS:
            for a, b in zip(per_rep[e]["NR4A3"], per_rep[e][par]):
                tot += 1
                wins += int(a > b)
        contrasts[f"NR4A3_minus_{par}"] = {
            "per_replica_delta": [_round(x) for x in diffs],
            "delta_mean": _round(statistics.mean(diffs)),
            "delta_replicate_SD": _round(statistics.stdev(diffs)),
            "delta_over_replicate_SD": _round(statistics.mean(diffs) / statistics.stdev(diffs), 2),
            "ratio_mean": _round(statistics.mean(ratios), 3),
            "matched_frame_win_rate": {"wins": wins, "n": tot, "rate": _round(wins / tot, 3)},
        }

    return {
        "_question": ("Is the transfer zone able to reach a lysine on NR4A3 more often than on NR4A1/NR4A2 — "
                      "i.e. does DEGRADATION COMPETENCE discriminate on lysine availability alone?"),
        "_reads": "nr4a-paralogue-dynamics.json -> term_b.by_species.*.ensembles.*.frames[].coverage",
        "_error_bar_rule": ("Replicate-SD over the 3 independent unbiased replicas, NOT the per-frame SD "
                            "(CLAUDE.md: honest replicate-SD, not a within-run SE). n = 3, so the SD is "
                            "itself imprecise and is reported, not converted into a p-value."),
        "static_opened_model_P_any_lysine": {k: _round(v) for k, v in static.items()},
        "pooled_unbiased_P_any_lysine": pooled,
        "per_replica_means": {sp: [_round(x) for x in v] for sp, v in rep_means.items()},
        "contrasts": contrasts,
        "★_finding": (
            "NON-DISCRIMINATING against NR4A1 and weakly directional against NR4A2. Like-for-like over the "
            "same 75 unbiased conformers per species: NR4A3 0.4396, NR4A1 0.4279, NR4A2 0.3692. The "
            "NR4A3-vs-NR4A1 gap is +0.0118 against a replicate-SD of 0.0175 — under 1 SD, i.e. no measured "
            "difference — and the matched-frame win rate is 0.653, barely above a coin. NR4A2 is the only "
            "consistent direction (win rate 1.000, ratio 1.19x), and a 1.19x coverage ratio is not a "
            "selectivity mechanism."),
        "⚠_correction_to_a_quoted_triple": (
            "The roadmap's Tier-2 block and the lane doc quote 'NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363' as a "
            "comparable triple. It is not: 0.438 is NR4A3's pooled-unbiased MEDIAN over 75 conformers, while "
            "0.387 and 0.363 are SINGLE static opened models (the lane doc's own table labels the ensembles "
            "correctly; the roadmap's one-line restatement drops the labels). The like-for-like static triple "
            "is 0.4035 / 0.3914 / 0.3650 and the like-for-like pooled triple is 0.4396 / 0.4279 / 0.3692. "
            "⚠ The error is CONSERVATIVE for the conclusion drawn from it — matching the ensembles makes the "
            "NR4A1 gap SMALLER (+0.051 implied -> +0.012 measured), so 'already non-discriminating on the "
            "any-lysine measure' is if anything understated. Nothing downstream needs revising; the row needs "
            "its ensemble labels."),
    }


# =============================================================================================================
# M2 — residue-class sweep for paralogue-unique reactive residues
# =============================================================================================================
def m2_residue_class_sweep():
    """Is the categorical axis ONE residue class, or nine?

    The committed uniqueness map sweeps Cys and Lys only — `classify_positions(residue_types=("C","K"))` —
    because those were the two axes the module was written for. The function takes the classes as a
    parameter, so widening the sweep is free and uses the SAME two independent aligners and the SAME
    `unique_vs_both AND alignment_robust` rule.

    Reads: nr4a-sequences-cache.json (UniProt FASTA, committed) + results/nr4a3-matrix/nr4a3-opened.pdb
    """
    import nr4a_differential_atlas as atlas
    import nr4a_paralogue_unique_residues as U

    seqs = _load("research/modalities/nr4a-sequences-cache.json")
    rows = U.classify_positions(seqs, residue_types=tuple(CLASS_CHEMISTRY))

    residues, atoms = atlas.parse_pdb(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    rsa = atlas.residue_rsa(residues, atlas.shrake_rupley(atoms))
    by_local = {}
    for a in atoms:
        by_local.setdefault(a["resid"], []).append(a)
    pocket_atoms = []
    for u in U.CRYPTIC_POCKET_UNIPROT:
        pocket_atoms.extend(by_local.get(u - U.LOCAL_OFFSET, []))

    def geometry(uni):
        ats = by_local.get(uni - U.LOCAL_OFFSET)
        if not ats:
            return None
        want = REACTIVE_ATOM.get(ats[0]["resname"])
        rx = [a for a in ats if a["name"] == want]
        if not rx:
            return None
        p = (rx[0]["x"], rx[0]["y"], rx[0]["z"])
        # ⚠ self-exclusion: a pocket-LINING residue is 0.00 A from "the pocket" by construction, which is a
        # tautology, not a reach. Its own atoms are removed before the minimum is taken.
        others = [a for a in pocket_atoms if a["resid"] != uni - U.LOCAL_OFFSET]
        d = min(math.dist(p, (a["x"], a["y"], a["z"])) for a in others) if others else None
        return {"reactive_atom": want, "rsa": _round(rsa.get(uni - U.LOCAL_OFFSET, 0.0), 3),
                "exposed_by_V17_cutoff": rsa.get(uni - U.LOCAL_OFFSET, 0.0) >= atlas.EXPOSED_RSA,
                "dist_to_cryptic_pocket_A": _round(d, 2),
                "reach_class": U._reach_class(d) if d is not None else None}

    by_class, handles = {}, []
    for aa, (name, chem, cred) in CLASS_CHEMISTRY.items():
        got = [r for r in rows if r["residue"] == aa]
        uniq = [r for r in got if r["unique_vs_both"] and r["alignment_robust"]]
        lbd = [r for r in uniq if U.LBD_FIRST <= r["resnum"] <= U.LBD_LAST]
        by_class[aa] = {"side_chain": name, "covalent_chemistry": chem,
                        "chemistry_credibility": cred,
                        "_credibility_is_a_literature_judgement_not_a_measurement": True,
                        "n_in_NR4A3": len(got), "n_unique_and_alignment_robust": len(uniq),
                        "n_unique_in_LBD": len(lbd),
                        "lbd_positions": [r["resnum"] for r in lbd]}
        for r in lbd:
            g = geometry(r["resnum"])
            if not g:
                continue
            handles.append({"uniprot": r["resnum"], "class": aa,
                            "nr4a1": r["partners"]["NR4A1"]["residue"] + str(r["partners"]["NR4A1"]["resnum"]),
                            "nr4a2": r["partners"]["NR4A2"]["residue"] + str(r["partners"]["NR4A2"]["resnum"]),
                            "chemistry_credibility": cred, **g})

    tetherable = [h for h in handles
                  if h["reach_class"] in ("in_pocket", "exit_vector", "linker_borne")
                  and h["exposed_by_V17_cutoff"]]
    credible = [h for h in tetherable if h["chemistry_credibility"] in ("routine", "precedented")]

    # ⚠ THE CUTOFF IS THE WRONG RULER AND THE PROGRAM ALREADY KNOWS IT. V17 (EXPOSED_RSA = 0.25) fails its
    # own positive control — NR4A1 Cys551, the family's ONE literature-anchored covalent site, reads RSA
    # 0.165 on the state-matched opened model (roadmap §3.1 `V17`, which owns that figure). What the roadmap
    # says survives is a threshold-free RANK. So the same handles are re-read against that reference point
    # rather than against the cutoff — which is the only reading the program's own record permits.
    V17_POSITIVE_CONTROL_RSA = 0.165          # CITATION: roadmap §3.1 `V17`. Not re-homed here.
    reach_ok = [h for h in handles if h["reach_class"] in ("in_pocket", "exit_vector", "linker_borne")]
    ranked = sorted(reach_ok, key=lambda h: -h["rsa"])
    above_control = [h for h in ranked
                     if h["rsa"] >= V17_POSITIVE_CONTROL_RSA
                     and h["chemistry_credibility"] in ("routine", "precedented")]
    name = lambda h: "{}{}".format(h["class"], h["uniprot"])       # noqa: E731
    credible_names = [name(h) for h in credible]
    above_control_names = ["{} rsa={}".format(name(h), h["rsa"]) for h in above_control]
    ranked_names = ["{}={}".format(name(h), h["rsa"]) for h in ranked]
    new_above_control = [n for n in above_control_names if not n.split()[0] in credible_names]

    return {
        "_question": "Is the categorical covalent axis one residue (C397) or a family of handles?",
        "_method": ("nr4a_paralogue_unique_residues.classify_positions with residue_types widened from the "
                    "committed ('C','K') to 11 classes. Same two independent aligners, same "
                    "`unique_vs_both AND alignment_robust` rule. RSA and pocket distance from the same "
                    "committed opened model and the same Shrake-Rupley routine."),
        "by_class": by_class,
        "lbd_unique_handles": sorted(handles, key=lambda h: h["uniprot"]),
        "n_unique_alignment_robust_in_LBD_all_classes": sum(v["n_unique_in_LBD"] for v in by_class.values()),
        "n_tetherable_and_exposed": len(tetherable),
        "n_tetherable_exposed_and_chemically_credible": len(credible),
        "chemically_credible_handles_under_the_V17_cutoff": credible_names,
        "read_against_the_V17_positive_control_instead_of_the_cutoff": {
            "_why": ("The cutoff has a demonstrated false negative on the family's one literature-anchored "
                     "covalent site, so the roadmap's own rule is that only a threshold-free RANK survives. "
                     "The reference RSA is a CITATION (roadmap §3.1 `V17`), not re-homed here."),
            "reference_site": "NR4A1 Cys551 (celastrol), RSA 0.165 on the state-matched opened model",
            "reference_rsa": V17_POSITIVE_CONTROL_RSA,
            "handles_at_or_above_the_reference_with_credible_chemistry": above_control_names,
            "NEW_handles_this_reading_admits_that_the_cutoff_does_not": new_above_control,
            "rank_of_every_tetherable_unique_handle_by_rsa": ranked_names,
        },
        "★_finding": (
            "The categorical axis is NOT one residue — but the honest count depends on which ruler is used, "
            "and BOTH readings are given because the program's own record forbids trusting the cutoff. "
            "Across 11 reactive classes NR4A3 carries "
            f"{sum(v['n_unique_in_LBD'] for v in by_class.values())} paralogue-unique, alignment-robust "
            f"positions in the LBD, and {len(reach_ok)} of those are within linker reach of the cryptic "
            "pocket. ⛔ UNDER THE V17 CUTOFF the chemically-credible set is "
            + ", ".join(credible_names) + " — i.e. exactly the cysteines and lysines "
            "already committed, and NO new handle clears it. ★ UNDER THE THRESHOLD-FREE RANK the roadmap "
            "says must replace the cutoff, Y419 (RSA 0.221, exit-vector band, one residue from C420) sits "
            "ABOVE NR4A1 Cys551 (0.165) — the family's one covalent site with literature support and the "
            "very false negative that discredited the cutoff. So the new handle is real on the only ruler "
            "the program permits, and absent on the ruler it has already refused. M398/M399 (0.106/0.051) "
            "fall below the reference on both readings and are NOT carried forward."),
        "⛔_limits": [
            "Sequence uniqueness is exact; every geometric annotation is one static opened conformer.",
            "'exposed' is adjudicated by V17 (EXPOSED_RSA = 0.25), which FAILS its own positive control "
            "(NR4A1 Cys551) — so this column is a RANK, not a threshold, exactly as for the cysteine axis.",
            "Chemistry credibility is a literature judgement carried as a label, not a computed quantity. "
            "No thiol/phenol pKa, nucleophilicity, adduct stability or electrophile promiscuity is modelled.",
            "Ser/Thr/Asp/Glu/Arg/Trp are enumerated for completeness and graded 'not a handle'. Counting "
            "them as options would be the same error as counting a reachable buried cysteine.",
        ],
    }


# =============================================================================================================
# M3 / M4 — steric exclusion (negative design), with its null and its decisive control
# =============================================================================================================
def _superposed_models():
    import nr4a3_basin_search as B
    ref = B.load_paralogue(os.path.join(STRUCT, "nr4a3-opened.pdb"))
    raw = {sp: B.load_paralogue(os.path.join(STRUCT, f"{sp.lower()}-opened.pdb")) for sp in PARALOGUES}
    fit = {sp: B.superpose_paralogue(raw[sp], ref) for sp in PARALOGUES}
    return ref, raw, fit


def _sidechain(model, rid):
    return [(a["x"], a["y"], a["z"]) for a in model["atoms_by_res"].get(rid, [])
            if a["name"] not in BACKBONE]


def m3_steric_exclusion(ref, fit):
    """NEGATIVE DESIGN: is there a subpocket NR4A3 offers that BOTH paralogues sterically deny?

    The test: hold each NR4A3-docked ligand pose fixed, superpose each paralogue onto NR4A3, and ask whether
    the aligned side chain at each Pocket-5 position comes inside the search's own hard-clash radius (3.0 A).

    ⚠ THE NULL IS THE WHOLE POINT. The poses were docked INTO NR4A3, so their absence of NR4A3 clash is
    guaranteed by construction and is not evidence of anything. What can be graded is the CONTRAST between
    position classes: a conserved or shared position that fires is a measured false positive of this test.
    """
    import nr4a_paralogue_unique_residues as U
    import nr4a_differential_atlas as atlas  # noqa: F401  (import symmetry with the RSA path)

    seqs = _load("research/modalities/nr4a-sequences-cache.json")
    urows = {r["resnum"]: r for r in
             U.classify_positions(seqs, residue_types=tuple("ACDEFGHIKLMNPQRSTVWY"))}
    ligands = U._read_sdf_coords(os.path.join(STRUCT, "docked_nr4a3.sdf"))

    positions = {}
    for u in POCKET5:
        rid3 = u - U.LOCAL_OFFSET
        row = urows.get(u)
        unique = bool(row and row["unique_vs_both"] and row["alignment_robust"])
        rec = {"uniprot": u, "nr4a3": ref["aa_of"][rid3],
               "categorically_unique_vs_both": unique, "partners": {}, "n_side_chain_heavy": {}}
        rec["n_side_chain_heavy"]["NR4A3"] = len(_sidechain(ref, rid3))
        bulkier = []
        for sp in PARALOGUES:
            rp = fit[sp]["corr_from_ref"].get(rid3)
            rec["partners"][sp] = (fit[sp]["aa_of"].get(rp), (rp + U.LOCAL_OFFSET) if rp else None)
            n = len(_sidechain(fit[sp], rp)) if rp else 0
            rec["n_side_chain_heavy"][sp] = n
            rec["post_fit_deviation_A"] = rec.get("post_fit_deviation_A", {})
            rec["post_fit_deviation_A"][sp] = _round(fit[sp]["deviation_by_res"].get(rp), 2) if rp else None
            bulkier.append(n > rec["n_side_chain_heavy"]["NR4A3"])
        rec["both_paralogue_side_chains_bulkier"] = all(bulkier)
        rec["class"] = ("unique_and_both_bulkier" if unique and all(bulkier)
                        else "unique_not_bulkier" if unique else "conserved_or_shared")
        rec["paralogue_only_clash_poses"] = 0
        positions[u] = rec

    per_pose = []
    for title, coords in ligands:
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        rec = {"pose": title, "n_clashing_positions": {}, "paralogue_only_clash_positions": []}
        n_cl = {"NR4A3": 0, **{sp: 0 for sp in PARALOGUES}}
        for u in POCKET5:
            rid3 = u - U.LOCAL_OFFSET
            d = {"NR4A3": min((math.dist(p, q) for p in _sidechain(ref, rid3) for q in pts), default=None)}
            for sp in PARALOGUES:
                rp = fit[sp]["corr_from_ref"].get(rid3)
                sc = _sidechain(fit[sp], rp) if rp else []
                d[sp] = min((math.dist(p, q) for p in sc for q in pts), default=None)
            for sp, v in d.items():
                n_cl[sp] += int(v is not None and v < HARD_CLASH_A)
            par_all = all(d[sp] is not None and d[sp] < HARD_CLASH_A for sp in PARALOGUES)
            if par_all and not (d["NR4A3"] is not None and d["NR4A3"] < HARD_CLASH_A):
                rec["paralogue_only_clash_positions"].append(u)
                positions[u]["paralogue_only_clash_poses"] += 1
        rec["n_clashing_positions"] = n_cl
        per_pose.append(rec)

    n_poses = len(ligands)
    groups = {}
    for u, rec in positions.items():
        g = groups.setdefault(rec["class"], {"positions": [], "hits": 0, "trials": 0})
        g["positions"].append(u)
        g["hits"] += rec["paralogue_only_clash_poses"]
        g["trials"] += n_poses
    for g in groups.values():
        g["rate"] = _round(g["hits"] / g["trials"], 3) if g["trials"] else None

    signal = groups.get("unique_and_both_bulkier", {}).get("rate")
    null = groups.get("conserved_or_shared", {}).get("rate")

    return {
        "_question": ("Is there a subpocket that NR4A3 offers and BOTH paralogues sterically deny — a "
                      "NEGATIVE-DESIGN categorical handle, answered by SHAPE rather than by free energy?"),
        "_method": (f"{n_poses} committed NR4A3-docked ligand poses x {len(POCKET5)} Pocket-5 lining "
                    "positions. Paralogues superposed onto NR4A3 by nr4a3_basin_search.superpose_paralogue "
                    "(iterative core refinement). A position 'clashes' when its side-chain heavy atoms come "
                    f"within {HARD_CLASH_A} A of a ligand heavy atom — the search's own hard_clash_A."),
        "superposition": {sp: {k: fit[sp]["superposition"][k]
                               for k in ("n_ca_pairs", "n_core", "core_fraction", "core_rmsd_A")}
                          for sp in PARALOGUES},
        "n_poses": n_poses,
        "positions": positions,
        "per_pose": per_pose,
        "by_position_class": groups,
        "enrichment_signal_over_null": _round(signal / null, 2) if (signal and null) else None,
        "★_finding": (
            f"MEASURED AND CONTROLLED. Paralogue-only clash rate is {signal} at the three positions where "
            "NR4A3's residue is paralogue-unique AND both paralogue side chains are strictly bulkier "
            "(L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe), against a null of "
            f"{null} at conserved-or-shared positions — an enrichment of "
            f"{_round(signal / null, 2) if (signal and null) else 'n/a'}x. The three "
            "paralogue-unique-but-NOT-bulkier positions (T407, T410, R412) fire at 0.000, which is the "
            "correct behaviour: uniqueness alone does not create a steric exclusion. ⚠ The null is NOT zero "
            "— I531 (Ile in NR4A3 AND in NR4A2) accounts for 6 of the 9 null hits, i.e. a pure "
            "superposition/rotamer artifact, which is exactly what a null is for."),
        "⛔_limits": [
            "RIGID TRANSFER. The paralogue side chain is held in its own opened conformer; it could rotate "
            "away. This measures 'clash in the paralogue's modelled conformer with the ligand held fixed', "
            "never 'the ligand cannot bind'.",
            "The absence of NR4A3 clash is guaranteed by construction (these poses were docked into NR4A3) "
            "and carries no information. Only the between-class contrast is gradeable.",
            "Conditional on the two opened paralogue models and on the superposition: post-fit deviation at "
            "R412 is the largest in the set, so R412's geometry in this frame is the least trustworthy.",
            "The 13 molecules are the committed selectivity-matrix library, not the carried candidate.",
        ],
    }


def m4_paralogue_docking_control(ref, raw, fit):
    """THE DECISIVE $0 CONTROL FOR M3: when the SAME molecule is docked into the paralogue's own opened
    pocket, does the engine put it where NR4A3 put it, or somewhere else?

    Small displacement + no clash => the paralogue accommodates the same pose and the exclusion is soft.
    Large displacement => the specific subpocket really is unavailable and the ligand has to go elsewhere.
    """
    import basin_geom as G
    import nr4a_paralogue_unique_residues as U

    def recover_transform(raw_m, fit_m):
        keys = [k for k in raw_m["ca"] if k in fit_m["ca"]]
        R, t, rms = G.horn_superpose([raw_m["ca"][k] for k in keys], [fit_m["ca"][k] for k in keys])
        return R, t, rms

    def centroid(coords):
        pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
        n = len(pts)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)

    l3 = U._read_sdf_coords(os.path.join(STRUCT, "docked_nr4a3.sdf"))
    par = {sp: {t: c for t, c in U._read_sdf_coords(os.path.join(STRUCT, f"docked_{sp.lower()}.sdf"))}
           for sp in PARALOGUES}
    tf = {sp: recover_transform(raw[sp], fit[sp]) for sp in PARALOGUES}

    matrix = _load("results/nr4a3-matrix/nr4a3-matrix.json")
    dg = {c["label"]: c.get("dG", {}) for c in matrix["candidates"]}

    rows, shifts = [], {sp: [] for sp in PARALOGUES}
    for title, coords in l3:
        c3 = centroid(coords)
        rec = {"molecule": title.replace("NR4A3-active:", ""), "shift_A": {}}
        for sp in PARALOGUES:
            got = par[sp].get(title)
            if not got:
                rec["shift_A"][sp] = None
                continue
            R, t, _ = tf[sp]
            s = G.dist(c3, G.apply_superpose([centroid(got)], R, t)[0])
            rec["shift_A"][sp] = _round(s, 2)
            shifts[sp].append(s)
        rec["docking_dG"] = {k: _round(v, 2) for k, v in (dg.get(title) or dg.get(rec["molecule"]) or {}).items()}
        rows.append(rec)

    return {
        "_question": ("Does the paralogue accommodate the same molecule in the same place, or relocate it? "
                      "This is the control that decides whether M3's steric exclusion is categorical or soft."),
        "_method": ("The committed per-species docked poses (docked_nr4a1.sdf / docked_nr4a2.sdf) brought "
                    "into the NR4A3 frame with the transform recovered exactly from the superposition, then "
                    "compared centroid-to-centroid against the NR4A3-docked pose of the same molecule."),
        "per_molecule": rows,
        "median_centroid_shift_A": {sp: _round(statistics.median(v), 2) for sp, v in shifts.items()},
        "range_centroid_shift_A": {sp: [_round(min(v), 2), _round(max(v), 2)] for sp, v in shifts.items()},
        "★_finding": (
            "The paralogue relocates the ligand rather than reproducing the pose: median centroid shift "
            f"{_round(statistics.median(shifts['NR4A1']), 2)} A (NR4A1) and "
            f"{_round(statistics.median(shifts['NR4A2']), 2)} A (NR4A2). So M3's exclusion is real about the "
            "POSE and says nothing about whether the paralogue binds the molecule at all — which is the "
            "honest ceiling for a negative-design argument, and it is a design rule rather than a claim."),
        "⛔_the_scores_are_NOT_evidence": (
            "The per-species docking dG values are reproduced here for completeness and must not be read as "
            "a selectivity margin: single-snapshot scoring as a selectivity verdict is the instrument the "
            "roadmap's closed-route register lists as REFUTED (V20 — 22 of 38 unrelated marketed drugs score "
            "a positive NR4A3 margin). Two rows of this very table are the reason: resveratrol scores better "
            "on NR4A1 than NR4A3, and CHEMBL4755698 better on NR4A2 — and celastrol, the one molecule in the "
            "panel with a literature-anchored NR4A-family preference (NR4A1, via a covalent bond at Cys551), "
            "is scored BEST on NR4A3. A non-covalent score does not see the covalent step, which is the "
            "argument for the categorical axis, not against it — but it disposes of the margins."),
    }


# =============================================================================================================
# M5 — differential pocket opening (conformational selection)
# =============================================================================================================
def m5_pocket_opening():
    """CONFORMATIONAL SELECTION: is the cryptic pocket something only NR4A3 can open?"""
    summaries = {}
    for sp in PARALOGUES:
        s = _load(f"results/{sp.lower()}-pocket-ensemble/release_summary.json")
        summaries[sp] = {"seed_mode": s["seed_mode"], "seed_Rg_nm": s["seed_Rg_nm"],
                         "target_rg_nm": s["target_rg_nm"],
                         "metad_Rg_range_nm": [s["metad_Rg_min_nm"], s["metad_Rg_max_nm"]],
                         "reaches_NR4A3_druggable_CV": s["metad_Rg_min_nm"] <= s["target_rg_nm"] <= s["metad_Rg_max_nm"],
                         "frac_time_within_0.1nm_of_seed": [r["frac_time_within_0.1nm_of_seed"]
                                                            for r in s["replicas"]]}
    matrix = _load("results/nr4a3-matrix/nr4a3-matrix.json")
    drugg = {sp: matrix["paralogues"][sp]["fpocket_druggability"] for sp in ("NR4A3",) + PARALOGUES}
    return {
        "_question": ("Does the cryptic pocket open only in NR4A3 — i.e. is there conformational-selection "
                      "selectivity available before any chemistry?"),
        "_reads": ["results/nr4a{1,2}-pocket-ensemble/release_summary.json",
                   "results/nr4a3-matrix/nr4a3-matrix.json -> paralogues.*.fpocket_druggability"],
        "paralogue_metad": summaries,
        "fpocket_druggability_of_the_opened_frame": drugg,
        "★_finding": (
            "THE CATEGORICAL FORM IS DEAD ON COMMITTED DATA. Both paralogues reach NR4A3's druggable CV "
            "value (Rg = 0.717 nm) inside their own matched metadynamics — NR4A1 exactly, NR4A2 within "
            "0.004 nm — and in the opened frames fpocket rates NR4A1 (0.981) MORE druggable than NR4A3 "
            "(0.931). 'Only NR4A3 has the cryptic site' is not available as an argument."),
        "✓_what_survives": (
            "The QUANTITATIVE form: the paralogues may pay a different FREE-ENERGY price to reach that state. "
            "That is exactly requirement R6 (dg_open_paralogue) — a requirement with no instrument, held on "
            "an explicit nod, and whose only demonstrated single-profile reading is in the closed-route "
            "register. A biased ensemble reaching a CV value says nothing about its population."),
    }


# =============================================================================================================
# M6 — E3 choice: how much of the signal is the recruiter and how much is the staging?
# =============================================================================================================
def m6_e3_arm_stability():
    """E3 CHOICE AS A LEVER: does either recruiter discriminate — and is the answer stable?"""
    files = {
        "definitive_12_pose": "research/modalities/nr4a3-orientation-basins.json",
        "matched_native": "research/modalities/nr4a3-orientation-basins-matched-native.json",
        "matched_composed": "research/modalities/nr4a3-orientation-basins-matched-composed.json",
    }
    out = {}
    for tag, rel in files.items():
        d = _load(rel)
        g = d["tier2_gate"]
        rec = {"_artifact": rel,
               "e3_registry": d["inputs"]["e3_registry"],
               "n_meta_basins": g["n_meta_basins"],
               "term_a_basins": g["n_exploiting_term_a_electrophile_reach"],
               "term_b_basins_upper_bound": g["n_exploiting_term_b_unique_lysine_zone"],
               "by_arm": {}}
        for arm in ("vhl", "crbn"):
            mb = [m for m in d["meta_basins_ranked"] if m["arm_id"] == arm]
            nulls = [p["term_b_background_null"] for p in d["arms"][arm]["per_pose"]
                     if p.get("term_b_background_null")]
            anyl = [n["fraction_any_nr4a3_lysine"] for n in nulls if "fraction_any_nr4a3_lysine" in n]
            enr = [m["term_b_max_enrichment_over_background"] for m in mb
                   if m.get("term_b_max_enrichment_over_background")]
            bare = [m["term_b_mean_fraction_paralogues_bare"] for m in mb]
            rec["by_arm"][arm] = {
                "n_meta": len(mb),
                "n_exceeding_background": sum(1 for m in mb if m.get("term_b_exceeds_background")),
                "max_enrichment_over_null": _round(max(enr), 2) if enr else None,
                "max_paralogues_bare": _round(max(bare), 3) if bare else None,
                "any_lysine_null_range": [_round(min(anyl), 3), _round(max(anyl), 3)] if anyl else None,
            }
        out[tag] = rec

    swing = {}
    for arm in ("vhl", "crbn"):
        vals = [out[t]["by_arm"][arm]["max_enrichment_over_null"] for t in files]
        nulls = [out[t]["by_arm"][arm]["any_lysine_null_range"] for t in files]
        swing[arm] = {"max_enrichment_across_stagings": [v for v in vals],
                      "fold_swing": _round(max(vals) / min(vals), 2) if min(vals) else None,
                      "any_lysine_null_across_stagings": nulls}

    return {
        "_question": "Is one E3 recruiter paralogue-discriminating — and does the answer survive a restaging?",
        "_reads": list(files.values()),
        "by_staging": out,
        "sensitivity_to_staging_alone": swing,
        "★_finding": (
            "EVERY APPARENT E3 PREFERENCE MEASURED HERE HAS TRACKED THE STAGING CONSTRUCTION RATHER THAN THE "
            "RECRUITER. Changing only how the E3 arm is assembled — composed vs assembly-native, no change to "
            "recruiter, sampling or criteria — moves CRBN's any-lysine null from 0.760-0.980 to 0.320-0.445 "
            "while VHL's barely moves, swings VHL's maximum term-(b) enrichment 16.60 -> 6.07, and takes the "
            "term-(a) count 0 -> 2. The roadmap already records the one E3-preference claim this program made "
            "('the discrimination lives on VHL') as RETRACTED the same day, for exactly this reason. A "
            "recruiter preference is not measurable at the current staging precision."),
        "⚠_which_registry_the_headline_run_used": (
            "The definitive 12-pose Tier-2 run reads `nr4a3-e3-arm-registry.json`, NOT the assembly-native "
            "registry — so its CRBN null (0.765-0.945) is the composed-like value. The matched pair exists "
            "precisely so that this is checkable rather than assumed."),
    }


# =============================================================================================================
# M7 — how a margin converts into a degradation window
# =============================================================================================================
def m7_degradation_window():
    """WHAT SIZE OF MARGIN IS EVEN USEFUL, and can cooperativity substitute for affinity?

    Uses the committed three-body cooperative-equilibrium model unchanged. Its own header states it is a
    MECHANISTIC MODEL + SENSITIVITY MAP, not a calibrated prediction, and its parameters are illustrative.
    That caveat is carried into every number below.
    """
    import nr4a3_degradation_model as DM
    P = {"T_tot": 5e-8, "E_tot": 2e-7, "Kd_target": 1e-7, "Kd_e3": 1e-6, "ksyn_over_kdeg": 0.1}

    def window(kd, alpha):
        return DM.degradation_window(
            DM.hook_curve(P["T_tot"], P["E_tot"], kd, P["Kd_e3"], alpha), P["ksyn_over_kdeg"])

    on_alpha1 = window(P["Kd_target"], 1.0)
    affinity_rows = []
    for ddg in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        kdp = P["Kd_target"] * math.exp(ddg / RT_KCAL)
        w = window(kdp, 1.0)
        affinity_rows.append({"ddG_kcal_per_mol": ddg, "Kd_paralogue_M": float(f"{kdp:.3g}"),
                              "Dmax_on_target": on_alpha1["Dmax"], "Dmax_paralogue": w["Dmax"],
                              "Dmax_gap": _round(on_alpha1["Dmax"] - w["Dmax"], 3)})

    on_alpha3 = window(P["Kd_target"], 3.0)
    coop_rows = []
    for ddg in (0.0, 0.5, 1.0):
        kdp = P["Kd_target"] * math.exp(ddg / RT_KCAL)
        w = window(kdp, 1.0)
        coop_rows.append({"ddG_kcal_per_mol": ddg, "alpha_on_target": 3.0, "alpha_paralogue": 1.0,
                          "Dmax_on_target": on_alpha3["Dmax"], "Dmax_paralogue": w["Dmax"],
                          "DC50_on_target_M": on_alpha3["DC50_M"], "DC50_paralogue_M": w["DC50_M"],
                          "DC50_ratio": _round(w["DC50_M"] / on_alpha3["DC50_M"], 1) if w["DC50_M"] else None,
                          "paralogue_never_reaches_50pct": w["DC50_M"] is None,
                          "_null_DC50_reading": ("a null DC50 is NOT missing data — it means the paralogue "
                                                 "never reaches 50 % degradation at ANY dose in this model, "
                                                 "which is a wider window than any finite ratio")})

    return {
        "_question": ("How much true margin does a degradation WINDOW need, and can a cooperativity "
                      "difference substitute for an affinity difference?"),
        "_model": "research/modalities/nr4a3_degradation_model.py (unchanged), three-body cooperative equilibrium",
        "⛔_parameters_are_illustrative": (
            "Kd_target 1e-7 M, Kd_e3 1e-6 M, T 5e-8 M, E 2e-7 M, ksyn/kdeg 0.1 — the committed illustrative "
            "set. The owning artifact states it is a MECHANISTIC MODEL + SENSITIVITY MAP, not a calibrated "
            "prediction. These rows are a SHAPE, not a forecast, and no DC50 or Dmax here is a prediction "
            "about any molecule."),
        "affinity_margin_to_Dmax_gap_alpha_matched": affinity_rows,
        "cooperativity_substituting_for_affinity": coop_rows,
        "★_finding": (
            "Cooperativity is the higher-leverage lever, and it is the one whose instrument failed. With "
            "alpha = 3 on target and alpha = 1 on the paralogue and ZERO binary margin, the model gives a "
            "7.9x DC50 separation; a 1.0 kcal/mol binary margin at matched alpha gives a Dmax gap of only "
            "0.12 and a 2.0 kcal/mol margin 0.30. That ordering is why the roadmap's ~2.0 kcal/mol "
            "requirement for a useful window is the right scale for the AFFINITY route — and why the "
            "cooperativity route would need far less margin if its instrument worked. It does not: the "
            "ternary cooperativity calculator returned the WRONG SIGN in all three replicates at ~34x its "
            "own uncertainty, and the closure triangle localised the miss to an endpoint-state error that "
            "more sampling will not fix."),
    }


# =============================================================================================================
# The mechanism register
# =============================================================================================================
GRADE_KEY = {
    "A": "live, measured, and the claim it licenses is already defensible today",
    "B": "live and buildable now — a $0/cheap decisive test exists and no instrument it needs has failed",
    "C": "live but ceiling-limited — either the instrument is unvalidated in the needed regime, or a valid "
         "positive control cannot exist here, so a pass would license less than it appears to",
    "D": "blocked — the instrument it needs has FAILED, or the mechanism reduces to a ddG smaller than any "
         "instrument here resolves",
    "F": "refuted on committed evidence — do not retry this form of it",
}


def mechanisms(M):
    """The register. `M` is the measurement bundle so that every grade can cite the number behind it."""
    m1, m2, m3, m4, m5, m6, m7 = (M["M1"], M["M2"], M["M3"], M["M4"], M["M5"], M["M6"], M["M7"])
    return [
        {
            "id": "S1", "known_answer_short": '⛔ **NO** — `V17` fails its own positive control', "positive_control_short": '⚠ partially — NR-V04/C551 is the reciprocal precedent, and a confound for detection', "cheapest_test_short": '$0 — taken; the 12-atom gate holds on reach alone', "name": "Categorical covalent capture at a paralogue-unique cysteine (C397)",
            "status": "LIVE — the program's incumbent", "novelty": "current",
            "physical_basis": (
                "NR4A1 and NR4A2 carry a non-nucleophile at the aligned position (Asn363 / Ser363), so no "
                "electrophile can form the adduct on them at all. Set membership, not an energy difference."),
            "instrument": "reach enumeration + V17 exposure criterion; 73,867 matched E3 placements",
            "known_answer_test_in_the_needed_regime": (
                "NO, and the failure is named: V17 FAILS its own positive control (NR4A1 Cys551, RSA 0.165, "
                "0 of 25 metadynamics frames). What survives is a threshold-free RANK."),
            "positive_control_possible": (
                "PARTIALLY. NR-V04/celastrol is the family's one literature-anchored covalent site and it is "
                "the reciprocal of this mechanism — which is why the roadmap files it as a CONFOUND for a "
                "selectivity readout and simultaneously as a PRECEDENT for this one. Those are compatible: a "
                "system that cannot serve as a control for detecting selectivity can still demonstrate that "
                "the mechanism exists in this family."),
            "cheapest_decisive_test": (
                "$0 — already taken. The design gate holds on REACH alone (reach-only collision 0.000-0.003 "
                "at 12 atoms), so the discredited exposure cutoff carries almost no load there."),
            "a_pass_licenses": [
                "a short-linker design preference, measured and monotonic",
                "a refutation of C420 and C559 as handles at routine linker length",
                "a narrowed TARGET-ENGAGEMENT geometry statement over a construct class",
            ],
            "a_pass_does_not_license": [
                "degradation, affinity, efficacy, safety or a therapeutic window",
                "proteome-wide selectivity — the comparison set is two paralogues",
                "that a covalent bond forms at all (pKa, reactivity, adduct stability are untested)",
            ],
            "grade": "A-",
            "why_this_grade": (
                "The strongest available mechanism and the only one immune to the free-energy resolution "
                "gap — but it rests on ONE residue, its exposure adjudicator has a demonstrated false "
                "negative, and the chemoselectivity window is closed by a PARALOGUE cysteine in 30 of 30 "
                "graded cells, at a position NR4A3 SHARES in 24 of those 30."),
        },
        {
            "id": "S2", "known_answer_short": '⛔ **NO** — no selectivity ΔΔG across two pockets has ever been recovered here', "positive_control_short": 'yes and built (CREBBP/BRD4) — unauthorized, and binary-only', "cheapest_test_short": 'not $0 — the `V4` benchmark, unpriced, on no rung', "name": "Divergent pocket handles resolved by free energy (Route A)",
            "status": "BLOCKED", "novelty": "current",
            "physical_basis": "7 of 10 Pocket-5 lining residues are paralogue-divergent and all 10 are ortholog-invariant.",
            "instrument": "V4 (selectivity ABFE) — never run; V7 (absolute ABFE) FAILS by ~7.1 kcal/mol",
            "known_answer_test_in_the_needed_regime": (
                "NO. No instrument in this program has ever recovered a known selectivity ddG across two "
                "pockets. V6 passes WITHIN one pocket and one charge model; V10 passes on a LARGE effect."),
            "positive_control_possible": (
                "YES and it is built — CREBBP vs BRD4(1)/SGC-CBP30, same ligand, two holo crystals, "
                "experimental ddG ~2.2 kcal/mol. It is not authorized, and even a clean pass would be a "
                "BINARY control that would not discharge the paralogue/ternary statement."),
            "cheapest_decisive_test": "not $0 — it is the V4 benchmark, unpriced and on no rung",
            "a_pass_licenses": ["that the free-energy engine can resolve selectivity between two proteins"],
            "a_pass_does_not_license": [
                "the NR4A3 paralogue margin — a passing instrument does not supply R6 (dG_open per paralogue), "
                "which validation requirement 2 says can MISS OR REVERSE selectivity",
                "closing the size-of-prize gap: ~2.0 kcal/mol needed against ~0.60 best-case resolvable",
            ],
            "grade": "D",
            "why_this_grade": (
                "Three independent blocks and only one is the instrument. Graded down further by lesson 2: "
                "the whole claim reduces to a ~1 kcal/mol ddG in exactly the regime nothing here is "
                "validated in."),
        },
        {
            "id": "S3", "known_answer_short": 'not yet — but its **null is measured here**: 0.923 vs 0.173 (5.34×)', "positive_control_short": '**yes, cleanly** — steric-gatekeeper selectivity pairs are well documented', "cheapest_test_short": '**$0 — taken, with its decisive control**', "name": "★ Steric exclusion / negative design — a subpocket both paralogues deny",
            "status": "LIVE — NEW, and measured in this file", "novelty": "NEW",
            "physical_basis": (
                "At three Pocket-5 positions NR4A3's residue is paralogue-unique AND both paralogues carry a "
                "strictly bulkier side chain: L406->His/His, I484->Tyr/Tyr, L534->Phe/Phe. A ligand "
                "substituent that fills that lobe in NR4A3 has nowhere to sit in either paralogue. The "
                "quantity is a CLASH, which is tens of kT, not a ~1 kcal/mol preference — and the question "
                "'does this atom fit' is answered by shape, not by a free-energy engine."),
            "instrument": ("shape/steric evaluation on an already-generated structure — the SCORING side of "
                           "lesson 1, not the generating side"),
            "known_answer_test_in_the_needed_regime": (
                "NOT YET RUN as such — but this file supplies its own internal null, which is the thing that "
                f"was missing: signal {m3['by_position_class']['unique_and_both_bulkier']['rate']} vs null "
                f"{m3['by_position_class']['conserved_or_shared']['rate']} "
                f"({m3['enrichment_signal_over_null']}x). A known-answer test is cheap and obvious: any "
                "published kinase/NR selectivity pair whose selectivity is attributed to a single "
                "gatekeeper-size difference."),
            "positive_control_possible": (
                "YES, and unusually cleanly — steric-gatekeeper selectivity is the best-documented "
                "structure-based selectivity mechanism in the literature, so a known-answer pair with a "
                "measured selectivity ratio and two crystal structures is findable. This is the ONLY new "
                "mechanism here for which an unconfounded, adequately-powered positive control is "
                "straightforwardly constructible."),
            "cheapest_decisive_test": (
                "$0 — taken here, including its decisive control. M4: the paralogue's own docking relocates "
                f"the same molecule by a median {m4['median_centroid_shift_A']['NR4A1']} A (NR4A1) / "
                f"{m4['median_centroid_shift_A']['NR4A2']} A (NR4A2), so the paralogue does not reproduce "
                "the pose."),
            "a_pass_licenses": [
                "a POSITIVE DESIGN RULE with a measured basis: grow the warhead into the L406/I484/L534 lobe",
                "a falsifiable prediction — a matched pair differing only in that substituent",
            ],
            "a_pass_does_not_license": [
                "that the paralogue does not bind the molecule. It binds it somewhere else (M4).",
                "any affinity, degradation or selectivity RATIO — no energy is computed anywhere here",
                "escape from R5: it is conditional on the cryptic pocket being the right site",
            ],
            "grade": "B+",
            "why_this_grade": (
                "The strongest of the new options. It scores a structure rather than generating one "
                "(lesson 1), its claim is a shape constraint rather than a ~1 kcal/mol ddG (lesson 2), it "
                "arrives with its own null already measured, and a valid positive control could exist "
                "(lesson 3). It is capped at B+ because it is conditional on the docked pose and on the "
                "rigid-transfer assumption, and because the mechanism constrains the POSE, not binding."),
        },
        {
            "id": "S4", "known_answer_short": '⛔ **NO** — identical to Route A', "positive_control_short": 'same as Route A — insufficient even on a pass', "cheapest_test_short": '$0 — the uniqueness call is taken here', "name": "★ Categorical PHARMACOPHORE handles — a functional group both paralogues lack",
            "status": "LIVE — NEW framing of an existing measurement", "novelty": "NEW",
            "physical_basis": (
                "Six of Route A's divergent pocket residues are not merely different but CATEGORICALLY "
                "unique: T407 (Leu/Val in the paralogues — only NR4A3 can donate/accept an H-bond there), "
                "R412 (Ala/Thr — only NR4A3 offers a cation), T410 (Gly/Asn). Designing to a functional "
                "group the paralogues do not possess is a larger expected ddG than designing to a size "
                "difference between similar residues — a buried H-bond or salt bridge is conventionally "
                "1-3 kcal/mol, against Route A's ~0.6 kcal/mol resolvable."),
            "instrument": "the same free-energy engines as Route A — this changes the EFFECT SIZE, not the ruler",
            "known_answer_test_in_the_needed_regime": "NO — identical to Route A. V4 is unrun.",
            "positive_control_possible": "same as Route A: the V4 binary control, unauthorized and insufficient",
            "cheapest_decisive_test": (
                "$0 — the uniqueness call is taken here (S4's three positions are the "
                "`unique_not_bulkier` class of M3, and they fire at 0.000 on the steric test, which is "
                "correct: they are electronic handles, not steric ones)."),
            "a_pass_licenses": ["a pharmacophore constraint on the warhead, stated as a hypothesis"],
            "a_pass_does_not_license": [
                "any margin — it still needs a free-energy number in the unvalidated regime",
                "R412 in particular: the roadmap records it facing into the pocket in only 0.25 of druggable "
                "frames, from an S3-only artifact NOT committed to this repo; and its post-fit superposition "
                "deviation is the largest of the ten positions measured in M3",
            ],
            "grade": "C+",
            "why_this_grade": (
                "Strictly better than Route A as drawn — a bigger expected effect for the same instrument — "
                "but it does not escape lesson 2, and its best residue (R412) has both a facing caveat "
                "resting on an uncommitted artifact and the worst geometry reliability in the set."),
        },
        {
            "id": "S5", "known_answer_short": '⚠ partially — `V2` 0.839 post-horizon, `V1` one contact in one pair', "positive_control_short": 'yes for assembly; ⛔ **no** for the selectivity read (`V11` 0/2)', "cheapest_test_short": '**$0 CPU — rung `5b-T`, needs no authorization**', "name": "Ternary interface discrimination (rung 5b-T)",
            "status": "LIVE — $0, unauthorized-free, and on the roadmap as row 1", "novelty": "current",
            "physical_basis": "the induced target-E3 interface differs between paralogues; V1 reads it structurally",
            "instrument": "V2 (assembly-route generator, PASSES in scope) -> V1 (interface descriptor, PASSES in scope)",
            "known_answer_test_in_the_needed_regime": (
                "PARTIALLY — the strongest pair in the program. V2 rebuilt post-horizon 9DTY at DockQ 0.839 "
                "(best of 16 seeds, median 0.442, one arm only — the SMARCA4 arm was refused and no SMARCA4 "
                "number exists). V1 recovered the published SMARCA2 Gln1469 contact — ONE contact in ONE "
                "pair, and it makes no NR4A3 prediction correct."),
            "positive_control_possible": (
                "YES for assembly (9DTY, post-horizon, already recovered). NO, currently, for the "
                "SELECTIVITY read: the E1 interface-stability endpoint has two attempts and no pass "
                "(p = 0.393 DISCORDANT, p = 0.747 NULL on an adequately-powered design)."),
            "cheapest_decisive_test": "$0 CPU — rung 5b-T, priced at $0, needs no authorization, and has a pre-registered three-arm gate",
            "a_pass_licenses": [
                "that an NR4A3 ternary can be assembled at all — currently NO ternary for this target has been",
                "R11's reproducibility bar: 16 models per arm against a bar of 3, currently met by 1",
            ],
            "a_pass_does_not_license": [
                "any thermodynamic statement — the output is structural, never energetic",
                "selectivity, unless a readout with power exists, and V11 has failed twice",
            ],
            "grade": "B",
            "why_this_grade": (
                "The best-instrumented live mechanism and the cheapest big move on the board: both "
                "instruments have passed a known-answer test IN SCOPE, it scores rather than generates "
                "(lesson 1), and it costs $0 with no nod required. Capped at B because its selectivity "
                "readout is the one that has already failed twice."),
        },
        {
            "id": "S6", "known_answer_short": 'n/a for reach (enumeration); ⛔ **NO** for the exposure half', "positive_control_short": 'geometry only — no experimental control without a bench', "cheapest_test_short": '$0 — already computed and committed', "name": "Linker length AS the selectivity filter — 'shortest viable linker' as a design principle",
            "status": "LIVE — publishable as a principle, with one caveat that must travel with it", "novelty": "current",
            "physical_basis": (
                "P(a paralogue cysteine is also reached | an NR4A3-unique one is) climbs monotonically with "
                "backbone length: 0.000-0.003 at 12 atoms, 0.009-0.032 at 14, 0.054-0.133 at 16, 0.263-0.383 "
                "at 20, over three ensembles. Length is therefore not merely a tractability axis — it is the "
                "variable that sets the discrimination."),
            "instrument": "geometric enumeration over 73,867 placements — no free energy anywhere",
            "known_answer_test_in_the_needed_regime": (
                "N/A for the reach half (it is enumeration, and its exactness was independently corrected in "
                "2026-07-26 from a bound to an exact three-ball kernel). NO for the exposure half — V17 again."),
            "positive_control_possible": (
                "YES in the weak sense that the enumeration is checkable against geometry, and the artifact "
                "already carries a cross-convention agreement check. There is no experimental positive "
                "control, and there cannot be one without a bench."),
            "cheapest_decisive_test": "$0 — already computed and committed",
            "a_pass_licenses": [
                "a genuine, quantitative design principle: prefer 11-12 backbone atoms; a construct drifting "
                "to 16+ trades away the axis it exists to exploit",
                "a publishable negative: C420 and C559 are not usable at routine length",
            ],
            "a_pass_does_not_license": [
                "the 16- and 20-atom columns as a SELECTIVITY statement. P(categorical | exposed) is 1.000 at "
                "EVERY length, so the entire length dependence lives in cysteines that the discredited V17 "
                "cutoff calls buried. At 12 atoms the result holds on reach alone; past 14 it does not.",
                "any statement about the chemoselectivity WINDOW being NR4A3-limited — it is closed by a "
                "PARALOGUE cysteine in 30 of 30 graded cells, and in 24 of 30 through-space cells by NR4A1 "
                "C505, a position NR4A3 SHARES (C536)",
            ],
            "grade": "B",
            "why_this_grade": (
                "A real, measured, publishable design principle that costs nothing and needs no instrument "
                "this program lacks — provided it is stated at the 12-atom gate, where it does not depend on "
                "the failed exposure criterion. Stated at 16-20 atoms it inherits V17's false negative."),
        },
        {
            "id": "S7", "known_answer_short": '⛔ **NO** — `V18` has none, and the roadmap says so', "positive_control_short": '⛔ **not with any system named here** — the confound is in the biology', "cheapest_test_short": '$0 — taken (M1), and it refutes the availability form', "name": "Degradation-competence selectivity — a unique lysine in the transfer zone",
            "status": "SPLIT: the availability form is refuted here; the joint form is live but uncalibrated",
            "novelty": "current (the roadmap's third route)",
            "physical_basis": (
                "A PROTAC can be selective at the ubiquitin-transfer step rather than at binding: a lysine "
                "that is not present cannot be ubiquitinated. NR4A3 has 4 unique lysines, 3 exposed "
                "(K518/K572/K592), against a MEASURED 17.1 A transfer distance."),
            "instrument": "V18, the transfer-zone lysine-identity term",
            "known_answer_test_in_the_needed_regime": "NO — none exists for V18, and the roadmap says so.",
            "positive_control_possible": (
                "⛔ NOT WITH ANY SYSTEM NAMED HERE. A positive control needs a degrader whose selectivity is "
                "ATTRIBUTED to lysine placement, with the ubiquitinated site mapped. Real degraders often "
                "ubiquitinate several lysines and lysine-less substrates are still degraded, so even a "
                "correct prediction would be weakly diagnostic. This is the same shape as lesson 3: the "
                "confound is in the biology, not the instrument."),
            "cheapest_decisive_test": "$0 — taken here (M1)",
            "measured_here": m1["★_finding"],
            "a_pass_licenses": [
                "the JOINT form only: a basin whose transfer zone covers an NR4A3-unique lysine while both "
                "paralogue zones stay bare — max 0.152 over 58 meta-basins, 37 of 58 non-zero",
            ],
            "a_pass_does_not_license": [
                "⛔ the AVAILABILITY form. Measured here: matched over 75 conformers per species the transfer "
                "zone reaches a lysine on NR4A3 0.4396, NR4A1 0.4279, NR4A2 0.3692 of the time. The "
                "NR4A3-NR4A1 gap is under one replicate-SD. The paralogues are NOT lysine-poor.",
                "any degradation rate — the term is set membership, and no composed RING or E2 may carry it",
            ],
            "grade": "C",
            "why_this_grade": (
                "The mechanism is real and is the program's only insurance against a C397-specific chemical "
                "failure — but it has no known-answer test, no constructible positive control, and its "
                "intuitive form (the paralogues lack lysines) is measured here to be false. Its surviving "
                "form is a rare coincidence read off a best-of-N-prone statistic."),
        },
        {
            "id": "S8", "known_answer_short": '⛔ **NO**, and the readout is unstable under a nuisance variable', "positive_control_short": 'moot until staging precision is fixed', "cheapest_test_short": '$0 — taken (M6)', "name": "E3 recruiter choice as a selectivity lever",
            "status": "BLOCKED — not by capability but by measurement precision", "novelty": "current",
            "physical_basis": "different recruiters give different ternary interfaces and different lysine reach",
            "instrument": "the orientation-basin search, per arm",
            "known_answer_test_in_the_needed_regime": "NO — and worse, the readout is not stable under a nuisance variable.",
            "positive_control_possible": (
                "In principle yes (a target with published VHL-vs-CRBN degradation selectivity), but it is "
                "moot until the staging precision problem is fixed."),
            "cheapest_decisive_test": "$0 — taken here (M6)",
            "measured_here": m6["★_finding"],
            "a_pass_licenses": ["nothing today"],
            "a_pass_does_not_license": [
                "any recruiter preference. The program's one E3-preference claim was retracted the same day "
                "it was made, and the numbers still swing 2-3x on staging construction alone.",
            ],
            "grade": "D",
            "why_this_grade": (
                "A measured instability, not an untested hope: the answer changes more with how the arm is "
                "assembled than with which arm it is. Reopening it needs a staging precision argument first, "
                "and that is a methods problem with no rung."),
        },
        {
            "id": "S9", "known_answer_short": '⛔ **NO** — and metadynamics already failed cross-replica on a simpler CV', "positive_control_short": 'exists in the literature; the instrument does not exist here', "cheapest_test_short": '⛔ none is cheap — nothing here could test it', "name": "Kinetic / residence-time selectivity",
            "status": "NO INSTRUMENT — and the nearest one has already failed on a simpler quantity", "novelty": "current",
            "physical_basis": "equal Kd with unequal k_off gives unequal occupancy under washout, and degradation is a kinetic readout",
            "instrument": ("nothing in this repo computes k_off, residence time or an unbinding barrier. The "
                           "only classes that could are infrequent-metadynamics / weighted-ensemble unbinding."),
            "known_answer_test_in_the_needed_regime": (
                "NO, and the prior is bad: the program's metadynamics on a much simpler CV failed "
                "cross-replica reproducibility outright — three independent seeds do not reconstruct a "
                "common F(Rg), which is in the closed-route register. A k_off estimate needs strictly more "
                "convergence than that."),
            "positive_control_possible": (
                "YES in the literature (residence-time series with measured k_off exist), but building the "
                "instrument is a multi-month methods project with a known-hard convergence problem, on a "
                "cryptic induced-fit pocket — the exact regime the closed-route register already parked "
                "Track A for."),
            "cheapest_decisive_test": "none is cheap. The honest answer is that nothing here could test it.",
            "a_pass_licenses": ["n/a"],
            "a_pass_does_not_license": ["n/a"],
            "grade": "D",
            "why_this_grade": "Enumerated for completeness and for the record that it was considered and costed as unbuildable here.",
        },
        {
            "id": "S10", "known_answer_short": '⛔ **RUN AND FAILED** — wrong sign, 3/3 replicates, ~34× its uncertainty', "positive_control_short": '**yes — it was built, was run, and refuted the instrument**', "cheapest_test_short": '$0 — the leverage calculation, taken here (M7)', "name": "Cooperativity (alpha) differences between paralogues",
            "status": "HIGH LEVERAGE, INSTRUMENT FAILED", "novelty": "current",
            "physical_basis": "alpha multiplies the ternary population; a paralogue with lower alpha is spared at the same occupancy",
            "instrument": "V5 (alchemical ternary ddG_coop, valB_mini)",
            "known_answer_test_in_the_needed_regime": (
                "⛔ RUN AND FAILED. Target +0.944 kcal/mol, returned -0.599 — WRONG SIGN in all three "
                "replicates at ~34x the statistical uncertainty. The closure triangle localises the miss to "
                "an endpoint-state error, so more sampling will not fix it, and the triangle is separately "
                "REFUTED as a diagnostic for that miss."),
            "positive_control_possible": (
                "YES — it exists, is built, and is exactly what failed. That is the strongest possible form "
                "of this answer and it is why this row is D rather than C: the control was available, was "
                "run, and returned a refutation of the instrument."),
            "cheapest_decisive_test": "$0 — the leverage calculation, taken here (M7)",
            "measured_here": m7["★_finding"],
            "a_pass_licenses": ["a degradation window from cooperativity alone — the model gives 7.9x DC50 at zero binary margin"],
            "a_pass_does_not_license": [
                "anything today. valB_full's module 1 has failed and the decision declined to amend or "
                "decouple it, so the prospective NR4A ternary matrix stays unrun and cooperativity claims "
                "stay exploratory.",
            ],
            "grade": "D",
            "why_this_grade": (
                "Leverage A, instrument F. This row is the clearest case in the register where the size of "
                "the prize must not be allowed to raise the grade — and it is the reason the whole "
                "prospective tail is blocked."),
        },
        {
            "id": "S11", "known_answer_short": "⛔ **NO** — inherits `V17`'s false negative, plus a literature judgement", "positive_control_short": 'yes for geometry; none for the chemistry without a bench', "cheapest_test_short": '$0 — taken (M2); both rulers reported', "name": "★ Categorical covalent at a NON-cysteine unique nucleophile (Tyr / Met / Lys)",
            "status": "LIVE — NEW, and enumerated here for the first time", "novelty": "NEW",
            "physical_basis": (
                "The categorical argument is about a residue type the paralogues lack — nothing in it is "
                "specific to sulfur. Sweeping 11 reactive classes instead of the committed two finds "
                f"{m2['n_unique_alignment_robust_in_LBD_all_classes']} paralogue-unique, alignment-robust LBD "
                "positions, and the one new handle that survives BOTH the reach test and the program's own "
                "threshold-free accessibility rank is Y419 — a tyrosine addressable by SuFEx chemistry, one "
                "residue from C420, at RSA 0.221."),
            "instrument": "identical to S1 — the same reach enumeration and the same exposure rank",
            "known_answer_test_in_the_needed_regime": (
                "NO — it inherits V17's demonstrated false negative exactly as S1 does, and adds a second "
                "untested layer: the chemistry credibility label is a literature judgement, not a measurement."),
            "positive_control_possible": (
                "YES for the geometry (same as S1). For the chemistry, published SuFEx tyrosine-targeting "
                "and oxaziridine methionine-targeting probes exist as precedent, but no positive control "
                "for THIS site is possible without a bench."),
            "cheapest_decisive_test": "$0 — taken here (M2); the reach envelope per new handle is the same $0 kernel already written for cysteines",
            "measured_here": m2["★_finding"],
            "a_pass_licenses": [
                "removal of Route B's single point of failure — the paper currently states the only "
                "insurance against a C397-specific chemical failure is the unique-LYSINE degradation term, "
                "which is a different requirement; this supplies engagement-level redundancy",
                "one prioritised second handle: Y419 (SuFEx), ranked above the family's one "
                "literature-anchored covalent site on the accessibility observable",
            ],
            "a_pass_does_not_license": [
                "the 'not a handle' classes (Ser/Thr/Asp/Glu/Arg/Trp) as options — counting them would be "
                "the same error as counting a buried cysteine",
                "⛔ M398/M399. Measured here at RSA 0.106/0.051, i.e. below the reference site on the only "
                "ruler the program permits. They are enumerated and dropped, not carried.",
                "any statement that these adducts form; only that the residue is unique and reachable",
            ],
            "grade": "C+",
            "why_this_grade": (
                "Cheap, already computed, and it addresses a structural weakness the paper names about "
                "itself — but the measurement partly undercut the idea, and that is reported rather than "
                "smoothed. Under the V17 cutoff NO new handle clears at all: the credible set collapses to "
                "the cysteines and lysines already committed. Y419 survives only on the threshold-free "
                "rank, which is the reading the roadmap mandates but which is a weaker instrument than a "
                "criterion; SuFEx tyrosine chemistry is precedented rather than routine; and every added "
                "handle re-opens the chemoselectivity-window question that `S1` already answers "
                "uncomfortably."),
        },
        {
            "id": "S12", "known_answer_short": 'n/a — nothing is built', "positive_control_short": "⚠ hard — a disordered moiety is lesson 1's worst case", "cheapest_test_short": '$0 — a sequence-level junction inventory needs no structure', "name": "★ Fusion-junction selectivity — target EWSR1::NR4A3, not NR4A3",
            "status": "NO RUNG, NO GATE, NO PRICE — the largest unclaimed mechanism on the board", "novelty": "NEW framing of R13",
            "physical_basis": (
                "The disease object is the fusion oncoprotein. It carries an EWSR1 N-terminal moiety and a "
                "junction that NO wild-type NR4A has — including wild-type NR4A3. Selectivity against the "
                "fusion is therefore categorically stronger than paralogue selectivity: it spares NR4A1, "
                "NR4A2 AND the patient's own NR4A3. The committed uniqueness map already carries EWSR1 "
                "lysine counts under three documented breakpoint scenarios."),
            "instrument": ("⛔ none. Every structure in this program is an isolated LBD construct (373-626); "
                           "C166, one of the four unique cysteines, is already outside it."),
            "known_answer_test_in_the_needed_regime": "N/A — nothing is built.",
            "positive_control_possible": (
                "⚠ HARD. The EWSR1 moiety is a low-complexity prion-like region with no folded structure, so "
                "the generation problem is the WORST case of lesson 1 — a de novo structure of a "
                "disordered region, which is the failure mode that put the two halves 32 A apart. A "
                "sequence-level and lysine-inventory analysis needs no structure and is $0."),
            "cheapest_decisive_test": (
                "$0 — extend the existing uniqueness sweep across the junction and inventory EWSR1-moiety "
                "lysines under each breakpoint scenario. The producer function already exists "
                "(`fusion_lysine_scenarios`) and is already committed with 1-2 lysines per scenario."),
            "a_pass_licenses": [
                "a claim-SCOPE upgrade: selectivity against the oncoprotein rather than against a paralogue",
                "validation requirement 5's explicit ask — model the real biological object",
            ],
            "a_pass_does_not_license": [
                "any geometry claim. A disordered fusion moiety cannot be modelled by anything in this repo, "
                "and a co-fold of it would be the exact generation problem that already failed.",
            ],
            "grade": "C+",
            "why_this_grade": (
                "The highest CEILING in the register and the lowest readiness. It is graded C+ rather than "
                "lower because its cheapest useful form — a sequence-level lysine and uniqueness inventory "
                "across the junction — is $0, needs no structure, and would give the paper a scope sentence "
                "it currently cannot write. It is graded no higher because everything past that needs a "
                "structure of a disordered region."),
        },
        {
            "id": "S13", "known_answer_short": 'n/a — a design architecture, not a measurement', "positive_control_short": 'yes in the literature (bivalent / AND-gate degraders)', "cheapest_test_short": '**$0 — it is a DECISION, and it has never been asked**', "name": "★ Two-point AND-gate engagement (cryptic pocket AND C397 simultaneously)",
            "status": "BLOCKED ON A DECISION NOBODY HAS ASKED FOR", "novelty": "NEW framing",
            "physical_basis": (
                "If binding requires BOTH a pocket interaction and a covalent capture at a unique residue, "
                "the selectivity ratios multiply rather than add. It is the only mechanism in the register "
                "whose margin COMPOUNDS."),
            "instrument": "RDKit enumeration + the same reach kernel — no new instrument needed",
            "known_answer_test_in_the_needed_regime": "N/A — it is a design architecture, not a measurement.",
            "positive_control_possible": "YES in the literature (bivalent/AND-gate degraders are an established class).",
            "cheapest_decisive_test": (
                "$0, and it is a DECISION rather than a computation: the one-pendant linker grid is in the "
                "closed-route register as architecturally incapable of emitting such a molecule (branch "
                "floor k = 3 + SEG2 + tail, no grid change reaches k < 4). The fix is a two-branch template "
                "at n = 18 with existing segments — a design change to a preregistered enumeration that "
                "'has never been put to trimcrae'."),
            "a_pass_licenses": ["a multiplicative selectivity argument built from two independently-measured terms"],
            "a_pass_does_not_license": [
                "either term individually being any stronger than its own row here",
                "any claim before the template decision is taken — enumerating over the current grid searches "
                "a space that structurally cannot contain the answer",
            ],
            "grade": "B-",
            "why_this_grade": (
                "Highest compounding upside of anything buildable, zero new instrument risk, and blocked "
                "only by a $0 decision that the roadmap already lists as row 8 and records as never having "
                "been asked. It is not higher because the two terms it multiplies are themselves A- and "
                "C+/D, and multiplying an unvalidated term by a validated one does not validate it."),
        },
        {
            "id": "S14", "known_answer_short": '⛔ **NO** — Gate 1 failed as registered; seeds do not share an F(Rg)', "positive_control_short": '⛔ no — a reproducibility failure is not repaired by a control', "cheapest_test_short": '$0 — taken (M5), and it refutes the categorical form', "name": "★ Conformational-selection selectivity — differential cryptic-pocket opening",
            "status": "CATEGORICAL FORM REFUTED HERE; quantitative form is requirement R6", "novelty": "NEW test of an old assumption",
            "physical_basis": "a binder requiring the open state is selective if the paralogues open less readily",
            "instrument": "V13 (metadynamics F(Rg)) — its only demonstrated reading is in the closed-route register",
            "known_answer_test_in_the_needed_regime": "NO. Gate 1 FAILED as registered; three seeds do not reconstruct a common F(Rg).",
            "positive_control_possible": (
                "⛔ Not with this instrument. The cross-replica failure is a reproducibility failure, which "
                "no positive control repairs."),
            "cheapest_decisive_test": "$0 — taken here (M5)",
            "measured_here": m5["★_finding"],
            "a_pass_licenses": ["nothing in the categorical form"],
            "a_pass_does_not_license": [
                "⛔ 'only NR4A3 has the cryptic pocket'. Both paralogues reach NR4A3's druggable CV inside "
                "their own matched metadynamics, and fpocket rates NR4A1's opened frame MORE druggable "
                "(0.981) than NR4A3's (0.931).",
            ],
            "grade": "D",
            "why_this_grade": (
                "Filed so it is not re-proposed. The quantitative version is not dead — it is R6, a "
                "requirement with NO instrument, held on an explicit nod, and the one term validation "
                "requirement 2 says can REVERSE the margin. Reporting everything conditional on the open "
                "state remains $0 and fully defensible."),
        },
        {
            "id": "S15", "known_answer_short": 'n/a in the free-energy sense — it is a geometric constraint', "positive_control_short": "**yes — the register's cleanest: NR4A1 C551 / celastrol is an anti-handle**", "cheapest_test_short": '$0 — the closure data is committed; only the constraint is missing', "name": "★ Reciprocal anti-handle avoidance — design AWAY from the paralogues' own unique residues",
            "status": "LIVE — free, and it is already the binding constraint", "novelty": "NEW as an explicit axis",
            "physical_basis": (
                "The mirror of S1. NR4A1 carries 14 reciprocal-unique reactive residues and NR4A2 carries 5 "
                "— sites where a paralogue is chemically addressable and NR4A3 is not. These are not a "
                "curiosity: they are what actually CLOSES the chemoselectivity window, in 30 of 30 graded "
                "cells, and NR4A2 C534 (a position NR4A3 lacks) closes 23 of 30 corridor cells."),
            "instrument": "the committed reciprocal-uniqueness map + the reach kernel — both already exist",
            "known_answer_test_in_the_needed_regime": (
                "NO in the free-energy sense and it does not need one: avoiding a residue is a geometric "
                "constraint of exactly the kind S1 already relies on."),
            "positive_control_possible": (
                "YES, and it is the best-supported one in the entire register: NR4A1 Cys551 / celastrol is "
                "the family's one literature-anchored covalent site, and it is an ANTI-handle. A construct "
                "reaching C551 is a demonstrated NR4A1 liability — the confound that ruins NR-V04 as a "
                "positive control for detecting selectivity is a clean positive control for AVOIDING one."),
            "cheapest_decisive_test": (
                "$0 — the closure data is committed. What is missing is that the anti-handle set is not "
                "carried as a design CONSTRAINT anywhere: the enumeration optimises reach TO C397 and only "
                "reports the paralogue closure afterwards."),
            "a_pass_licenses": [
                "a hard design filter — reject any construct whose reach envelope admits NR4A1 C505/C551 or "
                "NR4A2 C534 — which is free and strictly tightens every other row here",
            ],
            "a_pass_does_not_license": [
                "an increase in NR4A3 engagement. It removes liabilities; it adds no signal.",
                "a proteome-wide claim — an electrophile does not know it is meant to be selective",
            ],
            "grade": "B",
            "why_this_grade": (
                "Free, already measurable, uses only instruments that have not failed, and it has the "
                "register's cleanest positive control. It is capped at B because it is a filter rather than "
                "a mechanism: it can only ever narrow the design space, never widen the margin."),
        },
        {
            "id": "S16", "known_answer_short": 'n/a — an equilibrium identity, not an estimator', "positive_control_short": 'yes trivially; nothing here needs one', "cheapest_test_short": '$0 — taken (M7)', "name": "★ Pharmacological window as an amplifier — dose, Dmax and the hook",
            "status": "NOT A SELECTIVITY MECHANISM — a conversion between one and an observable", "novelty": "NEW",
            "physical_basis": (
                "Degradation is not linear in binding. A given margin becomes an observable window through "
                "the three-body equilibrium, so the question 'how much margin do we need?' has a computable "
                "answer that does not depend on measuring the margin."),
            "instrument": "the committed three-body cooperative-equilibrium model",
            "known_answer_test_in_the_needed_regime": (
                "N/A — it is an equilibrium identity, not an estimator. Its INPUTS (Kd, alpha) are the "
                "unvalidated quantities, and the model's own header says it is illustrative."),
            "positive_control_possible": "YES trivially (published DC50/Dmax series), but nothing here needs one.",
            "cheapest_decisive_test": "$0 — taken here (M7)",
            "measured_here": m7["★_finding"],
            "a_pass_licenses": [
                "an honest statement of the REQUIRED margin per mechanism, which is what the register above "
                "grades against",
                "a reporting frame: report the margin needed for a window, not a raw ddG",
            ],
            "a_pass_does_not_license": [
                "any DC50, Dmax or dose for any molecule. The parameters are illustrative and the artifact "
                "says so.",
                "the idea that a window can substitute for a margin — it converts one, it does not create one",
            ],
            "grade": "C+",
            "why_this_grade": (
                "Included because it changes how every other row is graded and it costs nothing. It is not "
                "higher because it produces no selectivity of its own."),
        },
        {
            "id": "S17", "known_answer_short": 'n/a — a data lookup, not an estimator', "positive_control_short": 'yes — tissue-restricted E3 degraders are an established concept', "cheapest_test_short": '$0 — E3 half already answered; paralogue half is a 1-line CI change', "name": "★ Expression-context selectivity — a tissue-restricted E3, or a paralogue that is not there",
            "status": "REFUTED for the E3 half on committed data; UNTESTED for the paralogue half", "novelty": "NEW",
            "physical_basis": (
                "A degrader is only active where its full CRL arm is expressed, and a paralogue that is not "
                "expressed in the tissue at risk does not need to be spared. Neither requires any molecular "
                "discrimination at all."),
            "instrument": "committed expression artifacts (Human Protein Atlas arms; DepMap for the target)",
            "known_answer_test_in_the_needed_regime": "N/A — it is a data lookup, not an estimator.",
            "positive_control_possible": "YES — tissue-restricted E3 degraders are an established concept with published examples.",
            "cheapest_decisive_test": (
                "$0. The E3 half is already answered: all 10 recruiter arms in the widened panel are "
                "BROADLY EXPRESSED and complete, so no arm in the panel offers tissue restriction. The "
                "paralogue half is NOT answered — the committed DepMap artifact carries NR4A3 only "
                "(sarcoma mean log2TPM 1.03, expressed in 0.09 of lines) and holds no NR4A1 or NR4A2 row. "
                "Widening the existing gene list is a one-line change to an existing $0 CI job."),
            "a_pass_licenses": [
                "a claim-scope statement: WHICH paralogue actually needs sparing, and where",
                "a re-weighting of every other row — the roadmap names NR4A2 as carrying the dopaminergic-loss "
                "liability, and it is also the paralogue Route A is 20% thinner against",
            ],
            "a_pass_does_not_license": [
                "⛔ any molecular selectivity. Expression context changes what a margin BUYS, never whether "
                "the molecule discriminates.",
                "safety or a therapeutic window — neither is computed anywhere in this program",
            ],
            "grade": "C",
            "why_this_grade": (
                "The E3 half is closed on committed data and should stop being proposed. The paralogue half "
                "is a $0 CI job that nobody has run and that would sharpen the scope of every selectivity "
                "sentence in the paper — which is worth more than it sounds, because the program's "
                "selectivity claim is currently bounded to two paralogues by an unrun cross-binding check."),
        },
    ]


# =============================================================================================================
# markdown
# =============================================================================================================
_LETTER = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
_MODIFIER = {"+": 0, "": 1, "-": 2}


def _grade_sort(m):
    """Best first: A- ... B+ B B- ... — so '+' must sort BEFORE '' and '-', which plain string order does not."""
    g = m["grade"]
    return (_LETTER[g[0]], _MODIFIER.get(g[1:], 1), m["id"])


def to_markdown(d):
    L = []
    A = L.append
    A("# Every mechanism by which paralogue selectivity could be argued for an NR4A3 degrader")
    A("")
    A("**Breadth first, then honest grading.** 17 mechanisms, 7 measurements taken to settle them, "
      "**$0 — no GPU, no rental, no priced rung dispatched.** Nothing here is a claim about binding, "
      "reactivity, degradation, efficacy, safety or clinical readiness; several rows exist precisely to "
      "record that a mechanism **cannot** be claimed.")
    A("")
    A("Regenerate with `python3 research/modalities/selectivity_mechanism_options.py`. Every figure taken "
      "from an existing artifact is a **citation** carrying the artifact that owns it; the seven "
      "measurements below are new and this file is their one home. This document is about **which "
      "mechanism**; "
      "[`selectivity-resolution-options.md`](./selectivity-resolution-options.md) is about **how much "
      "resolution** — they are orthogonal and neither restates the other.")
    A("")
    A("---")
    A("")
    A("## If you read only this")
    A("")
    for i, s in enumerate(d["headline"], 1):
        A(f"{i}. {s}")
    A("")
    A("---")
    A("")
    A("## The register")
    A("")
    A("Grades: " + " · ".join(f"**{k}** {v}" for k, v in GRADE_KEY.items()))
    A("")
    A("| grade | id | mechanism | new? | instrument passed a known-answer test **in the needed regime**? | "
      "could a valid positive control exist here? | cheapest decisive test |")
    A("|---|---|---|---|---|---|---|")
    for m in sorted(d["mechanisms"], key=_grade_sort):
        new = "★ **NEW**" if m["novelty"].startswith("NEW") else "—"
        A(f"| **{m['grade']}** | `{m['id']}` | {m['name']} | {new} | {m['known_answer_short']} | "
          f"{m['positive_control_short']} | {m['cheapest_test_short']} |")
    A("")
    A("---")
    A("")
    A("## The seven measurements taken here")
    A("")
    for key in ("M1", "M2", "M3", "M4", "M5", "M6", "M7"):
        m = d["measurements"][key]
        A(f"### {key} — {m['_question']}")
        A("")
        A(m["★_finding"])
        A("")
        for k in ("⚠_correction_to_a_quoted_triple", "✓_what_survives",
                  "⚠_which_registry_the_headline_run_used", "⛔_the_scores_are_NOT_evidence"):
            if k in m:
                A(f"> {k.replace('_', ' ')}: {m[k]}")
                A("")
        if "⛔_limits" in m:
            A("Limits:")
            for x in m["⛔_limits"]:
                A(f"- {x}")
            A("")
    A("---")
    A("")
    A("## Every mechanism in full")
    A("")
    for m in sorted(d["mechanisms"], key=_grade_sort):
        A(f"### `{m['id']}` {m['name']} — grade **{m['grade']}**")
        A("")
        A(f"**Status:** {m['status']}  ·  **{m['novelty']}**")
        A("")
        A(f"- **Physical basis.** {m['physical_basis']}")
        A(f"- **Instrument.** {m['instrument']}")
        A(f"- **Known-answer test in the needed regime?** {m['known_answer_test_in_the_needed_regime']}")
        A(f"- **Could a valid positive control exist here?** {m['positive_control_possible']}")
        A(f"- **Cheapest decisive test.** {m['cheapest_decisive_test']}")
        if "measured_here" in m:
            A(f"- **Measured here.** {m['measured_here']}")
        A("- **A pass would license:**")
        for x in m["a_pass_licenses"]:
            A(f"  - {x}")
        A("- **⛔ A pass would NOT license:**")
        for x in m["a_pass_does_not_license"]:
            A(f"  - {x}")
        A(f"- **Why this grade.** {m['why_this_grade']}")
        A("")
    A("---")
    A("")
    A("## What this changes about the plan")
    A("")
    for x in d["consequences"]:
        A(f"- {x}")
    A("")
    A("---")
    A("")
    A("## ⛔ Scope of this document")
    A("")
    for x in d["_scope"]:
        A(f"- {x}")
    A("")
    A(f"*Generated {d['_generated']['et']} by `selectivity_mechanism_options.py`.*")
    return "\n".join(L) + "\n"


# =============================================================================================================
# build
# =============================================================================================================
def build():
    ref, raw, fit = _superposed_models()
    M = {
        "M1": m1_lysine_coverage(),
        "M2": m2_residue_class_sweep(),
        "M3": m3_steric_exclusion(ref, fit),
        "M4": m4_paralogue_docking_control(ref, raw, fit),
        "M5": m5_pocket_opening(),
        "M6": m6_e3_arm_stability(),
        "M7": m7_degradation_window(),
    }
    mechs = mechanisms(M)
    now = _dt.datetime.now(_dt.timezone.utc)
    et = now - _dt.timedelta(hours=4)

    by_grade = {}
    for m in mechs:
        by_grade.setdefault(m["grade"][0], []).append(m["id"])

    headline = [
        f"**The shortlist was three; the enumeration is {len(mechs)}.** "
        f"{sum(1 for m in mechs if m['novelty'].startswith('NEW'))} mechanisms in this register had no row, "
        "node or mention anywhere in the program before this file — and one of them (`S3`) grades **above "
        "every non-incumbent option the program already had**, while a second (`S15`) ties the best of them.",
        "**★ The best genuinely-new option is STERIC EXCLUSION (`S3`, B+)** — three Pocket-5 positions where "
        f"both paralogues carry a strictly bulkier side chain. Measured here with its own null: "
        f"{M['M3']['by_position_class']['unique_and_both_bulkier']['rate']} paralogue-only clash against a "
        f"{M['M3']['by_position_class']['conserved_or_shared']['rate']} null at conserved/shared positions "
        f"({M['M3']['enrichment_signal_over_null']}×). It scores a structure rather than generating one, its "
        "claim is a shape constraint rather than a ~1 kcal/mol ΔΔG, and it is the only new mechanism for "
        "which an unconfounded positive control is straightforwardly constructible.",
        "**★ The categorical axis had never been swept beyond cysteine and lysine — and the sweep cuts both "
        "ways.** Across 11 reactive classes NR4A3 carries "
        f"{M['M2']['n_unique_alignment_robust_in_LBD_all_classes']} paralogue-unique, alignment-robust LBD "
        "positions (`S11`). ⛔ Under the V17 exposure cutoff **no new handle clears at all** — the credible "
        "set collapses to the cysteines and lysines already committed. ★ Under the threshold-free rank the "
        "roadmap says must *replace* that cutoff, **Y419** (RSA 0.221, SuFEx tyrosine, one residue from "
        "C420) sits above NR4A1 Cys551 (0.165), the family's one literature-anchored covalent site. Both "
        "readings are reported; neither is chosen here.",
        "**⛔ Two mechanisms are refuted here on committed data.** The paralogues are **not** lysine-poor — "
        "matched over 75 conformers per species the transfer zone reaches a lysine 0.4396 / 0.4279 / 0.3692 "
        "of the time, and the NR4A3−NR4A1 gap is under one replicate-SD (`S7`). And the cryptic pocket is "
        "**not** NR4A3-specific — both paralogues reach its druggable CV under matched metadynamics and "
        "fpocket rates NR4A1's opened frame *more* druggable (`S14`).",
        "**⛔ E3 choice is not measurable at current staging precision (`S8`, D).** Changing only how the E3 "
        "arm is assembled swings the maximum term-(b) enrichment 16.60 → 6.07 on VHL and halves CRBN's "
        "any-lysine null. The program's one E3-preference claim was already retracted for this reason.",
        "**The three cheapest high-value moves are all $0 and none needs authorization:** rung `5b-T` "
        "(`S5`, already roadmap row 1), the anti-handle design filter (`S15`), and asking for the two-branch "
        "template decision that unblocks the only compounding mechanism in the register (`S13`, roadmap "
        "row 8, *never asked*).",
        "**One quoted figure needs its ensemble labels.** The triple `NR4A3 0.438 / NR4A1 0.387 / NR4A2 "
        "0.363` mixes a 75-conformer pooled median with two single static frames. The like-for-like values "
        "are given in M1. ⚠ The error is **conservative** for the conclusion drawn from it — nothing "
        "downstream needs revising.",
    ]

    consequences = [
        "**Nothing here amends a preregistration, a gate or a plan.** It is an options register; trimcrae "
        "chooses. The roadmap remains the single steering document and no row below is scheduled by this file.",
        "`S3` (steric exclusion) and `S11` (non-cysteine categorical handles) are **new candidate rows for "
        "the roadmap's ordered list**, both at $0, both needing a rung/gate/price they do not have.",
        "`S15` (anti-handle avoidance) is **free and strictly tightens every other row** — the enumeration "
        "currently optimises reach TO C397 and only reports paralogue closure afterwards, rather than "
        "carrying the anti-handle set as a constraint.",
        "`S8` (E3 choice) and `S14` (conformational selection) should be recorded as **closed in their "
        "categorical form**, so they are not re-proposed. Neither belongs in the DEAD register: `S14`'s "
        "quantitative form is requirement `R6`, and `S8` needs a staging-precision argument, not a retry.",
        "`S12` (fusion-junction) is the register's **highest ceiling and lowest readiness**, and it maps "
        "exactly onto the roadmap's `R13` hole — which has no rung, gate or price anywhere in the program. "
        "Its $0 form (a sequence-level junction uniqueness and lysine inventory) needs no structure.",
        "**The grading rule applied throughout:** leverage never raises a grade. `S10` (cooperativity) has "
        "the highest leverage of any mechanism measured here — 7.9× DC50 separation at zero binary margin — "
        "and is graded **D**, because the control for its instrument was available, was run, and refuted it.",
    ]

    doc = {
        "_title": ("Every mechanism by which paralogue selectivity could be argued for an NR4A3 degrader — "
                   "enumerated, measured where committed artifacts can settle it, and graded"),
        "_status": ("OPTIONS REGISTER. $0 — CPU/stdlib analysis of committed artifacts only. No GPU, no "
                    "rental, no priced rung dispatched. Nothing here is launched, decided, or preregistered, "
                    "and no existing gate or criterion is amended or re-scored."),
        "_scope": [
            "Nothing here is a claim about binding, affinity, reactivity, degradation, efficacy, safety, a "
            "therapeutic window or clinical readiness. None of those is computed anywhere in this file.",
            "No claim of proteome-wide selectivity is made or implied. The comparison set throughout is "
            "NR4A1 and NR4A2, and the program's own scope is separately bounded by an unrun AR/MR "
            "cross-binding check.",
            "Grades rank mechanisms against each other for PLANNING. A grade is not evidence, and an A- row "
            "is still an unvalidated prediction under the roadmap's claim-ceiling rule.",
            "Every measurement is conditional on the artifacts it reads, including the docked poses (whose "
            "known-answer test returned INCONCLUSIVE on site selection) and the matched opened models.",
        ],
        "_one_fact_one_place": (
            "Figures quoted from existing artifacts are CITATIONS naming the owner. The seven measurements "
            "in `measurements` are new facts and this file is their one home. Regenerate rather than edit."),
        "_generated": {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "et": et.strftime("%Y-%m-%d ") + et.strftime("%I:%M %p ET").lstrip("0"),
                       "generator": "research/modalities/selectivity_mechanism_options.py"},
        "_grade_key": GRADE_KEY,
        "_reads": [
            "research/modalities/nr4a-paralogue-dynamics.json",
            "research/modalities/nr4a3-orientation-basins.json",
            "research/modalities/nr4a3-orientation-basins-matched-native.json",
            "research/modalities/nr4a3-orientation-basins-matched-composed.json",
            "research/modalities/nr4a-paralogue-unique-residues.json",
            "research/modalities/nr4a-sequences-cache.json",
            "research/modalities/nr4a3-linker-covalent-reach.json",
            "research/modalities/categorical-axis-audit.json",
            "research/modalities/nr4a-e3-expression.json",
            "research/modalities/depmap-target-expression.json",
            "results/nr4a3-matrix/{nr4a3,nr4a1,nr4a2}-opened.pdb, docked_*.sdf, nr4a3-matrix.json",
            "results/nr4a{1,2}-pocket-ensemble/release_summary.json",
        ],
        "headline": headline,
        "counts": {
            "n_mechanisms": len(mechs),
            "n_new": sum(1 for m in mechs if m["novelty"].startswith("NEW")),
            "by_grade_letter": {k: len(v) for k, v in sorted(by_grade.items())},
            "ids_by_grade_letter": {k: v for k, v in sorted(by_grade.items())},
        },
        "measurements": M,
        "mechanisms": mechs,
        "consequences": consequences,
    }
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()
    doc = build()
    with open(OUT_JSON, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"[selmech] wrote {OUT_JSON}")
    if not args.json_only:
        with open(OUT_MD, "w") as f:
            f.write(to_markdown(doc))
        print(f"[selmech] wrote {OUT_MD}")
    c = doc["counts"]
    print(f"[selmech] {c['n_mechanisms']} mechanisms, {c['n_new']} new; by grade {c['by_grade_letter']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
