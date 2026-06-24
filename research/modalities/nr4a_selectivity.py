#!/usr/bin/env python3
"""
Selectivity scaffold for the NR4A3 degrader warhead (de-novo design prep).

WHY. A warhead must bind NR4A3 but NOT the homologous NR4A1/NR4A2 LBDs — the family is highly
conserved, yet selectivity is achievable (an existing NR4A1 PROTAC does not cross-degrade NR4A3).
The actionable design question is: *which residues lining the NR4A3 LBD pocket DIFFER from NR4A1/2?*
Those divergent positions are where a selective warhead gets its margin.

WHAT. Reuses the working AFDB + fpocket machinery (nr4a3_structure.py) to:
  1. fetch AlphaFold LBD models for NR4A1 (P22736), NR4A2 (P43354), NR4A3 (Q92570);
  2. run fpocket on each and report the top-pocket druggability;
  3. enumerate the NR4A3 top-pocket lining residues;
  4. align NR4A3 to NR4A1 and NR4A2 (Biopython, BLOSUM62) and, for each NR4A3 pocket residue, report
     the paralogue residue and whether it is conserved or DIVERGENT (the selectivity handles).

A reusable design input (independent of the MD; the generative step later targets the MD-revealed
pocket conformer). CI: fpocket (micromamba) + biopython (pip). Output: nr4a-selectivity.json
"""
import json
import os
import sys

import nr4a3_structure as ns  # reuse fetch_pdb / run_fpocket / _pocket_residues (same dir)

OUT = os.path.join(os.path.dirname(__file__), "nr4a-selectivity.json")
PARALOGUES = {"NR4A1": "P22736", "NR4A2": "P43354", "NR4A3": "Q92570"}

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


def seq_items(pdb):
    """Ordered [(resnum, one-letter-aa)] from a PDB's CA records."""
    d = {}
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            d[int(line[22:26])] = THREE2ONE.get(line[17:20].strip(), "X")
    return sorted(d.items())


def index_map(aligner, seq_a, seq_b):
    """Map index-in-seq_a -> index-in-seq_b via a global alignment (or None where gapped)."""
    aln = aligner.align(seq_a, seq_b)[0]
    m = {}
    for (a0, a1), (b0, b1) in zip(aln.aligned[0], aln.aligned[1]):
        for off in range(a1 - a0):
            m[a0 + off] = b0 + off
    return m


def main():
    try:
        from Bio.Align import PairwiseAligner, substitution_matrices
    except ImportError:
        json.dump({"_status": "biopython missing (pip install biopython)"}, open(OUT, "w"), indent=2)
        print("biopython missing", file=sys.stderr)
        return

    work = os.environ.get("RUNNER_TEMP", "/tmp")
    pdbs, pockets, seqs = {}, {}, {}
    result = {"_note": "NR4A1/2/3 LBD pocket characterisation + NR4A3-vs-paralogue divergent "
                       "pocket residues = selectivity handles for the degrader warhead. AFDB "
                       "models + fpocket; alignment BLOSUM62. Design prep, not validated.",
              "paralogues": {}}

    for name, acc in PARALOGUES.items():
        try:
            pdb = ns.fetch_pdb(acc, os.path.join(work, f"AF-{acc}.pdb"))
            pdbs[name] = pdb
            seqs[name] = seq_items(pdb)
            fp = ns.run_fpocket(pdb, {"LBD": (1, 99999)})
            top = (fp.get("pockets") or [{}])[0]
            pockets[name] = fp
            result["paralogues"][name] = {
                "uniprot": acc,
                "n_pockets": fp.get("n_pockets"),
                "top_pocket_druggability": top.get("druggability"),
                "top_pocket_resid_span": (fp.get("top_pocket_locale") or {}).get(
                    "resid_min"),
            }
        except Exception as e:  # noqa
            result["paralogues"][name] = {"uniprot": acc, "error": str(e)}
            print(f"  {name} {acc}: {e}", file=sys.stderr)

    # NR4A3 top-pocket lining residues
    if "NR4A3" in pdbs and pockets.get("NR4A3", {}).get("pockets"):
        stem = pdbs["NR4A3"][:-4]
        topnum = pockets["NR4A3"]["pockets"][0]["pocket"].split()[-1]
        nr4a3_pocket = ns._pocket_residues(stem, topnum)
    else:
        nr4a3_pocket = []
    result["nr4a3_top_pocket_residues"] = nr4a3_pocket

    # align NR4A3 to NR4A1/NR4A2 and classify each pocket residue
    if nr4a3_pocket and "NR4A1" in seqs and "NR4A2" in seqs:
        aligner = PairwiseAligner()
        aligner.mode = "global"
        aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
        aligner.open_gap_score = -10
        aligner.extend_gap_score = -0.5

        s3 = "".join(a for _, a in seqs["NR4A3"])
        s1 = "".join(a for _, a in seqs["NR4A1"])
        s2 = "".join(a for _, a in seqs["NR4A2"])
        resnum3 = [r for r, _ in seqs["NR4A3"]]
        idx_of_resnum3 = {r: i for i, r in enumerate(resnum3)}
        m31 = index_map(aligner, s3, s1)
        m32 = index_map(aligner, s3, s2)

        rows, n_div = [], 0
        for r in nr4a3_pocket:
            i = idx_of_resnum3.get(r)
            if i is None:
                continue
            aa3 = s3[i]
            aa1 = s1[m31[i]] if i in m31 else "-"
            aa2 = s2[m32[i]] if i in m32 else "-"
            divergent = (aa3 != aa1) or (aa3 != aa2)
            n_div += divergent
            rows.append({"nr4a3": f"{aa3}{r}", "nr4a1": aa1, "nr4a2": aa2, "divergent": divergent})
        result["pocket_residue_selectivity"] = rows
        result["n_pocket_residues"] = len(rows)
        result["n_divergent_selectivity_handles"] = n_div
        result["selectivity_handles"] = [x["nr4a3"] for x in rows if x["divergent"]]

    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: result.get(k) for k in
                      ("n_pocket_residues", "n_divergent_selectivity_handles", "selectivity_handles")},
                     indent=2))


if __name__ == "__main__":
    main()
