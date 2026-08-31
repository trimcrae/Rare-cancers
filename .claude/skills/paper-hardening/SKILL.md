---
name: paper-hardening
description: The repeatable cycle that takes a manuscript from "the science is done" to "submission ready" — iterated blind adversarial review rounds, applied and re-run until convergence, WITHOUT the paper ballooning in length. Load when starting or continuing a hardening cycle, before launching a review round, before applying a round's findings to the prose, before deciding whether another round is warranted, and any time you are about to add a sentence to a manuscript that is already under review. Covers: the per-round word budget as a hard gate on VENUE-CAPPED submissions and why it does not apply to aiXiv, which caps nothing; why thirteen rounds grew one article monotonically 2,914 to 5,976 words; a correction REPLACES text and never appends; the five blind seats and the regression lens that found the only round-13 blocker; review a PINNED COMMIT, never the working tree; refute by default; why a verifier's pasteable fix is not pre-verified prose; the one-of-a-pair defect class (seven found, the seventh inside the test selector itself); mutation-testing every guard you write, single-site mutations included; the four process defects that cost real rounds; and the convergence test — no blockers on the posted commit, with the open P1 count reported beside it rather than gating (changed 2026-08-29). Commit and gate mechanics live in `repo-gates`, not here.
---

# Hardening a paper: adversarial rounds without prose inflation

Measured 2026-08-22 across rounds 8–13 of the fusion-junction ASO submission
([`fusion-junction-aso-journal-article.md`](./research/manuscripts/aso/fusion-junction-aso-journal-article.md),
review commits `b8da13da` → `40fc3c82`). ⚠ Two spans are quoted below and they are not the same
one: the REVIEW runs from `b8da13da`, round 8's commit, while the word counts run from `c3909ed8`,
the last commit that touched the article BEFORE any round saw it. This is the counterpart to
**`repo-gates`**, which owns commit gates,
preflight, linters and the reviewer-AI block. ⛔ **Nothing about committing is restated here — load
`repo-gates` for that.**

⚠ **Not a `pinned-figures.json` target.** Every figure below names the commit or ledger that is its one
home; correcting one means correcting it there and registering the old value per CLAUDE.md rule 1.3.

---

## 1 · ★★ LENGTH IS A GATE, NOT AN OUTCOME

**Thirteen rounds closed real defects and grew the paper every single time.** Measured over
`c3909ed8` → `40fc3c82`: main text **2,914 → 5,976 words**, whole file **3,760 → 7,035**,
**MONOTONICALLY — not one round shrank it.** §5 alone went **682 → 1,749 words**, reaching **1.89× §3**
in a paper where §3 carries the selection result. (Reproduce: `git show <PIN>:<path> | wc -w`.)

⛔ **THE GROWTH WAS NOT A SIDE EFFECT — IT *WAS* THE METHOD.** Each P1 was closed by **appending a
qualifying clause** instead of editing the sentence that was wrong. That is why the curve is monotone:
appending always passes the finding, and nothing in the loop was ever asked what it cost.

**Three separate hostile-referee seats independently reported the same verdict: the measurement layer is
finished and the prose layer is not — *because it is still being edited*.** Convergent, independent, and
about the process rather than any one sentence, which is the strongest signal this loop produces.

### The rule

- **⛔ A ROUND ON A VENUE-CAPPED SUBMISSION DECLARES A WORD BUDGET BEFORE IT STARTS, AND A ROUND THAT
  EXCEEDS IT IS NOT DONE.** The budget is declared before the seats launch, so it cannot be
  rationalised from the findings. Measure main text and each section, both at the pin and after
  application.
  - **⛔ NOT ON aiXiv (trimcrae, 2026-08-22: *"We don't need a word budget on aiXiv submissions"*).**
    aiXiv imposes no length limit of any kind — `SubmissionCreate.abstract` is a nullable string with
    no `maxLength`, and there is no page or word cap — so a numeric cap on an aiXiv-targeted round is
    a constraint this repository invented. Measured that day: a round trimmed **six words** to meet a
    self-declared +60, which bought the paper nothing and cost a revision cycle.
  - ⚠ **WHAT THE BUDGET WAS ACTUALLY FOR SURVIVES, AND IT IS NOT A VENUE LIMIT.** The thirteen-round
    evidence above is a *prose* failure, not a length-limit failure: every P1 was closed by appending
    a qualifying clause, which is why §5 reached **1.89× §3** in a paper where §3 carries the result.
    So on an uncapped venue: **still measure at the pin and after, still report the delta, and the
    replace-not-append rule below is the gate.** A round that grows the paper while leaving the
    wrong sentences in place has failed whether or not a number was exceeded.
  - ⚠ **AND UNCAPPED IS NOT A LICENCE TO PAD.** If a round's delta is large, that is a finding about
    the round — say so and say why — not a fact to leave unremarked because nothing forbade it.
- **⛔ A CORRECTION REPLACES TEXT; IT DOES NOT APPEND TO IT.** If the sentence is wrong, rewrite the
  sentence. A qualifier bolted onto a wrong sentence leaves the wrong sentence in the paper and adds a
  second one that argues with it.
  - **★★ ENFORCED AS OF 2026-08-31 BY A LENGTH RATCHET, BECAUSE THIS RULE WAS CORRECT AND MEASURED BY
    NOTHING FOR NINE DAYS.**
    [`test_a_hardening_round_may_not_grow_the_paper.py`](./research/manuscripts/tests/test_a_hardening_round_may_not_grow_the_paper.py)
    holds a main-text word CEILING per outgoing paper: it may fall freely and may not rise, and its
    remedy text says in words that raising it to fit an edit is the self-serving amendment
    `amendment_guard` exists to catch. The count comes from `submission_metrics.measure` rather than
    a second counter — ⚠ the first draft counted its own way and got **4,120 against the
    repository's 3,793**, an 8.6% disagreement that would have made the ceiling a bound on a
    quantity nobody reports.
    ⚠ **trimcrae, 2026-08-31, which is why it exists:** *"If we are going from 6 pages to 8 pages,
    that's a 33% increase just in response to reviewer feedback. That's clearly over hedging and
    scope creep. Not only should we aggressively cut the fat, we need to be more strict in our
    process about adding more length to satisfy one of our internal reviewers."*
    ⭐ **AND THE ROUND THAT TRIGGERED IT IS THE PROOF THE RULE WORKS.** Round 26's two prose
    corrections were first written as EXPANSIONS — *"covers every position of GRCh38"* → *"covers
    GRCh38 end to end, skipping only windows that carry an ambiguous base"* — costing 13 words and,
    through re-wrapping, a whole page; an hour then went into cutting good prose to fund them, and
    **four of those six cuts were wrong**, two breaking guards that deliberately pin their wording
    and one INVERTING a provenance sentence into a false statement. Rewritten as REPLACEMENTS
    (*"covers unambiguous GRCh38"*) the identical corrections came in **11 words shorter than the
    text they replaced**, and the page came back with nothing cut at all. ★ **The finding was never
    what cost the page. The prose was** — so the first move on a length failure is to re-read your
    own repair, not to go hunting for fat.
- **★ DERIVATIONS MOVE TO THE EXTENDED REPORT; THE BOUND STAYS IN THE PAPER AS ONE SENTENCE.** The
  arithmetic behind a bound is not the bound. A short paper's job is to state what is bounded and at
  what level, and to point at where it is derived.

### ⚠ Only three things may be cut, and you must know which you are cutting

| | class | test | cuttable |
|---|---|---|---|
| 1 | **derivation** | the arithmetic behind a bound | ✅ move it to the extended report |
| 2 | **duplication** | the same statistic stated in two sections | ✅ keep one, and see §6 — deleting one of N sites is how drift starts |
| 3 | **meta-commentary** | a sentence *about* what the paper does and does not claim | ✅ cut |
| 4 | **a bound** | a number, an interval, a condemnation, a concession | ⛔ **NEVER, to hit a budget, without saying explicitly which bounds came out** |

⛔ **A BUDGET IS NOT A LICENCE TO DROP EVIDENCE.** If a budget can only be met by removing a bound, the
removal is a finding in its own right and goes in the round's record by name. Silently trimming a
concession to make a length target is the one failure this rule must never cause — and the concession
is usually the sentence that costs the most (round 13 restored one: the strongest null sits inside the
panel's own Wilson interval at the adopted ten-base-pair cut, 40.6 % in 38.9–52.9 %).

---

## 2 · What a round looks like — the runbook

1. **Declare the word budget** (§1) and write it down before anything launches — **on a venue-capped submission**. On aiXiv there is no cap: still record the word count at the pin, and report the delta at the end.
2. **Pin a commit** (§3). Every seat reviews that SHA and nothing else.
3. **Launch N blind seats with distinct lenses** (§4). No cross-talk.
4. **Synthesize by grade** — blocker / P1 / P2 — and note where seats converged independently.
5. **Verify every finding against the artifacts** (§5). Default REFUTED.
5a. **Record `introduced_by` on every blocker** (§5a). One `git log -S` per finding. It is a
   diagnostic about the PROCESS and it never decides what may ship.
6. **Apply survivors as REPLACEMENTS** (§1) — inside the budget where one applies, and replacing
   rather than appending in every case, which is the gate that does not depend on a venue.
6a. **⛔ EVERY EDIT PASSES THE REPAIR GATE BEFORE IT LANDS (§5b). A ROUND MAY NOT SHIP AN UNREVIEWED
   REPAIR.** This is the step the series did not have, and it is where every recent blocker came
   from.
7. **Regenerate downstream artifacts with the chain script** (§7c), never by hand.
8. **Gate** — `repo-gates`.
9. **Commit with a message whose claims match its diff** (§7b).
10. **Decide: another round, or converged** (§8).

---

## 3 · ⛔ REVIEW A PIN, NEVER THE WORKING TREE

**Round 13's seats hit tree drift mid-review — the article changed under them at `06:30:10Z` — and had
to re-derive findings they had already written.** A seat reading a moving file cannot say which version
its quotation came from, so every finding it files becomes unfalsifiable at exactly the moment you try
to verify it.

- Give every seat a **commit SHA** and the exact command: `git show <PIN>:<path>`.
- **Tell them the tree may drift and that the pin is the subject** — otherwise a seat that notices a
  discrepancy will "helpfully" reconcile against the live file.
- The synthesis, the verification and the word counts all run against the same pin.

---

## 4 · Seat design that worked

**Five blind seats per round, one lens each, all on the same pinned commit:**

| seat | lens | what it is for |
|---|---|---|
| 1 | **regression on the previous round's repairs** | ⭐ **found the only blocker in round 13**, and six of ten findings were damage from the previous round's own fix |
| 2 | **arithmetic against committed artifacts** | every printed number re-derived from the file that produces it |
| 3 | **statistics and experimental design** | power, familywise level, what a gate actually bounds |
| 4 | **citations, build and gates** | provenance, the built PDF, which instruments read this document |
| 5 | **hostile referee** | one verdict: accept / revise / reject, with reasons |

**Round 13 counts: 1 blocker, 8 distinct P1s across five seats — and three seats filed the same §6
defect independently, from different artifacts.** ★ **Independent convergence is the signal that a
finding is real.** A defect reached by three lenses that could not see each other is not a matter of
taste; a defect only one seat can see usually is.

⛔ **THE REGRESSION SEAT IS NOT OPTIONAL ONCE ROUND 2 EXISTS.** In round 13 it was the highest-yield
lens in the round. The failure mode it catches — a repair that invents a new defect — is invisible to
every other lens, because the other lenses read the paper as it now stands and the repair looks
deliberate.

### 4a · ⛔⛔ A SEAT THAT FINDS NOTHING HAS SUCCEEDED, AND THE PROMPT MUST SAY SO IN WORDS

**Every seat prompt ends with this clause, verbatim, and no seat is dispatched without it:**

> Returning **no findings** is a complete and expected answer. Do not lower your bar to produce one.
> If your lens turns up nothing on this commit, say so plainly and stop — that is the round's most
> valuable result, not its least.

⚠ **THIS IS NOT ENCOURAGEMENT, IT IS A MEASURED INTERVENTION, AND IT IS THE ONLY ONE IN THE
2026-08-27 PRIOR-ART SURVEY WITH AN EFFECT SIZE ATTACHED.** SciIntegrity-Bench built 33 scenarios in
which honest acknowledgement of failure is the *only* correct answer while completing the task
requires misconduct — 231 runs across 7 frontier models, **34.2% overall integrity problem rate, no
model at zero, and all seven synthesised data rather than admit infeasibility.** ⭐ **Removing
explicit completion pressure cut UNDISCLOSED fabrication from 20.6% to 3.2% while the underlying
synthesis rate was unchanged** — i.e. the pressure does not change how often a model reaches for
something it cannot support, it changes whether it tells you. A one-line prompt clause is therefore
worth more here than another gate, and it costs nothing.
⚠ **SEARCH-grade** (arXiv:2605.10246; arxiv.org is blocked at this sandbox's egress). The effect size
is safe to ACT on and is not safe to QUOTE in a manuscript until somebody fetches the paper —
[`method-watch-autonomy-prior-art-2.md`](../../../research/method-watch-autonomy-prior-art-2.md) §5.

★ **AND THIS REPOSITORY REACHED THE SAME PLACE FROM THE SYMPTOM SIDE, WHICH IS WHY THE FINDING
LANDS RATHER THAN BEING INTERESTING.** §5 already carries trimcrae's own reading — *"if it's coming
back as having 10 blockers… that strikes me as agents making things up to fill a quota"* — and §8a
already says a blocker count that stops falling means you are sampling surfaces. Those two describe
what a pressured seat LOOKS like afterwards. This clause is the upstream half: **stop applying the
pressure, and there is less to detect.**

⛔ **WHAT COUNTS AS PRESSURE, so the audit is repeatable rather than a matter of taste.** Any of
these in a seat prompt, however incidentally phrased:
- a **count** — "find the top N", "at least three", "list ten"; the number becomes the target
- an **expectation of yield** — "this seat has historically found the most", "there will be defects"
- a **completion framing** — "do not return until", "keep looking until you have", "your job is to
  produce a findings list"
- a **comparison** — telling a seat what a sibling seat found, before it has finished

✅ **What is NOT pressure and stays**: the lens itself, the pinned commit, the artifact paths, the
refute-by-default standard of §5, and the requirement to say what it looked at. Constraining HOW a
seat looks is the point; promising WHAT it will find is the defect.

⛔ **AND THE HIGHEST-RISK COPY IS IN THIS SKILL, NOT IN A PROMPT.** §4's seat table records yield
history — *"found the only blocker in round 13"*, *"six of ten findings"*, *"the highest-yield lens
in the round"* — and that history is **for the DRIVER, choosing which seats to run.** ⛔ **It must
never be repeated to the seat itself**, where it stops being evidence and becomes a quota with a
precedent attached. The same goes for telling a seat what a sibling seat has already filed.

⭐ **AUDITED 2026-08-27, and the other two prompt homes came back CLEAN — which is a reading, not an
assumption.** `research/autonomy/routine-prompts.md`'s driver prompt and
[`research-loop`](../research-loop/SKILL.md) were both read for the four shapes above and carry
none. The driver prompt already ends with the right instinct in its own words: *"If the cycle did
nothing, say that plainly rather than describing what you looked at."* Its one completion framing —
*"a cycle without [a receipt] has failed however much it wrote"* — is a **deliverable requirement,
not a yield expectation**, and stays: it demands a record of what happened, never a finding.

### 4b · ★ THE EXTERNAL SEAT — aiXiv's attack review, and exactly which seats it can replace

aiXiv runs an adversarial reviewer over HTTP, so part of a round's model spend can be moved off our
budget. Client: [`scripts/aixiv_review.py`](./scripts/aixiv_review.py). API surface read at primary
source 2026-08-22 into `literature/aixiv-api-surface-2026-08-22/` on `literature-cache`.

⛔ **IT CANNOT REVIEW A PINNED COMMIT, AND THAT IS A SPEC FACT RATHER THAN A PREFERENCE.**
`POST /api/start_attack_review` requires `aixiv_id` **and** `aixiv_url`, and the scheduler endpoint
returns "submissions with status 'Under Review'" — the reviewer is keyed to a paper **already on
aiXiv**. There is no endpoint that takes a local file. So §3's "review a pin, never the working tree"
cannot be satisfied by this seat: using it means the text has been uploaded to a third party first,
which is an outward-facing act (CLAUDE.md §3) and never a side effect of running a round. The client
refuses to submit without an explicit acknowledgement flag for that reason.

**What it can and cannot stand in for, graded on this loop's own measured record (round 13):**

| seat | replaceable by the external reviewer? | why |
|---|---|---|
| 1 · regression on the previous round's repairs | ⛔ **no** | It needs the previous round's diff and findings. An external engine sees one PDF, once, and has no prior. This is the seat that found round 13's **only blocker** and 6 of 10 findings. |
| 2 · arithmetic against committed artifacts | ⛔ **no** | Re-deriving a printed number requires the repository file that produces it. |
| 4 · citations, build and gates | ⛔ **no** | Needs the built PDF, the citation ledger and which instruments read the document. |
| 3 · statistics and experimental design | ✅ **yes** | Judged from the text alone; no repository access needed. |
| 5 · hostile referee (accept/revise/reject) | ✅ **yes** | This is the shape aiXiv's reviewer already emits. |

⭐ **So the saving is real and it is bounded: two of five seats.** The three that cannot move are
exactly the three that read this repository, which is also why they are the ones that catch things a
journal referee would not. **Swapping seat 1 out to save spend would remove the highest-yield lens in
the series** — that is the trade being made, and it must be made explicitly, not by convenience.

⚠ **PASS `--seed` ON EVERY EXTERNAL REVIEW.** §3 exists so that every finding is falsifiable against
one fixed text; an unseeded reviewer re-run on the same version gives a different answer and there is
no way to tell genuine drift from engine variance. Record the seed in the round's notes with the pin.

⚠ **AN EMPTY `review_list` IS AN ABSENT READING, NOT A PASS.** `fetch` says so in those words. And
`Review.review_results` is typed `string` in the spec, so store it verbatim and parse best-effort —
assuming a structure nobody checked is the "populated field is not a measured one" failure (CLAUDE.md §4).

⚠ **THE REVIEW SERIES IS ITSELF A ONE-OF-A-PAIR RISK (see §6).** Rounds 1–7 all reviewed
`fusion-junction-aso-research-article.md`. The short journal article had **zero coverage until round
8**, which then found **24 blocker-grade charges** against it — a document nobody had ever reviewed,
inside a submission seven rounds deep. **Enumerate what each round's seats actually read.**

---

## 5a · ★★ RECORD WHERE EVERY BLOCKER CAME FROM — THE MEASUREMENT THAT WOULD HAVE STOPPED THIS SERIES

**⛔⛔ MOST BLOCKERS IN THIS SERIES ARE WRITTEN BY THE PREVIOUS ROUND'S OWN REPAIRS, AND NOBODY
MEASURED IT FOR FOUR ROUNDS.** Round 27 of PUB-ASO, 2026-08-31, traced with one command per finding:

    git log --oneline -S "<the offending string>" -- <the manuscript>

Both of round 27's prose blockers return exactly two commits: `a294fee68` (round 26) **introduced**
them, `fade4a548` (round 27) removed them. The third was not a paper defect at all — an unpublished
Zenodo DOI, an outside-world state no round could clear. ★ **So ZERO of round 27's blockers were
pre-existing defects the earlier rounds missed.** §8's own record says the same of round 24: six of
its seven were prior repairs. The paper is not decaying and the seats are not filling a quota — the
loop is breaking the paper with its own fixes.

★ **SO EVERY BLOCKER CARRIES `introduced_by`, one of three values**, derived rather than judged:

| value | how it is established |
|---|---|
| `pre_existing` | `git log -S` shows the text predates the first round of this series |
| `prior_repair` | it shows a round's own repair commit introduced it — **name the commit** |
| `not_a_paper_defect` | the artifact is correct; the defect is an outside-world state or a tooling record (§8.0a) |

⛔⛔ **AND IT NEVER, EVER GATES WHAT MAY SHIP.** A false sentence is false whether it was written last
week or last month, and a reader is misled exactly as much either way. `introduced_by` is a
diagnostic about the PROCESS, in the same family as `route_advanced: none` — an alarm, never a
licence. ⚠ *The first version of this section proposed exactly that licence — "converged = zero
blockers of pre-existing origin" — and it was wrong: it would have loosened the one gate that is
working, in the cycle that gate was blocking, which is what `amendment_guard` exists to refuse.
Recorded because the wrong version is instructive: the pull toward weakening a bar arrives disguised
as a process insight.*

★ **WHAT THE NUMBER IS FOR: when a round's blockers are mostly `prior_repair`, STOP EDITING.** That
is §8a's rule with a measurement behind it at last. Another round against undisciplined edits
converts repair damage into more repair damage; the answer is §5b, not a rerun.

---

## 5b · ⛔⛔ THE REPAIR GATE — NO EDIT LANDS UNREVIEWED

**THE STRUCTURAL DEFECT THIS CLOSES, STATED PLAINLY: a round REVIEWS THE PAPER AND NEVER REVIEWS THE
REPAIR.** Five blind seats read 3,800 words at real cost. The four-word replacement that goes in
afterwards is read by nobody until the next round, five more seats and a day later — by which time
it is in the manuscript, in four PDFs, in the .docx, and possibly in a published archive.

⛔ **AND IT IS WHY THE SERIES CANNOT CONVERGE.** `publish_bar.clause_1` requires zero blockers **on
the commit being posted**. Any round that finds something produces repairs, which produce a new
commit, which requires a new round. If a round's repairs reliably introduce a defect — and across
rounds 24 and 27 they do — the loop cannot terminate by construction. **Twenty-seven rounds on a
six-page paper is that fact, not bad luck.** The fix is not to relax the clause; it is to stop
repairs from introducing defects, after which a clean round is reachable and the clause terminates
on its own.

★★ **THE GATE. Every proposed manuscript edit is checked on two axes BEFORE it is applied, and both
are named in the round's record:**

| | axis | the question | the measured failure it catches |
|---|---|---|---|
| **a** | **against its source** | does the artifact this new sentence cites actually say this? Re-derive the number, re-read the verbatim. | Round 27's five-steps blocker: the paper said steps 2–5 are laboratory work; the deposited verbatim of PMID 39912803 calls 4 and 5 risk assessment and management. One field, unread. |
| **b** | **against every other site of the same fact** | does any other sentence in the outgoing set state this same quantity or relation, and do they now agree? | Round 26's gap-length blocker: it wrote "more than the seven-to-ten" 130 lines below the paper's own "with seven to ten the working range", from the same citation. Two sentences, one fact, contradicting. |

⭐ **BOTH MEASURED FAILURES ARE CAUGHT BY ONE OF THE TWO AXES**, which is why this is a gate and not
an exhortation. Axis (b) is CLAUDE.md rule 1 — one fact, one place — pointed at the edit instead of
at the repository.

⛔ **A ROUND MAY REPORT AND A ROUND MAY REPAIR, BUT THE REPAIR IS A SEPARATE, GATED UNIT.** §5 already
says verification is a separate pass from application; what was missing is that application had no
pass of its own. A repair that has not been through (a) and (b) is an unreviewed claim entering a
paper under review.

⚠ **THIS DOES NOT REPLACE THE REGRESSION SEAT.** That seat catches damage that has already landed;
this gate stops it landing. Keep both — the seat is now the check on whether this gate is working.

---

## 5 · Verification — refute by default

- **⛔ REFUTE BY DEFAULT. EVERY FINDING NAMES THE ARTIFACT PATH AND FIELD THAT CONFIRMS IT.** Anything
  that will not reproduce is dropped, or kept as **PLAUSIBLE** with the observation that would settle
  it. **The most-promoted blocker of round 8 was refuted on inspection** (`5faf0f41`): it had confused a
  duplex-**LENGTH** metric with the per-mismatch cleavage-**RATE** multiplier — different quantity,
  different citation. A ledger's own ranking is not evidence; four of five blocker charges in the
  round before it did not survive verification either.
- **⛔ A VERIFIER'S PASTEABLE FIX IS NOT PRE-VERIFIED PROSE.** A refuter's suggested sentence —
  *"at any run length 181 of the 190 pair a parent"* — was applied **verbatim** and reintroduced an
  error the repository had already corrected once: **181 is the count at a SIX-base-pair cut**, not a
  count that holds at any run length. ★ **Re-derive every number in any proposed replacement**, from
  the artifact, before it enters the manuscript. A fix arriving in quotable form is the most dangerous
  kind, because it reads as already checked.
- **⛔⛔ VERIFY EXISTENCE *AND* SEVERITY — AND THE SECOND ONE IS THE ONE THAT GETS SKIPPED.**
  ⚠ *Measured round 9, on the ASO journal article, 2026-08-27.* Every one of eight findings was
  checked against the committed artifacts and every one passed, because the seats were quoting
  accurately. The check answered *does the text actually say this?* It never asked *is this a reason
  to stop the paper?* — so **severity was inherited from the seat's own heading**, and eight
  suggestions were applied as blockers.
  ★ **A SEAT'S GRADE IS NOT EVIDENCE; IT IS THE THING UNDER REVIEW.** A seat is instructed to emit a
  `BLOCKERS:` section, so five seats will produce blockers. A synthesis that reads those headings as
  data has outsourced the judgment that is the synthesis's whole job.
  ★★ **THE TEST, APPLIED PER FINDING BEFORE ANY PROSE IS TOUCHED: would a reviewer STOP this paper
  for it, or SUGGEST it?** A wrong fact, a claim the paper's own text contradicts, and an internal
  contradiction stop a paper. A completeness wish, a *"you should also measure X"*, and a caveat the
  body already carries elsewhere are suggestions — record them, do not apply them.
  ⛔ **AND THE COST IS NOT WASTED EFFORT, IT IS DELETED GOOD CONTENT.** Applying all eight took that
  paper from 4,614 to 5,563 words and from six typeset pages to eight, against a **hard 6-page budget
  backed by a per-page charge**. An hour then went into cutting cited case reports, the coverage
  arithmetic and a paragraph of the Introduction to fund additions that should not have been made.
  Every individual cut looked defensible. **A §1 word budget does not protect you here — it makes the
  over-grade expensive rather than preventing it.**
  ⚠ **The count itself is the smoke alarm** (trimcrae, that day): *"if it's coming back as having 10
  blockers… that strikes me as agents making things up to fill a quota."* Late rounds on a paper that
  has already survived eight of them should produce FEW blockers. A high count is evidence about the
  synthesis before it is evidence about the paper.
- **★ VERIFICATION IS A SEPARATE PASS FROM APPLICATION.** The round-8 ledger applies nothing: the
  ledger is the deliverable and application is its own commit. Mixing them is how an unverified charge
  reaches the prose while you are busy fixing a verified one.

---

## 6 · ★ THE ONE-OF-A-PAIR DEFECT CLASS — seven found, and the seventh was the instrument

**An instrument bound to ONE document while reporting on both.** The submission ships as two documents:
the extended report and the short journal article. `test_aso_submission_numbers.py` carries **~200
prose-against-artifact assertions and binds every one to the extended report**, so the short document
had **no numbers guard at all** — a value could drift there, disagree with the artifact that produces
it, and every test in the repository would still pass. Five sibling guards had the same shape and were
widened in rounds 8–11; this one could not be widened, because the journal article restates the same
quantities in its own sentences, so it got its own guard
([`test_journal_article_numbers.py`](./research/manuscripts/tests/)).

⭐ **THE SEVENTH WAS THE PRE-COMMIT TEST SELECTOR ITSELF.** Editing the journal article selected zero
modality tests — correct, no modality test names it — and the selector **announced that as "this
document is unguarded"** while **four modules in `research/manuscripts/tests` guard it**. It only ever
looked in the suite it draws from. **An instrument reporting a false absence is the failure this
repository keeps paying for** (CLAUDE.md §4: an absent reading is not a reading of absence). Two more
found in the same pass: the changed-prose linter resolved §-references for **both** documents against
the extended report's headings (the report runs §1–§6, the article §1–§8, so §7 and §8 errored falsely
*and* every reference to §1–§6 was silently validated against a different document), and
`blast_radius.py` — the tool that MEASURES gate coverage — read the extended-report family only, so
every "nothing moved" it returned was a statement about one document wearing the costume of a statement
about the packet.

⛔ **GENERALISE IT: WHENEVER A DELIVERABLE GAINS A SECOND FORM, ENUMERATE EVERY INSTRUMENT THAT NAMES
THE FIRST AND ASK WHETHER IT SHOULD NAME BOTH.** Guards, linters, selectors, coverage tools, target
lists, and the review series itself (§4).

### ★ A guard that asks "is the right number in here anywhere" cannot see drift

The journal article's new numbers guard first asserted `value in prose`. **A mutation test walked
through three of nine corruptions**, because one figure is stated at **three sites** and another at
**two** — corrupting ONE left the others standing and the `in` test still passed. Rewritten to **capture
the number out of the CONSTRUCTION that states it and check every match: 18 of 18 mutations caught,
single-site drift included.**

⛔ **MUTATION-TEST EVERY GUARD YOU WRITE, AND INCLUDE SINGLE-SITE MUTATIONS.** A guard you have not
tried to break is a guard whose coverage you are guessing at, and this is the class of guess this
repository has paid for most often.

---

## 7 · ⚠ Process defects that cost real rounds

- **(a) ⛔ BATCH EDIT SCRIPTS SILENTLY DISCARD EARLIER SUCCESSFUL EDITS.** Several `assert old in s`
  statements before a **single** write: when a later assertion throws, every earlier edit in that
  script is lost, and the traceback names only the assertion — so it reads as "one edit failed" when in
  fact none landed. **Read, write and VERIFY per edit.**
- **(b) ⛔ CHECK THE DIFF AGAINST THE MESSAGE BEFORE COMMITTING.** **Two commit messages claimed repairs
  their diffs did not contain** — `a076415d` is titled for exactly this ("the two repairs my own commit
  message claimed and its diff did not contain"). A commit message is the record a later round trusts;
  a false one turns a real defect into a closed one.
- **(c) ⛔ REGENERATE WITH THE DEPENDENCY-ORDER CHAIN SCRIPT, NEVER BY HAND.**
  `./scripts/regenerate_aso_chain.sh` (and `--check` to test for staleness without changing anything).
  **Hand-walking it produced four successive staleness failures — PDF, metrics, packet, manifest** —
  each caught only after the previous one was fixed. The order is not alphabetical and not obvious: the
  archive manifest hashes every other artifact, **so it must be last**, and the PDF must be built in
  BOTH styles because the bare command writes only the first.
- **(d) ⛔ SUBAGENT LIVENESS: CHECK THE LAST EVENT'S TIMESTAMP *AND* TYPE.** **Six killed seats were
  reported as "running" in three separate status boards.** A seat that died leaves a board that looks
  exactly like a seat that is thinking. Never infer liveness from the absence of a failure — CLAUDE.md
  §4's progress-check rule applies to review seats exactly as it does to a GPU job.

---

## 8 · Convergence — when to stop

### 8.0 · ⛔⛔ WHAT A BLOCKER IS, BECAUSE GETTING THIS WRONG MAKES CONVERGENCE UNMEASURABLE

**trimcrae, 2026-08-23, on being handed nine of them: *"That is just so many blockers. Are you
confirming that they actually are blockers and not nitpicks?"* They were not.** Audited on the spot:
of round 16's nine BLOCKERs, **ZERO were a wrong statement in the shipped paper.** In every case the
mutation was green BEFORE and red after — and "before" was the clean, correct text. The round changed
**16 test files, 4 tools, and 2 manuscript files; the journal article itself was never edited at all.**

| grade | the test |
|---|---|
| **BLOCKER** | the artifact **as it stands now** is wrong, misleading or unsafe. A reader acting on the committed text would be misled. Quote the wrong text and the record that contradicts it. |
| **P1** | the artifact is **correct now**, but an ordinary future edit would silently make it wrong and nothing would catch that. **Every guard gap belongs here, however central the claim.** |

### 8.0a · ⛔⛔ *WHICH* ARTIFACT — THE HALF §8.0 NEVER SAID, AND THE ROUND THAT PAID FOR IT

**§8.0 defines a BLOCKER as "the artifact **as it stands now** is wrong". It never says WHICH
artifact, and a seat brief that repeats it without saying so hands every seat the choice.**

⚠ **Measured round 21, PUB-ASO, 2026-08-30.** Five seats returned **four blockers, and three were
not in the paper**: two in `scripts/zenodo_deposit.py` and one in `deposit-state.json`. The
regression seat wrote *"the manuscript prose needs no change"* in its own scope note **and filed
three blockers anyway** — correctly, under a brief that never told it what the artifact was. The
three seats that read the paper as a paper returned **zero** blockers between them; the
citations seat re-fetched all 23 PMIDs live and recommended **accept**.
⛔ **AND THE DRIVER CAUSED IT TWICE OVER.** The brief said *"the artifact AS IT STANDS AT THE PIN is
wrong"* with no artifact named, and the regression LENS then said *"pay particular attention to
records that describe an OUTSIDE system — a DOI, a deposit, a submission status"*. That is an
instruction to go and grade the tooling. The seats did as they were told.
⚠ **The compounding fact: three of the four were defects the SAME SESSION had introduced hours
earlier**, building the Zenodo publish path. The round was reviewing its own driver.

★★ **THE OUTGOING ARTIFACT SET — name it in every brief, and let each seat's blockers be about it.**
The manuscript being posted, its display items, its references, the built PDFs and `.docx`; the
**deposited copy of any of those**; and **whether the archive the paper's DOIs resolve to actually
CONTAINS what the paper promises it contains**. Round 21 found a deposited manuscript that was
sixteen files behind the paper citing it, and rounds 23 and 24 each found code behind printed
numbers missing from the archive while Data availability promised all code was there. All three are
blockers and stay blockers.

⛔ **WHAT IS NOT IN IT: the repository's own tooling, tests, ledgers, receipts and state files.** A
defect there is real, is worth fixing, and is **not a blocker on a paper**. Grade it and say where
it lives. Nothing is lost by this — round 21's three all got fixed the same day.

⛔⛔ **AND STALE PROSE INSIDE A DEPOSITED *CODE* FILE IS A P2, NOT A BLOCKER** (trimcrae, 2026-08-31,
after four rounds of it). ⚠ **Measured that day: the archive is 496 files, 88 of them carrying
hand-written prose, against 14 that are the paper and its display items** — so a comment documenting
a constant graded the same as a wrong number in the abstract, and five seats reading 88 prose files
will find something every round by construction. That is whack-a-mole, not convergence: rounds 21-24
produced 18 blockers and **six of the seven in round 24 were introduced by this loop's own previous
repairs.**
★ **THE LINE, AND IT IS ABOUT WHAT A READER CAN BE MISLED INTO DOING.** A deposited comment that
moves no printed number, breaks no promise the paper makes, and misstates nothing a reader would act
on → **P2**, swept in batches. It becomes a **BLOCKER** the moment it does any of: contradict a
number the paper prints, falsify a promise the paper or the manifest makes, or misdescribe what the
archive contains.
⚠ **THE NARROWING DOES NOT REACH THE PAPER.** Wrong text in the manuscript, its display items or its
references is a blocker at any size — round 16's one real defect was a caption reading "two
single-base slides" where the canonical file records one, and it was worth more than the other eight
together.
⛔ **AND IT IS NOT A LICENCE TO LEAVE THE ARCHIVE WRONG.** A P2 is still a defect and still gets
fixed; what changes is that it no longer holds a paper. The right instrument for 88 files of prose
is a SWEEP, not a five-seat sample — see `test_the_deposit_does_not_restate_a_count_the_paper_owns.py`,
which closes the one class that bit three times in one file.

⛔⛔ **THE COVER LETTER IS NOT IN THE OUTGOING SET AND SEATS MUST NOT BE GIVEN IT AT ALL** (trimcrae,
2026-08-31: *"we should stop including the cover letter in what we give to the reviewers"*). Put
`**/*-cover-letter.md` on the brief's **may-not-read** list beside `research/autonomy/` and
`.claude/skills/`, so it is out of reach rather than merely out of scope.
★ **WHY OUT OF REACH AND NOT JUST OUT OF SCOPE.** Leaving it readable but ungradeable wastes the
scarcest thing a round has — a seat's attention — on a document that cannot produce a blocker.
Measured across rounds 23 and 24: **five** findings against the cover letter, including one graded a
BLOCKER that the seat itself then had to caveat as not gating the preprint, plus repeated reports
that its status header names a superseded DOI. All were true. None could ever have mattered to v2.
⚠ **AND IT IS THE ONE DOCUMENT WITH NO INSTRUMENT ON IT**, deliberately — trimcrae removed every
automated check on cover letters on 2026-08-30 (*"That's just cruft"*), because a letter is
hand-written once, at a publisher's portal, against that venue's requirements. A document nothing
maintains between submissions will always read stale to a careful reviewer, and that is not a
defect in the paper.
⛔ **WHAT THIS DOES NOT MEAN: that the letter may go out wrong.** It is rewritten by hand at
submission, which is when its claims are made true. Findings against it are worth recording for that
moment; they are not worth a seat's round.

★ **EVERY BLOCKER NAMES THE OUTGOING ARTIFACT IT IS IN.** A blocker that cannot name one is, by that
fact, not a blocker. This is the cheapest possible enforcement and it is a REPORTING requirement, so
it binds the seat rather than the bar.

⛔⛔ **AND DO NOT "FIX" THIS IN `publish_bar.py`.** The obvious move — have clause 1 count only
in-scope blockers — is wrong three times over. It is a **GOVERNED path edited by the cycle that
clause blocked**, which `amendment_guard` refuses by construction and should. It would **silently
discard** findings like round 21's deposited-archive one, which is genuinely reader-facing, so it
automates exactly the judgement a synthesis exists to make. And the bar was never miscounting: it
counted what the seats filed, and **the seats were mis-briefed**. ★ Fix the input, never the meter.

**⛔ "COULD BE INVERTED" / "NO INSTRUMENT READS IT" IS A P1 BY CONSTRUCTION.** The severity of what
*would* happen never promotes a hypothetical to a defect. ⛔ **And the converse, which is the half
that gets forgotten: text that is actually wrong today is a BLOCKER even when it looks small.** Round
16's one real defect was a caption reading *"two single-base slides"* where the canonical file records
**one** — an order-safety margin understated 2× — and it was worth more than the other eight together.

**★★ WHY THIS IS NOT PEDANTRY ABOUT LABELS.** Grading coverage gaps as blockers means the count can
never reach zero, because there is always another unguarded sentence. So *"iterate until no blockers"*
silently becomes *"iterate until every sentence has an instrument"*, which is unbounded — the blocker
count starts tracking INSTRUMENT COVERAGE rather than PAPER DEFECTS. That is §8a's own diagnosis
applied to the scoreboard instead of the paper, and it went unnoticed for a whole round **because the
inflated grade made the work look more urgent than it was.** ⚠ Report the two counts separately and
never merge them: **defects found in the artifact**, and **coverage gaps found**.


**⛔ STOP WHEN A ROUND RETURNS NO BLOCKERS, ON THE COMMIT THAT GETS POSTED. REPORT THE OPEN P1 COUNT
BESIDE THAT VERDICT — IT DOES NOT GATE.**

⚠ *Superseded, retained (rule 1.2): "STOP WHEN A ROUND RETURNS NO BLOCKERS **AND** NO P1s", and
before that "a round with no blockers is converged."*

⛔⛔ **THE P1 HALF WAS REMOVED 2026-08-29, ON TRIMCRAE'S DECISION, BECAUSE IT CONTRADICTED §8b ABOVE.**
That section argues that grading coverage gaps as blockers is wrong **precisely because the count can
never reach zero** — there is always another unguarded sentence — so the number stops tracking paper
defects and starts tracking instrument coverage; and it ends *"report the two counts separately and
never merge them."* **This rule merged them**, and `publish_bar`'s `hardening_converged` enforced the
merge as a publication gate, which is the same defect one level up: closing a P1 ships a new guard, a
new guard is new machinery, and the next round finds gaps in **that**. ⚠ *Measured on PUB-ASO,
2026-08-29: round 18's three guard-coverage P1s were closed, the work was real, and not one of them
was a wrong statement in the paper.* He put it himself — *"'This number is true but not anchored'
doesn't seem like it should be a blocker"* — and it does not.

★★ **AND THE ROUND-13 OBJECTION SURVIVES INTACT, THROUGH A DIFFERENT MECHANISM.** **Round 12 was the
first round with no blockers from any seat** (`9476171b`) — and **round 13 found a blocker**
(`40fc3c82`), plus eight P1s, of which all but two were damage from round 12's own repairs. That is
still true, and it is still the reason a clean round is not automatically a converged one. But the
protection never came from the P1 count: it comes from **reviewing the exact commit that gets
posted**. `publish_bar` requires `reviewed_commit == sha`, so every repair is inside what the seats
read, and **a round whose own repairs have not been reviewed cannot clear the clause however few P1s
it declares.** ⛔ So the pinned-commit rule below is now load-bearing twice over — do not relax it to
"a recent commit".

⚠ **THIS IS A LOOSENING, SO IT IS DECLARED RATHER THAN QUIET:** `amendment_guard` forbids a bar being
changed by the cycle it blocked, the 2026-08-29 cycle **was** blocked by it, and the change is
therefore recorded in `amendments.jsonl` as trimcrae's rather than the loop's. **A P1 is still a
finding, still written down, still worth closing** — the open count now travels on the line that
clears the paper, so a paper passing with live coverage gaps says so.

**Track the blocker trend; it is the signal, not the round number:**

| round | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|
| distinct blockers | **24** | 7 | 3 | 2 | **0** | 1 | 3 | **6** |

## 8a · ★★ WHEN THE BLOCKER COUNT STOPS FALLING, YOU ARE SAMPLING SURFACES, NOT FIXING A PAPER

**⛔ THE TREND ABOVE REVERSED, AND ITERATING HARDER WAS THE WRONG ANSWER (trimcrae, 2026-08-22:
*"If we keep playing whack a mole on blockers, put some thought into why that is and alter your
approach."*).** Rounds 14 and 15 went 3 → 6 while every finding was being applied and
mutation-verified. The paper was not decaying. Read the nine distinct blockers of those two rounds
together and they are **one finding wearing nine costumes**:

| the blocker | what read that surface before |
|---|---|
| Table 2's caption counted rows it no longer had | nothing |
| §5's void figure was cut, orphaning a claim that needed it | nothing |
| the paper never stated its own chemistry | nothing — **absence has no anchor** |
| the wrong non-financial interest was declared | nothing reads a Declarations block |
| both reagents named by donor exon alone | nothing reads sequence-and-exon *together* |
| "ten" is a WORD, so no numeric instrument saw it | nothing reads criteria as words |
| the title's PREDICATE could be inverted (`pair` → `spare`) | nothing reads verbs |
| the two reagents swappable against their own table | nothing joins prose to a table cell |
| the frozen deposit drifted from the tree | nothing recorded what was deposited |

**Not one is a number a guard got wrong. Every one is a surface with ZERO instruments.** So the
blocker rate was tracking **how many new lenses each round introduced**, not how many defects
remained — a new seat looks where nobody looked and finds the first thing there. ⛔ **That process
cannot converge by iteration, because there is always another unexamined patch.** Adding a
sixteenth round buys a sixteenth patch.

★ **THE STRUCTURAL CAUSE, IN ONE LINE: a claim is a QUANTITY and a RELATION, and the whole guard set
was built on the quantity half.** Numbers have pins, `_every_site` bindings and linters. Verbs,
criteria-as-words, attributions, absences, prose-to-table correspondences and whole Declarations
blocks had almost nothing. That is why `pair` → `spare` inverted the paper's central negative on the
one sentence every reader sees, with every number still correct and every gate still green.

⛔ **SO CHANGE THE INSTRUMENT, NOT THE ITERATION COUNT. ENUMERATE THE SURFACES.**
[`research/manuscripts/claim_coverage.py`](./research/manuscripts/claim_coverage.py) asks, of every
assertive sentence, whether any **selective** committed pattern matches it. Run it BEFORE designing
the next round's seats; its uncovered list is the remaining blocker risk, available all at once
instead of one per round. First honest run, 2026-08-22: **76 of 124 sentences in the journal
article, 47 of the 66 that state a number** — and the uncovered set contained the next round's
blockers in plain sight.

- ⚠ **ITS FIRST RUN REPORTED 100% AND THAT WAS THE BUG IT EXISTS TO FIND.** Harvesting patterns
  picks up `\s+`, `\d`, `[^.]{0,140}` — matchers that hit every sentence and bind none. **A guard
  earns the word "covers" only by distinguishing the sentence it guards from the ones it does not**,
  so a pattern matching more than `MAX_MATCH_SHARE` of a document is dropped. A census that counted
  those as coverage would be a gate reporting while measuring nothing, inside the instrument built
  to detect exactly that.
- ⚠ **COVERED ≠ CORRECT.** The census says only whether anything would NOTICE a change. A covered
  sentence can still be false; an uncovered one is merely unwatched.
- ⚠ **AND SOME CLAIMS ARE NOT MECHANICALLY BINDABLE AT ALL** — "no such design is reported in the
  literature retrieved here" rests on a fetch record and on honesty. **Name those separately rather
  than letting them hide among the ones a test can hold**, or the coverage number becomes a comfort.
- ★ **THE SECOND-ORDER RULE THIS GIVES YOU:** when a seat files a blocker, ask *what class of
  surface was unwatched here* and close **the class**, not the instance. Nine instances above
  reduce to about five classes; closing classes is what makes the next round's yield fall.

- **★★ A ROUND THAT FINDS ONLY DEFECTS INTRODUCED BY THE PREVIOUS ROUND'S REPAIRS MEANS THE REPAIRS,
  NOT THE PAPER, ARE NOW THE PROBLEM.** Tighten the edit discipline (§1's replace-don't-append, §5's
  re-derive-every-number, §7a's per-edit verify) rather than running another round. Another round
  against undisciplined edits just converts repair damage into more repair damage.
  ⛔ **THIS RULE WAS CORRECT AND MEASURED BY NOTHING FOR THREE ROUNDS, WHICH IS WHY IT NEVER FIRED.**
  It says "a round that finds ONLY" — and nobody was computing the proportion, so nobody could tell.
  Round 24 was 6 of 7 prior repairs and ran again; rounds 25, 26 and 27 followed. **§5a now derives
  `introduced_by` per blocker from `git log -S`, so this rule has an input**, and §5b is the repair
  gate that makes the tightening a mechanism instead of an intention. ⚠ *A rule whose trigger nobody
  computes is a rule that never fires — the same shape as `subagent_width` and the `notified_utc`
  requirement, both of which cost this repository real work before they were measured.*
- **★ PRE-REGISTER THE STOPPING RULE BEFORE THE FINAL ROUND RUNS.** One home for this manuscript's:
  [`fusion-junction-aso-deposit-stopping-rule.md`](./research/manuscripts/aso/fusion-junction-aso-deposit-stopping-rule.md).
  **A stopping rule written after the results are known is not a stopping rule, it is a justification** —
  and round 7's pre-registered prediction that no coverage gap remained was *falsified*, which is the
  evidence that pre-registration here is doing real work.
- **★ RECORD EVERY ROUND, INCLUDING ITS WRONG LEADS.** A review whose findings are recorded nowhere gets
  re-run from scratch and its refuted charges get re-raised. Ledgers:
  `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round*.md`.

---

## 8b · ★★ THE FIX IS AN INSTRUMENT, AND AN INSTRUMENT IS A NEW UNMEASURED CLAIM — ABLATE, DON'T READ

**⛔ §8a WAS RIGHT AND NOT ENOUGH. Round 16 pointed three seats at the census §8a prescribed and found
the SAME defect one level up.** The diagnosis had been *"a claim is a QUANTITY and a RELATION, and the
guard set was built on the quantity half"*, and the remedy was to enumerate surfaces instead of
sampling them. `claim_coverage.py` then turned out to be **a coverage claim is a PATTERN and a
DOCUMENT, built on the pattern half** — it credited a guard's regexes to documents that guard never
opens (22 of 27 "covered" cover-letter sentences were false positives), its selectivity threshold could
not be REPRESENTED on a nine-sentence document (1/9 = 0.111 > 0.10, so every pattern was discarded and
`journal-tables: 0 of 9` was integer arithmetic), and it scored *"matches few sentences"* where
*"distinguishes this sentence"* was meant.

**★★ WHY ITERATION CANNOT CONVERGE, STATED PROPERLY.** Every fix ships a NEW INSTRUMENT, and every new
instrument is a new claim asserted in prose and measured nowhere. Each round's fix **refills the pool
the next round drains.** Reviewing instruments by READING them never catches up with writing them.
This is CLAUDE.md's *"a property asserted in prose about a value passed by a caller is not a property;
it is a hope"*, applied to the review process itself.

**★ WHAT CHANGES THE SHAPE: ABLATION.** *"Sentence S is covered by witness W"* predicts that if S
changed, W would go red. **So change it and look.** Ablation is different in kind from every fix that
preceded it — it introduces **no new hand-written constant**, and it derives its expectation from the
instrument's OWN output, so it cannot drift from what the instrument claims. One mechanism catches
document-blindness, non-selective patterns and the threshold bug, because all three make the census
credit coverage that is not there. Home: `claim_ablation.py`,
`test_the_census_word_covered_survives_ablation.py`.

**⛔⛔ AND THE FIRST THREE ABLATION READINGS OF THE DAY WERE FABRICATED — ALL THREE THE SAME WAY.**
A mutation that never lands reports exactly what a guard that never fires reports.

| the reading | what actually happened |
|---|---|
| "seven guards are BLIND" | `sentence in text` never matched — the flattener joins lines, so **no file was ever edited** |
| "the generator catches nothing" | the literal was split across source lines, so `old in s` was False |
| "generated ⇒ every sentence bound" | the ablation mutated the **artifact**; the realistic edit is to the **generator**, and that IS unguarded |

**★★ SO THE RULE IS: ASSERT THE MUTATION LANDED BEFORE READING THE RESULT, AND KEEP A POSITIVE
CONTROL IN THE GATE.** A sample in which nothing was applied must FAIL, never pass quietly — an absent
reading is not a reading of absence (CLAUDE.md §4), and the comfortable direction is the one to
distrust: a false POSITIVE inflates coverage and HIDES surfaces, so it is worse than the false negative
that merely wastes a seat. ⚠ **Ablate the object that would really change.** A generated document's
claim lives in its GENERATOR: "ten-base-pair criterion" → "eleven-base-pair" in `aso_journal_tables.py`,
then regenerate, and `--check` plus all three linters plus 24 tests were rc=0. **Reproduction is not
derivation**, so a generator is NOT a witness.

**⛔ AND ABLATION INHERITS THE BLIND SPOT OF WHATEVER IT PERTURBS.** This one perturbs NUMBERS, because
the perturbation is unambiguous there — and round 16 seat 3 then applied **73 predicate inversions**,
of which **66 survived every gate and 44 sat in sentences the census calls COVERED**. Among them: the
central negative inverting at all four prose homes, the two reagents' clearance claims inverting
against their own CSV rows, and **a single deleted word** giving *"Research use only, and **for**
administration to any person or animal"*. The relation half needs its own table —
`test_the_manuscript_asserts_the_relation_its_artifacts_compute.py`, `(span, require, forbid)` per
claim, both halves asserted separately because *"the right verb is present"* and *"no wrong verb is
present"* fail differently. **Whatever axis your instrument does not perturb is the axis the next round
will find.**

### 8b.1 · Four rules the ablation round produced, each from a mistake made that day

**⛔ ABLATE A CLONE, NEVER THE WORKING TREE.** The first harness mutated the real manuscript with a
`finally` restore and a digest check. That makes the window SHORT, not SAFE — safety is about
everything else reading the repo during it. Proven: perturbing a pinned figure while
`test_lint_consistency::test_the_real_repo_is_consistent` runs reproduces exactly the failure a
preflight reported. And the `finally` is not even reliable — a SIGTERM (or an orphaned grandchild
`pkill -P` does not reach) skips it and leaves a **deposit artifact corrupted on disk**. `cp -al`
costs **0.03 s for 3,326 files**, so there was never a reason to accept the risk. ⚠ The clone shares
inodes, so an in-place write still reaches the original — measured, it does. Write a new file and
`os.replace` it, which breaks the link instead of following it.
⛔ **AND THE CLONE'S LOCATION IS NOT YOURS TO CHOOSE — THE SCRATCHPAD ROOT IS SHARED BY EVERY
CONCURRENT SEAT.** A mutation harness at `scratchpad/mutate.py` is a path a sibling can take too,
and on 2026-08-28 one did: the surviving copy ran against a module in ANOTHER SEAT'S WORKTREE and
reported `4 caught / 4` in a log that read exactly like a clean run of its own. ★ **The naming
convention, the log stamp and the audit tool that reads them back are owned by
[`research-loop`](../research-loop/SKILL.md) §3 — read it before you write a seat prompt, and do
not restate it here.** This section owns *what* you ablate; that one owns *where the seat writes*.

**⛔ THE SAMPLE IS NOT THE SWEEP.** Six sentences per document per commit catches an instrument that
has stopped binding anything; it does not enumerate what is unbound. The bounded sample was green
while `PREFLIGHT_FULL=1` found **1 of 41** journal sentences fully unbound — and chasing that one
sentence's only DIGIT turned up a second gap behind it. Run the full sweep before anything
outward-facing.

**★★ A GATE THAT REDS ON TRUE INPUT IS WORSE THAN ONE THAT GREENS ON FALSE INPUT**, because the
first thing anyone does is loosen it. Two in one round: `_RATE_SCANNER` had no word boundaries, so
*"the **all**ele frequency"* and *"an over**all** rate"* both resolved as the band `all` at
[1.0, 1.0] — an honest title containing "overall" failed against a correct measurement; and every
polarity `span` was written with ordinary spaces while the source **wraps mid-phrase**, so a correct
sentence read as MISSING. ⚠ Fix the class, not the instance: normalise the text once rather than
anchoring sixteen patterns. And assert **both directions** — over-anchoring silently makes every
check vacuous, which is the same failure wearing the other costume.

**★ MEASURE BEFORE YOU WRITE THE RULE.** The artifacts' `_what_this_is_not` fields deny knockdown,
tolerability, delivery and a cleavage measurement, none of which `lint_claims` names — an obvious
gap to close with a ban. Measured first: **every** occurrence in the paper is already in a denying
or design frame. A ban would have red-flagged an honest paper. The real exposure was DELETION, so
the fix was a floor under the sentences that do the denying — and reading the delivered PDF for it
showed that *"efficacy"*, *"potency"*, *"therapeutic window"* and *"clinical readiness"* appear
**nowhere** in the condensed paper, which no amount of reasoning about the markdown would have said.

**⛔ A GUARD'S REMEDY TEXT TEACHES THE WRONG FIX IF IT SAYS "RE-ANCHOR" FIRST (round 16 seat 3,
P1-e).** Rewriting four claims *without* preserving their anchors fired four guards, and every
message said the same thing: *"the sentence was reworded and this guard needs to follow it."* True
of a guard that measures WORDING — and an author who has just INVERTED a predicate sees a red build
whose printed remedy is *update the regex*, after which the finding disappears. The same inversion
with the anchor preserved is silent, which is the tell: **these were wording guards that
occasionally collided with a predicate, and counting them as coverage is what let the census read
82/124.** Two fixes, and both are needed: bind the predicate separately (§8b), and make every
anchor-failure message say **check the meaning before the regex** — re-anchor only when the sentence
says the same thing in different words.

### 8b.1a · ⛔⛔ AN INSTRUMENT THAT BATCHES ITS CHECKS CAN MANUFACTURE A FINDING THAT LOOKS REAL

**THE UNIT OF EXCLUSION MUST BE THE FAILING CHECK, NEVER THE BATCH THAT CONTAINS IT** (measured
2026-08-23, and it is the sharpest version of §8b's "the instrument is a new unmeasured claim").
`claim_ablation` runs every pytest witness for a document in ONE invocation — a real optimisation,
fourteen modules for the price of one interpreter — and subtracts the commands that are already red
before the mutation, so an unrelated failure cannot make every sentence look bound. Both halves are
right. Together they are not: *"the command is red"* and *"this witness is red"* stopped being the
same statement the moment the command held more than one witness.

What it produced: `claim-coverage.json` was stale, so ONE module failed, so the single batched
command was red at baseline, so **all fourteen modules were excluded from ever firing**. The gate
then reported three sentences BLIND — one of them `NR4A3` → `NR4A7`, which
`test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py` exists specifically to catch
and was sitting inside the excluded batch.

★ **THE DAMAGE IS NOT THE FALSE VERDICT, IT IS WHERE THE VERDICT POINTS.** A blindness report reads
as *the paper has an unguarded claim*, so the reviewer goes to the manuscript and writes a new
guard — for a hole that was never open. That is the blocker-count treadmill of §8a, fed by the
instrument itself. **The fix is cheap and belongs in every batching checker: when a batch is red at
baseline, DECOMPOSE it and re-measure, so only the member that is actually red is subtracted.** The
cost is paid only in the case that was silently wrong.

⚠ **AND THE GENERAL FORM, WHICH IS WORTH MORE THAN THE INSTANCE.** Any check that reports
`state(group)` and then reasons about a member of that group has this defect. Ask of every gate:
*if one thing in this batch is broken for an unrelated reason, does the gate go quiet about the
others — and does its output still look like a finding?*

### 8b.1b · ★★ COUNT THE PAYLOAD, NEVER THE POINTER TO IT

Same day, same shape, in a converter written that hour. The .docx builder asserts the figure
survived conversion by counting `<w:drawing>` elements in `word/document.xml`. It passed. The
archive's `word/media/` was **empty**: LibreOffice had written a *link* to
`file:///home/user/.../figure.png`, so the file carried a pointer into the build container and would
have rendered as a broken frame for the journal. The count was of the REFERENCE, and a reference is
exactly what a missing payload still has.

⛔ **So when a check asks "does this artifact CONTAIN X", it must read X's BYTES** — the media entry,
the embedded stream, the row itself — never the element that names it. This is CLAUDE.md §4's
"presence is never evidence of provenance" reproduced inside the verifier written to enforce it,
which is where it keeps turning up: **the check you write to catch a class of defect is itself a
member of that class until something measures it.**

### 8b.1c · ★ A MECHANICAL MIGRATION NEEDS AN INVARIANT, NOT A PROOFREAD

Converting 23 hand-maintained reference entries to a venue's citation style is a pure re-arrangement:
every surname, title word, journal name, page range, PMID and DOI is COPIED, never retyped
(CLAUDE.md §7 — never write an identifier from recollection). That makes one invariant available and
it is worth more than reading the output: **every word of the input must appear in the output.**

It fired on entry 15, whose *title* begins "Establishment, characterization and functional testing …"
— the author-splitter split on ", ", the title's own comma looked like an author boundary, and
everything from "characterization" onward was silently dropped. Twenty-two entries were perfect;
that one was not, and it is precisely the one a reader skims past. ⚠ **Write the invariant BEFORE the
transform, print the whole proposed output, and let the assertion be what clears it** — a migration
that "looks right" across twenty entries is a sample, not a check.

### 8b.1d · ★★ A COVERAGE NUMBER THAT FALLS IS NOT AUTOMATICALLY A REGRESSION — DIFF THE SENTENCE FIRST

The coverage ratchet's remedy text says *find the reworded sentence; do NOT lower the floor.* Right
almost always, and on 2026-08-23 it pointed at the wrong thing. `cover-letter.covered` fell 7 → 6
after an ordinary prose edit. **The sentence that lost its witness was byte-identical before and
after.**

The procedure that settled it, and it is three cheap steps in this order:

1. **Diff the SENTENCE, not the count.** Census the pre-edit document *inside an ablation clone*, at
   its real basename — witness discovery greps for the basename, so a census of `/tmp/old-copy.md`
   silently credits nothing and reports every sentence uncovered. That fake reading looks like a
   catastrophic loss and is pure instrument error.
2. **If the sentence is unchanged, ask which PATTERN dropped it** and count that pattern's matches
   before and after. A pattern crossing the selectivity cap because the DOCUMENT GREW is not the
   same event as a sentence losing its binding.
3. **Then look at the pattern itself.** Here it was `…|miss(?:es|ed)?|…` with no word boundaries,
   matching the middle of "sub·miss·ion" — all five of its hits in the letter were the word
   "submission". The seventh covered sentence had never been covered by anything.

⛔ **AND THE FIX GOES IN THE GUARD, NOT THE FLOOR.** Bounding the alternation removed the phantom
credit *and* closed a live red-on-true-input hazard in the same expression: unbounded
`clear(?:s|ed)?` matches inside "nu·clear", in a paper about an orphan NUCLEAR receptor, in the guard
that checks the title does not assert the inverse of the central negative. ⚠ `\b` alone is not
enough — a HYPHEN is a word boundary, so `\bpair\b` still matches the unit inside "ten-base-pair",
which is this repository's oldest instance of the class.

★ **THE GENERAL RULE: A SUBSTRING MATCH INFLATES COVERAGE AND CAN INVERT A GATE, AND THE TWO ARE THE
SAME BUG.** Every unbounded word in an alternation is both a false witness somewhere and a false
alarm somewhere else. Grep your own guards for `[a-z]\(\?:` with no `\b` in front — it is a
two-minute sweep and it has paid three times here.

⚠ **THE SWEEP WAS RUN, AND WHAT IT RETURNED IS WORTH KNOWING.** Beyond the one fixed, every
remaining unbounded alternation in this suite is a NOUN or VERB list embedded inside a longer
anchored pattern (`_BINDING_VERB`, `_UNPAIRED_NOUN`, `_RUN_LIST` in
`test_paired_numeric_lists_are_bound_in_the_right_order.py`), where the surrounding structure —
`\s+of\s+`, an adjacent number list — supplies the boundary the alternation lacks. They are not
clean, and `has|have` unbounded would match inside "p·has·e" given the chance; they are green
today because nothing in these documents assembles the rest of the structure around a substring.
**Recorded as a known residue rather than fixed blind**, because rewriting a passing pattern is how
a guard becomes vacuous, and the three instances that actually bit were all found by a measurement
(a red on true input, or a coverage number moving), never by reading the regex.

### 8b.1e · ⛔⛔ A PATTERN COMPOSED AT RUNTIME IS INVISIBLE TO ANYTHING THAT READS SOURCE

The `\b` fix in §8b.1d was applied **and the defect stayed live for hours**, in the same document,
found again by the same gate. Worth its own entry because the fix LOOKED complete and was verified
the wrong way.

The bounds went into a helper:

    def _verb(alts):
        return r"\b(?:" + alts + r")\b"
    _SPARING_VERBS = _verb(r"spare(?:s|d)?|…|miss(?:es|ed)?|…")

At runtime that is correct, and it was proven correct — `clear` stopped matching inside "nu·clear",
`miss` stopped matching inside "sub·miss·ion", asserted case by case. **But `claim_coverage`
harvests regexes by STATICALLY READING THE TEST SOURCE**, so what it saw was the unbounded string
literal going IN to the call, never the bounded value coming out. It kept crediting sentences to
that guard on `miss` inside "submission", and the ablation gate caught it a second time.

★ **THE RULE: A REGEX THAT OTHER TOOLING READS MUST BE COMPLETE WHERE IT IS WRITTEN.** Not
assembled, not `.format()`-ed, not concatenated from a constant — complete, in the literal. The cost
is repeating six characters; the benefit is that the file says what it does to every reader, human
or harvester.

⚠ **AND THE VERIFICATION LESSON IS THE SHARPER ONE.** Testing the runtime value proved the guard
worked and said nothing about the census — two consumers of one expression, and only one was
checked. **When a fix touches something a second tool reads, re-run the second tool**, not just the
first. The tell that this was missed: coverage counts did not move after a change that should have
lowered them. When they finally did, `journal-article` fell 69 → 68 and `cover-letter` 9 → 6, and
all three papers landed exactly on their floors.

### 8b.2 · ★★ A FIX BOUND TO A LIST REGRESSES AT A SIBLING. A FIX BOUND TO A PREDICATE DOES NOT.

**This is the sharpest structural result of the series, and it was measured, not reasoned** (round 17
seat B, 2026-08-23, over 33 mutations each asserted landed by `git diff` before any gate was read).
Of eleven round-16 fixes re-attacked, **every one whose scope was a PREDICATE held. Six of eleven
whose scope was a LIST regressed at a sibling the fix did not name:**

| the fix's scope | what it missed |
|---|---|
| `ARTICLE` | 1 of 3 manuscripts |
| `DOCUMENTS` | 4 of 6 |
| `PAPERS` | 2 of 4 |
| one polarity `span` | 1 of 4 prose homes of the same claim |
| the re-anchor remedy text | 5 of 7 surfaces |
| the early-return repair | 1 of 12 sites |

**⛔⛔ AND IN THREE OF THE SIX, THE MISSED SIBLING WAS NAMED IN THE FIX'S OWN COMMENT** — including a
check headed *"⛔ EVERY DOCUMENT, NOT THE TWO OBVIOUS ONES"* that enumerated four and missed two, so
`NR4A7` in the supplementary information and `RNase-H7` in the deposit tables shipped green into both
rebuilt PDFs. **Writing "every" above a list does not make it one.** That is §8a's one-of-a-pair
class with its mechanism finally named: **a list is a thing somebody must remember to extend, and the
remembering is what fails.**

**★ SO SCOPE BY THE PROPERTY.** Not *"these four files"* but *"every document that CONTAINS the
clause"* — which puts a document added tomorrow in scope without anybody remembering it. The
safety-critical Declarations lines are scoped that way now, and it immediately caught the single-word
deletion in two documents the list-scoped version had never read.

**⚠ AND THE WRONG PREDICATE REDS ON TRUE INPUT, WHICH IS WORSE THAN THE LIST.** The first attempt was
*"every `.md` in the submission directory"*; it swept up working notes and a review backlog that
legitimately name genes no artifact attests, and went red on a correct tree. **A widening is only a
fix once you have run it** — the honest predicate here was *"a document this submission SHIPS"*, read
from the archive manifest, which is a record rather than a memory. ⛔ Same trap one level down: the
identifier regex matched a single leading letter and so claimed PMC accessions and mutation notation;
tightening a pattern can equally make a guard vacuous, so **assert the discrimination survives** —
`NR4A7`, `EWSR7` and `TAF19` must still fall outside the attested set.

## 9 · Where the rest lives

- **Commit gates, preflight, the linters, `systems/`, and the six-part reviewer-AI block: `repo-gates`.**
  ⛔ Do not re-derive a gate ordinal here — `systems_check.py` derives the whole list from
  `scripts/preflight.sh` and fails the build on any document that disagrees, this file included.
- **Manuscript language discipline (R1–R5, never imply proteome-wide selectivity, efficacy, safety, a
  therapeutic window or clinical readiness):**
  [the roadmap](./research/manuscripts/nr4a3-program-map.md).
- **Anything outward-facing** — preprint, submission, release, DOI — is a CLAUDE.md §3 trigger and needs
  the block *and* the full preflight tier. That is `repo-gates`' business, not this file's.
