"""⛔⛔ THE JOURNAL ARTICLE'S NUMBERED SENTENCES THAT NO SELECTIVE INSTRUMENT READ (round 16, seat 1).

`research/manuscripts/claim_coverage.py` enumerates, for every assertive sentence, whether any
SELECTIVE committed pattern matches it. Thirteen of the article's numbered sentences matched
nothing. This file binds the mechanically checkable ones to the artifact that DECIDES each — never
to a value derived by hand, which is worse than leaving the number unbound.

★ AND TWO OF THEM WERE FILED AS "NO ARTIFACT HOME EXISTS". Both have one:

  "123 gap-paired near-matches … against eight"  → `junction-aso-offtarget-{e12n3,taf15e6n3}-deep500-b1.json`
  "seven of the 190 … leaving 47 of 183"         → the 38 orientation-filtered screens, counted

The second is worse than unbound: the derivation is already committed, in
`research/modalities/tests/test_aso_submission_numbers.py::test_censoring_counts_match_the_manuscript`,
whose `PAPER` is the EXTENDED REPORT alone. Same one-of-a-pair shape this review has closed a dozen
times, in the guard written for these exact three counts.

⚠ THE DEPTH IS PART OF THE CLAIM, NOT CONTEXT AROUND IT. At the DEFAULT ceiling the same two
reagents return 5 and 7 gap-paired near-matches — the EWSR1 one looks CLEANER, which inverts §2's
"predicted transcriptome load separates the two". So a guard that checked 123 and 8 without checking
which screen they came from would pass a sentence that had quietly swapped in the default reading.
"""
from __future__ import annotations

import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
MOD = os.path.join(REPO, "research", "modalities")

ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
TABLES = os.path.join(ASO, "fusion-junction-aso-journal-tables.md")
COVERAGE = os.path.join(ASO, "fusion-junction-aso-reagent-coverage.json")
GAP_PAIRING = os.path.join(MOD, "aso-parent-gap-pairing.json")
ATLAS = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")
PREMRNA = os.path.join(MOD, "aso-premrna-offtarget.json")
MODELS = os.path.join(MOD, "emc-model-junction-evidence.json")
COLLAPSE = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")

#: The deep re-screens the two named reagents' transcriptome loads are quoted from.
DEEP = {"EWSR1": os.path.join(MOD, "junction-aso-offtarget-e12n3-deep500-b1.json"),
        "TAF15": os.path.join(MOD, "junction-aso-offtarget-taf15e6n3-deep500-b1.json")}
#: The same two junctions at the DEFAULT ceiling — the reading the sentence must NOT be quoting.
DEFAULT = {"EWSR1": os.path.join(MOD, "junction-aso-offtarget-e12n3.json"),
           "TAF15": os.path.join(MOD, "junction-aso-offtarget-taf15e6n3.json")}

_WORDS = ("no one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen").split()


def _word(n):
    """`n` as the article spells it — the article spells small counts and prints large ones."""
    return _WORDS[n]


def _required(path, what):
    """⛔ A MISSING ARTIFACT IS A FINDING, NEVER A SILENT PASS. Every path here is tracked."""
    if not os.path.exists(path):
        pytest.fail(f"{what} is missing at {path}; it is committed, so regenerate it rather than "
                    "passing over the assertions that depend on it")
    return path


def _load(path, what):
    return json.load(io.open(_required(path, what), encoding="utf-8"))


@pytest.fixture(scope="module")
def prose():
    return re.sub(r"\s+", " ", io.open(_required(ARTICLE, "the journal article"),
                                       encoding="utf-8").read())


def _every_site(prose, pattern, expected, what):
    """Every site that states the quantity, not whether it appears somewhere.

    Same contract as `test_journal_article_numbers._every_site`: a pattern that has stopped matching
    is a guard that has silently stopped guarding, so at least one match is required.
    """
    found = re.findall(pattern, prose)
    assert found, (f"nothing in the journal article matches the construction that states {what} "
                   f"(/{pattern}/) — either the sentence was reworded and this guard must follow "
                   "it, or the claim was dropped")
    wrong = [f for f in found if f != expected]
    assert not wrong, (f"{what} is {expected!r} in the artifact, and the article states {wrong!r} "
                       f"at {len(wrong)} of its {len(found)} site(s)")


def _oligo(path, sequence, what):
    rows = [o for o in _load(path, what)["oligos"] if o["antisense_5to3"] == sequence]
    assert len(rows) == 1, (f"{os.path.basename(path)} carries {len(rows)} records for {sequence}; "
                            "the load the article quotes is not attributable to one design")
    return rows[0]


def _named_sequences(prose):
    """The two exon-3 reagents §2 names, taken from the sentence that names them."""
    m = re.search(r"5′-([ACGT]{16})-3′ at \*?EWSR1\*? exon \d+ joined to \*?NR4A3\*? exon \d+, and "
                  r"5′-([ACGT]{16})-3′ at \*?TAF15\*? exon \d+", prose)
    assert m, "§2 no longer names its two reagents in the construction this guard reads"
    return {"EWSR1": m.group(1), "TAF15": m.group(2)}


# ────────────────────────────────────────────────────────── §2's transcriptome load
def test_the_two_transcriptome_loads_are_the_deep_screens_own(prose):
    """⛔ "123 … against eight" — BOTH COUNTS AND THE CEILING THEY WERE COUNTED AT.

    Filed by the round-16 brief as having no artifact home. It has one: `n_true_cleavage_risk` on
    the design's own record in the deep re-screen, which is also the field
    `aso-gap-length-tradeoff.json` republishes as 123 for this reagent.
    """
    named = _named_sequences(prose)
    deep = {k: _oligo(DEEP[k], named[k], f"the deep re-screen at the {k} seam")["n_true_cleavage_risk"]
            for k in named}
    _every_site(prose,
                r"(\d+) gap-paired sense-strand near-matches for the \*?EWSR1\*? reagent at a "
                r"deeper search ceiling than the default, against (\w+) for the \*?TAF15\*? one",
                (str(deep["EWSR1"]), _word(deep["TAF15"])),
                "the two reagents' gap-paired transcriptome loads at the deeper ceiling")
    # ⛔ AND THE SENTENCE'S VERB. "Separates the two" is a RELATION, and it is the relation that
    # fails first: at the DEFAULT ceiling these same two designs return 5 and 7, so the EWSR1
    # reagent is the cleaner of the pair and the sentence is backwards. Binding the numerals alone
    # would pass a swap to the default reading.
    shallow = {k: _oligo(DEFAULT[k], named[k], f"the default-depth screen at the {k} seam")
               ["n_true_cleavage_risk"] for k in named}
    for k in named:
        assert deep[k] > shallow[k], (
            f"the {k} reagent's load is {deep[k]} at the screen this sentence calls deeper and "
            f"{shallow[k]} at the default one; 'a deeper search ceiling than the default' no "
            "longer describes the artifact the count comes from")
    assert deep["EWSR1"] > deep["TAF15"], (
        "§2 says the predicted load separates the two with the EWSR1 reagent the heavier; the deep "
        f"screens now record {deep['EWSR1']} against {deep['TAF15']}")


def test_most_of_that_load_really_is_predicted_models(prose):
    """⛔ "Most of the 123 are predicted transcript models rather than curated records."

    A MAJORITY claim, which is the kind that goes false without producing a new number anywhere.
    RefSeq marks a prediction in the accession itself — XM_/XR_ against curated NM_/NR_ — so the
    split is derivable from the stored hit list rather than from a field someone maintained.
    """
    named = _named_sequences(prose)
    row = _oligo(DEEP["EWSR1"], named["EWSR1"], "the deep re-screen at the EWSR1 seam")
    hits = [h for h in row["offtargets"] if h["risk"] == "true_cleavage_risk"]
    assert len(hits) == row["n_true_cleavage_risk"], (
        "the stored hit list and the count beside it disagree, so neither decides the sentence")
    predicted = [h for h in hits if h["acc"].split("_")[0] in ("XM", "XR")]
    m = re.search(r"Most of the (\d+) are predicted transcript models rather than curated records",
                  prose)
    assert m, "§2's predicted-models sentence has been reworded; re-anchor this guard to it"
    assert int(m.group(1)) == len(hits), (
        f"the sentence calls the load {m.group(1)} and the screen records {len(hits)}")
    assert len(predicted) * 2 > len(hits), (
        f"the article says MOST of the {len(hits)} gap-paired hits are predicted models; the "
        f"accessions make it {len(predicted)}")


# ────────────────────────────────────────────────────────── §2's coverage arithmetic
def test_the_taf15_arm_is_priced_at_every_breakpoint_reported_for_it(prose):
    """⛔ "priced at three of three reported breakpoints, an upper bound rather than an estimate".

    Both halves are the coverage module's own: the counts, and the fact that the fraction is 1.0 —
    which is what makes it an upper bound rather than an estimate. Stated in the journal article
    and nowhere else, and read by nothing.
    """
    arms = _load(COVERAGE, "the reagent-coverage artifact")["arms"]
    taf = [a for a in arms if a["partner"] == "TAF15"]
    assert len(taf) == 1, f"expected one TAF15 arm in the coverage artifact; found {len(taf)}"
    k, n = (int(x) for x in taf[0]["breakpoint_fraction_counts"].split("/"))
    _every_site(prose,
                r"\*?TAF15\*? arm is priced at (\w+) of (\w+) reported breakpoints",
                (_word(k), _word(n)),
                "the TAF15 arm's breakpoint numerator and denominator")
    assert taf[0]["breakpoint_fraction_within_partner"] == 1.0, (
        "the article calls the TAF15 arm an upper bound rather than an estimate, which is only "
        "true while its breakpoint fraction is 1.0; the artifact now says "
        f"{taf[0]['breakpoint_fraction_within_partner']}")


# ────────────────────────────────────────────────────────── §3's censoring bounds
def _filtered_oligo_records():
    """Every oligo record of the 38 orientation-filtered screens, in the screens' own order."""
    import sys
    sys.path.insert(0, MOD)
    from junction_aso_offtarget import ORIENTATION_FILTERED  # noqa: E402

    collapse = _load(COLLAPSE, "the locus-collapse index of the alignment screens")
    screens = [s for s in collapse["screens"] if s["orientation"] == ORIENTATION_FILTERED]
    assert screens, "no orientation-filtered screen was found, so §3's bounds are unchecked"
    out = []
    for s in screens:
        raw = _load(os.path.join(MOD, s["screen"]), f"the alignment screen {s['screen']}")
        out.extend(raw.get("oligos", []))
    return out


def test_the_cleanliness_bounds_are_the_screens_own_counts(prose):
    """⛔ SEVEN, 190, 47 AND 183 — THE OTHER SENTENCE FILED AS HAVING NO ARTIFACT HOME.

    It has one, and the derivation is already written: `test_aso_submission_numbers.py::
    test_censoring_counts_match_the_manuscript` computes exactly these counts and asserts them
    against the EXTENDED REPORT. The journal article restates all four and nothing read them.

    ⚠ "the alignment screen censors the rest" is the retention ceiling, not the 50-hit cap: a hit
    list of 15 or fewer is what the pipeline records as complete, and that is the 47.
    """
    rows = _filtered_oligo_records()
    counted = [o["n_offtarget_near_matches"] for o in rows
               if o.get("status") == "screened" and o.get("n_offtarget_near_matches") is not None]
    never_returned = len(rows) - len(counted)
    assessable = sum(1 for c in counted if c <= 15)
    _every_site(prose,
                r"(\w+) of the (\d+) screens never returned, and the alignment screen censors the "
                r"rest, leaving (\d+) of (\d+) assessable at all",
                (_word(never_returned), str(len(rows)), str(assessable), str(len(counted))),
                "the two cleanliness bounds, with both of their denominators")


def test_the_panel_size_is_the_screens_at_every_site_that_states_it(prose):
    """⛔ §6's THIRD SITE OF THE PANEL SIZE, WHICH TWO PINS DO NOT REACH.

    `aso_panel_designs_total_journal_abstract` and `…_journal_selection` pin the abstract's "Of 190
    junction-spanning 16-mers" and §3's "190 junction-spanning designs were tiled". §6's "the
    procedure that produced the 190 designs" is a third statement of the same count and is in no
    pin context — the site-census defect round 14 recorded against 45.8% and 40.6%, one section
    later. §1's "puts to all 190 designs" is a fourth.
    """
    n = _load(GAP_PAIRING, "the mature-parent gap-pairing screen")["corpus"]["n_designs"]
    _every_site(prose, r"the procedure that produced the (\d+) designs", str(n),
                "the panel size §6 says the released procedure produced")
    _every_site(prose, r"puts to all (\d+) designs", str(n),
                "the panel size §1 says the parent question is put to")


# ────────────────────────────────────────────────────────── §8's inputs
def test_the_partner_count_is_the_atlas_partner_list(prose):
    """⛔ "the five partner genes" — A COUNT SPELT AS A WORD, WHICH IS WHY NOTHING NUMERIC SAW IT.

    Round 15's third blocker was exactly this: "ten" is a word. The partner list is the atlas's
    `partners_scored`, and §8 also has to name *NR4A3* separately from it, because the transcript
    set the screens ran over is the partners PLUS the acceptor.
    """
    atlas = _load(ATLAS, "the fusion-junction atlas")
    partners = atlas["partners_scored"]
    _every_site(prose, r"Canonical transcripts for the (\w+) partner genes and for \*?NR4A3\*?",
                _word(len(partners)), "how many partner genes §8 obtained transcripts for")
    _every_site(prose, r"in-frame junctions of (\w+) modelled partners", _word(len(partners)),
                "how many modelled partners the panel was tiled across")
    assert atlas["acceptor"] not in partners, (
        f"§8 names the {len(partners)} partner genes AND {atlas['acceptor']} separately; the atlas "
        "now carries the acceptor inside its own partner list, so the sentence double-counts it")
    assert set(_load(PREMRNA, "the precursor screen")["genes"]) == set(partners) | {atlas["acceptor"]}, \
        "the screens no longer run over exactly the partner genes plus the acceptor, so §8's " \
        "sentence describes a different transcript set from the one that was screened"


def test_the_exon_convention_is_the_acceptors_own_model(prose):
    """⛔ THE AXIS THIS WORK WAS WITHDRAWN ON, IN THE DOCUMENT THAT DOES NOT GUARD IT.

    `test_exon_numbering_convention_is_computed.py` derives every exon-convention claim — from the
    EXTENDED REPORT. §2's convention sentence in the journal article is read by nothing, and it is
    the sentence that tells a reader which of two readings of "*NR4A3* exon 3" the reagents were
    tiled at.

    ★ THE CLAIM IS DERIVABLE. The two conventions differ for a gene exactly when a non-coding exon
    precedes its coding sequence. *NR4A3* is the acceptor of every design in the panel, so if its
    shift were zero the sentence would be warning about a distinction that does not exist for the
    only gene it applies to.
    """
    spans = _load(PREMRNA, "the precursor screen")["genes"]
    atlas = _load(ATLAS, "the fusion-junction atlas")
    acceptor = atlas["acceptor"]
    lengths = [b - a + 1 for a, b in spans[acceptor]["exon_spans_0based_inclusive"]]
    model = atlas["transcripts"][acceptor]
    assert sum(lengths) == model["cdna_nt"], (
        f"{acceptor}: the two artefacts no longer describe the same transcript")
    cds_from, cds_to = model["utr5_nt"], model["utr5_nt"] + model["cds_nt"] - 1
    coding, at = [], 0
    for index, length in enumerate(lengths, start=1):
        if at <= cds_to and at + length - 1 >= cds_from:
            coding.append(index)
        at += length
    shift = sum(1 for i in range(1, coding[0]) if i not in coding)
    assert re.search(r"Exon numbers throughout are transcript exon indices counted from the "
                     r"transcript 5′ end, including non-coding exons", prose), \
        "§2's exon-numbering convention sentence has been reworded; re-anchor this guard to it"
    assert shift > 0, (
        f"§2 warns that an acceptor exon number read under the coding-exon convention selects a "
        f"different reagent; {acceptor}'s committed model now has no non-coding exon ahead of its "
        "coding sequence, so the two conventions coincide and the warning names nothing")
    assert len(coding) < len(lengths), (
        f"§2 says the indices include non-coding exons; {acceptor}'s model now has none")


# ────────────────────────────────────────────────────────── the abstract's test articles
def test_the_cell_models_count_and_acceptor_are_the_evidence_files_own(prose):
    """⛔ "the two fusion-positive EMC cell models are reported at an *NR4A3* exon-2 acceptor".

    The abstract's last quantitative sentence, and the one that decides whether a laboratory holding
    those cells can order either named reagent. Both the count and the acceptor index come from
    `emc-model-junction-evidence.json`, whose rows quote the source report verbatim.
    """
    models = _load(MODELS, "the cell-model junction evidence")["models"]
    acceptors = {re.search(r"::\s*([A-Z0-9]+) exon (\d+)$", m["reported_junction"]).groups()
                 for m in models}
    genes = {g for g, _ in acceptors}
    exons = {e for _, e in acceptors}
    assert len(genes) == 1 and len(exons) == 1, (
        f"the two cell models are no longer reported at one acceptor: {sorted(acceptors)}")
    _every_site(prose,
                r"the (\w+) fusion-positive EMC cell models are reported at an \*?([A-Z0-9]+)\*? "
                r"exon-(\d+) acceptor",
                (_word(len(models)), genes.pop(), exons.pop()),
                "how many cell models there are and the acceptor they are reported at")


def test_the_abstract_names_as_many_test_articles_as_section_4_enumerates(prose):
    """⚠ NO ARTIFACT DECIDES "Five test articles are named" — §4 DOES, AND THAT IS THE BINDING.

    There is no committed census of test articles; the count is the article's own enumeration of
    three engineered constructs and two patient-derived models. Typing 5 here would be a second
    home for a fact §4 owns, so the abstract is checked AGAINST §4 instead. That is a weaker
    instrument than an artifact binding and is labelled as one — but it is the strongest available,
    and it fires on the drift that actually happens: §4 losing or gaining a test article while the
    abstract keeps its count.
    """
    stated = re.search(r"(\w+) test articles are named", prose)
    assert stated, "the abstract no longer states how many test articles are named"
    engineered = re.search(r"(\w+) are engineered constructs from a published functional study",
                           prose)
    patient = re.search(r"The other (\w+) are patient-derived", prose)
    assert engineered and patient, (
        "§4 no longer enumerates its test articles as an engineered group and a patient-derived "
        "group, so the abstract's count is bound to nothing")
    total = _WORDS.index(engineered.group(1).lower()) + _WORDS.index(patient.group(1).lower())
    assert _WORDS.index(stated.group(1).lower()) == total, (
        f"the abstract names {stated.group(1)} test articles; §4 enumerates "
        f"{engineered.group(1)} engineered and {patient.group(1)} patient-derived, which is "
        f"{_word(total)}")
    opening = re.search(r"(\w+) test articles bear on the junctions this panel designs against",
                        prose)
    assert opening, ("§4 no longer opens with a count of the test articles it enumerates, so the "
                     "abstract's count has no second site to agree with")
    assert _WORDS.index(opening.group(1).lower()) == total, (
        f"§4 opens by naming {opening.group(1)} test articles and then enumerates "
        f"{engineered.group(1)} plus {patient.group(1)}")


# ────────────────────────────────────────────────────────── §2's register hazard
def _table2_rows():
    text = io.open(_required(TABLES, "the generated journal display items"), encoding="utf-8").read()
    block = re.search(r"\*\*Table 2\..*?(?=\n\*\*Table |\Z)", text, re.S)
    assert block, "the generated display items no longer carry a Table 2"
    rows = re.findall(r"^\|\s*(?P<seam>[^|]+?)\s*\|\s*5′-(?P<seq>[ACGT]+)-3′\s*\|"
                      r"\s*(?P<verdict>[^|]+?)\s*\|", block.group(0), re.M)
    assert len(rows) == 2, f"Table 2 now carries {len(rows)} design rows, not a pair"
    return rows


def test_the_register_hazard_sentence_is_read_off_table_2(prose):
    """⛔ "Consecutive registers of one seam differ by a single-base slide and can carry opposite
    verdicts (Table 2)" — three claims, all decidable from the table it cites, none of them read.

    Round 14's blocker was a Table 2 caption counting rows it no longer had. This is the sentence
    four inches above it making the same three claims in the body, where no gate reaches at all.
    """
    rows = _table2_rows()
    seams = {r[0] for r in rows}
    assert len(seams) == 1, f"Table 2's two designs are no longer at ONE seam: {sorted(seams)}"
    a, b = (r[1] for r in rows)
    slides = {a[i:] == b[:len(b) - i] or b[i:] == a[:len(a) - i] for i in (1, 2)}
    assert True in slides, (
        f"§2 says consecutive registers of one seam differ by a single-base slide; {a} and {b} are "
        "not slides of one another")
    verdicts = {r[2].split("(")[0].strip().lower() for r in rows}
    assert len(verdicts) == 2, (
        f"§2 says the two members carry OPPOSITE verdicts; Table 2 now gives them {sorted(verdicts)}")
    assert any(v.startswith("do not order") for v in verdicts), (
        f"neither member of Table 2 is condemned, so 'opposite verdicts' names nothing: {sorted(verdicts)}")
    assert re.search(r"Consecutive registers of one seam differ by a single-base slide and can "
                     r"carry opposite verdicts \(Table 2\)", prose), \
        "§2's register-hazard sentence has been reworded, or now cites a different table"
