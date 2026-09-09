---
id: DOC-FOLLOWTHROUGH-DISCOVERY-PROPOSALS-20260909
title: "FOLLOWTHROUGH-DISCOVERY — ten ready-to-execute next tasks built from returned campaign evidence"
level: L4
kind: proposal-set
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: FOLLOWTHROUGH-DISCOVERY
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# FOLLOWTHROUGH-DISCOVERY — ranked next tasks

**Ten proposals. Eleven candidates discarded** (§Discards) — all for a real reason: a closed or
proxy-refused route, a missing local dependency, an already-answered question, or a fence.

Nothing here is a publication act, an outreach act, a manuscript-admission act or a shared-state
edit. Every proposal writes only to its own new lane directory and, where a shared file should
change, emits an **unapplied** diff. ⛔ No wet lab. ⛔ No EMC efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim is available from any of this. No GPU, no paid API,
no download larger than what is already in the checkout. `MF1` and `P-ST` do not appear.

Locator existence and sha256 for every named input are recorded in `checks/01-locator-existence/`,
`checks/02-nr4a3-frames/` and `checks/03-discard-and-env-evidence/` (all exit 0).
**`checks/04-all-named-locators/` re-verifies every `path` named in `proposals.json` after writing
it: 45 entries, 0 missing, all 10 declared sha256 values MATCH, exit 0.** Repo HEAD at proposal time:
`04a4e0ef3078fca4259109ed376efdc60bca3aaa`.

## ⚠ Reconciliation with lanes that started while this survey ran — READ FIRST

`checks/05-inflight-lane-reconciliation` (exit 0) discovered a **third round already in flight**
that did not exist when this lane's survey began. It occupies part of this list. Applying the
task's own rule — *a stale prospect is not an untested one* — to my own proposals:

| Proposal | Status after reconciliation | Evidence |
|---|---|---|
| **P2 DEGRADER-RSA** | **SUPERSEDED — do not dispatch.** Lane `../DEGRADER-2/` already holds `per_frame_rsa_overlap.py` and `artifacts/per-frame-rsa-overlap.json`. | `checks/05` |
| **P3 IPD-SURVIVAL-3** | **SUPERSEDED — do not dispatch.** Lane `../IPD-SURVIVAL-3/` already holds `preserve-mark-y0-y1.diff`, `proximity-clause-rederivation.json` and the regenerated census. Same task, same artifacts, already executed. | `checks/05` |
| **P5 zero-partner filter** | **LIVE, but rename the lane** — `NEOANTIGEN-5` is taken by a *different* task (the guard's EWSR1 accession defect plus a failing-then-passing test). Dispatch as `NEOANTIGEN-6`. Its inputs are unaffected; the interaction to check is now with `../NEOANTIGEN-5/UNAPPLIED-01`/`-02` diffs, not NEOANTIGEN-4's. | `checks/05` |
| **P7 EWSR1::FLI1 discrepancy** | **AT RISK of duplication.** `../VACCINE-PATH-2/b1-exemplar-admissibility.json` is working the §B1 exemplar admissibility question through PubMed/PMC on the manuscript's own citations. Read that lane's output before dispatching; if it resolves the citation, P7 is spent. | `checks/05` |
| **P8 TXN-DEPENDENCY** | **LIVE, with a correction to its locator.** `research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md` is **modified in the working tree** (87 insertions, 19 deletions, uncommitted), as is `research/manuscripts/citation-provenance-ledger.json`. The sha256 recorded for it is therefore of the **dirty working tree**, not of a commit. Whoever runs P8 must re-hash at dispatch and say which version was read. | `checks/05` |
| P1, P4, P6, P9, P10 | **LIVE, no in-flight overlap found.** Lanes `BIOMARKER-DEP-3`, `HLA-COVERAGE-3`, `MATRIX-ADDRESS-3`, `SYNLETH-2` are on other questions (rest-arm denominators, staleness map, relaxed-k label recovery, breakdown denominator). | `checks/05` |

Net: **eight dispatchable proposals**, of which P1 is unchanged at rank 1.

## Ranking rationale

Ranked by **information gained per bounded run**, then scientific merit, then independence.
Proposals 1–3 change a load-bearing quantity or convert a published bound into an exact number:
they are the only ones whose result could alter what a paper is entitled to say. 4–5 are exact
sensitivity/repair work on a decision quantity, valuable but bounded to sharpening a number that is
already reported. 6–7 add genuinely new primary evidence through the admitted PubMed/PMC route and
are cheap, but each can plausibly return "not retrievable". 8–9 open evidence surfaces the campaign
has never touched (two of the 33 endpoints have no lane at all), so their expected information is
high but their variance is too — they can return "everything re-derives". 10 is consolidation: it
creates a reusable object rather than a new fact, and it is last for that reason.

---

## P1 — Composition-adjusted EMC expression contrast (rank 1)

**1 · Question and what is new.** KINASE-2 (`../KINASE-2/FINDING.md` §8.1) proved the 65.2 %
two-platform concordance is a real shared EMC contrast rather than inter-series correlation, and
left one sharply defined open alternative: **is the broad EMC contrast tumour/stroma composition, or
EMC biology?** No lane has tested it. New versus KINASE-2: that lane computed nulls under label
permutation and gene resampling; it did **not** adjust for or stratify on sample composition.

**2 · Inputs, already held.** `research/modalities/emc-expression-panels.json`
sha256 `59bccb553148c7100172456835957434b1349d701d4e0504e632a367c62a7f8d` — verified to carry
`gene_reads` (479 genes) with **per-sample** `z_vs_array` and `class` labels for both series, and
`signature_member_reads` with a 42-GSM × gene z matrix. Composition markers confirmed present:
PTPRC, CD68, CD3E, COL1A1, COL1A2, COL3A1, DCN, LUM, ACTA2, PECAM1, VWF, FN1, THY1, POSTN, MS4A1,
CD8A, HLA-DRA, B2M, FAP, PDGFRB, MKI67, EPCAM (22/25 probed). Scripts to reuse read-only:
`../KINASE-2/label_permutation_null.py`, `../KINASE-2/reproduce_lane1_check.py`.

**3 · One artifact.** `composition-adjusted-contrast.json` — per lead gene and per frame: the
unadjusted statistic, the composition score, the composition-adjusted statistic (rank-based partial
association), and the attenuation, with the pre-declared marker list frozen before any statistic is
read.

**4 · Ownership / dependencies.** New lane `EXPR-COMPOSITION`. Reads KINASE-2 read-only. **No write
conflict** — KINASE-2 is complete and nothing outside the new directory is written.

**5 · Smallest validation, and stop.** Known answer first: recompute KINASE-2's observed statistics
and require **0 mismatches** before any adjustment is computed; abort at exit 2 if they do not
reproduce. Negative control: a permuted composition score must not attenuate. Pre-register the
marker list and the seed in the lane before running. **Stop** when the adjusted statistic and its
null are computed on the primary and secondary frames, or immediately on a reproduction failure —
whichever comes first. Composition attenuation is a statement about *this contrast*, never about
efficacy or a target.

**Compute/storage.** Pure stdlib + numpy, one 13 MB JSON read, < 2 min CPU, < 5 MB written.

---

## P2 — Per-frame Shrake–Rupley RSA export for the paralogue exposure ceiling (rank 2)

**1 · Question and what is new.** `../PUB-DEGRADER/FINDING.md` §6 names it exactly: the committed
artifact publishes **quantile summaries, not per-frame RSA**, so the paralogue ceiling
(RSA ≤ 0.2126) and C397's margin can only be bounded, and the worst-case cross-replica p10 margin
(−0.014) cannot be turned into an overlap fraction. New: an **exact per-frame distribution**
replacing a coarse p10-over-25-frames reading, at $0 CPU, from conformers already on disk.

**2 · Inputs, already held.** `research/modalities/nr4a-paralogue-dynamics.json` sha256
`c3b7eaf38124177a2aa23d80135f7b5c8d96ffe70519234a878a0ed178523d4c` (its `ensemble_census` block
names the roots and the 75 unbiased frames/species). Conformers, existence verified:
`results/nr4a1-pocket-ensemble/release_rep{0,1,2}` (75 `frame.pdb`),
`results/nr4a2-pocket-ensemble/release_rep{0,1,2}` (75), `results/nr4a3-pocket-reharmonize/`
(100 frames, of which the three `release_rep*` are the 75 unbiased ones; `metad` excluded, as the
committed artifact excludes it). SASA engine: `Bio.PDB.SASA.ShrakeRupley` — **verified importable**
in this environment (`checks/01`).

**3 · One artifact.** `per-frame-rsa.json` — RSA per cysteine per frame per replica per species,
plus the exact overlap fraction of C397's frames above/below each paralogue frame's RSA, and a
replica-level confidence statement.

**4 · Ownership / dependencies.** New lane `DEGRADER-RSA`. Reads PUB-DEGRADER read-only; the
conformer trees are read in place, **not copied** (headroom fence). No write conflict.

**5 · Smallest validation, and stop.** Known-answer baseline: the per-frame values must reproduce
the committed artifact's published quantile summaries (the ceiling 0.2126 and each replica p10) to
the artifact's own precision; a mismatch indicts the re-implementation and the lane must report the
mismatch, not the new numbers. **Stop** when all 225 unbiased frames are scored and the reproduction
either holds or fails. ⛔ RSA is geometry: nothing about pKa, adduct stability, selectivity in cells,
efficacy or a therapeutic window follows, and the `STOP_NO_REFERENCE` covalent-ligandability
dependency is untouched.

**Compute/storage.** ~225 PDB frames × ShrakeRupley; estimated 3–8 min CPU single core; artifact
< 10 MB. No network.

---

## P3 — Make the KM proximity clause re-derivable (`y0`/`y1` in `Token.as_dict`) (rank 3)

**1 · Question and what is new.** `../IPD-SURVIVAL-2/FINDING.md` §6.2: one `absent` verdict in the
numbers-at-risk census rests **solely** on a proximity clause that cannot be re-derived from the
preserved intermediates, because `Token.as_dict` drops `y0`/`y1`. IPD-SURVIVAL-2 also established
the thing that makes this runnable: the census **is** repeatable at this HEAD and reproduces byte
for byte — `origin/literature-cache` exists here (`216bd1b5fb25a56b90ef3cc2373e1fe68322708f`,
verified in `checks/01`), contradicting the standing "not runnable at this HEAD" record. New: turn
the one non-re-derivable verdict into a re-derivable one.

**2 · Inputs, already held.** `research/modalities/km_risk_row_detect.py` sha256
`71ed29b707233bffb2736e89da5989e37e83758b2b81f3b6716fe9a2a80b3749`; the PDFs on
`origin/literature-cache` (licence-uncommitted, read in place by the same path IPD-SURVIVAL-2 used);
`../IPD-SURVIVAL-2/census-reproduced-2026-09-09.json` and `census_rederive.py` as the comparison
baseline.

**3 · One artifact.** `UNAPPLIED-token-y-coordinates.diff` (additive: `y0`/`y1` added to
`Token.as_dict`, nothing removed) **plus** `proximity-clause-rederivation.json` showing the clause
recomputed from the emitted coordinates and agreeing with the recorded verdict.

**4 · Ownership / dependencies.** New lane `IPD-SURVIVAL-3`. The producer is a shared file —
therefore **unapplied diff only**; the re-run is done on a lane-local copy. Reads IPD-SURVIVAL-2
read-only. No write conflict. The correction to `reports/W65-km-risk-row-instrument-audit.md` that
IPD-SURVIVAL-2 identified is **another lane's report**: propose it as a second unapplied diff, do
not apply it.

**5 · Smallest validation, and stop.** Every field of the regenerated census must be identical to
the committed/reproduced census **except** the added keys — a diff of anything else is a failure and
must be reported as such. **Stop** when the proximity clause either re-derives to the recorded
verdict or provably does not; do not re-adjudicate any figure. ⛔ Never weaken the detector, its
thresholds or any verdict rule; the diff is additive only.

**Compute/storage.** One census re-execution (IPD-SURVIVAL-2 measured this as feasible in-lane);
< 10 min, pdf parser warnings expected and must be preserved in `stderr.txt`.

---

## P4 — Clash-cutoff sweep of the experimental NR4A2 competitor closure (rank 4)

**1 · Question and what is new.** `../MONOVALENT-2/FINDING.md` next-work item 2. MONOVALENT-2
recomputed the corridor closure under ten **experimental** NR4A2 chains at the primary cutoff only;
the closure survived but the C534 residue attribution softened to a 20–36 range. Open: **is the
surviving closure a structural fact or a clash-rule artifact?** New: the same substitution repeated
across the cutoff sweep the engine already implements.

**2 · Inputs, already held.** `research/modalities/nr4a3_linker_covalent_reach.py` sha256
`25e3949d215890736fff45aafc80cf315aefeb350c90b3e34b41889c2ca533ff` — **verified** to define
`CLASH_SWEEP_A = (2.0, 2.6, 3.0, 3.4)` and to thread `cutoffs` through `reach_one_frame`, so no rule
is changed, only reported. `research/modalities/nr4a3-linker-covalent-reach.json` sha256
`d5ebc0a3db8d4cf2a9e8ea3827c02e4681fb733fbd9e3bb15f1bd7b6555e3320`;
`../MONOVALENT-2/nr4a2_experimental_competitor_reach.py` (reused unmodified, parameterised on
cutoff); structures `research/modalities/_s4_lane_inputs/{1OVL,7WNH}.pdb.gz` and
`results/nr4a3-matrix/{nr4a3,nr4a2}-opened.pdb` (existence verified).

**3 · One artifact.** `cutoff-sweep-closure.json` — the per-cell closure decision at each of the
four cutoffs under each of the ten experimental chains, with the corridor tally at each cutoff and
the cutoff at which any decision flips.

**4 · Ownership / dependencies.** New lane `MONOVALENT-3`. Reads MONOVALENT-2 read-only. No write
conflict. ⛔ NR4A1 stays out of scope — it needs a structure fetch nobody here is authorised for, and
MONOVALENT-2's refusal to substitute a model for it stands.

**5 · Smallest validation, and stop.** MONOVALENT-2's own gate is the known-answer test and must be
kept: **300/300 committed modelled competitor atom counts reproduced, hard exit 2 otherwise**,
before any experimental chain is read. Additional control: at the primary cutoff the sweep must
return MONOVALENT-2's published 34/8/18-of-60 tally exactly. **Stop** when all four cutoffs × ten
chains are decided, or on the reproduction gate firing.

**Compute/storage.** Same engine MONOVALENT-2 ran; ~4× its runtime; single core, minutes,
artifact < 5 MB.

---

## P5 — Zero-partner discriminator as an explicit, separately reported filter (rank 5)

**1 · Question and what is new.** `../NEOANTIGEN-4/FINDING.md` §8.1 measured it: **8 of 174**
junction peptides and **2 of 11** ranked binders (including rank 1) carry **zero** residues from one
parent, so they are not junction-specific. New versus NEOANTIGEN-4: that lane *measured* the
proportion and fixed the novelty guard's parent accession; it did **not** produce the re-emitted
panel that applying the discriminator would give.

**2 · Inputs, already held.** `research/modalities/fusion_breakpoints.py` sha256
`e9a2f4fcc10f626c0faa038555f444d5a9f3ebabab62305ab699b7e6f45ca626`;
`research/modalities/junction-proteome-novelty.json` sha256
`ff1ccc2c247eccb7963ee307d49ba50b048d238a1f280ef7c42e8546d165914a`;
`../NEOANTIGEN-4/neoantigen4-novelty-audit.json` (the per-peptide parent-residue split);
`../NEOANTIGEN-4/UNAPPLIED-junction_proteome_novelty-parent-accession.diff`.

**3 · One artifact.** `UNAPPLIED-zero-partner-filter.diff` plus `refiltered-panel.json` — the panel
re-emitted with the filter applied on a lane-local copy, with **both** the pre- and post-filter
ranks retained side by side so the filter is auditable and never silent.

**4 · Ownership / dependencies.** New lane `NEOANTIGEN-5`. `fusion_breakpoints.py` is shared →
**unapplied diff only**. Interaction to state explicitly: NEOANTIGEN-4's `PARENTS` diff also targets
the neoantigen family — check whether the two apply independently and, if not, emit a rebased
version (REPURPOSING-3 hit exactly this and the rebase is the accepted handling).

**5 · Smallest validation, and stop.** The existing repository tests for the audited scripts must be
run **unmodified** and stay green (NEOANTIGEN-4 ran 9 and used them as its baseline); the filter may
only ever *remove* candidates, never add or re-rank upward, and that must be asserted. Positive
control: `DMPCVQAQY` (zero EWSR1 residues, recorded in NR4A3 isoform Q92570-3) must be removed.
**Stop** at the re-emitted panel plus the diff. ⛔ This changes a **screen**, not a presentation or
immunogenicity claim, and no guard, matcher or test is weakened.

**Compute/storage.** Stdlib, seconds, < 5 MB.

---

## P6 — Take the RT local-control ledger from k = 2 to k = 3 (rank 6)

**1 · Question and what is new.** `../LOCOREGIONAL-2/FINDING.md` §6 next-work: identify the
**unidentified multicenter reference behind 1/10 vs 7/17** and read that primary directly, and
re-verify `bishop2019`'s 1/33 and 4/8 at source so both transcriptions become first-hand.
LOCOREGIONAL-2 moved k from 1 to 2 by exactly this move on `masunaga2025`; nobody has attempted the
third.

**2 · Inputs.** Held: `../LOCOREGIONAL-2/rt-local-control-contrast-ledger-k2.json` and
`rt_contrast_ledger_k2.py` (which has a `--check` byte-identity path); `research/modalities/
emc_locoregional_eligibility.py` (the shared Wilson closed form, z = 1.959963984540054, reused
unmodified). **New source, admitted route:** PubMed/PMC via `mcp__PubMed__search_articles`,
`lookup_article_by_citation`, `convert_article_ids`, `get_full_text_article` — used to resolve the
multicenter citation and to re-read `bishop2019` (DOI 10.1097/COC.0000000000000590) at source.
⛔ No direct HTTP (CONNECT 403 / curl exit 56); B9 (PMID 22592656) stays closed and is not a target.

**3 · One artifact.** `rt-local-control-contrast-ledger-k3.json` — the k = 2 ledger extended, or
explicitly **not** extended with the reason recorded per candidate.

**4 · Ownership / dependencies.** New lane `LOCOREGIONAL-3`. Reads LOCOREGIONAL-2 read-only. No
write conflict.

**5 · Smallest validation, and stop.** `--check` must re-derive the k = 2 rows **byte for byte**
before any new row is added; the four internal arithmetic consistency checks must stay ✅. **Stop**
as soon as the multicenter reference is either identified and read, or shown unresolvable through
the admitted route — a not-found is the result, recorded, not padded. ⛔ RT-RT-INTENSIFY stays
REFUTED and RT-METASTASECTOMY stays DO-NOT-WRITE; sizes only, no pooled effect estimate.

**Compute/storage.** A handful of MCP calls; negligible CPU; artifact < 1 MB. Every retrieval
attempt, including empty bodies, preserved under `checks/`.

---

## P7 — Resolve the EWSR1::FLI1 validated-epitope discrepancy (rank 7)

**1 · Question and what is new.** Two lanes stopped on the same unresolved item:
`../EPITOPE-BENCHMARK/FINDING.md` §8.2 and `../NEOANTIGEN-3/FINDING.md` §8.3 — a §B1 EWSR1::FLI1
record that PubMed term mapping did not surface, leaving the validated-epitope census's 34-vs-37
adjudication (`../EPITOPE-BENCHMARK/PARENT-ADJUDICATION-34-vs-37.md`) resting on an unread citation.
New: read the manuscript's **own cited primary directly** rather than re-searching by term.

**2 · Inputs.** Held: `../EPITOPE-BENCHMARK/epitope-records.json`, `validated-epitope-counts.json`,
`tabulate_epitopes.py`, `check_consistency.py`; the citing manuscript
`research/manuscripts/neoantigen/emc-vaccine-development-path.md` §B1 for the citation itself.
**New source, admitted route:** `mcp__PubMed__lookup_article_by_citation` →
`convert_article_ids` → `get_full_text_article`.

**3 · One artifact.** `ewsr1-fli1-discrepancy-resolution.json` — the citation as printed, what the
retrieved record actually reports, and the resulting delta (or no delta) to the n = 15 count, with
the inclusion rule re-applied in code.

**4 · Ownership / dependencies.** New lane `EPITOPE-BENCHMARK-2`. Reads EPITOPE-BENCHMARK and
NEOANTIGEN-3 read-only. Note the coupling: **NEOANTIGEN-3 asserts `len(VALIDATED) == 15`**, so if
this lane changes the count it must say so loudly rather than silently — it may not edit
NEOANTIGEN-3, and the assert is a feature, not an obstacle to remove.

**5 · Smallest validation, and stop.** Re-run `check_consistency.py` unmodified; the six negative
control rows must still be discriminating. **Stop** when the record is read or shown unreachable
through the admitted route. ⛔ Prediction is not validation; presentation is not efficacy.

**Compute/storage.** A few MCP calls; negligible.

---

## P8 — First investigation of `PUB-TXN-DEPENDENCY`: which claims re-derive? (rank 8)

**1 · Question and what is new.** Of the 33 endpoints in `systems/graph/publications.json`, this
one has **never had a lane** in either campaign round. Question: **which of its quantitative claims
can be re-derived today from committed artifacts, and which cannot?** New because nothing has been
checked at all — and because the dependency family's sibling lanes (PUB-BIOMARKER-DEP, DEP-THRESHOLD,
BIOMARKER-DEP-2, PUB-SYNLETH, PUB-MTAP-PRMT5) converged on one shared producer defect whose reach
into *this* manuscript is unknown.

**2 · Inputs, already held.** `research/manuscripts/dependency/emc-transcriptional-proteostatic-
dependency.md` sha256 `9523555483f00cfee00b6cd4cf64f5615f57c011f1640297bf952399e742b3ba`;
`research/modalities/depmap-sarcoma-dependency.json` sha256
`d88bed62a80dcb51675f0f7a5a27771a6c1f732e977200d39fa389cb8dd27546`;
`../DEP-THRESHOLD/threshold-sensitivity.json` and `CLAIMS-AT-RISK.md`;
`../BIOMARKER-DEP-2/producer-dispersion-retention.diff`.

**3 · One artifact.** `claim-rederivation-ledger.json` — one row per quantitative claim: the quoted
value, the artifact it should come from, the re-derived value, and a verdict in
{REPRODUCES, MISMATCH, NOT-RE-DERIVABLE-LOCALLY}, with the exact missing input named for the third.

**4 · Ownership / dependencies.** New lane `TXN-DEPENDENCY`. Reads the dependency-family lanes
read-only; touches no manuscript. No write conflict. ⛔ Not a "baseline review of a repaired paper" —
scope is re-derivation of stated numbers against committed inputs only, no prose grading, no gate
sweep.

**5 · Smallest validation, and stop.** Known-answer control: at least one claim already re-derived
by a sibling lane must be included and must reproduce that lane's value — if it does not, the
harness is wrong and the lane reports that instead. **Stop** at the first pass over the claims: no
second pass, no repair attempt, no diff to the manuscript. A MISMATCH is reported, never fixed here.

**Compute/storage.** Stdlib, < 5 min, < 5 MB.

---

## P9 — Reconcile the closed-routes negative record against what this campaign actually closed (rank 9)

**1 · Question and what is new.** `research/manuscripts/methods-record/closed-routes-negative-
record.md` (sha256 `e091b1cdf0b660b3ba947680b99a923c27f53565a6e4137d888bde6a6dbcf920`) is the
repository's standing record of closed routes and has had no lane. This campaign generated a large
amount of new, evidenced route-closure fact that is currently scattered across lane directories:
the GPL3290 accession bridge (`../FUSION-OUTPUT-3`), HPA `rnatss` returning empty so the
vital-tissue screen has no input (`../SURFACE-2`), the clinicaltrials.gov egress refusal at
curl exit 56 (`../STRATEGY-ARCH-2`), four references with no PMC record (`../REPURPOSING-3`),
`morioka2016trabectedin` retrieved incompletely (`../CARE-DELIVERY-3`), and the standing
B1/B2/B4/B8/B9 and R1–R4 dispositions. **Which of these does the record already carry, and which is
uncatalogued?**

**2 · Inputs, already held.** The manuscript above plus the six lane FINDING.md files named, all in
this checkout, all read-only.

**3 · One artifact.** `closed-route-coverage.json` + `UNAPPLIED-closed-routes-additions.diff` — a
coverage table (route · evidence locator · in-record yes/no) and an unapplied diff adding only the
uncatalogued rows, each with its evidence locator.

**4 · Ownership / dependencies.** New lane `CLOSED-ROUTES-2`. Reads six lanes read-only; the
manuscript change is **unapplied**. No write conflict. ⛔ A route being catalogued does **not**
reopen it, and cataloguing must not be written in a way that reads as a plan to retry one.

**5 · Smallest validation, and stop.** `git apply --check` on the diff with its **real** exit code
preserved (HLA-COVERAGE-2 hit exit 128 on a hand-written patch — generate, do not hand-write). Every
added row must quote its lane's own evidence path; a row without one may not be added. **Stop** at
the coverage table plus the diff.

**Compute/storage.** Stdlib, minutes, < 1 MB.

---

## P10 — Cross-paper EMC-patient-exposure index with a retrieval-completeness column (rank 10)

**1 · Question and what is new.** Proposed by `../REPURPOSING-2` and refined by
`../REPURPOSING-3/FINDING.md` §6.4: **how many distinct EMC patients does this portfolio's cited
evidence actually rest on, and how much of that is unread rather than absent?** New: nobody has
built it, and REPURPOSING-3 established the distinction it exists to preserve — [8] and [14] enter
as *unknown*, not as *none*; CARE-DELIVERY-3 independently invented the same
`retrieval_completeness` field for its own rows.

**2 · Inputs, already held.** `../REPURPOSING-2/CITED-REFERENCE-SWEEP.md`;
`../REPURPOSING-3/FIVE-REFERENCE-TABLE.md`; `../CARE-DELIVERY-3/care-delivery-element-coverage-v3.json`
(carries `retrieval_completeness` per row); `../CARE-DELIVERY-2/care-delivery-element-coverage-v2.json`;
`../LOCOREGIONAL-2/rt-local-control-contrast-ledger-k2.json`;
`../IPD-SURVIVAL-2/census-reproduced-2026-09-09.json`.

**3 · One artifact.** `emc-patient-exposure-index.json` — one row per cited series: identifier, n
EMC patients as reported, which papers cite it, and `retrieval_completeness` in
{complete, partial, unread}, with an explicit **overlap-unknown** flag wherever the same patients may
appear in more than one row.

**4 · Ownership / dependencies.** New lane `EXPOSURE-INDEX`. Reads five lanes read-only. No write
conflict. Not a pooled estimate and not a meta-analysis: **counts and provenance only**.

**5 · Smallest validation, and stop.** Every row's n must be traceable to a quoted figure in a named
source file — a row that cannot be traced is recorded UNKNOWN, never zero (CLAUDE.md §4). Control:
the two series LOCOREGIONAL-2 counted (21 recurrences / 175 patients) must reproduce from the index.
**Stop** at the index; no pooling, no denominator arithmetic across rows with an overlap-unknown
flag.

**Compute/storage.** Stdlib, minutes, < 2 MB.

---

## Discards — eleven candidates dropped, with the reason

1. **GPL3290 accession bridge** (FUSION-OUTPUT-3's named dependency) — needs GEO egress; direct HTTP
   is proxy-refused. Not eligible; belongs to the coordinator's networked route.
2. **HPA per-tissue `nTPM` for the vital-tissue screen** (SURFACE-2 §7.1) — networked fetch, and the
   surfaceome route **B4 is closed**. Relabelling would not reopen it.
3. **Per-line `CRISPRGeneEffect.csv` / `Model.csv`** (PUB-SYNLETH, PUB-MTAP-PRMT5, BIOMARKER-DEP-2)
   — networked **and** a large download. Two separate fences.
4. **Re-run MHCflurry over a wider allele panel incl. HLA-C** (NEOANTIGEN-3 §8.1) — predictor not
   installed (verified: no sklearn/pandas locally), model weights are a large download, and the
   HLA-C half is **route B8, excluded**.
5. **Any further sweep of the DepMap summaries** — DEP-THRESHOLD states explicitly there is nothing
   left to sweep, and BIOMARKER-DEP-2 says do not iterate on its diff.
6. **Measuring `C_E`** (ANDGATE-2's decisive quantity) — a wet-lab FCS measurement. Categorically out.
7. **Enlarging the trial-screen ablation** (STRATEGY-ARCH-2) — needs the clinicaltrials.gov fetch
   already refused at the proxy (curl exit 56), and the only offline substitute (paraphrasing
   criteria from adjudicator prose) is circular by that lane's own reasoning.
8. **Publisher PDFs for REPURPOSING references [8] and [14]** — no PMC record, so no admitted route
   reaches them. Recorded as a standing hole, not a task.
9. **Anything touching the EMC-classification endpoint** — user-rejected; and the retired
   patient-facing site is not to be recreated.
10. **`MF1` and `P-ST`** — ACCEPTED/CLOSED as of 2026-09-09; excluded by instruction.
11. **Checking `pinned-figures.json` against NEOANTIGEN-4's 170/174** (its §8.4) — **discarded on
    verified evidence, not on judgement**: `research/manuscripts/pinned-figures.json` contains no
    novelty pin, and `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md` contains
    zero occurrences of "174" (`grep -c` = 0, `checks/01`). There is nothing to reconcile. The live
    part of that item is P5.
