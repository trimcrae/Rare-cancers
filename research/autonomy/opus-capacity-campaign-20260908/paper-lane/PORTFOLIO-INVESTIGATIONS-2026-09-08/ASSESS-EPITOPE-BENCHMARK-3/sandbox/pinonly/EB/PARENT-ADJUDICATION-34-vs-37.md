---
id: DOC-OPUS-CAMPAIGN-EPITOPE-ADJUDICATION
title: "Parent adjudication: 34 vs 37, and the achievable-width digit"
level: L4
kind: adjudication
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Two of my lanes disagreed by one number. Here is the arbitration.

This lane reproduced PUB-VACCINE-PATH's Wilson sufficiency table and reported **93 / 78 / 60 exactly**
but **37** where that lane reported **34** at sensitivity 0.9 — and flagged the difference rather
than smoothing it, which is why it could be settled.

**I recomputed independently, from the Wilson closed form, with no reference to either lane's code:**

| sensitivity | minimum n for 95% CI width ≤ 0.20 | width at that n |
|---|---|---|
| 0.5 | **93** | 0.1992 |
| 0.7 | **78** | 0.1985 |
| 0.8 | **60** | 0.1995 |
| 0.9 | **34** | 0.1991 |

**PUB-VACCINE-PATH's 34 is right; this lane's 37 is the outlier.** The cause is the successes
convention, not the interval:

```
sens 0.9, k = round(0.9n) → minimum n = 34  (k=31, width 0.1991)
sens 0.9, k = ceil (0.9n) → minimum n = 34  (k=31, width 0.1991)
sens 0.9, k = floor(0.9n) → minimum n = 38  (k=34, width 0.1996)
```

Neither convention yields 37, so 37 is not simply a floor/ceil choice — it comes from something
narrower in this lane's own search, and I have not reverse-engineered it further because **the
number does not matter to either conclusion.**

**Achievable width at n = 15, sensitivity 0.5:** I get **0.4507**, this lane reported **0.4515**. At
n = 15 the half-success is exact — `0.5 × 15 = 7.5` — and `k = 7` and `k = 8` both give **0.4507**,
so the reported 0.4515 differs in the third decimal by a route I did not reproduce. This lane had
already caught and corrected a related rounding slip in its own `checks/06`, which failed at exit 1
and was fixed by tightening the assertion rather than loosening it — the right response.

## Why neither digit changes anything

The finding is a shortfall of **roughly six-fold**: n = 15 against a requirement of 93 at
sensitivity 0.5, and **short of the preregistered floor of 30 before any width criterion applies at
all**. Whether the sensitivity-0.9 row reads 34 or 37, and whether the achievable width is 0.4507 or
0.4515, the conclusion is identical and neither lane's argument depends on the digit.

**Recorded because a number that two of my own lanes disagree on should be arbitrated, not
averaged or quietly dropped.** No value in either lane's artifacts was edited.
