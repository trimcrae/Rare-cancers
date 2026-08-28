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


def _any_site_that_states_it(prose, pattern, expected, what):
    """The count is checked wherever it IS stated, and no site is required to state it.

    ⛔ THE DIFFERENCE FROM `_every_site`, WHICH IS THE WHOLE POINT: that helper requires at least
    one match, because a pattern that has stopped matching is usually a guard that has silently
    stopped guarding. That is the right default and it stays the default. It is the WRONG check for
    a sentence whose count is allowed to become an anaphor — there the absence of a match is the
    prose working, not the guard failing.
    ⛔ SO THIS HELPER IS ONLY EVER CORRECT NEXT TO A SEPARATE ASSERTION THAT THE CLAIM ITSELF IS
    STILL PRESENT. Used alone it is exactly the fail-quiet shape `_every_site` exists to forbid.
    Its one caller asserts the release claim in the line above.
    """
    wrong = [f for f in re.findall(pattern, prose) if f != expected]
    assert not wrong, (f"{what} is {expected!r} in the artifact, and the article states {wrong!r}")


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
    assert m, "§2's predicted-models sentence has been reworded; re-anchor this guard to it ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
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
    # ⛔ THE RELEASE SENTENCE MAY NAME THE COUNT OR REFER BACK TO IT, AND ONLY ONE OF THOSE IS A
    # SITE (2026-08-28, AUT-PD-117). This required "the procedure that produced the N designs" to
    # match at least once. Round 18 condensed the Abstract's "Also released is the procedure that
    # produced the 190 designs" to "The procedure producing them is released" — the count moved
    # from a restatement to an anaphor three sentences after the Abstract's own "panel of 190
    # junction-spanning 16-mers", which is pinned as `aso_panel_designs_total_journal_abstract`.
    # Nothing became unbound; the site simply stopped being a site, and a site census fired on its
    # own absence.
    # ⭐ SO THE TWO THINGS ARE ASSERTED SEPARATELY, WHICH IS WHAT THEY ALWAYS WERE. The CLAIM —
    # that the design procedure is released — is required to be present in any wording, so it
    # cannot be dropped silently. The COUNT is checked at every site that states it, and this
    # sentence is allowed to have none. Requiring the count back would buy nothing a pin does not
    # already hold, at the cost of a word in a paper whose page budget is a per-page charge.
    assert re.search(r"procedure (?:that produced|producing|behind) (?:the |them\b)", prose, re.I), (
        "the journal article no longer says the design procedure is released. That release is what "
        "makes the panel reproducible rather than merely reported, and it is a claim about this "
        "deposit — not a restatement of the count, which the Abstract pin holds.")
    _any_site_that_states_it(
        prose, r"procedure (?:that produced|producing) the (\d+) designs", str(n),
        "the panel size the released procedure is said to have produced")
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
    # ⚠ RE-ANCHORED 2026-08-27, AND ONLY FOR PUNCTUATION. The v2 readability pass set the NR4A3
    # clause off with commas — "for the five partner genes, and for *NR4A3*, were obtained" — which
    # is the identical sentence with identical words. The optional commas are the whole change; the
    # count, the construction around it and the binding to the atlas partner list are untouched, and
    # a mutation of the count still fails (asserted in the sibling test below).
    _every_site(prose, r"Canonical transcripts for the (\w+) partner genes,? and for \*?NR4A3\*?",
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
        "§2's exon-numbering convention sentence has been reworded; re-anchor this guard to it ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
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


def test_the_register_hazard_sentence_is_read_off_the_canonical_file(prose):
    """⛔ §2's register hazard now names its own molecule, so it is checked against the data.

    The sentence: "Consecutive registers of one seam differ by a single-base slide and can carry
    opposite verdicts, and the condemned class reaches these reagents: 5′-AGGGCATATCTTGTGT-3′ is one
    slide from the TAF15 reagent and pairs 11 base pairs of wild-type NR4A3 through its whole
    catalytic gap." Three checkable claims: it IS a single-base slide, it IS condemned, and 11 bp is
    what the screen measured.

    ⚠ RE-ANCHORED 2026-08-24, FROM A TABLE TO THE CANONICAL FILE. This guard used to read Table 2,
    the near-identical-twins display item, which was cut when the controls table pushed the article
    past its six-page fee budget; the hazard moved into §2 prose with its molecule named. Binding to
    `fusion-junction-aso-sequences.csv` is strictly better than binding to a table — the table was
    itself generated from that file, so this removes a hop rather than adding one, and the claim now
    fails if the SCREEN moves rather than only if the table is reformatted.
    """
    m = re.search(r"5′-(?P<condemned>[ACGT]+)-3′ is one\s+slide from the \*TAF15\* reagent and pairs "
                  r"(?P<bp>\d+) base pairs of wild-type\s+\*NR4A3\*", prose)
    assert m, ("§2 no longer names the condemned neighbour of the TAF15 reagent, its slide relation "
               "and its duplex length in one sentence; re-anchor this guard or restore the claim")
    condemned, stated_bp = m.group("condemned"), int(m.group("bp"))

    rows = {r["sequence"]: r for r in _all_csv_rows()}
    reagent = "GGGCATATCTTGTGTG"
    assert condemned in rows, f"{condemned} is not in the canonical sequence file at all"
    row = rows[condemned]

    slides = {condemned[i:] == reagent[:len(reagent) - i] or
              reagent[i:] == condemned[:len(condemned) - i] for i in (1, 2)}
    assert True in slides, (
        f"§2 calls {condemned} one slide from {reagent}; they are not slides of one another")
    assert (row.get("do_not_order") or "").strip(), (
        f"§2 calls {condemned} condemned, but the canonical file does not flag it do-not-order")
    measured = int(row["mature_parent_duplex_through_gap_bp"])
    assert measured == stated_bp, (
        f"§2 says {condemned} pairs {stated_bp} bp of a wild-type parent through its whole gap; the "
        f"canonical file measures {measured}")
    assert row["mature_parent_duplex_gene"] == "NR4A3", (
        f"§2 names wild-type NR4A3 as the parent; the file says "
        f"{row['mature_parent_duplex_gene']}")


def _all_csv_rows():
    """Every row of the canonical sequence file, comments dropped."""
    import csv
    path = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))


def _panel_5_6_5():
    rows = _all_csv_rows()
    out = [r for r in rows if r["geometry"] == "5-6-5" and r["gap_level_margin"]]
    assert out, f"{path} carries no 5-6-5 design with a gap-level margin"
    return out


def _named_for_synthesis():
    """The reagents the journal tables print in Table 1 — derived, never typed."""
    tables = io.open(os.path.join(ASO, "fusion-junction-aso-journal-tables.md"),
                     encoding="utf-8").read()
    first = re.split(r"(?m)^(?=\*\*Table 2\.)", tables)[0]
    found = re.findall(r"5[\u2032']-([ACGT]{12,25})-3[\u2032']", first)
    assert found, "Table 1 prints no sequence, so the named reagents cannot be derived"
    return set(found)


def test_the_top_gap_level_margin_is_the_panels_maximum_and_both_reagents_hold_it():
    """⛔⛔ FOUND BY THE EXHAUSTIVE ABLATION SWEEP, NOT BY THE PER-COMMIT SAMPLE (2026-08-22).

    One of 41 numbered journal-article sentences survived every guard that opens the file:

        "Both hold the panel's top gap-level margin of three: three junction-unique bases
         inside the catalytic gap on the shorter side of the breakpoint."

    The census called it covered — two guards' patterns matched it — and neither bound the number.
    It is the margin a reader uses to judge how much junction-unique sequence a reagent actually
    has, and `gap_level_margin` decides it exactly: over the 206 5-6-5 designs the distribution is
    {1: 81, 2: 83, 3: 42}, so the top is 3, and both named reagents hold it.

    ⚠ THE SAMPLE IS NOT THE SWEEP. Six sentences per document per commit is enough to catch a
    census that has stopped binding anything; it is not enough to enumerate what is unbound. Run
    `PREFLIGHT_FULL=1` over this suite before anything outward-facing.
    """
    rows = _panel_5_6_5()
    top = max(int(r["gap_level_margin"]) for r in rows)
    named_seqs = _named_for_synthesis()
    named = [r for r in rows if r["sequence"] in named_seqs]
    assert len(named) == len(named_seqs), (
        "a sequence Table 1 names for synthesis is not in the canonical 5-6-5 panel")
    holders = [r for r in named if int(r["gap_level_margin"]) == top]
    assert len(holders) == len(named), (
        f"the article says BOTH named reagents hold the panel's top gap-level margin of {top}; the "
        f"canonical file gives {[(r['sequence'], r['gap_level_margin']) for r in named]}. Either a "
        "reagent was reselected or the margin moved.")

    text = io.open(ARTICLE, encoding="utf-8").read()
    word = _word(top)
    assert re.search(rf"top\s+gap-level\s+margin\s+of\s+{word}\b", text), (
        f"the article does not state the panel's top gap-level margin as {word!r}. The canonical "
        f"file's maximum over the 5-6-5 panel is {top}; a stated margin that is not the measured "
        "one tells a reader a reagent carries more junction-unique sequence than it does.")
    # ⚠ `\s+`, not a space: the phrase wraps across a line break in the source, and a literal-space
    # pattern would report the claim missing when it is simply typeset over two lines.
    assert re.search(rf"{word}\s+junction-unique bases", text), (
        f"the article states the top margin but not what it counts — {word} junction-unique bases. "
        "The number and its unit have to move together, or the next edit separates them.")


def _numbered_sections(text):
    """{n: body} for the article's own `## N ` headings."""
    parts = re.split(r"(?m)^##\s+(\d+)\s", text)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def _named_cross_references_resolve(text, flat):
    """The IMRaD half: a NAMED section reference must resolve, and carry what it is cited for."""
    headings = set(re.findall(r"(?m)^##\s+(.+?)\s*$", text))
    names = [h for h in ("Introduction", "Materials and Methods", "Results", "Discussion")
             if h in headings]
    assert names, ("the article has neither numbered sections nor any of the four IMRaD headings, "
                   "so nothing here is checkable — re-anchor this guard to whatever it now uses")

    bodies = {}
    for name in names:
        m = re.search(rf"(?m)^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
        bodies[name] = re.sub(r"\s+", " ", m.group(1)).lower() if m else ""

    cited = sorted({n for n in names if re.search(rf"\bthe {re.escape(n)}\b", flat)})
    assert cited, ("the article makes no section cross-reference at all — if the references were "
                   "deliberately removed, retire this guard rather than leaving it green on nothing")

    # ★ THE SEMANTIC HALF, where the sentence names both the section and the thing:
    #   "the parent liability the Introduction describes" -> 'parent liability' must be IN it.
    misdirected = []
    pattern = (r"([a-z][a-z-]+(?:\s+[a-z][a-z-]+)?)\s+the\s+("
               + "|".join(re.escape(n) for n in names)
               + r")\s+(?:describes|specifies|defines|prescribes|identifies|states)")
    for m in re.finditer(pattern, flat):
        phrase, name = m.group(1).strip().lower(), m.group(2)
        if phrase in ("what", "which", "that", "and the", "of the", "is what", "it is",
                      "and what", "is the"):
            continue
        if phrase not in bodies[name]:
            misdirected.append((name, phrase))
    assert not misdirected, (
        "a cross-reference names a term the section it points at does not state:\n  "
        + "\n  ".join(f"{n} is cited for {p!r}, which does not appear in it" for n, p in misdirected)
        + "\n\nEither the reference points at the wrong section, or the term moved and the "
          "reference was not followed. Both send a reader to the wrong definition.")


def test_a_section_cross_reference_points_at_the_section_that_states_the_thing():
    """⛔⛔ THE LAST SENTENCE THE EXHAUSTIVE ABLATION SWEEP COULD NOT BIND (2026-08-22).

    "… neither pairs a wild-type parent through the gap at §3's ten-base-pair criterion."
    Its only DIGIT is the 3, and perturbing it to §7 changed nothing any guard reads: sections 1–8
    all exist, so an existence check would have passed it, and the sentence would ship pointing a
    reader at a section that does not define the criterion it names.

    ★ THE BINDING IS SEMANTIC, NOT NUMERIC: the section a claim cites must CONTAIN the thing it is
    cited for. That is checkable exactly where the reference names a technical term.

    ⚠ SCOPE, STATED HONESTLY. Only `§N's <hyphenated term>` is bound. The article's other four
    references read "§5 prescribes", "§4 is uncertifiable on…" — verb phrases whose target is a
    whole argument rather than a named term, and a naive span for those produces false positives
    ('arriving from a'), which is a guard that gets deleted rather than fixed. Those are covered
    only by the existence check below, and that is the limit.
    """
    text = io.open(ARTICLE, encoding="utf-8").read()
    flat = re.sub(r"\s+", " ", text)
    sections = _numbered_sections(text)

    # ⭐ AN IMRaD MANUSCRIPT HAS NO NUMBERED SECTIONS, AND THE PROPERTY SURVIVES THE CONVENTION
    # CHANGE (2026-08-25). Nucleic Acid Therapeutics requires Introduction / Materials and Methods /
    # Results / Discussion, unnumbered, so every `§N` reference in this article was rewritten as a
    # NAMED one. The binding this guard exists for is unchanged — the section a claim cites must
    # CONTAIN the thing it is cited for — and it is still checkable, just against names.
    # ⛔ NOT RETIRED AND NOT MADE VACUOUS: a guard that returns early when its subject changes shape
    # is the "reports while measuring nothing" defect this repository keeps paying for.
    if not sections:
        return _named_cross_references_resolve(text, flat)

    refs = sorted({int(n) for n in re.findall(r"§\s*(\d+)", flat)})
    assert refs, "the article makes no section cross-reference at all — re-anchor or retire this"
    dangling = [n for n in refs if n not in sections]
    assert not dangling, (
        f"the article cites section(s) {dangling}, which it does not contain (it has "
        f"{sorted(sections)}). A reader following that reference lands nowhere.")

    misdirected = []
    for m in re.finditer(r"§\s*(\d+)(?:'s|’s)\s+([a-z]+(?:-[a-z]+)+(?:\s+[a-z]+)?)", flat):
        n, phrase = int(m.group(1)), m.group(2)
        body = re.sub(r"\s+", " ", sections.get(n, "")).lower()
        if phrase.lower() not in body:
            misdirected.append((n, phrase))
    assert not misdirected, (
        "a cross-reference names a term the section it points at does not state:\n  "
        + "\n  ".join(f"§{n} is cited for {p!r}, which does not appear in §{n}" for n, p in misdirected)
        + "\n\nEither the reference points at the wrong section, or the term moved and the "
          "reference was not followed. Both send a reader to the wrong definition.")
