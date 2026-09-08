# PROPOSALS AWAITING ROOT ADMISSION — next-work backlog

**Status: PROPOSALS ONLY. Nothing here is admitted, dispatched, claimed or started.**
Written by a proposal-only planner on branch `claude/confident-bardeen-ji76cd`, at repository
revision **`414e661c9fbeb3d726f34525379fd57934b26d79`**, 2026-09-08 ~18:44 UTC. The scientific root
adjudicates every item below before anything is dispatched.

## What this planner did and did not do

**Did:** read `CLAUDE.md`, `AGENTS.md`, `research/autonomy/OPERATING_PROTOCOL.md`; read
`systems/graph/publications.json` (33 endpoints), `routes.json` (83 routes), `lanes.json` (18 lanes);
read the standing backlog record `research/autonomy/research-ledger.json` (415 entries — 172 queued,
10 in progress, 30 parked) and enumerated every non-`process_defect` open row; read the campaign's
own `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `WAVE-LOG.md`, the four `BLOCKER*` records, the
`A1`/`A2` decisions, `SELECTION-S1-S3-independent-questions.md` with its appended dispositions, the
`S2` result, and the `W20c`–`W20f` probe reports; inspected the committed artifacts named in each
proposal below.

**Did not:** run any producer, test, gate, preflight or figure build; fetch any source; edit any
manuscript, artifact or graph file; open any in-flight worker directory or any `*-executed-artifacts/`
working file; reopen any hold. **No source fact, reproduction or result below is this planner's own.**
Every quantity in this document is quoted from a committed file or from a collected campaign report,
and is attributed where it is used.

## Honest supply statement — read this before the list

**I found FOUR items that are genuinely independent, genuinely unresolved, computational, and
executable from inputs this repository already holds.** Not four hundred, not twenty. I am not
padding to a target and I did not invent a question to fill a slot.

**What limits the supply, measured rather than asserted:**

1. **The paper board is drafted-out.** Of 33 endpoints, 26 are `drafted` or `posted_preprint`; of the
   7 that are not, six were dispatched as P1–P6 in this campaign and one (`PUB-PARKED-MODALITIES`) is
   blocked on capabilities nobody has. `A2` graded all 52 un-closed routes on three tests and
   **zero passed all three**; `A1` graded all 14 hypothesis candidates and **all 14 failed gate 1**.
   Neither result is mine and neither is re-derived here.
2. **The open backlog is overwhelmingly tooling.** Of the 212 open ledger rows, **106 are
   `process_defect`** and a further ~30 are recorded negatives. Fifteen `fetch` rows all name a
   network act. That leaves a single-digit number of rows that are science and are local.
3. **Almost everything local and decisive has already been computed.** The CALVADOS single-chain arm
   ran (`emc-condensate-calvados.json`, 55 runs, verdict `NO_SEPARATION`); the scheduling two-population
   model ran (`emc-scheduling-medians.json`); the EWSR1 probe endpoint ran and returned a null (W20e);
   the FET-IDR census was rekeyed per reported type (AUT-PD-208's `✅` half).
4. **The remaining high-value questions are network-gated, not thought-gated.** Four of the eleven
   blocked items below are one public HTTP GET away from being ready. That is where the supply
   actually is, and it is not this planner's to authorise.
5. **The campaign's own exclusions remove several otherwise-live questions** — HLA/coverage, the W25
   chromatin continuation, the P6 scope, mortality/biomarker/endpoint, ICD-O, ASO. Those are on the
   blocked list with the exclusion named, not reworded onto the ready list.

**Two of the four ready items (R1, R4) are cheap and fully offline. One (R3) is cheap and fully
offline. One (R2) is a real multi-CPU-hour compute job with an environment precondition.** If root
wants sustained parallel work beyond that, the honest lever is authorising the network dependencies in
the blocked list — chiefly **B1** (one public Ensembl FASTA), which alone unblocks three items.

---

# READY LIST — ranked

Ranked by **decision value to an existing eligible paper × certainty the inputs can answer it**.
Cost is not a ranking term.

---

## R1 · What a journal must print beneath a survival figure for it to be reconstructable — the risk-table density, extent and anchoring arm the digitization control never had

**Rank 1.** Serves `PUB-IPD-SURVIVAL` (P1: writable now; its headline finding is *about* reporting
practice). Methods contribution, reusable by any rare disease.

**1 · Exact inputs and revision.**
- `research/modalities/km_digitize.py` at `414e661c` — `run_control()` (`:1427`), the hard-coded
  `risk_times = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]` at `:1429`,
  `_cohort_to_figure_inputs()` (`:1287-1292`, which **already takes `risk_times` as an argument**),
  `SCENARIOS` (`:1309-1357`), `cohort_size_sensitivity()` (`:1379-1425`), `digitize_recipe()`
  (`:876-915`, which already implements the printed-vs-anchored first-row contrast).
- `research/modalities/km-digitization-error.json` — the committed control artifact.
- `research/modalities/emc_ipd_survival.py` — `MAX_KM_DEVIATION = 0.05` (`:187`),
  `REQUIRE_RISK_TABLE = True` (`:182`).
- `research/modalities/km-figure-readings.json` — `recipes[0]`, for the *shape* of a printed risk table.
- `research/modalities/tests/test_km_digitize.py:100-101`, `tests/test_emc_ipd_survival.py:47-105`.
- **No network, no new data, no real published curve.** Synthetic cohort only, ground truth known by
  construction.

**2 · What this repository already answers.** The control varies **rendering and pixel reading only**
— line width, gridlines, censor ticks, a CI band, a second curve, resample 0.6, Gaussian noise σ=8,
JPEG q60 and q30, dashing, annotation placement, a lenient-matcher arm, and a 1-px axis anchor error
— 16 scenarios, 12 read / 4 refused, `worst_max_abs_curve_error` 0.0636, off-step 0.0035 (quoted from
the artifact by S2, not re-derived here). `cohort_size_sensitivity` varies **n** (20/59/150/270).
P1 verified the control exists and reported its headline. **One risk table is passed to the truth
record, to the exact-coordinates baseline and to all 16 scenarios**, so density is sampled at exactly
one point. The artifact already shows the axis is live and load-bearing: at **zero coordinate error
anywhere**, `exact_coordinates_baseline` loses **7 of 59 censorings** (`censored_delta_vs_truth` −7)
purely because the table stops at 168 of `t_max` 180.

**3 · The unresolved question.** *How does reconstruction error depend on the density, extent and
first-row anchoring of the printed numbers-at-risk table — i.e. what would a journal have to print for
a survival figure to be reconstructable at a stated error bound?* Answerable, and refutable: if error
is flat across 2→19 printed rows at fixed render quality, the proposed requirement is **wrong** and
the honest output is "density does not bind; extent does" (or neither).

**4 · Deliverable.** A table of `events_delta_vs_truth`, `censored_delta_vs_truth`,
`median_delta_vs_truth` and `internal_max_abs_km_deviation` per cell, over rows ∈ {2, 3, 5, 8, 13, 19}
(spacing 180/90/45/24/15/10) × last-row extent ∈ {0.25, 0.5, 0.75, 0.933, 1.0}·`t_max`, plus a
`printed`-vs-`anchored` first-row contrast **on the synthetic cohort where truth is known** — which
`digitize_recipe()` today applies only to the real figure, where truth is not. Emitted into the
existing artifact as a new block, with the generator's `⛔_direction_of_the_bound` carried verbatim on
every row.

**5 · Validation — what would make the answer wrong.**
(a) **Reproduction gate:** the existing 8-row / 0.933-extent cell must reproduce the committed
`exact_coordinates_baseline` (`events_delta_vs_truth` 0, `censored_delta_vs_truth` −7,
`internal_max_abs_km_deviation` 0.0009) exactly. If it does not, the sweep is instrumented wrong and
nothing else is quoted. (b) **Confound control:** density is swept **only at the `clean` render**, or
it is not separable from the pixel-reading error the 16 scenarios already measure. (c) **Direction of
bound:** a synthetic render is easier than a journal figure, so every figure bounds reading error
**from below** — the result can refute a reporting standard and can never certify one, and any
sentence claiming otherwise is wrong. (d) **Monotonicity is a prediction, not an assumption:** a
non-monotone or flat curve refutes the requirement framing and must be reported as such.

**6 · Scope and stop.** Lift `risk_times` to a `run_control()` keyword and a per-scenario `SCENARIOS`
key; run the 6×5 grid plus the anchoring contrast; write the block; stop. **Stop conditions:** the grid
completes; or the reproduction gate (5a) fails, in which case the branch stops with the failure
recorded and no requirement stated. **Out of scope, explicitly:** any real published curve, any
patient-level reconstruction, any pooling, any application to a closed IPD/recurrence/RT gate, any
change to `MAX_KM_DEVIATION`, any edit to `emc_ipd_survival.py`.

**7 · Dependencies and exclusive ownership.** No dependency on any other proposed item. **Exclusive
writer of** `research/modalities/km_digitize.py`, `research/modalities/km-digitization-error.json`,
`research/modalities/tests/test_km_digitize.py`. **Reads but must not write**
`emc_ipd_survival.py`, `km-figure-readings.json`, `emc-ipd-survival.json`. Collides with nothing on
the ready list.

**8 · Rough size.** Small-to-medium. ~60–120 lines of change to one module; the grid is 30 cells plus
a contrast, each a clean render already costed by the existing scenarios; single session.

**9 · Why not a duplicate, not cosmetic, not a re-run.** S2 executed this question's *feasibility* and
terminated on its missing-input criterion, naming the dependency to file, line, parameter and sweep
range — its acceptance branch (b), a documented "the retained control cannot answer this". This item
is the successor S2 explicitly did **not** take because it had no write path. `rg 'risk_times'` returns
10 hits in 3 files; `rg` for risk-table density/spacing/granularity returns **0** (S2's measurement).
No consumer of the artifact varies the risk table. It is not cosmetic: it produces a new measured
dependency curve, not a receipt. It is not a producer re-run: the 16 existing scenarios are untouched
and the existing cell must reproduce byte-comparably as the gate.

---

## R2 · Is the condensate NO_SEPARATION verdict a result, or an artifact of unconverged sampling?

**Rank 2.** Serves `research/manuscripts/fusion-direct/fusion-condensate-disruption-paper.md` and the
partner-stratification claim behind `PUB-FUSION-PARTNER`. The highest-value item on this list by
decision value; ranked second only because it has a real compute cost and an environment precondition.

**1 · Exact inputs and revision.**
- `research/modalities/emc-condensate-calvados-prespecification.md` (immutable prereg, frozen
  2026-08-24, with Amendment 1) — §2 readout, §3 constructs, §6 gates, §10 exclusions.
- `research/modalities/emc_condensate_calvados.py` (56,611 B) — the frozen executable half:
  `build_constructs()`, the guards G1–G5, `NU_BROKEN_RANGE`, `NU_EXPECTED_RANGE`, the scorer.
- `research/modalities/emc-condensate-constructs.json` (13,419 B) — every construct sequence with its
  SHA-256; `emc-condensate-window-eligibility.json` (2,719 B); `emc-condensate-composition.json`.
- `research/modalities/emc-condensate-calvados.json` (128,930 B) — the 55 completed runs, their per-run
  protocol block, `nu`, `wall_seconds`, `trajectory_sha256`, and the pooled statistics.
- Protocol as actually run, quoted from run `C161_r1`: CALVADOS 2, 293.15 K, 0.19 M, pH 7.5, 150 nm
  box, 10 fs step, 7,000 steps/frame, 1,010 frames (7,070,000 steps), 10 frames discarded, CPU,
  4 threads, `calvados_version` 0.8.1 @ `c16f59a6`, OpenMM 8.4.0.post2, wall **3,392 s**.

**2 · What this repository already answers.** The single-chain arm **ran**. `pooled_replicate_sd_nu`
0.01913, `separation_threshold_nu` 0.05738, verdict **`NO_SEPARATION`**, four registered negatives
(`NEGATIVE_NO_STRATIFICATION`, `NEGATIVE_FET_NOT_SPECIAL`, `NEGATIVE_WILDTYPE_NOT_SEPARATED`,
`NEGATIVE_COMPOSITION_ONLY`). All three primary pairs are unseparated with exact permutation p of
0.865 / 0.286 / 0.532 over 252 arrangements, `holm_reject_at_0.05` false, and the tests are **not
powerless** (floor p 0.00794).

**3 · The unresolved question.** The same artifact records `convergence.converged` = **false**:
`n_exceeding_pooled_sd` **14 of 55** runs (`fraction_exceeding_pooled_sd` 0.2545,
`max_half_vs_full_delta` 0.0519) against the prereg's own 20 % rule — so **every ν in the panel is
PROVISIONAL by the prespecification's own terms**, and the negative rests on them. *Does the
`NO_SEPARATION` verdict survive when the sampling is extended until the prespecified convergence rule
is met — or does a primary pair separate, or a ν move outside `NU_EXPECTED_RANGE`, once the chains have
finished relaxing?* Amendment 1 records the mechanism that makes this a live worry rather than a
formality: the local shakeout on TAF15 1–161 read ν 0.337 whole-trajectory against 0.289 on the second
half, "a chain still collapsing out of its initial configuration".

**4 · Deliverable.** A convergence-extension arm at the same construct set, same seeds where the
protocol permits, with trajectory length (and/or discarded equilibration) increased until
`fraction_exceeding_pooled_sd` ≤ 0.20 or a stated ceiling is reached; the re-scored panel emitted
beside — never over — the committed one; and an **appended, dated, numbered amendment** to the
prespecification recording exactly what changed and why. Either "the negative hardens and is no longer
PROVISIONAL" or "the negative does not survive convergence" is a publishable result.

**5 · Validation — what would make the answer wrong.** (a) The **instrument construct is the control**:
`E264_E15` (15 % of positions → Glu) must remain strictly more expanded than `E264`; if it does not,
the extended run is not measuring what the prereg says it measures and nothing is quoted. (b) The
**composition nulls** (`E264_scr1..3`, `C264_scr1..3`) must still differ from their parents.
(c) `NU_BROKEN_RANGE` — any ν outside (0.15, 0.95) is `INSTRUMENT_FAILED`, not a finding.
(d) The **prereg is immutable**: no gate, threshold, criterion or registered direction may be changed
to reach a verdict; the scorer, `separation_threshold_nu` and the Holm family assignment stay as
frozen. (e) A verdict that *changes* must be reported as changing, with the old panel retained.

**6 · Scope and stop.** One arm: longer sampling on the frozen construct set. **Stop** when the
convergence rule is met and the panel is re-scored, or at a stated wall-clock/CPU ceiling with the
partial panel and the unmet rule reported honestly. **Out of scope, explicitly and per §10 of the
prereg:** the slab / phase-coexistence arm (GPU, real dollars, put to the user separately), the
CALVADOS 3 multi-domain reading of the full type-1 segment, Mpipi, and any statement about saturation
concentration, condensate formation, efficacy, selectivity, safety or clinical readiness.

**7 · Dependencies and exclusive ownership.** **Environment precondition to be checked at admission,
not assumed:** `calvados` is **not importable in this container** (`ModuleNotFoundError: No module
named 'calvados'`, checked by me). The recorded run environment (calvados 0.8.1, OpenMM 8.4.0.post2,
MDAnalysis 2.10.0, mdtraj 1.11.1) must be re-established — a pip install from `pypi.org`, which is in
this container's `no_proxy`, or the standing Actions-runner escape hatch. **Exclusive writer of**
`research/modalities/emc-condensate-calvados.json` (new sibling block or sibling artifact),
`emc_condensate_calvados.py`, and the amendment log at the foot of
`emc-condensate-calvados-prespecification.md`. Collides with nothing else on this list.

**8 · Rough size.** **Large.** 55 runs at 3,392–4,324 s wall each is ~55 CPU-hours at the current
trajectory length; a convergence extension is a multiple of that. This is the one item on the list that
needs a compute decision, and it should be routed accordingly rather than run opportunistically.

**9 · Why not a duplicate, not cosmetic, not a re-run.** It is not a re-run for receipts: the committed
panel's own convergence block says the panel is unconverged, so re-running at the *same* length would
reproduce the same PROVISIONAL label and settle nothing. It is not cosmetic — it decides whether four
registered negatives are results or artifacts. It duplicates no campaign report: no W-series or
P-series report touches this artifact, and `A1`/`A2` did not reach it. It is not the excluded W25
chromatin work, not NR4A-Perspective, not the GPU slab arm the prereg itself withholds.

---

## R3 · Can the fourth cohort's panel say anything at all about the four `EWSR1`-negative specimens?

**Rank 3.** Serves `PUB-FUSION-PARTNER` and `PUB-FUSION-OUTPUT`. Small, decisive, and the expected
answer is **no** — which is exactly why it is worth settling in writing.

**1 · Exact inputs and revision.**
- `research/modalities/emc-fourth-cohort-probe-counts.tsv` (18,810,774 B, 213,007 distinct sequences
  across 12 runs) and `research/modalities/emc-fourth-cohort-quant-inputs.json` (97,964 B).
- `research/modalities/emc_fourth_cohort_quant.py` — `phase_map()` (`:711-727`), `_write_probe_tsv()`
  (`:583`, `:586`), `map_probes_to_genes()` (`:447-456`).
- `research/modalities/nr4a3-exon-audit.json` — the NR4A3 exon → residue / cDNA map on the canonical
  transcript, both numbering schemes, with per-exon coding lengths.
- `research/modalities/emc-construct-inputs.json` — committed NR4A3 `cdna` / `cds` / `exons[]` spans
  (the same records W20c used to place the TAF15 probe to the nucleotide).
- `research/modalities/emc-fourth-cohort-quant.json` — `FISH_1` per-sample EWSR1 break-apart calls
  (EWSR1+ 8, EWSR1− 4).
- **Offline, stdlib, no network.**

**2 · What this repository already answers.** `emc_fusion_read_scan.py` **refuses** a targeted probe
deposit outright, on the ground that a fixed short amplicon inside one gene cannot span a junction —
so a zero read carries no information (recorded in ledger row `AUT-115-11f2347b-f050ad8a`). W20c placed
the TAF15 probe at cDNA 1617–1666 and fixed TAF15 exon 6's end at cDNA 570 by two independent routes.
W20d computed probe positions for every recoverable case and found EWSR1, TCF12 and TFG present in the
committed table. W20e ran the EWSR1 endpoint to a pre-specified **NULL**. W20f measured the k=12
intersection filter (1,645 of 213,007 offered; 99.23 % withheld) and reported an **NR4A3 candidate
sequence persisting in 9 of 12 runs**, labelled `UNVERIFIED` as to probe identity. **Nobody has asked
where that sequence sits relative to NR4A3's exon boundaries.**

**3 · The unresolved question.** *Does the measured probe set contain any sequence assigned to NR4A3,
and does any such sequence cross an NR4A3 exon–exon boundary — i.e. could this panel, in principle,
carry information about fusion status for the four `EWSR1`-negative EMC-labelled specimens?* Refutable
in both directions: a probe straddling the exon 2/3 or exon 3 boundary would mean the refusal is too
strong; no straddling probe means the refusal is confirmed at nucleotide resolution rather than by
argument.

**4 · Deliverable.** A short artifact recording, for every committed 50-mer that maps into NR4A3
cDNA/CDS (both strands, exact match, the method W20f used for its seven genes): its 1-based cDNA span,
the exon(s) it lies in, its distance to the nearest exon boundary, its per-run persistence k, and a
single verdict — **can / cannot** span a reported junction. Plus the consequent statement about the
four `EWSR1−` specimens.

**5 · Validation — what would make the answer wrong.** (a) **Positive control:** the method must
reproduce W20c's TAF15 placement exactly — probe at cDNA 1617–1666, inside exon 15, exon 6 ending at
570 — and W20d's FUS placement at cDNA 1158–1207. If it does not, the exon arithmetic is wrong and no
NR4A3 statement is made. (b) **Internal consistency:** the NR4A3 exon lengths must sum to `len(cdna)`,
the check W20c ran on TAF15 and passed. (c) **Probe identity stays `UNVERIFIED`:** recovering a
sequence into a transcript is an identification by exact match, **not** confirmation that the vendor
panel contains an NR4A3 probe; the vendor manifest remains an unrecovered source behind a recorded
egress denial, and no wording may imply otherwise. (d) **A zero read count is never reported as
evidence about a tumour** — the module's own `⛔ a_zero_in_the_probe_table` caveat and W20e's
persistence-cap handling bind here.

**6 · Scope and stop.** Enumerate, place, report the verdict, stop. **Out of scope:** re-running the
EWSR1 endpoint (answered NULL — re-testing on any re-derived panel is the post-hoc iteration W20d
refused and W20e forbade); any new statistical endpoint on this cohort; any read-count comparison
between the FISH arms; any change to `phase_map`'s threshold (that is B1, blocked).

**7 · Dependencies and exclusive ownership.** Independent of R1, R2, R4. **Exclusive writer of** one
new artifact under `research/modalities/` and its producer. **Reads but must not write**
`emc_fourth_cohort_quant.py` and every fourth-cohort artifact — **R3 and R4 must not both write
`emc_fourth_cohort_quant.py`; neither is proposed to.**

**8 · Rough size.** Small. One script, one artifact, one session.

**9 · Why not a duplicate, not cosmetic, not a re-run.** It is ledger row `AUT-115` — filed, queued,
never taken — and the exon-boundary half of it is asked by no W-series report: `rg -i exon` over
`reports/W20*.md` returns TAF15 and FUS placements only. It is not cosmetic: it settles whether a
committed refusal (`emc_fusion_read_scan.py`'s) is correct at nucleotide resolution, and it bears on
four specimens' partner assignment in a drafted paper. It is not a producer re-run: it reads the
committed TSV and computes something the pipeline never computed.

---

## R4 · How much of this cohort's panel-level statistics is manufactured by the zero-handling convention?

**Rank 4.** Serves `PUB-FUSION-OUTPUT`. A methods robustness measurement, offline, over committed data.

**1 · Exact inputs and revision.** `research/modalities/emc-fourth-cohort-probe-counts.tsv`,
`emc-fourth-cohort-gene-counts.tsv` (862 genes), `emc-fourth-cohort-quant.json` (the `FISH_1` 8/4
split: `EWSR1−` = SRR35940648, 654, 656, 657), `emc_fourth_cohort_quant.py` (`:767-773` `gene_counts`,
and the module's own `⛔ a_zero_in_the_probe_table` caveat), and the `support_floor_reads` per-run
persistence caps W20e used (13.4, 13.0 for SRR35940651/652). Offline, stdlib.

**2 · What this repository already answers.** W20e pre-specified and ran **three** zero-handlings for
**one** probe — A drop-as-below-persistence-cap (primary), B literal zeros, C impute at the run's cap
— and measured that they **flip δ's sign**, −0.4766 → +1.9651, and move the gene from the 23rd to the
**100th** panel percentile, while all three verdicts agree at NULL. W20e states plainly that the panel
percentile is "the rank of δ among all 862 panel genes' δ computed on the same runs" — i.e. **the
calibration itself is computed under one convention and has never been recomputed under the others.**

**3 · The unresolved question.** *Across all 862 panel genes, how many δ values are sign-unstable
between the three zero-handling conventions, and how far does the panel percentile — the calibration
every per-gene claim in this cohort is quoted against — move when the convention changes?* Refutable:
if the percentile of a named gene is stable to within its stated tolerance under all three, the
calibration is sound and the answer is a clean negative.

**4 · Deliverable.** A per-gene table of δ under A / B / C with a sign-stability flag, the count and
identity of sign-unstable genes, and the percentile shift for the genes actually quoted anywhere in
`research/manuscripts/fusion-output/` — plus one sentence stating whether any published per-gene
statement in this repository depends on the convention.

**5 · Validation — what would make the answer wrong.** (a) **Reproduction gate:** TAF15 δ −0.8347 and
FUS δ +0.0789, with panel percentiles 9.05 and 62.06 under the `i/n` convention, must reproduce
exactly — W20e's own gate, which it passed to every reported digit. If they do not, nothing else is
quoted. (b) The `i/n` vs `(i+0.5)/n` percentile convention gap is **documented and bounded at 0.10
absolute** (W20e); a shift smaller than that is not a finding. (c) **No new endpoint:** this measures
an instrument's convention sensitivity; it makes no claim about any gene's biology, and it must not be
read as a test of any hypothesis.

**6 · Scope and stop.** Compute, tabulate, report; stop. **Out of scope:** re-running the EWSR1 or
TAF15 endpoints; any hypothesis test; any change to the pipeline's default convention (a default
change is an owner act, and this item only measures what such a change would cost).

**7 · Dependencies and exclusive ownership.** Independent of R1 and R2. **Shares read-only inputs with
R3 and must not write any file R3 writes**; exclusive writer of one new artifact and its producer under
`research/modalities/`. Neither R3 nor R4 writes `emc_fourth_cohort_quant.py`.

**8 · Rough size.** Small-to-medium. One pass over an 18.8 MB TSV, three aggregations, one table.

**9 · Why not a duplicate, not cosmetic, not a re-run.** W20e measured this for **one** sequence and
explicitly framed the percentile as calibration rather than as a measurement it had checked; no report
extends it to the panel. It is not a record or manifest audit — it recomputes statistics from read
counts. It is not a re-run of a producer chain: the three conventions are not what the committed
pipeline emits.

---

# BLOCKED LIST — with the exact dependency named

Each row states the exact thing that is missing. **A missing input is UNKNOWN, not absent**, and
nothing here is a claim that the dependency is unreachable in principle.

| # | Question | Exact blocking dependency |
|---|---|---|
| **B1** | How many genes does the fourth-cohort panel actually cover once the `phase_map` k=12 intersection filter is relaxed to k≥2 — i.e. how large is the false-absence set that made EWSR1 read as "absent from this panel"? | **The Ensembl cDNA + ncRNA FASTA.** `map_probes_to_genes` fetches it over the network; it is in neither the checkout nor the frozen corpus. W20f costed the repair (44.3 MB, no measurable time penalty, non-destructive at `MIN_RUNS_TO_QUANTIFY = 12`) and could not produce the one number — genes recovered at k=2. One unauthenticated public GET, i.e. an Actions-runner job. **Not authorised by this planner.** Everything except the matcher is already local. |
| **B2** | Is the EWSR1 probe sequence `GCTTGTTTCCATCC…GCTGCTGC` unique across the human transcriptome, or does a second locus break the attribution of W20e's counts to EWSR1? | **The same FASTA as B1.** W20e checked 14 sequences from 7 genes offline and said plainly that the transcriptome-wide check "could not be made offline". |
| **B3** | Do the FET-IDR census's operational definitions generalise beyond EWSR1 — does the RGG-free-ceiling criterion recover a **non-EWSR1** FET fusion's architecture? | **An exon-level junction for `EWSR1::WT1` or `FUS::DDIT3`.** Ledger row AUT-PD-208 records that `grep -rn` over `research/modalities` returns none and `emc_fet_construct_designs.py::BREAKPOINTS` carries none. Needs one PMC full-text read with the quote. **Inventing a breakpoint to complete the control is refused.** Until then the census's two positive controls stay both-EWSR1 and `PUB-ATR`'s lines 29–32 stand verbatim. |
| **B4** | How far does this repository's UniProt-derived surfaceome differ from the published machine-learning surfaceome (Bausch-Fluck 2018)? — `PUB-SURFACE-TARGETS` peer-review item 44. | **The Bausch-Fluck gene-level membership table, committed as data.** `research/literature/remaining-reference-metadata-2026-08-09.json` holds the citation only (PMID 30373828 / PMC6243280 / DOI 10.1073/pnas.1808790115); no `*surfy*` or `*surfaceome*membership*` file and no `SURFY` string exists under `research/`. The cheap first test — asking the admitted PubMed route for PMC6243280's supplementary files — **has not been run and is a new source-retrieval act needing its own authorisation.** After the table lands the overlap is a local computation. |
| **B5** | Does the fusion's retained 5′ segment differ from a non-FET partner's in **phase behaviour** rather than in single-chain conformation — a saturation concentration rather than ν? | **GPU compute and a real-dollar spend.** The prereg §10 withholds the slab / direct-coexistence arm explicitly and routes the price to the user; the active no-GPU-spend posture in `autonomy-state.json` binds. |
| **B6** | What does the **full** type-1 retained segment (EWSR1 1–431, including the RRM at 361–442) do, rather than the RRM-truncated `E360` proxy? | **AlphaFold coordinates plus domain restraints (CALVADOS 3).** Prereg §3.1 and §10: CALVADOS 2 treats every residue as disordered, so running 1–431 under it is a model misuse, and guard G2 asserts no simulated window reaches the RRM. Needs a coordinate fetch and a second model — a separate decision, not an extension of R2. |
| **B7** | Is either EMC model TP53 wild type at sequence level — the observation `RT-MDM2`'s own record says does not exist? | **Bangerter Supplementary Table 1** (the FoundationOne®HEME variant list, ~89 KB CC BY PDF reachable from the paper's DOI). Ledger row AUT-105 prices it at $0 and notes the ceiling honestly: a variant table settles "no TP53 alteration **detected**" and cannot alone establish wild type, because the panel's gene list is not published. Network act. |
| **B8** | Would adding HLA-C to the class-I panel change the junction-neoantigen coverage figures? (ledger AUT-079) | **EXCLUDED, not merely blocked.** The HLA population-coverage paper is parked adverse and is outside this backlog. Also gated on an unknown: whether MHCflurry 2.1.4 scores HLA-C at all is UNKNOWN from this tree, and the item collapses if it does not. Recorded here so it is not re-proposed under another name. |
| **B9** | Does the 20-year-old SGK1 observation reproduce in a human system? (`PUB-KINASE-LEADS` lead 4) | **PMID 22592656** — paywalled, no PMCID, names no gene in its abstract. An institutional-library ask. No network route has been attempted and none is proposed. |
| **B10** | Which draft of the ATR collaborator package is canonical — the committed pre-revision file, or the state its 2026-08-10 review response describes (41 of 47 items, none present)? | **An owner decision**, not a computation. `BLOCKER-atr-package-uncommitted-revision.md` states it is not patchable item-by-item. Listed so no lane mistakes it for available work. |
| **B11** | Does the condensate negative survive a **second force field** (Mpipi), or is `NO_SEPARATION` CALVADOS-specific? | **An Mpipi implementation and residue parameter set**, neither committed nor installed; and the prereg §10 calls a second force field "a genuine new axis… a separate decision". Distinct from R2, which stays inside the frozen CALVADOS 2 arm. |

---

## What I checked and found empty — recorded so it is not re-searched

- **`systems/graph/routes.json`** — A2 graded all 52 un-closed routes on distinctness, input availability
  and non-overlap with a drafted manuscript; **zero passed all three**. I re-read the file and found no
  row A2 missed that is also outside the exclusions.
- **`research/hypotheses/candidates.json`** — A1 graded all 14; **all 14 fail gate 1** (already covered by
  a drafted endpoint or a recorded closure). Nine of the 14 have a bench experiment as their open question.
- **`research/autonomy/research-ledger.json`** — 212 open rows, of which **106 are `process_defect`**
  and most of the remainder are recorded negatives, network fetches, or hardening/readiness steps.
  The scientific-and-local residue is R2 (via the prereg), R3 (`AUT-115`) and R4.
- **Preregistrations** — of the 11 `kind: prereg` documents under `research/modalities/`, the ATR-inhibitor
  panel, the selectivity sensitivity control, the ABFE repair, the ternary/covalent series and the
  druggability prereg are all wet-lab- or GPU-gated. The CALVADOS prereg is the only one with an
  unfinished, CPU-reachable arm, and that is R2.
- **Readiness work I deliberately did not propose**, because the instruction excludes it: the
  `PUB-MODALITY-CENSUS` hardening/seat/PREFLIGHT_FULL sequence (AUT-PROP-061/062/063, AUT-044), the
  MTAP/PRMT5 `lint_consistency` DOI-substring rule, the ASO archive-manifest and citation-lint rows,
  and every `process_defect` row about the loop's own machinery. These are real and they are not
  scientific evidence work.
- **Not proposed on principle:** no quota, manifest, coverage or history audit; no corpus-wide record
  census; no "another fresh look" review of a correct paper.

---

**End of proposals. Nothing above is admitted. Root adjudicates.**
