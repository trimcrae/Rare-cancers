"""Read-only dry run: provenance_check() against the CANDIDATE ledger. The real ledger is untouched."""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research/manuscripts"))
import lint_citations as lc
cand = ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
        "PORTFOLIO-INVESTIGATIONS-2026-09-08/REPURPOSING-3-LEDGER/"
        "citation-provenance-ledger.candidate.json")
lc.LEDGER = os.path.abspath(cand)
rc = lc.provenance_check()
print("provenance_check rc =", rc)
sys.exit(rc)
