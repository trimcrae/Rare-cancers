# Scaling GPU beyond the free credits — the paid-era playbook

**Purpose.** What to do when the free pools (GCP $300, Modal $30/mo, and any nonprofit/HPC allocation) are
spent and a campaign still needs **a lot more** GPU — e.g. the RUNG‑5 prospective ternary matrix, a measured
cross‑provider sweep, or a re‑run wave as methods improve. This is the *demand‑exceeds‑free* plan.

**Sibling docs (read alongside):**
- [cheap-gpu-plan.md](./cheap-gpu-plan.md) — *which GPU / what it costs per hour* + the free‑first waterfall + measured $/ns table.
- [md-throughput-optimizations.md](./md-throughput-optimizations.md) — *how fast and how many sims per GPU* (the free multipliers).
- Credit board: [credit-status.json](./credit-status.json) + [credit_status.py](./credit_status.py) — tells you *when* you're about to cross into paid.

**The one framing that governs everything:** our workload (OpenMM PME explicit‑solvent MD / OpenFE RBFE / ABFE)
is **memory‑bandwidth‑bound, not FLOP‑bound**. So cost is set by **$ per finished nanosecond ($/ns)**, which
tracks a GPU's **GB/s**, *not* its $/hr or its TFLOPS. Every strategy below is a lever on $/ns or on total ns
demanded. Two guarantees are already built and apply to every option: the **auto‑teardown wrapper** (no idle‑GPU
billing on any provider) and **per‑unit checkpoint/resume** (interruptible/spot is safe — lose ≤1 interval).

---

## The paid-era waterfall (apply top-down)

Free multipliers first (they cut the bill for *every* later tier), then cheapest‑$/ns paid capacity, then—only
at sustained high volume—capex.

### Tier 0 — squeeze free ns before buying any (do this first, it's $0)
The highest‑ROI "GPU" is the ns you don't have to run. Per md‑throughput‑optimizations.md, we already capture
CUDA‑over‑OpenCL (~1.3×), HMR 4 fs (~2×), mixed precision, energy‑only `.nc`, single right‑sized replicate.
**Before scaling spend, re‑audit that ledger for any untapped lever** and **right‑size the science**: the
breadth‑first/standard‑depth rule (run each test to field standard, then STOP) is a *demand‑side* cost control.
A campaign that doesn't over‑sample needs a fraction of the GPU. This tier can halve the paid bill for free.

### Tier 1 — pin the cheapest-$/ns card with a measured sweep
The repo's a‑priori $/ns ranking (measured L4 = **$0.0092/ns**; estimates: A10G ~$0.009–0.011, **RTX 4090
~$0.003–0.006**, L40S ~$0.010–0.019, A100 a *trap* for our small ~35k‑atom systems). **RTX 4090 is the a‑priori
winner by ~2–3× on $/ns**, purely because of its 1008 GB/s bandwidth (3.4× the L4). The catch is provider, not
card: 4090s live on **interruptible community clouds** (Vast/Salad). Before committing a large fleet, run the
**measured $/ns sweep on CUDA** (A10G / L4 / L40S / RTX 4090) that cheap‑gpu‑plan.md defers — it costs a little
AWS/Vast $, but it settles the single biggest cost variable for the whole paid campaign. **Route bulk work to
the measured cheapest‑$/ns card**; `pick_cheapest()` in the harness can auto‑route once the numbers are pinned.

### Tier 2 — bulk triage on cheapest interruptible community GPU
For the many short‑sampling legs (binary/paralogue triage, the prospective matrix's first pass): **Vast.ai**
(a bidding marketplace — cheapest 4090/3090 capacity, prices vary wildly by host, bid at spot‑like rates) or
**SaladCloud** (cheapest sustained consumer GPU). Interruptible is fine here — checkpoint/resume makes preemption
cost ≤1 interval. This is where "a lot more GPU" gets *cheap*: 4090‑community at ~$0.005/ns roughly **halves**
the current L4‑on‑GCP cost and beats AWS A10G by ~2×.

### Tier 3 — terminal legs on a stable cheap host
The few long full‑sampling / certifying ternary runs want a **stable host** so frequent preemption doesn't force
costly MD‑env/system reloads: **RunPod Secure Cloud** (clean API, stable, cheap) or, if the nonprofit/academic
route lands, **ACCESS/NRP** (free, see Tier 4). Pay a small premium over community spot here to buy reliability
on the runs where a reload wastes real progress.

### Tier 4 — free-at-scale routes (the biggest lever if either lands)
These dwarf any paid option and should be pursued *in parallel* with the paid tiers, not after:
- **Nonprofit / academic HPC** (ACCESS Explore ~400k credits of A100/H100; NRP/Nautilus free GPU). Blocked today
  by affiliation — but a **501(c)(3)** research org is an *eligible institution*, which unlocks both. If the
  nonprofit path is taken (see the nonprofit strategy discussion), free national‑HPC becomes the primary bulk
  engine and this whole paid playbook drops to a fallback.
- **Renewable nonprofit cloud credits** (AWS Nonprofit ~$2k/fiscal‑yr via TechSoup; Microsoft/Google for
  Nonprofits) — small but *recurring*, unlike one‑shot trials.

### Tier 5 — startup/grant credit scale-up (only on the for-profit route)
If the for‑profit techbio route is taken, larger credit pools open as you show a product/traction:
- **NVIDIA Inception** — cloud credits + potentially discounted DGX Cloud for qualifying startups.
- **Startup cloud programs at their higher tiers** — Microsoft Founders Hub scales past the $1–5k entry tier;
  **AWS Activate** up to ~$100k and **Google for Startups** up to ~$200k *with* an accelerator/equity funding.
  These require the for‑profit entity to genuinely exist and, for the big tiers, external validation.
- **Verify every amount at signup — these move.** Treat the top‑tier headline numbers as gated, not given.

### Tier 6 — own hardware (capex breakeven at sustained heavy use)
At high, *sustained* utilization, buying beats renting. Consumer cards (RTX 4090/5090) are far better $/ns than
datacenter cards for our small systems. **Rough breakeven** (verify current prices): a 4090 rents ~$0.20–0.35/hr
on community clouds and costs ~$1.6–2k to buy → breakeven ≈ **5,000–9,000 GPU‑hours** (~7–12 months at 24/7).
So a single‑ or dual‑4090 workstation pays for itself inside a year *if* you'd otherwise rent that much, and is
dramatically cheaper thereafter. **Costs of owning:** capex up front, power/cooling, maintenance, no elasticity,
consumer‑GPU datacenter‑use license/warranty caveats, no ECC. **Verdict:** worth modeling once sustained demand
is proven (a steady multi‑month fleet), *not* for bursty campaigns where cloud elasticity wins. A local box also
pairs well with cloud burst for peaks.

### Tier 7 — committed-use discounts (only if locked to a hyperscaler)
GCP Committed‑Use Discounts / AWS Savings Plans cut 30–60% for 1–3‑yr commitments — but only make sense at
*predictable sustained* hyperscaler volume, and community‑cloud 4090 generally beats even reserved hyperscaler
pricing for our workload. **Low priority** unless a specific reason forces us onto a hyperscaler at scale.

---

## Worked cost intuition

For a bulk campaign of *N* nanoseconds of MD:

| Path | ~$/ns | Relative | Notes |
|---|---|---|---|
| AWS SageMaker A10G spot | ~$0.010 | 2× | already‑staged data; convenience premium |
| **GCP L4 spot (current free workhorse)** | **$0.0092** | ~1.8× | measured; what we run on free credits now |
| **RTX 4090, Vast/Salad interruptible** | **~$0.005** | **1× (baseline)** | a‑priori cheapest; confirm with the sweep |
| ACCESS / NRP (nonprofit HPC) | **$0** | free | biggest lever; needs 501(c)(3) or affiliation |
| Owned dual‑4090 (sustained) | →~$0 marginal after ~1 yr | capex | only at proven sustained demand |

So the dominant paid‑era move is **Tier 0 (don't over‑compute) → Tier 1 (pin 4090 via the sweep) → Tier 2/3
(community‑spot bulk, stable terminal legs)**, run in parallel with **Tier 4 (chase free‑at‑scale HPC)**. Capex
(Tier 6) only enters once demand is provably sustained.

---

## Decision rule (one line)
**Cut ns before buying (Tier 0), buy the cheapest measured $/ns interruptible card (Tiers 1–2) with teardown +
checkpoint making spot safe, reserve stable hosts for terminal legs (Tier 3), and pursue free‑at‑scale HPC
(Tier 4) in parallel — treat owned hardware (Tier 6) as a breakeven question only once demand is sustained.**
No provider switch or capex commitment without a measured $/ns number behind it (repo rule #1: evidence, not
a plausible story).
