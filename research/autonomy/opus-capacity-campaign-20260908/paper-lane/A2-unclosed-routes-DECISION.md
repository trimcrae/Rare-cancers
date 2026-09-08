<!-- collected 2026-09-08T07:19:04Z by campaign coordinator; agent id a6675fd70c358f364; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a6675fd70c358f364.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker
**A2**, OPUS-CAPACITY-CAMPAIGN-20260908, cross-paper route scouting on `systems/graph/routes.json`.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report as `claude-opus-5`. Nothing in the environment confirms a served model; the coordinator must extract it from the transcript. Env output (start and end) is pasted below and in the provenance section; long proxy/no-proxy variables trimmed at end only.

**Start** `date -u` = `Tue Sep 8 07:10:45 UTC 2026`; HEAD `666b1fd2a6d324233291c24ec1429f24609954b1`; `git status --porcelain` empty; `df -h /` = 20G avail (47%).
**End** `date -u` = `Tue Sep 8 07:16:38 UTC 2026`; HEAD `2e803291d58c4a5a8fc3be0dce4e4a4a721e74e9` (advanced under me — coordinator collection commits, as the brief predicts); `git status --porcelain` **empty**; `df -h /` = 20G avail. ≥10 GiB floor honoured throughout.

Start env (literal, secrets redacted) is in the first tool call of this session and is reproduced end-of-run above. Key rows both times: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_CHILD_SESSION=1`. **No variable names a model.**

## Stream and question
83 routes in `systems/graph/routes.json`. Question: among routes that are NOT closed, which carries an unmet scientific question whose decisive inputs are committed and reachable — and is it a distinct paper rather than a relabelled old one?

## Prior-work and exclusion check
Read in full first: `CLOSED-WORK.md`, `COMMON-BRIEF.md` (1,029 lines, both halves), `CORPUS-CONTEXT.md`, `paper-lane/DECISION-synthetic-line-and-S6.md` (including the 06:34 narrowing, the 06:40 S6 result and the 06:44 retention/scope corrections).

**Coordinator scope correction, applied mid-run.** My dispatch's "treat every NR4A-labelled route as excluded" was withdrawn. I retracted my rank-11 block exclusion and re-judged all six affected routes on named holds only. Excluding by label is wrong here — the disease is NR4A3-driven — and I record that my first pass made that error before the correction arrived.

Exclusions I applied, each with its cited recorded reason:
- **RT-ASO** — CLOSED-WORK: the ASO/NAT submission and Qeios history belong to the submission owner; frozen deliverables not to be edited or re-reviewed.
- **RT-HORMONE-PARTNER, RT-NR2F1** (`PUB-NR-OUTSIDE-NR4A3`) — P6's proposed NR4A3 negative-results/architecture manuscript and its claim corrections are explicitly not authorized. The endpoint's label is incidental.
- **P1–P5 endpoint routes** — their own recorded dispositions (notably AUT-064's "ANSWERED — no" on PUB-CARE-DELIVERY) and this campaign's collected P-results.
- **RT-POPULATION-REGISTRY** — CLOSED-WORK: "User rejected the registry ICD-O classification paper."
- The parked synthetic figure-validation family, GSE4303/GSE28866, PMID **22592656** (not 22562656), W25/GSE243553/primary-article/Results/novelty, the NR4A Perspective, the genome-access probe restriction: none touched, none rephrased, none rerouted.
- Routes with `closure_kind` `premise_false` / `definitional` / `arithmetic_over_fixed_fact` / `confound_in_the_system` treated as closed on their merits and not restated.

No network retrieval. No script, test, generator or preflight run. `atr_hrd_sarcoma_series.py` never invoked. Repository untouched (`porcelain` empty at both ends).

## Un-closed route enumeration
83 routes; 31 carry a closed `closure_kind` (12 `instrument_limit`, 10 `premise_false`, 4 `authorization`, 3 `definitional`, 1 `confound_in_the_system`, 1 `arithmetic_over_fixed_fact`). **52 un-closed** — 24 `open`, 28 with no `closure_kind` at all. All 52 are in the retained census with grade head, state block, blockers and disqualifiers.

**The decisive structural fact, from the two graph files alone:** every un-closed route maps to an endpoint that is `drafted` or `posted_preprint`, *except* the routes of the six P1–P6 endpoints and PUB-ASO. The only other non-drafted endpoint on the board, `PUB-PARKED-MODALITIES` (unwritten), owns five routes and **all five are `instrument_limit`** — closed on their merits.

## Shortlist with resolved pointers

| route | endpoint / state | pointer resolved | what it actually contains | grade |
|---|---|---|---|---|
| RT-HOST-FACTOR | PUB-MORTALITY-MECHANISM / **drafted** | `emc-host-factor-model.json` (19,890 B), `emc-host-factor-inputs.json` (12,845 B), `emc-mortality-decomposition.json`, paper `:46-51` | 4 factors, 3 modelled in compartment B; every sarcoma-specific estimate recorded at zero as association-only; diabetes/hypertension `factors_not_entered`; paper's own STATUS block says the band is "a queued item, not a done one" | PRIMARY (committed bytes) |
| RT-EARLY-PALLIATIVE | PUB-MORTALITY-MECHANISM / drafted | `EV-TEMEL-2010`, `EV-PACO-2024`, `EV-CHEN-2023-CEPC`, `EV-KOCHOVSKA-2020` | three independent RCTs with OS benefit — **all NSCLC, months-scale**; the route's own record states the transfer to a decades-scale history is answered by none of them | RETRIEVED (class-inherited) |
| RT-TRIAL-REACH | PUB-STRATEGY-ARCH / drafted | `care-delivery/emc-trial-reachability.md` (20,985 B) | route is `status: ready`, `work_state: complete`, `maturity: computed`, `confidence: moderate`, no blockers; best_next_action is literally "Publish the eligibility map" — the manuscript already exists | RETRIEVED |
| RT-VTE-PROPHYLAXIS | PUB-MORTALITY-MECHANISM / drafted | `emc-terminal-events.json` (14,836 B), AVERT/CASSINI | both feasible validations DONE and **negative**: zero true VTE deaths in corpus; no OS benefit in either trial | RETRIEVED, negative preserved |
| RT-CARFILZOMIB | PUB-REPURPOSING / drafted | `EV-BANGERTER-2023` (PMC9813045), `EV-MAKI-2005` | ex-vivo on n=2 patient-derived models; a **negative** class-level clinical read in the parent histology | ASSOCIATION / ex-vivo |
| RT-PPARG-DOWNSTREAM | PUB-REPURPOSING / drafted | `repurposing/pparg-direction-emc.md` (28,523 B), fusion-output SI §S4 | both cheap tests RUN; direction unresolved; residual is a study-design limit (bulk archival tissue), not missing data | UNRESOLVED |

## Ranking and criterion
**Criterion, stated before ranking: paper merit = would a competent reader of the rare-sarcoma literature change a belief, on evidence at PRIMARY or RETRIEVED grade, at an endpoint not already drafted or posted. Tractability, cost and runnability are not scored.**

Per the coordinator's correction I kept three tests separate — **T1 distinct**, **T2 input actually available**, **T3 non-overlap with a drafted/posted endpoint**:

| route | T1 | T2 | T3 | eligible |
|---|---|---|---|---|
| RT-HOST-FACTOR | PASS | PARTIAL (repair input committed; diabetes/hypertension need network) | **FAIL** | NO |
| RT-EARLY-PALLIATIVE | PASS | FAIL (no trial in an indolent population exists) | **FAIL** | NO |
| RT-TRIAL-REACH | PASS | PASS (US) / FAIL (non-US needs authenticated endpoint) | **FAIL** | NO |
| RT-VTE-PROPHYLAXIS | PASS | PASS | **FAIL** | NO |
| RT-CARFILZOMIB | PASS (`distinct_from` RT-TRABECTEDIN holds) | FAIL (two $0 texts need network) | **FAIL** | NO |
| RT-PPARG-DOWNSTREAM | PASS (`distinct_from` RT-RXR holds) | FAIL (BLK-NO-WET-LAB) | **FAIL** | NO |
| RT-FAP-RLT | PASS (`distinct_from` RT-SSTR2 holds) | FAIL (protein/imaging gap) | **FAIL** | NO |
| RT-VACCINE-COMBINATION | PASS (`distinct_from` RT-VACCINE holds) | PARTIAL (Stage 0 unrun) | **FAIL** | NO |

**Zero routes pass all three.** On `distinct_from`: only 15 of 52 un-closed routes carry it, and the mortality family carries none. Four claims tested against the tree and all four hold — but the load-bearing observation is that **`distinct_from` asserts distinctness from another *route*, never from an already-drafted *manuscript*, and in every case tested the manuscript is what disqualifies the row.** A `distinct_from` that holds is not paper novelty.

## DECISION: recommended next checkpoint

**Nothing qualifies as a distinct paper.** The top-merit unmet question is **RT-HOST-FACTOR**, and it is disqualified by requirement 3. The recommended checkpoint is therefore explicitly an evidence repair inside an existing drafted endpoint, not a paper.

**Measured defect found (PRIMARY, committed bytes only):** `emc-host-factor-model.json` sets `competing_share_of_deaths_used = 0.394` and sources it to "within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients". The paper's own Appendix A.1 (`emc-mortality-mechanisms-paper.md:391`) reads verbatim: *"Competing share, 39.4 per cent superseded by 21.7 per cent."* The paper's Results use **21.7 %** (`:241`, 163 patients, 18 disease / 5 other-cause deaths), corroborated independently at 23.0 % by relative survival (`:255`). Two consequences: (1) the model's load-bearing denominator is the superseded estimator, **high by 39.4/21.7 = 1.82×**, inflating every compartment-B band it produces; (2) the model's source sentence is now **false** — `direct_cause_split` *is* a pairing on the same patients, and it is what the paper adopted.

**(a) Unmet question and why it matters.** What share of death after an EMC diagnosis is attributable to common, independently treatable host conditions, and what is the honest upper band on treating them? It matters because this is the only route in the portfolio whose intervention already exists and is already approved, and because the portfolio's entire antitumour argument is bounded by the competing-mortality share.

**(b) Exact reachable inputs and access limits.** Committed, $0, no network: `emc-host-factor-inputs.json`, `emc-host-factor-model.json`, `emc-mortality-decomposition.json`, `emc-terminal-events.json`, `emc-mortality-mechanisms-paper.md`. **Not reachable:** the model's own `factors_not_entered` (type 2 diabetes/metformin, hypertension) needs a fresh retrieval — a network act outside worker authority; host-factor prevalence in a real EMC cohort is blocked on `BLK-NO-EMC-DATA` and unobtainable here.

**(c) Contribution and novelty uncertainty.** Correct the model's competing-share input, then write the corrected compartment-B band into the existing draft. **No novelty is claimed** — this is a correction plus a queued section. Whether the band is scientifically interesting at 21.7 % rather than 39.4 % is UNKNOWN until recomputed.

**(d) Distinction from prior no-gos.** Not P1–P6 (different endpoint; PUB-CARE-DELIVERY's AUT-064 "no" names that endpoint, not this one); not the synthetic figure-validation family (no digitization, reconstruction or sweep); not W25/GSE243553; not the NR4A Perspective; touches no CLOSED-WORK denied source; no record or consumer census. **It is also not a distinct paper — that is the decision, not a claim of distinction.**

**(e) Finite acceptance.** Owner (not a read-only worker) re-runs `emc_host_factor_model.py` with the share from `direct_cause_split`. Accept when: (i) `competing_share_of_deaths_used` equals the paper's adopted value and `competing_share_source` names `direct_cause_split`; (ii) the false "only pairing" sentence is replaced; (iii) every compartment-B figure moves by the recomputed ratio and none is quoted outside its band; (iv) `pytest` (never `python3 -m pytest`) over the module's tests exits 0 with the tree otherwise unchanged. Any clause failing is a fail, not a waiver.

**(f) Stop condition.** Stop when the model reproduces from the corrected input — or when a committed record shows the within-series estimator was chosen deliberately, in which case this is a documentation defect and the branch stops there. Do not expand into re-deriving the decomposition, re-retrieving effect sizes, or writing a paper.

## Routes rejected and why (exact missing condition each)
Full 52-row table is in the retained census. Representative reasons, all endpoint-`drafted` unless noted: RT-EARLY-PALLIATIVE — needs a supportive-care trial in an indolent population; none exists. RT-TRIAL-REACH — needs non-US registry coverage via an authenticated endpoint this programme lacks; publishing it *is* the existing draft. RT-VTE-PROPHYLAXIS — needs an EMC-specific thrombotic base rate (`BLK-NO-EMC-DATA`); both feasible items already done and negative. RT-TREATMENT-HARM — needs late cardiac outcome data in anthracycline-exposed EMC survivors; the corpus count (2/52, both postoperative skull-base, PMID 23115670) neither corroborates nor refutes it. RT-CARFILZOMIB — two named $0 full texts require network. RT-PPARG-DOWNSTREAM — needs a readout separating PPARγ output from adipogenic composition; a study-design limit no further expression cohort lifts. RT-FAP-RLT / RT-PRAME-IMMTAC — protein/imaging gap, `BLK-NO-WET-LAB`. The five `PUB-BIOMARKER-DEP` rows carry no `closure_kind` but their grade text is an explicit NOT SUPPORTED/SPLIT verdict; missing conditions are wet-lab or clinical-cohort inputs.

**Inspection of the four `closure_kind: authorization` rows** (inspection only; nothing tested, weakened or routed around). RT-ASO-ASK, RT-ATR-PANEL, RT-TRABECTEDIN-PPARG, RT-SSTR2. In **all four**, the row's own `next.blocked_on` names `BLK-NO-WET-LAB`, not a permission gate — so the `authorization` label is **partly stale**. The standing boundary is two conditions, and both must be named: (1) an absent bench, which is a *capability* (CLAUDE.md §5, "there is no wet lab"); (2) an un-granted *permission* for the outreach act (CLAUDE.md §3), whose enforcer is the user, not a script. RT-TRABECTEDIN-PPARG's reason is freshest (updated 2026-08-28: the expression read landed and does not establish direction, so the ask would now go out without one). I did not open or test `publication-authority.json`, so whether any current grant covers such an ask is **UNKNOWN**, stated as unknown rather than assumed either way. None becomes executable; none is proposed for revival.

## Durable artifacts written and verified
`/tmp/claude-0/a2-retained/` — **not deleted**, parent alone collects:
- `unclosed-route-census.json` — `741593e091f3b36171842f1131b0e4fc46aa0672caad45d3019c3d4ab2ad29f0` (34,671 B; all 52 un-closed rows with grade head, state, blockers, disqualifiers)
- `A2-DECISION.md` — `53bcfd3defc59a5b1871917e989a33dc4c1777a5b04b46aa2f0ba213e9c9eecb` (13,054 B + appended correction)
- `SHA256SUMS`

`sha256sum -c SHA256SUMS` → **2 of 2 OK**, re-run after the correction was appended.

## Validation evidence
**RUN:** `date -u`, `git rev-parse HEAD`, `git status --porcelain`, `df -h /`, `env | grep …` (start and end, both pasted). Python reads of `systems/graph/routes.json` and `systems/graph/publications.json`, exit 0. `grep`/`sed` reads of the six manuscripts and four JSON artifacts named above. `sha256sum -c SHA256SUMS` → `unclosed-route-census.json: OK`, `A2-DECISION.md: OK`, exit 0.
**PROPOSED (NOT RUN):** the `emc_host_factor_model.py` re-run and its `pytest` gate — that is the recommended checkpoint and it is an owner act; I am read-only.
**NOT RUN:** every repository script, test, generator, `preflight.sh`, `atr_hrd_sarcoma_series.py`, and all network retrieval.

## Limitations
The census is a read of two graph files at one HEAD; a `drafted` endpoint state is a graph assertion, and I did not audit whether each drafted manuscript actually covers each contributing route — I verified this only for the mortality family (§3.2/§3.3 present; host-factor and supportive-care transfer explicitly absent per the paper's own STATUS block). The 1.82× ratio is arithmetic over two committed values, not a re-derivation of either estimator. I did not open `publication-authority.json`, so the authorization inspection reports the rows' recorded reasons, not the current grant. `COMMON-BRIEF` (W57) records `routes.json` route 81 — RT-VTE-PROPHYLAXIS, in the family I recommend — as attributing 162 to "death-cue sentences" where 162 is the paper count and the sentence count is 577; I did **not** re-measure that settled census, but any write-up in this family must resolve the key, not the number. No clinical efficacy, safety, selectivity, therapeutic-window or readiness claim is made or implied anywhere above; there is no wet lab.

## Stop condition
Set: stop at a delivered ranked decision. **MET.** The decision is a negative — nothing qualifies as a distinct paper — with per-route reasons and exact missing conditions, plus one recommended checkpoint that is explicitly not a paper.

## Tool-call and wall-clock count actually used
**24 tool calls**, **07:10:45 → 07:16:38 UTC = 5 min 53 s**. Both inside the ~40/~40 target.
