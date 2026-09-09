"""Measure the self-anchoring effect of a ledger COPY sitting in the tree, real ledger unchanged."""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research/manuscripts"))
import lint_citations as lc
rc = lc.provenance_check()
print("provenance_check rc =", rc, "(REAL ledger; candidate .json copy present in the tree)")
