#!/usr/bin/env python3
"""Offline source/hash/unit verification; no outcome computation or network."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

B = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
checks = []
def check(label, condition):
    checks.append({"check": label, "pass": bool(condition)})
    assert condition, label

before = {n: sha(B/n) for n in ["PEG10-SAFE-METHOD-AND-IDENTITY.json", "IGF2BP3-SAFE-SOURCE-LINEAGE.json"]}
subprocess.run([sys.executable, str(B/"project_safe_sources.py")], check=True, capture_output=True, text=True)
for n, digest in before.items():
    check("exact replay " + n, sha(B/n) == digest)
access = json.loads((B/"SOURCE-ACCESS.json").read_text())
check("four authorized calls only", len(access) == 4)
for r in access:
    raw = B/r["raw_path"]
    check("raw hash " + r["name"], sha(raw) == r["sha256"])
    check("accepted source " + r["name"], r["accepted"] and r["status"] == 200)
port = json.loads((B/"PORTABILITY.json").read_text())
check("raw total", port["retained_new_raw_bytes"] == sum(r["bytes"] for r in access) == 481729)
check("raw budget", port["retained_new_raw_bytes"] < 64*1024**2)
peg = json.loads((B/"PEG10-SAFE-METHOD-AND-IDENTITY.json").read_text())
check("25 tumor specimens", sum(x["specimens"] for x in peg["specimen_groups"][:3]) == peg["tumor_specimens"] == 25)
check("18 generic CHS specimens", sum(x["specimens"] for x in peg["specimen_groups"][1:3]) == peg["generic_CHS_specimens"] == 18)
check("normal sample not extra donor", peg["specimen_groups"][3]["specimens"] == 1 and "not a new independent donor" in peg["specimen_groups"][3]["status"])
check("ten distinct model labels", len(set(peg["all_reported_line_labels"])) == 10)
cards = json.loads((B/"SOURCE-CONDITION-DISPOSITIONS.json").read_text())
check("nine assigned unique sources", len(cards["own_sources"]) == cards["own_unique_source_count"] == 9)
check("no inferred native zeros", all(c["native_EMC_conditions"] is None for c in cards["own_sources"]))
for c in cards["own_sources"]:
    check("resolving evidence " + c["source"], (B/c["evidence"]).is_file())
car = json.loads((B/"CAR-VERIFIED-REUSE.json").read_text())
for r in car["bindings"]:
    check("CAR reused exact " + Path(r["path"]).name, sha(Path(r["path"])) == r["sha256"])
adc = json.loads((B/"ADC2025-VERIFIED-REUSE.json").read_text())
check("ADC evaluated card hash", sha(Path(adc["source_path"])) == adc["source_sha256"])
check("ADC original hash", sha(Path(adc["source_raw"])) == adc["source_raw_sha256"])
check("ADC selected roster", sum(adc["ADC2025_reused"]["selected_histotype_counts"].values()) == 1664)
check("CAR no accepted body", car["accepted_primary_body"] is False)
check("conferences retain all three wrappers", len(json.loads((B/"CONFERENCE-SOURCE-SCHEMA.json").read_text())) == 3)
check("no new biological finding", json.loads((B/"DECISION.json").read_text())["new_measurement_or_finding"] is False)
check("no new outcomes", json.loads((B/"EXPOSURE-AND-LIMITS.json").read_text())["new_gene_or_protein_outcome_values"] == 0)
check("pending blocks promotion", cards["suitable_accessible_pending_blocks_promotion"] is True)
for p in B.glob("*.json"):
    json.loads(p.read_text())
check("all JSON parses", True)
out = {"checks": checks, "count": len(checks), "failures": 0, "scope": "Offline exact source/units/reuse checks only; no gene quantities, recomputation or network."}
(B/"VALIDATION.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"checks": len(checks), "failures": 0}))
