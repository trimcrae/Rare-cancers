#!/usr/bin/env python3
"""The scratchpad collision guard, asserted rather than agreed (AUT-PD-055).

⛔⛔ THE DEFECT THIS PINS, MEASURED TWICE INDEPENDENTLY ON 2026-08-28. The scratchpad root is shared
by every concurrent seat. One seat's `scratchpad/mutate.py` was overwritten by a sibling's; the next
run executed the sibling's file and reported `4 caught / 4` **against a module in another worktree**,
in a log that read exactly like a clean run of its own. Nothing failed. Nothing was empty. The
result was fabricated in substance and finished in appearance — CLAUDE.md §4's "a plausible-looking
record is more dangerous than an empty one", with a mutation verdict attached.

⛔ THE PRIOR FIX (AUT-PD-027, `research-loop` §3) SAID **LOGS**, AND THE FILE THAT COLLIDED WAS A
**SCRIPT** — and it was prose, measured by nothing. This suite is the measuring half.

★ BOTH DIRECTIONS ARE ASSERTED THROUGHOUT. `paper-hardening` §8b.1: a gate that reds on true input
is worse than one that greens on false input, because the first thing anyone does is loosen it — and
over-anchoring makes a check vacuous, which is the same failure wearing the other costume. This
suite's own subject already paid that toll once: the first prefix rule demanded a file carry its
directory's WHOLE name, which called the compliant `s55-scratchpad/s55-blast-radius.log` a violation
on the tool's first live run.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import seat_scratch as S  # noqa: E402


def _kinds(findings):
    return sorted({k for k, _, _ in findings})


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE COLLISION SURFACE — the file `mutate.py` actually was.
# ---------------------------------------------------------------------------------------------

def test_a_generic_file_at_the_shared_root_is_reported_as_unowned(tmp_path):
    """⛔ THE REGRESSION, REBUILT. `mutate.py` at the root is a path every writer may take."""
    (tmp_path / "s55-seat").mkdir()
    (tmp_path / "mutate.py").write_text("print('hi')\n")
    findings = S.audit_root(str(tmp_path))
    assert _kinds(findings) == ["UNOWNED"], findings
    assert findings[0][1].endswith("mutate.py")


def test_a_root_that_holds_only_writer_directories_is_clean(tmp_path):
    """★ THE OTHER DIRECTION. The convention, followed, must not fire — or it gets loosened."""
    (tmp_path / "s55-seat").mkdir()
    (tmp_path / "s55-seat" / "s55-run.log").write_text("x\n")
    (tmp_path / "s33-other").mkdir()
    (tmp_path / "s33-other" / "s33-other-run.log").write_text("x\n")
    assert S.audit_root(str(tmp_path)) == []


def test_the_prefix_rule_accepts_the_owner_token_not_only_the_whole_directory_name(tmp_path):
    """⚠ THE FALSE POSITIVE THIS TOOL SHIPPED WITH FOR ONE RUN, pinned so it cannot come back.

    The seat prompt asks for filenames prefixed with the seat ID (`s55-`), inside a directory named
    for the seat (`s55-scratchpad/`). Demanding the full directory name reds on that.
    """
    (tmp_path / "s55-scratchpad").mkdir()
    (tmp_path / "s55-scratchpad" / "s55-blast-radius.log").write_text("x\n")
    assert S.audit_root(str(tmp_path)) == []


def test_a_file_carrying_no_owner_token_at_all_is_still_reported(tmp_path):
    """⛔ AND LOOSENING IT TO THE OWNER TOKEN MUST NOT MAKE IT VACUOUS."""
    (tmp_path / "s55-scratchpad").mkdir()
    (tmp_path / "s55-scratchpad" / "preflight.log").write_text("x\n")
    findings = S.audit_root(str(tmp_path))
    assert _kinds(findings) == ["UNPREFIXED"], findings


def test_a_missing_root_is_reported_rather_than_passing_silently(tmp_path):
    """⛔ CLAUDE.md §4: an absent reading is not a reading of absence."""
    findings = S.audit_root(str(tmp_path / "does-not-exist"))
    assert _kinds(findings) == ["MISSING"], findings


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE PROVENANCE HALF — the fabricated verdict itself.
# ---------------------------------------------------------------------------------------------

def _log(dirpath, name, seat, worktree, body):
    d = dirpath / seat
    d.mkdir(exist_ok=True)
    p = d / name
    p.write_text(S.stamp(seat, worktree) + body)
    return str(p)


def test_a_log_naming_a_sibling_worktree_is_reported_foreign(tmp_path):
    """⛔⛔ THE MEASURED INCIDENT. Stamped for sA, but the run it records touched sB's module."""
    p = _log(tmp_path, "sA-mutate.log", "sA", "/home/user/wt/sA",
             "4 caught / 4 against /home/user/wt/sB/research/manuscripts/lint_claims.py\nEXIT=0\n")
    findings = S.verify_log(p, parent="/home/user/wt")
    assert _kinds(findings) == ["FOREIGN"], findings
    assert "/home/user/wt/sB/research/manuscripts/lint_claims.py" in findings[0][2]


def test_the_same_log_pointing_at_its_own_worktree_is_clean(tmp_path):
    """★ THE CONTROL. Identical shape, own tree — this is the run we must not cry wolf on."""
    p = _log(tmp_path, "sA-mutate.log", "sA", "/home/user/wt/sA",
             "4 caught / 4 against /home/user/wt/sA/research/manuscripts/lint_claims.py\nEXIT=0\n")
    assert S.verify_log(p, parent="/home/user/wt") == []


def test_an_unstamped_log_is_unstamped_and_never_ok(tmp_path):
    """⛔ THE GRADING ERROR THAT WOULD UNDO THE WHOLE TOOL: reading a missing stamp as a pass."""
    d = tmp_path / "sA"
    d.mkdir()
    p = d / "sA-mutate.log"
    p.write_text("4 caught / 4\nEXIT=0\n")
    findings = S.verify_log(str(p), parent="/home/user/wt")
    assert _kinds(findings) == ["UNSTAMPED"], findings


def test_a_half_stamped_log_is_unstamped(tmp_path):
    """⛔ ONE FIELD IS NOT THE STAMP — a SEAT with no WORKTREE binds the log to nothing checkable."""
    d = tmp_path / "sA"
    d.mkdir()
    p = d / "sA-mutate.log"
    p.write_text("SEAT=sA\n4 caught / 4\nEXIT=0\n")
    assert _kinds(S.verify_log(str(p), parent="/home/user/wt")) == ["UNSTAMPED"]


def test_a_log_filed_under_a_seat_it_was_not_stamped_for_is_misattributed(tmp_path):
    """⛔ A LOG COPIED INTO ANOTHER SEAT'S DIRECTORY still carries its real owner — say so."""
    d = tmp_path / "sB"
    d.mkdir()
    p = d / "sB-mutate.log"
    p.write_text(S.stamp("sA", "/home/user/wt/sA") + "EXIT=0\n")
    assert _kinds(S.verify_log(str(p), parent="/home/user/wt")) == ["MISATTRIBUTED"]


def test_an_explicit_expected_seat_overrides_the_directory(tmp_path):
    """★ THE DRIVER CHECKING A LOG IT HAS MOVED must be able to say who it expects."""
    d = tmp_path / "anywhere"
    d.mkdir()
    p = d / "x.log"
    p.write_text(S.stamp("sA", "/home/user/wt/sA") + "EXIT=0\n")
    assert S.verify_log(str(p), parent="/home/user/wt", expect_seat="sA") == []
    assert _kinds(S.verify_log(str(p), parent="/home/user/wt", expect_seat="sB")) == ["MISATTRIBUTED"]


def test_the_worktree_itself_is_not_foreign_to_itself(tmp_path):
    """⚠ THE OFF-BY-ONE THAT WOULD MAKE EVERY CLEAN LOG RED: the tree root as a bare path."""
    p = _log(tmp_path, "sA-run.log", "sA", "/home/user/wt/sA",
             "cd /home/user/wt/sA && ./scripts/preflight.sh\nEXIT=0\n")
    assert S.verify_log(p, parent="/home/user/wt") == []


def test_a_prefix_neighbour_worktree_is_foreign(tmp_path):
    """⛔ `/home/user/wt/sA2` STARTS WITH `/home/user/wt/sA` and is a different tree.

    A naive `startswith` on the unterminated path calls it own. It is not.
    """
    p = _log(tmp_path, "sA-run.log", "sA", "/home/user/wt/sA",
             "read /home/user/wt/sA2/research/x.py\nEXIT=0\n")
    assert _kinds(S.verify_log(p, parent="/home/user/wt")) == ["FOREIGN"], p


def test_a_missing_log_is_reported_rather_than_passing(tmp_path):
    assert _kinds(S.verify_log(str(tmp_path / "nope.log"))) == ["MISSING"]


# ---------------------------------------------------------------------------------------------
# ★ THE HONESTY CLAUSE. The header must keep saying what the tool cannot see, because a reader who
#   believes a green audit proves the result is the seat's own has been misled by this file.
# ---------------------------------------------------------------------------------------------

def test_the_tool_documents_what_it_does_not_catch():
    """⛔ A guard whose limits are undocumented gets read as a proof. Ours names four gaps."""
    src = open(os.path.join(os.path.dirname(HERE), "seat_scratch.py"), encoding="utf-8").read()
    assert "WHAT THIS DOES NOT CATCH" in src
    for gap in ("RELATIVE", "OUTSIDE the audited root", "AFTER-THE-FACT"):
        assert gap in src, gap
