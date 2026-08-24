---
id: DOC-GPU-MARKET-BACKFILL-2026-08
title: GPU market backfill, 2026-06-15 → 2026-08-24 — the window the weekly Routine never delivered
level: —
kind: runbook
status: live
canonical_for: [the 2026-06-15 to 2026-08-24 GPU-market reading]
purpose: >
  Close the gap left when the weekly field-scan Routine stopped delivering, by reading what actually
  changed in the GPU market over that window and grading each item by provenance. Answers one
  question only — should we change what we buy, or how we buy it?
scope: >
  Evidence and a recommendation. It sets no price, no basis, no gate and no provider choice: the cost
  evidence lives in pricing.md, the provider plan in cheap-gpu-plan.md, and provider choice is
  trimcrae's. Nothing here is a planning number.
audience: [maintainers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# GPU market backfill, 2026-06-15 → 2026-08-24

## ★ VERDICT: NO. Nothing found in this window changes what we buy or how we buy it.

The quantity that sets our cost is the **cheapest interruptible RTX 4090 floor on our own filtered
board**, and it did not move. Across **467 hourly samples** of our own offer search, its weekly median
was **$0.1333/hr** in each of the four full weeks 2026-W31 through 2026-W34 and **$0.1350/hr** in the
partial W35 — while qualifying board depth held at a weekly median of **34–43 offers**. A
third-party daily series over the wider window agrees: the Vast platform-wide RTX 4090 daily low
averaged **$0.1357/hr** in July and **$0.1347/hr** in August.

**Recommendation: change nothing.** Do not reprice the ladder, do not revise the bid policy, do not
move provider, do not re-rank cards. The planning basis and the buy line are untouched by anything
below — their homes are [pricing.md](./pricing.md) and
[`inflight_usd_per_ns.py`](../modalities/inflight_usd_per_ns.py), and this file deliberately does not
restate or recompute either.

⛔ **The numbers in this file are OBSERVATIONS OF A MARKET, NOT A BASIS.** They are the output of the
two artifacts named in §2 and regenerate from them. None of them supersedes anything in
`pricing.md`; none of them is a cost basis; none is a $/ns.

---

## 1 · Why this file exists, and what was actually lost

The weekly field-scan Routine (`trig_01X5xHy1cmkLjkATEijZSNJf`) is credited in
[method-watch.md](../method-watch.md) §1 with auto-capturing GPU-market changes into
[cheap-gpu-plan.md](./cheap-gpu-plan.md). It has delivered nothing since 2026-07-13.

**Checked for $0 before writing this sentence:** `cheap-gpu-plan.md` contains no "Auto-captured"
section — `grep -n -i "auto-captured"` returns nothing. So the Routine did not write a section that
later drifted; **it never wrote one at all.** Nothing was lost or overwritten. What was lost is the
*reading*, which is what this file replaces.

---

## 2 · What was actually measured, and how far it reaches

| instrument | what it reads | coverage | grade |
|---|---|---|---|
| **Our own hourly offer sampler** — `vast-price-sample.yml mode=sample` → [`vast-price-history.jsonl`](../modalities/vast-price-history.jsonl) on `modalities-cache` | the **narrow filtered subset we can actually rent** (`rtx4090`), cheapest and median interruptible floor + qualifying-offer count, hourly | **2026-07-25 16:56 Z → 2026-08-24 13:17 Z**, 467 samples | **A — first-party** |
| **Third-party daily tracker** — `fusion-cpu-extras.yml task=vast_price_history` → [`vast-price-history-raw.json`](../modalities/vast-price-history-raw.json), dispatched for this file (**run 32734470066**, 2026-08-24) | **platform-wide** RTX 4090 daily low, per provider × kind | **2026-07-05 → 2026-08-24**, 51 days | **C — third-party aggregator** |

**⛔ 2026-06-15 → 2026-07-04 IS UNREAD, AND NO INSTRUMENT REACHES IT.** That is **20 of the window's
70 days**. The tracker returned 51 days against a `--days 60` request and the sampler did not exist
yet. Everything below about that fortnight is press or nothing. Do not let §3's "flat" be read as
covering it.

### ⚠ Two provenance defects in the instruments themselves, both found while using them

- **The `vast_price_history` job is labelled as Vast's own data and is not.** The workflow comment
  reads *"Pull Vast's OFFICIAL historical market metrics"*, and the script's module docstring names
  `console.vast.ai/api/v0/metrics/gpu/history/`. The fetched artifact records
  `_source.path = https://gpu.watchworks.dev/api/history`, `auth_mode: none` — a **third-party
  tracker**. This is not a silent failure: the script's own source comment explains that Vast's
  endpoint is login-gated (established by CI run 30130107337) and that gpuwatch is the documented
  fallback. But a reader who quotes the artifact from the workflow's label will call a third-party
  series official. **Graded C above for that reason.**
- **80 of the 182 rows in the committed `vast-price-history.jsonl` are contaminated legacy rows.**
  They carry `ts: null` and no `provider` field, and they pool providers — RunPod-secure at $0.69/hr
  sits in the same "distribution" as Vast at $0.13/hr. This is exactly the defect the parser's own
  comment says was fixed; the fix stopped *producing* such rows but never purged the ones already
  committed to an append-only log. The 102 rows appended since are correctly dated and
  provider-filtered. **Anyone pooling that file without filtering `ts is not None` gets a
  cross-provider spread masquerading as a price history.** Not fixed here — it is another lane's
  evidence log and other agents are active.

---

## 3 · Findings, each graded, each framed as impact on OUR cost

| # | finding | impact on our cost | grade |
|---|---|---|---|
| 1 | **Our own filtered RTX 4090 board is flat.** Weekly median of the cheapest interruptible floor: W31 **$0.1333**, W32 **$0.1333**, W33 **$0.1333**, W34 **$0.1333**, W35 (partial) **$0.1350**. Median floor **$0.3333** in both months. Qualifying offers, weekly median: 37 / 36.5 / 39 / 34 / 43. *(W30 is the sampler's first 18 samples at board depth 6 — a startup artifact, not comparable.)* | **None.** This is the input to everything we pay. Five consecutive weeks at one value. | **A** |
| 2 | **Platform-wide Vast RTX 4090 daily low is flat over 51 days.** July mean **$0.1357/hr**, August mean **$0.1347/hr** (−0.7 %); range $0.054–$0.2015 across single days. Vast "verified" slice **$0.2662 → $0.2737** (+2.8 %). | **None.** Corroborates #1 on a wider population, and extends the flat reading three weeks further back. | **C** |
| 3 | **RunPod RTX 4090 did not get cheaper; the secure tier got dearer.** Community-cloud daily low **$0.34/hr on all 51 days, without a single move**. Secure **$0.69 → $0.74** (August mean $0.7317). | **None, and it removes a hypothetical.** RunPod is not undercutting our lane; the gap widened slightly. | **C** |
| 4 | **Vast's own pricing pages, read 2026-08-24:** RTX 3090 from **$0.07/hr**, RTX 4090 from **$0.13/hr**, RTX 5090 from **$0.21/hr**, RTX PRO 6000 WS from **$0.67/hr**, RTX PRO 6000 S from **$1.00/hr**. | **None.** The 4090 entry point matches #1 and #2. Consistency across three independent readings is the point of this row. | **B — provider's own pricing page**, read from the page titles; `vast.ai` is **egress-blocked**, so the page bodies could not be fetched |
| 5 | **RTX 5090 is broadly available and cheap, but its $/ns is not answerable from price.** Listed across 14+ providers; Vast entry **$0.21/hr**. Our throughput table holds a **single-host** 5090 bench (registered in `pinned-figures.json`), not a median-of-N. | **Potentially real, currently UNKNOWN.** A card's $/ns is price ÷ throughput and **we have no gradeable throughput for it**. A price fetch cannot settle this; `vast-bench-sweep.yml` can. See §5. | **B / UNKNOWN on the decision** |
| 6 | **RTX PRO 6000 Blackwell has entered the marketplace tier.** On Vast at $0.67/hr (WS) and $1.00/hr (S); market median across 55 configurations $1.89/GPU-hr. | **None today.** No entry in `MEASURED_NS_PER_DAY_84K`, so it is unpriceable by our ranking and excluded from selection by design. Same open question as #5, at ~5× the hourly rate. | **B / UNKNOWN** |
| 7 | **No new provider or credit programme relevant to MD/FEP appeared in the window.** Searched for marketplace entrants and for free/academic credit routes; the named players are unchanged. Salad still lists RTX 4090 on-demand at **$0.160/hr**, already in the plan. | **None.** No route to add. | **C** |
| 8 | **Modal's free tier is unchanged at $30/month, use-it-or-lose-it.** The 2026 change was to Shared-API access tiering, not to the credit. | **None.** [`credit-status.json`](./credit-status.json)'s Modal cap stands. | **C** |
| 9 | **Vast storage still bills continuously on stopped instances, by the same mechanism.** No change to the billing model found. | **None.** The storage line in [pricing.md §A](./pricing.md) stands as written; the rate is not restated here. | **C** |
| 10 | **Spot-discount compression since ~May 2026 is a DATACENTER-class phenomenon and does not reach us.** Reported for H100/B200 pools — in July an H100 spot pool was tight enough that spot exceeded on-demand. Our lane is consumer-card interruptible, where #1–#3 show no compression at all. | **None — and this is the row most likely to be misread.** Do not import a datacenter-GPU spot narrative into our bid policy. | **C** |
| 11 | **AWS GPU price cuts are outside this window.** The P5/P5en (up to 45 %) and P4d/P4de (up to 33 %) reductions took effect **June 2025**, not 2026. | **None.** AWS is not the go-forward lane regardless (pricing.md §A). | **C** |
| 12 | **NVIDIA's RTX 50 SUPER refresh has not landed and has slipped.** Reported held by NVIDIA as of July 2026 on 3 GB GDDR7 memory cost, with talk of CES 2027; expected uplift over non-SUPER parts is single-digit-to-10 %. | **None.** No new consumer part to bench in this window. A ~10 % uplift would not reorder a board whose gradeable offers span ~4× in $/ns. | **C — press/rumour, and it is rumour about an unreleased part** |

---

## 4 · One item that is NOT a change in the window, but should be recorded anyway

**ACCESS-CI is closed to us, and more firmly than [access-allocation-request.md](./access-allocation-request.md)
records.** That draft hedges: *"an unaffiliated independent researcher may not be directly eligible as
PI."* The current policy is not a hedge — ACCESS requires a US-based institutional affiliation **and a
matching institutional email address**, with personal domains (gmail.com, yahoo.com) prohibited, and
will not process new requests, supplements, transfers or extensions for unaffiliated PIs or where
email domain and organization do not match.

- **This is dated 2025-09-30 — BEFORE this window.** It is not a delta and must not be reported as
  one. It surfaced because the window search asked whether any free-credit route had opened.
- **Impact on our cost:** `cheap-gpu-plan.md`'s outlook line — *"low hundreds of dollars (or free if
  ACCESS lands)"* — rests on a route that a `trimcrae@gmail.com` PI with no affiliation cannot enter.
  The LLC path already parked in that file is the same unlock, and it stays trimcrae's decision.
- **Grade: C.** The policy page and the ACCESS announcement are both **egress-blocked** from here, so
  this is search-summary provenance, not a read of the page. **Before anyone acts on it, read
  `allocations.access-ci.org/allocations-policy` directly.**
- **NAIRR is a separate route and is not closed by the above**, but its eligibility classes (US
  academic, non-profit, federal/FFRDC, state/local/tribal, or a startup/small business **holding a
  federal grant**) do not obviously admit an unaffiliated individual either. **UNKNOWN**, and worth
  one authoritative read rather than an assumption in either direction.

---

## 5 · What I could NOT check — stated plainly

- **2026-06-15 → 2026-07-04.** No first-party or third-party series reaches it. 20 of 70 days.
- **Every provider dashboard.** Real bid/on-demand cross-sections for RunPod, Salad, Lambda, Crusoe,
  CoreWeave, Together and Modal sit behind auth. Rows 3, 7 and 8 are aggregator readings, not console
  reads.
- **Vast's own metrics API.** Login-gated; the API key is refused (`auth_error: This action requires
  login`). That is why row 2 is graded C and not A.
- **Egress-blocked hosts**, all confirmed blocked from this sandbox this session: `vast.ai`,
  `docs.vast.ai`, `getdeploying.com`, `www.spheron.network`, `allocations.access-ci.org`,
  `support.access-ci.org`. Rows 4 and §4 would be one grade better if these were readable — a CI
  runner can reach them.
- **Any throughput reading.** Nothing here was benched. **$/ns is price ÷ throughput, and this file
  only read the price axis** — which is precisely why rows 5 and 6 stop at UNKNOWN rather than
  recommending a card.
- **The engine axis.** Whether the OpenMM/OpenFE version our image pins moved in the window returned
  **contradictory** evidence (a search summary and the GitHub releases page disagree on both the
  latest version and its date). **UNKNOWN, deliberately left so** — a remembered or half-sourced
  version number is worth nothing, and it is out of scope for a market read.

---

## 6 · The only thing that would change the answer, and it is not a price fetch

Rows 5 and 6 are the sole live leads, and **both are throughput questions wearing a price costume.**
A cheaper card that we cannot grade cannot win selection — by design, `card_of` resolves it to `None`
and the ranking excludes it (pricing.md §A.2, §A.3).

So the one warranted follow-up is a **`vast-bench-sweep.yml` pass** (`mode=launch`, `replicates≥3`,
fresh wave, then `mode=collect`) to put RTX 5090 — and, if a cheap offer exists, RTX PRO 6000 — on the
same median-of-N estimator as the three anchored cards. **That is real GPU spend, small** (the
2026-07-27 re-anchoring of the whole table cost ≈$1.74), and it is **trimcrae's call, not this
file's.** It is also the only route by which anything in this window could turn into a cost saving.

Everything else on this page says: **the market did not move, and neither should we.**
