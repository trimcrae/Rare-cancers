#!/usr/bin/env python3
"""Which sentences of every publication endpoint does any instrument actually read?

⛔⛔ WHY THIS EXISTS — THE CONVERGENCE DIAGNOSIS (2026-08-22, after round 15).

Fifteen rounds of blind adversarial review, and the BLOCKER count went UP: three distinct in round
14, six in round 15. That is not a paper getting worse. Read the blockers together and they are one
finding:

  r14  Table 2's caption counted rows it no longer had     — no gate read that file
  r14  §5's void figure was deleted, orphaning a claim     — no gate read the dependency
  r14  the paper never stated its own chemistry            — no gate reads absence
  r15  the wrong non-financial interest was declared       — no gate reads Declarations
  r15  both reagents named by donor exon alone             — no gate reads sequence+exon together
  r15  "ten" is a WORD, so no numeric instrument read it   — no gate reads criteria as words
  r15  the title's PREDICATE could be inverted             — no gate reads verbs
  r15  the two reagents swappable against their own table  — no gate joins prose to a table cell

Every one is a surface with ZERO instruments, not a number a guard got wrong. So the blocker rate
was tracking how many new LENSES each round introduced, not how many defects the paper held: a new
seat looks somewhere nobody looked, and finds the first thing there. That process does not converge
by iteration, because there is always another unexamined patch.

★ WHAT CHANGES THE SHAPE: stop sampling surfaces one lens at a time and ENUMERATE them. This script
asks, of every assertive sentence in a manuscript, whether any committed instrument matches it —
pins, the prose-guard patterns, the claim linter. The uncovered set IS the remaining blocker risk,
available all at once instead of one per round.

⚠ WHAT THIS IS NOT. It does not check whether a sentence is TRUE — only whether anything would
notice if it changed. A covered sentence can still be wrong; an uncovered one is simply unwatched.
And matching is approximate by construction: a pattern that matches a sentence may be asserting
about a different part of it. Treat the covered count as an upper bound and the uncovered list as
the finding.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TESTS = os.path.join(HERE, "tests")
PINS = os.path.join(HERE, "pinned-figures.json")

#: ⛔⛔ THE DOCUMENT SET IS A PREDICATE READ FROM RECORDS, NOT A LIST SOMEBODY MUST REMEMBER TO
#: EXTEND (2026-08-26). Until today this was three hand-typed entries, all three belonging to ONE
#: submission — and the omission was not hypothetical: `fusion-partner/emc-fusion-partner-
#: stratification.md` is a live publication endpoint that was being hardened by blind review seats
#: while NO instrument read it, not even to say its coverage was zero. Measured that day: 94 test
#: modules name `fusion-junction-aso`, 2 name `fusion-partner`, and its blocker count across four
#: rounds went 3 -> 2 -> 9, which is `paper-hardening` §8a's signature of sampling surfaces rather
#: than fixing a paper.
#: ★★ THE STRUCTURAL REASON, MEASURED (`paper-hardening` §8b.2, 33 mutations): every fix scoped to a
#: PREDICATE held; six of eleven scoped to a LIST regressed at a sibling the fix did not name, and in
#: three of the six the missed sibling was named in the fix's own comment. A list is a thing somebody
#: must remember to extend, and the remembering is what fails. So a manuscript added tomorrow lands
#: in this census without anybody editing anything here.
#: ⚠ AND A WIDENING IS ONLY A FIX ONCE YOU HAVE RUN IT. The first attempt at this class of predicate
#: — "every `.md` in the submission directory" — swept up working notes and a review backlog and went
#: RED ON A CORRECT TREE, which is worse than a gate that greens on false input because the first
#: thing anyone does is loosen it. So the predicate is not "a markdown file near a manuscript"; it is
#: "a document a committed RECORD calls a publication endpoint, or a part one of those ships".
#: Run 2026-08-26, it selects 32 documents: the 25 endpoint manuscripts the systems graph names, the
#: two ASO companion files the submission metrics name, and the five cover letters the generated
#: submission packet names. It selects NO redteam round, NO working record, NO receipt, and none of
#: the program memos (`nr4a3-program-map.md`, `program/emc-treatment-strategy.md`,
#: `program/emc-post-degrader-options.md`) — those are memory, not endpoints.
_PUBLICATION_GRAPH = os.path.join("systems", "graph", "publications.json")
_SUBMISSION_METRICS = os.path.join("research", "manuscripts", "submission-metrics.json")
_SUBMISSION_PACKET = os.path.join("research", "manuscripts", "SUBMISSION-PACKET.md")

#: The packet is generated markdown whose per-paper tables name each shipped part in backticks.
_PACKET_DOCUMENT = re.compile(r"`([A-Za-z0-9._/-]+\.md)`")


def _record(repo, rel, load, missing):
    """Read one record. Absent -> `missing`; present and unreadable -> the exception, unswallowed."""
    path = os.path.join(repo, rel)
    if not os.path.exists(path):
        return missing
    return load(io.open(path, encoding="utf-8"))


def endpoint_documents(repo=None):
    """{repo-relative path: the record that named it} for every publication-endpoint document.

    Three records, each authoritative for a different half of the question, and each read rather
    than remembered:

      · `systems/graph/publications.json` — the source of truth for every L3 publication endpoint
        (CLAUDE.md §7). Its `document.file` is the manuscript itself. This is what puts a new paper
        in scope the day it is registered.
      · `research/manuscripts/submission-metrics.json` — the per-submission measurement rows, whose
        `companion_files` name the tables and reference list a submission is counted over. This is
        what keeps `fusion-junction-aso-journal-tables.md` in scope; the graph names only the
        article.
      · `research/manuscripts/SUBMISSION-PACKET.md` — generated, and the only record that says which
        cover letter belongs to which paper (`submission_packet.py` resolves it from the directory
        because nothing else records it). This is what keeps the ASO cover letter in scope.

    ⚠ A record entry naming a file that is not on disk is DROPPED rather than raising: an endpoint
    can be registered before it is written (`state: unwritten` carries no `document`), and a census
    that dies on a planned paper would be a gate reddening on a correct tree.
    """
    repo = REPO if repo is None else repo
    found = {}

    def offer(rel, record):
        rel = rel.replace(os.sep, "/")
        if os.path.exists(os.path.join(repo, rel)):
            found.setdefault(rel, record)

    # ⛔ A RECORD THAT IS PRESENT AND UNREADABLE RAISES; ONLY AN ABSENT ONE IS TOLERATED. Swallowing
    # a parse error would shrink the document set silently, and a census reporting on 4 documents
    # because a file failed to parse looks exactly like a census reporting on 4 documents. An absent
    # reading is not a reading of absence (CLAUDE.md §4).
    graph = _record(repo, _PUBLICATION_GRAPH, json.load, [])
    for entry in graph:
        if entry.get("kind") != "publication":
            continue
        rel = (entry.get("document") or {}).get("file")
        if rel and rel.endswith(".md"):
            offer(rel, "systems/graph/publications.json")

    metrics = _record(repo, _SUBMISSION_METRICS, json.load, {})
    for row in metrics.get("rows") or []:
        for rel in [row.get("file")] + list(row.get("companion_files") or []):
            if rel and rel.endswith(".md"):
                offer(os.path.join("research", "manuscripts", rel),
                      "research/manuscripts/submission-metrics.json")

    packet = _record(repo, _SUBMISSION_PACKET, lambda fh: fh.read(), "")
    for rel in _PACKET_DOCUMENT.findall(packet):
        offer(os.path.join("research", "manuscripts", rel),
              "research/manuscripts/SUBMISSION-PACKET.md")

    return {k: found[k] for k in sorted(found)}


#: Which record named each censused document — carried into the report so a reader sees the
#: predicate rather than having to trust that one was used.
NAMED_BY = endpoint_documents()

#: ⚠ THE KEY IS THE REPO-RELATIVE PATH, not a short label. A short label ("journal-article") has to
#: be invented per document by somebody, which is the same remembering this derivation removes.
PAPERS = {rel: os.path.join(REPO, rel) for rel in NAMED_BY}

#: FLOORS, not targets: coverage may rise freely and may not fall. Taken by
#: `python3 research/manuscripts/claim_coverage.py --write`; the ratchet that enforces them, and the
#: full history of every time one moved and why, is
#: `tests/test_the_paper_states_what_its_own_claims_depend_on.py`.
#: ⚠ Raising a floor is a deliberate act — do it when you have closed a class, never to make a red
#: run green. Lowering one is legitimate only when the INSTRUMENT was proved wrong, not when a run
#: went red, and the commit must say which.
#: ⛔ THE TABLE LIVES HERE RATHER THAN BESIDE ITS TEST BECAUSE ITS KEYS ARE MANUSCRIPT PATHS, and
#: `_test_patterns` treats any test module mentioning a manuscript's basename — in a constant, in a
#: comment, anywhere — as a reader of that document, then credits that module's literals to it as
#: coverage. Measured 2026-08-26: with these four keys in the test file, the cover letter read
#: 16 covered instead of 10 and the fusion-partner manuscript gained a witness that binds nothing in
#: it. This module is not scanned, so the table is inert here.
#: ⚠ A DOCUMENT WITH NO ROW IS STILL CENSUSED. Its coverage is visible in the committed report and
#: checked for staleness; it is simply not held. 28 of the 32 are in that state, most of them at zero.
COVERAGE_FLOOR = {
    "research/manuscripts/aso/fusion-junction-aso-journal-article.md":
        {"covered": 66, "with_a_number_covered": 44},
    "research/manuscripts/aso/fusion-junction-aso-journal-tables.md":
        {"covered": 4, "with_a_number_covered": 1},
    "research/manuscripts/aso/fusion-junction-aso-cover-letter.md":
        {"covered": 6, "with_a_number_covered": 4},
    #: ⭐ FIRST CENSUS OF THIS DOCUMENT, 2026-08-26, AND THE LOW NUMBER IS THE FINDING. The census had
    #: never read it — its document set was three hand-typed entries, all three of one submission —
    #: while blind review seats hardened it with no instrument behind them. Measured at
    #: `6b2bd3729`: 1 of 259 sentences, 1 of 192 stating a number, and the one witness is a pin
    #: (`fusion_partner_dod_fisher_p`). No test module named the file at all. That 1 is not a false
    #: positive: ablating it — perturbing the number in a clone and re-running the witness — goes red.
    #: ⚠ THE LIVE READING IS NO LONGER 1, AND IT IS NOT WRITTEN HERE. `8bd6cff9d` landed a numbers
    #: guard against this manuscript hours later and the count moved, which is the instrument
    #: working. The current count has ONE home — the committed report `claim-coverage.json` that
    #: `main(--write)` below produces — and it is read there, never restated here.
    #: THE FLOOR IS DELIBERATELY LEFT AT 1 rather than raised to the live count, because raising a
    #: floor holds whoever owns that guard to its current shape and it was still being written when
    #: this was committed. Raising it is a one-line, deliberate act for that owner, and leaving the
    #: gain unheld is the cost of not taking it.
    #: ⚠ Superseded, retained (2026-08-27, round-10 audit STALE_GUARD_TEXT 4): this note used to
    #: state "the census now reads 46 of 259 (46 of 192 numbered)". Re-measured 2026-08-27 by
    #: `python3 research/manuscripts/claim_coverage.py` — none of those four numbers is current, and
    #: the committed `claim-coverage.json` agreed with the live run to the digit on every one of
    #: them. The count was frozen into a comment while the artifact beside it kept measuring; that
    #: is why the sentence above now points instead of repeating.
    "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md":
        {"covered": 1, "with_a_number_covered": 1},
}

#: ⛔⛔ A SENTENCE WHOSE ABLATION IS BLOCKED BY A KNOWN CENSUS FALSE POSITIVE, WITH THE COUNTEREXAMPLE
#: WRITTEN DOWN RATHER THAN THE GATE LOOSENED. `test_the_census_word_covered_survives_ablation.py`
#: perturbs a covered sentence's NUMBER and demands that some witness the census names goes red. That
#: is a stronger claim than `covered` makes — the census says only that a selective pattern matches
#: the sentence, and this module's own docstring calls the covered count an upper bound — so a
#: pattern can legitimately bind a sentence's WORDS while claiming nothing about its digits.
#: ⭐⭐ NARROWED FROM A DOCUMENT TO A SENTENCE ON 2026-08-27 (AUT-PROP-025), AND THE MEASUREMENT IS
#: WHY. The round-10 guard-coverage audit filed this row as stale: it re-ran the gate's own sampling
#: (`SAMPLE=6`, evenly spaced over covered numbered sentences) through `claim_ablation.ablate` and
#: got `applied=6 blind=0`, concluding the exemption removed a whole floored manuscript "on a reading
#: that no longer reproduces". BOTH HALVES WERE RE-MEASURED HERE AND THEY DISAGREE:
#:   · the audit's NUMBER reproduces exactly — the same sampling at `2ca11bfe8` gives
#:     `applied=6 blind=0 skipped=0`, every sampled sentence red;
#:   · the audit's CONCLUSION does not. Ablating EVERY covered numbered sentence — which is what
#:     `PREFLIGHT_FULL=1` does, and what the six-sentence sample never reaches — gives
#:     `applied=71 blind=3 skipped=5` over all 76, and the recorded sentence is one of the three
#:     still blind, under the identical perturbations the row already named.
#: ★ SO THE ROW IS EVIDENCE, NOT ROT, AND THE DEFECT WAS ITS SCOPE: three blind sentences were taking
#: a 269-sentence manuscript out of the gate, so 68 covered numbered sentences that DO go red went
#: unfalsified to buy cover for three that do not. Exemptions are now keyed by SENTENCE and the
#: document stays in the gate.
#: ⚠ THE OTHER TWO BLINDS ARE NEW ROWS, NOT A LOOSENING: nothing was ablating them before, because
#: nothing was ablating this document at all. They are the audit's real finding, and they are the
#: reason the honest move was to narrow the exemption rather than delete it.
#: ⚠ AND A SAMPLE THAT MISSES A DEFECT IS NOT A SAMPLE THAT DISPROVES IT. `SAMPLE=6` over 76
#: candidates touches 8% of them; reading `blind=0` from it as "the cause is gone" is an absent
#: reading taken for a reading of absence, which is the failure `claim_ablation` was built to stop.
#: Re-grade an exemption with `PREFLIGHT_FULL=1`, never with the commit-loop sample.
#: ★ MEASURED, NOT ARGUED (2026-08-26, at `8bd6cff9d`, 6 sentences sampled, 1 blind):
#:   sentence  "The development environment's egress proxy refuses CONNECT to Europe PMC, NCBI and
#:              ClinicalTrials.gov (verified this session: curl exit 56, HTTP 000)."
#:   credited  test_fusion_partner_prose_matches_its_artifact.py, by the harvested pattern
#:             `HTTP \d{3}` — which matches 5 of 259 sentences, so it passes the share filter, and
#:             contains the literal run "HTTP", so it passes `_binds_literal_text`.
#:   perturbed 56 -> 57 and 000 -> 007. Nothing went red, because `\d{3}` matches "007" too.
#: ⚠ THE VERDICT IS THE GATE'S, NOT THE PAPER'S: that sentence is counted as covered and is not, and
#: the remedy the gate prints applies — bind the number for real, or stop crediting a pattern that is
#: wildcard exactly where the claim is. Both live in the guard, which another session owns and was
#: still writing when this was committed, so the finding is recorded here for it.
#: ⛔ THIS IS AN EXEMPTION FROM ONE GATE ON NAMED SENTENCES, NOT A RULE CHANGE. The census still
#: counts every sentence of these documents, their committed counts are still checked for staleness,
#: their floors still hold, and every other covered numbered sentence in them is still ablated.
#: Deleting a row here is the fix; adding one is a defect being recorded, and each must carry the
#: perturbation that proved it.
#: SHAPE: `{document: {a literal excerpt of the exempted sentence: what was measured}}`. The excerpt must
#: match exactly ONE censused sentence of that document, which is what makes the row expire on its
#: own: edit or delete the sentence and the validator in
#: `tests/test_the_census_reads_every_publication_endpoint.py` goes red instead of the exemption
#: quietly outliving the defect it records. That is the property the document-keyed shape lacked.
ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE = {
    #: ⛔ ALL THREE ROWS BELOW ARE ONE DEFECT WITH ONE CAUSE, and it is worth stating once: each
    #: sentence's only census witness is the harvested pattern `HTTP \\d{3}`, which is a WILDCARD
    #: EXACTLY WHERE THE CLAIM IS — it goes on matching after the status code moves. The rows are
    #: kept separate because the validator requires each excerpt to pick out exactly one censused
    #: sentence, which is what lets a row expire when its sentence is fixed or deleted.
    #: ★ THE SYSTEMIC REMEDY IS NOT HERE AND IS NOT TAKEN HERE. Refusing to credit a pattern whose
    #: only variable part is the number would delete all three rows at once, and it would change
    #: `covered` for every censused document and every floor that holds one — a separate, measured
    #: change with its own blast radius, raised rather than absorbed into a docstring fix.
    "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md": {
        "egress proxy refuses CONNECT to Europe PMC":
            "credited only by `HTTP \\d{3}`; re-measured 2026-08-27 at 2ca11bfe8 against every "
            "guard that opens the file, 56 -> 57 and 000 -> 007 turned nothing red",
        "It is **bronze open access**":
            "credited only by `HTTP \\d{3}`, matching the sentence's HTTP 403; measured 2026-08-27 "
            "at 2ca11bfe8, 2023 -> 2027, 03 -> 07, 21 -> 27 and 403 -> 407 turned nothing red",
        "That was necessary because the publisher's edge blocks automation":
            "credited only by `HTTP \\d{3}`, matching the sentence's HTTP 403; measured 2026-08-27 "
            "at 2ca11bfe8, 2023 -> 2027, 03 -> 07, 21 -> 27, 403 -> 407 and 2 -> 7 turned nothing red",
    },
}


def ablation_exempt(paper_key, sentence):
    """Is this censused sentence one of the recorded false positives for its own document?

    ⛔ SUBSTRING, NOT EQUALITY, AND DELIBERATELY SO: `sentences()` flattens line wrapping, so a
    sentence's exact text is a property of the splitter rather than of the manuscript, and an
    exemption keyed on it would expire on a reflow instead of on a fix. The validator holds the
    other end — an excerpt matching zero or several censused sentences fails there.
    """
    return any(excerpt in sentence
               for excerpt in ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE.get(paper_key, {}))


#: Front matter, HTML comments, headings and table pipes are not prose claims.
_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SUP = re.compile(r"<sup>.*?</sup>", re.S)


def _prose(path):
    text = io.open(path, encoding="utf-8").read()
    text = _FRONTMATTER.sub("", text)
    text = _COMMENT.sub("", text)
    text = _SUP.sub("", text)
    keep = [ln for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", "|", ">", "```"))]
    return re.sub(r"\s+", " ", " ".join(keep))


def sentences(path):
    """Assertive sentences, split on terminal punctuation that is not inside a number or a 5′ tag."""
    flat = _prose(path)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z*‘“])", flat)
    return [s.strip() for s in parts if len(s.split()) >= 6]


def _pin_patterns():
    """Every `context` regex a pin uses, with the document it is pinned to."""
    pins = json.load(io.open(PINS, encoding="utf-8"))["artifact_figures"]
    out = []
    for pin in pins:
        ctx = pin.get("context")
        if not ctx:
            continue
        for home in pin.get("must_appear_in") or []:
            out.append((os.path.basename(home), ctx, f"pin:{pin['id']}"))
    return out


#: ⚠ HARVESTING LITERALS MAKES COVERAGE SENSITIVE TO A GUARD'S SOURCE, NOT ONLY TO ITS BEHAVIOUR
#: (measured 2026-08-23). Replacing an enumerated `DOCUMENTS = {...}` in one guard with a derived
#: lookup removed the manuscript basenames from that file's source; the census lost a pattern it had
#: been crediting and the cover-letter reading moved 7 -> 6. Restoring the literals moved it back.
#: NOTHING ABOUT WHAT THE GUARD CHECKS CHANGED IN EITHER DIRECTION.
#: ⛔ So a coverage delta is not by itself evidence that binding was won or lost, and a floor moved on
#: one is a floor moved on a refactor. The reading that does not twitch is `claim_ablation` — it RUNS
#: the guards rather than inferring them from their source, which is why it, and not this count, is
#: what the convergence claim rests on.


def _test_patterns(document=None):
    """String literals from tests that compile as a regex — from tests that OPEN `document`.

    ⛔⛔ THE DOCUMENT SCOPE IS THE WHOLE POINT, AND ITS ABSENCE MADE THIS SCRIPT LIE (round 16
    seat 4, 2026-08-22). The first version applied EVERY test file's literals to EVERY document, so
    a pattern belonging to a test that only ever opens the journal article could mark a cover-letter
    sentence "covered". Measured on the letter: **27 of 40 reported covered, and 22 of those 27 were
    false positives** — only four test files name that file at all. The census was over-reporting
    the exact quantity it exists to report, and a floor had already been ratcheted onto the wrong
    number.
    ⚠ THE EARLIER COMMENT HERE SAID THE OVER-INCLUSION WAS SAFE because "the finding is the
    UNCOVERED list, so the bias runs against the conclusion". That reasoning was wrong in the
    direction that matters: inflating COVERED shrinks UNCOVERED, which HIDES surfaces. The bias ran
    toward the comfortable answer, which is the one to distrust.
    ★ A test's patterns count for a document only if the test names that document. Crude, and
    exactly right: a guard that never opens a file cannot be binding a sentence in it.
    """
    out = []
    for name in sorted(os.listdir(TESTS)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        try:
            src = io.open(os.path.join(TESTS, name), encoding="utf-8").read()
        except OSError:
            continue
        if document and document not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if len(s) < 8 or "\n" in s:
                    continue
                if not re.search(r"[\\(\[]|\\d|\\w|\\s", s):
                    continue
                try:
                    re.compile(s)
                except re.error:
                    continue
                out.append((None, s, f"test:{name}"))
    return out


#: A pattern matching more than this share of a document's sentences is not binding any of them.
#:
#: ⛔⛔ WITHOUT THIS THE SCRIPT REPORTED 100% COVERAGE ON EVERY PAPER, WHICH IS THE DEFECT IT WAS
#: WRITTEN TO FIND (measured 2026-08-22, first run). Harvesting string literals picks up `\s+`,
#: `\d`, `[^.]{0,140}` and their kin — patterns that match every sentence and therefore bind none.
#: A census that counts those as coverage is a gate reporting while measuring nothing, in the very
#: instrument built to detect that. THE SELECTIVITY TEST IS THE MEASUREMENT: a guard earns the word
#: "covers" only by distinguishing the sentence it guards from the ones it does not.
MAX_MATCH_SHARE = 0.10

#: ⛔⛔ A SHARE IS NOT REPRESENTABLE ON A SHORT DOCUMENT, AND THAT SILENTLY ZEROED A WHOLE PAPER
#: (round 16 seat 5, 2026-08-22). `fusion-junction-aso-journal-tables.md` flattens to NINE sentences.
#: The smallest non-zero share on nine is 1/9 = 0.111, which is GREATER than 0.10 — so every pattern
#: matching even one sentence was discarded before the coverage loop ran, and the reported
#: `journal-tables: 0 of 9` was integer arithmetic rather than a reading. A gate whose verdict is
#: fixed by the size of its population is measuring nothing.
#: ★ A pattern is non-binding only when it matches MORE THAN the greater of one sentence and the
#: share, so one sentence is always bindable however short the document.
#:
#: ⚠ AT THE TIME THIS WAS WRITTEN THE TABLES FILE STILL READ 0/9 AFTER THE SCOPE FIX, for a different
#: and worse reason than the arithmetic: almost nothing named that document. That has since been
#: closed — six test files name it now and the census reads 4 of 10 — so this constant is not what
#: fixed it and must not be read as though it were. It is fixed so that a future binding on a short
#: document cannot be silently discarded before the coverage loop runs.


def _binds_literal_text(pattern, runlen=4):
    r"""Does this pattern contain a run of literal characters, or only structure?

    ⛔⛔ "MATCHES FEW SENTENCES" WAS IMPLEMENTED WHERE "DISTINGUISHES THIS SENTENCE" WAS MEANT
    (round 16 seat 5, 2026-08-22). The docstring above states the property exactly right and the
    share filter delivers a different one: a markdown artefact matches few sentences and
    distinguishes nothing. The widest patterns the 0.10 filter ACCEPTED on the 124-sentence article
    were `\b\d+(?:\.\d+)?%`, `\*\*[^*\n]+\*\*`, a code-span pattern, an ISO date and `(?<=\.)\s+` —
    bold, code, italics, a date and whitespace, not one of which can tell a true claim from a false
    one.

    ★★ AND THIS RULE IS NOT ARGUED, IT IS MEASURED. Seven numbered sentences lose their only witness
    to it. Six were ablated — the number perturbed in the real file, the named witness re-run — and
    all six stayed GREEN, so their "coverage" was false. The seventh could not be measured: the
    splitter had joined it across a `---` rule into a sentence with no home in the file.
    Ablation is `claim_ablation.py`; the run is `test_the_census_word_covered_survives_ablation.py`.
    """
    stripped = re.sub(r"\\.", " ", re.sub(r"\[(?:[^\]\\]|\\.)*\]", " ", pattern))
    return bool(re.search(r"[A-Za-z0-9]{%d,}" % runlen, stripped))


#: `<!-- GENERATED — DO NOT EDIT. Regenerate: python3 <script> -->`, the header every generated
#: deposit artifact carries.
_GENERATED = re.compile(r"<!--\s*GENERATED[^>]*?Regenerate:\s*(?:python3\s+)?(\S+\.py)", re.I)


def _generator(path):
    """The script a generated document reproduces from, or None if it is hand-written.

    ⛔⛔ `journal-tables: 0 of 9` WAS A FALSE NEGATIVE, AND THE CENSUS REPORTED IT FOR TWO ROUNDS
    (measured 2026-08-22 by ablation). Round 16 read that zero as "the display items the journal
    article cites have no instruments" — a manuscript finding, escalated, and WRONG. The tables file
    is GENERATED from `aso_journal_tables.py`, so its guarantee is REPRODUCTION rather than pattern
    matching: every cell and every caption is regenerated from the canonical sequence CSV and
    compared. No regex is homed to it because none needs to be.

    ★ MEASURED, NOT ARGUED, IN BOTH DIRECTIONS:
      · a Table 1 cell, `8 bp, wild-type *TFG*` -> `9 bp`  →  generator `--check` rc=1 STALE, and
        `test_journal_article_numbers.py` red as well;
      · a numbered CAPTION sentence, the population the census actually counts, perturbed  →  rc=1.
    ⚠ THIS IS THE ERROR DIRECTION INSPECTION NEVER FINDS. A false POSITIVE inflates coverage and
    hides surfaces; a false NEGATIVE sends a review round to defend something already defended. The
    first is more dangerous, but the second is what wasted a seat.
    """
    head = io.open(path, encoding="utf-8").read(400)
    m = _GENERATED.search(head)
    return m.group(1) if m else None


def is_selective(pattern, sents):
    """Does this pattern DISTINGUISH a sentence in `sents`, or does it merely match the document?

    Both halves are load-bearing and each was written after the other one alone reported a lie:
    `_binds_literal_text` refuses structure (bold, a code span, an ISO date, whitespace), and
    `MAX_MATCH_SHARE` refuses breadth. A pattern matching nothing at all distinguishes nothing
    either, and saying so here rather than letting it sit in the compiled set is what lets a guard
    assert the word "selective" against this function instead of against a comment.
    """
    if not sents:
        return False
    if not _binds_literal_text(pattern):
        return False  # structure only: bold, a code span, a date, whitespace — binds nothing
    try:
        rx = re.compile(pattern, re.I)
    except re.error:
        return False
    matched = sum(1 for s in sents if rx.search(s))
    if matched > max(1, MAX_MATCH_SHARE * len(sents)):
        return False  # matches most of the document; binds none of it
    return matched > 0


def census(paper_key):
    path = PAPERS[paper_key]
    base = os.path.basename(path)
    sents = sentences(path)
    pats = [(h, p, w) for h, p, w in _pin_patterns() if h == base] + _test_patterns(base)
    compiled = []
    for _h, p, w in pats:
        if not is_selective(p, sents):
            continue
        compiled.append((re.compile(p, re.I), w))
    # ⛔⛔ A GENERATOR IS NOT A WITNESS, AND CREDITING IT AS ONE WAS A FALSE POSITIVE THIS FILE HELD
    # FOR ABOUT AN HOUR (2026-08-22). The reasoning was: the tables file is generated, an edit to it
    # fails `--check`, therefore every sentence in it is bound — and the first ablation agreed, twice
    # (a Table 1 cell and a numbered caption both went rc=1 STALE). ⚠ BUT THE ABLATION WAS MUTATING
    # THE WRONG OBJECT. Reproduction is not derivation: the captions are TYPED LITERALS inside
    # `aso_journal_tables.py`, so the realistic way the claim changes is that somebody edits the
    # generator, not the artifact. Measured that way — "ten-base-pair criterion" -> "eleven-base-pair"
    # in the generator, then regenerate — `--check` rc=0, all three linters rc=0, and the 24 tests
    # naming the file all pass. NOTHING notices.
    # ★ SO THE CREDIT IS WITHHELD. `_generator` stays because the distinction is worth naming, and
    # because the right ablation for a generated document mutates its SOURCE.
    rows = []
    for s in sents:
        hits = sorted({w for rx, w in compiled if rx.search(s)})
        rows.append({"sentence": s, "has_number": bool(re.search(r"\d", s)),
                     "read_by": hits, "covered": bool(hits)})
    return rows


def uncovered(paper_key):
    """The finding, printed on demand: the sentences of one document nothing selective reads.

    ⛔⛔ THIS IS NOT IN THE COMMITTED REPORT, AND THAT IS A DECISION WITH A MEASUREMENT BEHIND IT
    (2026-08-26). The report used to carry every uncovered sentence, which was affordable while the
    census read three documents of one submission. Widened to every publication endpoint it produced
    a **1.1 MB** artifact holding a second copy of the prose of 32 manuscripts — a fact stored twice
    (CLAUDE.md §1), stale the moment any of those papers is edited, and re-diffed in full on every
    regeneration. The counts are the thing a ratchet can hold; the sentences are a WORKING LIST for
    designing a review round, and they cost $0 to reproduce here at the moment they are wanted.
    """
    rows = census(paper_key)
    return {"with_a_number": [r["sentence"] for r in rows if r["has_number"] and not r["covered"]],
            "without_a_number": [r["sentence"] for r in rows
                                 if not r["has_number"] and not r["covered"]]}


#: The one committed copy of this census. ⚠ NAMED HERE rather than typed at each use, because
#: `--write`, `--check` and the freshness test all have to mean the same file.
ARTIFACT = os.path.join(HERE, "claim-coverage.json")


def build_report():
    """The whole census, as the artifact records it. ⛔ NO PRINTING AND NO WRITING.

    `--write` and `--check` must be the SAME derivation or the check verifies a second
    implementation of the census rather than the census. This repository has already shipped a
    `--check` that regenerated its own reference and exited 0 (see the note beside the CI step
    "EMC evidence artifacts reproduce from their generators"), and the defence against that is
    one producer function with two callers, not two functions that agree today.
    """
    report = {"_what": __doc__.strip().splitlines()[0],
              "_generated_by": "research/manuscripts/claim_coverage.py",
              "_scope": "every document a committed record calls a publication endpoint, or a part "
                        "one of those ships — never a list typed here. See "
                        "`claim_coverage.endpoint_documents`.",
              "named_by": NAMED_BY, "papers": {}}
    for key in PAPERS:
        rows = census(key)
        n = len(rows)
        cov = sum(r["covered"] for r in rows)
        num = [r for r in rows if r["has_number"]]
        num_cov = sum(r["covered"] for r in num)
        report["papers"][key] = {
            "sentences": n, "covered": cov,
            "with_a_number": len(num), "with_a_number_covered": num_cov,
            #: The uncovered sentences themselves are `--uncovered=<path>`, not a field here — see
            #: `uncovered()` for the 1.1 MB measurement that took them out of the artifact.
            "uncovered": n - cov, "uncovered_with_a_number": len(num) - num_cov,
        }
    return report


def render(report):
    """The exact bytes `--write` puts on disk, so `--check` can compare bytes and not opinions."""
    return json.dumps(report, indent=1, ensure_ascii=False) + "\n"


def disagreements(report, committed_text):
    """Every way the committed artifact differs from a live census. Empty list = it reproduces.

    ⛔⛔ WHY A DIFF AND NOT A BOOLEAN. The reader of a red gate has to know WHICH document moved, or
    the only actionable advice is "regenerate and hope" — and a regeneration is exactly what makes a
    real regression disappear into a green run. Each line names the field, the committed value and
    the live one.
    ⚠ THE FIELD COMPARISON RUNS BOTH WAYS, and then the bytes are compared as a backstop: a
    document dropped from the census leaves its counts behind looking like a reading of a document
    nothing measures, and a change to `named_by` (which records WHICH RECORD put each document in
    scope) moves no count at all while changing what the artifact says the census read.
    """
    try:
        committed = json.loads(committed_text)
    except ValueError as exc:
        return [f"the committed artifact is not readable JSON ({exc})"]
    if not isinstance(committed, dict):
        return ["the committed artifact is not a JSON object"]
    out = []
    live_papers, com_papers = report["papers"], committed.get("papers") or {}
    for paper, fields in live_papers.items():
        for field, value in fields.items():
            was = com_papers.get(paper, {}).get(field)
            if was != value:
                out.append(f"papers.{paper}.{field}: committed {was!r}, "
                           f"the census now reports {value!r}")
    out += [f"papers.{paper}: in the committed artifact but no longer censused, so its numbers are "
            f"a reading of nothing" for paper in sorted(set(com_papers) - set(live_papers))]
    for key in [k for k in report if k != "papers"]:
        if committed.get(key) != report[key]:
            out.append(f"{key}: the committed value is not the one this module now derives")
    out += [f"{key}: in the committed artifact and no longer produced at all"
            for key in sorted(set(committed) - set(report))]
    #: ⛔ AND IF EVERY FIELD AGREES AND THE BYTES DO NOT, SAY SO RATHER THAN PASSING. A hand edit
    #: that reformats or reorders the file leaves `--write` producing something different from what
    #: is committed, which is the staleness this gate exists to refuse.
    if not out and committed_text != render(report):
        out.append("every field agrees but the committed bytes are not what --write would produce "
                   "(a hand edit to formatting, ordering or whitespace)")
    return out


#: What `--check` prints above its diff. Kept as a constant so the guard that proves the check is
#: real can bind the message without re-typing it.
STALE_HEADER = "claim-coverage.json is stale — it is not what the live census computes:"
STALE_REMEDY = ("\nRe-run `python3 research/manuscripts/claim_coverage.py --write` and commit the "
                "result in THIS change.\n"
                "⛔ If you did not touch a manuscript, look at research/manuscripts/tests/: the "
                "census harvests its patterns from that corpus, so widening a guard's regex moves "
                "`covered` with no manuscript byte touched. That edit and this artifact are a pair "
                "even though they live in different directories.")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in argv
    check = "--check" in argv
    #: ⛔⛔ AN UNRECOGNISED FLAG IS AN ERROR, NOT A NO-OP, AND THAT IS THE WHOLE POINT OF THE CHECK
    #: MODE (AUT-PD-130). Until this line every argument this script did not know was silently
    #: ignored and the run exited 0 — so wiring `claim_coverage.py --verify` into a gate would have
    #: bought a green row that measured nothing, which is the exact defect recorded against
    #: `emc_systemic_therapy_pooling.py` in `.github/workflows/tests.yml`.
    unknown = [a for a in argv
               if a not in ("--write", "--check") and not a.startswith("--uncovered=")]
    if unknown:
        print(f"unrecognised argument(s): {' '.join(unknown)}\n"
              f"usage: claim_coverage.py [--write | --check | --uncovered=<repo-relative path>]",
              file=sys.stderr)
        return 2
    #: ⛔ AND THE TWO MODES MAY NOT BE COMBINED. A verify that regenerates its own reference first
    #: passes unconditionally; that is not a hypothetical failure mode in this repository.
    if write and check:
        print("--write and --check together verify nothing: the write would produce the reference "
              "the check then reads. Run one.", file=sys.stderr)
        return 2
    if check:
        report = build_report()
        if not os.path.exists(ARTIFACT):
            print(f"{os.path.relpath(ARTIFACT, REPO)} is missing.{STALE_REMEDY}", file=sys.stderr)
            return 1
        bad = disagreements(report, io.open(ARTIFACT, encoding="utf-8").read())
        if bad:
            print(STALE_HEADER + "\n  " + "\n  ".join(bad) + STALE_REMEDY, file=sys.stderr)
            return 1
        print(f"claim-coverage.json reproduces from the live census "
              f"({len(report['papers'])} documents)")
        return 0
    for arg in argv:
        if arg.startswith("--uncovered="):
            key = arg.split("=", 1)[1]
            if key not in PAPERS:
                print(f"{key} is not a censused document. The census reads what "
                      f"`claim_coverage.endpoint_documents` selects:\n  "
                      + "\n  ".join(PAPERS), file=sys.stderr)
                return 2
            found = uncovered(key)
            for half in ("with_a_number", "without_a_number"):
                print(f"\n=== uncovered, {half.replace('_', ' ')} "
                      f"({len(found[half])}) — {key}\n")
                for s in found[half]:
                    print(f"  * {s}")
            return 0
    report = build_report()
    for key, row in report["papers"].items():
        print(f"{key}: {row['covered']}/{row['sentences']} sentences read by something "
              f"({row['with_a_number_covered']}/{row['with_a_number']} of those stating a number)")
    if write:
        #: ⚠ THIS ARTIFACT MOVED OUT OF `aso/` ON 2026-08-26 AND THE MOVE IS THE POINT. While the
        #: census read one submission it was an ASO deposit artifact; it now reads every publication
        #: endpoint in the repository, and a repo-wide census filed under one paper's directory is a
        #: fact stored where nobody looking for it would look.
        io.open(ARTIFACT, "w", encoding="utf-8").write(render(report))
        print(f"wrote {os.path.relpath(ARTIFACT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
