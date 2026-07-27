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
