# Killing the O(n²) commit — design, for review before it is built

**Status: DESIGN ONLY. Nothing in the commit path has been changed.** trimcrae asked to see the design first
if the file format fought the obvious approach. It does, but not in the way that matters — the measurement
below says a byte-level incremental upload is neither possible nor *necessary*.

---

## 1. What was measured (2026-07-31, 7:41 PM ET, real S3 objects)

Split by file type across the four live 5a-KS legs. The commit stores an openmmtools **analysis** file (`.nc`)
and a **checkpoint** file (`.chk`):

| leg | phase | largest single `.chk` | largest single `.nc` |
|---|---|---|---|
| nr4a1_r0 | warmup done | **1231.1 MiB** | 110.3 MiB |
| nr4a1_r1 | warmup | **1243.4 MiB** | 110.3 MiB |
| nr4a3_r1 | production/80 | **877.2 MiB** | 107.2 MiB |
| nr4a3_r0 | production, 91 % | 1474.0 MiB | **4089.5 MiB** |

Two different growth laws, and confusing them would have sent the work at the wrong file:

* **`.chk` — grows during WARMUP.** It accumulates **one full-coordinate frame per checkpoint interval**, and
  every commit re-uploads all of them. The arithmetic closes exactly: 12 replicas × 147,788 atoms × 3 × 4 B ×
  2 (positions + velocities) = **40.6 MiB** predicted per frame, against **49.2 / 49.7 MiB** observed
  (`1231.1 / 25` and `1243.4 / 25` frames at interval 64 over a 1600-iteration warmup). The remainder is
  netCDF overhead and box vectors.
* **`.nc` — flat in warmup (~110 MiB), grows in PRODUCTION** (4.1 GiB at 91 %), because that is where the
  trajectory lands at `positions_write_frequency` (`RBFE_POSITIONS_WRITE_PS = 50` ps).

**A resume reads only the LAST checkpoint frame.** Every earlier frame in the `.chk` is re-uploaded on every
commit and never read by anything.

### Why this makes the interval change worse than reported

Halving the interval doubles the commit COUNT *and* doubles the frames inside each `.chk`:

| interval | commits | final `.chk` | total `.chk` uploaded over warmup |
|---|---|---|---|
| 64 | 25 | 1.2 GiB | **15.6 GiB** |
| 32 | 50 | 2.4 GiB | **61.0 GiB** |

**≈4× the bytes, not 2×.** The revert (STRATEGY Appendix A 63) was conservative for the right reason and
understated the cost.

---

## 2. The format does fight a true byte-level append — evidence, not assertion

The `.nc`/`.chk` are **netCDF-4**, i.e. HDF5 containers. HDF5 is *not* append-only at the byte level: writing
new data updates chunk B-trees, the object header and free-space manager, all of which live at file offsets
that are not the tail. So "upload the new bytes and concatenate on restore" is **unsound** — it would
reconstruct a file whose internal structures disagree with its contents, and the failure mode is a corrupt
resume, which is the one failure this lane cannot absorb. (netCDF-3 *record* variables would permit it; we do
not use netCDF-3, and switching would forfeit compression and the openmmtools reporter contract.)

**But incremental upload is the wrong target anyway.** The growth is not new science accumulating — it is
*restart frames nobody reads* being re-sent. Fix the payload, not the transport.

---

## 3. Proposed fix — make the `.chk` flat

The NR-V04 lane is the existence proof trimcrae supplied: its checkpoint is a **fixed ~45.6 MiB `state.xml`**,
flat rather than cumulative, and that is the lane whose shorter cadence paid off tonight. A single-frame
`.chk` for this lane is **~49 MiB** — the same shape and nearly the same size.

**Where it goes.** `_BaseCommitStore.commit` already snapshots the pair to a temp dir and validates *before*
`_persist`. That snapshot is the natural and safest place: the live reporter files are never touched, so a
bug cannot corrupt the running simulation — it can only produce a bad *upload*, which validation then rejects.

```
commit(phase, iteration, nc, chk, interval):
    snapshot nc, chk -> tmp                     # unchanged
    prune_chk_to_last_frame(tmp/chk)            # NEW: keep the final checkpoint frame only
    validate_reporter_pair(tmp/nc, tmp/chk, …)  # unchanged — must still pass
    persist(...)                                # unchanged
```

**Expected effect**: warmup `.chk` per commit goes 1231 MiB → ~49 MiB (~25×), and total warmup upload 15.6 GiB
→ ~1.2 GiB. At interval 32 it becomes ~2.4 GiB total — *less than a quarter of what interval 64 costs today*,
which is what would make the halving free.

### What has to be proven before it goes near a billing leg

1. **openmmtools accepts a single-frame `.chk` on resume.** Its checkpoint reader indexes frames by
   `iteration // checkpoint_interval`; a pruned file must either preserve that indexing or the restore path
   must be taught the offset. **This is the load-bearing unknown and the reason this is a design and not a
   diff.**
2. **`validate_reporter_pair` still means what it means.** It checks the `.chk`'s last full frame against the
   expected iteration. It must keep failing on a genuinely bad pair, not merely pass because there is one
   frame.
3. **`effective_interval` / `read_checkpoint_interval` still read the interval** from a pruned file.
4. **A real resume from a pruned chain**, offline, before any rental.

### Ladder (CLAUDE.md §6, in full)

`LocalCommitStore` round-trip test (commit → prune → restore → compare) → `mode=smoke` → **one real leg** →
anything wider. Four legs are sitting at 91 %, 59 %, 46 % and 44 % on the current resume path; none of them
runs this until a fresh leg has proved it end to end.

### Cheaper fallbacks, if pruning proves unsafe

* **Do not upload the `.chk` on every commit.** The `.nc` alone advances the analysis; a `.chk` every *k*
  commits bounds re-work to *k* intervals instead of losing everything. Strictly weaker, but a pure
  scheduling change with no format risk.
* **Drop velocities from the checkpoint** (`velocities_write_frequency` is already unset for the trajectory;
  the checkpoint frame carries them regardless) — halves the frame at the cost of a velocity-rescaled restart.
* **Prune old *generations*** from S3. Saves storage, not upload — the O(n²) is unaffected.

---

## 4. `COMMIT_OVERHEAD_S` — not re-derived yet, deliberately

`COMMIT_OVERHEAD_S = 23.0` was calibrated on an "~25 MB .nc/.chk pair" and the real median is **699.5 MiB**,
so it is stale by ~28×, and `MAX_COMMIT_OVERHEAD_FRAC = 0.05` is being evaluated against it.

`rbfe_spot_checkpoint.commit` now self-times and prints
`[barrier] commit <phase>@<iter> persisted N MiB in Ns`; `setup_tax.commit_cost` parses it. **No commit has
been observed yet** — the four legs are running code from before the instrumentation, and there has been no
re-placement in ~2 h. Per §1 the constant will be **derived from that measurement, not typed**, so it stays at
23.0 with this note attached rather than being replaced by a guess.
