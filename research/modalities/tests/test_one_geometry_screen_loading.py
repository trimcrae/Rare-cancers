"""No module may discover ASO screen artifacts by pattern. There is ONE loader.

★★ WHY THIS EXISTS — the same generator as `test_no_hand_rolled_publish.py`, which this file is
modelled on: fix the instance, write the rule down as a comment at that instance, and then wait for
every remaining instance to fail in production one at a time.

THE INSTANCE (2026-08-13). Screens of different gapmer geometries share one filename pattern.
`aso_per_junction_table` globbed `junction-aso-offtarget-*deep500*.json`, got 18-mer 5-8-5 and
20-mer 5-10-5 screens along with the 16-mer 5-6-5 panel, and applied
`junction_aso_offtarget.GAP_REGION_1BASED` — the 5-6-5 span (6, 11) — to all of them. An 18-mer's
gap-paired hits were counted over six of its eight catalytic bases, and `best_available` moved at
the *EWSR1* e12, *FUS* e10 and *TAF15* e11 seams: the three clinically central rows, the ones the
manuscript recommends. It produced a WRONG NUMBER, not a crash. A human caught it.

⛔ THE COMMENT-AT-THE-SITE FIX PROTECTS ONE CALL SITE. A guard was written into that one consumer.
Measured while writing this file, the same defect was latent in six other modules and LIVE in two
more that nobody had looked at:

  * `junction_aso_locus_collapse` — a re-run would have moved `n_deep_oligos_uncensored` 187 -> 303
    and the median inflation factor 5.52 -> 5.14, both manuscript-facing.
  * `junction_aso_offtarget.grade_panel` — wrote THIS PROCESS'S geometry into every graded
    re-score, so step 0 of `scripts/regenerate_aso_chain.sh` (which rescores every screen it finds)
    would have published 18-mer designs under `oligo_len: 16`, `gap_region_1based: [6, 11]`.
    Reproduced end to end before the fix.
  * `offtarget_chance_baseline` — hard-coded `OLIGO_LEN = 16` beside a glob that matched 18-mer and
    20-mer panels. Its seam-identity guard turned that into a hard failure rather than a wrong
    number, so on this branch the artifact had become un-regenerable.

So the rule stops being prose and becomes a checked invariant over ALL sites, which is what this
file is: every python module that reads these artifacts goes through
`aso_screen_sets.load_screens` / `load_by_geometry`, which return one geometry or a mapping keyed
by geometry and never one mixed bag.

⚠ SCOPE, STATED RATHER THAN IMPLIED. This scans PYTHON. Workflow YAML and shell that `cp`, `find`
or `git add` these files are transport: they move bytes and compute no quantity, so they cannot
produce a number measured against the wrong window. `scripts/regenerate_aso_chain.sh` DOES feed
every screen it finds into `--rescore`, and that is exactly why the fix there is in `grade_panel`
— the producer, in python — rather than in the shell that calls it.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

MODALITIES = Path(__file__).resolve().parents[1]
REPO = MODALITIES.parents[1]
sys.path.insert(0, str(MODALITIES))

import aso_screen_sets as ass  # noqa: E402

LOADER = "research/modalities/aso_screen_sets.py"

#: Directories with no first-party source in them.
_SKIP_DIRS = {".git", ".claude", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
              ".pytest_cache", "site-packages"}

#: ⛔ THE REGISTERED EXCEPTIONS — EACH WITH A WRITTEN REASON, AND EACH CHECKED.
#: An entry is not a pardon: `test_a_registered_exception_cannot_outlive_the_pattern_it_names`
#: fails if the module stops containing a discovery pattern, so an entry cannot rot into a
#: permanent hole that a NEW glob could then slip through under.
#: ⚠ THE BAR FOR AN ENTRY IS "IT COMPUTES NO PER-DESIGN QUANTITY". A module that hashes files, or
#: grades a declared seam, does not index into an oligonucleotide and cannot apply the wrong gap
#: window. A module that counts, ranks, collapses or scores designs can, and does not belong here
#: whatever its reason sounds like.
ALLOWED: dict[str, str] = {
    LOADER: (
        "the loader itself owns the patterns — this is the one home they are allowed to live in"),
    "research/manuscripts/aso_archive_manifest.py": (
        "its `patterns` lists are the DEPOSIT SPEC: the exact file globs published to the archive, "
        "used to hash bytes. Hashing is geometry-blind by nature and a deposit that silently "
        "stopped shipping a geometry would be a worse defect than the one this guard prevents. "
        "⚠ The part of that module that COUNTS screens does not rely on this exception — "
        "`_screen_coverage` goes through the loader and reports per geometry, because "
        "`n_screens_committed` is quoted as the size of the panel the manuscript describes."),
    "research/modalities/tests/test_junction_seam_retraction.py": (
        "its patterns are QUOTATIONS of `.github/workflows/aso-offtarget.yml` — the test asserts "
        "that each staging glob appears inside the sweep guard in that YAML. It reads no artifact "
        "and computes no per-design quantity; it is a string search over a workflow file, and the "
        "strings have to match the workflow's spelling rather than the loader's."),
}


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE SCANNER
# ═════════════════════════════════════════════════════════════════════════════════════════════
def _docstring_nodes(tree: ast.AST) -> set[int]:
    """`id()` of every docstring literal in the module.

    ⛔ DOCSTRINGS ARE PROSE AND MUST NOT BE SCANNED — the precedent is
    `test_no_hand_rolled_publish.test_the_primitive_exists_and_is_executable`, whose comment reads
    "COMMENTS STRIPPED FIRST … a naive scan finds the string it is testing for and fails on the
    documentation rather than on the code." Exactly that happened here on the first run: this
    file's own header, which quotes the offending glob in order to explain it, was reported as a
    violation. The incident record must survive; the CODE must not contain the operation.
    ⚠ Comments need no handling — the AST never sees them.
    """
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None) or []
        if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            out.add(id(body[0].value))
    return out


def _string_templates(tree: ast.AST):
    """Every non-docstring string literal in the module, f-strings reconstructed as templates.

    An f-string is reconstructed with `{}` where an expression was, so a
    `f"<prefix>-{tag}.json"` is judged as `<prefix>-{}.json` — a concrete single filename with a
    hole in it, which is a targeted read and not discovery.
    ⚠ AND ITS CONSTANT PIECES ARE NOT ALSO YIELDED SEPARATELY. `ast.walk` descends into a
    `JoinedStr`, so a naive walk yielded the bare fragment `<prefix>-` as well as the whole
    template — and a bare prefix is exactly what this scanner treats as discovery, so every
    templated single-file read was flagged. Measured on the first run of this file.
    """
    docstrings = _docstring_nodes(tree)
    stack = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, ast.JoinedStr):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(v.value)
                else:
                    parts.append("{}")
                    stack.extend(ast.iter_child_nodes(v))   # expressions inside the holes
            yield "".join(parts), getattr(node, "lineno", 0)
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                yield node.value, getattr(node, "lineno", 0)
            continue
        stack.extend(ast.iter_child_nodes(node))


#: Characters a filename-shaped token may contain. `*?[]` are glob metacharacters and `{}<>` are
#: the two placeholder spellings used for a single templated filename; everything else ends the
#: token, which is what stops a sentence of prose from being read as one enormous pattern.
_TOKEN_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-*?[]{}<>")


def _is_discovery(text: str) -> bool:
    """Does this literal select MORE THAN ONE artifact of a screen family?

    Two shapes count, and between them they cover every way these files have actually been reached:

      * a glob — anything containing `*`, `?` or `[` inside the filename token;
      * a bare PREFIX — a token that starts a family name and does not end in `.json`, which is
        what `startswith(...)`, `os.listdir` filtering and `str.removeprefix` use.

    A complete concrete filename is NOT discovery: reading one named artifact cannot mix
    geometries, and flagging it would make the guard unusable and therefore switched off.

    ⚠ THE JUDGEMENT IS ON THE FILENAME TOKEN, NOT ON THE REST OF THE LINE. The first version tested
    everything after the prefix to the end of the literal, which flagged
    `hybrid_intron.py`'s artifact note — a sentence that happens to list four concrete filenames
    inside a parenthesis. A guard that fires on prose gets switched off, and then the real globs go
    unwatched with it.
    """
    for prefix in ass.FAMILY_PREFIXES:
        i = text.find(prefix)
        if i < 0:
            continue
        j = i
        while j < len(text) and text[j] in _TOKEN_CHARS:
            j += 1
        token = text[i:j]
        if any(ch in token for ch in "*?["):
            return True
        if not token.endswith(".json"):
            return True
    return False


def _python_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                yield Path(dirpath) / fn


def discovering_modules(root: Path | None = None) -> dict[str, list[tuple[str, int]]]:
    """{repo-relative module path: [(literal, line), ...]} for every module that discovers.

    ⛔ AN UNPARSEABLE FILE IS A FINDING, NOT A SKIP. A module the AST cannot read is a module this
    scanner has not checked, and silently skipping it is how a guard comes to vouch for a path it
    never inspected — the exact blind spot `test_no_hand_rolled_publish` records for its own
    YAML-only registry. It is reported under a sentinel so it fails loudly.
    """
    root = REPO if root is None else root
    found: dict[str, list[tuple[str, int]]] = {}
    for path in _python_files(root):
        rel = str(path.relative_to(root))
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(path))
        except (OSError, ValueError, SyntaxError) as exc:
            found[rel] = [(f"⛔ UNPARSEABLE: {exc}", 0)]
            continue
        hits = [(t, ln) for t, ln in _string_templates(tree) if _is_discovery(t)]
        if hits:
            found[rel] = sorted(set(hits))
    return found


def _violations() -> list[tuple[str, list[tuple[str, int]]]]:
    return sorted((m, h) for m, h in discovering_modules().items() if m not in ALLOWED)


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE GUARD
# ═════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("module,hits", _violations(), ids=[m for m, _ in _violations()])
def test_no_module_discovers_screen_artifacts_outside_the_loader(module, hits):
    """⛔ THE GUARD. Reach these artifacts through `aso_screen_sets`, not through a pattern.

    If this fails on a module you just wrote, replace the glob with

        import aso_screen_sets as ass
        for screen in ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN):
            ...                                  # screen.artifact, screen.geometry, screen.name

    and take the gap window from `screen.geometry.gap_region_1based` rather than from
    `junction_aso_offtarget.GAP_REGION_1BASED`, which is whatever geometry YOUR process's
    environment built. If you genuinely need more than one geometry — only
    `aso_gap_length_tradeoff` does — use `ass.load_by_geometry(...)`, which hands back a mapping
    keyed by geometry so that combining two is something you have to write down.
    """
    shown = ", ".join(f"{t!r}:{ln}" for t, ln in hits[:4])
    pytest.fail(
        f"{module} discovers ASO screen artifacts by pattern ({shown}). Those patterns match more "
        f"than one gapmer geometry: applying one geometry's gap span to another's designs counted "
        f"an 18-mer's gap-paired hits over six of its eight catalytic bases and moved the "
        f"recommended reagent at three clinically central seams. Go through {LOADER}.")


def test_the_repository_is_clean_of_direct_discovery():
    """⚠ THE PARAMETRIZED GUARD ABOVE SKIPS WHEN THERE ARE NO VIOLATIONS, and "0 collected" reads
    identically whether the repository is clean or the scanner stopped resolving files. This states
    the clean case affirmatively, so a green build is a reading rather than a silence."""
    violations = _violations()
    assert not violations, "\n".join(f"{m}: {h}" for m, h in violations)
    # …and the walk really did look at something, so "clean" is not "found nothing to look at"
    assert len(discovering_modules()) >= len(ALLOWED), (
        "the scanner sees fewer modules than the registered exceptions — the walk has broken")


def test_a_registered_exception_cannot_outlive_the_pattern_it_names():
    """⚠ A registered exception that no longer describes reality is a hole the guard cannot see.

    A module that stopped containing a discovery pattern must leave this list, or a NEW glob added
    to it tomorrow would inherit a pardon written for something else.
    """
    live = set(discovering_modules())
    stale = sorted(set(ALLOWED) - live)
    assert not stale, (
        f"these entries no longer describe a module that discovers screen artifacts — delete them "
        f"so the guard tightens: {stale}")


def test_every_registered_exception_states_a_reason():
    for module, reason in ALLOWED.items():
        assert len(reason.split()) >= 8, (
            f"{module} is exempted with no usable reason. An exception without a written reason is "
            f"indistinguishable from an oversight, and is what turns a guard into a formality.")


def test_no_module_is_unparseable_to_the_scanner():
    """A file the AST could not read is a file this guard did not check."""
    bad = {m: h for m, h in discovering_modules().items()
           if any(t.startswith("⛔ UNPARSEABLE") for t, _ in h)}
    assert not bad, f"the scanner could not parse: {sorted(bad)}"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ A GUARD THAT CANNOT GO RED IS WORSE THAN NO GUARD — the scanner is tested against planted code
# ═════════════════════════════════════════════════════════════════════════════════════════════
def _plant(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


#: ⚠ BUILT AT RUNTIME FROM THE LOADER'S OWN PREFIXES, so this test file contains no discovery
#: literal of its own and is therefore subject to its own guard like everything else. A scanner
#: that had to be exempted from itself would be one exemption away from being exempted for real.
_GLOB = ass.FAMILY_PREFIXES[0] + "-*deep500*.json"
_PREFIX = ass.FAMILY_PREFIXES[0] + "-"
_CONCRETE = ass.FAMILY_PREFIXES[0] + "-e12n3.json"


def test_the_scanner_finds_a_deliberately_planted_glob(tmp_path):
    """★★ THE SELF-TEST. A scanner that silently matches nothing passes forever while protecting
    nothing — which is precisely how the geometry defect reached print in the first place."""
    _plant(tmp_path, "planted_offender.py",
           "import glob, os\n"
           "def rows(here):\n"
           f"    return sorted(glob.glob(os.path.join(here, {_GLOB!r})))\n")
    found = discovering_modules(tmp_path)
    assert "planted_offender.py" in found, (
        "the scanner did not see a raw glob of the screen artifacts. It is passing vacuously.")


def test_the_scanner_finds_a_planted_startswith_prefix(tmp_path):
    """⛔ A PREFIX IS A GLOB WITH EXTRA STEPS, and it is the shape the real code actually used.

    `aso_gap_length_tradeoff._discover` walked `os.listdir` and filtered on
    `fn.startswith(prefix)`; a detector that only looked for `*` would have called that module
    clean while it read every geometry on disk."""
    _plant(tmp_path, "planted_prefix.py",
           "import os\n"
           "def rows(here):\n"
           f"    return [f for f in os.listdir(here) if f.startswith({_PREFIX!r})]\n")
    found = discovering_modules(tmp_path)
    assert "planted_prefix.py" in found, (
        "the scanner missed a prefix-style discovery — the exact shape one real consumer used")


def test_the_scanner_finds_a_planted_pathlib_glob(tmp_path):
    """The same defect written with `Path.glob` instead of the `glob` module."""
    _plant(tmp_path, "planted_pathlib.py",
           "from pathlib import Path\n"
           "def rows(here):\n"
           f"    return sorted(Path(here).glob({_GLOB!r}))\n")
    assert "planted_pathlib.py" in discovering_modules(tmp_path)


def test_the_scanner_does_not_fire_on_one_named_artifact(tmp_path):
    """⚠ AND THE OTHER DIRECTION, WHICH DECIDES WHETHER THE GUARD SURVIVES CONTACT.

    Reading one named file cannot mix geometries. A guard that went red on
    `json.load(open("junction-aso-offtarget-e12n3.json"))` would be switched off within a week, and
    then the real globs would go unwatched with it."""
    _plant(tmp_path, "planted_innocent.py",
           "import json, os\n"
           "def one(here):\n"
           f"    return json.load(open(os.path.join(here, {_CONCRETE!r})))\n")
    assert "planted_innocent.py" not in discovering_modules(tmp_path)


def test_the_scanner_does_not_fire_on_an_f_string_naming_one_artifact(tmp_path):
    """`f"...-{tag}.json"` selects one file per call, which is a targeted read, not discovery."""
    _plant(tmp_path, "planted_template.py",
           "import json, os\n"
           "def one(here, tag):\n"
           f"    return json.load(open(os.path.join(here, f'{_PREFIX}{{tag}}.json')))\n")
    assert "planted_template.py" not in discovering_modules(tmp_path)


def test_the_scanner_covers_the_whole_repository_not_only_modalities():
    """⚠ THE BLIND SPOT THAT THIS GUARD'S MODEL ALREADY PAID FOR ONCE. `KNOWN_HAND_ROLLED` read
    workflow YAML only, so a publisher living in python was outside its field of view and its green
    VOUCHED for a path it could not inspect. Two of this defect's consumers live under
    `research/manuscripts/`, so a modalities-only walk would have reported clean over both."""
    seen = {str(p.relative_to(REPO)) for p in _python_files(REPO)}
    for must in ("research/manuscripts/submission_tables.py",
                 "research/manuscripts/aso_archive_manifest.py",
                 "research/modalities/junction_aso_locus_collapse.py",
                 "scripts/affected_tests.py"):
        assert must in seen, f"the scanner's walk does not reach {must}"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE LOADER'S OWN INVARIANTS — the properties the guard above is pointing everything at
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_there_is_no_default_geometry():
    """⛔ A DEFAULT IS HOW THIS HAPPENS AGAIN. The module that has not thought about geometry is
    exactly the module that takes the default, and the default is right until the day it is not."""
    with pytest.raises(TypeError):
        ass.load_screens(ass.MANUSCRIPT_GEOMETRY)              # family omitted
    with pytest.raises(ass.GeometryError):
        ass.load_screens(None, ass.BLAST_SCREEN)               # "any geometry" is refused
    with pytest.raises(TypeError):
        ass.load_screens(16, ass.BLAST_SCREEN)                 # a bare int is not a geometry


def test_a_screen_set_cannot_be_handed_a_second_geometry():
    """The type is the guard: there is no `+`, no `extend`, and the constructor refuses."""
    with pytest.raises(ass.GeometryError):
        ass.ScreenSet(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN,
                      [ass.Screen("x.json", {}, ass.GEOMETRY_18MER_585, ass.BLAST_SCREEN, {})],
                      str(MODALITIES))
    for forbidden in ("__add__", "extend", "append", "update"):
        assert not hasattr(ass.ScreenSet, forbidden), (
            f"ScreenSet grew `{forbidden}` — a convenience method for merging two geometries is "
            f"the first step back to a mixed bag")


def _copy_one(tmp_path: Path, name: str) -> Path:
    shutil.copy(MODALITIES / name, tmp_path / name)
    return tmp_path / name


def test_geometry_is_measured_from_the_designs_not_from_the_filename(tmp_path):
    """★★ THE PROPERTY THE WHOLE FIX RESTS ON. Filenames carry `-18mer-` markers today; nothing
    enforces that, and the pre-2026-08-13 screens carry no geometry block at all."""
    src = MODALITIES / "junction-aso-offtarget-e12n3-18mer-deep500.json"
    lying = tmp_path / "junction-aso-offtarget-e12n3-deep500-b9.json"   # says nothing about 18
    shutil.copy(src, lying)
    by = ass.load_by_geometry(ass.BLAST_SCREEN, root=str(tmp_path))
    assert list(by) == [ass.GEOMETRY_18MER_585], (
        f"an 18-mer screen under a name with no geometry marker was read as {list(by)}")
    assert by[ass.GEOMETRY_18MER_585].gap_region_1based == (6, 13)


def test_a_screen_whose_stated_gap_region_disagrees_with_its_designs_is_refused(tmp_path):
    """⛔ THE SILENT FORM OF THE BUG. A screen graded against one window and counted against another
    crashes nothing: every gap-paired count is simply measured over the wrong columns."""
    src = MODALITIES / "junction-aso-offtarget-e12n3-18mer-deep500.json"
    d = json.loads(src.read_text(encoding="utf-8"))
    d["method"]["gap_region_1based"] = [6, 11]                 # a 16-mer's gap on 18-mer designs
    (tmp_path / src.name).write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ass.GeometryError, match="gap_region_1based"):
        ass.load_by_geometry(ass.BLAST_SCREEN, root=str(tmp_path))


def test_a_screen_holding_two_design_lengths_is_refused(tmp_path):
    """No single dispatch tiles two geometries, so such a file is internally inconsistent and
    picking one of its two halves would be choosing which to believe."""
    src = MODALITIES / "junction-aso-offtarget-e12n3-deep500-b1.json"
    d = json.loads(src.read_text(encoding="utf-8"))
    d["oligos"][0]["antisense_5to3"] = d["oligos"][0]["antisense_5to3"] + "AA"
    (tmp_path / src.name).write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ass.GeometryError):
        ass.load_by_geometry(ass.BLAST_SCREEN, root=str(tmp_path))


def test_loading_nothing_raises_rather_than_reporting_over_an_empty_set(tmp_path):
    """A consumer that silently measures nothing is the defect this repository keeps paying for."""
    with pytest.raises(ass.GeometryError, match="allow_empty"):
        ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, root=str(tmp_path))
    empty = ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, root=str(tmp_path),
                             allow_empty=True)
    assert len(empty) == 0


def test_a_graded_rescore_states_the_screens_geometry_not_the_process_geometry(tmp_path):
    """★★ THE SECOND LIVE INSTANCE, PINNED. `grade_panel` wrote `ja.OLIGO_LEN` and
    `GAP_REGION_1BASED` — this process's geometry — into every re-score, and step 0 of
    `scripts/regenerate_aso_chain.sh` rescores every screen it finds. Before the fix, grading
    `junction-aso-offtarget-e12n3-18mer-deep500.json` produced an artifact stating `oligo_len: 16`,
    `gap_region_1based: [6, 11]` and `>= 14/16 identical` over designs measured at 18."""
    import junction_aso_offtarget as jo                                  # noqa: PLC0415
    for name, want_len, want_gap in (
            ("junction-aso-offtarget-e12n3-18mer-deep500.json", 18, [6, 13]),
            ("junction-aso-offtarget-e12n3-20mer-deep500.json", 20, [6, 15]),
            ("junction-aso-offtarget-e12n3-deep500-b1.json", 16, [6, 11])):
        screen = json.loads((MODALITIES / name).read_text(encoding="utf-8"))
        art = jo.grade_panel(screen)
        assert art["oligo_len"] == want_len, name
        assert art["gap_region_1based"] == want_gap, name
        assert art["near_match_threshold"] == f">= {want_len - 2}/{want_len} identical", name
        seqs = {s for rows in art["per_oligo"].values() for s in rows}
        assert {len(s) for s in seqs} == {want_len}, name


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE COMMITTED TREE — data assertions, so they cannot gate anything (see conftest)
# ═════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.committed_artifact
def test_every_committed_artifact_agrees_with_its_own_stated_geometry():
    """The agreement assertion, exercised over the real tree rather than only over a fixture.

    ⚠ It passes today on all committed screen artifacts, which is the point: the check costs
    nothing now and is the only thing standing between a future divergence and a wrong number.
    """
    total = 0
    for family in ass.FAMILIES:
        for geom, screens in ass.load_by_geometry(family, root=str(MODALITIES)).items():
            for s in screens:
                total += 1
                assert s.geometry == geom
                assert {len(x) for x in family.designs(s.artifact)} == {geom.oligo_len}, s.name
    assert total > 100, f"only {total} artifacts were read — the walk has narrowed"


@pytest.mark.committed_artifact
def test_no_screen_artifact_on_disk_falls_outside_every_family():
    """⛔ THE FAIL-QUIET DIRECTION. A file no family matches is invisible to every consumer that
    goes through the loader, and invisible is how a screen stops being counted silently.

    Two are legitimately unclaimed and both are pinned here: the un-suffixed legacy pre-panel
    screen, which the collapse population has always excluded (widening that population is a data
    decision with manuscript consequences, not a glob tidy-up), and the derived locus-collapse
    artifact, which is an output rather than a screen.
    """
    assert ass.unclaimed_files(str(MODALITIES)) == [
        "junction-aso-offtarget-locus-collapse.json",
        "junction-aso-offtarget.json",
    ]


@pytest.mark.committed_artifact
def test_the_manuscript_geometry_is_the_one_the_committed_artifacts_report():
    """The panel the paper describes, asserted against the artifacts rather than against a memory.

    ⚠ THE ARTIFACT'S FIELD NAMES ARE THE ONES ALREADY PUBLISHED — `manuscript_oligo_len` and
    `other_geometries` — and this test reads them rather than renaming them. Introducing the
    loader is a refactor, and a refactor that also churns a deposited schema makes the byte-identity
    check that guards it unusable.
    """
    collapse = json.loads(
        (MODALITIES / "junction-aso-offtarget-locus-collapse.json").read_text(encoding="utf-8"))
    assert collapse["manuscript_oligo_len"] == ass.MANUSCRIPT_GEOMETRY.oligo_len
    # every screen it counted really is that geometry, measured rather than trusted
    for row in collapse["screens"] + collapse["deep_screens"]:
        assert row["oligo_len"] == ass.MANUSCRIPT_GEOMETRY.oligo_len, row["screen"]
    # and the other geometries are NAMED rather than silently dropped
    assert collapse["other_geometries"], (
        "the collapse artifact reports no other geometry on a tree that holds fifteen of them — "
        "a set-aside that is not published reads exactly like a file that was never written")
    assert {r["oligo_len"] for r in collapse["other_geometries"]} == {18, 20}
