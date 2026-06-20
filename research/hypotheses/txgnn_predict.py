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
EMC_RX = "myxoid chondrosarcoma"
TOPN = 50

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

    # --- locate the EMC disease node by name ------------------------------------
    matches = {k: v for k, v in disease_idx2name.items() if EMC_RX in str(v).lower()}
    log("disease-name matches for /%s/: %s" % (EMC_RX, matches))
    emc_items = {k: v for k, v in matches.items() if "extraskeletal" in str(v).lower()} or matches
    if not emc_items:
        raise RuntimeError("EMC disease node not found in id mapping")
    emc_idx = float(next(iter(emc_items)))
    emc_name = str(emc_items[next(iter(emc_items))])
    log(f"Using EMC disease node: idx={emc_idx} name={emc_name!r}")

    # --- run the model on EMC, indication relation -------------------------------
    teval = TxEval(model=model)
    out = teval.eval_disease_centric(disease_idxs=[emc_idx], relation="indication",
                                     save_result=False, return_raw=True)
    log("=== eval output structure ===")
    summarize(out)

    # --- best-effort extraction of ranked (drug, score) --------------------------
    ranked = extract_ranked(out, drug_id2name)
    log(f"extracted {len(ranked)} ranked drugs")

    result = {
        "model": "TxGNN (Huang et al., Nat Med 2024) — pretrained 'complex_disease' weights",
        "source": "https://github.com/mims-harvard/TxGNN ; weights via the repo's Google Drive link",
        "relation": "indication",
        "disease": {"name": emc_name, "kg_idx": emc_idx, "mondo_hint": "extraskeletal myxoid chondrosarcoma"},
        "note": "Genuine zero-shot output of the trained TxGNN model, NOT a hand-built heuristic. A high score is a model-predicted repurposing hypothesis to triage under METHODOLOGY, not evidence of efficacy.",
        "topDrugs": ranked[:TOPN],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)
    log(f"WROTE {OUT} with {len(result['topDrugs'])} drugs")
    if ranked[:15]:
        log("Top 15:")
        for d in ranked[:15]:
            log("  %-32s %.4f" % (str(d.get('drug'))[:32], d.get('score', float('nan'))))

def extract_ranked(out, drug_id2name):
    """TxGNN eval returns {'prediction': {disease_id: {drug_id: score}}, 'label':..., 'result':...}.
    Pull the per-drug indication scores for the (single) disease and sort descending."""
    pairs = []
    pred = out.get("prediction") if isinstance(out, dict) else None
    if isinstance(pred, dict) and pred:
        disease_id = next(iter(pred))           # single disease evaluated
        scores = pred[disease_id]               # {drug_id: score}
        if isinstance(scores, dict):
            for drug_id, sc in scores.items():
                try:
                    s = float(sc)
                except Exception:
                    continue
                pairs.append({"drug_id": str(drug_id),
                              "drug": str(drug_id2name.get(str(drug_id), drug_id)),
                              "score": round(s, 5)})
    if not pairs:
        # fallback: result -> 'Ranked List' -> [ [name/id, score], ... ]
        res = (out.get("result") if isinstance(out, dict) else None) or {}
        rl = res.get("Ranked List") or {}
        if isinstance(rl, dict) and rl:
            lst = next(iter(rl.values()))
            for item in (lst or []):
                try:
                    name, sc = item[0], float(item[1])
                except Exception:
                    continue
                pairs.append({"drug": str(drug_id2name.get(str(name), name)), "score": round(sc, 5)})
    pairs.sort(key=lambda d: d["score"], reverse=True)
    return pairs

def _isnum(x):
    try:
        float(x); return True
    except Exception:
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("FATAL:\n" + traceback.format_exc())
        sys.exit(1)
