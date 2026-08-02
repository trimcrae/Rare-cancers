"""Unit tests for `apo_pose_recovery` — the known-answer pose-recovery benchmark.

★★ THE MOST IMPORTANT TEST IN THIS FILE IS `test_thresholds_are_frozen`. The whole value of a
known-answer test is that its criterion was fixed before the answer was seen; a suite that does not pin the
numbers lets a future edit quietly move the goalposts and still show green. If a threshold genuinely has to
change, this test is what forces the change to be deliberate and to carry the superseded value.

Everything here is offline: no network, no smina, no fpocket.
"""
import math
import os

import pytest

import apo_pose_recovery as A


# ============================================================ the pre-registration itself

def test_thresholds_are_frozen():
    """⛔ DO NOT EDIT TO MAKE A RUN PASS. Changing any of these changes what the benchmark means, and the
    old value belongs in an appendix (CLAUDE.md §1.2), not in a diff nobody reads."""
    assert A.RECOVER_RMSD_A == 2.00      # field-standard redocking-success boundary
    assert A.PARTIAL_RMSD_A == 4.00      # field-standard "wrong pose" boundary
    assert A.FNAT_SUCCESS == 0.50
    assert A.NULL_POWER_MAX == 0.05
    assert A.N_NULL == 200


def test_the_criterion_and_both_outcomes_are_written_in_the_docstring():
    doc = A.__doc__
    assert "PRE-REGISTERED CRITERION" in doc
    assert "BOTH OUTCOMES, WRITTEN DOWN NOW" in doc
    for phrase in ("RECOVERED", "NOT RECOVERED", "INCONCLUSIVE"):
        assert phrase in doc


def test_selection_rules_are_declared_before_any_query():
    assert len(A.SELECTION_RULES) >= 8
    assert any(r.startswith("R1 HARD") for r in A.SELECTION_RULES)
    # the accession list is fixed up front so the search cannot be steered to a convenient answer
    accs = [a for a, _n, _w in A.NR_ACCESSIONS]
    assert accs[0] == "P43354", "NR4A2/Nurr1 leads: NR4A3's own subfamily and the same 'no cavity' regime"
    assert len(accs) == len(set(accs))


def test_the_pipelines_own_docking_settings_are_read_not_retyped():
    """If someone changes the pipeline's exhaustiveness, the benchmark must change with it."""
    p = A.pipeline_dock_params()
    for k in ("size_x", "size_y", "size_z", "exhaustiveness", "num_modes"):
        assert k in p and p[k].isdigit(), "missing %s — the source parse broke" % k
    import inspect

    import nr4a3_warhead as wh
    src = inspect.getsource(wh.dock_into)
    for k, v in p.items():
        if k != "_read_from":
            assert '"%s"' % v in src


# ============================================================ apo / holo classification

def test_drug_like_rejects_crystallisation_matter():
    assert A.drug_like({"id": "GOL", "formula_weight": 92.1, "type": "NON-POLYMER"})[0] is False
    assert A.drug_like({"id": "SO4", "formula_weight": 96.1, "type": "NON-POLYMER"})[0] is False
    assert A.drug_like({"id": "ZN", "formula_weight": 65.4, "type": "NON-POLYMER"})[0] is False


def test_drug_like_rejects_by_size_and_class():
    assert A.drug_like({"id": "XXX", "formula_weight": 120.0, "type": "NON-POLYMER"})[0] is False
    assert A.drug_like({"id": "XXX", "formula_weight": 1500.0, "type": "NON-POLYMER"})[0] is False
    assert A.drug_like({"id": "NAG", "formula_weight": 221.2, "type": "D-SACCHARIDE"})[0] is False
    assert A.drug_like({"id": "BRL", "formula_weight": 357.4, "type": "NON-POLYMER"})[0] is True


def _entry(pdb, acc, comps, method="X-RAY DIFFRACTION", res=2.0, models=1, seq="ACDEFGHIK"):
    return {
        "rcsb_id": pdb, "struct": {"title": pdb + " title"}, "exptl": [{"method": method}],
        "rcsb_entry_info": {"resolution_combined": [res], "deposited_model_count": models},
        "polymer_entities": [{
            "entity_poly": {"pdbx_seq_one_letter_code_can": seq},
            "rcsb_polymer_entity_container_identifiers": {
                "auth_asym_ids": ["A"],
                "reference_sequence_identifiers": [{"database_accession": acc,
                                                    "database_name": "UniProt"}]}}],
        "nonpolymer_entities": [{
            "rcsb_nonpolymer_entity_container_identifiers": {"auth_asym_ids": ["A"]},
            "nonpolymer_comp": {"chem_comp": c,
                                "rcsb_chem_comp_descriptor": {"SMILES_stereo": c.get("smiles", "CCO")}}}
            for c in comps],
    }


def test_a_structure_carrying_only_additives_is_apo():
    e = A.classify_entry(_entry("1AAA", "P43354",
                                [{"id": "GOL", "formula_weight": 92.1, "type": "NON-POLYMER"},
                                 {"id": "SO4", "formula_weight": 96.1, "type": "NON-POLYMER"}]), "P43354")
    assert e["apo"] is True
    assert e["non_ligand_components"] == ["GOL", "SO4"]


def test_a_structure_with_a_drug_like_component_is_holo_and_its_smiles_is_carried():
    e = A.classify_entry(_entry("2BBB", "P43354",
                                [{"id": "ROS", "formula_weight": 357.4, "type": "NON-POLYMER",
                                  "smiles": "CC(=O)Nc1ccccc1"}]), "P43354")
    assert e["apo"] is False
    assert e["ligands"][0]["comp_id"] == "ROS"
    assert e["ligands"][0]["smiles"] == "CC(=O)Nc1ccccc1"


def test_pairing_prefers_the_nr4a_subfamily_then_an_nmr_apo():
    by_acc = {
        "P37231": {"name": "PPARG", "entries": [
            A.classify_entry(_entry("1XR", "P37231", []), "P37231"),
            A.classify_entry(_entry("2XR", "P37231",
                                    [{"id": "AAA", "formula_weight": 350.0, "type": "NON-POLYMER"}]),
                             "P37231")]},
        "P43354": {"name": "NR4A2", "entries": [
            A.classify_entry(_entry("1NR", "P43354", [], method="X-RAY DIFFRACTION"), "P43354"),
            A.classify_entry(_entry("1NMR", "P43354", [], method="SOLUTION NMR", res=None, models=20),
                             "P43354"),
            A.classify_entry(_entry("2NR", "P43354",
                                    [{"id": "BBB", "formula_weight": 300.0, "type": "NON-POLYMER"}]),
                             "P43354")]},
    }
    ranked = A.pair_candidates(by_acc)
    assert ranked, "an apo and a holo exist for both proteins"
    best = ranked[0][1]
    assert best["accession"] == "P43354", "R6: the NR4A subfamily outranks PPARG"
    assert best["apo"] == "1NMR", "R7: an NMR apo ensemble mirrors 8XTT and is preferred"


def test_no_pair_is_reported_as_a_finding_not_papered_over():
    sel = A.mode_select({"by_accession": {"P43354": {"name": "NR4A2", "entries": [
        A.classify_entry(_entry("1NR", "P43354", []), "P43354")]}}})   # apo only, no holo
    assert sel["chosen"] is None
    assert "no substitute benchmark is used" in sel["_finding_if_empty"].lower() or \
           "No substitute benchmark is used" in sel["_finding_if_empty"]


# ============================================================ structure handling

_HOLO = """\
ATOM      1  N   MET A   1      0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  MET A   1      1.000   0.000   0.000  1.00  0.00           C
ATOM      3  CA  LYS A   2      3.000   0.000   0.000  1.00  0.00           C
ATOM      4  CA  LEU B   1     50.000   0.000   0.000  1.00  0.00           C
HETATM    5  C1  LIG A 900      2.000   0.000   0.000  1.00  0.00           C
HETATM    6  O1  LIG A 900      2.000   1.000   0.000  1.00  0.00           O
HETATM    7  C1  LIG C 901     60.000   0.000   0.000  1.00  0.00           C
HETATM    8  O   HOH A 950      9.000   9.000   9.000  1.00  0.00           O
ENDMDL
ATOM      9  CA  ALA A   3      4.000   0.000   0.000  1.00  0.00           C
"""


def test_protein_only_keeps_one_chain_and_the_first_model():
    out = A.protein_only(_HOLO)
    lines = [l for l in out.splitlines() if l.startswith("ATOM")]
    assert len(lines) == 3 and all(l[21] == "A" for l in lines)
    assert "ALA" not in out, "records after ENDMDL belong to a different model"


def test_ligand_hetatms_takes_the_largest_copy():
    lines, key = A.ligand_hetatms(_HOLO, "LIG")
    assert key[0] == "A" and len(lines) == 2, "chain A's 2-atom copy beats chain C's 1-atom copy"
    assert A.ligand_hetatms(_HOLO, "NOPE") == (None, None)


def test_residues_near_is_heavy_atom_and_respects_the_cutoff():
    assert A.residues_near(A.protein_only(_HOLO), [(2.0, 0.0, 0.0)], 1.5) == {1, 2}
    assert A.residues_near(A.protein_only(_HOLO), [(2.0, 0.0, 0.0)], 0.5) == set()


def test_chain_nearest_picks_the_chain_the_ligand_actually_touches():
    assert A._chain_nearest(_HOLO, [(2.0, 0.0, 0.0)]) == "A"
    assert A._chain_nearest(_HOLO, [(50.0, 0.0, 0.0)]) == "B"


# ============================================================ chemical correspondence + power

def test_crystal_ligand_correspondence_is_graph_based_not_order_based():
    """★ The crystal copy is written in a SHUFFLED atom order; a correct graph match still recovers the
    exact coordinates. An order- or proximity-based match would not, and would then under-report the
    deviation of a flipped pose — the failure `selcal_cofold_decompose.py` documents."""
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    rdMolAlign = pytest.importorskip("rdkit.Chem.rdMolAlign")
    import random
    smi = "CC(=O)Nc1ccc(O)cc1"
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    assert AllChem.EmbedMolecule(m, randomSeed=7) == 0
    AllChem.MMFFOptimizeMolecule(m)
    m = Chem.RemoveHs(m)
    conf = m.GetConformer()
    order = list(range(m.GetNumAtoms()))
    random.Random(3).shuffle(order)
    lines = []
    for n, i in enumerate(order):
        p = conf.GetAtomPosition(i)
        el = m.GetAtomWithIdx(i).GetSymbol()
        lines.append("HETATM%5d %-4s LIG A 501    %8.3f%8.3f%8.3f  1.00 20.00          %2s\n"
                     % (n + 1, (el + str(n + 1))[:4], p.x, p.y, p.z, el.rjust(2)))
    got, why = A.crystal_mol(lines, smi)
    assert got is not None, why
    assert rdMolAlign.CalcRMS(got, m) < 0.01


def test_an_atom_count_mismatch_is_refused_not_guessed():
    got, why = A.crystal_mol(
        ["HETATM    1  C1  LIG A 501       0.000   0.000   0.000  1.00 20.00           C\n"],
        "CC(=O)Nc1ccc(O)cc1")
    assert got is None and "refusing to guess" in why


def test_the_random_in_box_null_gives_the_criterion_power():
    """C2. If a random placement cleared 2 A often, a pass would mean nothing — so the test asserts the
    control is capable of showing that, on a case where the answer is obvious."""
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    m = Chem.AddHs(Chem.MolFromSmiles("CC(=O)Nc1ccc(O)cc1"))
    AllChem.EmbedMolecule(m, randomSeed=7)
    m = Chem.RemoveHs(m)
    conf = m.GetConformer()
    c = A.centroid([(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
                    for i in range(m.GetNumAtoms())])
    null = A.random_in_box_null(m, c, (24.0, 24.0, 24.0), n=200)
    assert null["n"] == 200
    assert null["p_within_criterion"] <= A.NULL_POWER_MAX
    # and the same null in a TINY box must lose power — proving the control is measuring something
    tight = A.random_in_box_null(m, c, (0.2, 0.2, 0.2), n=200)
    assert tight["p_within_criterion"] > null["p_within_criterion"]


# ============================================================ the verdict decision table

def _res(primary, c1, p_null=0.0, oracle=None, band=None):
    return {"arms": {"PRIMARY_blind_apo_pipeline_box": {"rmsd_A": primary, "fnat": 0.7,
                                                        "verdict": band or (
                                                            "RECOVERED" if primary is not None
                                                            and primary <= A.RECOVER_RMSD_A else
                                                            "PARTIAL" if primary is not None
                                                            and primary <= A.PARTIAL_RMSD_A
                                                            else "NOT RECOVERED")},
                     "C1_self_dock_holo": {"rmsd_A": c1},
                     "C3_oracle_box_apo": {"rmsd_A": oracle}},
            "C2_random_in_box_null": {"p_within_criterion": p_null}}


def test_c1_failure_is_INCONCLUSIVE_not_a_pipeline_failure():
    v = A.verdict(_res(primary=8.0, c1=5.0))
    assert v["outcome"] == "INCONCLUSIVE" and "C1 FAILED" in v["reason"]


def test_a_powerless_criterion_is_INCONCLUSIVE():
    v = A.verdict(_res(primary=1.2, c1=0.8, p_null=0.4))
    assert v["outcome"] == "INCONCLUSIVE" and "C2 FAILED" in v["reason"]


def test_recovery_passes_only_inside_the_frozen_boundary():
    assert A.verdict(_res(primary=1.99, c1=0.8))["outcome"] == "RECOVERED"
    assert A.verdict(_res(primary=2.01, c1=0.8))["outcome"] == "NOT RECOVERED"


def test_a_failure_names_which_stage_failed():
    """A bare 'it failed' is not a diagnosis. Site transfer and pose placement have different remedies."""
    site = A.verdict(_res(primary=9.0, c1=0.8, oracle=1.1))
    assert site["outcome"] == "NOT RECOVERED" and "SITE TRANSFER" in site["failing_stage"]
    place = A.verdict(_res(primary=9.0, c1=0.8, oracle=8.5))
    assert "POSE PLACEMENT" in place["failing_stage"]


def test_the_failure_sentence_does_not_overclaim_about_nr4a3():
    v = A.verdict(_res(primary=9.0, c1=0.8, oracle=8.5))
    s = v["sentence"]
    assert "does not prove the NR4A3 denovo_401 pose wrong" in s
    assert "removes the presumption that it is right" in s


def test_the_oracle_arm_can_never_turn_a_failure_into_a_pass():
    v = A.verdict(_res(primary=9.0, c1=0.8, oracle=0.4))
    assert v["outcome"] == "NOT RECOVERED"


def test_panel_takes_one_pair_per_distinct_holo_and_caps_per_protein():
    """★ THE BUG THE FIRST RUN EXPOSED. Five apo structures against ONE crystal is one answer measured five
    times; the stated rule always said otherwise and the implementation did not."""
    sel = {"chosen": {"accession": "P43354", "apo": "1OVL", "holo": "5Y41", "ligand": {"comp_id": "RPG"}},
           "considered_top": [
               {"accession": "P43354", "apo": "6L6Q", "holo": "5Y41", "ligand": {"comp_id": "RPG"}},
               {"accession": "P43354", "apo": "6L6L", "holo": "5Y41", "ligand": {"comp_id": "RPG"}},
               {"accession": "P43354", "apo": "1OVL", "holo": "5YD6", "ligand": {"comp_id": "8SU"}},
               {"accession": "P43354", "apo": "1OVL", "holo": "8CYO", "ligand": {"comp_id": "OBJ"}},
               {"accession": "P22736", "apo": "4RZF", "holo": "4REF", "ligand": {"comp_id": "3N0"}},
               {"accession": "P22736", "apo": "3V3E", "holo": "4REF", "ligand": {"comp_id": "3N0"}},
               {"accession": "P22736", "apo": "4KZJ", "holo": "4RE7", "ligand": {"comp_id": "XXX"}},
               {"accession": "P22736", "apo": "4KZJ", "holo": "4RZG", "ligand": {"comp_id": "YYY"}}]}
    out = A._dedup_pairs([dict(sel["chosen"])] + sel["considered_top"])
    holos = [r["holo"] for r in out]
    assert len(holos) == len(set(holos)), "one pair per distinct crystallographic answer"
    for acc in {r["accession"] for r in out}:
        assert sum(1 for r in out if r["accession"] == acc) <= A.MAX_PER_PROTEIN


def test_engineered_constructs_are_flagged_but_never_filtered():
    """4REF is 'TR3 LBD_L449W in complex with Molecule 2'. A reader must see the mutation; a rule that
    dropped structures until the benchmark passed would be exactly the tuning this module forbids."""
    flag, ev = A.engineered_flag("Crystal Structure of TR3 LBD_L449W in complex with Molecule 2",
                                 "Crystal Structure of Nurr1 LBD")
    assert flag and ev
    assert A.engineered_flag("Crystal Structure of Nurr1 LBD")[0] is False
    # and it is not wired into any selection rule
    assert not any("MUTANT" in r.upper() and "HARD" in r for r in A.SELECTION_RULES)


def test_covalent_ligands_are_excluded_with_the_deposits_own_evidence():
    """R2b. Every deposited Nurr1 ligand complex turned out to be covalent; the exclusion cites the LINK."""
    txt = "LINK         SG  CYS A 566                 C11 RPG A 601     1555   1555  1.64\n"
    assert A.covalent_links(txt, "RPG")
    assert A.covalent_links(txt, "GOL") == []


def test_each_blind_arm_is_reported_against_its_own_control():
    """A single C1 on the pipeline box cannot interpret the fpocket arm: if the transferred site is not
    where the ligand binds, its control fails for a reason that says nothing about the docking."""
    res = _res(primary=19.4, c1=19.5)
    res["arms"]["blind_apo_fpocket_top_box"] = {"rmsd_A": 3.1, "fnat": 0.78}
    res["arms"]["C1_self_dock_holo_fpocket"] = {"rmsd_A": 1.4}
    v = A.verdict(res)
    assert v["outcome"] == "INCONCLUSIVE"
    block = v["blind_arms_each_against_its_own_control"]
    assert block["pipeline_site_transfer"]["control_passed"] is False
    assert block["fpocket_top_pocket"]["control_passed"] is True
    assert block["fpocket_top_pocket"]["blind_apo_rmsd_A"] == 3.1


def test_the_panel_has_a_wall_clock_budget_per_pair():
    """CLAUDE.md §6: the per-unit timeout is the real hang-guard. One pathological ligand must cost that
    pair and no more, and must surface as a refusal carrying its elapsed time — never as a killed job."""
    assert A.PAIR_BUDGET_S > 0 and A.PANEL_BUDGET_S > A.PAIR_BUDGET_S
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "out_of_time(" in src, "the arms must honour the deadline, not just record it"
    assert "are UNRUN, " in src, "a skipped arm must be reported as UNRUN, never as a failure"


def test_the_panel_pool_comes_from_the_full_ranked_list_not_the_40_row_excerpt():
    """★ THE CAP THAT MADE THE PANEL UNABLE TO LEAVE THE NR4A SUBFAMILY (CI run 30762378689). The excerpt
    kept for the record is 40 rows and, at two pairs per protein, yielded four candidates — all NR4A."""
    import inspect
    src = inspect.getsource(A.mode_select)
    assert "panel_pool" in src
    assert "_dedup_pairs([c for _s, c in ranked])" in src, "the pool must be built from ALL ranked pairs"


def test_the_panel_has_no_early_exit_conditioned_on_results():
    """An early exit on 'enough good ones' is a way of choosing which results to have."""
    import inspect
    src = inspect.getsource(A.main)
    assert "attempted >= PANEL_SIZE" in src
    assert 'r.get("verdict")}) >= N_BENCHMARKS' not in src


if __name__ == "__main__":
    raise SystemExit(pytest.main([os.path.abspath(__file__), "-q"]))
