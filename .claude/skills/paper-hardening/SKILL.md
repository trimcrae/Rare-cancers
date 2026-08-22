---
name: paper-hardening
description: The repeatable cycle that takes a manuscript from "the science is done" to "submission ready" — iterated blind adversarial review rounds, applied and re-run until convergence, WITHOUT the paper ballooning in length. Load when starting or continuing a hardening cycle, before launching a review round, before applying a round's findings to the prose, before deciding whether another round is warranted, and any time you are about to add a sentence to a manuscript that is already under review. Covers: the per-round word budget as a hard gate on VENUE-CAPPED submissions and why it does not apply to aiXiv, which caps nothing; why thirteen rounds grew one article monotonically 2,914 to 5,976 words; a correction REPLACES text and never appends; the five blind seats and the regression lens that found the only round-13 blocker; review a PINNED COMMIT, never the working tree; refute by default; why a verifier's pasteable fix is not pre-verified prose; the one-of-a-pair defect class (seven found, the seventh inside the test selector itself); mutation-testing every guard you write, single-site mutations included; the four process defects that cost real rounds; and the convergence test — no blockers AND no P1s. Commit and gate mechanics live in `repo-gates`, not here.
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
6. **Apply survivors as REPLACEMENTS** (§1) — inside the budget where one applies, and replacing rather than appending in every case, which is the gate that does not depend on a venue.
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

**⛔ STOP WHEN A ROUND RETURNS NO BLOCKERS *AND* NO P1s.**

⚠ *Superseded, retained: "a round with no blockers is converged."* **Round 12 was the first round with
no blockers from any seat** (`9476171b`) — and **round 13 found a blocker** (`40fc3c82`), plus eight
P1s, of which all but two were damage from round 12's own repairs. A zero-blocker round with live P1s
in it is a round whose repairs have not yet been reviewed.

**Track the blocker trend; it is the signal, not the round number:**

| round | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|
| blockers filed | **24** | 7 | 3 | 2 | **0** | **1** |

- **★★ A ROUND THAT FINDS ONLY DEFECTS INTRODUCED BY THE PREVIOUS ROUND'S REPAIRS MEANS THE REPAIRS,
  NOT THE PAPER, ARE NOW THE PROBLEM.** Tighten the edit discipline (§1's replace-don't-append, §5's
  re-derive-every-number, §7a's per-edit verify) rather than running another round. Another round
  against undisciplined edits just converts repair damage into more repair damage.
- **★ PRE-REGISTER THE STOPPING RULE BEFORE THE FINAL ROUND RUNS.** One home for this manuscript's:
  [`fusion-junction-aso-deposit-stopping-rule.md`](./research/manuscripts/aso/fusion-junction-aso-deposit-stopping-rule.md).
  **A stopping rule written after the results are known is not a stopping rule, it is a justification** —
  and round 7's pre-registered prediction that no coverage gap remained was *falsified*, which is the
  evidence that pre-registration here is doing real work.
- **★ RECORD EVERY ROUND, INCLUDING ITS WRONG LEADS.** A review whose findings are recorded nowhere gets
  re-run from scratch and its refuted charges get re-raised. Ledgers:
  `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round*.md`.

---

## 9 · Where the rest lives

- **Commit gates, preflight, the linters, `systems/`, and the six-part reviewer-AI block: `repo-gates`.**
  ⛔ Do not re-derive a gate ordinal here — `systems_check.py` derives the whole list from
  `scripts/preflight.sh` and fails the build on any document that disagrees, this file included.
- **Manuscript language discipline (R1–R5, never imply proteome-wide selectivity, efficacy, safety, a
  therapeutic window or clinical readiness):**
  [the roadmap](./research/manuscripts/nr4a3-program-map.md).
- **Anything outward-facing** — preprint, submission, release, DOI — is a CLAUDE.md §3 trigger and needs
  the block *and* the full preflight tier. That is `repo-gates`' business, not this file's.
