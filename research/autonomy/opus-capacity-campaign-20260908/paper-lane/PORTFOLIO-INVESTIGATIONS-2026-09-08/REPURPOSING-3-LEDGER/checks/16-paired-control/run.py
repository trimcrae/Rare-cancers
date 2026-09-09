"""Paired control, ONE survey() shared by both arms so a concurrently-changing tree cannot confound
it. Arm A = the real ledger as committed. Arm B = the candidate ledger (outside the checkout).
Neither arm writes anything."""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research/manuscripts"))
import lint_citations as lc

prose, anchors = lc.survey()          # ONE scan, reused by both arms
real = lc.LEDGER
cand = ("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/"
        "scratchpad/citation-provenance-ledger.candidate.json")
un = lc.unanchored(prose, anchors)


def new_errors(ledger_path):
    lc.LEDGER = ledger_path
    led = lc.load_ledger()
    known = {lc._norm_stored_key(e["key"]) for e in led["entries"]}
    return [(k, i, f) for k, i, f in un if lc._key(k, i) not in known]


a = new_errors(real)
b = new_errors(cand)
tag = "REPURPOSING-3/"
a3 = [x for x in a if any(tag in f for f in x[2])]
b3 = [x for x in b if any(tag in f for f in x[2])]
print("unanchored identifiers (shared survey): %d" % len(un))
print("ARM A  real ledger      : %d new-unanchored errors, %d of them from REPURPOSING-3 prose"
      % (len(a), len(a3)))
for k, i, f in a3:
    print("        %s %s" % (k, i))
print("ARM B  candidate ledger : %d new-unanchored errors, %d of them from REPURPOSING-3 prose"
      % (len(b), len(b3)))
for k, i, f in b3:
    print("        %s %s" % (k, i))
print("DELTA A-B = %d (expected 4: the four rows this diff adds, and nothing else)"
      % (len(a) - len(b)))
print("resolved by the diff:", sorted(lc._key(k, i) for k, i, _ in a
                                      if (k, i) not in {(x[0], x[1]) for x in b}))
