"""Unit tests for the Processing->spot-Training helpers (pure logic; no AWS)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sagemaker_src"))

import sagemaker_submit as ss  # noqa: E402
import sm_io  # noqa: E402


def test_arguments_list_to_hyperparameters():
    hp = ss._to_hyperparameters(["--git-ref", "main", "--dcd-name", "traj.dcd", "--block-ns", "10"])
    assert hp == {"git-ref": "main", "dcd-name": "traj.dcd", "block-ns": "10"}


def test_store_true_flag():
    hp = ss._to_hyperparameters(["--control", "--git-ref", "main"])
    assert hp == {"control": "true", "git-ref": "main"}


def test_dict_passthrough_strips_dashes():
    assert ss._to_hyperparameters({"--k": 1, "j": "v"}) == {"k": "1", "j": "v"}


def test_empty_arguments():
    assert ss._to_hyperparameters(None) == {} and ss._to_hyperparameters([]) == {}


def test_channel_prefers_training_env(monkeypatch):
    monkeypatch.setenv("SM_CHANNEL_NR4A3", "/opt/ml/input/data/nr4a3")
    assert sm_io.channel("nr4a3") == "/opt/ml/input/data/nr4a3"
    assert sm_io.channel("NR4A3") == "/opt/ml/input/data/nr4a3"


def test_channel_hyphen_to_underscore(monkeypatch):
    monkeypatch.setenv("SM_CHANNEL_MY_CH", "/data/x")
    assert sm_io.channel("my-ch") == "/data/x"


def test_channel_falls_back_to_processing_path(monkeypatch):
    monkeypatch.delenv("SM_CHANNEL_METAD", raising=False)
    assert sm_io.channel("metad") == "/opt/ml/processing/input/metad"


def test_out_dir_honours_override(monkeypatch, tmp_path):
    monkeypatch.setenv("SM_OUTPUT_DIR", str(tmp_path / "out"))
    assert sm_io.out_dir() == str(tmp_path / "out")
    assert os.path.isdir(str(tmp_path / "out"))
