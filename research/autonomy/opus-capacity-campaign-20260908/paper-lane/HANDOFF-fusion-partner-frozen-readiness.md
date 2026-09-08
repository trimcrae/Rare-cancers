---
id: DOC-OPUS-CAMPAIGN-FROZEN-FUSION-PARTNER
title: "Frozen final-readiness handoff — fusion-variant stratification in EMC (EWSR1::NR4A3 vs TAF15::NR4A3)"
level: L4
kind: memo
status: live
purpose: >
  Hand the corrected fusion-partner prognosis manuscript to root's scientific acceptance with its
  exact frozen revision, its complete dependency list with digests, its source provenance, the checks
  that actually ran with their real scope, and every unresolved scientific and release gap.
scope: >
  L4. A readiness handoff. It edits no science, runs no producer for a receipt, opens no new source
  hunt, authorises no publication act, and asserts no green gate.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen handoff — `fusion-partner/emc-fusion-partner-stratification.md`

## 1 · Exact frozen revision, verified rather than assumed

- **Manuscript:** `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`,
  **82,557 bytes**, sha256
  `f850211474be5a298a662460f9713a8ea9fa446dc8a03addb955d967f56d184b`. Title: *Fusion-variant
  stratification in EMC (EWSR1::NR4A3 vs TAF15::NR4A3) — a partner-stratified pooled synthesis*.
  Front matter `id: DOC-EMC-FUSION-PARTNER-STRATIFICATION`, `level: L3`, `kind: manuscript`,
  `date: 2026-08-08`, `last_verified: 2026-08-08` — ⚠ the front matter's `last_verified` is a month
  older than the corrections landed below and was **not** refreshed by them.
- **Branch:** `claude/confident-bardeen-ji76cd`. **Last touched at `0f58b4ba`** ("Clear the last
  lint_claims ERROR by rewording, not by touching the guard", 2026-09-08).
- ⭐ **Checked, not forced.** The working-tree bytes of the manuscript, the artifact, the producer and
  the correction register each hash identically to the same paths at `HEAD`. The only modified file
  in the tree is `research/manuscripts/neoantigen/hla-coverage-emc.md`, which belongs to another
  writer and to a different package; it is untouched here.
- **The revision is a three-lane composite, and each lane is named** so nothing is credited to the
  wrong hand:
  | commit | date | what it moved |
  |---|---|---|
  | `e7a5a5d0` | 2026-09-08 | FP1's four applied prose fixes (with DG1/MV1/NA1 for other papers) |
  | `4d8fa9e3` | 2026-09-08 | PR2 stage 1 — the generator's narrative strings, five prose guards re-bound |
  | `94af5aa8` | 2026-09-08 | PR2 stage 2 — the unidentified-partner case is not partner-assigned |
  | `8c76f51b` | 2026-09-08 | PR2 stage 3 — non-overlap scoped as ARGUED; the missing Agaram follow-up field |
  | `56c9f985` | 2026-09-08 | the eight-verifier pass: FP1's D2, D3 and D4, previously deferred, landed in prose |
  | `0f58b4ba` | 2026-09-08 | one word, `treats` → `handles`, to clear a `lint_claims` false positive |
- **Publication record:** `systems/graph/publications.json` → `PUB-FUSION-PARTNER`, state **`drafted`**,
  target venue **`preprint`**, `outcome_potential: live_positive`, `patient_path: clinical_adoption`,
  `unit: full_paper`. It carries **no `blocked_by`**.

## 2 · Complete dependency list, with digests

"Complete" here means what the code actually imports and the inputs it actually reads, established by
reading `emc_fusion_partner_pooling.py`'s imports and path constants and each guard's path constants —
not by transcribing the links the manuscript prints. **Sixteen enumerable files, 810,080 bytes.**

| role | file | bytes | sha256 |
|---|---|---:|---|
| manuscript | `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` | 82,557 | `f850211474be5a29…f56d184b` |
| second prose document (guarded identically) | `research/manuscripts/fusion-partner/emc-fusion-partner-correction-register.md` | 50,781 | `c57f5658149e06f7…ea7251a9` |
| the one home of every number | `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | 113,953 | `f60c550c617fdc34…39cf6c53b` |
| producer | `research/manuscripts/emc_fusion_partner_pooling.py` | 141,313 | `7ba6f81a3ee8f8f2…c45ec9a9` |
| extraction companion (read by two guards) | `research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md` | 24,809 | `4c36b9b4f5bbfd8d…8bd7b56637` |
| foreign artifact bound by the prose guard | `research/modalities/gse28866-tumour-vs-normal.json` | 27,256 | `ac0a17bd81dd8bc2…49720be407` |
| binding evidence contract (method, cited not read) | `systems/POLICY-evidence.md` | 22,663 | `b971355b40bebfdc…503c2cd59` |
| prose↔artifact guard | `research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py` | 147,383 | `83e3f83665cc5b86…c5172df6d` |
| relations guard | `…/test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py` | 41,660 | `386c2926d90d7c1b…a1d79db93a` |
| author-year↔citation-map guard | `…/test_fusion_partner_author_years_are_bound_to_the_citation_map.py` | 14,989 | `a6b274940f2e9153…6bd8d3067` |
| gene-identifier attestation guard | `…/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` | 24,233 | `43d8f96b2bf00420…5c46a76c` |
| generator `--check` guard | `…/test_emc_fusion_partner_pooling_check.py` | 10,578 | `326c5d492b9afa95…a051cb9c` |
| the guards' own mutation harness | `…/mutate_fusion_partner_guard.py` | 54,876 | `a417529a5dd3a74b…5848b7bfb23` |
| lane companion, cited in artifact strings | `research/manuscripts/fusion-partner/lit-targets-partner-events.json` | 14,937 | `d19e26b5e76f808d…8cf0f79d1` |
| lane companion, cited in artifact strings | `research/manuscripts/fusion-partner/partner-strat-graph-records.json` | 29,605 | `854583dc11fe125b…6e1f3a595b` |
| lane companion, cited in artifact strings | `research/manuscripts/fusion-partner/emc-fusion-partner-map-edits.json` | 8,487 | `089523e3b11c9a64…943f27cdad5` |

**Two facts about that list that a link-transcription would have missed, and one it cannot enumerate:**

1. ⭐ **The producer reads no inputs at all.** Its imports are stdlib only — `argparse`, `json`, `math`,
   `os`, `sys`, `datetime` — and the only file paths in the module are `REPO` and `OUT`
   (`…/fusion-partner/emc-fusion-partner-pooling.json`), opened for reading in `--check` and for
   writing in `--write`. Every cohort count, every citation record and every source note is **typed
   into the module's own `COHORTS` and citation tables**. So the artifact's reproducibility rests on
   the module's text and on nothing else on disk: there is no upstream data file to refresh, and
   equally **no independent input against which the typed counts could be re-verified by machine**.
   That is a strength for determinism and a weakness for provenance, and §3 states it as both.
2. ⭐ **The prose guard binds a second, foreign artifact.** `gse28866-tumour-vs-normal.json` is not in
   `fusion-partner/` and is not the pooling artifact, but §3.6's SEMA3C fold-changes (1.8×, 1.7×,
   n = 4 EMC libraries) are read against it. A dependency list built from the manuscript's own §8
   links would have omitted it.
3. ⚠ **One guard's input set is a directory scan and is therefore NOT a fixed list.**
   `test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` attests every
   identifier-shaped token in the three prose documents against a corpus built by walking
   `research/modalities/`, `research/data/` and `research/literature/` for `.json`/`.csv`/`.jsonl`
   files under 8 MB. Measured on this revision that is **936 files, 123,040,796 bytes**. Those files
   are not dependencies of the *paper*; they are the attestation corpus of one *guard*, and the guard's
   result therefore moves if unrelated files are added or removed elsewhere in the repository. It is
   named here rather than folded into the table, because folding it in would be a false claim of a
   frozen dependency set.

⭐ **No essential file is missing.** Every path the producer and the five guards name resolves on disk
at the digests above; nothing had to be reconstructed, searched for or invented, and the pytest
`_required()` helpers — which fail rather than skip on an absent input — all passed.

## 3 · Source provenance and reproducibility, with its real weaknesses

- **The estimator is fixed by contract, not chosen.** `systems/POLICY-evidence.md` §1–§2 binds this
  synthesis to crude denominator-weighted proportions with **Wilson score 95 % intervals**,
  explicit-integer `{events, denom}` pairs only, non-overlapping populations only, and heterogeneity
  reported as the **range of per-cohort rates** with **I² deliberately not computed**. The artifact's
  `method` block records exactly that, and records the DerSimonian–Laird random-effects pooler in
  `research/meta/meta-analysis.mjs` under `not_used`, because the per-stratum denominators cannot
  support an estimable between-study variance.
- **Regeneration is deterministic and was exercised three times, by PR2, not by this handoff.** Each
  of `4d8fa9e3`, `94af5aa8` and `8c76f51b` ran the producer **once**, exit 0, and each was followed by
  a parent-computed leaf-by-leaf comparison against the committed artifact: **1142/1142 leaves, no key,
  type or list-length change**; run 3 records **all 521 numeric and all 52 boolean leaves equal**, with
  4 / 2 / 3 changed strings respectively (the regeneration timestamp plus the narrative fields under
  repair). `--check` returned OK, exit 0, after each. ⚠ **I am relaying those three receipts from the
  commit messages and `COLLECTION-d357-onward.md` §4; I did not re-run the producer**, and this
  handoff deliberately does not, because the task is packaging and a re-run would only produce a
  fourth timestamp.
- ⚠ **The primary sources are published papers read by a human-equivalent reader, and two of the
  decisive reads are PDF transcriptions.** Huang 2023's Table 1 (PMID 36948401) was read from the
  published PDF on 2026-08-08; the quoted sentence about large tumours was transcribed in the same
  read and carries the same provenance caveat, which the manuscript states at §4.7a. Two full texts
  that would settle the open questions are recorded as **genuinely closed and re-measured** rather
  than assumed — Stacchiotti 2019 (PMID 31331701) and Paioli 2021 (PMID 32572850) — with the
  measurement (Unpaywall, OpenAlex, named institutional repositories, one Anubis proof-of-work block
  recorded as UNREAD rather than empty) held in the artifact's provenance block and in
  `partner-event-counts-2026-08-08.md` §2.3. ⛔ **No new source hunt was opened here**, and those
  measurements are carried forward unchanged.
- ⚠ **There is no machine check that the typed counts match their sources.** `--check` closes the
  generator↔artifact loop and the five guards close the artifact↔prose loop. Nothing in this
  repository closes the **source↔generator** loop; that remains a human read, recorded in prose.
- ⛔ **No wet lab, no compute, no spend.** The manuscript's own banner reads "Preprint draft · no wet
  lab · no compute · $0". Nothing in this package establishes efficacy, safety, selectivity, a
  therapeutic window or clinical readiness for any agent, and the manuscript states in its own header
  block that no treatment recommendation is made or implied.

## 4 · The five quantities that must survive verbatim in meaning

Each was re-derived here from `emc-fusion-partner-pooling.json` and located in the current prose. None
is restated below as anything stronger than the page states it.

1. **73 = 23 + 50.** §3.3: *"The pooled outcome total is therefore 23 + 50, not 24 + 57."* Agaram 2014
   contributes **23 of its 24 partner-assigned** cases (the single TCF12 case is carried by no arm);
   Huang 2023 contributes **50** of the 53 followed. The artifact states the same in
   `analyses.B_outcome_by_partner.verdict`: *"TWO cohorts, 73 patients assigned to EWSR1::NR4A3 or
   TAF15::NR4A3 — Agaram 2014's 23 of 24 partner-assigned, for which the retained extraction carries
   no separate follow-up-count field, plus Huang 2023's 50 of the 53 followed."* ⚠ The Agaram clause is
   deliberately a statement **about this repository's extraction**, not about the primary publication —
   `cohorts[agaram-2014-outcome]` carries no `n_with_followup` key. Do not restate it as "the source
   reports no follow-up count".
2. **53 followed, including 3 other partners.** §3.2 and §4.7: of Huang's 58-case series, **53** have
   follow-up; the **50** entering the pooled table are those assigned to the two arms being contrasted,
   *"the other three being two TCF12 cases, which are partner-assigned but carried by no arm here, and
   one whose partner was not identified."* ⛔ The three are **not** uniformly "other partners" in the
   loose sense: two are partner-assigned (TCF12) and one is **unidentified**, which is not
   partner-assigned at all. `94af5aa8` exists precisely to keep those two categories apart; collapsing
   them re-creates the defect.
3. **154 as the partner-assigned denominator.** `analyses` prevalence pool: EWSR1::NR4A3 120/154
   (77.9 %, 70.7–83.7), **TAF15::NR4A3 28/154 = 18.2 % (12.9–25.0)**, TCF12::NR4A3 5/154 (3.2 %),
   TFG::NR4A3 1/154 (0.6 %). 120 + 28 + 5 + 1 = 154, from four series (Agaram 24 · Huang 57 · Lenz 11 ·
   Paioli 62). ⛔ **154 is the prevalence denominator and is not the outcome denominator.** The
   manuscript says so in §3.3 in as many words: *"The outcome denominator is narrower than the
   prevalence denominator of §3.5 and the two must not be read as the same population."* FP1's audit
   recorded as a **negative finding** that the expected denominator trap was *not* present here — the
   prevalence pool was already correctly partner-assigned in all six places.
4. **Non-overlap is ARGUED, not PROVED.** §5: *"Non-overlap of the two cohorts is argued from their
   reported institutions, author lists and geography (§3.2); no patient-level verification was
   performed, and a third series is held out because the same argument could not be made for it."* The
   artifact matches: *"two cohorts whose non-overlap is ARGUED from the reported authors, institutions
   and geography and is NOT patient-verified."* The held-out third series is Suemitsu 2025 (MSK, n = 18),
   excluded as `population-overlap-unresolved` against Agaram's MSKCC cohort — and reported rather than
   omitted because it also cuts toward the null.
5. **Common-binomial / Wilson versus the heterogeneity limits.** §4.2: *"every Wilson bound in §3.3 is
   computed on the summed counts, under a common-binomial approximation that handles the two cohorts'
   patients as one sample. Between-cohort variation therefore enters the point estimate through the
   denominator weights and enters the interval not at all, and no prediction-interval reading is
   available."* The same paragraph states that this is **not a meta-analysis**, that there is no
   random-effects model, no between-study variance, no I², no funnel plot and no formal heterogeneity
   test, that this is a decision recorded in §2.5 rather than an omission, and — importantly — that
   *"no two-study interval was computed, so nothing here establishes that these bounds are narrower
   than every valid one."* The **only** heterogeneity signal offered is the per-cohort range, and §3.3
   demonstrates why that matters: local recurrence **flips direction** between the two cohorts
   (Agaram 2/7 vs 1/16; Huang 2/8 vs 12/42), with a 22.4-point comparator-arm spread, so the pooled
   4.3-point gap *"is a cancellation of two cohorts that disagree, not a small effect they share."*

⛔ **And the headline never travels alone.** 7/15 = 46.7 % (24.8–69.9) against 6/58 = 10.3 % (4.8–20.8),
gap 36.3 points, Fisher two-sided p = 0.0034 — labelled in the artifact as **post-hoc descriptive only,
not prespecified, not performed in any source, not corrected for multiplicity, and not used to license
any claim** — and stated inseparably from its defeater: in Huang 2023's own multivariable model only
size > 10 cm (HR 30.60) and metastasis at presentation (HR 8.14) remain independent, and TAF15::NR4A3
loses significance under adjustment.

## 5 · Checks that actually ran, with their real exit codes and their real scope

Every row below was executed in this session on this revision. Exit codes are the observed ones.

| check | scope as actually implemented | result | exit |
|---|---|---|---|
| `python3 research/manuscripts/lint_style.py` (no args — the gate) | its own `TARGETS`, 15 files | 0 ERROR | **0** |
| `python3 research/manuscripts/lint_consistency.py` (no args — repo-wide) | see the scope note below | 0 ERROR | **0** |
| `python3 research/manuscripts/lint_claims.py <manuscript>` | this manuscript | 0 ERROR, **4 WARN** | **0** |
| `python3 research/manuscripts/lint_claims.py <correction register>` | the register | 0 ERROR, 2 WARN | **0** |
| `/root/.local/bin/pytest -q …test_fusion_partner_prose_matches_its_artifact.py` | the binding test named in the brief | **137 passed** | **0** |
| `/root/.local/bin/pytest -q` over all five fusion-partner modules | prose↔artifact, relations, author-years, identifiers, `--check` | **178 passed** | **0** |
| `python3 research/manuscripts/lint_style.py <manuscript>` (explicit path) | this file only — **NOT the gate** | **191 ERROR** | **1** |

**⚠ Scope, stated honestly rather than implied by a green line.**

- **`lint_style.py` does NOT cover this paper.** The gate's no-argument run reads only its own
  `TARGETS` list, and `emc-fusion-partner-stratification.md` is **not in it**. The gate's 0/15 above is
  therefore silent about this file, not a pass for it. The explicit-path run measures **191 ERROR**,
  dominated by register: **262 bold runs over 11,353 words = 23.1/1000 against a limit of 12.0**, and
  **110 em-dashes = 9.7/1000 against a limit of 6.0**, plus decorative-glyph and mid-sentence-bold
  findings. That is a measurement of repository register against journal register, and it is a
  **release** question (§7), not a failing gate and not a defect in the science. FP1 recorded 189
  before and after its edits; the count is now 191 on a manuscript two later commits have grown.
- **`lint_consistency.py` DOES cover this paper, and its own summary line understates that.** The
  printed *"0 ERROR across 29 target file(s)"* counts only `pinned-figures.json`'s `targets` list — the
  scope of the **superseded-marker** check — and this manuscript is **not** in those 29. But
  `check_artifact_figures()` iterates every registry entry's own `must_appear_in`, independent of
  `targets`, and **three pinned figures bind this manuscript**:
  | pin id | artifact key | what it pins |
  |---|---|---|
  | `fusion_partner_dod_fisher_p` | `analyses.B_outcome_by_partner.disease_specific_death.fisher_exact_two_sided_p` | Fisher p = 0.0034 |
  | `fusion_partner_dod_taf15_percent` | `…disease_specific_death.taf15_arm.percent` | 7/15 = 46.7 % |
  | `fusion_partner_dod_comparator_percent` | `…disease_specific_death.comparator_arm.percent` | 6/58 = 10.3 % |
  So the repo-wide `lint_consistency` run **is** a real pass for those three quantities in this file.
  It is **not** a pass for anything else in the file.
- **`lint_claims` exits 0 with WARNs, and the WARNs are not nothing.** Four `R4-confirms` warnings on
  `validate` / `confirmed` / `confirmation` at lines 165, 591, 661 and 835. Read in context, three are
  descriptions of other people's methods ("molecularly confirmed", "FISH-confirmation series") and one
  describes the repository's own CI. They are recorded, not silently absorbed.
- **Not run here, and named rather than implied:** `scripts/preflight.sh` (normal or
  `PREFLIGHT_FULL=1`), `lint_citations.py`, `claim_ablation.py`, the mutation harness
  `mutate_fusion_partner_guard.py`, and `publish_bar.py`. ⚠ `COLLECTION-d357-onward.md` carries two
  standing repo-wide facts unchanged: **`lint_citations` still fails repo-wide, pre-existing and
  untouched**, and `lint_claims` repo-wide now reports **0 ERROR / 183 WARN across 137 files** after
  `0f58b4ba`. Neither was re-measured here.
- ⛔ **No test was skipped, xfailed or deselected to reach any number above.** 137 and 178 are passes,
  and 191 is a failure reported as a failure.

## 6 · Prior dispositions — what FP1 and PR2 found, what was accepted, what was left open

**FP1** (paper lane, `FP1-executed-artifacts/`, 29/29 observed tool pairs, transcript retained and
`cmp`-verified; adjudicated in `COLLECTION-DG1-MV1-FP1-NA1-adjudication.md`). 62 quantities
dispositioned: **59 MATCH, 2 MISMATCH, 1 NO SOURCE LOCATED**.

- **Negative finding, recorded because it is one:** the expected denominator trap was **not** present
  in the prevalence pool — 24/57/11/62 = 154, correctly labelled partner-assigned in all six places,
  with the 2/1/1/5 residues stated.
- **Three findings the parent re-derived and confirmed:** the *outcome* pool was mislabelled
  "partner-assigned"; `cohorts[agaram-2014-outcome]` carries **no `n_with_followup` field at all**, so
  "23 partner-assigned with follow-up" was two errors in one phrase; and Huang's 50 is neither
  partner-assigned nor simply "with follow-up".
- **Applied, four** (`e7a5a5d0`): §3.2's two rows, §3.3's pooled-cohort paragraph and §4.7's
  self-contradicting sentence.
- **Deferred at the time, and since closed:** FP1's **D2** (§5 stating non-overlap as established),
  **D3** (the two different 58s) and **D4** (what a Wilson interval on summed counts assumes) were
  judged sound but editorial and referred to the paper's owner. All three are now **in the prose**,
  landed at `56c9f985` — §5's "argued … no patient-level verification", §3.3's *"Note on the two 58s"*,
  and §4.2's common-binomial paragraph. ⭐ Verified by `git log -S` on each phrase, not assumed.
- **Left open at the time:** FP1 noted the same wrong wording lived in the generator and the artifact,
  a `COHORTS`-table change requiring regeneration, *"not attempted here"*, with the prose half landed
  knowing the artifact still carried the old phrasing. **PR2 closed exactly that.**

**PR2** (coordinator's separate producer-repair lane; commits `4d8fa9e3`, `94af5aa8`, `8c76f51b`). Three
producer runs, each once, each exit 0, each followed by an independent leaf comparison (§3). It
repaired `counts_read_from`, the PMID 36948401 assertion message, `what_changed_2026_08_08` and the
analysis-B verdict; made every integer they print **derived** rather than typed (a new
`_assigned_with_counts` helper); re-bound five prose guards, three of which now capture **more**
quantities than before, with **no regex loosened, no group made optional and no literal dropped**;
then corrected its own new label error (the unidentified case is not partner-assigned) and scoped
both the non-overlap claim and the Agaram follow-up statement. Guard baseline before PR2 was a
measured **5 failed / 132 passed**; after, **146 passed, exit 0**.

**`0f58b4ba`, recorded because the alternative was the tempting move.** `lint_claims`' R2
treatment-verb rule fired on §4.2's verb in *"a common-binomial approximation that … the two
cohorts' patients as one sample"* — the statistical sense of that verb, a false positive, and the
single ERROR standing between the repository and a clean run. The fix was **one word of prose**: the
verb the rule matched became **handles**. ⛔ **The guard was not weakened and its pattern was not
narrowed to exclude the usage.** Every hedge in the paragraph is intact.
⚠ The same rule fires on any document that quotes the retired verb, this handoff included, which is
why §4 item 5 and this paragraph both paraphrase it rather than reprint it.

## 7 · Unresolved gaps

### Scientific — owned by root

1. ⛔ **Blind review has not converged, and no seat covers this revision.**
   `research/autonomy/hardening-state/PUB-FUSION-PARTNER.json` is pinned to `reviewed_commit`
   `9d5b4def…`, **round 11**, `converged: false`, **9 distinct blockers and 25 P1 instances** across 4
   of 5 seats, and its own note says *"Round 12 (apply) required, then a re-pin and re-seat."* The
   newest seat record in `research/autonomy/review-seats/` is 2026-08-29T13:10Z; **no blind-seat record
   exists for `e7a5a5d0`, `56c9f985` or `0f58b4ba`**. Since the publish bar's clause 1 grades the
   commit to be posted against seats covering that sha, this revision has **no clause-1 evidence at
   all** — a missing measurement, which is unknown and not a pass.
2. ⛔ **At least two round-11 blockers are still open in the frozen text. I verified these two myself.**
   - **CITE-B-1.** Reference [10] (line 943) prints *Hum Pathol* **2023;132:88–97** for Lenz 2023.
     `research/manuscripts/surface-targets/emc-surface-target-landscape.md:669` carries
     **2023;134:19–29** for the same PMID 36563884 and the same DOI. This is one fact in two places
     with the manuscript holding the copy the seat measured as resolving to nothing. ⛔ **Not fixed
     here** — a reference-list correction is an edit to the paper's science-facing text and this is a
     packaging task; it is named exactly, with both locations, so the owner can close it in one move.
   - **REF-B-1.** The unqualified historical superlative survives at **line 75** (Abstract: *"That is
     the first magnitude this contrast has ever had"*) and **line 347** (§3.3). The seat's objection
     stands on the paper's own §2.3a, which concedes no database query, no registered search string,
     no screening flow and no second reader.
   - ⚠ **The remaining seven round-11 findings (REF-B-2, REF-B-3, REG-B-1, REG-B-2, STAT-B-1, STAT-B-2,
     STAT-B-3) I did NOT re-verify line by line.** They are relayed as recorded and remain unclosed;
     treat this as an unmeasured surface, not as a clean one.
3. **The prognostic magnitude is crude and confounded, by the paper's own statement.** Not adjusted for
   size, stage, era, treatment or grade; the larger cohort's own multivariable model defeats the
   partner; nuclear pleomorphism is tested by partner nowhere; chemotherapy allocation by partner is
   published by neither cohort. §4.1 says the partner *"may be standing in for grade or for treatment
   as readily as for size, and this record cannot separate the three."*
4. **Both outcome cohorts are consultation material, not population samples** (§4.6): a tertiary
   referral centre that is also the prevalence high outlier, and a fifteen-institution FISH-confirmation
   series. Both biases inflate the arm carrying the headline.
5. **Non-overlap is argued, never verified** (§4 above), and a third MSK series is held out because the
   argument could not be made for it.
6. **Two decisive full texts remain genuinely closed** (Stacchiotti 2019, Paioli 2021), re-measured
   2026-08-08 rather than assumed. They carry the fusion distribution, the prior-therapy table and the
   per-partner event counts that would close the overlap and composition questions. ⛔ **Not re-fetched
   here, and deliberately not re-hunted.**
7. **The treatment-response arm has a direction and no magnitude.** Worst case the world's entire
   TAF15 antiangiogenic experience is three patients; a zero-event arm yields no magnitude at any
   denominator. Nothing in the prognostic result bears on it.
8. ⛔ **No efficacy, safety, selectivity or clinical-readiness claim is made, and none is available from
   this package.** There is no wet lab.

### Release — owned by the author

9. ⚠ **Register.** 191 explicit-path `lint_style` errors, dominated by bold and em-dash density, and
   the file is **outside the gate's TARGETS**. A journal-register conversion is an owner decision and
   an authorship act, deliberately not made here.
10. ⚠ **Gate coverage is partial and now stated precisely.** `lint_style`: **not covered**.
    `lint_consistency`: **covered for three pinned figures only**, via `must_appear_in`, not via the
    29-target list. `pinned-figures.json`: **three pins bind this manuscript** and nothing else in it.
11. ⛔ **No `scripts/preflight.sh` receipt and no `PREFLIGHT_FULL=1` receipt exists for this revision.**
12. ⚠ **The front matter's `last_verified: 2026-08-08` predates every correction in §1**, and the
    **correction register carries no row for the 2026-09-08 FP1/PR2/verifier edits** (it was last
    touched at `14a3f172`, 2026-09-04). No pinned quantity moved, so no `pinned-figures.json`
    correction record was owed; the register gap is nonetheless a divergence between the paper and its
    own correction record, and it is the owner's call whether it matters.
13. **Publication authority.** `research/autonomy/publication-authority.json` gives aiXiv a standing
    scoped grant over *"ANY publication endpoint passing all clauses"* except `excluded_papers`, which
    lists only PUB-ASO. **PUB-FUSION-PARTNER is not excluded — and it does not pass clause 1** (gap 1).
    ⛔ This handoff is not a publication act and requests none.
14. ⚠ **Campaign evidence retention (CLAUDE.md §8).** `FP1-executed-artifacts/` is intact on disk —
    `BEFORE`/`AFTER` manuscripts, `applied-fixes.diff`, and the original child transcript
    `ORIGINAL-CHILD-TRANSCRIPT-a81e800ea32b54de9.jsonl` (437,485 bytes). **No collection receipt naming
    that exact directory was found** in the campaign tree, so it stays intact. PR2's sandbox
    `/tmp/claude-0/pr2-lane` (65 MB, present) is explicitly **unclaimed** by
    `collected/README-small-originals-20260908.md`, which names it as deliberately not shipped and
    remaining in place. ⛔ Nothing here authorises deleting either. Volume headroom is 19 GiB used of
    252 GiB, 51 % — no disk-floor problem exists.

## 8 · What this handoff is not

⛔ It is not publication permission, not a review, not a selection memo, and not a claim that any gate is
green. No producer was re-run for it, no source hunt was opened, no guard, gate, pin or test was edited,
and no readiness claim is forced: **blind review has not converged on this revision and at least two
round-11 blockers are demonstrably still in the text.** Root owns scientific acceptance and the
independent review that clause 1 requires.
