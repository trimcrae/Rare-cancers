#!/usr/bin/env python3
"""Pure logic for the GENERATION-MATCHED DECOY NULL (winner's-curse / generative-confound control).

WHY. The de-novo lead ``denovo_401`` was **DiffSBDD-generated conditioned on the NR4A3 release-frame
pocket AND selected best-of-N**, whereas the decoy null it beats (``decoy_library`` /
``selectivity_calibration.DECOY_2026_06_30``) was NOT generated for any pocket. That asymmetry is a
winner's-curse / generative confound the manuscript already flags (§2.6): a fair specificity test must
push CONTROL OBJECTIVES through the *identical* generate -> developability-filter -> dock -> multi-snapshot
MM-GBSA -> best-of-N funnel and measure how often the WHOLE FUNNEL manufactures a "confirmed-selective,
above-null survivor" by chance. This module is the pure, unit-tested arithmetic behind that measurement:

  1. ``scramble_promise`` — the winner's-curse null on the SELECTION step: permute the de-novo promise so
     the top-N advanced to docking is decoupled from the real divergent-handle objective (same generations,
     null objective). This is control (b).
  2. ``is_survivor`` / ``survivor_report`` — the identical survivor bar the real campaign held ``denovo_401``
     to: MM-GBSA ``confirmed_selective`` AND above the decoy-null q-th percentile (optionally after
     subtracting the multi-snapshot SD, exactly as denovo_401 was judged: margin-SD > null).
  3. ``binom_sf`` / ``false_positive_rate`` / ``compare_campaigns`` — turn per-control survivor counts into
     the funnel's false-positive rate and ask whether the real campaign's survival EXCEEDS what the
     procedure manufactures on control objectives.

No IO / RDKit / numpy — the driver (``nr4a3_generation_matched_null.py``) passes the loaded JSON rows and
the decoy margins, and writes ``nr4a3-generation-matched-null.json``. Pure => unit-tested (TESTING.md #3).
Everything here is a screening-null statistic, NOT an affinity.
"""

import random

import selectivity_calibration as sc


# ---------------------------------------------------------------------------
# Control (b): the scrambled-objective (winner's-curse-on-selection) null.
# ---------------------------------------------------------------------------
def scramble_promise(rows, seed=0):
    """Return a NEW candidate list (nr4a3-denovo.json 'candidates' shape) whose ``denovo_promise`` values
    are RANDOMLY PERMUTED among the valid generations, so ``denovo_library.top_candidates`` advances a
    top-N that is DECOUPLED from the real divergent-handle objective. The generations (smiles, profile) are
    untouched — only which ones the funnel *selects* changes. This isolates the winner's-curse contributed
    by the best-of-N SELECTION step (a real pocket, a null objective).

    Invalid rows (promise None / error / no smiles) keep promise None so they stay unselectable, matching
    the real funnel. Deterministic in ``seed`` (reproducible control). Does not mutate the input rows.
    """
    out = [dict(r) for r in rows]
    valid_idx = [i for i, r in enumerate(out)
                 if r.get("denovo_promise") is not None and r.get("smiles") and "error" not in r]
    promises = [out[i]["denovo_promise"] for i in valid_idx]
    rnd = random.Random(seed)
    rnd.shuffle(promises)
    for j, i in enumerate(valid_idx):
        out[i]["denovo_promise"] = promises[j]
    return out


def scrambled_denovo_json(denovo, seed=0):
    """Wrap ``scramble_promise`` into a full nr4a3-denovo.json dict the dock funnel can consume unchanged
    (``nr4a3_matrix`` candidate mode reads {'candidates': [...]}). Tags the campaign so the provenance of a
    scrambled-objective control is never mistaken for a real generation."""
    out = dict(denovo)
    out["candidates"] = scramble_promise(denovo.get("candidates", []), seed=seed)
    out["campaign"] = "genmatched-null-scramble"
    out["_genmatched_null"] = {"control": "scrambled-objective", "seed": seed,
                               "note": ("promise permuted among valid generations: real NR4A3 release-frame "
                                        "pocket, NULL selectivity objective (winner's-curse-on-selection "
                                        "control for the generation-matched decoy null)")}
    return out


# ---------------------------------------------------------------------------
# The identical survivor bar (confirmed-selective AND above the decoy null).
# ---------------------------------------------------------------------------
def survivor_margin(row, margin_key="mm_min_margin", sd_key="mm_min_margin_sd", subtract_sd=False):
    """The effective NR4A3-selectivity margin used for the above-null test. When ``subtract_sd`` (the bar
    denovo_401 was actually held to — margin-SD > null), the multi-snapshot SD is subtracted so a noisy
    margin cannot clear the bar. Returns None if the margin is missing."""
    m = row.get(margin_key)
    if m is None:
        return None
    if subtract_sd:
        sd = row.get(sd_key)
        m = m - (sd if sd is not None else 0.0)
    return m


def is_survivor(row, decoy_margins, q=95.0, band=1.0, margin_key="mm_min_margin",
                sd_key="mm_min_margin_sd", subtract_sd=False, require_confirmed_verdict=True):
    """Did ONE candidate pass the identical bar the real campaign held its survivor to?

    A survivor must be BOTH:
      * MM-GBSA ``confirmed_selective`` — the raw ``mm_min_margin`` clears the selectivity band (> band),
        i.e. NR4A3 is favoured over BOTH paralogues by more than MM-GBSA noise. If the row carries a
        ``verdict`` field and ``require_confirmed_verdict``, it must equal ``confirmed_selective`` (so a
        docking-nonselective 'rescued' row does not count) — this mirrors the manuscript, where the survivor
        census counts ``confirmed_selective`` only.
      * ABOVE THE DECOY NULL — the effective margin (optionally minus its SD) exceeds the decoy q-th
        percentile (``selectivity_calibration.decoy_threshold``). This is the winner's-curse-aware bar.

    Returns bool. A missing margin or empty decoy null is not a survivor (fail-closed).
    """
    raw = row.get(margin_key)
    if raw is None or not decoy_margins:
        return False
    mm_sel = raw > band
    if require_confirmed_verdict and row.get("verdict") is not None:
        mm_sel = mm_sel and row.get("verdict") == "confirmed_selective"
    thr = sc.decoy_threshold(decoy_margins, q)
    eff = survivor_margin(row, margin_key=margin_key, sd_key=sd_key, subtract_sd=subtract_sd)
    above = thr is not None and eff is not None and eff > thr
    return bool(mm_sel and above)


def survivor_report(rows, decoy_margins, n_generated=None, q=95.0, band=1.0,
                    margin_key="mm_min_margin", sd_key="mm_min_margin_sd", subtract_sd=False,
                    require_confirmed_verdict=True, label_key="label"):
    """Aggregate the survivor bar over one campaign's rescored candidate rows.

    ``n_generated`` is the number of molecules the funnel STARTED from (the best-of-N pool size) — the
    denominator for the per-molecule false-positive rate. When None it defaults to the number of rescored
    rows (an underestimate; the driver should pass the true generation count). Returns:

      n_generated, n_rescored, n_confirmed_selective, n_above_null, n_survivors, survivors (labels),
      best_margin (the strongest effective margin — the best-of-N pick), threshold (decoy q-th pct),
      manufactured (bool: >=1 survivor emerged).
    """
    thr = sc.decoy_threshold(decoy_margins, q) if decoy_margins else None
    n_conf = 0
    n_above = 0
    survivors = []
    best_margin = None
    for r in rows:
        raw = r.get(margin_key)
        conf = raw is not None and raw > band and (
            not (require_confirmed_verdict and r.get("verdict") is not None)
            or r.get("verdict") == "confirmed_selective")
        if conf:
            n_conf += 1
        eff = survivor_margin(r, margin_key=margin_key, sd_key=sd_key, subtract_sd=subtract_sd)
        if eff is not None and (best_margin is None or eff > best_margin):
            best_margin = eff
        if thr is not None and eff is not None and eff > thr:
            n_above += 1
        if is_survivor(r, decoy_margins, q=q, band=band, margin_key=margin_key, sd_key=sd_key,
                       subtract_sd=subtract_sd, require_confirmed_verdict=require_confirmed_verdict):
            survivors.append(r.get(label_key))
    n_res = len(rows)
    return {
        "n_generated": n_generated if n_generated is not None else n_res,
        "n_rescored": n_res,
        "n_confirmed_selective": n_conf,
        "n_above_null": n_above,
        "n_survivors": len(survivors),
        "survivors": survivors,
        "best_margin": (round(best_margin, 3) if best_margin is not None else None),
        "threshold": (round(thr, 3) if thr is not None else None),
        "manufactured": len(survivors) > 0,
    }


# ---------------------------------------------------------------------------
# Funnel false-positive rate + real-vs-manufactured comparison.
# ---------------------------------------------------------------------------
def _log_binom_coeff(n, k):
    """log(C(n,k)) via lgamma — avoids huge integers and float overflow for the binomial tail."""
    import math
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1))


def binom_sf(k, n, p):
    """Binomial survival function P(X >= k) for X ~ Binomial(n, p). Pure (math only), so the one-sided
    'is the real campaign's survival beyond the manufactured null rate?' p-value needs no scipy.

    Edge cases: k <= 0 -> 1.0; k > n -> 0.0; p <= 0 -> (1.0 if k == 0 else 0.0); p >= 1 -> 1.0.
    """
    import math
    if n <= 0:
        return 1.0 if k <= 0 else 0.0
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        logp = _log_binom_coeff(n, i) + i * math.log(p) + (n - i) * math.log1p(-p)
        total += math.exp(logp)
    return min(1.0, max(0.0, total))


def false_positive_rate(control_reports):
    """Pool the control campaigns into the funnel's false-positive statistics.

    control_reports: list of ``survivor_report`` dicts (one per control objective). Returns:
      n_controls, n_control_campaigns_with_survivor, campaign_manufacture_rate (fraction of control
      campaigns that manufactured >=1 survivor — the best-of-N false-positive rate), pooled_generated,
      pooled_survivors, per_molecule_fp_rate (pooled survivors / pooled generations — the per-generation
      false-positive rate of the whole funnel).
    """
    n = len(control_reports)
    with_surv = sum(1 for r in control_reports if r.get("n_survivors", 0) > 0)
    gen = sum(r.get("n_generated", 0) for r in control_reports)
    surv = sum(r.get("n_survivors", 0) for r in control_reports)
    return {
        "n_controls": n,
        "n_control_campaigns_with_survivor": with_surv,
        "campaign_manufacture_rate": (round(with_surv / n, 4) if n else None),
        "pooled_generated": gen,
        "pooled_survivors": surv,
        "per_molecule_fp_rate": (round(surv / gen, 6) if gen else None),
    }


def build_control_receptor_manifest(pdb_name, box_residues, target, source):
    """Assemble the DiffSBDD receptor manifest (nr4a3-release-druggable.json shape) that points the
    IDENTICAL ``nr4a3_denovo.py`` generation job at a CONTROL pocket instead of the NR4A3 release frame —
    control (c): generate into a paralogue's opened pocket (NR4A1/NR4A2), or any property-matched decoy
    pocket PDB. ``nr4a3_denovo._read_receptor_choice`` reads ``docking_primary_receptor`` and the matching
    ``receptors[].box_residues``, so the generation runs unchanged against the control pocket.

    pdb_name: basename of the receptor PDB placed alongside the manifest (e.g. 'nr4a1-opened.pdb').
    box_residues: the pocket-lining resSeqs to box generation on (the paralogue CV residues, or the matched
                  decoy pocket lining). Pure dict assembly => unit-tested; the driver does the IO/upload.
    """
    if not pdb_name:
        raise ValueError("build_control_receptor_manifest: pdb_name required")
    box = [int(r) for r in (box_residues or [])]
    return {
        "_note": ("GENERATION-MATCHED NULL control target — a NON-NR4A3-release generation pocket pushed "
                  "through the identical DiffSBDD funnel to measure the funnel's false-positive rate."),
        "_genmatched_null": {"control": "control-pocket-generation", "target": target, "source": source},
        "docking_primary_receptor": pdb_name,
        "selection_primary_receptor": pdb_name,
        "druggable_subensemble": [pdb_name],
        "receptors": [{"pdb": pdb_name, "role": "primary", "box_residues": box,
                       "confirmed_druggability": None}],
        "_status": "ok",
    }


def decoy_margins_from_mmgbsa(mmgbsa, margin_key="mm_min_margin"):
    """Extract the decoy NR4A3-selectivity margins from a decoy MM-GBSA result dict (the frame-matched
    decoy null: ``nr4a3_matrix`` DECOY_MODE -> ``nr4a3_mmgbsa`` on the same NR4A3/NR4A1/NR4A2 frames the
    controls dock into). Returns the list of non-None margins; the driver feeds it to the survivor bar so a
    control is judged against a null computed in the SAME frame (the manuscript stresses frame-dependence)."""
    out = []
    for r in mmgbsa.get("candidates", []):
        m = r.get(margin_key)
        if m is not None:
            out.append(m)
    return out


def compare_campaigns(real_report, control_reports, real_survivors=None):
    """Does the real NR4A3-release campaign's survival EXCEED what the funnel manufactures on control
    objectives? Compares the real campaign's survivor count against the pooled per-molecule false-positive
    rate estimated from the controls, via a one-sided binomial tail.

    real_survivors overrides ``real_report['n_survivors']`` when the real survivor is defined externally
    (e.g. denovo_401 as the sole robust lead). Returns:
      real_n_generated, real_n_survivors, control_fp (the false_positive_rate dict), p_value
      (P(>= real_survivors manufactured under the control per-molecule rate), None if that rate is unknown),
      exceeds_chance (real survivors strictly more than the null expectation AND p < 0.05),
      enrichment (real per-molecule rate / control per-molecule rate), verdict (human string).
    """
    fp = false_positive_rate(control_reports)
    n_real = real_report.get("n_generated") or 0
    k_real = real_survivors if real_survivors is not None else real_report.get("n_survivors", 0)
    p_ctrl = fp.get("per_molecule_fp_rate")
    real_rate = (k_real / n_real) if n_real else None
    p_value = None
    exceeds = False
    enrichment = None
    if p_ctrl is not None and n_real:
        p_value = round(binom_sf(k_real, n_real, p_ctrl), 6)
        expected = p_ctrl * n_real
        exceeds = bool(k_real > expected and p_value < 0.05)
        if p_ctrl > 0 and real_rate is not None:
            enrichment = round(real_rate / p_ctrl, 3)
        elif real_rate and real_rate > 0:
            enrichment = float("inf")   # controls manufactured nothing; real did -> unbounded enrichment
    if p_ctrl == 0 and k_real > 0:
        # controls manufactured zero survivors; any real survivor is beyond the manufactured rate.
        exceeds = True
        verdict = ("real campaign produced a survivor the control objectives NEVER manufactured "
                   "(0 control survivors) -> survival is not a generic funnel artifact")
    elif p_value is None:
        verdict = "insufficient control data to estimate the funnel false-positive rate"
    elif exceeds:
        verdict = (f"real survival exceeds the manufactured null (p={p_value}); denovo_401's survival is "
                   f"NOT explained by the generate->filter->dock->MM-GBSA->best-of-N procedure alone")
    else:
        verdict = (f"real survival is within what the funnel manufactures on control objectives "
                   f"(p={p_value}); the generative/winner's-curse confound is NOT excluded")
    return {
        "real_n_generated": n_real,
        "real_n_survivors": k_real,
        "real_per_molecule_rate": (round(real_rate, 6) if real_rate is not None else None),
        "control_fp": fp,
        "p_value": p_value,
        "enrichment": enrichment,
        "exceeds_chance": exceeds,
        "verdict": verdict,
    }
