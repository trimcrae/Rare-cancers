---
id: DOC-SPRINT-S6-COMMITLOOP
title: "S6-COMMITLOOP — the commit loop's pinned cost, re-measured and re-attributed"
level: L3
kind: memo
status: live
date: 2026-09-01
last_verified: 2026-09-01
purpose: "Re-measure what `./scripts/preflight.sh` actually costs, attribute the growth of its pytest gate with a real diagnostic, and record the corrections made to CLAUDE.md §6, scripts/preflight.sh and pinned-figures.json (AUT-PD-164 / AUT-PD-172 / AUT-PD-183)."
scope: "The DEFAULT preflight tier only, measured in this dev sandbox on 2026-09-01 under twelve-way sprint contention, plus CI run 33523366953 as the uncontended reference. NOT a verdict on any gate — the tree was mutating throughout. NOT a decision about re-tiering gate 13, which CLAUDE.md §6 reserves for trimcrae."
audience: [autonomous research agents, maintainers]
---

# S6-COMMITLOOP — the commit loop's pinned cost, re-measured

**Item(s):** AUT-PD-164, AUT-PD-183, AUT-PD-172
**Owned paths:** `scripts/preflight.sh`, `scripts/affected_tests.py`, `scripts/selector-validation.json`,
`CLAUDE.md` (§6 cost figures only), `research/manuscripts/pinned-figures.json` (this figure only),
this file
**Started (UTC):** 2026-09-01T18:40:21Z   **Finished (UTC):** 2026-09-01T19:30Z

## Verdict

**FIXED (the pin) + PARTIAL (the cost), with one hypothesis refuted and two new defects found.**
The commit loop is **~9 minutes on a quiet box, not 75 seconds** — fast gates **81.3 s**, gate 13
**446.3 s** quiet and **1 247.8 s** under tonight's twelve-way contention — so gate 13 is **85–94 %
of the loop**, not half of it; CLAUDE.md §6, `scripts/preflight.sh`'s comments and
`pinned-figures.json` are corrected in this change. The growth is **scope and population, not a
per-test regression** — settled on one machine by re-timing the five byte-identical 2026-08-24 files
(79 tests / 74.4 s today against 55 / 39.3 s then, i.e. 0.94 vs 0.72 s per test on a box carrying
eleven other seats). AUT-PD-183's "one slow file serializes the gate" is **refuted** by CI's own
`--durations=25`. ⭐ **And the real hot spot is now named and quantified: 48 230 of the gate's
50 270 `git` calls — 96 % — are `git show <sha>:research-ledger.json`, i.e. 130 complete repeated
walks of the ledger's history at 7.5 s each, ~55 % of gate 13, growing with every commit rather
than with every test.** The fix is memoisation plus `git cat-file --batch` and changes no assertion,
but it lives in `research/autonomy/stuck_clock.py`, which this seat does not own — written up as a
ledger row rather than taken.

## What I measured

### 0 · The instrument, and what it can and cannot say tonight

One `./scripts/preflight.sh` (default tier, no flags), started 2026-09-01T18:40:2xZ, run
`run_in_background` with every stdout line prefixed by seconds-since-start and an `EXIT=` marker
appended on the last line. Log:
`…/scratchpad/preflight-default.log`.

⛔ **The verdict of that run is meaningless and is not reported as one. Only the timings are.**
Eleven sibling seats were mutating the same working tree throughout. Two things went red for that
reason and neither is evidence about anything:

* gate 2 (systems model) failed inside the run, on whatever another seat had in flight;
* **gate 13 ended in `tracked_tree_guard.assert_tree_unchanged`**, naming
  `research/manuscripts/tests/test_the_census_word_covered_survives_ablation.py`,
  `research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py` and
  `scripts/regenerate_aso_chain.sh` — three files this seat does not own. The guard raises in
  `pytest_sessionfinish`, **after** the run, so it replaced pytest's own summary line and preflight
  then reported `pytest reported no test count -- the run collected nothing`. **The tests did run**
  — the stage occupied 1 247.8 s of four busy workers — but their pass/fail list was eaten by the
  guard. This is the sprint-wide hazard the coordinator flagged at ~19:00Z, observed independently
  here; it does not affect a wall-clock reading and it destroys a verdict.

Load average over the run climbed 1.2 → 12.1 on a 4-core box, so every wall-clock number below is an
**upper bound taken under twelve-way contention**, labelled as such rather than presented as the
machine's clean cost.

### 1 · The fast-gate tier is 81.3 s, not 31.4 s

Derived from the timestamped log (each gate's cost is the interval to the next `== … ==` banner):

| | s |
|---|---|
| start-up: `dev-setup.sh --if-needed` + the interpreter/dep probe, before gate 1 | 15.34 |
| 1 `lint_consistency` | 2.25 |
| 2 systems model | 7.67 |
| 3 EMC systems map | 4.08 |
| 4 claim strength (`lint_claims`) | 2.16 |
| 5 changed prose | 0.04 |
| **6 citation provenance + publication type** | **44.40** |
| 7 manuscript prose style | 0.30 |
| 8 readability screen | 0.27 |
| 9 parser guard | 0.04 |
| 10 registry evidence contract | 0.24 |
| 11 generated deposit artifacts | 4.44 |
| 12 cycle-receipt fan-out width | 0.05 |
| **fast gates, total, to the moment the pytest gate starts** | **81.28** |

⭐ **The single largest fast gate is citation provenance at 44.4 s — 55 % of the tier.** Its own line
says why: `1068 prose identifier(s), 106 unanchored, 237 in ledger`. That gate walks the whole prose
corpus on every run, and the corpus grows. CI's uncontended runner spends 35 s on the same step
(run 33523366953, step 7, 15:04:06 → 15:04:41), so this is not a sandbox artefact.

⚠ **`31.4 s` was never wrong; it is a 2026-08-23 reading of a smaller tier.** Between then and now
the tier gained the receipt gate, the residue gate and the cycle-contract gate, and gate 6 gained its
publication-type axis.

### 2 · Gate 13's growth is SCOPE plus POPULATION, not a per-test regression

This is the fork AUT-PD-172 left open in as many words — *"whether the growth is the suite genuinely
being 811 tests now, or a per-test cost regression … Time the suite per-test on one machine before
concluding either."* Three observations settle it, and none of them is arithmetic across machines.

**(a) The gate's SCOPE doubled after the 39.3 s reading was taken.** `git ls-tree` over `origin/main`,
one commit per day:

| date | `scripts/tests` | `research/autonomy/tests` |
|---|---|---|
| 2026-08-24 (the day 39.3 s / 55 tests was measured) | 5 files | **0 — the directory did not exist** |
| 2026-08-26 | 6 | 0 |
| 2026-08-27 | 8 | 9 |
| 2026-08-28 | 10 | 35 |
| 2026-08-29 | 10 | 47 |
| 2026-09-01 | 14 | 47 |

So the 39.3 s figure describes `scripts/tests` **alone**, five files. `research/autonomy/tests` was
wired into this gate on 2026-08-27 (`8eef10faf`, "run the suites that guard the loop") and went from
nothing to 47 files in two days. **Nothing regressed; a second directory was added and then grew.**

**(b) `affected_tests.py` is not implicated and has not changed since 2026-08-23.**
`git log -- scripts/affected_tests.py` → newest commit `49e42881c`, 2026-08-23. Its own test file
`scripts/tests/test_affected_tests.py` is byte-identical to its 2026-08-24 blob. The selector is not
where the time went.

**(c) CI's own `--durations=25`, on an uncontended runner, contains no test from either of this
gate's directories.** `tests.yml` already passes `--durations=25`; the last green run on `main`
(33523366953, sha 850edb335, job 99907910433) reports `11012 passed, 55 skipped … in 1234.92s` and
its 25 slowest tests are all in `research/modalities/tests`, `research/manuscripts/tests` and
`systems/tests`. The 25th is **24.09 s**, so **no test in `scripts/tests` or `research/autonomy/tests`
costs more than 24 s** on that machine.

⛔ **That refutes AUT-PD-183's leading hypothesis, and the row said to check it rather than believe
it.** The row proposed that *"a single slow test file serializes the whole gate"* under
`--dist loadfile`, with the file UNKNOWN. On the uncontended runner there is no such file. The
observed one-worker-busy/three-idle shape is the **tail** of a `loadfile` schedule running out of
files, not one pathological file.

**(d) What the gate actually spends its CPU on: `git` subprocesses.** Sampled from `/proc` at
18:46:00Z, ~4.5 min into the gate-13 stage of the live run, reading `utime+stime` (self) against
`cutime+cstime` (reaped children) for each of the four xdist workers:

```
pid=6137 state=S self_cpu=28.3s child_cpu=68.5s
pid=6142 state=S self_cpu=33.6s child_cpu=79.1s
pid=6145 state=S self_cpu=71.6s child_cpu=17.3s
pid=6152 state=S self_cpu=30.8s child_cpu=76.6s
```

and `ps` at the same instant showed two live `git` processes parented to workers 6152 and 6142.
**Three of the four workers had more than twice as much CPU in reaped children as in themselves;
~60 % of the gate's CPU is spent in child processes, and the children observed are `git`.** That is
consistent with the code: `research/autonomy/*.py` shells out to `git` from eleven modules
(`session_reaper.py` alone does so five times, twice inside a loop over every committed receipt — 89
of them today), and `research/autonomy/tests/test_a_lost_push_is_a_lost_lease.py` builds real bare
repositories, clones and pushes.

⭐ **So the mechanism is: ~800 individually-cheap tests, a large fraction of whose cost is `fork`ing
`git`.** In this sandbox a subprocess costs much more than it does on a CI runner, which is why the
same suite that shows up nowhere in CI's 25 slowest tests dominates the local gate.

### 3 · The controlled experiment: the same five files, timed today

The five `scripts/tests` files that WERE gate 13 on 2026-08-24 all still exist and every one is
**byte-identical** to its blob at `970c5e52c` (sha256 compared file by file). Running exactly those
five, same command shape (`pytest -n 4 --dist loadfile … -q`), on this machine tonight:

```
79 passed in 74.35s (0:01:14)          WALL_B1=74 s     load average 4.95 → 6.96
```

against the recorded **55 tests in 39.3 s** on 2026-08-24.

| | 2026-08-24 | 2026-09-01 |
|---|---|---|
| files | 5 (byte-identical) | the same 5 |
| tests collected | 55 | **79** |
| wall | 39.3 s | **74.4 s** |
| per test | 0.715 s | **0.94 s** |

⭐ **Per-test cost moved by 1.3×, on a box carrying eleven other seats; the test COUNT inside
unchanged files moved by 1.44×** (several of these tests are parametrised over the tree, which has
grown). **There is no per-test regression to find.** That is the fork AUT-PD-172 said to settle on
one machine before concluding either way, and it is settled: **the gate grew because its scope and
its population grew.**

### 4 · Where the gate's time actually goes — counted, not inferred: **130 repeated walks of the ledger's git history**

The whole gate was re-run with a counting shim first on `PATH` (one appended line per call, then
`exec /usr/bin/git "$@"`), so this is an exact census rather than a sample.

```
total git invocations in one gate-13 run          50 270
  against the real repository                     48 546
  `git show <sha>:research/autonomy/research-ledger.json`
                                                  48 230   ← 96 % of every git call the gate makes
  distinct commits whose ledger blob was read         371
  ⇒ complete walks of the ledger's history            130
`git log --follow -- research-ledger.json`, real repo  130   (61 more against test temp repos)
everything else, together                          ~1 700   (init/commit/add/config in temp repos)
```

The caller is **`research/autonomy/stuck_clock.py::ledger_versions()`**, whose docstring says what it
does in one line — *"`git log --follow` + `git show <sha>:<path>`, each version parsed"*. Reached
directly, and through `learning_rate.py` and `out_of_ideas.py`, by ~130 test calls that leave `repo`
at its default (the real repository) rather than pointing it at a fixture.

**Timed directly, on this box, after the sprint load fell away:**

```
ledger_versions(): 372 versions in 7.5 s
```

⭐⭐ **130 × 7.5 s = ~975 CPU-seconds of one gate run, spread over four xdist workers ≈ 244 s of
wall — about 55 % of the 446 s quiet gate, and roughly 46 % of the whole default commit loop.**
The ledger is **1.25 MB**, so that one command extracts and JSON-parses about **60 GB** of blob text
per gate run.

⛔⛔ **AND THIS IS WHY THE GATE GOT SLOWER WITH NOTHING "CHANGING": THE COST SCALES WITH COMMIT
COUNT, NOT WITH TEST COUNT.** Every commit this loop makes to the ledger adds one more `git show` to
every one of the 130 walks, of a file that is itself growing. It went from 371 versions during the
census run to **372 by the time the walk was timed, twenty minutes later.** No test was added and the
gate got more expensive. That is the mechanism AUT-PD-164 was reaching for when it said the cost
"came back … by accretion rather than by a decision anybody took", and it is the one part of gate 13
that will keep growing whatever is decided about tiering.

### 5 · Two hypotheses tested and refuted

**(i) "A per-test fixture builds the selector's import graph 55 times."** Refuted by reading:
`build_graph()` is called in exactly two of the nineteen tests in
`scripts/tests/test_affected_tests.py` (`test_selection_follows_imports_transitively`,
`test_the_graph_covers_the_real_tree`), not in a fixture, and `scripts/affected_tests.py` has not
changed since 2026-08-23.

**(ii) "The tracked-tree audit hook is the tax."** `research/autonomy/tests/conftest.py` installs a
process-wide `sys.addaudithook` that inspects every `open`. Measured directly rather than assumed:

```
tracked set size: 6931    install cost: 0.16 s
20 000 × open+read:  no hook 0.156 s | with the audit hook 0.176 s | ratio 1.13×
```

**1.13× on the most hook-sensitive workload there is, and a 0.16 s one-off per worker.** It is not
the cost. (For scale, on the same box `git rev-parse HEAD` costs ~4 ms warm.)

### 4 · A $0 observation that refutes a second §6 sentence

CLAUDE.md §6 says of the selector-validation record: *"**Both hashes are stale** — `preflight.sh`
changed 2026-08-23, `affected_tests.py` arrived by merge 2026-08-24."* Checked directly:

```
a77c6097…d69de  scripts/affected_tests.py     ← recorded: a77c6097…d69de   MATCH
6af7147f…22b0d  scripts/preflight.sh          ← recorded: 274fcb1f…c59e4   STALE
```

`affected_tests.py` **matches** — the record was re-stamped on 2026-08-26 (`84f5a0a2c`, "Re-stamp the
selector record my preflight change invalidated"). Only `preflight.sh` is stale, and it is stale
because the file has taken **eighteen** commits since that re-stamp. ⚠ **The conclusion §6 draws is
unchanged** — one stale hash still forces FULL — but the sentence states a fact that is half false,
and a session reading it concludes the record is unmaintainable when it was in fact maintained five
days ago.

⛔ **I did not re-stamp it.** `record_selector_validation.py` may only be run after a green
`PREFLIGHT_FULL=1`, and a green FULL cannot be obtained on a tree eleven seats are mutating. It is
also guaranteed to go stale again the moment any seat touches `preflight.sh` tonight — including me.

## What I changed

**`CLAUDE.md` §6 — the preflight bullet only.** The present-tense claim "it costs about **75
seconds**" is replaced by the re-measurement, split by tier so the two halves stop being conflated:
fast gates 81.3 s, gate 13 446.3 s quiet / 1 247.8 s contended, gate 13 therefore **85–94 % of the
loop** rather than "half" of it. The old figures are kept on a `⚠ Superseded, retained (rule 1.2)`
line, with the reason they went stale (scope + population, not regression). The clause that matters
most is untouched in substance and updated in number: **moving gate 13 behind `PREFLIGHT_TESTS=1`
remains trimcrae's call**, now worth ~81 s rather than ~31 s. The gate's description is corrected
from "the test selector's own contract" to "the pure-logic suites nothing else runs (the test
selector's own contract **and** the loop's instruments)", because it has covered two directories
since 2026-08-27. **Nothing else in §6 or in the file was touched.**

**`research/manuscripts/pinned-figures.json`** — two `superseded` entries, `commit_loop_about_75_seconds`
and `commit_loop_gate13_39s_55_tests`, inserted **surgically into the existing formatting** (12-line
diff; a naive re-serialisation churned 1 890 lines and was discarded). Both were checked against
every one of the 26 lint targets before registering, so neither can fire on a file this seat does
not own: the `31.4 s` fast-gate figure was deliberately **not** registered, because
`.claude/skills/repo-gates/SKILL.md:119` states it and that file belongs to nobody tonight.

* `python3 research/manuscripts/lint_consistency.py` → **`0 ERROR across 26 target file(s)`**.
* **Mutation-tested, in a `tempfile.mkdtemp()` scratch copy and never in the live tree** (charter §7):
  the unmutated `CLAUDE.md` copy yields `[]`; appending one line that restates
  *"costs about **75 seconds** … gate 13 **39.3 s** = **77.5 s** over its 55 tests"* without a
  marker yields **both** `S-commit_loop_about_75_seconds` and `S-commit_loop_gate13_39s_55_tests` as
  ERRORs.

**`scripts/preflight.sh`** — two comment blocks re-measured, no executable line touched
(`bash -n` clean):

1. the `PREFLIGHT_TESTS` tiering block, whose table said `ten fast gates 31.4 s / + gate 13 39.3 s /
   DEFAULT tier 77.5 s` and whose prose said gate 13 "IS NOW HALF THE DEFAULT LOOP … 39.3 s of the
   77.5 s … each of its 55 tests". Replaced with the 2026-09-01 split, the scope/population
   attribution, the byte-identical-five-files control, and the refutation of the slow-file
   hypothesis. The old text is retained verbatim under `⚠ Superseded, retained`.
2. the `PYTHONPYCACHEPREFIX` cost note, which measured "+0.6 s, about 2%" on a **213-test** version
   of this gate and quoted `32.5 s` as its base. **The ratio is the finding and it stands; the
   absolute no longer describes the gate**, and the note now says so and points at the block that
   carries the live number.

⛔ **ANTI-GAMING, PER CHANGE (charter item 5).** **No change makes any gate check less.** Every edit
above is a comment, a documentation figure, or a `superseded` registry entry; **not one line of test
selection, gate ordering, gate scope or exit-code handling was touched**, and `PYTEST_PAR`,
`RUN_TESTS`, `RUN_MODALITIES` and the gate list are byte-identical. Net effect on what the commit
loop verifies: **zero**. Net effect on the registry: **+2 entries, 0 removed, 0 loosened** — the
direction that adds refusals. I made the gate's cost *honest*, not smaller; the one change that
would make it smaller (re-tiering gate 13) is explicitly reserved for trimcrae and I did not take it.

## What I could not do, and what it is actually waiting on

1. **An uncontended local reading.** Tonight's box carries eleven other seats; load ran 1.2 → 12.1 on
   4 cores. Every local wall-clock number is an upper bound and is labelled as one. The quiet figure
   in the pin (446.3 s) is CYC-0078's 2026-08-29 reading on clean `origin/main`, not mine. ⚠ Waiting
   on: **the sprint window closing**, nothing else. One `./scripts/preflight.sh` after 09:00Z
   re-derives it.
2. **Re-stamping `scripts/selector-validation.json`.** It is an owned path and I did not touch it.
   `record_selector_validation.py` may only be run after a green `PREFLIGHT_FULL=1`, which cannot be
   obtained on a tree twelve seats are mutating — and I have since edited `preflight.sh`, which
   invalidates it again anyway. ⚠ Waiting on: a settled tree plus one FULL run, i.e. the next
   publication act, which is exactly the "tripwire clearable only by a rare act" §6 already names.
3. **The fix for the cost itself.** It exists, it is named below with its evidence, and **every file
   that would carry it is outside this seat's ownership** (`research/autonomy/stuck_clock.py`,
   `research/autonomy/tests/*`). Requirement written up rather than taken, per charter §2.
4. **`.claude/skills/repo-gates/SKILL.md` carries two stale present-tense cost claims** —
   `"**`./scripts/preflight.sh`** — every fast gate, and **no test**. ~**30 s**. **This is the commit
   loop.**"` and `"Measured: **fast gates 31.4 s, manuscripts 176.1 s on every commit**"`. That file
   is a `pinned-figures.json` target and nobody owns it tonight, so the `31.4 s` supersession was
   deliberately left unregistered to avoid reddening a file no seat can fix. ⚠ Waiting on: the driver
   assigning it. **It is one edit, and until it lands the skill still tells its reader ~30 s.**
5. **CLAUDE.md §6's "Both hashes are stale" is half false** (§4 of this document). Not corrected here
   — it is not a cost figure and my mandate on that file is narrow. ⚠ Waiting on: the driver saying
   the word.
6. **The per-test `--durations=25` breakdown was lost, and it is not needed.** The instrumented run
   carried `--durations=25`, but `tracked_tree_guard` raised in `pytest_sessionfinish` and its
   traceback — 40 lines naming every file eleven seats had touched — pushed the durations block out
   of the captured tail. ⚠ **I did not re-run for it**, because the `git` census localises the cost
   far more precisely than a per-test table would: 96 % of the gate's git calls are one command, and
   that command was then timed directly. AUT-PD-183's `next_action` asked for `--durations=15` to
   *"name the file"*; the census names the **function**, which is better.
7. **The ordinal "gate 13" is now wrong** — `repo-gates` enumerates the pure-logic suites as **gate
   15** of seventeen, with 13 being the modalities tests. Every ledger row and CLAUDE.md §6 say "gate
   13", so renaming it would break more than it fixes and is not this seat's call. Flagged only.

## Amendment record for the driver

⛔ Not appended by this seat — `amendments.jsonl` is driver-only while a wave is in flight.

```json
{
  "utc": "<driver fills>",
  "cycle_id": "<driver fills>",
  "actor": "sprint-2026-09-01/S6-COMMITLOOP",
  "kind": "amend",
  "paths": [
    "CLAUDE.md",
    "scripts/preflight.sh",
    "research/manuscripts/pinned-figures.json"
  ],
  "items": ["AUT-PD-164", "AUT-PD-172", "AUT-PD-183"],
  "what_changed": "CLAUDE.md §6's commit-loop cost figures, and the same figures where scripts/preflight.sh states them in comments. Replaced 'it costs about 75 seconds' and 'fast gates 31.4 s + gate 13 39.3 s = 77.5 s ... each of its 55 tests' with a re-measurement split by tier: fast gates 81.3 s (dev-setup/interpreter probe 15.3 s, citation provenance 44.4 s, everything else 21.6 s), gate 13 446.3 s quiet / 1247.8 s under twelve-way contention, so gate 13 is 85-94 % of the loop rather than half. Corrected the gate's description from 'the test selector's own contract' to the two directories it has actually covered since 2026-08-27. Registered both retired figures in pinned-figures.json in the same change.",
  "old_value": "CLAUDE.md: 'it is the commit loop, it costs about **75 seconds**'; 'Measured 2026-08-24: fast gates **31.4 s** + gate 13 **39.3 s** = **77.5 s** ... each of its 55 tests builds the selector's import graph and shells out to git ... would take the commit loop back to ~31 s'. preflight.sh: the same table, plus 'GATE 13 IS NOW HALF THE DEFAULT LOOP' and a PYTHONPYCACHEPREFIX note quoting 32.5 s over 213 tests.",
  "new_value": "The 2026-09-01 measurement, with every retired figure retained verbatim on a '⚠ Superseded, retained (rule 1.2)' line, plus the attribution: the growth is SCOPE and POPULATION, not a per-test regression. Two superseded entries added to pinned-figures.json (76 -> 78), both mutation-tested in a scratch copy.",
  "why": "AUT-PD-164, AUT-PD-172, AUT-PD-183. CLAUDE.md loads every session, and the figure it carried is what every cycle used to decide whether it could afford the gate.",
  "self_serving_check": "ANSWERED: NO, and the tempting self-serving edit was available and declined. The cheap way to make a 22-minute gate go away is to re-tier it or scope it; CLAUDE.md reserves that for trimcrae and this change does not take it. Not one line of gate selection, gate scope, gate ordering or exit-code handling was touched — only comments, documentation figures and two ADDED registry refusals (76 -> 78 superseded entries, none removed, none loosened). The change makes the loop's cost harder to misstate and does not make the loop cheaper: every number moved in the direction that makes this repository's gate look MORE expensive, which is the opposite of a self-serving edit.",
  "mutation_tested": true,
  "_mutation_evidence": "lint_consistency.check_superseded over a tempfile scratch copy of CLAUDE.md: unmutated -> []; one appended line restating 'about **75 seconds** ... gate 13 **39.3 s** = **77.5 s** ... its 55 tests' without a marker -> S-commit_loop_about_75_seconds and S-commit_loop_gate13_39s_55_tests, both ERROR. Never mutated in the live tree.",
  "_filed_by_seat": "S6-COMMITLOOP"
}
```

## Ledger rows the driver should write

**1 · Close AUT-PD-164, AUT-PD-172 and AUT-PD-183 as MEASURED-AND-PINNED.** All three are the same
defect from three angles and all three asked for a measurement and a pin. Both are done, the fork
AUT-PD-172 left open is closed on one machine, and AUT-PD-183's leading hypothesis is refuted with
CI's own `--durations` output. ⚠ **None of them asked for an optimisation and none is taken.**

**2 · NEW — `research/autonomy/tests` re-reads the whole ledger history through `git show`, once per
commit, 130 times per gate run.** `kind: process_defect`, `state: queued`,
`cost_class: free`, `requires_trimcrae: false`, serves `RT-AUTONOMY`.
*what:* ⛔ THE COMMIT LOOP'S BIGGEST SINGLE COST IS A HISTORY WALK NOBODY MEANT TO PAY FOR 130 TIMES.
`stuck_clock.ledger_versions()` runs `git log --follow` over `research-ledger.json` and then one
`git show <sha>:research/autonomy/research-ledger.json` per commit, parsing each blob as JSON. There
are **371 committed versions** of a **1.2 MB** file today. Counted exactly, with a `PATH` shim in
front of `git`: the gate makes **50 270 git invocations, of which 48 230 — 96 % — are that one
`git show`**, over **371 distinct commits**: **130 complete walks of the whole history in a single
gate run**. One walk is **7.5 s** (`ledger_versions(): 372 versions in 7.5 s`, timed directly once
the sprint load fell away), so this is **~975 CPU-seconds per gate run — about 55 % of the 446 s
quiet gate** and roughly **60 GB** of blob text extracted and JSON-parsed.
⭐ **THE COST GROWS WITH COMMIT COUNT, NOT WITH TEST COUNT**, which is why this gate got slower with nothing "changing": every ledger commit
this loop makes adds one more blob to every walk, of an ever-larger file. ★ The fix is the ordinary
one and it does not weaken anything: stream the blobs in ONE process (`git cat-file --batch`) instead
of forking per commit, and/or memoise `ledger_versions(repo, path)` on `(repo, HEAD)` so 130 identical
walks in one pytest session cost four (one per xdist worker). **Both keep the assertions identical.**
*Paths:* `research/autonomy/stuck_clock.py` (`_git`, `ledger_versions`), callers in
`research/autonomy/learning_rate.py` and `research/autonomy/out_of_ideas.py`.

**3 · NEW — the selector's staleness guard is inert, and that is why §6's "permanent tripwire" was
never cleared.** `kind: process_defect`, `state: queued`, `cost_class: free`,
`requires_trimcrae: false`, serves `RT-AUTONOMY`.
*what:* ⛔⛔ `scripts/tests/test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers`
CANNOT FAIL. The file's `@pytest.fixture(autouse=True) _validated` rewrites `A.VALIDATION_RECORD` to
a temp record built from the **on-disk hashes**, so every test — including the one whose whole job is
to notice a stale record — is handed a record that matches by construction. The fixture's own
docstring says *"The two tests that are about the record patch it themselves"*; that is true of the
two that patch it, and **false of this third one, which does not**. ⭐ MEASURED, NOT REASONED:
`affected_tests._unvalidated_gatekeepers()` against the real record returns
`{'scripts/preflight.sh'}`, and calling the test function directly (module imported, no fixture)
raises its AssertionError — while `pytest scripts/tests/test_affected_tests.py` reports
**17 passed**. ⛔ THE COST IS ALREADY BOOKED: `scripts/preflight.sh` has been unvalidated since
2026-08-26 across **eighteen commits**, CLAUDE.md §6 describes that state as a *"permanent
tripwire"*, and the guard written to shout about it has been silent the whole time. This is the
one-of-a-pair shape `paper-hardening` §8b.2 names, in the selector's own contract — for the second
time (round 14 seat 4 found the first). ★ Fix: exempt that test from the autouse fixture (a marker,
or move it to its own module), then mutation-test the exemption by pointing the record at a wrong
hash and watching it go red.
*Path:* `scripts/tests/test_affected_tests.py`.

**4 · NEW — CLAUDE.md §6 says "Both hashes are stale"; one of them is not.**
`kind: process_defect`, `state: queued`, `cost_class: free`, `requires_trimcrae: false`.
*what:* `scripts/affected_tests.py` MATCHES its recorded hash (`a77c6097…`) — the record was
re-stamped on 2026-08-26 in `84f5a0a2c`. Only `scripts/preflight.sh` is stale. The conclusion §6
draws is unaffected (one stale hash still forces FULL), but the sentence tells a reader the record is
unmaintainable when it was maintained five days ago. One-line edit, in a governed file, outside
S6-COMMITLOOP's mandate. Fold into row 3 if the driver prefers.

**5 · NEW — `.claude/skills/repo-gates/SKILL.md` states the commit loop as "~30 s".**
`kind: process_defect`, `state: queued`, `cost_class: free`. Same defect as AUT-PD-172, different
file, and the file is a `pinned-figures.json` target — so once it is corrected, the `31.4 s` /
`176.1 s` fast-gate figures can be registered as superseded too, which this seat deliberately did not
do because it would have reddened a file no seat could fix tonight.
