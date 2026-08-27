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
import re
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


# ⛔ THE ALLOW-LIST OF RETRIEVAL CHANNELS. A transcription's defence is that a later reader can go
# back to the same bytes, so `verified_against` must name a channel someone else can re-run. Two
# exist: the text layer of a rendered article PDF, and the NCBI PMC full-text record. Adding a
# channel here is a deliberate act; naming none is the failure this guard catches.
VERIFICATION_CHANNELS = ("text layer", "PMC full-text record")


def test_every_series_names_its_table_and_its_verification():
    for s in mod.SERIES:
        assert "Table" in s["printed_in"] or "TABLE" in s["printed_in"], s["source_id"]
        v = s["verified_against"]
        assert any(c in v for c in VERIFICATION_CHANNELS), (s["source_id"], v)
        # ⭐ STRICTLY STRONGER THAN THE 2026-08-25 FORM, which asserted the channel and nothing
        # else: a channel with no identifier in it is unrepeatable, so the identifier is now
        # required too. Every row must carry a PMC accession a reader can resolve.
        assert re.search(r"PMC\d{6,}", v), (s["source_id"], v)


def test_context_rows_are_never_pooled_into_any_fraction():
    """A percentage-only series may be recorded and may never become an addend.

    POLICY-evidence §2.1.2 forbids deriving counts from a published percentage. The context rows
    exist so the reading is not lost; this guard is what stops the next editor from summing them.
    """
    art = mod.build()
    pooled_ids = set()
    for block in art["pooled_extremity_fraction"].values():
        pooled_ids |= set(block["per_cohort_percent"])
    for row in mod.CONTEXT_NOT_POOLED:
        assert row["source_id"] not in pooled_ids, row["source_id"]
        assert any(k.startswith("⛔_why_not_pooled") for k in row), row["source_id"]
    assert pooled_ids == {s["source_id"] for s in mod.SERIES}


def test_no_pooled_lung_confined_fraction_is_ever_published():
    """The lung-confined readings are different estimands and must stay side by side.

    Two series print an exclusive partition over different presentation strata and a third states
    the fraction only as a percentage. Summing any pair of them is the single most tempting invalid
    move this artifact enables, so it is asserted against directly.
    """
    art = mod.build()
    block = art["lung_confined_readings"]
    assert any(k.startswith("⛔_no_pooled_estimate") for k in block)
    for r in block["readings"]:
        assert not any(k in r for k in ("percent", "ci95_lo_percent", "pooled")), r["source_id"]
    integer_rows = [r for r in block["readings"] if r["events"] is not None]
    assert len({r["stratum"] for r in integer_rows}) == len(integer_rows), (
        "two integer rows sharing a stratum would invite a sum")


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
