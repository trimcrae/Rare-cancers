#!/usr/bin/env python3
"""Compartment-readability census for the three committed EMC expression instruments.

QUESTION IT ANSWERS (and the only one):
  For a pre-specified panel of compartment markers -- the cell lineages and matrix-turnover
  genes any statement about "what an agent can reach in this tumour" would have to rest on --
  which markers are actually MEASURABLE on each EMC expression instrument this repository
  holds, and is a compartment FRACTION even mathematically derivable from that instrument's
  value kind?

WHAT IT IS NOT:
  * Not a deconvolution. No compartment fraction is estimated anywhere.
  * Not an arm-to-arm statistic. No EMC-vs-comparator contrast, score, p-value or effect size
    is computed. Lane 2 is closed on this substrate (COMMON-BRIEF 2026-09-08T04:38Z:
    "Do not dispatch further lane-2 statistics on emc-expression-panels.json"), and this
    script deliberately reads only gene IDENTITY and per-instrument metadata, never a value.
  * Not a delivery, accessibility, efficacy, selectivity or therapeutic-window claim.
    Marker readability is a property of the instrument, not of the tumour.

INPUTS (all committed, read-only, live checkout):
  research/modalities/emc-expression-panels-inputs.json   GSE24369/GPL6244 and GSE4303/GPL3290
                                                          retained gene extract + value_kind
  research/modalities/emc-fourth-cohort-gene-counts.tsv    PRJNA1357027/SRP640302 TempO-Seq,
                                                          gene rows = the whole instrument
  research/modalities/emc-fourth-cohort-quant.json         units / assay description
"""
import json
import csv
import os
import sys
import hashlib

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))

# ---------------------------------------------------------------------------
# Pre-specified compartment panels. Author-specified from standard lineage
# markers; NOT drawn from any signature database and NOT tuned to the data --
# the panels were written before any file was opened, and no marker was added
# or dropped after seeing coverage. Each panel names the compartment question
# it stands for.
# ---------------------------------------------------------------------------
PANELS = {
    "endothelial": {
        "question": "is there vasculature, and how much of the tissue is vessel",
        "genes": ["PECAM1", "CDH5", "VWF", "KDR", "TEK", "ENG", "ESAM", "CLDN5",
                  "FLT1", "ROBO4", "EMCN"],
    },
    "mural_pericyte": {
        "question": "are the vessels invested (a determinant of what leaves them)",
        "genes": ["RGS5", "ACTA2", "PDGFRB", "MCAM", "NOTCH3", "CSPG4", "MYH11"],
    },
    "immune": {
        "question": "is there an immune compartment inside the matrix at all",
        "genes": ["PTPRC", "CD68", "CD163", "CD3E", "CD2", "ITGAM", "AIF1",
                  "CSF1R", "LYZ", "MS4A1"],
    },
    "fibroblast_stromal": {
        "question": "how much of the signal is non-tumour stromal cell",
        "genes": ["COL1A1", "COL1A2", "COL3A1", "FAP", "THY1", "PDGFRA",
                  "LUM", "DCN", "POSTN"],
    },
    "hyaluronan_matrix_turnover": {
        "question": "the myxoid matrix's own synthesis and degradation",
        "genes": ["HAS1", "HAS2", "HAS3", "HYAL1", "HYAL2", "CD44", "VCAN",
                  "ACAN", "HAPLN1", "HAPLN3", "TNFAIP6"],
    },
    "transport_barrier": {
        "question": "water/solute handling and caveolar transcytosis",
        "genes": ["AQP1", "AQP4", "CAV1", "CAV2", "SLC2A1"],
    },
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out = {
        "_title": "Compartment-readability census across the committed EMC expression instruments",
        "_what_this_measures": (
            "Per instrument, which pre-specified compartment markers are measurable, and "
            "whether a compartment FRACTION is derivable from that instrument's value kind. "
            "No expression value is read; no arm contrast is computed."
        ),
        "_what_this_cannot_settle": (
            "Nothing about vessel density, perfusion, interstitial pressure, matrix volume "
            "fraction, or what any agent can reach in EMC tissue. Marker readability bounds "
            "what a dataset could in principle be asked; it is not a measurement of the tumour."
        ),
        "panels": {k: {"question": v["question"], "n_genes": len(v["genes"]),
                       "genes": v["genes"]} for k, v in PANELS.items()},
        "instruments": {},
    }

    # --- arrays ------------------------------------------------------------
    p_in = os.path.join(REPO, "research/modalities/emc-expression-panels-inputs.json")
    d = json.load(open(p_in))
    wanted = set(d["genes_wanted"])
    for tname, t in d["targets"].items():
        measured = set(t["genes"])
        rec = {
            "source_file": "research/modalities/emc-expression-panels-inputs.json",
            "accession": t["gse"],
            "platform": t["platform"],
            "n_samples": t["n_samples"],
            "n_probes_on_platform": t["n_probes"],
            "value_kind_verbatim": t["value_kind"],
            "coverage_universe": (
                "RETAINED EXTRACT ONLY. The platform is genome-wide; this repository holds "
                "values for the %d genes a prior panel asked for, of which %d resolved here. "
                "A marker absent below is absent FROM THE RETAINED EXTRACT, which is not a "
                "statement that the platform cannot measure it." % (len(wanted), len(measured))
            ),
            "panels": {},
        }
        for pname, p in PANELS.items():
            have = [g for g in p["genes"] if g in measured]
            miss = [g for g in p["genes"] if g not in measured]
            rec["panels"][pname] = {
                "n_readable": len(have), "n_in_panel": len(p["genes"]),
                "readable": have, "not_in_retained_extract": miss,
            }
        out["instruments"][tname] = rec

    # --- fourth cohort (TempO-Seq targeted panel) --------------------------
    p_tsv = os.path.join(REPO, "research/modalities/emc-fourth-cohort-gene-counts.tsv")
    p_q = os.path.join(REPO, "research/modalities/emc-fourth-cohort-quant.json")
    q = json.load(open(p_q))
    with open(p_tsv) as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    header, body = rows[0], rows[1:]
    genes4 = set(r[0] for r in body)
    rec = {
        "source_file": "research/modalities/emc-fourth-cohort-gene-counts.tsv",
        "accession": "%s / %s" % (q.get("bioproject"), q.get("sra_study")),
        "platform": q.get("depositor_assay_description"),
        "n_samples": len(header) - 1,
        "n_genes_on_instrument": len(genes4),
        "gene_counts_sha256_recorded": q.get("gene_counts_sha256"),
        "gene_counts_sha256_measured": sha256(p_tsv),
        "units_verbatim": q.get("⛔ gene_counts_units"),
        "coverage_universe": (
            "WHOLE INSTRUMENT. This is a targeted panel: the %d gene rows are everything the "
            "assay can report. A marker absent below is absent FROM THE ASSAY -- an instrument "
            "fact, not a retention artefact." % len(genes4)
        ),
        "panels": {},
    }
    for pname, p in PANELS.items():
        have = [g for g in p["genes"] if g in genes4]
        miss = [g for g in p["genes"] if g not in genes4]
        rec["panels"][pname] = {
            "n_readable": len(have), "n_in_panel": len(p["genes"]),
            "readable": have, "absent_from_instrument": miss,
        }
    out["instruments"]["PRJNA1357027_TempO-Seq"] = rec

    # --- roll-up -----------------------------------------------------------
    tot = sum(len(p["genes"]) for p in PANELS.values())
    out["summary"] = {
        "n_markers_prespecified": tot,
        "per_instrument_total_readable": {
            k: sum(v["panels"][pn]["n_readable"] for pn in PANELS)
            for k, v in out["instruments"].items()
        },
        "readable_on_every_instrument": sorted(
            set.intersection(*[
                set(g for pn in PANELS for g in v["panels"][pn]["readable"])
                for v in out["instruments"].values()])),
    }
    out["summary"]["readable_on_no_instrument"] = sorted(
        set(g for p in PANELS.values() for g in p["genes"])
        - set(g for v in out["instruments"].values()
              for pn in PANELS for g in v["panels"][pn]["readable"]))

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "compartment-readability-census.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote", dst)
    print(json.dumps(out["summary"], indent=2))
    for k, v in out["instruments"].items():
        print("\n==", k, "|", v.get("platform"), "| n_samples", v["n_samples"])
        print("   universe:", v["coverage_universe"][:120])
        for pn in PANELS:
            pp = v["panels"][pn]
            print("   %-28s %d/%d" % (pn, pp["n_readable"], pp["n_in_panel"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
