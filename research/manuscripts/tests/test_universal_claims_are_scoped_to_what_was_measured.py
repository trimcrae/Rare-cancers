"""Universal and counted claims must not be wider than the quantity that was actually measured.

⛔ WHY. On 2026-08-18 an exhaustive audit of all 251 universal/counted sentences in the manuscript
returned six findings, two of them CONFIRMED CONTRADICTIONS of the paper's own content. Every one had
the same shape: a sentence whose scope was left open ("every", "the only", "outside every") while the
measurement behind it covered a subset. None was a wrong number — the arithmetic was right in all six
— so no numeric test could have caught them.

⛔⛔ AND THEY WERE MISSED BY EIGHT PRIOR BLIND SCREENS. The class only started surfacing once the
screening brief was widened to name it explicitly. That is the reason this file exists: a screener
finds this class only if it is told to look, and a test is told every time.

The six, and what each now has to say instead:

1. §2.10 / Table 4 caption — ΔΔG°37 was called the margin over "the best duplex either parent can
   form". The generator (junction_aso_thermo.py) scores only the two SEAM runs, donor-side and
   acceptor-side, which by the paper's own identity reach at most ten base pairs. 87 of the 190
   designs pair a mature parent at ten or more base pairs somewhere else. "Best" was wider than the
   search.
2. §4.3 / §5 — "It falls outside every parent count reported here" / "Every parent count requires the
   catalytic gap paired in full". The hit is sense-strand, intron–exon-spanning and one gap mismatch
   short, so it sits inside §2.5's 53, forty and 21 — which are parent counts. §5's version named
   "the 21 designs of §2.5" as a count in the same sentence that denied such counts exist.
3. §2.9 — "the 16-mer surviving at that junction". Two 16-mers survive at TCF12 exon 7.
4. §4.4 — an optional arm "only at EWSR1 exon 12", defended against TAF15 exon 6 alone while Table 2
   shows lower-margin registers clearing the parent screen at two of the other three junctions.
5. §2.7 — "The genome scan, screen 5, removes that bound", said of both liability classes. Screen 5
   runs at two mismatches; an eleven-base-pair run inside a 16-mer carries five.
6. §5 — "Every screened count outside §2.9 is for one architecture", falsified by §4.2 and Table 5.

★ EACH TEST BELOW PINS THE CORRECTED SCOPE, NOT THE WORDING. The prose may be rewritten freely; what
may not come back is the open quantifier over a measurement that does not reach that far.

⛔⛔ REPAIRED 2026-08-19 (lane C-b) — THE FILE DID NOT DO WHAT ITS OWN PREAMBLE SAID. Five of the six
sections were EXACT-STRING BLACKLISTS: `assert "best duplex either parent can form" not in text`,
`assert "excluded from every near-match count" not in body`, and three more. Every one of the six
recorded contradictions can be reinstated in synonyms with no test turning red — "the strongest
duplex a parent forms", "excluded from all near-match counts", "the design surviving at that
junction", "at EWSR1 exon 12 alone", "screen 5 lifts that bound". What each now asserts is the
QUANTIFIER GOVERNING THE NOUN, the way
`test_no_sentence_quantifies_universally_over_the_parent_counts` already did — and every rewrite in
this round was re-proved against the original defective string before it was kept.

⚠ AND THE SECTION ANCHORS ARE NOW HEADINGS, NOT SENTENCES. Six of these tests located their passage
by `body.find("<a sentence>")`, so a rewrite of that sentence turned the guard into a hard failure
with nothing wrong, and a rewrite that also removed the anchor's clause would have had to be
re-anchored by hand. They now split the document at its `##`/`###` headings and scan the section.

⚠ ONE FINDING THIS ROUND, REPORTED UPWARD RATHER THAN GUARDED: §6's screen-5 bullet still reads
"Screens 1 to 4 are bounded either by an annotation or by six transcripts. The fifth removes that
bound." — the same wording §2.7 was corrected for. There the antecedent is the SEARCH SPACE, which
screen 5 genuinely does unbound, and the ≤2-mismatch threshold follows one clause later, so it is
not the §2.7 contradiction restated. It is not asserted on here, because a checker that flags true
sentences is worse than no checker.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
JOURNAL = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-article.md")
TABLES = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-submission-tables.md")

#: ⛔⛔ THIS MODULE READ ONE DOCUMENT WHILE REASONING ABOUT "THE MANUSCRIPT" (round 10's
#: guard-coverage audit, item MISCOVERED G). `ARTICLE` was the extended report and no journal-article
#: path appeared anywhere in the file, so the class it polices — an open quantifier over a subset
#: measurement — was unguarded in the paper that is actually being submitted. Three inversions in the
#: journal article went green in a run that included this module: "none 3′ of exon 3" -> "several",
#: "Every source of a test article named here ends at someone culturing cells" -> "reaches an animal
#: model", and "performs the in-silico half of the first step" -> "performs all five of those steps".
#:
#: ★ THE SPLIT IS BY WHAT A CHECK IS, NOT BY A LIST OF FILES. A PROHIBITION — no sentence may put an
#: open quantifier over a measurement that does not reach that far — is true of every document this
#: work submits, so it runs over `ARTICLES`. A REQUIREMENT on a numbered section — "§2.10 must say
#: the comparison is to the seam" — can only be checked where that section exists, and the journal
#: article has no numbered sections at all. Adding a third document means adding one path here.
ARTICLES = [ARTICLE, JOURNAL]
IDS = [os.path.basename(a) for a in ARTICLES]


def _read(path):
    if not os.path.exists(path):
        pytest.fail(f"missing artefact: {path}")
    return open(path, encoding="utf-8").read()


def _body(path=ARTICLE):
    text = _read(path)
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)


def _flat(text):
    """⛔ THE MANUSCRIPT HARD-WRAPS AT ~100 COLUMNS, SO A PROSE NEEDLE MUST FLATTEN FIRST.

    Measured 2026-08-19 (lane C2): §6 says "…excluded from this / screen's near-match counts…" with
    the wrap falling INSIDE the phrase, and `assert "this screen's near-match counts" in _section(6)`
    therefore failed on correct prose. A guard that goes red on a document that says exactly what it
    is meant to say is worse than one that is silent: the repair reflex is to re-type the needle.
    """
    return " ".join(text.split())


def _sentences(text):
    """Prose sentences only — table rows and fenced blocks carry no universals to audit."""
    prose = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    prose = "\n".join(ln for ln in prose.splitlines() if not ln.lstrip().startswith("|"))
    prose = prose.replace("\n", " ")
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", prose) if s.strip()]


def _section(number):
    """The text of §<number>, located by its HEADING rather than by a sentence inside it.

    ⛔ WHY NOT A SENTENCE. Six tests here used `body.find("<some clause>")` as their anchor, which
    couples a scope guard to a wording the manuscript is free to change — the guard then fails for
    the wrong reason, and the repair is to re-type the clause, which is how a needle rots.
    """
    body = _body()
    heads = [(m.start(), m.group(1), m.group(2))
             for m in re.finditer(r"^(#{2,3})\s*([\d.]+)\s*·", body, flags=re.M)]
    for index, (start, _, found) in enumerate(heads):
        if found == number:
            end = heads[index + 1][0] if index + 1 < len(heads) else len(body)
            return body[start:end]
    pytest.fail(f"§{number} is not in the manuscript; its scope claims are unchecked. "
                f"Headings found: {[h[2] for h in heads]}")


# ── 1 · the free-energy margin is over the seam, not over the transcriptome ──────────────────

#: A superlative GOVERNING a parent duplex. The generator scores two seam runs; a superlative over
#: what a parent "can form" claims a search of the parent that was never run.
_SUPERLATIVE = r"(?:best|strongest|tightest|most\s+stable|greatest)"
_SUPERLATIVE_OVER_A_PARENT_DUPLEX = re.compile(
    _SUPERLATIVE + r"[\w\s,'’-]{0,40}?\b(?:duplex|hybrid|pairing)\b[\w\s,'’-]{0,40}?\bparents?\b"
    r"|" + _SUPERLATIVE + r"[\w\s,'’-]{0,30}?\bparents?\b[\w\s,'’-]{0,30}?\b(?:duplex|hybrid|pairing)\b",
    re.I)

#: …unless the sentence localises it to the seam, which is what the generator actually scores. The
#: paper's own corrected phrasing ("the better of the two runs a parent can pair at the junction
#: itself") and §2.9's per-junction "most stable parent duplex" both carry one of these.
_LOCALISED_TO_THE_SEAM = re.compile(
    r"\bat (?:the|this|that|its|each) (?:same )?(?:junction|seam)\b|\bjunction itself\b"
    r"|\bat the seam\b|\bthrough (?:the|its|this) (?:whole )?(?:catalytic )?gap\b", re.I)


def test_the_free_energy_margin_is_never_called_the_best_duplex_a_parent_can_form():
    """ΔΔG°37 scores the donor-side and acceptor-side seam runs. It does not search a parent.

    ⛔ WAS A THREE-STRING BLACKLIST. "the strongest duplex a parent forms" said the same thing and
    passed. The quantifier is now read where it governs: a superlative over a parent duplex, in a
    sentence that does not localise it to the seam.
    """
    for path in (*ARTICLES, TABLES):
        offenders = [s for s in _sentences(_read(path))
                     if _SUPERLATIVE_OVER_A_PARENT_DUPLEX.search(s)
                     and not _LOCALISED_TO_THE_SEAM.search(s)]
        assert not offenders, (
            f"{os.path.basename(path)} puts a superlative over a parent duplex with nothing "
            "localising it to the seam:\n  " + "\n  ".join(o[:220] for o in offenders[:3])
            + "\n\nThe generator scores only the two runs a parent pairs AT THE JUNCTION; 87 of the "
              "190 designs pair a mature parent longer than that elsewhere, so an unlocalised "
              "superlative claims a search that was never run. See §2.5.")


def test_the_free_energy_section_says_what_the_margin_is_not_scored_against():
    """Naming the seam is not enough — the reader has to be told the mature duplexes are excluded."""
    section = _section("2.10")
    assert "at the junction itself" in section, (
        "§2.10 must say the comparison is to the runs a parent pairs AT THE JUNCTION, not to any "
        "duplex it can form.")
    assert "§2.5" in section and "not scored here" in section, (
        "§2.10 must state that the mature-parent duplexes of §2.5 are not what the free energy "
        "scores. Without that the 'every one of the 190 designs' claim reads as proteome-wide.")


# ── 2 · no universal quantifier over the parent counts ──────────────────────────────────────


@pytest.mark.parametrize("path", ARTICLES, ids=IDS)
def test_no_sentence_quantifies_universally_over_the_parent_counts(path):
    """§2.5 reports 53 / forty / 21 as parent counts that do NOT require a fully paired gap."""
    # The quantifier has to GOVERN the noun. A sentence that scopes the set first and then
    # distributes over it ("the mature-parent counts … so each is a floor") is exactly the
    # corrected form, so proximity — not mere co-occurrence — is what this looks for.
    governs = re.compile(r"\b(every|all|each|any|no other|the only)\b[\w\s,-]{0,20}?\bparent counts?\b",
                         re.I)
    offenders = [s for s in _sentences(_body(path)) if governs.search(s)]
    assert not offenders, (
        f"{os.path.basename(path)} quantifies universally over 'parent count(s)':\n  "
        + "\n  ".join(offenders[:4])
        + "\n\n§2.5 reports 53 designs with a pre-mRNA near-match, forty on the sense strand and 21 "
          "pairing all of the gap but one or two positions. None of those requires the gap paired in "
          "full, so any 'every parent count …' sentence is false of the paper's own content. Say "
          "'the headline parent counts' and name what sits outside them.")


def test_the_premrna_hit_of_section_4_3_is_placed_inside_the_wider_tallies():
    """It is sense-strand, intron–exon-spanning and one gap mismatch short: it is one of the 21."""
    section = _section("4.3")
    assert "headline parent counts" in section, (
        "§4.3 must scope the exclusion to the HEADLINE parent counts — the hit is inside §2.5's "
        "wider tallies.")
    wider = _section("2.5")
    for tally in ("53", "forty", "21"):
        assert tally in wider, (
            f"§2.5 no longer reports the wider tally '{tally}'; §4.3 places its pre-mRNA hit inside "
            "these three, so if §2.5's set has changed §4.3 is pointing at nothing. Re-derive both "
            "rather than editing this list.")
        assert tally in section, (
            f"§4.3 must name the wider tally '{tally}' that this hit does sit inside, so a reader "
            "cannot conclude the paper counted it nowhere.")


#: "excluded from EVERY near-match count" — a universal over counts that includes screen 3's, which
#: are counts of parent records and nothing else.
_EXCLUDED_FROM_ALL_NEAR_MATCH_COUNTS = re.compile(
    r"\bexcluded from\b[\w\s,'’-]{0,30}?\b(?:every|all|each|any|the)\b[\w\s,'’-]{0,25}?"
    r"\bnear-match counts?\b", re.I)

#: …and the POSITIVE half, on the same shape rather than on a phrase. §6 has to tie the exclusion to
#: ONE screen — "this screen's", "screen 1's", "the alignment screen's" all do it; the paper is free
#: to pick any of them.
_EXCLUSION_SCOPED_TO_ONE_SCREEN = re.compile(
    r"\bexcluded from\b[\w\s,'’-]{0,20}?"
    r"\b(?:this|that|its|screen\s*\d+|the (?:alignment|transcript|first) screen)(?:'s|’s)?\b"
    r"[\w\s,'’-]{0,25}?\bnear-match counts?\b", re.I)


def test_the_parent_exclusion_is_scoped_to_the_screen_that_makes_it():
    """Screen 1 excludes parent records. Screen 3's near-match counts ARE parent counts.

    Found by this file, not by the 251-claim audit: §6 said parent records were "excluded from every
    near-match count reported here", but §2.5 opens "Of the 190 designs, 53 have a near-match
    somewhere in parent pre-mRNA" — a near-match count that is nothing but parent records.

    ⛔ WAS `assert "excluded from every near-match count" not in body`. "excluded from all
    near-match counts" and "excluded from the near-match counts reported here" both said it and
    both passed. The quantifier is now read where it governs the noun.
    """
    for path in ARTICLES:
        offenders = [s for s in _sentences(_body(path))
                     if _EXCLUDED_FROM_ALL_NEAR_MATCH_COUNTS.search(s)]
        assert not offenders, (
            f"{os.path.basename(path)} excludes parent records from an unscoped set of near-match "
            "counts:\n  " + "\n  ".join(o[:220] for o in offenders[:3])
            + "\n\n§2.5 reports 53 designs with a near-match in parent pre-mRNA, from screen 3, "
              "where the parent records ARE the measurement. Scope the exclusion to the screen "
              "that makes it.")
    methods = _flat(_section("6"))
    assert _EXCLUSION_SCOPED_TO_ONE_SCREEN.search(methods), (
        "§6 must scope the parent-record exclusion to the alignment screen that makes it — some "
        "wording that ties 'excluded' to ONE screen's near-match counts rather than to the "
        "paper's. Nothing in §6 does.")
    assert "§2.5" in methods, (
        "§6 must point at §2.5, where parent near-match counts ARE reported, so the exclusion cannot "
        "be read as covering the whole paper.")


def test_the_two_nine_design_sets_are_never_left_to_look_like_one():
    """§3 discusses two DISJOINT sets of nine designs, two sentences apart, and never says so.

    Found by a blind reader of the deposit PDF, 2026-08-19. The first nine are Table 4's — the
    designs with no sense-strand near-match. The second nine are §2.5's intron–exon-spanning
    pre-mRNA sites. §2.5 states they cannot overlap: "None of the nine designs with no sense-strand
    near-match on either transcript screen carries one." Equal size, adjacent paragraphs, opposite
    meaning — a reader carries the liability onto the paper's cleanest molecules.

    This is the counted-phrase cousin of the universal-claim class: not a wrong number, a number
    whose referent is left open.
    """
    disjointness = [s for s in _sentences(_section("2.5"))
                    if re.search(r"\bnine\b", s, re.I)
                    and re.search(r"\b(none|no|neither)\b", s, re.I)
                    and "sense-strand near-match" in s]
    assert disjointness, (
        "§2.5 no longer states that the nine designs with no sense-strand near-match carry no "
        "intron–exon-spanning pre-mRNA site. That statement is the evidence the two sets of nine do "
        "not overlap, and without it the §3 passage cannot be checked at all.")
    section = _section("3")
    assert "a different nine" in section, (
        "§3 introduces a second set of nine designs two sentences after Table 4's nine, with nothing "
        "marking them as disjoint. Say 'a different nine' and point at §2.5.")
    where = section.find("a different nine")
    assert "§2.5" in section[max(0, where - 400):where + 400], (
        "§3 must cite §2.5 beside 'a different nine', where the disjointness is established, so the "
        "distinction is checkable rather than asserted.")


# ── 3 · TCF12 exon 7 has two surviving 16-mers, not one ─────────────────────────────────────


_NUMBER_WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}

#: A definite SINGULAR reference to a survivor. The corrected form ("the two 16-mers surviving")
#: puts a count between the article and the plural noun, so it cannot match.
_THE_SINGULAR_SURVIVOR = re.compile(
    r"\bthe (?:16-mer|18-mer|20-mer|design|oligonucleotide|reagent|gapmer)\b\s+"
    r"(?:surviving|that survives|which survives|clearing|that clears|to survive)\b", re.I)


def _survivors_at_tcf12_exon7():
    """Derived, not asserted: Table 4's survivors plus the design the deeper pass added.

    Table 4 prints one row per design whose hit list is complete, with a 'survives' verdict in the
    last column. §2.4 reports a seventh design that failed at the remote service on the shallow pass
    and came back clean at the deeper ceiling — it is a survivor that Table 4 has no row for.
    """
    count = 0
    for row in _read(TABLES).splitlines():
        if not row.startswith("|") or "TCF12 e7::NR4A3 e3" not in row:
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells[-1].strip("* ").lower() == "yes":
            count += 1
    body = _body()
    # ⚠ PUNCTUATION-AGNOSTIC, AND IT HAD TO BECOME SO. This regex required the design to be set off
    # by EM-DASHES. A style pass on 2026-08-19 converted paired em-dash parentheticals to brackets
    # to bring the manuscript under its em-dash density limit, which changed
    #   "one — 5′-…-3′ at *TCF12* exon 7 — with three near-matches"   into
    #   "one (5′-…-3′ at *TCF12* exon 7) with three near-matches".
    # The sentence's MEANING did not move an inch, and this DERIVATION silently dropped from two
    # survivors to one -- which then failed the count assertion below and read as a data change.
    # A derived count must not depend on which bracket character a sentence uses.
    late = re.search(
        r"one\s*[—(]\s*(5′-[ACGT]+-3′)\s*at\s+\*TCF12\*\s+exon\s+7\s*[—)]\s*"
        r"with three near-matches and none\s+on\s+the sense strand",
        " ".join(body.split()) if False else body)
    if late:
        count += 1
    return count


def test_the_number_of_surviving_16mers_at_tcf12_exon7_is_stated_correctly():
    """§2.9's gap-length contrast compares an 18-mer against the 16-mers at the same junction.

    ⛔ WAS `assert "the 16-mer surviving at that junction" not in sentence`. "the design surviving
    at that junction" and "the gapmer that survives there" both reinstate it. What is asserted now
    is that §2.9 carries NO definite-singular survivor where the derivation says two survive.
    """
    n = _survivors_at_tcf12_exon7()
    assert n == 2, (
        f"derived {n} surviving 16-mers at TCF12 exon 7; the test's premise has changed. Re-derive "
        "before editing §2.9 — Table 4's 'survives' column and §2.4's late-returning design are the "
        "two sources.")
    section = _section("2.9")
    if n != 1:
        singular = [s for s in _sentences(section) if _THE_SINGULAR_SURVIVOR.search(s)]
        assert not singular, (
            f"§2.9 refers to a survivor in the definite singular where {n} survive at TCF12 exon "
            "7:\n  " + "\n  ".join(s[:220] for s in singular[:3])
            + f"\n\nSay '{_NUMBER_WORD[n]} 16-mers'. The one Table 4 flags returns two "
              "near-matches, not three.")
    assert f"{_NUMBER_WORD[n]} 16-mers" in section, (
        f"§2.9 must say '{_NUMBER_WORD[n]} 16-mers' at TCF12 exon 7, matching what Table 4 and §2.4 "
        "between them establish.")


# ── 4 · the optional arm is placed, not unique ──────────────────────────────────────────────


def _lead_junction():
    """The junction §4.4's arm sits at, read from Table 5's first lead-reagent row.

    ⛔ NOT TYPED. The exclusivity claim is about wherever the lead reagent is; if the lead moves,
    the guard has to move with it rather than keep policing a junction nobody claims anything about.
    """
    for row in _read(TABLES).splitlines():
        m = re.match(r"\|\s*lead reagent\s*\|\s*(\w+) e(\d+)::", row)
        if m:
            return f"*{m.group(1)}* exon {m.group(2)}"
    pytest.fail("Table 5 prints no 'lead reagent' row; §4.4's arm has no derivable junction")


def test_the_optional_margin_arm_is_not_claimed_to_be_the_only_one_available():
    """Table 2 shows lower-margin registers clearing the parent screen at two other §4.1 junctions.

    ⛔ WAS `assert "and only at *EWSR1* exon 12" not in body` — one comma away from silent. "at
    EWSR1 exon 12 alone", "solely at EWSR1 exon 12" and "only at EWSR1 exon 12" all reinstate it.
    The exclusivity quantifier is now read where it governs the junction, in both word orders, and
    the junction itself is derived from Table 5.
    """
    contrary = {}
    for row in _read(TABLES).splitlines():
        m = re.match(r"\|\s*(EWSR1 e13|TCF12 e5)::NR4A3 e3\s*\|[^|]*\|\s*(\d+) of 5\s*\|", row)
        if m:
            contrary[m.group(1)] = int(m.group(2))
    assert contrary, (
        "Table 2 no longer prints a 'designs clearing the parent screen' count for EWSR1 e13 or "
        "TCF12 e5; this test's evidence base has moved.")
    assert all(v >= 2 for v in contrary.values()), (
        f"Table 2 now shows {contrary}; with one margin-3 register per junction, a count below 2 "
        "would mean no lower-margin register clears there and the exclusivity claim could return. "
        "Re-derive §4.4 before relaxing this.")

    junction = re.escape(_lead_junction())
    exclusive = re.compile(
        r"\b(?:only|solely|exclusively|uniquely)\b[\w\s,'’-]{0,25}?\bat " + junction + r"\b"
        r"|\bat " + junction + r"\b[\s,]{0,3}(?:alone|only)\b", re.I)
    offenders = [(os.path.basename(path), s)
                 for path in ARTICLES for s in _sentences(_body(path)) if exclusive.search(s)]
    assert not offenders, (
        "a sentence claims the margin contrast is available only at the lead junction:\n  "
        + "\n  ".join(f"{n}: {o[:220]}" for n, o in offenders[:3])
        + f"\n\nTable 2 shows {contrary} designs clearing the parent screen at the other two §4.1 "
          "junctions, so lower-margin registers survive there too. The arm is PLACED at the lead "
          "junction.")
    section = _section("4.4")
    assert "Table 2" in section and "not because it is the" in section, (
        "§4.4 must say why the arm sits at the lead junction rather than at the junctions Table 2 "
        "shows could carry one — otherwise the TAF15 disqualifier reads as a proof of uniqueness.")


# ── 5 · screen 5 lifts the six-transcript bound for one class only ──────────────────────────

#: A claim that a screen removes a bound. In §2.7 the antecedent is the six-transcript bound on a
#: LIABILITY CLASS, and screen 5's two-mismatch threshold cannot see the mature-parent class at all.
_REMOVES_THE_BOUND = re.compile(r"\b(?:removes|lifts|eliminates|dissolves)\s+(?:that|the)\s+bound\b",
                                re.I)
#: …so the claim has to name the class it is made for, or the class it is not made for.
_CLASS_RESTRICTION = re.compile(
    r"\b(?:class alone|classes? alone|for the pre-mRNA|only for|alone\b|stays? bounded"
    r"|remains? bounded|not for the)\b", re.I)


def test_the_genome_scan_is_scoped_to_the_class_its_threshold_can_see():
    """Screen 5 runs at ≤2 mismatches. An 11–12 bp run inside a 16-mer carries 4–5.

    ⛔ WAS `assert "The genome scan, screen 5, removes that bound." not in passage` — a blacklist
    of one sentence including its full stop. "Screen 5 lifts that bound" passed it.
    """
    section = _section("2.7")
    unrestricted = [s for s in _sentences(section)
                    if _REMOVES_THE_BOUND.search(s) and not _CLASS_RESTRICTION.search(s)]
    assert not unrestricted, (
        "§2.7 claims a screen removes the six-transcript bound without naming the class:\n  "
        + "\n  ".join(s[:220] for s in unrestricted[:3])
        + "\n\nScreen 5 runs at two mismatches, so it cannot see a mature-parent duplex of eleven "
          "or twelve base pairs — the class §2.5 calls invisible to the alignment screens at any "
          "setting. It lifts the bound for the pre-mRNA class alone.")
    assert "pre-mRNA class alone" in section, (
        "§2.7 must say screen 5 lifts the bound for the pre-mRNA class alone.")
    assert re.search(r"two\s+mismatches", section), (
        "§2.7 must give the reason — screen 5's two-mismatch threshold — not just the restriction.")


# ── 6 · the one-geometry bound names its own exception ──────────────────────────────────────

#: A universal GOVERNING the screened counts. §4.2 and Table 5 both print screened counts for the
#: 5-8-5 18-mer, so any such universal has to carry them in its exception clause.
_ALL_SCREENED_COUNTS = re.compile(r"\b(?:every|all|each)\b[\w\s,'’-]{0,20}?\bscreened counts?\b", re.I)


def test_the_one_geometry_bound_admits_the_5_8_5_counts_that_sit_outside_section_2_9():
    """§4.2 and Table 5 both print screened counts for the 5-8-5 18-mer.

    ⛔ WAS `assert "Every screened count outside §2.9" not in passage`. "All screened counts other
    than §2.9's" reinstated it. What is asserted now: a universal over the screened counts must
    carry an exception clause that names the 5-8-5 counts, in the same sentence.
    """
    tables = _read(TABLES)
    assert re.search(r"\|\s*gap-length control\s*\|.*\|\s*5-8-5\s*\|", tables), (
        "Table 5's 5-8-5 gap-length control row is gone; this test's evidence base has moved.")
    section = _section("5")
    universals = [s for s in _sentences(section) if _ALL_SCREENED_COUNTS.search(s)]
    assert universals, (
        "§5 no longer bounds the paper to one architecture over the screened counts at all. That "
        "bound is what stops a reader reading every count in the paper as a 16-mer result.")
    unqualified = [s for s in universals
                   if not (re.search(r"\bexcept|other than|apart from|besides\b", s, re.I)
                           and "5-8-5" in s)]
    assert not unqualified, (
        "§5 quantifies over the screened counts without an exception clause naming the 5-8-5 "
        "counts:\n  " + "\n  ".join(s[:240] for s in unqualified[:3])
        + "\n\n§4.2 and Table 5 both sit outside §2.9 and both print screened counts for the 5-8-5 "
          "18-mer, so the bound is falsified by the paper's own display items unless it names them.")
