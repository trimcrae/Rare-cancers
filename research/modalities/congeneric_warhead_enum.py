#!/usr/bin/env python3
"""
Focused CONGENERIC WARHEAD ENUMERATION for the NR4A3-selective-degrader program.

This implements the "Warhead source" section of
    research/manuscripts/nr4a3-degrader-strategy-ternary-first.md
(Track B: selectivity from warhead x linker x E3 x ternary-interface geometry). It enumerates a small,
curated, chemically-motivated congeneric set around the experimentally-anchored NR4A3 tool compound and
emits it as a machine-readable design table for the downstream RBFE / ternary matrix.

ANCHOR: Zaienne 2022 compound 19 = methyl 5-bromoindole-3-carboxylate (registry id `zaienne_cmpd19`;
        SMRT IC50 9+/-2 uM, NCoR1 12+/-3 uM; PMID 35704774 / PMC9542104 / DOI 10.1002/cmdc.202200259).

>>> HONESTY / GOLDEN-RULE CAVEATS (this is a medical-research repo; do NOT fabricate) <<<
  * Compound 19 is FUNCTIONAL target engagement only (it blocks the NOR-1<->SMRT/NCoR1 corepressor
    interactions and derepresses MYC). It is NOT a structurally proven LBD binder: there is no solved
    NR4A3-19 cocrystal. THEREFORE the binding pose, and with it the "5-position is the linker exit
    vector" claim, are HYPOTHESES, not established facts. The SAR (5-substitution tolerated; 5-Br/5-Ph
    best) is the *only* experimental basis for the exit-vector choice.
  * NONE of the enumerated analogues carries any measured potency, selectivity, or binding. They are
    DESIGN PROPOSALS. No activity value is asserted for any of them.
  * Every emitted SMILES is required to PARSE + SANITIZE in RDKit; anything that fails is DROPPED (not
    emitted) and counted. InChIKey is computed by RDKit; if RDKit's InChI backend is unavailable the
    field is emitted as null and flagged.

The enumeration is a CURATED table (quality over quantity, ~15-25 compounds) across four classes:
  1. exit_vector_sub   -- replace the 5-Br with a chemically distinct linker-attachment handle
  2. bioisostere       -- replace the 3-methyl-ester while PRESERVING the 3-carboxylate H-bond SAR
                          (5-Br retained as the anchor; indole NH always kept)
  3. microstate_variant-- variants chosen to make the pH-7.4 dominant microstate explicit / unambiguous
  4. comparator        -- 2-3 denovo_401 analogues retained ONLY as a comparator baseline (is_comparator)

Pure-CPU RDKit + stdlib only. No GPU, no AWS, no network. The pure structural-integrity logic
(`REQUIRED_FIELDS`, `VALID_CLASSES`, `check_enum_table`) is import-safe without RDKit and unit-tested in
tests/test_congeneric_warhead_enum.py. Output: congeneric-warhead-series.json
"""
import json
import os
import sys

OUT = os.path.join(os.path.dirname(__file__), "congeneric-warhead-series.json")
ENUM_VERSION = "1.0.0"

# The anchor structure (verified: parses in RDKit; MW 254.08; C10H8BrNO2; skeleton = methyl
# 5-bromo-1H-indole-3-carboxylate). Recorded in the header, not as an enumerated "modification".
ANCHOR_ID = "zaienne_cmpd19"
ANCHOR_SMILES = "COC(=O)c1c[nH]c2ccc(Br)cc12"

# denovo_401 SMILES resolved from the repo's authoritative sources (nr4a3_pose_validity.py,
# nr4a3-antitarget-denovo401.json, nr4a3_developability.py, nr4a3_admet_ext.py -- all identical). Since
# it IS authoritatively resolved, the comparator series carries real structures (needs_resolution=False).
DENOVO401_ID = "denovo_401"
DENOVO401_SMILES = "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"

# ---------------------------------------------------------------------------------------------------
# Pure structural-integrity contract (import-safe; unit-tested without RDKit) ------------------------
# ---------------------------------------------------------------------------------------------------
VALID_CLASSES = ("exit_vector_sub", "bioisostere", "microstate_variant", "comparator")
REQUIRED_FIELDS = ("id", "parent", "cls", "smiles", "modification", "exit_vector_atom_hint",
                   "predicted_dominant_microstate_pH7.4", "microstate_ambiguous", "rationale",
                   "is_comparator")


def check_enum_table(enum):
    """Validate the curated ENUM table's structural integrity WITHOUT touching RDKit. Returns a list of
    human-readable problem strings (empty == clean). Checked: unique ids; class in VALID_CLASSES; every
    REQUIRED_FIELD present; microstate_ambiguous / is_comparator are bools; comparator<->is_comparator
    consistency; comparator parent is denovo_401, non-comparator parent is the anchor; smiles present."""
    problems = []
    seen = set()
    for e in enum:
        eid = e.get("id", "<no-id>")
        if eid in seen:
            problems.append("duplicate id: %s" % eid)
        seen.add(eid)
        for f in REQUIRED_FIELDS:
            if f not in e:
                problems.append("%s: missing field %s" % (eid, f))
        cls = e.get("cls")
        if cls not in VALID_CLASSES:
            problems.append("%s: invalid class %r" % (eid, cls))
        if not isinstance(e.get("microstate_ambiguous"), bool):
            problems.append("%s: microstate_ambiguous must be bool" % eid)
        if not isinstance(e.get("is_comparator"), bool):
            problems.append("%s: is_comparator must be bool" % eid)
        if (cls == "comparator") != bool(e.get("is_comparator")):
            problems.append("%s: comparator class <-> is_comparator mismatch" % eid)
        if cls == "comparator" and e.get("parent") != DENOVO401_ID:
            problems.append("%s: comparator parent must be %s" % (eid, DENOVO401_ID))
        if cls != "comparator" and e.get("parent") != ANCHOR_ID:
            problems.append("%s: non-comparator parent must be %s" % (eid, ANCHOR_ID))
        if not e.get("smiles"):
            problems.append("%s: empty smiles" % eid)
    return problems


# ---------------------------------------------------------------------------------------------------
# The curated congeneric enumeration. `smiles` here are INPUT structures; main() re-canonicalizes them
# through RDKit and drops any that fail to parse/sanitize. Every entry keeps the indole NH intact.
# ---------------------------------------------------------------------------------------------------
ENUM = [
    # ---- 1. exit_vector_sub : replace 5-Br with a distinct linker-attachment handle ----------------
    {
        "id": "cw_ev_5nh2",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(N)cc12",
        "modification": "5-Br -> 5-NH2 (aryl amine handle for amide/urea linker coupling)",
        "exit_vector_atom_hint": "5-position aniline N (amide/urea attachment)",
        "predicted_dominant_microstate_pH7.4": "neutral (aryl amine, conjugate-acid pKa ~4.6)",
        "microstate_ambiguous": False,
        "rationale": "Aryl amine gives an amide/urea coupling vector at the SAR-favored 5-position; "
                     "weakly basic aniline is predominantly neutral at 7.4, so the microstate is clear.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5oh",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(O)cc12",
        "modification": "5-Br -> 5-OH (phenol handle for ether/ester/carbamate linker)",
        "exit_vector_atom_hint": "5-position phenol O (ether/carbamate attachment)",
        "predicted_dominant_microstate_pH7.4": "neutral (phenol, pKa ~10)",
        "microstate_ambiguous": False,
        "rationale": "Phenolic O is a clean O-alkylation vector; neutral at 7.4. Small, minimally "
                     "perturbing to the modeled pocket relative to Br.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5cooh",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(C(=O)O)cc12",
        "modification": "5-Br -> 5-COOH (carboxyl handle for amide-linker coupling)",
        "exit_vector_atom_hint": "5-position carboxyl C (amide-bond linker attachment)",
        "predicted_dominant_microstate_pH7.4": "anionic carboxylate (pKa ~4)",
        "microstate_ambiguous": True,
        "rationale": "Direct amide-coupling vector, but the free acid is ionized at 7.4 (acid/carboxylate) "
                     "-- microstate is DISPREFERRED for a clean neutral warhead; used as coupling "
                     "intermediate, expected to be consumed into a neutral amide in the final degrader.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5alkyne",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(C#C)cc12",
        "modification": "5-Br -> 5-C#CH (terminal alkyne; CuAAC/click linker handle)",
        "exit_vector_atom_hint": "5-position terminal alkyne C (azide click / Sonogashira)",
        "predicted_dominant_microstate_pH7.4": "neutral",
        "microstate_ambiguous": False,
        "rationale": "Terminal alkyne is a compact, neutral, orthogonal click handle -- ideal for rapid "
                     "combinatorial linker attachment in the ternary matrix; unambiguous microstate.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5ch2nh2",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(CN)cc12",
        "modification": "5-Br -> 5-CH2NH2 (benzylic primary amine handle)",
        "exit_vector_atom_hint": "5-position aminomethyl N (amide/reductive-amination attachment)",
        "predicted_dominant_microstate_pH7.4": "cationic (protonated 1' amine, pKa ~9.3)",
        "microstate_ambiguous": True,
        "rationale": "Flexible benzylic amine vector, but a basic aliphatic amine is protonated/cationic "
                     "at 7.4 -- flagged; the cation may perturb pocket electrostatics and is usually "
                     "acylated into a neutral amide in the assembled degrader.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5opropargyl",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(OCC#C)cc12",
        "modification": "5-Br -> 5-O-CH2-C#CH (propargyl ether; click handle on an ether tether)",
        "exit_vector_atom_hint": "propargyl-ether terminal alkyne C (click), O-tethered off 5-position",
        "predicted_dominant_microstate_pH7.4": "neutral (ether)",
        "microstate_ambiguous": False,
        "rationale": "Neutral ether-tethered click handle -- combines a defined exit geometry with a "
                     "clean microstate; a step-out from the ring plane vs the bare 5-alkyne.",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5piperazine",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(N3CCNCC3)cc12",
        "modification": "5-Br -> 5-piperazin-1-yl (secondary-amine handle; common PROTAC linker node)",
        "exit_vector_atom_hint": "distal piperazine N (acylation/alkylation to the linker)",
        "predicted_dominant_microstate_pH7.4": "cationic (distal N protonated, pKa ~9.8, mono-protonated)",
        "microstate_ambiguous": True,
        "rationale": "Piperazine is a workhorse linker node with a built-in solubilizing handle, but is "
                     "cationic at 7.4 -- flagged; useful where the distal N becomes an amide in the "
                     "final construct (removing the charge).",
        "is_comparator": False,
    },
    {
        "id": "cw_ev_5pegamine",
        "parent": ANCHOR_ID, "cls": "exit_vector_sub",
        "smiles": "COC(=O)c1c[nH]c2ccc(OCCOCCN)cc12",
        "modification": "5-Br -> 5-O-CH2CH2-O-CH2CH2-NH2 (short PEG2-amine stub)",
        "exit_vector_atom_hint": "terminal PEG primary amine N (amide coupling to the E3-recruiter arm)",
        "predicted_dominant_microstate_pH7.4": "cationic (terminal 1' amine, pKa ~9.5)",
        "microstate_ambiguous": True,
        "rationale": "A PEG-amine stub previews solubility + a realistic amide-coupling geometry to the "
                     "E3 arm; terminal amine is cationic at 7.4 -- flagged; becomes a neutral amide "
                     "once conjugated.",
        "is_comparator": False,
    },

    # ---- 2. bioisostere : replace the 3-methyl ester, PRESERVE the carboxylate H-bond SAR ----------
    #        (5-Br retained as the SAR anchor; indole NH always kept)
    {
        "id": "cw_bio_primary_amide",
        "parent": ANCHOR_ID, "cls": "bioisostere",
        "smiles": "NC(=O)c1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-C(=O)NH2 (primary carboxamide bioisostere)",
        "exit_vector_atom_hint": "5-position (Br retained as placeholder for a linker handle)",
        "predicted_dominant_microstate_pH7.4": "neutral (amide)",
        "microstate_ambiguous": False,
        "rationale": "Primary amide preserves the 3-carbonyl H-bond acceptor and adds an NH donor while "
                     "removing the hydrolyzable ester; neutral, unambiguous microstate.",
        "is_comparator": False,
    },
    {
        "id": "cw_bio_nmethyl_amide",
        "parent": ANCHOR_ID, "cls": "bioisostere",
        "smiles": "CNC(=O)c1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-C(=O)NHMe (N-methyl carboxamide bioisostere)",
        "exit_vector_atom_hint": "5-position (Br retained); amide N-substituent is a secondary vector option",
        "predicted_dominant_microstate_pH7.4": "neutral (amide)",
        "microstate_ambiguous": False,
        "rationale": "N-methyl carboxamide keeps the carbonyl acceptor + one NH donor and is metabolically "
                     "more robust than the ester; the amide N is a possible secondary exit vector.",
        "is_comparator": False,
    },
    {
        "id": "cw_bio_tetrazole",
        "parent": ANCHOR_ID, "cls": "bioisostere",
        "smiles": "Brc1ccc2[nH]cc(-c3n[nH]nn3)c2c1",
        "modification": "3-CO2Me -> 3-(1H-tetrazol-5-yl) (classic carboxylate bioisostere)",
        "exit_vector_atom_hint": "5-position (Br retained as placeholder for a linker handle)",
        "predicted_dominant_microstate_pH7.4": "anionic (tetrazolate, pKa ~4.9)",
        "microstate_ambiguous": True,
        "rationale": "Tetrazole is the canonical carboxylate isostere and would mimic a 3-carboxyLATE "
                     "(rather than the neutral ester) H-bond pattern; it is anionic at 7.4 -- flagged. "
                     "Included because if the bound species is the carboxylate, this is the better mimic.",
        "is_comparator": False,
    },
    {
        "id": "cw_bio_acylsulfonamide",
        "parent": ANCHOR_ID, "cls": "bioisostere",
        "smiles": "CS(=O)(=O)NC(=O)c1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-C(=O)NH-SO2Me (N-acylsulfonamide carboxylate bioisostere)",
        "exit_vector_atom_hint": "5-position (Br retained as placeholder for a linker handle)",
        "predicted_dominant_microstate_pH7.4": "anionic (acidic acylsulfonamide NH, pKa ~4-5)",
        "microstate_ambiguous": True,
        "rationale": "Acylsulfonamide is an acidic carboxylate isostere retaining the carbonyl acceptor; "
                     "anionic at 7.4 -- flagged. Pairs with the tetrazole as an anionic-mimic hypothesis.",
        "is_comparator": False,
    },
    {
        "id": "cw_bio_hydroxamic",
        "parent": ANCHOR_ID, "cls": "bioisostere",
        "smiles": "ONC(=O)c1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-C(=O)NHOH (hydroxamic acid)",
        "exit_vector_atom_hint": "5-position (Br retained as placeholder for a linker handle)",
        "predicted_dominant_microstate_pH7.4": "neutral (hydroxamic acid, pKa ~9; >95% neutral at 7.4)",
        "microstate_ambiguous": False,
        "rationale": "Hydroxamic acid keeps the carbonyl acceptor and adds a donor/acceptor NHOH; weakly "
                     "acidic (pKa ~9) so predominantly neutral at 7.4. Note metal-chelation liability to "
                     "watch downstream (not asserted here).",
        "is_comparator": False,
    },

    # ---- 3. microstate_variant : make the pH-7.4 dominant microstate explicit ----------------------
    {
        "id": "cw_ms_free_acid",
        "parent": ANCHOR_ID, "cls": "microstate_variant",
        "smiles": "OC(=O)c1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-CO2H (ester-hydrolysis product / free acid of compound 19)",
        "exit_vector_atom_hint": "5-position (Br retained); 3-carboxyl also couplable",
        "predicted_dominant_microstate_pH7.4": "anionic carboxylate (pKa ~4)",
        "microstate_ambiguous": True,
        "rationale": "Explicitly records the ester-vs-acid ambiguity: the likely in-vitro/in-vivo "
                     "hydrolysis product of compound 19 is the 3-carboxylate, ionized at 7.4. Which "
                     "species (neutral ester vs anionic acid) actually engages NR4A3 is UNKNOWN, so both "
                     "microstates must be carried into any binding calc.",
        "is_comparator": False,
    },
    {
        "id": "cw_ms_carbinol",
        "parent": ANCHOR_ID, "cls": "microstate_variant",
        "smiles": "OCc1c[nH]c2ccc(Br)cc12",
        "modification": "3-CO2Me -> 3-CH2OH (primary alcohol; neutral H-bond donor/acceptor)",
        "exit_vector_atom_hint": "5-position (Br retained); 3-CH2OH is an alternate neutral coupling vector",
        "predicted_dominant_microstate_pH7.4": "neutral (primary alcohol)",
        "microstate_ambiguous": False,
        "rationale": "Preferred UNAMBIGUOUS-microstate variant: a neutral carbinol retains an H-bond "
                     "donor/acceptor near the 3-position without any pH-dependent charge, de-risking the "
                     "microstate uncertainty of the ester/acid pair (with the SAR caveat that it drops "
                     "the carbonyl).",
        "is_comparator": False,
    },
    {
        "id": "cw_ms_5acetamido_ester",
        "parent": ANCHOR_ID, "cls": "microstate_variant",
        "smiles": "COC(=O)c1c[nH]c2ccc(NC(C)=O)cc12",
        "modification": "5-Br -> 5-NHAc (neutral acetamide 'capped' exit vector; ester retained)",
        "exit_vector_atom_hint": "5-position amide N (models a neutral amide-linked attachment)",
        "predicted_dominant_microstate_pH7.4": "neutral (acetamide)",
        "microstate_ambiguous": False,
        "rationale": "Neutral, unambiguous alternative to the basic 5-amine handles: a 5-acetamide "
                     "previews the electronics/geometry of a real amide-linked degrader attachment "
                     "WITHOUT introducing a charged microstate.",
        "is_comparator": False,
    },

    # ---- 4. comparator : denovo_401 analogues (baseline ONLY; is_comparator=True) ------------------
    {
        "id": "cw_cmp_denovo401",
        "parent": DENOVO401_ID, "cls": "comparator",
        "smiles": DENOVO401_SMILES,
        "modification": "denovo_401 parent (generated NR4A3 lead; retained as comparator baseline)",
        "exit_vector_atom_hint": "n/a for this series -- comparator only; not a congeneric warhead design",
        "predicted_dominant_microstate_pH7.4": "neutral (ether + tertiary/secondary alcohol; no ionizable group)",
        "microstate_ambiguous": False,
        "rationale": "The generated de-novo lead, kept ONLY as a comparator against the experimentally "
                     "anchored congeneric series. SMILES is authoritatively resolved from repo sources "
                     "(nr4a3_pose_validity.py et al.); no needs_resolution.",
        "is_comparator": True,
    },
    {
        "id": "cw_cmp_denovo401_desmethyl",
        "parent": DENOVO401_ID, "cls": "comparator",
        "smiles": "OC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",
        "modification": "denovo_401 methyl ether -> free primary alcohol (des-methyl analogue)",
        "exit_vector_atom_hint": "n/a for this series -- comparator only",
        "predicted_dominant_microstate_pH7.4": "neutral (diol; no ionizable group)",
        "microstate_ambiguous": False,
        "rationale": "Minimal comparator perturbation of denovo_401 (O-demethylation) to probe how the "
                     "comparator baseline moves under a small change; comparator only, no activity claimed.",
        "is_comparator": True,
    },
    {
        "id": "cw_cmp_denovo401_4f",
        "parent": DENOVO401_ID, "cls": "comparator",
        "smiles": "COC[C@H](c1ccc(F)cc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",
        "modification": "denovo_401 phenyl -> 4-fluorophenyl (comparator analogue)",
        "exit_vector_atom_hint": "n/a for this series -- comparator only",
        "predicted_dominant_microstate_pH7.4": "neutral (ether + alcohol; no ionizable group)",
        "microstate_ambiguous": False,
        "rationale": "A second small comparator variant (para-F) on denovo_401; comparator only, "
                     "retained solely to anchor the generated-scaffold baseline, not proposed as a warhead.",
        "is_comparator": True,
    },
]


# ---------------------------------------------------------------------------------------------------
def build_records(Chem):
    """Validate + canonicalize each ENUM entry through RDKit. Returns (records, drops).
    An entry is DROPPED (never emitted) if its SMILES fails to parse/sanitize. Emitted records carry the
    RDKit-canonical SMILES + InChIKey (InChIKey null if the InChI backend is unavailable)."""
    records = []
    drops = []
    inchi_ok = _inchi_available(Chem)
    for e in ENUM:
        mol = None
        try:
            mol = Chem.MolFromSmiles(e["smiles"])  # MolFromSmiles sanitizes by default
        except Exception as ex:  # noqa
            drops.append({"id": e["id"], "smiles": e["smiles"], "reason": "exception: %s" % ex})
            continue
        if mol is None:
            drops.append({"id": e["id"], "smiles": e["smiles"], "reason": "failed to parse/sanitize"})
            continue
        canonical = Chem.MolToSmiles(mol)
        inchikey = None
        if inchi_ok:
            try:
                inchikey = Chem.MolToInchiKey(mol) or None
            except Exception:  # noqa
                inchikey = None
        rec = {
            "id": e["id"],
            "parent": e["parent"],
            "class": e["cls"],
            "smiles": canonical,
            "inchikey": inchikey,
            "modification": e["modification"],
            "exit_vector_atom_hint": e["exit_vector_atom_hint"],
            "predicted_dominant_microstate_pH7.4": e["predicted_dominant_microstate_pH7.4"],
            "microstate_ambiguous": e["microstate_ambiguous"],
            "rationale": e["rationale"],
            "is_comparator": e["is_comparator"],
        }
        records.append(rec)
    return records, drops


def _inchi_available(Chem):
    try:
        return Chem.MolToInchiKey(Chem.MolFromSmiles("c1ccccc1")) is not None
    except Exception:  # noqa
        return False


def summarize(records):
    by_class = {}
    n_ambiguous = 0
    n_comparator = 0
    for r in records:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        if r["microstate_ambiguous"]:
            n_ambiguous += 1
        if r["is_comparator"]:
            n_comparator += 1
    return {"n_compounds": len(records), "by_class": by_class,
            "n_microstate_ambiguous": n_ambiguous, "n_comparator": n_comparator}


def main():
    problems = check_enum_table(ENUM)
    if problems:
        for p in problems:
            print("ENUM INTEGRITY:", p, file=sys.stderr)
        sys.exit("ABORT: ENUM table failed structural-integrity check (%d problems)" % len(problems))

    from rdkit import Chem

    # anchor + denovo_401 canonical references (for the header; the anchor is NOT an enumerated compound)
    anchor_mol = Chem.MolFromSmiles(ANCHOR_SMILES)
    if anchor_mol is None:
        sys.exit("ABORT: anchor SMILES did not parse -- refusing to emit")
    inchi_ok = _inchi_available(Chem)
    anchor = {"id": ANCHOR_ID, "smiles": Chem.MolToSmiles(anchor_mol),
              "inchikey": (Chem.MolToInchiKey(anchor_mol) if inchi_ok else None),
              "name": "methyl 5-bromoindole-3-carboxylate",
              "source": {"pmid": "35704774", "pmc": "PMC9542104", "doi": "10.1002/cmdc.202200259"}}
    d401_mol = Chem.MolFromSmiles(DENOVO401_SMILES)
    denovo401 = {"id": DENOVO401_ID,
                 "smiles": (Chem.MolToSmiles(d401_mol) if d401_mol is not None else None),
                 "inchikey": (Chem.MolToInchiKey(d401_mol) if (inchi_ok and d401_mol is not None) else None),
                 "needs_resolution": False,
                 "resolution_note": ("denovo_401 SMILES is authoritatively resolved from repo sources "
                                     "(nr4a3_pose_validity.py, nr4a3-antitarget-denovo401.json, "
                                     "nr4a3_developability.py, nr4a3_admet_ext.py -- all identical). "
                                     "No structure was invented.")}

    records, drops = build_records(Chem)
    summary = summarize(records)

    out = {
        "_schema": "congeneric_warhead_series",
        "version": ENUM_VERSION,
        "purpose": ("Focused congeneric warhead enumeration around the experimentally-anchored NR4A3 tool "
                    "compound (Zaienne 2022 compound 19), for the ternary-first NR4A3-degrader program's "
                    "RBFE + ternary-selectivity matrix. Design proposals only."),
        "anchor": anchor,
        "denovo401_comparator": denovo401,
        "caveats": {
            "pose_and_exit_vector_are_hypotheses": (
                "Compound 19 is FUNCTIONAL target engagement only (blocks NOR-1<->SMRT/NCoR1, derepresses "
                "MYC; SMRT IC50 9+/-2 uM). There is NO solved NR4A3-19 cocrystal, so the binding pose and "
                "therefore the '5-position is the linker exit vector' assignment are HYPOTHESES, not "
                "established. The only experimental basis for the 5-position exit vector is the published "
                "5-substitution SAR (5-Br/5-Ph most potent)."),
            "no_activity_claimed": ("NONE of the enumerated analogues carries any measured or predicted "
                                    "potency, selectivity, or binding. They are design proposals only; no "
                                    "activity value is asserted."),
            "microstates": ("predicted_dominant_microstate_pH7.4 is a rule-of-thumb pKa estimate, not a "
                            "measured/calculated pKa. Any compound flagged microstate_ambiguous must have "
                            "BOTH candidate microstates carried into downstream binding calculations."),
            "chemistry_validation": ("Every emitted SMILES parses + sanitizes in RDKit; failures are "
                                     "dropped (see dropped_for_invalid_chemistry) and counted. InChIKeys "
                                     "are RDKit-computed (null if the InChI backend is unavailable)."),
            "indole_nh_preserved": "The indole N-H is retained in every enumerated compound (SAR).",
        },
        "class_definitions": {
            "exit_vector_sub": "5-Br replaced by a distinct linker-attachment handle (hypothesized exit vector).",
            "bioisostere": "3-methyl-ester replaced while preserving the 3-carboxylate H-bond SAR; 5-Br retained.",
            "microstate_variant": "variant chosen to make the pH-7.4 dominant microstate explicit/unambiguous.",
            "comparator": "denovo_401 analogue retained ONLY as a comparator baseline (is_comparator=true).",
        },
        "inchikey_backend_available": inchi_ok,
        "summary": summary,
        "dropped_for_invalid_chemistry": drops,
        "n_dropped": len(drops),
        "compounds": records,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote %s" % OUT)
    print("  compounds=%d  by_class=%s  ambiguous=%d  comparator=%d  dropped=%d  inchi=%s" % (
        summary["n_compounds"], summary["by_class"], summary["n_microstate_ambiguous"],
        summary["n_comparator"], len(drops), inchi_ok))
    for r in records:
        print("  %-28s %-18s amb=%-5s %s" % (r["id"], r["class"], r["microstate_ambiguous"],
                                             (r["inchikey"] or "-")))


if __name__ == "__main__":
    main()
