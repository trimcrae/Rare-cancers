"""`lint_asymmetry` must go RED on the 2026-08-07 defect and stay GREEN on honest prose.

⛔ WHY EVERY TEST HERE MUTATES A CORPUS RATHER THAN ASSERTING A CLEAN TREE. A guard that fails OPEN
and a guard that is genuinely satisfied render identically. So each test builds a corpus, puts a real
sentence in it — most of them lifted verbatim from the `Superseded, retained` notes the 2026-08-07
sweep left behind, which are the defect's own preserved evidence — and asserts the guard names it.

⛔ AND EVERY CORPUS IS A `tmp_path` TREE, NEVER THE WORKING TREE. `lint_asymmetry.check()` takes its
root for exactly this reason. `research-loop` §3 added that rule on 2026-08-27, after a mutation
window in the SHARED tree let 13 inverted claims reach origin/main.

★ THE ONE TEST THAT IS NOT A UNIT TEST is `test_the_gate_is_green_on_the_committed_tree`: the guard
is meant to sit in the commit loop, and a guard that is red on a clean checkout gets switched off,
taking the case it exists for with it (CLAUDE.md §6).
"""
import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


la = _load("lint_asymmetry")


_CORPUS_N = [0]


def corpus(tmp_path, text, name="research/manuscripts/probe.md"):
    """Write one document into a throwaway tree of its own and return the findings over it.

    ⚠ A FRESH SUBTREE PER CALL, not a fresh file in one tree: two calls in one test otherwise scan
    each other's fixtures and the second assertion counts findings from the first. Measured, in this
    file, on the first run."""
    _CORPUS_N[0] += 1
    root = tmp_path / f"c{_CORPUS_N[0]}"
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return la.check(str(root))


def rules(findings):
    return sorted({f.rule for f in findings})


# --------------------------------------------------------------------------------------------
# one test per finding class — each fixture is a real pre-2026-08-07 sentence
# --------------------------------------------------------------------------------------------

def test_the_requirement_register_class_is_caught(tmp_path):
    """The commonest shape: a deontic verb over the pair. Verbatim from the pre-sweep
    `nr4a3-degrader-broader-indications.md`, preserved today in that file's retained note."""
    found = corpus(tmp_path, (
        "**Purpose (manuscript motivation section).** EMC is ultra-rare, which weakens the\n"
        "commercial case for *making* the molecule. The degrader we design **must be\n"
        "NR4A3-selective** — it has to spare NR4A1 and NR4A2 to avoid their on-target toxicities.\n"
    ))
    assert len(found) == 1, found
    assert found[0].rule == "requirement-register"


def test_the_adjectival_design_compound_class_is_caught(tmp_path):
    """No deontic word anywhere — the compound IS the specification. This is the paper's own §2.4
    heading as it read before the sweep, and it is the site the ledger row calls 'the paper heading'."""
    found = corpus(tmp_path, (
        "### 2.4 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead\n"
    ))
    assert [f.rule for f in found] == ["adjectival-design-compound"], found


def test_the_adjectival_compound_is_caught_across_the_line_wrap(tmp_path):
    """⚠ REGRESSION. The outreach email wraps between the compound and its noun, and a
    newline-excluding window missed it — one of the 16 sites, invisible for one iteration."""
    found = corpus(tmp_path, (
        "I designed a predicted NR4A3-selective (NR4A1/2-sparing)\n"
        "binder as a degrader warhead starting point.\n"
    ))
    assert [f.rule for f in found] == ["adjectival-design-compound"], found


def test_the_criteria_list_class_is_caught(tmp_path):
    """An advancement bar carries its register in the sentence ABOVE it. Verbatim from
    `nr4a3-ensemble-redesign-brief.md`, whose item 4 the sweep rewrote."""
    found = corpus(tmp_path, (
        'The desired outcome is not "another high-scoring molecule." It is a candidate for which:\n'
        "\n"
        "1. the same mapped orthosteric pocket is present under a corrected method;\n"
        "4. matched NR4A1 and NR4A2 conformers do not provide strong counterexamples;\n"
        "5. receptor preference is larger than conformer sensitivity;\n"
    ))
    assert [f.rule for f in found] == ["criteria-list-item"], found


def test_the_same_list_item_without_its_lead_in_is_not_a_finding(tmp_path):
    """⛔ The lead-in is what supplies the register. Without it the sentence is a report, and a guard
    that fired anyway would be matching on `counterexample` alone — which was tried, and returned
    three false positives inside a retired scoring formula."""
    found = corpus(tmp_path, (
        "Observed across the run:\n"
        "\n"
        "4. matched NR4A1 and NR4A2 conformers do not provide strong counterexamples;\n"
    ))
    assert found == [], found


def test_the_graph_record_class_is_caught_in_json(tmp_path):
    """`systems/graph/routes.json` -> RT-DEGRADER's `purpose`, exactly as it read before the sweep."""
    found = corpus(tmp_path, (
        '{"routes": [{"id": "RT-DEGRADER", "purpose": "Can a bifunctional molecule recruit an E3'
        ' ligase to NR4A3 and degrade it selectively over NR4A1 and NR4A2?"}]}'
    ), name="systems/graph/routes.json")
    assert len(found) == 1, found
    assert "selectively over NR4A1 and NR4A2" in found[0].sentence


def test_a_module_docstring_is_scanned_and_its_code_is_not(tmp_path):
    """Two of the 16 sites were module docstrings. ⛔ Code is deliberately not scanned: a dict key
    naming both paralogues is an identifier, not a statement about the requirement."""
    found = corpus(tmp_path, (
        '"""Selectivity scaffold for the NR4A3 degrader warhead.\n'
        "\n"
        'A warhead must bind NR4A3 but NOT the homologous NR4A1/NR4A2 LBDs.\n'
        '"""\n'
        'PAIR = {"NR4A1/NR4A2": "must spare both"}\n'
    ), name="research/modalities/probe_module.py")
    assert len(found) == 1, found
    assert "must bind NR4A3" in found[0].sentence


# --------------------------------------------------------------------------------------------
# the four things that must NOT fire — each is a real, correct sentence
# --------------------------------------------------------------------------------------------

def test_a_symmetric_measurement_is_left_alone(tmp_path):
    """⭐ THE RULE THAT DOES THE WORK. A reading taken over both paralogues is RIGHT to be symmetric;
    only a BAR stated over both is the defect. Without rule 3 this guard fires on roughly one line in
    five of the modalities corpus."""
    found = corpus(tmp_path, (
        "**Figure 4.** One candidate library docked into the metadynamics-opened NR4A3, NR4A1 and\n"
        "NR4A2 pockets, giving each candidate a per-paralogue selectivity fingerprint.\n"
        "\n"
        "At three Pocket-5 positions NR4A3's residue is paralogue-unique and NR4A1 and NR4A2 both\n"
        "carry a strictly bulkier side chain.\n"
    ))
    assert found == [], found


def test_a_block_that_carries_the_asymmetry_is_exempt(tmp_path):
    """The corrected form of the defect names the pair in one clause and its two weights in the
    next, so rule 4's window is the BLOCK. This is the fixed `emc-treatment-roadmap.md` paragraph."""
    found = corpus(tmp_path, (
        "A LBD warhead could hit the paralogues NR4A1/NR4A2 — but ⚠ **those two are not one\n"
        "constraint.** Sparing **NR4A1 is the HARD half**. Sparing **NR4A2 is the SOFT half**,\n"
        "best-effort. So the design target is **NR4A3-selective — NR4A1-sparing mandatory,\n"
        "NR4A2-sparing best-effort**.\n"
    ))
    assert found == [], found


def test_a_superseded_retained_quotation_is_exempt(tmp_path):
    """⛔ NON-NEGOTIABLE. CLAUDE.md rule 1.2 requires a correction to REGISTER the text it replaced,
    and the sweep left all 16 superseded phrasings inline as the evidence of its own work. A guard
    that fires on those makes the honest correction pattern the expensive one."""
    found = corpus(tmp_path, (
        "The design target is stated asymmetrically and its evidence is in §2.4; the hard half is\n"
        "NR4A1 and the soft half is NR4A2.\n"
        "\n"
        '⚠ *Superseded, retained: "the design target is **NR4A3-selective, NR4A1/2-sparing**",\n'
        "which stated one bar over both paralogues.*\n"
    ))
    assert found == [], found


def test_the_pan_nr4a_triple_is_not_the_pair(tmp_path):
    """`NR4A1/2/3` is the CAR-T pan-NR4A mode — the opposite requirement. Measured: without the
    trailing negative lookahead it produced two false positives in the indication stack."""
    found = corpus(tmp_path, (
        "NR4A1/2/3 drive CD8⁺ T-cell exhaustion, and the effect is complementary across all three.\n"
        "This needs a pan-NR4A degrader that must spare nothing — the opposite of the EMC\n"
        "requirement — avoiding the systemic AML risk only by staying ex vivo.\n"
    ))
    assert found == [], found


def test_the_anti_target_genotype_is_not_the_pair(tmp_path):
    """`NR4A1 + NR4A3` is the combination genotype that makes NR4A1-sparing MANDATORY. A guard that
    read it as the paralogue pair would fire on the evidence for the asymmetry itself."""
    found = corpus(tmp_path, (
        "A degrader must spare NR4A1: **NR4A1 + NR4A3 lost together** → acute myeloid leukaemia in\n"
        "mice (Mullican 2007), and that is precisely the pair a non-selective degrader reconstitutes.\n"
    ))
    assert found == [], found


# --------------------------------------------------------------------------------------------
# ⭐⭐ the heading rule — the sweep's own root-cause finding, made mechanical
# --------------------------------------------------------------------------------------------

def test_a_heading_gets_no_exemption_from_the_paragraph_under_it(tmp_path):
    """★★ THE MOST IMPORTANT BEHAVIOUR IN THIS GUARD, and it is the 2026-08-07 commit's own root
    cause: the §2.4 row was TITLED 'NR4A2 — UNBOUNDED, in both directions' while the cell beside it
    said BOUNDED, and every downstream register copied the TITLE, *because a heading is what gets
    quoted*. So a symmetric heading is a finding even when the paragraph below it is correct.

    ⚠ This is not hypothetical: gluing headings to their bodies hid a LIVE symmetric heading in
    `degrader/nr4a3-degrader-broader-indications.md` that the hand sweep had also missed."""
    body_is_correct = (
        "The requirement is asymmetric: NR4A1-sparing is the HARD half and NR4A2-sparing the SOFT,\n"
        "best-effort half (§2.4).\n"
    )
    found = corpus(tmp_path, (
        "## Framing: the indication must want NR4A3 *down* AND NR4A1/2 *spared*\n"
        + body_is_correct
    ))
    assert len(found) == 1, found
    assert found[0].sentence.startswith("## Framing"), found[0].sentence

    # and the same paragraph, with no heading over it, is correctly silent
    assert corpus(tmp_path, body_is_correct, name="research/manuscripts/probe2.md") == []


def test_a_body_block_does_inherit_its_heading(tmp_path):
    """The converse, and it is what keeps §2.4 itself out of the report: prose UNDER a heading that
    declares the asymmetry is discussing it, not restating it symmetrically."""
    found = corpus(tmp_path, (
        "### 2.4 · The selectivity requirement is ASYMMETRIC — and this page stated it symmetrically\n"
        "\n"
        "`R7`, `R11` and `R12` all read *\"selective over NR4A1/NR4A2\"*, one requirement with two\n"
        "comparators. The biology does not say that, and the design target must change.\n"
    ))
    assert found == [], found


# --------------------------------------------------------------------------------------------
# the baseline
# --------------------------------------------------------------------------------------------

def test_a_baselined_sentence_is_not_a_new_finding_and_editing_it_makes_one(tmp_path):
    """⛔ THE AMNESTY IS KEYED ON THE SENTENCE'S OWN DIGEST. Reword the sentence and the row stops
    covering it — which is the only property that stops a baseline becoming a landfill."""
    live = "These all want NR4A3 removed and NR4A1/2 spared — the *same* molecule we design for EMC.\n"
    found = corpus(tmp_path, live)
    assert len(found) == 1 and found[0].baseline is not None, found
    assert found[0].baseline["verdict"] == "open-defect"

    edited = live.replace("These all want", "These indications all want")
    found2 = corpus(tmp_path, edited, name="research/manuscripts/probe3.md")
    assert len(found2) == 1 and found2[0].baseline is None, found2


def test_every_baseline_row_still_matches_something_in_the_tree():
    """⚠ A BASELINE ROW THAT MATCHES NOTHING IS AN AMNESTY FOR A SENTENCE THAT NO LONGER EXISTS — it
    silently pre-approves whatever future prose happens to hash to it, and it hides the good news
    that a defect was fixed. Retire the row instead."""
    live = {la.baseline_key(f.sentence) for f in la.check(ROOT)}
    stale = sorted(set(la.BASELINE) - live)
    assert not stale, (
        "these BASELINE rows no longer match any sentence — delete them:\n  "
        + "\n  ".join(f"{k}  ({la.BASELINE[k]['where']})" for k in stale))


def test_the_open_defects_are_reported_and_not_merely_recorded():
    """A baselined defect that prints nothing has been deleted, not deferred."""
    open_rows = [k for k, v in la.BASELINE.items() if v["verdict"] == "open-defect"]
    assert open_rows, "if there are no open defects the baseline should say so by being empty"
    for k in open_rows:
        assert la.BASELINE[k]["where"], "an open row must name where it is"
        assert la.BASELINE[k]["first_seen"], "an open row must carry the date it was found"


# --------------------------------------------------------------------------------------------
# the gate contract
# --------------------------------------------------------------------------------------------

@pytest.mark.committed_artifact
def test_the_gate_is_green_on_the_committed_tree():
    """⛔ A guard that is red on a clean checkout gets switched off, taking the case it exists for
    with it. New findings must be zero; the known-open rows print but do not fail."""
    new = [f for f in la.check(ROOT) if f.baseline is None]
    assert new == [], "\n".join(f"{f.path}:{f.line}  {f.sentence[:160]}" for f in new)


@pytest.mark.committed_artifact
def test_strict_mode_still_fails_while_an_open_defect_stands():
    """The other half: `--strict` is what the person fixing the prose runs, and it must not be green
    while a known symmetric restatement is still in a manuscript."""
    assert la.main(["--strict", "--report"]) == 0        # --report never fails
    assert la.main(["--strict"]) == 1


def test_the_known_holes_are_written_down():
    """CLAUDE.md §4: an honest UNKNOWN costs nothing; a hole nobody wrote down costs the route."""
    assert len(la.NOT_BOUND) >= 5
    for name, why in la.NOT_BOUND:
        assert name and len(why) > 60, name
