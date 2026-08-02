#!/usr/bin/env python3
"""A DECLARED ARTIFACT THAT NOTHING PRODUCES IS NOT AN ARTIFACT — the lane registry, verified.

WHY THIS EXISTS. `lane_staleness_watch.LANES` is a DECLARATION: each entry names the files the watcher will
read to decide whether a billing lane is advancing, held, or dead. Nothing checked that any of those names
corresponded to a real thing, and on 2026-07-31 one of them did not.

    `nrv04-retro-market-hold.json` was named in THREE places as a thing that exists — this registry (the
    `nrv04-retro` lane's `hold_artifact`), `nrv04_vast_launch.RETRO_MARKET_READOUT`, whose docstring said it
    "is written to ..., printed, and annotated with `::notice::`", and `fusion-cpu-extras.yml`'s commit list.
    IT HAD NEVER BEEN COMMITTED. The other four lanes' hold artifacts all existed and were minutes old.
    Consequence: the NR-V04 Arm E pilot sat hostless from 12:07 PM to 2:02 PM ET — 1 h 55 m across TEN ticks
    of a supervisor that runs every 8 minutes and is permitted to buy — and the reason it declined each time
    was recorded nowhere. CLAUDE.md §6 requires the exact opposite: "a fleet that never launched looks
    identical to one that finished", so a decision to decline must never be silent. A human noticed before
    the monitoring did.

That file is committed now. **That is precisely why this test exists**: a fix nothing pins regrows, and the
failure mode is silent by construction — an absent artifact makes the watcher say "not present in the repo",
which reads like a lane being quiet rather than like a monitor that was never wired up.

★★ THE THREE RULES, AND WHY BOTH HALVES ARE NEEDED. Presence and provenance answer different questions and
neither substitutes for the other — the same two-sided discipline as CLAUDE.md §4's "an absent reading is not
a reading of absence, and a populated field is not a measured one":

  1. EXISTENCE proves the write reached git AT LEAST ONCE. Nothing else does.
  2. A PRODUCER proves it can happen AGAIN. Existence alone passes on a file written once by hand and never
     regenerated — and the 2026-07-31 incident proves the converse just as hard: `RETRO_MARKET_READOUT` was
     a real module constant naming the file the whole time it did not exist. **A constant is not a commit.**
  3. The `tick_workflow` an entry names must be a workflow that exists, or the lane's supervision verdict
     (`supervision_for`) is asking the Actions API about a file nobody ships.

★★ WHAT THIS TEST DELIBERATELY DOES NOT DO: replace the explicit registry with a discovered one. That is
already litigated at `lane_staleness_watch.py`'s "WHY THE FIVE LANES ARE NAMED EXPLICITLY RATHER THAN
DISCOVERED" — a discovered list silently shrinks, so a lane whose artifact went missing would simply not
appear and "not watched" would render exactly like "healthy". Naming them is what makes "the retro tick
stopped" LOUD. So the list stays explicit and this VERIFIES it. In the same spirit, and per
`TESTING.md` rule 7 (assert the property, never a label or a population count), **nothing here counts the
lanes**: every check is parameterised over whatever `LANES` holds, so a new lane is covered the moment it is
added and a new lane that forgets an artifact fails BY NAME rather than moving a total nobody can grade.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
THE FOUR FIELDS ARE NOT THE SAME KIND OF THING, AND TREATING THEM ALIKE WOULD MANUFACTURE FALSE FAILURES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
`generation_artifact` / `hold_artifact`   the tick's OWN EVIDENCE, rewritten every pass. Must EXIST and must
                                          have a producer. This is the incident's shape, and it has NO escape
                                          hatch of any kind. `generation_artifact: None` already means
                                          "deliberately absent, stated not faked" (the census lives in S3) and
                                          that existing convention is honoured rather than duplicated.
`terminal_artifact`                       the lane's DELIVERABLE. Absent is the NORMAL state of an unfinished
                                          lane — demanding it exist would fail every lane that is still
                                          running, which is most of them. So: existence NOT required, producer
                                          REQUIRED. A terminus nothing can write is a lane that can never be
                                          graded FINISHED.
`watch_file`                              a DECLARATIVE INPUT the tick reads, not an output. Demanding a
                                          producer would be a false requirement: nothing in this repo writes
                                          `ternary-watch.json` — `gcp_launch_guard.py` and
                                          `watchdog_validate.py` only validate and read it. So: must EXIST and
                                          must be READ somewhere outside this registry, i.e. not an orphan.
                                          ⚠ AND IT COULD NOT HONESTLY BE GRADED THE OTHER WAY: the producer
                                          idioms below cannot tell a READ-path constant from a WRITE-path one
                                          (`gcp_watch_reap.DEFAULT_PATH = "research/modalities/
                                          ternary-watch.json"` matches "assigned to a name" and is a reader),
                                          so applying rule 2 here would pass on evidence that proves nothing.
"""
from __future__ import annotations

import functools
import os
import pathlib
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import lane_staleness_watch as lsw  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
MODALITIES = REPO / "research" / "modalities"
WORKFLOWS = REPO / ".github" / "workflows"

# The file the declaration lives in. A name that appears ONLY here is an orphan by definition — the registry
# claiming a file exists is the claim under test, so it cannot also be the evidence for it.
REGISTRY_MODULE = "lane_staleness_watch.py"

PRODUCED_EVERY_TICK = ("generation_artifact", "hold_artifact")
PRODUCED_AT_THE_END = ("terminal_artifact",)
DECLARED_INPUT = ("watch_file",)
ARTIFACT_FIELDS = PRODUCED_EVERY_TICK + PRODUCED_AT_THE_END + DECLARED_INPUT

# ★★ THE ONE KEY THAT MAY EXCUSE A MISSING PRODUCER, AND THE FOUR THINGS THAT KEEP IT FROM BECOMING AN
# OFF SWITCH. A guard with a general escape hatch is not a guard, so this one is typed as narrowly as the
# honest case requires:
#   (a) it is legal ONLY beside `terminal_artifact` — the incident's fields (`hold_artifact`,
#       `generation_artifact`) and `watch_file` can NEVER be silenced, which is the whole point;
#   (b) it must carry a substantive reason, not a token;
#   (c) it must still be TRUE — if a producer for that artifact ever appears, this test goes RED and tells
#       you to delete the key. The marker self-retires; it cannot outlive the bug it records;
#   (d) the entry remains subject to every other rule here.
# Registering a known-false declaration in the open, where the claim lives, is CLAUDE.md §1's rule for a
# superseded value: never silently drop it, never leave it unmarked.
TERMINAL_UNBACKED_KEY = "terminal_artifact_unbacked"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the corpus, and what counts as PRODUCING a file
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@functools.lru_cache(maxsize=1)
def _corpus() -> tuple[tuple[str, int, str, bool], ...]:
    """Every line of every file that could plausibly produce a lane artifact: `(relpath, lineno, text, is_comment)`.

    Scope is the modalities scripts and the workflows, minus the registry module itself and minus `tests/`.
    Excluding the tests matters: a test that mentions a filename is not a producer, and letting one count
    would mean this very file could vouch for the name it is checking.
    """
    out: list[tuple[str, int, str, bool]] = []
    paths = [p for p in sorted(MODALITIES.glob("*.py")) if p.name != REGISTRY_MODULE]
    paths += sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:  # pragma: no cover - unreadable file in the tree is its own problem
            continue
        rel = os.path.relpath(p, REPO)
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            out.append((rel, i, s, s.startswith("#")))
    return tuple(out)


# ★ PRODUCING POSITIONS, AS STRUCTURE RATHER THAN AS WORDING. TESTING.md rule 7 warns against pinning a
# label; these pin CONSTRUCTS, each of which is a real way this repo creates a committed artifact today.
# A failure prints every candidate site it found, so a new idiom is a five-second diagnosis and a one-line
# addition rather than a mystery.
PRODUCER_IDIOMS: tuple[tuple[str, re.Pattern], ...] = (
    # ⚠ `.*?` AND NOT `[^)]*`, WHICH IS WHAT THIS WAS FIRST WRITTEN AS. A character class excluding `)`
    # cannot cross a nested call, so it silently missed `open(os.path.join(OUT, "x.json"), "w")` — the
    # single most common write in this package. No lane artifact happened to use that shape, so every rule
    # here still passed: a FALSE NEGATIVE that would have gone red on the next lane rather than on this
    # commit. Caught by sweeping the repo for "written to X" claims and finding one the checker called
    # unproduced while `nr4a3_fpocket_enumerate.py:157` plainly writes it.
    ("open-for-write", re.compile(r"open\s*\(.*['\"]w['\"]")),
    ("an output flag", re.compile(r"--(?:gate-)?out\b|--json\b")),
    ("git add", re.compile(r"\bgit\s+add\b")),
    # `RETRO_MARKET_READOUT = "..."`, `OUT = os.path.join(HERE, "...")`, and the shell `F=research/...`
    # that a later `git add "$F"` commits.
    ("assigned to a name", re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*\s*=|[A-Z_]+=)")),
    # A bare path on its own line: the `path:`/`git add` multi-line lists in the workflows, AND the
    # argument lists handed to `research/compute/publish_artifacts.sh`.
    # ⚠ THE TRAILING ` \` IS THE WHOLE POINT OF THE SECOND GROUP (2026-08-01). Every publish converted to
    # the primitive spells its artifacts as continued shell arguments —
    #     bash research/compute/publish_artifacts.sh "$BRANCH" \
    #       "message" \
    #       research/modalities/inflight-board.d/nrv04-retro.json
    # — so all but the LAST path carries a continuation. Without it this rule reported "NOTHING IN THE REPO
    # PRODUCES IT" for a file being committed on every tick, which is a false alarm that would fire once per
    # converted lane and get the whole guard ignored. `research/` rather than `research/modalities/` because
    # the same lists carry `research/compute/gcp-gpu-facts.md`.
    ("a committed/uploaded path list", re.compile(r"^research/\S+(?:\s*\\)?$")),
)


def references(artifact: str) -> list[tuple[str, int, str]]:
    """Every NON-COMMENT mention of the artifact's basename outside the registry and the tests.

    Basename, not the declared path: `inflight-board.d/nrv04-retro.json` is written by a workflow that spells
    the path from the repo root, and a lane's artifacts are read relative to whichever root that lane commits
    to (`--source-root`), so the leading directory is not stable and matching on it would miss real writers.
    """
    base = artifact.rsplit("/", 1)[-1]
    return [(f, i, s) for f, i, s, is_comment in _corpus() if base in s and not is_comment]


def producer_sites(artifact: str) -> list[tuple[str, str, int, str]]:
    """The subset of `references` that sit in a producing position, tagged with which idiom matched."""
    hits = []
    for f, i, s in references(artifact):
        for name, rx in PRODUCER_IDIOMS:
            if rx.search(s):
                hits.append((name, f, i, s))
                break
    return hits


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the rules, as PURE predicates over one registry entry — so the negative control below can exercise the
# checker itself rather than only the data it happens to be pointed at
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _declared(spec: dict) -> list[tuple[str, str]]:
    """`(field, path)` for every artifact field this entry actually sets. `None` is skipped on purpose: it is
    the registry's existing way of saying "deliberately absent, stated not faked"."""
    return [(f, spec[f]) for f in ARTIFACT_FIELDS if isinstance(spec.get(f), str) and spec[f]]


def existence_problems(spec: dict) -> list[str]:
    """RULE 1 — a declared path that the watcher READS must be a real file. No escape hatch.

    `terminal_artifact` is exempt BY FIELD, not by entry: it is the lane's deliverable and its absence is the
    normal state of an unfinished lane. That exemption is structural and stated once (§1: one fact, one
    place), rather than copied as a per-lane excuse into every entry that has not landed yet.
    """
    out = []
    for field, rel in _declared(spec):
        if field in PRODUCED_AT_THE_END:
            continue
        if not (MODALITIES / rel).exists():
            out.append(
                f"{spec['key']}.{field} = {rel!r} — DECLARED BUT NOT IN THE REPO. The watcher reads this "
                f"file every tick; when it is absent `load_json` returns 'not present in the repo' and the "
                f"lane's hold/generation state silently stops being measured. This is the 2026-07-31 "
                f"`nrv04-retro-market-hold.json` shape: 1 h 55 m of a supervisor declining to buy with the "
                f"reason recorded nowhere. Either commit the producer's output or set the field to None, "
                f"which is this registry's existing way of saying 'deliberately absent, stated not faked'."
                f"\n    SECOND DIAGNOSIS, and it is not a reason to relax this check: a lane re-pointed at a "
                f"long-lived branch would have its artifacts land THERE and vanish from main, which reads "
                f"here as an absent artifact. That is CLAUDE.md §7's branch-drift data-loss bug — main said "
                f"the fan-out was 1 of 19 edges while the branch held 14 — so a red here is CORRECT for it "
                f"too. The remedy is port-then-switch, never widening this test's search path.")
    return out


def producer_problems(spec: dict) -> list[str]:
    """RULE 2 — something in the repo must actually WRITE each produced artifact.

    Existence alone would pass on a file written once by hand and never regenerated, which is a monitor that
    reports a frozen snapshot forever. This is the half that proves it can happen again.
    """
    out = []
    excused = spec.get(TERMINAL_UNBACKED_KEY)
    for field, rel in _declared(spec):
        if field in DECLARED_INPUT:
            continue
        sites = producer_sites(rel)
        if sites:
            if field in PRODUCED_AT_THE_END and excused:
                # (c) the marker must still be true — a producer landing retires it.
                out.append(
                    f"{spec['key']}.{TERMINAL_UNBACKED_KEY} is STALE: {rel!r} now has a producer at "
                    f"{sites[0][1]}:{sites[0][2]} ([{sites[0][0]}]). Delete the key — a marker recording a "
                    f"gap that has been closed is a false statement in the registry.")
            continue
        if field in PRODUCED_AT_THE_END and excused:
            continue
        seen = references(rel)
        out.append(
            f"{spec['key']}.{field} = {rel!r} — NOTHING IN THE REPO PRODUCES IT. "
            + (f"It is named at {len(seen)} non-comment site(s) outside this registry "
               f"({', '.join(f'{f}:{i}' for f, i, _ in seen[:4])}) but none of them is a producing position "
               f"({', '.join(n for n, _ in PRODUCER_IDIOMS)})."
               if seen else
               "It is named at exactly ONE site in the whole repo: this registry entry. A declaration is not "
               "a producer.")
            + " A watcher graded on a file no code path can create is a monitor that cannot ever report "
              "the thing it claims to report.")
    return out


def workflow_problems(spec: dict) -> list[str]:
    """RULE 3 — the `tick_workflow` an entry names must be a workflow that ships."""
    wf = spec.get("tick_workflow")
    if not wf:
        return [f"{spec['key']} declares no tick_workflow — `supervision_for` has nothing to ask the Actions "
                f"API about, so the lane's supervision verdict is unreachable."]
    if not (WORKFLOWS / wf).exists():
        return [f"{spec['key']}.tick_workflow = {wf!r} — no such file in .github/workflows/. "
                f"`supervision_for` fetches this workflow's runs to decide whether anything is visiting the "
                f"lane; against a name that does not exist it can only ever report NO-TICKS or an API error, "
                f"which is an alarm about the registry wearing the label of an alarm about the lane."]
    return []


def input_problems(spec: dict) -> list[str]:
    """RULE 2b — a declarative INPUT must at least be known to the machinery that consumes it.

    Not a producer requirement, deliberately: `ternary-watch.json` is a hand-maintained watch list and no
    code in this repo writes it. What would be wrong is for it to be an ORPHAN — a filename the registry
    invented that nothing reads, validates or acts on.
    """
    out = []
    for field, rel in _declared(spec):
        if field not in DECLARED_INPUT:
            continue
        if not references(rel):
            out.append(
                f"{spec['key']}.{field} = {rel!r} — named ONLY by this registry. A declarative input nothing "
                f"else reads or validates is a filename with no machinery behind it.")
    return out


LANE_IDS = [s.get("key", f"lane{i}") for i, s in enumerate(lsw.LANES)]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the contract
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.committed_artifact
@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_every_artifact_the_watcher_reads_is_really_in_the_repo(spec):
    # `committed_artifact`: this asserts the state of MUTABLE FILES COMMITTED IN THE REPO, not the behaviour
    # of code (conftest.pytest_configure). It must be LOUD — a missing hold artifact is the incident — but it
    # must not gate a market gate or a collect behind a bookkeeping assertion.
    problems = existence_problems(spec)
    assert not problems, "\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_every_produced_artifact_has_something_that_writes_it(spec):
    problems = producer_problems(spec)
    assert not problems, "\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_every_declared_input_is_read_by_something(spec):
    problems = input_problems(spec)
    assert not problems, "\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_every_tick_workflow_exists(spec):
    problems = workflow_problems(spec)
    assert not problems, "\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_every_entry_names_a_reader_that_is_implemented(spec):
    """A registry is only declarative if every declaration resolves. `gather` raises ValueError on an unknown
    reader — correct, but it raises at RUN time, on the tick, in front of a billing fleet."""
    assert spec.get("reader") in {"step1", "ternary_family", "nrv04_retro", "gcp_watch", "selcal",
                                  "selcal_md"}, (
        f"{spec.get('key')} names reader {spec.get('reader')!r}, which `gather` does not implement — it "
        f"would raise ValueError mid-tick.")
    for required in ("key", "label", "provider", "artifact_source", "tick_workflow"):
        assert spec.get(required), f"{spec.get('key')} is missing {required!r}"


def test_lane_keys_are_unique():
    keys = [s["key"] for s in lsw.LANES]
    assert len(set(keys)) == len(keys), f"duplicate lane keys: {keys}"


@pytest.mark.parametrize("spec", [s for s in lsw.LANES if s.get("reader") == "ternary_family"],
                         ids=[s["key"] for s in lsw.LANES if s.get("reader") == "ternary_family"])
def test_a_ternary_lane_always_declares_a_terminus(spec):
    """MEASURED, not assumed (controlled reproduction, 2026-08-01): a `ternary_family` entry with
    `terminal_artifact` unset grades UNKNOWN on every run, forever.

        terminal_artifact='valb-replicate-reduction.json' -> ADVANCING, ok=True
        terminal_artifact=None                           -> UNKNOWN,   ok=False,
                                                            unreadable={'finished': 'could not determine
                                                            whether None exists'}

    `gather` computes `present = os.path.exists(...) if term else None`, and `read_ternary_family` reads that
    None as "the caller could not check" — which is `unreadable['finished']`, and `finished` is in `CRITICAL`.
    An alarm that is always red is the same end state as no alarm, so this is pinned: dropping the key to
    silence a stale terminus would silence the lane instead.
    """
    assert isinstance(spec.get("terminal_artifact"), str) and spec["terminal_artifact"], (
        f"{spec['key']} uses the ternary_family reader with no terminal_artifact — it would be graded "
        f"UNKNOWN on every run. If the lane genuinely has no committed terminus, that is a change to "
        f"read_ternary_family's tri-state, not a None here.")


@pytest.mark.parametrize("spec", lsw.LANES, ids=LANE_IDS)
def test_the_unbacked_marker_can_only_ever_excuse_a_terminus(spec):
    """(a) and (b) of the marker's four constraints. The incident's own fields must stay unsilenceable: if
    `hold_artifact` could carry an excuse, this whole test file would be a formality."""
    reason = spec.get(TERMINAL_UNBACKED_KEY)
    if reason is None:
        return
    assert isinstance(spec.get("terminal_artifact"), str) and spec["terminal_artifact"], (
        f"{spec['key']} sets {TERMINAL_UNBACKED_KEY} with no terminal_artifact to excuse.")
    assert isinstance(reason, str) and len(reason) >= 80, (
        f"{spec['key']}.{TERMINAL_UNBACKED_KEY} must state WHY nothing writes it and what would close the "
        f"gap; got {reason!r}.")
    forbidden = [f for f in PRODUCED_EVERY_TICK + DECLARED_INPUT if f in reason.split()]
    assert not forbidden, f"{spec['key']}: the marker is scoped to a terminus only, not {forbidden}"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# NEGATIVE CONTROLS — a guard nobody has watched fail is not known to work (TESTING.md rule 7)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# These break each property deliberately and assert the checker goes red WITH A MESSAGE NAMING THE PROPERTY.
# Run once by hand and then discarded, a negative control proves nothing tomorrow — so it lives here, where
# a refactor that quietly makes a rule vacuous fails immediately.
_REAL = next(s for s in lsw.LANES if s["key"] == "step1-fanout")


def test_NEGATIVE_CONTROL_a_hold_artifact_that_does_not_exist_is_caught():
    broken = dict(_REAL, key="synthetic", hold_artifact="step1-fanout-market-hold-THAT-NEVER-LANDED.json")
    problems = existence_problems(broken)
    assert len(problems) == 1, problems
    assert "hold_artifact" in problems[0] and "NOT IN THE REPO" in problems[0]
    # and the real entry it was cloned from is still clean, so the control is testing the rule, not the tree
    assert existence_problems(_REAL) == []


def test_NEGATIVE_CONTROL_an_artifact_nothing_writes_is_caught():
    broken = dict(_REAL, key="synthetic", generation_artifact="a-name-no-code-path-in-this-repo-emits.json")
    problems = producer_problems(broken)
    assert len(problems) == 1, problems
    assert "NOTHING IN THE REPO PRODUCES IT" in problems[0]
    assert "exactly ONE site" in problems[0]


def test_NEGATIVE_CONTROL_a_name_that_is_only_MENTIONED_is_not_a_producer():
    """The sharper half of rule 2, and the one the incident actually turned on: `RETRO_MARKET_READOUT` named
    the missing file in prose and in a docstring the entire time it did not exist. A mention must not vouch.
    """
    # `TESTING.md` is cited by name in a dozen module docstrings — real, non-comment lines — and no script
    # or workflow writes it. Exactly the shape the incident wore: talked about everywhere, produced nowhere.
    talked_about = "TESTING.md"
    refs = references(talked_about)
    assert refs, f"precondition: the corpus mentions {talked_about} outside comments"
    assert not producer_sites(talked_about), (
        f"precondition: {talked_about} has no producer; got {producer_sites(talked_about)[:2]}")
    mentioned = dict(_REAL, key="synthetic", terminal_artifact=talked_about)
    problems = producer_problems(mentioned)
    assert problems, "a name the repo merely TALKS ABOUT was accepted as produced — rule 2 is vacuous"
    assert "none of them is a producing position" in problems[0], problems


def test_NEGATIVE_CONTROL_a_tick_workflow_that_does_not_exist_is_caught():
    broken = dict(_REAL, key="synthetic", tick_workflow="step1-fanout-autoscale-RENAMED.yml")
    problems = workflow_problems(broken)
    assert len(problems) == 1 and "no such file in .github/workflows/" in problems[0], problems
    assert workflow_problems(_REAL) == []


def test_NEGATIVE_CONTROL_the_marker_cannot_excuse_the_incidents_own_field():
    broken = dict(_REAL, key="synthetic",
                  hold_artifact="a-hold-artifact-that-was-never-committed.json",
                  **{TERMINAL_UNBACKED_KEY: "x" * 100})
    assert existence_problems(broken), (
        "the unbacked marker silenced a missing HOLD ARTIFACT — that is the 2026-07-31 incident itself, and "
        "it must be unsilenceable")


def test_NEGATIVE_CONTROL_the_corpus_actually_sees_the_workflows_and_the_scripts():
    """A scan that silently reads nothing would make every rule above pass vacuously — the exact shape of the
    2026-07-26 collection abort, where a green build had run no tests at all."""
    files = {f for f, _, _, _ in _corpus()}
    assert any(f.endswith(".yml") and "workflows" in f for f in files), "no workflows in the corpus"
    assert any(f.endswith(".py") and "modalities" in f for f in files), "no modalities scripts in the corpus"
    assert not any(f"{os.sep}tests{os.sep}" in f or f.endswith(REGISTRY_MODULE) for f in files), (
        "the corpus includes the registry or the tests — a declaration would be able to vouch for itself")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the SECOND lane registry, checked for the same class
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# `inflight_board.LANES` is a different registry with the same failure mode: each entry declares the PRODUCER
# that publishes that lane's board fragment (`gcp_fanout_rep.py board`, `ternary_vast_launch.py task=collect`,
# ...). The board renders from the registry rather than from the fragments on disk — deliberately, so a lane
# that has never published still shows up — which means a producer that does not exist would render as a lane
# quietly awaiting its first fragment. Fragment ABSENCE is already loud there ("no fragment at ... — this lane
# has never published one"), so only the producer claim is unverified, and only that is asserted here.
def _inflight_lanes():
    try:
        import inflight_board
    except Exception:  # pragma: no cover - optional dependency at import time
        pytest.skip("inflight_board not importable in this environment")
    return list(getattr(inflight_board, "LANES", ()))


def test_every_inflight_board_lane_names_a_producer_module_that_exists():
    missing = []
    for entry in _inflight_lanes():
        key, producer = entry[0], (entry[2] if len(entry) > 2 else "")
        script = str(producer).split()[0] if producer else ""
        if not script.endswith(".py"):
            continue
        if not (MODALITIES / script).exists():
            missing.append(f"{key} -> {producer!r}: research/modalities/{script} does not exist")
    assert not missing, ("in-flight board lanes whose declared producer is not a real module:\n  "
                         + "\n  ".join(missing))
