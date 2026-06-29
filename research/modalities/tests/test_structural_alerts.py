"""Tests for structural_alerts — the developability gate for de-novo warheads.

The pure decision (`developable_verdict`) is tested without RDKit (TESTING.md #3). The SMARTS catalog +
RDKit matcher are smoke-tested only if RDKit is importable (skipped otherwise, so CI without RDKit still
passes the pure logic).
"""
import pytest
import structural_alerts as sa


# ---- pure verdict (no RDKit) ----

def test_clean_molecule_is_developable():
    v = sa.developable_verdict([], aromatic_rings=2, sascore=3.0)
    assert v["developable"] is True
    assert v["reasons"] == []


def test_any_liability_fails():
    v = sa.developable_verdict(["peroxide"], aromatic_rings=2, sascore=3.0)
    assert v["developable"] is False
    assert "alert:peroxide" in v["reasons"]


def test_no_aromatic_ring_fails():
    v = sa.developable_verdict([], aromatic_rings=0, sascore=3.0)
    assert v["developable"] is False
    assert "no_aromatic_ring" in v["reasons"]
    # None aromatic_rings is treated as 0
    assert sa.developable_verdict([], aromatic_rings=None, sascore=3.0)["developable"] is False


def test_high_sascore_fails():
    assert sa.developable_verdict([], 2, sascore=5.08)["developable"] is False        # denovo_15's SA
    assert sa.developable_verdict([], 2, sascore=4.5)["developable"] is True           # at the cut
    assert sa.developable_verdict([], 2, sascore=None)["developable"] is False         # unprofiled SA -> fail


def test_reasons_accumulate():
    v = sa.developable_verdict(["carbamic_acid", "cyclopentadiene"], aromatic_rings=0, sascore=6.0)
    assert v["developable"] is False
    assert len(v["reasons"]) == 4         # 2 alerts + no_aromatic_ring + SAscore


def test_brenk_alerts_fail():
    # BRENK>0 fails the gate (the "BRENK + curated" medchem-realism gate); default 0 has no effect
    assert sa.developable_verdict([], 2, 3.0, brenk_alerts=1)["developable"] is False
    assert "BRENK:1" in sa.developable_verdict([], 2, 3.0, brenk_alerts=1)["reasons"]
    assert sa.developable_verdict([], 2, 3.0)["developable"] is True            # default brenk=0 passes


# ---- SMARTS catalog (needs RDKit) ----

def _has_rdkit():
    try:
        import rdkit  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _has_rdkit(), reason="RDKit not installed")
def test_catalog_flags_artifacts_and_passes_clean():
    # the two artifact leads + denovo_57 (clean) + a few marketed drugs (must be clean = no false positives)
    assert "carbamic_acid" in sa.liabilities_from_smiles(
        "C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C")          # denovo_15
    assert "peroxide" in sa.liabilities_from_smiles(
        "CO[C@H]1S[C@H](N[C@H]2CCOO[C@@]2(C)CO)c2nc(-c3ccccc3F)ccc21")          # denovo_94
    assert sa.liabilities_from_smiles("NC[C@@H]1CCN(Cc2ccccc2)C1") == []        # denovo_57 clean
    for drug in ("CC(=O)Oc1ccccc1C(=O)O",                                       # aspirin
                 "CC(C)Cc1ccc(C(C)C(=O)O)cc1",                                  # ibuprofen
                 "Cn1cnc2c1c(=O)n(C)c(=O)n2C",                                  # caffeine
                 "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1"):  # imatinib
        assert sa.liabilities_from_smiles(drug) == []


@pytest.mark.skipif(not _has_rdkit(), reason="RDKit not installed")
def test_catalog_flags_michael_and_NO_bond():
    assert "michael_acceptor" in sa.liabilities_from_smiles("C=CC(C)=O")        # methyl vinyl ketone
    assert "NO_single_bond" in sa.liabilities_from_smiles("CN(O)C")             # hydroxylamine
    assert sa.liabilities_from_smiles("c1cc(C)on1") == []                       # aromatic isoxazole N-O is fine


@pytest.mark.skipif(not _has_rdkit(), reason="RDKit not installed")
def test_unparseable_smiles():
    assert sa.liabilities_from_smiles("not_a_smiles%%%") == ["unparseable"]
