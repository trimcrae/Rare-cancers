#!/usr/bin/env python3
"""Does the junction screen's knife-edge survive a SECOND, independently trained predictor?

WHAT QUESTION THIS SETTLES. Every binding figure in the EMC junction-vaccine paper comes from one
software suite, and the paper's central claim is about how those figures move with the acceptance
threshold. An external reviewer put the obvious objection (aiXiv 1365, W2): the threshold
sensitivity may be "an artifact of a specific, single metric". If it is, the paper's main result is
about MHCflurry. If it is not, the result is about the junction, and that is a stronger paper.

WHAT IS COMPARED, AND WHAT DELIBERATELY IS NOT. MHCnuggets is an independently trained class I
predictor with a different architecture, a different training set and a NATIVE OUTPUT ON A DIFFERENT
SCALE — predicted IC50 in nM, against MHCflurry's presentation percentile.
⛔ THE TWO SCALES ARE NOT FORCED ONTO ONE AXIS. Rescaling one predictor's output into the other's
units would make the agreement an artifact of the rescaling. Each predictor is swept over ITS OWN
conventional threshold instead, and what is compared is the SHAPE of the two curves and the SET of
presenting alleles each returns at its own field-standard cut. Concordance then means two
independent instruments agree about the junction; it never means two numbers were made to match.

⚠ AN ALLELE MHCNUGGETS HAS NO MODEL FOR IS NOT AN ALLELE THAT FAILS TO PRESENT. Every such allele
is recorded by name in `alleles_without_a_model` and excluded from the comparison's denominator; a
missing model silently scored as a non-binder would manufacture agreement in the direction that
flatters the paper.

Phases, because MHCnuggets needs an old Keras and lives in its own interpreter in CI:
  --predict   run MHCnuggets class I over the junction peptides x the panel; write the matrix.
  --curve     read that matrix, build coverage vs IC50 threshold with hla_coverage's own formula
              and frequencies, and compare against the MHCflurry curve. Needs no MHCnuggets.

Outputs: epitope-allele-matrix-mhcnuggets.json (--predict),
         predictor-concordance.json (--curve)
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BREAKPOINTS = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
MATRIX = os.path.join(HERE, "epitope-allele-matrix.json")
FLURRY_CURVE = os.path.join(HERE, "coverage-threshold-curve.json")
NUG_MATRIX = os.path.join(HERE, "epitope-allele-matrix-mhcnuggets.json")
OUT = os.path.join(HERE, "predictor-concordance.json")

LENGTHS = [8, 9, 10, 11]
#: The field-standard class I binder cut on predicted IC50. Named as a convention, exactly as the
#: manuscript names 0.5 as one — the point of this file is that neither is defended by its user.
IC50_STRONG = 500.0
#: The sweep. Wide enough that the shape, not one point, is what gets compared.
IC50_GRID = [10, 20, 50, 100, 150, 200, 300, 400, 500, 600, 750, 1000, 1500, 2000, 3000, 5000,
             10000, 20000, 50000]


def peptides():
    bp = json.load(open(BREAKPOINTS))
    return sorted({p for jn in bp.get("junctions", []) for p in jn.get("novel_peptides", [])
                   if len(p) in LENGTHS})


def panel():
    return json.load(open(MATRIX))["panel"]


def nuggets_allele(a):
    """'HLA-A*02:01' -> 'HLA-A02:01' (MHCnuggets class I format)."""
    return "HLA-" + a.replace("HLA-", "").replace("*", "")


def do_predict():
    try:
        from mhcnuggets.src.predict import predict as mn_predict
    except Exception as e:  # noqa: BLE001
        print(f"  mhcnuggets unavailable ({e}); nothing written", file=sys.stderr)
        return 1
    peps, pan = peptides(), panel()
    pf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    pf.write("\n".join(peps) + "\n")
    pf.close()

    calls, missing, errors = [], [], {}
    for a in pan:
        out_csv = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False).name
        try:
            mn_predict(class_="I", peptides_path=pf.name, mhc=nuggets_allele(a), output=out_csv)
        except Exception as e:  # noqa: BLE001 — a missing model IS the finding for that allele
            missing.append(a)
            errors[a] = f"{type(e).__name__}: {e}"
            continue
        with open(out_csv) as fh:
            fh.readline()
            for line in fh:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                try:
                    ic = float(parts[1])
                except ValueError:
                    continue
                calls.append({"peptide": parts[0], "allele": a, "ic50_nM": round(ic, 1)})
    json.dump({
        "_note": ("MHCnuggets class I predicted IC50 for every junction peptide x panel allele. "
                  "The SECOND predictor of predictor_concordance.py; MHCflurry's matrix is "
                  "epitope-allele-matrix.json and the two are never merged."),
        "predictor": "MHCnuggets (class I)", "scale": "predicted IC50, nM",
        "panel": pan, "n_peptides": len(peps),
        "alleles_without_a_model": missing,
        "⚠_missing_model_is_not_a_negative": (
            "An allele listed above was not scored at all. It is excluded from every comparison "
            "denominator and must never be counted as an allele that failed to present."),
        "model_errors": errors,
        "calls": sorted(calls, key=lambda c: (c["ic50_nM"], c["allele"], c["peptide"])),
    }, open(NUG_MATRIX, "w"), indent=2)
    print(f"  mhcnuggets: {len(calls)} calls over {len(pan) - len(missing)}/{len(pan)} alleles "
          f"({len(missing)} without a model)", file=sys.stderr)
    return 0


def do_curve():
    import hla_coverage as hc
    if not os.path.exists(NUG_MATRIX):
        print("  epitope-allele-matrix-mhcnuggets.json absent; run --predict first", file=sys.stderr)
        return 1
    m = json.load(open(NUG_MATRIX))
    calls, missing = m["calls"], set(m["alleles_without_a_model"])
    scored = [a for a in m["panel"] if a not in missing]

    alleles = sorted({c["allele"] for c in calls})
    resolve = hc.build_region_resolver(hc.fetch(hc.ISO_JSON_URL))
    freqs, _r, source_ok, _u = hc.load_afnd(alleles, resolve)
    if not source_ok:
        print("  AFND mirror unavailable; nothing written rather than fabricated", file=sys.stderr)
        return 1

    rows = []
    for t in IC50_GRID:
        present = sorted({c["allele"] for c in calls if c["ic50_nM"] <= t})
        cov, _ci, used = hc.coverage_with_ci({a: freqs[a] for a in present})
        rows.append({"ic50_nM": t, "n_presenting_alleles": len(used),
                     "coverage": cov if cov is not None else 0.0, "alleles": used})

    at_conv = next(r for r in rows if r["ic50_nM"] == IC50_STRONG)
    nug_set = set(at_conv["alleles"])

    flurry = json.load(open(FLURRY_CURVE)) if os.path.exists(FLURRY_CURVE) else None
    fl_conv = (flurry or {}).get("at_conventional_threshold") or {}
    fl_set = set(fl_conv.get("alleles", []))
    # ⚠ Only alleles BOTH predictors could score may be compared. An allele MHCnuggets has no model
    # for is not evidence either way, and leaving it in would let a missing model read as a
    # disagreement — or, worse, as an agreement.
    comparable = set(scored)
    a_only, b_only = (fl_set & comparable) - nug_set, nug_set - fl_set
    agree = (fl_set & comparable) & nug_set

    result = {
        "_what": ("Coverage vs. acceptance threshold under a SECOND, independently trained class I "
                  "predictor (MHCnuggets, IC50 nM), beside the same curve under MHCflurry "
                  "(presentation percentile)."),
        "_why": ("aiXiv review 1365 (W2): the manuscript's threshold sensitivity may be an artifact "
                 "of one software suite. If it reproduces under an independent predictor it is a "
                 "property of the junction; if not, the paper's own result is about MHCflurry."),
        "⛔_what_this_is_not": (
            "Not a validation of either predictor and not evidence of presentation. Two prediction "
            "tools agreeing are still two prediction tools; concordance narrows the space of "
            "software-specific artifacts and does nothing else. The scales are NOT rescaled onto "
            "one axis — each predictor is swept over its own conventional cut and the SHAPES are "
            "compared, because a forced rescaling would manufacture the agreement it reports."),
        "_method": (f"MHCnuggets class I IC50 over the same peptides and panel; coverage at each "
                    f"cut = 1 - prod(1-af)^2 over presenting alleles via hla_coverage, the same "
                    f"formula and pooled AFND frequencies the manuscript uses. Conventional cuts: "
                    f"{IC50_STRONG} nM here, 0.5 presentation percentile for MHCflurry."),
        "_sources": [hc.AFND_CITATION],
        "n_panel": len(m["panel"]),
        "n_alleles_scored_by_both": len(comparable),
        "alleles_without_an_mhcnuggets_model": sorted(missing),
        "mhcnuggets": {"conventional_cut_nM": IC50_STRONG, "at_conventional_cut": at_conv,
                       "curve": rows},
        "mhcflurry": {"conventional_cut_percentile": (flurry or {}).get("conventional_threshold"),
                      "at_conventional_cut": fl_conv,
                      "steps": (flurry or {}).get("steps")},
        "agreement_at_each_predictors_own_cut": {
            "presenting_in_both": sorted(agree),
            "mhcflurry_only": sorted(a_only),
            "mhcnuggets_only": sorted(b_only),
            "⚠_scope": ("computed over the alleles BOTH predictors could score; alleles without an "
                        "MHCnuggets model are excluded from every count here, not scored as absent"),
        },
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"  concordance: MHCnuggets presents on {len(nug_set)} allele(s) at {IC50_STRONG} nM; "
          f"MHCflurry on {len(fl_set)} at its own cut; {len(agree)} in both, "
          f"{len(a_only)} flurry-only, {len(b_only)} nuggets-only", file=sys.stderr)
    return 0


def main(argv):
    if "--predict" in argv:
        return do_predict()
    if "--curve" in argv:
        return do_curve()
    print("usage: predictor_concordance.py --predict | --curve", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
