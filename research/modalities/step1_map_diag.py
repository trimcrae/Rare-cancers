#!/usr/bin/env python3
"""WHY DID `leg-complex-FAILED-rc1` FAIL? — the atom-map matrix, on the PRODUCTION components. $0, CPU only.

★ WHY THIS EXISTS (2026-07-27). Step 1 fan-out unit `e_zaienne_cmpd19__cw_bio_nmethyl_amide__neutral__neutral`
(label `s1f-09`) aborted its complex leg with rc=1. The leg log carries the reason verbatim:

    [rbfe] LOMAP element_change=False: 17 mapped atoms for zaienne_cmpd19->cw_bio_nmethyl_amide
      ABORT: DEGENERATE atom map — mapped 17 atoms ... below the PROVABLE floor 20 (a complete map of 22
      atoms exists) ... Most likely the LOMAP MCS hit its 300s budget (RBFE_LOMAP_TIME_S); raise it and re-run.

That last sentence is a HYPOTHESIS the abort message asserts about ITSELF, and CLAUDE.md §4 does not accept a
"most likely" as a diagnosis. There are two competing mechanisms and they demand opposite fixes:

  H1  TIMEOUT. The MCS search ran out of its `RBFE_LOMAP_TIME_S` budget and returned its best partial match.
      Prediction: the map GROWS with the budget (t300 > t20) and the search burns most of its budget.
      Fix: raise the budget and re-run. Infrastructure-shaped; the edge is fine.

  H2  ELEMENT-CHANGE ASYMMETRY. `element_change=False` forbids mapping the one mismatched heavy atom, which
      severs the map around it; `element_change=True` maps it 1:1 as the single alchemical atom.
      Prediction: t20 == t300 for BOTH settings, in well under a second, and ec=True >> ec=False.
      Fix: the MAPPER's setting for this edge class, not the budget. The edge is fine but the call is wrong.

`nr4a3_rbfe._mapping`'s own docstring states the discriminator: a timeout moves both settings together, "a
real element-change asymmetry moves the two settings apart, and that is the entire reason this function
computes both". So the ONE observation that separates H1 from H2 is the 2x2 matrix
{element_change} x {budget}, with wall times. This module measures it.

★ AND IT MEASURES IT ON THE PRODUCTION COMPONENTS, WHICH IS THE WHOLE POINT. `atom_map_audit.py maps` already
sweeps both budgets, but it builds a FRESH ETKDG conformer per endpoint and its own docstring disclaims the
result: "treat every step 1 row as A PROPERTY OF THIS HARNESS until it is re-run through `_build_components`
on the staged SDFs." A pose-dependent explanation therefore survives that harness. This one calls
`nr4a3_rbfe._build_components` against the SAME staged, docked, common-frame tree the rented host downloads
(`s3://$BUCKET/$STAGE_PREFIX/`), with the SAME env the fan-out sets (`congeneric_fanout.unit_env`), so a row
here is a statement about the leg that actually failed.

It also runs `_mapping` EXACTLY as production calls it — positionally, with no `prefer_element_change` — so
the "what did the leg actually get" column is the real one and not a reconstruction.

RENTS NOTHING, WRITES NOTHING TO S3. It reads the staged inputs and writes `step1-map-diag.json` locally for
CI to commit back.

Usage (inside the parity image — needs openfe):
    MAP_DIAG_UNITS=cw_bio_nmethyl_amide python step1_map_diag.py     # one edge
    python step1_map_diag.py                                          # all 19
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "step1-map-diag.json")

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
STAGE_PREFIX = os.environ.get("STAGE_PREFIX", "nr4a3-step1-fanout/stage")
# The two budgets the repo already argues about. 20 s was the historical value; 300 s is today's default.
BUDGETS = tuple(int(x) for x in (os.environ.get("MAP_DIAG_BUDGETS") or "20,300").split(","))


def stage_inputs(dest):
    """Download the common-mode staged tree — the SAME one `_PREAMBLE` pulls onto every rented host.

    Deliberately the staged tree and not a rebuild: the entire value of this diagnostic over
    `atom_map_audit.maps` is that it reads the poses the failing leg read, so a pose-dependent story cannot
    hide behind a different conformer."""
    import boto3
    s3 = boto3.client("s3")
    n = 0
    pag = s3.get_paginator("list_objects_v2")
    for page in pag.paginate(Bucket=BUCKET, Prefix=STAGE_PREFIX.rstrip("/") + "/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            rel = key[len(STAGE_PREFIX.rstrip("/")) + 1:]
            if not rel or rel.endswith("/"):
                continue
            path = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            s3.download_file(BUCKET, key, path)
            n += 1
    print(f"[map-diag] staged {n} objects from s3://{BUCKET}/{STAGE_PREFIX}/ -> {dest}", flush=True)
    return n


def matrix_for_unit(unit, in_dir):
    """The 2x2 (element_change x budget) map matrix for ONE unit, plus what production actually picks.

    Returns a row dict. Every cell is a MEASUREMENT — n_mapped and wall seconds — or an error string; a cell
    that could not be computed says so rather than being dropped, because an absent cell read as a benign one
    is the failure mode this repo keeps paying for."""
    import importlib
    import openfe
    from openfe.setup import LomapAtomMapper
    from rdkit import Chem
    import congeneric_fanout as cf

    # The env a rented host sets for the COMPLEX leg of this unit, from the lane's own function so the
    # diagnostic cannot drift from the launcher (CLAUDE.md §1 — one fact, one home).
    env = cf.unit_env(unit, "complex", int(os.environ.get("N_WINDOWS", "12")))
    for k, v in env.items():
        os.environ[k] = str(v)
    os.environ["INPUT_DIR"] = in_dir
    # nr4a3_rbfe reads LIGAND_A/LIGAND_B/RECEPTOR/LEG/IN into MODULE GLOBALS at import time, so a reload is
    # not cosmetic — without it every unit after the first would be mapped with the first unit's ligands.
    import nr4a3_rbfe as rbfe
    rbfe = importlib.reload(rbfe)

    row = {
        "unit_id": unit["unit_id"], "edge_id": unit["edge_id"],
        "edge": f"{unit['ligand_a']}->{unit['ligand_b']}",
        "ligand_a": unit["ligand_a"], "ligand_b": unit["ligand_b"],
    }
    try:
        ligA, ligB, _ = rbfe._build_components(openfe, Chem)
    except Exception as e:  # noqa: BLE001
        row["build_error"] = f"{type(e).__name__}: {e}"
        return row
    row["n_atoms_a"] = ligA.to_rdkit().GetNumAtoms()
    row["n_atoms_b"] = ligB.to_rdkit().GetNumAtoms()

    # ---- the provable floor, from the module that owns that arithmetic. Never re-derived here. ----
    try:
        import atom_map_audit as ama
        b = ama.edge_bounds(unit["ligand_a"], unit["smiles_a"], unit["ligand_b"], unit["smiles_b"])
        row["provable_floor"] = b.get("total_floor_enforced")
        row["complete_map"] = b.get("expected_n_mapped_atoms")
    except Exception as e:  # noqa: BLE001
        row["provable_floor"] = None
        row["floor_error"] = f"{type(e).__name__}: {e}"

    # ---- the 2x2 matrix. threed=False exactly as production, so the map stays pose-independent. ----
    cells = {}
    for ec in (False, True):
        for budget in BUDGETS:
            t0 = time.time()
            try:
                m = next(LomapAtomMapper(time=budget, threed=False,
                                         element_change=ec).suggest_mappings(ligA, ligB))
                n = len(m.componentA_to_componentB)
                err = None
            except StopIteration:
                n, err = None, "StopIteration (LOMAP returned no mapping)"
            except Exception as e:  # noqa: BLE001
                n, err = None, f"{type(e).__name__}: {e}"
            cells[f"ec{int(ec)}_t{budget}"] = {"n_mapped": n, "wall_s": round(time.time() - t0, 2),
                                               "error": err}
    row["matrix"] = cells

    # ---- what PRODUCTION picks. Called positionally with no prefer_element_change, exactly as
    #      nr4a3_rbfe.run_leg / _prep_units do — this column must be the real one, not a reconstruction. ----
    t0 = time.time()
    try:
        m = rbfe._mapping(openfe, ligA, ligB)
        row["production_n_mapped"] = len(m.componentA_to_componentB)
        row["production_error"] = None
    except SystemExit as e:  # an ABORT is a legitimate outcome and must be recorded, not raised
        row["production_n_mapped"] = None
        row["production_error"] = f"SystemExit: {e}"
    except Exception as e:  # noqa: BLE001
        row["production_n_mapped"] = None
        row["production_error"] = f"{type(e).__name__}: {e}"
    row["production_wall_s"] = round(time.time() - t0, 2)

    floor = row.get("provable_floor")
    prod = row.get("production_n_mapped")
    row["production_clears_floor"] = (None if (floor is None or prod is None) else prod >= floor)
    return row


def verdict(row):
    """H1 (timeout) vs H2 (element-change asymmetry) vs CLEAN, from the row's own cells. PURE.

    The test is the one `nr4a3_rbfe._mapping`'s docstring names: a timeout moves BOTH element_change settings
    together and burns the budget; an element-change asymmetry separates them and returns instantly. Anything
    that matches neither says so — an unclassifiable row must never be rendered as a clean one."""
    cells = row.get("matrix") or {}

    def n(ec, b):
        return (cells.get(f"ec{ec}_t{b}") or {}).get("n_mapped")

    def w(ec, b):
        return (cells.get(f"ec{ec}_t{b}") or {}).get("wall_s")

    lo, hi = min(BUDGETS), max(BUDGETS)
    floor = row.get("provable_floor")
    if row.get("production_clears_floor"):
        return "CLEAN", f"production mapped {row.get('production_n_mapped')} >= provable floor {floor}"
    if floor is None or row.get("production_n_mapped") is None:
        return "UNVERIFIABLE", "no provable floor or no production map — not a clean reading, an absent one"

    grew = [ec for ec in (0, 1) if None not in (n(ec, lo), n(ec, hi)) and n(ec, hi) > n(ec, lo)]
    slow = [ec for ec in (0, 1) for b in BUDGETS if (w(ec, b) or 0) >= 0.5 * b]
    if grew or slow:
        return "TIMEOUT", (f"the map grows with the budget (settings {grew}) or the search burns its budget "
                           f"(settings {slow}) — H1: raise RBFE_LOMAP_TIME_S")
    sep = [b for b in BUDGETS if None not in (n(0, b), n(1, b)) and n(1, b) > n(0, b)]
    if sep and all(n(1, b) is not None and n(1, b) >= floor for b in sep):
        return "ELEMENT_CHANGE", (
            f"element_change=True clears the floor ({[n(1, b) for b in sep]} >= {floor}) at every budget while "
            f"element_change=False does not ({[n(0, b) for b in sep]}), and neither setting moves between "
            f"t{lo} and t{hi} — H2: the budget is not binding; the mapper's element_change choice is")
    return "UNEXPLAINED", ("neither the timeout nor the element-change signature fits — this needs a human "
                           "before any GPU is rented for this edge")


def main():
    import tempfile
    import congeneric_fanout as cf
    want = (os.environ.get("MAP_DIAG_UNITS") or "").strip()
    units = [u for u in cf.default_units() if (not want or any(
        w.strip() and w.strip() in u["unit_id"] for w in want.split(",")))]
    if not units:
        raise SystemExit(f"[map-diag] no unit matches MAP_DIAG_UNITS={want!r}")
    print(f"[map-diag] {len(units)} unit(s); budgets {BUDGETS}", flush=True)

    in_dir = os.environ.get("MAP_DIAG_INPUT_DIR") or tempfile.mkdtemp(prefix="s1f_mapdiag_")
    if not os.environ.get("MAP_DIAG_INPUT_DIR"):
        stage_inputs(in_dir)

    rows = []
    for u in units:
        row = matrix_for_unit(u, in_dir)
        row["verdict"], row["why"] = verdict(row)
        rows.append(row)
        cells = row.get("matrix") or {}
        print("[map-diag] %-46s %s | %s | prod=%s floor=%s"
              % (row["edge"][:46], row["verdict"],
                 " ".join("%s=%s(%.1fs)" % (k, v.get("n_mapped"), v.get("wall_s") or 0.0)
                          for k, v in sorted(cells.items())),
                 row.get("production_n_mapped"), row.get("provable_floor")), flush=True)

    doc = {
        "_what": "step 1 fan-out atom-map matrix on the PRODUCTION staged components — element_change x LOMAP "
                 "budget, with wall times, to separate a timed-out MCS from an element-change asymmetry",
        "_no_spend": "no GPU, no instance; reads the staged inputs only",
        "_stage": f"s3://{BUCKET}/{STAGE_PREFIX}/",
        "budgets_s": list(BUDGETS),
        "rows": rows,
        "summary": {v: [r["edge"] for r in rows if r["verdict"] == v]
                    for v in sorted({r["verdict"] for r in rows})},
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"[map-diag] wrote {OUT}", flush=True)
    for v, edges in doc["summary"].items():
        print(f"[map-diag] {v}: {len(edges)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
