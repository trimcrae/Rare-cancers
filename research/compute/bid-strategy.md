# Vast bidding as an optimisation problem — findings and policy (2026-07-24)

> **Headline, model-free:** on today's RTX-4090 market, **on-demand is ~1.17× the interruptible floor**, while the
> incumbent policy bids **1.9× the floor**. So the current policy pays **~38 % more per hour than on-demand for a
> box that can still be preempted.** That is strictly dominated, and it needs no hazard model to see.
>
> Engine: [`vast_bid_optimizer.py`](../modalities/vast_bid_optimizer.py) (28 unit tests). Live evidence:
> `vast-bid-advice-ternary.json`, `vast-bid-advice-rbfe.json`, `vast-bid-ondemand-crosscheck.json`
> (read-only offer search — no rent, no instance, no spend).

---

## 1. What the incumbent policy is, and its four defects

`gpu_backend._vast_bid_price` returns `min_bid × 1.9` — one global multiple of the market floor, for every job on
every host. It was a sound response to a real problem (the NR-V04 covalent tail churned at ×1.5), but as a policy:

1. **The on-demand cap is documented but not enforced.** The docstring says "never above on-demand"; the code is
   `ref * 1.9` with no cap. The earlier cap was removed because it could fall *below* `min_bid` and leave the box
   created-but-stopped — but the fix for that is a cap **clamped to ≥ min_bid**, not the absence of one.
2. **We rank by the wrong quantity.** Offers are ranked by `min_bid`, yet we pay `1.9 × min_bid` and the job takes
   `work / throughput` hours. Measured host throughput varies ~6× (19–116 ns/day, covalent panel). A host 2×
   faster at 1.3× the floor is far cheaper per completed leg; ranking on the floor cannot see it.
3. **A scale-free multiple misprices risk.** The premium ×1.9 buys scales with the floor; the *hazard* depends on
   where the bid sits in the local offer-price distribution, which is not a function of the floor. The same
   multiple over-insures a thin market and under-insures a thick one.
4. **One constant serves every job.** The right margin depends on what a preemption costs — image reload plus work
   lost since the last checkpoint. A ternary leg checkpointing every 40 iterations and a 6 ns endpoint-MD leg
   writing 500 frames do not share an optimum.

## 2. The model

With bid `b`, floor `m`, on-demand `d`, work `W` GPU-h on the chosen host, restart overhead `R` hours per
preemption, and hazard `λ(b)` per hour:

```
W_wall(b) = W / (1 − λ(b)·R)            each preemption adds R
C(b)      = b · W_wall(b)               on Vast you PAY YOUR BID
```

Minimise `C` over `b ≥ m` subject to `W_wall ≤ W_max`, and compare against **on-demand as a genuine alternative**
(`d·W`, zero preemption) rather than as a cap. That comparison is the question the fixed multiple never asks.

**Hazard.** You are preempted when someone outbids you, so `λ ∝` the arrival rate of higher bidders. The competing
bid distribution is estimated **free, from the offer list the same query already returned**:

```
λ(b) = λ_ref · (1 − F(b)) / (1 − F(m))      F = empirical CDF of competing offer prices
```

so protection is measured as *"the fraction of the market I am now above"* rather than as an arbitrary multiple,
and `λ(m) = λ_ref` by construction.

**`R` is what makes the answer job-specific:** `R = image_reload + ½ · checkpoint_interval · sec_per_iter`.
Tighten checkpointing and a cheaper, riskier bid becomes optimal — the two knobs are coupled, and the fixed
multiple assumes they are independent.

## 3. Live measurement (2026-07-24, read-only)

| | ternary profile (10.7 GPU-h, 146 k atoms) | RBFE profile (13.7 GPU-h, 35 k atoms) |
|---|---|---|
| live 4090 offers | 7 | 7 |
| offers where **×1.9 exceeds on-demand** | **7 / 7** | **7 / 7** |
| incumbent bid on the best offer | $0.329/hr | $0.279/hr |
| optimiser recommendation | $0.173/hr (= floor; on-demand wins) | $0.147/hr (= floor; on-demand wins) |

**`min_bid == dph_base` on every offer returned by the bid query.** That equality is the load-bearing claim, so it
was cross-checked against a separate **on-demand** query matched by `machine_id`: on the one machine visible in
both, on-demand `dph_total` = **1.17 ×** the interruptible floor. *(Honest limit: only **one** machine appeared in
both result sets, so the 1.17 is a single observation. The `min_bid == dph_base` equality across 6–7 offers is the
stronger leg of the evidence.)*

**Decomposing the saving — what is measured vs what is modelled:**

- **Model-free (~38 %):** on-demand at ~1.17× floor versus the incumbent's 1.9× floor, per hour, *and* with zero
  preemption risk. No hazard model involved.
- **Model-dependent (the rest of the ~62 % the tool reports):** the remainder comes from the hazard model
  inflating the incumbent's expected wall clock at `λ_ref = 1.0/hr`, which is a **prior, not a measurement**.
  Do not quote the 62 % as measured.

## 4. Policy

1. **Default to on-demand while `min_bid ≈ dph_base`.** Interruptible only pays when the floor is materially below
   on-demand. Right now it is not, so interruptible buys nothing and costs preemption risk.
2. **Never bid above on-demand.** Cap at `dph_base`, clamped to `≥ min_bid`.
3. **Rank offers by expected $ per completed unit**, not by `min_bid` — throughput and reliability belong in the
   ranking.
4. **Set the margin from `R`, not from a constant.** Tight checkpointing earns a cheaper bid.
5. **Log every launch** (`LaunchRecord`: bid, floor, market prices, hours observed, censored) so `λ_ref` becomes a
   measurement. Until then it is a prior and every output says so.

## 5. What has NOT been changed, and why

`gpu_backend._vast_bid_price` is **untouched**. The optimiser is advisory until (a) the `λ_ref` prior is replaced
by fitted survival data, and (b) the `min_bid == dph_base` condition is confirmed to persist rather than being a
snapshot of one afternoon's market. Changing the launch path on one read-only sample would repeat exactly the
error that produced the ~2.6× RBFE mispricing: generalising from a single measurement without checking it
transfers.

**Immediate, no-calibration-needed action:** for the next launch, take **on-demand** and record the realized
`dph_total`. That is both the cheaper choice on today's market and the cleanest way to start the ledger.
