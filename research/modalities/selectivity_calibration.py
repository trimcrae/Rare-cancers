#!/usr/bin/env python3
"""Decoy-calibrated selectivity threshold for the de-novo funnel (red-team 2026-06-30).

WHY. The single-snapshot MM-GBSA NR4A3 margin (mmMin) is NON-SPECIFIC on its own — a 38-drug non-NR4A decoy
null scored `confirmed_selective` 39 % of the time (margin>0 in ~58 %), because the NR4A3 receptor is scored
more favourably than the paralogue frames (a systematic bias). So `margin > 0` is meaningless. BUT the decoy
run gives us a calibrated yardstick: a candidate is only credibly NR4A3-selective if its margin is in the
extreme right tail of the DECOY distribution. This module turns the decoy margins into a threshold and a
percentile-based verdict, so selection optimises against the null instead of against zero.

Pure (no IO/RDKit) → unit-tested. The driver passes the committed decoy margins + candidate margins.

Result with the 2026-06-30 decoy run (n=38): mean 1.26, sd 6.25, 90th pct 9.74, 95th pct 13.12, max 16.46.
Only `denovo_111` (+15.70) clears the 95th-pct bar (1 decoy above it) — the program's first above-null hit.
"""

# Committed single-snapshot MM-GBSA NR4A3 margins of the 38-drug non-NR4A decoy set (2026-06-30 run, the
# de-novo funnel: release NR4A3 + metad-opened paralogues). The canonical null. NOTE: it is receptor-frame
# dependent — for a screen run through a DIFFERENT funnel, prefer a frame-matched decoy pass and only fall
# back to this constant when none is available.
DECOY_2026_06_30 = [16.46, 13.21, 13.10, 9.75, 9.73, 9.50, 9.30, 5.32, 5.17, 5.15, 4.43, 4.41, 3.42, 3.08,
                    2.76, 2.46, 1.32, 1.11, 0.69, 0.32, 0.21, 0.09, -0.75, -2.74, -2.77, -3.41, -3.44,
                    -3.52, -3.56, -3.81, -3.95, -4.38, -5.43, -5.72, -5.79, -6.51, -8.46, -8.89]


def percentile(sorted_vals, q):
    """Linear-interpolated percentile q in [0,100] of an ascending-sorted list (numpy-free)."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    rank = (q / 100.0) * (len(sorted_vals) - 1)
    lo = int(rank)
    frac = rank - lo
    if lo + 1 >= len(sorted_vals):
        return float(sorted_vals[-1])
    return float(sorted_vals[lo] + frac * (sorted_vals[lo + 1] - sorted_vals[lo]))


def decoy_threshold(decoy_margins, q=95.0):
    """The selectivity threshold = the q-th percentile of the decoy NR4A3-margin null (default 95th)."""
    return percentile(sorted(decoy_margins), q)


def calibrated_verdict(margin, decoy_margins, q=95.0):
    """Verdict for one candidate vs the decoy null. Returns dict with:
      threshold      : decoy q-th percentile,
      n_decoys_above : how many decoys score >= this candidate (0 = strictly best),
      decoy_frac_above: that as a fraction (an empirical p-value-ish against the null),
      above_null     : margin > threshold (credibly selective vs the null).
    A candidate is only worth advancing (FEP/synthesis) if above_null AND its chemistry is clean."""
    thr = decoy_threshold(decoy_margins, q)
    n_above = sum(1 for d in decoy_margins if d >= margin)
    return {"margin": margin, "threshold": thr,
            "n_decoys_above": n_above,
            "decoy_frac_above": round(n_above / len(decoy_margins), 4) if decoy_margins else None,
            "above_null": (thr is not None and margin > thr)}


def rank_against_null(candidates, decoy_margins, q=95.0):
    """candidates: list of dicts each with 'label' and 'margin'. Returns them sorted by margin desc, each
    annotated with the calibrated verdict. Use this to harvest the above-null set across dev + v2 + future
    campaigns — the only candidates worth optimising/confirming."""
    out = []
    for c in candidates:
        v = calibrated_verdict(c.get("margin"), decoy_margins, q)
        out.append({**c, **v})
    out.sort(key=lambda r: (r.get("margin") is not None, r.get("margin") or -1e9), reverse=True)
    return out
