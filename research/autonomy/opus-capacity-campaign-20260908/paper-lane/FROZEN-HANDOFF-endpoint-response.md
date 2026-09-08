---
id: DOC-OPUS-CAMPAIGN-FROZEN-ENDPOINT
title: "Frozen final-review handoff — response endpoint in indolent tumours"
level: L4
kind: memo
status: live
purpose: >
  Hand the already-written response-endpoint manuscript to independent final review with its exact
  revision, its package, the original promotion disposition, and the checks that have and have not run.
scope: >
  L4. A handoff. It authorises no publication act, asserts no green gate, and creates no reviewer record.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen handoff — `response-endpoint-indolent-tumours.md`

## Exact revision and content identity

- **Git revision:** `9c6f4a80fc2fd69ee71ad6124c8de03e6e1af395`, branch `claude/confident-bardeen-ji76cd`.
- **Manuscript:** `research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`, 53,719 bytes,
  sha256 `bae48dbd23966cc247d428448ea81116fef7aeabf718e5f2da74103014f30408`, computed at handoff
  time. The per-file manifest shipped with the package is the authoritative record.
- **Package:** `collected/endpoint-final-review-package-20260908.tar.gz`, 418,826 bytes, sha256
  `14c8d32ab587bfa2216d3626449b52d54e7ae1554dbe095b14175684358f9411` — 21 files, 3,066,938 bytes, with
  a per-file sha256 manifest shipped beside it and inside it.

## What is in the package

The manuscript; the three SVG figures it prints (`endpoint-gap-distribution`, `endpoint-regime-map`,
`endpoint-zero-response`); the ten committed data artifacts it reads (`endpoint-corpus.json`,
`endpoint-corpus-inputs.json`, `endpoint-regime-map.json`, `emc-endpoint-discordance.json`,
`emc-endpoint-alternatives.json`, `emc-systemic-therapy-pooling.json`, `orr-dcr-reread.json`,
`placebo-arm-calibration.json`, `endpoint-prior-art-audit.json`,
`lit-targets-cross-disease-endpoints.json`); the six producers and the chain script
`regenerate_endpoint_chain.sh` that rebuild them in dependency order.

## Original promotion disposition, unmodified

The promotion lane returned **ALREADY COHERENT — freeze, zero edits**, having read all 763 lines. It
verified, and named, the following rather than asserting coherence:

- Internal arithmetic closes: 44 = 16 + 28; 14/28 = 50.0%; 2,851 + 1,563 = 4,414 and
  2,715 + 1,561 = 4,276; 4,414 − 4,235 = 179; 96.9 − 95.2 = 1.7; 251/552 = 45.5%; 6/47 = 12.8,
  42/47 = 89.4, 42 − 6 = 36 = 76.6% of 47; the four remedy families sum to 18.
- All 19 relative links resolve on disk. All seven producers named in §2.4 exist, are listed in the
  order `regenerate_endpoint_chain.sh` enforces, and all seven appear in
  `.github/workflows/tests.yml` lines 204–210 — so §2.4's "All seven run in continuous integration"
  is checkable and true.
- §8's prose matches storage exactly: `emc-endpoint-discordance.json` →
  `D1_same_patients_two_endpoints` holds 47 / 12.8 / 89.4 / 76.6, and
  `sensitivity_immunosarc2_denominator_22` holds 46 / 13.0 / 91.3 / 78.3 with
  `gap_moves_by_pct_points = 1.7`. The nominal 47 stays reported, the 46 denominator is
  distinguished, nothing is imputed.

⭐ **It named NO outstanding material scientific revision.** That is why this handoff exists.

## Checks that actually ran, with their exit codes

| check | result | exit |
|---|---|---|
| `lint_style.py <target>` | `clean` · 0 ERROR across 1 file | 0 |
| `lint_consistency.py` (repo-wide; takes no file argument) | 0 ERROR across 29 target files | 0 |
| `lint_claims.py <target>` | 0 ERROR, 2 WARN across 1 file | 0 |
| `test_endpoint_manuscript_figures.py` | 7 passed | 0 |
| `test_endpoint_logic.py`, `test_the_census_reads_every_publication_endpoint.py`, `test_the_endpoint_reference_list_binds_to_what_was_fetched.py` | 85 passed | 0 |

The two `lint_claims` WARNs are pre-existing and are not defects: line 39's `'confirmed'` sits inside
the editorial authorship comment, and line 631's `'confirmation'` is "central molecular confirmation"
in settled §8.

## Checks that did NOT run, stated rather than implied

- ⛔ **No full `scripts/preflight.sh`.** No `PREFLIGHT_FULL` receipt exists for this revision.
- ⛔ **The producers were NOT re-run**, so this package shows that the manuscript's figures match
  their stored artifacts — it does **not** re-establish that those artifacts re-derive from their
  inputs. CI is the standing evidence for that; it is wired, and I did not confirm its last run.
- ⛔ `lint_citations.py` still exits 1 repo-wide. Its inventory is 187 unanchored plus 13 uncached
  type claims, **all 200 inside `research/autonomy/opus-capacity-campaign-20260908/` and none in this
  or any other live manuscript**. ⚠ Its summary line says "type claim(s) disagree with PubMed", which
  is wrong: every one of the 13 is `MISSING` — no cached metadata — and **zero** are `MISMATCH`.
- ⛔ `systems_check.py --check` reports 2,394 ERROR / 270 WARN, measured identical with and without
  this session's changes. Pre-existing, not cleared.

## The one editorial preparation, identified and NOT silently applied

⚠ Lines 44–56 are an HTML comment block headed `EDITORIAL, NOT FOR SUBMISSION`. It records venue
intent (medRxiv then JNCI), the absent ORCID, and the filename artifact. **It must be stripped at
deposit and it has NOT been stripped here** — the manuscript in this package is byte-for-byte the
version the promotion lane read and froze. Stripping it is a deposit-time packaging step, and doing
it now would substitute a different file for the reviewed one.

One further observation, left alone deliberately: §8 names three cohorts but states sizes for only
two (22 and 23), leaving the third as 47 − 45 = 2 for the reader to infer. It is arithmetically
consistent and owned by the companion JSON (`per_cohort`), and §8 is closed, so adding the third size
would be new content in a settled section.

## What this handoff is not

⛔ It is not publication permission, not a reviewer record, and not a claim that any gate is green.
It asserts no EMC efficacy, safety, selectivity or clinical readiness, and it reopens none of the
closed EP1/PR1 source, denominator or sensitivity questions — the stored sensitivity values are
carried exactly as they stand.
