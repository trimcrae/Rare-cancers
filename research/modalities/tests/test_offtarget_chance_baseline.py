#!/usr/bin/env python3
"""The chance-baseline generator, and the guard whose absence let its default invocation drift.

⛔ THE DEFECT THIS FILE EXISTS FOR. `offtarget_chance_baseline.py` globbed
`aso-insilico-evaluation*.json`, which meant one file per junction until the deeper re-screen
campaign began emitting a second evaluation per junction under its own suffix. Then a plain
`python3 offtarget_chance_baseline.py` read 51 panels instead of 40 and produced `n_designs` 255
against the committed 200, `mean` 8.1 against 9.5, `n_at_or_below_chance_upper` 192 against 142, and
61 multi-junction oligonucleotides spanning [2, 4] seams against the committed 9 spanning [2, 3] —
while reproducing the committed artifact byte-for-byte under the non-default
`--panels-from-artifact`.

⚠ THE SHAPE OF THIS IS WORSE THAN A CRASH, WHICH IS WHY THE FIRST TEST BELOW IS THE ONE IT NEEDED.
A generator whose default output disagrees with its committed artifact reads as reproducible: it
exits 0, writes a plausible file, and the disagreement is visible only to somebody who diffs. No test
ran the thing the way anybody actually runs it, so nothing could see that.

⛔ AND NOTHING HERE WRITES INTO THE MODALITIES DIRECTORY. Two reasons, both learned writing this
file. A stray `aso-insilico-evaluation-*.json` beside the real ones is precisely the failure under
test, so a test that created one would be reproducing the bug in order to check for it. And the
pre-fix module had no `--check` at all, so `--check` fell through to the WRITE path: running these
tests against the unfixed module OVERWROTE the committed artifact, and every later test in the file
then read the corrupted copy and failed for the wrong reason. Anything that must exercise the real
command line therefore runs against an isolated copy of the tree.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import aso_screen_sets as ass
import offtarget_chance_baseline as B  # noqa: E402

ART = os.path.join(MOD, "offtarget-chance-baseline.json")
SCRIPT = os.path.join(MOD, "offtarget_chance_baseline.py")


def _committed():
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit): it IS committed, so an absence is a broken tree.
    if not os.path.exists(ART):
        pytest.fail(f"the chance-baseline artifact is missing at {ART}; it is committed, and the "
                    "null the paper's near-match counts are read against is unchecked without it.")
    return open(ART, encoding="utf-8").read()


def _panel(name):
    path = os.path.join(MOD, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} is not in this checkout")
    return path, json.load(open(path))


def _copy_to(tmp_path, record, name):
    p = tmp_path / name
    p.write_text(json.dumps(record), encoding="utf-8")
    return str(p)


def _isolated_tree(tmp_path):
    """A throwaway copy of the module, its inputs and its artifact, so the CLI can be run for real.

    The module resolves everything from its own `__file__`, so a copy is a complete, isolated
    installation — the command under test can write whatever it likes and the checkout is untouched.
    """
    d = tmp_path / "modalities"
    d.mkdir()
    shutil.copy(SCRIPT, d)
    # ⚠ THE ISOLATED TREE MUST HOLD WHAT THE REAL ONE HOLDS, INCLUDING THE OTHER GEOMETRIES. Every
    # panel of every geometry is copied on purpose: a fixture quietly containing only the 16-mer
    # panels would exercise a corpus the module never meets, and selecting correctly out of a
    # directory that has all three is the module's whole job here.
    for _g, screens in ass.iter_geometries(ass.DESIGN_EVALUATION, root=MOD):
        for sc in screens:
            shutil.copy(sc.path, d)
    shutil.copy(ART, d)
    shutil.copy(os.path.join(MOD, "aso_screen_sets.py"), d)   # the loader travels with the module
    return d


def _run(script, *args):
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def test_the_default_derivation_reproduces_the_committed_artifact():
    """⛔ THE GUARD WHOSE ABSENCE WAS THE WHOLE DEFECT. No flags, exactly as a person runs it.

    In-process and byte-for-byte against the committed file, so it asserts the DEFAULT derivation
    without writing anything. It fails on the pre-fix module, which counted every re-emitted panel
    as a new junction and returned 255 rows where the committed artifact holds 200.
    """
    committed = _committed()
    derived = json.dumps(B.build(), indent=2)
    if derived != committed:
        got, want = json.loads(derived)["observed"], json.loads(committed)["observed"]
        pytest.fail("the DEFAULT derivation no longer reproduces the committed artifact: "
                    f"n_designs {got['n_designs']} vs {want['n_designs']}, "
                    f"mean {got['mean']} vs {want['mean']}, "
                    f"at-or-below {got['n_at_or_below_chance_upper']} vs "
                    f"{want['n_at_or_below_chance_upper']}")


def test_check_mode_verifies_instead_of_writing(tmp_path):
    """⛔ A `--check` THAT WRITES IS NOT A CHECK.

    The module had no `--check` at all, so the flag fell through to the write path: it overwrote the
    artifact it was asked to verify and exited 0 — the one behaviour a staleness gate must never
    have. Both directions are asserted, because a gate that always passes and a gate that always
    fails are equally useless.
    """
    d = _isolated_tree(tmp_path)
    script, art = d / "offtarget_chance_baseline.py", d / "offtarget-chance-baseline.json"

    before = art.read_text(encoding="utf-8")
    r = _run(script, "--check")
    assert r.returncode == 0, f"--check called a current artifact stale:\n{r.stderr}"
    assert art.read_text(encoding="utf-8") == before, "--check rewrote the artifact it was checking"

    art.write_text('{"stale": 1}', encoding="utf-8")
    r = _run(script, "--check")
    assert r.returncode == 1, "--check passed a stale artifact"
    assert art.read_text(encoding="utf-8") == '{"stale": 1}', (
        "--check repaired the artifact instead of reporting it")


def test_the_default_run_writes_and_names_every_panel_it_set_aside(tmp_path):
    """The whole command line, end to end, on a copy — and the collapse is in the readout.

    ⚠ A selection rule that silently drops files reads exactly like the glob that silently added
    them, so every set-aside panel is named where the operator is looking.
    """
    d = _isolated_tree(tmp_path)
    script, art = d / "offtarget_chance_baseline.py", d / "offtarget-chance-baseline.json"
    committed = art.read_text(encoding="utf-8")
    r = _run(script)
    assert r.returncode == 0, r.stderr
    assert art.read_text(encoding="utf-8") == committed
    n_panels = len(B.panel_paths())
    n_used = len({row["_source"] for row in json.loads(committed)["per_design"]})
    if n_panels > n_used:
        assert "collapsed onto the seam" in r.stderr, r.stderr
        for line in r.stderr.splitlines():
            if "set aside" in line:
                assert "-> kept" in line
    # ⚠ THE TWO OMISSIONS ARE DIFFERENT DECISIONS AND MUST READ DIFFERENTLY. A panel collapsed onto
    # the seam it re-screens is named "set aside X -> kept Y"; a panel excluded for being a
    # different reagent length is named "excluded X (designs of length N)". A line carrying the
    # collapse verb without `-> kept` would read as a truncated collapse, which is why the geometry
    # readout uses its own wording and why both are asserted here rather than only the first.
    if any(g != ass.MANUSCRIPT_GEOMETRY
           for g, _ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=MOD)):
        assert "at other geometries excluded" in r.stderr, r.stderr
        for line in r.stderr.splitlines():
            if line.strip().startswith("excluded "):
                assert "designs of length" in line, line


def test_one_panel_per_seam_and_geometry():
    """No two chosen panels are re-emissions of one another: same seam AND same reagent length.

    ⚠ THE KEY GAINED ITS SECOND HALF ON 2026-08-14 AND THIS IS NOT A RELAXATION. It previously read
    `seam_identity` alone, which was complete while every panel was a 16-mer. The gap-length work
    evaluates these seams at 18 and 20 nucleotides too, and those are different molecules rather
    than re-readings of one — so grouping them made the selector refuse to build at all. The
    property under test is unchanged, that de-duplication leaves no duplicate; what changed is what
    counts as a duplicate. Both halves are asserted, so collapsing on either alone still fails.
    """
    # ⚠ EVERY GEOMETRY HERE, because the property under test is that the compound key
    # de-duplicates ACROSS them — a population narrowed to one geometry could not fail it.
    paths = [sc.path for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=MOD)
             for sc in ss]
    chosen, collapsed = B.select_primary_panels(paths)
    assert len(chosen) + len(collapsed) == len(paths)
    keys = [(B.seam_identity(d), tuple(sorted(B.panel_oligo_lens(d)))) for _, d in chosen]
    assert len(set(keys)) == len(keys), "two chosen panels screen the same seam at the same length"

    # and the seam half still does real work: the 16-mer subset alone must have unique seams
    at_16 = [k for k in keys if k[1] == (B.OLIGO_LEN,)]
    assert len({k[0] for k in at_16}) == len(at_16), "two 16-mer panels screen the same seam"
    assert len(at_16) < len(keys), (
        "no longer-geometry panel is present, so the second half of the key is untested here")


def test_a_re_emission_under_an_unanticipated_suffix_is_still_collapsed(tmp_path):
    """⛔ THE POINT OF NOT KEYING ON A FILENAME. `-deep500` is a convention, not a discriminator.

    A panel restating a seam under a suffix nobody has used yet must still collapse onto it. This
    fails against any fix that excludes a spelling instead of reading the panel's own record.
    """
    src, d = _panel("aso-insilico-evaluation-e1n3.json")
    for invented in ("aso-insilico-evaluation-e1n3-quantum-rerun-v7.json",
                     "aso-insilico-evaluation-e1n3-deep500-b1.json",
                     "evaluation-of-e1n3-under-some-other-name.json"):
        other = _copy_to(tmp_path, d, invented)
        chosen, collapsed = B.select_primary_panels([src, other])
        assert len(chosen) == 1 and chosen[0][0] == src, invented
        assert [c["set_aside"] for c in collapsed] == [invented]


def test_an_unlabelled_control_panel_does_not_fall_back_to_its_filename(tmp_path):
    """The two legacy control seams carry no `junction_label`, and that hole had to be closed too.

    Keying an unlabelled panel on its basename would let a re-emission of it duplicate silently —
    the same defect, in the one corner where the primary key is absent. Its seam identity is instead
    the breakpoint it declares and the window that breakpoint produced, both properties of the seam.
    """
    src, d = _panel("aso-insilico-evaluation-bp200-8.json")
    assert d.get("junction_label") is None, "this panel now has a label; the test's premise is gone"
    other = _copy_to(tmp_path, d, "aso-insilico-evaluation-bp200-8-rescreen.json")
    chosen, collapsed = B.select_primary_panels([src, other])
    assert len(chosen) == 1 and len(collapsed) == 1

    # ...and two DIFFERENT unlabelled seams must still be two seams, or the fix would quietly merge
    # the two legacy controls into one and lose a whole panel from the excluded set.
    src2, _ = _panel("aso-insilico-evaluation.json")
    chosen2, collapsed2 = B.select_primary_panels([src, src2])
    assert len(chosen2) == 2 and collapsed2 == []


def test_two_evaluations_of_one_seam_that_disagree_are_refused_not_resolved(tmp_path):
    """⛔ CHOOSING BETWEEN THEM IS A DATA DECISION, NOT A DERIVATION DETAIL.

    `offtarget_le1mm` is the uncapped scan, so a deeper search ceiling cannot move it; two panels for
    one seam reporting different counts are two different evaluations. Picking one silently would
    re-base numbers the manuscript quotes as a side effect of a regeneration.
    """
    src, d = _panel("aso-insilico-evaluation-e1n3.json")
    d = json.loads(json.dumps(d))
    d["top_designs"][0]["offtarget_le1mm"] = (d["top_designs"][0]["offtarget_le1mm"] or 0) + 7
    other = _copy_to(tmp_path, d, "aso-insilico-evaluation-e1n3-disagreeing.json")
    with pytest.raises(ValueError) as e:
        B.select_primary_panels([src, other])
    assert "different off-target counts" in str(e.value)
    assert "--panels-from-artifact" in str(e.value), "a refusal must say what to do next"


def test_a_junction_design_pair_may_appear_exactly_once(monkeypatch):
    """The invariant every count in the artifact is arithmetic over.

    ⚠ ASSERTED INDEPENDENTLY OF HOW PANELS ARE CHOSEN, which is the whole point: the selection makes
    this unreachable today, and the guard is what fails loudly the next time something enlarges this
    population by a route nobody anticipated. Exercised by handing `collect_observed` a duplicated
    selection rather than by trusting that the selection is the only way in.
    """
    rows = B.collect_observed()
    keys = [(r["junction"], r["antisense_5to3"]) for r in rows]
    assert len(set(keys)) == len(keys), "the real panel set already double-counts a design"

    real = B.select_primary_panels
    monkeypatch.setattr(B, "select_primary_panels",
                        lambda paths: (lambda c, d: (c + c[:1], d))(*real(paths)))
    with pytest.raises(ValueError) as e:
        B.collect_observed()
    assert "appears twice" in str(e.value) and "pseudoreplication" in str(e.value)


def test_the_multi_junction_span_counts_seams_not_files():
    """The tell that named the mechanism, asserted on the DERIVED artifact rather than the committed
    one, so it is a test of the generator instead of a test of a file.

    `dedupe_sequences` collapses one oligonucleotide's rows and appends a junction label per row, so
    two panels for the SAME junction appended the SAME label twice and a design at one seam was
    recorded as spanning two. The committed artifact says nine multi-seam molecules spanning [2, 3];
    the pre-fix default said 61 spanning [2, 4].
    """
    art = B.build()
    fs = art["figure_series"]
    assert fs["n_multi_junction_sequences"] == 9, fs["n_multi_junction_sequences"]
    assert fs["multi_junction_span"] == [2, 3], fs["multi_junction_span"]
    for s in art["per_sequence"]:
        assert len(set(s["junctions"])) == len(s["junctions"]), (
            f"{s['antisense_5to3']} lists the same junction more than once: {s['junctions']}")
        assert s["n_junctions"] == len(set(s["junctions"]))


def test_the_population_is_the_one_the_manuscript_quotes():
    """200 rows, 186 molecules, 40 source panels — derived, not read back. All of them moved
    together when the glob widened, and the figure legend is written off three of them.
    """
    art = B.build()
    assert art["observed"]["n_designs"] == 200
    assert art["observed_distinct_sequences"]["n_sequences"] == 186
    assert art["observed"]["mean"] == 9.5
    # ⚠ *Superseded, retained: 142.* The at-or-below count is not a property of the designs alone —
    # it is counted against the chance expectation, and on 2026-08-13 that expectation stopped being
    # an assumed 3e8-8e8 nt band and became a measured 718,571,139 nt span. A tighter expectation
    # (8.2 rather than an upper bound of 9.1) necessarily moves designs from below it to above it.
    # The observed counts themselves did not change; the line they are compared against did.
    assert art["observed"]["n_at_or_below_chance_upper"] == 135
    sources = {r["_source"] for r in art["per_design"]}
    assert len(sources) == 40
    assert not [s for s in sources if "deep500" in s]


def test_panels_at_other_geometries_are_excluded_from_the_sixteen_mer_corpus():
    """⛔ WITHOUT THIS FILTER THE MODULE DOES NOT BUILD AT ALL, AND THAT REFUSAL WAS CORRECT.

    The gap-length work emits `aso-insilico-evaluation-*-18mer-deep500.json` and `-20mer-` panels of
    seams this corpus already covers. `seam_identity` keys on the junction label — deliberately, so
    that a re-emission cannot escape grouping by renaming itself — so an 18-mer panel of the EWSR1
    e12 seam grouped with the 16-mer one, their counts differed, and `select_primary_panels` raised
    "two different evaluations, not a shallow and a deep reading of one". They ARE two different
    evaluations, because they are two different reagents, so the answer is to separate them before
    grouping rather than to choose between them.

    ⚠ THE FILTER IS `OLIGO_LEN`, THE SAME CONSTANT THE EXPECTATION USES, and that is what makes it a
    correctness guard rather than a scoping preference: every `expected` in this artifact is
    `chance_expectation(OLIGO_LEN, k)`, so an 18-mer observation admitted here would be divided by a
    16-mer expectation and the ratio would describe neither length.
    """
    import glob  # noqa: PLC0415
    import json as _json  # noqa: PLC0415
    import os as _os  # noqa: PLC0415
    import offtarget_chance_baseline as M  # noqa: PLC0415

    off = []
    rows = M.collect_observed(None, [], off)
    assert rows, "no observations were collected"
    assert all(len(r["antisense_5to3"]) == M.OLIGO_LEN for r in rows), sorted(
        {len(r["antisense_5to3"]) for r in rows})

    # something must actually have been excluded, or this asserts nothing
    assert off, "no other-geometry panel was set aside; the filter may be matching everything"
    assert {n for g in off for n in g["oligo_lens"]} == {18, 20}
    excluded = {g["panel"] for g in off}
    assert not (excluded & {r["_source"] for r in rows})

    # and the span attribution names a panel this corpus actually uses, not an 18-mer one
    nt, src = M.measured_transcriptome_nt()
    assert nt and src
    d = _json.load(open(_os.path.join(M.HERE, src), encoding="utf-8"))
    lens = M.panel_oligo_lens(d)
    assert not lens or lens == {M.OLIGO_LEN}, (src, sorted(lens))
    assert glob  # imported for parity with the module's own discovery path


# ═════════════════════════════════════════════════════════════════════════════════════════════
# The geometry exclusion is PUBLISHED, not printed (2026-08-14)
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_the_geometry_exclusions_are_in_the_artifact_not_only_on_stderr():
    """⛔ STDERR DOES NOT SURVIVE INTO THE RECORD, AND THIS DECISION HAD TO BE READ BACK.

    Twelve 18-mer and 20-mer panels are declined from this 16-mer corpus. Until this field existed
    they were announced only on stderr at generation time, and measured on the committed artifact
    beforehand: the twelve panels appeared nowhere in it and the strings "18mer"/"20mer" occurred
    zero times. So a reader of the deposited file could not tell that a longer-geometry panel of a
    seam existed and was declined — nor, the fail-quiet direction, that a seam was missing from the
    corpus entirely because it had only ever been evaluated at another geometry.

    ⚠ THE COLLAPSE READOUT IS DELIBERATELY STILL STDERR-ONLY and that is not an inconsistency: a
    collapsed panel is a re-emission of one the artifact DOES name in `per_design[]._source`, so
    the file can already answer it. An excluded panel is in the file nowhere.
    """
    art = B.build()
    assert "other_geometries" in art, "the geometry exclusion is not published at all"
    assert art["manuscript_oligo_len"] == B.OLIGO_LEN
    assert art["other_geometries"], (
        "no panel was declined, so this test asserts nothing about the corpus. If the 18-mer and "
        "20-mer panels have left the tree, this guard needs a different fixture.")
    for g in art["other_geometries"]:
        assert set(g) == {"panel", "oligo_lens"}, sorted(g)


def test_every_published_exclusion_is_really_a_different_geometry():
    """The published list is checked against the loader's MEASURED geometry, not against a name."""
    art = B.build()
    excluded = {g["panel"]: g["oligo_lens"] for g in art["other_geometries"]}
    measured = {s.name: s.geometry.oligo_len
                for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=MOD) for s in ss}
    for panel, lens in excluded.items():
        assert panel in measured, f"{panel} is published as excluded but is not on disk"
        assert measured[panel] != B.OLIGO_LEN, (
            f"{panel} is published as a different geometry but measures {measured[panel]}-mer, "
            f"which is this corpus's own length")
        assert lens == [measured[panel]], (panel, lens, measured[panel])

    # and nothing at the manuscript geometry was quietly swept in with them
    used = {r["_source"] for r in art["per_design"]}
    assert not (set(excluded) & used), "a panel is both used and published as excluded"


def test_the_exclusion_list_does_not_depend_on_the_caller_collecting_it():
    """⛔ `build()` AND `main()` MUST PRODUCE THE SAME BYTES.

    `collapsed` and `off_geometry` are out-parameters for the stderr readout. Once the exclusion
    became part of the ARTIFACT, an artifact whose content depended on whether a caller passed a
    list would make `--check` red on a tree nobody had touched — and
    `test_the_default_derivation_reproduces_the_committed_artifact` above compares exactly the
    no-argument call against the file that `main()` wrote.
    """
    bare = B.build()
    collected = B.build(None, [], [])
    assert bare["other_geometries"] == collected["other_geometries"]
    assert json.dumps(bare, indent=2) == json.dumps(collected, indent=2)


def test_the_committed_artifact_carries_the_exclusions():
    """The deposited bytes, not just the generator."""
    committed = json.loads(_committed())
    assert committed.get("other_geometries"), (
        "the committed chance-baseline artifact publishes no geometry exclusions. Re-run "
        "research/modalities/offtarget_chance_baseline.py.")
    assert committed["other_geometries"] == B.build()["other_geometries"]
