#!/usr/bin/env python3
"""
Build the versioned `published_warhead_registry` — the Phase-1 / Workstream-B deliverable of the
NR4A3-selective-degrader master brief (deliverables 30-33).

This is the machine-readable catalog of the *published, experimentally anchored* NR4A chemistry the
program must benchmark against (co-equal priority with the generated de-novo molecules — brief rule 18):

  1. NR4A3 / NOR-1 direct chemistry            (Zaienne 2022 fragment->inverse-agonist series)
  2. NR4A1 / Nur77 ligand panel                (anti-target controls + warhead sources)
  3. NR4A2 / Nurr1 ligand panel                (anti-target controls; the hardest paralogue to spare)
  4. NR-V04 reference degrader + controls      (Wang 2024; VHL-recruiting NR4A1 PROTAC precedent)
  5. E3-ligase ligands                         (VHL / CRBN handles used in the degrader-assembly work)

Every compound carries an EVIDENCE CLASS and a SOURCE (PMID/DOI/PMC/PDB). Structures are NOT
hard-coded: for every named compound the builder resolves an isomeric SMILES + InChIKey from up to
THREE independent public resolvers (ChEMBL, PubChem PUG-REST, NCI CACTUS) and cross-checks them by
InChIKey skeleton (first 14 chars). `structure_confidence` = "high" when >=2 resolvers agree on the
skeleton, "medium" when 1 resolves, "unresolved" when none do (novel medchem matter behind a paywall
is recorded HONESTLY as unresolved with smiles=null — never invented; brief golden rule).

Needs internet + RDKit, which the dev sandbox lacks -> runs on a GitHub-hosted CPU runner
(published-warhead-registry.yml). No GPU / no AWS. Triage-grade cheminformatics; not a validated lead.

Output: published-warhead-registry.json  (published to the modalities-cache branch)

The pure structure-agreement logic (`skeleton`, `reconcile_structures`) is import-safe without RDKit
or internet and is unit-tested in tests/test_published_warhead_registry.py.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
PUBCHEM = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
CACTUS = "https://cactus.nci.nih.gov/chemical/structure"
OUT = os.path.join(os.path.dirname(__file__), "published-warhead-registry.json")
REGISTRY_VERSION = "1.0.0"

# ---------------------------------------------------------------------------------------------------
# CURATED COMPOUND TABLE — real, published NR4A chemistry with evidence class + source.
# `resolve` = ordered synonyms to hand the resolvers (most-specific first). explicit CID/ChEMBL ids go
# in `resolve` prefixed pubchem:/chembl: to pin an exact record when a common name is ambiguous.
# `smiles` is left null and filled by the resolvers on the runner; a curated `smiles_hint` may seed a
# compound the resolvers cannot name (used ONLY as a labelled hint, cross-checked, never as fact).
# ---------------------------------------------------------------------------------------------------
REGISTRY = [
    # ---- 1. NR4A3 / NOR-1 direct chemistry — Zaienne 2022 (the primary published NR4A3 warhead source)
    {
        "id": "zaienne_nor1_series",
        "display_name": "Zaienne 2022 NOR-1 fragment->inverse-agonist series",
        "role": "warhead_source",
        "targets": ["NR4A3"],
        "evidence_class": "functional_plus_fragment",
        "evidence_notes": (
            "Drug-fragment library screened for NOR-1/NR4A3 modulation (Gal4-NR4A3 hybrid reporter). "
            "Hit rate <1%; THREE ligand chemotypes recovered, ONE rapidly elaborated to a low-micromolar "
            "INVERSE NOR-1 agonist that shifted a NOR-1-regulated gene in cells. Direct-engagement of the "
            "modeled cryptic orthosteric pocket is NOT established by the reporter/cellular data (brief 3.2)."
        ),
        "assay": "Gal4-NR4A3 hybrid cell reporter; cellular target-gene modulation",
        "potency": "low micromolar (elaborated inverse agonist)",
        "selectivity_notes": "NR4A1/NR4A2 counter-screen per the paper; verify from SI when OA text lands",
        "source": {"authors": "Zaienne D, Arifi S, Marschner JA, Heering J, et al.",
                    "title": "Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse NOR-1 Agonists",
                    "journal": "ChemMedChem 17(16):e202200259 (2022)",
                    "pmid": "35704774", "pmc": "PMC9542104", "doi": "10.1002/cmdc.202200259"},
        "structure_status": "series_placeholder",
        "resolve": [],   # novel medchem; individual members are not name-resolvable -> unresolved by design
        "note": ("Series-level record. Individual member structures are behind the ChemMedChem paywall; the "
                 "OA full text (fetch-literature -> literature-cache) is needed to transcribe the elaborated "
                 "compound's structure + assay values. Recorded as unresolved rather than invented."),
    },

    # ---- 2. NR4A1 / Nur77 ligand panel (anti-target controls + warhead sources) --------------------
    {
        "id": "cytosporone_b",
        "display_name": "Cytosporone B (Csn-B)",
        "role": "pan_nr4a_direct_binder",
        "targets": ["NR4A1", "NR4A2", "NR4A3"],
        "evidence_class": "direct_binding_structural_and_nmr",
        "evidence_notes": (
            "First-described natural Nur77/NR4A1 agonist; binds the Nur77 LBD (Zhan 2008). Independently "
            "confirmed to directly bind the Nurr1/NR4A2 LBD by protein-NMR footprinting (Munoz-Tello 2021). "
            "Analog cocrystals localize to Nur77 LBD surface pockets; NMR places Csn-B in the Nurr1 "
            "orthosteric pocket. A genuine cross-NR4A direct binder -> the key positive-control ligand."
        ),
        "assay": "Nur77 reporter/agonism (Zhan); Nurr1 LBD protein-NMR (Munoz-Tello)",
        "potency": "low micromolar",
        "selectivity_notes": "pan-NR4A binder (Nur77 + Nurr1); NOT a selectivity exemplar",
        "source": {"pmid_zhan": "18690216", "ref_zhan": "Zhan et al. Nat Chem Biol 2008 (nchembio.106)",
                    "pmid_munoztello": "33289551", "pmc_munoztello": "PMC8006468",
                    "ref_munoztello": "Munoz-Tello et al. J Med Chem 2021"},
        "resolve": ["cytosporone B", "chembl:CHEMBL1221517"],
    },
    {
        "id": "thpn",
        "display_name": "THPN (1-(3,4,5-trihydroxyphenyl)nonan-1-one)",
        "role": "nr4a1_direct_binder",
        "targets": ["NR4A1"],
        "evidence_class": "direct_binding_structural",
        "evidence_notes": "Nur77 LBD agonist; cocrystal with the Nur77 LBD (PDB 4JGV). Crystallographic direct-binding anchor for NR4A1.",
        "assay": "Nur77 LBD X-ray cocrystal (4JGV) + functional",
        "potency": "n/a (structural)",
        "selectivity_notes": "NR4A1-directed control ligand",
        "source": {"pdb": "4JGV", "ref": "Zhan et al. (Nur77 LBD-THPN cocrystal)"},
        "resolve": ["THPN nuclear receptor", "1-(3,4,5-trihydroxyphenyl)nonan-1-one",
                     "1-(3,4,5-trihydroxyphenyl)-1-nonanone"],
    },
    {
        "id": "tmpa",
        "display_name": "TMPA (ethyl 2-[2,3,4-trimethoxy-6-(1-octanoyl)phenyl]acetate)",
        "role": "nr4a1_functional_modulator",
        "targets": ["NR4A1"],
        "evidence_class": "functional_modulator",
        "evidence_notes": ("Binds Nur77 to modulate the Nur77-LKB1 axis (Zhan 2012). NOT a Nurr1 LBD binder "
                            "in the Munoz-Tello NMR assessment -> a NR4A1-leaning functional control."),
        "assay": "Nur77 functional (LKB1 cytoplasmic axis)",
        "potency": "sub-micromolar (functional)",
        "selectivity_notes": "does NOT bind Nurr1 LBD (Munoz-Tello 2021) -> NR4A1 vs NR4A2 discriminator control",
        "source": {"pmid_munoztello": "33289551", "ref": "Zhan et al. Nat Chem Biol 2012; Munoz-Tello 2021 (non-binder)"},
        "resolve": ["TMPA", "ethyl 2-[2,3,4-trimethoxy-6-octanoylphenyl]acetate"],
    },
    {
        "id": "cdim8_dimcpphoh",
        "display_name": "C-DIM8 / DIM-C-pPhOH (1,1-bis(3'-indolyl)-1-(p-hydroxyphenyl)methane)",
        "role": "nr4a1_functional_modulator",
        "targets": ["NR4A1"],
        "evidence_class": "functional_modulator",
        "evidence_notes": "para-hydroxyphenyl C-substituted DIM; Nur77/NR4A1 functional modulator (Safe lab). Cellular NR4A1-dependent activity; direct-LBD-binding not cleanly established.",
        "assay": "NR4A1-dependent cellular assays",
        "potency": "micromolar",
        "selectivity_notes": "NR4A1-oriented functional control",
        "source": {"ref": "Safe et al. (C-DIM/NR4A1 series)"},
        "resolve": ["DIM-C-pPhOH", "1,1-bis(3-indolyl)-1-(4-hydroxyphenyl)methane", "C-DIM8"],
    },

    # ---- 3. NR4A2 / Nurr1 ligand panel (anti-target controls; NR4A2 is the hardest paralogue to spare)
    {
        "id": "amodiaquine",
        "display_name": "Amodiaquine",
        "role": "nr4a2_direct_binder",
        "targets": ["NR4A2", "NR4A1", "NR4A3"],
        "evidence_class": "direct_binding_nmr",
        "evidence_notes": ("4-aminoquinoline antimalarial; directly binds the Nurr1/NR4A2 LBD by protein-NMR "
                            "footprinting (Munoz-Tello 2021) and modulates Nurr1 activity. A cross-NR4A binder "
                            "-> a strong ANTI-TARGET control (an NR4A3-selective molecule must NOT resemble it)."),
        "assay": "Nurr1 LBD protein-NMR; Nurr1 reporter",
        "potency": "micromolar",
        "selectivity_notes": "binds Nurr1 (and the NR4A family) -> anti-target promiscuity control",
        "source": {"pmid": "33289551", "pmc": "PMC8006468", "ref": "Munoz-Tello et al. J Med Chem 2021"},
        "resolve": ["amodiaquine", "chembl:CHEMBL682"],
    },
    {
        "id": "chloroquine",
        "display_name": "Chloroquine",
        "role": "nr4a2_direct_binder",
        "targets": ["NR4A2"],
        "evidence_class": "direct_binding_nmr",
        "evidence_notes": "4-aminoquinoline; directly binds the Nurr1/NR4A2 LBD by protein-NMR (Munoz-Tello 2021). Chloroquinoline-amine Nurr1-activator chemotype (also de Vera 2021).",
        "assay": "Nurr1 LBD protein-NMR; Nurr1 reporter",
        "potency": "micromolar",
        "selectivity_notes": "Nurr1-directed anti-target control",
        "source": {"pmid": "33289551", "ref": "Munoz-Tello 2021; de Vera et al. 2021 (chloroquinoline-amines)"},
        "resolve": ["chloroquine", "chembl:CHEMBL76"],
    },
    {
        "id": "dhi",
        "display_name": "5,6-Dihydroxyindole (DHI)",
        "role": "nr4a2_covalent_binder",
        "targets": ["NR4A2"],
        "evidence_class": "covalent_crystal",
        "evidence_notes": ("Endogenous-melanin-pathway indole; NR4A2/Nurr1 LBD cocrystal, COVALENTLY bound to "
                            "Cys566 behind helix 12 (a non-orthosteric, covalent mode). Treat as covalent (not a "
                            "clean reversible orthosteric control)."),
        "assay": "Nurr1 LBD X-ray cocrystal (covalent Cys566)",
        "potency": "n/a (covalent)",
        "selectivity_notes": "covalent NR4A2 mode; special-handling like the celastrol/NR-V04 warhead",
        "source": {"ref": "Nurr1 LBD-DHI / -PGA1 covalent cocrystals (Cys566)"},
        "expected_mw": 149.15,   # C8H7NO2; disambiguates the parent indole from carboxylic-acid derivatives
        "resolve": ["5,6-dihydroxyindole", "5,6-dihydroxy-1H-indole"],
    },
    {
        "id": "pga1",
        "display_name": "Prostaglandin A1 (PGA1)",
        "role": "nr4a2_covalent_binder",
        "targets": ["NR4A2"],
        "evidence_class": "covalent_crystal",
        "evidence_notes": "Cyclopentenone prostaglandin; NR4A2/Nurr1 LBD cocrystal, covalently bound to Cys566 behind H12 (Michael acceptor). Covalent NR4A2 control.",
        "assay": "Nurr1 LBD X-ray cocrystal (covalent Cys566)",
        "potency": "n/a (covalent)",
        "selectivity_notes": "covalent NR4A2 mode",
        "source": {"ref": "Nurr1 LBD-PGA1 covalent cocrystal (Cys566)"},
        "resolve": ["prostaglandin A1", "PGA1"],
    },
    {
        "id": "c_dim12",
        "display_name": "C-DIM12 / DIM-C-pPhtBu",
        "role": "nr4a2_functional_modulator",
        "targets": ["NR4A2"],
        "evidence_class": "functional_nonbinder",
        "evidence_notes": ("para-t-butyl C-substituted DIM; widely used as a Nurr1 'activator' in cells but "
                            "does NOT bind the Nurr1 LBD in the Munoz-Tello 2021 NMR assessment -> a functional-"
                            "modulator-but-non-LBD-binder control (important negative for the docking benchmark)."),
        "assay": "cellular Nurr1-dependent readouts (NMR: non-binder)",
        "potency": "micromolar (functional)",
        "selectivity_notes": "non-LBD-binder control -> the model should NOT dock it as a strong LBD binder",
        "source": {"pmid": "33289551", "ref": "Munoz-Tello 2021 (non-binder); Safe/De Miranda C-DIM12"},
        "resolve": ["DIM-C-pPhtBu", "1,1-bis(3-indolyl)-1-(4-tert-butylphenyl)methane", "C-DIM12"],
    },

    # ---- 4. NR-V04 reference degrader + controls (Wang 2024) — stored separately (covalent warhead) --
    {
        "id": "celastrol",
        "display_name": "Celastrol",
        "role": "nrv04_warhead",
        "targets": ["NR4A1"],
        "evidence_class": "reactive_covalent_functional",
        "evidence_notes": ("Pentacyclic triterpenoid quinone-methide; the NR-V04 warhead. Its C-28 CARBOXYLIC "
                            "ACID is the PROTAC tethering vector (Wang 2024 docking). Reactive/reversible-covalent "
                            "(Michael-acceptor quinone methide) -> must NOT be pushed through an ordinary "
                            "noncovalent workflow (brief 21.1). Notably NOT a clean Nurr1 LBD binder in the "
                            "Munoz-Tello NMR panel -> its NR4A engagement is not simple orthosteric binding."),
        "assay": "NR4A1 functional; NR-V04 tethering-vector docking (Wang 2024)",
        "potency": "n/a (reactive)",
        "selectivity_notes": "reactive electrophile; anti-target/liability flags expected (PAINS/BRENK)",
        "source": {"pmid_wang": "38334978", "ref_wang": "Wang et al. J Exp Med 2024;221(3):e20231519 (NR-V04)", "pmc_wang": "PMC10857906",
                    "doi_wang": "10.1084/jem.20231519", "pmid_munoztello": "33289551"},
        "resolve": ["celastrol", "chembl:CHEMBL189512"],
    },
    {
        "id": "vh032_vhl_ligand",
        "display_name": "VH032 (VHL ligand)",
        "role": "e3_ligand_vhl",
        "targets": ["VHL"],
        "evidence_class": "e3_ligand",
        "evidence_notes": ("Hydroxyproline-based VHL recruiter (the VHL-ligand class NR-V04 uses). The trans-"
                            "hydroxyproline stereochemistry is REQUIRED; the epimer is the standard inactive-"
                            "recruiter control (brief 25.2 / 21). Reference E3 handle for the VHL degrader arm."),
        "assay": "VHL binding (reference E3 ligand)",
        "potency": "sub-micromolar (VHL)",
        "selectivity_notes": "E3 handle; epimer = inactive-recruiter control",
        "source": {"ref": "VH032 / VHL-ligand class (Crews/Ciulli); NR-V04 VHL arm (Wang 2024)"},
        "resolve": ["VH032", "VH-032"],
    },
    {
        "id": "nrv04",
        "display_name": "NR-V04 (celastrol-VHL NR4A1 PROTAC)",
        "role": "reference_degrader",
        "targets": ["NR4A1"],
        "evidence_class": "reference_degrader",
        "evidence_notes": ("First NR4A1-selective PROTAC: celastrol warhead + linker + VHL recruiter. Degrades "
                            "NR4A1 while SPARING NR4A2 and NR4A3 in the reported systems; proteasome- and VHL-"
                            "dependent (Wang 2024). Establishes that PARALOGUE-SELECTIVE NR4A degradation is "
                            "experimentally real -> the ternary-modeling benchmark (brief Phase 15) and the "
                            "reason to prioritize VHL alongside CRBN. Sparing mechanism is unresolved."),
        "assay": "cellular NR4A1 degradation (DC50/Dmax); VHL/proteasome dependence; in-vivo tumor",
        "potency": "degrades NR4A1 within hours",
        "selectivity_notes": "NR4A1-selective (spares NR4A2/NR4A3) -> the family-selectivity benchmark",
        "source": {"pmid": "38334978", "pmc": "PMC10857906", "doi": "10.1084/jem.20231519",
                    "ref": "Wang et al. PROTAC-mediated NR4A1 degradation... J Exp Med 2024;221(3):e20231519",
                    "vendor": "MedChemExpress NR-V04 (structure/formula reference)"},
        "structure_status": "protac_composite",
        "resolve": [],   # NAME-COLLISION GUARD: ChEMBL's "NR-V04" (CHEMBL4779766) is a CRBN/glutarimide-PEG
                          # PROTAC, which CONTRADICTS Wang 2024's VHL-recruiting celastrol NR-V04 (brief 3.3).
                          # So the auto-resolved "NR-V04" record is NOT this compound -> do not resolve by name;
                          # keep as a verified composite of celastrol (warhead, resolved high) + VH032 (VHL,
                          # resolved) + linker. Never assert the collided structure.
        "note": ("Recorded as a composite of celastrol(warhead)+linker+VHL(recruiter). The full assembled "
                 "PROTAC SMILES is not asserted: name-resolving 'NR-V04' returns a CRBN/glutarimide PROTAC "
                 "(ChEMBL CHEMBL4779766) that conflicts with the published VHL/celastrol composition, so it is "
                 "rejected rather than trusted (brief golden rule: verify or leave unresolved). Component "
                 "structures (celastrol, VH032) ARE resolved in their own rows."),
    },

    # ---- 5. CRBN E3 handle (independent architecture; used in the ternary control) -----------------
    {
        "id": "lenalidomide",
        "display_name": "Lenalidomide (CRBN ligand)",
        "role": "e3_ligand_crbn",
        "targets": ["CRBN"],
        "evidence_class": "e3_ligand",
        "evidence_notes": ("Glutarimide IMiD; CRBN recruiter used as the in-distribution ternary positive control "
                            "(seats in the CRBN tri-Trp pocket; reproduced by Boltz-2 in this program's §2.4). The "
                            "independent (CRBN) degrader architecture vs the VHL arm."),
        "assay": "CRBN binding (tri-Trp pocket)",
        "potency": "micromolar (CRBN)",
        "selectivity_notes": "E3 handle (CRBN arm)",
        "source": {"ref": "CRBN/IMiD class; this program's ternary control (paper §2.4)"},
        "resolve": ["lenalidomide", "chembl:CHEMBL848"],
    },
]


# ---------------------------------------------------------------------------------------------------
# Pure structure-agreement logic (import-safe; unit-tested) -----------------------------------------
# ---------------------------------------------------------------------------------------------------
def skeleton(inchikey):
    """The connectivity skeleton of an InChIKey = the first block (14 chars before the first '-').
    Two structures share a skeleton iff they are the same 2D connectivity (ignoring stereo/protonation).
    Returns None for a falsy/short key."""
    if not inchikey or not isinstance(inchikey, str):
        return None
    head = inchikey.split("-")[0]
    return head if len(head) >= 10 else None


def _group_mw(group):
    """Median MW of a resolver-hit group (hits may carry a numeric 'mw'); None if none present."""
    mws = sorted(h["mw"] for h in group if h.get("mw") is not None)
    if not mws:
        return None
    n = len(mws)
    return mws[n // 2] if n % 2 else 0.5 * (mws[n // 2 - 1] + mws[n // 2])


def reconcile_structures(resolved, expected_mw=None, mw_tol=8.0):
    """resolved: list of dicts {source, smiles, inchikey[, mw]}. Decide a structure_confidence + consensus.
    Returns {structure_confidence, n_sources, agree, consensus_smiles, consensus_inchikey, per_source}.
      - 'high'      : >=2 sources resolved AND >=2 share an InChIKey skeleton (independent agreement)
      - 'medium'    : exactly 1 source resolved, OR >=2 resolved but skeletons DISAGREE (flagged)
      - 'unresolved': 0 sources resolved
    Consensus = the SMILES from the largest agreeing skeleton group. If `expected_mw` is given, it is used
    as a DISAMBIGUATOR: a skeleton group whose median MW is within `mw_tol` of expected_mw is preferred
    over a larger group that is NOT (this rejects a name that resolved to a derivative/salt of the wrong
    mass, e.g. an indole-2-carboxylic-acid record standing in for the parent indole). Confidence still
    reflects independent agreement, not the MW hint."""
    got = [r for r in resolved if r.get("smiles") and r.get("inchikey")]
    n = len(got)
    if n == 0:
        return {"structure_confidence": "unresolved", "n_sources": 0, "agree": False,
                "consensus_smiles": None, "consensus_inchikey": None, "per_source": resolved}
    groups = {}
    for r in got:
        k = skeleton(r["inchikey"])
        groups.setdefault(k, []).append(r)

    def group_rank(item):
        k, grp = item
        mw = _group_mw(grp)
        mw_ok = (expected_mw is not None and mw is not None and abs(mw - expected_mw) <= mw_tol)
        # prefer: MW-consistent group first (when an expectation is given), then larger group
        return (1 if mw_ok else 0, len(grp))

    best_k, best = max(groups.items(), key=group_rank)
    # `agree` = the CHOSEN group has independent (>=2 source) support
    agree = len(best) >= 2
    mw_selected = (expected_mw is not None and _group_mw(best) is not None
                   and abs(_group_mw(best) - expected_mw) <= mw_tol)
    if agree:
        conf = "high"
    else:
        conf = "medium"  # 1 source, or multiple that disagree -> flag, don't trust blindly
    return {"structure_confidence": conf, "n_sources": n, "agree": agree,
            "skeleton_disagreement": (len(groups) > 1),
            "mw_disambiguated": bool(mw_selected and len(groups) > 1),
            "consensus_smiles": best[0]["smiles"], "consensus_inchikey": best[0]["inchikey"],
            "per_source": resolved}


# ---------------------------------------------------------------------------------------------------
# Resolvers (runner-only; need internet) ------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
def _get(url, timeout=60, accept="application/json"):
    import time
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0", "Accept": accept})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            print("  retry %d %s: %s" % (i + 1, url[:90], e), file=sys.stderr)
            time.sleep(2 ** i)
    return None


def _inchikey_from_smiles(smiles, Chem):
    try:
        m = Chem.MolFromSmiles(smiles)
        return Chem.MolToInchiKey(m) if m is not None else None
    except Exception:  # noqa
        return None


def resolve_chembl(term, Chem):
    """ChEMBL: accept 'chembl:CHEMBLxxxx' (exact) or a name (search)."""
    try:
        if term.lower().startswith("chembl:"):
            cid = term.split(":", 1)[1]
            raw = _get("%s/molecule/%s?format=json" % (CHEMBL, cid))
            if not raw:
                return None
            d = json.loads(raw)
            smi = (d.get("molecule_structures") or {}).get("canonical_smiles")
            src_id = d.get("molecule_chembl_id")
        else:
            raw = _get("%s/molecule/search?q=%s&format=json&limit=1" % (CHEMBL, urllib.parse.quote(term)))
            if not raw:
                return None
            mols = json.loads(raw).get("molecules", [])
            if not mols:
                return None
            smi = (mols[0].get("molecule_structures") or {}).get("canonical_smiles")
            src_id = mols[0].get("molecule_chembl_id")
        if not smi:
            return None
        return {"source": "chembl", "source_id": src_id, "smiles": smi,
                "inchikey": _inchikey_from_smiles(smi, Chem)}
    except Exception as e:  # noqa
        print("  chembl '%s': %s" % (term, e), file=sys.stderr)
        return None


def resolve_pubchem(term, Chem):
    """PubChem PUG-REST: 'pubchem:CID' (exact) or a name."""
    try:
        if term.lower().startswith("pubchem:"):
            cid = term.split(":", 1)[1]
            path = "compound/cid/%s" % cid
        elif term.lower().startswith("chembl:"):
            return None
        else:
            path = "compound/name/%s" % urllib.parse.quote(term)
        raw = _get("%s/%s/property/IsomericSMILES,InChIKey/JSON" % (PUBCHEM, path))
        if not raw:
            return None
        props = json.loads(raw).get("PropertyTable", {}).get("Properties", [])
        if not props:
            return None
        p = props[0]
        smi = p.get("IsomericSMILES") or p.get("CanonicalSMILES")
        if not smi:
            return None
        return {"source": "pubchem", "source_id": "CID%s" % p.get("CID"), "smiles": smi,
                "inchikey": p.get("InChIKey") or _inchikey_from_smiles(smi, Chem)}
    except Exception as e:  # noqa
        print("  pubchem '%s': %s" % (term, e), file=sys.stderr)
        return None


def resolve_cactus(term, Chem):
    """NCI CACTUS name->SMILES (third independent resolver). Skip explicit-id terms."""
    try:
        if ":" in term:
            return None
        raw = _get("%s/%s/smiles" % (CACTUS, urllib.parse.quote(term)), accept="text/plain")
        if not raw:
            return None
        smi = raw.decode("utf-8", "ignore").strip().split("\n")[0].strip()
        if not smi or " " in smi or len(smi) < 3:
            return None
        return {"source": "cactus", "source_id": None, "smiles": smi,
                "inchikey": _inchikey_from_smiles(smi, Chem)}
    except Exception as e:  # noqa
        print("  cactus '%s': %s" % (term, e), file=sys.stderr)
        return None


def resolve_all(resolve_terms, Chem):
    """Try each term against all three resolvers; collect every distinct hit for cross-checking.
    Attaches an RDKit MW to each hit (used by reconcile's expected_mw disambiguator)."""
    from rdkit.Chem import Descriptors as _Desc
    hits = []
    for term in resolve_terms:
        for fn in (resolve_chembl, resolve_pubchem, resolve_cactus):
            r = fn(term, Chem)
            if r and r.get("smiles"):
                r["query"] = term
                try:
                    _m = Chem.MolFromSmiles(r["smiles"])
                    r["mw"] = round(_Desc.MolWt(_m), 2) if _m is not None else None
                except Exception:  # noqa
                    r["mw"] = None
                hits.append(r)
    # de-dup by (source, skeleton) keeping first
    seen = set()
    uniq = []
    for h in hits:
        key = (h["source"], skeleton(h.get("inchikey")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(h)
    return uniq


# ---------------------------------------------------------------------------------------------------
def main():
    # RDKit imported lazily (runs on the CI runner; the pure logic above imports without it).
    from rdkit import Chem
    from rdkit.Chem import Descriptors as Desc, Crippen, Lipinski as Lip, QED, rdMolDescriptors as rdMD
    from rdkit.Chem import RDConfig
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    # reuse the exact profiling used for the warhead-screen hits
    import warhead_chem_profile as wcp
    rdkit_tools = (Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer)

    records = []
    for entry in REGISTRY:
        rec = {k: entry[k] for k in entry if k != "resolve" and k != "smiles_hint"}
        resolved = resolve_all(entry.get("resolve", []), Chem)
        recon = reconcile_structures(resolved, expected_mw=entry.get("expected_mw"))
        rec["structure"] = {
            "structure_confidence": recon["structure_confidence"],
            "n_resolvers_agreeing": recon["n_sources"],
            "independent_agreement": recon["agree"],
            "skeleton_disagreement": recon.get("skeleton_disagreement", False),
            "mw_disambiguated": recon.get("mw_disambiguated", False),
            "expected_mw": entry.get("expected_mw"),
            "smiles": recon["consensus_smiles"],
            "inchikey": recon["consensus_inchikey"],
            "per_resolver": [{"source": r["source"], "source_id": r.get("source_id"),
                               "query": r.get("query"), "smiles": r["smiles"],
                               "mw": r.get("mw"), "inchikey": r.get("inchikey")}
                              for r in recon["per_source"]],
        }
        if recon["consensus_smiles"]:
            rec["cheminformatics"] = wcp.profile(recon["consensus_smiles"], rdkit_tools)
        else:
            rec["cheminformatics"] = None
        records.append(rec)

    # summary census
    by_conf = {}
    by_class = {}
    for r in records:
        c = r["structure"]["structure_confidence"]
        by_conf[c] = by_conf.get(c, 0) + 1
        ec = r.get("evidence_class", "?")
        by_class[ec] = by_class.get(ec, 0) + 1

    out = {
        "_schema": "published_warhead_registry",
        "version": REGISTRY_VERSION,
        "purpose": ("Versioned catalog of the PUBLISHED, experimentally anchored NR4A chemistry the "
                    "NR4A3-degrader program benchmarks against (brief Phase 1 / Workstream B, deliverables "
                    "30-33). Structures resolved + cross-checked from ChEMBL/PubChem/CACTUS; evidence "
                    "class + source per compound; unresolved (paywalled/novel) matter recorded honestly."),
        "resolvers": ["ChEMBL", "PubChem PUG-REST", "NCI CACTUS"],
        "structure_confidence_rule": ("high = >=2 resolvers agree on InChIKey skeleton; medium = 1 "
                                       "resolver, or multiple that disagree; unresolved = none resolved"),
        "evidence_classes": sorted(by_class.keys()),
        "summary": {"n_compounds": len(records), "by_structure_confidence": by_conf,
                     "by_evidence_class": by_class},
        "compounds": records,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote %s (%d compounds; confidence %s)" % (OUT, len(records), by_conf))
    for r in records:
        s = r["structure"]
        chem = r.get("cheminformatics") or {}
        print("  %-26s %-28s conf=%-10s MW=%s QED=%s handles=%s" % (
            r["id"], r.get("evidence_class", "")[:28], s["structure_confidence"],
            chem.get("MW", "-"), chem.get("QED", "-"),
            (chem.get("protac_handles") or {}).get("total", "-")))


if __name__ == "__main__":
    main()
