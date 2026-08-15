#!/usr/bin/env python3
"""Where are the TCF12 e5 :: NR4A3 e3 reagent's off-target loci EXPRESSED?

⛔ WHY THIS FILE EXISTS SEPARATELY, AND WHY THAT IS NOT A DUPLICATE INSTRUMENT.
`aso_offtarget_tissue_expression.py` owns this question for the panel, and this seam is now IN its
`PANEL` — added the day GenBank AF289510.1 resolved the junction. Running that module's `--fetch`
here would answer the question for all four seams at once, and it is the right thing to run. It
cannot be run here, and the reason is measured rather than assumed:

    GTEx storage.googleapis.com   HTTP 206   reachable
    eutils.ncbi.nlm.nih.gov       403 Forbidden at the egress proxy
    www.proteinatlas.org          403 Forbidden at the egress proxy
    www.ebi.ac.uk                 403 Forbidden at the egress proxy

That module's `collect()` writes ALL FOUR arms into one committed cache. Running it from this box
would overwrite a cache in which arms C (NCBI Gene) and D (HPA) SUCCEEDED — for the three seams
already in the artifact — with one in which they failed. ⛔ THAT IS A REGRESSION DRESSED AS A
MEASUREMENT: the new seam would gain a reading and the three existing ones would silently lose two
arms. So this file adds the arm that IS reachable, for the loci that have no reading at all, and
touches neither the panel's module nor its cache.

⭐ WHAT IS REUSED, AND WHY NOTHING IS RE-IMPLEMENTED. The GTEx fetcher, its URL list, the
known-answer controls, the GCT parse, `_tissue_block`, `_whole_body_context`, `_control_verdict`,
the exposure and tumour-proxy tissue lists, AND the locus derivation all come from
`aso_offtarget_tissue_expression` by import. A second GTEx parser here would be a second definition
of "median TPM in tissue T", and the off-by-one-column failure that module's `GTEX_CONTROLS` block
exists to catch is exactly what a private copy would reintroduce with nothing checking it. Same
pattern, and the same reasoning, as `pgr_tissue_expression.py`.

⛔ THE CONTROLS GATE THE ARTIFACT. A GCT is a wide tab matrix and a one-column shift produces a
completely plausible set of tissue profiles, so a run whose controls fail is not a measurement. ALB
must peak in Liver, UMOD in a kidney tissue, MYH7 in ventricle or skeletal muscle. They are read
from the same matrix, in the same call, as every locus below.

WHY THIS SEAM IS WORTH ASKING ABOUT AT ALL, stated without importing a hazard. Its disclosed load is
CONCENTRATED rather than broad: the deep screen puts 17 of its gap-paired near-matches on ONE
curated locus. A per-gene expression reading is informative in that shape and uninformative when the
load is smeared across many. ⛔ THAT IS NOT A STATEMENT THAT THE SEAM IS RISKIER, and there is no
risk column in this file, deliberately — a locus is here because a 16-mer matched it at 14/16, which
is two mismatches and is not a predicted cleavage event.

WHAT THIS IS NOT.
  · NOT the panel's screen, and NOT parity with it. Arms B (the two readable EMC array series), C
    (NCBI Gene identity) and D (HPA) are unreachable from this box and are NOT in this file. The
    seam reaches full parity when `aso_offtarget_tissue_expression.py --fetch` next runs on a
    runner with the PANEL entry committed; this is the exposure arm, delivered early.
  · NOT a cleavage or knockdown prediction, and not joined to any oligonucleotide. Expression is a
    NECESSARY condition for an off-target effect and never a sufficient one.
  · NOT a safety, tolerability, therapeutic-window or clinical-readiness statement about any
    sequence. An expression value is a fact about a gene in a tissue.
  · NOT a tumour reading. GTEx contains no EMC and no sarcoma of any kind; the tumour-proxy block is
    normal tissue of the anatomical compartment EMC arises in, and says so.
  · NOT a reading of absence. A locus with no row in the matrix is `readable: false` with the reason
    stated, and is NEVER rendered as "not expressed".

Run:
    python3 research/modalities/tcf12_offtarget_tissue_expression.py --fetch   # needs GTEx
    python3 research/modalities/tcf12_offtarget_tissue_expression.py           # re-derive from cache
    python3 research/modalities/tcf12_offtarget_tissue_expression.py --check   # is it current?
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_offtarget_tissue_expression as TE     # noqa: E402  — ONE home for the GTEx instrument

OUT = os.path.join(HERE, "tcf12-offtarget-tissue-expression.json")
INPUTS = os.path.join(HERE, "tcf12-offtarget-tissue-expression-inputs.json")

#: The seam this file is about, named once and matched against the panel's own membership.
SEAM = "TCF12_e5__NR4A3_e3"


def loci_rows():
    """The loci THIS seam contributes, derived from the committed deep screen — never typed here.

    ⛔ DERIVED, AND THE DERIVATION IS THE POINT. `_locus_rows()` reads the committed
    `junction-aso-offtarget-tcf12e5n3-deep500-b1.json`, applies the screen's own
    `true_cleavage_risk` class and recounts hits per gene. Typing a locus list into this file would
    let it drift from the screen it claims to describe, which is the failure the panel's module
    already refuses for its own three seams.
    """
    if not any(p["seam"] == SEAM for p in TE.PANEL):
        raise RuntimeError(
            f"{SEAM} is not in aso_offtarget_tissue_expression.PANEL, so this file would be "
            "describing a seam the panel does not carry. Add it there first — the panel's "
            "membership rule is a published exon-resolved breakpoint, and this seam has one "
            "(GenBank AF289510.1).")
    _, rows, prov = TE._locus_rows()
    mine = [r for r in rows if SEAM in (r.get("seams") or [])]
    if not mine:
        raise RuntimeError(f"the committed deep screen at {SEAM} yielded no locus rows")
    return mine, prov


def collect():
    """Fetch GTEx for this seam's loci plus the known-answer controls, and cache it."""
    rows, prov = loci_rows()
    symbols = [r["locus"] for r in rows]
    print(f"loci from the {SEAM} screen: {symbols}", file=sys.stderr)
    gtex = TE.fetch_gtex(symbols)
    rec = {
        "_what": (f"GTEx v8 gene-level median TPM for the off-target loci of the {SEAM} reagent, "
                  "plus the three known-answer controls."),
        "_generated_utc": TE.datetime.now(TE.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seam": SEAM,
        "symbols_requested": sorted(set(symbols) | set(TE.GTEX_CONTROLS)),
        "loci_provenance": prov,
        "loci": rows,
        "arm_a_gtex": gtex,
    }
    with open(INPUTS, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
    print(f"wrote {os.path.basename(INPUTS)}", file=sys.stderr)
    return rec


def _load_inputs():
    if not os.path.exists(INPUTS):
        raise SystemExit(
            f"{os.path.basename(INPUTS)} is not present — run with --fetch. GTEx answers from this "
            "sandbox (measured HTTP 206); NCBI, HPA and Europe PMC do not (403 at the proxy).")
    with open(INPUTS, encoding="utf-8") as fh:
        return json.load(fh)


def derive(inp):
    gtex = inp["arm_a_gtex"]
    controls = TE._control_verdict(gtex)
    loci = {}
    for row in inp["loci"]:
        sym = row["locus"]
        # ⚠ FIELD NAMES ARE READ OFF THE ROW, NOT GUESSED. The first draft of this carried
        # `row.get("n_hits")`, which does not exist on a locus row, so the artifact shipped a
        # plausible-looking `n_gap_paired_hits: null` for every locus — a populated field that was
        # never measured, which CLAUDE.md §4 names as more dangerous than an empty one.
        loci[sym] = {
            "n_transcript_records": row.get("n_transcript_records"),
            "n_curated_records": row.get("n_curated_records"),
            "n_predicted_records": row.get("n_predicted_records"),
            "n_designs_hitting_it": row.get("n_designs_hitting_it"),
            "designs_hitting_it": row.get("designs_hitting_it"),
            "exposure_liver_kidney": TE._tissue_block(
                gtex, sym, TE.EXPOSURE_TISSUES, "exposure_liver_kidney"),
            "tumour_compartment_proxy": TE._tissue_block(
                gtex, sym, TE.TUMOUR_COMPARTMENT_PROXY_TISSUES, "tumour_compartment_proxy"),
            "whole_body_context": TE._whole_body_context(gtex, sym),
        }
    readable = [s for s, b in loci.items() if b["exposure_liver_kidney"].get("readable")]
    unreadable = {s: b["exposure_liver_kidney"].get("reason")
                  for s, b in loci.items() if not b["exposure_liver_kidney"].get("readable")}
    return {
        "_what": (f"Where the off-target loci of the {SEAM} junction gapmer are expressed in normal "
                  "human tissue — GTEx v8 median TPM, in the two dosed compartments and a "
                  "tumour-bed proxy."),
        "_why": ("This seam entered the panel's expression screen on 2026-08-15, when GenBank "
                 "AF289510.1 resolved its junction to the nucleotide and it became the fourth seam "
                 "with a published exon-resolved breakpoint. Its loci had no expression reading of "
                 "any kind. GTEx answers from the dev sandbox and the panel's other three arms do "
                 "not, so this delivers the exposure arm rather than waiting for all four."),
        "_cost": "$0 — one GTEx release read. No GPU, no rental, no CI dispatch.",
        "_what_this_is_not": [
            "NOT the panel's screen and NOT parity with it. Arms B (EMC array series), C (NCBI "
            "Gene identity) and D (HPA) are 403 at this box's egress proxy and are absent here. "
            "Parity arrives when aso_offtarget_tissue_expression.py --fetch next runs on a runner "
            "with this seam committed into its PANEL.",
            "NOT a cleavage or knockdown prediction, and not joined to any oligonucleotide. Every "
            "hit behind these loci sits at 14/16 identity — two mismatches in a 16-mer — and "
            "whether such a duplex is a substrate at all is an affinity question no screen here "
            "and no expression value anywhere can answer.",
            "NOT a safety, tolerability, therapeutic-window or clinical-readiness statement.",
            "NOT a tumour reading. GTEx contains no EMC and no sarcoma of any kind.",
            "NOT a risk ranking. There is no risk column in this file, deliberately.",
            "NOT a reading of absence. An unreadable locus says so, with its reason.",
        ],
        "seam": SEAM,
        "seam_breakpoint_provenance": {
            "reported_at": "nucleotide resolution",
            "accession": "AF289510.1",
            "cites_pmid": "11156374",
            "one_home": "research/manuscripts/tcf12_breakpoint_assignment.py",
            "⚠_one_tumour": ("the junction is resolved and its recurrence is UNTESTED: one "
                             "TCF12-rearranged tumour has ever been sequenced at it."),
        },
        "method": {
            "source": gtex.get("source"),
            "release": gtex.get("release"),
            "unit": gtex.get("unit"),
            "endpoint_used": gtex.get("endpoint_used"),
            "url": gtex.get("url"),
            "url_attempts": gtex.get("url_attempts"),
            "status": gtex.get("_status"),
            "⛔_known_answer_controls": controls,
            "_controls_note": ("ALB -> Liver, UMOD -> a kidney tissue, MYH7 -> ventricle or "
                               "skeletal muscle, read from the same matrix in the same call. A run "
                               "whose controls fail must not be read as a measurement: a "
                               "one-column shift in a GCT produces entirely plausible profiles."),
            "exposure_tissues": TE.EXPOSURE_TISSUES,
            "tumour_compartment_proxy_tissues": TE.TUMOUR_COMPARTMENT_PROXY_TISSUES,
            "_lists_and_reader_are_imported": ("every tissue label, the GTEx fetcher, the GCT "
                                               "parse and the block builders come from "
                                               "aso_offtarget_tissue_expression; nothing is "
                                               "re-implemented or re-typed here"),
            "loci_are_derived_from": inp.get("loci_provenance", {}).get("panel"),
        },
        "⚠_which_designs_touch_which_locus_stated_WITHOUT_the_expression_join": {
            "_why_this_is_separate": (
                "⛔ THIS FILE DOES NOT JOIN EXPRESSION TO AN OLIGONUCLEOTIDE, and the panel's module "
                "refuses the same join for the same reason: a locus is in this population because a "
                "16-mer matched it at 14/16, so a median TPM is evidence about the GENE and the "
                "step from 'this gene is expressed in kidney' to 'this reagent does something in "
                "kidney' needs an affinity argument no screen here has made. What IS reportable is "
                "set membership — which designs touch which locus — and a reader can hold that "
                "beside the expression blocks without either of us making the inference for them."),
            "by_locus": {s: {"n_designs_hitting_it": b["n_designs_hitting_it"],
                             "designs_hitting_it": b["designs_hitting_it"]}
                         for s, b in loci.items()},
        },
        "n_loci": len(loci),
        "n_loci_readable_in_gtex": len(readable),
        "loci_not_readable_in_gtex": unreadable,
        "_reading_the_unreadable_five": (
            "All five are LOC/LINC entries with no row in the GTEx v8 gene model. That is a property "
            "of the reference the instrument was built on, not of the loci: they are annotated in "
            "RefSeq, which is where the screen found them, and absent from a 2017 gene model. "
            "⛔ THEY ARE NOT READ AS ZERO, and the exposure question is UNANSWERED for them rather "
            "than answered negatively. Arms C and D of the panel's screen exist to characterise "
            "exactly this class, and neither is reachable from this box."),
        "loci": loci,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    inp = collect() if "--fetch" in argv else _load_inputs()
    art = derive(inp)
    new = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print(f"{os.path.basename(OUT)} is stale; re-run without --check", file=sys.stderr)
            return 1
        print("TCF12 off-target tissue-expression artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    c = art["method"]["⛔_known_answer_controls"]
    print(f"  controls: {json.dumps(c)[:300]}", file=sys.stderr)
    for sym, b in art["loci"].items():
        e = b["exposure_liver_kidney"]
        if e.get("readable"):
            vals = {t: v for t, v in (e["values"] or {}).items() if v is not None}
            w = b.get("whole_body_context") or {}
            top = (w.get("top_tissues") or [{}])[0]
            print(f"  {sym:<14} liver/kidney max: {e.get('max_tissue_in_block')} = "
                  f"{vals.get(e.get('max_tissue_in_block'))} TPM   | whole-body max "
                  f"{top.get('tissue')} = {top.get('median_tpm')}", file=sys.stderr)
        else:
            print(f"  {sym:<14} UNREADABLE — {e.get('reason')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
