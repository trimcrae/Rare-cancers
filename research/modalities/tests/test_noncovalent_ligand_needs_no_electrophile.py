"""A ligand with no electrophile is a FACT ABOUT THE LIGAND, not a build failure.

★★ MEASURED, on the sensitivity control's first MD leg (Vast 46531433, $0.0154, 2026-08-01):

    File ".../nrv04_covalent_md.py", line 449, in _electrophile_and_neighbour
    File ".../nrv04_ligands.py", line 57, in electrophile_atom_index
    ValueError: no enone (C=C-C=O) found — cannot locate the celastrol electrophile

That control stages **PRT3789** (CCD `A1BB4`), a NON-COVALENT SMARCA2 degrader — deliberately, and by the
same design its driver is `nrv04_covalent_md` *verbatim*, because "a sensitivity control that ran a modified
driver would calibrate a readout the program does not use" (`selcal_vast_launch.__doc__`). So the two
requirements were in direct conflict: run this driver unchanged, on a ligand it refused to parse.

THE RESOLUTION IS THE FILE'S OWN PRECEDENT, ONE CALL EARLIER. On 2026-07-31 `_frozen_cys_by_construct` was
found to be called on every leg while being USED only by the covalent restraint and the C551A mutation; it
became conditional, and its absence recorded. `_electrophile_and_neighbour` has exactly three callers:

    _covalent_indices          the covalent restraint          — NEEDS it, still raises
    _sg_electrophile_distance  the frozen-site distance        — NEEDS it, still raises
    _reactive_cys_by_geometry  the geometric DIAGNOSTIC        — does not need it

and `build_system` states the rule that decides it: "Geometry is kept only as a diagnostic", under
**a diagnostic must never be able to kill the run it is describing**.

⚠ SO THE COVALENT PATH IS UNTOUCHED, AND THESE TESTS ARE MOSTLY ABOUT THAT. The danger in a change like this
is not that it fails to help the control — it is that it quietly lets a COVALENT leg build without a warhead,
which would produce numbers about a system nobody ran.
"""
from __future__ import annotations

import ast
import os
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MOD)
SRC = open(os.path.join(MOD, "nrv04_covalent_md.py")).read()
TREE = ast.parse(SRC)


def _fn(name):
    for n in ast.walk(TREE):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    raise AssertionError("%s is gone — this guard has lost its subject" % name)


def _calls_electrophile(fn):
    return any(isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_electrophile_and_neighbour"
               for n in ast.walk(fn))


def test_the_three_callers_are_still_the_three_callers():
    """The whole argument rests on WHICH callers need the electrophile. If a fourth appears, the reasoning
    has to be redone rather than inherited."""
    callers = sorted(f.name for f in ast.walk(TREE)
                     if isinstance(f, ast.FunctionDef) and _calls_electrophile(f))
    assert callers == ["_covalent_indices", "_reactive_cys_by_geometry", "_sg_electrophile_distance"], callers


def test_only_the_diagnostic_tolerates_a_missing_electrophile():
    """⚠ THE LOAD-BEARING ASSERTION. The diagnostic degrades; the two USERS must still raise, or a covalent
    leg could be built with no warhead and report numbers about a system nobody ran."""
    diag = _fn("_reactive_cys_by_geometry")
    guarded = [n for n in ast.walk(diag) if isinstance(n, ast.Try) and _calls_electrophile(n)]
    assert guarded, "the geometric diagnostic must tolerate a ligand with no electrophile"
    for name in ("_covalent_indices", "_sg_electrophile_distance"):
        fn = _fn(name)
        assert not [n for n in ast.walk(fn) if isinstance(n, ast.Try) and _calls_electrophile(n)], (
            f"{name} USES the electrophile — it must keep raising when there is none. Swallowing it here "
            f"would let a covalent leg build with no warhead.")


def test_a_covalent_leg_with_no_electrophile_is_a_hard_stop():
    """The other half: the diagnostic returning None must not let a COVALENT leg proceed."""
    build = _fn("build_system")
    assert "covalent and react_dist is None" in SRC, \
        "a covalent leg whose electrophile could not be located must stop with a reason, not a TypeError"
    # …and it must be a SystemExit, i.e. it actually stops.
    txt = ast.get_source_segment(SRC, build) or ""
    i = txt.index("covalent and react_dist is None")
    assert "SystemExit" in txt[i:i + 400]


def test_every_use_of_the_distance_tolerates_not_measured():
    """`react_dist` is None for a non-covalent control leg. A float format or comparison on it is a
    TypeError that kills the leg exactly as dead as the ValueError this change removes — and one of these
    (`react_dist > MAX_COVALENT_TETHER_A`) ran on EVERY leg, covalent or not."""
    txt = ast.get_source_segment(SRC, _fn("build_system")) or ""
    for bad, why in (
            ("{react_dist:.2f} Å from the warhead electrophile; preregistered",
             "the summary log line formats the distance unconditionally"),
    ):
        assert bad not in txt, why
    assert "react_dist is not None and react_dist > MAX_COVALENT_TETHER_A" in txt, \
        "the descriptive WARN compares the distance on every leg and must first check it was measured"
    assert "None if react_dist is None else round(react_dist, 2)" in txt or \
           "(None if react_dist is None" in txt, "the leg JSON must record an unmeasured distance as null"


def test_the_degraded_return_is_json_serializable():
    """NaN is not valid strict JSON, and this value reaches the committed leg record."""
    import json
    diag = ast.get_source_segment(SRC, _fn("_reactive_cys_by_geometry")) or ""
    assert 'float("nan")' not in diag, "an unmeasurable distance must be null, not NaN"
    assert "return None, None, None, {" in diag
    json.dumps({"sg_electrophile_dist_A": None})            # the shape that lands in the record


def test_a_C551A_leg_can_never_be_labelled_without_being_mutated():
    """A fabricated arm is worse than a failed one: mutating 'chain None residue None' would knock out
    nothing and still produce a leg labelled C551A."""
    txt = ast.get_source_segment(SRC, _fn("build_system")) or ""
    # ⚠ the FIRST occurrence is `needs_frozen_site = bool(covalent) or mutation == "C551A"`, which is a
    # different statement — anchor on the mutation BLOCK or this guard grades the wrong lines.
    i = txt.index('if mutation == "C551A":')
    seg = txt[i:i + 900]
    assert "react_chain is None or react_resid is None" in seg and "SystemExit" in seg
    assert "fabricated arm" in seg
