---
id: DOC-SPRINT-S41-BLOCKED-ROUTE-AUDIT
title: "S41-BLOCKED-ROUTE-AUDIT — the population is 23 routes and 28 entries, not sixteen; seven routes were never adjudicated, and six of their entries carry a blocker that never claimed them"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Re-test BLK-NO-EMC-DATA route by route for AUT-PD-116, verify the count the row asserts, and close the
  gap left by S32-EMCDATA — which adjudicated sixteen of the twenty-three routes in the mechanical
  population and left seven UNKNOWN. Produces a proposed, unapplied patch to systems/graph/routes.json.
scope: >
  Every required_validation entry in systems/graph/routes.json with feasible_today=false and
  BLK-NO-EMC-DATA in blocked_by, at HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138. Adjudicates records,
  measures nothing new, and edits no graph file.
last_verified: 2026-09-02
---

# S41 — BLK-NO-EMC-DATA re-tested: how many "blocked" routes are actually takeable

**Item:** `AUT-PD-116` (`research/autonomy/research-ledger.json`, `state: queued`, `cost_class: free`,
score 135.9).
**Owned paths:** this file and
[`S41-proposed-routes-patch.json`](./S41-proposed-routes-patch.json). Nothing else was written.
**Baseline:** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`. `systems/graph/routes.json`
and `systems/graph/blockers.json` are byte-identical between the working tree and HEAD (`git diff --stat
HEAD --` returns empty for both), so no concurrent seat's uncommitted edit is under this audit.

## ⭐ HOW MANY MOVED, UP FRONT

**Twenty-three routes and twenty-eight `required_validation` entries** carry `feasible_today: false` on
`BLK-NO-EMC-DATA`. **Nineteen entries across sixteen routes were already adjudicated** by seat S32 on
2026-09-01 and are committed in `research/modalities/emc-blk-no-emc-data-route-retest.json`
(`git log --oneline -1 --` → `1132109a5`). **Nine entries across seven routes had never been adjudicated
by anybody**, and this memo adjudicates them.

Of those nine new entries: **zero are TAKEABLE TODAY**, **six carry the wrong blocker**, **three carry it
correctly**, and **zero are UNDECIDABLE**. ⛔ **No route in this memo is promoted, re-graded or made
ready.**

Across the whole 28-entry population, counted **per entry** (S32's own tally is per route, over sixteen):

| verdict | entries | which |
|---|---|---|
| requirement satisfied — TAKEABLE / UNBLOCKED | **3** | all S32, all already recorded |
| half-satisfied — PARTIAL, entry needs splitting | **5** | all S32 |
| open, and `BLK-NO-EMC-DATA` is the WRONG blocker | **17** | 11 S32 + **6 new here** |
| open, and `BLK-NO-EMC-DATA` is the RIGHT blocker | **3** | **all new here** |
| UNDECIDABLE FROM THE GRAPH | **0** | — |
| **total** | **28** | |

The per-entry table at the foot of this memo is the authority; the patch file's tally derives from it.

**UNMEASURED: 0.** Every one of the 28 entries has a verdict with a named artifact or a named blocker
record behind it.

---

## ⛔ FINDING 1 — THE BLOCKER'S OWN RECORD SAYS IT DOES NOT COVER AN EXPRESSION READ, AND ALSO NOT A CLINICAL ONE

`BLK-NO-EMC-DATA` in `systems/graph/blockers.json` is not a blocker about EMC data in general. Its
`name` scopes it precisely — *"EMC is nearly absent from public FUNCTIONAL-GENOMICS data (one DepMap
line, n = 1, no CRISPR data)"* — and its `retired_by_action` says the same thing twice more, unprompted,
about two separate datasets it was offered as retirements:

> "This blocker's statement is about FUNCTIONAL-GENOMICS data — one DepMap line, no CRISPR — and a
> tumour expression panel is not a dependency screen, so nothing here touches it."

> "A methylation reference set is not a dependency screen and carries no drug response, so it moves this
> blocker not at all."

★ **Read forward, that is the audit's result in one line: an entry asking for anything that is not a
dependency or drug-response screen cannot be blocked by this blocker.** S32 applied that reading to
entries naming an *expression or tissue read*. ⛔ **The same reading applies with equal force to entries
naming a CLINICAL series, an OUTCOME series or a REGISTRY analysis, and nobody had applied it there** —
which is exactly the population S32's text filter could not see, and which is Finding 2.

⚠ This finding costs $0 and needs no data artifact: the blocker record is itself the evidence.

---

## ⛔⛔ FINDING 2 — THE NUMBER IS NOT SIXTEEN, AND THE SEVEN ROUTES THE SIXTEEN LEFT OUT WERE NEVER TESTED

`AUT-PD-116`'s headline reads *"SIXTEEN ROUTES CARRY A required_validation MARKED feasible_today=false ON
BLK-NO-EMC-DATA…"*. The mechanical population is larger. Derivation, run at the baseline HEAD:

```
python3 - <<'EOF'
import json
r=json.load(open('systems/graph/routes.json'))
hits=[(x['id'],v) for x in r for v in (x.get('required_validation') or [])
      if v.get('feasible_today') is False and 'BLK-NO-EMC-DATA' in (v.get('blocked_by') or [])]
print('routes_total',len(r),'entries',len(hits),'distinct_routes',len({h[0] for h in hits}))
print('reference_anywhere',len([x for x in r if 'BLK-NO-EMC-DATA' in json.dumps(x)]))
print('blockers_inherited',len([x for x in r if 'BLK-NO-EMC-DATA' in (x.get('blockers_inherited') or [])]))
print('blockers_retired',len([x for x in r if 'BLK-NO-EMC-DATA' in (x.get('blockers_retired') or [])]))
EOF
```

```
routes_total 77 entries 28 distinct_routes 23
reference_anywhere 44
blockers_inherited 38
blockers_retired 0
```

★ **The row's "sixteen" is not wrong — it is a SUBSET, and the row never says so.** The sixteen is
`23 minus the 7 whose entry text does not name an expression or tissue read`; S32 reconstructed it by
adding that text filter to the row's own stated reproduce recipe and recorded the reconstruction in its
own `_limits` (*"THE POPULATION IS RECONSTRUCTED, NOT INHERITED"*). Set-differencing the retest's
`routes` keys against the mechanical population returns the seven exactly and returns nothing in the
other direction:

```
NOT_adjudicated ['RT-6MP', 'RT-ATR-PANEL', 'RT-CARFILZOMIB', 'RT-ENDPOINT-CHOICE',
                 'RT-ICI-TKI', 'RT-PARTNER-STRAT', 'RT-SYNLETH-DEP']
adjudicated_not_in_pop []
```

⚠ **The stale part is the row's summary line, and the direction of the staleness is the usual one.** A
reader who takes "sixteen" as the population stops seven routes short. S32's own tally already flagged a
residue — *"44 of the 77 routes reference this blocker somewhere; 16 are adjudicated here and the other
28 were NOT tested by this seat — their attribution is UNKNOWN, not endorsed"* — but that sentence
counts routes *mentioning the string anywhere* (44), which mixes `blockers_inherited` (38 routes) with
the `required_validation` population (23). **The seven that matter — routes holding an unadjudicated,
explicitly-blocked validation requirement — were never separated out of that 28 and so read as
low-priority background.** They are the whole of the un-audited population, and they are enumerated
above.

---

## ⛔ FINDING 3 — SIX OF THE NINE NEW ENTRIES ARE CLINICAL REQUIREMENTS ON A FUNCTIONAL-GENOMICS BLOCKER

The nine entries, verbatim from `systems/graph/routes.json` at HEAD, with verdicts.

### GENUINELY BLOCKED — blocker CORRECT (3 entries, 3 routes)

| route | `required_validation` text (verbatim) | evidence for the verdict |
|---|---|---|
| `RT-SYNLETH-DEP` | *"An EMC-specific dependency screen"* | This is verbatim what `BLK-NO-EMC-DATA.retired_by_action` names as its retiring action (*"an EMC dependency or drug-response screen"*). S32's `verdict_scale` already names this route as the one that carries the blocker correctly. **No change.** |
| `RT-ATR-PANEL` | *"The panel itself"* — route `display_name` *"The ATR-inhibitor cell panel in EMC lines (the ask)"* | An ex-vivo drug-response panel in EMC lines is the second half of the same retiring action. Also correctly carries `BLK-NO-WET-LAB`. **No change.** |
| `RT-6MP` | *"A primary measurement of 6-MP's direction of effect on the EWSR1::NR4A3 fusion, not on wild-type NR4A3"* | A primary perturbation measurement. Defensible under "no drug-response screen", but the *precise* residual is a bench: the route's `readiness.attainable_today` is `internal_note` and `next.best_next_action` is *"Nothing. Cite the closure"*. **Recommend ADDING `BLK-NO-WET-LAB`; do not remove `BLK-NO-EMC-DATA`.** ⚠ Bookkeeping only — the route is closed on direction of effect and no ranking consequence follows. |

### STILL BLOCKED — WRONG BLOCKER (6 entries, 4 routes). None becomes takeable; each becomes honestly labelled.

| route | entry (verbatim, truncated where marked) | why `BLK-NO-EMC-DATA` is wrong | proposed residual |
|---|---|---|---|
| `RT-ICI-TKI` `[0]` | *"A larger EMC series or a registry analysis"* | Clinical outcome evidence, not functional genomics. The route's own `readiness.missing` already states the residual correctly — *"a larger clinical series — unchanged. Four patient-level PFS values now exist (`km-swimmer-readings.json`) and four patients is not a series"* — and never mentions dependency data. | `BLK-NO-CURATED-CLINICAL-DATA` + `BLK-REGISTRY-DUA` |
| `RT-CARFILZOMIB` `[0]` | *"A clinical series"* | Same category error. `BLK-NO-CURATED-CLINICAL-DATA` is explicitly *"a statement about the REACHABLE SET"* of clinical publications, which is the thing this entry is short of. | `BLK-NO-CURATED-CLINICAL-DATA` |
| `RT-ENDPOINT-CHOICE` `[2]` | *"A comparator that would separate treatment effect from natural history … a randomised no-treatment arm, or an observational within-patient design such as growth-modulation index or time to next treatment"* | A trial-design and clinical-content gap. **Checked, not assumed:** `research/modalities/emc-ipd-survival.json` reconstructs single-interval survival endpoints from published Kaplan–Meier curves (`curve_schema.endpoint` = `os \| dss \| pfs \| lrfs \| dmfs`) and holds `printed_patient_level_data.n_rows: 2`. Neither growth-modulation index nor time-to-next-treatment is derivable from that — both need *paired sequential* intervals per patient, which no reachable artifact carries. **Not takeable.** ⚠ This route's `blockers_inherited` is `[]` while this entry carries a blocker — an internal inconsistency the patch removes for free. | `BLK-NO-CURATED-CLINICAL-DATA` |
| `RT-PARTNER-STRAT` `[0]` | *"Partner-stratified event counts from the largest outcome series. ✅ HALF DONE 2026-08-08: Huang 2023 … obtained … Paioli 2021 … remains genuinely closed: oa_status closed, zero OA locations …"* | The entry's own text names its residual: one closed-access publication. That is a reachability gap in the clinical literature, and no dependency screen would supply it. | `BLK-NO-CURATED-CLINICAL-DATA` |
| `RT-PARTNER-STRAT` `[1]` | *"The pazopanib trial's full fusion-partner distribution and its prior-therapy table …"* | A publication-content gap in a clinical trial report. | `BLK-NO-CURATED-CLINICAL-DATA` |
| `RT-PARTNER-STRAT` `[2]` | *"A partner-stratified reanalysis of any registry with size and stage adjusted for …"* | `BLK-REGISTRY-DUA` names this exactly — *"Population cancer-registry microdata (SEER, NCDB) needs a signed data-use agreement"*, `kind: requires_authorization`. | `BLK-REGISTRY-DUA` + `BLK-NO-CURATED-CLINICAL-DATA` |

★ **WHY THIS RE-ATTRIBUTION IS NOT COSMETIC.** `BLK-NO-EMC-DATA` is `kind: insufficient_data` and its
retiring action is *"an EMC dependency or drug-response screen … none of which exists"* — i.e. it reads
as waiting on the world. `BLK-REGISTRY-DUA` is `kind: requires_authorization` and its retiring action is
*"An action only trimcrae can take: register for SEER research data and sign the agreement."* **Filing an
authorization gap under a data-nonexistence blocker turns a question with an owner into a route that
looks permanently dead.** That is CLAUDE.md §0's failure mode with the polarity S32 warned about, arriving
through the clinical door rather than the expression one.

⚠ **AND `BLK-REGISTRY-DUA` CARRIES ITS OWN PRIOR, WHICH THIS MEMO DOES NOT OVERRIDE:** *"⚠ DO NOT DO THIS
FIRST. The prior question is whether a SEER cohort keyed on ICD-O-3 9231/3 is an EMC cohort at all …
Access bought before that split is quantified buys a contaminated denominator."* Re-attributing the
blocker does not recommend buying the access.

---

## ⭐ FINDING 4 — ONE ROUTE RECORDS A $0 ACTION AS BLOCKED ON THIS BLOCKER, IN THE SAME FIELD THAT PRICES IT AT $0

`RT-CARFILZOMIB`'s `next` block, verbatim at HEAD, holds all three of these at once:

- `next.cost`: `"$0"`
- `next.best_next_action`: *"Re-run the CLASS-LEVEL query, not the EMC one … the query that found them —
  a proteasome inhibitor against the parent histology — is recorded verbatim in
  `research/literature/carfilzomib-class-clinical-2026-08-28.json` and costs $0 to repeat. Two named $0
  items remain open …"*
- `next.blocked_on`: `["BLK-NO-EMC-DATA"]`

⛔ **The action the field prescribes is a literature query. `BLK-NO-EMC-DATA` does not gate a literature
query, and the field says so itself by pricing it at $0 and calling it repeatable.** The referenced file
exists at HEAD (`research/literature/carfilzomib-class-clinical-2026-08-28.json`, 15 961 bytes). This is
the single cheapest correction in the audit and the only one that unsticks a live action rather than a
label: **$0, no fetch, no CI, no GPU.**

⚠ **What it does NOT do.** It does not satisfy `required_validation[0]` (*"A clinical series"*), which
stays open on `BLK-NO-CURATED-CLINICAL-DATA`; it does not touch the route's grade, whose own text
already records the negative class-level clinical read (`EV-MAKI-2005`) beside the ex-vivo positive; and
it makes no claim about carfilzomib's activity, selectivity or safety in EMC.

---

## What I verified of S32's nineteen entries rather than inheriting

S32's adjudication is committed and I did not re-derive it. I spot-checked the four load-bearing claims
it rests on, at HEAD:

- **The row's citation claim.** Grepping every route record for the artifact id: three routes cite
  `ART-EMC-EXPRESSION-PANELS` (`RT-TRABECTEDIN-PPARG`, `RT-PPARG-DOWNSTREAM`, `RT-PRAME-IMMTAC`) and two
  cite the file path only (`RT-ALK-HIT`, `RT-VACCINE-COMBINATION`). **None of the three id-citers is in
  the sixteen** — they are the routes AUT-052 and AUT-053 already adjudicated. So `AUT-PD-116`'s
  *"not one of them cites ART-EMC-EXPRESSION-PANELS"* holds literally, and S32's refinement (the reading
  was consumed through a second id, `ART-CENSUS-ROUTE-GRADING`) is the substantive correction. **CONFIRMED.**
- **`read_5_HYPOXIA` `readability_verdict.state` = `TAKEN`**, on both platforms — the reading behind S32's
  `RT-HYPOXIA-PRODRUG` verdict. **CONFIRMED** in `research/modalities/emc-expression-panels.json`.
- **`read_2_CS_GAG_PAPS` = `PARTIALLY TAKEN`**, both platforms — behind `RT-MATRIX-SYNTHESIS`. S32 claimed
  the read exists and was graded, not that it was fully taken. **CONFIRMED, and the weaker state is the
  one in the record.**
- **The platform and probe facts underneath every UNBLOCKED verdict.** `platforms` names exactly two read
  series: `GSE24369` on `GPL6244` (42 samples, 28 459 probes, 20 235 symbol-mapped, 6 EMC vs 29
  comparator) and `GSE4303-GPL3290` on `GPL3290` (16 samples, 43 008 probes, 27 197 mapped). `gene_reads`
  holds 479 symbols. Every gene `AUT-PD-116` names as answered has a `readable: true` entry with a probe
  id on `GPL6244` — `SSTR2` (probe 8009526), `CD276` (7984743), `FAP` (8056257), `MTAP` (8154635),
  `PPARG` (8077899), `HLA-A` (8117800), `TAF15` (8006573), `NR4A3` (8156848), `PRAME` (8074856).
  **CONFIRMED — but see the next line, which is why "has a probe" is not "answers the requirement".**

⛔ **AND S32'S DANGEROUS-DIRECTION CORRECTION IS THE ONE TO CARRY FORWARD, VERIFIED HERE:** the artifact's
own `_what_this_cannot_conclude` refuses three of the six routes `AUT-PD-116` lists as answered — *"That
a gene with no probe is unexpressed. It was not read."*, *"That a transcript reading is a protein
reading. Every therapeutic address named here — CSPG4, DLL3, CD248, CD276, SSTR2 … is a protein or a
glycan question."*, and *"⛔ That any antigen in read 7 is on the cell SURFACE, at a usable density, on
the TUMOUR cell rather than the stroma, or RESTRICTED relative to normal tissue."* **A probe on
`GPL6244` is a transcript readout and nothing more.** `RT-JUNCTION-NEOANTIGEN` asks for *presentation*,
`RT-MTAP-PRMT5` for a *copy number*, `RT-FUSION-OUTPUT` for *fusion-type-stratified* data — none of which
a probe id supplies at any n.

---

## Per-entry census — all 28

`(S32)` = adjudicated in `research/modalities/emc-blk-no-emc-data-route-retest.json`, verdict reproduced
here unchanged. `(S41)` = adjudicated in this memo.

| # | route | entry | verdict | decided by |
|---|---|---|---|---|
| 1 | `RT-TCRT-CTA` | *"A real EMC expression series"* | **TAKEABLE / UNBLOCKED** (S32) | two read series exist with a passing control; residual is CTA probe coverage, an instrument state |
| 2 | `RT-MATRIX-SYNTHESIS` | *"A measurement of the matrix compartment in EMC tissue"* | **TAKEABLE / UNBLOCKED** (S32) | `reads.read_2_CS_GAG_PAPS`; grade already moved 2026-08-09 |
| 3 | `RT-HYPOXIA-PRODRUG` | *"A measurement of the matrix compartment in EMC tissue"* | **TAKEABLE / UNBLOCKED, entry is a copy-paste of the wrong requirement** (S32) | `reads.read_5_HYPOXIA` state `TAKEN`; route premise is hypoxia, not matrix |
| 4 | `RT-SSTR2` | *"A receptor imaging scan in an EMC patient, or an expression readout on EMC tissue"* | **PARTIAL — split the disjuncts** (S32) | second disjunct read; imaging half stays on `BLK-NO-WET-LAB` |
| 5 | `RT-B7H3` | *"Selectivity measured on real EMC tissue rather than surrogates"* | **PARTIAL** (S32) | transcript read taken; "selectivity" is a protein/normal-tissue axis |
| 6 | `RT-CART-SURFACE` | *"A selective surface antigen confirmed on EMC tissue"* | **PARTIAL** (S32) | `read_8_SURFACE_ANTIGEN` ran; "surface" and "selective" are not transcript claims |
| 7 | `RT-FAP-RLT` | *"An expression or imaging readout on EMC tissue"* | **PARTIAL** (S32) | `FAP` readable on `GPL6244`; imaging half open |
| 8 | `RT-FAP-RLT` | *"Bystander/crossfire dose … tumour-to-normal uptake ratio"* | **STILL BLOCKED, wrong blocker** (S32) | a dosimetry quantity; no expression read reaches it |
| 9 | `RT-IMMUNOCYTOKINE` | *"A measurement of the matrix compartment in EMC tissue"* | **PARTIAL** (S32) | same read as #2; oncofetal spliced-domain half open |
| 10 | `RT-TRABECTEDIN` | *"A larger EMC series, or a measured effect on the fusion's transcriptional output"* | **STILL BLOCKED, wrong blocker** (S32) | |
| 11 | `RT-JUNCTION-NEOANTIGEN` | *"Measured presentation on EMC tissue"* | **STILL BLOCKED, wrong blocker** (S32) | presentation ≠ transcript; artifact refuses it in its own words |
| 12 | `RT-SYNPROMOTER` | *"A direct read of the fusion's DNA-binding specificity in EMC"* | **STILL BLOCKED, wrong blocker** (S32) | |
| 13 | `RT-FUSION-OUTPUT` | *"Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq"* | **STILL BLOCKED, wrong blocker** (S32) | a perturbation experiment |
| 14 | `RT-FUSION-OUTPUT` | *"Fusion-type-stratified EMC expression data"* | **STILL BLOCKED, wrong blocker** (S32) | neither series carries a partner label |
| 15 | `RT-TXN-CDK` | *"A measurement in a fusion-positive EMC model"* | **STILL BLOCKED, wrong blocker** (S32) | |
| 16 | `RT-MTAP-PRMT5` | *"A gene-level copy-number read of the locus in any EMC cohort"* | **STILL BLOCKED, wrong blocker** (S32) | an expression panel answers no copy number |
| 17 | `RT-MATRIX-ADDRESS` | *"A stain or binding assay for the oncofetal chondroitin-sulfate pattern on EMC tissue"* | **STILL BLOCKED, wrong blocker** (S32) | a glycan epitope assay |
| 18 | `RT-VACCINE-COMBINATION` | *"Immunopeptidomics on EMC tissue or a patient-derived line"* | **STILL BLOCKED, wrong blocker** (S32) | |
| 19 | `RT-VACCINE-COMBINATION` | *"T-cell reactivity against identified peptide-HLA complexes"* | **STILL BLOCKED, wrong blocker** (S32) | |
| 20 | `RT-SYNLETH-DEP` | *"An EMC-specific dependency screen"* | **GENUINELY BLOCKED, blocker correct** (S41) | verbatim the blocker's retiring action |
| 21 | `RT-ATR-PANEL` | *"The panel itself"* | **GENUINELY BLOCKED, blocker correct** (S41) | an ex-vivo drug-response panel |
| 22 | `RT-6MP` | *"A primary measurement of 6-MP's direction of effect on the EWSR1::NR4A3 fusion …"* | **GENUINELY BLOCKED, blocker defensible; add `BLK-NO-WET-LAB`** (S41) | a primary perturbation measurement |
| 23 | `RT-ICI-TKI` | *"A larger EMC series or a registry analysis"* | **STILL BLOCKED, wrong blocker** (S41) | clinical, not functional-genomics; route's own `readiness.missing` agrees |
| 24 | `RT-CARFILZOMIB` | *"A clinical series"* | **STILL BLOCKED, wrong blocker** (S41) | clinical reachable-set gap |
| 25 | `RT-ENDPOINT-CHOICE` | *"A comparator that would separate treatment effect from natural history …"* | **STILL BLOCKED, wrong blocker** (S41) | `emc-ipd-survival.json` carries single-interval endpoints and 2 printed patient rows; GMI/TTNT need paired sequential intervals |
| 26 | `RT-PARTNER-STRAT` | *"Partner-stratified event counts from the largest outcome series …"* | **STILL BLOCKED, wrong blocker** (S41) | residual is one closed-access publication |
| 27 | `RT-PARTNER-STRAT` | *"The pazopanib trial's full fusion-partner distribution and its prior-therapy table …"* | **STILL BLOCKED, wrong blocker** (S41) | publication-content gap |
| 28 | `RT-PARTNER-STRAT` | *"A partner-stratified reanalysis of any registry with size and stage adjusted for …"* | **STILL BLOCKED, wrong blocker** (S41) | `BLK-REGISTRY-DUA` names it exactly |

**TAKEABLE TODAY: 3 of 28 (all S32, all already recorded).** **Newly TAKEABLE from this memo: 0.**
**UNDECIDABLE FROM THE GRAPH: 0.**

---

## What I changed

- `research/autonomy/sprint-2026-09-01/S41-BLOCKED-ROUTE-AUDIT.md` — this file.
- `research/autonomy/sprint-2026-09-01/S41-proposed-routes-patch.json` — a **proposed, unapplied** patch
  covering the nine entries in Findings 3 and 4, with a per-route justification. ⛔ It is written as
  instructions. `systems/graph/routes.json` was NOT edited: flipping or re-attributing a blocker is what
  makes the ranker start offering a route, and that call belongs to a cycle that can gate it.

## What I did not touch

- `systems/graph/*.json` — read-only for this seat. `systems/views/` — generated; not opened for writing.
- `research/autonomy/research-ledger.json` — sprint-wide no-touch.
- `research/modalities/emc-blk-no-emc-data-route-retest.json` — S32's, committed, verified not amended.
- No git write command was run. `git log`, `git show`, `git diff --stat`, `git rev-parse` only.

## Ledger rows the driver should write

| what | kind | state | serves |
|---|---|---|---|
| **`AUT-PD-116`'s headline says "sixteen" and the mechanical population is 23 routes / 28 entries.** Seven routes were never adjudicated; this memo adjudicates them. Amend the row's summary line to name the population and the subset, and mark the sixteen closed by `emc-blk-no-emc-data-route-retest.json`. | `process_defect` | `queued` | — |
| **Apply `S41-proposed-routes-patch.json`** — six entries re-attributed to `BLK-NO-CURATED-CLINICAL-DATA` / `BLK-REGISTRY-DUA`, one gains `BLK-NO-WET-LAB`, one `next.blocked_on` cleared. $0, no grade change, requires a `systems/views` regeneration. | `process_defect` | `queued` | `RT-PARTNER-STRAT` |
| **`RT-CARFILZOMIB.next.blocked_on` is `["BLK-NO-EMC-DATA"]` while the same field prices its own next action at `$0` and calls it repeatable.** Clear the field and take the class-level query recorded in `research/literature/carfilzomib-class-clinical-2026-08-28.json`. | `fetch` | `queued` | `RT-CARFILZOMIB` |
| **`RT-ENDPOINT-CHOICE.blockers_inherited` is `[]` while `required_validation[2]` carries `BLK-NO-EMC-DATA`.** A route-level/entry-level inconsistency the graph build does not catch. Worth a guard, not only a fix. | `process_defect` | `queued` | `RT-ENDPOINT-CHOICE` |

## Gates

None run — this seat wrote two new files under `research/autonomy/sprint-2026-09-01/` and touched no
manuscript, no SI, no citation, no `systems/` path and no generated artifact. `./scripts/preflight.sh`
is the driver's to run before the commit that lands them.
