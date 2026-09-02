---
id: DOC-SPRINT-S42-ELIGIBILITY-MAP-READINESS
title: "S42-ELIGIBILITY-MAP-READINESS — the eligibility map exists, clears 3 of 7 bar clauses, and the one FAIL is a one-word overage with a verified split"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Deliver a readiness verdict for ledger row AUT-073 ("publish the eligibility map") against
  research/autonomy/publish_bar.py, with every clause graded from the artifact that decides it,
  and an ordered gap list priced by what it costs to close. No outward act was taken and none is
  proposed here: this memo is the measurement, not the post.
scope: >
  PUB-STRATEGY-ARCH / research/manuscripts/care-delivery/emc-trial-reachability.md as it stands at
  commit b4cf28c6be8f464fc25e0cee06f6be50eb181138. Records three readiness facts the bar does not
  see (endpoint/paper scope mismatch, no lint_consistency coverage, no PDF build target) and one
  verified free fix for the single failing clause.
last_verified: 2026-09-02
---

# Eligibility-map readiness — AUT-073

Seat: S42, sprint-2026-09-01. Read `publish_bar.py` first, ran it second, wrote this third.
⛔ **Nothing was posted, submitted, deposited or sent. No git write command was run. The manuscript
body was not edited** — the one prose fix this memo recommends was verified on a scratch copy and is
handed over as text, not applied.

---

## 1 · The artifact exists, and it is not the thing the row's phrasing suggests

★ **The eligibility map is a real, drafted paper.** AUT-073's "publish the eligibility map" names an
artifact that is on disk today:

| field | value | read from |
|---|---|---|
| publication id | `PUB-STRATEGY-ARCH` | `systems/graph/publications.json` |
| title | *Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it* | `systems/views/L3-publications.md:330` |
| document | `research/manuscripts/care-delivery/emc-trial-reachability.md` | `publications.json` → `document.file` |
| state / venue / unit | `drafted` · `preprint` · `short_report` | same |
| length | 1,958 words, 78 sentences | `wc -w`; `lint_readability.py` |
| doc sha256 @ b4cf28c6 | `4d67e5012c89477ca46aaf8711f8bc9e62443b0e3859197737b965c0ad6df00b` | `publish_bar._document_digest` |
| routes feeding it | `RT-TRIAL-REACH`, `RT-SCHEDULING`, `RT-SEQUENCING` (all `contributing`) | `L3-publications.md:612-614` |

⭐ **And the route under it was unblocked outright this week, by measurement rather than by decay.**
`systems/graph/blockers.json:82` records the 2026-09-02 blocker-model correction: *"RT-SCHEDULING AND
RT-TRIAL-REACH GAINED NOTHING AND ARE NOW UNBLOCKED OUTRIGHT"*, because RT-TRIAL-REACH's
`readiness.missing` names non-US registry coverage needing an authenticated endpoint — *"an access
condition and not a curation gap"*. So the route is live, its paper is drafted, and the ledger row's
`cost_class` of `free` is accurate.

⚠ **The row is already PARKED, and the park is honest.** `research-ledger.json` → `AUT-073` carries
`_PARKED_2026_09_01` on trimcrae's verbatim *"ASO only today."* That same note records the bar at
**3/7 on 850edb3358ba** with the same four clauses open that this seat re-measures below — i.e. the
park never claimed to be waiting on him, and the row deliberately carries **no `notified_utc`**
because he was never asked about this paper by name.

---

## 2 · The clause count, read from the code

⛔ **Seven.** Not quoted from prose — `CLAUSES` is a tuple at `research/autonomy/publish_bar.py:722`
with seven entries, and `evaluate()` derives `n_clauses = len(clauses)` at runtime. The file's own
docstring records why no number is typed anywhere: *"eight copies of one number, all correct on
2026-08-26 and all stale by 12:41 PM ET the next day, when `clause_7_readable_enough_to_review`
landed in commit 648114f."*

```
clause_1_hardening_converged        clause_5_endpoint_declared
clause_2_preflight_full_green       clause_6_independent_adversarial_seat
clause_3_claim_ceiling_honoured     clause_7_readable_enough_to_review
clause_4_identifiers_resolvable
```

---

## 3 · The bar, run

```
$ python3 research/autonomy/publish_bar.py --paper PUB-STRATEGY-ARCH \
      --sha b4cf28c6be8f464fc25e0cee06f6be50eb181138

PUB-STRATEGY-ARCH @ b4cf28c6be8f -> BLOCKED (3/7 clauses)
  [????] hardening converged (no blockers on this commit; P1s reported)
         absent: research/autonomy/hardening-state/PUB-STRATEGY-ARCH.json — run a hardening round and record its result
  [????] PREFLIGHT_FULL=1 green on the posted commit
         absent: research/autonomy/preflight-receipts/b4cf28c6be8f464fc25e0cee06f6be50eb181138.json — run PREFLIGHT_FULL=1 and record its exit code
  [OK  ] claim strength within the endpoint's ceiling
         lint_claims clean over research/manuscripts/care-delivery/emc-trial-reachability.md
  [OK  ] every identifier traces to a fetch or the ledger
         lint_citations clean corpus-wide, covering research/manuscripts/care-delivery/emc-trial-reachability.md
  [OK  ] the endpoint is a declared falsifiable claim
         PUB-STRATEGY-ARCH claims: For a cancer that will never have a randomised trial, the variables a clinician actually c...
  [????] a blind adversarial seat finds the claim supported
         absent: research/autonomy/review-seats/PUB-STRATEGY-ARCH-b4cf28c6be8f464fc25e0cee06f6be50eb181138.json — run a blind seat on this commit
  [FAIL] the outgoing text is readable and keeps its caution
         1 sentence(s) over 60 words in research/manuscripts/care-delivery/emc-trial-reachability.md (longest 61w at line 165). Split them — see the `scientific-writing` skill. Do NOT raise the ceiling and do NOT cut a clause to get under it.
  authority: OK — granted: trimcrae, 2026-08-26, AskUserQuestion D1, verbatim: 'Broad: any paper meeting the bar'
```

### One line per clause

| # | clause | verdict | the artifact and line that decides it |
|---:|---|---|---|
| 1 | `hardening_converged` | **UNMEASURED** | `research/autonomy/hardening-state/PUB-STRATEGY-ARCH.json` — **absent**. `ls hardening-state/` returns exactly three files: `PUB-ASO.json`, `PUB-ATR.json`, `PUB-FUSION-PARTNER.json`. Round 0. |
| 2 | `preflight_full_green` | **UNMEASURED** | `research/autonomy/preflight-receipts/b4cf28c6….json` — **absent**. Four receipts exist on disk, none for this sha. |
| 3 | `claim_ceiling_honoured` | **PASS** | `lint_claims.py` exit 0 over the document. |
| 4 | `identifiers_resolvable` | **PASS** | `lint_citations.py` exit 0 **corpus-wide** — the clause deliberately has no paper-scoped mode (`publish_bar.py:530-545`), so any unresolved identifier anywhere in the repository re-reds this. |
| 5 | `endpoint_declared` | **PASS** | `publications.json` → `what_it_would_claim`, 1,047 chars against a 40-char floor; `document.file` exists. |
| 6 | `independent_adversarial_seat` | **UNMEASURED** | `research/autonomy/review-seats/PUB-STRATEGY-ARCH-b4cf28c6….json` — **absent**. a `grep` for `strategy` over `ls review-seats/` returns nothing: this paper has never had a seat, at any commit. |
| 7 | `readable_enough_to_review` | **FAIL** | `lint_readability.measure()` on the document at the pinned sha: **1 sentence at 61 w** against `SENTENCE_CEILING = 60`. Screen line: `emc-trial-reachability.md  78 sent  mean 18.7  p90 31  max 61  >60w 1  FKGL 11.4  caution 10.3/1kw`. |

**Counts: 3 PASS · 1 FAIL · 3 UNMEASURED.** ⚠ `publish_bar`'s header is explicit that UNVERIFIABLE
and FAIL both block and differ only in what to do next — *"an absent reading is not a reading of
absence"*. The three UNMEASURED rows are not near-passes; nobody has looked.

⭐ **The authority half is already green.** `authority_permits` returns OK: the standing aiXiv grant
covers this paper, and it is not in `scope.excluded_papers` (only `PUB-ASO` is). **So nothing here
waits on trimcrae. Every open clause is the loop's own work** — which is exactly what the parked
row's own note said, and this seat's own run at a newer commit reads the same way.

---

## 4 · The gap list, ordered by what it costs to close

| # | clause | what exactly has to happen | $ | needs trimcrae? |
|---:|---|---|---|---|
| 1 | 7 · `readable_enough_to_review` | **Split one sentence** — the `- **Two registries, of five or more.**` bullet at `emc-trial-reachability.md:172-176`. A verified split is in §5 below; it drops no clause and moves `max` 61 w → 45 w and `>60w` 1 → 0. | **$0**, one edit | no |
| 2 | 6 · `independent_adversarial_seat` | **One blind seat on the FINAL commit**, writing `research/autonomy/review-seats/PUB-STRATEGY-ARCH-<sha>.json` with `blind: true`, `reviewed_commit == <sha>`, `verdict == "supported"`, a `central_claim` of ≥40 chars, and `document_sha256` equal to `git show <sha>:<doc>` hashed — the clause re-derives that digest itself (`_document_digest`, `publish_bar.py:658`). | **$0**, one subagent | no |
| 3 | 1 · `hardening_converged` | **One hardening round on the same final commit**, writing `research/autonomy/hardening-state/PUB-STRATEGY-ARCH.json` with `blockers`, `p1s`, `last_round` (int ≥ 1), `reviewed_commit == <sha>` and a `seats` list naming records that all exist at that sha and are all closed (`status != "open"`). Shape: copy `hardening-state/PUB-ATR.json`. ⭐ **The width trap does not bind here**: `_look_history("PUB-STRATEGY-ARCH")` returns `{}`, so `widest = 0` and the declaring round cannot be refused for being narrower than a prior one. Blockers must be **zero**; P1s are reported, not gated (loosened 2026-08-29 on trimcrae's own decision, recorded in `amendments.jsonl`). | **$0**, seats + one applied round | no |
| 4 | 2 · `preflight_full_green` | **`PREFLIGHT_FULL=1 ./scripts/preflight.sh` on the final commit**, log committed, and a receipt at `preflight-receipts/<sha>.json` carrying `mode: "FULL"`, `exit: 0`, `sha`, `log`, and `log_sha256` matching the committed log byte-for-byte. The clause re-derives the exit code from the log and requires the `== pytest (modalities: FULL, PREFLIGHT_FULL=1) ==` banner plus a terminal `EXIT=0` marker (`publish_bar.py:451-495`). | **$0 cash, ~25 min wall clock** | no |

⛔ **Order is not negotiable, and it is not the order above.** Clauses 1, 2 and 6 are all **bound to
one sha**. Clause 7's fix changes the document, which changes the commit, which invalidates any seat,
hardening record or FULL receipt taken before it. ★ **So the sequence is: split the sentence → commit
→ freeze that sha → then seats, hardening round and the FULL run against it, in parallel.** Doing the
expensive one first is how the 70 minutes recorded in CLAUDE.md §6 got spent.

⚠ **AND THAT IS WHY THIS SEAT DID NOT RUN `PREFLIGHT_FULL=1`.** Measured, not assumed: local `HEAD`
is `b4cf28c6be8f` (2026-09-02 07:59:08 +0000) and `origin/main` is already `cfdc0a58b`, with the four
preceding commits landing at 07:59, 07:58, 07:44 and 07:43. **The trunk moved four times in sixteen
minutes while this sprint runs.** A receipt costs 25 minutes and binds to a sha that will not be the
posted one, and CLAUDE.md §6 reserves `PREFLIGHT_FULL=1` for the four publication acts in any case.
Running it now would buy nothing and would look like progress.

---

## 5 · The one free fix, verified rather than proposed

The failing sentence, verbatim from `emc-trial-reachability.md:172-176`:

> **Two registries, of five or more.** A non-US sweep ran on the date of this draft and only one of
> four non-US endpoints answered: the EU endpoint returned an authentication error for the second
> time on a second date, two more refused automated access, and the WHO portal was not reached
> because this sweep's URL was wrong — a defect here, not a finding about that registry.

★ **It is a one-word overage on a four-clause sentence, and it splits at its own punctuation.** The
colon becomes a full stop and the second comma becomes a full stop; **no clause is cut, no hedge
weakened, and the em-dash caveat about the WHO URL being *our* defect stays attached to the WHO
clause** — which is the sentence's whole ethical content and the thing a length-driven trim would
have eaten first.

Pasteable replacement for the three wrapped lines (the anchor is `four non-US endpoints answered:`):

```
  four non-US endpoints answered. The EU endpoint returned an authentication error for the second
  time on a second date, and two more refused automated access. The WHO portal was not reached
  because this sweep's URL was wrong
```

**Verified on a scratch copy** (`/tmp/.../scratchpad/sprint/split-candidate.md`, the manuscript itself
untouched):

| metric | before | after |
|---|---:|---:|
| sentences over 60 w | **1** | **0** |
| longest sentence | 61 w | **45 w** |
| mean sentence | 18.7 w | 18.2 w |
| FKGL | 11.4 | 11.3 |
| caution markers / 1000 w | 10.3 | **10.3** |

⭐ **Caution is unchanged**, so clause 7's second failure mode — *"a FALL in caution markers against
the pinned baseline"* — cannot be triggered by this edit. ⚠ It could not have been anyway: **no
baseline is pinned for this document.** `readability-baseline.json` → `caution_per_1000w` carries 11
entries and this file is not among them, so `was is None` and that half of the clause is **UNMEASURED
for this paper**, now and after the fix. That is a real hole in the gate, not a pass.

⚠ **This is the residue of a fix already made, not a new finding.** `S5-READABILITY.md:156` records
this document at **1 over / longest 90 w before**, **1 over / longest 61 w after** the extractor
repair, graded *"⛔ real (shortened, still over)"*. The artefact half is gone; what is left is prose.

---

## 6 · Three readiness facts the bar cannot see

⛔ **A 7/7 on this paper would not mean the four things below are fine.** Each is outside every
clause, and each is the kind of defect this repository has already paid for once.

**6.1 · The endpoint claims three variables; the paper covers one.** `publications.json` says so
itself, in the endpoint's own text: *"⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY. The
endpoint's claim spans three variables — scheduling, sequencing and reachability — and the other two
are now graded as closed (RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit) … but they are
NOT in the drafted manuscript yet."* ★ **Clause 5 checks that `what_it_would_claim` is ≥40 characters
and that the document exists. It does not check that the document defends the claim.** So the bar
would clear a paper narrower than its own registered endpoint, and the disclosure that makes this
honest lives in the graph rather than in the outgoing text. **That is a decision for whoever posts:
either the paper's declared scope is narrowed to reachability, or the other two routes' findings go
in.** It is not a bar failure and this seat does not resolve it.

**6.2 · `lint_consistency.py` has never looked at this paper.** `research/manuscripts/pinned-figures.json`
→ `targets` holds **28** entries and `emc-trial-reachability.md` is **not** one of them. ⚠ This is the
exact shape `PUB-ATR`'s round 3 filed as a blocker-class hazard for its own document — *"every
correction this paper has made is registered ONLY in its own prose appendix, which is why 27,195 /
20,324 / 93.2 % … each survived one or more hardening rounds after being corrected somewhere else in
the same document"*. Adding the file to `targets` is one line and subjects it to all existing
superseded patterns, so it is a cascade to run deliberately (CLAUDE.md §6), not a side effect.

**6.3 · There is no PDF build target for this paper.** `research/manuscripts/build_submission_pdf.py`
→ `PAPERS` has exactly three keys: `aso-journal`, `fusion-output`, `vaccine-path`. ⭐ **This is not
necessarily a gap** — no `publish_bar` clause requires a PDF and the aiXiv path generates metadata
from the manuscript — but "build the PDF" was not a free step available to this seat, and anyone
planning a typeset preview should know the builder does not know this paper.

**6.4 · `ready_to_post.py` correctly does not list it, and that is a green signal.** Running it
returns one row (`PUB-ASO`, NOT-READY, blocked on `hardening_converged`, `preflight_full_green`,
`independent_adversarial_seat`). PUB-STRATEGY-ARCH is filtered out because its `next_act` is not in
`HIS_ACTS` — i.e. **the queue of papers waiting on trimcrae does not contain this one, by
construction.** That is the machine agreeing with the ledger row's `requires_trimcrae: false`.

---

## 7 · Verdict

⛔ **Not publishable today: 3 of 7 clauses pass, one fails, three have never been measured.**

★ **The shortest honest path is four steps, all of them free, none of them his:** split the one
61-word sentence (§5, verified, pasteable) → commit and freeze that sha → run a hardening round and a
blind adversarial seat against **that** sha, recording both in the shapes clauses 1 and 6 re-derive →
run `PREFLIGHT_FULL=1` on the same sha and commit the log with a digest-bound receipt. **No GPU, no
money, no external access, no decision that is trimcrae's.** ⚠ And it is currently held above all of
that by his 2026-09-01 *"ASO only today"*, which the ledger row records and this seat does not
reinterpret.

## 8 · What this seat did and did not do

- **Did:** read `AUT-073` from the ledger; located the artifact and its publication id; read
  `publish_bar.py` end to end and enumerated `CLAUSES` from the tuple; ran the bar at HEAD and pasted
  its unedited output; ran `lint_readability.py` on the document; read `_look_history` and
  `_seat_records` for this paper (both empty) and computed the document digest at HEAD; verified a
  candidate split on a scratch copy; checked `pinned-figures.json`, `readability-baseline.json`,
  `build_submission_pdf.py` and `ready_to_post.py`.
- **Did not:** post, submit, deposit or send anything; run any git write command; edit the
  manuscript, the ledger, the graph or any state file; run `PREFLIGHT_FULL=1` (§4, with the
  sha-churn measurement that makes it worthless right now); stamp `notified_utc` on anything.
