#!/usr/bin/env python3
"""⛔⛔ THE NO-GPU BAN IS ENFORCED, NOT MERELY RECORDED.

trimcrae, 2026-09-02: **"You shouldn't be doing any GPU runs as part of this automation."**

★★ WHY THIS FILE EXISTS AT ALL, IN THE REPOSITORY'S OWN WORDS. `autonomy-state.json`'s
`gpu_spend_prohibited._ENFORCEMENT_IS_NOT_THIS_FIELD` says: *"RECORDED IS NOT ENFORCED, AND THIS
REPOSITORY HAS ALREADY PAID FOR THAT GAP TWICE — `subagent_width` was a governed number that `grep`
proved no code read, and `max_versions_per_paper` was measured on this same day to be enforced by
nothing while a paper carried 11 versions against a cap of 3."* Two halves are therefore measured here,
and the second is the one those two incidents lacked:

  1. THE GATE'S OWN LOGIC — every way the read can go wrong REFUSES, and `active: false` read out of a
     real file is the only thing that permits.
  2. THE WIRING — each launch path still calls the gate, and no NEW GPU-billing path has appeared
     ungated. A gate nothing calls is exactly `subagent_width` again.

⚠ THESE TESTS BIND THE REAL FUNCTIONS AT IMPORT (`_real_read_ban`). `research/modalities/tests/conftest.py`
autouse-neutralises the ban so the lanes' rental MECHANICS can be unit-tested; that fixture is scoped to
that suite and cannot reach this file, and every test here that needs the true reading re-patches the real
function into place explicitly. The BAN's own behaviour is never measured against a stub.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

_HERE = pathlib.Path(__file__).resolve().parent
_AUTONOMY = _HERE.parent
_REPO = _AUTONOMY.parent.parent
sys.path.insert(0, str(_AUTONOMY))

import gpu_ban  # noqa: E402

#: ⛔ THE REAL FUNCTION, BOUND BEFORE ANY FIXTURE CAN REPLACE IT — same discipline as
#: `test_vast_account_rental_hold._real_hold`, and for the same reason.
_real_read_ban = gpu_ban.read_ban

_STATE = _AUTONOMY / "autonomy-state.json"


def _write(tmp_path, doc) -> str:
    p = tmp_path / "autonomy-state.json"
    p.write_text(doc if isinstance(doc, str) else json.dumps(doc), encoding="utf-8")
    return str(p)


# =============================================================================================================
# 1 · FAIL CLOSED — "AN ABSENT READING IS NOT A READING OF ABSENCE" (CLAUDE.md §4)
# =============================================================================================================

def test_a_missing_state_file_refuses(tmp_path):
    r = _real_read_ban(str(tmp_path / "nope.json"))
    assert r["refuses"] is True
    assert "MISSING" in r["why"]


def test_an_unparseable_state_file_refuses(tmp_path):
    r = _real_read_ban(_write(tmp_path, "{ this is not json"))
    assert r["refuses"] is True
    assert "could not be parsed" in r["why"]


def test_a_state_file_that_is_not_an_object_refuses(tmp_path):
    r = _real_read_ban(_write(tmp_path, [1, 2, 3]))
    assert r["refuses"] is True


def test_a_deleted_ban_block_refuses(tmp_path):
    """⛔ DELETING THE PROHIBITION IS NOT LIFTING IT. A record that was never written and one that was
    removed read identically from here, so the only safe answer to both is no."""
    r = _real_read_ban(_write(tmp_path, {"backoff_level": 0}))
    assert r["refuses"] is True
    assert "ABSENT" in r["why"]


def test_a_ban_block_that_is_not_an_object_refuses(tmp_path):
    r = _real_read_ban(_write(tmp_path, {gpu_ban.BAN_KEY: "no gpu"}))
    assert r["refuses"] is True


def test_a_deleted_active_field_refuses(tmp_path):
    r = _real_read_ban(_write(tmp_path, {gpu_ban.BAN_KEY: {"ceiling_usd": 0}}))
    assert r["refuses"] is True
    assert "active` is ABSENT" in r["why"]


@pytest.mark.parametrize("bad", ["false", "no", 0, 1, None, [], {}])
def test_a_non_boolean_active_refuses_rather_than_being_coerced(tmp_path, bad):
    """⛔ NO TRUTHINESS RULE. Under coercion `active: "false"` (a non-empty string) would mean TRUE and
    `active: 0` would mean FALSE — a spend permission decided by JSON typing accidents."""
    r = _real_read_ban(_write(tmp_path, {gpu_ban.BAN_KEY: {"active": bad}}))
    assert r["refuses"] is True
    assert "not a boolean" in r["why"]


def test_active_true_refuses_and_quotes_the_record_rather_than_restating_it(tmp_path):
    r = _real_read_ban(_write(tmp_path, {gpu_ban.BAN_KEY: {
        "active": True, "verbatim": "NO GPU AT ALL", "set_by": "somebody", "scope": "everything"}}))
    assert r["refuses"] is True
    assert "NO GPU AT ALL" in r["why"] and "somebody" in r["why"] and "everything" in r["why"]


def test_active_false_is_the_only_thing_that_permits(tmp_path):
    r = _real_read_ban(_write(tmp_path, {gpu_ban.BAN_KEY: {"active": False}}))
    assert r["refuses"] is False


# =============================================================================================================
# 2 · THE TWO CALLER SHAPES
# =============================================================================================================

def test_assert_permitted_raises_a_distinct_type_and_returns_the_record_when_lifted(tmp_path, monkeypatch):
    monkeypatch.setattr(gpu_ban, "read_ban", _real_read_ban)
    banned = _write(tmp_path, {gpu_ban.BAN_KEY: {"active": True, "verbatim": "no"}})
    with pytest.raises(gpu_ban.GPUSpendProhibited):
        gpu_ban.assert_permitted("a rental", state_path=banned)
    lifted_dir = tmp_path / "lifted"
    lifted_dir.mkdir()
    rec = gpu_ban.assert_permitted(
        "a rental", state_path=_write(lifted_dir, {gpu_ban.BAN_KEY: {"active": False}}))
    assert rec == {"active": False}


def test_refusal_never_raises_and_returns_none_when_permitted(tmp_path, monkeypatch):
    """`relaunch_market_gate.gate` returns a `(hold, doc)` pair; a raise there would read as a launcher
    fault rather than as a standing refusal, which is the ambiguity `NoQualifyingOffer` exists to remove."""
    monkeypatch.setattr(gpu_ban, "read_ban", _real_read_ban)
    assert gpu_ban.refusal("x", state_path=_write(tmp_path, {gpu_ban.BAN_KEY: {"active": False}})) is None
    msg = gpu_ban.refusal("x", state_path=str(tmp_path / "missing.json"))
    assert msg and "REFUSED: x" in msg


def test_the_refusal_message_says_a_price_cannot_clear_it(tmp_path, monkeypatch):
    """★ THE ORDERING, IN THE MESSAGE ITSELF. The cycle that nearly bought the $25.45 rental reasoned
    correctly from a dollar ceiling; the refusal must tell the next one that no dollar figure applies."""
    monkeypatch.setattr(gpu_ban, "read_ban", _real_read_ban)
    msg = gpu_ban.refusal("a rental", state_path=_write(tmp_path, {gpu_ban.BAN_KEY: {"active": True}}))
    assert "CATEGORY ban, not a budget" in msg
    assert "$/ns" in msg


@pytest.mark.parametrize("active,code", [(True, 3), (False, 0)])
def test_the_cli_exit_code_is_what_a_workflow_step_reads(tmp_path, monkeypatch, active, code):
    """The GCP and Modal workflows have no Python between the runner and the meter, so the exit code IS
    the gate there. 3 rather than 1, so a refusal is never confused with an interpreter crash."""
    monkeypatch.setattr(gpu_ban, "read_ban", _real_read_ban)
    assert gpu_ban.main(["--context", "wf", "--state",
                         _write(tmp_path, {gpu_ban.BAN_KEY: {"active": active}})]) == code


def test_the_cli_runs_as_a_subprocess_the_way_a_workflow_calls_it():
    """⚠ NOT THE SAME TEST AS THE ONE ABOVE. The workflows shell out; an import-time break in this module
    would leave `main()` green and every workflow ungated."""
    p = subprocess.run([sys.executable, str(_AUTONOMY / "gpu_ban.py"), "--context", "ci"],
                       capture_output=True, text=True)
    assert p.returncode == 3, p.stdout + p.stderr
    assert "NO GPU RUNS" in p.stderr


# =============================================================================================================
# 3 · THE COMMITTED STATE — this is the test that a mutation of the real record reddens
# =============================================================================================================

def test_the_committed_state_still_refuses_every_gpu_rental(monkeypatch):
    """⛔ MUTATE THE FLAG, DELETE THE FIELD OR CORRUPT THE FILE AND THIS GOES RED. It reads the real
    committed `autonomy-state.json`, not a fixture — the ban is a fact about this repository's HEAD."""
    monkeypatch.setattr(gpu_ban, "read_ban", _real_read_ban)
    r = _real_read_ban()
    assert r["refuses"] is True, (
        "`gpu_spend_prohibited` no longer refuses. If trimcrae lifted the ban that is his call and this "
        "test is what records it; if a cycle lifted it to unblock itself, that is the shape "
        "`amendment_guard` refuses.")
    assert r["record"]["ceiling_usd"] == 0
    assert "any GPU runs" in r["record"]["verbatim"]


def test_the_ban_is_not_a_subclass_of_the_quiet_market_refusals():
    """⛔ A LANE THAT TREATS AN UNAFFORDABLE MARKET AS 'quiet, retry next tick' MUST NOT DO THAT HERE.
    `NoQualifyingOffer` and its two subclasses are deliberately quiet in every lane's `except`; the ban is
    not a market condition and a silent forever-retry would hide it."""
    assert gpu_ban.GPUSpendProhibited.__bases__ == (RuntimeError,)


# =============================================================================================================
# 4 · THE WIRING — the half `subagent_width` and `max_versions_per_paper` both lacked
# =============================================================================================================

_GB = (_REPO / "research/modalities/gpu_backend.py").read_text(encoding="utf-8")
_SM = (_REPO / "research/modalities/sagemaker_submit.py").read_text(encoding="utf-8")
_RMG = (_REPO / "research/modalities/relaunch_market_gate.py").read_text(encoding="utf-8")


def test_the_vast_create_endpoint_is_gated_at_the_one_door_every_rental_uses():
    """`PUT /asks/{id}/` is Vast's create-instance call. Three call sites reach it and one of them
    (`vast_bid_semantics_probe`) does NOT go through `VastBackend.submit`, so gating `submit` alone
    would have left a real rental path open."""
    assert 'if method in ("PUT", "POST", "PATCH") and path.startswith("/asks/"):' in _GB
    assert "_gpu_ban.assert_permitted" in _GB.split("def _vast_request")[1].split("\n    url = ")[0]


def test_the_vast_gate_is_creation_only_so_teardown_still_runs():
    """⛔ THE MOST EXPENSIVE WAY TO GET THIS WRONG. `vast_rental_hold` records it: a stood-down account
    must still tear down a host that somehow exists, or 'stood down' becomes 'billing unwatched'."""
    body = _GB.split("def _vast_request")[1].split("\n    url = ")[0]
    m = re.search(r'if method in \(([^)]*)\) and path\.startswith\("([^"]+)"\)', body)
    assert m, "the create-only test in _vast_request changed shape"
    assert "GET" not in m.group(1) and "DELETE" not in m.group(1)
    assert m.group(2) == "/asks/", "gating a wider path would reach destroy/stop/reap"


def test_every_backend_adapter_is_gated_and_only_mock_is_exempt():
    """One wrapper at `Backend.__init_subclass__` rather than a copy in each `submit`. The failure mode
    it removes is the one `vast-RENTAL-HOLD.json` names of per-lane holds: 'wrong the moment a seventh
    lane is added'."""
    assert "def __init_subclass__(cls, **kwargs):" in _GB
    assert "_GPU_BAN_EXEMPT_BACKENDS" in _GB and "_gpu_ban.assert_permitted" in _GB
    assert re.search(r'_GPU_BAN_EXEMPT_BACKENDS = frozenset\(\{"mock", "abstract"\}\)', _GB), (
        "the exemption set changed — every name in it is a backend that may spend unchecked")
    adapters = set(re.findall(r"^class (\w+)\(Backend\):", _GB, re.M))
    assert {"VastBackend", "SageMakerBackend", "GCPBackend", "ModalBackend", "RunPodBackend",
            "SaladBackend", "SlurmBackend"} <= adapters


# ------------------------------------------------------------------------------------------------------------
# ⚠⚠ THESE THREE ARE BEHAVIOURAL, AND THEY EXIST BECAUSE A SOURCE-INSPECTION TEST COULD NOT SEE THE BUG.
# Mutation L4 — `__init_subclass__` left in the file but made a no-op, so no adapter's `submit` is ever
# wrapped — SURVIVED the whole suite on the first pass: every string the coverage tests look for was still
# there. That is the one-of-a-pair defect exactly: the test proved the TEXT and said nothing about the
# WRAPPING. A gate is only measured by calling it.
# ------------------------------------------------------------------------------------------------------------

def _gpu_backend():
    sys.path.insert(0, str(_REPO / "research/modalities"))
    import gpu_backend  # noqa: PLC0415
    return gpu_backend


def test_a_real_backend_submit_actually_refuses_when_called():
    gb = _gpu_backend()
    for cls in (gb.VastBackend, gb.SageMakerBackend, gb.GCPBackend, gb.ModalBackend):
        with pytest.raises(gpu_ban.GPUSpendProhibited):
            cls().submit(gb.JobSpec(name="x", command=["true"]))


def test_the_mock_backend_still_submits_because_it_bills_nothing():
    """⚠ THE EXEMPTION IS MEASURED TOO. `mock` creates nothing and contacts nothing; if the wrapper ever
    started refusing it, every dry run and half the modalities suite would go red for the wrong reason."""
    gb = _gpu_backend()
    assert gb.get_backend("mock").submit(gb.JobSpec(name="x", command=["true"])).job_id


def test_a_backend_written_tomorrow_is_gated_with_no_edit_to_this_repository():
    """★★ THE POINT OF WRAPPING AT `__init_subclass__` RATHER THAN IN EACH `submit`.
    `vast-RENTAL-HOLD.json` records the failure this removes: a per-lane hold is "wrong the moment a
    seventh lane is added". This defines an EIGHTH backend here, in a test file, and asserts it is gated
    anyway — which is the only way to prove the wrapper is installed rather than merely written."""
    gb = _gpu_backend()

    class _EighthBackend(gb.Backend):
        name = "eighth-provider-nobody-has-written-yet"

        def self_terminate_cmd(self):
            return []

        def submit(self, spec):  # pragma: no cover — the gate must stop it before the body runs
            raise AssertionError("the no-GPU ban did not stop a new backend's submit")

        def status(self, handle):
            return "unknown"

    with pytest.raises(gpu_ban.GPUSpendProhibited):
        _EighthBackend().submit(gb.JobSpec(name="x", command=["true"]))


def test_the_sagemaker_submit_helper_is_gated_before_the_sdk_is_imported():
    """21 lane modules call `submit_spot` directly and none goes through a `Backend` adapter."""
    body = _SM.split("def submit_spot(")[1]
    gate = body.index("_gpu_ban.assert_permitted")
    sdk = body.index("import sagemaker")
    assert gate < sdk, "a refused lane must not need AWS credentials to learn that it is refused"


def test_the_ban_outranks_the_money_gate_and_its_exemptions():
    """★★ THE ORDERING IS THE WHOLE POINT, AND IT IS ASSERTED BY INDEX SO A REORDER GOES RED.
    On 2026-09-02 a cycle compared a committed $25.45 against CLAUDE.md §2's ≲$50 ceiling and concluded
    the buy was authorised. Every written rule it applied, it applied correctly. The market gate answers
    'is this RATE acceptable'; the ban answers a different question, and it is asked first."""
    body = _RMG.split("\ndef gate(")[1]
    ban = body.index("_gpu_ban.refusal(")
    exempt = body.index("ex_key, ex_why = exemption(")
    board = body.index('"/search/asks/"')
    assert ban < exempt < board, (
        "the no-GPU ban must be read before the EXEMPTIONS, before the board and before any price — an "
        "exemption that out-ranked it would turn 'we would lose work' into a purchase permission")
    assert '"hold_cause": "gpu_spend_prohibited"' in body


# ------------------------------------------------------------------------------------------------------------
# The census guard: a NEW ungated billing path is the failure this cannot be allowed to miss.
# ------------------------------------------------------------------------------------------------------------
#: ⛔ EVERY ENTRY IS AN ARGUED EXCLUSION, NOT A CONVENIENCE. Both were read on 2026-09-02 and neither
#: starts a GPU. Adding a row here is how the census gets quietly narrowed, so each carries its evidence.
_NOT_A_GPU = {
    ("gcp-quota-check.yml", "gcloud compute instances create"):
        "creates e2-micro CPU VMs to probe --max-run-duration flag semantics; the workflow's own comment "
        "records ~$0.0002 and 'WITHOUT touching the single-L4 GPU quota'. No accelerator is passed.",
    ("modal-s3-smoke.yml", "modal run"):
        "modal_s3_smoke.py's @app.function declares no gpu=, so it runs on Modal CPU.",
}
_BILLING_MARKERS = ("gcloud compute instances create", "modal run ")


def _ungated_sites():
    out = []
    for wf in sorted((_REPO / ".github/workflows").glob("*.yml")):
        lines = wf.read_text(encoding="utf-8").split("\n")
        for i, ln in enumerate(lines):
            st = ln.strip()
            if st.startswith("#"):
                continue
            for marker in _BILLING_MARKERS:
                if marker not in st:
                    continue
                if (wf.name, marker.strip()) in _NOT_A_GPU:
                    continue
                window = "\n".join(lines[max(0, i - 6):i])
                if "gpu_ban.py" not in window:
                    out.append(f"{wf.name}:{i + 1}: {st[:70]}")
    return out


def test_no_workflow_starts_a_gpu_without_passing_the_gate():
    """⛔ THE GUARD AGAINST THE NEXT PATH, NOT THE LAST ONE. A gate that lists the ten sites it knows
    about is a snapshot; this scans the workflow tree every commit, so a GPU workflow added tomorrow
    fails the build until it carries the gate."""
    assert _ungated_sites() == [], (
        "these workflow lines start a billable GPU with no `gpu_ban.py --context` guard within the six "
        "lines above them. Add the guard, or — if the line genuinely starts no GPU — add it to _NOT_A_GPU "
        "with the reading that shows it:\n  " + "\n  ".join(_ungated_sites()))


def test_the_census_guard_can_actually_fail():
    """⚠ A GUARD THAT CANNOT FAIL IS THE ONE-OF-A-PAIR DEFECT. The test above is green today, so this
    one proves the scanner has teeth by running it against a synthetic ungated workflow."""
    assert "gcloud compute instances create" in _BILLING_MARKERS
    fake = "jobs:\n  x:\n    steps:\n      - run: |\n          gcloud compute instances create \"$VM\" \\\n"
    lines = fake.split("\n")
    hits = [i for i, ln in enumerate(lines)
            if any(m in ln for m in _BILLING_MARKERS) and "gpu_ban.py" not in "\n".join(lines[max(0, i - 6):i])]
    assert hits, "the window scan would not have caught an ungated create"


def test_the_ten_known_workflow_sites_are_all_still_gated():
    n = sum((_REPO / ".github/workflows" / w).read_text(encoding="utf-8").count("gpu_ban.py\" --context")
            for w in os.listdir(_REPO / ".github/workflows") if w.endswith(".yml"))
    assert n >= 10, f"only {n} workflow gate line(s) remain of the 10 the census placed"
