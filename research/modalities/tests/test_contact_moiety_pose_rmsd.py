#!/usr/bin/env python3
"""The ligand-escape flag must be about the atoms that are actually in the pocket.

WHY. LIG_RMSD_MAX_A (4 Å) is a POCKET-ESCAPE threshold, and ternary_fep_convergence.py has now had to stop
applying it to atoms with no pocket three times:

  1. the whole 146 k-particle system (79 Å, dominated by bulk water)          -- GH run 30156744299
  2. the SOLVENT leg's internal RMSD (a free PROTAC in water explores)        -- GH run 30167976061
  3. the BINARY leg's whole-ligand pose RMSD                                  -- GH run 30201372471

Case 3 measured: calib_hi_to_lo__binary_vhl pose_rmsd max 16.636 Å / median 6.987 Å -> technical_failure=TRUE,
against calib_hi_to_lo__ternary_vhl at max 2.765 / median 1.644 in the SAME cycle. A PROTAC in a binary complex
has ONE warhead bound; the linker and the distal warhead are in solvent BY CONSTRUCTION because the second
protein is absent. So a whole-ligand pose RMSD there is dominated by the free end moving, and cannot distinguish

    "the bound warhead left its pocket"   (real: invalidates ΔG_binary, hence ΔΔG_coop = ternary - binary)
from
    "the unbound end moved"               (the expected physics of the binary state)

That distinction is decision-relevant, so the flag now uses the CONTACT-MOIETY pose RMSD and the whole-ligand
value is reported as information.

THE POINT OF THIS TEST FILE is that restricting a gate's observable is exactly the kind of change that can
quietly turn a real failure into a pass, so the cases below pin BOTH directions: a flailing free end must pass
while REPORTING its large whole-ligand value, and a genuinely escaping bound warhead must still fail. Plus the
third outcome that is neither: no contact moiety at all must be UNMEASURED, never passed.

Pure numpy against the real functions -- no openmmtools, no trajectory, so it runs in the dev sandbox.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _skip_guard import skip_module    # noqa: E402

try:
    import numpy as np
except ImportError:  # pragma: no cover
    skip_module("numpy unavailable")

import ternary_fep_convergence as cv


def _system(free_end_shift_nm=0.0, bound_end_shift_nm=0.0, ligand_far=False):
    """A receptor slab plus a 10-atom 'PROTAC': 5 atoms in contact, 5 out in solvent.

    Rows 0-19 receptor, 20-24 the bound warhead (0.3 nm from the slab -> inside the 0.45 nm contact cutoff),
    25-29 the distal warhead (3 nm away -> never in contact). Frame B applies the requested shifts.
    """
    rng = np.random.default_rng(0)
    receptor = rng.uniform(-1.0, 1.0, size=(20, 3))
    receptor[:, 2] = 0.0                                  # a flat slab at z=0
    bound = np.array([[0.1 * i, 0.0, 0.30] for i in range(5)])
    distal = np.array([[0.1 * i, 0.0, 3.00] for i in range(5)])
    if ligand_far:
        bound = bound + np.array([0.0, 0.0, 5.0])         # nothing within the cutoff
    A = np.vstack([receptor, bound, distal])
    B = A.copy()
    B[20:25] += np.array([bound_end_shift_nm, 0.0, 0.0])
    B[25:30] += np.array([free_end_shift_nm, 0.0, 0.0])
    prot_rows = list(range(20))
    lig_rows = list(range(20, 30))
    return A, B, prot_rows, lig_rows


def _measure(A, B, prot_rows, lig_rows):
    contact_rows = cv._contact_ligand_rows(A, lig_rows, prot_rows)
    whole = cv._kabsch_rmsd(A, B, prot_rows, lig_rows)
    contact = cv._kabsch_rmsd(A, B, prot_rows, contact_rows)
    return contact_rows, whole, contact


def test_contact_set_is_the_bound_warhead_only():
    A, B, p, l = _system()
    rows, _, _ = _measure(A, B, p, l)
    assert rows == list(range(20, 25)), (
        f"contact set should be exactly the 5 bound-warhead atoms, got {rows}. If this picks up the distal "
        f"warhead the whole distinction collapses.")


def test_flailing_free_end_passes_the_flag_but_its_large_value_is_still_reported():
    """The r0 binary-leg case: bound warhead rock-steady, distal warhead swings 2 nm."""
    A, B, p, l = _system(free_end_shift_nm=2.0)
    _, whole, contact = _measure(A, B, p, l)
    assert whole > cv.LIG_RMSD_MAX_A, (
        f"whole-ligand RMSD should exceed the 4 Å threshold here ({whole:.2f}) — that is the value that made the "
        f"binary leg read as a technical failure, and the test is meaningless if it does not reproduce it")
    assert contact <= cv.LIG_RMSD_MAX_A, (
        f"contact-moiety RMSD should PASS ({contact:.2f} Å) — the bound warhead never moved")
    # and the whole-ligand number must remain visible, not be replaced
    assert whole > contact * 5, "the two observables must stay distinguishable in the record"


def test_an_escaping_bound_warhead_still_FAILS():
    """The direction that matters for not weakening the gate: the bound end leaves, the free end is still."""
    A, B, p, l = _system(bound_end_shift_nm=1.0)
    _, whole, contact = _measure(A, B, p, l)
    assert contact > cv.LIG_RMSD_MAX_A, (
        f"a bound warhead displaced 1 nm MUST fail the contact-moiety flag, got {contact:.2f} Å. If this passes, "
        f"the change is a loosening and must be reverted.")
    assert whole > cv.LIG_RMSD_MAX_A, "the whole-ligand value should also be large here"


def test_both_ends_moving_fails():
    A, B, p, l = _system(bound_end_shift_nm=1.0, free_end_shift_nm=2.0)
    _, _, contact = _measure(A, B, p, l)
    assert contact > cv.LIG_RMSD_MAX_A, "a real escape must not be masked by also having a floppy free end"


def test_no_contact_moiety_is_UNMEASURED_not_a_pass():
    """A ligand with no receptor contact in the reference frame is itself a finding, so the flag must be None."""
    A, B, p, l = _system(ligand_far=True)
    rows, _, contact = _measure(A, B, p, l)
    assert rows == [], f"expected an empty contact set, got {rows}"
    assert contact is None, (
        "with no contact moiety the contact RMSD must be None so the flag reads UNMEASURED. Returning a number "
        "here (or 0.0) would let 'the ligand was never in contact' report as 'the ligand is stable'.")


def test_contacts_come_from_the_reference_frame_not_the_later_one():
    """A warhead that escapes would drop out of a frame-B contact set and erase its own evidence.

    Frame B has the bound warhead displaced 1 nm, i.e. out of contact. Deriving contacts from B would give an
    empty set (or the wrong atoms) and lose the escape; deriving from A keeps the 5 atoms and reports it.
    """
    A, B, p, l = _system(bound_end_shift_nm=1.0)
    from_a = cv._contact_ligand_rows(A, l, p)
    from_b = cv._contact_ligand_rows(B, l, p)
    assert from_a == list(range(20, 25)), f"reference-frame contacts should be the bound warhead, got {from_a}"
    assert from_b != from_a, (
        "this test only proves something if the two frames genuinely disagree; if they agree, the escape "
        "displacement is too small to have left the contact shell")
    assert cv._kabsch_rmsd(A, B, p, from_a) > cv.LIG_RMSD_MAX_A, "frame-A contacts must still catch the escape"


def test_the_call_site_passes_the_REFERENCE_frame():
    """The test above pins the HELPER's behaviour; this pins the CALL SITE, which is where the mistake lives.

    Verified necessary: swapping `_contact_ligand_rows(A, ...)` to `(B, ...)` inside _ligand_pose_block left all
    the other tests in this file green, because they call the helper directly and never exercise the call site.
    A frame-B contact set drops the atoms that have just escaped, so the flag would be computed over whatever
    stayed put -- or be empty and read as UNMEASURED -- and either way the escape erases its own evidence. There
    is no cheap way to drive _ligand_pose_block without an openmmtools reporter, so this asserts on the source.
    """
    import inspect
    src = inspect.getsource(cv._ligand_pose_block)
    calls = [l.strip() for l in src.splitlines() if "_contact_ligand_rows(" in l]
    assert len(calls) == 1, f"expected exactly one contact-row call in _ligand_pose_block, found {calls}"
    assert calls[0].startswith("contact_rows = _contact_ligand_rows(A,"), (
        f"the contact set MUST be derived from the reference frame A, got: {calls[0]}")


def test_rigid_body_motion_of_the_whole_complex_is_not_an_escape():
    """Superposition is on the receptor, so translating everything together must read ~0 on both observables."""
    A, B, p, l = _system()
    B = A + np.array([5.0, -3.0, 2.0])          # move the entire system
    _, whole, contact = _measure(A, B, p, l)
    assert whole < 0.01 and contact < 0.01, (
        f"a pure rigid-body move must not register (whole={whole:.4f}, contact={contact:.4f})")


def test_cutoff_is_the_documented_value():
    assert cv.CONTACT_CUTOFF_NM == 0.45, "the contact cutoff is quoted in the report and in the docstrings"


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
