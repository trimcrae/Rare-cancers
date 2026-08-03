# C02-L — the decoy null re-measured over a scope that contains C397 (`C24`)

> **$0 CPU/CI. No GPU, no rental.** Nothing here is a claim about binding, reactivity, adduct formation,
> degradation, selectivity in vivo, efficacy, safety, a therapeutic window or clinical readiness.
>
> **★ ONE FACT, ONE PLACE.** The design and every number live in
> [`categorical-decoy-null-lbd-plan.json`](./categorical-decoy-null-lbd-plan.json) (the pre-registration and
> the selected pairs, committed **before** any statistic under it existed) and
> [`categorical-decoy-null-lbd.json`](./categorical-decoy-null-lbd.json) (results), produced by
> [`categorical_decoy_null.py`](./categorical_decoy_null.py) `--scope lbd`. The **first** run keeps its own
> home in [`categorical-decoy-null.json`](./categorical-decoy-null.json) and
> [its own page](./categorical-decoy-null.md). The committed NR4A3 figures both of these calibrate keep
> theirs in [`nr4a-paralogue-dynamics.json`](./nr4a-paralogue-dynamics.json) → `categorical_verdict`.
> This file carries reasoning and points at those; it is not a second home for any figure.

---

## 1 · The gap this exists to close, stated exactly

The first cross-system decoy null ([`C02`](./categorical-decoy-null.md)) did what it was built to do: it gave
the categorical covalent screen a **measured** background instead of an unmeasured one, which is the shape
whose absence had already cost the program `V20`.

⛔ **But its NR4A3 arm never scored C397.** The pre-registered domain trim (`C16` — largest contiguous
pLDDT ≥ 70 run, minimum 120 residues) keeps UniProt **427–570** of the NR4A3 AlphaFold model, and of the
committed unique set `{397, 420, 559}` only **559** falls inside it. So the percentile that run reports is a
real measurement **of a different residue's question**, and the residue the entire covalent route rests on
had no measured background at all. The run says this itself, in
`results.⛔_nr4a3_harness_scope`, and the roadmap carries it as
[§3.4 fact 4](../manuscripts/nr4a3-program-map.md) and configuration item `C16`.

## 2 · Why the fix is a SECOND scope and not a wider one

⛔ **`C16` is not relaxed, edited, re-reduced or superseded by anything on this page.** Widening a
pre-registered window *after* seeing which residue fell outside it is exactly the outcome-tuning a
pre-registration exists to prevent — the first run refuses it in its own artifact, and that refusal was
correct. The honest repair, which the roadmap named as `Q2`, is a **separate test with its own
pre-registered scope**.

So there are now two runs, two plan files, two shard directories, two result files, and:

> **⛔ THE ROWS ARE NEVER POOLED, AND NEITHER RUN SUPERSEDES THE OTHER.** A percentile from either always
> names which scope produced it. The CI artifact names, the download patterns and the concurrency group are
> all keyed on the scope precisely so that a merge cannot happen by accident — pooling two backgrounds into
> one is the worst failure this lane can have and would be a silent one.

⚠ **And the thing that cannot be undone is stated rather than hidden.** `C16`'s result was known when this
scope was designed. Pretending otherwise would be worse than saying it. Three mitigations, all structural:

1. the scope rule is stated entirely in terms of **what the scope is for** and references no collision
   statistic, no percentile and no decoy's answer;
2. **every other pre-registered constant is held byte-identical** — gate, lengths, exposure cutoff, identity
   band, coverage floor, ranking rule, orientations, pocket rule, gradeability floor, placement budget, pose
   count and seed. A unit test asserts it
   (`test_the_lbd_scope_holds_every_other_preregistered_constant_identical_to_C16`). Exactly one variable
   moves, plus one stated budget change;
3. the design was **committed to git before any statistic under it existed**, and the CI job that samples
   placements refuses to start unless the trim it just produced actually contains C397 — while asserting the
   *opposite* for `C16`, so the check cannot pass by being vacuous.

## 3 · `C24` — the reference-anchored LBD window

**What the scope is FOR.** The categorical screen is a screen over the **ligand-binding domain**. Everything
it does happens there: the E3 placements are built around a cavity of the LBD, the frozen site definition
`C5` is an LBD lining set (NR4A3 Pocket-5) mapped onto each structure by alignment, and every cysteine the
screen adjudicates — the committed unique set and every paralogue cysteine they are compared against — is an
LBD cysteine. A scope for this screen is therefore **the LBD, taken as the same structural region in every
protein.** That is a statement about what the instrument is pointed at.

| decision | rule |
|---|---|
| **reference** | the **committed NR4A3 LBD construct** — `results/nr4a3-matrix/nr4a3-opened.pdb`, the same model the committed categorical verdict was computed on. Its UniProt span is DERIVED from the file at run time, never typed |
| **procedure** | for every protein, NR4A3 and decoys alike: **Smith-Waterman local** alignment of the AlphaFold model's sequence to the reference, same BLOSUM62 matrix and same affine gaps (−11 / −1) as the frozen `nw_align`; the window is the residue-number **span** of the model residues aligned to a reference position |
| **why local** | the query is a full-length chain and the reference is one domain. A **global** aligner pays end-gap penalties proportional to the query's length — 919 residues for AR against a 254-residue reference — which is the wrong instrument for *"find this domain inside this protein"* |
| **refusals** | reference coverage < **0.60**, or window < **120** residues. ⭑ Both numbers are **borrowed, not invented**: the coverage floor is the pair-formation coverage floor `C16` already uses, and the length floor is `C16`'s own `MIN_DOMAIN_LEN` |
| **confidence** | ⭑ **none applied.** pLDDT is *reported* per window (mean, min, max, fraction ≥ 70) as an observable so a reader can see exactly what `C16` would have removed — and it decides nothing |

### 3.1 · The defect it repairs is NOT C397 — C397 is the symptom

A **confidence** criterion is not a **structural** one. pLDDT is a per-model property, so "largest contiguous
pLDDT ≥ 70 run" returns a *different region of the fold* in every protein, and a background pooled over those
windows is pooling regions rather than measuring one. That is visible in `C16`'s **own plan file**, which
contains no statistic of any kind — see `window_size_spread` in each plan, and the `trimmed` block for the
per-protein windows. Window size drives how many cysteines the screen can even see, so it is a confound on
the background independent of which residues survive.

### 3.2 · ⚠ How well that worked, measured — and it is a partial success, not a clean one

**This is the honest reading and it belongs here rather than in a footnote.** `C24` achieves its *primary*
requirement decisively: NR4A3's window is the whole reference LBD and all three committed unique cysteines,
C397 included, are in scope (`⛔_nr4a3_scope_check`). Its *secondary* claim — a better-matched region across
proteins — is only **partially** achieved: compare `window_size_spread` between the two plan files. The
reason is measurable and worth stating: outside the NR4A subfamily, identity to the NR4A3 LBD reference sits
in the **low-twenties to low-thirties percent** (`trimmed[*].scope_alignment.identity_to_reference`, whose
one home is the plan file), i.e. in the alignment twilight zone, so the local alignment is partial for
distant receptors and the window inherits that. ⭑ NR4A1 and NR4A2 are the exception and align nearly
completely, which is what makes the NR4A3 reference rows the best-covered in the run.

⛔ **AND THE COVERAGE FLOOR DOES REAL, KNIFE-EDGE WORK.** Read `trim_refusals`: every refusal under `C24` is
a coverage refusal, and several sit within a few thousandths of the 0.60 floor. **PPARA is one of them** —
and PPARA supplied two of `C16`'s graded rows, including its highest-collision one. Two consequences, both
binding:

- the two scopes' pair sets are **not** nested in each other (`selected_pairs` in each plan). Most of `C16`'s
  pairs survive; the PPARA pairs do not, and `C24` adds pairs built from receptors `C16` refused outright;
- ⛔ **the floor is NOT moved to rescue PPARA.** Changing a pre-registered threshold once you can see which
  pair it removed is the same defect as widening `C16` to admit C397. It stays where it was registered, the
  exclusion is reported, and if a third scope is ever wanted it gets its own pre-registration.

⚠ **A registered limit for any future scope, recorded now:** a coverage floor tuned for domain-vs-domain
alignment between close paralogues is doing different work when applied to a full-length chain against a
single domain at ~28 % identity. That is a real weakness of `C24` and it is stated as one.

## 4 · What is NEW in the readout: a cysteine-level background

`C16` reported **one conditional per ordered pair**, pooled over that target's unique cysteines. A pooled row
answers *"does this PAIR collide?"* — it cannot give **one residue** a percentile, and C397's percentile is
the deliverable. So `C24` also computes, for decoys and NR4A3 alike and under the same gradeability floor,
the conditional **per individual target-unique cysteine**, conditioned on the placements that reach that
cysteine. Both are reported; the row-level number is computed under the identical rule `C16` used so the two
designs can be compared.

⚠ **Two non-independences bound what the cysteine-level percentile means, and the artifact carries both:**
cysteines within one target share a placement set, so background points are **clustered by target** and the
effective *n* is below `n_graded` (`n_distinct_targets_contributing` is the honest lower bound); and both
orientations of every pair are present by design, so a protein appears as target and as paralogue. Neither is
a defect — both make the background *less* independent than *n* suggests, which should make a reader more
cautious, not less. A percentile's resolution is `1/n_graded` and is printed beside every percentile.

## 5 · Comparability — the check that had to pass first

> **A background measured on one structure source, against a target measured on another, is not a
> background.**

**8XTT — the experimental NR4A3 NMR ensemble — is REFUSED for the NR4A3 arm, deliberately.** It is the
obvious candidate: it is what the committed NR4A3 numbers use and it has no pLDDT problem at all. But the
decoys have no experimental structures. An NMR-ensemble target against AlphaFold-model decoys would differ in
structure source, in conformer count and in whether hydrogens are present, and no percentile from it would be
interpretable. The choice was therefore between changing the **target's structure source** and changing the
**trim** — and only the trim can be changed for *both* arms at once. So the trim is what changed.

⚠ **The price, stated plainly: the NR4A3 row here is an ALPHAFOLD-MODEL row.** It is not the committed
opened-model row and it is not an 8XTT row. It calibrates the **screen**, under one identical rule, on one
identical structure source. It is **not** a re-derivation of the committed C397-led verdict, which keeps its
own home and is quoted, never recomputed.

## 6 · How to read the result

Every number lives in [`categorical-decoy-null-lbd.json`](./categorical-decoy-null-lbd.json) and is not
restated here (rule 1):

| read this | where |
|---|---|
| ⛔ **which NR4A3 unique cysteines this scope could see** — the check that licenses a C397 percentile at all | `results.⛔_nr4a3_harness_scope` |
| ★ **the cysteine-level background** — one point per (ordered decoy × target-unique cysteine) | `results.★_cysteine_level_background_at_gate_12` |
| ★ **C397's own percentile against it**, with its resolution | `results.★_nr4a3_per_cysteine_vs_that_background` |
| the row-level decoy distribution, reach-only **and** exposure-filtered | `results.background_at_gate_12` |
| NR4A3 row-level under the identical rule `C16` used | `results.nr4a3_harness_matched` |
| how often a close paralogue pair even **has** a target-unique cysteine, re-derived under this scope | `results.precondition_has_a_target_unique_cysteine` |
| **what changed versus the first null** | `results.comparison_to_the_other_scope` |
| the driver's reproduction of the committed static verdict | `harness_known_answer_check` |
| the verdict, its rule, and the roadmap edits it requires | `map_edits_required` |

**⛔ THE REACH-ONLY COLUMN IS THE LOAD-BEARING ONE.** The exposure-filtered column is adjudicated by `C7`
(`EXPOSED_RSA = 0.25`), which is registered ⛔ **KNOWN-DEFECTIVE**: it fails its own positive control —
NR4A1 **C551**, the one NR4A-family covalent site with literature support, reads RSA **0.165** and clears the
cutoff in **no frame of any scope**. Both columns are reported and neither is chosen on its answer, but a
statement that rests on the exposure filter inherits a demonstrated false negative.

## 7 · What a favourable result licenses — and what it does not

**It licenses exactly one sentence:** that the categorical **screen** fires on NR4A3 more rarely-by-chance
than on an arbitrary close human paralogue pair — over the LBD, at the 12-atom gate (`C8`), under the reach
convention `C9`, on AlphaFold models, inside a **nuclear-receptor** universe.

**⛔ It does NOT license:**

- no statement about binding, affinity or any free energy — none is computed anywhere in this run;
- no statement about reactivity, thiol pKa, nucleophilicity, adduct formation or adduct stability — reach
  and exposure are **necessary, not sufficient**, for the decoys exactly as for NR4A3;
- nothing about degradation, nothing about efficacy, nothing about safety, and never a therapeutic window
  or clinical readiness — no such quantity is modelled here;
- no claim of **proteome-wide** selectivity of any kind. This is a nuclear-receptor background and it does
  not bound the rate over the proteome;
- that a linker exists. **Linker length and exit vector remain conditional on the docked-pose-derived
  anchors**, i.e. on `R5`. ⭑ Cysteine **uniqueness** and paralogue **burial** are pose-independent — the
  split the categorical audit established, and the reason this test was not blocked behind the second
  pose-method work.

## 8 · Configuration this rests on

Per [§3b](../manuscripts/nr4a3-program-map.md)'s declaration rule, every conditional figure names the frozen
choices it depends on. This run's are:

| id | what it fixes | status |
|---|---|---|
| **`C24`** | **this scope** — the reference-anchored LBD window (new; registered by this run) | ✅ frozen |
| `C8` | the 12-backbone-atom design gate | ✅ frozen |
| `C9` | the reach convention | ⚠ **CONTESTED** — two frozen conventions that disagree |
| `C7` | `EXPOSED_RSA = 0.25` | ⛔ **KNOWN-DEFECTIVE** — fails its own positive control; the reach-only column is the load-bearing one for that reason |
| `C16` | `C02`'s domain trim — **not used here, not changed here** | ⚠ CONTESTED (its own row) |

⛔ **None of `C7`, `C8`, `C9` or `C16` is altered by this run.** They are cited, not edited.
