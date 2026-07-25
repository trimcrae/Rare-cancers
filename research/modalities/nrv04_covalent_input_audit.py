#!/usr/bin/env python3
"""
NR-V04 covalent panel — EXHAUSTIVE input-admissibility audit over EVERY co-fold in the bucket ($0 CPU).

WHY THIS EXISTS, precisely. Prereg AMENDMENT 1 (2026-07-25) adds binding criterion **A1**: a leg declared
covalent must stage its electrophilic carbon within `MAX_COVALENT_TETHER_A` (8.0 A) of the TARGET-CHAIN Cys
S-gamma, against a ~1.8 A C-S bond. It records A1 as failing at 8.99 A (`cov_nr4a1`) and 16.39 A
(`warhead_only`) and concludes "Boltz does not seat celastrol against an NR4A1 cysteine in **any** co-fold
currently in the bucket".

That conclusion rests on `nrv04_prespend_check._pull_model`, which selects

    sorted([k for k in keys if k.endswith("_model_0.cif")])[0]

i.e. **ONE** model per system: model_0 of the lexicographically-first seed. The co-folds were generated over a
seed ensemble (`--seeds 1,2,3`, and `--diffusion_samples` can emit several poses per seed), so "any co-fold in
the bucket" was never measured -- one member of each ensemble was. Boltz pose placement varies substantially
across diffusion seeds; a claim of the form "no member of the ensemble does X" cannot be supported by a sample
of size one. This script measures A1 on **every** model of **every** system of **every** co-fold prefix, so the
claim is settled by enumeration instead of by extrapolation.

It also measures three things the pre-spend check does not, each of which can change the verdict:

  (a) **A1 AT THE FROZEN SITE, not merely at the nearest cysteine.** `_reactive_cys_by_geometry` returns the
      *nearest* target-chain Sg. The panel's frozen covalent site is NR4A1 **Cys551** (prereg S3
      `TARGET_COV_RESNUM = 551`, confirmed a cysteine by Leg 0). Those are different questions: a model can pass
      A1 on some other cysteine while the frozen site is 25 A away, and it would then be admissible under the
      letter of A1 while modelling a different adduct than the one preregistered. Both numbers are reported for
      every model, together with the LBD-index <-> full-length P22736 mapping that connects them.
  (b) **Where the celastrol warhead actually is.** Contacts of the celastrol moiety with the target chain vs
      with the E3 chains, and the same for the VH032 recruiter moiety with VHL. A model whose warhead is not on
      the target at all fails for a reason no restraint can repair, and is distinguishable here from one whose
      warhead is in the pocket but pointing the wrong way.
  (c) **Which co-fold prefix and seed each model came from**, so a claim about "the bucket" is an enumeration
      rather than an extrapolation, and a contaminated prefix is reported on rather than aborted upon.

  *(Boltz per-model confidence is deliberately NOT read here. It would matter for choosing between models that
  pass; every model fails at the frozen site by 20+ A, so a confidence tie-break would be decoration on a
  decision already made. Add it if a model ever passes.)*

Chemistry note: the electrophile is located by the single frozen definition in `nrv04_ligands`, and the ligand
pose is recovered by the same template kernel `nrv04_covalent_assemble` uses, so this audit measures exactly
what the driver would build -- not a re-derivation that could differ.

$0: read-only S3 + CPU. Emits `nrv04-covalent-input-audit.json`. Exit code is always 0 -- a diagnostic that
reports a verdict, never one that hides it.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Frozen from the panel; imported (not retyped) so the audit cannot drift from what runs.
from nrv04_covalent_assemble import (  # noqa: E402
    CONTAMINANT_CHAIN_RESIDUES,
    E3_CHAIN_RESIDUES,
    NR4A_LBD_RESIDUES,
    ligand_mol_from_coords,
)
from nrv04_covalent_panel import CELASTROL_ELECTROPHILE_ATOM, TARGET_COV_RESNUM  # noqa: E402
from nrv04_ligands import LIGANDS, electrophile_atom_index  # noqa: E402

# `nrv04_prespend_check.LIGAND_TO_SYSTEM` inverted: co-fold system subdir -> the ligand co-folded into it.
SYSTEM_TO_LIGAND = {"nr4a1": "nrv04", "neg_inactive": "nrv04_epimer", "neg_celastrol": "celastrol",
                    # nrv04_celastrol_site_probe.py systems (the C551 root-cause probe / steered re-fold)
                    "binary_free": "celastrol", "binary_pocket": "celastrol", "ternary_pocket": "nrv04"}
# The A1 limit, read from the driver so there is one definition of the bar.
try:
    from nrv04_covalent_md import MAX_COVALENT_TETHER_A  # noqa: E402
except Exception:  # noqa: BLE001 -- driver imports openmm lazily, but keep the audit runnable regardless
    MAX_COVALENT_TETHER_A = float(os.environ.get("NRV04_MAX_TETHER_A", "8.0"))

# UniProt P22736 (human NR4A1) full length. The frozen LBD construct is its C-terminal NR4A_LBD_RESIDUES
# residues (nr4a3_ternary.lbd_seq: `full[-254:]`), so co-fold residue i (1-based) is full-length residue
# i + (NR4A1_FULL_LEN - 254). Verified against the fetched sequence at run time when the network allows; the
# constant is only the fallback and any mismatch is recorded rather than silently used.
NR4A1_FULL_LEN_EXPECTED = 598
NR4A1_ACC = "P22736"

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


# ---------------------------------------------------------------------------------------------------------
# S3 enumeration
# ---------------------------------------------------------------------------------------------------------

def list_keys(s3, bucket, prefix):
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        keys += [(o["Key"], o["Size"], o["LastModified"].isoformat()) for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    return keys


def discover_cofold_prefixes(s3, bucket):
    """Every top-level prefix that looks like a co-fold output (contains a */*_model_*.cif). Enumerated rather
    than hardcoded so a prefix nobody remembered cannot be the one that held an admissible model."""
    out = set()
    r = s3.list_objects_v2(Bucket=bucket, Delimiter="/")
    tops = [c["Prefix"] for c in r.get("CommonPrefixes", [])]
    while r.get("IsTruncated"):
        r = s3.list_objects_v2(Bucket=bucket, Delimiter="/", ContinuationToken=r["NextContinuationToken"])
        tops += [c["Prefix"] for c in r.get("CommonPrefixes", [])]
    for t in tops:
        # cheap probe: one page is enough to see whether any .cif lives under here
        rr = s3.list_objects_v2(Bucket=bucket, Prefix=t, MaxKeys=400)
        if any(o["Key"].endswith(".cif") for o in rr.get("Contents", [])):
            out.add(t.rstrip("/"))
    return sorted(out)


_MODEL_RE = re.compile(r"_model_(\d+)\.cif$")


def index_models(keys, prefix):
    """Group every model CIF under a prefix into {system: [ {key, seed, model, size, mtime}, ... ]}."""
    systems = {}
    for key, size, mtime in keys:
        m = _MODEL_RE.search(key)
        if not m:
            continue
        rel = key[len(prefix.rstrip("/")) + 1:]
        parts = rel.split("/")
        system = parts[0] if parts else "?"
        seed = next((p for p in parts if p.startswith("seed_")), "")
        systems.setdefault(system, []).append(
            {"key": key, "system": system, "seed": seed, "model": int(m.group(1)), "size": size, "mtime": mtime})
    for v in systems.values():
        v.sort(key=lambda d: (d["seed"], d["model"]))
    return systems


# ---------------------------------------------------------------------------------------------------------
# per-model measurement
# ---------------------------------------------------------------------------------------------------------

def read_cif(path):
    """Return (protein_chains, ligand). protein_chains = {chain: [(resid, resname, {atomname: xyz}), ...]};
    ligand = {"chain": id, "elements": [...], "coords": [...]}. Uses the same polymer test as the assembler.

    NOTE the `UNK` trap recorded in nrv04-covalent-panel-recovery-2026-07-25.md S4: `UNK` IS a tabulated amino
    acid, so an `is_amino_acid()` test alone counts a `UNK`-named ligand as a 1-residue protein. The assembler
    dodges it because it iterates non-polymer residues for the ligand and lets gemmi's `remove_ligands_and_waters`
    handle the protein side. Here we require BOTH a polymer classification AND a recognised 3-letter code, which
    excludes UNK explicitly."""
    import gemmi
    st = gemmi.read_structure(path)
    chains, lig = {}, {"chain": None, "elements": [], "coords": []}
    for chain in st[0]:
        for res in chain:
            info = gemmi.find_tabulated_residue(res.name)
            is_poly = bool(info) and (info.is_amino_acid() or info.is_nucleic_acid()) and res.name in THREE2ONE
            if res.name in ("HOH", "WAT"):
                continue
            if is_poly:
                atoms = {a.name: (a.pos.x, a.pos.y, a.pos.z) for a in res if a.element.name != "H"}
                chains.setdefault(chain.name, []).append((res.seqid.num, res.name, atoms))
            else:
                lig["chain"] = chain.name
                for a in res:
                    if a.element.name != "H":
                        lig["elements"].append(a.element.name)
                        lig["coords"].append((a.pos.x, a.pos.y, a.pos.z))
    return chains, lig


def identify_chains_from_census(chains):
    """Same identification rule as nrv04_covalent_assemble.identify_chains, but on the parsed CIF and
    returning a STRUCTURED verdict instead of raising -- the audit must be able to report on a contaminated
    co-fold, not abort on it."""
    census = [{"chain": c, "residues": len(v)} for c, v in chains.items()]
    bad = [c for c in census if c["residues"] in CONTAMINANT_CHAIN_RESIDUES]
    e3 = [c["chain"] for c in census if c["residues"] in E3_CHAIN_RESIDUES]
    rest = [c for c in census if c["chain"] not in e3]
    out = {"census": census, "e3_chains": sorted(e3),
           "e3_roles": {c["chain"]: E3_CHAIN_RESIDUES[c["residues"]] for c in census if c["chain"] in e3},
           "contaminant": [{"chain": c["chain"], "residues": c["residues"],
                            "what": CONTAMINANT_CHAIN_RESIDUES[c["residues"]]} for c in bad]}
    if len(rest) == 1 and rest[0]["residues"] == NR4A_LBD_RESIDUES:
        out["target_chain"] = rest[0]["chain"]
        out["admissible_assembly"] = not bad
    else:
        out["target_chain"] = None
        out["admissible_assembly"] = False
        out["why_no_target"] = f"leftover chains {[c['chain'] for c in rest]} (need exactly 1 x {NR4A_LBD_RESIDUES})"
    return out


def chain_sequence(chains, cid):
    return "".join(THREE2ONE.get(rn, "X") for _, rn, _ in sorted(chains[cid], key=lambda t: t[0]))


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def warhead_fragment_indices(lig_mol, c6_idx):
    """Heavy-atom indices of the CELASTROL (warhead) moiety of a ligand, defined structurally rather than by
    substructure match.

    A naive `GetSubstructMatch(celastrol)` MISSES inside NR-V04: celastrol's C(=O)OH is consumed into the
    linker amide, so free celastrol is not a substructure of the conjugate. Instead: cut every amide C-N bond
    (which is exactly where the celastroyl, the PEG linker, the tBu-Gly and the Hyp-benzylamide are joined) and
    return the fragment carrying the electrophilic carbon. For free celastrol there is no amide, so the whole
    molecule is returned -- the same rule, no special case."""
    from rdkit import Chem
    patt = Chem.MolFromSmarts("[CX3](=O)[NX3]")
    bonds = set()
    for a_c, _a_o, a_n in lig_mol.GetSubstructMatches(patt):
        b = lig_mol.GetBondBetweenAtoms(a_c, a_n)
        if b is not None:
            bonds.add(b.GetIdx())
    if not bonds:
        return list(range(lig_mol.GetNumAtoms()))
    frag_mol = Chem.FragmentOnBonds(lig_mol, sorted(bonds), addDummies=False)
    for frag in Chem.GetMolFrags(frag_mol, asMols=False):
        if c6_idx in frag:
            return list(frag)
    return list(range(lig_mol.GetNumAtoms()))


def contacts(coords_a, coords_b, cutoff=4.5):
    n = 0
    for a in coords_a:
        for b in coords_b:
            if _dist(a, b) <= cutoff:
                n += 1
    return n


def measure_model(path, ligand_name, lbd_offset):
    """Every A1-relevant quantity for one co-fold model."""
    from rdkit import Chem
    out = {"ligand": ligand_name}
    chains, lig = read_cif(path)
    ident = identify_chains_from_census(chains)
    out.update({k: ident[k] for k in ("census", "e3_chains", "e3_roles", "contaminant", "target_chain",
                                      "admissible_assembly")})
    if ident.get("why_no_target"):
        out["why_no_target"] = ident["why_no_target"]
    if not lig["elements"]:
        out["error"] = "no non-polymer ligand atoms in the CIF"
        return out
    out["ligand_heavy_atoms"] = len(lig["elements"])

    # posed, bond-order-correct ligand via the SAME kernel the assembler uses
    try:
        mol = ligand_mol_from_coords(lig["elements"], lig["coords"], LIGANDS[ligand_name])
    except Exception as e:  # noqa: BLE001
        out["error"] = f"ligand pose reconstruction failed: {type(e).__name__}: {e}"
        return out
    heavy = Chem.RemoveHs(mol)
    try:
        c6_idx, _ = electrophile_atom_index(heavy)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"electrophile location failed: {type(e).__name__}: {e}"
        return out
    conf = heavy.GetConformer()
    ep = tuple(conf.GetAtomPosition(c6_idx))
    out["electrophile_atom_idx"] = int(c6_idx)

    tgt = ident.get("target_chain")
    if tgt is None:
        out["a1"] = {"verdict": "UNEVALUABLE", "why": "no identified degradation-target chain"}
        return out

    # --- target-chain cysteine inventory, with the LBD-index <-> full-length mapping -----------------------
    seq = chain_sequence(chains, tgt)
    out["target_len"] = len(seq)
    cys = []
    for resid, resname, atoms in sorted(chains[tgt], key=lambda t: t[0]):
        if resname != "CYS" or "SG" not in atoms:
            continue
        cys.append({"lbd_resid": resid, "fulllen_resid": resid + lbd_offset if lbd_offset is not None else None,
                    "sg_dist_A": round(_dist(ep, atoms["SG"]), 2)})
    out["target_cys"] = cys
    out["n_target_cys"] = len(cys)
    if not cys:
        out["a1"] = {"verdict": "UNEVALUABLE", "why": "target chain carries no cysteine"}
        return out

    nearest = min(cys, key=lambda c: c["sg_dist_A"])
    frozen = next((c for c in cys if c["fulllen_resid"] == TARGET_COV_RESNUM), None)
    out["a1"] = {
        "limit_A": MAX_COVALENT_TETHER_A,
        "nearest_target_cys": nearest,
        "nearest_passes": nearest["sg_dist_A"] <= MAX_COVALENT_TETHER_A,
        "frozen_site": {"fulllen_resid": TARGET_COV_RESNUM,
                        "lbd_resid": (TARGET_COV_RESNUM - lbd_offset) if lbd_offset is not None else None,
                        "found": frozen is not None,
                        "sg_dist_A": frozen["sg_dist_A"] if frozen else None},
        "frozen_site_passes": bool(frozen and frozen["sg_dist_A"] <= MAX_COVALENT_TETHER_A),
    }
    out["a1"]["verdict"] = ("PASS" if out["a1"]["frozen_site_passes"] else
                            "PASS_WRONG_CYS" if out["a1"]["nearest_passes"] else "FAIL")

    # --- where is the warhead, and where is the recruiter? -------------------------------------------------
    lig_xyz = [tuple(conf.GetAtomPosition(i)) for i in range(heavy.GetNumAtoms())]
    cel_idx = warhead_fragment_indices(heavy, c6_idx)
    rec_idx = [i for i in range(heavy.GetNumAtoms()) if i not in set(cel_idx)]
    tgt_xyz = [xyz for _, _, atoms in chains[tgt] for xyz in atoms.values()]
    e3_xyz, vhl_xyz = [], []
    for c in ident["e3_chains"]:
        xs = [xyz for _, _, atoms in chains[c] for xyz in atoms.values()]
        e3_xyz += xs
        if ident["e3_roles"].get(c) == "VHL":
            vhl_xyz = xs
    cel_xyz = [lig_xyz[i] for i in cel_idx]
    out["warhead"] = {
        "celastrol_heavy_atoms": len(cel_idx),
        "contacts_target_4.5A": contacts(cel_xyz, tgt_xyz),
        "contacts_e3_4.5A": contacts(cel_xyz, e3_xyz),
        "min_dist_target_A": round(min((_dist(a, b) for a in cel_xyz for b in tgt_xyz), default=-1), 2),
    }
    if rec_idx:
        rec_xyz = [lig_xyz[i] for i in rec_idx]
        out["recruiter"] = {
            "heavy_atoms": len(rec_idx),
            "contacts_vhl_4.5A": contacts(rec_xyz, vhl_xyz) if vhl_xyz else None,
            "min_dist_vhl_A": round(min((_dist(a, b) for a in rec_xyz for b in vhl_xyz), default=-1), 2)
            if vhl_xyz else None,
        }
    return out


# ---------------------------------------------------------------------------------------------------------

def resolve_lbd_offset():
    """full-length residue number = co-fold residue number + offset, for the frozen `full[-254:]` construct.
    Fetched from UniProt when the network allows (CI runner); falls back to the recorded constant and SAYS so."""
    import urllib.request
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{NR4A1_ACC}.fasta"
        with urllib.request.urlopen(url, timeout=60) as r:
            fa = r.read().decode()
        seq = "".join(l.strip() for l in fa.splitlines() if not l.startswith(">"))
        if seq:
            return len(seq) - NR4A_LBD_RESIDUES, {"source": "uniprot", "full_len": len(seq),
                                                  "residue_551": seq[550] if len(seq) >= 551 else None}
    except Exception as e:  # noqa: BLE001
        return (NR4A1_FULL_LEN_EXPECTED - NR4A_LBD_RESIDUES,
                {"source": "fallback-constant", "full_len": NR4A1_FULL_LEN_EXPECTED,
                 "fetch_error": f"{type(e).__name__}: {e}"})
    return (NR4A1_FULL_LEN_EXPECTED - NR4A_LBD_RESIDUES,
            {"source": "fallback-constant", "full_len": NR4A1_FULL_LEN_EXPECTED})


def main(argv=None):
    import argparse
    import boto3
    ap = argparse.ArgumentParser(description="Exhaustive A1 admissibility audit over every co-fold model.")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--prefixes", default="",
                    help="comma-sep co-fold prefixes; blank = auto-discover every prefix holding CIFs")
    ap.add_argument("--out", default="research/modalities/nrv04-covalent-input-audit.json")
    ap.add_argument("--max-models-per-system", type=int, default=0, help="0 = all")
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    s3 = boto3.client("s3")
    lbd_offset, off_prov = resolve_lbd_offset()
    doc = {"bucket": args.bucket, "a1_limit_A": MAX_COVALENT_TETHER_A,
           "frozen_covalent_site_fulllen": TARGET_COV_RESNUM,
           "electrophile_atom_label": CELASTROL_ELECTROPHILE_ATOM,
           "lbd_offset": lbd_offset, "lbd_offset_provenance": off_prov,
           "note": ("A1 measured on EVERY model of EVERY system of EVERY co-fold prefix. The prereg amendment's "
                    "'any co-fold in the bucket' rested on nrv04_prespend_check._pull_model, which samples ONE "
                    "model per system (sorted(_model_0.cif)[0])."),
           "prefixes": {}}

    prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()] or discover_cofold_prefixes(s3, args.bucket)
    doc["prefixes_examined"] = prefixes
    print(f"[audit] prefixes: {prefixes}", flush=True)

    for prefix in prefixes:
        keys = list_keys(s3, args.bucket, prefix.rstrip("/") + "/")
        systems = index_models(keys, prefix)
        pdoc = {"n_cif_objects": sum(1 for k, _, _ in keys if k.endswith(".cif")), "systems": {}}
        for system, models in sorted(systems.items()):
            ligand = SYSTEM_TO_LIGAND.get(system)
            if ligand is None:
                pdoc["systems"][system] = {"skipped": f"system {system!r} is not one of {list(SYSTEM_TO_LIGAND)}",
                                           "n_models": len(models)}
                continue
            sel = models if args.max_models_per_system <= 0 else models[: args.max_models_per_system]
            rows = []
            for m in sel:
                local = f"/tmp/audit_{prefix.replace('/', '_')}_{system}_{m['seed']}_{m['model']}.cif"
                try:
                    s3.download_file(args.bucket, m["key"], local)
                    r = measure_model(local, ligand, lbd_offset)
                except Exception as e:  # noqa: BLE001
                    r = {"error": f"{type(e).__name__}: {e}"}
                finally:
                    if os.path.exists(local):
                        os.remove(local)
                r.update({k: m[k] for k in ("key", "seed", "model", "mtime")})
                rows.append(r)
                a1 = r.get("a1") or {}
                print(f"  {prefix}/{system} {m['seed']}/model_{m['model']}: "
                      f"target={r.get('target_chain')} nearest_cys="
                      f"{(a1.get('nearest_target_cys') or {}).get('fulllen_resid')}@"
                      f"{(a1.get('nearest_target_cys') or {}).get('sg_dist_A')}A "
                      f"C551@{(a1.get('frozen_site') or {}).get('sg_dist_A')}A "
                      f"verdict={a1.get('verdict', r.get('error', '?'))}", flush=True)
            pdoc["systems"][system] = {"ligand": ligand, "n_models": len(models), "models": rows}
        doc["prefixes"][prefix] = pdoc
        with open(args.out, "w") as f:                     # checkpoint after every prefix
            json.dump(doc, f, indent=2)

    # ---- verdict ------------------------------------------------------------------------------------------
    allrows = [(p, s, r) for p, pd in doc["prefixes"].items() for s, sd in pd["systems"].items()
               for r in (sd.get("models") or [])]
    clean = [(p, s, r) for p, s, r in allrows if r.get("admissible_assembly")]
    passes_frozen = [(p, s, r) for p, s, r in clean if (r.get("a1") or {}).get("frozen_site_passes")]
    passes_any = [(p, s, r) for p, s, r in clean if (r.get("a1") or {}).get("nearest_passes")]
    dists = [((r.get("a1") or {}).get("frozen_site") or {}).get("sg_dist_A") for _, _, r in clean]
    dists = [d for d in dists if d is not None]
    doc["summary"] = {
        "n_models_measured": len(allrows),
        "n_models_clean_assembly": len(clean),
        "n_pass_A1_at_frozen_C551": len(passes_frozen),
        "n_pass_A1_at_any_target_cys": len(passes_any),
        "best_frozen_site_dist_A": min(dists) if dists else None,
        "best_frozen_site_model": (min(clean, key=lambda t: (t[2]["a1"]["frozen_site"]["sg_dist_A"]
                                                             if (t[2].get("a1") or {}).get("frozen_site", {})
                                                             .get("sg_dist_A") is not None else 1e9))[2].get("key")
                                   if dists else None),
        "admissible_input_exists": len(passes_frozen) > 0,
    }
    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2)
    print("\n=== EXHAUSTIVE A1 AUDIT SUMMARY ===", flush=True)
    print(json.dumps(doc["summary"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
