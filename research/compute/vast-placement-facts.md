# Vast placement & market structure — hard facts (read BEFORE diagnosing why a lane cannot get a host)

**Scope.** Why a Vast rental does or does not happen: our own filters, board width, host survival, and the
readouts that tell those apart. **Not** what things cost — [pricing.md](./pricing.md) owns the cost evidence
and the bid; **not** host-survival priors — [vast-churn-observations-2026-07-25.md](./vast-churn-observations-2026-07-25.md)
owns those. This is the Vast counterpart of [gcp-gpu-facts.md](./gcp-gpu-facts.md), and it exists for the same
reason: every fact below cost real debugging time, and several were **learned twice** because their only
record was a commit message or a comment three thousand lines into a launcher.

---

## 1. THE RECURRING FAULT: our own filter, not the market, is usually the binding constraint

**State the pattern first, because the individual incidents keep being diagnosed as new.** A lane that cannot
get a host reports the same surface symptom — `no rentable verified offer`, or a market gate holding on price
— whether the cause is a thin market or a filter of ours that has quietly eaten the board. **The default
hypothesis should be the filter**, because it has been the cause every time it has been checked:

| # | the filter | what it did | where the evidence lives (one home each — do not restate here) |
|---|---|---|---|
| 1a | the **durable machine blacklist** | grew until it, not price, decided placement; authorised units failed to place against a healthy, wide board | `vast_exclusion_census.__doc__`; `congeneric_fanout_vast.withdraw_wrong_exclusions.__doc__` and `.retire_perishable_exclusions.__doc__`; the wave-scoped comment in `ternary_vast_launch.collect`; `vast_machine_blacklist.__doc__` (which parked the hazard before it happened) |
| 1b | **`min_cuda` = 13.0** | may be excluding hosts this lane's image can actually use — **UNRESOLVED, see §4** | `gpu_backend.ResourceSpec.min_cuda` (the raise and its 2026-07-23 diag proof) |
| 1c | a **card floor** (`min_ns_per_h`) | deleted the cheapest cards from an already-starved board, on a premise its own lane's ledger refutes — **see §3** | this file §3; `step1-fanout-supervisor.yml` 5aks-gate block |
| 1d | **`vast_idle_guard` is LABEL-SCOPED** | runs only inside a lane's own collect, so a lane that stops being dispatched stops being guarded, and nothing says so — two orphaned rentals billed for days | `realised_spend.ATTESTED` → `vast_bench_sweep_orphans.closes_when` and `nrv04_retro_orphan.closes_when`; STRATEGY.md Appendix A 58 |
| 1e | **truncated board pagination** | the query carried no `limit`, so every gate and every submit decided on a small fraction of the market — and it manufactured apparent price volatility (§2) | `gpu_backend._vast_offer_query` (the `_VAST_SEARCH_LIMIT` block, with the paired-read numbers) |

**The asymmetry that makes this the right default.** Re-testing a host we wrongly refused is nearly free —
a failed *submit* costs no rental and no billing, and a box that starts and then crash-loops is reaped on
measured write-silence. Wrongly refusing a good host costs capacity on every lane, every night, silently.
So when placement fails, **widen before you conclude anything about the market.**

### 1a′ — THE DURABLE BLACKLIST IS RETIRED (trimcrae, 2026-07-31)

> *"You've gotta just stop doing the blacklist. It seems like it only ever bites us in the ass and clearing it
> always makes things better."*

The standing rule now lives in **CLAUDE.md §6**. What that retires is the **durable, cross-lane, host-scoped
set** — the thing that survives a wave and filters somebody else's placement tomorrow. Two mechanisms are
**kept** and must not be confused with it, because both are bounded and neither can accumulate:

- **`used_machines`** (`congeneric_fanout_vast.mode_launch`) — wave-scoped double-rent prevention. It seeds
  from the hosts the lane is *already renting* so a second wave does not re-book them, and **it dies with the
  wave**. A machine we are happily running on is a good machine.
- **the in-call retry skip** (`gpu_backend.submit`) — when a host refuses the start with
  `resources_unavailable`, that machine is skipped for the *remaining offers of that one placement call*, on
  a **copy** of the spec, bounded by `_VAST_START_REFUSAL_TRIES`. It never outlives the call.

⚠ **The reason the durable set has to go is not that it was wrong on any single host** — some of those hosts
really do refuse every start. It is that the set has **no evidence that can retire an entry** (nothing ages
out, and a TTL was correctly refused for want of a measurement), so it is a ratchet: monotone in a quantity
that shrinks the board, on a market where the cost of re-learning is one free failed submit.

---

## 2. BOARD WIDTH IS A DIFFERENT DIAGNOSIS FROM PRICE — AND THE READOUT MUST SAY WHICH

**The failure mode.** A market gate that finds one acceptable offer reports a high `$/ns` and holds. That
reads as *"the market is expensive, wait for it to open"* — but it is equally consistent with *"our filters
left one host, and we are pricing the only survivor."* Those have opposite remedies: one says wait, the other
says widen. **They are indistinguishable from the price alone.**

**This has now been measured twice, on two different mechanisms, and diagnosed wrongly the first time on both
occasions.** The 2026-07-27 instance — a gate reading two very different multiples of basis minutes apart,
perfectly predicted by **how many rows came back** rather than by any price movement — is recorded in
`gpu_backend._vast_offer_query` with its paired-read numbers, which is their one home. *Its conclusion, in its
own words:* **"the board had not moved; the page had."**

### 2a — the field that discriminates, and what each one means

Every gate in this repo emits `board_depth` / `depth`. It is computed once, in
`relaunch_market_gate.price_offers` (and the identical shape in `congeneric_fanout_vast`,
`nrv04_vast_launch` and `step1_terminus_evidence`), and it is the whole diagnosis:

| field | what it counts | what a low value means |
|---|---|---|
| `offers_returned` | rows the **server-side query** returned (`gpu_backend._vast_offer_query`: verified, rentable, 1 GPU, VRAM/RAM/cores/disk/reliability/`cuda_max_good` floors, `type` bid-vs-on-demand, `limit`) | the *query* is narrow — a spec floor or the tier, not the market |
| `qualifying` | of those, how many survived the **client-side** hard filters in `gpu_backend.rank_offers_by_usd_per_ns` (exclusions, `require_gpu`, `min_ns_per_h`, `num_gpus`, VRAM slack, `cuda_max_good`, hourly cap) | **our filters ate the board** — this is the exclusion/card-floor signal |
| `priceable` | of those, how many carry a **benched** card, so a `$/ns` can be formed at all | the board is full of cards we have never measured; see [pricing.md §A.3](./pricing.md) |
| `used_for_mean` | how many of the cheapest `priceable` offers the reported mean was taken over — `min(needed, priceable)`, where `needed` is the number of hosts about to be bought | ⚠ **not a symptom.** For a single unit this is 1 **by design**, and a mean over one offer is a high-variance statistic in any market |

**The rule that follows, and it is now in CLAUDE.md §6: a hold reported on price MUST report board width
beside it.** A hold whose `qualifying` is a small fraction of `offers_returned` is a **filter diagnosis wearing
a price label**. The machinery to say so already exists and should be used rather than re-invented:
`relaunch_market_gate` and `congeneric_fanout_vast` both detect "the board returned offers and none survived
the filter while N machines are excluded" and set **`hold_cause: exclusions_or_spec_not_price`** (plus
`hold_cause_why`), which `lane_staleness_watch` already reads as "our filter, not the market".

### 2b — MEASURED 2026-07-31: one artifact, two specs, opposite verdicts

`research/modalities/5aks-market-hold.json` was written all afternoon by **two interleaved streams** whose
verdicts differ by 2× in price and by ~half the board in width. Both are committed; read them with
`git log -- research/modalities/5aks-market-hold.json`.

Two consecutive commits, **both stamped `2026-07-31T17:09:23Z`**, same unit needing a host
(`5aks_d0_to_d__ternary_nr4a1_r0…`), same three machines already occupied:

| commit | `offers_returned` | `qualifying` | `priceable` | best offer | `$/ns` | ×basis | verdict |
|---|---|---|---|---|---|---|---|
| `1fee1e5a` | 201 | **80** (40 %) | 80 | RTX 5090, machine 137832 @ $0.2948/hr | 0.007282 | **2.134** | **HOLD** |
| `191615f3` | 169 | **167** (99 %) | 93 | RTX 4090, machine 12976 @ $0.1120/hr | 0.003840 | **1.126** | **CLEAR** |

The two signatures alternate all afternoon, **at one point 56 seconds apart** (`15:12:47Z` → 207/81/81 →
2.227× → HOLD; `15:13:43Z` → 169/168/94 → 0.833× → CLEAR). **No market moves 87 qualifying offers and 2× in
price in 56 seconds. A spec does.**

⚠ **Which spec, is NOT established, and this file does not guess.** The `5aks-gate` job's price depends on
four workflow inputs — `gpu_class`, `min_ns_per_h`, `on_demand`, `bid_floor_mult`
(`gpu-ternary-fep-vast.yml`, the `5aks-gate` job `env:`) — and **the artifact it writes records none of
them**, so a committed row cannot be attributed to the spec that produced it. Two live candidates, and they
are not exclusive: the ternary lane's self-heal re-placement path dispatches every gate with a hard-coded
`-f min_ns_per_h=28 -f bid_floor_mult=2.0` and conditionally `-f on_demand=1`, while the supervisor's
`5aks-gate` dispatch passes no floor; and the query's `type` field is `bid` vs `on-demand` depending on the
tier, which changes `offers_returned` as well as the rate. **The discriminating observation** is to read
those four inputs off the runs behind each stream — the CLEAR stream's run ids are in
`ternary-vast-launch-attempts.json` (e.g. `30649738323` for the 1:09 PM ET row) — or, better, to record the
spec in the gate artifact so the question cannot be asked again.

⚠ **A HOLD is absent from `ternary-vast-launch-attempts.json` by design** (that ledger records
`dispatched` / `nothing-to-launch` / `blocked`, per its own `_read_this_when`). So the two streams are only
visible together in the **hold file's git history**. Do not conclude from the attempts ledger that the
expensive stream does not exist.

---

## 3. CARD CLASS DOES NOT PREDICT HOST LIFETIME ON THIS ACCOUNT (measured 2026-07-31)

**The claim this refutes** is "a cheap card cannot close a checkpoint interval inside a host lifetime, so
exclude it" — the premise of a `min_ns_per_h` card floor. It was applied to the 5a-KS gate at 12:41 PM ET
(`7eb97ad6`) and reverted at 1:10 PM ET (`9e02ea6f`) after trimcrae asked that 3090s be considered.

**Source: the step 1 fan-out's own rental ledger**, `research/modalities/step1-fanout-map.json` →
`realised_rentals`, **n = 208 rentals** across **100 distinct machines** and 19 units. Reproduce with:

```bash
python3 - <<'PY'
import json, statistics as st
r = json.load(open('research/modalities/step1-fanout-map.json'))['realised_rentals']
for name, g in (('<=$0.12/hr', [x for x in r if x['rate_usd_h'] <= 0.12]),
                (' >$0.12/hr', [x for x in r if x['rate_usd_h'] >  0.12])):
    b = sorted(x['billed_h'] for x in g)
    print(f"{name}  n={len(b):<4} median={st.median(b):.2f} h  "
          f">1h={100*sum(v>1 for v in b)/len(b):.0f}%  max={max(b):.2f} h")
PY
```

| rate band (card-class **proxy**) | n | median billed hours | share over 1 h | max |
|---|---|---|---|---|
| **≤ $0.12/hr** (3090-class) | 34 | **1.50 h** | 62 % | 6.62 h |
| **> $0.12/hr** (4090/5090-class) | 174 | **1.65 h** | 67 % | 11.13 h |

**Cheap hosts hold essentially as long as expensive ones.** A floor that deletes the cheap band therefore
buys no retention; its only measured effect is to narrow an already-narrow board (§2).

⚠ **Two honest limits, both load-bearing.** (i) **Rate is a PROXY for card class** — `realised_rentals`
records `machine_id` and `rate_usd_h` but **no `gpu_name`**, so the split is a price cut, not a card census.
Adding `gpu_name` to the ledger row would settle it. (ii) `billed_h` is **rental** time, not leg time (the
semantics are pinned by `tests/test_price_ledger_uptime_semantics.py`), so this measures how long we *held*
a host, which is the quantity a card floor claims to improve.

### 3a — churn frequency was never the failure mode

The same ledger says the fan-out **converged at 208 rentals for 18 completed edges = 11.6 rentals per
completed edge**, for its full realised cost (one home: `step1-fanout-map.json` → `realised_usd`). Churn at
that rate did not stop it. What does stop a lane is the condition already stated in
`ternary_vast_launch.resource_spec`'s on-demand escape-hatch comment: **when mean host lifetime is below
time-to-first-commit, faster recovery cannot converge — only a host that cannot be taken away can.** That is
a statement about *interval length vs lifetime*, and the remedy it points at is the uninterruptible tier or a
shorter checkpoint interval, **not** a card floor.

### 3b — a telemetry gap is not a stall (the misread that produced the floor)

The observational evidence cited for the card floor was a 3090 leg "frozen at 40.9 % for 33 minutes while its
ETA slipped 11 h". **That same census row also carried `targets not in the record` and `no openmmtools rate
line`** — the collector could not READ that leg's progress. **An absent reading was taken for a reading of
absence**, and a code change was made on it. The general rule is in **CLAUDE.md §4**; recorded here because
this is where the row will be looked at again.

---

## 4. OPEN QUESTION — which CUDA floor does the ternary image actually need?

**Not answered here. Do not close it from this file; the diagnostic is named below and costs $0.**

Three places in the repo say different things about the same host filter:

| where | what it says |
|---|---|
| `gpu_backend.ResourceSpec.min_cuda` (the value in force) | **13.0**, raised from 12.6 on 2026-07-23 on a diag proof that the `cuda-version=12.6` env pin *did not take* — legs on driver-12.6/12.7 hosts died at `build_system` with `CUDA_ERROR_UNSUPPORTED_PTX_VERSION` |
| `research/compute/Dockerfile.ternaryfep` | `FROM nvidia/cuda:12.6.3-runtime-ubuntu22.04`, with `cuda-version=12.6` pinned in the mamba spec and a comment stating the base tag "only needs to be ≤ the host driver" |
| [pricing.md §E](./pricing.md) | ⚠ **stale, and repaired 2026-07-31** — it previously named a filter of `cuda_max_good ≥ 12.6`, superseded by the code's raise and never followed here. It now points at `min_cuda` instead of restating it |

`ternary_vast_launch.resource_spec()` takes 13.0 (overridable by `TVAST_MIN_CUDA`), and `cuda_max_good` is a
**server-side** query term (`_vast_offer_query`), so this floor moves `offers_returned` itself — the §2 field
that reads as "the market is narrow" rather than as "we asked for a narrow market".

**The question:** is the CUDA-13-class PTX that justified the raise present in **this** image, or was 13.0
inherited from a lane whose env genuinely differs? A base image and a conda pin at 12.6 are consistent with
either — the PTX version is a property of the built OpenMM, not of the tag.

**The discriminating observation, $0 and no rental** — read what the image actually *contains*, in CI, per
CLAUDE.md §6's pull-don't-solve rule:

```yaml
- run: |
    docker run --rm --entrypoint micromamba docker.io/triskit23/ternary-fep:latest \
      list -p /opt/mamba/envs/rbfe openmm cuda-version
```

The `openmm` row's **build string** carries the CUDA it was built for (`…_cuda12…` vs `…_cuda13…`), and the
`cuda-version` row says whether the 12.6 pin took at all — which is precisely the claim the 2026-07-23 raise
was made on. Pair it with two board reads at `min_cuda=12.6` and `13.0` for the `offers_returned` difference,
so the cost of the floor is measured beside its justification. Until that is done, **13.0 stands** (it is the
value with a measured failure behind it) and §1b stays open. Whatever the answer, the fix is **one home for
this number** — pricing.md §E's `12.6` is stale against the code either way.

---

## 5. What this file deliberately does NOT restate

Per CLAUDE.md §1 rule 1, these have exactly one home and it is not here:

- **Host-survival priors, the `resources_unavailable` refusal rate, and the hazard/downtime constants they
  dispute** → [vast-churn-observations-2026-07-25.md](./vast-churn-observations-2026-07-25.md).
- **The bid policy, the `$/ns` ranking argument, disk sizing, the throughput table and its re-anchoring** →
  [pricing.md](./pricing.md) (+ Appendices T and U).
- **The buy line / drift line and its absolute-rate expression** → `inflight_usd_per_ns.APPROVED_USD_PER_NS`,
  ruled on in CLAUDE.md §1.
- **The capacity-refusal rule (pick another host, never wait it out) and the fleet-launch `$/ns` gate** →
  CLAUDE.md §6.
- **What can and cannot stop a rental's meter** → `vast_idle_guard.__doc__` (with the `unshare` reproduction)
  and CLAUDE.md §6.
- **The orphaned rentals themselves, their dollar ranges and their remediations** →
  `realised_spend.ATTESTED`; the incidents in STRATEGY.md Appendix A rows 57 and 58.
- **The double-booking classifier and the four never-started classes** →
  [../modalities/step1-fanout-lane.md](../modalities/step1-fanout-lane.md) §7.
