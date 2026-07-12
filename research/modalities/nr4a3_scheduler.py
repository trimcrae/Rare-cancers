#!/usr/bin/env python3
"""
Scheduling layer for the NR4A3 screen — DELEGATED to a maintained library (Optuna), not hand-rolled.

Rationale (2026-07-12 review + trimcrae): the allocation/scheduling problem here is best-arm / good-arm
identification over a FIXED, small congeneric candidate set under a multi-fidelity ladder — i.e. successive
halving / Hyperband, which is exactly what Optuna's pruners implement and battle-test. So we use it rather
than reinvent it. (Continuous multi-fidelity Bayesian optimisation — Ax/BoTorch, active-learning FEP — is the
right tool only if/when candidates are GENERATED from a chemical space; for a fixed 19-compound set it is the
wrong shape.) The genuinely novel piece — thresholded, error-controlled, noncompensatory CERTIFICATION — is
kept entirely separate in adaptive_certify.py and is the ONLY thing that declares a candidate.

This module requires `optuna` (and, for the stats cross-check, `confseq`). The dev sandbox does not have them;
run it on a CI runner or SageMaker where `pip install optuna confseq` is allowed (see
.github/workflows/allocator-validate.yml). The stdlib prototype in adaptive_allocator.py remains an OFFLINE
design artifact only — this library-backed scheduler is the intended production scheduling path.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adaptive_certify import (  # noqa: E402
    PASS_CANDIDATE, CertCandidate, MarginEvidence, campaign_delta_split, certify_candidate,
)


def require_optuna():
    try:
        import optuna
        return optuna
    except ImportError:
        sys.exit("nr4a3_scheduler needs `optuna` — run on a CI runner or SageMaker (pip install optuna), "
                 "not the dev sandbox. The stdlib adaptive_allocator.py is the offline prototype only.")


def make_study(candidate_ids, min_resource=1, reduction_factor=3, seed=0):
    """A successive-halving/Hyperband study that enumerates the FIXED candidate set (GridSampler over the
    candidate id) and prunes across candidates at matched rungs — the library's implementation of the method
    we would otherwise hand-roll."""
    optuna = require_optuna()
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler = optuna.samplers.GridSampler({"candidate": list(candidate_ids)}, seed=seed)
    pruner = optuna.pruners.SuccessiveHalvingPruner(min_resource=min_resource, reduction_factor=reduction_factor)
    return optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner)


def run_offline_shadow(config, evaluate_fn, budget_gate=None):
    """
    Offline shadow driver. Scheduling = Optuna successive halving (which candidate advances). Certification =
    adaptive_certify (whether a candidate PASSES), on terminal-rung margin evidence only, with the pre-declared
    campaign delta. Kept OFFLINE: `evaluate_fn` is expected to return cached/simulated results, not to dispatch
    real GPU jobs, until the calibration gate + stress suite + code review clear it.

    evaluate_fn(cid, rung) -> {"promise": float,               # scheduling scalar (noncompensatory-aware)
                               "terminal": bool,
                               "margins": {target: obs} | None, # per-anti-target margin observations
                               "meta": {seed, start_state, parent_traj}}
    Returns {"declared": cid|None, "spent": float, "trials": int, "pruned": int, "escalate": bool}.
    """
    optuna = require_optuna()
    cert = config["certification"]
    ids = [c["id"] for c in config["candidates"]]
    rungs = [r["rung"] for r in config["rungs"]]
    terminal = config["terminal_rung"]
    delta_cand = campaign_delta_split(cert["delta_total"], len(ids))    # certify splits this across margins
    state = {"declared": None, "spent": 0.0, "pruned": 0,
             "cands": {cid: CertCandidate(cid=cid) for cid in ids}}
    for cid in ids:
        state["cands"][cid].margins = {t: MarginEvidence(target=t, sigma=cert.get("sigma_known", 1.0),
                                                         sigma_fixed=True) for t in cert["targets"]}
    cost_by_rung = {r["rung"]: r["cost_usd"] for r in config["rungs"]}
    can_certify = {r["rung"]: r["can_certify"] for r in config["rungs"]}

    def objective(trial):
        cid = trial.suggest_categorical("candidate", ids)
        cand = state["cands"][cid]
        last = 0.0
        for rung in rungs:
            if budget_gate is not None and state["spent"] >= budget_gate:
                raise optuna.TrialPruned()
            ev = evaluate_fn(cid, rung)
            state["spent"] += cost_by_rung.get(rung, 0.0)
            last = ev.get("promise", 0.0)
            # ---- fold terminal evidence for CERTIFICATION (only certifying rungs count) ----
            # A certifying rung supplies >=1 INDEPENDENT replica per margin: margins[t] may be a scalar (one
            # replica) or a list (several). Each is folded with a distinct seed/start so the independence check
            # counts them separately (fix 4).
            if can_certify.get(rung) and ev.get("margins"):
                meta = ev.get("meta") or {}
                for t, obs_or_list in ev["margins"].items():
                    obs_list = obs_or_list if isinstance(obs_or_list, (list, tuple)) else [obs_or_list]
                    m = cand.margins[t]
                    m.from_terminal_rung = True
                    for j, o in enumerate(obs_list):
                        m.update(o, seed=f"{meta.get('seed')}_{j}",
                                 start_state=f"{meta.get('start_state')}_{j}", parent_traj=meta.get("parent_traj"))
                verdict = certify_candidate(cand.margins, bar=cert["bar_kcal"], robustness=cert["robustness_kcal"],
                                            delta_candidate=delta_cand,
                                            min_independent_replicas=cert["min_independent_replicas"],
                                            require_terminal=cert["require_terminal"])
                if verdict == PASS_CANDIDATE and state["declared"] is None:
                    state["declared"] = cid          # first CERTIFIED candidate — stop (good-arm ID)
                    trial.study.stop()
                    return last
            # ---- SCHEDULING ONLY: report to the pruner; it decides halving across candidates ----
            trial.report(last, step=rung)
            if trial.should_prune():
                state["pruned"] += 1
                raise optuna.TrialPruned()
        return last

    if cert.get("bar_kcal") is None:
        sys.exit("certification bar (each_difference_min_kcal) is not frozen in the prereg yet — set it during "
                 "the retrospective calibration; refusing to run with a guessed bar.")
    study = make_study(ids)
    study.optimize(objective, n_trials=len(ids), catch=())
    return {"declared": state["declared"], "spent": round(state["spent"], 2),
            "trials": len(study.trials), "pruned": state["pruned"],
            "escalate": state["declared"] is None}


if __name__ == "__main__":
    from nr4a3_screen_config import build_config
    cfg = build_config()
    print("candidates:", len(cfg["candidates"]), "| terminal rung:", cfg["terminal_rung"],
          "| bar_kcal:", cfg["certification"]["bar_kcal"], "| offline:", cfg["offline"])
    print("scheduling:", cfg["scheduling"])
