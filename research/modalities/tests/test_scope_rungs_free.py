#!/usr/bin/env python3
"""Guards for the two FREE scope rungs — `R14-a` (anti-target self-control) and `R13-a` (fusion object).

Both rungs run on a free CI runner and both are gates rather than measurements, so the failure mode that
matters is a gate that PASSES when it should refuse. Every test below is shaped to catch that direction.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import antitarget_prep as prep                     # noqa: E402
import antitarget_selfcontrol as sc                # noqa: E402
import fusion_object_inventory as fi               # noqa: E402


# ==================================================================================================
# R14-a — the anti-target panel's self-control
# ==================================================================================================

def test_selfcontrol_offline_check_passes():
    assert sc.check() == 0


def test_bands_are_read_not_typed():
    """The two RMSD bands must come from `apo_pose_recovery`, so they cannot drift apart."""
    import apo_pose_recovery as apr
    b = sc.bands()
    assert b["recovered_rmsd_A"] is apr.RECOVER_RMSD_A
    assert b["partial_rmsd_A"] is apr.PARTIAL_RMSD_A
    assert b["null_power_max"] is apr.NULL_POWER_MAX
    assert "apo_pose_recovery" in b["_read_from"]


def test_protocol_is_read_from_the_panel_and_the_panel_dock():
    """A control that docks with different settings from the panel is not a control of the panel."""
    p = sc.dock_protocol()
    spec = json.load(open(os.path.join(MOD, "antitarget_panel.json")))
    assert p["box_size"] == spec["box_size"]
    assert p["exhaustiveness"] == "8" and p["num_modes"] == "1"
    src = open(os.path.join(MOD, "antitarget_dock.py")).read()
    assert '"--num_modes", "%s"' % p["num_modes"] in src


def test_one_failure_blocks_every_published_clause():
    """Every SI §S1 clause is a max/every-survivor over the panel, so one bad receptor blocks them all."""
    rows = [{"name": n, "verdict": "PASS"} for n in ("RXRA", "PPARG", "ESR1", "AR", "GR", "VDR",
                                                     "PXR", "CYP3A4", "HSA")]
    assert sc.panel_verdict(rows)["panel_readable"] is True
    rows[7]["verdict"] = "FAIL"                                   # CYP3A4, the haem-stripped one
    pv = sc.panel_verdict(rows)
    assert pv["panel_readable"] is False
    assert pv["blocking_targets"] == ["CYP3A4"]
    assert [s["readable"] for s in pv["si_s1_statements"]] == [False] * 4


def test_partial_and_unscored_are_not_passes():
    """The one direction that must never soften: anything short of PASS blocks the panel."""
    for bad in ("PARTIAL", "FAIL", "UNSCORED", "NO_POWER"):
        pv = sc.panel_verdict([{"name": "PXR", "verdict": "PASS"}, {"name": "HSA", "verdict": bad}])
        assert pv["panel_readable"] is False, bad
        assert "HSA" in pv["blocking_targets"], bad


def test_a_powerless_criterion_cannot_manufacture_a_pass():
    b = sc.bands()
    assert sc.target_verdict(0.4, 0.9, b["recovered_rmsd_A"], b["partial_rmsd_A"],
                             b["null_power_max"]) == "NO_POWER"
    assert sc.target_verdict(0.4, 0.0, b["recovered_rmsd_A"], b["partial_rmsd_A"],
                             b["null_power_max"]) == "PASS"


def test_no_power_is_not_an_excuse_for_a_miss():
    """A failure under a powerless criterion is still a failure — the opposite reading would be an alibi."""
    assert sc.target_verdict(7.0, 0.99, 2.0, 4.0, 0.05) == "FAIL"


def test_resolve_prefers_a_wild_type_receptor_over_a_better_resolution_mutant():
    ranked = sc.rank_resolve_candidates([
        {"pdb": "WTWT", "title": "Mineralocorticoid receptor LBD with aldosterone",
         "method": "X-RAY DIFFRACTION", "resolution_A": 2.4, "sequence": "M",
         "ligands": [{"comp_id": "LG1", "name": "l", "mw": 360, "smiles": "C"}]},
        {"pdb": "MUTM", "title": "MR LBD S810L with aldosterone", "method": "X-RAY DIFFRACTION",
         "resolution_A": 1.8, "sequence": "M",
         "ligands": [{"comp_id": "LG1", "name": "l", "mw": 360, "smiles": "C"}]},
    ], "P08235")
    assert ranked[0][1]["pdb"] == "WTWT"
    assert ranked[1][1]["engineered_title"] is True


def test_resolve_rejects_apo_and_nmr_entries_rather_than_ranking_them_low():
    ranked = sc.rank_resolve_candidates([
        {"pdb": "APOA", "title": "MR apo", "method": "X-RAY DIFFRACTION", "resolution_A": 1.2,
         "sequence": "M", "ligands": []},
        {"pdb": "NMRN", "title": "MR NMR", "method": "SOLUTION NMR", "resolution_A": None,
         "sequence": "M", "ligands": [{"comp_id": "L", "name": "l", "mw": 300, "smiles": "C"}]},
    ], "P08235")
    for _s, r in ranked:
        assert r["rejected_because"], r["pdb"]


def test_the_flagged_receptors_are_the_ones_the_sequence_screen_flagged():
    """MR is added because a committed screen flagged it — not because someone remembered a receptor."""
    screen = json.load(open(os.path.join(MOD, "nr4a-superfamily-selectivity.json")))
    genes = {f["gene"] for f in screen["flagged_liabilities"]}
    assert genes == {"NR3C2", "AR"}
    assert sc.MR_GENE in genes
    assert {f["gene"]: f["accession"] for f in screen["flagged_liabilities"]}[sc.MR_GENE] == sc.MR_ACCESSION


def test_the_nearest_ligand_copy_is_the_one_scored():
    """A chain carrying two copies of the same ligand must not have them merged into one 'pose'."""
    lines = [
        "HETATM    1  C1  LIG A 501       0.000   0.000   0.000  1.00  0.00           C",
        "HETATM    2  C2  LIG A 501       1.000   0.000   0.000  1.00  0.00           C",
        "HETATM    3  C1  LIG A 900      40.000  40.000  40.000  1.00  0.00           C",
        "HETATM    4  C2  LIG A 900      41.000  40.000  40.000  1.00  0.00           C",
    ]
    copy, gid = sc._pick_copy(lines, [0.5, 0.0, 0.0])
    assert len(copy) == 2 and gid[2].strip() == "501"
    copy, gid = sc._pick_copy(lines, [40.5, 40.0, 40.0])
    assert gid[2].strip() == "900"


def test_prep_refactor_is_behaviour_preserving(monkeypatch):
    """`_prep_target` must still return exactly what it always did, now delegating to prep_target_full."""
    pdb = []
    for i in range(60):                       # 60 residues so the >=50 guard passes
        pdb.append("ATOM  %5d  CA  ALA A%4d    %8.3f%8.3f%8.3f  1.00  0.00           C"
                   % (i + 1, i + 1, i * 1.0, 0.0, 0.0))
    pdb.append("HETATM 9001  C1  LIG A 501      10.000   2.000   0.000  1.00  0.00           C")
    pdb.append("HETATM 9002  C2  LIG A 501      12.000   2.000   0.000  1.00  0.00           C")
    monkeypatch.setattr(prep, "_fetch", lambda pid: pdb)
    t = {"name": "T", "pdb_id": "XXXX", "ligand_resname": "LIG"}
    text, center, n_res = prep._prep_target(t)
    full = prep.prep_target_full(t)
    assert (text, center, n_res) == (full["receptor_pdb"], full["center"], full["n_res"])
    assert center == [11.0, 2.0, 0.0]
    assert full["lig_resname"] == "LIG"
    assert len(full["lig_lines"]) == 2
    assert full["centre_source"] == "ligand"
    assert "HETATM" not in full["receptor_pdb"]


def test_the_gate_sentence_is_present_in_the_module():
    """The ordering rule is the rung; if it is ever deleted from the docstring, say so loudly."""
    src = open(os.path.join(MOD, "antitarget_selfcontrol.py")).read()
    assert "UNTIL IT PASSES NO ANTI-TARGET MARGIN FROM THIS" in src.upper()
    assert "SI §S1" in src


# ==================================================================================================
# R13-a — the fusion-object inventory
# ==================================================================================================

@pytest.fixture()
def maps():
    audit = json.load(open(os.path.join(MOD, "nr4a3-exon-audit.json")))
    cache = json.load(open(os.path.join(MOD, "nr4a-sequences-cache.json")))
    return (dict(audit["EWSR1"], protein=cache["EWSR1"]),
            dict(audit["NR4A3"], protein=cache["NR4A3"]))


def test_inventory_offline_check_passes():
    assert fi.check() == 0


def test_gate_reproduces_the_corrected_junction(maps):
    ews, nr4 = maps
    g = fi.gate(ews, nr4)
    assert g["status"] == "REPRODUCED"
    assert g["junction"] == "EWSR1(1-264)::NR4A3(1-626)"


def test_gate_refuses_the_off_by_two(maps):
    """Replay the exact bug: NR4A3 'exon 3' resolving to residue 361 must REFUSE, not warn."""
    ews, nr4 = maps
    bad = json.loads(json.dumps({k: v for k, v in nr4.items() if k != "protein"}))
    for r in bad["exons"]:
        if r["transcript_exon_rank"] == 3:
            r["first_protein_residue"] = 361
    g = fi.gate(ews, bad)
    assert g["status"] == "REFUSED"
    assert g["junction"] is None


def test_gate_refuses_a_map_that_failed_its_own_self_checks(maps):
    ews, nr4 = maps
    bad = json.loads(json.dumps({k: v for k, v in nr4.items() if k != "protein"}))
    bad["self_checks"]["cds_translation_equals_ensembl_protein"] = False
    assert fi.gate(ews, bad)["status"] == "REFUSED"


def test_a_non_coding_exon_is_skipped_not_slid(maps):
    """The bug was a silent slide onto a neighbour. A non-coding exon must produce a NAMED skip."""
    ews, nr4 = maps
    b = fi.enumerate_breakpoints(ews, nr4, {"EWSR1_exons": [7], "NR4A3_exons": [2, 3, 4]})
    skipped = {s["exon"] for s in b["skipped_exons"] if s["side"] == "NR4A3"}
    assert skipped == {2}
    assert all(r["nr4a3_exon_start"] != 2 for r in b["breakpoints"])


def test_windows_are_read_from_the_module_that_declares_them():
    import fusion_breakpoints as fb
    w = fi.declared_windows()
    assert w["EWSR1_exons"] == list(fb.EWSR1_EXON_WINDOW)
    assert w["NR4A3_exons"] == list(fb.NR4A3_EXON_WINDOW)


def test_only_the_exon3_resume_keeps_the_dna_binding_domain(maps):
    ews, nr4 = maps
    b = fi.enumerate_breakpoints(ews, nr4, fi.declared_windows())
    ps = fi.plausible_set(b["breakpoints"])
    assert ps["n_after_DBD_filter"] > 0
    assert {r["nr4a3_first_residue"] for r in ps["plausible"]} == {1}
    assert all(r["retains_C166"] for r in ps["plausible"])
    assert ps["excluded_by_DBD_filter"], "the excluded rows are KEPT as evidence, never dropped"


def test_c166_is_in_the_inventory_and_marked_unique(maps):
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    rows = {r["residue"]: r for r in doc["inventory"]["rows"]}
    assert "C166" in rows
    assert rows["C166"]["protein"] == "NR4A3"
    assert rows["C166"]["in_modelled_LBD_construct"] is False
    assert rows["C166"]["class"] == "INVARIANT"
    assert rows["C166"]["nr4a3_unique_vs_paralogues"] == ["NR4A1", "NR4A2"]
    assert nr4["protein"][165] == "C", "the residue must actually be a cysteine in the real sequence"


def test_nothing_inside_the_modelled_construct_is_listed(maps):
    """The inventory is what the construct EXCLUDES. An LBD residue appearing here is a scope error."""
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    lbd_lo, lbd_hi = fi.domain_boundaries(
        json.load(open(os.path.join(MOD, "nr4a3-structure-assessment.json"))))[fi.LBD_LABEL]
    for r in doc["inventory"]["rows"]:
        if r["protein"] == "NR4A3":
            assert r["resnum"] < lbd_lo, r


def test_invariance_split_is_exhaustive_and_derived(maps):
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    inv = doc["inventory"]
    assert inv["n_invariant"] + inv["n_breakpoint_dependent"] == inv["n_rows"]
    assert inv["_where_the_variation_is"]["proteins"] == ["EWSR1"]
    # the clause in the emitted sentence must be the DERIVED one, not a typed guess
    assert inv["_where_the_variation_is"]["clause"] in doc["the_sentence"]


def test_the_canonical_cut_is_not_the_window_maximum(maps):
    """A max over the window keeps ~526 EWSR1 residues; the canonical junction keeps 264."""
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    ex = doc["inventory"]["excluded_span"]
    assert ex["n_EWSR1_residues_canonical"] == 264
    assert ex["EWSR1_kept_range_across_plausible_breakpoints"][1] > 264
    assert "1-264" in doc["the_sentence"]


def test_the_neoantigen_artifact_is_flagged_not_regenerated(maps):
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    nf = doc["neoantigen_lane_flag"]
    assert nf["read"] is True
    assert nf["all_seams_stale"] is True
    assert nf["n_predicted_binders"] == 26
    assert sorted(nf["stale_resume_residues"]) == [318, 361, 419]
    before = open(os.path.join(MOD, "fusion-breakpoint-neoantigens.json")).read()
    assert "MHCflurry" in nf["⛔_not_fixed_here"]
    assert before == open(os.path.join(MOD, "fusion-breakpoint-neoantigens.json")).read()


def test_no_clinical_or_geometric_claim_leaks_into_the_sentence(maps):
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    s = doc["the_sentence"].lower()
    for banned in ("efficacy", "safe", "tolerab", "therapeutic window", "patients benefit",
                   "binds", "affinity", "kcal", "degrades"):
        assert banned not in s, banned


def test_map_edits_are_routed_not_applied(maps):
    """Neither module owns the roadmap. Every required change must arrive as a routed edit block."""
    ews, nr4 = maps
    doc = fi.new_doc()
    fi.assemble(ews, nr4, doc)
    edits = fi.map_edits(doc)
    assert edits
    for e in edits:
        assert set(e) >= {"section", "anchor", "current_text", "proposed_text", "why", "artifact"}
        assert e["current_text"] != e["proposed_text"]
    before = open(os.path.join(MOD, "..", "manuscripts", "nr4a3-program-map.md")).read()
    fi.map_edits(doc)
    assert before == open(os.path.join(MOD, "..", "manuscripts", "nr4a3-program-map.md")).read()


def test_selfcontrol_map_edits_carry_the_verdict():
    doc = {"selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": "FAIL"}]),
                              targets=[])}
    edits = sc.map_edits(doc)
    assert edits and any("no anti-target margin" in e["why"] for e in edits)
    doc = {"selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": "PASS"}]), targets=[])}
    edits = sc.map_edits(doc)
    assert edits and any("readable" in e["why"] for e in edits)


# ==================================================================================================
# R14-a — the COFACTOR REPAIR, after the self-control failed on CYP3A4 / PPARG / PXR
# ==================================================================================================

def _pdb(n_res=60, het=()):
    """A minimal receptor plus arbitrary HETATM groups: (resname, chain, resseq, [(x,y,z), ...])."""
    out = []
    for i in range(n_res):
        out.append("ATOM  %5d  CA  ALA A%4d    %8.3f%8.3f%8.3f  1.00  0.00           C"
                   % (i + 1, i + 1, i * 1.0, 0.0, 0.0))
    k = 9000
    for resname, chain, seq, pts in het:
        for j, (x, y, z) in enumerate(pts):
            k += 1
            out.append("HETATM%5d  C%-2d %-3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00           C"
                       % (k, j + 1, resname, chain, seq, x, y, z))
    return out


def _target():
    return {"name": "T", "pdb_id": "XXXX", "ligand_resname": "LIG"}


def test_a_contacting_cofactor_is_retained_and_a_distant_one_is_not(monkeypatch):
    """CYP3A4's haem in miniature: the predicate keeps what the ligand touches and nothing else."""
    pdb = _pdb(het=[
        ("LIG", "A", 501, [(10.0, 2.0, 0.0), (12.0, 2.0, 0.0)]),
        ("HEM", "A", 601, [(10.0, 4.0, 0.0)]),        # 2.0 A from the ligand -> IN the site
        ("HEM", "A", 602, [(10.0, 40.0, 0.0)]),       # 38 A away -> not in the site
    ])
    monkeypatch.setattr(prep, "_fetch", lambda pid: pdb)
    f = prep.prep_target_full(_target(), keep_cofactors=True)
    kept = [(k["resname"], k["resseq"]) for k in f["cofactors"]["kept"]]
    assert kept == [("HEM", "601")], kept
    assert "HEM" in f["receptor_pdb"]
    assert f["receptor_pdb"].count("HETATM") == 1, "only the contacting copy is written"


def test_the_stripped_arm_reproduces_the_published_receptor(monkeypatch):
    """The A/B is only meaningful if one arm is byte-identical to what produced SI §S1's numbers."""
    pdb = _pdb(het=[("LIG", "A", 501, [(10.0, 2.0, 0.0)]), ("HEM", "A", 601, [(10.0, 4.0, 0.0)])])
    monkeypatch.setattr(prep, "_fetch", lambda pid: pdb)
    stripped = prep.prep_target_full(_target(), keep_cofactors=False)
    assert "HETATM" not in stripped["receptor_pdb"]
    assert stripped["cofactors"]["kept"] == []
    # ...and it still REPORTS what it dropped, so the stripped arm is not silent about its own defect
    assert [d["resname"] for d in stripped["cofactors"]["dropped_in_pocket"]] == ["HEM"]
    assert stripped["cofactors"]["dropped_in_pocket"][0]["is_cofactor"] is True


def test_a_non_cofactor_in_the_pocket_is_reported_but_never_retained(monkeypatch):
    """The predicate is not 'keep whatever is nearby'. A second drug-like molecule stays out — and is
    named, because 'we stripped something else in there' must never be an unasked question."""
    pdb = _pdb(het=[("LIG", "A", 501, [(10.0, 2.0, 0.0)]), ("XYZ", "A", 700, [(10.0, 4.0, 0.0)])])
    monkeypatch.setattr(prep, "_fetch", lambda pid: pdb)
    f = prep.prep_target_full(_target(), keep_cofactors=True)
    assert f["cofactors"]["kept"] == []
    assert [d["resname"] for d in f["cofactors"]["dropped_in_pocket"]] == ["XYZ"]
    assert "not a recognised cofactor" in f["cofactors"]["dropped_in_pocket"][0]["why_still_dropped"]


def test_a_metal_ion_is_kept_only_when_the_ligand_contacts_it(monkeypatch):
    near = _pdb(het=[("LIG", "A", 501, [(10.0, 2.0, 0.0)]), ("ZN", "A", 800, [(10.0, 4.0, 0.0)])])
    far = _pdb(het=[("LIG", "A", 501, [(10.0, 2.0, 0.0)]), ("ZN", "A", 800, [(10.0, 90.0, 0.0)])])
    monkeypatch.setattr(prep, "_fetch", lambda pid: near)
    assert [k["resname"] for k in prep.prep_target_full(_target())["cofactors"]["kept"]] == ["ZN"]
    monkeypatch.setattr(prep, "_fetch", lambda pid: far)
    assert prep.prep_target_full(_target())["cofactors"]["kept"] == []


def test_the_repair_is_a_predicate_not_a_target_list():
    """⛔ THE FROZEN RULE. A per-target exception would be "dropping a failing target" by another route.

    Scanned over the EXECUTABLE code only — docstrings and comments are stripped first, because the
    reasoning legitimately names CYP3A4 as the measurement that motivated the predicate, and a guard that
    punishes documenting your evidence is a guard that gets deleted."""
    import ast
    src = open(os.path.join(MOD, "antitarget_prep.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    code = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            ds = ast.get_docstring(node, clean=False)
            if ds is not None and node.body and isinstance(node.body[0], ast.Expr):
                node.body = node.body[1:]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            continue
        if isinstance(node, ast.Name):
            code.append(node.id)
        elif isinstance(node, ast.Attribute):
            code.append(node.attr)
    # string CONSTANTS still count — a hard-coded "CYP3A4" compared against a name is the real sin
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) or isinstance(node, ast.Set) or isinstance(node, ast.List):
            for c in ast.walk(node):
                if isinstance(c, ast.Constant) and isinstance(c.value, str):
                    code.append(c.value)
    blob = " ".join(code)
    for name in ("CYP3A4", "PPARG", "PXR", "2V0M", "2PRG", "1NRL"):
        assert name not in blob, "the prep branches on %s — that is a per-target exception" % name


def test_the_silent_ligand_fallback_is_now_reported(monkeypatch):
    """PXR was centred on SRL while the panel declared 348, and nothing said so. A populated field is
    not a measured one (CLAUDE.md §4b)."""
    pdb = _pdb(het=[("SRL", "A", 501, [(10.0, 2.0, 0.0), (12.0, 2.0, 0.0)])])
    monkeypatch.setattr(prep, "_fetch", lambda pid: pdb)
    f = prep.prep_target_full({"name": "PXR", "pdb_id": "1NRL", "ligand_resname": "348"})
    assert f["ligand_resname_matched"] is False
    assert f["ligand_resname_declared"] == "348" and f["lig_resname"] == "SRL"
    f2 = prep.prep_target_full({"name": "PXR", "pdb_id": "1NRL", "ligand_resname": "SRL"})
    assert f2["ligand_resname_matched"] is True


def test_every_crystal_copy_is_considered_before_a_pose_is_called_a_miss():
    """Some deposits place one ligand in several orientations in one cavity. Scoring against a single
    copy would call a genuinely observed pose a miss."""
    lines = [
        "HETATM    1  C1  SRL A 501       0.000   0.000   0.000  1.00  0.00           C",
        "HETATM    2  C1  SRL B 501      30.000   0.000   0.000  1.00  0.00           C",
        "HETATM    3  C1  ZZZ A 900      60.000   0.000   0.000  1.00  0.00           C",
    ]
    copies = sc._all_cognate_copies(lines, "SRL")
    assert len(copies) == 2 and all(g[0] == "SRL" for g in copies)


def test_the_si_edit_only_exists_while_the_panel_is_unreadable():
    """⛔ It conditions a published sentence. Emitting it after a pass would be a false alarm in the SI."""
    fail = {"criterion": {"recovered_rmsd_A": 2.0},
            "selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": "FAIL"}]),
                                targets=[{"name": "PXR", "verdict": "FAIL", "rmsd_A": 6.761}])}
    edits = sc.si_edits(fail)
    # BOTH manuscripts, because the main text asserts the same panel-wide maximum as the SI. Conditioning
    # only the SI leaves a reader who never opens it with the unqualified claim.
    files = sorted(e["file"] for e in edits)
    assert files == ["research/manuscripts/nr4a3-degrader-paper-SI.md",
                     "research/manuscripts/nr4a3-degrader-paper.md"], files
    assert all("NOT CURRENTLY READABLE" in e["proposed_text"] for e in edits)
    si = [e for e in edits if e["file"].endswith("-SI.md")][0]
    assert "PXR" in si["proposed_text"] and "6.761" in si["proposed_text"]
    ok = {"criterion": {"recovered_rmsd_A": 2.0},
          "selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": "PASS"}]), targets=[])}
    assert sc.si_edits(ok) == []


def test_the_si_edit_conditions_the_result_rather_than_deleting_it():
    """The frozen rule licenses one thing: saying the margin is not currently readable."""
    fail = {"criterion": {"recovered_rmsd_A": 2.0},
            "selfcontrol": dict(sc.panel_verdict([{"name": "PXR", "verdict": "FAIL"}]),
                                targets=[{"name": "PXR", "verdict": "FAIL", "rmsd_A": 6.761}])}
    for e in sc.si_edits(fail):
        assert e["current_text"] in e["proposed_text"], "the original sentence must survive verbatim"
    si = [e for e in sc.si_edits(fail) if e["file"].endswith("-SI.md")][0]
    assert "may not be quoted until the control passes" in si["proposed_text"]
