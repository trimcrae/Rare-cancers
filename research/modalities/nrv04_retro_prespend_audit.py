#!/usr/bin/env python3
"""
NR-V04 RETROSPECTIVE (RUNG 4) — $0 PRE-SPEND AUDIT of the inputs and the collector.

WHY THIS EXISTS. The sibling covalent feasibility panel was found on 2026-07-25 to be wrong in four
independent ways (wrong cysteine, nanometres under an Angstrom label, a positional chain split, contaminated
inputs). The retrospective is built, preregistered and UNLAUNCHED, and it SHARES the driver
(`nrv04_covalent_md.py`), the assembler (`nrv04_covalent_assemble.py`) and the readouts
(`nrv04_readouts.py`). Before ~$21 is spent, this audit checks whether it inherits any of them — and it does
so by reading THE ARTIFACT THAT WOULD ACTUALLY RUN, not the prefix the code names. That distinction is what
made the 2026-07-24 audit wrong: it cleared `nrv04-covalent-cofold` (the prefix the code pointed at) while the
panel had actually consumed `nrv04-descriptive-v3` (the prefix the workflow default supplied).

Three things are measured, all read-only, all $0:

  A. THE RETROSPECTIVE'S OWN CO-FOLD INPUTS. `nrv04_retro_panel.COFOLD_PREFIX` pins
     `nrv04-descriptive-v4/<system>/seed_<m>/` per leg. The published A1 audit
     (`nrv04-covalent-input-audit.json`) measured v4's **nr4a1** models only — it skipped `nr4a2`/`nr4a3`
     because they are not in its covalent-panel system allowlist. Those 6 skipped models are the inputs to 12
     of the retrospective's 18 primary (R1) legs, i.e. two thirds of the primary contrast has never had its
     chain identity verified from the artifact. This audit measures all 9.
     It also re-runs the leg pipeline's own invariant — EXACTLY ONE `*_model_0.cif` under the pinned model
     prefix (`_RETRO_PIPELINE`, exit 3 otherwise) — because a seed pin that silently resolves two models would
     corrupt the model-level statistics the frozen verdict is computed from (prereg 4a).

  B. A1 AT THE FROZEN COVALENT SITE, for the R2 arm. `retro_cov_nr4a1` is declared covalent and inherits
     `MAX_COVALENT_TETHER_A` (8.0 A), which `nrv04_covalent_md.build_system` now RAISES on. Measured at the
     preregistered site (NR4A1 C551 = construct 207), not at the nearest cysteine.

  C. THE COLLECTOR'S KEY CONTRACT. The MD driver writes its readouts under `R1_interface` / `R2_recruitment` /
     `R3_lys` (`nrv04_covalent_md.run_leg`). `nrv04_vast_launch.retro_collect` reads `d.get("R1")` /
     `d.get("R2")`. If the on-disk keys are the driver's, every `e1_plateau_A` the frozen gate receives is
     None, every leg is marked `technical_failure`, and the verdict is INDETERMINATE by construction. This
     audit reads the key names off REAL committed leg JSONs in the bucket rather than trusting either source
     file, and reports both what is there and what the collector would extract.

  D. THE REAL E1 DISTRIBUTION. Every landed leg's `R1_interface.plateau_A` is collected so the frozen
     primary test can be assessed for POWER against measured noise rather than against an assumption.

$0: read-only S3 + CPU. Emits `nrv04-retro-prespend-audit.json`. Exit code is always 0 — a diagnostic reports
its verdict, it never hides it by failing.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nrv04_retro_panel as retro                                          # noqa: E402  (the frozen panel)
from nrv04_covalent_input_audit import (                                   # noqa: E402
    index_models,
    list_keys,
    measure_model,
    resolve_lbd_offset,
)

# The retrospective's R1/R2 systems all carry the SAME ligand (NR-V04 active); R3's epimer arms carry the
# epimer. Taken from the frozen panel so this audit cannot drift from what would run.
SYSTEM_LIGAND = {a.cofold_system: a.ligand for a in retro.ARMS}

LEG_RESULT_PREFIXES = ("nrv04-covalent-results", "nrv04-covalent-results-chainfix", "nrv04-retro-results")


def audit_cofold_inputs(s3, bucket, out):
    """A + B: every co-fold model the AUTHORIZED legs would actually stage (R1 since AMENDMENT 3;
    the set of co-fold SYSTEMS is unchanged by the retirement, since retro_cov_nr4a1 shared nr4a1)."""
    lbd_offset, off_prov = resolve_lbd_offset()
    out["lbd_offset"] = lbd_offset
    out["lbd_offset_provenance"] = off_prov
    prefix = retro.COFOLD_PREFIX
    out["cofold_prefix_the_panel_pins"] = prefix
    keys = list_keys(s3, bucket, prefix.rstrip("/") + "/")
    systems = index_models(keys, prefix)

    rows = []
    wanted = sorted({(a.cofold_system, m) for a in retro.arms_for_stages()
                     for m in retro.COFOLD_MODEL_SEEDS})
    for system, model_seed in wanted:
        seed_dir = f"seed_{model_seed}"
        # The leg pipeline copies '*_model_0.cif' from the pinned seed prefix and REQUIRES exactly one.
        cands = [m for m in systems.get(system, []) if m["seed"] == seed_dir and m["model"] == 0]
        row = {"system": system, "cofold_model_seed": model_seed,
               "s3_prefix": f"s3://{bucket}/{prefix}/{system}/{seed_dir}/",
               "n_model_0_cifs_under_pinned_prefix": len(cands),
               "pipeline_seed_pin_ok": len(cands) == 1}
        if len(cands) != 1:
            row["error"] = ("the leg pipeline requires EXACTLY ONE *_model_0.cif under the pinned model prefix "
                            "(exit 3 otherwise)")
            rows.append(row)
            print(f"  {system}/{seed_dir}: {len(cands)} model_0 CIFs — PIN BROKEN", flush=True)
            continue
        m = cands[0]
        local = f"/tmp/retroaudit_{system}_{seed_dir}.cif"
        try:
            s3.download_file(bucket, m["key"], local)
            r = measure_model(local, SYSTEM_LIGAND.get(system, "nrv04"), lbd_offset)
        except Exception as e:                                             # noqa: BLE001
            r = {"error": f"{type(e).__name__}: {e}"}
        finally:
            if os.path.exists(local):
                os.remove(local)
        r.update({"key": m["key"], "mtime": m["mtime"]})
        row["measurement"] = r
        a1 = r.get("a1") or {}
        row["target_chain"] = r.get("target_chain")
        row["census"] = {c["chain"]: c["residues"] for c in (r.get("census") or [])}
        row["e3_roles"] = r.get("e3_roles")
        row["contaminant"] = r.get("contaminant")
        row["admissible_assembly"] = r.get("admissible_assembly")
        row["frozen_site_C551_dist_A"] = (a1.get("frozen_site") or {}).get("sg_dist_A")
        row["a1_verdict"] = a1.get("verdict", r.get("error"))
        rows.append(row)
        print(f"  {system}/{seed_dir}: census={row['census']} target={row['target_chain']} "
              f"e3={row['e3_roles']} contaminant={row['contaminant']} "
              f"C551={row['frozen_site_C551_dist_A']} A1={row['a1_verdict']}", flush=True)
    out["cofold_models"] = rows

    # --- the R2 (covalent) arm's admissibility, decided by the SAME gate the driver applies ----------------
    # ⚠ SCANS `retro.ARMS`, NOT `arms_for_stages()`. This measurement IS the evidence that retired R2
    # (AMENDMENT 3 defect 1), so it must survive the retirement: sourcing it from the AUTHORIZED stages would
    # return an empty set the day the arm was retired and report `0 of 0` — which reads as "nothing to see"
    # rather than "0 of 3 models are inside the 8.0 A limit". A retired arm's evidence must stay measurable.
    cov_arms = [a for a in retro.ARMS if a.covalent]
    cov_rows = [r for r in rows if r["system"] in {a.cofold_system for a in cov_arms}]
    dists = [r.get("frozen_site_C551_dist_A") for r in cov_rows]
    dists = [d for d in dists if d is not None]
    from nrv04_covalent_md import MAX_COVALENT_TETHER_A
    out["covalent_arm_admissibility"] = {
        "arms": [a.arm_id for a in cov_arms],
        "limit_A": MAX_COVALENT_TETHER_A,
        "frozen_site_fulllen": retro.TARGET_COV_RESNUM,
        "per_model_C551_dist_A": {f"{r['system']}/m{r['cofold_model_seed']}": r.get("frozen_site_C551_dist_A")
                                  for r in cov_rows},
        "n_models_passing_A1": sum(1 for d in dists if d <= MAX_COVALENT_TETHER_A),
        "n_models": len(cov_rows),
        "stage_retired": [a.arm_id for a in cov_arms if a.stage in retro.RETIRED_STAGES],
        "verdict": ("EVERY covalent-arm model FAILS the A1 tether gate — build_system RAISES, so these legs "
                    "cannot run at all" if dists and min(dists) > MAX_COVALENT_TETHER_A else "see per-model"),
    }


def audit_leg_key_contract(s3, bucket, out):
    """C + D: what key names real committed leg JSONs carry, and what retro_collect would extract from them."""
    found = []
    for pref in LEG_RESULT_PREFIXES:
        keys = [k for k, _s, _m in list_keys(s3, bucket, pref.rstrip("/") + "/")
                if k.endswith(".json") and k.rsplit("/", 1)[-1].startswith("leg_")]
        for k in keys:
            try:
                d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
            except Exception as e:                                          # noqa: BLE001
                found.append({"key": k, "error": f"{type(e).__name__}: {e}"})
                continue
            # VERBATIM the mapping in nrv04_vast_launch.retro_collect (copied, so a fix there shows up here as
            # a disagreement rather than being silently inherited).
            collect_e1 = (d.get("R1") or {}).get("plateau_A")
            collect_e2 = (d.get("R1") or {}).get("stable")
            collect_e3 = (d.get("R2") or {}).get("mean_contacts")
            driver_e1 = (d.get("R1_interface") or {}).get("plateau_A")
            found.append({
                "key": k, "prefix": pref, "leg_id": d.get("leg_id"), "seed": d.get("seed"),
                "top_level_keys": sorted(d.keys()),
                "driver_R1_interface_plateau_A": driver_e1,
                "driver_R3_lys_min_A": (d.get("R3_lys") or {}).get("min_A"),
                "collector_would_read_e1": collect_e1,
                "collector_would_read_e2": collect_e2,
                "collector_would_read_e3": collect_e3,
                "collector_marks_technical_failure": bool(d.get("blew_up")) or collect_e1 is None,
                "chain_split": d.get("chain_split"),
            })
    out["leg_results"] = found
    landed = [f for f in found if "error" not in f]
    e1s = [f["driver_R1_interface_plateau_A"] for f in landed
           if f["driver_R1_interface_plateau_A"] is not None]
    out["leg_key_contract"] = {
        "n_leg_jsons_read": len(landed),
        "n_with_driver_key_R1_interface": sum(1 for f in landed
                                              if f["driver_R1_interface_plateau_A"] is not None),
        "n_with_collector_key_R1": sum(1 for f in landed if f["collector_would_read_e1"] is not None),
        "n_collector_would_mark_technical_failure": sum(1 for f in landed
                                                        if f["collector_marks_technical_failure"]),
        "measured_E1_plateau_A": sorted(e1s),
        "verdict": ("MISMATCH: the driver writes R1_interface/R2_recruitment/R3_lys and retro_collect reads "
                    "R1/R2, so every e1_plateau_A is None and every leg is marked technical_failure"
                    if landed and not any(f["collector_would_read_e1"] is not None for f in landed)
                    else "see counts"),
    }


def main(argv=None):
    import argparse
    import boto3
    ap = argparse.ArgumentParser(description="NR-V04 retrospective $0 pre-spend audit (read-only).")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--out", default="research/modalities/nrv04-retro-prespend-audit.json")
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")
    s3 = boto3.client("s3")
    out = {"bucket": args.bucket, "panel": "nrv04_retrospective",
           "prereg": "nr4a3-nrv04-retrospective-prereg.md",
           "authorized_stages": list(retro.AUTHORIZED_STAGES),
           "retired_stages": list(retro.RETIRED_STAGES),
           "note": ("Reads the artifacts the legs would actually stage, not the prefixes the code names. "
                    "$0: read-only S3 + CPU. Nothing is launched.")}
    print(f"[retro-audit] A/B — co-fold inputs for the authorized {list(retro.AUTHORIZED_STAGES)} "
          f"legs (retired: {list(retro.RETIRED_STAGES)})", flush=True)
    try:
        audit_cofold_inputs(s3, args.bucket, out)
    except Exception as e:                                                  # noqa: BLE001
        out["cofold_audit_error"] = f"{type(e).__name__}: {e}"
        print(f"[retro-audit] co-fold audit ERROR: {e}", flush=True)
    print("[retro-audit] C/D — leg-JSON key contract + measured E1 distribution", flush=True)
    try:
        audit_leg_key_contract(s3, args.bucket, out)
    except Exception as e:                                                  # noqa: BLE001
        out["leg_audit_error"] = f"{type(e).__name__}: {e}"
        print(f"[retro-audit] leg audit ERROR: {e}", flush=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k not in ("leg_results", "cofold_models")}, indent=2),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
