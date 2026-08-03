#!/usr/bin/env python3
"""BOTTOM-UP PRICE FOR THE TWO SCOPE RUNGS — `R13` (fusion-context object) and `R14` (AR/MR cross-binding).

★ WHY. Roadmap §10.1 rows 9 and 10 both read "⛔ unpriced — on no plan, spine or ranked list", and §10.2 says
of five such rows that "the next action is the same $0 act: give it a rung, a gate and a price." This file is
that act for two of them. It buys nothing and dispatches nothing.

★★ EVERY FIGURE HERE IS **DERIVED**, NEVER TYPED (CLAUDE.md §1.1):
  * the market rate and its band come from `vast-ladder-repricing.json` (`plan_usd_per_reference_gpu_h`,
    `range_usd_per_reference_gpu_h`) — the SAME live artifact the ladder itself is priced from, so these
    rungs move with the ladder instead of freezing a remembered $0.137;
  * the co-fold per-model GPU-h is READ OUT of `selcal-price-ledger.json` — a completed, billed, 12-model
    co-fold panel on the reference card — not estimated;
  * the metadynamics leg lengths are read as the workflow's own declared defaults, and its throughput is the
    MEASURED LANE-13 table in pricing.md §A.1, cited with its source rather than re-derived.

⛔⛔ AND THESE TWO RUNGS ARE **EXCLUDED FROM THE PINNED LADDER TOTAL**, deliberately and in the same way the
5a-KS confirmatory wedge and the reciprocal mutation cycle are (pricing.md §C, "Excluded from the total").
Reason: they are CLAIM-CEILING conditions, not steps of the gated 5a→5d spine, and they are not gated on any
rung's GO. Folding them into the pinned total would silently move a number `lint_consistency` checks and that
`vast_cost_model.py` derives. The map links to this artifact; it does not add these into `Cum.`.

★ WHAT THIS FILE REFUSES TO PRICE, AND WHY — read `unpriceable` in the artifact. Pricing the whole of `R13`
or the whole of `R14` would be inventing numbers; each has a tier that rests on something not measured
anywhere, and those tiers are named as unpriced rather than given a figure.

CLI:  python3 scope_rung_cost.py            # regenerate scope-rung-cost.json
      python3 scope_rung_cost.py --check    # regenerate and diff against the committed artifact (CI)
"""
from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUT_JSON = os.path.join(HERE, "scope-rung-cost.json")
LADDER = os.path.join(HERE, "vast-ladder-repricing.json")
SELCAL_LEDGER = os.path.join(HERE, "selcal-price-ledger.json")

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# MEASURED INPUTS — each names the artifact or file that OWNS it. Nothing here is an estimate wearing a
# measurement's clothes; anything that is an assumption says so in its own key.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════

#: LANE-13 metadynamics legs, realised ns/day, measured with the board's `gpu_util` at the same moment.
#: ONE HOME: research/compute/pricing.md §A.1 (four legs). Quoted here, not created here.
LANE13_METAD_NS_PER_DAY = (141.0, 146.0, 77.0, 47.0)
LANE13_METAD_SOURCE = "research/compute/pricing.md §A.1 — four LANE-13 metadynamics legs, realised ns/day"

#: The SAME instance crossing the metad→release boundary, minutes apart, same card: the unbiased-MD rate.
#: ONE HOME: pricing.md §A.1 second table (instance 45896793, RTX 4080S, ~8.7 ns/h ≈ 209 ns/day).
#: Used as a CONSERVATIVE release rate: it was measured on a 4080S, and the reference 4090 is faster.
RELEASE_NS_PER_DAY = 209.0
RELEASE_SOURCE = ("research/compute/pricing.md §A.1 — instance 45896793 at the metad→release phase boundary "
                  "(RTX 4080S; the reference RTX 4090 is faster, so this is a conservative rate)")

#: Workflow-declared ensemble recipe per species. ONE HOME:
#: .github/workflows/gpu-nr4a-paralogue-md-vast.yml:104-105 (metad_ns 60, release_ns 5) and the committed
#: ensembles' own census (25 metad + 3 x 25 release frames, nr4a-paralogue-dynamics.json ensemble_census).
METAD_NS = 60.0
RELEASE_NS_PER_REP = 5.0
N_RELEASE_REPS = 3
ENSEMBLE_SOURCE = (".github/workflows/gpu-nr4a-paralogue-md-vast.yml:104-105 defaults (metad_ns 60, "
                   "release_ns 5) x n_rep 3, matching nr4a-paralogue-dynamics.json ensemble_census "
                   "(25 metad + 3 x 25 release = 100 frames per species)")

#: R13-b unit count: 2 constructs (seam, composite — fusion_cofold.py) x 6 seeds, where 6 is the seed count
#: the ONE completed co-fold panel in this repo actually ran (selcal-cofold-census.json n_models_per_arm).
R13B_CONSTRUCTS = 2
R13B_SEEDS = 6

#: R14-b species count: AR and MR/NR3C2 — the two the 47-receptor screen flagged and the SI names as "the
#: sole sequence-level non-paralogue follow-ups" (nr4a-superfamily-selectivity.json; SI §S3).
R14B_SPECIES = 2


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def _r(x, n=4):
    return None if x is None else round(float(x), n)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PURE arithmetic
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def cofold_basis(ledger):
    """Measured ref-GPU-h and $ per co-fold MODEL, read out of the one completed co-fold panel. PURE-ish.

    Only rentals whose label marks them as the CO-FOLD stage are counted; this lane's MD legs are a different
    rung and carry their own labels. Every counted rental was on the reference card, so GPU-h == ref-GPU-h
    with no conversion — which is why this basis needs no card ratio at all.
    """
    rows = [r for r in ledger["rentals"] if "cofold" in r.get("label", "")]
    cards = sorted({r.get("gpu_name") for r in rows})
    hours = sum((r.get("uptime_s") or 0.0) for r in rows) / 3600.0
    billed = sum((r.get("billed_usd") or 0.0) for r in rows)
    n_models = R13B_CONSTRUCTS * R13B_SEEDS  # the panel delivered 6 seeds x 2 arms == our unit count
    return {
        "n_rentals": len(rows),
        "cards": cards,
        "all_on_reference_card": cards == ["RTX 4090"],
        "ref_gpu_h_total": _r(hours, 3),
        "billed_usd_as_run": _r(billed, 4),
        "models_delivered": n_models,
        "ref_gpu_h_per_model": _r(hours / n_models, 4),
        "as_run_usd_per_model": _r(billed / n_models, 4),
        "_source": ("selcal-price-ledger.json, rentals labelled `selcal-cofold-*`; model count from "
                    "selcal-cofold-census.json n_models_per_arm (6 per arm, 2 arms, complete)"),
        "_why_this_is_an_UPPER_bound_twice_over": [
            "SIZE: the panel co-folded a SMARCA2/4 ternary + degrader (~4.5k heavy atoms, ~570 residues). "
            "The fusion constructs are SMALLER — seam ~380 residues, composite ~486 (fusion_cofold.py "
            "EWS_SEAM_LEN / NR4A3_AF1_END / NR4A3_CORE_START) — and fusion_cofold.py's own header states the "
            "cost is ~N^2 in sequence length. A bigger system's per-model rate therefore OVERSTATES ours.",
            "ENVIRONMENT: those hours include an environment BUILD on the billing host (apt/pip/~3 GB "
            "download), which CLAUDE.md §6 has since forbidden. Running the same work off a baked image is "
            "strictly cheaper, so the measured hours overstate a compliant re-run as well.",
        ],
    }


def metad_ensemble_basis():
    """ref-GPU-h for ONE matched cryptic-pocket ensemble (metad + release replicas). PURE.

    ⚠ The metadynamics half is priced on MEASURED realised ns/day, NOT on the card-constant throughput
    table — pricing.md §A.1 establishes that `$/ns` built from a card constant CANNOT represent a workload
    whose rate depends on the host CPU, and PLUMED metadynamics is exactly that workload. The measured
    host-to-host spread is carried as the band rather than averaged away.
    """
    ns = sorted(LANE13_METAD_NS_PER_DAY)
    med = statistics.median(ns)
    release_h = (RELEASE_NS_PER_REP * N_RELEASE_REPS) / (RELEASE_NS_PER_DAY / 24.0)

    def _tot(metad_rate):
        return METAD_NS / (metad_rate / 24.0) + release_h

    return {
        "recipe_per_species": {"metad_ns": METAD_NS, "release_ns_per_rep": RELEASE_NS_PER_REP,
                               "n_release_reps": N_RELEASE_REPS,
                               "total_ns": METAD_NS + RELEASE_NS_PER_REP * N_RELEASE_REPS,
                               "_source": ENSEMBLE_SOURCE},
        "metad_ns_per_day_measured": list(LANE13_METAD_NS_PER_DAY),
        "metad_ns_per_day_median": med,
        "_metad_source": LANE13_METAD_SOURCE,
        "release_ns_per_day": RELEASE_NS_PER_DAY,
        "_release_source": RELEASE_SOURCE,
        "release_ref_gpu_h": _r(release_h, 3),
        "ref_gpu_h_per_species": _r(_tot(med), 3),
        "ref_gpu_h_per_species_band": [_r(_tot(max(ns)), 3), _r(_tot(min(ns)), 3)],
        "_the_band_is_HOST_CPU_not_price": (
            "the 3.1x spread (%.0f -> %.0f ns/day) is measured on the SAME workload and is host-CPU-bound, "
            "not market-driven: pricing.md §A.1 caught the same instance jump 24-33%% -> 74%% gpu_util at the "
            "metad->release boundary, same card, minutes apart. So this rung's dominant uncertainty is "
            "GPU-HOURS, not $/hr, and host CPU has to enter selection for it."
            % (max(ns), min(ns))),
    }


def price(ref_gpu_h, plan_rate, rate_band):
    return {"ref_gpu_h": _r(ref_gpu_h, 3),
            "plan_usd": _r(ref_gpu_h * plan_rate, 4),
            "range_usd": [_r(ref_gpu_h * rate_band[0], 4), _r(ref_gpu_h * rate_band[1], 4)]}


def price_band(ref_gpu_h_band, plan_rate, rate_band):
    """A rung whose GPU-HOURS themselves have a measured band: low = fewest hours at the best rate,
    high = most hours at the median rate. Same low/high convention pricing.md §C uses."""
    lo_h, hi_h = ref_gpu_h_band
    return {"ref_gpu_h_band": [_r(lo_h, 3), _r(hi_h, 3)],
            "range_usd": [_r(lo_h * rate_band[0], 4), _r(hi_h * rate_band[1], 4)]}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def build():
    ladder = _load(LADDER)
    plan_rate = ladder["plan_usd_per_reference_gpu_h"]
    rate_band = ladder["range_usd_per_reference_gpu_h"]
    basis_usd_per_ns = ladder["market"]["best10_mean_usd_per_ns"]

    import inflight_usd_per_ns as I
    buy_line = I.APPROVED_USD_PER_NS

    cf = cofold_basis(_load(SELCAL_LEDGER))
    me = metad_ensemble_basis()

    # ---- R13 -------------------------------------------------------------------------------------------
    r13b_units = R13B_CONSTRUCTS * R13B_SEEDS
    r13b_h = cf["ref_gpu_h_per_model"] * r13b_units
    r13b = price(r13b_h, plan_rate, rate_band)
    r13b.update({
        "units": r13b_units,
        "unit": "apo Boltz-2 co-fold model (construct x seed)",
        "usd_per_ns": None,
        "_why_no_usd_per_ns": ("a co-fold is structure INFERENCE — it integrates no dynamics and produces no "
                               "nanoseconds, so a $/ns here would have no denominator and would be a "
                               "fabricated figure in the one column CLAUDE.md §1 exists to make gradeable. "
                               "Same refusal as selcal_board.py / inflight_board.unpriceable_usd_cell. This "
                               "rung is gated on its DOLLAR ceiling only, and a refusal must say so."),
    })

    # ---- R14 -------------------------------------------------------------------------------------------
    r14b_h = me["ref_gpu_h_per_species"] * R14B_SPECIES
    r14b = price(r14b_h, plan_rate, rate_band)
    r14b.update(price_band([me["ref_gpu_h_per_species_band"][0] * R14B_SPECIES,
                            me["ref_gpu_h_per_species_band"][1] * R14B_SPECIES], plan_rate, rate_band))
    total_ns = me["recipe_per_species"]["total_ns"] * R14B_SPECIES
    r14b_usd_per_ns = r14b["plan_usd"] / total_ns
    r14b.update({
        "units": R14B_SPECIES,
        "unit": "matched cryptic-pocket ensemble (60 ns well-tempered metadynamics + 3 x 5 ns release)",
        "total_ns": total_ns,
        "usd_per_ns": _r(r14b_usd_per_ns, 6),
        "multiple_of_ladder_basis": _r(r14b_usd_per_ns / basis_usd_per_ns, 2),
        "multiple_of_buy_line": _r(r14b_usd_per_ns / buy_line, 2),
        "⛔_WOULD_BE_REFUSED_BY_THE_STANDING_RATE_LINE": bool(r14b_usd_per_ns >= buy_line),
        "★_and_that_refusal_is_a_BLOCKER_TO_SURFACE_not_a_price_to_pay": (
            "This rung's $/ns is %.4f against a buy line of %.6f — it would be REFUSED, and per CLAUDE.md §1 "
            "a refused row must NAME which ceiling it hit. ⚠ But the comparison is NOT like-for-like and "
            "must not be reported as drift: the line's basis is the 84,534-particle UNBIASED RBFE benchmark, "
            "and a PLUMED-biased leg does per-step HOST-CPU work the benchmark does not — measured on ONE "
            "instance at the metad->release boundary, same card, minutes apart (pricing.md §A.1). So the "
            "honest state is: there is no metadynamics-anchored basis in this repo, and until there is, this "
            "rung cannot be graded by the rate line at all. ⛔ REGISTERED GATE: do not launch R14-b until "
            "that is resolved. This is surfaced now rather than discovered at launch, and it is a decision "
            "for trimcrae, not a rule to loosen." % (r14b_usd_per_ns, buy_line)),
    })

    rungs = {
        "R13-a · fusion-junction SEQUENCE inventory at the CORRECTED junction": {
            "serves": "R13", "ref_gpu_h": 0.0, "plan_usd": 0.0, "range_usd": [0.0, 0.0],
            "where_it_runs": "CI / CPU (Ensembl is networked -> a GitHub Actions runner, CLAUDE.md §6)",
            "needs_authorization": False,
            "what_it_buys": ("the uniqueness + lysine/cysteine inventory across the CORRECTED junction, and "
                             "the explicit statement of which real residues the modelled LBD construct "
                             "(373-626) excludes from every geometry claim in the program"),
        },
        "R13-b · apo co-fold of the two corrected fusion constructs": dict(
            r13b, serves="R13", needs_authorization=True,
            where_it_runs="Vast, reference card; baked image (CLAUDE.md §6 — never build on a billing host)"),
        "R14-a · complete the anti-target panel + run its never-run self-control": {
            "serves": "R14", "ref_gpu_h": 0.0, "plan_usd": 0.0, "range_usd": [0.0, 0.0],
            "where_it_runs": "CI / CPU — smina, the identical 24 A box / exhaustiveness 8 protocol",
            "needs_authorization": False,
            "what_it_buys": ("MR/NR3C2 added to antitarget_panel.json (AR is already a target), the panel's "
                             "own cognate-ligand self-control run for the first time, and denovo_401 + the "
                             "carried candidates docked into both flagged receptors"),
        },
        "R14-b · matched AR/MR cryptic-pocket ensembles (+ the $0 detector)": dict(
            r14b, serves="R14", needs_authorization=True,
            where_it_runs="Vast; the detector itself is $0 CPU once frames exist"),
    }

    priced_plan = sum(v.get("plan_usd", 0.0) for v in rungs.values())
    priced_lo = sum(v.get("range_usd", [0, 0])[0] for v in rungs.values())
    priced_hi = sum(v.get("range_usd", [0, 0])[1] for v in rungs.values())

    return {
        "_title": "Bottom-up price for the two SCOPE rungs — R13 (fusion-context object) and R14 (AR/MR)",
        "_owner": "research/manuscripts/nr4a3-program-map.md §10.1 rows 9 and 10, and THE ORDERED PLAN",
        "_this_dispatches_nothing": True,
        "⛔_EXCLUDED_FROM_THE_PINNED_LADDER_TOTAL": (
            "deliberately, and for the same reason pricing.md §C excludes the 5a-KS confirmatory wedge and "
            "the reciprocal cycle: these are CLAIM-CEILING conditions, not steps of the gated 5a->5d spine, "
            "and no rung's GO gates them. The map LINKS to this artifact and never adds these into `Cum.`."),
        "market": {"plan_usd_per_reference_gpu_h": plan_rate,
                   "range_usd_per_reference_gpu_h": rate_band,
                   "ladder_basis_usd_per_ns": basis_usd_per_ns,
                   "approved_buy_line_usd_per_ns": _r(buy_line, 6),
                   "_source": "vast-ladder-repricing.json + inflight_usd_per_ns.APPROVED_USD_PER_NS — read "
                              "live so these rungs move with the ladder instead of freezing a rate"},
        "bases": {"cofold_per_model": cf, "metad_ensemble_per_species": me},
        "rungs": rungs,
        "totals_for_these_four_rungs_only": {
            "plan_usd": _r(priced_plan, 4), "range_usd": [_r(priced_lo, 4), _r(priced_hi, 4)],
            "_not_the_ladder": "DERIVED here from the rows above; it is NOT added to and does NOT move the "
                               "pinned ladder total, which vast_cost_model.py owns.",
        },
        "unpriceable": {
            "R13 · the FULL validation-requirement-5 object": (
                "⛔ NOT PRICED, and it must not be. Requirement 5 asks for a fusion-context ENSEMBLE plus "
                "full CRL/E2~Ub ensembles. Three separate things are missing before a number could mean "
                "anything: (1) no particle count exists anywhere in this repo for an ~890-residue chimera "
                "carrying a 264-residue prion-like IDR, and the binary NR4A3 complex's particle count is "
                "ALREADY recorded as unknown (pricing.md B); (2) nothing determines how many replicas a "
                "statement about a disordered region would need, and fusion_cofold.py's own honest prior is "
                "that an MSA-based predictor has NO cross-seam coevolution to work from; (3) the "
                "patient-level breakpoint is not pinned — nr4a3-exon-audit.json says only a primary "
                "breakpoint report can do that, and EMC carries several — so the OBJECT ITSELF is not "
                "uniquely defined yet. Pricing an ensemble over an undetermined object would be pricing a "
                "guess."),
            "R14 · the ENERGETIC (FEP) half": (
                "⛔ NOT PRICED, and it does not get its own rung. The SI asks for 'docking/FEP into their "
                "LBDs'. The FEP half IS `V4`'s instrument — the selectivity-ABFE that has never recovered a "
                "known selectivity answer across two pockets. Under the claim-ceiling rule a number from it "
                "could not raise R14 above 'unvalidated prediction', so pricing it here would create a "
                "SECOND home for a decision that already has one: §10.1 row 2, `V4`'s missing rung. It is "
                "downstream of row 2, not parallel to it."),
        },
    }


def main(argv):
    art = build()
    txt = json.dumps(art, indent=1, sort_keys=False)
    if "--check" in argv and os.path.exists(OUT_JSON):
        with open(OUT_JSON) as fh:
            if fh.read().strip() != txt.strip():
                print("[scope-rung-cost] ⛔ artifact does not reproduce from source", file=sys.stderr)
                return 1
        print("[scope-rung-cost] ✅ reproduces")
        return 0
    with open(OUT_JSON, "w") as fh:
        fh.write(txt + "\n")
    for name, r in art["rungs"].items():
        print("  %-62s %6.2f ref-GPU-h  $%.2f  (%s)" % (
            name[:62], r.get("ref_gpu_h", 0.0), r.get("plan_usd", 0.0),
            "no nod" if not r.get("needs_authorization") else "needs a nod"))
    t = art["totals_for_these_four_rungs_only"]
    print("[scope-rung-cost] these four rungs: $%.2f (%s) — EXCLUDED from the pinned ladder total"
          % (t["plan_usd"], t["range_usd"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
