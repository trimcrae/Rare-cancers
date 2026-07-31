"""The per-arm checkpoint cadence — and the guard against it being tidied back into one shared value.

★★ WHAT THIS PINS, AND WHY IT IS NOT A STYLE TEST. Host churn is the dominant cost of wall-clock on this
lane, and the warmup checkpoint interval is the single lever that decides how much work each churn event
destroys. What a reclaim costs is

    EXPOSURE = warmup_ckpt_iters x seconds_per_iteration          [SECONDS, not iterations]

and `seconds_per_iteration` is a property of the ARM (how big the solvated system is) while
`warmup_ckpt_iters` was a property of the MODE. A single shared iteration count therefore CANNOT express
"the same exposure" for two arms that sample at different rates — it silently buys the slower arm a longer
unprotected runway — and the natural-looking cleanup, giving both arms one number again, reinstates exactly
that. That is what these tests exist to stop.

★ THE LANE'S OWN NUMBERS (`ternary-reps-diag.json`, 2026-07-28). Both arms churn on the same market; at the
shared interval of 64 the binary legs banked ~105 and ~250 iterations per archived attempt and finished
their legs, while the ternary legs banked ~32 and ~64 — r1 taking 26 attempts to reach 13 commits, i.e. its
AVERAGE ATTEMPT DID NOT REACH ONE CHECKPOINT BOUNDARY. Same churn, different cost per churn event.

⛔ WHAT IS **NOT** CLAIMED HERE, because CLAUDE.md §4 forbids dressing a hypothesis as a diagnosis: the
ternary units' leg records read `status=failed`, and nothing in this file explains why. Exposure is one
lever — the one that decides what each reclaim costs — and equalising it is worth doing on its own measured
terms. No test here asserts it is the cause of anything.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402

TERNARY = "calib_hi_to_lo__ternary_vhl"
BINARY = "calib_hi_to_lo__binary_vhl"
MODE = "edge_reps"


def _dt(mode=MODE):
    return tv.resolve_timesteps(mode)


# -------------------------------------------------------------------------------------------------------
# the measured basis — it must exist, be real, and be honest about what it may be compared with
# -------------------------------------------------------------------------------------------------------
def test_the_rates_are_measured_and_not_typed_into_the_launcher():
    """★ THE PROVENANCE TEST. The whole derivation stands on a MEASURED seconds-per-iteration, and a measured
    number typed into a source file is one nobody re-derives when the fleet moves to a different card. The
    rates therefore live in a regenerable artifact with one home, and the launcher reads it."""
    assert os.path.exists(tv._ARM_RATES_PATH), (
        "ternary-arm-iteration-rates.json is missing — regenerate it with "
        "`python research/modalities/ternary_arm_rates.py --out <path>` (CI: task=reps-diag)")
    doc = json.load(open(tv._ARM_RATES_PATH))
    assert doc.get("legs"), "the artifact records no legs — it was not built from real leg records"
    for row in doc["legs"]:
        assert row.get("unit_id") and row.get("arm"), row
        assert (row.get("production_median_s_per_iter") or row.get("warmup_median_s_per_iter")), (
            f"{row['unit_id']} is in the artifact with no measured rate at all")
    src = open(os.path.join(os.path.dirname(tv._ARM_RATES_PATH), "ternary_vast_launch.py")).read()
    assert "ARM_MEASURED_S_PER_ITER" not in src, (
        "a hand-typed per-arm rate table is back in the launcher — the rates have one home, and it is the "
        "artifact `ternary_arm_rates.py` regenerates from the legs' own timing blocks")


def test_rates_are_never_pooled_across_the_production_timestep():
    """⚠ AN ITERATION IS NOT A FIXED AMOUNT OF WORK. `n_steps = time_per_iteration / dt`, so a 2 fs iteration
    is 1250 MD steps and a 4 fs one is 625 — the same physics at ~2x the seconds
    (`ternary-4fs-vast-findings.md` §1/§2, whose closing line is "iterations are not comparable across
    protocols"). Pooling the two would make a slow arm out of a slow TIMESTEP, and the cadence derived from
    it would be wrong by a factor of two."""
    doc = json.load(open(tv._ARM_RATES_PATH))
    for dt, arms in doc["rates"].items():
        float(dt)  # the key IS the timestep, not a label
        for arm, agg in arms.items():
            for uid in agg["units"]:
                row = next(r for r in doc["legs"] if r["unit_id"] == uid)
                assert f"{float(row['timestep_fs']):.1f}" == dt, (
                    f"{uid} ran at {row['timestep_fs']} fs and was aggregated under dt={dt}")
                assert row["arm"] == arm


def test_the_arm_ratio_is_not_secretly_a_CARD_ratio():
    """★★ THE CONFOUND THAT WOULD MAKE THE WHOLE DERIVATION WRONG, and the one this repo has already been
    caught by from the other direction (pricing.md's superseded ~2.06x L4→4090 ratio). This lane rents a
    MIXED fleet — 4080 SUPER, 4090 and 5090 all appear in the artifact — so if one arm happened to be
    measured on faster silicon than the other, the "arm ratio" driving the cadence would be partly a card
    ratio and the derived interval would be wrong for every host that is not that card.

    The check: recompute the ratio using ONLY the card both arms were measured on, and require it to agree
    with the mixed-fleet ratio. If a future re-measurement lands the two arms on disjoint hardware this test
    says so instead of letting a card difference masquerade as a system difference.
    """
    doc = json.load(open(tv._ARM_RATES_PATH))
    dt, _ = _dt()
    arms = doc["rates"][f"{float(dt):.1f}"]
    t, b = arms["ternary"], arms[tv.CKPT_REFERENCE_ARM]
    shared = set(t["by_gpu"]) & set(b["by_gpu"])
    assert shared, (f"the two arms share no GPU model — ternary on {sorted(t['by_gpu'])}, "
                    f"{tv.CKPT_REFERENCE_ARM} on {sorted(b['by_gpu'])}; the ratio cannot be separated from "
                    f"the card")
    mixed = t["s_per_iter"] / b["s_per_iter"]
    for g in shared:
        same_card = t["by_gpu"][g] / b["by_gpu"][g]
        assert same_card == pytest.approx(mixed, rel=0.25), (
            f"on {g} alone the arms differ by {same_card:.2f}x but the mixed-fleet estimate is "
            f"{mixed:.2f}x — the fleet's card mix is doing the work, not the systems")


def test_using_a_production_median_as_the_warmup_rate_errs_toward_LESS_work_at_risk():
    """The one cross-phase step the artifact takes, checked rather than assumed. The structural argument is
    that a warmup iteration and a production iteration are the same `n_steps` (`rbfe_spot_driver` overrides
    only `.timestep` on a move whose step count was fixed at the production dt), so the substitution should
    be ~neutral. Measured, warmup comes in at or below production on every leg that recorded both — so a
    production median OVERSTATES the seconds a warmup iteration costs, and the derived interval is finer
    than strictly needed. Wrong in the safe direction, and stated so nobody has to re-derive which direction
    that is."""
    x = json.load(open(tv._ARM_RATES_PATH))["phase_cross_check"]
    assert x["n"] >= 3, "too few legs measured both phases to make this claim"
    assert x["median_warmup_over_production"] <= 1.05, (
        f"warmup is running {x['median_warmup_over_production']:.2f}x production — a production median now "
        f"UNDERSTATES the warmup seconds at risk, and the derivation should switch to warmup medians")


def test_the_aggregation_is_re_derivable_without_credentials():
    """§1: a derived number must be REGENERABLE, not just recorded. `--rebuild-from` re-aggregates the stored
    per-leg rows, so the step from measurements to rates can be re-run and re-checked by anyone."""
    import ternary_arm_rates as tar
    doc = json.load(open(tv._ARM_RATES_PATH))
    rebuilt = tar.build(rows=doc["legs"], n_records=doc["n_leg_records"])
    assert rebuilt["rates"] == doc["rates"], "the artifact's rates are not what its own rows produce"
    assert rebuilt["phase_cross_check"]["per_unit"] == doc["phase_cross_check"]["per_unit"]


def test_a_timestep_with_no_measurement_falls_back_rather_than_guessing():
    """An unmeasured timestep must return {} — today's flat behaviour — not an extrapolated rate. Inventing
    one would silently re-cadence a lane nobody measured, which is the failure this file is about."""
    assert tv.arm_iteration_rates(7.5) == {}


# -------------------------------------------------------------------------------------------------------
# the derivation itself
# -------------------------------------------------------------------------------------------------------
def test_the_arms_of_edge_reps_do_not_share_a_checkpoint_interval():
    """The state the lane was in: both arms on one number."""
    t = tv.warmup_ckpt_iters_for(TERNARY, MODE)
    b = tv.warmup_ckpt_iters_for(BINARY, MODE)
    assert t != b, "the ternary and binary arms are back on one interval"
    assert int(t) < int(b), "the SLOWER arm needs the FINER interval, not the coarser one"


def test_the_ternary_arms_exposure_is_inside_the_binary_arms_proven_exposure():
    """★★ THE INVARIANT THE WHOLE CHANGE EXISTS TO SATISFY, stated in the units that matter: SECONDS of
    sampling at risk from a host reclaim, not iterations. The binary arm's figure is the proven one — it is
    the arm that demonstrably banks progress on these hosts (`ternary-reps-diag.json`)."""
    t = tv.ckpt_exposure_s(TERNARY, MODE)
    b = tv.ckpt_exposure_s(BINARY, MODE)
    assert t is not None and b is not None, "an arm has no measured rate — see the artifact"
    assert t <= b, f"ternary exposure {t:.0f}s exceeds the binary arm's proven {b:.0f}s"
    # ...and not absurdly under it either, or we pay commit overhead for nothing. The derivation takes the
    # LARGEST interval that fits, so the result is within one interval-step of the budget.
    assert t > b / 4, f"ternary exposure {t:.0f}s is far under the {b:.0f}s budget — over-committing"


def test_every_derived_interval_divides_the_warmup_target_exactly():
    """⚠ A PROTOCOL GUARD, NOT AN ARITHMETIC ONE. `rbfe_spot_driver` rounds each phase's target DOWN to a
    multiple of the interval (`warmup_target = (warmup_iters // wci) * wci`), so an interval that did not
    divide the target would SHORTEN this leg's equilibration relative to r0's — a protocol difference inside
    a matched cycle, which is precisely the class of error the closure triangle's 2 fs pinning exists to
    prevent."""
    dt, wdt = _dt()
    target = tv.warmup_target_iters(dt, wdt)
    for leg in (TERNARY, BINARY):
        ci = int(tv.warmup_ckpt_iters_for(leg, MODE))
        assert target % ci == 0, f"{leg}: interval {ci} does not divide the {target}-iteration warmup"
        assert (target // ci) * ci == target


def test_the_warmup_target_is_derived_from_BOTH_timesteps_not_a_constant():
    """1600 is arithmetic, not folklore — and it is arithmetic that CHANGES with the protocol, which is why
    it cannot be a module constant. `rbfe_spot_driver` takes the equilibration length at the WARMUP timestep
    but the PRODUCTION integrator's steps-per-iteration:

        1.0 ns / 1.0 fs warmup dt                      = 1e6 steps
        2.5 ps time_per_iteration / 4.0 fs prod dt      = 625 steps per iteration  -> 1600
        2.5 ps time_per_iteration / 2.0 fs prod dt      = 1250 steps per iteration ->  800

    The 2 fs row is not hypothetical: `MODES["triangle"]` pins 2 fs, so a hardcoded 1600 would have asserted
    divisibility against a target that lane never runs."""
    assert tv.warmup_target_iters(4.0, 1.0) == 1600
    assert tv.warmup_target_iters(2.0, 1.0) == 800
    equilibration_ns, warmup_dt_fs, time_per_iter_ps, prod_dt_fs = 1.0, 1.0, 2.5, 4.0
    steps = equilibration_ns * 1e6 / warmup_dt_fs
    steps_per_iter = time_per_iter_ps * 1000.0 / prod_dt_fs
    assert int(steps / steps_per_iter) == tv.warmup_target_iters(prod_dt_fs, warmup_dt_fs)


def test_the_protocol_lengths_are_imported_from_the_engine_not_retyped():
    """ONE FACT, ONE PLACE (CLAUDE.md §1). `EQUILIBRATION_NS` belongs to the engine; if the launcher carried
    its own copy the two could disagree and the divisibility guard above would be checking the wrong target.
    """
    import nr4a3_ternary_fep as tfep
    assert tfep.EQUILIBRATION_NS == 1.0
    src = open(os.path.join(os.path.dirname(tv._ARM_RATES_PATH), "ternary_vast_launch.py")).read()
    assert "EQUILIBRATION_NS" not in src.split("def warmup_target_iters")[0], \
        "the launcher defines its own equilibration length above the derivation — that is a second home"


def test_only_a_mode_that_opts_in_gets_a_per_arm_interval():
    """Scoped, so this cannot silently re-cadence a lane nobody measured. `edge` (seed 0, the legs that are
    already DONE), `5aks` and the triangle must be byte-identical to what they ran with."""
    for mode in tv.MODES:
        if tv.MODES[mode].get("per_arm_ckpt"):
            continue
        for (leg, _s, _d) in tv.units_for(mode):
            assert tv.warmup_ckpt_iters_for(leg, mode) == str(tv.MODES[mode]["warmup_ckpt_iters"]), \
                f"{mode}/{leg} must keep the mode's own interval — it did not opt in"


def test_the_reference_arm_itself_is_never_re_cadenced():
    """The budget is the reference arm's own exposure, so moving the reference arm would move the budget it
    is measured against — a self-referential change nobody could grade."""
    assert tv.warmup_ckpt_iters_for(BINARY, MODE) == str(tv.MODES[MODE]["warmup_ckpt_iters"])


def test_the_derivation_only_ever_refines_never_coarsens():
    """A fast arm (solvent, ~1/7th the ternary rate) could 'equalise' UPWARD to a much coarser interval. It
    must not: the mode's own value is the coarsest cadence that was ever authorised, and buying extra
    exposure on an arm that is not failing is not what this change is for."""
    ref = int(tv.MODES[MODE]["warmup_ckpt_iters"])
    for leg in (TERNARY, BINARY, "calib_hi_to_lo__solvent"):
        assert int(tv.warmup_ckpt_iters_for(leg, MODE)) <= ref


# -------------------------------------------------------------------------------------------------------
# the other half of the trade-off: commit overhead
# -------------------------------------------------------------------------------------------------------
def test_the_interval_never_gets_small_enough_for_commit_overhead_to_dominate():
    """★ THE REAL TRADE-OFF, WITH NUMBERS. A commit is one reporter sync plus an ~25 MB .nc/.chk pair copied
    and PUT to S3, MEASURED at ~23 s (`ternary-4fs-vast-findings.md` §4: pure MD ~8.5 s/iter against 11.4
    s/iter commit-inclusive at ci=8, so (11.4-8.5)x8 ~= 23 s). Since overhead is fixed per commit and the MD
    between commits is the exposure, the fraction of wall-clock spent committing is

        COMMIT_OVERHEAD_S / EXPOSURE_S

    — which is why refining an interval is not free, and why 'just checkpoint every iteration' is wrong. The
    tolerance is not new: it is the one this lane already chose `edge`'s ci=64 with ("at the edge's ci=64 it
    is ~0.4 s/iter, under 5 %", same section)."""
    for (leg, _s, _d) in tv.units_for(MODE):
        f = tv.ckpt_overhead_fraction(leg, MODE)
        assert f is not None, f"{leg} has no measured rate"
        assert f <= tv.MAX_COMMIT_OVERHEAD_FRAC, (
            f"{leg} would spend {f:.1%} of its warmup committing, over the "
            f"{tv.MAX_COMMIT_OVERHEAD_FRAC:.0%} this lane accepts — the reference arm's interval is too "
            f"small to give the slower arm a workable budget; that is a decision, not a clamp")


def test_the_overhead_fraction_is_exactly_the_ratio_it_claims_to_be():
    """The relation the argument above rests on, asserted rather than asserted-in-prose."""
    for leg in (TERNARY, BINARY):
        assert tv.ckpt_overhead_fraction(leg, MODE) == pytest.approx(
            tv.COMMIT_OVERHEAD_S / tv.ckpt_exposure_s(leg, MODE))


# -------------------------------------------------------------------------------------------------------
# the wiring
# -------------------------------------------------------------------------------------------------------
def test_the_jobspec_actually_carries_the_per_arm_value():
    """The derivation is worthless if `build_jobspec` still reads the mode's flat value."""
    got = {}
    for (leg, seed, direction) in tv.units_for(MODE):
        j = tv.build_jobspec(leg, seed, direction, mode=MODE)
        got.setdefault(tv.arm_of_leg(leg), set()).add(j.env["WARMUP_CKPT_ITERS"])
    assert got["binary"] == {str(tv.MODES[MODE]["warmup_ckpt_iters"])}, got
    assert got["ternary"] == {tv.warmup_ckpt_iters_for(TERNARY, MODE)}, got
    assert got["ternary"] != got["binary"], got


def test_the_jobspec_uses_the_timestep_it_was_actually_resolved_at():
    """⚠ THE SAME TRAP `build_jobspec` already documents for the template label. The workflow exports
    `TVAST_TIMESTEP_FS` lane-wide, so a cadence derived at the MODE's default while the SPEC ran at an
    override would be a cadence for a different protocol: at 2 fs an iteration is 1250 MD steps rather than
    625 and the warmup target is 800 rather than 1600, so both inputs to the derivation change.

    ★★ THIS TEST ASSERTED A VALUE AND THE VALUE WENT RED ON 2026-07-31 — and the value was the wrong thing
    to assert, in a way worth recording rather than quietly patching.

    It used to end `assert WARMUP_CKPT_ITERS == str(MODES[MODE]["warmup_ckpt_iters"])`, i.e. **64**, on the
    stated discriminator that *"the 2 fs table has no measured `binary` rate, so the derivation correctly
    declines and returns the flat value"*. That absence was TRANSIENT DATA: the valB closure triangle's two
    2 fs BINARY legs landed, `ternary_arm_rates` measured them, and the reference arm the derivation needs
    now exists at 2 fs. So the derivation legitimately stopped declining — `TESTING.md` rule 7's
    population-assertion-on-a-data-driven-derivation, exactly.

    ⚠ AND THE OLD EXPECTATION WAS NOT MERELY STALE, IT WAS INVALID AT 2 fs. `warmup_target_iters(2.0, 1.0)`
    is **800**, and 800 / 64 = 12.5 — the flat interval does not divide the 2 fs warmup target, so a leg that
    really ran at 64 here would sit off-grid, which is the 2026-07-21 `resume iteration 520 != expected 540`
    class of defect. The derived 50 divides 800 exactly (16 commits). The test was pinning a number that
    would have been a bug.

    PROVENANCE WAS CHECKED BEFORE THE TEST WAS TOUCHED, because the alternative hypothesis was serious: that
    the derivation had started feeding on today's **4 fs** 5a-KS leg records. It has not. Every unit behind
    the 2 fs table is `…_dt2.0fs_…` and every unit behind the 4 fs table is `…_dt4.0fs_…`, and that is
    structural rather than lucky — `arm_iteration_rates` looks the table up by the hard key
    `f"{float(timestep_fs):.1f}"`, so a 4 fs record cannot reach a 2 fs derivation. The check is now an
    assertion of its own, below, so the question is answered by CI rather than by a person re-deriving it.

    So this asserts the PROPERTY: the cadence was derived at the timestep the spec actually runs, it divides
    THAT timestep's warmup target, and it is not the 4 fs answer."""
    j = tv.build_jobspec(TERNARY, 1, "fwd", mode=MODE, timestep_fs="2.0", warmup_timestep_fs="1.0")
    assert j.env["RBFE_TIMESTEP_FS"] == "2.0"
    got = int(j.env["WARMUP_CKPT_ITERS"])

    # 1. It is the answer THIS timestep's table gives, recomputed independently of build_jobspec.
    assert got == int(tv.warmup_ckpt_iters_for(TERNARY, MODE, timestep_fs="2.0", warmup_timestep_fs="1.0"))

    # 2. It is ON THE 2 fs GRID. The original defect this whole file guards is an interval that does not
    #    divide the warmup target, which makes a leg unresumable.
    target_2fs = tv.warmup_target_iters(2.0, 1.0)
    assert target_2fs and target_2fs % got == 0, (
        f"interval {got} does not divide the 2 fs warmup target {target_2fs} — off-grid, unresumable")

    # 3. It is NOT the 4 fs answer, which is the actual failure mode: a spec cadenced off the wrong table.
    assert got != int(tv.warmup_ckpt_iters_for(TERNARY, MODE)), \
        "the 2 fs spec was cadenced off the 4 fs rate table"


def test_no_rate_table_is_fed_by_a_leg_that_ran_at_a_DIFFERENT_timestep():
    """THE PROVENANCE CHECK, asserted rather than re-derived by hand each time it is doubted.

    The hazard is specific and expensive: at 2 fs an iteration is 1250 MD steps rather than 625 and the
    warmup target is 800 rather than 1600, so a rate measured at one timestep applied to the other yields a
    cadence for a protocol that is not running. `ternary_arm_rates` keys the table by timestep and the
    lookup is a hard key, but the table is DATA — it is regenerated from whatever leg records exist — so the
    invariant belongs in CI rather than in a comment.
    """
    import json as _json
    import pathlib as _pl
    p = _pl.Path(tv.__file__).with_name("ternary-arm-iteration-rates.json")
    if not p.exists():                       # the fallback path is "no per-arm cadence at all", not a wrong one
        pytest.skip("no measured arm-rate table committed")
    doc = _json.loads(p.read_text())
    for dt, arms in (doc.get("rates") or {}).items():
        for arm, v in arms.items():
            for unit in v.get("units") or []:
                assert f"_dt{dt}fs_" in unit, (
                    f"the {dt} fs / {arm} rate is fed by {unit!r}, which did NOT run at {dt} fs — a cadence "
                    f"derived from it would be a cadence for a different protocol")


# -------------------------------------------------------------------------------------------------------
# a finding this work turned up, pinned rather than quietly fixed
# -------------------------------------------------------------------------------------------------------
KNOWN_DIVISIBILITY_GAP = {"triangle"}


def test_no_mode_silently_shortens_its_own_equilibration_except_the_one_already_known_to():
    """★★ A DEFECT THIS CHANGE FOUND AND DELIBERATELY DID **NOT** FIX IN FLIGHT (2026-07-28).

    `rbfe_spot_driver` sets `warmup_target = (warmup_iters // wci) * wci`, so a mode whose interval does not
    DIVIDE its derived warmup target silently runs a SHORTER equilibration than the protocol asks for. At
    4 fs the target is 1600 = 2^6 x 25 and every interval in `MODES` divides it. At 2 fs it is 800 = 2^5 x 25,
    which **64 does not divide**: `MODES["triangle"]` runs 768 of its 800 warmup iterations, 4 % short.

    That is decision-relevant to the closure triangle rather than cosmetic. T1 IS r0, and r0 ran on the GCP
    lane with `RBFE_WARMUP_CKPT_ITERS=8` (`gpu-ternary-fep-gcp.yml`), which divides 800 exactly — so r0
    equilibrated 800 and T2/T3 equilibrate 768. The triangle mode's own comment is the argument for why that
    matters: "anything that makes T2/T3's protocol differ from T1's converts R from a path-error detector
    into a protocol-difference detector."

    ⛔ WHY IT IS LEFT ALONE HERE, AND WHY THAT IS NOT TIMIDITY. Those legs are billing now. On a resume the
    interval baked into the committed .nc OVERRIDES the environment (the driver's single-interval invariant),
    so re-cadencing the mode today would leave the already-started legs on 64 -> 768 and give any fresh leg
    50 -> 800: a protocol difference WITHIN the triangle, which is strictly worse than the uniform one it
    has. The fix belongs to that lane, between rounds. Recorded here so it cannot be lost, and asserted so
    that a NEW mode acquiring the same gap fails immediately instead of quietly shortening its equilibration.
    """
    offenders = set()
    for mode, sizing in tv.MODES.items():
        if sizing["warmup_iters"]:          # an explicit short warmup, not the derived science length
            continue
        dt, wdt = tv.resolve_timesteps(mode)
        target = tv.warmup_target_iters(dt, wdt)
        for leg, _s, _d in tv.units_for(mode):
            if target % int(tv.warmup_ckpt_iters_for(leg, mode)) != 0:
                offenders.add(mode)
    assert offenders == KNOWN_DIVISIBILITY_GAP, (
        f"divisibility gaps changed: {offenders}, expected {KNOWN_DIVISIBILITY_GAP}. A mode in this set runs "
        f"a SHORTER equilibration than its protocol specifies — see this test's note before editing it.")


def test_an_explicit_env_override_still_wins():
    """The escape hatch has to keep working — it is how a one-off re-cadence is done without editing MODES."""
    os.environ["TVAST_WARMUP_CKPT_ITERS"] = "8"
    try:
        j = tv.build_jobspec(TERNARY, 1, "fwd", mode=MODE)
        assert j.env["WARMUP_CKPT_ITERS"] == "8"
    finally:
        del os.environ["TVAST_WARMUP_CKPT_ITERS"]


def test_the_measured_rates_carry_every_arm_the_opted_in_lane_runs():
    """A missing arm falls back to the reference interval SILENTLY, which is the failure this whole file is
    about — so it must be impossible to add a leg type to an opted-in mode without noticing."""
    for mode, sizing in tv.MODES.items():
        if not sizing.get("per_arm_ckpt"):
            continue
        dt, _ = tv.resolve_timesteps(mode)
        rates = tv.arm_iteration_rates(dt)
        missing = {tv.arm_of_leg(leg) for (leg, _s, _d) in tv.units_for(mode)} - set(rates)
        assert not missing, (f"{mode}: no measured s/iter at {dt} fs for {missing} — those legs would "
                             f"silently inherit the reference cadence")


@pytest.mark.parametrize("factor,expect_finer", [(1.0, False), (4.0, True), (0.5, False)])
def test_the_interval_re_derives_when_a_rate_is_re_measured(monkeypatch, factor, expect_finer):
    """★ THE POINT OF DERIVING RATHER THAN TYPING: re-measure an arm and the cadence follows, with nobody
    having to remember to re-tune a constant. Scaled off the arm's OWN measured rate so this test does not
    become a second home for the number."""
    dt, _ = _dt()
    base = dict(tv.arm_iteration_rates(dt))
    ref_rate = base[tv.CKPT_REFERENCE_ARM]
    faked = dict(base, ternary=ref_rate * factor)
    monkeypatch.setattr(tv, "arm_iteration_rates", lambda _dt, path=None: faked)
    ci = int(tv.warmup_ckpt_iters_for(TERNARY, MODE))
    ref = int(tv.MODES[MODE]["warmup_ckpt_iters"])
    assert (ci < ref) is expect_finer
    assert ci * faked["ternary"] <= ref * ref_rate, "the derived interval broke the exposure budget"


def test_arm_of_leg_covers_every_leg_id_the_lane_can_launch():
    """One home for the arm split; a leg that fell through to a wrong arm would be given the wrong cadence
    with nothing printed."""
    seen = {tv.arm_of_leg(leg) for mode in tv.MODES for (leg, _s, _d) in tv.units_for(mode)}
    assert seen <= {"ternary", "binary", "solvent"}
    assert tv.arm_of_leg("calib_hi_to_lo__solvent") == "solvent"
    assert tv.arm_of_leg("5aks_d0_to_d__ternary_nr4a3") == "ternary"
    assert tv.arm_of_leg("calib_lo_to_lo2__binary_vhl") == "binary"


def test_the_derivation_survives_a_stdlib_only_runner():
    """★★ THE SILENT-DISABLE RISK, AND WHY IT IS WORTH ITS OWN TEST. `warmup_target_iters` imports the engine
    for `EQUILIBRATION_NS` (one home) and, if that import fails, WARNs and falls back to the mode's flat
    value. That fallback is correct behaviour and a terrible failure mode: the job that actually rents hosts
    is a plain `ubuntu-latest` runner with `setup-python` and `pip install boto3` — no rdkit, no numpy, no
    OpenMM — so if any module on the import chain grew a heavy top-level dependency, the per-arm cadence
    would switch itself off *in the only place it matters* and the launch would still be green.

    So: block the heavy packages outright and require the derivation to still produce its per-arm answer.
    """
    import importlib
    import subprocess
    src = (
        "import sys\n"
        "blocked = {'rdkit','numpy','scipy','openmm','openfe','pandas','matplotlib','boto3','mdtraj'}\n"
        "class B:\n"
        "    def find_module(self, name, path=None):\n"
        "        return self if name.split('.')[0] in blocked else None\n"
        "    def load_module(self, name):\n"
        "        raise ImportError('blocked ' + name)\n"
        "sys.meta_path.insert(0, B())\n"
        f"sys.path.insert(0, {os.path.dirname(tv._ARM_RATES_PATH)!r})\n"
        "import ternary_vast_launch as t\n"
        f"print(t.warmup_target_iters(4.0, 1.0), t.warmup_ckpt_iters_for({TERNARY!r}, {MODE!r}))\n"
    )
    out = subprocess.run([sys.executable, "-c", src], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
    target, ci = out.stdout.split()
    assert target == "1600", f"the warmup target could not be derived without heavy deps: {out.stdout!r}"
    assert ci == tv.warmup_ckpt_iters_for(TERNARY, MODE) != str(tv.MODES[MODE]["warmup_ckpt_iters"]), (
        f"the per-arm cadence silently fell back to the flat value on a stdlib-only runner (got {ci}) — "
        f"that is the environment the launch job runs in")
    assert importlib  # keep the import meaningful to linters


def test_the_helpers_are_pure_and_rent_nothing():
    """This runs inside `build_jobspec`, on the path to a rental. It must not reach the network, and it must
    certainly never touch an instance."""
    import ast
    src = open(os.path.join(os.path.dirname(tv._ARM_RATES_PATH), "ternary_vast_launch.py")).read()
    tree = ast.parse(src)
    wanted = {"arm_of_leg", "warmup_target_iters", "warmup_ckpt_iters_for", "ckpt_exposure_s",
              "ckpt_overhead_fraction", "_divisors_up_to"}
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            found.add(node.name)
            body = ast.dump(node)
            for banned in ("_vast_request", "boto3", "_s3", "DELETE"):
                assert banned not in body, f"{node.name} reaches for {banned}"
    assert found == wanted, f"missing {wanted - found}"
