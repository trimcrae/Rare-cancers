"""Guard tests for `emc_care_delivery_evidence.py`.

The artifact is a table of clinical claims attributed to named PMIDs, so the failure that matters
is a hand edit to a quoted number or a citation that persists undetected. `--check` re-derives to
MEMORY and compares against the committed copy; these tests perturb the REAL committed artifact on
disk and assert the REAL `--check` refuses it AND writes nothing — a regenerating check returns 0
precisely because it just made the file match, so the return code alone cannot separate the guard
from the defect.

They also hold the two properties the artifact's own honesty rests on: that every row carries a
provenance label, and that the ICD-O finding keeps BOTH sides of the contradiction. A one-sided
version of that finding would read as a coding opinion rather than as two published Methods
sections disagreeing.
"""

from __future__ import annotations

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_care_delivery_evidence as mod  # noqa: E402


def test_check_passes_on_the_committed_artifact():
    assert mod.main(["--check"]) == 0


def test_check_refuses_a_perturbed_claim_and_writes_nothing(tmp_path, monkeypatch):
    # ⛔ ISOLATED 2026-08-29 (AUT-PD-187). This mutated the LIVE tracked artifact and restored it in
    # a `finally` — safe only while nothing else reads it, and this suite runs under xdist. See
    # research/manuscripts/tests/tracked_tree_guard.py for what that cost. The producer's OUT is
    # redirected at a private copy, so what is under test is unchanged and the tree is never written.
    assert os.path.exists(mod.OUT), "run the generator first"
    copy = tmp_path / os.path.basename(mod.OUT)
    shutil.copyfile(mod.OUT, copy)
    monkeypatch.setattr(mod, "OUT", str(copy))

    with open(mod.OUT, encoding="utf-8") as fh:
        payload = json.load(fh)
    # the exact edit the banner forbids: a hazard ratio changed by hand
    payload["findings"][0]["what_it_says"] = "surgery had no effect"
    with open(mod.OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    mtime_before = os.path.getmtime(mod.OUT)

    assert mod.main(["--check"]) == 1, "--check accepted a hand-edited clinical claim"

    with open(mod.OUT, encoding="utf-8") as fh:
        assert json.load(fh)["findings"][0]["what_it_says"] == "surgery had no effect", (
            "--check rewrote the artifact instead of refusing it"
        )
    assert os.path.getmtime(mod.OUT) == mtime_before


def test_every_row_carries_a_provenance_label():
    """An unlabelled row is indistinguishable from a full-text-verified one."""
    for row in mod.FINDINGS + mod.ABSENCES:
        assert row.get("provenance") in {"[FT]", "[API]", "[snippet]", "[unverified]"}, (
            f"{row['id']} carries no provenance label"
        )
    for side in mod.ICD_O["sides"]:
        assert side.get("provenance") in {"[FT]", "[API]"}
        assert side.get("quote"), f"{side['pmid']} states a reading with no quote behind it"


def test_the_icd_o_finding_keeps_both_sides_of_the_contradiction():
    """One side alone is an opinion about coding; two are a contradiction in the record."""
    sides = mod.ICD_O["sides"]
    assert len(sides) >= 2
    readings = {s["reads_the_code_as"] for s in sides}
    assert len(readings) == len(sides), "both sides must record DIFFERENT readings of the code"
    pmids = {s["pmid"] for s in sides}
    assert len(pmids) == len(sides), "both sides must be different papers"


def test_every_finding_names_a_route_that_exists_in_the_graph():
    """A finding pointing at no route is evidence nothing reads."""
    repo = mod.REPO
    with open(os.path.join(repo, "systems", "graph", "routes.json"), encoding="utf-8") as fh:
        known = {r["id"] for r in json.load(fh)}
    for row in mod.FINDINGS + mod.ABSENCES:
        assert row["route"] in known, f"{row['id']} names unknown route {row['route']}"
