# Y1 — provenance of "Roughly 3 to 4 per cent of EMC carries TCF12::NR4A3"

Worker Y1. Input revision 545e6cf7c1dd7099f5072444d4dd166c4536206e; session HEAD 49d7748f96ea20c0373f6ddc01a0b9d9ce9684c3.
Read-only. No manuscript edit, no shared-path write, no git write, no network.

## VERDICT

**SUPPORTED — with one denominator qualification that the proposed fix carries.**

Committed inputs contain (a) a **pooled, computed** TCF12::NR4A3 prevalence of **5/154 = 3.2 %
(95 % CI 1.4–7.4)** over four independent molecular series, and (b) the **two per-series
percentages 4 % and 3 %** that bracket the manuscript's "3 to 4 per cent" exactly, one of them
(Agaram 2014) **already reference 6 of this manuscript's own reference list**.

The qualification: every committed figure has denominator *partner-assigned / molecularly
confirmed* EMC, not "EMC". The manuscript says "of EMC". No committed input states the range
"3 to 4 per cent" verbatim; the range is the bracket of the two series figures.

## The quotations, with file and path

1. `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json`, `pooled` block (lines
   1477–1485) — the computed artifact:
   > `"TCF12::NR4A3": { "events": 5, "denom": 154, "proportion": 0.0325, "percent": 3.2,
   > "ci95_lo_percent": 1.4, "ci95_hi_percent": 7.4, "interval": "Wilson score, 95%" }`
   Cohorts pooled (`partner_assigned_per_cohort`): agaram-2014 24, huang-2023 57, lenz-2023 11,
   paioli-2021 62. Excluded, with reasons recorded: llombart-bosch-2022 (abstract-only),
   klubickova-2022 (overlap with lenz-2023), sjogren-2003 (§2.1(3), outcome is the inclusion
   criterion).

2. `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md:433` — the same value
   in prose, in §3.5 "Partner prevalence":
   > `| TCF12::NR4A3 | 5/154 | 3.2 % | 1.4–7.4 |`
   Column header: **"share of partner-assigned EMC"**. Pinned by
   `research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py:997`.

3. `research/manuscripts/program/emc-post-degrader-options.md:356–358` — the likeliest textual
   ancestor of the sentence, since it states both endpoints in one breath:
   > "From two published series: **EWSR1 62 % / TAF15 27 % / TCF12 4 %** (n = 26, Agaram et al.,
   > *Hum Pathol* 2014) and **EWSR1 79 % / TAF15 16 % / TCF12 3 %** (n = 58, Huang SC et al.,
   > *Mod Pathol* 2023)."

4. `research/literature/rt-lung-mets-probe.json:396` (Agaram 2014 abstract, verbatim):
   > "…EWSR1-NR4A3 gene fusion in 16 cases (62%), TAF15-NR4A3 gene fusion in 7 cases (27%), and
   > **TCF12-NR4A3 gene fusion in 1 case (4%)**."

5. `research/literature/no-wet-lab-archetypes-2026-08-12.json:218` and `:741` (Huang 2023, n = 58):
   > "46 EWSR1::NR4A3 (79%), 9 TAF15::NR4A3 (16%), **2 TCF12::NR4A3 (3%)**, 1 NR4A3-rearranged with
   > no identified partner (2%)."
   Same figures at `research/manuscripts/no-wet-lab-publication-archetypes.md:295` and
   `research/manuscripts/program/emc-post-degrader-options.md:1122`.

6. `research/autonomy/opus-capacity-campaign-20260908/paper-lane/R2-executed-artifacts/BASELINE-emc-clinical-registry.json:30`:
   > "In one molecularly confirmed series of 58 cases, fusions were EWSR1::NR4A3 in 79%,
   > TAF15::NR4A3 in 16% and **TCF12::NR4A3 in 3%**."

**Committed figures that do NOT match, recorded so the range is not read as universal:**
`research/literature/rt-lung-mets-probe.json:166` — Paioli-type series, "1 (2%) NR4A3-TCF12" of 62
partner-assigned; and Sjögren 2003, TCF12 **1 of 10** (10 %), quoted in
`research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md:96` and
`…-review-response-2026-08-10.md:95`. Sjögren is the series X1 found and is *excluded* from the pool
on a stated policy ground, which is why it does not defeat 3.2 %.

## Where I looked (so the search is reproducible)

- The claim and its section: `research/manuscripts/dependency/emc-atr-collaborator-package.md`
  lines 370–400; every "%"/"per cent" occurrence in that file (lines 170, 382, 394, 397, 398).
- The manuscript's own reference list (§8) and Data-and-code table (§7).
- Its peer review `…-peer-review-2026-08-10.md`, review response `…-review-response-2026-08-10.md`,
  changelog `…-changelog.md`, and companion `emc-atr-vulnerability-assessment.md`.
- `research/literature/*.json` (incl. `rt-lung-mets-probe.json`,
  `no-wet-lab-archetypes-2026-08-12.json`, `tcf12-nr4a3-breakpoint-primary-sources.json`),
  `research/modalities/*.json`, `systems/graph/*.json`, `research/hypotheses/`.
- `research/manuscripts/fusion-partner/` (pooling JSON, stratification MD, correction register,
  partner-event-counts) and `research/manuscripts/aso/lit-targets-aso-verify.json`.
- Retained campaign records: `research/autonomy/opus-capacity-campaign-20260908/paper-lane/**`
  (X1-DECISION-RECORD §9 UNRESOLVED, R1/R2/U1/W-inputs, proposed diffs) and
  `…/reports/**` (W01c/W01e/W01h/W01i, W03, W06, W07e/W07g, W10c, W19–W23, W30).
- Numeric searches, repo-wide excluding `.git`: `3 to 4 per cent`, `3-4%`, `3–4%`, `3 to 4%`,
  `roughly 3`, `3% to 4%`, `0.03`, `0.04`, plus `TCF12` co-occurring with
  `%|per cent|frequen|preval|cases|series`.
- Git history: `git log --all -S "3 to 4 per cent"` and `--diff-filter=A` on the manuscript. The
  file and the phrase both first appear in the squash-merge `14a3f172`, so the introducing edit is
  not recoverable from history; the later touching commits are `fb6f7028`, `67050fcc`, `545e6cf7`.

## PROPOSED minimal fix (not applied — I edited nothing)

Replace line 382's opening clause, and add one reference. Smallest change that sources the figure
and fixes the denominator:

> **Proposed:** "TCF12::NR4A3 is carried by 3.2 per cent of partner-assigned EMC (5 of 154 pooled
> across four independent molecular series, 95 % CI 1.4 to 7.4) [6,9], and TCF12 is not a
> FET-family gene."

Home of the arithmetic, for the §7 table:
`research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` → `pooled.TCF12::NR4A3`.

Citation to attach — reference 6 already exists (Agaram 2014, 1/26 = 4 %); the second series needs
a new entry:

> Huang SC, et al. *Mod Pathol* 2023. PMID 36948401. doi 10.1016/j.modpat.2023.100161. 58
> molecularly confirmed EMC; EWSR1::NR4A3 46 (79 %), TAF15::NR4A3 9 (16 %), TCF12::NR4A3 2 (3 %).

⚠ Two cautions the coordinator must weigh before applying: (i) the Huang record is **abstract-level**
in this repository — W07g records PMID 36948401 as having **no PMC full text, UNRECOVERED**, and
`W01e` D5 flags a possible Huang/Warmke attribution conflation that `emc-post-degrader-options.md`
already corrected on 2026-08-08; the DOI above is copied from the committed record at
`research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`-adjacent artifacts and
should be re-checked against that record before it is typed into a reference list, not retrieved.
(ii) A lighter alternative that needs **no new reference** is to cite reference 6 alone and write
"about 4 per cent in one series of 26 (1 case) [6]" — narrower, fully sourced from the existing list.

⛔ I make no epidemiological claim of my own. Every figure above is quoted from a committed file.

## What I did NOT do

No manuscript or shared-path edit. No git write, no commit, no branch. No network, retrieval,
PubMed call or new source. No gate, preflight, test or figure run. No census beyond this question.
No closed contract reopened. Nothing deleted. Did not verify the Huang DOI or resolve the
Huang/Warmke attribution question — both are out of scope and are flagged above.

## State receipts

- **Start:** `2026-09-08T12:22:29Z`, HEAD `49d7748f96ea20c0373f6ddc01a0b9d9ce9684c3`,
  `git status --porcelain` **empty**.
- **End:** `2026-09-08T12:24:59Z`, HEAD `67ee85e3b7a61a2c71477d0afae421a9027e229b`,
  `git status --porcelain` **empty**.
- ⚠ HEAD moved during the task and **not by me.** The single intervening commit is
  `67ee85e3 "paper-lane: Y1 executing on the unsourced TCF12 frequency"`, whose entire diff is
  `+42` lines adding `…/paper-lane/Y1-MODEL-START-RECEIPT.md` — written by the coordinator, not by
  this worker. I issued no git write command of any kind. The manuscript line 382 is byte-identical
  at both revisions. Every quotation above re-reads the same at `67ee85e3`.
- Deliverable: `/tmp/claude-0/y1-lane/Y1-MEMO-tcf12-frequency-provenance.md` (this file, the only
  file I created).
