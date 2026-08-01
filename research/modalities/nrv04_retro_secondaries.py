#!/usr/bin/env python3
"""
NR-V04 retrospective — the PREREGISTERED SECONDARY ENDPOINTS E2, E3 and E4, reported from the landed panel.

★★ WHY THIS EXISTS. Prereg §3 says, of E2–E4: *"reported alongside it in every result, including when they
disagree with E1."* They never were. The criteria audit
([`nrv04-retro-criteria-audit.json`](./nrv04-retro-criteria-audit.json) → `criterion_by_criterion`) recorded
that in as many words — *"prereg §3's promise that E2-E4 are 'reported alongside it in every result' is
unimplemented in the verdict output"* — and it stayed unimplemented after the panel completed 16/16 and the
frozen gate emitted **DISCORDANT**. This module is that promise, kept. It is owed regardless of how the
secondaries came out, and it was written without looking at them first.

⛔ **REPORT ONLY. NOTHING HERE IS PROMOTED.** No value computed in this module may become a verdict, a tier
condition, or a substitute primary. **E1 is the registered primary and the only endpoint the verdict turns
on.** If a secondary looks better-behaved than E1 — cleaner separation, a friendlier ordering, a smaller
spread — that is a fact to state and explicitly *not* act on: **gating on the friendliest endpoint is
precisely the retune this program forbids.** The module therefore computes no p-value on E2, E3 or E4, offers
no tier, and imports `nrv04_retro_gate` only for its FROZEN constants and for the pure re-derivations in
§`frozen_scorer_probes`, which re-run the primary rule unchanged rather than proposing a new one.

★★ IT RESTS ON WHAT IS STORED, NOT ON WHAT A COLLECTOR BELIEVED (CLAUDE.md §4b). `retro_collect` maps each
leg into a compact record and the verdict readout deliberately does NOT carry those records (`_CARRY` omits
`legs`). So the secondaries are read back from the leg JSONs THEMSELVES, under the lane's S3 prefix, and each
one is graded on the fields **only a real run can produce** — measured wall time, the readout kernel's own
frame count, the trajectory writer's receipt — never on a field a default could fill:

    MEASURED (a run had to happen)     n_frames · timed_ns · prod_wall_s · ns_per_day · R2_recruitment.frames
                                       · analysis_traj.written_frames · pe_pre_min_kj / pe_post_min_kj
    ECHOED FROM ENV (a default fills)  mode · prod_ns · equil_ns · LEG_ID · SEED

That split is the whole point. 17 smoke legs once echoed `prod_ns: 5.0` and a fully-populated `R1_interface`
from their ENV and drove `panel_complete` true (see `nrv04_retro_panel`'s "WHAT COUNTS AS A LANDED LEG"), so
a census that reads the echo and calls it provenance reproduces exactly that failure. Membership is decided
by the frozen `nrv04_retro_panel.production_leg_check` — imported, never re-spelled — and this module then
CORROBORATES each admitted leg against the measured columns and says so leg by leg.

The two `mode='smoke'` records already listed in the emitted verdict's `nonconforming_records` are excluded
here by the same predicate, and are reported as excluded rather than dropped silently (CLAUDE.md rule 1.2).

Read-only. Rents nothing, destroys nothing, writes nothing to S3. $0.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
PREFIX = os.environ.get("NRV04_RETRO_RESULT_PREFIX") or "nrv04-retro-results"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nrv04-retro-secondaries.json")
VERDICT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nrv04-retro-verdict.json")

#: The fields a real run had to produce, against the fields an ENV default can fill. ⚠ `mode` is on the
#: RIGHT-hand list even though `production_leg_check` keys on it: it is `env["MODE"]`, echoed. Membership
#: legitimately rests on it (a leg that ASKS for smoke gets smoke), but it is not *evidence* that 5 ns ran —
#: the measured columns are, and this module reports the two side by side so a disagreement is visible.
MEASURED_FIELDS = ("n_frames", "timed_ns", "prod_wall_s", "ns_per_day",
                   "pe_pre_min_kj", "pe_post_min_kj")
ENV_ECHOED_FIELDS = ("mode", "prod_ns", "equil_ns", "leg_id", "seed")

#: ⚠ AN ADMITTED GAP, STATED RATHER THAN PAPERED OVER (CLAUDE.md §4b). Equilibration leaves **no positive
#: receipt** in the leg record: `equil_ns` is an ENV echo, and the only equilibration-specific field the
#: driver writes is the NEGATIVE one — `blow_phase`, which names an `equil@<n>steps/<m>` chunk when the 4 fs
#: HMR integrator NaN'd during equilibration (`nrv04_covalent_md.run_leg`). There is also a *structural*
#: receipt: the minimization energies `pe_pre_min_kj` / `pe_post_min_kj` prove the system was built and
#: minimized, which is the step equilibration follows. That is as far as the artifacts go, and this module
#: says so rather than dressing an ENV echo as a verification.
EQUIL_EVIDENCE_NOTE = (
    "NO DIRECT RECEIPT: `equil_ns` is echoed from ENV and the driver writes no equilibration wall time or "
    "frame count. What the artifacts DO carry is (a) the minimization pair pe_pre_min_kj / pe_post_min_kj — "
    "a real built-and-minimized system — and (b) the only direct equilibration field, which is negative: "
    "`blow_phase` = 'equil@<n>steps/<m>' when the 4 fs HMR integrator NaN'd during equilibration. Reported "
    "as a gap, never as a verification.")

#: ⛔ WHY THE S3 WRITE SPAN IS REPORTED BUT NEVER GRADED (root-caused 2026-08-01 from the driver's source,
#: after this module's first pass flagged 9 of 16 legs on it). A unit's S3 span looks like a free wall-clock
#: check — first object written to last — and it is NOT one, in two independent ways, both of which shorten
#: it for a leg that finished CLEANLY:
#:   1. `nrv04_covalent_md._rm_ckpt` DELETES the checkpoint objects from S3 the moment a leg finishes
#:      ("leg finished -> drop the checkpoint"), so the earliest-written objects of a successful leg are gone
#:      before any census can list them;
#:   2. continuous upload (`s3_upload_mode="Continuous"`) OVERWRITES the same keys — traj blob, phase.txt,
#:      run.log — so each surviving object carries the mtime of its LAST write, not its first.
#: Measured consequence on this panel: 9 legs showed a span SHORTER than their own `prod_wall_s`, and every
#: one of the 9 was a 500-frame / 5.0 ns leg with a 500-frame trajectory receipt. Grading on the span would
#: therefore have condemned real legs — the exact "an absent reading is not a reading of absence" failure,
#: pointed the other way. The span is kept as REPORTED CONTEXT with this caveat attached; the corroboration
#: verdict rests only on fields the run itself wrote into the record.
S3_SPAN_NOTE = (
    "REPORTED, NOT GRADED. A unit's S3 write span is neither an upper nor a lower bound on the leg's wall "
    "clock: nrv04_covalent_md._rm_ckpt DELETES the checkpoint objects when a leg finishes, and continuous "
    "upload overwrites keys so each object carries its LAST write time. A clean leg can therefore show a "
    "span far shorter than its own measured prod_wall_s — 9 of the 16 landed legs do, all of them 500-frame "
    "5.0 ns legs. Corroboration is decided on the record's own measured fields instead.")


# =============================================================================================================
# the three secondary endpoints — PURE
# =============================================================================================================
def secondary_endpoints(legs):
    """E2, E3 and E4 from the landed legs, using the prereg §3 definitions EXACTLY as written. PURE.

    `legs`: iterable of dicts carrying at least {arm_id, cofold_model_seed, replica} plus the driver's own
    readout blocks under `R1_interface` / `R2_recruitment` / `R3_lys`. Only legs that already passed
    `nrv04_retro_panel.production_leg_check` may be handed in; this function does not re-filter, so the
    membership decision has exactly one home.

    ⛔ Returns numbers and definitions. No p-value, no tier, no threshold on E3 or E4 — see the module
    docstring. E2's 4.0 Å threshold is READ from the frozen scorer, never typed here.
    """
    import nrv04_retro_gate as gate

    rows = []
    for leg in legs:
        r1 = leg.get("R1_interface") or {}
        r2 = leg.get("R2_recruitment") or {}
        r3 = leg.get("R3_lys") or {}
        plateau = r1.get("plateau_A")
        rows.append({
            "arm_id": leg.get("arm_id"),
            "cofold_model_seed": leg.get("cofold_model_seed"),
            "replica": leg.get("replica"),
            "unit": leg.get("unit"),
            "e1_plateau_A": plateau,
            # E2 is a per-leg BINARY. Two spellings on purpose: the driver's own flag, and the flag
            # re-derived from the plateau against the frozen threshold. They must agree, and
            # `e2_threshold_agrees` says whether they do — a disagreement would mean the leg was scored
            # against a threshold other than the frozen 4.0 Å, which is the one thing that could silently
            # re-tune a preregistered endpoint.
            "e2_stable_recorded": r1.get("stable"),
            "e2_stable_rederived": None if plateau is None else bool(float(plateau) < gate.STABLE_PLATEAU_A),
            "e3_mean_contacts": r2.get("mean_contacts"),
            "e3_frames": r2.get("frames"),
            "e3_frac_frames_in_contact": r2.get("frac_frames_in_contact"),
            "e4_min_A": r3.get("min_A"),
            "e4_median_A": r3.get("median_A"),
            "e4_max_A": r3.get("max_A"),
            "e4_note": r3.get("note"),
        })
    for r in rows:
        r["e2_threshold_agrees"] = (r["e2_stable_recorded"] is None or
                                    r["e2_stable_recorded"] == r["e2_stable_rederived"])

    arms = sorted({r["arm_id"] for r in rows if r["arm_id"]})

    def _arm(a):
        return [r for r in rows if r["arm_id"] == a]

    def _mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 4) if xs else None

    def _by_model(a, field):
        """Model-level value = mean over that co-fold model's replicas (prereg §4a's unit of independence).
        Reported for E3 because §4a fixes the unit for every quantity, not just the primary — but NO test is
        run on it here."""
        out = {}
        for r in _arm(a):
            if r[field] is not None and r["cofold_model_seed"] is not None:
                out.setdefault(int(r["cofold_model_seed"]), []).append(float(r[field]))
        return {m: round(sum(v) / len(v), 4) for m, v in sorted(out.items())}

    e2 = {}
    for a in arms:
        rs = [r for r in _arm(a) if r["e2_stable_rederived"] is not None]
        n_stable = sum(1 for r in rs if r["e2_stable_rederived"])
        e2[a] = {"n_legs": len(rs), "n_stable": n_stable,
                 "stable_fraction": round(n_stable / len(rs), 4) if rs else None,
                 "per_leg_plateau_A": [r["e1_plateau_A"] for r in rs],
                 # model-level too, because §4a's unit of independence applies to every endpoint. NOT a test.
                 "model_level_stable_fraction": {
                     m: round(sum(1 for r in _arm(a)
                                  if r["cofold_model_seed"] == m and r["e2_stable_rederived"]) /
                              max(1, sum(1 for r in _arm(a) if r["cofold_model_seed"] == m)), 4)
                     for m in sorted({r["cofold_model_seed"] for r in _arm(a)
                                      if r["cofold_model_seed"] is not None})}}

    e3 = {}
    for a in arms:
        vals = [r["e3_mean_contacts"] for r in _arm(a)]
        e3[a] = {"n_legs": sum(1 for v in vals if v is not None),
                 "per_leg_mean_contacts": vals,
                 "model_level_mean_contacts": _by_model(a, "e3_mean_contacts"),
                 "arm_mean_contacts": _mean(vals),
                 "min_leg": min([v for v in vals if v is not None], default=None),
                 "max_leg": max([v for v in vals if v is not None], default=None)}

    e4 = {}
    for a in arms:
        mins = [r["e4_min_A"] for r in _arm(a) if r["e4_min_A"] is not None]
        meds = [r["e4_median_A"] for r in _arm(a) if r["e4_median_A"] is not None]
        maxs = [r["e4_max_A"] for r in _arm(a) if r["e4_max_A"] is not None]
        e4[a] = {"n_legs_with_a_distribution": len(mins),
                 "n_legs_with_no_surface_Lys": sum(1 for r in _arm(a) if r["e4_min_A"] is None),
                 "per_leg_min_A": mins, "per_leg_median_A": meds, "per_leg_max_A": maxs,
                 "arm_min_of_min_A": min(mins, default=None),
                 "arm_mean_of_min_A": _mean(mins),
                 "arm_mean_of_median_A": _mean(meds),
                 "arm_max_of_max_A": max(maxs, default=None)}

    return {
        "_role": "PREREGISTERED SECONDARIES, REPORTED. None of E2/E3/E4 is a verdict, a tier condition or a "
                 "substitute primary; E1 is the registered primary and the only endpoint the verdict turns "
                 "on. Gating on the friendliest endpoint is precisely the retune this program forbids.",
        "n_legs_scored": len(rows),
        "arms": arms,
        "E2": {
            "prereg_definition": "stable fraction: fraction of an arm's legs with interface-RMSD plateau "
                                 "< %.1f A (prereg §3, kernel nrv04_readouts.interface_rmsd_stable().stable)"
                                 % gate.STABLE_PLATEAU_A,
            "threshold_A": gate.STABLE_PLATEAU_A,
            "threshold_source": "nrv04_retro_gate.STABLE_PLATEAU_A (frozen; inherited unchanged from "
                                "nrv04_readouts.INTERFACE_RMSD_STABLE_A) — read, never typed here",
            "prereg_caveat": "the motivating observation behind E2 (recruiter_active 3/3 vs epimer 1/3) was "
                             "WITHDRAWN 2026-07-24 — that panel scored the Elongin C interface, not "
                             "VHL↔NR4A1. The endpoint and its 4.0 A threshold are unchanged (frozen before "
                             "the panel ran, not re-tuned), but E2 has no demonstrated discrimination "
                             "behind it. See nrv04-cofold-chain-forensics-2026-07-24.md.",
            "unit": "fraction of legs (a per-LEG binary, as written — not a model-level quantity; the "
                    "model-level split is reported beside it, untested)",
            "per_arm": e2,
            "threshold_disagreements": [r["unit"] for r in rows if not r["e2_threshold_agrees"]],
        },
        "E3": {
            "prereg_definition": "mean interface contact count over production (prereg §3, kernel "
                                 "nrv04_readouts.recruitment().mean_contacts; contacts are heavy-atom pairs "
                                 "within %.1f A)" % 4.5,
            "prereg_caveat": "KNOWN WEAK DISCRIMINATOR — the feasibility panel showed co-fold seeds contact "
                             "in all arms — so it is reported, never gating (prereg §3).",
            "unit": "heavy-atom contact pairs per frame",
            "per_arm": e3,
        },
        "E4": {
            "prereg_definition": "Lys-Nζ presentation distance distribution: per frame, the minimum "
                                 "target-Lys-Nζ → catalytic-proxy distance; the distribution's min / median "
                                 "/ max across production frames (prereg §3, kernel "
                                 "nrv04_readouts.lys_presentation())",
            "prereg_caveat": "DESCRIPTIVE ONLY, NEVER A GATE (prereg §3, citing ternary prereg §6.3: no "
                             "distance cutoff quantitatively predicts degradation). No threshold is applied "
                             "to E4 anywhere in this module and none may be introduced.",
            "unit": "Angstrom",
            "per_arm": e4,
        },
        "per_leg": rows,
    }


# =============================================================================================================
# re-derivations through the FROZEN scorer — PURE, no S3
# =============================================================================================================
def pairwise_power_probe(model_level_means, alpha=None):
    """Exact size and power of each preregistered PAIRWISE secondary test, re-derived through the frozen
    scorer's own enumeration. PURE.

    ★ THE POINT. A one-sided exact permutation test on `n_a` vs `n_b` model-level values can only ever return
    a p-value in {1/C, 2/C, …, 1} with C = C(n_a+n_b, n_a). When the SMALLEST of those, 1/C, already exceeds
    α, the rejection region is EMPTY: no observed arrangement, at any separation δ however large, produces
    p ≤ α. Its exact size is 0.0 and its power against every δ is exactly 0.0 — **by construction, before any
    data**. Such a test is a NON-MEASUREMENT, not a null: "did not reach significance" and "unresolvable" both
    understate it, because both suggest an experiment that could have come out the other way.

    Returns one entry per paralogue arm with `min_attainable_p`, `alpha_attainable`, `exact_size`,
    `power_against_any_delta` and the observed result copied from the frozen scorer."""
    import nrv04_retro_gate as gate

    alpha = gate.ALPHA if alpha is None else alpha
    means = {a: {int(m): float(v) for m, v in ms.items()} for a, ms in model_level_means.items()}
    primary_vals = [means[gate.PRIMARY_ARM][m] for m in sorted(means.get(gate.PRIMARY_ARM, {}))]
    out = {}
    for arm in gate.POOLED_ARMS:
        arm_vals = [means[arm][m] for m in sorted(means.get(arm, {}))]
        if not primary_vals or not arm_vals:
            out[arm] = {"_absent": "no model-level values for %s — NOT a null result" % arm}
            continue
        r = gate.exact_permutation_p(primary_vals, arm_vals, alternative="less")
        attainable = r["min_attainable_p"] <= alpha + 1e-12
        out[arm] = {
            "n_models_nr4a1": len(primary_vals), "n_models_paralogue": len(arm_vals),
            "n_arrangements": r["n_arrangements"],
            "attainable_p_values": [round(k / r["n_arrangements"], 6)
                                    for k in range(1, r["n_arrangements"] + 1)][:12],
            "min_attainable_p": r["min_attainable_p"],
            "alpha": alpha,
            "alpha_attainable": attainable,
            "exact_size": 0.0 if not attainable else None,
            "power_against_any_delta": 0.0 if not attainable else None,
            "observed": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()},
            "reading": (
                "MEASURED, blunt: α is attainable (min p = %.4g ≤ α = %.2f), so the observed p is a real "
                "null at this design's power." % (r["min_attainable_p"], alpha) if attainable else
                "⛔ NON-MEASUREMENT, NOT A NULL. min attainable one-sided p = %.4g > α = %.2f, so the "
                "rejection region is EMPTY: exact size 0.0 and power exactly 0.0 against a true effect δ of "
                "ANY magnitude. The observed p = %.4g could not have been small; this test could not have "
                "detected a difference of any size. 'Unresolvable' and 'did not reach significance' both "
                "understate it — nothing was measured."
                % (r["min_attainable_p"], alpha, r["p"])),
        }
    return out


def replicate_invariance_probe(model_level_means, legs_per_model=(2, 8, 20, 100)):
    """Feed the FROZEN scorer the landed panel at k legs per co-fold model and show the verdict does not move.
    PURE, $0, launches nothing.

    ★ WHY IT SETTLES THE QUESTION. The obvious response to a p of 0.39 is "run more replicates". It cannot
    help, and this is the demonstration rather than the argument: `nrv04_retro_gate.model_level_values`
    collapses a model's legs to their mean BEFORE the enumeration, so the reference set is sized by the number
    of MODELS (8 here → C(8,3) = 56), not by the number of legs. At 100 legs per model — 800 legs against the
    16 that ran — the enumeration, the reference set, the statistic and the p-value are IDENTICAL.

    Each synthetic leg carries its model's LANDED model-level mean, so this changes only the leg COUNT and
    nothing about the values; the noise a real replicate would average down is treated separately by
    `selectivity_resolution_options.variance_decomposition`, whose 19 % ceiling is its one home."""
    import nrv04_retro_gate as gate

    means = {a: {int(m): float(v) for m, v in ms.items()} for a, ms in model_level_means.items()}
    rows = []
    for k in legs_per_model:
        legs = [{"arm_id": a, "cofold_model_seed": m, "replica": i, "e1_plateau_A": v}
                for a, ms in means.items() for m, v in ms.items() for i in range(k)]
        v = gate.verdict(legs)
        rows.append({"legs_per_model": k, "n_legs_total": len(legs),
                     "tier": v["tier"],
                     "n_arrangements": v["primary"]["n_arrangements"],
                     "min_attainable_p": v["primary"]["min_attainable_p"],
                     "stat": v["primary"]["stat"], "p": v["primary"]["p"],
                     "pairwise_nr4a3_n_arrangements":
                         v["pairwise_secondary"]["retro_noncov_nr4a3"]["n_arrangements"],
                     "pairwise_nr4a3_p": v["pairwise_secondary"]["retro_noncov_nr4a3"]["p"]})
    identical = all(r["n_arrangements"] == rows[0]["n_arrangements"] and
                    abs(r["p"] - rows[0]["p"]) < 1e-12 and abs(r["stat"] - rows[0]["stat"]) < 1e-9
                    for r in rows)
    return {
        "_what": "the FROZEN scorer re-run on the landed model means at k legs per co-fold model",
        "rows": rows,
        "identical_across_k": identical,
        "mechanism": "nrv04_retro_gate.model_level_values collapses a model's legs to their mean BEFORE the "
                     "enumeration (prereg §4a: the unit of independence is the CO-FOLD MODEL, not the leg), "
                     "so the reference set is sized by the number of MODELS and replicates cannot move it.",
        "what_replicates_CAN_buy": "only a reduction in the replicate component of model-level noise, which "
                                   "is bounded. That ceiling is DERIVED in "
                                   "selectivity_resolution_options.variance_decomposition and reported in "
                                   "selectivity-resolution-options.md — its one home; not re-derived here.",
    }


def frozen_scorer_probes(model_level_means):
    """Both pure re-derivations in one object, with the pointer to σ's one home. PURE."""
    return {
        "_role": "REPORTED. Re-runs the FROZEN primary/pairwise rule unchanged; proposes no new rule, moves "
                 "no threshold, and promotes nothing.",
        "pairwise_power": pairwise_power_probe(model_level_means),
        "replicate_invariance": replicate_invariance_probe(model_level_means),
        "which_sigma": {
            "_pointer": "σ has ONE home and it is not here: selectivity-resolution-options.md §1a / "
                        "selectivity-resolution-options.json → `which_sigma`, derived by "
                        "selectivity_resolution_options.py from this same landed panel.",
            "the_one_the_test_competes_against": "MODEL-LEVEL σ — the pooled within-arm SD of the model "
                                                 "means (df 5). It is neither the registered leg-to-leg σ "
                                                 "(smaller, optimistic, frozen in "
                                                 "nrv04_retro_gate.MEASURED_LEG_SIGMA_A) nor the "
                                                 "criteria-audit's same-quantity-smaller-sample figure "
                                                 "(nrv04-retro-criteria-audit.json → measured_noise).",
            "why_it_matters_here": "quoting a leg-to-leg σ overstates power; the replicate-invariance row "
                                   "above and the bounded noise cut are the two halves of why more "
                                   "replicates buy nothing structural.",
        },
    }


# =============================================================================================================
# the S3 census — what is actually stored under the lane prefix
# =============================================================================================================
def _list_leg_objects(s3, bucket, prefix):
    """Every object under the lane prefix, with LastModified and Size. Paginated."""
    objs, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix.rstrip("/") + "/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            objs.append({"key": o["Key"], "size": o["Size"], "last_modified": o["LastModified"]})
        tok = r.get("NextContinuationToken")
        if not r.get("IsTruncated"):
            break
    return objs


def census(s3, bucket=BUCKET, prefix=PREFIX):
    """Walk the lane's S3 prefix and grade every leg record on MEASURED provenance. Read-only.

    Returns `(census_dict, admitted_legs)` where `admitted_legs` are the records that passed the frozen
    `production_leg_check` and are therefore the ONLY ones `secondary_endpoints` may be handed."""
    import nrv04_retro_panel as retro

    objs = _list_leg_objects(s3, bucket, prefix)
    leg_objs = [o for o in objs if o["key"].endswith(".json") and o["key"].rsplit("/", 1)[-1].startswith("leg_")]

    # Per-unit S3 write span — the indirect equilibration evidence (see EQUIL_EVIDENCE_NOTE). A unit's
    # objects are all written under `<prefix>/<unit>/`, so first→last bounds the whole leg's wall clock.
    spans = {}
    for o in objs:
        parts = o["key"].split("/")
        if len(parts) < 3:
            continue
        unit = parts[-2]
        s = spans.setdefault(unit, {"first": o["last_modified"], "last": o["last_modified"], "n_objects": 0})
        s["n_objects"] += 1
        s["first"] = min(s["first"], o["last_modified"])
        s["last"] = max(s["last"], o["last_modified"])

    admitted, rejected, rows = [], [], []
    for o in sorted(leg_objs, key=lambda x: x["last_modified"]):
        k = o["key"]
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception as e:  # noqa: BLE001 — "could not read" is NEVER "read and found nothing"
            rejected.append({"key": k, "unreadable": "%s: %s" % (type(e).__name__, e),
                             "note": "UNREADABLE, not absent — this record is neither admitted nor "
                                     "declared missing (CLAUDE.md §4b)"})
            continue
        unit = k.split("/")[-2]
        leg_id = d.get("leg_id") or ""
        arm_id, _, mtag = leg_id.partition("__m")
        ok, why = retro.production_leg_check(d)
        done_ok, done_why = retro.completed_production_check(d)
        span = spans.get(unit) or {}
        prod_wall = d.get("prod_wall_s")
        span_s = None
        if span.get("first") and span.get("last"):
            span_s = round((span["last"] - span["first"]).total_seconds(), 1)
        traj = d.get("analysis_traj") or {}
        r2 = d.get("R2_recruitment") or {}
        meta = d.get("meta") or {}
        row = {
            "unit": unit, "key": k, "arm_id": arm_id,
            "cofold_model_seed": int(mtag) if mtag.isdigit() else None,
            "replica": d.get("seed"),
            "record_bytes": o["size"],
            "record_written_utc": o["last_modified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            # ── MEASURED: a run had to happen ────────────────────────────────────────────────────────────
            "measured": {f: d.get(f) for f in MEASURED_FIELDS},
            "measured_readout_frames": r2.get("frames"),
            "measured_traj_written_frames": traj.get("written_frames"),
            "measured_traj_bytes": traj.get("bytes"),
            # The topology the readouts were actually computed against — written by the run, not requestable
            # from ENV. `target_lys_nz` is the size of the atom set E4's distribution is taken over, so an
            # E4 outlier can be checked against it rather than guessed at.
            "measured_chain_split": d.get("chain_split"),
            "measured_n_atoms": meta.get("n_atoms"),
            "reported_unit_s3_span_s": span_s,
            "reported_unit_s3_objects": span.get("n_objects"),
            "reported_unit_s3_span_note": S3_SPAN_NOTE,
            # ── ECHOED: an ENV default fills these ───────────────────────────────────────────────────────
            "env_echoed": {f: d.get(f) for f in ENV_ECHOED_FIELDS},
            # ── the two verdicts, kept apart (nrv04_retro_panel: membership ≠ completion) ────────────────
            "admitted_to_panel": ok, "admitted_why": why,
            "completed_production": done_ok, "completed_why": done_why,
            "blew_up": bool(d.get("blew_up")), "blow_phase": d.get("blow_phase"),
        }
        # CORROBORATION: does the measured evidence agree with the ENV echo? A leg that says mode='run' and
        # shows 5 frames in 7 s is the 2026-07-31 failure wearing a production label. ⛔ EVERY CHECK BELOW
        # COMPARES TWO THINGS THE RUN ITSELF WROTE — no ENV field is an input to any of them, and the S3
        # span is deliberately absent (see S3_SPAN_NOTE: it would condemn clean legs).
        checks = []
        want_frames = retro.expected_production_frames(retro.PROD_NS)
        if d.get("n_frames") != want_frames:
            checks.append("n_frames=%r != %d expected at the canonical stride" % (d.get("n_frames"), want_frames))
        if r2.get("frames") is not None and r2.get("frames") != d.get("n_frames"):
            checks.append("R2_recruitment.frames=%r != n_frames=%r (the readout kernel counted a different "
                          "number of production frames than the driver recorded)"
                          % (r2.get("frames"), d.get("n_frames")))
        if traj.get("written_frames") is not None and traj.get("written_frames") != d.get("n_frames"):
            checks.append("analysis_traj.written_frames=%r != n_frames=%r (the durable trajectory does not "
                          "match the scored trajectory)" % (traj.get("written_frames"), d.get("n_frames")))
        if isinstance(prod_wall, (int, float)) and prod_wall < 600:
            checks.append("prod_wall_s=%r — under 10 minutes of measured production wall clock, which no "
                          "5 ns leg on this lane's cards has achieved" % prod_wall)
        # ns/day is DERIVED by the driver from timed_ns and prod_wall_s. Recomputing it is a measured-vs-
        # measured identity: it fails if any of the three was written from something other than the run.
        nspd, timed = d.get("ns_per_day"), d.get("timed_ns")
        if all(isinstance(x, (int, float)) for x in (nspd, timed, prod_wall)) and prod_wall > 0:
            want_nspd = timed / (prod_wall / 86400.0)
            row["measured_ns_per_day_recomputed"] = round(want_nspd, 2)
            if abs(want_nspd - nspd) > max(0.05, 0.001 * abs(nspd)):
                checks.append("ns_per_day=%r but timed_ns/prod_wall_s gives %.2f — the throughput field does "
                              "not follow from the two measurements it is derived from" % (nspd, want_nspd))
        row["corroboration_failures"] = checks
        row["measured_corroborates_env_echo"] = not checks
        row["equilibration_evidence"] = EQUIL_EVIDENCE_NOTE
        rows.append(row)
        if ok:
            admitted.append({"arm_id": arm_id, "unit": unit,
                             "cofold_model_seed": int(mtag) if mtag.isdigit() else None,
                             "replica": d.get("seed"),
                             "R1_interface": d.get("R1_interface") or d.get("R1") or {},
                             "R2_recruitment": d.get("R2_recruitment") or d.get("R2") or {},
                             "R3_lys": d.get("R3_lys") or d.get("R3") or {}})
        else:
            rejected.append({"key": k, "unit": unit, "leg_id": leg_id, "mode": d.get("mode"),
                             "n_frames": d.get("n_frames"), "timed_ns": d.get("timed_ns"), "why": why})

    expected = {retro.unit_name(a, m, r) for a, m, r in retro.enumerate_units()}
    have = {r["unit"] for r in rows if r["admitted_to_panel"]}
    return {
        "_what": "S3 census of the NR-V04 retrospective lane's stored leg records, graded on MEASURED "
                 "provenance rather than on ENV-echoed fields (CLAUDE.md §4b).",
        "bucket": bucket, "prefix": prefix,
        "n_objects_under_prefix": len(objs),
        "n_leg_records_found": len(leg_objs),
        "n_admitted_to_panel": len(admitted),
        "n_rejected": len(rejected),
        "expected_units": sorted(expected),
        "missing_units": sorted(expected - have),
        "panel_complete": not (expected - have),
        "measured_fields": list(MEASURED_FIELDS),
        "env_echoed_fields": list(ENV_ECHOED_FIELDS),
        "equilibration_evidence": EQUIL_EVIDENCE_NOTE,
        "s3_span_evidence": S3_SPAN_NOTE,
        "all_admitted_legs_corroborated": all(r["measured_corroborates_env_echo"]
                                              for r in rows if r["admitted_to_panel"]),
        "legs_failing_corroboration": [r["unit"] for r in rows
                                       if r["admitted_to_panel"] and not r["measured_corroborates_env_echo"]],
        "rejected_records": rejected,
        "per_record": rows,
    }, admitted


def reproduces_emitted_verdict(admitted, model_means):
    """★ THE INTEGRITY CHECK THE CENSUS EXISTS FOR. Collapse the S3-read legs to model-level E1 means by
    prereg §4a and compare them, model by model, with the means in the EMITTED verdict. PURE.

    If the two disagree, then either the collector and this census saw different objects or one of them
    mapped a key wrongly — and the paper would be quoting a number nothing supports. Agreement is what makes
    "reported from the 16 landed legs" a statement about stored artifacts rather than about a readout."""
    got = {}
    for leg in admitted:
        v = (leg.get("R1_interface") or {}).get("plateau_A")
        if v is None or leg.get("cofold_model_seed") is None:
            continue
        got.setdefault(leg["arm_id"], {}).setdefault(int(leg["cofold_model_seed"]), []).append(float(v))
    got = {a: {m: round(sum(v) / len(v), 4) for m, v in sorted(ms.items())} for a, ms in sorted(got.items())}
    want = {a: {int(m): round(float(v), 4) for m, v in ms.items()} for a, ms in model_means.items()}
    diffs = []
    for a in sorted(set(got) | set(want)):
        for m in sorted(set(got.get(a, {})) | set(want.get(a, {}))):
            g, w = got.get(a, {}).get(m), want.get(a, {}).get(m)
            if g is None or w is None or abs(g - w) > 5e-4:
                diffs.append({"arm": a, "model": m, "from_s3_legs": g, "in_emitted_verdict": w})
    return {
        "_what": "model-level E1 means recomputed from the S3 leg records, against the EMITTED verdict's own "
                 "`model_level_means`. The verdict is authoritative; this is the check that the census read "
                 "the same panel.",
        "from_s3_legs": got, "in_emitted_verdict": want,
        "agree": not diffs, "disagreements": diffs,
    }


def e4_outliers(secondaries, ratio=4.0):
    """FLAG ONLY. Legs whose E4 distribution sits a factor of `ratio` away from their arm's median leg.

    ⚠ It changes nothing. E4 is descriptive-only and never a gate (prereg §3), so an outlier is neither
    excluded, down-weighted, nor allowed to move any number — it is NAMED, with the fields that would
    discriminate a real geometry from an artifact, so the next reader starts from the observation rather
    than from a story."""
    out = []
    for arm in secondaries["arms"]:
        rows = [r for r in secondaries["per_leg"] if r["arm_id"] == arm and r["e4_median_A"] is not None]
        if len(rows) < 3:
            continue
        meds = sorted(r["e4_median_A"] for r in rows)
        centre = meds[len(meds) // 2]
        for r in rows:
            if centre and (r["e4_median_A"] * ratio < centre or r["e4_median_A"] > centre * ratio):
                out.append({"unit": r["unit"], "arm_id": arm,
                            "e4_min_A": r["e4_min_A"], "e4_median_A": r["e4_median_A"],
                            "e4_max_A": r["e4_max_A"],
                            "arm_median_leg_e4_median_A": centre,
                            "ratio_to_arm_median": round(centre / r["e4_median_A"], 2) if r["e4_median_A"] else None})
    return {"_role": "FLAG ONLY — E4 is descriptive, never a gate (prereg §3). No leg is excluded, "
                     "re-weighted or corrected on the strength of this list, and no E4 number elsewhere in "
                     "this document is computed with outliers removed.",
            "ratio": ratio, "outliers": out}


# =============================================================================================================
# assembly
# =============================================================================================================
def _landed_model_means(path=VERDICT_JSON):
    """Model-level E1 means from the EMITTED verdict artifact — copied, never recomputed (rule 1)."""
    with open(path) as fh:
        v = json.load(fh)
    m = ((v.get("verdict") or {}).get("model_level_means")) or {}
    if not m:
        raise SystemExit("no model_level_means in %s — an unreadable verdict is NOT an absent one" % path)
    return {a: {int(s): float(x) for s, x in ms.items()} for a, ms in m.items()}


def build(census_doc, admitted, model_means):
    """The committed document. PURE given its inputs."""
    sec = secondary_endpoints(admitted)
    return {
        "_what": "The PREREGISTERED SECONDARY ENDPOINTS E2, E3 and E4 of the NR-V04 retrospective (prereg §3), "
                 "reported from the 16 landed legs — the report prereg §3 promised and "
                 "nrv04-retro-criteria-audit.json recorded as unimplemented.",
        "_not_promoted": "REPORT ONLY. None of E2, E3 or E4 is promoted to a verdict, a tier condition or a "
                         "substitute primary. E1 (interface-RMSD plateau) is the registered primary and the "
                         "only endpoint the verdict turns on; the emitted tier is DISCORDANT and nothing "
                         "here changes it. If a secondary looks better-behaved than E1, that is a fact "
                         "stated and explicitly NOT acted on: gating on the friendliest endpoint is "
                         "precisely the retune this program forbids. Reporting them was owed regardless of "
                         "how they came out.",
        "_primary_lives_at": "nrv04-retro-verdict.json (the emitted verdict; the tier, the primary "
                             "statistic, its p and the reference set have their one home there and are not "
                             "re-typed here).",
        "prereg": "nr4a3-nrv04-retrospective-prereg.md",
        "amendment": "AMENDMENT 4 (2026-07-31): 16 legs, model-level n = 3 / 3 / 2.",
        "s3_census": census_doc,
        "reproduces_emitted_verdict": reproduces_emitted_verdict(admitted, model_means),
        "secondaries": sec,
        "e4_outliers": e4_outliers(sec),
        "frozen_scorer_probes": frozen_scorer_probes(model_means),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="NR-V04 retrospective secondaries E2/E3/E4 (read-only, $0).")
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--prefix", default=PREFIX)
    ap.add_argument("--verdict", default=VERDICT_JSON)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--no-s3", action="store_true",
                    help="skip the S3 census and emit only the pure frozen-scorer probes (offline check)")
    args = ap.parse_args(argv)

    model_means = _landed_model_means(args.verdict)
    if args.no_s3:
        doc = {"_what": "OFFLINE PROBE ONLY — no S3 census, no E2/E3/E4. Not the deliverable.",
               "frozen_scorer_probes": frozen_scorer_probes(model_means)}
    else:
        import boto3
        s3 = boto3.client("s3")
        census_doc, admitted = census(s3, args.bucket, args.prefix)
        doc = build(census_doc, admitted, model_means)

    print(json.dumps({k: v for k, v in doc.items() if k != "s3_census"}, indent=2, default=str)[:60000],
          flush=True)
    c = doc.get("s3_census") or {}
    if c:
        print("\n=== S3 CENSUS: %d object(s), %d leg record(s), %d admitted, %d rejected ==="
              % (c["n_objects_under_prefix"], c["n_leg_records_found"], c["n_admitted_to_panel"],
                 c["n_rejected"]), flush=True)
        hdr = ("%-42s %-6s %7s %9s %9s %8s %9s  ADMITTED"
               % ("UNIT", "mode", "FRAMES", "timed_ns", "wall_s", "span_s", "traj_fr"))
        print(hdr, flush=True)
        print("-" * len(hdr), flush=True)
        for r in c["per_record"]:
            print("%-42s %-6s %7s %9s %9s %8s %9s  %s%s"
                  % (r["unit"], r["env_echoed"].get("mode"), r["measured"].get("n_frames"),
                     r["measured"].get("timed_ns"), r["measured"].get("prod_wall_s"),
                     r.get("reported_unit_s3_span_s"), r.get("measured_traj_written_frames"),
                     "yes" if r["admitted_to_panel"] else "NO",
                     "" if r["measured_corroborates_env_echo"] else
                     "  ⚠ %s" % "; ".join(r["corroboration_failures"])), flush=True)
        rep = doc.get("reproduces_emitted_verdict") or {}
        print("\n[retro-secondaries] model-level E1 recomputed from the S3 legs %s the emitted verdict%s"
              % ("AGREES WITH" if rep.get("agree") else "⛔ DISAGREES WITH",
                 "" if rep.get("agree") else ": %s" % rep.get("disagreements")), flush=True)
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=2, default=str)
    print("\n[retro-secondaries] wrote %s" % args.out, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
