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
