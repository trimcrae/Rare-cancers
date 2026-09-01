# S14-DETECTOR — a mechanical detector for the symmetric-paralogue-requirement defect

**Item(s):** AUT-009 · **Owned paths:** `research/manuscripts/lint_asymmetry.py` (NEW — the detector),
`research/manuscripts/tests/test_lint_asymmetry.py` (NEW — its tests), this file.
**Started (UTC):** 2026-09-01T19:0x · **Finished (UTC):** 2026-09-01T21:1x

⭐ **PATH DECLARED BEFORE WRITING, per the seat prompt:** the detector is
`research/manuscripts/lint_asymmetry.py`, beside the `lint_*.py` prose-guard family
(`lint_claims`, `lint_citations`, `lint_consistency`, `lint_style`, `lint_submission_residue`,
`lint_changed_prose`, `lint_readability`, `lint_citation_types`). Its tests are
`research/manuscripts/tests/test_lint_asymmetry.py`.

---

## Verdict

**FIXED (detector built and measured) — and it found two live defects the hand sweep missed.**
Recall **19/19** of the 2026-08-07 sweep's symmetric-restatement sites, **1 false positive** in 23
findings over the same pre-sweep corpus, **~3.1 s** to scan 1,919 files. On today's tree it returns
**0 new findings, 2 known-open defects** (both live, both in
`degrader/nr4a3-degrader-broader-indications.md`, both present *before* the sweep and left by it)
and **1 accepted non-defect**.

---

## 1 · Refute first — does the defect still exist, and is anything already detecting it?

The row's claim is *"nothing mechanical detects the next symmetric restatement."* **It stands.**

```
$ grep -rln "sparing" --include=test_*.py .
research/modalities/tests/test_nr4a1_sparing_axis.py        <- tests nr4a1_sparing_axis.py's ARITHMETIC
research/modalities/tests/test_nr4a2_sparing_bound.py       <- tests the MGI/HPA artifact
research/modalities/tests/test_selectivity_fingerprint.py   <- tests a docking artifact
research/manuscripts/tests/test_paired_numeric_lists_are_bound_in_the_right_order.py
```

Every hit tests a computed artifact. **No guard reads prose for this defect**, and
`systems/views/L2-rt-asymmetric.md`'s "Required validation" table says so itself: *"The asymmetry
carried through every downstream selectivity statement rather than stated once | ⛔ **none built**"*.

The route record and the ledger row are byte-identical (`systems/graph/routes.json:1530` →
`best_next_action`), so the row is not stale.

## 2 · The specification comes out of the sweep's record, not out of an idea

The sweep is commit **`9f560a5ad`** (2026-08-07T00:41:56Z), *"Carry the NR4A1/NR4A2 asymmetry through
24 sites"*. Its message carries the triage numbers the ledger quotes: **1,354 raw hits → 126
requirement-shaped lines → 24 confirmed defects in 18 files; ~1,330 considered and deliberately
left.** I reconstructed the pre-sweep tree (`git archive 9f560a5ad^`) and parsed every removed line
out of the diff — 42 contiguous removal groups across 24 files.

**Reading those 42 groups shows the sweep fixed THREE different defects at once, and the ledger's
prose runs them together.** The detector targets the first and says so:

| class | what it is | groups | detector |
|---|---|---|---|
| **A · symmetric one-bar restatement** | the REQUIREMENT / BRIEF / DESIGN TARGET stated as one bar over both paralogues — *"NR4A1/2-sparing"*, *"it has to spare NR4A1 and NR4A2"*, *"selectively over NR4A1 and NR4A2"* | **19 statement sites in 15 documents** | ✅ this file |
| **B · a superseded FACT inside an already-asymmetric sentence** | *"NR4A2-sparing is unbounded in both directions"* (R7, its `requirements.json` record, §2.4's row label, `target-route-options.md`) — the sentence already carries the asymmetry and is still wrong | 8 groups | ❌ out of scope, in `NOT_BOUND`; this is `lint_consistency`'s axis (a pinned figure), not a register axis |
| **C · the closed PK/CNS-exposure lever** | *"source NR4A2 safety from PK/CNS-exclusion as the primary lever"* (selectivity architecture, SI safety note, carT framing) | 6 groups | ❌ out of scope, in `NOT_BOUND` |
| **D · bookkeeping / generated mirrors** | `routes.json` `best_next_action`, the four `systems/views/**` files that were regenerated | 9 groups | n/a — views are generated from the graph, which IS scanned |

⚠ **The ledger says "16" and the mechanical count of class A is 19 sites in 15 documents.** The
ledger's list (*"requirement R7 and its graph record, RT-DEGRADER purpose, the degrader design spec,
the treatment roadmap, the selectivity architecture, the paper heading and SI safety note, three
companion fusion papers, the indication stack, the outreach template and two module docstrings"*)
names fifteen items, three of which (R7, its graph record, the SI safety note) are class **B/C**, and
omits the ensemble redesign brief, the positioning memo and the framing-options register, which are
class A. **I report against the mechanical set, not the prose count**, and both are listed below.

**The four properties every class-A site shares** (this is the spec, and each is quoted from a real
pre-sweep line):

1. **PAIR** — both paralogues in one coordinated unit: `NR4A1/2`, `NR4A1/NR4A2`, `NR4A1 and NR4A2`.
   ⛔ `NR4A1/NR4A3` is the anti-target **genotype** and `NR4A1/2/3` is the **pan-NR4A** CAR-T mode —
   the opposite requirement. Both must be excluded, and both produced false positives before they were.
2. **BAR** — a sparing / selectivity / non-engagement / counterexample predicate over that unit.
3. **REGISTER** — the statement is a requirement, not a report. `must` / `has to` / `design target` /
   `advancement standard` / front-matter `purpose:` / `designed to be` / an **adjectival compound on a
   design noun** (`"an NR4A3-selective (NR4A1/2-sparing) warhead"` — the paper heading, which carries
   no deontic word at all) / a **criteria-list lead-in** (`"It is a candidate for which:"` above six
   numbered bars).
4. **THE ASYMMETRY IS ABSENT** from the enclosing block — no `asymmetr`, `HARD half`/`SOFT half`,
   `mandatory` beside `best-effort`, `not one constraint`, or §2.4 link.

Plus one exemption that is not negotiable: **a sentence carrying `Superseded, retained` is skipped.**
The sweep left all its superseded phrasings inline on purpose (CLAUDE.md rule 1.2); a guard that fired
on the record of its own fix would be uninstalled inside a week.

★ **And the sweep's own root cause is implemented as a rule.** Its commit message: *"a heading and its
body disagreeing means the heading wins everywhere it is quoted, because a heading is what gets
quoted."* So **a heading is its own block and gets no exemption from the paragraph under it**, while a
body block inherits its heading. That single rule is what found live defect #1 below.

## 3 · ⭐ THE MEASUREMENT

### 3a · Recall and false positives against the pre-sweep corpus

```
$ git archive 9f560a5ad^ | tar -x -C <scratch>/pre
$ python3 research/manuscripts/lint_asymmetry.py --root <scratch>/pre --report --explain
... 23 findings, 3.1 s
```

| # | finding | verdict |
|---|---|---|
| 1 | `emc-treatment-roadmap.md:274` | **TP** — class-A site (*"the design target is NR4A3-selective, NR4A1/2-sparing"*) |
| 2 | `fusion-coactivator-ppi-paper.md:87` | **TP** — companion paper 1 |
| 3 | `fusion-condensate-disruption-paper.md:116` | **TP** — companion paper 2 |
| 4 | `fusion-selective-andgate-degrader-paper.md:318` | **TP** — companion paper 3 |
| 5 | `nr4a3-degrader-broader-indications.md:8` | **TP** — front-matter `purpose:` |
| 6 | `nr4a3-degrader-broader-indications.md:23` | **TP** — *"it has to spare NR4A1 and NR4A2"* |
| 7 | `nr4a3-degrader-broader-indications.md:25` | **TP, duplicate** — second sentence of the same rewritten paragraph |
| 8 | `nr4a3-degrader-broader-indications.md:30` | ⭐ **TP the sweep MISSED** — still live today (see §4) |
| 9 | `nr4a3-degrader-broader-indications.md:31` | **TP** — *"safe only if NR4A1/2 are spared"* |
| 10 | `nr4a3-degrader-broader-indications.md:37` | ⭐ **TP the sweep MISSED** — still live today (see §4) |
| 11 | `nr4a3-degrader-broader-indications.md:91` | **TP** — the manuscript paragraph |
| 12 | `nr4a3-degrader-outreach-emails.md:141` | **TP** — the outreach template |
| 13 | `nr4a3-degrader-paper-positioning.md:68` | **TP** |
| 14 | `nr4a3-degrader-paper.md:608` | **TP** — the paper §2.4 heading |
| 15 | `nr4a3-degrader-selectivity-architecture.md:171` | **TP** |
| 16 | `paper-framing-options.md:587` | **TP** — the register row quoting that heading |
| 17 | `nr4a3-abfe-repair-prereg.md:93` | ⛔ **FALSE POSITIVE** (the only one — see §5) |
| 18 | `nr4a3-degrader-design-spec.md:44` | **TP** — *"→ Design target: NR4A3-selective, NR4A1/2-sparing"* |
| 19 | `nr4a3-ensemble-redesign-brief.md:36` | **TP** — criteria item 4 |
| 20 | `nr4a3-ensemble-redesign-brief.md:174` | **TP** — the advancement standard |
| 21 | `nr4a3_warhead.py:10` | **TP** — module docstring 1 |
| 22 | `nr4a_selectivity.py:5` | **TP** — module docstring 2 |
| 23 | `systems/graph/routes.json:130` | **TP** — RT-DEGRADER `purpose` |

**⭐ RECALL: 19 / 19 class-A sites = 100 %.** Every line number lands on the statement itself, not on
its paragraph.
**⭐ FALSE POSITIVES: 1 of 23 findings (4.3 %).**
Also returned: 1 duplicate of a counted site, and **2 true findings the hand sweep did not make**.

⛔ **It recovers 0 of the 8 class-B and 0 of the 6 class-C groups, and that is by design, not a
shortfall** — both are different defects with different remedies, and both are written into
`NOT_BOUND` rather than left to be discovered by someone assuming coverage.

### 3b · The operating point on today's tree

```
$ python3 research/manuscripts/lint_asymmetry.py
⚠ KNOWN OPEN  research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:35 (baselined 2026-09-01)
⚠ KNOWN OPEN  research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:44 (baselined 2026-09-01)
lint_asymmetry: 0 new symmetric restatements of the paralogue requirement (2 known open, 1 accepted)
exit 0        # and `--strict` exits 1 while an open defect stands
```

**Cost: 3.15 / 3.04 / 3.14 s over three runs**, 1,919 files. ~10 % of the 31 s fast-gate tier.

Three optimisations were each **profiled per file, not guessed**, and all three are recorded in the
source with the numbers that forced them:
* the whole-file literal pre-check `"NR4A1" in text` before any regex (`_PAIR_EXPLICIT` has no literal
  prefix and walks all 96 MB of `emc-ret-cistrome-inputs.json`);
* JSON scanned **from the pair outward** rather than parsed — `json.loads` on that one file cost
  **3.0 s of a 5.1 s run**, and a value-shaped regex made it **worse at 11.8 s**;
* the first draft resolved JSON line numbers with a Python loop over every line per value, which ran
  the whole gate **past its 120 s timeout**. Diagnosed by timing every file under a 3 s `SIGALRM`.

## 4 · ⭐ TWO LIVE DEFECTS, FOUND BY THE DETECTOR, NOT FIXED BY THIS SEAT

Both are in `research/manuscripts/degrader/nr4a3-degrader-broader-indications.md` — **the same file in
which the sweep rewrote three other statements.** Both were present before the sweep (they appear in
the pre-sweep run at lines 30 and 37) and both survived it unchanged.

1. **`:35` — a SECTION HEADING.**
   `## Framing: the indication must want NR4A3 *down* AND NR4A1/2 *spared*`
   The paragraph immediately below it *is* correct: it links §2.4 and carries a `Superseded, retained`
   note for line 31. **The heading was not updated with it** — which is precisely the mechanism the
   sweep's own commit message names as the root cause. It is why the heading rule exists in this guard.

2. **`:44` — the section's opening sentence.**
   `These all want NR4A3 removed and NR4A1/2 spared — the *same* molecule we design for EMC.`

⛔ **I did not touch the prose** — the seat prompt forbids editing manuscripts, and this is another
seat's file tonight. Both are entered in the detector's `BASELINE` with
`verdict: "open-defect"`, they **print on every single run**, and `--strict` fails while they stand.
A ledger row for the fix is proposed in §8.

## 5 · The one false positive, and why it is baselined rather than regexed away

`research/modalities/nr4a3-abfe-repair-prereg.md:93` — *"An unqualified 'selective vs NR4A1 AND NR4A2'
statement requires NR4A1 independent replicates until its 95 % t-interval is entirely below zero."*
This is a **reporting rule that REFUSES the symmetric claim**, i.e. the opposite of the defect, and its
own section separates the halves. Clearing it by rule would mean a regex tuned to one sentence, so it
is a `BASELINE` row with `verdict: "not-a-defect"` and the reason written out.

⚠ **And it surfaced something a linter cannot adjudicate, so it is reported here instead.** That
section is headed *"Both anti-targets for an UNQUALIFIED selectivity claim"* and states **"NR4A2 is the
primary gate (harder paralogue), but NR4A1 cannot be ignored."** Program-map §2.4 says the opposite:
**NR4A1-sparing is the HARD, evidenced-mandatory half.** Two live documents disagree about which half
is which. This is not a symmetric restatement and this guard is right not to fail on it — but it is a
real inconsistency and somebody should decide which reading is current. Proposed as a ledger row in §8.

## 6 · Mutation testing — both directions, both in scratch copies

**(a) The corpus.** A `cp -r` copy of `research/` + `systems/` into scratch. For nine files, the
**pre-sweep version was copied over the corrected one** and the guard re-run:

```
RED    program/emc-treatment-roadmap.md: 1 finding [274]
RED    degrader/nr4a3-degrader-paper.md: 1 finding [608]
RED    degrader/nr4a3-degrader-outreach-emails.md: 1 finding [141]
RED    modalities/nr4a3-degrader-design-spec.md: 1 finding [44]
RED    modalities/nr4a3_warhead.py: 1 finding [10]
RED    modalities/nr4a_selectivity.py: 1 finding [5]
RED    systems/graph/routes.json: 1 finding [130]
RED    fusion-direct/fusion-condensate-disruption-paper.md: 1 finding [116]
RED    modalities/nr4a3-ensemble-redesign-brief.md: 2 findings [36, 174]
all restored; scratch copy clean: True
```

**(b) The guard's own rules.** Nine single-site mutations, one per rule, each run against the test
file. **All nine go red** — no rule is unbound by a test:

```
RED (good)  rule1 pair -> never matches          RED (good)  rule5 superseded -> never exempts
RED (good)  rule2 bar -> always matches          RED (good)  heading blocks glued to bodies
RED (good)  rule3 register -> always matches     RED (good)  adjectival rule disabled
RED (good)  rule4 asymmetry -> always exempts    RED (good)  criteria-list rule disabled
RED (good)  triple lookahead removed
```

⛔ **PROCESS DEFECT I COMMITTED, REPORTED RATHER THAN TIDIED AWAY.** Round (b) mutated
`research/manuscripts/lint_asymmetry.py` **in the live working tree** — a write-then-restore loop —
instead of a scratch copy. That is the exact 2026-08-27 shape (CLAUDE.md §6): eleven other seats were
running, and a `git add -A` inside that window would have captured a deliberately broken guard. The
file was byte-restored from a pre-mutation backup and verified (`diff -q` → identical), the window was
about 40 s, and the tests pass on the restored file. **It should have been an `EnterWorktree` or a copy
of the module under `tmp_path`, and the correct shape is what round (a) and every shipped test already
do.** Flagging it so the driver diffs this path before staging.

## 7 · Where the guard should be wired, and what it would cost

⛔ I did **not** touch `scripts/preflight.sh` — another seat owns it tonight.

★ **Recommendation: bolt it onto gate 6's call site, not onto a new gate heading.** Preflight gate
ordinals are derived from `preflight.sh`'s `== heading ==` lines by
`systems_check.check_preflight_gate_list` and are hard-coded in four other documents, so **a new
heading renumbers every gate below it.** `lint_citation_types` solved exactly this by being invoked
from `lint_citations.check()` rather than getting its own heading, and that precedent is written into
its header. Two options, in order of preference:

1. **Call it from `lint_claims.py`'s `check()`** (gate `== lint_claims ==`, already in the commit loop
   and in `tests.yml`). One import and one call; no gate renumbering; no `preflight.sh` edit at all.
   `lint_claims` is the right neighbour: it owns claim STRENGTH, this owns claim SHAPE.
2. If a standalone line is wanted anyway, append it **below** the last existing gate heading so no
   ordinal moves, and accept the four-document update.

**Cost at that site: +3.1 s** measured (3.15 / 3.04 / 3.14 s over 1,919 files), against a ~31 s fast
tier — about **+10 %**. It is stdlib-only, offline, deterministic, needs no cache and no network, so it
is safe in both preflight and `tests.yml`. It also runs standalone:
`python3 research/manuscripts/lint_asymmetry.py`.

⚠ **The gate is GREEN on the committed tree today** — that is what makes it wireable. The two live
defects are baselined as `open-defect` and print loudly on every run; a **new** symmetric restatement
is red on its first commit.

## 8 · What I changed

| path | what |
|---|---|
| `research/manuscripts/lint_asymmetry.py` | **NEW**, 774 lines (the header and the inline rule notes carry the measurements that forced each rule). Five rules, three finding classes, a `BASELINE` of 3 rows keyed on the sentence's own sha1, a `NOT_BOUND` list of 7 written-down holes (printed by `--not-bound`), `--report` / `--explain` / `--strict` / `--not-bound` / `--root`. |
| `research/manuscripts/tests/test_lint_asymmetry.py` | **NEW**, 306 lines / 20 tests, all passing (12.1 s). One per finding class, one per must-not-fire class, the heading rule in both directions, the baseline's digest semantics, a staleness check on every baseline row, and the gate-green contract. Every corpus is a fresh `tmp_path` subtree. |
| `research/autonomy/sprint-2026-09-01/S14-DETECTOR.md` | this file |

Nothing else. **No manuscript, no ledger, no `preflight.sh`, no git write command.**

### Gates run (scoped, per charter §6)

```
$ python3 -m pytest research/manuscripts/tests/test_lint_asymmetry.py -q      20 passed in 12.12s
$ python3 research/manuscripts/lint_consistency.py                            0 ERROR across 26 files
$ python3 research/manuscripts/lint_claims.py                                 0 ERROR, 170 WARN across 129 files
$ python3 -m py_compile <both new files>                                       OK
```

⚠ **Two things I saw that are NOT mine and are reported, not touched:**
* `python3 research/manuscripts/lint_style.py` exits **1** — `bold-midsentence` at
  `research/manuscripts/neoantigen/emc-vaccine-development-path.md:653` (`**less**`). Nothing to do
  with these files (`grep lint_asymmetry` over its output: 0 hits).
* The first pytest run aborted in `pytest_sessionfinish` with
  `tracked_tree_guard.assert_tree_unchanged` naming four modified paths I do not own
  (`methods-record/closed-routes-negative-record.md`, `methods-record/degrader-methods-failure-record.md`,
  `modality-census/cancer-modality-census.md`, `neoantigen/hla-coverage-emc.md`). This is the
  sprint-wide hazard the seat prompt names. Re-ran once; clean. **Not my writes** — my tests only ever
  write under `tmp_path`.

## 9 · What I could not do, and what it is actually waiting on

* **Fixing the two live defects (§4).** Waiting on **nothing but permission** — the seat prompt says
  report, do not fix, and `nr4a3-degrader-broader-indications.md` is not an owned path. Both are one
  sentence each and the corrected wording already exists three paragraphs away in the same file.
* **Class B and class C detectors** (§2). Waiting on a decision, not on data: B is a pinned-figure
  problem (`lint_consistency`'s axis, and §2.4's `nr4a2-sparing-bound.json` is the pin), C is a
  claim-about-a-nonexistent-molecule problem closer to `lint_claims`. Neither belongs in this module.
* **`systems/views/**` coverage.** Deliberately out of scope, not blocked: views are generated from
  `systems/graph/*.json`, which **is** scanned, and a hand-edit there fails the build.
* **Wiring (§7).** Waiting on the driver, because `preflight.sh` belongs to another seat tonight.

## 10 · Ledger rows the driver should write

I may not write these.

1. **`what`:** "Fix the two live symmetric restatements `lint_asymmetry` found on 2026-09-01 in
   `research/manuscripts/degrader/nr4a3-degrader-broader-indications.md`: the section heading at :35
   (`## Framing: the indication must want NR4A3 *down* AND NR4A1/2 *spared*`) and the sentence at :44
   (`These all want NR4A3 removed and NR4A1/2 spared`). Both predate the 2026-08-07 hand sweep and
   both survived it; the corrected wording already exists three paragraphs above in the same file, and
   the heading is the exact failure mode that sweep's own commit message names. Register the replaced
   text inline (CLAUDE.md rule 1.2), then delete the two `open-defect` rows from
   `lint_asymmetry.BASELINE` — `test_every_baseline_row_still_matches_something_in_the_tree` will fail
   until they are. `python3 research/manuscripts/lint_asymmetry.py --strict` is the acceptance test.
   ⛔ Raises no selectivity claim: both statements stay unvalidated predictions."
   **`kind`:** `correction` · **`state`:** `queued` · **`cost_class`:** `free` ·
   **`serves`:** route `RT-ASYMMETRIC`, publication `PUB-DEGRADER`, strategy `ST-OCCUPANCY`

2. **`what`:** "Wire `lint_asymmetry` into the commit loop. Preferred: call it from
   `lint_claims.check()` so no `== heading ==` is added and no preflight gate ordinal moves — the
   precedent and its reasoning are in `lint_citation_types.py`'s header. Measured cost **+3.1 s**
   (3.15 / 3.04 / 3.14 s over 1,919 files) against a ~31 s fast tier. Stdlib-only, offline,
   deterministic, green on the committed tree. ⛔ A guard nothing runs is `subagent_width` again."
   **`kind`:** `infrastructure` · **`state`:** `queued` · **`cost_class`:** `free`

3. **`what`:** "Decide which paralogue is the HARD half, because two live documents disagree.
   `research/modalities/nr4a3-abfe-repair-prereg.md` §5 says *'NR4A2 is the primary gate (harder
   paralogue), but NR4A1 cannot be ignored'*; `nr4a3-program-map.md` §2.4 says NR4A1-sparing is the
   HARD, evidenced-mandatory half (a named combination anti-target genotype) and NR4A2-sparing the
   SOFT, best-effort half. Both may be right about different things — the prereg means *molecularly*
   harder (I531 is Ile in NR4A3 and NR4A2, so only 4 of 5 engageable handles distinguish it) while
   §2.4 means *evidentially* mandatory — but nothing in either document says so, and 'harder' is doing
   two jobs. Surfaced by `lint_asymmetry` on 2026-09-01 as its single false positive; it is a prose
   decision, not a linter matter."
   **`kind`:** `correction` · **`state`:** `queued` · **`cost_class`:** `free` ·
   **`serves`:** route `RT-ASYMMETRIC`

4. **`what`:** "Close AUT-009's open validation. `RT-ASYMMETRIC`'s 'Required validation' row reads
   *'The asymmetry carried through every downstream selectivity statement rather than stated once |
   instrument: ⛔ none built'*. The instrument is now built
   (`research/manuscripts/lint_asymmetry.py`, 19/19 recall on the 2026-08-07 sweep's own sites, 1
   false positive in 23, ~3.1 s) and its findings file is
   `research/autonomy/sprint-2026-09-01/S14-DETECTOR.md`. Update `systems/graph/routes.json` →
   `RT-ASYMMETRIC` `required_validation` and `best_next_action`, then regenerate the views. ⛔ Do NOT
   mark the validation PASSED while the two open defects of row 1 stand — the instrument exists, the
   corpus is not yet clean."
   **`kind`:** `infrastructure` · **`state`:** `queued` · **`cost_class`:** `free` ·
   **`serves`:** route `RT-ASYMMETRIC`

## Amendment record for the driver

`**/tests/**` is governed and I may not append to `amendments.jsonl`. Ready to paste:

```json
{"utc": "2026-09-01T21:15:00Z", "actor": "S14-DETECTOR (sprint-2026-09-01 wave 1)", "path": "research/manuscripts/tests/test_lint_asymmetry.py", "action": "add", "governed_reason": "**/tests/** is governed; a new test file is an amendment to the guard surface", "what": "20 tests for the new prose guard research/manuscripts/lint_asymmetry.py: one per finding class (requirement-register, adjectival-design-compound, criteria-list-item, JSON graph record, module docstring), one per must-not-fire class (a symmetric MEASUREMENT, a block that already carries the asymmetry, a `Superseded, retained` quotation, the NR4A1/2/3 pan-NR4A triple, the NR4A1+NR4A3 anti-target genotype), the heading rule in both directions, the BASELINE's sha1 semantics, a staleness check on every baseline row, and the gate-green / --strict contract.", "why": "AUT-009 -- the 2026-08-07 corpus sweep was a hand measurement that decays; RT-ASYMMETRIC's required-validation row read `instrument: none built`. Every test mutates a fresh tmp_path corpus rather than asserting a clean tree, because a guard that fails OPEN and a guard that is satisfied render identically.", "measurement": "20 passed in 12.34 s. Guard recall 19/19 against the sweep's own class-A sites on the reconstructed pre-sweep tree (git archive 9f560a5ad^), 1 false positive in 23 findings, ~3.1 s over 1,919 files. Nine single-site mutations of the guard's own rules were run against this suite and all nine went RED -- no rule is unbound by a test.", "writes_to_tracked_files": false, "risk": "low -- pure additions; no existing test, guard, gate or manuscript was modified"}
```
