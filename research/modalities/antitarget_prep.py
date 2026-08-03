#!/usr/bin/env python3
"""Prepare the off-target / anti-target selectivity panel receptors (survivor-INDEPENDENT; run once).

For each target in antitarget_panel.json: fetch the RCSB PDB, isolate the chain that carries the reference
ligand, write a clean receptor PDB (protein ATOM records only — smina reads a plain PDB, as the NR4A dock
does), and define the docking-box CENTER as the centroid of that reference ligand (the orthosteric site) or,
if `box_residues` is given instead, the CA centroid of those residues. Upload each receptor PDB + a manifest
(name -> center) to s3://<bucket>/<OUTPUT_PREFIX>/ so the panel dock reads them exactly like the NR4A dock
reads its release receptors. Pure-stdlib PDB parsing (no rdkit/smina) so it runs on a plain GitHub runner.

A target whose ligand/chain cannot be resolved is DROPPED with a logged warning (never silently emitted as a
bad receptor) — refine its pdb_id/ligand_resname in the panel JSON and re-run.

Env: BUCKET (opt), OUTPUT_PREFIX (default nr4a3-antitarget-panel), AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STD_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
          "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "SEC", "PYL"}
# waters, ions, and common crystallization/cryo additives — never the biological ligand we center on.
NON_LIGAND = {"HOH", "DOD", "WAT", "NA", "CL", "K", "MG", "ZN", "CA", "MN", "FE", "CU", "NI", "CO", "CD",
              "SO4", "PO4", "NO3", "ACT", "EDO", "GOL", "PEG", "PGE", "PG4", "DMS", "MPD", "TRS", "EPE",
              "FMT", "BME", "IOD", "BR", "CS", "IMD", "CIT", "MLI", "ACY", "FLC", "TLA", "1PE", "P6G"}

# =============================================================================================================
# ⛔ COFACTOR RETENTION — added 2026-08-03, AFTER the panel's cognate-ligand self-control FAILED on CYP3A4.
# =============================================================================================================
# THE DOCSTRING ABOVE PREDICTED THIS FAILURE AND NOTHING ACTED ON THE PREDICTION. "protein ATOM records only"
# is correct for waters, ions and cryo-buffer, and WRONG for a prosthetic group the ligand is coordinated to.
# `antitarget_selfcontrol.py` measured the consequence: re-docking each panel target's own co-crystallised
# ligand recovered 7 of 10 poses, and CYP3A4 missed by 9.503 A against a 2.00 A criterion — docking
# ketoconazole into a haem protein with the haem deleted, when ketoconazole's binding mode is a direct
# Fe-N coordination to that haem. The cavity the panel was scoring had a hole where the cofactor belongs.
#
# ★ THE RULE IS UNIFORM AND CANNOT BE TARGET-SPECIFIC TUNING, WHICH MATTERS BECAUSE THE FROZEN RULE IN
# `antitarget-selfcontrol.json` FORBIDS EXACTLY THAT: "a failing target may not be dropped, its box may not
# be re-centred, and no band may be lowered." Retaining a cofactor is none of those — it makes the RECEPTOR
# more complete rather than the CRITERION more forgiving — but it must apply to every target identically or
# it becomes the same sin by another route. So the rule is stated once and evaluated for all ten:
#
#     retain a HETATM group iff it is (a) a recognised prosthetic group/cofactor OR a metal ion, AND
#     (b) it lies within COFACTOR_CONTACT_A of the cognate ligand copy the box is centred on.
#
# For nine of the ten targets this is a no-op. It is not a list of exceptions; it is one predicate, and
# `prep_target_full` reports what it kept AND what it still dropped inside the pocket, so "we stripped
# something else in there" can never again be an unasked question.
#
# ⚠ ANY NUMBER PRODUCED BEFORE THIS CHANGE WAS PRODUCED ON THE STRIPPED RECEPTOR. That includes every
# anti-target margin in SI §S1. `antitarget_selfcontrol.py` therefore runs BOTH receptors as an A/B rather
# than quietly replacing one with the other.
COFACTORS = {
    # haems and haem-like prosthetic groups
    "HEM", "HEA", "HEB", "HEC", "HEV", "HDD", "HNI", "SRM", "VER", "COH", "DHE", "1CP", "MH0",
    # flavins, nicotinamides, thiamine, pyridoxal, biotin, SAM/SAH, CoA
    "FAD", "FMN", "FDA", "NAD", "NAI", "NAP", "NDP", "NAJ", "TPP", "TDP", "PLP", "PMP", "BTN",
    "SAM", "SAH", "COA", "ACO", "COO", "MCA",
    # iron-sulfur clusters, molybdopterin, cobalamin, chlorophylls, quinones
    "FES", "SF4", "F3S", "FE2", "MGD", "MOO", "B12", "COB", "CLA", "BCL", "CHL", "PQN", "UQ1", "UQ2",
}
#: Monatomic metal ions. They live in NON_LIGAND (they are never the *ligand* to centre a box on) and are
#: retained here only when the cognate ligand actually contacts them — a catalytic zinc a ligand chelates
#: is part of the site; a crystallisation sodium 20 A away is not.
METAL_IONS = {"ZN", "FE", "FE2", "MG", "MN", "CU", "CU1", "NI", "CO", "CA", "CD", "K", "NA", "HG", "PT", "MO"}
#: Heavy-atom distance below which a cofactor counts as part of the site the ligand occupies. 4.5 A is the
#: conventional non-bonded contact shell; a direct metal coordination is ~2 A and sits well inside it.
COFACTOR_CONTACT_A = 4.5
#: Default. Env override exists so the A/B can reproduce the STRIPPED receptor that produced the published
#: numbers — not so anyone can turn the repair off and forget.
KEEP_COFACTORS = os.environ.get("ANTITARGET_KEEP_COFACTORS", "1") != "0"


def _fetch(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (trusted RCSB host)
        return r.read().decode("utf-8", "replace").splitlines()


def _prep_target(t):
    """Return (receptor_pdb_text, center_xyz, n_res) or raise with a reason.

    ⚠ THIN WRAPPER, DELIBERATELY. The body moved to `prep_target_full` on 2026-08-03 so the panel's
    never-run cognate-ligand SELF-CONTROL (`antitarget_selfcontrol.py`) can obtain the crystallographic
    ligand copy this function centres the box on. Duplicating the prep there would have meant the control
    graded a receptor the panel does not dock into — the one thing a self-control may not do. Nothing
    about the emitted receptor, the chain choice or the box centre changes; `tests/test_antitarget_
    selfcontrol.py` pins the tuple this returns to `prep_target_full`'s fields.
    """
    f = prep_target_full(t)
    return f["receptor_pdb"], f["center"], f["n_res"]


def _groups(lines, want=None, exclude_resnames=()):
    """{(resname, chain, resSeq): [lines]} over HETATM records. Pure."""
    g = {}
    for ln in lines:
        if not ln.startswith("HETATM"):
            continue
        res = ln[17:20].strip()
        if res in exclude_resnames:
            continue
        if want is not None and res not in want:
            continue
        g.setdefault((res, ln[21], ln[22:27]), []).append(ln)
    return g


def _xyz(ln):
    return float(ln[30:38]), float(ln[38:46]), float(ln[46:54])


def _min_dist(a_lines, b_lines):
    """Minimum heavy-atom distance between two groups of PDB lines. Pure."""
    b = [_xyz(l) for l in b_lines if (l[76:78].strip() or l[12:16].strip()[:1]).upper() not in ("H", "D")]
    best = None
    for l in a_lines:
        if (l[76:78].strip() or l[12:16].strip()[:1]).upper() in ("H", "D"):
            continue
        ax, ay, az = _xyz(l)
        for bx, by, bz in b:
            d2 = (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2
            if best is None or d2 < best:
                best = d2
    return None if best is None else round(best ** 0.5, 2)


def site_hetatm_census(lines, cognate_lines, keep_cofactors=True, cutoff=None):
    """What non-solvent HETATM matter sits IN the pocket, and what the prep does with it. Pure.

    ⛔ THIS IS THE DIAGNOSTIC THAT ANSWERS "SAME CLASS OF REASON OR NOT". A self-control failure on a
    receptor built by deletion has exactly two shapes: something the ligand touches was deleted, or it was
    not. Returning `kept` and `dropped_in_pocket` for EVERY target — not only the failing ones — means the
    question is answered by measurement for all of them at once, and a target that fails with an empty
    `dropped_in_pocket` is thereby shown NOT to share CYP3A4's cause.
    """
    cutoff = COFACTOR_CONTACT_A if cutoff is None else cutoff
    cog_ids = {(l[17:20].strip(), l[21], l[22:27]) for l in cognate_lines}
    kept, dropped = [], []
    for gid, gl in _groups(lines, exclude_resnames={"HOH", "DOD", "WAT"}).items():
        if gid in cog_ids:
            continue
        d = _min_dist(gl, cognate_lines)
        if d is None:
            continue
        rec = {"resname": gid[0], "chain": gid[1], "resseq": gid[2].strip(), "n_atoms": len(gl),
               "min_dist_to_cognate_A": d,
               "is_cofactor": gid[0] in COFACTORS, "is_metal_ion": gid[0] in METAL_IONS}
        in_site = d <= cutoff
        rec["in_site"] = in_site
        eligible = rec["is_cofactor"] or rec["is_metal_ion"]
        if keep_cofactors and in_site and eligible:
            kept.append(rec)
        elif in_site:
            rec["why_still_dropped"] = ("not a recognised cofactor or metal ion" if not eligible else
                                        "cofactor retention is OFF for this build")
            dropped.append(rec)
    kept.sort(key=lambda r: r["min_dist_to_cognate_A"])
    dropped.sort(key=lambda r: r["min_dist_to_cognate_A"])
    return {"kept": kept, "dropped_in_pocket": dropped, "cutoff_A": cutoff,
            "keep_cofactors": bool(keep_cofactors)}


def prep_target_full(t, keep_cofactors=None):
    """Everything `_prep_target` derives, plus the ligand copy the box is centred on.

    Keys: receptor_pdb, center, n_res, chain, lig_resname, lig_lines (the HETATM records of the copy
    used for the centroid, in file order), centre_source ('ligand' | 'box_residues'), cofactors (the
    site-HETATM census above), and `ligand_resname_matched` — FALSE when the panel's declared
    `ligand_resname` is not in the file and the auto-ligand fallback chose a different molecule.

    ⚠ `ligand_resname_matched` EXISTS BECAUSE THE FALLBACK IS SILENT AND TWO PANEL ROWS WERE WRONG. The
    self-control's first run centred PXR on `SRL` while the panel declared `348`, and HSA on `RWF` while
    the panel declared `SWF`; both fell back to "largest drug-like HETATM group" and neither said so
    anywhere a reader would look. A populated field is not a measured one (CLAUDE.md §4).
    """
    keep_cofactors = KEEP_COFACTORS if keep_cofactors is None else keep_cofactors
    lines = _fetch(t["pdb_id"])
    lig = t.get("ligand_resname")
    box_res = t.get("box_residues")

    # locate the ligand copy (resname `lig`) and its chain -> that chain is the receptor we dock into.
    lig_atoms, lig_chain, lig_lines, lig_used = [], None, [], (lig.strip() if lig else None)
    if lig:
        for ln in lines:
            if ln.startswith("HETATM") and ln[17:20].strip() == lig.strip():
                ch = ln[21]
                if lig_chain is None:
                    lig_chain = ch
                if ch == lig_chain:
                    lig_atoms.append((float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
                    lig_lines.append(ln)
    # Fallback: named ligand absent (or none given) -> auto-pick the LARGEST drug-like HETATM group
    # (excludes waters/ions/buffers), which is the co-crystallized ligand in an orthosteric holo structure.
    if not lig_atoms:
        groups, group_lines = {}, {}
        for ln in lines:
            if not ln.startswith("HETATM"):
                continue
            res = ln[17:20].strip()
            if res in NON_LIGAND:
                continue
            gid = (res, ln[21], ln[22:27])
            groups.setdefault(gid, []).append((float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
            group_lines.setdefault(gid, []).append(ln)
        if groups:
            gid = max(groups, key=lambda g: len(groups[g]))
            lig_atoms, lig_chain = groups[gid], gid[1]
            lig_lines, lig_used = group_lines[gid], gid[0]
            print(f"  [{t['name']}] auto-ligand {gid[0]} chain {gid[1]} ({len(lig_atoms)} atoms)"
                  + (f" — named {lig} not found" if lig else ""))
        else:
            raise RuntimeError(f"no drug-like ligand found in {t['pdb_id']}")
    chain = lig_chain if lig_chain is not None else t.get("chain", "A")

    # clean receptor: standard-aa ATOM records of the chosen chain, altloc blank/A, drop hydrogens.
    rec, seen = [], set()
    for ln in lines:
        if not ln.startswith("ATOM"):
            continue
        if ln[21] != chain:
            continue
        if ln[17:20].strip() not in STD_AA:
            continue
        if ln[16] not in (" ", "A"):            # altloc: keep the primary conformer
            continue
        if ln[76:78].strip() == "H" or ln[12:16].strip().startswith("H"):
            continue
        rec.append(ln)
        seen.add(ln[22:27])                     # resSeq+iCode
    if len(seen) < 50:
        raise RuntimeError(f"only {len(seen)} residues on chain {chain} of {t['pdb_id']}")

    # ⛔ COFACTOR RETENTION. One predicate, evaluated for every target; see the header. The census is
    # computed whether or not retention is ON, so the STRIPPED build still reports what it is stripping.
    census = site_hetatm_census(lines, lig_lines, keep_cofactors=keep_cofactors)
    if keep_cofactors and census["kept"]:
        keep_ids = {(k["resname"], k["chain"], k["resseq"]) for k in census["kept"]}
        for ln in lines:
            if not ln.startswith("HETATM"):
                continue
            if ln[16] not in (" ", "A"):
                continue
            if (ln[76:78].strip() or ln[12:16].strip()[:1]).upper() in ("H", "D"):
                continue
            if (ln[17:20].strip(), ln[21], ln[22:27].strip()) in keep_ids:
                rec.append(ln)

    if lig_atoms:
        n = len(lig_atoms)
        center = (sum(a[0] for a in lig_atoms) / n, sum(a[1] for a in lig_atoms) / n,
                  sum(a[2] for a in lig_atoms) / n)
        centre_source = "ligand"
    elif box_res:
        want = {int(r) for r in box_res}
        xs = [(float(l[30:38]), float(l[38:46]), float(l[46:54]))
              for l in rec if l[12:16].strip() == "CA" and int(l[22:26]) in want]
        if not xs:
            raise RuntimeError(f"no box_residues CA found in {t['pdb_id']}")
        center = (sum(x[0] for x in xs) / len(xs), sum(x[1] for x in xs) / len(xs),
                  sum(x[2] for x in xs) / len(xs))
        centre_source = "box_residues"
    else:
        raise RuntimeError("no ligand_resname or box_residues to center on")
    return {"receptor_pdb": "\n".join(rec) + "\n", "center": [round(c, 3) for c in center],
            "n_res": len(seen), "chain": chain, "lig_resname": lig_used, "lig_lines": lig_lines,
            "centre_source": centre_source, "pdb_id": t["pdb_id"], "name": t.get("name"),
            "cofactors": census, "keep_cofactors": bool(keep_cofactors),
            "ligand_resname_declared": (lig.strip() if lig else None),
            "ligand_resname_matched": bool(lig) and lig_used == lig.strip(),
            "all_lines": lines}


def main():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-antitarget-panel")

    spec = json.load(open(os.path.join(HERE, "antitarget_panel.json")))
    ok, manifest = [], {"box_size": spec.get("box_size", 24), "targets": []}
    for t in spec["targets"]:
        try:
            pdb_text, center, n_res = _prep_target(t)
        except Exception as e:  # noqa: BLE001
            print(f"DROP {t['name']:<8} ({t['pdb_id']}): {e}")
            continue
        key = f"{prefix}/{t['name']}.pdb"
        s3.put_object(Bucket=bucket, Key=key, Body=pdb_text.encode())
        manifest["targets"].append({"name": t["name"], "class": t.get("class"),
                                    "pdb_id": t["pdb_id"], "center": center, "n_res": n_res})
        ok.append(t["name"])
        print(f"OK   {t['name']:<8} ({t['pdb_id']}): {n_res} res, center {center} -> s3://{bucket}/{key}")
    s3.put_object(Bucket=bucket, Key=f"{prefix}/panel-manifest.json",
                  Body=json.dumps(manifest, indent=2).encode())
    print(f"\nprepared {len(ok)}/{len(spec['targets'])} panel targets: {ok}")
    print(f"manifest -> s3://{bucket}/{prefix}/panel-manifest.json")
    if len(ok) < len(spec["targets"]):
        print("NOTE: some targets dropped — fix their pdb_id/ligand_resname in antitarget_panel.json and re-run.")


if __name__ == "__main__":
    main()
