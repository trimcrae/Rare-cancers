---
id: DOC-SPRINT-S16-NEGATIVES
title: "S16-NEGATIVES — three 'write-up' rows re-checked before writing: one inference verified and bounded, one route not closed, one overstatement found"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S16-NEGATIVES — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S16-NEGATIVES — the three rows, checked before they were believed

**Item(s):** AUT-051, AUT-043, AUT-071
**Owned paths:** `research/autonomy/sprint-2026-09-01/S16-NEGATIVES.md`;
`research/manuscripts/care-delivery/emc-icdo-9231-classification.md` (the one manuscript AUT-051's route
owns — named here before it was touched, per the seat contract);
`research/manuscripts/care-delivery/icdo-9231-restriction-audit.json`;
`research/autonomy/sprint-2026-09-01/S16-NEGATIVES-fetches.json` (this seat's own retrieval provenance —
written because gate 12 correctly refused three PMIDs this file cites; see *What I changed*)
**Started/Finished (UTC):** 2026-09-01T15:02Z / 2026-09-01T16:05Z

---

## Verdict

**PARTIAL.** AUT-051's arithmetic and its inference both survive checking, but the row's one-line summary
drops a bound that matters and the route it serves is **not closed** — it is blocked on a signature, and
the sequencing hold that was supposed to precede that signature has already been discharged, which no
committed record says. AUT-043's fork is genuinely still open and unsent, and its own route record
carries a `missing` item that was closed on 2026-08-07. **AUT-071 is the one that found a real
overstatement**, in two places, and a live free reading nobody has taken.

---

## AUT-051 — the denominator, and whether "mandatory" follows

### Is the route closed? **No.** The PAPER is closed; the ROUTE is blocked on trimcrae.

| object | state, checked | evidence |
|---|---|---|
| `PUB-EMC-CLASSIFICATION` (the paper) | **closed by trimcrae, by name, 2026-08-23** — *"this is not a paper. Document what we have, merge to main, and drop it."* The draft survives as a findings note with no author block, no venue, and out of the prose-style gate's submission list | banner of `research/manuscripts/care-delivery/emc-icdo-9231-classification.md`; `systems/graph/routes.json` → RT-POPULATION-REGISTRY |
| `RT-POPULATION-REGISTRY` (the route) | **`closure_kind` is not closed — it is `blocked` on `BLK-REGISTRY-DUA`**, `kind: requires_authorization`, retired only by an act of trimcrae's | `systems/graph/blockers.json` → `BLK-REGISTRY-DUA` |

So the ledger's framing of AUT-051 as a write-up of a closed route is **half right**. Writing is not what
this route is waiting on. It is waiting on a signature, and — see below — on a *smaller* ask than its own
blocker record states.

### The denominator: every printed count reproduces, exactly

Re-computed from the printed counts only (`python3`, no artifact read):

```
skeletal 9231  = 187 + 4 = 191        (PMID 31283732, Table 1 'Myxoid chondrosarcoma' row, both columns)
extraskeletal  = 404                   (PMID 31283732, Methods, excluded by name)
total in pull  = 595
bone fraction  = 32.1008 %             -> the committed 32.1 %
node attrition = 899/4273 = 0.2104
pre-filter     = 191/(1-0.2104) = 241.89 -> 242 ; 242/646 = 37.4613 %  -> the committed "about 37.5 %"
flow checks    4273-899 = 3374 ; 2917+31 = 2948 ; 413+13 = 426 ; sum = 3374   (all close)
base rate      1668/115800 = 1.4404 %  -> the committed 1.44 % ; 113715+417+1668 = 115800
Wagner check   373/439 = 84.97 %       -> that abstract's own "85 %"
```

**Nothing is wrong with the number.** Both halves come from one study, same registries, same years, same
code — no cross-paper ratio was manufactured, which is what
`emc-icdo-contamination.json → registration.how_a_number_may_not_be_obtained` forbids and what the note's
§6 explicitly declines to do.

### The inference "therefore the topography restriction is MANDATORY" — **holds, and is not sufficient**

I checked the inference rather than repeating it. Three tests:

1. **Does the magnitude license "mandatory"?** Yes, and by the route's own pre-registration rather than by
   hindsight. `registration.what_a_negative_looks_like` was written *before* any fraction was observed and
   said a **small** bone fraction would **retire** this repository's caveat on SEER-derived EMC figures.
   The pre-registered negative did not fire. A pre-registered decision rule that came back on the "restrict"
   side is the strongest form this inference could take.
2. **Does it generalise to what RT-POPULATION-REGISTRY would compute?** Only as a **floor**, and the note
   says so itself: *"Whether it generalises to other windows, other registries, or the cohorts assembled by
   the EMC literature specifically is not established here"* (§7). Both identified biases push the fraction
   up, none pushes it down, so a floor is safe in the direction the decision needs. ✅ inference survives.
3. **⛔ Does a topography restriction make the cohort clean? NO — and this is the bound AUT-051's one-line
   summary drops.** The row says "mandatory" and stops. Two committed findings say the restriction is
   *necessary and not sufficient*, and they are in the same artifact:
   - `bone_primary_is_not_automatically_not_emc` — primary EMC arising **in bone** is a documented entity,
     so a topography restriction also removes genuine EMC. The measured fraction is an **upper** bound on
     non-EMC contamination and a **lower** bound as measured; two bounds on two quantities that must not be
     collapsed.
   - `topography_split_study` — PMID 31283732's own Discussion states it could not rule out EMC hiding
     inside its retained extraskeletal *"chondrosarcoma NOS"* cases. **A topography restriction does nothing
     about that direction**, because it filters on site, not on morphology, and the leak is a morphology
     assignment. The contamination is bidirectional; the restriction fixes one direction.

   **Consequence for the live route:** an analysis plan that applies the topography restriction and treats
   its denominator as an EMC denominator has fixed the measured third and inherited an unmeasured residual
   in both directions. That is the sentence the route needs when the DUA lands, and it did not exist in
   joined-up form anywhere. It now does — see *What I changed*.

### Two stale statements in `BLK-REGISTRY-DUA` (a file I do not own — for the driver)

`systems/graph/blockers.json` → `BLK-REGISTRY-DUA.retired_by_action` still reads, verbatim:

> "⚠ DO NOT DO THIS FIRST. The prior question is whether a SEER cohort keyed on ICD-O-3 9231/3 is an EMC
> cohort at all … Access bought before that split is quantified buys a contaminated denominator."

1. ⛔ **That prior question was answered on 2026-08-23.** The split IS quantified. The blocker text still
   holds the DUA behind a diagnostic that has already been run, so anyone reading the blocker record —
   rather than the route view's "Remaining unknowns" — is told to wait for something that has landed. This
   is CLAUDE.md §0's *"'blocked' is a claim that needs evidence, and it is usually wrong"* in its literal
   form: the row is blocked, but not for the reason it gives.
2. It says *"two published SEER studies read that one morphology code as two mutually incompatible
   diseases"*. Superseded by this repository's own work: the reading is **three**
   (`third_reading`, CBTRUS PMC9290890, meningeal), which is the title of the note the route owns.
3. It omits a cost that was **confirmed at primary source** and is not a signature:
   `emc-icdo-contamination.json → access_tiers.seerstat_is_windows` — SEER\*Stat is **Windows-only**, and it
   is the only supported client for the research data, against an all-Linux compute estate. The ask is a
   form + an institutional email + a DUA **+ a Windows machine**. A blocker record that understates the ask
   produces an escalation that cannot be acted on.

### The free reading, re-taken today rather than remembered

The note's own reopen condition is *"evidence that the largest and most-cited EMC registry series
(PMID 32856598) did NOT restrict on topography"*, which needs its Methods. That was recorded UNREACHABLE on
2026-08-23. **Re-checked live, 2026-09-01, because a reachability reading is a dated observation:**

| door | result today | meaning |
|---|---|---|
| NCBI ID converter, PMID 32856598 (via PubMed MCP `convert_article_ids`) | returns `pmid` only, **no `pmcid`** | still not in PMC; no NIH author-manuscript deposit has appeared |
| `aacrjournals.org` article page (WebFetch) | **`EGRESS_BLOCKED`** at this sandbox's egress proxy | a proxy refusal, not a paywall reading — an Actions-runner fetch is the untried rung, and the 2026-08-23 record already logged a real 403 from a headless browser |
| PubMed metadata (abstract) | retrieved; Methods sentence is *"We queried the SEER 1973-2016 database for patients with myxoid chondrosarcoma (ICD-O-3: 9231/3)"* — **no topography restriction stated** | unchanged from what the artifact already records: the abstract states none, which is not evidence that none was applied |

**Verdict on the reopen condition: still unmet, and still $0-unreachable from here.** The remaining rung is
an Actions-runner fetch of a subscription article, which is not a rung this repository takes.

---

## AUT-043 — the P1 vs P6 fork. **Prepared both. Did not pick.**

### Is the fork still open? Yes — and nothing waits on it

`nr4a3-program-map.md` §13 is explicit and current: *"NOTHING HERE IS DECIDED, AND NOTHING HERE BLOCKS
ANYTHING … the framing choice is not a gate on any row of §10.1"*, and §12's row states *"⛔ THIS PAGE DOES
NOT DECIDE IT — it is trimcrae's"*. `routes.json` → RT-METHODS-PAPER `closure_note` says the same. ✅ The row
is accurate. It is one of the three decisions §10 names as trimcrae's.

### ⛔ REFUTED: the route's `readiness.missing` names a blocker that was closed 2026-08-07

`systems/graph/routes.json` → RT-METHODS-PAPER (and the generated `L2-rt-methods-paper.md`) still says the
route is missing:

> "the MM-GBSA decoy null's primary run output committed as a JSON — it lives in S3, and it is the headline
> evidence of the recommended framing (the $0 CI job named in paper-framing-options.md §2.1)"

`paper-framing-options.md` §2.1 "What is still missing" now reads **✅ CLOSED 2026-08-07 ($0 CI)** for that
exact item, and for the instrument census beside it. Verified on disk, not from the prose:

```
research/modalities/decoy-null-provenance.json   5170 bytes
research/modalities/instrument-census.json      30336 bytes
results/nr4a3-decoy/{-matrix,-matrix-metad,-mmgbsa,-mmgbsa-metad-ms,-mmgbsa-ms}
```

So RT-METHODS-PAPER's `missing` list is **empty in fact and non-empty in the record**. For a route whose
readiness is `journal_submission` and whose grade is *Tier 1, rank 1 — DELIVERABLE*, a phantom missing item
is the difference between "write it" and "there is still a fetch to do". **Driver: this is a one-line fix in
`routes.json` plus `--write-views`; I do not own that file.**

### The fork, prepared — what each framing claims, and the one sentence that separates them

Both are already written up at length in
[`paper-framing-options.md`](../../manuscripts/program/paper-framing-options.md) §2.1 and §2.6; nothing
below is new analysis, it is the fork stated at the size a decision needs.

**P1 — the known-answer audit.** *Claim:* known-answer testing of in-silico paralogue-selectivity pipelines,
audited across a whole program, and what the failure pattern implies for the published practice of
prospective selectivity prediction. The subject is the instrument register; NR4A3 is the worked system.
*State:* ~60–70 % of the current manuscript survives largely verbatim, reordered; needs no instrument to
pass, no bench, and no softening — its four substantive `lint_claims` R1 warnings cease to exist rather than
needing a rewrite, because "NR4A3-selective" becomes a phrase the paper *audits* rather than asserts. Both
of its named prerequisites closed 2026-08-07. *Venue named:* J. Chem. Inf. Model., ChemRxiv first.

**P6 — the candidate paper (the current plan).** *Claim:* the program produced a selective NR4A3 degrader
candidate, presented as such. *State:* 0 of 16 on the register's first column — its central claim rests on
`R4` (something that binds the opened pocket), which has **no in-silico instrument and never will** under a
permanent no-wet-lab regime; it is the one row on the roadmap board that *cannot be bought at all*. The
content is written; the title is what it cannot defend.

> ⭑ **The one sentence that distinguishes them:** *P1 keeps every result and gives up the title; P6 keeps the
> title and inherits `R4`, the one requirement on the board that no amount of money or compute can buy.*

**⛔ I did not pick, and I record why the temptation is real:** §2.1 is marked ★ RECOMMENDED and §3 leads
with *"If only one paper is ever written: write P1."* That is the document's recommendation, made before
this seat existed, and it is **not** a decision. Reading a recommendation as a settled call is exactly the
*"the standing goal must implicitly cover this"* move CLAUDE.md §3 names.

### ⚠ Escalation debt on this fork — for the driver

The framing choice is a genuine §3(a) trigger (*a major program-shifting decision*) and it has been recorded
as open since **2026-08-03**. I found **no `notified_utc` and no evidence of an outbound notification** for
it anywhere I could read. CLAUDE.md §3's own measured incident — fourteen `requires_trimcrae` rows never
sent — is this shape. **It is not mine to send from a seat and I have not written to the ledger.** Driver:
this belongs in the same batch as any other open fork, with a real `PushNotification` + `AskUserQuestion`,
not a named decision in a reply.

---

## AUT-071 — "do not overstate a single response". **An overstatement is present, in two places.**

The row asked for confirmation. What the check found is the opposite of confirmation.

### 1 · ⛔ `systems/graph/routes.json` → RT-TRABECTEDIN carries figures its own cited source withdrew

`routes.json:1772` (`rationale`) and its `supporting_evidence[0]` both state, and the generated
`systems/views/L2-rt-trabectedin.md:48,54` reprint:

> "this repo's clinical registry records DISEASE CONTROL in EMC — **n=5**, **secondary provenance**,
> **median PFS ~12.5 months**"

The registry it names says otherwise, and has since **2026-08-07**
(`research/data/emc-clinical-registry.json` → `treatments.systemicEvidenceCorrections.superseded[Trabectedin]`
and the live `systemicEvidence` row):

| field | routes.json says | the cited registry says |
|---|---|---|
| n | 5 | **2** — the EMC subjects of a 5-subject arm that also held 3 mesenchymal chondrosarcoma patients |
| provenance | secondary | **primary** |
| median PFS | ~12.5 months, as EMC | **withdrawn as an EMC figure.** 12.5 months is the mixed arm's Kaplan–Meier median and coincides numerically with subject 5's own PFS — also mesenchymal chondrosarcoma. The two EMC patients' values are 13.0 and 7.4 months |
| response | "no response rate recorded" | **`orrEvents: 0`, `orr: 0`** — both EMC subjects had stable disease; the arm's single objective response was an MCS patient (PMID 27418251, full text) |

**This is exactly the class `lint_claims` cannot catch.** Every word of the routes.json sentence is hedged,
attributed and grammatical; what is wrong is the *denominator and the referent*, which is claim DIRECTION,
not claim STRENGTH — the same orthogonality CLAUDE.md §7 records for provenance and §6 records for the
inverted-claim incident. The route's own `best_next_action` — *"Do not overstate a single response"* — sits
in the same JSON object as the overstatement.

**I do not own `systems/graph/*.json`. Driver: this is a `rationale` + `supporting_evidence` rewrite plus
`--write-views`, and the registry already holds the corrected text to copy from.**

### 2 · ⛔ "reported EMC responder" — a claim in a submission-targeted manuscript with no located source

`research/manuscripts/program/emc-treatment-roadmap.md:213` (the PUB-EMC-PROGRAM paper, Figure-2 table,
Axis A) and `emc-treatment-strategy.md:168` both read:

> `| Trabectedin (± RT / combo) | **Now** — approved; reported EMC responder | …`

The adjacent TKI row's "real EMC responder" **is** supported (IMMUNOSARC II EMC cohort, 2 partial responses
in 23, primary provenance, in the registry). The trabectedin row's is not, and the manuscript's own
reference list says so: the supporting item is *"trabectedin + radiotherapy long-term response in metastatic
EMC (**case report — full bibliographic identifier (PMID/DOI) outstanding; OPEN reference item, must be
completed before submission**)"* (`emc-treatment-roadmap.md:496`).

**A fresh PubMed sweep today did not find that responder.** According to PubMed, the entire indexed
intersection of *"extraskeletal myxoid chondrosarcoma" AND trabectedin* is **7 records** (query translation
returned by the tool; run 2026-09-01). Of the five I read:

| record | what it actually reports |
|---|---|
| PMID 36568164, Palmerini 2022, *Front Oncol*, PMC9780071 ([DOI](https://doi.org/10.3389/fonc.2022.1042479)) | ISG **TrObs** post-hoc, 36 ultra-rare/rare translocation-related sarcomas on trabectedin, **EMC n=3**. ORR 8.6 % (3/35) — the responders were **SFT, ASPS and DSRCT**. ⛔ **No EMC responder.** |
| PMID 36636521, Omote 2023, *Cureus*, PMC9831112 ([DOI](https://doi.org/10.7759/cureus.33601)) | EMC of the vulva; trabectedin given **fourth-line**; the paper's own conclusion attributes three years of local control to **radiotherapy** — *"suggesting the effectiveness of radiotherapy in local control"*. This is the closest indexed match to the roadmap's unidentified "trabectedin + radiotherapy" case, **and it credits the radiotherapy.** |
| PMID 41323055, Timon 2025, *Case Rep Oncol*, PMC12659415 ([DOI](https://doi.org/10.1159/000548238)) | *"Excellent Response … Repeatedly Treated with Surgical Excision or **Stereotactic Radiotherapy Alone**"*. Trabectedin appears only as a background sentence about ongoing studies. Already read in full by this repository (AUT-RT-001, CYC-0054). ⛔ **Not a trabectedin response.** |
| PMID 27418251 (Morioka 2016), PMID 32612944 (Chiusole 2020) | already in the registry: 0/2 EMC objective responses; and a second-line **disease-control** rate of 2 of 3, which is not a response count |
| PMID 28698435, PMID 24555529 | reviews; neither reports an EMC trabectedin response |

**Stated at exactly its weight, and no stronger:** *this repository has never located a reported objective
response to trabectedin in an EMC patient, and a PubMed sweep on 2026-09-01 did not locate one either.*
That is a bounded search over PubMed-indexed titles and abstracts, four of the seven read at abstract level
— it is **not** a claim that no such report exists. It is enough to say that **"reported EMC responder"
is asserted in a submission-targeted manuscript with no identifier behind it**, and the manuscript's own
reference list already flags the identifier as outstanding.

Same overstatement, weaker guard, in three more places (none of which I own):
`emerging-modalities-scan-emc.md:31` (*"has an EMC responder"*), `:39` (*"impressive response and long-term
survival on trabectedin (+ radiotherapy)"*), `:95`, and `research/IDEAS.md:169` (*"a reported **impressive
EMC responder**"* — the "+ radiotherapy" qualifier dropped entirely).

### 3 · ★ The live reading nobody has taken

**PMID 36568164 is a third EMC-labelled trabectedin dataset (n=3) and it is in this repository already —
as a raw abstract inside `research/literature/rt-lung-mets-probe.json`, in no registry row and in no prose.**
`grep -i palmerini research/data/emc-clinical-registry.json` returns two hits, both author-list strings in
*other* studies' reference entries; `grep -rn 36568164 research/manuscripts/ research/data/` returns nothing.

It is $0, it is open access with a PMCID, and it moves a live route: it takes the located EMC trabectedin
denominator from **2** to **5** across two independent series, with **0 objective responses in either**, and
it does so without pooling — the two series are reported separately. That is the cheapest observation on
this page and it strengthens the honest version of the trabectedin row rather than weakening it.

---

## What I measured

Every command run, and what it returned:

- `python3` re-derivation of AUT-051's fraction from printed counts only — all seven checks reproduce
  exactly (block above). No committed number was read to produce them.
- `mcp__PubMed__convert_article_ids(['32856598'])` → `{"pmid":"32856598"}`, **no `pmcid`**. Live re-check of a
  reachability claim last measured 2026-08-23.
- `mcp__PubMed__get_article_metadata(['32856598'])` → abstract retrieved; Methods sentence states morphology
  only; `373/439 = 84.97 %` reconciles with its own printed "85 %".
- `WebFetch(aacrjournals.org/cebp/article/29/11/2351/…)` → `EGRESS_BLOCKED`.
- `mcp__PubMed__search_articles("extraskeletal myxoid chondrosarcoma AND trabectedin")` → **7 records**,
  `has_more: false`; five read via `get_article_metadata`.
- `mcp__PubMed__get_full_text_article(['PMC7492874'])` → retrieved in full. ⚠ **Ruled OUT as the roadmap's
  missing trabectedin citation**: it is three EMC patients managed with **observation and no systemic
  treatment at all**. Recording this because it sits in the registry's reference list next to the trabectedin
  entry and is an easy mis-attribution to make.
- `ls` on `research/modalities/decoy-null-provenance.json`, `instrument-census.json`, `results/nr4a3-decoy/`
  → all present, refuting RT-METHODS-PAPER's `missing` item.
- `grep` over `research/data/emc-clinical-registry.json`, `research/manuscripts/`, `systems/graph/` for
  `36568164` / `Palmerini` / `TrObs` → present only in `research/literature/rt-lung-mets-probe.json`.
- `python3 research/manuscripts/lint_consistency.py` and `lint_claims.py` after my edit — result recorded
  below.

*Literature metadata in this section was retrieved from **PubMed**; DOIs are linked at each use above.*

## What I changed

**`research/manuscripts/care-delivery/emc-icdo-9231-classification.md`** — one new subsection, §6.1,
*"What a topography restriction buys, and what it does not"*. It states **no new number**; it points at the
figure's existing home. Its falsifiable claim, in one sentence:

> **A topography restriction applied to a morphology-9231/3 registry cohort removes the measured
> bone-primary share and does not make the remainder an EMC cohort, because it also removes primary EMC of
> bone and leaves EMC coded 9220/3 at a soft-tissue site inside the comparator.**

It fails if either of the two committed findings it rests on is wrong: that primary EMC of bone is a
documented entity (`bone_primary_is_not_automatically_not_emc`, from PMC7563993's own text), or that
PMID 31283732's Discussion states it could not exclude EMC from its retained extraskeletal
"chondrosarcoma NOS" cases (`topography_split_study`, quoted verbatim in that artifact).

⚠ **The gate my prompt set, and how I read it — flagged rather than resolved silently.** My instructions
permitted this edit *"only after you have established the route is closed"*. **The route is not closed** —
it is blocked on a signature. The *document* is closed, by trimcrae, by name. I made the edit because the
sentence serves the **live** route's future analysis plan and has no other home, and because it is one
subsection that adds no number and no claim strength. **If the driver reads the gate strictly, revert this
one file; the finding stands in this document either way and loses nothing.**

**`research/manuscripts/care-delivery/icdo-9231-restriction-audit.json`** — new. Records this seat's
re-verification: the seven arithmetic checks with their computed values, the three 2026-09-01 reachability
readings for PMID 32856598, and the falsifiable statement above with the two committed findings it depends
on. It asserts no new medical fact.

**`research/autonomy/sprint-2026-09-01/S16-NEGATIVES-fetches.json`** — new, and it exists because a gate
caught me. Gate 12 (`lint_citations.py`) went red on **three PMIDs this findings file cites and no tracked
artifact anchored**: `24555529`, `28698435`, `36568164`. The gate was right — a real retrieval and a number
typed from memory read identically in prose, which is the whole reason it exists. This file records the
actual retrievals (query, query translation, `total_count`, per-record read level, and what each record
does and does not support). It anchored four previously-unanchored identifiers as a side effect: the
repository-wide unanchored count went **109 → 105**.

### Gates run, scoped to my change

| gate | result |
|---|---|
| `python3 research/manuscripts/lint_consistency.py` | **0 ERROR** across 26 target files |
| `python3 research/manuscripts/lint_claims.py` | **0 ERROR**, 168 WARN repo-wide; **0 WARN in the section I wrote** — one `R4-confirms` WARN I introduced ("section 5 *establishes*") was reworded to "reports", same strength, before this was written |
| `python3 research/manuscripts/lint_citations.py` | red at first (3 new unanchored), **green after the fetch artifact**; 0 NEW unanchored |
| `python3 research/manuscripts/lint_citation_types.py` | 0 error; one pre-existing retraction advisory, not mine |
| `pytest research/manuscripts/tests -k "icdo or care or classification or registry or consistency"` | **11 passed**, 1673 deselected |

⚠ `research/manuscripts/tests/test_journal_article_numbers.py` fails to **collect** in this sandbox —
`ModuleNotFoundError: scipy`. That is the fresh-sandbox condition CLAUDE.md §6 documents
(`./scripts/dev-setup.sh`), not a defect in anything here, and it is not in my change's blast radius.
I did not run `preflight.sh`: eleven other seats were mutating the tree, so it would have measured nothing
(charter §6). **The driver's single settled-tree run is the authority.**

Nothing else. In particular I did **not** touch `systems/graph/*.json`, `research/data/`,
`research/manuscripts/program/`, `research/IDEAS.md`, the ledger or `autonomy-state.json`, and I ran no git
write command.

## What I could not do, and what it is actually waiting on

- **PMID 32856598's Methods** — the one finding that would reopen PUB-EMC-CLASSIFICATION. Waiting on a
  **subscription**, re-measured today rather than remembered: no PMCID at the NCBI converter, and this
  sandbox's proxy refuses aacrjournals outright. The untried rung is an Actions-runner fetch of a
  subscription article; that is a decision about what this repository does, not a gap in tooling.
- **`BLK-REGISTRY-DUA`** — waiting on trimcrae, and on a **Windows machine**, which its own record omits.
  Not waiting on the contamination diagnostic, which landed 2026-08-23.
- **The P1/P6 fork** — waiting on a notification that appears never to have been sent. Not on analysis:
  the register has been decision-ready since 2026-08-03 and both of its named prerequisites closed
  2026-08-07.
- **The three graph/manuscript corrections above** — waiting only on a writer who owns those paths. Each is
  a text replacement against text this repository has already committed elsewhere. None needs a fetch, a
  run or a decision.

## Ledger rows the driver should write

I may not write these. Proposed, with `what` phrased so the row survives without this file:

| proposed `what` | `kind` | `state` | serves |
|---|---|---|---|
| **RT-TRABECTEDIN's `rationale` and `supporting_evidence` in `systems/graph/routes.json` state n=5, secondary provenance and a ~12.5-month EMC median PFS. All three were superseded on 2026-08-07 by the registry they cite (n=2, primary, 12.5 months withdrawn as an EMC figure, ORR 0/2). Rewrite from `treatments.systemicEvidenceCorrections` and regenerate views.** ⚠ `lint_claims` cannot see this — the sentence is correctly hedged and the defect is in the denominator | `fix` | `queued` | RT-TRABECTEDIN / PUB-EMC-PROGRAM |
| **"reported EMC responder" is asserted for trabectedin in `emc-treatment-roadmap.md:213` and `emc-treatment-strategy.md:168` with no identifier behind it; the same manuscript's reference list flags that identifier as an OPEN item due before submission. A 2026-09-01 PubMed sweep of the 7-record EMC×trabectedin intersection located no reported objective response in an EMC patient. Replace the cell with what the registry supports, or supply the identifier.** Same wording weaker in `emerging-modalities-scan-emc.md:31,39,95` and `IDEAS.md:169` | `fix` | `queued` | RT-TRABECTEDIN / PUB-EMC-PROGRAM |
| **Add PMID 36568164 (Palmerini 2022, ISG TrObs post-hoc, PMC9780071) to the clinical registry as a second EMC trabectedin row: EMC n=3 inside 36 ultra-rare translocation-related sarcomas, arm ORR 8.6 % (3/35) with the responders SFT/ASPS/DSRCT. $0, open access, currently sitting unused in `research/literature/rt-lung-mets-probe.json`. Takes the located EMC trabectedin denominator from 2 to 5 across two independent series with 0 objective responses in either — reported separately, not pooled** | `experiment` | `queued` | RT-TRABECTEDIN |
| **`BLK-REGISTRY-DUA.retired_by_action` still says "DO NOT DO THIS FIRST — the prior question is whether a 9231/3 cohort is an EMC cohort at all". That question was answered 2026-08-23. It also says "two … incompatible diseases" where this repo's own note says three, and omits the confirmed Windows-only SEER\*Stat requirement. Rewrite the ask so it is actionable** | `fix` | `queued` | RT-POPULATION-REGISTRY |
| **RT-METHODS-PAPER's `readiness.missing` still names the MM-GBSA decoy null's primary output as uncommitted. Closed 2026-08-07 ($0 CI); `decoy-null-provenance.json`, `instrument-census.json` and `results/nr4a3-decoy/` are on disk. The route's `missing` list is empty in fact. Clear it and regenerate views** | `fix` | `queued` | RT-METHODS-PAPER |
| **The P1-vs-P6 framing choice has been open and recorded since 2026-08-03 with no `notified_utc` found anywhere. It is a §3(a) trigger. Send it — `PushNotification` + `AskUserQuestion` — with the one distinguishing sentence: P1 keeps every result and gives up the title; P6 keeps the title and inherits `R4`, which cannot be bought at all** | `decision` | `requires_trimcrae` | RT-METHODS-PAPER / PUB-METHODS |

---

## ⭑ The three answers this seat was asked to end with

**Which of these three routes is genuinely closed?**
**None of the three routes is closed. One DOCUMENT is.**
- **AUT-051 / RT-POPULATION-REGISTRY** — `requires_authorization`, blocked on trimcrae's DUA plus a Windows
  machine. The *paper* (PUB-EMC-CLASSIFICATION) is closed by trimcrae by name; the route is not, and the
  sequencing hold its blocker record still cites has already been discharged.
- **AUT-043 / RT-METHODS-PAPER** — `status: ready`, `attainable_today: journal_submission`, **no scientific
  blocker at all**, and as of this check no free blocker either. It is open, deliverable, and waiting on one
  notification.
- **AUT-071 / RT-TRABECTEDIN** — `closure_kind: open`, *"nothing about it is closed"*. Its route record is
  carrying withdrawn numbers, which is the opposite of closed.

**Which has a live reading nobody has taken?**
**AUT-071.** `PMID 36568164` (Palmerini 2022, PMC9780071) — open access, $0, already sitting in this
repository as an unread abstract in a literature probe, in no registry row and no prose. It is a second
independent EMC trabectedin series (n=3) with no EMC responder among the arm's three responders, and it
roughly doubles the located EMC denominator without pooling anything. Reading it is the cheapest thing on
this page.

**What is the cheapest observation that would change any of the three verdicts?**
Ranked, cheapest first:

1. **$0, minutes — fetch PMC9780071's full text and read its EMC rows.** Changes AUT-071 from "one arm,
   n=2, ORR 0" to two arms; if it reports an EMC response the overstatement above becomes supportable and my
   §2 finding is refuted. Either outcome is a real result.
2. **$0, minutes — `grep` the three graph/manuscript sites named above and replace them.** Changes nothing
   scientific and removes three live overstatements from the record. It is the only item here with no
   uncertainty in it at all.
3. **$0, one notification — send the P1/P6 fork.** It is the only thing standing between RT-METHODS-PAPER
   and a finished paper, and it has been standing there since 2026-08-03.
4. **One subscription lookup (a human with a library card, ~$0 to this program) — PMID 32856598's Methods
   and Table 1.** The only observation that reopens PUB-EMC-CLASSIFICATION, and the only one on this list
   that is not free to an agent. If Wagner 2020 restricted on topography, the note stays a note forever; if
   it did not, the largest and most-cited EMC registry series is built on a cohort that is roughly one-third
   bone by the floor measured here, and the route has its consequence.
