#!/usr/bin/env python3
"""
Score denovo_401's NR4A3-favoured ENDPOINT (MM-GBSA) score across ALL 20 deposited 8XTT NMR conformers,
with a per-conformer decoy null — reviewer P1 ask (comment 12 / P1.12).

WHY. denovo_401's endpoint MM-GBSA ΔG into NR4A3 was scored on a SINGLE AF2/metad frame. A reviewer
correctly asked whether that NR4A3-favoured endpoint score is a property of the LEAD or of the one FRAME:
does it survive across the *experimental* structural ensemble? PDB 8XTT is an apo NR4A3 LBD solution-NMR
ensemble of ~20 deposited conformers — the natural experimental test set. This job docks denovo_401 (and a
decoy set) into EACH of the 20 conformers, MM-GBSA endpoint-scores the pose(s), and asks, per conformer:
does denovo_401's endpoint score clear a matched decoy null (> the decoy q-th percentile), and where does
it rank among {denovo_401 ∪ decoys}? Then it aggregates across the 20 conformers: in HOW MANY does
denovo_401 clear the null, and what is the DISTRIBUTION of its rank.

HONEST SCOPE (read before trusting a number). This is an ENDPOINT-SCORE ROBUSTNESS check across the
experimental conformer ensemble — NOT a binding proof and NOT a selectivity proof:
  * MM-GBSA endpoint ΔG is enthalpy + implicit-solvent only, single minimized snapshot per pose — a
    better-than-docking TRIAGE energy, not an affinity (mmgbsa_energy.py scope note).
  * There is NO paralogue comparator here — this asks "is denovo_401 a favoured NR4A3 endpoint binder vs
    random drug-like matter, across experimental geometry?", not "is it NR4A3-selective vs NR4A1/2?"
    (that is the separate matched decoy-null / re-dock job, nr4a3_8xtt_decoy_null.py).
  * The decoy set is a property-SPANNING non-NR4A negative set (decoy_library.py), not a property-matched
    DUD-E set; the per-conformer percentile is empirical over a modest decoy subset (default 15), so the
    add-one p floors at 1/(n+1). The deliverable is a robustness *distribution* across conformers, honestly.

WHAT (all reuse — no new docking/scoring physics):
  1. fetch 8XTT (RCSB) + AF-Q92570 (AFDB reference sequence only) and build the UniProt->8XTT numbering map
     (nr4a3_8xtt_benchmark: fetch/split/align/map — reused, not reimplemented);
  2. for EACH selected conformer (default 'all' 20): protein-only receptor (nr4a3_8xtt_redock.protein_only_model),
     boxed on the mapped Pocket-5 lining residues (nr4a3_warhead.pocket_box);
  3. dock denovo_401 + the decoy subset into it with smina (nr4a3_warhead.dock_into) and MM-GBSA endpoint-score
     each pose (mmgbsa_energy.endpoint_dG — the SAME single-snapshot GBn2 endpoint the matrix/redock tier uses);
  4. per conformer: denovo_401's endpoint ΔG + the decoy ΔG distribution -> a decoy-null verdict
     (clears the q-th-pct bar? rank among {denovo ∪ decoys}? percentile rank + add-one p);
  5. aggregate across conformers: #{clears the null} / #scored, and the rank DISTRIBUTION of denovo_401.

Output: nr4a3-8xtt-conformer-scoring.json, checkpointed after EACH (conformer, ligand) MM-GBSA leg
(Continuous S3 upload keeps the partial as the deliverable — CLAUDE.md checkpoint rule). PURE aggregation /
ranking logic (favourability, per-conformer null verdict, cross-conformer summary) is dependency-free and
unit-tested in tests/test_8xtt_conformer_scoring.py; the heavy dock/MM-GBSA glue is lazy-imported.
"""
import json
import os
import sys
import traceback

import nr4a3_8xtt_benchmark as bm            # fetch/split/align/map + distribution_stats + _quantile (reuse)
import nr4a3_8xtt_pocketminer as pm          # reuse select_models (8XTT conformer resolution, 'all' -> 20)
import nr4a3_8xtt_redock as rd               # reuse protein_only_model + _fetch_af2 + LIGAND_{LABEL,SMILES}
import nr4a3_8xtt_decoy_null as dn           # reuse percentile_rank / empirical_p_add_one (pure null stats)
import decoy_library as dl                   # the fixed non-NR4A decoy negative-control set

LIGAND_LABEL = rd.LIGAND_LABEL               # "denovo_401"
LIGAND_SMILES = rd.LIGAND_SMILES             # the carried lead (as-generated diastereomer)

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
REQUESTED_MODELS = os.environ.get("MODELS", "all")           # default: score across ALL 20 conformers
DECOY_COUNT = int(os.environ.get("DECOY_COUNT", "15"))       # decoys per conformer (cost/coverage knob)
MINIMIZE_ITERS = int(os.environ.get("MMGBSA_MIN_ITERS", "250"))
NULL_Q = float(os.environ.get("NULL_PCT", "95.0"))           # the "clears the null" bar = q-th pct of decoys
OUT_JSON = "nr4a3-8xtt-conformer-scoring.json"


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_conformer_scoring.py (no smina/openmm/rdkit/biopython/net).
# All scoring is done in "favourability" space (= -ΔG, so HIGHER = more favourable) so the right-tail
# percentile / add-one machinery reused from nr4a3_8xtt_decoy_null applies unchanged; ΔG is reported in
# the output for honesty (more-negative ΔG = better binder).
# ==================================================================================================

def favourability(dG):
    """Endpoint MM-GBSA ΔG (kcal/mol; more NEGATIVE = more favourable) -> favourability (= -ΔG; HIGHER =
    more favourable). None passes through. Pure — the sign convention lets the reused right-tail null
    stats (dn.percentile_rank / dn.empirical_p_add_one) treat 'better' as 'higher'."""
    return None if dG is None else -float(dG)


def _row_scores(row, denovo_label=LIGAND_LABEL):
    """Extract (denovo_dG, [decoy_dGs]) from a per-conformer row, supporting two shapes:
      * checkpoint shape: {"model": int, "dG": {label: ΔG|None, ...}}  (the driver's on-disk form)
      * explicit shape:   {"model": int, "denovo_dG": ΔG|None, "decoy_dGs": [ΔG, ...]}
    Pure. Missing / None decoy scores are dropped from the decoy list."""
    if "dG" in row and isinstance(row["dG"], dict):
        d = row["dG"]
        denovo_dG = d.get(denovo_label)
        decoys = [v for k, v in d.items() if k != denovo_label and v is not None]
        return denovo_dG, decoys
    denovo_dG = row.get("denovo_dG")
    decoys = [v for v in (row.get("decoy_dGs") or []) if v is not None]
    return denovo_dG, decoys


def conformer_null_verdict(denovo_dG, decoy_dGs, q=NULL_Q):
    """One conformer's decoy-null verdict for denovo_401's endpoint score.

    `decoy_dGs`: the decoy endpoint ΔGs in THIS conformer. Returns a dict:
      n_decoys              : # decoys with a score in this conformer,
      denovo_dG             : denovo_401's endpoint ΔG here (echoed),
      decoy_dG_distribution : bm.distribution_stats over the decoy ΔGs,
      decoy_pct_bar_dG      : the ΔG at the q-th favourability percentile of the decoys (the pass bar; a
                              more-negative bar is harder to beat),
      clears_null           : denovo_401 MORE favourable than the q-th-pct decoy bar (fav > bar_fav),
      rank                  : 1-based rank of denovo_401 among {denovo_401 ∪ decoys} by favourability
                              (1 = strongest endpoint binder in the conformer; competition rank),
      n_ligands_ranked      : denominator for rank (# ligands with a score here),
      percentile_rank       : % of decoys strictly LESS favourable than denovo_401 (0..100),
      empirical_p_add_one   : (#{decoy fav >= denovo fav} + 1)/(n+1), one-sided right-tail,
      verdict               : 'clears' | 'within-null' | 'no-data'.
    Pure — reuses dn.percentile_rank / dn.empirical_p_add_one (favourability space) + bm quantile/stats."""
    decoy_fav = [favourability(d) for d in decoy_dGs if d is not None]
    denovo_fav = favourability(denovo_dG)
    stats = bm.distribution_stats(decoy_dGs, threshold=0.0)
    n = len(decoy_fav)
    if n == 0:
        return {"n_decoys": 0, "denovo_dG": denovo_dG, "decoy_dG_distribution": stats,
                "decoy_pct_bar_dG": None, "clears_null": None, "rank": None, "n_ligands_ranked": 0,
                "percentile_rank": None, "empirical_p_add_one": None, "verdict": "no-data", "q": q}
    bar_fav = bm._quantile(sorted(decoy_fav), q / 100.0)
    clears = denovo_fav is not None and denovo_fav > bar_fav
    rank = None if denovo_fav is None else 1 + sum(1 for f in decoy_fav if f > denovo_fav)
    n_ranked = n + (1 if denovo_fav is not None else 0)
    if denovo_fav is None:
        verdict = "no-data"
    elif clears:
        verdict = "clears"
    else:
        verdict = "within-null"
    return {"n_decoys": n, "denovo_dG": denovo_dG, "decoy_dG_distribution": stats,
            "decoy_pct_bar_dG": round(-bar_fav, 3), "clears_null": clears,
            "rank": rank, "n_ligands_ranked": n_ranked,
            "percentile_rank": dn.percentile_rank(denovo_fav, decoy_fav),
            "empirical_p_add_one": dn.empirical_p_add_one(denovo_fav, decoy_fav),
            "verdict": verdict, "q": q}


def summarize_conformer_scoring(rows, denovo_label=LIGAND_LABEL, q=NULL_Q):
    """Aggregate the per-conformer decoy-null verdicts across the 8XTT ensemble.

    `rows`: per-conformer rows (either shape accepted by _row_scores). Returns:
      per_conformer          : {str(model): conformer_null_verdict},
      n_conformers_scored     : # conformers with denovo_401 scored AND >=1 decoy (a usable null),
      n_conformers_clear      : # of those where denovo_401 clears the q-th-pct decoy bar,
      frac_conformers_clear   : n_clear / n_scored,
      denovo401_rank_distribution : distribution of denovo_401's 1-based rank across scored conformers,
      denovo401_dG_distribution   : distribution of denovo_401's endpoint ΔG across conformers,
      verdict                 : 'robust' | 'mixed' | 'fragile' | 'no-data',
      rationale               : plain-English, honestly scoped.
    Overall verdict: robust = clears in a MAJORITY of scored conformers; mixed = clears in some but not a
    majority; fragile = clears in none; no-data = nothing scored. Pure."""
    per = {}
    ranks, denovo_dgs = [], []
    n_scored = n_clear = 0
    for r in rows:
        model = r.get("model")
        denovo_dG, decoy_dGs = _row_scores(r, denovo_label)
        v = conformer_null_verdict(denovo_dG, decoy_dGs, q=q)
        per[str(model)] = v
        if denovo_dG is not None:
            denovo_dgs.append(denovo_dG)
        if v["verdict"] != "no-data" and v["n_decoys"] > 0:
            n_scored += 1
            if v["clears_null"]:
                n_clear += 1
            if v["rank"] is not None:
                ranks.append(v["rank"])
    rank_dist = bm.distribution_stats(ranks, threshold=0.0)
    denovo_dG_dist = bm.distribution_stats(denovo_dgs, threshold=0.0)
    frac = (n_clear / n_scored) if n_scored else None
    if n_scored == 0:
        verdict = "no-data"
        rationale = "no 8XTT conformer produced denovo_401 + a decoy null (docking/scoring failed)"
    elif n_clear > n_scored / 2:
        verdict = "robust"
        rationale = (f"denovo_401 clears the decoy null (> decoy {q:g}th-pct endpoint score) in "
                     f"{n_clear}/{n_scored} 8XTT conformers (median rank {rank_dist.get('median')} of "
                     f"{DECOY_COUNT + 1}); its NR4A3-favoured endpoint score is a ROBUST property of the "
                     "lead across the experimental NMR ensemble, not an artefact of one AF2/metad frame. "
                     "TRIAGE energy, not affinity, and no paralogue comparator — this is an endpoint-score "
                     "robustness check, not a binding or selectivity proof.")
    elif n_clear > 0:
        verdict = "mixed"
        rationale = (f"denovo_401 clears the decoy null in {n_clear}/{n_scored} 8XTT conformers "
                     f"(median rank {rank_dist.get('median')} of {DECOY_COUNT + 1}); its endpoint score is "
                     "geometry-sensitive across the experimental ensemble — report the spread honestly. "
                     "Endpoint-score robustness check only (TRIAGE energy, no paralogue comparator).")
    else:
        verdict = "fragile"
        rationale = (f"denovo_401 clears the decoy null in 0/{n_scored} 8XTT conformers "
                     f"(median rank {rank_dist.get('median')} of {DECOY_COUNT + 1}); its NR4A3-favoured "
                     "endpoint score does NOT survive across the experimental NMR ensemble — the single-frame "
                     "score does not generalise. Endpoint-score robustness check only (TRIAGE energy).")
    return {"per_conformer": per, "n_conformers_scored": n_scored, "n_conformers_clear": n_clear,
            "frac_conformers_clear": frac, "q": q,
            "denovo401_rank_distribution": rank_dist, "denovo401_dG_distribution": denovo_dG_dist,
            "verdict": verdict, "rationale": rationale}


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — smina/openmm/rdkit/biopython/network live here).
# Mirrors nr4a3_8xtt_redock.main() (denovo_401 into 8XTT conformers) but scores the ENDPOINT ΔG into each
# NR4A3 conformer against a per-conformer decoy null (no paralogue receptors), across ALL 20 conformers.
# ==================================================================================================

def _read(path):
    with open(path) as fh:
        return fh.read()


def _write(res):
    with open(os.path.join(OUT, OUT_JSON), "w") as fh:
        json.dump(res, fh, indent=2)


def _load_checkpoint():
    """Resume: return {model:int -> {label -> ΔG|None}} from a prior partial JSON, so a spot kill/timeout
    costs at most the in-flight (conformer, ligand) MM-GBSA leg. Empty on a fresh / unreadable run."""
    p = os.path.join(OUT, OUT_JSON)
    if not os.path.exists(p):
        return {}
    try:
        prev = json.load(open(p))
    except Exception:  # noqa: BLE001
        return {}
    done = {}
    for r in prev.get("per_conformer", []):
        m = r.get("model")
        if m is not None and isinstance(r.get("dG"), dict):
            done[int(m)] = dict(r["dG"])
    return done


def _decoy_subset(n):
    """The first `n` decoys (deterministic, name-sorted) from the fixed negative-control library, as
    (label, id, smiles) triples. `n <= 0` or `n >= all` -> the whole set."""
    cands = dl.decoy_candidate_json()["candidates"]        # already name-sorted, labels 'decoy_<name>'
    if n and 0 < n < len(cands):
        cands = cands[:n]
    return [(c["name"], c["name"], c["smiles"]) for c in cands]


def _poses_for_conformer(wh, rec_pdb, center, sdf, model, work):
    """Dock the combined ligand SDF into one conformer (reusing an existing docked SDF on resume) and load
    the poses. Returns {label: OpenFF pose}."""
    import mmgbsa_energy as mme
    tag = f"nr4a3_m{model}"
    docked = os.path.join(work, f"docked_{tag}.sdf")
    if not os.path.exists(docked):
        wh.dock_into(rec_pdb, center, sdf, tag)            # writes docked_<tag>.sdf into wh.OUT (== work)
    if not os.path.exists(docked):
        return {}
    try:
        return mme.load_poses(docked)
    except Exception as e:  # noqa: BLE001
        print(f"  could not load poses for model {model}: {e}", file=sys.stderr)
        return {}


def main():
    import nr4a3_warhead as wh
    import nr4a3_dock as dock
    import mmgbsa_energy as mme
    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "conformer_scoring_work")
    os.makedirs(work, exist_ok=True)
    wh.OUT = work

    # Fail FAST if no GPU OpenMM platform (MM-GBSA has NO CPU fallback — ~48 min/ligand on CPU), before the
    # (CPU) smina docking, so a broken GPU/ICD dies in seconds not after burning the timeout.
    omm, _app, ommunit, *_ = mme._mm()
    mme._platform(omm, ommunit)

    decoys = _decoy_subset(DECOY_COUNT)
    ligands = [(LIGAND_LABEL, LIGAND_LABEL, LIGAND_SMILES)] + decoys
    decoy_labels = [lab for lab, _c, _s in decoys]

    res = {"_note": "denovo_401 NR4A3-favoured ENDPOINT (MM-GBSA) score across ALL 20 deposited 8XTT NMR "
                    "conformers, each with a per-conformer decoy null. Docks denovo_401 + a decoy subset "
                    "into each 8XTT conformer (protein-only, boxed on the mapped Pocket-5 lining set), "
                    "MM-GBSA single-snapshot GBn2 endpoint-scores each pose, and per conformer ranks "
                    "denovo_401 against the decoy endpoint-score null (clears the q-th-pct bar? rank among "
                    "{denovo ∪ decoys}?). Aggregates: #{conformers where denovo_401 clears the null} and "
                    "denovo_401's rank distribution. HONEST SCOPE: endpoint-score ROBUSTNESS across the "
                    "experimental ensemble — enthalpy-only TRIAGE energy, NO paralogue comparator; NOT a "
                    "binding or selectivity proof.",
           "ligand": {"label": LIGAND_LABEL, "smiles": LIGAND_SMILES},
           "params": {"requested_models": REQUESTED_MODELS, "decoy_count": DECOY_COUNT,
                      "minimize_iters": MINIMIZE_ITERS, "null_pct": NULL_Q,
                      "decoy_labels": decoy_labels, "n_decoys_library": dl.n_decoys()},
           "per_conformer": [], "summary": {}}

    # 1) build the combined ligand SDF (denovo_401 + decoys) once (RDKit 3D embed).
    sdf = os.path.join(work, "ligands.sdf")
    kept = dock.make_sdf(ligands, sdf)
    kept_labels = [lab for lab, _c, _s in kept]
    res["params"]["n_ligands_embedded"] = len(kept_labels)
    if LIGAND_LABEL not in kept_labels:
        res["_status"] = "RDKit could not build denovo_401 3D structure"
        _write(res); sys.exit("ABORT: denovo_401 SDF build failed")
    print(f"  embedded {len(kept_labels)} ligands ({LIGAND_LABEL} + {len(kept_labels) - 1} decoys)", flush=True)

    # 2) fetch 8XTT (RCSB) + AF2 (AFDB, reference sequence only) and build the UniProt->8XTT numbering map.
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
    res["_method"] = {"pdb": bm.PDB_ID, "alignment_identity": round(identity, 4),
                      "mapped_pocket5_8xtt": mapped_pocket5, "n_models": len(models),
                      "box": "24 A cube on the mapped Pocket-5 CA centroid (nr4a3_warhead.pocket_box)"}
    if not mapped_pocket5:
        res["_status"] = "no Pocket-5 residues mapped onto 8XTT — cannot box"
        _write(res); sys.exit("ABORT: empty Pocket-5 map")

    # 3) select conformers (default 'all' -> every one of the ~20 NMR models).
    chosen = pm.select_models(range(1, len(models) + 1), REQUESTED_MODELS)
    res["_method"]["conformers_scored"] = chosen
    print(f"  8XTT: {len(models)} models; identity {identity:.3f}; scoring {len(kept_labels)} ligands into "
          f"conformers {chosen}", flush=True)

    # 4) per conformer: dock all ligands, MM-GBSA endpoint each; checkpoint after EACH (conformer, ligand).
    done = _load_checkpoint()
    if done:
        n_done = sum(len(v) for v in done.values())
        print(f"  resuming: {n_done} (conformer,ligand) legs already scored", flush=True)
    cache = os.path.join(work, "sysgen_cache.json")
    per = []
    for model in chosen:
        rec = {"model": model, "dG": dict(done.get(model, {}))}
        try:
            # if every ligand already scored for this conformer, skip the (re-)dock + MM-GBSA entirely.
            remaining = [lab for lab in kept_labels if lab not in rec["dG"]]
            if remaining:
                rec_pdb = os.path.join(work, f"8xtt_model{model}_nr4a3.pdb")
                with open(rec_pdb, "w") as fh:
                    fh.write(rd.protein_only_model(models[model - 1]))
                center, nbox = wh.pocket_box(rec_pdb, mapped_pocket5)
                rec["n_box_residues"] = nbox
                poses = _poses_for_conformer(wh, rec_pdb, center, sdf, model, work)
                rec_top, rec_pos = mme.prepare_receptor(rec_pdb)
                for lab in remaining:
                    pose = poses.get(lab)
                    if pose is None:
                        rec["dG"][lab] = None
                        continue
                    try:
                        rec["dG"][lab] = mme.endpoint_dG(rec_top, rec_pos, pose,
                                                         minimize_iters=MINIMIZE_ITERS, cache=cache)["dG"]
                    except Exception as e:  # noqa: BLE001 — one bad ligand never voids the conformer
                        rec["dG"][lab] = None
                        print(f"  model {model} ligand {lab}: MM-GBSA ERROR {e}", file=sys.stderr, flush=True)
                    # checkpoint after EACH (conformer, ligand) MM-GBSA leg (Continuous S3 upload).
                    _flush(res, per, model, rec)
            v = conformer_null_verdict(rec["dG"].get(LIGAND_LABEL),
                                       [rec["dG"][l] for l in decoy_labels if l in rec["dG"]], q=NULL_Q)
            rec["verdict"] = v["verdict"]
            rec["clears_null"] = v["clears_null"]
            rec["rank"] = v["rank"]
            rec["denovo_dG"] = rec["dG"].get(LIGAND_LABEL)
            print(f"  model {model:>2}: denovo_401 ΔG={rec['denovo_dG']} rank={v['rank']}/"
                  f"{v['n_ligands_ranked']} clears_null={v['clears_null']}", flush=True)
        except Exception as e:  # noqa: BLE001 — record + keep going; one bad conformer never voids the run
            rec["error"] = str(e)[:300]
            print(f"  model {model:>2}: ERROR {e}", file=sys.stderr, flush=True)
        _flush(res, per, model, rec)

    res["per_conformer"] = per
    res["summary"] = summarize_conformer_scoring(per, denovo_label=LIGAND_LABEL, q=NULL_Q)
    res["_status"] = "ok"
    _write(res)
    print(json.dumps({"summary_verdict": res["summary"]["verdict"],
                      "n_conformers_clear": res["summary"]["n_conformers_clear"],
                      "n_conformers_scored": res["summary"]["n_conformers_scored"],
                      "rank_distribution": res["summary"]["denovo401_rank_distribution"],
                      "rationale": res["summary"]["rationale"]}, indent=2), flush=True)


def _flush(res, per, model, rec):
    """Upsert `rec` into `per` (by model), recompute the summary, and write the checkpoint JSON. Keeps the
    on-disk partial a valid, aggregated deliverable after every (conformer, ligand) leg."""
    for i, r in enumerate(per):
        if r.get("model") == model:
            per[i] = rec
            break
    else:
        per.append(rec)
    res["per_conformer"] = per
    res["summary"] = summarize_conformer_scoring(per, denovo_label=LIGAND_LABEL, q=NULL_Q)
    _write(res)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        os.makedirs(OUT, exist_ok=True)
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, OUT_JSON), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
