#!/usr/bin/env python3
"""
Is the ATR axis a SELECTIVE dependency of FET-fusion sarcomas — and is the ATM axis correspondingly
DISPENSABLE in them? A DepMap transfer prior for EMC.

WHY THIS EXISTS
---------------
Gorthi/Bailey and successors report that FET fusion oncoproteins (EWSR1::FLI1 and, explicitly,
EWSR1::ATF1 in clear cell sarcoma) impair ATM activation at double-strand breaks, leaving the
compensatory ATR axis load-bearing -> ATR inhibitors are synthetic lethal in FET-rearranged cancers
("FET fusion oncoproteins disrupt physiologic DNA repair and create a targetable opportunity for
ATR inhibitor therapy", biorxiv 2023.04.30.538578 / Cancer Res). EMC's three commonest 5' partners
- EWSR1, TAF15, FUS - are the three FET-family genes, so EMC is a FET-rearranged cancer by
construction. That makes ATR inhibition a CLASS hypothesis EMC inherits, with drugs already in
humans, and it needs no NR4A-paralogue selectivity at all.

THE TEST, AND WHY IT IS A DOUBLE PREDICTION (not one delta)
-----------------------------------------------------------
A single gene delta on one axis is a coin flip dressed up as evidence. The mechanism above predicts
BOTH directions at once, over two multi-gene axes:

    (i)  ATR axis  (ATR, ATRIP, CHEK1, TOPBP1, CLSPN, RPA1/2/3) -> MORE essential in FET lines
    (ii) ATM axis  (ATM, MDC1, NBN, MRE11A, RAD50, TP53BP1)     -> NOT more essential, and
                                                                   plausibly LESS, in FET lines
                                                                   (already functionally suppressed)

Only the conjunction is interesting. Either half alone is consistent with a lineage artefact.

WHAT THIS CANNOT DO - read before quoting any number
----------------------------------------------------
1. **CRISPR knockout is not inhibitor sensitivity.** ATR is a common-essential gene: a full KO
   removes the protein in every line, so Chronos measures "how much does this line mind losing ATR
   entirely", not "how much does this line mind ATR being partly inhibited". A synthetic-lethal
   window that a drug would exploit at sub-lethal occupancy can be invisible here, and a
   common-essential floor compresses exactly the differences we are looking for. This scan can
   therefore SUPPORT the hypothesis or fail to see it; it cannot refute it.
2. **EMC is n=0 in DepMap for this scan's purposes.** ⛔ 2026-08-05: the one model DepMap LABELS EMC
   (ACH-001519 / H-EMC-SS) is recorded by Cellosaurus as not carrying an EWSR1 fusion, and DepMap's
   own filtered fusion caller names no FET gene for it (`emc-atr-vulnerability.json` ->
   `part_a_hemcss_identity`, verdict NOT_FUSION_POSITIVE_PER_CURATED_RECORD). ✅ **No number in this
   module rests on it**: the model has no CRISPR gene-effect data, so `fet_ids` (which intersects
   with the CRISPR index) never contained it, `grouping.FET_rearranged.EMC.n_with_crispr` is 0, and
   it is absent from `fet_ids_by_call` because none of its 2 fusion calls names a FET gene. The
   script reports what CRISPR data that model actually has rather than assuming. Every FET
   number below is a transfer prior from OTHER FET sarcomas, never an EMC measurement.
   *(Superseded, retained: "**EMC is n<=1 in DepMap** (ACH-001519 / H-EMC-SS, expression-only per
   this repo's own record).")*
3. **Grouping is reported TWICE and the disagreement is the uncertainty.** The primary grouping is
   string matching on Oncotree disease labels, with the labels seen recorded per group. A second
   grouping is built from DepMap's own `OmicsFusionFiltered.csv` calls (a line is FET-rearranged if a
   filtered call names EWSR1, FUS or TAF15). Neither is authoritative - a called FET fusion is not
   automatically the oncogenic driver fusion, and a disease label is not a genotype - so both are
   emitted and their overlap is counted rather than one being trusted silently.

Output: fet-ddr-axis-scan.json. Internet required (figshare/DepMap) -> runs in CI, not the sandbox.
"""

import io
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fet-ddr-axis-scan.json")

sys.path.insert(0, HERE)
from depmap_sarcoma_dependency import (  # noqa: E402  (shares the release discovery + fetch)
    DEPENDENT_THRESHOLD,
    _download,
    _get,
    discover_depmap_files,
)

# --- the two axes, and what each gene is doing there ---------------------------------------------
ATR_AXIS = ["ATR", "ATRIP", "CHEK1", "TOPBP1", "CLSPN", "RPA1", "RPA2", "RPA3"]
ATM_AXIS = ["ATM", "MDC1", "NBN", "MRE11A", "MRE11", "RAD50", "TP53BP1"]
# Neighbouring DDR nodes that are drugged in the clinic; reported, not part of the double prediction.
OTHER_DDR = ["WEE1", "CHEK2", "PRKDC", "PARP1", "POLQ", "RAD51", "USP1", "PKMYT1"]
# Controls: a pan-essential floor, a known-dispensable gene, and the fusion context genes.
# NOTE POLR2A and PRKDC are NOT in the 24Q4 CRISPRGeneEffect column set (measured, not assumed —
# they came back absent on run 30848356798), so the pan-essential control is RPL5, which is.
PAN_ESSENTIAL_CONTROL = "RPL5"
NEAR_NEUTRAL_CONTROL = "ATM"
CONTEXT = ["POLR2A", "RPL5", "NR4A3", "EWSR1", "TAF15", "FUS", "FLI1", "ATF1", "DDIT3", "WT1"]

# --- the SECOND instrument: ATR-INHIBITOR sensitivity, not ATR knockout -------------------------
# The source paper's own DepMap analysis used elimusertib sensitivity across 880 lines and split it
# only as "Ewing vs non-Ewing". Re-cutting the same public data by FET status - so clear cell
# sarcoma, DSRCT and myxoid liposarcoma sit with Ewing rather than in the comparator - is the free
# analysis that is NOT in the paper, and it is the one that decides whether the class claim EMC
# would inherit is really partner-agnostic or really a Ewing effect.
ATRI_NAMES = ["elimusertib", "bay-1895344", "bay1895344", "ceralasertib", "azd6738", "azd-6738",
              "berzosertib", "vx-970", "m6620", "ve-822", "ve-821", "az20", "camonsertib",
              "rp-3500", "gartisertib", "m4344", "atrn-119", "art0380"]
# Comparator drug classes, so an "everything is more sensitive in FET lines" artefact is visible.
CONTROL_DRUG_NAMES = ["doxorubicin", "paclitaxel", "olaparib", "talazoparib", "adavosertib",
                      "az-d1775", "mk-1775", "prexasertib", "trabectedin", "bortezomib",
                      "carfilzomib", "pazopanib", "sunitinib"]

ALL_GENES = sorted(set(ATR_AXIS) | set(ATM_AXIS) | set(OTHER_DDR) | set(CONTEXT))

# FET-rearranged sarcoma subtypes that DepMap actually carries, matched on Oncotree labels.
# Each entry: group label -> (regex-ish substring, the FET fusion it stands for).
FET_SUBTYPES = {
    "Ewing": ("ewing", "EWSR1::FLI1 / EWSR1::ERG"),
    "clear_cell_sarcoma": ("clear cell sarcoma", "EWSR1::ATF1"),
    "myxoid_liposarcoma": ("myxoid", "FUS::DDIT3 / EWSR1::DDIT3"),
    "DSRCT": ("desmoplastic small round", "EWSR1::WT1"),
    "EMC": ("extraskeletal myxoid chondrosarcoma", "EWSR1::NR4A3 (the disease itself)"),
}
# Non-FET sarcoma comparator subtypes (fusion-driven or not, but NOT FET-rearranged).
NON_FET_SARCOMA_SUBTYPES = {
    "synovial": ("synovial", "SS18::SSX"),
    "rhabdomyosarcoma": ("rhabdomyosarcoma", "PAX3::FOXO1 or fusion-negative"),
    "osteosarcoma": ("osteosarcoma", "complex karyotype"),
    "leiomyosarcoma": ("leiomyosarcoma", "complex karyotype"),
    "rhabdoid": ("rhabdoid", "SMARCB1 loss"),
    "chondrosarcoma": ("chondrosarcoma", "IDH1/2 (conventional)"),
}
# The model DepMap LABELS 'Extraskeletal Myxoid Chondrosarcoma'. ⚠ NOT confirmed EMC: the curated
# record contradicts the fusion label (see the module docstring, point 2). Kept under this name
# because the question it answers -- "does that model have CRISPR data?" -- is about the model, not
# about EMC. Superseded, retained: "H-EMC-SS, per this repo's IDEAS.md correction of 2026-07-03".
EMC_MODEL_ID = "ACH-001519"


def _label_col(model):
    for c in ("OncotreeSubtype", "OncotreePrimaryDisease", "lineage"):
        if c in model.columns:
            return c
    return model.columns[-1]


def _ids_matching(model, col, needle):
    hit = model[col].astype(str).str.contains(needle, case=False, na=False)
    return set(model.index[hit])


def _axis_stats(ge, ids, genes, label):
    """Mean gene effect over an axis, per line then averaged, plus the per-gene breakdown."""
    present = [g for g in genes if g in ge.columns]
    rows = ge.reindex([i for i in ge.index if i in ids])[present].dropna(how="all")
    if rows.empty or not present:
        return {"group": label, "n_lines": 0, "_status": "no lines or no genes in release"}
    per_line = rows.mean(axis=1)            # each line's mean over the axis
    per_gene = {g: round(float(rows[g].dropna().mean()), 4) for g in present
                if rows[g].notna().any()}
    return {
        "group": label,
        "n_lines": int(len(per_line)),
        "genes_used": present,
        "axis_mean_gene_effect": round(float(per_line.mean()), 4),
        "axis_sd_across_lines": round(float(per_line.std(ddof=1)), 4) if len(per_line) > 1 else None,
        "frac_lines_dependent_on_axis": round(float((per_line < DEPENDENT_THRESHOLD).mean()), 3),
        "per_gene_mean": per_gene,
    }


def _welch(a, b):
    """Welch t statistic + df for two small samples. No scipy in this lane; report t and df only,
    never a p-value we cannot compute exactly."""
    import math
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    if va == 0 and vb == 0:
        return None
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return None
    t = (ma - mb) / se
    num = (va / na + vb / nb) ** 2
    den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    return {"t": round(t, 3), "df": round(num / den, 1) if den else None,
            "mean_a": round(ma, 4), "mean_b": round(mb, 4),
            "delta_a_minus_b": round(ma - mb, 4)}


def _fet_by_fusion_call(pd, article_ids, crispr_index):
    """Group lines by the fusion DepMap actually CALLED, not by their disease label.

    Limit 3 of the module docstring was that grouping is string matching on Oncotree labels. It does
    not have to be: `OmicsFusionFiltered.csv` is in both known releases (measured, run 30848796748).
    A line is FET-rearranged if a filtered fusion call names EWSR1, FUS or TAF15 on either side.
    Reported ALONGSIDE the label grouping so the two can disagree visibly rather than silently."""
    out = {"_what": "FET status from DepMap's own filtered fusion calls, not from disease labels"}
    for label, aid in article_ids:
        try:
            files = {f["name"]: f["download_url"]
                     for f in json.loads(_get(f"https://api.figshare.com/v2/articles/{aid}"))
                     .get("files", [])}
        except Exception:  # noqa: BLE001
            continue
        if "OmicsFusionFiltered.csv" not in files:
            continue
        try:
            path = _download(files["OmicsFusionFiltered.csv"], timeout=900)
            fus = pd.read_csv(path)
        except Exception as exc:  # noqa: BLE001
            out["_error"] = f"{label}: {exc}"
            continue
        mid = next((c for c in fus.columns if c in ("ModelID", "DepMap_ID", "SampleID")), None)
        name_c = next((c for c in fus.columns if c.lower() in ("fusionname", "fusion_name")), None)
        if not mid or not name_c:
            out["_error"] = f"{label}: columns {list(fus.columns)[:8]}"
            continue
        fet_hits, partners = {}, {}
        for _, r in fus[[mid, name_c]].dropna().iterrows():
            parts = str(r[name_c]).replace("::", "--").split("--")
            genes = [p.split("(")[0].strip().upper() for p in parts]
            hit = [g for g in genes if g in ("EWSR1", "FUS", "TAF15")]
            if hit:
                fet_hits.setdefault(str(r[mid]), set()).update(hit)
                partners.setdefault(str(r[mid]), set()).add(str(r[name_c]))
        ids = set(fet_hits) & set(crispr_index)
        out.update({
            "source_release": label,
            "n_models_with_a_FET_fusion_call": len(fet_hits),
            "n_of_those_with_crispr": len(ids),
            "model_ids_with_crispr": sorted(ids),
            "_caveat": "a called EWSR1/FUS/TAF15 fusion is not automatically the ONCOGENIC driver "
                       "fusion — read this as a wider, noisier grouping than the label one, and use "
                       "the disagreement between the two as the uncertainty, not either alone",
        })
        out["_fet_ids"] = sorted(ids)
        return out
    out["_status"] = "no OmicsFusionFiltered.csv in any known release"
    return out


# Where drug-sensitivity data actually lives. Measured, not assumed: run 30849351348 showed the
# quarterly figshare releases carry no drug matrix (73 and 52 files, all CRISPR/omics), and figshare's
# search endpoint returns unrelated articles for every PRISM term tried. GDSC publishes static bulk
# files instead, and GDSC2 contains ATR inhibitors, so that is the instrument to use.
GDSC_CANDIDATES = [
    ("GDSC2_8.5_27Oct23", "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/"
                          "GDSC2_fitted_dose_response_27Oct23.xlsx"),
    ("GDSC2_8.4_25Feb20", "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.4/"
                          "GDSC2_fitted_dose_response_25Feb20.xlsx"),
    ("GDSC1_8.5_27Oct23", "https://cog.sanger.ac.uk/cancerrxgene/GDSC_release8.5/"
                          "GDSC1_fitted_dose_response_27Oct23.xlsx"),
]


def _gdsc_atri_read(pd, model, fet_ids, comparator_ids):
    """ATR-INHIBITOR sensitivity from GDSC, re-cut by FET status.

    Sign convention is explicit and load-bearing: GDSC reports LN_IC50, so **LOWER = MORE SENSITIVE**,
    and a NEGATIVE delta (FET minus comparator) is the direction the hypothesis predicts. Control
    drugs are read through the identical path so an 'FET lines are sensitive to everything' artefact
    is visible rather than inferred."""
    out = {"_instrument": "GDSC LN_IC50 — ATR-INHIBITOR sensitivity, not ATR knockout",
           "_sign": "LN_IC50: LOWER = MORE SENSITIVE. delta_a_minus_b < 0 == FET lines more sensitive.",
           "_attempts": []}
    # DepMap ModelID -> Sanger/COSMIC identifiers, so GDSC rows can be mapped onto our groups.
    sanger_col = next((c for c in model.columns if c.lower() in ("sangermodelid", "sanger_model_id")),
                      None)
    cosmic_col = next((c for c in model.columns if c.lower() in ("cosmicid", "cosmic_id")), None)
    if not sanger_col and not cosmic_col:
        out["_status"] = f"no Sanger/COSMIC id column in Model.csv: {list(model.columns)[:12]}"
        return out
    fet_keys, comp_keys = set(), set()
    for mid in model.index:
        for col, cast in ((sanger_col, str), (cosmic_col, lambda v: str(int(float(v))))):
            if not col:
                continue
            try:
                key = cast(model.loc[mid, col])
            except Exception:  # noqa: BLE001
                continue
            if key in ("nan", "None", ""):
                continue
            (fet_keys if mid in fet_ids else comp_keys if mid in comparator_ids else set()).add(key)

    for label, url in GDSC_CANDIDATES:
        try:
            path = _download(url, timeout=1800)
            df = pd.read_excel(path)
        except Exception as exc:  # noqa: BLE001
            out["_attempts"].append({"source": label, "error": str(exc)[:200]})
            continue
        cols = {c.upper(): c for c in df.columns}
        drug_c = cols.get("DRUG_NAME")
        ic_c = cols.get("LN_IC50")
        key_cs = [cols[k] for k in ("SANGER_MODEL_ID", "COSMIC_ID", "CELL_LINE_NAME") if k in cols]
        if not (drug_c and ic_c and key_cs):
            out["_attempts"].append({"source": label, "error": f"columns {list(df.columns)[:10]}"})
            continue
        df["_key"] = df[key_cs[0]].astype(str)
        if len(key_cs) > 1:
            alt = df[key_cs[1]].map(lambda v: str(int(v)) if pd.notna(v) else "")
            df["_key2"] = alt
        # ⭑ GENERAL-SENSITIVITY CORRECTION. A line that is simply easy to kill is more sensitive to
        # everything, and FET-rearranged lines (Ewing especially) are fast-growing and broadly
        # chemosensitive in vitro — so a raw LN_IC50 contrast measures growth rate as much as biology.
        # Subtracting each line's own median LN_IC50 across ALL GDSC drugs leaves the drug-specific
        # residual, which is the quantity the hypothesis is actually about.
        line_median = df.groupby("_key")[ic_c].median()
        df["_resid"] = df[ic_c] - df["_key"].map(line_median)
        by_drug = {}
        names = df[drug_c].astype(str).str.lower()
        for want in ATRI_NAMES + CONTROL_DRUG_NAMES:
            sub = df[names.str.contains(want, regex=False, na=False)]
            if sub.empty:
                continue
            keys = set(sub["_key"]) | (set(sub["_key2"]) if "_key2" in sub else set())
            a = [float(v) for k, v in zip(sub["_key"], sub[ic_c]) if k in fet_keys]
            b = [float(v) for k, v in zip(sub["_key"], sub[ic_c]) if k in comp_keys]
            if "_key2" in sub:
                a += [float(v) for k, v in zip(sub["_key2"], sub[ic_c]) if k in fet_keys]
                b += [float(v) for k, v in zip(sub["_key2"], sub[ic_c]) if k in comp_keys]
            ra = [float(v) for k, v in zip(sub["_key"], sub["_resid"]) if k in fet_keys]
            rb = [float(v) for k, v in zip(sub["_key"], sub["_resid"]) if k in comp_keys]
            if "_key2" in sub:
                ra += [float(v) for k, v in zip(sub["_key2"], sub["_resid"]) if k in fet_keys]
                rb += [float(v) for k, v in zip(sub["_key2"], sub["_resid"]) if k in comp_keys]
            by_drug[want] = {"is_atr_inhibitor": want in ATRI_NAMES,
                             "n_rows": int(len(sub)), "n_FET": len(a), "n_comparator": len(b),
                             "keys_seen": len(keys),
                             "welch_raw_ln_ic50": _welch(a, b),
                             "welch_line_median_corrected": _welch(ra, rb)}
        if not any(v["is_atr_inhibitor"] and v.get("welch_raw_ln_ic50") for v in by_drug.values()):
            out["_attempts"].append({"source": label, "n_rows": int(df.shape[0]),
                                     "error": "no ATR inhibitor with a computable contrast",
                                     "drugs_matched": sorted(by_drug)})
            continue
        out.update({"_status": "read", "source": label, "n_rows": int(df.shape[0]),
                    "n_FET_keys": len(fet_keys), "n_comparator_keys": len(comp_keys),
                    "by_drug": by_drug,
                    "_reading": "Read the CONTROL drugs first, and quote the LINE-MEDIAN-CORRECTED contrast, never the raw one. A negative delta across ATR inhibitors AND controls alike in the RAW numbers is a growth-rate or lineage artefact, which is exactly what run 30849750035 found: talazoparib -2.34 and olaparib -1.28 against azd6738 -0.76. The corrected column removes each line's own general drug sensitivity and is what the hypothesis is actually about."})
        return out
    out["_status"] = "no GDSC release yielded an ATR-inhibitor contrast; see _attempts"
    return out


def _figshare_search(terms, page_size=25):
    """Find figshare articles whose title matches a term. The PRISM / Repurposing drug matrices are
    SEPARATE articles from the quarterly CRISPR release — measured on run 30848796748, whose recorded
    inventory of 24Q4 (73 files) and 23Q2 (52 files) contains no drug-sensitivity file at all."""
    found = {}
    for term in terms:
        try:
            arts = json.loads(_get(
                f"https://api.figshare.com/v2/articles?search_for={urllib.parse.quote(term)}"
                f"&page_size={page_size}&order=published_date&order_direction=desc"))
        except Exception as exc:  # noqa: BLE001
            found[term] = [f"_error: {exc}"]
            continue
        found[term] = [{"id": a.get("id"), "title": a.get("title"),
                        "published": a.get("published_date")} for a in arts]
    return found


def _figshare_inventory(article_ids):
    """Every file name each known DepMap release exposes. A diagnostic, not a guess: if the drug
    matrix cannot be found, the JSON says what WAS on offer instead of reporting 'unavailable'."""
    inv = {}
    for label, aid in article_ids:
        try:
            files = json.loads(_get(f"https://api.figshare.com/v2/articles/{aid}")).get("files", [])
            inv[f"{label}:{aid}"] = sorted(f["name"] for f in files)
        except Exception as exc:  # noqa: BLE001
            inv[f"{label}:{aid}"] = [f"_error: {exc}"]
    return inv


def _find_drug_files(inv):
    """Pick (matrix, metadata) file names that look like a PRISM / Repurposing / OncRef screen."""
    want_matrix = ("repurposing", "prism", "oncref", "drug_sensitivity", "log2fc", "auc", "viability")
    hits = {}
    for src, names in inv.items():
        for n in names:
            low = n.lower()
            if low.endswith((".csv", ".csv.gz")) and any(w in low for w in want_matrix):
                hits.setdefault(src, []).append(n)
    return hits


def _drug_sensitivity_read(pd, inv, releases, fet_ids, comparator_ids, ge_index):
    """Best-effort second instrument. Returns a dict that ALWAYS says what it managed to read."""
    out = {"_instrument": "ATR-INHIBITOR sensitivity (PRISM-class drug screen), NOT ATR knockout — "
                          "the readout the source paper used and the one a CRISPR KO cannot give",
           "candidate_files": _find_drug_files(inv)}
    if not out["candidate_files"]:
        out["_status"] = ("no PRISM/Repurposing/OncRef-looking file in the release inventory below; "
                          "the inventory is recorded so the next attempt starts from fact")
        return out
    # Try each candidate matrix + its sibling metadata until one yields an ATR-inhibitor column.
    for src, names in out["candidate_files"].items():
        label, aid = src.split(":")
        try:
            files = {f["name"]: f["download_url"]
                     for f in json.loads(_get(f"https://api.figshare.com/v2/articles/{aid}"))
                     .get("files", [])}
        except Exception as exc:  # noqa: BLE001
            out.setdefault("_attempts", []).append({"source": src, "error": str(exc)})
            continue
        meta_name = next((n for n in files
                          if "meta" in n.lower() and ("compound" in n.lower()
                                                      or "treatment" in n.lower()
                                                      or "drug" in n.lower())), None)
        for mat_name in names:
            try:
                path = _download(files[mat_name], timeout=1800)
                header = list(pd.read_csv(path, nrows=0).columns)
            except Exception as exc:  # noqa: BLE001
                out.setdefault("_attempts", []).append({"source": src, "file": mat_name,
                                                        "error": str(exc)})
                continue
            # Column ids may be compound names or opaque ids resolved through the metadata file.
            name_by_col = {c: c for c in header[1:]}
            if meta_name:
                try:
                    meta = pd.read_csv(io.BytesIO(_get(files[meta_name], timeout=600)))
                    id_c = next((c for c in meta.columns if c.lower() in
                                 ("column_name", "sample_id", "broad_id", "iemcompoundid",
                                  "compoundid", "drug_id")), meta.columns[0])
                    nm_c = next((c for c in meta.columns if c.lower() in
                                 ("name", "drug_name", "compoundname", "compound_name")), None)
                    if nm_c:
                        name_by_col = {str(r[id_c]): str(r[nm_c]) for _, r in meta.iterrows()}
                except Exception as exc:  # noqa: BLE001
                    out.setdefault("_attempts", []).append({"source": src, "meta": meta_name,
                                                            "error": str(exc)})

            def _match(namelist):
                got = {}
                for col in header[1:]:
                    nm = str(name_by_col.get(col, col)).lower()
                    for want in namelist:
                        if want in nm:
                            got.setdefault(want, []).append(col)
                return got

            atri_cols = _match(ATRI_NAMES)
            if not atri_cols:
                out.setdefault("_attempts", []).append(
                    {"source": src, "file": mat_name, "n_cols": len(header) - 1,
                     "error": "no ATR-inhibitor column matched"})
                continue
            ctrl_cols = _match(CONTROL_DRUG_NAMES)
            use = sorted({c for cols in atri_cols.values() for c in cols} |
                         {c for cols in ctrl_cols.values() for c in cols})
            df = pd.read_csv(path, usecols=[header[0]] + use, index_col=0)
            res = {}
            for want, cols in list(atri_cols.items()) + list(ctrl_cols.items()):
                vals = df[cols].mean(axis=1).dropna()
                a = [float(v) for i, v in vals.items() if i in fet_ids]
                b = [float(v) for i, v in vals.items() if i in comparator_ids]
                res[want] = {"n_FET": len(a), "n_comparator": len(b),
                             "is_atr_inhibitor": want in ATRI_NAMES,
                             "welch": _welch(a, b)}
            out.update({"_status": "read", "source": src, "matrix_file": mat_name,
                        "metadata_file": meta_name, "n_lines_in_matrix": int(df.shape[0]),
                        "n_lines_also_in_crispr": len(set(df.index) & set(ge_index)),
                        "by_drug": res,
                        "_reading": "The score's SIGN convention is dataset-specific (log2 fold "
                                    "change / AUC: LOWER = more sensitive). Read delta_a_minus_b "
                                    "with that in mind, and read the control drugs FIRST: if FET "
                                    "lines look more sensitive to everything, nothing here is "
                                    "about ATR."})
            return out
    out["_status"] = "candidate files found but none yielded an ATR-inhibitor column; see _attempts"
    return out


def main():
    try:
        import pandas as pd
    except ImportError:
        json.dump({"_status": "pandas missing"}, open(OUT, "w"), indent=2)
        print("pandas missing", file=sys.stderr)
        return 0

    urls = discover_depmap_files()
    release = urls.get("release", "unknown")

    model = pd.read_csv(io.BytesIO(_get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    model = model.set_index(id_col)
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    lab_col = _label_col(model)

    crispr_path = _download(urls["CRISPRGeneEffect.csv"], timeout=900)
    cols = list(pd.read_csv(crispr_path, nrows=0).columns)
    idx_col = cols[0]
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in set(ALL_GENES)}
    ge = pd.read_csv(crispr_path, usecols=[idx_col] + list(keep.values()), index_col=0)
    ge.columns = [c.split(" (")[0] for c in ge.columns]

    sarcoma_ids = set(model.index[model[lin_col].isin(["Soft Tissue", "Bone"])])

    # ---- group membership, reported so the grouping is auditable ---------------------------------
    fet_groups, fet_ids = {}, set()
    for name, (needle, fusion) in FET_SUBTYPES.items():
        ids = _ids_matching(model, lab_col, needle) & set(ge.index)
        fet_groups[name] = {
            "oncotree_match": needle, "fusion": fusion,
            "n_with_crispr": len(ids),
            "labels_seen": sorted({str(model.loc[i, lab_col]) for i in ids})[:6],
        }
        fet_ids |= ids
    nonfet_groups, nonfet_ids = {}, set()
    for name, (needle, driver) in NON_FET_SARCOMA_SUBTYPES.items():
        ids = (_ids_matching(model, lab_col, needle) & set(ge.index) & sarcoma_ids) - fet_ids
        nonfet_groups[name] = {"oncotree_match": needle, "driver": driver,
                               "n_with_crispr": len(ids)}
        nonfet_ids |= ids
    other_sarcoma_ids = (sarcoma_ids & set(ge.index)) - fet_ids - nonfet_ids
    nonsarcoma_ids = set(ge.index) - sarcoma_ids

    # ---- the EMC line itself: does it have CRISPR data at all? (an open repo question, $0) --------
    emc = {"model_id": EMC_MODEL_ID,
           "in_model_metadata": bool(EMC_MODEL_ID in model.index),
           "has_crispr_gene_effect": bool(EMC_MODEL_ID in ge.index)}
    if emc["in_model_metadata"]:
        emc["oncotree_label"] = str(model.loc[EMC_MODEL_ID, lab_col])
        emc["lineage"] = str(model.loc[EMC_MODEL_ID, lin_col])
    if emc["has_crispr_gene_effect"]:
        emc["atr_axis_mean"] = round(float(ge.loc[EMC_MODEL_ID, [g for g in ATR_AXIS
                                                                if g in ge.columns]].mean()), 4)
        emc["atm_axis_mean"] = round(float(ge.loc[EMC_MODEL_ID, [g for g in ATM_AXIS
                                                                if g in ge.columns]].mean()), 4)

    # ---- the double prediction --------------------------------------------------------------------
    def per_line_axis(ids, genes):
        present = [g for g in genes if g in ge.columns]
        rows = ge.reindex([i for i in ge.index if i in ids])[present].dropna(how="all")
        return [float(v) for v in rows.mean(axis=1).dropna()]

    comparators = {
        "non_FET_sarcoma": nonfet_ids | other_sarcoma_ids,
        "all_non_sarcoma": nonsarcoma_ids,
    }
    axes = {"ATR_axis": ATR_AXIS, "ATM_axis": ATM_AXIS}
    double = {}
    for axis_name, genes in axes.items():
        fet_vals = per_line_axis(fet_ids, genes)
        double[axis_name] = {"FET": _axis_stats(ge, fet_ids, genes, "FET-rearranged sarcoma")}
        for comp_name, comp_ids in comparators.items():
            double[axis_name][comp_name] = _axis_stats(ge, comp_ids, genes, comp_name)
            double[axis_name][f"contrast_FET_vs_{comp_name}"] = _welch(
                fet_vals, per_line_axis(comp_ids, genes))

    # The conjunction, stated so it cannot be read selectively. NEGATIVE delta = more essential
    # in FET lines (gene effect is more negative when the gene is more essential).
    def _delta(axis, comp):
        c = double[axis].get(f"contrast_FET_vs_{comp}")
        return c["delta_a_minus_b"] if c else None

    verdict = {}
    for comp in comparators:
        d_atr, d_atm = _delta("ATR_axis", comp), _delta("ATM_axis", comp)
        if d_atr is None or d_atm is None:
            verdict[comp] = {"tier": "UNREADABLE", "why": "a contrast could not be computed"}
            continue
        atr_more = d_atr < 0
        atm_not_more = d_atm >= 0
        verdict[comp] = {
            "atr_axis_delta_FET_minus_comparator": d_atr,
            "atm_axis_delta_FET_minus_comparator": d_atm,
            "atr_axis_more_essential_in_FET": bool(atr_more),
            "atm_axis_not_more_essential_in_FET": bool(atm_not_more),
            "tier": ("BOTH_HALVES" if (atr_more and atm_not_more)
                     else "ATR_HALF_ONLY" if atr_more
                     else "ATM_HALF_ONLY" if atm_not_more
                     else "NEITHER"),
            "_reading": "BOTH_HALVES is the only tier that supports the mechanism. Any other tier "
                        "is consistent with a lineage artefact and must be reported as one. NOTE "
                        "the ceiling in the module docstring: a common-essential ATR compresses "
                        "exactly this contrast, so a null here is NOT a refutation.",
        }

    other_ddr = {g: {
        "FET_mean": (round(float(ge.reindex([i for i in ge.index if i in fet_ids])[g]
                                 .dropna().mean()), 4) if g in ge.columns else None),
        "non_FET_sarcoma_mean": (round(float(ge.reindex(
            [i for i in ge.index if i in (nonfet_ids | other_sarcoma_ids)])[g]
            .dropna().mean()), 4) if g in ge.columns else None),
    } for g in OTHER_DDR}

    context = {g: (round(float(ge[g].dropna().mean()), 4) if g in ge.columns else None)
               for g in CONTEXT}

    # --- second instrument: ATR-INHIBITOR sensitivity, re-cut by FET status ----------------------
    from depmap_sarcoma_dependency import KNOWN_RELEASES
    fusion_grouping = _fet_by_fusion_call(pd, KNOWN_RELEASES, ge.index)
    fet_ids_by_call = set(fusion_grouping.pop("_fet_ids", []))
    if fet_ids_by_call:
        for axis_name, genes in axes.items():
            fusion_grouping.setdefault("double_prediction_by_fusion_call", {})[axis_name] = {
                "FET_by_call": _axis_stats(ge, fet_ids_by_call, genes, "FET by fusion call"),
                "contrast_vs_everything_else": _welch(
                    per_line_axis(fet_ids_by_call, genes),
                    per_line_axis(set(ge.index) - fet_ids_by_call, genes)),
            }
        fusion_grouping["agreement_with_label_grouping"] = {
            "n_label_only": len(fet_ids - fet_ids_by_call),
            "n_call_only": len(fet_ids_by_call - fet_ids),
            "n_both": len(fet_ids & fet_ids_by_call),
        }
    inventory = _figshare_inventory(KNOWN_RELEASES)
    # The drug matrices live in their OWN figshare articles — search for them, then inventory
    # whatever the search finds, so a miss records the search result rather than "unavailable".
    search = _figshare_search(["PRISM Repurposing Public", "PRISM Oncology Reference",
                               "Repurposing_Public", "DepMap PRISM", "prism drug repurposing"])
    extra = []
    seen_ids = {aid for _, aid in KNOWN_RELEASES}
    for term, arts in search.items():
        for a in arts:
            if isinstance(a, dict) and a.get("id") and a["id"] not in seen_ids:
                seen_ids.add(a["id"])
                extra.append((str(a.get("title", term))[:60], a["id"]))
    inventory.update(_figshare_inventory(extra[:12]))
    comparator_all = nonfet_ids | other_sarcoma_ids | nonsarcoma_ids
    drug = _drug_sensitivity_read(pd, inventory, KNOWN_RELEASES + extra, fet_ids,
                                  comparator_all, ge.index)
    # The figshare path found nothing on run 30849351348, so GDSC is the primary attempt now.
    gdsc = _gdsc_atri_read(pd, model, fet_ids | fet_ids_by_call, comparator_all)

    # --- is the KNOCKOUT instrument saturated? Decide it from the data, not from the docstring ---
    atr_panel = ge[[g for g in ATR_AXIS if g in ge.columns]].mean(axis=1).dropna()
    saturation = {
        "atr_axis_panel_mean": round(float(atr_panel.mean()), 4),
        "atr_axis_panel_sd": round(float(atr_panel.std(ddof=1)), 4),
        "largest_group_delta_seen": max(
            (abs(v) for v in (_delta("ATR_axis", c) for c in comparators) if v is not None),
            default=None),
        "_criterion": "the ATR axis sits near the common-essential floor (~ -1 is the median "
                      "common-essential gene) in EVERY group, so a between-group delta an order of "
                      "magnitude under the within-group SD is an INSTRUMENT reading, not a "
                      "biological one",
    }
    saturation["verdict"] = (
        "SATURATED — the knockout read cannot address this hypothesis; use the drug-sensitivity "
        "instrument below"
        if (saturation["atr_axis_panel_mean"] < -1.0
            and saturation["largest_group_delta_seen"] is not None
            and saturation["largest_group_delta_seen"] < saturation["atr_axis_panel_sd"])
        else "NOT SATURATED — the knockout contrast is readable and should be taken at face value")

    result = {
        "_what": "Does DepMap support the FET-fusion -> ATM-suppression -> ATR-axis-dependency "
                 "mechanism, as a transfer prior for EMC (EWSR1/TAF15/FUS::NR4A3)?",
        "_hypothesis_source": "FET fusion oncoproteins disrupt physiologic DNA repair and create a "
                              "targetable opportunity for ATR inhibitor therapy — biorxiv "
                              "10.1101/2023.04.30.538578 (PMID 37205599); clear cell sarcoma "
                              "(EWSR1::ATF1) is reported to share the FET-dependent ATRi synthetic "
                              "lethality, which is what makes this a CLASS claim EMC can inherit.",
        "_instrument_ceiling": "CRISPR knockout != inhibitor sensitivity. ATR is common-essential, "
                               "so this scan can SUPPORT the hypothesis or miss it; it cannot "
                               "refute it. Read with the module docstring's three limits.",
        "depmap_release": release,
        "n_models_with_crispr": int(ge.shape[0]),
        "genes_found": sorted(ge.columns),
        "genes_requested_but_absent": sorted(set(ALL_GENES) - set(ge.columns)),
        "dependent_threshold": DEPENDENT_THRESHOLD,
        "grouping": {
            "label_column_used": lab_col,
            "FET_rearranged": fet_groups,
            "n_FET_lines_total": len(fet_ids),
            "non_FET_sarcoma": nonfet_groups,
            "n_other_sarcoma_unclassified": len(other_sarcoma_ids),
            "n_non_sarcoma": len(nonsarcoma_ids),
        },
        "emc_line": emc,
        "double_prediction": double,
        "verdict": verdict,
        "knockout_instrument_saturation": saturation,
        "atr_inhibitor_sensitivity_gdsc": gdsc,
        "atr_inhibitor_sensitivity_depmap_attempt": drug,
        "depmap_release_file_inventory": inventory,
        "figshare_search_for_drug_matrices": search,
        "fet_grouping_by_fusion_call": fusion_grouping,
        "other_druggable_ddr_nodes": other_ddr,
        "context_gene_panel_means": context,
        "_controls": {
            f"{PAN_ESSENTIAL_CONTROL}_should_be_strongly_negative_panel_wide": round(
                float(ge[PAN_ESSENTIAL_CONTROL].dropna().mean()), 4
            ) if PAN_ESSENTIAL_CONTROL in ge.columns else None,
            f"{NEAR_NEUTRAL_CONTROL}_should_be_near_zero_panel_wide": round(
                float(ge[NEAR_NEUTRAL_CONTROL].dropna().mean()), 4
            ) if NEAR_NEUTRAL_CONTROL in ge.columns else None,
            "_reading": f"If {PAN_ESSENTIAL_CONTROL} is not clearly essential or "
                        f"{NEAR_NEUTRAL_CONTROL} is not near-neutral panel-wide, the read is broken "
                        "and nothing else here should be quoted. ⚠ POLR2A and PRKDC are NOT in the "
                        "24Q4 column set — measured on run 30848356798, which is why the "
                        "pan-essential control is RPL5.",
        },
    }

    json.dump(result, open(OUT, "w"), indent=2)
    print(json.dumps({k: result[k] for k in ("depmap_release", "verdict", "emc_line")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
