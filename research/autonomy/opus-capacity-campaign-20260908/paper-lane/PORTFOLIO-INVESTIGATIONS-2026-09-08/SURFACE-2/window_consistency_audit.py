#!/usr/bin/env python3
"""SURFACE-2 — derived-flag vs source-annotation consistency audit.

READ-ONLY. Emits one TSV row per candidate. Changes no value, flag, window or classification.

Vocabulary, held firmly apart:
  DATA      — the serialized value does not follow from the producer's own rule applied to the
              source text beside it (a transcription or staleness slip). Remedy: re-derive.
  PRODUCER  — the serialized value DOES follow from the rule, and the rule mis-summarises its
              own input (the field asserts more, or other, than its source supports).
              Remedy: change the rule or rename/qualify the field. Re-running fixes nothing.
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
WIN = os.path.join(ROOT, "research/modalities/emc-surface-normal-window.json")
LIM = os.path.join(ROOT, "research/modalities/surfaceome-instrument-limits.json")

d = json.load(open(WIN))
ant = d["antigens"]
rows = []

def add(cand, derived_f, derived_v, source_f, source_v, cls, changes_window, verdict, note):
    rows.append(dict(candidate=cand, derived_field=derived_f, derived_value=json.dumps(derived_v),
                     source_field=source_f, source_value=json.dumps(source_v), hit_class=cls,
                     changes_window_classification=changes_window, error_kind=verdict, note=note))

hits = {g: [] for g in ant}
for g, v in ant.items():
    if v.get("_status"):
        add(g, "(none scored)", None, "_status", v["_status"], "-", "no", "CLEAN",
            "record discarded on symbol mismatch; no derived flag exists to contradict anything")
        continue
    bspec = v.get("rna_blood_cell_specificity")
    # C1 — immune_or_circulating vs the blood-cell annotation it summarises
    if bspec and "immune cell" in bspec.lower() and "not detected" not in bspec.lower() \
       and "low immune" not in bspec.lower() and v.get("immune_or_circulating") is False:
        cw = "YES" if v.get("window") == "RESTRICTED" else "no (already a liability row)"
        add(g, "immune_or_circulating", v["immune_or_circulating"], "rna_blood_cell_specificity",
            bspec, "C1", cw, "PRODUCER",
            "rule is `'enriched' in blood_spec.lower()`; 'Immune cell enhanced' is real immune-cell "
            "expression and the flag named immune_or_circulating reports its absence")
        hits[g].append("C1")
    # C2 — vital_tissue derived from an input that is null on every row
    if v.get("vital_tissue") == [] and v.get("rna_tissue_specific_nTPM") is None:
        add(g, "vital_tissue", v["vital_tissue"], "rna_tissue_specific_nTPM",
            v.get("rna_tissue_specific_nTPM"), "C2", "no (branch never fires)", "PRODUCER",
            "vital_hits is substring-matched against the JSON of rna_tissue_specific_nTPM, which is "
            "null here; [] is an absent reading rendered as a negative finding")
        hits[g].append("C2")
    # C3 — RESTRICTED (glossed 'confined to one/few tissues') vs a broad distribution
    if v.get("window") == "RESTRICTED" and (v.get("rna_tissue_distribution") or "") == "Detected in many":
        add(g, "window", v["window"], "rna_tissue_distribution", v.get("rna_tissue_distribution"),
            "C3", "no (label unchanged; its gloss is unsupported)", "PRODUCER",
            "_note glosses RESTRICTED as 'confined to one/few tissues'; the distribution field beside "
            "it says the transcript is detected in many. classify() never reads distribution on this branch")
        hits[g].append("C3")
    # C4 — window contradicts the mapping the file's own _note publishes
    spec = (v.get("rna_tissue_specificity") or "")
    note_map = None
    sl = spec.lower()
    if "enriched" in sl: note_map = "RESTRICTED"
    elif "enhanced" in sl: note_map = "ENHANCED_BROAD"
    elif "low tissue specificity" in sl: note_map = "BROAD_LIABILITY"
    if note_map and v.get("window") not in (note_map, "VITAL_OR_IMMUNE_LIABILITY"):
        add(g, "window", v["window"], "rna_tissue_specificity", spec, "C4",
            "YES vs the specificity field alone; no vs the pair of source fields", "PRODUCER",
            "TWO source criteria collide on this row: rna_tissue_specificity meets a "
            + note_map + " criterion and rna_tissue_distribution ("
            + str(v.get("rna_tissue_distribution")) + ") meets the BROAD_LIABILITY one. The _note "
            "names both criteria and states NO precedence; classify() silently resolves it "
            "distribution-first. Stated narrowly: the legend under-determines the row, it is not a "
            "flat contradiction")
        hits[g].append("C4")
    # C5 — plasma_membrane_confirmed false on a null subcellular_location
    if v.get("plasma_membrane_confirmed") is False and v.get("subcellular_location") is None:
        add(g, "plasma_membrane_confirmed", False, "subcellular_location", None, "C5",
            "no (does not feed classify())", "PRODUCER",
            "bool(None and ...) -> False; 'confirmed: false' is an unperformed check rendered as a "
            "negative result, the same shape as C2")
        hits[g].append("C5")
    if not hits[g]:
        add(g, "window/immune_or_circulating/vital_tissue/plasma_membrane_confirmed",
            v.get("window"), "rna_tissue_specificity + rna_tissue_distribution + "
            "rna_blood_cell_specificity", [spec, v.get("rna_tissue_distribution"), bspec],
            "-", "no", "CLEAN", "every derived flag follows from and is supported by the text beside it")

# C6 — cross-artifact membership flag
lim = json.load(open(LIM))
l4 = lim["limits"]["L4_cspg4_coverage_gap"]
live = "CSPG4" in json.dumps(d)
if l4.get("in_emc_surface_normal_window") != live:
    add("CSPG4 (surfaceome-instrument-limits.json)", "limits.L4_cspg4_coverage_gap."
        "in_emc_surface_normal_window", l4.get("in_emc_surface_normal_window"),
        "emc-surface-normal-window.json antigens.CSPG4.window",
        ant["CSPG4"]["window"], "C6", "no (CSPG4's own window is unaffected)", "DATA",
        "producer computes `'CSPG4' in json.dumps(normal_window)` live; against the committed "
        "normal-window file that is True. The committed false predates the run that added CSPG4 "
        "(see _drift_vs_previous_artifact.newly_added_this_run). Re-running the unchanged producer fixes it")

out = os.path.join(os.path.dirname(__file__), "WINDOW-CONSISTENCY-AUDIT.tsv")
cols = ["candidate", "derived_field", "derived_value", "source_field", "source_value",
        "hit_class", "changes_window_classification", "error_kind", "note"]
with open(out, "w") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in rows:
        fh.write("\t".join(str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")

from collections import Counter
print("rows_emitted", len(rows))
print("candidates_in_file", len(ant))
print("by_class", dict(Counter(r["hit_class"] for r in rows)))
print("by_kind", dict(Counter(r["error_kind"] for r in rows)))
print("clean_candidates", sorted(g for g in ant if not hits.get(g) and not ant[g].get("_status")))
print("C1_rows", sorted(g for g in hits if "C1" in hits[g]))
print("C3_rows", sorted(g for g in hits if "C3" in hits[g]))
print("C4_rows", sorted(g for g in hits if "C4" in hits[g]))
print("C5_rows", sorted(g for g in hits if "C5" in hits[g]))
print("C2_rows_n", sum(1 for g in hits if "C2" in hits[g]))
print("wrote", out)

# ---- per-candidate roll-up (one row per candidate, as the lane contract requires) --------------
SEV = {"C1": 4, "C3": 3, "C4": 3, "C2": 2, "C5": 1}
per = {}
for r in rows:
    per.setdefault(r["candidate"], []).append(r)
roll = os.path.join(os.path.dirname(__file__), "WINDOW-CONSISTENCY-AUDIT.tsv")
det = os.path.join(os.path.dirname(__file__), "HITS-DETAIL.tsv")
os.replace(roll, det)
rcols = ["candidate", "window_as_committed", "verdict", "hit_classes", "n_hits",
         "worst_hit_derived_field", "worst_hit_derived_value", "worst_hit_source_field",
         "worst_hit_source_value", "error_kind", "changes_window_classification", "note"]
with open(roll, "w") as fh:
    fh.write("\t".join(rcols) + "\n")
    for cand in list(ant) + [c for c in per if c not in ant]:
        rs = per[cand]
        cls = [r["hit_class"] for r in rs if r["hit_class"] != "-"]
        w = ant.get(cand, {}).get("window") or "(n/a — different artifact)"
        best = max(rs, key=lambda r: SEV.get(r["hit_class"], 0))
        verdict = "CLEAN" if not cls else "HIT"
        fh.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in [
            cand, w, verdict, ",".join(sorted(set(cls))) or "-", len(cls),
            best["derived_field"], best["derived_value"], best["source_field"],
            best["source_value"], best["error_kind"], best["changes_window_classification"],
            best["note"]]) + "\n")
print("per_candidate_rows", len(per))
print("wrote", roll, "and", det)
