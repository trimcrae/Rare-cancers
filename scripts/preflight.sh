#!/usr/bin/env bash
# Pre-commit preflight: run every cheap check, and FAIL LOUDLY if any of them fails.
#
# WHY THIS EXISTS. On 2026-07-25 an agent session pushed a real lint error to `main`, then ~an hour later
# pushed a merge without noticing 14 failing tests. Both times the command looked like this:
#
#     python3 research/manuscripts/lint_consistency.py | tail -3 && git commit ...
#
# A pipeline's exit status is the status of its LAST command. `tail` succeeds, so `&&` proceeds and `set -e`
# never fires -- the check ran, printed its error, and was structurally incapable of stopping anything. That is
# the same defect class this repo keeps paying for: a check that reports while measuring nothing actionable
# (seven false-success diagnostics on the valB lane; a watchdog unparseable for days so its cron never fired;
# `_diagnostics_ok()` returning True when the report was absent).
#
# The fix is not "remember not to pipe". It is one entry point whose exit code cannot be masked:
#   * `set -euo pipefail` so a failure anywhere in a pipeline propagates;
#   * every check's status captured explicitly and re-reported at the end;
#   * a non-zero exit if ANY check failed, so `./scripts/preflight.sh && git commit` is actually safe.
#
# Sandbox note: this box lacks the scientific deps, so those tests fail here and pass in CI, where the
# baked images supply them. MEASURED 2026-08-05, rather than remembered -- absent: numpy, scipy, pymbar,
# rdkit, boto3, netCDF4; present: pyyaml, jsonschema. (The line here used to name "scipy, pymbar, rdkit"
# and omitted numpy and boto3, which between them account for 29 of the 48 baseline failures.) Rather
# than hide that behind an ignore list -- which would be the very "silently measures nothing" pattern
# above -- the test step reports a BASELINE count and fails only when failures EXCEED it. Update the
# baseline deliberately, in a commit, when the environment changes.
#
# Usage:  ./scripts/preflight.sh          # lint + tests
#         SKIP_TESTS=1 ./scripts/preflight.sh   # docs-only change
set -euo pipefail

cd "$(dirname "$0")/.."

# Known-failing-in-sandbox count. Raise ONLY with a recorded reason; lowering it is always safe.
#
# ⛔ RAISED 14 -> 48 ON 2026-08-05, AND THE RAISE IS A CORRECTION RATHER THAN A CONCESSION. The 14 was
# never measured against a run that executed anything: without `--continue-on-collection-errors` below,
# pytest aborted at collection and this script counted `^FAILED` lines in the output of a run that had
# tried zero tests. The first sweep that actually ran measured **50 failed** over `research/modalities/tests`
# alone (manuscripts and systems pass in full). That one figure is the whole evidence for the raise.
#
# ⚠ THE REST OF THAT SWEEP'S SUMMARY USED TO BE QUOTED HERE AND HAS BEEN REMOVED, BECAUSE A PASSED COUNT IS
# NOT A FACT ABOUT THIS GATE — IT IS A FACT ABOUT A SUITE THAT GROWS, so it starts going stale the moment it
# is committed and there is no check that would ever catch it. Superseded, retained (CLAUDE.md rule 1.2):
# `5984 passed, 107 skipped, 6 errors` in 596 s. Re-measured ONE DAY LATER, 2026-08-06, on the same command:
# the passed count had already moved by +135 and skipped by +8, and the collection-error count by −1, while
# the failure count this gate actually tracks had not moved at all. Exactly the drift the removal prevents.
# ⛔ SO DO NOT RE-TYPE THE CURRENT POPULATION HERE. This script MEASURES it on every run and prints it:
# `tail -1 "$out"` below emits pytest's own `N failed, M passed, K skipped, E errors` line. THAT printed
# line is the one home of the live count (CLAUDE.md rule 1: a total is derived, never typed).
#
# ⭐ ALL 50 WERE THEN CLASSIFIED RATHER THAN ASSUMED, ON 2026-08-05, and two were NOT dep-related. The split
# below is that day's reading, not a standing property — re-derive it rather than trusting it, by grouping
# the `ModuleNotFoundError` lines in the FAILURES section of this step's own output:
#   48  ModuleNotFoundError -- boto3 (20), rdkit (19), numpy (9). CI installs all three and runs green.
#    1  test_no_hand_rolled_publish -- a REAL failure, and the same one that had CI red. Fixed.
#    1  test_itemsize_survives_a_dtype_that_is_not_a_numpy_dtype -- a REAL bug in chk_prune._itemsize,
#       whose `except Exception` swallowed ImportError as well as the VLEN TypeError it was written
#       for, so every dtype fell back to 8 bytes where numpy is absent. Fixed.
# Those two are exactly what a gate reporting "0 failures" from an empty run cannot show you.
#
# THIS NUMBER SHOULD FALL as the sandbox gains packages. It describes a deficient environment; it is
# not a tolerance for broken tests, and every one is a missing import, not a failing assert.
#
# ⭐ RAISED 48 -> 50 ON 2026-08-07, AND THE RAISE IS MEASURED RATHER THAN CONCEDED. A raise is the
# dangerous direction for this field -- it is how a real regression gets absorbed -- so it was gated on
# a two-sided set comparison, not on a count:
#
#   clean `origin/main` worktree : 50 failed, 6367 passed
#   this branch after the merge  : 50 failed, 6409 passed
#   failing-test-name sets       : IDENTICAL -- both comm(1) directions empty, 50 vs 50
#
# So the branch adds 42 PASSING tests and zero failing ones. The cause of the drift is the suite
# GROWING against a fixed environment: more rdkit/pymbar/boto3-dependent modules land, each adds its
# import failure, and the count rises while nothing breaks. 6120 -> 6409 passing in one day.
#
# ⛔ DO NOT RAISE THIS ON A COUNT COMPARISON. Two counts agreeing proves nothing -- 2 new failures
# masked by 2 fixes reads identically. The check that matters is the NAME SET, and the way to get it is
# a worktree at the merge base (the command is printed by this script when the gate trips). An earlier
# attempt at exactly this comparison on the same day was VACUOUS because it diffed this script's own
# truncated 20-line output against a full 50-line list: a subset can never show "new on branch", so it
# returned a clean verdict it had no power to produce. Compare pytest's full list on both sides.
# ⛔ DERIVED FROM THE LIST, NEVER TYPED (CLAUDE.md rule 1.1: "a total is DERIVED, never typed --
# hand-carried totals drift silently"). This was hard-coded at 50 while the authoritative baseline
# list held 53, so every run printed a drift notice on an otherwise green build -- and a green build
# that always carries a note is a note nobody reads. The list is the source of truth; the count is a
# cross-check on it, so computing one from the other makes the two structurally unable to disagree.
# Superseded, retained: `BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-50}"`.
# ⚠ THIS DOES NOT WEAKEN THE GATE. What actually fails a run is a failure NOT NAMED in the list, and
# that check is untouched -- see the `comm -23` below. Deriving the count removes bookkeeping noise;
# it does not raise a ceiling, because the ceiling was never what caught anything.
_baseline_file=research/modalities/tests/sandbox-failure-baseline.txt
BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-$(
  grep -v '^#' "$_baseline_file" 2>/dev/null | sed '/^[[:space:]]*$/d' | sort -u | wc -l | tr -d ' '
)}"
BASELINE_FAILURES="${BASELINE_FAILURES:-0}"
rc=0

echo "== lint_consistency =="
if python3 research/manuscripts/lint_consistency.py; then
  echo "   OK"
else
  echo "   FAILED"; rc=1
fi

# ⛔ ADDED 2026-08-05 — THE SYSTEMS MODEL'S INVARIANTS WERE NOT IN THE STATED PRE-COMMIT GATE.
# CLAUDE.md §7 says "before committing, ./scripts/preflight.sh must pass", and this script did not run
# systems_check or parser_guard at all: ~35 invariants — a failing instrument cited as SUPPORT, a
# permanent blocker claiming a technology, a drifted generated view, a parser that has lost its input —
# were CI-only. Anyone following the documented workflow would not have run them.
echo "== systems model (invariants, pointers, view drift) =="
if python3 systems/systems_check.py --check >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 systems/systems_check.py --check' to see why"; rc=1
fi

# ⛔ ADDED 2026-08-06, AND IT COST A RED `main` TO NOTICE. This is the SIBLING registry of the gate
# above -- same shape, same "regenerate the view and diff it" discipline, pure stdlib, ~2 s -- and it
# was CI-only while its sibling was here. So a session could run this script, see PREFLIGHT OK, merge,
# and turn `main` red: a new generated view named a cell line whose identity is DISPUTED, and O4 (which
# requires every tracked file naming it to classify the use) fired in CI and nowhere else.
#
# ⚠ The gap was invisible in the worst way: the check that was missing is one of the two that enforce
# MEDICAL INTEGRITY rather than tidiness. A local gate that is green while the strongest evidentiary
# guard in the repository has not run is worse than no local gate, because it is trusted.
echo "== EMC systems map (disputed identities, claim artifacts, view drift) =="
if python3 research/manuscripts/emc_systems_map_check.py --check >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/emc_systems_map_check.py --check' to see why"; rc=1
fi

# ⛔ ADDED 2026-08-07, AND IT IS HERE RATHER THAN CI-ONLY BECAUSE THAT MISTAKE WAS MADE TWICE ABOVE.
# An agent drafting a manuscript wrote a PMID from RECOLLECTION -- present in no committed source
# anywhere in this repository -- and it PASSED lint_claims TWICE. Six invented titles and author-lists
# went out in the same pass, caught only by a human-directed audit.
#
# ⚠ lint_claims cannot catch this and is not deficient for failing to: it checks how strongly a claim is
# WORDED (R1-R5: selectivity, efficacy, safety, therapeutic window, clinical readiness). A fabricated
# identifier on a properly-hedged sentence is, to that linter, a perfect sentence. Claim STRENGTH and
# citation PROVENANCE are orthogonal, and no other gate reads an identifier at all -- against a
# repository whose FIRST golden rule is "never fabricate medical facts, stats, citations or patient
# data". This gate closes that and only that.
# ⛔⛔ lint_claims RUNS HERE NOW, AND ROUND 9 IS WHY (2026-08-22). It was CI-only by design, on the
# reading that CI would catch it. What actually happened: a manuscript repair introduced a word that
# fires R2, preflight went green, the commit shipped, and CI failed at this step -- which SKIPS the
# 26 steps behind it, so citation provenance, prose style and every manuscript test went unrun on
# that commit too. A gate whose failure blinds the rest of the suite belongs in the commit loop.
echo "== claim strength (R1-R5: selectivity, efficacy, safety, window, readiness) =="
if python3 research/manuscripts/lint_claims.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_claims.py' to see which claim"; rc=1
fi

# ⚠ AND lint_changed_prose, WHICH RAN NOWHERE AT ALL -- not in preflight, not in tests.yml. It is the
# only instrument that watches for a qualifier being dropped from a claim by an edit, which is the
# defect class that produced most of rounds 9-11's findings. It reports warnings rather than errors,
# so it cannot fail the build; printing them is the whole point.
echo "== changed prose (a qualifier dropped by an edit) =="
python3 research/manuscripts/lint_changed_prose.py || true

echo "== citation provenance (every prose identifier traces to a fetch or to the ledger) =="
if python3 research/manuscripts/lint_citations.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_citations.py' to see which identifier"; rc=1
fi

# ADDED 2026-08-09. The repository's house style -- glyph warnings, bold on the load-bearing clause,
# running commentary about why a rule exists -- is correct in CLAUDE.md, in the roadmap and in the
# artifacts, where the reader is a maintainer being stopped from repeating a mistake. It is wrong in a
# manuscript: a journal reader is not being warned, prose that keeps asserting its own honesty reads as
# advocacy, and the tics are recognisable as machine-written, which costs a paper credibility it has
# otherwise earned. Measured when this gate was added: 81 findings in the one manuscript then listed --
# 25 glyphs, 32 mid-sentence bolds, 14 sentence-shaped headings, bold at 20.1 per 1000 words against a
# limit of 12. Scoped to TARGETS in the linter; memos, plans and findings notes keep the house style.
echo "== manuscript prose style (journal register, not repository register) =="
if python3 research/manuscripts/lint_style.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_style.py' to see which lines"; rc=1
fi

echo "== parser guard (every registered parser can still find its input) =="
if python3 systems/parser_guard.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 systems/parser_guard.py' to see why"; rc=1
fi

echo "== validate (EMC clinical registry evidence contract) =="
if node scripts/validate-registry.mjs >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'node scripts/validate-registry.mjs' to see why"; rc=1
fi

# ⛔ A FILE MARKED "GENERATED" WAS AN INSTRUCTION TO HUMANS BACKED BY NOTHING (added 2026-08-16).
# Four deposit artifacts are produced by generators and carry GENERATED banners, and no gate ever
# re-derived any of them. Round 7 measured THREE of the four stale at once: the archive manifest 78
# commits behind HEAD (so the recorded manuscript hash described a pre-restructure file), and
# submission-metrics.json under-counting by 263 main words while every other deposit document
# defers to it as "the one home" for those counts. Both had been wrong for weeks under nine green
# gates, because "is this file current?" was a question nothing could ask.
# ⚠ THE MANIFEST ALREADY HAD A --check MODE AND NO GATE RAN IT. Two of the others were given one in
# the same pass that added this block; the fourth (submission_packet.py) still has none and is
# named as unverified by scripts/regenerate_aso_chain.sh rather than silently assumed current.
# ⚠ POSITION IS LOAD-BEARING, AND NOT FOR A TECHNICAL REASON. This gate was first inserted BEFORE
# the parser guard, which pushed the registry validator from gate 7 to gate 8 -- and four documents
# (README.md, CONTRIBUTING.md, systems/POLICY-evidence.md and .claude/skills/repo-gates/SKILL.md)
# state its ordinal in prose. systems_check's P1 rule caught all four immediately, which is the
# one-fact-one-place rule doing its job on a change that looked purely additive. Appending here
# leaves every existing ordinal untouched; it still runs before the test steps, which is all this
# gate's placement actually requires. ⛔ Insert a new gate ABOVE this line and you will move an
# ordinal that four documents hard-code.
echo "== generated deposit artifacts reproduce from their generators =="
gen_fail=""
# ⛔ THE MANIFEST TAKES `--check-archive`, NOT `--check`, AND THE DIFFERENCE IS NOT COSMETIC.
# `aso_archive_manifest.py` stamps `git_revision`, which advances on EVERY commit — including
# commits touching no archived file — so `--check` is red the instant you commit the manifest you
# just regenerated. Measured 2026-08-17: PREFLIGHT_FULL=1 failed on exactly that, one commit after
# the manifest was regenerated and committed. The generator's own header had predicted it in words
# and said not to wire `--check` into preflight; this gate did anyway.
# ⚠ THE FIX IS NOT TO DROP THE MANIFEST FROM THE GATE. A cry-wolf gate gets relaxed, and the
# relaxation that suggests itself is removing the row — which is how a REAL hash-list staleness
# would then go unwatched. `--check-archive` compares everything except the two repository-state
# fields, so it still fails when the inventory, the hashes or the promises move, and no longer
# fails because a commit happened. The strict `--check` remains the pre-deposit check.
for g in "research/manuscripts/submission_tables.py|submission tables|--check" \
         "research/manuscripts/submission_citations.py|submission references|--check" \
         "research/manuscripts/submission_metrics.py|submission metrics|--check" \
         "research/manuscripts/aso_sequence_manifest.py|canonical sequence file|--check" \
         "research/manuscripts/aso_journal_tables.py|journal article tables|--check" \
         "research/manuscripts/vaccine_path_tables.py|vaccine-path manuscript tables|--check" \
         "research/manuscripts/aso_archive_manifest.py|archive manifest|--check-archive"; do
  gen="${g%%|*}"; rest="${g#*|}"; label="${rest%%|*}"; mode="${rest##*|}"
  if python3 "$gen" "$mode" >/dev/null 2>&1; then
    echo "   OK   $label"
  else
    echo "   STALE $label -- rerun 'python3 $gen' and commit the result"
    gen_fail="$gen_fail $label"; rc=1
  fi
done
[ -n "$gen_fail" ] && echo "   ⛔ a stale generated file ships a claim its own artifacts no longer support:$gen_fail"

if [ "${SKIP_TESTS:-0}" != "1" ]; then
  # ⭐ CHANGE-SCOPED BY DEFAULT, FULL ON DEMAND (trimcrae, 2026-08-12: the suite was the bottleneck,
  # and "only the ones affected by the changes" plus "not on every push, manually before
  # publication").
  #
  # MEASURED, which is why this changed: the modalities step was **745.9 s of a ~15-minute gate**,
  # 87 % of preflight, while the seven doc / systems-model / medical-integrity gates above cost
  # about a minute between them — and those are the ones that have actually caught things here.
  #
  # ⚠ AND THE EXPENSIVE COPY IS THE WEAKER ONE. This sandbox lacks numpy, rdkit, boto3, scipy,
  # pymbar and netCDF4, so 48 of these tests fail as missing imports and five modules do not import
  # at all. `tests.yml` runs `on: push` WITH those dependencies installed, so the version of this
  # suite that means something runs in CI on every push regardless. Twelve local minutes bought a
  # degraded rerun of a check that was about to run properly.
  #
  # ⛔ THE SELECTOR FAILS TO FULL, AND THAT IS THE WHOLE SAFETY ARGUMENT. A changed conftest, a
  # changed test helper, an unparseable source, a git that does not answer, or an edit to the
  # selector or to this script all return FULL rather than a subset — because a gate that quietly
  # runs too little is the "reports while measuring nothing" defect this file was written against,
  # not a faster gate. `scripts/tests/test_affected_tests.py` asserts each of those directions.
  #
  # ⛔ BEFORE ANYTHING OUTWARD-FACING — a preprint, a submission, a release, a DOI — run
  #     PREFLIGHT_FULL=1 ./scripts/preflight.sh
  # Scoping is for the commit loop. It is not a claim that the rest of the suite passes.
  # ⛔ HOW PYTEST IS INVOKED, AND WHY IT IS NOT `python3 -m pytest` (measured 2026-08-15).
  # Both test steps below called `python3 -m pytest` and BOTH reported "No module named pytest" in
  # this sandbox, which the count guard correctly turned into a hard FAILED -- so preflight could
  # not be run at all, and the only ways past it were to skip tests or to mask the exit code. The
  # cause is not a missing pytest: `pytest --version` answers 9.0.2. It is installed as a **uv
  # tool**, in an isolated venv under /root/.local/share/uv/tools/pytest, whose interpreter is not
  # the `python3` on PATH -- so the console script works and `-m` cannot. Resolved once, here, and
  # exported, rather than at each call site: a per-call fallback is how one of the two steps ends up
  # fixed and the other silently left behind. If neither form exists, PYTEST stays as `python3 -m
  # pytest` so the run still FAILS loudly with the same message rather than skipping quietly --
  # never resolve this to `true` or to a no-op.
  #
  # ⛔ THE ORDER OF THESE TWO BRANCHES IS LOAD-BEARING, AND THE CONSOLE-SCRIPT FALLBACK IS A TRAP
  # (measured 2026-08-15, the same day, an hour after the block above was written). Resolving to the
  # bare `pytest` on PATH made the gate report **36 failures that do not exist**: that pytest was a
  # uv TOOL, and a uv tool runs in its OWN isolated venv, so `import yaml` failed inside the tests
  # while `python3 -c "import yaml"` succeeded in the shell one line earlier. Every one of the 36 was
  # a ModuleNotFoundError for a package the repository actually has. They were proved spurious the
  # expensive way -- a worktree at origin/main, the same eight files, two-sided `comm` on the failure
  # NAME SETS: 39 on main, 39 on branch, both directions EMPTY.
  # ⚠ SO A GREEN `python3 -c "import pytest"` IS NOT MERELY THE PREFERRED BRANCH, IT IS THE ONLY ONE
  # THAT SEES THE REPOSITORY'S DEPENDENCIES. The fix when the first branch is false is to
  # `python3 -m pip install pytest`, NOT to fall through -- the fallback exists so the gate can still
  # run somewhere degraded, and its failures must be read as suspect until traced. A gate that
  # invents failures is as broken as one that hides them: this one nearly got 36 healthy tests
  # written into the sandbox baseline as permanent known-failures, which would have masked a real
  # regression in any of them forever.
  if python3 -c "import pytest" >/dev/null 2>&1; then
    PYTEST="python3 -m pytest"
  elif command -v pytest >/dev/null 2>&1; then
    PYTEST="pytest"
  else
    PYTEST="python3 -m pytest"
  fi

  # ⛔ THE GATE WAS SINGLE-THREADED ON A FOUR-CORE BOX, AND THAT COST 16 MINUTES A RUN.
  # Measured 2026-08-17 on this tree: the modalities suite is 968.9s serial and 336.9s at `-n 4
  # --dist loadfile`, a 2.9x saving, with the verdict IDENTICAL -- 14 failed, 7,756 passed, 58
  # skipped both ways, the same 14 tests by name, every one already in sandbox-failure-baseline.txt,
  # and the working tree clean afterwards.
  # ⚠ `--dist loadfile` IS LOAD-BEARING, NOT A TUNING CHOICE. Several tests regenerate a committed
  # artifact and then assert against it; distributing by TEST rather than by FILE would let two
  # workers race the same file and produce failures that are real-looking and untrue. Keeping every
  # test in a file on one worker preserves the within-file ordering those tests rely on. The clean
  # tree after the parallel run is the evidence that no regeneration raced.
  # ⛔ IF XDIST IS ABSENT, RUN SERIAL. A missing plugin must slow the gate down, never skip it.
  PYTEST_PAR=""
  if [ "${PREFLIGHT_SERIAL:-0}" != "1" ] && python3 -c "import xdist" >/dev/null 2>&1; then
    _cores=$(nproc 2>/dev/null || echo 1)
    [ "$_cores" -gt 1 ] && PYTEST_PAR="-n $_cores --dist loadfile"
  fi

  # ⛔ THE SELECTOR IS ASKED ONCE, AND ITS THREE ANSWERS ARE KEPT APART (measured 2026-08-16).
  # This block used to call `affected_tests.py` here, discard the result, and call it AGAIN below to
  # decide whether an empty selection meant "nothing affected". That conflated two opposite answers:
  #   "" from a selector that RAN and found nothing   -> correctly green, run nothing
  #   "" from a selector that DIED before printing    -> must run everything
  # The first call caught the second case safely (`|| echo FULL`) and the second call then threw that
  # away, because a dead selector's stdout is also empty. MEASURED CONSEQUENCE: an editorial pass
  # broke 11 tests in `test_aso_submission_numbers.py` -- all 35 pass at c131f5a30, 11 fail after --
  # and preflight printed "FULL -- the change could not be scoped" IMMEDIATELY followed by "no
  # modality test is affected by this change" and exited 0, having run zero modality tests. Four
  # commits were made against that green.
  # ⚠ This is the header defect of this very file, for the fifth time: a gate that reports while
  # measuring nothing. The rule it violates is the one the block below already states -- an empty
  # selection is a real answer -- but only when the selector actually answered.
  SELECTED=""
  SEL_STATUS=full
  if [ "${PREFLIGHT_FULL:-0}" = "1" ]; then
    echo "== pytest (modalities: FULL, PREFLIGHT_FULL=1) =="
  elif SELECTED="$(python3 scripts/affected_tests.py 2>/dev/null)"; then
    if [ "$SELECTED" = "FULL" ]; then
      SELECTED=""
      echo "== pytest (modalities: FULL -- the selector asked for the full suite) =="
    elif [ -z "$SELECTED" ]; then
      SEL_STATUS=none
      echo "== pytest (modalities: none -- the selector ran and this change affects no module) =="
    else
      SEL_STATUS=scoped
      n=$(printf '%s\n' "$SELECTED" | grep -c . || true)
      echo "== pytest (modalities: $n module(s) affected by this change; PREFLIGHT_FULL=1 for all) =="
    fi
  else
    SELECTED=""
    echo "== pytest (modalities: FULL -- the selector FAILED, so nothing is assumed) =="
  fi
  out=$(mktemp)
  # ⛔ `--continue-on-collection-errors` ADDED 2026-08-05, AND WITHOUT IT THIS STEP MEASURED NOTHING.
  #
  # Five test modules in this sandbox fail to IMPORT. Without this flag pytest prints
  # `Interrupted: 5 errors during collection` and EXITS HAVING RUN ZERO TESTS. The
  # parser below then greps for `^FAILED`, finds none, and prints
  #     OK (0 failures, at/below the 14 sandbox baseline -- all dep-related, green in CI)
  # -- a green line, from a run that executed no test at all. The real number that day was 50.
  #
  # ⚠ THIS LINE USED TO NAME THE CAUSE — "(scipy, pymbar, rdkit are absent)" — AND THAT WAS THE SAME WRONG
  # TRIPLE THE SANDBOX NOTE AT THE TOP OF THIS FILE ALREADY RECORDS AS CORRECTED. The correction landed up
  # there on 2026-08-05 and was missed HERE, ~85 lines away in the same file: one fact, two places, one of
  # them repeating the error the other had already retired. Measured 2026-08-06, not remembered: all five
  # collection errors are `ModuleNotFoundError: No module named 'numpy'` — not one is scipy, pymbar or rdkit.
  # Superseded, retained (CLAUDE.md rule 1.2): "(scipy, pymbar, rdkit are absent)".
  # ⛔ The cause is deliberately NOT re-typed here now. It is one command, and it answers for today:
  #     $PYTEST $PYTEST_PAR research/modalities/tests/ -q --collect-only --continue-on-collection-errors \
  #       --ignore=research/modalities/tests/test_ternary_endpoint_align.py 2>&1 | grep ModuleNotFoundError
  #
  # ⚠ THAT IS THIS SCRIPT'S OWN HEADER DEFECT, IN THIS SCRIPT. The comment at the top of this file
  # exists because a check "reported while measuring nothing actionable", and names three prior
  # instances. This was a fourth, sitting inside the fix for the first three. `set -euo pipefail` and
  # an explicit exit code do not help when the thing being counted is never produced.
  # ⚠ AN EMPTY SELECTION IS A REAL ANSWER — "this change touches no modality test" — and pytest
  # exits 5 on "no tests ran", which must not read as a failure. It is handled below.
  # ⛔ BRANCH ON SEL_STATUS, NEVER ON EMPTINESS, AND NEVER RE-ASK THE SELECTOR. `$SELECTED` is empty
  # for BOTH "nothing affected" and "run everything"; only SEL_STATUS distinguishes them, and it was
  # decided once, above, where the selector's exit code was still in hand.
  if [ "$SEL_STATUS" = "scoped" ]; then
    # shellcheck disable=SC2086
    $PYTEST $PYTEST_PAR $SELECTED -q --continue-on-collection-errors >"$out" 2>&1 || true
  elif [ "$SEL_STATUS" = "none" ]; then
    echo "no modality test is affected by this change" >"$out"
  else
    $PYTEST $PYTEST_PAR research/modalities/tests/ -q --continue-on-collection-errors \
        --ignore=research/modalities/tests/test_ternary_endpoint_align.py >"$out" 2>&1 || true
  fi
  failed=$(grep -cE '^FAILED' "$out" || true)
  errored=$(grep -cE '^ERROR ' "$out" || true)
  tail -1 "$out"

  # ⛔ A RUN THAT EXECUTED NOTHING IS NOT A PASS. Belt and braces against the failure above returning
  # in another form: if pytest never reports a test count, the parsed failure count is meaningless and
  # this step must go red rather than quietly agree with itself.
  if grep -q '^no modality test is affected by this change$' "$out"; then
    echo "   OK (no modality test is affected; CI runs the full suite on push)"
  elif ! grep -qE '[0-9]+ (passed|failed)' "$out"; then
    echo "   FAILED: pytest reported no test count -- the run collected nothing, so '0 failures' would"
    echo "           be a statement about an empty run. Last lines:"
    tail -5 "$out"
    rc=1
  else
    # ⛔ THE GATE NOW DIFFS A LIST, NOT A COUNT, AND THAT CHANGE IS AN INCIDENT FIX (2026-08-08).
    # A count cannot tell a new real failure from a missing module. Measured: a genuine regression
    # (test_lint_citations.py::test_the_ledger_does_not_anchor_itself, broken by a newly committed
    # artifact) took the count 48 -> 49, sat under the baseline of 50, and this gate printed
    # PREFLIGHT OK -- "all dep-related, green in CI", asserted without checking. That tree was pushed
    # and turned `main` red, where CI with full deps reported exactly 1 failure against 7,363 passes.
    #
    # ⚠ THE PREVIOUS VERSION KNEW THIS ABOUT ITSELF. It printed, correctly, "THE NEW FAILURE(S) ARE NOT
    # IDENTIFIED BELOW ... This gate tracks a COUNT, not a list", and that honesty was mistaken for
    # sufficiency -- a limitation stated in prose is still a limitation. It only ever printed when the
    # count was EXCEEDED, so the case that actually bit (a real failure that fits under the ceiling,
    # because a dep failure was fixed or never counted) produced no warning at all.
    # Superseded, retained (CLAUDE.md rule 1.2): the `-gt "$BASELINE_FAILURES"` count comparison and
    # its "excess:" readout. BASELINE_FAILURES is kept only as the cross-check below.
    base=research/modalities/tests/sandbox-failure-baseline.txt
    if [ ! -f "$base" ]; then
      echo "   FAILED: $base is missing. Without it this gate would fall back to trusting a count,"
      echo "           which is the defect it was built to remove. Restore it from git."
      rc=1
    else
      got=$(mktemp); known=$(mktemp)
      # ⛔ `|| true` BECAUSE grep EXITS 1 ON NO MATCH AND THIS SCRIPT RUNS `set -euo pipefail`
      # (2026-08-12). No match here means ZERO test failures — the good case — so the pipeline
      # returned 1 and `set -e` killed preflight at exactly the moment everything passed. The
      # damage was not the non-zero exit: gate 9, the manuscript tests, sits BELOW this line and
      # therefore never ran locally at all, while the script's own header comment warns about this
      # precise interaction. A gate that is skipped in silence is the failure mode CLAUDE.md §7
      # records; here the skip was caused by the suite being green.
      grep -E '^FAILED' "$out" | sed 's/^FAILED //; s/ - .*//' | sed 's/[[:space:]]*$//' \
        | sort -u >"$got" || true
      grep -v '^#' "$base" | sed '/^[[:space:]]*$/d' | sort -u >"$known"
      new=$(comm -23 "$got" "$known"); fixed=$(comm -13 "$got" "$known")
      if [ -n "$new" ]; then
        echo "   FAILED: $(printf '%s\n' "$new" | wc -l | tr -d ' ') failure(s) NOT in the sandbox baseline."
        echo "   ⚠ These are NEW and are named in full -- they are not the known dep gap:"
        printf '%s\n' "$new" | sed 's/^/     /'
        echo "   If one is genuinely a missing-dependency failure, trace it to the module and add it to"
        echo "   $base in the same commit, with the reason. Never add one to silence it."
        rc=1
      else
        echo "   OK ($failed failure(s), every one named in the sandbox baseline as dep-related;"
        echo "       $errored module(s) could not be imported here and are counted separately)"
      fi
      # ⛔ A SUBSET CANNOT SAY A BASELINE ENTRY IS FIXED, AND SAYING SO WOULD BE THE WORST KIND OF
      # WRONG (2026-08-12, with the change-scoped run above). `fixed` is comm(1) over the baseline
      # minus THIS RUN's failures — so a scoped run, which never executed most of the suite, would
      # report every unrun entry as "no longer fails, prune it". Acting on that would delete the
      # baseline wholesale and the next full run would go red against nothing. The list is only
      # meaningful when the run that produced it covered the same population, so it is printed only
      # for a full run; for a scoped one the pruning question is simply not asked.
      if [ -n "$fixed" ] && [ -z "$SELECTED" ]; then
        # Not a failure: the list is meant to shrink, and a stale entry quietly widens what is tolerated.
        echo "   ⓘ $(printf '%s\n' "$fixed" | wc -l | tr -d ' ') baseline entr(y/ies) no longer fail -- prune them from $base:"
        printf '%s\n' "$fixed" | sed 's/^/     /'
      elif [ -n "$SELECTED" ]; then
        echo "   ⓘ scoped run — the baseline-pruning check is skipped (a subset cannot speak for"
        echo "     tests it did not execute). Run PREFLIGHT_FULL=1 to re-derive it."
      fi
      # Cross-check the retained count against the list, so the two can never disagree silently.
      if [ "$failed" -gt "$BASELINE_FAILURES" ] && [ -z "$new" ]; then
        echo "   ⓘ $failed failures exceeds the retained count baseline $BASELINE_FAILURES, but every one is"
        echo "     in the list. Lower BASELINE_FAILURES or re-check the list -- they have drifted apart."
      fi
      rm -f "$got" "$known"
    fi
  fi
  rm -f "$out"

  # ⛔ GATE 9: THE MANUSCRIPT TESTS, WHICH THIS SCRIPT DID NOT RUN UNTIL 2026-08-12.
  #
  # CI has run `research/manuscripts/tests` since 2026-08-03 and preflight never did, so a session
  # could read PREFLIGHT OK and push a manuscript guard failure — the exact shape of the 2026-08-06
  # incident recorded in CLAUDE.md §7, where gate 3 was CI-only and a disputed cell line reached
  # `main` behind a green local run. What made this worth closing today rather than noting: the
  # newest guard here is `test_submission_citations.py`, and citation integrity is the repository's
  # FIRST golden rule. A citation guard that only fires after the push is a citation guard that
  # fires after the mistake is shared.
  #
  # ⚠ RUN SEPARATELY, NOT FOLDED INTO THE INVOCATION ABOVE. That one diffs its failures against
  # `sandbox-failure-baseline.txt`, whose entries are all modalities test IDs; widening its scope
  # would silently change what the baseline is a baseline OF. These have no dep gap in this sandbox
  # — 151 passed, 0 failed, measured the day this gate was added — so the bar here is simply zero.
  echo "== pytest (manuscripts: endpoints, systems map, pooling, submission citations) =="
  mout=$(mktemp)
  $PYTEST $PYTEST_PAR research/manuscripts/tests -q --continue-on-collection-errors >"$mout" 2>&1 || true
  tail -1 "$mout"
  if ! grep -qE '[0-9]+ (passed|failed)' "$mout"; then
    echo "   FAILED: pytest reported no test count -- the run collected nothing."
    tail -5 "$mout"; rc=1
  elif grep -qE '^(FAILED|ERROR )' "$mout"; then
    echo "   FAILED:"; grep -E '^(FAILED|ERROR )' "$mout" | sed 's/^/     /'
    rc=1
  else
    echo "   OK"
  fi
  rm -f "$mout"
fi

if [ "$rc" -ne 0 ]; then
  echo; echo "PREFLIGHT FAILED -- do not commit."
else
  echo; echo "PREFLIGHT OK"
fi
exit "$rc"
