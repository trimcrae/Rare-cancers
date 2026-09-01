---
id: DOC-SPRINT-S2-ESCALATION
title: "S2-ESCALATION — the requires_trimcrae queue, measured clause by clause"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S2-ESCALATION — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S2-ESCALATION — the `requires_trimcrae` queue, measured clause by clause

**Item(s):** AUT-PD-203, AUT-PD-196  
**Owned paths:** `research/autonomy/sprint-2026-09-01/S2-ESCALATION.md` (nothing else written)  
**Started/Finished (UTC):** 2026-09-01T18:36Z / 2026-09-01T18:55Z  
**Commit measured:** `bd8aac753fea89ad6798e35be34ee652befac358` (HEAD at start; `origin/main` ledger read separately for the hook path)

## Verdict

**PARTIAL — both rows describe defects that still exist, and both are mis-stated in a way that
matters.**

- **AUT-PD-196: CONFIRMED, unchanged at HEAD and in the working tree.** The retired permission is
  still asserted in `autonomy-state.json`; the driver's 18:32Z edit did not touch it.
- **AUT-PD-203: the census reproduces, the diagnosis is half right, and the proposed FIX is
  unimplementable as written and would be harmful if forced.** Its premise about `build_entries`
  is false — measurably — and its "not one is at 7/7" evidence proves less than it claims, because
  **three of the seven clauses are pinned to the exact commit and 4/7 is the ceiling any paper can
  read at an ordinary commit.** Six of the fifteen rows are acts the bar cannot speak to at all
  (outreach and a journal submission); for those, no amount of loop work makes the act takeable and
  they are **still his**.

---

## 1 · The census — every `requires_trimcrae` row at HEAD

`requires_trimcrae: true` is on **fifteen** rows, not thirteen. The working tree and
`origin/main` agree exactly (the hook reads the trunk; both were read).

⚠ **AUT-PD-203's "thirteen" was the count of UNSENT rows on 2026-09-01 before the group send**, not
the count of flagged rows. Two had already been sent individually (AUT-010 14:40:19Z, AUT-046
15:14:10Z); five more were sent as a named group at 16:54:38Z. **Eight are unsent now.**

| id | state | score | `notified_utc` | serves → publication | the act the row asks for |
|---|---|---|---|---|---|
| AUT-010 | queued | 165.0 | 2026-09-01T14:40:19Z | PUB-ATR | publish the ATR assessment **and** ask an external cell-panel group |
| AUT-046 | queued | 162.0 | 2026-09-01T15:14:10Z | PUB-MTAP-PRMT5 | post the preprint **and** approach a group holding archival material |
| AUT-042 | queued | 155.0 | 2026-09-01T16:54:38Z (group) | PUB-CARE-DELIVERY | judgement: is an EMC metastasectomy note worth writing |
| AUT-057 | queued | 155.0 | 2026-09-01T16:54:38Z (group) | PUB-CARE-DELIVERY | judgement: what an ordering-only prognostic statement is worth publishing as |
| AUT-058 | queued | 155.0 | 2026-09-01T16:54:38Z (group) | PUB-LOCOREGIONAL | judgement: is the RT-contradiction negative worth writing up |
| AUT-064 | queued | 155.0 | 2026-09-01T16:54:38Z (group) | PUB-CARE-DELIVERY | judgement: is an EMC margin note worth writing |
| AUT-065 | queued | 155.0 | 2026-09-01T16:54:38Z (group) | PUB-CARE-DELIVERY | judgement: write the surveillance observation up, or hold the route |
| AUT-073 | queued | 135.0 | **absent** | PUB-STRATEGY-ARCH | publish the trial-eligibility map |
| AUT-081 | parked | 115.1 | **absent** | PUB-SURFACE-TARGETS | contact a named external research group |
| AUT-044 | queued | 110.0 | **absent** | PUB-MODALITY-CENSUS | decide the framing and the venue |
| AUT-PROP-041 | parked | 107.2 | **absent** | *(none)* | respond to the Vancouver AI-disclosure consultation under his name |
| AUT-PD-188 | parked | 83.1 | **absent** | PUB-ASO | Table 1 clipping: a per-page cost vs. a content change on the submission PDF |
| AUT-061 | parked | 42.4 | **absent** | PUB-STRATEGY-ARCH | whether and where to publish the sequencing negative |
| AUT-005 | queued | 19.0 | **absent** | PUB-BIOMARKER-DEP | put an MCL-1/BCL-xL arm in front of the external group |
| AUT-027 | queued | 10.0 | **absent** | PUB-FUSION-OUTPUT | **submit to a journal** |

⚠ **`requires_trimcrae_why` is absent on two rows that carry the flag** — AUT-044 and AUT-PROP-041
have the reason under `_requires_trimcrae_why` (underscore-prefixed) instead. Every other flagged
row carries the un-prefixed field.

## 2 · The bar, measured — `publish_bar.py --paper <PUB> --sha bd8aac753…`

Ten endpoints, one backgrounded loop, ~55 s each. Raw JSON kept per paper; readings below are the
`n_passed/n_clauses` and the open clause names, both taken from the tool's own output.

| endpoint | reading | open clauses | authority |
|---|---|---|---|
| PUB-ATR | 4/7 | hardening_converged (FAIL), preflight_full_green, independent_adversarial_seat | granted |
| PUB-MTAP-PRMT5 | 4/7 | hardening_converged, preflight_full_green, independent_adversarial_seat | granted |
| PUB-BIOMARKER-DEP | 4/7 | hardening_converged, preflight_full_green, independent_adversarial_seat | granted |
| PUB-ASO | 4/7 | hardening_converged (FAIL), preflight_full_green, independent_adversarial_seat | **refused — excluded by name** |
| PUB-STRATEGY-ARCH | 3/7 | the three above **+ readable_enough_to_review (FAIL)** | granted |
| PUB-MODALITY-CENSUS | 3/7 | the three above **+ readable_enough_to_review (FAIL)** | granted |
| PUB-SURFACE-TARGETS | 3/7 | the three above **+ readable_enough_to_review (FAIL)** | granted |
| PUB-FUSION-OUTPUT | 3/7 | the three above **+ readable_enough_to_review (FAIL)** | granted *for aiXiv only — the row's act is a journal* |
| PUB-CARE-DELIVERY | 0/7 | all seven, **`endpoint_declared` FAIL: "endpoint names no existing document (None)"** | granted |
| PUB-LOCOREGIONAL | 0/7 | all seven, same `endpoint_declared` FAIL | granted |

**The whole readable_enough_to_review debt is nineteen sentences across four papers.** Verbatim from the tool:
PUB-MODALITY-CENSUS "1 sentence(s) over 60 words … longest 64w at line 39" of
`research/manuscripts/modality-census/cancer-modality-census.md`; PUB-STRATEGY-ARCH "1 … longest
61w at line 165" of `research/manuscripts/care-delivery/emc-trial-reachability.md`;
PUB-SURFACE-TARGETS "2 … longest 80w at line 176" of
`research/manuscripts/surface-targets/emc-surface-target-landscape.md`; PUB-FUSION-OUTPUT "15 …
longest 89w at line 800" of `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`.

⭐ **Two readings MOVED since AUT-PD-203's census on `850edb3358ba`, in the right direction, and
nobody had checked**: PUB-BIOMARKER-DEP 3/7 → **4/7** and PUB-ATR 3/7 (on `f37ef3c02`, per AUT-010's
own note) → **4/7**. `readable_enough_to_review` now passes on both. A census is a dated observation.

### ⛔ 2.1 · The single most important correction: **4/7 is the CEILING at an ordinary commit**

`publish_bar` clauses 1, 2 and 6 are all keyed to the **exact sha being posted**:

- `clause_2_preflight_full_green` reads `research/autonomy/preflight-receipts/<sha>.json` and FAILs
  if `record["sha"] != sha`. The repository holds **four** such receipts in total
  (`64fdc665b…`, `cec95069b…`, `da0d73318…`, `ec78ba94d…`) and **none is for HEAD**.
- `clause_1_hardening_converged` requires `reviewed_commit == sha`; on PUB-ASO it reports "last round
  reviewed 'b53290b37e…', not 'bd8aac753f…'".
- `clause_6_independent_adversarial_seat` reads
  `research/autonomy/review-seats/PUB-<X>-<sha>.json`; only three endpoints have ANY seat file
  (PUB-ASO, PUB-ATR, PUB-FUSION-PARTNER) and none is bound to HEAD.

All three are produced only by a deliberate publication run against one pinned commit. **So a paper
that is completely finished still reads 4/7 at any commit that has not been prepared for posting** —
which is exactly what PUB-ATR, PUB-MTAP-PRMT5, PUB-BIOMARKER-DEP and PUB-ASO read now.

⛔ **AUT-PD-203's sentence "NOT ONE IS AT 7/7" is true and proves much less than it is used for.**
7/7 is not a description of a finished paper; it is a description of a *staged post*. Reading the
gap as "the loop's own work remains" is right about the three sha-pinned clauses only in the sense
that *every* paper always has them open. **The clauses that actually discriminate between papers
are the four stable ones** — `claim_ceiling_honoured`, `identifiers_resolvable`, `endpoint_declared`,
`readable_enough_to_review` — and on those the board is: **four papers already at 4/4**, four papers
short of 4/4 by 1, 1, 2 and 15 sentences respectively, and two papers with **no document at all**.

---

## 3 · The board — per row, is the open clause the loop's work or his act?

**The distinction the bar cannot make.** `publish_bar` answers one question: *may the loop post this
paper to aiXiv unattended?* It says nothing about outreach, and for a journal it refuses by
construction — `authority_permits` returns `{"ok": False, "why": "journal submission always
escalates (D4); no bar reaches it"}` **before any clause is consulted**. So for six of the fifteen
rows the bar reading is not evidence about the row at all.

### A · Still his — no bar reaches the act (4 rows)

| id | act | why the bar cannot help |
|---|---|---|
| AUT-081 | contact a named external research group | outreach under his name; `publish_bar` has no clause for it |
| AUT-005 | put an MCL-1/BCL-xL arm to the group holding the two EMC models | outreach |
| AUT-PROP-041 | respond to the Vancouver AI-disclosure consultation under his name | outreach, **and on a clock** — see §5.2 |
| AUT-027 | **submit to a journal** (RT-FUSION-OUTPUT `attainable_today: journal_submission`) | `authority_permits` refuses `journal` unconditionally; `standing_grant` for journals is a `_constant`, "Not a parameter. No bar reaches it." |

⛔ For these four, "the paper is at 3/7" is a fact about a different act. Finishing the loop work
would leave every one of them exactly as undecided as it is now.

### B · Two acts welded into one row — split them (2 rows)

| id | the loop's half | his half |
|---|---|---|
| AUT-010 | publish the ATR assessment — PUB-ATR **4/7**, only the three sha-pinned clauses open | ask an external cell-panel group |
| AUT-046 | post the MTAP/PRMT5 preprint — PUB-MTAP-PRMT5 **4/7**, same three | approach a group holding EMC archival material |

One flag covers both halves, so the loop cannot advance the free half without touching a row it is
forbidden to take. Both rows' own `_NOTIFIED_AND_ANSWERED_2026_09_01` notes already state this
split; nothing in the ledger acts on it.

### C · Mislabelled — the act is the loop's own work (6 rows)

| id | evidence that it is loop work |
|---|---|
| AUT-042, AUT-057, AUT-064, AUT-065 | the act is "write a short note from data already in hand". PUB-CARE-DELIVERY reads **0/7** with `endpoint_declared` **FAIL — "endpoint names no existing document (None)"**: the bar's own words say the missing thing is a manuscript, which is writing, which is free (CLAUDE.md §5). The fork was put to him as a named group on 2026-09-01T16:54:38Z and **answered** ("ASO only today"), so flipping these suppresses no unsent decision. |
| AUT-058 | identical shape on PUB-LOCOREGIONAL, also **0/7**, also `endpoint_declared` FAIL, also inside the answered group. |
| AUT-PD-188 | ⛔ **its own `blocked_evidence`, dated 2026-08-30, withdraws the fork its `requires_trimcrae_why` still asserts.** The `why` describes a three-way cost/content trade at a per-page-charging journal. The evidence field says, verbatim: *"the three-way trade I was about to put to trimcrae — cut ~1000 words, pay a per-page charge, or post a known defect — was moot for v2 before I framed it"*, because Qeios takes Word and *"a Word build has no multicol container, so it cannot clip"*. What is left is a build fix with a three-part acceptance test — engineering, not a decision. The cost/content call, if it ever arrives, arrives as part of AUT-027. |

### D · Ambiguous — keep the flag (3 rows)

| id | the ambiguity |
|---|---|
| AUT-073 | "Publish the eligibility map" names no venue, and `RT-TRIAL-REACH.readiness.attainable_today` is **`internal_note`**, not `preprint`. The aiXiv standing grant covers an aiXiv post; a venue that is not aiXiv is his (§3, per paper per act). Unresolved → his. |
| AUT-044 | its own reason is "Decide the framing and **the venue**, which is an outward-facing call". Venue selection outside aiXiv is his. |
| AUT-061 | "whether **and where** to publish that is a judgement call". Same venue ambiguity. |

⛔ **These three are kept flagged deliberately.** The bar reads 3/7 on both their endpoints, and
every open clause is the loop's — but a venue that nobody has named is not a clause the loop may
resolve for him, and the failure this whole area exists to prevent is a decision quietly not sent.

---

## 4 · AUT-PD-196, verified directly — CONFIRMED, not refuted

The driver edited `research/autonomy/autonomy-state.json` at 18:32:47Z today. The **current
working-tree file** was read, and `git diff` was checked against HEAD.

**The two homes, quoted.**

`research/autonomy/publication-authority.json` → `zenodo_archive_publication` (the authority record):

> `"standing_grant": true` … `"approval_is_required_per_publication": false` …
> *"⛔ THE PER-PUBLICATION GATE WAS REMOVED BY TRIMCRAE ON 2026-08-30, verbatim … "On second
> thought, this is annoying. I don't want my approval to gate Zenodo. Just do it.""*

`research/autonomy/autonomy-state.json` →
`.budget_hold.authorised_exceptions[0]._SUPERSEDED_BY_A_WIDER_GRANT_2026_08_30` (the state file):

> *"⚠ AND IT DOES NOT TOUCH THE PUBLICATION AUTHORITY: PUB-ASO is still excluded by name from the
> standing aiXiv grant, **the Zenodo publish is still his by hand**, and the Qeios v2 post is still
> his."*

**Which one the code reads.** Measured, not assumed:

- `grep -rn "publication-authority" --include=*.py` → `scripts/zenodo_deposit.py:268-270` opens
  `research/autonomy/publication-authority.json` and takes `zenodo_archive_publication`, refusing
  when the grant is absent. `research/autonomy/publish_bar.py:61` binds the same file as
  `AUTHORITY_FILE`, and `authority_permits` (line 626) is the one function every outward path goes
  through.
- `grep -rn "authorised_exceptions"` over the whole repository, `.git` excluded → **six hits, none
  of them code**: three ledger `what` strings, one receipt's `took_why`, and two `goals.json`
  pointers. **No module reads it.**

⭐ **So the stale sentence governs nothing mechanically and misleads every human and agent reader** —
which is exactly the failure AUT-PD-196 records, and exactly why it is dangerous: the enforcement
path is correct, so nothing goes red while a reader acts on the wrong file.

⚠ **Why it reads as authoritative, and why the fix must be surgical.** Two of that sentence's three
clauses are TRUE and were re-verified here: `publish_bar --paper PUB-ASO` returns
`authority: {"ok": false}` — *"PUB-ASO is excluded from the aiXiv grant for 'submit'"* — and the
Qeios post is genuinely his. Only the middle clause is stale. A reader has no way to tell which
third is wrong.

**State at HEAD and in the working tree:** `grep -c "still his by hand"` returns **1** in
`git show HEAD:research/autonomy/autonomy-state.json` and **1** in the working tree, and
`git diff` contains **0** `+`/`-` lines matching it. The driver's 18:32Z edit rewrote
`backoff_level`, `budget_hold.active`, the dials and `declared_posture`; it did not touch this
field. **The defect is live.**

---

## 5 · Four further findings, each a $0 read taken before the sentence about it was written

### 5.1 · `build_entries` does not set `requires_trimcrae`, so AUT-PD-203's proposed fix cannot be built where it says

AUT-PD-203 says: *"THE FIX BELONGS IN THE DERIVATION … `build_entries` sets `requires_trimcrae`
from the graph, so it is the place that can also ask whether the act is possible."*

**That premise is false, and the code already documents why.** `priority.py` never assigns
`requires_trimcrae` anywhere (`grep` for an assignment returns nothing); `build_entries` (line 216)
writes 20 keys and that is not one of them. The field survives a re-score only through `merge()`'s
forward-compat `setdefault` loop at line 650-651. And `apply_requires_trimcrae`'s own docstring, put
there by the AUT-PD-127 fix, says it outright:

> *"⭐ WHY IT IS A POST-MERGE PASS AND NOT A TERM IN `build_entries` … `build_entries` reads only
> `systems/graph` (its own docstring says so), and `requires_trimcrae` is a property of a LEDGER ROW
> … The field is therefore unreachable at derive time."*

### 5.2 · The hook's dated-decision branch has never been reachable — `expires_utc` is on 0 of 344 rows

`escalation-debt-at-turn-end.sh` was written with AUT-PROP-041's clock as its motivating case, and
carries a whole branch for it (`EXPIRY_LEAD_DAYS = 45`, "A DATED decision … outranks everything
else"). That branch reads `e.get("expires_utc")`.

**Measured: `expires_utc` appears on zero of the ledger's 344 entries.** AUT-PROP-041's deadline
lives only in prose inside its `what` field. And the arithmetic is not academic: 2026-10-16 is
**exactly 45 days** from today, so the branch would be firing *right now* if the field existed.

⛔ Same shape as `subagent_width`: a rule recorded, asserted by prose, read by nothing.

### 5.3 · "An outstanding decision suppresses the rest" is implemented only for notices ≥ 7 days old

The hook's header states the intent: *"⛔ ONE AT A TIME, AND AN OUTSTANDING ONE SUPPRESSES THE REST.
If something has already been put to him and is still open, sending a second competes with the first
for the same attention."*

The code builds three lists — `dated` (needs `expires_utc`), `stale` (notified **and**
`age >= STALE_DAYS`, which is 7), and `never` (no `notified_utc`). A row notified **today** and still
open lands in **none of them**, so it suppresses nothing.

**Measured, by running the hook rather than reasoning about it** (`echo '{}' | bash
.claude/hooks/escalation-debt-at-turn-end.sh`, exit **2**):

```
⛔ ONE decision is ready for trimcrae and has never been sent:
   [135.0] AUT-073  Publish the eligibility map — this is the one route in the portfolio whose output could
   (7 others are parked and are deliberately NOT listed …)
```

Seven decisions were sent and answered today, the last at 16:54:38Z, with an answer ("ASO only
today") that plainly covers AUT-073 — and the hook is demanding an eighth send in the same session.

### 5.4 · The concrete cost of the mislabelling, measured in `handoff.py`

`handoff._takeable` filters `and not e.get("requires_trimcrae")`, so **all fifteen rows are withheld
from every successor's queue**, and `apply_requires_trimcrae` subtracts 25 from each score. AUT-073
(135.0) and AUT-044 (110.0) outrank most of what the loop's own workers are taking and are invisible
to them. That is the harm CLAUDE.md §0 names: *"If you cannot find live work, SAY SO"* — the loop
cannot see this work at all.

---

## 6 · The recommendation

⛔ **Recommend only. The driver applies. This seat wrote no ledger row, no hook and no state file.**

### R1 · Do NOT implement AUT-PD-203's fix as written — a bar-gated suppressor would zero the queue permanently

Three independent reasons, each measured above:

1. **It cannot go where the row says** (§5.1): `build_entries` does not write the field, and the code
   already carries the explanation of why it cannot.
2. **`bar < 7/7` is true of every paper at every ordinary commit** (§2.1). Three of seven clauses are
   sha-pinned to a staged post; the achievable ceiling at HEAD is 4/7 and four papers already sit
   there. A rule "suppress `requires_trimcrae` while the bar blocks the act" therefore suppresses
   **every row, always**, and the escalation queue never surfaces anything again.
3. **It suppresses the wrong six rows hardest** (§3.A, §3.B). Outreach and journal rows can never
   reach 7/7 for their act, because the bar does not measure their act. Those are the four rows that
   are genuinely his, and a bar-gated filter hides precisely them.

⭐ **What the census DOES support** is narrower and still worth having: a derived row whose endpoint
fails **`endpoint_declared`** — the bar saying "endpoint names no existing document" — is not a
publication decision, because there is no publication. That is 5 rows (§3.C) and it is a stable
clause, not a sha-pinned one.

### R2 · Correct six rows to `requires_trimcrae: false`, each with its evidence

`AUT-042`, `AUT-057`, `AUT-058`, `AUT-064`, `AUT-065` — the endpoint has no document, the act is
writing, the fork was sent as a named group on 2026-09-01T16:54:38Z and answered. Replace
`requires_trimcrae_why` with a pointer to that answer and to `endpoint_declared`.

`AUT-PD-188` — its own `blocked_evidence` withdraws the fork its `why` still asserts (§3.C). Replace
the `why`; keep the row as engineering work on the journal build.

⛔ **Nothing here removes an unsent decision.** Five of the six were answered today; the sixth was
refuted by its own evidence field a day after it was written.

### R3 · Split AUT-010 and AUT-046 into a publish row and an outreach row

The publish halves are 4/7 with only sha-pinned clauses open — takeable loop work. The outreach
halves stay `requires_trimcrae: true`. Today one flag holds both hostage.

### R4 · Keep AUT-073, AUT-044, AUT-061 flagged, and file the loop work beside them

Their venue is unnamed and venue selection outside aiXiv is his. **But file separate takeable rows
for what they are actually waiting on** — that unblocks the work without touching a decision.

### R5 · Add `expires_utc: "2026-10-16T00:00:00Z"` to AUT-PROP-041

The hook's dated branch is dead until some row carries the field, and this is the row it was written
for. At 45 days out it fires on the day it is added — which is the intended behaviour and is why it
should be added rather than deferred.

### R6 · Fix the hook's same-day suppression gap (§5.3)

An open row with a `notified_utc` newer than `STALE_DAYS` should suppress the `never` list, matching
the hook's own stated contract. ⛔ **This is a change to the guard that is nagging — `amendment_guard`
territory.** It must be made by a session that is not the one being nagged, its self-serving check
answered in the open: the change makes the loop nag itself less, and its defence is that the hook's
own header already declares this behaviour and the code does not implement it.

### R7 · AUT-PD-196: delete the middle clause only, and leave a pointer

Edit `.budget_hold.authorised_exceptions[0]._SUPERSEDED_BY_A_WIDER_GRANT_2026_08_30` to drop **"the
Zenodo publish is still his by hand,"** and nothing else — the other two clauses in that sentence are
true and were re-verified (§4). Replace it with a pointer to
`publication-authority.json` → `zenodo_archive_publication`. This is candidate fix (1) in AUT-PD-196's
own list, it is the one CLAUDE.md rule 1.1 prescribes, and the cycle that was misled by it (CYC-0090)
is not this seat, so `amendment_guard`'s objection does not apply here.

⭐ **And AUT-PD-196's candidate (2) is worth more than the edit:** a check that fails when any file
other than `publication-authority.json` asserts what the loop may or may not publish. The edit fixes
one sentence; the check fixes the class. `autonomy-state.json` is the driver's path this sprint —
this seat may not touch it.

---

## What I measured

Every command below was run; nothing here is inferred.

- `python3` over `research/autonomy/research-ledger.json` — **15** rows with `requires_trimcrae:
  true` of 344 entries; **8** with no `notified_utc`; `expires_utc` on **0**.
- `git show origin/main:research/autonomy/research-ledger.json` — the same 15 rows, same stamps. The
  hook reads the trunk, so both were checked.
- `python3 research/autonomy/publish_bar.py --paper <PUB> --sha bd8aac753… --json` for all ten
  endpoints, one backgrounded loop, ~55 s each (two returned in 0 s because their endpoint has no
  document). Results in §2.
- `echo '{}' | bash .claude/hooks/escalation-debt-at-turn-end.sh` → **exit 2**, demanding AUT-073.
- `grep -rn "authorised_exceptions"` (repo, `.git` excluded) → 6 hits, **no code**.
  `grep -rn "publication-authority" --include=*.py` → `zenodo_deposit.py:268`, `publish_bar.py:61`.
- `git show HEAD:…autonomy-state.json | grep -c "still his by hand"` → **1**; working tree → **1**;
  `git diff | grep -E "^[+-].*still his by hand"` → **0 lines**.
- `grep -n "SESSION_STATES"` in `priority.py:399` → `{"running", "done", "abandoned"}`, confirming
  AUT-PD-203's park finding. ⭐ **And the prediction is visible in the file right now:** of the six
  rows stamped `_PARKED_2026_09_01`, the three hand-filed ones (AUT-081, AUT-PROP-041, AUT-PD-188)
  are still `parked`, while the `_derived` ones (AUT-073, AUT-044, AUT-005, AUT-027) are back to
  `queued`. AUT-061 is `parked` only because `RT-SEQUENCING.state.status` is `parked` in the graph.

## What I changed

**Nothing but this file.** This seat is an investigation; it wrote
`research/autonomy/sprint-2026-09-01/S2-ESCALATION.md` and touched no other path, ran no git write
command, and edited no hook, test, ledger or state file.

## What I could not do, and what it is actually waiting on

- **Applying R2–R7.** Waiting on the driver: `research-ledger.json` and `autonomy-state.json` are
  unowned/driver-owned this sprint (charter §2), and R6 touches a hook.
- **Naming the venue for AUT-073, AUT-044 and AUT-061.** Genuinely waiting on trimcrae. Not blocked
  by any measurement this seat could take.
- **Nothing else was blocked.** The bar run is slow, not blocked; it completed in ~7 minutes.

## Ledger rows the driver should write

| proposed `what` | `kind` | `state` | `requires_trimcrae` |
|---|---|---|---|
| Correct `requires_trimcrae` to false on AUT-042/057/058/064/065 (endpoint has no document; the fork was sent as a group 2026-09-01T16:54:38Z and answered) and on AUT-PD-188 (its own `blocked_evidence` withdraws the fork its `why` asserts). Replace each `requires_trimcrae_why`; do not delete it. | `fix` | queued | false |
| Split AUT-010 and AUT-046 into a publish row (4/7, sha-pinned clauses only — takeable) and an outreach row (his). One flag currently blocks the free half. | `fix` | queued | false |
| Add `expires_utc: "2026-10-16T00:00:00Z"` to AUT-PROP-041. The hook's dated-decision branch reads that field and it is on 0 of 344 rows, so the branch has never been reachable — measured 2026-09-01. | `fix` | queued | false |
| `escalation-debt-at-turn-end.sh`: an open row notified inside `STALE_DAYS` must suppress the `never` list, which the hook's own header already declares and the code does not do. ⛔ `amendment_guard` — must not be taken by a session the hook is nagging; answer `self_serving_check` in the open. | `process_defect` | queued | false |
| AUT-PD-196 fix (1): drop the clause "the Zenodo publish is still his by hand," from `autonomy-state.json` `.budget_hold.authorised_exceptions[0]._SUPERSEDED_BY_A_WIDER_GRANT_2026_08_30` and leave a pointer to `publication-authority.json`. ⛔ Surgical — the other two clauses of that sentence are true and were re-verified 2026-09-01. | `fix` | queued | false |
| AUT-PD-196 fix (2), worth more than (1): a check that fails when any governance artifact OTHER than `publication-authority.json` asserts what the loop may or may not publish. The edit fixes one sentence; this fixes the class. | `process_defect` | queued | false |
| Clear the `readable_enough_to_review` debt: 19 over-length sentences across four papers — cancer-modality-census.md (1, longest 64w L39), emc-trial-reachability.md (1, 61w L165), emc-surface-target-landscape.md (2, 80w L176), nr4a3-fusion-transcriptional-output.md (15, 89w L800). Split them; do not raise the ceiling. Free, and it moves four endpoints from 3/7 to 4/7. | `write` | queued | false |
| Amend AUT-PD-203 rather than closing it: the census reproduces, but (a) `build_entries` never writes `requires_trimcrae` — `apply_requires_trimcrae`'s docstring says so — and (b) three of seven clauses are sha-pinned, so 4/7 is the ceiling at an ordinary commit and a `bar < 7/7` suppressor would hide every row forever, hardest the outreach and journal rows the bar cannot measure. The supportable rule is narrower: `endpoint_declared` FAIL means there is no publication to decide about. | `process_defect` | queued | false |
