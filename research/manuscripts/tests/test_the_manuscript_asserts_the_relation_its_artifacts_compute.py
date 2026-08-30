"""A claim is a QUANTITY and a RELATION. Every other guard reads the quantity. This reads the relation.

⛔⛔ THE MEASUREMENT THAT FORCED THIS (round 16 seat 3, 2026-08-22). Seventy-three predicate
inversions were applied one at a time to the journal article, each followed by the full regeneration
chain and BOTH PDF styles rebuilt, then twelve linter/generator gates and all fifty-eight test files.

    66 of the 73 survived every gate.
    44 of those 66 sit in sentences `claim_coverage.py` calls COVERED.

That second line is the important one, and it is why this file exists rather than another census
tweak: "covered" was measuring whether a NUMBER in the sentence was watched. The verb next to it was
not, anywhere. Three of the survivors are unshippable:

  · the paper's central negative inverts at ALL FOUR of its prose homes — the pins and
    `test_journal_article_numbers.py` anchor on `transcript(s)` and restart at `pair`, so inserting
    "fail to" in the gap between them satisfies both, and it renders in the built 6-page PDF;
  · every operative statement in Declarations inverts, one of them by DELETING A SINGLE WORD and
    staying word-count neutral: "Research use only, and **for** administration to any person or
    animal" — an unsafe instruction, shipped, with the page footer three lines below still saying
    the opposite because both come from the same builder;
  · the two named reagents' clearance claims invert against their own CSV rows ("neither pairs" ->
    "both pair"), which is the difference between a reagent a lab may order and one it may not.

★ THE SHAPE OF THE GUARD. Each row is a claim SITE (`span`), the relation its artifact computes
(`require`), and that relation's inverse (`forbid`). Both halves are asserted separately, because
"the right verb is present" and "no wrong verb is present" fail differently — a sentence reading
"pair or spare" satisfies the first. `span` is checked at EVERY occurrence, since the central
negative has four prose homes and round 15 shipped a fix to one of a pair more than once.

⚠ AND THE TABLE IS MUTATION-TESTED AGAINST ITSELF. A row whose `span` stops matching after a
rewording has silently stopped guarding — the exact defect this file is about — so a missing site is
an ERROR, never a skip, and every `forbid` must still match the inversion it names.
"""
from __future__ import annotations

import io
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(os.path.dirname(HERE), "aso")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")

#: (id, span, require, forbid, decided_by, an inversion the `forbid` half MUST catch)
POLARITY = [
    # ⛔⛔ THIS SPAN BOUND ONE OF THE CENTRAL NEGATIVE'S FOUR PROSE HOMES (round 17 seat B). The
    # window was `{0,160}` and the §2 site sits 161 characters from its terminal period, so
    # "pair" -> "fail to pair" there shipped with 4 linters and 983 tests green. Measured: 1 site
    # bound at {0,160}, 2 at {0,400}, and four `catalytic gap` sites have tails over 160.
    # ⚠ A WINDOW IS A DISGUISED LIST — it enumerates the sentence lengths a row happens to fit, and
    # a sentence that grows by one word leaves the guard without any signal that it did.
    ("liability-predicate",
     r"\b87\b[^.]{0,300}catalytic gap[^.]{0,400}\.",
     r"\bpair\b|\bpairs\b|\bpairing\b|\bpaired\b",
     r"\bfails? to pair\b|\bspares?\b|\bfrom pairing\b|\bunpaired\b|\bavoids?\b|\bmiss(?:es)?\b|\bclears?\b",
     "aso-parent-gap-pairing.json:corpus.n_with_parent_duplex_through_gap and the CSV column "
     "`pairs_a_wild_type_parent_through_the_gap`",
     "87 of 190 designs fail to pair a wild-type parent through the catalytic gap."),
    ("liable-definition",
     r"A design is\s+liable where[^.]{0,200}\.",
     r"liable where a wild-type parent pairs",
     r"liable where no\b|liable where none\b|fails? to pair",
     "aso-parent-null.json:method.min_duplex_bp and the same CSV column",
     "A design is liable where no wild-type parent pairs the whole gap."),
    ("precursor-class",
     r"designs carry a sense-strand near-match in parent precursor RNA[^.]{0,80}\.",
     r"pairing the gap in full",
     r"leaving the gap unpaired|not pairing the gap",
     "the precursor-RNA screen record",
     "designs carry a sense-strand near-match in parent precursor RNA, leaving the gap unpaired."),
    ("named-reagents-clear-the-cut",
     r"top gap-level margin of three:[^.]{0,260}\.",
     r"neither pairs a wild-type parent through the gap",
     r"both pair a wild-type parent through the gap",
     "the CSV rows for the two named sequences, "
     "`pairs_a_wild_type_parent_through_the_gap` = no for each",
     "top gap-level margin of three: both pair a wild-type parent through the gap."),
    ("research-use-only",
     r"\*\*Research use only[^*]{0,90}\*\*",
     r"and not for administration to any person or animal",
     r"and for administration to any person or animal",
     "the constant build_submission_pdf.py stamps into every page footer",
     "**Research use only, and for administration to any person or animal.**"),
    ("order-after-sequencing",
     r"Order from the canonical record[^#]{0,320}?sequencing\.",
     r"\bnot until the breakpoint has been established\b",
     r"\beven before the breakpoint\b|\bwithout waiting\b",
     "the ordering rule test_every_ordering_route_carries_the_same_verdict.py enforces elsewhere",
     "Order from the canonical record even before the breakpoint is known, before sequencing."),
    # ⚠ RE-ANCHORED 2026-08-23 when the Declarations were restructured to Nucleic Acid
    # Therapeutics' required template, which splits the single "Ethics approval, consent to
    # participate and consent for publication" statement into three headed ones. The RELATION is
    # unchanged; only its heading moved. ⛔ The `forbid` half now admits "or animals" as well as
    # "and animals": the cheapest inversion of this sentence is deleting the word "No", which
    # leaves the conjunction alone, and the old pattern demanded a conjunction swap the inverter
    # has no reason to make.
    ("ethics-not-applicable",
     r"\*\*Ethical considerations\.\*\*[^#]{0,220}?required\.",
     r"No human\s+subjects, human material or animals were involved",
     r"(?<!No )Human\s+subjects, human material (?:or|and) animals were involved",
     "the repository's no-wet-lab invariant",
     "**Ethical considerations.** Human subjects, human material or animals were involved, and "
     "ethics approval was required."),
    # ⚠ RE-ANCHORED 2026-08-23: "**Competing interests.**" -> the venue's required
    # "**Declaration of conflicting interest.**". Relation unchanged.
    # ⚠ RE-ANCHORED AGAIN 2026-08-25, and the wording is the VENUE'S, not a preference. Nucleic Acid
    # Therapeutics requires the heading "Author Disclosure Statement" verbatim, immediately after
    # Acknowledgments, carrying the sentence "No competing financial interests exist." So the claim
    # moved out of Statements and Declarations into a section of its own. ⛔ THE RELATION IS
    # UNCHANGED AND MUST STAY SCOPED TO *FINANCIAL* INTERESTS: the author has a non-financial one,
    # and `test_the_envelope_declares_one_interest.py` is the guard that stops this paper ever
    # denying it. A row here that read "no competing interests" would be the misstatement that guard
    # exists to catch.
    ("competing-interests",
     r"## Author Disclosure Statement[^#]{0,320}",
     r"No competing financial interests exist",
     # ⛔ THE INVERSE NEEDLE MUST NOT MATCH INSIDE ITS OWN POSITIVE. "Competing financial interests
     # exist" is a substring of "NO competing financial interests exist", and the search is
     # case-insensitive, so without the lookbehind this row reported the inversion as present at the
     # moment the paper stated the correct thing. Same trap `test_the_envelope_declares_one_interest`
     # records against its survivorship needle.
     r"(?<!No )Competing financial interests exist",
     "the author's own funding statement: he received no funding for this work",
     "## Author Disclosure Statement\n\nCompeting financial interests exist."),
    ("ai-use",
     r"\*\*Use of artificial intelligence\.\*\*[^#]{0,140}",
     r"A large language model \(Claude, Anthropic\) was used",
     r"No large language model was used",
     "the repository's own AI-use record",
     "**Use of artificial intelligence.** No large language model was used."),
    # ⛔ THE `deposit-not-yet-posted` ROW WAS REMOVED 2026-08-25 WITH ITS SUBJECT. It anchored on
    # "inside that deposit; it is not posted as a preprint", a sentence about the EXTENDED REPORT's
    # preprint status. That document left the gate that day and the Data availability statement was
    # rewritten to cite the archive itself, so the phrase the row bound to no longer exists — and a
    # polarity row whose anchor cannot be found is inert, which is exactly what this module's own
    # `test_every_polarity_row_still_finds_the_claim_it_guards` exists to catch.
    # ⚠ AND THE FORWARD CASE IS NOT COVERED BY ANYTHING. A Qeios preprint of the journal article is
    # the stated next step; once one is posted the paper has to declare it, and a claim about the
    # ARTICLE's preprint status will need its own row. This is not that row rewritten — it is a
    # different claim about a different document, and writing it before the preprint exists would
    # be guarding a sentence nobody has written.
    ("coverage-is-not-a-measurement",
     r"That prices which published junctions[^.]{0,220}\.",
     r"it is not a coverage measurement, no patient having been screened",
     r"it is a coverage measurement, patients having been screened",
     "fusion-junction-aso-reagent-coverage.json:_what_this_is_not[0]",
     "That prices which published junctions are modelled: it is a coverage measurement, "
     "patients having been screened."),
    ("no-prior-nr4a3-design",
     r"(?:No|Such)\s+(?:such design|a design) is reported[^.]{0,180}\.",
     r"No\s+such design is reported",
     r"Such\s+a design is reported",
     "fusion-junction-aso-priorart-evidence.json, the what-this-does-not-establish field",
     "Such a design is reported in the prior literature."),
    ("backbone-is-phosphorothioate",
     r"Both reagents are phospho[a-z]+",
     r"phosphorothioate",
     r"phosphodiester",
     "the sequences CSV header: 'every internucleoside linkage is a phosphorothioate'",
     "Both reagents are phosphodiester throughout."),
    ("acceptor-reagents-not-interchangeable",
     r"A reagent selected for one acceptor is[^.]{0,60}\.",
     r"is\s+not valid for the other",
     r"is\s+valid for the other",
     "the CSV: the exon-2 sequences differ from the exon-3 sequences",
     "A reagent selected for one acceptor is valid for the other."),
    # ⛔⛔ A CLINICAL FACT UNDER A REAL PMID INVERTS AS FREELY AS ANY OTHER PREDICATE (round 16
    # seat 3). "responds poorly" -> "responds well" states the opposite of the cited source while
    # the citation, the superscript and the PMID anchor all stay put — and CLAUDE.md §7 is explicit
    # that claim STRENGTH is orthogonal to citation PROVENANCE, so a hedge-checking linter cannot
    # see it. This is the one clinical claim the condensed paper makes in its own voice.
    # ⚠ `decided_by` here is a CITATION, not an artifact, and that is the honest description: the
    # guard binds the polarity to the source, and the source is what makes the claim checkable by a
    # reader. It cannot verify the source says it; nothing available here can.
    # ⚠ `\s+` between every word: the sentence wraps mid-phrase in the source ("cytotoxic" ends
    # line 68, "chemotherapy" opens line 69), and a literal-space pattern reports the claim missing
    # when it is simply typeset over two lines.
    ("chemotherapy-response",
     r"The\s+disease\s+responds[^.]{0,140}chemotherapy",
     r"responds\s+poorly\s+to\s+conventional\s+cytotoxic\s+chemotherapy",
     r"responds\s+well\b|responds\s+favourably\b|is\s+responsive\s+to\b|responds\s+strongly\b",
     "PMID:41055792, the source cited at that sentence",
     "The disease responds well to conventional cytotoxic chemotherapy"),
    ("margin-is-the-shorter-side",
     r"gap-level margin is the count of junction-unique bases[^.]{0,90}\.",
     r"on\s+the shorter side of the breakpoint",
     r"on\s+the longer side of the breakpoint",
     "the CSV column gap_level_margin, computed on the shorter side",
     "gap-level margin is the count of junction-unique bases on the longer side of the "
     "breakpoint."),
    # ─────────────────────────────────────────────────────────────────────────────────────────
    # ⛔⛔ ROUND 10's GUARD-COVERAGE AUDIT: 34 OF 42 SINGLE-SENTENCE MUTATIONS SHIPPED GREEN, AND
    # ALL FIVE LINTERS RETURNED rc=0 ON ALL 42 (research/manuscripts/aso/
    # fusion-junction-aso-guard-coverage-audit.md, 2026-08-27). Its structural finding is the
    # reason the nine rows below are HERE rather than in a new module: this file is the only
    # instrument in the repository that reads VERBS, its sixteen rows accounted for six of the
    # eight catches, and every one of the 34 survivors fell outside their spans. Widening the
    # table is the fix; a new file would have been a second list to remember.
    # ★ AND EVERY ROW BELOW BINDS THE `.md`, WHICH IS THE POINT. The audit's MISCOVERED A is a
    # guard that reads the built PDF's text layer and therefore could not see its own sentence:
    # two-column typesetting interleaves the columns, so `none has been synthesised` occurs ZERO
    # times in the pdfminer text of a paper that states it (measured — the extraction reads
    # "…and none has been record, fusion-junction-aso-sequences.csv, … by RNA sequencing. tested.
    # Order canonical"). A PDF-text guard on a scattered clause cannot be tightened into a
    # working one; the source is where the clause exists as a clause, so the source is what these
    # rows read. The delivered-document direction is not lost — it is held by the stale-build-stamp
    # guards, which refuse a commit whose PDF was not rebuilt from this same `.md`.
    # ─────────────────────────────────────────────────────────────────────────────────────────
    # ⛔⛔ THE SYNTHESIS DENIAL — audit item UNGUARDED 1 and MISCOVERED A, THE WORST HOLE IT FOUND.
    # `test_the_paper_states_what_its_own_claims_depend_on.py::REQUIRED["that nothing was
    # synthesised or tested"]` is named for this sentence and does not bind it, for TWO
    # independent reasons measured that day: its pattern is satisfied by the Table 1 caption
    # constant at `research/manuscripts/aso_journal_tables.py:194` ("Nothing here has been
    # synthesised or tested…"), which is a GENERATED STRING and not the paper; and even with that
    # branch gone the clause is unmatchable in the PDF text layer. The seat DELETED the clause
    # from the `.md`, rebuilt the real PDF (BUILD_RC=0) and re-ran the module: green, on a paper
    # that no longer said it. This row is the binding — deletion trips the missing-site ERROR,
    # inversion trips `forbid`, and both read the source the author edits.
    ("nothing-synthesised-or-tested",
     r"Every sequence here is a research reagent[^.]{0,140}\.",
     r"none has been synthesi[sz]ed or tested",
     r"(?<!none )has been synthesi[sz]ed|have been synthesi[sz]ed|w(?:as|ere) synthesi[sz]ed",
     "this repository has no wet lab: no protocol, instrument record or assay result exists for "
     "any sequence in fusion-junction-aso-sequences.csv, and the whole submission is the "
     "in-silico half of a first step",
     "Every sequence here is a research reagent for laboratory investigation only, and each has "
     "been synthesised and tested."),
    # ⛔ THE DECLARATIONS BLOCK — audit item UNGUARDED 4. `SAFETY_CLAUSES` below covers exactly two
    # of the six operative statements (no-administration, no-human-subjects) and the `POLARITY`
    # rows above cover two more (ethics, competing interests). The remaining three sat beside them
    # reading nothing: `grep -n "funding\|participants\|individual person\|consent"` over
    # `research/manuscripts/tests/*.py` and `research/manuscripts/lint_*.py` returned three hits,
    # all of them comments. Each inverts into a fabricated human-subjects or funding claim in a
    # document going to a journal under a real name and ORCID, and each inversion is CHEAPER than
    # the ones this file already catches — deleting the word "No" is enough for two of the three.
    ("consent-to-participate",
     r"\*\*Consent to participate\.\*\*[^*]{0,140}",
     r"No participants were enrolled",
     r"(?<!No )[Pp]articipants were enrolled|participants were recruited|participants gave",
     "this repository enrolled nobody: there is no protocol, no consent form and no participant "
     "record anywhere in it, and no wet-lab work of any kind",
     "**Consent to participate.** Not applicable. Participants were enrolled."),
    ("no-individual-patient-data",
     r"\*\*Consent for publication\.\*\*[^*]{0,180}",
     r"contains no data from any individual person",
     r"contains data from (?:any |an )?individual person|contains individual patient data",
     "every clinical number in the submission is a published aggregate under a PMID "
     "(research/manuscripts/aso/fusion-junction-aso-references.json); no record of any individual "
     "person exists in this repository, and AGENTS.md's medical-integrity rule forbids one",
     "**Consent for publication.** Not applicable. The manuscript contains data from individual "
     "persons."),
    ("no-external-funding",
     r"\*\*Funding statement\.\*\*[^*]{0,140}",
     r"No external funding",
     r"external funding was received|received external funding|funded by a grant|"
     r"supported by (?:a )?grant",
     "the repository's own funding record: no grant, contract or institutional support of any "
     "kind was received for this work",
     "**Funding statement.** External funding was received by the author."),
    # ⛔⛔ THE CONDEMNED ONE-SLIDE DESIGN — audit item UNGUARDED 6, AND THE ONE THAT COULD BE ACTED
    # ON. This sentence sits immediately after the paper prints `5′-AGGGCATATCTTGTGT-3′`, a
    # sequence whose own CSV row reads `do_not_order` = "DO NOT ORDER — pairs its whole catalytic
    # gap against a wild-type parent gene at the ten-base-pair criterion" while its one-base slide
    # `GGGCATATCTTGTGTG` is the named, orderable *TAF15* reagent. Inverted — "Either may be
    # substituted for the other" — the paper tells a laboratory holding both strings that it may
    # order the condemned one. The span is anchored at BOTH ends on purpose: a reworded warning
    # leaves the site unmatched, which is an ERROR here rather than a silent pass.
    ("condemned-slide-is-not-a-substitute",
     r"AGGGCATATCTTGTGT[^#]{0,220}?substituted for the other\.",
     r"\bNeither may be substituted for the other\b",
     r"\bEither may be substituted\b|\bmay be substituted for either\b|\bmay substitute for\b",
     "fusion-junction-aso-sequences.csv: AGGGCATATCTTGTGT carries a do_not_order verdict and "
     "names GGGCATATCTTGTGTG as 'a single-base slide; orderable', and "
     "aso-parent-gap-pairing.json:per_design gives it longest_parent_duplex_bp_through_gap = 11 "
     "with counts_as_liability = true",
     "AGGGCATATCTTGTGT-3′ is one slide from the *TAF15* reagent and pairs 11 base pairs of "
     "wild-type *NR4A3* through its whole catalytic gap. Either may be substituted for the "
     "other."),
    # ⛔ FIGURE 1's TWO SCOPE SENTENCES — audit item UNGUARDED 8. The figure draws one 16-mer across
    # *EWSR1* e12, *TAF15* e11 and *FUS* e10, and the legend's two scope clauses are the only
    # things stopping a reader taking the *TAF15* exon-11 row for an orderable reagent at a
    # patient junction. The audit searched test_aso_figure_provenance.py,
    # test_aso_figure_chain_is_complete.py, test_figure_text_carries_no_markdown.py and
    # test_display_items_are_cited_in_order.py: all four check provenance, rendering or ordering,
    # and none reads the legend's claims. Both inversions shipped green.
    ("figure1-one-of-three-is-a-reported-junction",
     r"\*\*Figure 1\.[^*]{0,220}\*\*",
     r"only one of the three is a junction any patient is reported to carry",
     r"all three are junctions|each of the three is a junction|"
     r"three of the three|all three of them are junctions",
     "aso-per-junction-table.json:junctions[].clinical_tier — EWSR1_e12__NR4A3_e3 is "
     "published_exon_resolved_breakpoint, TAF15_e11__NR4A3_e3 is "
     "partner_published_this_exon_not_reported and FUS_e10__NR4A3_e3 is "
     "no_published_exon_resolved_breakpoint",
     "**Figure 1. One 16-mer spans three partners' breakpoints, and all three are junctions "
     "patients are reported to carry.**"),
    ("figure1-no-reagent-at-the-taf15-exon-11-row",
     r"The \*TAF15\* row is exon 11[^#]{0,280}?named at it\.",
     r"No reagent is named at it",
     r"\bAn? reagent is named at it\b|\bone reagent is named at it\b|"
     r"\bthe reagent named at it\b",
     "fusion-junction-aso-sequences.csv: no row carries junction TAF15_e11__NR4A3_e3; the named "
     "TAF15 reagent is at TAF15_e6__NR4A3_e3",
     "The *TAF15* row is exon 11 — a different junction from Table 1's *TAF15* exon 6 reagent, "
     "and one of the two further breakpoints the *EWSR1* reagent also spans. A reagent is named "
     "at it."),
    # ⛔ THE THREE CLEAN DESIGNS — audit item UNGUARDED 10, and the sentence CLAUDE.md §6 quotes as
    # the worst of the thirteen inversions that reached `origin/main` on 2026-08-27: "Three designs
    # clear every screen, each at a junction patients are reported to carry, which makes them
    # candidates rather than mechanism controls" is the exact reverse of the sentence, in the paper
    # whose whole value is not overclaiming. `test_aso_submission_numbers.py::
    # test_the_discussion_recommends_the_two_published_junctions` holds the same relation against
    # the same artifact — but its `PAPER` is the EXTENDED REPORT, so the journal article's copy is
    # one of a pair with nothing on this side of it.
    ("three-clean-designs-are-mechanism-controls",
     r"Three designs clear every screen[^.]{0,200}\.",
     r"none at a junction any patient is reported to carry",
     r"each at a junction patients are reported to carry|"
     r"at a junction patients are reported to carry|"
     r"candidates rather than mechanism controls",
     "aso-per-junction-table.json:junctions[].clinical_tier — the five junctions tiered "
     "published_exon_resolved_breakpoint are EWSR1 e12/e13, TAF15 e6, TCF12 e5 and TFG e7, and "
     "none of the three designs clearing every screen is tiled at one of them",
     "Three designs clear every screen applied here, each at a junction patients are reported to "
     "carry, which makes them candidates rather than mechanism controls."),
    # ⛔ THE AI-USE PROVENANCE SENTENCE — audit item UNGUARDED 2 / MISCOVERED F, AND A WINDOW THAT
    # WAS SEVENTY CHARACTERS SHORT. `POLARITY["ai-use"]` above binds the DISCLOSURE (a model was
    # used); the sentence that says the citations are real is a different claim and sits outside
    # its span — measured at the pin, the span ends 174 characters into the section and this
    # sentence begins at 244. Widening that row's window would have been the "a window is a
    # disguised list" mistake this file's own first comment records, so the claim gets its own
    # site anchored on its own subject.
    # ⚠ AND `lint_citations` DOES NOT COVER THIS. It checks the PROVENANCE of identifiers; this
    # sentence is the paper's STATEMENT that they were retrieved rather than generated, which is
    # CLAUDE.md §7's core invariant said to the reader. Inverted, the paper admits fabricated
    # citations while every PMID in it still resolves and every linter stays green.
    # ⚠ PATTERN AND `decided_by` BOTH CORRECTED 2026-08-30, ROUND 21, AND FOR TWO SEPARATE REASONS.
    # (1) The sentence changed: it said every record "was retrieved from PubMed", which UNDERSTATES
    # and mis-names the provenance. The citations seat measured it — journal-reference-authors.json
    # records "Europe PMC and Crossref fetch products on branch literature-cache", all 23 printed
    # author lists come from Europe PMC, and reference 1's AUTHOR COUNT (the field deciding whether
    # "et al." prints) comes from Crossref DELIBERATELY, because PubMed's pre-1996 MEDLINE record
    # caps that list at ten. The repository went past PubMed on purpose and the Declaration denied
    # it. The direction this row guards — retrieved, never model-written — is unchanged and is what
    # the widened pattern still requires.
    # (2) The old `decided_by` named fusion-junction-aso-2026-citation-resolution.json as "the
    # retrieval record lint_citations reads". Both halves were wrong: that file resolves three
    # PMIDs, NONE of which appears in this article, and lint_citations does not read it specifically
    # — it scans every tracked .json for anchors. A row whose stated witness cannot see the claim is
    # a row nobody can check, even while its direction test works.
    ("citation-provenance-statement",
     r"Every reference's bibliographic record was[^.]{0,240}\.",
     # ⛔ (3) THE SOURCE LIST IS REQUIRED, NOT OPTIONAL — round 22's regression seat caught this
     # exact defect in round 21's own repair, one round later. Written first as
     # `(?:, Europe PMC or Crossref)?`, the optional group accepted the bare "retrieved from
     # PubMed" — the sentence the repair exists to replace, and the one
     # journal-reference-authors.json contradicts. pinned-figures.json stated the correct policy
     # in the very same commit ("The new pattern will not match the old wording, which is the
     # point: reverting the prose fails the pin"), so one repair closed the revert path and this
     # one left it open. Required now: reverting the Declaration fails here.
     r"retrieved from PubMed, Europe PMC or Crossref rather than written from model output",
     r"written from model output rather than retrieved|"
     r"no citation was checked|generated from model output",
     "lint_citations.py, which anchors every prose identifier to a tracked fetch product (46 of 46 "
     "in this article), plus journal-abbreviations.json and journal-reference-authors.json, the "
     "PubMed/Europe PMC/Crossref fetch products the printed fields are taken from; and CLAUDE.md "
     "§7's never-write-an-identifier-from-recollection rule",
     "Every reference's bibliographic record was written from model output rather than retrieved "
     "from PubMed, and no citation was checked against a retrieved record."),
    # ─────────────────────────────────────────────────────────────────────────────────────────
    # ⛔⛔ ROUND 10's AUDIT ITEMS G AND E, AS DIRECTIONS RATHER THAN AS A WIDER FILE LIST. Both
    # findings are one instrument reading one document: `test_universal_claims_are_scoped_to_what_
    # was_measured.py` bound the EXTENDED REPORT alone (item G) and
    # `test_the_exon2_reading_stands_without_an_unpublished_sequence.py`'s sequencing requirement
    # was a keyword that survives its own negation (item E). Both of those modules were repaired in
    # place — the first now scans every submitted document, the second reads the negation standing
    # on the verb. What neither repair can supply is what THIS file supplies: the audit's three
    # surviving inversions in the journal article are open quantifiers whose defect is DIRECTION,
    # and a scope guard that reads quantifier shape cannot tell "none 3′ of exon 3" from "several".
    # ★ SO THE DIRECTION LIVES HERE, WHERE THE VERBS ARE READ, AND THE SHAPE LIVES THERE. Two
    # instruments, one claim each, neither a copy of the other.
    # ─────────────────────────────────────────────────────────────────────────────────────────
    # ⛔ THE ACCEPTOR BOUND — audit mutation 16a, "none 3′ of exon 3" -> "several", green. This is
    # the sentence that says why the panel designs nothing downstream of exon 3: not that the
    # position was screened and rejected, but that no patient is reported there. Inverted, the
    # paper reports patients at acceptors the census does not contain, and the reason the panel
    # stops where it stops becomes a claim about the disease that its own source contradicts.
    ("no-acceptor-3-prime-of-exon-3",
     r"across the exon-resolved \*NR4A3\* junctions retrieved here[^#]{0,240}?reported there\.",
     r"none 3′ of exon 3",
     r"\b(?:several|some|others?|many|two|three|four|five|a few|one|both)\s+3′ of exon 3",
     "lit-targets-aso-breakpoint-census.json:junction_census — every acceptor it records is "
     "NR4A3 exon 3, NR4A3 exon 2 or the cryptic exon in NR4A3 intron 2, and it records none "
     "3′ of exon 3",
     "across the exon-resolved *NR4A3* junctions retrieved here every acceptor is exon 2, exon 3, "
     "or a cryptic exon in intron 2, several 3′ of exon 3, so nothing is designed there because "
     "no patient is reported there."),
    # ⛔ WHERE THE TEST ARTICLES STOP — audit mutation 16b, "ends at someone culturing cells" ->
    # "reaches an animal model", green. It is the last sentence of the limits paragraph and it
    # prices every downstream claim in the paper: an in-vivo result would change what a reader may
    # conclude about delivery, which the sentence beside it calls unsolved.
    # ⚠ `decided_by` HERE IS THE PAPER'S OWN TEST-ARTICLE SECTION AND THE TWO SOURCES IT CITES,
    # which is the honest description — the same shape as `chemotherapy-response` above. Nothing
    # available in this repository can verify what those sources contain; what this row binds is
    # that the paper does not claim more than the section two pages earlier describes.
    ("test-articles-end-at-cell-culture",
     r"Every source of a test article named here[^.]{0,120}\.",
     r"ends at someone culturing cells",
     r"reaches an animal model|reaches a mouse|ends at an animal|goes on to an animal"
     r"|reaches a xenograft|ends in a patient|reaches the clinic",
     "the paper's own Test articles section: three engineered constructs expressed in a "
     "heterologous background (PMID:31020999) and two patient-derived cell lines reported with "
     "doubling times (PMID:36316541). No animal model is named anywhere in the submission, and "
     "this repository has no wet lab",
     "Every source of a test article named here reaches an animal model."),
    # ⛔ HOW MUCH OF THE CITED WORKFLOW THIS WORK DOES — audit mutation 16c, "performs the
    # in-silico half of the first step" -> "performs all five of those steps", green. The five
    # steps are the cited source's recommendations; claiming all five claims cell-type activity
    # work, in-vitro verification and risk management this project has never done, in the same
    # paragraph that introduces them. It is the paper's scope sentence in the Introduction.
    ("in-silico-half-of-the-first-step",
     r"This work performs[^;]{0,140};",
     r"the in-silico half of the first step",
     r"all five of those steps|all five steps|each of the five steps|the whole of the first step"
     r"|the first three steps|steps one to",
     "the Methods' own first sentence, 'All analyses are computational and use public data; no "
     "laboratory work was performed' — steps two to five of the cited recommendations "
     "(PMID:39912803) are laboratory steps",
     "This work performs all five of those steps and stops there;"),
    # ⛔⛔ THE SEQUENCING REQUIREMENT, METHODS COPY — audit item MISCOVERED E and UNGUARDED 5, and
    # the second half of that repair. `test_the_exon2_reading_stands_without_an_unpublished_
    # sequence.py` now rejects a negation standing on the verb at EVERY copy of the phrase, which
    # is the general defence; this row binds THIS site's relation to the ordering rule, so a
    # rewrite that keeps the phrase and drops the requirement is caught as a missing site rather
    # than passing as a mention. The Declarations copy is already held by `order-after-sequencing`
    # above — these are the two copies the audit measured as able to stand in for each other.
    ("breakpoint-sequenced-before-order",
     # ⚠ RE-ANCHORED 2026-08-28 (round 18), AFTER CHECKING THE MEANING FIRST. The claim this row
     # guards — sequence the breakpoint before ordering — is untouched. What changed is the
     # subordinate reason clause: "every design here being specific to the exon pair it was tiled
     # at" was a universal the panel refutes (nine of its 176 distinct sequences sit at more than
     # one exon pair, the lead reagent among them), so the sentence no longer ends at "tiled at".
     # The requirement is if anything strengthened by the correction: a sequence that spans three
     # partners' breakpoints cannot tell you which junction the sample carries.
     r"One requirement is upstream of all of them:[^#]{0,420}?match at more than one\.",
     r"must be established at nucleotide resolution by RNA sequencing before any oligonucleotide "
     r"is ordered",
     r"need not be established|must not be established|need not be sequenced"
     r"|no design here being specific|without RNA sequencing|after any oligonucleotide is ordered",
     "fusion-junction-aso-sequences.csv, whose every row is specific to one exon pair, and the "
     "ordering rule test_every_ordering_route_carries_the_same_verdict.py enforces across the "
     "routes a laboratory can order from",
     "One requirement is upstream of all of them: the breakpoint of the test article need not be "
     "established at nucleotide resolution by RNA sequencing before an oligonucleotide is "
     "ordered, no design here being specific to the exon pair they were tiled at, and nine of "
     "the panel's 176 distinct sequences match at more than one."),
]


def _article():
    """The article with its line wrapping collapsed.

    ⛔ EVERY SPAN BELOW IS WRITTEN WITH ORDINARY SPACES, AND THE SOURCE WRAPS MID-PHRASE. The
    chemotherapy sentence breaks between "cytotoxic" and "chemotherapy"; without this, that row
    reported its claim MISSING on a correct paper, and a reflow of any other paragraph would do the
    same to its row. A missing span is an ERROR here — correctly, since a row that stops matching
    has stopped guarding — so the failure would have been loud but wrong, and a gate that reds on
    honest input gets loosened. Normalising once is cheaper than anchoring sixteen patterns.
    """
    return re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())


def _errors(text):
    """Every polarity violation, at every occurrence of every claim site."""
    bad = []
    for cid, span, require, forbid, src, _inv in POLARITY:
        hits = list(re.finditer(span, text, re.I | re.S))
        if not hits:
            bad.append(f"{cid}: the claim site is not in the document at all")
            continue
        for m in hits:
            win = m.group(0)
            if not re.search(require, win, re.I):
                bad.append(f"{cid}: the relation is NOT asserted at its own site — decided by {src}")
            if re.search(forbid, win, re.I):
                bad.append(f"{cid}: the INVERSE of the relation is asserted — decided by {src}")
    return bad


def test_no_claim_asserts_the_inverse_of_what_its_artifact_computes():
    """⛔ THE VERB IS THE CLAIM. 66 of 73 inversions shipped green before this existed."""
    bad = _errors(_article())
    assert not bad, (
        "the journal article states a relation its own artifact contradicts:\n  "
        + "\n  ".join(bad)
        + "\n\nEvery number in the sentence can be correct while the verb states the opposite "
          "result. Check the artifact named on each line and fix the SENTENCE — never the row, "
          "unless the artifact itself changed.")


@pytest.mark.parametrize("row", POLARITY, ids=[r[0] for r in POLARITY])
def test_every_polarity_row_still_finds_the_claim_it_guards(row):
    """⛔⛔ A ROW WHOSE SITE STOPPED MATCHING HAS SILENTLY STOPPED GUARDING.

    This is the defect the whole file is about, one level up: a reworded sentence slips out of its
    own `span`, the row finds nothing, and a table of fifteen guards quietly becomes a table of
    fourteen. A missing site is an ERROR, never a skip.
    """
    cid, span, _req, _forbid, src, _inv = row
    assert re.search(span, _article(), re.I | re.S), (
        f"{cid}: no sentence in the journal article matches this row's claim site, so the row is "
        f"guarding nothing. Either the claim was REWORDED — re-anchor `span` to it — or it was "
        f"REMOVED, in which case {src} no longer has a home in the paper and that is the finding.")


@pytest.mark.parametrize("row", POLARITY, ids=[r[0] for r in POLARITY])
def test_every_forbid_pattern_still_catches_the_inversion_it_names(row):
    """⛔ AN ALTERNATION NOBODY MATCHES IS AN ALTERNATION THAT HAS STOPPED GUARDING.

    Each row carries the inverted sentence it exists to reject. Asserting against that string rather
    than against the live document is what keeps the check honest as the paper is reworded: the
    `forbid` half is never exercised by a clean document, so nothing else would ever notice it going
    stale. This is the lesson the title guard learned when `\\bpairs?\\b` was found matching the unit
    inside "ten-base-pair" rather than the verb.
    """
    cid, _span, require, forbid, _src, inverted = row
    assert re.search(forbid, inverted, re.I), (
        f"{cid}: this row's `forbid` pattern no longer matches the inversion it names, so an "
        f"inverted claim would pass:\n  forbid : {forbid}\n  misses : {inverted!r}")
    assert not re.search(require, inverted, re.I) or cid == "liability-predicate", (
        f"{cid}: the inversion example also satisfies `require`, so the two halves do not "
        f"discriminate:\n  require: {require}\n  example: {inverted!r}")


def test_the_polarity_table_actually_fires_on_an_inverted_document():
    """⛔⛔ THE POSITIVE CONTROL. Everything above argues from a GREEN document; prove it can go red.

    Substituting each row's own inversion into the article must produce at least as many errors as
    rows substituted. Without this, a `span` that silently stopped matching would leave the main
    check passing on a paper it is no longer reading.
    """
    text = _article()
    fired = 0
    for cid, span, _req, _forbid, _src, inverted in POLARITY:
        m = re.search(span, text, re.I | re.S)
        if not m:
            continue
        mutated = text[:m.start()] + inverted + text[m.end():]
        if any(e.startswith(cid) for e in _errors(mutated)):
            fired += 1
    assert fired == len(POLARITY), (
        f"only {fired} of {len(POLARITY)} polarity rows fire when their own inversion is "
        "substituted into the article. A row that cannot catch the sentence it names is inert, and "
        "the main check above is passing on claims nothing reads.")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# ⛔⛔ SCOPE BY THE PROPERTY, NOT BY A LIST (round 17 seat B, 2026-08-23).
#
# Seat B's shape verdict, measured over 33 mutations: "fixes bound to a PREDICATE held; every fix
# whose scope is a LIST regressed at a sibling" — ARTICLE (1 of 3), DOCUMENTS (4 of 6), PAPERS
# (2 of 4), one span (1 of 4 homes), the re-anchor messages (5 of 7), the early-return repair
# (1 of 12). Six of eleven, AND IN THREE THE SIBLING WAS NAMED IN THE FIX'S OWN COMMENT — including
# a check headed "⛔ EVERY DOCUMENT, NOT THE TWO OBVIOUS ONES" that enumerated four and missed two.
#
# ★ A list is a thing somebody must remember to extend; a predicate is not. So the safety-critical
# Declarations lines are not checked against a named set of files — every document that CONTAINS the
# clause must state it correctly, which is a rule that extends itself to a document added tomorrow.
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: (what it is, the clause that puts a document in scope, the form it must take, the inversion)
SAFETY_CLAUSES = [
    ("the no-administration instruction",
     re.compile(r"administration to any person or animal", re.I),
     re.compile(r"not for administration to any person or animal", re.I),
     "a document telling a reader a research reagent MAY be administered is the one sentence in "
     "this submission that could hurt somebody"),
    ("the no-wet-lab statement",
     re.compile(r"human\s+subjects, human material", re.I),
     re.compile(r"No human\s+subjects, human material (?:or|and) animals were involved", re.I),
     "this repository has no wet lab; a document claiming human subjects were involved is a "
     "fabricated ethics claim"),
]


def _aso_documents():
    """Every markdown document in the submission directory. Derived, never enumerated."""
    found = sorted(f for f in os.listdir(ASO) if f.endswith(".md"))
    assert found, f"no markdown documents under {ASO}, so this guard reads nothing"
    return found


@pytest.mark.parametrize("clause", SAFETY_CLAUSES, ids=[c[0] for c in SAFETY_CLAUSES])
def test_every_document_stating_a_safety_clause_states_it_the_right_way_round(clause):
    """⛔ THE DOCUMENT SET IS WHATEVER CONTAINS THE CLAUSE, SO A NEW DOCUMENT IS IN SCOPE BY DEFAULT."""
    label, in_scope, correct, why = clause
    checked, wrong = [], []
    for name in _aso_documents():
        text = re.sub(r"\s+", " ", io.open(os.path.join(ASO, name), encoding="utf-8").read())
        for m in in_scope.finditer(text):
            window = text[max(0, m.start() - 120):m.end() + 40]
            checked.append(name)
            if not correct.search(window):
                wrong.append((name, window.strip()[-150:]))
    assert checked, (
        f"no document in {os.path.basename(ASO)} states {label}, so this guard is vacuous. Either "
        "the clause was reworded everywhere at once, or it was dropped — both are findings.")
    assert not wrong, (
        f"{len(wrong)} document(s) state {label} the wrong way round. WHY THAT MATTERS: {why}.\n  "
        + "\n  ".join(f"{n}: …{w}" for n, w in wrong))


def test_the_safety_clause_scope_is_derived_and_catches_more_than_one_document():
    """⛔ A DERIVED SCOPE THAT RESOLVES TO ONE FILE IS A LIST WITH EXTRA STEPS.

    The defect this replaces was a guard reading the journal article while the same clause shipped
    in the extended report and the supplementary information. If the derivation ever collapses to a
    single document, it has stopped doing the thing it was written for.
    """
    hits = {name for name in _aso_documents()
            if SAFETY_CLAUSES[0][1].search(
                re.sub(r"\s+", " ", io.open(os.path.join(ASO, name), encoding="utf-8").read()))}
    assert len(hits) >= 3, (
        f"the no-administration clause was found in {len(hits)} document(s): {sorted(hits)}. It is "
        "carried by the journal article, the extended report, the supplementary information and the "
        "deposit tables; a derivation finding fewer has stopped reading the siblings, which is the "
        "exact regression this section exists to prevent.")
