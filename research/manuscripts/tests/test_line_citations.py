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
import subprocess
import sys
import unicodedata

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
    """⛔ THE ORIGINAL DEFECT: a citation that resolves, to the wrong line.

    ⚠ SCOPED TO CONFIDENT ATTACHMENTS SINCE 2026-09-01, and the scoping is not a loosening. A citation
    whose quote is separated from it by another citation or a sentence boundary is one `--fix` refuses to
    rewrite — demanding a green build on it would demand a hand-edit the tool declines to specify. Before
    this change such a citation was attached to a PHANTOM quote and reported UNRESOLVED, which gated
    nothing either; what changed is that it is now named as a drift a reader has to settle, and
    `test_an_unconfident_drift_is_reported_rather_than_swallowed` asserts it is still reported.
    """
    drifted = [c for c in scanned if c["status"] == "drifted" and c["confident"]]
    assert not drifted, (
        f"{len(drifted)} line citation(s) in the roadmap point at a line that does not contain the phrase "
        f"they quote:\n  "
        + "\n  ".join(f"{c['target']} `:{c['cited']}` should be :{c['true']} — {c['quote'][:70]!r}"
                      for c in drifted)
        + "\n⛔ Do NOT hand-edit these. Run `python3 research/manuscripts/line_citations.py --fix`, which "
          "derives each from the quote it sits beside, THEN regenerate the downstream copies it names."
    )


def test_an_unconfident_drift_is_reported_rather_than_swallowed(scanned):
    """⛔ THE SCOPING ABOVE MUST NOT BECOME A HIDING PLACE.

    `confident=False` buys exemption from the FIXER, never from the REPORT. Every drifted citation, of
    either confidence, must carry a resolved line so a reader can settle it; a record that reached
    `drifted` with `true=None` would be an exemption with nothing behind it.
    """
    for c in scanned:
        if c["status"] == "drifted":
            assert c["true"] and c["true"] != c["cited"], c


def test_every_citation_in_the_roadmap_is_accounted_for(scanned):
    """⛔⛔ AUT-PD-134: THE DENOMINATOR WAS THE DEFECT.

    Until 2026-09-01 `scan()` dropped every citation that had no quoted phrase in its 400-character
    lookback — fourteen of them — and then reported "(42 quoted citations)" as though that were the file.
    A tool that silently narrows its own scope cannot be caught by a threshold on its output, because the
    threshold is measured against the narrowed set.

    ⭐ THE COUNT IS DERIVED, TWICE, INDEPENDENTLY. The expected total is re-derived here with `git grep -o`
    — a different implementation from the module's own `CITE.finditer` — so this is a measurement rather
    than a restatement of what `scan()` chose to walk.
    """
    r = subprocess.run(["git", "-C", ROOT, "grep", "-I", "-oP", r"`:[0-9]+([–-][0-9]+)?`", "--",
                        os.path.relpath(lc.MAP, ROOT).replace(os.sep, "/")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    expected = len([l for l in r.stdout.split("\n") if l.strip()])
    assert expected > 0, "git grep found no citations in the roadmap at all — the syntax changed"
    assert len(scanned) == expected, (
        f"`scan()` returned {len(scanned)} records for {expected} citations in the roadmap. Every citation "
        f"must produce a record, including the ones this tool cannot check — a dropped citation is one "
        f"nothing will ever report on, which is exactly AUT-PD-134."
    )
    unknown = {c["status"] for c in scanned} - set(lc.STATUSES)
    assert not unknown, f"scan() invented statuses outside STATUSES: {unknown}"


def test_the_checker_resolves_every_citation_an_independent_reader_can_resolve(scanned):
    """⭐⭐ THE GUARD ON THE GUARD, AND IT IS DERIVED RATHER THAN TYPED.

    It replaces `assert len(resolved) >= 10`, which was a number somebody chose. Ten was below the
    then-live count of eighteen and far below the fifty-six citations in the file, so the checked share
    could fall by half without anything going red — the guard permitted the rot it was written to catch.

    ⛔ THE FLOOR IS NOW THE TREE ITSELF. A SECOND, INDEPENDENTLY WRITTEN normaliser (below — it folds the
    same typography as `_norm` but shares no code with it) says which attached quotes are genuinely
    present in their target. Every one of those must reach a status that means the checker FOUND it. If a
    regex slip, a rename or a normalisation change makes `_norm` blind, this goes red at exactly the
    citations that went dark, and the bound moves with the roadmap instead of ageing into a formality.

    ⚠ IT IS DELIBERATELY NOT AN EQUALITY. `not_found` is the honest verdict for a paraphrase the paper has
    since rewritten, and the independent reader must not be able to force a match the strict one refuses.
    """
    def _independently_normalised(s):
        s = unicodedata.normalize("NFKC", s)
        for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                     ("\u2013", "-"), ("\u2014", "-")):
            s = s.replace(a, b)
        return " ".join("".join(ch for ch in s if ch not in "*`_\\").lower().split())

    targets = {"paper": _independently_normalised(open(lc.PAPER, encoding="utf-8").read()),
               "SI": _independently_normalised(open(lc.SI, encoding="utf-8").read())}
    blind = []
    for c in scanned:
        if c["status"] != "not_found":
            continue
        parts = [p for p in lc.ELIDE.split(c["quote"]) if p.strip()]
        if all(_independently_normalised(p) in targets[c["target"]] for p in parts):
            blind.append(c)
    assert not blind, (
        f"{len(blind)} citation(s) quote text that IS in the target, and the checker reported it "
        f"not-found. The resolver has gone blind to them:\n  "
        + "\n  ".join(f"{c['target']} `:{c['cited']}` — {c['quote'][:70]!r}" for c in blind)
    )


# ─────────────────────────────────────────────────────────────────────────────────────────────────────
# ⭐ THE RESOLVER'S OWN BEHAVIOUR, ON A SYNTHETIC TREE.
#
# ⛔ WHY A FIXTURE AND NOT THE ROADMAP. The guard the four tests below replace asserted a COUNT against
# the live roadmap, so it measured the roadmap's prose as much as the resolver's code and could only ever
# say "fewer than expected resolved" without saying which mechanism died. Each test here breaks exactly
# one mechanism's back and names it, and none of them moves when the roadmap is edited.
# ─────────────────────────────────────────────────────────────────────────────────────────────────────


def _tree(tmp_path, monkeypatch, roadmap, paper, si="SI line one\n"):
    m, p_, s_ = tmp_path / "map.md", tmp_path / "paper.md", tmp_path / "si.md"
    m.write_text(roadmap, encoding="utf-8")
    p_.write_text(paper, encoding="utf-8")
    s_.write_text(si, encoding="utf-8")
    monkeypatch.setattr(lc, "MAP", str(m))
    monkeypatch.setattr(lc, "PAPER", str(p_))
    monkeypatch.setattr(lc, "SI", str(s_))
    return {c["cited"]: c for c in lc.scan()[1]}


def test_the_resolver_is_alive_and_discriminating_on_a_synthetic_tree(tmp_path, monkeypatch):
    """⭐ THE LIVENESS HALF OF THE OLD `>= 10`, WITHOUT ITS NUMBER.

    A quote that is present at a known line must resolve TO that line, and a quote that is absent must
    NOT resolve. A `_norm` regression, a `QUOTE` slip or a target-path rename fails the first half; a
    resolver that has started guessing fails the second.
    """
    got = _tree(
        tmp_path, monkeypatch,
        roadmap=('*"the alpha sentence carries this"* (`:2`)\n\n'
                 '*"a phrase the paper never contained"* (`:9`)\n'),
        paper="filler line one\nthe alpha sentence carries this, plus more\nfiller\n",
    )
    assert got[2]["status"] == "ok" and got[2]["true"] == 2, got[2]
    assert got[9]["status"] == "not_found" and got[9]["true"] is None, got[9]


def test_a_bold_quoted_phrase_does_not_open_a_citation_quote(tmp_path, monkeypatch):
    r"""⛔ MECHANISM 2 (2026-09-01). `**"…"**` is ordinary bold-plus-quotes prose in these documents, and
    the old `\*"(.+?)"\*` matched the SECOND asterisk of a `**"`. The span then ran to the next `"*`
    anywhere in the file — on the trunk, 900 characters downstream — swallowing the genuine citation quote
    that lay between and handing the citation a phrase from an unrelated paragraph.

    ⚠ AND THE CLOSING ASYMMETRY IS ASSERTED TOO, in the second half: the trunk writes a citation quote
    INSIDE a bold run (`**SI `:229` — *"…"***`), so a matching guard on `"*` would drop a real quote. The
    two halves are one test because a fix that adds `(?!\*)` passes the first and fails the second.

    ⛔ THE SPECIMEN'S SHAPE IS LOAD-BEARING AND ITS FIRST VERSION SURVIVED THE MUTATION. `**"aside"**`
    does NOT reproduce the defect: the phantom span opens at the `*"` and closes one word later at the
    same run's `"*`, harming nothing. The trunk's actual shape is `**"quoted" then more words**` — the
    closing quotation mark is NOT adjacent to the bold markers, so the span finds no close until the next
    genuine citation quote and swallows it whole. Measured by mutation M1, 2026-09-01.
    """
    got = _tree(
        tmp_path, monkeypatch,
        roadmap=('Prose with **"bold" then several more words** in it, then the real one:\n'
                 '*"the alpha sentence carries this"* (`:2`)\n'),
        paper="filler line one\nthe alpha sentence carries this, plus more\nfiller\n",
    )
    assert got[2]["status"] == "ok" and got[2]["true"] == 2, (
        "a `**\"…\"**` bold aside opened a quote span and swallowed the real citation quote", got[2])

    got = _tree(
        tmp_path, monkeypatch,
        roadmap='**A heading `:2` — *"the alpha sentence carries this"*** and more\n',
        paper="filler line one\nthe alpha sentence carries this, plus more\nfiller\n",
    )
    assert got[2]["status"] == "ok", (
        "a citation quote written inside a bold run (`*\"…\"***`) is no longer matched at all", got[2])


def test_a_quote_that_follows_its_citation_is_attached_to_it(tmp_path, monkeypatch):
    """⛔ MECHANISM 3. The roadmap writes `` `:N`: *"…"* `` and `` `:N` says *"…"* ``. Backwards-only
    attachment missed those AND let the next citation reach back past them for a quote that was never its
    own — one citation lost, one mis-attributed, from a single gap.

    The second half is the anti-widening assertion: a quote a full sentence later must NOT be swept up,
    because "the nearest quote in either direction" is how a citation with no quote at all acquires one.
    """
    got = _tree(
        tmp_path, monkeypatch,
        roadmap='the paper `:2` says *"the alpha sentence carries this"* and that is all\n',
        paper="filler line one\nthe alpha sentence carries this, plus more\nfiller\n",
    )
    assert got[2]["status"] == "ok" and got[2]["true"] == 2, got[2]

    got = _tree(
        tmp_path, monkeypatch,
        roadmap='a bare reference (`:2`). A different sentence: *"the alpha sentence carries this"*\n',
        paper="filler line one\nthe alpha sentence carries this, plus more\nfiller\n",
    )
    assert got[2]["status"] == "no_quote", (
        "the trailing-quote grammar widened past punctuation and one attributive verb, so a citation with "
        "no quote of its own took the next sentence's", got[2])


def test_a_quote_wrapped_over_more_than_two_lines_still_resolves(tmp_path, monkeypatch):
    """⛔ MECHANISM 4. `_find` joined at most two lines — a guess about wrapping, not a rule about
    citations. Two live roadmap citations were wrong by +68 and +15 lines behind that limit, reported as
    unresolvable paraphrases. The window is now derived from the needle's own length.

    ⛔ AND THE ANCHOR IS ASSERTED WITH IT: a match must BEGIN on the line the resolver returns. Without
    that, a window long enough to hold the needle holds it from almost any starting line, and every
    citation becomes `ambiguous` — a failure that looks like strictness.
    """
    got = _tree(
        tmp_path, monkeypatch,
        roadmap='*"a quoted phrase that the paper happens to wrap across four separate lines"* (`:2`)\n',
        paper=("filler line one\na quoted phrase that\nthe paper happens to\nwrap across four\n"
               "separate lines and then continues\nfiller\n"),
    )
    assert got[2]["status"] == "ok" and got[2]["true"] == 2, got[2]


def test_a_quote_that_occurs_twice_is_ambiguous_and_never_rewritten(tmp_path, monkeypatch):
    """⛔ `_find` used to return the FIRST match and say nothing about the rest.

    Two roadmap citation pairs already share one quoted phrase while citing DIFFERENT lines
    (`:387–394`/`:2549`, `:1405`/`:1425`). A first-match resolver collapses both onto one line the moment
    that phrase becomes findable, and the collapse is silent — the citations still point at real lines.
    """
    got = _tree(
        tmp_path, monkeypatch,
        roadmap='*"the alpha sentence carries this"* (`:2`)\n',
        paper="filler\nthe alpha sentence carries this\nfiller\nthe alpha sentence carries this\n",
    )
    assert got[2]["status"] == "ambiguous" and got[2]["true"] is None, got[2]


def test_a_quote_too_short_to_identify_a_line_is_reported_as_such(tmp_path, monkeypatch):
    """⚠ `_find` refused a needle under `MIN_NEEDLE` and returned `None`, indistinguishable from "the
    paper no longer says this". Three live citations (`SI :213`, quoting *"must clear"*) were counted as
    stale paraphrases when the checker had simply declined to look."""
    got = _tree(
        tmp_path, monkeypatch,
        roadmap='*"must clear"* (`:2`)\n',
        paper="filler\nmust clear the bar\nfiller\n",
    )
    assert got[2]["status"] == "quote_too_short", got[2]


def test_an_attachment_that_crosses_another_citation_is_reported_but_not_auto_fixed(tmp_path, monkeypatch,
                                                                                   capsys):
    """⭐⭐ THE TWO HALVES AUT-PD-134 SAID MUST NOT BE FIXED AS ONE.

    Correctness — did we attach the right quote? — and staleness — has the paper stopped saying this? — are
    different defects with different remedies, and a change that raised the resolved count by loosening
    the match would have hidden the first while appearing to fix the second. The separation is this: an
    attachment that crosses another citation or a sentence boundary is still CHECKED and still REPORTED,
    and `--fix` will not rewrite it. This test asserts both halves, and that `--fix` still rewrites the
    confident one in the same run — a fixer that refused everything would also pass half of this.
    """
    roadmap = ('*"the alpha sentence carries this"* (`:9`) and later, unrelated, (`:7`)\n'
               '*"the beta sentence carries that"* (`:8`)\n')
    got = _tree(tmp_path, monkeypatch, roadmap=roadmap,
                paper="filler\nthe alpha sentence carries this\nthe beta sentence carries that\n")
    assert got[9]["status"] == "drifted" and got[9]["confident"] and got[9]["true"] == 2, got[9]
    assert got[7]["status"] == "drifted" and not got[7]["confident"] and got[7]["true"] == 2, (
        "a citation separated from its quote by ANOTHER citation was treated as a confident attachment; "
        "`--fix` would rewrite it on a guess", got[7])

    monkeypatch.setattr(lc, "carriers", lambda: [])
    monkeypatch.setattr(lc, "check_generated_carriers", lambda found: [])
    rc = lc.main(["--fix"])
    after = open(lc.MAP, encoding="utf-8").read()
    assert "(`:2`)" in after, "`--fix` did not rewrite the confident drift at all"
    assert "(`:7`)" in after, (
        "`--fix` rewrote a citation whose attachment crosses another citation. That is a repair made on a "
        "guessed attachment, which is how a citation comes to vouch for a sentence it does not contain."
    )
    out = capsys.readouterr().out
    assert "LEFT 1 DRIFTED CITATION" in out, ("`--fix` was silent about the drift it declined to repair — "
                                              "silence from a tool that just reported a success reads as "
                                              "completeness.\n" + out)
    assert rc != 0, "`--fix` exited 0 while leaving a drifted citation for a reader to settle"


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

ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _independently_derived_carriers():
    """Re-derive the carrier set with a DIFFERENT implementation (git grep, not a Python read loop).

    ⭐ THE POINT OF A SECOND IMPLEMENTATION. Asserting `carriers()` against a list built by calling
    `carriers()` proves nothing; asserting it against `git grep -lP` for the same syntax is what makes
    "the enumeration is complete" a measurement instead of a restatement.
    """
    r = subprocess.run(["git", "-C", ROOT, "grep", "-I", "-lP", r"`:[0-9]+([–-][0-9]+)?`"],
                       capture_output=True, text=True)
    assert r.returncode in (0, 1), f"git grep failed: {r.stderr}"
    map_rel = os.path.relpath(lc.MAP, ROOT).replace(os.sep, "/")
    return {f for f in r.stdout.split("\n") if f and f != map_rel}


def test_git_enumeration_covers_unicode_ranges_but_not_binary_archives(tmp_path):
    """Independent Git matching must agree on textual syntax without reading binary payloads."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "citations.txt").write_text("`:12` `:13-15` `:16–18`\n", encoding="utf-8")
    (tmp_path / "ordinary.txt").write_text("12-18 is not a line citation\n", encoding="utf-8")
    (tmp_path / "archive.bin").write_bytes(b"\x00archive payload `:999`\x00")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    pattern = r"`:[0-9]+([–-][0-9]+)?`"
    result = subprocess.run(["git", "-C", str(tmp_path), "grep", "-I", "-oP", pattern],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "citations.txt:`:12`", "citations.txt:`:13-15`", "citations.txt:`:16–18`"]


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
    me = os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")
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


def test_the_pin_detector_names_the_carriers_that_declare_a_basis_commit():
    """⭐ AUT-PD-031'S RESIDUAL, HALF-SETTLED BY MACHINE AND HONEST ABOUT THE OTHER HALF.

    The row closed the fixer's silence about downstream copies and left this open: the tool NAMES the
    hand-written carriers and CHECKS none, and deciding which are pinned-by-design "is a reading job
    nobody has done". A machine can settle one half of it — whether the document's own header names the
    commit its line numbers were taken against — and `declared_pin` reports exactly that half.

    ⛔ WHAT IT MUST NOT BECOME: evidence that the undeclared ones are current. Both classes print as
    unchecked; this test asserts the detector still finds the declared ones, and the module asserts
    nothing about the rest.
    """
    by_path = {f: g for f, g in lc.carriers()}
    pinned = {}
    for f, g in by_path.items():
        if g:
            continue
        with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
            pin = lc.declared_pin(fh.read())
        if pin:
            pinned[f] = pin
    assert "research/manuscripts/program/map-audit-strategy.md" in pinned, (
        "the largest hand-written carrier states its own basis in its header — *\"Audited: … at commit "
        "`f67d0781`\"* — and the detector no longer reads it. That is the one file where advancing a "
        "line number would silently re-date an audit."
    )
    assert len(pinned) >= 1 and all(re.fullmatch(r"[0-9a-f]{7,40}", v) for v in pinned.values()), pinned


def test_the_pin_detector_does_not_classify_the_module_that_describes_it():
    """⛔ ONE-OF-A-PAIR, THE SAME TRAP THAT CAUGHT THE GENERATOR DETECTOR (M5, 2026-08-28).

    `line_citations.py`'s docstring quotes `map-audit-strategy.md`'s declaration verbatim — including the
    commit — so a whole-file search makes the module report ITSELF as a pinned audit. The window is the
    fix, and this asserts it through `declared_pin` rather than re-implementing it, because a test that
    re-applies `GENERATOR_DECL_HEADER_LINES` itself moves with a widened constant and survives.
    """
    with open(os.path.join(MANUSCRIPTS, "line_citations.py"), encoding="utf-8") as fh:
        body = fh.read()
    assert lc.PIN_DECL.search(body), (
        "the specimen is gone from line_citations.py, so this test no longer tests anything: the module "
        "no longer quotes a basis-commit declaration anywhere."
    )
    assert lc.declared_pin(body) is None, (
        "line_citations.py classified itself as a document with a pinned basis commit. It is not one — it "
        "merely QUOTES the declaration, in the docstring about that exact confusion. The header window is "
        "too wide, or the declaration is being matched outside it."
    )


def test_a_generator_path_escaping_the_repository_is_refused_and_reported(tmp_path):
    """⛔ `check_generated_carriers` EXECUTES A PATH IT READ OUT OF A FILE.

    `GENERATOR_DECL`'s character class admits `.` and `/`, so `<!-- GENERATED by ../../x.py -->` is a
    well-formed declaration in any file anyone can add. The refusal must also be REPORTED: a generator we
    decline to run is a copy we are not checking, and silently skipping it is the same silence this whole
    section exists to remove.
    """
    results = lc.check_generated_carriers([("some/file.md", "../../escape.py")])
    assert len(results) == 1
    gen, status, out = results[0]
    assert status == lc.GEN_UNMEASURED and "OUTSIDE" in out, results
    # ⛔ AND IT IS UNMEASURED, NOT STALE. A generator we refuse to run told us nothing about its copy;
    # filing that under "stale" is a finding we did not make.
    assert status != lc.GEN_STALE, results


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


# ─────────────────────────────────────────────────────────────────────────────────────────────────────
# AUT-PD-031, SECOND HALF (2026-09-02, seat s29). The enumeration landed and the fixer stopped being
# silent — and it then started printing a reading it had not taken. Measured on the trunk: the ledger
# declares `research/autonomy/priority.py` as its producer, `priority.py` has no `--check`, and the
# two-valued checker turned an argparse usage error into "reports its committed copy stale". A
# MANUFACTURED finding printed beside a real one is worse than the silence it replaced, because the
# reader who checks it and finds nothing wrong learns to discount the whole block.
#
# ⛔ THE THREE PROPERTIES THESE GUARDS PIN, and each is a thing the tool could otherwise say untruthfully:
#   (1) a generator that cannot be ASKED is UNMEASURED, never STALE — and still exits non-zero;
#   (2) a generator whose source does not advertise the flag is NOT RUN AT ALL, because a generator that
#       does not recognise an argv REGENERATES on it, and a linter that silently rewrites a deposit
#       artifact is a worse bug than the staleness it reports;
#   (3) no run — green, red, check or fix — may end on a line that reads as completeness: the rewrite
#       count is never last, and every verdict counts the carriers it did NOT check.
# ─────────────────────────────────────────────────────────────────────────────────────────────────────


def _carrier_tree(tmp_path, generator_source, decl=None):
    """A minimal git tree holding one carrier that declares one generator. Returns (work, sentinel)."""
    work = tmp_path / "tree"
    (work / "gen").mkdir(parents=True)
    (work / "gen" / "g.py").write_text(generator_source, encoding="utf-8")
    (work / "copy.md").write_text(
        (decl if decl is not None else "<!-- GENERATED by gen/g.py -->") + "\n\n`:1234`\n",
        encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)
    return work, work / "REGENERATED"


def test_a_generator_whose_source_never_mentions_the_flag_is_not_run_at_all(tmp_path, monkeypatch):
    """⛔⛔ THE PROHIBITION THAT WAS WRITTEN AND NOT ENFORCED.

    `check_generated_carriers` has always said "this function must never regenerate". It then handed
    `--check` to whatever path a file declared — and the shape `if "--check" in argv: … else: WRITE` (the
    shape `instrument_census.py` itself uses) regenerates on any argv it does not recognise. Today's
    carriers are safe because one implements the flag and one rejects it through argparse: safe by luck,
    which is exactly what "RECORDED IS NOT ENFORCED" means in this repository.

    The specimen below WRITES A SENTINEL on any invocation. If the tool runs it, the sentinel exists.
    """
    work, sentinel = _carrier_tree(tmp_path, "import pathlib\n"
                                             "pathlib.Path(__file__).parent.parent.joinpath('REGENERATED')"
                                             ".write_text('written')\n")
    monkeypatch.setattr(lc, "ROOT", str(work))
    results = lc.check_generated_carriers([("copy.md", "gen/g.py")])
    assert not sentinel.exists(), (
        "line_citations RAN a generator whose source never mentions `--check`, and the generator wrote "
        "the tree. A linter that silently regenerates a deposit artifact is a worse bug than the "
        "staleness it was reporting."
    )
    assert len(results) == 1 and results[0][1] == lc.GEN_UNMEASURED, results
    assert "NOT RUN" in results[0][2] and "UNMEASURED" in results[0][2], results[0][2]


def test_a_generator_that_refuses_the_flag_is_unmeasured_and_never_reported_as_stale(tmp_path,
                                                                                    monkeypatch):
    """⛔ THE TRUNK'S OWN CASE, IN MINIATURE: argparse exits 2 on an unknown flag.

    The specimen MENTIONS `--check` (in a docstring) so the static gate lets it run, and then rejects it
    the way `priority.py` does. That is the second, independent mechanism: a token search cannot tell a
    mention from an implementation, so the refusal is caught after the fact instead.
    """
    work, _ = _carrier_tree(tmp_path, '"""A generator. It does not take --check."""\n'
                                      "import argparse\n"
                                      "argparse.ArgumentParser().parse_args()\n")
    monkeypatch.setattr(lc, "ROOT", str(work))
    results = lc.check_generated_carriers([("copy.md", "gen/g.py")])
    assert len(results) == 1, results
    gen, status, out = results[0]
    assert status == lc.GEN_UNMEASURED, (
        "a generator that REFUSED the flag was reported as %r. It made no statement about its copy: "
        "reporting the refusal as staleness is a finding this tool did not make, printed beside ones it "
        "did.\n%s" % (status, out)
    )
    assert status != lc.GEN_STALE
    assert "NOT a staleness reading" in out, out


def test_a_generator_that_answers_is_read_as_the_answer_it_gave(tmp_path, monkeypatch):
    """⭐ THE GUARD ON THE GUARD: every above passes trivially if nothing is ever FRESH or ever STALE."""
    ok, bad = ("import sys\nsys.exit(0 if '--check' in sys.argv else 1)\n",
               "import sys\nsys.exit(3 if '--check' in sys.argv else 0)\n")
    for src, want in ((ok, lc.GEN_FRESH), (bad, lc.GEN_STALE)):
        work, _ = _carrier_tree(tmp_path / want, src)
        monkeypatch.setattr(lc, "ROOT", str(work))
        results = lc.check_generated_carriers([("copy.md", "gen/g.py")])
        assert results[0][1] == want, (want, results)


def test_the_trunks_generated_carriers_are_actually_asked_and_at_least_one_answers():
    """⛔ AN ALWAYS-UNMEASURED CHECKER IS A CHECKER THAT CHECKS NOTHING, and it would pass every test
    above. On the real tree at least one declared generator must be reachable and must ANSWER — today
    `instrument_census.py` does, at ~0.03 s."""
    found = lc.carriers()
    results = lc.check_generated_carriers(found)
    assert results, "no carrier declares a generator, so the downstream check is checking nothing"
    fresh = [g for g, st, _ in results if st == lc.GEN_FRESH]
    assert fresh, (
        "not one declared generator on the trunk could be ASKED and answered. Either every generator "
        "lost its `--check`, or `_advertises_check` / `FLAG_REFUSED` stopped letting anything through — "
        "in which case the downstream half of AUT-PD-031 is silently doing nothing.\n%r" % (results,)
    )


def test_the_module_does_not_classify_itself_as_a_generated_copy():
    """⛔ ONE-OF-A-PAIR, AND IT BIT AGAIN ON 2026-09-02 WHILE WRITING THE FIX ABOVE.

    `test_the_detector_does_not_classify_a_file_that_merely_describes_it` asserts on THIS TEST MODULE.
    Its pin-detector twin asserts on `line_citations.py`. Nobody asserted the GENERATOR detector against
    `line_citations.py` itself — so when the new docstring quoted the ledger's declaration verbatim
    inside the header window, the module classified ITSELF as a generated copy of `priority.py`, the
    generated count went 3 -> 4, and the whole suite stayed green. The guard existed and was pointed at
    the wrong specimen, which is this repository's most-repeated defect.
    """
    by_path = dict(lc.carriers())
    me = os.path.relpath(os.path.join(MANUSCRIPTS, "line_citations.py"), ROOT).replace(os.sep, "/")
    assert me in by_path, f"{me} no longer carries the `:NNNN` syntax, so this test measures nothing"
    assert by_path[me] is None, (
        f"line_citations.py classified ITSELF as generated by {by_path[me]!r}. It is not generated — its "
        f"docstring merely describes generator declarations. Move the literal out of the first "
        f"{lc.GENERATOR_DECL_HEADER_LINES} lines, or the module will keep asking a generator about a copy "
        f"that is its own source."
    )


def test_unmeasured_is_as_loud_as_stale_and_the_verdict_never_reads_as_success():
    """⛔⛔ THE HONEST-OUTPUT HALF, ON THE PURE FUNCTION. `verdict` is where every exit code is decided,
    so a copy that is stale OR unmeasured must produce a non-zero exit and must be NAMED — and no run
    with one outstanding may print a tick."""
    found = [("a.md", "gen.py"), ("hand.md", None)]
    for status in (lc.GEN_STALE, lc.GEN_UNMEASURED):
        lines, code = lc.verdict(found, [("gen.py", status, "detail-%s" % status)], rewrote=18)
        blob = "\n".join(lines)
        assert code != 0, (
            "verdict() exited 0 with a %s copy outstanding. Exit 0 after `rewrote 18 citation(s)` is "
            "precisely what read as done and shipped a red trunk.\n%s" % (status, blob))
        assert "gen.py" in blob, blob
        assert "✓" not in blob, (
            "a ✓ was printed while a copy was %s. A tick beside an unmeasured copy is the same false "
            "completeness in a smaller font.\n%s" % (status, blob))
    # ⭐ AND THE OTHER DIRECTION: an all-fresh run is allowed to exit 0, or these assertions are vacuous.
    _, code = lc.verdict(found, [("gen.py", lc.GEN_FRESH, "")], rewrote=0)
    assert code == 0


def test_the_verdict_distinguishes_unmeasured_from_stale_in_what_it_prints():
    """⛔ THE EXIT CODE IS THE SAME; THE REASON IS NOT, AND THE REASON IS THE HALF A READER ACTS ON.
    Folding "I could not ask" into "it says it is stale" is the fabricated reading §4 names."""
    found = [("a.md", "gen.py")]
    stale = "\n".join(lc.verdict(found, [("gen.py", lc.GEN_STALE, "x")], rewrote=0)[0])
    unmeas = "\n".join(lc.verdict(found, [("gen.py", lc.GEN_UNMEASURED, "x")], rewrote=0)[0])
    assert "STALE" in stale and "UNMEASURED" not in stale.split("verdict:")[0], stale
    assert "UNMEASURED" in unmeas and "STALE:" not in unmeas, unmeas
    assert stale != unmeas


def test_every_verdict_counts_the_carriers_it_did_not_check():
    """⛔ THE CLAUSE THAT MUST SURVIVE A GREEN RUN. "N files were never checked" is exactly the fact a
    clean-looking run hides, so it is printed in EVERY mode and EVERY outcome — including the one where
    nothing is wrong, which is the only run anybody reads quickly."""
    found = [("a.md", "gen.py"), ("hand1.md", None), ("hand2.md", None)]
    for gen_results in (None, [("gen.py", lc.GEN_FRESH, "")],
                        [("gen.py", lc.GEN_STALE, "")]):
        last = lc.verdict(found, gen_results, rewrote=0)[0][-1]
        assert "NOT CHECKED" in last and "2 hand-written carrier(s)" in last, (gen_results, last)


def test_the_rewrite_count_is_never_the_last_thing_the_fixer_says():
    """⛔⛔ THE INCIDENT IN ONE SENTENCE. `rewrote 18 citation(s)` was TRUE; being the LAST THING SAID is
    what made it read as done. The count now lives inside the verdict, which always continues past it."""
    found = [("hand.md", None)]
    for gen_results in (None, [], [("gen.py", lc.GEN_FRESH, "")]):
        lines = lc.verdict(found, gen_results, rewrote=18)[0]
        last = lines[-1]
        assert "rewrote 18" in last and "NOT CHECKED" in last, (gen_results, lines)
        assert not last.strip().endswith("rewrote 18 citation(s)"), last


def test_fix_names_and_exits_non_zero_when_a_generator_cannot_be_asked(tmp_path):
    """⛔ END TO END, ON A COPY: the trunk's real shape — a carrier declaring a generator with no
    `--check` — must leave `--fix` non-zero with the copy named UNMEASURED, not silently green and not
    falsely stale."""
    work = tmp_path / "tree"
    for f in ("research/manuscripts/line_citations.py",
              "research/manuscripts/nr4a3-program-map.md",
              "research/manuscripts/degrader/nr4a3-degrader-paper.md",
              "research/manuscripts/degrader/nr4a3-degrader-paper-SI.md"):
        dst = work / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(os.path.join(ROOT, f), dst)
    (work / "gen").mkdir(parents=True, exist_ok=True)
    (work / "gen" / "g.py").write_text("print('I do not take a check flag')\n", encoding="utf-8")
    (work / "copy.md").write_text("<!-- GENERATED by gen/g.py -->\n\n`:1234`\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)

    proc = subprocess.run([sys.executable, "research/manuscripts/line_citations.py", "--fix"],
                          cwd=work, capture_output=True, text=True)
    assert proc.returncode != 0, (
        "`--fix` exited 0 while a generated copy went UNMEASURED. An unasked generator is not a clean "
        "one.\n" + proc.stdout + proc.stderr)
    assert "UNMEASURED" in proc.stdout and "gen/g.py" in proc.stdout, proc.stdout + proc.stderr
    assert "NOT CHECKED by this tool" in proc.stdout.strip().split("\n")[-1], proc.stdout


def test_the_exit_code_separates_a_broken_tree_from_an_unaskable_one():
    """⛔⛔ THE FIX FOR A SILENT TOOL MUST NOT BE A PERMANENTLY RED ONE, AND `2` IS NOT A SOFTENING.

    ⚠ MEASURED, and it is why this contract exists rather than a single non-zero: `research-ledger.json`
    is UNMEASURABLE BY CONSTRUCTION. `priority.py` stamps `score_inputs.age_factor_as_of` from today's
    date, so the ledger is not byte-reproducible from the graph and its generator cannot honestly carry a
    read-only `--check` at all. Folding that into the WRONG code would leave `--fix` red on every run of
    every day, over a condition nobody can clear — CLAUDE.md §6: "a gate that reddens under load is one
    people learn to re-run — worse than no gate".

    ⛔ AND THE ANSWER IS NEVER 0. `EXIT_UNMEASURED` is non-zero, stops a `&&` chain, and is named in the
    verdict every run. What it declines to do is claim the tree is broken when the truth is that one copy
    cannot be asked — and it must never MASK a real fault, which is the last case below.
    """
    found = [("a.md", "g1.py"), ("b.md", "g2.py")]
    assert lc.EXIT_UNMEASURED != 0, "an unmeasured copy that exits 0 is the silence this row is about"
    assert lc.EXIT_WRONG != lc.EXIT_UNMEASURED != lc.EXIT_CLEAN
    cases = (
        ([("g1.py", lc.GEN_FRESH, ""), ("g2.py", lc.GEN_FRESH, "")], lc.EXIT_CLEAN),
        ([("g1.py", lc.GEN_FRESH, ""), ("g2.py", lc.GEN_UNMEASURED, "")], lc.EXIT_UNMEASURED),
        ([("g1.py", lc.GEN_STALE, ""), ("g2.py", lc.GEN_FRESH, "")], lc.EXIT_WRONG),
        # ⛔ THE ONE THAT MATTERS MOST: a standing condition must never downgrade a real fault.
        ([("g1.py", lc.GEN_STALE, ""), ("g2.py", lc.GEN_UNMEASURED, "")], lc.EXIT_WRONG),
    )
    for gen_results, want in cases:
        assert lc.verdict(found, gen_results, rewrote=0)[1] == want, (gen_results, want)
    # ⚠ A drift left for a reader is WRONG NOW, not a standing condition.
    assert lc.verdict(found, [("g1.py", lc.GEN_FRESH, ""), ("g2.py", lc.GEN_UNMEASURED, "")],
                      rewrote=0, needs_review=1)[1] == lc.EXIT_WRONG
