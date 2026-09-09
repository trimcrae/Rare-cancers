#!/usr/bin/env python3
"""What a k>=6 / k>=10 re-run of emc_fourth_cohort_quant.py WOULD and would NOT recover.

QUESTION. MATRIX-ADDRESS-2 measured that the fourth EMC cohort's 862-gene ceiling is imposed by
our own all-12-runs strict intersection: k=12 keeps 1,645 probes carrying 35.11% of the
67,890,929 persisted reads, while k>=6 keeps 16,222 carrying 66.40%. It named the next step as a
CPU-only re-run of the committed matcher at k>=6 and k>=10. That matcher assigns a gene by
streaming the Ensembl human cDNA + ncRNA FASTAs over HTTP (route B1/B2), which is CLOSED here and
is NOT attempted, retried, proxied around or substituted by this module.

WHAT THIS MODULE DOES INSTEAD, entirely from committed inputs and with no network at all:
it executes the ONE part of the matcher that needs no reference -- the core-identity step -- and
so measures, exactly rather than by projection, how many of the k>=6 and k>=10 probes could carry
a gene label from evidence already held in this checkout, and how many could not.

The matcher's own rule (emc_fourth_cohort_quant.py::_core_sets / map_probes_to_genes): for each
probe of the measured read length 50 nt it forms cores at trims 0, 4 and 8 -- lengths 50, 42 and
34 -- and indexes each core AND its reverse complement; the gene is read off the transcript that
matched the core at the BEST core length, recorded as 34 nt. Two probes sharing a core (or a
core's reverse complement) therefore match the same transcript and carry the same gene. That
propagation needs no FASTA, so it is run here.

INPUTS (committed, read-only):
  research/modalities/emc-fourth-cohort-probe-counts.tsv   213,007 rows, assigned_gene column
  research/modalities/emc-fourth-cohort-quant-inputs.json  probe_map.probe_to_gene (906) and
                                                           probe_map.probe_to_several_genes (77)
  research/modalities/emc-fourth-cohort-quant.json         the producer's own recorded counts

WHAT IT CANNOT SETTLE. Every probe whose core is NOT already held is UNKNOWN, not unassigned and
not absent: only the closed Ensembl route can label it. No expression value, contrast, score or
p-value is computed. Nothing here is a measurement of EMC biology, delivery, accessibility,
efficacy, selectivity, safety, therapeutic window or clinical readiness, and no such claim
follows from any line of it.
"""
import json, hashlib, os, sys

REPO = "/home/user/Rare-cancers"
PROBES = os.path.join(REPO, "research/modalities/emc-fourth-cohort-probe-counts.tsv")
INPUTS = os.path.join(REPO, "research/modalities/emc-fourth-cohort-quant-inputs.json")
QUANT = os.path.join(REPO, "research/modalities/emc-fourth-cohort-quant.json")

RC = str.maketrans("ACGTN", "TGCAN")
def revcomp(s): return s.translate(RC)[::-1]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

quant = json.load(open(QUANT))
got = sha256(PROBES)
if got != quant["probe_counts_sha256"]:
    sys.exit(f"ABORT: probe table sha256 {got} != recorded {quant['probe_counts_sha256']}")

pm = json.load(open(INPUTS))["probe_map"]
p2g = pm["probe_to_gene"]                    # 906 probes -> one gene
p2mg = pm["probe_to_several_genes"]          # 77 probes -> several genes
READ_LEN = pm["read_length_nt"]
BEST = pm["best_core_length_nt"]

# --- read the probe table -------------------------------------------------------------------
probes, kof, reads, tsvlab = [], {}, {}, {}
with open(PROBES) as f:
    header = next(f).rstrip("\n").split("\t")
    nrun = len(header) - 2
    for line in f:
        p = line.rstrip("\n").split("\t")
        seq, lab = p[0], p[1]
        vals = [int(x) for x in p[2:]]
        probes.append(seq)
        kof[seq] = sum(1 for v in vals if v > 0)
        reads[seq] = sum(vals)
        tsvlab[seq] = lab
total_reads = sum(reads.values())

# committed label inventory: the TSV column, plus the two maps in the inputs checkpoint
labelled = {}                                  # probe -> (source, gene-or-genes)
for s, g in p2g.items():   labelled[s] = ("inputs.probe_to_gene", [g])
for s, gs in p2mg.items(): labelled.setdefault(s, ("inputs.probe_to_several_genes", list(gs)))
for s, l in tsvlab.items():
    if l != "unassigned": labelled.setdefault(s, ("tsv.assigned_gene", [l]))

# --- the matcher's core-identity step, run without any reference ------------------------------
def cores(seq):
    out = {}
    for trim in (0, 4, 8):
        L = READ_LEN - 2 * trim
        if L < 24: continue
        c = seq[trim:trim + L]
        if "N" in c: continue
        out[L] = c
    return out

core_index = {}                                # (L, core) -> set of genes, from LABELLED probes
for s, (_, gs) in labelled.items():
    for L, c in cores(s).items():
        for key in (c, revcomp(c)):
            core_index.setdefault((L, key), set()).update(gs)

def propagated(seq):
    """Genes this probe would inherit under the matcher's own core rule, best length first."""
    for L in (BEST, READ_LEN, READ_LEN - 8):
        c = cores(seq).get(L)
        if c is None: continue
        g = core_index.get((L, c)) or core_index.get((L, revcomp(c)))
        if g: return L, sorted(g)
    return None, None

# --- Hamming-neighbour diagnostic against the k=12 set ---------------------------------------
k12 = [s for s in probes if kof[s] == nrun]
def blocks(seq, n):
    step = len(seq) // n
    return [(i, seq[i*step:(i+1)*step if i < n-1 else len(seq)]) for i in range(n)]
idx2 = {}
for s in k12:
    for b in blocks(s, 2): idx2.setdefault(b, []).append(s)
idx3 = {}
for s in k12:
    for b in blocks(s, 3): idx3.setdefault(b, []).append(s)
def hamm(a, b, cap):
    d = 0
    for x, y in zip(a, b):
        if x != y:
            d += 1
            if d > cap: return cap + 1
    return d
def nearest_k12(seq):
    best = 99
    cand = set()
    for b in blocks(seq, 3): cand.update(idx3.get(b, ()))
    for b in blocks(seq, 2): cand.update(idx2.get(b, ()))
    for c in cand:
        d = hamm(seq, c, 2)
        if d < best: best = d
        if best == 1: break
    return best

# --- per-threshold accounting -----------------------------------------------------------------
rows = []
for k in (12, 11, 10, 9, 8, 7, 6):
    sel = [s for s in probes if kof[s] >= k]
    have = [s for s in sel if s in labelled]
    miss = [s for s in sel if s not in labelled]
    prop_probes, prop_genes, prop_by_len = [], set(), {}
    for s in miss:
        L, gs = propagated(s)
        if gs:
            prop_probes.append(s)
            prop_by_len[L] = prop_by_len.get(L, 0) + 1
            if len(gs) == 1: prop_genes.add(gs[0])
    genes_have = set()
    for s in have:
        src, gs = labelled[s]
        if len(gs) == 1: genes_have.add(gs[0])
    halo = {1: 0, 2: 0}
    if k in (6, 10):
        for s in miss:
            d = nearest_k12(s)
            if d in halo: halo[d] += 1
    rows.append({
        "min_runs_present": k,
        "n_probes": len(sel),
        "persisted_read_share": round(sum(reads[s] for s in sel) / total_reads, 6),
        "n_probes_with_a_committed_gene_label": len(have),
        "n_probes_with_NO_committed_gene_label": len(miss),
        "n_of_those_labelled_by_core_identity_without_any_reference": len(prop_probes),
        "core_length_that_propagated": prop_by_len,
        "n_probes_still_UNKNOWN_without_the_closed_Ensembl_route": len(miss) - len(prop_probes),
        "distinct_single_genes_from_committed_labels": len(genes_have),
        "distinct_single_genes_added_by_core_identity": len(prop_genes - genes_have),
        "best_case_gene_count_from_held_data_alone": len(genes_have | prop_genes),
        "hamming_diagnostic_vs_k12_set": (
            {"n_unlabelled_probes_examined": len(miss),
             "n_within_hamming_1_of_a_k12_probe": halo[1],
             "n_at_hamming_2_of_a_k12_probe": halo[2],
             "fraction_within_hamming_2": round((halo[1] + halo[2]) / len(miss), 6) if miss else None}
            if k in (6, 10) else "not computed at this threshold"),
    })

out = {
 "_title": "What a k>=6 / k>=10 re-run would and would not recover — fourth EMC cohort",
 "_generated_by": "MATRIX-ADDRESS-3/relaxed_k_label_recovery.py",
 "_no_network": "No HTTP of any kind. The Ensembl cDNA/ncRNA route (B1/B2) is closed and was not "
                "attempted, retried, proxied around or substituted.",
 "_inputs": {
   "probe_counts_tsv": "research/modalities/emc-fourth-cohort-probe-counts.tsv",
   "probe_counts_sha256_measured": got,
   "probe_counts_sha256_recorded": quant["probe_counts_sha256"],
   "quant_inputs_checkpoint": "research/modalities/emc-fourth-cohort-quant-inputs.json",
   "quant_record": "research/modalities/emc-fourth-cohort-quant.json",
 },
 "committed_label_inventory": {
   "probe_to_gene_one_gene": len(p2g),
   "probe_to_several_genes_ambiguous": len(p2mg),
   "tsv_assigned_gene_rows": sum(1 for l in tsvlab.values() if l != "unassigned"),
   "distinct_probes_with_any_committed_label": len(labelled),
   "⛔ every_one_of_them_sits_at_k": sorted({kof[s] for s in labelled}),
 },
 "matcher_rule_applied": {
   "read_length_nt": READ_LEN, "core_trims": [0, 4, 8], "core_lengths_nt": [50, 42, 34],
   "best_core_length_nt": BEST, "both_strands": True,
   "⚠ note": "emc_fourth_cohort_quant.py builds its core dict with d.setdefault(core, p), so if "
             "two probes shared a core the matcher would credit only the first; the GENE is still "
             "determined, but the assigned-probe count would not double.",
 },
 "n_runs": nrun, "n_probe_rows": len(probes), "total_persisted_reads": total_reads,
 "⛔ unknown_is_not_zero": "A probe with no committed core match is UNKNOWN, not unassigned and "
   "not absent from the panel. Only the closed reference route can decide it.",
 "by_threshold": rows,
}
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
print()
