#!/usr/bin/env python3
"""A paper-scoped publication run must never be recordable as clause 2's evidence.

⛔⛔ WHAT THIS PROTECTS. `PREFLIGHT_FULL=1` is the one gate between this repository and an outside
reader, and `publish_bar` clause 2 accepts nothing else. On 2026-09-02 a PAPER-SCOPED variant was
added — `PREFLIGHT_PAPER=PUB-ASO PREFLIGHT_FULL=1` — because the modalities suite was 423.6 s of a
583 s gate, 72 %, and `affected_tests.select()` for a change to the ASO article returns 0 of 429
modality test files while only 39 name an artifact that paper deposits.

★ THAT VARIANT IS FOR ITERATING, NOT FOR PUBLISHING, AND THE DIFFERENCE MUST BE MECHANICAL RATHER
THAN REMEMBERED. `record_bar_evidence.record_preflight` refuses any log lacking the exact banner
`== pytest (modalities: FULL, PREFLIGHT_FULL=1) ==`, and the scoped branch prints a DIFFERENT line —
so a scoped run cannot produce a receipt. Today that holds by the accident of one `)` versus one
`--`. This file turns the accident into a requirement: reword either line so they collide, and this
goes red before the collision can clear a publication.

⚠ AND THE FAILURE WOULD BE SILENT. A scoped run is green, fast and says "FULL" in its heading; a
receipt minted from one would assert that 8,212 modality tests passed when 727 ran, and the only
reader who could tell is one who re-read the log.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
PREFLIGHT = os.path.join(REPO, "scripts", "preflight.sh")


def _recorder():
    spec = importlib.util.spec_from_file_location(
        "record_bar_evidence", os.path.join(AUTONOMY, "record_bar_evidence.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _banner_lines():
    """Every heading preflight.sh can print for the modalities stage, as literal text."""
    src = open(PREFLIGHT, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'echo "(== pytest \(modalities:[^"]*)"', src):
        out.append(m.group(1))
    return out


def test_the_recorder_and_the_gate_still_agree_on_one_exact_banner():
    """The unscoped publication heading must be printable verbatim by the gate and demanded
    verbatim by the recorder. If either side rewords it, clause 2 becomes unreachable — which is
    exactly what happened to `PINNED_SHA=` and went unnoticed because a green FULL run is rare."""
    banner = _recorder().FULL_BANNER
    lines = _banner_lines()
    assert lines, "no modalities heading found in preflight.sh — the parser above has drifted"
    exact = [ln for ln in lines if banner in ln]
    assert len(exact) == 1, (
        "the recorder demands %r and preflight.sh prints %d heading(s) containing it: %r. Exactly "
        "one heading may satisfy it — none makes clause 2 unreachable, and more than one lets a "
        "narrower run mint a receipt." % (banner, len(exact), exact))


def test_no_scoped_heading_can_satisfy_the_recorder():
    """⛔ THE ONE THAT MATTERS. Every heading for a run that did NOT execute the whole modalities
    suite must fail the recorder's check."""
    banner = _recorder().FULL_BANNER
    for line in _banner_lines():
        narrowed = ("scoped" in line or "affected by this change" in line
                    or "none --" in line or "could not be scoped" in line
                    or "selector" in line)
        if narrowed:
            assert banner not in line, (
                "the heading %r describes a run that did not execute the full modalities suite and "
                "yet contains the recorder's banner verbatim, so a receipt minted from it would "
                "assert 8,212 tests passed when far fewer ran" % line)


def test_the_scoped_tier_is_opt_in_and_a_bare_full_run_is_unchanged():
    """⚠ NOTHING THAT ALREADY RELIES ON `PREFLIGHT_FULL=1` MAY BE NARROWED UNDERNEATH IT. The
    scoped branch fires only when PREFLIGHT_PAPER is also set and non-empty."""
    src = open(PREFLIGHT, encoding="utf-8").read()
    assert '[ "${PREFLIGHT_FULL:-0}" = "1" ] && [ -n "${PREFLIGHT_PAPER:-}" ]' in src, (
        "the paper-scoped branch is no longer gated on PREFLIGHT_PAPER being set, so a bare "
        "PREFLIGHT_FULL=1 could now run a narrowed modalities suite while calling itself FULL")


def test_the_scoper_fails_to_full_for_a_paper_it_cannot_scope():
    """⛔ A SCOPE THAT CANNOT BE DERIVED IS NOT A SMALL SCOPE. An unknown paper, a missing manifest
    or a manifest naming no modality file must all answer FULL."""
    r = subprocess.run(
        ["python3", os.path.join(REPO, "research", "manuscripts", "paper_scoped_tests.py"),
         "--paper", "PUB-DOES-NOT-EXIST"],
        capture_output=True, text=True, cwd=REPO, timeout=120)
    assert r.returncode == 0 and r.stdout.strip() == "FULL", (
        "an unscopeable paper answered %r instead of FULL" % r.stdout.strip()[:200])


def test_the_scope_is_derived_from_the_deposit_and_is_a_real_narrowing():
    """Both halves matter: derived (so a new deposited file pulls its guards in with nobody
    remembering) and genuinely narrower (or the tier buys nothing and should be deleted)."""
    scoper = os.path.join(REPO, "research", "manuscripts", "paper_scoped_tests.py")
    r = subprocess.run(["python3", scoper, "--paper", "PUB-ASO"],
                       capture_output=True, text=True, cwd=REPO, timeout=200)
    assert r.returncode == 0
    selected = [ln for ln in r.stdout.split("\n") if ln.strip()]
    if selected == ["FULL"]:
        pytest.fail("PUB-ASO can no longer be scoped — its archive manifest names no "
                    "research/modalities/ file, so the tier has silently stopped narrowing")
    total = len([f for f in os.listdir(os.path.join(REPO, "research", "modalities", "tests"))
                 if f.startswith("test_") and f.endswith(".py")])
    assert 0 < len(selected) < total / 2, (
        "the scope is %d of %d modality modules; under half is what makes this worth its risk, and "
        "a scope approaching the whole suite means the manifest or the match rule has widened"
        % (len(selected), total))
    # ⛔ DERIVED, DRIVEN RATHER THAN ASSERTED: every selected module must name a file the paper's
    # own manifest deposits. A hand-kept list would pass a "the constant exists" check and fail
    # this one the moment it drifted from the deposit.
    import importlib.util
    spec = importlib.util.spec_from_file_location("paper_scoped_tests", scoper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    deposited = mod.deposited_modality_files("PUB-ASO")
    assert deposited, "the manifest yielded no research/modalities/ file to scope on"
    for rel in selected:
        body = open(os.path.join(REPO, rel), encoding="utf-8", errors="replace").read()
        assert any(name in body for name in deposited), (
            "%s is in the scope but names no file PUB-ASO deposits, so the scope is not derived "
            "from the manifest it claims to read" % rel)
