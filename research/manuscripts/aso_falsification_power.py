#!/usr/bin/env python3
"""The falsification experiment's power and void-SD figures — DERIVED, not typed.

⛔ WHY THIS EXISTS (round 11 seat 2 and seat 3, independently, P1). The journal article's
Discussion states five numbers for the pre-registered falsification design — "about 80% power ...
six independent biological replicates ... three give about 30%" and "about 0.65 at three
replicates — 1.53 at six, 2.25 at ten" — and every one of them is numerically correct as printed.
None of them had a producing artifact anywhere in the repository: round 8's red-team review found
the same gap in 2026-08-22 and it was never closed, because the underlying assumptions (a cut of
5.0, adopted for pre-registration, and an assumed replicate SD of 0.35 on the natural-log scale)
are DESIGN CHOICES, not measurements — there is no upstream JSON artifact to bind them to the way
`null["method"]["min_duplex_bp"]` binds the duplex-pairing criterion. So the numbers sat in prose,
free-floating, and a future change to the cut, the assumed SD, or a replicate count — or a simple
copy-paste slip in any of the five figures — would pass every gate in the repository.

★ THE FIX: derive them from the two pre-registered constants below, the same way the manuscript's
own text derives them, so the manuscript's figures have exactly one place they could come from.
`CUT` here is the same "cut of 5.0" that
`test_the_falsification_cut_is_the_stated_value` in
`research/manuscripts/tests/test_the_paper_states_what_its_own_claims_depend_on.py` pins in the
prose; if that convention is ever revised, this module's `CUT` must move in the same commit, and
the test that reads both stays exactly two lines apart from a guaranteed disagreement rather than
zero lines from a silent one.

WHAT THIS IS NOT. Neither figure is a measurement — the underlying replicate SD of 0.35 is stated
in the article itself as "adopted for pre-registration rather than measured here." This module
computes what the STATED assumptions imply, not what any experiment observed.

    python3 research/manuscripts/aso_falsification_power.py    # print the table for a human
"""
from __future__ import annotations

import math

from scipy import stats

#: The pre-registered selectivity cut (fold-enrichment), on the natural scale. Matches the "cut of
#: 5.0" pinned in test_the_falsification_cut_is_the_stated_value — the two must move together.
CUT = 5.0

#: The assumed replicate standard deviation on the natural-log scale, adopted for pre-registration
#: rather than measured. Matches the article's own "assumed replicate standard deviation of 0.35".
SIGMA = 0.35

#: The true selectivity the power calculation asks whether the design could falsify.
TRUE_SELECTIVITY = 3.0


def power_pct(n: int, cut: float = CUT, sigma: float = SIGMA,
              true_selectivity: float = TRUE_SELECTIVITY) -> float:
    """Exact one-sided power, at n replicates, to put the upper 95% bound below `cut` when the
    true selectivity is `true_selectivity` — a noncentral-t calculation, since a normal
    approximation understates power at n=3."""
    df = n - 1
    log_cut, log_true = math.log(cut), math.log(true_selectivity)
    t_crit = stats.t.ppf(0.025, df)
    ncp = (log_true - log_cut) * math.sqrt(n) / sigma
    return stats.nct.cdf(t_crit, df, ncp) * 100


def void_sd(n: int, cut: float = CUT) -> float:
    """The realised SD above which no observed ratio at or above 1 can put the two-sided 95%
    interval's upper bound below `cut` — the design is void at n replicates above this SD."""
    df = n - 1
    t975 = stats.t.ppf(0.975, df)
    return math.log(cut) * math.sqrt(n) / t975


def main() -> int:
    print(f"CUT={CUT}, SIGMA={SIGMA}, TRUE_SELECTIVITY={TRUE_SELECTIVITY}")
    for n in (3, 6, 10):
        print(f"  n={n:>2}  power={power_pct(n):5.2f}%  void_sd={void_sd(n):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
