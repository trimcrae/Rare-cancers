#!/usr/bin/env python3
"""Manuscript prose style — journal register, not repository register. ($0, stdlib)

WHY THIS EXISTS. This repository's house style is loud on purpose: glyphs that make a warning
impossible to skim past, bold that pins the load-bearing clause, and running commentary about why a
rule exists. That style earns its keep in CLAUDE.md, in the roadmap and in the JSON artifacts, where
the reader is a maintainer or an agent who needs to be stopped from repeating a specific mistake.

It is wrong in a manuscript. A journal reader is not being warned, and prose that keeps insisting on
its own honesty reads as advocacy rather than as a report. The tics are also recognisable as
machine-written, which costs the paper credibility it has otherwise earned.

WHAT IT CHECKS. Only files in TARGETS, and only their bodies. Frontmatter, fenced code, and any
section under an "Appendix" heading are exempt, because superseded-value bookkeeping is required by
CLAUDE.md rule 1.2 and belongs in an appendix rather than in the running text.

WHAT IT CANNOT CHECK. Whether the argument is any good, whether the register is consistent, or
whether a sentence is merely bad. It catches recurring mechanical tells. A clean run means the
known tics are absent, not that the prose is well written.

Usage:
  python3 research/manuscripts/lint_style.py                    # check (preflight / CI)
  python3 research/manuscripts/lint_style.py --report           # counts per file, exit 0
  python3 research/manuscripts/lint_style.py path/to/file.md    # check specific files
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

#: Manuscript bodies held to journal register. A file is added here when it becomes a submission
#: text; a memo, a plan or a findings note is NOT a submission text and must not be listed.
TARGETS = [
    "research/manuscripts/endpoint/response-endpoint-indolent-tumours.md",
    # ⭐ ADDED 2026-08-09, the day four endpoints were taken to submission form. Gate 5 checks
    # REGISTER, and until now it enforced that on exactly one file while three other submission
    # texts drifted freely — a rule filed where it cannot fire is absent (CLAUDE.md §6). Measured
    # before the rewrites: 96 findings in the ATR package (bold 42.4/1000 against a limit of 12),
    # 283 in the surface-target landscape, and em-dashes at 18.7/1000 against a limit of 6 in the
    # repurposing menu. All are clean now, and this list is what stops them going back.
    # ⛔ SUBMISSION TEXTS ONLY. A memo, a plan or a findings note must not be added here — the
    # house style is CORRECT everywhere else in this repository.
    "research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md",
    "research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis-SI.md",
    "research/manuscripts/dependency/emc-atr-collaborator-package.md",
    "research/manuscripts/repurposing/repurposing-hypotheses.md",
    "research/manuscripts/surface-targets/emc-surface-target-landscape.md",
    "research/manuscripts/surface-targets/emc-surface-target-landscape-si.md",
    # ⚠ REMOVED 2026-08-23, the day it was added. emc-icdo-9231-classification.md was listed here
    # as a submission text and is no longer one: trimcrae closed it as "not a paper" and it is now
    # a findings note. This list is SUBMISSION TEXTS ONLY, and the comment at the top of it says a
    # findings note must not be added — so it comes back out. The register rule did its job while
    # the file was aimed at a venue; a note is correctly written in house style.
    # ⭐ THE ASO SUBMISSION, ADDED 2026-08-12 WHEN IT BECAME A SUBMISSION TEXT RATHER THAN A
    # WORKING DOCUMENT. It passes on merit, not by exemption; its 24,000-word predecessor could not,
    # and the split is what made both readable — see the note below.
    # ⛔ DO NOT RESTATE ITS LENGTH HERE. Length and abstract length have ONE home,
    # `research/manuscripts/submission-metrics.json` (regenerate: `submission_metrics.py`), and the
    # live style densities are what a `lint_style.py` run prints. ⚠ *Superseded, retained: "Measured
    # on entry: 2,341 words, 274-word structured abstract … bold 6.8/1000 …, em-dashes 3.4/1000".*
    # Those were true on 2026-08-12 and false a day later — the paper more than tripled as the
    # pre-mRNA compartment, the censoring re-screen and Table 3 landed, and this comment went on
    # reading as a current measurement. That is the exact failure rule 1 exists to stop, sitting
    # inside the gate that enforces it.
    # ⛔ THE EXTENDED REPORT WAS REMOVED FROM THIS TARGET LIST ON 2026-08-25 (trimcrae:
    # "Remove any checks requiring it from the gate"). Nothing in the gate reads
    # fusion-junction-aso-research-article.md any more; the file stays in the tree as history.
    # ⭐ THE ASO SUPPORTING INFORMATION, ADDED 2026-08-16 — THE SAME SPLIT-HALVES HOLE
    # `lint_claims.py` records for the degrader SI, in the paper that is next to be deposited. The
    # 2026-08-16 editorial restructure moved six Methods blocks out of the research article and into
    # `fusion-junction-aso-supplementary-information.md`, and the moment it did, half the submission
    # left this gate: TARGETS names one file per paper, so a split narrows coverage silently while
    # the pass rate stays green — the shrinking-scope failure this list has now seen three times.
    # ⛔ AND THE SI IS NOT THE SAFE HALF FOR *REGISTER* EITHER. What a split moves out is the method
    # detail, which is where the house register survives longest: the bookkeeping voice ("Section
    # numbers here are prefixed **S**") is exactly the machine-written tell a reviewer meets first.
    # Measured on entry: 4 ERROR (2 bold-midsentence, 2 heading-style). They are SI-side text fixes
    # and are reported rather than silenced — a gate added with an exemption is not a gate.
    "research/manuscripts/aso/fusion-junction-aso-supplementary-information.md",
    # ⭐ THE CONDENSED JOURNAL SUBMISSION, ADDED 2026-08-20. It is a submission text from the
    # first commit rather than becoming one later, which is the mistake the ASO article row
    # above records: gate 5 checks REGISTER, and a manuscript absent from this list is not
    # checked at all rather than checked and passing.
    "research/manuscripts/aso/fusion-junction-aso-journal-article.md",
    # ⛔ THE TABLES FILE IS PROSE TOO, ADDED 2026-08-22 (round 14 seat 2). Its captions are spliced
    # into both journal PDFs and carry the two DO NOT ORDER verdicts. Until this line no
    # build-failing instrument read it at all, and a caption stating "four designs at two seams"
    # over a two-row, one-seam table shipped in both built PDFs with every gate green.
    "research/manuscripts/aso/fusion-junction-aso-journal-tables.md",
    # ⛔ THE REFERENCE LIST WAS NEVER HELD TO REGISTER EITHER, ADDED 2026-08-28 (round 11 seat 4, P1,
    # the same gap as the tables-file entry above, for the same document family). It is
    # hand-maintained prose in the submission, and adding it surfaced a real defect: its own
    # provenance banner carried two ⛔ glyphs — house register, not journal register — which is why
    # `_body_lines` above now exempts HTML comments rather than the entries here being wrapped in one.
    "research/manuscripts/aso/fusion-junction-aso-journal-references.md",
    # ⚠ THE COVER LETTER IS DELIBERATELY NOT HERE, AND IT IS IN `lint_claims` (round 15, 2026-08-22).
    # It was added to both gates and then removed from this one on measurement, not on preference:
    # this linter's rules are a MANUSCRIPT register, and a letter is a different genre. It fired
    # `second-person` on "Thank you for considering this manuscript" and on "Yours sincerely" —
    # correspondence conventions, not tics — and a gate that reports a salutation as a defect is one
    # its reader learns to skip, which costs the gate on the findings that are real.
    # ⛔ THE CLAIM GATE IS THE ONE THAT MATTERS FOR THIS FILE AND IT DOES READ IT. Every real finding
    # a reviewer has ever raised against the letter has been a CLAIM finding — an unhedged novelty
    # claim, a qualifier dropped off a paraphrase of the extended report, an "as well as" inverted
    # into a "rather than". Those are R1-R5's business, and `lint_claims.DEFAULT_TARGETS` carries it.
    # ⭐ THE EMC VACCINE DEVELOPMENT PATH, ADDED 2026-08-19 AS A SUBMISSION TEXT FROM THE START.
    # Written to this gate rather than retrofitted to it: it entered at bold 9.1/1000 and em-dashes
    # 0.0/1000, and its only findings were 9 sentence-shaped headings and one fragment, all fixed
    # before the first commit. ⛔ DO NOT RESTATE ITS DENSITIES HERE — a `lint_style.py` run prints
    # the live ones, and the comment above records what happened when a measurement was frozen into
    # this file and went on reading as current.
    "research/manuscripts/neoantigen/emc-vaccine-development-path.md",
    # ⭐ THE TRIAL-REACHABILITY SHORT REPORT, ADDED 2026-09-02. `PUB-STRATEGY-ARCH`, state `drafted`,
    # `target_venue: preprint`, `unit: short_report` — a submission text since 2026-08-09 that this
    # gate had never read, which is the SAME absent-guard shape the 2026-08-09 comment above records
    # for the other three endpoints. Measured on entry, before the rewrite: 33 ERROR — bold 54 runs
    # over 1,718 words = 31.4/1000 against a limit of 12.0, em-dash 12.2/1000 against 6.0, 14 glyph,
    # 11 bold-midsentence, 6 heading-style. Clean on entry to this list at 0 ERROR.
    # ⛔ THE CONVERSION CHANGED NO CLAIM, AND THAT WAS THE BINDING CONSTRAINT RATHER THAN THE COUNTS.
    # Every ⚠ and ⛔ in that paper carried a caveat or a refusal, so deleting the glyph without
    # rewriting the sentence would have deleted the flag: the warnings are now carried by the prose
    # ("The large screens are fields-limited and carry no eligibility text, so they can identify a
    # candidate and can never confirm one"). Sentence-level diff with emphasis and dash punctuation
    # normalised: every hunk is punctuation, a heading or a connective. Record:
    # `research/autonomy/sprint-2026-09-01/S48-ELIGIBILITY-REGISTER.md`.
    "research/manuscripts/care-delivery/emc-trial-reachability.md",
]

# ⛔ fusion-junction-aso-working-record.md IS DELIBERATELY NOT IN `TARGETS`, AND THAT IS NOW CORRECT
# RATHER THAN DEFERRED (2026-08-12). It is no longer a manuscript: the working record is the
# provenance archive of the ASO line — every analysis in full plus the superseded-value register
# that rule 1.2 REQUIRES. Gate 5 checks journal REGISTER, and that file's audience is a maintainer,
# so the house style is right there.
#
# ⚠ Superseded, retained (2026-08-27): this comment used to name
# `fusion-junction-aso-research-article.md` — the extended report — as "the submission". It is not,
# and had not been since 2026-08-25, when the extended report was removed from `TARGETS` (trimcrae:
# "Remove any checks requiring it from the gate"); the comment 45 lines ABOVE, inside the list,
# already said so — "the file stays in the tree as history". THE SUBMISSION IS THE JOURNAL ARTICLE,
# `fusion-junction-aso-journal-article.md`, which is the row in `TARGETS` above. Two comments in one
# gate described two different regimes, and the wrong one was the one a reader meets last. Measured
# 2026-08-27 by the round-10 guard-coverage audit (STALE_GUARD_TEXT 1) and re-checked here: no
# element of `TARGETS` contains "research-article".
#
# ⚠ Superseded, retained: the measurement below was taken when the working record still WAS the
# manuscript, and it is kept because it is the EVIDENCE FOR SPLITTING rather than rewriting. Getting
# bold from 33.2 to under 12 across 20,915 words would have meant stripping emphasis off the very
# clauses that stop the paper over-claiming ("**predicted**, not demonstrated", "**0 of 5** clean").
# A single document carrying both a journal argument and a correction ledger cannot satisfy one
# audience without failing the other, and the attempt produced a 24,000-word file in which — as an
# editorial review put it — no sentence stated a result the manuscript did not itself withdraw.
#
#     20,915 words · bold 33.2/1000 (limit 12) · em-dash 17.5/1000 (limit 6)
#     286 bold-midsentence · 127 glyph · 14 heading-style · 4 banned-phrase
#
# ⚠ The old path `fusion-junction-aso-paper.md` no longer exists: it was renamed to the working
# record, and the short communication took its place as the deliverable. The name is written here
# once so a reader meeting it in history can resolve it.
_NOT_YET_A_SUBMISSION_TEXT_IN_REGISTER = "research/manuscripts/aso/fusion-junction-aso-working-record.md"

# ⛔⛔ THE 18 PUBLICATION ENDPOINTS `TARGETS` DOES NOT REACH, AND WHY EACH ONE IS OUT (2026-08-28,
# AUT-PD-141). `TARGETS` above is this repository's ONE HOME for "is this a submission text", and
# `lint_readability._targets` imports it so the pair cannot drift. Both then read a list somebody
# typed. `systems/graph/publications.json` is the source of truth for what a publication endpoint
# IS, and until this constant existed the two sets had never been compared: 25 graph endpoints
# resolve to a `.md` on disk and 7 of them are in `TARGETS`, so 18 live endpoints sat outside the
# register screen, outside the readability screen and outside `readability-baseline.json` — with
# nothing anywhere recording that as a decision rather than an oversight.
#
# ⭐ THE CONSEQUENCE REACHES THE PUBLISH BAR, WHICH IS WHY THIS IS A RECORD AND NOT A COMMENT.
# `publish_bar.clause_7_readable_enough_to_review` measures the outgoing document directly, so its
# SENTENCE-CEILING half fires for any endpoint. Its CAUTION-FLOOR half — the one
# `lint_readability`'s docstring calls the failure mode that matters, a paper buying readability by
# dropping a hedge — reads `readability-baseline.json`, which is written from `TARGETS`. For an
# endpoint absent from `TARGETS` that lookup returns None and the clause returns PASS reading
# "(no baseline pinned)": a clause that cannot fail, reported as passing, in the file whose own
# docstring says an unreadable artifact is a FAILED clause and never a skipped one.
#
# ⛔ AND THE FIX IS NOT "ADD THE PATHS", WHICH WAS MEASURED BEFORE IT WAS REJECTED. `lint_file` over
# these 18 returns 2795 findings in 0.59 s — 1170 from the 43,680-word degrader paper alone —
# because several are internal program documents whose callout glyphs are CORRECT for their reader.
# A blanket add reddens the commit loop on documents nobody is submitting, and a gate that reds on
# true input is the gate somebody loosens.
#
# ★★ SO EVERY ROW BELOW IS A DECISION SOMEBODY HAD TO TAKE, AND SILENCE FAILS.
# `tests/test_every_publication_endpoint_is_style_screened_or_recorded.py` asserts that every graph
# endpoint resolving to a `.md` is in `TARGETS` or here, and that nothing is in both. Two decisions
# exist, and they are not the same kind of thing:
#
#   `not_a_submission_text` — the graph's own `target_venue` says the document is aimed at no
#       outside reader. That basis is not this file's opinion:
#       `emc-icdo-9231-classification.md` was REMOVED from `TARGETS` on 2026-08-23 when trimcrae
#       closed it as "not a paper" (the comment inside the list above records it), and the venue
#       the graph gives it is `internal_note`. The guard re-reads `venue_when_decided` against the
#       graph on every run, so a document re-aimed at a preprint reopens its own exemption without
#       anyone having to remember it.
#
#   `unscreened_debt` — the document IS aimed outward (`preprint` or `journal_submission`) and this
#       screen has never read it. That is a recorded DEFECT, and it is written here in those words
#       so it cannot be read as an exemption. `findings_when_filed` pins what `lint_file` measured
#       on 2026-08-28 at origin/main 170314393; the guard re-measures and fails if a count RISES,
#       so a document may not get worse while it waits, and fails if a count reaches 0, because a
#       document that could be screened and is not is this defect again. It is the contract
#       `submission-residue-baseline.json` already records: the count is meant to fall.
#       ⛔ A DEBT ROW IS NOT PERMISSION TO POST. Clause 7's caution half stays inert for that paper
#       until the document enters `TARGETS` and `--write-baseline` re-pins the baseline.
#
# ⛔ THIS CONSTANT IS A RECORD, NOT AN INPUT TO THE LINTER — the same shape as
# `_NOT_YET_A_SUBMISSION_TEXT_IN_REGISTER` above and for the same reason: a reader deciding whether
# to add a path to `TARGETS` must meet the reasoning in the file where they are making the edit.
UNSCREENED_ENDPOINT_DECISIONS = {
    # ── decided: the graph aims these at no outside reader ────────────────────────────────────
    "research/manuscripts/care-delivery/emc-icdo-9231-classification.md": {
        "decision": "not_a_submission_text",
        "venue_when_decided": "internal_note",
        "why": "Removed from TARGETS on 2026-08-23 when trimcrae closed it as 'not a paper', and "
               "the graph agrees at target_venue internal_note. Its single finding is one glyph, "
               "so it is out on GENRE and not on cost. This row is that removal written where a "
               "guard can read it instead of only in a comment above the list.",
    },
    "research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md": {
        "decision": "not_a_submission_text",
        "venue_when_decided": "internal_note",
        "why": "The route record for the monovalent pocket line, aimed at no outside reader "
               "(target_venue internal_note). Its reader is a maintainer deciding whether to "
               "reopen the route, and its 57 glyphs and 10 sentence-shaped headings are that job "
               "done correctly. Holding it to journal register would strip the emphasis off the "
               "verdicts the document exists to carry.",
    },
    "research/manuscripts/dependency/degrader-vs-synthetic-lethal.md": {
        "decision": "not_a_submission_text",
        "venue_when_decided": "internal_note",
        "why": "A route-comparison memo for this program's own sequencing decisions, aimed at no "
               "outside reader (target_venue internal_note). It reports which of two routes to "
               "spend on rather than a result to a journal reader, and its 40 mid-sentence bolds "
               "are the comparison's load-bearing clauses.",
    },
    # ── recorded debt: aimed outward, never screened ──────────────────────────────────────────
    "research/manuscripts/degrader/nr4a3-degrader-paper.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "journal_submission",
        "findings_when_filed": 1170,
        "why": "The largest register debt here: 43,680 words aimed at a journal, 1042 of the "
               "findings mid-sentence bold and 92 glyphs. Clearing it is a rewrite, not a pass, "
               "and the ASO line's precedent says the answer is probably a SPLIT — a journal "
               "argument and a working record cannot satisfy one audience without failing the "
               "other.",
    },
    "research/manuscripts/dependency/emc-atr-vulnerability-assessment.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 287,
        "why": "Aimed at a preprint and still in house register: 133 glyph findings and 25 "
               "sentence-shaped headings over 9,004 words, at bold 41.9/1000 against a limit of "
               "12. The collaborator package built from the same route IS in TARGETS and passes, "
               "so the register is reachable for this material.",
    },
    "research/manuscripts/methods-record/degrader-methods-failure-record.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "journal_submission",
        "findings_when_filed": 189,
        "why": "A methods-failure record the graph aims at a journal. Its 75 glyphs and 18 "
               "sentence-shaped headings are the house register a journal reader does not share; "
               "the negative it reports is the reason to submit it, and the register is the "
               "reason it cannot go as written.",
    },
    "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 188,
        "why": "⛔ THE INSTANCE. This is the manuscript "
               "test_the_census_reads_every_publication_endpoint.py records as a live publication "
               "endpoint hardened by blind review seats while the claim census did not list it at "
               "all. It was outside THIS screen and outside the readability baseline for the whole "
               "of that hardening too — the same defect, in a second instrument, found separately "
               "and two days later.",
    },
    "research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "journal_submission",
        "findings_when_filed": 121,
        "why": "13,903 words aimed at a journal submission, at 79 mid-sentence bolds, 25 glyphs "
               "and 9 sentence-shaped headings. Large enough that a register pass is real work "
               "and small enough that it is one document's work rather than a split.",
    },
    "research/manuscripts/program/emc-treatment-roadmap.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "journal_submission",
        "findings_when_filed": 112,
        "why": "The graph aims the treatment roadmap at a journal submission, and it is written as "
               "a program document: em-dashes at 22.5/1000 against a limit of 6, 80 mid-sentence "
               "bolds, 19 glyphs. ⚠ Whether this is a paper AT ALL is the prior question — if the "
               "answer is no, the honest edit is the graph's venue, not this row.",
    },
    "research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 107,
        "why": "Aimed at a preprint, 4,713 words, and never read by this gate: 64 mid-sentence "
               "bolds, 38 glyphs and 2 emphasis fragments. Its sibling in the same directory, "
               "emc-vaccine-development-path.md, was written TO this gate from the start and "
               "passes, which is the measured precedent for what a pass costs here.",
    },
    "research/manuscripts/methods-record/closed-routes-negative-record.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 95,
        "why": "A negative record aimed at a preprint, at 33 glyphs and 14 sentence-shaped "
               "headings over 5,872 words. A negative is the class of paper whose value depends "
               "most on not reading as advocacy, which is exactly what this gate checks.",
    },
    "research/manuscripts/neoantigen/hla-coverage-emc.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 81,
        "why": "3,093 words aimed at a preprint, at bold 30.7/1000 against a limit of 12, with 63 "
               "mid-sentence bolds and 3 emphasis fragments. Small enough to clear in one pass.",
    },
    "research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 72,
        "why": "4,099 words aimed at a preprint, at 58 mid-sentence bolds, 9 glyphs and 3 banned "
               "phrases, with em-dashes at 15.4/1000 against a limit of 6. Its claim is that a "
               "design cannot be built for a stated reason, so the register matters: house "
               "emphasis on a negative reads as advocacy.",
    },
    "research/manuscripts/tcip/tcip-induced-interface-preprint.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 54,
        "why": "Names itself a preprint in its own filename and is aimed at one in the graph, and "
               "has never been screened: 43 mid-sentence bolds and 4 sentence-shaped headings "
               "over 2,394 words. The smallest outward-aimed document here after the two below.",
    },
    "research/manuscripts/modality-census/cancer-modality-census.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 49,
        "why": "3,651 words aimed at a preprint, and unusually glyph-dominated for its size: 31 "
               "of the 49 findings are decorative glyphs, against only 10 mid-sentence bolds. A "
               "glyph-dominated profile is the cheapest kind of debt to clear.",
    },
    "research/manuscripts/dependency/emc-biomarker-selected-classes.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 36,
        "why": "1,806 words aimed at a preprint, at 19 glyphs, 11 mid-sentence bolds and 4 "
               "sentence-shaped headings. Short, and dominated by findings that are mechanical "
               "rather than structural.",
    },
    "research/manuscripts/care-delivery/emc-trial-reachability.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 33,
        "why": "1,718 words aimed at a preprint, at bold 31.4/1000 against a limit of 12, with 14 "
               "glyphs and 6 sentence-shaped headings. A care-delivery paper whose reader is a "
               "clinician, which is the audience the house register serves worst.",
    },
    "research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md": {
        "decision": "unscreened_debt",
        "venue_when_decided": "preprint",
        "findings_when_filed": 27,
        "why": "The cheapest debt on this list: 27 findings over 1,437 words, aimed at a preprint. "
               "11 glyphs, 10 mid-sentence bolds and 3 sentence-shaped headings, with no banned "
               "phrase beyond one. Clearing this one first is what proves the pass is a pass.",
    },
}


# Densities are per 1000 words. They are deliberately generous: the aim is to catch prose that
# leans on a device, not to ban the device. A paper that trips one of these is not using emphasis,
# it is using emphasis instead of sentence structure.
MAX_BOLD_PER_1000 = 12.0
MAX_EMDASH_PER_1000 = 6.0

GLYPHS = "⭐⛔⚠★◐○●✅❌📏⏱⏰📱🔬⚖⊕⇢⭑📊🌙♦✕⏸➜▸→⇒✦❗❓‼"

BANNED = [
    (r"\bthat is the point\b", "rhetorical closer; state the point instead of announcing it"),
    (r"\bwhich is precisely why\b", "rhetorical connective; use 'because' or start a new sentence"),
    (r"\bfor (that|this) reason\b(?=[^.]*\bstated\b)", "meta-commentary about ordering"),
    (r"\bstated (first|here|at full strength)\b", "narration about how the paper states things"),
    (r"\bdeliberately\b", "usually defends a choice the reader has not questioned"),
    (r"\b(Crucially|Importantly|Notably|Significantly),", "tells the reader what to find important"),
    (r"\bit is worth (noting|remembering|saying)\b", "if it is worth saying, say it"),
    (r"\bworth noting\b", "if it is worth noting, note it"),
    (r"\bthe honest (verb|answer|form|version|statement)\b", "self-describing candour"),
    (r"\bstated honestly\b", "self-describing candour"),
    (r"\brather than deflect(ed|ing)?\b", "self-describing candour"),
    (r"\bto be clear\b", "filler"),
    (r"\bcosts? (a sentence|nothing)\b", "rhetorical costing; give the actual cost"),
    (r"\bis not a (bug|feature)\b", "engineering idiom, out of register"),
    (r"\bthe whole (point|of it) is\b", "rhetorical closer"),
    (r"\bdoes exactly that\b", "self-congratulation"),
    (r"\breason (this|it) exists\b", "meta-commentary"),
    (r"\blet me\b", "first-person address, out of register for a manuscript"),
    (r"\bwe should be clear\b", "filler"),
]

SELF_REFERENTIAL = [
    (r"\bthis (paper|manuscript|section) (does not|refuses to|declines to)\b.{0,40}\b(hide|soften|smooth|deflect)",
     "narration about the paper's own candour"),
    (r"\b(stated|placed|put) in the abstract rather than\b", "narration about the paper's own structure"),
    (r"\bthe objection that would sink\b", "dramatised limitation"),
    (r"\bat (its|their) full strength\b", "dramatised limitation"),
    (r"\bthis is the (finding|objection|argument) with the\b", "editorialising about the paper's own content"),
]

SECOND_PERSON = re.compile(r"(?<![\w-])(you|your|yours)(?![\w-])", re.I)

# A short sentence opening with a negation or restriction and carrying no finite verb is the
# fragment-for-emphasis tic ("Not a landmark result.", "Only in one direction.").
FRAGMENT = re.compile(r"(?:^|(?<=[.!?]\s))(Not|Never|Only|No)\b([^.!?]{0,60})[.!?]")
# ⭐ `exists?` ADDED 2026-08-25, and it is a gap in this list rather than a relaxation of the rule.
# Nucleic Acid Therapeutics requires the disclosure sentence "No competing financial interests
# exist." verbatim. That is a COMPLETE sentence — subject "No competing financial interests", finite
# verb "exist" — and it was reported as a fragment only because the verb was missing from this
# enumeration. ⛔ The rule still fires on a real fragment: "No competing financial interests." has no
# verb at all and is caught, which is asserted in the mutation check beside this file's own tests.
FINITE_VERB = re.compile(
    r"\b(is|are|was|were|has|have|had|does|do|did|will|would|can|could|may|might|must|shall|"
    r"should|remains?|becomes?|shows?|gives?|carries|holds?|means?|makes?|exists?)\b", re.I)

HEADING_VERBS = re.compile(
    r"\b(is|are|was|were|does|do|did|cannot|can|must|should|would|will|has|have|means|makes|"
    r"leaves|gives|shows|comes|goes|fails|survives|changes)\b", re.I)


def _strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:], i + 1
    return lines, 0


def _body_lines(path):
    """Yield (lineno, text) for body prose: no frontmatter, no fences, no appendices, no HTML
    comments.

    ⚠ HTML COMMENTS ADDED 2026-08-28 (round 11 seat 4's target-list fix surfaced it). An
    `<!-- ... -->` block never renders in the typeset PDF, so it is maintainer bookkeeping in
    exactly the sense frontmatter is — `fusion-junction-aso-journal-references.md`'s provenance
    banner carries two decorative ⛔ glyphs for a maintainer reading the markdown, and would have
    tripped this gate the moment it was added to TARGETS despite never reaching a reader.
    """
    with open(path, encoding="utf-8") as fh:
        raw = fh.read().split("\n")
    body, offset = _strip_frontmatter(raw)
    in_fence = False
    in_comment = False
    in_appendix = False
    seen_title = False
    table_header_next = False
    out = []
    for i, line in enumerate(body):
        lineno = offset + i + 1
        if in_comment:
            if "-->" in line:
                line = line.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        # A same-line-closed `<!-- ... -->` comment must lose only the comment SPAN, not the
        # whole line -- this article's citation markers (`<sup>1</sup><!--PMID:...-->`) sit
        # mid-sentence, so dropping the whole line blinded every style check over the prose that
        # follows them (round 12 seat 1, verified by mutation: real content silently uncaught).
        had_comment = False
        while "<!--" in line:
            had_comment = True
            before, rest = line.split("<!--", 1)
            if "-->" in rest:
                line = before + " " + rest.split("-->", 1)[1]
            else:
                line = before
                in_comment = True
                break
        if had_comment and not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        heading_text = None
        if m:
            in_appendix = bool(re.match(r"^appendix\b", m.group(2).strip(), re.I))
            # The document title is the first H1 and is exempt from the noun-phrase rule. A paper
            # title is allowed to be a sentence -- that is what titles are -- and holding it to a
            # rule written for section headings would force a worse title to satisfy a linter.
            if m.group(1) == "#" and not seen_title:
                seen_title = True
            else:
                heading_text = m.group(2)
        if in_appendix:
            continue
        # A markdown table's header row legitimately uses bold; its separator marks it.
        is_sep = bool(re.match(r"^\|[\s:|-]+\|?$", stripped))
        out.append((lineno, line, table_header_next, heading_text))
        table_header_next = is_sep
    return out


def _word_count(entries):
    n = 0
    for _, line, _, _ in entries:
        n += len(re.findall(r"[A-Za-z][A-Za-z'-]*", line))
    return max(n, 1)


# ── FIGURE SOURCES ────────────────────────────────────────────────────────────────────────
#: ⛔ A FIGURE TITLE IS SUBMISSION TEXT AND THIS GATE HAD NEVER SEEN ONE (trimcrae, 2026-08-10,
#: on a screenshot: "The header language in this diagram is unprofessional and painfully obvious
#: that it's Claude talking"). The reason is structural rather than an oversight in any one file:
#: this linter reads `.md`, and every figure title, axis label and caption in this repository is a
#: Python string inside a generator. So four manuscripts passed gate 5 cleanly while shipping a
#: figure captioned "This QUALIFIES the route rather than supporting it" — mid-sentence capitals
#: for emphasis, an argument with the reader, and the house register at its most recognisable, in
#: the element a reviewer looks at first.
FIGURE_SOURCES = [
    "research/modalities/emc_mtap_prmt5_figures.py",
    "research/manuscripts/figures/repurposing_design_figure.py",
]

#: Emphasis capitals: an all-caps run of 4+ letters that is not an accepted acronym or gene symbol.
FIG_SHOUT = re.compile(r"(?<![A-Z0-9:/_-])([A-Z]{4,})(?![A-Z0-9:/_-])")
FIG_SHOUT_OK = {
    "MTAP", "PRMT", "CDKN", "EWSR", "LGFMS", "CRISPR", "DGID", "TXGNN", "GRG", "RGG",
    "TRUE", "FALSE", "TYPE", "NOTE",
}

#: ⚠ SCOPED TO WHAT IS ACTUALLY RENDERED, by walking calls rather than every string constant. A
#: first version linted every literal and its only finding was a console message, `--check: DRIFT`,
#: which no reviewer will ever read. Docstrings, comments, paths and CLI output are not figure text,
#: and a gate that flags them trains people to ignore it. The house register BELONGS in a comment
#: explaining why a rule exists; it does not belong on an axis.
FIG_RENDERERS = {"set_title", "set_xlabel", "set_ylabel", "suptitle", "text", "annotate",
                 "set_xticklabels", "set_yticklabels", "figtext"}
FIG_RENDERED_KW = {"label", "title", "xlabel", "ylabel"}


def lint_figure_source(path):
    """Lint the strings a figure generator actually renders into a figure."""
    import ast
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except (OSError, SyntaxError):
        return None

    targets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = (node.func.attr if isinstance(node.func, ast.Attribute)
                else node.func.id if isinstance(node.func, ast.Name) else "")
        parts = list(node.args) if name in FIG_RENDERERS else []
        parts += [kw.value for kw in node.keywords if kw.arg in FIG_RENDERED_KW]
        for part in parts:
            for sub in ast.walk(part):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    targets.append(sub)

    findings, seen = [], set()
    for c in targets:
        t = c.value
        if len(t) < 18 or " " not in t.strip() or (c.lineno, t) in seen:
            continue
        seen.add((c.lineno, t))
        flat = " ".join(t.split())
        for ch in GLYPHS:
            if ch in flat:
                findings.append((c.lineno, "ERROR", "glyph",
                                 f"decorative glyph {ch!r} in figure text: {flat[:70]}"))
                break
        for pat, why in BANNED + SELF_REFERENTIAL:
            if re.search(pat, flat, re.I):
                findings.append((c.lineno, "ERROR", "banned-phrase", f"{why}: {flat[:70]}"))
        shouts = [w for w in FIG_SHOUT.findall(flat) if w not in FIG_SHOUT_OK]
        if shouts:
            findings.append((c.lineno, "ERROR", "emphasis-capitals",
                             f"all-caps for emphasis {shouts[:3]} in figure text: {flat[:60]}"))
    return {"path": path, "findings": findings, "words": 0,
            "bold_per_1000": 0.0, "emdash_per_1000": 0.0}


def lint_file(path):
    findings = []
    full = os.path.join(ROOT, path) if not os.path.isabs(path) else path
    if not os.path.exists(full):
        return None
    entries = _body_lines(full)
    words = _word_count(entries)

    bold_runs = 0
    emdashes = 0

    for lineno, line, is_table_header, heading in entries:
        for ch in line:
            if ch in GLYPHS:
                findings.append((lineno, "ERROR", "glyph",
                                 f"decorative glyph {ch!r} in manuscript body"))
                break

        emdashes += line.count("—")

        for m in re.finditer(r"\*\*(.+?)\*\*", line):
            bold_runs += 1
            if is_table_header or heading:
                continue
            prefix = line[:m.start()]
            # Bold opening a line, a list item or a table cell is a label; bold after running
            # text is emphasis inside a sentence, which is the tic.
            if re.search(r"[A-Za-z0-9,)][\s]*$", prefix) and not re.match(r"^[\s>|*\-+\d.]*$", prefix):
                findings.append((lineno, "ERROR", "bold-midsentence",
                                 f"bold inside a sentence: **{m.group(1)[:48]}**"))

        # ⛔ AND THE SAME CHECK ACROSS THE LINE BREAK (2026-08-12). The scan above is per LINE, so
        # `**fifty-five of seventy carry\nload at or below chance**` — bold whose opening and
        # closing markers sit on different lines — never matched, and two of them survived a clean
        # gate into the submission draft. In a hard-wrapped manuscript that is not an exotic case:
        # it is what happens to any emphasis long enough to be worth flagging. Reported at the
        # OPENING line, and only when the next line continues it, so a `**` that merely appears
        # twice on adjacent lines is not miscounted as one span.
        if line.count("**") % 2 == 1:
            nxt = next((ln for (n, ln, _, _) in entries if n == lineno + 1), None)
            if nxt is not None and "**" in nxt and not (is_table_header or heading):
                prefix = line[:line.rfind("**")]
                if re.search(r"[A-Za-z0-9,)][\s]*$", prefix) and \
                        not re.match(r"^[\s>|*\-+\d.]*$", prefix):
                    span = (line[line.rfind("**"):] + " " + nxt.split("**")[0]).strip("* ")
                    findings.append((lineno, "ERROR", "bold-midsentence",
                                     f"bold inside a sentence, across a line break: "
                                     f"**{span[:48]}**"))

        for pat, why in BANNED:
            mm = re.search(pat, line, re.I)
            if mm:
                findings.append((lineno, "ERROR", "banned-phrase",
                                 f"{mm.group(0)!r} — {why}"))
        for pat, why in SELF_REFERENTIAL:
            mm = re.search(pat, line, re.I)
            if mm:
                findings.append((lineno, "ERROR", "self-referential",
                                 f"{mm.group(0)[:48]!r} — {why}"))

        mm = SECOND_PERSON.search(re.sub(r"`[^`]*`", "", line))
        if mm and not line.strip().startswith(">"):
            findings.append((lineno, "ERROR", "second-person",
                             f"{mm.group(0)!r} addresses the reader directly"))

        if heading:
            # ⚠ THE SECTION LABEL IS STRIPPED BEFORE THE NOUN-PHRASE TEST, AND A SUPPORTING-
            # INFORMATION LABEL CARRIES A LETTER. `S1 · Target-site accessibility` lost only the
            # `1 · ` under the old pattern, so the finding printed `'STarget-site accessibility …'`
            # — a mangled quotation of the heading the author has to find and fix. The label also
            # counts toward the >10-word test, so an unstripped prefix is not purely cosmetic.
            # Anchored at the start: only a leading `S1 ·` / `S12.3 ·` label is a label; a `·` mid-
            # heading is punctuation and must survive.
            h = re.sub(r"\*\*|`|^\s*[A-Za-z]?\d[\d.]*\s*·\s*|[0-9]+\s*·\s*", "", heading).strip()
            if h.endswith("?"):
                findings.append((lineno, "ERROR", "heading-style",
                                 f"heading is a question: {h[:60]!r}"))
            elif HEADING_VERBS.search(h) or len(h.split()) > 10:
                findings.append((lineno, "ERROR", "heading-style",
                                 f"heading is a sentence, not a noun phrase: {h[:60]!r}"))

        for mm in FRAGMENT.finditer(line):
            frag = mm.group(0)
            if not FINITE_VERB.search(frag) and len(frag.split()) <= 8:
                findings.append((lineno, "ERROR", "fragment",
                                 f"sentence fragment used for emphasis: {frag.strip()!r}"))

    bold_density = bold_runs * 1000.0 / words
    emdash_density = emdashes * 1000.0 / words
    if bold_density > MAX_BOLD_PER_1000:
        findings.append((0, "ERROR", "bold-density",
                         f"{bold_runs} bold runs over {words} words = "
                         f"{bold_density:.1f}/1000, limit {MAX_BOLD_PER_1000}"))
    if emdash_density > MAX_EMDASH_PER_1000:
        findings.append((0, "ERROR", "emdash-density",
                         f"{emdashes} em-dashes over {words} words = "
                         f"{emdash_density:.1f}/1000, limit {MAX_EMDASH_PER_1000}"))

    return {"path": path, "words": words, "findings": findings,
            "bold_per_1000": round(bold_density, 1),
            "emdash_per_1000": round(emdash_density, 1)}


def main(argv):
    report = "--report" in argv
    paths = [a for a in argv if not a.startswith("--")] or TARGETS

    results = [r for r in (lint_file(p) for p in paths) if r]
    if not [a for a in argv if not a.startswith("--")]:
        results += [r for r in (lint_figure_source(p) for p in FIGURE_SOURCES) if r]
    if not results:
        print("lint_style: no target files present — nothing to check")
        return 0

    errors = 0
    for r in results:
        by_kind = {}
        for _, sev, kind, _ in r["findings"]:
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if sev == "ERROR":
                errors += 1
        print(f"\n{r['path']}  ({r['words']} words, bold {r['bold_per_1000']}/1000, "
              f"em-dash {r['emdash_per_1000']}/1000)")
        if not r["findings"]:
            print("  clean")
            continue
        print("  " + ", ".join(f"{k}={v}" for k, v in sorted(by_kind.items())))
        if not report:
            for lineno, sev, kind, msg in r["findings"][:200]:
                loc = f"{r['path']}:{lineno}" if lineno else r["path"]
                print(f"  ::{sev.lower()} file={r['path']},line={lineno}::[{kind}] {loc}: {msg}")

    print(f"\nlint_style: {errors} ERROR across {len(results)} file(s)")
    if report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
