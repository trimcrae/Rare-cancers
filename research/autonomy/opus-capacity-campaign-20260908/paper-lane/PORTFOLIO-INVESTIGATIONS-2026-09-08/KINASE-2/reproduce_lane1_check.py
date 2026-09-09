#!/usr/bin/env python3
"""Does this lane's gene-resampling column reproduce lane PUB-KINASE-LEADS exactly?

Both nulls in this lane must sit on the same numbers lane PUB-KINASE-LEADS published, or
the side-by-side comparison is meaningless. This compares, field by field, this lane's
recomputed gene-resampling values against that lane's committed artifact.
Exit 1 if anything disagrees beyond the precision the earlier artifact was written at.
Reads only; prints; writes nothing.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(os.path.dirname(HERE), "PUB-KINASE-LEADS",
                   "two-platform-concordance-null.json")
NEW = os.path.join(HERE, "label-permutation-vs-gene-resampling-null.json")
o, n = json.load(open(OLD)), json.load(open(NEW))
bad = 0
oj, nj = o["joint_null"], n["frames"]["primary"]["gene_resampling_null"]
for label, a, b in (("n genes in frame", oj["n_genes_in_both_background_draws"],
                     n["frames"]["primary"]["n_genes_scored_on_both_platforms"]),
                    ("n concordant", oj["n_concordant_in_direction"], nj["n_concordant"]),
                    ("concordance rate", oj["frac_concordant_in_direction"], nj["concordance_rate"])):
    ok = a == b
    bad += not ok
    print("%-18s lane1=%-8s this lane=%-8s %s" % (label, a, b, "OK" if ok else "MISMATCH"))
for g, rec in o["leads"].items():
    j = rec.get("joint")
    m = n["leads"].get(g, {}).get("placement_primary_frame")
    if j is None or m is None:
        print("%-7s both record no joint placement: %s" % (g, (j is None) == (m is None)))
        bad += (j is None) != (m is None)
        continue
    a = j["joint_empirical_p_two_sided"]; b = m["joint_p_gene_resampling"]
    ok = abs(a - b) < 1e-9
    bad += not ok
    print("%-7s lane1 joint p=%-9s this lane=%-9s %s   (label-permutation p=%s)"
          % (g, a, b, "OK" if ok else "MISMATCH", m["joint_p_label_permutation"]))
print("mismatches:", bad)
sys.exit(1 if bad else 0)
