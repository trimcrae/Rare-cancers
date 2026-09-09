"""Read-only dry run of the provenance axis against the CANDIDATE ledger, which lives OUTSIDE the
checkout so it cannot anchor anything (see checks/10 and checks/11 for why that matters).
The real ledger on disk is not modified by this script."""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research/manuscripts"))
import lint_citations as lc
lc.LEDGER = ("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/"
             "scratchpad/citation-provenance-ledger.candidate.json")
rc = lc.provenance_check()
print("provenance_check rc =", rc)
