#!/usr/bin/env python3
"""READ-ONLY: what the committed C1 rule buys. Writes nothing to the artifact; prints only.

Shows which windows the committed threshold ("enriched" only) holds in place versus a LITERAL
reading of the field name immune_or_circulating ("any reported immune-cell expression"). This is
a statement about the RULE, not a recommendation to change any candidate's standing.
"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."]*6))
d = json.load(open(os.path.join(ROOT, "research/modalities/emc-surface-normal-window.json")))
ant = d["antigens"]
moved = []
for g, v in ant.items():
    if v.get("_status"):
        continue
    b = (v.get("rna_blood_cell_specificity") or "").lower()
    literal = bool(b) and "not detected in immune cells" not in b and "low immune cell" not in b
    if literal and not v["immune_or_circulating"]:
        moved.append((g, v["window"], "VITAL_OR_IMMUNE_LIABILITY", v["rna_blood_cell_specificity"]))
print("rows whose window would move under a LITERAL reading of the flag name:")
for g, was, now, src in moved:
    print(f"  {g:9s} {was:26s} -> {now}   (source: {src})")
ctrl = d["self_validation"]
print("\ncontrols in that set:",
      [g for g, *_ in moved if g in ("DLL3", "GPC3", "B2M", "CD3E")])
print("committed self_validation positive controls:", ctrl["positive_controls_restricted"])
print("\nrestricted_window_candidates that would leave the list:",
      [g for g, *_ in moved if g in d["restricted_window_candidates"]])
print("\n=> The committed threshold is the one that keeps DLL3 and GPC3 RESTRICTED, i.e. it is")
print("   calibrated so the file's own positive controls pass. ALCAM's blood-cell annotation sits")
print("   in the SAME band as those two controls. Nothing here changes any candidate's standing.")
