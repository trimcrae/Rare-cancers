---
id: DOC-REGISTRY-FULL-REPLAY-20261002
title: Known full-corpus registry extraction transfer replay
level: cross-cutting
kind: memo
status: live
purpose: Describe the executable comparison of conservative literal extraction with the frozen registry reconciliation.
scope: Same selected 552 parent tables and 575 historical class-group units; frozen replay method and separately linked executed findings.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: unverified
---

# Known full-corpus transfer replay

Executed status: [run 37017553101](https://github.com/trimcrae/Rare-cancers/actions/runs/37017553101/job/110872050056) passed at `e4e41e8cc93e66c2a576ec8a6f6f4acba5c5d496`. See [result memo](result-memo.md), [summary](results/summary.json) and [complete compressed output](results/full-replay-output.zip). The frozen method below remains distinct from those findings.

Question: does applying the conservative reusable literal extractor to the same archived source outcomes change retained class/group units, four-cell qualification or eligible participant denominators relative to the frozen 575-row normalization? This is a transfer check on the known development corpus, not held-out validation, a registry error-rate study or retrieval-recall measurement.

## Cloud invocation

```sh
python3 registry-full-replay/replay_full_registry.py \
  --source-dir /tmp/emc-registry-full-inputs \
  --out outputs-registry-full \
  --download --max-seconds 600
```

The runner and adjacent `expected-inputs.json` are sufficient. It fetches the exact pinned utility rather than whatever version happens to be importable. Omit `--download` to reuse already staged, hash-verified inputs. No package installation is needed. Do not run the download on the low-space local workstation.

The manifest includes ten raw archives (156,081,683 bytes), the 935,150-byte original compact input, both frozen result artifacts and the 9,486-byte extractor. Raw archive byte counts and SHA256 hashes come from the original reconciliation's source receipts. The two result artifacts and extractor were additionally retrieved in memory and hashed during preparation. Reconciliation SHA256 exactly equals the normalization's recorded inputSHA256. Corpus archives were not downloaded during preparation.

Before any download, the runner requires 10 GiB free plus all expected input bytes and a 64 MiB output reserve. Individual downloads cannot exceed their exact frozen sizes, use 25-second socket timeouts and share a 600-second default deadline. A partial response is not accepted. A source directory is a dedicated cache; successful inputs remain reusable. The deadline is checked between chunks and computation stages, not enforced by an external process watchdog. Root may apply a cloud job timeout as well.

## Unit reconciliation and evidence

Parent identity is `(NCT ID, SHA256 of complete canonical outcome JSON, outcome-local group ID)`. Class/group identity adds the literal class index. A short `OG...` ID is never joined across outcomes. All ten archives are scanned, but only the pre-existing 552 parent identities are in analysis scope. Other outcomes are not silently added as a new cohort.

The utility receives each complete selected outcome and original study protocol in a one-outcome envelope to bound memory; temporary array positions are explicitly rebased to the original study/outcome indices. Full outcome literals, measurement objects, category/class fields, denominator entries and source coordinates are retained. Repeated query occurrences are compared for identical normalized output and then deduplicated by semantic identity. The original 564 physical occurrences are checked separately.

The old 575 units existed only for classes with observed measurements for that group. The reusable utility also retains declared class/group combinations without measurements. Such new units are listed explicitly with zero measurement counts; they must not be misreported as additional observed populations. Populated unmatched units, old-only units, missing source occurrences or loss of literal fidelity produce a nonzero exit and an integrity-review-required result.

For matched units, the comparator checks ordered category index/title/value tuples, class fields and group definitions against the frozen old reconciliation independently of the new alias functions. It then reports qualification transitions, exact-cell vector changes, alias assignment differences, denominator value/scope differences and original group-observed versus complete-outcome class counts. It does not calculate response rates, substitute zeros, harmonize immune/qualified response categories or pool classes.

Expected reasons for genuine differences are explicit policy changes: the old normalizer recognized leading category abbreviations and i/ir-parenthesized labels; the new utility is more conservative. The old denominator fallback used classes observed for one group and deduplicated integer denominator values; the new utility uses complete-outcome class scope and refuses duplicate participant entries even when their values match. These are hypotheses to test, not measured results. Historical 552/575/537/38 scope assertions validate that the intended old benchmark loaded; the new utility's counts are never asserted equal to them.

## Outputs and interpretation

- `summary.json`: source receipts, scope, qualification transitions and change counts.
- `unit-comparison.json`: matched-unit evidence and physical coordinates.
- `unmatched-units.json`: every old-only/new-only unit and occurrence discrepancy.
- `generic-literal-rows.json`: complete new row representations.
- `generic-literal-outcomes.json`: complete selected outcome objects, preserving context.

A zero exit means source identity, matched literal fidelity and coverage checks completed; it does not mean the two normalization policies are clinically equivalent. Qualification changes are findings, not automatically test failures. Review the explicit differences before adding any manuscript count. Existing historical correction counts remain unchanged until a separately labelled replay result is reviewed. The prepared method was frozen at the executed revision; the subsequent result is recorded separately.
