#!/usr/bin/env python3
"""Tests for the ternary launch-attempt ledger.

WHY THIS IS TESTED AT ALL, given it is "just a log". Because the thing it replaces was also just a log —
`_last_launch.json`, written by the launcher — and its gap is what produced a wrong report on 2026-07-27: a
launch that dies BEFORE the launcher runs leaves that file untouched and hours stale, which reads as "no
launch was attempted". A record whose absence is indistinguishable from a normal state is worse than none,
so the properties that make this one unambiguous are pinned here.
"""
import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_launch_ledger as tll  # noqa: E402


@pytest.fixture()
def ledger(tmp_path):
    return str(tmp_path / "attempts.json")


def test_a_dispatched_launch_and_its_outcome_are_two_distinguishable_rows(ledger):
    """★ THE 2026-07-27 FAILURE, in one test. The gate cleared, dispatched, and the launch died — and
    afterwards every artifact looked like an ordinary hold. The ledger must make "authorised and dispatched"
    and "and then it died" two separate, explicit, still-present facts."""
    tll.record("dispatched", stage="market-gate", path=ledger,
               gate={"ratio_vs_basis": 1.261, "hold": False})
    tll.record("refused-on-price", stage="rent", path=ledger,
               gate={"ratio_vs_basis": 2.436, "hold": True}, n_requested=4, n_rented=0)
    rows = tll.load(ledger)["attempts"]
    assert [r["outcome"] for r in rows] == ["dispatched", "refused-on-price"]
    assert rows[0]["gate_ratio_vs_basis"] == 1.261, "the CLEAR that authorised it must survive"
    assert rows[1]["gate_ratio_vs_basis"] == 2.436
    # and the row explains itself without a second lookup
    assert "the guard working" in rows[1]["what_that_means"]


def test_the_outcome_vocabulary_is_closed_so_a_typo_cannot_invent_a_state(ledger):
    with pytest.raises(ValueError):
        tll.record("held", path=ledger)
    assert "refused-on-price" in tll.OUTCOMES and "launched" in tll.OUTCOMES


def test_history_is_appended_never_rewritten(ledger):
    """The defect the ledger exists to close was a MUTABLE single-snapshot file: the dead launch's HOLD
    overwrote the CLEAR that had authorised it, four minutes later, and the evidence was gone. Appending is
    the property that matters — an earlier row must never be editable by a later event."""
    for i in range(5):
        tll.record("dispatched", reason="n=%d" % i, path=ledger)
    rows = tll.load(ledger)["attempts"]
    assert [r["reason"] for r in rows] == ["n=%d" % i for i in range(5)], "newest LAST, nothing rewritten"


def test_the_ledger_is_bounded_so_it_stays_reviewable(ledger):
    for i in range(tll.MAX_ATTEMPTS + 12):
        tll.record("dispatched", reason="n=%d" % i, path=ledger)
    rows = tll.load(ledger)["attempts"]
    assert len(rows) == tll.MAX_ATTEMPTS
    assert rows[-1]["reason"] == "n=%d" % (tll.MAX_ATTEMPTS + 11), "the newest is always kept"


def test_times_are_us_eastern_12_hour_not_utc(ledger):
    """CLAUDE.md §1. The reader of this file is trimcrae, and a 24-hour UTC stamp is the exact thing that
    rule exists to stop. EDT = UTC-4, so 13:16 UTC is 9:16 AM ET — the timestamp of the launch this ledger
    was built because of."""
    import time
    e = tll.record("dispatched", path=ledger)
    assert e["et"].endswith(" ET") and (" AM " in e["et"] + " " or " PM " in e["et"] + " ")
    assert tll._et(time.strptime("2026-07-27T13:16:28Z", "%Y-%m-%dT%H:%M:%SZ")) == "9:16 AM ET"
    assert tll._et(time.strptime("2026-07-27T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ")) == "8:30 PM ET"
    assert tll._et(time.strptime("2026-07-27T16:05:00Z", "%Y-%m-%dT%H:%M:%SZ")) == "12:05 PM ET"


def test_the_summary_line_says_what_happened_without_opening_the_file(ledger):
    """`collect` prints this. If it did not carry the outcome and the board it faced, a reader would still
    have to know the ledger exists and go find it — which is the same failure one indirection further out."""
    tll.record("refused-on-price", stage="rent", path=ledger, n_requested=4, n_rented=0,
               gate={"ratio_vs_basis": 1.904}, reason="every offer above the buy line")
    s = tll.summary_line(ledger)
    assert "refused-on-price" in s and "0/4 rented" in s and "1.904x basis" in s and "ET" in s


def test_an_empty_or_corrupt_ledger_reports_that_rather_than_crashing(tmp_path):
    missing = str(tmp_path / "nope.json")
    assert "no launch attempt" in tll.summary_line(missing)
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert "no launch attempt" in tll.summary_line(str(bad))


@pytest.mark.committed_artifact
def test_the_committed_ledger_is_valid_and_records_the_lost_windows():
    """The real file in the repo. It is seeded with the two 2026-07-27 attempts reconstructed from the job
    logs — the evidence that the lane HAS lost cleared windows, which is the fact a future reader most needs
    and the one that no artifact carried at the time."""
    with open(tll.LEDGER) as fh:
        d = json.load(fh)
    rows = d["attempts"]
    assert rows, "the committed ledger must not be empty"
    assert all(r["outcome"] in tll.OUTCOMES for r in rows)
    lost = [r for r in rows if r["outcome"] == "refused-on-price"]
    # ⚠ THE SEEDED ROWS MUST BE PRESENT; THE TOTAL MUST BE FREE TO GROW (fixed 2026-07-30).
    # This asserted `len(lost) == 2`, which made a LEGITIMATE new refusal turn CI red: the guard declining
    # an over-line board is the system working, and a third one duly appeared and broke the build. A test
    # that goes red when the guard does its job trains a reader to ignore red builds, which is strictly
    # worse than the drift it was defending against. The invariant that actually matters is that the two
    # reconstructed 2026-07-27 windows are still there and still labelled as reconstructions.
    seeded = {r["et"]: r for r in lost if r.get("reconstructed_from_job_log")}
    assert set(seeded) == {"9:16 AM ET", "9:26 AM ET"}, \
        "both reconstructed 2026-07-27 refusals must remain in the ledger"
    assert len(lost) >= 2, "refusals only accumulate; a shrinking count means rows were dropped"
    assert all(r.get("reconstructed_from_job_log") for r in lost if r["et"] in seeded), \
        "a retroactively reconstructed row must SAY it was reconstructed, never pass as live telemetry"
    # A LIVE refusal must NOT claim to be a reconstruction — that is the direction that would launder a
    # made-up row into the record.
    live = [r for r in lost if r["et"] not in seeded]
    assert not any(r.get("reconstructed_from_job_log") for r in live)


# ---------------------------------------------------------------- the 11:10 AM ET ledger defect
def test_the_gates_own_sentence_is_copied_because_it_carries_the_diagnosis(ledger):
    """★★ THE DEFECT THIS FILE'S OWN AUTHOR SHIPPED (2026-07-27, 11:10 AM ET).

    The gate readout handed to that row contained, verbatim, "could not read the board (RuntimeError: vast
    API GET /search/asks/ -> 403 ...) — an unreadable market is not a cheap one". The ledger copied the
    numeric fields and `hold` and dropped `reason` — the only field that was prose and the only one that
    said WHY. The row therefore recorded `gate_hold: true` with no ratio beside it, and answering "was this
    the price guard or a broken launcher?" still required the job log. That is the exact failure the ledger
    exists to prevent, one level in."""
    gate = {"hold": True,
            "reason": "could not read the board (RuntimeError: vast API GET /search/asks/ -> 403: "
                      "<html>403 Forbidden</html>) — an unreadable market is not a cheap one"}
    e = tll.record("board-unreadable", stage="rent", path=ledger, gate=gate, n_requested=4, n_rented=0)
    assert "403" in e["gate_reason"], "the sentence that carries the diagnosis must survive into the row"
    s = tll.summary_line(ledger)
    assert "403" in s and "⛔ FAULT" in s, "and must be legible in the one line collect prints"
    assert "\n" not in s, "a multi-line provider error page must not break the summary line"


def test_no_outcome_names_two_possibilities(ledger):
    """`rented-nothing` used to mean "every offer above the buy line, OR creates failed". An outcome that
    names two causes names neither, and it was the only thing the ledger said about the 403. Every value is
    now a single fact — enforced, so the disjunction cannot come back by a well-meaning merge."""
    for outcome, meaning in tll.OUTCOMES.items():
        assert " or " not in meaning.lower().replace("authorisation", ""), \
            f"{outcome!r} describes more than one situation: {meaning!r}"
    assert "rented-nothing" not in tll.OUTCOMES


def test_a_price_hold_is_not_a_fault_but_an_unreadable_board_is(ledger):
    """The distinction the CI signal now turns on. Nothing affordable = wait, the work is checkpointed and
    the next tick re-checks. Board unreadable = we never learned what the market cost, so a cleared window
    can be lost without anyone noticing — which is what happened."""
    tll.record("refused-on-price", path=ledger)
    assert not tll.is_fault(ledger)
    assert "⏸ held" in tll.summary_line(ledger)
    tll.record("board-unreadable", path=ledger)
    assert tll.is_fault(ledger)
    assert "⛔ FAULT" in tll.summary_line(ledger)
    tll.record("launched", path=ledger, n_requested=4, n_rented=4)
    assert not tll.is_fault(ledger) and "✅" in tll.summary_line(ledger)


# =============================================================================================================
# ★★ THE 12:39 PM ET ROW — a `launched` that rented nothing, beside a board reading over the buy line
# =============================================================================================================
# On 2026-07-27 the valB_mini lane recorded three `launched` rows in 25 minutes for a FOUR-unit job. Only the
# first rented anything; the 12:29 and 12:39 ticks found every unit already running and rented ZERO. Both were
# filed as `launched` — whose meaning is literally "hosts were actually rented" — because the workflow derived
# the word from the rent step's exit code, and a launch with nothing to do exits 0.
#
# The 12:39 row then carried the launch job's advisory board snapshot: `gate_ratio_vs_basis: 2.032`,
# `gate_mean_usd_per_ns: 0.006931`, both above trimcrae's $0.006539/ns buy line. Read together with the word
# `launched`, the lane's own ledger said we had bought at 2.032x basis. We had not: we bought nothing, and the
# four hosts actually held were billing between 0.80x and 1.08x basis.
#
# These tests pin the two halves of the fix — the word cannot contradict the rental, and the row must carry
# what was PAID and not only what the board cost.
def test_launched_cannot_be_recorded_when_nothing_was_rented(ledger):
    """`launched` means "hosts were actually rented". Zero rentals is therefore not a `launched` row."""
    e = tll.record("launched", path=ledger, n_requested=0, n_rented=0)
    assert e["outcome"] == "nothing-to-launch", \
        "a launch that rented nothing because nothing needed renting must not be filed as `launched`"
    assert "nothing was spent" in e["what_that_means"]
    assert not tll.is_fault(ledger), "a satisfied lane is a normal state, not a fault"


def test_wanting_units_and_renting_none_is_a_fault_not_the_benign_word(ledger):
    """The two zero-rental cases must not collapse. Wanting nothing is benign; wanting four and getting none
    is unexplained, and the file's own rule is that an unrecognised failure is never filed as benign."""
    e = tll.record("launched", path=ledger, n_requested=4, n_rented=0)
    assert e["outcome"] == "submit-failed" and tll.is_fault(ledger)


def test_the_row_records_what_was_paid_not_only_what_the_board_cost(ledger):
    """The board mean and the rented rate are DIFFERENT QUANTITIES, and the row must say which is which.

    A gate's `mean_usd_per_ns` prices the n cheapest offers on the market at some instant; it is a property
    of the board and is never conditioned on a purchase. What we pay is read back off the live instance.
    """
    receipt = {"n_requested": 2, "n_rented": 2, "rented": [
        {"unit_id": "u1", "instance": 1, "gpu": "RTX 5090", "usd_per_ns": 0.00273, "x_basis": 0.8,
         "over_buy_line": False},
        {"unit_id": "u2", "instance": 2, "gpu": "RTX 3090", "usd_per_ns": 0.003576, "x_basis": 1.048,
         "over_buy_line": False}]}
    # a board that was expensive at the moment of the snapshot...
    gate = {"ratio_vs_basis": 2.032, "mean_usd_per_ns": 0.006931, "hold": True, "reason": "board is dear"}
    e = tll.record("launched", path=ledger, gate=gate, receipt=receipt)
    assert e["outcome"] == "launched" and e["n_rented"] == 2
    # ...must not be mistakable for what we paid, which was well under the line
    assert e["rented_max_usd_per_ns"] == 0.003576
    assert e["rented_any_over_buy_line"] is False
    line = tll.summary_line(ledger)
    assert "PAID up to $0.003576/ns" in line, "the summary must lead with what was actually paid"
    assert "board(not paid)" in line, \
        "the board figure must be labelled as the market, or a reader takes it for the purchase"


def test_a_zero_rental_row_says_it_paid_nothing(ledger):
    """The precise misreading being fixed: a row whose only $/ns figure was a 2.032x board mean."""
    tll.record("launched", path=ledger, n_requested=0, n_rented=0,
               gate={"ratio_vs_basis": 2.032, "mean_usd_per_ns": 0.006931, "hold": True})
    line = tll.summary_line(ledger)
    assert "PAID $0 (nothing rented)" in line
    assert "board(not paid) 2.032x" in line


def test_the_receipt_supplies_the_counts_so_the_shell_need_not_guess(ledger):
    """The counts come from the launcher, which knows the rental, rather than from a workflow step's exit
    code, which cannot see it. That substitution is the whole root cause."""
    e = tll.record("launched", path=ledger,
                   receipt={"n_requested": 4, "n_rented": 4, "rented": [{"unit_id": "u", "usd_per_ns": 0.003}]})
    assert e["n_requested"] == 4 and e["n_rented"] == 4


def test_a_gate_that_could_not_run_is_not_a_gate_that_refused(ledger):
    """★★ THE 2026-07-27 6:01 PM ET MISREPORT, in one test. `task=triangle-smoke` (run 30309074338) died
    inside the step named "ATOM-MAP GATE — the launch cannot rent until the map is proven complete" and was
    filed as `failed` / "job status failure". Nothing in the row could tell that from the mapper having come
    up short on T3's closing edge, so it was read as a chemistry result. It was a Docker Hub login timeout;
    the four maps had measured 59/59 heavy atoms complete three hours earlier.

    The two must be separately nameable, and — the part that matters for how the row is acted on — a
    measured refusal must NOT be a fault, while a gate that never ran must be one. Same red job, opposite
    remedies: one is a finding about the edge, the other is a retry."""
    refused = tll.record("map-gate-refused", path=ledger,
                         reason="task=triangle; atom-map gate: refused: cmpd1->cmpd4prime 17/20 heavy mapped")
    could_not = tll.record("failed", path=ledger,
                           reason="task=triangle-smoke; atom-map gate: could-not-run: docker login")
    assert refused["outcome"] != could_not["outcome"]
    # The refusal is the guard working on the science, not the pipeline breaking — so it must not be swept
    # into the fault bucket that callers use to decide "is something wrong?".
    assert "map-gate-refused" not in tll.FAULTS
    assert "failed" in tll.FAULTS
    # ...and each row must explain itself without opening the run.
    assert "SHORT map" in refused["what_that_means"]
    assert "Re-running will not help" in refused["what_that_means"]
    assert "17/20 heavy mapped" in refused["reason"]
    assert "docker login" in could_not["reason"]


def test_the_three_zero_rental_outcomes_do_not_render_alike(ledger):
    """CLAUDE.md §1: a row we are paying and a row the gate refused must never render alike — one glyph, one
    meaning. All three of these rented nothing and spent $0, and each calls for a DIFFERENT next action:
    a price hold self-heals on the next tick, a launched row is normal green, and a map refusal will be
    exactly as short an hour later and needs a person to read the chemistry. Three glyphs."""
    marks = {}
    for outcome, kw in (("refused-on-price", {"n_requested": 4, "n_rented": 0}),
                        ("map-gate-refused", {"n_requested": 4, "n_rented": 0}),
                        ("failed", {})):
        tll.record(outcome, path=ledger, **kw)
        marks[outcome] = tll.summary_line(ledger).split("—")[0]
    assert len(set(marks.values())) == 3, marks
    assert "🔬" in marks["map-gate-refused"]
    assert "✅" not in marks["map-gate-refused"], "a blocked edge must not wear the healthy-launch glyph"
    assert "⏸" not in marks["map-gate-refused"], "held promises a retry that cannot help a short map"


# =============================================================================================================
# ★★ THE 2026-07-28 OUTAGE — the "append-only" ledger was a RING BUFFER, and it ate a pinned row
# =============================================================================================================
# For ~90 minutes (4:12–6:11 AM ET) every task in `gpu-ternary-fep-vast.yml` was red, because the `test` job
# gates them all and `test_the_committed_ledger_is_valid_and_records_the_lost_windows` had started failing.
#
# THE CAUSE WAS NOT A MERGE, A RACE OR A STALE CHECKOUT. It was `(attempts + [e])[-MAX_ATTEMPTS:]`. The file
# had reached the 60-row cap at 07:08 UTC, so from that moment every single append silently deleted the row
# at the HEAD of the list. At 08:12 the head was the 9:16 AM ET `refused-on-price` row — one of the four
# reconstructed rows this ledger exists to preserve, and one the test pins by name.
#
# The discriminating observations, all reproduced by the tests below:
#   * every commit through the window has EXACTLY 60 rows — the signature of a cap, not of a lost merge;
#   * the losing commit still contains the row written by the commit immediately before it, so its base was
#     current — which refutes stale-checkout and lost-race outright;
#   * the diff is exactly {one row removed from the front, one added at the back} = `[-60:]`;
#   * the hand restore left the file at 61 rows, and the next append 73 seconds later evicted TWO rows
#     (61 + 1 - 60), undoing the restore and re-reddening the lane.
def _fill(ledger, n, **kw):
    for i in range(n):
        tll.record("dispatched", reason="routine n=%d" % i, path=ledger, **kw)


def test_the_cap_can_never_evict_an_evidence_row(ledger):
    """★ THE REGRESSION. Fill the ledger to the cap with the OLDEST row marked as evidence, then append one
    more. Under the old ring buffer the evidence row was the one that went, because it was oldest. It must
    now be a routine row that ages out instead, and the evidence row must still be there."""
    tll.record("refused-on-price", reason="the 9:16 AM ET row", path=ledger)
    rows = tll.load(ledger)["attempts"]
    rows[0]["reconstructed_from_job_log"] = True
    with open(ledger, "w") as fh:
        json.dump({"attempts": rows}, fh)
    _fill(ledger, tll.MAX_ATTEMPTS - 1)
    assert len(tll.load(ledger)["attempts"]) == tll.MAX_ATTEMPTS, "precondition: the file is exactly full"

    tll.record("launched", reason="the 4:12 AM ET append", path=ledger, n_requested=1, n_rented=1)

    after = tll.load(ledger)["attempts"]
    assert len(after) == tll.MAX_ATTEMPTS, "the cap still holds"
    assert after[0].get("reconstructed_from_job_log"), \
        "the cap evicted the evidence row — this is the 2026-07-28 outage"
    assert after[0]["reason"] == "the 9:16 AM ET row"
    assert after[-1]["reason"] == "the 4:12 AM ET append", "the newest is still kept"
    assert "routine n=0" not in [r.get("reason") for r in after], "a ROUTINE row is what should have gone"


def test_evidence_survives_even_when_it_leaves_the_file_over_the_cap(ledger):
    """When evidence alone exceeds the cap the cap yields, not the evidence. A readability preference must
    never be the thing that deletes the record it is keeping — that inversion is the whole defect."""
    n_before = tll.MAX_ATTEMPTS + 5
    with open(ledger, "w") as fh:
        json.dump({"attempts": [{"utc": "2026-07-27T%02d:%02d:00Z" % (i // 60, i % 60),
                                 "outcome": "dispatched", "reason": "evidence n=%d" % i, "retain": True}
                                for i in range(n_before)]}, fh)
    tll.record("dispatched", reason="one more", path=ledger)
    after = tll.load(ledger)["attempts"]
    assert len(after) == n_before + 1 > tll.MAX_ATTEMPTS
    assert all(r.get("retain") or r["reason"] == "one more" for r in after)
    assert "_aged_out" not in tll.load(ledger), "nothing was aged out, so nothing is claimed to have been"


def test_aging_a_row_out_is_recorded_in_the_file_never_silent(ledger):
    """90 minutes went to accounting for a diff nobody could explain. A deletion the file does not mention
    is only visible in `git log`, and only to someone who already suspects it."""
    _fill(ledger, tll.MAX_ATTEMPTS)
    assert "_aged_out" not in tll.load(ledger), "nothing has been aged out yet"
    tll.record("dispatched", reason="overflow", path=ledger)
    aged = tll.load(ledger)["_aged_out"]
    assert aged["n_total"] == 1 and aged["through_utc"]
    assert "recover" in aged["_what"].lower()
    tll.record("dispatched", reason="overflow 2", path=ledger)
    assert tll.load(ledger)["_aged_out"]["n_total"] == 2, "the count accumulates across writes"


def test_two_concurrent_appends_both_survive(ledger):
    """★ THE OTHER WAY A ROW CAN VANISH, closed at the same time. `record` rewrites the WHOLE file from a
    list it has just read, so two writers that read the same base each append their own row and the second
    write erases the first one's. The read is therefore inside the same exclusive section as the write.

    The race is made deterministic rather than hoped for: `load` is slowed so both writers are certainly
    inside their read-modify-write window at once. With the section locked, the second writer blocks and
    then reads a base that already contains the first writer's row.
    """
    import threading
    real_load, barrier = tll.load, threading.Barrier(2)

    def slow_load(path=tll.LEDGER):
        d = real_load(path)
        try:                       # both writers are now certainly mid-read-modify-write, if unserialised
            barrier.wait(timeout=2)
        except threading.BrokenBarrierError:
            pass                   # serialised — which is the point of the fix, not a failure
        time.sleep(0.15)
        return d

    tll.load = slow_load
    try:
        threads = [threading.Thread(target=tll.record, args=("dispatched",),
                                    kwargs={"reason": "writer-%d" % i, "path": ledger}) for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
    finally:
        tll.load = real_load

    reasons = sorted(r["reason"] for r in tll.load(ledger)["attempts"])
    assert reasons == ["writer-0", "writer-1"], \
        "a concurrent append overwrote the other writer's row: %r" % (reasons,)


def test_merge_is_a_union_keyed_on_utc_outcome_run_url():
    """The established reconciliation rule for this file — the same triple the 2026-07-28 hand restore used.
    Two divergent copies union instead of conflicting, and the union is ordered oldest-first."""
    a = [{"utc": "2026-07-27T13:16:28Z", "outcome": "refused-on-price", "run_url": "r1", "reason": "rich"},
         {"utc": "2026-07-28T08:08:09Z", "outcome": "dispatched", "run_url": "r2"}]
    b = [{"utc": "2026-07-27T13:16:28Z", "outcome": "refused-on-price", "run_url": "r1"},   # dup of a[0]
         {"utc": "2026-07-27T15:07:21Z", "outcome": "dispatched", "run_url": "r3"}]         # only in b
    out = tll.merge(a, b)
    assert [e["utc"] for e in out] == ["2026-07-27T13:16:28Z", "2026-07-27T15:07:21Z", "2026-07-28T08:08:09Z"]
    assert out[0]["reason"] == "rich", "the richer copy of a duplicated row wins"
    # ...and a fresh append is NOT deduplicated: several attempts can share a second, an outcome and a run.
    assert tll.key(a[0]) == ("2026-07-27T13:16:28Z", "refused-on-price", "r1")


def test_repair_restores_a_missing_evidence_row_from_git_history(tmp_path):
    """★ WHAT THE OUTAGE ACTUALLY NEEDED. The row was never gone — every version of the ledger is a blob in
    the repo — but nothing could get it back out, so it was restored by hand from a diff at 6:10 AM, and the
    hand restore left the file one row over the cap and was undone 73 seconds later by the next append."""
    import subprocess
    repo = tmp_path / "repo"
    repo.mkdir()
    led = repo / "ternary-vast-launch-attempts.json"

    def git(*args):
        subprocess.run(("git", "-C", str(repo)) + args, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    tll.record("refused-on-price", reason="9:16 AM ET, reconstructed", path=str(led))
    d = tll.load(str(led))
    d["attempts"][0]["reconstructed_from_job_log"] = True
    with open(led, "w") as fh:
        json.dump(d, fh)
    git("add", "-A")
    git("commit", "-qm", "seed")

    # ...now the cap-style loss: the evidence row is dropped and the file committed without it. The routine
    # row that replaces it is stamped strictly LATER than the evidence row (which `record` stamped with the
    # wall clock), so the union's oldest-first ordering is asserted against a known order.
    seeded_utc = d["attempts"][0]["utc"]
    with open(led, "w") as fh:
        json.dump({"attempts": [{"utc": "2099-01-01T00:00:00Z", "outcome": "launched", "reason": "routine"}]},
                  fh)
    assert seeded_utc < "2099-01-01T00:00:00Z"
    git("add", "-A")
    git("commit", "-qm", "a launch job dropped it")

    missing = tll.verify(str(led))
    assert [e["reason"] for e in missing] == ["9:16 AM ET, reconstructed"]
    restored = tll.repair(str(led))
    assert [e["reason"] for e in restored] == ["9:16 AM ET, reconstructed"]
    rows = tll.load(str(led))["attempts"]
    assert [r.get("reason") for r in rows] == ["9:16 AM ET, reconstructed", "routine"], "union, oldest first"
    assert tll.verify(str(led)) == [], "and the file is healthy afterwards"
    assert tll.repair(str(led)) == [], "repair is idempotent"


def test_verify_is_read_only_and_says_nothing_is_missing_when_nothing_is(tmp_path):
    """`--verify` gates a CI job, so it must not itself mutate the artifact it is checking, and it must not
    explode outside a git checkout — a recovery tool that raises where it is needed is no tool."""
    led = str(tmp_path / "attempts.json")          # not in any repo
    tll.record("dispatched", path=led)
    before = open(led).read()
    assert tll.verify(led) == []
    assert tll.evidence_from_git(led) == []
    assert open(led).read() == before


@pytest.mark.committed_artifact
def test_the_committed_ledger_still_holds_all_four_reconstructed_rows():
    """`_seeded` says "the first four rows are RECONSTRUCTED". By 6:11 AM ET on 2026-07-28 the cap had eaten
    three of them and the file's own note described rows that were not there. All four are evidence, and
    evidence is now exempt from the cap."""
    d = json.load(open(tll.LEDGER))
    seeded = [r for r in d["attempts"] if r.get("reconstructed_from_job_log")]
    assert len(seeded) == 4, "the four rows this ledger exists to preserve"
    assert [r["et"] for r in seeded] == ["9:13 AM ET", "9:16 AM ET", "9:23 AM ET", "9:26 AM ET"]
    assert all(tll.is_evidence(r) for r in seeded)


def test_merging_our_row_onto_origins_copy_is_idempotent(tmp_path):
    """★ THE RETRY LOOP'S OWN HAZARD, closed with the same union. The workflow recovered from a lost push
    by re-running `--record` — but `record` stamps `utc` from the wall clock, so every retry minted a row
    with a different key, and five half-successful retries could leave five rows for one launch. Unioning
    the row we already wrote onto origin's current file produces exactly one row however often it runs, and
    picks up the rows the other lane pushed while we were racing it."""
    ours, theirs = str(tmp_path / "ours.json"), str(tmp_path / "ledger.json")
    tll.record("launched", run_url="run-A", path=ours, n_requested=1, n_rented=1)
    # origin moved on while we were pushing: another lane appended its own row.
    with open(theirs, "w") as fh:
        json.dump({"attempts": [{"utc": "2026-07-28T09:00:00Z", "outcome": "dispatched",
                                 "run_url": "run-B"}]}, fh)

    added = tll.merge_from(ours, theirs)
    assert len(added) == 1
    assert sorted(r.get("run_url") for r in tll.load(theirs)["attempts"]) == ["run-A", "run-B"], \
        "our row and theirs both survive the race"
    # ...and running it again — as the loop does on the next failed push — changes nothing.
    assert tll.merge_from(ours, theirs) == []
    assert len(tll.load(theirs)["attempts"]) == 2, "a retry must not duplicate the row"
