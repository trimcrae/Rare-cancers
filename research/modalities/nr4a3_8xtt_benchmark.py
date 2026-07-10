#!/usr/bin/env python3
"""
Benchmark the AF2-based NR4A3 LBD model (AF-Q92570) against the experimental apo NMR ensemble PDB 8XTT.

WHY. The whole NR4A3-degrader manuscript is built on an AlphaFold2 model (AF-Q92570, UniProt Q92570, LBD
residues 373-626); its orthosteric "Pocket 5" (residues 406-534, fpocket druggability 0.495), its 10
pocket-lining residues, and its 7 paralogue-divergent selectivity handles all inherit that single model.
PDB 8XTT ("Nuclear receptor Nor1 ligand binding domain") is a NEWLY-discovered *experimental* apo NR4A3
LBD solution-NMR ensemble (~20 conformers). This job benchmarks the AF2 pocket/handles against 8XTT and
returns a plain-English verdict (agree / partial / disagree) with the numbers behind it.

WHAT (all inside an AWS SageMaker CPU job — RCSB is egress-blocked from the dev container):
  (a) download 8XTT from RCSB (the multi-MODEL NMR PDB);
  (b) split the ~20 NMR conformers;
  (c) map AF2 Pocket-5 residues (406-534) + 7 handles + 10 lining residues onto 8XTT author numbering via
      a global BLOSUM62 pairwise alignment of the 8XTT chain to Q92570 (fail loud if identity is implausibly
      low — 8XTT and Q92570 are the SAME protein, so identity must be near 1.0 over the LBD);
  (d) run fpocket on EACH conformer and report the druggability of the pocket overlapping the mapped
      Pocket-5 residue set -> a DISTRIBUTION across the 20 conformers (min/median/max/IQR, fraction >= 0.53),
      alongside the static AF2 0.495 for comparison;
  (e) superpose the AF2 LBD onto each 8XTT conformer and report global Ca-RMSD, pocket-local (Pocket-5
      residues) Ca-RMSD, and per-residue displacement of the 7 handles;
  (f) write nr4a3-8xtt-benchmark.json with all of the above + a `verdict` field.

DESIGN. ALL pure logic (numbering map, superposition/RMSD, distribution stats, verdict) lives in
importable, dependency-free functions (tests/test_8xtt_benchmark.py exercises them WITHOUT 8XTT, numpy,
biopython, or fpocket). The AWS-side I/O (download, fpocket, biopython alignment) is thin glue on top.
Reuses the calibration/enumerate conventions (INPUT_DIR/OUTPUT_DIR, fpocket_lib mapping, RCSB fetch).

CPU only (fpocket). Run via .github/workflows/gpu-8xtt-benchmark-aws.yml. Do NOT run locally against RCSB
(blocked); the pure functions are what is tested locally.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys

# --------------------------------------------------------------------------------------------------
# Constants — the AF2 quantities under test (single source of truth: nr4a3_fpocket_enumerate.py /
# nr4a3_pocketminer_sagemaker.py / the manuscript).
# --------------------------------------------------------------------------------------------------
UNIPROT = "Q92570"                         # NR4A3 / NOR-1, human canonical
LBD_FIRST, LBD_LAST = 373, 626             # ligand-binding domain window (UniProt numbering)
POCKET5_FIRST, POCKET5_LAST = 406, 534     # orthosteric "Pocket 5" residue span
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]   # 10 Pocket-5 lining residues
HANDLES = [406, 407, 410, 412, 484, 531, 534]                  # 7 selectivity-divergent handles (subset)
AF2_STATIC_DRUGGABILITY = 0.495            # the manuscript's static AF2 Pocket-5 fpocket score
DRUGGABLE_REF = 0.53                        # empirical NR-panel reference boundary (nr4a3-calibration)
PDB_ID = "8XTT"

# 8XTT and Q92570 are the SAME human protein — over the LBD the alignment MUST be near-identical. A low
# identity means we aligned the wrong chain / a corrupt download / a numbering catastrophe: FAIL LOUD.
MIN_ALIGN_IDENTITY = 0.80

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
WORK = os.environ.get("RUNNER_TEMP", "/tmp")

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_benchmark.py (no I/O, no numpy/biopython/fpocket).
# ==================================================================================================

# --- numbering map (align 8XTT author numbering <-> Q92570 UniProt numbering) ---------------------

def positions_from_blocks(blocks_a, blocks_b, resnums_a, resnums_b):
    """Map {resnum_a -> resnum_b} from paired alignment blocks.

    `blocks_a`/`blocks_b` are lists of (start, end) half-open index ranges into sequence A / B (exactly
    Biopython's `Alignment.aligned` structure). Each block pair covers an equal number of ungapped,
    mutually-aligned columns, so column k of block j maps index a0+k in A to b0+k in B. `resnums_a` /
    `resnums_b` are the author residue numbers for those sequence indices (index i -> resnums_x[i]).
    Fails loud on a malformed block pair (unequal spans)."""
    if len(blocks_a) != len(blocks_b):
        raise ValueError(f"block count mismatch: {len(blocks_a)} vs {len(blocks_b)}")
    m = {}
    for (a0, a1), (b0, b1) in zip(blocks_a, blocks_b):
        if (a1 - a0) != (b1 - b0):
            raise ValueError(f"aligned block spans differ: ({a0},{a1}) vs ({b0},{b1})")
        for off in range(a1 - a0):
            ia, ib = a0 + off, b0 + off
            if ia >= len(resnums_a) or ib >= len(resnums_b):
                raise ValueError("alignment index exceeds residue-number list length")
            m[resnums_a[ia]] = resnums_b[ib]
    return m


def identity_from_blocks(blocks_a, blocks_b, seq_a, seq_b):
    """Fraction of aligned columns whose residues are identical (aligned-column identity). 0.0 if no
    aligned columns."""
    same = total = 0
    for (a0, a1), (b0, b1) in zip(blocks_a, blocks_b):
        for off in range(min(a1 - a0, b1 - b0)):
            total += 1
            if seq_a[a0 + off] == seq_b[b0 + off]:
                same += 1
    return (same / total) if total else 0.0


def map_uniprot_to_pdb(uniprot_seq, uniprot_resnums, pdb_seq, pdb_resnums,
                       align_fn=None, min_identity=MIN_ALIGN_IDENTITY):
    """Build {uniprot_resnum -> pdb_resnum} by globally aligning the two chains.

    `align_fn(seq_a, seq_b) -> (blocks_a, blocks_b)` performs the alignment; defaults to a Biopython
    BLOSUM62 global aligner (the repo convention, see nr4a_selectivity.py). Injecting `align_fn` keeps
    this function pure/testable. Returns (mapping, identity). Raises if identity < `min_identity`
    (8XTT and Q92570 are the same protein — a low identity signals a wrong/corrupt input)."""
    if align_fn is None:
        align_fn = _biopython_align
    blocks_a, blocks_b = align_fn(uniprot_seq, pdb_seq)
    identity = identity_from_blocks(blocks_a, blocks_b, uniprot_seq, pdb_seq)
    if identity < min_identity:
        raise ValueError(
            f"alignment identity {identity:.3f} < {min_identity} between Q92570 and {PDB_ID} chain — "
            "implausibly low for the same protein; refusing to map (wrong chain / corrupt download?).")
    mapping = positions_from_blocks(blocks_a, blocks_b, uniprot_resnums, pdb_resnums)
    return mapping, identity


# --- superposition / RMSD (pure Python; no numpy) -------------------------------------------------

def centroid(coords):
    n = len(coords)
    if n == 0:
        raise ValueError("centroid of empty coordinate list")
    sx = sum(c[0] for c in coords)
    sy = sum(c[1] for c in coords)
    sz = sum(c[2] for c in coords)
    return (sx / n, sy / n, sz / n)


def _sub(coords, c):
    return [(x - c[0], y - c[1], z - c[2]) for (x, y, z) in coords]


def rmsd(a, b):
    """Plain (no-superposition) RMSD between two equal-length coordinate lists."""
    if len(a) != len(b):
        raise ValueError(f"coordinate-count mismatch: {len(a)} vs {len(b)}")
    if not a:
        raise ValueError("RMSD of empty coordinate lists")
    s = 0.0
    for (ax, ay, az), (bx, by, bz) in zip(a, b):
        s += (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2
    return math.sqrt(s / len(a))


def _jacobi_eigen(A, max_sweeps=100, tol=1e-14):
    """Eigen-decomposition of a small symmetric matrix by cyclic Jacobi rotation (pure Python).
    Returns (eigenvalues, eigenvectors) with eigenvectors as columns: vecs[i][j] = component i of
    eigenvector j. Deterministic; ample for the 4x4 quaternion key matrix."""
    n = len(A)
    a = [row[:] for row in A]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(max_sweeps):
        off = 0.0
        for p in range(n):
            for q in range(p + 1, n):
                off += a[p][q] * a[p][q]
        if off < tol:
            break
        for p in range(n):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-300:
                    continue
                theta = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for i in range(n):
                    aip, aiq = a[i][p], a[i][q]
                    a[i][p] = c * aip - s * aiq
                    a[i][q] = s * aip + c * aiq
                for i in range(n):
                    api, aqi = a[p][i], a[q][i]
                    a[p][i] = c * api - s * aqi
                    a[q][i] = s * api + c * aqi
                for i in range(n):
                    vip, viq = v[i][p], v[i][q]
                    v[i][p] = c * vip - s * viq
                    v[i][q] = s * vip + c * viq
    eigvals = [a[i][i] for i in range(n)]
    return eigvals, v


def kabsch_transform(mobile, target):
    """Optimal rigid transform (R, t) minimising RMSD of `mobile` onto `target` (equal-length, paired),
    via the quaternion method (Horn 1987). Apply with apply_transform(coords, R, t): R@x + t.
    Pure Python — no numpy."""
    if len(mobile) != len(target):
        raise ValueError(f"coordinate-count mismatch: {len(mobile)} vs {len(target)}")
    if len(mobile) < 3:
        raise ValueError("need >= 3 paired points for a stable superposition")
    pc, qc = centroid(mobile), centroid(target)
    P, Q = _sub(mobile, pc), _sub(target, qc)
    # S[i][j] = sum_k P_k[i] * Q_k[j]
    S = [[0.0] * 3 for _ in range(3)]
    for p, q in zip(P, Q):
        for i in range(3):
            for j in range(3):
                S[i][j] += p[i] * q[j]
    Sxx, Sxy, Sxz = S[0]
    Syx, Syy, Syz = S[1]
    Szx, Szy, Szz = S[2]
    K = [
        [Sxx + Syy + Szz, Syz - Szy,        Szx - Sxz,        Sxy - Syx],
        [Syz - Szy,       Sxx - Syy - Szz,  Sxy + Syx,        Szx + Sxz],
        [Szx - Sxz,       Sxy + Syx,       -Sxx + Syy - Szz,  Syz + Szy],
        [Sxy - Syx,       Szx + Sxz,        Syz + Szy,       -Sxx - Syy + Szz],
    ]
    eigvals, eigvecs = _jacobi_eigen(K)
    best = max(range(4), key=lambda i: eigvals[i])
    w, x, y, z = (eigvecs[0][best], eigvecs[1][best], eigvecs[2][best], eigvecs[3][best])
    nrm = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    w, x, y, z = w / nrm, x / nrm, y / nrm, z / nrm
    R = [
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z),     2 * (x * z + w * y)],
        [2 * (x * y + w * z),     1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y),     2 * (y * z + w * x),     1 - 2 * (x * x + y * y)],
    ]
    # t = qc - R @ pc
    rpc = (R[0][0] * pc[0] + R[0][1] * pc[1] + R[0][2] * pc[2],
           R[1][0] * pc[0] + R[1][1] * pc[1] + R[1][2] * pc[2],
           R[2][0] * pc[0] + R[2][1] * pc[1] + R[2][2] * pc[2])
    t = (qc[0] - rpc[0], qc[1] - rpc[1], qc[2] - rpc[2])
    return R, t


def apply_transform(coords, R, t):
    out = []
    for (x, y, z) in coords:
        out.append((R[0][0] * x + R[0][1] * y + R[0][2] * z + t[0],
                    R[1][0] * x + R[1][1] * y + R[1][2] * z + t[1],
                    R[2][0] * x + R[2][1] * y + R[2][2] * z + t[2]))
    return out


def superpose_and_score(mobile_by_res, target_by_res, fit_residues, pocket_residues, handle_residues):
    """Fit `mobile` onto `target` over the common `fit_residues` (Ca coords keyed by residue number),
    then report global RMSD (over the fit set), pocket-local RMSD (over pocket_residues present in the
    fit set), and per-residue handle displacements (post-fit distance, Angstrom). Pure.

    Returns {global_rmsd, n_fit, pocket_rmsd, n_pocket, handle_displacements, handle_rmsd}.
    Coordinates are (x,y,z) tuples. Residues missing from either structure are skipped."""
    common = sorted(r for r in fit_residues if r in mobile_by_res and r in target_by_res)
    if len(common) < 3:
        raise ValueError(f"only {len(common)} common residues to superpose on (need >= 3)")
    mob = [mobile_by_res[r] for r in common]
    tgt = [target_by_res[r] for r in common]
    R, t = kabsch_transform(mob, tgt)
    mob_fit = apply_transform(mob, R, t)
    global_rmsd = rmsd(mob_fit, tgt)
    fit_pos = {r: i for i, r in enumerate(common)}

    def _disp(r):
        i = fit_pos[r]
        (ax, ay, az), (bx, by, bz) = mob_fit[i], tgt[i]
        return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2)

    pres = [r for r in pocket_residues if r in fit_pos]
    if pres:
        pdisp = [_disp(r) for r in pres]
        pocket_rmsd = math.sqrt(sum(d * d for d in pdisp) / len(pdisp))
    else:
        pocket_rmsd = None
    handle_disp = {r: _disp(r) for r in handle_residues if r in fit_pos}
    handle_rmsd = (math.sqrt(sum(d * d for d in handle_disp.values()) / len(handle_disp))
                   if handle_disp else None)
    return {
        "global_rmsd": global_rmsd,
        "n_fit": len(common),
        "pocket_rmsd": pocket_rmsd,
        "n_pocket": len(pres),
        "handle_displacements": handle_disp,
        "handle_rmsd": handle_rmsd,
    }


# --- distribution statistics ----------------------------------------------------------------------

def _quantile(sorted_vals, q):
    """Linear-interpolation quantile (same convention as numpy's default 'linear')."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def distribution_stats(values, threshold=DRUGGABLE_REF):
    """min / median / max / IQR (Q1, Q3) / mean / fraction >= threshold over a list of floats.
    Returns a dict with n=0 and None fields on empty input (fail-soft — a per-conformer dropout
    shouldn't crash the panel; the caller records n)."""
    vals = sorted(float(v) for v in values if v is not None)
    n = len(vals)
    if n == 0:
        return {"n": 0, "min": None, "median": None, "max": None, "q1": None, "q3": None,
                "iqr": None, "mean": None, "frac_ge_threshold": None, "threshold": threshold}
    q1 = _quantile(vals, 0.25)
    q3 = _quantile(vals, 0.75)
    return {
        "n": n,
        "min": vals[0],
        "median": _quantile(vals, 0.5),
        "max": vals[-1],
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "mean": sum(vals) / n,
        "frac_ge_threshold": sum(1 for v in vals if v >= threshold) / n,
        "threshold": threshold,
    }


# --- verdict --------------------------------------------------------------------------------------

def verdict(pocket_dist, af2_static, global_rmsd_median, pocket_rmsd_median, handle_rmsd_median):
    """Plain-English agree / partial / disagree on whether 8XTT supports the AF2 pocket + handles.

    Criteria (transparent, reported alongside the numbers — NOT a black box):
      * pocket agreement: the experimental per-conformer druggability distribution BRACKETS the AF2
        static 0.495 (min <= af2 <= max) OR the median is within 0.15 of it -> the AF2 pocket score is
        experimentally plausible; and at least some conformers reach the druggable reference (0.53).
      * fold agreement: pocket-local Ca-RMSD median <= 2.5 A (AF2 pocket backbone matches the NMR
        ensemble) — apo NMR spread of ~1-3 A is expected.
      * handle agreement: handle Ca-RMSD median <= 3.0 A (the selectivity handles sit where AF2 places
        them, within apo flexibility).
    agree = all three; disagree = none (or fold badly broken, pocket-local RMSD > 5 A); partial =
    otherwise. Fold is weighted most (a broken backbone invalidates the pocket/handle mapping)."""
    reasons = []
    md = pocket_dist.get("median")
    mn = pocket_dist.get("min")
    mx = pocket_dist.get("max")
    frac = pocket_dist.get("frac_ge_threshold")

    pocket_ok = False
    if md is not None and mn is not None and mx is not None:
        brackets = (mn <= af2_static <= mx)
        near = abs(md - af2_static) <= 0.15
        reaches = (frac or 0) > 0.0
        pocket_ok = (brackets or near) and reaches
        reasons.append(
            f"pocket druggability: experimental median {md:.3f} (range {mn:.3f}-{mx:.3f}) vs AF2 "
            f"{af2_static:.3f}; {'brackets' if brackets else 'does not bracket'} the AF2 value, "
            f"{'close' if near else 'far'} to it, {100 * (frac or 0):.0f}% of conformers >= {DRUGGABLE_REF} "
            f"-> {'consistent' if pocket_ok else 'inconsistent'}")
    else:
        reasons.append("pocket druggability: no distribution (fpocket found no overlapping pocket)")

    fold_ok = pocket_rmsd_median is not None and pocket_rmsd_median <= 2.5
    fold_broken = pocket_rmsd_median is not None and pocket_rmsd_median > 5.0
    if pocket_rmsd_median is not None:
        reasons.append(
            f"pocket-local Ca-RMSD median {pocket_rmsd_median:.2f} A -> "
            f"{'AF2 pocket backbone matches 8XTT' if fold_ok else 'divergent backbone'}")
    else:
        reasons.append("pocket-local Ca-RMSD: unavailable")

    handle_ok = handle_rmsd_median is not None and handle_rmsd_median <= 3.0
    if handle_rmsd_median is not None:
        reasons.append(
            f"handle Ca-RMSD median {handle_rmsd_median:.2f} A -> "
            f"{'handles placed as in AF2' if handle_ok else 'handles displaced'}")
    else:
        reasons.append("handle Ca-RMSD: unavailable")

    if global_rmsd_median is not None:
        reasons.append(f"global LBD Ca-RMSD median {global_rmsd_median:.2f} A (context)")

    n_ok = sum([pocket_ok, fold_ok, handle_ok])
    if fold_broken or n_ok == 0:
        label = "disagree"
    elif pocket_ok and fold_ok and handle_ok:
        label = "agree"
    else:
        label = "partial"
    return {"verdict": label, "pocket_ok": pocket_ok, "fold_ok": fold_ok, "handle_ok": handle_ok,
            "rationale": reasons}


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — RCSB/fpocket/biopython live here).
# ==================================================================================================

def fetch_rcsb(pdb_id, dest):
    import urllib.request
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    print(f"  downloading {url}", flush=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def split_models(pdb_text):
    """Split a multi-MODEL NMR PDB into a list of single-model PDB texts (each MODEL..ENDMDL body,
    wrapped so fpocket/parsers see one structure). If there are no MODEL records, returns the whole
    ATOM/HETATM body as a single model. Pure text transform."""
    models, cur, in_model = [], [], False
    for line in pdb_text.splitlines(keepends=True):
        if line.startswith("MODEL"):
            in_model, cur = True, []
            continue
        if line.startswith("ENDMDL"):
            if cur:
                models.append("".join(cur) + "END\n")
            in_model, cur = False, []
            continue
        if in_model and line.startswith(("ATOM", "HETATM", "TER", "ANISOU")):
            cur.append(line)
    if not models:
        body = [l for l in pdb_text.splitlines(keepends=True)
                if l.startswith(("ATOM", "HETATM", "TER"))]
        if body:
            models.append("".join(body) + "END\n")
    return models


def chain_ca(model_text):
    """From one model's ATOM records, pick the chain with the most CA atoms and return
    (chain_id, resnums[list], seq[str], ca_coords[{resnum:(x,y,z)}]). Uses author residue numbers.
    Keeps the first altloc (blank or 'A')."""
    by_chain = {}
    for line in model_text.splitlines():
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        if line[16] not in (" ", "A"):
            continue
        chain = line[21]
        try:
            resseq = int(line[22:26])
            xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        except ValueError:
            continue
        aa = THREE2ONE.get(line[17:20].strip(), "X")
        by_chain.setdefault(chain, {})
        by_chain[chain].setdefault(resseq, (aa, xyz))   # first altloc wins
    if not by_chain:
        raise ValueError("no CA atoms found in model")
    chain = max(by_chain, key=lambda c: len(by_chain[c]))
    items = sorted(by_chain[chain].items())
    resnums = [r for r, _ in items]
    seq = "".join(aa for _, (aa, _) in items)
    ca = {r: xyz for r, (_, xyz) in items}
    return chain, resnums, seq, ca


def af2_lbd_ca(pdb_path):
    """CA coords of the AF2 model within the LBD window, keyed by UniProt resnum, + (resnums, seq)."""
    ca, items = {}, []
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            try:
                resseq = int(line[22:26])
            except ValueError:
                continue
            if not (LBD_FIRST <= resseq <= LBD_LAST):
                continue
            try:
                xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            except ValueError:
                continue
            aa = THREE2ONE.get(line[17:20].strip(), "X")
            ca[resseq] = xyz
            items.append((resseq, aa))
    items.sort()
    return ca, [r for r, _ in items], "".join(a for _, a in items)


def _biopython_align(seq_a, seq_b):
    """Global BLOSUM62 alignment (repo convention, nr4a_selectivity.py) -> (blocks_a, blocks_b) as
    plain Python lists of (start, end) index tuples."""
    from Bio.Align import PairwiseAligner, substitution_matrices
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    aln = aligner.align(seq_a, seq_b)[0]
    blocks_a = [(int(a0), int(a1)) for a0, a1 in aln.aligned[0]]
    blocks_b = [(int(b0), int(b1)) for b0, b1 in aln.aligned[1]]
    return blocks_a, blocks_b


def _read(path):
    with open(path) as fh:
        return fh.read()


def fpocket_pockets_with_residues(model_pdb_path):
    """Run fpocket on one model; return [{pocket, druggability, alpha_spheres, residues[list int]}] with
    the file->pocket mapping DERIVED from data (fpocket_lib), never assumed. Reuses the exact machinery
    of the calibration/enumerate scripts."""
    import fpocket_lib as fl
    subprocess.run(["fpocket", "-f", model_pdb_path], check=True, capture_output=True, text=True)
    stem = model_pdb_path[:-4] if model_pdb_path.endswith(".pdb") else model_pdb_path
    out_dir, base = stem + "_out", os.path.basename(stem)
    info = fl.parse_info(_read(os.path.join(out_dir, base + "_info.txt")))
    out_pdb = os.path.join(out_dir, base + "_out.pdb")
    out_coords = fl.out_pdb_sphere_coords(_read(out_pdb)) if os.path.exists(out_pdb) else {}
    file_res, counts, coords = {}, {}, {}
    for f in glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb")):
        fidx = int(re.search(r"pocket(\d+)_atm", f).group(1))
        file_res[fidx] = fl.parse_atm_residues(_read(f))
        vert = os.path.join(out_dir, "pockets", f"pocket{fidx}_vert.pqr")
        vtext = _read(vert) if os.path.exists(vert) else ""
        coords[fidx] = fl.pqr_sphere_coords(vtext)
        counts[fidx] = fl.count_pqr_spheres(vtext)
    mapping = fl.map_files_to_pockets(info, counts, coords, out_coords)
    pockets = []
    for fidx, num in mapping.items():
        pockets.append({
            "pocket": num,
            "druggability": info[num]["druggability"],
            "alpha_spheres": info[num]["alpha_spheres"],
            "residues": file_res[fidx],
        })
    return pockets


def pocket_overlapping_site(pockets, site_residues):
    """The pocket whose lining residues overlap `site_residues` the most (>=1 shared). Returns
    (pocket_dict, n_overlap) or (None, 0). Pure; kept beside its caller."""
    site = set(site_residues)
    best, best_n = None, 0
    for p in pockets:
        n = len(site & set(p["residues"]))
        if n > best_n:
            best, best_n = p, n
    return best, best_n


def _r(v):
    return "None" if v is None else f"{v:.2f}"


def assemble_result(n_models, identity, mapped_pocket5, mapped_handles, per_conformer,
                    drug_values, global_rmsds, pocket_rmsds, handle_rmsds, handle_disp_by_res):
    """Build the full result dict (distributions + verdict) from the accumulated per-conformer data.
    Called after EACH conformer so a Continuous ProcessingOutput ships a valid partial JSON — a
    timeout/crash leaves the last checkpoint as the deliverable (CLAUDE.md checkpoint rule)."""
    drug_dist = distribution_stats(drug_values, threshold=DRUGGABLE_REF)
    global_dist = distribution_stats(global_rmsds, threshold=0.0)
    pocket_dist = distribution_stats(pocket_rmsds, threshold=0.0)
    handle_dist = distribution_stats(handle_rmsds, threshold=0.0)
    per_handle = {str(r): distribution_stats(v, threshold=0.0) for r, v in handle_disp_by_res.items()}
    vd = verdict(drug_dist, AF2_STATIC_DRUGGABILITY,
                 global_dist.get("median"), pocket_dist.get("median"), handle_dist.get("median"))
    return {
        "_title": f"AF2 NR4A3 LBD (AF-{UNIPROT}) benchmarked against experimental apo NMR ensemble {PDB_ID}",
        "_method": {
            "pdb": PDB_ID,
            "pdb_title": "Nuclear receptor Nor1 ligand binding domain (apo, solution NMR)",
            "af2_model": f"AFDB AF-{UNIPROT}, LBD {LBD_FIRST}-{LBD_LAST} (UniProt numbering)",
            "n_conformers": n_models,
            "n_conformers_processed": len(per_conformer),
            "alignment": "global BLOSUM62 (Biopython PairwiseAligner), 8XTT chain vs Q92570 LBD",
            "alignment_identity": round(identity, 4),
            "fpocket_site": "pocket whose lining residues most overlap the mapped Pocket-5 residue set",
            "druggable_reference_boundary": DRUGGABLE_REF,
            "note": ("Per-conformer fpocket druggability of the mapped Pocket-5 site is a DISTRIBUTION "
                     "across the NMR ensemble; compare to the static AF2 0.495. RMSDs are Ca-only after "
                     "rigid superposition on the mapped LBD Ca set. Apo NMR ensembles show intrinsic "
                     "~1-3 A spread — RMSD is read against that expectation, not zero."),
        },
        "af2_static_pocket5_druggability": AF2_STATIC_DRUGGABILITY,
        "pocket5_residues_uniprot": POCKET5,
        "handles_uniprot": HANDLES,
        "mapped_pocket5_8xtt": mapped_pocket5,
        "mapped_handles_8xtt": mapped_handles,
        "per_conformer_druggability_distribution": drug_dist,
        "global_ca_rmsd_distribution": global_dist,
        "pocket_ca_rmsd_distribution": pocket_dist,
        "handle_ca_rmsd_distribution": handle_dist,
        "per_handle_displacement_distribution_uniprot": per_handle,
        "per_conformer": per_conformer,
        **vd,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    if not shutil.which("fpocket"):
        sys.exit("  ABORT: fpocket binary not on PATH")

    # 1. AF2 model — mounted at INPUT_DIR if provided, else fetched fresh from AFDB.
    af2_path = os.path.join(IN, f"AF-{UNIPROT}.pdb")
    if not os.path.exists(af2_path):
        from nr4a3_structure import fetch_pdb as fetch_afdb
        af2_path = fetch_afdb(UNIPROT, os.path.join(WORK, f"AF-{UNIPROT}.pdb"))
    af2_ca, af2_resnums, af2_seq = af2_lbd_ca(af2_path)
    if len(af2_resnums) < 3:
        sys.exit("  ABORT: AF2 LBD has too few CA atoms — wrong/empty model?")
    print(f"  AF2 LBD: {len(af2_resnums)} CA ({af2_resnums[0]}-{af2_resnums[-1]})", flush=True)

    # 2. 8XTT — download + split conformers.
    xtt_path = fetch_rcsb(PDB_ID, os.path.join(WORK, f"{PDB_ID}.pdb"))
    models = split_models(_read(xtt_path))
    print(f"  {PDB_ID}: {len(models)} NMR conformers", flush=True)
    if not models:
        sys.exit(f"  ABORT: no models parsed from {PDB_ID}")

    # 3. Numbering map from conformer 1 (all conformers share the chain sequence/numbering).
    _, xtt_resnums0, xtt_seq0, _ = chain_ca(models[0])
    mapping, identity = map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq0, xtt_resnums0)
    inv = dict(mapping)                                 # uniprot resnum -> 8XTT author resnum
    print(f"  alignment identity {identity:.3f}; mapped {len(mapping)} residues", flush=True)
    mapped_pocket5 = sorted({inv[r] for r in POCKET5 if r in inv})
    mapped_handles = sorted({inv[r] for r in HANDLES if r in inv})
    mapped_pocket_span = sorted({inv[r] for r in range(POCKET5_FIRST, POCKET5_LAST + 1) if r in inv})

    # 4. Per-conformer fpocket (mapped-site druggability) + superposition.
    per_conformer, drug_values = [], []
    global_rmsds, pocket_rmsds, handle_rmsds = [], [], []
    handle_disp_by_res = {r: [] for r in HANDLES}
    work = os.path.join(OUT, "fpocket_runs")
    os.makedirs(work, exist_ok=True)
    out_json = os.path.join(OUT, "nr4a3-8xtt-benchmark.json")
    for i, model_text in enumerate(models, 1):
        rec = {"model": i}
        try:
            _, _, _, ca_i = chain_ca(model_text)
            mp = os.path.join(work, f"{PDB_ID}_model{i}.pdb")
            with open(mp, "w") as fh:
                fh.write(model_text)
            pockets = fpocket_pockets_with_residues(mp)
            site, nov = pocket_overlapping_site(pockets, mapped_pocket5)
            if site is not None:
                rec["site_druggability"] = site["druggability"]
                rec["site_pocket"] = site["pocket"]
                rec["site_overlap_residues"] = nov
                if site["druggability"] is not None:
                    drug_values.append(site["druggability"])
            else:
                rec["site_druggability"] = None
            rec["max_druggability"] = max((p["druggability"] or 0.0) for p in pockets) if pockets else None
            # superpose AF2 -> this conformer over mapped LBD Ca present in both
            common_u = [u for u in af2_resnums if u in inv and inv[u] in ca_i]
            mobile = {inv[u]: af2_ca[u] for u in common_u}
            target = {inv[u]: ca_i[inv[u]] for u in common_u}
            sc = superpose_and_score(mobile, target, fit_residues=sorted(target),
                                     pocket_residues=mapped_pocket_span,
                                     handle_residues=mapped_handles)
            rec["global_ca_rmsd"] = sc["global_rmsd"]
            rec["pocket_ca_rmsd"] = sc["pocket_rmsd"]
            rec["handle_ca_rmsd"] = sc["handle_rmsd"]
            # record handle displacements back under UniProt numbering
            xtt_to_uni = {inv[u]: u for u in HANDLES if u in inv}
            rec["handle_displacements_uniprot"] = {
                str(xtt_to_uni[k]): round(v, 3) for k, v in sc["handle_displacements"].items()
                if k in xtt_to_uni}
            for k, v in sc["handle_displacements"].items():
                if k in xtt_to_uni:
                    handle_disp_by_res[xtt_to_uni[k]].append(v)
            global_rmsds.append(sc["global_rmsd"])
            if sc["pocket_rmsd"] is not None:
                pocket_rmsds.append(sc["pocket_rmsd"])
            if sc["handle_rmsd"] is not None:
                handle_rmsds.append(sc["handle_rmsd"])
            print(f"    model {i:>2}: site_drug={rec.get('site_druggability')} "
                  f"pocketRMSD={_r(sc['pocket_rmsd'])} handleRMSD={_r(sc['handle_rmsd'])}", flush=True)
        except Exception as e:  # noqa: BLE001 — record, keep the ensemble alive
            rec["error"] = str(e)[:300]
            print(f"    model {i:>2}: ERROR {e}", file=sys.stderr, flush=True)
        per_conformer.append(rec)
        # 5. Checkpoint the full result after EACH conformer (Continuous S3 upload ships partials).
        result = assemble_result(len(models), identity, mapped_pocket5, mapped_handles, per_conformer,
                                 drug_values, global_rmsds, pocket_rmsds, handle_rmsds, handle_disp_by_res)
        with open(out_json, "w") as fh:
            json.dump(result, fh, indent=2)

    print(f"\n  wrote {out_json}", flush=True)
    print(f"  VERDICT: {result['verdict']}", flush=True)
    for r in result["rationale"]:
        print(f"    - {r}", flush=True)


if __name__ == "__main__":
    main()
