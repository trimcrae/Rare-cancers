#!/usr/bin/env python3
"""IS THE PRE-MD `setup()` NaN A PROPERTY OF THE EDGE, OR OF THE HOST? — decided on a free CPU runner. $0.

★ WHY THIS EXISTS (2026-07-27). Step 1 fan-out unit
`e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral` (label `s1f-08`) lost its complex leg at
**1:41 PM ET** with, verbatim from its S3 `complex.log`:

    File ".../_rfe_utils/multistate.py", line 345, in minimize
        openmm.LocalEnergyMinimizer.minimize(
    openmm.OpenMMException: Particle coordinate is NaN.

That is inside `unit._get_sampler(...)` -> `sampler.setup()` — the small minimisation `setup()` runs
BEFORE any MD. The edge is measurably NOT a mapping limit (`step1-map-diag.json`: production maps 17
against a provable floor of 12, the matrix is identical at both LOMAP budgets, kartograf 18), so
unlike `cw_bio_nmethyl_amide` it is not a block-by-mapper case, and the two available answers are
expensive in opposite directions:

  BLOCK   if the NaN is deterministic for this staged system — otherwise the lane rents a fresh host
          for it on every tick, forever, and never gets a ddG.
  RETRY   if it was incidental to one machine — a block would retire a viable edge on a wrong
          diagnosis, which is exactly the mistake avoided earlier the same day when this edge was
          nearly blocked as a mapper limit.

★ AND WHY IT IS NOT DECIDED BY RENTING ANOTHER HOST. That was tried. The relaunch onto machine 19499
(instance 46031270) sat `loading` / `cur_state: stopped` for over half an hour without running the
container — a reading about that MACHINE and not about this edge, the same never-starts pattern
machine 1569 produced earlier and the reason 1569 is in the shared exclusion set. Counting failures
across hosts cannot separate the two mechanisms while the hosts themselves keep failing. A per-force
single-point energy can, because it needs no host at all.

★ THE ONE OBSERVATION THAT DISCRIMINATES. `nr4a3_rbfe.execute_hybrid_dag_spot_safe` builds the
solvated hybrid `system` and its `positions` on CPU and, under `RBFE_HMRDIAG_ONLY=1`, exits before
touching a GPU. That pair is the pair handed to the `setup()` that NaN'd. So:

  * ANY force term non-finite at those coordinates, before a single minimisation step -> the fault is
    in the system as built. Every host reproduces it. BLOCK.
  * every term finite and sane -> the blow-up happened inside the minimisation trajectory, which is
    integrator/platform state rather than the staged system. RETRY.

The wording of the verdict is `rbfe_spot_driver.energy_probe_verdict` — the same function the GPU
leg's own failure path calls — so the CPU reproduction and the rented leg cannot produce two
different sentences for the same evidence (CLAUDE.md rule 1: one fact, one home).

RENTS NOTHING, DESTROYS NOTHING, WRITES NOTHING TO S3. Reads the staged tree and writes
`step1-setup-energy-probe.json` next to this file for CI to commit back.

Usage (inside the parity image — needs openfe + openmm):
    PROBE_UNITS=cw_bio_primary_amide python step1_setup_energy_probe.py
"""
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "step1-setup-energy-probe.json")

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
STAGE_PREFIX = os.environ.get("STAGE_PREFIX", "nr4a3-step1-fanout/stage")
# The leg that failed was the COMPLEX leg; probing the solvent leg builds a different system and
# answers a different question. Overridable only so the same harness can check the other leg on demand.
LEG = os.environ.get("PROBE_LEG", "complex")


def probe_unit(unit, in_dir):
    """Build ONE unit's hybrid system on CPU and return its energy-probe row.

    Every field is a MEASUREMENT or an explicit error string. A cell that could not be computed says
    so rather than being dropped — an absent reading rendered as a benign one is the failure mode
    this repo keeps paying for."""
    import importlib
    import tempfile
    import openfe
    from rdkit import Chem
    import congeneric_fanout as cf

    row = {"unit_id": unit["unit_id"], "edge_id": unit["edge_id"], "leg": LEG,
           "edge": f"{unit['ligand_a']}->{unit['ligand_b']}"}

    # The env a rented host sets for this leg, taken from the launcher's own function so the
    # diagnostic cannot drift from production.
    env = cf.unit_env(unit, LEG, int(os.environ.get("N_WINDOWS", "12")))
    for k, v in env.items():
        os.environ[k] = str(v)
    os.environ["INPUT_DIR"] = in_dir
    # No GPU on this runner, and no MD wanted: build the system, probe it, exit.
    os.environ["OPENMM_REQUIRE_CUDA"] = "0"
    os.environ["RBFE_PLATFORM"] = os.environ.get("RBFE_PLATFORM", "CPU")
    os.environ["RBFE_HMRDIAG_ONLY"] = "1"
    os.environ["RBFE_ENERGY_PROBE"] = "1"
    # Never let an inherited cache/commit URI make a $0 diagnostic write to a production prefix.
    for k in ("RBFE_SETUP_CACHE_GCS", "RBFE_SETUP_CACHE_S3", "RBFE_SPOT_COMMIT_GCS",
              "RBFE_SPOT_COMMIT_S3", "RBFE_PRIME_ONLY"):
        os.environ.pop(k, None)

    # nr4a3_rbfe reads LIGAND_A/LIGAND_B/RECEPTOR/LEG/IN into MODULE GLOBALS at import time, so the
    # reload is not cosmetic — without it every unit after the first is built with the first's ligands.
    import nr4a3_rbfe as rbfe
    rbfe = importlib.reload(rbfe)

    t0 = time.time()
    try:
        ligA, ligB, prot = rbfe._build_components(openfe, Chem)
        mapping = rbfe._mapping(openfe, ligA, ligB)
        row["n_mapped_atoms"] = len(mapping.componentA_to_componentB)
        A, B = rbfe._chemical_systems(openfe, ligA, ligB, prot)
        proto = rbfe._protocol(openfe)
        dag = proto.create(stateA=A, stateB=B, mapping=mapping)
        ckpt = tempfile.mkdtemp(prefix="s1f_eprobe_")
        _, _, info = rbfe.execute_hybrid_dag_spot_safe(
            proto, dag, ckpt, tag="eprobe_%s" % unit["unit_id"])
    except SystemExit as e:                    # an ABORT is a legitimate outcome, not a crash
        row["build_error"] = f"SystemExit: {e}"
        row["wall_s"] = round(time.time() - t0, 1)
        return row
    except Exception as e:                     # noqa: BLE001
        row["build_error"] = f"{type(e).__name__}: {e}"
        row["traceback"] = traceback.format_exc()[-2000:]
        row["wall_s"] = round(time.time() - t0, 1)
        return row
    row["wall_s"] = round(time.time() - t0, 1)
    info = dict(info or {})
    row["n_particles"] = info.get("n_particles")
    row["force_census"] = info.get("force_census")
    row["energy_probe"] = info.get("energy_probe")

    # ---- STAGE 2: RUN THE REAL MINIMISER --------------------------------------------------------
    # ★★ WHY STAGE 1 IS NOT ENOUGH, STATED PLAINLY. The energy probe evaluates ONE point: the
    # coordinates as handed over, with the alchemical global parameters as built. `sampler.setup()`
    # minimises EVERY thermodynamic state of the lambda schedule, setting that state's parameters on
    # the context first. A softcore term that is finite at the built lambda and divergent at an
    # intermediate one is therefore invisible to stage 1 — so all-finite energies rule OUT "the
    # system is broken as built" and leave "the minimiser deterministically diverges" open. Only
    # running the real `_get_sampler` -> `setup()` closes that, and it is the same $0 CPU build.
    if os.environ.get("PROBE_MINIMIZE", "1") == "1":
        row["minimize_repro"] = _minimize_repro(rbfe, openfe, Chem, unit)
    return row


def _minimize_repro(rbfe, openfe, Chem, unit):
    """Re-run the production `_get_sampler` -> `sampler.setup()` on CPU and report what it did.

    Returns {"outcome": completed|nan|error, ...}. `completed` means the pre-MD minimiser ran over
    every lambda state without a NaN on a host-independent build — the strongest available evidence
    that the failing leg's NaN was not a property of the edge. `nan` means it reproduced, which is a
    scientific finding about the edge and a block."""
    import importlib
    import tempfile
    out = {}
    os.environ.pop("RBFE_HMRDIAG_ONLY", None)
    os.environ.pop("RBFE_ENERGY_PROBE", None)
    os.environ["RBFE_SETUP_ONLY"] = "1"          # stop the instant setup() returns; no MD, no commits
    os.environ["RBFE_SPOT_SAFE"] = "1"
    rbfe = importlib.reload(rbfe)
    t0 = time.time()
    try:
        ligA, ligB, prot = rbfe._build_components(openfe, Chem)
        mapping = rbfe._mapping(openfe, ligA, ligB)
        A, B = rbfe._chemical_systems(openfe, ligA, ligB, prot)
        proto = rbfe._protocol(openfe)
        dag = proto.create(stateA=A, stateB=B, mapping=mapping)
        rbfe.execute_hybrid_dag_spot_safe(proto, dag, tempfile.mkdtemp(prefix="s1f_minrepro_"),
                                          tag="minrepro_%s" % unit["unit_id"])
        out["outcome"] = "completed_without_the_sentinel"
        out["note"] = ("setup() returned but RBFE_SETUP_ONLY did not stop the run — the guard did not "
                       "fire, so treat this as unverified rather than as a clean pass")
    except SystemExit as e:
        s = str(e)
        out["outcome"] = "completed" if "COMPLETED WITHOUT A NaN" in s else "aborted"
        out["detail"] = s[:400]
    except Exception as e:                       # noqa: BLE001
        s = f"{type(e).__name__}: {e}"
        out["outcome"] = "nan" if "NaN" in s else "error"
        out["detail"] = s[:400]
        out["traceback"] = traceback.format_exc()[-2000:]
    out["wall_s"] = round(time.time() - t0, 1)
    return out


def verdict(row):
    """(decision, why) in {BLOCK, RETRY, INCONCLUSIVE}. PURE — the rule that decides whether this
    lane keeps buying hosts for an edge is testable, not eyeballed in a CI log.

    INCONCLUSIVE is a first-class answer and must never collapse into RETRY: 'the probe did not run'
    and 'the probe ran and the system is fine' are different states, and only the second is a licence
    to rent another host."""
    if row.get("build_error"):
        return "INCONCLUSIVE", (f"the system could not be built here, so nothing was measured about "
                                f"the minimiser: {row['build_error']}")
    ep = row.get("energy_probe") or {}
    if ep.get("error"):
        return "INCONCLUSIVE", f"the energy probe itself failed: {ep['error']}"
    rows = ep.get("rows") or []
    if not rows:
        return "INCONCLUSIVE", ("the probe evaluated no force groups — it measured nothing, which is "
                                "not the same as measuring that nothing is wrong")
    bad = [r["force"] for r in rows if not r.get("finite", True)]
    if bad:
        return "BLOCK", (f"{len(bad)} force term(s) are NON-FINITE at the coordinates handed to "
                         f"setup(), before a single minimisation step — {bad}. That is a property of "
                         f"the staged system and reproduces on every host, so renting another one "
                         f"buys nothing")
    hi = max(abs(r["energy_kj_mol"]) for r in rows)
    # Stage 2 is what actually closes the question — a single-point reading cannot see a lambda
    # window it never visited. Its absence downgrades the answer rather than being ignored.
    mr = row.get("minimize_repro") or {}
    oc = mr.get("outcome")
    if oc == "nan":
        return "BLOCK", (f"the production `sampler.setup()` — the same call that failed on the rented "
                         f"host — NaN'd again on a host-independent CPU build of the same staged "
                         f"system: {mr.get('detail')}. Deterministic for this edge; another host "
                         f"reproduces it")
    if oc == "completed":
        return "RETRY", (f"the production `sampler.setup()`, including its pre-MD LocalEnergyMinimizer "
                         f"over every lambda state, COMPLETED WITHOUT A NaN on a host-independent CPU "
                         f"build of the same staged system ({mr.get('wall_s')}s), and every force term "
                         f"is finite at the handed-over coordinates (max |E| = {hi:.6g} kJ/mol). The "
                         f"edge is not the fault, so this is a retry candidate and not a block")
    return "INCONCLUSIVE", (f"every force term is finite at the handed-over coordinates "
                            f"(max |E| = {hi:.6g} kJ/mol), which rules out a system that is broken as "
                            f"built — but the minimiser reproduction did not return a usable outcome "
                            f"({oc or 'not run'}: {mr.get('detail') or mr.get('note')}), and a "
                            f"single-point reading cannot see a lambda window it never visited")


def main():
    import tempfile
    import congeneric_fanout as cf
    want = (os.environ.get("PROBE_UNITS") or "").strip()
    units = [u for u in cf.default_units() if (not want or any(
        w.strip() and w.strip() in u["unit_id"] for w in want.split(",")))]
    if not units:
        raise SystemExit(f"[eprobe] no unit matches PROBE_UNITS={want!r}")
    print(f"[eprobe] {len(units)} unit(s), leg={LEG}", flush=True)

    in_dir = os.environ.get("PROBE_INPUT_DIR") or tempfile.mkdtemp(prefix="s1f_eprobe_in_")
    if not os.environ.get("PROBE_INPUT_DIR"):
        import step1_map_diag as md
        md.stage_inputs(in_dir)

    rows = []
    for u in units:
        row = probe_unit(u, in_dir)
        row["decision"], row["why"] = verdict(row)
        rows.append(row)
        print("[eprobe] %-46s %s — %s" % (row["edge"][:46], row["decision"], row["why"]), flush=True)

    doc = {
        "_what": "per-force single-point energy at the coordinates handed to OpenFE's sampler.setup(), "
                 "built on a free CPU runner from the PRODUCTION staged tree. Decides BLOCK vs RETRY "
                 "for a leg that died with 'Particle coordinate is NaN' inside the pre-MD minimiser.",
        "_no_spend": "no GPU, no instance, no S3 writes; reads the staged inputs only",
        "_stage": f"s3://{BUCKET}/{STAGE_PREFIX}/",
        "_leg": LEG,
        "rows": rows,
        "summary": {d: [r["edge"] for r in rows if r["decision"] == d]
                    for d in sorted({r["decision"] for r in rows})},
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"[eprobe] wrote {OUT}", flush=True)
    for d, edges in doc["summary"].items():
        print(f"[eprobe] {d}: {len(edges)} — {edges}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
