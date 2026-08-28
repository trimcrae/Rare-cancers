#!/usr/bin/env python3
"""Stratified claim audit: sample a finished manuscript's sentences BY CLAIM TYPE, and say what a
verifier would have to reproduce or re-find for each. It never says whether the claim is supported.

⛔⛔ WHY THIS EXISTS — SOMEBODY ELSE MEASURED OUR BLIND SPOT ON THEIR OWN SYSTEM.

Kosmos (Edison Scientific) had 102 statements from 3 reports independently classified
Supported/Refuted by expert scientists who had to REPRODUCE THE ANALYSIS OR FIND THE LITERATURE
SUPPORT, and reported the rate stratified by statement type:

    data-analysis claims    85.5% supported
    literature claims       82.1% supported
    interpretation claims   57.9% supported      <- the one that collapses

(research/method-watch-autonomy-prior-art-2.md §4.1, SEARCH-grade, arXiv:2511.02824, arxiv.org
blocked at this sandbox's egress.) Named failure modes: conflating statistically significant with
scientifically valuable, excessively strong claims, unorthodox invented metrics.

⛔ READ AGAINST THIS REPOSITORY'S GATES THAT IS UNCOMFORTABLE IN A SPECIFIC WAY.
`lint_citations.py` instruments the 82.1% axis — does the cited record exist and carry the fields we
attribute to it. `lint_claims.py` R1–R5 instruments claim STRENGTH — verb discipline and the
never-imply bans. Neither instruments the 57.9% axis, because an interpretive sentence carries no
citation to resolve and no number to pin: "that mismatch is a property of how the panel was
selected, not of the disease" is grammatical, hedged, uncited, numberless, and either follows from
the artifacts or does not. This repository has already recorded the same orthogonality twice from
the other direction — a hedged sentence on a fabricated PMID passes `lint_claims` (CLAUDE.md §7),
and claim STRENGTH is orthogonal to claim DIRECTION (CLAUDE.md §6, the 13 inverted claims). This is
a third axis of the same gap.

★★ WHAT THIS MODULE IS, AND THE ONE LINE IT MUST NOT CROSS.

It is the SAMPLING half of Kosmos's protocol and nothing else: enumerate the manuscript's claim
sentences, assign each the type that decides WHAT A VERIFIER WOULD HAVE TO DO, draw a reproducible
stratified sample, and emit the evidence handle for each draw. The classification of
Supported / Refuted / Unverifiable is deliberately NOT here and must not be added.

⛔ A TOOL THAT SCORES ITS OWN PAPER IS THE FAILURE MODE THIS AUDIT EXISTS TO CATCH. The Kosmos
number is 57.9% *because independent expert scientists went and reproduced the analysis*, not
because the system re-read its own prose and agreed with it. An automated support verdict here
would be the author's own model grading the author's own sentences on the axis where the author's
own model is measured to be least reliable — and it would produce a comfortable number with no
information in it. The paper the survey cites states outright that no automated method reliably
evaluates whether a claim is accurate, novel and significant. So `verdict` is emitted as `null`,
`--tally` will only ever do arithmetic over verdicts a human or a blind seat WROTE, and there is a
guard test asserting this module emits no verdict.

★ THE TYPE IS A STATEMENT ABOUT THE VERIFIER'S WORK, NOT ABOUT THE SENTENCE'S SUBJECT.

    LITERATURE      the sentence rests on a cited external record
                    -> verifier RE-FINDS the source and checks it says this
    DATA-ANALYSIS   the sentence states a quantity this work computed
                    -> verifier REPRODUCES the number from the artifact that owns it
    INTERPRETATION  neither: no external record to re-find, no number to reproduce
                    -> verifier JUDGES whether the inference follows from what is there

Precedence is LITERATURE > DATA-ANALYSIS > INTERPRETATION, and the order is not cosmetic: it drains
the two strata that have something external to check against FIRST, so the residual INTERPRETATION
stratum is exactly the set with nothing external to check against. That is the stratum this audit
is about. A sentence firing more than one axis keeps every signal in `signals` and is flagged
`mixed: true`, because the precedence hides a real ambiguity and hiding it silently would be the
same defect as `claim_coverage.py`'s round-16 false positives.

⚠ WHAT THIS DELIBERATELY DOES NOT DO.
  · It does not decide whether a claim is true, supported, novel or significant.
  · It does not rank sentences by risk. The sample is random within stratum, seeded, and that is
    the point: a hand-picked sample measures the picker.
  · It does not read the PDF. It reads the markdown that the PDF is built from.
  · It does not assert that an evidence handle SUPPORTS the sentence — only that it is the thing a
    verifier would have to go to. `fusion-junction-aso-references.json` makes the identical
    disclaimer about its own records and it applies here verbatim.

Usage:
    python3 research/manuscripts/claim_audit.py --manuscript <path> --write <manifest.json>
    python3 research/manuscripts/claim_audit.py --manuscript <path> --summary
    python3 research/manuscripts/claim_audit.py --tally <manifest-with-verdicts.json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PINS = os.path.join(HERE, "pinned-figures.json")

#: PMID -> bibliographic record, for naming what a LITERATURE verifier must re-find. These files are
#: citation METADATA (a record exists with that title in that journal); none is evidence that the
#: record supports the sentence, and each says so in its own `_what_this_is_not`.
#: ⚠ THE JOURNAL ARTICLE HAS NO PMID->TITLE ARTIFACT OF ITS OWN, AND THIS AUDIT IS HOW THAT WAS
#: FOUND. The first two files below are the numbered lists of the WORKING RECORD and of the
#: research-article submission; the journal article's own list is rendered straight to
#: `fusion-junction-aso-journal-references.md`, and the only committed JSON keyed by its PMIDs is
#: `journal-reference-authors.json`, which holds author names and no title. So PMID 39912803 —
#: reference 13 of the journal article, the industry off-target recommendations — resolved to an
#: EMPTY record on the first run of this tool. The third source below fixes the resolution; the
#: missing title is reported per source as `title: null` with `record_source` naming where the
#: record did come from, rather than being silently blank.
REFERENCE_SOURCES = (
    os.path.join(HERE, "aso", "fusion-junction-aso-submission-references.json"),
    os.path.join(HERE, "aso", "fusion-junction-aso-references.json"),
    os.path.join(HERE, "aso", "journal-reference-authors.json"),
)

TYPE_LITERATURE = "LITERATURE"
TYPE_DATA = "DATA-ANALYSIS"
TYPE_INTERPRETATION = "INTERPRETATION"
TYPES = (TYPE_DATA, TYPE_LITERATURE, TYPE_INTERPRETATION)

#: ⛔ SECTIONS EXCLUDED AS NON-CLAIM SURFACES. These carry administrative statements — who funded the
#: work, who consented, what may not be administered — which are declarations about the SUBMISSION
#: rather than assertions about the science, and a verifier cannot reproduce or re-find them. They
#: are excluded from the population and COUNTED, so the exclusion is visible rather than silent.
EXCLUDED_SECTIONS = (
    "acknowledgments",
    "acknowledgements",
    "author disclosure statement",
    "statements and declarations",
    "keywords",
    "references",
    "tables",
)

#: A sentence shorter than this is a fragment, a cross-reference or a heading remnant. Counted as
#: excluded rather than dropped.
MIN_WORDS = 6

#: A trailing token that ends in "." without ending the sentence. Initials ("T.D.M.") are matched
#: separately by INITIALS.
ABBREV = frozenset(
    "e.g. i.e. cf. vs. viz. etc. approx. ca. no. fig. figs. eq. eqs. ref. refs. al. "
    "dr. prof. mr. mrs. ms. st. inc. ltd. corp. jr. sr. vol. pp. ed. eds.".split()
)
INITIALS = re.compile(r"^(?:[A-Z]\.)+$")

#: A superscript reference and its PMID annotation may sit BETWEEN the full stop and the space that
#: ends the sentence ("...trial report.<sup>5</sup><!--PMID:31331701--> The fusion junction..."), so
#: the boundary regex has to step over them or every cited sentence merges with its successor.
_TRAILER = r"(?:<sup>[^<]*</sup>)?(?:\s*<!--[^>]*-->)?"
SENT_BOUNDARY = re.compile(
    r"(?<=[.!?])" + _TRAILER + r"\s+(?=[A-Z“‘\"(*—])"
)

PMID_COMMENT = re.compile(r"<!--\s*PMID:([0-9,\s]+)\s*-->")
DOI_LINK = re.compile(r"\bdoi[:/]", re.I)
SUP_REF = re.compile(r"<sup>[\d,\s]+</sup>")
ACCESSION = re.compile(r"\b(?:RRID:[A-Z]+_[A-Za-z0-9]+|GSE\d+|[A-Z]{2}\d{6}\.\d)\b")

#: ⛔ A BARE DIGIT RUN IS NOT A QUANTITY IN THIS FIELD, AND THE FIRST VERSION OF THIS MODULE GOT
#: THAT WRONG IN THE DIRECTION THAT MATTERS. Every gene in this manuscript carries a digit —
#: *NR4A3*, *TAF15*, *EWSR1*, *TCF12*, GRCh38, RNase-H1 — so `\d` alone typed 12 purely interpretive
#: sentences as DATA-ANALYSIS, including "That junction is in no normal transcript, so an antisense
#: gapmer could in principle cleave the fusion", which contains no reproducible number at all. That
#: error drains the stratum the audit is about into the stratum it is compared against, i.e. it
#: flatters the result. A QUANTITY is therefore a digit run with no letter on either side.
QUANTITY = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?(?![A-Za-z])")

#: A named oligonucleotide or transcript sequence. Reproducible against the canonical sequence file,
#: so it is a data-analysis claim rather than an interpretation one.
SEQUENCE = re.compile(r"[ACGTU]{8,}")

#: Quantity words this manuscript uses for its own screens. A quantity alone is not enough — an exon
#: index and a reference year are quantities too — so a DATA-ANALYSIS type needs a quantity AND a
#: unit or a countable object of this work's own analysis, OR a named sequence, OR a pin match.
OWN_QUANTITY = re.compile(
    r"\b(?:%|per cent|percent|base pairs?|bp|kcal/mol|nM|mer|16-mer|designs?|junctions?|"
    r"screens?|panel|replicates?|power|interval|standard deviation|scrambles?|chimeras?|"
    r"near-match(?:es)?|duplex(?:es)?|reagents?|mismatch(?:es)?|draws?|cases?|cohort|"
    r"margin|registers?|positions?|nucleotides?|residues?|test articles?)\b",
    re.I,
)

#: ⛔ AND A NUMBER IN THIS MANUSCRIPT IS OFTEN A WORD. This repository has already paid for that
#: once: `claim_coverage.py`'s round-15 blocker list records *"'ten' is a WORD, so no numeric
#: instrument read it"* — the paper's own house style writes its criterion, its margins and its
#: counts out in words. A digit-only quantity test therefore leaves genuinely reproducible sentences
#: ("Three designs clear every screen applied here", "the panel's top gap-level margin of three") in
#: the interpretation stratum, which FLATTERS the interpretation rate by padding it with claims that
#: are easy to support. Both error directions distort the headline, so the two forms are detected
#: separately and held to different bars.
#: ⚠ "one" IS DELIBERATELY ABSENT. It is a pronoun far more often than a numeral in this prose
#: ("that parent liability is the one this work screens for"), and including it typed several
#: purely interpretive sentences as data-analysis.
NUMBER_WORD = re.compile(
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
    r"fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred|thousand)\b",
    re.I,
)

#: A number WRITTEN AS A WORD is held to a stricter object list than a digit run, because a numeral
#: word collides with discourse ("two bounds apply", "three limits bound what any test could show")
#: far more than a digit does. This list is units and things the artifacts actually count; the
#: broader OWN_QUANTITY nouns — panel, screen, reagent, duplex — are excluded from it on purpose.
STRICT_QUANTITY_OBJECT = re.compile(
    r"\b(?:%|base pairs?|bp|kcal/mol|nM|designs?|junctions?|replicates?|mismatch(?:es)?|"
    r"bases?|nucleotides?|residues?|test articles?|draws?|cases?|registers?|scrambles?|"
    r"chimeras?|near-match(?:es)?|nulls?|margin)\b",
    re.I,
)

#: ★ THE MANUSCRIPT'S OWN VOCABULARY FOR "THIS HAS NO EVIDENCE HANDLE". A sentence that says a
#: premise, a cut or a direction is adopted, taken or conventional rather than measured, retrieved
#: or established is BY CONSTRUCTION an interpretation claim: it states in its own words that there
#: is nothing to reproduce and nothing to re-find. It is typed INTERPRETATION even when it also
#: carries a number, and the number keeps its `own-quantity` signal and sets `mixed`.
#: ⚠ LIMITATION, STATED RATHER THAN HIDDEN: this list is drawn from THIS repository's house style
#: for flagging an adopted premise. A manuscript written elsewhere may flag the same thing in words
#: that are not here, in which case its interpretation stratum is UNDER-counted, not over-counted.
#: Re-read the emitted types before quoting a rate off a manuscript this list was not checked on.
ADOPTION_MARKERS = (
    "adopted here", "adopted rather than", "is adopted", "are adopted", "was adopted",
    "adopted for", "taken here", "is taken to", "are taken to", "premise adopted",
    "rather than established", "rather than measured", "rather than retrieved",
    "a convention, not a measurement", "is a convention", "being adopted",
    "adopted as a convention", "not from that source", "assumed",
)

#: A claim ABOUT THE LITERATURE carrying no citation of its own — what is or is not reported,
#: published or retrievable. Verifying it means going back to the literature, so it is a literature
#: claim; carrying no citation is what makes it worth surfacing separately.
UNCITED_LITERATURE = re.compile(
    r"\b(?:reported|reports|published|retrieved here|in the literature|no survey|"
    r"literature retrieved|annotated|sequenced acceptor)\b",
    re.I,
)

#: Markers of a sentence whose work is to assign meaning, direction or worth. NOT used to CREATE the
#: interpretation stratum — that stratum is the residual — only to record which markers fired, so a
#: reader of the manifest can see why a residual sentence reads as interpretive. An empty list here
#: on an INTERPRETATION row is informative, not a bug: it flags a bare assertion.
INTERPRETIVE_MARKERS = (
    "suggests", "indicates", "implies", "consistent with", "supports", "points to",
    "therefore", "so that", "which makes", "means that", "is not", "does not",
    "rather than", "is adopted", "adopted here", "taken here", "in principle",
    "plausible", "parsimonious", "unsettled", "not resolved", "does not resolve",
    "worth", "the case for", "a property of", "cannot", "would", "could", "must",
    "speaks to", "reading", "the constraint", "is invisible", "follows from",
)

STRIP_MARKUP = (
    (re.compile(r"<!--.*?-->", re.S), ""),
    (re.compile(r"<sup>.*?</sup>", re.S), ""),
    (re.compile(r"<sub>.*?</sub>", re.S), ""),
    (re.compile(r"`([^`]*)`"), r"\1"),
    (re.compile(r"\*\*([^*]*)\*\*"), r"\1"),
    (re.compile(r"\*([^*]*)\*"), r"\1"),
    (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"),
)


def plain(text):
    """The sentence with this repository's markdown and annotation markup removed."""
    out = text
    for pat, rep in STRIP_MARKUP:
        out = pat.sub(rep, out)
    return re.sub(r"\s+", " ", out).strip()


# --------------------------------------------------------------------------------------------
# Reading the manuscript
# --------------------------------------------------------------------------------------------


def _front_matter_end(lines):
    """Index of the first body line, stepping over a leading YAML front-matter block."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def iter_paragraphs(path):
    """Yield (section, level, paragraph_text, [(char_offset, line_no), ...]) per prose paragraph.

    Skips YAML front matter, fenced code, markdown tables, headings, HTML-only lines and horizontal
    rules. `section` is the nearest preceding heading text, lowercased — it is what EXCLUDED_SECTIONS
    is matched against — and `level` is that heading's depth. Depth 1 is the manuscript TITLE, whose
    paragraphs are the byline, the affiliation, the ORCID and the running title: metadata about the
    submission, not claims about the science, and excluded on that ground.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    start = _front_matter_end(lines)
    section = "(preamble)"
    level = 0
    fenced = False
    buf, offsets = [], []
    pos = 0

    def flush():
        nonlocal buf, offsets, pos
        if buf:
            yielded = (section, level, " ".join(buf), list(offsets))
            buf, offsets, pos = [], [], 0
            return yielded
        buf, offsets, pos = [], [], 0
        return None

    for idx in range(start, len(lines)):
        raw = lines[idx]
        line_no = idx + 1
        stripped = raw.strip()
        if stripped.startswith("```"):
            got = flush()
            if got:
                yield got
            fenced = not fenced
            continue
        if fenced:
            continue
        if stripped.startswith("#"):
            got = flush()
            if got:
                yield got
            level = len(stripped) - len(stripped.lstrip("#"))
            section = stripped.lstrip("#").strip().lower()
            continue
        if not stripped or stripped.startswith("|") or stripped in ("---", "***", "___"):
            got = flush()
            if got:
                yield got
            continue
        offsets.append((pos, line_no))
        buf.append(stripped)
        pos += len(stripped) + 1
    got = flush()
    if got:
        yield got


def split_sentences(para):
    """Split a paragraph into sentences, returning (sentence_text, char_offset) pairs."""
    pieces, last = [], 0
    for m in SENT_BOUNDARY.finditer(para):
        head = para[last:m.start()].rstrip()
        tail_token = head.split()[-1].lower() if head.split() else ""
        if tail_token in ABBREV or INITIALS.match(head.split()[-1] if head.split() else ""):
            continue
        pieces.append((para[last:m.end()].strip(), last))
        last = m.end()
    remainder = para[last:].strip()
    if remainder:
        pieces.append((remainder, last))
    return pieces


def _line_for(offset, offsets):
    line = offsets[0][1] if offsets else 0
    for off, ln in offsets:
        if off <= offset:
            line = ln
        else:
            break
    return line


# --------------------------------------------------------------------------------------------
# Classification — type only, never support
# --------------------------------------------------------------------------------------------


def classify(sentence, pin_contexts, section=""):
    """Return (type, meta). `meta["signals"]` records EVERY axis that fired, not only the winner.

    ★★ THE PRECEDENCE, AND WHY EACH RUNG SITS WHERE IT DOES. Each rung answers "what would a verifier
    have to DO", and the order drains the rungs that have something external to check against first,
    so the residual is exactly the set with nothing external to check against.

      1  an external record is cited ON the sentence          -> LITERATURE   (re-find it)
      2  the sentence says its premise was ADOPTED, not
         measured / retrieved / established                   -> INTERPRETATION
      3  the sentence states a quantity or a sequence this
         work produced, or matches a pinned-figure context     -> DATA-ANALYSIS (reproduce it)
      4  the sentence sits in Materials and Methods and is
         a procedure description                              -> DATA-ANALYSIS (reproduce it)
      5  the sentence claims something about the literature
         while carrying no citation                           -> LITERATURE   (go re-search)
      6  residual                                             -> INTERPRETATION (judge the inference)

    ⛔ RUNG 2 IS ABOVE RUNG 3 ON PURPOSE, AND IT IS THE ONE ARGUABLE ORDERING HERE. "Ten is a
    convention, not a measurement: exon-terminus chimeras meet the same screen at 40.6% against the
    panel's 45.8%" carries two reproducible numbers AND declares that its own criterion rests on
    nothing measured. Reproducing 40.6% does not verify the sentence; what the sentence asserts is
    that ten is conventional. Putting rung 3 first would file it as data-analysis and score it
    Supported off a number that is not what is being claimed — which is Kosmos's named failure mode
    "conflating statistically significant with scientifically valuable" arriving through the
    instrument instead of the prose. Such a row keeps `own-quantity` in `signals` and sets `mixed`.

    ⚠ RUNG 4 IS SECTION-BASED AND THEREFORE THE CRUDEST RULE HERE. A Methods sentence describing
    what a screen does ("the third reads the parents' unspliced sequence") is reproducible from the
    code, so filing it as interpretation would inflate the stratum this audit reports. It is typed
    DATA-ANALYSIS with the `methods-section` signal so any reader of the manifest can see the rule
    that moved it and dispute it per row.
    """
    body = plain(sentence)
    low = body.lower()
    signals = []

    pmids = []
    for m in PMID_COMMENT.finditer(sentence):
        pmids.extend(p.strip() for p in m.group(1).split(",") if p.strip())
    if pmids:
        signals.append("cited-pmid")
    if DOI_LINK.search(sentence):
        signals.append("doi")
    if SUP_REF.search(sentence) and not pmids:
        signals.append("superscript-without-pmid")
    if ACCESSION.search(sentence):
        signals.append("accession")

    adoption = [m for m in ADOPTION_MARKERS if m in low]
    if adoption:
        signals.append("adoption-marker")

    matched_pins = [pid for pid, rx in pin_contexts if rx.search(sentence) or rx.search(body)]
    if matched_pins:
        signals.append("pinned-figure")
    if QUANTITY.search(body) and OWN_QUANTITY.search(body):
        signals.append("own-quantity")
        signals.append("quantity-form:digit")
    elif NUMBER_WORD.search(body) and STRICT_QUANTITY_OBJECT.search(body):
        signals.append("own-quantity")
        signals.append("quantity-form:numeral-word")
    if SEQUENCE.search(body):
        signals.append("named-sequence")
    in_methods = section.startswith("materials and methods")
    if in_methods:
        signals.append("methods-section")
    if UNCITED_LITERATURE.search(body) and not pmids:
        signals.append("uncited-literature-scope")

    fired = [m for m in INTERPRETIVE_MARKERS if m in low]
    if fired:
        signals.append("interpretive-marker")

    has_record = any(
        s in signals for s in ("cited-pmid", "doi", "accession", "superscript-without-pmid")
    )
    has_own_data = any(
        s in signals for s in ("pinned-figure", "own-quantity", "named-sequence")
    )

    if has_record:
        claim_type = TYPE_LITERATURE
    elif adoption:
        claim_type = TYPE_INTERPRETATION
    elif has_own_data:
        claim_type = TYPE_DATA
    elif in_methods:
        claim_type = TYPE_DATA
    elif "uncited-literature-scope" in signals:
        claim_type = TYPE_LITERATURE
    else:
        claim_type = TYPE_INTERPRETATION

    axes = sum(
        1
        for group in (
            ("cited-pmid", "doi", "accession", "superscript-without-pmid",
             "uncited-literature-scope"),
            ("pinned-figure", "own-quantity", "named-sequence"),
            ("adoption-marker",),
        )
        if any(s in signals for s in group)
    )
    return claim_type, {
        "signals": signals,
        "interpretive_markers": fired,
        "adoption_markers": adoption,
        "pmids": sorted(set(pmids)),
        "pins": matched_pins,
        "mixed": axes > 1,
    }


# --------------------------------------------------------------------------------------------
# Evidence handles — what a verifier would have to go to
# --------------------------------------------------------------------------------------------


def load_pins(manuscript_rel):
    """(pin_id, compiled context regex) for every artifact_figures pin that targets this manuscript."""
    with open(PINS, encoding="utf-8") as fh:
        pins = json.load(fh)
    out, table = [], {}
    for entry in pins.get("artifact_figures", []):
        if manuscript_rel not in entry.get("must_appear_in", []):
            continue
        ctx = entry.get("context")
        if not ctx:
            continue
        try:
            out.append((entry["id"], re.compile(ctx)))
        except re.error:
            continue
        table[entry["id"]] = entry
    return out, table


def load_references():
    """PMID -> (record, source path), merged over the committed reference artifacts, first wins."""
    table = {}
    for path in REFERENCE_SOURCES:
        if not os.path.exists(path):
            continue
        rel = os.path.relpath(path, REPO)
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        records = doc.get("records")
        if isinstance(records, dict):
            for pmid, rec in records.items():
                table.setdefault(str(pmid), (rec, rel))
        for rec in doc.get("references", []) or []:
            if rec.get("pmid"):
                table.setdefault(str(rec["pmid"]), (rec, rel))
        for pmid, rec in (doc.get("by_pmid") or {}).items():
            table.setdefault(str(pmid), (rec, rel))
    return table


def evidence_for(claim_type, meta, pin_table, refs, antecedents):
    """The handle a verifier goes to. NOT a claim that the handle supports the sentence."""
    if claim_type == TYPE_LITERATURE:
        sources = []
        for pmid in meta["pmids"]:
            rec, rel = refs.get(pmid, ({}, None))
            sources.append({
                "pmid": pmid,
                "title": rec.get("title"),
                "journal": rec.get("journal"),
                "year": rec.get("year"),
                "record_source": rel,
                "resolved_from_committed_record": bool(rec),
            })
        return {
            "verification_action": (
                "RE-FIND each source independently and check it states what the sentence "
                "attributes to it. Do not settle this by re-reading the manuscript."
            ),
            "sources": sources,
            "note": (
                "No PMID annotation is carried on this sentence" if not sources else None
            ),
        }
    if claim_type == TYPE_DATA:
        artifacts = []
        for pid in meta["pins"]:
            entry = pin_table.get(pid, {})
            artifacts.append({
                "pin_id": pid,
                "artifact": entry.get("artifact"),
                "key": entry.get("key"),
                "regenerate": entry.get("regenerate"),
            })
        return {
            "verification_action": (
                "REPRODUCE the number from the artifact that owns it — read the named key, or "
                "re-run the named regeneration. Do not settle this by re-reading the manuscript."
            ),
            "artifacts": artifacts,
            "note": (
                "UNPINNED: this sentence states a quantity that no artifact_figures pin claims. "
                "The verifier has to locate the producing artifact first, and the absence of a pin "
                "is itself a finding." if not artifacts else None
            ),
        }
    return {
        "verification_action": (
            "JUDGE whether the inference follows from the artifacts and sources it rests on. "
            "There is no number to reproduce and no citation on this sentence, so the verifier "
            "must reconstruct the antecedents below and ask whether they carry it. "
            "Do not settle this by re-reading the manuscript — agreeing with the prose is the "
            "failure mode this stratum exists to measure."
        ),
        "antecedents_in_same_section": antecedents,
        "note": (
            "An interpretation claim has no committed evidence handle of its own. That is the "
            "point: lint_citations and lint_claims are both silent here."
        ),
    }


# --------------------------------------------------------------------------------------------
# Enumeration and sampling
# --------------------------------------------------------------------------------------------


def enumerate_claims(manuscript, manuscript_rel):
    pin_contexts, pin_table = load_pins(manuscript_rel)
    refs = load_references()
    population, excluded = [], []

    for section, level, para, offsets in iter_paragraphs(manuscript):
        section_excluded = any(section.startswith(s) for s in EXCLUDED_SECTIONS)
        title_block = level == 1
        for sentence, offset in split_sentences(para):
            body = plain(sentence)
            line = _line_for(offset, offsets)
            claim_type, meta = classify(sentence, pin_contexts, section)
            row_base = {
                "file": manuscript_rel,
                "line": line,
                "section": section,
                "sentence": sentence.strip(),
                "text_plain": body,
            }
            if title_block:
                excluded.append(dict(row_base, excluded_because="title block (byline, ORCID, running title)"))
                continue
            if section_excluded:
                excluded.append(dict(row_base, excluded_because="administrative section"))
                continue
            if len(body.split()) < MIN_WORDS:
                excluded.append(dict(row_base, excluded_because="fragment (<%d words)" % MIN_WORDS))
                continue
            claim_id = "C-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
            population.append(dict(row_base, claim_id=claim_id, type=claim_type, **meta))

    # Antecedents for an interpretation claim: every PMID and every pin that appears elsewhere in
    # the same section. Derived from the enumeration, so it cannot drift from what was enumerated.
    by_section = {}
    for row in population:
        acc = by_section.setdefault(row["section"], {"pmids": set(), "pins": set()})
        acc["pmids"].update(row["pmids"])
        acc["pins"].update(row["pins"])

    for row in population:
        acc = by_section.get(row["section"], {"pmids": set(), "pins": set()})
        antecedents = {
            "section": row["section"],
            "pmids_cited_in_section": sorted(acc["pmids"]),
            "pinned_figures_in_section": sorted(acc["pins"]),
        }
        row["evidence"] = evidence_for(row["type"], row, pin_table, refs, antecedents)
        row["verdict"] = None
        row["verdict_evidence"] = None
        row["verdict_by"] = None
    return population, excluded


def draw(population, seed, n_per_type):
    """Deterministic stratified sample. Sorted by claim_id first, so the draw depends on the SEED
    and the sentence CONTENT — never on line numbers, which drift with every paragraph added above.
    """
    sample, strata = [], {}
    for claim_type in TYPES:
        pool = sorted(
            (r for r in population if r["type"] == claim_type), key=lambda r: r["claim_id"]
        )
        rng = random.Random("%s|%s" % (seed, claim_type))
        take = min(n_per_type, len(pool))
        drawn = rng.sample(pool, take) if take else []
        strata[claim_type] = {
            "population": len(pool),
            "sampled": take,
            "sampled_all": take == len(pool),
        }
        sample.extend(drawn)
    sample.sort(key=lambda r: (r["line"], r["claim_id"]))
    return sample, strata


def build_manifest(manuscript, seed, n_per_type):
    manuscript_rel = os.path.relpath(os.path.abspath(manuscript), REPO)
    with open(manuscript, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    population, excluded = enumerate_claims(manuscript, manuscript_rel)
    sample, strata = draw(population, seed, n_per_type)
    return {
        "_what": (
            "A stratified sample of this manuscript's claim sentences, each with the type that "
            "decides what a verifier would have to DO, and the evidence handle they would have to "
            "reproduce or re-find. Kosmos's audit protocol, sampling half only."
        ),
        "_what_this_is_not": [
            "NOT a support verdict. Every `verdict` is null and this tool never fills one in. "
            "Classifying Supported/Refuted/Unverifiable is the human or blind-seat step; a tool "
            "that scored its own paper would be the exact failure mode the audit exists to catch.",
            "NOT a claim that any evidence handle SUPPORTS the sentence it is attached to. It is a "
            "claim about what a verifier would have to go to.",
            "NOT a risk ranking. The draw is uniform within stratum and seeded; a hand-picked "
            "sample measures the picker.",
            "NOT a reading of the PDF. It reads the markdown the PDF is built from.",
        ],
        "_generated_by": "research/manuscripts/claim_audit.py",
        "_protocol_source": "research/method-watch-autonomy-prior-art-2.md §4.1, §4.2",
        "manuscript": manuscript_rel,
        "manuscript_sha256": digest,
        "seed": seed,
        "n_per_type_requested": n_per_type,
        "reproduce": (
            "python3 research/manuscripts/claim_audit.py --manuscript %s --seed %s "
            "--n-per-type %s --write <out.json>" % (manuscript_rel, seed, n_per_type)
        ),
        "population_by_type": {t: strata[t]["population"] for t in TYPES},
        "excluded_non_claim": len(excluded),
        "strata": strata,
        "sample": sample,
    }


# --------------------------------------------------------------------------------------------
# Tally — arithmetic over verdicts SOMEBODY ELSE WROTE
# --------------------------------------------------------------------------------------------

VERDICTS = ("SUPPORTED", "REFUTED", "UNVERIFIABLE")


def tally(manifest):
    """Stratified support rate over a manifest whose verdicts have been filled in by a verifier.

    ⛔ This does arithmetic. It does not decide a verdict, and a row still holding `null` is counted
    as UNSCORED rather than given one.
    """
    out = {}
    for claim_type in TYPES:
        rows = [r for r in manifest["sample"] if r["type"] == claim_type]
        counts = {v: 0 for v in VERDICTS}
        unscored = 0
        for row in rows:
            verdict = (row.get("verdict") or "").upper()
            if verdict in counts:
                counts[verdict] += 1
            else:
                unscored += 1
        scored = sum(counts.values())
        out[claim_type] = {
            "n_sampled": len(rows),
            "n_scored": scored,
            "n_unscored": unscored,
            **{v.lower(): counts[v] for v in VERDICTS},
            "supported_rate_of_scored": (
                round(counts["SUPPORTED"] / scored, 4) if scored else None
            ),
            "supported_rate_of_sampled": (
                round(counts["SUPPORTED"] / len(rows), 4) if rows else None
            ),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manuscript")
    ap.add_argument("--seed", type=int, default=20260828)
    ap.add_argument("--n-per-type", type=int, default=12)
    ap.add_argument("--write", help="write the manifest to this path")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--tally", help="a manifest whose verdicts a verifier has filled in")
    args = ap.parse_args(argv)

    if args.tally:
        with open(args.tally, encoding="utf-8") as fh:
            manifest = json.load(fh)
        rates = tally(manifest)
        print(json.dumps(rates, indent=1))
        return 0

    if not args.manuscript:
        ap.error("--manuscript is required unless --tally is given")
    manifest = build_manifest(args.manuscript, args.seed, args.n_per_type)

    if args.write:
        with open(args.write, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("wrote %s" % args.write)

    if args.summary or not args.write:
        print("manuscript      %s" % manifest["manuscript"])
        print("sha256          %s" % manifest["manuscript_sha256"][:16])
        print("seed            %s" % manifest["seed"])
        for claim_type in TYPES:
            s = manifest["strata"][claim_type]
            print(
                "%-15s population %4d   sampled %3d%s"
                % (claim_type, s["population"], s["sampled"], "  (all)" if s["sampled_all"] else "")
            )
        print("excluded        %4d non-claim sentences" % manifest["excluded_non_claim"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
