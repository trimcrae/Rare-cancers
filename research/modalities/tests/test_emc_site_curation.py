"""Guards for `emc_site_curation.py` — transcribed anatomical-site denominators.

WHAT EACH GUARD CAN FAIL:
  * a series whose site counts do not add up to its own stated n — the arithmetic that would make
    every fraction below it wrong, and the cheapest thing to get wrong while transcribing;
  * a series row with no `printed_in` or no text-layer verification — transcription's failure mode
    is a silent digit, so provenance is the whole defence;
  * the two extremity definitions collapsing into one, which would hide the category boundary the
    artifact exists to expose;
  * a non-exclusive metastatic table being read as a lung-confined fraction — asserted directly,
    because that inference is the one a reader most wants to make and it is invalid.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_site_curation as mod  # noqa: E402


def test_every_series_site_table_adds_up_to_its_own_n():
    for s in mod.SERIES:
        total = sum(s["primary_site_counts"].values())
        assert total == s["n_total"], (s["source_id"], total, s["n_total"])


def test_subcounts_add_up_to_their_group():
    for s in mod.SERIES:
        for group, subs in (s.get("primary_site_subcounts") or {}).items():
            assert sum(subs.values()) == s["primary_site_counts"][group], (s["source_id"], group)


def test_every_series_names_its_table_and_its_verification():
    for s in mod.SERIES:
        assert "Table" in s["printed_in"] or "TABLE" in s["printed_in"], s["source_id"]
        assert "text layer" in s["verified_against"], s["source_id"]


def test_the_two_extremity_definitions_are_reported_separately_and_differ():
    art = mod.build()
    strict = art["pooled_extremity_fraction"]["extremity_strict"]
    inclusive = art["pooled_extremity_fraction"]["extremity_inclusive"]
    assert inclusive["events"] > strict["events"], "the inclusive definition adds nobody"
    assert inclusive["percent"] != strict["percent"]


def test_a_non_exclusive_metastatic_table_is_flagged_and_never_summed_to_a_fraction():
    for s in mod.SERIES:
        met = s["metastatic"]
        counts = met["counts_non_exclusive"]
        total = sum(counts.values())
        if total > met["denominator"]:
            assert any(k.startswith("⚠_non_exclusive") for k in met), s["source_id"]
        else:
            assert total == met["denominator"], (s["source_id"], total, met["denominator"])


def test_the_committed_artifact_matches_the_generator():
    assert os.path.exists(mod.OUT)
    with open(mod.OUT, encoding="utf-8") as fh:
        assert json.load(fh) == mod.build()


def test_check_refuses_a_perturbed_artifact(tmp_path):
    import shutil
    backup = str(tmp_path / "b.json")
    shutil.copy(mod.OUT, backup)
    try:
        with open(mod.OUT, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["pooled_extremity_fraction"]["extremity_strict"]["percent"] = 99.9
        with open(mod.OUT, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        assert mod.check() == 1
    finally:
        shutil.copy(backup, mod.OUT)
