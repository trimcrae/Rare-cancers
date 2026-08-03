"""Unit tests for `paralogue_site_correction` — the $0 fix for the anti-target docking box.

★★ WHAT THESE GUARD. This module produces a CORRECTED SITE that downstream selectivity work is meant to
adopt, which makes it the most consequential kind of artifact in the repo: one whose output becomes an
input. Every test here pins a rule that, if it slipped, would let a wrong site through looking right.

Offline: no network, no smina, no fpocket, no Bio.PDB required.
"""
import inspect
import json
import os
import re

import paralogue_site_correction as P


def test_the_holo_entry_list_is_READ_not_typed():
    """⛔ ONE FACT, ONE PLACE. The in-regime entries live in `apo-pose-site-in-regime.json`, which the
    docking panel also grades. A hand-typed list here could drift from it silently and nothing would
    catch it — and then the correction and the evidence for the correction would be about different sets.
    """
    # ⚠ EXECUTABLE CODE ONLY — every docstring is stripped via the AST (widened 2026-08-03). The first
    # version skipped only the MODULE docstring and then failed when `af2_domain_span`'s docstring cited
    # `4WHF`/`4WHG` as the EVIDENCE for the register bug. Naming the deposits that proved a defect is
    # exactly what a docstring is for; the rule is that no entry list is typed into the code.
    import ast
    tree = ast.parse(inspect.getsource(P))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc and node.body and isinstance(node.body[0], ast.Expr):
                node.body[0].value = ast.Constant(value="")
    code = ast.unparse(tree)
    ids = set(re.findall(r"\b[1-9][A-Z0-9]{3}\b", code)) - {"2026", "3000"}
    assert not ids, "PDB-like literals typed into the code: %s — read them from the panel" % sorted(ids)
    assert "apo-pose-site-in-regime.json" in inspect.getsource(P)


def test_the_box_edge_comes_from_the_pipeline_not_from_a_constant():
    """A containment test against a box the pipeline never draws is a test of nothing. The edge is parsed
    out of `dock_into`'s own smina invocation, so a change there follows through here."""
    assert P._pipeline_box_edge() == 24.0
    import nr4a3_warhead as wh
    assert '"--size_x", "24"' in inspect.getsource(wh.dock_into), \
        "the pipeline's box edge moved; `_pipeline_box_edge` should track it and this test should see it"


def test_covalent_entries_are_KEPT_because_this_module_runs_no_dock():
    """`R2b` excludes covalent ligands from a DOCKING panel — a non-covalent dock cannot reproduce a
    covalent pose. This module asks only WHERE the ligand sits, which crystallography answered either way.
    ⛔ It matters concretely: all three NR4A2 entries are covalent, so applying R2b here would leave
    NR4A3's CLOSEST paralogue with no correction at all, for a reason that does not apply to it."""
    entries = P.in_regime_holo_entries()
    nr4a2 = entries["P43354"]["entries"]
    assert len(nr4a2) == 3 and all(e["covalent"] for e in nr4a2)
    src = inspect.getsource(P.in_regime_holo_entries)
    assert "R2b" in src and "runs no dock" in src


def test_both_paralogues_are_read_and_the_loop_records_each_one():
    """⚠ REGRESSION GUARD. `doc["paralogues"][acc] = row` was first written OUTSIDE the per-paralogue
    loop, so only the last accession would have landed and NR4A1 — 11 of the 14 entries — would have
    vanished from the artifact without any refusal explaining it."""
    entries = P.in_regime_holo_entries()
    assert set(entries) == {"P22736", "P43354"}
    src = inspect.getsource(P.run)
    loop = src.index("for acc, info in sorted(by_acc.items()):")
    tail = src.index('doc["summary"] = _summary(doc)')
    assigns = src[loop:tail]
    for line in assigns.splitlines():
        if 'doc["paralogues"][acc] = row' in line:
            assert line.startswith(" " * 8), "the record must be INSIDE the per-paralogue loop: %r" % line


def test_a_paralogue_with_no_usable_ligand_is_REFUSED_not_defaulted():
    """CLAUDE.md §4: an absent reading is not a reading of absence. A paralogue we could not measure must
    never render as one whose box was found to be fine."""
    doc = {"paralogues": {"P22736": {"refusals": [{"stage": "fetch_af2", "evidence": "boom"}]}}}
    s = P._summary(doc)
    assert s["measured"] is False
    assert "UNMEASURED" in s["_reads"] and "not 'the box is fine'" in s["_reads"]


def test_containment_uses_the_box_HALF_EDGE_on_every_axis():
    """A 24 Å box reaches 12 Å from its centre per axis, not 24. Getting this wrong would call a site
    contained when it is a box-width away — the exact error the module exists to detect."""
    src = inspect.getsource(P.run)
    assert "half = edge / 2.0" in src
    assert "abs(box[\"center\"][i] - c[i]) <= half for i in range(3)" in src


def test_the_summary_reports_displacement_and_refuses_to_license_a_selectivity_claim():
    doc = {"paralogues": {
        "P22736": {"corrected_site": {"center": [0.0, 0.0, 0.0]},
                   "displacement": {"pipeline_box_center_to_crystallographic_site_A": 18.4,
                                    "crystallographic_site_inside_the_pipeline_box": False}},
        "P43354": {"corrected_site": {"center": [1.0, 1.0, 1.0]},
                   "displacement": {"pipeline_box_center_to_crystallographic_site_A": 3.2,
                                    "crystallographic_site_inside_the_pipeline_box": True}}}}
    s = P._summary(doc)
    assert s["measured"] is True and s["n_paralogues_measured"] == 2
    assert s["displacement_A"] == {"min": 3.2, "max": 18.4}
    assert s["n_with_the_crystallographic_site_OUTSIDE_the_pipeline_box"] == 1
    assert s["paralogues_docked_outside_their_own_ligand_site"] == ["P22736"]
    assert set(s["corrected_sites"]) == {"P22736", "P43354"}
    # the boundary that must travel with the corrected site
    assert "RECOMPUTED at the corrected site" in s["_does_not_license"]
    assert "3.147" in s["_does_not_license"], "the pose-resolution bound must travel with the correction"


def test_it_rescores_nothing():
    """⛔ SCOPE. This emits a site and a displacement. It must not touch a score, a ΔΔG or a verdict —
    a module that both re-picks the site AND re-scores would make the two impossible to review separately.

    ⚠ TESTED AS BEHAVIOUR, NOT AS VOCABULARY (rewritten 2026-08-03). The first version grepped the whole
    module source for "abfe"/"affinity"/"ddG" and failed on its own DOCSTRING, which cites the ABFE margin
    to explain what the defect does to it. Banning a word from the prose is not the rule; the rule is that
    no code path computes or writes a score. So: walk the AST of the executable body, and check the emitted
    document's keys."""
    import ast
    tree = ast.parse(inspect.getsource(P))
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            called.add(getattr(f, "attr", None) or getattr(f, "id", None))
    for forbidden in ("dock_into", "run_mmgbsa", "score", "rescore", "make_sdf", "submit"):
        assert forbidden not in called, "%s() is called — this module must not re-score" % forbidden

    doc = {"paralogues": {"P22736": {
        "corrected_site": {"center": [0.0, 0.0, 0.0]},
        "displacement": {"pipeline_box_center_to_crystallographic_site_A": 18.4,
                         "crystallographic_site_inside_the_pipeline_box": False}}}}
    # ⚠ DATA FIELDS ONLY. This repo's convention is that `_`-prefixed keys are PROSE, and the summary's
    # prose necessarily contains "re-score" — it is the disclaimer. Grepping it was the same
    # vocabulary-vs-behaviour mistake one layer down, so the assertion is scoped to what the artifact
    # actually reports.
    summary = P._summary(doc)
    data = {k: v for k, v in summary.items() if not k.startswith("_")}
    blob = json.dumps(data).lower()
    for forbidden in ("kcal", "affinity", "ddg", "score"):
        assert forbidden not in blob, "the summary DATA emits %r — it must carry geometry only" % forbidden
    assert set(data) <= {"measured", "n_paralogues_measured", "displacement_A",
                         "n_with_the_crystallographic_site_OUTSIDE_the_pipeline_box",
                         "paralogues_docked_outside_their_own_ligand_site", "corrected_sites"}
    assert "RE-SCORES NOTHING" in P.__doc__


def test_nr4a3s_own_site_is_explicitly_out_of_scope():
    """NR4A3's box is built directly on NR4A3, NOT by `map_pocket_to_paralogue`. Correcting it here would
    be changing a thing this evidence says nothing about."""
    src = inspect.getsource(P.run)
    assert "nr4a3_site_untouched" in src
    assert "not what this corrects" in src


def test_the_crystallographic_transfer_is_structure_based_not_sequence_based():
    """⛔ THE DEFECT BEING MEASURED IS A BLOSUM62 RESIDUE MAPPING. Validating it with another sequence
    alignment could inherit the same error and agree with it. CE reads no sequence at all."""
    src = inspect.getsource(P.crystal_site_in_af2_frame)
    assert "CEAligner" in src
    assert "cannot inherit" in inspect.getsource(P) or "could inherit the same error" in src


# ============================== the agreement gate, and the wrong answer that created it

def test_the_agreement_gate_refuses_the_first_runs_real_data():
    """★★ THE REGRESSION FIXTURE IS THE ACTUAL WRONG ANSWER (2026-08-03, CI run 30850991002).

    The first run emitted a corrected site for BOTH paralogues and a clean displacement — 22.814 A and
    24.656 A, both "outside the pipeline's box" — from ligand positions scattered 8.8-26.8 A (NR4A1) and
    28.6-55.2 A (NR4A2) around their own consensus. A centroid of a cloud that wide is a point where no
    ligand is, so the displacement was measured against a fiction.

    ⛔ The agreement data was ALREADY IN THE ARTIFACT (`spread_from_consensus`) and the summary did not
    read it. That is the same failure shape as `regime_dock`'s first headline: evidence emitted, conclusion
    ignoring it. These are the real numbers; the gate must refuse both."""
    nr4a1 = [8.821, 11.969, 13.709, 17.227, 22.722, 22.788, 23.139, 25.401, 26.517, 26.529, 26.783]
    nr4a2 = [28.602, 41.782, 55.249]
    assert max(nr4a1) > P.AGREEMENT_MAX_SPREAD_A, "NR4A1's real spread must fail the gate"
    assert max(nr4a2) > P.AGREEMENT_MAX_SPREAD_A, "NR4A2's real spread must fail the gate"
    # and the threshold is the pipeline's own box half-edge, not a number chosen to make this pass
    assert P.AGREEMENT_MAX_SPREAD_A == P.BOX_EDGE_A / 2.0


def test_a_refused_paralogue_emits_no_site_and_no_displacement():
    """A refusal must remove the CONCLUSION, not just annotate it. A corrected site left beside a failed
    agreement check is a number someone will quote."""
    src = inspect.getsource(P.run)
    i = src.index("if not agrees:")
    blk = src[i:i + 1200]
    assert 'row["corrected_site"] = None' in blk
    assert "no displacement is computed" in blk
    assert "UNMEASURED, not evidence that the pipeline's box is right" in blk
    # and the refusal must point at the mechanism, not just say "wide"
    assert "reference_af2_span" in blk and "ALIGNMENT symptom" in blk


def test_the_reference_is_bounded_to_the_domain_the_crystal_covers():
    """⛔ THE CAUSE OF THE WRONG ANSWER. AlphaFold serves the FULL-LENGTH protein (NR4A1 is 598 aa, mostly
    a disordered AF1 arm); every deposit is an LBD-only construct of ~250 aa. CE placed a 250-residue
    domain inside that at CE RMS 0.7-1.6 A and in the WRONG REGISTER for some entries — putting `4WHF` and
    `4WHG`, consecutive depositions from ONE paper, 48 A apart in the same protein."""
    src = inspect.getsource(P.crystal_site_in_af2_frame)
    assert "TRIM THE REFERENCE, NEVER THE MOBILE STRUCTURE" in src
    assert "reference_af2_span" in src, "the span must be recorded — CE RMS alone cannot show a register error"
    run_src = inspect.getsource(P.run)
    assert "af2_domain_span(holo_path, para_pdb)" in run_src
    assert "span=(lo, hi)" in run_src


def test_the_span_helper_refuses_an_implausible_self_identity():
    """A deposit and the model of the SAME accession must align near-exactly. Anything low is a
    chain-selection or wrong-file symptom, and aligning onto the wrong region is precisely the failure
    this helper exists to stop — so it refuses rather than proceeding."""
    src = inspect.getsource(P.af2_domain_span)
    assert "frac < 0.9" in src
    assert "SAME accession" in src and "refusing rather than aligning onto the wrong region" in src


def test_using_a_sequence_alignment_here_is_justified_not_an_oversight():
    """The module forbids a sequence alignment for the CROSS-PROTEIN transfer, because that inference is
    what is under test. `af2_domain_span` aligns the SAME protein against itself, only to bound the
    reference — the placement stays CE's. The distinction must be written down, or a later reader will
    'fix' it back."""
    src = inspect.getsource(P.af2_domain_span)
    assert "NOT A CONTRADICTION OF THE MODULE'S OWN RULE" in src
    assert "SAME protein against itself" in src


def test_only_the_chain_the_ligand_touches_is_aligned():
    """★★ THE ACTUAL CAUSE OF THE SCATTER, and it is NOT the register error the domain trim was built for.

    ⛔ WHAT KILLED THE REGISTER HYPOTHESIS: bounding the reference to the LBD (361-598, aligned identity
    0.987-1.000, CE RMS 0.7-1.2 A) changed the NR4A1 ligand positions by NOTHING — identical coordinates.
    CE had been landing on the LBD all along.

    ⭑ WHAT THE NUMBER SAYS INSTEAD: the separation is bimodal at ~49 A and a nuclear-receptor LBD is only
    ~40 A across, so two ligands 49 A apart cannot both sit on one monomer — they are on different chains
    of a crystallographic dimer. `ligand_hetatms` picks the largest ligand COPY while CE aligned the WHOLE
    deposit, so whenever that copy sat on the chain CE did not superpose, the ligand landed a subunit away.

    ⚠ The helper for this already existed and was TESTED — `apo_pose_recovery._chain_nearest`, documented
    as "the chain the ligand actually binds", used by that module's own benchmark, which is why its site
    arm worked while this one's did not. Bypassing it was the defect."""
    src = inspect.getsource(P.crystal_site_in_af2_frame)
    assert "_chain_nearest(holo_txt, lig" in src, "the ligand's own chain must select the alignment target"
    assert "protein_only(holo_txt, chain)" in src
    assert "holo_chain_the_ligand_touches" in src, "the chain must be recorded, or this stays invisible"
    # the refusal path: a ligand touching no chain is refused, not aligned against an arbitrary one
    assert "no protein chain within 6.0 A" in src


def test_the_register_hypothesis_is_recorded_as_REFUTED_not_quietly_dropped():
    """The domain trim stays — it is correct and cheap — but the artifact and the code must not imply it
    was the fix. A superseded diagnosis left looking live is how a wrong mechanism gets re-cited."""
    src = inspect.getsource(P.crystal_site_in_af2_frame)
    assert "changed the NR4A1 ligand positions by NOTHING" in src
    assert "the register was never wrong" in inspect.getsource(P.af2_domain_span) or \
           "not the register error" in src
