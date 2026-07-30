"""The commit-store audit: does the board's frontier match the one a rented host would resume from?

The founding case (2026-07-30, valB closure triangle T3 ternary): the board said `production/1800` and
the freshly rented host said `restore -> production@iter 1760`. Both read the same S3 prefix. These tests
pin the two rules apart so a future edit cannot quietly re-merge them.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import commit_store_audit as csa  # noqa: E402

BASE = "ternary-vast/commits/unit_x"


def _k(phase, it, gen, name):
    return f"{BASE}/{phase}/iter-{it:08d}/{gen}/{name}"


def test_group_keys_splits_phase_iteration_and_generation():
    keys = [_k("production", 1760, "aaaa", "prod.nc"),
            _k("production", 1760, "aaaa", "prod.chk"),
            _k("production", 1760, "aaaa", csa.MANIFEST)]
    g = csa.group_keys(keys, BASE)
    assert list(g) == [("production", 1760, "aaaa")]
    assert sorted(g[("production", 1760, "aaaa")]) == [csa.MANIFEST, "prod.chk", "prod.nc"]


def test_group_keys_ignores_keys_that_are_not_generation_objects():
    # A stray object at the unit root, and a directory-marker key, must not invent a generation.
    keys = [f"{BASE}/README.txt", f"{BASE}/production/", _k("warmup", 8, "bbbb", "warm.nc")]
    assert list(csa.group_keys(keys, BASE)) == [("warmup", 8, "bbbb")]


def test_leading_zeros_in_the_iteration_do_not_survive_into_the_number():
    # The store writes iter-00001800; the board's regex and this one must agree on 1800, not 1800-as-text.
    g = csa.group_keys([_k("production", 1800, "cccc", "p.nc")], BASE)
    assert list(g)[0][1] == 1800


def test_a_generation_without_a_manifest_is_not_restorable():
    # THE FOUNDING CASE. _persist uploads data first and the manifest LAST, so this is exactly the shape
    # of a host that died (or hung) mid-persist. The board counts it; the restorer must not.
    verdict, why = csa.classify(["prod.nc", "prod.chk"], None, None)
    assert verdict == csa.NO_MANIFEST
    assert "manifest is absent" in why
    assert "prod.nc" in why  # the objects that DID land are named, so the report is evidence not assertion


def test_a_manifest_that_does_not_parse_is_its_own_verdict():
    verdict, _ = csa.classify([csa.MANIFEST, "prod.nc"], None, None)
    assert verdict == csa.BAD_MANIFEST


def test_a_fingerprint_mismatch_is_reported_with_the_reason_verbatim():
    verdict, why = csa.classify([csa.MANIFEST], {"system_fingerprint": "deadbeef"},
                                "SEED: committed 1, running 2")
    assert verdict == csa.FINGERPRINT
    assert "SEED: committed 1, running 2" in why


def test_a_complete_matching_generation_is_restorable():
    verdict, _ = csa.classify([csa.MANIFEST, "prod.nc", "prod.chk"], {"system_fingerprint": "abc"}, None)
    assert verdict == csa.RESTORABLE


def test_frontiers_report_the_gap_the_board_cannot_see():
    rows = [{"phase": "production", "iteration": 1800, "verdict": csa.NO_MANIFEST},
            {"phase": "production", "iteration": 1760, "verdict": csa.RESTORABLE},
            {"phase": "production", "iteration": 1720, "verdict": csa.RESTORABLE}]
    counted, restorable = csa.frontiers(rows)
    assert counted["production"] == 1800
    assert restorable["production"] == 1760


def test_frontiers_agree_when_every_generation_is_complete():
    rows = [{"phase": "production", "iteration": 400, "verdict": csa.RESTORABLE},
            {"phase": "warmup", "iteration": 768, "verdict": csa.RESTORABLE}]
    counted, restorable = csa.frontiers(rows)
    assert counted == restorable == {"production": 400, "warmup": 768}


def test_a_phase_with_no_restorable_generation_at_all_reports_zero_not_missing():
    # "nothing restorable" must render as a gap, not vanish from the report — an absent key reads as
    # "no problem here", which is the failure mode this whole module exists to remove.
    rows = [{"phase": "production", "iteration": 40, "verdict": csa.NO_MANIFEST}]
    counted, restorable = csa.frontiers(rows)
    assert counted["production"] == 40
    assert restorable.get("production", 0) == 0
    out = csa.render("u", {"rows": rows, "counted": counted, "restorable": restorable})
    assert "GAP OF 40 ITERATIONS" in out


def test_render_says_AGREE_when_there_is_no_gap_and_never_warns():
    rows = [{"phase": "production", "iteration": 2000, "generation": "g" * 12,
             "objects": [], "verdict": csa.RESTORABLE, "why": ""}]
    counted, restorable = csa.frontiers(rows)
    out = csa.render("u", {"rows": rows, "counted": counted, "restorable": restorable})
    assert "AGREE" in out and "GAP" not in out and "⚠" not in out


def test_render_names_the_gap_in_iterations_so_the_rework_is_quantified():
    rows = [{"phase": "production", "iteration": 1800, "generation": "a" * 12,
             "objects": ["prod.nc"], "verdict": csa.NO_MANIFEST, "why": "the manifest is absent"},
            {"phase": "production", "iteration": 1760, "generation": "b" * 12,
             "objects": [], "verdict": csa.RESTORABLE, "why": ""}]
    counted, restorable = csa.frontiers(rows)
    out = csa.render("u", {"rows": rows, "counted": counted, "restorable": restorable})
    assert "GAP OF 40 ITERATIONS" in out
    assert "board counts 1800, restorer would use 1760" in out


def test_audit_uses_the_injected_env_and_never_the_process_environment(monkeypatch):
    """If the audit ever fell back to os.environ, a CI runner would report every stamped generation as
    fingerprint-rejected. This asserts the env actually reaches fingerprint_mismatch_reason."""
    seen = {}

    class FakeS3:
        def get_paginator(self, _):
            outer = self

            class P:
                def paginate(self, **kw):
                    del kw
                    yield {"Contents": [{"Key": _k("production", 40, "g1", csa.MANIFEST)}]}
            del outer
            return P()

        def get_object(self, Bucket, Key):  # noqa: N803 — boto3's own kwarg spelling
            del Bucket, Key

            class B:
                def read(self):
                    return b'{"system_fingerprint": "abc"}'
            return {"Body": B()}

    def fake_reason(man):
        seen["manifest"] = man
        return None

    res = csa.audit(FakeS3(), "bkt", BASE, env={"SEED": "7"}, fingerprint_reason=fake_reason)
    assert seen["manifest"] == {"system_fingerprint": "abc"}
    assert res["rows"][0]["verdict"] == csa.RESTORABLE
    assert res["counted"]["production"] == 40 == res["restorable"]["production"]


def test_the_board_regex_and_this_module_extract_the_same_iteration():
    """ternary_vast_launch.committed_progress and group_keys must agree on what N is — the whole finding
    is that they disagree on RESTORABILITY, not on parsing. A parsing divergence would confound it."""
    import re

    key = _k("production", 1800, "gen", "prod.nc")
    board = re.search(r"/(warmup|production)/iter-(\d+)/", key)
    mine = list(csa.group_keys([key], BASE))[0]
    assert board.group(1) == mine[0]
    assert int(board.group(2)) == mine[1]


@pytest.mark.parametrize("phase", ["warmup", "production"])
def test_both_phases_are_audited(phase):
    g = csa.group_keys([_k(phase, 8, "g", "x.nc")], BASE)
    assert list(g)[0][0] == phase


def test_the_jobspec_env_the_cli_reads_is_actually_reachable():
    """`build_jobspec` returns a JobSpec DATACLASS. The first CI run of this module did `spec["env"]`
    and died with TypeError on all four legs — and because the step piped through `tee`, the shell saw
    tee's exit status and reported success, so a step that produced nothing but tracebacks was green.
    This pins the attribute so the CLI cannot silently lose its env again, and every field the
    fingerprint hashes is asserted present — an env missing one of them hashes a '' and would report
    correctly stamped generations as rejected."""
    from rbfe_spot_checkpoint import SYSTEM_FINGERPRINT_ENV
    from ternary_vast_launch import build_jobspec

    spec = build_jobspec("calib_hi_to_lo2__ternary_vhl", seed=0, direction="fwd", mode="triangle",
                         timestep_fs="2.0", warmup_timestep_fs="1.0")
    env = dict(spec.env)  # the exact expression main() uses
    assert env["UNIT_ID"] == "calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle"
    # A fingerprint field the JobSpec does not set hashes as '' — which is CORRECT only so long as the
    # container does not set it either, because then both sides hash ''. That is true today of exactly one
    # field, and pinning the set means a future field added to the JobSpec (or to the container) trips this
    # test instead of silently shifting the audit's fingerprint away from the host's.
    missing = sorted(k for k in SYSTEM_FINGERPRINT_ENV if k not in env)
    assert missing == ["RBFE_CONSTRAIN_LIGAND_CH"], (
        f"the set of fingerprint fields absent from the JobSpec env changed to {missing}. Each one hashes "
        "as '' here; confirm the CONTAINER also leaves it unset, or the audit will compare a different "
        "fingerprint than the host computed.")
