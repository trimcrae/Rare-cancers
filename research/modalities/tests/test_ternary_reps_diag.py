"""The $0 forensic that answers WHY an arm commits nothing (research/modalities/ternary_reps_diag.py).

Only the pure parts are exercised here — the S3 and provider reads are the job of the CI task. What must not
be allowed to rot is the arm grouping (the entire diagnosis is a comparison BETWEEN arms, so a mis-grouped
unit silently destroys the comparison) and the credential allow-list.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_reps_diag as diag  # noqa: E402


def test_every_replicate_unit_is_assigned_to_an_arm():
    """A unit that groups as None would vanish from the comparison rather than break it loudly."""
    import ternary_vast_launch as tv
    uids = [tv.unit_id(l, s, d, 4.0, 1.0, "edge_reps") for (l, s, d) in tv.units_for("edge_reps")]
    arms = [diag.arm_of(u) for u in uids]
    assert arms.count("ternary") == 2 and arms.count("binary") == 2, arms
    # and the seed-0 edge, whose solvent leg is the one that cancels out of the cycle
    edge = [tv.unit_id(l, s, d, 4.0, 1.0, "edge") for (l, s, d) in tv.units_for("edge")]
    assert sorted(diag.arm_of(u) for u in edge) == ["binary", "solvent", "ternary"]


def test_the_last_line_is_the_last_NON_BLANK_line():
    """The comparison is 'did every ternary attempt end on the same line'. A trailing newline answering
    '' for every log would make every arm look identical, which is the one wrong answer that looks fine."""
    assert diag.last_meaningful_line("a\nINFO: Adding forces\n\n   \n") == "INFO: Adding forces"
    assert diag.last_meaningful_line("") == ""
    assert diag.last_meaningful_line(None) == ""


def test_the_printed_instance_record_never_leaks_a_credential():
    """A diagnostic's output gets pasted into commit messages and issues, and a Vast instance record carries
    jupyter_token / ssh_host / public_ipaddr. Allow-list, not redaction-list."""
    import json
    blob = json.dumps(diag.safe_instance({
        "id": 1, "cpu_ram": 64, "disk_space": 60, "gpu_name": "RTX 4090",
        "jupyter_token": "SECRET", "ssh_host": "1.2.3.4", "public_ipaddr": "1.2.3.4", "ssh_port": 22}))
    for leaked in ("SECRET", "1.2.3.4", "jupyter_token", "ssh_host", "public_ipaddr"):
        assert leaked not in blob
    # ...and it must still carry the fields the diagnosis actually turns on
    for kept in ("cpu_ram", "disk_space", "gpu_name"):
        assert kept in blob


def test_the_console_path_is_imported_rather_than_re_implemented():
    """CLAUDE.md §1. Vast's request-logs flow has two non-obvious steps (the PUT only TRIGGERS collection and
    returns a URL; that URL is empty for several seconds and must be polled). A second copy would get one of
    them wrong and report 'no logs' for a container that had plenty."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "ternary_reps_diag.py")).read()
    assert "from nrv04_vast_launch import _vast_instance_logs" in src
    assert "request_logs" not in src.split('"""', 2)[-1].split("def console")[-1].split("\ndef ")[0] \
        .replace("`request_logs`", ""), "the endpoint must be called through the reviewed helper"


# ── the status.json breadcrumb (added 2026-08-01, after it cost a rung) ──────────────────────────────────
#
# ★★ WHAT IT COST. The 5a-KS prune smoke rented instance 46459452 at 10:02 PM ET, billed, and produced
# NOTHING: `n_attempts_archived` unchanged at 61, `log_age_min` still counting from 2026-07-26, `leg.json`
# untouched, `instance` gone by morning. `run_ternary_leg.sh` archives the previous run.log and calls
# `mark start` at the very top, so a unit whose archive count AND log age are both unchanged never reached
# the script's first line — and this diagnostic, reading run.log / leg.json / attempts / commits / the
# instance record, printed a picture IDENTICAL to "no rental ever happened". `status.json` is the only
# thing `fail()` writes in that window, and for `fail cuda-probe` it is the ONLY record at all, because that
# branch deliberately writes no leg.json so the launcher re-places the unit elsewhere.

def test_the_diag_reads_the_status_breadcrumb():
    src = open(diag.__file__).read()
    assert "def status_breadcrumb(" in src
    assert "status.json" in src
    body = src[src.index("def diagnose("):]
    assert "status_breadcrumb(uid" in body, "the breadcrumb must be collected per unit, not just defined"


def test_the_breadcrumb_is_in_the_committed_record_not_only_the_console():
    """The console scrolls and needs an authenticated log download; the JSON artifact is what a later
    session reads. A field that exists only in stdout is a field nobody will have."""
    src = open(diag.__file__).read()
    body = src[src.index("def diagnose("):]
    assert '"status_breadcrumb": crumb' in body


def test_an_ABSENT_breadcrumb_is_labelled_rather_than_omitted():
    """§4: an absent reading is not a reading of absence. 'no status.json' and 'a status.json saying
    cuda-probe' are opposite diagnoses, and a key that only appears on failure lets a reader mistake a
    missing collector for a healthy unit."""
    src = open(diag.__file__).read()
    assert '{"_absent"' in src
    body = src[src.index("def diagnose("):]
    assert "status.json: ABSENT" in body, "the absent case must print, not fall through silently"


def test_the_breadcrumb_never_raises_because_a_diagnostic_must_not_die_on_a_missing_key():
    """A healthy unit has no status.json at all, which is the common case — so the reader must return the
    absence rather than propagate the S3 404."""
    src = open(diag.__file__).read()
    fn = src[src.index("def status_breadcrumb("):src.index("def console(")]
    assert "except Exception" in fn and "return {\"_absent\"" in fn


# ── the ACCOUNT census (added 2026-08-01, the other half of the same incident) ───────────────────────────
#
# ★★ THE BREADCRUMB SAYS WHAT THE HOST DID; THE CENSUS SAYS WHETHER THE HOST IS STILL BEING PAID FOR.
# Instance 46459452 was rented for mode `5aks_smoke`. `collect` enumerates the units of mode `5aks`, so its
# board could not have shown that host whether it was alive or dead — and a reader who concluded "gone"
# from not seeing it there would have been guessing. Absence from a per-mode board is not absence from the
# account (CLAUDE.md §4a).

def _census_code():
    """The census function's CODE, with its docstring removed.

    The docstring recounts the incident and therefore contains the very words ("destroy", "unit_hosts")
    these tests forbid in the code — a prose-vs-code test that reads the prose fails on the explanation
    instead of on the behaviour."""
    src = open(diag.__file__).read()
    fn = src[src.index("def account_census("):src.index("def console(")]
    head, _, rest = fn.partition('"""')
    _doc, _, body = rest.partition('"""')
    return head + body


def test_the_census_asks_the_account_not_one_modes_units():
    """`unit_hosts` filters GET /instances/ by label AND by the unit ids of one mode. The census must not
    go through it, or it inherits exactly the blindness it exists to remove."""
    fn = _census_code()
    assert 'tv._vast_request("GET", "/instances/"' in fn
    assert "unit_hosts" not in fn, "the census must not be built on the per-mode filter"


def test_the_census_is_read_only():
    """Reaping is vast_idle_guard.py's job. Two components empowered to destroy is how they start
    disagreeing about what to kill — and this one runs unattended in a forensic step."""
    fn = _census_code()
    for mutating in ("DELETE", '"PUT"', "destroy"):
        assert mutating not in fn, f"the census must never {mutating}"


def test_an_asked_about_instance_gets_an_EXPLICIT_present_or_absent():
    """The whole point is to replace 'I did not find it in a list' with an answer. A census that only prints
    what IS held leaves the reader doing the same silent inference that lost the forensic."""
    fn = _census_code()
    assert '"present": rec is not None' in fn
    assert "ABSENT from the account" in fn and "PRESENT" in fn


def test_no_key_is_reported_as_UNREADABLE_rather_than_as_an_empty_account():
    """§4a again, and it is the dangerous direction here: an empty census with no credential looks exactly
    like a clean account, which would say 'nothing is billing' about a fleet nobody could see."""
    import ternary_reps_diag as d
    saved = os.environ.pop("VAST_API_KEY", None)
    try:
        out = d.account_census()
    finally:
        if saved is not None:
            os.environ["VAST_API_KEY"] = saved
    assert out.get("error"), "a missing key must be an error field, not an empty instance list"
    assert out["n_instances"] is None, "n_instances must stay UNKNOWN, never 0"


def test_uptime_and_spend_stay_None_when_the_record_cannot_supply_them():
    """A fabricated 0 in a money column is worse than a blank one: it sums."""
    fn = _census_code()
    assert 'row["uptime_h"] = None' in fn and 'row["spend_so_far_usd"] = None' in fn
