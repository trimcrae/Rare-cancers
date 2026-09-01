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


# ---------------------------------------------------------------------------
# The false-absence class (added 2026-09-01, seat S18-FALSE-ABSENCES)
# ---------------------------------------------------------------------------
# ⛔ WHAT THESE ARE FOR. `absences[no-emc-metastasectomy-literature].result` read the literal
# string "ZERO records." from 2026-08-09 to 2026-09-01. It was false: PMC12398172 (Masunaga 2025,
# blob 79a8c197243ff4202a713d437def379c5f499a68) sits inside the corpus the query names and
# reports metastasectomy in eight of its 29 metastatic patients. No test could have caught it,
# because `--check` compares the generator against its own output and a wrong input reproduces
# perfectly. These tests bind the verdict to the evidence instead.


def test_no_absence_row_states_a_zero_its_own_corpus_quote_contradicts():
    """The exact defect, asserted directly rather than through the derivation."""
    for row in mod.ABSENCES:
        term = row["term_searched"]
        if mod.corpus_hits(term):
            assert row["status"] == "REFUTED", f"{row['id']} has a matching quote and is not REFUTED"
            assert row["result"].startswith("⛔ NOT ZERO"), (
                f"{row['id']} still asserts an absence its own committed quote refutes"
            )


def test_every_absence_result_is_derived_and_not_typed():
    """A retyped literal must not survive. This is the mutation that reintroduces the defect."""
    for row in mod.ABSENCES:
        assert row["result"] == mod.absence_result(row["term_searched"]), (
            f"{row['id']}: `result` is a typed string, not the one its corpus quotes derive"
        )
    assert mod._check_structure() == []


def test_a_retyped_zero_is_refused_by_the_structural_guard(monkeypatch):
    """Mutation test: put the original wrong literal back and the guard must go red."""
    broken = [dict(r) for r in mod.ABSENCES]
    broken[0]["result"] = "ZERO records."
    monkeypatch.setattr(mod, "ABSENCES", broken)
    errs = mod._check_structure()
    assert any("may not be typed" in e for e in errs), errs


def test_deleting_the_evidence_behind_a_refutation_is_refused(monkeypatch):
    """The ratchet. Every derived field agrees again once the quotes are gone, so the marker —
    which is NOT derived — is what makes the erasure visible."""
    monkeypatch.setattr(mod, "CORPUS_QUOTES", [])
    errs = mod._check_structure()
    assert any("may not be deleted" in e for e in errs), errs


def test_every_corpus_quote_is_pinned_by_a_real_blob_sha():
    """A quote with no pinned blob is an argument; a quote with one is a byte comparison."""
    import re as _re

    assert mod.CORPUS_QUOTES, "the corpus-quote table is empty"
    for q in mod.CORPUS_QUOTES:
        assert _re.fullmatch(r"[0-9a-f]{40}", q["blob_sha"]), q["path"]
        assert q["corpus"] in q["path"], f"{q['path']} is not under the corpus it names"
        assert len(q["text"]) >= 40, f"{q['path']} carries no usable verbatim quote"
        assert q["pmid"] and q["read_via"] and q["read_utc"]


def test_the_corpus_search_can_only_turn_an_absence_into_a_presence():
    """`corpus_hits` never certifies a zero — a miss means 'not in the quotes committed here'."""
    assert mod.corpus_hits("metastasectom"), "the refuting quote is not reachable by its own term"
    assert mod.corpus_hits("carbon ion") == [], (
        "this file's quote table is not a corpus sweep and must not read as one"
    )


def test_the_correction_states_a_lower_bound_and_never_a_new_count():
    """⛔ Replacing one unmeasured number with another repeats the defect."""
    result = mod.ABSENCES[0]["result"]
    assert "lower bound" in result and "UNKNOWN" in result, (
        "the corrected row must say the corpus total is unknown, not assert a new count"
    )


def test_the_correction_asserts_no_efficacy():
    """A count of what was DONE is not evidence that it works. CLAUDE.md §1 language discipline."""
    row = mod.ABSENCES[0]
    blob = " ".join(str(v) for v in row.values()).lower()
    for banned in ("improves survival", "is effective", "benefit of metastasectomy",
                   "should be offered", "efficacy of metastasectomy"):
        assert banned not in blob, f"the corrected absence row implies efficacy: {banned!r}"
    assert "no outcome" in blob or "prints no outcome" in blob
