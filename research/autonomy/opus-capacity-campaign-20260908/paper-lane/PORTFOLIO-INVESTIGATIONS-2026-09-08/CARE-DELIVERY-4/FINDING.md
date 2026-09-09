---
id: DOC-PORTFOLIO-INVESTIGATION-CARE-DELIVERY-4-2026-09-09
title: "The margin element re-derives digit for digit; the sentence that summarises it does not — 'no trial series prints a margin at all' quantifies over four trial series of which one was examined"
level: L4
kind: investigation
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# CARE-DELIVERY-4 — option (a): settling whether "no trial series prints a margin" is a claim about the papers or about the retrieval

> ⛔ Nothing here is medical advice and nothing here asserts efficacy, safety, selectivity, a
> therapeutic window or clinical readiness. No patient was studied; no wet-lab work exists. **No
> association between treatment setting, referral or excision planning and any outcome is stated or
> implied anywhere in this lane.**

## 0 · Which option, and why this one

**Option (a).** Options (b) and (c) were both live, and (b) is partly answered here as a by-product
(the two counts do re-derive — §2). (a) was chosen because it is the only one of the three whose
answer is a **falsifiable statement already written down**, and because settling it needs **no
retrieval at all**: every input is a committed artifact or an artifact an earlier lane already wrote.
Option (c) would have required new retrieval for most of the 14 series, which under this lane's
fences would have produced a partial extension and a longer residue rather than a settled question.
A question that can be closed for good beats a field that can only be half-filled.

## 1 · The question

CARE-DELIVERY-3 §7 records the margin element as **unchanged — four series REPORTED, three poolable
on the R0/R1/R2 scale — "because *no trial series prints a margin at all*."**
**Is the four-REPORTED / three-poolable structure still true across every series in the examined set,
and is "no trial series prints a margin" a bounded statement about what was retrieved or a claim
about the papers?**

## 2 · Re-derivation first — 16 numbers, all REPRODUCES

Before testing the sentence, every number it sits on was rebuilt from the matrix rows and the
committed registry artifacts rather than read off CARE-DELIVERY-3's summary blocks.
`build_margin_scope_audit.py`, `checks/01-build-margin-scope-audit/`, exit 0.

| claim | stated | re-derived | verdict |
|---|---|---|---|
| margin REPORTED — series / patients | 4 / 358 | 4 / 358 | **REPRODUCES** |
| margin EXAMINED_NOT_PRINTED — series / patients | 2 / 79 | 2 / 79 | **REPRODUCES** |
| margin NOT_EXAMINED — series / patients | 11 / 696 | 11 / 696 | **REPRODUCES** |
| all three bucket **membership sets** | — | identical | **REPRODUCES** |
| poolable R0/R1/R2 set | masunaga2025, chiusole2020, drilon2008 | same | **REPRODUCES** |
| masunaga2025 operated-with-a-margin | 156 | 117+30+9 = **156** | **REPRODUCES** |
| chiusole2020 margin-field denominator | 40 | `margin_field_available_for` = **40** | **REPRODUCES** |
| drilon2008 margin denominator | 43 | 24+12+7 = **43**, = printed denominator | **REPRODUCES** |
| `emc-surgical-quality.counts.series` | 2 | `len(series)` = **2** | **REPRODUCES** |
| `counts.operated_patients_with_a_margin_recorded` | 196 | 156 + 40 = **196** | **REPRODUCES** |
| margin examined set = the absence audit's six | 6 series | identical 6 | **REPRODUCES** |

**So the answer to the first half of the question is yes.** The margin element's structure holds
across the whole examined set: REPORTED (4) ∪ EXAMINED_NOT_PRINTED (2) is **exactly** the six-series
examined set the v3 absence audit uses — no series is examined for the absence claims but unexamined
for the margin, and none the other way. The three buckets partition all 17 candidate series and all
1,133 candidate patients. **Nothing in this lane changes a count.**

> Two things worth carrying from the re-derivation. **196 is not 358.** `counts.series` (2) and 196
> are correct *for the two-series artifact that carries them* and are **not** the margin element's
> denominators as the matrix now stands. And the poolable denominator — 156 + 40 + 43 = **239** — is
> stated by no committed artifact; it exists only inside the coverage matrix.
> A validator assertion that 239 appears nowhere in `emc-surgical-quality.json` **failed** on first
> run: `0.2239` contains the substring. Recorded in `checks/02-validate/` and corrected, because a
> substring test is not an arithmetic test.

## 3 · The scope test — the finding

"Trial series" was resolved **mechanically**, from each series' own `why_candidate` string in
`research/modalities/emc-ipd-survival.json`, quoted verbatim in the artifact. A series is
TRIAL_DESIGN only where its own committed description names a prospective phase study or a
randomised trial and names no retrospective/registry/institutional design. Nothing is inferred from
a drug name. All 17 classify cleanly; none lands in MIXED or NOT_STATED.

**Four of the 17 candidate series are trial-design:**

| series | n | its own `why_candidate`, verbatim | margin status in v3 |
|---|---|---|---|
| `stacchiotti2019pazopanib` | 26 | "the only **prospective** single-arm **phase 2** in advanced EMC; PFS is the primary endpoint" | **NOT_EXAMINED** |
| `immunosarc2emc2025` | 24 | "**phase 2** histology-specific cohort, sunitinib plus nivolumab" | **NOT_EXAMINED** |
| `martinbroto2020immunosarc1` | 68 | "single-arm **phase Ib/II**; EMC may appear only as a subgroup" | EXAMINED_NOT_PRINTED |
| `morioka2016trabectedin` | 5 | "sub-analysis of a **randomised trial**; EMC arm is tiny" | **NOT_EXAMINED** |

> ### Verdict: **a bounded statement about what was retrieved — not a claim about the papers.**
> **Of the four trial-design series, exactly one was examined for the margin element.** The other
> three were not. So the universal "no trial series prints a margin **at all**" is asserted over a
> set of four on the evidence of one.

Three further things sharpen it, and none of them required a retrieval:

1. **The sentence contradicts the artifact the same lane wrote.** `morioka2016trabectedin`'s margin
   cell in `care-delivery-element-coverage-v3.json` is `NOT_EXAMINED`, carrying v3's own note:
   *"⛔ This lane therefore asserts NO absence for this element. A retrieval limit is not a reporting
   absence."* The prose sentence asserts precisely the absence the cell refuses.
2. **One of the three series the prose calls "trial series" is not one.**
   `stacchiotti2013anthracycline` is described by `emc-ipd-survival.json` as a *"retrospective
   centrally-reviewed systemic-therapy series"*, and CARE-DELIVERY-3's own §4 heading calls it an
   Italian Rare Cancer Network series. Its margin verdict is sound and rests on a per-patient table
   returned in full; the **category label** attached to it is not. "Systemic-therapy series" is the
   label its evidence supports.
3. **The defect is confined to the prose.** The phrase appears in `CARE-DELIVERY-3/FINDING.md` and
   **not** in `care-delivery-element-coverage-v3.json` (asserted both ways in the validator). The
   machine-readable artifact never over-scopes: every unexamined trial series sits at NOT_EXAMINED.
   So the correction is a **sentence**, and **no value in any artifact changes**.

> ⭐ **Why this is worth a lane rather than a footnote.** PUB-CARE-DELIVERY's decisive finding was
> that `emc-surgical-quality.json`'s `recorded_in_any_reachable_series: false` is a universal
> quantifier over an examined set of two. **One lane later, the same shape reappeared in the prose
> that reports the fix** — while that lane's own JSON, its audit blocks and its `retrieval_completeness`
> field all got it right. The over-scoping is a habit of **language**, not of curation, and it
> survives exactly where the discipline of a schema does not reach.

**The sentence that the evidence supports**, and which the unapplied diff substitutes:
of the four trial-design series, one (`martinbroto2020immunosarc1`) was examined with its baseline
table returned in full and prints no margin; the other three were not examined for this element.
With `stacchiotti2013anthracycline` — a retrospective systemic-therapy series — that is **two
systemic-therapy reports examined and no margin printed in either**. **Whether any trial series
prints a margin is UNKNOWN.**

## 4 · Artifact · validation · provenance · limitations · stop condition

**Artifacts.**
`margin-element-scope-audit.json` — the 16-check re-derivation ledger, the design class of all 17
candidate series with each `why_candidate` string verbatim, and the scope test with its arithmetic.
Generated by `build_margin_scope_audit.py`.
`PROPOSED-UNAPPLIED-care-delivery-3-margin-scope.diff` — **UNAPPLIED**. It replaces the four-line
paragraph in CARE-DELIVERY-3 §7 that carries the over-scoped clause and nothing else. It **adds no
number and removes none**; the only numerals on added lines are `2`, `196`, `156`, `40` and `17`,
each already present in the paragraph it replaces or re-derived above. `git apply --check --verbose`
returns **0** — `checks/04-dryrun-diff/`. **Not applied**; CARE-DELIVERY-3 is another lane's
directory and this lane does not write there.

**Validation.** `validate_scope_audit.py` — **45/45 pass, exit 0** — `checks/03-validate-rerun/`, re-confirmed on the settled tree in
`checks/07-final-settled-revalidation-from-repo-root/`.
It re-hashes all four inputs against the hashes recorded in the artifact; proves `git status` is
empty over `research/modalities`, `systems`, `research/literature`, `research/data`,
`research/manuscripts`, `scripts` **and over all three parent lanes**; asserts every one of the 16
ledger verdicts is REPRODUCES and that no MISMATCH or NOT-RE-DERIVABLE string appears; proves the
margin buckets partition all 17 series and all 1,133 patients; re-derives 2, 196 and 156+40
independently of the artifact; proves every `why_candidate` string is byte-identical to
`emc-ipd-survival.json`; proves exactly four trial-design series, that `stacchiotti2013anthracycline`
is not one and `morioka2016trabectedin` is; proves 1 of 4 examined and 3 of 4 not; proves morioka's
v3 margin cell is NOT_EXAMINED; proves the phrase is in v3's FINDING.md and absent from v3's JSON;
proves the v1 → v2 → v3 margin history (REPORTED 2/230 → 4/358, unchanged v2→v3; EXAMINED_NOT_PRINTED
0 → 2; NOT_EXAMINED 13 → 11); and scans the artifact for clinical, pooling and digitisation wording.
A **second failed execution is preserved**: `checks/06-final-settled-revalidation/` exited **1**
because `git apply --check` was invoked with the working directory set to this lane, and git
resolves a diff's paths relative to the **current directory**, not the repository root — so it
looked for `CARE-DELIVERY-4/research/autonomy/.../CARE-DELIVERY-3/FINDING.md`. Re-run from the
repository root it exits **0** (`checks/07-final-settled-revalidation-from-repo-root/`: 45/45 pass,
diff still applies cleanly, still unapplied). The diff was never at fault and was not edited.

**A first validator run failed 4/43** and is preserved in `checks/02-validate/` (exit **1**). Three
of the four failures were **my assertions being wrong, not the artifact**: a miscounted ledger length
(17 vs 16); the `0.2239` substring above; and an over-strong claim that v2 and v3 have identical
margin `element_counts` — **they do not**, v3 moved two series from NOT_EXAMINED to
EXAMINED_NOT_PRINTED, which is a real reading and is now asserted as such in three separate checks.
The fourth was the fence scan hitting the word *efficacy* inside the artifact's own
not-medical-advice banner. No guard was weakened: the corrected assertions are strictly more
specific than the ones they replace.

**Provenance.** Repo `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`, working
tree read concurrently — no copy, no worktree. Inputs, with SHA-256 recorded in the artifact:
`CARE-DELIVERY-3/care-delivery-element-coverage-v3.json`, `CARE-DELIVERY-3/FINDING.md`,
`research/modalities/emc-ipd-survival.json`, `research/modalities/emc-surgical-quality.json`.
Also read, not modified: `CARE-DELIVERY-2/care-delivery-element-coverage-v2.json`,
`PUB-CARE-DELIVERY/care-delivery-element-coverage.json`, `systems/POLICY-evidence.md`.
**This lane performed NO retrieval of any kind** — no PubMed MCP call, no HTTP request, no MCP tool
call at all. No `git add`, `commit`, `push`, `preflight`, subagent, GPU, paid API, download,
publication act or outreach. Writes confined to this directory
(`checks/05-no-shared-state-written/`).

**Limitations.**
1. The design classification is a reading of **this repository's own one-line descriptions**, not of
   the papers. It is exactly as good as `emc-ipd-survival.json`'s `why_candidate` field, and it is
   recorded verbatim so a later session can overturn it by reading the papers.
2. "One trial series was examined for the margin element" is a statement about **CARE-DELIVERY-3's
   retrieval**, and even for that one, `martinbroto2020immunosarc1`'s supplementary appendix was not
   returned — so its EXAMINED_NOT_PRINTED verdict is not a claim about the appendix.
3. This lane **re-read no paper** and confirms no verdict against a source text. `masunaga2025`,
   `chiusole2020`, `bishop2019` and `drilon2008` remain trusted from the parent lanes.
4. The `retrieval_completeness` field exists on the **three** series CARE-DELIVERY-3 read and is
   `null` on `bishop2019` and `drilon2008` — the two CARE-DELIVERY-2 read. **Option (c)'s gap is not
   closed and is not narrowed here**; it is one row wider than the 14 the brief names, because two
   already-examined series also lack the field.
5. The margin element's REPORTED patient total (358) and its poolable total (239) are **sums over
   overlapping cohorts** (Milan/INT, US institutions) and, per CARE-DELIVERY-3 §6, over partly
   non-EMC denominators. They are accounting weights. ⛔ **Overlap is unknown and nothing is pooled.**
6. Nothing here bears on any clinical question, and the reporting-quality framing is not a criticism
   of any study's conclusions.

**Stop condition — reached.** The question was whether one written sentence is bounded or universal.
It is bounded, the arithmetic that shows it is 4 trial-design series against 1 examined, and the
correction is prepared as an unapplied diff. **This lane stops.** The only step that could turn the
UNKNOWN into a finding is retrieving `stacchiotti2019pazopanib` and `immunosarc2emc2025` — a
retrieval this lane did not attempt and does not propose as mandatory.

**Honest outcome.** Every number re-derives, digit for digit — the margin element is sound and
CARE-DELIVERY-3's structural claim about it holds across the whole examined set. The **summary
sentence** does not: it restates a bounded retrieval result as a universal about the literature, the
same defect this paper family was opened to correct, and it contradicts the same lane's own JSON.
Small, and worth having, because it is the second instance of one recurring failure mode.
⛔ This does **not** make `PUB-CARE-DELIVERY` writable — its publish decision is recorded "no" and
`BLK-NO-FIELD-ATTENTION-MEASUREMENT` is unresolved; neither is touched or reopened. **No diff from
any lane was applied**, including CARE-DELIVERY-3's (which supersedes and subsumes CARE-DELIVERY-2's,
and CARE-DELIVERY-2's must never be applied first).
