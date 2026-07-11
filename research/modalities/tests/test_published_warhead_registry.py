"""Tests for published_warhead_registry — the pure structure-agreement logic (no RDKit / no internet).

Covers skeleton() and reconcile_structures(): the InChIKey-skeleton cross-check that decides
`structure_confidence` (high/medium/unresolved) from the ChEMBL/PubChem/CACTUS resolver hits, and the
integrity of the curated REGISTRY table itself.
"""
import published_warhead_registry as pwr


# ---- skeleton() -----------------------------------------------------------------------------------
def test_skeleton_first_block():
    # aspirin InChIKey -> first 14-char connectivity block
    assert pwr.skeleton("BSYNRYMUTXBXSQ-UHFFFAOYSA-N") == "BSYNRYMUTXBXSQ"


def test_skeleton_ignores_stereo_protonation_blocks():
    # same connectivity, different stereo/charge suffix -> same skeleton
    assert pwr.skeleton("AAAAAAAAAAAAAA-BBBBBBBBBB-N") == pwr.skeleton("AAAAAAAAAAAAAA-CCCCCCCCCC-M")


def test_skeleton_none_on_garbage():
    assert pwr.skeleton("") is None
    assert pwr.skeleton(None) is None
    assert pwr.skeleton("SHORT") is None
    assert pwr.skeleton(12345) is None


# ---- reconcile_structures() -----------------------------------------------------------------------
def _hit(source, key, smiles="C", mw=None):
    return {"source": source, "smiles": smiles, "inchikey": key, "mw": mw}


def test_reconcile_high_when_two_agree():
    k = "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
    r = pwr.reconcile_structures([_hit("chembl", k, "CC(=O)Oc1ccccc1C(=O)O"),
                                  _hit("pubchem", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N", "OC(=O)c1ccccc1OC(C)=O")])
    assert r["structure_confidence"] == "high"
    assert r["n_sources"] == 2 and r["agree"] is True
    assert r["consensus_smiles"] is not None
    assert r["consensus_inchikey"].startswith("BSYNRYMUTXBXSQ")


def test_reconcile_medium_single_source():
    r = pwr.reconcile_structures([_hit("cactus", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N")])
    assert r["structure_confidence"] == "medium"
    assert r["n_sources"] == 1 and r["agree"] is False
    assert r["consensus_inchikey"].startswith("BSYNRYMUTXBXSQ")


def test_reconcile_medium_when_sources_disagree():
    # two resolvers, DIFFERENT skeletons -> not trusted as high; flagged
    r = pwr.reconcile_structures([_hit("chembl", "AAAAAAAAAAAAAA-X-N", "C"),
                                  _hit("pubchem", "ZZZZZZZZZZZZZZ-Y-N", "N")])
    assert r["structure_confidence"] == "medium"
    assert r["skeleton_disagreement"] is True
    assert r["agree"] is False


def test_reconcile_majority_group_wins_consensus():
    # 2 agree vs 1 outlier -> consensus is the majority skeleton, confidence high
    good = "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
    r = pwr.reconcile_structures([_hit("chembl", good, "good1"),
                                  _hit("pubchem", good, "good2"),
                                  _hit("cactus", "OUTLIEROUTLIE-Q-N", "bad")])
    assert r["structure_confidence"] == "high"
    assert r["consensus_smiles"] in ("good1", "good2")


def test_reconcile_expected_mw_rejects_wrong_mass_group():
    # The DHI failure mode: a name resolves to a derivative (wrong mass) in one source and the correct
    # parent in another. expected_mw must pick the PARENT even though both groups are size 1.
    parent = _hit("cactus", "SGNZYJXNUURYCH-UHFFFAOYSA-N", "Oc1cc2[nH]ccc2cc1O", mw=149.15)
    deriv = _hit("chembl", "UEDKWJDOUGYJQX-UHFFFAOYSA-N", "CCn1c(C(=O)O)cc2cc(O)c(O)cc21", mw=221.2)
    r = pwr.reconcile_structures([deriv, parent], expected_mw=149.15)
    assert r["consensus_inchikey"].startswith("SGNZYJXNUURYCH")   # the parent, not the derivative
    assert r["mw_disambiguated"] is True
    assert r["skeleton_disagreement"] is True


def test_reconcile_expected_mw_prefers_mass_match_over_larger_group():
    # two sources agree on a WRONG mass, one source has the right mass -> expected_mw wins over count
    wrong = "WRONGWRONGWRO-X-N"
    r = pwr.reconcile_structures(
        [_hit("chembl", wrong, "bad1", mw=500.0), _hit("pubchem", wrong, "bad2", mw=500.0),
         _hit("cactus", "RIGHTRIGHTRI-Y-N", "good", mw=150.0)], expected_mw=150.0)
    assert r["consensus_smiles"] == "good"
    assert r["mw_disambiguated"] is True


def test_reconcile_unresolved_when_empty():
    r = pwr.reconcile_structures([])
    assert r["structure_confidence"] == "unresolved"
    assert r["n_sources"] == 0
    assert r["consensus_smiles"] is None


def test_reconcile_skips_hits_missing_structure():
    # a resolver dict with no smiles/inchikey doesn't count toward agreement
    r = pwr.reconcile_structures([_hit("chembl", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"),
                                  {"source": "pubchem", "smiles": None, "inchikey": None}])
    assert r["n_sources"] == 1
    assert r["structure_confidence"] == "medium"


# ---- REGISTRY table integrity ---------------------------------------------------------------------
def test_registry_entries_wellformed():
    ids = set()
    required = {"id", "display_name", "role", "targets", "evidence_class", "source"}
    for e in pwr.REGISTRY:
        assert required <= set(e), "missing keys in %s" % e.get("id")
        assert e["id"] not in ids, "duplicate id %s" % e["id"]
        ids.add(e["id"])
        assert isinstance(e["targets"], list) and e["targets"]
        assert isinstance(e["source"], dict) and e["source"]


def test_registry_has_all_five_workstream_b_arms():
    roles = {e["role"] for e in pwr.REGISTRY}
    # NR4A3 warhead source, NR4A1 + NR4A2 anti-target panels, NR-V04 reference degrader, E3 handles
    assert "warhead_source" in roles                                  # Zaienne NOR-1
    assert any("nr4a1" in r for r in roles)                           # NR4A1 panel
    assert any("nr4a2" in r for r in roles)                           # NR4A2 panel
    assert "reference_degrader" in roles                              # NR-V04
    assert {"e3_ligand_vhl", "e3_ligand_crbn"} <= roles              # both E3 architectures


def test_nrv04_and_covalent_flagged_special():
    # NR-V04's warhead (celastrol) + the NR4A2 cocrystal ligands must be flagged covalent/reactive,
    # not ordinary noncovalent (brief 21.1 / golden handling).
    by_id = {e["id"]: e for e in pwr.REGISTRY}
    assert "reactive" in by_id["celastrol"]["evidence_class"] or "covalent" in by_id["celastrol"]["evidence_class"]
    assert by_id["dhi"]["evidence_class"] == "covalent_crystal"
    assert by_id["pga1"]["evidence_class"] == "covalent_crystal"


def test_zaienne_series_row_is_context_only():
    # the series row itself stays a context record (no name resolution, no fabricated SMILES)...
    z = next(e for e in pwr.REGISTRY if e["id"] == "zaienne_nor1_series")
    assert z.get("resolve") == []
    assert "smiles" not in z
    assert z["source"]["pmc"] == "PMC9542104"


def test_zaienne_lead_compound19_resolved_from_oa_text():
    # ...but the elaborated lead (compound 19, methyl 5-bromoindole-3-carboxylate) is now a resolvable
    # entry with an expected_mw disambiguator (transcribed from the OA full text, not invented).
    c19 = next(e for e in pwr.REGISTRY if e["id"] == "zaienne_cmpd19")
    assert c19["targets"] == ["NR4A3"]
    assert c19["expected_mw"] == 254.08
    assert any("5-bromo" in r for r in c19["resolve"])
    assert c19["source"]["pmc"] == "PMC9542104"
