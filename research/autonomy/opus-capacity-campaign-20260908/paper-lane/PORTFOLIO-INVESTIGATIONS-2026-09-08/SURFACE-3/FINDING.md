---
id: DOC-PORTFOLIO-INVESTIGATION-SURFACE-3
title: "SURFACE-3 — what does the surface-target manuscript claim on the strength of a screen that never ran?"
level: L4
kind: audit
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# SURFACE-3 — claims resting on an unfired vital-tissue screen

Branch `claude/confident-bardeen-ji76cd`, tree `b14a84259`. Offline, committed files only. **Nothing
outside this directory was written.** No commit, no push, no preflight, no subagent, no network, no
HTTP egress, no re-probe of HPA or any other host. `git status` shows `research/manuscripts/` and
`research/modalities/` unmodified.

## 1 · The question

SURFACE-2 established that the 21-tissue vital-tissue screen in
`research/modalities/emc-surface-normal-window.json` **has never fired** — 45 classified records, a
null per-tissue nTPM input on every one, `vital_tissue: []` on every one — and CLOSED-ROUTES-2
established why (HPA's `rnatss` column is already requested and comes back empty). Neither was
re-litigated or re-probed here. The bounded manuscript-integrity question that leaves:
**what does the PUB-SURFACE-TARGETS document family claim on the strength of that screen, and which
of those claims assert an absence the screen never measured?**

## 2 · Merit

A surface-target paper's normal-tissue arm is the one thing a reader converts directly into "which
antigen would you stain, and what would you not put a T cell against". If any sentence in the family
says an exclusion was performed when the exclusion's input never arrived, a reader inherits a
confidence no measurement supports — and in the direction that matters most, because the missing
half of the verdict is the *vital-organ* half. The correction is cheap, checkable and permanent, and
it is exactly CLAUDE.md §4's distinction between a missing measurement and a zero.

## 3 · Re-derivation first — SURFACE-2's core measurement reproduces

Run before anything else was written (`checks/02-rederive-surface2-core`, exit **0**), independently
of SURFACE-2's script, against `research/modalities/emc-surface-normal-window.json`
(sha256 `0787c7f7…5b09aab`):

| Quantity | Re-derived here | SURFACE-2 |
|---|---:|---:|
| Antigen rows in the artifact | 46 | 46 |
| **Classified records** (carry a `window`) | **45** | 45 |
| Unclassified | 1 (`ALPPL2`, discarded symbol mismatch) | 1 |
| Records with a **non-empty `vital_tissue`** | **0** | 0 |
| Records with a **non-null `rna_tissue_specific_nTPM`** (the screen's input) | **0** | 0 |
| Vital-tissue labels the screen advertises | 21 | 21 |

**It reproduces.** No discrepancy, so the task continued past step 4 rather than stopping there.

## 4 · The step taken, and the honest outcome

Every sentence, table cell, caption and artifact field in
`research/manuscripts/surface-targets/` (plus the `research/manuscripts/README.md` entry that
summarises it) that rests on the vital-tissue screen having produced a result was enumerated and
sorted, with file and line, into **(a)** claims asserting an absence of vital-tissue expression and
**(b)** claims correctly reporting the field as null or unknown. `CLAIM-LIST.md` is the enumeration.

**Outcome — and it is a partly negative one, which is the useful part.** The **main manuscript and
the SI are already correct on this axis**: 21 sites (b1–b21), including *both* display-item captions
(Table 1 at `emc-surface-target-landscape.md`:918–923 and Table S2 at `…-si.md`:299–303), already
state that the quantitative fields are null for all 45 classified records, that the vital-tissue
branch never inspected an expression level, and that a RESTRICTED label is "not evidence of absence
from any vital tissue". A previous correction pass reached the paper.

**It did not reach the surrounding texts.** Category (a) is **4 sites in 3 files**, all of the same
shape — the phrase "a **hard** normal-tissue-window filter" / "a **hard** normal-tissue window",
asserting an exclusion step:

| # | Site | Fragment |
|---|---|---|
| a1 | `…/emc-surface-target-outreach.md`:54–55 | "a hard normal-tissue-window filter, most 'obvious' candidates fall away" |
| a2 | `…/emc-surface-target-outreach.md`:92–93 | same, second recipient letter |
| a3 | `…/emc-surface-target-redteam.md`:182–183 | "(2) a hard normal-tissue window under which most candidates are liabilities" — listed as a *surviving main result* |
| a4 | `research/manuscripts/README.md`:107–108 | the repository index restating a3 |

**What it would take to support them — the exact missing input, identical for all four:** HPA's
per-tissue nTPM column (`rna_tissue_specific_nTPM`, requested as `rnatss`) returned **non-null for
the 45 classified records**, so the 21-label substring branch has something to match. Nothing else
substitutes: a categorical specificity label is not a per-tissue level, and even a non-null nTPM
field would not be a per-tissue expression matrix (the manuscript already says so at
`…-landscape.md`:263–266). That fetch is a networked acquisition, **out of scope and behind a
recorded closure** (CLOSED-ROUTES-2) — so the supportable statement today is UNKNOWN, not a promise
of a future value.

**Ordering checked, no hit.** Table 1 is ordered by enrichment, not by verdict; the only
verdict-gated set (selective ∩ RESTRICTED → DLL3) is already stated as a stored-label intersection.
`vital_tissue` is empty on every row and therefore orders nothing.

## 5 · Artifact · validation · provenance · limitations · stop condition

* **Artifact** — `CLAIM-LIST.md` (4 category-(a) sites with file:line and missing input; 21
  category-(b) sites; 2 adjacent items deliberately excluded and why),
  `UNAPPLIED-vital-tissue-unknown.diff`, `rederive_surface2_core.py`, `generate_diff.py`,
  `checks/01`–`04`.
* **Validation** — the core measurement is re-derived independently and reproduces exactly
  (`checks/02`, exit 0); the diff is machine-generated from unique anchors (a non-unique anchor exits
  2 rather than guessing) and **applies cleanly: `git apply --check --verbose`, real exit `0`,
  `checks/04-git-apply-check`**. `checks/01` preserves a genuine failure (wrong `ROOT` depth,
  `FileNotFoundError`, exit 1) rather than only the run that worked. Both scripts are read-only
  outside this directory.
* **Provenance** — `research/modalities/emc-surface-normal-window.json` (sha256 recorded in
  `checks/02/stdout.txt`); `research/manuscripts/surface-targets/*` and
  `research/manuscripts/README.md`; the lane records `SURFACE-2/FINDING.md` (§3.2 C2),
  `CLOSED-ROUTES-2/`, `PUB-SURFACE-TARGETS/FINDING.md`; `systems/graph/publications.json`
  (PUB-SURFACE-TARGETS → `research/manuscripts/surface-targets/emc-surface-target-landscape.md`).
  `systems/POLICY-evidence.md` read before this lane touched anything; **no registry-adjacent file
  and no clinical registry record was read for content or edited.**
* **Limitations** — this is a **claim audit of prose and stored labels against a recorded null**. It
  measures no expression, re-derives no HPA value, and checks nothing against HPA's live records. It
  cannot say what any antigen's vital-tissue expression **is**. The category (a)/(b) split is a
  reading of English, applied by one stated rule and reproducible from the file:line table, not a
  computed quantity. The car-t-strategies B7-H3 tension (§ "Adjacent" in `CLAIM-LIST.md`) is
  recorded and **not** graded — it is a protein-literature question, not a screen question.
* **Stop condition** — reached: the enumeration is complete over the named family, the diff proves
  out at exit 0, and the remaining dependency is a closed networked fetch. Stop also if any owner
  applies a competing edit to the same four sites, in which case this diff is superseded rather than
  rebased.

## 6 · The unapplied diff

`UNAPPLIED-vital-tissue-unknown.diff` — three files, four sites, **not applied and not to be applied
by this lane.** Each hunk (i) replaces "hard … filter/window" with "normal-tissue **category
annotation**", (ii) states that the vital-tissue screen **produced no input and never ran**
(per-tissue nTPM null on all 45 classified records) and that vital-tissue status is therefore
**UNKNOWN**, and (iii) preserves the superseded wording verbatim in a dated
`⛔ *Superseded, retained (2026-09-09): …*` note rather than erasing it (the two outreach hunks; the
red-team and README hunks are single-sentence rewrites inside paragraphs that already carry their own
dated amendment blocks).

⛔ **The diff makes no safety claim in either direction.** It does not say any antigen is safe and it
does not say any antigen is unsafe; it says a screen produced no input, so the question is open. It
changes no threshold, no rule, no verdict, no label, no antigen's standing and no ordering. It does
not touch `research/modalities/`: the artifact-field form of the same defect is already covered by
SURFACE-2's unapplied producer diff, and two lanes editing one producer would be worse than one.

## 7 · Next credible independent work

1. The blocking dependency is unchanged and **recorded closed**: non-null `rna_tissue_specific_nTPM`
   for the 45 classified records. Until it exists, UNKNOWN is the only supportable statement.
2. A **sweep for the same shape elsewhere**: this lane found that a correction pass reached the
   manuscript and SI but not the outreach, red-team and index texts. Whether other paper families
   share that pattern — corrected body, uncorrected satellite — is a bounded, checkable question and
   is **not** this lane's to answer.
3. Owner decision on the car-t-strategies B7-H3 "restricted on normal tissue" line against this
   programme's own `BROAD_LIABILITY` label for CD276.
