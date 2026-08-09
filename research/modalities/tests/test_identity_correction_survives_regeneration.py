#!/usr/bin/env python3
"""A medical-integrity marker on a GENERATED artifact must be emitted by its generator.

⛔ THE FAILURE THIS COMES FROM, TWICE IN ONE DAY (2026-08-09). A disputed cell-line identity is
flagged in every file that reads it, and `[O3]` in emc_systems_map_check.py fails the build when a
file classed as still bearing on the dispute stops carrying its marker. Two of those files are
GENERATED, and in both the marker had been added as an annotation-only HAND EDIT to the artifact:

  * `depmap-target-expression.json` — dropped by a regeneration, caught, fixed at its generator.
  * `emc-surfaceome-scan.json` — the identical defect in a sibling that was not checked at the same
    time, dropped by the next regeneration hours later, and it turned gate 3 red on a branch.

⭐ AN ANNOTATION-ONLY HAND EDIT TO A GENERATED ARTIFACT IS A REGRESSION WITH A FUSE ON IT. It sits
inert until somebody re-runs the generator — which can be weeks later — and then presents as an
unrelated CI job breaking the build, so the diagnosis starts in the wrong place. The corrected
WORDING regenerated correctly in both cases; only the marker that makes the correction auditable
was lost, which is the worst half to lose, because the file then reads as if it had never needed
one.

⚠ AND THE OBVIOUS AUDIT FOR THIS CANNOT WORK. The first sweep listed the artifacts that CONTAIN the
marker and checked their generators — which structurally cannot find a file that has already LOST
it, i.e. exactly the failure case. So this test sources its file list from the REGISTRY of what must
carry a marker, never from what currently does.

$0 — stdlib, reads committed files, runs anywhere.
"""
from __future__ import annotations

import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MAP = os.path.join(REPO, "research", "manuscripts", "emc-systems-map.json")

#: `unaffected` files are exempt by classification — they name the object without resting on it.
#: Everything else is classed as still bearing on the dispute and must show it.
MUST_SHOW = ("invalidated", "survives_relabelled")

#: ⚠ THE MARKER IS PER-ENTRY AND IS READ FROM THE REGISTRY, NEVER HARDCODED HERE. The first draft
#: of this file assumed every JSON artifact used `_identity_correction`; three of the eight use
#: different strings, and the test then failed a file that was perfectly correct while claiming it
#: was the [O3] failure. A guard that invents its own version of the rule it is guarding is worse
#: than none — it teaches the reader to distrust real failures. `[O3]` reads this same field.


def _registry_entries():
    if not os.path.exists(MAP):
        return []
    with open(MAP, encoding="utf-8") as fh:
        m = json.load(fh)
    out = []
    for obj in m.get("objects", []):
        if obj.get("status") != "identity_disputed":
            continue
        for rb in obj.get("read_by", []):
            f = rb.get("file")
            marker = rb.get("correction_marker")
            if f and f.endswith(".json") and rb.get("classification") in MUST_SHOW and marker:
                out.append((obj["id"], f, rb["classification"], marker))
    return out


def _generator_for(rel_json):
    """The generator a repo artifact is produced by, under this repository's naming convention.

    ⚠ Convention-based and deliberately conservative: a `.json` with no same-named `.py` beside it
    is treated as NOT generated and skipped, because asserting a generator that does not exist would
    make this test fail on hand-maintained registries — of which the read_by list contains several
    (systems/graph/*.json are edited directly and must stay editable).
    """
    d, base = os.path.split(rel_json)
    cand = os.path.join(REPO, d, base[:-len(".json")].replace("-", "_") + ".py")
    return cand if os.path.exists(cand) else None


def test_the_registry_still_names_at_least_one_generated_artifact():
    """⛔ A GUARD WHOSE INPUT LIST SILENTLY EMPTIES IS WORSE THAN NO GUARD — it goes green forever.
    If the disputed-identity registry or the naming convention ever changes shape, fail loudly here
    rather than letting every assertion below vacuously pass."""
    pairs = [(f, _generator_for(f)) for _, f, _, _ in _registry_entries()]
    generated = [f for f, g in pairs if g]
    assert generated, (
        "no registry-listed artifact resolved to a generator. Either the disputed-identity registry "
        "moved, or the <name>.json -> <name>.py convention did. Both make this test vacuous.")


@pytest.mark.parametrize("oid,rel,classification,marker",
                         _registry_entries() or [(None, None, None, None)])
def test_a_generated_artifact_that_must_carry_the_marker_has_it_emitted_by_its_generator(
        oid, rel, classification, marker):
    """The marker must live in the CODE, not only in the artifact — otherwise the next run drops it.

    ⚠ Both halves are asserted, and the second is the one that actually bites. A marker present in
    the artifact today proves nothing about tomorrow: it is exactly what both regressions looked
    like the day before they fired.
    """
    if rel is None:
        pytest.skip("disputed-identity registry not present")
    gen = _generator_for(rel)
    if gen is None:
        pytest.skip(f"{rel} is not generated by convention (hand-maintained registry)")

    path = os.path.join(REPO, rel)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            assert marker in fh.read(), (
                f"{rel} is classed `{classification}` for {oid} and does not carry {marker!r}. "
                f"This is the [O3] failure itself — a file using a disputed-identity model with no "
                f"visible statement that the identity is disputed.")

    with open(gen, encoding="utf-8") as fh:
        assert marker in fh.read(), (
            f"{rel} must carry {marker!r} but its generator {os.path.relpath(gen, REPO)} does NOT "
            f"emit it, so the marker is a HAND EDIT ON A GENERATED FILE and the next run of that "
            f"generator will silently delete a medical-integrity marker. Move it into the generator; "
            f"do not re-patch the artifact.")
