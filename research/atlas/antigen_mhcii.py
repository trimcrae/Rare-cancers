#!/usr/bin/env python3
"""
EMC Atlas — MHC class-II (CD4 help) junction epitopes for BOTH fusion subtypes.

Completes the fusion-junction antigen axis: an effective fusion vaccine usually needs CD4 helper
(class-II) epitopes, not just class-I. MHCflurry (class-I) can't do class-II, so this uses MHCnuggets
[Shao 2020] (run in an isolated venv in CI to avoid the TensorFlow-pin clash with MHCflurry). Reuses
the junction construction + sequences from research/modalities/fusion_neoantigen.py.

Both breakpoints MODELED (flagged). Output: research/atlas/_generated/antigen-mhcii.json (+ .md).
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "..", "modalities"))
import fusion_neoantigen as FN  # noqa: E402

SUBTYPES = {"EWSR1::NR4A3": {"acc": "Q01844", "keep_to": FN.EWSR1_KEEP_TO},
            "TAF15::NR4A3": {"acc": "Q92804", "keep_to": 200}}
# Common class-II DRB1 alleles (high global frequency).
DRB1 = ["DRB1*15:01", "DRB1*03:01", "DRB1*07:01", "DRB1*04:01", "DRB1*01:01", "DRB1*13:01", "DRB1*11:01"]
LEN2 = [15]
IC50_STRONG, IC50_BIND = 100.0, 1000.0


def mn_allele(a):
    a = a.strip()
    if a.upper().startswith("HLA-"):
        a = a[4:]
    return "HLA-" + a.replace("*", "")


def predict_class2(peptides):
    try:
        from mhcnuggets.src.predict import predict as mn_predict
    except Exception as e:  # noqa
        return None, f"mhcnuggets unavailable ({e})"
    pf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    pf.write("\n".join(sorted(peptides)) + "\n")
    pf.close()
    rows, errs = [], {}
    for a in DRB1:
        out_csv = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False).name
        try:
            mn_predict(class_="II", peptides_path=pf.name, mhc=mn_allele(a), output=out_csv)
        except Exception as e:  # noqa
            errs[a] = str(e)
            continue
        with open(out_csv) as fh:
            fh.readline()
            for line in fh:
                p = line.strip().split(",")
                if len(p) < 2:
                    continue
                try:
                    ic = float(p[1])
                except ValueError:
                    continue
                rows.append({"peptide": p[0], "allele": a, "ic50_nM": round(ic, 1),
                             "call": "strong" if ic < IC50_STRONG else ("binder" if ic < IC50_BIND else "non")})
    return {"rows": rows, "allele_errors": errs}, None


def main():
    nr4 = FN.fetch_fasta(FN.NR4A3)
    right = nr4[FN.NR4A3_KEEP_FROM - 1:]
    out = {"_note": "MHC class-II (CD4 help) junction epitopes, EWSR1 vs TAF15 (MHCnuggets). "
                    "IC50<100 strong, <1000 binder. Both breakpoints MODELED. Screen only; T-cell assay required.",
           "class_ii_alleles": DRB1, "subtypes": {}}
    for name, cfg in SUBTYPES.items():
        five = FN.fetch_fasta(cfg["acc"])
        left = five[:cfg["keep_to"]]
        span = FN.junction_peptides(left, right, LEN2)
        novel = {p: L for p, L in span.items() if p not in five and p not in nr4}
        entry = {"five_prime_acc": cfg["acc"], "n_novel_15mers": len(novel),
                 "seam": left[-12:] + "|" + right[:12], "breakpoint_modeled": True}
        pred, err = predict_class2(list(novel))
        if err:
            entry["prediction"] = err
            entry["novel_peptides"] = sorted(novel)
        else:
            rows = pred["rows"]
            strong = sorted([r for r in rows if r["call"] == "strong"], key=lambda x: x["ic50_nM"])
            binders = [r for r in rows if r["call"] in ("strong", "binder")]
            entry["n_strong_pep_allele"] = len(strong)
            entry["n_binder_pep_allele"] = len(binders)
            entry["distinct_strong_peptides"] = sorted({r["peptide"] for r in strong})
            entry["top_strong"] = strong[:12]
            if pred["allele_errors"]:
                entry["allele_errors"] = pred["allele_errors"]
        out["subtypes"][name] = entry
    json.dump(out, open(os.path.join(OUTDIR, "antigen-mhcii.json"), "w"), indent=2)

    lines = ["# Fusion-junction class-II (CD4 help) epitopes: EWSR1 vs TAF15 (CI)", "", out["_note"], ""]
    for name, e in out["subtypes"].items():
        lines.append(f"## {name}")
        lines.append(f"- novel 15mers: {e['n_novel_15mers']}; strong pep×allele: {e.get('n_strong_pep_allele','n/a')}; "
                     f"binder pep×allele: {e.get('n_binder_pep_allele','n/a')}; "
                     f"distinct strong peptides: {len(e.get('distinct_strong_peptides', []))}")
        lines.append(f"- seam (modeled): ...{e['seam']}...")
    open(os.path.join(OUTDIR, "antigen-mhcii.md"), "w").write("\n".join(lines) + "\n")
    print("wrote antigen-mhcii.json/.md", file=sys.stderr)


if __name__ == "__main__":
    main()
