#!/usr/bin/env python3
"""Stability / reactivity / synthesizability structural-alert filter for de-novo generated warheads.

WHY. The de-novo MM-GBSA result (2026-06-29 red-team) found that the strongest "confirmed_selective"
generations were chemically non-viable — `denovo_15` carried a carbamic acid + 1,3-cyclopentadiene +
imine, `denovo_94` a peroxide (1,2-dioxane) + N,S-/O,S-acetals — classic pretrained-DiffSBDD artifacts that
score well on QED/SAscore but cannot be made or would decompose. QED and the PAINS/BRENK catalogs do **not**
reliably catch these instability/reactivity classes, so the funnel floated artifacts to the top.

This module adds a deliberately STRICT developability gate: a curated SMARTS catalog of unstable / reactive
/ hard-to-make substructures (beyond PAINS/BRENK), plus the rules "must contain an aromatic ring" and
"SAscore <= 4.5" (the campaign's own synthesizability cut). It favours false negatives (rejecting a
borderline-OK molecule) over false positives (passing an artifact) — the point is a clean *lead*, and there
are hundreds of generations to choose from.

Split for testing (TESTING.md #3): the SMARTS catalog + RDKit matcher need RDKit (guarded import), but the
pass/fail DECISION (`developable_verdict`) is pure and unit-tested without RDKit.
"""

# name -> (SMARTS, one-line why). Curated for INSTABILITY / REACTIVITY / synthetic-intractability that the
# PAINS/BRENK catalogs miss. Kept tight + documented so the gate is defensible, not a black box.
LIABILITY_SMARTS = {
    "peroxide":            ("[OX2][OX2]", "O-O bond: unstable / potentially explosive"),
    "carbamic_acid":       ("[NX3][CX3](=O)[OX2H1,OX1-]", "decomposes to amine + CO2"),
    "cyclopentadiene":     ("[CR1]1=[CR1][CR1]=[CR1][CR1]1", "reactive 1,3-diene (Diels-Alder)"),
    "allene":              ("[CX3]=[CX2]=[CX3]", "strained/reactive cumulated diene"),
    "ketene":              ("[CX3]=[CX2]=[OX1]", "highly reactive ketene"),
    "isocyanate":          ("[NX2]=[CX2]=[OX1]", "reactive isocyanate"),
    "isothiocyanate":      ("[NX2]=[CX2]=[SX1]", "reactive isothiocyanate"),
    "thiocarbonyl":        ("[CX3]=[SX1]", "thione/thioamide-type C=S, reactive/labile"),
    "NS_acetal":           ("[CX4]([NX3])[SX2]", "N,S-acetal/aminal, hydrolytically labile"),
    "OS_acetal":           ("[CX4]([OX2])[SX2]", "O,S-acetal, hydrolytically labile"),
    "NN_aminal":           ("[CX4]([NX3])[NX3]", "aminal, hydrolytically labile"),
    "OO_acetal":           ("[CX4]([OX2])[OX2]", "acetal/ketal, acid-labile"),
    "hemiketal":           ("[CX4;!$([CX4]([OX2H])[OX2H])]([OX2H])[OX2,NX3]", "hemiketal/hemiaminal, labile"),
    "gem_diol":            ("[CX4]([OX2H])[OX2H]", "gem-diol, dehydrates"),
    "hydrazine":           ("[NX3;!$(N=*);!$(N-[CX3]=[OX1])][NX3;!$(N=*);!$(N-[CX3]=[OX1])]",
                            "free hydrazine N-N, reactive/toxic"),
    "nitroso":             ("[NX2]=[OX1]", "nitroso, reactive/mutagenic"),
    "azide":               ("[NX1]~[NX2]~[NX2,NX1]", "azide, energetic"),
    "aliphatic_enol":      ("[OX2H][CX3]=[CX3]", "enol, tautomerically unstable"),
    "phosphorus_oddity":   ("[PX2,PX1]", "low-valent phosphorus, not drug-like"),
}

MAX_SASCORE = 4.5      # the campaign's own synthesizability cut


def find_liabilities(mol, chem):
    """Return the sorted list of liability names whose SMARTS match `mol`. `chem` is rdkit.Chem (passed in
    so this stays import-light and testable with a real RDKit). Returns [] for a clean molecule."""
    hits = []
    for name, (smarts, _why) in LIABILITY_SMARTS.items():
        q = chem.MolFromSmarts(smarts)
        if q is not None and mol.HasSubstructMatch(q):
            hits.append(name)
    return sorted(hits)


def liabilities_from_smiles(smiles):
    """Convenience: parse a SMILES and return its liability names (RDKit imported lazily). Returns
    ["unparseable"] if RDKit can't parse it. Used by the local re-screen of existing generations."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return ["unparseable"]
    return find_liabilities(m, Chem)


def developable_verdict(liabilities, aromatic_rings, sascore, max_sa=MAX_SASCORE):
    """PURE pass/fail gate for a generated molecule (no RDKit). A molecule is developable only if it has
    NO structural-alert liability, at least one aromatic ring, and SAscore <= max_sa.

    liabilities: list of liability names from find_liabilities (or []).
    aromatic_rings: int (profile['aromatic_rings']); None -> treated as 0 (fail the aromatic rule).
    sascore: float (profile['SAscore']); None -> treated as too-hard (fail).
    Returns {"developable": bool, "reasons": [..]} where reasons are the failing criteria (empty if clean).
    """
    reasons = []
    if liabilities:
        reasons.extend(f"alert:{n}" for n in liabilities)
    if not aromatic_rings:                          # 0, None -> no aromatic ring
        reasons.append("no_aromatic_ring")
    if sascore is None or sascore > max_sa:
        reasons.append(f"SAscore>{max_sa}")
    return {"developable": len(reasons) == 0, "reasons": reasons}
