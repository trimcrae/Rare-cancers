#!/usr/bin/env python3
"""
De-novo plan STEP 2 — pocket-conditioned generation of NR4A3-selective warhead candidates (DiffSBDD).

WHY. The matrix + MM-GBSA showed repurposed ChEMBL compounds mostly do NOT hold up as NR4A3-selective
under a better energy model (cytosporone B reverses). We need bona-fide selective chemotypes designed FOR
the NR4A3 pocket. DiffSBDD (pocket-conditioned diffusion, pretrained on CrossDocked) generates 3D molecules
complementary to a given pocket. We condition it on the STEP-0 DRUGGABLE UNBIASED RELEASE conformation
(nr4a3-release-druggable) — the thermally-real, breathing, induced-fit pocket — NOT the biased-metad frame.
Designing into the NR4A3-specific *opened conformation* is itself a selectivity lever (the paralogues may
not adopt it); explicit paralogue selectivity is then enforced downstream (dock into the 3 opened pockets +
MM-GBSA). This is the PILOT: ~200 molecules, triaged on synthesizability/cleanliness/handle-contact before
any docking spend.

WHAT. (1) Read the Step-0 receptor manifest, take docking_primary_receptor + its fpocket box residues.
(2) Build DiffSBDD's --resi_list (chain:resnum) from those residues. (3) Run DiffSBDD generate_ligands.py
to sample N molecules into the pocket. (4) For each generated molecule: RDKit profile (QED/SAscore/PAINS/
BRENK/PROTAC-handles, reusing warhead_chem_profile.profile) + engageable-handle contact from the GENERATED
POSE (no docking needed — DiffSBDD places atoms in the pocket) + a composite triage score (denovo_funnel).
(5) Rank + summarise → nr4a3-denovo.json + a named SDF. Screening priors, NOT affinity / not a lead.

Inputs (env): RECEPTOR_DIR (Step-0 outputs: manifest + receptor PDBs), DIFFSBDD_DIR (cloned repo),
CKPT (checkpoint path), N_SAMPLES, CAMPAIGN (selective|pan). Output (env OUTPUT_DIR): nr4a3-denovo.json,
nr4a3-denovo.sdf, the receptor used, and a diversity plot.
"""
import json
import os
import shutil
import subprocess
import sys
import time

import denovo_funnel as funnel

LBD_FIRST = 373
POCKET_FIRST, POCKET_LAST = 406, 534
ENGAGEABLE = [406, 410, 484, 531, 534]        # pocket-facing divergent handles (handle-facing run)
RECEPTOR_DIR = os.environ.get("RECEPTOR_DIR", "/opt/ml/processing/input/receptor")
DIFFSBDD_DIR = os.environ.get("DIFFSBDD_DIR", "/opt/diffsbdd")
CKPT = os.environ.get("CKPT", "/opt/ckpt/crossdocked_fullatom_cond.ckpt")
N_SAMPLES = int(os.environ.get("N_SAMPLES", "200"))
CAMPAIGN = os.environ.get("CAMPAIGN", "selective")
# Lead-size constraint (the pilot showed unconstrained generation top-ranks fragments). Comma-separated
# DiffSBDD --num_nodes_lig values (heavy-atom counts); N_SAMPLES is split evenly across them so the output
# spans lead-sized molecules (~MW 300-450). Empty -> let the model sample its own size distribution.
NUM_NODES_LIST = os.environ.get("NUM_NODES_LIST", "24,28,32,36")
GEN_TIMEOUT = int(os.environ.get("GEN_TIMEOUT", "5400"))     # 90 min hard cap on generation (total)
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def _read_receptor_choice():
    """From the Step-0 manifest pick the receptor PDB + its box residues. Returns (pdb_path, box_resnums,
    source_str). Falls back to nr4a3-release-druggable.pdb + the 406-534 lining if the manifest is absent."""
    man = os.path.join(RECEPTOR_DIR, "nr4a3-release-druggable.json")
    if os.path.exists(man):
        m = json.load(open(man))
        pdb_name = m.get("docking_primary_receptor") or m.get("selection_primary_receptor") \
            or "nr4a3-release-druggable.pdb"
        box = []
        for r in m.get("receptors", []):
            if r.get("pdb") == pdb_name:
                box = r.get("box_residues") or []
                break
        pdb = os.path.join(RECEPTOR_DIR, pdb_name)
        if os.path.exists(pdb):
            return pdb, box, f"manifest docking_primary={pdb_name} (box {len(box)} res, confirmed druggable)"
    # fallback
    pdb = os.path.join(RECEPTOR_DIR, "nr4a3-release-druggable.pdb")
    if not os.path.exists(pdb):
        sys.exit(f"  ABORT: no receptor in {RECEPTOR_DIR} (need Step-0 nr4a3-release-druggable outputs)")
    return pdb, [], "fallback nr4a3-release-druggable.pdb (no manifest box; will map 406-534)"


def _pdb_residues(pdb):
    """Ordered unique (chain, resSeq) for protein residues with a CA atom; plus the resSeq list."""
    seen, residues = set(), []
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            chain = line[21].strip() or "A"
            try:
                rs = int(line[22:26])
            except ValueError:
                continue
            if (chain, rs) not in seen:
                seen.add((chain, rs))
                residues.append((chain, rs))
    return residues, [rs for _c, rs in residues]


def _resi_list_and_handles(pdb, box_resnums):
    """Build DiffSBDD --resi_list (chain:resnum) for the pocket, and map the engageable handles to the
    receptor's actual resSeqs for pose contact scoring. Uses residue_map so AF2 vs renumbered PDBs both work."""
    import residue_map as rm
    residues, resseqs = _pdb_residues(pdb)
    chain_of = {rs: ch for ch, rs in residues}
    if box_resnums:
        pocket_rs = [rs for rs in box_resnums if rs in chain_of]
    else:
        pos, _ = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
        pocket_rs = [resseqs[i] for i in pos]
    resi_list = [f"{chain_of.get(rs, 'A')}:{rs}" for rs in pocket_rs]
    hpos, _ = rm.resolve_positions(resseqs, ENGAGEABLE, LBD_FIRST)
    handle_rs = [resseqs[i] for i in hpos]
    return resi_list, handle_rs, len(residues)


def _run_diffsbdd(gen, pdb, resi_list, out_sdf, n, num_nodes, deadline):
    """One DiffSBDD generate_ligands.py invocation (optionally at a fixed --num_nodes_lig). Streams output;
    enforces the shared wall-clock deadline. Raises on failure."""
    cmd = ["python", gen, CKPT, "--pdbfile", pdb, "--outfile", out_sdf,
           "--n_samples", str(n), "--sanitize"]
    if num_nodes is not None:
        cmd += ["--num_nodes_lig", str(num_nodes)]
    cmd += ["--resi_list"] + resi_list
    tag = f"n={n}" + (f" size={num_nodes}" if num_nodes is not None else " size=model")
    print(f"  [denovo] generating ({tag}) → {os.path.basename(out_sdf)}", flush=True)
    proc = subprocess.Popen(cmd, cwd=DIFFSBDD_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    try:
        for line in proc.stdout:
            print(f"    [diffsbdd] {line.rstrip()}", flush=True)
            if time.time() > deadline:
                proc.kill()
                sys.exit(f"  ABORT: generation exceeded {GEN_TIMEOUT}s wall clock")
        rc = proc.wait()
    finally:
        if proc.poll() is None:
            proc.kill()
    if rc != 0:
        sys.exit(f"  ABORT: DiffSBDD generate_ligands.py ({tag}) exit {rc}")


def _generate(pdb, resi_list, out_sdf):
    """Sample N_SAMPLES molecules into the pocket, split across the configured lead-size list
    (NUM_NODES_LIST) so the output spans lead-sized molecules rather than fragments. Concatenates the
    per-size SDFs into out_sdf (SDF = concatenated $$$$ blocks). Raises on failure / empty output."""
    gen = os.path.join(DIFFSBDD_DIR, "generate_ligands.py")
    if not os.path.exists(gen):
        sys.exit(f"  ABORT: DiffSBDD generate_ligands.py not found at {gen} (DIFFSBDD_DIR wrong?)")
    if not os.path.exists(CKPT):
        sys.exit(f"  ABORT: checkpoint not found at {CKPT} (download failed? set CKPT)")
    sizes = [int(s) for s in NUM_NODES_LIST.split(",") if s.strip()] if NUM_NODES_LIST.strip() else []
    print(f"  [denovo] resi_list ({len(resi_list)} res): {' '.join(resi_list)}", flush=True)
    print(f"  [denovo] lead-size split: {sizes or 'model size distribution'}", flush=True)
    t0 = time.time()
    deadline = t0 + GEN_TIMEOUT
    if not sizes:
        _run_diffsbdd(gen, pdb, resi_list, out_sdf, N_SAMPLES, None, deadline)
    else:
        per = max(1, N_SAMPLES // len(sizes))
        parts = []
        for sz in sizes:
            part = out_sdf.replace(".sdf", f"_n{sz}.sdf")
            _run_diffsbdd(gen, pdb, resi_list, part, per, sz, deadline)
            if os.path.exists(part) and os.path.getsize(part) > 0:
                parts.append(part)
            else:
                print(f"  [denovo] WARN: size {sz} produced no SDF", file=sys.stderr)
        with open(out_sdf, "w") as o:
            for p in parts:
                o.write(open(p).read())
    if not os.path.exists(out_sdf) or os.path.getsize(out_sdf) == 0:
        sys.exit("  ABORT: DiffSBDD produced no molecules")
    print(f"  [denovo] generation done in {int(time.time() - t0)}s", flush=True)


def _profile_and_name(in_sdf, named_sdf, rdkit):
    """RDKit-profile each generated molecule; rewrite the SDF with stable names (denovo_<i>) so
    handle_contacts can key by name. Returns [{name, smiles, **profile}] (one per readable molecule)."""
    from rdkit import Chem
    import warhead_chem_profile as wc
    rows = []
    suppl = Chem.SDMolSupplier(in_sdf, sanitize=True)
    writer = Chem.SDWriter(named_sdf)
    for i, m in enumerate(suppl):
        name = f"denovo_{i}"
        if m is None:
            rows.append({"name": name, "error": "unreadable/invalid generated molecule"})
            continue
        try:
            smi = Chem.MolToSmiles(m)
            prof = wc.profile(smi, rdkit)
            m.SetProp("_Name", name)
            writer.write(m)
            rows.append({"name": name, "smiles": smi, **prof})
        except Exception as e:  # noqa: BLE001
            rows.append({"name": name, "error": f"profile failed: {str(e)[:160]}"})
    writer.close()
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    pdb, box, src = _read_receptor_choice()
    recep_copy = os.path.join(OUT, "receptor-used.pdb")
    shutil.copy(pdb, recep_copy)
    resi_list, handle_rs, n_res = _resi_list_and_handles(pdb, box)
    print(f"  receptor: {src}; protein residues={n_res}; engageable handle resSeqs={handle_rs}", flush=True)

    res = {"_note": "NR4A3 de-novo warhead generation (DiffSBDD, pocket-conditioned on the Step-0 DRUGGABLE "
                    "UNBIASED RELEASE conformation). Pilot tier: generate + cheminformatics + pose handle "
                    "contact. Screening priors, NOT affinity / not a validated lead. Paralogue selectivity "
                    "is enforced downstream (dock into 3 opened pockets + MM-GBSA).",
           "campaign": CAMPAIGN, "n_samples_requested": N_SAMPLES, "num_nodes_list": NUM_NODES_LIST,
           "receptor_source": src,
           "checkpoint": os.path.basename(CKPT), "resi_list": resi_list,
           "engageable_handle_resseqs": handle_rs}

    gen_sdf = os.path.join(OUT, "diffsbdd_raw.sdf")
    _generate(pdb, resi_list, gen_sdf)

    # RDKit lazily (runs inside the DiffSBDD env, which has RDKit).
    from rdkit.Chem import Descriptors as Desc, Crippen, Lipinski as Lip, QED, rdMolDescriptors as rdMD
    from rdkit.Chem import RDConfig
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    from rdkit import Chem
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    rdkit = (Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer)

    named_sdf = os.path.join(OUT, "nr4a3-denovo.sdf")
    rows = _profile_and_name(gen_sdf, named_sdf, rdkit)

    # Handle-contact from the generated pose (reuse the warhead geometry on the named SDF).
    import nr4a3_warhead as wh
    contacts = wh.handle_contacts(recep_copy, named_sdf, handle_rs, cutoff=4.0)
    for r in rows:
        hc = contacts.get(r["name"], 0)
        r["handle_contacts"] = hc
        r["denovo_promise"] = funnel.score_molecule(r if "error" not in r else None, hc)

    rows = funnel.rank(rows)
    res["summary"] = funnel.summarize(rows)
    res["candidates"] = rows
    res["_status"] = "ok"
    with open(os.path.join(OUT, "nr4a3-denovo.json"), "w") as fh:
        json.dump(res, fh, indent=2)

    s = res["summary"]
    print(f"  DONE: {s['n_valid']}/{s['n_generated']} valid, {s['n_unique_smiles']} unique; "
          f"synthesizable(SA<=4.5)={s['frac_synthesizable_sa_le_4.5']} "
          f"PAINS-free={s['frac_pains_free']} contacts>=4handles={s['frac_contacts_ge_4_handles']} "
          f"(max {s['max_handle_contacts']})", flush=True)
    top = [r for r in rows if r.get("denovo_promise") is not None][:5]
    for r in top:
        print(f"    {r['name']:<11} promise={r['denovo_promise']} QED={r.get('QED')} "
              f"SA={r.get('SAscore')} handles={r['handle_contacts']} {r.get('smiles', '')[:60]}", flush=True)
    _plot(rows)


def _plot(rows):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        valid = [r for r in rows if r.get("denovo_promise") is not None]
        if not valid:
            return
        sa = [r.get("SAscore") for r in valid if r.get("SAscore") is not None]
        qed = [r.get("QED") for r in valid if r.get("QED") is not None]
        plt.figure(figsize=(7, 4))
        plt.scatter(sa, qed, c=[r["handle_contacts"] for r in valid], cmap="viridis", s=22)
        plt.colorbar(label="engageable-handle contacts")
        plt.xlabel("SAscore (1 easy … 10 hard)")
        plt.ylabel("QED")
        plt.title(f"NR4A3 de-novo generations ({CAMPAIGN}) — synthesizability vs drug-likeness")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "nr4a3-denovo.png"), dpi=130)
    except Exception as e:  # noqa: BLE001
        print(f"  plot skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
