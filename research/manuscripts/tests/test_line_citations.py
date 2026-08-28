"""⛔ A LINE-NUMBER CITATION IS A CLAIM, AND IT ROTS SILENTLY.

★ MEASURED 2026-08-06 by a verification read, not by CI. The roadmap cites the manuscript and the SI by
line number — `*"the quoted phrase"* (`:2200–2203`)` — and **every one of the 39 such citations was stale**,
by a systematic +16 to +35 lines into the paper and +15 to +35 into the SI. Not typos: the accumulated drift
of ordinary edits above each cited line.

⚠ NOTHING COULD HAVE CAUGHT IT BEFORE. A wrong line number is a well-formed reference — it points at a real
line, just not the one that says what the sentence claims it says. `check_links` validates that a FILE and
an ANCHOR exist; neither concept reaches inside a file to a line. So the failure mode is a citation that
looks checked, reads as precise, and vouches for a sentence it does not contain.

⭐ THE FIX IS THAT THE QUOTE MAKES IT DERIVABLE. Each citation follows the phrase it cites, so the true line
can be found by searching the target — which is what `line_citations.py` does, and what makes this a class
that can be closed rather than 39 separate corrections.

This test asserts only that no citation whose quote CAN be located points at the wrong line. It deliberately
does not require every citation to be resolvable: a paraphrase, or a sentence the paper has since rewritten,
is reported as UNRESOLVED and left alone, because repointing a citation at the nearest match is how one
comes to vouch for something it does not say.
"""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import line_citations as lc  # noqa: E402


@pytest.fixture(scope="module")
def scanned():
    _, cites = lc.scan()
    return cites


def test_no_resolvable_line_citation_points_at_the_wrong_line(scanned):
    drifted = [c for c in scanned if c["true"] and c["true"] != c["cited"]]
    assert not drifted, (
        f"{len(drifted)} line citation(s) in the roadmap point at a line that does not contain the phrase "
        f"they quote:\n  "
        + "\n  ".join(f"{c['target']} `:{c['cited']}` should be :{c['true']} — {c['quote'][:70]!r}"
                      for c in drifted)
        + "\n⛔ Do NOT hand-edit these. Run `python3 research/manuscripts/line_citations.py --fix`, which "
          "derives each from the quote it sits beside."
    )


def test_the_checker_still_resolves_a_useful_share_of_them(scanned):
    """⭐ THE GUARD ON THE GUARD.

    The test above passes trivially if the checker resolves NOTHING — a normalisation change, a regex slip,
    or a rename of the target files would make every citation UNRESOLVED and the suite would go green while
    checking zero citations. That is the same "absent reading is not a reading of absence" failure the rest
    of this repository keeps paying for, in test form.

    The bound is deliberately loose: it asserts the checker is alive and discriminating, not a fixed count.
    """
    assert scanned, "no quoted line citations found at all — the scanner or the roadmap's format changed"
    resolved = [c for c in scanned if c["true"]]
    assert len(resolved) >= 10, (
        f"only {len(resolved)} of {len(scanned)} citations resolved to a line. The checker is not doing its "
        f"job — check `_norm`, `QUOTE` and the paper/SI paths before trusting a green run above."
    )


# ─────────────────────────────────────────────────────────────────────────────────────────────────────
# ⛔ AUT-PD-031: A FACT WITH TWO HOMES AND ONE FIXER.
#
# ★ MEASURED 2026-08-27, and it put a RED TRUNK on `main` for hours. An edit to the paper shifted its
# lines by one. `line_citations.py --fix` repaired the roadmap's 18 drifted citations, printed
# "rewrote 18 citation(s)", and exited 0 — and `research/modalities/instrument-census.json` and `.md`,
# which EMBED the roadmap's citation-bearing cells verbatim behind a SEPARATE generator, stayed stale.
# The staleness surfaced THREE COMMITS LATER, in a `PREFLIGHT_MODALITIES=1` run.
#
# ⭐ THE FAILURE WAS SILENCE, NOT A WRONG ANSWER. The fixer was correct about the file it knows and said
# nothing about the file it does not, and silence from a tool that has just reported a success reads as
# completeness. So the tests below assert the two properties that make silence impossible: the list of
# other carriers is DERIVED (nothing can carry the syntax without being enumerated), and a `--fix` that
# leaves a downstream generated copy stale EXITS NON-ZERO.
#
# ⚠ WHAT THEY DELIBERATELY DO NOT ASSERT: that the fixer repairs the other copies. It must not. Their
# correct content is whatever their generator derives, and the resolver here is context-dependent — the
# same citation gets a different quote read from the roadmap than read from the census, because the
# census table has a column the roadmap does not. Repairing across that boundary is how a citation comes
# to vouch for a sentence it does not contain, which is the one thing this module has always refused.
# ─────────────────────────────────────────────────────────────────────────────────────────────────────

import re            # noqa: E402
import shutil        # noqa: E402
import subprocess    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _independently_derived_carriers():
    """Re-derive the carrier set with a DIFFERENT implementation (git grep, not a Python read loop).

    ⭐ THE POINT OF A SECOND IMPLEMENTATION. Asserting `carriers()` against a list built by calling
    `carriers()` proves nothing; asserting it against `git grep -lP` for the same syntax is what makes
    "the enumeration is complete" a measurement instead of a restatement.
    """
    r = subprocess.run(["git", "-C", ROOT, "grep", "-lE", r"`:[0-9]+([–-][0-9]+)?`"],
                       capture_output=True, text=True)
    assert r.returncode in (0, 1), f"git grep failed: {r.stderr}"
    map_rel = os.path.relpath(lc.MAP, ROOT)
    return {f for f in r.stdout.split("\n") if f and f != map_rel}


def test_every_tracked_file_carrying_the_citation_syntax_is_enumerated_by_the_fixer():
    """⛔ THE LEDGER'S OWN ASK: 'a test that every file matching it is in the fixer's own list.'"""
    listed = {f for f, _ in lc.carriers()}
    expected = _independently_derived_carriers()
    missing = expected - listed
    assert not missing, (
        f"{len(missing)} tracked file(s) carry a `:NNNN` line citation and are INVISIBLE to "
        f"`line_citations.py`, so `--fix` would rewrite the roadmap and say nothing about them:\n  "
        + "\n  ".join(sorted(missing))
        + "\n⛔ Do NOT add an exclusion list. `carriers()` derives this set; if it is missing a file, the "
          "derivation is wrong."
    )
    # ⚠ And the other direction, loosely: the enumeration must not invent files.
    assert not (listed - expected), f"carriers() names files that do not carry the syntax: {listed - expected}"


def test_the_enumeration_refuses_to_report_an_empty_list_when_it_cannot_read_the_tree(monkeypatch):
    """⛔ AN ABSENT READING IS NOT A READING OF ABSENCE.

    `_tracked_files()` returning `[]` when git is unavailable would render as "no other file carries a
    line citation" — the exact false completeness this section exists to remove. It must raise.
    """
    class _Fail:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr(lc.subprocess, "run", lambda *a, **k: _Fail())
    with pytest.raises(RuntimeError):
        lc._tracked_files()


def test_a_generated_copy_is_bound_to_a_generator_that_exists_and_declares_itself():
    """⭐ THE GUARD ON THE CLASSIFIER. It passes trivially if nothing is ever classed GENERATED."""
    generated = [(f, g) for f, g in lc.carriers() if g]
    assert generated, (
        "no carrier of a `:NNNN` citation declares a generator. Either the trunk genuinely has none — in "
        "which case `--fix`'s downstream check is now checking nothing — or `GENERATOR_DECL` / "
        "`GENERATOR_DECL_HEADER_LINES` stopped matching the header the generators actually write."
    )
    for f, g in generated:
        assert os.path.isfile(os.path.join(ROOT, g)), f"{f} declares generator {g}, which does not exist"


def test_both_declaration_forms_the_trunk_actually_uses_are_live():
    """⛔ ONE-OF-A-PAIR, AGAIN — MEASURED BY MUTATION M7 (2026-08-28).

    Two generated copies of the census exist and they declare their producer DIFFERENTLY: the `.md` opens
    with an HTML comment, the `.json` carries a `_generated_by` key. Breaking only the HTML-comment regex
    left the earlier suite green, because the JSON half still classified something and every assertion
    was about *some* generated carrier existing. Each form is asserted separately here, through
    `declared_generator` itself so that no window logic is re-implemented (that is what let M5 survive).
    """
    md_form = "<!-- GENERATED by research/modalities/instrument_census.py -- DO NOT HAND-EDIT. -->"
    json_form = '  "_generated_by": "research/modalities/instrument_census.py",'
    assert lc.declared_generator(md_form) == "research/modalities/instrument_census.py", (
        "the HTML-comment declaration form is no longer matched. `instrument-census.md` uses it, and an "
        "unmatched form silently demotes a GENERATED copy to a merely-NAMED one."
    )
    assert lc.declared_generator(json_form) == "research/modalities/instrument_census.py", (
        "the `_generated_by` declaration form is no longer matched. `instrument-census.json` uses it."
    )
    # ⭐ AND BOTH FORMS ARE STILL THE ONES ON THE TRUNK, not a museum piece in this test: each of the two
    # committed census copies must classify.
    by_path = dict(lc.carriers())
    for f in ("research/modalities/instrument-census.md", "research/modalities/instrument-census.json"):
        assert by_path.get(f) == "research/modalities/instrument_census.py", (
            f"{f} carries roadmap line citations verbatim and is no longer bound to its generator, so "
            f"`--fix` would rewrite the roadmap and never `--check` it. That is AUT-PD-031."
        )


def test_the_detector_does_not_classify_a_file_that_merely_describes_it():
    """⚠ MEASURED WHILE WRITING THIS, then measured again by mutation. The detector's first version
    searched the WHOLE file, so `line_citations.py`'s own comment — which quoted both declaration forms
    so a reader could see them — made the module match its own detector and report itself as a generated
    copy of the instrument census. One-of-a-pair in the smallest possible form: a detector and the
    document describing it, in one file.

    ⛔ AND THIS TEST IS ASSERTED THROUGH `carriers()`, NOT THROUGH A RE-IMPLEMENTATION OF THE WINDOW.
    Its first version re-ran `GENERATOR_DECL` against a synthetic string using
    `GENERATOR_DECL_HEADER_LINES` — so widening that constant to 100000 moved the test with the code and
    the mutation SURVIVED (M5, 2026-08-28). THIS file is the live specimen: the line below it contains
    `<!-- GENERATED by …instrument_census.py -->` verbatim, far past the header window, precisely so that
    a widened window classifies this test module as a generated copy of the census and fails here.
    """
    _SPECIMEN = "<!-- GENERATED by research/modalities/instrument_census.py -->"  # noqa: F841
    by_path = dict(lc.carriers())
    me = os.path.relpath(os.path.abspath(__file__), ROOT)
    assert me in by_path, (
        f"{me} carries the `:NNNN` syntax and must be enumerated as a carrier; it is not, so the "
        f"specimen above is no longer doing its job."
    )
    assert by_path[me] is None, (
        f"{me} was classified as GENERATED by {by_path[me]!r}. It is not generated — it merely QUOTES a "
        f"generator declaration, in a test about that exact confusion. `GENERATOR_DECL_HEADER_LINES` is "
        f"too wide, or the declaration is being matched outside the header."
    )
    generated = [(f, g) for f, g in lc.carriers() if g]
    assert generated, "nothing is classified GENERATED any more — the detector is dead, not strict"


def test_a_generator_path_escaping_the_repository_is_refused_and_reported(tmp_path):
    """⛔ `check_generated_carriers` EXECUTES A PATH IT READ OUT OF A FILE.

    `GENERATOR_DECL`'s character class admits `.` and `/`, so `<!-- GENERATED by ../../x.py -->` is a
    well-formed declaration in any file anyone can add. The refusal must also be REPORTED: a generator we
    decline to run is a copy we are not checking, and silently skipping it is the same silence this whole
    section exists to remove.
    """
    results = lc.check_generated_carriers([("some/file.md", "../../escape.py")])
    assert len(results) == 1
    gen, okg, out = results[0]
    assert okg is False and "OUTSIDE" in out, results


def test_fix_exits_non_zero_when_it_leaves_a_downstream_generated_copy_stale(tmp_path):
    """⛔⛔ THE INCIDENT, REPRODUCED END TO END ON A COPY.

    Shift the paper by one line, run `--fix`, and assert BOTH halves of the repair: the roadmap is
    rewritten (the tool still does its job) AND the exit code is non-zero with the stale generated copy
    NAMED (the tool no longer reads as done). A non-zero exit is the one signal a caller cannot mistake
    for completeness — and nothing automated runs `--fix`: `scripts/fast_checks.py` and `tests.yml` both
    invoke the checker with no arguments.

    ⚠ ON A COPY, NEVER THE LIVE TREE. This test mutates a manuscript; a mutation window is a commit
    window, and the repository has paid for that once already.
    """
    work = tmp_path / "tree"
    # ⭐ ONLY THE FILES THIS PATH TOUCHES, re-`git init`ed so `carriers()` can enumerate it. Copying the
    # whole tracked tree also works and costs ~15 s of the manuscripts suite for nothing: the COMPLETENESS
    # of the enumeration is measured against the real repository by the first test in this section, and
    # what is being exercised here is the fix -> stale -> non-zero path.
    for f in ("research/manuscripts/line_citations.py",
              "research/manuscripts/nr4a3-program-map.md",
              "research/manuscripts/degrader/nr4a3-degrader-paper.md",
              "research/manuscripts/degrader/nr4a3-degrader-paper-SI.md",
              "research/modalities/instrument_census.py",
              "research/modalities/instrument-census.json",
              "research/modalities/instrument-census.md"):
        dst = work / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(os.path.join(ROOT, f), dst)
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)

    paper = work / "research" / "manuscripts" / "degrader" / "nr4a3-degrader-paper.md"
    lines = paper.read_text(encoding="utf-8").split("\n")
    lines.insert(5, "")
    paper.write_text("\n".join(lines), encoding="utf-8")

    before = (work / "research" / "manuscripts" / "nr4a3-program-map.md").read_text(encoding="utf-8")
    proc = subprocess.run([sys.executable, "research/manuscripts/line_citations.py", "--fix"],
                          cwd=work, capture_output=True, text=True)
    after = (work / "research" / "manuscripts" / "nr4a3-program-map.md").read_text(encoding="utf-8")

    assert after != before, "the fixer did not rewrite the roadmap at all — the reproduction is broken"
    assert re.search(r"rewrote \d+ citation", proc.stdout), proc.stdout + proc.stderr
    # ⚠ ASSERT ON TEXT ONLY `report_carriers` CAN PRODUCE. The first version of this assertion looked for
    # the census path in stdout — which the stale generator's OWN message ("instrument-census.json has
    # DRIFTED") also contains, so deleting the `report_carriers` call left the test green. Measured by
    # mutation M2, 2026-08-28. The header and the regenerate hint have exactly one source.
    assert "THIS IS NOT THE WHOLE TREE" in proc.stdout, (
        "`--fix` rewrote the roadmap and did not NAME the other files carrying the same line numbers. "
        "That silence is AUT-PD-031.\n" + proc.stdout + proc.stderr
    )
    assert "(regenerate: python3 research/modalities/instrument_census.py)" in proc.stdout, (
        "`--fix` named no generated copy, or stopped printing the command that repairs it.\n"
        + proc.stdout + proc.stderr
    )
    assert proc.returncode != 0, (
        "`--fix` exited 0 while a downstream generated copy was left stale. That exit code is what read "
        "as 'done' and shipped a red trunk.\n" + proc.stdout + proc.stderr
    )


def test_fix_touches_nothing_outside_the_roadmap():
    """⛔ THE FIXER MUST NAME, NOT REPAIR, THE OTHER COPIES — asserted against the source, because the
    danger is a repair that writes a WRONG shared value silently. `--fix` may open exactly one file for
    writing: the roadmap."""
    src = open(os.path.join(MANUSCRIPTS, "line_citations.py"), encoding="utf-8").read()
    writes = re.findall(r'open\(([^,)]+),\s*"w"', src)
    assert writes == ["MAP"], (
        f"line_citations.py writes to {writes}; `--fix` must write only MAP. Repairing a downstream copy "
        f"here would write a value its generator does not produce, and would resolve the citation from a "
        f"different context than the roadmap's — which is how a citation comes to vouch for a sentence it "
        f"does not contain."
    )
