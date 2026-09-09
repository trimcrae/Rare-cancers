#!/usr/bin/env python3
"""SURFACE-3 step 4: independently re-derive SURFACE-2's core measurement from the
committed artifact -- 45 classified records, 0 with a non-null vital-tissue INPUT and
0 with a non-empty vital_tissue OUTPUT.  Read-only.  Writes nothing."""
import json, os, sys, hashlib

ROOT = os.path.abspath(__file__)
for _ in range(7):
    ROOT = os.path.dirname(ROOT)
P = os.path.join(ROOT, "research", "modalities", "emc-surface-normal-window.json")
raw = open(P, "rb").read()
d = json.loads(raw)
ant = d["antigens"]

rows = list(ant.items())
scored = [(k, v) for k, v in rows if "window" in v and v.get("window")]
unscored = [k for k, v in rows if k not in dict(scored)]

# the OUTPUT field the screen is supposed to populate
nonempty_vital = [k for k, v in scored if v.get("vital_tissue")]
missing_vital_key = [k for k, v in scored if "vital_tissue" not in v]
# the INPUT the screen substring-matches against
nonnull_input = [k for k, v in rows if v.get("rna_tissue_specific_nTPM") is not None]

out = {
    "artifact": "research/modalities/emc-surface-normal-window.json",
    "sha256": hashlib.sha256(raw).hexdigest(),
    "antigen_rows_total": len(rows),
    "classified_records": len(scored),
    "unclassified_records": unscored,
    "vital_tissue_key_present_on_scored": len(scored) - len(missing_vital_key),
    "records_with_nonempty_vital_tissue": len(nonempty_vital),
    "records_with_nonnull_rna_tissue_specific_nTPM": len(nonnull_input),
    "vital_tissues_screened_label_count": len(d.get("vital_tissues_flagged", {}).get("tissues", []))
        if isinstance(d.get("vital_tissues_flagged"), dict) else None,
    "vital_tissues_flagged_block": d.get("vital_tissues_flagged"),
}
out["reproduces_surface2"] = (
    out["classified_records"] == 45
    and out["records_with_nonempty_vital_tissue"] == 0
    and out["records_with_nonnull_rna_tissue_specific_nTPM"] == 0
)
json.dump(out, sys.stdout, indent=2)
print()
sys.exit(0 if out["reproduces_surface2"] else 3)
