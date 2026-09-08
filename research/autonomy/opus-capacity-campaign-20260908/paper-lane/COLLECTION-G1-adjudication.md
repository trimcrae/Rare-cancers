# G1 — collection and adjudication against `CONTRACT-G1-surface-targets-platform-confound.md`

Collected by the parent 2026-09-08 09:11–09:14 UTC from the retained originals, not from G1's
self-report. No re-run, no restart, no review cycle.

## Child identity — parsed from the transcript

| item | measured |
|---|---|
| child | `a5ae37108b22c6b0c` |
| original JSONL | `G1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a5ae37108b22c6b0c.jsonl`, **169,979 bytes**, `cmp`-identical at copy |
| model strings | **34 × `claude-opus-5`, 0 others** |
| tool pairs | **21 `tool_use` / 21 `tool_result`** |
| span | 09:07:30Z → 09:10:21Z (~2 m 51 s) |

⚠ **Count correction.** G1 self-reported "13 tool calls"; the transcript holds **21**. The same
undercount appeared in E1 (18 reported / 37 actual). Self-reported call counts in this campaign are
not reliable; the transcript is. Bounds ~40/~40 are met either way.

## Verification of the committed state

| copy | sha256 |
|---|---|
| `git show HEAD:…emc-surface-target-landscape.md` (read-only baseline) | `8a87e271…08f1` |
| retained `BEFORE.md` | `8a87e271…08f1` — identical |
| working tree | `4aa5cdb2…9219` |
| retained `AFTER.md` | `4aa5cdb2…9219` — identical |

Baseline was taken by **read-only `git show`**; no stash, no checkout of the shared tree.

## Finite acceptance, adjudicated

1. **Disclosed in Methods, Limitations and Results, in place — MET.** Three passages, no end-note.
   `grep` for `CRH|UHR` over the manuscript: **0 before → 4 after**.
2. **Annotations quoted from the committed artifact — MET.** The CRH/mRNA and UHR/total-RNA strings
   and the GSM accessions come from `research/modalities/emc-expression-panels.json`. No annotation
   was inferred.
3. **Scope figures verified or omitted — MET, and this is the strongest thing G1 did.** It used
   **+0.599**, which it verified in the committed text (GPL3290 route panel, disagreeing with
   GPL6244's −0.0935; `grep` finds it twice). It **refused** the review's "all 78 GPL3290 gene
   contrasts": the only 78 in the artifact sits under `n_symbols_at_least_as_extreme_two_sided`, an
   unrelated null-distribution count. It wrote "every GPL3290 contrast reported here" instead. `grep`
   for `78 GPL3290|all 78` returns **0**. A reviewer's own figure was declined for want of evidence —
   correct behaviour, not a shortfall.
4. **No recomputation — MET.** No analysis module run, edited or invoked; no new number produced. The
   Methods paragraph says so explicitly: "No reprocessing or sensitivity analysis was run here, so the
   mismatch is disclosed rather than excluded."
5. **No overclaim; hedges intact — MET, parent-checked line by line.** The new Results clause states
   the mismatch "does not show the reported contrast to be wrong". I read **all four** apparent
   deletions in the diff: every one is a **line-wrap artifact of an insertion**, not a content
   removal. The two-colour hedge survives verbatim across the wrap at line 492
   ("…only / the between-group contrast is interpretable"), as do both original CSPG4 explanations —
   only the counting words changed, "Two candidate explanations … neither is settled" → "Three
   candidate explanations … none is settled".
6. **Word caps — MET, with a disclosed self-correction.** G1's first pass hit **main 5,010 > 5,000**.
   It trimmed **only its own newly added redundancy** (a sentence duplicating the Limitations
   statement, and one clause shortened), leaving every pre-existing sentence untouched. Final: **main
   4,994 / 5,000**, abstract 194 / 200, `submission_metrics` exit 0, `0 limit(s) exceeded`.
   ⚠ **6 words of headroom remain** — the next edit to this paper must budget for that.
7. **Linters honest — MET.** `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry`,
   `submission_metrics` all **exit 0**. `lint_consistency` **exit 1** and `lint_citations` **exit 1**
   are both pre-existing: the consistency output is **byte-identical to G1's own pre-edit baseline**
   (`cmp` clean) and names `surface-target` **0** times; its sole ERROR is the separately owned
   MTAP/PRMT5 `2.102` blocker. No gate weakened, relaxed, reordered or edited.
8. **No network, no git write — MET.** G1 performed no git write at all and took its baselines by
   `cp`. It left `research/manuscripts/submission-metrics.json` modified as the
   `submission_metrics.py` side effect and reported it rather than reverting.

## Deviation, and it is mine

**My contract misquoted the target sentence.** It said the paper reads "Two explanations are live";
the committed wording is "**Two candidate** explanations are live and neither is settled here". G1
verified the real string before editing and flagged the discrepancy rather than pattern-matching my
paraphrase. The contract text stands as written; this is the correction, appended not rewritten.

## Out of scope, untouched and routed

- SI line 353, "Two explanations for the platform disagreement are live", concerns the
  **platform-disagreement** section, not the CSPG4 discordance. Left alone. Whether it needs the same
  third explanation is a separate question for the paper's owner.
- Results ~line 407 carries an analogous "Four explanations are live" about the surrogate/tissue
  instrument disagreement — a different disagreement, untouched.

## Standing

The disclosure is accepted and integrated. **This is not publication acceptance:** the paper sits 6
words under its main cap, the SI's parallel sentence is unresolved, and the review's suggested
sensitivity analysis (recomputing GPL3290 contrasts against the three DFSP arrays alone) remains
**undone and out of scope here** — it is a genuine, separately ownable next step, and the manuscript
now says plainly that the mismatch was neither reprocessed nor excluded.
