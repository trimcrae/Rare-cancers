"""`os.environ.get(X, default)` collapses three situations into two — AUT-PROP-034 (c).

⛔⛔ THE COLLAPSE, AND THE ONE ROW EVERYBODY GETS WRONG.
`sd_watchdog_enabled()` returns three values — armed, not-armed, and a negative errno for *error*.
`os.environ.get(VAR, default)` returns two, and the row it loses is the one that matters:

    UNSET                      -> the default.        Correct.
    SET and usable             -> that value.         Correct.
    SET TO SOMETHING UNUSABLE  -> ⛔ THAT UNUSABLE VALUE, NOT THE DEFAULT.

An exported-but-empty variable is the everyday form of the third row — `X= cmd`, a `${MISSING}` that
expanded to nothing, a CI `env:` whose secret was unavailable — and `os.environ.get("X", "d")`
returns `""` for it, never `"d"`. Python does not treat an empty export as an absent variable.

★★ WHY THAT IS SPECIFICALLY DANGEROUS IN `research/autonomy/`. Both callers here are built so that
"no runs found" is a legitimate MEASUREMENT: `gates_verdict.py` writes no file and leaves
`health.py`'s `gates_green` row `unmeasured`; `await_ci.py` waits out its deadline and reports
UNKNOWN. Those are the right answers when the API genuinely has nothing, and they are indistinguishable
from what you get by asking the wrong server. CLAUDE.md §4 records the outcome that class of bug has
already produced here: *env-echoed defaults once carried a fabricated verdict all the way out.*

⚠ WHAT IS DELIBERATELY NOT GUARDED HERE. Around 1,840 `os.environ.get` calls exist outside this
directory, almost all of them job-shaped knobs on rented GPU hosts (`NS`, `N_REP`, `RUN_TAG`,
`CHECKPOINT_EVERY`). They configure a computation whose failure is loud and local; they do not decide
which server a verdict is read from. Converting them would be churn, and the item that asked for this
work said so.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

AUTONOMY = pathlib.Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"autonomy_{name}", AUTONOMY / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def env():
    return _load("envread")


# ════════════════════════════════════════════════════════════════════════ the three values, apart ══
def test_unset_is_the_default_and_says_it_is_a_reading(env, monkeypatch):
    monkeypatch.delenv("EMC_TEST_VAR", raising=False)
    r = env.read("EMC_TEST_VAR", default="fallback")
    assert (r.status, r.value, r.usable, r.defaulted) == (env.DEFAULTED, "fallback", True, True)
    assert "unset" in r.detail


def test_set_and_usable_is_the_value(env, monkeypatch):
    monkeypatch.setenv("EMC_TEST_VAR", "  owner/name  ")
    r = env.read("EMC_TEST_VAR", default="fallback", validate=env.repo_slug)
    assert (r.status, r.value, r.usable) == (env.SET, "owner/name", True)


def test_exported_and_empty_is_the_third_state_and_never_silently_the_default(env, monkeypatch):
    """⛔ THE WHOLE POINT. `os.environ.get("X", "fallback")` returns `""` here — not the fallback —
    so the caller proceeds with an empty repo slug. This read refuses instead."""
    monkeypatch.setenv("EMC_TEST_VAR", "")
    r = env.read("EMC_TEST_VAR", default="fallback")
    assert r.status == env.UNREADABLE
    assert r.value is None, "the unusable read handed back a value, which is the collapse restored"
    assert r.usable is False
    import os
    assert os.environ.get("EMC_TEST_VAR", "fallback") == "", (
        "the premise of this whole module has changed — Python now returns the default for an "
        "exported-empty variable, and every comment here needs rewriting"
    )


def test_whitespace_only_is_also_unreadable(env, monkeypatch):
    monkeypatch.setenv("EMC_TEST_VAR", "   \t ")
    assert env.read("EMC_TEST_VAR", default="fallback").status == env.UNREADABLE


def test_a_validator_failure_fails_closed_rather_than_defaulting(env, monkeypatch):
    """An explicit setting we cannot honour is not the same as no setting at all. Substituting the
    default would silently do something other than what somebody asked for."""
    monkeypatch.setenv("EMC_TEST_VAR", "not-a-slug")
    r = env.read("EMC_TEST_VAR", default="trimcrae/Rare-cancers", validate=env.repo_slug)
    assert r.status == env.UNREADABLE and r.value is None
    assert "not `owner/name`" in r.detail


def test_a_secret_is_never_echoed(env, monkeypatch):
    """These details are printed into $GITHUB_STEP_SUMMARY."""
    monkeypatch.setenv("EMC_TEST_TOKEN", "ghp_supersecretvalue")
    ok = env.read("EMC_TEST_TOKEN", secret=True)
    monkeypatch.setenv("EMC_TEST_TOKEN", "has space")
    bad = env.read("EMC_TEST_TOKEN", secret=True, validate=env.opaque_token)
    for r in (ok, bad):
        assert "supersecret" not in r.detail and "has space" not in r.detail
    assert "20 character(s)" in ok.detail


def test_the_status_and_the_usable_flag_can_never_disagree(env, monkeypatch):
    """`usable` is derived, not stored — one fact, one place, and the `_row` assertion in `health.py`
    exists for the identical reason."""
    for value, expect in (("owner/name", True), ("", False)):
        monkeypatch.setenv("EMC_TEST_VAR", value)
        r = env.read("EMC_TEST_VAR", default="d", validate=env.repo_slug)
        assert r.usable is expect and (r.status == env.UNREADABLE) is (not expect)


# ══════════════════════════════════════════════════════════════════════════════════════ validators ══
@pytest.mark.parametrize("bad", ["noslash", "/name", "owner/", "a/b/c", "own er/name", ""])
def test_repo_slug_rejects_what_would_build_a_url_nobody_meant(env, bad):
    assert env.repo_slug(bad), f"{bad!r} passed as a repository slug"


def test_repo_slug_accepts_the_shapes_github_actually_uses(env):
    for good in ("trimcrae/Rare-cancers", "org-name/repo.name", "a/b", "A_b/c-d.e"):
        assert env.repo_slug(good) is None, good


def test_first_set_stops_at_a_broken_alias_rather_than_stepping_over_it(env, monkeypatch):
    """⛔ `A or B` SKIPS AN EMPTY A AND QUIETLY USES B. That hides a fact somebody needs: A was set,
    to something broken. An alias that is merely UNSET is skipped, which is what an alias is for."""
    monkeypatch.setenv("EMC_A", "")
    monkeypatch.setenv("EMC_B", "usable")
    broken = env.first_set(("EMC_A", "EMC_B"))
    assert broken.status == env.UNREADABLE and broken.name == "EMC_A"

    monkeypatch.delenv("EMC_A")
    assert env.first_set(("EMC_A", "EMC_B")).value == "usable"

    monkeypatch.delenv("EMC_B")
    none_set = env.first_set(("EMC_A", "EMC_B"))
    assert none_set.status == env.DEFAULTED and none_set.value is None


# ══════════════════════════════════════════════════════════ the call sites that gate a decision ══
def test_gates_verdict_refuses_rather_than_reading_the_wrong_repository(monkeypatch, tmp_path, capsys):
    """⛔ THE FAILURE THIS CLOSES, END TO END. An empty `GITHUB_REPOSITORY` used to build
    `https://api.github.com/repos//actions/...`; whatever came back, the row ended up `unmeasured`
    and looked exactly like the honest unmeasured. Now nothing is written and the reason is printed."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "")
    gv = _load("gates_verdict")

    def _never(*a, **k):
        raise AssertionError("fetch was called with an unreadable GITHUB_REPOSITORY")

    monkeypatch.setattr(gv, "fetch", _never)
    out = tmp_path / "gates.json"
    assert gv.main(["--out", str(out)]) == 0, "the tick's other steps must still run"
    assert not out.exists(), "a verdict was written from an environment that could not be read"
    assert "EXPORTED AND EMPTY" in capsys.readouterr().out


def test_gates_verdict_still_works_unset_and_names_the_default(monkeypatch, tmp_path, capsys):
    """⚠ THE OTHER SIDE. Unset is the sandbox case and must keep working, out loud."""
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    gv = _load("gates_verdict")
    seen = {}

    def _fake(token, per_page=40, repo=None):
        seen["repo"], seen["token"] = repo, token
        return [{"status": "completed", "conclusion": "success", "head_sha": "a" * 40,
                 "updated_at": "2026-08-28T10:00:00Z", "created_at": "2026-08-28T09:00:00Z"}]

    monkeypatch.setattr(gv, "fetch", _fake)
    out = tmp_path / "gates.json"
    assert gv.main(["--out", str(out)]) == 0
    assert seen["repo"] == gv.DEFAULT_REPO and seen["token"] is None
    assert json.loads(out.read_text())["ok"] is True
    assert "is unset" in capsys.readouterr().out


def test_gates_verdict_refuses_an_exported_empty_token(monkeypatch, tmp_path, capsys):
    """An `Authorization: Bearer ` header earns a 401, which this module's error path reports as an
    API problem — burying the real cause, which is a quoting accident in the environment."""
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "")
    gv = _load("gates_verdict")
    monkeypatch.setattr(gv, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("fetched")))
    out = tmp_path / "gates.json"
    assert gv.main(["--out", str(out)]) == 0
    assert not out.exists()
    assert "GITHUB_TOKEN" in capsys.readouterr().out


def test_await_ci_refuses_an_unreadable_repo_with_unknown_never_green(monkeypatch, capsys):
    """⛔ EXIT 2, NOT 0, AND THAT IS THIS FILE'S OWN VOCABULARY: its docstring defines 2 as "the
    deadline passed with runs still going, which is NOT a pass". An environment we cannot read is the
    same class of answer. Exit 0 would report a commit's CI as clean because a variable was empty."""
    monkeypatch.setenv("EMC_CI_REPO", "  ")
    ac = _load("await_ci")
    monkeypatch.setattr(ac, "poll", lambda *a, **k: (_ for _ in ()).throw(AssertionError("polled")))
    assert ac.main(["--sha", "b" * 40]) == 2
    assert "EXPORTED AND EMPTY" in capsys.readouterr().out


def test_await_ci_unset_uses_the_default_and_an_explicit_flag_still_wins(monkeypatch, capsys):
    monkeypatch.delenv("EMC_CI_REPO", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    ac = _load("await_ci")
    seen = {}
    monkeypatch.setattr(ac, "poll", lambda repo, *a, **k: seen.setdefault("repo", repo) and 0 or 0)
    assert ac.main(["--sha", "c" * 40]) == 0
    assert seen["repo"] == ac.DEFAULT_REPO

    seen.clear()
    monkeypatch.setenv("EMC_CI_REPO", "someone/else")
    assert ac.main(["--sha", "c" * 40, "--repo", "explicit/wins"]) == 0
    assert seen["repo"] == "explicit/wins", "an explicit --repo stopped winning over the environment"
    capsys.readouterr()


def test_the_two_pollers_agree_on_which_repository_this_is(monkeypatch):
    """⛔ ONE FACT, ONE PLACE — and they did NOT agree before this item: `await_ci` said
    `trimcrae/rare-cancers` and `gates_verdict` said `trimcrae/Rare-cancers`. The API is
    case-insensitive on the path, so nothing broke, which is precisely why it survived."""
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert _load("await_ci").DEFAULT_REPO == _load("gates_verdict").DEFAULT_REPO


def test_session_cap_reports_the_two_cases_apart_while_deciding_the_same(monkeypatch):
    """⚠ THE READ THAT WAS CHANGED FOR ITS REPORT, NOT ITS DECISION. `verdict()` fails closed either
    way — it always did — but this module's own docstring records an OPEN question ("is
    CLAUDE_CODE_SESSION_ID set inside a scheduled-Routine session?") that a two-valued read cannot
    answer for whoever reads the output next."""
    sc = _load("session_cap")

    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    unset_may, unset_why = sc.verdict()
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
    empty_may, empty_why = sc.verdict()

    assert unset_may is False and empty_may is False, "the fail-closed decision changed"
    assert unset_why != empty_why, (
        "unset and exported-empty still read identically — the open question this read was widened "
        "to answer is still unanswerable from the output"
    )
    assert "unset" in unset_why and "EXPORTED AND EMPTY" in empty_why


def _raw_env_reads(path):
    """Every genuine `os.environ.get` / `os.getenv` / `os.environ[...]` in a file, by AST.

    ⛔ AST, NOT `grep` — AND THE FIRST VERSION OF THIS GUARD WAS THE GREP, WHICH FAILED IMMEDIATELY.
    Both files that were FIXED name the old idiom in the docstring explaining why they no longer use
    it, so a text scan indicted exactly the two modules whose repair it was reading about. A guard
    that fires on the prose describing the fix is worse than none: it teaches the next person that
    the honest comment is the thing to delete. `paper-hardening` records the same finding — a guard
    scraping source shape got two of four wrong and would have had someone "fix" what was never
    broken — and the answer both times is to check the CODE rather than a rendering of it.
    """
    import ast

    def _is_os(node, attr):
        return (isinstance(node, ast.Attribute) and node.attr == attr
                and isinstance(node.value, ast.Name) and node.value.id == "os")

    hits = []
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if _is_os(f, "getenv"):
                hits.append((node.lineno, "os.getenv(...)"))
            elif (isinstance(f, ast.Attribute) and f.attr == "get"
                  and _is_os(f.value, "environ")):
                hits.append((node.lineno, "os.environ.get(...)"))
        elif isinstance(node, ast.Subscript) and _is_os(node.value, "environ"):
            hits.append((node.lineno, "os.environ[...]"))
    return hits


def test_no_two_valued_read_survives_on_a_decision_path():
    """★ THE CLASS, NOT THE INSTANCE (`paper-hardening` §8b.2). A fix bound to two call sites
    regresses at the third. Every environment read on the autonomy loop's own decision paths must go
    through `envread`, so the third state can never be collapsed again by a later edit."""
    offenders = []
    for path in sorted(AUTONOMY.glob("*.py")):
        if path.name == "envread.py":
            continue
        offenders += [f"{path.name}:{line}: {what}" for line, what in _raw_env_reads(path)]
    assert not offenders, (
        "a raw two-valued environment read is back on the autonomy loop's decision paths:\n  "
        + "\n  ".join(offenders)
    )


def test_that_guard_can_actually_see_a_raw_read(tmp_path):
    """⛔ THE GUARD'S OWN GUARD. The assertion above passes trivially if `_raw_env_reads` returns
    nothing for every input — which is exactly what the AST rewrite risks, and exactly the
    unrun-guard shape this repository keeps paying for. Feed it all three idioms and require it to
    find all three, and feed it the prose that broke the grep and require it to find none."""
    live = tmp_path / "live.py"
    live.write_text("import os\n"
                    "a = os.environ.get('X', 'd')\n"
                    "b = os.getenv('Y', 'd')\n"
                    "c = os.environ['Z']\n")
    assert len(_raw_env_reads(live)) == 3

    prose = tmp_path / "prose.py"
    prose.write_text('"""Why this is no longer os.environ.get(X, default) — see envread."""\n'
                     "# os.getenv is the other spelling of the same collapse\n"
                     "value = 1\n")
    assert _raw_env_reads(prose) == [], "the guard indicts comments again"
