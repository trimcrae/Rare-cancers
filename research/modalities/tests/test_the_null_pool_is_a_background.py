#!/usr/bin/env python3
"""THE NULL'S POOL IS A SEPARATE DECISION FROM WHAT THE PANELS ARE SCORED OVER (AUT-PD-170).

⛔⛔ THIS FILE EXISTS BECAUSE CONFLATING THEM IS THE DEFECT AUT-PD-167 MEASURED, AND THE CONFLATION
WAS INVISIBLE PRECISELY BECAUSE IT WAS STRUCTURAL. `ndrg1_panel_attribution.py` drew its
size-matched null from whatever genes happened to carry a per-sample value — so the null's reference
population was, under one read, a 479-gene roster curated for six unrelated questions, and under the
other, mostly the signature sets under test. Neither is a background, and the size-matched null
cannot notice: it controls for panel SIZE and for array structure, never for who is in the pool.

★ WHAT IS PINNED HERE, AND WHY EACH IS A DIFFERENT KIND OF CLAIM.

  1. **THE PRODUCER DRAWS A REAL, REPRODUCIBLE, UNFILTERED SAMPLE.** `_background_reads` is
     exercised against a synthetic matrix — no network, no GEO — and must return the same genes for
     the same seed, a different set for a different matrix, and the same z the rest of the artifact
     reports. ⚠ It must also RECORD its sampling frame: a background pool whose selection rule is
     unwritten is the same confound with a better name.
  2. **THE CONSUMER REFUSES RATHER THAN FALLING BACK.** Selecting the background read when the
     block is absent must raise, not quietly narrow. A silent narrowing under unchanged field names
     is exactly how a committed verdict reversed with nobody able to see it.
  3. **THE NULL POOL AND THE SCORING CACHE ARE ACTUALLY DIFFERENT OBJECTS.** Asserted by mutating
     the background so that it CANNOT be the scored pool, and requiring the null to move while the
     panel's own rho does not.

⚠ Every mutation is applied to LOCAL COPIES — never the module, never the committed artifact
(research-loop §3).
"""

from __future__ import annotations

import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import emc_expression_panels as P  # noqa: E402
import ndrg1_panel_attribution as N  # noqa: E402

BIG = "GSE24369_series_matrix.txt.gz"


SMALL = "GSE4303-GPL3290_series_matrix.txt.gz"


def _background_for(src, rows_for):
    """A synthetic `background_reads` covering EVERY matrix the module will walk.

    ⛔ COVERING ONLY THE MATRIX UNDER TEST IS WHAT THIS HELPER EXISTS TO PREVENT, and the module is
    right to refuse it: a background read present on one platform and absent on the other would give
    the two series nulls of different provenance under identical field names. `rows_for(mf, gsms)`
    returns the z row every synthetic gene on that matrix carries."""
    out = {}
    for mf in sorted(src.get("signature_member_reads") or {}):
        gsms = ((src["signature_member_reads"].get(mf) or {}).get("gsms")) or []
        if not gsms:
            continue
        row, n = rows_for(mf, gsms)
        out[mf] = {"platform": "GPLFAKE", "gsms": gsms, "sampling_frame": "test", "seed": "test",
                   "n_frame": n, "n_requested": n, "n_drawn": n,
                   # ⛔ NAMES NO REAL GENE, so it cannot overlap a panel or the curated roster.
                   "z": {f"BG{i:04d}": row for i in range(n)}}
    return out


def _subject_row(src, mf, gsms, sign=1.0):
    subj = N.sample_z(src["gene_reads"], N.SUBJECT, mf)
    order = {g: i for i, g in enumerate(gsms)}
    row = [None] * len(gsms)
    for smp, v in (subj or {}).items():
        if smp in order:
            row[order[smp]] = round(sign * v, 4)
    return row


def _fake_tgt(n_genes=50, n_samples=8, seed=7):
    """A matrix shaped like the real one and nothing like it in content. `_zrow` needs `n_samples`,
    `background_per_sample` and `genes[g]['values']`; `_background_reads` needs `samples` too."""
    rng = random.Random(seed)
    return {
        "platform": "GPLFAKE",
        "n_samples": n_samples,
        "samples": [{"gsm": f"GSM{i:03d}"} for i in range(n_samples)],
        "background_per_sample": [{"mean": 5.0, "sd": 2.0} for _ in range(n_samples)],
        "genes": {f"G{i:03d}": {"values": [rng.uniform(0, 10) for _ in range(n_samples)]}
                  for i in range(n_genes)},
    }


def _live(**tgts):
    return {mf: (t, None, None, None) for mf, t in tgts.items()}


# ------------------------------------------------------------------ 1. the producer
def test_the_background_is_reproducible_and_matrix_specific():
    live = _live(a=_fake_tgt(), b=_fake_tgt(seed=99))
    first = P._background_reads(live)
    second = P._background_reads(live)
    assert set(first["a"]["z"]) == set(second["a"]["z"]), "the same seed drew a different pool"
    assert first["a"]["seed"] != first["b"]["seed"], (
        "both matrices share a seed, so their pools are drawn in lockstep rather than independently")


def test_the_background_carries_the_same_z_the_rest_of_the_artifact_reports():
    """⛔ IF THIS DRIFTS, THE NULL AND THE PANELS ARE ON DIFFERENT SCALES and every comparison
    between them is meaningless — the failure mode ruled out by measurement in AUT-PD-167, kept
    ruled out here by construction."""
    tgt = _fake_tgt()
    blk = P._background_reads(_live(a=tgt))["a"]
    for g, row in blk["z"].items():
        expected = [None if x is None else round(x, 4) for x in P._zrow(tgt, g)]
        assert row == expected, f"{g} disagrees with _zrow"


def test_the_background_records_the_frame_it_sampled_from():
    """A pool with no recorded selection rule is not auditable, and an unauditable null is the whole
    defect this block was built to remove."""
    blk = P._background_reads(_live(a=_fake_tgt(n_genes=50)))["a"]
    assert blk["n_frame"] == 50
    assert blk["n_drawn"] == min(P.BACKGROUND_N, 50) == 50
    assert blk["n_requested"] == P.BACKGROUND_N
    assert "unfiltered" in blk["sampling_frame"]
    assert set(blk["z"]) <= set(_fake_tgt(n_genes=50)["genes"]), "drew a gene not in the frame"


def test_the_background_is_not_filtered_toward_the_expressed_or_the_variable():
    """★ THE MUTATION FOR THE 'UNFILTERED' CLAIM. Give half the frame a flat, near-zero profile —
    exactly what an expression or variance cut would remove — and require it to survive the draw at
    roughly its share. A producer that quietly filtered would pass every test above and fail this."""
    tgt = _fake_tgt(n_genes=400)
    dead = sorted(tgt["genes"])[:200]
    for g in dead:
        tgt["genes"][g]["values"] = [5.0] * tgt["n_samples"]
    drawn = set(P._background_reads(_live(a=tgt))["a"]["z"])
    share = len(drawn & set(dead)) / len(drawn)
    assert 0.35 < share < 0.65, (
        f"flat-profile genes are {share:.0%} of the draw, not ~50% — something is filtering")


# ------------------------------------------------------------------ 2. the consumer refuses
def test_selecting_the_background_read_without_the_block_raises(monkeypatch, tmp_path):
    """⛔⛔ THE ONE THAT MATTERS. AUT-PD-167 happened because a missing input produced a QUIETLY
    DIFFERENT ANSWER under the same field names instead of an error."""
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    src.pop("background_reads", None)
    stripped = tmp_path / "panels.json"
    stripped.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(stripped))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")
    with pytest.raises(SystemExit) as e:
        N.build(n_draws=5)
    assert "background_reads" in str(e.value)


def test_the_pinned_read_is_one_the_module_implements():
    assert N.MEMBERSHIP_SOURCE in N.MEMBERSHIP_SOURCES
    assert "full_membership_background_null" in N.MEMBERSHIP_SOURCES


def test_the_artifact_states_where_its_null_drew_from(  ):
    """One fact, one place — and a reader comparing two runs needs to know the null's pool changed
    even when every field name is identical."""
    with open(N.OUT, encoding="utf-8") as fh:
        committed = json.load(fh)
    assert committed["panel_membership_source"].get("null_pool")


# ------------------------------------------------------------------ 3. they are different objects
def test_the_null_pool_and_the_scored_membership_are_not_the_same_object(monkeypatch, tmp_path):
    """★ THE MUTATION FOR THE SEPARATION ITSELF. Build a background whose genes track the subject
    NEGATIVELY and are disjoint from every panel. If the null still drew from the scored pool the
    panels' nulls would be unmoved; if the two are genuinely separate the null median must fall.

    ⚠ The panels' own rho must NOT move, because the background is not a scoring source. Asserting
    both directions is what makes this a test of the separation rather than of any change at all.
    """
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    # 400 synthetic genes: the null pool must outnumber the largest panel (231 members), which is a
    # constraint that no longer holds automatically now that the null's pool is not the scored pool.
    src["background_reads"] = _background_for(
        src, lambda mf, gsms: (_subject_row(src, mf, gsms, sign=-1.0), 400))
    if BIG not in src["background_reads"]:
        pytest.skip("no signature_member_reads on the large matrix to borrow a sample order from")
    patched = tmp_path / "panels.json"
    patched.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(patched))

    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_plus_signature_members")
    wide = N.build(n_draws=40)["series"][BIG]
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")
    bg = N.build(n_draws=40)["series"][BIG]

    panel = next(p for p, r in bg["panels"].items() if r.get("scored"))
    assert bg["panels"][panel]["rho"] == wide["panels"][panel]["rho"], (
        "the panel's own score moved, so the background leaked into the SCORING cache")
    assert bg["panels"][panel]["null_median"] < wide["panels"][panel]["null_median"], (
        "the null did not move when its pool was replaced wholesale — the null is still drawing "
        "from the scored membership")


def test_a_background_smaller_than_a_panel_is_a_refusal_not_a_crash(monkeypatch, tmp_path):
    """★ FOUND BY THIS FILE'S OWN FIXTURE BEING TOO SMALL, AND KEPT. Because the null's pool is no
    longer the scored pool, nothing makes it at least as large as the biggest panel — and a
    truncated or partially-fetched background is a real shape. The module must say which pool, which
    panel and which sizes, not raise `ValueError: Sample larger than population` out of random.py.

    ⚠ It must also stay a statement about the POOL. A panel left unscored for want of a null is not
    a panel that failed to separate, and the row must not read like one."""
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    src["background_reads"] = _background_for(
        src, lambda mf, gsms: (_subject_row(src, mf, gsms), 8))
    if BIG not in src["background_reads"]:
        pytest.skip("no signature_member_reads on the large matrix to borrow a sample order from")
    patched = tmp_path / "panels.json"
    patched.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(patched))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")

    doc = N.build(n_draws=5)          # must not raise
    rows = doc["series"][BIG]["panels"]
    unscored = [r for r in rows.values() if not r.get("scored") and "null pool" in r.get("why", "")]
    assert unscored, f"no panel refused for an undersized null pool: {list(rows)[:3]}"
    assert "about the POOL" in unscored[0]["why"]


def test_the_refusal_names_the_matrix_that_is_missing_its_background(monkeypatch, tmp_path):
    """⛔ A BACKGROUND PRESENT ON ONE PLATFORM AND ABSENT ON THE OTHER MUST REFUSE, not quietly give
    the two series nulls of different provenance under identical field names. Found by this file's
    own first fixture, which covered the large matrix only."""
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    full = _background_for(src, lambda mf, gsms: (_subject_row(src, mf, gsms), 400))
    if BIG not in full or SMALL not in full:
        pytest.skip("this artifact does not carry both matrices")
    src["background_reads"] = {BIG: full[BIG]}          # the small matrix deliberately left out
    patched = tmp_path / "panels.json"
    patched.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(patched))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")
    with pytest.raises(SystemExit) as e:
        N.build(n_draws=5)
    assert SMALL in str(e.value), "the refusal does not say which matrix is missing its background"
