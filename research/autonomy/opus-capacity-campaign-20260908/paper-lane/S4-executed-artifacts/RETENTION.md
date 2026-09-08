# S4 executed-artifact retention — mechanical, by the same collector

No worker dispatched, no experiment re-run, no code executed by the launcher. Bounded preservation only.

## Retained here

| path | bytes | sha256 | status |
|---|---:|---|---|
| `sweep.py` | 8183 | `28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d` | **VERIFIED — matches the execution record exactly.** Extracted verbatim from the sole ```python fence of the collected report; hash computed on the extracted bytes and compared, not assumed. Parameters and the full grid live inside this code, so their identity is preserved by the file itself. |
| `ORIGINAL-PARTIAL-STDOUT.txt` | 890 | `6325271b57b3b412ce…` (full hash in the file's own record below) | **ORIGINAL bytes from the child transcript**, not a reconstruction. Carries the `sha256sum sweep.py` line, the `time` output (`real 0m0.229s / user 0m0.197s / sys 0m0.031s`), `EXIT=0`, the complete `meta` block of `out.json` and the `cells 25` count. |

## Pinned unmodified inputs — verified in place at this HEAD, not copied

| repository path | sha256 | verification |
|---|---|---|
| `research/modalities/km_digitize.py` | `05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37` | **matches** the pinned hash and the child's scratch copy — the copy was byte-identical, so the generator was never edited |
| `research/modalities/emc_ipd_survival.py` | `a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5` | **matches** the pinned hash; imported unmodified, with `MAX_KM_DEVIATION 0.05` and `REQUIRE_RISK_TABLE true` echoed back by the run |

Both files are already tracked at these bytes, so they are retained by reference rather than duplicated.

## ⛔ Irrecoverable original-output gap, recorded rather than papered over

**The original `out.json` bytes are NOT recoverable.** Searched the full child transcript
(`acd5d9ce31630ead4`, 236,738 bytes, 1,669 string nodes): **zero** strings hash to
`ebc40a755bf0be6a64c42c95bc4df913e8cc67f02a9a5005fda1c35efd74b75c`, and the four strings carrying `out.json`
markers are the report itself, `sweep.py`, the 890-byte partial stdout above, and the determinism-check
command. The cause is structural: the child ran `python3 sweep.py > out.json`, so the full JSON went to a
scratch file and **never passed through a tool output**; scratch was then deleted per contract.

**Nothing was re-run and no JSON was reconstructed from the committed tables.** A reconstruction could not
carry the original per-cell `seconds` fields and would not hash to `ebc40a75…`; presenting one as original
output is exactly what this retention forbids. What survives instead:

- the **original hash** `ebc40a755bf0be6a64c42c95bc4df913e8cc67f02a9a5005fda1c35efd74b75c`, recorded so any
  future recovery of the file can be checked against it;
- the **original `meta` block verbatim** in `ORIGINAL-PARTIAL-STDOUT.txt` — cohort hash
  `7deb0b9f…`, n 59, truth 18 events / 41 censored / median 168.0, `t_max` 180.0, thresholds as imported,
  `render_read_seconds` 0.041, `read_ok` true, `refusal` null, curve error 0.0292 / 0.0012 / 0.0008,
  `digitized_sha256` `48af484b…`, 20 points, `total_seconds` 0.151, `n_cells` 25;
- **complete per-cell tables** in `../S4-density-extent-anchoring-EXECUTED.md` — all 25 cells × 2 arms = 50
  reconstructions, each with `events_delta_vs_truth`, `censored_delta_vs_truth`, `median_delta_vs_truth`,
  `internal_max_abs_km_deviation` and admissibility. **Table completeness: 50 of 50 arms present.** What the
  tables do *not* carry, and the raw file did, are the per-cell `seconds` fields and the per-cell
  `n_reconstructed / n_events / n_censored` for the axis-2, axis-2b and axis-3 blocks (axis-1 totals are
  narrated). That is the exact residual loss.

## Observations preserved verbatim from the executed run

- **Six quality failures on the unchanged floor**, retained and not suppressed: four t₁=24 cells
  (`0.0941` exact, `0.1155` read) and two t₁=11 clean-render cells (`0.0536`, message
  `['km_deviation 0.0536 exceeds floor 0.05']`). **No guard was touched to make them pass.**
- **Missing dependency, outside the clean grid:** Pillow (`PIL`) not installed —
  `ModuleNotFoundError: No module named 'PIL'`; call site `km_digitize.jpeg_roundtrip`
  (`km_digitize.py:1495-1501`). No cell of the grid depended on it; nothing was installed.
- **Actual runtime:** executed experiment `real 0m0.229s` (`user 0m0.197s`, `sys 0m0.031s`), in-process
  `total_seconds` 0.151, render+read 0.041 s. Child wall clock 05:47:17Z → 05:49:59Z.
- **Repeat / determinism record:** a byte re-run differed from the first **only** in recorded `seconds`; with
  timing fields stripped the two runs compared **identical**. Recorded because it was observed, not because it
  is a real difference. The `out2.json` used for that check was removed by the child's own command and is
  likewise unrecoverable.
- **No cell crashed**; the adapter's `except` never fired and `err.txt` was empty at exit 0.

## Provenance of this retention

Child `acd5d9ce31630ead4`; model confirmed from the existing child transcript as **`claude-opus-5`** (observed
model set is exactly that single value) — re-confirmed here, not re-derived by any new run. Collected by the
one parent collector. Prior records remain intact: the S4 report, the S4 contract with its appended
disposition, the S1/S3 interrupted partials, the selection record with both appended corrections, and the
P1–P6 reports are unchanged.

All scientific conclusions remain restricted to the executed synthetic control and its contract: no clinical
claim, no reporting requirement from a passing synthetic cell, figures bound real-figure reading error from
below, the control result is not a universal lower bound for real 8-row tables, and a general requirement
remains **UNKNOWN**. No deadline, billing, controller, session or hold changed.
