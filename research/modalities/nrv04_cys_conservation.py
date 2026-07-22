#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — Leg 0: is the celastrol-reactive cysteine (NR4A1 Cys551) conserved in
NR4A2 / NR4A3?

Decisive, $0 confound check (prereg §3 leg 0). Celastrol binds NR4A1 covalently at Cys551. If the aligned
position in NR4A2/NR4A3 is NOT a cysteine, celastrol simply cannot form the adduct there — so NR-V04's
NR4A1-selective degradation would be (at least partly) a WARHEAD-REACTIVITY effect, which the noncovalent
free-energy machinery used for cmpd19 cannot represent. That directly informs the panel's GO/NO-GO framing.

Pure stdlib (urllib fetch of UniProt FASTA + a Needleman-Wunsch global align). The dev sandbox's egress proxy
403s UniProt, so this is meant to run on a GitHub Actions runner (open internet). The aligner is unit-testable
offline; only the fetch needs the network.

UniProt: NR4A1 = P22736 (NUR77, 598 aa), NR4A2 = P43354 (NURR1), NR4A3 = Q92570 (NOR-1).
Output: nrv04-cys-conservation.json
"""
import json
import sys
import urllib.request

ACCESSIONS = {"NR4A1": "P22736", "NR4A2": "P43354", "NR4A3": "Q92570"}
NR4A1_COV_RESNUM = 551          # celastrol-reactive cysteine (1-based, UniProt numbering)

# BLOSUM-lite: identity + a small positive for conservative pairs is unnecessary here — the NR4A LBDs are
# ~60-65% identical, so simple match/mismatch/gap Needleman-Wunsch places the cysteine unambiguously.
MATCH, MISMATCH, GAP = 2, -1, -2


def needleman_wunsch(a: str, b: str):
    """Global alignment of a,b. Returns (aln_a, aln_b) with '-' gaps. Pure stdlib, O(len_a*len_b)."""
    n, m = len(a), len(b)
    # score + traceback matrices
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        f[i][0] = i * GAP
    for j in range(1, m + 1):
        f[0][j] = j * GAP
    for i in range(1, n + 1):
        ai = a[i - 1]
        fi, fim1 = f[i], f[i - 1]
        for j in range(1, m + 1):
            diag = fim1[j - 1] + (MATCH if ai == b[j - 1] else MISMATCH)
            fi[j] = max(diag, fim1[j] + GAP, fi[j - 1] + GAP)
    # traceback
    ra, rb = [], []
    i, j = n, m
    while i > 0 and j > 0:
        cur = f[i][j]
        if cur == f[i - 1][j - 1] + (MATCH if a[i - 1] == b[j - 1] else MISMATCH):
            ra.append(a[i - 1]); rb.append(b[j - 1]); i -= 1; j -= 1
        elif cur == f[i - 1][j] + GAP:
            ra.append(a[i - 1]); rb.append("-"); i -= 1
        else:
            ra.append("-"); rb.append(b[j - 1]); j -= 1
    while i > 0:
        ra.append(a[i - 1]); rb.append("-"); i -= 1
    while j > 0:
        ra.append("-"); rb.append(b[j - 1]); j -= 1
    return "".join(reversed(ra)), "".join(reversed(rb))


def aligned_residue(aln_ref: str, aln_other: str, ref_resnum: int):
    """Given a ref/other alignment (ref = NR4A1, 1-based residue numbering) return the other-sequence residue
    (and its 1-based index in `other`, or None if it aligns to a gap) opposite ref position `ref_resnum`."""
    ref_i = 0          # 1-based residue counter in ref
    other_i = 0
    for cr, co in zip(aln_ref, aln_other):
        if cr != "-":
            ref_i += 1
        if co != "-":
            other_i += 1
        if ref_i == ref_resnum and cr != "-":
            return (co, (other_i if co != "-" else None))
    raise ValueError(f"ref position {ref_resnum} not found (ref len in alignment < {ref_resnum})")


def _context(seq: str, idx1: int, flank: int = 5) -> str:
    """A +/- flank window around 1-based index idx1 (uppercase the center)."""
    if idx1 is None:
        return ""
    i = idx1 - 1
    lo, hi = max(0, i - flank), min(len(seq), i + flank + 1)
    return seq[lo:i] + "[" + seq[i] + "]" + seq[i + 1:hi]


def fetch_fasta(acc: str) -> str:
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    with urllib.request.urlopen(url, timeout=60) as r:
        lines = r.read().decode().splitlines()
    return "".join(l.strip() for l in lines if not l.startswith(">"))


def main():
    seqs = {name: fetch_fasta(acc) for name, acc in ACCESSIONS.items()}
    ref = seqs["NR4A1"]
    if len(ref) < NR4A1_COV_RESNUM:
        raise SystemExit(f"NR4A1 length {len(ref)} < {NR4A1_COV_RESNUM}")
    ref_res = ref[NR4A1_COV_RESNUM - 1]
    print(f"[nr4a1] residue {NR4A1_COV_RESNUM} = {ref_res}  context {_context(ref, NR4A1_COV_RESNUM)}", flush=True)

    out = {
        "leg": "cys_conservation",
        "source": "UniProt FASTA (rest.uniprot.org)",
        "accessions": ACCESSIONS,
        "nr4a1_cov_resnum": NR4A1_COV_RESNUM,
        "nr4a1_residue": ref_res,
        "nr4a1_is_cysteine": ref_res == "C",
        "aligned": {},
    }
    conserved = {}
    for name in ("NR4A2", "NR4A3"):
        aln_ref, aln_oth = needleman_wunsch(ref, seqs[name])
        res, idx = aligned_residue(aln_ref, aln_oth, NR4A1_COV_RESNUM)
        is_cys = res == "C"
        conserved[name] = is_cys
        out["aligned"][name] = {
            "residue": res, "resnum": idx, "is_cysteine": is_cys,
            "context": _context(seqs[name], idx) if idx else "(aligned to a gap)",
        }
        print(f"[{name}] aligned residue = {res} (pos {idx}) cysteine={is_cys}", flush=True)

    # Frozen interpretation (prereg §3 leg 0 / §5 criterion 4)
    if not out["nr4a1_is_cysteine"]:
        verdict = ("ANOMALY: NR4A1 residue %d is %s, not Cys — the assumed covalent site is wrong; "
                   "re-derive the celastrol-reactive cysteine before proceeding." % (NR4A1_COV_RESNUM, ref_res))
    elif not any(conserved.values()):
        verdict = ("Reactive Cys is UNIQUE to NR4A1 (absent in NR4A2 and NR4A3). Celastrol cannot form the "
                   "adduct on the paralogues → NR-V04 selectivity is, at least in part, a WARHEAD-REACTIVITY "
                   "effect the noncovalent machinery cannot see. The panel MUST disentangle covalent engagement "
                   "from ternary cooperativity, and the write-up must state this confound explicitly.")
    elif all(conserved.values()):
        verdict = ("Reactive Cys is CONSERVED in NR4A2 and NR4A3 → covalency alone does NOT explain the "
                   "paralogue selectivity; ternary cooperativity is a live driver. Run the optional paralogue "
                   "covalent legs (cov_nr4a2/cov_nr4a3).")
    else:
        present = [n for n, c in conserved.items() if c]
        verdict = ("Reactive Cys is PARTIALLY conserved (present in %s). Mixed picture — model covalent "
                   "engagement explicitly for the Cys-bearing paralogue(s)." % ", ".join(present))
    out["verdict"] = verdict
    print("[verdict]", verdict, flush=True)

    with open("nrv04-cys-conservation.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote nrv04-cys-conservation.json", flush=True)


if __name__ == "__main__":
    sys.exit(main())
