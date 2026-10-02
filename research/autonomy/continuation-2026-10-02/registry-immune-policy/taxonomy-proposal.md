---
id: DOC-REGISTRY-IMMUNE-TAXONOMY-PROPOSAL-20261002
title: Outcome-scoped immune response families in the accepted registry replay
level: cross-cutting
kind: memo
status: live
purpose: Resolve the source taxonomy behind 27 qualification reductions without converting immune response labels to ordinary RECIST.
scope: Three archived outcome objects covering 27 previously reviewed units; descriptive schema proposal and manuscript wording, with no production extractor change.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Finding

All 27 reductions have explicitly named response families in their archived outcome context. They can support a **descriptive, family-specific category map**, retaining four literal cells under the exact outcome-specific family name. They cannot support silent reassignment to ordinary RECIST or standardized iRECIST. This conclusion uses the accepted replay artifact, not a new registry retrieval or a repeated corpus analysis.

| Source outcome | Units | Explicit family | Assessment context | Remaining uncertainty |
|---|---:|---|---|---|
| NCT02263508, Phase 3 BOR | 2 | modified irRC-RECIST | BICR; confirmed iCR/iPR/iPD at least four weeks later; minimum iSD duration specified | Modified charter/version not identified in this outcome; do not erase its trial-specific definition |
| NCT02626000, Best Overall Confirmed Response | 1 | irRECIST | Investigator assessment; iCR/iPR/iPD confirmation at least four weeks later | No versioned criteria citation; standardized iRECIST equivalence is not established |
| NCT02829723, Phase I BOR with confirmation | 24 | irRC | Local investigator; CR/PR confirmation at least four weeks later, progression confirmation; assessments more than 30 days after last dose excluded | Outcome does not specify dimensional measurement convention, numeric response thresholds or criteria version; none are imported |

These are three **source-reported names**, not three independently validated universal ontologies. The result set contains three distinct complete outcome hashes, and those hashes remain part of family identity. The full registry descriptions, time frames, population definitions and physical source pointers are retained in `reviewed-27-unit-contexts.json`; `all-27-units.md` enumerates every unit and literal count. This preserves the distinctions between randomized participants, a restricted efficacy analysis set, and treated Phase I solid-tumor participants excluding glioblastoma/lymphoma.

The named families are not identified as iRECIST anywhere in these three outcome descriptions. The primary iRECIST guideline separately describes variability in historical irRECIST implementations and uses iUPD/iCPD terminology. Its terminology supports avoiding an equivalence inference; it does not retroactively assign a standard to these trials. [Seymour et al., primary guideline](https://pmc.ncbi.nlm.nih.gov/articles/PMC5648544/). Metadata and the actual retrieval receipt are in `criteria-source-receipt.json`.

## Proposed representation

Preserve existing `normalizedIntegerCells` and `normalizationStatus` unchanged. Add a separate optional `contextualFamilyAssignment` with:

- `familyNameLiteral`: the name explicitly reported by the outcome, without synonym collapse.
- `familyScopeKey`: NCT ID plus full outcome JSON SHA256. Keep class index and group ID in the unit key.
- `evidencePointers`: source archive/hash, physical outcome pointer and title/description fields supporting the assignment.
- `evidenceStatus`: `explicit-in-outcome`; use `label-only`, `conflicting` or `not-established` for other cases rather than a numeric confidence score.
- `criteriaVersion`: null when absent; retain reader, confirmation, timing, population and treatment-discontinuation rules as context.
- `categoryMap`: CR/PR/SD/PD as lexical roles **within this family**, paired with complete literal category titles and measurement objects. This is not a standardized clinical response vector.
- `crossOutcomeEquivalence`: `not-established`; `poolingAllowed`: false by default.

The proposed mappings match all 27 older family-qualified literal vectors exactly. This was checked against the saved comparison rows, not by changing either accepted normalizer. Every selected row contains one literal cell per family role. Unevaluable, missing, not-done and unknown categories remain separate. Posted participant denominators remain in their existing scope; no response fraction or imputed category is added.

An eventual implementation should require outcome evidence rather than infer family from an `i`/`ir` suffix. Conflicting or absent context must remain unresolved; unconfirmed and confirmed progression must not collapse; duplicate aliases must remain ambiguous. No production family extractor is implemented at this checkpoint, so no synthetic implementation tests or new extraction totals are claimed.

## Important boundary exposed by adjacent context

The same archived NCT02263508 study includes “Phase 1b: Best Overall Response (BOR)” assessed using modified irRC, despite ordinary CR/PR/SD/PD labels. Its outcome description states tumor-area response definitions and confirmation requirements distinct from the Phase 3 modified irRC-RECIST outcome. This is a concrete counterexample to inferring criteria solely from category labels. It means the accepted **510 unqualified-label vectors are not 510 verified ordinary-RECIST outcomes**. The review does not expand to classify all 510; the counterexample is retained in the machine-readable evidence.

## Source-bound replacement paragraph

> In the known-corpus replay, 510 of 575 retained class–group units met the conservative utility's unqualified-label four-cell policy. This is label-policy qualification, not confirmation that 510 outcomes used ordinary RECIST. The 27 reductions were confined to three explicitly named, outcome-specific immune-response contexts: modified irRC-RECIST in NCT02263508 (two units), irRECIST in NCT02626000 (one), and irRC in NCT02829723 (24). None of those outcome descriptions explicitly identified standardized iRECIST. Their literal four-category measurements can be represented within separate named families while retaining assessor, confirmation, population and timing context; equivalence across families was not established. An adjacent NCT02263508 Phase 1b outcome used modified irRC with unprefixed category labels, demonstrating why labels alone cannot determine clinical criteria. The historical normalizer's 537 qualified rows and 27 corrected extraction rows remain the results of its original policy; the conservative replay and this contextual review are reported separately.

## Provenance and scope

Accepted [replay run 37017553101, job 110872050056](https://github.com/trimcrae/Rare-cancers/actions/runs/37017553101/job/110872050056), code `e4e41e8cc93e66c2a576ec8a6f6f4acba5c5d496`, artifact `11231565922`. The 251939-byte ZIP was read in memory and verified against SHA256 `57d104bd9f9e101c82c0ecf90e50837b084eafd165a0d12bb8faaecf3fed0deb`. Only scoped contextual evidence was materialized. All three selected outcomes come from the [frozen 2014–2017 BOR archive](https://github.com/trimcrae/Rare-cancers/blob/216bd1b5fb25a56b90ef3cc2373e1fe68322708f/literature/xdisease-ctg-results/ctg_results_bor_2014_2017.txt), SHA256 `d5a460a9f9a703cbfb05aaeeef2e0b620bfbf288ec7a0c90316907d8f5b42ef1`.

NCT02829723 has 25 declared groups in the selected outcome, but OG011 is outside the accepted 24-unit subset; it is not added. No historical counts, accepted algorithms, clinical estimands or patient denominators are revised. The result is not a clinical error rate, held-out validation or confirmation of response-criteria implementation in patient-level data.
