# O1 — collection and adjudication against `CONTRACT-O1-repurposing-imatinib-registry-claim.md`

Collected 2026-09-08 11:05-11:10 UTC from retained originals. No re-run, no restart.

## Child identity — from the transcript, full lifetime

| item | measured |
|---|---|
| child | `a24f906c6b0bf30f6` |
| original JSONL | `O1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a24f906c6b0bf30f6.jsonl`, **162,351 B**, `cmp`-identical |
| model strings | **`claude-opus-5` only, 0 others** |
| tool pairs | **15** (self-reported 10) |
| **full lifetime** | **11:02:28.249Z -> 11:04:48.031Z** (~2 m 20 s) of a ~40 min bound |

## The false claim is gone

**Before:** *"It is the only candidate flagged as eligible to graduate into the cited clinical
registry, pending clinician review."*

**After (committed, lines 420-424):** *"It is not a hypothesis awaiting promotion into the project's
cited clinical registry: it is already listed there, among the emerging treatments, as "Imatinib (KIT
inhibitor) — only for KIT-mutant EMC", with the status "Off-label; single published case
(biomarker-restricted)" and attributed to the same case report [7], which the entry itself describes
as a single case. What remains open is the clinical route set out above, not admission to the
registry."*

Parent-verified: `grep -c "eligible to graduate"` -> **0**; `grep -c "not a hypothesis awaiting
promotion"` -> **1**. The registry terms quoted match `emc-clinical-registry.json` verbatim, and
reference [7] was already cited in the preceding sentence — **no source was added**.

## Constraints held — each checked, not assumed

| constraint | verification |
|---|---|
| registry untouched | `git status` shows **0** modifications to `research/data/emc-clinical-registry.json`; `git diff --stat` empty |
| no tier or rule changed | the diff contains **0** lines matching `T3`, `T2`, `may migrate` or `firewall` |
| no reference added | reference count **22 before, 22 after** |
| general rules left alone | lines 272 and 577 are tier rules naming no agent; O1 read them, judged them not false, and said so — the contract's acceptance 2 asked exactly that |
| isolation | no git write; baselines taken out to the lane |

Gates, my own run: six **exit 0**; **`lint_citations` exit 1**, pre-existing and repo-wide, naming
this manuscript **0** times. **Not all gates are green.** Main text 5,566 -> **5,619**, within limits.

## ⭐ O1 corrected my contract's premise, and it was right to

**My contract asserted the manuscript grades imatinib T2.** I took that from the review response, not
from the manuscript. **In the committed text imatinib is graded T3** — line 416 "candidate at T3,
resting on direct EMC clinical evidence", line 523 "only imatinib reaching T3" — which I confirmed
independently.

**Consequence:** the "T2 agent sitting in a T3-only registry" tension **does not arise in the
manuscript's current text**. At T3 the firewall rule and the registry entry are internally consistent,
so the corrected sentence needed no statement of tension to be accurate. O1 established this and
declined to state a tension that is not there — the better result than following my framing.

**My contract's premise is corrected here rather than repeated.** The instruction it carried — do not
adjudicate the tension, do not change any tier — remains right, and O1 obeyed it.

## Finding routed, not acted on

**The first half of review item 1 is also unapplied.** The response describes regrading imatinib to
**T2**, restating §2.2 as a three-valued scale with "nothing reaches T3", and propagating that through
the abstract, Table 1, §5, §6 and §2.7. The committed manuscript still carries the **four-valued T0-T3
scale** with imatinib at T3.

That is a **tier change**, which this contract forbids and which O1 correctly did not make. It is
recorded for a separate decision — and it is the **fourth** divergence found on this paper between the
review response and the committed file, after the class evidence (E1), the completion note and the
"stripped at submission" markers (N1), and the reference count. **The canonical-draft identity
question, first raised at E1, is now the paper's dominant unresolved dependency**, and item-by-item
correction is reaching its limit: a regrade touching the abstract, two tables and four sections is not
a defect to patch but a version decision to take.

## A judgement call, same as N1's and again correct

`submission-metrics.json` is modified because the contract required running the gate that rewrites it.
O1 did **not** revert it, on the ground that restoring a file over a shared path is what the isolation
rule forbids. The parent stages the regenerated file deliberately; the delta is one line,
`main_words` 5566 -> 5619.

## Standing

**Not publication acceptance.** The T3/T2 regrade is unapplied and unresolved, the reference-count
divergence is open, `lint_citations` is red, and the canonical-draft question is unresolved.

## Retention

`/tmp/claude-0/o1-lane/` **intact, nothing deleted**, pending an exact-directory receipt. In-repo copy
`O1-executed-artifacts/` with a self-exclusive manifest.
