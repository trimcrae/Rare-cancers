#!/usr/bin/env python3
"""Freeze the exact, auditable gene sets for the two pre-registered contrasts.

PRE-REGISTRATION ARTIFACT. Membership only. NO expression value is read, no contrast is
computed, no outcome is produced. The sets are fixed here so that they cannot be chosen
after any expression value is seen.

Sole input: outputs/common-platform-membership.tsv from the coordinator-frozen packet
research/autonomy/nr4a3-program-source-2026-09-07 (memberships frozen before any outcome;
mapping specification hashed before mapping began). Read in place, never copied.

Contrast A set (NR4A3-vs-other-fusion):
    EWSR1-NR4A3 program MINUS the union of all 28 non-NR4A3 fusion programs.
Contrast B set (EWSR1-partner-specific):
    Contrast A set MINUS the union of the other three NR4A3 fusion programs
    (TAF15-NR4A3, TCF12-NR4A3, TFG-NR4A3).
Both at each of the source packet's three pre-declared windows: 1 kb (sensitivity),
2 kb (primary), 5 kb (sensitivity).
"""
import csv, collections, hashlib, json, sys

SRC = sys.argv[1]
INDEX = "EWSR1-NR4A3"
NR4A3 = ["EWSR1-NR4A3", "TAF15-NR4A3", "TCF12-NR4A3", "TFG-NR4A3"]
FLOOR_GENES = 4          # PUB-FUSION-OUTPUT Sec 2.3 set-score floor
FLOOR_COVERAGE = 0.4     # PUB-FUSION-OUTPUT Sec 2.3 coverage floor

h = hashlib.sha256()
with open(SRC, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        h.update(chunk)

mem = collections.defaultdict(lambda: collections.defaultdict(set))
gene_id = {}
with open(SRC) as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        mem[int(r["window_bp"])][r["program"]].add(r["symbol"])
        gene_id.setdefault(r["symbol"], r["gene_id"])

out = {
    "artifact": "pre-registered gene sets for the two NR4A3-program contrasts",
    "status": "FROZEN BEFORE ANY EXPRESSION VALUE IS READ",
    "input": {"path": SRC, "sha256": h.hexdigest()},
    "index_program": INDEX,
    "nr4a3_family": NR4A3,
    "floors_from_manuscript": {"min_readable_genes": FLOOR_GENES, "min_coverage": FLOOR_COVERAGE},
    "windows": {},
}
for w in sorted(mem):
    P = mem[w]
    progs = sorted(P)
    alt = [p for p in progs if p not in NR4A3]
    union_alt = set().union(*(P[p] for p in alt))
    union_other = set().union(*(P[p] for p in NR4A3 if p != INDEX and p in P))
    idx = P.get(INDEX, set())
    A = idx - union_alt
    B = A - union_other
    def ann(gs):
        return {g: {"gene_id": gene_id[g],
                    "programs_containing": sorted(p for p in progs if g in P[p])}
                for g in sorted(gs)}
    out["windows"][str(w)] = {
        "n_programs": len(progs),
        "n_alternative_programs_subtracted": len(alt),
        "index_size": len(idx),
        "contrast_A_set": {
            "definition": "EWSR1-NR4A3 minus union of all %d non-NR4A3 fusion programs" % len(alt),
            "n": len(A), "clears_gene_floor": len(A) >= FLOOR_GENES,
            "genes": sorted(A), "gene_detail": ann(A)},
        "contrast_B_set": {
            "definition": "contrast A set minus union of TAF15/TCF12/TFG-NR4A3 programs",
            "n": len(B), "clears_gene_floor": len(B) >= FLOOR_GENES,
            "max_tolerable_probe_dropout_before_floor_breach": len(B) - FLOOR_GENES,
            "genes": sorted(B), "gene_detail": ann(B)},
        "subtracted_alternative_programs": alt,
    }
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
