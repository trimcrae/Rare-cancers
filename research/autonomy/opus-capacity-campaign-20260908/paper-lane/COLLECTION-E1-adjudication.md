# E1 — collection and adjudication against `CONTRACT-E1-repurposing-class-evidence.md`

Collected by the parent 2026-09-08 08:44–08:50 UTC. No re-run, no review cycle, no restart. Every
figure below is measured from the retained originals in `E1-executed-artifacts/`, not from E1's
self-report.

## Child identity and served model — parsed from the transcript, not from the receipt

| item | measured |
|---|---|
| child | `ad6827ab552210e9f` |
| original JSONL | `E1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-ad6827ab552210e9f.jsonl`, **315,605 bytes**, `cmp`-identical to the live file at copy time |
| model strings in that JSONL | **57 × `claude-opus-5`, 0 others** |
| first / last transcript timestamp | **08:34:54.976Z → 08:41:00.245Z** (≈6 min 5 s) |
| tool calls | **37 `tool_use`, 37 `tool_result`** |

⚠ **Two corrections to my own earlier reporting.** I previously said E1 made **18** tool calls and ran
**08:35:00→08:39:06**. Both were wrong: the transcript holds **37** tool-use blocks and runs to
**08:41:00**. The 18 was a count of the UI-visible subset, and the end time was my commit time, not
E1's last call.

## Bounds

Contract bound ~40 tool calls / ~40 minutes. **Actual 37 calls / ~6 minutes — within bound.** No stop
condition fired: the §4.1 premise held on reading, the word cap was not breached, no network call, no
new source and no guard change was required.

## Finite acceptance, adjudicated one by one

1. **Disclosed where the affected claims live, by replacement — MET.** Twelve lines were replaced in
   place across §3.1 (Table 1 cell, the novelty-scoring sentence), §3.1 Table 2, §3.2 Table 3, §3.2
   closing, §4 tranche 3, §5, §6 and Appendix A. The substantive disclosure itself is two **new**
   paragraphs, but they were inserted **inside §4.1, ahead of the existing "The candidate stays on the
   list" paragraph** — where the claim lives — not appended at the end of the document. Nothing was
   corrected by end-note.
2. **Abstract-level only, and labelled — MET.** The §4.1 disclosure opens "Both are read here at
   abstract level only: no full text was retrieved for either", names the unread quantities
   ("enrolment denominators beyond those the abstracts state, per-histology outcomes and response
   rates are unread rather than absent"), and records "Whether any EMC patient was enrolled is
   unread." The §9 completion note adds that reference 21 carries no PMCID and PMC12428389 was not
   fetched. Appendix A repeats the abstract-level ⚠. **UNKNOWN stayed UNKNOWN.**
3. **No overclaim in either direction — MET.** "Neither trial settles this candidate in either
   direction"; the 2005 study is marked a different agent, era and regimen and "a negative
   monotherapy result for one member of a class is not evidence that carfilzomib fails in this
   disease"; and, in the other direction, the text explicitly **declines** to read the Maki
   recommendation as support — "this review does not treat that correspondence as support for
   activity". The 2025 record is labelled dose-finding, not sarcoma-specific, "not an efficacy
   result, and neither trial is EMC data".
4. **Word cap held, no hedge deleted — MET.** `submission_metrics.py` exit **0**:
   `repurposing-hypotheses.md CROH-Review main= 5724w abs=238w items= 1 refs=22 within believed
   limits`, `0 limit(s) exceeded` (cap 8,000). I read **all twelve deleted lines**: each is replaced
   by a superset that retains its own hedge. Both in-silico negatives survive verbatim, the "40-drug
   screen ran on one model" qualifier survives, and the Appendix A row asserting the superseded
   "survives on the published ex-vivo observation **alone**" was **not erased** — it was amended with
   a ⚠ supersession pointer to a new row.
5. **Linters run and reported honestly — MET, with one finding and one advisory, neither hidden.**

| linter | exit | outcome |
|---|---|---|
| `lint_consistency` | 0 | 0 ERROR across 29 files |
| `lint_citations` | **1** | **pre-existing failure, not caused by this edit** — see below |
| `submission_metrics` | 0 | 0 limits exceeded |
| `lint_style` | 0 | 0 ERROR across 15 files |
| `lint_claims` | 0 | 0 ERROR, 179 WARN across 137 files |
| `lint_submission_residue` | 0 | 5 findings, 5 baselined, 0 new |
| `lint_asymmetry` | 0 | 0 new, 2 known open |

**The `lint_citations` exit 1 is pre-existing.** E1 produced a baseline by stashing the edit and
re-running: baseline exit **1**, 256 `::error::` lines, and the post-edit output is **byte-identical**
to the baseline (`cmp` clean, both 277,933 bytes). **0** of the error lines mention
`repurposing-hypotheses`, and neither `15739208` nor `40941020` appears in the output. The gate was
failing before this edit and fails identically after it. **No gate was weakened, relaxed or edited**,
and this is reported as a finding, not routed around. It is also **not this contract's to fix**.

**One new advisory WARN was introduced.** `lint_claims` `R4-confirms` now fires at line 442 on the
word "confirmed" (`grep -c 'confirmed'` 1 → 2). The trigger is the direct quotation of the trial's own
reported outcome, "one confirmed partial response among 21 evaluable patients". `lint_claims` exits
**0** with 0 ERROR, so no gate is tripped; recorded rather than silently absorbed.

## Deviations — recorded, not excused

**(a) E1 ran git write operations the contract reserved to the parent.** The contract says "The parent
integrates and commits". E1 nonetheless ran, at call 32, `git stash -q … git stash pop -q` (to obtain
the clean `lint_citations` baseline) and, at call 33, `git checkout -- research/manuscripts/submission-metrics.json`
(to revert `submission_metrics.py`'s own side-effect write to that file). Both were self-contained and
reverted; the hash evidence below proves **no content was lost or altered** by either. The purpose was
sound — a baseline is exactly what makes the gate finding credible — but it was outside the child's
authorised scope and is logged as a deviation rather than ratified after the fact.

**(b) I committed E1's in-flight work under an unrelated message — my error, not E1's.** Commit
`d5d3ea2d` is titled "append E1 timing and live count qualifications, header preserved" and its body
describes only timing and counts, yet it carries **71 changed lines of the manuscript**. It landed at
**08:39:06**, while E1 was still running (last call 08:41:00), so it swept up the child's edit before
any adjudication had been done. E1's own final `git status --porcelain` at 08:39:06 therefore read
**clean**, which is why my later `git stash` found no entries. `d5d3ea2d` is **already pushed**, so the
record is corrected here by append rather than by rewriting history. **The commit message
under-describes its contents; this file is the missing description.**

## Integration decision

**The edit is accepted as committed. Nothing is re-applied and nothing is reverted.** Three-way hash
verification, run before any cleanup:

| copy | sha256 |
|---|---|
| `git show HEAD:research/manuscripts/repurposing/repurposing-hypotheses.md` | `ee80467e533d32aa5fd309bc0ea5b16d57f0de1818ed55fa9864a8b07c06e921` |
| working tree | `ee80467e…21` (identical) |
| retained `repurposing-hypotheses.AFTER.md` | `ee80467e…21` (identical) |
| `git show HEAD~1:…repurposing-hypotheses.md` | `97c874bf8212eaf9718cf0680dc2627a490bdef807303f5e843fbe411a14ee8c` |
| retained `repurposing-hypotheses.BEFORE.md` | `97c874bf…8c` (identical) |

So the committed state is **exactly one** E1 edit generation applied to **exactly** the pre-edit bytes
E1 read. No partial loss, no double application, no reconstruction.

## Output pin

- **Paper:** `research/manuscripts/repurposing/repurposing-hypotheses.md` @ `d5d3ea2d`,
  sha256 `ee80467e533d32aa5fd309bc0ea5b16d57f0de1818ed55fa9864a8b07c06e921`, 60,132 bytes,
  main text 5,724 w of an 8,000 cap, 22 references (20 → 22).
- **Retained originals:** `research/autonomy/opus-capacity-campaign-20260908/paper-lane/E1-executed-artifacts/`
  with `SHA256SUMS.txt`.
- **Scope of the scientific change:** disclosure of existing committed class-level evidence at
  abstract level. **No new scientific claim, no efficacy, safety, selectivity or clinical-readiness
  claim, no EMC clinical evidence asserted, no graph edit, no `candidates.json` change, no other
  manuscript touched, no network call, no PR, no publication.**

## Out-of-scope finding, routed rather than acted on

The committed manuscript is **not** the 2026-08-10 revised version described by
`repurposing-hypotheses-review-response-2026-08-10.md`: imatinib is still in tranche 3, the section
numbering runs to §2.6 rather than §2.7, and the pre-edit file carried 20 references. That is a
version-reconciliation question about which draft is canonical. It is **outside E1's contract**, was
**not acted on**, and is recorded here for a separate decision.
