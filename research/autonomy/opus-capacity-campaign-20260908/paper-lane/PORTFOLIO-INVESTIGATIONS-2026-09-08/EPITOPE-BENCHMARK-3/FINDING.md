---
id: DOC-EPITOPE-BENCHMARK-3-FINDING
title: "EPITOPE-BENCHMARK-3 — the stale 37 was a coherent convention, not a typo; the corrected pin is prepared, proved minimal, and proved still to fire"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# EPITOPE-BENCHMARK-3 — one pin, re-derived, sourced, corrected in an UNAPPLIED diff, and shown still to discriminate

Writes confined to this directory. **The diff is NOT applied.** No `git add`, commit or push; no
`scripts/preflight.sh`; no subagent; no GPU, no paid API, no publication, no outreach, no download,
no direct HTTP (none attempted, so no refusal was met or worked around); cost $0. EPITOPE-BENCHMARK,
EPITOPE-BENCHMARK-2 and NEOANTIGEN-3 were **read only** — `git status --porcelain` on
EPITOPE-BENCHMARK is **empty** after every run (`checks/08`). NEOANTIGEN-3's
`assert len(VALIDATED) == 15` was not touched, and **n = 15 is not reopened here.**

⛔ **No immunogenicity, presentation, tolerance, efficacy, safety, selectivity, therapeutic-window or
clinical-readiness claim is made or implied.** Everything below is arithmetic about a confidence
interval's width and about whether a test file rejects a wrong number. Closed routes B1/B2, B4, B8
and B9 stayed closed; R1/R4, R2, R3 not restarted; MF1 and P-ST out of scope.

## 1 · Question

> Is the settled Wilson requirement at sensitivity 0.9 really **34**; where did the pinned **37**
> come from; and can the pin be corrected in a way that is provably *minimal*, *safe* and **still a
> working guard** rather than a number that no longer rejects anything?

## 2 · Merit

A pin is the only thing standing between a derived figure and silent drift. This one is **stale in
the direction that matters least and dangerous in the direction that matters most**: it is a real
guard on a real artifact, and the obvious one-line "fix" — retype 37 as 34 — **breaks the guard
immediately** (`checks/06`, exit **1**), because the producer still emits 37. A lane that changed
only the pin would have left the repository with a guard that fails on its own correct artifact, and
the natural next move under time pressure is to weaken the assertion. Establishing the *whole*
correction, and then proving the corrected pin still fires on eleven wrong values, is what makes the
change safe to hand to the owner. Patient relevance is indirect and honest: this is bookkeeping on a
sufficiency table whose conclusion (**INSUFFICIENT**) does not move.

## 3 · Evidence gap this lane closes

EPITOPE-BENCHMARK-2 flagged the stale pin, ran `check_consistency.py` unmodified, and **correctly
refused to repair another lane's guard** — leaving three things open: (i) an independent
re-derivation not taken from either lane's code; (ii) **the origin of 37**, which the parent
adjudication explicitly did not reverse-engineer, writing *"it comes from something narrower in this
lane's own search, and I have not reverse-engineered it further"*; and (iii) a concrete, checked,
unapplied correction. All three are closed below. **The parent adjudication's guess about the origin
was wrong, and that is reported rather than smoothed.**

## 4 · Step taken — (a) independent re-derivation

`rederive_wilson.py` (`checks/01`, exit **0**) implements the Wilson score-interval width from the
closed form and searches for the smallest n meeting width ≤ 0.20, under **four** successes
conventions. **Digit for digit, at sensitivity 0.9:**

```
p-exact  -> minimum n = 37   (phat=0.900000, width=0.198803)   <- what the producer does
k=round  -> minimum n = 34   (k=31, phat=0.911765, width=0.199139)
k=ceil   -> minimum n = 34   (k=31, phat=0.911765, width=0.199139)
k=floor  -> minimum n = 38   (k=34, phat=0.894737, width=0.199603)
```

**My re-derivation agrees with 34** under k=round and k=ceil, exactly as the parent arbitration
states, and with 38 under k=floor. The full ladder:

| convention | 0.5 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|
| **p-exact** | 93 | 78 | 60 | **37** |
| **k=round** | 93 | 78 | 60 | **34** |
| k=ceil | 93 | 76 | 58 | 34 |
| k=floor | 93 | 79 | 60 | 38 |

**Which convention is the rest of the ladder consistent with — the question that decides what kind
of defect this is.** The pinned ladder **93 / 78 / 60 / 37 is exactly and only `p-exact`**. The
corrected ladder **93 / 78 / 60 / 34 is exactly and only `k=round`**. `k=ceil` and `k=floor` are both
excluded by the 0.7 and 0.8 rows. So **37 is not a value consistent with nothing** — it is the value
consistent with the very convention that produced the other three rows. It is a defect of the
*abandoned-convention* kind, not the typo kind, and that is the milder of the two diagnoses.

The two candidate ladders agree on three of four rows **by coincidence of the arithmetic, not by
construction**: `p-exact` and `k=round` diverge only at 0.9. That coincidence is what makes the
correction a genuinely one-value change (§6).

## 5 · Step taken — (b) origin of 37, established from the retained records

**Not UNKNOWN. Not a typo. Not `k=floor`.** `origin_of_37.py` (`checks/02`, exit **0**) lifts the
sufficiency block **verbatim** out of `../EPITOPE-BENCHMARK/tabulate_epitopes.py`
(sha256 `477dbfaccb780e288f33c1db9aa87fe5b686c2ce8394aa3b64fc21ec8ec9ee7f`) by regex, `exec`s it, and
reports what it returns. It returns:

```
executed producer REQ = {0.5: 93, 0.7: 78, 0.8: 60, 0.9: 37}
block forms an integer success count k?  False
```

The producer's `n_for_width(p)` calls `wilson_width(p, n)` — **the continuous sensitivity `p` goes
straight into the interval; no integer success count is ever formed.** That is the `p-exact`
convention, and it yields 37 deterministically. **37 was correct under the convention actually in
force in the code that wrote the artifact, and under no other.**

**Why it was nonetheless retired, stated as arithmetic and not as taste:** a sensitivity is estimated
from an integer count of successes out of n, so the estimate must be *attainable at that n*. At
n = 37 the attainable count nearest 0.9 is `round(0.9 × 37) = 33`, giving width **0.204233 > 0.20** —
so **no real sample of size 37 meets the criterion**. 37 is therefore not a conservative larger
requirement that happens to be safe; it is unattainable as stated. Under `k=round` the smallest n at
which a real sample meets the criterion is **34** (width 0.199139). *This is a statement about
interval arithmetic only.*

**Correction to the parent adjudication, recorded rather than quietly absorbed.**
`PARENT-ADJUDICATION-34-vs-37.md` says *"Neither convention yields 37"* and attributes it to
"something narrower in this lane's own search." Both halves are wrong: a fourth convention it did not
enumerate — the continuous-p one, the one the producer actually implements — yields 37 exactly, and
also yields 93 / 78 / 60. Its **verdict (34) stands**; its **explanation of 37 does not.** The diff's
dated notes carry the corrected explanation so the record is not left with a wrong cause.

**One thing this lane did NOT resolve.** The adjudication also disputes
`achieved_ci_width_at_sens_0.5_with_n_available` — pinned **0.4515**, adjudicated **0.4507**. That is
a *separate* pinned quantity on a *separate* line, it is out of this lane's brief, and the diff
below deliberately **leaves it untouched and unchanged** (see §6). Its status here is **OPEN**, not
resolved and not silently swept into this correction.

## 6 · Step taken — (c) the UNAPPLIED diff, and the proof it is minimal

`0001-correct-wilson-0.9-pin-37-to-34.patch` — **four files, all inside EPITOPE-BENCHMARK, applied
nowhere.** It changes the *producer's convention*, the *derived artifact*, the *pin*, and the *prose
that quotes the value*; each carries a **dated 2026-09-09 note that preserves 37 and names its
origin** rather than erasing it.

**A pin-only change would have been wrong, and this was tested, not assumed.** `checks/06` patches
**only** `check_consistency.py` and leaves the artifact at 37: exit **1**, `FAIL: - Wilson n table
changed`. That failing run is preserved. This is why the diff touches the producer.

**Safe and strengthening, not merely different:**

| evidence | check | exit |
|---|---|---|
| baseline: `check_consistency.py` run **UNMODIFIED, in place** in EPITOPE-BENCHMARK | `03` | **0** — `Wilson 93/78/60/37` |
| patched producer regenerates the artifact from `epitope-records.json` | `04` | **0** |
| regenerated artifact vs. the hand-edited one | `04` | **IDENTICAL** — the diff is what the code produces, not a hand-typed number |
| regenerated artifact vs. the **original committed** artifact | `09` | exit 1 (diff found), and it is **one line**: `"0.9": 37` → `"0.9": 34`. Nothing else in 500+ lines moves — `0.4515`, `INSUFFICIENT`, the shortfalls, all 40 record ids, all strata are byte-identical |
| patched tree: `check_consistency.py` | `05` | **0** — `Wilson 93/78/60/34` |
| baseline stdout vs. patched stdout | `05` | **one line differs**, and only the `37`→`34` on it. Every other assertion prints the same |
| `git apply --check -v` from the repo root | `08` | **0**, all four files |
| live tree after every run | `08` | `git status --porcelain` on EPITOPE-BENCHMARK: **empty** |
| counterfactual: pin-only patch | `06` | **1** — proves the producer change is necessary |

**No assertion was removed, loosened, or made conditional. The assertion count is unchanged, the
equality is still an exact dict equality on all four rows, and the printed banner still names every
figure.**

## 7 · ⚠ The part that matters most — the corrected pin still FIRES

An arithmetically-right pin that no longer discriminates is worse than a stale one. `checks/07`
(`guard_firing_battery.py`, exit **0**) builds fixtures in which **the guarded quantity itself is
wrong** — `sufficiency.n_required` in the regenerated artifact — and runs the **corrected**
`check_consistency.py` against each as a subprocess, recording the real `returncode` (no pipes).

**Two controls — correct values that must NOT trip it:**

| control | exit | required |
|---|---|---|
| the correct ladder `93 / 78 / 60 / 34` | **0** | must not fire ✓ |
| `"0.9": 34.0` — the neighbouring *correct* representation of the same value | **0** | must not fire ✓ |

**Eleven fixtures — wrong values that MUST be rejected. All eleven fired, exit 1, `Wilson n table changed`:**

`0.9 = 37` (**the stale value the diff supersedes — the corrected pin rejects it**) · `0.9 = 33`
(one below) · `0.9 = 35` (one above) · `0.9 = 38` (the `k=floor` value) · `0.5 = 92` · `0.5 = 94` ·
`0.7 = 77` · `0.7 = 79` · `0.8 = 59` · `0.8 = 61` · the `0.9` row deleted entirely.

**Both neighbours of every one of the four rows are rejected, and the only ladder accepted is the
correct one.** The guard is not a tautology, it did not lose resolution in the correction, and it
now rejects the very value it used to assert. Its discriminating power is strictly **greater** than
before on one axis (it rejects 37) and unchanged on the other three rows.

## 8 · Site census

`SITE-LIST-34-vs-37.md` — every file and line quoting this quantity. Summary: **eleven** sites carry
37, of which the diff changes **six** (all in EPITOPE-BENCHMARK); five deliberately keep it — the
arbitration record itself, two retained `checks/` stdout logs (a check log records what actually
ran and is never retrofitted), and EPITOPE-BENCHMARK-2's two true quotations of them. **Five** sites
carry 34, all in VACCINE-PATH-2, all already correct and untouched. And three negatives worth
stating: **`research/manuscripts/pinned-figures.json` does not pin this quantity at all** (its `34`s
are the 34-allele screen, a different number); **PUB-VACCINE-PATH's manuscript does not print the
ladder** — its Wilson intervals were withdrawn; and `systems/graph/*.json` and `systems/views/` do
not contain it. **The diff's blast radius is one lane's directory.**

## 9 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `0001-correct-wilson-0.9-pin-37-to-34.patch` (**unapplied**), `rederive_wilson.py`,
  `origin_of_37.py`, `guard_firing_battery.py`, `SITE-LIST-34-vs-37.md`, `sandbox/` (the patched
  tree the checks ran against), `sandbox-pinonly/` (the counterfactual tree), `runcheck.sh`, and
  `checks/` — **nine attempts, all preserved, real exit codes, including the two deliberate
  failures** (`06` exit 1, `09` exit 1).
* **Validation / baseline.** The unmodified baseline is `checks/03`, exit 0. Every claim in §6 and
  §7 is an execution in `checks/`, not an assertion. The re-derivation was written from the Wilson
  closed form in this lane and **agrees with 34**; had it disagreed, that would have been the finding
  and the diff would not exist.
* **Provenance.** `../EPITOPE-BENCHMARK/{tabulate_epitopes.py (sha256 477dbfac…9ee7f),
  check_consistency.py, validated-epitope-counts.json, FINDING.md,
  PARENT-ADJUDICATION-34-vs-37.md}`; `../EPITOPE-BENCHMARK-2/FINDING.md`; `../VACCINE-PATH-2/`;
  `../NEOANTIGEN-3/` — **all read-only**. No external source was consulted, and none was needed: this
  is arithmetic on a stated criterion, not a literature question, so the PubMed/PMC MCP route was
  not used.
* **Limitations.** (i) **This lane does not adjudicate which successes convention a sufficiency table
  *should* use.** It takes 34 as settled by two independent lanes plus the parent arbitration, shows
  the arithmetic that supports it, and shows that adopting it changes exactly one value. A reader who
  preferred `p-exact` would keep 37 — and the §5 attainability argument is the case against that, not
  a proof. (ii) The `0.4515` vs `0.4507` achieved-width dispute is **OPEN and untouched**. (iii) The
  criterion itself (95% Wilson width ≤ 0.20) is inherited from EPITOPE-BENCHMARK's attribution to
  PUB-VACCINE-PATH; the manuscript no longer prints it, so the attribution could not be verified
  against a printed sentence — recorded as **unverified attribution**, not as a defect.
  (iv) `n = 15`, the verdict `INSUFFICIENT`, and the ~6× shortfall are **unchanged and unexamined**
  here. (v) The diff is unapplied and unreviewed by the owner; nothing in the repository has changed.
* **Stop condition.** **Reached.** The pin was re-derived, its stale value sourced to a named
  convention in named code, a minimal correction prepared and proved safe by execution, and the
  corrected guard proved still to fire. **This lane stops. The diff is EPITOPE-BENCHMARK's to apply.**

## 10 · Next credible independent work (not done, not authorised here)

1. **Owner applies the diff** in EPITOPE-BENCHMARK's lane; `checks/08` shows it applies cleanly.
2. **Resolve `achieved_ci_width_at_sens_0.5_with_n_available`: 0.4515 (p-exact) vs 0.4507
   (integer-k).** Note the dependency: if that is also moved to the integer-k convention, the
   producer's `wilson_width(0.5, n_bench)` call at line 87 must change too, and *that* would be a
   second one-value change to the same artifact. This lane left it alone precisely so the two do not
   get entangled.
3. **Amend `PARENT-ADJUDICATION-34-vs-37.md`** to carry the corrected origin of 37 (§5), since its
   stated cause is wrong even though its verdict is right.
