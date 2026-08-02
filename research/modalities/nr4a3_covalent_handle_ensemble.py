#!/usr/bin/env python3
"""
NR4A3-UNIQUE CYSTEINES — accessibility ACROSS the experimental ensemble, with the NR-V04 site as the
positive control ($0, CPU/CI only).

THE QUESTION. NR-V04 (Zhang et al. 2018) is the one working NR4A degrader: a celastrol-VHL PROTAC that
degrades NR4A1 and spares NR4A2/NR4A3. Its selectivity is ATTRIBUTED — proposed, never structurally
confirmed — to covalent engagement at NR4A1 Cys551, a position where NR4A3 carries Thr579 and NR4A2 Tyr.
That mechanism is therefore unavailable on NR4A3. The reciprocal question is whether NR4A3 carries a
cysteine of its OWN that both paralogues lack, and whether any such cysteine is plausibly ligandable.

WHAT IS ALREADY ANSWERED ELSEWHERE, AND IS NOT RE-DERIVED HERE (rule 1 — one fact, one place):
  * Which NR4A3 cysteines are paralogue-unique, by two independent aligners, lives in
    `nr4a_paralogue_unique_residues.py` -> `nr4a-paralogue-unique-residues.json`. This module IMPORTS that
    classifier and CROSS-CHECKS its committed numbers rather than restating them.
  * That NR4A1 Cys551 is unique to NR4A1 lives in `nrv04_cys_conservation.py`.
  * The 8XTT <-> UniProt numbering map and the per-conformer pocket druggability live in
    `nr4a3_8xtt_benchmark.py` -> `results/nr4a3-pocket-reharmonize/8xtt/nr4a3-8xtt-benchmark.json`. The
    numbering map derived here is CHECKED against that artifact's `mapped_pocket5_8xtt`.

WHAT IS NEW HERE, AND WHY IT WAS NEEDED. The committed unique-residue map reports accessibility from ONE
static opened conformer (its own `_limits` says so). A single conformer's RSA is not an answer to "is this
cysteine ligandable" — apo NR4A3 is a molten, cryptic-pocket protein whose experimental structure is a
20-model solution-NMR ensemble (PDB 8XTT) with 2.3-4.4 A pocket-local Ca spread. So this module reports a
DISTRIBUTION per cysteine across all 20 experimental conformers, and states the spread as the finding.

And the committed map has NO positive control: it never ran its own criteria on NR4A1 Cys551, the one
cysteine a real covalent degrader is believed to use. Criteria that cannot recover the known case cannot be
trusted on the unknown one, so the control is computed here under BYTE-IDENTICAL criteria and reported
whether or not it passes.

CRITERIA ARE PRE-SPECIFIED BY IMPORT, NOT CHOSEN HERE. Both thresholds are taken from constants that
already existed in the repo before this question was asked:
    EXPOSED_RSA = 0.25                     (nr4a_differential_atlas)
    REACH_BANDS = 8 / 12 / 22 A            (nr4a_paralogue_unique_residues)
They are imported, never re-typed. If the control fails them, that is the reported result — the thresholds
are not moved to make NR4A3 look better.

METHOD. Pure stdlib. Shrake-Rupley SASA (the atlas implementation, same 96 sphere points) evaluated on the
atoms of interest with every atom of the structure as an occluder — mathematically identical to the atlas's
whole-structure call for those residues, and ~400x cheaper, which is what makes 60+ conformers free.
Numbering is established by GLOBAL SEQUENCE ALIGNMENT of each model's own ATOM-record sequence to its
UniProt sequence, never by an assumed offset, and the alignment identity is asserted.

HONEST LIMITS (carried into the JSON). Sequence uniqueness is exact. Everything downstream — accessibility,
tether reach, adduct formation, degradation — is a hypothesis generated for testing. Intrinsic thiol
reactivity (pKa, local electrostatics, hard/soft preference) is NOT computed. No claim is made that a
covalent NR4A3 degrader is feasible; this module reports accessibility, its spread, and whether the known
case is recovered. Feasibility is not a conclusion available from these measurements.

Outputs: nr4a3-covalent-handle-ensemble.json (+ .md)
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nr4a_differential_atlas as atlas                 # noqa: E402  parse_pdb / nw_align / SASA / MAXASA
import nr4a_paralogue_unique_residues as uniq           # noqa: E402  classify_positions / pocket / bands
import nrv04_cys_conservation as cyscons                # noqa: E402  _context

# ---- imported, never re-typed: the criteria this module is graded on -----------------------------------
EXPOSED_RSA = atlas.EXPOSED_RSA                          # 0.25
REACH_BANDS = uniq.REACH_BANDS                           # 8 / 12 / 22 A
CRYPTIC_POCKET_UNIPROT = uniq.CRYPTIC_POCKET_UNIPROT     # fpocket pocket 5 lining, NR4A3 UniProt numbering
ACCESSIONS = {k: v for k, v in uniq.ACCESSIONS.items() if k.startswith("NR4A")}

# NR4A3 LBD construct bounds (uniq owns them)
LBD_FIRST, LBD_LAST = uniq.LBD_FIRST, uniq.LBD_LAST

# The known case. PROPOSED by Zhang et al. 2018 from mutagenesis + mass spec, NOT structurally confirmed —
# the wording matters and is carried into the artifact.
POSITIVE_CONTROL = ("NR4A1", 551)

PDB_ID = "8XTT"
MIN_ALIGN_IDENTITY = 0.90        # a model and its own UniProt sequence: anything lower means wrong input

# Ensembles already in the repo. Every path is checked and a missing one is REFUSED (reported as UNREAD),
# never silently treated as an empty ensemble.
ENSEMBLES = {
    "NR4A3_8xtt_nmr": {
        "protein": "NR4A3",
        "kind": "experimental solution-NMR ensemble (PDB 8XTT, 20 conformers)",
        "glob": None,        # supplied at runtime: fetched from RCSB (CI) or --models-dir
    },
    "NR4A1_metad": {
        "protein": "NR4A1",
        "kind": "metadynamics pocket-opening ensemble (biased along a pocket CV — NOT a Boltzmann ensemble)",
        "glob": "results/nr4a1-pocket-ensemble/metad/*/frame.pdb",
    },
    "NR4A2_metad": {
        "protein": "NR4A2",
        "kind": "metadynamics pocket-opening ensemble (biased along a pocket CV — NOT a Boltzmann ensemble)",
        "glob": "results/nr4a2-pocket-ensemble/metad/*/frame.pdb",
    },
}

# The state-matched single models — the apples-to-apples layer across all three paralogues.
OPENED = {"NR4A1": "results/nr4a3-matrix/nr4a1-opened.pdb",
          "NR4A2": "results/nr4a3-matrix/nr4a2-opened.pdb",
          "NR4A3": "results/nr4a3-matrix/nr4a3-opened.pdb"}


# ==============================================================================================
# PURE FUNCTIONS — no I/O, no network. Unit-tested in tests/test_nr4a3_covalent_handle_ensemble.py
# ==============================================================================================
def atom_sasa(atoms, target_indices, n_points: int = 96):
    """Per-atom SASA (A^2) for `target_indices` only, with EVERY atom in `atoms` acting as an occluder.

    SASA is per-atom additive, so summing this over a residue's atoms reproduces
    `atlas.shrake_rupley(atoms)[resid]` exactly at the same `n_points` — asserted by a unit test and by the
    cross-check against the committed unique-residue artifact. Evaluating only the atoms of interest is what
    makes a 60-conformer sweep free: ~10 target atoms instead of ~4000.
    """
    sphere = atlas._fib_sphere(n_points)
    rad = [atlas.VDW.get(a["elem"], 1.70) + atlas.PROBE for a in atoms]
    xs = [a["x"] for a in atoms]
    ys = [a["y"] for a in atoms]
    zs = [a["z"] for a in atoms]
    unit = 4.0 * math.pi / n_points
    out = {}
    for i in target_indices:
        ri = rad[i]
        cand = []
        for j in range(len(atoms)):
            if j == i:
                continue
            d2 = (xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2 + (zs[i] - zs[j]) ** 2
            if d2 < (ri + rad[j]) ** 2:
                cand.append(j)
        acc = 0
        for (px, py, pz) in sphere:
            tx, ty, tz = xs[i] + px * ri, ys[i] + py * ri, zs[i] + pz * ri
            for j in cand:
                if (tx - xs[j]) ** 2 + (ty - ys[j]) ** 2 + (tz - zs[j]) ** 2 < rad[j] * rad[j]:
                    break
            else:
                acc += 1
        out[i] = acc * unit * ri * ri
    return out


def pdb_to_uniprot_map(residues, uniprot_seq, min_identity: float = MIN_ALIGN_IDENTITY):
    """{pdb residue number -> UniProt residue number} by GLOBAL alignment of the model's own ATOM-record
    sequence to its UniProt sequence. Never an assumed offset.

    Returns (map, identity). Raises if identity < min_identity — a model and its own UniProt sequence are the
    same protein, so a low identity means the wrong chain, a corrupt file or a numbering catastrophe, and a
    silent wrong answer is the one failure mode this repo keeps paying for.
    """
    ids = [r for r, _ in residues]
    seq = "".join(a for _, a in residues)
    pairs = atlas.nw_align(seq, uniprot_seq)
    m, matched = {}, 0
    for ia, ib in pairs:
        if ia is None or ib is None:
            continue
        m[ids[ia]] = ib + 1
        if seq[ia] == uniprot_seq[ib]:
            matched += 1
    identity = matched / len(seq) if seq else 0.0
    if identity < min_identity:
        raise ValueError(
            f"alignment identity {identity:.3f} < {min_identity} over {len(seq)} modelled residues — "
            f"refusing to map (wrong chain / corrupt model / not this protein?)")
    return m, identity


def reach_class(d):
    """Imported band logic — `uniq._reach_class` is the one home of the thresholds."""
    return uniq._reach_class(d)


def spread(values):
    """min/q1/median/q3/max/IQR/mean over a list. `None`s are dropped and COUNTED, never silently ignored:
    an absent reading is not a reading of absence."""
    vals = sorted(v for v in values if v is not None)
    n_missing = sum(1 for v in values if v is None)
    if not vals:
        return {"n": 0, "n_missing": n_missing}

    def q(p):
        if len(vals) == 1:
            return vals[0]
        k = p * (len(vals) - 1)
        lo, hi = int(math.floor(k)), int(math.ceil(k))
        return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)

    return {"n": len(vals), "n_missing": n_missing,
            "min": round(vals[0], 3), "q1": round(q(0.25), 3), "median": round(q(0.5), 3),
            "q3": round(q(0.75), 3), "max": round(vals[-1], 3),
            "iqr": round(q(0.75) - q(0.25), 3),
            "mean": round(sum(vals) / len(vals), 3)}


def criteria(rsa, dist_pocket):
    """THE pre-specified test, applied identically to every cysteine in every structure.

    accessible : residue RSA >= EXPOSED_RSA        (atlas constant, 0.25)
    reachable  : reach_class(dist) in the tethered bands (in_pocket / exit_vector / linker_borne)
    flagged    : both.
    """
    acc = rsa is not None and rsa >= EXPOSED_RSA
    rc = reach_class(dist_pocket) if dist_pocket is not None else None
    rch = rc in ("in_pocket", "exit_vector", "linker_borne")
    return {"accessible": acc, "reach_class": rc, "reachable": rch, "flagged": bool(acc and rch)}


def cysteine_geometry(residues, atoms, uni_map, pocket_uniprot, n_points: int = 96,
                      sg_n_points: int = 960):
    """Per-cysteine geometry for ONE model.

    TWO SPHERE COUNTS, DELIBERATELY. Shrake-Rupley quantises an atom's SASA into `4*pi*r^2/n_points`
    lumps; for a sulfur (r = 1.8 + 1.4 probe) at n_points = 96 that lump is **1.34 A^2**, so every SG number
    lands on a multiple of 1.34 and two cysteines differing by less than that are indistinguishable noise.
    (It is why two unrelated sites in this artifact both read exactly 24.13 = 18 x 1.34.)
      * `n_points` (96) is used for the RESIDUE RSA, because that is what the committed
        `nr4a-paralogue-unique-residues.json` used and the cross-check must reproduce it exactly.
      * `sg_n_points` (960) is used for the single-ATOM SG measures, where the extra points cost nothing
        (one atom, not four thousand) and buy a ~10x finer quantum.
    Mixing them would be wrong; keeping them separate is what lets the artifact be both reproducible and
    precise where precision matters.

    Returns {uniprot_resnum: {rsa, sg_sasa_A2, sg_sasa_heavy_A2, dist_to_pocket_A, ...}}.

    Two SASA conventions are reported deliberately, because they answer different questions and quoting one
    as the other is exactly the kind of silent substitution rule 1 exists to stop:
      * `rsa` / `sg_sasa_A2`   — ALL atoms present (hydrogens included). This is the convention the committed
                                 `nr4a-paralogue-unique-residues.json` used, so the two are comparable.
      * `sg_sasa_heavy_A2`     — hydrogens deleted from the structure. Protonation-independent, and the
                                 convention covalent-ligandability work uses for a thiol sulfur.
    """
    by_res = {}
    for idx, a in enumerate(atoms):
        by_res.setdefault(a["resid"], []).append(idx)

    pocket_local = [r for r, u in uni_map.items() if u in set(pocket_uniprot)]
    pocket_atom_idx = [i for r in pocket_local for i in by_res.get(r, [])]

    cys_local = [r for r, aa in residues if aa == "C"]
    targets = [i for r in cys_local for i in by_res.get(r, [])]
    sasa_all = atom_sasa(atoms, targets, n_points) if targets else {}
    # finer, atom-level pass for the SG only (see the two-sphere-count note above)
    sg_all_idx = [i for r in cys_local for i in by_res.get(r, []) if atoms[i]["name"] == "SG"]
    sasa_all_sg = atom_sasa(atoms, sg_all_idx, sg_n_points) if sg_all_idx else {}

    heavy_idx = [i for i, a in enumerate(atoms) if a["elem"] != "H"]
    heavy_atoms = [atoms[i] for i in heavy_idx]
    remap = {old: new for new, old in enumerate(heavy_idx)}
    sg_of = {}
    heavy_targets = []
    for r in cys_local:
        for i in by_res.get(r, []):
            if atoms[i]["name"] == "SG":
                sg_of[r] = i
            if i in remap:
                heavy_targets.append(remap[i])
    sasa_heavy = atom_sasa(heavy_atoms, heavy_targets, n_points) if heavy_targets else {}
    sg_heavy_idx = [remap[i] for i in sg_all_idx if i in remap]
    sasa_heavy_sg = atom_sasa(heavy_atoms, sg_heavy_idx, sg_n_points) if sg_heavy_idx else {}

    # Per-residue REFERENCE for the SG: its SASA with only its own residue's heavy atoms present. This is
    # the Gly-X-Gly-style denominator applied at the ATOM level, so `sg_rel` asks "how much of what this
    # thiol could expose in this rotamer is actually exposed" — the question a warhead cares about, which
    # residue-level RSA does not answer (RSA averages the SG in with a backbone that may be buried).
    sg_ref = {}
    for r in cys_local:
        own = [atoms[i] for i in by_res.get(r, []) if atoms[i]["elem"] != "H"]
        if not own:
            continue
        k = next((j for j, a in enumerate(own) if a["name"] == "SG"), None)
        if k is not None:
            sg_ref[r] = atom_sasa(own, [k], sg_n_points)[k]

    out = {}
    for r in cys_local:
        uni = uni_map.get(r)
        if uni is None:
            continue                      # modelled residue with no UniProt counterpart — reported as absent
        res_sasa = sum(sasa_all.get(i, 0.0) for i in by_res.get(r, []))
        maxasa = atlas.MAXASA.get("C")
        sg_i = sg_of.get(r)
        d_pocket = None
        if sg_i is not None and pocket_atom_idx:
            p = (atoms[sg_i]["x"], atoms[sg_i]["y"], atoms[sg_i]["z"])
            d_pocket = min(math.dist(p, (atoms[j]["x"], atoms[j]["y"], atoms[j]["z"]))
                           for j in pocket_atom_idx)
        rsa = (res_sasa / maxasa) if maxasa else None
        sg_heavy = (None if sg_i is None or remap.get(sg_i) is None
                    else sasa_heavy_sg.get(remap[sg_i], 0.0))
        res_sasa_heavy = sum(sasa_heavy.get(remap[i], 0.0)
                             for i in by_res.get(r, []) if i in remap)
        rsa_heavy = (res_sasa_heavy / maxasa) if maxasa else None
        ref = sg_ref.get(r)
        sg_rel = (sg_heavy / ref) if (sg_heavy is not None and ref) else None
        row = {
            "pdb_resnum": r,
            "rsa": None if rsa is None else round(rsa, 3),
            "rsa_heavy": None if rsa_heavy is None else round(rsa_heavy, 3),
            "residue_sasa_A2": round(res_sasa, 2),
            "residue_sasa_heavy_A2": round(res_sasa_heavy, 2),
            "sg_sasa_A2": None if sg_i is None else round(sasa_all_sg.get(sg_i, 0.0), 2),
            "sg_sasa_heavy_A2": None if sg_heavy is None else round(sg_heavy, 2),
            "sg_sasa_isolated_A2": None if ref is None else round(ref, 2),
            "sg_rel": None if sg_rel is None else round(sg_rel, 3),
            "dist_to_pocket_A": None if d_pocket is None else round(d_pocket, 2),
            "sg_present": sg_i is not None,
        }
        row.update(criteria(rsa, d_pocket))
        out[uni] = row
    return out


def map_pocket_to(seq_from, seq_to, positions):
    """Map a residue-number set from one paralogue's UniProt numbering into another's, by global alignment.
    Used to place the NR4A3 cryptic pocket on NR4A1/NR4A2 so the positive control is measured against the
    SAME site, not a differently-defined one."""
    m = {}
    for ia, ib in atlas.nw_align(seq_from, seq_to):
        if ia is None or ib is None:
            continue
        m[ia + 1] = ib + 1
    return sorted(m[p] for p in positions if p in m), [p for p in positions if p not in m]


def summarise_ensemble(per_model, uniprots):
    """Collapse {model_label: {uniprot: row}} into per-cysteine distributions + flag counts."""
    out = {}
    for u in uniprots:
        rows = [per_model[k].get(u) for k in sorted(per_model)]
        present = [r for r in rows if r is not None]
        out[u] = {
            "n_models": len(rows),
            "n_models_with_residue": len(present),
            "n_models_missing_residue": len(rows) - len(present),
            "rsa": spread([r["rsa"] for r in present]),
            "sg_sasa_A2": spread([r["sg_sasa_A2"] for r in present]),
            "sg_sasa_heavy_A2": spread([r["sg_sasa_heavy_A2"] for r in present]),
            "sg_rel": spread([r["sg_rel"] for r in present]),
            "dist_to_pocket_A": spread([r["dist_to_pocket_A"] for r in present]),
            "n_accessible": sum(1 for r in present if r["accessible"]),
            "n_reachable": sum(1 for r in present if r["reachable"]),
            "n_flagged": sum(1 for r in present if r["flagged"]),
            "reach_classes": sorted({r["reach_class"] for r in present if r["reach_class"]}),
            "per_model": {k: per_model[k].get(u) for k in sorted(per_model)},
        }
    return out


# ==============================================================================================
# I/O
# ==============================================================================================
def _load(path):
    residues, atoms = atlas.parse_pdb(path)
    return residues, atoms


def fetch_8xtt_models(dest_dir, pdb_id=PDB_ID):
    """Download the multi-MODEL NMR PDB from RCSB and split it into one file per conformer.
    NETWORK — the dev sandbox's egress proxy 403s files.rcsb.org, so this path is CI-only (§6)."""
    import nr4a3_8xtt_benchmark as bench
    os.makedirs(dest_dir, exist_ok=True)
    raw = os.path.join(dest_dir, f"{pdb_id}.pdb")
    bench.fetch_rcsb(pdb_id, raw)
    with open(raw) as fh:
        text = fh.read()
    models = bench.split_models(text)
    paths = []
    for i, body in enumerate(models, start=1):
        p = os.path.join(dest_dir, f"{pdb_id.lower()}_m{i}.pdb")
        with open(p, "w") as fh:
            fh.write(body)
        paths.append(p)
    return paths


def model_label(path):
    """A label that is UNIQUE per model file.

    ⚠ Not cosmetic. The NR4A1/NR4A2 metadynamics ensembles are 25 directories each containing a file called
    `frame.pdb`, so keying on the basename collapses all 25 onto one dict entry and silently reports an
    ensemble of ONE — which is exactly the class of failure (a populated field that looks plausible but was
    not measured) §4 warns about, and it happened here on the first run. The parent directory name is what
    distinguishes them, so it is part of the key.
    """
    parent = os.path.basename(os.path.dirname(os.path.abspath(path)))
    base = os.path.basename(path)
    return f"{parent}/{base}" if parent else base


def analyse_models(paths, uniprot_seq, pocket_uniprot, label_fn=None, n_points: int = 96,
                   sg_n_points: int = 960):
    """Run cysteine_geometry over a list of model paths. Returns (per_model, identities, refusals).

    Labels are asserted UNIQUE — a duplicate would silently discard a model (see `model_label`)."""
    labels = [(label_fn or model_label)(p) for p in paths]
    if len(set(labels)) != len(labels):
        dupes = sorted({l for l in labels if labels.count(l) > 1})
        raise ValueError(f"model labels are not unique ({dupes[:3]}...) — refusing to silently drop models")
    per_model, identities, refusals = {}, {}, []
    for p in sorted(paths):
        label = (label_fn or model_label)(p)
        try:
            residues, atoms = _load(p)
            uni_map, ident = pdb_to_uniprot_map(residues, uniprot_seq)
        except Exception as exc:                              # noqa: BLE001 — refusal is the product
            refusals.append({"model": label, "path": p, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        identities[label] = round(ident, 4)
        per_model[label] = cysteine_geometry(residues, atoms, uni_map, pocket_uniprot, n_points,
                                             sg_n_points)
    return per_model, identities, refusals


def crosscheck_committed(nr4a3_opened_rows, committed_path):
    """Rule 1: this module must not produce a SECOND value for a number that already has a home. Reproduce
    the committed unique-residue artifact's `rsa` and `dist_to_cryptic_pocket_A` for the NR4A3 opened model
    and report agreement. A mismatch is a finding, not something to paper over."""
    if not os.path.exists(committed_path):
        return {"status": "UNREAD", "path": committed_path,
                "note": "committed artifact not present — cross-check NOT performed (not 'passed')"}
    with open(committed_path) as fh:
        d = json.load(fh)
    checks, worst_rsa, worst_d = [], 0.0, 0.0
    for r in d.get("nr4a3_cysteines", []):
        g = r.get("geometry") or {}
        if "rsa" not in g:
            continue
        mine = nr4a3_opened_rows.get(r["resnum"])
        if mine is None:
            checks.append({"resnum": r["resnum"], "status": "MISSING_HERE"})
            continue
        d_rsa = abs(mine["rsa"] - g["rsa"])
        d_dist = abs((mine["dist_to_pocket_A"] or 0) - (g["dist_to_cryptic_pocket_A"] or 0))
        worst_rsa, worst_d = max(worst_rsa, d_rsa), max(worst_d, d_dist)
        checks.append({"resnum": r["resnum"], "committed_rsa": g["rsa"], "here_rsa": mine["rsa"],
                       "committed_dist_A": g["dist_to_cryptic_pocket_A"],
                       "here_dist_A": mine["dist_to_pocket_A"],
                       "d_rsa": round(d_rsa, 4), "d_dist_A": round(d_dist, 3)})
    ok = bool(checks) and worst_rsa <= 0.002 and worst_d <= 0.02
    return {"status": "AGREES" if ok else ("DISAGREES" if checks else "NO_OVERLAP"),
            "source_of_truth": os.path.relpath(committed_path, REPO),
            "max_abs_rsa_delta": round(worst_rsa, 4), "max_abs_dist_delta_A": round(worst_d, 3),
            "tolerance": {"rsa": 0.002, "dist_A": 0.02}, "rows": checks}


# ==============================================================================================
# BUILD
# ==============================================================================================
def build(seqs, models_dir=None, n_points: int = 96, ensembles=None, struct_root=REPO,
          sg_n_points: int = 960):
    ensembles = ENSEMBLES if ensembles is None else ensembles
    refusals, unread = [], []

    # ---- layer 0: sequence uniqueness (imported classifier; cross-checked, not restated) --------------
    cys_rows = uniq.classify_positions(seqs, residue_types=("C",))
    lbd_cys = [r for r in cys_rows if LBD_FIRST <= r["resnum"] <= LBD_LAST]
    unique_lbd = [r["resnum"] for r in lbd_cys if r["unique_vs_both"] and r["alignment_robust"]]

    # positive control: is the NR-V04 site really a paralogue-unique Cys of NR4A1?
    pc_prot, pc_num = POSITIVE_CONTROL
    pc_res = seqs[pc_prot][pc_num - 1]
    pc_partners = {}
    for other in [p for p in ACCESSIONS if p != pc_prot]:
        aln_a, aln_b = cyscons.needleman_wunsch(seqs[pc_prot], seqs[other])
        res, idx = cyscons.aligned_residue(aln_a, aln_b, pc_num)
        pc_partners[other] = {"residue": res, "resnum": idx, "is_cysteine": res == "C"}

    # ---- pocket, mapped into each paralogue's own numbering -------------------------------------------
    pockets, pocket_unmapped = {"NR4A3": sorted(CRYPTIC_POCKET_UNIPROT)}, {}
    for other in ("NR4A1", "NR4A2"):
        mapped, missing = map_pocket_to(seqs["NR4A3"], seqs[other], CRYPTIC_POCKET_UNIPROT)
        pockets[other], pocket_unmapped[other] = mapped, missing

    # ---- layer A: state-matched single opened models, all three paralogues -----------------------------
    opened = {}
    for prot, rel in OPENED.items():
        path = os.path.join(struct_root, rel)
        if not os.path.exists(path):
            unread.append({"input": rel, "reason": "file not present — UNREAD, not absent"})
            continue
        try:
            residues, atoms = _load(path)
            uni_map, ident = pdb_to_uniprot_map(residues, seqs[prot])
        except Exception as exc:                              # noqa: BLE001
            refusals.append({"input": rel, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        rows = cysteine_geometry(residues, atoms, uni_map, pockets[prot], n_points, sg_n_points)
        opened[prot] = {"path": rel, "alignment_identity": round(ident, 4),
                        "modelled_uniprot_range": [min(uni_map.values()), max(uni_map.values())],
                        "pocket_uniprot_used": pockets[prot], "cysteines": rows}

    # ---- layer B: ensembles ---------------------------------------------------------------------------
    ens_out = {}
    for name, cfg in ensembles.items():
        prot = cfg["protein"]
        if name == "NR4A3_8xtt_nmr":
            paths = sorted(glob.glob(os.path.join(models_dir, "*.pdb"))) if models_dir else []
            paths = [p for p in paths if not os.path.basename(p).upper().startswith(PDB_ID + ".")]
        else:
            paths = sorted(glob.glob(os.path.join(struct_root, cfg["glob"])))
        if not paths:
            unread.append({"input": name,
                           "reason": ("no model files found — UNREAD, not absent. "
                                      + ("8XTT needs a network fetch (files.rcsb.org is 403'd by the dev "
                                         "sandbox egress proxy); run this in CI or pass --models-dir."
                                         if name == "NR4A3_8xtt_nmr" else f"glob: {cfg['glob']}"))})
            continue
        per_model, idents, refs = analyse_models(paths, seqs[prot], pockets[prot], n_points=n_points,
                                                 sg_n_points=sg_n_points)
        refusals.extend([dict(r, ensemble=name) for r in refs])
        if not per_model:
            unread.append({"input": name, "reason": "every model refused — see refusals"})
            continue
        uniprots = sorted({u for rows in per_model.values() for u in rows})
        ens_out[name] = {
            "protein": prot, "kind": cfg["kind"], "n_models_found": len(paths),
            "n_models_analysed": len(per_model),
            "alignment_identity": spread(list(idents.values())),
            "pocket_uniprot_used": pockets[prot],
            "cysteines": summarise_ensemble(per_model, uniprots),
        }

    # ---- cross-checks ---------------------------------------------------------------------------------
    xcheck = {
        "committed_unique_residue_map": crosscheck_committed(
            opened.get("NR4A3", {}).get("cysteines", {}),
            os.path.join(HERE, "nr4a-paralogue-unique-residues.json")),
        "8xtt_numbering_vs_benchmark": _crosscheck_8xtt_numbering(models_dir, seqs, struct_root),
    }

    data = {
        "_title": ("NR4A3-unique cysteines: accessibility across the experimental ensemble, with NR4A1 "
                   "Cys551 (the NR-V04 site) as the positive control"),
        "_question": ("NR-V04's NR4A1 selectivity is ATTRIBUTED — proposed by Zhang et al. 2018, never "
                      "structurally confirmed — to covalent engagement at NR4A1 Cys551, a position NR4A3 "
                      "lacks. Does NR4A3 carry a cysteine of its own that BOTH paralogues lack, and how "
                      "accessible is it across the experimental ensemble?"),
        "_method": ("Uniqueness: imported from nr4a_paralogue_unique_residues.classify_positions (two "
                    "independent aligners). Geometry: Shrake-Rupley SASA (atlas implementation, "
                    f"{n_points} sphere points for residue SASA, {sg_n_points} for the single-atom SG "
                    "measures) on the atoms of interest with all atoms as occluders; SG "
                    "distance to the mapped cryptic pocket. Numbering by global BLOSUM62 alignment of each "
                    "model's ATOM-record sequence to its own UniProt sequence, identity asserted "
                    f">= {MIN_ALIGN_IDENTITY}. Pure stdlib, $0 CPU."),
        "_criteria": {
            "note": ("PRE-SPECIFIED BY IMPORT. Both thresholds already existed in the repo before this "
                     "question was asked and are imported, not re-typed here. They were NOT tuned."),
            "accessible": f"residue RSA >= EXPOSED_RSA ({EXPOSED_RSA}) — nr4a_differential_atlas",
            "reachable": ("SG within a tethered reach band (in_pocket/exit_vector/linker_borne) — "
                          "nr4a_paralogue_unique_residues.REACH_BANDS"),
            "reach_bands_A": {label: cut for cut, label in REACH_BANDS if cut != float("inf")},
            "flagged": "accessible AND reachable",
        },
        "_limits": [
            "Sequence uniqueness is exact. Accessibility, tether reach, adduct formation and degradation "
            "are HYPOTHESES generated for testing, not results.",
            "Intrinsic thiol reactivity (pKa, local electrostatics, hard/soft electrophile preference) is "
            "NOT computed. An exposed cysteine is not necessarily a reactive one.",
            "The 8XTT ensemble is 20 solution-NMR conformers of the APO LBD: a restraint-satisfying "
            "ensemble, not a Boltzmann-weighted one. Spread across it is a measure of experimental "
            "structural heterogeneity, not of populated-state probability.",
            "The NR4A1/NR4A2 metadynamics ensembles are BIASED along a pocket-opening collective variable "
            "and are not Boltzmann-weighted either; they are a heterogeneity comparator only.",
            "NR4A1 Cys551's status as the NR-V04 covalent site is PROPOSED (Zhang et al. 2018), not "
            "structurally confirmed. The positive control therefore tests the criteria against a "
            "literature attribution, not against a solved covalent complex.",
            "No claim is made — and none follows from these measurements — that a covalent NR4A3 degrader "
            "is feasible. This reports accessibility, its spread, and control recovery only.",
            "No efficacy, safety, therapeutic-window or clinical claim is made or implied.",
        ],
        "accessions": ACCESSIONS,
        "positive_control": {
            "protein": pc_prot, "resnum": pc_num, "residue": pc_res,
            "is_cysteine": pc_res == "C",
            "attribution": ("celastrol warhead of NR-V04; PROPOSED by Zhang et al. 2018 from mutagenesis "
                            "and MS, NOT structurally confirmed"),
            "paralogue_partners": pc_partners,
            "context": cyscons._context(seqs[pc_prot], pc_num),
        },
        "cryptic_pocket_uniprot_nr4a3": sorted(CRYPTIC_POCKET_UNIPROT),
        "pocket_mapped_into_paralogue_numbering": pockets,
        "pocket_positions_unmappable": pocket_unmapped,
        "nr4a3_lbd_cysteines": [
            {"resnum": r["resnum"], "context": r["context"],
             "nr4a1": r["partners"]["NR4A1"]["residue"], "nr4a1_resnum": r["partners"]["NR4A1"]["resnum"],
             "nr4a2": r["partners"]["NR4A2"]["residue"], "nr4a2_resnum": r["partners"]["NR4A2"]["resnum"],
             "unique_vs_both": r["unique_vs_both"], "alignment_robust": r["alignment_robust"]}
            for r in lbd_cys],
        "nr4a3_unique_lbd_cysteines": unique_lbd,
        "opened_models": opened,
        "ensembles": ens_out,
        "cross_checks": xcheck,
        "refusals": refusals,
        "unread_inputs": unread,
    }
    data["control_recovery"] = _control_recovery(data)
    data["control_rank"] = control_rank(opened)
    data["criteria_diagnosis"] = _criteria_diagnosis(data)
    data["thiol_hydrogen_occlusion"] = _hydrogen_occlusion(opened)
    data["comparison_validity"] = COMPARISON_VALIDITY
    data["summary"] = _summary(data)
    return data


# Which comparisons these numbers license — stated because the tempting one is the invalid one. The NR4A3
# ensemble is EXPERIMENTAL (solution NMR) and the only NR4A1/NR4A2 ensembles in the repo are BIASED
# metadynamics; putting their spreads side by side would compare structure-determination method as much as
# protein, and would flatter whichever side happened to be sampled more widely.
COMPARISON_VALIDITY = {
    "licensed": [
        {"comparison": "NR4A3 cysteines against each other, within the 8XTT ensemble",
         "why": "same protein, same 20 experimental conformers, same measurement"},
        {"comparison": ("NR4A1 Cys551 against every NR4A3/NR4A2 cysteine, on the state-matched opened "
                        "models (this is what `control_rank` does)"),
         "why": ("all three models come from one modelling pipeline in one state, so a rank across them "
                 "compares proteins rather than methods — which is why rank, not the ensemble spread, is "
                 "the load-bearing cross-paralogue statement here")},
        {"comparison": "the spread of one cysteine across conformers, read as structural heterogeneity",
         "why": "within a single ensemble, spread is a property of that ensemble and is reported as such"},
    ],
    "not_licensed": [
        {"comparison": ("NR4A3 8XTT ensemble spread against the NR4A1/NR4A2 metadynamics ensemble spread"),
         "why": ("experimental restraint-satisfying NMR conformers vs conformers driven along a "
                 "pocket-opening bias potential. Neither is Boltzmann-weighted and they are not weighted "
                 "the same way, so a difference in spread is not evidence about the proteins.")},
        {"comparison": "any ensemble spread read as a population or an occupancy",
         "why": "neither ensemble is Boltzmann-weighted; frequency across conformers is not probability"},
        {"comparison": "a flagged/not-flagged count read as evidence of ligandability",
         "why": ("the pre-specified criteria do not recover the known covalent site, so passing them is "
                 "not evidence — see criteria_diagnosis")},
    ],
    "absent_input": ("There is no experimental NR4A1 or NR4A2 LBD ensemble in this repo, so the like-for-"
                     "like ensemble comparison the question really wants CANNOT be made from what is here. "
                     "That is a missing input, not a negative result."),
}


def _hydrogen_occlusion(opened):
    """How much of each thiol sulfur's accessible surface is occluded by its OWN hydrogens.

    Measured, not assumed, because it decides which of the two SASA conventions may be quoted as "how
    accessible is this cysteine". The committed `nr4a-paralogue-unique-residues.json` uses the ALL-ATOM
    convention (atlas.parse_pdb keeps hydrogens), which measures the accessibility of the PROTONATED thiol
    — including the HG proton that a covalent warhead displaces. If the occlusion is large, the all-atom
    number systematically understates what a warhead sees, and the two conventions are not interchangeable.
    """
    rows = []
    for prot, blk in sorted(opened.items()):
        for uni, r in blk.get("cysteines", {}).items():
            a, h = r.get("sg_sasa_A2"), r.get("sg_sasa_heavy_A2")
            if a is None or not h:
                continue
            rows.append({"site": f"{prot} C{uni}", "sg_all_atom_A2": a, "sg_heavy_A2": h,
                         "fraction_occluded_by_own_H": round(1.0 - a / h, 3)})
    return {
        "note": ("SG SASA with hydrogens present vs deleted, per cysteine, on the state-matched opened "
                 "models. The occluding atom is the residue's own HG thiol proton — the atom a covalent "
                 "warhead replaces."),
        "per_cysteine": rows,
        "fraction_occluded": spread([r["fraction_occluded_by_own_H"] for r in rows]),
        "reading": ("A large occluded fraction means the ALL-ATOM convention answers 'how exposed is the "
                    "protonated thiol', not 'how exposed is the sulfur a warhead must reach'. Both are "
                    "reported here so neither can be quoted as the other; the pre-specified criterion uses "
                    "the all-atom convention because that is what the committed artifact used."),
    }


def _crosscheck_8xtt_numbering(models_dir, seqs, struct_root=REPO):
    """The alignment-derived 8XTT->UniProt map must reproduce the committed benchmark's mapped_pocket5."""
    ref = os.path.join(struct_root, "results", "nr4a3-pocket-reharmonize", "8xtt",
                       "nr4a3-8xtt-benchmark.json")
    if not os.path.exists(ref):
        return {"status": "UNREAD", "path": os.path.relpath(ref, struct_root)}
    with open(ref) as fh:
        committed = json.load(fh).get("mapped_pocket5_8xtt")
    paths = sorted(glob.glob(os.path.join(models_dir, "*.pdb"))) if models_dir else []
    paths = [p for p in paths if not os.path.basename(p).upper().startswith(PDB_ID + ".")]
    if not paths:
        return {"status": "UNREAD", "committed": committed,
                "reason": "no 8XTT model files available to derive a map from"}
    residues, _ = _load(paths[0])
    uni_map, _ = pdb_to_uniprot_map(residues, seqs["NR4A3"])
    rev = {u: p for p, u in uni_map.items()}
    derived = sorted(rev[u] for u in CRYPTIC_POCKET_UNIPROT if u in rev)
    return {"status": "AGREES" if derived == sorted(committed or []) else "DISAGREES",
            "committed": committed, "derived_here": derived,
            "source_of_truth": "results/nr4a3-pocket-reharmonize/8xtt/nr4a3-8xtt-benchmark.json"}


RANK_OBSERVABLES = (
    ("rsa", "residue RSA, ALL atoms (the criterion's own observable; hydrogens present)"),
    ("rsa_heavy", "residue RSA, hydrogens deleted"),
    ("sg_sasa_A2", "SG atom SASA, hydrogens present"),
    ("sg_sasa_heavy_A2", "SG atom SASA, hydrogens deleted"),
    ("sg_rel", "SG SASA / SG SASA of the same residue in isolation (rotamer-referenced)"),
)


def control_rank(opened, control=POSITIVE_CONTROL):
    """THRESHOLD-FREE control test: across every cysteine of all three state-matched opened models, where
    does the known covalent site RANK on each observable?

    This exists so the failure of a threshold can be diagnosed WITHOUT moving the threshold. A cutoff that
    misses the known site can be wrong in two very different ways — the OBSERVABLE is uninformative (the
    known site is mid-pack however you slice it), or the observable is fine and only the CUTOFF is
    misplaced (the known site ranks at the top and the line was drawn above it). Rank separates those, and
    unlike a re-tuned cutoff it cannot be gamed toward a preferred answer: the ordering is fixed by the
    structures. Rank 1 = most exposed. Ties share the better rank.
    """
    pc_prot, pc_num = control
    pool = []
    for prot, blk in sorted(opened.items()):
        for uni, row in blk.get("cysteines", {}).items():
            pool.append((prot, int(uni), row))
    if not pool:
        return {"status": "UNREAD", "reason": "no opened models analysed"}
    target = next((r for p, u, r in pool if p == pc_prot and u == pc_num), None)
    if target is None:
        return {"status": "UNREAD",
                "reason": f"{pc_prot} Cys{pc_num} absent from the modelled constructs"}
    out = {"status": "OK", "n_cysteines_pooled": len(pool),
           "pool": f"all cysteines of {', '.join(sorted(opened))} state-matched opened models",
           "observables": {}}
    for key, desc in RANK_OBSERVABLES:
        vals = [(r[key], p, u) for p, u, r in pool if r.get(key) is not None]
        if target.get(key) is None or not vals:
            out["observables"][key] = {"status": "UNREAD"}
            continue
        vals.sort(key=lambda t: -t[0])
        tv = target[key]
        rank = 1 + sum(1 for v, _, _ in vals if v > tv)
        out["observables"][key] = {
            "description": desc, "control_value": tv, "rank": rank, "of": len(vals),
            "percentile_from_top": round(100.0 * (rank - 1) / len(vals), 1),
            "top3": [f"{p} C{u} = {v}" for v, p, u in vals[:3]],
        }
    return out


def _control_recovery(d):
    """Did the pre-specified criteria flag NR4A1 Cys551 — the one cysteine a real covalent degrader is
    believed to use? If not, the criteria are wrong and that is the reported finding."""
    pc_prot, pc_num = POSITIVE_CONTROL
    op = d["opened_models"].get(pc_prot)
    if not op:
        return {"status": "UNREAD",
                "reason": f"{pc_prot} opened model unavailable — control NOT run (not 'passed')"}
    row = op["cysteines"].get(pc_num)
    if row is None:
        return {"status": "UNREAD",
                "reason": (f"{pc_prot} residue {pc_num} is not present in the modelled construct "
                           f"({op['modelled_uniprot_range']}) — control NOT run")}
    ens = d["ensembles"].get("NR4A1_metad", {}).get("cysteines", {}).get(pc_num)
    which = []
    if not row["accessible"]:
        which.append(f"accessible (RSA {row['rsa']} < {EXPOSED_RSA})")
    if not row["reachable"]:
        which.append(f"reachable (reach_class {row['reach_class']})")
    return {
        "status": "RECOVERED" if row["flagged"] else "NOT_RECOVERED",
        "site": f"{pc_prot} Cys{pc_num}",
        "failed_criteria": which,
        "passed_criteria": [k for k in ("accessible", "reachable") if row[k]],
        "state_matched_model": row,
        "ensemble": ens,
        "reading": (
            "The pre-specified criteria FLAG the known covalent site. They are therefore not obviously "
            "wrong, and the same criteria applied to NR4A3 can be read at face value."
            if row["flagged"] else
            "The pre-specified criteria DO NOT flag the known covalent site. Per the design of this "
            "analysis that is the finding: the criteria are wrong, or too coarse, and any NR4A3 cysteine "
            "they flag inherits that unreliability. The thresholds are NOT adjusted to fix this — see "
            "`criteria_diagnosis` for the threshold-free reading that replaces them."),
    }


def _criteria_diagnosis(d):
    """WHY the criteria behaved as they did, from the rank test — and an explicit refusal to re-tune.

    A cutoff that misses the known site is ambiguous between 'the observable is uninformative' and 'the
    observable is fine, the line is in the wrong place'. `control_rank` discriminates them. Neither reading
    licenses moving the line: this module reports RANKS, which no choice of cutoff can flatter.
    """
    cr, rk = d.get("control_recovery", {}), d.get("control_rank", {})
    if cr.get("status") == "UNREAD" or rk.get("status") != "OK":
        return {"status": "UNREAD", "reason": "control or rank pool unavailable — no diagnosis"}
    obs = rk["observables"]
    ranks = {k: v["rank"] for k, v in obs.items() if "rank" in v}
    n = max((v["of"] for v in obs.values() if "of" in v), default=0)
    top_decile = {k: r for k, r in ranks.items() if n and (r - 1) / n <= 0.20}
    if cr["status"] == "RECOVERED":
        verdict = "criteria recovered the control; no diagnosis needed"
    elif top_decile:
        verdict = ("OBSERVABLE INFORMATIVE, CUTOFF MISPLACED. The known covalent site is not mid-pack — it "
                   "ranks in the top fifth of all pooled NR4A-family LBD cysteines on "
                   f"{len(top_decile)}/{len(ranks)} accessibility observables ({', '.join(sorted(top_decile))}). "
                   "So accessibility does order these cysteines usefully; what fails is the location of the "
                   "0.25 RSA line, which sits ABOVE the known site. The line is NOT moved here — a cutoff "
                   "re-fitted to make the control pass would make every downstream NR4A3 call circular. "
                   "Rank is reported instead, and rank is what any NR4A3 statement must be read against.")
    else:
        verdict = ("OBSERVABLE UNINFORMATIVE. The known covalent site is mid-pack or worse on every "
                   "accessibility observable, so no cutoff on these measures could separate it from "
                   "cysteines that are not covalent-degrader sites. Static accessibility is therefore not "
                   "evidence about ligandability here, and NR4A3 cysteines must not be ranked on it.")
    return {
        "status": cr["status"],
        "ranks": ranks,
        "n_pooled": n,
        "verdict": verdict,
        "refusal": ("Thresholds are imported from pre-existing repo constants and are NOT re-fitted in this "
                    "module. See `_criteria` for their homes."),
    }


def _summary(d):
    uniq_nums = d["nr4a3_unique_lbd_cysteines"]
    nmr = d["ensembles"].get("NR4A3_8xtt_nmr", {}).get("cysteines", {})
    per_cys = {}
    for u in uniq_nums:
        e = nmr.get(u)
        if not e:
            per_cys[u] = {"ensemble": "UNREAD"}
            continue
        per_cys[u] = {
            "n_models": e["n_models_with_residue"],
            "rsa_median": e["rsa"].get("median"), "rsa_min": e["rsa"].get("min"),
            "rsa_max": e["rsa"].get("max"),
            "dist_median_A": e["dist_to_pocket_A"].get("median"),
            "dist_min_A": e["dist_to_pocket_A"].get("min"), "dist_max_A": e["dist_to_pocket_A"].get("max"),
            "n_flagged": e["n_flagged"], "reach_classes": e["reach_classes"],
        }
    return {
        "n_nr4a3_lbd_cysteines": len(d["nr4a3_lbd_cysteines"]),
        "n_nr4a3_lbd_cysteines_unique_vs_both": len(uniq_nums),
        "nr4a3_unique_lbd_cysteines": uniq_nums,
        "control_status": d["control_recovery"]["status"],
        "per_unique_cysteine_across_8xtt": per_cys,
        "n_refusals": len(d["refusals"]),
        "n_unread_inputs": len(d["unread_inputs"]),
    }


# ==============================================================================================
# markdown
# ==============================================================================================
def to_markdown(d):
    L = [f"# {d['_title']}", "", d["_question"], "", f"*Method:* {d['_method']}", ""]

    c = d["_criteria"]
    L += ["## Pre-specified criteria", "", c["note"], "",
          f"- **accessible** — {c['accessible']}", f"- **reachable** — {c['reachable']}",
          f"- **flagged** — {c['flagged']}", ""]

    pc = d["positive_control"]
    cr = d["control_recovery"]
    L += ["## Positive control — does the test recover the known case?", "",
          f"**{pc['protein']} {pc['residue']}{pc['resnum']}** — {pc['attribution']}.", "",
          "| paralogue | aligned residue | cysteine? |", "|---|---|---|"]
    for k, v in pc["paralogue_partners"].items():
        L.append(f"| {k} | {v['residue']}{v['resnum'] or '-'} | {'yes' if v['is_cysteine'] else 'no'} |")
    L += ["", f"**Result: {cr['status']}**", "", cr.get("reading", ""), ""]
    if cr.get("state_matched_model"):
        r = cr["state_matched_model"]
        L += [f"- state-matched opened model: RSA **{r['rsa']}** "
              f"(exposed >= {EXPOSED_RSA}: {r['accessible']}), SG-to-pocket **{r['dist_to_pocket_A']} A** "
              f"(`{r['reach_class']}`), SG SASA {r['sg_sasa_A2']} A^2 all-atom / "
              f"{r['sg_sasa_heavy_A2']} A^2 heavy-atom-only", ""]
    if cr.get("ensemble"):
        e = cr["ensemble"]
        L += [f"- across the {e['n_models_with_residue']}-frame NR4A1 metadynamics ensemble: "
              f"RSA {e['rsa'].get('min')}-{e['rsa'].get('max')} (median {e['rsa'].get('median')}), "
              f"SG-to-pocket {e['dist_to_pocket_A'].get('min')}-{e['dist_to_pocket_A'].get('max')} A "
              f"(median {e['dist_to_pocket_A'].get('median')}); flagged in "
              f"{e['n_flagged']}/{e['n_models_with_residue']} frames", ""]
    if cr.get("failed_criteria"):
        L += [f"- failed on: **{'; '.join(cr['failed_criteria'])}**; passed: "
              f"{', '.join(cr['passed_criteria']) or 'nothing'}", ""]

    rk, diag = d.get("control_rank", {}), d.get("criteria_diagnosis", {})
    if rk.get("status") == "OK":
        L += ["### Threshold-free reading — where the known site RANKS", "",
              "A cutoff that misses the known site is ambiguous between *the observable is uninformative* "
              "and *the observable is fine, the line is misplaced*. Rank separates them, and unlike a "
              "re-tuned cutoff it cannot be steered toward a preferred answer.", "",
              f"Pool: {rk['n_cysteines_pooled']} cysteines — {rk['pool']}. Rank 1 = most exposed.", "",
              "| observable | control value | rank | top 3 |", "|---|---|---|---|"]
        for k, v in rk["observables"].items():
            if "rank" not in v:
                L.append(f"| `{k}` | — | UNREAD | — |")
                continue
            L.append(f"| `{k}` | {v['control_value']} | **{v['rank']}/{v['of']}** | "
                     f"{'; '.join(v['top3'])} |")
        L.append("")
    if diag.get("verdict"):
        L += [f"**Diagnosis: {diag['verdict']}**", "", f"*{diag['refusal']}*", ""]

    ho = d.get("thiol_hydrogen_occlusion")
    if ho and ho.get("fraction_occluded", {}).get("n"):
        f = ho["fraction_occluded"]
        L += ["### Which SASA convention is being quoted", "", ho["note"], "",
              f"Across the pooled cysteines the residue's own thiol proton occludes "
              f"**{f['min']}–{f['max']}** of the SG surface (median **{f['median']}**).", "",
              ho["reading"], ""]

    L += ["## NR4A3 LBD cysteines and their aligned paralogue residues", "",
          "| NR4A3 | context | NR4A1 | NR4A2 | unique vs both | aligners agree |", "|---|---|---|---|---|---|"]
    for r in d["nr4a3_lbd_cysteines"]:
        L.append("| C{} | `{}` | {}{} | {}{} | {} | {} |".format(
            r["resnum"], r["context"], r["nr4a1"], r["nr4a1_resnum"] or "-",
            r["nr4a2"], r["nr4a2_resnum"] or "-",
            "**yes**" if r["unique_vs_both"] else "no", "yes" if r["alignment_robust"] else "NO"))
    L.append("")

    nmr = d["ensembles"].get("NR4A3_8xtt_nmr")
    if nmr:
        L += [f"## Spread across the experimental ensemble — {nmr['kind']}", "",
              f"{nmr['n_models_analysed']} of {nmr['n_models_found']} models analysed.", "",
              "| NR4A3 Cys | unique | RSA min–med–max | SG SASA heavy min–med–max (Å²) | SG→pocket "
              "min–med–max (Å) | reach classes seen | flagged in |",
              "|---|---|---|---|---|---|---|"]
        for u in sorted(nmr["cysteines"], key=int):
            e = nmr["cysteines"][u]
            L.append("| C{} | {} | {} – **{}** – {} | {} – **{}** – {} | {} – **{}** – {} | {} | {}/{} |".format(
                u, "**yes**" if int(u) in d["nr4a3_unique_lbd_cysteines"] else "no",
                e["rsa"].get("min"), e["rsa"].get("median"), e["rsa"].get("max"),
                e["sg_sasa_heavy_A2"].get("min"), e["sg_sasa_heavy_A2"].get("median"),
                e["sg_sasa_heavy_A2"].get("max"),
                e["dist_to_pocket_A"].get("min"), e["dist_to_pocket_A"].get("median"),
                e["dist_to_pocket_A"].get("max"),
                ", ".join(e["reach_classes"]) or "—", e["n_flagged"], e["n_models_with_residue"]))
        L += ["",
              "Spread across the ensemble is itself the result: a single conformer's number is not the "
              "answer for any of these cysteines.", ""]

    xc = d["cross_checks"]
    L += ["## Cross-checks (rule 1 — this module must not mint a second value for an existing number)", ""]
    for k, v in xc.items():
        L.append(f"- `{k}`: **{v['status']}**"
                 + (f" (max |ΔRSA| {v['max_abs_rsa_delta']}, max |Δd| {v['max_abs_dist_delta_A']} A)"
                    if "max_abs_rsa_delta" in v else "")
                 + (f" — {v.get('reason', v.get('note', ''))}" if v["status"] == "UNREAD" else ""))
    L.append("")

    if d["unread_inputs"] or d["refusals"]:
        L += ["## Refusals and unread inputs", "",
              "An input that could not be read is UNREAD, not absent. Nothing below was guessed.", ""]
        for u in d["unread_inputs"]:
            L.append(f"- **UNREAD** `{u['input']}` — {u['reason']}")
        for r in d["refusals"]:
            L.append(f"- **REFUSED** `{r.get('model', r.get('input'))}` — {r['reason']}")
        L.append("")

    cv = d.get("comparison_validity")
    if cv:
        L += ["## Which comparisons these numbers license", ""]
        L += ["**Licensed:**", ""] + [f"- {x['comparison']} — *{x['why']}*" for x in cv["licensed"]]
        L += ["", "**NOT licensed:**", ""] + [f"- {x['comparison']} — *{x['why']}*"
                                              for x in cv["not_licensed"]]
        L += ["", f"**Missing input:** {cv['absent_input']}", ""]

    L += ["## Honest limits", ""] + [f"- {x}" for x in d["_limits"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--seq-cache", default=os.path.join(HERE, "nr4a-sequences-cache.json"))
    ap.add_argument("--models-dir", default=None,
                    help="directory of split 8XTT conformer PDBs (use --fetch-8xtt to populate it in CI)")
    ap.add_argument("--fetch-8xtt", action="store_true",
                    help="download 8XTT from RCSB and split it into --models-dir (CI only; the dev "
                         "sandbox's egress proxy 403s files.rcsb.org)")
    ap.add_argument("--n-points", type=int, default=96,
                    help="Shrake-Rupley sphere points for RESIDUE SASA; 96 matches the atlas default and "
                         "the committed map, and changing it breaks the cross-check")
    ap.add_argument("--sg-n-points", type=int, default=960,
                    help="sphere points for the single-atom SG measures; at 96 the SG quantum is 1.34 A^2, "
                         "which is coarse enough to make distinct cysteines read identically")
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-covalent-handle-ensemble.json"))
    args = ap.parse_args(argv)

    with open(args.seq_cache) as fh:
        seqs = json.load(fh)
    missing = [k for k in ACCESSIONS if k not in seqs]
    if missing:
        raise SystemExit(f"sequence cache {args.seq_cache} is missing {missing} — REFUSING to guess")

    models_dir = args.models_dir
    if args.fetch_8xtt:
        models_dir = models_dir or os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "8xtt_models")
        paths = fetch_8xtt_models(models_dir)
        print(f"[8xtt] fetched + split {len(paths)} conformers into {models_dir}", flush=True)

    data = build(seqs, models_dir=models_dir, n_points=args.n_points, sg_n_points=args.sg_n_points)
    with open(args.out, "w") as fh:
        json.dump(data, fh, indent=1)
    md = os.path.splitext(args.out)[0] + ".md"
    with open(md, "w") as fh:
        fh.write(to_markdown(data))

    print(json.dumps(data["summary"], indent=1), flush=True)
    print("[control]", data["control_recovery"]["status"], "-", data["control_recovery"].get("reading", ""),
          flush=True)
    for k, v in data["cross_checks"].items():
        print(f"[xcheck] {k}: {v['status']}", flush=True)
    for u in data["unread_inputs"]:
        print(f"[UNREAD] {u['input']}: {u['reason']}", flush=True)
    for r in data["refusals"]:
        print(f"[REFUSED] {r.get('model', r.get('input'))}: {r['reason']}", flush=True)
    print(f"[out] {os.path.relpath(args.out, REPO)} + {os.path.relpath(md, REPO)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
