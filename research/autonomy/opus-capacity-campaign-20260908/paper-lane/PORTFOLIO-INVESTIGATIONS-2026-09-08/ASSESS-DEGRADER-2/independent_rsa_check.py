#!/usr/bin/env python3
"""INDEPENDENT re-derivation of a stated SUBSET of the DEGRADER-2 per-frame RSA result.

Written from scratch for ASSESS-DEGRADER-2: own PDB parser, own Shrake-Rupley, own
Tien max-ASA table, own local->UniProt offset derivation (substring match against the
committed sequence cache, NOT nr4a_paralogue_dynamics.species_offset).

It does NOT import nr4a_differential_atlas or nr4a_paralogue_dynamics for any number it
reports.  Read-only on the conformer trees (never copied).  No GPU, no network.

usage: independent_rsa_check.py <n_points> <species:ensemble> [<species:ensemble> ...]
"""
import json, math, os, sys, statistics as st
from multiprocessing import Pool

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research", "modalities")
ROOT = {"NR4A3": os.path.join(REPO, "results", "nr4a3-pocket-reharmonize"),
        "NR4A1": os.path.join(REPO, "results", "nr4a1-pocket-ensemble"),
        "NR4A2": os.path.join(REPO, "results", "nr4a2-pocket-ensemble")}
SEQS = json.load(open(os.path.join(MOD, "nr4a-sequences-cache.json")))
COMMITTED = json.load(open(os.path.join(MOD, "nr4a-paralogue-dynamics.json")))

T2O = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G",
       "HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S",
       "THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
# Tien et al. 2013, theoretical max ASA (A^2)
TIEN = {"A":129.0,"R":274.0,"N":195.0,"D":193.0,"C":167.0,"E":223.0,"Q":225.0,"G":104.0,
        "H":224.0,"I":197.0,"L":201.0,"K":236.0,"M":224.0,"F":240.0,"P":159.0,"S":155.0,
        "T":172.0,"W":285.0,"Y":263.0,"V":174.0}
RVDW = {"C":1.70,"N":1.55,"O":1.52,"S":1.80,"H":1.20,"P":1.80}
PROBE = 1.4
NPTS = 96


def read_pdb(path):
    seq, order, at = {}, [], []
    for ln in open(path):
        if not ln.startswith("ATOM"):
            continue
        rn = ln[17:20].strip()
        if rn not in T2O:
            continue
        rid = int(ln[22:26])
        at.append((rid, ln[12:16].strip(), (ln[76:78].strip() or ln[12:16].strip()[0]).upper(),
                   float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
        if rid not in seq:
            seq[rid] = T2O[rn]; order.append(rid)
    return order, seq, at


def sphere(n):
    # golden-angle Fibonacci lattice, endpoints included (matches the documented convention)
    ga = math.pi * (3.0 - math.sqrt(5.0))
    out = []
    for i in range(n):
        y = 1.0 - 2.0 * i / (n - 1)
        r = math.sqrt(max(0.0, 1.0 - y * y))
        out.append((math.cos(ga * i) * r, y, math.sin(ga * i) * r))
    return out


def sasa(at, npts):
    sph = sphere(npts)
    rad = [RVDW.get(a[2], 1.70) + PROBE for a in at]
    n = len(at)
    cell = 2.0 * max(rad) + 0.1
    grid = {}
    for i, a in enumerate(at):
        grid.setdefault((int(a[3] // cell), int(a[4] // cell), int(a[5] // cell)), []).append(i)
    unit = 4.0 * math.pi / npts
    per = {}
    for i in range(n):
        _, _, _, xi, yi, zi = at[i]
        ri = rad[i]
        cx, cy, cz = int(xi // cell), int(yi // cell), int(zi // cell)
        cand = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in grid.get((cx + dx, cy + dy, cz + dz), ()):
                        if j == i:
                            continue
                        d2 = (xi - at[j][3])**2 + (yi - at[j][4])**2 + (zi - at[j][5])**2
                        if d2 < (ri + rad[j])**2:
                            cand.append(j)
        acc = 0
        for px, py, pz in sph:
            tx, ty, tz = xi + px * ri, yi + py * ri, zi + pz * ri
            for j in cand:
                if (tx - at[j][3])**2 + (ty - at[j][4])**2 + (tz - at[j][5])**2 < rad[j]**2:
                    break
            else:
                acc += 1
        per[at[i][0]] = per.get(at[i][0], 0.0) + acc * unit * ri * ri
    return per


def offset_of(order, seq, species):
    """local->UniProt offset, derived independently: exact substring match of the model
    sequence into the canonical UniProt sequence."""
    s = "".join(seq[r] for r in order)
    full = SEQS[species]
    k = full.find(s)
    if k < 0:
        raise RuntimeError(f"{species}: model sequence not a substring of the cached UniProt sequence")
    if full.find(s, k + 1) >= 0:
        raise RuntimeError(f"{species}: ambiguous placement")
    # UniProt number of the first modelled residue = k+1 ; its local id = order[0]
    return (k + 1) - order[0]


def one(job):
    species, ens, fname, path, npts = job
    order, seq, at = read_pdb(path)
    off = offset_of(order, seq, species)
    s = sasa(at, npts)
    has_sg = {rid for rid, name, *_ in at if name == "SG"}
    return (species, ens, fname, off,
            {f"C{rid+off}": round(s.get(rid, 0.0) / TIEN["C"], 4)
             for rid in order if seq[rid] == "C" and rid in has_sg})


def quant(xs):
    s = sorted(float(x) for x in xs); n = len(s)
    def q(f):
        if n == 1: return s[0]
        i = f * (n - 1); lo = int(math.floor(i)); hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (i - lo)
    return {"n": n, "min": round(s[0], 4), "p10": round(q(.10), 4), "median": round(q(.50), 4),
            "p90": round(q(.90), 4), "max": round(s[-1], 4), "mean": round(sum(s)/n, 4),
            "sd": round(st.pstdev(s), 4) if n > 1 else 0.0}


def main():
    npts = int(sys.argv[1])
    targets = [t.split(":") for t in sys.argv[2:]]
    jobs = []
    for sp, ens in targets:
        d = os.path.join(ROOT[sp], ens)
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name, "frame.pdb")
            if os.path.isfile(p):
                jobs.append((sp, ens, name, p, npts))
    print(f"[chk] n_points={npts} frames={len(jobs)} targets={sys.argv[2:]}", flush=True)
    with Pool(4) as pool:
        rows = pool.map(one, jobs, chunksize=2)
    offs = sorted({(r[0], r[3]) for r in rows})
    print(f"[chk] independently derived offsets: {offs}", flush=True)

    nchk = nbad = 0
    for sp, ens in targets:
        cells = [r for r in rows if r[0] == sp and r[1] == ens]
        pub = COMMITTED["term_a"]["by_species"][sp]["ensembles"][ens]["summary"]
        labs = sorted({l for r in cells for l in r[4]})
        print(f"[chk] {sp}/{ens}: {len(cells)} frames, cysteines {labs}", flush=True)
        for lab in labs:
            mine = quant([r[4][lab] for r in cells if lab in r[4]])
            th = pub.get(lab, {}).get("rsa")
            if th is None:
                print(f"  !! {lab} ABSENT from committed artifact"); nbad += 1; continue
            bad = []
            for k in ("n", "min", "p10", "median", "p90", "max", "mean", "sd"):
                nchk += 1
                if abs(float(mine[k]) - float(th[k])) > 1e-9:
                    bad.append(f"{k}: mine={mine[k]} committed={th[k]}"); nbad += 1
            print(f"  {lab}: max={mine['max']} median={mine['median']} "
                  f"{'OK all 8 stats' if not bad else 'MISMATCH ' + '; '.join(bad)}", flush=True)
        # argmax attribution
        best = max(((lab, r[4][lab], r[2]) for r in cells for lab in r[4]), key=lambda t: t[1])
        print(f"  >> ensemble max = {best[1]} at {sp} {best[0]} frame {best[2]}", flush=True)
    print(f"[chk] TOTAL {nchk} statistics compared, {nbad} mismatches", flush=True)

    # NR4A3 C397 frames at or below the published pooled ceiling 0.2126
    low = sorted((r[4]["C397"], r[1], r[2]) for r in rows if r[0] == "NR4A3" and "C397" in r[4]
                 and r[4]["C397"] <= 0.2126)
    if any(r[0] == "NR4A3" for r in rows):
        print(f"[chk] NR4A3 C397 frames <= 0.2126: {low}", flush=True)
    json.dump([{"species": r[0], "ensemble": r[1], "frame": r[2], "offset": r[3], "cys": r[4]}
               for r in rows],
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                f"artifacts/independent-rsa-n{npts}.json"), "w"), indent=1)
    return 0 if nbad == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
