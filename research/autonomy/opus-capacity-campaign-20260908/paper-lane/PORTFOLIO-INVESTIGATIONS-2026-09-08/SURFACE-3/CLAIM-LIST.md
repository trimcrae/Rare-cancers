---
id: DOC-PORTFOLIO-INVESTIGATION-SURFACE-3-CLAIMS
title: "SURFACE-3 claim list — every surface-target claim that rests on the vital-tissue screen having produced a result"
level: L4
kind: audit
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# SURFACE-3 — claim list

Scope: the PUB-SURFACE-TARGETS document family (`research/manuscripts/surface-targets/`, plus the
`research/manuscripts/README.md` entry that summarises it). Line numbers are against the committed
tree at `b14a84259`, branch `claude/confident-bardeen-ji76cd`.

Established upstream and **not re-probed here**: the 21-tissue vital-tissue screen has never fired —
45 classified records, per-tissue nTPM null on every one, `vital_tissue: []` on every one
(SURFACE-2), because HPA's `rnatss` column returns empty (CLOSED-ROUTES-2). Re-derived independently
in `checks/02-rederive-surface2-core` (exit 0) before this list was written.

**The sorting rule.** A claim is **(a) unsupported** if it asserts, states or implies that a
vital-tissue / normal-tissue *exclusion* was performed or passed. A claim is **(b) fine** if it
reports the field as null, the branch as never fired, or the verdict as a stored category label.

---

## (a) Unsupported — assert an exclusion the screen never performed

| # | File : line | Claim, verbatim fragment | Why unsupported | Exact missing input |
|---|---|---|---|---|
| a1 | `research/manuscripts/surface-targets/emc-surface-target-outreach.md` : 54–55 | "with a rigorous selectivity test and **a hard normal-tissue-window filter**, most 'obvious' candidates fall away … CD56/CDH11/others carry specific normal-tissue liabilities" | "Hard … filter" asserts an exclusion step. The vital half of that filter never executed on any record; the surviving liability labels come from the blood-cell category branch alone. | HPA `rna_tissue_specific_nTPM` (per-tissue nTPM) non-null for the 45 classified records — the `rnatss` column that returns empty. Nothing less makes the 21-tissue branch executable. |
| a2 | `…/emc-surface-target-outreach.md` : 92–93 | "with a rigorous selectivity test and **a hard normal-tissue-window filter**, most candidates fall away … CD56/CDH11 carry normal-tissue liabilities" | Same assertion, second recipient letter. | Same as a1. |
| a3 | `…/emc-surface-target-redteam.md` : 182–183 | "(2) **a hard normal-tissue window** under which **most candidates are liabilities**" | Presented as a surviving *main result* of the red-team passes. The window is a category annotation whose vital branch is inert; "hard" claims a screen that produced no input. | Same as a1. |
| a4 | `research/manuscripts/README.md` : 107–108 | "rigorous selectivity + **a hard normal-tissue window** show B7-H3 is not selective and the selective candidates carry window liabilities" | The repository index restates a3 as the paper's summary, so the unsupported form is the one a reader meets first. | Same as a1. |

All four are corrected by `UNAPPLIED-vital-tissue-unknown.diff`. **The correction states that the
screen produced no input and the vital-tissue status is UNKNOWN. It states no safety conclusion in
either direction, and it changes no antigen's standing, label, ordering or verdict.**

### Adjacent, recorded, and deliberately NOT in the diff

* `…/car-t-strategies-emc.md` : 40 — "B7-H3 / CD276 … Expressed in 97% of soft-tissue sarcomas (69% high), **restricted on normal tissue**". This is a cited-literature claim about B7-H3 protein, not an output of the screen, so it is outside category (a) as defined. It nonetheless **sits beside** this programme's own stored label for CD276, `BROAD_LIABILITY` (SI Table S2, `…-si.md` : 329). That tension is real and pre-dates the screen question; grading it would require a protein-level source review this lane has no mandate for.
* `research/modalities/emc-surface-normal-window.json` — the artifact-field form of the same defect: `vital_tissue: []` serialised on all 45 classified rows, the `vital_tissues_flagged` block advertising 21 tissue labels, and the `_note` defining `VITAL_OR_IMMUNE_LIABILITY` as "expressed in a vital tissue **or** immune/circulating cell". **Already covered by SURFACE-2's unapplied producer diff (hunk 1).** Not duplicated here — two lanes proposing competing edits to the same producer would be worse than one.

---

## (b) Fine — correctly report the field as null / the branch as never fired

Recorded because the null result is load-bearing: the manuscript body and SI are, on this axis,
**already corrected**, and the residue in (a) is confined to the outreach, red-team and index texts
that were not swept when the body was.

| # | File : line | What it says |
|---|---|---|
| b1 | `…/emc-surface-target-landscape.md` : 90–92 | Scope box: verdicts are "historical labels … whose quantitative tissue and blood fields are null for every classified record"; "no clean normal-tissue window, **no absence from any vital tissue** and no exposure bound is established by anything in this paper". |
| b2 | `…/emc-surface-target-landscape.md` : 245 (heading) | "Normal-tissue annotation heuristic, **and what it did not observe**". |
| b3 | `…/emc-surface-target-landscape.md` : 257–261 | "The implemented classifier did not run the quantitative half of that rule… null for **all 45 classified records**… the vital-tissue branch never inspected an expression level… All nine VITAL_OR_IMMUNE_LIABILITY labels therefore arise from the blood-category branch alone." |
| b4 | `…/emc-surface-target-landscape.md` : 263–266 | "RESTRICTED is consequently a category label from an incompletely observed heuristic. It is **not** evidence of absence from any vital tissue, not a validated therapeutic window…". |
| b5 | `…/emc-surface-target-landscape.md` : 252–255 | The *declared* rule is quoted as declared ("no vital-tissue signal…"), immediately before b3 withdraws its quantitative half. Reporting a rule as declared is not asserting it ran. |
| b6 | `…/emc-surface-target-landscape.md` : 473–476 | "Because the quantitative tissue and blood fields are null for every classified record and the vital-tissue branch never inspected an expression level (Methods), a RESTRICTED label here is a historical category assignment and not a demonstrated clean normal-tissue window." |
| b7 | `…/emc-surface-target-landscape.md` : 488–490 | FGFR1/MCAM/EPHB4 liability labels are "category assignments from blood and distribution fields **rather than measured vital-tissue exposure**". |
| b8 | `…/emc-surface-target-landscape.md` : 918–923 (Table 1 caption) | "the quantitative tissue and blood fields are null for all 45 classified records, so **no verdict here reflects a measured vital-tissue level**". Covers every `Normal-tissue verdict` cell of Table 1 (lines 925–950). |
| b9 | `…/emc-surface-target-landscape.md` : 1429 (red-team row F01) | Records the corrected form: the "no vital-tissue signal" framing was the *finding*, and the correction is stated in the same row. |
| b10 | `…/emc-surface-target-landscape-si.md` : 104–117 | S3 quotes the declared rule and the 21-label vital list as declared. |
| b11 | `…/emc-surface-target-landscape-si.md` : 119–129 | "⚠ **The vital-tissue branch never operated on any record in this study.** … no expression level was ever inspected … not evidence of absence from a vital tissue, and not a therapeutic window". |
| b12 | `…/emc-surface-target-landscape-si.md` : 137–141 | The eight RESTRICTED labels and the DLL3 intersection are stated as a **stored-label** intersection, "not a demonstration that DLL3 is absent from normal tissue". |
| b13 | `…/emc-surface-target-landscape-si.md` : 299–303 (Table S2 caption) | "⚠ … null for all 45 classified records, so no row below reports a measured expression level, **no row establishes absence from a vital tissue**". Covers every Verdict cell in Table S2 (lines 308–342, e.g. CD276 at 329). |
| b14 | `…/emc-surface-target-landscape-si.md` : 350–357 | ALCAM note: RESTRICTED is stored "on a record whose quantitative fields are null"; the failed-validation framing is explicitly withdrawn. |
| b15 | `…/emc-surface-target-landscape-si.md` : 715–719 | "**No safety statement.** … Neither is a safety assessment, neither establishes a clean window or absence from any tissue". |
| b16 | `…/emc-surface-target-landscape-cover-letter.md` : 62–63 | Asserts no validated target, no safety, no therapeutic window claim; makes no filter claim at all. |
| b17 | `…/emc-surface-antigen-map-edits.json` : 77 | "⛔ HPA RNA is BULK NORMAL TISSUE and mRNA is not surface protein, so RESTRICTED is a window **PRIOR** and never a safety statement." |
| b18 | `…/emc-surface-antigen-map-edits.json` : 239 | "⛔_what_ALCAM_IS_NOT_YET": "Not tumour-restricted (RESTRICTED is a normal-tissue RNA prior, not a safety statement)." |
| b19 | `…/emc-surface-antigen-map-edits.json` : 241 | Names the exact gap: "`rna_tissue_specific_nTPM` is null for ALCAM, so WHICH normal tissue it is enriched in is not recorded, and that is precisely the field an on-target/off-tumour argument would need." |
| b20 | `…/emc-surface-antigen-map-edits.json` : 3, 109, 136, 155, 175–176, 195, 217, 237–238, 244 | Every per-gene `window`/`verdict` mention is reported as the stored HPA-window label, with 109 and 239 attached to ALCAM as the qualifying pair. Label-reporting, not exclusion-claiming. |
| b21 | `…/surface-targets-graph-records.json` : 135 ; `…/ofcs-cspg4-map-edits.json` : 42, 58 | CD56's failure is attributed to the **blood/immune** window specifically, which is the branch that did run; the intersection claims are scoped to stored labels and to their instrument limits. |

**Counts.** Category (a): **4 sites in 3 files.** Category (b): **21 sites**, spanning the entire
main manuscript and SI treatment of the screen, including both display-item captions.

## Ordering and prioritisation — checked separately, no hit

The paper's target ordering (Table 1, lines 925–950) is ordered by **enrichment (log2TPM)**, not by
normal-tissue verdict; the verdict is a reported column, captioned by b8. The one place a verdict
does gate a set — the "selective ∩ RESTRICTED" intersection yielding DLL3 — is stated as a
stored-label intersection at b12 and again in the body at lines 468–476. **No prioritisation
ordering in this family is computed from `vital_tissue`,** which is expected: `vital_tissue` is
empty on every row, so it can order nothing.
