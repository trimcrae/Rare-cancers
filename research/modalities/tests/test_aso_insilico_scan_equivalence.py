"""The inverted-index off-target scan must return EXACTLY what the loop it replaced returned.

★ WHY THIS TEST IS THE GATE ON THAT REWRITE. `aso_insilico.offtarget_scan` used to run `seq.find()` for
every candidate against every record — O(n_designs x transcriptome). That is affordable for one junction's
24 designs and impossible for a pan-fusion catalog (~2e9 string searches at ~19,000 designs), so the loop
was inverted: index the seeds once, walk each record once, score only the candidates whose seed occurs.

⛔ THE COMMITTED EMC NUMBERS ARE PUBLISHED. `fusion-junction-aso-research-article.md` reports off-target
counts over 186,185 transcripts, and nine designs are called clean on the strength of them. A speed-up that
moved any of those counts by one would silently invalidate a manuscript claim — and it would look like a
faster pipeline, not like a retraction. So the reference implementation is kept here VERBATIM and both are
run over the same bytes.

⚠ THE SUBTLE ONE IS THE siRNA SEED. The original counts seed occurrences with `str.count`, which counts
NON-overlapping matches; the obvious sliding-window rewrite counts overlapping ones, and the two differ
only on self-overlapping 7-mers (`AAAAAAA` in `AAAAAAAA`). That is exactly the kind of difference nobody
notices until a number is in print, so it gets its own fixture below.
"""
from __future__ import annotations

import gzip
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("junction_aso")
import aso_insilico as ai  # noqa: E402
import junction_aso as ja  # noqa: E402


# ── the implementation this replaced, verbatim ──────────────────────────────────────────────────
def _reference_scan(candidates, records):
    """The pre-2026-08-13 loop, unchanged except that it reads records from a list rather than a gz."""
    L = ja.OLIGO_LEN
    half = L // 2
    seeds = []
    for ci, c in enumerate(candidates):
        t = c["target_mRNA_5to3"]
        seeds.append((ci, [(t[:half], 0), (t[half:], half)]))
        c["offtarget_exact"] = 0
        c["offtarget_le1mm"] = 0
        c["offtarget_hits"] = []

    for acc, seq in records:
        for ci, slist in seeds:
            c = candidates[ci]
            t = c["target_mRNA_5to3"]
            seed7 = c.get("_seed7")
            if seed7:
                c["sirna_seed_offtarget_sites"] += seq.count(seed7)
            seen = set()
            for seed, off in slist:
                idx = seq.find(seed)
                while idx != -1:
                    wstart = idx - off
                    if 0 <= wstart and wstart + L <= len(seq):
                        if wstart not in seen:
                            seen.add(wstart)
                            mm = ai._mismatches(seq[wstart:wstart + L], t)
                            if mm <= 1:
                                c["offtarget_le1mm"] += 1
                                if mm == 0:
                                    c["offtarget_exact"] += 1
                                if len(c["offtarget_hits"]) < 5:
                                    c["offtarget_hits"].append({"acc": acc, "mm": mm})
                    idx = seq.find(seed, idx + 1)
    return candidates


# ── fixtures ────────────────────────────────────────────────────────────────────────────────────
def _cand(target, seed7=None):
    c = {"target_mRNA_5to3": target, "sirna_seed_offtarget_sites": 0}
    if seed7:
        c["_seed7"] = seed7
    return c


def _write_fasta(tmp_path, records):
    p = tmp_path / "grch38_rna.fna.gz"
    with gzip.open(p, "wt") as fh:
        for acc, seq in records:
            fh.write(f">{acc} some description\n")
            for i in range(0, len(seq), 70):
                fh.write(seq[i:i + 70] + "\n")
    return p


def _run_both(tmp_path, monkeypatch, candidates_spec, records):
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    _write_fasta(tmp_path, records)

    fast = [_cand(*spec) for spec in candidates_spec]
    meta = ai.offtarget_scan(fast)

    ref = [_cand(*spec) for spec in candidates_spec]
    _reference_scan(ref, records)
    return fast, ref, meta


def _assert_identical(fast, ref):
    assert len(fast) == len(ref)
    for a, b in zip(fast, ref):
        for field in ("offtarget_exact", "offtarget_le1mm", "offtarget_hits",
                      "sirna_seed_offtarget_sites"):
            assert a[field] == b[field], (
                f"{field} diverged for {a['target_mRNA_5to3']}: fast={a[field]} ref={b[field]}")


# ── tests ───────────────────────────────────────────────────────────────────────────────────────
TARGET = "ACGTACGTTGCATGCA"          # 16 nt, two distinct 8-mer halves


def test_exact_and_one_mismatch_hits_match_the_reference(tmp_path, monkeypatch):
    exact = "TTTT" + TARGET + "TTTT"
    # ⚠ the substituted base must actually differ — TARGET already ends in 'A', so "…[:15] + 'A'"
    # reconstructs TARGET exactly and silently tests the wrong thing (caught on the first run)
    assert TARGET[15] != "G"
    one_mm = "GGGG" + TARGET[:15] + "G" + "GGGG"          # mismatch in the final base
    two_mm = "GGGG" + "CC" + TARGET[2:14] + "CC" + "GGGG"  # must NOT count
    fast, ref, meta = _run_both(
        tmp_path, monkeypatch, [(TARGET,)],
        [("NM_000001", exact), ("NM_000002", one_mm), ("NM_000003", two_mm)])

    _assert_identical(fast, ref)
    assert meta["transcripts_scanned"] == 3
    assert fast[0]["offtarget_exact"] == 1
    assert fast[0]["offtarget_le1mm"] == 2      # the exact one plus the single-mismatch one


def test_a_record_with_no_seed_is_scored_identically(tmp_path, monkeypatch):
    """The prefilter skips these entirely; the reference walks them and finds nothing. Same answer."""
    fast, ref, _ = _run_both(tmp_path, monkeypatch, [(TARGET,)],
                             [("NM_000010", "AAAA" * 40), ("NM_000011", "CCCC" * 40)])
    _assert_identical(fast, ref)
    assert fast[0]["offtarget_le1mm"] == 0


def test_repeated_and_overlapping_hits_in_one_record(tmp_path, monkeypatch):
    """Per-record `seen` de-duplication is load-bearing: one window found via BOTH half-seeds must be
    counted once, not twice."""
    seq = ("N" * 5).replace("N", "T") + (TARGET + "AC") * 4 + "TTTT"
    fast, ref, _ = _run_both(tmp_path, monkeypatch, [(TARGET,)], [("NM_000020", seq)])
    _assert_identical(fast, ref)
    assert fast[0]["offtarget_le1mm"] >= 4


def test_the_five_hit_cap_fills_in_the_same_order(tmp_path, monkeypatch):
    """`offtarget_hits` is capped at five, so ORDER decides which five are kept."""
    records = [(f"NM_1000{i:02d}", "GG" + TARGET + "GG") for i in range(9)]
    fast, ref, _ = _run_both(tmp_path, monkeypatch, [(TARGET,)], records)
    _assert_identical(fast, ref)
    assert len(fast[0]["offtarget_hits"]) == 5
    assert [h["acc"] for h in fast[0]["offtarget_hits"]] == [r[0] for r in records[:5]]


def test_sirna_seed_counting_stays_non_overlapping(tmp_path, monkeypatch):
    """⛔ THE QUIET ONE. `str.count` is non-overlapping; a sliding-window rewrite is not. On a
    self-overlapping seed the two disagree, and nothing downstream would flag it."""
    seed7 = "AAAAAAA"
    seq = "C" + "A" * 20 + "C" + TARGET
    fast, ref, _ = _run_both(tmp_path, monkeypatch, [(TARGET, seed7)], [("NM_000030", seq)])
    _assert_identical(fast, ref)
    assert fast[0]["sirna_seed_offtarget_sites"] == 2      # 20 A's -> two non-overlapping 7-mers


def test_many_candidates_over_many_records(tmp_path, monkeypatch):
    """The case the rewrite exists for: the answer must not depend on how many designs are in flight."""
    targets = [
        ("ACGTACGTTGCATGCA", "GCATGCA"),
        ("TTGGCCAAGGCCTTAA", "GGCCTTA"),
        ("ACGTACGTAAAACCCC", "GTAAAAC"),
        ("GGGGTTTTACGTACGT", "TTACGTA"),
    ]
    records = []
    for i, (t, _s) in enumerate(targets):
        records.append((f"NM_2000{i:02d}", "TT" + t + "TT"))
        records.append((f"NM_3000{i:02d}", "GG" + t[:15] + "A" + "GG"))
    records.append(("NM_400000", "ACGT" * 60))

    fast, ref, meta = _run_both(tmp_path, monkeypatch, targets, records)
    _assert_identical(fast, ref)
    assert meta["transcripts_scanned"] == len(records)
    assert sum(c["offtarget_le1mm"] for c in fast) > 0


def test_max_records_still_stops_the_stream(tmp_path, monkeypatch):
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    _write_fasta(tmp_path, [(f"NM_5000{i:02d}", "GG" + TARGET + "GG") for i in range(10)])
    meta = ai.offtarget_scan([_cand(TARGET)], max_records=3)
    assert meta["transcripts_scanned"] == 3
