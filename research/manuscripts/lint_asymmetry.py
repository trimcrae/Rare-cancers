#!/usr/bin/env python3
"""The paralogue requirement is ASYMMETRIC — this finds the places that restate it as one bar.
($0, stdlib only, offline, no network, no third-party import.)

⛔ WHY THIS EXISTS, AND IT IS A MEASUREMENT THAT WAS TAKEN ONCE BY HAND. On 2026-08-07 commit
`9f560a5ad` swept the corpus for a single defect: a statement of the design REQUIREMENT / BRIEF /
DESIGN TARGET that puts NR4A1-sparing and NR4A2-sparing under ONE bar. 1,354 raw paralogue-pair
mentions were triaged down to 126 requirement-shaped lines and 24 confirmed defects across 18 files;
~1,330 lines were considered and deliberately left. The root cause is recorded in the commit and is
worth restating, because it is what makes the defect RECUR rather than merely exist:

    The §2.4 table row was TITLED "NR4A2 — UNBOUNDED, in both directions" while the cell beside it
    had read "NR4A2 — BOUNDED as of 2026-08-03" since the day it was written. Every downstream
    register copied the LABEL, not the cell. A heading and its body disagreeing means the heading
    wins everywhere it is quoted, because a heading is what gets quoted.

⭐ THE HAND SWEEP IS NOT THE ARTIFACT — THE DETECTOR IS. `RT-ASYMMETRIC`'s one open validation reads
*"the asymmetry carried through every downstream selectivity statement rather than stated once"*, and
its instrument column said `⛔ none built`. A sweep is a reading taken on one day; nothing mechanical
would notice the SEVENTEENTH symmetric restatement. This file is that instrument. Ledger row
`AUT-009`; route record `systems/graph/routes.json` → `RT-ASYMMETRIC`.

★ THE SUBSTANTIVE RULE, WHICH IS A BIOLOGY FACT AND NOT A STYLE PREFERENCE
  (`research/manuscripts/nr4a3-program-map.md` §2.4):

  * **NR4A1-sparing is the HARD half.** A named anti-target genotype — combined `Nr4a1-/-;Nr4a3-/-`,
    postnatal lethality at complete penetrance — is precisely the pair a NON-selective NR4A3 degrader
    reconstitutes. Single nulls do not do it.
  * **NR4A2-sparing is the SOFT half, best-effort.** Bounded for germline DEVELOPMENTAL loss by the
    2026-08-03 MGI reading; UNBOUNDED for the adult, transient, incomplete loss a degrader delivers.
  * The asymmetry runs OPPOSITE to the intuition the corpus had absorbed: all 7 divergent Pocket-5
    residues differ from NR4A1 (5 engageable), only 6 of 7 from NR4A2 (I531 is Ile in NR4A3 *and*
    NR4A2), so the program has MORE discriminating power against the half whose sparing is
    evidenced-mandatory and LESS against the half it cannot bound.

  Writing "NR4A1/2-sparing" therefore makes the brief HARDER than it is where the program is
  strongest and SOFTER than it should be where the program is weakest. It is a wrong specification,
  not an infelicity.

⛔ WHAT THIS BINDS, AND IT IS DELIBERATELY NARROW — read `NOT_BOUND` before concluding it covers a
case. A finding requires FOUR things in ONE sentence-sized statement, and drops on a fifth:

    1. PAIR         both paralogues named as one coordinated unit ("NR4A1/2", "NR4A1 and NR4A2",
                    "NR4A1/NR4A2"). ⛔ The COLLECTIVE form ("the paralogues", "paralogue-selective")
                    is deliberately NOT a pair — see the note on `_PAIR_COLLECTIVE`, which records
                    the 24 -> 65 measurement that refused it.
    2. BAR          a sparing / selectivity / non-engagement / counterexample predicate over it.
    3. REGISTER     the statement is a REQUIREMENT, BRIEF or DESIGN TARGET rather than a report:
                    a deontic ("must", "has to", "should"), a specification noun ("design target",
                    "advancement standard", "requirement", front-matter `purpose:`), a design
                    participle ("designed to be", "engineered to be"), or an ADJECTIVAL compound
                    attached to a design noun ("NR4A1/2-sparing warhead").
    4. NOT ALREADY  the enclosing BLOCK carries no asymmetry marker — "asymmetr", "HARD half" /
       ASYMMETRIC  "SOFT half", "mandatory" beside "best-effort", "not one constraint", or a link to
                   §2.4. The window is the BLOCK, not the sentence, because the corrected form of
                   this defect states the pair in one clause and its two weights in the next.
    5. NOT A        a sentence carrying the repository's `Superseded, retained` marker is exempt:
       QUOTATION    the sweep left every superseded phrasing inline ON PURPOSE, and a guard that
                    went red on the record of its own fix would be uninstalled within a week.

⭐ SYMMETRIC MEASUREMENTS ARE CORRECT AND ARE NOT TOUCHED. "Both paralogues carry a strictly bulkier
side chain at three Pocket-5 positions", "the contrast returns ONE pooled verdict over BOTH
paralogues", "dock every candidate into the aligned NR4A1/NR4A2 pockets" — these report what was
measured over a pair and are RIGHT to be symmetric. That is why rule 3 exists and why it is the rule
that does the work: without it this guard fires on roughly one line in five of the modalities corpus.
The distinction is REGISTER (a bar) versus REPORT (a reading), and it is the same distinction
`lint_claims` draws on strength and `lint_citations` draws on provenance — a third, orthogonal axis:

    lint_claims       how strongly is the claim WORDED
    lint_citations    does the identifier have an ORIGIN
    THIS FILE         is a two-weight REQUIREMENT being restated as a one-weight one

Usage:
  python3 research/manuscripts/lint_asymmetry.py            # check; non-zero exit on any finding
  python3 research/manuscripts/lint_asymmetry.py --report   # every finding, always exits 0
  python3 research/manuscripts/lint_asymmetry.py --root DIR # measure against another tree
  python3 research/manuscripts/lint_asymmetry.py --explain   # print which rule matched, per finding
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# ── SCOPE ────────────────────────────────────────────────────────────────────────────────────────
#: ⛔ THE SCOPE IS THE THREE PLACES THE REQUIREMENT IS STATED, NOT THE WHOLE REPOSITORY. The 2026-08-07
#: sweep found all 24 defects inside these prefixes; everything it deliberately left outside them is
#: either a record of a past state (`research/autonomy/**` — the ledger, receipts and review seats
#: quote defects verbatim on purpose) or a fetch product (`research/literature/**`).
SCAN_PREFIXES = (
    "research/manuscripts",
    "research/modalities",
    "systems/graph",
)

#: ⚠ `systems/views/**` IS DELIBERATELY OUT OF SCOPE AND THAT IS NOT A HOLE. Every view is GENERATED
#: from `systems/graph/*.json` (CLAUDE.md §7; a hand-edit fails the build), so a symmetric statement
#: there is a symmetric statement in the graph, which IS scanned. Scanning both would double every
#: finding and point the remedy at a file nobody may edit. The 2026-08-07 sweep touched four view
#: files for exactly this reason: they were regenerated, not fixed.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".pytest_cache", "archive", "tests", "views",
}

SKIP_BASENAMES = {
    # Records of past states. Each quotes the defect verbatim as evidence; that is their job.
    "research-ledger.json",
    "CLAUDE-history.md",
    #: ⛔ AND THIS FILE. A guard whose own docstring must quote the defect verbatim in order to
    #: explain it will otherwise flag itself — measured: 4 findings, all inside comments written to
    #: describe the rules. `lint_citations` has the same carve-out for the same reason.
    "lint_asymmetry.py",
}

EXTENSIONS = (".md", ".py", ".json")

# ── RULE 1 · THE PAIR ────────────────────────────────────────────────────────────────────────────
#: The two paralogues named as ONE coordinated unit. ⛔ `NR4A1/NR4A3` and `NR4A1+NR4A3` must NOT
#: match: that pair is the anti-target GENOTYPE, whose whole point is that it names one half.
#: ⛔ AND `NR4A1/2/3` MUST NOT MATCH EITHER — MEASURED, NOT ANTICIPATED. The triple is the CAR-T
#: pan-NR4A mode, which is the OPPOSITE requirement ("this needs a pan-NR4A degrader — the opposite of
#: the EMC requirement"). Without the trailing negative lookahead it produced 2 of the pre-sweep
#: tree's false positives, both in `nr4a3-degrader-broader-indications.md`'s immuno-oncology bullet.
_PAIR_EXPLICIT = re.compile(
    r"(?:"
    r"NR4A1\s*(?:/|,\s*|\s*\+\s*|\s*&\s*|\s+(?:and|or|plus)\s+)\s*(?:NR4A)?2"
    r"|NR4A2\s*(?:/|,\s*|\s*\+\s*|\s*&\s*|\s+(?:and|or|plus)\s+)\s*NR4A1"
    r"|Nr4a1\s*/\s*(?:Nr4a)?2"
    r")\b(?!\s*(?:/|,|\s+and\s+|\s*\+\s*)\s*(?:NR4A)?3\b)",
    re.IGNORECASE,
)

#: ⛔ THE COLLECTIVE FORM — "the paralogues", "paralogue-selective" — IS NOT A PAIR HERE, AND THAT WAS
#: A MEASUREMENT RATHER THAN A JUDGEMENT. Admitting it as rule 1 took the pre-sweep tree from 24 to
#: 65 findings, and every one of the 41 extra was an honest sentence about the requirement IN GENERAL
#: ("Nobody has stated how much paralogue selectivity this family would need"; "the paralogue
#: selectivity requirement has never been sized"). Those sentences never state a symmetric BAR — they
#: state that a bar is missing, which is the opposite defect. Dropping it costs no known finding:
#: every one of the 2026-08-07 sweep's symmetric sites names both paralogues explicitly, because that
#: is what made them copyable. Recorded in NOT_BOUND.
_PAIR_COLLECTIVE = None

# ── RULE 2 · THE BAR PREDICATE ───────────────────────────────────────────────────────────────────
_BAR = re.compile(
    r"\bspar(?:e|es|ed|ing)\b"
    r"|-sparing\b"
    r"|\bselectiv(?:e|ity)\s+(?:over|against|versus|vs\.?|to)\b"
    r"|\bselectively\s+over\b"
    r"|\bparalogue[- ]selectiv"
    r"|\bcounterexamples?\b"
    r"|\bNOT\s+(?:bind|hit|degrade|engage|cross-degrade)"
    #: ⚠ THE GAPPED NEGATION, AND IT WAS FOUND BY A TEST RATHER THAN BY READING. `nr4a_selectivity.py`
    #: — one of the two module docstrings among the 16 — reads "A warhead must bind NR4A3 but NOT the
    #: homologous NR4A1/NR4A2 LBDs", where the verb sits before the negation rather than after it.
    #: The guard scored that site GREEN on its own merits and only reported it because an ADJACENT
    #: clause in the same paragraph happened to say "does not cross-degrade". A finding that depends
    #: on a neighbouring sentence is a finding that disappears when someone rewraps the paragraph.
    r"|\bbut\s+NOT\b"
    r"|\bavoid(?:s|ing)?\s+(?:their|its|the)\b",
    re.IGNORECASE,
)

_DESIGN_NOUN = (
    r"warhead|binder|degrader|design|designs|agent|molecule|profile|ligand|drug|candidate"
    r"|specification|spec|brief|programme|program"
)

# ── RULE 3 · THE REQUIREMENT REGISTER ────────────────────────────────────────────────────────────
#: ⭐ THIS IS THE RULE THAT DOES THE WORK. Rules 1 and 2 together match ~1 line in 5 of the paralogue
#: corpus, almost all of them correct measurements. A finding needs the statement to be a BAR the
#: molecule must clear, not a READING taken over the pair.
_REGISTER = re.compile(
    r"\bmust\b|\bMUST\b"
    r"|\bha(?:s|ve)\s+to\b"
    r"|\bshould\b"
    r"|\bneeds?\s+to\b"
    r"|\bnon-negotiable\b"
    r"|\bmandator(?:y|ily)\b"
    r"|\brequire(?:s|d|ment|ments)?\b"
    r"|\bdesign\s+(?:target|goal|brief|constraint|spec(?:ification)?)\b"
    r"|\btarget\s*:\s"
    r"|\badvancement\s+standard\b"
    r"|\bcriteri(?:on|a)\b(?!-)"   # ⚠ NOT "criterion-matched", which describes a MEASUREMENT
    r"|\bspecifi(?:ed|cation)\b"
    r"|\b(?:designed|engineered|specified|intended|built)\s+to\b"
    r"|^\s*purpose\s*:"
    r"|\"purpose\"\s*:"
    r"|\bsafe\s+only\s+if\b"
    r"|\bwant(?:s|ed)?\b(?=.{0,80}\bspared\b)"
    r"|\bthe\s+relevant\s+question\s+is\b"
    #: ⭐ THE AGENT-PROPERTY FORM, WHICH CARRIES NO DEONTIC WORD AT ALL: "so the agent can be both
    #: fusion-selective and paralogue-selective". It is a design property predicated of the molecule,
    #: which is a specification however the sentence is otherwise phrased. Narrowly written — the
    #: subject must be one of the design nouns and the verb must be a copula — because a bare `\bcan\b`
    #: matches most of the modalities corpus.
    #: ⚠ `be BOTH` IS LOAD-BEARING AND WAS NARROWED BY MEASUREMENT. Without it, "A drug can be
    #: selective at three increasingly tight levels" — a taxonomy sentence in
    #: `fusion-selective-approaches-overview.md` — became a false positive. The conjunction is what
    #: makes the sentence a specification: it asserts TWO design properties of one molecule at once,
    #: which is the same collapse this guard exists for.
    r"|\b(?:the\s+|this\s+|an?\s+)?(?:" + _DESIGN_NOUN + r")\s+"
    r"(?:can|could|will|would|is|are|must|should)\s+be\s+both\b",
    re.IGNORECASE | re.MULTILINE,
)

#: The ADJECTIVAL form, which carries no deontic word at all and is how the defect reached a section
#: HEADING and an outreach email: "an NR4A3-selective (NR4A1/2-sparing) warhead". A sparing compound
#: attached to a design noun IS a specification, however the sentence is otherwise phrased.
#: ⚠ `[^.]` AND NOT `[^.\n]`: the compound and its design noun are routinely split by the 100-column
#: wrap. `"a predicted NR4A3-selective (NR4A1/2-sparing)\nbinder"` — the outreach email, one of the 16
#: — is invisible to a newline-excluding window, and was measured as a miss before this was widened.
_ADJECTIVAL = re.compile(
    r"(?:NR4A1\s*/\s*(?:NR4A)?2|NR4A1\s*/\s*NR4A2)[-‑–]?\s*sparing[^.]{0,60}?\b(?:"
    + _DESIGN_NOUN + r")\b"
    r"|sparing\s+NR4A1\s*/\s*(?:NR4A)?2[^.]{0,60}?\b(?:" + _DESIGN_NOUN + r")\b"
    r"|\b(?:" + _DESIGN_NOUN + r")\b[^.]{0,60}?(?:NR4A1\s*/\s*(?:NR4A)?2)[-‑–]?\s*sparing",
    re.IGNORECASE,
)

#: ⭐ THE CRITERIA-LIST LEAD-IN, AND IT IS WHY THE REGISTER IS NOT A PURE PER-SENTENCE TEST. A numbered
#: advancement list carries its register in the sentence ABOVE it: the redesign brief reads *"It is a
#: candidate for which:"* and then six numbered bars, of which item 4 — *"matched NR4A1 and NR4A2
#: conformers do not provide strong counterexamples"* — is one of the 16 sites the sweep rewrote and
#: contains no register word of its own. ⛔ The alternative tried first was admitting `counterexample`
#: to `_REGISTER` outright; that collapses rules 2 and 3 into one word and returned three false
#: positives inside a RETIRED scoring formula (`− γ·max(NR4A1/2 counterexample)`), which is a penalty
#: term rather than a statement. The lead-in is narrower and reads the document the way a person does.
_LIST_ITEM = re.compile(r"^\s*(?:\d+[.)]|[-*+•])\s+")
_CRITERIA_LEAD_IN = re.compile(
    r"(?:candidate|molecule|design|compound|series)\s+for\s+which\s*:"
    r"|\b(?:criteri(?:on|a)|advancement\s+standard|requirements?|specification|design\s+target"
    r"|must\s+(?:satisfy|meet|clear)|desired\s+outcome)\b[^\n]*:\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# ── RULE 4 · THE ASYMMETRY IS ALREADY CARRIED (block-scoped exemption) ───────────────────────────
#: ⚠ THE WINDOW IS THE BLOCK, NOT THE SENTENCE, AND THAT IS DELIBERATE. The CORRECTED form of this
#: defect names the pair in one clause and its two different weights in the next — see the fixed
#: `emc-treatment-roadmap.md` paragraph, where "could hit the paralogues NR4A1/NR4A2" is immediately
#: followed by "but those two are not one constraint". A sentence-scoped exemption would go red on
#: every correctly-fixed site, which is the failure mode that gets a guard switched off.
_ASYMMETRY_MARKERS = re.compile(
    r"asymmetr"
    r"|\bhard\s+half\b|\bsoft\s+half\b"
    r"|\bHARD,\s*(?:evidenced-)?mandatory\b"
    r"|\bbest[- ]effort\b"
    r"|\bnot\s+(?:the\s+same|one)\s+(?:requirement|constraint|bar)\b"
    r"|\bnot\s+one\s+constraint\b"
    r"|\btwo\s+requirements\s+with\s+different\s+weights\b"
    r"|\b(?:carry|have|take)\s+different\s+(?:weights|kinds|bounds)\b"
    #: ⛔ "different optimal LEVERS" IS NOT ON THIS LIST AND MUST NOT BE. It was added for one line and
    #: immediately hid a real finding: the pre-sweep selectivity architecture read *"Treating 'spare
    #: NR4A1 and NR4A2' as one requirement hides that the two have different optimal levers"* — which
    #: names a difference in MECHANISM while still stating one bar, and is exactly the site the sweep
    #: rewrote. Different levers is not different WEIGHTS. Measured: recall fell from 19/19 to 18/19.
    r"|\bharder\s+of\s+the\s+two\b"
    r"|\bhard\s*(?:,|/|\s+and\s+)\s*soft\b"
    r"|24--the-selectivity-requirement-is-asymmetric"
    r"|\bmandatory\b(?=[\s\S]{0,400}\bbest[- ]effort\b)"
    r"|\bbest[- ]effort\b(?=[\s\S]{0,400}\bmandatory\b)",
    re.IGNORECASE,
)

# ── RULE 5 · THE SUPERSEDED-QUOTATION EXEMPTION ──────────────────────────────────────────────────
#: ⛔ NON-NEGOTIABLE. CLAUDE.md rule 1.2 requires a correction to REGISTER the text it replaced, and
#: the 2026-08-07 sweep left all 16 superseded phrasings inline as the evidence of its own work. A
#: guard that fires on those makes the honest correction pattern the expensive one.
_SUPERSEDED = re.compile(r"superseded,\s*retained", re.IGNORECASE)

# ── WHAT THIS DOES NOT BIND ──────────────────────────────────────────────────────────────────────
#: ⛔ READ THIS BEFORE CONCLUDING THE GUARD COVERS A CASE. Each row is a real class the 2026-08-07
#: sweep also corrected, or a real evasion, that this detector does NOT catch. An honest listed hole
#: costs nothing; a hole nobody wrote down costs the route.
NOT_BOUND = [
    ("the stale-bound class",
     "'NR4A2-sparing is unbounded in both directions' was ALSO fixed by the same sweep (R7 and its "
     "graph record, program-map §2.4's row label, target-route-options). That is a SUPERSEDED FACT, "
     "not a symmetric statement: the sentence already carries the asymmetry and is still wrong. "
     "Detecting it needs a pinned-figure check, which is `lint_consistency`'s axis, not this one."),
    ("the exposure-lever class",
     "'source NR4A2 safety from PK/CNS-exclusion' was fixed by the same sweep in the selectivity "
     "architecture, the SI safety note and the carT framing. It is symmetric in neither direction — "
     "it is a claim about a molecule that does not exist. Same remedy, different detector."),
    ("a pair split across two sentences",
     "'The degrader must spare NR4A1. It must also spare NR4A2.' states one bar in two sentences and "
     "no sentence-scoped rule sees a pair. Widening the match unit to the block trades this for "
     "false positives on every block that discusses both halves correctly, which is most of them."),
    ("a superseded quotation spanning a sentence boundary",
     "Rule 5 exempts the SENTENCE carrying the marker. A retained quotation whose symmetric phrasing "
     "falls into the following sentence would be flagged. Measured on the 2026-09-01 tree: zero such "
     "cases. If one appears, the fix is to extend the exemption to the emphasis run, not to drop it."),
    ("a symmetric sentence ADDED to a block that already carries the asymmetry",
     "Rule 4 is BLOCK-scoped, so a corrected paragraph is exempt as a whole. Measured directly: "
     "restoring the pre-sweep clause 'so the design target is NR4A3-selective, NR4A1/2-sparing' into "
     "the CORRECTED roadmap paragraph left the guard green, because 'HARD half', 'SOFT half' and the "
     "§2.4 link were still in the same block. Narrowing rule 4 to the sentence is not the fix -- it "
     "makes every correctly-fixed site red, which is how a guard gets switched off. This hole is the "
     "price of that, and it is the one to reopen first if the defect recurs."),
    ("prose outside SCAN_PREFIXES",
     "`research/autonomy/**` (ledger, receipts, review seats), `research/literature/**` and "
     "`systems/views/**` are out of scope by construction — see SCAN_PREFIXES and SKIP_DIRS."),
    ("a paraphrase with no NR4A token and no 'paralogue'",
     "'selective against the other two family members' names the pair without naming it. Adding "
     "family-member paraphrases to rule 1 was tried and returns measurement prose almost exclusively."),
]

# ── THE BASELINE ─────────────────────────────────────────────────────────────────────────────────
#: ⛔ THREE ROWS, EACH WITH A VERDICT, AND THE KEY IS THE SENTENCE'S OWN DIGEST — EDIT THE SENTENCE
#: AND THE AMNESTY IS GONE. This is not a "known failures" list that grows: a `not-a-defect` row is a
#: rule this guard cannot express and says so; an `open-defect` row is a REAL finding that is still
#: in the prose, printed loudly on every run so it cannot be forgotten, and `--strict` fails on it.
#: The gate is green on these so it can be WIRED — a guard nobody runs catches nothing (CLAUDE.md's
#: `subagent_width` finding) — but a NEW symmetric restatement is red on its first commit, which is
#: the whole point.
#: ⚠ Keys are sha1(whitespace-collapsed sentence)[:16] and deliberately NOT path-keyed: these files
#: move between directories (all three of the 2026-08-07 sweep's manuscript paths did), and a moved
#: file must not silently re-fire.
BASELINE = {
    "2520065eff760e40": {
        "verdict": "open-defect",
        "where": "research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:35",
        "note": "A SECTION HEADING stating one bar: '## Framing: the indication must want NR4A3 "
                "*down* AND NR4A1/2 *spared*'. The 2026-08-07 sweep rewrote three statements in this "
                "same file (lines 23, 31, 91 of the pre-sweep text) and left this heading, which is "
                "precisely the failure its own commit message names -- a heading is what gets quoted. "
                "Found 2026-09-01 by this detector, by seat S14-DETECTOR of the 2026-09-01 sprint. "
                "The prose fix is owed and is not this file's to make.",
        "first_seen": "2026-09-01",
    },
    "63106dd065a89a7f": {
        "verdict": "open-defect",
        "where": "research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:44",
        "note": "'These all want NR4A3 removed and NR4A1/2 spared -- the *same* molecule we design "
                "for EMC.' Same file, same defect, also missed by the hand sweep. Found 2026-09-01.",
        "first_seen": "2026-09-01",
    },
    "b86f5bbe5d8347d4": {
        "verdict": "not-a-defect",
        "where": "research/modalities/nr4a3-abfe-repair-prereg.md:93",
        "note": "A REPORTING RULE that REFUSES the symmetric claim: 'An unqualified \"selective vs "
                "NR4A1 AND NR4A2\" statement requires NR4A1 independent replicates...'. Its own "
                "section already separates the halves ('NR4A2 is the primary gate (harder "
                "paralogue), but NR4A1 cannot be ignored'). It is the opposite of this defect and "
                "the guard cannot see that without a rule tuned to one sentence. "
                "⚠ SEPARATELY WORTH SOMEONE'S ATTENTION AND NOT A LINTER MATTER: that section calls "
                "NR4A2 the *harder* paralogue, while program-map §2.4 makes NR4A1-sparing the HARD, "
                "evidenced-mandatory half. Two live documents disagree about which half is which.",
        "first_seen": "2026-09-01",
    },
}


def baseline_key(sentence: str) -> str:
    return hashlib.sha1(re.sub(r"\s+", " ", sentence).strip().encode("utf-8")).hexdigest()[:16]


_ABBREV = re.compile(
    r"(?:\b(?:et al|e\.g|i\.e|cf|approx|vs|Fig|Ref|No|Dr|Nat Med|Mol|Sci|ca)\.)$", re.IGNORECASE
)
#: ⚠ `\\s+` AND NOT `[ \\t]+`: prose here is hard-wrapped at ~100 columns, so most sentence breaks
#: fall on a newline. With the tab-only form a "sentence" was the whole paragraph and the reported
#: line number pointed at the block rather than the statement.
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[^\s])")
_LIST_MARKER_TAIL = re.compile(r"(?:^|\s)\(?\d{1,2}[.)]$")

#: ⛔ A STRUCTURAL BOUNDARY IS A STATEMENT BOUNDARY, AND SENTENCE PUNCTUATION DOES NOT SEE IT. A bullet
#: ending `... risk of §C.**` is followed by a newline and a new bullet; the terminator is hidden
#: behind the closing `**`, so a purely punctuation-based split ran two list items together and
#: reported the pair from the SECOND inside the register of the FIRST. Measured: one false positive in
#: `nr4a3-degrader-broader-indications.md`, and a wrong line number on several true ones.
_UNIT_BOUNDARY = re.compile(
    r"^(?:\s*(?:[-*+•]|\d+[.)])\s|#{1,6}\s|>\s|\||\s*→\s"
    r"|[a-z_][a-z0-9_-]*:\s)",            # a YAML front-matter key is a statement of its own
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[tuple[int, str]]:
    """(offset, sentence) pairs. ⚠ Never splits on ':' — 'Design target: NR4A3-selective,
    NR4A1/2-sparing' must stay one unit or rule 3 and rule 1 land in different sentences."""
    out: list[tuple[int, str]] = []
    pos = 0
    buf = ""
    start = 0
    for piece in _SENT_SPLIT.split(text):
        if not buf:
            start = pos
        buf = (buf + " " + piece).strip() if buf else piece
        pos = text.find(piece, pos) + len(piece)
        # a trailing abbreviation means the split was spurious; keep accumulating
        if _ABBREV.search(buf.rstrip()):
            continue
        #: ⛔ A LIST MARKER IS NOT A SENTENCE END, AND THIS COST A REAL FINDING. "4. matched NR4A1 and
        #: NR4A2 conformers do not provide strong counterexamples" split after the "4.", so the unit
        #: the criteria-list rule inspected began with "matched" and no longer looked like a list
        #: item. `\d{1,2}\.` after whitespace is a marker; a four-digit year is not (the digits before
        #: the last two are not whitespace), and neither is a decimal.
        if _LIST_MARKER_TAIL.search(buf.rstrip()):
            continue
        out.append((start, buf))
        buf = ""
    if buf:
        out.append((start, buf))
    return out


_HEADING = re.compile(r"^#{1,6}\s")


def md_blocks(text: str) -> list[tuple[int, str, bool]]:
    """Blank-line-delimited blocks as (first_line_number, block_text, is_heading). Fenced code blocks
    are kept: the defect reached a section heading quoted inside backticks in
    `paper-framing-options.md`.

    ⭐⭐ A HEADING IS ALWAYS ITS OWN BLOCK, AND THAT IS THE MOST IMPORTANT LINE IN THIS FILE. The
    2026-08-07 commit's own root-cause finding is that a heading and its body disagreeing means the
    HEADING wins everywhere, *because a heading is what gets quoted* — the §2.4 table row was titled
    "NR4A2 — UNBOUNDED, in both directions" while the cell beside it said BOUNDED, and every
    downstream register copied the title. So a heading gets no exemption from the paragraph under it
    (see `judge_document`), and it is judged on what it says by itself. Measured: gluing headings to
    their bodies hid a live symmetric heading in
    `degrader/nr4a3-degrader-broader-indications.md` that the hand sweep had also missed."""
    blocks: list[tuple[int, str, bool]] = []
    cur: list[str] = []
    first = 1
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip() == "":
            if cur:
                blocks.append((first, "\n".join(cur), False))
                cur = []
        elif _HEADING.match(line):
            if cur:
                blocks.append((first, "\n".join(cur), False))
                cur = []
            blocks.append((i, line, True))
        else:
            if not cur:
                first = i
            cur.append(line)
    if cur:
        blocks.append((first, "\n".join(cur), False))
    return blocks


def py_blocks(text: str) -> list[tuple[int, str]]:
    """Only docstrings and `#` comment runs. ⛔ Code is excluded on purpose: a dict key 'NR4A1/NR4A2'
    is an identifier, not a statement about the requirement, and the two module docstrings the sweep
    fixed (`nr4a3_warhead.py`, `nr4a_selectivity.py`) are both prose."""
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    in_doc = False
    quote = ""
    cur: list[str] = []
    first = 1
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if in_doc:
            cur.append(line)
            if quote in line:
                out.append((first, "\n".join(cur)))
                cur, in_doc = [], False
            continue
        m = re.match(r'^[ \t]*[rbuf]{0,2}("""|\'\'\')', line)
        if m:
            quote = m.group(1)
            rest = line.split(quote, 1)[1]
            if quote in rest:
                out.append((i, line))
            else:
                in_doc, first, cur = True, i, [line]
            continue
        if s.startswith("#"):
            if not cur:
                first = i
            cur.append(s.lstrip("#").strip())
            if i == len(lines):
                out.append((first, "\n".join(cur)))
        else:
            if cur:
                out.append((first, "\n".join(cur)))
                cur = []
    if cur:
        out.append((first, "\n".join(cur)))
    # blank-line-separated docstring paragraphs become their own blocks, so rule 4's window is a
    # paragraph here too rather than a 40-line module header.
    split: list[tuple[int, str]] = []
    for ln, blk in out:
        off = 0
        for para in re.split(r"\n[ \t]*\n", blk):
            split.append((ln + blk[:off].count("\n"), para))
            off += len(para) + 2
    return split


#: ⛔ JSON IS SCANNED FROM THE PAIR OUTWARD, NOT FROM THE TOP DOWN, AND BOTH OBVIOUS ROUTES WERE
#: MEASURED AND REJECTED. (1) `json.loads` on every modalities artifact builds an object graph for
#: `emc-ret-cistrome-inputs.json`, which is **96 MB**: 3.0 s of a 5.1 s run, in one file. (2) A
#: value-shaped regex `"(?:[^"\\]|\\.){40,}"` walks that file character by character through an
#: alternation and made it **worse** — 11.8 s. What is actually rare is the PAIR: a handful of hits
#: per file at most. So find those with one C-level scan and expand each to its enclosing JSON string.
_PROSE_KEYS = ("purpose", "statement", "title", "best_next_action", "what", "why")
_JSON_KEY_BEFORE = re.compile(r'"(?P<key>[A-Za-z_][A-Za-z0-9_]*)"\s*:\s*$')
_MAX_VALUE = 20000


def _string_bounds(text: str, i: int) -> tuple[int, int] | None:
    """The unescaped quotes enclosing offset `i`, or None if it is not inside a JSON string."""
    a = i
    while a > 0:
        a = text.rfind('"', 0, a)
        if a < 0 or i - a > _MAX_VALUE:
            return None
        bs = 0
        while a - bs - 1 >= 0 and text[a - bs - 1] == "\\":
            bs += 1
        if bs % 2 == 0:
            break
    if a < 0:
        return None
    b = i
    while True:
        b = text.find('"', b + 1)
        if b < 0 or b - i > _MAX_VALUE:
            return None
        bs = 0
        while text[b - bs - 1] == "\\":
            bs += 1
        if bs % 2 == 0:
            return a, b
    return None


def json_blocks(text: str) -> list[tuple[int, str]]:
    """Every JSON string value of 40+ characters that names the pair, with the line it sits on."""
    out: list[tuple[int, str]] = []
    seen: set[int] = set()
    for m in _PAIR_EXPLICIT.finditer(text):
        span = _string_bounds(text, m.start())
        if span is None or span[0] in seen:
            continue
        seen.add(span[0])
        a, b = span
        raw = text[a + 1:b]
        if len(raw) < 40:
            continue
        try:
            val = json.loads('"' + raw + '"')
        except ValueError:
            continue
        km = _JSON_KEY_BEFORE.search(text[max(0, a - 80):a])
        if km and km.group("key").lower() in _PROSE_KEYS:
            val = f"{km.group('key').lower()}: {val}"
        out.append((text.count("\n", 0, a) + 1, val))
    return out


class Finding:
    __slots__ = ("path", "line", "sentence", "rule")

    def __init__(self, path: str, line: int, sentence: str, rule: str):
        self.path, self.line, self.sentence, self.rule = path, line, sentence, rule

    @property
    def baseline(self) -> dict | None:
        return BASELINE.get(baseline_key(self.sentence))

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"{self.path}:{self.line} [{self.rule}]"


def block_units(block: str) -> list[tuple[int, str]]:
    """(line offset within the block, unit text). A unit is a run of wrapped lines belonging to one
    list item, heading, table row or paragraph — see `_UNIT_BOUNDARY`."""
    units: list[tuple[int, str]] = []
    cur: list[str] = []
    first = 0
    for i, ln in enumerate(block.splitlines()):
        if cur and _UNIT_BOUNDARY.match(ln):
            units.append((first, "\n".join(cur)))
            cur, first = [], i
        if not cur:
            first = i
        cur.append(ln)
    if cur:
        units.append((first, "\n".join(cur)))
    return units


def judge_block(path: str, line: int, block: str, lead_in: str = "",
                asym_window: str = "") -> list[Finding]:
    """The five rules, in the order that makes a rejection cheapest.

    ⚠ RULE 4 IS EVALUATED ON THE WHOLE BLOCK AND THE OTHER FOUR ON A UNIT INSIDE IT. That asymmetry
    is the point: a correctly-fixed site names the pair in one clause and its two weights in the
    next, so the exemption must see the whole paragraph, while a finding must be reportable at the
    statement that carries it.

    `lead_in` is the preceding block when this block is a criteria LIST — see `_CRITERIA_LEAD_IN`."""
    in_criteria_list = bool(lead_in) and bool(_CRITERIA_LEAD_IN.search(lead_in))
    if not _PAIR_EXPLICIT.search(block):
        return []
    if _ASYMMETRY_MARKERS.search(asym_window or block):   # rule 4 — window-scoped, checked once
        return []
    sents: list[tuple[int, str]] = []
    for unit_line, unit in block_units(block):
        for off, sent in split_sentences(unit):
            sents.append((unit_line + unit[:off].count("\n"), sent))
    out: list[Finding] = []
    for off, sent in sents:
        if _SUPERSEDED.search(sent):              # rule 5
            continue
        if not _PAIR_EXPLICIT.search(sent):
            continue
        if not _BAR.search(sent):                 # rule 2
            continue
        if _ADJECTIVAL.search(sent):
            rule = "adjectival-design-compound"
        elif _REGISTER.search(sent):
            rule = "requirement-register"
        elif in_criteria_list and _LIST_ITEM.search(sent):
            rule = "criteria-list-item"
        else:
            continue                              # rule 3 — a symmetric MEASUREMENT, left alone
        out.append(Finding(path, line + off, sent.strip(), rule))
    return out


def scan_text(path: str, text: str) -> list[Finding]:
    #: ⭐ WHOLE-FILE PRE-FILTER, AND IT IS WHAT MAKES THIS CHEAP ENOUGH FOR A GATE. No explicit pair
    #: anywhere in the bytes means no finding is reachable, so the file never gets parsed, split or
    #: sentence-segmented. `re.search` over 16 MB is C-level and costs milliseconds; `json.loads` of
    #: the same file costs seconds. Measured: 26.4 s -> 1.6 s over the same corpus.
    #: ⛔ AND THE LITERAL CHECK COMES BEFORE THE REGEX, WHICH IS THE DIFFERENCE BETWEEN 6.1 s AND
    #: 2.6 s. `_PAIR_EXPLICIT` opens on a group of alternations, so it has no literal prefix for the
    #: engine to memchr on and it walks every byte: `emc-ret-cistrome-inputs.json` is 96 MB and cost
    #: **3.4 s by itself**, more than half the whole run. `"NR4A1" in text` is a C substring search
    #: and settles the same question, because every branch of `_PAIR_EXPLICIT` requires one of these
    #: three tokens. Profiled per file, not guessed.
    if not ("NR4A1" in text or "NR4A2" in text or "Nr4a1" in text):
        return []
    if not _PAIR_EXPLICIT.search(text):
        return []
    if path.endswith(".py"):
        blocks = [(ln, b, False) for ln, b in py_blocks(text)]
    elif path.endswith(".json"):
        blocks = [(ln, b, False) for ln, b in json_blocks(text)]
    else:
        blocks = md_blocks(text)
    out: list[Finding] = []
    prev_block = ""
    heading = ""
    for entry in blocks:
        line, block, is_heading = entry if len(entry) == 3 else (entry[0], entry[1], False)
        if is_heading:
            heading = block
            out.extend(judge_block(path, line, block, "", block))
            continue
        lead_in = prev_block if _LIST_ITEM.search(block.split("\n", 1)[0]) else ""
        out.extend(judge_block(path, line, block, lead_in, heading + "\n" + block))
        prev_block = block
    return out


def iter_paths(root: str):
    for prefix in SCAN_PREFIXES:
        base = os.path.join(root, prefix)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                if not fn.endswith(EXTENSIONS) or fn in SKIP_BASENAMES:
                    continue
                yield os.path.join(dirpath, fn)


def check(root: str = ROOT) -> list[Finding]:
    out: list[Finding] = []
    for full in iter_paths(root):
        rel = os.path.relpath(full, root)
        try:
            text = open(full, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        out.extend(scan_text(rel, text))
    return out


_HELP = """
⛔ EACH LINE ABOVE STATES THE PARALOGUE REQUIREMENT AS ONE BAR OVER TWO COMPARATORS. It is not.
   NR4A1-sparing is the HARD half (a named anti-target genotype a non-selective degrader
   reconstitutes); NR4A2-sparing is the SOFT half, best-effort (bounded for developmental loss,
   unbounded for the adult transient loss a degrader delivers).
   Full statement, evidence and citations: research/manuscripts/nr4a3-program-map.md §2.4.

★ HOW TO FIX ONE, AND THE ONLY TWO ACCEPTABLE FIXES:
   (a) State both weights in the same BLOCK — "NR4A1-sparing mandatory, NR4A2-sparing best-effort",
       or "the HARD half ... the SOFT half", or a link to §2.4. Rule 4 then clears it.
   (b) If the statement is a MEASUREMENT over both paralogues, it is correct and symmetric — reword
       it out of the requirement register ("scored against", not "must spare").
⛔ NOT ACCEPTABLE: deleting the superseded phrasing instead of registering it (CLAUDE.md rule 1.2),
   or loosening a rule in this file to clear a real finding.
⚠ Replacing text? Register what you replaced with an inline `⚠ *Superseded, retained: "..."*` note;
   rule 5 exempts it, and that is how the 2026-08-07 sweep's own 16 sites read today.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT, help="tree to scan (default: this repository)")
    ap.add_argument("--report", action="store_true", help="print everything, always exit 0")
    ap.add_argument("--explain", action="store_true", help="print which rule matched each finding")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on baselined open-defect rows (for whoever fixes the prose)")
    ap.add_argument("--not-bound", action="store_true", help="print the known holes and exit 0")
    args = ap.parse_args(argv)

    if args.not_bound:
        for name, why in NOT_BOUND:
            print(f"  - {name}: {why}")
        return 0

    new_findings: list[Finding] = []
    known_open: list[Finding] = []
    accepted: list[Finding] = []
    for f in check(args.root):
        row = f.baseline
        if row is None:
            new_findings.append(f)
        elif row["verdict"] == "open-defect":
            known_open.append(f)
        else:
            accepted.append(f)

    for f in new_findings:
        tag = f"  [{f.rule}]" if args.explain else ""
        print(f"{f.path}:{f.line}{tag}")
        print(f"    {f.sentence[:300]}")

    #: ⭐ THE OPEN ROWS PRINT ON EVERY RUN, GREEN OR NOT. A baselined defect that prints nothing is a
    #: defect that has been deleted, not deferred.
    for f in known_open:
        row = f.baseline or {}
        print(f"⚠ KNOWN OPEN  {f.path}:{f.line}  (baselined {row.get('first_seen')})")
        print(f"    {f.sentence[:200]}")

    if args.report:
        for f in accepted:
            print(f"· accepted, not a defect  {f.path}:{f.line}")
            print(f"    {f.sentence[:200]}")

    n_open = len(known_open)
    if not new_findings and not (args.strict and n_open):
        print(f"lint_asymmetry: 0 new symmetric restatements of the paralogue requirement"
              f" ({n_open} known open, {len(accepted)} accepted)")
        return 0
    if new_findings:
        print(f"\nlint_asymmetry: {len(new_findings)} NEW finding(s), {n_open} known open")
    else:
        print(f"\nlint_asymmetry: {n_open} known open finding(s) (--strict)")
    if args.report:
        return 0
    print(_HELP)
    return 1


if __name__ == "__main__":
    sys.exit(main())
