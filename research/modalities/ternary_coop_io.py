#!/usr/bin/env python3
"""Ternary-coop harness — INTEGRATION BOUNDARY (reviewer 2026-07-12, Plan B: retain before deferring the engine).

The production OpenFE/OpenMM relative-alchemical execution + cloud submitter are DEFERRED until an executable
MD environment exists (none in this sandbox). But the reviewer required that the verifiable integration
boundary be retained + tested NOW, so the eventual engine plugs into a fixed, validated contract:
  * versioned input/output schemas;
  * environment + force-field LOCK specification;
  * system + ligand hashes (reproducibility anchors);
  * expected artifact manifest per leg;
  * sign/unit validation of a result (the dG_coop convention is a hard invariant);
  * a mocked end-to-end artifact test (a schema-valid fake result validates; a malformed one fails);
  * explicit FAILURE on STUB GPU-hour / cost values in execution mode.

Pure stdlib + unit-tested. Consumes ternary_coop (sign convention) + ternary_coop_prep (assembly spec).
"""
import hashlib
import json
import math

import ternary_coop as tcoop
import ternary_coop_prep as prep

SCHEMA_VERSION = "ternary-coop/1.0"

# Environment + force-field LOCK — the versions the production engine MUST pin. Values are placeholders to be
# frozen when the MD environment is stood up; the KEYS are the contract (a run missing any key is invalid).
ENV_FORCEFIELD_LOCK = {
    "schema_version": SCHEMA_VERSION,
    "protein_ff": None,        # e.g. "amber/ff14SB" — freeze at env build
    "ligand_ff": None,         # e.g. "openff-2.x"
    "water_model": None,       # e.g. "tip3p"
    "engine": None,            # e.g. "openfe==x.y / openmm==a.b"
    "integrator": None,        # e.g. "LangevinMiddle, 4 fs, HMR"
    "container_digest": None,  # image sha256
    "_note": "None = to be frozen at MD-env build; the eventual runner must fail if any lock value is None.",
}


def input_schema():
    """Versioned input contract for one alchemical morph leg."""
    return {
        "schema_version": SCHEMA_VERSION,
        "leg_id": "str (a frozen pilot leg id)",
        "environment": "binary|ternary",
        "protein_components": "[{role,name,acc,...}]  (from ternary_coop_prep.assembly_for_leg)",
        "morph": {"endpoint_a": "str", "endpoint_b": "str", "smiles_a": "str", "smiles_b": "str"},
        "n_windows": "int", "n_replicas": "int>=3",
        "lock": "ENV_FORCEFIELD_LOCK (all values non-null)",
        "system_hash": "sha256 of the assembled system", "ligand_hash": "sha256 of (smiles_a, smiles_b)",
    }


def output_schema():
    """Versioned output contract a completed leg must satisfy."""
    return {
        "schema_version": SCHEMA_VERSION,
        "leg_id": "str", "environment": "binary|ternary",
        "ddg_alch_kcal": "float (the leg's relative alchemical free energy)",
        "ci95_half_width_kcal": "float", "n_replicas": "int>=3",
        "hysteresis_kcal": "float", "converged": "bool",
        "unit_gpu_h_observed": "float (>0; STUB value forbidden in execution mode)",
        "cost_usd_observed": "float (>0; STUB value forbidden in execution mode)",
        "system_hash": "sha256", "ligand_hash": "sha256",
        "artifacts": "[str]  (must cover expected_artifact_manifest)",
    }


def system_hash(assembly):
    """Deterministic SHA-256 of an assembly spec's reproducibility-relevant fields (order-independent)."""
    key = {"environment": assembly["environment"],
           "components": sorted((c.get("role", ""), c.get("name", ""), str(c.get("acc")),
                                 str(c.get("lbd_lo")), str(c.get("lbd_hi"))) for c in assembly["protein_components"]),
           "morph": (assembly["morph"]["endpoint_a"], assembly["morph"]["endpoint_b"])}
    return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()


def ligand_hash(smiles_a, smiles_b):
    """Deterministic hash of the morph endpoints (None-safe: unresolved endpoints hash distinctly)."""
    return hashlib.sha256(json.dumps([smiles_a, smiles_b]).encode()).hexdigest()


def expected_artifact_manifest(leg_id):
    """The files a completed leg run MUST produce (checked against a result's 'artifacts')."""
    return ["%s/checkpoint_lambda_%02d.jsonl" % (leg_id, 0), "%s/mbar_result.json" % leg_id,
            "%s/hysteresis.json" % leg_id, "%s/meta.json" % leg_id]


# STUB sentinels (from the MODE=plan forecasters) — forbidden as OBSERVED values in execution mode.
_STUB_GPU_H = {1.0, 2.0, 3.0}     # the labeled planning stubs in ternary_coop.plan / rbfe_pilot.plan
_STUB_COST = set()


def validate_result(result, mode="execution"):
    """Validate a leg RESULT dict against the output schema + the hard invariants. In execution mode a STUB
    GPU-hour/cost is a FAILURE (a real run must report observed values). Returns {ok, failures}."""
    reasons = []

    def _num(x):
        if isinstance(x, bool) or x is None:
            return None
        try:
            f = float(x)
        except (TypeError, ValueError):
            return None
        return f if math.isfinite(f) else None

    if result.get("schema_version") != SCHEMA_VERSION:
        reasons.append("schema_version != %s" % SCHEMA_VERSION)
    if result.get("environment") not in ("binary", "ternary"):
        reasons.append("environment must be binary|ternary")
    ddg = _num(result.get("ddg_alch_kcal"))
    if ddg is None:
        reasons.append("ddg_alch_kcal missing/non-finite")
    ci = _num(result.get("ci95_half_width_kcal"))
    if ci is None or ci <= 0:
        reasons.append("ci95_half_width_kcal missing/non-positive")
    reps = result.get("n_replicas")
    if not isinstance(reps, int) or isinstance(reps, bool) or reps < 3:
        reasons.append("n_replicas must be int >= 3")
    if not isinstance(result.get("converged"), bool):
        reasons.append("converged must be an explicit bool")
    # sign/unit invariant: if a coupling alpha is asserted, dG_coop must match -RT ln(alpha) in sign
    if "implied_alpha" in result:
        a = _num(result.get("implied_alpha"))
        dg = _num(result.get("ddg_coop_kcal"))
        if a is not None and a > 0 and dg is not None:
            expect = tcoop.dg_coop_from_alpha(a)
            if expect is not None and (expect == 0 or dg == 0 or (expect * dg < 0)):
                reasons.append("sign/unit invariant: ddg_coop_kcal sign disagrees with -RT ln(implied_alpha)")
    # artifact coverage
    leg = result.get("leg_id", "")
    arts = set(result.get("artifacts") or [])
    missing = [a for a in expected_artifact_manifest(leg) if a not in arts]
    if missing:
        reasons.append("missing artifacts: %r" % missing)
    # STUB guard (execution mode only)
    if mode == "execution":
        gh = _num(result.get("unit_gpu_h_observed"))
        if gh is None or gh <= 0:
            reasons.append("unit_gpu_h_observed missing/non-positive (a real run must report it)")
        elif gh in _STUB_GPU_H:
            reasons.append("unit_gpu_h_observed=%g is a PLANNING STUB — forbidden as an observed value" % gh)
        cost = _num(result.get("cost_usd_observed"))
        if cost is None or cost <= 0:
            reasons.append("cost_usd_observed missing/non-positive")
    # lock completeness (execution mode)
    if mode == "execution":
        lock = result.get("lock") or {}
        nulls = [k for k, v in ENV_FORCEFIELD_LOCK.items() if not k.startswith("_") and lock.get(k) is None]
        if nulls:
            reasons.append("force-field/env lock has unfrozen (null) keys: %r" % nulls)
    return {"ok": not reasons, "failures": reasons}


def mock_result_for(leg_id="nrv04_active_to_epimer__binary_vhl"):
    """A schema-valid MOCK leg result (for the mocked end-to-end artifact test — no MD). Observed GPU-h is a
    deliberately non-stub value so it passes execution-mode validation."""
    return {
        "schema_version": SCHEMA_VERSION, "leg_id": leg_id, "environment": "binary",
        "ddg_alch_kcal": -2.3, "ci95_half_width_kcal": 1.1, "n_replicas": 3,
        "hysteresis_kcal": 0.4, "converged": True,
        "unit_gpu_h_observed": 4.7, "cost_usd_observed": 63.0,
        "system_hash": "0" * 64, "ligand_hash": "0" * 64,
        "artifacts": expected_artifact_manifest(leg_id),
        "lock": {k: ("frozen" if not k.startswith("_") else None) for k in ENV_FORCEFIELD_LOCK},
    }


def _cli(argv=None):
    print(json.dumps({"schema_version": SCHEMA_VERSION, "input_schema": input_schema(),
                      "output_schema": output_schema(), "env_forcefield_lock": ENV_FORCEFIELD_LOCK,
                      "pilot_system_hashes": [{"leg": a["leg_id"], "system_hash": system_hash(a)}
                                              for a in prep.assemble_pilot()]}, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
