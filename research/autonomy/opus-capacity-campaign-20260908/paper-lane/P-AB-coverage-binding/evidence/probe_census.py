"""Read-only probe: which witnesses credit each covered sentence of a document."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "research", "manuscripts"))
import claim_coverage as cc

key = sys.argv[1] if len(sys.argv) > 1 else "research/manuscripts/endpoint/response-endpoint-indolent-tumours.md"
rows = cc.census(key)
cov = [r for r in rows if r["covered"]]
out = {
    "paper": key,
    "sentences": len(rows),
    "covered": len(cov),
    "with_a_number": sum(1 for r in rows if r["has_number"]),
    "with_a_number_covered": sum(1 for r in rows if r["has_number"] and r["covered"]),
    "covered_rows": [{"sentence": r["sentence"][:220], "has_number": r["has_number"],
                      "read_by": r["read_by"]} for r in cov],
}
print(json.dumps(out, indent=1))
