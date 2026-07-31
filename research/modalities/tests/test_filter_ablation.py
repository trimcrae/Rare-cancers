"""THE FILTER ABLATION — the study that tells a narrow board apart from a thin market.

trimcrae, 2026-07-31: *"If we're in a price spike we can wait that out, that's fine. But the floor being 2x
over baseline would be quite unusual. Make sure we aren't filtering too many options out."* Those two
diagnoses call for OPPOSITE actions (CLAUDE.md §6 waits a thin market out; an over-tight filter is fixed), and
nothing in the repo could tell them apart: `vast_board_census` says the board could not be PRICED,
`vast_exclusion_census` says the blacklist ate it, neither says which HARD FILTER did.

Pure tests only — the study takes ONE live board read and then does all its arithmetic client-side, which is
precisely what makes it testable against a fixture.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_filter_ablation as fa  # noqa: E402
from gpu_backend import ResourceSpec  # noqa: E402


def _offer(**kw):
    o = {"id": kw.pop("id", 1), "machine_id": kw.pop("machine_id", 100), "gpu_name": "RTX 4090",
         "num_gpus": 1, "verified": True, "rentable": True, "gpu_ram": 24576, "cpu_ram": 65536,
         "cpu_cores": 16, "disk_space": 200, "reliability2": 0.99, "cuda_max_good": 13.0,
         "min_bid": 0.12, "dph_total": 0.30, "storage_cost": 0.20, "dlperf": 60.0}
    o.update(kw)
    return o


def _res(**kw):
    base = dict(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=60, min_cuda=13.0)
    base.update(kw)
    return ResourceSpec(**base)


# =============================================================================================================
# the predicates mirror the launcher, which is the whole validity claim
# =============================================================================================================
@pytest.mark.parametrize("field,bad,name", [
    ("cuda_max_good", 12.6, "cuda_max_good(min_cuda)"),
    ("cpu_ram", 16384, "cpu_ram(ram_gb)"),
    ("cpu_cores", 4, "cpu_cores(vcpus)"),
    ("disk_space", 40, "disk_space(disk_gb)"),
    ("reliability2", 0.5, "reliability2"),
    ("gpu_ram", 8192, "gpu_ram(min_vram_gb)"),
    ("verified", False, "verified"),
    ("rentable", False, "rentable"),
    ("num_gpus", 2, "num_gpus_1"),
])
def test_each_predicate_rejects_exactly_its_own_violation(field, bad, name):
    preds = fa.predicates(_res())
    good, bad_o = _offer(), _offer(**{field: bad})
    assert preds[name](good) is True
    assert preds[name](bad_o) is False
    # and no OTHER predicate reacts to it — a study whose rows overlap cannot attribute a loss
    for other, fn in preds.items():
        if other != name:
            assert fn(bad_o) is not False or other == name, f"{other} also rejected a {field} violation"


def test_min_ns_per_h_is_a_no_op_when_unset_and_excludes_unbenched_when_set():
    """`ResourceSpec.min_ns_per_h`'s documented rule: an UNBENCHED card cannot clear a floor, so setting one
    silently removes every card the throughput table has never measured — which is most of the board."""
    unset = fa.predicates(_res(min_ns_per_h=0))["min_ns_per_h"]
    assert unset(_offer(gpu_name="RTX PRO 6000 WS")) is True

    on = fa.predicates(_res(min_ns_per_h=28.0))["min_ns_per_h"]
    assert on(_offer(gpu_name="RTX 5090")) is True          # 43.1 ns/h
    assert on(_offer(gpu_name="RTX 4090")) is True          # 33.5
    assert on(_offer(gpu_name="RTX 3090")) is False         # 19.2
    assert on(_offer(gpu_name="RTX PRO 6000 WS")) is False  # unbenched -> cannot clear


# =============================================================================================================
# the arithmetic the readout is graded on
# =============================================================================================================
def test_marginal_cost_is_what_the_filter_removes_ON_TOP_OF_the_others():
    """The actionable number. A filter that is redundant with another has a big `alone` loss and a ZERO
    marginal cost, and confusing the two is how a cheap filter gets blamed for an expensive one."""
    offers = [
        _offer(id=1, machine_id=1),                                   # clears everything
        _offer(id=2, machine_id=2, cuda_max_good=12.6),               # only the CUDA floor rejects it
        _offer(id=3, machine_id=3, cuda_max_good=12.6, cpu_cores=2),  # rejected twice over
    ]
    out = fa.ablate(offers, _res(), interruptible=True, n_units=1, basis=0.003412)
    rows = {r["filter"]: r for r in out["per_filter"]}
    assert out["full_spec"]["surviving"] == 1
    # dropping the CUDA floor re-admits #2 only: #3 still fails on cores
    assert rows["cuda_max_good(min_cuda)"]["marginal_cost_offers"] == 1
    # dropping the cores floor re-admits nothing: #3 still fails on CUDA. Redundant, not expensive.
    assert rows["cpu_cores(vcpus)"]["marginal_cost_offers"] == 0
    assert out["per_filter"][0]["filter"] == "cuda_max_good(min_cuda)", "sorted by what it actually costs"


def test_the_cuda_sweep_is_monotone_and_holds_everything_else():
    offers = [_offer(id=i, machine_id=i, cuda_max_good=c)
              for i, c in enumerate([12.0, 12.4, 12.6, 12.8, 13.0, 13.0])]
    rows = fa.cuda_sweep(offers, _res(), interruptible=True, n_units=1, basis=0.003412)
    counts = [r["surviving"] for r in rows]
    assert counts == sorted(counts, reverse=True), "a higher floor can only ever remove offers"
    assert rows[0]["min_cuda"] == 0.0 and rows[0]["surviving"] == 6
    assert rows[-1]["min_cuda"] == 13.0 and rows[-1]["surviving"] == 2


def test_the_retired_blacklist_is_priced_as_a_counterfactual_not_as_a_live_filter():
    """With the list retired, `ResourceSpec.exclude_machine_ids` is empty and its ablation row reads 0 — true
    and useless. The number that settles whether the removal was worth doing is what those stored ids WOULD
    have removed from today's board."""
    offers = [_offer(id=1, machine_id=11, min_bid=0.05),   # the cheapest, and on the retired list
              _offer(id=2, machine_id=22, min_bid=0.20)]
    cf = fa.blacklist_counterfactual(offers, _res(), interruptible=True,
                                     excluded_ids=["11"], n_units=1, basis=0.003412)
    assert cf["surviving_without_blacklist"] == 2
    assert cf["surviving_with_blacklist"] == 1
    assert cf["offers_it_would_remove"] == 1
    assert cf["best_usd_per_ns_with"] > cf["best_usd_per_ns_without"]
    assert cf["usd_per_ns_penalty_pct"] > 0, "the cost of an exclusion is a PRICE, not just a count"


def test_the_two_tiers_are_priced_separately_and_labelled():
    """Conflating them is the misreading that started this: a hold priced against the small, dear
    uninterruptible tier says nothing about the market the ladder is costed on."""
    offers = [_offer(id=1, machine_id=1, min_bid=0.10, dph_total=0.30)]
    bid = fa.ablate(offers, _res(), interruptible=True, n_units=1, basis=0.003412)
    od = fa.ablate(offers, _res(), interruptible=False, n_units=1, basis=0.003412)
    assert "bid" in bid["tier"] and "on-demand" in od["tier"]
    assert od["full_spec"]["best_usd_per_ns"] > bid["full_spec"]["best_usd_per_ns"], \
        "on-demand must be priced on dph_total, not on the bid floor"


def test_the_permissive_query_selects_the_tier_and_nothing_else_of_substance():
    q = fa.permissive_query(True)
    assert q["type"] == "bid" and fa.permissive_query(False)["type"] == "on-demand"
    # Everything the launcher filters on must be ABSENT here, or the client-side count would be measuring a
    # board the server had already pruned.
    for k in ("cuda_max_good", "cpu_ram", "cpu_cores", "disk_space", "reliability2", "gpu_ram", "verified"):
        assert k not in q, f"{k} must be counted client-side, not pre-filtered by the server"


# =============================================================================================================
# ⚠ A "SAVING" IN THIS TABLE IS NOT ALWAYS A SAVING
# =============================================================================================================
def test_the_ram_floor_carries_its_refutation_next_to_its_gain():
    """THE TRAP THIS CLOSES. The ablation measured relaxing `cpu_ram >= 32 GB` as worth ~35.7 % better $/ns —
    the largest gain in the table — and that number is an ARTEFACT. Every $/ns here is computed on TABLE
    throughput, which is a measure of MD speed and cannot see setup time at all.

    `ternary-rbfe-runbook.md` §2 root-caused, by serial console, setup varying 8 min <-> 30 min on what looked
    like one machine: the provisioner had fallen back to a 4 vCPU / 16 GB box, and openff `interchange`
    parameterising a ~146k-atom system is CPU+RAM bound, so 16 GB swaps and runs ~4x slower. Same GPU — so the
    $/ns is genuinely unchanged and genuinely irrelevant. Against a ~1.00 h median session, a ~4x setup
    penalty converts a rental that banks into one that does not.

    So the caveat must travel WITH the row. A future reader proposing to relax this floor will read the gain
    column first."""
    caveat = fa.FILTER_CAVEATS["cpu_ram(ram_gb)"]
    assert "DO NOT RELAX" in caveat
    assert "8 min" in caveat and "30 min" in caveat, "the measurement must travel with the verdict"
    assert "CPU+RAM bound" in caveat


def test_every_caveat_reaches_the_row_and_the_rendered_readout():
    offers = [_offer(id=1, machine_id=1), _offer(id=2, machine_id=2, cpu_ram=16384)]
    out = fa.ablate(offers, _res(), interruptible=True, n_units=1, basis=0.003412)
    rows = {r["filter"]: r for r in out["per_filter"]}
    assert rows["cpu_ram(ram_gb)"]["caveat"], "the row must carry it"
    doc = {"basis_usd_per_ns": 0.003412, "buy_line_usd_per_ns": 0.006539, "n_units": 1, "tiers": [out]}
    assert "DO NOT RELAX" in fa._render(doc), "and the human-readable readout must print it"


def test_a_filter_with_no_caveat_is_not_given_a_fabricated_one():
    offers = [_offer(id=1, machine_id=1)]
    out = fa.ablate(offers, _res(), interruptible=True, n_units=1, basis=0.003412)
    rows = {r["filter"]: r for r in out["per_filter"]}
    assert rows["disk_space(disk_gb)"]["caveat"] is None
