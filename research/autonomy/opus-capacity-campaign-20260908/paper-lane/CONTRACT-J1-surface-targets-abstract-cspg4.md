# J1 — paper-level contract, recorded BEFORE launch

`date -u` **Tue Sep  8 10:01:51 UTC 2026**. Input revision **20f19e5f579db9e0e1706ab4189c434ff726622f**. Same session, one parent/controller, `claude-opus-5`
**medium**, saved first-party subscription — no overage, no credits, no paid fallback, no new
controller. Deadline **2026-09-09T02:37:19Z**, never extended.

## Selected paper and the exact issue — parent-verified

`research/manuscripts/surface-targets/emc-surface-target-landscape.md`, `PUB-SURFACE-TARGETS`,
drafted and unpublished.

**Review item 9** (`…-peer-review-2026-08-10.md:290`) — *"The Abstract omits the paper's one live lead
and leaves a stronger negative impression than the body supports."* Its resolution asks for:

> "One clause in the Abstract's Results, naming CSPG4 as elevated on one array and in the sequencing
> cohort, uninformative on the second, never evaluated at stage 1, and held open. Say in the same
> breath that this is a transcript reading on one peak at n = 4 and one probe at n = 6."

**The review response records this as applied** ("Item 23 … The clause is added"), stating only that
the n = 4 basis was placed in Results and Conclusion instead of the abstract "because the abstract is
at 199 words of 200 and the sentence would not fit."

**Measured by me at the revision above:** `sed -n '/^## Abstract/,/^## Keywords/p' | grep -c -i cspg4`
→ **0**. **There is no CSPG4 clause in the Abstract at all.** The abstract's Results still says only
that "None of eleven therapeutic addresses named by candidate routes was concordantly elevated",
which is the all-negative summary the review objected to.

⭐ **So the paper's abstract still undersells its one live lead, and the response's stated reason —
no room at 199/200 — no longer holds: the abstract now measures 194 of 200.**

## The constraint that makes this real work

**6 words of headroom.** The review's full ask is far larger than 6 words. Fitting it requires
**tightening existing abstract prose**, which is allowed, or reporting honestly that it cannot be done
within the cap.

## Finite acceptance

1. A clause naming **CSPG4** appears in the **Abstract's Results**, carrying as much of the review's
   ask as the cap allows, in priority order: (a) elevated on one array **and** in the sequencing
   cohort; (b) uninformative — not negative — on the second; (c) never evaluated at stage 1;
   (d) held open; (e) the n = 4 / n = 6 transcript basis.
2. **Abstract stays ≤ 200 words** — `submission_metrics.py` is the measure. Main text must stay
   **≤ 5,000** and is currently **4,994**: do not spend main-text headroom on this.
3. **No hedge deleted, anywhere.** Room comes from tightening wording, never from removing a
   qualification, a negative finding or a caveat. The abstract's existing resolution sentence and the
   "surrogate's negatives transferred and its positives did not" conclusion must survive in substance.
4. **No overclaim.** CSPG4 must not read as a positive result: it is elevated on **one** array and in
   the sequencing cohort, **uninformative** on the second, **never evaluated at stage 1**, **held
   open**, at transcript level. If (e) will not fit, the clause must still not imply more confidence
   than the body carries — say "held open" over any wording that suggests a finding.
5. **If items (a)–(d) cannot fit within 200 words without deleting a hedge, STOP and report that
   exactly**, with the word counts you measured. A documented cap stop is a successful result.
6. Linters run and reported honestly with exit codes. ⛔ A tripped gate is a finding to report, never
   a reason to weaken, relax, reorder or edit a gate.
   ⚠ **`lint_citations` fails repo-wide at exit 1 and was NOT fixed by any recent work** — it is
   pre-existing and not yours. Establish a baseline and attribute honestly. **Do not describe all
   gates or tests as green.**

## Explicitly out of scope

⛔ **No recomputation and no new number.** The DFSP-only sensitivity analysis remains **out of scope
and undone** — this contract does not admit it. ⛔ No edit to the SI, to any other manuscript, to the
registry or to any code. ⛔ No source retrieval, no network, no denied-route retry. ⛔ No git write of
any kind. ⛔ No `scripts/preflight.sh`, no GPU, no paid API. G1, H1, I1 and F1 contracts are closed
and are not reopened.

## Isolation and retention

Work from **task-scoped copies under `/tmp/claude-0/j1-lane/`**; the parent alone integrates.
Preserve there, before any cleanup: pre-edit manuscript, post-edit manuscript, unified diff, and every
linter's stdout **and** stderr with exit code echoed, plus a baseline you take by `cp` or
`git show HEAD:<path>` — **never** by stashing the shared tree, which may carry another writer's
work. ⛔ **DELETE NOTHING**, including your own lane: cleanup requires a directory-specific local
collector receipt that does not exist yet.

## Stop conditions

The cap stop in (5); the issue already being resolved on reading; any step requiring a prohibited
action; or **~40 tool calls / ~40 minutes**. Returning early with a supported result or block is
success; padding is not.
