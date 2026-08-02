#!/usr/bin/env python3
"""Resolve chains, verify the fragments are really fragments, prep, run DeepTernary, score. ($0 CPU)

The head-to-head: our Boltz co-folds score DockQ 0.023-0.046 on the target<->VHL interface of 9DTY/9DTX.
This runs a different generator, blind, on the SAME two targets and scores it with the SAME instruments
against the SAME references.

Three things this module refuses to assume, each because assuming it would produce a plausible wrong number:

  1. **Chains are RESOLVED FROM THE FILE, never typed.** The POI chains are the polymer chains with a heavy
     atom near the picked ligand; the E3 chains are the polymer chains of the VCB entry. Typing a chain letter
     is the defect class that once scored Elongin C as the degradation target for a whole panel.
  2. **The 'warhead' and 'anchor' fragments are VERIFIED to overlap the degrader.** They were picked on an
     RCSB name and a molecular weight, which is not evidence of chemistry. If the picked fragment is not a
     substructure of the degrader (or close to it by MCS), the arm REFUSES -- because a warhead frame defined
     by an unrelated molecule points DeepTernary at the wrong pocket sub-site and the resulting score would
     measure our input error, not the generator.
  3. **A refusal is never a zero.** Any arm that cannot be prepped, run or scored is reported as unrun.

⛔ SCOPE. A better score licenses one sentence: a different generator places this target against VHL closer to
the crystal than our co-folds did. Nothing about NR4A3, degradation, selectivity, or whether the endpoint can
rank paralogues -- the panel those co-folds fed returned a NULL whose bound is unchanged by anything here.

⚠ THE TWO ARMS ARE NOT COMPARABLE TO EACH OTHER (`selcal-deepternary-inputs-curated.json`): SMARCA2 has a
binary from the degrader's own CCD series, SMARCA4 has an unrelated chemotype nine years older. Each arm is
read only against OUR co-fold on that same arm.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
RCSB_PDB = "https://files.rcsb.org/download/{p}.pdb"
RCSB_IDEAL = "https://files.rcsb.org/ligands/download/{c}_ideal.sdf"

#: A picked fragment must share at least this fraction of its own heavy atoms with the degrader, by MCS.
#: Below it the arm refuses. Not a tuned threshold -- a genuine warhead or anchor fragment is a SUBSTRUCTURE
#: of the degrader and scores ~1.0; an unrelated molecule scores far below. It exists to catch the second
#: case, not to grade the first.
MIN_FRAGMENT_OVERLAP = 0.55


def _fetch(url, dest):
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            body = r.read()
    except Exception as e:                                  # noqa: BLE001
        return False, str(e)
    open(dest, "wb").write(body)
    return True, None


def resolve_chains(pdb_path, comp_id, near_a=6.0):
    """Polymer chains with a heavy atom within `near_a` of the named ligand. DERIVED from the file."""
    lig, prot = [], []
    for line in open(pdb_path):
        if line[:6] not in ("ATOM  ", "HETATM"):
            continue
        if line[16] not in (" ", "A"):
            continue
        try:
            xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        except ValueError:
            continue
        res, ch = line[17:20].strip(), line[21]
        if res == comp_id:
            lig.append(xyz)
        elif line[:6] == "ATOM  ":
            prot.append((ch, xyz))
    if not lig:
        return [], "ligand %s not found in %s" % (comp_id, os.path.basename(pdb_path))
    c2 = near_a * near_a
    near = set()
    for ch, p in prot:
        if ch in near:
            continue
        for q in lig:
            if (p[0]-q[0])**2 + (p[1]-q[1])**2 + (p[2]-q[2])**2 <= c2:
                near.add(ch); break
    return sorted(near), (None if near else "no polymer chain within %.1f A of %s" % (near_a, comp_id))


def all_polymer_chains(pdb_path):
    return sorted({l[21] for l in open(pdb_path) if l[:6] == "ATOM  " and l[16] in (" ", "A")})


def fragment_overlap(frag_comp, degrader_comp, workdir):
    """(fraction of the fragment's heavy atoms shared with the degrader by MCS, detail). Needs RDKit.

    Picked on a name and a molecular weight; this is the check that turns that into chemistry."""
    from rdkit import Chem
    from rdkit.Chem import rdFMCS
    paths = {}
    for c in (frag_comp, degrader_comp):
        p = os.path.join(workdir, "%s_ideal.sdf" % c)
        ok, err = _fetch(RCSB_IDEAL.format(c=c), p)
        if not ok:
            return None, "could not fetch %s ideal SDF: %s" % (c, err)
        paths[c] = p
    mols = {}
    for c, p in paths.items():
        m = next(iter(Chem.SDMolSupplier(p, removeHs=True)), None)
        if m is None:
            return None, "RDKit could not read %s ideal SDF" % c
        mols[c] = m
    res = rdFMCS.FindMCS([mols[frag_comp], mols[degrader_comp]], timeout=60,
                         ringMatchesRingOnly=True, completeRingsOnly=False)
    if res.canceled or res.numAtoms == 0:
        return 0.0, "no common substructure found"
    n_frag = mols[frag_comp].GetNumHeavyAtoms()
    return round(res.numAtoms / float(n_frag), 4), "MCS %d atoms / fragment %d heavy" % (res.numAtoms, n_frag)


def prepare(configs, workdir, degrader_comp):
    """Fetch, resolve chains, verify fragments. Returns (ready_configs, report)."""
    os.makedirs(workdir, exist_ok=True)
    ready, report = [], []
    for cfg in configs:
        row = {"name": cfg["name"], "ok": True, "why": None}
        paths = {}
        for key in ("poi_binary_pdb", "e3_binary_pdb", "native_pdb"):
            p = os.path.join(workdir, "%s.pdb" % cfg[key])
            if not os.path.exists(p):
                ok, err = _fetch(RCSB_PDB.format(p=cfg[key]), p)
                if not ok:
                    row.update(ok=False, why="could not fetch %s: %s" % (cfg[key], err))
                    break
            paths[key] = p
        if not row["ok"]:
            report.append(row); continue

        poi_chains, err = resolve_chains(paths["poi_binary_pdb"], cfg["warhead_comp"])
        if err:
            row.update(ok=False, why="POI chain resolution: %s" % err); report.append(row); continue
        e3_chains = all_polymer_chains(paths["e3_binary_pdb"])
        row["poi_chains"], row["e3_chains"] = poi_chains, e3_chains

        for label, comp in (("warhead", cfg["warhead_comp"]), ("anchor", cfg["anchor_comp"])):
            frac, detail = fragment_overlap(comp, degrader_comp, workdir)
            row["%s_overlap" % label] = frac
            row["%s_overlap_detail" % label] = detail
            if frac is None or frac < MIN_FRAGMENT_OVERLAP:
                row.update(ok=False,
                           why=("%s fragment %s shares only %s of its heavy atoms with the degrader %s (%s) — "
                                "below %.2f. A frame defined by an unrelated molecule points the generator at "
                                "the wrong sub-site, so this arm is REFUSED rather than run."
                                % (label, comp, frac, degrader_comp, detail, MIN_FRAGMENT_OVERLAP)))
                break
        if not row["ok"]:
            report.append(row); continue

        ready.append(dict(cfg, poi_chains=poi_chains, e3_chains=e3_chains))
        report.append(row)
    return ready, report


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Prep + run + score the DeepTernary head-to-head ($0 CPU).")
    ap.add_argument("--configs", default=os.path.join(HERE, "selcal-deepternary-prep-configs.json"))
    ap.add_argument("--workdir", default="/tmp/selcal_dt")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-deepternary-prep.json"))
    args = ap.parse_args(argv)

    cfgdoc = json.load(open(args.configs))
    cfgs = cfgdoc["configs"] if isinstance(cfgdoc, dict) else cfgdoc
    degrader = cfgs[0]["degrader_comp"]
    ready, report = prepare(cfgs, args.workdir, degrader)

    doc = {
        "_what": "Chain resolution + fragment verification for the DeepTernary head-to-head, before any "
                 "prediction is made.",
        "_licenses": "NOTHING about NR4A3, degradation or selectivity. A better score would license one "
                     "sentence about generator placement.",
        "_min_fragment_overlap": MIN_FRAGMENT_OVERLAP,
        "_why_the_overlap_check": "the fragments were picked on an RCSB name and a molecular weight, which is "
                                  "not evidence of chemistry. A frame defined by an unrelated molecule points "
                                  "the generator at the wrong sub-site and the score would measure our input "
                                  "error rather than the generator.",
        "degrader_comp": degrader,
        "arms": report,
        "n_ready": len(ready),
        "n_refused": len(report) - len(ready),
        "ready_configs": ready,
    }
    json.dump(doc, open(args.out, "w"), indent=1)
    print("[selcal-dt-run] wrote %s — %d ready, %d refused" % (args.out, doc["n_ready"], doc["n_refused"]),
          flush=True)
    for r in report:
        print("  %-16s %s  poi_chains=%s e3_chains=%s warhead=%s anchor=%s%s"
              % (r["name"], "READY " if r["ok"] else "REFUSED", r.get("poi_chains"), r.get("e3_chains"),
                 r.get("warhead_overlap"), r.get("anchor_overlap"),
                 "" if r["ok"] else "\n      %s" % r["why"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
