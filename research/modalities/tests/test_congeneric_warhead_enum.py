"""Tests for congeneric_warhead_enum.

Two layers:
  * PURE structural-integrity of the curated ENUM table (import-safe, no RDKit) -- check_enum_table.
  * RDKit-backed build (SMILES parse/sanitize, canonicalization, InChIKey, drop-counting) -- skipped
    automatically if RDKit is not importable in the environment.
"""
import pytest

import congeneric_warhead_enum as cwe

try:
    from rdkit import Chem  # noqa
    HAVE_RDKIT = True
except Exception:  # noqa
    HAVE_RDKIT = False

rdkit_only = pytest.mark.skipif(not HAVE_RDKIT, reason="RDKit not available")


# ---- pure ENUM-table integrity (no RDKit) ---------------------------------------------------------
def test_enum_table_is_clean():
    assert cwe.check_enum_table(cwe.ENUM) == []


def test_enum_size_is_focused():
    # brief asks for a FOCUSED set, ~15-25 compounds
    assert 15 <= len(cwe.ENUM) <= 25


def test_all_four_classes_present():
    classes = {e["cls"] for e in cwe.ENUM}
    assert classes == set(cwe.VALID_CLASSES)


def test_required_fields_and_ids_unique():
    ids = [e["id"] for e in cwe.ENUM]
    assert len(ids) == len(set(ids))
    for e in cwe.ENUM:
        for f in cwe.REQUIRED_FIELDS:
            assert f in e, "%s missing %s" % (e.get("id"), f)


def test_comparator_flag_matches_class():
    for e in cwe.ENUM:
        assert (e["cls"] == "comparator") == e["is_comparator"]


def test_comparator_parent_is_denovo401_others_anchor():
    for e in cwe.ENUM:
        if e["cls"] == "comparator":
            assert e["parent"] == cwe.DENOVO401_ID
        else:
            assert e["parent"] == cwe.ANCHOR_ID


def test_at_least_two_comparators():
    assert sum(1 for e in cwe.ENUM if e["is_comparator"]) >= 2


# ---- check_enum_table catches injected defects ----------------------------------------------------
def test_check_catches_duplicate_id():
    bad = list(cwe.ENUM) + [dict(cwe.ENUM[0])]
    probs = cwe.check_enum_table(bad)
    assert any("duplicate id" in p for p in probs)


def test_check_catches_bad_class():
    e = dict(cwe.ENUM[0]); e["id"] = "x"; e["cls"] = "not_a_class"
    probs = cwe.check_enum_table([e])
    assert any("invalid class" in p for p in probs)


def test_check_catches_comparator_mismatch():
    e = dict(cwe.ENUM[0]); e["id"] = "x"; e["cls"] = "exit_vector_sub"; e["is_comparator"] = True
    probs = cwe.check_enum_table([e])
    assert any("is_comparator mismatch" in p for p in probs)


def test_check_catches_nonbool_microstate():
    e = dict(cwe.ENUM[0]); e["id"] = "x"; e["microstate_ambiguous"] = "yes"
    probs = cwe.check_enum_table([e])
    assert any("microstate_ambiguous must be bool" in p for p in probs)


# ---- RDKit-backed build (skips if RDKit absent) ---------------------------------------------------
@rdkit_only
def test_anchor_smiles_parses_and_is_bromoindole_ester():
    m = Chem.MolFromSmiles(cwe.ANCHOR_SMILES)
    assert m is not None
    from rdkit.Chem import rdMolDescriptors as rdMD, Descriptors
    assert rdMD.CalcMolFormula(m) == "C10H8BrNO2"
    assert abs(Descriptors.MolWt(m) - 254.08) < 0.1
    # InChIKey skeleton is stable for methyl 5-bromo-1H-indole-3-carboxylate
    assert Chem.MolToInchiKey(m).startswith("MFOKOKHNSVUKON")


@rdkit_only
def test_denovo401_smiles_parses():
    assert Chem.MolFromSmiles(cwe.DENOVO401_SMILES) is not None


@rdkit_only
def test_every_enum_smiles_parses_no_drops():
    records, drops = cwe.build_records(Chem)
    assert drops == [], "unexpected drops: %s" % drops
    assert len(records) == len(cwe.ENUM)


@rdkit_only
def test_build_populates_canonical_smiles_and_inchikey():
    records, _ = cwe.build_records(Chem)
    for r in records:
        assert r["smiles"] and Chem.MolFromSmiles(r["smiles"]) is not None
        # InChI backend is available in standard RDKit -> keys should be populated + well-formed
        assert r["inchikey"] and len(r["inchikey"].split("-")[0]) == 14


@rdkit_only
def test_indole_nh_preserved_in_warhead_compounds():
    # SAR: the indole N-H must survive in every anchor-derived warhead. The denovo_401 comparators are
    # not indoles, so they are exempt (is_comparator=True).
    nh_indole = Chem.MolFromSmarts("[nH]")
    records, _ = cwe.build_records(Chem)
    for r in records:
        if r["is_comparator"]:
            continue
        m = Chem.MolFromSmiles(r["smiles"])
        assert m.HasSubstructMatch(nh_indole), "%s lost the indole NH" % r["id"]


@rdkit_only
def test_build_drops_and_counts_invalid_smiles(monkeypatch):
    # inject a deliberately invalid entry and confirm it is dropped + counted, not emitted
    bad = dict(cwe.ENUM[0]); bad["id"] = "cw_bad"; bad["smiles"] = "C1CC"  # unclosed ring -> won't parse
    monkeypatch.setattr(cwe, "ENUM", list(cwe.ENUM) + [bad])
    records, drops = cwe.build_records(Chem)
    assert any(d["id"] == "cw_bad" for d in drops)
    assert all(r["id"] != "cw_bad" for r in records)


@rdkit_only
def test_summary_counts_consistent():
    records, drops = cwe.build_records(Chem)
    s = cwe.summarize(records)
    assert s["n_compounds"] == len(records)
    assert sum(s["by_class"].values()) == len(records)
    assert s["n_comparator"] == sum(1 for r in records if r["is_comparator"])
