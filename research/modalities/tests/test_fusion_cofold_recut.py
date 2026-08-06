"""The `R13-b` pre-launch cut, held by tests rather than by a paragraph.

⛔ These exercise the REAL committed artifacts, not fixtures. Mock the thing under test and you test the mock
(CLAUDE.md §6) — and the whole point of this gate is that it refuses on the real data before a cent is spent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fusion_cofold_recut as fc  # noqa: E402


def test_the_gate_passes_on_the_real_committed_artifacts():
    _inp, _built, checks, ok = fc.build_all()
    failed = [c["check"] for c in checks if not c["ok"]]
    assert ok, "the R13-b cut gate must pass on committed data; failed: %s" % failed
    assert len(checks) > 30, "a gate this thin is not doing the job it claims"


def test_both_seams_begin_the_nr4a3_block_at_residue_1_which_is_the_X9_correction():
    """`fusion_cofold.py` resumes NR4A3 at residue 2. Finding X9 settled that exon 3 IS residue 1, so the
    fusion RETAINS the AF-1 and the cut must start there. If this ever reverts, the re-cut was undone."""
    _inp, built, _checks, _ok = fc.build_all()
    for key, rec in built.items():
        seam = rec["constructs"]["seam"]
        assert seam["nr4a3_range"][0] == 1, "%s seam must resume NR4A3 at residue 1" % key
        assert seam["chain"][seam["block_boundary"]] == "M", (
            "%s seam must place NR4A3 M1 immediately after the 5' block" % key)


def test_neither_object_is_a_default_because_OC_2_is_open():
    """OC-2 (systems/graph/integrity.json) registers 'the canonical EMC fusion' as naming two incompatible
    objects and says choosing is not a navigation-layer call. The two SEAMS differ, which is the one thing a
    seam co-fold cannot be agnostic about — so `--object` must stay required and unset by default."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", choices=sorted(fc.OBJECT_SPECS), nargs="+")
    assert ap.parse_args([]).object is None
    _inp, built, _checks, _ok = fc.build_all()
    seams = {k: v["constructs"]["seam"]["chain"] for k, v in built.items()}
    assert len(set(seams.values())) == len(seams), (
        "if the two objects' seams were identical the OC-2 choice would be moot; they are not")


def test_the_reported_type_1_cut_reproduces_its_committed_junction_context():
    """The decisive provenance check: the built seam must carry the exact junction context string the
    committed construct-design artifact records for reported type 1."""
    inp, built, _checks, _ok = fc.build_all()
    entry = fc.designs_by_id(inp["designs"])["EWSR1_NR4A3_type1"]
    left, right = entry["junction_in_residue_numbering"]["junction_context_aa"].split("|")
    seam = built["t1_reported_canonical"]["constructs"]["seam"]
    b = seam["block_boundary"]
    # left is 10 residues ending at the 5' partner's last fully-encoded residue; the junction residue is the
    # first character of `right`, and it sits immediately before the NR4A3 block.
    assert seam["chain"][b - len(left):b - 1] == left[1:], "5' context does not match the committed artifact"
    assert seam["chain"][b - 1] == right[0], "the junction-encoded residue does not match"
    assert seam["chain"][b:b + len(right) - 1] == right[1:], "NR4A3 context does not match"


def test_no_usd_per_ns_is_reported_for_this_rung_and_the_dollar_ceiling_is_derived():
    """A co-fold integrates no dynamics. A `$/ns` here would be a fabricated figure in the one column
    CLAUDE.md §1 exists to make gradeable, so its absence is a refusal and the dollar band is the gate."""
    d = fc.dollar_ceiling()
    assert d["usd_per_ns"] is None
    assert d["ceiling_usd_total"] == d["band_usd"][1]
    assert d["ceiling_usd_per_model"] == round(d["band_usd"][1] / d["units"], 6)
    assert "DOLLAR" in d["which_ceiling_binds"]


def test_the_launch_path_check_reads_the_real_repo_and_does_not_assert_a_capability_we_lack():
    """The rung's plan cell says 'Vast, baked image'. This check must read the Dockerfiles rather than
    repeat the claim — and it must not silently pass while no Boltz image exists."""
    lp = fc.launch_path_check()
    assert lp["verdict"] in ("READY", "BLOCKED")
    names = {f["check"] for f in lp["findings"]}
    assert any("Dockerfile for a Boltz image" in n for n in names)
    assert any("billing host" in n for n in names)
    # ⛔ THE ONE THAT MATTERS: a Dockerfile in the tree must never be allowed to satisfy "a baked image
    # exists". A file's presence is not provenance (CLAUDE.md §4b), and the registry is unreadable from
    # here, so the pushed-image finding must stay FAIL until a bake run says otherwise.
    pushed = [f for f in lp["findings"] if "BAKED AND PUSHED" in f["check"]]
    assert len(pushed) == 1 and pushed[0]["ok"] is False
    assert lp["verdict"] == "BLOCKED"
