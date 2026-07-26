# GCP GPU — hard facts (verified 2026-07-22, read BEFORE any GCP GPU work)

These are empirically verified, expensive-to-relearn facts about THIS GCP project
(`project-a7ebde30-e2ed-4b8d-9a9`). Every one cost real debugging time. Check them
before diagnosing a GPU provisioning/quota problem.

## 1. We have a **1-GPU TOTAL** quota — this is the binding limit

- **`GPUS_ALL_REGIONS = 1`** (project-global quota) is THE binding cap: **at most 1 GPU
  concurrently, across ALL regions and ALL GPU types (spot or on-demand).** Confirmed
  `limit=1.0 usage=1.0` on 2026-07-22.
- The **per-type regional** quotas are REAL but **NON-binding** because the global 1 caps
  below them:
  - `NVIDIA_L4_GPUS` (on-demand L4, us-central1) = **1**
  - `PREEMPTIBLE_NVIDIA_L4_GPUS` (spot L4, us-central1) = **3**  ← looks like 3, but you can
    never use more than 1 because GPUS_ALL_REGIONS=1 wins.
- **Consequence:** NEVER assume you can run >1 GPU job concurrently. Replicate seeds
  (0/1/2), multiple edges, or spot+on-demand together all run **strictly sequentially**.
  "The spot L4 quota is 3 so we can fan out" is **WRONG** — the global cap is 1.
- **How to check:** `gcp-quota-check.yml` prints BOTH the global `GPUS_ALL_REGIONS` and the
  per-type regional rows. Read GPUS_ALL_REGIONS for the real answer.

## 2. Quota ≠ capacity; and the zombie test

- **Quota** = your allowed ceiling. **Capacity** = whether GCE physically has an idle GPU to
  hand you right now. They are independent: quota can be free while capacity is exhausted
  (`ZONE_RESOURCE_POOL_EXHAUSTED`), even for on-demand at peak.
- **Zombie discriminator (definitive):** a zombie VM holding a GPU shows **quota usage ≥ 1**.
  If `NVIDIA_L4_GPUS`/`PREEMPTIBLE_NVIDIA_L4_GPUS` **usage = 0** AND no `gcp-ternary-*` VM is
  listed, there is **no zombie** — a provisioning failure then is real capacity or a bad
  request, NOT a zombie. `mode=tail` and `gcp-reap-vms.yml` both print live VMs + quota usage.

## 3. On-demand (`provisioning=standard`) create REQUIRES `--instance-termination-action`

- GCP requires `--instance-termination-action` (STOP or DELETE) **whenever
  `--max-run-duration` is set** — for BOTH spot AND standard VMs. (The old belief that
  termination-action is "spot-only" is WRONG; standard supports it.)
- Bug fixed 2026-07-22 in `gpu-ternary-fep-gcp.yml`: the standard branch omitted it, so every
  on-demand create **failed request-validation** and the leg had NEVER actually run on-demand.
  Both provisioning branches must carry `--instance-termination-action=DELETE`.

## 3b. `max-run-duration` CANNOT be changed on a RUNNING instance — the boundary is fixed

- Measured 2026-07-26 on a **decoy** e2-micro (`gcp-quota-check.yml`), never on a live leg. Create at
  `--max-run-duration=7200s`, then `gcloud compute instances set-scheduling --max-run-duration=259200s`:

  ```
  ERROR: (gcloud.compute.instances.set-scheduling) Could not fetch resource:
   - Max run duration cannot be changed while the instance is running.
  ```

  rc=1, duration unchanged at 7200, instance still RUNNING (so the attempt is at least harmless).
- **Consequence, and it is a planning constraint not a bug:** a VM's cap is fixed at CREATE time. When a leg is
  going to outlive its cap you cannot buy more time later — you get a boundary, the leg resumes from its last
  committed checkpoint on a fresh VM, and the cost is the **detection latency**, not the extension.
- **So set the cap correctly at create.** `144000s` (40 h) is validated as acceptable at create time. A full
  ternary leg is ~2800 iterations at ~56.5 s/iter ≈ **44 h of MD**, so 40 h does NOT span a fresh leg and one
  boundary is structural. Validate a larger create-time value before assuming it is allowed.
- **What IS recoverable is the latency.** Recovery runs off the watchdog cron, which GitHub delivers at ~2–4 h
  intervals for this repo regardless of the expression. Dispatching `ternary-leg-watchdog.yml` by hand the moment
  the VM disappears turns 2–4 h of dead wall clock into minutes — which matters on GCP specifically, where the
  credits are free and expiring so **wall clock is the scarce resource, not money**.
- A `mode=extend` was built for this and then **removed**, because the operation can never succeed on a running
  instance. Kept here as the fact rather than as dead code that invites a retry.

## 4. "L4 stocked out" in a launcher log is NOT proof of capacity exhaustion

- The provision loop historically labeled ANY non-quota create failure as "stocked out",
  which masked a **malformed-request** bug as a capacity problem (see #3). The workflow now
  **echoes the real gcloud error** on each failed create (`ERROR/exhausted/Invalid/
  required/termination/...`). Read that line before concluding "capacity."
- Sanity check on any provisioning stall: **spot working but on-demand failing is backwards**
  (on-demand is normally EASIER to get than spot). That pattern means a broken command, not
  capacity.

## 5. us-central1 ONLY for L4/G2

- This project has L4/G2 quota **only in us-central1**. Diversify across zones a/b/c/f for
  spot-capacity resilience; never add other regions (they have no quota → wasted attempts).

## 6. VMs self-delete on exit (IAM granted 2026-07-22)

- The default compute SA (`878095411563-compute@developer.gserviceaccount.com`) was granted
  a custom role with `compute.instances.delete` + `compute.instances.get`, so VMs now
  self-delete on graceful exit → a finished/dead leg shows `live_vms=0` (no zombie left).
- Backstops if self-delete ever fails: `--max-run-duration=25200s` (7h auto-DELETE) +
  `gcp-reap-vms.yml` (project-wide universal killer; `mode=reap` deletes dead VMs always and
  RUNNING VMs older than `max_age_min`; `mode=dry_run` lists only).

## Quick command reference (all via GitHub Actions, WIF auth)

- **Quota (global + regional):** dispatch `gcp-quota-check.yml`.
- **List VMs + reap strays:** `gcp-reap-vms.yml` (`mode=dry_run` to list, `mode=reap` to kill;
  `prefix=gcp-ternary-`, `max_age_min=20` protects a just-launched leg).
- **Live leg state (VMs, quota, preemption ops, run log):** `gpu-ternary-fep-gcp.yml mode=tail`.
- **On-demand (non-preemptible) run:** `gpu-ternary-fep-gcp.yml mode=run provisioning=standard`
  (+ `force_rerun=1` to bypass the idempotent-skip, else it exits without resuming).
