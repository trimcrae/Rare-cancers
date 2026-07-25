# The reach rule credited the pendant with shortening the span — correction, re-run, and what moved

**LANE 10 · 2026-07-25 · $0 realized (CPU/CI only, no GPU) · branch `claude/max-effort-2dq11l-reach`**

**STATUS: results pending the corrected production runs; this document is the method + the pre-run analysis.
Numbers marked ⏳ are filled from the CI artifacts when they land.**

---

## 1 · The defect, in one line

RUNG 5a's term-(a) criterion was the prolate-spheroid **relaxation**

```
|q-a| + |q-b|  <=  n*rise + 2e            (basin_geom.linker_can_visit)
```

which is a **necessary** condition, not a sufficient one. Its loophole needs no computation to see. By the
triangle inequality `|q-a| + |q-b| >= |a-b|`, so for a nucleophile sitting **on** the anchor-anchor segment
the rule reduces to

```
span  <=  n*rise + 2e
```

— the pendant arm buying up to `2e/rise = 6.0/1.25 = 4.8 → 5` backbone atoms of **span**. No pendant can do
that. The pendant hangs off the backbone; the backbone still has to connect the warhead exit vector to the E3
exit atom, so `n*rise >= span` however long the arm is.

**Every published RUNG-5a C397 figure is therefore a LOWER BOUND on the length a linker actually needs.**
Lane 6 audited all 576 (basin × unique cysteine) records and found none internally impossible — no record's
`min_linker_atoms` sits below its own `min_linker_atoms_for_span` — so this is a **bound, not an error**. But
the bound is up to ~5 atoms wide, the gate is read at 12 atoms, and the term-(a) reach fractions are
0.019–0.057, so the correction is decision-relevant rather than cosmetic.

## 2 · What replaced it

`linker_design.min_linker_atoms_exact` — the shortest `n` for which **some integer branch position `k`**
admits a common point of the three balls

```
B(a, k*rise)      the chain from the warhead anchor to the branch atom
B(b, (n-k)*rise)  the chain from the branch atom to the E3 anchor
B(q, e)           the pendant, from the branch atom to the cysteine SG
```

This is the kernel RUNG 5b already hands to a chemist. After the correction **the repo holds one reach rule
instead of two that disagreed**, and the number the gate is read on is the number a molecule would be built
at. The superseded relaxed value is carried **per record** (`*_relaxed_superseded`), not dropped, so the
change is auditable at the record level rather than only in prose.

Three structural facts make the swap safe and cheap, and all three are unit-tested:

| fact | why it holds | test |
|---|---|---|
| exact ≥ relaxed | a witness `p` gives `\|q-a\|+\|q-b\| <= (\|p-a\|+e)+(\|p-b\|+e) <= n*rise+2e` | `test_exact_is_never_below_relaxed_or_the_span_floor` |
| exact ≥ span floor | the same witness gives `\|a-b\| <= \|p-a\|+\|p-b\| <= n*rise` | same |
| the scan may **start** at `max(floor, relaxed)` | both are necessary, so nothing below can be feasible | `test_exact_scan_start_is_exact_not_a_heuristic`, against a scan from `n=2` |

The third is what makes the exact kernel affordable at ~10⁵ calls inside the 5a inner loop (~1.5 ms/call,
~2 min added to a ~72 min run) instead of only on a handful of exemplars.

**The gate arm is UNCHANGED at 3.0 Å.** It is shorter than every named building block in
`linker_design.PENDANT_REACH_A` (aryl-direct 4.0, aryl branch residue 4.5, amide-direct 5.0, Dap 7.5,
Dab 8.75), so it is the conservative reading. Moving the gate onto a longer pendant *after* seeing that the
correction costs basins would be precisely the tuning STRATEGY.md's load-bearing piece 5 forbids. The
named-pendant sweep is now emitted per basin as `fraction_reachable_at_gate_by_pendant` and is a **sensitivity,
never the gate**.

## 3 · Three things the correction dragged out with it

**(a) The same rule was written twice and only one copy carried the constraint.**
`term_a_feasibility_envelope` — the E3-**independent** upper bound — used the relaxed criterion too, but it
was already span-correct *by construction*, because it draws the E3 anchor at radius `r <= L`. So the two
implementations of "can a linker reach this cysteine" disagreed, and the disagreement was invisible because
neither was compared to the other. Both now call the shared kernel.

**(b) Exemplar selection was part of the bug.** The exemplar — the member a chemist designs on — was the
member with the smallest **focal sum**. Under the relaxed rule that is the same thing as the shortest linker.
Under the exact rule it is not: the span enters, so the member *closest* to the cysteine can need a *longer*
chain than one slightly further away but better placed between the anchors. Exemplar selection is now on the
exact requirement, focal sum breaking ties.

**(c) `--self-test` overwrote the production artifact.** The synthetic self-test wrote to the same default
`--out` path as the real run. It destroyed the committed 12-pose result **twice in one session** and was
caught only by `git status`. A lane that ran the self-test and then committed would have replaced the
definitive Tier-2 result with synthetic numbers, under the filename every downstream consumer reads without
question (RUNG 5b, STRATEGY.md's Tier-2 block, `nr4a3_handle_ensemble`). Fixed: separate default filename
under `--self-test`, plus a `.gitignore` entry.

## 4 · What the correction can and cannot do to the Tier-2 gate

The gate is a **disjunction**: `cat_a or cat_b`, where `cat_b` counts basins whose transfer zone covers a
paralogue-unique lysine **and** beats the null. **The reach rule does not enter term (b) at all**, and term (b)
stands at **40** basins. So:

> **The Tier-2 GO cannot fail from this correction.** What is at risk is the *term-(a) count* (published: 7)
> and the *headline* — that the strongest basin `crbn|M0` reaches C397 at a chemically routine length.

Two further certainties follow from `exact ≥ relaxed` being pointwise:

* **C420 and C559 cannot come INTO the gate.** The corrected requirement is never shorter than the published
  one, and both already sat above 12 atoms. The categorical chemistry axis stays one residue deep; the only
  question the re-run can answer is whether it gets *thinner*.
* Every corrected figure is ≥ its published value, so no number moves in the flattering direction.

### Pre-run bracket, from the committed artifact ($0, seconds)

The exemplar placements stored in `nr4a3-orientation-basins.json` carry both the focal sum and the span, so
the corrected requirement **at the old exemplar** is computable without re-running anything. Because the old
exemplar minimised the *focal sum* rather than the *exact* requirement, these are an **upper** bracket on what
the re-run will report; the published relaxed values are the lower one.

| meta-basin | poses | published (relaxed) | exact **at the old exemplar**, 3.0 Å arm | still ≤ 12-atom gate? |
|---|---|---|---|---|
| **`crbn\|M0`** | 11/12 | 11 | **13** | ✗ at this member |
| `vhl\|M3` | 9/12 | 8 | **11** | ✔ |
| `vhl\|M2` | 6/12 | 9 | **11** | ✔ |
| `vhl\|M4` | 5/12 | 12 | **15** | ✗ at this member |
| `vhl\|M14` | 3/12 | 12 | **13** | ✗ at this member |

So **at least 2 of the 7 term-(a) basins survive the corrected gate**, on the old exemplars alone, and the
re-run can only find shorter members. With a real pendant rather than the 3.0 Å convention, `crbn|M0`'s
exemplar needs **12** atoms (aryl branch residue, 4.5 Å) or **11** (Dab branch, 8.75 Å) — reported as a
labelled sensitivity, not as the gate.

## 5 · Results of the corrected runs

### 5.0 · A mismatch caught before it was quoted, and how

The first corrected run (CI 30178697504) returned **term (a) = 0**. Before reporting that as the effect of the
rule, two numbers in its own output were checked against the published run and did not match: `runtime_s`
**1082 vs 4295**, and `term_b` **31 vs 40** — and term (b) is *untouched* by the reach rule, so it had no
business moving at all. That is the discriminating observation. The cause is in the artifact, not in the
rule: **`samples_per_arm_pose` = 250 000 vs the published 1 000 000.** The published 12-pose run was launched
with `--samples 1000000` via `ternary_extra_args`; my dispatch omitted it and took the script default. Accepted
counts confirm it directly — `vhl` pose 0: **1003 → 257**, `crbn` pose 0: **845 → 196**, a clean ~4× across
every pose.

Two consequences, both load-bearing:

* **Meta-basin IDs are positional and are NOT comparable across runs with different sampling.** `vhl|M4` reads
  0.42 pose persistence in one run and 0.75 in the other; they are different basins wearing the same label.
  Any comparison has to be matched on the **interface patch** (Jaccard), which `scratchpad/lane10-compare.py`
  does.
* The definitive comparison needed a re-run at 10⁶ (CI 30179315860). ⏳

### 5.1 · The matched 10⁶ comparison

⏳ *pending CI 30179315860.*

### 5.2 · What the 250 k run already establishes (rule-only quantities)

Two things in that run are **not** sample-count-sensitive in the way the basin counts are, and both point the
same way:

**The E3-INDEPENDENT envelope did not move at all.**

| | C397 | C420 | C559 |
|---|---|---|---|
| published (relaxed) | 10 atoms | 16 | 20 |
| corrected (exact) | **10** | **16** | **20** |

The upper bound is unchanged, which is exactly what the envelope's construction predicts: it already drew the
E3 anchor at radius `r <= L`, so it never gave the pendant the span. **The target-side geometry is not what
the correction breaks.** If term (a) falls, it falls because no E3 body docks where an exact-feasible 12-atom
path exists — a fact about the RECRUITER placements, not a closed target. That is the distinction the envelope
was built to make, and it is the difference between "widen the E3 panel" and "this mechanism is closed".

**The correction costs about one atom at each basin's minimum, and one atom is enough at a 12-atom gate.**
Within the 250 k run, comparing each basin's own `min_linker_atoms_relaxed_superseded` against its exact
value: 12 → 13, 13 → 14, 12 → 13 on the basins that had been at or just under the gate. The published minima
of 8, 9, 11 and 12 atoms were the *low* end of a bound up to 5 atoms wide, and the exact values land above 12.

**C420 and C559 are reached by NO basin at the gate with ANY named pendant** — not at 3.0 Å, not at the 8.75 Å
Dab branch. The categorical chemistry axis is confirmed one residue deep, and more firmly than before.

### 5.3 · The pendant sweep, and why it is not a rescue

The gate is read at the preregistered **3.0 Å** arm. That value is **shorter than every real pendant**, and
this was recorded by RUNG 5b **before** the corrected run existed — it is item 4 of
`_corrections_to_rung_5a` in the committed `nr4a3-linker-design.json`: *"an aryl bonded to a backbone carbon
reaches ~4 Å, a directly N-acylated acrylamide ~5 Å, and a Dab-type branch carrying a cyanoacrylamide
~8.75 Å. The gate is therefore CONSERVATIVE on term (a)."*

So the 250 k run's pendant sweep is a pre-registered sensitivity, not a post-hoc reach for a better number
(C397, meta-basins reaching the **12-atom** gate):

| pendant | reach | meta-basins reaching C397 at the gate | best fraction |
|---|---|---|---|
| `rung5a_convention` **(THE GATE)** | 3.00 Å | **0** | — |
| `aryl_direct` | 4.00 Å | 3 | 0.091 |
| `aryl_branch_residue` | 4.50 Å | 6 | 0.091 |
| `amide_direct` | 5.00 Å | 7 | 0.091 |
| `dap_branch` | 7.50 Å | 11 | 0.200 |
| `dab_branch` | 8.75 Å | 18 | 0.250 |

**Two conservatisms were stacked.** The 3.0 Å arm was chosen while the rule was simultaneously giving away up
to 5 atoms of span; removing the giveaway without revisiting the arm leaves a gate that no realisable
chemistry is being asked to clear. **Re-reading the gate at a real pendant would be a change to a
preregistered threshold made after seeing the result, so it is NOT a call this lane makes** — the corrected
number at 3.0 Å is reported as the primary result and the sweep beside it, and the choice is surfaced.

### 5.4 · The conformer ensemble, matched and re-run (`nr4a3-handle-ensemble.json`, $0 local)

The same relaxed rule fed `nr4a3_handle_ensemble.py` through `term_a_feasibility_envelope`, so the three
figures STRATEGY.md and three manuscripts quote — "C397 reaches the 12-atom gate in **96 %** of unbiased MD
frames, C420 and C559 in **0 of 75**" — were computed with it. Re-run over the same 100 conformers
(75 unbiased release + 25 metadynamics), identical seed, identical everything but the rule:

| quantity, 75 unbiased frames | published (relaxed) | corrected (exact) |
|---|---|---|
| C397 at or below the 12-atom gate | **72/75 = 96 %** | **65/75 = 87 %** |
| C397 median shortest linker | 10 atoms | **12 atoms** |
| C397 RSA median (unchanged — not a reach quantity) | 0.4156 | 0.4156 |
| C420 at the gate | 0/75 | 0/75 |
| C420 median shortest linker | 16 atoms | **20 atoms** |
| C420 frames never open within 20 atoms | 1 | **5** |
| C559 at the gate | 0/75 | 0/75 |
| C559 frames **never open within 20 atoms** | 14 | **45** (60 % of frames geometrically closed) |
| joint P(pocket druggable **and** C397 reachable) | 0.56 | **0.48** |
| P(C397 reachable │ pocket druggable) | 0.955 | **0.818** |

**Read it as three things.** (i) C397 survives comfortably — 87 % of unbiased conformers still present it at
or below the gate, and it is the *median* frame that now needs 12 atoms rather than 10. (ii) The
one-residue-deep risk gets **worse**, not better: C559 is now geometrically closed in 60 % of frames rather
than 19 %. (iii) The joint number is the one to quote — the pocket being open and C397 being reachable are
**not** independent and the conditional fell from 0.955 to 0.818, so "96 % reachable" was doing more work in
prose than it should have.

**And this is the observation that keeps the two results coherent.** The conformer ensemble says C397 *is*
reachable at 12 atoms in 87 % of frames; the basin search says **no basin** places an electrophile there. Both
are computed with the same corrected rule and they do not contradict: the ensemble is the
**E3-INDEPENDENT** bound (is there *any* spannable anchor position from which a 12-atom chain works?), the
basin search additionally requires **a real E3 body actually docked at such a position without clashing**. The
gap between 87 % and 0 is therefore a statement about the **recruiter placements**, not about the target —
which is exactly the distinction the envelope was built to make, and it is the difference between "widen the
E3 panel" and "this mechanism is closed."

## 6 · RUNG 5b re-enumerated at exemplar geometry

Lane 6 named this as its own next step: *"re-enumerate the library at exemplar geometry, and swap the 3-point
span approximation for the now-emitted deciles."* Both done.

`basin_requirements` now returns **two** records per basin — representative and term-(a) exemplar — from one
derivation, and the **identical** enumerator and **identical** preregistered filter run against each. A
difference between the two libraries is therefore a difference in the geometry, not in the rule.

Four defects surfaced by doing it:

1. The **preregistered wedge chemistry rule** (NR4A3 presents an H-bond donor, **both** paralogues do not) was
   applied only on the exemplar path. The representative pair satisfied it by luck, not by construction. Now
   binding on both paths and named in the selection audit's blocker text.
2. The **span distribution was looked up from the representative's member basin**. The exemplar routinely comes
   from a *different* member basin in a *different* pose with *different* deciles, so the exemplar's
   accessibility was being computed over another placement's basin. Looked up per placement now.
3. Each construct's reported `span_window_A` was the 3-point `{min, median, max}` while its own fidelity
   numbers were computed over the **deciles** — the one place in the rung where a construct's reported span
   window disagreed with the distribution it was scored against. Now the deciles, with the 3-point summary
   retained beside it.
4. `arm_selection_note` **transcribed** in prose which basin was excluded and the length that excluded it.
   That sentence goes stale the moment the geometry changes — the drift class `lint_consistency.py` exists to
   catch. Derived from the audit now.

### The finding nobody asked for: the fidelity filter carries no basin-quality information

The library carries a **labelled weak control** (`vhl|M14`, which does not exceed the term-(b) background) so
that "the filter selects good basins" is falsifiable rather than tautological. Read at both placements:

| placement | `crbn\|M0` (strongest) | `vhl\|M3` | `vhl\|M2` | `vhl\|M4` | `vhl\|M14` (weak control) |
|---|---|---|---|---|---|
| representative | **0 on merit**, 1 despite failing | 9 | 9 | 0, 1 despite failing | **0 on merit**, 1 despite failing |
| term-(a) exemplar | 9 | 9 | 9 | 9 | **9** |

At the representative it rejected RUNG 5a's **strongest** basin on exactly the ground it rejected the weak
control — a long representative span. At the exemplar all five pass identically at the diversity cap. The
filter tests whether a *linker* can hold a basin, which is not the same question as whether the *basin* is
good, and it must not be credited with an answer it never computes. Basin quality comes from Tier 2 (terms a
and b, pose persistence) and from nowhere else. Emitted per placement as `filter_control_reading` so the
reading lives in the artifact rather than in prose.

### The recommended matched pair

**Unchanged, and it now has molecules.** `crbn|M0` at its term-(a) exemplar, **3-(3-pyridyl)-L-Ala (*d*) vs
L-Phe (*d₀*)** at **Thr407** (Leu in NR4A1, Val in NR4A2 — the donor is removed in **both**), **8.6 Å** of E3
clearance. It was previously a design target *without SMILES*; it is now an enumerated, filtered,
RDKit-verifiable `d`/`d₀` pair selected by the same code as the representative pair, at 14 backbone atoms.
"Differs only in the wedge element" is intact: one atom (C–H → N), identical formal charge, heavy-atom count,
rotatable bonds and (S) centre.

## 7 · Honest scope

Unchanged by any of this, and it bounds everything above: conditional on the **hypothesised cmpd19 binary
pose × the chosen receptor frame** — a double conditionality — and on one static opened conformer per
paralogue. A basin is a **nomination of a region of orientation space**, not a modelled complex. Every
construct is a **predicted selective candidate**, never a selective hit. No efficacy, safety,
therapeutic-window or clinical claim is made or implied.
