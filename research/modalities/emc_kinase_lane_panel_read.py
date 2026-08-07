#!/usr/bin/env python3
"""PRKDC and SGK1 in real EMC tumours — read from a committed artifact. $0, no network, no GPU.

⭐ WHY THIS EXISTS, AND WHY IT IS A RE-READ RATHER THAN A RETRIEVAL (2026-08-07).

Both kinase lanes (emc-dnapk-nr4a3-lane-assessment.md, emc-sgk1-lane-assessment.md) reached the
same question — *is this kinase actually elevated in EMC tumours?* — and both were about to record
it as "no reading exists, needs a GEO dispatch". That was wrong for one of the two genes.

`emc-atr-vulnerability-inputs.json` -> `/part_b/platforms/<platform>/geneset_gene_values` already
holds **PER-SAMPLE values for a 1,299-gene panel** across every EMC-bearing GEO series the repo has
characterised, with the sample titles beside them. **PRKDC is in that panel.** So the answer was on
disk and nobody had asked. CLAUDE.md §4: a $0 observation is never "watching" — take it now.

⛔ AND THE HALF THAT IS STILL AN ABSENT READING. **SGK1 is NOT in the 1,299-gene panel**, on any
platform. That is a fact about the panel, which was assembled for a DDR/replication-stress question,
and it is NOT a statement about SGK1's expression in EMC. This script prints that distinction
explicitly for every gene it is asked about, because the two look identical in a results table and
only one of them is a finding.

WHAT THE NUMBERS ARE, AND WHAT THEY ARE NOT:
  * `value_kind` is carried through from the source. Two-colour platforms are LOG-RATIO AGAINST A
    REFERENCE POOL, so a "mean" there is relative, not absolute expression, and the two kinds must
    never be pooled.
  * `delta_emc_minus_comparator` is a crude difference of means over small n. It has no p-value and
    none is offered.
  * `percentile_of_delta_within_panel` is the null that makes the delta readable: where this gene's
    contrast sits among the SAME 1,299 genes' contrasts on the SAME samples. A gene near the 50th
    percentile is doing what the panel does. That is the honest way to read a delta with n=6.

Usage:  python3 research/modalities/emc_kinase_lane_panel_read.py > <out>.json
"""
import json
import statistics as st

SRC = 'research/modalities/emc-atr-vulnerability-inputs.json'

# The EMC-bearing series label their samples in several ways; all observed forms are matched.
EMC_MARKERS = ('myxoid chondrosarcoma', 'extraskeletal myxoid', '_emc')

# PRKDC and SGK1 are the two lanes' genes. ATR and NR4A3 are read alongside as orientation:
# ATR because the panel was built for it (so it is the panel's own positive-shaped control), and
# NR4A3 because its absence from the panel is worth showing rather than assuming.
GENES = ('PRKDC', 'SGK1', 'NR4A3', 'ATR')


def main() -> None:
    d = json.load(open(SRC, encoding='utf-8'))
    plats = d['part_b']['platforms']

    out = {
        "_what": "PRKDC and SGK1 in real EMC tumour expression, read from the committed 1,299-gene "
                 "panel in emc-atr-vulnerability-inputs.json. NO NEW RETRIEVAL — a re-read of data "
                 "already on disk. $0.",
        "_source_artifact": SRC,
        "_source_field": "/part_b/platforms/<platform>/geneset_gene_values",
        "_absent_reading_warning": "measured:false means the gene is NOT IN THE 1,299-GENE PANEL. "
                                   "The panel was assembled for a DDR/replication-stress question. "
                                   "It is a fact about the collector, never about the gene.",
        "_no_clinical_claim": "Nothing here asserts efficacy, safety, a therapeutic window or "
                              "clinical readiness. These are expression contrasts over 6 and 10 "
                              "tumours on two platforms, with no p-values.",
        "generated": "2026-08-07",
        "genes_requested": list(GENES),
        "platforms": {},
    }

    for name, p in plats.items():
        if p.get('_status') != 'read':
            out['platforms'][name] = {
                "_status": p.get('_status'),
                "_reading": "the collector could not read this platform — an ABSENT READING, "
                            "not a reading of absence",
            }
            continue

        samples = p.get('samples') or []
        vals = p.get('geneset_gene_values') or {}
        titles = [((s.get('title') or '') + ' ' + (s.get('annotation_verbatim') or '')).lower()
                  for s in samples]
        emc_idx = [i for i, t in enumerate(titles) if any(m in t for m in EMC_MARKERS)]
        rest_idx = [i for i in range(len(titles)) if i not in emc_idx]

        rec = {
            "series": p.get('series'),
            "platform": p.get('platform'),
            "value_kind": p.get('value_kind'),
            "n_samples": p.get('n_samples'),
            "n_geneset_genes_measured": p.get('n_geneset_genes_measured'),
            "n_emc_samples": len(emc_idx),
            "n_comparator_samples": len(rest_idx),
            "emc_sample_titles": [samples[i].get('title') for i in emc_idx],
            "genes": {},
        }

        # The null: every panel gene's own EMC-vs-comparator delta on these same samples.
        panel_deltas = []
        for g, v in vals.items():
            if not isinstance(v, list) or len(v) != len(samples):
                continue
            e = [v[i] for i in emc_idx if v[i] is not None]
            r = [v[i] for i in rest_idx if v[i] is not None]
            if e and r:
                panel_deltas.append((g, st.mean(e) - st.mean(r)))
        panel_deltas.sort(key=lambda x: x[1])
        order = {g: i for i, (g, _) in enumerate(panel_deltas)}

        for g in GENES:
            v = vals.get(g)
            if v is None:
                rec['genes'][g] = {
                    "measured": False,
                    "_reading": "gene NOT IN the panel — this is not a statement about its expression",
                }
                continue
            if not isinstance(v, list) or len(v) != len(samples):
                rec['genes'][g] = {
                    "measured": False,
                    "_reading": f"shape mismatch: {len(v) if hasattr(v, '__len__') else '?'} "
                                f"values against {len(samples)} samples",
                }
                continue
            e = [v[i] for i in emc_idx if v[i] is not None]
            r = [v[i] for i in rest_idx if v[i] is not None]
            if not e or not r:
                rec['genes'][g] = {
                    "measured": True,
                    "n_emc_nonnull": len(e),
                    "n_comparator_nonnull": len(r),
                    "_reading": "no usable EMC-vs-comparator split on this platform",
                }
                continue
            c = {
                "measured": True,
                "n_emc_nonnull": len(e),
                "n_comparator_nonnull": len(r),
                "emc_mean": round(st.mean(e), 4),
                "comparator_mean": round(st.mean(r), 4),
                "delta_emc_minus_comparator": round(st.mean(e) - st.mean(r), 4),
                "emc_values": e,
            }
            if g in order and len(panel_deltas) > 1:
                c["percentile_of_delta_within_panel"] = round(
                    100.0 * order[g] / (len(panel_deltas) - 1), 1)
                c["panel_n_genes_ranked"] = len(panel_deltas)
            rec['genes'][g] = c

        if panel_deltas:
            rec['panel_delta_background'] = {
                "mean": round(st.mean([x[1] for x in panel_deltas]), 4),
                "sd": round(st.pstdev([x[1] for x in panel_deltas]), 4),
                "_reading": "the spread of EMC-vs-comparator deltas across all panel genes on these "
                            "same samples. A gene's delta inside about one SD of this is doing what "
                            "the panel does.",
            }
        out['platforms'][name] = rec

    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
