#!/usr/bin/env python3
"""Early-stop decision logic for the parallel FEP (pure, unit-tested).

Two ways a FEP run "looks like it'll fail", checked from the PILOT (short-sampling) returns before the long
production burns the spot fleet:

  1. SELECTIVITY fail — the provisional ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralogue) is *confidently* not
     selective enough: even its most-optimistic (most-negative) bound is still above the success target for
     some paralogue. The lead won't be NR4A3-selective → stop and save the rest of the budget.
  2. CONVERGENCE fail — adjacent-λ phase-space overlap is too poor across too many windows, so the estimate
     won't converge no matter how long we run this protocol → stop and flag "needs more windows / re-design",
     don't pour sampling into a broken schedule.

Also supports an optional early SUCCESS stop (confidently selective vs both paralogues) to save compute on a
clear winner. All decisions carry the provisional numbers + the reason so the monitor can log them.
"""

from fep_sharding import selectivity_ddg, combine_error


def provisional_ddg(binding_se, reference="nr4a3"):
    """binding_se: {receptor: {"dg": ΔG_bind, "se": stderr}}. Returns {other: {"ddg","se"}} for ref-vs-other
    (ddg<0 == reference-selective)."""
    dgs = {r: v["dg"] for r, v in binding_se.items()}
    ddg = selectivity_ddg(dgs, reference)
    out = {}
    for other, d in ddg.items():
        se = combine_error(binding_se[reference]["se"], binding_se[other]["se"])
        out[other] = {"ddg": round(d, 4), "se": round(se, 4)}
    return out


def early_stop(binding_se, reference="nr4a3", target_ddg=-1.0, z=1.0, allow_success_stop=False):
    """Decide continue / stop_fail / stop_success from provisional per-receptor ΔG_bind (+ se).
      target_ddg : ΔΔG a candidate must reach to count as selective (kcal/mol; e.g. -1.0 = 1 kcal tighter).
      z          : confidence multiple on the ΔΔG standard error (1.0 ≈ 68 %, 1.64 ≈ 95 % one-sided).
    Returns {action, reason, ddg}. Rules (per paralogue, ΔΔG<0 == selective):
      - stop_fail    if for ANY paralogue the most-optimistic bound (ddg − z·se) > target_ddg
                     (even optimistically not selective enough → the lead fails).
      - stop_success if allow_success_stop AND for ALL paralogues the pessimistic bound (ddg + z·se) < target
                     (confidently selective vs both → a clear winner; optional).
      - continue     otherwise (still ambiguous — keep sampling)."""
    ddg = provisional_ddg(binding_se, reference)
    # 1) confident failure vs any paralogue
    for other, d in ddg.items():
        optimistic = d["ddg"] - z * d["se"]          # most-negative (most-selective) plausible value
        if optimistic > target_ddg:
            return {"action": "stop_fail", "ddg": ddg,
                    "reason": (f"provisional ΔΔG vs {other} = {d['ddg']}±{d['se']}; even the optimistic bound "
                               f"{optimistic:.2f} > target {target_ddg} → confidently NOT selective, aborting")}
    # 2) optional confident success vs all
    if allow_success_stop and ddg:
        if all((d["ddg"] + z * d["se"]) < target_ddg for d in ddg.values()):
            return {"action": "stop_success", "ddg": ddg,
                    "reason": f"provisional ΔΔG confidently ≤ {target_ddg} vs all paralogues → clear winner"}
    return {"action": "continue", "ddg": ddg, "reason": "ambiguous — keep sampling"}


def convergence_flag(overlaps, min_overlap=0.03, min_frac_ok=0.5):
    """overlaps: list of adjacent-λ overlap metrics (e.g. BAR overlap / min statistical-overlap per pair).
    Returns {ok, frac_ok, reason}. If fewer than min_frac_ok of pairs clear min_overlap, the schedule is too
    coarse to converge → the monitor treats this as stop_unconverged (re-design with more windows)."""
    if not overlaps:
        return {"ok": True, "frac_ok": None, "reason": "no overlap data yet"}
    ok = sum(1 for o in overlaps if o is not None and o >= min_overlap)
    frac = ok / len(overlaps)
    return {"ok": frac >= min_frac_ok, "frac_ok": round(frac, 3),
            "reason": (f"{ok}/{len(overlaps)} λ-pairs have overlap ≥ {min_overlap} "
                       f"({'ok' if frac >= min_frac_ok else 'TOO COARSE → stop_unconverged'})")}
