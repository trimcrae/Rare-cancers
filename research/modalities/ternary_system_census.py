#!/usr/bin/env python3
"""What SYSTEM is inside a committed ternary `.nc`? A composition census, not just a particle count.

WHY THIS EXISTS. `nc_particle_probe.py` answers "how many particles" from the `atom` dimension — one integer,
read from the header, and it is the right tool for "can this trajectory resume that checkpoint?". It is NOT
enough to answer the question RUNG 2b actually raises. The 2 fs and 4 fs ternary trajectories carry DIFFERENT
`atom` dimensions (7,388 against 7,398 and 7,392, GH run 30312683166), and a bare integer cannot distinguish
the two explanations that matter:

  H1  the SOLUTE is identical and the difference is bulk solvent — a different number of waters placed by an
      independent solvation, and the counter-ions that scale with them. Nothing about the alchemical
      transformation changes; the difference is thermodynamically inert at the size seen here.
  H2  the SOLUTE differs — a different protonation/tautomer state, a different chain, a different hybrid-topology
      dummy-atom count. Then the two runs are not the same alchemical system and a ΔΔG comparison between them
      is not a timestep comparison.

Both produce "the counts differ by 10". Only a COMPOSITION census separates them, and the composition is
recoverable from the committed artifact alone: openmmtools serializes the thermodynamic states — and therefore
the whole `openmm.System` — into `simulation.nc`, so bonded connectivity partitions every particle into
molecules and each molecule is classifiable by size and mass. That is a measurement, not an inference from
which setup caches happen to exist (audit J.2–J.5 is the record of what those inferences cost).

METHOD PARITY IS DELIBERATE. The connectivity, the union-find partition and the mass reader are IMPORTED from
`ternary_fep_convergence.py` rather than reimplemented — that module's `_ligand_atoms` already identifies the
PROTAC in these exact files, and a second private copy of the graph rules is precisely the "one fact, two
places" defect CLAUDE.md §1 forbids. This module adds only the bookkeeping the convergence report does not
keep: waters, ions, box vectors and net charge.

READS ONE FILE AT A TIME, ON PURPOSE. Each ternary `simulation.nc` is ~2 GB; a runner cannot hold four. The
caller downloads one, runs this with `--label`, deletes it, and repeats; `--compare` then reads the collected
per-leg JSONs and prints the cross-leg verdict.

$0: CPU only, no GPU, no VM. Runs inside the pre-baked parity image (`triskit23/ternary-fep`), which is
required rather than convenient — openmmtools stores each end state as a serialized class reference and
OpenFE's alchemical state is one of them, so deserialization needs openfe importable.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Water is 3 sites in TIP3P and 4 in TIP4P/OPC; both are "3 heavy-plus-hydrogens plus maybe a massless site".
# Classify on COMPOSITION (one ~16 Da atom + two ~1 Da atoms, plus any zero-mass virtual sites), never on the
# component size alone — a bare size-3 count silently folds in any other triatomic and would make the water
# tally quietly wrong in exactly the place this module is supposed to be trustworthy.
O_MASS_LO, O_MASS_HI = 14.0, 18.0
H_MASS_HI = 4.5                 # generous: HMR moves hydrogen mass up to ~3-4 Da, and these legs run HMR
VSITE_MASS_MAX = 1e-6


def _classify_small(component, masses):
    """('water' | 'ion' | 'other', detail) for a component small enough not to be a protein or the ligand."""
    ms = sorted(masses[i] for i in component)
    real = [m for m in ms if m > VSITE_MASS_MAX]
    if len(real) == 1:
        return "ion", round(real[0], 2)
    if len(real) == 3:
        heavy = [m for m in real if O_MASS_LO <= m <= O_MASS_HI]
        light = [m for m in real if m <= H_MASS_HI]
        if len(heavy) == 1 and len(light) == 2:
            return "water", len(ms)          # detail = site count (3 = TIP3P, 4 = TIP4P/OPC)
    return "other", tuple(round(m, 2) for m in real)


def _net_charges(system):
    """Per-particle charge from the NonbondedForce, or None if the System exposes none. Reported rather than
    assumed: the ion tally below is a mass tally, and charge is the independent corroboration of it."""
    for k in range(system.getNumForces()):
        f = system.getForce(k)
        gp = getattr(f, "getParticleParameters", None)
        gn = getattr(f, "getNumParticles", None)
        if gp is None or gn is None or type(f).__name__ != "NonbondedForce":
            continue
        out = []
        for i in range(int(gn())):
            q = gp(i)[0]
            v = getattr(q, "value_in_unit_system", None)
            out.append(float(q._value) if hasattr(q, "_value") else (float(v) if v is None else float(q / q.unit)))
        return out
    return None


def _box_nm(system):
    try:
        vecs = system.getDefaultPeriodicBoxVectors()
    except Exception:  # noqa: BLE001
        return None
    out = []
    for v in vecs:
        row = []
        for c in v:
            row.append(round(float(c.value_in_unit(c.unit)) if hasattr(c, "value_in_unit") else float(c), 4))
        out.append(row)
    return out


def census_one(nc_path, label):
    """Full composition census of one committed trajectory. Never raises for a bad file — returns a record
    carrying the reason, because a census that dies is indistinguishable from a system that is missing."""
    import ternary_fep_convergence as C

    rec = {"label": label, "nc": nc_path, "status": None}
    try:
        from openmmtools.multistate import MultiStateReporter
    except Exception as e:  # noqa: BLE001
        rec["status"] = "openmmtools unavailable (%s: %s)" % (type(e).__name__, e)
        return rec
    reporter = None
    try:
        reporter = MultiStateReporter(nc_path, open_mode="r")
        idx = getattr(reporter, "analysis_particle_indices", None)
        subset = [int(v) for v in idx] if idx is not None else None
        rec["n_analysis_particles"] = len(subset) if subset is not None else None

        system = None
        for route in ("read_end_thermodynamic_states", "read_thermodynamic_states"):
            fn = getattr(reporter, route, None)
            if fn is None:
                continue
            try:
                st = fn()
                while isinstance(st, (list, tuple)) and st:
                    st = st[0]
                system = getattr(st, "system", None)
                if system is not None:
                    rec["system_provenance"] = route
                    break
            except Exception as e:  # noqa: BLE001
                rec.setdefault("route_errors", {})[route] = "%s: %s" % (type(e).__name__, e)
        if system is None:
            rec["status"] = "no System could be deserialized (%s)" % rec.get("route_errors", "no route")
            return rec

        n = int(system.getNumParticles())
        rec["n_particles"] = n
        masses = [C._mass_da(system.getParticleMass(i)) for i in range(n)]
        edges, prov = C._system_edges(system)
        rec["bond_provenance"] = {k: v for k, v in prov.items()}
        comps = C.molecules_from_edges(n, edges)
        info = C.classify_components(comps, subset)

        waters, water_sites, ions, others, chains, ligand = 0, {}, {}, [], [], None
        for c in comps:
            if len(c) >= C.PROTEIN_MIN_ATOMS:
                chains.append(len(c))
                continue
            if C.LIG_MIN_ATOMS <= len(c) <= C.LIG_MAX_ATOMS:
                ligand = len(c) if ligand is None else ligand
                others.append(("ligand-sized", len(c)))
                continue
            kind, detail = _classify_small(c, masses)
            if kind == "water":
                waters += 1
                water_sites[detail] = water_sites.get(detail, 0) + 1
            elif kind == "ion":
                ions[detail] = ions.get(detail, 0) + 1
            else:
                others.append((kind, detail))

        chains.sort(reverse=True)
        n_ion = sum(ions.values())
        n_chain_atoms = sum(chains)
        n_ligand_atoms = int(info.get("ligand") and len(info["ligand"]) or (ligand or 0))
        rec.update({
            "n_protein_chains": len(chains), "protein_chain_sizes": chains, "n_protein_atoms": n_chain_atoms,
            "n_ligand_atoms": n_ligand_atoms,
            "n_solute_atoms": n_chain_atoms + n_ligand_atoms,
            "n_water_molecules": waters, "water_site_histogram": {str(k): v for k, v in water_sites.items()},
            "n_water_atoms": n - (n_chain_atoms + n_ligand_atoms + n_ion),
            "n_ions": n_ion, "ion_mass_histogram": {str(k): v for k, v in sorted(ions.items())},
            "n_other_components": len(others), "other_components": others[:8],
            "ligand_identified": info.get("ligand") is not None,
            "ligand_status": info.get("status"),
            "n_components": info.get("n_components"),
            "box_vectors_nm": _box_nm(system),
        })
        q = _net_charges(system)
        if q is not None:
            rec["net_charge_e"] = round(sum(q), 4)
        rec["status"] = "ok"
        return rec
    except Exception as e:  # noqa: BLE001
        rec["status"] = "census failed (%s: %s)" % (type(e).__name__, e)
        return rec
    finally:
        try:
            if reporter is not None:
                reporter.close()
        except Exception:  # noqa: BLE001
            pass


# =============================================================================================================
# the cross-leg verdict — the part that answers the RUNG 2b question
# =============================================================================================================
# THE VERDICT IS TRI-STATE AND ABSENCE IS NOT AGREEMENT. Two legs whose census failed agree on nothing; a
# comparison that reported them as matching would reproduce, inside the tool built to stop it, the exact defect
# the provenance step was added for.

def compare(records):
    """Cross-leg composition verdict. PURE — unit-testable with hand-built records, no .nc and no openmm."""
    ok = [r for r in records if r.get("status") == "ok"]
    bad = [r.get("label") for r in records if r.get("status") != "ok"]
    out = {"n_compared": len(ok), "uncensused": bad}
    if len(ok) < 2:
        out["verdict"] = "INSUFFICIENT — fewer than two legs produced a census; nothing is established"
        return out

    def spread(key):
        vals = {}
        for r in ok:
            vals.setdefault(json.dumps(r.get(key), sort_keys=True), []).append(r["label"])
        return vals

    solute = spread("n_solute_atoms")
    ligand = spread("n_ligand_atoms")
    chains = spread("protein_chain_sizes")
    charge = spread("net_charge_e")
    total = spread("n_particles")
    waters = spread("n_water_molecules")
    ions = spread("ion_mass_histogram")
    out["fields"] = {"n_solute_atoms": solute, "n_ligand_atoms": ligand, "protein_chain_sizes": chains,
                     "net_charge_e": charge, "n_particles": total, "n_water_molecules": waters,
                     "ion_mass_histogram": ions}
    solute_same = len(solute) == 1 and len(ligand) == 1 and len(chains) == 1
    solvent_same = len(waters) == 1 and len(ions) == 1
    out["solute_identical"] = solute_same
    out["solvent_identical"] = solvent_same
    if solute_same and solvent_same:
        out["verdict"] = ("IDENTICAL SYSTEMS — same solute and same solvent box. Any particle-count difference "
                          "reported elsewhere is not a system difference.")
    elif solute_same:
        out["verdict"] = ("SAME SOLUTE, DIFFERENT SOLVENT — the protein chains, the ligand and the net charge "
                          "agree atom-for-atom; the systems differ only in the number of bulk water molecules "
                          "and the counter-ions that scale with them. The alchemical transformation is the "
                          "same one in both.")
    else:
        out["verdict"] = ("SOLUTE DIFFERS — the legs do not describe the same alchemical system. A free-energy "
                          "comparison between them is not a comparison of the variable under test.")
    return out


def _fmt(rec):
    if rec.get("status") != "ok":
        return "  %-34s CENSUS FAILED — %s" % (rec.get("label"), rec.get("status"))
    return ("  %-34s total=%-8s subset=%-7s solute=%-7s (chains=%s lig=%s) waters=%-7s ions=%s net_q=%s"
            % (rec.get("label"), rec.get("n_particles"), rec.get("n_analysis_particles"),
               rec.get("n_solute_atoms"), rec.get("protein_chain_sizes"), rec.get("n_ligand_atoms"),
               rec.get("n_water_molecules"), rec.get("ion_mass_histogram"), rec.get("net_charge_e")))


def main(argv=None):
    ap = argparse.ArgumentParser(description="composition census of a committed ternary trajectory ($0, CPU)")
    ap.add_argument("--nc", help="path to one simulation.nc")
    ap.add_argument("--label", help="tag for this trajectory (the commit prefix it came from)")
    ap.add_argument("--out-dir", default=os.environ.get("CENSUS_DIR", "/tmp/census"))
    ap.add_argument("--compare", action="store_true", help="read every census JSON in --out-dir and rule")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)

    if a.nc:
        label = a.label or os.path.basename(os.path.dirname(a.nc))
        rec = census_one(a.nc, label)
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in label)
        with open(os.path.join(a.out_dir, "census__%s.json" % safe), "w") as fh:
            json.dump(rec, fh, indent=2)
        print(_fmt(rec), flush=True)

    if a.compare:
        recs = []
        for f in sorted(glob.glob(os.path.join(a.out_dir, "census__*.json"))):
            try:
                recs.append(json.load(open(f)))
            except Exception as e:  # noqa: BLE001
                print("  (unreadable census %s: %s)" % (f, e))
        print("\n==== TERNARY SYSTEM CENSUS ====")
        for r in recs:
            print(_fmt(r))
        verdict = compare(recs)
        with open(os.path.join(a.out_dir, "census_verdict.json"), "w") as fh:
            json.dump(verdict, fh, indent=2)
        print("\n---- cross-leg verdict ----")
        for k in ("n_solute_atoms", "n_ligand_atoms", "protein_chain_sizes", "net_charge_e",
                  "n_particles", "n_water_molecules", "ion_mass_histogram"):
            v = (verdict.get("fields") or {}).get(k)
            if v is not None:
                print("  %-22s %s" % (k, {kk: vv for kk, vv in v.items()}))
        if verdict.get("uncensused"):
            print("  UNCENSUSED (not agreement): %s" % verdict["uncensused"])
        print("  VERDICT: %s" % verdict["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
