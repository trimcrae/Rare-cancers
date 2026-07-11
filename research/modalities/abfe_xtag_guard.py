#!/usr/bin/env python3
"""Cross-tag ABFE reduction guard (external reviewer §8).

A *cross-tag reduce* pairs a DENSE (λ-repaired, 16-window) complex leg living under one S3 checkpoint tag with
the SHARED STANDARD (12-window) solvent leg living under another tag (the `complex_tag_overrides` path in
reduce-abfe-ci.yml). That is only algebraically valid if the two legs describe the *same physical system, same
thermodynamics, same conventions* — otherwise the shared-solvent cancellation is meaningless.

This module provides two independent safeguards, both PURE (no numpy / pymbar / openmm) so they run in the free
CPU reduce runner and are fully unit-testable:

  * ``check_xtag_compatibility`` — FAIL-CLOSED metadata compatibility check across the cross-tag leg pair.
  * ``ddg_direct_from_complex_diff`` — proves the shared-solvent cancellation ALGEBRAICALLY by computing the
    selectivity ΔΔG two ways (full-ABFE subtraction vs the direct complex-leg-difference form) and asserting
    they agree to a tight tolerance.

Neither reuses the MBAR machinery; both operate on already-reduced numbers / metadata dicts.
"""
import math
import os
import sys


# Metadata keys we look for. A value may live in the leg's meta.json OR its reference_aux.json (either is fine
# — meta wins). Identity keys are tried in priority order; the FIRST present-on-both key decides.
_LIGAND_ID_KEYS = ("ligand_inchikey", "inchikey", "ligand_smiles", "smiles",
                   "ligand_id", "ligand_name", "ligand")
_TEMP_KEYS = ("temperature_K", "temperature_k", "temperature")
_RESTRAINT_CONV_KEYS = ("restraint_convention", "standard_state_convention", "restraint_type")
_ENDPOINT_KEYS = ("thermodynamic_endpoints", "lambda_endpoints", "endpoints")
_REPLICATE_KEYS = ("seed", "replicate", "replicate_id")


def _fetch(meta, aux, keys):
    """First (key, value) found for any of `keys`, meta preferred over aux. (None, None) if absent."""
    for src in (meta, aux):
        if isinstance(src, dict):
            for k in keys:
                if k in src and src[k] is not None:
                    return k, src[k]
    return None, None


def check_xtag_compatibility(complex_meta, solvent_meta, complex_aux=None, solvent_aux=None,
                             complex_hashes=None, solvent_hashes=None):
    """Confirm a dense-complex + standard-solvent cross-tag reduce is compatible enough to be valid.

    Verifies IDENTICAL (or, where a leg legitimately differs by design, CONVENTION-consistent):
      * ligand topology/parameters — n_ligand_atoms AND any recorded ligand identity (SMILES/InChIKey/name);
      * temperature + thermodynamic endpoints;
      * standard-state + restraint conventions — the complex leg must carry restraint_standard_state_dg, the
        solvent leg must NOT be restrained, and the restraint convention tag (if recorded) must be present;
      * replicate mapping (which complex replicate is paired with the shared solvent);
      * if solvent object hashes are provided, that the SAME solvent leg is used (hashes match).

    FAIL-CLOSED: anything that cannot be positively confirmed is listed in ``unverifiable``; for the
    SAFETY-CRITICAL items (ligand identity, temperature, restraint convention) an unverifiable result forces
    ``compatible=False`` unless the metadata explicitly confirms them. Non-critical unverifiables (endpoints,
    replicate mapping, solvent-hash when not provided) are surfaced but do not by themselves block.

    Returns {"compatible": bool, "mismatches": [str...], "checked": [str...], "unverifiable": [str...]}.
    """
    mismatches = []
    checked = []
    unverifiable = []
    critical_unverifiable = False  # any safety-critical item we could not confirm → fail closed

    def note_unverifiable(msg, critical=False):
        nonlocal critical_unverifiable
        unverifiable.append(msg + (" [SAFETY-CRITICAL → fail-closed]" if critical else ""))
        if critical:
            critical_unverifiable = True

    # --- 1. ligand topology: atom count -----------------------------------------------------------------
    _, c_n = _fetch(complex_meta, complex_aux, ("n_ligand_atoms",))
    _, s_n = _fetch(solvent_meta, solvent_aux, ("n_ligand_atoms",))
    if c_n is not None and s_n is not None:
        if int(c_n) == int(s_n):
            checked.append(f"n_ligand_atoms match ({int(c_n)})")
        else:
            mismatches.append(f"n_ligand_atoms: complex {int(c_n)} vs solvent {int(s_n)}")
    else:
        note_unverifiable("n_ligand_atoms not recorded on both legs", critical=True)

    # --- 2. ligand identity: SMILES / InChIKey / name ---------------------------------------------------
    id_confirmed = False
    id_mismatch = False
    for k in _LIGAND_ID_KEYS:
        _, cv = _fetch(complex_meta, complex_aux, (k,))
        _, sv = _fetch(solvent_meta, solvent_aux, (k,))
        if cv is not None and sv is not None:
            if str(cv).strip() == str(sv).strip():
                checked.append(f"ligand identity {k} match ({str(cv).strip()})")
                id_confirmed = True
                break
            else:
                mismatches.append(f"ligand identity {k}: complex {cv!r} vs solvent {sv!r}")
                id_mismatch = True
                break
    if not id_confirmed and not id_mismatch:
        note_unverifiable("ligand identity (SMILES/InChIKey/name) not recorded on both legs — "
                          "cannot confirm the same ligand", critical=True)

    # --- 3. temperature ---------------------------------------------------------------------------------
    _, c_T = _fetch(complex_meta, complex_aux, _TEMP_KEYS)
    _, s_T = _fetch(solvent_meta, solvent_aux, _TEMP_KEYS)
    if c_T is not None and s_T is not None:
        if abs(float(c_T) - float(s_T)) <= 1e-6:
            checked.append(f"temperature match ({float(c_T):.4f} K)")
        else:
            mismatches.append(f"temperature: complex {float(c_T)} K vs solvent {float(s_T)} K")
    else:
        note_unverifiable("temperature not recorded on both legs", critical=True)

    # --- 4. thermodynamic endpoints (non-critical: window COUNT differs by design, endpoints should not) -
    _, c_ep = _fetch(complex_meta, complex_aux, _ENDPOINT_KEYS)
    _, s_ep = _fetch(solvent_meta, solvent_aux, _ENDPOINT_KEYS)
    if c_ep is not None and s_ep is not None:
        if c_ep == s_ep:
            checked.append(f"thermodynamic endpoints match ({c_ep})")
        else:
            mismatches.append(f"thermodynamic endpoints: complex {c_ep!r} vs solvent {s_ep!r}")
    else:
        note_unverifiable("thermodynamic endpoints (coupled/decoupled λ) not explicitly recorded on both "
                          "legs — endpoints must match even though window COUNT legitimately differs "
                          "(dense 16 vs standard 12)")

    # --- 5. standard-state + restraint conventions -----------------------------------------------------
    _, c_ssc = _fetch(complex_meta, complex_aux, ("restraint_standard_state_dg",))
    if c_ssc is None:
        mismatches.append("complex leg has no restraint_standard_state_dg (required for the complex leg)")
    elif not math.isfinite(float(c_ssc)):
        mismatches.append(f"complex restraint_standard_state_dg is non-finite ({c_ssc})")
    else:
        checked.append(f"complex leg carries restraint_standard_state_dg ({float(c_ssc):+.3f} kcal/mol)")
    _, s_ssc = _fetch(solvent_meta, solvent_aux, ("restraint_standard_state_dg",))
    if s_ssc is not None:
        mismatches.append("solvent leg unexpectedly carries a restraint_standard_state_dg "
                          "(the solvent leg must be UNrestrained)")
    else:
        checked.append("solvent leg is unrestrained (no restraint_standard_state_dg), as required")
    # restraint / standard-state convention tag (safety-critical). Compared PER-KEY across the legs: if BOTH
    # legs record the same convention key and the values differ → a genuine convention mismatch (incompatible);
    # if the complex records one → confirmed; if the complex records none → fail-closed unverifiable.
    conv_confirmed = False
    conv_mismatch = False
    for k in _RESTRAINT_CONV_KEYS:
        _, cv = _fetch(complex_meta, complex_aux, (k,))
        _, sv = _fetch(solvent_meta, solvent_aux, (k,))
        if cv is not None and sv is not None and str(cv).strip() != str(sv).strip():
            mismatches.append(f"restraint/standard-state convention {k}: complex {cv!r} vs solvent {sv!r}")
            conv_mismatch = True
        elif cv is not None and not conv_confirmed:
            checked.append(f"restraint convention recorded on complex ({k}={cv!r})")
            conv_confirmed = True
    if not conv_confirmed and not conv_mismatch:
        note_unverifiable("restraint / standard-state convention tag not recorded on the complex leg — "
                          "cannot confirm the Boresch-6DOF + analytic-SSC convention combine_legs assumes",
                          critical=True)

    # --- 6. replicate mapping (non-critical: recorded so the pairing is auditable) ---------------------
    _, c_rep = _fetch(complex_meta, complex_aux, _REPLICATE_KEYS)
    _, s_rep = _fetch(solvent_meta, solvent_aux, _REPLICATE_KEYS)
    if c_rep is not None and s_rep is not None:
        checked.append(f"replicate mapping recorded (complex replicate={c_rep} paired with "
                       f"shared solvent replicate={s_rep})")
    else:
        note_unverifiable("replicate mapping (which complex replicate is paired with the shared solvent) "
                          "not fully recorded")

    # --- 7. solvent object hashes: SAME solvent leg ----------------------------------------------------
    if complex_hashes is not None and solvent_hashes is not None:
        if _hashes_equal(complex_hashes, solvent_hashes):
            checked.append("solvent-leg object hashes match — the SAME solvent leg is used")
        else:
            mismatches.append("solvent-leg object hashes differ — a DIFFERENT solvent leg was used, so the "
                              "shared-solvent cancellation is invalid")
    else:
        note_unverifiable("solvent-leg object hashes not provided — cannot cryptographically confirm the "
                          "SAME solvent leg is used across the cross-tag pair")

    compatible = (not mismatches) and (not critical_unverifiable)
    return {"compatible": compatible, "mismatches": mismatches, "checked": checked,
            "unverifiable": unverifiable}


def _hashes_equal(a, b):
    """Robust equality for the solvent-hash argument: accepts a plain str/hex digest, or a dict mapping
    filename→digest (order-independent). Anything else falls back to ==."""
    if isinstance(a, dict) and isinstance(b, dict):
        return {k: str(v) for k, v in a.items()} == {k: str(v) for k, v in b.items()}
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return list(map(str, a)) == list(map(str, b))
    return str(a).strip() == str(b).strip()


def _import_combine_legs():
    """Import nr4a3_abfe.combine_legs. nr4a3_abfe's top level pulls only json/os (numpy/pymbar are imported
    INSIDE its functions), so this is safe in the pymbar-free sandbox. Ensures this file's directory is on the
    path so it works both as a top-level import (conftest) and standalone."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from nr4a3_abfe import combine_legs
    return combine_legs


def ddg_direct_from_complex_diff(complex_dg_target, complex_dg_off, ssc_target, ssc_off, solvent_dg,
                                 tol=1e-6):
    """Compute the selectivity ΔΔG(target − off-target) TWO ways and assert they agree — proving the
    shared-solvent cancellation is algebraically correct for a cross-tag reduce.

    Both receptors share the SAME solvent leg (solvent_dg), which is the whole point of the cross-tag reduce.

    Route (a) — full ABFEs, then subtract (exactly what reduce-abfe-ci.yml does):
        combine_legs gives  ΔG_bind = solvent_dg − complex_dg − SSC   (nr4a3_abfe.combine_legs)
        ΔG_bind(target) = solvent_dg − complex_dg_target − ssc_target
        ΔG_bind(off)    = solvent_dg − complex_dg_off    − ssc_off
        ΔΔG = ΔG_bind(target) − ΔG_bind(off)

    Route (b) — directly from the complex-leg difference + non-cancelling corrections. Substituting and
    cancelling the SHARED solvent_dg term:
        ΔΔG = (solvent_dg − complex_dg_target − ssc_target) − (solvent_dg − complex_dg_off − ssc_off)
            =  −(complex_dg_target − complex_dg_off) − (ssc_target − ssc_off)
    The solvent_dg cancels exactly; only the complex-leg difference and the SSC difference survive (the SSC
    difference is a genuine non-cancelling correction — the two paralogues have different restraint geometries).

    Returns {ddg_via_full_abfe, ddg_direct_from_complex_diff, dg_bind_target, dg_bind_off, abs_diff, agree}.
    """
    combine_legs = _import_combine_legs()
    # Route (a): SEs are irrelevant to the ΔΔG mean, so pass 0.0 for the leg SEs.
    dg_bind_target, _ = combine_legs(complex_dg_target, 0.0, solvent_dg, 0.0, ssc_target)
    dg_bind_off, _ = combine_legs(complex_dg_off, 0.0, solvent_dg, 0.0, ssc_off)
    ddg_a = dg_bind_target - dg_bind_off
    # Route (b): direct, solvent cancelled.
    ddg_b = -(complex_dg_target - complex_dg_off) - (ssc_target - ssc_off)
    abs_diff = abs(ddg_a - ddg_b)
    agree = abs_diff <= tol
    return {"ddg_via_full_abfe": ddg_a, "ddg_direct_from_complex_diff": ddg_b,
            "dg_bind_target": dg_bind_target, "dg_bind_off": dg_bind_off,
            "abs_diff": abs_diff, "agree": agree}
