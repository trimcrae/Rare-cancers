# R1 — original commands, exit codes, stdout and stderr

Every exit code below was emitted by the shell, captured with `echo "EXIT=$?"` immediately after the
command and **not** through a pipe. Nothing is transcribed from memory.

Environment: `/home/user/Rare-cancers`, HEAD `3e833d982f0c057804ec6a67cea64dfb1a68bfdf`,
`python3` = `/usr/local/bin/python3` (3.11.15), 2026-09-08T19:21–19:26Z. No network call of any kind,
no paid API, no GPU, no source fetch, no test suite, no preflight, no commit, no push.

## 1 — inputs pinned before the run

```
$ sha256sum research/modalities/km_digitize.py research/modalities/emc_ipd_survival.py
05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37  research/modalities/km_digitize.py
a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5  research/modalities/emc_ipd_survival.py
$ git rev-parse HEAD
3e833d982f0c057804ec6a67cea64dfb1a68bfdf
```

Both hashes are identical to the values S4 pinned, so the generator and the survival module are
unchanged since that run.

## 2 — the experiment

```
$ date -u > RUN-01.status
$ { time python3 r1_sweep.py > RUN-01.stdout.json 2> RUN-01.stderr.txt ; } 2>> RUN-01.status
$ echo "EXIT=$?" >> RUN-01.status
$ cat RUN-01.status
Tue Sep  8 19:22:44 UTC 2026

real	0m0.413s
user	0m0.397s
sys	0m0.016s
EXIT=0

$ wc -c RUN-01.stderr.txt RUN-01.stdout.json
    0 RUN-01.stderr.txt
72838 RUN-01.stdout.json
```

`EXIT=0` is the harness's own return value and carries the sentinel verdict: `r1_sweep.py` returns
**0 only if the sentinel reproduces the committed baseline** and **3 on any sentinel mismatch**
(`main()`'s final `return`). It returned 0 on the first and only execution. **stderr was empty
(0 bytes).** The run was **not** repeated, retried or corrected; there is exactly one run.

## 3 — cross-check of the clean reading against S4's independent run

```
$ python3 - <<'PY'   (ad-hoc, stdout below)
   render once with the repository generator and hash the reading S4's way
PY
S4-style hash: 48af484b67124d1553ed0ec98ea175657c6239fa6b32d000572b2813bd5ed773
EXIT=0
```

That is byte-for-byte S4's recorded `digitized_sha256`, so the fixed clean render/read is
reproducible across the two independent runs. R1's own `meta.digitized_sha256`
(`61032c8c924e0d2024ec4f9d45e3cc872882ecbc93f656c9b478a161ef99580a`) differs **only** because this
harness hashes with compact JSON separators.

## 4 — inputs re-verified after the run, and repository cleanliness

```
$ sha256sum research/modalities/km_digitize.py research/modalities/emc_ipd_survival.py \
            research/modalities/km-digitization-error.json research/modalities/km-figure-readings.json
05aeeb4b8f2150f65cf95d8320c0f5dac647f928a42ed2ebba40276ae1a7dd37  .../km_digitize.py
a82420f026547a27d5dbe571faa8325bdf4fd1930281eec163db2c20157f5aa5  .../emc_ipd_survival.py
966f670636b484ed122ee4724b1c2917b0f50892c9d5b2878294db29ee5a4dea  .../km-digitization-error.json
a34f5de3375f08d05cf5b249ed4ef9c0077ad4d5e31d4ee35fd3b683a73b1499  .../km-figure-readings.json
EXIT=0
$ git status --porcelain research/modalities/     ->  (no output; 0 lines)
```

`km_digitize.py` and `emc_ipd_survival.py` hash exactly as they did before the run. **The committed
results remain byte-identifiable**: `km-digitization-error.json` was never opened for writing, and no
file under `research/modalities/` is modified. `km-figure-readings.json` was read for the SHAPE of a
printed risk table only; `digitize_recipe()` and every real-figure path were never called.

## 5 — the exact changed code

**No repository file was changed, so there is no diff against `research/modalities/`.** The change
this experiment needs — supplying `risk_times` from outside instead of the hard-coded local at
`km_digitize.py:1429` — is made entirely in the new harness `r1_sweep.py` in this directory, which
imports both repository modules unmodified and uses `MAX_KM_DEVIATION` and `REQUIRE_RISK_TABLE`
exactly as imported (echoed back in `RUN-01.stdout.json` as `0.05` and `true`). The equivalent-diff
statement, stated precisely:

```
km_digitize.py:1429   risk_times = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]   # UNCHANGED in the repo
r1_sweep.py           risk_times(R, L) = [L*i/(R-1) for i in range(R)]                   # supplied externally
```

At `R = 8, L = 168.0` the harness's expression evaluates to the repository's literal list exactly —
that identity is the sentinel, and it is asserted programmatically, not by eye.

## 6 — files retained here

| file | what it is |
|---|---|
| `GRID-DEFINITION.md` | the grid resolved mathematically, written before any measurement |
| `r1_sweep.py` | the exact executed harness |
| `RUN-01.stdout.json` | the complete original stdout of the single run (52 cells × 2 arms) |
| `RUN-01.stderr.txt` | the original stderr — empty, 0 bytes |
| `RUN-01.status` | `date -u`, `time` output and the emitted `EXIT=0` |
| `CELLS-TABLE.md` | every cell's parameters and truth comparisons |
| `PIVOTS.md` | R × L pivots per arm for each recorded quantity |
| `RESULT.md` | the result block and interpretation |
| `SHA256SUMS.txt` | hashes of every file above |

Per CLAUDE.md §8 this directory is campaign task evidence and stays intact until a directory-specific
local receipt verifies it.
