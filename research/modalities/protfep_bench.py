#!/usr/bin/env python3
"""Known-answer PROTEIN-mutation benchmark systems for the 5a-KS wedge engine.

WHY THIS FILE EXISTS
--------------------
`nr4a3_protein_fep.py` implements the 5a-KS wedge (an alchemical protein point mutation run in two
environments and subtracted). nr4a3-program-map.md marks that rung **UNPRICED and UNVALIDATED**: the engine
exists, but no leg has ever run, and an engine that exists is not a rate. The gate the engine must
clear before any number it produces may enter the manuscript is a **known-answer protein-mutation
benchmark** — a published, experimentally measured protein-protein interface ddG that the engine
must recover within ~1.5 kcal/mol AND rank in the right order.

This module is that benchmark's *system* layer: which structures, which chains, which mutations,
what the measured answer is, and how the two legs of the cycle are staged from the PDB. The engine
itself stays system-agnostic.

THE CYCLE, FOR A PROTEIN-PROTEIN INTERFACE MUTATION
---------------------------------------------------
    ddG_bind = dG_bind(mutant) - dG_bind(WT) = dG_mut(complex) - dG_mut(free partner)

i.e. alchemically mutate the SAME residue twice — once in the bound two-chain complex, once in the
isolated partner chain — and subtract. Positive ddG_bind = the mutation weakens binding = the WT
residue was contributing to the interface. That is *identically* the shape of the 5a-KS wedge
(`dG_mut^ternary - dG_mut^binary`), which is the whole point: the benchmark exercises the same
arithmetic, the same guards, and the same sampling path the science will use, so a pass is
informative about the wedge and not about a parallel code path.

Leg naming maps onto the engine's two cycle roles:
    complex leg  <-> the "ternary"/bound role   (barnase + barstar)
    apo leg      <-> the "binary"/free role     (barstar alone)

NOTE ON PERSES VOCABULARY, because it collides with ours: perses' `get_apo_htf()` means "no
SMALL-MOLECULE ligand", not "unbound partner". BOTH of our legs are apo in perses' sense (there is
no small molecule anywhere in these benchmarks) — the difference between them is how many protein
chains we hand it. So both legs call `get_apo_htf()`, and the leg distinction lives entirely in
which PDB we stage.

WHY THESE SYSTEMS
-----------------
Every benchmark mutation here is **charge-conserving**, deliberately: a charge-changing mutation
under PME carries a system-size-dependent finite-size artifact that does NOT cancel between two
differently-sized boxes (see `nr4a3_protein_fep`'s blocker 2). Qualifying the engine on a
charge-changing mutation would confound engine error with that artifact, and we would not know
which one we had measured.

HONESTY ON THE REFERENCE VALUES
-------------------------------
Each reference ddG carries `verified: False` until its primary source has been read full-text
through a CI runner (the repo's egress-proxy rule — the dev sandbox cannot reach the publishers).
The pass/fail criterion is computed AGAINST these numbers, so an unverified reference means an
unverified verdict; `verify_status()` says so out loud rather than letting a green PASS imply more
than it should.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RCSB_PDB = "https://files.rcsb.org/download/{pdb}.pdb"

# ------------------------------------------------------------------------------------------------
# The benchmark set
# ------------------------------------------------------------------------------------------------
# `partner_chain` is the chain the mutation sits on and the chain the apo leg keeps ALONE.
# `receptor_chains` are the other chain(s) present only in the complex leg.
BENCHMARKS = {
    "barnase_barstar_Y29A": {
        "system": "barnase-barstar",
        "pdb": "1BRS",
        "partner_chain": "D",          # barstar
        "receptor_chains": ["A"],      # barnase
        "mutation": "D:Y29A",
        "ref_ddg_bind_kcal": 3.4,
        "ref_source": ("SKEMPI 2.0 record for 1BRS_A_D YD29A (Kd_mut 3.5E-12 M / Kd_wt 1E-14 M at 298 K "
                       "-> 3.47 kcal/mol), cited to PMID 7739054 = Schreiber & Fersht, J Mol Biol "
                       "248:478-486 (1995), 'Energetics of protein-protein interactions: analysis of the "
                       "barnase-barstar interface by single mutations and double mutant cycles'"),
        # VERIFIED 2026-07-24: protfep_refcheck recomputed 3.469 from SKEMPI's deposited affinities,
        # 0.07 kcal/mol from the stored 3.4.
        "ref_verified": True,
        "why": ("The canonical, most-measured PPI hot spot in the literature. Charge-conserving, and a "
                "large experimental effect — an engine that cannot see this cannot see our wedge either."),
    },
    "barnase_barstar_Y29F": {
        "system": "barnase-barstar",
        "pdb": "1BRS",
        "partner_chain": "D",
        "receptor_chains": ["A"],
        "mutation": "D:Y29F",
        # CORRECTED 2026-07-24 from +0.5 (entered from memory of the paper's table) to -0.13,
        # RECOMPUTED by protfep_refcheck from SKEMPI 2.0's deposited affinities for 1BRS_A_D YD29F
        # (Kd_mut 8E-15 vs Kd_wt 1E-14 at 298 K, record cited to PMID 7739054 = Schreiber & Fersht
        # 1995). The stored value had the WRONG SIGN: Y29F very slightly STRENGTHENS binding, it does
        # not weaken it. The old value survived the +/-0.75 agreement window purely because the
        # discrepancy was 0.63 — which is exactly why the checker now fails on a sign disagreement
        # regardless of magnitude.
        "ref_ddg_bind_kcal": -0.13,
        "ref_source": ("SKEMPI 2.0 record for 1BRS_A_D YD29F (Kd_mut 8E-15 M / Kd_wt 1E-14 M at 298 K), "
                       "cited to PMID 7739054 = Schreiber & Fersht, J Mol Biol 248:478-486 (1995)"),
        "ref_verified": True,
        "why": ("Conservative OH->H swap at the SAME site, and a near-NULL reference (~0 kcal/mol). It pairs "
                "with Y29A as a graded control in two ways: a working engine must rank Y29A as much the "
                "larger effect (ORDERING — a magnitude pass with the ordering wrong is a fail, because a "
                "wedge is read as a ranking), and it must NOT invent a large effect where the experiment "
                "sees none. Note the honest limitation: because the reference sits near zero, the +/-1.5 "
                "tolerance is weak here, so the ordering test carries most of this benchmark's weight."),
    },
    "barnase_barstar_W35F": {
        "system": "barnase-barstar",
        "pdb": "1BRS",
        "partner_chain": "A",          # barnase carries this one
        "receptor_chains": ["D"],      # barstar
        "mutation": "A:W35F",
        "ref_ddg_bind_kcal": 1.26,
        "ref_source": ("SKEMPI 2.0, two records for 1BRS_A_D WA35F, both recomputed from the deposited "
                       "Kd pairs at 298 K by protfep_refcheck --wedge-scan -> "
                       "protfep-wedge-band-candidates.json: 1.4E-13/1.3E-14 -> +1.407 and "
                       "8.5E-13/1.3E-13 -> +1.112, median +1.26, spread 0.295 kcal/mol. Both records "
                       "cite PMID 8494892 (Schreiber & Fersht, Biochemistry 1993) — so the spread is "
                       "WITHIN one paper's two wild-type baselines, not agreement between two "
                       "independent laboratories, and must not be quoted as the latter."),
        "ref_verified": True,
        # ⛔ NOT IN THE QUALIFICATION SET UNTIL IT HAS RUN. Adding a benchmark to `BENCHMARKS` also
        # adds it to `complete`, which would flip the engine's COMMITTED, CITED verdict from qualified
        # to "incomplete — 2/3 scored" without a single new measurement. That would be a stale artifact
        # reading as a current fail, which is the exact harm CLAUDE.md §7 names. Promotion is a
        # deliberate edit, made once this has actually landed.
        "in_qualification_set": False,
        "why": ("★ THE HONEST VALIDATION THAT WAS MISSING, and the only candidate the whole of SKEMPI "
                "offers for it. The qualified set BRACKETS the wedge without covering it: a +3.4 "
                "hot-spot knockout and a ~0 near-null, with NOTHING at the size a paralogue-scale "
                "difference actually has. Between-replicate SD is 6.2x different at those two ends "
                "(±1.077 vs ±0.175) while within-leg MBAR SEs are 0.05–0.13, so the scatter is "
                "setup/equilibration variance and cannot be extrapolated across the gap — which is "
                "why pricing.md records that the confirmatory line 'may not claim to resolve a "
                "paralogue-scale difference'. W35F sits at **+1.26 kcal/mol**: inside the 0.5–1.5 "
                "wedge band, charge-conserving, buildable, on the 1BRS complex whose staging is "
                "already proven, and with a reference resolved to 0.295 kcal/mol — tighter than the "
                "band is wide, so scoring against it is not scoring against noise. It was found by "
                "`protfep_refcheck --wedge-scan`, which rejected 29 other mutations of the same "
                "complex and returned this one. ⚠ What it would and would NOT settle: it measures "
                "whether THIS ENGINE resolves a ~1 kcal/mol interface effect. It is not a selectivity "
                "control, it involves no paralogue, and passing it would license no claim about "
                "SMARCA2/4 or NR4A3."),
    },
}

# The engine is qualified only on the whole set, not on a lucky single point.
PASS_ABS_ERR_KCAL = 1.5

#: The benchmarks whose completion the qualification verdict requires. A benchmark may be defined,
#: stageable and launchable without yet being part of the bar the engine is graded against — see
#: `in_qualification_set` on W35F for why that separation exists.
QUALIFICATION_SET = [k for k, v in BENCHMARKS.items() if v.get("in_qualification_set", True)]
ORDERING_PAIRS = [("barnase_barstar_Y29A", "barnase_barstar_Y29F")]  # (larger, smaller) by experiment

# Pilot-one-leg-first: this is the single most decision-relevant benchmark. If the engine cannot
# recover the canonical 3.4 kcal/mol barstar hot spot, the wedge is not deliverable and the rest of
# the set is not worth renting a GPU for.
PILOT_BENCHMARK = "barnase_barstar_Y29A"


def benchmark(name):
    """Look up one benchmark definition. Pure."""
    try:
        return dict(BENCHMARKS[name])
    except KeyError:
        raise KeyError(f"unknown benchmark {name!r}; known: {sorted(BENCHMARKS)}") from None


def leg_ids(name):
    """The two cycle legs for one benchmark: (complex_leg_id, apo_leg_id). Pure."""
    return f"{name}__complex", f"{name}__apo"


def leg_spec(name, environment, replicate=0):
    """Fully resolved spec for ONE leg — what the GPU host needs to stage and run. Pure.

    `environment` is 'complex' (bound, both chains) or 'apo' (the mutated partner alone).
    """
    if environment not in ("complex", "apo"):
        raise ValueError(f"environment must be 'complex' or 'apo', got {environment!r}")
    b = benchmark(name)
    chains = ([*b["receptor_chains"], b["partner_chain"]] if environment == "complex"
              else [b["partner_chain"]])
    return {
        "benchmark": name,
        "leg_id": f"{name}__{environment}_r{int(replicate)}",
        "environment": environment,
        "cycle_role": "ternary" if environment == "complex" else "binary",
        "pdb": b["pdb"],
        "chains": chains,
        "mutation": b["mutation"],
        "replicate": int(replicate),
    }


def all_leg_specs(names=None, n_replicas=3):
    """Every leg needed to complete the benchmark set. Pure."""
    out = []
    for name in (names or list(QUALIFICATION_SET)):
        for env in ("complex", "apo"):
            for r in range(n_replicas):
                out.append(leg_spec(name, env, r))
    return out


# ------------------------------------------------------------------------------------------------
# Verdict
# ------------------------------------------------------------------------------------------------
def score_benchmark(name, calc_ddg_kcal, calc_sd_kcal=None):
    """Compare one computed ddG_bind against its measured value. Pure.

    Reports the absolute error against the published number and whether it clears the qualification
    tolerance. `ref_verified` is carried through so a caller cannot read a PASS without also seeing
    whether the number it was scored against has been checked at primary source.
    """
    b = benchmark(name)
    ref = float(b["ref_ddg_bind_kcal"])
    calc = float(calc_ddg_kcal)
    err = abs(calc - ref)
    return {
        "benchmark": name,
        "system": b["system"],
        "mutation": b["mutation"],
        "ref_ddg_bind_kcal": ref,
        "ref_source": b["ref_source"],
        "ref_verified": b["ref_verified"],
        "calc_ddg_bind_kcal": calc,
        "calc_sd_kcal": (float(calc_sd_kcal) if calc_sd_kcal is not None else None),
        "abs_err_kcal": err,
        "tolerance_kcal": PASS_ABS_ERR_KCAL,
        "within_tolerance": err <= PASS_ABS_ERR_KCAL,
    }


def qualify(results):
    """Turn per-benchmark scores into the engine's qualification verdict. Pure.

    `results` maps benchmark name -> the dict returned by score_benchmark. The engine qualifies only
    if EVERY scored benchmark is within tolerance AND every ordering pair whose members are both
    present comes out in the measured order. A magnitude pass with a broken ordering is a FAIL: the
    wedge's job is to RANK a mutation's interface contribution, so ordering is the load-bearing
    property, not the absolute value.
    """
    scored = {k: v for k, v in results.items() if v is not None}
    if not scored:
        return {"qualified": False, "reason": "no benchmark results supplied", "n_scored": 0}
    failures = [k for k, v in scored.items() if not v["within_tolerance"]]
    ordering = []
    for larger, smaller in ORDERING_PAIRS:
        if larger in scored and smaller in scored:
            ok = scored[larger]["calc_ddg_bind_kcal"] > scored[smaller]["calc_ddg_bind_kcal"]
            ordering.append({"larger": larger, "smaller": smaller, "ordering_correct": ok})
    ordering_broken = [o for o in ordering if not o["ordering_correct"]]
    complete = set(scored) >= set(QUALIFICATION_SET)
    unverified = sorted(k for k, v in scored.items() if not v.get("ref_verified"))
    qualified = (not failures) and (not ordering_broken) and complete
    if qualified:
        reason = (f"all {len(scored)} benchmarks within {PASS_ABS_ERR_KCAL} kcal/mol and ordering correct")
    elif failures:
        reason = f"outside tolerance: {', '.join(sorted(failures))}"
    elif ordering_broken:
        reason = ("magnitudes within tolerance but ORDERING WRONG: "
                  + ", ".join(f"{o['larger']} !> {o['smaller']}" for o in ordering_broken))
    else:
        reason = (f"incomplete — {len(scored)}/{len(QUALIFICATION_SET)} benchmarks scored; a partial set cannot "
                  f"qualify the engine")
    return {
        "qualified": qualified,
        "reason": reason,
        "n_scored": len(scored),
        "n_required": len(QUALIFICATION_SET),
        "complete": complete,
        "failures": sorted(failures),
        "ordering": ordering,
        "unverified_references": unverified,
        "caveat": (("VERDICT IS PROVISIONAL — the reference ddG values for "
                    + ", ".join(unverified)
                    + " have not been checked against primary source full text yet, so a PASS is scored "
                      "against unverified numbers.") if unverified else None),
        "gate": ("5a-KS may not contribute a number to the manuscript, and the rung may not be priced from a "
                 "leg rate alone, until this qualifies."),
    }


def verify_status():
    """Which reference values still need a primary-source read. Pure."""
    return {k: {"mutation": v["mutation"], "ref_ddg_bind_kcal": v["ref_ddg_bind_kcal"],
                "source": v["ref_source"], "verified": v["ref_verified"]}
            for k, v in BENCHMARKS.items()}


# ------------------------------------------------------------------------------------------------
# Structure staging (network + optional PDBFixer; runs on the GPU host or a CI runner)
# ------------------------------------------------------------------------------------------------
def fetch_pdb(pdb_id, dest_dir):
    """Download a PDB from RCSB. Returns the local path.

    Deliberately the raw RCSB file: every atom in the benchmark comes from the deposited structure,
    nothing is modelled in. The dev sandbox's egress proxy blocks this host, which is exactly why
    staging runs on the GPU host / a CI runner, never here.
    """
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, f"{pdb_id.upper()}.pdb")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    url = RCSB_PDB.format(pdb=pdb_id.upper())
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-protfep"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    with open(path, "wb") as fh:
        fh.write(raw)
    return path


def select_chains(pdb_path, chains, out_path):
    """Write a PDB containing only `chains`, protein atoms only (no waters, no heteroatoms).

    Pure text surgery on ATOM records — no structure library needed, so this is testable on CPU and
    cannot silently rebuild anything. Returns a small report (atom/residue counts per chain) that
    gets stamped into the leg JSON as provenance.
    """
    keep = set(chains)
    counts = {c: 0 for c in keep}
    residues = {c: set() for c in keep}
    lines = []
    with open(pdb_path) as fh:
        for line in fh:
            rec = line[:6]
            if rec == "ATOM  ":
                ch = line[21]
                if ch in keep:
                    lines.append(line)
                    counts[ch] += 1
                    residues[ch].add(line[22:27].strip())
            elif rec == "TER   " and len(line) > 21 and line[21] in keep:
                lines.append(line)
    if not lines:
        raise ValueError(f"no ATOM records for chains {sorted(keep)} in {pdb_path}")
    missing = [c for c in keep if counts[c] == 0]
    if missing:
        raise ValueError(f"chains {missing} absent from {pdb_path}")
    with open(out_path, "w") as fh:
        fh.writelines(lines)
        fh.write("END\n")
    return {"out": out_path, "chains": sorted(keep),
            "atoms_per_chain": counts,
            "residues_per_chain": {c: len(residues[c]) for c in sorted(keep)}}


def observed_residue(pdb_path, chain, resid):
    """The 3-letter residue name actually present at chain:resid in the file, or None. Pure.

    Used to CHECK the mutation site rather than assume it: a benchmark that silently mutated the
    wrong residue would produce a confident wrong number, which is the failure mode this whole gate
    exists to catch. It also records the crystal's real identity at other positions (e.g. whether a
    deposited 'wild-type' is actually an engineered pseudo-WT background), so provenance is observed,
    not asserted.
    """
    with open(pdb_path) as fh:
        for line in fh:
            if line[:6] == "ATOM  " and line[21] == chain and line[22:27].strip() == str(resid):
                return line[17:20].strip().upper()
    return None


def stage_leg(spec, work_dir, structure_dir=None):
    """Stage ONE leg: fetch the PDB, cut the chains, verify the mutation site, PDBFixer-prep.

    Returns a dict with the prepared PDB path plus the provenance report. PDBFixer is imported
    lazily and skipped (with the reason recorded) if unavailable, so the chain surgery + site check
    are exercisable on a CPU runner with no MD stack — the cheap parts of staging get tested for
    free before a GPU is rented.
    """
    os.makedirs(work_dir, exist_ok=True)
    structure_dir = structure_dir or os.path.join(work_dir, "_pdb")
    raw = fetch_pdb(spec["pdb"], structure_dir)
    sel = os.path.join(work_dir, f"{spec['leg_id']}_chains.pdb")
    report = select_chains(raw, spec["chains"], sel)

    # Verify the mutation site is the residue the benchmark claims it is.
    import nr4a3_protein_fep as pf
    m = pf.classify_mutation(spec["mutation"])
    seen = observed_residue(sel, m["chain"], m["resid"])
    if seen != m["wt"]:
        raise ValueError(
            f"mutation-site mismatch: {spec['mutation']} expects {m['wt']} at chain {m['chain']} "
            f"residue {m['resid']}, but {spec['pdb']} has {seen!r}. Refusing to stage — mutating the "
            f"wrong residue would produce a confident wrong benchmark number.")
    report["mutation_site_observed"] = seen
    report["mutation_site_expected"] = m["wt"]

    prepared = os.path.join(work_dir, f"{spec['leg_id']}.pdb")
    try:
        from openmm.app import PDBFile
        from pdbfixer import PDBFixer
    except ImportError as e:  # CPU/CI context — the surgery above is still verified
        report["prepared"] = None
        report["pdbfixer_skipped"] = f"{type(e).__name__}: {e}"
        return {"leg": spec, "structure": sel, "report": report}

    fixer = PDBFixer(filename=sel)
    fixer.findMissingResidues()
    # Do NOT model in missing terminal/loop residues we have no coordinates for — a rebuilt loop is a
    # modelling assumption, and this is supposed to be the leg where nothing is assumed. Only missing
    # ATOMS within resolved residues are completed.
    fixer.missingResidues = {}
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    with open(prepared, "w") as fh:
        PDBFile.writeFile(fixer.topology, fixer.positions, fh, keepIds=True)
    report["prepared"] = prepared
    report["pdbfixer"] = {"ph": 7.0, "missing_residues_modelled": False,
                          "heterogens_removed": True, "water_removed": True}
    # Re-check the site survived preparation with its identity and chain id intact.
    after = observed_residue(prepared, m["chain"], m["resid"])
    if after != m["wt"]:
        raise ValueError(f"after PDBFixer prep, chain {m['chain']} residue {m['resid']} reads {after!r}, "
                         f"not {m['wt']} — chain ids or numbering did not survive preparation")
    return {"leg": spec, "structure": prepared, "report": report}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="5a-KS known-answer benchmark systems (list / stage / score)")
    ap.add_argument("--list", action="store_true", help="print the benchmark set")
    ap.add_argument("--legs", action="store_true", help="print every leg spec")
    ap.add_argument("--n-replicas", type=int, default=3)
    ap.add_argument("--stage", metavar="LEG_SPEC_JSON", help="stage one leg (JSON from --legs)")
    ap.add_argument("--stage-benchmark", metavar="NAME", help="stage both legs of one benchmark")
    ap.add_argument("--work-dir", default=os.environ.get("INPUT_DIR", "/tmp/protfep_in"))
    ap.add_argument("--verify-status", action="store_true", help="which reference ddG values are unverified")
    args = ap.parse_args(argv)

    if args.list:
        print(json.dumps(BENCHMARKS, indent=2))
    elif args.verify_status:
        print(json.dumps(verify_status(), indent=2))
    elif args.legs:
        print(json.dumps(all_leg_specs(n_replicas=args.n_replicas), indent=2))
    elif args.stage:
        print(json.dumps(stage_leg(json.loads(args.stage), args.work_dir), indent=2))
    elif args.stage_benchmark:
        out = [stage_leg(leg_spec(args.stage_benchmark, env), args.work_dir) for env in ("complex", "apo")]
        print(json.dumps(out, indent=2))
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
