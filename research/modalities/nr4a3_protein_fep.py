#!/usr/bin/env python3
"""Alchemical PROTEIN point-mutation free-energy engine — the missing 5a-KS wedge engine.

WHY THIS FILE EXISTS
--------------------
`STRATEGY.md` designates the **5a-KS reciprocal target-surface mutation wedge** as the program's
*causal kill-switch* — the one designed-in falsification test, and the paper's primary causal
result. Until 2026-07-24 that rung was priced (~$5-10) off a capability **this repository does not
have**:

    OpenFE's RelativeHybridTopologyProtocol (the engine behind nr4a3_rbfe.py and
    nr4a3_ternary_fep.py) builds its hybrid topology from a LIGAND-TO-LIGAND ATOM MAPPING
    (LOMAP/Kartograf). It maps small-molecule atoms. It cannot mutate a protein residue.

So the wedge had no engine at all, and a ladder rung with no engine is not a cheap rung — it is an
unscoped one. This file is the engine, built after trimcrae's 2026-07-24 decision to scope one
rather than descope the wedge or substitute an MM-GBSA proxy.

WHAT THE WEDGE ACTUALLY COMPUTES
--------------------------------
For a target-surface mutation `m` (e.g. NR4A3 R412A), run the SAME alchemical protein mutation in
two environments and subtract:

    ddG_neo-interface^m  =  dG_mut^ternary  -  dG_mut^binary

The subtraction is the point. A mutation that costs the same in both environments is telling you
about protein stability, not about the interface. Only the DIFFERENCE isolates the free-energy
contribution the mutated residue makes to the *neo-interface* formed in the ternary complex. That
is the causal claim: perturb the surface, and the ternary-specific signal must move with it.

This is the same thermodynamic-cycle shape as ternary_coop.ddg_coop (ternary leg minus binary leg),
so we reuse that helper rather than re-deriving the arithmetic.

ENGINE CHOICE (and why not the obvious alternatives)
----------------------------------------------------
`perses.app.relative_point_mutation_setup.PointMutationExecutor` + perses'
`HybridTopologyFactory`, sampled with openmmtools' `MultiStateSampler` and reduced with MBAR.

  * It is OpenMM-native, so it inherits this repo's existing GPU/spot/checkpoint infrastructure
    rather than introducing a second MD stack.
  * It is the same hybrid-topology *lineage* OpenFE already vendors for the ligand lane, so the
    alchemical machinery under the wedge is the machinery already exercised here — the new surface
    is the residue-mutation topology construction, not the sampling engine.
  * It is published and benchmarked for protein mutations (Rufa et al.), so the wedge rests on an
    established method rather than a bespoke one.

Rejected: pmx (GROMACS-centric — would mean a second MD engine and a second force-field pipeline);
FoldX/Rosetta ddG (empirical, not a free energy — that is the proxy option trimcrae declined);
hand-rolling a dual-topology factory (all of perses' correctness risk, none of its validation).

TWO BLOCKERS THIS FILE MUST CLEAR — BOTH ARE ENCODED AS HARD GUARDS
--------------------------------------------------------------------
1. **CROSS-LANE CHARGE MISMATCH.** The binary RBFE lane charges its small molecule with AM1-BCC
   (AmberTools sqm); every ternary/endpoint lane charges with NAGL (see md_settings.py's DOCUMENTED
   DEVIATION block). Those are genuinely different Hamiltonians for the same ligand. A ternary-minus-
   binary subtraction across lanes with different ligand charges is not a thermodynamic cycle — the
   ligand's own parameters fail to cancel, and the residual lands in the wedge looking like signal.
   `assert_charge_consistency` therefore HARD-FAILS a wedge whose two legs disagree, and both result
   JSONs record the pinned method. This is not a style rule; an un-pinned wedge is uninterpretable.

2. **NET-CHARGE-CHANGING MUTATIONS.** Alchemically mutating a charged residue to a neutral one
   (R->A, K->A, D->A, E->A) changes the net charge of the periodic box. Under Ewald/PME that is a
   well-known artifact source: the neutralising background plasma shifts the electrostatic free
   energy by a system-size-dependent amount that does NOT cancel between two differently-sized boxes.
   This is not hypothetical for us: **R412 is one of the repo's own seven selectivity handles**, so
   the most obvious wedge to reach for is charge-changing. `classify_mutation` flags these and
   `plan_wedge` refuses to plan one unless an explicit correction strategy is chosen (co-alchemical
   counterion, or matched-box finite-size correction). Silently running R412A would produce a number
   that looks like a causal result and is an artifact.

VALIDATION STATUS — READ THIS BEFORE QUOTING ANY NUMBER FROM THIS ENGINE
------------------------------------------------------------------------
**UNVALIDATED.** No leg has run. Per the repo's pilot-one-leg-first rule and the reviewer's
known-answer-benchmark requirement, this engine must clear a **known-answer protein-mutation
benchmark** (a published, experimentally-measured protein-protein interface ddG) BEFORE it gates
anything or contributes a number to the manuscript. `KNOWN_ANSWER_BENCHMARKS` below carries the
candidate set. Until that passes, this file is infrastructure, not evidence.

The pure planning/arithmetic/guard helpers here are importable and tested on CPU with no MD stack
(tests/test_protein_fep.py); the MD entry points import lazily and only work in the `protfep` conda
environment on a GPU.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import md_settings  # noqa: E402
import ternary_coop as tcoop  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUTPUT_DIR", HERE)

# --------------------------------------------------------------------------------------
# Residue chemistry
# --------------------------------------------------------------------------------------
# Formal charge at pH 7 of each standard residue's side chain. Used ONLY to decide whether a
# mutation changes the net charge of the box — see blocker 2 above. HIS is listed at 0 because the
# force field's default protonation (HIE/HID) is neutral; a HIP-protonated His mutation must be
# declared explicitly rather than inferred from the sequence.
RESIDUE_CHARGE = {
    "ALA": 0, "ARG": +1, "ASN": 0, "ASP": -1, "CYS": 0, "GLN": 0, "GLU": -1,
    "GLY": 0, "HIS": 0, "HIP": +1, "ILE": 0, "LEU": 0, "LYS": +1, "MET": 0,
    "PHE": 0, "PRO": 0, "SER": 0, "THR": 0, "TRP": 0, "TYR": 0, "VAL": 0,
}

ONE_TO_THREE = {
    "A": "ALA", "R": "ARG", "N": "ASN", "D": "ASP", "C": "CYS", "Q": "GLN", "E": "GLU",
    "G": "GLY", "H": "HIS", "I": "ILE", "L": "LEU", "K": "LYS", "M": "MET", "F": "PHE",
    "P": "PRO", "S": "SER", "T": "THR", "W": "TRP", "Y": "TYR", "V": "VAL",
}

# Mutations perses cannot build cleanly. PRO has no backbone amide H and a fused ring, and GLY has
# no CB, so a hybrid topology across either is not a side-chain swap but a backbone change. These
# are refused rather than silently attempted.
BACKBONE_ALTERING = {"PRO", "GLY"}

# Charge-change correction strategies. "none" is only legitimate for a charge-CONSERVING mutation.
CHARGE_CORRECTIONS = ("none", "coalchemical_ion", "finite_size_correction")


class MutationError(ValueError):
    """Raised for a mutation this engine refuses to plan or build."""


def parse_mutation(spec):
    """Parse 'A:R412A' (chain:WT-resid-MUT) into a dict. Pure.

    One-letter WT/mutant codes are used because that is how the selectivity handles are written
    everywhere else in this repo (L406, T407, R412 ...), so the wedge spec reads the same as the
    handle it perturbs.
    """
    if not isinstance(spec, str) or ":" not in spec:
        raise MutationError(f"mutation spec must be 'CHAIN:WT<resid>MUT' (e.g. 'A:R412A'), got {spec!r}")
    chain, _, body = spec.partition(":")
    chain = chain.strip()
    body = body.strip().upper()
    if not chain:
        raise MutationError(f"empty chain in mutation spec {spec!r}")
    if len(body) < 3:
        raise MutationError(f"malformed mutation body {body!r} in {spec!r}")
    wt_letter, mut_letter, resid_str = body[0], body[-1], body[1:-1]
    if not resid_str.isdigit():
        raise MutationError(f"residue number {resid_str!r} in {spec!r} is not an integer")
    for letter in (wt_letter, mut_letter):
        if letter not in ONE_TO_THREE:
            raise MutationError(f"unknown one-letter residue code {letter!r} in {spec!r}")
    wt, mut = ONE_TO_THREE[wt_letter], ONE_TO_THREE[mut_letter]
    if wt == mut:
        raise MutationError(f"{spec!r} is a null mutation (WT == mutant); the wedge would be identically zero")
    return {"spec": spec, "chain": chain, "resid": int(resid_str), "wt": wt, "mutant": mut,
            "wt_letter": wt_letter, "mutant_letter": mut_letter}


def net_charge_change(mutation):
    """Net formal charge change (mutant - WT) of a parsed mutation. Pure."""
    return RESIDUE_CHARGE[mutation["mutant"]] - RESIDUE_CHARGE[mutation["wt"]]


def classify_mutation(spec):
    """Classify a mutation for buildability and charge-artifact risk. Pure.

    Returns the parsed mutation augmented with `charge_change`, `charge_changing`, `buildable`, and
    a human-readable `risk`. This is the function that keeps a plausible-looking artifact (R412A)
    from being mistaken for a causal result.
    """
    m = parse_mutation(spec)
    dq = net_charge_change(m)
    m["charge_change"] = dq
    m["charge_changing"] = dq != 0
    backbone = {m["wt"], m["mutant"]} & BACKBONE_ALTERING
    m["buildable"] = not backbone
    if backbone:
        m["risk"] = (f"REFUSED — {'/'.join(sorted(backbone))} alters the backbone (PRO has no amide H and a "
                     f"fused ring; GLY has no CB), so this is not a side-chain swap and perses cannot build a "
                     f"clean hybrid residue for it.")
    elif dq != 0:
        m["risk"] = (f"CHARGE-CHANGING (dq = {dq:+d}) — under PME the neutralising background plasma shifts the "
                     f"electrostatic free energy by a system-size-dependent amount that does NOT cancel between "
                     f"the ternary and binary boxes (they are different sizes). Requires an explicit correction "
                     f"strategy; running it uncorrected yields an artifact that looks like interface signal.")
    else:
        m["risk"] = "charge-conserving side-chain swap — the standard, well-behaved case for alchemical mutation FEP."
    return m


# --------------------------------------------------------------------------------------
# Charge-model consistency (blocker 1)
# --------------------------------------------------------------------------------------
def assert_charge_consistency(ternary_charge_method, binary_charge_method):
    """HARD-FAIL a wedge whose two legs charge the small molecule differently. Pure.

    The wedge is a subtraction. If the ligand carries AM1-BCC charges in one leg and NAGL charges in
    the other, the ligand's own parameters do not cancel and the residual contaminates the wedge.
    md_settings.py registers this exact split as a DOCUMENTED DEVIATION between the binary RBFE lane
    (am1bcc) and the ternary lane (nagl), which is precisely why this guard exists.
    """
    t = (ternary_charge_method or "").strip().lower()
    b = (binary_charge_method or "").strip().lower()
    if not t or not b:
        raise MutationError("both legs must declare a charge method; an unrecorded charge model makes the "
                            "wedge uninterpretable after the fact")
    if t != b:
        raise MutationError(
            f"CROSS-LANE CHARGE MISMATCH: ternary leg uses {t!r} but binary leg uses {b!r}. The wedge "
            f"ddG_ternary - ddG_binary is only a thermodynamic cycle if the ligand Hamiltonian is identical in "
            f"both legs. Pin ONE method (md_settings.CHARGE_METHOD = {md_settings.CHARGE_METHOD!r}) for both "
            f"legs and re-run; do NOT subtract these.")
    return t


# --------------------------------------------------------------------------------------
# Wedge planning
# --------------------------------------------------------------------------------------
def plan_wedge(spec, n_replicas=3, charge_method=None, charge_correction="none", allow_charge_change=False):
    """Plan the legs for one reciprocal mutation wedge. Pure — no MD, no GPU, no network.

    A wedge is 2 environments (ternary, binary) x n_replicas independent legs. Replicates are
    independent seeds, not extra lambda windows: the wedge's error bar must be a between-replicate
    SD, because that is the only estimator that captures the setup-to-setup variance that dominates
    a mutation in a large assembly.
    """
    m = classify_mutation(spec)
    if not m["buildable"]:
        raise MutationError(m["risk"])
    if charge_correction not in CHARGE_CORRECTIONS:
        raise MutationError(f"charge_correction must be one of {CHARGE_CORRECTIONS}, got {charge_correction!r}")
    if m["charge_changing"]:
        if not allow_charge_change:
            raise MutationError(
                f"{spec} is charge-changing (dq = {m['charge_change']:+d}) and would be run uncorrected. "
                f"{m['risk']} Pass allow_charge_change=True together with a charge_correction other than 'none' "
                f"once you have chosen how to handle it. NOTE: R412 is one of this repo's seven selectivity "
                f"handles, so this is the default trap, not an edge case — prefer a charge-conserving wedge "
                f"(e.g. a hydrophobic handle) for the FIRST causal test.")
        if charge_correction == "none":
            raise MutationError(f"{spec} is charge-changing; charge_correction='none' is not a legitimate "
                                f"choice for it. Use one of {CHARGE_CORRECTIONS[1:]}.")
    elif charge_correction != "none":
        raise MutationError(f"{spec} is charge-conserving; charge_correction={charge_correction!r} would apply "
                            f"an unnecessary correction. Use 'none'.")
    if n_replicas < 2:
        raise MutationError("n_replicas must be >= 2 — a single leg gives no between-replicate SD, and an "
                            "MBAR standard error on one leg understates the real uncertainty of a mutation in a "
                            "large assembly.")
    cm = (charge_method or md_settings.CHARGE_METHOD).strip().lower()
    legs = []
    for env in ("ternary", "binary"):
        for r in range(n_replicas):
            legs.append({
                "leg_id": f"wedge_{m['chain']}{m['wt_letter']}{m['resid']}{m['mutant_letter']}_{env}_r{r}",
                "environment": env,
                "mutation": m["spec"],
                "replicate": r,
                "charge_method": cm,
                "charge_correction": charge_correction,
            })
    return {
        "mutation": m,
        "n_replicas": n_replicas,
        "charge_method": cm,
        "charge_correction": charge_correction,
        "legs": legs,
        "n_legs": len(legs),
        "engine": "perses.PointMutationExecutor + openmmtools.MultiStateSampler + MBAR",
        "validated": False,
        "validation_note": ("UNVALIDATED — this engine has never completed a leg. It must clear a known-answer "
                            "protein-mutation benchmark before any number it produces enters the manuscript."),
    }


def wedge_ddg(dg_ternary, dg_binary):
    """The wedge itself: ddG_neo-interface = dG_mut^ternary - dG_mut^binary. Pure.

    Delegates to ternary_coop.ddg_coop because it is the identical cycle shape (ternary leg minus
    binary leg) already used for cooperativity — the only difference is that the alchemical
    transformation is a protein mutation rather than a ligand morph. Reusing it keeps one definition
    of the subtraction in the repo instead of two that can drift.
    """
    return tcoop.ddg_coop(dg_ternary, dg_binary)


def summarize_wedge(ternary_dgs, binary_dgs, charge_method_ternary, charge_method_binary, mutation_spec):
    """Reduce per-replicate leg free energies into the wedge result. Pure.

    Error bars are BETWEEN-REPLICATE SD, never the MBAR standard error — the repo's standing rule for
    free-energy error reporting, and doubly right here where setup variance dominates.
    """
    charge_method = assert_charge_consistency(charge_method_ternary, charge_method_binary)
    m = classify_mutation(mutation_spec)
    t = [float(x) for x in ternary_dgs if x is not None]
    b = [float(x) for x in binary_dgs if x is not None]
    if len(t) < 2 or len(b) < 2:
        raise MutationError(f"need >= 2 completed replicates per environment to report a wedge; "
                            f"got ternary={len(t)}, binary={len(b)}")

    def _mean_sd(xs):
        n = len(xs)
        mean = sum(xs) / n
        var = sum((x - mean) ** 2 for x in xs) / (n - 1)
        return mean, var ** 0.5

    t_mean, t_sd = _mean_sd(t)
    b_mean, b_sd = _mean_sd(b)
    ddg = wedge_ddg(t_mean, b_mean)
    # Independent legs -> the SDs add in quadrature.
    ddg_sd = (t_sd ** 2 + b_sd ** 2) ** 0.5
    return {
        "mutation": m["spec"],
        "charge_change": m["charge_change"],
        "charge_method": charge_method,
        "dg_ternary_kcal": t_mean, "dg_ternary_sd": t_sd, "n_ternary": len(t),
        "dg_binary_kcal": b_mean, "dg_binary_sd": b_sd, "n_binary": len(b),
        "ddg_neo_interface_kcal": ddg,
        "ddg_neo_interface_sd": ddg_sd,
        "error_model": "between-replicate SD, added in quadrature across the two independent environments "
                       "(NOT an MBAR standard error)",
        "engine": "perses.PointMutationExecutor + openmmtools.MultiStateSampler + MBAR",
        "validated": False,
        "interpretation": _interpret(ddg, ddg_sd),
    }


def _interpret(ddg, sd):
    """State what the wedge does and does not license. Pure.

    Deliberately conservative: a wedge inside its own error bar is a null, and a null is a real
    result here — it is the kill-switch firing.
    """
    if abs(ddg) < 2.0 * sd:
        return ("NULL — the ternary and binary legs cost the same within 2 SD, so this mutation shows no "
                "detectable neo-interface contribution. For a residue predicted to line the ternary interface "
                "this is the KILL-SWITCH FIRING: the predicted interface is not carrying the free energy the "
                "model attributes to it.")
    if ddg < 0:
        return ("Mutation is MORE favourable in the ternary environment than the binary one — the WT residue "
                "is a net destabiliser of the modelled neo-interface. Directionally against the design "
                "hypothesis; read it as evidence the modelled interface is wrong before reading it as a "
                "design opportunity.")
    return ("Mutation costs MORE in the ternary environment than in the binary one — consistent with the WT "
            "residue making a real free-energy contribution to the neo-interface. This is the expected sign "
            "for a genuine interface residue, and is CONDITIONAL on the modelled ternary pose; it is evidence "
            "for the interface model, not proof of it.")


# --------------------------------------------------------------------------------------
# Known-answer benchmarks (the gate this engine must pass before it gates anything else)
# --------------------------------------------------------------------------------------
# Protein-protein interface mutations with measured ddG, chosen because each is charge-conserving
# (so the first benchmark does not confound engine error with the charge-artifact problem) and sits
# at a genuine PPI hot spot. The engine is qualified when it recovers these within ~1.5 kcal/mol.
KNOWN_ANSWER_BENCHMARKS = [
    {"system": "barnase-barstar", "mutation": "A:Y29A",
     "why": "The canonical, most-measured PPI hot spot in the literature; charge-conserving; large "
            "experimental effect, so an engine that cannot see it cannot see our wedge either."},
    {"system": "barnase-barstar", "mutation": "A:Y29F",
     "why": "Conservative OH->H swap at the same site. Pairs with Y29A as a graded control: a working engine "
            "must rank Y29A as the larger effect, which tests ordering, not just magnitude."},
    {"system": "hGH-hGHR", "mutation": "A:W104A",
     "why": "Second independent hot spot in a different fold, so a pass is not barnase-specific."},
]


def benchmark_plan(n_replicas=3, charge_method=None):
    """Plan the known-answer qualification set. Pure.

    Deliberately runs the benchmark through the SAME plan_wedge path as a real wedge, so a guard that
    would block a production wedge also blocks the benchmark — the benchmark cannot accidentally
    validate a path the science will not be allowed to use.
    """
    plans = []
    for b in KNOWN_ANSWER_BENCHMARKS:
        p = plan_wedge(b["mutation"], n_replicas=n_replicas, charge_method=charge_method)
        p["benchmark_system"] = b["system"]
        p["benchmark_rationale"] = b["why"]
        plans.append(p)
    return {"benchmarks": plans,
            "pass_criterion": "recover each measured ddG within ~1.5 kcal/mol AND reproduce the Y29A > Y29F "
                              "ordering; a magnitude pass with the ordering wrong is a FAIL.",
            "gate": "5a-KS may not contribute a number to the manuscript until this set passes."}


# --------------------------------------------------------------------------------------
# MD entry points (lazy imports — this module must stay importable on CPU with no MD stack)
# --------------------------------------------------------------------------------------
def build_hybrid(structure_path, mutation_spec, ligand_sdf=None, charge_method=None):
    """Build the perses hybrid-topology system for one protein point mutation.

    Imports perses lazily so the pure helpers above stay importable in the dev sandbox and in CI with
    no MD stack installed. UNVALIDATED — see the module docstring.
    """
    from perses.app.relative_point_mutation_setup import PointMutationExecutor  # noqa: F401

    m = classify_mutation(mutation_spec)
    if not m["buildable"]:
        raise MutationError(m["risk"])
    cm = (charge_method or md_settings.CHARGE_METHOD).strip().lower()
    return PointMutationExecutor(
        protein_filename=structure_path,
        mutation_chain_id=m["chain"],
        mutation_residue_id=str(m["resid"]),
        proposed_residue=m["mutant"],
        ligand_input=ligand_sdf,
        # Match the rest of the repo's MD settings so the wedge is sampled under the same Hamiltonian
        # family as every other lane (md_settings is the single source of truth for these).
        forcefield_files=["amber14/protein.ff14SB.xml", "amber14/tip3p.xml"],
        small_molecule_forcefield=md_settings.SMALL_MOLECULE_FORCEFIELD,
        # NOTE: the timestep is deliberately NOT taken from md_settings.TIMESTEP_FS here. The ternary
        # lane's 4 fs required plain-MD pre-equilibration to avoid softcore NaNs in a large rough
        # assembly, and a mutation hybrid in the same assembly carries the same risk. Start at 1 fs
        # for warmup; the driver escalates only after a clean warmup.
    ), {"charge_method": cm, "mutation": m}


def main(argv=None):
    ap = argparse.ArgumentParser(description="5a-KS protein-mutation wedge engine (plan / classify / benchmark)")
    ap.add_argument("--classify", metavar="SPEC", help="classify a mutation spec, e.g. A:R412A")
    ap.add_argument("--plan", metavar="SPEC", help="plan a wedge for a mutation spec")
    ap.add_argument("--benchmark-plan", action="store_true", help="plan the known-answer qualification set")
    ap.add_argument("--n-replicas", type=int, default=3)
    ap.add_argument("--charge-method", default=None)
    ap.add_argument("--charge-correction", default="none", choices=CHARGE_CORRECTIONS)
    ap.add_argument("--allow-charge-change", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.classify:
            out = classify_mutation(args.classify)
        elif args.plan:
            out = plan_wedge(args.plan, n_replicas=args.n_replicas, charge_method=args.charge_method,
                             charge_correction=args.charge_correction,
                             allow_charge_change=args.allow_charge_change)
        elif args.benchmark_plan:
            out = benchmark_plan(n_replicas=args.n_replicas, charge_method=args.charge_method)
        else:
            ap.print_help()
            return 2
    except MutationError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
