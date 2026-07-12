# Cheap-GPU migration plan — exact accounts, steps, and free-credit offers

**Goal:** move the NR4A3 MD/FEP fleet off AWS SageMaker onto cheaper (or free) GPU before the Stage-2 fan-out.
The current pilot run finishes on AWS untouched; **nothing new kicks off until this is set up.**

**What's already scaffolded (in `research/modalities/`):** a provider-agnostic harness (`gpu_backend.py`),
the auto-teardown guarantee so no provider ever idles a GPU on the meter (`autoteardown.py`), an S3-compatible
checkpoint bridge so compute is stateless and swappable (`object_store.py`), a portable job container
(`research/compute/Dockerfile.mdjob`), and the ACCESS free-allocation draft (`access-allocation-request.md`).
16 unit tests pass. **Only the real per-provider `submit()` calls remain — those need live accounts, which is
what this doc is for.**

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
