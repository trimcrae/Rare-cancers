#!/usr/bin/env python3
"""valB_mini RESCOPE — both candidate calibrator designs, priced, powered, and stress-tested. $0 CPU.

The r0 verdict's step 4 is "rescope the calibrator to a >=2 kcal/mol signal". This module turns that sentence
into two fully specified designs with edge lists, leg counts, Vast-4090 costs and MEASURED power, so the choice
is made on arithmetic rather than on which one sounds better:

  (i)  a MULTI-EDGE CONGENERIC NETWORK on the Ciulli SMARCA2-VHL P-series, whose redundant path supplies
       CYCLE CLOSURE — a systematic-error detector that needs no experimental reference at all, and which this
       programme currently lacks entirely (no reverse legs existed, no redundant edge, so no closure);
  (ii) the HIGH-CONTRAST P1->P4 / P1->P5 pair (+2.53 / +2.99 kcal/mol), direct if the perturbation maps and via
       intermediate hops if it does not.

Nothing here is fabricated. Every alpha is read from `nr4a3-ternary-coop-prereg.json`, where each was
primary-source verified (Nat Commun 2025 PMC12480974 Supplementary Table 1, SI archived + checksummed); every
cost comes from `vast_cost_model.LADDER_REFERENCE_GPU_H` at the $0.137/reference-GPU-hour planning rate; every
P(PASS) comes from calling the shipped `ternary_fep_reduce.calibration_gate`. The one thing this module cannot
supply offline is the LIGAND CHEMISTRY (are the P-series pairs congeneric and mappable?) — that needs RCSB,
which the dev sandbox's egress proxy blocks, so it is fetched on a CI runner and reported as a status when
absent rather than assumed.

Two findings that fall out of the arithmetic and that a prose design would have missed:

  * ONCE THE TARGET EXCEEDS ~2 kcal/mol THE ACCURACY MARGIN STOPS BINDING and the gate's power is set entirely
    by the between-replicate SD (valb_gate_audit, audit F: the ceiling is exactly P(sample SD <= 0.75)). So
    beyond ~2 kcal/mol a bigger signal buys nothing and only PRECISION does.
  * WHICH MEANS MULTI-HOP PATHS CAN BE A NET LOSS. Signal adds linearly across hops but SD adds in quadrature,
    so a 2-hop route to +2.53 has HIGHER power than the direct +0.944 edge only if each hop's SD is below
    ~0.71x the direct edge's. Hops are justified by UNMAPPABILITY, not by the bigger endpoint separation.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_fep_reduce as red  # noqa: E402
import vast_cost_model as vcm  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RT_KCAL = 0.5925                       # R*T at 298.15 K, matching the prereg's ddG_coop_exp formula
USD_PER_REF_GPU_H = 0.137              # pricing.md section A, best-10-offer planning rate
# valB_mini = 1 ternary edge x 3 replicas = 56-72 reference GPU-h (vast_cost_model.LADDER_REFERENCE_GPU_H).
# One replicate of one edge is a binary leg + a ternary leg, so:
REF_GPU_H_PER_EDGE_REPLICATE = sum(vcm.LADDER_REFERENCE_GPU_H["valB_mini (1 ternary edge, 3 replicas)"]) / 2.0 / 3.0
# A solvent leg is ~5.3k particles against the ternary leg's ~146k (measured: the r0 solvent leg stored 120 of
# 5304 atoms, the ternary leg 7388 of 141968). It is also NOT needed for ddG_coop, which is ternary - binary
# with the solvent morph cancelling identically. Carried at a nominal cost so no design silently omits it.
REF_GPU_H_PER_SOLVENT_LEG = 0.5
TRIALS = 20000


def _load_alphas():
    """alpha values + PDBs, read from the prereg. Never hardcoded here: the prereg is where provenance lives."""
    p = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")
    panel = json.load(open(p))["calibration"]["layer1_vhl_panel"]
    out = {}
    for s in panel.get("candidate_systems", []):
        if s.get("measured_alpha") and s.get("id", "").startswith("smarca2_p"):
            out[s["id"]] = {"alpha": float(s["measured_alpha"]), "pdb": s.get("pdb"),
                            "ligand_ccd": s.get("ligand_ccd")}
    return out, panel.get("observable", {}).get("name"), panel.get("prespecified_ordinal_tiers", {})


def ddg_coop(alpha_hi, alpha_lo):
    """ddG_coop for the hi->lo morph = -RT ln(alpha_lo/alpha_hi) = RT ln(alpha_hi/alpha_lo). Positive when
    cooperativity DROPS across the morph, matching the frozen Wurz convention (+0.944 for 12.8 -> 2.6)."""
    return RT_KCAL * math.log(alpha_hi / alpha_lo)


def pass_probability(target, per_edge_sd, n_edges_in_series=1, n_replicates=5, extended=True, mu_scale=1.0):
    """P(PASS) through the REAL gate for a design whose measured quantity is the SUM of `n_edges_in_series`
    independent hops. Signal adds linearly (it is already in `target`); the replicate SD of the SUM adds in
    quadrature, sqrt(n_hops) * per_edge_sd. `mu_scale` = 0 gives the null method, 1 an exactly-accurate one."""
    sd = per_edge_sd * math.sqrt(n_edges_in_series)
    rng = random.Random(1729)
    hits = 0
    for _ in range(TRIALS):
        vals = [rng.gauss(target * mu_scale, sd) for _ in range(n_replicates)]
        if red.calibration_gate(vals, target, extended=extended)["decision"] == "PASS":
            hits += 1
    return round(100.0 * hits / TRIALS, 2)


def _price(n_edges, n_replicates, include_solvent=True):
    """Leg count and Vast-4090 cost for a design.

    THE CANCELLATION IDENTITY, APPLIED HONESTLY. STRATEGY's identity — 'the binary and solvent legs are
    paralogue-independent, so a panel is N ternary legs + 1 shared binary + 1 shared solvent, not N edges' —
    is about ONE ligand pair against SEVERAL TARGETS. It does NOT apply within a congeneric network on a single
    target: there every edge is a different alchemical transformation, so every edge needs its own binary leg.
    Claiming the sharing here would underprice these designs by ~2x. What the identity DOES buy is stated as
    `shared_if_extended_to_a_second_target`: if any of these edges is later re-run against a second known-answer
    system (BRD4-VHL), its binary legs transfer unchanged, because binary_vhl never sees the target."""
    ternary = n_edges * n_replicates
    binary = n_edges * n_replicates
    solvent = (n_edges * n_replicates) if include_solvent else 0
    gpu_h = (ternary + binary) * REF_GPU_H_PER_EDGE_REPLICATE / 2.0 + solvent * REF_GPU_H_PER_SOLVENT_LEG
    return {"n_edges": n_edges, "n_replicates": n_replicates,
            "legs": {"ternary": ternary, "binary": binary, "solvent": solvent,
                     "total": ternary + binary + solvent},
            "reference_gpu_h": round(gpu_h, 1),
            "usd_mid": round(gpu_h * USD_PER_REF_GPU_H, 2),
            "usd_range": [round(gpu_h * USD_PER_REF_GPU_H * 0.36, 2), round(gpu_h * USD_PER_REF_GPU_H * 2.5, 2)],
            "_range_basis": "the same 0.36x-2.5x spread pricing.md carries on the valB_mini edge ($8.8, $3.2-22)",
            "shared_if_extended_to_a_second_target": ("the %d binary legs are target-independent and would "
                                                      "transfer unchanged to a BRD4-VHL replication" % binary)}


def design_i_closure_network(alphas):
    """(i) MULTI-EDGE CONGENERIC NETWORK WITH CYCLE CLOSURE.

    The minimum network that closes is a triangle: two hops plus the direct edge they span. The closure
    residual R = ddG(A->B) + ddG(B->C) - ddG(A->C) is identically zero for an exact method REGARDLESS of the
    experimental alphas, so it detects systematic error WITHOUT a reference measurement — the one instrument
    this programme has never had. It also gives a MEASURED RESOLUTION FLOOR for the ddG_coop cycle: |R| is a
    direct, self-contained statement of what the workflow can and cannot resolve, and it is a publishable
    result whether or not the calibration itself passes."""
    tri = []
    ids = sorted(alphas)
    for a in ids:
        for b in ids:
            for c in ids:
                if len({a, b, c}) != 3:
                    continue
                if alphas[a]["alpha"] <= alphas[b]["alpha"] <= alphas[c]["alpha"]:
                    continue                     # keep one orientation: strictly decreasing alpha a > b > c
                if not (alphas[a]["alpha"] > alphas[b]["alpha"] > alphas[c]["alpha"]):
                    continue
                span = ddg_coop(alphas[a]["alpha"], alphas[c]["alpha"])
                hops = [ddg_coop(alphas[a]["alpha"], alphas[b]["alpha"]),
                        ddg_coop(alphas[b]["alpha"], alphas[c]["alpha"])]
                tri.append({
                    "triangle": [a, b, c],
                    "pdbs": [alphas[a]["pdb"], alphas[b]["pdb"], alphas[c]["pdb"]],
                    "edges": ["%s->%s" % (a, b), "%s->%s" % (b, c), "%s->%s (direct, closes the loop)" % (a, c)],
                    "hop_targets_kcal": [round(h, 3) for h in hops],
                    "direct_target_kcal": round(span, 3),
                    "smallest_hop_kcal": round(min(hops), 3),
                    "closure_identity": "ddG(%s->%s) + ddG(%s->%s) - ddG(%s->%s) == 0 for an exact method"
                                        % (a, b, b, c, a, c),
                })
    tri.sort(key=lambda t: (-t["smallest_hop_kcal"], -t["direct_target_kcal"]))
    return {"_design": "(i) multi-edge congeneric network -> CYCLE CLOSURE + a measured resolution floor",
            "_why_it_is_different_in_kind": "closure is reference-free. Every other check this lane has "
                                            "(accuracy vs alpha, replicate SD, MBAR overlap) either needs the "
                                            "experimental answer or measures precision only. A nonzero closure "
                                            "residual is proof of systematic error with nothing else assumed.",
            "_selection_rule": "prefer the triangle whose SMALLEST hop is largest — the weakest hop sets how "
                               "much of the closure residual is signal rather than noise",
            "candidate_triangles": tri,
            "recommended": tri[0] if tri else None,
            "cost_n1_scout": _price(3, 1),
            "cost_n3": _price(3, 3),
            "cost_n5": _price(3, 5)}


def design_ii_high_contrast(alphas):
    """(ii) THE HIGH-CONTRAST PAIR, direct or hopped.

    Direct P1->P4 (+2.53) or P1->P5 (+2.99) is ONE edge, the cheapest design on the table. Its whole risk is
    chemical: a 93 -> 0.6 cooperativity span is a large linker/exit-vector change, and if LOMAP/Kartograf cannot
    map it the edge does not converge at any price. The hopped fallback removes that risk and adds a different
    one, quantified in `power_vs_per_edge_sd`: two hops multiply the replicate SD by sqrt(2), and past ~2
    kcal/mol the gate is SD-limited, so hopping can LOWER the pass probability even while raising the signal."""
    p = alphas
    routes = []
    for lo in ("smarca2_p4", "smarca2_p5"):
        if "smarca2_p1" not in p or lo not in p:
            continue
        t = ddg_coop(p["smarca2_p1"]["alpha"], p[lo]["alpha"])
        routes.append({"route": "smarca2_p1 -> %s (DIRECT)" % lo, "n_hops": 1,
                       "pdbs": [p["smarca2_p1"]["pdb"], p[lo]["pdb"]],
                       "target_kcal": round(t, 3),
                       "risk": "unmappable perturbation — a 93 -> %.1f span is a large linker change; "
                               "congenericity is UNVERIFIED until the RCSB ligand fetch returns"
                               % p[lo]["alpha"],
                       "cost_n3": _price(1, 3)})
        for mid in ("smarca2_p2", "smarca2_p3"):
            if mid not in p:
                continue
            hops = [ddg_coop(p["smarca2_p1"]["alpha"], p[mid]["alpha"]),
                    ddg_coop(p[mid]["alpha"], p[lo]["alpha"])]
            routes.append({"route": "smarca2_p1 -> %s -> %s (HOPPED)" % (mid, lo), "n_hops": 2,
                           "pdbs": [p["smarca2_p1"]["pdb"], p[mid]["pdb"], p[lo]["pdb"]],
                           "target_kcal": round(sum(hops), 3),
                           "hop_targets_kcal": [round(h, 3) for h in hops],
                           "risk": "SD of the SUM is sqrt(2)x a single hop's; past ~2 kcal/mol the gate is "
                                   "SD-limited, so this is only a win if each hop converges better than the "
                                   "direct edge would (per-hop SD below ~0.71x)",
                           "cost_n3": _price(2, 3)})
    return {"_design": "(ii) high-contrast P1->P4 / P1->P5, direct or via intermediate congeneric hops",
            "routes": routes}


def power_table(alphas):
    """P(PASS) through the real gate for every design x plausible per-edge SD, plus the null-method rate at the
    same settings. This is the table the choice should actually be made on."""
    rows = []
    cases = [("current valB_mini (Wurz 1->4, 1 hop)", 0.944, 1),
             ("P1->P4 direct (1 hop)", ddg_coop(93.0, 1.3), 1),
             ("P1->P5 direct (1 hop)", ddg_coop(93.0, 0.6), 1),
             ("P1->P3->P5 hopped (2 hops)", ddg_coop(93.0, 0.6), 2),
             ("P1->P2->P4 hopped (2 hops)", ddg_coop(93.0, 1.3), 2)]
    for label, tgt, hops in cases:
        for sd in (0.3, 0.5, 0.7):
            rows.append({"design": label, "target_kcal": round(tgt, 3), "n_hops": hops,
                         "per_edge_replicate_sd": sd,
                         "effective_sd_of_the_measured_quantity": round(sd * math.sqrt(hops), 3),
                         "pass_pct_accurate_n5": pass_probability(tgt, sd, hops, 5, True, 1.0),
                         "pass_pct_null_n5": pass_probability(tgt, sd, hops, 5, True, 0.0)})
    return {"_what": "P(PASS) at n=5 through ternary_fep_reduce.calibration_gate (corrected anti-null rule)",
            "_read_this_first": "compare rows at EQUAL per-edge SD. A 2-hop design at per-edge SD s is "
                                "evaluated at an effective SD of s*sqrt(2), which is why hops can lose.",
            "rows": rows}


def futility_stopping_saving():
    """Wiring adaptive_certify into the ternary ladder — evaluated, not assumed.

    WHAT IT CAN LEGITIMATELY DO HERE: stop early for FUTILITY. If the anytime-valid UPPER bound on ddG_coop is
    already below target - 1.0, the frozen accuracy criterion is unreachable however many replicates are bought,
    so the remaining ones are wasted money. Because the bound is a confidence SEQUENCE it stays valid under
    repeated looks and data-dependent stopping, which a fixed-n gate peeked at repeatedly does not.

    WHAT IT MUST NOT DO HERE: license an early PASS. The frozen rule's PASS also requires a between-replicate SD
    ceiling and clean diagnostics on every leg; an anytime bound on the MEAN cannot speak to either, and an
    early-success stop would be an amendment to a preregistered rule, not a scheduling choice. So the proposed
    wiring is futility-only, which — exactly like the anti-null fix — can only ever REDUCE what gets bought and
    can never manufacture a favourable verdict.

    Measured below against the real r0, and against the scenarios that matter."""
    try:
        import adaptive_certify as ac
    except Exception as e:  # noqa: BLE001
        return {"status": "adaptive_certify unavailable: %s" % e}
    target, bar = 0.944, 0.944 - red.GATE_ABS_ERR_PASS      # unreachable-accuracy bar
    rows = []
    for label, mu in (("r0 is representative (mu = -0.534)", -0.534), ("null (mu = 0)", 0.0),
                      ("method exactly right (mu = +0.944)", target)):
        for sd in (0.5, 0.7):
            rng = random.Random(31337)
            legs_seq, legs_fixed, stopped = 0, 0, 0
            for _ in range(4000):
                vals = [-0.534]                             # r0 is already bought in every world
                n_bought = 1
                fired = False
                for _ in range(4):                          # replicates 2..5
                    vals.append(rng.gauss(mu, sd))
                    n_bought += 1
                    if n_bought >= 2:
                        m = sum(vals) / len(vals)
                        ub = ac.anytime_upper_bound(m, len(vals), sd, 0.05)
                        if ub < bar:                        # even optimistically the margin cannot be met
                            fired = True
                            break
                legs_seq += n_bought
                legs_fixed += 5
                stopped += 1 if fired else 0
            rows.append({"scenario": label, "replicate_sd": sd,
                         "mean_replicates_bought_sequential": round(legs_seq / 4000.0, 2),
                         "replicates_bought_fixed": 5,
                         "futility_fired_pct": round(100.0 * stopped / 4000.0, 1),
                         "saving_pct": round(100.0 * (1 - legs_seq / float(legs_fixed)), 1)})
    return {"_proposal": "wire adaptive_certify's anytime-valid UPPER bound as a FUTILITY stop on the ternary "
                         "replicate ladder; leave the PASS criterion untouched",
            "_why_it_is_not_an_amendment": "it can only stop spending sooner. It never converts a non-PASS into "
                                           "a PASS, so it needs no change to the frozen rule.",
            "_honest_limit": "the saving is real only when the truth is far from target; when the method is "
                             "accurate the rule almost never fires and the ladder costs exactly what it did.",
            "rows": rows}


def rev_leg_decision_tree():
    """The rescope choice is NOT independent of the reverse leg that is in flight. Both branches, specified now,
    so the next step is already decided when it lands."""
    return {
        "_pending": "|dG_fwd + dG_rev| on the valB r0 ternary (and binary) legs — the preregistered antisymmetry "
                    "check, still null on all three legs because the rev direction was unreachable until "
                    "2026-07-25",
        "branch_A_small": {
            "trigger": "|dG_fwd + dG_rev| <= ~0.3 kcal/mol (no hysteresis)",
            "means": "the alchemical path is internally consistent and sampling along lambda is adequate. The "
                     "1.478 kcal/mol systematic is therefore NOT a path/sampling artifact — it lives in the "
                     "MODEL (SMARCA4->SMARCA2 homology substitution, NAGL charges, force field, protonation) "
                     "or in the REFERENCE DATA (alpha_SPR -> ddG_coop conversion; an apparent cooperativity is "
                     "not a Kd-derived thermodynamic one).",
            "action": "RESCOPE. Design (i) on the Ciulli P-series is then strictly dominant, because it "
                      "attacks BOTH candidate causes at once: the P-series has FIVE solved SMARCA2-VHL "
                      "ternaries, so the homology-model term disappears entirely, and the closure residual "
                      "tests the remaining systematic without needing the reference data to be right.",
        },
        "branch_B_large": {
            "trigger": "|dG_fwd + dG_rev| > ~1.0 kcal/mol (real hysteresis)",
            "means": "a slow degree of freedom orthogonal to lambda — an interface substate the replica "
                     "exchange does not traverse — despite every MBAR diagnostic reading clean. Note the one "
                     "diagnostic that already leans this way: replica mixing 0.8915 against a 0.90 ceiling, "
                     "recorded as MARGINAL.",
            "action": "DO NOT RESCOPE YET. A larger target measured through a hysteretic path is still wrong, "
                      "so buying a new calibrator would buy a better-looking wrong number. Fix the protocol "
                      "FIRST, and test the fix on the edge already paid for: more lambda windows across the "
                      "0.10 bottleneck at pair 4-5, a softer softcore schedule, longer pre-equilibration, or "
                      "interface-aware enhanced sampling. Only once |dG_fwd + dG_rev| is small does the "
                      "rescope design above become the right next spend.",
        },
        "shared_by_both_branches": "the closure network of design (i) is worth buying under EITHER branch, "
                                   "because the closure residual is the instrument that tells the two apart "
                                   "for any future edge without waiting for a reverse leg each time.",
    }


def main():
    alphas, observable, tiers = _load_alphas()
    report = {
        "_what": "valB_mini calibrator rescope — two designs, priced and powered",
        "_date": "2026-07-25",
        "_alpha_provenance": "nr4a3-ternary-coop-prereg.json -> calibration.layer1_vhl_panel (each system "
                             "primary-source verified; Nat Commun 2025 PMC12480974 Supp. Table 1, SI archived "
                             "and checksummed). Nothing in this file re-derives or invents an alpha.",
        "_observable": observable,
        "_assay_warning": "the P-series alphas are alpha_TR-FRET (an APPARENT cooperativity, IC50 ratio) while "
                          "the current valB target is alpha_SPR. Each EDGE is same-assay, which is what a "
                          "relative calibration needs, but a P-series result must never be reported as "
                          "continuous with the Wurz number.",
        "_pricing": {"usd_per_reference_gpu_h": USD_PER_REF_GPU_H,
                     "ref_gpu_h_per_edge_replicate": round(REF_GPU_H_PER_EDGE_REPLICATE, 1),
                     "basis": "vast_cost_model.LADDER_REFERENCE_GPU_H['valB_mini (1 ternary edge, 3 replicas)'] "
                              "= 56-72 ref GPU-h for 3 replicates of one edge"},
        "panel": alphas,
        "resolution_floor_today": {
            "statistical_per_leg_kcal": 0.045,
            "statistical_on_the_cycle_kcal": round(0.045 * math.sqrt(2), 3),
            "observed_total_error_kcal": 1.478,
            "ratio": round(1.478 / (0.045 * math.sqrt(2)), 1),
            "reading": "the cycle's STATISTICAL resolution is ~0.06 kcal/mol; its TOTAL error on the single "
                       "available observation is 1.478 — a ~23x gap, which is the finding. A resolution floor "
                       "is not yet MEASURED, because measuring one needs the reverse legs (in flight) and a "
                       "redundant edge (design (i)); r0 alone gives a single-point lower bound, not a floor.",
        },
        "design_i_closure_network": design_i_closure_network(alphas),
        "design_ii_high_contrast": design_ii_high_contrast(alphas),
        "power": power_table(alphas),
        "adaptive_futility_stopping": futility_stopping_saving(),
        "rev_leg_decision_tree": rev_leg_decision_tree(),
        "open_blocker": {
            "what": "ligand chemistry for 9HYN / 7Z77 / 9HYB / 9HYO / 9HYP — are the pairs congeneric and "
                    "mappable, and is the net charge conserved across each edge?",
            "why_it_decides_everything": "an unmappable edge does not converge at any price, and a "
                                         "charge-changing edge needs a different (and much more expensive) "
                                         "treatment. Until this returns, every edge below is a CANDIDATE.",
            "how": "$0 RCSB fetch on a CI runner (the dev sandbox's egress proxy blocks RCSB), then RDKit MCS "
                   "in the pre-baked triskit23/ternary-fep image, which already carries rdkit + lomap2 + "
                   "kartograf — the same mapper the production edge would use.",
        },
    }
    out = os.path.join(HERE, "valb-rescope-design.json")
    json.dump(report, open(out, "w"), indent=2)
    print(json.dumps({k: report[k] for k in ("resolution_floor_today", "power")}, indent=2)[:6000])
    print("\n[rescope] wrote %s" % out)
    return report


if __name__ == "__main__":
    main()
