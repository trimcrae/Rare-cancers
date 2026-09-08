> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

- **Worker:** W03c, lane 3 (second refill). **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the coordinator must extract the served model from the transcript.
- `date -u` **start:** `Tue Sep  8 02:27:34 UTC 2026`. `date -u` **end:** `Tue Sep  8 02:30:08 UTC 2026`.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (key lines; full output was 40 lines, none naming a model):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

- **HEAD actually read:** at start `b9a0257e6acff53ad22535cf2adf261313e0b250`; at end `47aac85f874a57a6f981c3432abcf16980968aec`. **This is NOT the campaign freeze `92abbcb…` named in COMMON-BRIEF.md** — the coordinator committed during my run. I verified my inputs were unaffected: `git diff --name-only b9a0257 47aac85 | grep -v '^research/autonomy/opus-capacity-campaign-20260908/'` returned **empty**, i.e. the only changes were inside the campaign directory. My scratch copy was taken at `b9a0257`.
- **I wrote nothing into the Git working tree and ran no git write operation.** All execution was under `/tmp/claude-0/w03c/`. Final `git status --porcelain` filtered for anything outside the campaign directory returned empty.
- **Standing correction honoured.** Nothing in this report rests on, asserts, or implies a catalogue-acceptor contract violation. The premise is withdrawn and I did not reintroduce it under any label; the successor I executed is about *test-guard sensitivity*, which is independent of it.

## Question

W03b's "Next concrete action" named exactly one bounded successor, and I executed it:

> **Copy `aso-per-junction-table.json` to scratch, perturb it, and observe which of the seven panel guard tests actually fail — converting W03b's SECONDARY reading ("no test asserts acceptor universality", reached by reading the guards) into a RUN mutation result.**

Open because W03b explicitly recorded this as a limitation it could not discharge: *"I did not execute the repository's test suite, so 'no test asserts acceptor universality' rests on reading the guards, not on mutating the table and observing failures. A mutation test would be stronger and I did not have write authority to run one."* The write-isolation constraint that blocked W03b is satisfiable by copying the tree out of the repository, which is read-only on the tree.

**Successor taken:** the mutation test of the panel guards.

**Successors declined, with reasons:**

| Declined route | Named by | Reason declined |
|---|---|---|
| Retrieve Panagopoulos 2002 Table 1 and Urbini 2018 Table 1 through an egress hatch | W03 "Next concrete action" | Fails filter 3 (needs network beyond PubMed MCP metadata) and filter 2 — `onlinelibrary.wiley.com/doi/10.1002/gcc.10127` and `mdpi.com/1422-0067/19/7/1855` are recorded `EGRESS_BLOCKED` in W03, and `CLOSED-WORK.md` forbids unchanged denied-route replay. W03's coordinator note also declines a GitHub Actions egress dispatch as out of campaign scope. |
| COSMIC / cBioPortal / Mitelman queries | W03 "Method / inputs" (UNKNOWN, not searched) | Fails filter 3 (network). Remains **UNKNOWN**, not empty. |
| Re-opening the acceptor-coverage question itself | implied by lane name | W03b closed it as `ALREADY-KNOWN` on committed evidence; re-reviewing a correct artifact is forbidden by `CLAUDE.md` §5. Also would rest on the withdrawn premise. |
| The 38-of-77 mRNA-in-frame exon-2 bookkeeping | W03b R3-K "optional routing" | Not a successor task — it is already computed and reported by W03b; recomputing is restatement, not an artifact. |

**The fallback (three-way dependency classification) was NOT triggered** — the named successor passed all three filters and executed to a definite verdict.

## Prior-work check

```
cat /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md   # read in full
cat .../reports/W03-genomic-structural-variant.md .../reports/W03b-acceptor-blast-radius.md   # read in full
git ls-files | grep -E 'test_aso_per_junction_table|test_aso_coverage_ladder|test_the_numbered_claims_no_instrument_read|test_round6_fixes_landed|test_the_manuscript_asserts_the_relation_its_artifacts_compute|test_aso_submission_numbers|test_submission_tables_round7_generator_defects'
```

The `git ls-files` filter resolved W03b's seven named guards to real tracked paths (4 under `research/manuscripts/tests/`, 3 under `research/modalities/tests/`) — so the successor's premise (that these seven files are the guard set) is itself confirmed rather than assumed.

**Confirmed not replayed, from `CLOSED-WORK.md`:** no Brenca route (PRJNA692081 / SRP301712 would be DUPLICATE; not approached); no PUB-EMC-CLASSIFICATION or EMC calibration work; no lane-11 source-index work (W11b sole owner); no Hofvander/EGA, sunitinib-2014, Wagner, CTARC, pazopanib, trabectedin or anthracycline route; **no network call of any kind**, so no denied route was replayed unchanged; `GSE4303`/`GSE28866` untouched. From the W03/W03b transfer: I did not re-derive the empty 0/23 breakpoint × natural-history join, did not touch `PUB-FUSION-PARTNER`, and did not edit the junction table in the repository.

## Method / inputs

- **Isolation.** `tar --exclude=./.git -cf - .` piped into `/tmp/claude-0/w03c/repo/` — a full working-tree copy at `b9a0257`, 608 MB, verified `.git` absent (`ls -a`, no `.git` entry). Every mutation and every pytest invocation ran with `cwd=/tmp/claude-0/w03c/repo`. The guards resolve their artifacts via `os.path.dirname(os.path.abspath(__file__))`, so in the copy they read the copy's JSON — which is why this technique works at all under write isolation.
- **Mutated artifact (copy only):** `research/modalities/aso-per-junction-table.json` (38 junctions; tiers 25 / 8 / 5).
- **Guards exercised (all 7, every run):** `research/modalities/tests/test_aso_per_junction_table.py`, `test_aso_submission_numbers.py`, `test_submission_tables_round7_generator_defects.py`; `research/manuscripts/tests/test_aso_coverage_ladder.py`, `test_round6_fixes_landed.py`, `test_the_numbered_claims_no_instrument_read.py`, `test_the_manuscript_asserts_the_relation_its_artifacts_compute.py`.
- **Harness:** `/tmp/claude-0/w03c/mutation_test.py` (stdlib only; returned inline below). Protocol per mutation: restore pristine → apply one mutation → run all 7 files → parse `^FAILED <nodeid>` → restore. Bracketed by a green baseline, a green restore, and a **control mutation that must be detected** (harness asserts its own blindness would abort the run).
- **Interpreter, and the documented trap.** `python3` = 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; `python3 -c "import pytest"` **fails** (`No module named pytest`), so per `scripts/preflight.sh:419-427` this container is on the **second branch**: the bare `pytest` console script, a **uv tool in its own isolated venv** (`/root/.local/bin/pytest`, pytest 9.1.1). `preflight.sh` documents that this branch once invented 36 phantom failures. **That risk is controlled here and does not invalidate the result**: this is a *differential* design — the baseline in the identical interpreter is `183 passed, exit 0`, so there are no phantom failures to subtract, and every reported failure is a delta caused by one mutation.
- **Not run:** `scripts/preflight.sh` (dispatch did not authorise it, and I changed nothing in the tree). No network, no GPU, no spend, no MCP call.

## Result

### R1 — Baseline and control (PRIMARY, RUN)

| Run | Result | Grade |
|---|---|---|
| Baseline, unmutated copy, 7 files | **183 passed, exit 0** | PRIMARY |
| Restore after all mutations | **183 passed, exit 0** | PRIMARY |
| Control mutation M5 detected? | **YES** (harness would have aborted otherwise) | PRIMARY |

The harness is not blind, and the copy is faithful.

### R2 — Mutation battery: which guards actually fire (PRIMARY, RUN)

n = 5 mutations, each a single edit to the scratch copy. "Killed" = at least one of the 7 guard files failed.

| ID | Mutation | Exit | Guards failed | Killed |
|---|---|---|---|---|
| M1 | `clinical_tier` demote, label **named** in guards: `TFG_e7__NR4A3_e3` `published_exon_resolved_breakpoint` → `no_published_exon_resolved_breakpoint` | 1 | **4** | YES |
| M2 | `clinical_tier` promote, label **not named** in guards: `EWSR1_e10__NR4A3_e3` `partner_published_this_exon_not_reported` → `published_exon_resolved_breakpoint` | 1 | **4** | YES |
| M3 | **acceptor 3→2**, label **not named** in guards: `EWSR1_e10__NR4A3_e3` → `EWSR1_e10__NR4A3_e2` | 1 | **1** | YES |
| M4 | **acceptor 3→2**, label **named** in guards: `EWSR1_e12__NR4A3_e3` → `EWSR1_e12__NR4A3_e2` | 1 | **8** | YES |
| M5 | CONTROL: drop one junction (list length 37, declared `n_junctions` left at 38) | 1 | **1** | YES |

**Mutation score 5/5.** No mutation survived.

Failing node IDs, verbatim from the run:

- **M1 and M2 (identical guard set, 4 each):** `test_round6_fixes_landed.py::test_the_panel_junction_count_matches_the_artifact`; `test_aso_per_junction_table.py::test_the_published_junctions_are_tiered_apart_from_the_rest`; `test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs`; `test_aso_submission_numbers.py::test_the_discussion_recommends_the_two_published_junctions`.
- **M3:** `test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs` **only**.
- **M4:** the eight listed in the Validation section, including `test_every_frame_compatible_junction_is_present`, `test_the_multi_partner_design_appears_under_all_three_of_its_junctions`, `test_both_published_junctions_have_a_usable_reagent`, `test_ties_on_locus_breadth_break_on_margin_not_on_raw_hits`, and `test_the_numbered_claims_no_instrument_read.py::test_the_locus_recount_that_reverses_the_load_comparison_is_the_tables_own`.
- **M5:** `test_the_table_reproduces_from_committed_inputs` **only**.

### R3 — Verdict on W03b's SECONDARY claim (PRIMARY, RUN — this is the deliverable)

W03b's reading was **CONFIRMED in its literal content and CORRECTED in its practical consequence.**

1. **Confirmed:** no guard contains an acceptor-universality assertion. M3 — the acceptor-side mutation on a junction whose label no guard names — was killed by **exactly one** test, and that test is not about acceptors. `test_the_table_reproduces_from_committed_inputs` is three lines (`research/modalities/tests/test_aso_per_junction_table.py:131-133`): `assert m.main(["--check"]) == 0, "aso-per-junction-table.json is stale; re-run the script"`. It is a whole-artifact regeneration check, and M5 (an edit with nothing to do with acceptors) was killed by the same single guard. So the guard set contains **zero** acceptor-specific assertions, exactly as W03b read them.

2. **Corrected:** the practical inference some readers would draw — that acceptor drift is therefore *unguarded* — is **false**. The regeneration check pins the entire artifact to its generator plus committed inputs, so no acceptor edit can survive, and the kill is total (5/5) rather than assertion-by-assertion. Acceptor uniformity is enforced **upstream, at generation**, not by any test: `research/modalities/aso_per_junction_table.py:237` reads `label = d.get("junction_label")` off the deep-screen artifacts, and `:397` writes `"n_junctions": len(junctions)` — a computed length, never a hand-typed constant.

3. **Consequent minor observation, reported as an observation and not a defect:** M5 shows that a declared/observed count mismatch (`n_junctions` 38 vs 37 rows) is caught **only** by the regeneration guard — `test_every_frame_compatible_junction_is_present` asserts `a["n_junctions"] == 38` against the *declared field*, not against `len(a["junctions"])`. This state is **unreachable in a regenerated table**, because `:397` computes the field from the list. **I am not proposing a change.** No guard is weakened, reordered, or given a new acceptance criterion by me.

**Nothing above is a violation, a contract breach, or a defect report.** It is a measured sensitivity property of an existing, currently green test set.

## Validation evidence

**RUN.** Environment: Linux; `python3` 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0], stdlib only; test runner = bare `pytest` console script `/root/.local/bin/pytest`, **pytest 9.1.1**, a uv tool in its own isolated venv (`python3 -c "import pytest"` → `No module named pytest`). Executed in `/tmp/claude-0/w03c/`, outside the repository.

Baseline, run directly before the harness:

```
$ cd /tmp/claude-0/w03c/repo && pytest -q <the 7 guard files>
........................................................................ [ 39%]
........................................................................ [ 78%]
.......................................                                  [100%]
183 passed in 2.44s
EXIT=0
```

Full mutation battery:

```
$ cd /tmp/claude-0/w03c && python3 mutation_test.py; echo "EXIT=$?"
BASELINE (unmutated copy): exit=0  183 passed in 2.23s  failures=[]

M1 tier demote, label NAMED in guards: TFG_e7__NR4A3_e3 published->no_published
  exit=1  4 failed, 179 passed in 2.31s
    FAILED research/manuscripts/tests/test_round6_fixes_landed.py::test_the_panel_junction_count_matches_the_artifact
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_published_junctions_are_tiered_apart_from_the_rest
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs
    FAILED research/modalities/tests/test_aso_submission_numbers.py::test_the_discussion_recommends_the_two_published_junctions

M2 tier promote, label NOT named in guards: EWSR1_e10__NR4A3_e3 partner_not_reported->published
  exit=1  4 failed, 179 passed in 2.19s
    FAILED research/manuscripts/tests/test_round6_fixes_landed.py::test_the_panel_junction_count_matches_the_artifact
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_published_junctions_are_tiered_apart_from_the_rest
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs
    FAILED research/modalities/tests/test_aso_submission_numbers.py::test_the_discussion_recommends_the_two_published_junctions

M3 acceptor exon 3->2, label NOT named in guards: EWSR1_e10__NR4A3_e3 -> EWSR1_e10__NR4A3_e2
  exit=1  1 failed, 182 passed in 2.25s
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs

M4 acceptor exon 3->2, label NAMED in guards: EWSR1_e12__NR4A3_e3 -> EWSR1_e12__NR4A3_e2
  exit=1  8 failed, 175 passed in 2.23s
    FAILED research/manuscripts/tests/test_the_numbered_claims_no_instrument_read.py::test_the_locus_recount_that_reverses_the_load_comparison_is_the_tables_own
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_both_published_junctions_have_a_usable_reagent
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_every_frame_compatible_junction_is_present
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_multi_partner_design_appears_under_all_three_of_its_junctions
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_published_junctions_are_tiered_apart_from_the_rest
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_ties_on_locus_breadth_break_on_margin_not_on_raw_hits
    FAILED research/modalities/tests/test_aso_submission_numbers.py::test_the_discussion_recommends_the_two_published_junctions

M5 CONTROL drop one junction (len 37 vs declared n_junctions 38): EWSR1_e10__NR4A3_e3
  exit=1  1 failed, 182 passed in 2.28s
    FAILED research/modalities/tests/test_aso_per_junction_table.py::test_the_table_reproduces_from_committed_inputs

RESTORED copy: exit=0  183 passed in 2.23s

SUMMARY: 5/5 mutations killed by the 7 guard files
SELF-CHECK PASSED (baseline green, restore green, control M5 must be killed): True
EXIT=0
```

Isolation evidence:

```
$ ls -a /tmp/claude-0/w03c/repo | head
.  ..  .claude  .gitattributes  .githooks  .github  .gitignore  .zenodo.json  AGENTS.md  CITATION.cff
$ du -sh /tmp/claude-0/w03c/repo/.git 2>/dev/null || echo "no .git (good)"
no .git (good)

$ cd /home/user/Rare-cancers && git rev-parse HEAD
47aac85f874a57a6f981c3432abcf16980968aec
$ git status --porcelain | grep -v '^?? research/autonomy/opus-capacity-campaign-20260908/'
   (no output)
$ git diff --name-only b9a0257e6acff53ad22535cf2adf261313e0b250 47aac85f874a57a6f981c3432abcf16980968aec | grep -v '^research/autonomy/opus-capacity-campaign-20260908/'
   (no output)
```

**PROPOSED (NOT RUN):** `scripts/preflight.sh` (not authorised, and no tree change to gate); any repair to `test_every_frame_compatible_junction_is_present`; any network retrieval; any COSMIC/cBioPortal/Mitelman query; any `python3 -m pytest` run (impossible in this container — system `python3` has no pytest).

**No repair is being routed.** R3.3 is an observation about an unreachable state, not a defect, so there is no exact-current-text / exact-proposed-text / file / line repair to route. I did not weaken, reorder, or author any acceptance criterion; my harness's own assertions bracket the experiment (baseline green, restore green, control must die) and are stricter than none.

## Limitations

- **Five mutations are five mutations.** A 5/5 mutation score over a hand-picked battery is *not* a mutation-coverage figure for the guard set. It bounds nothing about mutations I did not try. The untried space is **UNKNOWN**, not clean.
- **The kill is concentrated in one guard.** M3 and M5 were each killed by `test_the_table_reproduces_from_committed_inputs` alone. If that single check ever became unable to run — a missing importable input, a generator refactor — acceptor and row-count drift would become **silent** under the remaining six. I measured this; I did not test it by disabling the guard, and I will not.
- **Interpreter caveat, retained not resolved.** The run used the uv-tool `pytest`, the branch `preflight.sh` documents as having once invented 36 phantom failures. The differential design and the green baseline/restore control for it, but this is **not** the interpreter `preflight.sh` prefers, and these numbers are not a preflight result.
- **Scratch-copy fidelity.** The copy omits `.git`. Any guard that consults git history would behave differently; none of the 7 failed at baseline, so none did here, but that is an observation about this run.
- **HEAD moved mid-run** (`b9a0257` → `47aac85`). I verified the delta was confined to the campaign directory, so my inputs are identical at both — but neither HEAD is the `92abbcb` freeze named in COMMON-BRIEF.md.
- **Nothing here is scientific evidence.** This is test-harness bookkeeping about a data catalogue. It is not primary evidence, not prediction, not association, and emphatically not experimental validation. It bears on no molecule, no reagent, no patient, and no clinical question of any kind. There is no wet lab.
- The withdrawn catalogue-acceptor-violation premise is **not** used, reintroduced, or relied on anywhere above.

## Stop condition

Set by dispatch: *the named successor executed to a definite verdict with a real command and exit code.*

**MET.** The successor W03b named — a mutation test of the panel guards — was executed as five single-edit mutations against a scratch copy, bracketed by a green baseline (`183 passed`, exit 0), a green restore (`183 passed`, exit 0), and a control that the harness required to die. Verdict: **mutation score 5/5, and W03b's SECONDARY claim is CONFIRMED in content** (no guard asserts acceptor universality; the acceptor mutation on an unnamed label was killed by exactly one non-acceptor regeneration guard) **and CORRECTED in consequence** (acceptor drift is nonetheless fully guarded, upstream at generation and downstream by the regeneration check). Returned immediately on meeting it; the fallback was not needed and was not performed.

## Tool-call and wall-clock count actually used

**14 tool calls** (all Bash; zero MCP, zero network, zero git-write). Wall clock `02:27:34Z` → `02:30:08Z` = **2 min 34 s** of execution, plus report drafting. Well inside the ~40-call / ~40-minute self-observed target. No padding.

## Next concrete action

**One bounded successor, and it is the limitation this run created rather than removed:** R3.2 shows the panel's mutation-tightness rests almost entirely on a single three-line regeneration guard. The smallest honest next step is to **measure that guard's own reachability** — in a scratch copy, confirm that `aso_per_junction_table.main(["--check"])` genuinely regenerates from committed inputs rather than short-circuiting when an input is absent, by removing one deep-screen artifact from the copy and observing whether `--check` fails loudly or returns 0 on a degraded input set. It needs no network, no GPU, no spend, no write access to the tree, and no route recorded denied; it uses the same scratch-copy technique proven here. It is bookkeeping about a guard, not a scientific question, so if the coordinator has any lane with an open *evidentiary* question it should take priority over this.

**Honest alternative if that is judged too narrow:** there is **no viable scientific successor in lane 3 on this thread.** The lane's two live scientific routes are both closed — the breakpoint × natural-history join is empty at 0/23 for a denominator reason (W03), and the only two documents that could move it off zero are `EGRESS_BLOCKED` and may not be replayed unchanged; the acceptor-coverage question is `ALREADY-KNOWN` on committed evidence (W03b). Continuing past that would be re-reviewing correct artifacts.

**Routing:** nothing is owed to the PUB-ASO owner. No defect was found, no repair is proposed, and no guard was touched.

### Code returned inline

`/tmp/claude-0/w03c/mutation_test.py` — the harness, verbatim as run:

```python
#!/usr/bin/env python3
"""W03c mutation test of the PUB-ASO panel guards.

Converts W03b's SECONDARY reading ("no test asserts acceptor universality") into a RUN
result, by perturbing a scratch COPY of aso-per-junction-table.json and observing which
of the seven guard files actually fail.

Read-only on the Git working tree: everything happens under /tmp/claude-0/w03c/repo.
"""
import json, shutil, subprocess, sys, os, re

REPO = "/tmp/claude-0/w03c/repo"
ART = os.path.join(REPO, "research/modalities/aso-per-junction-table.json")
PRISTINE = "/tmp/claude-0/w03c/aso-per-junction-table.pristine.json"

TESTS = [
    "research/modalities/tests/test_aso_per_junction_table.py",
    "research/modalities/tests/test_aso_submission_numbers.py",
    "research/modalities/tests/test_submission_tables_round7_generator_defects.py",
    "research/manuscripts/tests/test_aso_coverage_ladder.py",
    "research/manuscripts/tests/test_round6_fixes_landed.py",
    "research/manuscripts/tests/test_the_numbered_claims_no_instrument_read.py",
    "research/manuscripts/tests/test_the_manuscript_asserts_the_relation_its_artifacts_compute.py",
]

def set_tier(label, tier):
    def f(a):
        j = next(x for x in a["junctions"] if x["junction_label"] == label)
        assert j["clinical_tier"] != tier, "mutation is a no-op"
        j["clinical_tier"] = tier
    return f

def set_acceptor(label, new_label):
    def f(a):
        j = next(x for x in a["junctions"] if x["junction_label"] == label)
        j["junction_label"] = new_label
    return f

def drop(label):
    def f(a):
        n = len(a["junctions"])
        a["junctions"] = [x for x in a["junctions"] if x["junction_label"] != label]
        assert len(a["junctions"]) == n - 1
    return f

MUTS = [
 ("M1 tier demote, label NAMED in guards: TFG_e7__NR4A3_e3 published->no_published",
  set_tier("TFG_e7__NR4A3_e3", "no_published_exon_resolved_breakpoint")),
 ("M2 tier promote, label NOT named in guards: EWSR1_e10__NR4A3_e3 partner_not_reported->published",
  set_tier("EWSR1_e10__NR4A3_e3", "published_exon_resolved_breakpoint")),
 ("M3 acceptor exon 3->2, label NOT named in guards: EWSR1_e10__NR4A3_e3 -> EWSR1_e10__NR4A3_e2",
  set_acceptor("EWSR1_e10__NR4A3_e3", "EWSR1_e10__NR4A3_e2")),
 ("M4 acceptor exon 3->2, label NAMED in guards: EWSR1_e12__NR4A3_e3 -> EWSR1_e12__NR4A3_e2",
  set_acceptor("EWSR1_e12__NR4A3_e3", "EWSR1_e12__NR4A3_e2")),
 ("M5 CONTROL drop one junction (len 37 vs declared n_junctions 38): EWSR1_e10__NR4A3_e3",
  drop("EWSR1_e10__NR4A3_e3")),
]

def run():
    p = subprocess.run(["pytest", "-q", "--no-header", "-p", "no:cacheprovider"] + TESTS,
                       cwd=REPO, capture_output=True, text=True)
    fails = sorted(set(re.findall(r"^FAILED (\S+)", p.stdout, re.M)))
    tail = [l for l in p.stdout.strip().splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
    return p.returncode, fails, (tail[-1] if tail else p.stdout.strip().splitlines()[-1:])

def main():
    shutil.copyfile(ART, PRISTINE)
    rc, fails, summary = run()
    print(f"BASELINE (unmutated copy): exit={rc}  {summary}  failures={fails}")
    assert rc == 0 and not fails, "baseline is not green; mutation test is not interpretable"
    results = []
    for name, mut in MUTS:
        shutil.copyfile(PRISTINE, ART)
        a = json.load(open(ART, encoding="utf-8"))
        mut(a)
        json.dump(a, open(ART, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        rc, fails, summary = run()
        results.append((name, rc, fails, summary))
        print(f"\n{name}\n  exit={rc}  {summary}")
        if fails:
            for f in fails:
                print(f"    FAILED {f}")
        else:
            print("    NO GUARD FAILED  <-- mutation survives")
    shutil.copyfile(PRISTINE, ART)
    rc, fails, summary = run()
    print(f"\nRESTORED copy: exit={rc}  {summary}")
    assert rc == 0 and not fails, "restore failed"
    killed = sum(1 for _, rc, f, _ in results if rc != 0)
    print(f"\nSUMMARY: {killed}/{len(results)} mutations killed by the 7 guard files")
    print("SELF-CHECK PASSED (baseline green, restore green, control M5 must be killed):",
          results[-1][1] != 0)
    assert results[-1][1] != 0, "control mutation M5 was NOT detected; the harness is blind"

main()
```

The scratch copy was created with `mkdir -p /tmp/claude-0/w03c/repo && cd /home/user/Rare-cancers && tar --exclude=./.git -cf - . | (cd /tmp/claude-0/w03c/repo && tar -xf -)` (`rsync` is not installed in this container).
