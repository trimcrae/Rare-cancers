"""`scripts/fast_checks.py` must keep "the fast six" reproducible, and must keep the number honest.

⛔ THE DEFECT THIS CLOSES (roadmap §10.1a `Q21`). *"The fast six"* was quoted as a verification line in
`three-row-audit-2026-08-03.md` (`| the fast six | 6/6 PASS |`) with no definition anywhere in the repo,
and `r3-site-choice-audit-2026-08-03.md` said so two days later and asked for the $0 fix. A verification
line nobody can reproduce is not a verification line.

⚠ THE RISK IN FIXING IT IS THE NAME. A set called "six" that quietly grows to seven is worse than an
undefined phrase, because it reads as reproducible while meaning something new. So the count is asserted
against `EXPECTED_N` and the name is asserted against the count -- both must move in the same commit.

⚠ THIS TEST DOES NOT RUN THE SIX. Each of them is already its own CI step and (for four of the six) a
preflight gate; running them again here would make one test fail for six unrelated reasons and get
skipped. What it asserts is that the DEFINITION is well formed, executable, and honest about what it
cannot reconstruct.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT = os.path.join(ROOT, "scripts", "fast_checks.py")

_spec = importlib.util.spec_from_file_location("fast_checks", SCRIPT)
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)


def test_the_set_called_six_has_six_members():
    assert len(fc.MEMBERS) == fc.EXPECTED_N == 6, (
        "the phrase is 'the fast six'. If the membership rule now admits a different number, rename the "
        "set and update every quoting document in the SAME commit -- a 'six' with seven members is a "
        "verification line that has silently changed meaning: %d members, EXPECTED_N=%d"
        % (len(fc.MEMBERS), fc.EXPECTED_N))


def test_every_member_names_a_command_that_exists():
    """A member pointing at a deleted script would make `6/6 PASS` unreachable and the failure obscure."""
    for name, cmd, why in fc.MEMBERS:
        assert cmd[0] == "python3", (name, cmd)
        target = os.path.join(ROOT, cmd[1])
        assert os.path.exists(target), "%s names %s, which does not exist" % (name, cmd[1])
        assert why.strip(), "%s carries no statement of what it guards" % name


def test_member_names_and_commands_are_unique():
    names = [m[0] for m in fc.MEMBERS]
    cmds = [" ".join(m[1]) for m in fc.MEMBERS]
    assert len(set(names)) == len(names), names
    assert len(set(cmds)) == len(cmds), cmds


def test_every_exclusion_states_the_clause_it_fails():
    """⛔ AN UNSTATED EXCLUSION IS HOW A COUNT DRIFTS. Six has to be a consequence of the rule."""
    assert fc.EXCLUDED, "the exclusions were emptied; six then becomes a number somebody liked"
    for path, why in fc.EXCLUDED:
        assert any(c in why for c in ("(a)", "(b)", "(c)", "(d)")), (
            "%s is excluded without naming which clause of the membership rule it fails: %r" % (path, why))


def test_the_two_checks_preflight_does_not_run_are_members():
    """⭐ THE REASON THE SET IS NOT AN ALIAS FOR preflight.sh. CLAUDE.md §7: `lint_claims.py` is NOT in
    preflight, so a green preflight does not mean the language rules passed. `line_citations.py` is the
    same shape. If either ever leaves this set, the gap CLAUDE.md warns about reopens silently."""
    cmds = " ".join(" ".join(m[1]) for m in fc.MEMBERS)
    assert "lint_claims.py" in cmds
    assert "line_citations.py" in cmds
    preflight = open(os.path.join(ROOT, "scripts", "preflight.sh"), encoding="utf-8").read()
    # If preflight ever DOES gain them, that is good news -- but this set's stated reason for existing
    # would then be wrong, so it must be rewritten rather than left standing.
    if "lint_claims.py" in preflight and "line_citations.py" in preflight:
        raise AssertionError(
            "preflight now runs lint_claims and line_citations, so fast_checks.py's stated reason for "
            "existing ('the set that closes the gap preflight leaves') is out of date -- rewrite the "
            "header rather than deleting the check")


def test_pytest_is_not_a_member():
    """(b): ~10 min and it needs numpy/rdkit/boto3. Folding it in would make 'fast' false and would make
    the set unusable in this sandbox, which is exactly where a doc author works."""
    cmds = " ".join(" ".join(m[1]) for m in fc.MEMBERS)
    assert "pytest" not in cmds


def test_the_unreconstructable_original_is_recorded_and_not_claimed():
    """⚠ THE ASSERTION WITH THE MOST AT STAKE. `preflight.sh` did not have six gates on 2026-08-03 -- its
    own comments date `systems_check` to 2026-08-05 and `emc_systems_map_check` to 2026-08-06 -- so the
    original `6/6 PASS` was a pass of some other set. Silently letting this definition inherit that line
    would manufacture a verification that never happened."""
    src = open(SCRIPT, encoding="utf-8").read()
    assert "2026-08-03" in src, "the origin of the phrase is not recorded"
    assert "not recoverable" in src or "cannot be reproduced" in src, (
        "the header must state that the original referent cannot be reconstructed")
    # And preflight's own comments must still support that reading; if they stop, this claim needs redoing.
    preflight = open(os.path.join(ROOT, "scripts", "preflight.sh"), encoding="utf-8").read()
    assert "2026-08-05" in preflight and "2026-08-06" in preflight, (
        "preflight.sh no longer dates its gate additions, so the dating argument in fast_checks.py's "
        "header rests on nothing -- re-derive it before trusting it")


def test_both_quoting_documents_point_at_the_definition():
    """The whole deliverable is that a reader hitting the phrase can find out what it means."""
    for rel in ("research/manuscripts/three-row-audit-2026-08-03.md",
                "research/manuscripts/r3-site-choice-audit-2026-08-03.md"):
        body = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert "fast six" in body, rel
        assert "fast_checks.py" in body, (
            "%s quotes 'the fast six' without pointing at scripts/fast_checks.py, which is the only "
            "place it is defined" % rel)


def test_the_list_mode_runs_and_prints_the_members():
    r = subprocess.run([sys.executable, SCRIPT, "--list"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    for name, _cmd, _why in fc.MEMBERS:
        assert name in r.stdout, name
    assert "EXCLUDED" in r.stdout
