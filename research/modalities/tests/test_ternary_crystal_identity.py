"""The crystal ligand's identity must be DIRECTION-INVARIANT.

Regression test for the bug that killed the first reverse leg (2026-07-25).

`nr4a3_ternary_fep._build_components` passes a `base_smiles` to `_endpoint_pose` meaning "the identity of the
molecule that is actually in the staged crystal SDF", so `_repair_pose` can assign bond orders against the right
template. It was hardcoded to `sa` (endpoint A's SMILES). That is correct only in the FORWARD direction: for the
Wurz calibration edge, endpoint A = calib_hi = cmpd1 = the 8G1Q co-crystallised ligand (CCD YHB), while cmpd4 is
DERIVED (linker pyridine N->CH) and exists in no crystal.

`_morph_endpoints` swaps A/B when DIRECTION=rev. So a reverse leg asserted the crystal contained **cmpd4**, bond
orders were repaired against a template whose linker ring differs by N->CH, the thiazole lost its aromatic C-H,
and NAGL refused the molecule:

    openff.toolkit.utils.exceptions.RadicalsNotSupportedError:
      ... Found 1 radical electrons on molecule ...[C:7]2=[C:9]([C:10])[N:45]=[C:8][S:59]2...

(~30 s into charge assignment; GH run 30158125225. Note the thiazole rendered aliphatic/kekulé while the rest of
the molecule stayed aromatic, with C:8 carrying only =N and -S — its hydrogen gone. That is the radical.)

Which molecule sits in the crystal is a fact about the STRUCTURE, not about the direction we happen to morph in,
so it must not be derived from a value the direction swaps. Pure/stdlib: no OpenFE, OpenMM, RDKit or network.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_ternary_fep as eng  # noqa: E402

CALIB_TERNARY = "calib_hi_to_lo__ternary_vhl"


def _resolve(direction):
    """(endpoint_a, endpoint_b, smiles_a, smiles_b, crystal_smiles) with DIRECTION patched."""
    prev = eng.DIRECTION
    try:
        eng.DIRECTION = direction
        leg, _env = eng.leg_spec(CALIB_TERNARY)
        a, b, sa, sb = eng._morph_endpoints(leg)
        return a, b, sa, sb, eng.CRYSTAL_SMILES
    finally:
        eng.DIRECTION = prev


def test_direction_rev_swaps_the_endpoints():
    """The swap itself must still work — the fix must not silently disable reverse legs."""
    fa, fb, fsa, fsb, _ = _resolve("fwd")
    ra, rb, rsa, rsb, _ = _resolve("rev")
    assert (ra, rb) == (fb, fa), "DIRECTION=rev must swap the endpoint roles"
    assert (rsa, rsb) == (fsb, fsa), "DIRECTION=rev must swap the endpoint SMILES"


def test_crystal_identity_is_direction_invariant():
    """THE REGRESSION: the crystal ligand is the same molecule whichever way the morph runs."""
    _fa, _fb, _fsa, _fsb, fwd_crystal = _resolve("fwd")
    _ra, _rb, _rsa, _rsb, rev_crystal = _resolve("rev")
    assert fwd_crystal is not None, "crystal identity was never resolved"
    assert fwd_crystal == rev_crystal, (
        "crystal ligand identity changed with morph direction (fwd=%r rev=%r) — _repair_pose would be handed "
        "the wrong template and the built endpoint can carry a radical" % (fwd_crystal, rev_crystal))


def test_in_reverse_the_crystal_is_NOT_endpoint_a():
    """The precise shape of the old bug: in reverse, `sa` is the DERIVED molecule, so any code using `sa` as the
    crystal template is wrong. Asserting they differ is what makes the regression detectable rather than a
    coincidence of two equal strings."""
    _ra, _rb, rsa, _rsb, rev_crystal = _resolve("rev")
    assert rev_crystal != rsa, (
        "in DIRECTION=rev the crystal ligand must NOT equal endpoint A's SMILES — if these are equal the test "
        "cannot distinguish the fix from the bug")


def test_forward_crystal_is_endpoint_a():
    """Complement: forward is the case the old code got right, and must be unchanged."""
    _fa, _fb, fsa, _fsb, fwd_crystal = _resolve("fwd")
    assert fwd_crystal == fsa, "forward behaviour must be untouched (crystal == endpoint A)"


if __name__ == "__main__":  # runnable without pytest (the dev sandbox has none)
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS %s" % fn.__name__)
    print("%d checks pass" % len(fns))
