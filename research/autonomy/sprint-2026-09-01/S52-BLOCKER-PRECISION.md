---
id: DOC-SPRINT-S52-BLOCKER-PRECISION
title: "S52-BLOCKER-PRECISION — the premise held, the clause was false rather than imprecise, and the blast radius is a reader's, not the build's: nothing computes on retired_by_action"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Verify AUT-PD-113's premise against the primary source, derive the inheritance count, replace
  BLK-NO-EMC-DATA's retirement clause with one naming what is actually absent, and test whether any
  of the 38 inheriting routes has a grade resting on the looser reading. Extends S41, which fixed the
  ATTRIBUTIONS this memo fixes the DEFINITION of.
scope: >
  systems/graph/blockers.json (BLK-NO-EMC-DATA.retired_by_action) and the read-only evidence needed to
  justify the wording. Baseline HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138. Measures nothing new;
  every reading below is a $0 read of a committed file or a cached primary text.
last_verified: 2026-09-02
---

# S52 — what is actually absent, and why it is not "an ex-vivo panel"

**Item:** `AUT-PD-113` (`research/autonomy/research-ledger.json`, `kind: process_defect`,
`cost_class: free`, score 132.9).
**Owned paths:** `systems/graph/blockers.json`, the generated `systems/views/registers/blockers.md`
(written by `systems_check.py --write-views`, not by hand), and this file. Nothing else was written.
**Baseline:** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`;
`git diff --stat HEAD -- systems/graph/blockers.json systems/graph/routes.json` was empty before the
edit, so no concurrent seat's uncommitted work is underneath it.

---

## ⭐ THE ANSWER UP FRONT

**⛔ NO ROUTE BECOMES TAKEABLE UNDER THE PRECISE WORDING, AND THAT RESULT IS STRUCTURAL RATHER THAN
LUCKY.** The precise clause is strictly NARROWER than the one it replaces, so it can only make the
blocker harder to retire; a narrowing edit has no mechanism by which to promote a route. The rewording
was applied. `systems/systems_check.py --check` returns
**`systems_check: 604 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO`**, exit 0.

**★ WHAT IS TAKEABLE — AND IT IS TAKEABLE AT HEAD, INDEPENDENT OF THIS EDIT — IS A $0 LITERATURE READ ON
THREE ROUTES THAT DO NOT KNOW THEIR OWN COMPOUND WAS SCREENED IN EMC.** `EV-BANGERTER-2023` names five
of its forty compounds in the accessible record. Two of the five are the selecting agents of routes that
inherit this blocker and cite the paper nowhere: **`RT-CHAPERONE`** (PU-H71, HSP90) and **`RT-MDM2`**
(HDM201, MDM2/MDM4). A third, **`RT-APOPTOSIS-DEP`** (venetoclax), uses the result in its grade prose
while naming no source for it. §4 is the per-route detail; §4.2 is the one a reader should not skip.

⚠ **This memo re-grades nothing and edits no route.** `systems/graph/routes.json` was not opened for
writing (S41's patch is pending on it). The three findings are filed as ledger rows in §7.

---

## 1 · THE PREMISE HELD, AND THE ROW UNDERSTATES IT

`AUT-PD-113` calls the clause *"imprecise rather than false"*. **On the third disjunct it is false as
written.** Both fields verbatim from `systems/graph/blockers.json` at the baseline HEAD.

`BLK-NO-EMC-DATA.name`:

> "EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)"

`BLK-NO-EMC-DATA.retired_by_action`, the operative sentence (the field is long; this is the clause under
audit, and it was the field's ONLY statement of a retirement condition):

> "What WOULD retire it is an EMC dependency or drug-response screen (a second EMC line in DepMap, a
> CRISPR screen, or an ex-vivo panel), none of which exists; TRG-SARCOMA-ATRI-RESPONSE-PANEL watches for
> it."

The field carries no `readiness` and no `retired_by` key; the schema's other retirement key,
`retired_by_technology`, is absent, which is why the B2 invariant is satisfied by this field alone
(`systems_check.py:634` — *"is not permanent and names neither a technology nor an action that would
retire it"*).

**`EV-BANGERTER-2023`, read from `systems/graph/evidence.json`** (not assumed — the id resolves in the
evidence collection, and its `cited_in` names `research/IDEAS.md` and
`research/manuscripts/repurposing/repurposing-hypotheses.md`):

> `citation`: "Bangerter et al. 2023, Hum Cell — ex-vivo drug sensitivity in patient-derived EMC models
> USZ20-EMC1 and USZ22-EMC2."
> `canonical`: pmid **36316541**, doi **10.1007/s13577-022-00818-x**, pmcid **PMC9813045**.

**What it actually is**, read from the cached primary text
(`git show origin/literature-cache:literature/bangerter-2023-emc-exvivo/PMC9813045.txt`, 29 246 bytes —
the cache lives on the `literature-cache` branch, not on `main`, which is why a repo-wide `find` for it
returns nothing):

| question | answer, verbatim where quoted |
|---|---|
| ex-vivo? | Yes. Two patient-derived models grown as "sarco-spheres"; "To the best of our knowledge, we here present the first molecularly characterized and functionally tested ex vivo EMC models (USZ20-EMC1 and USZ22-EMC2)." |
| tissue | Human EMC. USZ20-EMC1 from an amputation specimen of recurrent tumour (54-year-old); USZ22-EMC2 from a diagnostic biopsy (68-year-old). Both fusion-confirmed: EWSR1-NR4A3 and TAF15-NR4A3 respectively, on RNA by FoundationOne®HEME, with NR4A3 break-apart FISH and a DKFZ sarcoma-classifier methylation score of **0.99** for both. |
| drug-response? | Yes. "A medium throughput drug screen using 40 drugs was conducted with USZ20-EMC1 at passage 5" — 23 targeted agents + 17 chemotherapies, acoustic dispensing, 3-log 6-dose curves from 33 pmol/l to 200 μmol/l, 6-day CellTiter-Glo readout, **AUC** endpoint. |
| how many samples | **Screen: n = 1 model.** Validation: carfilzomib, doxorubicin and venetoclax in 96-well triplicate 6-point dose-response in **both** models (passages 8–10), plus 5-point combination matrices scored with SynergyFinder (ZIP/Loewe/Bliss/HSA). |
| published where | *Human Cell* (Hum Cell) 2023;36(1):446–455. CC BY, open access, in PMC. |

⛔ **So the premise holds and the row's hedge is too kind.** "An ex-vivo panel … none of which exists" is
not a loose reading of a true statement; it asserts the non-existence of a thing this repository has
committed, cited twice in prose, resolved a PMID/DOI/PMCID for, cached the full text of, and re-read at
least four times in review seats. **The disjunct is false, and it has been false since the paper
published.**

---

## 2 · THE COUNT — 38 OF 77, CONFIRMED EXACTLY

Run at the baseline HEAD, before the edit:

```
python3 - <<'EOF'
import json
r=json.load(open('systems/graph/routes.json'))
print('routes_total',len(r))
print('blockers_inherited',len([x for x in r if 'BLK-NO-EMC-DATA' in (x.get('blockers_inherited') or [])]))
print('reference_anywhere',len([x for x in r if 'BLK-NO-EMC-DATA' in json.dumps(x)]))
print('blockers_retired',len([x for x in r if 'BLK-NO-EMC-DATA' in (x.get('blockers_retired') or [])]))
hits=[(x['id'],i) for x in r for i,v in enumerate(x.get('required_validation') or [])
      if v.get('feasible_today') is False and 'BLK-NO-EMC-DATA' in (v.get('blocked_by') or [])]
print('rv_entries',len(hits),'distinct',len({h[0] for h in hits}))
EOF
```

```
routes_total 77
blockers_inherited 38
reference_anywhere 44
blockers_retired 0
rv_entries 28 distinct 23
```

★ **`AUT-PD-113`'s "38 OF 77 ROUTES INHERIT IT" is exact, and it is the right denominator for a
retirement clause** — `blockers_inherited` is what a retirement would clear, whereas S41's population
(23 routes / 28 entries) is the narrower set holding an explicitly-blocked `required_validation`. The
two numbers answer different questions and both are in this memo's §4 on purpose. No route lists this
blocker in `blockers_retired`, so nothing has ever been recorded as released from it.

Distribution over the 38, for the blast-radius argument below: `status` = 15 blocked, 14 parked,
6 ready, 2 closed, 1 delegated; `timing.recommendation` = 25 monitor, 8 pursue_now, 4 wait, 1 closed.

---

## 3 · THE PRECISE CLAUSE, AND WHAT IT ADMITS

### 3.1 The wording, as applied

The replacement (full text now in `BLK-NO-EMC-DATA.retired_by_action`; the surrounding paragraphs of
that field — the PRJNA1357027 lead and the GSE140686 methylation record — are untouched):

> ⛔ **WHAT WOULD RETIRE IT IS A FETCHABLE OR DEPOSITED EMC DEPENDENCY OR DRUG-RESPONSE DATASET** — a
> second EMC line in DepMap, an EMC CRISPR screen, or a drug-response matrix this repository can PULL AND
> RE-ANALYSE (an accession, a supplementary data table, or any archive). None of those exists;
> TRG-SARCOMA-ATRI-RESPONSE-PANEL watches for them. ⭐ CORRECTED 2026-09-02 (S52-BLOCKER-PRECISION):
> [the old clause quoted, the paper named with PMID/doi/PMCID and its design]. ⛔ **WHAT DOES NOT RETIRE
> IT: a published panel whose numbers stay with its authors.** [data-availability statement quoted; the
> five named compounds; the three ordinal bands; no AUC or IC50 table; 35 of 40 identities unreadable]
> ★ THE DISTINCTION IS OPERATIONAL, NOT PEDANTIC […] ⚠ AND THE DIRECTION OF THE OLD ERROR WAS THE
> DANGEROUS ONE […] ⚠ Superseded, retained (rule 1.2): [the old clause].

### 3.2 The evidence that makes "deposited" the right axis rather than a convenient one

⛔ **A retirement condition must be checkable, and "a panel exists" is not checkable in a useful
direction — it was already true when the clause was written.** The axis that separates the world where
this blocker binds from the world where it does not is whether a session can OBTAIN THE NUMBERS. Three
readings from the primary text settle that this panel's numbers cannot be obtained:

1. **The data-availability statement is the canonical non-deposit**, verbatim: *"The datasets used
   and/or analyzed during the current study are available from the corresponding author on reasonable
   request. Both cell models USZ20-EMC1 and USZ22-EMC2 can be made available from the Laboratory for
   Systems Pathology and Functional Tumor Pathology, Department for Pathology and Molecular Parhology,
   University of Zurich, Zurich."* No accession, no archive, no repository. ⚠ Note the second sentence
   carries a MODEL-ACCESS offer, which is `BLK-NO-WET-LAB` / `TR-EMC-MODEL-ACCESS` territory and not
   this blocker's — the two must not be merged.
2. **Five of forty compounds are named in the accessible record; thirty-five are not.** The Results
   name carfilzomib and doxorubicin among the 17 chemotherapies and PU-H71, HDM201 and venetoclax among
   the 23 targeted agents. The remaining 35 identities live in Fig. 2a/b only. The two supplementary
   files that ARE deposited are Supplementary Table 1 (the FoundationOne variant list) and Supplementary
   Table 2 (the STR authentication) — neither is the drug matrix.
3. **What is reported for the five is an ORDINAL BAND, not a value.** *"Drug sensitivities were
   classified as (i) none, (ii) low to moderate and (iii) good to high."* The paper computes AUC and
   IC50 and prints neither in text. So even for the five named agents there is no number a route could
   rank, threshold, or compare against a class prior.

### 3.3 What the clause DOES and DOES NOT admit — stated so a future session can settle it in one read

| would retire it | would NOT retire it |
|---|---|
| A second EMC line entering DepMap with gene-effect data | A second EMC line entering DepMap with expression only |
| An EMC CRISPR / RNAi dependency screen with per-gene scores obtainable | A dependency claim transferred from a sarcoma class prior containing no EMC line |
| A deposited drug-response matrix under an accession (GEO/ArrayExpress/PRIDE/Zenodo/figshare/a journal supplementary data table) with per-compound values | A published panel whose per-compound values remain with its authors — **`EV-BANGERTER-2023` is exactly this and does not retire it** |
| The Bangerter AUC/IC50 matrix itself, if the authors deposit it or supply it on request and it is committed here | An "on reasonable request" statement, which is an offer to a person and not a fetchable dataset |
| A tumour drug-response dataset in EMC from any future cohort, deposited | A tumour EXPRESSION cohort (PRJNA1357027/SRP640302), a METHYLATION reference set (GSE140686), or any profiling dataset carrying no perturbation — **already recorded twice in this same field and unchanged by this edit** |

⛔ **Both failure modes the seat brief names are avoided, and here is the argument for each.** A clause
that a published paper already satisfies can never be honestly retired — that was the OLD clause, and
§4.4 shows what it would have cost. A clause too narrow retires a blocker that should still block half
the portfolio — the new clause cannot do that, because it is a strict subset of the old one: every
dataset that satisfies the new clause satisfies the old, and the only thing removed from the admitted
set is the undeposited published panel. **The blocker binds today exactly where it bound yesterday, on
38 routes, and now says why.**

---

## 4 · BLAST RADIUS — THE ROW'S ACTUAL ASK

### 4.1 ⭐ THE MECHANICAL HALF: NOTHING COMPUTES ON THIS FIELD

`retired_by_action` has exactly four consumers in the codebase (`grep -n retired_by_action
systems/systems_check.py`), and **not one of them reads its TEXT**:

| site | what it does | reads the text? |
|---|---|---|
| `systems_check.py:302` | forecast classifier — presence promotes the blocker to `class: "action"`, `when: "not forecast — an action, not an advance"` | no, truthiness only |
| `systems_check.py:634` | invariant **B2** — errors if a non-permanent blocker names neither a technology nor an action | no, truthiness only |
| `systems_check.py:2950` | renders it into a register row, or `*permanent*` / `—` | verbatim passthrough |
| `systems_check.py:3334`, `:3349` | renders it into the blockers register, truncated to 120 chars in one place and whole in the other | verbatim passthrough |

★ **So the wording cannot move a grade, a status, a ranking or an inheritance edge by any mechanism.**
Both consumers that branch on it branch on whether the string is non-empty, and both the old and the new
string are non-empty. The single generated file that changed is
`systems/views/registers/blockers.md`, written by `--write-views`. ⛔ **The blast radius of this field is
therefore entirely on READERS — and in this repository the reader is the next session**, which is
precisely the population CLAUDE.md §6 says the content-rigour rule exists to protect.

### 4.2 ⛔⛔ THE PROSE HALF — AND THE THREE ROUTES THAT DO NOT KNOW THEIR OWN COMPOUND WAS SCREENED

Test run over the 38 inheriting routes: does any route's grade, readiness or unknowns assert the absence
the old clause asserted? A regex sweep for absence-of-drug-data claims
(`no (EMC )?(ex-vivo|drug-response|drug screen|drug sensitivit)…`, `no drug screening…`, `never been
screened/tested…`) over the full JSON of each of the 38 returns **one** hit, `RT-ALK-HIT`, and it is
about a specific record's contents rather than the state of EMC drug data:

> "no drug response, nothing on ROS1, and nothing about the model the 221-drug screen ran on"

**So no inheriting route's prose grade rests on the looser reading, and the falsity was confined to the
blocker record itself.** That is the finding that made the edit safe to apply.

⚠ **But the sweep for the CONVERSE — routes that should hold the panel and do not — is where the value
is.** Only **two** of the 77 routes mention Bangerter anywhere in their record (`RT-CARFILZOMIB`,
`RT-PARTNER-STRAT`), and both cite `EV-BANGERTER-2023` properly. Ten of the 38 mention `ex vivo` /
`patient-derived` / `USZ` at all. Cross the five named compounds against the 38:

| compound (named in the accessible record) | class | reported band | route selected by that class | inherits `BLK-NO-EMC-DATA`? | cites the paper? |
|---|---|---|---|---|---|
| carfilzomib | proteasome | "the only compound that showed high sensitivity" | `RT-CARFILZOMIB` | yes | **yes** — grade is built on it |
| doxorubicin | anthracycline | "good sensitivity" | — (no route selects on it alone) | — | n/a |
| **PU-H71** | **HSP90** | **"performed best from the compounds tested and showed good sensitivity"** | **`RT-CHAPERONE`** | **yes** | **NO** |
| **HDM201** | **MDM2/MDM4** | **"performed best from the compounds tested and showed good sensitivity"** | **`RT-MDM2`** | **yes** | **NO** |
| venetoclax | BCL2 | "moderate" in screen; **no monotherapy response** on validation; additive/synergistic in combination | `RT-APOPTOSIS-DEP` | yes | **NO — uses the result, names no source** |

The sentence all three rest on, verbatim: *"PU-H71 (HSP90) and HDM201 (MDM2/MDM4) performed best from
the compounds tested and showed good sensitivity while the cells had a moderate sensitivity to
venetoclax."*

**`RT-CHAPERONE`** — ⛔ **the strongest of the three, because the route's own literature file went
looking for this and came back empty.** Its `remaining_unknowns[0]` records a 2026-08-27 assessment:
*"NO FET-family fusion protein is a documented client … What does exist is dependence without binding —
EWS::FLI1 protein falls on HSP90 inhibition"*, pointing at
`research/literature/fet-fusion-chaperone-clientship-2026-08-27.json`. That file contains **zero**
occurrences of `Bangerter`, `USZ20`, `USZ22`, `EMC1`, `9813045` or `36316541` — checked by string count.
And the Ewing evidence it does hold is **PU-H71 itself** (*"Pre-clinical efficacy of PU-H71, a novel
HSP90 inhibitor, alone and in combination with bortezomib in Ewing sarcoma"*, also in
`research/literature/live-lane-answers-2026-08-09.json`). ★ **So the repository cites PU-H71-in-Ewing as
a class transfer while a PU-H71-in-EMC reading sits unused in its own literature cache.**
⚠ **What this does NOT do:** an ordinal band on one model, single-arm, with no normal-cell comparator
and no AUC, does not answer the route's actual premise (is the chimera a chaperone CLIENT — a binding
question), supplies no therapeutic index, and cannot distinguish tumour need from general need. **The
grade `◐ PARTLY SUPPORTED` stands.** What changes is that the dependence-without-binding half acquires
a direct EMC observation in place of a Ewing transfer, and that is a `supporting_evidence` addition, not
a re-grade.

**`RT-MDM2`** — ⛔ **graded `NOT SUPPORTED` on expression alone, while the primary source carries a
pharmacologic reading in the opposite direction AND the selecting copy-number lesion.** Its grade reads
*"The class needs a p53 axis that is intact AND LIVE. The p53 transcriptional output group reads LOWER
in EMC on BOTH platforms"*; `timing.recommendation` is `monitor`; `next.best_next_action` is *"Report
the negative; the quiet-genome inference did not survive its own test."* Against that:
- HDM201 is an MDM2/MDM4 antagonist and is one of the two best-performing targeted agents in the screen.
- The same paper reports, verbatim: *"The copy number profiles exhibited gains mainly in chromosome 1,
  where the MDM4 locus is located, and in chromosome 8, where MYC is located for USZ20-EMC1."* **An
  MDM4 gain is a selecting feature for this drug class**, and the route holds it nowhere.
- The route's own `remaining_unknowns[0]` is *"Whether TP53 is wild-type, which this reading does not
  establish either way"*. ⚠ **UNKNOWN, and it stays UNKNOWN here.** The strings `TP53` and `p53` appear
  **zero** times in the cached full text; the variant list is in Supplementary Table 1, a PDF this seat
  did not read. **An absent reading is not a reading of absence** — do not infer wild-type TP53 from the
  body text's silence.
⚠ **AND THE REPOSITORY'S ONLY EXISTING RECORD OF HDM201 SAYS THE OPPOSITE OF THE PAPER.**
`research/autonomy/sprint-2026-09-01/S39-ATLAS-ADJUDICATION.md:166` carries the row
*"MDM2/MDM4 — HDM201 not a USZ hit | `repurposing-hypotheses-review.md` (identities resolved via CI full
text)"*. Checked, not assumed: `grep -n -i "hdm201\|MDM2"` over
`research/manuscripts/repurposing/repurposing-hypotheses-review.md` returns **nothing**, and `HDM201`
appears elsewhere in the repository only as unrelated GEO sample titles ("HDM201 rep1/2/3") in
`research/modalities/emc-cohort-search-inputs.json`. **So the claim has no home at the pointer given and
contradicts the primary source.** ⛔ Not this seat's file and not corrected here; filed in §7.
⚠ **The route does not become supported.** n = 1, ordinal band, no TP53 call, and the class's stated
haematological toxicity liability is untouched. What it becomes is a route whose `next.best_next_action`
("report the negative") is **wrong about the cheapest remaining observation**.

**`RT-APOPTOSIS-DEP`** — a provenance gap rather than a missing reading. Its grade already says *"what
would explain this repository's own EMC result where BCL-2 inhibition was inactive alone and active only
in combination"*, which is Bangerter's venetoclax result exactly — but the route cites no evidence id for
it, and its `supporting_evidence` lists only `ART-CENSUS-ROUTE-GRADING`. ⚠ **§7 of CLAUDE.md: claim
STRENGTH is orthogonal to citation PROVENANCE.** The claim is correctly stated and correctly weighted;
it is simply unattributed. Adding `EV-BANGERTER-2023` to `supporting_evidence` changes no grade.

### 4.3 The other 35 — why none of them moves

The remaining 35 inheriting routes fall in three groups, and no member of any group has a grade that the
precise wording touches:

- **The 23-route / 28-entry `required_validation` population** already adjudicated by S32 and S41. Their
  verdicts turn on what each entry ASKS for (an expression read, a clinical series, a registry
  reanalysis, a dependency screen), never on whether an ex-vivo panel exists in the world. S41's table
  is the authority and this memo does not amend a single row of it. ⛔ **And S41's re-attributions and
  this memo's rewording are complementary rather than overlapping:** S41 moves 6 entries off a blocker
  that never claimed them; this memo makes the blocker say what it claims. Neither is sufficient alone.
- **Routes inheriting the blocker with no `required_validation` entry on it** — the difference between
  38 and 23. For these it is a portfolio-level rate-limiter carried at the route header, and a header
  inheritance has no grade of its own.
- **The 2 `closed` and 25 `monitor` routes**, whose next actions are literature reads, negatives, or
  waits on `TR-EMC-MODEL-ACCESS`. None is gated on a deposited dataset arriving.

### 4.4 ⛔ WHAT THE OLD CLAUSE COULD HAVE COST, WHICH IS WHY THE ROW SCORED 132.9

Read literally — and a session doing the honest thing reads literally — the old clause said this
blocker's own retirement condition was **already met**. `EV-BANGERTER-2023` is committed, cited, and
resolvable in three identifier systems; a session finding it and matching it against *"an ex-vivo panel,
none of which exists"* has a complete, self-consistent argument for retiring `BLK-NO-EMC-DATA` and
releasing **38 of 77 routes in one edit**, with `blockers_retired` currently empty on every one of them.
⚠ **Nothing in the build would have stopped it**: §4.1 shows the field is prose, B2 only requires that
SOME retirement condition be named, and the B3 warning fires on blockers that hold down *no* route — the
opposite direction. **The guard against that edit was a sentence, and the sentence was wrong.**

---

## 5 · WHAT I APPLIED, AND THE VERDICT

Applied to `systems/graph/blockers.json`: a single-key replacement inside
`BLK-NO-EMC-DATA.retired_by_action`, made by anchoring on the exact old clause (asserted unique before
replacing) so no other byte of the file moved. `git diff --stat -- systems/graph/blockers.json` →
**`1 file changed, 1 insertion(+), 1 deletion(-)`**.

Views regenerated with the repository's own generator — `python3 systems/systems_check.py --write-views`
→ `systems_check: wrote 104 view(s) to systems/views/`, with exactly one view changing
(`systems/views/registers/blockers.md`). **No file under `systems/views/` was hand-edited.**

`python3 systems/systems_check.py --check`, verbatim verdict line:

```
systems_check: 604 objects across 15 collections · 0 ERROR · 87 WARN · 7 INFO
```

exit code **0**. ⚠ **Recorded honestly:** an intermediate run of the same command showed
`1 ERROR · 87 WARN`, and the error was `[D4] research/autonomy/sprint-2026-09-01/S49-BLOCKER-LEVERAGE.md
has no frontmatter` — another seat's untracked memo, resolved by that seat between my two runs. It never
touched `blockers.json` and my edit never produced an error. The 87 WARN are pre-existing and unrelated
(X4 ungraded scan signals, D5 unverified documents, K3 dead pointers in S43's memo, B9 over-claiming
triggers).

⛔ **Gates:** `./scripts/preflight.sh` was NOT run by this seat — it is the driver's to run before the
commit that lands this, with the whole sprint's tree settled (CLAUDE.md §6: one run, tree settled).

---

## 6 · What I did not touch

- `systems/graph/routes.json` — S41's patch is pending on it; three route defects found here are filed
  as rows in §7 rather than applied.
- `research/autonomy/research-ledger.json` — sprint-wide no-touch; the driver writes it.
- `research/manuscripts/**` — read-only here (`repurposing-hypotheses-review.md` was grepped, not
  edited).
- `research/autonomy/sprint-2026-09-01/S39-ATLAS-ADJUDICATION.md`, `S41-*` — other seats' files.
- No git write command was run: `git rev-parse`, `git diff --stat`, `git status --porcelain`,
  `git show origin/literature-cache:…` only.

---

## 7 · Ledger rows the driver should write

| what | kind | state | serves |
|---|---|---|---|
| **`RT-CHAPERONE` does not hold the EMC PU-H71 reading that sits in this repository's own literature cache.** Its `fet-fusion-chaperone-clientship-2026-08-27.json` has zero occurrences of Bangerter/USZ20/PMC9813045 while citing PU-H71-in-EWING as the class transfer. Add `EV-BANGERTER-2023` to `supporting_evidence` with the ordinal band and its limits stated (n = 1, no comparator, no AUC), and record in `remaining_unknowns` that the AUC rank is in Fig. 2b and unread. **$0 — no fetch beyond a branch read.** ⛔ Not a re-grade: the clientship premise is untouched. | `process_defect` | `queued` | `RT-CHAPERONE` |
| **`RT-MDM2` is graded `NOT SUPPORTED` on expression alone and its `next.best_next_action` is "report the negative", while the primary source carries HDM201 among the two best-performing targeted agents in an EMC model AND a chr1 gain at the MDM4 locus.** Re-read Bangerter Fig. 2b and Supplementary Table 1 (for a TP53 call, currently **UNKNOWN** — `TP53`/`p53` appear zero times in the cached body text). **$0.** ⛔ Does not promote the route; it replaces a wrong "nothing left to look at". | `fetch` | `queued` | `RT-MDM2` |
| **`S39-ATLAS-ADJUDICATION.md:166` asserts "MDM2/MDM4 — HDM201 not a USZ hit" and points at `repurposing-hypotheses-review.md`, which contains neither string.** The primary source says the opposite. A claim with no home at its own pointer, contradicting a cached full text. | `process_defect` | `queued` | — |
| **`RT-APOPTOSIS-DEP`'s grade uses Bangerter's venetoclax result and names no source.** Add `EV-BANGERTER-2023` to `supporting_evidence`. Provenance only; no claim changes strength. | `process_defect` | `queued` | `RT-APOPTOSIS-DEP` |
| **A guard is missing under `BLK-NO-EMC-DATA`:** nothing in `systems_check.py` can tell that a retirement clause has become satisfiable, because nothing reads the field's text (§4.1). Consider a test asserting that no committed `EV-*` record's `citation` matches a phrase this field declares non-existent. | `process_defect` | `queued` | — |
