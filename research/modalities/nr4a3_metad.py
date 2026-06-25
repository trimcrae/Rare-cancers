#!/usr/bin/env python3
"""
NR4A3 LBD well-tempered metadynamics — cryptic-pocket opening (GPU experiment #1, enhanced sampling).

Unbiased 10 ns MD showed Pocket-5 only breathing (max +3.3 nm^2 SASA, no clear opening). Metadynamics
actively biases a collective variable that tracks the pocket opening, so a cryptic opening that would
take microseconds of plain MD is reached in tens of ns — and yields a FREE-ENERGY profile (the cost of
opening), a stronger druggability argument than a single spontaneous event.

CV: radius of gyration of the Calpha atoms of the Pocket-5 lining residues enumerated by fpocket on
the AF2 model (nr4a3_fpocket_enumerate.py -> pocket5_lining_residues.json):
    406, 407, 410, 411, 412, 481, 484, 485, 531, 534   (incl. all 7 selectivity handles)
Opening the collapsed pocket spreads these residues apart -> Rg rises. Well-tempered metadynamics fills
the closed basin and drives Rg outward, bounded by walls to prevent unfolding artifacts.

Same validated stack as nr4a3_md.py (conda-forge CUDA OpenMM, forced CUDA platform). Adds openmm-plumed.

CHECKPOINT / RESTART (so GPU time is never lost and runs are reproducible for the paper appendix):
every run writes a serialized base System (metad_system.xml), the solvated topology
(nr4a3-lbd-solvated.pdb), an OpenMM checkpoint (metad_checkpoint.chk) + a portable state
(metad_state.xml), the PLUMED bias (HILLS) and CV trace (COLVAR), the trajectory, fes.dat, and a
manifest (metad_manifest.json: CV + metad params + cumulative biased ns + git sha). If a follow-on run
finds these files (placed back here by entry_metad.py --resume-from), it rebuilds the *identical*
system, re-attaches PLUMED with RESTART (which re-reads HILLS and keeps depositing), loads the
checkpoint, and continues — skipping minimise/equilibrate. A resume is REFUSED if the CV or metad
parameters differ from the prior manifest (the existing HILLS would be invalid for new settings).
So 30 ns = 5 + 25, or extend 30 -> 60, is identical to one continuous run and costs only the extra ns.

Output: COLVAR, HILLS, the trajectory, the solvated PDB, fes.dat (free energy vs Rg via plumed
sum_hills), plus the checkpoint/state/system/manifest restart set. Post-process opened-state frames
with the existing fpocket/SASA analysis.
"""
import json
import os
import subprocess
import sys

LBD_FIRST, LBD_LAST = 373, 626
CV_RESIDUES = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]   # from pocket5_lining_residues.json
AF2_PDB = os.path.join(os.path.dirname(__file__), "AF-Q92570.pdb")
NS = float(os.environ.get("NS", "30"))           # nanoseconds of biased MD to add THIS segment
HERE = os.path.dirname(os.path.abspath(__file__))

# Reproducibility artifacts == the resume inputs. A run writes these; a follow-on run that finds them
# (placed back in HERE by entry_metad.py --resume-from) continues from the saved state + accumulated bias.
SYSTEM_XML   = os.path.join(HERE, "metad_system.xml")        # serialized base System (NO PlumedForce)
SOLVATED_PDB = os.path.join(HERE, "nr4a3-lbd-solvated.pdb")  # solvated topology + reference coords
CHECKPOINT   = os.path.join(HERE, "metad_checkpoint.chk")    # OpenMM binary checkpoint (fast resume)
STATE_XML    = os.path.join(HERE, "metad_state.xml")         # portable state (archival / cross-env)
HILLS        = os.path.join(HERE, "HILLS")                   # PLUMED deposited Gaussians (the bias)
COLVAR       = os.path.join(HERE, "COLVAR")                  # CV + bias vs time
DCD          = os.path.join(HERE, "nr4a3-lbd-metad.dcd")     # trajectory
FES          = os.path.join(HERE, "fes.dat")                 # free energy vs Rg
MANIFEST     = os.path.join(HERE, "metad_manifest.json")     # params + cumulative ns + git sha

# Well-tempered metadynamics parameters — shared by the PLUMED script AND the reproducibility manifest.
# A resume is refused unless these match the prior segment (else the existing HILLS is meaningless).
METAD = {
    "sigma": 0.03, "height": 1.0, "pace": 500, "biasfactor": 10, "temp": 310,
    "grid_min": 0.4, "grid_max": 3.0, "grid_bin": 260,
    "lower_wall": 0.6, "upper_wall": 2.2, "wall_kappa": 2000,
}

# Amino-acid residue names (for identifying the protein chain after solvation).
_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
       "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE", "HIP", "CYX", "HSD", "HSE"}


def main():
    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        from pdbfixer import PDBFixer
        from openmmplumed import PlumedForce
    except ImportError as e:  # noqa: BLE001
        print(f"  needs openmm + pdbfixer + openmm-plumed (GPU box): {e}", file=sys.stderr)
        return

    _fetch_af_model()

    # Ground-truth residue identities (UniProt numbering) read straight from the AF2 model. Used below
    # to assert the CV CA atoms in the solvated topology really are residues 406...534 — a count match
    # alone wouldn't catch a contiguity shift (ASSUMPTIONS.md #7) selecting the wrong residues.
    cv_identities = _af2_residue_names(AF2_PDB, CV_RESIDUES)
    missing = [r for r in CV_RESIDUES if r not in cv_identities]
    if missing:
        sys.exit(f"  ABORT: CV residues {missing} absent from the AF2 model {AF2_PDB}")
    print(f"  CV residue identities (AF2, UniProt numbering): {cv_identities}", file=sys.stderr)

    resume = _resume_ready()
    if resume:
        _check_resume_params()   # aborts if CV/METAD changed since the prior segment
        prior_ns = float(_read_manifest().get("cumulative_ns", 0.0))
        print(f"  RESUME: continuing from saved checkpoint + HILLS (prior {prior_ns} ns)",
              file=sys.stderr)
        topology, positions, system = _load_base_for_resume(mm, app)
    else:
        prior_ns = 0.0
        topology, positions, system = _build_fresh(mm, app, unit, PDBFixer)

    # --- PLUMED well-tempered metadynamics on Rg of the CV-residue CA atoms -----------------------
    plumed_atoms = _cv_ca_plumed_indices(topology, cv_identities)
    if len(plumed_atoms) != len(CV_RESIDUES):
        sys.exit(f"  ABORT: matched {len(plumed_atoms)}/{len(CV_RESIDUES)} CV CA atoms "
                 "(residue numbering mismatch in the solvated topology)")
    print(f"  CV: Rg of {len(plumed_atoms)} CA atoms (PLUMED 1-based idx): {plumed_atoms}",
          file=sys.stderr)
    system.addForce(PlumedForce(_plumed_script(plumed_atoms, restart=resume)))

    integrator = mm.LangevinMiddleIntegrator(METAD["temp"] * unit.kelvin, 1.0 / unit.picosecond,
                                             2.0 * unit.femtosecond)
    # Force CUDA (no silent CPU fallback) — same rule as nr4a3_md.py.
    try:
        cuda = mm.Platform.getPlatformByName("CUDA")
        sim = app.Simulation(topology, system, integrator, cuda, {"Precision": "mixed"})
    except Exception as e:  # noqa: BLE001
        print(f"  ABORT: CUDA platform unavailable/uninitializable: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"  OpenMM platform: {sim.context.getPlatform().getName()}", file=sys.stderr)

    if resume:
        _load_checkpoint(sim, mm)        # positions + velocities + box; no minimise / equilibrate
    else:
        sim.context.setPositions(positions)
        print("  minimizing...", file=sys.stderr)
        sim.minimizeEnergy()
        minpos = sim.context.getState(getPositions=True).getPositions()
        app.PDBFile.writeFile(topology, minpos, open(SOLVATED_PDB, "w"))

        # Pre-flight (ASSUMPTIONS.md #5): the CV's starting Rg must sit inside the wall/grid window,
        # else the bias is mis-scaled or the walls clip the basin before any GPU time is spent.
        rg0 = _rg_nm(minpos, plumed_atoms, unit)
        print(f"  INITIAL CV Rg = {rg0:.3f} nm  (walls {METAD['lower_wall']}-{METAD['upper_wall']}, "
              f"grid {METAD['grid_min']}-{METAD['grid_max']}, SIGMA {METAD['sigma']})", file=sys.stderr)
        if not (METAD["lower_wall"] < rg0 < METAD["upper_wall"]):
            sys.exit(f"  ABORT: initial Rg {rg0:.3f} nm is outside the wall window "
                     f"[{METAD['lower_wall']}, {METAD['upper_wall']}] — retune walls/grid first.")
        if (rg0 < METAD["lower_wall"] + 5 * METAD["sigma"]
                or rg0 > METAD["upper_wall"] - 5 * METAD["sigma"]):
            print(f"  WARNING: initial Rg {rg0:.3f} nm is within 5*SIGMA of a wall; basin may clip.",
                  file=sys.stderr)

        sim.context.setVelocitiesToTemperature(METAD["temp"] * unit.kelvin)
        print("  NPT equilibration (200 ps)...", file=sys.stderr)
        sim.step(100000)

    steps = int(NS * 1e6 / 2)
    sim.reporters.append(app.DCDReporter(DCD, 25000, append=resume))   # continue the same trajectory
    sim.reporters.append(app.CheckpointReporter(CHECKPOINT, 50000))    # crash-safe checkpoint / 100 ps
    sim.reporters.append(app.StateDataReporter(sys.stdout, 50000, step=True,
                         temperature=True, potentialEnergy=True, speed=True))
    print(f"  metadynamics {'RESUME ' if resume else ''}segment {NS} ns ({steps} steps) -> {DCD}",
          file=sys.stderr)
    sim.step(steps)

    # Persist the restart + reproducibility set.
    sim.saveCheckpoint(CHECKPOINT)
    with open(STATE_XML, "w") as fh:
        fh.write(mm.XmlSerializer.serialize(
            sim.context.getState(getPositions=True, getVelocities=True, enforcePeriodicBox=True)))
    _sum_hills()
    cumulative = prior_ns + NS
    _write_manifest(cumulative, plumed_atoms)
    print(f"  done. cumulative biased time: {cumulative} ns. Wrote checkpoint/state/system/manifest + "
          f"HILLS/COLVAR/fes.dat. Extend by feeding this output dir back via --resume-from.",
          file=sys.stderr)


def _build_fresh(mm, app, unit, PDBFixer):
    """Build the solvated NR4A3 LBD system from the AF2 model; serialize the base System (sans PLUMED,
    with the barostat) so a resume reconstructs it identically. Returns (topology, positions, system)."""
    lbd_pdb = os.path.join(HERE, "nr4a3-lbd.pdb")
    with open(AF2_PDB) as fh, open(lbd_pdb, "w") as out:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    rid = int(line[22:26])
                except ValueError:
                    continue
                if LBD_FIRST <= rid <= LBD_LAST:
                    out.write(line)
        out.write("END\n")

    fixer = PDBFixer(filename=lbd_pdb)
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)

    modeller = app.Modeller(fixer.topology, fixer.positions)
    ff = app.ForceField("amber14-all.xml", "amber14/tip3pfb.xml")
    modeller.addSolvent(ff, model="tip3p", padding=1.0 * unit.nanometer,
                        ionicStrength=0.15 * unit.molar, neutralize=True)
    system = ff.createSystem(modeller.topology, nonbondedMethod=app.PME,
                             nonbondedCutoff=1.0 * unit.nanometer, constraints=app.HBonds)
    # NPT: the barostat is part of the reproducible base System (serialized below; PLUMED is added
    # separately each run so RESTART can be toggled without re-serializing a custom force).
    system.addForce(mm.MonteCarloBarostat(1 * unit.bar, METAD["temp"] * unit.kelvin))
    with open(SYSTEM_XML, "w") as fh:
        fh.write(mm.XmlSerializer.serialize(system))
    return modeller.topology, modeller.positions, system


def _load_base_for_resume(mm, app):
    """Reconstruct the identical base System + topology from the serialized resume artifacts."""
    pdb = app.PDBFile(SOLVATED_PDB)
    with open(SYSTEM_XML) as fh:
        system = mm.XmlSerializer.deserialize(fh.read())
    return pdb.topology, pdb.positions, system


def _load_checkpoint(sim, mm):
    """Restore positions/velocities/box: prefer the binary checkpoint, fall back to portable state.xml."""
    if os.path.exists(CHECKPOINT):
        try:
            with open(CHECKPOINT, "rb") as fh:
                sim.context.loadCheckpoint(fh.read())
            print("  loaded binary checkpoint", file=sys.stderr)
            return
        except Exception as e:  # noqa: BLE001 — fall through to the portable state
            print(f"  checkpoint load failed ({e}); trying portable state.xml", file=sys.stderr)
    with open(STATE_XML) as fh:
        sim.context.setState(mm.XmlSerializer.deserialize(fh.read()))
    print("  loaded portable state.xml", file=sys.stderr)


def _plumed_script(plumed_atoms, restart):
    """Build the PLUMED well-tempered metadynamics input. With restart=True, prepend RESTART so METAD
    re-reads the existing HILLS (continuing the bias) and PRINT appends to COLVAR."""
    m = METAD
    lines = ["RESTART"] if restart else []
    lines += [
        "UNITS LENGTH=nm ENERGY=kj/mol TIME=ps",
        f"cv: GROUP ATOMS={','.join(str(i) for i in plumed_atoms)}",
        "rg: GYRATION TYPE=RADIUS ATOMS=cv",
        # well-tempered: small Gaussians every PACE steps, bias factor 10 at 310 K
        f"metad: METAD ARG=rg SIGMA={m['sigma']} HEIGHT={m['height']} PACE={m['pace']} "
        f"BIASFACTOR={m['biasfactor']} TEMP={m['temp']} GRID_MIN={m['grid_min']} "
        f"GRID_MAX={m['grid_max']} GRID_BIN={m['grid_bin']} FILE={HILLS}",
        # walls keep the CV physical: don't collapse below ~closed, don't unfold beyond ~open
        f"lwall: LOWER_WALLS ARG=rg AT={m['lower_wall']} KAPPA={m['wall_kappa']}",
        f"uwall: UPPER_WALLS ARG=rg AT={m['upper_wall']} KAPPA={m['wall_kappa']}",
        f"PRINT ARG=rg,metad.bias STRIDE={m['pace']} FILE={COLVAR}",
    ]
    return "\n".join(lines)


def _resume_ready():
    """True iff a complete restart set is present (entry_metad.py --resume-from staged it into HERE)."""
    return (os.path.exists(SYSTEM_XML) and os.path.exists(SOLVATED_PDB) and os.path.exists(HILLS)
            and (os.path.exists(CHECKPOINT) or os.path.exists(STATE_XML)))


def _check_resume_params():
    """Refuse to resume if the CV residues or metad parameters changed — the prior HILLS would be
    invalid for new settings, silently corrupting the free-energy surface."""
    prior = _read_manifest()
    if not prior:
        return
    if prior.get("cv_residues") != CV_RESIDUES or prior.get("metad") != METAD:
        sys.exit("  ABORT: resume parameters differ from the prior manifest (CV residues or metad "
                 "settings changed). The existing HILLS is invalid for these settings — start a fresh "
                 "run (don't pass --resume-from) instead.")


def _write_manifest(cumulative_ns, plumed_atoms):
    man = {
        "cv_residues": CV_RESIDUES,
        "metad": METAD,
        "segment_ns": NS,
        "cumulative_ns": round(cumulative_ns, 3),
        "plumed_ca_indices": plumed_atoms,
        "git_ref": os.environ.get("GIT_REF", ""),
        "git_sha": os.environ.get("GIT_SHA", ""),
    }
    with open(MANIFEST, "w") as fh:
        json.dump(man, fh, indent=2)


def _read_manifest():
    try:
        with open(MANIFEST) as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {}


def _af2_residue_names(pdb_path, residues):
    """{resSeq: 3-letter resName} for the requested residues, read from a PDB in its own numbering."""
    want, names = set(residues), {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            try:
                rid = int(line[22:26])
            except ValueError:
                continue
            if rid in want:
                names[rid] = line[17:20].strip()
    return names


def _cv_ca_plumed_indices(topology, cv_identities):
    """CA atom indices (PLUMED 1-based) of the CV residues, via the unit-tested residue resolver
    (handles the solvated PDB being renumbered from 1 vs. preserving AF2 numbering). Asserts each
    selected residue's NAME matches the AF2 ground truth (`cv_identities`), so a contiguity shift
    (ASSUMPTIONS.md #7) that picked the wrong residue is caught here, not discovered in the results."""
    import residue_map as rm
    prot_residues = [r for r in topology.residues() if r.name in _AA]
    # OpenMM topology Residue exposes the PDB residue number as `.id` (a string), not `.resSeq`
    # (that is an mdtraj attribute) — cast to int for the resolver.
    resseqs = [int(r.id) for r in prot_residues]
    positions, label = rm.resolve_positions(resseqs, CV_RESIDUES, LBD_FIRST)
    out = []
    for i in positions:
        # which CV residue is this position supposed to be, under the resolver's chosen scheme?
        cv_res = resseqs[i] if label == "resSeq-preserved" else LBD_FIRST + i
        expected = cv_identities.get(cv_res)
        got = prot_residues[i].name
        # normalise protonation/variant names (HID/HIE/HIP->HIS, CYX->CYS) for the identity check
        norm = {"HID": "HIS", "HIE": "HIS", "HIP": "HIS", "HSD": "HIS", "HSE": "HIS", "CYX": "CYS"}
        if expected is not None and norm.get(got, got) != norm.get(expected, expected):
            sys.exit(f"  ABORT: CV residue {cv_res} ({label}) is {got} in the solvated topology but "
                     f"{expected} in the AF2 model — residue mapping is wrong, not selecting 406...534.")
        ca = next((a for a in prot_residues[i].atoms() if a.name == "CA"), None)
        if ca is not None:
            out.append(ca.index + 1)            # PLUMED indices are 1-based
    return out


def _rg_nm(positions, plumed_atoms, unit):
    """Radius of gyration (nm) of the CV CA atoms, from OpenMM positions. `plumed_atoms` are 1-based."""
    idx = [i - 1 for i in plumed_atoms]
    xyz = [positions[i].value_in_unit(unit.nanometer) for i in idx]
    n = len(xyz)
    cx = sum(p[0] for p in xyz) / n
    cy = sum(p[1] for p in xyz) / n
    cz = sum(p[2] for p in xyz) / n
    msd = sum((p[0] - cx) ** 2 + (p[1] - cy) ** 2 + (p[2] - cz) ** 2 for p in xyz) / n
    return msd ** 0.5


def _sum_hills():
    """Reconstruct the free-energy profile F(Rg) with `plumed sum_hills` (best-effort)."""
    import shutil
    if not shutil.which("plumed") or not os.path.exists(HILLS):
        return
    try:
        subprocess.run(["plumed", "sum_hills", "--hills", HILLS, "--outfile", FES],
                       cwd=HERE, check=False, timeout=600)
    except Exception as e:  # noqa: BLE001
        print(f"  sum_hills skipped: {e}", file=sys.stderr)


def _fetch_af_model():
    if os.path.exists(AF2_PDB):
        return
    import json
    import urllib.request
    import urllib.error
    acc = "Q92570"
    try:
        with urllib.request.urlopen(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}", timeout=60) as r:
            meta = json.load(r)
        pdb_url = (meta[0] or {}).get("pdbUrl") if meta else None
        if pdb_url:
            urllib.request.urlretrieve(pdb_url, AF2_PDB)
            return
    except Exception as e:  # noqa: BLE001
        print(f"  AFDB API lookup failed ({e}); trying versioned URLs", file=sys.stderr)
    for v in ("v6", "v5", "v4", "v3", "v2", "v1"):
        try:
            urllib.request.urlretrieve(
                f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.pdb", AF2_PDB)
            return
        except urllib.error.HTTPError:
            continue
    sys.exit(f"  ABORT: could not fetch the AlphaFold model for {acc}.")


if __name__ == "__main__":
    main()
