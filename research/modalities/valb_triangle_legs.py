#!/usr/bin/env python3
"""The four NEW legs of the valB synthetic closure TRIANGLE, and the ONE derivation of their third endpoint.

WHAT THIS IS FOR. `valb_triangle_closure.py` does the arithmetic (does the cycle close, what can R diagnose,
what does it cost); `valb_triangle_chem.py` did the $0 chemistry pre-gate. Neither of them can be RUN as a
leg. This module is the missing registry: it names the four legs the triangle actually buys, derives the third
endpoint they morph to, and hands both to the engine through the same interfaces `nr4a3_5aks_cofold` uses.

THE TOPOLOGY IS THE PRE-GATE'S, NOT THE DESIGN'S. `valb-closure-triangle-pregate-2026-07-25.md` §2 REFUTED
the design's named candidates (aminopyridazine N->CH, thiazole 4-Me->H, tBu->iPr, phenol OH->H): each sits at
a site different from T1's, so the closing edge cmpd1 -> cmpd4' carries BOTH transforms and is a DOUBLE
mutation -- which `rbfe_map.validate_map()` forbids on a closing edge specifically. §2d's replacement puts
all three vertices on the SAME ring, the linker pyridine, as an aza-scan:

    T1  cmpd1 -> cmpd4    remove the linker ring N        1 atom   0 heavy dummies   ALREADY RUN (this is r0)
    T2  cmpd4 -> cmpd4"   add a ring N at a free CH       1 atom   0 heavy dummies   new
    T3  cmpd1 -> cmpd4"   MOVE the ring N                 2 atoms  0 heavy dummies   new (closes the loop)

Every edge is single-site*, charge-neutral, and a pure element change with ZERO heavy dummy atoms, so no edge
grows the softcore region that `ternary-rbfe-runbook.md` §1b/§1c root-causes this lane's warmup NaNs to.
(*T3 changes two atoms but on ONE ring in ONE contiguous perturbation, which is what the invariant is about --
it is a nitrogen 1,2-shift, not two independent site changes.)

WHERE THE NEW NITROGEN GOES, AND WHY IT IS NOT A FREE CHOICE. `_aza_site` picks the free ring C-H whose
minimum ring-bond distance to ANY substituted ring atom is greatest, ties broken by canonical rank. On the
Wurz linker ring (substituents: the amide carbonyl and the piperazine, meta to each other) that is a UNIQUE
position -- the only free CH that is meta to both -- so the rule does not merely break a tie, it selects.
Three properties make it the right rule rather than an arbitrary one:

  * TOPOLOGICAL, so it does not depend on atom ordering, on the SMILES string, or on an RDKit canonical-rank
    implementation that a version bump could reorder. A rule keyed on `sorted(ring_atoms)[0]` would silently
    select a DIFFERENT molecule under a different RDKit, and nothing downstream would notice.
  * CHARGE-NEUTRAL BY CONSTRUCTION, because only a ring carbon bearing exactly one hydrogen is eligible. An
    aza-substitution at a SUBSTITUTED ring position makes a quaternary aromatic N+ -- the formal-charge change
    that killed 6 of the 10 P-series pairs (`valb_pseries_chem.py`), and the same missing charge correction
    that blocks 8 legs of `step1_fanout`. Enforced in code and asserted, not assumed.
  * MOST REMOTE FROM BOTH SUBSTITUENTS, so the aza-scan perturbs the linker's substitution pattern as little
    as the ring allows and cannot introduce an ortho clash with either the amide or the piperazine.

TWO INDEPENDENT ROUTES TO THE SAME ENDPOINT, AND THEY MUST AGREE. This is the closure PREREQUISITE, not a
nicety: if the two constructions disagree the three edges do not share endpoints and R is not a closure
residual at all (`valb_triangle_closure.closure_identity`).

    route A:  frozen cmpd4  --(C->N at the aza site)-->                    cmpd4"
    route B:  frozen cmpd1  --(N->C at the pyridine N, C->N at the site)--> cmpd4"

They start from DIFFERENT frozen molecules (`wurz-calib-frozen.json`'s `calib_lo` and `calib_hi`) and take
different code paths, so agreement is evidence rather than tautology. `derive()` fails closed if they differ.

⚠ ALL THREE EDGES RUN AT SEED 0. `ternary_pdb_stage` sets starting_model_index = SEED % n_models, so a
triangle at mixed seeds is computed on DIFFERENT Hamiltonians, the edges stop sharing endpoint states, the
telescoping fails, and |R| becomes a measure of homology-model sensitivity instead of method consistency.
r0 is seed 0 (`valb_triangle_closure.same_seed_requirement`), so T2 and T3 are seed 0.

⚠ AND THE BINARY LEGS RUN UNRESTRAINED. Decided 2026-07-26 (trimcrae delegated) and recorded in
`valb_triangle_closure.binary_departure_prereg`. Restraining T2/T3's binary legs inside a cycle whose T1 is
the UNRESTRAINED r0 would make R measure the PROTOCOL DIFFERENCE rather than the path error -- destroying the
experiment's only claim -- and would forfeit the r0-as-T1 reuse that makes the triangle 4 legs instead of 6.
A separate lane is concurrently building a RESTRAINED binary re-run for a different purpose. They are
different experiments and must never be conflated or their legs mixed in one reduction.

⚠ AND AT 2 fs, NOT THE LANE DEFAULT 4 fs, for exactly the same reason: r0 is a 2 fs leg. The mode pins the
timestep (`ternary_vast_launch.MODES['triangle']`), because the workflow exports `TVAST_TIMESTEP_FS`
lane-wide and an env-first resolution would silently buy a 4 fs triangle around a 2 fs T1.

WHY A FROZEN FILE RATHER THAN A LIVE DERIVATION. `wurz-calib-frozen.json` already treats cmpd4 exactly this
way -- a DERIVED SMILES, frozen with its transform recorded -- and for the same reason: what was simulated
must be recoverable from git, not recomputed by whatever RDKit happens to be installed later. `derive()`
runs once in the parity image and writes `valb-triangle-frozen.json`; everything else (this module's
`LEG_MAP`, `ternary_coop_prep._morph_endpoints`, the launcher, the reducer) reads that file with the standard
library and no chemistry stack at all. `verify()` re-derives and fails closed on drift.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CALIB_FROZEN = os.path.join(HERE, "wurz-calib-frozen.json")
FROZEN = os.path.join(HERE, "valb-triangle-frozen.json")

# ---------------------------------------------------------------------------------------------------------
# ENDPOINT ROLE NAMES ARE A CONTRACT WITH THE ENGINE, NOT LABELS. `ternary_coop_prep._morph_endpoints` splits
# a leg's `morph` string on `->`, and the two halves become the SDF record names `nr4a3_rbfe._sdf_mol`
# resolves each alchemical endpoint by. Four files therefore have to agree on three strings; they agree by
# importing THESE. `calib_hi`/`calib_lo` are the existing roles (Wurz cmpd1 / cmpd4) and must not be renamed.
# ---------------------------------------------------------------------------------------------------------
ROLE_HI = "calib_hi"        # Wurz cmpd1 -- the co-crystallised ligand (8G1Q, CCD YHB)
ROLE_LO = "calib_lo"        # Wurz cmpd4 -- linker pyridine N -> CH (derived, frozen)
ROLE_LO2 = "calib_lo2"      # cmpd4"     -- the aza-scan third vertex (derived here, frozen here)

# The two NEW edges, in the orientation `valb_triangle_closure.TRIANGLE` uses. T1 (calib_hi -> calib_lo) is
# NOT here on purpose: it is r0, already run, and re-registering it would invite it being re-bought.
T2_MORPH = f"{ROLE_LO} -> {ROLE_LO2}"       # cmpd4 -> cmpd4"   (coefficient +1)
T3_MORPH = f"{ROLE_HI} -> {ROLE_LO2}"       # cmpd1 -> cmpd4"   (coefficient -1, the closing edge)

# `<morph>__<environment>_<e3>` -- the repo convention `nr4a3_ternary_fep._environment_of` and `_morph_key`
# parse. The `__ternary` / `__binary` separator is what classifies the environment, and a single-underscore
# id would classify a ternary leg as BINARY, drop the target chain, and converge perfectly well on the wrong
# system (the trap `nr4a3_5aks_cofold` documents). `calib_` prefix is also load-bearing: it is what turns on
# `RBFE_MAP_ASSERT` in `ternary_vast_launch.build_jobspec`.
T2_KEY = "calib_lo_to_lo2"
T3_KEY = "calib_hi_to_lo2"

_PURPOSE = ("edge %s of the valB synthetic closure triangle (aza-scan at the linker ring). The deliverable is "
            "the closure residual R = ddG_coop(T1) + ddG_coop(T2) - ddG_coop(T3), which is IDENTICALLY ZERO "
            "for any endpoint-STATE error (force field, SMARCA4->SMARCA2 homology, NAGL charges, protonation) "
            "and non-zero only for PATH error -- so R decides whether r0's 1.478 kcal/mol miss is fixable by "
            "sampling at all. Reported as R_ternary and R_binary SEPARATELY, never as R alone.")

LEG_MAP = {
    f"{T2_KEY}__ternary_vhl": {
        "morph": T2_MORPH, "environment": "ternary", "e3": "VHL", "target": "SMARCA2",
        "wedge": "linker ring: add an aromatic ring N at the free C-H most remote from both substituents",
        "triangle_edge": "T2", "triangle_coefficient": +1,
        "purpose": _PURPOSE % "T2 (ternary arm)"},
    f"{T2_KEY}__binary_vhl": {
        "morph": T2_MORPH, "environment": "binary", "e3": "VHL", "target": None,
        "wedge": "linker ring: add an aromatic ring N at the free C-H most remote from both substituents",
        "triangle_edge": "T2", "triangle_coefficient": +1,
        "purpose": _PURPOSE % "T2 (binary arm, UNRESTRAINED)"},
    f"{T3_KEY}__ternary_vhl": {
        "morph": T3_MORPH, "environment": "ternary", "e3": "VHL", "target": "SMARCA2",
        "wedge": "linker ring: MOVE the aromatic ring N (a 1,2-shift) -- the closing edge",
        "triangle_edge": "T3", "triangle_coefficient": -1,
        "purpose": _PURPOSE % "T3 (ternary arm, the closing edge)"},
    f"{T3_KEY}__binary_vhl": {
        "morph": T3_MORPH, "environment": "binary", "e3": "VHL", "target": None,
        "wedge": "linker ring: MOVE the aromatic ring N (a 1,2-shift) -- the closing edge",
        "triangle_edge": "T3", "triangle_coefficient": -1,
        "purpose": _PURPOSE % "T3 (binary arm, UNRESTRAINED, the closing edge)"},
}

# The SIX legs R is built from, and which of them already exist. Exactly two do -- r0's ternary and binary --
# and they are the entire economy of the design: 4 new legs, not 6.
TRIANGLE_LEGS = {
    "T1": {"ternary": "calib_hi_to_lo__ternary_vhl", "binary": "calib_hi_to_lo__binary_vhl",
           "coefficient": +1, "status": "ALREADY RUN as valB_mini r0 (seed 0, 2 fs) -- REUSED, not re-bought"},
    "T2": {"ternary": f"{T2_KEY}__ternary_vhl", "binary": f"{T2_KEY}__binary_vhl",
           "coefficient": +1, "status": "new"},
    "T3": {"ternary": f"{T3_KEY}__ternary_vhl", "binary": f"{T3_KEY}__binary_vhl",
           "coefficient": -1, "status": "new"},
}

NEW_LEG_IDS = sorted(LEG_MAP)


def load_frozen(path=FROZEN):
    """The frozen cmpd4" record. Pure stdlib -- no RDKit, no network.

    Returns None when the file is absent, which is a real state (before `--derive` has ever run) and must be
    reported as `pending` upstream rather than papered over with a guess."""
    try:
        with open(path) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return None
    return d if str(d.get("_status", "")).startswith("FROZEN") else None


def calib_lo2_smiles(path=FROZEN):
    """cmpd4"'s frozen SMILES, or None. The ONE accessor; nothing else may read the field directly."""
    d = load_frozen(path)
    return (d or {}).get("calib_lo2", {}).get("smiles")


def smiles_by_role(path=FROZEN, calib_path=CALIB_FROZEN):
    """{role: smiles} across all THREE triangle vertices, or {} if either freeze is missing.

    This is what `ternary_coop_prep._morph_endpoints` resolves a triangle leg against. It deliberately reads
    calib_hi/calib_lo from the WURZ freeze rather than re-stating them here: cmpd1 and cmpd4 already have a
    home, and a second copy is how the molecule actually simulated and the molecule on record drift apart.
    """
    tri = load_frozen(path)
    if not tri:
        return {}
    try:
        with open(calib_path) as fh:
            cal = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not str(cal.get("_status", "")).startswith("FROZEN"):
        return {}
    out = {ROLE_HI: cal[ROLE_HI]["smiles"], ROLE_LO: cal[ROLE_LO]["smiles"],
           ROLE_LO2: tri[ROLE_LO2]["smiles"]}
    return {k: v for k, v in out.items() if v}


# =============================================================================================================
# the derivation -- RDKit only, run ONCE in the parity image, never at leg time
# =============================================================================================================
def _linker_ring(mol, Chem):
    """The Wurz linker ring, identified by its SUBSTITUENTS rather than by its element content.

    Returns (ring_atom_indices, substituted_positions) or raises. Identifying it by chemistry is what makes
    this work on BOTH cmpd1 (where the ring is a pyridine and could be found by 'the unique pyridine') and
    cmpd4 (where it is a benzene among FOUR other aromatic six-rings -- the tolyl, the pyridazine and the
    2-hydroxyphenyl -- and 'the unique benzene' would be ambiguous or wrong).

    The signature is exact and fails closed: a six-membered aromatic ring carrying exactly one amide-carbonyl
    substituent and exactly one aliphatic-ring-nitrogen (piperazine) substituent.
    """
    amide_c = {a.GetIdx() for a in mol.GetAtoms()
               if a.GetSymbol() == "C" and not a.GetIsAromatic()
               and any(b.GetBondType() == Chem.BondType.DOUBLE and b.GetOtherAtom(a).GetSymbol() == "O"
                       for b in a.GetBonds())
               and any(n.GetSymbol() == "N" for n in a.GetNeighbors())}
    pip_n = {a.GetIdx() for a in mol.GetAtoms()
             if a.GetSymbol() == "N" and not a.GetIsAromatic() and a.IsInRing()}
    hits = []
    for ring in mol.GetRingInfo().AtomRings():
        if len(ring) != 6 or not all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring):
            continue
        rs = set(ring)
        c_at = [i for i in ring if any(n.GetIdx() in amide_c for n in mol.GetAtomWithIdx(i).GetNeighbors()
                                       if n.GetIdx() not in rs)]
        n_at = [i for i in ring if any(n.GetIdx() in pip_n for n in mol.GetAtomWithIdx(i).GetNeighbors()
                                       if n.GetIdx() not in rs)]
        if len(c_at) == 1 and len(n_at) == 1:
            hits.append((list(ring), sorted(set(c_at + n_at))))
    if len(hits) != 1:
        raise SystemExit("[triangle] linker ring not uniquely identified (%d candidate six-rings carrying "
                         "exactly one amide carbonyl and one piperazine N) -- refusing to guess" % len(hits))
    return hits[0]


def _ring_distance(ring, i, j):
    """Bond distance between two atoms AROUND the ring (the shorter arc). PURE."""
    n = len(ring)
    a, b = ring.index(i), ring.index(j)
    d = abs(a - b)
    return min(d, n - d)


def _aza_site(mol, ring, substituted, Chem):
    """Which ring atom becomes the new nitrogen. Deterministic, topological, charge-safe. See the module
    docstring for why each of those three words is load-bearing.

    Eligible: a ring atom that is a CARBON bearing EXACTLY ONE hydrogen. Ranked by (-min ring distance to any
    substituted ring atom, canonical rank), so the winner is the most remote free C-H and ties -- if the ring
    were symmetric enough to produce one -- resolve reproducibly rather than by iteration order.
    """
    ranks = list(Chem.CanonicalRankAtoms(mol, breakTies=True))
    elig = []
    for i in ring:
        a = mol.GetAtomWithIdx(i)
        if a.GetSymbol() != "C" or a.GetTotalNumHs() != 1:
            continue
        remote = min(_ring_distance(ring, i, s) for s in substituted) if substituted else 0
        elig.append((-remote, ranks[i], i, remote))
    if not elig:
        raise SystemExit("[triangle] no free ring C-H on the linker ring -- every aza position would make a "
                         "quaternary aromatic N+ and change the formal charge. Refusing.")
    elig.sort()
    best = elig[0]
    n_tied = sum(1 for e in elig if e[0] == best[0])
    return {"atom_idx": best[2], "min_ring_distance_to_a_substituent": best[3],
            "n_eligible_free_CH": len(elig), "n_tied_at_max_distance": n_tied,
            "unique_by_topology": n_tied == 1}


def _set_ring_element(mol, idx, z, Chem):
    """Change one aromatic ring atom's element, re-sanitize, return a NEW mol (or None). No coordinates are
    involved here -- this is the SMILES-level derivation; the 3D pose analogue lives in
    `nr4a3_ternary_fep._aromatic_element_swap_pose`, and the two are checked against each other by the
    5-part gate's endpoints_match test at leg time."""
    m = Chem.RWMol(mol)
    a = m.GetAtomWithIdx(idx)
    a.SetAtomicNum(z)
    a.SetNumExplicitHs(0)
    a.SetNoImplicit(False)
    a.SetFormalCharge(0)
    out = m.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception:  # noqa: BLE001
        return None
    return out


def _canon(m, Chem):
    return Chem.MolToSmiles(Chem.RemoveHs(m)) if m is not None else None


def derive(calib_path=CALIB_FROZEN):
    """Derive cmpd4" by TWO independent routes and return the frozen record. Needs RDKit.

    Fails closed on: a linker ring that is not uniquely identifiable, an ineligible aza site, a formal-charge
    change, a route A/route B disagreement, or a cmpd4" that is not distinct from both cmpd1 and cmpd4.
    """
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")

    with open(calib_path) as fh:
        cal = json.load(fh)
    if not str(cal.get("_status", "")).startswith("FROZEN"):
        raise SystemExit("[triangle] the Wurz calib pair is not FROZEN -- refusing to derive from it")
    smi_hi, smi_lo = cal[ROLE_HI]["smiles"], cal[ROLE_LO]["smiles"]
    hi, lo = Chem.MolFromSmiles(smi_hi), Chem.MolFromSmiles(smi_lo)
    if hi is None or lo is None:
        raise SystemExit("[triangle] a frozen calib SMILES did not parse")

    # --- the ring, in each molecule independently ---------------------------------------------------------
    ring_hi, subst_hi = _linker_ring(hi, Chem)
    ring_lo, subst_lo = _linker_ring(lo, Chem)

    # cmpd1's linker ring must be the pyridine T1 consumes: exactly one aromatic ring N, and it must carry no
    # hydrogen (a pyridine-type N, not a pyrrole-type one).
    ns_hi = [i for i in ring_hi if hi.GetAtomWithIdx(i).GetSymbol() == "N"]
    if len(ns_hi) != 1 or hi.GetAtomWithIdx(ns_hi[0]).GetTotalNumHs() != 0:
        raise SystemExit("[triangle] cmpd1's linker ring is not a single pyridine-type N -- the design's T1 "
                         "transform does not describe this molecule")
    if any(lo.GetAtomWithIdx(i).GetSymbol() != "C" for i in ring_lo):
        raise SystemExit("[triangle] cmpd4's linker ring is not all-carbon -- T1 is not the N->CH edge on it")

    # CROSS-CHECK T1 ITSELF before building anything on top of it: removing cmpd1's linker ring N must
    # reproduce the frozen cmpd4 exactly. If it does not, the triangle is being built on a T1 that is not r0's.
    t1 = _set_ring_element(hi, ns_hi[0], 6, Chem)
    if _canon(t1, Chem) != _canon(lo, Chem):
        raise SystemExit("[triangle] re-deriving cmpd4 from cmpd1 (linker ring N->CH) does NOT reproduce the "
                         "frozen calib_lo -- the T1 edge on record is not the T1 edge this code builds")

    # --- the aza site, chosen on cmpd4 (the molecule route A edits) ---------------------------------------
    site_lo = _aza_site(lo, ring_lo, subst_lo, Chem)
    # ...and independently on cmpd1, EXCLUDING its existing ring N, which is a carbon in cmpd4 and must not be
    # re-selected (that would just rebuild cmpd1).
    site_hi = _aza_site(hi, [i for i in ring_hi if i != ns_hi[0]], subst_hi, Chem)

    # --- route A: cmpd4 --(C->N at the site)--> cmpd4" ----------------------------------------------------
    route_a = _set_ring_element(lo, site_lo["atom_idx"], 7, Chem)
    if route_a is None:
        raise SystemExit("[triangle] route A: the aza-substitution did not sanitize (kekulization?)")

    # --- route B: cmpd1 --(N->C at the pyridine N, then C->N at the site)--> cmpd4" -----------------------
    # Note this edits the ORIGINAL cmpd1 twice, so it never passes through the frozen cmpd4 string; the two
    # routes therefore share no intermediate and agreement is evidence.
    b0 = _set_ring_element(hi, ns_hi[0], 6, Chem)
    route_b = _set_ring_element(b0, site_hi["atom_idx"], 7, Chem) if b0 is not None else None
    if route_b is None:
        raise SystemExit("[triangle] route B: the two-step aza-move did not sanitize")

    ca, cb = _canon(route_a, Chem), _canon(route_b, Chem)
    if ca != cb:
        raise SystemExit("[triangle] CLOSURE PREREQUISITE FAILED: route A (%s) and route B (%s) do not give "
                         "the same cmpd4\" -- the three edges would not share endpoints and R would not be a "
                         "closure residual at all." % (ca, cb))
    if ca in (_canon(hi, Chem), _canon(lo, Chem)):
        raise SystemExit("[triangle] cmpd4\" is identical to cmpd1 or cmpd4 -- that is not a triangle, it is "
                         "a degenerate two-vertex cycle")

    from rdkit.Chem import rdmolops
    charges = {ROLE_HI: rdmolops.GetFormalCharge(hi), ROLE_LO: rdmolops.GetFormalCharge(lo),
               ROLE_LO2: rdmolops.GetFormalCharge(route_a)}
    if len(set(charges.values())) != 1:
        raise SystemExit("[triangle] formal charge is not conserved across the three vertices (%r) -- a charge "
                         "change needs a correction this lane does not have, and it is what blocks 8 legs of "
                         "step1_fanout." % charges)

    # PERTURBED HEAVY ATOMS PER EDGE, measured rather than asserted, by the same rdFMCS settings
    # `valb_pseries_chem.py` used -- so these numbers are directly comparable to the 58-80 that refuted the
    # P-series and the 2 of the edge already running.
    from rdkit.Chem import rdFMCS
    def _perturbed(m1, m2):
        r = rdFMCS.FindMCS([m1, m2], timeout=60, ringMatchesRingOnly=True, completeRingsOnly=True)
        core = r.numAtoms
        return max(m1.GetNumHeavyAtoms(), m2.GetNumHeavyAtoms()) - core

    edges = {
        "T1 (calib_hi -> calib_lo)": _perturbed(hi, lo),
        "T2 (calib_lo -> calib_lo2)": _perturbed(lo, route_a),
        "T3 (calib_hi -> calib_lo2)": _perturbed(hi, route_a),
    }

    return {
        "_status": "FROZEN",
        "_what": "the third vertex of the valB synthetic closure triangle -- cmpd4\", the aza-scan analogue "
                 "of the Wurz linker ring. DERIVED (no crystal exists), by two independent routes that agree.",
        "_provenance": "derived from wurz-calib-frozen.json's calib_hi (RCSB 8G1Q, CCD YHB) by "
                       "valb_triangle_legs.derive() inside docker.io/triskit23/ternary-fep -- the production "
                       "mapper's own container. No SMILES in this file was typed by hand.",
        "_topology": "valb-closure-triangle-pregate-2026-07-25.md section 2d (aza-scan at the linker ring), "
                     "which REPLACED the design's four named candidates because each made T3 a double "
                     "mutation that rbfe_map.validate_map() forbids on a closing edge.",
        ROLE_LO2: {
            "role": ROLE_LO2,
            "name": "Wurz_cmpd4_aza",
            "smiles": ca,
            "modeled_from": "8G1Q (cmpd1 crystal pose; no separate crystal exists)",
            "derivation": {
                "transform": "linker ring aza-scan: the free C-H most remote from both ring substituents "
                             "becomes an aromatic N",
                "route_A": "frozen calib_lo (cmpd4) --(C->N at ring atom %d)--> cmpd4\""
                           % site_lo["atom_idx"],
                "route_B": "frozen calib_hi (cmpd1) --(N->C at ring atom %d, C->N at ring atom %d)--> cmpd4\""
                           % (ns_hi[0], site_hi["atom_idx"]),
                "routes_agree": True,
                "linker_ring_atom_idx_in_cmpd4": sorted(ring_lo),
                "substituted_ring_positions_in_cmpd4": subst_lo,
                "site_selection_cmpd4": site_lo,
                "site_selection_cmpd1": site_hi,
                "site_rule": "the eligible free ring C-H with the greatest minimum ring-bond distance to any "
                             "substituted ring atom; ties by RDKit canonical rank. Topological, so it is "
                             "invariant to atom ordering and to a canonical-rank implementation change.",
                "cmpd4_redderived_from_cmpd1_matches_frozen": True,
            },
            "formal_charges": charges,
            "perturbed_heavy_atoms_by_edge": edges,
            "heavy_dummy_atoms_by_edge": {k: 0 for k in edges},
            "heavy_dummy_basis": "every edge is a pure aromatic ELEMENT change (N<->C), which maps 1:1 and "
                                 "creates no appearing/disappearing heavy atom. This is the property that "
                                 "keeps the softcore region -- the runbook's own root cause for this lane's "
                                 "warmup NaNs -- exactly the size it already is.",
            "note": "DERIVED, not observed. The 5-part gate re-checks built-vs-frozen identity at leg time, "
                    "and the endpoint pose is built from cmpd1's crystal coordinates by a two-atom aromatic "
                    "element swap that preserves every coordinate.",
        },
        "triangle": {
            "T1": {"morph": f"{ROLE_HI} -> {ROLE_LO}", "coefficient": +1,
                   "status": "ALREADY RUN as valB_mini r0 (seed 0, 2 fs) -- reused, not re-bought"},
            "T2": {"morph": T2_MORPH, "coefficient": +1, "legs": [f"{T2_KEY}__ternary_vhl",
                                                                  f"{T2_KEY}__binary_vhl"]},
            "T3": {"morph": T3_MORPH, "coefficient": -1, "legs": [f"{T3_KEY}__ternary_vhl",
                                                                  f"{T3_KEY}__binary_vhl"]},
            "seed": 0,
            "seed_requirement": "ALL THREE EDGES AT SEED 0. Ternary seed s selects the s%n-th independently "
                                "relaxed SMARCA2 model, so a mixed-seed triangle is computed on different "
                                "Hamiltonians and |R| stops being a closure residual.",
            "binary_legs": "UNRESTRAINED, matching r0. Restraining them would make R measure the protocol "
                           "difference rather than the path error, and would forfeit the r0-as-T1 reuse.",
            "timestep_fs": 2.0,
            "timestep_requirement": "2 fs production / 1 fs warmup, matching r0. The lane's 4 fs default is "
                                    "RUNG 2b's and must not reach this mode.",
        },
    }


def verify(path=FROZEN, calib_path=CALIB_FROZEN):
    """Re-derive and compare against the frozen file. Returns (ok, reason). Needs RDKit.

    Same discipline as `ternary_coop.load_pilot_legs`: a freeze that no longer matches the code that made it
    is a silent scientific drift, so it is checked rather than trusted."""
    frozen = load_frozen(path)
    if not frozen:
        return False, "no frozen record at %s" % path
    fresh = derive(calib_path)
    a, b = frozen[ROLE_LO2]["smiles"], fresh[ROLE_LO2]["smiles"]
    if a != b:
        return False, "frozen cmpd4\" (%s) != re-derived (%s)" % (a, b)
    return True, "frozen cmpd4\" re-derives exactly"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Derive/verify the valB closure triangle's third endpoint.")
    ap.add_argument("--derive", action="store_true", help="derive and WRITE the frozen record")
    ap.add_argument("--verify", action="store_true", help="re-derive and fail if it disagrees with the freeze")
    ap.add_argument("--out", default=FROZEN)
    a = ap.parse_args(argv)
    if a.verify:
        ok, why = verify(a.out)
        print("[triangle] verify: %s -- %s" % ("OK" if ok else "FAILED", why))
        return 0 if ok else 1
    if a.derive:
        rec = derive()
        with open(a.out, "w") as fh:
            json.dump(rec, fh, indent=2)
            fh.write("\n")
        print(json.dumps(rec, indent=2))
        print("[triangle] wrote %s" % a.out)
        return 0
    print(json.dumps({"new_leg_ids": NEW_LEG_IDS, "triangle_legs": TRIANGLE_LEGS,
                      "calib_lo2_smiles": calib_lo2_smiles()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
