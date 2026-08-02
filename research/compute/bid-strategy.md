# Vast bidding and host selection — the measured policy (rewritten 2026-07-25)

> **Read this for "what do we bid and where do we run."** The policy is derived in
> [`research/modalities/vast_cost_model.py`](../modalities/vast_cost_model.py) (36 unit tests) and imported by
> `gpu_backend.py` and `vast_bid_optimizer.py`, so the code cannot disagree with this page. Cost figures are
> regenerated with `python vast_cost_model.py`, not carried by hand.
>
> **This rewrite replaces four mutually contradictory policies** that were all live in the repo at once —
> `min_bid × 1.9` (bid-strategy.md §4b), `× 1.5` (pricing.md §E), `× 1.25` (the shipped constant), and a
> reservation-price/adaptive-UCB scheme (§3c) that never reached the launch path. §7 records what each one
> believed and which measurement retired it.

---

## 0. THE POLICY, IN FOUR LINES

1. **Rank offers by all-in `$/ns`** — the bid we would actually pay, *plus storage*, divided by that card's
   measured throughput. Never by `$/hr`, never by card name.
2. **Bid the floor plus a staleness tick** (`min_bid × 1.02`, min +$0.0005), capped at that machine's on-demand
   price, never at or below the floor.
3. **Interruptible always**, unless a single leg genuinely cannot survive a pause.
4. **Buy retention with checkpoint frequency, not with dollars.**

**What it achieves on the live board (2026-07-25, 148 qualifying offers): `$0.137` per reference GPU-hour**
against the **`$0.35–0.39/hr` that `step1_fanout` actually paid** — **2.6–2.8×**. Range `$0.057` (best offer)
to `$0.309` (ignoring the ranking and taking a median host).

---

## 1. THE FIVE FACTS IT IS BUILT ON

Everything below is a measurement or a quote from Vast's own documentation, pulled 2026-07-25 through a CI
runner (the dev sandbox's egress proxy 403s every vast.ai host). Raw evidence:
[`vast-docs-raw.json`](../modalities/vast-docs-raw.json),
[`vast-market-intel.json`](../modalities/vast-market-intel.json),
[`vast-market-offers-raw.json`](../modalities/vast-market-offers-raw.json),
[`vast-bid-semantics-probe-ladder.json`](../modalities/vast-bid-semantics-probe-ladder.json).

### F1. You pay your bid, capped at the machine's on-demand price — **MEASURED, and it was nearly wrong**

The whole policy rested on "on Vast you pay your bid," asserted throughout the repo and **never verified**.
Vast's documentation describes the auction but *never states what you are charged*, and a secondary source
claimed the opposite ("you pay what's needed to maintain the highest bid"). Under that reading the policy
inverts: bidding high would be nearly free and the right bid would be your full reservation value.

So it was settled by renting the same offer at three bid multiples — host, card, disk and storage held
constant, bid the only variable. Total cost under one cent.

| bid multiple | bid $/hr | **charged $/hr** |
|---|---|---|
| ×1.0 | 0.00930 | **0.00930** — exactly the bid |
| ×2.5 | 0.02330 | 0.021333 |
| ×8.0 | 0.07470 | **0.021333** — identical to ×2.5 |

The charge tracks the bid and then saturates. A read-only query then identified the ceiling: machine 142136's
own on-demand `dph_base` is **0.021333333333333333** — a match to 17 significant figures.

> **`charged = min(your bid, the machine's on-demand price)`**

Pay-your-bid is therefore **confirmed in the only range we operate in**, and every cent of premium below the
cap is spent on *every hour*, needed or not.

### F2. A higher bid cannot buy safety from on-demand renters

> *"On-demand instances will always take precedence over interruptible instances."* — Vast, *On Demand vs
> Interruptible Rental Types*

The hazard has a floor no bid reaches under. A premium buys protection against *part* of the risk only.

### F3. Being outbid pauses; it does not destroy

> *"Lower-priority instances are paused until their bid is raised enough to regain the highest priority or
> until a higher bid finishes up."*

The disk survives, so a preemption costs the work since the last checkpoint plus downtime — **not** a ~6 GiB
image reload. The reload that once justified the now-retired `×1.9` was **self-inflicted**: our own reaper listed `"stopped"` as
terminal and DELETEd paused instances, forcing a fresh pull on re-rent. The premium was insuring against our
own bug.

### F4. Storage bills continuously, running or paused — and it is not a rounding error

> *"Billed continuously while your instance exists, regardless of running state ... typically higher for
> stopped instances."* — Vast, *Pricing*

Measured across 445 offers: median **$0.20/GB/month** (p90 $0.467, max $1.00) → **~$0.011/hr** at the 40 GB the
launcher requests. This is the term that stops an arbitrarily low bid from being free, and the reason waiting
is not costless. **At the cheap end it dominates:** on the best offer (a $0.0147/hr RTX 3090) storage is
**42% of all-in cost**. Dropping the request to 20 GB cuts all-in cost **21%** — more than the entire bid
change is worth.

### F5. The market is in deep excess supply

Of 445 interruptible offers across usable cards, **essentially none were rented**. On an idle machine `min_bid`
is the host's **reserve price, not a competing bid** — there is nobody there to outbid. And 148 offers passed
our launch filters, so a preempted job has ~148 substitutes.

**This is what makes the premium pointless.** Protection against preemption is available for **$0** by
re-dispatching to a substitute; the premium charges for it by the hour, on one machine, and cannot cover the
on-demand case at all (F2).

---

## 2. THE OBJECTIVE

We buy delivered science, not hours:

```
T_run  = (W/θ) / (1 − λR)        billed running hours, inflated by work redone after a preemption
T_wall = T_run · (1 + λD)        wall clock, inflated by paused time — storage still billing (F4)
C      = c·T_run + s·T_wall

              W     c + s(1 + λD)
     C  =   ───── · ─────────────
              θ         1 − λR
```

`c` = compute $/hr (our bid, F1) · `s` = storage $/hr (F4) · `θ` = ns/hr on this host · `λ` = preemptions per
running hour (**a prior**) · `R` = work lost per preemption ≈ half the checkpoint interval (F3) · `D` =
downtime per preemption ≈ re-dispatch latency (F5).

**λ and D are priors and every output says so.** They do not need to be measured, because the ranking is
*stable* in them: re-running the live board at λ = 0, 0.05, 0.1, 0.3 and 1.0 per hour returns **the same top
three offers every time**. The conclusion does not rest on the unmeasured quantity.

---

## 3. WHAT FALLS OUT — each a property of the cost function, not a preference

### R1. Rank by `$/ns`, never `$/hr`
`C ∝ c/θ`. Ranking by `$/hr` picks a $0.103/hr RTX 3090 over a $0.149/hr RTX 4090 and pays **45% more per ns**.

### R2. Bid the floor plus a tick — a premium is not close to worthwhile
With λ roughly flat in `b` (F5: idle machines, no incumbent), `C` is strictly increasing in `b`, so the optimum
is the lowest bid that wins. The refutable form — differentiate `C(b)` with `c = b` and set `dC/db < 0`:

```
|dλ/db|  >  (1 − λR) / [ (b + s(1 + λD))·R + s·D·(1 − λR) ]
```

At the policy's own operating point on the live board that is **105 preemptions/hour per $/hr of premium**. No
market in excess supply delivers a slope remotely like that. On the very offer their own `min_bid` ranking
selects, the retired rules cost **1.12× (×1.25), 1.26× (×1.5), 1.48× (×1.9)** the policy.

The tick is **not** a priority premium. It exists so a quote that moves between the search call and the rent
call still clears the floor — a bid at or below `min_bid` can leave the box created-but-stopped (verified
2026-07-23), which costs a whole launch to save a fraction of a cent.

### R3. The offer is the lever — not the card, not the multiple
Measured all-in `$/ns` on the live board:

| | $/ns | per reference GPU-hour |
|---|---|---|
| best offer | 0.00181 | **$0.057** |
| best-10 mean (**the planning number**) | 0.00436 | **$0.137** |
| median offer | 0.00983 | $0.309 |

**5.43× from best to median.** Against **1.48×** for the entire bid change that retired `×1.9`. Selection is worth
several times what bidding is, and it is the thing the old policy did worst — it ranked by `min_bid`, which is
neither what we pay nor what we get.

### R4. Interruptible essentially always
`breakeven_hazard_vs_ondemand` gives the λ at which on-demand wins: **~2.2–3.3 preemptions per hour** on
today's board. Take on-demand only for a leg that genuinely cannot be paused.

### R5. Buy retention with engineering, not dollars
`R` enters as `1/(1−λR)` and is ours to shrink **for free** by checkpointing more often. `b` enters linearly
and costs money. When churn hurts, tighten checkpointing — the two are substitutes and only one has a price.

### R6. Ask for the disk the job needs
Storage bills on the *allocation*, continuously (F4). The launcher's `max(40, disk_gb)` floor is a real cost at
the cheap end — see F4.

---

## 4. ⚠ THE CARD RULE IS RETIRED — "the 4090 is the default" is false as a *selection* rule

Both `pricing.md` and `nr4a3-program-map.md` say *"the 4090 wins $/ns at every size, so it is the default."* Two
problems.

**(a) The supporting numbers are from a WITHDRAWN bench.** The quoted `4090 = 1549 / 669 / 175.6 ns/day` and
`3090 = 72.5 @444k` come from the 2026-07-24 23:08 grid, which was withdrawn the same day — every leg was a
single 0.9–4.5 s window, and it ranked an RTX 4080 SUPER above a 4090 and a mislabelled Quadro RTX 8000 as
cheapest per ns. The **validated** re-run (3 × ~20 s independent blocks, physics-checked, CV < 1.4%, with a
rejection gate) gives:

| card | ns/day @ 84,534 | CV |
|---|---|---|
| RTX 4090 | **755.36** | 0.14% |
| RTX 4080 | **703.51** | 0.18% |
| RTX 3090 | **359.36** | 1.31% |

So the 4090/3090 ratio is **2.10×, not 2.42×**, and the 4080 is within **7%** of a 4090, not 40% behind. The
withdrawn 669 figure survived in `vast_bid_optimizer.MEASURED_NS_PER_DAY` for a day because the number lived in
two tables and only one was corrected — which is why there is now exactly one.

**(b) At equal price the 4090 wins; prices are not equal.** On the live board the cheapest 3090 is
`$0.0147/hr` against `$0.1310` for the cheapest 4090 — **8.8× on the bid**, which more than covers being 2.10×
slower. All-in (storage included, F4) the best 3090 is **2.61×** cheaper per ns than the best 4090, and
**the top 10 offers contain both cards**.

> The correct statement is **not** "prefer the 3090." It is: **the card is not the decision — the offer is.**
> Rank on `$/ns` and take whatever wins. Hard-coding either card is how you end up paying 2.6× to run on the
> "faster" one.

**One honest caveat, and it cuts against the cheap 3090 tail.** The validated grid measured **one system size**
(84,534 particles) for three cards; our real systems are 146k (ternary) and 466–650k (covalent). Ratios are far
more size-stable than absolute rates, so the ranking is sound, but an absolute ns/day at another size is not
measured. Also, a 3090 needs **2.10× the wall clock** for the same leg, so a leg with a hard continuity
requirement is 2.10× more exposed on it — `JobProfile.min_uninterrupted_h` scales the requirement per card and
flags this, precisely so the cheap tail is not chosen for the covalent-style legs that need to run through.

---

## 5. ⚠ WHAT THIS DOES **NOT** FIX

**This work corrects the `$/hr` axis only. The GPU-hour axis keeps every uncertainty it already had.**

`nr4a3-program-map.md`'s spend summary records that the ternary base was measured on the **SMARCA2/VHL 8G1Q** assembly
and is being used to price **NR4A** ternaries — the same non-transferability that cost **2.6×** on the binary
lane when the real cmpd19/NR4A3 complex turned out to sample at ~13.6 s/iter against TYK2's ~5.2. **Repricing
multiplies the repo's own GPU-hour estimates; if those are 2.6× low, the costs are 2.6× low regardless of what
we bid.** Nothing here touches that, and the ladder totals in §6 inherit it.

Also unfixed, and worth naming:
- **λ and D are priors** (§2). The ranking is stable in them, but no preemption hazard has ever been measured.
  A launch ledger recording bid, floor and observed uptime would turn them into measurements.
- **One market snapshot.** The 21-day external series shows the 4090 floor is **flat** (18/21 days at its
  trough, peak/trough 1.25×) but the 3090 floor swings **1.71×** with only 4/21 days at trough — so the cheap
  3090 tail is *less* dependable than the 4090 floor. Plan with the best-10 mean, not the best offer.
- **A continuity requirement is a constraint, not a cost.** Ranking on `$/ns` alone hands a leg that must run
  through to the cheapest and therefore slowest card. `JobProfile.min_uninterrupted_h` (in reference-card
  hours) plus `min_clean_run_prob` **excludes** hosts that cannot plausibly meet it; both default to off,
  because most legs checkpoint and genuinely do not care.
- **Host throughput variance is real** (the covalent panel spanned 19–116 ns/day on nominally equal cards). The
  table is per *card*, not per *host*. `verify_and_abandon_threshold` is the response: benchmark briefly on
  arrival and drop a host whose realised `$/ns` is worse than the next candidate — cheap, because substitutes
  are abundant (F5).

---

### 5b. The price series mixes two provenances — do not read a quantile off it yet

`vast-price-history.jsonl` currently holds **two different kinds of row**, and
`vast_bid_optimizer._load_history` takes **every row with a `min_floor`, ignoring `source` and `ts`**:

| rows | `source` | `ts` | what they are |
|---|---|---|---|
| 80 (on `main`) | `gpuwatch_tracker` | **null** | a backfilled external scrape — `min_floor` only, `n_offers` and `median_floor` null, `floors: []` |
| accumulating (on `modalities-cache`) | `systematic` | real ISO timestamps | this workflow's own live snapshots, full offer detail |

Pooling an untimestamped external scrape with our own snapshots into one quantile is a **provenance mix**, not a
longer series: the two are not sampling the same thing, and the untimestamped rows cannot be placed in time at
all. **Left explicit rather than silently merged** — deciding whether the `gpuwatch_tracker` rows belong in the
distribution is a judgement about what the reservation price is being set against, and it should be made
deliberately, with the answer written here.

**Low stakes today, and worth saying so:** the reservation-price / waiting-value read-out that consumes this
history is part of the scheme §7 records as retired — it never reached the launch path. The live policy is
floor-plus-tick ranked on all-in `$/ns` and does not read this file. This is a data-collection lane for a
*possible* future policy, not an input the ladder currently rests on.

*(Found 2026-07-25 while verifying the sampler fix: the workflow's seed step used `git show … > file`, which
truncates before the command runs, so a failed `git show` silently emptied the series. Fixed to a
write-temp-then-adopt-if-non-empty. My first reading of that incident — "it zeroed an 80-sample history" — was
**wrong**: the 80 are this separate external scrape, and the systematic series legitimately starts from zero.)*

## 6. REPRICED LADDER

Regenerate with `python research/modalities/vast_cost_model.py`; JSON in
[`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json). Reference GPU-hours are **the repo's
own work estimates** (pricing.md §B/C) — this reprices them, it does not re-derive them (§5).

| stage | ref GPU-h | **plan $** | range $ |
|---|---|---|---|
| `step1_pilot` (1–2 RBFE edges) | 13.7–27.4 | **2.35** | 0.65–7.89 |
| `step1_fanout` (19 RBFE edges) | 260–260 | **29.72** | 12.30–74.91 |
| `valB_mini` (1 ternary edge, 3 replicas) | 65.3–84 | **8.53** | 3.09–24.20 |
| `valB_full` (2–3 ternary edges + CRL-MD) | 130.7–252 | **21.87** | 6.18–72.60 |
| `nrv04_retrospective` (3 ternary legs + shared pair) | 98–252 | **20.00** | 4.64–72.60 |
| `ternary_4fs_recalibration` | 42–54 | **5.49** | 1.99–15.56 |
| `5a-KS` primary (ligand-side double difference, 2 seeds × 2 arms) | 65.3–336 | **22.93** | 3.09–96.80 |
| `5c` ensemble refinement (24–200 endpoint-MD legs) | 33.12–276 | **17.67** | 1.57–79.52 |
| local within-basin FEP | 65.3–303.3 | **21.07** | 3.09–87.38 |
| **TOTAL (stages this tool prices)** | | **~$150** | **$37–531** |

*(Repriced 2026-07-27 from the re-anchored throughput table — pricing.md Appendix T. The **~$166** / **$42–519**
this table carried is superseded; the GPU-hours are unchanged, only the `$/reference-GPU-hour` moved.)*

⚠ **This is not the ladder total.** It covers only the nine alchemical/MD stages the cost model reprices. The
whole gated ladder — adding step0, `valA_mini`, the measured `$8` covalent panel, and the CPU-dominated 5a/5b —
is **~$169 (~$46–626)** *(the **~$158 (~$44–578)** this line carried is superseded — RUNG 5a-KS went from 2 ternary legs to 4, STRATEGY Appendix A row 54; and the **~$185 (~$51–614)** before that — pricing.md Appendix T)*;
[nr4a3-program-map.md → Spend summary](../manuscripts/nr4a3-program-map.md) carries the derivation and is
authoritative. *(This table previously omitted the `5c` row, which is where a stray `~$128` total for the whole
ladder came from. Fixed 2026-07-25.)*

At the `$0.35–0.39/hr` the fan-out actually paid, the same work is **~$330**. The 5a-KS **confirmatory**
protein-mutation wedge is not in this table: its engine qualified on 2026-07-25, but its NR4A cost is a
particle-count projection (~$4.6 for 3 replicates), not a measured rate, so it stays out of the total.

---

## 7. WHAT WAS BELIEVED BEFORE, AND WHICH MEASUREMENT RETIRED IT

Kept because the reasoning was not stupid — each step was a locally sensible response to a real incident, and
the failure was structural: numbers lived in several places, so a correction never reached all of them.

| policy | why it was adopted | what retired it |
|---|---|---|
| `× 1.1` (floor-hugging) | preemptions assumed cheap (~3-min boot) | measured ~20-min reload on the ~6 GiB image |
| `× 1.5` | reload is expensive, buy retention | the NR-V04 covalent tail churned anyway |
| **`× 1.9`** | tail legs needed a continuous ~4 h; a bigger premium holds the box | **the reload was self-inflicted** — our reaper deleted paused instances (F3) |
| `× 1.25` + on-demand cap | ×1.9 exceeded on-demand on 20/23 4090s | still a multiple of a floating floor; **the bid ladder (F1) showed the premium is paid on every hour** and (F2) cannot cover on-demand preemption |
| "default to on-demand while `min_bid ≈ dph_base`" | that equality looked like "no interruptible discount" | it was a **query artifact** — a bid-type search reports `dph_base` *as* the floor, so it compared the floor to itself |
| reservation price / adaptive UCB duty-cycle quantile | treat the bid as a limit order and wait for cheap capacity | the floor is **flat** (18/21 days at trough), so there is almost nothing to wait for; and it never reached the launch path |
| "rank offers by `min_bid`" | the floor looked like the cost | it is neither what we pay (the bid is) nor what we get (throughput); **it is the single most expensive of these mistakes** at 5.43× best-to-median |

**Two options deliberately rejected, with reasons:**
- **Reserved instances** (Vast's third tier, "up to 50% off" on 1/3/6-month commitment). Rejected: it discounts
  *on-demand*, and interruptible at the floor is already **5–9×** below on-demand at the cheap tail. A monthly
  commitment also buys continuous capacity we do not need — the ladder is ~$130 spread over weeks.
- **Prepaid-credit discount.** Real but thin: only **25%** of 4090/3090 offers advertise one, median **10%**
  among those (max 40%). Worth taking where it exists; not worth restructuring around, and it does not change
  any ranking.

---

## 8. WHERE THIS LIVES IN THE CODE

| what | where |
|---|---|
| the model, the policy, the bid, the ranking, the repricing CLI | [`vast_cost_model.py`](../modalities/vast_cost_model.py) |
| launch path (bid + offer selection) | `gpu_backend.py` — `_vast_bid_price`, `_select_cheapest_offer`, both delegating |
| market/doc evidence pull (CI, read-only) | [`vast_market_intel.py`](../modalities/vast_market_intel.py) |
| the pay-your-bid experiment | [`vast_bid_semantics_probe.py`](../modalities/vast_bid_semantics_probe.py) |
| hazard/quantile machinery (advisory, not on the launch path) | `vast_bid_optimizer.py` |
| tests pinning every claim above | `tests/test_vast_cost_model.py` (36), `tests/test_gpu_backend.py` |

`VAST_BID_FLOOR_MULT` survives as an **unset escape hatch** — a leg that genuinely cannot tolerate pauses may
still want to buy retention. Unset, the derived policy runs.
