#!/usr/bin/env python3
"""Read-only analysis of the retrospective NR-V04 / VHL ternary benchmark outputs in S3 (Track B).

The NR-V04 benchmark differs from the CRBN report_ternary.py in three ways, so it needs its own reader:
  * E3 is VHL (+ ElonginB/C) — FOUR protein chains, not two; report_ternary's "smaller=NR4A, larger=CRBN"
    assignment breaks. Here chains are identified by their YAML id: L=ligand, A=NR4A target, E=VHL, F/G=EloB/C
    (nr4a3_ternary.boltz_yaml preserves ids; nrv04_ternary.e3_chains sets VHL='E').
  * The positive control is VH032 seated in VHL's hydroxyproline pocket (Ser111/His115/Trp117), not
    lenalidomide in CRBN's tri-Trp.
  * Every system is an ENSEMBLE over diffusion seeds (control/seed_N, nr4a1/seed_N, ...). The readout is the
    DISTRIBUTION across seeds (ligand-iPTM, bridging, seed persistence), not a single pose.

PILOT GATE (nrv04-ternary-benchmark.json → single_leg_first_pilot): with only control + NR4A1 present, decide
  PROCEED  — control seats VH032 AND NR4A1 forms a productive, seed-persistent ternary → fan out NR4A2/NR4A3;
  ABORT    — control can't seat VH032 (workflow broken) OR NR4A1 can't form a productive ternary (can't even
             recover the known-degraded positive case) → don't spend on the full paralogue fleet.
When NR4A2/NR4A3 are also present (full run) it additionally applies the informative/inconclusive/failed
verdict_gate by comparing NR4A1 vs NR4A2/NR4A3 on the ensemble readouts.

CPU only (boto3 + gemmi). Env: AWS creds, OUTPUT_PREFIX (default nrv04-ternary-pilot). Writes a JSON summary to
$OUT (default report_nrv04.json) and prints a human table.
"""
import glob
import json
import os
import re
import statistics
import sys
import tempfile

STANDARD_AA = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
}
# VHL hydroxyproline (Hyp) pocket — the substrate sub-pocket that binds HIF-1α Hyp564 and every VHL-PROTAC's
# (2S,4R)-4-hydroxyproline (VH032 included). P40337 (pVHL) numbering; S111+H115 make the defining H-bonds.
VHL_HYP_POCKET = [98, 110, 111, 115, 117]     # Tyr98, His110, Ser111, His115, Trp117
VHL_SEAT_KEY = [111, 115]                       # seating requires proximity to these two
SEAT_CUTOFF = 4.5                               # Å; ligand heavy atom within this of a key pocket residue
BRIDGE_CUTOFF = 4.5                             # Å; ligand-to-protein contact defining a bridge
LYS_BINS = (8.0, 12.0, 16.0)                    # Å; target Lys NZ → VHL (ubiquitin-ACCESSIBILITY proxy; NOT SASA)
LIG_ID, NR4A_ID, VHL_ID = "L", "A", "E"
CUTOFFS = (4.0, 4.5, 5.0)                        # Å; contact cutoffs for cutoff-sensitivity (review fix 7)
DEFAULT_CUTOFF = 4.5
WRONG_END_MARGIN = 2.0                           # Å an end must be *closer* to the wrong protein to flag wrong-end
NR4A1_CYS = 551                                  # celastrol Michael-acceptor covalent target on NR4A1 (proxy only)
NR4A1_LBD_UNIPROT_FIRST = 345                    # NR4A1 P22736 (598 aa), LBD = last 254 → first UniProt res 345.
#                                                  UniProt 551 → local 207. UNVERIFIED against an output CIF —
#                                                  the analyzer emits cys551_evaluated=False unless a CYS is found
#                                                  at the mapped position (fail-closed; review fix #4).
CLASH_CUTOFF = 2.0                               # Å; heavy-atom–heavy-atom ligand↔protein distance flagged a clash
POCKET_OCC_CUTOFF = SEAT_CUTOFF                  # Å; recruiter-moiety atom within this of a Hyp-pocket residue = occupancy

# ---------------------------------------------------------------------------------------------------------
# ATOM-MAPPED MOIETIES (2nd external review, fix #2). The moiety decomposition is now defined on the ligand's
# CHEMICAL GRAPH (SMILES) via SMARTS, then mapped onto the CIF ligand atoms by an explicit, ARCHIVED atom-index
# mapping — replacing the conformation-dependent sulfur-anchor spatial partition. The SMILES per system come from
# the frozen benchmark spec (nrv04-ternary-benchmark.json). Overridable at runtime via prep_data['ligand_smiles'].
NRV04_PROTAC_SMILES = ("CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)NCCOCCOCCOCCOCCC"
                       "(=O)N[C@@H](C(C)(C)C)C(=O)N4C[C@H](O)C[C@H]4C(=O)NCc4ccc(-c5scnc5C)cc4)CC[C@]3(C)CC"
                       "[C@]12C")                                              # nrv04.representative_smiles
NRV04_INACTIVE_PROTAC_SMILES = ("CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)NCCOCCOCC"
                                "OCCOCCC(=O)N[C@@H](C(C)(C)C)C(=O)N4C[C@@H](O)C[C@H]4C(=O)NCc4ccc(-c5scnc5C)"
                                "cc4)CC[C@]3(C)CC[C@]12C")                     # Hyp (2S,4R)->(2S,4S) epimer PROTAC
FREE_CELASTROL_SMILES = ("CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)O)CC[C@]3(C)CC"
                         "[C@]12C")                                           # control_ligand_negatives.free_celastrol
SYSTEM_SMILES = {"nr4a1": NRV04_PROTAC_SMILES, "nr4a2": NRV04_PROTAC_SMILES, "nr4a3": NRV04_PROTAC_SMILES,
                 "neg_inactive": NRV04_INACTIVE_PROTAC_SMILES, "neg_celastrol": FREE_CELASTROL_SMILES}

# SMARTS defining the two chemical ends. Warhead = celastrol quinone-methide chromophore, then grown over the
# fused pentacyclic ring system + its terminal (methyl / =O / -OH) substituents. Recruiter (VH032) = the
# (2S,4R)-4-hydroxyproline ring + the 4-(4-methylthiazol-5-yl)phenyl group (stereo-agnostic SMARTS so the
# epimer control maps identically; stereochemistry is NOT a geometry criterion here).
_SMA_CHROM = "CC1=C(O)C(=O)C=C2C1=CC=C[C]2"      # celastrol 2-hydroxy quinone-methide chromophore
_SMA_THZ = "c1scnc1"                              # 4-methylthiazol-5-yl (required recruiter substructure)
_SMA_PHZ = "c1ccc(cc1)-c1scnc1C"                  # 4-(4-methylthiazol-5-yl)phenyl
_SMA_HYP = "[C]1C[C](O)C[N]1"                     # 4-hydroxyproline ring + OH (required recruiter substructure)


def _euclid(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _min_d(a_pts, b_pts):
    return None if not a_pts or not b_pts else min(_euclid(a, b) for a in a_pts for b in b_pts)


def split_ligand_ends(lig_atoms):
    """DEPRECATED / RETIRED — NO LONGER CALLED by moiety_geometry (2nd review, fix #2). The conformation-dependent
    sulfur-anchor spatial partition has been REPLACED by atom_map_moieties() (chemically-mapped, atom-index
    substructures). This function is retained only so its historical unit tests keep exercising the fail-closed
    contract; do not use it for any new analysis. It uses the ligand's single sulfur (thiazole, VHL half) as one
    spatial anchor and the farthest atom as the other, then partitions by 3-D distance — conformation-dependent
    and able to misassign atoms in a folded PROTAC. Returns (vhl_end_pts, nr4a_end_pts, note) or
    (None, None, fail_reason). `lig_atoms` = list of (element, (x,y,z))."""
    pts = [p for _, p in lig_atoms]
    sulfurs = [p for el, p in lig_atoms if el.upper() == "S"]
    if len(sulfurs) != 1 or len(pts) < 2:
        return None, None, "FAIL-CLOSED: sulfur-anchor unavailable (S count=%d); no whole-ligand fallback" % len(sulfurs)
    a_vhl = sulfurs[0]                                            # VH032/thiazole spatial anchor (PROVISIONAL)
    a_nr4a = max(pts, key=lambda p: _euclid(p, a_vhl))           # farthest atom (PROVISIONAL celastrol terminus)
    vhl_end, nr4a_end = [], []
    for p in pts:
        (vhl_end if _euclid(p, a_vhl) <= _euclid(p, a_nr4a) else nr4a_end).append(p)
    return vhl_end, nr4a_end, "PROVISIONAL sulfur-anchor split (conformation-dependent; not atom-mapped occupancy)"


def _ref_mol(smiles):
    """RDKit mol from a SMILES with only heavy atoms (implicit H). None on parse failure."""
    try:
        from rdkit import Chem
    except ImportError:
        return None
    m = Chem.MolFromSmiles(smiles) if smiles else None
    return None if m is None else Chem.RemoveHs(m)


def _fused_component(mol, seed, ringset):
    """All ring atoms in the fused ring system reachable from `seed` (staying within ring atoms)."""
    from collections import deque
    comp = set(a for a in seed if a in ringset)
    dq = deque(comp)
    while dq:
        x = dq.popleft()
        for nb in mol.GetAtomWithIdx(x).GetNeighbors():
            j = nb.GetIdx()
            if j in ringset and j not in comp:
                comp.add(j); dq.append(j)
    return comp


def _moiety_ref_sets(mol):
    """Warhead / recruiter / linker atom-index sets on the SMILES graph (review fix #2). Returns dict with the
    three index sets (SMILES/ref indices) plus has_warhead / has_recruiter flags for the REQUIRED substructures.
    Warhead = celastrol quinone-methide chromophore grown over its fused ring system + terminal substituents;
    recruiter = (4-methylthiazol-5-yl)phenyl ∪ 4-hydroxyproline; linker = everything else (PEG + the two amides)."""
    from rdkit import Chem
    ring = set(a for r in mol.GetRingInfo().AtomRings() for a in r)
    chrom = mol.GetSubstructMatch(Chem.MolFromSmarts(_SMA_CHROM))
    has_warhead = bool(chrom)
    warhead = set()
    if chrom:
        warhead = _fused_component(mol, chrom, ring)
        for a in list(warhead):                                   # add terminal methyl / =O / -OH substituents
            for nb in mol.GetAtomWithIdx(a).GetNeighbors():
                if nb.GetIdx() in warhead:
                    continue
                if nb.GetSymbol() == "O" or (nb.GetSymbol() == "C" and nb.GetDegree() == 1):
                    warhead.add(nb.GetIdx())
    has_thz = bool(mol.GetSubstructMatch(Chem.MolFromSmarts(_SMA_THZ)))
    has_hyp = bool(mol.GetSubstructMatch(Chem.MolFromSmarts(_SMA_HYP)))
    has_recruiter = has_thz and has_hyp
    recruiter = set()
    for sm in (_SMA_PHZ, _SMA_HYP):
        for mm in mol.GetSubstructMatches(Chem.MolFromSmarts(sm)):
            recruiter.update(mm)
    recruiter -= warhead                                          # keep the two ends disjoint (no overlap expected)
    linker = set(range(mol.GetNumAtoms())) - warhead - recruiter
    return {"warhead": warhead, "recruiter": recruiter, "linker": linker,
            "has_warhead": has_warhead, "has_recruiter": has_recruiter}


def _map_by_bond_perception(mol, cif_atoms):
    """FALLBACK mapping when the CIF heavy-atom order does NOT match the SMILES order: build a mol from the CIF
    element+coords, perceive CONNECTIVITY (rdDetermineBonds), and graph-match the SMILES graph onto it. Returns
    mapping[ref_idx] = cif_idx or None. Best-effort: any failure → None (caller FAILS CLOSED)."""
    try:
        from rdkit import Chem
        from rdkit.Geometry import Point3D
        from rdkit.Chem import rdDetermineBonds
        rw = Chem.RWMol()
        for el, _ in cif_atoms:
            rw.AddAtom(Chem.Atom(el))
        conf = Chem.Conformer(rw.GetNumAtoms())
        for i, (_, (x, y, z)) in enumerate(cif_atoms):
            conf.SetAtomPosition(i, Point3D(float(x), float(y), float(z)))
        cm = rw.GetMol()
        cm.AddConformer(conf, assignId=True)
        rdDetermineBonds.DetermineConnectivity(cm)                # connectivity only (bond orders unreliable here)
        # graph query ignoring bond order / aromaticity so a connectivity-only cif mol can still match the SMILES
        params = Chem.AdjustQueryParameters.NoAdjustments()
        params.makeBondsGeneric = True
        params.aromatizeIfPossible = False
        q = Chem.AdjustQueryProperties(Chem.Mol(mol), params)
        match = cm.GetSubstructMatch(q, useChirality=False)       # match[ref_idx] = cif_idx
        if match and len(match) == mol.GetNumAtoms():
            return list(match)
    except Exception:  # noqa: BLE001
        return None
    return None


def atom_map_moieties(smiles, cif_atoms):
    """Establish an explicit, ARCHIVED atom-index mapping between the ligand SMILES graph and the CIF ligand atoms,
    then project the chemically-defined warhead / recruiter / linker sets onto CIF indices (review fix #2).

    `cif_atoms` = ordered list of (element, (x,y,z)) heavy atoms as read from the CIF ligand block.

    Mapping strategy (FAIL CLOSED — never a spatial/whole-ligand fallback):
      1. Parse SMILES → heavy-atom ref graph; require the element MULTISET to match the CIF ligand exactly.
      2. PRIMARY (atom_order): Boltz-2 writes ligand heavy atoms in the RDKit/SMILES input order. We only trust
         the identity map when the ORDERED element sequences are identical — an exact, verifiable check. If they
         differ we do NOT assume identity.
      3. FALLBACK (bond_perception): perceive CIF connectivity and graph-match the SMILES onto it.
      4. If neither yields a full mapping → {"ok": False, ...} and the caller returns unmapped/fail-closed.
    Returns a dict; on success has keys ok, method, mapping (list[ref]->cif), warhead_cif/recruiter_cif/linker_cif,
    has_warhead, has_recruiter, n_ref, n_cif."""
    from collections import Counter
    mol = _ref_mol(smiles)
    if mol is None:
        return {"ok": False, "method": None, "mapping": None,
                "reason": "FAIL-CLOSED: RDKit unavailable or could not parse ligand SMILES"}
    ref_elems = [a.GetSymbol().upper() for a in mol.GetAtoms()]
    cif_elems = [el.upper() for el, _ in cif_atoms]
    if len(cif_elems) < 2:
        return {"ok": False, "method": None, "mapping": None, "reason": "FAIL-CLOSED: <2 CIF ligand heavy atoms"}
    if Counter(ref_elems) != Counter(cif_elems):
        return {"ok": False, "method": None, "mapping": None,
                "reason": "FAIL-CLOSED: element composition mismatch (SMILES %s vs CIF %s)"
                          % (dict(Counter(ref_elems)), dict(Counter(cif_elems)))}
    if ref_elems == cif_elems:
        mapping, method = list(range(len(ref_elems))), "atom_order"
    else:
        mapping = _map_by_bond_perception(mol, cif_atoms)
        method = "bond_perception" if mapping is not None else None
    if mapping is None:
        return {"ok": False, "method": None, "mapping": None,
                "reason": ("FAIL-CLOSED: SMILES↔CIF atom mapping could not be established (CIF heavy-atom order "
                           "differs from SMILES order and bond-perception graph match failed)")}
    sets = _moiety_ref_sets(mol)
    to_cif = lambda refset: sorted(mapping[i] for i in refset)
    return {"ok": True, "method": method, "mapping": mapping, "n_ref": len(ref_elems), "n_cif": len(cif_elems),
            "reason": "mapped via %s (element multiset matched)" % method,
            "warhead_cif": to_cif(sets["warhead"]), "recruiter_cif": to_cif(sets["recruiter"]),
            "linker_cif": to_cif(sets["linker"]), "has_warhead": sets["has_warhead"],
            "has_recruiter": sets["has_recruiter"]}


def _centroid(pts):
    n = len(pts)
    return None if not n else (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)


def _moiety_metrics(warhead_pts, recruiter_pts, linker_pts, lig_pts, nr4a_pts, vhl_pts, pocket_pts,
                    has_warhead, has_recruiter, cutoffs=CUTOFFS):
    """Pure geometry core (no gemmi) so the occupancy logic is unit-testable. Consumes already-projected point
    lists for each mapped moiety and each protein partner; returns the moiety-bridging + intended-site occupancy
    fields (review fixes #2 + #3). moiety_bridges is a dict per cutoff ONLY when BOTH ends are mapped; otherwise
    None (fail-closed for the correct-half criterion) while occupancy fields are still reported."""
    d_w_nr = _min_d(warhead_pts, nr4a_pts)
    d_w_vhl = _min_d(warhead_pts, vhl_pts)
    d_r_vhl = _min_d(recruiter_pts, vhl_pts)
    d_r_nr = _min_d(recruiter_pts, nr4a_pts)
    prot_pts = nr4a_pts + vhl_pts
    d_lnk_prot = _min_d(linker_pts, prot_pts)
    d_w_prot = _min_d(warhead_pts, prot_pts)
    d_r_prot = _min_d(recruiter_pts, prot_pts)
    d_rec_pocket = _min_d(recruiter_pts, pocket_pts)
    both = bool(has_warhead and has_recruiter)
    # correct-half dual-surface proximity: celastrol end contacts NR4A AND recruiter end contacts VHL
    bridges = None
    if both:
        bridges = {}
        for c in cutoffs:
            bridges["%.1f" % c] = bool(d_w_nr is not None and d_r_vhl is not None and d_w_nr <= c and d_r_vhl <= c)
    # wrong-end: a mapped end sits clearly closer to the protein it should NOT engage
    wrong_end = bool((d_w_vhl is not None and d_w_nr is not None and d_w_vhl + WRONG_END_MARGIN < d_w_nr)
                     or (d_r_nr is not None and d_r_vhl is not None and d_r_nr + WRONG_END_MARGIN < d_r_vhl))
    # review fix #3 — INTENDED-SITE occupancy (not any-surface proximity)
    recruiter_pocket_occupancy = bool(has_recruiter and d_rec_pocket is not None and d_rec_pocket <= POCKET_OCC_CUTOFF)
    warhead_site_occupancy = bool(has_warhead and d_w_nr is not None and d_w_nr <= DEFAULT_CUTOFF)
    linker_only_contact = bool(d_lnk_prot is not None and d_lnk_prot <= DEFAULT_CUTOFF
                               and (d_w_prot is None or d_w_prot > DEFAULT_CUTOFF)
                               and (d_r_prot is None or d_r_prot > DEFAULT_CUTOFF))
    clashes = sum(1 for a in lig_pts for b in prot_pts if _euclid(a, b) < CLASH_CUTOFF)
    w_c, r_c = _centroid(warhead_pts), _centroid(recruiter_pts)
    e2e = _euclid(w_c, r_c) if (w_c and r_c) else None
    ext = round(len(linker_pts) * 1.3, 1) if linker_pts else None
    strain = {"warhead_recruiter_centroid_A": None if e2e is None else round(e2e, 2),
              "n_linker_atoms": len(linker_pts), "extended_estimate_A": ext,
              "compaction_ratio": None if (e2e is None or not ext) else round(e2e / ext, 2),
              "note": "crude end-to-end vs extended-length proxy; NOT a force-field strain energy; not in verdict"}
    out = {"moiety_bridges": bridges,
           "moiety_bridges_default": None if bridges is None else bridges["%.1f" % DEFAULT_CUTOFF],
           "wrong_end": wrong_end,
           "celastrol_end_to_NR4A_A": None if d_w_nr is None else round(d_w_nr, 2),
           "celastrol_end_to_VHL_A": None if d_w_vhl is None else round(d_w_vhl, 2),
           "vh032_end_to_VHL_A": None if d_r_vhl is None else round(d_r_vhl, 2),
           "vh032_end_to_NR4A_A": None if d_r_nr is None else round(d_r_nr, 2),
           # review fix #3 fields (separate booleans/distances — intended site, not any surface)
           "recruiter_pocket_occupancy": recruiter_pocket_occupancy,
           "recruiter_pocket_min_A": None if d_rec_pocket is None else round(d_rec_pocket, 2),
           "warhead_site_occupancy": warhead_site_occupancy,
           "warhead_site_defined": False,        # no NR4A pocket residues defined → LBD-contact proxy only
           "warhead_to_NR4A_min_A": None if d_w_nr is None else round(d_w_nr, 2),
           "linker_only_contact": linker_only_contact,
           "linker_to_protein_min_A": None if d_lnk_prot is None else round(d_lnk_prot, 2),
           "steric_clashes": clashes,
           "linker_strain_proxy": strain,
           "_warhead_site_note": ("warhead-moiety contact to the NR4A LBD (BRIDGE_CUTOFF); the SPECIFIC NR4A "
                                  "site is NOT defined — no pocket residues provided (fail-open flag, not a claim)")}
    return out


def _ligand_atoms_ordered(model):
    """Heavy-atom (element, (x,y,z)) list for the LIGAND in CIF atom order. Prefers the designated ligand chain
    (LIG_ID='L'); falls back to all non-standard residues. Order is the CIF write order — the index space the
    SMILES↔CIF mapping assumes."""
    lchain = None
    for chain in model:
        if chain.name == LIG_ID:
            lchain = chain; break
    out = []
    if lchain is not None:
        for res in lchain:
            for a in res:
                if a.element.name != "H":
                    out.append((a.element.name, (a.pos.x, a.pos.y, a.pos.z)))
        if out:
            return out
    for chain in model:
        for res in chain:
            if res.name not in STANDARD_AA:
                for a in res:
                    if a.element.name != "H":
                        out.append((a.element.name, (a.pos.x, a.pos.y, a.pos.z)))
    return out


def moiety_geometry(model, ligand_smiles=None, cutoffs=CUTOFFS, is_nr4a1=False):
    """Moiety-SPECIFIC ternary read (review fixes #2 + #3): ATOM-MAPPED chemical moieties (not a spatial anchor).
    Establishes a SMILES↔CIF atom-index mapping (atom_map_moieties, archived), then asks whether the celastrol
    WARHEAD contacts the NR4A target AND the VH032 RECRUITER contacts VHL — via the correct chemical ends, not a
    wrong-end/linker/surface contact. Also reports intended-SITE occupancy (recruiter in the VHL Hyp pocket;
    warhead at the NR4A LBD), a linker-only/nonspecific flag, steric clashes, and a crude linker-strain proxy.
    FAILS CLOSED to {"moiety_bridges": None, "unmapped": True, ...} if the mapping or a required substructure is
    missing — NEVER a whole-ligand or spatial-only fallback. (NR4A1 only) adds the celastrol-end→Cys551-SG
    distance as a covalent-geometry PROXY."""
    prot, _lig = _chains(model)
    nr4a = prot.get(NR4A_ID)
    vhl = prot.get(VHL_ID)
    if nr4a is None or vhl is None:
        big = sorted(prot.items(), key=lambda kv: len(kv[1]), reverse=True)[:2]
        if len(big) < 2:
            return {"moiety_bridges": None, "unmapped": True, "note": "fewer than 2 protein chains"}
        nr4a, vhl = big[0][1], big[1][1]
    cif_atoms = _ligand_atoms_ordered(model)
    if len(cif_atoms) < 2:
        return {"moiety_bridges": None, "unmapped": True, "note": "no ligand atoms"}
    if not ligand_smiles:
        return {"moiety_bridges": None, "unmapped": True,
                "note": "FAIL-CLOSED: no ligand SMILES provided — cannot atom-map moieties (review fix #2)"}
    am = atom_map_moieties(ligand_smiles, cif_atoms)
    if not am.get("ok"):                                          # FAIL CLOSED — no whole-ligand/spatial fallback
        return {"moiety_bridges": None, "unmapped": True, "note": am.get("reason"),
                "atom_map": {"ok": False, "reason": am.get("reason"), "method": None}}
    nr4a_pts = [(p.x, p.y, p.z) for p in _atoms(nr4a)]
    vhl_pts = [(p.x, p.y, p.z) for p in _atoms(vhl)]
    pocket_pts = [(p.x, p.y, p.z) for atoms in _pocket_atoms(vhl, VHL_HYP_POCKET).values() for p in atoms]
    warhead_pts = [cif_atoms[i][1] for i in am["warhead_cif"]]
    recruiter_pts = [cif_atoms[i][1] for i in am["recruiter_cif"]]
    linker_pts = [cif_atoms[i][1] for i in am["linker_cif"]]
    lig_pts = [p for _, p in cif_atoms]
    out = _moiety_metrics(warhead_pts, recruiter_pts, linker_pts, lig_pts, nr4a_pts, vhl_pts, pocket_pts,
                          am["has_warhead"], am["has_recruiter"], cutoffs=cutoffs)
    out["atom_map"] = {"ok": True, "method": am["method"], "reason": am["reason"],
                       "n_ref": am["n_ref"], "n_cif": am["n_cif"], "mapping": am["mapping"],
                       "n_warhead": len(am["warhead_cif"]), "n_recruiter": len(am["recruiter_cif"]),
                       "n_linker": len(am["linker_cif"]), "has_warhead": am["has_warhead"],
                       "has_recruiter": am["has_recruiter"]}
    out["split"] = ("atom-mapped moiety occupancy (SMILES↔CIF %s map; warhead=%d, recruiter=%d, linker=%d atoms)"
                    % (am["method"], len(am["warhead_cif"]), len(am["recruiter_cif"]), len(am["linker_cif"])))
    if out["moiety_bridges"] is None:                            # a required end substructure was absent → fail closed
        missing = [n for n, ok in (("warhead", am["has_warhead"]), ("recruiter", am["has_recruiter"])) if not ok]
        out["unmapped"] = True
        out["note"] = ("FAIL-CLOSED for correct-half bridging: required %s substructure not matched — this is the "
                       "no-%s architecture (e.g. free-warhead negative); occupancy fields still reported"
                       % (" & ".join(missing), missing[0] if missing else "moiety"))
    if is_nr4a1:
        # Cys551 covalent proxy (review fix #4): the LBD chain is renumbered by the co-fold, so UniProt 551 must
        # be MAPPED to the local index and the residue identity VERIFIED. NR4A1 (P22736, 598 aa) LBD = last 254
        # residues → first UniProt residue = 598-254+1 = 345 → local = 551-345+1 = 207. Emit the distance ONLY
        # if a residue is found at that mapped position AND it is a CYS; otherwise record NOT-evaluated with the
        # reason (never a misleading proxy). Also accepts direct numbering if the CIF preserved UniProt numbers.
        cys_hit = None
        for name, num, a in nr4a:
            if name == "CYS" and "SG" in a and num in (NR4A1_CYS, NR4A1_CYS - NR4A1_LBD_UNIPROT_FIRST + 1):
                cys_hit = a["SG"]; break
        if cys_hit is not None and warhead_pts:
            out["celastrol_end_to_Cys551_A"] = round(_min_d(warhead_pts, [(cys_hit.x, cys_hit.y, cys_hit.z)]), 2)
            out["cys551_evaluated"] = True
            out["_cys551_note"] = "covalent-geometry PROXY (no covalent bond modeled); celastrol-end min dist to Cys551 SG"
        else:
            out["cys551_evaluated"] = False
            out["_cys551_note"] = ("NOT evaluated: no CYS found at UniProt-551 (local %d) — residue-offset mapping "
                                   "unverified against this CIF; covalent geometry not assessed" % (NR4A1_CYS - NR4A1_LBD_UNIPROT_FIRST + 1))
    return out


def _download(prefix, dest):
    import boto3
    s3 = boto3.client("s3")
    bucket = f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')}-" \
             f"{boto3.client('sts').get_caller_identity()['Account']}"
    n = 0
    for page in boto3.client("s3").get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            local = os.path.join(dest, key[len(prefix):].lstrip("/"))
            os.makedirs(os.path.dirname(local), exist_ok=True)
            s3.download_file(bucket, key, local)
            n += 1
    print(f"downloaded {n} objects from s3://{bucket}/{prefix}", flush=True)
    return n, bucket


def _chains(model):
    """{chain_id: [(resname, resnum, {atom: pos})]} for protein chains, plus ligand heavy-atom positions."""
    prot, lig = {}, []
    for chain in model:
        residues = []
        for res in chain:
            if res.name in STANDARD_AA:
                residues.append((res.name, res.seqid.num, {a.name: a.pos for a in res if a.element.name != "H"}))
            else:
                lig.extend(a.pos for a in res if a.element.name != "H")
        if residues:
            prot[chain.name] = residues
    return prot, lig


def _min_dist(a, b):
    return None if not a or not b else min(pa.dist(pb) for pa in a for pb in b)


def _atoms(residues):
    return [p for _, _, atoms in residues for p in atoms.values()]


def _pocket_atoms(vhl, wanted):
    out = {}
    for name, num, atoms in vhl:
        if num in wanted:
            out[num] = list(atoms.values())
    return out


def seat_geometry(model):
    """Control read: closest approach of the ligand (VH032) to VHL's hydroxyproline pocket. SEATED iff within
    SEAT_CUTOFF of BOTH key residues (S111, H115)."""
    prot, lig = _chains(model)
    vhl = prot.get(VHL_ID) or (max(prot.values(), key=len) if prot else [])
    if not lig or not vhl:
        return {"seated": None, "note": "no ligand or VHL chain"}
    pocket = _pocket_atoms(vhl, VHL_HYP_POCKET)
    dists = {num: _min_dist(lig, atoms) for num, atoms in pocket.items()}
    key_ok = all(dists.get(k) is not None and dists[k] <= SEAT_CUTOFF for k in VHL_SEAT_KEY)
    closest = min((d for d in dists.values() if d is not None), default=None)
    return {"seated": bool(key_ok), "closest_pocket_A": None if closest is None else round(closest, 2),
            "per_residue_A": {int(k): (None if v is None else round(v, 2)) for k, v in dists.items()}}


def bridge_geometry(model):
    """NR4A1 ternary read: does NR-V04 bridge the NR4A target (chain A) and VHL (chain E), and how close is the
    nearest exposed target Lys NZ to VHL (ubiquitin-reach proxy)?"""
    prot, lig = _chains(model)
    nr4a = prot.get(NR4A_ID)
    vhl = prot.get(VHL_ID)
    if nr4a is None or vhl is None:
        # fall back: two largest protein chains are target + VHL (EloB/C are ~112-118 aa, smaller)
        big = sorted(prot.items(), key=lambda kv: len(kv[1]), reverse=True)[:2]
        if len(big) < 2:
            return {"bridges": None, "note": "fewer than 2 protein chains"}
        nr4a, vhl = big[0][1], big[1][1]
    d_nr4a = _min_dist(lig, _atoms(nr4a))
    d_vhl = _min_dist(lig, _atoms(vhl))
    bridges = d_nr4a is not None and d_vhl is not None and d_nr4a <= BRIDGE_CUTOFF and d_vhl <= BRIDGE_CUTOFF
    lys = [(num, atoms["NZ"]) for name, num, atoms in nr4a if name == "LYS" and "NZ" in atoms]
    vhl_atoms = _atoms(vhl)
    closest_lys = None
    if lys:
        cand = sorted(((num, _min_dist([nz], vhl_atoms)) for num, nz in lys), key=lambda t: (t[1] is None, t[1]))
        closest_lys = {"resnum": int(cand[0][0]), "dist_A": round(cand[0][1], 2),
                       "counts": {f"{b:g}A": sum(1 for _, d in cand if d is not None and d <= b) for b in LYS_BINS}}
    return {"bridges": bool(bridges), "lig_to_target_A": None if d_nr4a is None else round(d_nr4a, 2),
            "lig_to_vhl_A": None if d_vhl is None else round(d_vhl, 2), "n_lys": len(lys),
            "closest_exposed_lys": closest_lys}


_RANK_RE = re.compile(r"model_(\d+)")


def _rank_of(path):
    m = _RANK_RE.search(os.path.basename(path))
    return int(m.group(1)) if m else 0


def _all_models(seed_dir):
    """ALL generated ranks under a seed dir (review fix 7: analyze every sample, not just model_0).
    Returns [(rank, cif_path, confidence_dict_or_None)] sorted by rank."""
    cifs = sorted(glob.glob(os.path.join(seed_dir, "**", "*_model_*.cif"), recursive=True)) \
        or sorted(glob.glob(os.path.join(seed_dir, "**", "*.cif"), recursive=True))
    keys = ("confidence_score", "ptm", "iptm", "ligand_iptm", "protein_iptm", "complex_plddt", "complex_iplddt")
    out = []
    for cif in cifs:
        rank = _rank_of(cif)
        conf = None
        cdir = os.path.dirname(cif)
        cand = glob.glob(os.path.join(cdir, "confidence*model_%d*.json" % rank)) \
            or glob.glob(os.path.join(cdir, "**", "confidence*model_%d*.json" % rank), recursive=True)
        if cand:
            try:
                d = json.load(open(cand[0]))
                conf = {k: round(d[k], 4) for k in keys if isinstance(d.get(k), (int, float))}
            except Exception:  # noqa: BLE001
                conf = None
        out.append((rank, cif, conf))
    return out


def analyse_system(root, system, kind, ligand_smiles=None):
    """Walk system/seed_*/ dirs; per seed AND per rank collect confidence + whole-ligand geometry + (ternary)
    atom-mapped moiety geometry; aggregate over ALL samples (seed × rank). `ligand_smiles` (the ligand for THIS
    system) is required for the ternary atom-map; if None we fall back to the frozen SYSTEM_SMILES by name and,
    failing that, moiety_geometry fails closed (unmapped)."""
    import gemmi
    sysdir = os.path.join(root, system)
    seed_dirs = sorted(glob.glob(os.path.join(sysdir, "seed_*")))
    if not seed_dirs:
        seed_dirs = sorted(set(os.path.dirname(os.path.dirname(p))
                               for p in glob.glob(os.path.join(root, "**", system, "seed_*", "**"), recursive=True)))
    is_nr4a1 = (system.lower() == "nr4a1")
    smiles = ligand_smiles or SYSTEM_SMILES.get(system.lower())
    samples = []
    for sd in seed_dirs:
        seed = os.path.basename(sd)
        for rank, cif, conf in _all_models(sd):
            model = gemmi.read_structure(cif)[0]
            rec = {"seed": seed, "rank": rank, "confidence": conf}
            if kind == "control":
                rec["geometry"] = seat_geometry(model)
            else:
                rec["geometry"] = bridge_geometry(model)                     # whole-ligand (kept for comparison)
                rec["moiety"] = moiety_geometry(model, ligand_smiles=smiles, is_nr4a1=is_nr4a1)   # atom-mapped (primary)
            samples.append(rec)
    n_seeds = len(set(s["seed"] for s in samples))
    return {"system": system, "kind": kind, "n_seeds": n_seeds, "n_samples": len(samples),
            "samples": samples, "per_seed": samples,   # per_seed kept as alias for back-compat readers
            "ensemble": _aggregate(samples, kind)}


def _vals(per_seed, path):
    out = []
    for s in per_seed:
        d = s
        for p in path:
            d = (d or {}).get(p) if isinstance(d, dict) else None
        if isinstance(d, (int, float)):
            out.append(d)
    return out


def _frac(flags):
    flags = [bool(x) for x in flags if x is not None]
    return (None, 0, 0) if not flags else (round(sum(flags) / len(flags), 3), sum(flags), len(flags))


def _aggregate(samples, kind):
    lig_iptm = _vals(samples, ["confidence", "ligand_iptm"])
    iptm = _vals(samples, ["confidence", "iptm"])
    agg = {"ligand_iptm": _dist(lig_iptm), "iptm": _dist(iptm), "n_samples": len(samples),
           "n_seeds": len(set(s["seed"] for s in samples))}
    if kind == "control":
        f, n, d = _frac([s["geometry"].get("seated") for s in samples if s.get("geometry")])
        agg["seated_fraction"], agg["n_seated"], agg["n_scored"] = f, n, d
        return agg
    # whole-ligand bridging (kept ONLY for comparison — the review flagged it can pass on wrong-end contacts)
    f, n, d = _frac([s["geometry"].get("bridges") for s in samples if s.get("geometry")])
    agg["whole_ligand_bridged_fraction"], agg["n_bridged_wholeligand"], agg["n_scored"] = f, n, d
    # correct-half dual-surface proximity (renamed from 'moiety/productive'; NOT chemically-mapped occupancy).
    # FAIL-CLOSED samples (unmapped: moiety_bridges is None) are counted + EXCLUDED, never treated as a bridge.
    moi = [s.get("moiety") for s in samples if s.get("moiety") and s["moiety"].get("moiety_bridges")]
    agg["n_unmapped"] = sum(1 for s in samples if s.get("moiety") and s["moiety"].get("moiety_bridges") is None)
    agg["n_poses"] = len(samples)
    dk = "%.1f" % DEFAULT_CUTOFF
    # POSE-level fractions (poses within a seed are NESTED/correlated — report but do NOT treat as independent n).
    agg["pose_level_fraction"] = {}
    for c in CUTOFFS:
        key = "%.1f" % c
        f, n, d = _frac([m["moiety_bridges"].get(key) for m in moi])
        agg["pose_level_fraction"][key] = {"fraction": f, "n_bridged": n, "n_poses": d}
    wf, wn, wd = _frac([m.get("wrong_end") for m in moi])
    agg["wrong_end_fraction"], agg["n_wrong_end"] = wf, wn
    # INTENDED-SITE occupancy summaries (review fix #3) — over ALL samples whose moiety was atom-mapped (occupancy
    # fields exist even when moiety_bridges is None, e.g. free-warhead negative). Reported separately from bridging.
    occ = [s.get("moiety") for s in samples if s.get("moiety") and s["moiety"].get("atom_map", {}).get("ok")]
    def _occ_frac(key):
        fr, nn, dd = _frac([m.get(key) for m in occ if key in m])
        return {"fraction": fr, "n": nn, "n_scored": dd}
    agg["recruiter_pocket_occupancy_fraction"] = _occ_frac("recruiter_pocket_occupancy")
    agg["warhead_site_occupancy_fraction"] = _occ_frac("warhead_site_occupancy")
    agg["linker_only_contact_fraction"] = _occ_frac("linker_only_contact")
    agg["steric_clashes"] = _dist([m["steric_clashes"] for m in occ if isinstance(m.get("steric_clashes"), int)])
    agg["occupancy_caveat"] = ("intended-SITE occupancy: recruiter within the canonical VHL Hyp pocket (98/110/111/"
                               "115/117); warhead in LBD-contact of NR4A (specific NR4A site NOT defined); "
                               "linker-only flags nonspecific-surface contacts. Separate from the bridging metric.")
    # SEED-LEVEL (the primary sampling unit; review fix #6 — no pose pseudoreplication). Per seed: within-seed
    # pose-bridge fraction; a seed COUNTS as bridged if a MAJORITY of its poses bridge at the default cutoff.
    per_seed = {}
    for s in samples:
        m = s.get("moiety")
        if m and m.get("moiety_bridges"):
            per_seed.setdefault(s["seed"], []).append(bool(m["moiety_bridges"].get(dk)))
    agg["per_seed_pose_fraction"] = {k: round(sum(v) / len(v), 3) for k, v in per_seed.items()}
    seed_bridged = [1 if (sum(v) / len(v)) >= 0.5 else 0 for v in per_seed.values()]
    agg["n_seeds_scored"] = len(seed_bridged)
    agg["seed_bridged_fraction"] = round(sum(seed_bridged) / len(seed_bridged), 3) if seed_bridged else None
    # primary readout is now SEED-level; keep the old key name mapped to it for downstream compatibility.
    agg["moiety_bridged_default"] = agg["seed_bridged_fraction"]
    agg["denominator"] = "seeds=%d, poses=%d, unmapped=%d" % (agg["n_seeds"], agg["n_poses"], agg["n_unmapped"])
    # ubiquitin-ACCESSIBILITY proxy (NOT solvent-accessibility): min Lys-NZ→VHL. Relabelled + demoted from the
    # verdict per review fix 5 (analyzer computes no SASA; per-seed ordering is inconsistent).
    lysd = [s["geometry"]["closest_exposed_lys"]["dist_A"] for s in samples
            if s.get("geometry") and s["geometry"].get("closest_exposed_lys")]
    agg["lys_nz_to_vhl_A"] = _dist(lysd)
    agg["lys_caveat"] = "min Lys-NZ→VHL over ALL modeled lysines (no SASA); crude accessibility proxy, NOT in verdict"
    # celastrol-end→Cys551 covalent-geometry proxy (NR4A1 only)
    cys = [s["moiety"]["celastrol_end_to_Cys551_A"] for s in samples
           if s.get("moiety") and s["moiety"].get("celastrol_end_to_Cys551_A") is not None]
    if cys:
        agg["celastrol_end_to_Cys551_A"] = _dist(cys)
    return agg


def _dist(xs):
    if not xs:
        return None
    return {"n": len(xs), "mean": round(statistics.mean(xs), 4), "min": round(min(xs), 4),
            "max": round(max(xs), 4), "sd": round(statistics.pstdev(xs), 4) if len(xs) > 1 else 0.0}


def pilot_verdict(control, nr4a1):
    """Encode single_leg_first_pilot: PROCEED / ABORT / NOT-EVALUATED for the control+NR4A1 pilot.
    A control that is ABSENT BY DESIGN (e.g. a --targets fan-out / --skip-control run) must report
    NOT-EVALUATED — not ABORT/'workflow suspect' (review fix #8): missing-by-design ≠ failure."""
    c = control["ensemble"] if control else {}
    n = nr4a1["ensemble"] if nr4a1 else {}
    if not control or not nr4a1:
        missing = [x for x, present in (("control", bool(control)), ("NR4A1", bool(nr4a1))) if not present]
        return {"verdict": "not-evaluated", "reason": "not part of this run (absent by design): %s" % ", ".join(missing),
                "control_ok": None, "nr4a1_ok": None}
    control_ok = (c.get("seated_fraction") or 0) >= 0.5
    nr4a1_ok = (n.get("moiety_bridged_default") or 0) >= 0.5   # correct-half dual-surface proximity, majority of samples
    if control_ok and nr4a1_ok:
        verdict, reason = "PROCEED", ("control seats VH032 in VHL (%s/%s samples) AND NR4A1 meets the correct-half "
                                      "dual-surface proximity criterion (fraction %.2f at %.1f Å). NOTE: this is an "
                                      "architecture-feasibility gate ONLY — not a binding/affinity gate." %
                                      (c.get("n_seated"), c.get("n_scored"),
                                       n.get("moiety_bridged_default") or 0, DEFAULT_CUTOFF))
    else:
        bad = []
        if not control_ok:
            bad.append("VH032 control did NOT seat in VHL")
        if not nr4a1_ok:
            bad.append("NR4A1 (known-degraded) did NOT meet the correct-half dual-surface proximity criterion")
        verdict, reason = "ABORT", " ; ".join(bad) + " → architecture gate not met."
    return {"verdict": verdict, "reason": reason, "control_ok": control_ok, "nr4a1_ok": nr4a1_ok}


def _seed_bridged_fraction(system, cutoff_key, drop_seed=None):
    """SEED-level bridged fraction at a cutoff (review fix #6 — seed is the sampling unit, poses are nested):
    per seed take the majority-of-poses bridge call, then the fraction of seeds that pass. `drop_seed` excludes
    one seed (for leave-one-seed-out). Returns None if no seeds are scorable."""
    per_seed = {}
    for s in system.get("samples", []):
        if drop_seed is not None and s["seed"] == drop_seed:
            continue
        m = s.get("moiety")
        if m and m.get("moiety_bridges"):
            per_seed.setdefault(s["seed"], []).append(bool(m["moiety_bridges"].get(cutoff_key)))
    if not per_seed:
        return None
    seed_pass = [1 if (sum(v) / len(v)) >= 0.5 else 0 for v in per_seed.values()]
    return sum(seed_pass) / len(seed_pass)


def _sep_at(systems, cutoff_key, drop_seed=None):
    """SEED-level concordance test at one cutoff: NR4A1 passes in a MAJORITY of seeds while BOTH spared
    paralogues pass in a MINORITY. Returns (bool_or_None, {name: seed_fraction})."""
    fr = {name: _seed_bridged_fraction(systems[name], cutoff_key, drop_seed) for name in ("nr4a1", "nr4a2", "nr4a3")}
    if any(v is None for v in fr.values()):
        return None, fr
    return (fr["nr4a1"] >= 0.5 and max(fr["nr4a2"], fr["nr4a3"]) < 0.5), fr


def _loo_robust(systems):
    """Leave-one-SEED-out: does the default-cutoff seed-level separation survive dropping ANY single seed?"""
    dk = "%.1f" % DEFAULT_CUTOFF
    seeds = sorted(set(s["seed"] for s in systems["nr4a1"].get("samples", [])))
    if len(seeds) < 2:
        return None
    for drop in seeds:
        ok, fr = _sep_at(systems, dk, drop_seed=drop)
        if ok is None:
            return None
        if not ok:
            return False
    return True


def full_verdict(systems):
    """EXPLORATORY concordance verdict (per the 2026-07-11 external methods review — NOT a validation of
    ternary-selectivity prediction). Primary readout = MOIETY-SPECIFIC bridging (celastrol end contacts the NR4A
    target AND the VH032 end contacts VHL — via the correct ends, not a wrong-end/linker/surface artefact), at
    the default cutoff, with cutoff-sensitivity (4.0/4.5/5.0 Å) and leave-one-seed-out robustness. ligand-iPTM
    ordering is reported for transparency ONLY. Language deliberately avoids 'validated'/'population'/
    'cooperativity' — those quantities are not estimated here."""
    for name in ("nr4a1", "nr4a2", "nr4a3"):
        if name not in systems:
            return {"verdict": "pilot-only", "note": "NR4A2/NR4A3 not present — full verdict needs all three."}

    dk = "%.1f" % DEFAULT_CUTOFF
    sep_default, fr = _sep_at(systems, dk)
    cutoff_sep = {("%.1f" % c): _sep_at(systems, "%.1f" % c)[0] for c in CUTOFFS}
    cutoff_robust = all(v is True for v in cutoff_sep.values())
    loo = _loo_robust(systems)

    def li(name):
        d = systems[name]["ensemble"].get("ligand_iptm")
        return (d or {}).get("mean")
    li1, li2, li3 = li("nr4a1"), li("nr4a2"), li("nr4a3")
    li_note = None
    if None not in (li1, li2, li3):
        li_note = ("ligand-iPTM did NOT reproduce the ordering in this benchmark (NR4A1 %.3f vs NR4A2 %.3f / "
                   "NR4A3 %.3f) and must not rank paralogue-selective ternaries alone." % (li1, li2, li3))

    counts = {name: systems[name]["ensemble"].get("denominator") for name in ("nr4a1", "nr4a2", "nr4a3")}
    if sep_default is None:
        verdict, basis = "insufficient-data", "seed-level fractions unavailable for all three paralogues"
    elif sep_default:
        verdict = "exploratory-architecture-concordance"
        basis = ("in ONE retrospective example the correct-half dual-surface proximity classifier (SEED-level) was "
                 "concordant with the reported phenotype: NR4A1 %.2f of seeds vs NR4A2 %.2f / NR4A3 %.2f at %.1f Å%s%s. "
                 "Architecture-feasibility only; NOT validation, NOT affinity/selectivity." %
                 (fr["nr4a1"], fr["nr4a2"], fr["nr4a3"], DEFAULT_CUTOFF,
                  "; robust across 4.0/4.5/5.0 Å" if cutoff_robust else "; NOT robust across all cutoffs",
                  "; survives leave-one-seed-out" if loo else ("; does NOT survive leave-one-seed-out" if loo is False else "")))
    elif fr.get("nr4a1", 0) and fr["nr4a1"] >= 0.5:
        verdict = "inconclusive"
        basis = "NR4A1 passes the correct-half proximity criterion but a spared paralogue also does — no clean separation"
    else:
        verdict = "discordant"
        basis = "NR4A1 (known-degraded) does not pass the correct-half proximity criterion in a majority of seeds"

    return {"verdict": verdict, "primary_basis": "correct_half_dual_surface_proximity_SEED_level", "basis": basis,
            "seed_bridged_fraction_default": fr, "cutoff_sensitivity_seedlevel": cutoff_sep,
            "cutoff_robust": cutoff_robust, "leave_one_seed_out_robust": loo, "denominators": counts,
            "wrong_end_fraction": {name: systems[name]["ensemble"].get("wrong_end_fraction")
                                   for name in ("nr4a1", "nr4a2", "nr4a3")},
            "ligand_iptm_mean": {"nr4a1": li1, "nr4a2": li2, "nr4a3": li3}, "ligand_iptm_note": li_note,
            "not_an_affinity_gate": ("this is a structure-only architecture-feasibility readout; an inactive "
                                     "stereo-epimer passed it at the active rate — affinity/binding/selectivity "
                                     "ranking requires a SEPARATE affinity method (FEP/ABFE) that first passes the "
                                     "active-vs-epimer control"),
            "caveats": ["retrospective n=1 (NR-V04-inspired representative reconstruction; exact graph unverified)",
                        "NR4A1-selectivity != NR4A3-selectivity", "phenotype does not establish geometry as the cause",
                        "no CRL4/E2~Ub; Lys reach demoted; Cys551 not evaluated",
                        "correct-half proximity (conformation-dependent sulfur-anchor, NOT atom-mapped occupancy) "
                        "elevated to primary AFTER the ligand-iPTM result (exploratory)"]}


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds required")
    try:
        import gemmi  # noqa: F401
    except ImportError:
        sys.exit("pip install gemmi")
    prefix = os.environ.get("OUTPUT_PREFIX", "nrv04-ternary-pilot")
    out_path = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_nrv04.json"))
    with tempfile.TemporaryDirectory() as tmp:
        n, bucket = _download(prefix, tmp)
        if not n:
            sys.exit(f"nothing under s3 prefix {prefix}")
        prep = glob.glob(os.path.join(tmp, "**", "nrv04-ternary-prep.json"), recursive=True)
        prep_data = json.load(open(prep[0])) if prep else {}
        # per-system ligand SMILES: prep_data override (exact graph used for this run) wins over the frozen spec.
        smiles_map = dict(SYSTEM_SMILES)
        smiles_map.update({k.lower(): v for k, v in (prep_data.get("ligand_smiles") or {}).items()})

        systems = {}
        control = None
        # control dir is 'control'; targets are nr4a1/nr4a2/nr4a3
        if glob.glob(os.path.join(tmp, "control", "seed_*")) or glob.glob(os.path.join(tmp, "**", "control", "seed_*"), recursive=True):
            control = analyse_system(tmp, "control", "control")
        for name in ("nr4a1", "nr4a2", "nr4a3"):
            if glob.glob(os.path.join(tmp, name, "seed_*")) or glob.glob(os.path.join(tmp, "**", name, "seed_*"), recursive=True):
                systems[name] = analyse_system(tmp, name, "ternary", ligand_smiles=smiles_map.get(name))

        # Controls, separated by TYPE (review fix #5). ARCHITECTURE negative: free celastrol (no VHL handle) —
        # the classifier IS entitled to catch this. AFFINITY negative: the VHL-inactive Hyp-epimer PROTAC — a
        # structure-only classifier is NOT expected to catch a pure-affinity stereochemical knockout; if it
        # "passes" the epimer that shows the classifier has no affinity sensitivity (the decisive result).
        NEG_TYPE = {"neg_celastrol": "architecture", "neg_inactive": "affinity"}
        negatives = {}
        for name in ("neg_inactive", "neg_celastrol"):
            if glob.glob(os.path.join(tmp, name, "seed_*")) or glob.glob(os.path.join(tmp, "**", name, "seed_*"), recursive=True):
                negatives[name] = analyse_system(tmp, name, "ternary", ligand_smiles=smiles_map.get(name))
        # architecture controls should FAIL the classifier; affinity controls are reported (they define the
        # classifier's affinity-blindness) but do NOT make the architecture gate 'pass'.
        arch_pass = None
        arch = {k: v for k, v in negatives.items() if NEG_TYPE.get(k) == "architecture"}
        if arch:
            arch_pass = all((s["ensemble"].get("seed_bridged_fraction") or 0) < 0.5 for s in arch.values())
        affinity_classifier_blind = None
        aff = {k: v for k, v in negatives.items() if NEG_TYPE.get(k) == "affinity"}
        if aff:
            affinity_classifier_blind = any((s["ensemble"].get("seed_bridged_fraction") or 0) >= 0.5 for s in aff.values())

        report = {"prefix": prefix, "bucket": bucket, "mode": prep_data.get("mode"),
                  "seeds": prep_data.get("seeds"), "ground_truth": prep_data.get("ground_truth"),
                  "control": control, "systems": systems,
                  # PAIRED per-seed/rank records preserved for negatives (review fix #7), not just ensembles.
                  "negative_controls": {k: {"type": NEG_TYPE.get(k), "ensemble": v["ensemble"],
                                            "samples": v.get("samples")} for k, v in negatives.items()},
                  "architecture_controls_pass": arch_pass,
                  "affinity_classifier_blind": affinity_classifier_blind}
        report["pilot_gate"] = pilot_verdict(control, systems.get("nr4a1"))
        if all(k in systems for k in ("nr4a1", "nr4a2", "nr4a3")):
            fg = full_verdict(systems)
            fg["architecture_controls_pass"] = arch_pass
            fg["affinity_classifier_blind"] = affinity_classifier_blind
            if arch_pass is False:
                fg["verdict"] = "failed-architecture-control"
                fg["basis"] = "an ARCHITECTURE negative (should not span) passed the classifier — not even architecture-specific"
            if affinity_classifier_blind:
                fg["affinity_note"] = ("AFFINITY control failed: the VHL-inactive stereo-epimer passed the "
                                       "structure-only classifier at the active rate → no affinity sensitivity; "
                                       "prohibited from affinity/selectivity/linker ranking")
            report["full_gate"] = fg

        json.dump(report, open(out_path, "w"), indent=2)
        print("\n=== NR-V04 / VHL ternary benchmark — %s ===" % prefix)
        if control:
            e = control["ensemble"]
            print("CONTROL VHL+VH032: seated %s/%s samples; ligand-iPTM %s" %
                  (e.get("n_seated"), e.get("n_scored"), e.get("ligand_iptm")))
        for name, s in systems.items():
            e = s["ensemble"]
            print("%s: SEED-level correct-half proximity %s (%s); wrong-end %s; ligand-iPTM %s" %
                  (name.upper(), e.get("seed_bridged_fraction"), e.get("denominator"),
                   e.get("wrong_end_fraction"), (e.get("ligand_iptm") or {}).get("mean")))
        for name, rec in report["negative_controls"].items():
            e = rec["ensemble"]
            print("NEG %s [%s]: SEED-level proximity %s (%s)" %
                  (name, rec.get("type"), e.get("seed_bridged_fraction"), e.get("denominator")))
        if report.get("architecture_controls_pass") is not None:
            print("ARCHITECTURE controls pass (fail to span): %s" % report["architecture_controls_pass"])
        if report.get("affinity_classifier_blind"):
            print("AFFINITY control: classifier is BLIND (inactive epimer passed at the active rate)")
        print("\nPILOT GATE: %s — %s" % (report["pilot_gate"]["verdict"], report["pilot_gate"]["reason"]))
        if "full_gate" in report:
            print("FULL GATE: %s" % json.dumps(report["full_gate"]))
        print("\nwrote %s" % out_path)


if __name__ == "__main__":
    main()
