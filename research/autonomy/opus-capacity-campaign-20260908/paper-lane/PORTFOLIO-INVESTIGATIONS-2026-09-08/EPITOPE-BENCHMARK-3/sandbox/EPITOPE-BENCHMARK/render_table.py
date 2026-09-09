#!/usr/bin/env python3
"""Render VALIDATED-EPITOPE-TABLE.md from epitope-records.json. One row per record."""
import json, re
R = json.load(open("epitope-records.json"))
rows = R["records"]
C = json.load(open("validated-epitope-counts.json"))
elig = set(C["strata"]["BENCHMARK_ELIGIBLE"]["ids"])

def grade(r):
    e = r["evidence"]
    if e == ["PREDICTION"]: return "PREDICTION ONLY"
    if set(e) <= {"BINDING","PREDICTION"}: return "BINDING ONLY"
    g = []
    if "MS_ELUTION" in e: g.append("MS elution")
    if "MULTIMER" in e:   g.append("multimer")
    if "TCELL" in e:      g.append("T-cell")
    return " + ".join(g)

def esc(s): return (s or "").replace("|", "\\|").replace("\n", " ")

hdr = ("| ID | Fusion | Junction peptide | Len | HLA restriction | **Spans the junction?** "
       "| Evidence grade | Assay / material | Source (PMID · DOI) |")
sep = "|---|---|---|---|---|---|---|---|---|"

lines = [hdr, sep]
for r in rows:
    star = " **✓elig**" if r["id"] in elig else ""
    src  = "PMID %s" % r["pmid"]
    if r.get("doi"): src += " · [DOI](https://doi.org/%s)" % r["doi"].split(";")[0].strip()
    lines.append("| %s%s | %s | `%s` | %s | %s | **%s** — %s | %s | %s | %s |" % (
        r["id"], star, esc(r["fusion"]), esc(r["peptide"]), r["len"] or "—",
        esc(r["hla"]), r["spans_junction"].upper(), esc(r["junction_note"]),
        grade(r), esc(r["assay"]) + " · *" + esc(r["material"]) + "*", src))
open("_table_body.md","w").write("\n".join(lines) + "\n")
print("rows rendered:", len(rows))
