# N1 — paper-level contract, recorded BEFORE launch

`date -u` **2026-09-08 ~10:56 UTC**. Input revision **f83e6f77646d4cb1eb360690d14b8cbd3a073098**. Same parent/controller and session,
`claude-opus-5` **medium**, existing first-party saved subscription — no paid fallback, no overage, no
credits, no new controller. Deadline **2026-09-09T02:37:19Z**, never extended.

## Paper — the next eligible unfinished draft

`research/manuscripts/repurposing/repurposing-hypotheses.md`, endpoint `PUB-REPURPOSING`, state
**drafted, unpublished**. Eligible: drafted is not an exclusion. Not held, not frozen, not W25, not the
NR4A Perspective, not P6.

**Surface-targets is set down** with its disposition recorded — its remaining items are the tested and
recorded item 44 blocker, the pre-existing repo-wide `lint_citations` failure, the abstract's
n = 4 / n = 6 residue, and the out-of-scope DFSP sensitivity analysis. None is ready unblocked work.

## The exact issue — two divergences, parent-verified at the revision above

The 2026-08-10 review response records two submission-readiness items as **applied**. Both are
**absent from the committed manuscript**:

1. **Item 24.** The response states the reference completion note is *"removed from the body of the
   manuscript and its content moved into the editorial comment, which is stripped at submission; it is
   editor-facing and states that the reference list is not submission-ready, which is a repository
   fact rather than a claim a published paper should carry."*
   **Measured:** the note is still **in the body**, at line 655, opening *"Reference completion
   note. Author lists, journal titles, volumes and pages are taken from..."*.

2. **Item 26.** The response states Appendix A and the HTML comment are *"marked as stripped at
   submission, in the first line of the editorial comment and in a banner on Appendix A"*.
   **Measured:** `grep -i "stripped at submission"` over the manuscript returns **nothing**. There is
   no such banner and no such first line.

⭐ **So a paper that is otherwise submission-shaped still carries an editor-facing note in its body
and lacks the markers that tell a reader which sections are not part of the submission.** These are
exactly the defects the review raised and the response recorded as fixed.

## Finite acceptance

1. **Item 24:** move the reference completion note **out of the body** and into the editorial HTML
   comment, preserving **every word of its content** — it is a repository fact and must not be lost,
   only relocated. Nothing about the references themselves changes.
2. **Item 26:** add the **banner on Appendix A** and the **first line of the editorial comment**
   naming both Appendix A and the comment itself as stripped at submission. **Do not delete either**
   from the repository copy — this repository keeps one file per deliverable, and the response's own
   reasoning for retaining them stands.
3. **⛔ No scientific claim, number, citation, hedge or reference may change.** This is submission
   hygiene only. The class-evidence disclosure, both in-silico negatives, the abstract-level
   labelling and every qualification stay exactly as they are.
4. **Word counts:** report before and after. The paper is a CROH-Review; text moved into an HTML
   comment leaves the counted body, which is the point — confirm with `submission_metrics.py` and
   report honestly if any limit moves.
5. Gates run and reported with exit codes. ⛔ A tripped gate is a finding to report, never a reason to
   weaken, relax, reorder or edit a gate. ⚠ **`lint_citations` fails repo-wide at exit 1,
   pre-existing** — attribute it, and **do not describe all gates as green**.
   ⚠ `lint_submission_residue` is the gate most likely to move here: report its before/after exactly.
6. If either item cannot be done without changing a scientific claim, **STOP and report that**. A
   supported stop is a successful result.

## ⛔ Isolation

**You may not write, copy, move or restore any file over a shared repository path for a baseline,
comparison or test.** Baselines go **out** to `/tmp/claude-0/n1-lane/` via `git show HEAD:<path> >` or
by copying out — never in. Your only repository write is
`research/manuscripts/repurposing/repurposing-hypotheses.md`. **No git write** — read-only git only.

## Out of scope

⛔ No other manuscript, SI, registry, figure or code edit. ⛔ No network, no source retrieval, no
denied-route retry, no paid API, no GPU, no `scripts/preflight.sh`. ⛔ No reopening of E1, F1, G1, H1,
I1, J1, K1, L1 or M1, no DFSP recomputation, no item 44 work, no global census or review-all sweep.
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source or measurement.

## Retention

Under `/tmp/claude-0/n1-lane/`: pre-edit manuscript, post-edit manuscript, unified diff, and every
gate's stdout **and** stderr with exit code echoed. ⛔ **DELETE NOTHING**, including your own lane.

## Stop conditions

Acceptance 6; either item proving already done on reading; any step needing a prohibited action; or
**~40 tool calls / ~40 minutes**. Early with a supported result or block is success; padding is not.


---

# Timing qualification, appended 2026-09-08 11:16 UTC — original header preserved

The header's `date -u` of **"~10:56 UTC"** is inconsistent with the original events and is corrected
here rather than rewritten: the contract commit `d8fab1c8` landed at **~10:50 UTC**, the child ran
**10:51:00.205Z -> 10:54:38.244Z**, and the parent's model verification was at **10:51:23 UTC**. The
"~10:56" was an approximation written into the text ahead of the clock reading. **No contract term,
bound, acceptance item or stop condition changes.**
