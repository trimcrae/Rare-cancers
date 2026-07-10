#!/usr/bin/env python3
"""
MATCHED 8XTT-frame decoy null for the denovo_401 selectivity re-dock (JCIM reviewer high-priority ask).

WHY. nr4a3_8xtt_redock.py found the carried lead denovo_401 NR4A3-favoured in ALL 4 cavity-bearing 8XTT NMR
conformers (models 2,8,20,6; MM-GBSA min-margin median 9.4 kcal/mol). A reviewer correctly flagged that that
number has NO matched specificity control, and our own work proved MM-GBSA margins are strongly receptor-
FRAME-dependent (selectivity_calibration.py: a 38-drug non-NR4A decoy null scored `confirmed_selective` ~39%
of the time on a DIFFERENT funnel/frame). So the release-frame decoy null (DECOY_2026_06_30) CANNOT validate
an 8XTT-frame margin — a different frame inflates the decoy distribution enormously. The null must be MATCHED:
the SAME 38 decoys through the SAME 4 8XTT conformers + SAME paralogue reference receptors + SAME single-
snapshot MM-GBSA protocol, then report denovo_401's percentile rank against THAT null, per conformer.

WHAT (all reuse — no new docking/scoring physics; the whole point is a *matched* null):
  1. reuse nr4a3_8xtt_redock.protein_only_model + nr4a3_8xtt_benchmark's fetch/split/UniProt->8XTT map +
     nr4a3_8xtt_pocketminer.select_models to extract the SAME druggable 8XTT conformers (models 2,8,20,6);
  2. reuse the SAME paralogue reference states denovo_401 used — the matrix nr4a1-opened.pdb / nr4a2-opened.pdb
     receptors, boxed by the SAME nr4a3_warhead.map_pocket_to_paralogue mapping (never re-selected);
  3. dock the 38 decoys (decoy_library.DECOY_SMILES) into each conformer + each paralogue with the SAME
     nr4a3_warhead.dock_into (smina), and MM-GBSA-rescore every pose with the SAME
     mmgbsa_energy.endpoint_dG single-snapshot GBn2 endpoint denovo_401 used (matched — NOT multi-snapshot;
     the archived denovo_401 8XTT run is single-snapshot, so a multi-snapshot null would be UNMATCHED);
  4. per conformer + pooled: the decoy NR4A3-vs-paralogue MIN-margin distribution and denovo_401's
     percentile rank + add-one one-sided empirical p against that matched null, plus the 95th-pct bar and a
     pass/fail (denovo_401 margin > decoy 95th percentile).

Output: nr4a3-8xtt-decoy-null.json (per-conformer + pooled decoy margin stats, denovo_401 margin, percentile,
empirical p, pass/fail), checkpointed after EACH decoy (Continuous S3 upload keeps the partial as deliverable).
PURE logic (percentile / add-one p / distribution / verdict aggregation) is dependency-free and unit-tested in
tests/test_8xtt_decoy_null.py; the heavy dock/MM-GBSA glue is lazy-imported and mirrors the re-dock exactly.
"""
import json
import os
import sys
import traceback

import nr4a3_8xtt_benchmark as bm
import nr4a3_8xtt_pocketminer as pm       # reuse select_models (8XTT conformer resolution)
import nr4a3_8xtt_redock as rd            # reuse protein_only_model + PARALOGUES/KEY (matched receptors)
import mmgbsa_select as ms               # reuse margins (unit-tested selectivity arithmetic)
import selectivity_calibration as sc     # reuse percentile / decoy_threshold (the null-bar machinery)
import decoy_library as dl               # the SAME 38 non-NR4A decoys

PARALOGUES = rd.PARALOGUES
KEY = rd.KEY

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
MATRIX_DIR = os.environ.get("MATRIX_DIR", os.path.join(IN, "matrix"))   # mounted s3://<bucket>/nr4a3-matrix
# The denovo_401 8XTT re-dock result (per-conformer denovo_401 margins to rank against the matched null).
# Mounted (redock channel) or the committed repo copy; NEVER fabricated.
REDOCK_JSON = os.environ.get("REDOCK_JSON", "")
REQUESTED_MODELS = os.environ.get("MODELS", rd.DEFAULT_MODELS)
MINIMIZE_ITERS = int(os.environ.get("MMGBSA_MIN_ITERS", "250"))
BAND = float(os.environ.get("SELECT_BAND", str(ms.BAND)))
NULL_Q = float(os.environ.get("NULL_PCT", "95.0"))                      # the pass bar = 95th pct of the null
OUT_JSON = "nr4a3-8xtt-decoy-null.json"


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_decoy_null.py (no smina/openmm/rdkit/biopython/network).
# ==================================================================================================

def percentile_rank(value, null_values):
    """Percentile rank (0..100) of `value` in `null_values` = % of the null STRICTLY below it. A high
    rank means denovo_401 sits in the right tail of the matched decoy null. None on empty null. Pure."""
    if value is None or not null_values:
        return None
    n = len(null_values)
    n_below = sum(1 for x in null_values if x < value)
    return round(100.0 * n_below / n, 2)


def empirical_p_add_one(value, null_values):
    """One-sided (right-tail) empirical p-value with an add-one pseudocount (Phipson & Smyth):
        p = (#{null >= value} + 1) / (n + 1)
    Conservative (never 0), the standard way to test 'is denovo_401 more NR4A3-selective than a random
    non-NR4A drug in the SAME matched funnel?'. None on empty null. Pure."""
    if value is None or not null_values:
        return None
    n = len(null_values)
    n_ge = sum(1 for x in null_values if x >= value)
    return round((n_ge + 1) / (n + 1), 4)


def decoy_null_verdict(denovo_margin, decoy_margins, band=BAND, q=NULL_Q):
    """One conformer's (or the pooled) matched-null verdict for denovo_401.

    `decoy_margins`: the decoy NR4A3-vs-paralogue MIN-margins in this frame (add-one/percentile null).
    Returns a dict:
      n_decoys            : # decoys with a margin in this frame,
      decoy_margin_stats  : bm.distribution_stats(decoy_margins, threshold=band),
      decoy_95th_bar      : the q-th percentile of the decoy null (the pass bar),
      denovo401_margin    : denovo_401's margin in this frame,
      percentile_rank     : % of decoys strictly below denovo_401,
      n_decoys_above      : # decoys with margin >= denovo_401 (0 = strictly best),
      empirical_p_add_one : (n_decoys_above + 1)/(n + 1), one-sided,
      pass_95th           : denovo_401 margin > decoy q-th percentile bar (credible vs the matched null),
      verdict             : 'above-null' | 'within-null' | 'no-data'.
    Pure — all inputs are plain numbers; reuses sc.percentile/decoy_threshold + bm.distribution_stats."""
    stats = bm.distribution_stats(decoy_margins, threshold=band)
    n = stats.get("n", 0)
    bar = sc.decoy_threshold(decoy_margins, q) if n else None
    if n == 0:
        return {"n_decoys": 0, "decoy_margin_stats": stats, "decoy_95th_bar": None,
                "denovo401_margin": denovo_margin, "percentile_rank": None, "n_decoys_above": None,
                "empirical_p_add_one": None, "pass_95th": None, "verdict": "no-data"}
    n_above = None if denovo_margin is None else sum(1 for d in decoy_margins if d >= denovo_margin)
    pass_bar = (denovo_margin is not None and bar is not None and denovo_margin > bar)
    if denovo_margin is None:
        verdict = "no-data"
    elif pass_bar:
        verdict = "above-null"
    else:
        verdict = "within-null"
    return {"n_decoys": n, "decoy_margin_stats": stats,
            "decoy_95th_bar": round(bar, 3) if bar is not None else None,
            "denovo401_margin": denovo_margin, "percentile_rank": percentile_rank(denovo_margin, decoy_margins),
            "n_decoys_above": n_above, "empirical_p_add_one": empirical_p_add_one(denovo_margin, decoy_margins),
            "pass_95th": pass_bar, "verdict": verdict, "q": q, "band": band}


def collect_decoy_margins(decoy_rows, model):
    """From the recorded per-decoy rows, the list of MIN-margins in one conformer `model` (skips None /
    errored decoys). `decoy_rows`: [{"name":.., "per_conformer": {str(model): min_margin|None}}]. Pure."""
    key = str(model)
    out = []
    for r in decoy_rows:
        m = (r.get("per_conformer") or {}).get(key)
        if m is not None:
            out.append(m)
    return out


def collect_pooled_margins(decoy_rows, models):
    """Pool every decoy's MIN-margin across all scored conformers into one null (the pooled matched null).
    Pure."""
    pooled = []
    for model in models:
        pooled.extend(collect_decoy_margins(decoy_rows, model))
    return pooled


def denovo401_margins_from_redock(redock):
    """Extract denovo_401's per-conformer MIN-margins from a parsed nr4a3-8xtt-redock-denovo401.json dict.

    Returns {"per_conformer": {model:int -> min_margin|None}, "median": float|None}. Fail-loud (raises) if
    the redock JSON has no per_conformer with mm_min_margin — we must NOT rank against a fabricated value.
    Pure (dict in, dict out)."""
    per = {}
    for c in redock.get("per_conformer", []):
        model = c.get("model")
        if model is None:
            continue
        per[int(model)] = c.get("mm_min_margin")
    present = [m for m in per.values() if m is not None]
    if not present:
        raise ValueError("redock JSON carries no denovo_401 mm_min_margin — cannot rank against the null")
    median = bm.distribution_stats(present, threshold=0.0).get("median")
    return {"per_conformer": per, "median": median}


def summarize_null(decoy_rows, denovo_per_conformer, models, band=BAND, q=NULL_Q):
    """Assemble the per-conformer + pooled matched-null report.

    `decoy_rows`         : recorded per-decoy rows (collect_decoy_margins reads them),
    `denovo_per_conformer`: {model:int -> denovo_401 min_margin|None} (from the redock JSON),
    `models`             : the conformers scored (ints).
    Returns {"per_conformer": {model: verdict}, "pooled": verdict, "verdict": overall, "rationale": str}.
    Overall: 'above-null' if denovo_401 clears the 95th-pct bar in a MAJORITY of scored conformers AND
    pooled; 'mixed' if it clears some; 'within-null' if none; 'no-data' if nothing scored. Pure."""
    per = {}
    n_pass = 0
    n_scored = 0
    for model in models:
        null_m = collect_decoy_margins(decoy_rows, model)
        v = decoy_null_verdict(denovo_per_conformer.get(model), null_m, band=band, q=q)
        per[str(model)] = v
        if v["verdict"] != "no-data":
            n_scored += 1
            if v["pass_95th"]:
                n_pass += 1
    pooled_null = collect_pooled_margins(decoy_rows, models)
    # denovo_401 pooled reference = the median of its per-conformer margins (its central 8XTT margin).
    dn_present = [denovo_per_conformer.get(m) for m in models if denovo_per_conformer.get(m) is not None]
    dn_pooled = bm.distribution_stats(dn_present, threshold=0.0).get("median") if dn_present else None
    pooled = decoy_null_verdict(dn_pooled, pooled_null, band=band, q=q)

    if n_scored == 0:
        verdict, rationale = "no-data", "no conformer produced a matched decoy null (docking/scoring failed)"
    elif n_pass > n_scored / 2 and pooled["pass_95th"]:
        verdict = "above-null"
        rationale = (f"denovo_401 clears the matched-null 95th-pct bar in {n_pass}/{n_scored} 8XTT conformers "
                     f"AND pooled (pooled margin {pooled['denovo401_margin']} > {pooled['decoy_95th_bar']} "
                     f"kcal/mol; pooled add-one p {pooled['empirical_p_add_one']}); its 8XTT selectivity is "
                     "credible against a matched non-NR4A decoy null, not a frame artefact.")
    elif n_pass > 0 or pooled["pass_95th"]:
        verdict = "mixed"
        rationale = (f"denovo_401 clears the matched-null bar in {n_pass}/{n_scored} conformers "
                     f"(pooled pass={pooled['pass_95th']}, pooled add-one p {pooled['empirical_p_add_one']}); "
                     "the 8XTT-frame selectivity is frame-sensitive relative to the decoy null — report the spread.")
    else:
        verdict = "within-null"
        rationale = (f"denovo_401 clears the matched-null bar in 0/{n_scored} conformers "
                     f"(pooled add-one p {pooled['empirical_p_add_one']}); its 8XTT margin is INSIDE the decoy "
                     "null — the apparent selectivity is not distinguishable from random non-NR4A drug-like matter "
                     "in the SAME matched funnel.")
    return {"per_conformer": per, "pooled": pooled, "n_conformers_scored": n_scored,
            "n_conformers_pass": n_pass, "band": band, "q": q, "verdict": verdict, "rationale": rationale}


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — smina/openmm/rdkit/biopython/network live here).
# Mirrors nr4a3_8xtt_redock.main() step-for-step so the null is MATCHED, then loops the 38 decoys.
# ==================================================================================================

def _read(path):
    with open(path) as fh:
        return fh.read()


def _load_redock_denovo401():
    """Parse denovo_401's per-conformer margins from the mounted redock JSON or the committed repo copy.
    Fail-loud if neither is present (we must not invent denovo_401's numbers)."""
    candidates = [REDOCK_JSON] if REDOCK_JSON else []
    candidates += [
        os.path.join(MATRIX_DIR, "nr4a3-8xtt-redock-denovo401.json"),
        os.path.join(IN, "..", "..", "results", "nr4a3-8xtt-redock", "nr4a3-8xtt-redock-denovo401.json"),
        os.path.join(IN, "results", "nr4a3-8xtt-redock", "nr4a3-8xtt-redock-denovo401.json"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            try:
                return denovo401_margins_from_redock(json.load(open(p))), p
            except Exception as e:  # noqa: BLE001
                print(f"  redock JSON {p} unusable: {e}", file=sys.stderr)
    raise RuntimeError("no usable nr4a3-8xtt-redock-denovo401.json found (mount it as REDOCK_JSON or the "
                       "matrix channel) — cannot rank denovo_401 against the matched null without its margins")


def _write(res):
    with open(os.path.join(OUT, OUT_JSON), "w") as fh:
        json.dump(res, fh, indent=2)


def _load_checkpoint():
    """Resume: return (rows, done_names) from a prior partial nr4a3-8xtt-decoy-null.json if present."""
    p = os.path.join(OUT, OUT_JSON)
    if not os.path.exists(p):
        return [], set()
    try:
        prev = json.load(open(p))
    except Exception:  # noqa: BLE001
        return [], set()
    rows = [r for r in prev.get("decoy_rows", []) if r.get("name") and not r.get("error")]
    return rows, {r["name"] for r in rows}


def _pose_from_sdf(pose_sdf, label):
    import mmgbsa_energy as mme
    try:
        poses = mme.load_poses(pose_sdf)
    except Exception as e:  # noqa: BLE001
        print(f"  could not load poses from {pose_sdf}: {e}", file=sys.stderr)
        return {}
    return poses if label is None else poses.get(label)


def _dock_all_into(receptor_pdb, center, sdf, tag):
    """Dock the full decoy SDF into one receptor (matched box) and return {label: OpenFF pose}."""
    import nr4a3_warhead as wh
    _scores, pose_sdf = wh.dock_into(receptor_pdb, center, sdf, tag)
    poses = _pose_from_sdf(pose_sdf, None) or {}
    return poses


def main():
    import nr4a3_warhead as wh
    import nr4a3_dock as dock
    import mmgbsa_energy as mme
    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "decoy_null_work")
    os.makedirs(work, exist_ok=True)
    wh.OUT = work

    # Fail FAST if no GPU OpenMM platform (MM-GBSA has NO CPU fallback) — die in seconds, not after docking.
    omm, _app, ommunit, *_ = mme._mm()
    mme._platform(omm, ommunit)

    denovo, redock_src = _load_redock_denovo401()
    denovo_per = denovo["per_conformer"]

    res = {"_note": "MATCHED 8XTT-frame decoy null for denovo_401: the SAME 38 non-NR4A decoys through the "
                    "SAME 4 druggable 8XTT conformers (models 2,8,20,6) + SAME matrix paralogue receptors + "
                    "SAME single-snapshot GBn2 MM-GBSA endpoint denovo_401 used, so denovo_401's per-conformer "
                    "NR4A3-selectivity can be ranked against a frame-matched null (percentile + add-one p + "
                    "95th-pct bar). Single-snapshot to MATCH the archived denovo_401 8XTT run — a multi-snapshot "
                    "null would be unmatched. Enthalpy-only TRIAGE, not affinity.",
           "matched_to": {"redock_json": redock_src, "denovo401_per_conformer": denovo_per,
                          "denovo401_median": denovo["median"]},
           "params": {"minimize_iters": MINIMIZE_ITERS, "band": BAND, "null_pct": NULL_Q,
                      "requested_models": REQUESTED_MODELS, "n_decoys_library": dl.n_decoys()},
           "decoy_rows": [], "summary": {}}

    # 1) build the 38-decoy SDF (RDKit 3D embed) — the docking ligand set (SAME set as the release-frame null).
    decoy_json = dl.decoy_candidate_json()
    ligands = [(c["name"], c["name"], c["smiles"]) for c in decoy_json["candidates"]]
    sdf = os.path.join(work, "decoys.sdf")
    kept = dock.make_sdf(ligands, sdf)
    kept_labels = [lab for lab, _cid, _smi in kept]
    res["params"]["n_decoys_embedded"] = len(kept_labels)
    if not kept_labels:
        res["_status"] = "RDKit embedded 0 decoys"
        _write(res); sys.exit("ABORT: no decoy SDF")
    print(f"  embedded {len(kept_labels)}/{dl.n_decoys()} decoys", flush=True)

    # 2) fetch 8XTT + AF2 and build the SAME UniProt->8XTT numbering map (reuse redock/benchmark machinery).
    xtt_path = bm.fetch_rcsb(bm.PDB_ID, os.path.join(work, f"{bm.PDB_ID}.pdb"))
    models = bm.split_models(_read(xtt_path))
    if not models:
        res["_status"] = f"no models parsed from {bm.PDB_ID}"
        _write(res); sys.exit(f"ABORT: no models in {bm.PDB_ID}")
    af2_path = rd._fetch_af2(os.path.join(work, f"AF-{bm.UNIPROT}.pdb"))
    _af2_ca, af2_resnums, af2_seq = bm.af2_lbd_ca(af2_path)
    _c, xtt_resnums0, xtt_seq0, _ca0 = bm.chain_ca(models[0])
    uni_to_auth, identity = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq0, xtt_resnums0)
    mapped_pocket5 = sorted({uni_to_auth[u] for u in bm.POCKET5 if u in uni_to_auth})
    if not mapped_pocket5:
        res["_status"] = "no Pocket-5 residues mapped onto 8XTT — cannot box"
        _write(res); sys.exit("ABORT: empty Pocket-5 map")
    json.dump(mapped_pocket5, open(os.path.join(work, "nr4a3_pocket_authnums.json"), "w"))
    chosen = pm.select_models(range(1, len(models) + 1), REQUESTED_MODELS)
    res["_method"] = {"pdb": bm.PDB_ID, "alignment_identity": round(identity, 4),
                      "mapped_pocket5_8xtt": mapped_pocket5, "n_models": len(models),
                      "conformers_scored": chosen}
    print(f"  8XTT: {len(models)} models; identity {identity:.3f}; docking {len(kept_labels)} decoys into "
          f"models {chosen} + {PARALOGUES}", flush=True)

    # 3) MATCHED receptors: the 4 conformers (protein-only) + the SAME matrix paralogue-opened receptors.
    #    NR4A3 reference receptor (first chosen conformer) for the paralogue pocket mapping (as redock).
    first_rec = os.path.join(work, "nr4a3_ref_for_paralogue_map.pdb")
    with open(first_rec, "w") as fh:
        fh.write(rd.protein_only_model(models[chosen[0] - 1]))
    pocket_auth = json.load(open(os.path.join(work, "nr4a3_pocket_authnums.json")))

    receptors = {}                                   # tag -> (rec_pdb, {label: pose})
    # 3a) conformers
    for model in chosen:
        rec_pdb = os.path.join(work, f"8xtt_model{model}_nr4a3.pdb")
        with open(rec_pdb, "w") as fh:
            fh.write(rd.protein_only_model(models[model - 1]))
        center, _n = wh.pocket_box(rec_pdb, mapped_pocket5)
        poses = _dock_all_into(rec_pdb, center, sdf, f"nr4a3_m{model}")
        receptors[f"m{model}"] = (rec_pdb, poses)
        print(f"  docked decoys into 8XTT model {model}: {len(poses)} poses", flush=True)
    # 3b) SAME matrix paralogue receptors, SAME mapping/box as denovo_401 (never re-selected).
    para_ok = {}
    for tag in PARALOGUES:
        rec = os.path.join(MATRIX_DIR, f"{tag}-opened.pdb")
        if not os.path.exists(rec):
            print(f"  WARNING: matrix paralogue receptor missing: {rec} (margin vs {KEY[tag]} will be absent)",
                  file=sys.stderr)
            receptors[tag] = (None, {})
            para_ok[tag] = False
            continue
        para_res = wh.map_pocket_to_paralogue(first_rec, rec, pocket_auth)
        if not para_res:
            print(f"  WARNING: 0 pocket residues mapped onto {tag}", file=sys.stderr)
            receptors[tag] = (rec, {})
            para_ok[tag] = False
            continue
        center, _n = wh.pocket_box(rec, para_res)
        poses = _dock_all_into(rec, center, sdf, tag)
        receptors[tag] = (rec, poses)
        para_ok[tag] = True
        print(f"  docked decoys into {KEY[tag]} ({rec}): {len(poses)} poses", flush=True)
    res["_method"]["paralogue_receptors_ok"] = para_ok
    if not any(para_ok.values()):
        res["_status"] = "no matrix paralogue receptor available — cannot compute a matched margin"
        _write(res); sys.exit("ABORT: no paralogue reference states (mount the matrix channel)")

    # 4) prepare each receptor topology ONCE (reused across all 38 decoys — engineering-free speed-up).
    prepared = {}
    for tag, (rec_pdb, _poses) in receptors.items():
        if rec_pdb is None:
            prepared[tag] = None
            continue
        try:
            prepared[tag] = mme.prepare_receptor(rec_pdb)
        except Exception as e:  # noqa: BLE001
            prepared[tag] = None
            print(f"  prepare_receptor({tag}) failed: {e}", file=sys.stderr)

    cache = os.path.join(work, "sysgen_cache.json")

    # 5) per-decoy MM-GBSA across all matched receptors; checkpoint after EACH decoy (continuous upload).
    rows, done = _load_checkpoint()
    if done:
        print(f"  resuming: {len(done)} decoys already scored", flush=True)
    res["decoy_rows"] = rows
    for label in kept_labels:
        if label in done:
            continue
        row = {"name": label, "per_conformer": {}, "paralogue_dG": {}}
        try:
            # paralogue ΔG (shared across conformers for this decoy).
            dg_para = {}
            for tag in PARALOGUES:
                prep = prepared.get(tag)
                pose = receptors[tag][1].get(label)
                if prep is None or pose is None:
                    dg_para[tag] = None
                    continue
                rec_top, rec_pos = prep
                dg_para[tag] = mme.endpoint_dG(rec_top, rec_pos, pose, minimize_iters=MINIMIZE_ITERS,
                                               cache=cache)["dG"]
            row["paralogue_dG"] = {KEY[t]: dg_para.get(t) for t in PARALOGUES}
            # per conformer: NR4A3 ΔG -> min-margin vs the two paralogues.
            for model in chosen:
                prep3 = prepared.get(f"m{model}")
                pose3 = receptors[f"m{model}"][1].get(label)
                if prep3 is None or pose3 is None:
                    row["per_conformer"][str(model)] = None
                    continue
                rt, rp = prep3
                dg3 = mme.endpoint_dG(rt, rp, pose3, minimize_iters=MINIMIZE_ITERS, cache=cache)["dG"]
                mar = ms.margins(dg3, dg_para.get("nr4a1"), dg_para.get("nr4a2"))
                row["per_conformer"][str(model)] = mar["min_margin"]
            print(f"  decoy {label}: per-conformer min-margins "
                  f"{ {k: row['per_conformer'][k] for k in row['per_conformer']} }", flush=True)
        except Exception as e:  # noqa: BLE001 — one bad decoy never voids the null
            row["error"] = str(e)[:300]
            print(f"  decoy {label}: ERROR {e}", file=sys.stderr, flush=True)
        rows.append(row)
        res["decoy_rows"] = rows
        res["summary"] = summarize_null([r for r in rows if not r.get("error")], denovo_per, chosen,
                                        band=BAND, q=NULL_Q)
        _write(res)   # checkpoint after EACH decoy

    res["summary"] = summarize_null([r for r in rows if not r.get("error")], denovo_per, chosen,
                                    band=BAND, q=NULL_Q)
    res["_status"] = "ok"
    _write(res)
    print(json.dumps({"summary_verdict": res["summary"]["verdict"],
                      "rationale": res["summary"]["rationale"]}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        os.makedirs(OUT, exist_ok=True)
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, OUT_JSON), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
