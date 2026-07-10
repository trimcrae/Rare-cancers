"""Unit tests for the reproducibility-archival classification logic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import archive_results as ar  # noqa: E402


def test_durable_json_archived():
    assert ar.classify_object("nr4a3-denovo/nr4a3-denovo.json", 12345) == "archive"
    assert ar.classify_object("nr4a3-mmgbsa/nr4a3-mmgbsa.json", 500) == "archive"


def test_scratch_rejected_even_with_durable_ext():
    # fpocket scratch PDBs have a .pdb (durable) ext but must never reach git
    assert ar.classify_object("nr4a3-8xtt-benchmark/fpocket_runs/8XTT_model8_out/pockets/pocket5_atm.pdb", 2500) == "scratch"
    assert ar.classify_object("x/8XTT_model8_out/8XTT_model8.pml", 776) == "scratch"
    assert ar.classify_object("x/8XTT_model8_out/8XTT_model8_pockets.pqr", 42946) == "scratch"
    assert ar.classify_object("x/redock_work/tmp.pdb", 100) == "scratch"


def test_too_big_goes_to_zenodo_bucket():
    # trajectories are load-bearing large artifacts → too-big (Zenodo), never dropped
    assert ar.classify_object("nr4a3-metad-r1/ckpt/nr4a3-lbd-metad.dcd", 200 * 1024 * 1024) == "too-big"
    assert ar.classify_object("nr4a3-release/rep0.dcd", 100) == "too-big"  # regardless of size
    # a durable-ext file over the cap → too-big (not silently committed)
    assert ar.classify_object("nr4a3-abfe/reduced_potentials.dat", 50 * 1024 * 1024) == "too-big"


def test_nondurable_ext_skipped():
    assert ar.classify_object("x/model.ckpt", 1000) == "skip"
    assert ar.classify_object("x/plot.png", 1000) == "skip"


def test_durable_name_without_ext():
    # HILLS / COLVAR have no extension but are load-bearing metad outputs
    assert ar.classify_object("nr4a3-metad-r1/ckpt/HILLS", 40000) == "archive"
    assert ar.classify_object("nr4a3-metad-r1/ckpt/COLVAR", 40000) == "archive"
    assert ar.classify_object("nr4a3-metad-r1/ckpt/fes.dat", 8000) == "archive"


def test_empty_and_dir_skipped():
    assert ar.classify_object("nr4a3-denovo/", 0) == "skip"
    assert ar.classify_object("nr4a3-denovo/empty.json", 0) == "skip"
    assert ar.classify_object("x/foo.json.sagemaker-uploaded", 0) == "skip"  # 0-byte marker
    assert ar.classify_object("x/foo.json.sagemaker-uploaded", 5) == "scratch"  # nonzero marker → scratch suffix


def test_build_manifest_totals():
    objs = [
        ("p/a.json", 100),                                   # archive
        ("p/big.dat", 10 * 1024 * 1024),                     # too-big
        ("p/fpocket_runs/x/pockets/pocket1_atm.pdb", 2000),  # scratch
        ("p/model.ckpt", 500),                               # skip
        ("p/HILLS", 3000),                                   # archive
    ]
    man = ar.build_manifest(objs)
    assert man["n_objects"] == 5
    assert man["totals"] == {"archive": 2, "too-big": 1, "scratch": 1, "skip": 1}
    assert man["archive_bytes"] == 100 + 3000
    # every object is accounted for with an action
    assert all("action" in e for e in man["objects"])


def test_cap_is_configurable():
    assert ar.classify_object("p/x.json", 2000, cap_bytes=1000) == "too-big"
    assert ar.classify_object("p/x.json", 500, cap_bytes=1000) == "archive"
