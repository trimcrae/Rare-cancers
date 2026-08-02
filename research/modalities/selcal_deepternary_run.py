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
RCSB_CIF = "https://files.rcsb.org/download/{p}.cif"
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


def _fetch_structure(pdb_id, workdir):
    """(path, error). Tries the legacy PDB format, falls back to mmCIF.

    ⚠ MEASURED, run 30751709728: BOTH arms refused on `HTTP 404` for the .pdb file. Recent and large entries
    are deposited mmCIF-only and have NO legacy PDB — 9DU0 and 9DTX are both in that class. A 404 here is a
    FORMAT fact, not a missing structure, and reading it as "structure unavailable" would have retired two
    perfectly good inputs."""
    for url, ext in ((RCSB_PDB, "pdb"), (RCSB_CIF, "cif")):
        dest = os.path.join(workdir, "%s.%s" % (pdb_id, ext))
        if os.path.exists(dest):
            return dest, None
        ok, err = _fetch(url.format(p=pdb_id), dest)
        if ok:
            return dest, None
        last = err
        if os.path.exists(dest):
            os.remove(dest)
    return None, "neither .pdb nor .cif could be fetched (last: %s)" % last


def resolve_chains(pdb_path, comp_id, near_a=6.0):
    """Polymer chains with a heavy atom within `near_a` of the named ligand. DERIVED from the file.

    Parsing is delegated to `selcal_cofold_validate.parse_structure`, which already handles both mmCIF and
    PDB and already applies the altloc/first-model rules — so this lane cannot drift from the parser the
    scoring instruments use."""
    import selcal_cofold_validate as V
    atoms = V.parse_structure(pdb_path)
    lig = [a.xyz for a in atoms if a.resname == comp_id and a.is_heavy]
    prot = [(a.chain, a.xyz) for a in atoms if a.resname in V._THREE_TO_ONE and a.is_heavy]
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


def e3_copy_chains(pdb_path, anchor_comp, n_subunits=3, near_a=6.0):
    """The ONE copy of the E3 that holds the anchor ligand: the chain the ligand sits on, grown by contact.

    ⚠ MEASURED, run 30751800137: the first version returned ALL polymer chains and gave 12 (A-L) for 5NVX,
    which holds four copies of VHL/EloB/EloC. Handing a generator four copies of the E3 is not a harder
    version of the same question — it is a different, meaningless one. Same multi-copy trap the scoring
    instruments hit earlier today, arriving from the input side instead.

    Grown by contact to ANY chain already chosen, not just to the ligand-bearing one, because Elongin B and C
    hang off VHL rather than touching the anchor."""
    import selcal_cofold_validate as V
    atoms = V.parse_structure(pdb_path)
    # ⚠ MEASURED, run 30751897153: seeding from "every chain near the ligand" returned ['C','F','I','L'] --
    # one VHL from each of 5NVX's four copies, because the anchor ligand is present in ALL of them. Seed from
    # ONE ligand INSTANCE, not from the ligand NAME.
    import selcal_cofold_validate as _V
    _atoms = _V.parse_structure(pdb_path)
    _inst = {}
    for a in _atoms:
        if a.resname == anchor_comp and a.is_heavy:
            _inst.setdefault(a.key, []).append(a.xyz)
    if not _inst:
        return [], "no copy of %s found in %s" % (anchor_comp, os.path.basename(pdb_path))
    _one = _inst[sorted(_inst)[0]]
    _c2 = near_a * near_a
    seed = sorted({a.chain for a in _atoms
                   if a.resname in _V._THREE_TO_ONE and a.is_heavy
                   and any((a.x-q[0])**2 + (a.y-q[1])**2 + (a.z-q[2])**2 <= _c2 for q in _one)})
    err = None if seed else "no polymer chain within %.1f A of the chosen %s copy" % (near_a, anchor_comp)
    if err or not seed:
        return [], err or "no chain carries %s" % anchor_comp
    ca = {}
    for a in atoms:
        if a.name == "CA" and a.resname in V._THREE_TO_ONE:
            ca.setdefault(a.chain, []).append(a.xyz)
    chosen = list(seed)
    while len(chosen) < n_subunits:
        rest = [c for c in ca if c not in chosen]
        if not rest:
            break
        best = max(rest, key=lambda c: (sum(V._chain_contact_count(ca, s, c) for s in chosen), c))
        if sum(V._chain_contact_count(ca, s, best) for s in chosen) == 0:
            break                                          # nothing else is bound to this copy
        chosen.append(best)
    return sorted(chosen), None


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
            p, err = _fetch_structure(cfg[key], workdir)
            if err:
                row.update(ok=False, why="could not fetch %s: %s" % (cfg[key], err))
                break
            paths[key] = p
        if not row["ok"]:
            report.append(row); continue

        poi_chains, err = resolve_chains(paths["poi_binary_pdb"], cfg["warhead_comp"])
        if err:
            row.update(ok=False, why="POI chain resolution: %s" % err); report.append(row); continue
        e3_chains, e3_err = e3_copy_chains(paths["e3_binary_pdb"], cfg["anchor_comp"])
        if e3_err:
            row.update(ok=False, why="E3 chain resolution: %s" % e3_err); report.append(row); continue
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


def write_pdb(atoms, dest):
    """Minimal PDB writer, so an mmCIF-only entry can still feed a PDB-only consumer.

    ⚠ WHY THIS EXISTS: `deepternary_blind_prep.fetch_pdb` requests the legacy .pdb format, and 9DU0 / 9DTY
    are mmCIF-only — the same 404 this module already hit and fixed on its own fetch path. Rather than
    changing a module another lane owns, the converted files are written into that module's `_raw` cache so
    its `_need()` finds them and never fetches. The conversion is coordinates only, which is all its chain and
    ligand extractors read."""
    n = 0
    with open(dest, "w") as fh:
        for i, a in enumerate(atoms, start=1):
            if i > 99999:
                break                                      # PDB serial field is 5 wide; truncation is loud below
            rec = "HETATM" if a.hetatm else "ATOM  "
            nm = a.name if len(a.name) >= 4 else " %-3s" % a.name
            fh.write("%s%5d %-4s %3s %s%4d%s   %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (rec, i, nm[:4], a.resname[:3], a.chain[:1], a.resseq, (a.icode or " ")[:1],
                        a.x, a.y, a.z, (a.element or "")[:2].rjust(2)))
            n += 1
        fh.write("END\n")
    return n


def emit_raw(configs, workdir, raw_dir):
    """Fetch every structure a config names and write it into `raw_dir` as <PDBID>.pdb."""
    import selcal_cofold_validate as V
    os.makedirs(raw_dir, exist_ok=True)
    out = []
    for cfg in configs:
        for key in ("poi_binary_pdb", "e3_binary_pdb", "native_pdb"):
            pid = cfg[key].upper()
            dest = os.path.join(raw_dir, "%s.pdb" % pid)
            if os.path.exists(dest):
                continue
            src, err = _fetch_structure(pid, workdir)
            if err:
                out.append({"pdb": pid, "ok": False, "why": err}); continue
            atoms = V.parse_structure(src)
            n = write_pdb(atoms, dest)
            out.append({"pdb": pid, "ok": n > 0, "n_atoms": n, "from": os.path.basename(src),
                        "truncated_at_99999": n == 99999})
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Prep + run + score the DeepTernary head-to-head ($0 CPU).")
    ap.add_argument("--emit-raw", default=None,
                    help="also write every named structure into this dir as <PDBID>.pdb (for a PDB-only consumer)")
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
    if args.emit_raw and ready:
        doc["raw_emitted"] = emit_raw(ready, args.workdir, args.emit_raw)
        for r in doc["raw_emitted"]:
            print("  raw %s %s %s" % (r["pdb"], "ok" if r["ok"] else "FAILED",
                                      r.get("why") or "%d atoms from %s" % (r.get("n_atoms", 0),
                                                                            r.get("from", "?"))), flush=True)
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
