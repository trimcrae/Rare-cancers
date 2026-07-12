"""Unit tests for layer1_vhl_fetch.py — the Layer-1 VHL panel primary-source dossier fetcher.

Only the OFFLINE surface is testable in the sandbox (network is egress-blocked; the real fetch runs on a CI
runner). Confirms the query-target plan is well-formed, the candidate set satisfies the prereg's composition
intent (an independent MZ1 control + the SMARCA2 series), and — critically — that the module NEVER fabricates
a measured alpha (measured_alpha is a curation output, always null from the fetcher)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import layer1_vhl_fetch as f  # noqa: E402


def test_plan_targets_offline_well_formed():
    p = f.plan_targets()
    ids = [c["id"] for c in p["candidates"]]
    assert "mz1_brd4_vhl" in ids and "smarca2_vhl_series" in ids
    for c in p["candidates"]:
        assert c["rcsb_text"] and c["europepmc"] and c["expected_class"]
    assert any("rcsb" in e.lower() for e in p["endpoints"])
    assert any("europepmc" in e.lower() for e in p["endpoints"])


def test_independent_control_is_flagged():
    mz1 = next(c for c in f.CANDIDATES if c["id"] == "mz1_brd4_vhl")
    assert mz1["independent_vhl"] is True and mz1["is_mz1"] is True
    assert mz1["expected_class"] == "cooperative"


def test_fetcher_never_fabricates_measured_alpha():
    # every candidate template carries measured_alpha as a curation TODO, never a value
    for c in f.CANDIDATES:
        assert "measured_alpha" not in c or c["measured_alpha"] is None


def test_candidate_search_seeds_present():
    for c in f.CANDIDATES:
        assert "rcsb_text" in c["search"] and "europepmc" in c["search"]
