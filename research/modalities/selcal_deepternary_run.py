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


CCD_CIF = "https://files.rcsb.org/ligands/download/{c}.cif"


def ccd_bonds(comp_id, workdir):
    """{(atom_id_1, atom_id_2)} for one chemical component, from the CCD's own `_chem_comp_bond` table.

    ⚠ SOURCED, NEVER DISTANCE-INFERRED. A distance guess would invent chemistry, and the whole point of the
    CONECT records this feeds is to tell RDKit what the bonds ARE. The CCD is the authority and it is keyed by
    ATOM NAME, which is exactly what a CONECT record needs."""
    dest = os.path.join(workdir, "%s_ccd.cif" % comp_id)
    if not os.path.exists(dest):
        ok, err = _fetch(CCD_CIF.format(c=comp_id), dest)
        if not ok:
            return None, "could not fetch the CCD definition for %s: %s" % (comp_id, err)
    cols, rows = _cif_loop(open(dest).read(), "_chem_comp_bond.")
    if not cols:
        return None, "no _chem_comp_bond loop in the CCD definition for %s" % comp_id
    try:
        i1 = cols.index("_chem_comp_bond.atom_id_1"); i2 = cols.index("_chem_comp_bond.atom_id_2")
    except ValueError:
        return None, "the %s bond loop lacks atom_id_1/atom_id_2" % comp_id
    return {(r[i1], r[i2]) for r in rows if len(r) > max(i1, i2)}, None


def _cif_loop(text, prefix):
    """(column names, rows) for the first `loop_` whose columns start with `prefix`. Pure stdlib."""
    import selcal_cofold_validate as V
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        if lines[i].strip() == "loop_":
            cols, j = [], i + 1
            while j < n and lines[j].strip().startswith("_"):
                cols.append(lines[j].strip()); j += 1
            if cols and cols[0].startswith(prefix):
                rows = []
                while j < n:
                    t = lines[j].strip()
                    if not t or t.startswith(("#", "loop_", "_")) or t == "stop_":
                        break
                    rows.append(V._split_cif_row(t)); j += 1
                return cols, rows
            i = j
        else:
            i += 1
    return [], []


#: Legacy PDB gives the residue-name field THREE columns (18-20). Modern CCD ids are five characters, which
#: is a large part of why entries carrying them are deposited mmCIF-only. Truncating silently produced
#: `A1BB5` -> `A1B`, so the downstream extractor found ZERO atoms for the warhead and `prep_control` still
#: reported ok (it checks that the file exists, not that it has atoms). Long codes are therefore ALIASED to a
#: short, unique, per-file placeholder, and the alias is RETURNED so every consumer uses the same name.
#: The CCD bond lookup keeps using the real code — the alias is a file-format workaround, not a rename of
#: the chemistry.
def _alias_for(resnames):
    out, used = {}, set()
    for rn in sorted(r for r in resnames if len(r) > 3):
        for i in range(1, 100):
            cand = "L%02d" % i
            if cand not in used and cand not in resnames:
                out[rn] = cand; used.add(cand); break
    return out


def write_pdb(atoms, dest, conect_for=()):
    """Minimal PDB writer, so an mmCIF-only entry can still feed a PDB-only consumer.

    ⚠ WHY THIS EXISTS: `deepternary_blind_prep.fetch_pdb` requests the legacy .pdb format, and 9DU0 / 9DTY
    are mmCIF-only — the same 404 this module already hit and fixed on its own fetch path. Rather than
    changing a module another lane owns, the converted files are written into that module's `_raw` cache so
    its `_need()` finds them and never fetches. The conversion is coordinates only, which is all its chain and
    ligand extractors read."""
    n = 0
    serial = {}
    alias = _alias_for({a.resname for a in atoms})
    with open(dest, "w") as fh:
        for i, a in enumerate(atoms, start=1):
            if i > 99999:
                break                                      # PDB serial field is 5 wide; truncation is loud below
            rec = "HETATM" if a.hetatm else "ATOM  "
            nm = a.name if len(a.name) >= 4 else " %-3s" % a.name
            fh.write("%s%5d %-4s %3s %s%4d%s   %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (rec, i, nm[:4], alias.get(a.resname, a.resname)[:3], a.chain[:1], a.resseq,
                        (a.icode or " ")[:1],
                        a.x, a.y, a.z, (a.element or "")[:2].rjust(2)))
            n += 1
            serial[(a.chain, a.resseq, a.icode, a.name)] = i
        # CONECT for the named HETATM components. mmCIF keeps connectivity in `chem_comp_bond`, not as CONECT,
        # so a straight coordinate conversion produces a ligand RDKit cannot sanitize -- measured on run
        # 30752326235, where `MolFromPDBFile` returned None and the prediction step died.
        for comp, bonds in (conect_for or {}).items():
            byres = {}
            for (ch, rs, ic, nm), ser in serial.items():
                byres.setdefault((ch, rs, ic), {})[nm] = ser
            for key, names in byres.items():
                for (a1, a2) in bonds:
                    if a1 in names and a2 in names:
                        fh.write("CONECT%5d%5d\n" % (names[a1], names[a2]))
        fh.write("END\n")
    return n, alias


def emit_raw(configs, workdir, raw_dir):
    """Fetch every structure a config names and write it into `raw_dir` as <PDBID>.pdb."""
    import selcal_cofold_validate as V
    os.makedirs(raw_dir, exist_ok=True)
    out, aliases = [], {}
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
            comps = {}
            errs = []
            for comp in {cfg.get("warhead_comp"), cfg.get("anchor_comp"), cfg.get("degrader_comp")}:
                if not comp or not any(a.resname == comp for a in atoms):
                    continue
                b, berr = ccd_bonds(comp, workdir)
                if berr:
                    errs.append(berr)
                else:
                    comps[comp] = b
            n, alias = write_pdb(atoms, dest, conect_for=comps)
            out.append({"pdb": pid, "ok": n > 0, "n_atoms": n, "from": os.path.basename(src),
                        "conect_components": {c: len(b) for c, b in comps.items()},
                        "conect_errors": errs or None,
                        "resname_alias": alias,
                        "_alias_why": ("legacy PDB's residue-name field is 3 columns; a 5-character CCD id "
                                       "would truncate and the downstream extractor would find zero atoms"),
                        "truncated_at_99999": n == 99999})
            aliases.update(alias)
    return out


def append_conect(lig_pdb, comp_id, workdir):
    """Append CONECT records to an already-extracted ligand PDB. (n_bonds_written, error).

    ⚠ THE LAST LINK IN A THREE-STEP CHAIN, each step of which was discovered by a failed CI run:
    mmCIF-only entry -> conversion drops CONECT (fixed in `write_pdb`) -> `deepternary_blind_prep.extract_
    ligand` copies the ligand's HETATM lines ONLY, stripping the CONECT that had just been added -> RDKit
    cannot sanitize a novel HETATM with no bonds and `MolFromPDBFile` returns None -> `predict_one_unbound`
    dies on `.GetConformer()`.

    Serials are re-read from THIS file rather than carried over, because the extracted file renumbers from 1.
    Bonds come from the CCD's own `_chem_comp_bond` table, never from interatomic distances: a covalent-radius
    guess would invent the very chemistry these records exist to state."""
    if not os.path.exists(lig_pdb):
        return 0, "ligand file absent: %s" % lig_pdb
    bonds, berr = ccd_bonds(comp_id, workdir)
    if berr:
        return 0, berr
    lines = open(lig_pdb).read().splitlines()
    serial = {}
    for ln in lines:
        if ln[:6] in ("ATOM  ", "HETATM"):
            try:
                serial[ln[12:16].strip()] = int(ln[6:11])
            except ValueError:
                continue
    if not serial:
        return 0, "no atom records in %s" % os.path.basename(lig_pdb)
    written, missing = [], set()
    for a1, a2 in sorted(bonds):
        if a1 in serial and a2 in serial:
            written.append("CONECT%5d%5d" % (serial[a1], serial[a2]))
        else:
            missing |= {a for a in (a1, a2) if a not in serial}
    if not written:
        return 0, ("no CCD bond of %s could be mapped onto %s — atom names do not correspond"
                   % (comp_id, os.path.basename(lig_pdb)))
    body = [l for l in lines if l.strip() != "END"]
    open(lig_pdb, "w").write("\n".join(body + written + ["END"]) + "\n")
    return len(written), (None if not missing else
                          "%d CCD atom name(s) absent from the extracted file (%s) — those bonds were "
                          "skipped, not guessed" % (len(missing), ",".join(sorted(missing)[:6])))


def fix_ligand_conect(configs, base, workdir):
    """Repair every ready arm's extracted ligand files in place."""
    out = []
    for cfg in configs:
        d = os.path.join(base, cfg["name"])
        for fn, comp in (("unbound_lig1.pdb", cfg.get("warhead_comp_real", cfg["warhead_comp"])),
                         ("unbound_lig2.pdb", cfg.get("anchor_comp_real", cfg["anchor_comp"]))):
            n, err = append_conect(os.path.join(d, fn), comp, workdir)
            out.append({"arm": cfg["name"], "file": fn, "comp": comp, "n_conect": n, "note": err,
                        "ok": n > 0})
    return out, aliases


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Prep + run + score the DeepTernary head-to-head ($0 CPU).")
    ap.add_argument("--fix-ligand-conect", default=None,
                    help="prep base dir (e.g. output/protac22): append CCD-sourced CONECT to the extracted "
                         "ligand files of every ready arm, then exit")
    ap.add_argument("--emit-raw", default=None,
                    help="also write every named structure into this dir as <PDBID>.pdb (for a PDB-only consumer)")
    ap.add_argument("--configs", default=os.path.join(HERE, "selcal-deepternary-prep-configs.json"))
    ap.add_argument("--workdir", default="/tmp/selcal_dt")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-deepternary-prep.json"))
    args = ap.parse_args(argv)

    cfgdoc = json.load(open(args.configs))
    cfgs = cfgdoc["configs"] if isinstance(cfgdoc, dict) else cfgdoc
    if args.fix_ligand_conect:
        rows = fix_ligand_conect(cfgs, args.fix_ligand_conect, args.workdir)
        for r in rows:
            print("  %-16s %-20s %s %d CONECT%s" % (r["arm"], r["file"], "ok " if r["ok"] else "FAILED",
                                                    r["n_conect"], "  — %s" % r["note"] if r["note"] else ""),
                  flush=True)
        json.dump(rows, open(args.out, "w"), indent=1)
        return 0 if all(r["ok"] for r in rows) else 4
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
        doc["raw_emitted"], aliases = emit_raw(ready, args.workdir, args.emit_raw)
        doc["resname_aliases"] = aliases
        # Consumers must extract by the ALIAS (what is in the file) while bonds are still looked up by the
        # REAL CCD id. Both are carried explicitly so neither is inferred.
        for c in ready:
            for k in ("warhead_comp", "anchor_comp"):
                c[k + "_real"] = c[k]
                c[k] = aliases.get(c[k], c[k])
        doc["ready_configs"] = ready
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
