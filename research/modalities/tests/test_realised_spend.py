"""The realised-spend summariser: the scoreboard's headline is arithmetic, not a sentence.

WHY IT EXISTS. On 2026-07-27 STRATEGY.md's scoreboard read "$0.74 spent" while the step 1 fan-out's own
ledger stood at $20.11 — a hand-typed total, ~27x low, understating spend while three lanes were billing.
Rule 1.1 already said a total is DERIVED; nothing enforced it for THIS total. These tests pin the four
properties that make the derived answer trustworthy, and every one of them is a mistake that was available:

  1. no lane is counted twice (two artifacts carry the same money at two moments);
  2. free credit is NEVER folded into realised spend (CLAUDE.md §6 — a separate ledger);
  3. an unreadable ledger yields an ERROR, not a silent zero (a fabricated all-clear is the worst failure
     a spend readout has — same rule as congeneric_fanout_vast.load_ledger_strict);
  4. an attested-only lane is a DEFECT with a stated remediation, not a place to file spend forever.
"""
import json
import os

import pytest

import realised_spend as rs


def test_lanes_and_mirrors_are_disjoint():
    """A mirror read as a lane double-counts that lane's entire spend."""
    lane_src = {(l["artifact"], l["key"]) for l in rs.LANES}
    mirror_src = {(m["artifact"], m["key"]) for m in rs.MIRRORS}
    assert not (lane_src & mirror_src), (
        "an artifact/key pair is declared BOTH as a lane's source and as a mirror deliberately not summed"
    )


def test_every_lane_has_a_distinct_name_and_source():
    names = [l["lane"] for l in rs.LANES]
    assert len(names) == len(set(names))
    srcs = [(l["artifact"], l["key"]) for l in rs.LANES]
    assert len(srcs) == len(set(srcs)), "two lanes reading the same key would double-count it"


def test_committed_artifacts_are_readable_and_sum():
    """The real repo state: every declared lane resolves, and the total is their sum to the cent."""
    rows = rs.ledgered()
    assert rows, "no lanes declared"
    for row, usd, err in rows:
        assert err is None, f"{row['lane']}: {err}"
        assert usd >= 0
    doc = rs.summary()
    assert doc["unreadable_lanes"] == []
    assert doc["realised_usd_ledgered"] == pytest.approx(
        round(sum(u for _, u, _ in rows), 2), abs=0.005)


def test_unreadable_lane_is_an_error_not_a_zero():
    """A missing artifact must NOT be read as 'this lane spent nothing'."""
    rows = rs.ledgered([{"lane": "ghost", "what": "-", "artifact": "research/modalities/no-such-file.json",
                         "key": "realised_usd", "provider": "vast", "ledger": "-"}])
    (_row, usd, err) = rows[0]
    assert usd is None and err, "an unreadable ledger reported a number"
    doc = rs.summary(lanes=[{"lane": "ghost", "what": "-",
                             "artifact": "research/modalities/no-such-file.json",
                             "key": "realised_usd", "provider": "vast", "ledger": "-"}])
    assert doc["unreadable_lanes"], "an unreadable lane vanished from the readout"
    assert doc["realised_usd_ledgered"] == 0.0
    # and the process says so, rather than exiting 0 with a confident total
    assert rs.main(["--json"]) in (0, 1)


def test_free_credit_is_never_added_to_realised_spend():
    """CLAUDE.md §6: GCP trial credit is a SEPARATE LEDGER. It must not move the realised figure."""
    doc = rs.summary()
    cred = doc["free_credit_separate_ledger"]
    assert cred, "credit state missing"
    credit_dollars = sum(float(c["spent_usd"]) for c in cred.values()
                         if isinstance(c.get("spent_usd"), (int, float)))
    assert credit_dollars > 0, "the fixture is not exercising the property"
    lane_sum = round(sum(l["usd"] for l in doc["lanes"]), 2)
    assert doc["realised_usd_ledgered"] == pytest.approx(lane_sum, abs=0.005)
    assert doc["realised_usd_best_estimate"] == pytest.approx(
        lane_sum + doc["attested_unledgered_usd"], abs=0.005)
    # the credit figure appears nowhere inside either total
    assert doc["realised_usd_best_estimate"] != pytest.approx(
        lane_sum + doc["attested_unledgered_usd"] + credit_dollars, abs=0.005)


def test_best_estimate_is_exactly_ledgered_plus_attested():
    doc = rs.summary()
    assert doc["realised_usd_best_estimate"] == pytest.approx(
        doc["realised_usd_ledgered"] + doc["attested_unledgered_usd"], abs=0.005)


def test_attested_entries_carry_a_source_and_a_remediation():
    """An attested-only lane is a defect register entry. Without a remediation it is just an excuse."""
    for a in rs.ATTESTED:
        assert isinstance(a.get("usd"), (int, float)) and a["usd"] >= 0
        assert a.get("read_from"), f"{a['lane']}: no source for its figure"
        assert a.get("closes_when"), f"{a['lane']}: no remediation — it would live here forever"


def test_committed_snapshot_is_internally_consistent_and_dated():
    """`realised-spend.json` is what STRATEGY.md quotes, so its own arithmetic must hold.

    It is NOT asserted equal to a live recomputation: the lanes bill continuously, so that test would be
    red most of the time and an always-red check is one nobody reads. The snapshot is allowed to lag; what
    it is not allowed to do is disagree with itself or hide when it was taken (`--check` prints the lag).
    """
    path = rs.READOUT_PATH
    assert os.path.exists(path), "run: python3 research/modalities/realised_spend.py --write"
    with open(path, encoding="utf-8") as fh:
        snap = json.load(fh)
    assert snap.get("_as_of_et") and "ET" in snap["_as_of_et"], "snapshot has no US-Eastern as-of stamp"
    assert snap["realised_usd_ledgered"] == pytest.approx(
        round(sum(l["usd"] for l in snap["lanes"]), 2), abs=0.005)
    assert snap["attested_unledgered_usd"] == pytest.approx(
        round(sum(a["usd"] for a in snap["attested_unledgered"]), 2), abs=0.005)
    assert snap["realised_usd_best_estimate"] == pytest.approx(
        snap["realised_usd_ledgered"] + snap["attested_unledgered_usd"], abs=0.005)


def test_drift_reports_the_lag_and_never_fails():
    """A lagging snapshot is expected; an INVISIBLE lag is the defect."""
    d = rs.drift()
    assert d["snapshot_readable"] is True
    assert "drift_usd" in d and "action" in d
    assert rs.main(["--check"]) == 0


def test_render_keeps_the_ledgers_visibly_apart():
    text = rs.render(rs.summary())
    assert "SEPARATE LEDGER" in text
    assert "MACHINE-LEDGERED" in text
    # the floor language is the honest one while any lane is unledgered
    if rs.ATTESTED:
        assert "FLOOR" in text and "defect register" in text.lower()
