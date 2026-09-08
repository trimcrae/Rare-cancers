#!/usr/bin/env python3
"""R3, second check: is the ONE window that could have been informative actually empty?

An NR4A3 probe can report on what precedes NR4A3 only if it crosses the NR4A3 exon-2/exon-3
seam (cDNA 697|698) -- present in the wild-type mRNA, replaced by the partner in the chimera.
For a 50-mer that means start in [648, 697]. This script asks how many committed sequences
occupy that window, how much of NR4A3 the committed table covers at all, and what the atlas
grades each acceptor exon start.
Offline, stdlib.
"""
import json, os
ROOT="/home/user/Rare-cancers"; MOD=os.path.join(ROOT,"research/modalities")
COMP=str.maketrans("ACGTN","TGCAN")
rc=lambda s: s.translate(COMP)[::-1]
ci=json.load(open(os.path.join(MOD,"emc-construct-inputs.json")))
at=json.load(open(os.path.join(MOD,"nr4a3-fusion-junction-atlas.json")))
nr=ci["genes"]["NR4A3"]; cdna=nr["cdna"].upper(); K=50
allseq=set()
with open(os.path.join(MOD,"emc-fourth-cohort-probe-counts.tsv")) as f:
    f.readline()
    for line in f: allseq.add(line.split("\t",1)[0])
print("committed distinct sequences:", len(allseq))

covered=set()
for i in range(len(cdna)-K+1):
    w=cdna[i:i+K]
    if w in allseq or rc(w) in allseq:
        covered.update(range(i+1,i+K+1))
print(f"NR4A3 cDNA nt covered by any committed 50-mer: {len(covered)} of {len(cdna)} "
      f"({100*len(covered)/len(cdna):.3f}%)")
cds_lo=nr["utr5_len"]+1; cds_hi=nr["utr5_len"]+len(nr["cds"])
print(f"NR4A3 CDS nt covered: {len([x for x in covered if cds_lo<=x<=cds_hi])} of {len(nr['cds'])}")

bounds=[]; cum=0
for ex in nr["exons"]:
    cum+=ex["exon_length_nt"]; bounds.append(cum)
internal=bounds[:-1]
print("\ninternal NR4A3 exon-exon seams (1-based cDNA end of the upstream exon):", internal)
for b in internal:
    lo,hi=max(1,b-K+2), b            # 50-mer starts that cross seam b
    n=0
    for i in range(lo-1, hi):
        w=cdna[i:i+K]
        if len(w)<K: break
        if w in allseq or rc(w) in allseq: n+=1
    print(f"  seam at {b:>5d}: 50-mer start positions {lo}..{hi} -> committed sequences crossing it: {n}")

print("\nacceptor exon starts the atlas enumerates, with grades:")
from collections import Counter
c=Counter((gp["acceptor_exon_start"], gp["grade"]) for gp in at["graded_pairs"])
for k in sorted(c): print(f"  acceptor e{k[0]:d}  {k[1]:24s} {c[k]:>4d}")
print("\ngrade_counts (committed):", json.dumps(at["grade_counts"]))
print("n_junctions_with_a_fusion_specific_design (committed):",
      at["n_junctions_with_a_fusion_specific_design"], " (this is an ASO design count, not a probe count)")
print("DONE")
