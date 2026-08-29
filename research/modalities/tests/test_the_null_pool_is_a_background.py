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


def _fake_matrix(n_symbols=300, n_probes_per=2, n_samples=8, seed=7):
    """A parsed matrix shaped like `_read_target`'s locals: probes, values, sym, bg, n_s, samples.

    ⛔ IT DELIBERATELY HAS FAR MORE SYMBOLS THAN ANY `want` PASSED TO IT, because the defect this
    file now guards was a producer that sampled the WANTED genes and reported the result as the
    array. A fixture where the two coincide cannot see that, and the first version of these tests
    was exactly such a fixture — it passed against a producer that was fabricating its frame."""
    rng = random.Random(seed)
    syms = [f"SYM{i:04d}" for i in range(n_symbols)]
    probes, sym, values = [], {}, []
    for g in syms:
        for k in range(n_probes_per):
            pid = f"{g}_p{k}"
            probes.append(pid)
            sym[pid] = g
            values.append([rng.uniform(0, 10) for _ in range(n_samples)])
    samples = [{"gsm": f"GSM{i:03d}"} for i in range(n_samples)]
    bg = [{"mean": 5.0, "sd": 2.0} for _ in range(n_samples)]
    return samples, probes, values, sym, bg, n_samples, syms


# ------------------------------------------------------------------ 1. the producer
def test_the_frame_is_the_whole_array_and_not_the_wanted_genes():
    """⛔⛔ THE REGRESSION TEST FOR AUT-PD-178, AND THE ONE THAT MATTERS MOST IN THIS FILE. The
    producer drew from `rec["genes"]`, which `_read_target` filters to `g in want`, so the published
    "background" was 100.0% the union of the curated roster and the signature members — 2,284 of
    2,284 on GSE24369 — while its own `sampling_frame` said the opposite. Ten of 300 symbols are
    wanted here; the frame must be 300."""
    samples, probes, values, sym, bg, n_s, syms = _fake_matrix()
    want = set(syms[:10])
    blk = P._background_draw(samples, probes, values, sym, bg, n_s, want, "M1")
    assert blk["n_frame"] == 300, f"frame is {blk['n_frame']}, not the array's 300 symbols"
    assert len(set(blk["z"]) - want) > 200, "almost everything drawn is a WANTED gene"
    assert blk["n_drawn_also_wanted"] <= 10


def test_the_background_is_reproducible_and_matrix_specific():
    m = _fake_matrix()
    first = P._background_draw(*m[:6], set(), "M1")
    second = P._background_draw(*m[:6], set(), "M1")
    other = P._background_draw(*m[:6], set(), "M2")
    assert set(first["z"]) == set(second["z"]), "the same seed drew a different pool"
    assert first["seed"] != other["seed"], "two matrices share a seed"


def test_the_background_carries_the_same_z_the_rest_of_the_artifact_reports():
    """⛔ IF THIS DRIFTS, THE NULL AND THE PANELS ARE ON DIFFERENT SCALES and every comparison
    between them is meaningless. The `genes` block rounds the probe mean to 4 dp BEFORE
    standardising; so must this, or a symbol in both carries two different numbers."""
    samples, probes, values, sym, bg, n_s, syms = _fake_matrix(n_symbols=40)
    blk = P._background_draw(samples, probes, values, sym, bg, n_s, set(), "M1")
    for g, row in blk["z"].items():
        rows = [v for pid, v in zip(probes, values) if sym[pid] == g]
        expected = []
        for i in range(n_s):
            v = round(sum(r[i] for r in rows) / len(rows), 4)
            expected.append(round((v - bg[i]["mean"]) / max(1e-9, bg[i]["sd"]), 4))
        assert row == expected, f"{g} is not the same reduction the genes block uses"


def test_the_background_records_the_frame_it_sampled_from():
    samples, probes, values, sym, bg, n_s, syms = _fake_matrix(n_symbols=50)
    blk = P._background_draw(samples, probes, values, sym, bg, n_s, set(), "M1")
    assert blk["n_frame"] == 50
    assert blk["n_drawn"] == min(P.BACKGROUND_N, 50) == 50
    assert blk["n_requested"] == P.BACKGROUND_N
    assert "unfiltered" in blk["sampling_frame"]
    assert "n_drawn_also_wanted" in blk


def test_the_background_is_not_filtered_toward_the_expressed_or_the_variable():
    """★ THE MUTATION FOR THE 'UNFILTERED' CLAIM. Give half the frame a flat profile — what an
    expression or variance cut removes — and require it to survive the draw at roughly its share."""
    samples, probes, values, sym, bg, n_s, syms = _fake_matrix(n_symbols=400)
    dead = set(syms[:200])
    for k, pid in enumerate(probes):
        if sym[pid] in dead:
            values[k] = [5.0] * n_s
    drawn = set(P._background_draw(samples, probes, values, sym, bg, n_s, set(), "M1")["z"])
    share = len(drawn & dead) / len(drawn)
    assert 0.35 < share < 0.65, f"flat-profile genes are {share:.0%} of the draw — something filters"


def test_the_collector_never_draws():
    """⛔ `_background_reads` GATHERS; it must not sample. It drew once, from the reduced record,
    and that is the whole of AUT-PD-178. A `live` entry with no stored block yields nothing."""
    tgt = {"genes": {f"G{i}": {"values": [1.0]} for i in range(50)}}
    assert P._background_reads({"m": (tgt, None, None, None)}) == {}
    tgt["background_reads_block"] = {"z": {"A": [1.0]}}
    assert P._background_reads({"m": (tgt, None, None, None)}) == {"m": {"z": {"A": [1.0]}}}


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


def test_a_background_contained_in_the_panels_is_refused(monkeypatch, tmp_path):
    """⛔⛔ THE CONSUMER HALF OF AUT-PD-178, AND IT MUST NOT TRUST THE PRODUCER'S SELF-REPORT.

    The block that reached the trunk was well-formed, fully populated, and carried a
    `sampling_frame` string asserting it was drawn from the whole array. Nothing about its FORM was
    wrong — only its CONTENT, which was 100.0% the union of the curated roster and the signature
    members. So the check is made against the panels and the roster, data this module already holds,
    and never against `n_frame` or `sampling_frame`: a producer with the wrong frame reports those
    just as confidently as a correct one."""
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    smr = (src.get("signature_member_reads") or {}).get(BIG) or {}
    gsms = smr.get("gsms") or []
    if not gsms:
        pytest.skip("no signature_member_reads on this matrix to borrow a sample order from")
    # ⛔ A background made ENTIRELY of real signature members — the exact published shape.
    members = sorted(smr.get("z") or {})[:600]
    if len(members) < 400:
        pytest.skip("too few signature members on this matrix to reproduce the shape")
    row = _subject_row(src, BIG, gsms)
    src["background_reads"] = {}
    for mf in sorted(src.get("signature_member_reads") or {}):
        g2 = ((src["signature_member_reads"].get(mf) or {}).get("gsms")) or []
        if not g2:
            continue
        mem = sorted(src["signature_member_reads"][mf].get("z") or {})[:600]
        src["background_reads"][mf] = {
            "platform": "GPLFAKE", "gsms": g2, "seed": "test",
            "sampling_frame": "every symbol ANY probe on this array maps to, unfiltered",
            "n_frame": 20000, "n_requested": 3000, "n_drawn": len(mem),
            "z": {g: _subject_row(src, mf, g2) for g in mem},
        }
    patched = tmp_path / "panels.json"
    patched.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(patched))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")
    with pytest.raises(SystemExit) as e:
        N.build(n_draws=5)
    msg = str(e.value)
    assert "not a background" in msg
    assert "AUT-PD-178" in msg, "the refusal does not point at the incident that motivates it"


def test_the_floor_admits_a_real_background(monkeypatch, tmp_path):
    """★ THE OTHER HALF OF THE MUTATION. A guard that refused every background would pass the test
    above while making the read unusable, so the same floor must ADMIT a pool that overlaps the
    panels at a realistic share rather than being contained in them."""
    with open(N.PANELS, encoding="utf-8") as fh:
        src = json.load(fh)
    full = _background_for(src, lambda mf, gsms: (_subject_row(src, mf, gsms), 400))
    if BIG not in full:
        pytest.skip("no signature_member_reads on the large matrix")
    for mf, blk in full.items():
        g2 = blk["gsms"]
        mem = sorted((src["signature_member_reads"].get(mf) or {}).get("z") or {})[:40]
        # ~10% panel members, the share a real array background would carry.
        for g in mem:
            blk["z"][g] = _subject_row(src, mf, g2)
        blk["n_drawn"] = len(blk["z"])
    src["background_reads"] = full
    patched = tmp_path / "panels.json"
    patched.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(N, "PANELS", str(patched))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "full_membership_background_null")
    doc = N.build(n_draws=20)          # must NOT raise
    assert doc["series"][BIG]["panels"], "a legitimate background was refused"
