"""The NR-V04 retrospective collector must read the keys the MD driver actually writes.

WHY THIS FILE EXISTS (Lane 11, 2026-07-25, pre-spend audit of RUNG 4). `nrv04_covalent_md.run_leg` writes its
readouts under `R1_interface` / `R2_recruitment` / `R3_lys`. `nrv04_vast_launch.retro_collect` read
`d.get("R1")` / `d.get("R2")`. Nothing errored: every `e1_plateau_A` came back None, every leg was marked
`technical_failure`, every arm was `underpowered`, and the frozen gate returned **INDETERMINATE on a panel of
24 flawless legs** — a ~$21 run that could not have returned any other answer, and whose failure would have
read post-hoc as a physics result rather than a key-name typo.

The existing tests could not catch it: `test_nrv04_retro.py` feeds the gate `e1_plateau_A` directly, so the
driver→collector boundary was never crossed by a test. These tests cross it, with the driver's key names taken
from the driver's own source by AST rather than transcribed.
"""
import ast
import json
import os
import sys
import types
from datetime import datetime

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import nrv04_retro_panel as retro  # noqa: E402


def _driver_result_keys():
    """The literal key set of the result dict `nrv04_covalent_md.run_leg` writes — read from source, so this
    test tracks the driver instead of a copy of it."""
    tree = ast.parse(open(os.path.join(HERE, "nrv04_covalent_md.py")).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_leg":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Dict):
                    keys = [k.value for k in sub.value.keys if isinstance(k, ast.Constant)]
                    if "leg_id" in keys and any(str(k).startswith("R1") for k in keys):
                        return keys
    raise AssertionError("could not locate run_leg's result dict")


def test_driver_still_writes_the_readout_keys_this_collector_reads():
    keys = _driver_result_keys()
    assert "R1_interface" in keys and "R2_recruitment" in keys and "R3_lys" in keys, (
        "the driver's readout keys changed; retro_collect's mapping must be updated with them: %s" % keys)


def _driver_shaped_leg(arm_id, model_seed, replica, plateau):
    leg = {k: None for k in _driver_result_keys()}
    leg.update({"panel": "nrv04_retrospective", "leg_id": f"{arm_id}__m{model_seed}", "seed": replica,
                # ★ 2026-07-31: the PROTOCOL fields are part of "driver-shaped", not decoration. A record is a
                # landed leg only if `nrv04_retro_panel.production_leg_check` passes it — 17 records that had
                # `mode: run`'s neighbours (`prod_ns: 5.0`) but were smokes underneath completed this panel and
                # reached the frozen gate. `timed_ns` is what ran; `prod_ns` is only what was asked for.
                "mode": "run", "prod_ns": retro.PROD_NS, "equil_ns": retro.EQUIL_NS,
                "timed_ns": retro.PROD_NS, "n_frames": retro.expected_production_frames(),
                "prod_wall_s": 3730.5, "ns_per_day": 115.8, "blew_up": False,
                "R1_interface": {"rmsd_series_mean": plateau, "plateau_A": plateau, "stable": plateau < 4.0},
                "R2_recruitment": {"frames": 500, "frac_frames_in_contact": 1.0, "mean_contacts": 1979.4,
                                   "recruited": True},
                "R3_lys": {"min_A": 31.2, "median_A": 38.0, "max_A": 49.0}})
    return leg


def _stub_s3(objects):
    class _Body:
        def __init__(self, b):
            self._b = b

        def read(self):
            return self._b

    class _S3:
        def list_objects_v2(self, **kw):
            pre = kw.get("Prefix", "")
            return {"Contents": [{"Key": k, "Size": len(v), "LastModified": datetime.now()}
                                 for k, v in objects.items() if k.startswith(pre)], "IsTruncated": False}

        def get_object(self, Bucket=None, Key=None):
            return {"Body": _Body(objects[Key])}

    mod = types.ModuleType("boto3")
    mod.client = lambda *a, **k: _S3()
    return mod


def _full_panel_objects(plateau_for):
    objects = {}
    for arm, m, r in retro.enumerate_units():
        name = retro.unit_name(arm, m, r)
        d = _driver_shaped_leg(arm.arm_id, m, r, plateau_for(arm.arm_id, m, r))
        objects[f"nrv04-retro-results/{name}/leg_{arm.arm_id}__m{m}_s{r}.json"] = json.dumps(d).encode()
        objects[f"nrv04-retro-results/{name}/phase.txt"] = b"done rc=0"
    return objects


@pytest.fixture()
def collect(monkeypatch, tmp_path):
    def _run(objects):
        monkeypatch.setitem(sys.modules, "boto3", _stub_s3(objects))
        monkeypatch.setenv("VAST_CKPT_BUCKET", "stub-bucket")
        monkeypatch.chdir(tmp_path)
        import importlib
        L = importlib.import_module("nrv04_vast_launch")
        # This fixture measures driver-result mapping. Keep all control-plane
        # activity synthetic too: the live board GET used to cost ~31 s per test.
        monkeypatch.setattr(L, "retro_reap", lambda *a, **kw: None)
        monkeypatch.setattr(L, "retro_supervise", lambda *a, **kw: {})

        def fleet_request(method, path, key, **kwargs):
            assert (method, path) == ("GET", "/instances/")
            return {"instances": []}

        monkeypatch.setattr(L, "_vast_request", fleet_request)
        rc = L.retro_collect("stub-bucket")
        return rc, json.load(open(tmp_path / "nrv04-retro-collect.json"))
    return _run


def test_a_complete_panel_of_good_legs_is_scored_not_declared_indeterminate(collect):
    """THE BUG, PINNED. NR4A1 clearly the most stable; the gate must be able to see it."""
    def plateau(arm_id, m, r):
        return 2.0 + 0.1 * m + 0.05 * r if arm_id == "retro_noncov_nr4a1" else 4.5 + 0.1 * m + 0.05 * r
    rc, out = collect(_full_panel_objects(plateau))
    assert rc == 0 and out["panel_complete"] is True
    assert "schema_mismatch" not in out
    assert all(l["e1_plateau_A"] is not None for l in out["legs"]), \
        "the collector read no E1 from driver-shaped leg JSONs — the R1/R1_interface key mismatch is back"
    assert not any(l["technical_failure"] for l in out["legs"])
    v = out["verdict"]
    assert v["tier"] != "INDETERMINATE", v
    assert v["underpowered_arms"] == []


def test_e2_e3_e4_are_carried_through_as_the_prereg_requires(collect):
    """Prereg §3: E2-E4 are reported alongside E1 in every result, including when they disagree with it."""
    rc, out = collect(_full_panel_objects(lambda a, m, r: 3.0))
    leg = out["legs"][0]
    assert leg["e2_stable"] is True
    assert leg["e3_mean_contacts"] == 1979.4
    assert leg["e4_lys_min_A"] == 31.2


def test_a_schema_drift_is_loud_instead_of_looking_like_a_physics_result(collect):
    """If the driver's key names ever move again, the collector must SAY so rather than emit a verdict built
    on 24 silent technical failures."""
    objects = _full_panel_objects(lambda a, m, r: 3.0)
    renamed = {}
    for k, v in objects.items():
        if k.endswith(".json"):
            d = json.loads(v)
            d["R1_SOMETHING_ELSE"] = d.pop("R1_interface")
            v = json.dumps(d).encode()
        renamed[k] = v
    rc, out = collect(renamed)
    assert rc == 1
    assert "schema_mismatch" in out
    assert out["verdict"] is None


def test_a_genuine_blowup_is_still_a_technical_failure_not_a_schema_alarm(collect):
    """The guard must not fire on real physics failures — only on the case where nothing blew up and yet no
    leg produced an endpoint."""
    objects = _full_panel_objects(lambda a, m, r: 3.0)
    k0 = next(k for k in objects if k.endswith(".json"))
    d = json.loads(objects[k0])
    d["blew_up"] = True
    d["R1_interface"] = {"rmsd_series_mean": None, "plateau_A": None, "stable": False}
    objects[k0] = json.dumps(d).encode()
    rc, out = collect(objects)
    assert "schema_mismatch" not in out
    assert sum(1 for l in out["legs"] if l["technical_failure"]) == 1
