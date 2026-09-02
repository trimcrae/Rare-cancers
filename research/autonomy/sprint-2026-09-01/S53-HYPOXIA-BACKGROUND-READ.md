---
id: DOC-SPRINT-S53-HYPOXIA-BACKGROUND-READ
title: "S53-HYPOXIA-BACKGROUND-READ — the one-series hypoxia/PPARγ separation does not survive the only read whose null is a background, and the claim it supports is in systems/graph, not in any manuscript"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Adjudicate AUT-PD-185 for route RT-SGK1 and publication PUB-KINASE-LEADS: verify every figure the row
  asserts against the committed artifacts rather than the row, decide which of the three background reads
  a referee would accept and argue it, locate the text that states the separation claim, and write the
  replacement text out in full. Proposes; applies nothing.
scope: >
  research/modalities/emc-expression-panels.json (background_reads), research/modalities/ndrg1-panel-attribution.json,
  research/modalities/ndrg1_panel_attribution.py, the RT-SGK1 evidence row in systems/graph/routes.json and the
  ART-NDRG1-PANEL-ATTRIBUTION note in systems/graph/artifacts.json, at HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138.
  Edits no graph file, no manuscript, no ledger and no artifact.
last_verified: 2026-09-02
---

# S53 — does the published hypoxia/PPARγ separation survive its own background read?

**Item:** `AUT-PD-185` (`research/autonomy/research-ledger.json`, `state: queued`, `cost_class: free`,
score 133.6, `serves.route: RT-SGK1`, `serves.publication: PUB-KINASE-LEADS`).
**Owned paths:** this file. Nothing else was written; no `git` write command was run.
**Baseline:** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`. `git status --porcelain`
is empty for `research/modalities/emc-expression-panels.json`,
`research/modalities/ndrg1-panel-attribution.json`, `research/modalities/ndrg1_panel_attribution.py`,
`systems/graph/artifacts.json` and `systems/graph/routes.json` — every figure below is read from the
committed tree, and no concurrent seat's uncommitted edit is under this adjudication.

## ⭐ THE ANSWER, UP FRONT

**The claim does not survive.** Under the only one of the three reads whose null is drawn from the array
rather than from a convenience pool, the series that carries the published finding — **GSE24369** —
does not separate the two programme families, and it leans the **wrong way**: two of six hypoxia panels
clear their null against three of six PPARγ panels. The published read's separation is a **selection
effect in the panel membership**, and the artifact has been carrying the measurement of that selection
on its own face — `within_panel_percentile` — since 2026-08-29.

⛔ **The GSE24369 separation is REFUTED as stated; the route-level "NDRG1's elevation is hypoxia-shaped"
is WEAKENED to nothing rather than refuted; and NOTHING here establishes a PPARγ attribution.** The three
are different verdicts and §6 separates them. ⚠ The evidence on either side is **twelve panel-versus-null
comparisons per series**, six per family, on 35 and 16 samples, uncorrected — a small number of
comparisons whichever way it points.

⭐ **What it costs is small, because the claim never reached a manuscript.** `grep -ric ndrg1
research/manuscripts/` returns **no file with a single occurrence** — the separation claim exists only in
`systems/graph/` and in the artifact itself. `PUB-KINASE-LEADS` is `"state": "outlined"` in
`systems/graph/publications.json:287` and is named nowhere in
`research/autonomy/publication-authority.json`. **Nothing has left the building.**

## 1 · EVERY FIGURE THE ROW ASSERTS, RE-READ FROM THE ARTIFACTS

⭐ **The row's `curated_only` numbers are not a probe result at all — they are the committed artifact**,
so they were checkable without running anything. `research/modalities/ndrg1-panel-attribution.json`,
`series[...]`:

| field | GSE24369 | GSE4303 | row says | verdict |
|---|---|---|---|---|
| `n_samples` | 35 | 16 | (n=35 / n=16 in the graph note) | ✅ |
| `readable_pool` | **463** | **417** | pool 463 / 417 | ✅ |
| `n_hypoxia_scored` / `n_hypoxia_above_null_p95` | 6 / **6** | 6 / **1** | hypoxia 6/6; 1/6 | ✅ |
| `n_pparg_scored` / `n_pparg_above_null_p95` | 6 / **0** | 6 / **1** | PPARγ 0/6; 1/6 | ✅ |
| `separates_hypoxia_from_pparg` | **true** | **false** | separates; does not | ✅ |
| `null_median_range` | [-0.0105, 0.0155] | [0.2529, 0.4191] | "+0.25 to +0.42" (graph note) | ✅ |

⚠ **One panel is unscored in both series and the "of 6" hides it.** `pparg_consensus_encode_chea` carries
`"scored": false, "why": "the signature set was never RETRIEVED"`. So the PPARγ family has **seven**
named panels and six scored ones, and every `x/6` below is out of the six that could be scored. The
hypoxia family has six named and six scored. That is a fetch failure, not a biological absence, and the
artifact says so in those words.

### 1.1 The `background_reads` block, read from `emc-expression-panels.json`

`research/modalities/emc-expression-panels.json`, `background_reads[<matrix>]`:

| key | GSE24369_series_matrix.txt.gz | GSE4303-GPL3290_series_matrix.txt.gz | row says | verdict |
|---|---|---|---|---|
| `platform` | GPL6244 | GPL3290 | — | — |
| `n_frame` | **18697** | **14928** | 18697 / 14928 | ✅ |
| `n_requested` | 3000 | 3000 | — | — |
| `n_drawn` | **3000** | **3000** | 3000 each | ✅ |
| `n_drawn_also_wanted` | **338** | **411** | 338 / 411 | ✅ |
| `seed` | `20260829:GSE24369_series_matrix.txt.gz` | `20260829:GSE4303-GPL3290_series_matrix.txt.gz` | — | — |
| `len(z)` / `len(gsms)` | 3000 / 42 | 3000 / 16 | — | — |

`MIN_BACKGROUND_OUTSIDE_PANELS = 0.5` — `research/modalities/ndrg1_panel_attribution.py:120`. ✅ The row's
floor is the pinned constant.

⚠ **ONE FIGURE IN THE ROW IS LOW, AND IT IS LOW IN THE SAFE DIRECTION.** The row writes *"about 87% of
drawn genes fall OUTSIDE the panels and the curated roster"*, which is `1 - n_drawn_also_wanted/n_drawn`
= 88.7% and 86.3%. **That is the producer's self-report, not the guard's computation.** Re-running the
consumer guard's own arithmetic from `ndrg1_panel_attribution.py:400-406` — `inside = panel_members |
set(cache)`, `frac_outside = len(outside)/len(bg)` — gives **91.1%** (2,733 of 3,000) on GSE24369 and
**89.6%** (2,689 of 3,000) on GSE4303. Both pass the 0.5 floor with room; the row understates the margin
by ~3 points because it read the producer field instead of the guard. ⛔ CLAUDE.md §4: the two fields
answer different questions and `n_drawn_also_wanted` is exactly the kind of producer self-report
AUT-PD-178 established cannot be trusted on its own. **The guard's number is the one to quote.**

### 1.2 ⭐ THE POOL COMPOSITIONS, MEASURED — THIS IS THE WHOLE ARGUMENT IN ONE TABLE

Computed in-process at HEAD over the committed `emc-expression-panels.json`, using the module's own
`family_of`, `sample_z`, `signature_member_z` and `background_z`. "panel members" = every gene in
`signature_scores[p].per_platform[m].genes_readable` for a hypoxia- or PPARγ-family panel; "outside" is
the guard's `inside = panel_members | set(cache)`.

| read | null pool drawn from | n | panel members | PPARγ members | outside panels+roster |
|---|---|---|---|---|---|
| `curated_only` (GSE24369) | the 479-gene curated roster | 463 | 126 (**27.2%**) | 69 (14.9%) | **0 (0.0%)** |
| `curated_plus_signature_members` (GSE24369) | roster ∪ signature sets | 2 283 | 1 403 (**61.5%**) | 983 (**43.1%**) | 543 (23.8%) |
| `full_membership_background_null` (GSE24369) | random sample of the array | 3 000 | 206 (**6.9%**) | 157 (5.2%) | **2 733 (91.1%)** |
| `curated_only` (GSE4303) | the 479-gene curated roster | 417 | 122 (29.3%) | 66 (15.8%) | **0 (0.0%)** |
| `curated_plus_signature_members` (GSE4303) | roster ∪ signature sets | 2 034 | 1 265 (62.2%) | 874 (43.0%) | 474 (23.3%) |
| `full_membership_background_null` (GSE4303) | random sample of the array | 3 000 | 237 (7.9%) | 174 (5.8%) | **2 689 (89.6%)** |

⭐ **The 61.5% / 43.1% figures in the RT-SGK1 evidence row reproduce exactly**
(`systems/graph/routes.json:6403`, *"its null pool is then 61.5% panel members and 43.1% PPARγ
members"*). That row's number is correct and independently re-derived here.

⭐ **And the array background lands exactly where the module predicted it should.**
`ndrg1_panel_attribution.py:118` — *"A real array background overlaps the panels by roughly the panels'
share of the transcriptome — order 10%"*. Measured: **6.9% and 7.9%**. The two convenience pools sit at
27–29% and 61–62%. ⛔ **That is not a matter of taste between three defensible reads. Two of the three
pools are majority- or plurality-composed of the hypothesis under test; one is not.**

## 2 · WHICH READ IS RIGHT, AND WHY A REFEREE WOULD ACCEPT ONLY ONE

★ **`full_membership_background_null` is the only admissible read, and the repository argued this in
its own code before this seat looked at it.** The argument is not that the alternatives disagree; it is
that each of the alternatives has a named, measured defect that the disagreeing read does not have.

**(a) `curated_only` — what is published — inflates the hypoxia side by selecting its members.** The
panels are scored not over their published membership but over `curated ∩ published`: 9 to 41 genes out
of published sets of 44 to 231 (`ndrg1_panel_attribution.py:28-34`). The roster was assembled for six
unrelated targeted EMC reads, so the intersection has no reason to be a fair sample — and on the series
carrying the finding it is not. From `ndrg1-panel-attribution.json`, `within_panel_percentile` on
GSE24369, with each panel's own `rho_over_full_panel` beside the subset's `rho`:

| panel | family | k / readable | subset rho | rho over FULL panel | within-panel percentile |
|---|---|---|---|---|---|
| `hypoxia_gobp_response` | hypoxia | 22 / 72 | 0.7445 | **0.2353** | **100.0** |
| `hypoxia_elvidge` | hypoxia | 19 / 158 | 0.6796 | **0.2625** | **97.4** |
| `hypoxia_harris` | hypoxia | 24 / 80 | 0.6588 | 0.5692 | 89.6 |
| `hypoxia_buffa` | hypoxia | 10 / 48 | 0.6361 | **0.4246** | 86.6 |
| `hypoxia_winter` | hypoxia | 41 / 231 | 0.4941 | 0.3866 | 76.6 |
| `hypoxia_hallmark` | hypoxia | 36 / 188 | 0.4782 | 0.4423 | 72.8 |
| `adipogenesis_process_proxy` | pparg | 10 / 189 | 0.3563 | **0.6246** | 52.4 |
| `pparg_chip_chea` | pparg | 18 / 188 | 0.3490 | **0.5308** | 46.0 |
| `pparg_curated_trrust` | pparg | 15 / 63 | 0.0081 | **0.5613** | **4.6** |
| `pparg_perturbation_OE_UP` | pparg | 16 / 250 | 0.2104 | -0.0269 | 75.2 |
| `pparg_perturbation_KO_DOWN` | pparg | 13 / 188 | 0.2258 | -0.0398 | 83.2 |
| `pparg_perturbation_KO_UP_CONTROL` | pparg | 19 / 231 | 0.1006 | 0.0263 | 54.4 |

⛔⛔ **READ THE THIRD AND FOURTH COLUMNS TOGETHER: THE CURATED SUBSET BEATS ITS OWN PANEL ON ALL SIX
HYPOXIA PANELS AND LOSES TO IT ON ALL THREE PPARγ TARGET SETS.** `hypoxia_gobp_response` scores 0.7445
from 22 members while its full 72-member panel scores **0.2353**; `pparg_curated_trrust` scores 0.0081
from 15 members while its full 63-member panel scores **0.5613**, at the **4.6th** percentile of its own
panel. ★ The three PPARγ **target** sets score 0.53–0.62 over their full membership against the hypoxia
panels' 0.24–0.57 — **the direction of the published separation inverts when each panel is asked to
speak for itself.** (The three PPARγ *perturbation* sets sit near zero over full membership; they are
KO/OE-derived rather than target sets.)

⚠ **`rho_over_full_panel` is a diagnostic, not a graded statistic** — it is not compared against any
null and carries no p-value. It is quoted here only for direction and for the subset-versus-panel
comparison, which is what it is for.

⛔ **And the size-matched null provably cannot repair this**, for a structural reason the module states
at `ndrg1_panel_attribution.py:71-79`: the null *"draws random genes from a POOL, never random members
from the PANEL, so a non-random choice of members passes straight through it."* A referee shown a
signature scored over a curated 19-of-158 subset that sits at the 97th percentile of its own signature
would ask for the full signature. There is no reading of `curated_only` in which the answer is a
property of the hypoxia programme rather than of the roster.

**(b) `curated_plus_signature_members` fixes the membership and breaks the null.** Scoring full
membership is the right membership — but the null's pool then becomes the scored pool, which §1.2
measures at **61.5% panel members and 43.1% PPARγ members**. A "random panel" drawn from that pool is
a diluted mixture of the two hypotheses, not a background, so the bar the panels are judged against
moves with the hypothesis. ⚠ AUT-PD-167 measured that the resulting shift is a **pool** effect and not a
panel-size one — *"swept over k = 10…231 the null median is flat within each pool and differs between
them at every k"* (`ndrg1_panel_attribution.py:88-90`). **This read is not the answer either; it is the
second confound.**

**(c) `full_membership_background_null` has neither defect, and it is the read AUT-PD-170 was opened to
build.** Panels scored over full readable membership — the published signature, not the roster's slice
of it — and the null drawn from a random, unfiltered sample of the symbols the platform's probes resolve
to. `ndrg1_panel_attribution.py:99-104`: *"THE ONLY ONE WHOSE NULL IS A BACKGROUND … a random sample of
the ARRAY, not from a curated roster and not from the union of the signature sets."* Its pool is 6.9%
and 7.9% panel members, which is the transcriptome share the module's own tuning note predicts, and
91.1% / 89.6% of it lies outside the panels and the roster.

⭐ **This is the read this repository committed itself to in advance, before the answer was known**, and
the commitment is enforceable rather than rhetorical: selecting it without a `background_reads` block is
a hard `SystemExit` (`ndrg1_panel_attribution.py:387-395`), and a background contained in the panels is
refused by the `MIN_BACKGROUND_OUTSIDE_PANELS` guard (`:406-413`) — a guard written after AUT-PD-178
caught this repository publishing a fabricated background of its own. ⛔ **Preferring `curated_only` now
would be preferring the read that keeps the finding, which both AUT-PD-167 and AUT-PD-170 name in
advance as the failure mode** (`AUT-PD-170`: *"Do not prefer the read that keeps the finding: AUT-PD-167
exists because preferring a read is how the current state was reached."*).

⚠ **`systems/POLICY-evidence.md` does not govern this.** It binds clinical study pooling — Wilson
intervals, denominator weighting, primary-versus-secondary provenance — and carries no rule about
expression nulls or background pools (`grep -n "null\|background" systems/POLICY-evidence.md` returns
only denominator- and stance-related lines). The governing text is the module's own `_method` block and
the two guard test files, which is where this repository puts arguments of this kind.

## 3 · THE THREE READS, RE-COMPUTED

Re-run in-process at HEAD `b4cf28c6be` over the committed `emc-expression-panels.json`, with
`MEMBERSHIP_SOURCE` monkeypatched to each of the three values in turn, `SEED = 20260829`,
`N_DRAWS = 2000`, `--check` semantics (nothing written, no artifact regenerated, no test touched).

| read | series | n | null pool | hypoxia above p95 | PPARγ above p95 | `separates` | null median range |
|---|---|---|---|---|---|---|---|
| `curated_only` | GSE24369 | 35 | 463 | **6 / 6** | **0 / 6** | **true** | [-0.0105, 0.0155] |
| `curated_only` | GSE4303 | 16 | 417 | 1 / 6 | 1 / 6 | false | [0.2529, 0.4191] |
| `curated_plus_signature_members` | GSE24369 | 35 | 2 283 | **2 / 6** | **3 / 6** | false | [0.0947, 0.1301] |
| `curated_plus_signature_members` | GSE4303 | 16 | 2 033 | 5 / 6 | 2 / 6 | false | [0.1706, 0.2735] |
| `full_membership_background_null` | GSE24369 | 35 | 3 000 | **2 / 6** | **3 / 6** | false | [0.0139, 0.0539] |
| `full_membership_background_null` | GSE4303 | 16 | 2 995 | **5 / 6** | **0 / 6** | false | [0.2029, 0.3882] |

✅ **Every count, every pool size and every headline the row asserts reproduces exactly** — 6/6 and 0/6,
1/6 and 1/6, 2/6 and 3/6 twice, 5/6 with 2/6 and 5/6 with 0/6, pools 463 / 417 / 2 283 / 2 033 / 3 000 /
2 995. The row's headline arithmetic — **1 of 2 published, 0 of 2 under each alternative** — is correct.
The only figure that disagrees is the ~87% of §1.1, and it disagrees conservatively.

⭐ **The two alternatives agree on the headline from differently-composed pools** (23.8% versus 91.1%
outside the panels), which is the strongest thing that can be said for the negative: the removal of the
separation is not an artefact of one particular replacement pool.

### 3.1 ⛔ WHAT THE ADMISSIBLE READ ACTUALLY SHOWS, PANEL BY PANEL — AND IT IS NOT A NULL

`full_membership_background_null`, every scored panel, `rho` against its own size-matched null:

**GSE24369 (n=35) — the series that carried the published finding, and it leans the OTHER WAY:**

| panel | family | k | rho | null p95 | above | `p_empirical` |
|---|---|---|---|---|---|---|
| `adipogenesis_process_proxy` | pparg | 189 | **0.6246** | 0.3983 | ✅ | **0.0015** |
| `hypoxia_harris` | hypoxia | 80 | 0.5692 | 0.4445 | ✅ | 0.0090 |
| `pparg_curated_trrust` | pparg | 63 | **0.5613** | 0.4515 | ✅ | 0.0140 |
| `pparg_chip_chea` | pparg | 188 | **0.5308** | 0.4109 | ✅ | 0.0125 |
| `hypoxia_hallmark` | hypoxia | 188 | 0.4423 | 0.4109 | ✅ | 0.0370 |
| `hypoxia_buffa` | hypoxia | 48 | 0.4246 | 0.4543 | ✗ | 0.0660 |
| `hypoxia_winter` | hypoxia | 231 | 0.3866 | 0.3978 | ✗ | 0.0560 |
| `hypoxia_elvidge` | hypoxia | 158 | 0.2625 | 0.4269 | ✗ | 0.1989 |
| `hypoxia_gobp_response` | hypoxia | 72 | 0.2353 | 0.4308 | ✗ | 0.2139 |
| `pparg_perturbation_KO_UP_CONTROL` | pparg | 231 | 0.0263 | 0.3978 | ✗ | 0.5217 |
| `pparg_perturbation_OE_UP` | pparg | 250 | -0.0269 | 0.4039 | ✗ | 0.6072 |
| `pparg_perturbation_KO_DOWN` | pparg | 188 | -0.0398 | 0.4109 | ✗ | 0.6377 |

★ **All three PPARγ TARGET sets clear; three of six hypoxia panels do not, and the strongest single
association in the series is the adipogenesis proxy.** The three PPARγ rows that fail are the
perturbation-derived sets (KO_DOWN, KO_UP_CONTROL, OE_UP), which sit at rho ≈ 0 — they are
KO/OE-response sets, not target sets, and one of them is named a control.

**GSE4303 (n=16) — the cleanest hypoxia-leaning pattern any read produces, and it fails only on a joint
criterion:**

| panel | family | k | rho | null p95 | above | `p_empirical` |
|---|---|---|---|---|---|---|
| `hypoxia_elvidge` | hypoxia | 149 | **0.8794** | 0.7059 | ✅ | **0.0010** |
| `hypoxia_gobp_response` | hypoxia | 66 | 0.8147 | 0.6912 | ✅ | 0.0055 |
| `hypoxia_hallmark` | hypoxia | 174 | 0.7647 | 0.7147 | ✅ | 0.0225 |
| `hypoxia_winter` | hypoxia | 219 | 0.7471 | 0.7147 | ✅ | 0.0315 |
| `hypoxia_harris` | hypoxia | 73 | 0.7029 | 0.6647 | ✅ | 0.0340 |
| `pparg_chip_chea` | pparg | 169 | 0.6647 | 0.7118 | ✗ | 0.0895 |
| `pparg_curated_trrust` | pparg | 57 | 0.6471 | 0.6765 | ✗ | 0.0720 |
| `hypoxia_buffa` | hypoxia | 44 | 0.5941 | 0.6588 | ✗ | 0.0880 |
| `adipogenesis_process_proxy` | pparg | 176 | 0.5412 | 0.7147 | ✗ | 0.2124 |
| `pparg_perturbation_KO_DOWN` | pparg | 157 | 0.4176 | 0.7118 | ✗ | 0.3878 |
| `pparg_perturbation_OE_UP` | pparg | 230 | 0.2324 | 0.7147 | ✗ | 0.6837 |
| `pparg_perturbation_KO_UP_CONTROL` | pparg | 195 | -0.4235 | 0.7206 | ✗ | 0.9940 |

⛔ **`separates` is FALSE here on ONE panel — `hypoxia_buffa` at `p_empirical` 0.0880 — because the
criterion requires EVERY scored hypoxia panel to clear.** `_separates_means` in the artifact states that
in its own words. **A near-miss on a strict joint criterion is a different fact from a null and must not
be reported as one.**

⛔⛔ **AND THIS IS THE FINDING THAT MATTERS MOST: THE TWO SERIES POINT IN OPPOSITE DIRECTIONS UNDER THE
ADMISSIBLE READ.** GSE24369 (n=35) leans PPARγ 3/6 over hypoxia 2/6; GSE4303 (n=16) leans hypoxia 5/6
over PPARγ 0/6. That is not a weak replication — it is a **contradiction between the two series**, and
neither direction can be reported as this repository's reading of NDRG1's elevation.

### 3.2 ⚠ HOW MANY COMPARISONS UNDERLIE EACH FRACTION, AND WHAT MULTIPLICITY DOES TO THEM

Each `x / 6` is **six panel-versus-null comparisons**, twelve per series across both families, and none
of the three reads applies any multiplicity correction across those twelve — `p_empirical` is the raw
empirical tail from 2 000 draws, floored at 1/2001 = 0.0005. ⚠ At a Bonferroni-corrected 0.05/12 =
0.00417, **exactly one panel clears in each series**: `adipogenesis_process_proxy` (PPARγ, p 0.0015) on
GSE24369 and `hypoxia_elvidge` (hypoxia, p 0.0010) on GSE4303 — again in opposite directions. ⛔ This is
arithmetic on the committed `p_empirical` values, **not** a new procedure and **not** a claim that either
survivor is a finding; it is stated so nobody reads `3/6` as three independent confirmations.

## 4 · WHERE THE CLAIM IS STATED, AND THE TEXT THAT SHOULD REPLACE IT

⭐⭐ **IT IS NOT IN A MANUSCRIPT.** `grep -ric "ndrg1" research/manuscripts/` returns **zero files with a
non-zero count**; `grep -rn "NDRG1" research/manuscripts/` returns nothing. No manuscript, SI, cover
letter or checklist in this repository mentions NDRG1 at all, let alone the separation. **The claim lives
in exactly two hand-written places in `systems/graph/`, plus the generated view that renders them and the
artifact and test that pin the number.**

### 4.1 ⛔ SITE 1 — `systems/graph/artifacts.json:533`, the `ART-NDRG1-PANEL-ATTRIBUTION` note

**The overclaiming clause, quoted exactly:**

> ⭐ ONE OF THE TWO SERIES SEPARATES THE PROGRAMMES, NOT BOTH, and it must never be written as a
> replication: in GSE24369 (n=35) all six hypoxia panels exceed their own size-matched random null and
> none of the six PPARγ panels do; in GSE4303 (n=16) a RANDOM size-matched panel already reaches rho
> +0.25 to +0.42, so that series cannot discriminate at all.

⛔ **What is wrong with it is not its hedge — the hedge is good.** It is that the sentence reports the
6/6-and-0/6 as a property of the data when it is a property of the roster, and it does not say that the
read producing it has been superseded by one this repository committed to in advance.

**PROPOSED REPLACEMENT for that clause (paste in place of the quoted text, leaving the rest of the note
as it stands):**

> ⛔⛔ THE ONE-SERIES SEPARATION DID NOT SURVIVE ITS OWN BACKGROUND READ AND IS WITHDRAWN AS A FINDING
> (AUT-PD-185, measured 2026-09-02 at b4cf28c6be over the committed `background_reads` block). Under
> `curated_only` — the read pinned when this note was written — GSE24369 (n=35) put all six hypoxia
> panels above their own size-matched null and none of the six scored PPARγ panels, and GSE4303 (n=16)
> separated nothing. ⭐ THAT SEPARATION IS A SELECTION EFFECT IN THE PANEL MEMBERSHIP, NOT A PROPERTY OF
> THE PROGRAMMES: the curated subset beats its own full panel on all six hypoxia panels and loses to it
> on all three PPARγ target sets — `hypoxia_gobp_response` scores 0.7445 from 22 of 72 members while the
> full 72 score 0.2353, `pparg_curated_trrust` scores 0.0081 from 15 of 63 while the full 63 score
> 0.5613 — and the size-matched null cannot absorb that, because it draws from a POOL and never from the
> PANEL. ⭐ SCORED OVER FULL PUBLISHED MEMBERSHIP AGAINST A NULL DRAWN FROM A RANDOM SAMPLE OF THE ARRAY
> (`full_membership_background_null`, the only read here whose null pool is 6.9%/7.9% panel members
> rather than 27%/62%), NEITHER SERIES SEPARATES, AND THE TWO POINT OPPOSITE WAYS: GSE24369 puts 3 of 6
> PPARγ panels above their null against 2 of 6 hypoxia, and GSE4303 puts 5 of 6 hypoxia above against 0
> of 6 PPARγ, failing the joint criterion on `hypoxia_buffa` alone (p_empirical 0.0880). ⛔ A NEAR-MISS
> ON A STRICT JOINT CRITERION IS NOT A NULL, AND A CONTRADICTION BETWEEN TWO SERIES IS NOT A WEAK
> REPLICATION — this artifact now supports NO directional attribution of NDRG1's elevation to either
> programme. ⚠ Each fraction is six panel-versus-null comparisons on 35 and 16 samples with no
> multiplicity correction; at 0.05/12 exactly one panel clears per series, in opposite directions.

### 4.2 ⛔ SITE 2 — `systems/graph/routes.json:6403`, the RT-SGK1 `supporting_evidence` entry

**The claim clause, quoted exactly** (`"ref": "ART-NDRG1-PANEL-ATTRIBUTION"`,
`"what_it_supports"`, `"strength": "direct"`):

> ⛔ NOT A CONFIRMED FINDING — the read that would confirm or refute it has not been taken (AUT-PD-167,
> measured 2026-08-29; AUT-PD-169 is the read). In the LARGER of the two series (GSE24369, n=35) NDRG1's
> per-sample level tracks all six hypoxia programme proxies above their own size-matched random nulls,
> and none of the six PPARγ/adipogenic proxies

⚠ **This row was already honest about its own status** — it says NOT A CONFIRMED FINDING, it names the
selection effect, and it says widening reverses the reading. ⛔ **Two things in it are now false:** the
read HAS been taken, and `"strength": "direct"` no longer describes an artifact that supports no
direction.

**PROPOSED REPLACEMENT for the whole `what_it_supports` string:**

> ⛔⛔ REFUTED AS A DIRECTIONAL FINDING, 2026-09-02 (AUT-PD-185). The read AUT-PD-167 said would settle
> this has been taken: full published membership scored against a null drawn from a random sample of the
> array (`background_reads`, 3 000 symbols per platform, 91.1%/89.6% of them outside the panels and the
> curated roster, against a floor of 50%). ⭐ UNDER IT NEITHER SERIES SEPARATES THE PROGRAMMES AND THE
> TWO POINT OPPOSITE WAYS: in GSE24369 (n=35) 3 of 6 scored PPARγ panels clear their own size-matched
> null against 2 of 6 hypoxia panels, the strongest single association in the series being the
> adipogenesis proxy (rho 0.6246, p_empirical 0.0015); in GSE4303 (n=16) 5 of 6 hypoxia panels clear
> against 0 of 6 PPARγ, missing the joint criterion on `hypoxia_buffa` alone (rho 0.5941 against a null
> p95 of 0.6588). ⛔ THE COMMITTED 6-of-6 / 0-of-6 SEPARATION IN GSE24369 IS A SELECTION EFFECT IN THE
> MEMBERSHIP, NOT A PROGRAMME EFFECT: every hypoxia panel's curated subset outscores its own full panel
> and every PPARγ target set's subset underscores its own, one at the 100th and one at the 4.6th
> within-panel percentile. ⚠ THIS IS A WITHDRAWAL, NOT A PPARγ FINDING — six comparisons per family per
> series, uncorrected, on 35 and 16 samples, and the two series contradict each other. NDRG1's elevation
> in EMC is attributed to NEITHER programme by this artifact. ⚠ Superseded, retained: "In the LARGER of
> the two series (GSE24369, n=35) NDRG1's per-sample level tracks all six hypoxia programme proxies above
> their own size-matched random nulls, and none of the six PPARγ/adipogenic proxies."

⛔ **And `"strength": "direct"` should become `"strength": "against"`** if that value is in the schema's
enum for `supporting_evidence` — **UNMEASURED, I did not read the schema.** If it is not, the honest
minimum is to leave the strength alone and let the withdrawn text carry the verdict.

### 4.3 The three downstream sites that follow mechanically, and are NOT this seat's to touch

1. `systems/views/L2-rt-sgk1.md:59` — **GENERATED** from `routes.json`. It re-renders when site 2 changes;
   hand-editing it fails the build (CLAUDE.md §7).
2. `research/modalities/ndrg1-panel-attribution.json` — carries
   `separates_hypoxia_from_pparg: true` for GSE24369 and the `_what_this_does_not_settle` preamble.
   Changing it means moving `MEMBERSHIP_SOURCE` at `ndrg1_panel_attribution.py:95` and regenerating,
   **which is AUT-PD-170's recorded act, not this memo's.**
3. `research/modalities/tests/test_ndrg1_panel_attribution_controls.py:69-70` —
   `test_the_verdict_reports_one_series_not_two` asserts `separates_hypoxia_from_pparg is True` for the
   larger series. ⛔ **It must not be relaxed by whoever adopts this memo's conclusion without the
   regeneration**: AUT-PD-170 states the anti-gaming condition verbatim — *"moving them without the
   measurement is not"* permitted. **This memo IS that measurement**, and it is recorded here so the
   move can be argued from numbers in a commit message rather than from a preference.

## 5 · WHAT IT COSTS, AND WHETHER ANYTHING HAS LEFT THE BUILDING

★ **Nothing has left the building.** Checked, not assumed:

- `systems/graph/publications.json:287` — `"id": "PUB-KINASE-LEADS"`, **`"state": "outlined"`**,
  `"target_venue": "preprint"`, `"unit": "full_paper"`. Not drafted, not submitted, not posted.
- `research/autonomy/publication-authority.json` — `grep -n "PUB-KINASE-LEADS"` returns **nothing**. The
  only paper named in that file is `PUB-ASO` (in `scope.excluded_papers`, on Qeios with a DOI). No post,
  version or submission of `PUB-KINASE-LEADS` is recorded anywhere.
- The claim appears in **no manuscript** (§4). The only public surface it has ever had is the repository
  itself, and CLAUDE.md §6 records that this repository has exactly one reader.

⭐ **So the remedy is an edit, not a correction against an identifier somebody may have cited.** The
correction costs one graph edit, one regeneration and one test move — and it is caught before the paper
was written rather than after.

⛔ **What it costs the paper is real but small, and it is not `PUB-KINASE-LEADS`'s headline.** That
publication's `what_it_would_claim` (`publications.json:289`) is *"Four kinase-directed observations
specific to this disease exist in the published and curated record … and none has been followed up"* —
a claim about the **record**, not about NDRG1's programme attribution. The SGK1 lead's grade
(`systems/views/L2-rt-sgk1.md:23`) is already **◐ DISCORDANT ON THE KINASE, CONCORDANT ON ITS
SUBSTRATE**, and already says the substrate reading is transcript abundance and not attributable to SGK1
activity. ★ **The hypoxia attribution was the "positive half" offered in place of that negative
(`ndrg1_panel_attribution.py:4-10`), and losing it returns RT-SGK1 to the negative AUT-062 and AUT-PD-099
established — it does not create a new one.** The paper's four-lead structure is untouched.

⚠ **The one thing that genuinely gets worse:** `emc-hypoxia-confounds.json` is cited at
`L2-rt-sgk1.md:23` as *"an alternative explanation for the number that needs no kinase"* — the hypoxia
co-elevation story. This memo does not touch that artifact and did not read it. **Whether the alternative
explanation still stands is UNMEASURED here**, and it is a separate question from panel attribution: the
co-elevation reading is a group-level comparison, not a per-sample correlation against a null.

## 6 · IS IT A WEAKENING, A REFUTATION, OR NEITHER?

★ **Both, in different places, and the distinction is not pedantry:**

- **The GSE24369 separation is REFUTED as stated.** Not "does not replicate", not "is unconfirmed" — the
  read that produced it is inadmissible for a named, measured reason, and under the admissible read the
  same series gives the opposite lean. ⛔ **Say it plainly and do not soften it into an ambiguity.**
- **The route-level claim — that NDRG1's elevation in EMC is hypoxia-shaped — is WEAKENED to nothing,
  not refuted.** GSE4303 gives 5 of 6 hypoxia panels above their null with 0 of 6 PPARγ, which is a
  hypoxia-leaning pattern the data genuinely contains. It fails a strict joint criterion on one panel.
- **Nothing here establishes a PPARγ attribution.** The GSE24369 PPARγ 3/6 rests on the same twelve
  uncorrected comparisons, contradicts the other series, and comes entirely from the three target sets
  while the three perturbation sets sit at rho ≈ 0. ⛔ **Trading one direction for the other would repeat
  exactly the error this memo documents.**

## 7 · UNMEASURED

**Five things this memo did not measure, counted so nobody reads silence as a null:**

1. **Whether `"strength": "against"` is in the `supporting_evidence` schema enum** (§4.2). Did not read
   `systems/graph/*.schema.json`. Would be settled by one `grep`.
2. **Whether `emc-hypoxia-confounds.json` still supports the co-elevation alternative** (§5). Not
   opened. It is a different reading with a different design and is not implicated by this result.
3. **Whether regenerating the artifact under `full_membership_background_null` reproduces this probe
   byte-for-byte.** The probe was in-process with `MEMBERSHIP_SOURCE` monkeypatched; it wrote nothing.
   The seeded design says it should, but **that is a prediction, not a measurement** — it is AUT-PD-170's
   act to take.
4. **`pparg_consensus_encode_chea`.** Never retrieved on either platform, so the PPARγ family is six
   scored panels out of seven named, under every read. A fetch failure, not a biological absence.
5. **Whether either series' samples are EMC.** These are "EMC-containing" series; this memo inherited
   that framing from the artifact and did not re-verify sample-level histology.

## 8 · WHAT THIS SEAT DID AND DID NOT DO

- **Wrote:** this file only. No `git` write command was run. Nothing under `research/manuscripts/`,
  nothing under `systems/`, and not `research/autonomy/research-ledger.json`.
- **Ran:** read-only in-process `build()` calls with `MEMBERSHIP_SOURCE` monkeypatched, plus pool-
  composition arithmetic, both over the committed `emc-expression-panels.json` at HEAD. No artifact
  regenerated, no test relaxed, no pin moved, no fetch dispatched.
- **Proposes:** the two replacement strings in §4.1 and §4.2, ready to paste.
