# Cheap-GPU migration plan — exact accounts, steps, and free-credit offers

**Goal:** move the NR4A3 MD/FEP fleet off AWS SageMaker onto cheaper (or free) GPU before the Stage-2 fan-out.
The current pilot run finishes on AWS untouched; **nothing new kicks off until this is set up.**

> **Sibling doc:** this is *which GPU / what it costs per hour*. For *how fast and how many sims per GPU we
> drive it* — NVIDIA-MPS GPU-packing, $/ns hardware choice, HMR/precision, energy-only `.nc`, and every other
> throughput/cost lever with its status + gate — see **[md-throughput-optimizations.md](./md-throughput-optimizations.md)**
> (deep-dive ledger, 2026-07-16). The two decisions compose: a faster card with idle SMs packs *more* MPS
> processes, so pick the matrix GPU by measured **$/ns**, not $/hr.

**What's already scaffolded (in `research/modalities/`):** a provider-agnostic harness (`gpu_backend.py`),
the auto-teardown guarantee so no provider ever idles a GPU on the meter (`autoteardown.py`), an S3-compatible
checkpoint bridge so compute is stateless and swappable (`object_store.py`), a portable job container
(`research/compute/Dockerfile.mdjob`), and the ACCESS free-allocation draft (`access-allocation-request.md`).
21 unit tests pass. **Only the real per-provider `submit()` calls remain — those need live accounts, which is
what this doc is for.**

> **★★★ VAST.AI BACKEND VALIDATED END-TO-END 2026-07-22 (`fusion-cpu-extras.yml` task=vast_smoke).** The full
> lifecycle now runs live against the Vast REST API from CI: **auth → search (GET /search/asks/, 63 verified
> single-GPU offers; pool = RTX 4090 ×8 / 5090 / PRO 6000 / 3090 / A100 SXM4 / H200) → client-side model pick
> (RTX 4090, 24564 MB, ~$0.20/hr) → create (PUT /asks/{id}/) → status=running → destroy (DELETE
> /instances/{id}/) → 0 instances left up** (anti-idle guarantee confirmed). Total smoke spend: fractions of a
> cent. **Three live-API gotchas the smoke caught + fixed** (all in `gpu_backend.py`): (1) per-key **2FA-required
> toggle** must be OFF or every call 401s "requires Two Factor Authentication" (account-side, not a scope);
> (2) endpoints drifted — list is `/api/v1/instances/` (the client now **auto-follows** Vast's own
> `410 deprecated_endpoint` "Use … instead" redirect), search is `GET /api/v0/search/asks/?q=<json>` (NOT
> /bundles/ or /offers/), create is `PUT /api/v0/asks/{id}/` (NOT POST /instances/); (3) a **server-side
> gpu_name filter silently returns 0** — the model is now chosen client-side (substring + fallback) and the VRAM
> floor is relaxed ~1 GB (a 4090 reports 24564 MB). **STATUS: Vast is production-ready** for the wide-parallel
> fan-out (each leg = an independent rented host → true N-wide, no shared-pool wall). Remaining before a real
> campaign: point `JobSpec` at the MD/RBFE container image + wire `object_store` checkpoints to R2/S3 (the job
> already checkpoints per-unit, so interruptible community hosts are safe). 24 unit tests pass.

> **★★ VAST.AI ADAPTER WIRED 2026-07-22 (trimcrae picked Vast as the paid wide-parallel workhorse).** The
> **wall-clock problem is diagnosed, not GCP-fixable:** GCP GPU is pinned to **us-central1 only** (our standing
> region rule — no L4/G2 quota elsewhere), so the whole fleet competes for **one region's shallow Spot L4 pool
> (~4–6 concurrent)** — a *shared-pool* ceiling that more GCP quota can't lift. The fix is **horizontal spread
> across a marketplace where each leg is its OWN independent rented machine**: N legs = N instances, genuinely
> N-wide, no shared-quota wall. **Modal (the one free-AND-instantly-parallel option) is exhausted this month**
> (monthly grant spent; resets next month), which is why the paid marketplace is now the wide-parallel play.
> **`VastBackend.submit()/status()/stop()` are now fully implemented** in `gpu_backend.py` (verified-offer
> search → cheapest single-GPU RTX-4090-class pick → instance-create with a **guaranteed self-destroy onstart**
> so no idle-GPU bleed). The load-bearing logic — `_select_cheapest_offer` + `_vast_onstart` + `_vast_status` —
> is factored into **pure, unit-tested** helpers; the thin `_vast_request` urllib client is isolated. **REMAINING
> (needs trimcrae):** create/fund a Vast.ai account, set **`VAST_API_KEY`** as a CI/job secret (+ a small
> balance — first out-of-pocket dollar). Then a **one-instance smoke** confirms the REST endpoint shapes (the
> only thing not exercisable in-repo, since the Vast API schema drifts between versions) before any fan-out.
> Azure ($200) + Oracle ($300) trials were considered but **deferred** (trimcrae chose Vast only): they're free
> $, but each is a *single quota-gated VM cloud like GCP* (GPU quota 0 on trial, Oracle GPU-capacity-starved),
> so they fix **cost** but not **parallelism** unless summed across accounts — revisit if we want $0 added width.

> **⚠ SPOT/PREEMPTIBLE CHECKPOINT DURABILITY (must-read before any spot MD run).** SageMaker managed-spot does
> NOT sync files a process holds **open and appends** (the openmmtools `.nc`/`.chk`) to S3 mid-run — only at
> clean job end — so a spot kill loses the whole leg. Fix = the **checkpoint-uploader sidecar** (explicit
> periodic boto3 upload of the resume-critical files). Root cause, proof, fix, and caveats:
> **[nr4a3-degrader-next-steps.md → "Infra gotchas" → SageMaker managed-spot checkpoint sync](../modalities/nr4a3-degrader-next-steps.md#infra-gotchas-a-fresh-session-must-know)**.
> Any provider whose checkpoint sync you don't control needs the same explicit-upload pattern — bake it into
> each `submit()`.

> 📱 **Phone-only, no terminal.** Every signup + API-key step below is done in a mobile browser; the
> key values go straight into the repo's GitHub Actions secrets (github.com -> repo -> Settings -> Secrets and
> variables -> Actions -> New secret). ALL command-line / deploy work is done by me via CI — you never open a
> terminal.
>
> ⚠️ **Free-credit amounts and promos change constantly.** The figures below are typical recent offers — verify
> the current amount on each signup page. I have not fabricated promo codes; there are none to enter.

---

## TL;DR — the recommended path (fastest to cheapest)

1. **Start on Modal** (free monthly credits, serverless = **zero idle-GPU risk by design**, Python-native).
   Run the whole triage tier and shake out the pipeline for ~free. **NOTE: Modal is the easy/free *starting*
   option, NOT the cheapest — per GPU-hour it's PRICIER than Salad (serverless premium). It's #1 only for the
   free credits + inherent no-idle + easiest setup.**
2. **Put the checkpoint bucket on Cloudflare R2** (free egress — matters because trajectories move between
   providers). This is the shared state that makes compute swappable.
3. **Add SaladCloud + RunPod** for the cheap sustained fleet — **Salad is the actual cost winner (cheapest per
   hour)** and should carry the bulk triage volume once Modal's credits are used; RunPod Secure for the few
   long terminal legs.
4. **Apply to ACCESS** in parallel (free national HPC; slower, needs affiliation) and burn any **$300 cloud
   trial credits** (Google/Oracle) opportunistically.

## GCP GPU + region choice (recorded 2026-07-12; quota request kicked off ahead of need)

> **STATUS 2026-07-12:** trimcrae requested **4× Preemptible L4 + 4× Preemptible T4** (us-central1), pending
> approval. 4 concurrent is enough for the pilot + early bulk triage; bump to 8 later if the campaign grows
> (follow-up increases approve faster once the first grant lands). When approved → wire the `gcp` adapter's
> launch/teardown, then GCP is live and first in line under the free-first waterfall.


**Cheapest GCP GPU for our MD/FEP = NVIDIA L4 on Spot**, region **us-central1** (Iowa, lowest-price US region).

> **★ MEASURED + CONFIRMED 2026-07-16 (L4 vs T4 head-to-head, `gpu-bench-gcp.yml`).** Same 35,211-atom TIP3P/PME
> system, 4000 steps @ 4 fs HMR, OpenMM **OpenCL** on both (see CUDA note below), us-central1-a Spot:
> **CUDA UPDATE 2026-07-16:** forcing OpenMM's **CUDA** platform (Miniforge+mamba conda-forge openmm, auto-matched
> to the driver via `__cuda`; `BENCH_REQUIRE_CUDA=1`) gives **L4 = 628.0 ns/day / $0.0092/ns on CUDA** vs 484.9 /
> $0.0119 on OpenCL — **1.30× faster, ~23% cheaper/ns**. CUDA is the production default going forward (widens L4's
> lead further). The OpenCL numbers below are the original apples-to-apples L4-vs-T4 comparison.
> **L4 (g2-standard-4) = 484.9 ns/day**, **T4 (n1-standard-4) = 228.2 ns/day** → L4 is **2.13× faster**. At
> est. Spot ~$0.24/hr (L4) vs ~$0.13/hr (T4): **L4 $0.0119/ns vs T4 $0.0137/ns** — L4 ~13% cheaper *per finished
> job*, confirming the cheapest-per-job hypothesis. **DECISION: L4 is the going-forward GCP GPU** (faster +
> cheaper/ns + 24 GB headroom; wins all three axes). Caveats: (1) the $/ns margin is within the uncertainty of
> the *estimated* Spot prices — pin real prices from Billing before a big fleet, but the pick is robust because
> L4 also wins on speed + VRAM outright; (2) both ran **OpenCL** because the pip OpenMM wheel's CUDA build didn't
> match the driver (`CUDA_ERROR_UNSUPPORTED_PTX_VERSION` fallback — same reason the AWS pipeline uses OpenCL);
> moving production to **CUDA** (pin OpenMM's cuda-version to the driver, or bake an image) speeds both up and
> **widens L4's lead**. Proof-of-concept milestone: OpenMM MD runs end-to-end on a GCP Spot GPU VM (~6 min, ~$0.01/run).

> **★★ GCP RBFE PLUMBING PROVEN 2026-07-16 (`gpu-rbfe-gcp.yml`, run 29509433578).** The FULL OpenFE
> RelativeHybridTopology RBFE pipeline now runs end-to-end on a GCE Spot L4 VM: openfe 1.12 env built via
> Miniforge+mamba, VM self-staged the public TYK2 valA edge (no S3), LOMAP mapped 31 atoms
> (tyk2_ejm_31→tyk2_ejm_42), and **setup → simulate → analyze** completed **on CUDA** (require-CUDA validated
> the CUDA platform on the L4) → `status=OK dg_morph=13.262±0.268 via=split`. This was a `RBFE_TINY` plumbing
> shakeout (2.5ps/10ps MD — the ΔG value is NOT science), but it answers the load-bearing question **"can we run
> RBFE on GCP at all" → YES.** Two bugs found + fixed en route: (1) L4 Spot stockout in us-central1 → hybrid
> zone search across us-central1/east1/east4/west1/west4 with wait-retry (a g2-standard-8 provisioned in
> **us-east1-c** — we have at least burst L4 quota beyond central); (2) `AmberTools not available` at am1bcc
> charge assignment → the env python was run directly instead of activated, so openff-toolkit's
> `shutil.which("antechamber")` missed the env bin → fixed by prepending the env bin to PATH (mirrors AWS
> `conda run -n rbfe`). NEXT: `mode=real` full spot-safe valA_mini (RUNG 1 kill-switch) — needs GCS
> checkpoint/restore for the multi-hour run.

> **★★ GCP SPOT-SAFE GCS CHECKPOINT PROVEN 2026-07-16 (`gpu-rbfe-gcp.yml` spot_safe=1, run 29519188186).** The
> full spot-safe path ran end-to-end on a GCE L4: setup → **simulate committing checkpoints to `GCSCommitStore`**
> (gs://project-a7ebde30-e2ed-4b8d-9a9-rbfe-ckpt, keyless via the VM SA + ADC) → analyze → `status=OK`. Commits
> are MANDATORY in the spot-safe driver (a failed GCS write raises + aborts — as the first attempt did when the
> bucket was absent), so reaching analyze-DONE PROVES every commit boundary wrote to GCS. Setup (one-time, owner):
> pre-created the bucket + granted the compute SA `roles/storage.objectAdmin` on it (S3-from-GCP was rejected — it
> would put AWS creds in GCE metadata; the scoped GCS grant is keyless + more secure). Also built: a
> **spot-preemption RESUME LOOP** (`vm_alive()` fast-detects preemption; re-creates the VM, whose startup restores
> the newest GCS-committed snapshot and resumes, ≤1 checkpoint lost) — run 29515433285 had been killed by an
> un-resumed preemption, which motivated it. REMAINING for the real kill-switch: wire `mode=real` to run BOTH legs
> (complex+solvent) at FULL sampling through the split + reduce → ΔΔG vs the known TYK2 value (the valA GO/NO-GO
> verdict is already in `reduce_receptor`); the ~4-5 h run needs multi-dispatch resumability (each GH job runs to
> its timeout, re-dispatch resumes from GCS).

> **★ CROSS-GPU / CROSS-PROVIDER $/ns — L4 vs A10G, and "is there something better" (analysis 2026-07-16,
> answering trimcrae's three questions).** KEY PHYSICS: OpenMM PME explicit-solvent MD is **memory-bandwidth
> bound**, not FLOP-bound — so for our workload the GPU's **GB/s** predicts ns/day far better than its TFLOPS.
> That single fact reorders the "best GPU" ranking:
>
> | GPU | Arch | BW (GB/s) | FP32 TFLOPS | VRAM | Spot $/hr (typ) | ns/day | $/ns | source |
> |---|---|---|---|---|---|---|---|---|
> | **L4** | Ada | **300** | ~30 | 24 GB | ~$0.24 (GCP) | **628** | **$0.0092** | **MEASURED (CUDA)** |
> | T4 | Turing | 320 | ~8 | 16 GB | ~$0.13 (GCP) | 228 | $0.0137 | measured (OpenCL) |
> | **A10G** | Ampere | **600** | ~31 | 24 GB | ~$0.40 (AWS g5) | ~900–1100 *(est)* | ~$0.0087–0.0107 *(est)* | estimate |
> | **RTX 4090** | Ada | **1008** | ~82 | 24 GB | ~$0.20–0.35 (Vast/Salad) | ~1500–2500 *(est)* | **~$0.003–0.006 *(est)*** | estimate |
> | L40S | Ada | 864 | ~91 | 48 GB | ~$0.80–1.10 | ~1400–2000 *(est)* | ~$0.010–0.019 *(est)* | estimate |
> | A100 40/80 | Ampere | 1555–2039 | ~19 | 40/80 GB | ~$1.0–1.5 | ~2000–3000 *(est)* | ~$0.008–0.018 *(est)* | estimate |
>
> **Answers:**
> 1. **Would L4 beat A10G on price/compute? NOT clearly — it's ~a wash.** A10G has **2× L4's bandwidth** (600 vs
>    300 GB/s) at similar TFLOPS, so A10G should deliver **more ns/day** (est. ~1.4–1.75× L4). L4 wins on $/hr,
>    A10G wins on throughput; the two roughly cancel on **$/ns**. So switching AWS off A10G *onto* L4 (via g6)
>    would **not** save money — no reason to do it. The A10G number is an ESTIMATE; a measured A10G-CUDA run is
>    the only way to settle it (see sweep below).
> 2. **Switch all providers to L4? No.** On **GCP** L4 is already the right pick (it's the best MD-$/ns card GCP
>    offers — GCP has no consumer 4090/L40S; its A100/H100 are bandwidth-huge but overpriced for our small
>    systems). On **AWS**, A10G (g5) is already ~cost-equal to L4 and is what we use — leave it. "L4 everywhere"
>    is not a win; the right rule is **per-provider pick the best MD-$/ns card that provider offers**, which the
>    require-CUDA default now makes automatic.
> 3. **Is there a better GPU than L4? YES — RTX 4090**, on $/ns, by a wide margin, *because* of bandwidth: 1008
>    GB/s (3.4× L4) at ~$0.20–0.35/hr Spot on Vast/Salad → est. **~2–3× cheaper per finished job than L4.** The
>    catch is the PROVIDER, not the card: Vast/Salad are interruptible community clouds (no managed-spot resume,
>    flakier hosts, MD-env reload cost on preemption) — which is exactly why the waterfall already slots them for
>    *bulk short-sampling triage* and reserves stable hosts (RunPod Secure / ACCESS) for long terminal legs.
>    **L40S** (48 GB, 864 GB/s) is the pick only when a system needs >24 GB. **A100 is a trap** for us —
>    huge bandwidth but its price kills $/ns on our ~35k-atom legs.
>
> **BOTTOM LINE:** for the **current GCP credit-burn phase, L4-CUDA stays the pick** (best card GCP offers, and
> it's on free credits). The definitive cross-provider ranking wants a **measured $/ns sweep on CUDA** — A10G
> (AWS g5), L4 (baseline), L40S, RTX 4090 (Vast/Salad) — but that spends on AWS/Vast, so it's **deferred until we
> move off GCP credits and are optimizing $ hard**; RTX 4090 on a stable-enough host is the a-priori winner to
> confirm then. No provider switch is warranted now.

- **T4** is cheapest *per hour* (~$0.11/hr Spot, 16 GB) but slow (Turing) and 16 GB risks OOM on a solvated
  complex → cheapest-per-hour, NOT cheapest-per-job.
- **L4** (~$0.25–0.40/hr all-in Spot, 24 GB, Ada) is ~2–3× faster for MD, so *fewer billed hours* → usually the
  cheapest **per finished job**, and 24 GB fits the complex leg comfortably. **Default = L4 Spot; T4 Spot as a
  cheap fallback.** Confirm cheapest-per-ns with the smoke/pilot before committing a fleet. Always Spot
  (preemptible) — our per-unit checkpointing makes preemption safe and Spot is 3–4× cheaper than on-demand.
- **Quota to request** (Console → Quotas & System Limits, after upgrading OFF the free trial + enabling the
  Compute Engine API): `Preemptible NVIDIA L4 GPUs` (us-central1) = 8, `Preemptible NVIDIA T4 GPUs`
  (us-central1) optional, `GPUs (all regions)` ≥ 8. Justification = independent computational-chemistry
  research, MD/FEP on checkpointed Spot GPUs. Small Spot requests approve in minutes–hours; large up to ~2 days.
  **Step 0 gotcha:** GPU quota is denied on a pure trial account — must upgrade to full billing first ($300
  credit still applies). The `gcp` backend defaults should target `us-central1` + L4 Spot to match this.

## ★★ COST WATERFALL — burn every free credit before paying a cent (POLICY — trimcrae, 2026-07-12)

**Spend order is FREE-FIRST. Never pay a "cheap" provider (Vast/RunPod) while a free credit sits unused —
$300 is a lot of GPU-hours.** Reach for compute in this order, dropping to the next tier only when the one
above is exhausted or genuinely can't run the job:

1. **Modal free monthly (~$30/mo, recurring)** — zero friction, already wired. First choice for validation +
   any work that fits inside the monthly grant. Recurs, so it never fully "runs out" — it caps per month.
2. **GCP $300 trial (90-day window)** — the biggest, most reliable free GPU credit. First stop once a job
   exceeds Modal's monthly grant. *This SUPERSEDES the old "GCP = terminal-leg reserve only" framing:* it's
   free money, so we use it wherever it fits (bulk triage OR terminal legs), not reserved for one tier.
3. **Oracle $300 trial (30-day window)** — burn if usable, but **low confidence**: Oracle trial accounts are
   notoriously GPU-starved (shapes often out-of-capacity / quota 0 until you convert to pay-as-you-go), and the
   window is only 30 days. Treat its $300 as a *bonus if a GPU shape actually launches*, not a planned tier.
4. **Any other signup credits** (RunPod/Salad occasional promos) — opportunistic.
5. **PAID cheap providers (Vast → RunPod Secure)** — ONLY after the free tiers above are spent/unavailable.
   `VAST_API_KEY` is staged and ready; it's the first *out-of-pocket* dollar, not the first dollar.

**Honest friction to plan around (why free ≠ instant):**
- **GCP:** needs a **service-account JSON key** (IAM & Admin → Service Accounts → Keys → JSON — NOT the
  Gemini/AI-Studio API key) **and** an **upgrade off the free trial to a paid account** (the $300 still applies)
  **plus a GPU-quota request** (new accounts start at 0; Google blocks GPU-quota grants while on pure trial).
  Quota approval has **lead time (hours–days)** → when a bulk campaign gets scheduled, kick the quota request
  a couple days ahead so the credit is usable when needed. We are **NOT** in a race (§ operating regime), so
  this hump is fine to absorb on the normal timeline.
- **Oracle:** expect to convert to pay-as-you-go and still possibly find no GPU capacity on trial. Validate one
  GPU launch before counting on it.

**ACTIVATION TRIGGER (event, not a date):** the *first time a bulk GPU campaign is scheduled that would exceed
Modal's monthly grant*, un-park GCP FIRST (start the account-upgrade + quota request), burn the $300, then
Oracle, then paid Vast — and name that free-credit provider in the standing "confirm provider before kickoff"
step. Until such a run is imminent, don't prompt trimcrae to do the GCP/Oracle setup (no GPU work to burn it on
yet). The `gcp` backend is already wired + unit-tested in `gpu_backend.py` (Spot GCE VM + self-delete anti-idle
guard); only the account-side setup above is deferred.

## Provider choice per GPU run (POLICY — trimcrae, 2026-07-12)

**Every substantial GPU run from here on names a preferred provider, confirmed with trimcrae BEFORE kickoff**
(no silent default to AWS). The provider named must respect the FREE-FIRST waterfall above. Default mapping by
tier (as a *capability* guide — the waterfall decides *which funded account* pays):
- **First/validation runs** → **Modal** (free credits, zero-idle, foolproof).
- **Bulk short-sampling triage** (the many binary/paralogue rungs) → free credit first (**GCP $300**), then
  **paid Vast** once free credit is spent.
- **Long full-sampling terminal legs** (the few certifying ternary runs) → free credit first (**GCP $300**;
  its Spot L4/A100 pricing is ideal here), then **RunPod Secure** or **ACCESS** (a stable host so frequent
  preemption doesn't force costly MD-env/system reloads).
- **AWS SageMaker** → only when specifically warranted (already-staged data, or nothing else set up yet).
The provider is a config in the provider-agnostic harness (`research/modalities/gpu_backend.py` +
`autoteardown.py` + `object_store.py`), not a rewrite — so switching is cheap and `pick_cheapest()` can even
auto-route within a tier.

---

## The exact accounts to create (in priority order)

| # | Account | URL | Why | Free credit (verify) |
|---|---|---|---|---|
| 1 | **Modal** | modal.com | serverless GPU, **auto-scales to zero (no idle billing)**, best "start for free" | **~$30/month free credits**, ongoing |
| 2 | **Cloudflare R2** | dash.cloudflare.com → R2 | checkpoint/state bucket, **$0 egress** | 10 GB storage + free egress |
| 3 | **SaladCloud** | portal.salad.com | cheapest sustained compute (consumer GPUs) for triage volume | trial credits for new orgs (verify) |
| 4 | **RunPod** | runpod.io | Secure Cloud for the long terminal legs (stable, clean API) | occasional signup credit (verify) |
| 5 | **Google Cloud** *(optional)* | cloud.google.com/free | burn a big trial credit on GPU VMs | **$300 / 90 days** |
| 6 | **Oracle Cloud** *(optional)* | oracle.com/cloud/free | another trial credit; sometimes cheap GPU | **$300 / 30 days** |
| 7 | **ACCESS** *(parallel, free-at-scale)* | allocations.access-ci.org | free national-HPC GPU hours | free allocation (see draft) |

For each of 1/3/4 you'll create an **API key** and give me the env-var names below; I never need to see the key
value in chat — set them as CI/job secrets.

**Also useful, no signup blocker:** **Google Colab / Kaggle** give free T4/L4 sessions (time-limited) — fine
for one-off smoke tests, not the fleet.

---

## Step-by-step to go live

**A. Stand up the state bucket (once).**
1. Create a **Cloudflare R2** bucket, e.g. `nr4a3-ckpt`.
2. Make an R2 **S3-API token** (Access Key ID + Secret). Note the endpoint `https://<acct>.r2.cloudflarestorage.com`.
3. Give me: `OBJECT_STORE_ENDPOINT` (that URL) — the key/secret go in job secrets as `AWS_ACCESS_KEY_ID` /
   `AWS_SECRET_ACCESS_KEY` (R2 uses the S3 auth scheme). *(If you'd rather reuse the existing AWS S3 bucket,
   skip R2 — just accept AWS egress fees on cross-provider traffic.)*

**B. Build + push the job container (once).** `research/compute/Dockerfile.mdjob` builds the OpenMM/OpenFE env.
I can add a GitHub Action that **builds and pushes it to GHCR** (free) so every provider pulls the same image —
say the word and I'll add that workflow (no account needed beyond the repo).

**C. Modal (start here — free + no idle risk).**
1. Sign up at **modal.com**; run `pip install modal` + `modal token new` locally, OR create a token and give me
   `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET`.
2. I finish `ModalBackend.submit()` (a `@app.function(gpu=...)` that runs the job unit + `.map()`s the windows).
3. We run the **triage tier for ~free** on the monthly credits, validating the end-to-end path on real GPU.

**D. Salad + RunPod (cheap sustained fleet).**
1. Create accounts; add a payment method; load a small balance (e.g. $10–20 each to start).
2. Create API keys → give me `SALAD_API_KEY` (+ org/project) and `RUNPOD_API_KEY`.
3. I finish `SaladBackend`/`RunPodBackend.submit()` + `stop()` (Salad group-scale-to-zero is the anti-idle
   guard; RunPod uses in-pod `runpodctl remove pod`, already wired in the teardown).
4. `pick_cheapest()` then routes: **triage → Salad/Vast**, **terminal legs → RunPod Secure**.

**E. ACCESS (free at scale, parallel track).** Resolve the PI-affiliation question in
`access-allocation-request.md`, submit the Explore request (~1–2 wk). If granted, I finish `SlurmBackend`
(sbatch) and the fleet's expensive tier runs **free** on national HPC.

---

## What I do vs. what needs you

- **Me (free, no accounts):** finish each provider's `submit()`/`stop()` to its real API; wire `object_store`
  into the FEP driver's checkpoint path; add the GHCR image-build workflow; a dry-run smoke on the mock backend.
  I can write all of it now; it just can't be *exercised* on a provider until a key exists.
- **You:** create the accounts above, generate API keys, load a small balance where required, and resolve the
  ACCESS affiliation. Hand me the key **names** (not values) or set them as secrets.

**Cost outlook once live:** triage-heavy Stage-2 on Salad/Modal-credits + terminal legs on RunPod/ACCESS should
bring the ~$1–5k AWS estimate down to **low hundreds of dollars (or free if ACCESS lands)** — with **no idle-GPU
bleed on any provider**, guaranteed by the teardown wrapper.

---

## Free-credit / offer cheat-sheet (verify at signup — these move)
- **Modal** — ~$30/month free credits, recurring. Best zero-idle starting point.
- **Google Cloud** — $300 / 90-day trial (GPU quota may need a request).
- **Oracle Cloud** — $300 / 30-day trial + an Always-Free tier (GPU not in always-free).
- **Azure** — ~$200 / 30-day trial; Azure-for-Students $100 if eligible.
- **Cloudflare R2** — 10 GB free + **free egress** (use it for the state bucket).
- **Backblaze B2** — 10 GB free, free egress to Cloudflare (R2 alternative).
- **SaladCloud / RunPod / Vast** — intermittent signup credits; check the current promo.
- **ACCESS** — free national-HPC allocation (Explore tier; see the drafted request).
- **NVIDIA Inception / Academic Hardware Grants** — free cloud credits/hardware **if** you qualify (startup /
  academic).
- **Colab / Kaggle** — free T4/L4 sessions, time-limited; smoke tests only.
