# N1 — collection and adjudication against `CONTRACT-N1-repurposing-submission-residue.md`

Collected 2026-09-08 10:55-11:00 UTC from retained originals. No re-run, no restart.

## Child identity — from the transcript, full lifetime

| item | measured |
|---|---|
| child | `a585eff566c8eae0d` |
| original JSONL | `N1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a585eff566c8eae0d.jsonl`, **194,517 B**, `cmp`-identical |
| model strings | **`claude-opus-5` only, 0 others** |
| tool pairs | **17** (self-reported 14) |
| **full lifetime** | **10:51:00.205Z -> 10:54:38.244Z** (~3 m 38 s) |

## Both divergences closed

**Item 24 — the completion note is out of the body.** Parent-verified by parsing the file: the string
`*Reference completion note.*` occurs **once in the whole file**, **inside** the editorial HTML
comment, and **zero times outside it**. The comment body contains **no `--` sequence**, so the block
is valid HTML and cannot truncate the comment — a real hazard when moving 1,546 characters into one,
and the child checked it.

**Item 26 — both markers exist.** The comment's first line now opens
`<!-- EDITORIAL, NOT FOR SUBMISSION. STRIPPED AT SUBMISSION: two things are removed from the
submitted manuscript, this editorial comment and Appendix A...`, and Appendix A carries a blockquote
banner immediately under its heading: `> *Stripped at submission.* Appendix A is removed from the
submitted manuscript, together with the editorial HTML comment at the head of this file.` **Neither is
deleted from the repository copy**, per the response's own retention reasoning.

## ⭐ Nothing was lost — verified by the parent, independently

I ran my own whitespace-token multiset comparison of the committed `HEAD` version against the working
file:

```
tokens REMOVED: {} (none)
tokens added: 115  — the two banners and the relocation lead-in
```

**Not one token left the file.** That is the strongest available check that no claim, number, citation
or hedge was touched while 203 words moved across the document, and it matches the child's own
identifier-multiset result (whose only addition was the item number `24` in its lead-in).

## Word counts and gates

`submission_metrics`: main **5,769 -> 5,566** (−203, exactly the note's length — the expected
consequence of moving text into an HTML comment), abstract 238, items 1, refs 22, **0 limits
exceeded**, well under the 8,000 believed limit.

My own gate run: `lint_consistency`, `submission_metrics`, `lint_style`, `lint_claims`,
`lint_submission_residue`, `lint_asymmetry` all **exit 0**. **`lint_citations` exits 1** — pre-existing
and repo-wide, its errors being type-claims with no cached metadata in unrelated campaign reports.
**Not all gates are green.**

⭐ **`lint_submission_residue` did not move** — before and after stdout **byte-identical**, `0 new`,
`0 stale baseline row(s)`. That was the main risk of this edit, since the gate matches todo-marker,
bracket-placeholder and meta-comment shapes; the banners were written to avoid every one.

## A judgement call the child got right

`submission-metrics.json` is modified in the tree because `submission_metrics.py` — a gate the
contract **required** it to run — rewrites the file on every run. N1 **did not revert it**, on the
explicit ground that restoring it would mean writing over a shared repository path, which the
isolation rule forbids. That is the correct reading: the rule tightened after J1 targets the
behaviour, and "putting a file back" is exactly the behaviour it forbids. The parent stages the
regenerated file deliberately here; the whole delta is `"main_words": 5769 -> 5566`.

## Finding routed, not acted on

Review-response item 24 also states *"Twenty becomes twenty-five"* references (line 381 of the
response). The manuscript carries **22**. N1 flagged this rather than touching it, correctly — the
contract forbids changing references. **This is the same divergence class again**: the response
describes a manuscript state that the committed file does not match. Recorded for the canonical-draft
decision, unresolved, and **no reference was added or removed**.

## Standing

**Not publication acceptance.** The reference-count divergence is open, `lint_citations` is red, and
the paper's canonical-draft identity remains the unresolved dependency first raised at E1.

## Retention

`/tmp/claude-0/n1-lane/` **intact, nothing deleted**, pending an exact-directory receipt. In-repo copy
`N1-executed-artifacts/` with a self-exclusive manifest.
