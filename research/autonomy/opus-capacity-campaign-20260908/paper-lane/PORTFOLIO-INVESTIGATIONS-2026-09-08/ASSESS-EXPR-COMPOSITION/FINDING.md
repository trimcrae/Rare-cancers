---
id: DOC-PORTFOLIO-ASSESS-EXPR-COMPOSITION-2026-09-09
title: "ASSESS-EXPR-COMPOSITION — independent methods and evidence assessment of the composition-adjusted EMC expression contrast"
level: L4
kind: assessment
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-EXPR-COMPOSITION
assesses: EXPR-COMPOSITION
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# ASSESS-EXPR-COMPOSITION

Independent assessment of `../EXPR-COMPOSITION/` — the claim that adjusting for a frozen 20-marker
tumour-composition score attenuates the cross-platform EMC expression concordance from 0.6521 to
0.5668 on the primary frame (56.1 % of the excess over 0.5), the residual surviving at p = 0.022
against KINASE-2's unadjusted p ≤ 0.0005.

**No file outside this directory was written or modified.** Every re-run was done on copies in
`work/`; the lane's own captures are untouched (`../EXPR-COMPOSITION/` mtimes are unchanged and its
files are the committed ones at `fc606cef`). No `git add`/`commit`/`push`, no `preflight.sh`, no
subagent, no network, no GPU, no paid API. Assessment only: I did not extend the analysis, propose a
better adjustment, or run the two-covariate / MKI67 / EPCAM sensitivity analyses the lane declared
out of scope.

## Headline

**The result is substantially sound and the lane's own reporting is unusually careful.** The
preregistration freeze is corroborated by evidence outside the author's control; the known-answer
gate really gates; the headline numbers reproduce under an independent implementation; and a
specificity control the lane did *not* run comes out in the lane's favour. Four qualifications
matter, one of them a plain factual error:

* **A factual claim in `PREREGISTRATION.md` §2, repeated in `FINDING.md` §3, is false.** The 22
  markers are **not** readable with per-sample `z_vs_array` for all 16 GPL3290 samples: 6 of the 20
  primary markers (DCN, PTPRC, CD3E, CD8A, MS4A1, HLA-DRA) plus MKI67 are missing on 1–8 of them.
  On GPL3290 the NaN-skipping score `C` is therefore built from **16–20 markers depending on the
  sample**, and the count correlates +0.21 with the EMC label. Impact is small but not nil
  (checks/06, 07).
* **Roughly half of the attenuation is generic**, not composition-specific: sham 20-gene non-marker
  covariates matched on label correlation also attenuate. The marker score still attenuates
  significantly *beyond* them, but 0.561 over-attributes (checks/05).
* **The gate covers KINASE-2's Welch-t data path, not this lane's rank statistics** — nothing the
  headline is actually computed from is gated by it.
* **A frozen parameter was silently relaxed**: `N_PERM_COMP` 2000 (prereg) → 500 (run), disclosed as
  "500" but never as a deviation.

---

## 1 · Is the preregistration real? — **SUPPORTED-WITH-QUALIFICATION**

**The freeze claim itself is SUPPORTED, on evidence the author would have had to forge to fake.**

* **File order** (checks/01). The only lane artifact predating `PREREGISTRATION.md` (mtime
  `01:06:45Z`) is `checks/01-locator-sha256` (`01:05:19Z`), whose stdout contains **exactly** a
  commit hash, a UTC timestamp and four sha256 sums — **no numeric statistic of any kind**. The
  first statistic in the lane is the gate output at `01:09:01Z`, 2 min 16 s *after* the freeze.
* **The document has not been edited since.** `sha256(PREREGISTRATION.md)` =
  `6386ac16556214…1ec8ad`, which is byte-identical to the `PREREG_SHA` constant hard-coded in
  `composition_adjusted_contrast.py` (written `01:12:00Z`) and stamped into the published artifact.
  A post-hoc edit of the prereg would have broken that pin.
* **Nothing in the frozen document requires having seen a result.** The seed (20260909), the frame
  sizes (431 / 413), the arm sizes and the lead list are all readable from KINASE-2's committed
  artifact; the marker list is canonical cell-type biology; §2's claim is explicitly presence-only.
  The prereg also commits to a null being as publishable (§6) and names the stop condition (§7).
* Corroboration in the other direction: the lane's own git history is a single commit
  (`fc606cef`, `01:16:20Z`) covering the whole lane, so **git provides no independent ordering** —
  the mtime chain and the sha pin are the evidence, and they agree.

**Qualification 1 — the pre-freeze probe's *content* is false as written.** §2 asserts all 22 markers
are readable "with per-sample `z_vs_array` for all 35 GPL6244 and all 16 GPL3290 labelled samples".
I checked (checks/06): true on GPL6244 (20/20 markers complete), **false on GPL3290** — DCN missing
on 8 of 16 samples, CD3E on 4, MS4A1 on 3, PTPRC on 2, CD8A / HLA-DRA / MKI67 on 1 each. This is the
one claim the author says was inspected before freezing, and it was inspected wrongly. Consequence
(checks/07): `C` on GPL3290 is a mean over a **sample-dependent marker set** (16–20 markers, count
correlated +0.21 with the label), i.e. the covariate is not a single fixed definition on that
platform. **Bounded**: recomputing `C` from only the 14 markers complete on GPL3290 gives
Spearman(C, label) = **−0.476** vs the reported −0.504, and correlates 0.918 with the published `C`,
so the substantive effect is small. The prereg sentence, and `FINDING.md` §3 which repeats it, are
nonetheless wrong and should be corrected.

**Qualification 2 — one frozen parameter was changed after the freeze, without disclosure.**
Prereg §3 freezes `N_PERM_COMP = 2000` composition permutations for the negative control. The
aborted run used 200 (`script-as-run.py`: `N_PERM_COMP = 2000` in the constant but 200 reported in
stdout), the published run 500 (`N_PERM_COMP_NC = 500`). `FINDING.md` reports "500 permuted
composition scores" but nowhere says the prereg said 2000. The direction is *against* the lane's own
interest (less power for its control) and the observed value sits ~5.9 sd outside the null, so
nothing substantive turns on it — but an undisclosed departure from a frozen count is exactly what a
preregistration exists to make visible. The other declared-but-unrun items (two-covariate,
MKI67/EPCAM) **are** disclosed, in `FINDING.md` §6.

## 2 · Does the known-answer gate actually gate? — **SUPPORTED-WITH-QUALIFICATION**

**It gates, verifiably, and the count is honest.** I enumerated every comparison by instrumenting a
copy (checks/02): 102 labelled comparisons print, plus one unprinted `nchk` increment on the ALK
"must stay unplaceable" branch = **103**, matching the reported figure with no padding. I then ran
three independent one-field mutations of a *copy* of KINASE-2's artifact through the lane's
**unmodified** script (checks/03): perturbing `primary.concordance_rate` by 1.1e-3, `leads.RET.
min_abs_t` by 1e-2, and `secondary.n_concordant` by 1 each produced `GATE FAILED`, **exit 2**, and
**no adjustment artifact written**. The gate is real, the tolerances (0 for counts, 5e-5 for rates,
5e-6 for joint p) are tight, and it precedes everything.

**What it covers:** per-frame `n`, concordant count, concordance rate, cross-platform Pearson and
Spearman r, five min|t| quantiles and both arm sizes on both frames; and for each of 13 leads the
min|t|, direction concordance, and null-gene count + joint p on both frames.

**What it does NOT cover — and this is load-bearing.** Every one of those 103 comparisons is in
**KINASE-2's Welch-t path**. The gate therefore certifies *that this lane is reading the same data,
building the same frames and reproducing the same prior result* — a genuine and non-trivial thing —
but it touches **nothing** the headline is computed from:

* the rank machinery (`rankdata`, `spearman`, `partial_rank`) and the vectorised permutation core;
* the composition score `C` and its construction;
* the 434-gene paired set, the unadjusted **rank** rate 0.6521, the adjusted rate 0.5668, the
  attenuation ratio 0.561, and the adjusted label-permutation null and its p.

Note in particular that the gated primary concordance is **0.65197 on 431 genes, Welch t**
(checks/03 output) while the headline baseline is **0.6521 on 434 genes, Spearman** — two different
statistics that happen to agree to 3 decimals. `FINDING.md` §6 discloses the 431/434 difference and
says the gate "compares like with like", which is accurate; but §4 and the validation list present
"103 comparisons, 0 mismatches" as validation *of the headline*, and it is not. The lane's own
`checks/05` (vectorised core vs the plain per-gene formula, 5.6e-16) is an **internal consistency**
check, not a known answer.

I supplied the missing external check (checks/04): recomputing the whole headline with
`scipy.stats.spearmanr` and an OLS-residual rank partial correlation in place of the lane's
hand-rolled formulas gives Spearman(C, label) **−0.5780 / −0.5041 (exact match)**, cross-platform
Pearson **0.4046 → 0.2511 (exact match)**, and rates **0.6544 → 0.5691** (primary) vs the lane's
0.6521 → 0.5668 — a difference of **exactly one gene out of 434 in each rate** (and one of 413 on
the secondary frame), i.e. a single borderline sign decision. The lane's implementation is
independently confirmed. But because 0.561 is a ratio of two small sign-count excesses, one
borderline gene moves it by ~0.01 (scipy's route gives 0.552). **The attenuation should be reported
as ≈ 0.56, not 0.5606.**

**The RNG-quantile exclusion is HONEST, not convenient.** KINASE-2's permutation quantiles depend on
its RNG call order, which is a property of code structure, not of data; a bit-exact match would
require re-implementing KINASE-2's call sequence, and pseudo-reproducing it would be worse than
excluding it. The scope note is stated in the artifact, not buried. **But** the excluded quantity
(p ≤ 0.0005) is one half of the headline comparison "≤ 0.0005 → 0.022", and a *distributional* gate
was available and unused: KINASE-2's unadjusted null is mean 0.499 sd 0.0374, this lane's adjusted
null mean 0.500 sd 0.0332 — consistent, and cheaply gateable within tolerance. Honest exclusion,
missing substitute.

## 3 · Is the negative control the right one? — **SUPPORTED-WITH-QUALIFICATION**

**What it establishes, exactly.** Shuffling `C` across samples while keeping the real labels
destroys the score's per-sample alignment with everything — labels, genes, composition. That 0 of
500 such draws reach 0.5668 (mean 0.6469, sd 0.0135) rules out precisely one thing: **the partial-
correlation machinery does not manufacture attenuation from a covariate carrying no per-sample
information.** That is a necessary control and it passes. The lane's artifact states this scope
correctly in its `_note_if_no_attenuation` field.

**What it does NOT rule out, and this is the gap.** A shuffled score also loses its **correlation
with the EMC label** (−0.578 / −0.504). So the control cannot separate "adjusting for *composition*
attenuates" from "adjusting for *anything that tracks the label* attenuates". Since a first-order
partial correlation with a covariate correlated −0.5 with the label removes a large shared component
of the label by construction, generic attenuation is the expected null here — and the lane's control
does not test against it. Nor does it address the question the lane's own limitations raise: whether
the marker score is a **proxy for something other than composition** (batch, series, fixation age,
platform-specific probe behaviour, or simply the comparator diagnosis mix).

**I ran the missing control** (checks/05). 300 sham covariates, each the mean background z of 20
randomly drawn **non-marker** genes in the primary frame, put through the lane's own machinery,
under a single no-leave-one-out convention applied to real and sham alike (which reproduces the
lane's published 0.6521 → 0.5668 exactly, so the LOO rule is not doing the work):

| covariate | Spearman with label (6244 / 3290) | adjusted primary rate |
|---|---|---|
| real `C` | −0.578 / −0.504 | **0.5668** |
| all 300 shams | median \|r\| 0.293 | mean 0.6253 (sd 0.0251, min 0.5392) |
| shams matched ±0.10 on both platforms (n=14) | ≈ C | mean 0.6256, **min 0.5829** |
| shams matched ±0.15 on both platforms (n=26) | ≈ C | mean 0.6197, **min 0.5737** |
| shams matched ±0.20 on both platforms (n=42) | ≈ C | mean 0.6170, min 0.5461 |

**Two readings, both real.** (i) *For the lane*: the marker score attenuates **more than any**
label-correlation-matched sham in the ±0.10 and ±0.15 bands (0 of 14, 0 of 26; one-sided p = 0.067
and 0.037). The attenuation is **not** a generic artefact of adjusting for a label-tracking
covariate — a stronger specificity statement than the lane's own control supports. (ii) *Against the
lane's arithmetic*: adjusted rate regresses on the covariate's mean |label r| with slope −0.073
(r = −0.40); at `C`'s label correlation the generic prediction is **0.6077**, against an observed
0.5668. On that decomposition roughly **half** of the 0.0853 drop is generic covariate shrinkage and
half is specific to the marker score — i.e. a composition-specific attenuation of the excess nearer
**0.27** than 0.561. **This does not touch the "proxy for something else" question**: a marker score
and a sham gene score are both bulk transcript averages, so anything that moves whole-transcriptome
levels between these two series (batch, fixation, comparator mix) is present in both arms of my
comparison. My own control's limitations run the same way: shams are drawn from the same frame whose
genes may themselves carry stromal signal, and from the background-`z` matrix rather than the
curated `z_vs_array` path `C` uses — both push shams toward attenuating, so the marker-specific
excess I report is a **lower** bound.

## 4 · Is the stated bound correct? — **SUPPORTED-WITH-QUALIFICATION**

The lane's argument: in a mesenchymal tumour the stromal programme is partly the tumour's own, so
adjusting for `C` removes real EMC biology as well as any confounding; therefore 0.561 is an
**upper bound** on the composition share and the surviving p values are **conservative**.

**The direction of that argument is right, and my sham result independently supports it** — a second
over-removal mechanism (generic shrinkage from any label-correlated covariate, ≈ half the drop)
inflates the measured attenuation the same way. A third, unmentioned, does too: with n = 16 on
GPL3290 and a covariate correlated −0.50 with the label, the partial correlation is unstable, and a
**sign**-based concordance statistic degrades toward 0.5 under added noise regardless of confounding
(the lane does report 48–95 direction flips).

**The qualification is that the bound is stated one word too strongly.** `FINDING.md` §6 says
"0.561 is an upper bound on **the composition share**". The omitted counter-term is in the bullet
immediately above it and is never reconciled with it: `C` is an acknowledged **noisy proxy** for
composition, and adjusting for a mismeasured confounder removes only part of the confounding
(residual confounding / regression dilution), which biases the measured share **down**. The two
biases run in opposite directions, so what is actually bounded above is **the share of the excess
concordance removable by this particular score** — not the true composition share, which could be
larger. By the same token the conservatism of p = 0.022 / 0.0085 is conditional: over-adjustment
makes it conservative, residual confounding makes it anti-conservative, and the lane cannot say
which dominates. Correct wording would be: *"0.56 is an upper bound on the share this score removes;
because the score is an imperfect proxy, it bounds neither the true composition share nor the
direction of error in the residual p."*

Two smaller points on the same paragraph: the reported precision (0.5606, 0.561) is not supportable
at that resolution (item 2 — one gene moves it by ~0.01); and after the sham correction the
defensible headline is "**about half of the drop, and roughly a quarter to a half of the excess over
0.5, is attributable to this score, of which an unknown part is composition**".

## 5 · What would falsify the result? — **SUPPORTED (a concrete falsifier exists; I ran it)**

**Primary falsifier — the label-correlation-matched sham-covariate test, executed above.**
It is fully specified, costs seconds on already-committed data, and has a pre-statable failure
condition: *if the primary-frame adjusted rate under `C` (0.5668) sits inside the bulk of the
distribution of adjusted rates produced by sham 20-gene non-marker covariates matched to `C`'s
label correlation on both platforms, then the attenuation is a generic consequence of adjusting for
anything that tracks the EMC label, and its attribution to composition is refuted.* Command:
`cd work && python3 sham_matched_control.py 300` (checks/05). **On the run recorded here the claim
survives** at the ±0.10 and ±0.15 bands (0/14, 0/26) — while showing that about half of the
attenuation is generic, which the headline number does not currently reflect. Re-running it with
more draws (the ±0.10 band has only 14 members, so p cannot go below 0.067) is the obvious
strengthening, and a marker-set-size-matched and normalisation-path-matched sham (draw shams from
the curated `z_vs_array` path rather than background `z`) would remove the two disanalogies I named.

**Secondary falsifier, also runnable now:** replace covariate adjustment with **stratification** —
restrict each platform to the samples in the overlapping range of `C` between arms and recompute the
raw (unadjusted) concordance there. Covariate adjustment on n = 16 with a covariate this correlated
with the label extrapolates over a region with little overlap; if the concordance excess survives
inside the overlap region, the composition reading is weakened, and if it disappears there while the
partial-correlation residual persists, the residual p = 0.022 is an extrapolation artefact. A third:
recompute `C` on GPL3290 from only the 14 fully observed markers (checks/07 shows label r moves
−0.504 → −0.476) and re-derive the headline; a large move would show the sample-varying marker set
is load-bearing.

---

## What I checked, and what I did not

**Checked** (all in `checks/`, one directory per attempt, every attempt preserved):

| check | what | exit |
|---|---|---|
| 01-freeze-order-and-prereg-hash | mtime ordering of all 27 lane files; prereg sha vs the `PREREG_SHA` pin; content of the only pre-freeze capture; prereg-vs-code parameter diff | 0 |
| 02-gate-coverage-enumeration | instrumented **copy** of the script; enumerated all 103 gate comparisons by name | 0 |
| 03-gate-mutation-test | 3 one-field mutations of a **copy** of KINASE-2's artifact through the unmodified script | 0 (each run exit 2, no artifact) |
| 04-scipy-independent-recompute | headline recomputed with `scipy.stats.spearmanr` + OLS-residual partial correlation | 0 |
| 05-label-correlation-matched-sham-control | 300 sham non-marker covariates, matched on label correlation | 0 |
| 06-marker-presence-claim | prereg §2's presence claim, all 22 markers × both platforms × all labelled samples | 0 (claim **FAILS**) |
| 07-marker-missingness-differential | per-sample marker count entering `C`, differential by arm; complete-markers-only sensitivity | 0 |

**Not checked / limitations of this assessment.**
* I did not re-run the lane's 2000-permutation adjusted null or its 500-draw negative control; I
  accepted `checks/04`'s captured stdout for those, having confirmed the surrounding machinery
  reproduces. p = 0.022 is consistent with 45/2001 and p = 0.0085 with 17/2001, as reported.
* I did not audit KINASE-2 itself; it is the gate target here, taken as given.
* I did not verify the upstream provenance of `emc-expression-panels.json` beyond its sha256
  matching `FOLLOWTHROUGH-DISCOVERY/proposals.json`, which the lane's `checks/01` already showed.
* My sham control shares two disanalogies with the real score (background-`z` vs curated
  `z_vs_array`; shams may carry stromal signal), both making its verdict conservative for the lane.
* Nothing here is a whole-paper review of any endpoint, and MF1 / P-ST / TCIP / FP were not touched.

## Recommended corrections (not applied — the lane's files are another writer's)

1. Correct `PREREGISTRATION.md` §2 and `FINDING.md` §3: the 22 markers are **not** complete on
   GPL3290; state the 6+1 incomplete markers, the 16–20 per-sample marker count, and the
   complete-markers-only sensitivity (−0.504 → −0.476).
2. Disclose the `N_PERM_COMP` 2000 → 500 deviation in `FINDING.md` as a departure from the freeze.
3. Report the attenuation as ≈ 0.56 (two significant figures), and add the sham result: about half
   the drop is generic to label-correlated covariates, so the composition-specific share is nearer
   0.27; the marker score nonetheless attenuates more than every matched sham.
4. Reword the bound to "an upper bound on the share this score removes", and say that proxy error
   pushes the other way so the residual p's conservatism is not established.
5. Reword validation item (1) so the 103-comparison gate is described as certifying the KINASE-2
   Welch-t data path and frame construction, not the rank statistics that carry the headline.

## Stop condition

**Met.** The five assessment questions are answered with recorded evidence, and the one runnable
falsifier I named has been executed. I did not extend the analysis, did not propose a better
adjustment, did not run the lane's out-of-scope sensitivity analyses, and wrote nothing outside this
directory. Remaining work belongs to the owner of `EXPR-COMPOSITION/`.

## Verdict summary

| # | question | verdict |
|---|---|---|
| 1 | Is the preregistration real? | **SUPPORTED-WITH-QUALIFICATION** — the freeze is corroborated by mtime order and the sha pin; §2's presence claim is factually wrong on GPL3290 and one frozen parameter was relaxed undisclosed |
| 2 | Does the known-answer gate actually gate? | **SUPPORTED-WITH-QUALIFICATION** — it gates (3/3 mutations exit 2) and 103 is honest, but it covers KINASE-2's Welch-t path only, not the rank statistics the headline is built from; the RNG exclusion is honest, its substitute missing |
| 3 | Is the negative control the right one? | **SUPPORTED-WITH-QUALIFICATION** — right control for the machinery, silent on label-correlation genericity and on non-composition proxies; the missing control, run here, favours the lane but halves the attributable share |
| 4 | Is the stated bound correct? | **SUPPORTED-WITH-QUALIFICATION** — direction right and independently supported, but it bounds the share *this score removes*, not the composition share; proxy error runs the other way |
| 5 | What would falsify the result? | **SUPPORTED** — matched-sham covariate test, specified and executed (checks/05); stratified-overlap and complete-markers-only recomputation named as further runnable falsifiers |
