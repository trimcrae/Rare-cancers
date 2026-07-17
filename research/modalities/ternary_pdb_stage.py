#!/usr/bin/env python3
"""Stage ternary-FEP leg inputs from a CRYSTAL ternary structure (valB_mini: PROTAC 2 / SMARCA2-VHL, PDB 6HAX).

The ternary engine (nr4a3_ternary_fep._build_components) mounts, per leg:
  <out>/<leg_id>/complex.pdb  — the assembled E3 machinery [+ target] protein
  <out>/<leg_id>/ligands.sdf  — the two posed PROTAC endpoints (calib_hi, calib_lo) — SAME crystal pose written
                                twice; the engine re-imposes each endpoint's bond orders/stereo from SMILES.
Environments (nr4a3_ternary_fep._environment_of):
  ternary_smarca2 : VHL + ElonginB + ElonginC + SMARCA2 (bromodomain)   [PROTAC bridges VHL<->SMARCA2]
  binary_vhl      : VHL + ElonginB + ElonginC        (DROP the SMARCA2 chain)
  solvent         : ligands.sdf only (no protein)

Chain roles are resolved from RCSB (entity -> UniProt -> auth chain), never guessed:
  VHL=P40337, ElonginB=Q15370, ElonginC=Q15369, SMARCA2=P51531.
The bound PROTAC pose comes from the RCSB ModelServer as SDF (crystal coordinates, CCD bond orders).

HONESTY: every atom is from 6HAX (RCSB); nothing is fabricated. If a required chain role or the ligand cannot be
resolved, the stager reports exactly what is missing and stages nothing for that leg.

Runs on a GCP VM or a CI runner (unrestricted internet). Deps: gemmi + rdkit (+ stdlib urllib).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

import nr4a3_ternary_fep as eng

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"
RCSB_POLY = "https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/{eid}"
RCSB_CIF = "https://files.rcsb.org/download/{pdb}.cif"
RCSB_LIG_SDF = ("https://models.rcsb.org/v1/{pdb}/ligand?auth_comp_id={ccd}&encoding=sdf&copy_all_categories=false")

UNIPROT_ROLE = {"P40337": "VHL", "Q15370": "ElonginB", "Q15369": "ElonginC", "P51531": "SMARCA2"}
ROLE_CHAINS_FOR_ENV = {  # which protein ROLES each environment keeps
    "binary": ["VHL", "ElonginB", "ElonginC"],
    "ternary": ["VHL", "ElonginB", "ElonginC", "SMARCA2"],
}


def _get(url: str, as_json=True, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-ci",
                                               "Accept": "application/json" if as_json else "*/*"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    if binary:
        return raw
    txt = raw.decode("utf-8", "replace")
    return json.loads(txt) if as_json else txt


def role_to_chains(pdb: str) -> dict:
    """{role: [auth_chain_ids]} resolved from RCSB entity->UniProt->auth chains (no guessing)."""
    entry = _get(RCSB_ENTRY.format(pdb=pdb))
    eids = (entry.get("rcsb_entry_container_identifiers", {}) or {}).get("polymer_entity_ids") or []
    out: dict = {}
    for eid in eids:
        pe = _get(RCSB_POLY.format(pdb=pdb, eid=eid))
        cids = pe.get("rcsb_polymer_entity_container_identifiers", {}) or {}
        auth_chains = cids.get("auth_asym_ids") or cids.get("asym_ids") or []
        accs = [r.get("database_accession") for r in (cids.get("reference_sequence_identifiers") or [])
                if r.get("database_name") == "UniProt"]
        for acc in accs:
            role = UNIPROT_ROLE.get(acc)
            if role:
                out.setdefault(role, [])
                out[role].extend(c for c in auth_chains if c not in out[role])
    return out


def _ligand_ccd(pdb: str) -> str:
    """The PROTAC CCD in the entry (largest non-ion nonpolymer) — reuses the freeze module's resolver."""
    import ternary_calib_freeze as tcf
    lig = tcf._degrader_ligand(pdb)
    if not lig:
        raise SystemExit(f"[stage] no PROTAC-scale ligand resolved for {pdb}")
    return lig["ccd"]


def _write_complex_pdb(cif_text: str, keep_chains: list, out_pdb: str):
    """Extract the kept protein chains (polymer only, drop waters/ligands/ions) from the CIF -> PDB via gemmi."""
    import gemmi

    doc = gemmi.cif.read_string(cif_text)
    st = gemmi.make_structure_from_block(doc.sole_block())
    st.setup_entities()
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_ligands_and_waters()   # keep only polymer (protein) residues
    keep = set(keep_chains)
    model = st[0]
    for name in [ch.name for ch in model]:
        if name not in keep:
            model.remove_chain(name)
    st.remove_empty_chains()
    n_res = sum(len(ch) for ch in st[0])
    if n_res == 0:
        raise SystemExit(f"[stage] no residues left after chain surgery (keep={keep_chains}) — check role mapping")
    os.makedirs(os.path.dirname(out_pdb), exist_ok=True)
    st.write_pdb(out_pdb)


def _write_ligands_sdf(pdb: str, ccd: str, endpoint_names, out_sdf: str):
    """Fetch the bound PROTAC pose (crystal coords) from the RCSB ModelServer as SDF and write it once per
    endpoint name (calib_hi / calib_lo) — the engine re-imposes each endpoint's stereo from its SMILES."""
    import io

    from rdkit import Chem

    sdf_text = _get(RCSB_LIG_SDF.format(pdb=pdb, ccd=urllib.parse.quote(ccd)), as_json=False)
    supplier = Chem.ForwardSDMolSupplier(io.BytesIO(sdf_text.encode()), sanitize=False, removeHs=False)
    mol = next((m for m in supplier if m is not None), None)
    if mol is None:
        raise SystemExit(f"[stage] ModelServer returned no usable ligand SDF for {pdb}/{ccd}")
    os.makedirs(os.path.dirname(out_sdf), exist_ok=True)
    w = Chem.SDWriter(out_sdf)
    for nm in endpoint_names:
        mol.SetProp("_Name", nm)
        w.write(mol)
    w.close()


def stage_leg(leg_id: str, template_pdb: str, out_root: str) -> dict:
    """Stage one leg's complex.pdb (+ ligands.sdf) from the crystal template. Returns a manifest dict."""
    env = eng._environment_of(leg_id)
    leg, _ = eng.leg_spec(leg_id)
    m = eng.prep._morph_endpoints(leg)
    endpoint_names = [m["endpoint_a"], m["endpoint_b"]]
    leg_dir = os.path.join(out_root, leg_id)
    os.makedirs(leg_dir, exist_ok=True)

    ccd = _ligand_ccd(template_pdb)
    _write_ligands_sdf(template_pdb, ccd, endpoint_names, os.path.join(leg_dir, "ligands.sdf"))

    made_pdb = False
    chains_used: list = []
    if env in ("binary", "ternary"):
        roles = ROLE_CHAINS_FOR_ENV[env]
        r2c = role_to_chains(template_pdb)
        missing = [role for role in roles if not r2c.get(role)]
        if missing:
            raise SystemExit(f"[stage] {template_pdb}: could not resolve chains for roles {missing} "
                             f"(resolved: { {k: v for k, v in r2c.items()} }). Stage nothing.")
        chains_used = [c for role in roles for c in r2c[role]]
        cif = _get(RCSB_CIF.format(pdb=template_pdb), as_json=False)
        _write_complex_pdb(cif, chains_used, os.path.join(leg_dir, "complex.pdb"))
        made_pdb = True

    return {"leg_id": leg_id, "environment": env, "template_pdb": template_pdb, "ligand_ccd": ccd,
            "endpoint_names": endpoint_names, "complex_chains": chains_used, "wrote_complex_pdb": made_pdb,
            "wrote_ligands_sdf": True, "out_dir": leg_dir}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Stage ternary-FEP leg inputs from a crystal ternary structure.")
    ap.add_argument("--leg-id", required=True, help="e.g. calib_hi_to_lo__ternary_vhl | ..._binary_vhl | ...__solvent")
    ap.add_argument("--template-pdb", default="6HAX")
    ap.add_argument("--out", default=os.environ.get("STAGE_OUT", "/tmp/ternary_in"))
    args = ap.parse_args(argv)
    man = stage_leg(args.leg_id, args.template_pdb, args.out)
    print(json.dumps(man, indent=2), flush=True)
    # sanity: files exist + non-empty
    for f in (["ligands.sdf"] + (["complex.pdb"] if man["wrote_complex_pdb"] else [])):
        p = os.path.join(man["out_dir"], f)
        sz = os.path.getsize(p) if os.path.exists(p) else 0
        print(f"[stage]   {f}: {sz} B", flush=True)
        if sz == 0:
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
