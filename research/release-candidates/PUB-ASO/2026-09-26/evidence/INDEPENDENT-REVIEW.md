---
id: DOC-PUB-ASO-CBC-20260926-EVIDENCE-INDEPENDENT-REVIEW
title: "Independent read-only scientific review"
kind: memo
status: live
date: 2026-09-26
last_verified: 2026-09-26
purpose: Preserve the reviewed ASO candidate and its attributable supporting record.
scope: Local submission preparation with distinct source evidence classes.
audience: [maintainers, external reviewers]
---

# Independent read-only scientific review

Advisor: `/root/aso_source_advisor`, inherited session model and effort (no separate ultra setting requested or claimed). Scope and initial frozen hashes are in `REVIEW-REQUEST.json`. This is an internal AI review, not external peer review or submission certification. The advisor wrote no files and did not execute either analysis script.

## Initial source challenge

The advisor independently corroborated the Figure 4 coordinates and GRCh37 protein-to-transcript mappings, challenged the distinction between reference reconstruction and patient consensus, and identified the USZ22 internal-interval/direction ambiguity. It located the Brenca corrigendum and DElite sample mapping. It also identified the invalid general claim that an exon-3-anchored primer cannot recover an upstream cryptic exon. These findings were accepted with source checks and are addressed in the supporting methods and local correction record.

## Final advisor verdict (formatting normalized)

> Accept the changed scientific findings, with no scientific blocker identified. The proposed README runtime-command correction addresses the one reproducibility issue encountered.
>
> Independent read-only verification confirmed:
>
> - Every artifact hash in REVIEW-REQUEST.json matched.
> - The expanded corpus contains 77 records, 71 distinct sequences, including 68 RefSeq accessions with the stated gene counts.
> - Separate in-memory substring enumeration reproduced all 40 design maxima, checked antisense orientation, and found no full 16-base matches in this corpus.
> - Among the 35 source-linked designs, nine lengths increase; the adopted ten-base count changes 14→21. Five hypothetical controls remain separate.
> - For centred TCF12, the 11-base match TGGATATGCCC occurs at NM_173200.3:767–777 and U12767.1:85–95, independently confirming the reported 7→11 increase.
>
> The source interpretation is appropriately limited. USZ20 is a reference reconstruction supported by reported coordinates and displayed protein identifiers, with build/convention inferred and patient variants or insertions unexcluded. It is not a patient consensus. USZ22's internal-exon intervals and displayed directional discrepancy remain unresolved. Earlier independent GRCh37 API checks corroborated both interpretations.
>
> The Brenca probe's reporting is sound: a finite, nonrandom, single-mate prefix search with zero exact anchors does not establish absence or validate constructs. I inspected its code and result records; I did not independently rescan the compressed prefixes. The root's replay supplies that verification.
>
> The contribution merits a substantive integrated revision of the existing resource. A standalone technical note is defensible but modest: its useful advance is the corrected biological-model correspondence plus explicitly accessioned normal-isoform matches. Neither general register dependence nor the reused GenBank catalogue should carry its novelty claim. The current draft makes this distinction clearly.
>
> Optional clarity edit in supporting methods: replace "Thirty historical subset metrics were reused" with "Twenty-five source-linked metrics and five hypothetical-control metrics were reused; ten cryptic-junction metrics were newly calculated." This makes the 35-versus-40 denominators immediately clear.
>
> No files were written, no analysis script was executed, and no submission-readiness or ultra-review certification is implied.

## Root disposition

Accepted. The README now gives the actual installed Python executable, because the Windows `python` command invokes a Store shim. The supporting-methods denominator clarification was applied. The read-probe module docstring now names both supported prefix sizes and the final 64 MiB amendment. These presentation edits change no executable logic, scientific results or manuscript claims. Final artifact hashes are recorded in `ARTIFACT-MANIFEST.json`; the original review request is retained unchanged. No second full review is warranted by these presentation-only fixes.
