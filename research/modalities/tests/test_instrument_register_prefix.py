"""The instrument register may never go back to a `C`-prefixed id.

⛔ WHAT WAS WRONG (roadmap §10.1a `Q22`, §0.6). Two registers were both written `C`-and-a-number: the
roadmap's CONFIGURATION items (`C1`..`C25`, unpadded) and the instrument-options register (`C01`..`C16`,
zero-padded). Zero-padding was the tell and **it ran out at ten** -- `C10` `C11` `C12` `C13` `C14` `C15`
`C16` existed in both schemes spelled identically. Worst case `C14`: a pose-recovery criterion that
decides `panel_readable` and adjudicates four SI clauses, and a priced GPU benchmark.

`systems/CONVENTIONS.md` §1 already REGISTERED the fix (`IC-1`..`IC-16`) and nobody had performed it --
which is exactly what `Q22` says: *the disambiguation rule is registered, the renumbering is not.*
`instrument_register_renumber.py` performed it; this is what stops it coming back.

⚠ THE GUARD IS NARROW ON PURPOSE. It does NOT forbid `C10` repo-wide -- that string is a configuration id
in hundreds of legitimate places and an ATOM NAME in ~9,600 more under `results/`. What it forbids is the
register itself, or the register's own artifacts, going back to the colliding spelling.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MODALITIES))
MODULE = os.path.join(MODALITIES, "instrument_register_renumber.py")
REGISTER_JSON = os.path.join(MODALITIES, "instrument-options.json")
REGISTER_MD = os.path.join(MODALITIES, "instrument-options.md")

_spec = importlib.util.spec_from_file_location("instrument_register_renumber", MODULE)
irr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(irr)

NEW_ID = re.compile(r"\bIC-(\d{1,2})\b")


def test_every_register_id_uses_the_new_prefix():
    d = json.load(open(REGISTER_JSON, encoding="utf-8"))
    ids = [c["id"] for c in d["candidates"]]
    assert ids == ["IC-%d" % i for i in range(1, len(ids) + 1)], ids
    assert all(NEW_ID.fullmatch(i) for i in ids), ids


def test_the_register_files_carry_no_colliding_id_at_all():
    """⛔ THE CORE GUARD. A single `C0N` or `C1N` back in the register's own files means the collision has
    been reintroduced at its source, and every citation of it inherits the ambiguity."""
    for path in (REGISTER_JSON, REGISTER_MD):
        body = open(path, encoding="utf-8").read()
        bad = sorted(set(irr.ANY_ID.findall(body)))
        assert not bad, (
            "%s carries colliding instrument ids again: %r. The register uses `IC-1`..`IC-16` "
            "(systems/CONVENTIONS.md §1). Re-run "
            "`python3 research/modalities/instrument_register_renumber.py --audit`."
            % (os.path.relpath(path, ROOT), bad))


def test_the_number_is_unpadded_after_the_prefix():
    """`IC-4`, never `IC-04`. Padding was the failed tell; carrying it forward would preserve the very
    thing being removed, and would make `IC-04` and `IC-4` two spellings of one id."""
    for path in (REGISTER_JSON, REGISTER_MD):
        body = open(path, encoding="utf-8").read()
        assert not re.search(r"\bIC-0\d\b", body), (
            "%s uses a zero-padded IC id" % os.path.relpath(path, ROOT))


def test_the_target_spelling_is_the_one_the_conventions_document_registers():
    """⭐ THE PREFIX WAS NOT CHOSEN BY THE MIGRATION SCRIPT. If CONVENTIONS ever registers a different
    spelling, this fails rather than letting two authorities disagree silently."""
    conv = open(os.path.join(ROOT, "systems", "CONVENTIONS.md"), encoding="utf-8").read()
    assert "`IC-1`…`IC-16`" in conv or "`IC-1`...`IC-16`" in conv, (
        "systems/CONVENTIONS.md no longer registers `IC-1`…`IC-16` as the instrument-options spelling, so "
        "the migration and the convention have diverged -- reconcile them, do not edit this test")
    assert irr.MAP["C01"] == "IC-1" and irr.MAP["C16"] == "IC-16", irr.MAP


def test_the_collision_record_still_says_what_it_said():
    """⛔ THE MIGRATION MUST NOT ERASE ITS OWN EVIDENCE. §0.6's table shows `C10` meaning two different
    things, and §3b's bullet says "`C` collides ... the options registers already use `C01`…`C09`".
    Those old spellings are the record; a migration that rewrote them would document nothing."""
    road = open(os.path.join(ROOT, "research", "manuscripts", "nr4a3-program-map.md"),
                encoding="utf-8").read()
    assert "spelled IDENTICALLY" in road
    assert "`C01`…`C09`" in road or "`C01`..`C09`" in road, (
        "the §3b collision bullet lost the old spellings it quotes as evidence")
    conv = open(os.path.join(ROOT, "systems", "CONVENTIONS.md"), encoding="utf-8").read()
    assert "`C01`…`C16` (zero-padded)" in conv, "CONVENTIONS lost the `was written` column"


def test_the_classifier_never_touches_an_atom_name():
    """⚠ THE BUG THE AUDIT CAUGHT, PINNED. PDB atom names are spelled exactly `C01`, `C02`, `C07`. The
    first classifier said "padded => register, always" on §0.6's own authority and would have rewritten
    coordinate records."""
    sample = '{"name": "C01", "elem": "C", "xyz": [1.0, 2.0, 3.0]}'
    m = next(irr.ANY_ID.finditer(sample))
    assert irr.classify("some/other/file.json", sample, m) == "CONFIGURATION"
    log = "vhl: receptor entry 6GMN chains ['A'] ligand F4E n_heavy=12 exit atom C07 exposure 3.98 A"
    m = next(irr.ANY_ID.finditer(log))
    assert irr.classify("some/other/file.json", log, m) == "CONFIGURATION"


def test_an_ambiguous_high_id_is_only_promoted_by_an_explicit_marker():
    """`C14` alone stays a configuration item. Only *"instrument candidate `C14`"* is the register's."""
    bare = "the pose-recovery criterion `C14` decides panel_readable"
    m = next(irr.ANY_ID.finditer(bare))
    assert irr.classify("research/manuscripts/some.md", bare, m) == "CONFIGURATION"
    marked = "the priced benchmark, instrument candidate `C14`, is unrun"
    m = next(irr.ANY_ID.finditer(marked))
    assert irr.classify("research/manuscripts/some.md", marked, m) == "REGISTER"


def test_the_migration_is_idempotent_over_the_repo():
    """A second `--apply` must be a no-op. If it is not, the classifier is finding new work each run and
    the rename is not converging."""
    for f in irr.tracked_files():
        p = os.path.join(ROOT, f)
        try:
            t = open(p, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if f == irr.ROADMAP or f in irr.NEVER_REWRITE:
            continue
        new, n = irr.rewrite(f, t)
        assert new == t, ("%s would still be rewritten by --apply (%d occurrence(s)) -- the migration "
                          "has not converged" % (f, n))


def test_the_routed_roadmap_edits_are_all_accounted_for():
    """The roadmap is never rewritten mechanically. Its edits are routed, and a routed edit whose anchor
    is dead is the failure `map_edit_anchors` exists to catch."""
    p = os.path.join(ROOT, "research", "manuscripts", "program", "instrument-register-prefix-map-edits.json")
    if not os.path.exists(p):
        pytest.skip("the routed block has not been emitted in this checkout")
    d = json.load(open(p, encoding="utf-8"))
    s = d["anchor_summary"]
    assert not s["not_found"], s["not_found"]
    assert not s["ambiguous"], s["ambiguous"]
    assert s["all_accounted"] is True
    assert d["_section_0_6_is_excluded"], "the exclusion of the collision record is not stated"
