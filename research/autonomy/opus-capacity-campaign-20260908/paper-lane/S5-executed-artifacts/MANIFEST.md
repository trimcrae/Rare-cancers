# S5 durable artifact manifest — cohort-shape sensitivity of S4's density/extent findings

Worker S5, OPUS-CAPACITY-CAMPAIGN-20260908, paper-lane. Written to `/tmp/claude-0/s5-retained/`
per the coordinator's mid-task location change. **Exempt from cleanup until the parent verifies.**

## Randomness
**DETERMINISTIC, NO SEED IS USED.** No randomness is consumed anywhere. `km_digitize._synthetic_cohort`
constructs `_Rng(90210 + n)` but never samples from it (`_ = rng` at `km_digitize.py:1374`); the other two
cohorts are written out arithmetically. Measured, not asserted: every cohort was re-derived twice in-process
and compared by canonical-JSON sha256 (`meta.determinism_selfcheck`) — 4 of 4 identical.

## Vocabulary
Results are **sensitivity across fixed prespecified scenarios**. `render_km` is deterministic, so a repeated
identical render is a deterministic repeat carrying no information. Nothing here is a distribution,
replication, draw, variability estimate or confidence, and no statistic presupposing sampling is computed.

## Inputs (unmodified, hashes verified in place at run time)
| path | sha256 | matches contract pin |
|---|---|---|
| `research/modalities/km_digitize.py` | `05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37` | yes |
| `research/modalities/emc_ipd_survival.py` | `a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5` | yes |
| `paper-lane/S4-executed-artifacts/sweep.py` (predecessor code reused) | `28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d` | yes |

Thresholds imported and echoed, never modified: `MAX_KM_DEVIATION = 0.05`, `REQUIRE_RISK_TABLE = true`.

## Resolved grid
- Cohort shapes (4): `emc_anchor__terminal_censoring` (`kd._emc_shaped_cohort()`, sha256 `7deb0b9f61a765f83d8b3585b9d0e47f04da9c0788205f73b1caf71cb94deea9` — byte-identical to S4's cohort hash),
  `early_censoring` (explicit arithmetic, sha256 `524fab9ed618d9274039bfb1d8a47820d2b7f07ad5a99280dd583977c6fc1eab`),
  `uniform_censoring` (`kd._synthetic_cohort(59, 0.30, 180.0)`, sha256 `3ca5af0e5ef9fb2c0df6f49a0393fedf0a06c1abe2f7be36c9d20dca510e5e87`),
  `low_event` (`kd._synthetic_cohort(59, 0.10, 180.0)`, sha256 `44f23fd9e19864252899395dcbbb7f237ea7101dc5599ae3f5f6e072825cd694`).
- Density axis: rows 3, 5, 8, 13, 19 at fixed extent 0.933 (last row 168.0).
- Extent axis: 0.25, 0.50, 0.75, 0.933, 1.00 at fixed density 8 rows.
- Render/read scenarios (4, all Pillow-free): `clean__strict_matcher`, `line_width_4__strict_matcher`
  (`render_km(line_width=4)`), `gridlines__strict_matcher` (`render_km(gridlines=True)`),
  `clean__lenient_matcher_luma175` (`dark_matcher(max_luma=175)`).
- Control: an exact-coordinate arm in EVERY cell (no render, no read).
- Totals: 4 cohorts x 10 cells = **40 cells**; 40 x (1 exact + 4 read) = **200 reconstructions**.

## Runtime
`time python3 sweep5.py > results.json` → `real 0m0.864s  user 0m0.847s  sys 0m0.016s`, `EXIT=0`.
In-process `meta.total_seconds` = **0.827 s**. Start `Tue Sep  8 06:20:57 UTC 2026`, end `06:20:58 UTC 2026`.
Far inside the 20-minute bound. `stderr.txt` is 0 bytes.

## Failures (all recorded, none dropped)
- `results.failures` = `[]` — no render refusal and no exception in any of the 200 reconstructions.
- **Quality-floor refusals on the UNCHANGED floor: 11 of 200 arms** (`admissible_under_the_floor = false`),
  all in the read arms, all on the density axis, none in any exact-coordinate arm (0 of 40):
  `uniform_censoring` rows 13 — clean 0.0560, gridlines 0.0560, lenient 0.0560 (3);
  `uniform_censoring` rows 19 — clean 0.0548, line_width_4 0.0641, gridlines 0.0548, lenient 0.0548 (4);
  `low_event` rows 3 — clean 0.1015, line_width_4 0.1062, gridlines 0.1015, lenient 0.1015 (4).
  **No guard was touched.** The `emc_anchor` and `early_censoring` cohorts had 0 refusals.
- **Missing dependency:** Pillow (`PIL`) — `python3 -c "import PIL"` → `ModuleNotFoundError: No module named 'PIL'`.
  Call site `km_digitize.jpeg_roundtrip` (`km_digitize.py:1495-1501`). No scenario here depends on it;
  the JPEG branch is stopped as unavailable and nothing was installed.

## Outputs in this directory
See `SHA256SUMS.txt` (generated alongside this file).

## Also left in the repository checkout (written BEFORE the coordinator's location change; left exactly as-is)
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/S5-executed-artifacts/` contains byte-identical
copies of `sweep5.py`, `summarize5.py`, `results.json`, `SUMMARY-TABLES.txt`, `RUNLOG.txt`, `stderr.txt`
(same sha256 as here). Nothing was deleted, moved or rewritten to retrofit the rule. No git operation was run.

## Interpretation limits (binding)
Synthetic cohorts, generated arithmetic; **no row is a patient**. No clinical claim of any kind. A passing
synthetic cell creates no reporting requirement. `⛔_direction_of_the_bound`: a synthetic render is EASIER
than a journal figure, so every figure here bounds real reading error only FROM BELOW. No universal journal
requirement and no lower bound for real figures may be drawn from synthetic ease; a general reporting
requirement remains **UNKNOWN**.
