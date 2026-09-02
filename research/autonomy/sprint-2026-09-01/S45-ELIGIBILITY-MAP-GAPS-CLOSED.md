---
id: DOC-SPRINT-S45-ELIGIBILITY-MAP-GAPS-CLOSED
title: "S45-ELIGIBILITY-MAP-GAPS-CLOSED — the one FAIL is fixed in the tree, the never-armed consistency guard is armed and mutation-proved, and a SECOND uncovered gate is named"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Record the two in-repo edits that close the free half of AUT-073's gap list — the 61-word split and
  the arming of lint_consistency over the eligibility map — with every gate re-run and quoted, the
  post-commit bar tally derived from the clause's own code path, and the coverage holes that remain
  after both edits. No outward act was taken and none is proposed.
scope: >
  PUB-STRATEGY-ARCH / research/manuscripts/care-delivery/emc-trial-reachability.md, working tree at
  HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138 with two uncommitted edits by this seat. Verifies
  rather than inherits S42's findings; adds three it did not have.
last_verified: 2026-09-02
---

# Eligibility map — the free gaps, closed

Seat: S45, sprint-2026-09-01. Predecessor: `S42-ELIGIBILITY-MAP-READINESS.md`, whose four verifiable
claims were re-measured here and all four held. ⛔ **Nothing was posted, submitted, deposited or
sent. No git write command was run.** Two files were edited: the manuscript and
`pinned-figures.json`. Both are staged by path by the driver, not by this seat.

---

## 1 · The failing clause, fixed — and the split does more than shorten

**Before**, `emc-trial-reachability.md:172-175`, the sentence `lint_readability` reported at 61 w:

> **Two registries, of five or more.** A non-US sweep ran on the date of this draft and only one of
> four non-US endpoints answered: the EU endpoint returned an authentication error for the second
> time on a second date, two more refused automated access, and the WHO portal was not reached
> because this sweep's URL was wrong — a defect here, not a finding about that registry.

**After**, same lines, as applied:

> **Two registries, of five or more.** A non-US sweep ran on the date of this draft and only one of
> four non-US endpoints answered. The EU endpoint returned an authentication error for the second
> time on a second date, and two more refused automated access. The WHO portal was not reached
> because this sweep's URL was wrong — a defect here, not a finding about that registry.

★ **Nothing was dropped and nothing was strengthened.** Four facts in, four facts out: four non-US
endpoints attempted with one answering; the EU authentication error, still carrying *"for the second
time on a second date"*; the two further refusals; and the WHO non-retrieval with its em-dash caveat
**still attached to the WHO clause** — *"a defect here, not a finding about that registry"*, which is
the sentence's ethical content and the first thing a length-driven trim would have eaten.

⭐ **AND THE SPLIT REPAIRS AN ARITHMETIC AMBIGUITY THE OLD PUNCTUATION CREATED — this is a finding,
not a cosmetic side effect.** Under the colon, the enumeration reads as the endpoints that did *not*
answer, and it lists four of them (EU + two more + WHO) against a stated total of four attempted with
one answering. The source record settles which reading is right:
`research/literature/non-us-registry-sweep-2026-08-09.json` lists the non-US endpoints as ISRCTN
(HTTP 200, `read: True`), EU CTIS (403), ANZCTR (403), jRCT (SSL handshake failure) and WHO ICTRP
(404, with its own field reading *"THE URL WAS A GUESS AND IT WAS WRONG. A 404 here is a defect in
this sweep, not a finding about ICTRP"*), and its summary reads *"THREE of the four non-US registries
refused automated access and ICTRP was not reached because this sweep's URL was wrong."* **WHO sits
outside the four.** The full stop puts it outside the enumeration, which is where the data puts it,
and matches the abstract's own *"Three further non-US registries refused automated access"*
(`emc-trial-reachability.md:49`).

### The numbers, both ways, from `lint_readability.py`

| metric | before | after |
|---|---:|---:|
| sentences | 78 | 80 |
| sentences over 60 w (`>60w`) | **1** | **0** |
| longest sentence (`max`) | **61 w** | **45 w** |
| mean sentence | 18.7 w | 18.2 w |
| p90 | 31 | 30 |
| FKGL | 11.4 | 11.3 |
| caution markers / 1000 w | 10.3 | **10.3** |

⚠ **Caution is byte-identical at 10.3/1000 w**, so clause 7's second failure mode — *"a FALL in
caution markers against the pinned baseline"* — is not approached. ⛔ **It could not have been
approached anyway, and that remains a hole rather than a pass:** `readability-baseline.json` →
`caution_per_1000w` has no entry for this document, so `was is None`
(`publish_bar.py:637`) and **half of clause 7 is UNMEASURED for this paper before and after the fix.**
S42 said so; re-measured here, it still holds.

---

## 2 · The guard that had never read this paper is armed — and proved load-bearing

`research/manuscripts/pinned-figures.json` → `targets` went **28 → 29**, inserting
`research/manuscripts/care-delivery/emc-trial-reachability.md` in sorted position between the ASO SI
and the degrader SI.

```
$ python3 research/manuscripts/lint_consistency.py     # before arming
lint_consistency: 0 ERROR across 28 target file(s)     # EXIT=0

$ python3 research/manuscripts/lint_consistency.py     # after arming
lint_consistency: 0 ERROR across 29 target file(s)     # EXIT=0
```

★ **It was armed at a clean moment and it stayed clean: no superseded value had to be registered, and
no pattern was loosened.** The cascade S42 warned about did not materialise.

⛔ **AND A GREEN TICK IS NOT COVERAGE, SO THE ARMING WAS MUTATION-TESTED** — on a scratch copy under
`/tmp/.../scratchpad/sprint/`, never the live tree (CLAUDE.md §6, the 13-inverted-claims incident).
`check_superseded` (`lint_consistency.py:593-612`) runs **all 81 registered patterns against every
target**, with no per-entry file scoping, and a target it cannot read raises `S-target-missing` — so
`0 ERROR` is evidence the file was read rather than skipped. Planting the registered superseded value
`about 95% of confirmed cases` into a copy of the paper produced:

```
S-aso_reagent_coverage_95pct  line 187  superseded value 'about 95% of confirmed cases'
                                        stated without marking it superseded
```

⚠ **The first mutation attempt was NOT caught, and the reason is worth recording.** Planted beside
the paper's own line `- **Statuses go stale.**`, the match was cleared: **`stale` is one of the 34
`supersession_markers`**, and `is_cleared` clears anything within ±2 lines / ±200 chars of a marker
(`_WINDOW_BACK = 2`, `_WINDOW_FWD = 1`, `_WINDOW_CHARS = 200`). Measured over this document: **19 of
163 non-blank lines (12 %) sit inside an auto-clearing window**, at lines 69-71, 106-110, 157-159,
178-180 and 200-204, produced by ordinary English the marker list also owns — `carried` (*"would have
carried both"*, *"the drafting were carried out"*), `the earlier` (*"a transport defect in the earlier
read"*), `at the time` and `stale`. ★ **So the guard now covers this paper, and covers 88 % of its
lines. That is a real gain and it is not total** — the residual is a known, documented trade in
`lint_consistency`'s own design notes (a linter that flags true statements gets ignored), not a new
defect, and it is stated here so nobody reads `0 ERROR` as 100 %.

---

## 3 · Every free gate, re-run over the tree carrying both edits

| gate | command | verdict, verbatim |
|---|---|---|
| readability | `python3 research/manuscripts/lint_readability.py <doc>` | `emc-trial-reachability.md  80 sent  mean 18.2  p90 30  max 45  >60w 0  FKGL 11.3  caution/1kw 10.3` · EXIT=0 |
| consistency | `python3 research/manuscripts/lint_consistency.py` | `lint_consistency: 0 ERROR across 29 target file(s)` · EXIT=0 |
| claims (R1-R5) | `python3 research/manuscripts/lint_claims.py` | `lint_claims: 0 ERROR, 172 WARN across 129 file(s)` · EXIT=0 · **zero rows of any severity name this document** (`grep emc-trial-reachability` over the full output returns nothing), and it **is** in scope: `DEFAULT_TARGETS` carries it, 129 entries |
| citations | `python3 research/manuscripts/lint_citations.py` | `lint_citations: 1086 prose identifier(s), 105 unanchored, 237 in ledger (known_absent_upstream=1, unverified_at_baseline=143, verified=93)` · EXIT=0 · **no row names this document**; the three retraction advisories are `nr4a3-druggability-reconciliation.md`, `nr4a3-degrader-paper.md` and `no-wet-lab-publication-archetypes.md`, all already `acknowledged` in `citation-retraction-sweep.json` |
| prose style | `python3 research/manuscripts/lint_style.py` | `lint_style: 0 ERROR across 14 file(s)` · EXIT=0 · ⛔ **this document is NOT among the 14** — see §4.2 |
| the fast six (frontmatter/graph/link tier) | `python3 scripts/fast_checks.py` | `the fast six: 6/6 PASS` · EXIT=0 — cross-document numeric consistency 2.43 s, manuscript language discipline 2.19 s, roadmap line citations resolve 1.33 s, EMC systems map invariants 1.95 s, systems model invariants + view drift 5.85 s, parser guard 0.03 s |
| research validator | `node scripts/validate-research.mjs` | `OK - 14 candidate(s) valid. 1 warning(s) (unverified claims to resolve before publication).` · EXIT=0 — the one WARN is `candidates[0] "imatinib-kit-subset" is T3`, unrelated to this paper |
| submission residue | `python3 research/manuscripts/lint_submission_residue.py` | `33 outgoing document(s), 5 finding(s), 5 baselined, 0 new, 0 stale baseline row(s)` · EXIT=0 |
| paralogue asymmetry | `python3 research/manuscripts/lint_asymmetry.py` | `0 new symmetric restatements of the paralogue requirement (2 known open, 1 accepted)` · EXIT=0 |

### 3.1 · R1-R5 read by hand, because an eligibility paper sits close to the line

`lint_claims` returns nothing on this document, and a hand read of all 204 lines agrees: the paper
never asserts that any intervention works, is safe, has a window, or is ready for the clinic. The
banner at `:26-29` says so explicitly — *"Nothing here asserts that any intervention works in this
disease"* — and the two named agents appear only as the eligibility facts of the trials that carry
them.

⚠ **The closest sentence to the line is `:147`, and it points the other way**: *"Excluding a
histology expected to respond poorly to the agents under test is an ordinary and defensible design."*
It is a statement about **non**-response, attributed as another trial team's design rationale, and it
is **weaker than its own source** — `non-us-registry-sweep-2026-08-09.json` writes *"a histology
**known** to respond poorly"* and the manuscript softened `known` to `expected to`. The underlying
claim is carried in-repo with citation at `research/data/emc-clinical-registry.json:1751` (*"perioperative
chemotherapy does not measurably improve metastasis-free or overall survival in localized EMC, which
is generally chemoresistant"*). **Not a blocker, and no narrowing is available that would not weaken
an already-hedged sentence.** Left as written.

### 3.2 · Identifier spot-check, since §7 of the paper is its data-availability claim

Every trial identifier in the manuscript traces to a committed fetch record read this session:
two of the three appear in `emc-trial-reachability-adjudication-2026-08-09.json` and all three in
`fet-fusion-trial-eligibility-2026-08-07.json`. Both enrolment figures the paper prints (`n = 73`,
`n = 5500`) appear verbatim in the adjudication record. No identifier in this memo or in that
manuscript was written from recollection.

---

## 4 · What the gates still cannot see

**4.1 · The endpoint claims three variables; the paper defends one. Verified independently, not
inherited.** `systems/graph/publications.json` → `PUB-STRATEGY-ARCH.what_it_would_claim` spans *"when,
in what order, and whether the patient can reach a trial at all"* and then says so against itself:
*"⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY … the other two are now graded as closed
(RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit) … but they are NOT in the drafted
manuscript yet."* ⛔ **Clause 5 checks that this text is ≥40 characters and that the document file
exists. It does not check that the document defends the text**, so a 7/7 would clear a paper narrower
than its own registered endpoint. The manuscript's own title and `scope` are honest about being
reachability-only; the mismatch is in the graph, and the disclosure lives there rather than in the
outgoing text. **Whoever posts must either narrow the endpoint or fold the other two routes in.** Not
a bar failure, not this seat's call, and it costs nothing but a decision.

**4.2 · A SECOND gate has never read this paper, and S42 did not find it.**
`research/manuscripts/lint_style.py` → `TARGETS` is a hand-maintained list of **14** files whose own
comment reads *"⛔ SUBMISSION TEXTS ONLY. A memo, a plan or a findings note must not be added here"*.
`emc-trial-reachability.md` is not in it, so the bold-density, em-dash-density and prose-style gate
has never looked at a document whose `target_venue` is `preprint`. ★ **This is exactly the shape of
the hole this seat just closed for `lint_consistency`** — a paper heading outward, sitting outside a
gate that only knows a hand-typed list — and the same argument applies: the moment it becomes a
submission text it belongs in `TARGETS`, precedent being the ASO journal article (added 2026-08-12
*"WHEN IT BECAME A SUBMISSION TEXT"*) and the vaccine path (added 2026-08-19). ⛔ **This seat did not
add it**, because `lint_style.py` is outside its permitted paths and because adding a file to that
list is a scope call with a cascade — it is one line and one run for whoever takes it, **free, and
nobody's but the loop's.**

**4.3 · No readability baseline is pinned** (§1) and **no PDF build target exists** —
`build_submission_pdf.py` → `PAPERS` has three keys and none is this paper. Neither is a bar clause.
Both re-verified this session.

---

## 5 · The bar, re-run, and what it will read once the edit is committed

⛔ **Every clause reads `git show <sha>:<doc>`, not the working tree** (`publish_bar.py:598` — *"a bar
that reads the working tree measures a paper nobody is publishing"*; the call is at `:610`). This seat
may not commit, so **at HEAD the bar is unchanged from S42's reading and clause 7 still FAILs on the
61-word sentence that no longer exists in the tree.** That is the bar being correct, not a
regression.

```
$ python3 research/autonomy/publish_bar.py --paper PUB-STRATEGY-ARCH --sha b4cf28c6be8f…
PUB-STRATEGY-ARCH @ b4cf28c6be8f -> BLOCKED (3/7 clauses)
  [FAIL] the outgoing text is readable and keeps its caution
         1 sentence(s) over 60 words … (longest 61w at line 165)
  authority: OK — granted: trimcrae, 2026-08-26, AskUserQuestion D1, verbatim: 'Broad: any paper meeting the bar'
```

Clause 7's own code path, run against the working-tree bytes the driver will commit — same
`lint_readability.measure`, same `SENTENCE_CEILING = 60`, same baseline lookup:

```
over_ceiling = 0 | max_len = 45 | mean = 18.2 | FKGL = 11.3 | caution = 10.3 | baseline = None
VERDICT: PASS — no sentence over 60w (longest 45w, mean 18.2w, FKGL 11.3),
                caution 10.3/1000w (no baseline pinned)
```

| # | clause | at HEAD | once the split is committed | what closes it | $ | trimcrae? |
|---:|---|---|---|---|---|---|
| 1 | `hardening_converged` | UNMEASURED | UNMEASURED | one hardening round on the final sha → `hardening-state/PUB-STRATEGY-ARCH.json`, `blockers` empty, `seats` all closed at that sha. `_look_history` returns `{}` so `widest = 0` and no width floor binds | $0 | no |
| 2 | `preflight_full_green` | UNMEASURED | UNMEASURED | `PREFLIGHT_FULL=1` on the final sha, log committed, receipt digest-bound | $0, ~25 min | no |
| 3 | `claim_ceiling_honoured` | **PASS** | **PASS** | — | — | — |
| 4 | `identifiers_resolvable` | **PASS** | **PASS** | — (corpus-wide, so any unresolved identifier anywhere re-reds it) | — | — |
| 5 | `endpoint_declared` | **PASS** | **PASS** | — (but see §4.1: it does not test that the paper defends the endpoint) | — | — |
| 6 | `independent_adversarial_seat` | UNMEASURED | UNMEASURED | one blind seat on the final sha → `review-seats/PUB-STRATEGY-ARCH-<sha>.json`, `document_sha256` re-derived by the clause | $0 | no |
| 7 | `readable_enough_to_review` | **FAIL** | **PASS** (derived above) | **done, in the tree** | $0 | no |

**Tally: 3/7 BLOCKED at HEAD; 4/7 BLOCKED with 0 FAIL once the split lands.** Authority is OK and
`PUB-ASO` remains the only entry in `scope.excluded_papers`.

⛔ **Order still binds and did not change.** Clauses 1, 2 and 6 are sha-bound; the split moves the
sha. **Split → commit → freeze → then the seat, the round and the FULL run in parallel against that
frozen sha.** Doing the 25-minute one first buys a receipt for a commit nobody posts.

## 6 · What this seat did and did not do

- **Did:** read S42 in full and re-derived each of its four verifiable claims from the deciding
  artifact; read the failing sentence in place and checked it against the sweep record before
  touching it; applied the split; re-ran `lint_readability` both ways; added the document to
  `pinned-figures.json` → `targets` and ran `lint_consistency` before and after; read
  `check_superseded` and `is_cleared` and mutation-tested the arming on a scratch copy, twice,
  measuring the clearing-window coverage; ran claims, citations, style, residue, asymmetry, the fast
  six and the research validator; hand-read all 204 lines against R1-R5; spot-checked every trial
  identifier and both enrolment figures against committed fetch records; re-ran the bar at HEAD and
  derived clause 7's post-commit verdict from its own code path.
- **Did not:** post, submit, deposit or send anything; run any git write command; run
  `PREFLIGHT_FULL=1`; touch the ledger, the graph, any generated view, `lint_style.py` or any file
  outside the two named above; weaken a hedge; write any identifier from memory.
