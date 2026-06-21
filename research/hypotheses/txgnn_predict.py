#!/usr/bin/env python3
"""Run the REAL pretrained TxGNN model to get genuine drug-repurposing predictions for
EMC (roadmap #3). Loads the public TxGNN weights + knowledge graph, finds the EMC
disease node, and ranks therapeutic candidates by the model's indication score.

This is NOT a proxy or a hand-built heuristic: it is the trained TxGNN foundation model
(Huang et al., Nat Med 2024) evaluated zero-shot on EMC. Runs in CI (see
txgnn-run.yml); the dev sandbox has no network and no ML stack.

Output: research/hypotheses/txgnn-emc-predictions.json
"""
import os, sys, json, traceback

OUT = "research/hypotheses/txgnn-emc-predictions.json"
COMPARISON_OUT = "research/hypotheses/txgnn-relatives-comparison.json"
EMC_RX = "myxoid chondrosarcoma"
TOPN = 100

# EMC-relevant drugs (our mechanism catalog + DGIdb enumeration) — we report WHERE TxGNN
# ranked each in its full 7,957-drug list, as a triangulation signal (corroboration vs.
# divergence), independent of TxGNN's own top hits.
RELEVANT = [
    "pazopanib", "sunitinib", "sorafenib", "regorafenib", "cabozantinib", "axitinib",
    "nintedanib", "vandetanib", "tivozanib", "fruquintinib", "lenvatinib", "anlotinib", "apatinib",
    "imatinib", "dasatinib", "nilotinib", "ponatinib", "masitinib", "midostaurin", "quizartinib", "ripretinib",
    "trabectedin", "doxorubicin", "ifosfamide", "eribulin", "gemcitabine",
    "sirolimus", "everolimus", "pioglitazone", "rosiglitazone", "zaltoprofen",
    "pembrolizumab", "nivolumab",
]

def log(*a):
    print(*a, flush=True)

def summarize(obj, depth=0, maxd=3):
    """Verbosely describe an unknown return structure for debugging."""
    pad = "  " * depth
    t = type(obj).__name__
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            log(f"{pad}DataFrame cols={list(obj.columns)} shape={obj.shape}")
            log(obj.head(5).to_string())
            return
    except Exception:
        pass
    if isinstance(obj, dict):
        log(f"{pad}dict keys={list(obj.keys())[:10]} (n={len(obj)})")
        if depth < maxd:
            for k in list(obj.keys())[:3]:
                log(f"{pad}- key {k!r}:")
                summarize(obj[k], depth + 1, maxd)
    elif isinstance(obj, (list, tuple)):
        log(f"{pad}{t} len={len(obj)}")
        if obj and depth < maxd:
            summarize(obj[0], depth + 1, maxd)
    else:
        s = repr(obj)
        log(f"{pad}{t}: {s[:300]}")

def _f(x):
    try:
        return float(x)
    except Exception:
        return x

def build_idx2name(mapping, kind):
    """Build {node_idx(float) -> name(str)} for a node kind ('disease'/'drug') from
    TxGNN's retrieve_id_mapping(), tolerating several key layouts."""
    if not isinstance(mapping, dict):
        return {}
    keys = {k.lower(): k for k in mapping.keys()}
    def get(*subs):
        for lk, ok in keys.items():
            if kind in lk and all(s in lk for s in subs):
                return mapping[ok]
        return None
    idx2name = get("idx2name") or get("idx", "name")
    if isinstance(idx2name, dict) and idx2name:
        return {_f(k): str(v) for k, v in idx2name.items()}
    idx2id = get("idx2id")
    id2name = get("id2name") or get("id", "name")
    out = {}
    if isinstance(idx2id, dict) and isinstance(id2name, dict):
        for idx, _id in idx2id.items():
            nm = id2name.get(_id, id2name.get(str(_id), _id))
            out[_f(idx)] = str(nm)
    return out

def build_id2name(mapping, kind):
    """{node_id(str) -> name(str)} for a node kind, from retrieve_id_mapping()."""
    if not isinstance(mapping, dict):
        return {}
    keys = {k.lower(): k for k in mapping.keys()}
    for lk, ok in keys.items():
        if kind in lk and ("id2name" in lk or ("id" in lk and "name" in lk)):
            d = mapping[ok]
            if isinstance(d, dict) and d:
                return {str(k): str(v) for k, v in d.items()}
    return {}

def main():
    import numpy as np, pandas as pd
    import torch, dgl
    log("versions: torch", torch.__version__, "| dgl", dgl.__version__,
        "| numpy", np.__version__, "| pandas", pd.__version__)
    from txgnn import TxData, TxGNN, TxEval

    txdata = TxData(data_folder_path="./data")
    txdata.prepare_split(split="complex_disease", seed=42)

    model = TxGNN(data=txdata, weight_bias_track=False,
                  proj_name="TxGNN", exp_name="TxGNN", device="cpu")
    # README's documented architecture for the released weights
    model.model_initialize(n_hid=100, n_inp=100, n_out=100, proto=True, proto_num=3,
                           attention=False, sim_measure="all_nodes_profile",
                           agg_measure="rarity", num_walks=200, path_length=2)
    model.load_pretrained("./model_ckpt")
    log("Pretrained model loaded.")

    # --- diagnostics: schema of the data objects --------------------------------
    df = txdata.df_train if getattr(txdata, "df_train", None) is not None else txdata.df
    log("df_train columns:", list(df.columns))
    try:
        log("txdata.df columns:", list(txdata.df.columns))
    except Exception as e:
        log("no txdata.df:", e)

    # Node names live in retrieve_id_mapping(), not in the edge list.
    mapping = txdata.retrieve_id_mapping()
    log("retrieve_id_mapping type:", type(mapping).__name__,
        "keys:", list(mapping.keys()) if isinstance(mapping, dict) else "n/a")

    disease_idx2name = build_idx2name(mapping, "disease")
    drug_id2name = build_id2name(mapping, "drug")
    log(f"disease idx->name: {len(disease_idx2name)} | drug id->name: {len(drug_id2name)}")
    # sample a few disease names so we can see the format
    for i, (k, v) in enumerate(disease_idx2name.items()):
        if i >= 3: break
        log("  sample disease:", k, "->", v)

    # --- locate EMC + two data-rich relatives (the sparsity stress-test) ---------
    TARGETS = [
        ("EMC", "extraskeletal myxoid chondrosarcoma"),
        ("chondrosarcoma", "chondrosarcoma (disease)"),
        ("soft tissue sarcoma", "soft tissue sarcoma"),
    ]
    picked = []  # (label, idx_float, name)
    for label, needle in TARGETS:
        exact = [(k, v) for k, v in disease_idx2name.items() if str(v).lower() == needle]
        cont = [(k, v) for k, v in disease_idx2name.items() if needle in str(v).lower()]
        hit = exact or cont
        if hit:
            k, v = hit[0]
            picked.append((label, float(k), str(v)))
            log(f"node for {label!r}: idx={float(k)} name={v!r}")
        else:
            log(f"NODE NOT FOUND for {label!r} (needle={needle!r})")
    if not picked:
        raise RuntimeError("no disease nodes found")

    # --- run the model once for all diseases, indication relation ----------------
    teval = TxEval(model=model)
    out = teval.eval_disease_centric(disease_idxs=[p[1] for p in picked], relation="indication",
                                     save_result=False, return_raw=True)
    log("=== eval output structure ===")
    summarize(out)

    preds = (out.get("prediction") if isinstance(out, dict) else {}) or {}
    names = ((out.get("result") if isinstance(out, dict) else {}) or {}).get("Name", {}) or {}

    def label_of(disease_id):
        nm = str(names.get(disease_id, "")).lower()
        for label, needle in TARGETS:
            if needle in nm or (nm and nm in needle):
                return label
        return nm or str(disease_id)

    comparison = []
    emc_block = None
    for disease_id, scores in preds.items():
        if not isinstance(scores, dict):
            continue
        ranked = ranked_from_scores(scores, drug_id2name)
        total = len(ranked)
        relevant = relevant_ranks(ranked, total)
        present = [r["percentile"] for r in relevant if r["rank"] is not None]
        median_pct = round(sorted(present)[len(present) // 2], 1) if present else None
        nm = str(names.get(disease_id, disease_id))
        label = label_of(disease_id)
        log(f"\n=== {label} ({nm}) : {total} drugs | relevant-drug median percentile = {median_pct} ===")
        for r in sorted([x for x in relevant if x["rank"]], key=lambda x: x["rank"])[:8]:
            log("  %-14s #%d (%.1f pct)" % (r["query"], r["rank"], r["percentile"]))
        comparison.append({
            "label": label, "disease": nm, "disease_id": disease_id, "totalRanked": total,
            "relevantMedianPercentile": median_pct,
            "topDrugs": ranked[:15], "relevantDrugRanks": relevant,
        })
        if "extraskeletal myxoid" in nm.lower():
            emc_block = {
                "model": "TxGNN (Huang et al., Nat Med 2024) — pretrained 'complex_disease' weights",
                "source": "https://github.com/mims-harvard/TxGNN ; weights via the repo's Google Drive link",
                "relation": "indication",
                "disease": {"name": nm, "disease_id": disease_id, "mondo_hint": "extraskeletal myxoid chondrosarcoma"},
                "note": "Genuine zero-shot output of the trained TxGNN model, NOT a hand-built heuristic. A high score is a model-predicted repurposing hypothesis to triage under METHODOLOGY, not evidence of efficacy.",
                "totalRanked": total, "topDrugs": ranked[:TOPN], "relevantDrugRanks": relevant,
            }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if emc_block:
        with open(OUT, "w") as f:
            json.dump(emc_block, f, indent=2)
        log(f"WROTE {OUT}")
    comp = {
        "purpose": "Sparsity stress-test: do our mechanism/enumeration drugs rank higher for EMC's "
                   "data-rich relatives (chondrosarcoma, soft-tissue sarcoma) than for EMC itself? A higher "
                   "relevantMedianPercentile for the relatives isolates EMC's sparse KG neighbourhood — not "
                   "model failure — as the cause of the EMC divergence.",
        "relation": "indication",
        "diseases": comparison,
    }
    with open(COMPARISON_OUT, "w") as f:
        json.dump(comp, f, indent=2)
    log(f"WROTE {COMPARISON_OUT}")
    log("\n=== SPARSITY STRESS-TEST SUMMARY (relevant-drug median percentile; higher = better corroboration) ===")
    for c in comparison:
        log("  %-22s %s pct  (n_drugs=%d)" % (c["label"], c["relevantMedianPercentile"], c["totalRanked"]))

def ranked_from_scores(scores, drug_id2name):
    """Turn a {drug_id: score} dict (TxGNN out['prediction'][disease_id]) into a list of
    {drug_id, drug, score} sorted by descending indication score."""
    pairs = []
    for drug_id, sc in scores.items():
        try:
            s = float(sc)
        except Exception:
            continue
        pairs.append({"drug_id": str(drug_id),
                      "drug": str(drug_id2name.get(str(drug_id), drug_id)),
                      "score": round(s, 5)})
    pairs.sort(key=lambda d: d["score"], reverse=True)
    return pairs

def relevant_ranks(ranked, total):
    """For each EMC-relevant drug (RELEVANT), find its rank/percentile in the full list."""
    out = []
    for q in RELEVANT:
        hit = next(((i, d) for i, d in enumerate(ranked, 1) if q in d["drug"].lower()), None)
        if hit:
            i, d = hit
            out.append({"query": q, "matched": d["drug"], "rank": i, "of": total,
                        "score": d["score"], "percentile": round(100.0 * (1 - i / total), 1)})
        else:
            out.append({"query": q, "matched": None, "rank": None, "of": total})
    return out

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("FATAL:\n" + traceback.format_exc())
        sys.exit(1)
