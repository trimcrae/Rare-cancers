# MF1 shared-integration execution record — retention of already-executed admitted work

**2026-09-08, parent. Mechanical retention. ⛔ Not a new scientific or test run, not an additional MF1
repair, not a new audit. Nothing was rerun and no old command is presented as contemporaneous
evidence.**

**Integrated pin: `a6a21fc591d2451038cdf53449b91e3990d59cfb`.**
**Source pin the work was performed against: `c6d97dcc2043bd2a21c749339637286915a29a82`** (the value
printed by `git rev-parse HEAD` immediately before the census invocation).

**Patch source:** `MF1-repair/patches/CURRENT-SUMMARY-PATCHES.md`, **11,940 B, sha256
`d455f14daabe8937c26233c74ebc05e28bd011d52b3a137c5339de713074658a`** — verified in the working tree
and byte-identical at `01dd5a211`.

---

## ⛔ Precise limitation — which original streams were NOT saved

**Two of the three admitted operations were run without redirecting their streams to files, so no
original stdout/stderr/exit file exists for them.** They are named here rather than reconstructed:

1. **The 13-edit uniqueness verification and application.** Ran as inline Python; its per-target
   occurrence counts and the applied-edit tally were printed to the tool result only. ⛔ **No original
   stream file exists.**
2. **The view check → write-views → check sequence.** All three invocations were redirected to
   `/dev/null`; only their exit codes and the `[G2]` counts were read. ⛔ **No original stream files
   exist.**

⛔ **I have not recreated a command line and labelled it as an original log**, and the narrative in the
commit message is **not** an execution log. What survives from those two operations is the committed
result itself plus the exact target data listed below.

⭐ **What DOES survive as genuine originals** is in `originals/` and was copied byte-for-byte from the
files written at execution time:
- `instrument_census.stdout.txt` — 1,472 B, the real stdout of the admitted census invocation
- `instrument_census.stderr.txt` — **0 B, genuinely empty at execution**
- `instrument_census.exit.txt` — `0`, the exit code read at the time
- `patch-targets-as-applied.json` — 4,498 B, the exact OLD/NEW target pairs the application used

---

## The three operations, as actually performed

**1 · Patch application — 13 edits.** Each target's uniqueness was re-verified immediately before
replacement and **every one returned exactly 1 occurrence**; each replacement was applied with
`count=1` under an assertion that would have raised on any other count. Targets: P1 and P2 in
`systems/graph/publications.json`; P3a, P3b, P3c, P4a, P4b, P4c, P5, P6a and P6b in
`research/manuscripts/nr4a3-program-map.md`; **plus the two extra P3b repetitions** the patch file
flagged at ~2416 (`R11` row) and ~3238 (dependency row) but deliberately did not transcribe — located
by searching the withdrawn quantity, each confirmed unique, each given a matching withdrawal.
`publications.json` was re-parsed as JSON after editing and is valid. A post-application scan found
**zero residual instances of the 0.65 kcal/mol figure asserted as a bound**.

**2 · Instrument census — the one admitted metadata regeneration.**
`python3 research/modalities/instrument_census.py`, stdout and stderr redirected to files, **EXIT=0**,
**stderr 0 bytes**. It propagated **V5**, **V16** and the **R5 pose row**. ⛔ The census was never
hand-edited.

**3 · Views.** `systems_check.py --check` showed **3 `[G2]` stale views** caused by the graph edit;
`--write-views` exited 0; a re-check returned **`[G2]` = 0**. ⚠ Streams not saved, as stated above.

## ⚠ Dirty inputs at execution time
The working tree was **not clean**. At the census invocation it carried the in-flight edits of the
concurrently running P-ST and TD1 owners and the previously committed FO/FP work. **The census reads
`research/modalities/` and the roadmap, and the seven changed files are exactly those listed below —
no other lane's file was written by this integration.**

## Changed-file / target map at the integrated pin

| file | bytes | blob | what changed |
|---|---:|---|---|
| `systems/graph/publications.json` | 63,825 | `06693084…` | P1, P2 |
| `research/manuscripts/nr4a3-program-map.md` | 618,584 | `ae972fab…` | P3a-c, P4a-c, P5, P6a-b + 2 extra P3b repetitions |
| `research/modalities/instrument-census.json` | 30,692 | `165e5235…` | regenerated (V5, V16, R5 pose) |
| `research/modalities/instrument-census.md` | 21,835 | `bbf8c4d5…` | regenerated (V5, V16, R5 pose) |
| `systems/views/L3-publications.md` | 97,109 | `fc6c934d…` | regenerated from graph |
| `systems/views/L2-rt-methods-paper.md` | 8,584 | `baa3dd2e…` | regenerated from graph |
| `systems/views/L2-rt-partner-strat.md` | 20,690 | `91eba97c…` | regenerated from graph |

Seven files, 36 insertions and 28 deletions.

⚠ **MF1 final scientific clearance remains HOLD.** This record retains execution provenance only; it
clears no gate and begins no revision.
