# A2 DECISION — un-closed routes in systems/graph/routes.json
Repo HEAD read: 666b1fd2a6d324233291c24ec1429f24609954b1 (live checkout /home/user/Rare-cancers)
Written 2026-09-08 UTC. Read-only worker; no repository file was modified.

## Criterion (stated before ranking)
Paper merit = would a competent reader of the rare-sarcoma literature change a belief, on evidence
at PRIMARY or RETRIEVED grade, at an endpoint that is NOT already drafted or posted. Tractability,
cost and runnability are explicitly NOT scored. A cheap question with a small answer ranks below an
expensive question that moves a reader.

## DECISION: NOTHING QUALIFIES AS A DISTINCT PAPER.
Structural, and it is decidable from the two graph files alone:
- 83 routes; 31 carry a closed closure_kind (12 instrument_limit, 10 premise_false, 4 authorization,
  3 definitional, 1 confound_in_the_system, 1 arithmetic_over_fixed_fact). 52 are un-closed
  (24 `open`, 28 with no closure_kind).
- Every one of those 52 routes maps to a publication endpoint whose state is `drafted` or
  `posted_preprint`, EXCEPT the routes of PUB-IPD-SURVIVAL, PUB-CARE-DELIVERY, PUB-LOCOREGIONAL,
  PUB-KINASE-LEADS, PUB-MATRIX-ADDRESS and PUB-NR-OUTSIDE-NR4A3 — which are exactly the P1-P6
  dispatches this worker is forbidden to revive — plus PUB-ASO.
- The one remaining non-drafted endpoint, PUB-PARKED-MODALITIES (unwritten), owns five routes and
  ALL FIVE are closure_kind=instrument_limit, i.e. closed on their merits.
Therefore, by method requirement 3, no un-closed route is a new paper. The honest result is a
negative, and it is reported as one.

## Top-merit un-closed route: RT-HOST-FACTOR (endpoint PUB-MORTALITY-MECHANISM, state=drafted)
It is the highest-merit unmet question on the un-closed board and it is STILL NOT A DISTINCT PAPER:
its endpoint is drafted at research/manuscripts/emc-mortality-mechanisms-paper.md.
The recommended checkpoint is therefore an EVIDENCE REPAIR inside an existing endpoint, not a paper.

### MEASURED DEFECT (the executable finding of this run)
research/manuscripts/emc-host-factor-model.json sets
  competing_share_of_deaths_used = 0.39399999999999996
  competing_share_source = "emc-mortality-decomposition.json, within-series (Meis-Kindblom 1999) --
                            the only pairing measured on the same patients."
research/manuscripts/emc-mortality-mechanisms-paper.md:391 (Appendix A.1) states verbatim:
  "**A.1 Competing share, 39.4 per cent superseded by 21.7 per cent.**"
and the paper's own Results use 21.7 % (:241, combined 163 patients, 18 disease / 5 other-cause
deaths) corroborated independently at 23.0 % by relative survival (:255).
research/manuscripts/emc-mortality-decomposition.json still carries BOTH: within_series[0]
.competing_share_of_deaths_pct = 39.4 (:48, carrying its own `estimator_mismatch` note) and
direct_cause_split, whose entries are the ratio-of-counts estimator the paper adopted.
Two consequences, both checkable from committed bytes:
 1. The host-factor model's load-bearing denominator is the SUPERSEDED estimator, high by a factor
    of 39.4/21.7 = 1.82. Every compartment-B band it produces is inflated by that factor.
 2. The model's source sentence ("the only pairing measured on the same patients") is now FALSE:
    direct_cause_split is a pairing on the same patients under the same ascertainment, and it is
    what the paper uses.
The paper's own editorial STATUS block (:46-51) says the compartment-B band is "a queued item, not
a done one". So the defect is upstream of an unwritten section, not inside published prose.
Grade of this finding: PRIMARY (committed bytes, read directly, no retrieval, no computation beyond
the quoted ratio).

## The six elements, for RT-HOST-FACTOR
(a) UNMET QUESTION. What share of death after an EMC diagnosis is attributable to common,
    independently treatable host conditions, and what is the honest upper band on what treating them
    could return? It matters because it is the only route in this portfolio whose intervention
    already exists, is already approved, and needs no EMC-specific evidence — and because the
    portfolio's whole antitumour argument is bounded by the competing-mortality share.
(b) REACHABLE INPUTS AND ACCESS LIMITS. Committed and readable at $0, no network:
    emc-host-factor-inputs.json (4 factors: obesity, smoking, statin-eligible CV risk, sarcopenia),
    emc-host-factor-model.json, emc-mortality-decomposition.json, emc-terminal-events.json,
    emc-mortality-mechanisms-paper.md. NOT reachable: the model's own `factors_not_entered`
    (type 2 diabetes/metformin, hypertension) requires a fresh literature retrieval — a network act
    outside this container and outside worker authority. Host-factor prevalence in an actual EMC
    cohort is blocked on BLK-NO-EMC-DATA and cannot be obtained here at all.
(c) PROPOSED CONTRIBUTION AND NOVELTY UNCERTAINTY. Contribution: correct the model's competing-share
    input to the estimator the paper adopted, then write the corrected compartment-B band into the
    existing drafted manuscript as its own bounded section. Novelty: NONE claimed as a paper — this
    is a correction plus a queued section of an existing draft. Whether a corrected band is
    scientifically interesting at 21.7 % rather than 39.4 % is UNKNOWN until it is recomputed.
(d) DISTINCTION FROM PRIOR NO-GOS. It is not P1-P6 (different endpoint, not unwritten/outlined), not
    PUB-CARE-DELIVERY (AUT-064's recorded publish "no" names that endpoint, not this one), not the
    synthetic figure-validation family (no digitization, no reconstruction, no synthetic sweep), not
    NR4A-labelled, not W25/GSE243553, and not a record or consumer census. It touches no CLOSED-WORK
    denied source. ⚠ It is ALSO not a distinct paper — that is the decision above, not a claim of
    distinction.
(e) FINITE ACCEPTANCE FOR THE NEXT CHECKPOINT. The owner (not a read-only worker) re-runs
    research/manuscripts/emc_host_factor_model.py with the competing share taken from
    direct_cause_split, and accepts when: (i) emc-host-factor-model.json's
    competing_share_of_deaths_used equals the paper's adopted value and its competing_share_source
    names direct_cause_split; (ii) the false "only pairing measured on the same patients" sentence is
    replaced; (iii) every compartment-B figure changes by the recomputed ratio and none is quoted
    outside its stated band; (iv) `pytest` (never `python3 -m pytest`) over the module's own tests
    exits 0 and the tree is otherwise unchanged. Failure of any clause is a fail, not a waiver.
(f) STOP CONDITION. Stop when the model reproduces from the corrected input, or when the correction
    is found to be wrong — i.e. if a committed record shows the host-factor model deliberately uses
    the within-series estimator for a stated reason. In that case the finding becomes a documentation
    defect, not an arithmetic one, and the branch stops there. Do NOT expand this into re-deriving
    the mortality decomposition, re-retrieving effect sizes, or writing a new paper.

## Ranking (paper merit; every row disqualified as a distinct paper)
1. RT-HOST-FACTOR — highest merit; live measured input defect above. DQ: endpoint drafted.
2. RT-EARLY-PALLIATIVE — the only intervention class on the board with randomised OS evidence
   (Temel 2010, PACO 2024, Chen 2023, all NSCLC, months-scale). Unmet: transfer to a decades-scale
   natural history, answered by none of them. Missing condition: a sarcoma or indolent-disease
   supportive-care trial; the route's own record reports a 388-paper corpus with one unrelated
   sarcoma hit. DQ: endpoint drafted; §4.3 of the draft already states it qualitatively.
3. RT-TRIAL-REACH — status ready, work_state complete, maturity computed, confidence moderate, no
   blockers, and its own best_next_action is "publish the eligibility map". Missing condition:
   non-US registry coverage, which needs an authenticated endpoint this programme does not have.
   DQ: endpoint PUB-STRATEGY-ARCH is drafted at care-delivery/emc-trial-reachability.md — publishing
   it is not a new paper, it is that paper.
4. RT-VTE-PROPHYLAXIS — both feasible-today validations DONE and both NEGATIVE (zero true VTE deaths
   in the corpus; no OS benefit in AVERT or CASSINI). Merit is a preserved negative. Missing
   condition: an EMC-specific thrombotic base rate, blocked on BLK-NO-EMC-DATA. DQ: drafted.
5. RT-TREATMENT-HARM — the corpus count (2/52 treatment-related deaths, both postoperative
   skull-base, PMID 23115670) neither corroborates nor refutes its chemotherapy-subtraction argument.
   Missing condition: late cardiac outcome data in anthracycline-exposed EMC survivors
   (BLK-NO-EMC-DATA + BLK-NO-WET-LAB). DQ: drafted.
6. RT-CARFILZOMIB — ex-vivo n=2 patient-derived models, plus a NEGATIVE class-level clinical read in
   the parent histology (EV-MAKI-2005). Missing condition: two named $0 full texts, both requiring
   network retrieval unavailable here. DQ: PUB-REPURPOSING drafted.
7. RT-COMPETING-MORTALITY / RT-RESPIRATORY-FAILURE — already written into §3.2/§3.3 of the drafted
   manuscript. Missing condition: registry death-certificate linkage (BLK-NO-EMC-DATA). DQ: drafted.
8. RT-PPARG-DOWNSTREAM — both cheap tests RUN; residual is a study-design limit (bulk archival tissue
   cannot separate PPARG receptor output from adipogenic composition), so no further expression
   cohort lifts it. Missing condition: BLK-NO-WET-LAB. DQ: drafted.
9. RT-FAP-RLT, RT-PRAME-IMMTAC, RT-TRABECTEDIN, RT-ICI-TKI, RT-MTAP-PRMT5, RT-TXN-CDK,
   RT-CHAPERONE, RT-ARGININE, RT-MDM2, RT-APOPTOSIS-DEP, RT-EZH2, RT-POLQ, RT-METHODS-PAPER,
   RT-ATR-ASSESS, RT-ENDPOINT-CHOICE, RT-MODALITY-CENSUS — all DQ: endpoint drafted. The five
   BIOMARKER-DEP rows carry no closure_kind but their grade text is an explicit NOT SUPPORTED /
   SPLIT verdict; their missing conditions are wet-lab or clinical-cohort inputs.
10. RT-POPULATION-REGISTRY — DQ twice: endpoint drafted, AND CLOSED-WORK records that the user
    REJECTED the registry ICD-O classification paper; its blocker BLK-REGISTRY-DUA is a permission,
    named as such and not routed around.
11. RT-VACCINE-COMBINATION, RT-ASYMMETRIC, RT-PANNR4A-EXVIVO, RT-TCIP, RT-FUSION-OUTPUT,
    RT-PARTNER-STRAT — DQ: NR4A-labelled family (EWSR1::NR4A3 junction / NR4A degrader /
    NR4A3 fusion partner), excluded under the binding exclusion regardless of merit.
12. RT-ASO — DQ: PUB-ASO, excluded by name and posted_preprint.
Routes in the P1-P6 endpoints (RT-IPD-SURVIVAL, RT-SURGICAL-QUALITY, RT-SURVEILLANCE,
RT-METASTASECTOMY, RT-RISK-MODEL, RT-SGK1, RT-DNAPK, RT-RET, RT-ALK-HIT, RT-LIMB-PERFUSION,
RT-LUNG-DIRECTED, RT-MDT-LUNG, RT-RT-INTENSIFY, RT-MATRIX-*, RT-IMMUNOCYTOKINE, RT-HYPOXIA-PRODRUG,
RT-HORMONE-PARTNER, RT-NR2F1) were enumerated and NOT assessed: binding exclusion.

## distinct_from claims tested (not trusted)
Only 15 of 52 un-closed routes carry distinct_from at all; the mortality-mechanism family carries
none. Four tested against the tree:
- RT-CARFILZOMIB vs RT-TRABECTEDIN ("unbiased screen hit vs mechanism-fit"): HOLDS as a statement
  about kind of support, but both sit in already-drafted endpoints, so the distinction does not
  create a paper either way.
- RT-PPARG-DOWNSTREAM vs RT-RXR ("different dimer"): HOLDS — RT-RXR is closed premise_false on an
  NR4A3:RXR dimer; this row is PPARG:RXR downstream. The distinction is real and still does not
  survive requirement 3.
- RT-FAP-RLT vs RT-SSTR2 ("stroma vs neuroendocrine target"): HOLDS; both are in the same drafted
  endpoint PUB-SURFACE-TARGETS, so distinctness from each other is not distinctness as a paper.
- RT-VACCINE-COMBINATION vs RT-VACCINE ("unit of evaluation"): HOLDS as written, but is moot —
  the route is NR4A-junction-labelled and excluded.
CAUTION recorded: distinct_from asserts distinctness from another ROUTE. It never asserts
distinctness from an already-drafted MANUSCRIPT, and in every case tested here the manuscript, not
the sibling route, is what disqualifies the row. A distinct_from that holds is not paper novelty.

## Known stale-record cross-check
COMMON-BRIEF (W57) records that routes.json route 81 attributes 162 to "death-cue sentences" where
162 is the paper count and the sentence count is 577. Route index 81 is RT-VTE-PROPHYLAXIS, in the
same mortality family as the top recommendation. NOT RE-MEASURED here (that census is settled); it
is flagged because any write-up of that family must resolve the key, not the number.

## What this run did NOT do
NOT RUN: any script, any test, any generator, any network retrieval, any preflight, any
atr_hrd_sarcoma_series.py invocation. No P1-P6 route was assessed. No synthetic, figure-validation,
point-count or digitization work. No record census, consumer census or infrastructure audit.
No clinical efficacy, safety, selectivity, therapeutic-window or readiness claim is made anywhere
above, and none follows from any of it.

---

# CORRECTION APPENDED — coordinator scope correction received mid-run, 2026-09-08
The dispatch's "treat every NR4A-labelled route as excluded" is WITHDRAWN by the coordinator. The
ranking section above used it at rank 11 and that use is retracted here. The section above is
preserved unchanged; this appendix supersedes it on the points below. THE HEADLINE DECISION IS
UNCHANGED, and it now rests only on named holds and on requirement 3.

## 1. Routes wrongly excluded by label, re-admitted and re-judged
| route | endpoint | endpoint state | verdict on the correct reason |
|---|---|---|---|
| RT-ASYMMETRIC | PUB-DEGRADER | drafted | NOT A NEW PAPER (req. 3). No named hold applies. |
| RT-PANNR4A-EXVIVO | PUB-DEGRADER | drafted | NOT A NEW PAPER (req. 3). No named hold applies. |
| RT-TCIP | PUB-TCIP | drafted | NOT A NEW PAPER (req. 3). No named hold applies. |
| RT-FUSION-OUTPUT | PUB-FUSION-OUTPUT | drafted | NOT A NEW PAPER (req. 3). Also: CLOSED-WORK records the tissue-RNA paper as already disseminated — an ownership fact, not an NR4A label. |
| RT-PARTNER-STRAT | PUB-FUSION-PARTNER | drafted | NOT A NEW PAPER (req. 3). No named hold applies. |
| RT-VACCINE-COMBINATION | PUB-VACCINE-PATH | drafted | NOT A NEW PAPER (req. 3). No named hold applies. Its unrun Stage 0 items are real, and they are additions to a drafted endpoint. |
| RT-ASO | PUB-ASO | posted_preprint | EXCLUDED by a named hold: CLOSED-WORK — "ASO/NAT submission and the Qeios version history belong to the submission owner / user", frozen deliverables not to be edited or re-reviewed. Also posted, so req. 3 applies independently. |
Routes still excluded by a NAMED hold, with the recorded reason cited:
- RT-HORMONE-PARTNER, RT-NR2F1 (endpoint PUB-NR-OUTSIDE-NR4A3) — held because P6's proposed
  NR4A3 negative-results/architecture manuscript and its claim corrections are explicitly NOT
  AUTHORIZED. That is the named hold; the endpoint label is incidental.
- The P1-P5 endpoint routes — held by their own recorded dispositions (PUB-CARE-DELIVERY's AUT-064
  publish decision "ANSWERED — no"; PUB-IPD-SURVIVAL/-LOCOREGIONAL/-KINASE-LEADS/-MATRIX-ADDRESS
  collected as P1/P3/P4/P5 results under this campaign's intake limits).
- RT-POPULATION-REGISTRY — CLOSED-WORK: "User rejected the registry ICD-O classification paper."
NONE of these is excluded for containing "NR4A" in an id, display name or grade text.
Re-admitting all six routes changes NO ranking outcome: every one of their endpoints is `drafted`,
so requirement 3 disqualifies each as a new paper on its own.

## 2. The three tests kept separate (per correction 1: distinct != eligible)
T1 DISTINCT — is it a genuinely separate question? T2 INPUT AVAILABLE — is the decisive input
actually reachable at $0 with no network and no bench? T3 NON-OVERLAP — is its endpoint outside
`drafted`/`posted`? A route needs all three plus merit; T1 alone recommends nothing.
| route | T1 distinct | T2 input available | T3 non-overlap | eligible |
|---|---|---|---|---|
| RT-HOST-FACTOR | PASS (two-compartment host-factor arithmetic exists nowhere else) | PARTIAL — the correction input is committed; diabetes/hypertension need a network retrieval | FAIL (drafted) | NO |
| RT-EARLY-PALLIATIVE | PASS | FAIL — the transfer needs a trial in an indolent population; none exists | FAIL (drafted) | NO |
| RT-TRIAL-REACH | PASS | PASS for the US half; FAIL for non-US (authenticated endpoint absent) | FAIL (drafted) | NO |
| RT-VTE-PROPHYLAXIS | PASS | PASS (both feasible items done, both negative) | FAIL (drafted) | NO |
| RT-TREATMENT-HARM | PASS | FAIL (BLK-NO-EMC-DATA + BLK-NO-WET-LAB) | FAIL (drafted) | NO |
| RT-CARFILZOMIB | PASS (distinct_from RT-TRABECTEDIN holds) | FAIL (two $0 full texts need network) | FAIL (drafted) | NO |
| RT-PPARG-DOWNSTREAM | PASS (distinct_from RT-RXR holds) | FAIL (study-design limit, BLK-NO-WET-LAB) | FAIL (drafted) | NO |
| RT-FAP-RLT | PASS (distinct_from RT-SSTR2 holds) | FAIL (protein/imaging gap, BLK-NO-WET-LAB) | FAIL (drafted) | NO |
| RT-VACCINE-COMBINATION | PASS (distinct_from RT-VACCINE holds) | PARTIAL (Stage 0 computational items unrun) | FAIL (drafted) | NO |
Zero routes pass all three. The recommended checkpoint below is therefore explicitly NOT a paper.

## 3. Inspection of the four `closure_kind: authorization` rows (correction 2)
Inspection only. No gate was tested, weakened or routed around.
| route | recorded reason | still current? | actual enforcer | missing condition |
|---|---|---|---|---|
| RT-ASO-ASK | "Not refuted — waiting on a person with a bench." `next.blocked_on: BLK-NO-WET-LAB` | Reason current; LABEL IMPRECISE | No repository enforcer. CLAUDE.md §5 "there is no wet lab" plus CLAUDE.md §3 (outreach requires user authorization) | (i) a collaborator with a bench; (ii) user authorization for the outreach act. Both, not either. |
| RT-ATR-PANEL | "Best taker in the portfolio and still not something this programme executes." `blocked_on: BLK-NO-WET-LAB` | same | same | same |
| RT-TRABECTEDIN-PPARG | "the ask is the block … now an ask made without the direction" (updated 2026-08-28 after the expression read failed to establish direction) | Reason current AND freshest of the four | same | same, and the ask would now go out without a direction |
| RT-SSTR2 | "Not refuted — a negative scan still kills it cheaply, and it stays on the ask list." `blocked_on: BLK-NO-WET-LAB` | same | same | same |
FINDING: in all four, the row's own `next.blocked_on` names BLK-NO-WET-LAB, not a permission gate.
So `closure_kind: authorization` is a partly stale classification: the standing boundary is TWO
conditions — an absent bench (a capability, not a permission) and an un-granted outreach
authorization (a real permission under CLAUDE.md §3, whose enforcer is the user, not a script).
`research/autonomy/publication-authority.json` was NOT opened or tested in this run, so whether any
current grant covers such an ask is UNKNOWN here, stated as unknown rather than assumed either way.
None of the four becomes executable from this inspection, and none is proposed for revival.

## 4. What is unchanged
The DECISION stands: no un-closed route qualifies as a distinct paper. The top-merit unmet question
is still RT-HOST-FACTOR, still disqualified by requirement 3, and the recommended next checkpoint is
still the bounded evidence repair of the superseded 39.4 % competing-share input, with the six
elements as written above.
