---
id: DOC-VAST-PLACEMENT-FACTS
title: Vast placement & market structure — hard facts (read BEFORE diagnosing why a lane cannot get a host)
level: —
kind: runbook
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `runbook` from its location under research/compute/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
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
| 1b | **`min_cuda` as a global 13.0** | **MEASURED too high and FIXED** — `ternary-fep` JITs against NVRTC 12.6, so the floor was refusing hosts it can run on. Now looked up **per image**: **§4** | `research/modalities/image-cuda-requirements.json` (the one home); probe `ternary-fep-cuda-probe.json`; board cost in `vast-filter-ablation.json` → `cuda_sweep` |
| 1c | a **card floor** (`min_ns_per_h`) | deleted the cheapest cards on a premise its own lane's 208-rental ledger refutes, and roughly doubled the gate's reported price — **see §3** | this file §3; `step1-fanout-supervisor.yml` 5aks-gate block |
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

**Implemented the same day**, not just written down. One home for the decision:
**`vast_machine_blacklist.DURABLE_EXCLUSIONS_ENABLED = False`** — reads return empty, writes are refused, and
`tests/test_blacklist_retired.py` holds it there. `VAST_DURABLE_EXCLUSIONS=1` restores the old behaviour
exactly, which is what makes the change reversible; it is an escape hatch for a diagnosis, **not** a setting
to leave on. `vast-filter-ablation.json` records `durable_exclusions_enabled: false` with **45 ids retired**,
sourced per snapshot in that artifact.
⚠ **And an honest counterpoint that must travel with it:** on *that particular* board read the retired set
would have removed **0 offers** and cost **0 %** on `$/ns` (`vast-filter-ablation.json` →
`tiers[].retired_blacklist`). **That is not evidence the set was harmless** — its harm is intermittent by
construction, occurring only when its machines are on the board and cheap. One snapshot showing no damage is
exactly the reading that let it grow.

---

## 2. BOARD WIDTH IS A DIFFERENT DIAGNOSIS FROM PRICE — AND THE READOUT MUST SAY WHICH

**The failure mode.** A market gate prices the **cheapest surviving offer(s)** and holds if that is above the
buy line. A high number there reads as *"the market is expensive, wait for it to open"* — but it is equally
consistent with *"our filters removed the cheap end, and we are pricing what is left."* Those have opposite
remedies: one says wait, the other says widen. **They are indistinguishable from the price alone.**

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
| `offers_returned` | rows the **server-side query** returned (`gpu_backend._vast_offer_query`: verified, rentable, 1 GPU, VRAM/RAM/cores/disk/reliability/`cuda_max_good` floors, `type` bid-vs-on-demand, `limit`). ⚠ **already spec-filtered — it is NOT the size of the board**, see §2c | the *query* is narrow — a spec floor or the tier, not the market |
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

Two consecutive commits (`191615f3`'s parent **is** `1fee1e5a`), both carrying the artifact's own
`utc: 2026-07-31T17:09:23Z` — **1:09 PM ET** — same unit needing a host
(`5aks_d0_to_d__ternary_nr4a1_r0…`), same three machines already occupied:

| commit | `offers_returned` | `qualifying` | `priceable` | best offer | `$/ns` | ×basis | verdict |
|---|---|---|---|---|---|---|---|
| `1fee1e5a` | 201 | **80** (40 %) | 80 | RTX 5090, machine 137832 @ $0.2948/hr | 0.007282 | **2.134** | **HOLD** |
| `191615f3` | 169 | **167** (99 %) | 93 | RTX 4090, machine 12976 @ $0.1120/hr | 0.003840 | **1.126** | **CLEAR** |

The two signatures alternate all afternoon, **at one point 56 seconds apart** — **11:12 AM ET**
(`utc 15:12:47Z`) → 207 / 81 / 81 → 2.227× → HOLD, then **11:13 AM ET** (`utc 15:13:43Z`) → 169 / 168 / 94 →
0.833× → CLEAR. **No market moves 87 qualifying offers and 2× in price in 56 seconds. A spec does.**

⚠ **Which spec, is NOT established, and this file does not guess.** The `5aks-gate` job's price depends on
four workflow inputs — `gpu_class`, `min_ns_per_h`, `on_demand`, `bid_floor_mult`
(`gpu-ternary-fep-vast.yml`, the `5aks-gate` job `env:`) — and **the artifact it writes records none of
them**, so a committed row cannot be attributed to the spec that produced it. Two candidates, not exclusive:
the ternary lane's self-heal re-placement path dispatches every gate with a hard-coded
`-f min_ns_per_h=28 -f bid_floor_mult=2.0` and conditionally `-f on_demand=1`, while the supervisor's
`5aks-gate` dispatch passes no floor. **§2c narrows it, and the narrowing turns on WHERE each filter acts.**
`min_ns_per_h` is **client-side only** (`rank_offers_by_usd_per_ns`), so a card floor **cannot move
`offers_returned` at all** — it can only depress `qualifying`. The expensive stream shows **both**: 201
returned against 169 (*higher*) and 80 qualifying against 167 (lower). The **tier** does move both, and in the
right directions — measured on one board read, on-demand returned **more** rows than bid and cost **~2×** per
nanosecond. So the tier is the only one of the two candidates that accounts for the whole signature. That is a
mechanism, not an attribution of these rows. **The discriminating observation** for them is still to
read those four inputs off the runs behind each stream — the CLEAR stream's run ids are in
`ternary-vast-launch-attempts.json` (e.g. `30649738323` for the 1:09 PM ET row) — or, better, to record the
spec in the gate artifact so the question cannot be asked again.

⚠ **A HOLD is absent from `ternary-vast-launch-attempts.json` by design** (that ledger records
`dispatched` / `nothing-to-launch` / `blocked`, per its own `_read_this_when`). So the two streams are only
visible together in the **hold file's git history**. Do not conclude from the attempts ledger that the
expensive stream does not exist.

### 2c — the ablation: HOW MUCH board each of our own filters eats, and the TIER effect

Run the same afternoon (`vast_filter_ablation.py` → **`research/modalities/vast-filter-ablation.json`**, one
board read at **1:36 PM ET 2026-07-31**, $0, rents nothing). It is the one home of these numbers; two results
are worth carrying here because they change how a hold is read.

⚠⚠ **ITS `offers_returned` IS NOT THE GATE'S `offers_returned`, AND CONFLATING THEM WILL MISLEAD YOU.** The
ablation issues a deliberately **permissive** query — `num_gpus=1` server-side and nothing else
(`permissive_query`, `limit` 3000) — so every filter can be counted client-side against the same list. A
gate's query has already applied the VRAM / RAM / cores / disk / reliability / `cuda_max_good` floors before it
counts. **So the ablation's number is the whole single-GPU board; the gate's is what survived the server
query.** That is why one reads ~1370 and the other ~170 on the same afternoon, with no disagreement between
them.

**(i) Our own spec removes the overwhelming majority of the single-GPU board.** Bid tier: **1370 offers →
119 surviving the full spec → 52 priceable.** So a large drop is the *normal* case, not an alarm — what matters
is **which** filter is responsible, and `per_filter` gives each one's `marginal_cost_offers` (offers only that
filter removes) and the `$/ns` improvement from leaving it out. On that read the two worth re-examining were
`cuda_max_good ≥ 13.0` (§4, ~6 % better without it) and `cpu_ram ≥ 32 GB` (~36 % better without it — but that
floor is bought deliberately, because ternary setup is RAM-bound and a 16 GB box swaps; see
`ternary_vast_launch`'s HOST SPEC note). `reliability2`, `disk_space`, `cpu_cores` and `verified` each cost
essentially nothing and are free to keep.

**(ii) ⭐ THE TIER, NOT THE MARKET, IS WORTH ~2× — measured on the SAME board read:**

| tier | `offers_returned` | surviving full spec | priceable | best `$/ns` | ×basis |
|---|---|---|---|---|---|
| **bid** (interruptible) | 1370 | 119 | 52 | 0.003014 | **0.883** |
| **on-demand** (uninterruptible) | 1826 | 140 | 71 | 0.006066 | **1.778** |

**On-demand returns MORE rows and costs ~2× per nanosecond.** That is the mechanism behind §2b's two
signatures — a gate priced on the on-demand tier reads as "the market has doubled" and the market has not
moved at all. So **before reading any hold as a market event, establish which tier it priced.** `on_demand`
is a per-dispatch input and is still not recorded in the gate artifact (§2b), which is why the individual
17:09:23Z rows remain unattributed even though the mechanism is now measured.

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

## 4. `min_cuda` — MEASURED, APPLIED, and now a PER-IMAGE value (2026-07-31)

**Status: CLOSED.** It is written up rather than deleted because the *shape* of the answer is the reusable
part: a filter this expensive should be measured from the artifact it constrains, never asserted from a
Dockerfile line.

**The question was** whether the CUDA-13-class PTX that justified raising the floor from 12.6 to 13.0 on
2026-07-23 is actually present in *this* image. It could not be settled from the Dockerfile: `FROM
nvidia/cuda:12.6.3-runtime-ubuntu22.04` plus a `cuda-version=12.6` conda pin is consistent with either answer,
because conda-forge is free to resolve a newer CUDA runtime into the env — which is exactly what would have
made the 2026-07-23 comment true.

**The discriminating observation** (`probe_image_cuda.py`, run **inside** the container, $0, no GPU): OpenMM
JIT-compiles its CUDA kernels with **NVRTC**, so the PTX ISA it emits — and therefore the minimum host driver
— is fixed by `libnvrtc`'s own version, not by the base-image tag. **The env resolved `cuda-nvrtc 12.6.85`,
`libnvrtc.so.12` at 12.6, `libcudart` at 12.6 and `cuda-version 12.6`: the pin DID take.** The artifact and
its `verdict` are the one home — `research/modalities/ternary-fep-cuda-probe.json`
(`required_host_cuda: 12.6`).

**What the extra 0.4 costs**, from the live `cuda_sweep` in `research/modalities/vast-filter-ablation.json`
(bid tier, one board read, 2026-07-31 1:36 PM ET): the board's surviving offers fall from **134 at 12.6 to
119 at 13.0**, priceable from 58 to 52, and the best achievable rate moves from **0.829× to 0.883× basis**.
⚠ `cuda_max_good` is applied **twice** — a server-side query term (`_vast_offer_query`) *and* a client-side
filter — so unlike a card floor it moves **`offers_returned` itself**, the §2 field that then reads as "the
market is narrow" rather than as "we asked for a narrow market". *(Where it ranks against the other filters
is `vast-filter-ablation.json` → `per_filter`; it is not the largest, and no ranking is restated here.)*

**What was applied** (`881a34d0`) is better than the edit this section originally asked for, and the
difference is the lesson: `min_cuda` **stopped being a constant**. The floor is now looked up **per container
image** from `research/modalities/image-cuda-requirements.json` — written by the probe, never typed —
via `gpu_backend.measured_min_cuda(image)`, and held by `tests/test_image_cuda_floor.py`.
**`ternary-fep` → 12.6.** An image nobody has probed does **not** inherit another image's floor: it falls back
to `gpu_backend.CONSERVATIVE_MIN_CUDA`, which is deliberately the old **13.0**, so an unmeasured stack stays
safe and its cost stays visible as itself. *Superseded, retained: `min_cuda = 13.0` as a standing constant,
and the "the `cuda-version=12.6` pin did NOT take" claim it rested on.*

⚠ **One thing the probe does not settle, and it is the reason the fallback is conservative:** a probe reads
what an image *contains*, so it transfers to no other image. The 2026-07-23 crash it overturns was real; what
was wrong was generalising one env's floor into a global constant. **A newly-probed image still deserves one
leg watched through `build_system` before the lane is left unattended.**

⚠ **Not registered as a superseded figure, on purpose.** An entry retiring `cuda_max_good ≥ 12.6` was added to
`pinned-figures.json` earlier the same day and **removed once the probe landed**: 12.6 is the value the
measurement supports, so pinning it as retired would make CI flag a true statement — the one failure mode that
registry's own README forbids. What survives is the one-home repair: [pricing.md §E](./pricing.md) no longer
names a value, it points at the code.

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
- **Per-filter offer counts, the tier comparison and the CUDA sweep** → `vast_filter_ablation.py` →
  `research/modalities/vast-filter-ablation.json`. **Re-run it rather than quoting the numbers above** — they
  are one board read and the board moves; the *rankings* are the durable part.
- **What CUDA the baked image requires** → `probe_image_cuda.py` →
  `research/modalities/ternary-fep-cuda-probe.json`.

---

## 6. Open at the end of 2026-07-31 — the short list

1. **Only ONE image has been probed** (`ternary-fep`, §4). Every other stack — `nrv04vast`, `pmxfep`,
   `nr4a3fep`, `bioemu`, `protfep` — is still on `CONSERVATIVE_MIN_CUDA = 13.0` and is paying the ~6 %
   `$/ns` penalty §4 measures, for want of a $0 probe run. *(Closed 2026-07-31: `min_cuda` for `ternary-fep`
   itself, applied in `881a34d0`.)*
2. **A gate artifact still records no spec** — `gpu_class`, `min_ns_per_h`, `on_demand`, `bid_floor_mult`
   (§2b). Until it does, a committed hold cannot be attributed to the tier or floor that produced it, and the
   §2c tier effect makes that a ~2× ambiguity.
3. **`realised_rentals` records no `gpu_name`** (§3), so "card class does not predict host lifetime" rests on a
   price proxy rather than a card census.
4. **`vast_idle_guard` is still label-scoped** (§1 row 1d) — an account-wide sweep is the real fix, named in
   `realised_spend.ATTESTED` → `vast_bench_sweep_orphans.closes_when`.
