#!/usr/bin/env python3
"""
NR4A1/2/3 paralogue-differential SURFACE atlas (RUNG-4 free CPU step; STRATEGY.md orientation-first ladder).

WHY. The orientation-first prospective ladder needs a MAP of where NR4A3 could plausibly support a
paralogue-selective ternary neo-interface BEFORE any linker is designed. Precedent (BRD4-vs-BRD2/3, CDK4-vs-6,
VAV1) says degrader selectivity is created on the E3-facing PPI SURFACE + differential lysine geometry — NOT the
conserved warhead pocket. So this atlas asks, per residue: is it (a) solvent-EXPOSED (reachable by a recruited
E3), (b) DIVERGENT between NR4A3 and NR4A1/NR4A2, and (c) chemically NON-conservative / character-changing? The
intersection is the differential surface — the set of candidate "selectivity wedges" the orientation-basin search
(RUNG 5a) then tries to steer an E3 against. It also maps accessible lysines (the ubiquitination-geometry axis).

This is the RUNG-4 cheap early NO-GO named in STRATEGY.md: if there is NO exposed, divergent, E3-reachable surface
handle, the wedge search is unlikely to succeed and we say so before spending on the orientation search.

WHAT. Pure-stdlib (no numpy/biopython/freesasa needed — works in the dev sandbox at $0):
  * per-atom Shrake-Rupley SASA (Fibonacci sphere + spatial-grid neighbor search) -> per-residue relative SASA;
  * Needleman-Wunsch global alignment (BLOSUM62) of NR4A3 vs NR4A1 and vs NR4A2;
  * residue chemical-character classification + character-change type on divergent positions;
  * the differential-surface set (exposed x divergent x non-conservative) + a lysine-accessibility map.

INPUTS. Matched, state-matched opened-LBD models already cached in the repo (identical construction per paralogue
-> a fair, matched comparison, per the atlas's "matched ensemble" requirement):
  results/nr4a3-matrix/nr4a{3,1,2}-opened.pdb   (local residue numbering 1..~254; NR4A3 LBD == UniProt 373-626).

HONEST LIMITS (written into the output). Single static opened conformer per paralogue (NOT an MD ensemble — the
optional matched NR4A1/2 MD ensembles are the ~$10-40 Vast-3090 add-on); LBD-only (hinge/DBD/fusion lysines are
NOT in these models -> flagged, need a full-length/EWSR1::NR4A3 model); RSA is a solvent-exposure proxy for
"E3-reachable", NOT a docked-interface calc (that is the orientation-basin search). Design prep, not validated.
"""
from __future__ import annotations

import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
# van der Waals radii (A); probe 1.4 A (water).
VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "H": 1.20, "P": 1.80}
PROBE = 1.4
# Tien et al. 2013 theoretical max ASA (A^2) for RSA normalisation.
MAXASA = {"A": 129.0, "R": 274.0, "N": 195.0, "D": 193.0, "C": 167.0, "E": 223.0, "Q": 225.0,
          "G": 104.0, "H": 224.0, "I": 197.0, "L": 201.0, "K": 236.0, "M": 224.0, "F": 240.0,
          "P": 159.0, "S": 155.0, "T": 172.0, "W": 285.0, "Y": 263.0, "V": 174.0}
EXPOSED_RSA = 0.25   # standard relative-SASA cutoff for "exposed"
BACKBONE = {"N", "CA", "C", "O", "OXT"}

# Chemical character classes (for character-change typing on divergent positions).
POS = set("KRH"); NEG = set("DE"); AROM = set("FWY"); HYDRO = set("AVLIMFWPCG")
HBOND = set("NQSTYHWKRDE")  # side chains that can donate/accept an H-bond

# Compact BLOSUM62 (upper-tri expanded); score < 0 == non-conservative substitution.
_B62_ORDER = "ARNDCQEGHILKMFPSTWYV"
_B62_ROWS = [
    "4 -1 -2 -2 0 -1 -1 0 -2 -1 -1 -1 -1 -2 -1 1 0 -3 -2 0",
    "-1 5 0 -2 -3 1 0 -2 0 -3 -2 2 -1 -3 -2 -1 -1 -3 -2 -3",
    "-2 0 6 1 -3 0 0 0 1 -3 -3 0 -2 -3 -2 1 0 -4 -2 -3",
    "-2 -2 1 6 -3 0 2 -1 -1 -3 -4 -1 -3 -3 -1 0 -1 -4 -3 -3",
    "0 -3 -3 -3 9 -3 -4 -3 -3 -1 -1 -3 -1 -2 -3 -1 -1 -2 -2 -1",
    "-1 1 0 0 -3 5 2 -2 0 -3 -2 1 0 -3 -1 0 -1 -2 -1 -2",
    "-1 0 0 2 -4 2 5 -2 0 -3 -3 1 -2 -3 -1 0 -1 -3 -2 -2",
    "0 -2 0 -1 -3 -2 -2 6 -2 -4 -4 -2 -3 -3 -2 0 -2 -2 -3 -3",
    "-2 0 1 -1 -3 0 0 -2 8 -3 -3 -1 -2 -1 -2 -1 -2 -2 2 -3",
    "-1 -3 -3 -3 -1 -3 -3 -4 -3 4 2 -3 1 0 -3 -2 -1 -3 -1 3",
    "-1 -2 -3 -4 -1 -2 -3 -4 -3 2 4 -2 2 0 -3 -2 -1 -2 -1 1",
    "-1 2 0 -1 -3 1 1 -2 -1 -3 -2 5 -1 -3 -1 0 -1 -3 -2 -2",
    "-1 -1 -2 -3 -1 0 -2 -3 -2 1 2 -1 5 0 -2 -1 -1 -1 -1 1",
    "-2 -3 -3 -3 -2 -3 -3 -3 -1 0 0 -3 0 6 -4 -2 -2 1 3 -1",
    "-1 -2 -2 -1 -3 -1 -1 -2 -2 -3 -3 -1 -2 -4 7 -1 -1 -4 -3 -2",
    "1 -1 1 0 -1 0 0 0 -1 -2 -2 0 -1 -2 -1 4 1 -3 -2 -2",
    "0 -1 0 -1 -1 -1 -1 -2 -2 -1 -1 -1 -1 -2 -1 1 5 -2 -2 0",
    "-3 -3 -4 -4 -2 -2 -3 -2 -2 -3 -2 -3 -1 1 -4 -3 -2 11 2 -3",
    "-2 -2 -2 -3 -2 -1 -2 -3 2 -1 -1 -2 -1 3 -3 -2 -2 2 7 -1",
    "0 -3 -3 -3 -1 -2 -2 -3 -3 3 1 -2 1 -1 -2 -2 0 -3 -1 4",
]
BLOSUM62 = {}
for _i, _a in enumerate(_B62_ORDER):
    _vals = _B62_ROWS[_i].split()
    for _j, _b in enumerate(_B62_ORDER):
        BLOSUM62[(_a, _b)] = int(_vals[_j])


def blosum(a: str, b: str) -> int:
    return BLOSUM62.get((a, b), BLOSUM62.get((b, a), -4))


# ---------- PDB parsing ----------
def parse_pdb(path: str):
    """Return (residues, atoms). residues: ordered list of (resid, one_letter). atoms: list of
    dict(resid,resname,name,elem,x,y,z)."""
    residues = {}
    order = []
    atoms = []
    with open(path) as fh:
        for ln in fh:
            if not ln.startswith("ATOM"):
                continue
            name = ln[12:16].strip()
            resn = ln[17:20].strip()
            if resn not in THREE2ONE:
                continue
            rid = int(ln[22:26])
            x, y, z = float(ln[30:38]), float(ln[38:46]), float(ln[46:54])
            elem = (ln[76:78].strip() or name[0]).upper()
            atoms.append({"resid": rid, "resname": resn, "name": name, "elem": elem, "x": x, "y": y, "z": z})
            if rid not in residues:
                residues[rid] = THREE2ONE[resn]
                order.append(rid)
    return [(r, residues[r]) for r in order], atoms


# ---------- Shrake-Rupley SASA (pure stdlib) ----------
def _fib_sphere(n: int):
    pts = []
    ga = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        y = 1.0 - (i / float(n - 1)) * 2.0
        r = math.sqrt(max(0.0, 1.0 - y * y))
        t = ga * i
        pts.append((math.cos(t) * r, y, math.sin(t) * r))
    return pts


def shrake_rupley(atoms, n_points: int = 96):
    """Per-residue total SASA (A^2). Spatial-grid neighbour search keeps it fast in pure Python."""
    sphere = _fib_sphere(n_points)
    rad = [VDW.get(a["elem"], 1.70) + PROBE for a in atoms]
    xs = [a["x"] for a in atoms]; ys = [a["y"] for a in atoms]; zs = [a["z"] for a in atoms]
    maxr = max(rad)
    cell = maxr * 2.0 + 0.1
    grid = {}
    for i in range(len(atoms)):
        key = (int(xs[i] // cell), int(ys[i] // cell), int(zs[i] // cell))
        grid.setdefault(key, []).append(i)

    def neighbours(i):
        cx, cy, cz = int(xs[i] // cell), int(ys[i] // cell), int(zs[i] // cell)
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    out.extend(grid.get((cx + dx, cy + dy, cz + dz), []))
        return out

    per_res = {}
    unit = 4.0 * math.pi / n_points
    for i in range(len(atoms)):
        ri = rad[i]
        nb = [j for j in neighbours(i) if j != i]
        # prefilter neighbours whose spheres can possibly overlap i's
        cand = []
        for j in nb:
            d2 = (xs[i]-xs[j])**2 + (ys[i]-ys[j])**2 + (zs[i]-zs[j])**2
            if d2 < (ri + rad[j])**2:
                cand.append(j)
        acc = 0
        for (px, py, pz) in sphere:
            tx, ty, tz = xs[i] + px*ri, ys[i] + py*ri, zs[i] + pz*ri
            buried = False
            for j in cand:
                if (tx-xs[j])**2 + (ty-ys[j])**2 + (tz-zs[j])**2 < rad[j]*rad[j]:
                    buried = True
                    break
            if not buried:
                acc += 1
        area = acc * unit * ri * ri
        per_res[atoms[i]["resid"]] = per_res.get(atoms[i]["resid"], 0.0) + area
    return per_res


def residue_rsa(residues, sasa):
    """relative SASA per residue = total residue SASA / Tien max ASA."""
    out = {}
    for rid, aa in residues:
        m = MAXASA.get(aa)
        out[rid] = (sasa.get(rid, 0.0) / m) if m else None
    return out


# ---------- Needleman-Wunsch, AFFINE gaps (Gotoh; BLOSUM62) ----------
_NEG = -10**9  # integer -inf (all scores are ints, so traceback uses exact ==)


def nw_align(seq_a: str, seq_b: str, go: int = -11, ge: int = -1):
    """Global alignment with affine gaps (open=go, extend=ge) — standard EMBOSS/Biopython defaults; places
    indels far better than a linear penalty in low-identity stretches. Returns [(i_a|None, i_b|None), ...]."""
    n, m = len(seq_a), len(seq_b)
    M = [[_NEG]*(m+1) for _ in range(n+1)]   # ends in a residue-residue match
    X = [[_NEG]*(m+1) for _ in range(n+1)]   # ends in a gap in seq_b (consume seq_a)
    Y = [[_NEG]*(m+1) for _ in range(n+1)]   # ends in a gap in seq_a (consume seq_b)
    M[0][0] = 0
    for i in range(1, n+1):
        X[i][0] = go + (i-1)*ge
    for j in range(1, m+1):
        Y[0][j] = go + (j-1)*ge
    for i in range(1, n+1):
        ai = seq_a[i-1]
        for j in range(1, m+1):
            s = blosum(ai, seq_b[j-1])
            M[i][j] = s + max(M[i-1][j-1], X[i-1][j-1], Y[i-1][j-1])
            X[i][j] = max(M[i-1][j] + go, X[i-1][j] + ge)
            Y[i][j] = max(M[i][j-1] + go, Y[i][j-1] + ge)
    i, j = n, m
    state = max((M[n][m], "M"), (X[n][m], "X"), (Y[n][m], "Y"))[1]
    aln = []
    while i > 0 or j > 0:
        if state == "M":
            aln.append((i-1, j-1))
            prev = M[i][j] - blosum(seq_a[i-1], seq_b[j-1])
            i -= 1; j -= 1
            state = "M" if prev == M[i][j] else ("X" if prev == X[i][j] else "Y")
        elif state == "X":
            aln.append((i-1, None))
            state = "M" if X[i][j] == M[i-1][j] + go else "X"
            i -= 1
        else:
            aln.append((None, j-1))
            state = "M" if Y[i][j] == M[i][j-1] + go else "Y"
            j -= 1
    aln.reverse()
    return aln


def char_of(aa: str):
    tags = []
    if aa in POS: tags.append("pos")
    if aa in NEG: tags.append("neg")
    if aa in AROM: tags.append("aromatic")
    if aa in HBOND: tags.append("hbond")
    if aa in HYDRO and aa not in POS and aa not in NEG: tags.append("hydrophobic")
    return tags


def char_change(a: str, b: str) -> str:
    ca, cb = set(char_of(a)), set(char_of(b))
    if ("pos" in ca or "neg" in ca) and not ("pos" in cb or "neg" in cb):
        return "charge_lost"
    if not ("pos" in ca or "neg" in ca) and ("pos" in cb or "neg" in cb):
        return "charge_gained"
    if ("pos" in ca and "neg" in cb) or ("neg" in ca and "pos" in cb):
        return "charge_reversed"
    if "hbond" in ca and "hbond" not in cb:
        return "hbond_lost"
    if "hbond" not in ca and "hbond" in cb:
        return "hbond_gained"
    if "aromatic" in (ca ^ cb):
        return "aromatic_change"
    return "steric_or_neutral"


def build(struct_dir: str):
    paths = {p: os.path.join(struct_dir, f"nr4a{n}-opened.pdb")
             for p, n in (("NR4A3", 3), ("NR4A1", 1), ("NR4A2", 2))}
    data = {}
    for name, path in paths.items():
        residues, atoms = parse_pdb(path)
        sasa = shrake_rupley(atoms)
        rsa = residue_rsa(residues, sasa)
        data[name] = {"residues": residues, "rsa": rsa,
                      "seq": "".join(aa for _, aa in residues),
                      "ids": [r for r, _ in residues]}
    ref = data["NR4A3"]
    aln1 = dict((ia, ib) for ia, ib in nw_align(ref["seq"], data["NR4A1"]["seq"]) if ia is not None)
    aln2 = dict((ia, ib) for ia, ib in nw_align(ref["seq"], data["NR4A2"]["seq"]) if ia is not None)

    rows = []
    for idx, (rid, aa3) in enumerate(ref["residues"]):
        j1, j2 = aln1.get(idx), aln2.get(idx)
        aa1 = data["NR4A1"]["seq"][j1] if j1 is not None else "-"
        aa2 = data["NR4A2"]["seq"][j2] if j2 is not None else "-"
        rsa3 = ref["rsa"][rid]
        div1 = aa1 != "-" and aa1 != aa3
        div2 = aa2 != "-" and aa2 != aa3
        noncons = ((div1 and blosum(aa3, aa1) < 0) or (div2 and blosum(aa3, aa2) < 0))
        rows.append({
            "local_resid": rid,
            "uniprot_resid": 372 + rid,   # NR4A3 LBD local 1 == UniProt 373
            "nr4a3": aa3, "nr4a1": aa1, "nr4a2": aa2,
            "rsa": round(rsa3, 3) if rsa3 is not None else None,
            "exposed": (rsa3 is not None and rsa3 >= EXPOSED_RSA),
            "divergent_vs_nr4a1": div1, "divergent_vs_nr4a2": div2,
            "divergent_vs_both": div1 and div2,
            "nonconservative": noncons,
            "char_change_vs_nr4a1": char_change(aa3, aa1) if div1 else None,
            "char_change_vs_nr4a2": char_change(aa3, aa2) if div2 else None,
        })
    return data, rows


def summarize(data, rows):
    n = len(rows)
    exposed = [r for r in rows if r["exposed"]]
    div_any = [r for r in rows if r["divergent_vs_nr4a1"] or r["divergent_vs_nr4a2"]]
    # THE differential surface: exposed AND divergent AND (non-conservative OR a character change)
    def handle(r):
        return (r["exposed"] and (r["divergent_vs_nr4a1"] or r["divergent_vs_nr4a2"])
                and (r["nonconservative"]
                     or (r["char_change_vs_nr4a1"] not in (None, "steric_or_neutral"))
                     or (r["char_change_vs_nr4a2"] not in (None, "steric_or_neutral"))))
    surf = [r for r in rows if handle(r)]
    surf_both = [r for r in surf if r["divergent_vs_both"]]

    # lysine accessibility map (ubiquitination axis) — NR4A3 lysines in THIS (LBD-only) model
    lys = [{"local_resid": r["local_resid"], "uniprot_resid": r["uniprot_resid"],
            "rsa": r["rsa"], "exposed": r["exposed"],
            "divergent_position": r["divergent_vs_nr4a1"] or r["divergent_vs_nr4a2"]}
           for r in rows if r["nr4a3"] == "K"]
    lys_exposed = [k for k in lys if k["exposed"]]

    gate_pass = len(surf) >= 1
    return {
        "counts": {
            "n_residues_aligned": n,
            "n_exposed": len(exposed),
            "n_divergent_any": len(div_any),
            "pct_divergent_any": round(100.0*len(div_any)/n, 1),
            "n_differential_surface_handles": len(surf),
            "n_differential_surface_vs_both": len(surf_both),
            "n_lysines_LBD": len(lys),
            "n_lysines_LBD_exposed": len(lys_exposed),
        },
        "differential_surface_handles": sorted(
            surf, key=lambda r: (-(r["rsa"] or 0), r["local_resid"]))[:60],
        "lysine_map_LBD": lys,
        "gate": {
            "question": "Is there >=1 EXPOSED, DIVERGENT, character-changing surface handle reachable by a "
                        "recruited E3 (distinct from the buried warhead pocket)?",
            "pass": gate_pass,
            "verdict": ("GO — a differential surface exists to steer an E3 against; proceed to the orientation-"
                        "basin search (RUNG 5a)." if gate_pass else
                        "NO-GO — no exposed divergent surface handle; a ternary selectivity wedge is unlikely. "
                        "Do NOT run the orientation search; report the honest negative."),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--struct-dir", default=os.path.join(REPO, "results", "nr4a3-matrix"),
                    help="dir with matched nr4a{3,1,2}-opened.pdb")
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-differential-surface-atlas.json"))
    args = ap.parse_args(argv)

    data, rows = build(args.struct_dir)
    summary = summarize(data, rows)
    out = {
        "_title": "NR4A1/2/3 paralogue-differential SURFACE atlas (orientation-first RUNG-4, $0 CPU)",
        "_method": "Shrake-Rupley SASA (96-pt, probe 1.4 A, Tien-2013 RSA norm, cutoff RSA>=0.25) + "
                   "Needleman-Wunsch BLOSUM62 alignment of NR4A3 vs NR4A1/NR4A2; residue character-change typing.",
        "_inputs": os.path.relpath(args.struct_dir, REPO) + "/nr4a{3,1,2}-opened.pdb (matched state-matched "
                   "opened-LBD models; local numbering 1.., NR4A3 LBD == UniProt 373-626)",
        "_limits": ["single static opened conformer per paralogue (NOT an MD ensemble — the matched NR4A1/2 MD "
                    "ensembles are the optional ~$10-40 Vast-3090 add-on)",
                    "LBD-only: hinge/DBD/fusion-partner lysines are NOT in these models -> require a full-length / "
                    "EWSR1::NR4A3 model (flagged; do not claim LBD lysines are the only degradable sites)",
                    "RSA is a solvent-exposure proxy for 'E3-reachable', NOT a docked-interface calc (that is the "
                    "RUNG-5a orientation-basin search)",
                    "design prep, not validated; conditional on the opened-state models chosen"],
        "summary": summary,
        "residues": rows,
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)

    c = summary["counts"]
    print(f"[atlas] residues aligned: {c['n_residues_aligned']}  exposed: {c['n_exposed']}  "
          f"divergent(any): {c['n_divergent_any']} ({c['pct_divergent_any']}%)")
    print(f"[atlas] DIFFERENTIAL SURFACE handles (exposed x divergent x character-changing): "
          f"{c['n_differential_surface_handles']}  (vs BOTH paralogues: {c['n_differential_surface_vs_both']})")
    print(f"[atlas] LBD lysines: {c['n_lysines_LBD']}  (exposed: {c['n_lysines_LBD_exposed']})")
    print(f"[atlas] GATE: {'PASS/GO' if summary['gate']['pass'] else 'NO-GO'} — {summary['gate']['verdict']}")
    top = summary["differential_surface_handles"][:12]
    print("[atlas] top surface handles (NR4A3 -> NR4A1/NR4A2, RSA):")
    for r in top:
        print(f"        U{r['uniprot_resid']} {r['nr4a3']}->({r['nr4a1']}/{r['nr4a2']}) "
              f"RSA={r['rsa']}  vsBoth={r['divergent_vs_both']}  "
              f"chg1={r['char_change_vs_nr4a1']} chg2={r['char_change_vs_nr4a2']}")
    print(f"[atlas] wrote {os.path.relpath(args.out, REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
