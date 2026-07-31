#!/usr/bin/env python3
"""Guards for the two-branch (two-mechanism) linker template.

WHAT IS ACTUALLY AT RISK HERE, in order:
  1. **Silently corrupting the preregistered enumeration.** This module is an ADDITIVE extension and its
     whole legitimacy rests on not touching `nr4a3-linker-design.json`. A test asserts the library is
     byte-identical after a full run.
  2. **Two pendants capturing each other's ring bonds.** The one-pendant assembler partitioned SMILES ring
     digits E3 1-3 / warhead 4-6 / pendant 7-9 — a partition with room for exactly one pendant. Two
     fragments that both open ring `7` produce a DIFFERENT molecule that still parses, i.e. a silent
     structural error. The allocator must keep them disjoint or refuse.
  3. **Quietly widening the admissible set.** The finding is that exactly ONE chain satisfies both windows.
     If that ever becomes several without the windows changing, the scan has stopped discriminating.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import linker_twobranch as TB  # noqa: E402
import nr4a3_linker_design as LD  # noqa: E402


def test_the_preregistered_library_is_untouched_by_a_full_run():
    """★ THE LOAD-BEARING ONE. This module may add; it may not edit."""
    before = open(TB.LIB_JSON, "rb").read()
    TB.build_report()
    assert open(TB.LIB_JSON, "rb").read() == before, "the preregistered enumeration must be byte-identical"


def test_exactly_one_chain_satisfies_both_windows():
    chains = TB.admissible_chains()
    assert len(chains) == 1, f"the finding is a unique solution; got {len(chains)}"
    c = chains[0]
    assert c["k_far_covalent"] > c["k_near_wedge"], "the covalent branch sits further from the warhead"
    lo, hi = c["covalent_window"][0]
    assert lo <= c["k_far_covalent"] <= hi
    lo2, hi2 = c["wedge_window"][0]
    assert lo2 <= c["k_near_wedge"] <= hi2


def test_both_branch_positions_come_out_of_the_assembler_not_the_scan():
    """The scan and the assembler compute k independently; if they ever disagree, one of them is wrong and a
    construct would be recorded at a position it does not occupy."""
    c = TB.admissible_chains()[0]
    _smi, n, k_far, k_near = TB.build_two_branch_smiles(
        "crbn", c["warhead"], c["seg1"], c["seg2"], c["seg3"], "cyac_me", "pyr3")
    assert (n, k_far, k_near) == (c["n_backbone_atoms"], c["k_far_covalent"], c["k_near_wedge"])


def test_the_two_pendants_never_share_a_ring_digit():
    """Exhaustive over the real pendant set — this is a correctness property, not a sample."""
    import re
    for pe in TB.ELECTROPHILES:
        for pw in TB.WEDGES:
            far, near = TB._renumber_pair(LD.PENDANT[pe]["smi"], LD.PENDANT[pw]["smi"])
            a = {c for c in re.findall(r"\d", far)}
            b = {c for c in re.findall(r"\d", near)}
            assert not (a & b), f"{pe}+{pw} share ring digits {a & b}"


def test_ring_digits_do_not_collide_with_the_E3_or_WAREHEAD_ranges():
    """The pendants must stay out of E3's 1-3 and the warhead's 4-6, or a pendant closes an E3 ring."""
    import re
    far, near = TB._renumber_pair(LD.PENDANT["cyac_ph"]["smi"], LD.PENDANT["pyr3"]["smi"])
    used = {int(c) for c in re.findall(r"\d", far + near)}
    assert used and min(used) >= 7, f"pendant ring digits {used} intrude on the E3/warhead ranges"


def test_a_zero_length_inter_amide_segment_is_REFUSED_on_both_sides():
    """The acylurea guard has to apply to SEG2 as well as SEG3 — the two-branch template has an inter-amide
    segment the one-pendant one never had, and it is the same motif."""
    for bad in (("s0", "a2"), ("a2", "s0")):
        with pytest.raises(ValueError, match="acylurea"):
            TB.build_two_branch_smiles("crbn", "5amide", "a2", bad[0], bad[1], "cyac_me", "pyr3")


def test_an_acyl_only_segment_is_refused_after_an_amide_nitrogen():
    with pytest.raises(ValueError, match="N,O-acetal"):
        TB.build_two_branch_smiles("crbn", "5amide", "a2", "e3", "a2", "cyac_me", "pyr3")


def test_the_set_carries_its_own_matched_controls():
    """A lone active is not a design set. The non-electrophilic control and the des-aza wedge control must
    both be enumerated, or nothing in this set can be compared against anything."""
    _chains, lib = TB.enumerate_two_branch()
    kinds = {(c["pendant_far_kind"], c["pendant_near_kind"]) for c in lib}
    assert ("electrophile", "wedge") in kinds
    assert ("control", "wedge") in kinds, "the non-electrophilic control must be present"
    assert ("electrophile", "wedge_control") in kinds, "the des-aza wedge control must be present"


def test_the_artifact_states_its_claim_ceiling_and_the_transferred_windows():
    rep = TB.build_report()
    lim = rep["_limits"]
    assert "TRANSFERRED" in lim["windows_are_TRANSFERRED"] or "transfer" in lim["windows_are_TRANSFERRED"]
    assert "constructible" in lim["claim_ceiling"]
    assert "selective" in lim["claim_ceiling"], "it must disclaim being a selectivity statement"


@pytest.mark.skipif(not os.path.exists(TB.OUT), reason="artifact not built")
def test_the_committed_artifact_reports_the_property_cost_honestly():
    """Carrying two mechanisms is not free, and the artifact must say so rather than presenting the set as a
    win. This asserts the comparison exists and points the right way."""
    rep = json.load(open(TB.OUT))
    c = rep.get("cost_of_the_second_mechanism")
    assert c, "the property cost must be recorded"
    assert c["delta_median_heavy_atoms"] > 0 and c["delta_median_mw"] > 0
    assert "not a claim that" in c["★_reading"], "it must disclaim developability"
