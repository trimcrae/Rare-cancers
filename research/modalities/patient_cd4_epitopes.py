#!/usr/bin/env python3
"""
patient_cd4_epitopes.py — CD4 (MHC class-II) helper epitopes across the (EWSR1|TAF15)::NR4A3
fusion junction, per patient.

Why class II matters: an effective cancer vaccine usually needs CD4 "helper" T-cell
epitopes (MHC class II), not just CD8/class-I targets — class-II help drives durable CD8
responses and is built into the personalised-vaccine platforms cited in the clinical brief.
MHCflurry (used for class I) does not do class II, so this companion tool uses MHCnuggets
[Shao 2020], which predicts class-II binding and is pip-installable (run in an isolated
environment to avoid clashing with MHCflurry's TensorFlow pin).

Same inputs as patient_neoepitopes.py for the junction; class-II HLA via --hla2
(e.g. "DRB1*15:01,DRB1*03:01"). Output: ranked junction-spanning ~15mers predicted to bind
the patient's class-II alleles.

NOT a device / not clinical advice; predicted binding is a screen, not proof.
"""

import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LENGTHS = (15,)          # standard class-II presentation length (9mer core)
IC50_STRONG, IC50_BIND = 100.0, 1000.0   # nM; class-II binder conventions (looser than I)


def spanning(left, right, lengths):
    fusion = left + right
    j = len(left)
    out = {}
    for L in lengths:
        for s in range(max(0, j - L + 1), j):
            pep = fusion[s:s + L]
            if len(pep) == L and s < j < s + L:
                out[pep] = {"length": L, "n_from_left": j - s, "n_from_right": s + L - j}
    return out


def mhcnuggets_allele(a):
    """'DRB1*15:01' -> 'HLA-DRB115:01' (MHCnuggets class-II format)."""
    a = a.strip()
    if a.upper().startswith("HLA-"):
        a = a[4:]
    a = a.replace("*", "")
    # keep the gene (letters+digits) then 'NN:NN'
    return "HLA-" + a


def main():
    ap = argparse.ArgumentParser(description="Per-patient class-II (CD4) fusion-junction epitopes")
    ap.add_argument("--junction-seq", help="protein context 'LEFT|RIGHT' ('|' = seam)")
    ap.add_argument("--partner", default="EWSR1", choices=["EWSR1", "TAF15"])
    ap.add_argument("--partner-exon", type=int)
    ap.add_argument("--nr4a3-exon", type=int)
    ap.add_argument("--hla2", required=True, help="class-II alleles, e.g. 'DRB1*15:01,DRB1*03:01'")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sys.path.insert(0, HERE)
    from patient_neoepitopes import junction_from_seq, junction_from_exons  # type: ignore

    if args.junction_seq:
        left, right = junction_from_seq(args.junction_seq)
        source = {"mode": "junction-seq"}
    elif args.partner_exon and args.nr4a3_exon:
        left, right = junction_from_exons(args.partner, args.partner_exon, args.nr4a3_exon)
        source = {"mode": "exon", "partner": args.partner,
                  "partner_exon": args.partner_exon, "NR4A3_exon": args.nr4a3_exon}
    else:
        sys.exit("provide --junction-seq OR (--partner-exon AND --nr4a3-exon)")

    alleles = [a for a in (x.strip() for x in args.hla2.split(",")) if a]
    peps = spanning(left, right, LENGTHS)
    result = {
        "_note": "CD4/MHC class-II junction epitopes (MHCnuggets). IC50<100 strong, "
                 "<1000 binder. Screen only; confirm by T-cell assay. Not medical advice.",
        "source": source, "junction_context": left[-12:] + "|" + right[:12],
        "patient_class2_hla": alleles, "n_candidate_15mers": len(peps),
    }

    try:
        from mhcnuggets.src.predict import predict as mn_predict
    except Exception as e:  # noqa
        result["error"] = f"mhcnuggets unavailable ({e}); emitting candidate 15mers only"
        result["candidate_peptides"] = sorted(peps)
        _emit(result, args.out)
        return

    pep_file = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    pep_file.write("\n".join(sorted(peps)) + "\n")
    pep_file.close()

    rows = []
    for a in alleles:
        mhc = mhcnuggets_allele(a)
        out_csv = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False).name
        try:
            mn_predict(class_="II", peptides_path=pep_file.name, mhc=mhc, output=out_csv)
        except Exception as e:  # noqa
            result.setdefault("allele_errors", {})[a] = str(e)
            continue
        with open(out_csv) as fh:
            header = fh.readline()
            for line in fh:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                pep, ic50 = parts[0], parts[1]
                try:
                    ic = float(ic50)
                except ValueError:
                    continue
                m = peps.get(pep, {})
                rows.append({"peptide": pep, "allele": a, "ic50_nM": round(ic, 1),
                             "call": "strong" if ic < IC50_STRONG else ("binder" if ic < IC50_BIND else "non-binder"),
                             "tumour_specific_residues": f"{m.get('n_from_left','?')} left + {m.get('n_from_right','?')} right"})
    rows.sort(key=lambda r: r["ic50_nM"])
    binders = [r for r in rows if r["call"] != "non-binder"]
    result["n_predicted_binders"] = len(binders)
    result["n_strong"] = sum(1 for r in binders if r["call"] == "strong")
    result["shortlist"] = binders
    result["all_predictions"] = rows[:60]
    _emit(result, args.out)


def _emit(result, out):
    if out:
        with open(out, "w") as fh:
            json.dump(result, fh, indent=2)
        print("wrote", out, file=sys.stderr)
    print(f"\nCD4/class-II junction epitopes — {result['junction_context']}")
    print(f"class-II HLA: {', '.join(result['patient_class2_hla'])}")
    sl = result.get("shortlist")
    if sl is None:
        print("(mhcnuggets unavailable — candidate 15mers only)")
        return
    print(f"{len(sl)} predicted binder(s); {result.get('n_strong',0)} strong:")
    for r in sl[:15]:
        print(f"  {r['peptide']:17} {r['allele']:12} IC50={r['ic50_nM']:>8} nM  {r['call']}")


if __name__ == "__main__":
    main()
