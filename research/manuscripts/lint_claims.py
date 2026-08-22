#!/usr/bin/env python3
"""Language-discipline linter for the NR4A3 degrader manuscript and its SI.

WHY THIS EXISTS
---------------
The roadmap (`research/manuscripts/nr4a3-program-map.md`) -> "Honest scope and language
discipline (apply everywhere, including the manuscript)" states hard rules about what the
manuscript may and may not assert. ⚠ THAT SECTION MOVED ON 2026-08-02: it used to live in
`STRATEGY.md`, and the roadmap merge physically moved it -- heading string unchanged -- into
the roadmap, which is now the one document the program is steered by. The 21 provenance
strings below name the section, not the file, so a future move needs no edit here; the file
name is stated once, in this paragraph. Until this linter existed those rules had **zero
automated enforcement** -- they were a prose instruction that a
human or an agent had to remember. A 2026-07-24 audit reported a "linter FAIL (2 ERROR,
incl. SI:89 'efficacy')" that turned out to be a naive substring match: every "efficacy"
hit in the SI is a *disclaimer* ("makes no efficacy claim", "not EMC efficacy"). That
false positive is the design brief for this file:

    A substring match on a regulated word is NOT a violation. The violation is asserting
    the regulated claim. Negated / disclaimed / explicitly-scoped-out uses are CORRECT
    usage and must pass, or the linter will be ignored -- which is worse than no linter.

So every regulated pattern here is scanned at SENTENCE granularity and cleared when the
same sentence carries a disclaimer marker. Only the phrases that are wrong in *every*
context are hard errors.

RULES IMPLEMENTED (each cites its roadmap source section)
----------------------------------------------------------
  R1  earned-phrase substitutions      roadmap "selective hit" -> "predicted selective candidate" etc.
  R2  never-imply set                  roadmap "Never imply proteome-wide selectivity, EMC efficacy,
                                       safety, a therapeutic window, or clinical readiness."
  R3  novelty right-sizing             roadmap "Novelty is incremental, not landmark."
  R4  evidentiary-verb discipline      no computational result "proves" / "confirms" / "establishes"
  R5  measured-vs-projected            "measured" must not be attached to a projected cost/number

EXIT CODE
---------
  0  no ERRORs (WARNs may be present)
  1  one or more ERRORs

Stdlib only, no pip, runs in CI on every push (see .github/workflows/tests.yml).

Usage:
    python3 research/manuscripts/lint_claims.py                 # lint the default file set
    python3 research/manuscripts/lint_claims.py path/to/doc.md  # lint specific files
    python3 research/manuscripts/lint_claims.py --json          # machine-readable
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The manuscript IS the preprint IS the submission (CLAUDE.md single-source-of-truth rule),
# so the default set is the paper + its SI. Other docs can be passed explicitly.
DEFAULT_TARGETS = [
    "research/manuscripts/degrader/nr4a3-degrader-paper.md",
    "research/manuscripts/degrader/nr4a3-degrader-paper-SI.md",
    # ⛔ ADDED 2026-08-08 — A MANUSCRIPT IS PICKED UP FROM THE PUBLICATION REGISTER; ITS SI IS NOT.
    # `_publication_documents()` reads `publications.json` -> `publications[].document.file`, which
    # names one file per endpoint. So the moment a paper is split into a main text plus an SI, HALF
    # OF IT LEAVES THE LINTED SET AND NOTHING SAYS SO — the same shrinking-scope failure recorded
    # below for `systems/views/plan.md`, and the degrader SI is in this list by hand for exactly
    # that reason rather than by any rule.
    #
    # ⚠ AND THE SI IS NOT THE SAFE HALF. Splitting moves the DETAIL out, so what lands in the SI is
    # the fuller version of every hedged sentence: for the transcriptional-output paper that is the
    # six-arm PPARγ activity reading with its adipogenic ceiling, the pre-registered decision rule,
    # and the complete evidence catalogue with its per-row assay claims. Those are the sentences most
    # able to drift from "set-specific up against a size-matched null" into "PPARγ is active in EMC".
    "research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-SI.md",
    # Added 2026-08-02. The program map was linted by lint_consistency (pinned NUMBERS) but by
    # nothing that checks claim LANGUAGE -- which is how a table of bare "PASSES" verdicts and a
    # "Chemical basis: OK strong, and already measured" cell (whose owning artifact is not in this
    # repository) survived a green build, in the one file CLAUDE.md tells every session to read
    # first. R4-shaped over-claims on the map are exactly as damaging as in the manuscript,
    # because the map is what the next session steers by.
    # ⛔ ADDED 2026-08-20, IN THE SAME COMMIT THAT GAVE PUB-ASO A SECOND DOCUMENT. The endpoint's
    # `document.file` now names the condensed journal article, so `_publication_documents()` absorbs
    # that file and STOPS absorbing the preprint — the identical shrinking-scope failure recorded
    # above for the degrader SI and for the plan, arriving this time through a one-line change in
    # publications.json rather than through a split. Both documents are listed here by hand so that
    # neither can leave the linted set when the endpoint is repointed again.
    #
    # ⚠ AND THE SHORT PAPER IS THE RISKIER HALF. A compression pass rewrites every hedged sentence,
    # and the failure mode of a shortening pass is dropping the qualifier while keeping the claim —
    # which is precisely an R1-R5 defect. The long paper's language has been through seven red-team
    # rounds; the short paper's has been through none.
    "research/manuscripts/aso/fusion-junction-aso-research-article.md",
    "research/manuscripts/aso/fusion-junction-aso-journal-article.md",
    # ⛔ THE TABLES FILE IS PROSE TOO, ADDED 2026-08-22 (round 14 seat 2). Its captions are spliced
    # into both journal PDFs and carry the two DO NOT ORDER verdicts. Until this line no
    # build-failing instrument read it at all, and a caption stating "four designs at two seams"
    # over a two-row, one-seam table shipped in both built PDFs with every gate green.
    "research/manuscripts/aso/fusion-junction-aso-journal-tables.md",
    # ⛔ THE COVER LETTER IS A SUBMISSION TEXT AND NO LINTER OPENED IT (round 15 seat 3, 2026-08-22).
    # It is the FIRST thing an editor reads and it makes claims of its own — a novelty claim, a fit
    # statement paraphrasing the extended report, integrity declarations. Four of one seat's five P1s
    # landed in this one file, which is what an unguarded surface looks like from the outside.
    # ⚠ It is a submission text, so it belongs to gate 4 and gate 7 exactly as the manuscripts do.
    "research/manuscripts/aso/fusion-junction-aso-cover-letter.md",
    "research/manuscripts/nr4a3-program-map.md",
    # Added 2026-08-05, IN THE SAME COMMIT that moved THE ORDERED PLAN and the spend ladder out of the
    # map and into the systems model. ⚠ WITHOUT THIS LINE THE MOVE WOULD HAVE SILENTLY NARROWED
    # COVERAGE: the warning count fell from 50 to 43 the moment the sections left, because ~1,580 lines
    # of gate language walked out of the linted set and nothing said so. A linter whose scope shrinks
    # while its pass rate improves is the worst possible signal, and it is exactly the "absent reading
    # is not a reading of absence" failure in linter form. The plan is what the next session steers by,
    # so it is linted wherever it lives.
    "systems/views/plan.md",
    # ⭐ ADDED 2026-08-06 WITH THE PUBLICATION REGISTER, and it is the highest-risk generated page in
    # the model for exactly one reason: every row on it is a sentence beginning "what this paper would
    # claim". That is the single grammatical construction most likely to slide from "this work would
    # ESTABLISH X" into "X works" — and unlike the manuscript, these sentences are authored in JSON,
    # where no reviewer reads them in prose form. The generated view is where they become readable, so
    # it is where they are linted.
    "systems/views/L3-publications.md",
    # ⛔ ADDED 2026-08-05 — THE ONE DOCUMENT WRITTEN TO LEAVE THE BUILDING WAS THE ONE DOCUMENT NOTHING
    # LINTED. `nr4a3-degrader-outreach-emails.md` is six ready-to-send emails to named external groups,
    # carrying manuscript-grade claims, and it was in neither this file's targets nor
    # `lint_consistency.py`'s. So it drifted exactly as far as an unlinted file drifts, and the
    # measurement is stark: on 2026-07-10 the paper formally RETRACTED "NR4A3 has no experimental
    # structure" as FALSE (PDB 8XTT, apo NMR, identity 1.000 to Q92570) and removed it from the
    # abstract, §1 and §5. On 2026-08-05 three of the six templates still opened with it -- including
    # the one addressed to a structural-biology group that would recognise 8XTT on sight. Alongside it:
    # a pocket fraction of "~24 %" that belongs to neither the pre-harmonized (0.20/0.16/0.28) nor the
    # current (0.56/0.40/0.80, 44/75 = 59 % pooled) measurement, and a "full control battery" framing
    # for a margin the repo records as failing the metadynamics-frame decoy null (~84th pct) and
    # generated into a frame that scores 0.259 against D* = 0.53.
    #
    # ⭐ THE OUTWARD-FACING DOCUMENT NEEDS THE STRICTEST CHECK, NOT THE LOOSEST. A stale claim in the
    # manuscript is caught by review; a stale claim in an email is caught by the recipient.
    "research/manuscripts/degrader/nr4a3-degrader-outreach-emails.md",
    # ⛔ ADDED 2026-08-06 — THE SAME HOLE AS THE OUTREACH EMAILS, IN THE TWO FILES CLAUDE.md ITSELF
    # SENDS EVERY SESSION TO READ. §5 names `emc-treatment-strategy.md` as required reading before
    # resuming treatment-research work, and §6 names `nr4a3-degrader-next-steps.md` as the single home
    # of the checkpoint/upload rule. Neither was in this file's targets NOR `lint_consistency.py`'s, so
    # both were unlinted on language AND on pinned numbers — the strictly worse version of the outreach
    # gap above, because those two carry CLINICAL claims.
    #
    # ⭐ WHAT WAS ACTUALLY SITTING THERE, found by a verification read rather than by CI:
    # `emc-treatment-strategy.md` still carried "the only 1 of 17 drugs with high sensitivity across two
    # patient-derived EMC models" — a reading of Bangerter 2023 that this repo RETRACTED thirteen hours
    # earlier in `bea2424a4` after fetching the paper (the 40-drug panel ran on USZ20-EMC1 ALONE, and
    # venetoclax showed no monotherapy response at all). The retraction reached IDEAS.md and
    # repurposing-hypotheses.md and stopped there, because nothing linted the third file.
    # Alongside it: B7-H3 and FAP framed as gated only on an IHC, with the repo's own computed
    # selectivity screen recording BH q = 1.0 for CD276. ⛔ CORRECTED 2026-08-06: this comment said
    # "for both", and that was itself the transcription error it was describing -- FAP's measured
    # value is selectivity_q = 0.1555, not 1.0. The wrong number then propagated OUT of this file:
    # the route framing audit's own prompt inherited "q = 1.0 for both" from here and had to be
    # corrected by the subagent that opened the artifact. A linter's documentation is read as fact.
    # And a "full control battery" for denovo_401 that
    # this repo records as failing the metadynamics-frame decoy null.
    #
    # ⚠ A RETRACTION THAT REACHES SOME OF ITS COPIES IS NOT A RETRACTION. Adding these two is what makes
    # the next one land everywhere instead of everywhere-someone-remembered.
    "research/manuscripts/program/emc-treatment-strategy.md",
    "research/modalities/nr4a3-degrader-next-steps.md",
    # ⛔ ADDED 2026-08-06 by the route framing audit. RT-ASO is Tier 1 rank 2 and its
    # `next.best_next_action` is "Publish" — so this is the one manuscript actually queued to leave
    # the building, and it was in neither this file's targets nor the view glob below. That is the
    # outreach-emails lesson exactly: the outward-facing document needs the strictest check, not
    # the loosest.
    "research/manuscripts/aso/fusion-junction-aso-working-record.md",
    # ⛔ ADDED 2026-08-07, in the same commit that created it. `emc-hypoxia-reading.md` names three
    # DRUG CLASSES off a tissue-expression reading, which is the exact shape this linter exists for:
    # a measured observation whose mechanism suggests an intervention, written by an agent who has
    # just spent a session finding the observation and is therefore at maximum risk of writing it
    # one notch too strong. It is also the first EMC TISSUE-BIOLOGY memo here — the reason the ASO
    # paper was added (the outward-facing document needs the strictest check) applies before a
    # document is outward-facing, not after.
    "research/manuscripts/microenv/emc-hypoxia-reading.md",
    # ⛔ ADDED 2026-08-16 — THE DEGRADER-SI HOLE ABOVE, REPRODUCED EXACTLY, IN THE PAPER NEXT TO BE
    # DEPOSITED. `_publication_documents()` resolves PUB-ASO to the research article and to nothing
    # else, so when the 2026-08-16 restructure split six Methods blocks out into
    # `fusion-junction-aso-supplementary-information.md`, that half left the linted set and no
    # count moved to say so — the working record is here by hand for the same reason.
    #
    # ⚠ AND IT IS THE HALF WHERE R4 LIVES. The blocks that moved are the ones that JUSTIFY: the
    # accessibility rationale, the melting-temperature cross-check, the gap-length citation
    # provenance, the graded re-score's bookkeeping and the two unfiltered control screens. A
    # sentence explaining why a method is adequate is the one most likely to slide from "concordant
    # with" into "confirms". Measured on entry: 0 ERROR, 1 WARN (R4 'molecularly confirmed cases',
    # a diagnostic-status idiom, not a claim about this work's results).
    "research/manuscripts/aso/fusion-junction-aso-supplementary-information.md",
]

# ⛔ ADDED 2026-08-06 — THE THIRD TIME THIS EXACT HOLE HAS BEEN FOUND, AND THE LARGEST.
# `systems/views/plan.md` was added when THE ORDERED PLAN moved out of the roadmap, because the move
# silently dropped ~1,580 lines from the linted set. The SAME migration moved the OTHER half — the
# whole route portfolio — into `systems/`, and only the plan was carried across. So L0, the 9 L1
# family pages and all 40 L2 route pages were unlinted: every word of scientific framing for every
# therapeutic route this program holds, including `rationale`, `grade.value` and `closure_note`,
# unenforced against R1-R5.
#
# ⭐ THAT IS THE PORTFOLIO'S OUTWARD FACE. L0-ecosystem.md is what an external reviewer is pointed at
# first, and the L2 pages carry CLINICAL framing for repurposing and immunotherapy routes — the same
# risk class as the two files added earlier today, at 50x the surface area.
#
# ⚠ GLOBBED, NOT LISTED. A hand-typed list of 50 paths would leave the next new route outside the
# linter by default, which is this failure mode reproduced rather than fixed: coverage must follow
# the model, not a list someone remembers to extend. Generated from `systems/graph/*.json` by
# `systems_check.py --write-views`, so linting the views transitively lints the registry prose that
# produced them.
#
# Measured when added: 0 ERROR, 9 WARN across the 50 files, every WARN a benign R4 use (a `TECH-*`
# name containing "A validated prospective ... method"; "a step nobody has validated"). Pure coverage
# gain -- adding it cost no rewriting, which is precisely why it should not have waited.
DEFAULT_TARGETS += sorted(
    os.path.relpath(p, REPO)
    for p in glob.glob(os.path.join(REPO, "systems", "views", "L[012]-*.md"))
)

# ⭐ AND EVERY MANUSCRIPT A PUBLICATION ENDPOINT POINTS AT — same principle as the block above,
# applied to the half of the corpus that was still a hand-list (added 2026-08-06).
#
# ⛔ WHY, MEASURED. Two new manuscripts were written on 2026-08-06 for endpoints `PUB-CLOSED-ROUTES`
# and `PUB-METHODS`. Both were clean -- but only because each was checked by an EXPLICIT single-file
# run. Neither appeared in the 23-entry hand-list, so a bare `lint_claims.py` never opened them, and
# a full-corpus run reporting "0 ERROR across 59 files" was silent about both. **That is the exact
# shape this file's own docstring calls the design brief: a check that does not cover the file still
# reads as enforced.** The comment above already states the principle -- "coverage must follow the
# model, not a list someone remembers to extend" -- and then the manuscripts did not follow it.
#
# `document.file` is the model's own pointer from an endpoint to its manuscript, so a paper cannot
# be drafted without becoming linted in the same commit: `systems_check`'s [B4] requires the target
# exist and declare `level: L3`, which means this glob cannot silently resolve to nothing.
# Deduplicated against the hand-list, which stays because it also covers prose that no endpoint
# claims (the roadmap, the SI, outreach).
def _publication_documents():
    path = os.path.join(REPO, "systems", "graph", "publications.json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []          # the model is systems_check's to police, not this linter's
    rows = data if isinstance(data, list) else data.get("publications", [])
    out = []
    for row in rows:
        f = (row.get("document") or {}).get("file")
        if f and os.path.exists(os.path.join(REPO, f)):
            out.append(f)
    return out


DEFAULT_TARGETS += sorted(set(_publication_documents()) - set(DEFAULT_TARGETS))

# ---------------------------------------------------------------------------
# Disclaimer detection
# ---------------------------------------------------------------------------
# A regulated claim is CLEARED when its sentence scopes the claim out. These markers were
# derived from the real disclaimer sentences already in the manuscript, e.g.:
#   "It makes **no efficacy, potency, or therapeutic claim.**"
#   "This paper's claimed contribution is the target's computational druggability/
#    selectivity, not EMC efficacy."
#   "degrader efficacy ... is context-dependent and not guaranteed by target removal alone"
DISCLAIMER_MARKERS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bnever\b",
    r"\bnor\b",
    # "Nothing in the ternary work reported here is a landmark methodological first" is a
    # disclaimer, but "Nothing"/"Neither" do not match \bno\b or \bnot\b (word boundaries),
    # so the sentence read as an assertion of the very thing it disclaims.
    r"\bnothing\b",
    r"\bneither\b",
    r"\bwithout\b",
    r"\bcannot\b",
    r"\bcan't\b",
    r"\bdoes not\b",
    r"\bis not\b",
    r"\bare not\b",
    r"\bunvalidated\b",
    r"\buntested\b",
    r"\bunproven\b",
    r"\bunverified\b",
    r"\bnot guaranteed\b",
    r"\bassumes?\b",
    r"\brequires?\b",
    r"\bwould require\b",
    r"\bdelegat(?:ed|es)\b",
    r"\bout of scope\b",
    r"\bbeyond (?:the )?scope\b",
    r"\bmakes? no\b",
    r"\bclaim(?:s|ed)? (?:is|are)? ?not\b",
    r"\bonly earned\b",
    r"\bnot yet\b",
    # Explicitly framing a claim as testable is the OPPOSITE of asserting it, e.g. the SI's
    # "it makes the degrader's efficacy claim *quantitative and falsifiable*".
    r"\bfalsifiab\w+\b",
    r"\btestable\b",
    r"\bdo NOT\b",
    r"\bmust not\b",
    r"\bshould not\b",
]
DISCLAIMER_RE = re.compile("|".join(DISCLAIMER_MARKERS), re.IGNORECASE)

# A hedge is weaker than a disclaimer: it right-sizes rather than negates. Sufficient to
# clear the earned-phrase rules (R1) but NOT the never-imply rules (R2), which require an
# actual scope-out.
HEDGE_MARKERS = [
    r"\bpredicted\b",
    r"\bconditional(?:ly)?\b",
    r"\bhypothes(?:is|ized|ised)\b",
    r"\bprovisional\b",
    r"\bin[- ]silico\b",
    r"\bcomputational(?:ly)?\b",
    r"\bsurrogate\b",
    r"\bproxy\b",
    r"\bcandidate\b",
    r"\bprojected\b",
    r"\bestimate[ds]?\b",
    r"\bmodel(?:ed|led)\b",
]
HEDGE_RE = re.compile("|".join(HEDGE_MARKERS), re.IGNORECASE)


class Rule:
    """One language-discipline check.

    severity: "ERROR" (blocks CI) or "WARN" (reported, does not block)
    clears_on: "disclaimer" -> only a scope-out sentence clears it
               "hedge"      -> a disclaimer OR a hedge clears it
               None         -> nothing clears it; wrong in every context
    """

    def __init__(self, rid, pattern, severity, message, source, clears_on="hedge",
                 context_required=None):
        self.rid = rid
        self.re = re.compile(pattern, re.IGNORECASE)
        self.severity = severity
        self.message = message
        self.source = source
        self.clears_on = clears_on
        # An optional second pattern that must ALSO match the sentence. Used to narrow a
        # rule to the specific subject it is actually true about -- e.g. R5's "no dollar
        # figure is measured" holds for the per-EDGE alchemical bases (all projected) but
        # NOT for the endpoint-MD leg, which is a completed 15-leg ledger measurement.
        self.context_re = re.compile(context_required, re.IGNORECASE) if context_required else None


RULES = [
    # -- R1: earned-phrase substitutions -------------------------------------------------
    Rule(
        "R1-selective-hit",
        r"\bselective hits?\b",
        "ERROR",
        'say "predicted selective candidate", not "selective hit"',
        'roadmap "selective hit" -> "predicted selective candidate"',
        clears_on="local_negation",
    ),
    Rule(
        "R1-synthesis-ready",
        r"\bsynthesis[- ]ready\b",
        "ERROR",
        'the phrase "synthesis-ready" is only earned once exact structures/stereochem, '
        "exit-vector chemistry, routes, building-block availability and physicochemical "
        'assessment exist; say "computationally prioritized, structure-defined, '
        'retrosynthetically annotated candidate matrix"',
        'roadmap "synthesis-ready matrix" -> earned phrase',
        clears_on="local_negation",
    ),
    Rule(
        "R1-nr4a3-selective",
        r"\bNR4A3-selective\b",
        "WARN",
        'prefer "predicted NR4A-paralogue-selective" unless the sentence already scopes it',
        'roadmap "NR4A3-selective" -> "predicted NR4A-paralogue-selective"',
        clears_on="hedge",
    ),
    Rule(
        "R1-does-bind",
        r"\b(?:does|do) bind\b|\bbinds? at all\b",
        "WARN",
        'say "is compatible with the hypothesized conditional bound state"',
        'roadmap "does bind at all" -> conditional bound state',
        clears_on="hedge",
    ),
    Rule(
        "R1-recovered-degradation",
        r"\brecovered (?:the )?degradation\b",
        "ERROR",
        'say "produced a surrogate score concordant with the reported outcome"',
        'roadmap "recovered degradation" -> surrogate-score concordance',
        # Was clears_on=None ("wrong in every context"). ⚠ That was true while this linter
        # only read the manuscript. Validation requirement 4 -- the reviewer's own text --
        # ends `Report only directional concordance ... never "recovered degradation."`,
        # i.e. it PROHIBITS the phrase by naming it, and the roadmap merge moved that text
        # into a linted file. `LOCAL_NEGATION_RE`'s own comment already names this exact
        # construct (`never "recovered degradation"`) as the case it was built for, and it
        # is the same tight test the other two earned-phrase rules use: only a negation
        # sitting immediately before the phrase clears it, so "the workflow recovered
        # degradation for NR4A1" still ERRORs (pinned by test_lint_claims.py).
        clears_on="local_negation",
    ),
    # -- R2: never-imply set -------------------------------------------------------------
    # These are regulated words, NOT banned words. Disclaimed use is correct and passes.
    Rule(
        "R2-efficacy",
        r"\befficac(?:y|ious)\b",
        "ERROR",
        "efficacy may only appear in a sentence that scopes the claim OUT",
        "roadmap Never imply ... EMC efficacy",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-therapeutic-window",
        r"\btherapeutic window\b",
        "ERROR",
        "a therapeutic window may only appear scoped out (or when describing prior art)",
        "roadmap Never imply ... a therapeutic window",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-clinical-readiness",
        r"\bclinical(?:ly)? read(?:y|iness)\b|\bready for the clinic\b|\bclinic[- ]ready\b",
        "ERROR",
        "never imply clinical readiness",
        "roadmap Never imply ... clinical readiness",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-safe",
        r"\bis safe\b|\bsafe and effective\b|\bwell[- ]tolerated\b|\bsafety (?:is |was )?(?:established|demonstrated|shown)\b",
        "ERROR",
        "never imply safety",
        "roadmap Never imply ... safety",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-proteome-wide",
        # ⛔ WIDENED 2026-08-06 by the route framing audit. The rule matched one PHRASING of the claim
        # rather than the claim, so three live documents asserted it in other words and passed clean:
        #   "Highest — **absent from normal proteome**"          (fusion-selective-approaches-overview.md:62)
        #   "cannot, in principle, **harm any normal cell**"      (fusion-junction-neoantigen-paper.md:44)
        #   "it spares wild-type NR4A3, EWSR1, and **every normal cell**"                        (:85-86)
        # What the repo actually computes is `fusion_breakpoints.py:231` — novelty against the TWO PARENT
        # PROTEINS (`k not in ews["protein"] and k not in nr4["protein"]`) and nothing else. No
        # proteome-wide search has ever been run here. "Absent from the normal proteome" and "cannot harm
        # any normal cell" are the forbidden claim plus a safety claim, in words the old regex could not
        # see.
        # ⚠ THE LESSON IS ABOUT REGEX RULES GENERALLY: a keyword rule enforces the sentence someone
        # thought of, not the claim. On the same two files the linter simultaneously flagged three HEDGES
        # as errors — including the literal disclaimer "Ready to publish ≠ likely to cure" — so it was
        # strict where it should have cleared and blind where it should have fired.
        r"\bproteome[- ]wide selectiv\w*\b"
        r"|\bselective across the proteome\b"
        r"|\babsent from (?:the )?(?:normal|human) proteome\b",
        "ERROR",
        "never imply proteome-wide selectivity or normal-cell safety — the only novelty test in this "
        "repo compares against the two PARENT proteins (fusion_breakpoints.py:231), never the proteome",
        "roadmap Never imply proteome-wide selectivity",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-treats-cures",
        r"\b(?:cures?|cured|treats|will treat|therapy for EMC\b)",
        "ERROR",
        "no treatment claim -- degradation is experimentally unvalidated",
        "roadmap final deliverable: degradation experimentally unvalidated",
        clears_on="disclaimer",
    ),
    # -- R3: novelty right-sizing --------------------------------------------------------
    Rule(
        "R3-landmark",
        r"\blandmark\b|\bunprecedented\b|\bbreakthrough\b|\bfirst[- ]ever\b|\bparadigm[- ]shift\w*\b",
        "ERROR",
        "novelty is incremental, not landmark -- all-atom ternary-cooperativity FEP is an "
        "active published area (Chen 2023; JCTC 2025; JCIM 2024) and must be cited, not out-claimed",
        "roadmap Novelty is incremental, not landmark",
        # Was clears_on=None ("wrong in every context"), which fired on the manuscript's own
        # right-sizing sentence -- precisely the false-positive class this file's docstring
        # says must pass or the linter gets ignored. Disclaiming landmark status IS the rule
        # being obeyed; an undisclaimed "a landmark first" still carries no marker and errors.
        clears_on="disclaimer",
    ),
    Rule(
        "R3-first-to",
        r"\bthe first (?:to|study|work|report|demonstration)\b|\bwe are the first\b",
        "WARN",
        "a first-in-field claim needs the prior-art citations the roadmap mandates "
        "(Chen 2023; JCTC 2025 5c00064/5c00736; JCIM 2024 4c01227)",
        "roadmap The paper must cite and benchmark against this prior art",
        clears_on="disclaimer",
    ),
    # -- R4: evidentiary-verb discipline --------------------------------------------------
    Rule(
        "R4-proves",
        r"\bprove[sd]?\b|\bproven\b|\bproof that\b",
        "WARN",
        "a computational result does not prove -- say what it is evidence *for*, conditionally",
        "roadmap everything is conditional on the hypothesized pose x receptor frame",
        clears_on="disclaimer",
    ),
    Rule(
        "R4-confirms",
        r"\bconfirm(?:s|ed|ation)\b|\bestablishes?\b(?! a )|\bvalidates?\b|\bvalidated\b",
        "WARN",
        "reserve confirm/establish/validate for results with a committed primary artifact; "
        "otherwise say concordant / consistent with",
        "roadmap language discipline",
        clears_on="disclaimer",
    ),
    # -- R5: measured vs projected --------------------------------------------------------
    Rule(
        "R5-measured-edge-cost",
        # ⚠ `$0` IS EXCLUDED, and that is a narrowing rather than a loosening. This rule is
        # about a PROJECTED per-edge cost being labelled "measured"; a figure of exactly $0
        # is the absence of a cost — it marks free CPU/CI work — so it can never be the
        # mislabelled projection the rule exists to catch. Without the exclusion the roadmap
        # merge turned "(measured 2026-07-28, $0 CPU, `ternary-system-census.yml`)" into an
        # ERROR, which is a true statement flagged. Written so a real sub-dollar figure is
        # still checked: `$0.43 per leg` matches, `$0 CPU` does not.
        r"\bmeasured\b[^.\n]{0,80}\$(?!0(?![\d.]))|\$(?!0(?![\d.]))[^.\n]{0,60}\bmeasured\b",
        "ERROR",
        "no per-EDGE alchemical dollar figure is a completed run on the card quoted -- the "
        "RBFE edge is a rate x hardcoded phase counts, and the ternary edge is a projected "
        "L4 leg converted by a spec-based card ratio (research/compute/pricing.md). "
        "Label PROJECTED, not measured.",
        "pricing.md B: no per-edge base is a completed run on the quoted card",
        clears_on="disclaimer",
        # Scoped to alchemical per-edge costs on purpose. The endpoint-MD leg
        # (~$0.43, NR-V04 covalent panel) IS a genuine completed measurement over a
        # 15-leg S3 ledger, so a blanket "measured + $" rule would fire on a true claim
        # -- and a linter that flags true statements is a linter that gets ignored.
        context_required=r"\bedge\b|\bRBFE\b|\bternary\b|\balchemical\b|\bFEP\b",
    ),
    # -- R6: a claim about what OTHER PEOPLE routinely do ---------------------------------
    Rule(
        "R6-unsurveyed-field-practice",
        # ⛔ WHY THIS RULE EXISTS (trimcrae, 2026-08-15): *"I'm a little skeptical of the
        # claim here that standard practice for ASO design doesn't consider sparing the
        # parent gene. That seems like a pretty obvious thing to do. And we're claiming we
        # invented it?"* We were, in the abstract, and we should not have been. THIS
        # pipeline drops parent-gene records from its alignment screen for a stated reason
        # (`junction_aso_offtarget.is_parent`), and the abstract had generalised that
        # implementation choice into "standard practice does not look" and "specificity
        # screens routinely exclude the parent genes" — a claim about the field, with no
        # survey behind it, contradicted by this paper's OWN citations (refs 13-16
        # demonstrate parental sparing) and by its own working record ("this paper's
        # method-level novelty is nil").
        #
        # ⚠ WHY NO EXISTING RULE CAUGHT IT. R1-R5 police the strength of claims about OUR
        # results — "selective hit", "synthesis-ready", "recovered degradation". Every one
        # of them asks "is this result as strong as the sentence says". None asks "is this
        # sentence about SOMEONE ELSE, and did we measure it". A claim about the field is a
        # claim like any other and needs a source or a hedge.
        #
        # ⚠ KEPT TIGHT, per pinned-figures.json's own warning that a linter flagging true
        # statements gets ignored. It fires only on a generalisation about practice — the
        # subject must be the field or its tools AND the verb must be a habitual. It does
        # NOT fire on "the field has not asked of this disease", which is scoped to an
        # indication and anchored to a stated retrieval two sentences earlier.
        #
        # ⛔⛔ AND THE FIRST VERSION OF THIS RULE COULD NOT FIRE, which is the failure this
        # repository calls the bug rather than the miss. It was written `clears_on="hedge"`,
        # and `DISCLAIMER_MARKERS` contains `\bdoes not\b` — so the very phrase the rule
        # triggers on ("standard practice DOES NOT look") registered as its own disclaimer
        # and cleared it. Proved by running it against the retracted sentence: clean.
        # A negation-shaped assertion is exactly the shape this rule must catch, so the
        # disclaimer test can never be the right clearer for it.
        #
        # ⭐ IT CLEARS ON A CITATION INSTEAD, which is the thing actually missing. The
        # `(?![^.\n]*<sup>)` lookahead asserts there is no citation marker between the
        # generalisation and the end of its sentence. Cite a survey and the rule is silent;
        # assert it bare and it is an ERROR. That is the whole content of the objection.
        r"\b(?:standard|common|conventional|current|usual|established)\s+practice\b"
        r"(?![^.\n]*<sup>)"
        r"[^.\n]{0,60}\b(?:does not|do not|never|fails? to|ignores?|omits?|overlooks?)\b"
        r"|\b(?:screens?|pipelines?|tools?|the field|most groups?|designers?)\b"
        r"(?![^.\n]*<sup>)"
        r"[^.\n]{0,90}\broutinely\b[^.\n]{0,40}"
        r"\b(?:exclude|omit|ignore|skip|overlook)\b",
        "ERROR",
        "this asserts what OTHER GROUPS routinely do, and no survey of published pipelines "
        "was performed. Either cite one, or rewrite it as an argument about the instrument "
        "(what a screen filtering on global identity can and cannot surface) or about this "
        "paper's own screens, which is what is actually established",
        "trimcrae 2026-08-15: \"we're claiming we invented it?\"",
        clears_on=None,
    ),
]


def split_sentences(line):
    """Split a markdown line into sentence-ish spans, returning (start, text) pairs.

    Deliberately crude -- markdown prose, not NLP. Splitting on ., ;, : and newline is
    enough to keep a disclaimer attached to the clause it disclaims, which is the only
    thing the context check needs.
    """
    spans = []
    start = 0
    for m in re.finditer(r"[.;:!?]\s+|$", line):
        end = m.end()
        chunk = line[start:end]
        if chunk.strip():
            spans.append((start, chunk))
        start = end
        if start >= len(line):
            break
    return spans or [(0, line)]


def is_skippable(line, in_fence):
    """Code fences and reference/citation lines are not prose claims."""
    if in_fence:
        return True
    s = line.strip()
    if not s:
        return True
    # Bracketed reference entries and bare DOI/URL lines: quoting a *title* that contains a
    # regulated word (e.g. "[Neosubstrate basis of the del(5q) therapeutic window.]") is not
    # this paper making the claim.
    if re.match(r"^\[?\s*(?:\d+|[A-Z][a-z]+ \d{4})[\].]", s):
        return True
    if s.startswith("[") and s.endswith("]"):
        return True
    if re.match(r"^(?:https?://|doi:|10\.\d{4})", s, re.IGNORECASE):
        return True
    return False


def iter_paragraphs(lines):
    """Yield (joined_text, offset_to_lineno) for each prose paragraph.

    The manuscript is HARD-WRAPPED, so a single sentence routinely spans several physical
    lines. Scanning line-by-line therefore severs a claim from the disclaimer that scopes
    it -- which produced exactly the false positives this linter exists to avoid
    (e.g. paper.md "...no ... / demonstrated efficacy**." wraps mid-sentence). So join
    consecutive prose lines into a paragraph first, and keep an offset->lineno map so
    findings still report the physical line.
    """
    in_fence = False
    buf = []          # list of (text, lineno)
    for lineno, line in enumerate(lines, start=1):
        if re.match(r"^\s*(?:```|~~~)", line):
            in_fence = not in_fence
            if buf:
                yield _join(buf)
                buf = []
            continue
        if is_skippable(line, in_fence):
            if buf:
                yield _join(buf)
                buf = []
            continue
        buf.append((line, lineno))
    if buf:
        yield _join(buf)


def _join(buf):
    parts = []
    offsets = []   # (char_start, lineno)
    pos = 0
    for text, lineno in buf:
        offsets.append((pos, lineno))
        parts.append(text)
        pos += len(text) + 1  # +1 for the joining space
    return " ".join(parts), offsets


def _lineno_for(offsets, pos):
    ln = offsets[0][1]
    for start, lineno in offsets:
        if start <= pos:
            ln = lineno
        else:
            break
    return ln


# A banned *phrase* needs a tighter test than sentence-level negation. Compare:
#   "present it as a research hypothesis, NOT among synthesis-ready claims"  <- disclaims the phrase
#   "a synthesis-ready matrix, not another in-silico lead"                   <- ASSERTS it; the "not"
#                                                                              negates something else
# Both contain "not", so DISCLAIMER_RE clears both and the second escapes. For earned-phrase rules we
# therefore look only at the short span immediately BEFORE the match, where a negation that actually
# scopes the phrase has to sit.
#
# The gap between the negation and the phrase may contain quotes/backticks/emphasis: a prereg's banned-phrase
# list is written `never "recovered degradation"` or `never **validated**`, and a quote character must not
# defeat the scoping (it was doing exactly that on the NR-V04 retrospective prereg, 2026-07-24). Punctuation
# that would END the clause — . ; : ! ? — is still excluded, so "…is not X. Y is recovered degradation" does
# NOT clear.
LOCAL_NEGATION_WINDOW = 40
LOCAL_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|nor|non|isn't|aren't|without|rather than|instead of|as opposed to)\b"
    r"[\s\w,\"'`*_()\[\]-]{0,20}$",
    re.IGNORECASE,
)


def _locally_negated(sent, match_start):
    """True if a negation sits close enough before the match to scope it. Pure."""
    return bool(LOCAL_NEGATION_RE.search(sent[max(0, match_start - LOCAL_NEGATION_WINDOW):match_start]))


# ★★ A DOCUMENT THAT MANDATES A REPLACEMENT MUST BE ABLE TO NAME THE PHRASE IT REPLACES.
# The language-discipline section states every R1 rule as a SUBSTITUTION:
#
#     - "selective hit" → **"predicted selective candidate"**
#     - "recovered degradation" → **"produced a surrogate score concordant with ..."**
#
# so each banned phrase appears as the LEFT-HAND SIDE of an arrow. That is the rule being
# written down, not the claim being made -- and flagging it is exactly the "a linter that
# flags true statements gets ignored" failure this file's docstring is built around.
#
# WHY IT BECAME LIVE (2026-08-02). The rules' source section used to sit in STRATEGY.md,
# which this linter does not read. The roadmap merge moved it into the roadmap, which this
# linter DOES read, and three R1 rules immediately fired on their own definitions. The
# section is not wrong; the clearing rule was missing.
#
# Tight by construction, and this is the whole reason it is safe: the phrase must be
# followed by a substitution arrow INTO A QUOTED REPLACEMENT. An assertion is never written
# `... → **"..."`. It is applied to every rule, including `clears_on=None` ones, because
# naming a phrase as a substitution's LHS is not an assertion of it under any rule.
#
# The leading character class is the REST of the quoted left-hand side: the rules regex a
# token ("synthesis-ready") out of a longer quoted phrase ("synthesis-ready matrix"), so the
# closing quote is up to a few words further on. It admits only word characters, spaces,
# hyphens/dashes and commas — never a `.`, `;`, `:` or a stray quote — so it cannot bridge
# from an asserted phrase to some unrelated arrow later in the sentence.
_SUBSTITUTION_LHS_RE = re.compile(r'^[\w \-–—,]{0,30}["\'`”]?\s*(?:→|->|⇒|=>)\s*\*{0,2}["\'`“]')


def _is_substitution_lhs(sent, match_end):
    """True if the match is the left-hand side of a `"phrase" → "replacement"` rule. Pure."""
    return bool(_SUBSTITUTION_LHS_RE.match(sent[match_end:match_end + 72]))


# ★★ A REGULATED WORD INSIDE A PROPER NOUN IS A NAME, NOT A CLAIM (added 2026-08-06, when
# publication-endpoint coverage first opened `repurposing-hypotheses.md` to this linter).
#
# R2-treats-cures fired twice on **CURE ID**, the FDA/NCATS public registry of real-world
# off-label drug use, in the two sentences that say to CONTRIBUTE cases to it:
#
#   "...contributing real-world off-label experiences to public registries such as
#    **CURE ID** (FDA/NCATS) so that isolated n-of-1 outcomes become collective evidence."   (:333)
#   "...the FDA/NCATS CURE ID registry;"  — an acknowledgements line                          (:420)
#
# Naming a registry is not asserting that anything is cured, so this is the docstring's
# false-positive class exactly, and it is the same principle `is_skippable` already applies to
# a reference TITLE containing a regulated word ("...the del(5q) therapeutic window.").
#
# ⛔ DELIBERATELY THE NARROWEST POSSIBLE FORM, because CLAUDE.md §1's standing rule is "fix the
# doc, don't loosen the pattern" — the other three findings in this batch were fixed in prose,
# and only this one could not be, because the registry's name is not ours to reword.
#   (1) It matches the WHOLE PROPER NOUN ("CURE ID"), never the bare regulated word. A rule
#       match clears only if it lies entirely INSIDE one of these spans.
#   (2) It is CASE-SENSITIVE — the one place in this file that is. The registry is styled
#       CURE ID everywhere it appears in this repo, so "cure id"/"a cure, id..." never clears.
#   (3) It is a fixed list of names, not a pattern over English, so it cannot grow a hole:
#       "cures", "cured", "treats" and every lowercase "cure" are untouched, and a sentence
#       claiming a cure is still an ERROR even when it also mentions CURE ID.
PROPER_NOUNS = [
    r"CURE ID",           # FDA / NCATS registry of real-world off-label use
]
PROPER_NOUN_RE = re.compile("|".join(PROPER_NOUNS))   # NOT re.IGNORECASE — see (2) above


def _inside_proper_noun(sent, match_start, match_end):
    """True if the match falls wholly inside a known proper noun. Pure."""
    return any(
        pm.start() <= match_start and match_end <= pm.end()
        for pm in PROPER_NOUN_RE.finditer(sent)
    )


#: A numbered entry under a References heading is a BIBLIOGRAPHY ENTRY, and its regulated words
#: belong to somebody else's published title. Quoting a title verbatim is not this repository making
#: a claim, and altering a title to satisfy a linter would be a worse error than the one being
#: prevented -- it breaks the citation. Same principle as `PROPER_NOUNS`: a regulated word inside a
#: NAME is a name. Measured when added (2026-08-09): reference 15 of the endpoint manuscript is
#: titled "The Growth Modulation Index (GMI) as an Efficacy Outcome in Cancer Clinical Trials",
#: which fired R2-efficacy on a paper this repository did not write.
#: Scope: every non-heading line under a `References` heading, until the next heading. Entries wrap
#: across lines -- reference 14 above put the word "Efficacy" alone on a continuation line -- so
#: matching only the numbered first line of each entry misses exactly the case that fired.
_REFERENCES_HEADING_RE = re.compile(r"^#{1,6}\s*(?:\d+\s*[.·]?\s*)?references\b", re.I)
_NUMBERED_ENTRY_RE = re.compile(r"^\s{0,3}\d{1,3}\.\s")


def _reference_line_numbers(lines):
    """Line numbers (1-based) belonging to a References section."""
    out, in_refs, seen_entry = set(), False, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            in_refs = bool(_REFERENCES_HEADING_RE.match(line.strip()))
            seen_entry = False
            continue
        if not in_refs:
            continue
        if _NUMBERED_ENTRY_RE.match(line):
            seen_entry = True
        if seen_entry and line.strip():
            out.add(i + 1)
    return out


def lint_file(path):
    findings = []
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    reference_lines = _reference_line_numbers(lines)

    for para, offsets in iter_paragraphs(lines):
        for start, sent in split_sentences(para):
            has_disclaimer = bool(DISCLAIMER_RE.search(sent))
            has_hedge = has_disclaimer or bool(HEDGE_RE.search(sent))
            for rule in RULES:
                # ⛔ EVERY match in the sentence, not just the first (fixed 2026-08-06 while the
                # `PROPER_NOUNS` exception above was being added). This loop used to be
                # `m = rule.re.search(sent)`, so a sentence was judged on its FIRST hit alone and
                # any per-match clearing threw the rest of the sentence away with it. That was
                # survivable while the only per-match clearing was `_is_substitution_lhs` (whose
                # arrow syntax ends the clause), and it stopped being survivable the moment a
                # NAME could clear a match: the adversarial sentence
                #     "We contributed to CURE ID, and our degrader cures EMC."
                # cleared on "CURE" and never looked at "cures" — a real violation masked by a
                # registry name earlier in the same sentence. A per-match exception is only as
                # narrow as the scan it sits in.
                # Reporting is unchanged: the FIRST surviving match becomes the finding, so a
                # sentence still yields at most one finding per rule.
                m = None
                for cand in rule.re.finditer(sent):
                    # Applies to EVERY rule, before `clears_on` is consulted: naming a phrase as
                    # the LHS of a mandated substitution states the rule, it never asserts the
                    # claim. See `_SUBSTITUTION_LHS_RE`.
                    if _is_substitution_lhs(sent, cand.end()):
                        continue
                    # Also before `clears_on`: a regulated word that is part of a proper noun is
                    # a NAME. See `PROPER_NOUNS` -- whole-name, case-sensitive, fixed list.
                    if _inside_proper_noun(sent, cand.start(), cand.end()):
                        continue
                    if rule.clears_on == "local_negation" and _locally_negated(sent, cand.start()):
                        continue
                    m = cand
                    break
                if m is None:
                    continue
                if rule.clears_on == "disclaimer" and has_disclaimer:
                    continue
                if rule.clears_on == "hedge" and has_hedge:
                    continue
                if rule.context_re is not None and not rule.context_re.search(sent):
                    continue
                pos = start + m.start()
                # A bibliography entry quotes somebody else's title verbatim. See
                # `_reference_line_numbers`.
                if _lineno_for(offsets, pos) in reference_lines:
                    continue
                findings.append(
                    {
                        "file": os.path.relpath(path, REPO),
                        "line": _lineno_for(offsets, pos),
                        "rule": rule.rid,
                        "severity": rule.severity,
                        "match": m.group(0),
                        "message": rule.message,
                        "source": rule.source,
                        "context": sent.strip()[:200],
                    }
                )
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="markdown files to lint (default: paper + SI)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument(
        "--warn-as-error", action="store_true", help="exit 1 on WARN as well as ERROR"
    )
    args = ap.parse_args(argv)

    targets = args.files or [os.path.join(REPO, p) for p in DEFAULT_TARGETS]
    findings = []
    for t in targets:
        if not os.path.exists(t):
            print(f"lint_claims: missing target {t}", file=sys.stderr)
            return 2
        findings.extend(lint_file(t))

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warns = [f for f in findings if f["severity"] == "WARN"]

    if args.json:
        print(json.dumps({"findings": findings, "n_error": len(errors), "n_warn": len(warns)}, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']}: {f['severity']} [{f['rule']}] {f['match']!r}")
            print(f"    {f['message']}")
            print(f"    rule source: {f['source']}")
            print(f"    context: {f['context']}")
            print()
        n_files = len(targets)
        if errors or warns:
            print(f"lint_claims: {len(errors)} ERROR, {len(warns)} WARN across {n_files} file(s)")
        else:
            print(f"lint_claims: OK - {n_files} file(s) clean")

    if errors or (args.warn_as_error and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
