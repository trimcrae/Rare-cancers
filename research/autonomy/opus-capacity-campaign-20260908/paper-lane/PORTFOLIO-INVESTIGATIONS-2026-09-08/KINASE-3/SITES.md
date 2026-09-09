---
id: DOC-PORTFOLIO-INVESTIGATION-KINASE-3-SITES-2026-09-09
title: "KINASE-3 — every prose site the composition attenuation bears on, and every pin / generated-artifact site quoting the affected figures"
level: L4
kind: site-list
status: live
date: 2026-09-09
lane: KINASE-3
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# Site list

Line numbers are against the files as of repo HEAD at lane start (see FINDING.md). Paths are
repo-relative. `B/` abbreviates
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/`.

## A · Is there a "kinase manuscript"?

**No manuscript file exists for this endpoint.** `systems/graph/publications.json:281` registers
`PUB-KINASE-LEADS` with `"state": "outlined"` and **no `document.file`**. The nearest manuscript
asset is `research/manuscripts/dependency/emc-kinase-leads-source-verification.md` (475 lines) — a
source-verification record, not the endpoint's paper. Grepped for `concordan|both platforms|65.2|
0.652|joint p|two-platform|percentile|GPL`: **3 hits, none resting on the concordance statistic**:

| File · line | Sentence | Does the attenuation bear on it? |
|---|---|---|
| `research/manuscripts/dependency/emc-kinase-leads-source-verification.md:349` | "`ALK` and `ROS1` have **no probe** on either `GPL6244` or `GPL3290`…" | **No** — a probe-coverage statement. Unchanged. |
| `…:351` | "The one readable named target, `EGFR`, is lower in EMC on both platforms." | **No correction needed.** EGFR is a per-gene direction read, not the concordance rate, and it *survives* adjustment concordantly on both platforms (r −0.480 → −0.687 GPL6244; −0.476 → −0.455 GPL3290). Listed as checked, not corrected. |
| `…:388` | "*the arrays structurally cannot attribute the kinase hit* — no probe for either named kinase on either platform" | **No** — coverage, not concordance. Unchanged. |

So every sentence the attenuation bears on lives in the two campaign lane findings below. That is
itself part of the result: **the unadjusted concordance has not yet propagated into any manuscript,
pin or generated artifact**, so the correction is cheap now and would not be later.

## B · `B/PUB-KINASE-LEADS/FINDING.md` — sentences the attenuation bears on

| Line(s) | Claim | Rests on | In the diff? |
|---|---|---|---|
| 3 (title) | "the two-platform concordance argument has no negative, and when one is built the strongest lead is a 1-in-13 gene…" | the unadjusted joint p values | **No** — unchanged and still true; the joint p values are computed on the unadjusted statistic and stand. |
| 33–34 | "Two-platform concordance is the load-bearing inference of the paper's whole computational arm." | framing | No — still true, and more so. |
| **70–71** | "**281 of 431 randomly drawn genes (65.2%) already move the same way in EMC on both platforms.** Sensitivity frame … **65.8%**." | the unadjusted concordance | **Yes** — adjusted figures added alongside, unadjusted retained. |
| **73–76** | "Concordance is not near 50% because the two series share the same EMC arm identity and have correlated comparator arms; **whatever the cause** …" | the unadjusted concordance; "whatever the cause" is now partly answered | **Yes** — pointer added to the supplement. |
| 81–96 (Result 2 table) | per-lead joint empirical p | unadjusted statistic; **not invalidated** by the attenuation | No value changed. Covered by the new NDRG1/NR4A3 note at 114–117. |
| **110–112** | "The endpoint's supporting prose leans on NDRG1 at the '98th percentile' … joint p = 0.088 — about one gene in eleven." | NDRG1's unadjusted placement — the lead that attenuates most and most consistently | **Yes** — the adjusted NDRG1 reading is added immediately after, at 114–117. |
| **114–117** | "**this is a calibration, and it cuts both ways** … What it removes is the *unqualified* use of 'concordant on both platforms' anywhere in the paper." | the unadjusted calibration | **Yes** — new paragraph appended: the calibration is itself calibrated. |
| **146–149** | limitation: comparator-arm difference "is itself a candidate cause of the 65% baseline concordance and **is not separated here**" | explicitly the open question EXPR-COMPOSITION bounded | **Yes** — updated to "partly addressed", with the upper-bound wording. |
| 173–176 | next work item 1: "A permutation null for the concordance baseline itself" | superseded by KINASE-2, not by this attenuation | No — out of this correction's scope. |

## C · `B/KINASE-2/FINDING.md` — sentences the attenuation bears on

| Line(s) | Claim | Rests on | In the diff? |
|---|---|---|---|
| **3 (title)** | "the 65.2% two-platform concordance **is a real shared EMC contrast**, not inter-series correlation" | the unadjusted concordance, read as EMC-borne | **Not edited** — the claim as literally written (contrast, not inter-series correlation) survives the adjustment; the qualification is carried at 73 and 147–152 instead. **Flagged for the owner**: if the title is ever read as "EMC biology", it needs the same qualifier. |
| 31–34 | restatement of the 65.2% | unadjusted | No — quotation of lane 1, corrected at source in §B. |
| 53 | reproduction check "431 genes, 281 concordant, 0.652" | a reproduction record, not a claim | No. |
| 56–66 (§3 heading + table) | "0.6520 (281/431)", "0.6344 (262/413)", permuted 0.4990 / 0.5022 | unadjusted | Values retained unchanged; the supplement follows at 73. |
| **73** | "The 65.2% is a property of the **contrast**, not of the series pair." | the step from "contrast" toward "EMC biology" | **Yes** — supplement block inserted after it. |
| **111–115** | "we now know **why**: the EMC-vs-comparator contrast … is **broad**, moving a large fraction of the transcriptome consistently in both series." | breadth attributed to the contrast | **Yes** — at most about half that breadth is composition (upper bound). |
| **117–121** | "because its baseline is real shared signal, **the gene-resampling null is conservative, not lenient** … the baseline is **earned**." | "earned" reads as biology-borne | **Yes** — qualified: earned means label-borne, not composition-free. The conservatism conclusion is preserved. |
| 121–124 | "GFRA2 remains the most extreme gene under both nulls … null-independent" | GFRA2 attenuates negligibly on GPL3290 (+0.03) and *strengthens* on GPL6244 | No — unaffected; stated here so it is not silently swept in. |
| 128–135 | the crowding / specificity re-reading of NR4A3, RET, NDRG1 | unadjusted min\|t\| ordering | No — NR4A3 *strengthens* under adjustment, so the crowding statement is not weakened. |
| **147–152** | "(a2) a shared contrast-level confound … **It remains open**, and it is the more plausible driver…" | the exact open alternative EXPR-COMPOSITION answered | **Yes** — "partly closed, and against the biological reading", bounded not eliminated. |
| **211–214** | next work item 1: "Separate (a2) from (b): a composition-matched or composition-adjusted contrast." | now done | **Yes** — marked done, with what is still not done (deconvolution; two-covariate and MKI67/EPCAM sensitivity). |
| 215–219 | next work item 2: propagate both nulls into the endpoint's prose | joins this correction | No — still open, unchanged. |

## D · Pins and generated artifacts quoting the affected figures — **none found; nothing changed**

`checks/05-pin-and-generated-artifact-scan/`.

| Target | Pattern | Result |
|---|---|---|
| `research/manuscripts/pinned-figures.json` (2060 lines) | `0.652`, `0.6521`, `65.2`, `65.8`, `0.6368`, `0.6344`, `0.5668`, `0.5981`, `0.0742`, `0.0882`, `concordance` | **0 hits.** No pinned quantity quotes any affected figure. **No pin was changed by this lane.** |
| `systems/graph/*.json`, `systems/views/*.md` | `0.6521`, `65.2 %`, `two-platform concordance`, `label-permutation` | **0 hits.** |
| `research/modalities/*.json`, `research/manuscripts/**` | same | **Hits are all coincidental and unrelated** — `0.6521` appearing as an ordinary per-sample z or array-percentile value in `emc-expression-panels{,-inputs}.json`, `emc-hypoxia-null-background.json`, `nr4a3-fusion-targets-inputs.json`, `emc-atr-vulnerability-inputs.json`, `tcf12-/pgr-/aso-offtarget-*-inputs.json`; and `label-permutation` referring to the **fusion-output** paper's own exact test (`research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md:496, 971, 1257`; review files) and to `nr4a3-fusion-targets-review-sensitivity.json:959`. **None is this concordance statistic.** `research/manuscripts/surface-targets/emc-surface-target-landscape-peer-review-2026-08-10.md:494` uses the phrase "two-platform concordance" for the surface-target paper's own significance-based concordance rule, a different statistic on a different gene set — **not** affected. |
