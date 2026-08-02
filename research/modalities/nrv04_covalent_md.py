#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — endpoint-MD driver (prereg §2/§4).

Runs plain (non-alchemical) endpoint MD on ONE panel leg + seed, imposing the frozen restrained-covalent bond on
covalent legs, and emits the R1-R4 readouts. Env-driven by nrv04_covalent_panel.leg_env(); consumed by the Vast
launcher (one instance per leg+seed).

Force field: amber14 (protein) + GAFF/OpenFF small-molecule via openmmforcefields.SystemGenerator (the standard
non-alchemical path; the RBFE lane's OpenFE machinery is alchemy-only and not reused here). Covalent bond =
a stiff harmonic C6->Sγ bond + two flanking angle restraints (prereg §2), NOT a reparameterized junction.

MODE=smoke: build + minimize + a few hundred MD steps + run the readouts on that tiny trajectory (proves the leg
assembles + the whole pipeline executes end-to-end, ~cents). MODE=run: EQUIL_NS + PROD_NS production.

The OpenMM build/run needs the MD env (CI/Vast); the pure geometry helpers (kabsch, interface selection,
restraint indexing) are unit-tested offline. Nothing here is fabricated — a missing input exits loudly.
"""
from __future__ import annotations

import json
import math
import os
import sys

# ---- pure geometry helpers (no MD deps) -> unit-tested offline --------------------------------------------


def kabsch_rmsd(mobile, ref):
    """RMSD of `mobile` onto `ref` after optimal superposition (Kabsch). Both are Nx3 lists/arrays. Returns the
    post-fit RMSD. numpy only (present in the MD env); imported lazily so the module imports without numpy."""
    import numpy as np
    P = np.asarray(mobile, float)
    Q = np.asarray(ref, float)
    if P.shape != Q.shape or P.shape[0] == 0:
        raise ValueError("kabsch_rmsd: shape mismatch or empty")
    Pc = P - P.mean(0)
    Qc = Q - Q.mean(0)
    V, _, Wt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1.0, 1.0, d])
    U = V @ D @ Wt
    Prot = Pc @ U
    return float(np.sqrt(np.mean(np.sum((Prot - Qc) ** 2, axis=1))))


def interface_atom_indices(positions_nm, chain_ids, e3_chains, target_chains, cutoff_nm=0.8):
    """Heavy-atom indices at the E3<->target interface: any E3 atom within cutoff of a target atom (and vice
    versa), split into (e3_side, target_side). `chain_ids` is per-atom chain id. Pure (O(n_e3*n_target))."""
    e3 = [i for i, c in enumerate(chain_ids) if c in e3_chains]
    tg = [i for i, c in enumerate(chain_ids) if c in target_chains]
    c2 = cutoff_nm * cutoff_nm
    e3_side, tg_side = set(), set()
    for i in e3:
        xi = positions_nm[i]
        for j in tg:
            xj = positions_nm[j]
            if (xi[0] - xj[0]) ** 2 + (xi[1] - xj[1]) ** 2 + (xi[2] - xj[2]) ** 2 <= c2:
                e3_side.add(i); tg_side.add(j)
    return sorted(e3_side), sorted(tg_side)


# ---- OpenMM build / run (MD env only) --------------------------------------------------------------------


def _require(cond, msg):
    if not cond:
        raise SystemExit(f"[nrv04-md] {msg}")


def pdb_text_atom_count(pdb_text):
    return sum(1 for ln in pdb_text.splitlines() if ln[:6].strip() in ("ATOM", "HETATM"))


# The largest Sg...electrophile separation that a PREFORMED Michael adduct can honestly be modelled from. The
# restraint pulls the pair to 1.81 A with k = 3e5 kJ/mol/nm^2; from ~8 A that is a strain minimisation can
# dissipate, from ~12 A it is a winch that drags the ligand across the assembly. 8 A was already the driver's
# own warning threshold — this makes it a GATE for covalent legs instead of a line of log nobody reads.
# Overridable (NRV04_MAX_TETHER_A) so a deliberate exception is explicit and recorded, never accidental.
MAX_COVALENT_TETHER_A = float(os.environ.get("NRV04_MAX_TETHER_A", "8.0"))

# UniProt P22736 (human NR4A1/NUR77) full length, verified from the live FASTA on 2026-07-25 by
# `nrv04_covalent_input_audit.resolve_lbd_offset` (full_len = 598, residue 551 = Cys). The frozen LBD construct
# is the C-terminal `NR4A_LBD_RESIDUES` of that sequence (nr4a3_ternary.lbd_seq: `full[-254:]`), so full-length
# C551 is construct residue 551 - (598 - 254) = 207. Kept as a constant rather than fetched, because a GPU leg
# must not depend on a network call, and asserted to be a cysteine at use time so a construct change fails
# closed instead of anchoring the adduct somewhere else.
NR4A1_FULL_LEN = 598


def _frozen_cys_by_construct(pdb_text, target_chain, cov_resnum, full_len=NR4A1_FULL_LEN):
    """IDENTIFY the preregistered covalent cysteine by construct arithmetic, and VERIFY it is a Cys with an Sg.

    ⚠ WHY THIS REPLACED "THE NEAREST TARGET-CHAIN CYSTEINE" (Lane 8, 2026-07-25) — third instance of the same
    defect class as the positional E3/target split and the all-chain reactive-Cys search. `_reactive_cys_by_geometry`
    answers "which cysteine on the target chain is closest to the warhead", which is NOT the question the prereg
    asks: the covalent site is **NR4A1 Cys551**, established experimentally (Zhang et al., *Chem. Commun.* 2018,
    doi:10.1039/C8CC06140H, PMID 30376017 — celastrol is positioned by specific noncovalent interactions next to
    the C551 thiol and forms a reversible covalent bond).

    Measured consequence, over every clean co-fold in the bucket (`nrv04-covalent-input-audit.json`): the nearest
    target-chain cysteine is **C566** at 8.87-8.99 A, while **C551 is 28.4-39.1 A** away. So the geometric rule
    (a) reported an A1 distance for the WRONG residue — the amendment's 8.99 A is C566's, not C551's — (b) would
    have built the restraint onto C566 had it passed, and (c) made the `cov_c551a` leg mutate **C566**, not C551,
    so the control did not remove the engagement it is named for. The chemistry is known; it is not something the
    pose should be allowed to vote on. Geometry is demoted to a diagnostic.

    Returns (chain_id, resid_int). Raises rather than falling back."""
    from nrv04_covalent_assemble import NR4A_LBD_RESIDUES
    idx = cov_resnum - (full_len - NR4A_LBD_RESIDUES)
    if not (1 <= idx <= NR4A_LBD_RESIDUES):
        raise SystemExit(f"[nrv04-md] the preregistered covalent residue {cov_resnum} maps to construct index "
                         f"{idx}, outside the {NR4A_LBD_RESIDUES}-residue LBD — the construct definition or the "
                         f"full length ({full_len}) has changed; refusing to guess a site")
    have_sg = False
    seen = None
    for line in pdb_text.splitlines():
        if line[:6].strip() not in ("ATOM", "HETATM") or line[21] != target_chain:
            continue
        try:
            if int(line[22:26]) != idx:
                continue
        except ValueError:
            continue
        seen = line[17:20].strip()
        if seen == "CYS" and line[12:16].strip() == "SG":
            have_sg = True
    if seen is None:
        raise SystemExit(f"[nrv04-md] target chain {target_chain!r} has no residue {idx} (= full-length "
                         f"{cov_resnum}); this is not the frozen {NR4A_LBD_RESIDUES}-residue construct")
    if not have_sg:
        raise SystemExit(f"[nrv04-md] target chain {target_chain!r} residue {idx} (= full-length {cov_resnum}) "
                         f"is {seen}, not a CYS with an SG — the preregistered covalent site is not present, so "
                         f"no adduct can be modelled here. Refusing to substitute a different cysteine (that "
                         f"substitution is exactly how C566 came to carry the 8.99 A figure attributed to C551).")
    return target_chain, idx


def _residue_at_frozen_index(pdb_text, target_chain, cov_resnum, full_len=NR4A1_FULL_LEN):
    """The residue NAME sitting at the preregistered site's construct index, or None. NEVER raises.

    The reporting half of `_frozen_cys_by_construct`, split out so a leg that does not NEED the site can still
    RECORD what is there. For the retrospective's paralogue arms that string is the evidence for prereg §0's
    central claim — NR4A3 carries THR and NR4A2 TYR where NR4A1 has Cys551 — so it belongs in the leg record
    rather than in a traceback."""
    from nrv04_covalent_assemble import NR4A_LBD_RESIDUES
    idx = cov_resnum - (full_len - NR4A_LBD_RESIDUES)
    for line in pdb_text.splitlines():
        if line[:6].strip() not in ("ATOM", "HETATM") or line[21] != target_chain:
            continue
        try:
            if int(line[22:26]) != idx:
                continue
        except ValueError:
            continue
        return {"construct_index": idx, "residue": line[17:20].strip()}
    return {"construct_index": idx, "residue": None}


def build_system(complex_pdb, ligand_sdf, covalent, cov_lig_atom, cov_resnum, mutation, target_chain=None,
                 stage_probe=None):
    """Build a solvated OpenMM system for one leg. Returns (simulation, meta). CI/Vast only.

    `stage_probe(name, topology, positions, sysgen)` is called after each construction stage when supplied.
    It exists so a diagnostic can measure THE PRODUCTION PATH rather than a re-implementation of it: the
    2026-07-31 seed_3 investigation needs the single-point energy after PDBFixer, after the ligand is added
    and after solvation, and a probe that rebuilt those stages itself could diverge from this function and
    then answer about the wrong pipeline. Ignored (and costs nothing) when None, which is every real leg.
    """
    import numpy as np  # noqa: F401
    from openmm import app, unit, HarmonicBondForce, HarmonicAngleForce, Platform
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator

    import md_settings as MD                                   # canonical hyperparameters (single source of truth)

    _require(os.path.exists(complex_pdb), f"missing complex.pdb: {complex_pdb}")
    _require(os.path.exists(ligand_sdf), f"missing ligands.sdf: {ligand_sdf}")

    # Identify the reactive cysteine by GEOMETRY (nearest Sγ to the warhead electrophile in the co-fold pose) —
    # NOT by the hardcoded resnum 551, which does not exist in the co-fold's renumbered chains. This resolves the
    # target chain + the residue used by BOTH the C551A mutation and the covalent restraint, so they stay
    # consistent and are immune to renumbering.
    pdb_text = open(complex_pdb).read()
    cov_pair = None
    react_chain, react_resid, react_dist, cys_diag = _reactive_cys_by_geometry(
        pdb_text, ligand_sdf, cov_lig_atom, target_chain=target_chain)
    # THE SITE IS IDENTIFIED, NOT INFERRED FROM THE POSE (Lane 8, 2026-07-25 — see _frozen_cys_by_construct).
    # Geometry is kept only as a diagnostic; when the two disagree the disagreement is RECORDED, because that
    # disagreement (nearest = C566 at ~9 A vs frozen C551 at ~28 A) is what made an inadmissible input look
    # marginal. `target_chain=None` (a pre-chains.json input) has no identified target, so the old geometric
    # behaviour is retained there and labelled as such.
    geom = {"chain": react_chain, "resid": react_resid,
            "dist_A": None if react_dist is None else round(react_dist, 2)}
    # ★★ THE FROZEN SITE IS REQUIRED ONLY WHERE IT IS USED (2026-07-31, measured on the retrospective's
    # nr4a3 pilot — Vast 46400138, run 30634610517).
    #
    # `_frozen_cys_by_construct` RAISES when the residue aligned to full-length 551 is not a CYS with an SG.
    # It was called on EVERY leg, and `react_chain`/`react_resid` are used in exactly two places: the covalent
    # restraint, and the `C551A` mutation. A plain non-covalent leg uses neither — for it the site is a
    # DIAGNOSTIC, and a diagnostic must never be able to kill the run it is describing.
    #
    # WHY THAT IS NOT A CORNER CASE HERE — IT IS THE RETROSPECTIVE'S ENTIRE DESIGN POINT. Prereg §0 (Leg 0,
    # nrv04-cys-conservation.json): NR4A1 Cys551 is NOT conserved in NR4A2/NR4A3 — Thr and Tyr respectively.
    # Every R1 arm is non-covalent, and two of the three are paralogues that BY CONSTRUCTION have no cysteine
    # at that position. So the check turned the panel's central biological fact into a build failure:
    #
    #     [nrv04-md] target chain 'A' residue 207 (= full-length 551) is THR, not a CYS with an SG
    #
    # and because `nrv04_covalent_md` raises before it writes a leg JSON, the container died, Vast re-ran the
    # onstart, and the box CRASH-LOOPED on a live meter (CLAUDE.md §6: the host cannot stop its own billing —
    # the log shows the mock-terminate teardown failing on every cycle). Caught by §6's one-real-leg rung
    # BEFORE the 16-unit fan-out; had the fan-out gone first, all six nr4a3 units would have done this at once.
    #
    # ⚠ NOTHING IS WEAKENED FOR A COVALENT LEG. When the site is actually needed the resolution and its
    # SystemExit are unchanged, so the Lane-8 ruling (identify the site by construct arithmetic, never
    # substitute the geometrically nearest cysteine) still binds exactly where it was written to bind. The
    # absence is RECORDED rather than swallowed: `site_resolution` says the site was not required and what was
    # found instead, so a non-covalent paralogue leg carries the evidence that its Cys551 is absent.
    needs_frozen_site = bool(covalent) or mutation == "C551A"
    if target_chain is not None and needs_frozen_site:
        react_chain, react_resid = _frozen_cys_by_construct(pdb_text, target_chain, cov_resnum)
        react_dist = _sg_electrophile_distance(pdb_text, ligand_sdf, cov_lig_atom, react_chain, react_resid)
        cys_diag["site_resolution"] = "IDENTIFIED by construct arithmetic from the preregistered residue"
        cys_diag["preregistered_resnum_fulllen"] = cov_resnum
        cys_diag["geometric_nearest_on_target"] = geom
        cys_diag["geometry_agrees_with_frozen_site"] = (geom["resid"] == react_resid)
    elif target_chain is not None:
        # Non-covalent, unmutated: the frozen site is not used, so it is REPORTED rather than required.
        # `residue_at_frozen_index` is the paralogue fact prereg §0 rests on (Thr in NR4A3, Tyr in NR4A2).
        cys_diag["site_resolution"] = ("NOT REQUIRED — this leg is non-covalent and unmutated, so the "
                                       "preregistered Cys551 site is never used. Reported, not enforced.")
        cys_diag["preregistered_resnum_fulllen"] = cov_resnum
        cys_diag["residue_at_frozen_index"] = _residue_at_frozen_index(pdb_text, target_chain, cov_resnum)
        cys_diag["geometric_nearest_on_target"] = geom
    else:
        cys_diag["site_resolution"] = ("GEOMETRIC — no identified target chain, so the frozen site could not be "
                                       "resolved by construct arithmetic; this is the rule Lane 8 demoted")
    # ⚠ EVERY USE OF `react_dist` BELOW MUST TOLERATE "NOT MEASURED". It is None when the ligand carries no
    # locatable electrophile (see `_reactive_cys_by_geometry`), which is the sensitivity control's normal
    # state — and an unmeasured distance formatted or compared as a float is a TypeError that kills the leg
    # just as dead as the ValueError this whole change exists to stop.
    _dist_txt = "NOT MEASURED (no locatable electrophile)" if react_dist is None else f"{react_dist:.2f} Å"
    print(f"[nrv04-md] covalent Cys = chain {react_chain} resid {react_resid} "
          f"(Sγ {_dist_txt} from the warhead electrophile; preregistered full-length resnum "
          f"{cov_resnum}); {json.dumps(cys_diag)}", flush=True)
    # FAIL CLOSED on an un-modellable tether. The panel's warhead_only legs tethered celastrol to an ElonginC
    # cysteine 12.44 Å away — the co-fold had not posed free celastrol in the NR4A1 pocket at all — and the only
    # consequence was a WARN line. A covalent leg whose adduct partner is that far away is not the system the
    # prereg describes, so it must stop rather than produce numbers about something else.
    # ★ A COVALENT LEG WITH NO MEASURABLE TETHER IS STILL A HARD STOP — `react_dist is None` means the
    # electrophile could not be located, and a covalent leg cannot be built without one. It fails here with a
    # reason rather than later with a TypeError; `_covalent_indices` would raise anyway, but not legibly.
    if covalent and react_dist is None:
        raise SystemExit(
            "[nrv04-md] this leg is COVALENT but the ligand carries no locatable electrophile, so no adduct "
            "can be built and no tether can be measured. Diagnostics: %s" % json.dumps(cys_diag))
    if covalent and react_dist > MAX_COVALENT_TETHER_A:
        raise SystemExit(
            f"[nrv04-md] the PREREGISTERED covalent Cys ({react_chain}:{react_resid} = full-length {cov_resnum}) "
            f"has its Sγ {react_dist:.2f} Å from the warhead electrophile, "
            f"beyond the {MAX_COVALENT_TETHER_A} Å preformed-adduct limit. The co-fold did not pose the warhead "
            f"in this target's pocket, so a covalent leg cannot be built from it — re-fold the input rather than "
            f"stretching the restraint. Diagnostics: {json.dumps(cys_diag)}. "
            f"(Override with NRV04_MAX_TETHER_A only if the deviation is recorded in the prereg.)")
    if react_dist is not None and react_dist > MAX_COVALENT_TETHER_A:
        print(f"[nrv04-md] WARN reactive Sγ is {react_dist:.1f} Å from the electrophile "
              f"(>{MAX_COVALENT_TETHER_A} Å) — noncovalent leg, so this is descriptive only, but the warhead is "
              f"not seated in this target's pocket", flush=True)
    if mutation == "C551A":                                    # the panel's 'C551A' = knock out the reactive Cys
        # ⚠ THE ONLY REMAINING PATH THAT CAN SEE A NULL SITE. `needs_frozen_site` resolves it by construct
        # arithmetic whenever a target chain is identified, so this fires only for a legacy `target_chain=None`
        # input whose geometric search also could not run. Mutating "chain None residue None" would silently
        # knock out nothing and produce a leg labelled C551A that is not mutated — a fabricated arm.
        if react_chain is None or react_resid is None:
            raise SystemExit(
                "[nrv04-md] mutation=C551A was requested but the reactive Cys could not be identified "
                "(no identified target chain, and no locatable electrophile for the geometric fallback). "
                "A leg labelled C551A that was never mutated would be a fabricated arm. Diagnostics: %s"
                % json.dumps(cys_diag))
        from nrv04_covalent_stage import mutate_cys_to_ala
        pdb_text = mutate_cys_to_ala(pdb_text, react_chain, react_resid)
    tmp_pdb = complex_pdb + ".staged.pdb"
    open(tmp_pdb, "w").write(pdb_text)

    # PREP THE PREDICTED PROTEIN WITH PDBFIXER — the co-fold complex.pdb is heavy-atoms-only AND a multi-chain
    # predicted assembly (VHL/EloB/EloC/target) with uncapped chain termini, so a bare addHydrogens/createSystem
    # fails ("No template found ... missing terminal capping group / missing H"). PDBFixer is the standard prep:
    # add missing heavy atoms, cap termini, add hydrogens. We DON'T let it build long missing loops
    # (missingResidues={}) — the co-fold is sequence-complete; we only fix atoms/termini/H on existing residues.
    from pdbfixer import PDBFixer
    fixer = PDBFixer(filename=tmp_pdb)
    fixer.findMissingResidues(); fixer.missingResidues = {}
    fixer.findNonstandardResidues(); fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    n_before = pdb_text_atom_count(pdb_text)
    fixed_topology, fixed_positions = fixer.topology, fixer.positions
    n_after_h = fixed_topology.getNumAtoms()

    lig = Molecule.from_file(ligand_sdf)
    if isinstance(lig, list):
        lig = lig[0]

    # LIGAND CHARGES: assign md_settings.CHARGE_METHOD (NAGL) to the molecule BEFORE the SystemGenerator, using the
    # SAME shared helper every ternary lane uses (ternary_endpoint_stability.assign_rbfe_charges). This is THE fix
    # for the sqm intractability — AM1-BCC via AmberTools sqm ran >85 min on the 166-atom nrv04 recruiter without
    # converging (measured 2026-07-22), whereas NAGL (a deterministic ML AM1-BCC surrogate) charges it in seconds.
    # openmmforcefields then uses the molecule's pre-assigned charges instead of calling sqm. Because charging is
    # now instant + deterministic, there is NO charge cache (cache=None): a stale/partial am1bcc cache could
    # otherwise contaminate one leg's charges and silently break cross-leg consistency.
    if not lig.conformers:
        lig.generate_conformers(n_conformers=1)
    from ternary_endpoint_stability import assign_rbfe_charges
    charge_used = assign_rbfe_charges(lig, MD.CHARGE_METHOD)
    _require(charge_used is not None,
             f"could not assign {MD.CHARGE_METHOD} charges to the ligand (openff-nagl missing from the env?)")

    # ALL integration/FF/solvation hyperparameters come from md_settings (canonical). Do NOT hardcode here — a
    # per-driver value is exactly how the 2 fs-vs-4 fs drift crept in. Sharing md_settings with the RBFE lane is
    # ENGINE HYGIENE (same integrator/FF, no unexplained knobs) — NOT validation transfer: ValB validates the
    # free-energy method for the NR4A RBFE matrix, not this endpoint-MD panel. This panel reports geometric
    # readouts and is validated by its own biological control (NR-V04 selectivity). See md_settings.py
    # "SCOPE OF WHAT SHARING THESE BUYS".
    sysgen = SystemGenerator(
        forcefields=list(MD.PROTEIN_FORCEFIELDS),
        small_molecule_forcefield=MD.SMALL_MOLECULE_FORCEFIELD,
        molecules=[lig],
        forcefield_kwargs=MD.systemgenerator_forcefield_kwargs(),
        cache=None,
    )

    modeller = app.Modeller(fixed_topology, fixed_positions)   # PDBFixer already added protein H + capped termini
    if stage_probe:
        stage_probe("protein_after_pdbfixer", modeller.topology, modeller.positions, sysgen)
    lig_top = lig.to_topology().to_openmm()
    lig_pos = lig.conformers[0].to_openmm()
    modeller.add(lig_top, lig_pos)
    if stage_probe:
        stage_probe("protein_plus_ligand", modeller.topology, modeller.positions, sysgen)
    modeller.addSolvent(sysgen.forcefield, model=MD.WATER_MODEL,
                        padding=MD.SOLVENT_PADDING_NM * unit.nanometer,
                        ionicStrength=MD.IONIC_STRENGTH_M * unit.molar)
    if stage_probe:
        stage_probe("solvated", modeller.topology, modeller.positions, sysgen)

    system = sysgen.create_system(modeller.topology)

    meta = {"n_atoms": modeller.topology.getNumAtoms(),
            "protein_heavy_atoms": n_before, "after_addH": n_after_h, "charge_method": charge_used,
            "reactive_cys": {"chain": react_chain, "resid": react_resid,
                             "sg_electrophile_dist_A": (None if react_dist is None
                                                       else round(react_dist, 2)), "search": cys_diag}}
    if covalent:
        cov_pair = _covalent_indices(modeller.topology, ligand_sdf, cov_lig_atom, react_resid, react_chain)
        _add_covalent_restraint(system, cov_pair)
        meta["covalent_pair"] = {k: v for k, v in cov_pair.items() if k.endswith("_idx")}

    integrator = MD.openmm_integrator()                        # canonical LangevinMiddle (4 fs, matches ValB/OpenFE)
    platform = _select_platform(Platform)
    sim = app.Simulation(modeller.topology, system, integrator, platform)
    sim.context.setPositions(modeller.positions)
    return sim, modeller.topology, meta


def _select_platform(Platform):
    """Pick CUDA (GPU legs) else CPU (CI smoke). A conda-pack'd env can carry a STALE compiled OpenMM plugin dir
    so NO platform auto-loads — not even the built-in CPU (verified 2026-07-22 on Vast: 'no registered Platform
    called CPU' from the baked env). So if no platforms are present, explicitly load plugins from this env's
    lib/plugins first. OPENMM_REQUIRE_CUDA=1 (set for GPU legs) forbids the silent CPU fallback, which on a
    466k-atom system would be catastrophically slow instead of failing fast."""
    import glob
    have = lambda: [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())]
    names = have()
    if "CUDA" not in names and "CPU" not in names:            # plugins didn't auto-load -> load them explicitly
        cands = []
        pref = os.environ.get("CONDA_PREFIX") or os.environ.get("OPENMM_PREFIX") or "/opt/mamba/envs/md"
        cands.append(os.path.join(pref, "lib", "plugins"))
        try:
            cands.append(Platform.getDefaultPluginsDirectory())
        except Exception:  # noqa: BLE001
            pass
        cands += glob.glob("/opt/mamba/envs/*/lib/plugins") + glob.glob(os.path.join(pref, "lib*", "plugins"))
        loaded = []
        for d in cands:
            if d and os.path.isdir(d):
                try:
                    Platform.loadPluginsFromDirectory(d); loaded.append(d)
                except Exception as e:  # noqa: BLE001
                    print(f"[nrv04-md] plugin load {d} failed: {e}", flush=True)
        names = have()
        print(f"[nrv04-md] reloaded OpenMM plugins from {loaded}; platforms now: {names}", flush=True)
    require_cuda = os.environ.get("OPENMM_REQUIRE_CUDA") == "1"
    if "CUDA" in names:
        return Platform.getPlatformByName("CUDA")
    if require_cuda:
        raise SystemExit(f"[nrv04-md] CUDA platform unavailable (platforms: {names}); OPENMM_REQUIRE_CUDA=1 "
                         f"forbids the slow CPU fallback — check the GPU/driver + OpenMM plugin load on this host")
    if "CPU" in names:
        return Platform.getPlatformByName("CPU")
    raise SystemExit(f"[nrv04-md] no usable OpenMM platform even after plugin reload (platforms: {names})")


def _add_covalent_restraint(system, cov):
    """Impose the frozen restrained-covalent geometry: stiff C6->Sγ bond + CB-Sγ-C6 and Sγ-C6-Cn angle
    restraints (prereg §2). Not a reparameterized junction — a geometric tether for endpoint MD."""
    from openmm import HarmonicBondForce, HarmonicAngleForce, unit
    k_bond = 300000.0 * unit.kilojoule_per_mole / unit.nanometer ** 2
    k_ang = 500.0 * unit.kilojoule_per_mole / unit.radian ** 2
    bf = HarmonicBondForce()
    bf.addBond(cov["sg_idx"], cov["ligc_idx"], 0.181 * unit.nanometer, k_bond)
    system.addForce(bf)
    af = HarmonicAngleForce()
    if cov.get("cb_idx") is not None:
        af.addAngle(cov["cb_idx"], cov["sg_idx"], cov["ligc_idx"], 1.90 * unit.radian, k_ang)   # ~109 deg
    if cov.get("lign_idx") is not None:
        af.addAngle(cov["sg_idx"], cov["ligc_idx"], cov["lign_idx"], 1.90 * unit.radian, k_ang)
    system.addForce(af)


def _target_chain_for_resnum(pdb_text, resnum):
    """Chain id carrying a CYS at `resnum` (the target LBD chain)."""
    for line in pdb_text.splitlines():
        if line[:6].strip() in ("ATOM", "HETATM") and line[17:20].strip() == "CYS":
            try:
                if int(line[22:26]) == resnum:
                    return line[21]
            except ValueError:
                pass
    raise SystemExit(f"[nrv04-md] no CYS at resnum {resnum} to anchor the covalent bond / mutation")


def _covalent_indices(topology, ligand_sdf, cov_lig_atom, cov_resnum, cov_chain=None):
    """Map the restraint atoms to OpenMM particle indices: Cys Sγ, Cys CB, ligand C6, and C6's ligand
    neighbour (for the second angle). The Cys is identified by (cov_chain, cov_resnum) as resolved by geometry in
    build_system (robust to the co-fold's renumbering); cov_chain=None falls back to resid-only matching."""
    sg_idx = cb_idx = ligc_idx = lign_idx = None
    cys_inventory = {}                                          # (chain,resid) -> set of atom names, for diagnostics
    for atom in topology.atoms():
        res = atom.residue
        if res.name == "CYS":
            cys_inventory.setdefault((getattr(res.chain, "id", "?"), res.id), set()).add(atom.name)
        chain_ok = cov_chain is None or getattr(res.chain, "id", None) == cov_chain
        if res.name == "CYS" and _resid(res) == cov_resnum and chain_ok:
            if atom.name == "SG":
                sg_idx = atom.index
            elif atom.name == "CB":
                cb_idx = atom.index
    # ligand atoms: SystemGenerator names them by element+serial in the ligand residue; match cov_lig_atom by
    # order in the SDF (C6 = the electrophile) and its first heavy neighbour.
    from rdkit import Chem
    mol = Chem.SDMolSupplier(ligand_sdf, removeHs=False)[0]
    c6_sdf_idx, neigh_sdf_idx = _electrophile_and_neighbour(mol, cov_lig_atom)
    lig_atoms = [a for a in topology.atoms() if a.residue.name in ("UNK", "LIG", "UNL")]
    if lig_atoms:
        if c6_sdf_idx < len(lig_atoms):
            ligc_idx = lig_atoms[c6_sdf_idx].index
        if neigh_sdf_idx is not None and neigh_sdf_idx < len(lig_atoms):
            lign_idx = lig_atoms[neigh_sdf_idx].index
    if sg_idx is None or ligc_idx is None:
        inv = ", ".join(f"{c}:{r}{'(+SG)' if 'SG' in a else ''}" for (c, r), a in sorted(cys_inventory.items()))
        raise SystemExit(f"[nrv04-md] could not locate covalent atoms (sg={sg_idx}, ligc={ligc_idx}) for "
                         f"cov_resnum={cov_resnum}. CYS residues present (chain:resid): [{inv}]")
    return {"sg_idx": sg_idx, "cb_idx": cb_idx, "ligc_idx": ligc_idx, "lign_idx": lign_idx}


def _electrophile_and_neighbour(mol, cov_lig_atom):
    """The celastrol Michael-acceptor carbon + a heavy neighbour, as 0-based SDF atom indices. Delegates to the
    single frozen definition in nrv04_ligands so the restraint site can't drift between the ligand builder and
    the MD driver. `cov_lig_atom` is kept for interface compatibility (the choice is structural, not name-based)."""
    from nrv04_ligands import electrophile_atom_index
    return electrophile_atom_index(mol)


def _resid(res):
    try:
        return int(res.id)
    except (ValueError, TypeError):
        return None


def _sg_electrophile_distance(pdb_text, ligand_sdf, cov_lig_atom, chain_id, resid):
    """Distance (Å) from one named Cys Sg to the ligand's electrophilic carbon. This is the quantity prereg
    criterion A1 is defined on, once the residue is IDENTIFIED rather than chosen by proximity."""
    from rdkit import Chem
    mol = Chem.SDMolSupplier(ligand_sdf, removeHs=False)[0]
    c6_idx, _ = _electrophile_and_neighbour(mol, cov_lig_atom)
    ep = mol.GetConformer().GetAtomPosition(c6_idx)
    for line in pdb_text.splitlines():
        if line[:6].strip() not in ("ATOM", "HETATM") or line[21] != chain_id:
            continue
        if line[17:20].strip() != "CYS" or line[12:16].strip() != "SG":
            continue
        try:
            if int(line[22:26]) != resid:
                continue
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        return ((x - ep.x) ** 2 + (y - ep.y) ** 2 + (z - ep.z) ** 2) ** 0.5
    raise SystemExit(f"[nrv04-md] no CYS SG at {chain_id}:{resid} to measure the A1 tether against")


def _reactive_cys_by_geometry(pdb_text, ligand_sdf, cov_lig_atom, target_chain=None):
    """Identify the reactive cysteine as the CYS whose Sγ is NEAREST the ligand's electrophilic carbon, SEARCHED
    ONLY ON THE DEGRADATION-TARGET CHAIN.

    ⚠ HISTORY — READ BEFORE CHANGING. This search used to run over EVERY chain in the assembly, on the reasoning
    that "the co-fold placed the celastrol warhead in the NR4A1 pocket, so the nearest Sγ IS the modeled covalent
    partner." That reasoning assumes its conclusion. When the co-fold did NOT pose the warhead in the pocket —
    which is exactly what happened to the panel's `warhead_only` legs — the global search silently returned an
    ELONGIN C cysteine 12.44 Å away and the covalent restraint was built onto an E3 subunit. This is the same
    defect class as the positional E3/target split in `_topology_indices`: a selection rule that ignores the
    dimension the data varies along, and therefore returns a confident answer about the wrong thing.

    So the chain now comes from the assembler's identification, not from the geometry. The geometry chooses only
    WHICH cysteine on that chain, which is what it is actually competent to decide. `target_chain=None` keeps the
    old global behaviour for pre-chains.json inputs and says so in the returned diagnostics.

    Returns (chain_id, resid_int, distance_angstrom, diagnostics). `diagnostics` always reports the global
    nearest as well, so a leg whose target-chain distance is large can be told apart from one whose assembly is
    malformed. Raises if the requested chain carries no cysteine at all."""
    from rdkit import Chem
    mol = Chem.SDMolSupplier(ligand_sdf, removeHs=False)[0]
    # ★★ A LIGAND WITH NO ELECTROPHILE IS A FACT ABOUT THE LIGAND, NOT A BUILD FAILURE (2026-08-01).
    #
    # This is the SAME defect, one call earlier, as the `_frozen_cys_by_construct` fix recorded in
    # `build_system` on 2026-07-31 — and it has the same remedy for the same stated reason: the geometry here
    # is a DIAGNOSTIC ("Geometry is kept only as a diagnostic", `build_system`), and **a diagnostic must never
    # be able to kill the run it is describing.**
    #
    # MEASURED, on the sensitivity control's first MD leg (Vast 46531433, $0.0154, 2026-08-01):
    #
    #     ValueError: no enone (C=C-C=O) found — cannot locate the celastrol electrophile
    #
    # That control stages PRT3789 (CCD A1BB4), a NON-COVALENT SMARCA2 degrader — by design, and by the same
    # design its driver is `nrv04_covalent_md` verbatim, because "a sensitivity control that ran a modified
    # driver would calibrate a readout the program does not use" (`selcal_vast_launch.__doc__`). So a ligand
    # with no enone is not a misconfiguration to reject; it is the control's whole point, and the celastrol
    # warhead search must report its absence rather than raise on it.
    #
    # ⚠ NOTHING IS WEAKENED FOR A COVALENT LEG. The electrophile is still REQUIRED wherever it is USED —
    # `_covalent_indices` (the restraint) and `_sg_electrophile_distance` (the frozen-site distance) call
    # `_electrophile_and_neighbour` directly and their ValueError is unchanged. Only this diagnostic degrades,
    # and it degrades VISIBLY: `electrophile` in the returned diagnostics says the search could not be run and
    # why, so a non-covalent leg carries the evidence instead of a silent zero.
    try:
        c6_idx, _ = _electrophile_and_neighbour(mol, cov_lig_atom)
    except (ValueError, RuntimeError) as e:
        # `None`, NOT NaN: the leg JSON is serialized with json.dump, and NaN is not valid strict JSON —
        # a distance that cannot be measured must read as absent, not as a token every parser disagrees on.
        return None, None, None, {
            "target_chain": target_chain,
            "site_resolution": "NOT ATTEMPTED — the ligand carries no locatable electrophile",
            "electrophile": ("ABSENT: %s. This search anchors on the celastrol enone; a ligand without one "
                             "cannot be measured against a cysteine Sγ, and that is a fact about the ligand "
                             "rather than a fault in the assembly. The covalent restraint and the frozen-site "
                             "distance still REQUIRE it and still raise — see build_system." % e),
            "nearest_cys": None, "global_nearest_cys": None}
    conf = mol.GetConformer()
    ep = conf.GetAtomPosition(c6_idx)                          # electrophile xyz (Å, same frame as complex.pdb)
    cands = []                                                 # (dist, chain, resid) for every CYS Sγ
    for line in pdb_text.splitlines():
        if line[:6].strip() not in ("ATOM", "HETATM"):
            continue
        if line[17:20].strip() != "CYS" or line[12:16].strip() != "SG":
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            resid = int(line[22:26])
        except ValueError:
            continue
        d = ((x - ep.x) ** 2 + (y - ep.y) ** 2 + (z - ep.z) ** 2) ** 0.5
        cands.append((d, line[21], resid))
    if not cands:
        raise SystemExit("[nrv04-md] no CYS Sγ found in the complex — cannot anchor the covalent warhead")
    cands.sort()
    g_d, g_c, g_r = cands[0]
    diag = {"global_nearest": {"chain": g_c, "resid": g_r, "dist_A": round(g_d, 2)},
            "n_cys_sg_total": len(cands), "target_chain": target_chain}
    if target_chain is None:
        diag["search"] = ("GLOBAL — no chains.json target supplied. This is the rule that tethered celastrol to "
                          "Elongin C in the 2026-07-23 panel; verify the chain it returns.")
        return g_c, g_r, g_d, diag
    on_target = [c for c in cands if c[1] == target_chain]
    diag["n_cys_sg_on_target"] = len(on_target)
    diag["search"] = f"restricted to the identified degradation-target chain {target_chain!r}"
    if not on_target:
        raise SystemExit(f"[nrv04-md] the degradation-target chain {target_chain!r} carries no cysteine, so no "
                         f"covalent adduct can be modelled on it. Nearest Sγ anywhere is chain {g_c} resid {g_r} "
                         f"at {g_d:.2f} Å, which is NOT the target — building the restraint there is the defect "
                         f"this check exists to prevent.")
    t_d, t_c, t_r = on_target[0]
    diag["target_nearest"] = {"chain": t_c, "resid": t_r, "dist_A": round(t_d, 2)}
    diag["global_nearest_is_off_target"] = (g_c != target_chain)
    return t_c, t_r, t_d, diag


# ---- orchestration --------------------------------------------------------------------------------------


def _aws_bin():
    import shutil
    return shutil.which("aws") or "/opt/mamba/envs/md/bin/aws"


def _s3_cp(src, dst, timeout=600):
    """Best-effort aws s3 cp (the aws CLI lives in the md env). Returns True on success, never raises."""
    import subprocess
    try:
        r = subprocess.run([_aws_bin(), "s3", "cp", src, dst], capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _ckpt_paths(out_dir, leg_id, seed):
    # OpenMM SERIALIZED STATE (XML) not saveCheckpoint(): the state is PORTABLE across hosts/GPUs, so a spot
    # preemption that re-lands the leg on a *different* box can still resume (saveCheckpoint is hardware-locked).
    return (os.path.join(out_dir, f"ckpt_{leg_id}_s{seed}.state.xml"),
            os.path.join(out_dir, f"ckpt_{leg_id}_s{seed}.ckpt.json"))


def _save_ckpt(sim, state_path, cj_path, state, result_s3, traj=None):
    """Persist the simulation state (portable XML) + accumulated-readout JSON, then mirror both to S3 so a
    re-dispatched (preempted) leg can resume. Atomic local writes; S3 mirror is best-effort.

    `traj` (a `md_analysis_traj.TrajWriter`) is mirrored on the SAME hook, deliberately: a trajectory that only
    reaches S3 at clean exit is lost to precisely the preemption it is being kept for, and 17 of this panel's
    18 legs exited cleanly while leaving nothing to re-derive from."""
    tmp = state_path + ".tmp"
    sim.saveState(tmp); os.replace(tmp, state_path)
    tmpj = cj_path + ".tmp"
    json.dump(state, open(tmpj, "w")); os.replace(tmpj, cj_path)
    if result_s3:
        _s3_cp(state_path, f"{result_s3}/{os.path.basename(state_path)}")
        _s3_cp(cj_path, f"{result_s3}/{os.path.basename(cj_path)}")
    if traj is not None:
        traj.mirror(_s3_cp)


def _load_resume(state_path, cj_path, result_s3, leg_id, seed):
    """Return the accumulated-readout dict if a VALID in-progress production checkpoint exists (pull from S3 if
    not already local), else None. The caller then does sim.loadState(state_path)."""
    if result_s3 and not (os.path.exists(state_path) and os.path.exists(cj_path)):
        _s3_cp(f"{result_s3}/{os.path.basename(state_path)}", state_path)
        _s3_cp(f"{result_s3}/{os.path.basename(cj_path)}", cj_path)
    if not (os.path.exists(state_path) and os.path.exists(cj_path)):
        return None
    try:
        st = json.load(open(cj_path))
    except Exception:  # noqa: BLE001
        return None
    if (st.get("leg_id") == leg_id and st.get("seed") == seed and st.get("phase") == "production"
            and 0 < int(st.get("done_frames", 0)) < int(st.get("frames", 0))):
        return st
    return None


def _rm_ckpt(state_path, cj_path, result_s3):
    """Delete the checkpoint (local + S3) once the leg has finished, so a later re-dispatch re-runs cleanly
    instead of resuming a completed/terminated leg."""
    import subprocess
    for p in (state_path, cj_path):
        try:
            os.remove(p)
        except OSError:
            pass
    if result_s3:
        for name in (os.path.basename(state_path), os.path.basename(cj_path)):
            try:
                subprocess.run([_aws_bin(), "s3", "rm", f"{result_s3}/{name}"], capture_output=True, timeout=120)
            except Exception:  # noqa: BLE001
                pass


def _built_paths(out_dir, leg_id, seed):
    # The EXACT solvated system that produced a checkpoint (System XML + solvated topology as mmCIF + meta).
    # A resume MUST reload THIS rather than re-solvating: addSolvent/PDBFixer on a different host do NOT
    # reproduce a bit-identical atom count, so a rebuilt Context has the wrong particle count and
    # sim.loadState() throws "wrong number of positions". mmCIF (not PDB) carries the ~466k-atom topology
    # without the PDB 99999-atom-serial limit.
    b = os.path.join(out_dir, f"built_{leg_id}_s{seed}")
    return {"system": b + ".system.xml", "cif": b + ".solv.cif", "meta": b + ".built.json"}


def _save_built_system(bp, sim, topology, meta, result_s3):
    """Persist the solvated System (portable XML) + topology (mmCIF) + meta once at fresh build, so a later
    resume on a DIFFERENT host reloads this exact system and its atom count matches the checkpoint. S3 mirror
    is best-effort; a failed upload just means that preemption falls back to a clean restart."""
    from openmm import XmlSerializer, app
    tmp = bp["system"] + ".tmp"
    with open(tmp, "w") as f:
        f.write(XmlSerializer.serialize(sim.system))
    os.replace(tmp, bp["system"])
    pos = sim.context.getState(getPositions=True).getPositions()
    tmpc = bp["cif"] + ".tmp"
    with open(tmpc, "w") as f:
        app.PDBxFile.writeFile(topology, pos, f, keepIds=True)
    os.replace(tmpc, bp["cif"])
    json.dump(meta, open(bp["meta"], "w"))
    s3_ok = None
    if result_s3:
        # The snapshot S3 mirror is the ONE upload a resume on a different host depends on; a single transient
        # failure (verified 2026-07-23: a 648k-atom snapshot returned ok=False on one host while an equal-size
        # one succeeded on another) permanently blocks that leg from ever resuming -> it rebuilds from scratch
        # every preemption. So RETRY each file a few times before giving up (a checkpoint upload can be lossy;
        # this one must not be).
        import time as _t
        s3_ok = True
        for p in bp.values():
            dst = f"{result_s3}/{os.path.basename(p)}"
            ok = False
            for _a in range(3):
                if _s3_cp(p, dst, timeout=900):
                    ok = True
                    break
                _t.sleep(2 * (_a + 1))
            s3_ok = s3_ok and ok
    # Observability: if the mirror fails, the leg would restart-from-0 on every preemption (never resume).
    print(f"[nrv04-md] persisted built-system snapshot ({meta.get('n_atoms')} atoms) -> S3 ok={s3_ok}", flush=True)


def _load_built_system(bp, result_s3):
    """Reconstruct the Simulation from a persisted built-system snapshot (System XML + solvated mmCIF), so a
    resumed leg's Context matches the checkpoint's atom count exactly. Returns (sim, topology, meta) or None
    if the snapshot is unavailable/unreadable (-> caller does a clean fresh start). The existence check runs
    BEFORE any heavy import so the 'no snapshot' fallback needs neither OpenMM nor md_settings."""
    if result_s3:
        for p in bp.values():
            if not os.path.exists(p):
                _s3_cp(f"{result_s3}/{os.path.basename(p)}", p)
    if not all(os.path.exists(p) for p in bp.values()):
        return None
    import md_settings as MD
    from openmm import XmlSerializer, Platform, app
    try:
        cif = app.PDBxFile(bp["cif"])
        with open(bp["system"]) as f:
            system = XmlSerializer.deserialize(f.read())
        meta = json.load(open(bp["meta"]))
    except Exception:  # noqa: BLE001
        return None
    integrator = MD.openmm_integrator()
    platform = _select_platform(Platform)
    sim = app.Simulation(cif.topology, system, integrator, platform)
    sim.context.setPositions(cif.positions)                   # placeholder; loadState overwrites with the checkpoint
    return sim, cif.topology, meta


def run_leg(env):
    """Execute one leg from an env dict (see nrv04_covalent_panel.leg_env). Writes <OUTPUT_DIR>/leg_<id>_s<seed>.json.
    Checkpoint/resume: production is saved (portable OpenMM state + readout JSON) every CKPT_EVERY_FRAMES frames and
    mirrored to RESULT_S3, so a spot-preempted + re-dispatched leg RESUMES from the last saved frame. Resume reloads
    the EXACT persisted solvated system (built-system snapshot), never re-solvates, so the Context matches the
    checkpoint atom count (a rebuild would not -> loadState 'wrong number of positions')."""
    from openmm import unit, app

    import md_settings as MD                                   # canonical hyperparameters (single source of truth)

    leg_id = env["LEG_ID"]; seed = int(env["SEED"]); mode = env.get("MODE", "smoke")
    covalent = env.get("COVALENT") == "1"
    in_dir = os.path.join(env.get("INPUT_DIR", "/opt/ml/input/data"), leg_id)
    out_dir = env.get("OUTPUT_DIR", env.get("CKPT_DIR", "."))
    os.makedirs(out_dir, exist_ok=True)

    import numpy as _np
    import time

    def _pe_kj(_sim):
        return _sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilojoule_per_mole)

    def _finite(_sim):
        p = _sim.context.getState(getPositions=True).getPositions(asNumpy=True)._value
        return bool(_np.isfinite(p).all())

    # sampling lengths canonical (env may override for a shakeout, else the md_settings defaults)
    prod_ns = float(env.get("PROD_NS", MD.PROD_NS)); equil_ns = float(env.get("EQUIL_NS", MD.EQUIL_NS))
    dt_ns = MD.TIMESTEP_NS
    if mode == "smoke":
        equil_steps, prod_steps, stride = 0, 500, 100          # ~cents; proves the pipeline
    else:
        equil_steps = int(equil_ns / dt_ns); prod_steps = int(prod_ns / dt_ns)
        stride = MD.frame_stride_steps()                       # ~10 ps frame cadence (timestep-independent)
    frames = max(1, prod_steps // stride)

    # --- checkpoint/resume: production is the multi-hour cost, so a spot preemption must not throw it away.
    # A resume needs BOTH a valid production checkpoint AND the built-system snapshot that produced it (reloaded
    # verbatim, never re-solvated). A checkpoint with no matching snapshot (a pre-fix leg) is un-resumable -> we
    # drop it and restart the leg cleanly (and persist a snapshot this time so future preemptions resume). ---
    # The assembler identifies the E3/target split and writes it beside the inputs. It is read HERE, before the
    # build, because build_system needs it too: the reactive-cysteine search must be restricted to the target
    # chain, or it re-runs the very defect this file's two history notes describe.
    chains_json = os.path.join(in_dir, "chains.json")
    explicit_target = None
    if os.path.exists(chains_json):
        with open(chains_json) as _f:
            explicit_target = json.load(_f).get("target_chain")

    result_s3 = env.get("RESULT_S3")
    ckpt_every = max(1, int(env.get("CKPT_EVERY_FRAMES", "50")))
    state_path, cj_path = _ckpt_paths(out_dir, leg_id, seed)
    built_paths = _built_paths(out_dir, leg_id, seed)
    resume = _load_resume(state_path, cj_path, result_s3, leg_id, seed)
    reloaded = _load_built_system(built_paths, result_s3) if resume is not None else None
    if resume is not None and reloaded is None:
        print("[nrv04-md] checkpoint present but no matching built-system snapshot -> restarting leg from frame 0",
              flush=True)
        _rm_ckpt(state_path, cj_path, result_s3)
        resume = None

    if resume is not None:
        sim, topology, meta = reloaded                         # exact persisted solvated system (atom count matches)
    else:
        sim, topology, meta = build_system(
            os.path.join(in_dir, "complex.pdb"), os.path.join(in_dir, "ligand.sdf"),
            covalent, env.get("COV_LIG_ATOM", "C6"), int(env.get("COV_RESNUM", "551")), env.get("MUTATION", ""),
            target_chain=explicit_target)
        _save_built_system(built_paths, sim, topology, meta, result_s3)   # persist so future preemptions can resume
    chain_ids, e3_chains, target_chains, lys_nz = _topology_indices(topology, target_chain=explicit_target)

    blew_up = False; blow_phase = None
    _timed_accum = 0.0; _wall_accum = 0.0
    if resume is not None:
        sim.loadState(state_path)                              # portable state -> resumes on ANY host/GPU
        e_pre = resume["e_pre"]; e_min = resume["e_min"]
        e3_side = resume["e3_side"]; tg_side = resume["tg_side"]; iface = resume["iface"]
        ref_iface = resume["ref_iface"]; ref_e3ca = resume["ref_e3ca"]; proxy = tuple(resume["proxy"])
        per_frame_contacts = resume["per_frame_contacts"]; iface_rmsds = resume["iface_rmsds"]
        lys_frames = resume["lys_frames"]; _done_frames = int(resume["done_frames"])
        _timed_accum = float(resume.get("timed_ns_accum", 0.0)); _wall_accum = float(resume.get("wall_accum", 0.0))
        print(f"[nrv04-md] RESUMED from checkpoint at frame {_done_frames}/{frames} (spot-preemption safe)", flush=True)
    else:
        # The covalent restraint imposes a stiff bond (k=3e5, eq 0.181 nm) across the co-fold's *non-bonded*
        # Sγ···C6 gap -> a large initial strain (~0.5·k·Δ² can reach tens of thousands of kJ/mol). Minimize then
        # equilibration must dissipate it; if they can't, the 4 fs HMR integrator blows up (NaN coords) and the
        # Kabsch SVD fails. Record energies + a finite guard so a blow-up is a REPORTED 'blew_up' outcome.
        e_pre = _pe_kj(sim)
        sim.minimizeEnergy()
        e_min = _pe_kj(sim)
        _pull_A = (meta.get("reactive_cys") or {}).get("sg_electrophile_dist_A")
        print(f"[nrv04-md] covalent={covalent} pull={_pull_A} Å  PE pre-min={e_pre:.4g} post-min={e_min:.4g} kJ/mol",
              flush=True)
        sim.context.setVelocitiesToTemperature(MD.TEMPERATURE_K * unit.kelvin, seed + 1)
        if equil_steps:                                        # equilibrate in chunks with a finite guard so a
            n_chunks = max(1, min(20, equil_steps // 500))     # blow-up is caught (and pinpointed) here, not later
            per = max(1, equil_steps // n_chunks); done = 0
            for _c in range(n_chunks):
                n = per if _c < n_chunks - 1 else (equil_steps - done)
                if n <= 0:
                    break
                sim.step(n); done += n
                if not _finite(sim):
                    blew_up = True; blow_phase = f"equil@{done}steps/{equil_steps}"
                    print(f"[nrv04-md] BLOW-UP in {blow_phase}: PE={_pe_kj(sim):.4g} kJ/mol", flush=True)
                    break
        # reference frame for R1 alignment (post-equil); indices are from this reference geometry
        ref_positions = _positions_nm(sim)
        e3_side, tg_side = interface_atom_indices(ref_positions, chain_ids, e3_chains, target_chains)
        iface = e3_side + tg_side
        ref_iface = [ref_positions[i] for i in iface]
        ref_e3ca = [ref_positions[i] for i in _ca_indices(topology, e3_chains)]
        proxy = _catalytic_proxy(ref_positions, chain_ids, e3_chains)
        per_frame_contacts, iface_rmsds, lys_frames = [], [], []
        _done_frames = 0
        if not blew_up:
            sim.step(stride)                                   # one warmup stride (kernel compile/JIT) before timing

    def _ckpt_state():
        return {"leg_id": leg_id, "seed": seed, "phase": "production", "frames": frames,
                "done_frames": _done_frames, "e_pre": e_pre, "e_min": e_min,
                "e3_side": e3_side, "tg_side": tg_side, "iface": iface,
                "ref_iface": ref_iface, "ref_e3ca": ref_e3ca, "proxy": list(proxy),
                "per_frame_contacts": per_frame_contacts, "iface_rmsds": iface_rmsds, "lys_frames": lys_frames,
                "timed_ns_accum": _done_frames * stride * dt_ns, "wall_accum": _wall_accum + (time.time() - _t0)}

    # ★ THE DURABLE TRAJECTORY — nr4a3-program-map.md RUNG 3's adopted requirement, wired here because this is the
    # driver whose absence of one made three analysis defects uncorrectable and forced a whole panel to be
    # re-run. Every readout below (the chain split, the reactive-Cys search, the Lys/proxy separation) becomes
    # a $0 re-derivation instead of a re-rental. See md_analysis_traj for what it does and does NOT persist.
    import md_analysis_traj as MT
    _traj_idx, _traj_lab = MT.select_analysis_atoms(topology.atoms(),
                                                    all_heavy=env.get("TRAJ_ALL_HEAVY") == "1")
    traj = MT.TrajWriter(os.path.join(out_dir, f"traj_{leg_id}_s{seed}"), _traj_idx, _traj_lab,
                         units="nm", frame_stride_steps=stride, dt_ps=dt_ns * 1000.0,
                         stride_frames=int(env.get("TRAJ_STRIDE_FRAMES", "1")),
                         enabled=env.get("TRAJ_DISABLE") != "1", s3_prefix=result_s3,
                         extra={"leg_id": leg_id, "seed": seed, "mode": mode,
                                "chain_split": {"target": sorted(target_chains), "e3": sorted(e3_chains)}}
                         ).start(resume_frames=_done_frames)
    print(f"[nrv04-md] analysis trajectory: {len(_traj_idx)} atoms, {traj.frame_bytes} B/frame "
          f"-> {os.path.basename(traj.blob_path)} (enabled={traj.enabled})", flush=True)

    _t0 = time.time(); _resumed_from = _done_frames
    for _k in range(_done_frames, frames):
        if blew_up:
            break
        sim.step(stride)
        pos = _positions_nm(sim)
        if not _np.isfinite(_np.asarray(pos)).all():           # integrator diverged -> stop, record honestly
            blew_up = True; blow_phase = f"prod@frame{_k}/{frames}"
            print(f"[nrv04-md] BLOW-UP in {blow_phase}: PE={_pe_kj(sim):.4g} kJ/mol", flush=True)
            break
        per_frame_contacts.append(_contacts(pos, e3_side, tg_side))
        cur_e3ca = [pos[i] for i in _ca_indices(topology, e3_chains)]
        cur_iface = [pos[i] for i in iface]
        iface_rmsds.append(_aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface))
        lys_frames.append([pos[i] for i in lys_nz])
        traj.append(pos, _k)                               # BEFORE the counter bump: _k is this frame's index
        _done_frames += 1
        if _done_frames % ckpt_every == 0 and _done_frames < frames:     # continuous checkpoint -> S3
            _save_ckpt(sim, state_path, cj_path, _ckpt_state(), result_s3, traj)
            print(f"[nrv04-md] checkpoint @ frame {_done_frames}/{frames} -> S3", flush=True)

    _wall_accum += max(1e-6, time.time() - _t0)                # active-compute wall (excludes idle/preemption gaps)
    _timed_ns = _done_frames * stride * dt_ns
    _prod_wall_s = max(1e-6, _wall_accum)
    ns_per_day = round(_timed_ns / (_prod_wall_s / 86400.0), 2) if _done_frames else 0.0  # throughput -> $/ns
    print(f"[nrv04-md] production throughput: {ns_per_day} ns/day ({_timed_ns:.4f} ns in {_prod_wall_s:.1f}s active, "
          f"{_done_frames}/{frames} frames, resumed_from={_resumed_from}, blew_up={blew_up})", flush=True)

    # readouts (guarded: a blow-up may leave zero/partial frames -> report None, not a divide-by-zero crash)
    import nrv04_readouts as R
    r2 = R.recruitment(per_frame_contacts) if per_frame_contacts else {"recruited": None, "note": "no frames"}
    if iface_rmsds:
        _tail = iface_rmsds[len(iface_rmsds) // 2:]
        r1 = {"rmsd_series_mean": round(sum(iface_rmsds) / len(iface_rmsds), 3),
              "plateau_A": round(sum(_tail) / max(1, len(_tail)), 3)}
        r1["stable"] = r1["plateau_A"] < R.INTERFACE_RMSD_STABLE_A
    else:
        r1 = {"rmsd_series_mean": None, "plateau_A": None, "stable": False, "note": "no frames (blew up)"}
    # ⚠ UNITS. nrv04_readouts' contract is ÅNGSTRÖM ("frames are lists of (x,y,z) tuples, Å") but everything in
    # this driver is in NANOMETRES. R1 converts explicitly (`* 10.0  # nm -> Å` in _aligned_iface_rmsd); R3 did
    # not, so every reported `min_A` was a nanometre value wearing an Ångström label — a silent factor of 10.
    # Caught 2026-07-25 by recomputing R3 independently from the persisted starting systems: the committed
    # warhead_only legs report min_A = 2.34/2.44 against an independent t=0 distance of 25.21 Å, and the
    # cov/noncov/active legs report 4.0–4.48 against 48.92 Å. The ratio is ~10 at BOTH well-separated values,
    # and is ≥10 exactly as a trajectory minimum should be. Reported R3 distances were therefore ~10× too small
    # — which reads as ubiquitination-competent geometry when the real Lys Nζ–proxy separation is ~30–49 Å.
    _lys_A = [[(x * 10.0, y * 10.0, z * 10.0) for (x, y, z) in fr] for fr in lys_frames]
    _proxy_A = (proxy[0] * 10.0, proxy[1] * 10.0, proxy[2] * 10.0)
    r3 = R.lys_presentation(_lys_A, _proxy_A) if (lys_nz and lys_frames) else {"min_A": None, "note": "no target Lys/frames"}

    result = {"panel": env.get("PANEL", "nrv04_covalent_feasibility"), "leg_id": leg_id, "seed": seed, "mode": mode,
              # RECORD the chain split the readouts were computed against. The panel that ran before this field
              # existed could not be audited from its own output — the split had to be reconstructed from the
              # co-fold CIFs — which is exactly why it is recorded now.
              "chain_split": {"target": sorted(target_chains), "e3": sorted(e3_chains),
                              "explicit": explicit_target is not None, "target_lys_nz": len(lys_nz)},
              "covalent": covalent, "mutation": env.get("MUTATION", ""), "meta": meta,
              "md_settings": MD.summary(),                     # RECORD the exact canonical hyperparameters used
              "prod_ns": prod_ns, "equil_ns": equil_ns,
              "blew_up": blew_up, "blow_phase": blow_phase,    # numerical-stability outcome (covalent-pull strain)
              "pe_pre_min_kj": round(e_pre, 1), "pe_post_min_kj": round(e_min, 1),
              "ns_per_day": ns_per_day, "timed_ns": round(_timed_ns, 5), "prod_wall_s": round(_prod_wall_s, 1),
              "n_frames": len(per_frame_contacts), "R1_interface": r1, "R2_recruitment": r2, "R3_lys": r3,
              # The durable trajectory's own receipt. It is IN THE RESULT, not just in the log, so a leg that
              # silently failed to persist coordinates is visible in the same artifact the collector reads —
              # the panel that had no trajectory also had nothing that SAID it had none.
              "analysis_traj": traj.summary()}
    out = os.path.join(out_dir, f"leg_{leg_id}_s{seed}.json")
    json.dump(result, open(out, "w"), indent=2)
    print(f"[nrv04-md] wrote {out}: recruited={r2['recruited']} stable={r1['stable']} "
          f"traj_frames={traj.n_written}", flush=True)
    traj.mirror(_s3_cp)                                        # final push BEFORE the checkpoint is dropped
    _rm_ckpt(state_path, cj_path, result_s3)                   # leg finished -> drop the checkpoint (a re-dispatch
    return result                                             # should re-run cleanly, not resume a completed leg)


def _aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface):
    """R1 per-frame: superpose the current frame's E3 CAs onto the reference, apply to the interface atoms,
    RMSD in Å. Uses the E3 CA superposition so the metric captures target motion relative to E3."""
    import numpy as np
    P = np.asarray(cur_e3ca); Q = np.asarray(ref_e3ca)
    if not (np.isfinite(P).all() and np.isfinite(Q).all()):    # non-finite coords -> caller's finite guard handles it
        return float("nan")
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    try:
        V, _, Wt = np.linalg.svd(Pc.T @ Qc)
    except np.linalg.LinAlgError:                              # ill-conditioned covariance -> skip this frame's R1
        return float("nan")
    d = np.sign(np.linalg.det(V @ Wt))
    U = V @ np.diag([1, 1, d]) @ Wt
    ci = (np.asarray(cur_iface) - P.mean(0)) @ U
    ri = np.asarray(ref_iface) - Q.mean(0)
    return float(np.sqrt(np.mean(np.sum((ci - ri) ** 2, axis=1))) * 10.0)   # nm -> Å


def _contacts(pos, e3_side, tg_side, cutoff_nm=0.45):
    c2 = cutoff_nm ** 2; n = 0
    for i in e3_side:
        xi = pos[i]
        for j in tg_side:
            xj = pos[j]
            if (xi[0] - xj[0]) ** 2 + (xi[1] - xj[1]) ** 2 + (xi[2] - xj[2]) ** 2 <= c2:
                n += 1
    return n


def _positions_nm(sim):
    from openmm import unit
    return [(v.x, v.y, v.z) for v in sim.context.getState(getPositions=True).getPositions().value_in_unit(unit.nanometer)]


def _topology_indices(topology, target_chain=None):
    """Split the topology into E3 and degradation-target atoms.

    ⚠ HISTORY — READ BEFORE CHANGING. This function used to derive the split POSITIONALLY: "E3 are the first
    assembled chains, the target LBD is the LAST protein chain". That convention was never true of the co-folds
    it was applied to. nrv04_ternary.py builds its YAML as `proteins = [("A", target_lbd)] + e3`, i.e. the
    TARGET IS FIRST, so the positional rule selected the last chain — Elongin C, a 112-residue E3 subunit — as
    "the target". Every R1/R2/R3 readout of the covalent feasibility panel therefore described the ElonginC↔rest
    interface rather than the VHL↔NR4A one, and nothing errored: the numbers were simply about something else.
    Proof from the panel's own committed artifacts (2026-07-24 audit): the reactive cysteine, which is resolved
    independently BY GEOMETRY and sits on the NR4A1 LBD, is recorded on chain **A** in 12 of 14 legs, while the
    positional rule pointed at chain G.

    So the split is now EXPLICIT: `target_chain` comes from the assembler's chains.json, which identifies it by
    matching every other chain to a known E3 component (nrv04_covalent_assemble.identify_chains). The positional
    fallback is kept only for inputs that predate chains.json, and it SHOUTS, because a silent fallback to the
    rule that caused this is the one outcome worth preventing."""
    chain_ids = [a.residue.chain.id for a in topology.atoms()]
    prot_chains = sorted({a.residue.chain.id for a in topology.atoms()
                          if a.residue.name not in ("HOH", "NA", "CL", "UNK", "LIG", "UNL")})
    if target_chain and target_chain in prot_chains:
        target_chains = {target_chain}
        e3_chains = set(prot_chains) - target_chains
    else:
        if target_chain:
            print(f"[nrv04-md] WARN chains.json named target chain {target_chain!r}, absent from the topology "
                  f"{prot_chains} — falling back to the POSITIONAL rule", flush=True)
        else:
            print(f"[nrv04-md] WARN no explicit target chain supplied; falling back to the POSITIONAL rule "
                  f"(last of {prot_chains}). This rule mis-selected Elongin C as the target in the covalent "
                  f"feasibility panel — verify the readouts describe the interface you intend.", flush=True)
        e3_chains = set(prot_chains[:-1]) if len(prot_chains) > 1 else set(prot_chains)
        target_chains = {prot_chains[-1]} if len(prot_chains) > 1 else set()
    lys_nz = [a.index for a in topology.atoms()
              if a.residue.name == "LYS" and a.name == "NZ" and a.residue.chain.id in target_chains]
    print(f"[nrv04-md] chain split: target={sorted(target_chains)} e3={sorted(e3_chains)} "
          f"target_lys_nz={len(lys_nz)}", flush=True)
    return chain_ids, e3_chains, target_chains, lys_nz


def _ca_indices(topology, chains):
    return [a.index for a in topology.atoms() if a.name == "CA" and a.residue.chain.id in chains]


def _catalytic_proxy(positions_nm, chain_ids, e3_chains):
    """Coarse E2~Ub-presentation proxy: centroid of the E3 (VHL) chains (R3 is descriptive only, not a gate)."""
    pts = [positions_nm[i] for i, c in enumerate(chain_ids) if c in e3_chains]
    n = len(pts) or 1
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)


def main():
    env = dict(os.environ)
    if "LEG_ID" not in env:
        raise SystemExit("[nrv04-md] LEG_ID not set (run via nrv04_covalent_panel.leg_env)")
    run_leg(env)


if __name__ == "__main__":
    sys.exit(main())
