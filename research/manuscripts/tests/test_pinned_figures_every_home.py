"""⛔ THE CROSS-FILE CHECK, DERIVED FROM THE REGISTRY INSTEAD OF FROM A LIST SOMEONE MAINTAINS.

`test_round6_fixes_landed.py` was the only instrument in this repository that checked a statement
across more than one file, and it did so for about fifteen hand-written strings across seven
hand-written paths. Every fact it did not happen to name was uncovered, and nothing said so — the
shrinking-scope failure `lint_claims.py` records three times over, in the file written to stop
exactly that class of defect.

So the list is derived here. Every entry in `pinned-figures.json` names an artifact, a key and the
documents that quote it; this module walks that registry and asserts each figure agrees in EVERY
home. Registering a number is now the whole of the work — no test has to be extended for the guard
to cover it.

★★ AND EVERY GUARD PROVES IT CAN FAIL. A check that cannot fail is worse than no check, because it
reports coverage it does not have. `test_every_flattened_pin_rejects_a_defective_document` takes
each entry, corrupts the digits the document prints for it, and requires the linter to reject the
result; `..._rejects_a_document_that_dropped_the_passage` deletes the sentence instead. An entry
whose pattern has drifted off the text it was written for passes the first test by accident and
fails these, which is the point.

⚠ AND THE TWO FALSE-ALARM DIRECTIONS ARE PINNED TOO. A substring guard over markdown is brittle in
BOTH directions: it has reported a protected sentence destroyed when the text merely gained italics
(`*TAF15*` against `TAF15`), and it has reported a defective sentence absent when a hard wrap moved
four words onto the next line. Neither is a change in what the paper says. The last two tests apply
each transformation to the whole document and require every pin to keep passing.
"""
import json
import os
import re
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
assert os.path.exists(os.path.join(REPO, "CLAUDE.md")), (
    f"REPO resolved to {REPO!r}, which is not the repository root -- every check below would "
    "otherwise pass by skipping"
)
sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))
import lint_consistency as lc  # noqa: E402

ART = "research/manuscripts/aso/fusion-junction-aso-research-article.md"
#: ⛔ THE CONDENSED SUBMISSION, ADDED 2026-08-22 (round 15 seat 2). The floor below named the
#: extended report and the SI and not this — so all fifteen journal-article pins could be
#: deleted and this test, whose whole job is to notice an empty registry, stayed green.
JOURNAL_ART = "research/manuscripts/aso/fusion-junction-aso-journal-article.md"
SI = "research/manuscripts/aso/fusion-junction-aso-supplementary-information.md"
MANIFEST = "research/manuscripts/aso_archive_manifest.py"

REGISTRY = lc.load_registry()
FIGURES = REGISTRY["artifact_figures"]
#: Entries matched against the flattened document. Only these can be perturbed mechanically, because
#: only these declare the digits they are checking (a capturing group) or a bounded window.
FLAT = [a for a in FIGURES if a.get("match") == "flattened"]
FLAT_CAPTURING = [a for a in FLAT if re.compile(a["context"]).groups]


def _ids(entries):
    return [a["id"] for a in entries]


def _read(rel):
    p = os.path.join(REPO, rel)
    assert os.path.exists(p), f"{rel} is missing -- check the path resolution"
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _value(a):
    doc = json.loads(_read(a["artifact"]))
    return float(lc._dig_json(doc, a["key"])) * float(a.get("scale", 1.0))


def _shown(a, value):
    return a.get("format", "${:.2f}").format(value)


def _check_one(a, rel, text):
    """Run rule A's flattened arm over `text` as if it were the file at `rel`."""
    value = _value(a)
    return lc._check_flattened(a, rel, text.split("\n"), value, _shown(a, value),
                               a.get("tolerance", 0.005))


# --------------------------------------------------------------------------------------------
# 1. Every pinned figure agrees in every home it declares.
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("entry", FIGURES, ids=_ids(FIGURES))
def test_every_pinned_figure_agrees_in_every_home(entry):
    """The registry is the list. A number registered here is checked wherever it is quoted."""
    findings = lc.check_artifact_figures({"artifact_figures": [entry]}, REPO)
    assert not findings, "\n".join(
        f"{f['file']}:{f['line']} [{f['rule']}] {f['message']}" for f in findings)


def test_the_registry_actually_covers_this_paper():
    """⛔ A REGISTRY WITH NO ENTRIES FOR THE PAPER BEING DEPOSITED IS A GREEN BUILD ABOUT NOTHING.

    On 2026-08-16 `pinned-figures.json` held one ASO entry — a SUPERSEDED coverage figure — and no
    artifact figure at all, so `lint_consistency.py` was blind to the paper next to be deposited
    while reporting zero errors across 23 files. This asserts the floor rather than a count, because
    a count would have to be updated by whoever adds the next pin and would then be the stale
    number.
    """
    homes = {rel for a in FIGURES for rel in a["must_appear_in"]}
    assert ART in homes, "the ASO research article carries no pinned figure"
    assert SI in homes, "the ASO Supporting Information carries no pinned figure"
    assert JOURNAL_ART in homes, (
        "the CONDENSED journal submission carries no pinned figure. It is the document that goes to "
        "a journal, and it restates the four counts the whole argument rests on; a registry that "
        "covers the preprint and not the submission is the 2026-08-16 defect this test was written "
        "for, one paper over.")
    assert SI in REGISTRY["targets"], (
        "the SI is not a lint_consistency target, so no superseded value is policed in it"
    )


# --------------------------------------------------------------------------------------------
# 2. Every guard proves it can fail.
# --------------------------------------------------------------------------------------------

def _corrupt(a, text):
    """Return `text` with the digits this entry checks replaced by a different number."""
    flat = lc._flat_text(text.split("\n"))
    m = re.compile(a["context"]).search(flat)
    assert m, f"{a['id']}: pattern no longer matches, so nothing can be corrupted"
    digits = m.group(1)
    # +7 on the leading integer part: never a rounding-distance change, and it survives formats
    # from "{:.0f}" to "{:.4f}".
    head = re.match(r"[\d,]+", digits).group(0)
    wrong = str(int(head.replace(",", "")) + 7) + digits[len(head):]
    return flat[:m.start(1)] + wrong + flat[m.end(1):]


@pytest.mark.parametrize("entry", FLAT_CAPTURING, ids=_ids(FLAT_CAPTURING))
def test_every_flattened_pin_rejects_a_defective_document(entry):
    """Construct the defective string and require the check to reject it."""
    rel = entry["must_appear_in"][0]
    broken = _corrupt(entry, _read(rel))
    findings = _check_one(entry, rel, broken)
    assert any(f["rule"] == "A-figure-mismatch" for f in findings), (
        f"{entry['id']}: the pinned figure was changed in the document and the check stayed "
        f"green. A guard that cannot fail is worse than no guard."
    )


@pytest.mark.parametrize("entry", FLAT, ids=_ids(FLAT))
def test_every_flattened_pin_rejects_a_document_that_dropped_the_passage(entry):
    """The other half of the round-6 question: is the statement still THERE at all?

    An absence check that only asks "does the wrong number appear" passes on a paper that deleted
    the sentence, which is how a fact stops being carried without anything going red.
    """
    rel = entry["must_appear_in"][0]
    flat = lc._flat_text(_read(rel).split("\n"))
    rx = re.compile(entry["context"])
    assert rx.search(flat), f"{entry['id']}: pattern matches nothing in {rel}"
    # ⚠ EVERY occurrence, not the first. Several entries here deliberately match the same statement
    # in more than one passage ("against 45.8% observed" appears three times), and deleting one of
    # them leaves the figure correctly stated — so a test that removed only the first would be
    # asserting that a guard fires on a document that is still right.
    findings = _check_one(entry, rel, rx.sub("", flat))
    assert any(f["rule"] == "A-figure-not-stated" for f in findings), (
        f"{entry['id']}: the passage was deleted and the check stayed green"
    )


# --------------------------------------------------------------------------------------------
# 3. The two false-alarm directions.
# --------------------------------------------------------------------------------------------

_EMPHASISABLE = re.compile(r"(?<![\w*])(NR4A3|EWSR1|TAF15|TCF12|FUS|TFG)(?![\w*])")


def test_flattening_strips_emphasis_and_keeps_identifiers_intact():
    """⛔ ONLY ASTERISKS. Underscores are load-bearing in this corpus — every junction label is
    `EWSR1_e12__NR4A3_e3` — so a flattener that stripped them would rewrite one identifier into
    another, which is a worse defect than the italics false alarm it was written to fix.
    """
    assert lc._flat_text(["a *TAF15* run", "of **190**"]) == "a TAF15 run of 190"
    assert "EWSR1_e12__NR4A3_e3" in lc._flat_text(["*EWSR1_e12__NR4A3_e3*"])


@pytest.mark.parametrize("entry", FLAT, ids=_ids(FLAT))
def test_a_pin_survives_the_text_gaining_emphasis(entry):
    """⚠ MEASURED FAILURE MODE: a guard reporting a protected sentence destroyed by italics.

    Every free-standing gene symbol in the document is wrapped in asterisks, which double-wraps the
    ones already italic (`*NR4A3*` becomes `**NR4A3**`). Nothing the paper SAYS has changed, so
    nothing may go red.
    """
    rel = entry["must_appear_in"][0]
    emphasised = _EMPHASISABLE.sub(r"*\1*", _read(rel))
    assert emphasised != _read(rel), "the transformation changed nothing, so it proves nothing"
    assert not _check_one(entry, rel, emphasised), (
        f"{entry['id']}: adding emphasis to the document made the check fail"
    )


@pytest.mark.parametrize("entry", FLAT, ids=_ids(FLAT))
def test_a_pin_survives_the_text_being_rewrapped(entry):
    """⚠ THE OTHER MEASURED FAILURE MODE: a hard wrap moving four words onto the next line.

    The whole document is re-wrapped as violently as it can be — one word per line. A line-scoped
    check finds none of its patterns; a flattened one is unaffected, which is the property these
    entries are declaring when they set `match: flattened`.
    """
    rel = entry["must_appear_in"][0]
    rewrapped = _read(rel).replace(" ", "\n")
    assert not _check_one(entry, rel, rewrapped), (
        f"{entry['id']}: re-wrapping the document made the check fail"
    )


# --------------------------------------------------------------------------------------------
# 4. Agreements between artifacts that no pattern in the registry can express.
# --------------------------------------------------------------------------------------------

def test_the_gap_pairing_panel_spans_exactly_the_atlas_in_frame_junctions():
    """The panel size and the junction count are pinned to DIFFERENT artifacts, so their agreement
    has to be asserted somewhere. The atlas emits the junctions; the mature-parent screen tiles
    designs across them. If the atlas regenerated to a different set, rule A would keep vouching for
    both numbers separately while the paper's sentence joining them ("those 38 carry 190 design
    records") became false.
    """
    atlas = json.loads(_read("research/modalities/nr4a3-fusion-junction-atlas.json"))
    gap = json.loads(_read("research/modalities/aso-parent-gap-pairing.json"))
    spanned = {r["junction"] for r in gap["per_design"]}
    assert len(spanned) == atlas["n_emittable_junctions"], (
        f"the mature-parent screen spans {len(spanned)} junctions but the atlas emits "
        f"{atlas['n_emittable_junctions']}"
    )
    assert len(gap["per_design"]) == gap["corpus"]["n_designs"]


def test_the_null_re_measures_the_screen_rather_than_copying_it():
    """`aso-parent-null.json` re-measures the observed arm through its own index, and its own
    docstring says the two agree by test. This is that test: a null whose observed arm has drifted
    from the screen it is a null FOR would move every rate in section 2.5 while both artifacts
    stayed internally consistent.
    """
    null = json.loads(_read("research/modalities/aso-parent-null.json"))
    gap = json.loads(_read("research/modalities/aso-parent-gap-pairing.json"))
    obs, corpus = null["observed"], gap["corpus"]
    assert obs["n_designs"] == corpus["n_designs"]
    assert obs["n_liable"] == corpus["n_with_parent_duplex_through_gap"]
    assert obs["n_liable_against_NR4A3"] == corpus["which_parent_supplies_it"]["NR4A3"]
    assert abs(obs["rate_liable"] - obs["n_liable"] / obs["n_designs"]) < 5e-5


def test_every_null_arm_the_artifact_carries_is_quoted_by_the_manuscript():
    """⛔ AN ARM ADDED TO THE NULL AND NOT REPORTED IS A CHOSEN NULL, WHICH IS THE DEFECT THE NULL
    EXISTS TO RULE OUT.

    Three arms were added on 2026-08-16 (`donor_terminus_chimera`, `exon_terminus_chimera`,
    `exon_terminus_chimera_novel_acceptor`) and they are the ones that retired the paper's
    half-generic/half-specific apportionment. Registering a pin per arm covers the arms someone
    remembered; this covers the arms they did not, by reading the artifact's own list.
    """
    null = json.loads(_read("research/modalities/aso-parent-null.json"))
    pinned = {a["key"].split(".")[1] for a in FIGURES
              if a["artifact"].endswith("aso-parent-null.json") and a["key"].startswith("null_ensembles.")}
    missing = sorted(set(null["null_ensembles"]) - pinned)
    assert not missing, (
        f"the null carries arm(s) no pinned figure covers: {missing}. Either the manuscript reports "
        f"them (register a pin) or it reports a subset of the arms that were run (say so)."
    )


# --------------------------------------------------------------------------------------------
# 5. The split's own structural invariant: every cross-reference resolves.
# --------------------------------------------------------------------------------------------

_SECTION_HEADING = re.compile(r"^#{1,6}\s+(S?\d+(?:\.\d+)?)\s*·", re.M)
_SECTION_REF = re.compile(r"§\s*(S?\d+(?:\.\d+)?)")


def _headings(rel):
    return set(_SECTION_HEADING.findall(_read(rel)))


@pytest.mark.parametrize("rel", [ART, SI, MANIFEST])
def test_every_section_cross_reference_resolves(rel):
    """⛔ THE DEFECT A SPLIT MANUSCRIPT PRODUCES FIRST, AND THE ONE A READER MEETS FIRST.

    The 2026-08-16 restructure moved six Methods blocks into the Supporting Information and
    renumbered the main text. A pointer left behind sends a reviewer to a section that does not
    exist, and they cannot tell whether the method was withdrawn or never written — the same
    unanswerable question a missing deposit file raises. Found this way: three `§3.8` pointers in
    `aso_archive_manifest.py`, surviving a renumber that made section 3.8 not exist.

    Numeric only: an `§S` reference resolves against the SI, a bare number against the main text.
    """
    main, si = _headings(ART), _headings(SI)
    dangling = sorted({r for r in _SECTION_REF.findall(_read(rel))
                       if r not in (si if r.startswith("S") else main)})
    assert not dangling, (
        f"{rel} points at section(s) that do not exist: "
        + ", ".join("§" + d for d in dangling)
    )


def test_the_cross_reference_check_rejects_a_dangling_pointer():
    """The guard's own proof: a reference to a section that does not exist must be caught."""
    main, si = _headings(ART), _headings(SI)
    injected = "see §9.7 and SI §S99 for the detail"
    dangling = sorted({r for r in _SECTION_REF.findall(injected)
                       if r not in (si if r.startswith("S") else main)})
    assert dangling == ["9.7", "S99"], dangling
