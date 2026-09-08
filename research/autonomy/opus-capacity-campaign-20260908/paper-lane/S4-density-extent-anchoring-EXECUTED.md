<!-- collected 2026-09-08T05:53:52Z by campaign coordinator; agent id acd5d9ce31630ead4; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-acd5d9ce31630ead4.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**S4**, synthetic instrument method-development lane, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to S2.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. No environment variable names a model; the literal mandated output is below.

**Start** `date -u` = `Tue Sep  8 05:47:17 UTC 2026`; HEAD `81c077ea1461d291bd2f031e40f98028c4de583e`; `git status --porcelain` = **empty (0 lines)**; `df -h /` = `/dev/vda 252G 18G 20G 47% /`.
**End** `date -u` = `Tue Sep  8 05:49:59 UTC 2026`; HEAD `81c077ea1461d291bd2f031e40f98028c4de583e` (**unchanged**); `git status --porcelain` = **empty (0 lines)**; `df -h /` = `/dev/vda 252G 18G 20G 47% /` (≥ 10 GiB free preserved at both ends; peak scratch use 300K). No repository write, no git write operation, no manuscript/graph edit, no publication, no network, no paid API, no GPU. `scripts/preflight.sh` not run. `research/modalities/atr_hrd_sarcoma_series.py` never invoked.

Literal output of the mandated command (identical at start and end; secrets redacted by the mandated `sed`; long proxy lists shown in full as emitted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=localhost|127.0.0.1|::1|127.*|0.*|::|169.254.*|api.anthropic.com|api-staging.anthropic.com|api-pr-preview.anthropic.com|mcp-proxy.anthropic.com|mcp-proxy-staging.anthropic.com|registry.npmjs.org|jsr.io|npm.jsr.io|pypi.org|files.pythonhosted.org|index.crates.io|proxy.golang.org|host.docker.internal|10.*|172.16.*|172.17.*|172.18.*|172.19.*|172.20.*|172.21.*|172.22.*|172.23.*|172.24.*|172.25.*|172.26.*|172.27.*|172.28.*|172.29.*|172.30.*|172.31.*|192.168.*|100.64.0.0/10|*.svc.cluster.local|*.svc.cluster.local -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,...,*.svc.cluster.local
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...,*.svc.cluster.local
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(`NO_PROXY` and `npm_config_noproxy` values elided mid-list with `...` for length only; no other line altered. **No variable names a model** — hence the self-report.)

## Question

At **fixed clean rendering**, over the **synthetic** control cohort whose ground truth is known by construction, how does reconstruction error depend on the numbers-at-risk table's **density** (rows printed), **extent** (last printed row as a fraction of `t_max`), and **first-row anchoring** (printed time vs immediately before it) — the three axes S2 specified and could not run?

## Prior-work check

I did not repeat S2's corpus search; S2's structural finding is given context per my contract. I confirmed only the two facts my adapter depends on, by reading the live checkout at HEAD `81c077ea`:

- `research/modalities/km_digitize.py:1429` — `risk_times = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]` is still a hard-coded local in `run_control()`; `_cohort_to_figure_inputs()` at `:1287` takes `risk_times` as an argument. Confirmed by `sed -n '1287,1292p'` and `sed -n '1420,1440p'`.
- `research/modalities/emc_ipd_survival.py:187` — `MAX_KM_DEVIATION = 0.05`; `:182` `REQUIRE_RISK_TABLE = True`. Both were **imported and used unchanged**; the run echoes them back (`MAX_KM_DEVIATION_as_imported: 0.05`, `REQUIRE_RISK_TABLE_as_imported: true`).

Not replayed, not touched: no real curve inverted, no clinical IPD, no patient-level data produced or pooled, no IPD/recurrence/care-delivery/RT gate retry, no record or artifact census, S1/S3 not revived, W25 / GSE243553 / primary-article / Results / novelty and the NR4A Perspective untouched. `digitize_recipe()` (the only real-figure path) was **read but never called**.

## Method and inputs

Everything ran under `/tmp/claude-0/s4/`, now deleted.

- I copied `km_digitize.py` into scratch as `km_digitize_copy.py` and **made no edit to it** — `sha256 05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37`, byte-identical to `/home/user/Rare-cancers/research/modalities/km_digitize.py` (same hash, verified by one `sha256sum` over both). Exposing `risk_times` did not require editing the generator: the adapter imports the copy and calls `_emc_shaped_cohort`, `_cohort_to_figure_inputs`, `render_km`, `extract_series`, `dark_matcher`, `curve_error` and `emc_ipd_survival` directly, supplying the risk table from outside. That is strictly weaker than patching `run_control()` and leaves every guard provably as-imported.
- `research/modalities/emc_ipd_survival.py` imported from the repo path, unmodified — `sha256 a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5`.
- Adapter `sweep.py` — `sha256 28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d` (verbatim below).
- Output `out.json` — `sha256 ebc40a755bf0be6a64c42c95bc4df913e8cc67f02a9a5005fda1c35efd74b75c`.
- Synthetic cohort: `_emc_shaped_cohort()`, n=59, canonical-JSON `sha256 7deb0b9f61a765f83d8b3585b9d0e47f04da9c0788205f73b1caf71cb94deea9`. Truth by construction: 18 events, 41 censored, median 168.0, `t_max` 180.0. **Synthetic arithmetic; no row is a patient.**
- Python 3.11.15, `/usr/local/bin/python3`.

**Fixed rendering, done once.** The clean render and pixel read were executed **one time** (`render_km(true_steps, t_max=180.0)` → `extract_series(..., dark_matcher())`, 0.041 s, `read_ok: true`, `refusal: null`, 20 digitized points, `digitized sha256 48af484b…`, `curve_error_vs_truth` = `max_abs_curve_error 0.0292 / off_step 0.0012 / mean 0.0008`). The risk table cannot change pixels, so reusing that one reading across all cells *is* the fixed-rendering condition, not an approximation of it.

**Two arms per cell,** so risk-table effect and reading error are never conflated:
- `exact_arm` — exact coordinates, never rendered, never read (the artifact's `exact_coordinates_baseline` construction).
- `clean_render_arm` — the one clean render read back.

Per cell I record `events_delta_vs_truth`, `censored_delta_vs_truth`, `median_delta_vs_truth`, `internal_max_abs_km_deviation`, plus `admissible_under_the_floor` / `quality_failures` from `assess_quality` against the unmodified `MAX_KM_DEVIATION = 0.05`, and per-cell seconds.

## The grid actually run (and what was dropped)

25 cells × 2 arms = **50 reconstructions**. Rows are placed uniformly: `t_i = extent·t_max·i/(rows−1)`, first row at 0 unless the anchoring axis moves it.

| Axis | Cells | Held fixed | Confound, stated |
|---|---|---|---|
| **1 Density** | rows ∈ {2,3,5,8,13,19,25} | extent = 168/180 = 0.933 | **Row spacing moves with density** (168/(n−1)): at fixed extent, spacing is not independently controllable. Density and extent are separated; spacing is not, and cannot be, in this parameterisation. |
| **2 Extent** | extent ∈ {0.25,0.5,0.75,0.933,1.0} | rows = 8 | Same: spacing moves with extent at fixed row count. |
| **2b Confounded on purpose** | last row ∈ {24,48,96,144,168}, spacing fixed 24 | spacing | **Density and extent move together** — labelled `CONFOUNDED_…` in the output and never quoted as a clean density or extent effect. Included because "fixed spacing, shorter follow-up" is what a real journal table actually varies. |
| **3 Anchoring** | first row t₁ ∈ {0,6,11,24} × {printed, anchored} | remaining rows = the control's own 24-unit grid above t₁ | Within a pair only the first row changes, so the printed/anchored contrast is clean. **Across** t₁ values the row count also changes (t₁=24 drops the 0 and 24 rows to 7 rows), so t₁ levels are not comparable to each other. |

Anchoring definitions, mirroring `km-figure-readings.json` `recipes[0]` (`[[2,10],…]` vs `[[1.99,11],…]`) but over synthetic truth: **printed** = row at t₁ carrying the post-event count `#{time > t₁}`; **anchored** = row at t₁−0.01 carrying the pre-event count `#{time ≥ t₁}`.

**Dropped / not run, with reasons:**
- **Extent rungs below 0.25 on axis 2** — not attempted; nothing was refused, I simply did not extend the grid. NOT RUN.
- **rows = 1** — dropped by design: a one-row table is not a table, and `_interval_bounds` has no interval to walk. NOT RUN.
- **Every degraded-render scenario** (JPEG, noise, resample, thick line, gridlines, dashes, annotation boxes, second curve, `anchor_error_px`) — deliberately out of scope: the contract fixes rendering at clean. NOT RUN.
- **The JPEG branch is additionally unavailable in this container**: `python3 -c "import PIL"` → `ModuleNotFoundError: No module named 'PIL'`, and `km_digitize.jpeg_roundtrip` (call site `run_control()`, `km_digitize.py:1495-1501`) returns `None` in that case. Named dependency: **Pillow (`PIL`), not installed, any version**. No dependent branch of *my* grid needed it, so nothing of mine was stopped; I installed nothing.
- Anchoring at t₁ = 0 and t₁ = 24 are **null controls, kept and reported**: no cohort member has time exactly 0 or 24, so printed and anchored coincide by construction. A null cell is a result.

## Executed code (verbatim)

`/tmp/claude-0/s4/sweep.py`, sha256 `28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d`:

```python
#!/usr/bin/env python3
"""S4 adapter: density / extent / anchoring sweep over the SYNTHETIC control cohort.

READ-ONLY with respect to the repository. This file lives in /tmp/claude-0/s4/ and imports a
byte-identical COPY of research/modalities/km_digitize.py (sha256 verified by the caller).
No guard is changed anywhere: MAX_KM_DEVIATION and every other threshold are used as imported.

The only thing this adapter does that run_control() cannot is supply `risk_times` (and a
first-row anchoring rule) from outside, instead of the hard-coded local at km_digitize.py:1429.

Rendering is held FIXED at the `clean` scenario: the figure is rendered and read back exactly
ONCE, and every cell reuses that same digitized curve. Varying the risk table cannot change the
pixels, so a single render is not an approximation -- it is the fixed-rendering condition.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

REPO_MOD = "/home/user/Rare-cancers/research/modalities"
sys.path.insert(0, REPO_MOD)          # so the copy can find emc_ipd_survival
sys.path.insert(0, "/tmp/claude-0/s4")

import km_digitize_copy as kd          # noqa: E402
import emc_ipd_survival as ipd_mod     # noqa: E402

T_MAX = 180.0
EPS = 0.01                             # "immediately before" offset for the anchored arm


def cohort_hash(cohort):
    blob = json.dumps(cohort, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def risk_table_from_times(cohort, times):
    """Number at risk == number whose observed time is >= t (km_digitize._cohort_to_figure_inputs)."""
    return [[t, sum(1 for r in cohort if r["time"] >= t)] for t in times]


def reconstruct_cell(digitized, risk_table, truth, label):
    curve = {"id": label, "source_id": "control", "endpoint": "os",
             "population": "synthetic control cohort", "time_unit": "months",
             "digitized": digitized, "risk_table": risk_table, "total_events": None,
             "digitized_by": "S4 adapter (fixed clean render, risk table varied)"}
    t0 = time.time()
    try:
        rec = ipd_mod.reconstruct(curve)
        q = ipd_mod.assess_quality(curve, rec)
        med = ipd_mod._median_survival(ipd_mod.kaplan_meier(rec["ipd"]))
        out = {
            "n_reconstructed": rec["n_reconstructed"],
            "n_events": rec["n_events"],
            "n_censored": rec["n_censored"],
            "events_delta_vs_truth": rec["n_events"] - truth["n_events"],
            "censored_delta_vs_truth": rec["n_censored"] - truth["n_censored"],
            "median_survival": med,
            "median_delta_vs_truth": (None if med is None or truth["median_survival"] is None
                                      else round(med - truth["median_survival"], 3)),
            "internal_max_abs_km_deviation": rec["max_abs_km_deviation"],
            "admissible_under_the_floor": q["admissible"],
            "quality_failures": q["failures"],
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001 -- a crash is a RESULT and is recorded, not dropped
        out = {"error": f"{type(exc).__name__}: {exc}"}
    out["seconds"] = round(time.time() - t0, 3)
    return out


def main():
    t_start = time.time()
    cohort = kd._emc_shaped_cohort()
    truth_steps, _, censor_times = kd._cohort_to_figure_inputs(cohort, [0.0])
    truth = {
        "n_patients": len(cohort),
        "n_events": sum(1 for r in cohort if r["event"]),
        "n_censored": sum(1 for r in cohort if not r["event"]),
        "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(cohort)),
    }
    meta = {
        "cohort_sha256": cohort_hash(cohort),
        "n_cohort": len(cohort),
        "truth": truth,
        "t_max": T_MAX,
        "MAX_KM_DEVIATION_as_imported": ipd_mod.MAX_KM_DEVIATION,
        "REQUIRE_RISK_TABLE_as_imported": ipd_mod.REQUIRE_RISK_TABLE,
        "eps_for_anchored_first_row": EPS,
    }

    # ---- the fixed clean render, done ONCE -------------------------------------------------
    t0 = time.time()
    fig = kd.render_km(truth_steps, t_max=T_MAX)
    read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="clean")
    meta["render_read_seconds"] = round(time.time() - t0, 3)
    meta["read_ok"] = read["ok"]
    meta["refusal"] = read.get("refusal")
    if read["ok"]:
        meta["curve_error_vs_truth"] = kd.curve_error(read["digitized"], truth_steps, T_MAX)
        meta["digitized_sha256"] = hashlib.sha256(
            json.dumps(read["digitized"], sort_keys=True).encode()).hexdigest()
        meta["n_digitized_points"] = len(read["digitized"])
    digitized_read = read.get("digitized")
    digitized_exact = [[0.0, 1.0]] + [[t, s] for t, s in truth_steps]

    cells = []

    def run(axis, params, times, first_row_override=None):
        """One grid cell, run under BOTH arms: exact coordinates and the fixed clean render."""
        rt = risk_table_from_times(cohort, times)
        if first_row_override is not None:
            rt[0] = first_row_override
        base = {"axis": axis, **params, "risk_times": [round(t, 4) for t in times],
                "risk_table": rt, "n_rows": len(rt),
                "last_row_time": rt[-1][0], "extent_fraction": round(rt[-1][0] / T_MAX, 4),
                "spacing_note": ("uniform" if len(rt) > 2 else "two rows only")}
        base["exact_arm"] = reconstruct_cell(digitized_exact, rt, truth,
                                             f"s4_exact::{axis}::{params}")
        if digitized_read is not None:
            base["clean_render_arm"] = reconstruct_cell(digitized_read, rt, truth,
                                                        f"s4_read::{axis}::{params}")
        else:
            base["clean_render_arm"] = {"error": "clean render REFUSED; arm not run"}
        cells.append(base)

    def uniform(n_rows, extent_frac):
        last = extent_frac * T_MAX
        if n_rows == 1:
            return [0.0]
        return [round(last * i / (n_rows - 1), 6) for i in range(n_rows)]

    # AXIS 1 -- DENSITY at fixed extent 0.933 (last row 168, the committed control's extent).
    # Row spacing is 168/(n-1) and therefore MOVES with density: at fixed extent, spacing is not
    # independently controllable. Stated, not hidden.
    for n in (2, 3, 5, 8, 13, 19, 25):
        run("density@extent0.933", {"rows": n}, uniform(n, 168.0 / T_MAX))

    # AXIS 2 -- EXTENT at fixed density 8 rows. Spacing again moves with extent; density is held.
    for e in (0.25, 0.5, 0.75, 0.933, 1.0):
        run("extent@rows8", {"extent": e}, uniform(8, e))

    # AXIS 2b -- CONFOUNDED ON PURPOSE, and labelled: fixed 24-unit spacing, so shortening the
    # extent also removes rows. Density and extent move TOGETHER here. Reported as confounded.
    for last in (24.0, 48.0, 96.0, 144.0, 168.0):
        times = [24.0 * i for i in range(int(last // 24) + 1)]
        run("CONFOUNDED_spacing24_extent_and_density_move_together",
            {"last_row": last, "rows": len(times)}, times)

    # AXIS 3 -- ANCHORING of the first printed row, at fixed density/extent otherwise.
    # printed  : first row at t1 with the POST-event count  #{time > t1}
    # anchored : first row at t1-EPS with the PRE-event count #{time >= t1}
    # The remaining rows are the committed control's own 24-unit grid, those strictly above t1.
    for t1 in (0.0, 6.0, 11.0, 24.0):
        tail = [t for t in (0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0) if t > t1]
        n_post = sum(1 for r in cohort if r["time"] > t1)
        n_pre = sum(1 for r in cohort if r["time"] >= t1)
        run("anchoring", {"first_row_time": t1, "mode": "printed", "first_row_n": n_post},
            [t1] + tail, first_row_override=[t1, n_post])
        run("anchoring", {"first_row_time": t1, "mode": "anchored", "first_row_n": n_pre},
            [max(t1 - EPS, 0.0)] + tail, first_row_override=[max(t1 - EPS, 0.0), n_pre])

    meta["total_seconds"] = round(time.time() - t_start, 3)
    meta["n_cells"] = len(cells)
    print(json.dumps({"meta": meta, "cells": cells}, indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
```

Executed as `cd /tmp/claude-0/s4 && python3 sweep.py > out.json 2> err.txt` → **exit 0**, `err.txt` empty, `real 0m0.229s / user 0m0.197s / sys 0m0.031s`.

## Per-cell results

Truth: 18 events, 41 censored, median 168.0, n = 59. Deltas are reconstruction − truth. `maxdev` is `internal_max_abs_km_deviation` against the unmodified floor 0.05; `adm` is `assess_quality`'s verdict.

### Axis 1 — density, extent fixed at 0.933 (last row 168)

| rows | arm | ev Δ | cen Δ | median Δ | maxdev | adm | s |
|---|---|---|---|---|---|---|---|
| 2 | exact | +3 | −10 | −40.0 | 0.0203 | True | 0.000 |
| 2 | clean render | +4 | −12 | −40.031 | 0.0194 | True | 0.000 |
| 3 | exact | 0 | −7 | −40.0 | 0.0094 | True | 0.000 |
| 3 | clean render | +2 | −10 | −40.031 | 0.0248 | True | 0.000 |
| 5 | exact | 0 | −7 | −40.0 | 0.0069 | True | 0.000 |
| 5 | clean render | 0 | −8 | −40.031 | 0.0086 | True | 0.000 |
| **8** | **exact** | **0** | **−7** | **−40.0** | **0.0009** | True | 0.000 |
| 8 | clean render | 0 | −15 | −72.094 | 0.0183 | True | 0.002 |
| 13 | exact | 0 | −7 | −40.0 | 0.0013 | True | 0.000 |
| 13 | clean render | +1 | −20 | −84.188 | 0.0254 | True | 0.006 |
| 19 | exact | 0 | −11 | −58.0 | 0.0025 | True | 0.005 |
| 19 | clean render | 0 | −29 | −107.25 | 0.0152 | True | 0.011 |
| 25 | exact | 0 | −12 | −72.0 | 0.0014 | True | 0.005 |
| 25 | clean render | 0 | −35 | −116.25 | 0.0113 | True | 0.014 |

Reconstructed totals for the same cells (`n_reconstructed / n_events / n_censored`) — exact arm: 52/21/31, 52/18/34, 52/18/34, 52/18/34, 52/18/34, 48/18/30, 47/18/29 for rows 2→25. Clean-render arm: 51/22/29, 51/20/31, 51/18/33, 44/18/26, 40/19/21, 30/18/12, 24/18/6. Reconstructed medians, exact: 128.0 at rows 2–13, 110.0 at 19, 96.0 at 25; read: 127.97, 127.97, 127.97, 95.91, 83.81, 60.75, 51.75.

**The exact arm at rows = 8, extent 0.933 reproduces the committed artifact's `exact_coordinates_baseline` exactly: `events_delta_vs_truth 0`, `censored_delta_vs_truth −7`, `internal_max_abs_km_deviation 0.0009`.** That is an independent recomputation under me of the one figure S2 could only quote, and it is the anchor that makes the rest of this table comparable to the artifact.

### Axis 2 — extent, density fixed at 8 rows

| extent | last row | arm | ev Δ | cen Δ | median Δ | maxdev | adm |
|---|---|---|---|---|---|---|---|
| 0.25 | 45.0 | exact | +6 | −25 | −84.0 | 0.0099 | True |
| 0.25 | 45.0 | clean render | +6 | −34 | −84.188 | 0.0112 | True |
| 0.50 | 90.0 | exact | +2 | −16 | −72.0 | 0.0163 | True |
| 0.50 | 90.0 | clean render | +2 | −20 | −84.188 | 0.0144 | True |
| 0.75 | 135.0 | exact | 0 | −10 | −58.0 | 0.0222 | True |
| 0.75 | 135.0 | clean render | +1 | −15 | −72.094 | 0.0211 | True |
| 0.933 | 167.94 | exact | 0 | −7 | −40.0 | 0.0009 | True |
| 0.933 | 167.94 | clean render | 0 | −15 | −72.094 | 0.0183 | True |
| 1.00 | 180.0 | exact | 0 | −5 | −18.0 | 0.0018 | True |
| 1.00 | 180.0 | clean render | 0 | −11 | −58.031 | 0.0191 | True |

### Axis 2b — CONFOUNDED (spacing fixed at 24; density and extent move together)

| last row | rows | arm | ev Δ | cen Δ | median Δ | maxdev | adm |
|---|---|---|---|---|---|---|---|
| 24 | 2 | exact | +9 | −32 | −98.0 | 0.0099 | True |
| 24 | 2 | clean render | +9 | −32 | −84.188 | 0.0100 | True |
| 48 | 3 | exact | +5 | −24 | −84.0 | 0.0119 | True |
| 48 | 3 | clean render | +5 | −24 | −84.188 | 0.0115 | True |
| 96 | 5 | exact | +2 | −15 | −72.0 | 0.0145 | True |
| 96 | 5 | clean render | +2 | −16 | −72.094 | 0.0111 | True |
| 144 | 7 | exact | 0 | −9 | −58.0 | 0.0138 | True |
| 144 | 7 | clean render | 0 | −16 | −72.094 | 0.0243 | True |
| 168 | 8 | exact | 0 | −7 | −40.0 | 0.0009 | True |
| 168 | 8 | clean render | 0 | −15 | −72.094 | 0.0183 | True |

**This block is confounded by construction and must not be quoted as a density effect or an extent effect.**

### Axis 3 — first-row anchoring (printed vs anchored), otherwise fixed

| t₁ | mode | first row | rows | arm | ev Δ | cen Δ | median Δ | maxdev | adm |
|---|---|---|---|---|---|---|---|---|---|
| 0 | printed | (0, 59) | 8 | exact | 0 | −7 | −40.0 | 0.0009 | True |
| 0 | printed | (0, 59) | 8 | read | 0 | −15 | −72.094 | 0.0183 | True |
| 0 | anchored | (0, 59) | 8 | exact | 0 | −7 | −40.0 | 0.0009 | True |
| 0 | anchored | (0, 59) | 8 | read | 0 | −15 | −72.094 | 0.0183 | True |
| 6 | printed | (6, 56) | 8 | exact | 0 | **−10** | −40.0 | 0.0175 | True |
| 6 | printed | (6, 56) | 8 | read | 0 | **−18** | −72.094 | 0.0369 | True |
| 6 | anchored | (5.99, 57) | 8 | exact | 0 | **−9** | −40.0 | 0.0175 | True |
| 6 | anchored | (5.99, 57) | 8 | read | 0 | **−17** | −72.094 | 0.0369 | True |
| 11 | printed | (11, 53) | 8 | exact | 0 | **−13** | −40.0 | 0.0357 | True |
| 11 | printed | (11, 53) | 8 | read | 0 | **−21** | −72.094 | **0.0536** | **False** — `['km_deviation 0.0536 exceeds floor 0.05']` |
| 11 | anchored | (10.99, 54) | 8 | exact | 0 | **−12** | −40.0 | 0.0357 | True |
| 11 | anchored | (10.99, 54) | 8 | read | 0 | **−20** | −72.094 | **0.0536** | **False** — same failure |
| 24 | printed | (24, 45) | 7 | exact | −1 | −20 | −40.0 | **0.0941** | **False** |
| 24 | printed | (24, 45) | 7 | read | −1 | −28 | −72.094 | **0.1155** | **False** |
| 24 | anchored | (23.99, 45) | 7 | exact | −1 | −20 | −40.0 | 0.0941 | False |
| 24 | anchored | (23.99, 45) | 7 | read | −1 | −28 | −72.094 | 0.1155 | False |

t₁ = 0 and t₁ = 24 are the **null controls**: no cohort member has an observed time exactly there, so printed and anchored are the same table and produce byte-identical rows. They came out identical, as the construction requires.

**Measured anchoring effect, where it is non-null:** anchoring the first row recovers **exactly one censored patient** (−10 → −9 at t₁ = 6; −13 → −12 at t₁ = 11, in both arms) and changes **nothing else** — events, median and `max_abs_km_deviation` are bit-identical between the two modes. The size of the effect equals the number of cohort members whose observed time is exactly t₁ (one, in both cells).

**Runtime.** Total in-process `total_seconds` = **0.151 s** (render+read 0.041 s; per-cell reconstruction 0.000–0.014 s). Wall clock for the whole executed run 0.229 s. Nowhere near the 20-minute bound.

## Observed failures

Every failure, kept:

1. **`assess_quality` refused 6 of 50 reconstructions** on the unchanged floor — the four t₁ = 24 cells (`km_deviation 0.0941` exact / `0.1155` read) and the two t₁ = 11 clean-render cells (`0.0536`). Recorded as measured; **no guard was touched to make them pass.**
2. **Pillow (`PIL`) is not installed** in this container — `python3 -c "import PIL"` → `ModuleNotFoundError: No module named 'PIL'`. Call site `km_digitize.jpeg_roundtrip`, used by `run_control()` at `km_digitize.py:1495-1501`, which returns `None` and marks the arm skipped. No cell of my grid depends on it; the JPEG branch is stopped as unavailable and nothing was installed.
3. **No cell crashed.** The `except` in `reconstruct_cell` never fired; every cell returned a reconstruction, and `err.txt` was empty at exit 0.
4. **Determinism check flagged a false difference:** a byte re-run of `sweep.py` differed from the first — the difference is entirely the recorded `seconds` timing fields. With timings stripped, the two runs are **identical** (verified by comparing sorted canonical JSON). Recorded because it is an observed discrepancy, not because it is a real one.

## What this does and does not support

Measured, and scoped to **this control under these settings**:

- **Extent dominates the censored count in the exact arm.** Holding density at 8 rows, `censored_delta_vs_truth` moves −25 → −16 → −10 → −7 → −5 as the last printed row moves 0.25 → 1.0 of `t_max`. Even printing to the full axis does not recover everything (−5): extent is necessary, not sufficient.
- **Density is not monotone, and past a point it hurts the arm that reads pixels.** In the exact arm, going 2 → 3 rows removes an events error (+3 → 0) and everything from 3 to 13 rows sits flat at −7; 19 and 25 rows get *worse* (−11, −12). In the clean-render arm the degradation with density is severe and monotone beyond 5 rows: −8 → −15 → −20 → −29 → −35 censored, median error −40 → −116. More printed rows means more risk intervals for the recursion to force the read curve through, and small reading error inside a short interval is not absorbed. **Denser is not safer here.**
- **Anchoring is a one-patient effect in this cohort, in the direction the real-figure rationale predicts.** Anchoring the first row immediately before its printed time recovered exactly the one patient whose event sits at that time, in both arms, at both non-null t₁ values, changing nothing else.
- **The internal deviation does not police this error class.** In 44 of 50 cells `internal_max_abs_km_deviation` stayed under the 0.05 floor and `admissible` was True *while the reconstruction was losing up to 35 of 41 censorings and putting the median 116 units low*. That is the same failure mode the committed artifact already records for axis calibration, now measured on a second, independent axis — the risk table.

What this **does not** support, stated so it cannot be misread:

- **No clinical claim of any kind.** No efficacy, safety, selectivity, prognosis or therapeutic-window statement about EMC or any disease. The cohort is generated arithmetic; no row is a patient.
- **A passing cell creates no reporting requirement.** These numbers are a synthetic render read by one matcher at one clean setting, and **`⛔_direction_of_the_bound` applies to every one of them: a synthetic render is easier than a journal figure**, so each figure bounds reading error **from below**.
- **This is not a universal statement about journal figures, and not a universal lower bound for all real 8-row tables.** The single control result (the seven lost censorings included) describes this cohort's censoring pattern against this row placement. A different cohort with different late censoring would move every number in these tables.
- **A general reporting requirement remains UNKNOWN.** I measured one cohort, one shape, one renderer, one matcher, uniform row placement only. The most I can say inside stated limits is: *for this synthetic 59-patient cohort at clean rendering, no number of printed rows recovered the censored count when the table stopped at 0.933·t_max, and increasing row count beyond 5 made the read arm's censored count worse.* That is a statement about this instrument, not a rule for journals.

## Validation evidence

All **RUN**, `/tmp/claude-0/s4`, Python 3.11.15 (`/usr/local/bin/python3`), repo HEAD `81c077ea1461d291bd2f031e40f98028c4de583e`, no network:

```
$ sha256sum km_digitize_copy.py /home/user/Rare-cancers/research/modalities/km_digitize.py \
            /home/user/Rare-cancers/research/modalities/emc_ipd_survival.py
05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37  km_digitize_copy.py
05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37  .../km_digitize.py
a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5  .../emc_ipd_survival.py

$ sha256sum sweep.py
28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d  sweep.py

$ time python3 sweep.py > out.json 2> err.txt ; echo EXIT=$?
real 0m0.229s   user 0m0.197s   sys 0m0.031s
EXIT=0            (err.txt empty)

$ sha256sum out.json
ebc40a755bf0be6a64c42c95bc4df913e8cc67f02a9a5005fda1c35efd74b75c  out.json

meta: cohort_sha256 7deb0b9f61a765f83d8b3585b9d0e47f04da9c0788205f73b1caf71cb94deea9
      n_cohort 59, truth {n_events 18, n_censored 41, median 168.0}, t_max 180.0
      MAX_KM_DEVIATION_as_imported 0.05, REQUIRE_RISK_TABLE_as_imported true
      read_ok true, refusal null, n_digitized_points 20
      digitized_sha256 48af484b67124d1553ed0ec98ea175657c6239fa6b32d000572b2813bd5ed773
      curve_error_vs_truth {max 0.0292, off_step 0.0012, mean 0.0008, grid_points 401}
      render_read_seconds 0.041, total_seconds 0.151, n_cells 25

$ python3 -c "import PIL"
ModuleNotFoundError: No module named 'PIL'

$ du -sh /tmp/claude-0/s4  ->  300K       $ df -h /  ->  20G avail (start and end)
$ rm -rf /tmp/claude-0/s4  ->  scratch removed (verified absent from /tmp/claude-0/ listing)
```

`git status --porcelain` empty at start and at end; HEAD unchanged. No guard, threshold or repository file was modified anywhere.

## Limitations

One synthetic cohort (n = 59, 18 events, heavy terminal censoring with five patients at t = 180), one renderer (`render_km` defaults), one matcher (`dark_matcher()` defaults), uniform row placement only, and a single clean render reused across cells. Reading error is therefore a **fixed** draw, not a distribution: I did not repeat the render, so between-render variability of the clean-arm numbers is **UNKNOWN**. Spacing could not be held fixed while varying density or extent in this parameterisation, and the one block where spacing *is* fixed is confounded and labelled as such. Anchoring was tested at four first-row times, two of which are null by construction, and only in cohorts where exactly one patient sits at the anchor time — the effect size measured (+1 censored) is that count, not a general magnitude. The anchoring arms keep the digitized curve starting at t = 0 even when the first printed row is t₁ > 0, unlike the real stacchiotti2013 figure whose axis itself starts at 2; that is a stated difference from the real-figure case and I did not model an axis that starts late. I did not re-run `run_control()` end to end, so I did not verify the committed artifact as a whole — only that my exact arm at rows 8 / extent 0.933 reproduces its `exact_coordinates_baseline` triple. Every figure here bounds real-figure reading error **from below** (`⛔_direction_of_the_bound`). Nothing here inverts a real curve or touches patient data.

## Stop condition

Set: stop at acceptance (measured per-cell output retained), at the 20-minute experiment bound, or at ~40 tool calls. **Met at acceptance** — 25 cells × 2 arms executed, exit 0, code, hashes, parameters, runtimes and all six floor failures plus the named missing `PIL` retained above. Scratch deleted; this report is the durable record.

## Tool-call and wall-clock count actually used

**12 tool calls.** Wall clock `05:47:17Z → 05:49:59Z` ≈ **2.7 minutes** of tool time; **executed experiment wall-clock 0.229 s**, against a 20-minute bound. No padding.

## Next concrete action

One successor, **not authorized by this report and not started by me**: repeat the density and extent axes with the render *repeated* (a fresh `render_km` + `extract_series` per cell, and across ≥ 2 cohort shapes with different late-censoring patterns), to convert the clean-render arm's single fixed reading draw into a distribution and test whether "denser tables make the read arm worse beyond 5 rows" survives re-rendering and a second cohort. Until that runs, that trend is a **single-draw observation on one cohort**, and a general reporting requirement stays **UNKNOWN**.
