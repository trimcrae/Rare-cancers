---
id: DOC-PORTFOLIO-REPURPOSE-DECOY-1-FINDING
title: "REPURPOSE-DECOY-1 — is the NR4A3 shortlist separable from property-matched decoys?"
level: L4
kind: finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# REPURPOSE-DECOY-1 — separability of the shortlist from property-matched decoys

Lane `REPURPOSE-DECOY-1` (DISCOVERY-2 proposal 8). Nothing outside this directory was written. No
git write, no preflight, no subagent, no repo copy, no docking, no GPU, no structure prediction —
every number below is a re-analysis of scores already computed and committed. Retained output 128 KiB.

⛔ **Docking and MM-GBSA scores are not affinities and not efficacy.** Nothing here is a claim about
efficacy, safety, selectivity in cells, therapeutic window or clinical readiness for any drug, and
no drug named here is a candidate for use.

## 1 · The question

Does the committed NR4A3 shortlist separate from the committed decoy negative-control set on the
scores the screen actually uses — and does that separation survive matching the decoys to the
shortlist on molecular properties?

## 2 · Paper-level merit

The whole NR4A3 small-molecule route (de-novo, repurposing, degrader warhead) is calibrated against
one committed 38-drug decoy null: `nr4a3-repurpose-decoy-blend.md` states that the raw MM-GBSA
selectivity verdict is meaningless on its own and that only the decoy-calibrated bar (+13.12
kcal/mol) makes a call credible. Every downstream shortlist inherits whatever that null is worth.
If the null is separable from the shortlist on size and lipophilicity alone, the calibration is
measuring physicochemistry, and the bound on what the route may claim moves. That is decidable now,
from committed numbers, and a negative bounds the route rather than stalling it.

## 3 · The exact evidence gap

`decoy_library.py` says so in its own header: *"This is a property-spanning negative set, not a
property-matched DUD-E set … (A property-matched DUD-E decoy set is a heavier follow-up.)"* The one
piece of property-matching code in the repository, `property_matched_control.py`, was written for a
different question (7 IDH inhibitors) and **reads its docking scores from S3**
(`s3://<bucket>/nr4a3-repurpose-nr4a3only/shard-NN-ckpt/*.results.jsonl`), which are **not in this
checkout**. So no property-matched comparison of the shortlist against the decoys had ever been run
on committed data. This is distinct from the four prior repurposing lanes (PUB-REPURPOSING,
REPURPOSING-2/-3/-4), which are literature and reference-provenance work on the *clinical*
repurposing manuscript and touch none of these scores.

## 4 · The bounded step taken, and the result

`analyze.py` — read-only, re-hashes all 15 inputs at use, computes ROC-AUC with 4,000-draw bootstrap
CIs and 20,000-label permutation p-values, enrichment factors, an RDKit property audit, a
property-matched decoy subset, and the required chance check. **Four results.**

**(a) The decoy set is not property-matched, and the mismatch is larger than the signal.**

| separator | AUC (shortlist vs 38 decoys) | perm p |
|---|---|---|
| cLogP alone | **0.828** | 0.0004 |
| heavy-atom count alone | **0.823** | 0.0006 |
| molecular weight alone | **0.812** | 0.0006 |
| **NR4A3 docking score** | **0.761** | 0.005 |
| docking selectivity margin | 0.586 | 0.37 |

Three plain physicochemical descriptors each separate the two sets **better than the docking score
does**. Shortlist median cLogP 4.79 vs decoy 2.52; MW 356 vs 267.

**(b) On property-matched decoys the separation is not significant.** Restricting the decoys to the
shortlist's MW / cLogP / aromatic-ring envelope (25 of 38 survive) drops the NR4A3 docking AUC from
0.761 to **0.668, 95% CI [0.471, 0.831], p = 0.094**, and the selectivity margin — the quantity the
+13.12 bar is built on — to **0.512, CI [0.314, 0.706], p = 0.91**, i.e. exactly chance.

**(c) The required chance check PASSES.** The generation-matched scramble set, scored against the
scheme-matched (multi-snapshot) decoy run, lands at chance: mm_min_margin **AUC 0.513, CI [0.357,
0.668], p = 0.879**; MM-GBSA ΔG(NR4A3) AUC 0.625, CI [0.464, 0.772], p = 0.127. So the comparison
above is not an artifact of the matching procedure. Had this landed off chance, (a) and (b) would
have been uninterpretable and reported as such.

**(d) Incidental, and load-bearing: the committed +13.1165 bar is scheme-mismatched to what it is
applied to.** The bar reproduces exactly as the 95th percentile of the **single-snapshot** decoy run
(`results/nr4a3-decoy/-mmgbsa/`, p95 = 13.1165, max 16.46). But
`results/nr4a3-generation-matched-null/` applies it to the **multi-snapshot 10-frame** scramble and
de-novo rescoring, whose own decoy p95 is **6.69**. The third committed decoy run
(`-mmgbsa-metad-ms`) gives **17.70**. The bar therefore spans **6.69–17.70 kcal/mol (2.6×)**
depending on which committed decoy run its percentile is taken from. In the direction actually used
the mismatch is conservative (a 13.12 bar applied where the scheme-matched null says 6.69 makes
survival harder, so `n_above_null = 0` is not inflated by it) — but a bar with a 2.6× scheme
dependence is not a calibrated bar, and the same mismatch run the other way inflates. Mixing schemes
also manufactures apparent structure: scramble against the *mismatched* single-snapshot decoys gives
AUC 0.336, p = 0.044, where the scheme-matched comparison gives 0.513, p = 0.879.

**Answer: no.** The shortlist is not separably better than property-matched decoys on the committed
scores. The apparent separation against the full decoy set is at least as well explained by the
shortlist being larger and more lipophilic than the decoys.

## 5 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `repurpose-decoy-enrichment.json` (26 KB) — AUCs with bootstrap CIs and permutation
p-values, enrichment factors at 5/10/20 %, the eight-descriptor property audit, the property-matched
subset with its envelope and member list, the chance check, the decoy-bar scheme sensitivity, and
per-compound rows for all 51 molecules. `analyze.py` reproduces it.

**Validation / baseline.** The negative control is the shortlist's own property distribution
(property-only scorers) plus the property-matched decoy subset; the falsifiable check is the
generation-matched scramble set, which passed at chance. AUC ties count 0.5; null MM-GBSA rows are
dropped and counted, never treated as zero (1 scramble row).

**Provenance.** All 15 inputs SHA-256'd at use and recorded in the artifact under
`provenance_sha256`; DISCOVERY-2 computed none. Sizes match the dispatch note
(`nr4a3-repurpose-candidates.json` 1,437,223 B). `checks/01…05/` hold every attempt with
`command.txt`, `stdout.txt`, `stderr.txt`, `exit_code.txt`; **two failed** (01 TypeError on a null
MM-GBSA row, 04 IndentationError from a bad edit) and are preserved.

**Limitations.**
- **The set scored is not the clinical repurposing shortlist.** The 13-compound "shortlist" is the
  literature NR4A-active reference set in the committed 3-receptor tier
  (`results/nr4a3-matrix/`). The 5,988-drug Broad library's per-drug docking scores and the 250
  promoted drugs' MM-GBSA values live in S3 and are **not committed**; only a 195-line text report
  of selected subsets is. The repurposing shortlist's own AUC is therefore **not computable from
  this checkout**, and computing it would require re-reading S3 (out of scope, and the top-250 was
  selected on the same score, which would make a naive AUC circular).
- n = 13 vs 38 is small; the CIs are correspondingly wide and the matched-subset result is
  "not significant", not "proven null".
- Property matching here is a three-descriptor envelope, not DUD-E charge/topology matching.
- The decoy set was never docked in a pose-quality-controlled way against these compounds; AUC on a
  docking score is a property of the scoring function, not of binding.

**Stop condition.** Reached. The question is answered on the data that exists, the required chance
check ran and passed, and the artifact exists. The next credible independent step is a genuine
property-matched (DUD-E-style) decoy set built from the Broad library itself and pushed through the
identical funnel — that is new docking, which this lane's fences forbid. Finding (d) should be
routed to whoever owns the decoy calibration; **no shared file was edited and no diff is proposed**,
because the fix is a re-derivation, not a text change.
