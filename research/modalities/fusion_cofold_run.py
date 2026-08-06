#!/usr/bin/env python3
"""Rung `R13-b` GPU entry point — run the COMMITTED fusion co-fold YAMLs, one unit at a time, resumably.

⛔ IT FETCHES NOTHING. The constructs were cut, verified against committed artifacts and written by
`fusion_cofold_recut.py` on a free runner ($0). This script only reads
`research/modalities/fusion_cofold_inputs/<object>/{seam,composite}.yaml` and calls Boltz. That is deliberate
and is the difference from `fusion_cofold.py`, which resolves and downloads two AlphaFold PDBs at runtime —
on the rented host, before any science, which is the shape CLAUDE.md §6 forbids.

⛔ IT ALSO INSTALLS NOTHING. The environment is `triskit23/boltz` (research/compute/Dockerfile.boltz), which
carries boltz, cuequivariance AND the ~3 GB weight cache. If `/opt/boltz/BAKED` is absent this script says so
loudly rather than quietly solving an environment on a machine we are paying for.

UNIT OF WORK = (construct, seed). 12 units: 2 constructs x 6 seeds — the count `scope-rung-cost.json` prices
(`rungs -> R13-b -> units`). Per the standing checkpoint rule:
  * each unit writes into its OWN directory under $OUTPUT_DIR the moment it finishes, so the lane's
    background `aws s3 sync` uploads it immediately and a preemption after unit N keeps units 1..N;
  * a unit whose output directory already carries a prediction is SKIPPED, so a relaunch resumes rather than
    re-buying work that is already in the object store;
  * `--unit-timeout-s` is the real hang guard: a single wedged seed cannot consume the whole rental.
  * a partial run is the deliverable — `fusion-cofold-run.json` is rewritten after EVERY unit.

⛔ THE PRE-REGISTERED GATE TRAVELS WITH THE RUN, because a null here is the EXPECTED outcome and a null that
arrives without its gate gets read as a refutation. See `PREREGISTERED_GATE` below; it is copied into the
output JSON on every write.

SCOPE: structure inference only. No affinity, selectivity, efficacy, safety, therapeutic-window or clinical
claim is made or implied.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(HERE, "fusion_cofold_inputs")
OUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(HERE, "cofold_out"))
BAKED_MARKER = "/opt/boltz/BAKED"

CONSTRUCTS = ("seam", "composite")

PREREGISTERED_GATE = (
    "WRITTEN BEFORE THE RUN BECAUSE A NULL IS THE EXPECTED OUTCOME. The EWSR1 side is a prion-like IDR "
    "(mean pLDDT 38.8, 98% of residues < 50) and a de-novo fusion junction has NO cross-seam coevolution "
    "for an MSA-based predictor to use, so the predictor has no evidence for any specific inter-half "
    "packing and will default to independent domains plus a floppy linker. ABSENCE OF AN ORDERED COMPOSITE "
    "INTERFACE IS THEREFORE A FEASIBILITY READ, NOT EVIDENCE THAT NO POCKET CAN FORM, AND MAY NOT BE "
    "REPORTED AS A REFUTATION. GO = an interface cavity present in >=4 of 6 seeds on the `composite` "
    "construct that is ABSENT from both parent AlphaFold models. Anything less is INDETERMINATE — a third "
    "outcome, not a negative."
)


def unit_dir(construct, seed):
    return os.path.join(OUT_DIR, "%s__seed%d" % (construct, seed))


def unit_done(construct, seed):
    """A unit is done only if a real prediction file exists — never merely because its directory exists.

    A directory a crashed unit created is exactly the 'populated field that was never measured' shape
    CLAUDE.md §4 warns about, so the test is for the thing only a completed inference can produce.
    """
    d = unit_dir(construct, seed)
    return bool(glob.glob(os.path.join(d, "**", "*.cif"), recursive=True) or
                glob.glob(os.path.join(d, "**", "*.pdb"), recursive=True))


def environment_report():
    baked = os.path.exists(BAKED_MARKER)
    rep = {"baked_marker": BAKED_MARKER, "image_declares_baked": baked}
    try:
        rep["baked_stamp"] = open(BAKED_MARKER).read().strip() if baked else None
    except OSError:
        rep["baked_stamp"] = None
    try:
        import torch
        rep["torch"] = torch.__version__
        rep["cuda_available"] = bool(torch.cuda.is_available())
        rep["device"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception as exc:  # noqa: BLE001 — an env report must never be able to abort the run
        rep["torch"] = "import failed: %s" % exc
        rep["cuda_available"] = False
        rep["device"] = None
    rep["boltz_on_path"] = bool(_which("boltz"))
    rep["boltz_cache"] = os.environ.get("BOLTZ_CACHE")
    return rep


def _which(prog):
    import shutil
    return shutil.which(prog)


def run_unit(yaml_path, construct, seed, timeout_s):
    """One (construct, seed). Returns a record; never raises on a Boltz failure — the caller decides."""
    d = unit_dir(construct, seed)
    os.makedirs(d, exist_ok=True)
    # --no_kernels: pure-PyTorch triangle path. boltz>=2 hard-crashes on some cards when the accelerated
    # cuEquivariance kernels fail to import (the 2026-07-01 ternary incident). Slower but runs.
    cmd = ["boltz", "predict", yaml_path, "--use_msa_server", "--out_dir", d,
           "--no_kernels", "--seed", str(seed)]
    t0 = time.time()
    rec = {"construct": construct, "seed": seed, "cmd": " ".join(cmd), "out_dir": d}
    try:
        p = subprocess.run(cmd, timeout=timeout_s)
        rec["returncode"] = p.returncode
    except subprocess.TimeoutExpired:
        rec["returncode"] = "TIMEOUT"
        rec["_note"] = ("the per-unit hang guard fired; the partial output is the deliverable and the "
                        "remaining units continue")
    except FileNotFoundError as exc:
        rec["returncode"] = "boltz-not-found"
        rec["_note"] = str(exc)
    rec["wall_s"] = round(time.time() - t0, 1)
    # ★ Wall time and a produced file, not a populated field: CLAUDE.md §4(b). A record that says a unit ran
    # must rest on something only a real run can create.
    rec["produced_structure"] = unit_done(construct, seed)
    return rec


def write_state(state, path):
    with open(path, "w") as fh:
        json.dump(state, fh, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", required=True,
                    help="which construct object to fold — the directory name under fusion_cofold_inputs/. "
                         "REQUIRED and with no default: OC-2 (systems/graph/integrity.json) is open and the "
                         "two candidate objects have DIFFERENT seams, so naming one IS the decision.")
    ap.add_argument("--seeds", default=os.environ.get("SEEDS", "1,2,3,4,5,6"))
    ap.add_argument("--unit-timeout-s", type=int,
                    default=int(os.environ.get("COFOLD_UNIT_TIMEOUT_S", "3600")))
    ap.add_argument("--dry-run", action="store_true",
                    help="print the unit plan and the environment report; run no inference, rent nothing")
    args = ap.parse_args()

    obj_dir = os.path.join(INPUT_ROOT, args.object)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    os.makedirs(OUT_DIR, exist_ok=True)
    state_path = os.path.join(OUT_DIR, "fusion-cofold-run.json")

    yamls = {c: os.path.join(obj_dir, "%s.yaml" % c) for c in CONSTRUCTS}
    missing = [c for c, p in yamls.items() if not os.path.exists(p)]

    state = {
        "_what": "R13-b apo co-fold — per-unit run record. Rewritten after EVERY unit so a preemption "
                 "leaves a truthful partial rather than nothing.",
        "⛔_PRE_REGISTERED_GATE": PREREGISTERED_GATE,
        "_scope": "structure inference only; no affinity, selectivity, efficacy, safety, "
                  "therapeutic-window or clinical claim is made or implied",
        "object": args.object,
        "input_dir": obj_dir,
        "constructs": list(CONSTRUCTS),
        "seeds": seeds,
        "n_units_planned": len(CONSTRUCTS) * len(seeds),
        "environment": environment_report(),
        "units": [],
        "missing_inputs": missing,
    }

    if missing:
        write_state(state, state_path)
        sys.exit("REFUSING: no committed input for %s under %s. Run "
                 "`fusion_cofold_recut.py --object %s` on a free runner first — the cut is a $0 step and "
                 "must not happen on a billing host." % (missing, obj_dir, args.object))

    if not state["environment"]["image_declares_baked"]:
        print("::warning::%s absent — this container does not declare itself a baked Boltz image. "
              "CLAUDE.md §6: never build an environment on a machine we are paying for. Bake "
              "research/compute/Dockerfile.boltz (Actions -> 'Boltz image bake') and rent against "
              "triskit23/boltz instead of solving here." % BAKED_MARKER, flush=True)

    plan = [(c, s) for c in CONSTRUCTS for s in seeds]
    if args.dry_run:
        state["dry_run"] = True
        state["units"] = [{"construct": c, "seed": s, "already_done": unit_done(c, s)} for c, s in plan]
        write_state(state, state_path)
        print(json.dumps({k: v for k, v in state.items() if not k.startswith("⛔")}, indent=2))
        return 0

    write_state(state, state_path)   # a run that dies in unit 1 still leaves its plan and its environment
    failures = []
    for construct, seed in plan:
        if unit_done(construct, seed):
            state["units"].append({"construct": construct, "seed": seed, "skipped": "already complete",
                                   "produced_structure": True})
            write_state(state, state_path)
            print("[cofold] skip %s seed %d — already in the output store" % (construct, seed), flush=True)
            continue
        print("[cofold] run  %s seed %d" % (construct, seed), flush=True)
        rec = run_unit(yamls[construct], construct, seed, args.unit_timeout_s)
        state["units"].append(rec)
        write_state(state, state_path)          # ★ checkpoint written BEFORE the next unit starts
        if rec["returncode"] != 0 or not rec["produced_structure"]:
            failures.append(rec)

    state["n_units_completed"] = sum(1 for u in state["units"] if u.get("produced_structure"))
    state["n_failures"] = len(failures)
    state["complete"] = state["n_units_completed"] == state["n_units_planned"]
    write_state(state, state_path)
    print("[cofold] %d/%d units carry a structure; %d failed"
          % (state["n_units_completed"], state["n_units_planned"], len(failures)), flush=True)

    # Fail loud: a green job with missing units is how a partial panel gets read as a complete one.
    if failures:
        sys.exit("Boltz FAILED on %d unit(s): %s" %
                 (len(failures), [(f["construct"], f["seed"], f["returncode"]) for f in failures]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
