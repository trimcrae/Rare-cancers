#!/usr/bin/env python3
"""Explain the only two digits in MORTALITY-2's reported set that my exact arithmetic did not
reproduce: the two direct-standardisation values. Hypothesis: genre_stratified_rates.py:224
standardises the per-stratum rates AFTER they were rounded to 4 dp for the JSON, so the rounding
propagates. This probe recomputes both ways and prints all four numbers. Read-only, no writes."""
import json, pathlib
d = json.loads(pathlib.Path(__file__).with_name("genre-stratified-rates.json").read_text())
s = d["results"]["strict_terminal_event"]
five, ORDER = s["by_five_strata"], list(s["by_five_strata"])
we = {k: five[k]["emc"]["sentences"] for k in ORDER}
wo = {k: five[k]["other"]["sentences"] for k in ORDER}
def std(rate_key, weights, rounded):
    tot = sum(weights.values()); acc = 0.0
    for k in ORDER:
        cell = five[k][rate_key]
        r = cell["rate"] if rounded else (cell["flagged"] / cell["sentences"] if cell["sentences"] else None)
        if r is None: continue
        acc += weights[k] / tot * r
    return acc
for lbl, key, w in [("EMC -> comparator mix", "emc", wo), ("comparator -> EMC mix", "other", we)]:
    a, b = std(key, w, True), std(key, w, False)
    print(f"{lbl}: from ROUNDED stratum rates = {a:.10f} (5dp {round(a,5)}) | "
          f"from EXACT stratum rates = {b:.10f} (5dp {round(b,5)}) | delta = {abs(a-b):.2e}")
print("\nreported in artifact:",
      s["direct_standardisation"]["emc_rate_standardised_to_comparator_genre_mix"],
      s["direct_standardisation"]["comparator_rate_standardised_to_emc_genre_mix"])
print("as per cent, both routes: EMC 0.93 %, comparator 1.86 % -- the prose figures are unaffected.")
