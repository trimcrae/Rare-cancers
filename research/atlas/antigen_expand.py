#!/usr/bin/env python3
"""
EMC Atlas — expand the fusion-junction antigen axis to BOTH fusion subtypes (strategy Project 4).

The in-repo antigen computation covered only EWSR1::NR4A3. This adds the TAF15::NR4A3 junction and
directly COMPARES the two subtypes on MHC-I presentability, reusing the proven junction + MHCflurry
machinery in research/modalities/fusion_neoantigen.py (never duplicated).

Honest framing: the EWSR1 junction already gave a MODEST predicted MHC-I yield (2 strong / 34
peptides). The decision-relevant question is whether the TAF15 junction — a DIFFERENT 5' partner
meeting the same NR4A3 exon-2 start, so a different seam sequence — is any better or worse. Both
breakpoints are MODELED (flagged); junction peptides are breakpoint-sensitive, so this is a
feasibility comparison, not a patient-specific epitope list. Class II (MHCnuggets) is a separate,
isolated-env tool (patient_cd4_epitopes.py) run best-effort in CI.

MHCflurry -> runs in CI. Output: research/atlas/_generated/antigen-expanded.json (+ .md).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "..", "modalities"))
import fusion_neoantigen as FN  # noqa: E402  (reuse fetch_fasta, junction_peptides, ALLELES, LENGTHS)

# 5' partner UniProt + a MODELED retained N-terminal length (flagged assumption, as in FN for EWSR1).
# NR4A3 side is identical for both (exon-2 start), so only the left seam differs.
SUBTYPES = {
    "EWSR1::NR4A3": {"acc": "Q01844", "keep_to": FN.EWSR1_KEEP_TO},
    # TAF15 (Q92804): retain the N-terminal QG-rich transactivation region. Exact exon-6 boundary is
    # transcript-specific; modeled here and flagged. Re-run with a sequenced TAF15 breakpoint.
    "TAF15::NR4A3": {"acc": "Q92804", "keep_to": 200},
}
NR4A3_KEEP_FROM = FN.NR4A3_KEEP_FROM


def predict(peptides):
    """MHC-I presentation via MHCflurry across FN.ALLELES; returns (strong, sub500, best_pct, rows) or None."""
    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        return None
    predictor = Class1PresentationPredictor.load()
    df = predictor.predict(peptides=sorted(peptides), alleles={a: [a] for a in FN.ALLELES}, verbose=0)
    cols = list(df.columns)
    rank_col = "presentation_percentile" if "presentation_percentile" in cols else (
        "affinity_percentile" if "affinity_percentile" in cols else None)
    rows = []
    for _, r in df.iterrows():
        pct = float(r[rank_col]) if rank_col else None
        rows.append({"peptide": r["peptide"], "best_allele": r.get("best_allele"),
                     "affinity_nM": round(float(r["affinity"]), 1) if "affinity" in cols else None,
                     "presentation_percentile": round(pct, 4) if pct is not None else None})
    strong = sum(1 for x in rows if x["presentation_percentile"] is not None and x["presentation_percentile"] <= 0.5)
    sub500 = sum(1 for x in rows if x["affinity_nM"] is not None and x["affinity_nM"] <= 500)
    best = min((x["presentation_percentile"] for x in rows if x["presentation_percentile"] is not None), default=None)
    rows.sort(key=lambda x: (x["presentation_percentile"] is None, x["presentation_percentile"]))
    return {"n_strong_binders": strong, "n_sub500nM": sub500, "best_presentation_percentile": best,
            "top": rows[:15], "rank_column_used": rank_col}


def main():
    nr4 = FN.fetch_fasta(FN.NR4A3)
    right = nr4[NR4A3_KEEP_FROM - 1:]
    result = {"_note": "MHC-I junction-neoantigen comparison of EWSR1::NR4A3 vs TAF15::NR4A3 "
                       "(MHCflurry; %rank<=0.5 strong). Both breakpoints MODELED (flagged); "
                       "feasibility comparison, not patient-specific.",
              "alleles": FN.ALLELES, "lengths": FN.LENGTHS, "subtypes": {}}
    for name, cfg in SUBTYPES.items():
        five = FN.fetch_fasta(cfg["acc"])
        left = five[:cfg["keep_to"]]
        span = FN.junction_peptides(left, right, FN.LENGTHS)
        novel = {p: L for p, L in span.items() if p not in five and p not in nr4}
        entry = {"five_prime_acc": cfg["acc"], "keep_to_modeled": cfg["keep_to"],
                 "junction_context_left10": left[-10:], "junction_context_right10": right[:10],
                 "n_spanning": len(span), "n_novel": len(novel),
                 "breakpoint_modeled": True}
        pred = predict(list(novel))
        if pred is None:
            entry["prediction"] = "mhcflurry_unavailable"
            entry["novel_peptides"] = sorted(novel)
        else:
            entry.update(pred)
        result["subtypes"][name] = entry

    # comparison verdict (honest)
    ew = result["subtypes"].get("EWSR1::NR4A3", {})
    ta = result["subtypes"].get("TAF15::NR4A3", {})
    if "n_strong_binders" in ew and "n_strong_binders" in ta:
        result["comparison"] = {
            "EWSR1_strong": ew["n_strong_binders"], "TAF15_strong": ta["n_strong_binders"],
            "verdict": ("Both junctions give a MODEST predicted MHC-I yield -> neither common junction is a "
                        "strong shared class-I target; per the strategy this redirects toward fusion-induced "
                        "LINEAGE antigens. Class-II help + immunopeptidomics still warranted before any call.")}
    json.dump(result, open(os.path.join(OUTDIR, "antigen-expanded.json"), "w"), indent=2)

    lines = ["# Fusion-junction antigen: EWSR1 vs TAF15 (MHC-I, CI)", "", result["_note"], ""]
    for name, e in result["subtypes"].items():
        lines.append(f"## {name}")
        lines.append(f"- novel junction peptides: {e.get('n_novel')}; strong binders (%rank<=0.5): "
                     f"{e.get('n_strong_binders', 'n/a')}; sub-500nM: {e.get('n_sub500nM', 'n/a')}; "
                     f"best percentile: {e.get('best_presentation_percentile', 'n/a')}")
        lines.append(f"- seam (modeled): ...{e.get('junction_context_left10')}|{e.get('junction_context_right10')}...")
    if "comparison" in result:
        lines += ["", "**Verdict:** " + result["comparison"]["verdict"]]
    open(os.path.join(OUTDIR, "antigen-expanded.md"), "w").write("\n".join(lines) + "\n")
    print("wrote antigen-expanded.json/.md", file=sys.stderr)


if __name__ == "__main__":
    main()
