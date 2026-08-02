#!/usr/bin/env python3
"""Is a SMARCA4 ternary frame a safe stand-in for a SMARCA2 one? — the assumption valB's SMARCA2 arm rests on.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ THE QUESTION, AND WHY IT IS ASKED CRYSTAL-vs-CRYSTAL RATHER THAN BY RE-STAGING
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
`structural-provenance-census.json` flagged one lane as **checkable but never checked**: valB's SMARCA2 arm
is not a crystal and not a co-fold but a THIRD thing — SMARCA2 threaded into the **3.73 Å 8G1Q SMARCA4**
ternary frame and relaxed (`smarca2_model.py`). Its ternary INTERFACE is therefore inherited from a SMARCA4
complex rather than observed on a SMARCA2 one. Whether that transfer is safe is an assumption nobody has
measured.

The obvious way to test it — regenerate the staged arm and score it — introduces the staging pipeline as a
variable, and the staging pipeline is not what is in question. **The assumption itself is measurable
directly, from two deposited structures:**

    9DTY = SMARCA2 + PRT3789 + VCB          9DTX = SMARCA4 + PRT3789 + VCB

**The SAME degrader on BOTH paralogues.** So the difference between their target↔VHL interfaces isolates the
paralogue term exactly — with the ligand held fixed, which is the one thing every other available comparison
fails to do (8G1Q carries Wurz compound 1, 6HAX carries PROTAC 2, so those conflate ligand with paralogue).
That difference IS the error a SMARCA4→SMARCA2 frame transfer inherits, and it needs no staging, no model
and no GPU — two RCSB downloads.

★ IT ALSO ANSWERS A SECOND QUESTION FOR FREE, and this one is not incidental. The gap between 9DTY's and
9DTX's ternary interfaces is **the structural difference the entire selectivity programme is trying to
detect**. If two crystals of the same degrader on the two paralogues differ by ~nothing at the interface,
that is a statement about how much signal exists to find — measured, on deposited structures, rather than
assumed. Reported as an observation; it gates nothing and re-scores nothing.

⛔ WHAT THIS DOES NOT DO. It does not re-score any valB leg, move any ΔΔG, or amend the calibration prereg.
valB's own coordinates come straight from the crystal (`ternary_pdb_stage`: *"every atom is from 6HAX
(RCSB); nothing is fabricated"*) and its wrong-sign result stands as measured. This measures ONE inherited
assumption in ONE arm, and nothing else.

⚠ HONEST LIMITS, STATED BEFORE THE NUMBER EXISTS:
  * 9DTY is 3.19 Å and 9DTX is 2.11 Å; some of any measured difference is resolution, not biology.
  * valB's arm is built on **8G1Q** (3.73 Å), not on 9DTY, so this bounds the transfer error using the
    cleanest available pair rather than measuring valB's exact frame. It is an estimate of the assumption's
    size, not an audit of that specific file.
  * A SMALL difference does not certify the transfer — it removes the largest reason to doubt it. A LARGE
    difference does not invalidate valB, whose endpoint-state error was localised by the closure triangle.

Both instruments are reused as-is: `selcal_cofold_validate` (imported) and the canonical DockQ CLI via
`selcal_dockq_crosscheck` (imported). Nothing about the measurement is re-implemented here — this module
only chooses the two structures and states what their comparison means.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "valb-frame-transfer-check.json")

#: The one matched-ligand paralogue pair in the PDB for this chemotype. `selcal_panel.REFERENCE` is the one
#: home of these ids; they are read from it rather than typed, so a change there cannot leave this behind.
def pair_from_panel():
    import selcal_panel as P
    dep = P.REFERENCE["deposited_ternaries"]
    return {"smarca2_pdb": dep["SMARCA2"], "smarca4_pdb": dep["SMARCA4"],
            "ligand_ccd": P.REFERENCE.get("ligand_ccd"), "ligand": P.REFERENCE.get("ligand")}

#: ⚠ SMARCA2 and SMARCA4 bromodomains are ~80 % identical, which sits AT `selcal_cofold_validate`'s default
#: chain-matching floor. That floor exists to make a WRONG match impossible when comparing a model to its own
#: crystal; here the two structures are deliberately DIFFERENT proteins, so the floor has to be lowered or
#: the comparison refuses by construction. Lowered explicitly, named here, and only for this cross-paralogue
#: comparison — never for a model-vs-its-own-crystal check.
CROSS_PARALOGUE_MIN_IDENTITY = 0.55


def check(native_dir, min_identity=CROSS_PARALOGUE_MIN_IDENTITY):
    """Score the SMARCA2 ternary against the SMARCA4 ternary at the target↔VHL interface, both instruments."""
    import selcal_cofold_validate as V
    import selcal_dockq_crosscheck as X

    ids = pair_from_panel()
    a = os.path.join(native_dir, "%s.cif" % ids["smarca2_pdb"].upper())   # "model" = SMARCA2 ternary
    b = os.path.join(native_dir, "%s.cif" % ids["smarca4_pdb"].upper())   # "native" = SMARCA4 ternary

    out = {
        "_what": "How different is a SMARCA2 ternary from a SMARCA4 ternary carrying the SAME degrader? "
                 "This is the error a SMARCA4->SMARCA2 frame transfer inherits — the assumption valB's "
                 "SMARCA2 arm rests on — and it is also the structural difference the selectivity programme "
                 "is trying to detect.",
        "_licenses": "NOTHING. It re-scores no valB leg, moves no ddG, amends no prereg and gates no launch. "
                     "valB's own coordinates come straight from the crystal and its wrong-sign result stands.",
        "_limits": [
            "9DTY is 3.19 A and 9DTX is 2.11 A — some of any difference is resolution, not biology.",
            "valB's arm is built on 8G1Q (3.73 A), not on 9DTY, so this BOUNDS the transfer error using the "
            "cleanest available pair rather than auditing that specific file.",
            "A small difference does not certify the transfer; it removes the largest reason to doubt it. A "
            "large one does not invalidate valB, whose miss was localised to an endpoint-state error.",
        ],
        "pair": ids,
        "same_ligand_on_both_arms": True,
        "_why_this_pair": "the only matched-ligand paralogue pair available: both carry PRT3789, so the "
                          "paralogue term is isolated. 8G1Q vs 6HAX would conflate ligand with paralogue.",
        "cross_paralogue_min_identity": min_identity,
        "instruments": {},
    }

    if not (os.path.exists(a) and os.path.exists(b)):
        out["graded"] = False
        out["why"] = "missing structure(s): %s" % [p for p in (a, b) if not os.path.exists(p)]
        return out

    # --- instrument 1: the repo's interface-RMSD/fnat validator, on E1's scale -----------------------------
    # Chain roles come from the COMMITTED selcal chain map, so this module adds no chain-assignment logic of
    # its own and needs no network — and both structures stay on the same copy convention as every other
    # measurement in this lane (9DTY holds ~10 copies; picking a different one here would make the numbers
    # incomparable with the co-fold results for no gain).
    roles, role_err = roles_from_selcal_artifact(ids["smarca2_pdb"])
    native_roles, native_err = roles_from_selcal_artifact(ids["smarca4_pdb"])
    out["smarca2_chain_roles"] = roles
    out["smarca4_chain_roles"] = native_roles
    out["smarca2_chain_roles_error"] = role_err or native_err
    if role_err or native_err:
        out["graded"] = False
        out["why"] = role_err or native_err
        return out

    saved = V.MIN_CHAIN_IDENTITY
    try:
        V.MIN_CHAIN_IDENTITY = min_identity
        rec = V.validate_one(a, b, target_model_chain=roles["target"], e3_model_chains=roles["e3"])
    finally:
        V.MIN_CHAIN_IDENTITY = saved
    out["instruments"]["interface_rmsd_fnat"] = {
        "graded": rec.get("graded"),
        "why": rec.get("why"),
        "interface_rmsd_A": rec.get("interface_rmsd_to_crystal_A"),
        "fnat": (rec.get("fnat") or {}).get("fnat"),
        "n_native_contacts": (rec.get("fnat") or {}).get("n_native_contacts"),
        "chain_map": {k: v.get("native_chain") for k, v in
                      ((rec.get("chain_map") or {}).get("matched") or {}).items()},
    }

    # --- instrument 2: canonical DockQ, target<->VHL interface selected BY ROLE ----------------------------
    matched = ((rec.get("chain_map") or {}).get("matched")) or {}
    mapping, map_err = X.mapping_from_first_instrument(rec)
    tgt_native = (matched.get(roles["target"]) or {}).get("native_chain")
    vhl_native = (matched.get(roles["e3"][0]) or {}).get("native_chain")
    doc, err = X.run_dockq(a, b, mapping=mapping) if not map_err else (None, map_err)
    if err or not (tgt_native and vhl_native):
        out["instruments"]["dockq"] = {"error": err or "roles did not resolve to native chains"}
    else:
        best, iface_err = X.target_e3_interface(doc, tgt_native, vhl_native)
        out["instruments"]["dockq"] = ({"error": iface_err} if iface_err else
                                       {"interface": best["interface"], "DockQ": best["DockQ"],
                                        "quality_class": X.quality_class(best["DockQ"]),
                                        "fnat": best["fnat"], "iRMSD_A": best["iRMS"]})
        out["instruments"]["dockq_other_interfaces_context_only"] = X.other_interfaces(doc, tgt_native,
                                                                                       vhl_native)
    out["graded"] = bool(rec.get("graded"))
    return out


def roles_from_selcal_artifact(pdb_id, first_json=None):
    """(roles, error) — which chain of `pdb_id` is the degradation target and which are the VCB subunits.

    READ FROM A COMMITTED MEASUREMENT, not re-derived and certainly not typed: `selcal-cofold-vs-crystal.json`
    already records, per co-fold, the sequence-derived map from the panel's model chains (target = A, VHL/
    EloB/EloC = E/F/G — `selcal_stage`'s frozen input specification) onto this crystal's author chains. Taking
    the roles from there means this module introduces no new chain-assignment logic at all, and it needs no
    network.

    Reusing that map also keeps the two structures on the SAME copy convention as every other measurement in
    this lane — 9DTY holds ~10 copies, and picking a different one here would make the numbers
    incomparable with the co-fold results for no gain."""
    import selcal_stage as S
    first_json = first_json or os.path.join(HERE, "selcal-cofold-vs-crystal.json")
    if not os.path.exists(first_json):
        return None, "%s is absent — roles come from that committed map, and it has not been produced" % \
            os.path.basename(first_json)
    try:
        doc = json.load(open(first_json))
    except Exception as e:                                  # noqa: BLE001
        return None, "could not read %s: %s" % (os.path.basename(first_json), e)
    for rec in doc.get("records", []):
        if not rec.get("graded") or (rec.get("native_pdb_id") or "").upper() != pdb_id.upper():
            continue
        matched = ((rec.get("chain_map") or {}).get("matched")) or {}
        tgt_model = rec.get("target_model_chain") or S.CHAIN_TARGET
        e3_model = rec.get("e3_model_chains") or [S.CHAIN_VHL, S.CHAIN_ELOB, S.CHAIN_ELOC]
        if tgt_model not in matched or any(c not in matched for c in e3_model):
            continue
        return {"target": matched[tgt_model]["native_chain"],
                "e3": [matched[c]["native_chain"] for c in e3_model],
                "_derived": "read from selcal-cofold-vs-crystal.json's sequence-derived chain map; this "
                            "module adds no chain-assignment logic of its own",
                "_model_roles": {"target": tgt_model, "e3": list(e3_model)}}, None
    return None, ("no graded record for %s in %s — roles cannot be assigned, and guessing them is the defect "
                  "that once scored Elongin C as the degradation target" % (pdb_id, os.path.basename(first_json)))


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="SMARCA4->SMARCA2 ternary frame-transfer check ($0 CPU).")
    ap.add_argument("--native-dir", required=True)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)

    if args.fetch:
        import selcal_cofold_validate as V
        for pdb in (pair_from_panel()["smarca2_pdb"], pair_from_panel()["smarca4_pdb"]):
            info = V.fetch_rcsb_cif(pdb, args.native_dir)
            print("[valb-frame] fetched %s (%d bytes)" % (info["url"], info["bytes"]), flush=True)

    res = check(args.native_dir)
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("[valb-frame] wrote %s" % args.out, flush=True)
    print(json.dumps(res.get("instruments", {}), indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
