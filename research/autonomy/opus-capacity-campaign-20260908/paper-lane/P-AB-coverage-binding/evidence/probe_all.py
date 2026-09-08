"""Read-only: live census counts for every censused document (no --write)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research", "manuscripts"))
import claim_coverage as cc
out = {}
for key in sorted(cc.PAPERS):
    rows = cc.census(key)
    out[key] = {
        "sentences": len(rows),
        "covered": sum(1 for r in rows if r["covered"]),
        "with_a_number": sum(1 for r in rows if r["has_number"]),
        "with_a_number_covered": sum(1 for r in rows if r["has_number"] and r["covered"]),
        "witnesses": sorted({w for r in rows for w in r["read_by"]}),
    }
print(json.dumps(out, indent=1))
