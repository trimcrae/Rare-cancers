#!/usr/bin/env python3
"""RUNG 5a-KS — stage the ternary CO-FOLDS the ligand-side double difference needs.

WHAT 5a-KS IS, AND WHY THE CO-FOLD IS ITS FIRST STEP
-----------------------------------------------------
The primary kill-switch is a double difference over one matched ligand pair:

    S = ddG_coop(d0 -> d | NR4A3) - ddG_coop(d0 -> d | NR4A1)

`d0` and `d` differ by ONE atom (C-H -> N, phenyl -> 3-pyridyl) on a wedge aimed at T407, which is Leu in
NR4A1 and Val in NR4A2 — so the H-bond donor NR4A3 presents is absent in BOTH paralogues. The pair was
designed and RDKit-verified by RUNG 5b (`nr4a3-linker-design.json` -> `matched_pair_for_rung_5a_ks`); nothing
here re-derives it, and **no SMILES is typed in this file** — it is read from that artifact, because a second
copy of a molecule is exactly how a design and the thing actually simulated drift apart.

Only **ternary** legs are needed. The wedge sits 9.0 A clear of the E3 interface, so the ligand-E3 binary leg
and the solvent leg are paralogue-independent and cancel exactly in the double difference. That is what makes
5a-KS ~$12 rather than a full cycle per species.

The FEP engine (`nr4a3_ternary_fep.py`) mounts, per leg, `<leg_id>/complex.pdb` + `<leg_id>/ligands.sdf`, and
`ternary_fep_stage.py` derives those from ONE co-folded ternary structure per environment. So the input this
rung is missing — the only thing standing between "the pair is designed" and "the fleet can launch" — is a
co-fold of **CRBN + NR4A{3,1}-LBD + the construct**. This module produces exactly that, reusing
`nr4a3_ternary.py`, which already co-folds NR4A-LBD + CRBN + a PROTAC given its SMILES.

WHY ONLY `d0` IS CO-FOLDED
--------------------------
Both morph endpoints are staged from the SAME co-fold pose: the engine's pose repair re-imposes each
endpoint's bond orders and stereo from SMILES, and OpenFE's hybrid topology handles the perturbation. Two
independent co-folds would introduce a pose difference between the endpoints that the alchemical
transformation would then have to absorb — a difference that is NOT part of the physical question and would
contaminate `S`. One pose, two endpoints, is both cheaper and more correct. `d` is carried through only as the
SMILES the stager retitles onto that pose, and is recorded here so the two never drift apart.

NOT GATED ON RUNG 2b. The 4 fs timestep decision changes what the FEP legs cost, not what structure they
start from, so this co-fold is safe to run while RUNG 2b is still deciding. The ~$12 of ternary legs is the
part that waits.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(HERE, "nr4a3-linker-design.json")
OUT = os.path.join(HERE, "nr4a3-5aks-cofold-prep.json")

# The species the double difference is taken over. NR4A2 is deliberately NOT here: `S` is defined on the
# NR4A3/NR4A1 pair, and the design note records that extending to NR4A2 is what a DISCRIMINATING result earns,
# not something to pay for up front.
SPECIES = ("NR4A3", "NR4A1")

# ⚠ THE DOUBLE UNDERSCORE IS LOad-BEARING, NOT STYLE. `nr4a3_ternary_fep._environment_of` looks a leg id up in
# the frozen PILOT_LEG_MAP and, for anything not in it, falls back to `"ternary" if "__ternary" in leg_id else
# "binary"`. A single-underscore id like `5aks_ternary_nr4a3` therefore classifies as BINARY — the engine would
# drop the target chain and run the wrong system, and `S` would be a difference of two binary legs with no
# paralogue in them at all. Nothing downstream would notice: a binary leg converges perfectly well.
MORPH = "5aks_d0_to_d"

# ⚠ THE ENDPOINT NAMES ARE A CONTRACT WITH THE FEP ENGINE, NOT LABELS. `nr4a3_ternary_fep._build_components`
# resolves each alchemical endpoint by looking up `_Name` in `ligands.sdf` (`nr4a3_rbfe._sdf_mol`), and
# `ternary_coop_prep._morph_endpoints` derives those names by splitting the leg's `morph` string on `->`. So
# three files have to agree on two strings; they agree by importing THESE, and a test asserts the round trip.
# Bare `d0`/`d` were rejected as too generic to be safe as SDF record names in a shared tree.
ENDPOINT_A, ENDPOINT_B = "5aks_d0", "5aks_d"
MORPH_STR = f"{ENDPOINT_A} -> {ENDPOINT_B}"


def cofold_cif_stem(species):
    """The Boltz prediction stem for one species' ternary co-fold — `nr4a3_ternary.py`'s own naming.

    ⚠ THIS EXISTS BECAUSE A LOOSE GLOB PICKED THE WRONG STRUCTURE. The stager used to look for
    `*nr4a3*model_0.cif`, and `nr4a3_ternary.py` also writes the CRBN+lenalidomide POSITIVE CONTROL as
    `nr4a3-ternary-control` — a single-chain CRBN complex with no NR4A3 in it at all. Sorted, `...control...`
    precedes `...protac...`, so the NR4A3 leg would have been staged from the control. It would have failed
    closed at the template-match step (lenalidomide is not the construct), but for the wrong reason, and a
    future co-fold whose ligand happened to match would not have failed at all.
    """
    return f"{species.lower()}-ternary-protac"


def leg_id(species):
    """`5aks_d0_to_d__ternary_nr4a3` — the repo's `<morph>__<environment>_<target>` convention, which the FEP
    engine parses. `_morph_key` recovers `5aks_d0_to_d`, shared by both species' legs exactly as
    `nrv04_active_to_epimer` is shared by its binary and ternary arms."""
    return f"{MORPH}__ternary_{species.lower()}"


# The legs' physical meaning, kept HERE rather than added to `ternary_coop.PILOT_LEG_MAP`. That map is the
# FROZEN pilot bundle and `load_pilot_legs` fails closed when it disagrees with the preregistered leg-id list,
# so extending it would either break that guard or silently enlarge a preregistered experiment with legs it
# never declared. RUNG 5a-KS is a different experiment and carries its own registry.
LEG_MAP = {
    leg_id(sp): {
        # The morph string is PARSED, not displayed: `ternary_coop_prep._morph_endpoints` splits it on `->`
        # and the two halves become the SDF record names the engine resolves each endpoint by. It used to
        # read "5aKS_d0 (phenyl) -> 5aKS_d (3-pyridyl)", which would have made the engine hunt for a record
        # literally named "5aKS_d0 (phenyl)" and hard-fail. The chemistry lives in `wedge`, below.
        "morph": MORPH_STR,
        "wedge": "phenyl (d0, control) -> 3-pyridyl (d, wedge) — one aromatic C-H -> N",
        "environment": "ternary",
        "e3": "CRBN",
        "target": sp,
        "purpose": "one arm of the ligand-side double difference S = ddG_coop(d0->d | NR4A3) - "
                   "ddG_coop(d0->d | NR4A1). Ternary only: the wedge sits ~9 A clear of the E3 interface, so "
                   "the shared binary and solvent legs are paralogue-independent and cancel exactly.",
    } for sp in SPECIES
}


def load_pair(design_path=DESIGN):
    """The matched pair, read from RUNG 5b's artifact — never hand-typed.

    Returns {'d': {...}, 'd0': {...}, 'wedge_target_residue': {...}, ...} and REFUSES rather than guessing if
    the artifact does not carry what the rung needs. A missing field here means the design changed shape, and
    silently co-folding whatever was found would produce inputs that do not match the recorded design.
    """
    with open(design_path) as fh:
        design = json.load(fh)
    mp = design.get("matched_pair_for_rung_5a_ks")
    if not mp:
        raise SystemExit("[5aks] the design artifact carries no `matched_pair_for_rung_5a_ks` — run RUNG 5b")
    missing = [k for k in ("d", "d0", "wedge_target_residue", "test") if k not in mp]
    if missing:
        raise SystemExit(f"[5aks] matched pair is missing {missing} — refusing to co-fold a partial design")
    for role in ("d", "d0"):
        if not mp[role].get("smiles"):
            raise SystemExit(f"[5aks] endpoint `{role}` carries no SMILES — refusing to invent one")
    return mp


def endpoint_smiles(mp):
    """(d0_smiles, d_smiles) — the co-fold ligand first, the perturbed endpoint second."""
    return mp["d0"]["smiles"], mp["d"]["smiles"]


def pair_is_matched(mp):
    """Cheap structural sanity on the pair BEFORE any GPU time: the two endpoints must differ, and differ
    only by the aza-scan. A pair that is accidentally identical would give S == 0 by construction and look
    like a clean null — the single most expensive way this rung could fail silently."""
    d0, d = endpoint_smiles(mp)
    if d0 == d:
        return False, "d and d0 have identical SMILES — S would be 0 by construction"
    if len(d0) != len(d):
        # phenyl `c7ccccc7` -> 3-pyridyl `c7cccnc7` is a character-for-character substitution.
        return False, f"d/d0 SMILES differ in length ({len(d0)} vs {len(d)}) — not a one-atom aza-scan"
    diffs = [i for i, (a, b) in enumerate(zip(d0, d)) if a != b]
    if len(diffs) != 1:
        return False, f"d/d0 differ at {len(diffs)} positions — expected exactly 1 (C -> N)"
    i = diffs[0]
    if (d0[i], d[i]) != ("c", "n"):
        return False, f"the differing character is {d0[i]!r} -> {d[i]!r}, expected 'c' -> 'n'"
    return True, f"one-character aromatic C -> N at SMILES index {i}"


def cofold_plan(mp, species=SPECIES):
    """What has to be co-folded, per species — the pure planner, so the contract is testable with no network.

    One co-fold per species, on `d0` only (see the module docstring). The `d` SMILES rides along because the
    stager writes the same pose twice and retitles it, and recording both here is what keeps the simulated
    endpoints tied to the design.
    """
    d0, d = endpoint_smiles(mp)
    return [{
        "species": sp,
        "system": f"CRBN + {sp}-LBD + construct",
        "cofold_ligand_smiles": d0,
        "cofold_ligand_role": "d0 (control endpoint) — the pose BOTH endpoints are staged from",
        "perturbed_endpoint_smiles": d,
        "leg_id": leg_id(sp),
        "environment": "ternary",
        "e3": "CRBN",
        "cofold_cif_stem": cofold_cif_stem(sp),
        "endpoint_names": [ENDPOINT_A, ENDPOINT_B],
    } for sp in species]


def build(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--design", default=DESIGN)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--run", action="store_true",
                    help="run Boltz inference (needs a GPU); omit for the $0 prep that builds the input YAMLs")
    args = ap.parse_args(argv)

    mp = load_pair(args.design)
    ok, why = pair_is_matched(mp)
    print(f"[5aks] matched-pair check: {'OK' if ok else 'FAILED'} — {why}", flush=True)
    if not ok:
        raise SystemExit("[5aks] refusing to co-fold: the pair is not the one-atom aza-scan the rung tests")

    plan = cofold_plan(mp)
    for p in plan:
        print(f"[5aks] plan {p['leg_id']}: {p['system']}", flush=True)

    record = {
        "_title": "RUNG 5a-KS — ternary co-fold inputs for the ligand-side double difference",
        "_status": "INPUT STAGING. No free energy, no selectivity claim, nothing about efficacy or safety.",
        "_test": mp["test"],
        "_pair_source": os.path.relpath(args.design, HERE),
        "_why_one_cofold_per_species": (
            "Both morph endpoints are staged from ONE pose; the engine re-imposes each endpoint's bond orders "
            "and stereo from SMILES. Two independent co-folds would put a pose difference between the "
            "endpoints that the alchemical transformation would have to absorb — not part of the physical "
            "question, and it would contaminate S."),
        "_not_gated_on_rung_2b": (
            "The 4 fs decision changes what the FEP legs cost, not what structure they start from. The ~$12 "
            "of ternary legs is the part that waits for that gate."),
        "matched_pair_check": {"passes": ok, "reading": why},
        "wedge_target_residue": mp["wedge_target_residue"],
        "plan": plan,
    }

    if args.run:
        # The heavy path delegates to the existing co-fold driver rather than re-implementing Boltz staging.
        sys.path.insert(0, HERE)
        import nr4a3_ternary  # noqa: E402  (imported lazily: needs network + GPU, absent in the sandbox)
        d0, _d = endpoint_smiles(mp)
        # ⚠ --targets, NOT the driver's default. `nr4a3_ternary.py` co-folds NR4A3 **and NR4A1 and NR4A2**;
        # `S` is defined on the NR4A3/NR4A1 pair only, and the design records that extending to NR4A2 is what
        # a DISCRIMINATING result earns rather than something to pay for up front. Folding NR4A2 anyway would
        # be a third ~800-residue Boltz prediction of rented GPU time bought for a leg nobody is going to run.
        targets = ",".join(SPECIES)
        record["inference"] = {"driver": "nr4a3_ternary.py", "protac_smiles": d0, "targets": targets,
                               "cif_stems": {sp: cofold_cif_stem(sp) for sp in SPECIES}}
        # nr4a3_ternary.main() parses sys.argv; hand it the pair's CONTROL endpoint as the PROTAC. Passing d0
        # explicitly (rather than relying on $PROTAC_SMILES) keeps the molecule that was co-folded visible in
        # the recorded command instead of in an environment variable nobody reads back.
        sys.argv = ["nr4a3_ternary.py", "--run", "--protac-smiles", d0, "--targets", targets]
        nr4a3_ternary.main()
        record["inference"]["status"] = "ran"

    with open(args.out, "w") as fh:
        json.dump(record, fh, indent=1)
        fh.write("\n")
    print(f"[5aks] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
