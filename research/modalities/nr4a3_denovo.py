#!/usr/bin/env python3
"""
De-novo NR4A3 warhead design (matrix step 3) — the route's one genuinely missing piece: a *designed*,
NR4A3-selective warhead, rather than a repurposed tool compound. Two modes, split so the only GPU spend
is generation; the whole screen runs free on a GitHub CPU runner:

  MODE=generate  (GPU)  DiffSBDD samples molecules against the metad-OPENED NR4A3 pocket (frame-300
                        conformer the matrix already wrote to s3://<bucket>/nr4a3-matrix). Two campaigns:
                        `selective` conditions on the 5 engageable divergent handles (L406/T410/I484/
                        I531/L534); `pan` conditions on the conserved Pocket-5 CV residues. Emits the raw
                        SMILES pool (nr4a3-denovo-pool.json) + an SDF for provenance. Cheap: generation is
                        minutes-to-an-hour, unlike FEP.
  MODE=screen    (CPU)  Re-embeds the pool and runs the cheap cascade by REUSING the proven matrix
                        machinery — novelty (ECFP Tanimoto vs known NR4A actives) -> developability
                        (warhead_chem_profile.profile) -> smina docking into the three state-matched
                        opened pockets (the matrix's <tag>-opened.pdb) -> selectivity_fingerprint.classify
                        -> PROTAC-handle check. The pure thresholds/ranking live in denovo_select. Emits
                        nr4a3-denovo.json (ranked rows + shortlist + census).

The screen's output shortlist (docking-selective AND developable AND novel AND PROTAC-assemblable) is
what the one cheap MM-GBSA confirmation run scores; a molecule that comes back `confirmed_selective` is
the publishable designed candidate. Everything here is a design PRIOR, not affinity and not a validated
warhead — docking is triage, MM-GBSA is direction-only, the pocket is biased-MD-opened; the terminal
blockers (synthesise; prove binding/degradation; prove EMC fusion-addiction via dTAG) stay wet-lab.
"""
import json
import os
import subprocess
import sys

import nr4a3_dock as dock            # _which / chembl_* / make_sdf
import nr4a3_warhead as wh           # pocket_box / dock_into / handle_contacts
import nr4a3_matrix as mx            # box_for / read_manifest / KEY / ENGAGEABLE_HANDLES / CONSERVED_CV
import residue_map as rm
import denovo_select as dsl

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.environ.get("INPUT_DIR", HERE)
OUT = os.environ.get("OUTPUT_DIR", HERE)
wh.OUT = OUT                          # wh.dock_into / handle_contacts write pose SDFs into OUT
POOL_JSON = "nr4a3-denovo-pool.json"  # raw generated SMILES pool (generate -> screen hand-off)
RESULT_JSON = "nr4a3-denovo.json"     # screened, ranked result
N_PER_CAMPAIGN = int(os.environ.get("N_PER_CAMPAIGN", "200"))
NOVELTY_LIMIT = int(os.environ.get("NOVELTY_REF_LIMIT", "60"))   # cap known-actives set for fingerprints


# ============================================================ generation (GPU; DiffSBDD; guarded) ===
def _resseqs_from_pdb(pdb):
    out = []
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                out.append(int(line[22:26]))
            except ValueError:
                pass
    return out


def _resi_list_for(conf_pdb, resseqs, target_residues, lbd_first):
    """DiffSBDD `--resi_list` (chain:resi tokens) for the pocket residues to condition on, resolved onto
    the opened conformer's numbering. Chain defaults to A (the trimmed LBD)."""
    pos, _ = rm.resolve_positions(resseqs, target_residues, lbd_first)
    return [f"A:{resseqs[i]}" for i in pos]


def generate(campaign, conf_pdb, resseqs, n_samples=N_PER_CAMPAIGN):
    """Sample `n_samples` molecules with DiffSBDD conditioned on the opened pocket. Returns a list of
    {label, smiles, campaign}. GUARDED: needs a DiffSBDD checkout (DIFFSBDD_DIR) + checkpoint
    (DIFFSBDD_CKPT) + a GPU; without them it logs and returns [] (the repo's 'primed but skipped'
    pattern), so the module imports/compiles and the screen still runs on a provided pool.

    `campaign` selects the conditioning residues: 'selective' -> the 5 engageable divergent handles;
    'pan' -> the conserved Pocket-5 CV residues."""
    diffdir = os.environ.get("DIFFSBDD_DIR")
    ckpt = os.environ.get("DIFFSBDD_CKPT")
    if not (diffdir and ckpt):
        print(f"  [denovo] DIFFSBDD_DIR/DIFFSBDD_CKPT not set — generation skipped ({campaign})",
              file=sys.stderr)
        return []
    target = mx.ENGAGEABLE_HANDLES if campaign == "selective" else mx.CONSERVED_CV
    resi = _resi_list_for(conf_pdb, resseqs, target, mx.LBD_FIRST_NR4A3)
    if not resi:
        print(f"  [denovo] no conditioning residues resolved for {campaign} — skipped", file=sys.stderr)
        return []
    out_sdf = os.path.join(OUT, f"generated_{campaign}.sdf")
    cmd = ["python", os.path.join(diffdir, "generate_ligands.py"), ckpt,
           "--pdbfile", conf_pdb, "--outfile", out_sdf,
           "--resi_list", *resi, "--n_samples", str(n_samples)]
    print(f"  [denovo] DiffSBDD {campaign}: {' '.join(cmd[:6])} … ({len(resi)} pocket residues, "
          f"n={n_samples})", flush=True)
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:  # noqa: BLE001 — a failed campaign should not kill the other
        print(f"  [denovo] DiffSBDD {campaign} failed: {e}", file=sys.stderr)
        return []
    return _sdf_to_records(out_sdf, campaign)


def _sdf_to_records(sdf, campaign):
    """Read generated 3D molecules back to canonical SMILES (deduped within the file)."""
    try:
        from rdkit import Chem
    except ImportError:
        print("  [denovo] rdkit missing — cannot read generated SDF", file=sys.stderr)
        return []
    recs, seen = [], set()
    supplier = Chem.SDMolSupplier(sdf, sanitize=True)
    for i, m in enumerate(supplier):
        if m is None:
            continue
        try:
            smi = Chem.MolToSmiles(m)
        except Exception:  # noqa: BLE001
            continue
        if not smi or smi in seen:
            continue
        seen.add(smi)
        recs.append({"label": f"denovo-{campaign[:3]}-{len(recs):03d}", "smiles": smi,
                     "campaign": campaign})
    print(f"  [denovo] {campaign}: {len(recs)} unique valid molecules", flush=True)
    return recs


def run_generate():
    """GPU generation entry: NR4A3 opened conformer is the matrix's nr4a3-opened.pdb (mounted at IN)."""
    res = {"_mode": "generate", "campaigns": {}}
    conf = os.path.join(IN, "nr4a3-opened.pdb")
    if not os.path.exists(conf):
        res["_status"] = f"missing {conf} (mount s3://<bucket>/nr4a3-matrix at INPUT_DIR)"
        _write(res, POOL_JSON); return
    resseqs = _resseqs_from_pdb(conf)
    pool = []
    for campaign in ("selective", "pan"):
        recs = generate(campaign, conf, resseqs)
        res["campaigns"][campaign] = len(recs)
        pool.extend(recs)
    res["n_generated"] = len(pool)
    res["pool"] = pool
    res["_status"] = "ok" if pool else "no molecules generated (DiffSBDD model/GPU absent?)"
    _write(res, POOL_JSON)
    print(json.dumps({"campaigns": res["campaigns"], "n_generated": res["n_generated"]}, indent=2),
          flush=True)


# ===================================================================== screen (free CPU cascade) ===
def known_actives():
    """The known NR4A-active SMILES set the generated molecules must be NOVEL against (same ChEMBL
    matter the matrix/dock used). Network best-effort; empty on failure (novelty then can't gate)."""
    smis = []
    for nm in dock.LIGAND_NAMES:
        hit = dock.chembl_smiles_by_name(nm)
        if hit:
            smis.append(hit[1])
    for _, _, smi in dock.chembl_nr4a3_actives(limit=NOVELTY_LIMIT):
        smis.append(smi)
    return smis


def novelty_scores(smiles_list, ref_smiles):
    """Max ECFP4 Tanimoto of each candidate to the known-actives set (None if uncomputable)."""
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, DataStructs
    except ImportError:
        return {s: None for s in smiles_list}
    refs = []
    for s in ref_smiles:
        m = Chem.MolFromSmiles(s)
        if m is not None:
            refs.append(AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048))
    out = {}
    for s in smiles_list:
        m = Chem.MolFromSmiles(s)
        if m is None or not refs:
            out[s] = None
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)
        out[s] = round(max(DataStructs.BulkTanimotoSimilarity(fp, refs)), 3)
    return out


def _rdkit_profiler():
    """Assemble the RDKit tuple warhead_chem_profile.profile() expects (lazy; CPU runner has rdkit)."""
    import warhead_chem_profile as wcp
    from rdkit import Chem
    from rdkit.Chem import (Descriptors as Desc, Crippen, Lipinski as Lip, QED,
                            rdMolDescriptors as rdMD, RDConfig)
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    return wcp, (Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer)


def load_pool():
    p = os.path.join(IN, POOL_JSON)
    if not os.path.exists(p):
        p = os.path.join(OUT, POOL_JSON)
    with open(p) as fh:
        return json.load(fh).get("pool", [])


def run_screen():
    """Free CPU cascade over a generated pool: dock into the three opened pockets, classify, gate."""
    res = {"_mode": "screen",
           "_note": ("De-novo warhead screen: DiffSBDD pool docked into the metad-OPENED NR4A3/NR4A1/"
                     "NR4A2 pockets (state-matched, the matrix's <tag>-opened.pdb), then gated on "
                     "selectivity (selectivity_fingerprint) + novelty + developability + PROTAC handle. "
                     "Docking dG are screening PRIORS, not affinities; the shortlist is what the one "
                     "MM-GBSA run confirms. Not a validated warhead."),
           "engageable_handles": mx.ENGAGEABLE_HANDLES}
    os.makedirs(OUT, exist_ok=True)

    pool = load_pool()
    if not pool:
        res["_status"] = "no generated pool found (run MODE=generate first)"
        _write(res, RESULT_JSON); return
    res["n_generated"] = len(pool)

    # 1) re-embed the generated SMILES to a 3D SDF (same path the matrix used for ChEMBL matter).
    ligands = [(r["label"], r.get("smiles"), r["smiles"]) for r in pool]
    sdf = os.path.join(OUT, "denovo_candidates.sdf")
    kept = dock.make_sdf(ligands, sdf)
    kept_labels = {k[0] for k in kept}
    res["n_embedded"] = len(kept)

    # 2) dock the pool into each paralogue's OWN opened conformer (state-matched). Pose files use an
    #    internal `pool_<tag>` tag; the shortlist-only `docked_<tag>.sdf` handoff is emitted in step 6.
    per, n3 = {}, None
    for tag in mx.PARALOGUES:
        conf = os.path.join(IN, f"{tag}-opened.pdb")
        man = mx.read_manifest(os.path.join(IN, tag))
        if not os.path.exists(conf) or not man or not man.get("cv_residues"):
            res.setdefault("_warnings", []).append(f"{mx.KEY[tag]}: missing {tag}-opened.pdb or manifest")
            continue
        resseqs = _resseqs_from_pdb(conf)
        try:
            center = mx.box_for(conf, resseqs, man["cv_residues"], man["lbd_first"])
            scores, pose = wh.dock_into(conf, center, sdf, f"pool_{tag}")
        except Exception as e:  # noqa: BLE001
            res.setdefault("_warnings", []).append(f"{mx.KEY[tag]} dock failed: {e}")
            continue
        per[tag] = {"conformer": conf, "resseqs": resseqs, "scores": scores, "pose": pose}
    if "nr4a3" not in per:
        res["_status"] = "NR4A3 opened dock unavailable — cannot screen"
        _write(res, RESULT_JSON); return
    n3 = per["nr4a3"]

    # 3) NR4A3-pose contact scores (divergent engageable handles + conserved CV), as in the matrix.
    h_res = [n3["resseqs"][i] for i in rm.resolve_positions(n3["resseqs"], mx.ENGAGEABLE_HANDLES,
                                                            mx.LBD_FIRST_NR4A3)[0]]
    c_res = [n3["resseqs"][i] for i in rm.resolve_positions(n3["resseqs"], mx.CONSERVED_CV,
                                                            mx.LBD_FIRST_NR4A3)[0]]
    handle_contacts = wh.handle_contacts(n3["conformer"], n3["pose"], h_res) if h_res else {}
    conserved_contacts = wh.handle_contacts(n3["conformer"], n3["pose"], c_res) if c_res else {}

    # 4) developability (RDKit) + novelty (ECFP Tanimoto vs known actives).
    try:
        wcp, rdkit = _rdkit_profiler()
    except Exception as e:  # noqa: BLE001
        res["_status"] = f"rdkit profiler unavailable: {e}"; _write(res, RESULT_JSON); return
    novelty = novelty_scores([r["smiles"] for r in pool], known_actives())

    # 5) build + classify + gate every generated molecule (pure logic in denovo_select).
    rows = []
    for r in pool:
        if r["label"] not in kept_labels:
            continue
        dg = {t: per[t]["scores"].get(r["label"]) if t in per else None for t in mx.PARALOGUES}
        profile = wcp.profile(r["smiles"], rdkit)
        row = dsl.build_row(r, dg["nr4a3"], dg["nr4a1"], dg["nr4a2"], profile,
                            novelty.get(r["smiles"]),
                            handle_contacts=handle_contacts.get(r["label"], 0),
                            conserved_contacts=conserved_contacts.get(r["label"], 0))
        rows.append(row)

    summary = dsl.summarize(rows)
    res["candidates"] = dsl.rank(rows)
    res["summary"] = {k: v for k, v in summary.items()
                      if k in ("n_generated", "cell_census", "n_novel", "n_developable")}
    shortlist = [r["label"] for r in summary["screen_passers"]]
    res["shortlist"] = {
        "selective": [r["label"] for r in summary["selective_passers"]],
        "pan": [r["label"] for r in summary["pan_passers"]],
    }
    # 6) MM-GBSA handoff: emit the shortlist-only trio the existing mmgbsa job reads unchanged
    #    (<tag>-opened.pdb + docked_<tag>.sdf + a matrix-shaped nr4a3-matrix.json), so the one cheap
    #    confirmation run scores only the screen-passers (not all ~hundreds of generated molecules).
    res["mmgbsa_handoff"] = _emit_mmgbsa_handoff(shortlist, per,
                                                 [r for r in res["candidates"] if r["label"] in set(shortlist)])
    res["_status"] = "ok"
    _write(res, RESULT_JSON)
    print(json.dumps({"n_generated": res["n_generated"], "summary": res["summary"],
                      "shortlist": res["shortlist"]}, indent=2), flush=True)


def _filter_sdf(src, dst, keep_labels):
    """Write the SDF records whose title (molecule _Name) is in `keep_labels` to `dst`. Returns count."""
    if not os.path.exists(src):
        return 0
    blocks = open(src).read().split("$$$$")
    kept = []
    for b in blocks:
        lines = b.strip("\n").splitlines()
        if lines and lines[0].strip() in keep_labels:
            kept.append(b.strip("\n"))
    if kept:
        with open(dst, "w") as fh:
            fh.write("\n$$$$\n".join(kept) + "\n$$$$\n")
    return len(kept)


def _emit_mmgbsa_handoff(shortlist, per, shortlist_rows):
    """Stage the shortlist-only inputs the existing MM-GBSA job consumes from one prefix: copy each
    `<tag>-opened.pdb`, filter each pose set to the shortlist as `docked_<tag>.sdf`, and write a
    matrix-shaped `nr4a3-matrix.json` carrying the shortlist rows (label/margins/cell). Returns a small
    manifest dict. Skips silently if the shortlist is empty (nothing to confirm)."""
    import shutil
    info = {"n_shortlist": len(shortlist), "poses_per_target": {}}
    if not shortlist:
        return info
    keep = set(shortlist)
    for tag in mx.PARALOGUES:
        if tag not in per:
            continue
        shutil.copyfile(per[tag]["conformer"], os.path.join(OUT, f"{tag}-opened.pdb"))
        n = _filter_sdf(per[tag]["pose"], os.path.join(OUT, f"docked_{tag}.sdf"), keep)
        info["poses_per_target"][mx.KEY[tag]] = n
    handoff = {"_note": "Shortlist-only matrix-shaped projection of the de-novo screen, for the MM-GBSA "
                        "confirmation run (mmgbsa-aws.yml with input_prefix=nr4a3-denovo). Candidates are "
                        "DESIGNED molecules (no chembl_id); docking margins are screening priors.",
               "candidates": [{"label": r["label"], "chembl_id": None,
                               "margin_vs_NR4A1": r.get("margin_vs_NR4A1"),
                               "margin_vs_NR4A2": r.get("margin_vs_NR4A2"),
                               "cell": r.get("cell")} for r in shortlist_rows]}
    with open(os.path.join(OUT, "nr4a3-matrix.json"), "w") as fh:
        json.dump(handoff, fh, indent=2)
    return info


def _write(res, name):
    with open(os.path.join(OUT, name), "w") as fh:
        json.dump(res, fh, indent=2)


def main():
    mode = os.environ.get("MODE", "screen")
    if mode == "generate":
        run_generate()
    else:
        run_screen()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        import traceback
        name = POOL_JSON if os.environ.get("MODE") == "generate" else RESULT_JSON
        _write({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]}, name)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(0)
