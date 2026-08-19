"""The three condemned designs must stay out of the ordering tables, and the header must say so truly.

⛔ WHY. The generated tables file is the one document a laboratory prints and orders from, and its
research-use header is its safety notice. Until 2026-08-17 that header read: "Three of the sequences
below are named in the main text as designs NOT to be carried forward" — and **none of the three was
in the file**. A cold reader went looking for three unsafe rows, found none, and the nearest-looking
candidates were the two reagents the paper actually recommends at those same seams, one of which
(`CAGTGGGCTTCTGCTG`) differs from a condemned sequence (`CAGTGGGCTCTCCACG`) by a glance.

⚠ THE HEADER WAS WRONG IN THE SAFE DIRECTION AND THAT IS NOT A DEFENCE. Pointing at absent danger
teaches a reader to distrust the notice, and the same sentence would have been the only warning if a
condemned design ever DID reach a table. So both directions are pinned here:

  * the three sequences are absent from the tables — the substantive safety property; and
  * the header describes that absence rather than asserting a presence.

⭐ THE SEQUENCES ARE READ FROM THE MANUSCRIPT, NOT TYPED HERE. A guard holding its own copy of the
list would keep passing after §2.6 condemned a fourth design, which is the failure mode it exists to
prevent. §2.6 names them in one sentence, and that sentence is the source of truth.

⛔ REPAIRED 2026-08-19 (lane C-b). `test_the_research_use_header_describes_the_absence…` claimed in
its own docstring to be "ASSERTED ON THE PROPERTY, NOT ON THE WORDING" and was a blacklist of three
literal sentences. Every one of them is reinstatable in synonyms — "two of the strings printed here
are designs the main text forbids", "one of the sequences in this document must not be carried
forward" — and the guard passes. What it now asserts instead is the SHAPE of the claim: any sentence
in the banner that is about the condemned designs AND locates them among the ORDERABLE ROWS must
negate that location, and at least one such sentence must exist. The negation is looked for with the
condemnation phrase itself masked out, because "designs NOT to be carried forward are in these
tables" carries the word "not" while asserting exactly the defect.

⚠ AND THE SCOPE IS THE PARAGRAPH THAT NAMES THE THREE, NOT THE WHOLE BANNER. The banner now also
carries a TRUE presence claim — "a further fifteen rows of these tables … are also NOT to be
ordered", about the ⚑ rows, which really are in the tables. A guard that flagged that would be
flagging a correct sentence, which is how a checker stops being read. Two locators were dropped for
the same reason: "printed here" and "listed here" are what the banner does with the three ON
PURPOSE, so a reader holding a transcribed string has something to check it against.
"""
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASO = os.path.join(REPO, "research", "manuscripts", "aso")
PAPER = os.path.join(ASO, "fusion-junction-aso-research-article.md")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")

#: How this paper condemns a design, as a family rather than as one sentence.
#: ⛔ RE-ANCHORED 2026-08-19 (blind safety screen). The anchor was "are named here as not to be
#: carried forward" — the weakest of the four phrasings the paper used for these same three
#: molecules, and the only one standing beside their full reasoning. "Not carried forward",
#: reinforced by "excluded from every best-design field", reads as a RANKING decision (we did not
#: select these) rather than a prohibition, while the abstract, Box 1 and the CSV all say "not to be
#: used" / "DO NOT ORDER". A reader entering at §2.6 could reasonably have concluded they were
#: simply not the leads.
#: ⚠ WIDENED 2026-08-19 (lane C-b) from the single string "must not be ordered or used" to the
#: family, so that a rewrite inside the family re-anchors the guard instead of removing it.
_CONDEMNATION = re.compile(
    r"must not be (?:ordered|used|carried|synthesised|synthesized)"
    r"|not to be (?:ordered|used|carried forward)"
    r"|do not order",
    re.I)


def _flat(path):
    return " ".join(open(path, encoding="utf-8").read().split())


def _condemned_sequences():
    """The designs §2.6 condemns, read from the manuscript.

    Scans every condemnation the paper makes and takes the first whose preceding window names three
    or more distinct designs — §2.6's sentence, wherever it sits and however it is phrased.
    Sequences in this manuscript are always written 5′-XXXX-3′.
    """
    txt = _flat(PAPER)
    tried = []
    for hit in _CONDEMNATION.finditer(txt):
        window = txt[max(0, hit.start() - 1200):hit.start()]
        # Deduplicate, order-preserving: the window also restates the seams, and a repeat is not a
        # fourth design.
        out = list(dict.fromkeys(re.findall(r"5[′']-([ACGT]{12,25})-3[′']", window)))
        tried.append((hit.group(0), len(out)))
        if len(out) >= 3:
            return out
    pytest.fail(
        "no condemnation sentence in the manuscript is preceded by three or more designs. "
        f"Condemnations found and the design count before each: {tried}. §2.6 names the designs "
        "that must not be ordered; re-anchor _CONDEMNATION on whatever now condemns them rather "
        "than deleting this test.")


def _table_rows(path):
    """Only the pipe-delimited table rows — the lines a laboratory orders from.

    ⛔ THIS WAS A WHOLE-DOCUMENT SCAN AND THAT WAS TOO BROAD (fixed 2026-08-17). The property this
    guard exists for is "no condemned design sits in an ORDERABLE ROW". Scanning the flattened file
    also swept the research-use banner, so the moment the banner gained an explicit DO-NOT-ORDER list
    naming the three sequences — which a cold reader asked for, because two of them are one- and
    two-position register shifts of a listed reagent sharing 15 of 16 bases, and a reader cannot
    check a transcription against a list the document does not carry — this test failed on the fix.
    ⚠ A GUARD THAT FIRES ON ITS OWN REMEDY IS MIS-SCOPED, NOT VINDICATED. The tempting move is to
    weaken the assertion; the correct one is to narrow what it reads, so the substantive property
    stays exactly as strict as it was. Naming a sequence in order to forbid it and printing it in a
    row to be ordered are opposite acts, and only the second is the defect.
    """
    return "\n".join(ln for ln in open(path, encoding="utf-8").read().splitlines()
                     if ln.lstrip().startswith("|"))


def _banner_lines():
    return [ln for ln in open(TABLES, encoding="utf-8").read().splitlines()
            if not ln.lstrip().startswith("|")]


def test_no_condemned_design_appears_in_an_orderable_table_row():
    rows = _table_rows(TABLES)
    present = [s for s in _condemned_sequences() if s in rows]
    assert not present, (
        f"{len(present)} design(s) the main text condemns are printed in an orderable table row: "
        f"{present}. Each pairs its whole catalytic gap against the patient's own un-rearranged "
        "NR4A3 allele. Remove the row at the GENERATOR (research/manuscripts/submission_tables.py) "
        "— a table a laboratory orders from must not carry a sequence the paper says not to carry "
        "forward.")


def test_the_banner_prints_the_condemned_designs_as_a_do_not_order_list():
    """Naming them is load-bearing, and the reason is a near-neighbour hazard, not tidiness.

    A reader who transcribes `5′-AGTGGGCTCTCCACGG-3′` from Table 7 has no way to notice they have
    written one of the condemned register shifts instead unless the document carries the forbidden
    strings. The banner is the only place that can hold them without becoming an orderable row.
    """
    banner = "\n".join(_banner_lines())
    missing = [s for s in _condemned_sequences() if s not in banner]
    assert not missing, (
        f"the research-use banner no longer names {len(missing)} of the condemned design(s): "
        f"{missing}. They must be printed somewhere outside the tables so a reader can check a "
        "transcribed sequence against them.")


# ── the header's claim about WHERE the condemned designs are ────────────────────────────────
#
# Asserted as a shape. A sentence that is about the condemned designs and places them relative to
# this file is a LOCATION claim, and the companion test above proves the only true location claim is
# a negative one. Neither the vocabulary of the claim nor the count it uses is pinned.

#: Phrases that put something among the ORDERABLE ROWS of this document.
#: ⚠ "printed here" and "listed here" are NOT in this set, and that is deliberate. The banner
#: prints the three condemned strings on purpose, so a reader can check a transcription against
#: them — "They are printed here because excluding them by description leaves a reader with a
#: transcribed sequence nothing to check it against" is the remedy, not the defect. What may not be
#: said is that they are among the rows.
_IN_THIS_FILE = re.compile(
    r"\b(?:below|in any row|in the rows|among the rows|in these tables|of these tables"
    r"|in the tables|in this table|in any of these tables)\b", re.I)

#: Any negation. Searched only in the text BEFORE a location phrase, with the condemnation phrase
#: masked out first — "designs NOT to be carried forward are in these tables" is the defect, and its
#: own "not" must not be allowed to launder it.
_NEGATION = re.compile(r"\b(?:no|none|not|never|neither|nothing|absent|excluded|nowhere|without)\b",
                       re.I)

_LOOKBACK = 90


def _sentences(text):
    # ⚠ EMPHASIS STRIPPED FIRST. The banner ends run-in headings as `…WHITELIST.** A further…`, so a
    # splitter keyed on "full stop then whitespace" swallowed two sentences into one — and a
    # negation belonging to the first then laundered a presence claim in the second.
    text = re.sub(r"[*_]", "", text)
    return [s.strip() for s in re.split(r"(?<=[.:;])\s+", text) if s.strip()]


def _condemned_paragraphs():
    """The banner paragraph(s) that print the condemned designs.

    ⛔ SCOPED HERE AND NOT DOCUMENT-WIDE, DELIBERATELY. The banner also carries a TRUE presence
    claim — "a further fifteen rows of these tables … are also NOT to be ordered", about the ⚑ rows
    — and a guard that flagged it would be flagging a correct sentence, which is how a checker
    stops being read. The claim this file is about is where THE THREE are, so the scope is the
    paragraph that names them.
    """
    condemned = _condemned_sequences()
    blocks = [b for b in re.split(r"\n\s*\n", "\n".join(_banner_lines()))
              if any(s in b for s in condemned)]
    assert blocks, (
        "no banner paragraph prints a condemned design, so the banner makes no claim about where "
        "they are. The companion test covers their absence from the rows.")
    return [" ".join(b.split()) for b in blocks]


def _location_claims():
    """(sentence, unnegated location phrases, negated ones) over the paragraphs naming the three."""
    out = []
    for paragraph in _condemned_paragraphs():
        for sentence in _sentences(paragraph):
            masked = _CONDEMNATION.sub(lambda m: " " * len(m.group(0)), sentence)
            unnegated = [m.group(0) for m in _IN_THIS_FILE.finditer(masked)
                         if not _NEGATION.search(masked[max(0, m.start() - _LOOKBACK):m.start()])]
            negated = [m.group(0) for m in _IN_THIS_FILE.finditer(masked)
                       if _NEGATION.search(masked[max(0, m.start() - _LOOKBACK):m.start()])]
            if unnegated or negated:
                out.append((sentence, unnegated, negated))
    return out


def test_the_research_use_header_never_places_a_condemned_design_inside_this_file():
    """⛔ THE 2026-08-17 DEFECT, asserted on the claim's shape rather than on three literal strings.

    "Three of the sequences below are named in the main text as designs NOT to be carried forward"
    is a condemnation sentence carrying an unnegated location phrase ("below"). So is "designs not
    to be carried forward are in these tables", and so is any synonym of either. The companion test
    proves no such design is in a row, so every location claim the banner makes about them has to
    be a negative one.
    """
    claims = _location_claims()
    assert claims, (
        "the paragraph printing the condemned designs places them nowhere at all — it never says "
        "whether they are in these tables. The main text names designs that must not be ordered; "
        "the ordering document is where that matters most.")
    offenders = [(s, bad) for s, bad, _ in claims if bad]
    assert not offenders, (
        "the research-use header places a condemned design inside this file: "
        + " | ".join(f"{phrase!r} in {s[:120]!r}" for s, bad in offenders for phrase in bad)
        + ". The companion test proves their absence from every row. Pointing a reader at danger "
          "that is not there teaches them to distrust the one notice that would matter if it ever "
          "were.")


def test_the_research_use_header_states_the_absence_rather_than_leaving_it_implied():
    """Avoiding the false claim is not the same as making the true one.

    The header has to say, in some wording, that the condemned designs are in NO row of these
    tables — otherwise a reader holding one of the three printed strings cannot tell whether it is
    a forbidden design or one of the table's own reagents.
    """
    claims = _location_claims()
    assert any(good for _, _, good in claims), (
        "no sentence in the research-use header states where the condemned designs are NOT. The "
        "banner prints the three forbidden strings; without an explicit 'in no row of these "
        "tables' a reader meeting them there cannot tell them from the reagents the tables list. "
        f"Sentences about the condemned designs: "
        + " | ".join(repr(s[:110]) for s, _, _ in claims))


def test_the_banner_does_not_claim_a_condemned_design_is_in_a_row_anywhere_it_names_one():
    """The same shape check, run over every sentence that NAMES one of the three by its bases.

    A reader holding a transcribed string looks it up. Wherever the banner prints it, whatever it
    says about it there has to be consistent with the rows — and the rows do not carry it.
    """
    condemned = _condemned_sequences()
    offenders = []
    for sentence in _sentences(" ".join("\n".join(_banner_lines()).split())):
        if not any(s in sentence for s in condemned):
            continue
        masked = _CONDEMNATION.sub(lambda m: " " * len(m.group(0)), sentence)
        offenders += [(sentence, m.group(0)) for m in _IN_THIS_FILE.finditer(masked)
                      if not _NEGATION.search(masked[max(0, m.start() - _LOOKBACK):m.start()])]
    assert not offenders, (
        "a banner sentence naming a condemned design places it inside this file: "
        + " | ".join(f"{phrase!r} in {s[:130]!r}" for s, phrase in offenders)
        + ". The companion test proves no row carries it.")
