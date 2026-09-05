"""Mutation probes may stop at evidence; baselines must still measure every witness."""
import importlib.util
import hashlib
import itertools
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "ablation_execution_subject", ROOT / "research/manuscripts/claim_ablation.py")
CA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CA)


def test_short_circuit_preserves_the_verdict_and_excludes_baseline_reds(monkeypatch):
    commands = [["python", "-m", "pytest", "guard.py"],
                ["python", "pins.py"], ["python", "generator.py", "--check"]]
    for reds in itertools.product((False, True), repeat=3):
        for excluded in ([], [0], [1], [0, 1, 2]):
            calls = []

            def run(command, workspace):
                original = command[:-1] if command[-1] == "--maxfail=1" else command
                index = commands.index(original)
                calls.append(index)
                return reds[index]

            monkeypatch.setattr(CA, "_run", run)
            detected = CA._mutation_is_detected(commands, excluded, "clone")
            assert detected == any(red for i, red in enumerate(reds) if i not in excluded)
            assert not set(calls).intersection(excluded)
            if not detected:
                assert set(calls) == set(range(3)) - set(excluded)
    assert all("--maxfail=1" not in cmd for cmd in commands)


def test_real_pytest_probe_stops_but_an_ordinary_run_executes_the_rest(tmp_path):
    marker = tmp_path / "later-test-ran"
    guard = tmp_path / "test_witness.py"
    guard.write_text("from pathlib import Path\n"
                     "def test_fails():\n    assert False\n"
                     f"def test_later():\n    Path({str(marker)!r}).touch()\n", encoding="utf-8")
    command = [sys.executable, "-m", "pytest", str(guard), "-q", "-p", "no:cacheprovider"]
    assert CA._run(command, str(tmp_path))
    assert marker.exists(), "ordinary and baseline invocations must finish the test batch"
    marker.unlink()
    assert CA._mutation_is_detected([command], [], str(tmp_path))
    assert not marker.exists(), "the mutation already has its witness; later tests add no evidence"


def test_baseline_runs_all_commands_without_mutation_options(tmp_path, monkeypatch):
    commands = [["python", "-m", "pytest", "one.py"], ["python", "pins.py"]]
    calls = []
    monkeypatch.setattr(CA, "_witness_cmds", lambda *_: commands)
    monkeypatch.setattr(CA, "_run", lambda cmd, ws: calls.append(list(cmd)) or False)
    monkeypatch.setattr(CA, "_BASELINE_CACHE", {})
    assert CA._baseline_reds(["synthetic"], str(tmp_path)) == (commands, [])
    assert calls == commands


def test_orcid_identifiers_do_not_hide_adjacent_scientific_quantities(monkeypatch):
    identifier = "0000-0002-1823-1451"
    attribution = f"ORCID: [{identifier}](https://orcid.org/{identifier})"
    sentence = attribution + "; 190 designs across three transcripts."
    assert [before for _, _, before, _ in CA.perturbations(sentence, [])] == ["190", "three"]
    assert not CA.states_a_quantity(attribution)
    assert CA.states_a_quantity(sentence)
    assert CA.perturbations(identifier, []), "an unlabeled numeral is not recognized as an ORCID"
    assert CA.perturbations("ORCID: " + identifier[:-1] + "9", []), "bad checksums are not excluded"
    assert not CA.perturbations("https://orcid.org/0000-0002-1694-233X", [])

    monkeypatch.setattr(CA._cache, "witness_sources", lambda _: [])
    for text in (sentence, "190 designs across three transcripts."):
        old_key = hashlib.sha256(b"paper\0" + text.encode() + b"\0").hexdigest()
        new_key = CA._cache.key_for("paper", text, [])
        assert (new_key != old_key) == bool(CA.orcid_spans(text)), (
            "only sentences with changed mutation sites must lose their prior cache verdict")
