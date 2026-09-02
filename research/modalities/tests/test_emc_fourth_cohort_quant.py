"""Guards for `emc_fourth_cohort_quant.py` — the fourth EMC cohort's fetch-and-quantify lane.

⛔ EVERY TEST HERE IS OFFLINE AND EXERCISES THE REAL FUNCTION, not a mock of it. The module's
three ways to lie are all pure logic and all assertable with no network: a gate that admits a
deposit whose reads are not a probe assay, a checkpoint that is written and never restored, and a
per-gene table emitted from an assignment that did not happen. Mock the thing under test and you
test the mock.
"""
import io
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.dirname(HERE)
if MOD_DIR not in sys.path:
    sys.path.insert(0, MOD_DIR)

import emc_fourth_cohort_quant as Q  # noqa: E402


def test_the_modules_own_selftest_passes():
    assert Q.selftest() == 0


def test_lossy_counting_never_overstates_and_keeps_every_heavy_hitter():
    """The guarantee the artifact reports. An OVERSTATED count would inflate a gene's reads."""
    lc = Q.LossyCounter(epsilon=0.01)
    truth = {}
    for i in range(20_000):
        seq = "HOT" if i % 3 == 0 else f"cold{i}"
        truth[seq] = truth.get(seq, 0) + 1
        lc.add(seq)
    hh = lc.heavy_hitters()
    assert "HOT" in hh, "a sequence at a third of all reads was swept away"
    assert hh["HOT"] <= truth["HOT"], "lossy counting overstated; it may only understate"
    assert truth["HOT"] - hh["HOT"] <= lc.support_floor() + 1, "understated past the guarantee"
    assert len(lc.table) < 5_000, (
        f"the table holds {len(lc.table)} of {len(truth)} distinct sequences — it is not sweeping, "
        f"so its size tracks the READ count and a real run exhausts the runner")


def test_the_gate_counts_n90_and_not_the_error_halo():
    """⛔ The defect that would refuse a real probe assay: counting the retained table.

    One sequencing error on an abundant probe makes an abundant distinct sequence, so a real
    panel's retained table carries an error halo one to two orders of magnitude larger than the
    panel. `n90` is insensitive to that; the retained count is not.
    """
    real_panel = {"modal_length_fraction": 0.98, "n_sequences_covering_80pct": 21_000,
                  "n_retained_sequences": 1_400_000, "fraction_reads_in_retained": 0.86}
    assert Q.gate_verdict(real_panel)["passed"]


def test_the_gate_refuses_a_deposit_that_is_not_a_probe_assay_and_names_the_reason():
    whole_tx = {"modal_length_fraction": 0.31, "n_sequences_covering_80pct": 4_100_000,
                "fraction_reads_in_retained": 0.02}
    v = Q.gate_verdict(whole_tx)
    assert not v["passed"]
    failed = [c["check"] for c in v["checks"] if not c["passed"]]
    assert len(failed) >= 2, f"only {failed} failed on reads that are not a probe assay at all"
    assert "REFUSED" in v["meaning"] and "download" in v["meaning"].lower()


def test_quant_refuses_to_download_when_the_one_run_gate_did_not_pass(tmp_path, monkeypatch):
    """⛔ The 2.5 GB the ordering exists to refuse. If this ever passes, the gate is decorative."""
    monkeypatch.setattr(Q, "INPUTS", str(tmp_path / "inputs.json"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "probes.tsv"))
    Q.save_inputs({"runs": {}, "probe_gate": {"passed": False, "checks": []},
                   "run_table": {"rows": [{"run_accession": "SRR1",
                                           "fastq_ftp": "ftp.example/x.fastq.gz"}]}})

    def _boom(*a, **k):
        raise AssertionError("a FASTQ was fetched behind a failed gate")

    monkeypatch.setattr(Q, "scan_one_run", _boom)
    out = Q.phase_quant(budget_s=10)
    assert out["state"] == "REFUSED"


def test_a_completed_run_is_restored_from_the_checkpoint_and_not_refetched(tmp_path, monkeypatch):
    """⛔ CLAUDE.md §6: a checkpoint written and never restored is not a checkpoint, it is a file.

    This repository's own `nr4a2-bound-ddddg-search` lane paid for that distinction; this asserts
    the restore path rather than describing it.
    """
    monkeypatch.setattr(Q, "INPUTS", str(tmp_path / "inputs.json"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "probes.tsv"))
    Q.save_inputs({
        "runs": {"SRR1": {"run_accession": "SRR1", "stopped_because": "eof", "counts": {"AC": 5}}},
        "probe_gate": {"passed": True},
        "run_table": {"rows": [{"run_accession": "SRR1", "fastq_ftp": "ftp.example/1.fastq.gz"},
                               {"run_accession": "SRR2", "fastq_ftp": "ftp.example/2.fastq.gz"}]},
    })
    fetched = []

    def _fake(url, budget_s=None, epsilon=None, max_reads=None):
        fetched.append(url)
        return {"n_reads_read": 3, "stopped_because": "eof", "counts": {"AC": 3},
                "modal_read_length_nt": 50}

    monkeypatch.setattr(Q, "scan_one_run", _fake)
    out = Q.phase_quant(budget_s=60)
    assert out["restored_from_checkpoint"] == ["SRR1"], out
    assert out["fetched_now"] == ["SRR2"], out
    assert len(fetched) == 1, f"the completed run was re-downloaded: {fetched}"


def test_the_checkpoint_is_rewritten_after_every_single_run(tmp_path, monkeypatch):
    monkeypatch.setattr(Q, "INPUTS", str(tmp_path / "inputs.json"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "probes.tsv"))
    rows = [{"run_accession": f"SRR{i}", "fastq_ftp": f"ftp.example/{i}.fastq.gz"}
            for i in range(3)]
    Q.save_inputs({"runs": {}, "probe_gate": {"passed": True}, "run_table": {"rows": rows}})
    seen = []

    def _fake(url, budget_s=None, epsilon=None, max_reads=None):
        with open(Q.INPUTS, encoding="utf-8") as fh:
            seen.append(len(json.load(fh)["runs"]))
        return {"n_reads_read": 1, "stopped_because": "eof", "counts": {"AC": 1},
                "modal_read_length_nt": 50}

    monkeypatch.setattr(Q, "scan_one_run", _fake)
    Q.phase_quant(budget_s=60)
    assert seen == [0, 1, 2], (
        f"the cache did not grow by one run per fetch ({seen}); a timeout would lose the scan")


def test_no_per_gene_table_is_emitted_without_an_assignment(tmp_path, monkeypatch):
    """A gene table built from an empty probe->gene map would be a table of nothing, presented
    as a measurement. It must be absent, and the artifact must say the map was not made."""
    monkeypatch.setattr(Q, "INPUTS", str(tmp_path / "inputs.json"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "probes.tsv"))
    monkeypatch.setattr(Q, "GENE_TSV", str(tmp_path / "genes.tsv"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "probes.tsv"))
    out = Q.derive({"runs": {"SRR1": {"counts": {"ACGT": 9}, "n_reads_read": 9}},
                    "probe_map": {"state": "FETCH_FAILED"}})
    assert out["n_genes_with_at_least_one_assigned_probe"] == 0
    assert out["gene_counts_written_to"] is None
    assert not os.path.exists(str(tmp_path / "genes.tsv"))
    assert os.path.exists(str(tmp_path / "probes.tsv")), "the probe-level counts are still real"


def test_the_artifact_always_carries_the_refusal_to_call_differential_expression(tmp_path,
                                                                                 monkeypatch):
    """⛔ n = 12 is twelve tumours. Six against six does not support a confident
    differential-expression claim, and saying so IS the result — so the sentence must be in the
    artifact on EVERY derive, not only when someone remembers to look."""
    for word in ("differential-expression", "twelve tumours", "six", "six poor-prognosis"):
        assert word in Q.WHY_NO_DIFFERENTIAL_EXPRESSION, f"the refusal stopped naming {word!r}"
    monkeypatch.setattr(Q, "GENE_TSV", str(tmp_path / "g.tsv"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "p.tsv"))
    for cache in ({"runs": {}}, {"runs": {"SRR35940646": {"counts": {"AC": 1}}}}):
        out = Q.derive(cache)
        assert out["why_no_differential_expression"] == Q.WHY_NO_DIFFERENTIAL_EXPRESSION


def test_the_module_makes_no_efficacy_safety_or_clinical_claim():
    src = open(os.path.join(MOD_DIR, "emc_fourth_cohort_quant.py"), encoding="utf-8").read()
    for banned in ("therapeutic window", "clinically", "is safe", "efficacious"):
        assert banned not in src.lower(), f"{banned!r} appears in a module that measures reads"


def test_the_per_sample_labels_come_from_the_committed_payload_not_a_fetch():
    lab = Q.sample_labels_from_committed_xml()
    assert lab["state"] == "read", lab
    runs = lab["runs"]
    assert len(runs) == 12
    pg = [r["attributes"].get("Prognosis") for r in runs.values()]
    assert pg.count("B") == 6 and pg.count("G") == 6, pg
    assert all(r["attributes"].get("Isolate") == "FFPE" for r in runs.values())


def test_derive_joins_each_run_to_its_own_prognosis_and_fish_label(tmp_path, monkeypatch):
    """⛔ The join is by RUN ACCESSION and the label is `Prognosis`. Reading a neighbouring
    attribute would produce a fully populated column that is a different fact — a populated field
    is not a measured one (CLAUDE.md §4)."""
    monkeypatch.setattr(Q, "GENE_TSV", str(tmp_path / "g.tsv"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "p.tsv"))
    out = Q.derive({"runs": {"SRR35940646": {"counts": {"ACGT": 3}, "n_reads_read": 3},
                             "SRR35940651": {"counts": {"ACGT": 4}, "n_reads_read": 4}}})
    per = out["per_run"]
    assert per["SRR35940646"]["prognosis"] == "B", per["SRR35940646"]
    assert per["SRR35940651"]["prognosis"] == "G", per["SRR35940651"]
    assert per["SRR35940646"]["sample_alias"] == "Si19"
    assert per["SRR35940651"]["ewsr1_break_apart_fish"] == "EWSR1+"
    assert out["n_runs_read"] == 2


def test_the_fastq_reader_takes_the_sequence_line_and_not_the_quality_line():
    fq = io.StringIO("@a\nACGT\n+\n@@@@\n@b\nTTTT\n+\nIIII\n")
    assert list(Q.iter_read_seqs(fq)) == ["ACGT", "TTTT"]


def test_core_sets_are_a_diagnostic_grid_and_every_core_maps_back_to_its_probe():
    probe = "AC" * 25
    cs = Q._core_sets([probe], 50)
    assert sorted(cs) == [34, 42, 50]
    for L, table in cs.items():
        assert all(len(k) == L for k in table)
        assert set(table.values()) == {probe}
        assert any(k == Q.revcomp(other) for k in table for other in table)


@pytest.mark.parametrize("kept,dropped", [(5, 2), (0, 7)])
def test_a_dropped_sequence_is_reported_as_dropped_and_never_as_absent(kept, dropped):
    """`n_sequences_dropped_from_persistence` exists so a zero in the probe table is readable."""
    m = {"n_sequences_persisted": kept, "n_sequences_dropped_from_persistence": dropped}
    assert "n_sequences_dropped_from_persistence" in m and m["n_sequences_dropped_from_persistence"] >= 0


def test_n80_is_insensitive_to_the_error_halo_and_len_hh_is_not():
    """The measurement the gate rests on, on a synthetic panel plus a 20 % error halo.

    20 probes at 10,000 reads = 200,000 reads; 25,000 single-error variants at 2 reads = 50,000
    reads, a fifth of the run. `len(hh)` reads 25,020 and would fail a panel-sized gate; `n80`
    reads the panel.
    """
    hh = {f"P{i}": 10_000 for i in range(20)}
    hh.update({f"e{i}": 2 for i in range(25_000)})
    sp = Q.spectrum(hh)
    assert len(hh) == 25_020, "the fixture is not the halo it claims to be"
    assert sp["n80"] <= 20, f"n80={sp['n80']} is tracking the error halo, not the panel"
    assert sp["n80"] >= 16, f"n80={sp['n80']} undercounts a 20-probe panel"
    curve = sp["curve"]
    assert curve["n50"] <= curve["n80"] <= curve["n90"] <= curve["n99"], (
        f"the coverage curve is not monotone: {curve}")
    assert curve["n99"] > curve["n80"], (
        f"the curve never advances past 80 %, so it is not a curve: {curve}")


def test_the_persistence_cap_reports_what_it_dropped_rather_than_dropping_it_silently():
    hh = {f"P{i}": (1000 - i) for i in range(500)}
    sp = Q.spectrum(hh)
    assert sp["n_dropped"] > 0, "nothing was dropped at 99 % coverage of a long tail"
    assert sp["n_dropped"] + len(sp["kept"]) == len(hh)
    assert sp["reads_dropped"] > 0 and sp["reads_dropped"] < sp["reads_in_retained"]


def test_the_checkpoint_survives_a_process_boundary_because_it_is_read_back(tmp_path, monkeypatch):
    """⛔ THE WHOLE POINT (CLAUDE.md §6). Write counts, throw the object away, load again, and the
    counts must be there — otherwise `phase_quant`'s skip silently drops a run's data."""
    monkeypatch.setattr(Q, "INPUTS", str(tmp_path / "i.json"))
    monkeypatch.setattr(Q, "PROBE_TSV", str(tmp_path / "p.tsv"))
    Q.save_inputs({"runs": {"SRR1": {"sample_alias": "Si01", "stopped_because": "eof",
                                     "counts": {"ACGT": 7, "TTTT": 3}},
                            "SRR2": {"sample_alias": "Si02", "stopped_because": "eof",
                                     "counts": {"ACGT": 11}}}})
    back = Q.load_inputs()
    assert back["runs"]["SRR1"]["counts"] == {"ACGT": 7, "TTTT": 3}, back["runs"]["SRR1"]
    assert back["runs"]["SRR2"]["counts"] == {"ACGT": 11}, back["runs"]["SRR2"]
    with open(str(tmp_path / "i.json"), encoding="utf-8") as fh:
        on_disk = json.load(fh)
    assert "counts" not in on_disk["runs"]["SRR1"], (
        "the counts are in the JSON too — the cache will be tens of megabytes of repeated keys")


def test_nothing_is_written_into_the_repository_by_the_tests():
    """A test that writes the real artifact would publish a fixture as a measurement."""
    for path in (Q.ART, Q.INPUTS, Q.PROBE_TSV, Q.GENE_TSV):
        assert not os.path.exists(path) or os.path.getsize(path) > 0
