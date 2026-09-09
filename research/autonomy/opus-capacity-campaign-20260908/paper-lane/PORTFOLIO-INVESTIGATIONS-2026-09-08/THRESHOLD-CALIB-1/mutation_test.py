#!/usr/bin/env python3
"""Show the chance criterion CAN fail: feed the separating labels through the same
at_chance test WITHOUT shuffling. If it still says AT CHANCE the criterion is inert."""
import random, statistics, sys
import threshold_calibration as tc

ctrl = random.Random(tc.SEED + 1)
pos = [ctrl.lognormvariate(4.0, 1.0) for _ in range(200)]
neg = [ctrl.lognormvariate(7.5, 1.0) for _ in range(200)]
scores = pos + neg
labels = [1] * 200 + [0] * 200

vals = [tc.auroc(pos, neg)] * 2000          # the null with the shuffle REMOVED
vals.sort()
lo, hi = vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
mean = statistics.fmean(vals)
at_chance = lo <= 0.5 <= hi and abs(mean - 0.5) < 0.02
print(f"unshuffled 'null': mean={mean:.5f} [{lo:.5f}, {hi:.5f}] at_chance={at_chance}")
real = tc.shuffled_null(scores, labels, random.Random(tc.SEED + 2))
print(f"properly shuffled null: mean={real['mean_auroc']} at_chance={real['at_chance']}")
ok = (at_chance is False) and (real["at_chance"] is True)
print("MUTATION TEST", "PASSED — the criterion discriminates" if ok else "FAILED — criterion inert")
sys.exit(0 if ok else 1)
