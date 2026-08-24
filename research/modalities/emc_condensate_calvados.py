#!/usr/bin/env python3
"""
Does a residue-resolution phase-behaviour model separate EMC's 5' fusion partners?

THE QUESTION
------------
`research/manuscripts/fusion-direct/fusion-condensate-disruption-paper.md` argues that the aberrant
biomolecular-condensate behaviour of the EMC fusion is the one handle that is fusion-selective by
construction: wild-type NR4A3 has no EWS-type prion-like low-complexity (LC) domain, so the LC domain
is contributed entirely by the 5' partner. Its whole first-party evidence is amino-acid COMPOSITION
COUNTING (SYGQ fraction, aromatic fraction, FCR, Shannon entropy, SCD), which its own artifact
correctly calls a sequence-derived proxy and not a condensate measurement.

CALVADOS is the field-standard residue-resolution coarse-grained model for exactly that claim, and it
appears nowhere in this repository (`CALVADOS` and `Mpipi`: zero matches repo-wide, measured
2026-08-23 by `research/manuscripts/program/new-evidence-routes.md` s4). This module runs its
SINGLE-CHAIN arm - the arm whose founding result is that single-chain conformational properties inform
the model's phase behaviour - over the retained N-terminal segments of EMC's reported 5' partners.

WHY THE PARTNER CONTRAST AND NOT "THE EMC FUSION"
-------------------------------------------------
EWSR1 is the commonest partner, TAF15 the second, and TCF12 is NOT a FET protein at all - computed,
not asserted, in `emc-fet-construct-designs.json -> tcf12_negative_control`. A phase-behaviour model
therefore makes a DIFFERENTIAL prediction across the chimeras, which is a statement about the disease
rather than about our engine, and one a wet lab that is not ours could falsify.

WHAT IS AND IS NOT READ OUT
---------------------------
Read out: nu (Flory scaling exponent, `calvados.analysis.fit_scaling_exp`), Rg, Ree - single-chain
conformational observables. NOT read out, and not claimed anywhere: a saturation concentration, a
phase diagram, condensate formation, efficacy, selectivity in a patient, safety, a therapeutic window,
or clinical readiness. A single-chain conformational difference between two retained partner segments
is a single-chain conformational difference between two retained partner segments.

THE PRESPECIFICATION IS THE CONTRACT
------------------------------------
`research/modalities/emc-condensate-calvados-prespecification.md` is frozen BEFORE any simulation ran.
This module holds the executable half of it: the construct set, the protocol, the guards and the
scorer. `--selftest` asserts all of it OFFLINE, before one integration step is taken.

Modes
-----
  --selftest        offline guard suite (no network, no simulation)
  --manifest        emit the frozen construct manifest (sequences + sha256) to stdout or --out
  --plddt           fetch AlphaFold DB pLDDT and write the window eligibility table (network)
  --prepare ID K    write a CALVADOS run directory for construct ID, replicate K
  --analyse DIR     compute nu/Rg/Ree + provenance for one finished run directory
  --reduce          combine per-run JSON into emc-condensate-calvados.json and score it
"""

import argparse
import csv
import hashlib
import json
import os
import random
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-condensate-calvados.json")
PLDDT_OUT = os.path.join(HERE, "emc-condensate-window-eligibility.json")
MANIFEST_OUT = os.path.join(HERE, "emc-condensate-constructs.json")

SEQ_CACHE = os.path.join(HERE, "fet-sequences-cache.json")
CONSTRUCT_INPUTS = os.path.join(HERE, "emc-construct-inputs.json")
CONSTRUCT_DESIGNS = os.path.join(HERE, "emc-fet-construct-designs.json")
IDR_CENSUS = os.path.join(HERE, "emc-fet-idr-census.json")
STRUCTURE = os.path.join(HERE, "nr4a3-structure-assessment.json")

AFDB = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"
ACCESSIONS = {"EWSR1": "Q01844", "TAF15": "Q92804", "FUS": "P35637",
              "NR4A3": "Q92570", "TCF12": "Q99081"}

# ---------------------------------------------------------------------------------------------
# PROTOCOL - fixed here, before any run. Every number is either the package's own shipped
# single-IDR example or a value MEASURED to be free (see the prespecification s5).
# ---------------------------------------------------------------------------------------------
PROTOCOL = {
    "model": "CALVADOS 2",
    "residue_parameters": "the CALVADOS package default (calvados/data/residues.csv), which agrees "
                          "with the shipped residues_CALVADOS2.csv to 5e-13 in every lambda",
    "temperature_K": 293.15,
    "ionic_strength_M": 0.19,
    "pH": 7.5,
    "box_nm": 150.0,
    "timestep_fs": 10,
    "steps_per_frame": 7000,
    "n_frames": 1010,
    "steps": 1010 * 7000,
    "discard_frames": 10,
    "platform": "CPU",
    "charge_termini": "both",
    "_box_provenance": "the shipped example uses 50 nm for a 131-mer; 150 nm was MEASURED to cost "
                       "nothing (48.5 s vs 48.8 s for 20k steps of a 431-mer at 4 threads) and "
                       "removes any chance of a chain interacting with its own periodic image. "
                       "Identical for every construct, so box is not a between-construct variable.",
    "_sampling_provenance": "1010 frames x 7000 steps is the CALVADOS package's own shipped "
                            "single-IDR protocol (examples/single_IDR/prepare.py), unmodified.",
}

MIN_FRAMES_ANALYSED = 900          # of the 1000 kept after discarding the first 10
NU_PHYSICAL_RANGE = (0.30, 0.75)   # outside this the integration is broken, not the biology
ALPHA = 0.05
SEPARATION_SIGMAS = 3.0            # |dnu| must clear this many pooled replicate SDs
PLDDT_DISORDER_FRACTION = 0.75     # >= this fraction of window residues below pLDDT 50
PLDDT_DISORDER_CUTOFF = 50.0

# ---------------------------------------------------------------------------------------------
# CONSTRUCTS. Boundaries are READ from committed artifacts, never typed here - see `_boundaries`.
# ---------------------------------------------------------------------------------------------
SCRAMBLE_SEEDS = (20260824, 20260825, 20260826)
EDOPE_SEED = 20260827
EDOPE_FRACTION = 0.15


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _boundaries():
    """Every construct boundary, resolved from a committed artifact. Nothing here is a literal."""
    designs = _load(CONSTRUCT_DESIGNS)
    census = _load(IDR_CENSUS)
    struct = _load(STRUCTURE)

    # the retained 5' segment of each sourced EMC construct, e.g. "EWSR1(1-431)" -> 431
    retained = {}
    for c in designs["constructs"]:
        spec = c["domains_retained_and_lost"]["five_prime_FET_half"]["residues_retained"]
        gene, rng = spec.split("(", 1)
        retained[c["id"]] = (gene, int(rng.rstrip(")").split("-")[1]))

    regions = {g: {k: v for k, v in struct[g]["regions"].items()} for g in ("EWSR1", "NR4A3")}
    ewsr1_rrm_start = int(
        next(v for k, v in regions["EWSR1"].items() if "RNA-recognition" in k)["residues"].split("-")[0])
    nr4a3_af1_end = int(
        next(v for k, v in regions["NR4A3"].items() if k.startswith("AF1"))["residues"].split("-")[1])
    ewsr1_lc_end = int(
        next(v for k, v in regions["EWSR1"].items() if "SYGQ-rich" in k)["residues"].split("-")[1])

    return {
        "EWSR1_type2_retained": retained["EWSR1_NR4A3_type2"][1],      # 264
        "EWSR1_type1_retained": retained["EWSR1_NR4A3_type1"][1],      # 431
        "TAF15_retained": retained["TAF15_NR4A3"][1],                  # 161
        "EWSR1_RRM_start": ewsr1_rrm_start,                            # 361
        "EWSR1_LC_end": ewsr1_lc_end,                                  # 264
        "NR4A3_AF1_end": nr4a3_af1_end,                                # 260
        "FUS_rgg_free_ceiling": census["wild_type_annotation"]["FUS"]["rgg_free_ceiling"],  # 212
    }


def _sequences():
    """Partner sequences, all from committed caches. TCF12 needs no fetch - it is already here."""
    cache = _load(SEQ_CACHE)
    inputs = _load(CONSTRUCT_INPUTS)
    seqs = {k: cache[k] for k in ("EWSR1", "TAF15", "FUS", "NR4A3")}
    seqs["TCF12"] = inputs["genes"]["TCF12"]["protein"]          # Ensembl ENSP00000331057, 706 aa
    seqs["TCF12_uniprot"] = inputs["uniprot_sequences"]["TCF12"]  # Q99081 isoform, 682 aa
    return seqs


def scramble(seq, seed):
    """Composition-preserving shuffle. Deterministic in `seed`; asserted in the guard suite."""
    chars = list(seq)
    random.Random(seed).shuffle(chars)
    return "".join(chars)


def edope(seq, seed, fraction=EDOPE_FRACTION):
    """Substitute `fraction` of positions (never position 1) with Glu. Instrument control only."""
    chars = list(seq)
    rng = random.Random(seed)
    n = int(round(fraction * len(chars)))
    positions = rng.sample(range(1, len(chars)), n)
    for p in positions:
        chars[p] = "E"
    return "".join(chars)


def build_constructs():
    """The frozen construct set. Returns an ordered list of dicts."""
    b = _boundaries()
    s = _sequences()
    e_lc = b["EWSR1_LC_end"]                     # 264
    e_idr1 = b["EWSR1_RRM_start"] - 1            # 360 - the type-1 segment truncated at the RRM
    t_ret = b["TAF15_retained"]                  # 161
    n_af1 = b["NR4A3_AF1_end"]                   # 260
    f_ceil = b["FUS_rgg_free_ceiling"]           # 212

    def win(gene, end):
        return s[gene][:end]

    items = []

    def add(cid, seq, role, family, n_rep, window, prediction, falsifier, note=""):
        items.append({
            "id": cid, "role": role, "family": family, "n_replicates": n_rep,
            "window": window, "length": len(seq), "sequence": seq,
            "sha256": hashlib.sha256(seq.encode()).hexdigest(),
            "registered_prediction": prediction, "falsifier": falsifier, "note": note,
        })

    add("E264", win("EWSR1", e_lc), "TEST", "FET",
        5, f"EWSR1 1-{e_lc}",
        "more compact (lower nu) than the length-matched TCF12 window C264",
        "nu(E264) >= nu(C264), or the two not separated under D1",
        "double-anchored: this is BOTH the committed AlphaFold LC/disorder window and the retained "
        "5' segment of the reported EWSR1::NR4A3 type-2 junction")
    add("E360", win("EWSR1", e_idr1), "TEST", "FET",
        5, f"EWSR1 1-{e_idr1}",
        "more compact (lower nu) than the length-matched TCF12 window C360",
        "nu(E360) >= nu(C360), or the two not separated under D1",
        "the reported type-1 (commonest) junction retains EWSR1 1-431, which runs 71 residues into "
        "the committed folded RRM (361-442). CALVADOS 2 treats every residue as disordered, so the "
        "type-1 segment is truncated at the last residue before the RRM and the multi-domain reading "
        "is named in the prespecification and NOT run here")
    add("T161", win("TAF15", t_ret), "TEST", "FET",
        5, f"TAF15 1-{t_ret}",
        "more compact (lower nu) than the length-matched TCF12 window C161",
        "nu(T161) >= nu(C161), or the two not separated under D1",
        "the only reported TAF15::NR4A3 coding junction")
    add("C161", win("TCF12", t_ret), "TEST", "nonFET", 5, f"TCF12 1-{t_ret}",
        "less compact (higher nu) than T161", "not separated from T161 under D1",
        "length-matched non-FET comparator; isoform-independent (the two TCF12 isoforms in this "
        "repository are identical over 1-396)")
    add("C264", win("TCF12", e_lc), "TEST", "nonFET", 5, f"TCF12 1-{e_lc}",
        "less compact (higher nu) than E264", "not separated from E264 under D1",
        "length-matched non-FET comparator; isoform-independent")
    add("C360", win("TCF12", e_idr1), "TEST", "nonFET", 5, f"TCF12 1-{e_idr1}",
        "less compact (higher nu) than E360", "not separated from E360 under D1",
        "length-matched non-FET comparator; isoform-independent")
    add("N260", win("NR4A3", n_af1), "CONTROL", "wildtype", 5, f"NR4A3 1-{n_af1}",
        "less compact (higher nu) than E264 - it is disordered but not prion-like",
        "N260 not separated from E264 under D1, which would be negative N3",
        "wild-type NR4A3's own disordered AF1; the manuscript's internal negative control at the "
        "composition level, re-asked at the phase-behaviour level")
    add("F212", win("FUS", f_ceil), "CONTROL", "FET", 5, f"FUS 1-{f_ceil}",
        "in the same range as E264 and T161, not in the TCF12 range",
        "F212 lands in the TCF12 range rather than the FET range",
        "the third FET gene, at the RG-free ceiling read from emc-fet-idr-census.json; a FET anchor "
        "that is not an EMC construct")

    for i, seed in enumerate(SCRAMBLE_SEEDS, start=1):
        add(f"E264_scr{i}", scramble(win("EWSR1", e_lc), seed), "NULL", "scramble", 2,
            f"EWSR1 1-{e_lc} shuffled, seed {seed}",
            "nu differs from E264 by at least 3 pooled replicate SDs",
            "nu indistinguishable from E264, which is negative N1 for this parent",
            "composition is preserved EXACTLY; only the order changes")
    for i, seed in enumerate(SCRAMBLE_SEEDS, start=1):
        add(f"C264_scr{i}", scramble(win("TCF12", e_lc), seed), "NULL", "scramble", 2,
            f"TCF12 1-{e_lc} shuffled, seed {seed}",
            "nu differs from C264 by at least 3 pooled replicate SDs",
            "nu indistinguishable from C264, which is negative N1 for this parent",
            "composition is preserved EXACTLY; only the order changes")

    add("E264_E15", edope(win("EWSR1", e_lc), EDOPE_SEED), "INSTRUMENT", "instrument", 3,
        f"EWSR1 1-{e_lc} with {int(EDOPE_FRACTION*100)}% of positions substituted to Glu, "
        f"seed {EDOPE_SEED}",
        "STRICTLY more expanded (higher nu) than E264 - like charges repel under the model's "
        "Debye-Huckel term, so this is a property of the force field, not of the biology",
        "nu(E264_E15) not above nu(E264) by 3 pooled replicate SDs, which is INSTRUMENT_FAILED "
        "and withholds every nu in the run",
        "directional instrument control")
    return items


PRIMARY_FAMILY = [("E264", "C264"), ("E360", "C360"), ("T161", "C161")]
SECONDARY_PAIRS = [("E264", "T161"), ("E360", "T161"), ("E264", "E360"),
                   ("E264", "N260"), ("T161", "N260"), ("E264", "F212"), ("F212", "C264")]

# ---------------------------------------------------------------------------------------------
# SCORING - the rules, executable, so they cannot be reinterpreted after the numbers land.
# ---------------------------------------------------------------------------------------------


def _mean(xs):
    return sum(xs) / len(xs)


def _sd(xs):
    if len(xs) < 2:
        return None
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def pooled_sd(by_construct, ids):
    num = den = 0.0
    for cid in ids:
        xs = by_construct.get(cid) or []
        if len(xs) < 2:
            continue
        s = _sd(xs)
        num += (len(xs) - 1) * s * s
        den += (len(xs) - 1)
    if den == 0:
        return None
    return (num / den) ** 0.5


def _combinations(seq, k):
    n = len(seq)
    if k > n:
        return
    idx = list(range(k))
    yield tuple(seq[i] for i in idx)
    while True:
        for i in reversed(range(k)):
            if idx[i] != i + n - k:
                break
        else:
            return
        idx[i] += 1
        for j in range(i + 1, k):
            idx[j] = idx[j - 1] + 1
        yield tuple(seq[i] for i in idx)


def permutation_p(a, b):
    """Exact two-sided permutation p on |difference of means|, plus the design floor."""
    pooled = list(a) + list(b)
    obs = abs(_mean(a) - _mean(b))
    total = hits = 0
    total_sum = sum(pooled)
    na = len(a)
    for combo_idx in _combinations(list(range(len(pooled))), na):
        sa = sum(pooled[i] for i in combo_idx)
        ma = sa / na
        mb = (total_sum - sa) / (len(pooled) - na)
        total += 1
        if abs(ma - mb) >= obs - 1e-15:
            hits += 1
    return {"p": hits / total, "n_arrangements": total, "floor_p": 2.0 / total,
            "powered": (2.0 / total) <= ALPHA / 3.0}


def holm(pairs_with_p):
    """Holm-Bonferroni over the primary family. Returns {pair: reject_bool}."""
    ordered = sorted(pairs_with_p.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out, rejected_so_far = {}, True
    for i, (key, p) in enumerate(ordered):
        thresh = ALPHA / (m - i)
        rejected_so_far = rejected_so_far and (p <= thresh)
        out[key] = rejected_so_far
    return out


def separated(a_vals, b_vals, sigma):
    """Rule D1, exactly as prespecified: 3 pooled SDs AND disjoint replicate ranges."""
    if sigma is None or not a_vals or not b_vals:
        return None
    gap = abs(_mean(a_vals) - _mean(b_vals))
    disjoint = (max(a_vals) < min(b_vals)) or (max(b_vals) < min(a_vals))
    return bool(gap >= SEPARATION_SIGMAS * sigma and disjoint)


def completeness(runs):
    """Does the run set match the frozen manifest? An empty or partial set is NOT a result.

    ⛔ This exists because it was measured missing. Before it, `score([])` returned
    `NO_SEPARATION` — a verdict ABOUT THE DISEASE derived from zero simulations — and the guard
    that was supposed to catch that passed vacuously on an `or`. An absent reading is not a
    reading of absence, and a run set that does not match the manifest is absent, not negative.
    """
    want = {c["id"]: c["n_replicates"] for c in build_constructs()}
    have = {}
    for r in runs:
        if r.get("nu") is not None:
            have[r["construct"]] = have.get(r["construct"], 0) + 1
    missing = {cid: (n, have.get(cid, 0)) for cid, n in want.items() if have.get(cid, 0) != n}
    unknown = sorted(set(have) - set(want))
    return missing, unknown


def instrument_verdict(runs, by_construct, sigma):
    """Every condition that withholds a nu. Returns (ok, [reasons])."""
    bad = []
    missing, unknown = completeness(runs)
    for cid, (want, got) in sorted(missing.items()):
        bad.append(f"{cid}: {got} of {want} replicates carry a nu — the run set does not match "
                   f"the frozen manifest, so no verdict about any partner is emitted")
    for cid in unknown:
        bad.append(f"{cid}: not in the frozen construct manifest")
    for r in runs:
        if r.get("frames_analysed", 0) < MIN_FRAMES_ANALYSED:
            bad.append(f"{r.get('run_id')}: frames_analysed={r.get('frames_analysed')} "
                       f"< {MIN_FRAMES_ANALYSED}")
        if not r.get("wall_seconds") or r["wall_seconds"] < 60:
            bad.append(f"{r.get('run_id')}: wall_seconds={r.get('wall_seconds')} - a populated "
                       f"field is not a measured one")
        for field in ("calvados_version", "calvados_commit", "openmm_version", "platform",
                      "random_number_seed", "sequence_sha256"):
            if not r.get(field):
                bad.append(f"{r.get('run_id')}: missing provenance field {field}")
        nu = r.get("nu")
        if nu is None or not (NU_PHYSICAL_RANGE[0] <= nu <= NU_PHYSICAL_RANGE[1]):
            bad.append(f"{r.get('run_id')}: nu={nu} outside physical range {NU_PHYSICAL_RANGE}")
    for cid, vals in by_construct.items():
        seeds = [r["random_number_seed"] for r in runs
                 if r.get("construct") == cid and r.get("random_number_seed") is not None]
        if len(set(seeds)) != len(seeds):
            bad.append(f"{cid}: replicate seeds are not distinct - {seeds}")
    e, e15 = by_construct.get("E264"), by_construct.get("E264_E15")
    if e and e15 and sigma is not None:
        if not (_mean(e15) - _mean(e)) >= SEPARATION_SIGMAS * sigma:
            bad.append("E264_E15 did not expand relative to E264 by 3 pooled SDs - the "
                       "electrostatics direction control failed, so no nu in this run is quoted")
    return (len(bad) == 0), bad


def score(runs):
    """The whole prespecified decision, computed from a list of per-run analysis dicts."""
    by_construct = {}
    for r in runs:
        if r.get("nu") is not None:
            by_construct.setdefault(r["construct"], []).append(r["nu"])

    primary_ids = [c["id"] for c in build_constructs() if c["role"] in ("TEST", "CONTROL")]
    sigma = pooled_sd(by_construct, primary_ids)
    ok, reasons = instrument_verdict(runs, by_construct, sigma)

    result = {
        "pooled_replicate_sd_nu": sigma,
        "separation_threshold_nu": (SEPARATION_SIGMAS * sigma) if sigma is not None else None,
        "construct_means": {k: {"nu_mean": _mean(v), "nu_sd": _sd(v), "n": len(v),
                                "nu_min": min(v), "nu_max": max(v)}
                            for k, v in sorted(by_construct.items())},
    }
    if not ok:
        missing, unknown = completeness(runs)
        result["verdict"] = "INCOMPLETE" if (missing or unknown) else "INSTRUMENT_FAILED"
        result["reasons"] = reasons
        result["_what_this_is_not"] = ("Neither INCOMPLETE nor INSTRUMENT_FAILED is a negative "
                                       "result. No nu is quoted and no claim about any partner "
                                       "is made.")
        return result

    pair_rows, ps = {}, {}
    for a, b in PRIMARY_FAMILY + SECONDARY_PAIRS:
        va, vb = by_construct.get(a), by_construct.get(b)
        if not va or not vb:
            continue
        perm = permutation_p(va, vb)
        row = {"delta_nu_mean": _mean(va) - _mean(vb),
               "separated_D1": separated(va, vb, sigma),
               "permutation": perm,
               "family": "primary" if (a, b) in PRIMARY_FAMILY else "secondary"}
        pair_rows[f"{a}_vs_{b}"] = row
        if (a, b) in PRIMARY_FAMILY:
            ps[f"{a}_vs_{b}"] = perm["p"]
    if ps:
        for key, rej in holm(ps).items():
            pair_rows[key]["holm_reject_at_0.05"] = rej
    result["pairs"] = pair_rows

    prim = [pair_rows[f"{a}_vs_{b}"]["separated_D1"] for a, b in PRIMARY_FAMILY
            if f"{a}_vs_{b}" in pair_rows]
    fet_vs_fet = [pair_rows[k]["separated_D1"] for k in ("E264_vs_T161", "E360_vs_T161",
                                                         "E264_vs_E360") if k in pair_rows]

    # N1 - composition-only
    comp = {}
    for parent, kids in (("E264", [f"E264_scr{i}" for i in (1, 2, 3)]),
                         ("C264", [f"C264_scr{i}" for i in (1, 2, 3)])):
        pv = by_construct.get(parent)
        kv = [_mean(by_construct[k]) for k in kids if k in by_construct]
        if pv and kv:
            comp[parent] = {"delta_nu_vs_scramble_mean": _mean(pv) - _mean(kv),
                            "exceeds_threshold": abs(_mean(pv) - _mean(kv)) >= SEPARATION_SIGMAS * sigma,
                            "scramble_means": kv}
    result["composition_only_test"] = comp
    composition_only = bool(comp) and not any(v["exceeds_threshold"] for v in comp.values())

    negatives = []
    if prim and not any(prim):
        negatives.append("NEGATIVE_NO_STRATIFICATION")
        negatives.append("NEGATIVE_FET_NOT_SPECIAL")
    if "E264_vs_N260" in pair_rows and pair_rows["E264_vs_N260"]["separated_D1"] is False:
        negatives.append("NEGATIVE_WILDTYPE_NOT_SEPARATED")
    if composition_only:
        negatives.append("NEGATIVE_COMPOSITION_ONLY")

    if any(prim) or any(fet_vs_fet):
        verdict = "SEPARATION_OBSERVED"
    else:
        verdict = "NO_SEPARATION"
    result["verdict"] = verdict
    result["negatives"] = negatives
    result["claim_ceiling"] = (
        "nu is a single-chain conformational observable. A difference in nu between two retained "
        "partner segments is a difference in nu between two retained partner segments. No "
        "saturation concentration, phase diagram, condensate, efficacy, patient-level selectivity, "
        "safety, therapeutic window or clinical readiness is measured or claimed.")
    return result

# ---------------------------------------------------------------------------------------------
# RUN PREPARATION AND ANALYSIS (these import calvados; the guards above never do)
# ---------------------------------------------------------------------------------------------


def replicate_seed(construct_id, k):
    """Deterministic, distinct per (construct, replicate). Distinctness is asserted by a guard."""
    h = hashlib.sha256(f"{construct_id}/{k}".encode()).hexdigest()
    return int(h[:8], 16) % (2 ** 31 - 1) + 1


def prepare(construct_id, replicate, outdir):
    from calvados.cfg import Config, Components
    import calvados
    con = next(c for c in build_constructs() if c["id"] == construct_id)
    if replicate < 1 or replicate > con["n_replicates"]:
        raise SystemExit(f"replicate {replicate} outside 1..{con['n_replicates']} for {construct_id}")
    name = f"{construct_id}_r{replicate}"
    path = os.path.join(os.path.abspath(outdir), name)
    os.makedirs(path, exist_ok=True)
    fasta = os.path.join(path, "seq.fasta")
    with open(fasta, "w") as fh:
        fh.write(f">{name}\n{con['sequence']}\n")
    residues = os.path.join(os.path.dirname(os.path.abspath(calvados.__file__)), "data", "residues.csv")
    seed = replicate_seed(construct_id, replicate)
    cfg = Config(sysname=name, box=[PROTOCOL["box_nm"]] * 3, temp=PROTOCOL["temperature_K"],
                 ionic=PROTOCOL["ionic_strength_M"], pH=PROTOCOL["pH"], topol="center",
                 wfreq=PROTOCOL["steps_per_frame"], steps=PROTOCOL["steps"], runtime=0,
                 platform=PROTOCOL["platform"], restart="checkpoint", frestart="restart.chk",
                 verbose=False, random_number_seed=seed,
                 threads=int(os.environ.get("CALVADOS_THREADS", "4")))
    cfg.write(path, name="config.yaml", analyses="")
    comp = Components(molecule_type="protein", nmol=1, restraint=False,
                      charge_termini=PROTOCOL["charge_termini"], fresidues=residues, ffasta=fasta)
    comp.add(name=name)
    comp.write(path, name="components.yaml")
    with open(os.path.join(path, "prepared.json"), "w") as fh:
        json.dump({"construct": construct_id, "replicate": replicate, "run_id": name,
                   "random_number_seed": seed, "sequence_sha256": con["sha256"],
                   "length": con["length"], "residues_sha256": _sha256(residues),
                   "protocol": PROTOCOL}, fh, indent=1)
    print(path)
    return path


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _versions():
    import importlib.metadata as md
    out = {}
    for pkg in ("calvados", "openmm", "MDAnalysis", "mdtraj", "numpy", "pandas"):
        try:
            out[pkg] = md.version(pkg)
        except Exception:
            out[pkg] = None
    out["calvados_commit"] = os.environ.get("CALVADOS_COMMIT") or None
    return out


def analyse(rundir):
    """nu / Rg / Ree for one finished run, with the provenance a default value cannot fabricate."""
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    import MDAnalysis as mda
    from calvados.analysis import calc_ete, fit_scaling_exp
    import pandas as pd

    rundir = os.path.abspath(rundir)
    prepared = _load(os.path.join(rundir, "prepared.json"))
    name = prepared["run_id"]
    u = mda.Universe(os.path.join(rundir, "top.pdb"), os.path.join(rundir, f"{name}.dcd"),
                     in_memory=True)
    ag = u.select_atoms("all")
    n_total = len(u.trajectory)
    start = PROTOCOL["discard_frames"]
    frames = max(0, n_total - start)

    rec = dict(prepared)
    rec["frames_written"] = n_total
    rec["frames_analysed"] = frames
    rec.update(_versions())
    rec["calvados_version"] = rec.pop("calvados", None)
    rec["openmm_version"] = rec.pop("openmm", None)
    rec["trajectory_sha256"] = _sha256(os.path.join(rundir, f"{name}.dcd"))
    log = os.path.join(rundir, "wall_seconds.txt")
    rec["wall_seconds"] = float(open(log).read().strip()) if os.path.exists(log) else None

    if frames < MIN_FRAMES_ANALYSED:
        rec["nu"] = None
        rec["withheld_reason"] = (f"frames_analysed {frames} < {MIN_FRAMES_ANALYSED}; an absent "
                                  f"reading is not a reading of absence")
        return rec

    residues = pd.read_csv(prepared_residues_path()).set_index("three")
    masses = np.array(residues.loc[list(ag.resnames), "MW"].values, dtype=float)
    masses[0] += 2.0
    masses[-1] += 16.0
    rgs = []
    for _ in u.trajectory[start:]:
        com = ag.center(weights=masses)
        pos = (ag.positions - com) / 10.0
        rgs.append(float(np.sqrt(np.einsum("i,i->", masses,
                                           np.einsum("ij,ij->i", pos, pos)) / masses.sum())))
    rees, ree_mean, ree_sem = calc_ete(u, ag, start=start)
    _, _, _, nu, nu_err = fit_scaling_exp(u, ag, start=start)
    half = start + frames // 2
    _, _, _, nu_second_half, _ = fit_scaling_exp(u, ag, start=half)

    rec.update({
        "nu": float(nu), "nu_fit_error": float(nu_err),
        "nu_second_half": float(nu_second_half),
        "nu_half_vs_full_delta": float(abs(nu - nu_second_half)),
        "rg_mean_nm": float(np.mean(rgs)), "rg_sd_nm": float(np.std(rgs, ddof=1)),
        "ree_mean_nm": float(ree_mean), "ree_sem_nm": float(ree_sem),
        "rg_over_sqrt_n": float(np.mean(rgs) / (prepared["length"] ** 0.5)),
    })
    return rec


def prepared_residues_path():
    import calvados
    return os.path.join(os.path.dirname(os.path.abspath(calvados.__file__)), "data", "residues.csv")

# ---------------------------------------------------------------------------------------------
# pLDDT WINDOW ELIGIBILITY (network; $0; no simulation)
# ---------------------------------------------------------------------------------------------


def fetch_plddt():
    out = {"_what": "AlphaFold DB per-residue pLDDT over every candidate window. Entry criterion "
                    f"for the CALVADOS 2 single-chain arm, fixed before the fetch: at least "
                    f"{PLDDT_DISORDER_FRACTION:.0%} of window residues below pLDDT "
                    f"{PLDDT_DISORDER_CUTOFF:.0f}.",
           "_cutoff": PLDDT_DISORDER_CUTOFF, "_fraction_required": PLDDT_DISORDER_FRACTION,
           "_source": AFDB, "windows": {}}
    per_gene = {}
    for gene, acc in ACCESSIONS.items():
        req = urllib.request.Request(AFDB.format(acc=acc), headers={"User-Agent": "emc-condensate"})
        with urllib.request.urlopen(req, timeout=120) as fh:
            pdb = fh.read().decode()
        plddt = {}
        for line in pdb.splitlines():
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                plddt[int(line[22:26])] = float(line[60:66])
        per_gene[gene] = plddt
        out.setdefault("_lengths", {})[gene] = len(plddt)
    for con in build_constructs():
        if con["role"] not in ("TEST", "CONTROL"):
            continue
        gene = con["window"].split()[0]
        end = con["length"]
        vals = [per_gene[gene][i] for i in range(1, end + 1) if i in per_gene[gene]]
        if not vals:
            out["windows"][con["id"]] = {"read": False,
                                         "_meaning": "pLDDT could not be READ for this window; "
                                                     "that is not a reading of order"}
            continue
        frac = sum(1 for v in vals if v < PLDDT_DISORDER_CUTOFF) / len(vals)
        out["windows"][con["id"]] = {
            "read": True, "gene": gene, "window": con["window"], "n_residues_read": len(vals),
            "mean_plddt": round(sum(vals) / len(vals), 2),
            "frac_below_50": round(frac, 4),
            "eligible_for_calvados2_single_chain": bool(frac >= PLDDT_DISORDER_FRACTION),
        }
    out["all_primary_windows_eligible"] = all(
        w.get("eligible_for_calvados2_single_chain") for w in out["windows"].values())
    return out

# ---------------------------------------------------------------------------------------------
# GUARDS - all offline, all asserted before any integration step
# ---------------------------------------------------------------------------------------------


def selftest():
    checks, failures = [], []

    def ck(group, name, cond, detail=""):
        checks.append((group, name, bool(cond), detail))
        if not cond:
            failures.append(f"[{group}] {name} {detail}")

    cons = {c["id"]: c for c in build_constructs()}
    seqs = _sequences()
    b = _boundaries()

    # G1 - every boundary is READ from a committed artifact and equals what that artifact says
    ck("G1", "EWSR1 type-2 retained segment is 264", b["EWSR1_type2_retained"] == 264)
    ck("G1", "EWSR1 type-1 retained segment is 431", b["EWSR1_type1_retained"] == 431)
    ck("G1", "TAF15 retained segment is 161", b["TAF15_retained"] == 161)
    ck("G1", "EWSR1 folded RRM starts at 361", b["EWSR1_RRM_start"] == 361)
    ck("G1", "NR4A3 AF1 ends at 260", b["NR4A3_AF1_end"] == 260)
    ck("G1", "FUS RG-free ceiling is 212", b["FUS_rgg_free_ceiling"] == 212)

    # G2 - the type-1 window is truncated at the RRM, and the reason is real
    ck("G2", "type-1 retained segment really does overlap the folded RRM",
       b["EWSR1_type1_retained"] >= b["EWSR1_RRM_start"],
       f"431 vs RRM start {b['EWSR1_RRM_start']}")
    ck("G2", "E360 stops before the RRM", cons["E360"]["length"] == b["EWSR1_RRM_start"] - 1)
    ck("G2", "no simulated window reaches into the RRM",
       all(c["length"] < b["EWSR1_RRM_start"] for c in cons.values()
           if c["window"].startswith("EWSR1") and c["role"] in ("TEST", "CONTROL")))

    # G3 - every natural sequence is a verbatim prefix of a committed cached sequence
    for cid, gene in (("E264", "EWSR1"), ("E360", "EWSR1"), ("T161", "TAF15"),
                      ("C161", "TCF12"), ("C264", "TCF12"), ("C360", "TCF12"),
                      ("N260", "NR4A3"), ("F212", "FUS")):
        c = cons[cid]
        ck("G3", f"{cid} is a verbatim prefix of the cached {gene}",
           seqs[gene].startswith(c["sequence"]) and len(c["sequence"]) == c["length"])

    # G4 - length matching is exact, so chain length is not the between-partner variable
    for fet, non in (("E264", "C264"), ("E360", "C360"), ("T161", "C161")):
        ck("G4", f"{fet} and {non} are exactly length-matched",
           cons[fet]["length"] == cons[non]["length"],
           f"{cons[fet]['length']} vs {cons[non]['length']}")

    # G5 - TCF12 windows are isoform-independent, and the ambiguity we avoided is real
    ens, uni = seqs["TCF12"], seqs["TCF12_uniprot"]
    common = 0
    while common < min(len(ens), len(uni)) and ens[common] == uni[common]:
        common += 1
    ck("G5", "the two committed TCF12 isoforms agree over at least 396 residues", common >= 396,
       f"common prefix {common}")
    ck("G5", "every simulated TCF12 window lies inside that agreement",
       all(cons[c]["length"] <= common for c in ("C161", "C264", "C360")))
    ck("G5", "the isoform ambiguity is real beyond it - a 431-residue window WOULD differ",
       ens[:431] != uni[:431],
       "so truncating at the RRM removes a real ambiguity rather than a hypothetical one")

    # G6 - scrambles preserve composition exactly, differ from the parent, and are deterministic
    for parent in ("E264", "C264"):
        pseq = cons[parent]["sequence"]
        kids = [cons[f"{parent}_scr{i}"]["sequence"] for i in (1, 2, 3)]
        for i, k in enumerate(kids, start=1):
            ck("G6", f"{parent}_scr{i} preserves composition exactly",
               sorted(k) == sorted(pseq))
            ck("G6", f"{parent}_scr{i} is not the parent", k != pseq)
        ck("G6", f"{parent} scrambles are pairwise distinct", len(set(kids)) == 3)
    ck("G6", "scrambling is deterministic in its seed",
       scramble(cons["E264"]["sequence"], SCRAMBLE_SEEDS[0]) == cons["E264_scr1"]["sequence"])

    # G7 - the E-doped instrument control is a substitution, more negative, same length
    e, e15 = cons["E264"]["sequence"], cons["E264_E15"]["sequence"]
    ck("G7", "E-doping preserves length", len(e) == len(e15))
    ck("G7", "E-doping strictly lowers net charge",
       (e15.count("E") + e15.count("D")) > (e.count("E") + e.count("D")))
    ck("G7", "E-doping never touches position 1", e[0] == e15[0])
    ck("G7", "E-doping is deterministic", edope(e, EDOPE_SEED) == e15)

    # G8 - replicate seeds are distinct within and across constructs
    seeds = [replicate_seed(c["id"], k) for c in cons.values()
             for k in range(1, c["n_replicates"] + 1)]
    ck("G8", "every (construct, replicate) seed is distinct", len(set(seeds)) == len(seeds))
    ck("G8", "seeds are positive 32-bit", all(0 < s < 2 ** 31 for s in seeds))

    # G9 - the scorer returns the RIGHT verdict on synthetic input, including every negative.
    #      Each case is a single-site mutation of the clean one, so a guard cannot pass vacuously.
    def synth(values, extra=None):
        runs = []
        for cid, vals in values.items():
            for k, v in enumerate(vals, start=1):
                runs.append({"run_id": f"{cid}_r{k}", "construct": cid, "nu": v,
                             "frames_analysed": 1000, "wall_seconds": 9000.0,
                             "calvados_version": "0.8.1", "calvados_commit": "deadbeef",
                             "openmm_version": "8.4.0", "platform": "CPU",
                             "random_number_seed": replicate_seed(cid, k),
                             "sequence_sha256": "x" * 64})
        if extra:
            runs.extend(extra)
        return runs

    tight = lambda base: [base + d for d in (-0.002, -0.001, 0.0, 0.001, 0.002)]
    clean = {"E264": tight(0.50), "C264": tight(0.58), "E360": tight(0.50), "C360": tight(0.58),
             "T161": tight(0.50), "C161": tight(0.58), "N260": tight(0.58), "F212": tight(0.50),
             "E264_scr1": [0.54, 0.541], "E264_scr2": [0.539, 0.54], "E264_scr3": [0.54, 0.54],
             "C264_scr1": [0.60, 0.601], "C264_scr2": [0.60, 0.60], "C264_scr3": [0.599, 0.60],
             "E264_E15": [0.66, 0.661, 0.659]}
    r = score(synth(clean))
    ck("G9", "clean separation scores SEPARATION_OBSERVED", r["verdict"] == "SEPARATION_OBSERVED",
       str(r.get("verdict")))
    ck("G9", "clean case raises no negative", r["negatives"] == [], str(r.get("negatives")))
    ck("G9", "clean case rejects all three primary pairs under Holm",
       all(r["pairs"][f"{a}_vs_{b}"].get("holm_reject_at_0.05") for a, b in PRIMARY_FAMILY))
    ck("G9", "the primary permutation design is powered",
       all(r["pairs"][f"{a}_vs_{b}"]["permutation"]["powered"] for a, b in PRIMARY_FAMILY))

    flat = dict(clean)
    for cid in ("C264", "C360", "C161", "N260"):
        flat[cid] = tight(0.50)
    r = score(synth(flat))
    ck("G9", "no separation scores NO_SEPARATION", r["verdict"] == "NO_SEPARATION", str(r["verdict"]))
    ck("G9", "no separation raises N2", "NEGATIVE_NO_STRATIFICATION" in r["negatives"])
    ck("G9", "no separation raises N4", "NEGATIVE_FET_NOT_SPECIAL" in r["negatives"])
    ck("G9", "flat wild-type control raises N3",
       "NEGATIVE_WILDTYPE_NOT_SEPARATED" in r["negatives"])

    comp = dict(clean)
    comp["E264_scr1"] = comp["E264_scr2"] = comp["E264_scr3"] = [0.50, 0.50]
    comp["C264_scr1"] = comp["C264_scr2"] = comp["C264_scr3"] = [0.58, 0.58]
    r = score(synth(comp))
    ck("G9", "scrambles matching their parents raise N1",
       "NEGATIVE_COMPOSITION_ONLY" in r["negatives"], str(r["negatives"]))
    ck("G9", "N1 does not suppress a real separation", r["verdict"] == "SEPARATION_OBSERVED")

    bad = dict(clean)
    bad["E264_E15"] = [0.50, 0.50, 0.50]
    r = score(synth(bad))
    ck("G9", "a failed electrostatics control is INSTRUMENT_FAILED, not a negative",
       r["verdict"] == "INSTRUMENT_FAILED" and "negatives" not in r)

    runs = synth(clean)
    runs[0]["frames_analysed"] = 10
    ck("G9", "too few frames is INSTRUMENT_FAILED",
       score(runs)["verdict"] == "INSTRUMENT_FAILED")
    runs = synth(clean)
    runs[0]["wall_seconds"] = None
    ck("G9", "an absent wall time is INSTRUMENT_FAILED",
       score(runs)["verdict"] == "INSTRUMENT_FAILED")
    runs = synth(clean)
    runs[0]["calvados_commit"] = None
    ck("G9", "missing provenance is INSTRUMENT_FAILED",
       score(runs)["verdict"] == "INSTRUMENT_FAILED")
    runs = synth(clean)
    runs[0]["nu"] = 1.4
    ck("G9", "an unphysical nu is INSTRUMENT_FAILED",
       score(runs)["verdict"] == "INSTRUMENT_FAILED")
    runs = synth(clean)
    for r_ in runs:
        if r_["construct"] == "E264":
            r_["random_number_seed"] = 7
    ck("G9", "repeated replicate seeds are INSTRUMENT_FAILED",
       score(runs)["verdict"] == "INSTRUMENT_FAILED")

    # G10 - the permutation floor is what the prespecification says it is
    p = permutation_p([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
    ck("G10", "5 vs 5 gives 252 arrangements", p["n_arrangements"] == 252, str(p))
    ck("G10", "the 5 vs 5 floor clears alpha/3", p["powered"])
    p3 = permutation_p([1, 2, 3], [4, 5, 6])
    ck("G10", "3 vs 3 is declared UNDERPOWERED up front", not p3["powered"],
       f"floor {p3['floor_p']}")

    # G11 - an empty or partial input can never produce a verdict about a partner.
    #       ⛔ MEASURED VACUOUS ONCE: this guard used to accept `construct_means == {}` through an
    #       `or`, and `score([])` was returning NO_SEPARATION — a claim about the disease from zero
    #       simulations. The assertion is now on the verdict alone.
    r = score([])
    ck("G11", "zero runs is INCOMPLETE, never a separation verdict", r["verdict"] == "INCOMPLETE",
       str(r["verdict"]))
    ck("G11", "zero runs raises no negative", "negatives" not in r)
    partial = synth({k: v for k, v in clean.items() if k != "F212"})
    rp = score(partial)
    ck("G11", "one missing construct is INCOMPLETE", rp["verdict"] == "INCOMPLETE", str(rp["verdict"]))
    short = synth({**clean, "E264": tight(0.50)[:4]})
    rs = score(short)
    ck("G11", "one missing replicate is INCOMPLETE", rs["verdict"] == "INCOMPLETE", str(rs["verdict"]))
    extra_runs = synth(clean) + [{"run_id": "GHOST_r1", "construct": "GHOST", "nu": 0.5,
                                  "frames_analysed": 1000, "wall_seconds": 9000.0,
                                  "calvados_version": "0.8.1", "calvados_commit": "d",
                                  "openmm_version": "8.4.0", "platform": "CPU",
                                  "random_number_seed": 1, "sequence_sha256": "y" * 64}]
    ck("G11", "a construct outside the frozen manifest is INCOMPLETE",
       score(extra_runs)["verdict"] == "INCOMPLETE")

    n_pass = sum(1 for _, _, ok, _ in checks if ok)
    print(f"emc_condensate_calvados --selftest: {n_pass}/{len(checks)} checks pass "
          f"across {len(set(g for g, _, _, _ in checks))} guard groups")
    for f in failures:
        print("  FAIL " + f)
    return 0 if not failures else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--plddt", action="store_true")
    ap.add_argument("--prepare", nargs=2, metavar=("CONSTRUCT", "REPLICATE"))
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--analyse", metavar="RUNDIR")
    ap.add_argument("--reduce", nargs="*", metavar="RUNJSON")
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.manifest:
        cons = build_constructs()
        payload = {"_prespecification": "emc-condensate-calvados-prespecification.md",
                   "_frozen": "the construct set, the protocol and the scorer are frozen with the "
                              "prespecification; an amendment is appended, dated and numbered",
                   "protocol": PROTOCOL, "n_constructs": len(cons),
                   "n_runs": sum(c["n_replicates"] for c in cons),
                   "primary_family": [list(p) for p in PRIMARY_FAMILY],
                   "secondary_pairs": [list(p) for p in SECONDARY_PAIRS],
                   "constructs": cons}
        dest = args.out or MANIFEST_OUT
        with open(dest, "w") as fh:
            json.dump(payload, fh, indent=1)
        print(f"wrote {dest}: {len(cons)} constructs, {payload['n_runs']} runs")
        return 0
    if args.plddt:
        res = fetch_plddt()
        dest = args.out or PLDDT_OUT
        with open(dest, "w") as fh:
            json.dump(res, fh, indent=1)
        print(json.dumps(res["windows"], indent=1))
        return 0
    if args.prepare:
        prepare(args.prepare[0], int(args.prepare[1]), args.outdir)
        return 0
    if args.analyse:
        rec = analyse(args.analyse)
        dest = args.out or os.path.join(args.analyse, "analysis.json")
        with open(dest, "w") as fh:
            json.dump(rec, fh, indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k != "protocol"}, indent=1))
        return 0
    if args.reduce is not None:
        runs = [_load(p) for p in args.reduce]
        res = score(runs)
        res["_prespecification"] = "emc-condensate-calvados-prespecification.md"
        res["n_runs_reduced"] = len(runs)
        res["runs"] = runs
        dest = args.out or OUT
        with open(dest, "w") as fh:
            json.dump(res, fh, indent=1)
        print(json.dumps({k: v for k, v in res.items() if k != "runs"}, indent=1))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
