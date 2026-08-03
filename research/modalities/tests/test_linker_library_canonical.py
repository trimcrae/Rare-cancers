#!/usr/bin/env python3
"""
THE CHEAP HALF OF THE ANTI-DRIFT GUARD for the canonical-linker-library ruling (roadmap §10.1 row 25).

⛔ WHAT WENT WRONG, AND WHY A HASH WOULD NOT HAVE CAUGHT IT. `nr4a3-linker-design.json` silently stopped
reproducing from its own generator when a shared geometry kernel was corrected (`382c36947`). The ARTIFACT
never changed — the CODE did — so nothing that watches the artifact alone can see it. These tests therefore
pin the RELATIONSHIPS the program actually depends on: the executed enumeration, the design → library-chem →
rung-5b-T chain, `V16`'s executed molecules, and the release predicate that discharged the hold on `5b-T`.

The expensive half — re-running the generator and refusing a THIRD enumeration — is
`test_linker_library_reproduces.py`, kept separate so this module stays in the fast suite.

Nothing here is typed: every figure is read from the ruling artifact or from the libraries themselves.
"""

import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(MOD, "..", ".."))

RULING = os.path.join(MOD, "nr4a3-linker-library-canonical.json")
DESIGN = os.path.join(MOD, "nr4a3-linker-design.json")
CHEM = os.path.join(MOD, "nr4a3-linker-library-chem.json")
PREP = os.path.join(MOD, "nr4a3-5aks-cofold-prep.json")
ROADMAP = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")

LIB_KEYS = ("virtual_library_at_the_term_a_exemplar", "virtual_library_at_representative_geometry")


def _load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def ruling():
    assert os.path.exists(RULING), (
        "the canonical-library ruling artifact is missing. Regenerate it with "
        "`python3 research/modalities/nr4a3_linker_library_canonical.py --check`. Without it the program has "
        "no record of which linker enumeration is canonical, which is the exact state row 25 was opened for.")
    return _load(RULING)


@pytest.fixture(scope="module")
def design():
    return _load(DESIGN)


def _ids(doc):
    out = {}
    for k in LIB_KEYS:
        for x in doc[k]:
            out[x["construct_id"]] = x
    return out


# =============================================================================================================
# 1 · The EXECUTED enumeration is what the ruling says it is
# =============================================================================================================

def test_the_committed_artifact_still_is_the_registered_executed_enumeration(ruling, design):
    """A hand edit to nr4a3-linker-design.json is a rewrite of a preregistered enumeration. Refuse it."""
    reg = ruling["registered_enumerations"]["EXECUTED"]
    got = set(_ids(design))
    want_n = reg["n_constructs"]
    assert len(got) == want_n, (
        "the committed linker library no longer holds the registered EXECUTED construct count "
        "(%d, now %d). That artifact is FROZEN as the record of what `V16` was measured on and what rung "
        "`5b-T` draws its degrader from; changing it in place rewrites a preregistration. Revert it, or rule "
        "again and re-register in the same commit." % (want_n, len(got)))
    assert design["library_summary"]["n_enumerated"] == reg["n_enumerated"]
    for k in LIB_KEYS:
        assert len(design[k]) == reg["by_placement"][k]


def test_the_constructs_unique_to_each_enumeration_are_registered(ruling, design):
    """The whole difference between the two libraries is these two lists. Keep them true."""
    reg = ruling["registered_enumerations"]
    ids = set(_ids(design))
    for cid in reg["EXECUTED"]["only_in_this_set"]:
        assert cid in ids, "%s is registered as executed-only but is not in the committed library" % cid
    for cid in reg["CORRECTED"]["only_in_this_set"]:
        assert cid not in ids, (
            "%s is registered as belonging ONLY to the corrected enumeration, but it is in the committed "
            "library. Either the committed artifact was regenerated (which the ruling forbids) or the "
            "registration is stale." % cid)


def test_no_shared_construct_ever_changed_chemistry(ruling):
    """The correction moved which constructs are RETAINED, never what a retained construct IS."""
    shared = ruling["registered_enumerations"]["shared"]
    assert shared["n_with_a_changed_smiles"] == 0, (
        "a construct present in BOTH enumerations has a different SMILES in each: %s. That would mean the "
        "kernel correction changed a molecule rather than a selection, and every committed SMILES downstream "
        "would need re-checking." % shared["changed_smiles"])


# =============================================================================================================
# 2 · The design -> library-chem -> rung 5b-T chain
# =============================================================================================================

def test_library_chem_is_the_committed_design_and_not_something_else(design):
    """rung 5b-T's degrader source is derived from the design library. If they diverge, 5b-T is unsourced."""
    chem = _load(CHEM)
    chem_ids = {x["construct_id"] for x in chem["constructs"]}
    design_ids = set(_ids(design))
    assert chem_ids == design_ids, (
        "nr4a3-linker-library-chem.json and nr4a3-linker-design.json no longer describe the same "
        "enumeration (chem-only %s, design-only %s). `ternary_rebuild_cost.DEGRADER_SOURCE` says rung 5b-T "
        "takes its degrader from the chem file 'and from nowhere else', so a divergence here means that rung "
        "is drawing a molecule from an enumeration nobody ruled on."
        % (sorted(chem_ids - design_ids), sorted(design_ids - chem_ids)))
    assert chem["n_constructs"] == len(design_ids)


def test_the_5bT_release_predicate_still_holds(ruling):
    """This is the predicate that discharged row 25's hold on rung 5b-T. If it stops holding, so does that."""
    rel = ruling["release_condition"]
    assert rel["⛔_the_standing_condition"].startswith("`5b-T` must not run until this is settled"), (
        "the standing condition has been reworded. It is quoted verbatim on purpose — the roadmap row and "
        "this artifact must carry the same sentence.")
    bad = [k for k, v in rel["predicates_a_reader_can_re_check"].items() if v is not True]
    assert not bad, (
        "the rung-5b-T release predicate no longer holds: %s. The hold on 5b-T was discharged BECAUSE that "
        "rung is invariant to which enumeration is canonical; if any of these goes false, the rung's inputs "
        "have moved and the hold is live again." % bad)


def test_every_5bT_candidate_is_present_in_both_enumerations_with_one_smiles(ruling):
    rows = ruling["release_condition"]["candidates"]
    assert rows, "the rung-5b-T candidate list is empty — it is read from ternary_rebuild_cost.DEGRADER_SOURCE"
    for r in rows:
        assert r["in_executed"] and r["in_corrected"] and r["in_library_chem"], r
        assert r["smiles_identical_across_both"], (
            "%s has a different SMILES in the executed and corrected enumerations. Rung 5b-T would then be "
            "running a molecule whose identity depends on which kernel built the library." % r["construct_id"])


# =============================================================================================================
# 3 · V16 — the causal test article must stay recoverable
# =============================================================================================================

def test_V16s_executed_molecules_are_still_recorded_verbatim(ruling):
    """The 5a-KS endpoints must resolve to committed constructs, or the landed result is unreproducible."""
    v16 = ruling["V16_the_causal_test_article"]
    assert v16["all_present_in_the_committed_library"], (
        "an endpoint SMILES in nr4a3-5aks-cofold-prep.json no longer matches any construct in the committed "
        "library. That is the unregenerable-artifact failure mode: a landed measurement whose input molecule "
        "cannot be tied to any enumeration.")
    assert len(v16["resolved_to_construct_ids"]) == 2


def test_the_prep_file_endpoints_match_the_committed_library_byte_for_byte(design):
    """Read straight from the two files — the ruling artifact is not trusted to stand in for them."""
    prep = _load(PREP)
    committed = {x.get("smiles") for x in _ids(design).values()}
    for leg in prep["plan"]:
        for field in ("cofold_ligand_smiles", "perturbed_endpoint_smiles"):
            assert leg[field] in committed, (
                "%s of leg %s is not a committed construct SMILES" % (field, leg["leg_id"]))


# =============================================================================================================
# 4 · The ruling itself must stay honest about what it froze and what it did not
# =============================================================================================================

def test_the_ruling_names_the_cause_and_the_commit_that_caused_it(ruling):
    c = ruling["cause"]
    for k in ("commit", "parent", "file", "symbol", "which_is_right", "direction_of_the_error"):
        assert c.get(k), "the ruling's cause block is missing %r" % k
    assert "conservative" in c["direction_of_the_error"].lower(), (
        "the direction of the kernel error is the reason the committed library is safe to keep using. It "
        "must stay in the artifact, not be summarised away.")


def test_the_other_stale_consumer_of_the_same_kernel_is_still_named(ruling):
    """`nr4a3-orientation-basins.json` is the second artifact built on the pre-fix kernel and is NOT settled.

    Deleting this note would make an open item look closed, which is the failure the roadmap exists to stop.
    """
    blob = json.dumps(ruling, ensure_ascii=False)
    assert "nr4a3-orientation-basins.json" in blob and "term_a_feasibility_envelope" in blob, (
        "the ruling no longer names the OTHER artifact built on the pre-fix geometry kernel. That one is "
        "still unregistered and settling this one does not settle it.")


# =============================================================================================================
# 5 · The map edits must never ship with a dead anchor
# =============================================================================================================

def test_every_emitted_map_edit_anchor_is_present_in_the_live_roadmap(ruling):
    """A previous audit emitted nine verbatim edits and all nine failed to apply, because the documents moved
    underneath them. The anchors are therefore machine-checked, here and at generation time."""
    with open(ROADMAP, encoding="utf-8") as fh:
        text = fh.read()
    dead, ambiguous = [], []
    for e in ruling["map_edits_required"]["edits"]:
        ct = e.get("current_text")
        if ct is None:
            assert e.get("where_it_goes"), (
                "edit %r has anchor: null but does not say where it goes. An unanchored edit must describe "
                "its home or it is unroutable." % e["id"])
            continue
        n = text.count(ct)
        if n == 0:
            dead.append(e["id"])
        elif n > 1:
            ambiguous.append((e["id"], n))
    assert not dead, (
        "map edits with anchors that are NOT in the live roadmap: %s. Relocate them and regenerate — a dead "
        "anchor applies to nothing and reads as done." % dead)
    assert not ambiguous, (
        "map edits whose anchor matches more than once, so it cannot say which occurrence to change: %s"
        % ambiguous)


def test_every_map_edit_carries_the_fields_that_make_it_routable(ruling):
    for e in ruling["map_edits_required"]["edits"]:
        for f in ("id", "section", "why", "artifact", "proposed_text"):
            assert e.get(f), "map edit %r is missing %r" % (e.get("id"), f)
