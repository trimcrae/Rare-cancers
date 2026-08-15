#!/usr/bin/env python3
"""Where is wild-type PGR expressed — the exposure question this seam has and no other seam does.

⛔ WHY THIS FILE EXISTS SEPARATELY FROM `aso_offtarget_tissue_expression.py`.
That module answers: where are the OFF-TARGET LOCI of a transcriptome-wide search expressed. Its
membership rule is "a locus a 16-mer matched at 14/16", and its compartments are the two the drug is
DOSED into (liver, kidney) plus a soft-tissue proxy for the tumour bed. It is the right instrument
for the panel and it cannot answer the question the PGR::NR4A3 seam raises, for two reasons that are
both structural rather than fixable by running it harder:
  (1) the gene at issue is a PARENT, not an off-target locus, so it is not in that module's
      population at all; and
  (2) the tissues at issue — breast, uterus, ovary — are in neither of its compartments, because
      neither list was ever meant to cover a hormone receptor.

★ THE QUESTION, PLAINLY. PMID 36103645 reports the only EMC with a PGR 5' partner: "gene fusion of
progesterone receptor, PGR (exon2) to the 5′ untranslated region (UTR) of NR4A3 (exon2)", in a
35-year-old woman. Half of every junction-spanning gapmer at that seam is PGR sequence. So before
any off-target search, the reagent's most obvious liability is its own parent — a hormone receptor
that healthy premenopausal breast, uterus and ovary express — and the honest thing to publish beside
the design is where that parent is expressed, measured, in the same units and from the same release
the panel's screens use.

⛔ AND THE SEQUENCE HALF OF THAT QUESTION IS ALREADY ANSWERED, OFFLINE, BY A DIFFERENT FILE.
`pgr_parent_engagement.py` scans every design against the wild-type PGR MATURE transcript
exhaustively at <=2 mismatches, gap-resolved. Expression is the OTHER half: a transcript has to be
both matchable and present for an off-target effect, and neither alone is sufficient. This file
supplies only presence. ⚠ Reading a high TPM here as a hazard, without the sequence half, is exactly
the inference `aso_offtarget_tissue_expression.py` refuses to let a reader make — and there is no
risk column here either, for the same reason.

WHAT IS REUSED AND WHY NOTHING IS COPIED. The GTEx reader, its URL list with the recorded winner,
the known-answer controls, the release parse, `_tissue_block`, `_whole_body_context` and the tissue
LABELS all come from `aso_offtarget_tissue_expression` by import. A second GTEx parser in this
repository would be a second definition of "median TPM in tissue T", and the off-by-one-column
failure that module's `GTEX_CONTROLS` block describes is precisely what a private copy would
reintroduce with nothing checking it.

NETWORK. GTEx's public release object. The dev sandbox blocks it at CONNECT, so this runs on a
GitHub Actions runner (`fusion-cpu-extras.yml`, task `pgr_tissue_expression`). $0 CPU.

WHAT THIS IS NOT.
  · NOT a safety, tolerability, therapeutic-window or clinical-readiness statement. An expression
    value is a fact about a gene in a tissue.
  · NOT a cleavage or knockdown prediction, and NOT joined to any oligonucleotide here.
  · NOT a coverage claim. PGR is in neither partner-genotyped EMC cohort this repository counts
    against; the coverage consequence is zero and `aso_coverage_ladder.py` owns it.
  · NOT a claim about the tumour. GTEx contains no EMC and no sarcoma of any kind.

Run:
    python3 research/modalities/pgr_tissue_expression.py --fetch    # CI; needs the network
    python3 research/modalities/pgr_tissue_expression.py            # re-derive from the cache
    python3 research/modalities/pgr_tissue_expression.py --check    # is the artifact current?
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aso_offtarget_tissue_expression as TE     # noqa: E402  — ONE home for the GTEx instrument

OUT = os.path.join(HERE, "pgr-tissue-expression.json")
INPUTS = os.path.join(HERE, "pgr-tissue-expression-inputs.json")

#: ⭐ THE HORMONE-RESPONSIVE COMPARTMENT — the block this file exists to add, and the one neither of
#: the panel's two compartments contains. ⚠ EVERY LABEL BELOW WAS READ OUT OF THE COMMITTED
#: `aso-offtarget-tissue-expression-inputs.json` `arm_a_gtex.tissues` LIST, not written from
#: recollection: a GTEx `SMTSD` label that does not match a column silently reads as "no data",
#: which is the fail-quiet direction, and `_tissue_block` reports any that did not resolve under
#: `tissue_labels_not_found`.
HORMONE_TISSUES = [
    "Breast - Mammary Tissue",
    "Uterus",
    "Ovary",
    "Cervix - Ectocervix",
    "Cervix - Endocervix",
    "Fallopian Tube",
    "Vagina",
]

#: The genes this fetch is about. PGR is the parent; NR4A3 is the acceptor parent and is here so the
#: two halves of the chimera can be read side by side rather than one in isolation; the FET partners
#: are here because "PGR is unusual among the partners" is a claim that needs the others measured.
SYMBOLS = ["PGR", "NR4A3", "EWSR1", "TAF15", "FUS", "TCF12", "TFG"]


def collect():
    """Fetch GTEx for `SYMBOLS` plus the known-answer controls, and cache it. Needs the network."""
    gtex = TE.fetch_gtex(SYMBOLS)
    rec = {
        "_what": "GTEx v8 gene-level median TPM for the PGR::NR4A3 parents and the FET partners.",
        "_generated_utc": TE.datetime.now(TE.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols_requested": sorted(set(SYMBOLS) | set(TE.GTEX_CONTROLS)),
        "arm_a_gtex": gtex,
    }
    with open(INPUTS, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
    print(f"wrote {os.path.basename(INPUTS)}", file=sys.stderr)
    return rec


def _load_inputs():
    if not os.path.exists(INPUTS):
        raise SystemExit(
            f"{os.path.basename(INPUTS)} is not present. The fetch needs GTEx, which the dev "
            "sandbox blocks at CONNECT — run with --fetch on a GitHub Actions runner "
            "(fusion-cpu-extras.yml, task pgr_tissue_expression).")
    with open(INPUTS, encoding="utf-8") as fh:
        return json.load(fh)


def derive(inp):
    gtex = inp["arm_a_gtex"]
    # ⛔ THE CONTROLS GATE THE WHOLE ARTIFACT, exactly as they do for the panel's screen. A GCT is a
    # wide tab matrix and a one-column shift produces a completely plausible set of tissue profiles.
    controls = TE._control_verdict(gtex) if hasattr(TE, "_control_verdict") else None
    genes = {}
    for sym in SYMBOLS:
        genes[sym] = {
            "hormone_responsive_tissues": TE._tissue_block(
                gtex, sym, HORMONE_TISSUES, "hormone_responsive"),
            "exposure_liver_kidney": TE._tissue_block(
                gtex, sym, TE.EXPOSURE_TISSUES, "exposure_liver_kidney"),
            "tumour_compartment_proxy": TE._tissue_block(
                gtex, sym, TE.TUMOUR_COMPARTMENT_PROXY_TISSUES, "tumour_compartment_proxy"),
            "whole_body_context": TE._whole_body_context(gtex, sym),
        }
    return {
        "_what": ("Where the PGR::NR4A3 seam's two parents, and the five FET partners, are "
                  "expressed in normal human tissue — GTEx v8 median TPM, with a "
                  "HORMONE-RESPONSIVE block the panel's screen does not carry."),
        "_why": ("Half of every gapmer at the PGR e2 :: NR4A3 e2 seam is PGR sequence, and PGR is "
                 "a hormone receptor of normal breast, uterus and ovary in a premenopausal woman "
                 "— the patient of PMID 36103645. The parent's expression is therefore the "
                 "exposure half of this seam's specificity question and it belongs beside the "
                 "designs."),
        "_cost": "$0 — one GTEx release read on a GitHub-hosted CPU runner. No GPU, no rental.",
        "_what_this_is_not": [
            "NOT a safety, tolerability, therapeutic-window or clinical-readiness statement.",
            "NOT a cleavage or knockdown prediction, and not joined to any oligonucleotide here. "
            "The sequence half of the question is `pgr_parent_engagement.py`; expression is a "
            "NECESSARY condition for an off-target effect and never a sufficient one.",
            "NOT the panel's off-target tissue-expression screen. That screen's population is the "
            "loci a transcriptome-wide search returned at this seam, which requires the BLAST arm "
            "to have run; this file's population is the PARENTS, which it does not.",
            "NOT a tumour reading. GTEx contains no EMC and no sarcoma of any kind; the "
            "tumour_compartment_proxy block is normal tissue of the anatomical compartment EMC "
            "arises in and says so.",
            "NOT a coverage claim, and not a risk ranking. There is no risk column in this file.",
        ],
        "method": {
            "source": gtex.get("source"),
            "release": gtex.get("release"),
            "unit": gtex.get("unit"),
            "endpoint_used": gtex.get("endpoint_used"),
            "url": gtex.get("url"),
            "url_attempts": gtex.get("url_attempts"),
            "status": gtex.get("_status"),
            "known_answer_controls": controls,
            "_controls_note": ("ALB -> Liver, UMOD -> a kidney tissue, MYH7 -> muscle/heart. A run "
                               "whose controls fail must not be read as a measurement: a "
                               "one-column shift in a GCT produces entirely plausible profiles."),
            "hormone_responsive_tissues": HORMONE_TISSUES,
            "exposure_tissues": TE.EXPOSURE_TISSUES,
            "tumour_compartment_proxy_tissues": TE.TUMOUR_COMPARTMENT_PROXY_TISSUES,
            "_tissue_lists_are_imported": ("the exposure and proxy lists come from "
                                           "aso_offtarget_tissue_expression, not re-typed"),
        },
        "genes": genes,
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
        print("PGR tissue-expression artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"wrote {os.path.basename(OUT)}", file=sys.stderr)
    for sym in SYMBOLS:
        b = art["genes"][sym]["hormone_responsive_tissues"]
        if b.get("readable"):
            vals = {t: v for t, v in (b["values"] or {}).items() if v is not None}
            top = b.get("max_tissue_in_block")
            print(f"  {sym:<6} hormone-responsive max: {top} = "
                  f"{vals.get(top)} TPM   ({len(vals)}/{len(HORMONE_TISSUES)} tissues readable)",
                  file=sys.stderr)
        else:
            print(f"  {sym:<6} hormone-responsive: UNREADABLE — {b.get('reason')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
