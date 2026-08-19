"""THE OFF-TARGET SCREEN'S PROVENANCE BLOCK AND ITS PARENT FILTER — the two defects of 2026-08-13.

⛔ DEFECT 1: NO SCREEN ARTIFACT RECORDED THE PARAMETER VALUES IT RAN UNDER. Four knobs are
environment-overridable (`BLAST_HITLIST_SIZE`, `SAVED_HITS_PER_DESIGN`, and `OLIGO_LEN`/`WING`
through `junction_aso`), and a screen's `method` block recorded none of them. A `-deep500` re-screen
and the default screen beside it therefore have BYTE-IDENTICAL `method` blocks, separated only by a
filename suffix. That is what let a manuscript sentence claim "a tenfold deeper ceiling and
retention depth": the ceiling did go 50 -> 500, the retention went to 500 rather than 150, and the
error was caught only by counting stored hits in a file.

⛔ DEFECT 2: `is_parent` FIRED ON A BARE SUBSTRING OF THE DEFINITION LINE. For donor gene FUS the
alias tuple carries "FUS" and "TLS", so MITOFUSIN, "vesicle fusing ATPase" and "BCR-ABL fusion
transcript" all read as the parent gene and were dropped from every near-match count.

⭐ WHY THE CORPUS TESTS READ THE COMMITTED SCREENS RATHER THAN A FIXTURE. Both defects are about what
a REAL screen does to REAL RefSeq definition lines, and defect 2's whole safety argument is that no
committed count moves. A fixture cannot establish that; 6,767 committed hit records can.

⚠ WHAT THESE TESTS CANNOT DO. The `parameters` block is FORWARD-ONLY. Regenerating a committed screen
needs network BLAST, so every artifact in this tree predates the block, and none may be hand-edited
to carry one — an inferred value in a provenance field is the failure the block exists to prevent.
The committed-artifact test below therefore asserts the ABSENCE and says why, rather than pretending
the gap is closed.
"""
import glob
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import junction_aso as ja  # noqa: E402
import junction_aso_offtarget as jo  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The three definition lines defect 2 was reported on. Two are RefSeq records of genes that have
#: nothing to do with FUS; the third is a fusion-transcript model. All three contain "FUS".
FUS_SUBSTRING_COLLISIONS = (
    "Homo sapiens mitofusin 1 (MFN1), transcript variant 1, mRNA",
    "Homo sapiens N-ethylmaleimide sensitive factor, vesicle fusing ATPase",
    "PREDICTED: Homo sapiens BCR-ABL fusion transcript, misc_RNA",
)

#: A GENUINE parent record, taken from `hybrid_intron.py` rather than written here — that module
#: already runs the real `is_parent()` on it to measure what the screen does with a perfect
#: wild-type EWSR1 match, and `test_hybrid_intron.py` already asserts the answer is True. Sourcing
#: it from an in-repo user keeps one home for the string and makes this test fail if that one drifts.
WILDTYPE_EWSR1_ACC = "NM_005243.4"
WILDTYPE_EWSR1_DEFN = "Homo sapiens EWS RNA binding protein 1 (EWSR1), transcript variant 1, mRNA"


def _hit(defn, acc="XM_999999.1"):
    """A BLAST hit record carrying only what `is_parent` reads."""
    return {"acc": acc, "defn": defn}


def _screens():
    """Every committed screen artifact — the real ones, not the graded re-scores.

    ⚠ EVERY GEOMETRY, DELIBERATELY, AND ONE GEOMETRY AT A TIME RATHER THAN AS A GLOB. The tests
    below ask per-file questions — does this screen carry a `parameters` block, is it
    orientation-filtered, does `is_parent` misfire on its hits — and nothing is summed across
    screens, so a longer geometry is one more case to check. What the loader supplies that the glob
    did not is that each file has been MEASURED and checked against its own stated gap span before
    any test reads it.
    """
    import aso_screen_sets as ass  # noqa: PLC0415
    for _geom, screens in ass.iter_geometries(ass.BLAST_SCREEN, root=MOD):
        for s in screens:
            yield s.path, s.artifact


def _run_with_env(**env):
    """Import the module in a FRESH PROCESS under a real environment and read the block back.

    ⛔ A SUBPROCESS, NOT A MONKEYPATCH, AND THAT IS THE WHOLE POINT OF THESE THREE TESTS. The knobs
    are resolved at IMPORT time — `BLAST_HITLIST_SIZE` here, `OLIGO_LEN`/`WING` inside
    `junction_aso` — and `_ENV_OVERRIDDEN` is captured at that same instant. Patching the module
    constants afterwards would exercise the patch and prove nothing about the path CI actually
    takes, which is `env VAR=… python junction_aso_offtarget.py`. Mock the thing under test and you
    test the mock.
    """
    e = dict(os.environ)
    e.update(env)
    out = subprocess.run(
        [sys.executable, "-c",
         "import json, junction_aso_offtarget as jo; print(json.dumps(jo.screen_parameters()))"],
        cwd=MOD, env=e, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


# ─────────────────────────────────────────────────────────────────────────────────────────
# DEFECT 1 — the artifact states the parameters it ran under
# ─────────────────────────────────────────────────────────────────────────────────────────

def test_the_method_block_records_all_four_overridable_knobs():
    """The defect in one assertion: before this, `method` named none of the four.

    Asserted on `method_block()` — the function `main()` calls — so this cannot pass because a test
    helper happens to build a richer dict than the screen does.
    """
    m = jo.method_block({"note": "breakpoint model note"})
    p = m["parameters"]
    for k in ("blast_hitlist_size", "saved_hits_per_design", "oligo_len", "wing"):
        assert k in p, f"the method block still does not record {k}"
    # and it has not lost anything a committed screen already carried
    for k in ("db", "program", "near_match_threshold", "gap_region_1based",
              "breakpoint_model", "parent_set"):
        assert k in m, f"method_block dropped {k}, which every committed screen carries"


def test_the_recorded_values_are_the_ones_the_screen_actually_uses():
    """The values must come from the module constants the screen reads, not from a second copy.

    `SAVED_HITS_PER_DESIGN` is the number `screen_one` truncates its saved list with and
    `BLAST_HITLIST_SIZE` is the number `blast_put` sends to NCBI, so a `parameters` block that
    described anything else would be a provenance field reporting a value nothing ran under.
    """
    p = jo.screen_parameters()
    assert p["blast_hitlist_size"] == jo.BLAST_HITLIST_SIZE
    assert p["saved_hits_per_design"] == jo.SAVED_HITS_PER_DESIGN
    assert p["oligo_len"] == ja.OLIGO_LEN
    assert p["wing"] == ja.WING
    # the derived fields beside it must agree with the knobs it reports
    m = jo.method_block({"note": "n"})
    assert m["gap_region_1based"] == [p["wing"] + 1, p["oligo_len"] - p["wing"]]
    assert m["near_match_threshold"].endswith(f"/{p['oligo_len']} identical")


def test_a_default_run_reports_no_override():
    """The baseline. Every committed screen was a default run, and a block that could not say so
    would be unable to distinguish one from the deep re-screen — which is the defect.

    ⚠ THE FOUR DEFAULTS ARE PINNED HERE AS A TRIPWIRE, NOT AS A SECOND HOME FOR THEM. The manuscript
    quotes 50 and 15 as the ceiling and the retention depth every committed screen ran at; if a
    default moves, every one of those sentences becomes a statement about a value the code no longer
    uses, and that is a decision for a human rather than a number to update in passing.
    """
    p = _run_with_env(BLAST_HITLIST_SIZE="", SAVED_HITS_PER_DESIGN="", OLIGO_LEN="", WING="")
    assert p["overridden_from_env"] == []
    assert (p["blast_hitlist_size"], p["saved_hits_per_design"]) == (50, 15), (
        "a screen default moved; the manuscript's ceiling/retention figures and every committed "
        "screen's provenance now describe a different search than the code performs")
    assert (p["oligo_len"], p["wing"]) == (16, 5), (
        "the gapmer geometry default moved; the length-specific discrimination bound "
        "(duroux_16mer_none) is pinned to 16-mers — see test_junction_aso_graded.py")


def test_an_empty_env_var_is_a_default_run_not_an_override():
    """⛔ THE TRAP, AND IT IS ON THE LIVE CI PATH. `aso-offtarget.yml` splits one `gapmer_geometry`
    input into `OLIGO_LEN` and `WING` and then `export`s BOTH, so a dispatch that leaves the
    geometry blank exports them as EMPTY STRINGS rather than leaving them unset. `ja._env_int`
    treats "" as absent and uses the default — so a presence test written as `name in os.environ`
    would stamp `overridden_from_env: ["OLIGO_LEN", "WING"]` onto every screen CI has ever produced,
    describing an override that never happened, on the exact path every real run takes.

    This is the assertion that fails if `_env_was_set` is ever rewritten to test presence.
    """
    p = _run_with_env(OLIGO_LEN="", WING="   ")
    assert "OLIGO_LEN" not in p["overridden_from_env"]
    assert "WING" not in p["overridden_from_env"]
    assert (p["oligo_len"], p["wing"]) == (16, 5)


def test_the_deep_rescreen_is_distinguishable_from_a_default_screen():
    """⭐ THE CASE THE WHOLE BLOCK EXISTS FOR. `aso-offtarget.yml`'s `deep_rescreen` mode exports
    exactly these two variables; before this block the resulting artifact's `method` was
    byte-identical to a default screen's, so "which ceiling did this run at?" had no answer in the
    file and the manuscript's answer was wrong.
    """
    deep = _run_with_env(BLAST_HITLIST_SIZE="500", SAVED_HITS_PER_DESIGN="500")
    shallow = _run_with_env(BLAST_HITLIST_SIZE="", SAVED_HITS_PER_DESIGN="")
    assert deep != shallow, "a 500/500 re-screen still records the same parameters as a 50/15 run"
    assert deep["blast_hitlist_size"] == 500
    assert deep["saved_hits_per_design"] == 500
    assert sorted(deep["overridden_from_env"]) == ["BLAST_HITLIST_SIZE", "SAVED_HITS_PER_DESIGN"]
    # the geometry was NOT set by that dispatch, and the block must not claim it was
    assert "OLIGO_LEN" not in deep["overridden_from_env"]


def test_a_geometry_override_is_recorded_and_moves_the_derived_fields():
    """The 20-mer (5-10-5) lane. Both the knobs and everything derived from them must move together,
    because a screen whose `gap_region_1based` disagreed with its recorded `wing` would be two
    contradictory readings of the same run."""
    p = _run_with_env(OLIGO_LEN="20", WING="5")
    assert (p["oligo_len"], p["wing"]) == (20, 5)
    assert sorted(p["overridden_from_env"]) == ["OLIGO_LEN", "WING"]


def test_the_parameters_block_says_it_cannot_be_backfilled():
    """⚠ The one thing a reader of a NEW artifact needs to know about the OLD ones: their missing
    block is an absence of RECORD, not evidence they ran at these values. Stated in the artifact
    rather than only in a commit message, because the artifact is what gets archived."""
    what = jo.screen_parameters()["_what"].lower()
    assert "cannot be added" in what or "cannot be backfilled" in what
    assert "default" in what, "the block must say what an unlisted knob means"


#: Screens that legitimately carry a `parameters` block, with the CI run that produced each. A name
#: enters this list only when a real dispatch wrote the file; the run id is what makes that
#: checkable, and it is the whole difference between a recorded provenance block and an asserted one.
#: ⛔ ADDING A NAME HERE IS NOT HOW YOU FIX A RED BUILD. It is how you record a re-screen that
#: happened. If a block appeared without a run behind it, the file was hand-edited and the fix is to
#: revert the file, never to extend this list.
SCREENS_FROM_A_REAL_RERUN = {
    # The gap-length comparison: the same six frame-compatible seams the 5-6-5 panel was screened
    # at, re-tiled at 5-8-5 and 5-10-5 and screened at the same 500-deep ceiling and retention.
    # Dispatched at branch `worktree-agent-ad8ebd78fe770a538`, 2026-08-13.
    **{f"junction-aso-offtarget-{j}-18mer-deep500.json": "Actions run 31747720046"
       for j in ("e12n3", "taf15e11n3", "fuse10n3", "tcf12e7n3", "fuse8n3", "taf15e1n3")},
    **{f"junction-aso-offtarget-{j}-20mer-deep500.json": "Actions run 31747727309"
       for j in ("e12n3", "taf15e11n3", "fuse10n3", "tcf12e7n3", "fuse8n3", "taf15e1n3")},
    # ⭐ RE-DISPATCHES OF THREE JUNCTIONS WHOSE FIRST RUN LOST A DESIGN TO AN NCBI TRANSPORT DROP.
    # They are SEPARATE ARTIFACTS rather than replacements: each re-run recovered the design its
    # predecessor lost and lost a different one, so neither file is complete and neither supersedes
    # the other. `aso_gap_length_tradeoff` unions them at read time; nothing is merged on disk.
    "junction-aso-offtarget-taf15e11n3-18mer-deep500-b2.json": "Actions run 31749261712",
    "junction-aso-offtarget-fuse8n3-20mer-deep500-b2.json": "Actions run 31749268061",
    "junction-aso-offtarget-taf15e1n3-20mer-deep500-b2.json": "Actions run 31749268061",
}


@pytest.mark.committed_artifact
def test_every_committed_screen_predates_the_block_and_none_was_hand_backfilled():
    """⛔ THE ABSENCE IS ASSERTED, NOT PAPERED OVER.

    Regenerating a screen needs network BLAST, so this change reaches FUTURE screens only. Every
    artifact in this tree that predates the block legitimately lacks it. What must never happen is
    someone closing that gap by hand: the parameters a past run used are not recoverable from its
    output, so a `parameters` block appearing on an artifact that no re-run produced would be an
    inferred value in a provenance field — a populated field that was never measured, which is the
    exact failure this block was added to prevent.

    ⚠ SO THIS TEST IS EXPECTED TO CHANGE, AND ONLY IN ONE WAY: when a screen is genuinely re-run,
    it arrives with the block and this assertion fails. That is the signal to move the artifact into
    `SCREENS_FROM_A_REAL_RERUN`, WITH the run that produced it. It must never be satisfied by
    editing a JSON file.

    ⭐ AND IT FIRED FOR EXACTLY THAT REASON ON 2026-08-13, WHICH IS THE FIRST TIME IT HAD ANYTHING TO
    SAY. Twelve screens arrived carrying the block from two real dispatches. It also caught a
    thirteenth that was NOT from either of them — a `-spanprobe` artifact pulled into the working
    tree by an over-broad `git checkout` of the `modalities-cache` branch — so the guard separated a
    legitimate re-run from a stray in the same failure message.
    """
    unexplained = [os.path.basename(p) for p, s in _screens()
                   if "parameters" in (s.get("method") or {})
                   and os.path.basename(p) not in SCREENS_FROM_A_REAL_RERUN]
    assert unexplained == [], (
        "these screens carry a `parameters` block but no re-run in this tree could have produced "
        f"one: {unexplained}. If a real re-screen produced them, record which run did and move them "
        "into SCREENS_FROM_A_REAL_RERUN; if they were hand-edited, revert — an inferred provenance "
        "value is worse than a visible gap.")


@pytest.mark.committed_artifact
def test_every_allow_listed_screen_is_present_and_really_carries_the_block():
    """The allow-list may not outlive what it explains, or it becomes a licence rather than a record.

    Two directions, and the second is the one that rots: a name here whose file is gone leaves a
    standing exemption for a filename anyone could later create, and a name here whose file carries
    NO parameters block never needed an exemption at all.
    """
    have = {os.path.basename(p): s for p, s in _screens()}
    for name, run in sorted(SCREENS_FROM_A_REAL_RERUN.items()):
        #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit) — AND THE DOCSTRING ABOVE ALREADY SAYS WHY.
        #: "a name here whose file is gone leaves a standing exemption for a filename anyone could
        #: later create" is precisely the state this skip used to pass over in silence. The
        #: allow-list is the record; a missing member is the rot it exists to catch.
        assert name in have, (
            f"{name} is allow-listed as carrying a recorded parameters block (produced by {run}) "
            "and is not in this tree. A standing exemption for a filename nothing produces is a "
            "licence, not a record — remove the entry or restore the screen.")
        assert "parameters" in (have[name].get("method") or {}), (
            f"{name} is allow-listed as carrying a recorded parameters block and does not")
        assert re.search(r"run \d{6,}", run), f"{name} names no CI run id: {run!r}"


@pytest.mark.committed_artifact
def test_the_deep500_screens_are_still_indistinguishable_by_their_method_block():
    """The measured statement of the defect, kept as evidence rather than as prose.

    A `-deep500` screen ran at 500/500 and its default sibling at 50/15, and their `method` blocks
    are identical — which is why the retention error survived. This test is a record of the state
    the fix does NOT repair retroactively; it fails the day those artifacts are re-run, which is
    the day the claim above stops being true of them.
    """
    by_name = {os.path.basename(p): s for p, s in _screens()}
    pairs = [(n, n.replace("-deep500", "")) for n in by_name if n.endswith("-deep500.json")]
    pairs = [(d, s) for d, s in pairs if s in by_name]
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit). This test IS the record of a state the fix does
    #: not repair retroactively, so an empty pair set means the evidence it preserves has left the
    #: tree — which has to be said out loud, not passed over.
    assert pairs, (
        "no -deep500 / default screen pair is in this tree, so the recorded indistinguishability "
        "of their method blocks — the defect that let the retention error survive — is asserted "
        "against nothing. If the screens were genuinely re-run, re-derive this test against the "
        "re-run rather than letting it fall silent.")
    same = [(d, s) for d, s in pairs if by_name[d].get("method") == by_name[s].get("method")]
    assert same, "the -deep500 pairs now differ in `method` — re-derive this test against the re-run"
    # and the tell that a retention of 150 cannot explain: a design storing more than 150 hits
    deepest = max(len(o.get("offtargets") or [])
                  for d, _ in pairs for o in by_name[d].get("oligos", []))
    assert deepest > 150, (
        "the evidence that the retention went to 500 rather than 150 is a design storing more hits "
        f"than 150 could produce; the deepest committed -deep500 design now stores {deepest}")


# ─────────────────────────────────────────────────────────────────────────────────────────
# DEFECT 2 — `is_parent` anchors on the RefSeq gene symbol
# ─────────────────────────────────────────────────────────────────────────────────────────

def test_a_gene_whose_name_merely_contains_a_parent_symbol_is_not_a_parent():
    """⛔ THE DEFECT. Under the old bare-substring arm every one of these returned True for donor
    gene FUS and was silently dropped from the near-match count.

    Run against a FUS donor set built from the module's own alias table, not a hand-typed one, so
    an alias added to `_DONOR_ALIASES` is covered here the day it lands.
    """
    fus_aliases = jo._DONOR_ALIASES["FUS"]
    assert "FUS" in fus_aliases and "TLS" in fus_aliases, (
        "this test is about the FUS/TLS symbols specifically; the alias table changed")
    symbols = tuple(g.upper() for g in fus_aliases if " " not in g)
    phrases = tuple(g.upper() for g in fus_aliases if " " in g)
    for defn in FUS_SUBSTRING_COLLISIONS:
        d = defn.upper()
        assert any(s in d for s in symbols), (
            f"{defn!r} no longer contains a bare parent symbol, so it no longer demonstrates the "
            "defect — pick a definition line that does")
        found = {m.group(1).upper() for m in jo._REFSEQ_SYMBOL.finditer(d)}
        assert not found.intersection(symbols), f"{defn!r} matched the symbol arm"
        assert not any(p in d for p in phrases), f"{defn!r} matched the phrase arm"
        assert not any(jo._symbol_as_a_whole_word(s, d) for s in symbols), (
            f"{defn!r} matched the whole-word arm")


def test_a_genuine_parent_record_is_still_a_parent_by_name_alone():
    """The other direction, and the one that must not move: a real wild-type parent transcript is
    dropped from the off-target count on the strength of its definition line, with the accession arm
    deliberately disabled so the name arms are what is being tested."""
    assert jo.is_parent(_hit(WILDTYPE_EWSR1_DEFN)) is True
    # and with its real accession, which is in PARENT_ACCS, it is a parent twice over
    assert jo.is_parent(_hit(WILDTYPE_EWSR1_DEFN, acc=WILDTYPE_EWSR1_ACC)) is True


def test_the_hybrid_intron_fixture_is_still_the_string_this_test_pins():
    """One home for the wild-type EWSR1 definition line. `hybrid_intron.py` runs the real
    `is_parent()` on it to show that an intron-body oligo's fatal liability is filtered out as a
    parent hit; if that string drifts, the positive assertion above is testing a different record
    than the module is."""
    src = os.path.join(MOD, "hybrid_intron.py")
    with open(src, "r", encoding="utf-8") as fh:
        body = fh.read()
    assert WILDTYPE_EWSR1_DEFN in body, (
        "hybrid_intron.py no longer carries this definition line; re-source the fixture")
    assert WILDTYPE_EWSR1_ACC in body


def test_every_parent_alias_of_every_donor_still_matches_its_own_refseq_record():
    """No donor may lose its parent filter. Built from the module's alias table so a new donor is
    covered automatically, in RefSeq's own `description (SYMBOL), qualifiers` format.

    ⚠ These are synthetic FORMAT fixtures, not records: they carry no accession and assert nothing
    about the transcriptome. What is under test is the matcher, and the format is the one measured
    over all 6,767 committed hit definition lines.
    """
    probe = (
        "import json, junction_aso_offtarget as jo\n"
        "res = {}\n"
        "for alias in jo.PARENT_GENES:\n"
        "    sym = [g for g in jo.PARENT_GENES if ' ' not in g][0]\n"
        "    d = ('Homo sapiens %s (%s), transcript variant 1, mRNA' % (alias, sym)\n"
        "         if ' ' in alias else\n"
        "         'Homo sapiens some description (%s), transcript variant 1, mRNA' % alias)\n"
        "    res[alias] = jo.is_parent({'acc': 'XM_999999.1', 'defn': d})\n"
        "print(json.dumps(res))\n")
    for donor in jo._DONOR_ALIASES:
        out = subprocess.run([sys.executable, "-c", probe], cwd=MOD,
                             env={**os.environ, "DONOR_GENE": donor},
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr
        res = json.loads(out.stdout.strip().splitlines()[-1])
        assert res, f"donor {donor}: no aliases probed"
        missed = [a for a, ok in res.items() if not ok]
        assert missed == [], f"donor {donor}: aliases no longer match their own record: {missed}"


@pytest.mark.committed_artifact
def test_the_new_predicate_is_a_strict_subset_of_the_bare_substring_one():
    """⛔ THE PROPERTY THAT MAKES THIS SAFE TO LAND WITHOUT RE-RUNNING A SINGLE SCREEN.

    Each name arm implies the old test: a parenthesised `(FUS)` contains "FUS", a phrase match IS a
    substring match, and a whole-word match is a substring match with lookarounds. So the set of
    hits dropped as parents can only SHRINK, never grow — no currently-stored off-target can become
    a parent, and no committed near-match count can silently re-base.

    Checked against the real definition lines rather than argued, over every hit in every committed
    screen plus the collision cases.
    """
    def old_is_parent(h):
        acc = h["acc"].split(".")[0]
        if acc in jo.PARENT_ACCS:
            return True
        d = h["defn"].upper()
        return any(g.upper() in d for g in jo.PARENT_GENES)

    checked = 0
    for _, screen in _screens():
        for o in screen.get("oligos", []):
            for h in (o.get("offtargets") or []):
                rec = _hit(h.get("defn", ""), acc=h.get("acc", ""))
                if jo.is_parent(rec):
                    assert old_is_parent(rec), f"new predicate is WIDER on {rec['defn']!r}"
                checked += 1
    for defn in FUS_SUBSTRING_COLLISIONS:
        rec = _hit(defn)
        if jo.is_parent(rec):
            assert old_is_parent(rec)
        checked += 1
    assert checked > 1000, f"only {checked} definition lines checked — the corpus did not load"


@pytest.mark.committed_artifact
def test_no_committed_near_match_count_moves_under_the_new_parent_filter():
    """The measured guarantee, on real data: every hit STORED in every committed screen was stored
    because `is_parent` said False, and it must still say False. If one flipped, that hit would
    vanish from a count the manuscript quotes and the fix would have re-based a published number.

    ⚠ Measured 2026-08-13 while making this change: 0 of 6,767 stored definition lines contain
    "FUS" or "TLS" in any form, so the exposure of defect 2 was NIL. The fix is a correctness fix,
    not a correction to a number, and this test is what says so out loud.
    """
    flipped, checked = [], 0
    for p, screen in _screens():
        for o in screen.get("oligos", []):
            for h in (o.get("offtargets") or []):
                checked += 1
                if jo.is_parent(_hit(h.get("defn", ""), acc=h.get("acc", ""))):
                    flipped.append((os.path.basename(p), h.get("acc"), h.get("defn")))
    assert checked > 1000, f"only {checked} stored hits found — the corpus did not load"
    assert flipped == [], f"{len(flipped)} stored off-targets became parents: {flipped[:5]}"


@pytest.mark.committed_artifact
def test_the_refseq_symbol_anchor_is_supported_by_every_committed_definition_line():
    """The anchor is a MEASURED convention, not a hopeful one. If RefSeq definition lines ever stop
    carrying `(SYMBOL),`, the symbol arm silently stops deciding and the whole-word fallback — the
    loosest arm — becomes the one doing the work. That is worth failing over rather than drifting
    into."""
    missing, checked = [], 0
    for p, screen in _screens():
        for o in screen.get("oligos", []):
            for h in (o.get("offtargets") or []):
                checked += 1
                if not jo._REFSEQ_SYMBOL.search((h.get("defn") or "").upper()):
                    missing.append((os.path.basename(p), h.get("defn")))
    assert checked > 1000, f"only {checked} stored hits found — the corpus did not load"
    assert missing == [], (
        f"{len(missing)} of {checked} definition lines carry no parenthesised gene symbol: "
        f"{missing[:5]}")


def test_the_alias_split_is_derived_from_the_one_alias_tuple():
    """`PARENT_SYMBOLS` / `PARENT_PHRASES` must partition `PARENT_GENES` exactly. A second
    hand-maintained list is how the `DONOR_GENE` stale-constant defect happened once already."""
    assert set(jo.PARENT_SYMBOLS) | set(jo.PARENT_PHRASES) == {g.upper() for g in jo.PARENT_GENES}
    assert not set(jo.PARENT_SYMBOLS) & set(jo.PARENT_PHRASES)
    assert all(" " not in s for s in jo.PARENT_SYMBOLS)
    assert all(" " in p for p in jo.PARENT_PHRASES)


def test_the_accession_arm_is_untouched():
    """The strongest arm, and the one no definition-line change may weaken: a hit on a parent
    accession is a parent whatever its definition line says."""
    for acc in jo.PARENT_ACCS:
        assert jo.is_parent(_hit("Homo sapiens uncharacterized locus, mRNA", acc=acc + ".4")) is True
    assert jo.is_parent(_hit("Homo sapiens uncharacterized locus, mRNA")) is False
