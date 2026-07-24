#!/usr/bin/env python3
"""Language-discipline linter for the NR4A3 degrader manuscript and its SI.

WHY THIS EXISTS
---------------
`STRATEGY.md` -> "Honest scope and language discipline (apply everywhere, including the
manuscript)" states hard rules about what the manuscript may and may not assert. Until
now those rules had **zero automated enforcement** -- they were a prose instruction that a
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

RULES IMPLEMENTED (each cites its STRATEGY.md source line)
----------------------------------------------------------
  R1  earned-phrase substitutions      STRATEGY.md "selective hit" -> "predicted selective candidate" etc.
  R2  never-imply set                  STRATEGY.md "Never imply proteome-wide selectivity, EMC efficacy,
                                       safety, a therapeutic window, or clinical readiness."
  R3  novelty right-sizing             STRATEGY.md "Novelty is incremental, not landmark."
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
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The manuscript IS the preprint IS the submission (CLAUDE.md single-source-of-truth rule),
# so the default set is the paper + its SI. Other docs can be passed explicitly.
DEFAULT_TARGETS = [
    "research/manuscripts/nr4a3-degrader-paper.md",
    "research/manuscripts/nr4a3-degrader-paper-SI.md",
]

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
        'STRATEGY.md "selective hit" -> "predicted selective candidate"',
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
        'STRATEGY.md "synthesis-ready matrix" -> earned phrase',
        clears_on="local_negation",
    ),
    Rule(
        "R1-nr4a3-selective",
        r"\bNR4A3-selective\b",
        "WARN",
        'prefer "predicted NR4A-paralogue-selective" unless the sentence already scopes it',
        'STRATEGY.md "NR4A3-selective" -> "predicted NR4A-paralogue-selective"',
        clears_on="hedge",
    ),
    Rule(
        "R1-does-bind",
        r"\b(?:does|do) bind\b|\bbinds? at all\b",
        "WARN",
        'say "is compatible with the hypothesized conditional bound state"',
        'STRATEGY.md "does bind at all" -> conditional bound state',
        clears_on="hedge",
    ),
    Rule(
        "R1-recovered-degradation",
        r"\brecovered (?:the )?degradation\b",
        "ERROR",
        'say "produced a surrogate score concordant with the reported outcome"',
        'STRATEGY.md "recovered degradation" -> surrogate-score concordance',
        clears_on=None,
    ),
    # -- R2: never-imply set -------------------------------------------------------------
    # These are regulated words, NOT banned words. Disclaimed use is correct and passes.
    Rule(
        "R2-efficacy",
        r"\befficac(?:y|ious)\b",
        "ERROR",
        "efficacy may only appear in a sentence that scopes the claim OUT",
        "STRATEGY.md Never imply ... EMC efficacy",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-therapeutic-window",
        r"\btherapeutic window\b",
        "ERROR",
        "a therapeutic window may only appear scoped out (or when describing prior art)",
        "STRATEGY.md Never imply ... a therapeutic window",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-clinical-readiness",
        r"\bclinical(?:ly)? read(?:y|iness)\b|\bready for the clinic\b|\bclinic[- ]ready\b",
        "ERROR",
        "never imply clinical readiness",
        "STRATEGY.md Never imply ... clinical readiness",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-safe",
        r"\bis safe\b|\bsafe and effective\b|\bwell[- ]tolerated\b|\bsafety (?:is |was )?(?:established|demonstrated|shown)\b",
        "ERROR",
        "never imply safety",
        "STRATEGY.md Never imply ... safety",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-proteome-wide",
        r"\bproteome[- ]wide selectiv\w*\b|\bselective across the proteome\b",
        "ERROR",
        "never imply proteome-wide selectivity (nothing here tests off-family targets)",
        "STRATEGY.md Never imply proteome-wide selectivity",
        clears_on="disclaimer",
    ),
    Rule(
        "R2-treats-cures",
        r"\b(?:cures?|cured|treats|will treat|therapy for EMC\b)",
        "ERROR",
        "no treatment claim -- degradation is experimentally unvalidated",
        "STRATEGY.md final deliverable: degradation experimentally unvalidated",
        clears_on="disclaimer",
    ),
    # -- R3: novelty right-sizing --------------------------------------------------------
    Rule(
        "R3-landmark",
        r"\blandmark\b|\bunprecedented\b|\bbreakthrough\b|\bfirst[- ]ever\b|\bparadigm[- ]shift\w*\b",
        "ERROR",
        "novelty is incremental, not landmark -- all-atom ternary-cooperativity FEP is an "
        "active published area (Chen 2023; JCTC 2025; JCIM 2024) and must be cited, not out-claimed",
        "STRATEGY.md Novelty is incremental, not landmark",
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
        "a first-in-field claim needs the prior-art citations STRATEGY.md mandates "
        "(Chen 2023; JCTC 2025 5c00064/5c00736; JCIM 2024 4c01227)",
        "STRATEGY.md The paper must cite and benchmark against this prior art",
        clears_on="disclaimer",
    ),
    # -- R4: evidentiary-verb discipline --------------------------------------------------
    Rule(
        "R4-proves",
        r"\bprove[sd]?\b|\bproven\b|\bproof that\b",
        "WARN",
        "a computational result does not prove -- say what it is evidence *for*, conditionally",
        "STRATEGY.md everything is conditional on the hypothesized pose x receptor frame",
        clears_on="disclaimer",
    ),
    Rule(
        "R4-confirms",
        r"\bconfirm(?:s|ed|ation)\b|\bestablishes?\b(?! a )|\bvalidates?\b|\bvalidated\b",
        "WARN",
        "reserve confirm/establish/validate for results with a committed primary artifact; "
        "otherwise say concordant / consistent with",
        "STRATEGY.md language discipline",
        clears_on="disclaimer",
    ),
    # -- R5: measured vs projected --------------------------------------------------------
    Rule(
        "R5-measured-edge-cost",
        r"\bmeasured\b[^.\n]{0,80}\$|\$[^.\n]{0,60}\bmeasured\b",
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
LOCAL_NEGATION_WINDOW = 40
LOCAL_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|nor|non|isn't|aren't|without|rather than|instead of|as opposed to)\b"
    r"[\s\w,]{0,20}$",
    re.IGNORECASE,
)


def _locally_negated(sent, match_start):
    """True if a negation sits close enough before the match to scope it. Pure."""
    return bool(LOCAL_NEGATION_RE.search(sent[max(0, match_start - LOCAL_NEGATION_WINDOW):match_start]))


def lint_file(path):
    findings = []
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    for para, offsets in iter_paragraphs(lines):
        for start, sent in split_sentences(para):
            has_disclaimer = bool(DISCLAIMER_RE.search(sent))
            has_hedge = has_disclaimer or bool(HEDGE_RE.search(sent))
            for rule in RULES:
                m = rule.re.search(sent)
                if not m:
                    continue
                if rule.clears_on == "disclaimer" and has_disclaimer:
                    continue
                if rule.clears_on == "hedge" and has_hedge:
                    continue
                if rule.clears_on == "local_negation" and _locally_negated(sent, m.start()):
                    continue
                if rule.context_re is not None and not rule.context_re.search(sent):
                    continue
                pos = start + m.start()
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
