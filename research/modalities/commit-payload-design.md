---
id: DOC-COMMIT-PAYLOAD-DESIGN
title: Killing the O(n²) commit — measured, answered, and wired behind a switch
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Killing the O(n²) commit — measured, answered, and wired behind a switch

**Status: RUNG 1 ANSWERED — `PRUNING IS SAFE` (GH run 30676071569, $0, no rental). The prune is now in
`commit()` behind `RBFE_PRUNE_CHK`, DEFAULT OFF.** Nothing prunes until a dispatch asks, so the four legs
in flight when this landed are unaffected as a property of the code rather than a promise about sequencing.
The experiment is [`chk_prune_roundtrip.py`](./chk_prune_roundtrip.py); the prune itself has one home in
[`chk_prune.py`](./chk_prune.py), which the commit path and the experiment both import — so what was proven
and what runs cannot drift apart.

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

### What had to be proven before it went near a billing leg — all four, measured

Run **GH 30676071569**, on `triskit23/ternary-fep` (the parity image), CPU only, $0, no rental.

| # | question | answer |
|---|---|---|
| 1 | does openmmtools accept a single-frame `.chk` on resume? | **yes** — `from_storage` resumed at the right iteration, not 0, and the coordinates were **bit-identical** to an unpruned resume of the same run (`max Δ = 0.0 nm`) |
| 2 | does `validate_reporter_pair` still mean what it means? | **now it does — it did not before**; see §5 |
| 3 | does `effective_interval` / `read_checkpoint_interval` still read the interval? | **yes**, 64 read back from the pruned real pair |
| 4 | a real resume from a pruned CHAIN, offline? | **yes** — prune → commit → restore → resume → run on → prune → commit → restore → resume |

Measured alongside, and the reason the answer is trusted rather than assumed:

* **Storage mechanism, at the real 5a-KS shape** (12 × 147,788 × 3): 6 frames = 121.8 MiB → 1 frame =
  20.3 MiB, **6.0×**, against a **contiguous negative control at 1.0×**. The saving is the chunking, not the
  measurement.
* **A REAL committed 5a-KS warmup pair** (`5aks_d0_to_d__ternary_nr4a1_r0_dt4.0fs_wu1.0_5aks`, iter 1600,
  interval 64): **1231.1 MiB → 47.6 MiB, 25.88×, in ~4 s.** That is the whole §1 table's largest `.chk`
  reduced to the one frame anything ever reads, and it lands within 3 % of the 49 MiB predicted above.
* **Two deliberately-broken checkpoints are rejected**, which is what makes the pass mean anything.

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


---

## 5. ★★ WHAT THE NEGATIVE CONTROL FOUND, WHICH MATTERS MORE THAN THE PRUNE

Three runs returned `INCONCLUSIVE` before the verdict, all on the same check: a checkpoint built so that the
resume frame **does not exist** passed `validate_reporter_pair` unchanged. The instrumented run
(**GH 30675795333**) says why, and it is not what the first two hypotheses assumed:

```
source .chk        dim=5 frames=[0,1,2,3,4]
control#1 index-0  dim=1 frames=[0]      <- reader asked for index 4
control#2 no-frame dim=0 frames=[]       <- reader asked for index 4
naive_last_iteration_checkpoint  8       <- returned 8 on BOTH broken files
naive_frame_max_abs_nm           0.0
naive_frame_is_masked            False
```

1. **`read_last_iteration(last_checkpoint=True)` is arithmetic on the ANALYSIS file** —
   `last_iteration // interval * interval`. It never consults the checkpoint, so it returns the expected
   iteration whatever the `.chk` contains, including nothing.
2. **`read_sampler_states(iteration=N)` for a frame that does not exist raises nothing and returns no fill.**
   It returns an **unmasked array of ZEROS**, at the right shape, with the right replica count, alongside a
   working `read_energies`.

So the frame-magnitude check added after the first failure could not see it either: zeros are
indistinguishable from ordinary small coordinates by magnitude. **This is not a pruning problem.** It means
`commit()`'s "the pair is VALIDATED before it is persisted" and `restore_latest`'s "a bad generation is
rejected and we fall back" were both resting on *readability* rather than *content* — and a resume from such
a generation would start every replica with all atoms at the origin, silently.

Closed by `rbfe_spot_checkpoint.positions_are_unusable`, consulted per replica inside
`validate_reporter_pair`: a frame is unusable if it is absent, empty, masked, non-finite, at fill magnitude,
or **spatially degenerate** (every atom of a >1-atom system at the same point). Like the magnitude sentinel,
the degeneracy clause is *incapable* of a false reject, which is what makes it safe on a live commit path.
Pinned by [`tests/test_checkpoint_fill_guard.py`](./tests/test_checkpoint_fill_guard.py).

---

## 6. Where it goes next

`mode=smoke` → **one FRESH leg** with `RBFE_PRUNE_CHK=1` → wider. No leg already in flight runs this: the
switch is off by default, and the four sitting at 91 %, 59 %, 46 % and 44 % are not resumed into it.
Re-testing interval **32** belongs after the payload is flat, not before — at 25.88× the halving costs
~2.4 GiB of `.chk` across a warmup instead of 61.0 GiB, which is what would make it free.
