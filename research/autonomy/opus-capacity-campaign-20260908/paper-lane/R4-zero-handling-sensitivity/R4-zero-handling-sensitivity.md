# R4 — bounded zero-handling sensitivity measurement (fourth-cohort tables)

**Date (UTC): 2026-09-08.** Repo HEAD read: `4dc9e5d9df35e5a1d67b1cc96d6b26de018f41c0`.
Sole exclusive writer for `R4-zero-handling-sensitivity/`. No other path in the tree was written.
**No network. No commit. No push. No test suite. No preflight. No source fetch.**

**Stop reason: the finite comparison completed.** It is *not* an input insufficiency — the retained
tables answered the question. The answer is that the question is **structurally vacuous on the
retained gene panel**, and the reason is measurable and is given below.

---

## 0 · What is preserved unchanged

- ⛔ **The W20e EWSR1 endpoint result — NULL under all three zero-handlings — is unchanged.**
  Nothing here re-runs it, re-tests it, or revises it. `EWSR1` is **not a row of the retained gene
  table** (`grep -c '^EWSR1\t'` → 0); W20e measured a single *unassigned* 50-mer, which is a
  different unit from anything measured here.
- ⛔ **Every patient/partner-identity caveat stands.** Runs are not samples and samples are not
  people. A break-apart FISH call names no partner, so `EWSR1`-negative is not "not EMC". The
  sequence W20e measured is `UNVERIFIED` as to probe identity. The vendor panel is named nowhere.
  `Prognosis` B/G remains undefined by the deposit and is not used here.
- ⛔ **The canonical quantifier and every prior source table are unchanged.** The committed
  `emc-fourth-cohort-gene-counts.tsv` and `emc-fourth-cohort-probe-counts.tsv` were read only.
- ⛔ **The default convention is unchanged.** Convention B (literal) remains the committed pipeline.
- No hypothesis test is run. **No p-value is computed anywhere in this task**, deliberately.

---

## 1 · Step 1 — the unit the retained tables actually carry, and the conventions defined against it

### 1.1 The unit

Two retained tables, two units:

| Table | Unit | Rows |
|---|---|---|
| `research/modalities/emc-fourth-cohort-probe-counts.tsv` | one **retained 50-nt sequence** × 12 runs, plus an `assigned_gene` label | 213,007 |
| `research/modalities/emc-fourth-cohort-gene-counts.tsv` | one **gene** × 12 runs | 862 |

The source module states the gene cell's construction and its error bound verbatim
(`emc-fourth-cohort-quant.json` → `⛔ gene_counts_units`):

> "RAW READS PER GENE, **summed over the probes assigned to that gene**, per run. … understated by
> at most `support_floor_reads` **per probe** — the lossy-counting guarantee, per run."

**Therefore the persistence floor is a per-probe quantity, and the conventions are defined at the
probe unit and aggregated to the gene.** I verified the aggregation rather than assuming it: summing
the probe table by `assigned_gene` reproduces the committed gene table **cell-for-cell, 862/862 rows,
0 mismatches** (assertion in the script; it would have aborted otherwise). Assigned probes: 906, over
862 genes — **823 genes carry 1 probe, 36 carry 2, 2 carry 3 (`FAM156A`, `TPM4`), 1 carries 5
(`ENSG00000283738.3`)**.

### 1.2 Four states, kept separate and never collapsed

| State | Definition | Count in the retained tables |
|---|---|---|
| **1 · observed zero** | a cell known to be a measured zero read count | **0 cells — NOT REPRESENTABLE.** The source states `⛔ a_zero_in_the_probe_table`: a zero "means the sequence was not among the counts PERSISTED for that run … **It is not a measurement of zero reads.**" No cell is placed in this state by this task. |
| **2 · absent / filtered probe** | cell reads 0; value indeterminate in `[0, support_floor_reads]` | **0 of the 10,344 gene × run cells** (see §2 — this is the finding) |
| **3 · missing mapping** | the sequence carries no gene assignment, so no gene-level cell exists for it under any convention | **212,101 of 213,007 retained sequences**; **211,362** of those have ≥1 unpersisted run |
| **4 · uncomputable comparison** | an arm left with 0 valid runs, or a convention the tables do not support | **0 gene-level cells** under A/B/C; the whole of state 3 is uncomputable at gene level (§4) |

Root's first warning is honoured by state 1 being empty: **a missing probe below a per-run
persistence floor is never recorded here as a measured zero gene count.**

### 1.3 The three conventions, executable at the probe unit

Let `P(g)` be the probes assigned to gene `g`, `c(p,r)` the retained cell, `F(r)` the run's
`support_floor_reads`, and `Z(g,r) = { p ∈ P(g) : c(p,r) = 0 }` (the state-2 probes).

| Conv. | Name | Gene value in run `r` | Run eligibility |
|---|---|---|---|
| **B** | `LITERAL` — **the committed default, unchanged** | `Σ_p c(p,r)`; a state-2 cell contributes 0 | always eligible |
| **C** | `FLOOR_IMPUTED` | `Σ_{p∉Z} c(p,r) + |Z(g,r)|·F(r)` | always eligible |
| **A** | `DROP_CENSORED` | `Σ_p c(p,r)` when `|Z(g,r)| = 0` | **ineligible when `|Z(g,r)| ≥ 1`** — the gene's value in that run is a lower bound, not a measurement. Dropped **per gene**, never globally. |

**Explicit justification for `|Z|·F` rather than a single `F` — root's second warning.** The
module's lossy-counting guarantee is stated *per probe*. A gene whose `k` probes are all unpersisted
in a run is understated by up to `k·F(r)`, not by `F(r)`. Giving a multi-probe gene one probe's floor
would understate the imputation by exactly the factor `k` — up to 5× for `ENSG00000283738.3`. `|Z|·F`
is an **upper bound on the understatement, not a point estimate**: the true unpersisted count lies
anywhere in `[0, F(r)]` per probe, so C is the maximal-imputation end of the admissible range and B
is the minimal end. A and C therefore bracket the convention space rather than sampling it.

**Normalisation held fixed.** `CPM = value / L(r) · 1e6` with `L(r)` = the **committed panel library
size** (column sum of the committed gene table), identical under all three conventions, so a
convention moves the numerator only. The library-size inflation convention C would cause if
propagated is reported as a diagnostic and **not applied**: it is **exactly 0.0 in every one of the
12 runs**, because `|Z| = 0` everywhere (§2), so the choice is moot here and is recorded only so a
future re-use of these definitions on a different panel does not inherit an unstated assumption.

**Statistic (W20's, unchanged).** `δ(g) = mean_{FISH−} log2(CPM+1) − mean_{FISH+} log2(CPM+1)`.
Sign convention is W20's: **δ < 0 means higher in the FISH-positive arm.** FISH split reproduced:
`EWSR1−` = SRR35940648, 654, 656, 657 (n = 4) vs n = 8.

---

## 2 · The result: the three conventions are **exactly identical**, and the reason is structural

**Measured, not asserted:** across all **10,344** gene × run cells (862 genes × 12 runs), the number
carrying **≥ 1 unpersisted contributing probe is 0**. The minimum cell in the whole assigned-probe
block is **17 reads**. Consequently `|Z(g,r)| = 0` everywhere, and:

| Quantity | Value |
|---|---|
| Sign flips B → C | **0** |
| Genes whose panel percentile moves at all, B → C | **0** |
| `max |δ_C − δ_B|` over the panel | **0.0000000000 log2 units** (exact identity) |
| `max |δ_A − δ_B|` over the panel | **0.0000000000 log2 units** (exact identity) |
| `max |pct_C − pct_B|` over the panel | **0.0000 percentage points** |
| Runs dropped under A, any gene | **0** — every gene keeps `n_neg = 4`, `n_pos = 8` |
| Genes uncomputable under any convention | **0 of 862** |

**Why — and this is the load-bearing sentence of this report.** The panel is built from
`n_probes_common_to_every_read_run = 1,645`: the matcher was offered only the sequences persisted in
**every** run. I verified that this set is *precisely* the set of rows with no zero cell: rows with no
zero in any of the 12 columns = **1,645**, exactly the offered count, and **all 906 assigned probes
lie inside it** (see the `runs_persisted` histogram in `R4-run-log.txt`, column `n_assigned_to_a_gene`
— non-zero only at `k = 12`).

> **The intersection filter and the zero-handling question are the same filter.** A probe that could
> have produced a zero was removed from the panel before the gene table existed. So the gene panel
> **cannot** be sensitive to zero handling: the invariance is a **tautology of the panel's
> construction**, not an empirical robustness result.

⚠ This is the opposite of reassuring. The convention has no effect on the panel *because* every
sequence on which it would have had an effect was excluded. The excluded pool is large: **211,362
sequences carrying 64.89% of all retained reads** have at least one unpersisted run, and none of them
has a gene.

---

## 3 · Step 2 — implementation gate against the old arithmetic (run **once**)

Declared TAF15/FUS sentinels, reproduced from the retained tables by this new implementation:

| Gene | probes | δ observed | δ expected (W20) | pct `i/n` obs | expected | pct `(i+0.5)/n` | rank-set `n` |
|---|---|---|---|---|---|---|---|
| **TAF15** | 1 | **−0.8347** | −0.8347 ✓ | **9.05** | 9.05 ✓ | 9.11 | 862 |
| **FUS** | 1 | **+0.0789** | +0.0789 ✓ | **62.06** | 62.06 ✓ | 62.12 | 862 |

**GATE: PASS**, exact to every reported digit, on the first and only run. This fixes the pipeline,
the sign convention, the FISH split, the library-size definition, the rank set and the tie rule in
one shot.

⛔ **The sentinels' p-values were deliberately NOT recomputed.** Reproducing W20's exact-enumeration
p-values would be re-running their scientific endpoint, which this task forbids. The gate is placed
on δ and on the panel percentile — the two quantities this sensitivity measurement actually moves —
and that is sufficient to verify the implementation. No p-value appears in any R4 artifact.

---

## 4 · Step 3 — per convention and per gene

Full table: **`R4-per-gene-convention-table.tsv`** (862 genes × 3 conventions = 2,586 rows), carrying
for every cell: contributing probes; runs with a state-2 cell; valid samples in **each arm**
separately; the defined statistic; eligible rank-set size; the tie rule; the percentile units; both
percentile offsets; the cell state; and the uncomputable reason where one applies.

Sign/rank accounting: **`R4-sign-rank-sensitivity.tsv`** (862 rows, one per gene, all three
conventions side by side, **invalid cells retained rather than dropped** in the `invalid_cells`
column). Machine summary: **`R4-summary.json`**. Verbatim run output and exit code:
**`R4-run-log.txt`**.

### 4.1 Both the estimand and the rank set — shown separately

| | Convention A | Convention B | Convention C |
|---|---|---|---|
| **Estimand** — valid samples per arm, every gene | 4 neg / 8 pos | 4 neg / 8 pos | 4 neg / 8 pos |
| **Rank set** — eligible rank-set size `n` | **862** | **862** | **862** |
| Genes falling out of the rank set | 0 | 0 | 0 |

Missingness *can* alter both, which is why both are reported; here it alters **neither**, for the
structural reason in §2. A convention that dropped runs on a panel containing state-2 cells would
change the estimand gene-by-gene (different arms per gene) *and* shrink the rank set (genes losing an
entire arm become state 4), making percentiles from different genes non-comparable. That failure mode
is real and is simply not exercised by this panel.

### 4.2 Tie rule and percentile units

- **Tie rule:** `i = #{ h in the rank set : δ(h) < δ(g) }` — a strictly-less count, so tied genes all
  receive the same (minimum) rank. This is W20's rule; the sentinel gate confirms it
  (9.05 % of 862 = rank 78 exactly; 62.06 % of 862 = rank 535 exactly).
- **Percentile units:** **percent, 0–100**, of the rank position within the eligible rank set.
  Reported at both offsets, `i/n` (W20's) and `(i+0.5)/n` (W20d's).

### 4.3 The `i/n` versus `(i+0.5)/n` offset, derived from the actual `n`

The offset is exact arithmetic, not a tolerance:

```
offset = (i+0.5)/n − i/n = 0.5/n
n = 862  →  0.5/862 = 0.00058005  →  0.058005 percentage points  (= 0.058 pp, or the fraction 5.80e-4)
```

That is the whole of the "+0.06" discrepancy W20d recorded between its percentiles and W20's, and it
is identical for all three conventions here because all three share `n = 862`.

⚠ **W20e's `0.10` is not a unit-free universal threshold and is not treated as one.** At `n = 862`
the true offset is **0.058 pp**, so `0.10` was ≈1.72× larger than the gap it was meant to absorb —
adequate here by accident of `n`. The offset **exceeds** `0.10 pp` for **any rank set with `n < 500`**
(`0.5/n·100 > 0.10 ⟺ n < 500`), at which point a `0.10` tolerance silently stops covering the
convention gap it was written for. Anyone re-using that tolerance on a smaller rank set must
recompute `0.5/n` for their own `n`.

⚠ **This offset is a reporting-convention artefact. It is NOT a significance threshold and NOT a
biological-importance threshold, and it is not redefined as one anywhere in this task.**

### 4.4 Uncomputable cells, retained with their exact reasons

⛔ Nothing was fabricated to fill a cell. The uncomputable set is:

| Set | Size | State | Exact reason retained |
|---|---|---|---|
| Gene × convention cells | **0 of 2,586** | — | all computable |
| Retained sequences with no gene | **212,101 of 213,007** | **3 · missing mapping** | `assigned_gene = 'unassigned'`. No gene-level convention can be *defined* for them, let alone evaluated. Of these, **211,362 have ≥1 unpersisted run** — i.e. the entire population on which zero handling would bite sits behind a missing mapping. |
| The counterfactual rank set under a relaxed persistence rule | **UNCOMPUTABLE** | **4** | Assigning any of those 212,101 sequences to genes requires the matcher's own sequence set — the Ensembl GRCh38 cDNA + ncRNA FASTA, fetched over the network by `emc_fourth_cohort_quant.py` (`probe_map.sources`), **not committed to this repository and not in the frozen corpus**. Network access is forbidden here and was not attempted. The number of genes that would join the rank set is **UNKNOWN, not zero.** |

The excluded pool, quantified from the retained probe table alone (full histogram in
`R4-run-log.txt`): 162,981 sequences persist in exactly 1 run; only 1,645 persist in all 12. The 12/12
stratum carries **35.11 %** of retained reads; the other 64.89 % belongs to sequences no gene-level
convention can currently reach.

---

## 5 · Deliverable — exact mapping to current manuscript claims

**NONE. No current manuscript claim consumes any quantity measured here.** Checked, not assumed:

| Check | Result |
|---|---|
| `grep -rn -E "0\.8347\|0\.0789\|62\.06\|9\.05" research/manuscripts/` | **0 hits.** δ and the panel percentiles appear only in campaign reports `W20d`, `W20e` — never in a manuscript. |
| Manuscripts referencing the fourth cohort | `nr4a3-fusion-transcriptional-output.md` (§3.13 retraction row, line 1328) and `emc-fourth-cohort-sra-2026-08-08.md`. |
| What that manuscript row claims | It **narrows** an earlier "no fourth EMC expression cohort exists" sentence, and states explicitly that "**Limitation 1's n = 4, 6 and 10 is UNCHANGED for the analyses this paper runs**". It reports the deposit's existence and its FISH split; it derives **no expression quantity** from it. |
| Consequence | The mapping from R4 to live manuscript prose is **empty**. Nothing in §2–§4 requires any manuscript edit, and none is made. |

One adjacent, non-actionable observation, recorded so it is not mistaken for a gap: the same
manuscript's correction row at line 1329 (percentile denominators 14,120 → **13,708 / 13,247**,
because "the percentile distributions exclude any gene whose comparator median is zero") is
*structurally the same failure mode* — a zero-handling rule that changes a rank-set denominator. It
concerns the **GSE28866 axis, a different dataset and different tables**, it was already corrected on
2026-09-08, and it is **out of R4's input scope**. It is named here only to record that the
fourth-cohort panel has **no analogous exposure**, and nothing about it is re-opened.

---

## 6 · What this result does and does not mean

⚠ **Stability under three conventions is robustness to those choices — it is NOT proof that the
calibration is sound or unbiased.** Here it is weaker than even that: the three conventions coincide
*exactly*, and they coincide because the panel was constructed by excluding every sequence on which
they could differ. **An exact tie is evidence about the filter, not about the measurement.** It says
nothing about whether the retained 906 probes are a fair sample of transcript abundance, whether CPM
against a 862-gene panel is the right normalisation, whether FFPE degradation across 23 collection
years biases the arms differently, or whether any δ is unbiased.

⚠ **An unstable sign is not a new biological discovery.** No sign is unstable here (0 flips). Had one
been, it would have been a statement about a missing-data convention, not about a gene. W20e's own
sign flip (δ −0.48 → +1.97 on the candidate EWSR1 sequence) is exactly this: an artefact manufactured
by a value the source module says is not a measurement — and it did **not** change that endpoint's
verdict, which remains **NULL**.

⛔ No gene-biology claim is made about any of the 862 genes. No patient is classified. No FISH-arm
endpoint is created. There is no wet lab, and nothing here bears on EMC efficacy, safety, selectivity
or clinical readiness.

---

## 7 · Validation evidence

Python 3.11.15, standard library only. No third-party package, no network, no GPU, no paid API.

```
$ md5sum r4_zero_handling_sensitivity.py           # before run
e6c2ae09ad4191000585f08226b4b31f  r4_zero_handling_sensitivity.py
$ python3 r4_zero_handling_sensitivity.py > R4-run-log.txt 2>&1; EX=$?; echo "EXIT=$EX"
EXIT=0
$ md5sum r4_zero_handling_sensitivity.py           # after run — unchanged
e6c2ae09ad4191000585f08226b4b31f  r4_zero_handling_sensitivity.py
```

**Exit code 0 was actually emitted** (no pipe in the measured command; `$?` captured directly). The
script exits 0 only on `GATE=PASS` and 4 on gate failure. Full verbatim stdout: `R4-run-log.txt`.

Input hashes as recorded by the source module and relied on here (not recomputed — the tables were
read, not regenerated): `probe_counts_sha256 = c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc`,
`gene_counts_sha256 = 8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc`.

**PROPOSED (NOT RUN):** any assignment of the 212,101 unassigned sequences to genes (requires the
network Ensembl fetch — not attempted, recorded as UNCOMPUTABLE in §4.4); `scripts/preflight.sh` and
the test suite (both fenced out of this task); any commit or push (the parent integrates).

---

## 8 · Files produced (all under this directory; nothing else in the tree was written)

| File | Contents |
|---|---|
| `r4_zero_handling_sensitivity.py` | the analysis; conventions and states specified in its docstring |
| `R4-per-gene-convention-table.tsv` | **per-gene convention table**, 862 genes × 3 conventions, 17 columns |
| `R4-sign-rank-sensitivity.tsv` | **sign/rank sensitivity accounting**, invalid cells retained |
| `R4-summary.json` | machine-readable summary, including the gate |
| `R4-run-log.txt` | verbatim stdout plus the real exit code |
| `R4-zero-handling-sensitivity.md` | this report |
