#!/usr/bin/env python3
"""Probe-persistence rarefaction for the fourth EMC cohort (PRJNA1357027 / SRP640302).

QUESTION. The committed gene table for this cohort carries 862 genes and cannot see a
compartment (0/11 endothelial, 0/5 transport markers; re-derived in checks/01). Its producer
offered the gene matcher ONLY the probes present in EVERY one of the 12 read runs -- 1,645 of
them. This module measures, from committed files alone, how much of that 1,645 ceiling is
imposed by the all-12 intersection rule itself, versus by the panel or the matcher.

INPUT (committed, read-only, no network):
  research/modalities/emc-fourth-cohort-probe-counts.tsv   (sha256 c689e0fd...d26fc)
  research/modalities/emc-fourth-cohort-quant.json         (the producer's own record)

WHAT IT MEASURES. For k = 1..12: the number of distinct probe sequences whose count is
non-zero in at least k of the 12 runs, and the share of all persisted reads those probes carry.

WHAT IT CANNOT SETTLE. Per the producer's own caveat, "a zero in the probe table means the
sequence was not among the counts PERSISTED for that run -- it may have been observed below the
persistence cap. It is NOT a measurement of zero reads." So presence-in-k-runs is a statement
about lossy-counting persistence, not about the tumour. This module assigns no gene, computes
no expression, no contrast and no p-value, and supports no claim about EMC biology, delivery,
efficacy, selectivity or therapeutic window.
"""
import csv, json, hashlib, sys, os

REPO = "/home/user/Rare-cancers"
PROBES = os.path.join(REPO, "research/modalities/emc-fourth-cohort-probe-counts.tsv")
QUANT = os.path.join(REPO, "research/modalities/emc-fourth-cohort-quant.json")

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

quant = json.load(open(QUANT))
rec_sha = quant["probe_counts_sha256"]
got_sha = sha256(PROBES)
if rec_sha != got_sha:
    sys.exit(f"ABORT: probe table sha256 {got_sha} != recorded {rec_sha}")

n_runs = None
present_hist = {}          # k -> n probes present in exactly k runs
reads_by_k = {}            # k -> total persisted reads on probes present in exactly k runs
assigned_by_k = {}         # k -> n probes with a gene assignment
total_rows = 0
total_reads = 0

with open(PROBES, newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    run_cols = header[2:]
    n_runs = len(run_cols)
    for row in r:
        total_rows += 1
        vals = [int(x) for x in row[2:]]
        k = sum(1 for v in vals if v > 0)
        s = sum(vals)
        present_hist[k] = present_hist.get(k, 0) + 1
        reads_by_k[k] = reads_by_k.get(k, 0) + s
        if row[1] != "unassigned":
            assigned_by_k[k] = assigned_by_k.get(k, 0) + 1
        total_reads += s

# cumulative: probes present in AT LEAST k runs
curve = []
for k in range(1, n_runs + 1):
    n_at_least = sum(present_hist.get(j, 0) for j in range(k, n_runs + 1))
    reads_at_least = sum(reads_by_k.get(j, 0) for j in range(k, n_runs + 1))
    assigned_at_least = sum(assigned_by_k.get(j, 0) for j in range(k, n_runs + 1))
    curve.append({
        "min_runs_present": k,
        "n_probes": n_at_least,
        "persisted_reads_on_those_probes": reads_at_least,
        "fraction_of_all_persisted_reads": round(reads_at_least / total_reads, 6),
        "n_of_those_probes_the_matcher_assigned_to_one_gene": assigned_at_least,
    })

out = {
    "_title": "Probe-persistence rarefaction, fourth EMC cohort (PRJNA1357027 / SRP640302)",
    "_generated_by": "MATRIX-ADDRESS-2/probe_intersection_rarefaction.py",
    "_question": "How much of the 1,645-probe ceiling on this cohort's gene table is imposed by "
                 "the 'present in every one of the 12 read runs' rule, rather than by the assay "
                 "panel or by the gene matcher?",
    "_inputs": {
        "probe_counts_tsv": "research/modalities/emc-fourth-cohort-probe-counts.tsv",
        "probe_counts_sha256_recorded": rec_sha,
        "probe_counts_sha256_measured": got_sha,
        "quant_record": "research/modalities/emc-fourth-cohort-quant.json",
    },
    "⛔ a_zero_in_the_probe_table": quant["⛔ a_zero_in_the_probe_table"],
    "_what_this_cannot_settle": [
        "Nothing about EMC biology. No gene is assigned here, no expression value is compared.",
        "Presence-in-k-runs is a persistence statement under lossy counting, not a zero measurement.",
        "No delivery, accessibility, efficacy, selectivity, safety or therapeutic-window claim.",
        "It does NOT show that a relaxed intersection would recover any named marker: assigning "
        "the extra probes to genes needs a reference transcriptome, which is a closed route here.",
    ],
    "n_runs": n_runs,
    "run_columns": run_cols,
    "n_probe_rows": total_rows,
    "total_persisted_reads": total_reads,
    "producer_recorded": {
        "n_probes_common_to_every_read_run": quant["n_probes_common_to_every_read_run"],
        "n_probes_offered_to_matcher": quant["probe_map"]["n_probes_offered"],
        "n_probes_assigned_to_one_gene": quant["probe_map"]["n_probes_assigned_to_one_gene"],
        "n_probes_matching_several_genes": quant["probe_map"]["n_probes_matching_several_genes"],
        "n_probes_unassigned": quant["probe_map"]["n_probes_unassigned"],
        "n_genes_with_at_least_one_assigned_probe": quant["n_genes_with_at_least_one_assigned_probe"],
    },
    "rarefaction_at_least_k_runs": curve,
}
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
print()
