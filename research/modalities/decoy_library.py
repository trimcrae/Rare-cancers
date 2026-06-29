#!/usr/bin/env python3
"""Decoy / negative-control library for the de-novo selectivity funnel (red-team Tier-1 #2).

WHY. The de-novo funnel reports some generations as "NR4A3-selective" (NR4A3-favourable docking cell /
confirmed_selective MM-GBSA). That number is only meaningful against a NULL: if the SAME dock->MM-GBSA
funnel calls a set of *unrelated, non-NR4A* drug-like molecules NR4A3-selective at the same rate, the
"selectivity" is an artifact of the asymmetric receptor/scoring, not signal. This module supplies a fixed,
reproducible decoy set — diverse marketed drugs with no NR4A relevance — to push through the identical
funnel as a specificity control. Enrichment = (de-novo NR4A3-favourable rate) vs (decoy rate).

Pure (no RDKit/IO) so it is unit-tested; the driver docks decoy_candidate_json() exactly like a de-novo
generation set (same nr4a3-denovo.json shape).
"""

# ~40 diverse, drug-like, MARKETED compounds spanning chemotypes — none is an NR4A1/2/3 ligand. Canonical
# SMILES (hand-verified to parse). This is a property-spanning negative set, not a property-matched DUD-E
# set; it answers "does the funnel preferentially call random drug-like matter NR4A3-selective?" — the
# first-order specificity question. (A property-matched DUD-E decoy set is a heavier follow-up.)
DECOY_SMILES = {
    "caffeine":         "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "ibuprofen":        "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
    "aspirin":          "CC(=O)Oc1ccccc1C(=O)O",
    "acetaminophen":    "CC(=O)Nc1ccc(O)cc1",
    "atenolol":         "CC(C)NCC(O)COc1ccc(CC(N)=O)cc1",
    "diphenhydramine":  "CN(C)CCOC(c1ccccc1)c1ccccc1",
    "propranolol":      "CC(C)NCC(O)COc1cccc2ccccc12",
    "warfarin":         "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
    "naproxen":         "COc1ccc2cc(C(C)C(=O)O)ccc2c1",
    "fluconazole":      "OC(Cn1cncn1)(Cn1cncn1)c1ccc(F)cc1F",
    "ciprofloxacin":    "O=C(O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O",
    "omeprazole":       "COc1ccc2[nH]c(S(=O)Cc3ncc(C)c(OC)c3C)nc2c1",
    "sertraline":       "CNC1CCC(c2ccc(Cl)c(Cl)c2)c2ccccc21",
    "fluoxetine":       "CNCCC(Oc1ccc(C(F)(F)F)cc1)c1ccccc1",
    "amlodipine":       "CCOC(=O)C1=C(COCCN)NC(C)=C(C(=O)OC)C1c1ccccc1Cl",
    "metoprolol":       "COCCc1ccc(OCC(O)CNC(C)C)cc1",
    "lidocaine":        "CCN(CC)CC(=O)Nc1c(C)cccc1C",
    "diazepam":         "CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21",
    "haloperidol":      "O=C(CCCN1CCC(O)(c2ccc(Cl)cc2)CC1)c1ccc(F)cc1",
    "loratadine":       "CCOC(=O)N1CCC(=C2c3ccc(Cl)cc3CCc3cccnc32)CC1",
    "salbutamol":       "CC(C)(C)NCC(O)c1ccc(O)c(CO)c1",
    "verapamil":        "COc1ccc(CCN(C)CCCC(C#N)(C(C)C)c2ccc(OC)c(OC)c2)cc1OC",
    "captopril":        "CC(CS)C(=O)N1CCCC1C(=O)O",
    "chlorpromazine":   "CN(C)CCCN1c2ccccc2Sc2ccc(Cl)cc21",
    "nicotine":         "CN1CCCC1c1cccnc1",
    "celecoxib":        "Cc1ccc(-c2cc(C(F)(F)F)nn2-c2ccc(S(N)(=O)=O)cc2)cc1",
    "theophylline":     "Cn1c(=O)c2[nH]cnc2n(C)c1=O",
    "phenytoin":        "O=C1NC(=O)C(c2ccccc2)(c2ccccc2)N1",
    "furosemide":       "NS(=O)(=O)c1cc(C(=O)O)c(NCc2ccco2)cc1Cl",
    "metronidazole":    "Cc1ncc([N+](=O)[O-])n1CCO",
    "albendazole":      "CCCSc1ccc2[nH]c(NC(=O)OC)nc2c1",
    "indomethacin":     "COc1ccc2c(c1)c(CC(=O)O)c(C)n2C(=O)c1ccc(Cl)cc1",
    "ketoprofen":       "CC(C(=O)O)c1cccc(C(=O)c2ccccc2)c1",
    "tolbutamide":      "CCCCNC(=O)NS(=O)(=O)c1ccc(C)cc1",
    "hydrochlorothiazide": "NS(=O)(=O)c1cc2c(cc1Cl)NCNS2(=O)=O",
    "trimethoprim":     "COc1cc(Cc2cnc(N)nc2N)cc(OC)c1OC",
    "pyrimethamine":    "CCc1nc(N)nc(N)c1-c1ccc(Cl)cc1",
    "procainamide":     "CCN(CC)CCNC(=O)c1ccc(N)cc1",
}


def decoy_candidate_json(promise=0.0):
    """Return a dict in the nr4a3-denovo.json shape so the dock funnel (nr4a3_matrix candidate mode) can
    consume the decoys exactly like a generation set. Each candidate carries a placeholder denovo_promise
    (so the picker accepts it) and high aromatic_rings / low SAscore so the developability gate never
    excludes a decoy (we want ALL decoys docked to measure the null selectivity rate)."""
    return {"_note": "decoy negative-control set (non-NR4A marketed drugs) for the selectivity funnel",
            "campaign": "decoy-control",
            "candidates": [{"name": f"decoy_{nm}", "smiles": smi, "denovo_promise": promise,
                            "aromatic_rings": 1, "SAscore": 2.0, "BRENK_alert_count": 0}
                           for nm, smi in sorted(DECOY_SMILES.items())]}


def n_decoys():
    return len(DECOY_SMILES)
