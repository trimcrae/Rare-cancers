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


def test_the_receptor_chain_follows_the_accession_not_the_atom_count():
    """★ 1DSZ is an RXR/RAR heterodimer on DNA. 'Largest chain' handed the RARA pair an RXR chain and the
    apo<->holo alignment then returned 0.321 identity and refused — a real pair lost to a chain-picking
    bug (CI run 30762604893)."""
    txt = ("ATOM      1  CA  MET A   1       0.000   0.000   0.000  1.00  0.00           C\n"
           "ATOM      2  CA  LYS A   2       1.000   0.000   0.000  1.00  0.00           C\n"
           "ATOM      3  CA  LEU A   3       2.000   0.000   0.000  1.00  0.00           C\n"
           "ATOM      4  CA  GLY B   1       9.000   0.000   0.000  1.00  0.00           C\n")
    assert A._largest_of(txt) == "A"                      # A is bigger
    assert A._largest_of(txt, allowed=["B"]) == "B"        # but the accession says B
    assert A._largest_of(txt, allowed=["Z"]) == "A"        # an allowed set matching nothing must not wedge
    # the ligand sits on B; declaring B keeps B, and declaring A (which has nothing nearby) falls back
    # rather than returning nothing — an allowed set that matches no contact must never wedge the run
    assert A._chain_nearest(txt, [(9.0, 0.0, 0.0)], allowed=["B"]) == "B"
    assert A._chain_nearest(txt, [(9.0, 0.0, 0.0)], allowed=["A"]) == "B"
    assert A._chain_nearest(txt, [(1.0, 0.0, 0.0)], allowed=["A"]) == "A"


def test_the_protocol_ceiling_control_exists_and_can_only_flatter_the_pipeline():
    """C1c: same receptor the ligand was solved in, box centred on the ligand. A miss HERE is the search
    and scoring, not the site. It is strictly more favourable than the pre-registered primary, so adding it
    cannot be a route to tuning toward a pass."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "C1c_self_dock_holo_oracle_box" in src
    assert "oracle_center_holo" in src
    res = _res(primary=19.0, c1=19.5)
    res["arms"]["C1c_self_dock_holo_oracle_box"] = {"rmsd_A": 1.1}
    v = A.verdict(res)
    assert v["outcome"] == "INCONCLUSIVE", "a favourable ceiling control cannot overturn the primary"
    assert v["blind_arms_each_against_its_own_control"]["C1c_protocol_ceiling"][
        "self_dock_holo_oracle_box_rmsd_A"] == 1.1


def test_a_missing_legacy_pdb_file_is_named_as_a_format_refusal():
    """9QX6 returned HTTP 404 from files.rcsb.org: mmCIF-only. That is a FILE-FORMAT exclusion, not a
    scientific one, and it biases the panel toward older entries — so it has to say so."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "mmCIF-only" in src and "FILE-FORMAT reason" in src


# ==================================================================================================
# SITE vs DOCKING — the two questions the first panel could not tell apart (added 2026-08-02)
# ==================================================================================================

def test_the_added_arms_moved_no_pre_registered_threshold():
    """⛔ THE WHOLE POINT OF ADDING ARMS RATHER THAN CHANGING ONE. `test_thresholds_are_frozen` pins the
    numbers; this pins the SHAPE — the added endpoints must be new keys, and `verdict()` must still be the
    only thing that decides the headline."""
    assert A.LARGE_INDUCED_FIT_A == 1.00        # a REPORTING band, gates nothing
    assert A.STRUCT_TRANSFER_MAX_CA_A == 6.00
    import inspect
    src = inspect.getsource(A.verdict)
    for added in ("Q_SITE", "structure_transfer", "SITE FOUND", "LARGE_INDUCED_FIT_A", "seqadv"):
        assert added not in src, "%s leaked into the verdict — the headline must stay pre-registered" % added


def test_the_appendix_registers_every_change_and_keeps_the_superseded_value():
    """CLAUDE.md §1.2: a corrected number is never silently dropped."""
    ap = A.APPENDIX
    assert ap["unchanged"] and ap["added_2026_08_02_second_revision"]
    for row in ap["corrected_2026_08_02"]:
        assert row["superseded"] and row["now"] and row["what"]
    joined = " ".join(r["superseded"] for r in ap["corrected_2026_08_02"])
    assert "420" in joined and "2700" in joined, "the old wall-clock budgets must remain quotable"
    # ⚠ EVERY correction block, derived — not one hard-coded date. A correction list that exists in the
    # artifact and renders nowhere is the same failure as not registering it (asserted as a property).
    blocks = [k for k in ap if k.startswith("corrected_")]
    assert len(blocks) >= 2
    for k in blocks:
        for row in ap[k]:
            assert row["superseded"] and row["now"] and row["what"], "%s has an unregistered row" % k
    md = A.render_markdown({"_appendix": ap, "verdict": {"outcome": "INCONCLUSIVE", "reason": "x"}})
    for k in blocks:
        for row in ap[k]:
            assert row["what"] in md, "%s is registered but renders nowhere" % row["what"]


def test_the_site_endpoint_contains_no_docking():
    """A ligand outside the box cannot be found by any search, so the site question is answerable with
    geometry alone — deterministic, where an RMSD through a stochastic search is not."""
    box = (24.0, 24.0, 24.0)
    inside = A.box_containment((0, 0, 0), box, [(1, 1, 1), (2, 2, 2)])
    assert inside["ligand_centroid_in_box"] is True
    assert inside["frac_ligand_heavy_atoms_in_box"] == 1.0
    far = A.box_containment((0, 0, 0), box, [(30, 0, 0), (31, 0, 0)])
    assert far["ligand_centroid_in_box"] is False
    assert far["frac_ligand_heavy_atoms_in_box"] == 0.0
    # exactly on the face is inside; one step beyond is not — the boundary must not be vague
    assert A.box_containment((0, 0, 0), box, [(12.0, 0, 0)])["ligand_centroid_in_box"] is True
    assert A.box_containment((0, 0, 0), box, [(12.01, 0, 0)])["ligand_centroid_in_box"] is False
    assert A.box_containment(None, box, [(0, 0, 0)]) is None


def test_the_site_answer_reports_native_contact_recall_through_the_residue_map():
    row = A.site_answer((0, 0, 0), (24.0, 24.0, 24.0), [(0, 0, 0)],
                        box_residues=[10, 11, 12], res_map={10: 110, 11: 111, 12: 112},
                        native=[110, 111, 900, 901], site_label="x")
    assert row["answer"] == "SITE FOUND"
    assert row["n_box_residues_that_are_native_contacts"] == 2
    assert row["native_contact_recall_of_box_residues"] == 0.5
    assert A.site_answer(None, (24.0,) * 3, [(0, 0, 0)], None, None, [1], "y")["answer"] == "UNREAD"


def test_seqadv_is_read_from_the_deposit_not_inferred_from_the_title():
    """The title says 'L449W'; only SEQADV says which residue number the FILE uses and what it replaced."""
    txt = ("SEQADV 4REF TRP A  449  UNP  P22736    LEU   449 ENGINEERED MUTATION\n"
           "SEQADV 4REF GLY A  348  UNP  P22736              EXPRESSION TAG\n"
           "ATOM      1  CA  TRP A 449       0.000   0.000   0.000  1.00  0.00           C\n")
    got = A.seqadv_mutations(txt)
    assert len(got) == 2
    eng = [m for m in got if m["reason"] == "ENGINEERED MUTATION"]
    assert eng[0]["resseq"] == 449 and eng[0]["db_residue"] == "LEU" and eng[0]["deposit_residue"] == "TRP"
    assert A.seqadv_mutations(txt, chain="B") == []


def test_a_file_with_no_seqadv_block_is_UNREAD_not_wild_type():
    """⚠ CLAUDE.md §4: an absent reading is not a reading of absence. 'No engineered mutation declared'
    and 'this deposit carries no SEQADV records at all' are different facts, and one sentence covering
    both would let an unread file read as a clean wild-type deposit."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "NO SEQADV RECORDS AT ALL" in src
    assert "are UNREAD here, not" in src
    assert "none of them declares an engineered mutation" in src, \
        "the SEQADV-present-but-clean case must have its own sentence"


def test_a_declared_allosteric_ligand_is_read_from_the_title_and_never_filters():
    flag, ev = A.allosteric_flag("ROR(gamma)t ligand binding domain in complex with allosteric ligand FM156")
    assert flag and ev
    assert A.allosteric_flag("PPARgamma LBD in complex with rosiglitazone")[0] is False
    assert not any("ALLOSTERIC" in r.upper() for r in A.SELECTION_RULES), "reported, never a selection rule"


def _pair(seq_answer, struct_answer, accession="P22736", allosteric=False, eng_in_site=None,
          oracle=3.4, ceiling=1.1):
    def row(ans):
        return {"answer": ans, "ligand_centroid_in_box": ans == "SITE FOUND",
                "frac_ligand_heavy_atoms_in_box": 1.0 if ans == "SITE FOUND" else 0.0,
                "box_center_to_ligand_centroid_A": 1.0 if ans == "SITE FOUND" else 19.0,
                "native_contact_recall_of_box_residues": 0.8 if ans == "SITE FOUND" else 0.0}
    return {
        "arms": {"C3_oracle_box_apo": {"rmsd_A": oracle, "fnat": 0.7},
                 "C1c_self_dock_holo_oracle_box": {"rmsd_A": ceiling}},
        "boxes": {"pipeline_apo": {"center": (0, 0, 0), "detail": {"nr4a3_aligned_identity": 0.6}},
                  "struct_transfer_apo": {"center": (1, 0, 0),
                                          "detail": {"ce_rms_A": 2.1, "n_pocket5_transferred": 10,
                                                     "n_pocket5_source": 10,
                                                     "n_unique_receptor_residues": 8}}},
        "declared_allosteric": {"declared_in_holo_title": allosteric, "evidence": ["t"] if allosteric else []},
        "engineered_construct": {"engineered_residues_in_native_ligand_site": eng_in_site or []},
        "Q_SITE_does_site_selection_find_the_ligand": {"routes": {
            "pipeline_sequence_transfer_apo": row(seq_answer),
            "pocket5_structure_transfer_apo": row(struct_answer),
            "fpocket_top_pocket_apo": row("SITE FOUND")}},
    }, {"accession": accession, "protein": "p", "apo": "AAAA", "holo": "BBBB",
        "ligand": {"comp_id": "LIG"}}


def test_the_docking_question_is_asked_with_the_site_handed_over_and_its_own_ceiling():
    res, cand = _pair("SITE MISSED", "SITE MISSED", oracle=3.4, ceiling=1.1)
    q = A.pair_questions(res, cand)["Q_DOCKING_given_the_correct_site"]
    assert q["arm"].startswith("C3_oracle_box_apo")
    assert q["control_passed"] is True
    assert q["answer"] == "PARTIAL", "3.4 A is the pre-registered PARTIAL band, unchanged"
    # a failing ceiling makes the DOCKING question uninterpretable — the same rule C1 applies to the primary
    res2, cand2 = _pair("SITE MISSED", "SITE MISSED", oracle=3.4, ceiling=2.9)
    q2 = A.pair_questions(res2, cand2)["Q_DOCKING_given_the_correct_site"]
    assert q2["control_passed"] is False and q2["answer"].startswith("INCONCLUSIVE")


def test_the_confound_reading_separates_a_broken_alignment_from_a_ligand_elsewhere():
    """⛔ THE ONE ARM THAT CAN SETTLE IT. Two independent transfers of the SAME site; a docking RMSD gives
    the same big number under both causes, and the causes have opposite remedies."""
    def reading(seq, struct):
        res, cand = _pair(seq, struct)
        return A.pair_questions(res, cand)["Q_SITE_does_site_selection_find_the_site"]["confound_reading"]
    assert "real defect in the pipeline" in reading("SITE MISSED", "SITE FOUND")
    assert "benchmark's design" in reading("SITE MISSED", "SITE MISSED")
    assert "any miss on this pair is the docking" in reading("SITE FOUND", "SITE FOUND")
    assert "fold superposition" in reading("SITE FOUND", "SITE MISSED")


def test_the_regime_gate_is_read_from_the_pipeline_not_typed_here():
    """CLAUDE.md §1: one fact, one place. The set of proteins the pipeline transfers Pocket-5 onto lives in
    `nr4a3_warhead.PARALOGUES`; a copy here would drift the day someone adds a paralogue."""
    import nr4a3_warhead as wh
    import inspect
    src = inspect.getsource(A.pair_questions)
    assert "wh.PARALOGUES" in src
    for acc in wh.PARALOGUES.values():
        res, cand = _pair("SITE MISSED", "SITE MISSED", accession=acc)
        s = A.pair_questions(res, cand)["Q_SITE_does_site_selection_find_the_site"]
        assert s["interpretable_as_evidence_about_the_pipeline"] is True
    # PPARG is NOT a protein the pipeline ever transfers onto, so its site arm is not evidence about it
    res, cand = _pair("SITE MISSED", "SITE MISSED", accession="P37231")
    s = A.pair_questions(res, cand)["Q_SITE_does_site_selection_find_the_site"]
    assert s["interpretable_as_evidence_about_the_pipeline"] is False
    assert any("OUT OF THE PIPELINE'S REGIME" in d for d in s["disqualifiers"])


def test_a_declared_allosteric_or_engineered_pocket_disqualifies_the_site_arm_but_not_the_docking_arm():
    res, cand = _pair("SITE MISSED", "SITE MISSED", allosteric=True)
    q = A.pair_questions(res, cand)
    s = q["Q_SITE_does_site_selection_find_the_site"]
    assert s["interpretable_as_evidence_about_the_pipeline"] is False
    assert any("ALLOSTERIC" in d for d in s["disqualifiers"])
    # the docking question is untouched: the correct site was handed over, whatever site that is
    assert q["Q_DOCKING_given_the_correct_site"]["answer"] == "PARTIAL"
    res2, cand2 = _pair("SITE MISSED", "SITE MISSED",
                        eng_in_site=[{"db_residue": "LEU", "resseq": 449, "deposit_residue": "TRP"}])
    s2 = A.pair_questions(res2, cand2)["Q_SITE_does_site_selection_find_the_site"]
    assert s2["interpretable_as_evidence_about_the_pipeline"] is False
    assert any("ENGINEERED RESIDUE" in d for d in s2["disqualifiers"])


def test_the_panel_counts_the_site_question_over_interpretable_pairs_only():
    """Including a pair the benchmark's own design disqualified would let the design set the grade."""
    ran = []
    for acc, seq in (("P22736", "SITE MISSED"), ("P37231", "SITE MISSED"), ("P51449", "SITE MISSED")):
        res, cand = _pair(seq, "SITE MISSED", accession=acc)
        res["candidate"] = cand
        res["questions"] = A.pair_questions(res, cand)
        res["induced_fit"] = {"site_ca_rmsd_A": 0.142, "global_ca_rmsd_A": 0.457, "n_site": 9,
                              "large_rearrangement": False}
        ran.append(res)
    out = A.panel_site_vs_docking(ran)
    site = out["Q_SITE_does_site_selection_find_the_site"]
    assert site["n_pairs"] == 3 and site["n_interpretable_about_the_pipeline"] == 1
    assert site["pipeline_sequence_transfer_found"] == 0
    doc = out["Q_DOCKING_given_the_correct_site"]
    assert doc["n_gradeable"] == 3 and doc["n_partial"] == 3


def test_the_induced_fit_panel_says_out_loud_when_no_pair_is_a_real_test():
    """★ THE CAVEAT THAT MUST NOT BE BURIED. A cross-dock across 0.14 A of Ca movement is a re-dock; a
    panel made only of those cannot speak to apo->holo transfer whatever any RMSD says."""
    small = [{"candidate": {"apo": "A", "holo": "B", "protein": "p"},
              "induced_fit": {"site_ca_rmsd_A": 0.142, "global_ca_rmsd_A": 0.457, "n_site": 9,
                              "large_rearrangement": False}}]
    out = A.panel_induced_fit(small)
    assert out["panel_contains_a_large_rearrangement"] is False
    assert out["_reads"].startswith("⛔")
    assert "CANNOT speak to apo->holo" in out["_reads"]
    big = small + [{"candidate": {"apo": "C", "holo": "D", "protein": "q"},
                    "induced_fit": {"site_ca_rmsd_A": 6.46, "global_ca_rmsd_A": 2.78, "n_site": 22,
                                    "large_rearrangement": True}}]
    out2 = A.panel_induced_fit(big)
    assert out2["panel_contains_a_large_rearrangement"] is True
    assert out2["n_with_large_rearrangement"] == 1 and out2["max_site_ca_rmsd_A"] == 6.46
    assert "measured AT THE NATIVE LIGAND SITE" in out2["_caveat"]


def test_the_fpocket_rank_sentence_no_longer_claims_a_cavity_on_a_single_shared_residue():
    """⚠ CORRECTED. The first panel printed 'the transferred site IS a cavity on this receptor' beside
    `n_shared_residues: 1`. One residue in ten is a contact between two sets, not the same site."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "frac_transferred_residues_in_that_pocket" in src
    assert "only CLIPS this pocket" in src
    assert any("frac_transferred_residues_in_that_pocket" in str(r) or "_reads" in str(r)
               for r in A.APPENDIX["corrected_2026_08_02"])


def test_the_structural_transfer_uses_no_sequence_information():
    """C4 exists precisely because the pipeline's transfer is a sequence alignment. If this one used the
    sequence too, it could not be a control on it."""
    import ast
    import inspect
    import textwrap
    src = inspect.getsource(A.pocket5_structure_transfer)
    assert "cealign" in src and "CEAligner" in src and "STRUCT_TRANSFER_MAX_CA_A" in src
    # ⚠ THE PROSE NAMES THE SEQUENCE TRANSFER IT IS A CONTROL ON, so a substring scan over the source
    # would fail on its own docstring. What must be free of sequence alignment is the EXECUTED code, so
    # this walks the AST and looks at names actually referenced and modules actually imported.
    tree = ast.parse(textwrap.dedent(src))
    names, imports = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Import):
            imports.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
            names.update(a.name for a in node.names)
    for seqish in ("PairwiseAligner", "map_pocket_to_paralogue", "substitution_matrices",
                   "identity_from_blocks", "chain_ca", "_biopython_align", "map_uniprot_to_pdb"):
        assert seqish not in names, "%s would make C4 a second sequence transfer, not a control" % seqish
    assert not any(m.startswith("Bio.Align") for m in imports)
    assert any("cealign" in m for m in imports)


def test_the_structural_transfer_recovers_pocket5_on_nr4a3_itself():
    """The positive control for C4: carry NR4A3's Pocket-5 onto an NR4A3 structure. Both transfers must
    land in the same place, or the structural arm cannot be trusted to adjudicate anything."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    af2 = os.path.join(here, "..", "..", "results", "nr4a3-metad-r2", "ckpt", "AF-Q92570.pdb")
    rec = os.path.join(here, "_pose_convergence_inputs", "8xtt_model2_nr4a3.pdb")
    if not (os.path.exists(af2) and os.path.exists(rec)):
        pytest.skip("the NR4A3 reference structures are not in this checkout")
    pytest.importorskip("Bio.PDB.cealign")
    import tempfile
    work = tempfile.mkdtemp()
    ref, why = A.nr4a3_lbd_reference(os.path.abspath(af2), work)
    assert ref is not None, why
    sc, sdet = A.pocket5_structure_transfer(ref, rec)
    assert sc is not None, sdet
    assert sdet["n_pocket5_transferred"] >= 8
    qc, _qdet = A.pipeline_box(rec, os.path.abspath(af2), work)
    assert qc is not None
    d = math.dist(sc, qc)
    size = float(A.pipeline_dock_params().get("size_x", 24))
    assert d < size / 2.0, ("sequence and structure transfers disagree by %.2f A on NR4A3 itself — C4 "
                            "cannot adjudicate anything until they agree on the positive control" % d)


# ============================================================ C6 — seed replicates (added 2026-08-03)

def _fake_replicates(vals, arm="blind_apo_fpocket_top_box"):
    """Drive `seed_replicates` with a scripted sequence of RMSDs and no smina.

    `vals[0]` is the arm's unseeded draw; the rest are the replicate docks, and the LAST of those is the
    repeat of the first seed — that is the determinism self-check — so callers pass
    `1 + n_seeds + 1` numbers and the helper does not have to know the seed list. Only `arm` is given a
    box, so the other two replicated arms record themselves UNRUN instead of eating the sequence."""
    seq = list(vals[1:])

    def score_pose(mol, transform=True):
        v = seq.pop(0)
        return {"rmsd_A": v, "fnat": 0.5, "verdict": A._band(v)}

    real_dock, real_top = A.dock_seeded, A._top_pose
    A.dock_seeded = lambda *a, **k: ("/dev/null/pose.sdf", None)
    A._top_pose = lambda p, c: (object(), None)
    plan = {a: (None, None, True) for a in A.REPLICATED_ARMS}
    plan[arm] = ("rec.pdb", (0.0, 0.0, 0.0), True)
    try:
        return A.seed_replicates(len(vals) - 2, "/tmp", "lig.sdf", "LIG", score_pose,
                                 {arm: {"rmsd_A": vals[0]}}, plan, lambda stage: False)
    finally:
        A.dock_seeded, A._top_pose = real_dock, real_top


def test_c6_replicates_the_arms_the_program_actually_quotes():
    """A reproducibility control that skipped the arm the roadmap cites would measure nothing that
    matters. These three are named because each carries a decision."""
    assert "blind_apo_fpocket_top_box" in A.REPLICATED_ARMS      # the 3.04 A the roadmap quotes
    assert "C3_oracle_box_apo" in A.REPLICATED_ARMS              # Q-DOCKING's own arm
    assert "C1c_self_dock_holo_oracle_box" in A.REPLICATED_ARMS  # whether a pair is gradeable at all
    assert A.SEED_REPLICATES >= 3
    assert len(set(A.REPLICATE_SEEDS)) == len(A.REPLICATE_SEEDS), "the declared seeds must be distinct"


def test_c6_endpoint_is_the_band_not_a_tighter_number():
    """⛔ The whole risk of a replicate arm is that it becomes a way of reporting a nicer RMSD. The
    endpoint is whether the PRE-REGISTERED band holds; a stable band is reported as such, and the
    reading says out loud not to quote the digits."""
    out = _fake_replicates([3.04, 3.04, 3.5, 3.12, 3.9, 2.4, 3.04])
    row = out["arms"]["blind_apo_fpocket_top_box"]
    assert row["band_stable"] is True
    assert row["bands_seen"] == ["PARTIAL"]
    assert row["spread_A"] == round(3.9 - 2.4, 3)
    assert "never the" in row["_reads"] and "band" in row["_reads"]


def test_c6_says_the_arm_is_unquotable_when_the_band_flips():
    out = _fake_replicates([3.04, 1.8, 3.5, 4.6, 3.1, 2.2, 1.8])
    row = out["arms"]["blind_apo_fpocket_top_box"]
    assert row["band_stable"] is False
    assert set(row["bands_seen"]) == {"RECOVERED", "PARTIAL", "NOT RECOVERED"}
    assert "not quotable" in row["_reads"] or "quotable" in row["_reads"]


def test_c6_runs_the_first_seed_twice_and_reports_whether_it_reproduced():
    """A spread may only be attributed to seeding if the search reproduces at a fixed seed. The repeat
    is excluded from the spread itself, or the first seed would be double-counted."""
    same = _fake_replicates([3.04, 3.30, 3.40, 3.50, 3.60, 3.70, 3.30])
    chk = same["arms"]["blind_apo_fpocket_top_box"]["_determinism_selfcheck"]
    assert chk["identical"] is True and chk["first_rmsd_A"] == chk["repeat_rmsd_A"] == 3.30
    assert same["arms"]["blind_apo_fpocket_top_box"]["n_replicates"] == 5

    diff = _fake_replicates([3.04, 3.30, 3.40, 3.50, 3.60, 3.70, 3.99])
    chk2 = diff["arms"]["blind_apo_fpocket_top_box"]["_determinism_selfcheck"]
    assert chk2["identical"] is False
    assert "non-determinism" in chk2["_reads"]


def test_c6_can_never_reach_the_verdict():
    """Same guard as the second revision's added arms: a new control may not become the headline."""
    import inspect
    src = inspect.getsource(A.verdict)
    for leaked in ("C6", "seed_replicates", "band_stable", "REPLICATE_SEEDS"):
        assert leaked not in src, "%s leaked into verdict() — the headline stays pre-registered" % leaked
    assert A.RECOVER_RMSD_A == 2.00 and A.PARTIAL_RMSD_A == 4.00


def test_c6_leaves_the_pipelines_own_dock_unseeded():
    """⛔ THE UNSEEDED SEARCH IS THE BEHAVIOUR UNDER TEST. Seeding `nr4a3_warhead.dock_into` would change
    every number this program has ever produced and would make the control measure nothing."""
    import inspect
    import nr4a3_warhead as wh
    assert "--seed" not in inspect.getsource(wh.dock_into)
    seeded = inspect.getsource(A.dock_seeded)
    assert "--seed" in seeded
    # every other setting still comes from the pipeline, or a replicate would measure the settings
    assert "pipeline_dock_params()" in seeded
    for hardcoded in ('"--exhaustiveness", "8"', '"--size_x", "24"'):
        assert hardcoded not in seeded


def test_an_absent_replicate_set_is_recorded_as_absent_not_as_no_variation():
    """CLAUDE.md §4: an absent reading is not a reading of absence."""
    rp = A.panel_reproducibility([{"verdict": {"outcome": "INCONCLUSIVE"}}])
    assert rp["measured"] is False
    assert "UNMEASURED" in rp["_reads"] or "not zero" in rp["_reads"]


def test_the_reproducibility_rollup_flags_every_arm_whose_band_flips():
    out = _fake_replicates([3.04, 1.8, 3.5, 4.6, 3.1, 2.2, 1.8])
    rp = A.panel_reproducibility([{"C6_seed_replicates": out}])
    assert rp["measured"] is True
    assert "blind_apo_fpocket_top_box" in rp["arms_whose_band_flips"]
    assert rp["all_bands_stable"] is False


# ============================================================ C5b — the apo side of the construct

def test_c5b_grades_the_apo_construct_not_only_the_holo_one():
    """⛔ THE HEADLINE PAIR IS TWO DIFFERENT MUTANTS. 4RZF is 'NUR77 LBD, S441W mutant' and 4REF is
    'TR3 LBD_L449W'; the artifact already carried both SEQADV blocks and graded only the holo one, so
    the pair read as two states of ONE construct when it is a cross-CONSTRUCT dock as well."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    for field in ("engineered_residues_apo", "apo_and_holo_are_the_same_construct",
                  "engineered_apo_residues_in_native_ligand_site"):
        assert field in src, "%s is not emitted — the apo construct is ungraded" % field
    # the comparison must go through the apo->holo residue map, not raw resseqs in two frames
    assert "apo_to_holo[m[\"resseq\"]]" in src


def test_a_construct_mismatch_says_the_induced_fit_is_not_pure_conformational_change():
    """The whole reason to compare the two SEQADV sets: `induced_fit.site_ca_rmsd_A` is quoted as the
    size of the apo→holo problem, and on a cross-construct pair it is not only that."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    assert "cross-CONSTRUCT" in src
    assert "must not be quoted as pure conformational change" in src


def test_c5b_reports_and_never_filters():
    """Same rule as C5: a declared construct difference is evidence on the record, not an exclusion —
    the artifact must not gain a filter that silently shrinks the panel."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    i = src.find("apo_and_holo_are_the_same_construct")
    assert i > 0
    tail = src[i:i + 2500]
    for excluding in ("return refuse", "excluded_by"):
        assert excluding not in tail, "C5b became a filter — it may only report"


def test_the_markdown_says_UNREAD_when_the_apo_construct_was_never_compared():
    """CLAUDE.md §4: an artifact predating C5b must not render as 'the constructs match'."""
    doc = {"panel": [{"verdict": {"outcome": "INCONCLUSIVE"},
                      "candidate": {"apo": "4RZF", "holo": "4REF"},
                      "engineered_construct": {"engineered_residues_holo": []}}],
           "verdict": {"outcome": "INCONCLUSIVE", "reason": "x"}}
    md = A.render_markdown(doc)
    assert "UNREAD" in md
    assert 'Absent, not "the constructs match"' in md


# ============================================================ the inert chain restriction (2026-08-03)

def test_the_panel_pool_carries_the_declared_chains_or_the_restriction_is_inert():
    """⛔ THE FIX LANDED AND THEN RAN AGAINST `None` FOR THE WHOLE PANEL. `run_benchmark` restricts the
    receptor chain to the ones the deposit assigns to the UniProt entity under test — the repair for the
    1DSZ RXR/RAR heterodimer handing the RARA pair an RXR chain. `_dedup_pairs` projected each candidate
    onto a fixed key list that dropped `apo_chains`/`holo_chains`, so every panel pair reached that code
    with no allowed set at all. This test is the property, not the wording: what goes in comes out."""
    rows = [{"accession": "P10276", "protein": "RARA", "apo": "1DSZ", "holo": "9GFE",
             "ligand": {"comp_id": "EQN"}, "apo_chains": ["D"], "holo_chains": ["A"],
             "apo_method": "X-RAY DIFFRACTION", "apo_title": "t", "holo_title": "t"}]
    out = A._dedup_pairs(rows)
    assert out and out[0].get("apo_chains") == ["D"], "apo_chains was dropped — the restriction is inert"
    assert out[0].get("holo_chains") == ["A"], "holo_chains was dropped — the restriction is inert"


def test_a_low_identity_refusal_names_the_pair_it_actually_compared():
    """`map_uniprot_to_pdb` hard-codes Q92570/8XTT in its error. Passed through it told the reader an
    RXRA pair failed to align against NR4A3's NMR structure — two proteins neither of which is in the
    pair, which is how the same refusal got mis-diagnosed. The re-statement must survive refactoring."""
    import inspect
    src = inspect.getsource(A.run_benchmark)
    i = src.find("apo<->holo alignment failed")
    assert i > 0
    frag = src[i:i + 1400]
    assert 'cand["apo"]' in frag and 'cand["holo"]' in frag, "the refusal does not name the real pair"
    assert "CHAIN-SELECTION symptom" in frag
    # and the upstream function is left alone — other lanes call it
    import nr4a3_8xtt_benchmark as bm
    assert "Q92570" in inspect.getsource(bm.map_uniprot_to_pdb)


def test_the_third_revision_is_registered_in_the_appendix():
    ap = A.APPENDIX
    joined = " ".join(ap["added_2026_08_03_third_revision"])
    assert "C6" in joined and "band" in joined
    assert "verdict()` does not read it" in joined or "does not read it" in joined


if __name__ == "__main__":
    raise SystemExit(pytest.main([os.path.abspath(__file__), "-q"]))
