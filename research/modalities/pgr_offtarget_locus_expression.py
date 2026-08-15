#!/usr/bin/env python3
"""Where are the PGR::NR4A3 gapmers' OFF-TARGET LOCI expressed? The panel's screen, run at this seam.

⛔ WHY A SCOPED MODULE RATHER THAN A NEW ROW IN `aso_offtarget_tissue_expression.PANEL`.
That module's `PANEL` is the manuscript's population: four seams the manuscript reports, whose loci,
counts and verdicts are quoted in the submission. Adding a fifth entry would move
`aso-offtarget-tissue-expression.json` — its locus set, its `n_loci`, its summary counts and every
number derived from them — on behalf of a junction the manuscript's panel deliberately EXCLUDES.
That is the same hazard `aso_noncoding_acceptor_screened_table.py` avoids by screening this lane into
its own directory: an excluded junction must be placeable BESIDE the panel, never silently INSIDE it.

⭐ SO EVERY COMPUTATION HERE IS THE PANEL'S OWN, CALLED WITH A DIFFERENT PANEL. `_locus_rows` takes a
`panel=` argument; `fetch_gtex`, `fetch_ncbi_gene`, `fetch_hpa`, `fetch_emc_series`, `_tissue_block`,
`_whole_body_context`, `_locus_verdict`, `_control_verdict` and the tissue lists are imported and
called, not copied. Two implementations of "median TPM in the dosed organs" is precisely how a table
whose purpose is comparability stops being comparable, and this artifact exists to be compared.

★ WHAT IT ANSWERS. Five screens established that a 16-mer at this seam matches sequence elsewhere in
the transcriptome. None of them asks whether the transcript carrying that sequence is PRESENT in a
tissue the drug reaches. A perfect match in a transcript no dosed organ expresses is a different
object from a weak match in one the liver runs at hundreds of TPM.

⛔ THIS IS THE OFF-TARGET-LOCUS HALF, AND IT IS NOT THE PGR PARENT QUESTION. Wild-type PGR is a
PARENT of this fusion, not an off-target locus, so it is not in this file's population at all — the
screen excludes parent hits by construction. The parent question has two files of its own:
`pgr_tissue_expression.py` (is wild-type PGR expressed where the drug goes?) and
`pgr_parent_engagement.py` (can any design engage wild-type PGR at all?). A reader must not read one
as the other.

WHAT THIS IS NOT — inherited verbatim in spirit from the module it calls.
  · NOT a cleavage prediction. Every locus here is here because a 16-mer matched at 14/16 — two
    mismatches — which is a sequence match, not a predicted cleavage event. Expression is a
    NECESSARY condition for an off-target effect, never a sufficient one.
  · NOT a safety, efficacy, therapeutic-window or clinical-readiness claim about any sequence.
  · NOT a risk ranking, and there is no risk column. Loci are ordered as the panel's module orders
    them — by an annotation property that is stated as one.
  · NOT a coverage claim. PGR is outside the partner cohort this repository counts against; the
    coverage consequence is exactly zero and `aso_coverage_ladder.py` owns it.

Run:
    python3 research/modalities/pgr_offtarget_locus_expression.py --fetch   # needs GTEx/NCBI/HPA
    python3 research/modalities/pgr_offtarget_locus_expression.py           # re-derive from cache
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_offtarget_tissue_expression as TE   # noqa: E402 — ONE home for every computation here

OUT = os.path.join(HERE, "noncoding-acceptor", "pgr-offtarget-locus-expression.json")
INPUTS = os.path.join(HERE, "noncoding-acceptor",
                      "pgr-offtarget-locus-expression-inputs.json")

#: ⛔ `designs: None` MEANS EVERY SCREENED DESIGN AT THE SEAM, NOT A CHOSEN ONE. No design at this
#: seam has been selected as a reagent — and it must not be, because the seam belongs to ONE reported
#: patient and adds no measurable coverage. Picking one here would smuggle a recommendation into a
#: measurement. The union across tiling registers is what the seam actually presents.
PANEL = [{
    "seam": "PGR_e2__NR4A3_e2",
    "screen": os.path.join("noncoding-acceptor", "junction-aso-offtarget-pgre2n2-deep500.json"),
    "designs": None,
    "role": ("the only reported PGR::NR4A3 EMC breakpoint (PMID 36103645), excluded from the "
             "manuscript panel by the NON_CODING_ACCEPTOR grade"),
    "junction_is_reported_in_patients": True,
    "note": ("ONE patient, and zero measurable coverage: PGR is not a partner of the 58-case cohort "
             "the coverage arithmetic uses. The tumour was EWSR1 FISH-negative and the fusion was "
             "found only by exome-capture RNA-seq, so its value is evidence about the limits of "
             "canonical-partner diagnosis, not about panel coverage."),
}]


def collect():
    _, rows, prov = TE._locus_rows(panel=PANEL)
    symbols = [r["locus"] for r in rows]
    print(f"loci from the PGR seam screen ({len(symbols)}): {symbols}", file=sys.stderr)
    inp = {
        "_what": ("Raw retrievals behind pgr-offtarget-locus-expression.json. One block per arm; "
                  "an arm that failed says so here and its verdict downstream is readable:false."),
        "_generated_utc": TE.datetime.now(TE.timezone.utc).isoformat(),
        "loci_provenance": prov,
        "loci": rows,
        "arm_a_gtex": TE.fetch_gtex(symbols),
        "arm_b_emc_series": TE.fetch_emc_series(symbols),
        "arm_c_ncbi_gene": TE.fetch_ncbi_gene(symbols),
        "arm_d_hpa": TE.fetch_hpa(symbols),
    }
    os.makedirs(os.path.dirname(INPUTS), exist_ok=True)
    with open(INPUTS, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(inp, indent=1, sort_keys=False) + "\n")
    print(f"wrote {os.path.basename(INPUTS)}", file=sys.stderr)
    return inp


def _load_inputs():
    if not os.path.exists(INPUTS):
        raise SystemExit(f"{os.path.basename(INPUTS)} is not present — run with --fetch first.")
    with open(INPUTS, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    inp = collect() if "--fetch" in argv else _load_inputs()
    art = TE.derive(inp)
    # Re-label so no reader can mistake this for the manuscript panel's artifact.
    art = {
        "_title": "Off-target locus expression at the PGR e2 :: NR4A3 e2 seam",
        "⛔_this_is_not_the_manuscript_panel": (
            "The manuscript's off-target tissue-expression artifact is "
            "aso-offtarget-tissue-expression.json and covers the four seams its panel reports. This "
            "file covers ONE seam that panel EXCLUDES, computed by the same module with a different "
            "`panel=` argument so the two are comparable. It must never be pooled into the "
            "panel's counts."),
        "⛔_zero_coverage": (
            "PGR is not a partner of the 58-case cohort every coverage rung is computed against "
            "(0/58, Wilson 95% [0, 0.0621]). Completing these screens does not create a coverage "
            "contribution and must not be reported as one."),
        "⚠_this_is_the_off_target_half_only": (
            "Wild-type PGR is a PARENT of this fusion and is excluded from the population here by "
            "construction. The parent question lives in pgr-tissue-expression.json (is PGR "
            "expressed where the drug goes) and pgr-parent-engagement-noncoding-acceptor.json "
            "(can any design engage it at all)."),
        "_generated_by": "research/modalities/pgr_offtarget_locus_expression.py",
        **art,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n")
    s = art.get("summary") or {}
    print(f"wrote {os.path.basename(OUT)}: {s.get('n_loci')} loci, "
          f"{s.get('n_loci_with_a_readable_exposure_reading')} with a readable exposure reading; "
          f"expressed in an exposure organ: {s.get('loci_expressed_in_an_exposure_organ')}; "
          f"unanswerable: "
          f"{s.get('loci_whose_exposure_question_is_unanswerable_from_public_data')}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
