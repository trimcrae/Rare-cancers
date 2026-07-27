#!/usr/bin/env python3
"""Tests for the board census, the variant-SKU allow-list, and the $0 rule-out sweep.

WHAT THESE PIN, and why each is a regression rather than a feature:

  1. **THE ANCHOR DOES NOT MOVE.** `REFERENCE_NS_PER_H`, the three benched figures and the ladder basis are
     what every `$/ns` in the repo and in the ladder is quoted against. Widening the gradeable pool must leave
     them bit-identical, or every historical figure silently re-bases. This is the single most important test
     in the file and it asserts on exact float equality on purpose.
  2. **NO CARD ACQUIRES A THROUGHPUT BY ACCIDENT.** `card_of` was a longest-first SUBSTRING sweep, so any
     marketplace name containing a benched key inherited that card's number. `RTX 4090D` — a cut-down SKU with
     ~11 % fewer CUDA cores — took the full RTX 4090 figure, which UNDERSTATES its `$/ns` and lures a rental
     in. Pinned in both directions: the allow-listed supersets still resolve, everything else returns None.
  3. **ONE MATCHER, NOT TWO.** `gpu_backend.measured_ns_per_day` carried its own copy of the substring sweep.
     A second implementation of the rule is free to disagree with the first — which is the whole reason the
     throughput TABLE has one home — so the two are pinned to agree on the awkward names.
  4. **THE RULE-OUT IS ONE-DIRECTIONAL.** A rule-out needs an UPPER bound on throughput and a rule-in needs a
     LOWER one. The sweep may only ever say RULED_OUT or CANNOT_RULE_OUT, and the ceiling it uses must be the
     MOST generous of the candidate predictors, inflated by their worst under-prediction — otherwise a
     heuristic kills a card that a five-cent bench would have shown to be the cheapest on the board.
  5. **BREAK-EVEN IS THE EXACT INVERSE OF THE COST FUNCTION.** It is a screen, and a screen that does not
     round-trip against `vast_cost_model.usd_per_ns` is quietly a different quantity.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import gpu_backend as gb  # noqa: E402
import vast_board_census as vbc  # noqa: E402
import vast_cost_model as vcm  # noqa: E402


# =============================================================================================================
# 1. the anchor
# =============================================================================================================
def test_the_three_benched_figures_are_untouched():
    """Exact equality PER ANCHOR, deliberately. These are measurements; a 'harmless' re-round is a silent
    re-basing. Written as a subset check rather than whole-dict equality because GROWING the table is the
    point of the calibration lane — what must never move is the three figures the whole repo was priced
    against (2026-07-27: six measured cards added by `vast_bench_sweep`)."""
    for card, ns in {"RTX4090": 755.36, "RTX4080": 703.51, "RTX3090": 359.36}.items():
        assert vcm.MEASURED_NS_PER_DAY_84K[card] == ns
    assert vcm.REFERENCE_CARD == "RTX4090"


def test_reference_ns_per_h_is_bit_identical():
    assert vcm.REFERENCE_NS_PER_H == 755.36 / 24.0
    assert vcm.ns_per_hour("RTX 4090") == 755.36 / 24.0
    assert vcm.ns_per_hour("RTX 4080") == 703.51 / 24.0
    assert vcm.ns_per_hour("RTX 3090") == 359.36 / 24.0


def test_the_ladder_basis_does_not_move():
    """The basis every gate compares against is `plan $/ref-GPU-h / REFERENCE_NS_PER_H`. Widening the pool
    must not touch it — a gate whose threshold moves with the fix is not the same gate."""
    import congeneric_fanout as cf
    assert cf.basis_usd_per_ns() == cf._usd_per_ref_gpu_h()[1] / (755.36 / 24.0)


def test_an_alias_never_changes_a_measured_card():
    """Adding entries to CONSERVATIVE_ALIASES must not be able to shadow a benched card."""
    assert not (set(vcm.CONSERVATIVE_ALIASES) & set(vcm.MEASURED_NS_PER_DAY_84K))
    for variant, (base, _why) in vcm.CONSERVATIVE_ALIASES.items():
        assert base in vcm.MEASURED_NS_PER_DAY_84K, f"{variant} aliases a card that was never benched"


# =============================================================================================================
# 2. no card acquires a throughput by accident
# =============================================================================================================
@pytest.mark.parametrize("name,expect", [
    ("RTX 4090", "RTX4090"), ("RTX 4080", "RTX4080"), ("RTX 3090", "RTX3090"),
    # a VENDOR PREFIX is free: the marketplace says `RTX 4090`, the CUDA driver says the long form, and both
    # have to reach the same measurement or a bench cannot be matched to the offer that produced it
    ("NVIDIA GeForce RTX 4090", "RTX4090"), ("NVIDIA GeForce RTX 3090", "RTX3090"),
    # MEASURED 2026-07-27, so it no longer borrows the RTX 3090's figure — a measurement always wins over
    # the alias that stood in for it, and this one came in ~34% above the number it was borrowing.
    ("NVIDIA GeForce RTX 3090 Ti", "RTX3090TI"),
    # ...but a TRAILING qualifier is fatal unless it is on the allow-list — that is what marks a different SKU
    ("NVIDIA GeForce RTX 4090 Laptop GPU", None),
    # allow-listed strict spec supersets — the borrowed figure is a LOWER bound, so $/ns is an UPPER bound
    ("RTX 3090 Ti", "RTX3090TI"), ("RTX 4080S", "RTX4080"), ("RTX 4080 SUPER", "RTX4080"),
    # everything else, including the cut-down SKU that used to inherit the reference card
    ("RTX 4090D", None), ("RTX PRO 6000 WS", None), ("A100 SXM4", None),
    ("H100 SXM", None), ("Titan RTX", None), ("Q RTX 8000", None), ("", None), (None, None),
])
def test_card_of_is_an_allow_list_not_a_substring_sweep(name, expect):
    assert vcm.card_of(name) == expect


def test_the_cut_down_4090_no_longer_borrows_the_reference_figure():
    """The concrete defect: an RTX 4090D was on the live board being priced as a full RTX 4090, which
    understates its $/ns in the direction that BUYS. It must now be excluded like any unbenched card."""
    assert vcm.ns_per_hour("RTX 4090D") is None
    assert gb.measured_ns_per_day("RTX 4090D") is None
    assert "RTX4090D" in vcm.ANTI_CONSERVATIVE_VARIANTS


def test_provenance_distinguishes_a_measurement_from_a_borrowed_bound():
    assert vcm.throughput_provenance("RTX 4090")[0] == "measured"
    assert vcm.throughput_provenance("RTX 4080S")[0] == "conservative_alias"
    # RTX 3090 Ti graduated from alias to measurement on 2026-07-27; the pair below keeps both states covered.
    assert vcm.throughput_provenance("RTX 3090 Ti")[0] == "measured"
    assert vcm.throughput_provenance("RTX 3090 Ti")[1] == "RTX3090TI"
    assert vcm.throughput_provenance("H200 NVL")[0] == "unbenched"
    # An alias must SAY which way it errs, so nobody reads it as a measurement.
    assert "LOWER" in vcm.throughput_provenance("RTX 4080S")[2]


# =============================================================================================================
# 3. one matcher
# =============================================================================================================
@pytest.mark.parametrize("name", ["RTX 4090", "RTX 4090D", "RTX 3090 Ti", "RTX 4080S", "H200 NVL",
                                  "RTX PRO 6000 WS", "Q RTX 8000"])
def test_backend_and_cost_model_agree_on_every_awkward_name(name):
    c = vcm.card_of(name)
    expect = None if c is None else vcm.MEASURED_NS_PER_DAY_84K[c]
    assert gb.measured_ns_per_day(name) == expect


# =============================================================================================================
# 4. the rule-out is one-directional and generous
# =============================================================================================================
def test_ceilings_are_inflated_by_the_worst_under_prediction():
    c = vbc.throughput_ceilings({"RTX4090": 97.1, "RTX4080": 65.4, "RTX3090": 44.4})
    assert set(c) == {"fp32_tflops", "mem_bandwidth_gb_s", "vast_dlperf"}
    for label, v in c.items():
        # >= 1.0 always: a law that never under-predicts must not be allowed to SHRINK the ceiling.
        assert v["under_prediction_inflation"] >= 1.0, label


def test_the_bound_is_the_max_over_predictors_not_the_min():
    """A rule-out must survive the FRIENDLIEST reading. The three laws disagree by >2x on some cards, and
    taking the min would kill cards that one defensible heuristic says are fine."""
    c = vbc.throughput_ceilings({"RTX4090": 97.1, "RTX4080": 65.4, "RTX3090": 44.4})
    bound, detail = vbc.upper_bound_ns_per_day("A100 SXM4", c, dlperf=95.4)
    per_law = [v for k, v in detail.items() if k != "point_prediction"]
    assert bound == pytest.approx(max(per_law), rel=1e-3)   # detail rows are rounded for the readout
    assert bound > min(per_law) * 1.5      # the laws really do disagree here — the choice is load-bearing


def test_a_card_with_no_spec_input_cannot_be_ruled_out():
    """A missing specification is not evidence of slowness. Silence must not read as a rule-out."""
    c = vbc.throughput_ceilings({"RTX4090": 97.1, "RTX4080": 65.4})
    bound, _ = vbc.upper_bound_ns_per_day("SOME NEW CARD", c, dlperf=None)
    assert bound is None
    assert vbc.rule_out(99999.0, bound)[0] == "CANNOT_RULE_OUT"


def test_rule_out_needs_a_margin_beyond_the_ceiling():
    """A card that merely grazes the ceiling stays alive: the spec figures are not measurements, and one
    wrong in the tight direction must not be able to kill a card."""
    assert vbc.rule_out(1000.0, 1000.0)[0] == "CANNOT_RULE_OUT"
    assert vbc.rule_out(1000.0 * vbc.RULE_OUT_MARGIN * 0.99, 1000.0)[0] == "CANNOT_RULE_OUT"
    assert vbc.rule_out(1000.0 * vbc.RULE_OUT_MARGIN * 1.01, 1000.0)[0] == "RULED_OUT"


def test_every_candidate_spec_key_is_a_normalised_name():
    """A spec keyed on an un-normalised string is silently dead weight — it can never match an offer."""
    for k in vbc.CANDIDATE_SPECS:
        assert vcm.normalise_gpu_name(k) == k
    for k in vbc._BENCHED_SPECS:
        assert k in vcm.MEASURED_NS_PER_DAY_84K


# =============================================================================================================
# 5. break-even round-trips against the cost function
# =============================================================================================================
@pytest.mark.parametrize("bid,storage", [(0.05, 0.011), (0.20, 0.0), (1.30, 0.05)])
def test_breakeven_inverts_usd_per_ns_exactly(bid, storage):
    target = 0.00731
    nsh = vbc.breakeven_ns_per_h(target, bid, storage)
    back = vcm.usd_per_ns(bid, storage, nsh)
    assert back == pytest.approx(target, rel=1e-9)


def test_breakeven_is_none_for_a_non_positive_target():
    assert vbc.breakeven_ns_per_h(0.0, 0.1, 0.01) is None
    assert vbc.breakeven_ns_per_h(None, 0.1, 0.01) is None


def test_census_counts_and_classifies_a_synthetic_board():
    """End-to-end on a hand-built board: the benched card is priceable, the cut-down SKU is not, and the
    unbenched model lands in exactly one of the two verdict buckets."""
    import dataclasses
    from congeneric_fanout_vast import FANOUT_RES
    res = dataclasses.replace(FANOUT_RES, exclude_machine_ids=())

    def offer(i, gpu, bid):
        return {"id": i, "machine_id": 1000 + i, "gpu_name": gpu, "min_bid": bid, "num_gpus": 1,
                "gpu_ram": 24576, "cpu_ram": 64 * 1024, "cpu_cores_effective": 16, "disk_space": 200,
                "reliability2": 0.99, "cuda_max_good": 13.0, "rentable": True, "storage_cost": 0.20,
                "dph_total": bid, "dlperf": 100.0}

    board = [offer(1, "RTX 4090", 0.15), offer(2, "RTX 4090D", 0.15), offer(3, "RTX 5090", 0.20),
             offer(4, "B200", 6.0)]
    doc = vbc.census(board, res, n_units=2)
    by = {r["gpu_name"]: r for r in doc["by_gpu_model"]}
    assert by["RTX 4090"]["priceable"] and by["RTX 4090"]["throughput_provenance"] == "measured"
    assert not by["RTX 4090D"]["priceable"]
    assert doc["board_depth"]["priceable"] == 1 and doc["board_depth"]["qualifying"] == 4
    for name in ("RTX 4090D", "RTX 5090", "B200"):
        assert by[name]["verdict"] in ("RULED_OUT", "CANNOT_RULE_OUT")
    # A $6.00/hr B200 has to be absurdly fast to compete and cannot be; a $0.20/hr 5090 plainly can.
    assert by["B200"]["verdict"] == "RULED_OUT"
    assert by["RTX 5090"]["verdict"] == "CANNOT_RULE_OUT"
    assert {r["gpu_name"] for r in doc["ruled_out"]} | {r["gpu_name"] for r in doc["bench_shortlist"]} == {
        "RTX 4090D", "RTX 5090", "B200"}


# =============================================================================================================
# 6. a bench lands on the card it asked for, or on nothing
# =============================================================================================================
def _o(i, gpu, bid):
    return {"id": i, "machine_id": 900 + i, "gpu_name": gpu, "min_bid": bid, "dph_total": bid,
            "num_gpus": 1, "gpu_ram": 24576, "rentable": True}


def test_require_gpu_refuses_to_substitute_a_benched_card_for_the_one_asked_for():
    """Without this, `BENCH_GRID=rtx5090:9.5` rents an RTX 4090 — because `_select_cheapest_offer` returns the
    best MEASURED offer first — and files its throughput under `rtx5090`. That is the 2026-07-24 fallback
    incident (a Quadro RTX 8000 tabulated as an A10) which got a whole grid withdrawn."""
    board = [_o(1, "RTX 4090", 0.15), _o(2, "RTX 5090", 0.40)]
    soft = gb.ResourceSpec(gpu="rtx5090", min_vram_gb=24, min_cuda=0.0)
    assert gb._select_cheapest_offer(board, soft)["gpu_name"] == "RTX 4090"      # ranking wins: preference
    hard = gb.ResourceSpec(gpu="rtx5090", min_vram_gb=24, min_cuda=0.0, require_gpu=True)
    assert gb._select_cheapest_offer(board, hard)["gpu_name"] == "RTX 5090"      # constraint wins


def test_require_gpu_returns_nothing_rather_than_a_near_miss():
    """An unavailable card must fail the submit cleanly. Renting 'something close' is how a bench produces a
    number for a card that never ran."""
    board = [_o(1, "RTX 4090", 0.15), _o(2, "RTX 4090D", 0.15)]
    hard = gb.ResourceSpec(gpu="rtx5090", min_vram_gb=24, min_cuda=0.0, require_gpu=True)
    assert gb._select_cheapest_offer(board, hard) is None
    # ...and the cut-down SKU does not satisfy a request for the full card either
    hard4090 = gb.ResourceSpec(gpu="rtx4090", min_vram_gb=24, min_cuda=0.0, require_gpu=True)
    assert gb._select_cheapest_offer([_o(2, "RTX 4090D", 0.15)], hard4090) is None


def test_require_gpu_distinguishes_the_pro_6000_variants():
    """`RTXPRO6000S` must not be satisfied by `RTX PRO 6000 WS` — different SKUs, and the census treats them
    as separate rows with separate break-evens."""
    board = [_o(1, "RTX PRO 6000 WS", 0.20), _o(2, "RTX PRO 6000 S", 0.35)]
    hard = gb.ResourceSpec(gpu="rtxpro6000s", min_vram_gb=24, min_cuda=0.0, require_gpu=True)
    assert gb._select_cheapest_offer(board, hard)["gpu_name"] == "RTX PRO 6000 S"


def test_require_gpu_defaults_off_so_production_selection_is_unchanged():
    """Every production lane ranks on $/ns and takes whatever wins — 'the card is not the decision, the offer
    is'. This flag must be opt-in or that rule quietly inverts."""
    assert gb.ResourceSpec().require_gpu is False
    from congeneric_fanout_vast import FANOUT_RES
    assert FANOUT_RES.require_gpu is False


def test_bench_flags_accept_a_card_whose_driver_name_differs_from_its_market_name():
    """The wrong-card gate compares the REQUEST to the marketplace name when the leg recorded one. Comparing
    against the CUDA device string instead rejects every Blackwell workstation bench, because
    `rtxpro6000ws` is not a substring of 'NVIDIA RTX PRO 6000 Blackwell Workstation Edition'."""
    import nrv04_vast_launch as nv
    ok = {"status": "OK", "healthy": "True", "wall_s": 61.0, "cv": 0.01,
          "gpu_requested": "rtxpro6000ws", "market_gpu_name": "RTX PRO 6000 WS",
          "_raw": "device='NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition'"}
    assert nv._bench_flags(ok) == []
    bad = dict(ok, market_gpu_name="RTX 4090")
    assert any(f.startswith("wrong_card") for f in nv._bench_flags(bad))
