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
