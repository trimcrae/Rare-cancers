#!/usr/bin/env python3
"""ATOM-MAP BLAST-RADIUS AUDIT — what map did each archived alchemical leg actually run?

WHY THIS EXISTS (2026-07-26). `nr4a3_rbfe._mapping` ran `LomapAtomMapper(time=20, threed=False)` for the
whole life of this repo. `time` is LOMAP's MCS timeout IN SECONDS, and a timed-out MCS returns its best
PARTIAL match silently. So the atom map — i.e. WHAT THE ALCHEMICAL TRANSFORMATION ACTUALLY IS — depended on
how fast the rented host happened to be. A partial map is not a slow answer, it is A DIFFERENT EXPERIMENT:
atoms that should map 1:1 become dummies that are annihilated and recreated. The leg still converges, still
returns tight MBAR statistics, and still reports a confident ΔG — for a perturbation nobody designed.

Nothing downstream catches it. The reducer does not look at the map. `protocol_hash` covers OpenFE settings,
not the map. The system-identity check compares particle counts, which a remap leaves unchanged. Only
`ternary_endpoint_align.verify_endpoints` sees it, and only on the lanes that run it.

So every archived leg needs its recorded map size compared against the count that is PROVABLY achievable for
its transformation. This module does exactly that, in three separable modes, none of which rents a GPU:

    bounds   rdkit only, runs anywhere.  Per edge: the provably-complete map size when it exists, and the
             conservative MCS floor otherwise.  This is the "expected" column of the audit table.
    archive  boto3 only.  Sweeps the S3 result prefixes for every artifact that RECORDS a map size
             (leg JSONs' `n_mapped_atoms`, and the `[rbfe] LOMAP ...` lines in archived leg logs) and
             joins them against `bounds`.  This is the "actual" column.
    maps     needs openfe — run it inside `triskit23/ternary-fep` (or nr4a3fep).  Re-derives the PRODUCTION
             map for every edge at BOTH budgets (RBFE_LOMAP_TIME_S=20 and =300) so the timeout's effect is
             measured on this repo's real chemistry rather than argued about.

★ "UNVERIFIABLE" IS A REAL ANSWER AND IT IS PRINTED AS ONE. If an artifact does not record a map size, this
says so. Absence of evidence is not evidence of a clean map — the repo has twice today had a null reading
rendered as a benign one (`leg_status_peek._get`, and the fan-out monitor before it), so every unreadable or
unrecorded quantity comes back UNVERIFIABLE, never CLEAN.

Usage:
    python3 research/modalities/atom_map_audit.py bounds
    python3 research/modalities/atom_map_audit.py archive        # needs AWS creds (CI, not the dev sandbox)
    python3 research/modalities/atom_map_audit.py maps           # needs openfe (the parity image)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_SUFFIX = os.environ.get("MAP_AUDIT_OUT_SUFFIX", "")
OUT = os.path.join(HERE, "atom-map-audit%s.json" % (("-" + _SUFFIX) if _SUFFIX else ""))

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
# Every prefix under which this repo has ever archived an alchemical leg produced by `_mapping`.
ARCHIVE_PREFIXES = [p for p in (os.environ.get("MAP_AUDIT_PREFIXES") or
                                "ternary-vast,nr4a3-step1-fanout,nr4a3-rbfe,nrv04-retro").split(",") if p]

# The MCS floor is computed with LOMAP-COMPATIBLE ring rules on purpose (see _mcs). rdFMCS with the permissive
# defaults can return a core LOMAP would refuse to use (it will not map a partial ring), which would make the
# floor unachievable and the guard unsatisfiable — the same shape of bug as the RUNG 2b "expect 2fs" anchor
# that no build could satisfy.
MCS_TIMEOUT_S = int(os.environ.get("MAP_AUDIT_MCS_TIMEOUT_S", "120"))


# ---- provable bounds (rdkit only) ---------------------------------------------------------------------------

def _mol(smiles, Chem):
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError("unparseable SMILES: %s" % smiles)
    return m


_MAX_ISO_MATCHES = int(os.environ.get("MAP_AUDIT_MAX_ISO_MATCHES", "2000"))


def _skeleton_mol(mol, Chem):
    """A canonical form of a molecule's HEAVY-ATOM GRAPH with every label erased.

    Every atom becomes carbon, every bond becomes single, charges/isotopes/radicals/stereo/aromaticity all go.
    RDKit's canonical SMILES of that unlabelled skeleton is therefore a canonical form of the bare graph, so
    two molecules have isomorphic heavy-atom graphs IFF these strings are equal. Cheap, exact, and — unlike a
    substructure match against a generic query — it has no query-perception subtleties to get wrong."""
    m = Chem.RWMol(Chem.Mol(mol))
    Chem.RemoveStereochemistry(m)
    for a in m.GetAtoms():
        a.SetAtomicNum(6)
        a.SetFormalCharge(0)
        a.SetIsotope(0)
        a.SetNumRadicalElectrons(0)
        a.SetIsAromatic(False)
        a.SetNoImplicit(True)
        a.SetNumExplicitHs(0)
    for b in m.GetBonds():
        b.SetBondType(Chem.BondType.SINGLE)
        b.SetIsAromatic(False)
    out = m.GetMol()
    out.UpdatePropertyCache(strict=False)
    return out


def _skeleton_canonical(mol, Chem):
    """Canonical SMILES of that unlabelled skeleton — a canonical form of the bare graph, so two molecules
    have isomorphic heavy-atom graphs IFF these strings are equal. Exact, and (unlike a substructure match
    against a generic query) free of query-perception subtleties."""
    return Chem.MolToSmiles(_skeleton_mol(mol, Chem), canonical=True)


def graphs_isomorphic_ignoring_element(mA, mB, Chem):
    """Are A and B the SAME heavy-atom graph once you stop caring which element each atom is?

    This is the one bound that needs no search and admits no argument. If it holds, then every HEAVY atom of A
    has a partner in B, so a map covering all |heavy(A)| atoms provably exists and any mapper returning fewer
    has failed its SEARCH — it has not discovered chemistry. It is the exact situation of both edges that
    exposed the bug: the 5a-KS d0->d identity edge (one pose written twice) and the Wurz cmpd1->cmpd4 single
    ring N->CH swap."""
    if mA.GetNumAtoms() != mB.GetNumAtoms() or mA.GetNumBonds() != mB.GetNumBonds():
        return False
    return _skeleton_canonical(mA, Chem) == _skeleton_canonical(mB, Chem)


def _mcs(mA, mB, Chem, element_exact=True):
    """Conservative MCS floor, with LOMAP-compatible ring handling.

    `completeRingsOnly=True, ringMatchesRingOnly=True` matches how LOMAP treats rings, so the number this
    returns is one a correct LOMAP search should be able to REACH. A permissive rdFMCS core would not be, and
    a floor no build can satisfy is a bug in the gate, not a finding."""
    from rdkit.Chem import rdFMCS
    kw = dict(completeRingsOnly=True, ringMatchesRingOnly=True, timeout=MCS_TIMEOUT_S)
    if not element_exact:
        kw["atomCompare"] = rdFMCS.AtomCompare.CompareAny
        kw["bondCompare"] = rdFMCS.BondCompare.CompareAny
    r = rdFMCS.FindMCS([mA, mB], **kw)
    return {"n_atoms": r.numAtoms, "n_bonds": r.numBonds, "canceled": bool(r.canceled),
            "smarts": r.smartsString}


def _min_element_mismatch(mA, mB, Chem):
    """Over every isomorphism between A's and B's heavy skeletons, the FEWEST atoms whose element differs.

    This is what turns "the graphs are the same shape" into a number a guard can enforce. A strict
    (element_change=False) mapper is entitled to leave each element-mismatched atom unmapped; it is not
    entitled to leave anything else unmapped. So `hA - this` is a floor no correct search can fall below,
    under EITHER element policy — which is precisely the property a hard-fail needs and which the raw
    isomorphism floor `hA` does not have."""
    sk_a = _skeleton_mol(mA, Chem)
    sk_b = _skeleton_mol(mB, Chem)
    best = None
    for match in sk_b.GetSubstructMatches(sk_a, uniquify=False, useChirality=False,
                                          maxMatches=_MAX_ISO_MATCHES):
        n = sum(1 for i, j in enumerate(match)
                if mA.GetAtomWithIdx(i).GetAtomicNum() != mB.GetAtomWithIdx(j).GetAtomicNum())
        if best is None or n < best:
            best = n
            if best == 0:
                break
    return best


def _mismatch_indices(mA, mB, Chem):
    """A-side indices of the element-mismatched atoms under the BEST isomorphism (the one used for the floor)."""
    sk_a = _skeleton_mol(mA, Chem)
    sk_b = _skeleton_mol(mB, Chem)
    best_idx, best_n = [], None
    for match in sk_b.GetSubstructMatches(sk_a, uniquify=False, useChirality=False,
                                          maxMatches=_MAX_ISO_MATCHES):
        idx = [i for i, j in enumerate(match)
               if mA.GetAtomWithIdx(i).GetAtomicNum() != mB.GetAtomWithIdx(j).GetAtomicNum()]
        if best_n is None or len(idx) < best_n:
            best_idx, best_n = idx, len(idx)
            if best_n == 0:
                break
    return best_idx


def _h_on(mol, idxs, Chem):
    """Explicit+implicit hydrogens carried by the given heavy atoms — the H that travel with a mismatched atom
    and may therefore legitimately fail to map alongside it."""
    return sum(mol.GetAtomWithIdx(i).GetTotalNumHs() for i in idxs)


def edge_bounds(name_a, smi_a, name_b, smi_b):
    """Everything provable about how large this edge's atom map MUST be, before any mapper runs.

    Returns total-atom (explicit-H) counts because that is the unit OpenFE's mapping is counted in — verified
    against two independent observations: the 5a-KS identity edge mapped 111 atoms for a 111-atom (64 heavy)
    ligand, and the valB r0 legs mapped 109 for the 109-atom (59 heavy) Wurz cmpd1. LOMAP maps hydrogens."""
    from rdkit import Chem
    mA, mB = _mol(smi_a, Chem), _mol(smi_b, Chem)
    hA, hB = mA.GetNumAtoms(), mB.GetNumAtoms()
    nA = Chem.AddHs(mA).GetNumAtoms()
    nB = Chem.AddHs(mB).GetNumAtoms()
    iso = graphs_isomorphic_ignoring_element(mA, mB, Chem)
    out = {
        "edge": "%s->%s" % (name_a, name_b), "node_a": name_a, "node_b": name_b,
        "n_heavy_a": hA, "n_heavy_b": hB, "n_atoms_a": nA, "n_atoms_b": nB,
        "heavy_graphs_isomorphic_ignoring_element": iso,
    }
    if iso:
        # Every heavy atom of A has a partner. No MCS search is run — an isomorphic pair is exactly the case
        # where the search is unnecessary AND (on a 59-heavy PROTAC) prone to time out, which would downgrade
        # a provable bound to a spurious UNVERIFIABLE.
        mism = _min_element_mismatch(mA, mB, Chem)
        out["complete_map_provable"] = True
        out["n_element_mismatched_heavy"] = mism
        out["heavy_floor_ideal"] = hA
        out["expected_n_mapped_atoms"] = min(nA, nB)
        if mism is None:
            out["total_floor_enforced"] = None
            out["floor_note"] = ("skeletons are isomorphic but the isomorphism enumeration hit its cap, so no "
                                 "enforceable floor is derived — UNVERIFIABLE rather than assumed clean")
        else:
            # An element-mismatched atom, and the hydrogens it carries, may legitimately go unmapped under a
            # STRICT (element_change=False) map. Nothing else may. |nA-nB| covers the H-count difference the
            # substitution creates. This floor is therefore satisfiable under either element policy, which is
            # what makes it safe to hard-fail on.
            mism_idx = _mismatch_indices(mA, mB, Chem)
            slack = mism + _h_on(mA, mism_idx, Chem) + abs(nA - nB)
            out["total_floor_enforced"] = max(1, nA - slack)
            out["floor_note"] = (
                "the endpoints are the SAME heavy-atom graph up to %d element substitution(s), so a map of "
                "all %d atoms of A provably exists (complete = %d, with %d dummy on B). Enforceable floor "
                "%d = %d atoms of A minus the %d mismatched heavy atom(s), the %d H they carry, and the %d "
                "atom count difference — a floor a strict-element map still satisfies."
                % (mism, nA, min(nA, nB), abs(nA - nB), out["total_floor_enforced"], nA, mism,
                   _h_on(mA, mism_idx, Chem), abs(nA - nB)))
    else:
        out["complete_map_provable"] = False
        strict = _mcs(mA, mB, Chem, element_exact=True)
        anyel = _mcs(mA, mB, Chem, element_exact=False)
        out["mcs_heavy_element_exact"] = strict
        out["mcs_heavy_element_agnostic"] = anyel
        out["expected_n_mapped_atoms"] = None
        out["heavy_floor_ideal"] = None if anyel["canceled"] else anyel["n_atoms"]
        out["total_floor_enforced"] = None if strict["canceled"] else strict["n_atoms"]
        out["floor_note"] = (
            "no complete map is provable (the endpoints differ constitutionally), so the enforceable floor is "
            "the element-exact MCS HEAVY-atom count: %s. That deliberately ignores hydrogens, making it a "
            "loose but unfalsifiable bound — a LOMAP map below it has failed its search under either element "
            "policy." % ("UNVERIFIABLE (MCS timed out)" if strict["canceled"] else strict["n_atoms"]))
    return out


def classify(n_mapped, bounds):
    """CLEAN / DEGENERATE / SUSPECT / UNVERIFIABLE for one observed map size against one edge's bounds.

    UNVERIFIABLE is returned whenever the observation or the bound is missing, and it is NOT a synonym for
    'probably fine'. Absence of evidence is not evidence of a clean map."""
    if n_mapped is None:
        return "UNVERIFIABLE", "no map size recorded for this leg"
    floor = bounds.get("total_floor_enforced")
    if floor is None:
        return "UNVERIFIABLE", "no enforceable floor could be derived for this edge (%s)" % bounds["floor_note"]
    exp = bounds.get("expected_n_mapped_atoms")
    if n_mapped < floor:
        return "DEGENERATE", ("mapped %d < enforceable floor %d — a failed MCS search, not chemistry; %d atoms "
                              "that should map became dummies" % (n_mapped, floor, floor - n_mapped))
    if exp is not None and n_mapped < exp:
        return "SUSPECT", ("mapped %d clears the enforceable floor %d but falls short of the provably-complete "
                           "%d — legitimate only if the mapper returned a strict-element map" %
                           (n_mapped, floor, exp))
    return "CLEAN", ("mapped %d >= floor %d%s" % (n_mapped, floor,
                                                  " (complete)" if exp is not None and n_mapped >= exp else ""))


def _edge_catalogue():
    """Every A->B pair this repo has ever handed to `_mapping`, with its SMILES, read from the repo's own
    frozen artifacts — nothing here is typed by hand (rule 1: one fact, one place)."""
    edges = []
    mp = json.load(open(os.path.join(HERE, "congeneric-rbfe-map.json")))
    smiles = {n["id"]: n["smiles"] for n in mp["nodes"]}
    for e in mp["edges"]:
        edges.append({"lane": "step1_fanout", "edge_id": e["edge_id"], "klass": e["class"],
                      "name_a": e["node_a"], "smi_a": smiles[e["node_a"]],
                      "name_b": e["node_b"], "smi_b": smiles[e["node_b"]],
                      "prefer_element_change": e["class"] in ("bioisostere", "microstate_variant")})
    w = json.load(open(os.path.join(HERE, "wurz-calib-frozen.json")))
    edges.append({"lane": "valB_mini / RUNG 2b", "edge_id": "calib_hi_to_lo", "klass": "element_change",
                  "name_a": w["calib_hi"]["name"], "smi_a": w["calib_hi"]["smiles"],
                  "name_b": w["calib_lo"]["name"], "smi_b": w["calib_lo"]["smiles"],
                  "prefer_element_change": True})
    for leg in ("5aks_d0_to_d__ternary_nr4a3", "5aks_d0_to_d__ternary_nr4a1"):
        f = os.path.join(HERE, "5aks_fep_inputs", leg, "staging_manifest.json")
        if os.path.exists(f):
            s = json.load(open(f))["ligand"]["stereo_smiles"]
            edges.append({"lane": "RUNG 5a-KS", "edge_id": leg, "klass": "identity_pose",
                          "name_a": "5aks_d0", "smi_a": s, "name_b": "5aks_d", "smi_b": s,
                          "prefer_element_change": True})
    return edges


def run_bounds():
    rows = []
    for e in _edge_catalogue():
        b = edge_bounds(e["name_a"], e["smi_a"], e["name_b"], e["smi_b"])
        b.update({"lane": e["lane"], "edge_id": e["edge_id"], "class": e["klass"],
                  "prefer_element_change": e["prefer_element_change"]})
        rows.append(b)
        exp = b["expected_n_mapped_atoms"]
        print("[bounds] %-44s %-18s atoms %3d/%-3d heavy %2d/%-2d  complete=%-4s enforced_floor=%s"
              % (b["edge"][:44], e["lane"], b["n_atoms_a"], b["n_atoms_b"], b["n_heavy_a"], b["n_heavy_b"],
                 exp if exp is not None else "-", b.get("total_floor_enforced", "-")), flush=True)
    return rows


# ---- archive sweep (boto3 only) ------------------------------------------------------------------------------

_LOMAP_LINE = re.compile(r"LOMAP element_change=(True|False):\s+(\d+) mapped atoms for (\S+)->(\S+)")
_USING_LINE = re.compile(r"prefer_element_change -> using the (\d+)-atom map for (\S+)->(\S+)")
_MAPPED_LINE = re.compile(r"\[rbfe\] \S+: mapped (\d+) atoms A->B \((\S+)->(\S+)\)")
_TFEP_LINE = re.compile(r"\[tfep\] mapped (\d+) atoms A->B")


class Unreadable(RuntimeError):
    """The store could not be read. NOT the same as the object not existing — see leg_status_peek._get."""


def _iter_keys(s3, bucket, prefix):
    tok = None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []) or []:
            yield o["Key"], o["Size"], o["LastModified"]
        if not r.get("IsTruncated"):
            return
        tok = r.get("NextContinuationToken")


def run_archive():
    """Every archived artifact that records a map size, joined to nothing — the raw actuals."""
    try:
        import boto3
    except ImportError:
        raise Unreadable("boto3 unavailable")
    s3 = boto3.client("s3")
    found = []
    for prefix in ARCHIVE_PREFIXES:
        try:
            keys = list(_iter_keys(s3, BUCKET, prefix.strip().rstrip("/") + "/"))
        except Exception as e:  # noqa: BLE001 — credentials/permission/region MUST raise, never read as empty
            raise Unreadable("listing s3://%s/%s failed: %s: %s" % (BUCKET, prefix, type(e).__name__, e))
        print("[archive] s3://%s/%s -> %d objects" % (BUCKET, prefix, len(keys)), flush=True)
        for key, size, mtime in keys:
            base = os.path.basename(key)
            is_json = base.endswith(".json") and (base.startswith("leg") or base == "ddg.json")
            is_log = base.endswith(".log")
            if not (is_json or is_log) or size > 40 * 1024 * 1024:
                continue
            try:
                body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
            except Exception as e:  # noqa: BLE001
                found.append({"key": key, "status": "UNREADABLE", "error": "%s: %s" % (type(e).__name__, e)})
                continue
            if is_json:
                try:
                    d = json.loads(body)
                except Exception:  # noqa: BLE001
                    found.append({"key": key, "status": "UNREADABLE", "error": "not JSON"})
                    continue
                n = d.get("n_mapped_atoms")
                found.append({
                    "key": key, "kind": "leg_json", "mtime": str(mtime),
                    "n_mapped_atoms": n,
                    "status": "RECORDED" if n is not None else "UNRECORDED",
                    "ligand_a": d.get("ligand_a"), "ligand_b": d.get("ligand_b"),
                    "leg_id": d.get("leg_id"), "receptor": d.get("receptor"),
                    "dg_morph_kcal": d.get("dg_morph_kcal"), "ddg_bind_kcal": d.get("ddg_bind_kcal"),
                    "protocol_hash": (d.get("protocol_hash") or "")[:12] or None,
                    "mapping_setting": (d.get("protocol_settings") or {}).get("mapping"),
                })
            else:
                txt = body.decode("utf-8", "replace")
                per_setting = [{"element_change": m.group(1), "n_mapped": int(m.group(2)),
                                "a": m.group(3), "b": m.group(4)} for m in _LOMAP_LINE.finditer(txt)]
                used = [{"n_mapped": int(m.group(1)), "a": m.group(2), "b": m.group(3)}
                        for m in _USING_LINE.finditer(txt)]
                mapped = [{"n_mapped": int(m.group(1)), "a": m.group(2), "b": m.group(3)}
                          for m in _MAPPED_LINE.finditer(txt)]
                tfep = [int(m.group(1)) for m in _TFEP_LINE.finditer(txt)]
                degenerate = "DEGENERATE MAP" in txt
                if per_setting or used or mapped or tfep:
                    found.append({"key": key, "kind": "leg_log", "mtime": str(mtime),
                                  "lomap_per_setting": per_setting, "lomap_used": used,
                                  "rbfe_mapped": mapped, "tfep_mapped": tfep,
                                  "degenerate_warning_present": degenerate, "status": "RECORDED"})
                else:
                    found.append({"key": key, "kind": "leg_log", "mtime": str(mtime),
                                  "status": "UNRECORDED",
                                  "note": "log carries no [rbfe]/[tfep] map line — the leg died before the "
                                          "mapper, or the log was truncated"})
    for f in found:
        print("[archive] %-88s %s %s" % (f["key"][-88:], f.get("status"),
                                         f.get("n_mapped_atoms", f.get("lomap_used") or
                                               f.get("rbfe_mapped") or f.get("tfep_mapped") or "")), flush=True)
    return found


# ---- production-mapper re-derivation (needs openfe) ------------------------------------------------------------

def _component(openfe, Chem, smiles, name):
    from rdkit.Chem import AllChem
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    if AllChem.EmbedMolecule(m, randomSeed=0xF00D, maxAttempts=200) != 0:
        AllChem.EmbedMolecule(m, randomSeed=0xF00D, useRandomCoords=True, maxAttempts=200)
    try:
        AllChem.MMFFOptimizeMolecule(m, maxIters=300)
    except Exception:  # noqa: BLE001
        pass
    m.SetProp("_Name", name)
    return openfe.SmallMoleculeComponent.from_rdkit(m)


def run_maps():
    """Re-derive the PRODUCTION map for every edge at both budgets. The point is not to reproduce the failure
    (a CI runner is not the host that failed); it is to establish, on this repo's real chemistry, (a) what the
    correct map size is for every edge, and (b) whether 20 s is anywhere near sufficient."""
    import openfe
    from rdkit import Chem
    import nr4a3_rbfe as rbfe
    rows = []
    for e in _edge_catalogue():
        cA = _component(openfe, Chem, e["smi_a"], e["name_a"])
        cB = _component(openfe, Chem, e["smi_b"], e["name_b"])
        row = {"lane": e["lane"], "edge_id": e["edge_id"], "class": e["klass"],
               "edge": "%s->%s" % (e["name_a"], e["name_b"]),
               "prefer_element_change": e["prefer_element_change"]}
        import time as _time
        for budget in (20, 300):
            os.environ["RBFE_LOMAP_TIME_S"] = str(budget)
            t0 = _time.time()
            try:
                m = rbfe._mapping(openfe, cA, cB, prefer_element_change=e["prefer_element_change"])
                row["n_mapped_t%d" % budget] = len(m.componentA_to_componentB)
                row["err_t%d" % budget] = None
            except Exception as ex:  # noqa: BLE001
                row["n_mapped_t%d" % budget] = None
                row["err_t%d" % budget] = "%s: %s" % (type(ex).__name__, ex)
            row["wall_s_t%d" % budget] = round(_time.time() - t0, 2)
        rows.append(row)
        print("[maps] %-46s t20=%s (%.1fs)  t300=%s (%.1fs)"
              % (row["edge"][:46], row.get("n_mapped_t20"), row.get("wall_s_t20", 0.0),
                 row.get("n_mapped_t300"), row.get("wall_s_t300", 0.0)), flush=True)
    return rows


# ---- the verdict table --------------------------------------------------------------------------------------

# Observations this repo has already made and that do NOT live in S3, so the join would otherwise miss them.
# Each is a real reading with its provenance, not an assumption; per rule 1 the numbers point at their source.
_OFF_STORE_OBSERVATIONS = [
    {"lane": "valB_mini r0 (2 fs)", "leg": "calib_hi_to_lo__binary_vhl_fwd_r0", "edge_id": "calib_hi_to_lo",
     "n_mapped": 109, "source": "GH Actions run 30155238348 job 89811327292/89672043853 [LEG-TABLE] dump"},
    {"lane": "valB_mini r0 (2 fs)", "leg": "calib_hi_to_lo__solvent_fwd_r0", "edge_id": "calib_hi_to_lo",
     "n_mapped": 109, "source": "GH Actions run 30155238348 [LEG-TABLE] dump"},
    {"lane": "valB_mini r0 (2 fs)", "leg": "calib_hi_to_lo__ternary_vhl_fwd_r0", "edge_id": "calib_hi_to_lo",
     "n_mapped": 109, "source": "GH Actions run 30155238348 [LEG-TABLE] dump"},
    {"lane": "RUNG 2b timestep scan", "leg": "ANCHOR_calib_wurz_N_to_CH", "edge_id": "calib_hi_to_lo",
     "n_mapped": 47, "source": "congeneric-edge-timestep-table.json -> results[1].n_mapped_atoms"},
    {"lane": "RUNG 2b timestep scan", "leg": "ANCHOR_pilot_5Br_to_5NH2",
     "edge_id": "e_zaienne_cmpd19__cw_ev_5nh2", "n_mapped": 15,
     "source": "congeneric-edge-timestep-table.json -> results[0].n_mapped_atoms"},
    {"lane": "RUNG 5a-KS", "leg": "5aks_d0_to_d__ternary_nr4a3", "edge_id": "5aks_d0_to_d__ternary_nr4a3",
     "n_mapped": 111, "source": "nr4a3_5aks_ligand_diag.py docstring (preequil verify_endpoints)"},
    {"lane": "RUNG 5a-KS", "leg": "5aks_d0_to_d__ternary_nr4a1", "edge_id": "5aks_d0_to_d__ternary_nr4a1",
     "n_mapped": 80, "source": "nr4a3_5aks_ligand_diag.py docstring (preequil verify_endpoints ABORT)"},
]


def _bounds_index(report):
    idx = {}
    for b in report.get("bounds") or []:
        idx[b["edge_id"]] = b
    return idx


def run_verdict():
    """Join every observation to its edge's bounds and print the per-leg CLEAN / DEGENERATE / UNVERIFIABLE
    table. Merges every atom-map-audit*.json in the directory, because the archive sweep and the two parity
    images write separate files."""
    import glob as _glob
    merged = {}
    for f in sorted(_glob.glob(os.path.join(HERE, "atom-map-audit*.json"))):
        try:
            d = json.load(open(f))
        except Exception:  # noqa: BLE001
            continue
        for k, v in d.items():
            if k.startswith("_"):
                continue
            if k == "maps":
                merged.setdefault("maps", []).extend(v)
            else:
                merged.setdefault(k, v)
    bnd = _bounds_index(merged)
    rows = []

    def add(lane, leg, edge_id, n_mapped, source):
        b = bnd.get(edge_id)
        if b is None:
            rows.append({"lane": lane, "leg": leg, "edge_id": edge_id, "n_mapped": n_mapped,
                         "expected": None, "floor": None, "verdict": "UNVERIFIABLE",
                         "why": "no bounds computed for edge %r" % edge_id, "source": source})
            return
        v, why = classify(n_mapped, b)
        rows.append({"lane": lane, "leg": leg, "edge_id": edge_id, "n_mapped": n_mapped,
                     "expected": b.get("expected_n_mapped_atoms"), "floor": b.get("total_floor_enforced"),
                     "verdict": v, "why": why, "source": source})

    for o in _OFF_STORE_OBSERVATIONS:
        add(o["lane"], o["leg"], o["edge_id"], o["n_mapped"], o["source"])

    for a in merged.get("archive") or []:
        if a.get("kind") == "leg_json":
            add("S3 archive", a["key"], _edge_id_for(a, bnd), a.get("n_mapped_atoms"),
                "s3://%s/%s" % (BUCKET, a["key"]))
        elif a.get("kind") == "leg_log":
            for u in (a.get("lomap_used") or []) + (a.get("rbfe_mapped") or []):
                add("S3 archive (log)", a["key"], _edge_id_for(a, bnd, u), u["n_mapped"],
                    "s3://%s/%s" % (BUCKET, a["key"]))
            if a.get("status") == "UNRECORDED":
                add("S3 archive (log)", a["key"], "?", None, "s3://%s/%s" % (BUCKET, a["key"]))

    hdr = "%-24s %-52s %8s %9s %7s  %s" % ("lane", "leg", "n_mapped", "expected", "floor", "verdict")
    print("\n" + hdr)
    print("-" * len(hdr))
    for r in rows:
        print("%-24s %-52s %8s %9s %7s  %s" % (r["lane"][:24], str(r["leg"])[-52:],
                                               r["n_mapped"] if r["n_mapped"] is not None else "-",
                                               r["expected"] if r["expected"] is not None else "-",
                                               r["floor"] if r["floor"] is not None else "-", r["verdict"]))
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[verdict] " + "  ".join("%s=%d" % kv for kv in sorted(tally.items())), flush=True)
    return {"rows": rows, "tally": tally}


def _edge_id_for(artifact, bnd, hint=None):
    """Best-effort edge id for an S3 artifact, from the ligand names it recorded. Returns '?' when it cannot
    be established — which routes the row to UNVERIFIABLE rather than to a guessed edge."""
    a = (hint or {}).get("a") or artifact.get("ligand_a")
    b = (hint or {}).get("b") or artifact.get("ligand_b")
    if a and b:
        for eid, bb in bnd.items():
            if bb.get("node_a") == a and bb.get("node_b") == b:
                return eid
    key = artifact.get("key", "")
    for eid in bnd:
        if eid in key:
            return eid
    if "calib_hi_to_lo" in key:
        return "calib_hi_to_lo"
    return "?"


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "bounds").lower()
    prev = json.load(open(OUT)) if os.path.exists(OUT) else {}
    report = dict(prev)
    report["_what"] = ("atom-map blast-radius audit: what map size each archived alchemical leg actually used, "
                       "against the size provably achievable for its transformation")
    report["_no_spend"] = "no GPU, no instance, read-only against archives"
    if mode == "bounds":
        report["bounds"] = run_bounds()
    elif mode == "archive":
        report["archive"] = run_archive()
    elif mode == "maps":
        # bounds first: the maps run happens inside the parity image, and a re-derived map size is only
        # interpretable next to the floor it has to clear.
        report["bounds"] = run_bounds()
        report["maps"] = run_maps()
    elif mode == "verdict":
        report["verdict"] = run_verdict()
    elif mode == "all":
        report["bounds"] = run_bounds()
        try:
            report["archive"] = run_archive()
        except Unreadable as e:
            report["archive_error"] = str(e)
            print("[archive] UNREADABLE: %s" % e, flush=True)
        try:
            report["maps"] = run_maps()
        except ImportError as e:
            report["maps_error"] = "openfe unavailable: %s" % e
            print("[maps] SKIPPED — openfe unavailable (%s)" % e, flush=True)
    else:
        sys.exit("unknown mode %r (bounds | archive | maps | all)" % mode)
    json.dump(report, open(OUT, "w"), indent=2, default=str)
    print("[map-audit] wrote %s" % OUT, flush=True)


if __name__ == "__main__":
    main()
