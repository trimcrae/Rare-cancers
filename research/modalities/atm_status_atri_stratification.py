#!/usr/bin/env python3
"""ATM GENETIC STATUS vs ATR-INHIBITOR SENSITIVITY, in the SAME GDSC2 residual space part D uses.

WHY THIS MODULE EXISTS
----------------------
Part D of `emc_atr_vulnerability.py` operationalises the mechanism's load-bearing variable — ATM
signalling — as `expr::ATM_signalling_DSB_repair`, a log2(TPM+1) mean over a Reactome
double-strand-break-response set. The assessment itself concedes that a transcript score cannot
observe a phosphorylation event: a cell with wholly normal ATM transcript levels can carry a wholly
defective ATM response.

⭐ ATM **GENETIC** STATUS IS THE FIELD-STANDARD ATR-INHIBITOR-SENSITIVITY STRATIFIER, and the source
paper's own comparator for its elimusertib IC50s is "cancer cell lines with known pathogenic ATM
loss of function mutations". DepMap carries ATM mutation and copy-number calls for the same models
part D already maps to GDSC2, so the stratification is free — and it had never been run.

⛔ THIS IS A POSITIVE CONTROL ON THE INSTRUMENT AS MUCH AS A TEST, AND THAT IS THE POINT.
If ATM-null lines are NOT more ATR-inhibitor-sensitive in this residual space, the residual cannot
detect the effect the published mechanism predicts, and part D's ATM null is **uninformative rather
than negative**. That outcome is more valuable than a positive one and is reported at full strength.

⭐ AND THE INSTRUMENT GETS A SECOND, INDEPENDENT CHECK IT CANNOT ARGUE WITH.
An ATM/ATRi null on its own has two explanations that this module could not otherwise separate:
the biology is absent, or the residual space cannot resolve ANY genotype-drug association. So the
identical pipeline is run on **BRCA1/BRCA2 status against the two PARP inhibitors** — the textbook
genotype-drug association in cell-line panels, and one this repository makes no claim about. It is
a MACHINERY CONTROL, never a result about EMC:
  * BRCA-null more PARPi-sensitive AND ATM-null not more ATRi-sensitive  -> the instrument works and
    the ATM null is a real (if underpowered) negative on this axis.
  * NEITHER association detectable                                       -> the instrument, not the
    biology, is what the ATM null is about, and every null part D reports means less than stated.

USAGE
-----
    python3 atm_status_atri_stratification.py --refresh   # fetch DepMap ATM/BRCA calls -> inputs cache
    python3 atm_status_atri_stratification.py             # derive from the cached inputs (offline)
    python3 atm_status_atri_stratification.py --check     # re-derive, diff against the artifact

The fetch/derive split follows `emc_atr_vulnerability.py`: every DERIVED statistic is reproducible
offline from `atm-status-atri-inputs.json`, so `--check` is a real reproduce mode. Network is
required only for `--refresh` (figshare/DepMap), which the dev sandbox cannot reach — measured, not
assumed: `curl https://api.figshare.com/v2/articles/27993248` returns `CONNECT tunnel failed,
response 403` at this repo's egress proxy. So `--refresh` runs in CI (CLAUDE.md §6).

DESIGN RULES THIS FILE IS HELD TO (CLAUDE.md §4)
------------------------------------------------
1. **An ABSENT reading is not a reading of ABSENCE.** A model missing from the mutation file was
   not SEQUENCED; it does not have "no ATM mutation". Every arm below is built only from models
   that are demonstrably profiled, and the unprofiled count is reported separately, by name.
2. **State the n before reading anything off the contrast.** Every drug row carries both arm sizes
   and the minimum effect the arm sizes could detect, and a contrast below a pre-declared floor is
   refused rather than reported.
3. **The copy-number SCALE is DETECTED, not assumed.** DepMap has shipped `OmicsCNGene.csv` on more
   than one scale across releases; a deep-deletion threshold applied to the wrong one silently
   produces an empty arm or a nonsense one. The panel-wide median decides, and what was decided is
   recorded in the artifact.
4. **The damaging-mutation COLUMN is discovered and recorded, never remembered.** DepMap has renamed
   this annotation across releases. The column actually used, its full value distribution over the
   ATM rows, and every column the file exposed are all written to the inputs cache.
"""

import argparse
import csv
import datetime as _dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "atm-status-atri-stratification.json")
INPUTS = os.path.join(HERE, "atm-status-atri-inputs.json")
PART_D_INPUTS = os.path.join(HERE, "emc-atr-vulnerability-inputs.json")

sys.path.insert(0, HERE)

# ---------------------------------------------------------------------------------------------
# The framing that must travel with every number this module emits. Same words as part D's, because
# it is the same evidence class and the same disease claim — nothing here is efficacy evidence.
# ---------------------------------------------------------------------------------------------
FRAMING = (
    "TESTS WHETHER THE GDSC2 RESIDUAL SPACE PART D USES CAN DETECT THE GENOTYPE-DRUG ASSOCIATION "
    "THE PUBLISHED MECHANISM PREDICTS. This is NOT evidence that an ATR inhibitor kills EMC cells, "
    "and cannot become that evidence from public data — no ATR inhibitor has been put on an "
    "NR4A3-fusion-positive cell. No EMC line carries an ATM call here. No efficacy, potency, dose, "
    "safety, therapeutic-window or clinical-readiness claim is made or implied."
)

# --- the drugs, grouped exactly as part D groups them so the two are readable side by side -------
ATRI_DRUGS = ("azd6738", "ve-822")            # ceralasertib, berzosertib
PARP_DRUGS = ("olaparib", "talazoparib")
NON_DDR_CONTROLS = ("paclitaxel", "bortezomib")
NEAR_NEIGHBOUR_DDR = ("mk-1775",)             # adavosertib / WEE1 — reporting only, as in part D

# ⛔ THE PRE-REGISTERED PREDICTION, FIXED BEFORE THE NUMBERS LAND. GDSC reports LN_IC50, so LOWER =
# MORE SENSITIVE, and the residual is line-median-corrected, so general chemosensitivity is already
# removed. A NEGATIVE delta (ATM-null minus ATM-intact) is the direction the mechanism predicts.
PREDICTION = {
    "ATR_inhibitors": "MECHANISM PREDICTS delta < 0: ATM loss removes the parallel DSB-signalling "
                      "arm, so the cell leans on ATR and an ATR inhibitor bites harder => LOWER "
                      "residual LN_IC50 in the ATM-null arm.",
    "PARP_inhibitors": "REPORTED, NOT A TEST OF THIS MODULE'S QUESTION. ATM loss is independently "
                       "reported to sensitise to PARP inhibition, so a negative delta here is "
                       "consistent with the mechanism but does not discriminate it from general "
                       "DDR deficiency.",
    "non_DDR_controls": "NO PREDICTION — delta should be ~0. A separation as large here as at the "
                        "ATR inhibitors means the split is tracking general drug sensitivity or a "
                        "lineage confounder, not the ATR axis.",
    "near_neighbour_DDR": "REPORTING ONLY. MK-1775/adavosertib inhibits WEE1 — the same "
                          "replication-checkpoint module, a different named target. It enters no "
                          "aggregate and no pre-registered bar.",
}

# ⛔ THE POWER FLOOR, PRE-DECLARED. Below this many models in the smaller arm the module REFUSES to
# read a contrast and reports the n instead. Ten is a convention, not a measurement, and it is set
# here — before any n is known — precisely so it cannot be tuned to whatever the join returns.
MIN_ARM_N = 10

# --- the genes, and why each is here ------------------------------------------------------------
#   ATM   — the variable under test.
#   BRCA1 } the MACHINERY CONTROL described in the header. Their association with PARP-inhibitor
#   BRCA2 } sensitivity is the best-established genotype-drug link in cell-line pharmacology, so a
#           pipeline that cannot see it cannot be trusted to have looked for the ATM one.
GENES = ("ATM", "BRCA1", "BRCA2")

# ⚠ DepMap has renamed the damaging-call annotation across releases, so the column is DISCOVERED
# from an ordered candidate list and the choice is recorded. Each entry: (column, accepted values as
# lowercase strings, a note for the artifact).
DAMAGING_CALL_CANDIDATES = [
    ("LikelyLoF", {"true", "yes", "1"},
     "DepMap's own likely-loss-of-function flag — the strictest available call."),
    ("VariantInfo", {"damaging"},
     "DepMap's variant annotation; 'damaging' is its own top severity class."),
    ("Variant_annotation", {"damaging"},
     "the pre-23Q2 spelling of VariantInfo."),
]
# A LOOSER call, reported as a sensitivity arm only. Never the primary.
NONCONSERVING_CANDIDATES = [
    ("VariantInfo", {"damaging", "other non-conserving"}),
    ("Variant_annotation", {"damaging", "other non-conserving"}),
]

# ⛔ THE DEEP-DELETION THRESHOLD, PRE-DECLARED PER SCALE. Which one applies is decided by the scale
# DETECTED from the panel-wide median (design rule 3), not by which release we think we fetched.
#   log2_relative_plus_one : DepMap's usual OmicsCNGene scale; 1.0 is neutral diploid, so
#                            log2(CN+1) < 0.25 means relative CN < 0.19 — a deep deletion.
#   relative              : 1.0 neutral; < 0.19 deep deletion, the same cut untransformed.
DEEP_DELETION_CUT = {"log2_relative_plus_one": 0.25, "relative": 0.19}


# =============================================================================================
# statistics — pure stdlib, so the derive half runs anywhere the repository runs
# =============================================================================================
def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _sd(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _norm_sf(z):
    """Upper tail of the standard normal. `math.erfc` is exact enough and needs no scipy."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _mannwhitney(a, b):
    """Two-sided Mann-Whitney U with the tie correction, plus Cliff's delta.

    Sign convention, load-bearing and stated here rather than inferred: `delta` is oriented so that
    NEGATIVE means group `a` (the null arm) sits LOWER than group `b` — which, on GDSC's LN_IC50
    scale, means MORE SENSITIVE, the direction the mechanism predicts.
    """
    n1, n2 = len(a), len(b)
    if n1 < 1 or n2 < 1:
        return None
    joined = [(v, 0) for v in a] + [(v, 1) for v in b]
    joined.sort(key=lambda t: t[0])
    ranks = [0.0] * len(joined)
    i = 0
    tie_term = 0.0
    while i < len(joined):
        j = i
        while j + 1 < len(joined) and joined[j + 1][0] == joined[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        t = j - i + 1
        if t > 1:
            tie_term += t ** 3 - t
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, joined) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    n = n1 + n2
    mu = n1 * n2 / 2.0
    var = n1 * n2 * (n + 1) / 12.0
    if tie_term:
        var = n1 * n2 / 12.0 * ((n + 1) - tie_term / float(n * (n - 1)))
    if var <= 0:
        return {"u": u1, "n_null": n1, "n_intact": n2, "p_two_sided": None,
                "cliffs_delta": None, "_status": "zero variance — every value tied"}
    z = (u1 - mu) / math.sqrt(var)
    # continuity correction, toward the null
    zc = (u1 - mu - (0.5 if u1 > mu else -0.5)) / math.sqrt(var) if u1 != mu else 0.0
    # Cliff's delta = P(a>b) - P(a<b). U1 counts the (a>b) pairs, so this is ALREADY negative when
    # `a` sits lower — no negation. ⚠ An earlier draft negated it here and a self-test on a strictly
    # ordered pair (a=[1,1.1,1.2], b=[5,5.1,5.2]) returned +1.0 where the stated convention demands
    # -1.0. The sign of this field decides which way every contrast in the artifact reads, so it is
    # asserted in `_selftest` rather than left to inspection.
    delta = (2.0 * u1) / (n1 * n2) - 1.0
    p = 2.0 * _norm_sf(abs(zc))
    return {"u": round(u1, 1), "n_null": n1, "n_intact": n2,
            "z": round(z, 4),
            # 3 significant figures, not 6 decimal places: a p of 4e-16 must not print as 0.0, which
            # reads as an exact zero rather than as "below what this approximation resolves".
            "p_two_sided": float(f"{p:.3g}"),
            "cliffs_delta": round(delta, 4)}


def _hodges_lehmann(a, b, conf=0.95):
    """Hodges-Lehmann shift (median of all pairwise a-b differences) + its distribution-free CI.

    ⭐ THE CI IS THE POINT, NOT THE POINT ESTIMATE. "What can this n carry" is exactly the question
    a confidence interval answers, and the task this module was filed against asks for the n before
    anything is read off the contrast. A wide CI straddling zero is a real result: it says the arm
    sizes cannot resolve the effect, which is different from saying the effect is absent.
    """
    n1, n2 = len(a), len(b)
    if n1 < 1 or n2 < 1:
        return None
    diffs = sorted(x - y for x in a for y in b)
    m = len(diffs)
    hl = diffs[m // 2] if m % 2 else (diffs[m // 2 - 1] + diffs[m // 2]) / 2.0
    if abs(conf - 0.95) > 1e-9:
        raise ValueError("only the 95% CI is tabulated here; add the z before asking for another")
    z = 1.959963984540054
    k = n1 * n2 / 2.0 - z * math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    k = int(math.floor(k))
    if k < 0:
        return {"shift": round(hl, 4), "ci_low": None, "ci_high": None,
                "_status": f"arm sizes too small for a distributional CI (n1={n1}, n2={n2})"}
    lo = diffs[k] if k < m else None
    hi = diffs[m - 1 - k] if 0 <= m - 1 - k < m else None
    return {"shift": round(hl, 4),
            "ci_low": round(lo, 4) if lo is not None else None,
            "ci_high": round(hi, 4) if hi is not None else None,
            "conf": conf, "n_pairs": m}


def _min_detectable_delta(n1, n2, alpha=0.05, power=0.80):
    """Smallest |Cliff's delta| the arm sizes could detect, two-sided, at the stated power.

    Normal approximation to the Mann-Whitney null, using the null SD — the standard rough MDE, and
    labelled as such wherever it is printed. It exists so a null can be read as "no effect this
    large is detectable here" rather than as "no effect".
    """
    if n1 < 2 or n2 < 2:
        return None
    z_a, z_b = 1.959963984540054, 0.8416212335729143
    sd_u = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    return round(2.0 * (z_a + z_b) * sd_u / (n1 * n2), 4)


def _benjamini_hochberg(pvals):
    """BH-adjusted p-values, keyed the same way as the input dict."""
    items = [(k, v) for k, v in pvals.items() if v is not None]
    if not items:
        return {k: None for k in pvals}
    items.sort(key=lambda kv: kv[1])
    m = len(items)
    out, prev = {}, 1.0
    for rank in range(m, 0, -1):
        k, p = items[rank - 1]
        adj = min(prev, p * m / rank)
        out[k] = round(adj, 6)
        prev = adj
    for k in pvals:
        out.setdefault(k, None)
    return out


# =============================================================================================
# FETCH — network only, CI only
# =============================================================================================
def _utc_now():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scan_mutations(path, genes):
    """Stream the somatic-mutation table, keeping only `genes` rows plus the PROFILED MODEL SET.

    ⛔ THE PROFILED SET IS NOT OPTIONAL AND IS THE WHOLE REASON THIS IS A SCAN RATHER THAN A GREP.
    Without it, "this model has no ATM damaging call" and "this model was never sequenced" are the
    same observation, and the second one must never enter the intact arm (design rule 1).
    """
    out = {"gene_rows": {g: [] for g in genes}, "profiled_models": set(),
           "n_rows_scanned": 0, "columns": None}
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.DictReader(fh)
        out["columns"] = list(rd.fieldnames or [])
        mid_col = next((c for c in (rd.fieldnames or [])
                        if c in ("ModelID", "DepMap_ID", "SampleID", "ModelId")), None)
        sym_col = next((c for c in (rd.fieldnames or [])
                        if c in ("HugoSymbol", "Hugo_Symbol", "GeneSymbol", "Gene")), None)
        out["model_id_column"] = mid_col
        out["gene_symbol_column"] = sym_col
        if not mid_col or not sym_col:
            out["_status"] = (f"could not identify the model-id/gene columns "
                              f"(model={mid_col}, gene={sym_col})")
            out["profiled_models"] = []
            return out
        want = set(genes)
        for row in rd:
            out["n_rows_scanned"] += 1
            mid = row.get(mid_col)
            if mid:
                out["profiled_models"].add(mid)
            if row.get(sym_col) in want:
                # keep the whole row: which annotation column is authoritative is decided at
                # derive time, from the candidate list, and recorded there.
                out["gene_rows"][row[sym_col]].append({k: v for k, v in row.items() if v not in (None, "")})
    out["profiled_models"] = sorted(out["profiled_models"])
    out["_status"] = "read"
    return out


def _scan_cn(path, genes):
    """Stream the wide gene-level CN matrix, keeping only `genes` columns plus the profiled set."""
    out = {"by_gene": {g: {} for g in genes}, "profiled_models": [],
           "n_rows_scanned": 0, "panel_median_sample": {}}
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        try:
            header = next(rd)
        except StopIteration:
            out["_status"] = "empty file"
            return out
        # DepMap names CN columns "SYMBOL (ENTREZ)"; the first column is the model id.
        idx = {}
        for j, name in enumerate(header):
            sym = name.split(" (")[0].strip()
            if sym in genes and sym not in idx:
                idx[sym] = j
        out["gene_column_index"] = idx
        out["gene_columns_resolved"] = {g: header[j] for g, j in idx.items()}
        out["genes_absent_from_cn_header"] = sorted(set(genes) - set(idx))
        if not idx:
            out["_status"] = "no requested gene resolved in the CN header"
            return out
        # a scale probe: sample the first resolved gene's values across the whole panel
        probe_gene = sorted(idx)[0]
        probe_vals = []
        models = []
        for row in rd:
            if not row:
                continue
            out["n_rows_scanned"] += 1
            mid = row[0]
            models.append(mid)
            for g, j in idx.items():
                if j < len(row):
                    try:
                        out["by_gene"][g][mid] = float(row[j])
                    except (TypeError, ValueError):
                        pass
            v = out["by_gene"][probe_gene].get(mid)
            if v is not None:
                probe_vals.append(v)
        out["profiled_models"] = models
        out["panel_median_sample"] = {
            "gene": probe_gene, "n": len(probe_vals),
            "median": round(_median(probe_vals), 6) if probe_vals else None,
            "p05": round(sorted(probe_vals)[int(0.05 * len(probe_vals))], 6) if probe_vals else None,
            "p95": round(sorted(probe_vals)[int(0.95 * len(probe_vals))], 6) if probe_vals else None,
            "min": round(min(probe_vals), 6) if probe_vals else None,
            "max": round(max(probe_vals), 6) if probe_vals else None,
        }
    out["_status"] = "read"
    return out


def refresh():
    """Fetch the DepMap ATM/BRCA calls into the inputs cache. Network required — CI only."""
    from depmap_sarcoma_dependency import KNOWN_RELEASES, _download, _get  # noqa: E402

    inp = {
        "_what": "DepMap ATM / BRCA1 / BRCA2 mutation and copy-number calls, restricted to the "
                 "genes and fields this module reads. Fetched, never remembered.",
        "_framing": FRAMING,
        "fetched_utc": _utc_now(),
        "genes": list(GENES),
        "_release_candidates_tried": [],
    }
    want = {"OmicsSomaticMutations.csv", "OmicsCNGene.csv", "Model.csv"}
    chosen = None
    for label, aid in KNOWN_RELEASES:
        try:
            files = {f["name"]: f["download_url"]
                     for f in json.loads(_get(f"https://api.figshare.com/v2/articles/{aid}")).get("files", [])}
        except Exception as exc:  # noqa
            inp["_release_candidates_tried"].append({"release": label, "article": aid,
                                                     "error": str(exc)[:200]})
            continue
        have = sorted(want & set(files))
        inp["_release_candidates_tried"].append({"release": label, "article": aid, "exposes": have})
        if {"OmicsSomaticMutations.csv", "OmicsCNGene.csv"} <= set(files):
            chosen = (label, aid, files)
            break
    if not chosen:
        # ⭐ FALLBACK: search figshare by the distinctive filename token, exactly as
        # `depmap_sarcoma_dependency.discover_depmap_files` does for CRISPRGeneEffect. The pinned
        # article ids are a convenience, not a contract — DepMap has moved files between articles
        # across releases, and a hard-coded id that stopped resolving would present as "DepMap has
        # no mutation calls", which is an absent reading wearing the costume of a result.
        try:
            arts = json.loads(_get("https://api.figshare.com/v2/articles"
                                   "?search_for=OmicsSomaticMutations&page_size=20"
                                   "&order=published_date&order_direction=desc"))
        except Exception as exc:  # noqa
            arts = []
            inp["_fallback_search_error"] = str(exc)[:200]
        for art in arts:
            try:
                files = {f["name"]: f["download_url"]
                         for f in json.loads(
                             _get(f"https://api.figshare.com/v2/articles/{art['id']}")).get("files", [])}
            except Exception:  # noqa
                continue
            inp["_release_candidates_tried"].append(
                {"release": f"figshare-search:{art.get('title', '')[:60]}", "article": art["id"],
                 "exposes": sorted(want & set(files))})
            if {"OmicsSomaticMutations.csv", "OmicsCNGene.csv"} <= set(files):
                chosen = (f"figshare-search:{art.get('title', '')[:60]}", art["id"], files)
                break
    if not chosen:
        inp["_status"] = ("no DepMap release exposed both OmicsSomaticMutations.csv and "
                          "OmicsCNGene.csv — nothing fetched")
        _write(INPUTS, inp)
        print(inp["_status"], file=sys.stderr)
        return inp
    label, aid, files = chosen
    inp["depmap_release"] = label
    inp["depmap_figshare_article"] = aid
    inp["source_files"] = {n: files[n] for n in sorted(want & set(files))}

    print(f"  DepMap {label} (figshare {aid}): downloading mutations", file=sys.stderr)
    mut_path = _download(files["OmicsSomaticMutations.csv"], timeout=1800)
    inp["mutations"] = _scan_mutations(mut_path, GENES)
    try:
        os.unlink(mut_path)
    except OSError:
        pass

    print(f"  DepMap {label}: downloading gene-level copy number", file=sys.stderr)
    cn_path = _download(files["OmicsCNGene.csv"], timeout=1800)
    inp["copy_number"] = _scan_cn(cn_path, GENES)
    try:
        os.unlink(cn_path)
    except OSError:
        pass

    # Model.csv is small and is the ONLY way to say whether the null arm is a lineage artefact.
    inp["model_metadata"] = {"_status": "not fetched"}
    if "Model.csv" in files:
        try:
            mpath = _download(files["Model.csv"], timeout=600)
            meta = {}
            with open(mpath, newline="", encoding="utf-8", errors="replace") as fh:
                rd = csv.DictReader(fh)
                mid_col = next((c for c in (rd.fieldnames or [])
                                if c in ("ModelID", "DepMap_ID", "ModelId")), None)
                for row in rd:
                    mid = row.get(mid_col) if mid_col else None
                    if mid:
                        meta[mid] = {"OncotreeLineage": row.get("OncotreeLineage"),
                                     "OncotreePrimaryDisease": row.get("OncotreePrimaryDisease")}
            inp["model_metadata"] = {"_status": "read", "n_models": len(meta), "by_model": meta}
            os.unlink(mpath)
        except Exception as exc:  # noqa
            inp["model_metadata"] = {"_status": f"failed: {str(exc)[:200]}"}
    inp["_status"] = "read"
    _write(INPUTS, inp)
    print(f"  wrote {INPUTS}", file=sys.stderr)
    return inp


# =============================================================================================
# DERIVE — offline, from the inputs cache alone
# =============================================================================================
def _pick_damaging_column(columns, rows, candidates):
    """Choose the damaging-call column from an ordered candidate list, and audit every candidate.

    ⛔ PRESENT IS NOT THE SAME AS POPULATED, AND THE DIFFERENCE IS A SILENT UNDER-COUNT.
    DepMap ships some annotation columns that exist in the header but are blank for whole genes in
    a given release. A selector that stopped at the first column merely PRESENT would then build the
    null arm from an empty annotation and report a confident `n_models_damaging_mutation: 0` — an
    absent reading wearing the costume of a measurement (CLAUDE.md §4). So a candidate is taken only
    if it is present AND yields at least one call over this gene's rows, and the full audit of every
    candidate is returned so the choice can be checked rather than trusted.

    Returns (column, accepted_values, note, value_distribution, audit).
    """
    cols = set(columns or [])
    audit, chosen = [], None
    for col, accepted, note in candidates:
        entry = {"column": col, "present_in_release": col in cols, "note": note}
        if col in cols:
            dist, n_called = {}, 0
            for r in rows:
                v = (r.get(col) or "").strip()
                dist[v or "<empty>"] = dist.get(v or "<empty>", 0) + 1
                if v.lower() in accepted:
                    n_called += 1
            entry["value_distribution_over_this_gene"] = dist
            entry["n_rows_called"] = n_called
            if chosen is None and n_called > 0:
                chosen = (col, accepted, note, dist)
                entry["USED"] = True
        audit.append(entry)
    if chosen is None:
        why = ("no candidate damaging-call column is both present in this release and populated "
               "for this gene — see the audit; the mutation arm is EMPTY BY ABSENCE OF ANNOTATION, "
               "not by absence of damaging variants")
        return None, set(), why, {}, audit
    return chosen[0], chosen[1], chosen[2], chosen[3], audit


def _damaged_models(rows, col, accepted):
    out = set()
    if not col:
        return out
    for r in rows:
        v = (r.get(col) or "").strip().lower()
        if v in accepted:
            mid = r.get("ModelID") or r.get("DepMap_ID") or r.get("ModelId") or r.get("SampleID")
            if mid:
                out.add(mid)
    return out


def _detect_cn_scale(probe):
    """Decide the CN scale from the panel-wide median, and say which and why (design rule 3)."""
    med = (probe or {}).get("median")
    if med is None:
        return {"scale": None, "_why": "no CN values read — scale undecidable"}
    if 0.7 <= med <= 1.4:
        return {"scale": "log2_relative_plus_one", "panel_median": med,
                "_why": f"panel median {med} sits at the log2(relative CN + 1) neutral point of 1.0"}
    if 1.6 <= med <= 2.6:
        return {"scale": "absolute_copies", "panel_median": med,
                "_why": f"panel median {med} sits at the diploid absolute count of 2.0 — this "
                        f"module declares no threshold for that scale, so CN is NOT used"}
    if -0.4 <= med <= 0.4:
        return {"scale": "log2_ratio", "panel_median": med,
                "_why": f"panel median {med} sits at the log2-ratio neutral point of 0.0 — this "
                        f"module declares no threshold for that scale, so CN is NOT used"}
    if 0.85 <= med <= 1.15:
        return {"scale": "relative", "panel_median": med,
                "_why": f"panel median {med} sits at the relative-CN neutral point of 1.0"}
    return {"scale": None, "panel_median": med,
            "_why": f"panel median {med} matches no scale this module declares a threshold for; "
                    f"CN is NOT used rather than guessed"}


def _arm_definition(inp, gene):
    """Build the null / intact arms for one gene, with every count that makes them readable."""
    mut = inp.get("mutations") or {}
    cn = inp.get("copy_number") or {}
    rows = (mut.get("gene_rows") or {}).get(gene) or []
    seq_models = set(mut.get("profiled_models") or [])
    cn_models = set(cn.get("profiled_models") or [])

    col, accepted, note, dist, audit = _pick_damaging_column(
        mut.get("columns"), rows, DAMAGING_CALL_CANDIDATES)
    damaged = _damaged_models(rows, col, accepted)
    lcol, laccepted, _lnote, _ldist, _laudit = _pick_damaging_column(
        mut.get("columns"), rows,
        [(c, a, "looser non-conserving call") for c, a in NONCONSERVING_CANDIDATES])
    loose = _damaged_models(rows, lcol, laccepted)

    scale = _detect_cn_scale(cn.get("panel_median_sample"))
    cut = DEEP_DELETION_CUT.get(scale.get("scale"))
    cn_vals = (cn.get("by_gene") or {}).get(gene) or {}
    deleted = set()
    if cut is not None:
        deleted = {m for m, v in cn_vals.items() if v is not None and v < cut}
    return {
        "gene": gene,
        "damaging_call_column": col,
        "damaging_call_note": note,
        "damaging_call_value_distribution_over_this_gene": dist,
        "damaging_call_candidate_audit": audit,
        "nonconserving_call_column": lcol,
        "n_rows_for_this_gene_in_mutation_file": len(rows),
        "n_models_sequenced": len(seq_models),
        "n_models_with_cn_call": len(cn_models),
        "copy_number_scale": scale,
        "deep_deletion_cut_applied": cut,
        "cn_used": cut is not None,
        "n_models_damaging_mutation": len(damaged),
        "n_models_deep_deletion": len(deleted),
        "n_models_nonconserving_or_worse": len(loose),
        "_sets": {"damaged": damaged, "deleted": deleted, "loose": loose,
                  "sequenced": seq_models, "cn_profiled": cn_models},
    }


def _contrast(null_vals, intact_vals):
    """Everything that must be said about one drug x one arm split, n FIRST."""
    n1, n2 = len(null_vals), len(intact_vals)
    row = {
        "n_null_arm": n1,
        "n_intact_arm": n2,
        "min_detectable_cliffs_delta_80pct_power": _min_detectable_delta(n1, n2),
        "_mde_note": "normal approximation to the Mann-Whitney null, two-sided alpha 0.05, "
                     "80% power. A rough screen for what these arm sizes could resolve, not an "
                     "exact power calculation.",
    }
    # ⛔ THE FLOOR APPLIES TO BOTH ARMS. The null arm is the one that is normally scarce, but a
    # comparator can empty too — if every profiled model is called null (a mis-detected copy-number
    # scale does exactly this), there is no comparator and the contrast is undefined rather than
    # extreme. ⚠ Caught by `test_a_deep_deletion_is_only_called_on_a_scale_with_a_declared_threshold`,
    # which crashed on `round(None)` here: the failure was a TypeError, but the defect was that the
    # code had an opinion about an empty comparator at all.
    if n1 < MIN_ARM_N or n2 < MIN_ARM_N:
        which = "null" if n1 < MIN_ARM_N else "intact"
        row["_status"] = (f"REFUSED — the {which} arm holds {n1 if which == 'null' else n2} "
                          f"model(s), below the pre-declared floor of {MIN_ARM_N}. The n is the "
                          f"result; no contrast is read.")
        row["median_null"] = round(_median(null_vals), 4) if n1 else None
        row["median_intact"] = round(_median(intact_vals), 4) if n2 else None
        return row
    row["median_null"] = round(_median(null_vals), 4)
    row["median_intact"] = round(_median(intact_vals), 4)
    row["mean_null"] = round(_mean(null_vals), 4)
    row["mean_intact"] = round(_mean(intact_vals), 4)
    row["sd_null"] = round(_sd(null_vals), 4) if _sd(null_vals) is not None else None
    row["sd_intact"] = round(_sd(intact_vals), 4) if _sd(intact_vals) is not None else None
    row["delta_median_null_minus_intact"] = round(row["median_null"] - row["median_intact"], 4)
    row["mannwhitney"] = _mannwhitney(null_vals, intact_vals)
    row["hodges_lehmann"] = _hodges_lehmann(null_vals, intact_vals)
    row["_status"] = "read"
    return row


def _stub(status):
    """A failure object whose every top-level key is `_`-prefixed.

    ⛔ THIS SHAPE IS LOAD-BEARING, NOT COSMETIC. `artifact_stub_guard.is_stub` — the thing standing
    between a soft-failed CI step and a good committed artifact — defines a stub as exactly "a JSON
    object whose every top-level key starts with `_`". An earlier draft returned `{"verdict":
    "NO_DATA", "depmap_release": None, ...}` on these paths: real-looking keys, so the guard would
    have PASSED it and a network blip would have published NO_DATA over a real result. The guard is
    dumb on purpose and it is this function's job to be legible to it.
    """
    return {"_what": "ATM genetic status vs ATR-inhibitor sensitivity — NOT COMPUTED.",
            "_framing": FRAMING,
            "_status": status,
            "_verdict": "NO_DATA",
            "_stub_note": "every key here is `_`-prefixed so artifact_stub_guard.is_stub() drops "
                          "this rather than letting it overwrite a real artifact."}


def derive(inp):
    """Everything the artifact says, computed from the inputs cache alone."""
    art = {
        "_what": "ATM GENETIC STATUS vs ATR-INHIBITOR SENSITIVITY in the SAME GDSC2 residual space "
                 "part D of the EMC ATR vulnerability assessment uses — the field-standard "
                 "stratifier that assessment operationalises as a transcript score instead.",
        "_framing": FRAMING,
        "_sign": "GDSC LN_IC50: LOWER = MORE SENSITIVE. Residuals are line-median-corrected, so "
                 "what is compared is the DRUG-SPECIFIC residual and a line's general "
                 "chemosensitivity is already removed. delta < 0 == the null arm is MORE sensitive.",
        "_prediction_registered_before_the_numbers": PREDICTION,
        "_power_floor": {"min_models_in_null_arm": MIN_ARM_N,
                         "_why": "declared before any n was known, so it cannot be tuned to "
                                 "whatever the join returned"},
        "depmap_release": inp.get("depmap_release"),
        "depmap_figshare_article": inp.get("depmap_figshare_article"),
        "depmap_source_files": sorted((inp.get("source_files") or {}).keys()),
        "depmap_fetched_utc": inp.get("fetched_utc"),
    }
    if inp.get("_status") != "read":
        return _stub(f"inputs cache not populated: {inp.get('_status')}")

    # ---- the GDSC2 residuals part D already computed. Same file, same numbers, no re-derivation.
    try:
        with open(PART_D_INPUTS, encoding="utf-8") as fh:
            pdin = json.load(fh)
    except OSError as exc:
        return _stub(f"part D inputs cache unreadable: {exc}")
    part_d = pdin.get("part_d") or {}
    resid = part_d.get("gdsc_residual_ln_ic50_by_drug") or {}
    art["gdsc_source"] = {
        "_from": "research/modalities/emc-atr-vulnerability-inputs.json -> "
                 "part_d.gdsc_residual_ln_ic50_by_drug",
        "_note": "READ, NOT RECOMPUTED. These are the identical residuals part D correlates, so a "
                 "difference between this module and part D can never be a difference in the "
                 "drug-response numbers.",
        "release": (part_d.get("gdsc_meta") or {}).get("source"),
        "n_rows_in_release": (part_d.get("gdsc_meta") or {}).get("n_rows"),
        "drugs_with_data": sorted(resid),
        "n_models_per_drug": {d: len(v) for d, v in sorted(resid.items())},
    }
    if not resid:
        return _stub("no GDSC residuals in the part D cache — nothing to stratify")

    gdsc_models = set()
    for v in resid.values():
        gdsc_models |= set(v)
    art["gdsc_source"]["n_distinct_models_with_any_residual"] = len(gdsc_models)

    lineage = ((inp.get("model_metadata") or {}).get("by_model") or {})
    groups = {"ATR_inhibitors": ATRI_DRUGS, "PARP_inhibitors": PARP_DRUGS,
              "non_DDR_controls": NON_DDR_CONTROLS, "near_neighbour_DDR": NEAR_NEIGHBOUR_DDR}

    by_gene = {}
    for gene in GENES:
        d = _arm_definition(inp, gene)
        sets = d.pop("_sets")
        # ⛔ THE JOIN, STATED AS COUNTS BEFORE ANY CONTRAST IS READ (design rule 2). "Has a call" is
        # membership of the PROFILED set, never presence in the damaged set.
        callable_models = gdsc_models & (sets["sequenced"] | sets["cn_profiled"])
        null_primary = (sets["damaged"] | sets["deleted"]) & gdsc_models
        intact_primary = callable_models - null_primary
        d["join"] = {
            "n_gdsc_models": len(gdsc_models),
            "n_gdsc_models_with_any_depmap_call": len(callable_models),
            "n_gdsc_models_with_no_depmap_call": len(gdsc_models - callable_models),
            "_absent_reading_note": "a GDSC model with no DepMap call was NOT PROFILED. It is "
                                    "excluded from both arms rather than counted as intact — an "
                                    "absent reading is not a reading of absence (CLAUDE.md §4).",
            "n_null_arm_primary": len(null_primary),
            "n_intact_arm_primary": len(intact_primary),
            "null_arm_composition": {
                "damaging_mutation_only": len((sets["damaged"] - sets["deleted"]) & gdsc_models),
                "deep_deletion_only": len((sets["deleted"] - sets["damaged"]) & gdsc_models),
                "both": len((sets["damaged"] & sets["deleted"]) & gdsc_models),
            },
        }
        # lineage composition of the null arm — the confounder a reader would ask about first
        lin = {}
        for m in sorted(null_primary):
            k = (lineage.get(m) or {}).get("OncotreeLineage") or "UNKNOWN"
            lin[k] = lin.get(k, 0) + 1
        d["null_arm_lineage_composition"] = dict(sorted(lin.items(), key=lambda kv: -kv[1]))
        d["null_arm_model_ids"] = sorted(null_primary)

        # the arm variants: primary first, then the sensitivity arms
        arms = {
            "primary_damaging_mutation_or_deep_deletion": null_primary,
            "damaging_mutation_only": sets["damaged"] & gdsc_models,
            "deep_deletion_only": sets["deleted"] & gdsc_models,
            "nonconserving_or_worse": (sets["loose"] | sets["deleted"]) & gdsc_models,
        }
        d["_arm_variants_note"] = ("the PRIMARY arm is pre-declared; the others are a sensitivity "
                                   "analysis and no verdict is read from them")
        per_arm = {}
        for arm_name, null_set in arms.items():
            intact_set = callable_models - null_set
            per_drug, pvals = {}, {}
            for drug, per_line in sorted(resid.items()):
                nv = [per_line[m] for m in sorted(null_set & set(per_line))]
                iv = [per_line[m] for m in sorted(intact_set & set(per_line))]
                row = _contrast(nv, iv)
                row["group"] = next((g for g, ds in groups.items() if drug in ds), "ungrouped")
                per_drug[drug] = row
                mw = row.get("mannwhitney") or {}
                pvals[drug] = mw.get("p_two_sided")
            bh = _benjamini_hochberg(pvals)
            for drug in per_drug:
                per_drug[drug]["p_two_sided_bh_adjusted"] = bh.get(drug)
            per_arm[arm_name] = {"n_null_arm": len(null_set),
                                 "n_intact_arm": len(intact_set),
                                 "by_drug": per_drug}
        d["contrasts"] = per_arm
        by_gene[gene] = d
    art["by_gene"] = by_gene
    art["_multiple_testing"] = ("p_two_sided_bh_adjusted is Benjamini-Hochberg across the "
                                f"{len(resid)} drugs WITHIN one gene and one arm definition. It "
                                "does not adjust across genes or across the sensitivity arms, and "
                                "the sensitivity arms are not independent tests.")
    art.update(_verdict(art))
    art["_what_this_cannot_conclude"] = [
        "That ATR inhibition kills EWSR1::NR4A3-positive cells. No ATR inhibitor has ever been put "
        "on an NR4A3-fusion-positive cell in any public dataset, and no EMC line contributes an ATM "
        "call here.",
        "That EMC tumours carry ATM loss. This module reads cancer cell lines of other lineages; "
        "the published mechanism is fusion-driven ATM SUPPRESSION, which is not a mutation and "
        "would not appear in a mutation or copy-number call at all.",
        "An effective concentration, a dose, a schedule or an exposure.",
        "Whether a positive contrast would transfer to a fusion-driven ATM defect. A truncating "
        "mutation and a fusion-suppressed signalling arm are different lesions, and only the first "
        "is what was stratified on.",
        "Anything about a patient.",
    ]
    return art


def _verdict(art):
    """The instrument reading — the thing this module was actually filed to produce.

    ⛔ THE STRONG OUTCOME IS THE NEGATIVE ONE AND IT IS NOT SOFTENED HERE. If neither the ATM/ATRi
    association nor the BRCA/PARPi machinery control is detectable, the residual space cannot resolve
    a genotype-drug association of the size on offer, and every null part D reports on that axis is
    UNINFORMATIVE rather than NEGATIVE.
    """
    def _grab(gene, drugs):
        g = (art.get("by_gene") or {}).get(gene) or {}
        arm = ((g.get("contrasts") or {}).get("primary_damaging_mutation_or_deep_deletion") or {})
        rows = [(d, (arm.get("by_drug") or {}).get(d) or {}) for d in drugs]
        return [(d, r) for d, r in rows if r]

    def _summary(rows):
        out = {}
        for d, r in rows:
            mw = r.get("mannwhitney") or {}
            hl = r.get("hodges_lehmann") or {}
            out[d] = {"n_null_arm": r.get("n_null_arm"), "n_intact_arm": r.get("n_intact_arm"),
                      "status": r.get("_status"),
                      "delta_median": r.get("delta_median_null_minus_intact"),
                      "hl_shift": hl.get("shift"),
                      "hl_ci": [hl.get("ci_low"), hl.get("ci_high")],
                      "cliffs_delta": mw.get("cliffs_delta"),
                      "p_two_sided": mw.get("p_two_sided"),
                      "min_detectable_cliffs_delta": r.get("min_detectable_cliffs_delta_80pct_power")}
        return out

    atm_rows = _grab("ATM", ATRI_DRUGS)
    ctrl_rows = _grab("ATM", NON_DDR_CONTROLS)
    parp_rows = _grab("ATM", PARP_DRUGS)
    v = {"instrument_reading": {
        "ATM_vs_ATR_inhibitors": _summary(atm_rows),
        "ATM_vs_non_DDR_controls": _summary(ctrl_rows),
        "ATM_vs_PARP_inhibitors": _summary(parp_rows),
        # ⛔ THE AWKWARD DRUG IS ALWAYS REPORTED, AND IT ENTERS NO AGGREGATE.
        # MK-1775/adavosertib inhibits WEE1 — the same replication-checkpoint module as ATR/CHK1, a
        # DIFFERENT named target — so it is neither an ATR inhibitor nor a clean non-DDR control.
        # Part D added this group after a hardening round found the drug falling through the grid:
        # fetched, computed, stored, and invisible to every printed summary. The same hole is
        # possible here and is closed the same way.
        "ATM_vs_near_neighbour_DDR_reporting_only": _summary(_grab("ATM", NEAR_NEIGHBOUR_DDR)),
    }}
    # the machinery control: BRCA1/BRCA2 against the PARP inhibitors
    mach = {}
    for gene in ("BRCA1", "BRCA2"):
        mach[gene] = _summary(_grab(gene, PARP_DRUGS))
    v["machinery_control_BRCA_vs_PARP"] = mach
    v["_machinery_control_note"] = (
        "The best-established genotype-drug association in cell-line pharmacology, run through the "
        "IDENTICAL pipeline. It is not a claim of this repository and not a result about EMC; it "
        "exists so an ATM/ATRi null can be told apart from a residual space that cannot resolve any "
        "genotype-drug association.")

    def _detected(summ, directional=True):
        """A contrast counts as DETECTED when it was read at all and its 95% CI excludes zero.

        ⛔ `directional` IS NOT A STYLE CHOICE — IT IS WHAT THE GROUP IS FOR.
        For the ATR inhibitors the mechanism predicts a SIGN, so only a shift below zero counts;
        a null arm that came out RESISTANT would not be mechanism support and must not be scored
        as a hit. For the non-DDR CONTROLS there is no prediction and the question is different —
        "does this split move a drug it has no business moving?" — so a separation in EITHER
        direction is the confound signal. ⚠ Judging the controls one-sided (the first draft did)
        makes a null arm that is uniformly MORE RESISTANT to paclitaxel read as a clean control,
        when it is exactly the lineage/growth-rate artefact the control exists to catch.
        """
        hits = []
        for d, s in summ.items():
            if s.get("status") != "read":
                continue
            lo, hi = (s.get("hl_ci") or [None, None])
            if s.get("hl_shift") is None or lo is None or hi is None:
                continue
            if directional:
                if s["hl_shift"] < 0 and hi < 0:
                    hits.append(d)
            elif hi < 0 or lo > 0:
                hits.append(d)
        return hits

    atri_hits = _detected(v["instrument_reading"]["ATM_vs_ATR_inhibitors"])
    ctrl_hits = _detected(v["instrument_reading"]["ATM_vs_non_DDR_controls"], directional=False)
    mach_hits = sorted({d for g in mach.values() for d in _detected(g)})
    any_read = any(s.get("status") == "read"
                   for s in v["instrument_reading"]["ATM_vs_ATR_inhibitors"].values())
    v["detected"] = {"ATM_vs_ATR_inhibitors": atri_hits,
                     "ATM_vs_non_DDR_controls": ctrl_hits,
                     "machinery_control_BRCA_vs_PARP": mach_hits,
                     "_criterion": "ATR inhibitors and the BRCA/PARP machinery control are "
                                   "DIRECTIONAL — read at all, shift in the predicted direction, "
                                   "and the 95% Hodges-Lehmann CI entirely below zero. The non-DDR "
                                   "controls are TWO-SIDED: any CI excluding zero counts, because a "
                                   "control has no predicted direction and a separation either way "
                                   "is the confound this group exists to catch."}
    if not any_read:
        v["verdict"] = "UNDERPOWERED"
        v["verdict_reading"] = (
            "The join produces too few ATM-null models with a GDSC2 residual to support a contrast "
            f"at the pre-declared floor of {MIN_ARM_N}. The n is the result. Nothing is claimed "
            "about ATM status and ATR-inhibitor sensitivity either way, and part D's ATM row is "
            "neither rescued nor further damaged by this module.")
    elif atri_hits and not ctrl_hits:
        v["verdict"] = "ATRI_SPECIFIC_SEPARATION"
        v["verdict_reading"] = (
            "ATM-null lines are more sensitive to " + ", ".join(atri_hits) + " in this residual "
            "space, and the non-DDR controls do not separate. The residual space CAN resolve the "
            "genotype-drug association the mechanism predicts, which makes part D's transcript-score "
            "null a null about the transcript proxy rather than about the instrument.")
    elif atri_hits and ctrl_hits:
        v["verdict"] = "NON_SPECIFIC_SEPARATION"
        v["verdict_reading"] = (
            "ATM-null lines separate on the ATR inhibitors (" + ", ".join(atri_hits) + ") AND on "
            "the non-DDR controls (" + ", ".join(ctrl_hits) + "), so what the split tracks is "
            "general drug sensitivity or a lineage confound, not the ATR axis. The ATR-inhibitor "
            "separation may not be read as mechanism support. ⚠ The residuals are already "
            "line-median-corrected, so a control separating here means the confound survives that "
            "correction — check `null_arm_lineage_composition` before reading anything else.")
    elif mach_hits:
        v["verdict"] = "NULL_WITH_WORKING_INSTRUMENT"
        v["verdict_reading"] = (
            "ATM-null lines are NOT detectably more ATR-inhibitor-sensitive in this residual space, "
            "but the same pipeline DOES recover the BRCA/PARP-inhibitor association (" +
            ", ".join(mach_hits) + "). So the residual space can resolve a genotype-drug association "
            "of this kind, and the ATM/ATRi null is a real negative at the power available — bounded "
            "by the minimum detectable effect reported on every row, not by an instrument failure.")
    else:
        v["verdict"] = "INSTRUMENT_CANNOT_DETECT"
        v["verdict_reading"] = (
            "⛔ NEITHER the ATM/ATR-inhibitor association NOR the BRCA/PARP-inhibitor machinery "
            "control is detectable in this residual space at the arm sizes available. The residual "
            "space is therefore not shown to resolve ANY genotype-drug association, including the "
            "one part D's whole part-D instrument is built to detect. Part D's ATM row is "
            "UNINFORMATIVE rather than NEGATIVE, and every null part D reports on the drug-response "
            "axis means less than the assessment currently says. This is the outcome that most "
            "constrains what the paper may claim, and it is stated at full strength here.")
    return v


# =============================================================================================
# plumbing
# =============================================================================================
def _write(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, default=str)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true",
                    help="fetch DepMap calls into the inputs cache (network; CI only)")
    ap.add_argument("--check", action="store_true",
                    help="re-derive from the cache and diff against the committed artifact")
    args = ap.parse_args()

    if args.refresh:
        inp = refresh()
    else:
        try:
            with open(INPUTS, encoding="utf-8") as fh:
                inp = json.load(fh)
        except OSError:
            inp = {"_status": "inputs cache absent — run --refresh in CI"}

    art = derive(inp)

    if args.check:
        try:
            with open(OUT, encoding="utf-8") as fh:
                old = json.load(fh)
        except OSError:
            print("no committed artifact to check against", file=sys.stderr)
            return 1
        a = json.dumps(old, sort_keys=True, default=str)
        b = json.dumps(art, sort_keys=True, default=str)
        if a == b:
            print("--check OK: the artifact re-derives byte-identically from its inputs cache")
            return 0
        print("--check DRIFT: the artifact does not match a re-derive from its inputs cache",
              file=sys.stderr)
        return 1

    # ⛔ NEVER WRITE A STUB OVER A REAL ARTIFACT, EVEN LOCALLY.
    # `artifact_stub_guard` protects the CI PUBLISH path, but nothing protects the working tree: a
    # session running this module in the dev sandbox (where the DepMap fetch cannot run, so the
    # inputs cache is absent) would derive a stub and overwrite the committed result with it, ready
    # for the next `git add`. That is the same failure that made `emc-fet-idr-census.json` a two-key
    # stub on `main`, arriving by a different door.
    if art.get("_verdict") == "NO_DATA" and os.path.exists(OUT):
        print(f"REFUSING to overwrite {os.path.relpath(OUT)} with a NO_DATA stub "
              f"({art.get('_status')}). Run --refresh in CI; the committed artifact is untouched.",
              file=sys.stderr)
        return 1

    _write(OUT, art)
    print(json.dumps({"verdict": art.get("verdict"),
                      "n_null_arm_ATM": ((art.get("by_gene") or {}).get("ATM") or {})
                                        .get("join", {}).get("n_null_arm_primary"),
                      "n_intact_arm_ATM": ((art.get("by_gene") or {}).get("ATM") or {})
                                          .get("join", {}).get("n_intact_arm_primary"),
                      "artifact": os.path.relpath(OUT)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
