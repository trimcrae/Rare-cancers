"""Guards for the near-self (TCR cross-reactivity) scan.

⛔ THE ONE THAT MATTERS IS THE STRADDLE GUARD. The haystack is every reviewed human protein joined
by a sentinel, and at a mismatch tolerance of 1 or 2 a window carrying ONE sentinel still passes the
Hamming test. Such a window is not a human peptide — it is the tail of one protein glued to the head
of the next — and reporting it would INVENT a near-self hit in a safety analysis. Exact-match search
never had this failure mode, which is why it appears the moment mismatches are allowed.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "junction-selfsimilarity.json")

np = pytest.importorskip("numpy", reason="the scan is vectorised; CI installs numpy")

_spec = importlib.util.spec_from_file_location(
    "junction_selfsimilarity", os.path.join(MOD, "junction_selfsimilarity.py"))
js = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(js)


def _hay(seqs):
    hay = "\x00".join(seqs)
    arr = np.frombuffer(hay.encode("ascii"), dtype=np.uint8)
    sent = np.nonzero(arr == 0)[0]

    def straddles(i, L):
        k = np.searchsorted(sent, i)
        return bool(k < sent.shape[0] and sent[k] < i + L)

    return arr, straddles


def test_a_window_spanning_two_proteins_is_never_reported():
    """⛔ The defect this file exists for. 'AAAA' + sentinel + 'AAAA' must yield no 5-mer."""
    arr, straddles = _hay(["AAAA", "AAAA"])
    assert js.scan(np, arr, straddles, "AAAAA", 2) == []


def test_an_exact_match_inside_one_protein_is_found_at_zero_mismatches():
    arr, straddles = _hay(["MKWVTFISLL", "QQNMPCVQAQY"])
    hits = js.scan(np, arr, straddles, "NMPCVQAQY", 2)
    assert [mm for _, mm in hits] == [0]


def test_mismatches_are_counted_and_the_tolerance_is_respected():
    arr, straddles = _hay(["NMPCVQAQY", "NMPCVQAQA", "NMPCVQAAA", "NMPCVQKAK"])
    got = sorted(mm for _, mm in js.scan(np, arr, straddles, "NMPCVQAQY", 2))
    assert got == [0, 1, 2], "expected the 0-, 1- and 2-mismatch copies and not the 3-mismatch one"


def test_the_anchor_convention_is_p2_and_the_c_terminus():
    assert js.anchor_positions(9) == {2, 9}
    assert js.anchor_positions(11) == {2, 11}


@pytest.mark.skipif(not os.path.exists(ART), reason="junction-selfsimilarity.json not yet generated")
@pytest.mark.committed_artifact
def test_the_artifact_reports_its_null_beside_every_count():
    """⛔ A hit count with no chance baseline is not a finding — §7 concedes exactly that gap."""
    d = json.load(open(ART))
    assert "⛔_STATUS" not in d, d.get("error")
    assert d["queries"], "no queries searched"
    for q in d["queries"]:
        assert "null_mean" in q and "null_max" in q, f"{q['peptide']} has no chance baseline"


@pytest.mark.skipif(not os.path.exists(ART), reason="junction-selfsimilarity.json not yet generated")
@pytest.mark.committed_artifact
def test_the_artifact_refuses_to_read_as_a_safety_result():
    d = json.load(open(ART))
    assert "⛔_STATUS" not in d, d.get("error")
    text = d["⛔_what_this_is_not"].lower()
    assert "not a safety result" in text
    assert "sequence distance is not tcr distance" in text
