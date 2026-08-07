---
id: DOC-PARALOGUE-POCKET-ASYMMETRIC-READ
title: IC-4-A — the paralogue cryptic-pocket contrast carries two verdicts, not one
level: L4
kind: memo
status: live
canonical_for: []
purpose: Whether `paralogue-pocket-contrast.json`'s single pooled verdict hides an asymmetry along RT-ASYMMETRIC's mandatory / best-effort axes, and whether the split reading survives an honest small-n interrogation.
scope: One re-read of committed artifacts. No new data, no new compute.
audience: [maintainers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-08-06
---
# IC-4-A — the paralogue cryptic-pocket contrast carries two verdicts, not one

> **$0 CPU. NO NEW COMPUTE OF ANY KIND.** No fpocket run, no MD, no GPU, no rental. Every input is a
> committed artifact and every statistic is exact enumeration in the standard library. Nothing here is a
> claim about binding, reactivity, degradation, selectivity in vivo, efficacy or safety.
>
> **★ ONE FACT, ONE PLACE.** Every number lives in
> [`paralogue-pocket-asymmetric-read.json`](./paralogue-pocket-asymmetric-read.json), produced by
> [`paralogue_pocket_asymmetric_read.py`](./paralogue_pocket_asymmetric_read.py) and pinned by
> [`tests/test_paralogue_pocket_asymmetric_read.py`](./tests/test_paralogue_pocket_asymmetric_read.py).
> This file carries the reasoning and points at the JSON. The source artifact,
> [`paralogue-pocket-contrast.json`](./paralogue-pocket-contrast.json), is a **landed record and is not
> modified** — its reasoning keeps its own home at
> [`paralogue-pocket-contrast.md`](./paralogue-pocket-contrast.md).

---

## 1 · The defect: one `and` where the program asks two questions

`paralogue-pocket-contrast.json` reports a single pooled verdict, built in
[`paralogue_pocket_contrast.build_map_edits`](./paralogue_pocket_contrast.py) by

```python
sep = all(v is not None for v in (r3[0], r1[1], r2[1])) and r3[0] > r1[1] and r3[0] > r2[1]
```

— one boolean over **both** paralogues. The conjunction goes false as soon as *either* paralogue fails, and
the emitted string names neither, so a reader cannot tell which one failed, or whether both did.

That would be a presentation quibble if the program treated the two paralogues as one requirement. It does
not. [`RT-ASYMMETRIC`](../../systems/views/L2-rt-asymmetric.md) is titled *"NR4A1-sparing **mandatory**,
NR4A2-sparing **best-effort**"*, and its route record states that dropping the asymmetry *"lets a symmetric
restatement back in"*. A conjoined verdict is exactly such a restatement: **it reports the best-effort
axis's answer on the mandatory axis's behalf.**

⚠ **No number in the source artifact is wrong and no rule is loosened here.** Every figure reproduces
exactly (`_provenance_checks` re-derives them and requires agreement). The entire intervention is deleting
one `and` — the rule `NR4A3's worst release replicate beats the paralogue's best` is applied per paralogue
instead of conjoined. A rule *changed* after seeing which paralogue fails would be the outcome-selection
defect the harmonized rerun exists to remove; a rule *scoped* to the axis the program already declared is
not.

## 2 · What the split says

Read `verdict` and `per_paralogue` in the JSON. In words, and without their numbers (rule 1):

- **Mandatory axis (NR4A1):** the source artifact's own rule returns **SEPARATED at replicate
  granularity** — NR4A3's worst unbiased release replicate beats NR4A1's best, with every pairwise
  replicate comparison in NR4A3's favour.
- **Best-effort axis (NR4A2):** the same rule returns **RANKED but replicate ranges OVERLAP**.
- Therefore the pooled *"RANKED but replicate ranges OVERLAP"* is driven by **NR4A2 alone**
  (`verdict.the_pooled_verdict_is_driven_by`).

★ **The direction agrees with an independent, non-simulation reading of the same asymmetry.**
[`target-route-options.md` route 1](../manuscripts/target-route-options.md#route-1--asymmetric-selectivity-nr4a1-sparing-mandatory-nr4a2-sparing-best-effort--pk)
already records that all 7 Pocket-5 handles differ against NR4A1 but only 6 of 7 against NR4A2 — *"the
programme has more discriminating power against the paralogue whose sparing is mandatory"*. That is a
sequence fact and this is a conformational-frequency fact; they are not the same evidence and they point
the same way. **They are not independent confirmations of a mechanism** — the site definition is shared —
but the ordering was not put in by hand.

## 3 · The honest interrogation — and it demotes the finding

The interesting question is not whether the conjunction splits (it does, arithmetically, in one line). It
is whether a 3-vs-3 replicate comparison can carry the word **SEPARATED** at all. Four readings, each
computed rather than asserted, all in `small_n_interrogation` and `per_paralogue.*`:

1. **The exact test is at its ceiling, not past it.** With 3 vs 3 there are exactly 20 label assignments,
   so the smallest attainable one-sided p is 1/20 — and *"worst beats best"* **is** complete separation,
   i.e. the rule fires precisely when the exact permutation test hits its floor. ⚠ **So the achieved p must
   be read as "the design's ceiling", never as "just significant".** The two-sided floor is twice that, and
   two paralogue comparisons were made, so the Holm-adjusted p **cannot** reach 0.05 whatever the data. The
   defensible statement is a **ranking with an effect size**, not a significance claim.
2. **The effect size is maximal on the mandatory axis** (Cliff's δ = 1, every pair favouring NR4A3) and
   large but not maximal on the best-effort axis. An exhaustive cluster bootstrap — replicate as the
   resampling unit, all 3³ resamples per arm enumerated, so it is seedless and a re-run cannot move it —
   puts the difference away from zero on both axes.
3. **The pooled Wilson interval is anti-conservative, and now by a MEASURED amount.** The source artifact
   says so and never quantified it; `design_effect_measured` does. Correcting each species' interval by its
   own measured design effect **flips the NR4A1 pooled-interval reading from separated to overlapping** —
   narrowly, but it flips. This is a third, independent way of saying the same caution and it disagrees
   with the rank test, which is exactly why both are reported.
4. **The margin is small against the spread it is built from.** NR4A3's worst-replicate-beats-best margin
   on the mandatory axis is a fraction of NR4A3's own between-replicate SD. A normal-model predictive
   interval for a *fourth* NR4A3 replicate is wider than the [0,1] range the statistic lives in — which is
   not a usable interval, and is itself the finding: **at n = 3 the between-replicate spread is barely
   estimated.**

### 3.1 · ⛔ And the mandatory separation does **not** survive the contested `C2` rule

This is the reading that decides how the result may be written, and it had never been taken.

`C2` — which cavity is "the site" when more than one clears the acceptance gate — is registered
⚠ **CONTESTED** in [the roadmap §3b.2](../manuscripts/nr4a3-program-map.md): the prespecified 10-residue
site **splits across two real cavities**, and
[`r3-site-choice-audit.json`](./r3-site-choice-audit.json) already measured what an alternative ordering
would do to the paralogue margins — **but at POOLED granularity only**, while the verdict under test is a
**replicate-granularity** rule. Nothing had ever evaluated the replicate rule under the alternative
ordering.

It can be, at $0, because [`pocket-accepted-candidates.json`](./pocket-accepted-candidates.json) records
*every* cavity that cleared the frozen gate for all 300 committed frames — precisely so an ordering
question is arithmetic on a committed artifact instead of a new fpocket run. Re-reading the replicate
counts from it (and re-deriving them frame by frame as a check):

**under the alternative ordering the mandatory-axis separation collapses to a tie — margin exactly 0.00 —
and the exact test leaves its floor.** See
`per_paralogue.NR4A1.sensitivity_to_the_contested_C2_rule`.

⛔ **This is a SENSITIVITY, not a rule change and not a proposed rule.** The frozen rule remains the rule,
exactly as `r3-site-choice-audit.json` and `pocket_accepted_candidates.most_druggable` both insist. What it
establishes is that **the word SEPARATED is conditional on a choice the program has itself marked
contested**, and therefore may not be written unqualified.

## 4 · So: is the lead live?

**LIVE, and demoted — see `verdict.lead_status`.** Precisely:

- ✅ **The asymmetry is real and it should be reported.** The pooled verdict is driven by one paralogue,
  that paralogue is the best-effort one, and reporting a single string on the mandatory axis's behalf is
  the defect `RT-ASYMMETRIC` names. Splitting the verdict adds no data, changes no number and loosens no
  rule.
- ⛔ **The word SEPARATED may not travel alone.** It sits at the design's evidence ceiling (it cannot be
  stronger at this n), it does not survive family-wise adjustment over the two comparisons, its
  design-effect-corrected pooled intervals overlap, and it does not survive the contested `C2` ordering.
  Any sentence carrying it carries those four qualifiers or it is an over-claim.
- The honest one-line form is: **the mandatory axis is where the discrimination is, the best-effort axis is
  where the overlap is, and the mandatory result is at the ceiling of what three replicates can show.**

## 5 · Claim ceilings — inherited unchanged

Re-emitted verbatim in the JSON's `_ceilings_inherited`, and they bind every sentence above:

- **Not `ΔG_open`.** A detection fraction is not an opening penalty and must never be reported as one.
  `R6` is untouched and no free-energy statement is licensed. *(This is also the property that makes the
  reading worth having: [`path-family-synthesis.md`](../manuscripts/path-family-synthesis.md) records that
  the routes which genuinely reduce the selectivity requirement do so by leaving the free-energy axis, and
  this discriminator has no free energy in it.)*
- **Not evidence of absence, and never an exclusion.** At these ensemble sizes this supports a
  conformational-selection **ranking** only. Nothing here excludes NR4A1.
- **A paralogue row of 0 means "NR4A3's site did not open here"**, never "this protein has no druggable
  cavity" — the site is NR4A3's Pocket-5 mapped by alignment.
- **Conditional, as every `≥ D*` fraction in this program is** — on `C1` (D\*), `C2` (⚠ contested), `C3`,
  `C4`, `C5`. §3.1 is what that conditionality costs on this specific claim.
- Nothing about binding, reactivity, degradation, selectivity in vivo, efficacy or safety.

## 6 · Live documents that state the symmetric reading

Recorded, **not edited** — every one of these is outside this pass's write scope:

| document | what it says | why it is now misleading |
|---|---|---|
| [`paralogue-pocket-contrast.json`](./paralogue-pocket-contrast.json) → `map_edits_required` | the pooled verdict, and three proposed roadmap edits that would each carry it into the map | landed record, correct as generated. Its §8 Route A edit **has not been applied** to the map (verified: the Route A heading line is unchanged), so the pooled string is not yet in the roadmap — the cheapest possible moment to split it |
| [`path-family-synthesis.md`](../manuscripts/path-family-synthesis.md) → row `L4` | the ranking with all three species' counts in one row | states the ranking symmetrically; the mandatory/best-effort split is invisible in it |
| [`path-family-synthesis.md`](../manuscripts/path-family-synthesis.md) → row `C3` | *"Both support the ranking"* | true of the ordering, and it is the sentence that flattens the two axes into one |
| [`nr4a3-program-map.md`](../manuscripts/nr4a3-program-map.md) §6a, the CONFORMATIONAL-SELECTION row | scopes the categorical claim dead and keeps the ranking alive, treating the paralogues jointly | the ✕ rests on **detection**, which genuinely is symmetric — so this row is **correct as written**. It is listed only so a future editor does not "fix" it |

⛔ **`RT-ASYMMETRIC`'s route record makes a symmetric restatement a defect, and these are where one would
re-enter.** The roadmap edit that closes it is described — not applied — in the JSON's
`map_edits_required`, targeting **§8 Route A**.

---

*Produced by [`paralogue_pocket_asymmetric_read.py`](./paralogue_pocket_asymmetric_read.py). It imports no
compute, no network and no detector — `test_it_runs_no_compute_no_fpocket_and_names_no_gpu_path` fails the
build if that ever changes.*
