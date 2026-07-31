"""The GCP card probe: the system it measures, the card it asks for, and the VM it can switch off.

Three things had to hold before this probe's number was worth recording, and each one has a repo incident
behind it rather than a style preference:

1. **THE SIZE.** `gpu_md_bench.py` defaults to a ~36k-atom box and `gpu-bench-gcp.yml` never passed
   `BENCH_EDGE_NM`, so every GCP bench measured a system four times smaller than the lane's real one
   (141,968 particles). A number measured on the wrong system is not a weaker answer to the question — it is
   a confident answer to a different one.

2. **THE CARD.** The workflow hardcoded `nvidia-tesla-t4` for any `n1-*` machine. An `n1-*` created with NO
   accelerator boots CPU-only and `gpu_md_bench` will happily report a real-looking ns/day from the CPU
   platform, so "which card" must be underivable from anything but the card itself.

3. **THE OFF SWITCH.** A GCP VM cannot delete itself — GCE refuses the call (gcp-gpu-facts.md §6) — and
   GPUS_ALL_REGIONS=1 means an orphan blocks every GCP GPU job on the account. `gcp_launch_guard` covers
   detached ternary legs; this probe is covered instead by a create-time cap plus a runner-side teardown, and
   both must be present in the YAML rather than in someone's memory of it.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

import gcp_card_bench as gcb

WF = pathlib.Path(__file__).resolve().parents[3] / ".github/workflows/gpu-bench-gcp.yml"


def _wf_text() -> str:
    assert WF.is_file(), f"missing {WF}"
    return WF.read_text()


# ---------------------------------------------------------------------------------------------------------
# 1. the system size
# ---------------------------------------------------------------------------------------------------------
def test_the_edge_is_derived_from_the_repo_anchor_not_a_typed_density():
    """`edge_nm_for_particles` must reproduce the anchor it is calibrated on exactly."""
    assert gcb.edge_nm_for_particles(gcb.ANCHOR_ATOMS) == pytest.approx(float(gcb.ANCHOR_EDGE_NM))
    assert gcb.predicted_particles(float(gcb.ANCHOR_EDGE_NM)) == gcb.ANCHOR_ATOMS


def test_the_probe_is_sized_to_the_real_ternary_system_not_the_36k_default():
    """The dispatched edge must land within 1 % of 141,968 particles.

    The tolerance is deliberately tight: the whole point of the size choice is that PME cost and the
    bandwidth-vs-FLOPs balance move with particle count, so "roughly the right size" is the failure this
    guards against, not a rounding worry."""
    n = gcb.predicted_particles(gcb.TERNARY_EDGE_NM)
    assert abs(n - gcb.TERNARY_N_PARTICLES) / gcb.TERNARY_N_PARTICLES < 0.01, (
        f"edge {gcb.TERNARY_EDGE_NM} nm builds ~{n:,} particles, not ~{gcb.TERNARY_N_PARTICLES:,}")
    # and it must NOT be the 36k default that made every prior GCP bench answer the wrong question
    assert n > 100_000


def test_both_sizes_run_and_the_ternary_one_runs_first():
    """A VM that dies mid-probe must leave the decision-relevant measurement behind, not the comparability one."""
    edges = [float(x) for x in gcb.DEFAULT_EDGES.split(",")]
    assert edges[0] == gcb.TERNARY_EDGE_NM, "the ternary-sized arm must be measured FIRST"
    assert float(gcb.ANCHOR_EDGE_NM) in edges, (
        "the 84,534-particle anchor must also run, or the GCP cards cannot be compared with "
        "vast_cost_model.MEASURED_NS_PER_DAY_84K in one currency")


def test_the_workflow_actually_passes_the_edge_into_the_vm():
    """The regression that made this necessary: the variable existed and nothing passed it."""
    t = _wf_text()
    assert "BENCH_EDGE_NM=" in t, "the startup script must set BENCH_EDGE_NM per size"
    assert "BENCH_EDGES" in t, "the size list must reach the VM"


# ---------------------------------------------------------------------------------------------------------
# 2. the card
# ---------------------------------------------------------------------------------------------------------
def test_every_n1_card_gets_an_accelerator_and_the_g2_card_does_not():
    for key, card in gcb.CARDS.items():
        flag = gcb.accelerator_flag(key)
        if card.machine.startswith("n1-"):
            assert flag == f"--accelerator=type={card.accelerator},count=1", (
                f"{key} is on {card.machine}: without --accelerator this boots a CPU-only VM that still "
                f"reports a plausible ns/day")
        else:
            assert flag == "", f"{key} is on {card.machine}, which carries its accelerator built in"


def test_the_control_arm_exists():
    assert "l4" in gcb.CARDS, "without the L4 control there is no ratio, only four unanchored speeds"


def test_no_zone_outside_us_central1_is_reachable():
    """gcp-gpu-facts.md §5: quota exists ONLY in us-central1, so another region is a wasted attempt."""
    for key in gcb.CARDS:
        for z in gcb.zone_order(key, "us-east1-b"):
            assert z.startswith("us-central1-"), f"{key} would try {z}, which has no quota"


def test_a_zone_hint_orders_but_never_filters():
    """A wrong hint must cost one failed create, not a card we hold quota for."""
    for key in gcb.CARDS:
        assert set(gcb.zone_order(key)) == set(gcb.ALL_ZONES), (
            f"{key}'s zone list drops a zone — a hint used as a filter is how a usable card looks stocked out")


def test_a_mislabelled_card_is_refused_rather_than_recorded():
    """`card_from_device` is the VERIFY half of "the flag says what we asked for, the device says what ran"."""
    assert gcb.card_from_device("NVIDIA_L4") == "l4"
    assert gcb.card_from_device("Tesla_P100-PCIE-16GB") == "p100"
    assert gcb.card_from_device("Tesla_T4") == "t4"
    assert gcb.card_from_device("Tesla_V100-SXM2-16GB") == "v100"
    assert gcb.card_from_device("") is None


def test_the_workflow_derives_the_machine_and_accelerator_from_the_card_input():
    t = _wf_text()
    assert "--emit-env" in t, "machine/accelerator must be derived by gcp_card_bench, not typed in YAML"
    assert not re.search(r"n1-\*?\S*\)\s*ACCEL=.*nvidia-tesla-t4", t), (
        "the old hardcoded T4-for-any-n1 mapping is back — P100/V100 would silently run on a T4 or on no GPU")
    assert "OPENMM_REQUIRE_CUDA=1" in t, (
        "without this a CPU-platform fallback reports a real-looking ns/day instead of raising")


# ---------------------------------------------------------------------------------------------------------
# 3. the off switch
# ---------------------------------------------------------------------------------------------------------
def _create_invocation(text: str) -> str:
    i = text.index("gcloud compute instances create")
    out = []
    for line in text[i:].splitlines():
        out.append(line)
        if not line.rstrip().endswith("\\"):
            break
    assert len(out) > 1, "create invocation collapsed to one line — extraction is probably wrong"
    return " ".join(ln.rstrip().rstrip("\\").strip() for ln in out)


def test_every_provisioning_branch_caps_the_vm_and_says_what_to_do_at_the_cap():
    """gcp-gpu-facts.md §3: --max-run-duration REQUIRES --instance-termination-action, for STANDARD too.
    Omitting it on the standard branch is what made every on-demand create fail request-validation and get
    mislabelled 'stocked out' for months."""
    t = _wf_text()
    branches = re.findall(r'PROV_FLAGS="([^"]+)"', t)
    assert branches, "no provisioning branch found — extraction is wrong or the launcher was rewritten"
    for flags in branches:
        assert "--max-run-duration=" in flags, (
            f"branch {flags!r} has no create-time cap. Per gcp-gpu-facts.md §6c(3) a non-leg's cap is its "
            f"ONLY guaranteed bound, because the VM cannot delete itself and no watchdog watches a probe.")
        assert "--instance-termination-action=" in flags, f"branch {flags!r} sets a cap with no action"


def test_the_cap_is_short_and_has_one_home():
    """A probe is ~15-20 min. A leg's 72 h cap on a probe would hold the project's only GPU for three days."""
    t = _wf_text()
    m = re.search(r"MAXRUN_S:\s*'(\d+)'", t)
    assert m, "MAXRUN_S must be a single named value, not repeated inside each branch"
    assert int(m.group(1)) <= 7200, f"probe cap {m.group(1)}s is longer than 2 h"
    assert t.count("--max-run-duration=${MAXRUN_S}s") == len(re.findall(r'PROV_FLAGS="', t)), (
        "a branch hardcodes its own cap instead of interpolating MAXRUN_S — that is exactly how the ternary "
        "launcher told an operator a 72 h VM would self-destruct in 7 h")


def test_teardown_is_unconditional_and_does_not_depend_on_the_in_vm_trap():
    t = _wf_text()
    assert "if: always()" in t, "teardown must run on every path including failure and cancellation"
    assert "labels.bench-run=" in t, (
        "a create that fails AFTER allocating leaves a VM whose zone was never exported; the label sweep is "
        "the only thing that finds it")


def test_the_probe_refuses_to_provision_when_the_single_gpu_is_not_free():
    """GPUS_ALL_REGIONS=1: a second GPU job cannot run, and its create failure is indistinguishable from a
    capacity stockout after the fact (gcp-gpu-facts.md §2/§4)."""
    t = _wf_text()
    assert "GPUS_ALL_REGIONS" in t, "the binding cap is never read"
    assert "REFUSING TO PROVISION" in t, "the pre-flight check reports but does not refuse"
    pre = t.index("GPUS_ALL_REGIONS")
    create = t.index("gcloud compute instances create")
    assert pre < create, "the quota check must run BEFORE the create, not beside it"


def _step_body(text: str, title_fragment: str) -> str:
    """The `run:` body of the step whose name contains `title_fragment`. Extraction, not transcription."""
    i = text.index(title_fragment)
    j = text.index("run: |", i)
    k = text.find("\n      - name:", j)
    return text[j:k if k != -1 else len(text)]


def test_the_refusal_gate_cannot_fail_for_a_reason_that_is_not_a_refusal():
    """★★ MEASURED 2026-07-31, run 30631788507. The first version of the pre-flight ran under
    `set -eo pipefail` and read the global cap with `gcloud compute project-info describe`. The step exited
    non-zero with NO refusal annotation, the probe never provisioned — and the GPU was demonstrably free
    (that same run's teardown listed zero instances; gcp-reap-vms run 30631014002 said `no instances in
    project` eleven minutes earlier). The READER failed, not the condition, and an errored gate rendered
    exactly like a refusing one.

    So: the gate step must not abort on a readout, and the ONLY `exit 1` in it must be the refusal.
    """
    body = _step_body(_wf_text(), "PRE-FLIGHT — refuse unless the single GPU is genuinely free")
    assert "set +e" in body, (
        "the pre-flight runs under errexit again — a permission or API failure in a READOUT will abort the "
        "step and be indistinguishable from a refusal")
    assert not re.search(r"^\s*set -e", body, re.M), "errexit is back in the gate"
    exits = re.findall(r"exit 1", body)
    assert len(exits) == 1, f"the gate has {len(exits)} exit-1 paths; exactly one — the refusal — is allowed"
    assert "REFUSING TO PROVISION" in body.split("exit 1")[0], "the single exit 1 is not the refusal"
    # and it must gate on the check that is PROVEN to work here, not only on the one that failed
    assert "instances list" in body, (
        "quota can only be held by an instance (gcp-gpu-facts.md §2) — the instance list is the definitive "
        "zombie test and must be part of the gate")
    assert "rc=" in body, "each probe must report its exit code, or the next failure is a belief again"


def test_the_run_echoes_what_it_was_dispatched_with():
    """tests/test_workflow_dispatch_input_cap.py records that an over-cap workflow silently delivers EMPTY
    inputs. That is invisible unless something prints what arrived."""
    t = _wf_text()
    assert "ECHOED DISPATCH ENV" in t
    for var in ("MACHINE", "ACCELERATOR", "BENCH_EDGES", "CARD"):
        assert var in t, f"{var} is not echoed, so a discarded input cannot be caught"


# ---------------------------------------------------------------------------------------------------------
# admission, arithmetic and provenance
# ---------------------------------------------------------------------------------------------------------
_GOOD = ("BENCH_RESULT tag=l4_e11.29 status=OK atoms=141887 platform=CUDA device=NVIDIA_L4 steps=9000 "
         "dt_fs=4.0 wall_s=61.2 ns_per_day=95.10 sd=0.40 cv=0.0042 blocks=3 "
         "blocks_ns_day=94.7,95.1,95.5 attempt=1 minimize_iters=200 final_temp_k=299.8 healthy=True")


def test_a_result_line_round_trips():
    r = gcb.parse_result_line(_GOOD)
    assert r["status"] == "OK" and r["platform"] == "CUDA"
    assert r["atoms"] == 141887 and r["ns_per_day"] == pytest.approx(95.10)
    ok, why = gcb.admit(r)
    assert ok, why


@pytest.mark.parametrize("mutation,expect", [
    ("status=OK", "status=SUSPECT"),          # physics check failed -> a diverged system is FAST and fake
    ("platform=CUDA", "platform=CPU"),        # a CPU fallback prices a stack we do not run
    ("cv=0.0042", "cv=0.2100"),               # block scatter -> not a steady-state rate
])
def test_an_untrustworthy_measurement_is_refused_not_averaged_in(mutation, expect):
    ok, why = gcb.admit(gcb.parse_result_line(_GOOD.replace(mutation, expect)))
    assert not ok and why


def test_science_per_dollar_is_speed_over_rate_and_usd_per_ns_is_its_reciprocal():
    nsd, uph = 96.0, 0.5           # 4 ns/h at $0.50/h
    assert gcb.science_per_dollar(nsd, uph) == pytest.approx(8.0)
    assert gcb.usd_per_ns(nsd, uph) == pytest.approx(0.125)
    assert gcb.usd_per_ns(nsd, uph) == pytest.approx(1.0 / gcb.science_per_dollar(nsd, uph))


def test_machine_price_is_derived_from_components():
    """A bundled per-machine number cannot be checked against a SKU; cores + RAM + GPU can."""
    cores, ram = gcb.MACHINE_SHAPE["n1-standard-4"]
    p = gcb.LIST_PRICE_USD_PER_H
    assert gcb.machine_usd_per_h("p100") == pytest.approx(
        cores * p["n1_core"] + ram * p["n1_ram_gb"] + p["gpu_p100"])


def test_a_catalog_price_overrides_the_typed_list_rate():
    base = gcb.machine_usd_per_h("t4")
    bumped = gcb.machine_usd_per_h("t4", {"gpu_t4": gcb.LIST_PRICE_USD_PER_H["gpu_t4"] + 1.0})
    assert bumped == pytest.approx(base + 1.0), "the measured price is not actually used"


def test_ambiguous_skus_yield_no_price_rather_than_a_guess():
    skus = [
        {"description": "Nvidia Tesla T4 GPU running in Americas", "serviceRegions": ["us-central1"],
         "category": {"usageType": "OnDemand"},
         "pricingInfo": [{"pricingExpression": {"tieredRates": [{"unitPrice": {"units": "0", "nanos": 350000000}}]}}]},
        {"description": "Nvidia Tesla T4 GPU running in Americas", "serviceRegions": ["us-central1"],
         "category": {"usageType": "OnDemand"},
         "pricingInfo": [{"pricingExpression": {"tieredRates": [{"unitPrice": {"units": "1", "nanos": 0}}]}}]},
    ]
    prices, notes = gcb.parse_skus(skus)
    assert "gpu_t4" not in prices, "two prices for one component must not silently pick one"
    assert any("AMBIGUOUS" in n for n in notes)


def test_a_single_sku_is_read_as_units_plus_nanos():
    skus = [{"description": "Nvidia Tesla P100 GPU running in Americas", "serviceRegions": ["us-central1"],
             "category": {"usageType": "OnDemand"},
             "pricingInfo": [{"pricingExpression": {"tieredRates": [
                 {"unitPrice": {"units": "1", "nanos": 460000000}}]}}]}]
    prices, _ = gcb.parse_skus(skus)
    assert prices["gpu_p100"] == pytest.approx(1.46)


def test_the_list_prices_are_labelled_as_list_prices():
    """The one input here that is not measured must say so wherever it is read."""
    assert "NOT a measured invoice" in gcb.LIST_PRICE_SOURCE
    src = pathlib.Path(gcb.__file__).read_text()
    assert "LIST RATES, NOT AN INVOICE" in src


def test_the_ratio_table_omits_an_unmeasured_card_rather_than_estimating_it():
    doc = {"measurements": [
        {**gcb.parse_result_line(_GOOD), "card": "l4", "edge_nm": gcb.TERNARY_EDGE_NM},
        {**gcb.parse_result_line(_GOOD.replace("ns_per_day=95.10", "ns_per_day=190.20")
                                 .replace("device=NVIDIA_L4", "device=Tesla_P100")),
         "card": "p100", "edge_nm": gcb.TERNARY_EDGE_NM},
    ]}
    rows = gcb.ratio_table(doc, gcb.TERNARY_EDGE_NM)
    assert {r["card"] for r in rows} == {"l4", "p100"}, "an unmeasured card must be ABSENT, not guessed"
    p100 = next(r for r in rows if r["card"] == "p100")
    assert p100["x_reference"] == pytest.approx(2.0)


def test_the_artifact_if_present_is_readable_and_self_consistent():
    """Guards the committed measurement against a hand-edit: every admitted row must still pass `admit`."""
    p = pathlib.Path(gcb.RESULT_PATH)
    if not p.is_file():
        pytest.skip("no measurement recorded yet")
    doc = json.loads(p.read_text())
    for m in doc.get("measurements", []):
        if m.get("admitted"):
            ok, why = gcb.admit(m)
            assert ok, f"{m.get('card')} @ {m.get('edge_nm')} is marked admitted but fails admit(): {why}"
            assert m.get("card") in gcb.CARDS
