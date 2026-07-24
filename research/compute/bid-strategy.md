# Vast bidding as an optimisation problem — findings and policy (2026-07-24)

> **Headline, measured on 63 machines across 12 card classes:** the interruptible discount is **real and
> universal** — median on-demand = **1.25× the floor**, and **zero** hosts priced at parity. The incumbent
> `min_bid × 1.9` is not overpaying *today* (selection lands it on a cheap-tail host), but **`1.9 ×` exceeds that
> host's own on-demand price on 20 of 23 RTX 4090s** — so the policy is safe only while a fat cheap tail exists,
> and nothing bounds it when the tail thins. **The defect is the absence of a cap, not the level.**
>
> Engine: [`vast_bid_optimizer.py`](../modalities/vast_bid_optimizer.py) (78 unit tests). Live evidence:
> `vast-bid-ondemand-crosscheck.json` (n = 63 machines matched across a bid-type and an on-demand query),
> `vast-bid-advice-ternary.json`, `vast-bid-advice-rbfe.json` — read-only offer search, no rent, no spend.

---

## 0. THE NUMBER

**Stand at $0.30/hr for an RTX 4090, as an interruptible bid, hard-capped at the chosen host's on-demand price.**

Derived, not tuned. A ternary edge is ~64 GPU-h; allowing two weeks on one machine gives a required duty cycle
`ρ = 64/336 = 0.19`, so we accept the cheapest 19 % of the market. The measured 19th percentile of live RTX 4090
floors is **$0.293**. Round to **$0.30**.

| RTX 4090, live (n = 23 machines) | $/hr |
|---|---|
| cheapest floor | 0.1333 |
| **19th pct of floors — the target** | **0.293** |
| p25 / median / p75 of floors | 0.333 / 0.355 / 0.600 |
| cheapest **on-demand** anywhere | 0.3200 |
| incumbent `1.9 × cheapest floor`, today | 0.2533 |

Three things follow that a single price cannot show:

**The discount is real and universal.** Across 63 machines matched between a bid-type and an on-demand query,
**every single host** was cheaper interruptible — median 1.25×, IQR 1.14–1.68, max 5.0, and
`frac_hosts_with_no_discount = 0.0`. So bidding genuinely beats buying, and $0.30 sits below the cheapest
on-demand 4090 on the market ($0.32).

**Selection dominates bidding.** The cheapest 4090 floor is $0.1333 against a median of $0.3550 — a **2.7× spread
between hosts**, far larger than the ~1.20× median discount available *within* a host. Which machine you land on
matters more than what you bid. `_select_cheapest_offer` already ranks by `min_bid`, which is the single most
valuable thing the current code does.

**The incumbent's real defect is that it is unbounded.** `1.9 × floor` is $0.2533 today and *below* the $0.3600
on-demand price of the host it selects — it is not overpaying right now. But it exceeds on-demand on **20 of 23**
hosts, so it survives on the existence of a thin cheap tail (two hosts under $0.20). Remove those two and the
cheapest floor becomes $0.2667, the policy bids **$0.5067 against $0.3200 on-demand — 58 % over**, for a box that
can still be preempted. A multiple of a floating floor has no stable relationship to what a GPU-hour is worth.

```
P* = $0.30/hr (4090), capped at that machine's real on-demand dph_base, never below its min_bid.
     The cap needs a separate `type: "on-demand"` query joined by machine_id — a bid-type query's
     dph_base IS the floor, so it cannot bound anything.
Shipped: gpu_backend._vast_bid_price(offer, ondemand_base) + _vast_ondemand_base_by_machine.
```

### ★ Bench result (2026-07-24, 23:08 UTC) — the card decision moves, with one caveat to close first

Measured at the **ternary size (84,534 atoms)**, `ns/day` from the Vast bench legs, `$/hr` = what each leg
actually won:

| card | ns/day | ×4090 | $/hr | **$/ns** | basis |
|---|---|---|---|---|---|
| RTX 4090 | 669.27 | 1.000 | 0.1333 | 0.00478 | cheapest live floor |
| RTX 4090 | 669.27 | 1.000 | 0.3000 | 0.01076 | policy price `P*` |
| **A10** | **335.99** | 0.502 | **0.0377** | **0.00269** | won by the bench leg |
| L4 | 309.37 | 0.462 | 0.2607 | 0.02022 | won by the bench leg |

**The A10 leg is 1.77× cheaper per ns than a 4090 at its cheapest floor, and 4.0× cheaper than a 4090 at `P*`.**
Half the throughput at a *seventh* of the price. This is the "selection dominates" thesis paying out on the card
axis: the win comes from a $0.038/hr host existing, not from the silicon.

**⚠ Do not act on this yet — the A10 leg's CUDA device string starts with `Quadro`.** An A10 reports as
`NVIDIA A10`, so either Vast's `gpu_name` is mislabelled on that host or we benched a Quadro-family card. Until
the full device string is read back, "a10" names an *offer*, not a verified GPU. The `$/ns` above is real —
that host really did 335.99 ns/day for $0.0377/hr — but its **reproducibility depends on whether cheap hosts of
that kind are a standing feature of the market or a one-off**, which is the same thin-cheap-tail question that
makes a fixed multiple unsafe (§0).

**L4 is confirmed as a calibration-only lane, not a purchase option:** at $0.26/hr for 0.46× a 4090 it is the
worst `$/ns` on the board, 4× the 4090 and 7.5× the A10. We would never rent one for cash while free GCP ones
exist — its value is the `L4→4090` conversion factor.

**RTX 4080: no result.** The leg was still `status=created` at collect time (never started). Its $0.081/hr floor
remains the cheapest 24 GB-class offer seen, so it is still worth a re-run.

## 1. The strategy in plain terms

**We are not choosing a bid. We are choosing a price we are willing to pay, and letting the market come to us.**
On Vast an interruptible bid is a standing **limit order**: it acquires the machine whenever the clearing price
falls to our number and releases it when the price rises above. With per-unit checkpointing, being released is
not a loss — the job parks and resumes. So the only real decision is **what number to stand at.**

Three quantities set it. Each is a concrete number with a concrete source, and the answer is the middle one
clamped by the other two.

| | what it is | where it comes from |
|---|---|---|
| **CEILING** | the on-demand price | We can always buy at on-demand with **zero** preemption risk, so any bid above it is strictly worse. `×1.9` violates this on **20/23** hosts — it stays legal today only because selection lands it on the cheapest floor. |
| **TARGET** | the **duty-cycle quantile** of the price distribution | To finish `W` GPU-hours in `T` hours on `c` machines we must be running `ρ = W/(T·c)` of the time — so accept the cheapest `ρ`-fraction of prices. Need the GPU 12 % of the time → stand at the 12th percentile. **Derived from the deadline, not tuned.** |
| **FLOOR** | the **churn price** | A preemption costs `R` hours (image reload + work since the last checkpoint). Bid so low that `λ(P)·R > 0.2` and most of the money buys reloads, not science. This — and only this — is what the old ×1.9 was actually reaching for. |

```
P*  =  clamp( duty-cycle quantile,  ≥ churn floor,  ≤ on-demand )
```

**Behaviour that falls out of it, with no extra rules:** lots of slack ⇒ `ρ` small ⇒ stand low and wait.
Deadline approaching ⇒ `ρ` rises ⇒ the price rises automatically. `ρ ≥ 1` (must run continuously) ⇒ take
on-demand. Tighter checkpointing ⇒ smaller `R` ⇒ lower churn floor ⇒ we can afford to stand lower. **Knowing
nothing at all** ⇒ stand at `√(floor × ceiling)`, the geometric mean, which is worst-case optimal for bounded
search with no distribution.

### What the real data does to this

Honest punchline: **on the measured Vast market, most of the machinery does not bite.** The daily floor is flat —
`vast/any` sat at its trough on 17 of 20 days (§3d) — so the empirical quantile is ≈ the floor whatever `ρ` is.
In practice the rule reduces to:

> **Stand at the recent floor. Never above on-demand. Never below the churn price.**

The elaborate version earns its keep in exactly two places: when the market is *not* flat (which we can now
detect rather than assume), and the churn floor, which is real, job-specific, and was previously expressed as a
market multiple that had nothing to do with it.

### Where the money actually is — ranked

**⚠ CORRECTED (trimcrae, 2026-07-24). The previous version of this list was wrong in a way that matters.** It
ranked "card choice — up to ~3.6×" first, computed as though the L4 were a *paid* choice we had defaulted into.
It was not. **We have never paid a cent for L4** — every L4 hour ran on free GCP trial credit or Modal's free
tier. And on **Vast**, the only place we spend cash, we have always been on a 4090 or a 3090 depending on the
job. So there is no card mistake to fix on the paying lane, and **a 3.6× "saving" on a lane that costs $0 is not
a saving at all — you cannot save money you never spent.** Worse, "switch off L4" would *increase* cash spend,
from zero to something.

The correct decision rule for a free lane is not `$/ns`. It is **"use it before it expires, on whatever fits."**
`$0` beats any positive price at any throughput.

Ranked properly, for **cash**:

1. **Spend the expiring free credit — up to ~$292, but bounded, and it dies 2026-10-10.**
   `credit-status.json`: GCP trial cap $300, $8 spent → **~$292 left, ~11 weeks**. Bounded harder than it looks:
   a ternary edge runs ~$94 as-run on GCP L4 on-demand versus ~$13 on Vast 4090, so the credit buys **~3 ternary
   edges, not the ladder** (~7× less science per dollar). Still strictly better than paying for those 3. This is
   a **scheduling** decision, not a card or bid decision, and it is the largest single lever.
2. **Bounding the bid on Vast.** `×1.9` is not overpaying today ($0.2533 vs $0.3600 on-demand on the host it
   selects), but it exceeds on-demand on **20/23** hosts and is unbounded as the floor drifts. Capping it at the
   host's on-demand price costs nothing today and prevents a **58 % overpayment** the moment the cheap tail thins.
3. **Card choice *within Vast*** — 4090 vs 3090 is already settled by measurement (4090 wins `$/ns` at every
   size). Whether the **4080** (~16 % better on a proxy) or the **A10** (which bid at $0.016/hr) beats it is the
   genuinely open question, and is what the bench answers.
4. **Bid level** — a **real ~18 % interruptible discount** exists to capture (measured, §3), sized properly
   once the cross-class distribution lands.

**The Vast L4 bench leg is calibration, not a purchase option.** We would never rent an L4 for cash while free
ones exist on GCP; its value is as the **conversion factor** for translating GCP-L4-run results into
Vast-priced projections (the `L4→4090 ≈ 2.06×` ratio pricing.md depends on).

## 2. What the incumbent policy is, and its four defects

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
| optimiser recommendation | $0.173/hr (= floor) | $0.147/hr (= floor) |

**Superseded by the n=63 sweep in §0; retained for the artifact post-mortem.** **⚠ `min_bid == dph_base` is NOT evidence of anything — it is a tautology of the bid-type query**, in which Vast
reports `dph_base` as your rate *at the floor*. An earlier version of this section called that equality "the
load-bearing claim" and "the stronger leg of the evidence." It was neither; it was a definition, and the
"no interruptible discount" conclusion built on it is retracted (see §0).

The valid instrument is the separate **on-demand** query matched by `machine_id`. On machine 26385: floor
**$0.3733/hr**, on-demand compute **$0.4533/hr**, identical $0.003/hr surcharge on both sides — a **real 18 %
interruptible discount**. *(Honest limit: n = 1 machine, because the two query types return disjoint offer pages
at the API default limit. The crosscheck now pulls 512 offers per type across eight card classes and reports the
distribution; until that lands, treat 18 % as one observation, not a rate.)*

**Decomposing the saving — what is measured vs what is modelled:**

- **Model-free:** on machine 26385, `1.9 × floor` = $0.709/hr versus $0.456/hr on-demand — a **55 % premium** for
  a preemptible box. **⚠ But that host is not the one the selector picks**, so this figure does NOT describe the
  policy as run; see §0. Ranking by `min_bid` lands `×1.9` on the $0.1333 floor, where it bids $0.2533 against
  $0.3600 on-demand and overpays nothing today. The 55 % is what happens on a *typical* host — i.e. what the
  policy costs once the cheap tail thins, which is the case for capping it, not for calling it dominated now.
- **Model-dependent (the rest of the ~62 % the tool reports):** the remainder comes from the hazard model
  inflating the incumbent's expected wall clock at `λ_ref = 1.0/hr`, which is a **prior, not a measurement**.
  Do not quote the 62 % as measured.

## 3b. ★ CORRECTION (same day, trimcrae): the above optimises the wrong variable

Everything up to here answers *"given that I launch into THIS market snapshot, what should I pay?"* — and for
work that is not deadline-bound, that is the wrong question. Two things follow, and both are right:

**(a) The target should be an absolute PRICE, not any multiple.** What a GPU-hour is worth to us is an absolute
quantity — it is what prices the ladder. A multiple of a floating floor has no stable relationship to it: at a
$0.15 floor ×1.9 is $0.285, at a $0.55 floor it is $1.045, for identical work. The right object is a
**reservation price** `P*`: "we pay at most $X/hr for a 4090-equivalent," held fixed while the market moves.

**(b) We should wait for the market, not pay today's price.** The repo's own operating regime says this is never
a race, so the cost of waiting is close to zero — which means an optimal-stopping policy is available and both
the ×1.9 heuristic and my "take on-demand" answer ignored it.

**And the waiting mechanism already exists, unused: ON VAST AN INTERRUPTIBLE BID IS A LIMIT ORDER.** A standing
bid at `P*` acquires the machine whenever the clearing price falls to `P*`, and is preempted when it rises above.
With per-unit checkpointing that is not churn to be avoided — it *is* the strategy executing itself: the job
advances during cheap periods, parks during expensive ones, and the cost per unit of **work** is bounded by `P*`
regardless of what the market does. Wall clock stretches; we do not care.

**This also disposes of my regime-A reading.** That reading rested on `min_bid == dph_base` meaning the market
sat at its ceiling. The equality was a query artifact, so it never carried that information either way — and
with a genuine ~18 % discount available below on-demand, the limit-order argument stands on its own.

**The one thing that stops you bidding arbitrarily low.** Bid too far down and you acquire, spend `R` hours
reloading, run briefly, and lose the box — buying reloads instead of science. The useful fraction of paid time is
`(1 − λ·R)`, so `P*` must satisfy `λ(P*)·R ≤ max_churn` (default 0.2, i.e. ≥80 % of paid time is real work).
**That constraint is the legitimate core of what ×1.9 was groping at** — it just expressed it as a market
multiple instead of a job property.

```
P* = max( cheap-end quantile of the price history ,  no-churn floor λ(P*)·R ≤ 0.2 )
```

If the churn floor binds, the message is *"tighten checkpointing"*, not *"pay more"* — the two are substitutes.

**The gap this closes:** §3c's cold start means the absence of a price history is **no longer blocking** — the policy runs from day one and improves as the sampler fills in. What follows applies to the *static* form only.

**Our own hourly series is still worth having** (see §3d — the external source is daily-only). Every observation ever taken was at the instant we wanted to
launch, which is exactly the biased sample you must not set `P*` from. `reservation_price()` therefore **refuses
to return a number without one** rather than inventing a target. `.github/workflows/vast-price-sample.yml`
samples the market hourly (read-only, $0) and begins once it reaches main.

## 3c. ★★ THE ADAPTIVE POLICY — starts from zero knowledge, learns as it goes

A static reservation price needs a history before it answers, which is a real limitation. The literature solves
it, and three features of *our* problem make the solution unusually clean:

1. **Observing prices is FREE and non-committal.** An offer query costs nothing and binds us to nothing — so
   there is **no explore/exploit tradeoff on observation**, the usual difficulty in this class. We can watch the
   market as much as we like. (The one thing that genuinely costs experimentation is the preemption hazard `λ`,
   which you only learn by running — handled separately, as a by-product of jobs we'd run anyway.)
2. **The work is divisible and checkpointed.** We are not choosing one launch instant; we are **procuring
   `W` GPU-hours over a horizon**, buying whenever the price is acceptable. Deadline-constrained divisible
   procurement, not one-shot stopping.
3. **On-demand is a hard, known ceiling.** We can always buy at `d`, so our downside is bounded — and *bounded*
   online search is exactly where a clean distribution-free answer exists.

**The acceptance quantile is the DUTY CYCLE — derived, not tuned.** To finish `W` GPU-hours in `T` remaining
hours on `c` machines we must be running a fraction `ρ = W/(T·c)` of the time. With iid prices, accepting the
cheapest `ρ`-fraction of the distribution is exactly enough to hit the deadline and is the cheapest way to do it.
So `q = ρ`. Slack ⇒ picky. Behind schedule ⇒ `ρ → 1` ⇒ accept anything up to on-demand. It falls out of the
deadline rather than being chosen.

**Cold start (zero observations).** With no distribution but a known ceiling `d` and lower bound `m`, the
worst-case-optimal reservation price for bounded online search (El-Yaniv, Fiat, Karp & Turpin) is the **geometric
mean `√(m·d)`**, competitive ratio `√(d/m)`. No distributional knowledge required — precisely the "know nothing"
regime.

**Convergence.** Once observations accumulate, switch to the empirical quantile — but with an **upper** confidence
bound (normal approximation to the binomial order statistic). A thin sample that happened to catch a cheap spell
would otherwise have us holding out for a price that does not exist. The UCB starts conservative and tightens as
`n` grows, so the hand-off is smooth and never jumps the threshold upward (unit-tested).

```
P*  =  clamp(  max( no-churn floor(R),  economic threshold ),   ≤ on-demand )

economic threshold =  √(m̂·d)                   if n < 12          (distribution-free)
                      UCB_q( observations, ρ )  otherwise          (converges to empirical)
                      d                         if ρ ≥ 1           (deadline binding)
```

### Backtest (synthetic market — validates the ALGORITHM, not the saving)

`vast_bid_backtest.py`, seeded, 3-week diurnal+weekly path, 60 GPU-h of work, on-demand $0.60:

| policy | spend | $/GPU-h | vs clairvoyant |
|---|---|---|---|
| **ADAPTIVE (cold start, knows nothing)** | **$5.80** | **0.0967** | **1.11×** |
| best FIXED threshold (knows `F` perfectly) | $6.89 | 0.1149 | 1.32× |
| incumbent `min_bid × 1.9` | $18.36 | 0.3061 | 3.51× |
| always on-demand | $18.36 | 0.3061 | 3.51× |
| *clairvoyant lower bound (buys the 60 cheapest hours)* | *$5.23* | *0.0871* | *1.00×* |

The adaptive policy lands **within 11 % of a policy that knows the future**, from a cold start — and beats the
best *fixed* threshold even though that one knows `F` exactly, because a fixed threshold cannot relax as the
deadline approaches. Observed trajectory: `P*` starts at $0.13 with zero data, sits at $0.25 through the
cold-start phase, drops to ~$0.14–0.15 once the empirical phase engages, then climbs steadily to the on-demand
ceiling as slack runs out — exactly the urgency behaviour the derivation predicts.

**The price process is invented.** Re-run against `vast-price-history.jsonl` once the sampler has built a real
series; the table above is not a forecast of savings.

## 3d. ★★ REAL PRICE HISTORY OBTAINED — and it deflates my own waiting thesis

I claimed no price history existed and that we'd have to accumulate one hour-by-hour. **I never checked, and it
was wrong.** Vast publishes market metrics directly
(`console.vast.ai/api/v0/metrics/gpu/{current,history,locations}/`, hourly, P10/median/P90) — though those are
gated to a logged-in console session and refuse our API key (`auth_error: This action requires login`,
established by running it). A documented public tracker, [gpuwatch](https://gpu.watchworks.dev/), serves the
same market free during beta with **400-day retention**.

**First parse was wrong and the raw dump caught it.** `/api/history` returns a **panel** — one row per
`(day, provider, kind)` — and my parser pooled the lot, putting runpod-secure at $0.69 into the same
"distribution" as vast-any at $0.14. That is a cross-provider spread, not a price history. Fixed: filter to
`provider=vast`, keep `kind` as separate series, `day` is epoch-ms.

**Vast RTX 4090, 20 daily observations (2026-07-05 → 07-24):**

| slice | floor range | peak-to-trough | days at/near the trough |
|---|---|---|---|
| `vast/any` | $0.1356 – $0.1689 | 19.7 % | **17 / 20** |
| `vast/verified` | $0.2422 – $0.2896 | 16.4 % | 1 / 20 |

**The floor is flat.** The cheap price *is* the normal price — `vast/any` sat at its trough on 17 of 20 days. So
at daily granularity there is very little to wait *for*, and the synthetic backtest in §3c — whose diurnal
amplitude I invented — **overstates the value of waiting by a wide margin**. The algorithm is validated by that
backtest; the magnitude is not, and must not be quoted.

**What waiting is actually worth:** target $0.1356 against today's observed $0.1733 = **21.8 %**, with the target
reachable **85 %** of the time. That is real but modest, and because it is reachable almost always it is less
"wait for a dip" than "stop overpaying for the spot price."

**Ordering the effects, largest first:**
1. **Host selection — up to 2.7×** ($0.1333 vs $0.3550 median 4090 floor). Already done by ranking on `min_bid`;
   this is the largest effect and the current code's best feature.
2. **~22 %** — target the low end of the distribution rather than the moment's price (measured here).
3. **Unknown** — intraday variation. The tracker reports **daily lows only**, so it cannot see it, and this is
   where any remaining waiting value would live. Our own hourly sampler is what settles it.

**Level mismatch, flagged not smoothed over.** Our filtered query found $0.147 today, *below* the tracker's
`verified` low ($0.242–0.290) and near its `any` low ($0.136). So the tracker's `verified` slice is **not** our
rentable subset. Use the external series for the **shape and dynamics** of the distribution; calibrate the
**level** against our own observations before letting it set an absolute reservation price.

## 3e. ★★ CARD CLASS — we have mostly *not* been on RTX, and the card we did use is the worst $/ns

**What we have actually been running on.** Every *completed* science run used an **L4**: `valA_mini` and
`valB_mini` on GCP, `step1_pilot` on Modal. The only RTX runs were the NR-V04 covalent panel (3090) and the
step1_fanout wave-1 / firm timing runs (4090, since halted). So "all production on Vast RTX 4090" is a
**forward-looking policy, not a description of what has happened.**

**And the policy is under-determined.** "The 4090 wins $/ns at every size" rests on a bench that compared exactly
**two** cards — 4090 vs 3090. L4, the card we were actually using, was never in the grid, nor was anything else
on the market. A price analysis scoped to one card inherits that gap, and mine did.

**Live sweep, ranked by $/ns at 146 k atoms** (`--gpu-sweep`, read-only):

| card | offers | floor $/hr | ns/day | **$/ns** | throughput basis |
|---|---|---|---|---|---|
| RTX 4080 | 4 | 0.0810 | 239.5 | **0.00812** | ⚠ dlperf proxy |
| **RTX 4090** | 6 | 0.1733 | 431.9 | **0.00963** | **measured** |
| A10 | 6 | 0.2667 | 412.2 | 0.01553 | ⚠ proxy |
| A4000 | 1 | 0.1067 | 91.5 | 0.02798 | ⚠ proxy |
| **RTX 3090** | 4 | 0.0933 | 72.5 | 0.03090 | **measured** |
| **L4** | 3 | 0.1600 | 109.3 | **0.03514** | ⚠ proxy |
| RTX A6000 | 1 | 0.5600 | 235.3 | 0.05712 | ⚠ proxy |

**Two conclusions — the first CORRECTED 2026-07-24 after trimcrae pointed out the error:**

1. **On the paying lane there was never a card mistake.** Vast rents have always been 4090 or 3090 depending on
   the job; the L4 hours were **free** (GCP trial / Modal), so the `$/ns` gap is a throughput fact about a $0
   lane, **not a realizable saving**. The earlier claim that this "dwarfs everything else" was wrong: switching
   off free L4 would raise cash spend, not lower it. What the table *is* good for is choosing among the cards we
   actually pay for, and as the L4→4090 conversion factor.
2. **A candidate may beat the 4090 by ~16 %:** the RTX 4080 at $0.081/hr. **This is not a decision** — its
   throughput is a `dlperf` proxy, a generic DL score and a weak stand-in for MD. It is a candidate to **bench**,
   which costs cents via `bench_grid`. Note its 16 GB VRAM clears our `min_vram_gb=16` floor but may not hold the
   466 k-atom covalent systems; bench it at the sizes we actually run.

**Action:** add `rtx4080`, `a10`, `l4` to the bench grid before the next production launch. Two of the seven rows
above are measured; the rest are proxies, and a card decision taken on a proxy is how the ~2.6× RBFE mispricing
happened.

## 4. Policy

1. **Stand a limit order at the ADAPTIVE `P*` and wait** (§3c) — the default for all work. It needs no price
   history to start: `√(m̂·d)` from a cold start, converging to an upper-confidence empirical quantile at the
   duty cycle `ρ = W/(T·c)`, floored by the no-churn constraint and capped at on-demand. Do **not** pay today's
   price merely because today is when we happened to look.
   *(Superseded twice: "min_bid × 1.9", then "default to on-demand while `min_bid ≈ dph_base`" — the latter was
   right about one snapshot's arithmetic and wrong about the decision.)*
1b. **Take on-demand only when waiting is genuinely unavailable:** a hard deadline, or a leg that cannot tolerate
   preemption at all (the covalent tail's slow legs needed continuous ~4 h runs). Otherwise waiting is free.
2. **Never bid above on-demand.** Cap at `dph_base`, clamped to `≥ min_bid`.
3. **Rank offers by expected $ per completed unit**, not by `min_bid` — throughput and reliability belong in the
   ranking.
4. **Set the margin from `R`, not from a constant.** Tight checkpointing earns a cheaper bid.
5. **Log every launch** (`LaunchRecord`: bid, floor, market prices, hours observed, censored) so `λ_ref` becomes a
   measurement. Until then it is a prior and every output says so.

## 4b. ⚠ Why the fix is NOT a one-line cap on the bid

Defect 1 invites an obvious patch: `bid = max(min(min_bid × 1.9, dph_base), min_bid)`. **On today's market that
patch is wrong**, and the reason matters.

Since `dph_base == min_bid`, the capped bid collapses to **exactly `min_bid`** — and bidding at the floor is the
regime the incumbent comment explicitly warns about: the earlier "always under on-demand" cap was removed because
it drove the bid to/below the floor and left instances **created-but-stopped** (verified 2026-07-23). So the cap
would trade an overpay for a launch failure.

The correct action when `dph_base ≈ min_bid` is not a cheaper *bid* — it is **not using interruptible at all**:
launch `ResourceSpec(interruptible=False)` and pay on-demand, which on this market costs ~the floor and cannot be
preempted. That is a **provisioning-mode** change at launch time, not a change to the bid formula, which is why
`_vast_bid_price` is left alone. Keep the ×1.9 multiple for the regime it was tuned for — a floor genuinely below
on-demand — and switch modes when the floor converges on it.

## 5. What has NOT been changed, and why

`gpu_backend._vast_bid_price` is **untouched**. The optimiser is advisory until (a) the `λ_ref` prior is replaced
by fitted survival data, and (b) the `min_bid == dph_base` condition is confirmed to persist rather than being a
snapshot of one afternoon's market. Changing the launch path on one read-only sample would repeat exactly the
error that produced the ~2.6× RBFE mispricing: generalising from a single measurement without checking it
transfers.

**Immediate, no-calibration-needed action:** for the next launch, set `interruptible=False` and take
**on-demand** (a mode flag, not a bid change — see §4b), and record the realized `dph_total`. That is both the cheaper choice on today's market and the cleanest way to start the ledger.
