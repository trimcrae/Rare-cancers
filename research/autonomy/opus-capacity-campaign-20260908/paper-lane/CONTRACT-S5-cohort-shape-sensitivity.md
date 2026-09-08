# S5 — paper-level decision and finite contract, recorded BEFORE dispatch

Recorded `date -u` = **Tue Sep  8 06:17:40 UTC 2026** (actual reading, not an approximation). Same session
`session_01Eui7FVgatEXAwt2N35yHH6`, `claude-opus-5` medium, existing first-party subscription, deadline
2026-09-09T02:37:19Z. One parent collector. Disk at contract time: **20 GiB free** (floor 10 GiB).

## Paper-level decision: **SUPPORTED — with the successor redefined, because S4's own proposal is a no-go**

⛔ **S4's named successor, as S4 wrote it, is REJECTED and is not executed.** It proposed repeating
`render_km` per cell "to convert the single fixed reading draw into a distribution." `render_km` is
deterministic: identical calls return identical pixels, so repeated identical renders are **deterministic
repeats, not independent draws**, and would yield **zero** additional information while consuming quota. That
is a no-go on the mechanism, not on the topic, and it is recorded here rather than quietly re-scoped.

✅ **A defensible paper-relevant uncertainty does remain, and it is a different one.** Every S4 result rests on
**one** synthetic cohort (n=59, 18 events, heavy terminal censoring with five patients at `t_max`). Its two
substantive findings — that extent dominates censored recovery, and that density is non-monotone with the read
arm degrading past 5 rows — are properties of an interaction between the risk table and *that* censoring
pattern. Whether they are properties of the **instrument** or of **that cohort shape** is unresolved, and it is
the question a methods paper would have to answer before stating anything general.

**Selected methods-paper question:** *Do the density and extent effects measured on one synthetic cohort
persist across prespecified, structurally distinct censoring shapes — and does controlled variation in
rendering or reading settings change the ranking of those effects?*

**Relation to existing evidence.** S2 established the control has no density/extent/anchoring arm (acceptance
branch b). S4 built the adapter and measured the grid on one cohort, independently reproducing the committed
`exact_coordinates_baseline` (0 / −7 / 0.0009). S5 varies the one thing S4 held fixed and could not vary. It
repeats no unchanged failed gate and re-runs nothing to recreate S4's lost files.

**This remains a candidate, not an admitted manuscript and not a clinical result.** Nothing in S5 creates a
publication, manuscript or clinical-result admission.

## Finite design, prespecified here before any run

- **Cohort shapes (the axis S4 held fixed):** ≥3 structurally distinct, deterministically constructed —
  S4's `_emc_shaped_cohort()` as the anchor, plus shapes differing in *where censoring sits* (early-censoring,
  uniform-censoring, low-event) built via the existing `_synthetic_cohort(n, event_fraction, t_max)`
  (`km_digitize.py:1358`) or an explicit deterministic construction. **If randomness is used anywhere, the seed
  is recorded; if construction is deterministic, that is stated as "deterministic, no seed."**
- **Density × extent:** a reduced grid sufficient to test the two S4 findings — rows spanning the
  non-monotone region (including ≤5 and ≥13) and extent spanning 0.25–1.0.
- **Rendering / reading:** clean plus ≥1 **controlled, deterministic** variation available without Pillow
  (e.g. line width, gridlines, or matcher tolerance). Each is a **fixed scenario**, not a replicate.
- **Controls:** an exact-coordinate arm in every cell, and **unchanged acceptance thresholds** —
  `MAX_KM_DEVIATION = 0.05` and `REQUIRE_RISK_TABLE = True` imported and echoed, never modified.
- **Why this finite grid answers the question:** the two S4 findings are directional claims about how error
  moves with rows and extent. Re-measuring the same directions on cohorts whose censoring sits elsewhere
  either reproduces the direction (evidence of an instrument property) or does not (evidence it was a cohort
  property). No larger grid is needed to separate those two.
- **Binding vocabulary:** results are **sensitivity across fixed prespecified scenarios**. The words
  *distribution*, *replication*, *draw*, *confidence* and *variability* must not be used for them.

## Durability — overrides any default scratch-delete-on-return

**Raw results are written directly to the durable collector-owned path**
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/S5-executed-artifacts/` — raw JSON, the exact
executed code, inputs, grid, seeds-or-no-seed, hashes, runtime and **every failure**. The child **verifies
those files exist and hash as recorded BEFORE deleting any scratch**, and if verification fails it keeps
scratch and says so. A report fence or an output hash **is not a substitute for original raw bytes**. Missing
bytes are labelled explicitly; **no original timing file is ever reconstructed.** The child writes nowhere else
in the repository — no manuscript, no shared graph.

## Bounds, acceptance and stop

Experiment wall-clock **≤ 20 minutes**, no extension to consume quota. Preserve **≥ 10 GiB** free, checked both
ends. Accepted on **raw per-cell output durably written and verified**, or on a **named missing
capability/dependency** with that branch stopped. Stop at acceptance, the runtime bound, or ~40 tool calls.

## Prohibited

No real clinical curves, no clinical patient reconstruction or pooling, no held biological/source
continuation, no unchanged failed gate, no re-run to recreate S4's `out.json`/`out2.json` or their timing
fields. No record or artifact census. S1/S3 stops, the P1–P3 closure dispositions, the P4–P6 intake
limitations, the NR4A/P6 successor exclusion and the W25 / primary-article / Results / novelty safety hold all
stay exact — no retry, rewording, model or owner substitution, and no blocked-writer wake. **No universal
journal requirement or lower bound for real figures may be drawn from synthetic ease.**

## Pinned inputs at contract time

| file | sha256 |
|---|---|
| `research/modalities/km_digitize.py` | `05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37` |
| `research/modalities/emc_ipd_survival.py` | `a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5` |
| `paper-lane/S4-executed-artifacts/sweep.py` (predecessor code) | `28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d` |

**Output ownership:** artifacts are campaign records owned by the parent collector. They are not a manuscript,
not a shared-graph edit, and confer no publication or clinical-result admission.

---

## Mechanical ownership clarification, delivered to the RUNNING child at 2026-09-08 06:22Z — no restart

Sent to child `a53b0d25fa5e70b56` in flight; **no replacement worker, no duplicate calculation, no re-plan.**
Scientific design, grid, runtime bound, acceptance criteria, worker and model are all **unchanged**.

**Change:** the child's assigned durable location moves **outside the shared checkout** to
`/tmp/claude-0/s5-retained/`, which is **exempt from cleanup until the parent collector has verified it**. The
child writes raw JSON (all cells, all arms, unabridged), exact executed code, resolved grid/parameters/
seeds-or-explicit-no-seed, hashes, runtime and every failure **there**, and now writes nowhere inside
`/home/user/Rare-cancers` at all. **The parent alone copies, verifies and commits** into
`paper-lane/S5-executed-artifacts/`. This preserves the repository's separate-writer / one-collector rule.

**Anything already written inside the checkout is preserved as-is.** The child was instructed not to delete,
move or rewrite such a file to satisfy the new rule, and to report its path and hash so the parent collects it.
**No output is discarded to retrofit a location rule.** State at the time the clarification was sent:
`paper-lane/S5-executed-artifacts/` was empty and `git status --porcelain` clean, so nothing was at risk.

Verify-before-cleanup still binds, now against the new path: confirm the files exist and hash as recorded,
print the verification, do **not** delete that directory, delete only ordinary working scratch and only after
verification passes, and keep everything if it fails. No git operation, manuscript edit, shared-graph edit or
broad source edit by the child. All other bounds and every held/closed route stand exactly as recorded above.

---

# S5 — EXECUTED, collected and verified. **S4's density finding is partly REFUTED.**

Child `a53b0d25fa5e70b56`, model verified from transcript as exactly `claude-opus-5`. Ran 06:19:12Z → 06:22:24Z
(3 min 12 s); **executed experiment 0.864 s** against the 20-minute bound; 20 GiB free at both ends. 4 cohorts ×
10 cells = **40 cells × 5 arms = 200 reconstructions**, exit 0, `stderr.txt` 0 bytes. All three contract pins
verified at run time and matched. Thresholds imported and echoed unchanged (`MAX_KM_DEVIATION 0.05`,
`REQUIRE_RISK_TABLE true`). **Deterministic, no seed** — and measured, not asserted: each cohort re-derived
twice in-process and compared by canonical-JSON sha256, 4 of 4 identical.

## Retention verified BEFORE any cleanup, both locations, nothing lost

Durable location `/tmp/claude-0/s5-retained/` verified by the child's own `sha256sum -c SHA256SUMS.txt` — **7 of
7 OK** — and re-verified by the parent. It was **not deleted**. Files written into the checkout *before* the
mid-task location change were **left exactly as-is** per the clarification and are **byte-identical** to the
retained copies (parent-verified, 6 of 6): `sweep5.py` `469222f6…`, `summarize5.py` `40d5dbe7…`,
**`results.json` `4a465b1a…` (126,998 B, raw, all 40 cells × 5 arms, unabridged)**, `SUMMARY-TABLES.txt`
`ffec705e…`, `RUNLOG.txt` `d0ae39c8…` (original timing bytes), `stderr.txt` `e3b0c442…` (empty as produced).
The parent additionally collected the two files that existed only in the retained location — `MANIFEST.md`
`04c1a4af…` and `SHA256SUMS.txt` `5eedaac1…`. **No missing bytes. No reconstruction of any kind.**

## Paper-level result: the two S4 findings do not survive equally

- **Extent — PERSISTS in direction, 4 of 4 shapes.** Exact arm improves monotonically 0.25 → 0.933 in every
  cohort (−25→−7, −19→0, −33→−3, −42→−3). But extending to full axis made it **worse in 2 of 4**, so S4's
  ordering with 1.00 best is a property of its five patients sitting at `t_max`, not of the instrument.
  Magnitude is entirely shape-dependent: `early_censoring` reaches **exact recovery at 0.50 extent**;
  `emc_anchor` never fully recovers at any extent.
- ⛔ **Density — S4's claim does NOT generalise.** Its read-arm form fails in 1 of 4 shapes
  (`uniform_censoring` is −2,−2,−3,−18,−2 — worst at 13 rows and recovered at 19). Its **exact-arm** form fails
  in **3 of 4** (flat at every density). And a single rendering setting reorders it: **`line_width_4` — a
  *degraded* 4-pixel curve — largely abolished the degradation**, `emc_anchor` at 19 rows −29 → **−11**,
  `low_event` at 8/13/19 rows −48/−51/−49 → **−4/−3/−3**. ⭐ **A render that is worse by whole-curve error
  (0.0612 vs 0.0292) reconstructed better by censored count.** On this grid S4's density result is better
  described as a property of that cohort against that render than a property of the instrument.
- **The admissibility floor still fails to police this class, now across four shapes:** 189 of 200 arms sat
  under 0.05 and read `admissible: True`, including `low_event` losing **51 of 53** censorings at maxdev 0.0225
  and `early_censoring` losing **41 of 41** at 0.0142.

## Failures and nulls retained, not dropped

`results.failures` = `[]` — no render refused, no exception in 200 reconstructions. **11 of 200 arms refused by
`assess_quality`** on the unchanged floor (uniform_censoring rows 13 and 19; low_event rows 3), **0 of 40
exact-coordinate arms refused**; no guard touched. **Pillow absent** — named, `km_digitize.jpeg_roundtrip`
(`:1495-1501`), branch stopped, nothing installed; the JPEG branch is **UNKNOWN, not absent**.
⚠ **A genuine null the child flagged against its own design:** `gridlines` and `lenient_matcher` produced
**byte-identical digitized series to clean in all four cohorts** — gridlines are drawn at luma 215, above both
matcher thresholds — so 2 of 3 read variations were **inert**, and the whole "rendering reorders the ranking"
observation rests on `line_width_4` alone.

## Independent reproduction of prior records

Cohort hash `7deb0b9f…` and clean `digitized_sha256` `48af484b…` both reproduce S4's recorded values
byte-for-byte, and the anchor's exact arm at rows 8 / extent 0.933 again returns `0 / −7 / 0.0009` — the
committed `exact_coordinates_baseline`, now measured a second time under an independent child.

## Limits, binding

No clinical claim; cohorts are generated arithmetic and **no row is a patient**. A passing synthetic cell
creates **no** reporting requirement. `⛔_direction_of_the_bound` applies to every figure — synthetic renders
are easier than journal figures, so each bounds real-figure error only **from below**. **No universal journal
requirement and no lower bound for real figures.** A general reporting requirement remains **UNKNOWN**. Four
cohorts all at n=59, one renderer, uniform row placement only; they are not a sample and nothing estimates how
often a shape occurs. **No manuscript, publication or clinical-result admission is created.**

## Named successor — PROPOSED, NOT RUN, not authorized here

Test whether **read-curve point count**, rather than row count, drives censored loss: hold cohort and risk
table fixed and vary `render_km`'s figure `width` across a few fixed values on `emc_anchor` and `low_event`.
Deterministic, Pillow-free, fixed prespecified scenarios — not draws, and not to be described as a
distribution.
