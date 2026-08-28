"""`claim-ceiling-grade-map.json` must cover every rule `lint_claims.py` ACTUALLY has.

⛔ WHY THIS TEST EXISTS, MEASURED RATHER THAN IMAGINED. `lint_claims.py` grew an R6 family
(`R6-unsurveyed-field-practice`) on 2026-08-15. The ledger row that commissioned the GRADE mapping —
AUT-PROP-037, filed 2026-08-27 — still describes the linter as "R1–R5", and so did the roadmap
sentence the row quotes. A whole rule family arrived and every description of the gate stayed
twelve days behind it, with every gate green the entire time, because nothing joined the rule table
to the prose about the rule table. **The silent-R6 failure is not hypothetical here; it already
happened once, and this file is the join that would have caught it.**

★ THE TEST IS BIDIRECTIONAL, AND BOTH DIRECTIONS ARE REAL DEFECTS.
  * a rule with no GRADE row  → a ceiling nobody can read without the glossary; the failure above.
  * a GRADE row with no rule  → a published ceiling for a rule that no longer exists, which is a
    FABRICATED ceiling. `paper-hardening`'s one-of-a-pair defect class: the pair is the rule and its
    translation, and a checker that only walks one way finds only half the drift.

⛔ IT ALSO PINS THE SEVERITY AND THE CLEARER each row was written against. A rule flipped from
WARN to ERROR, or from `hedge` to `disclaimer`, is a rule whose ceiling was just re-argued by
somebody; the row must be re-read, not silently inherited.

⛔ AND IT ASSERTS THE MAPPING IS NOT A GATE. `lint_claims.py` must not read this file: the whole
point of AUT-PROP-037 is a LABELLING layer over an unchanged enforcement mechanism. A test that the
linter never imports the map is what keeps "translation layer" from drifting into "second linter".
Same reason the GRADErater check is here: the row's hard constraint is that no third-party
automation of unmeasured accuracy is wired into any gate, and a constraint checked by nothing is a
hope (CLAUDE.md §6).

Every check below is a pure function over PATHS, so the mutation harness can point it at a copy —
never at the working tree (`research-loop` §3, after a mutation window in the shared tree let 13
inverted claims reach origin/main).
"""
import importlib.util
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))

LINT_PATH = os.path.join(MANUSCRIPTS, "lint_claims.py")
MAP_PATH = os.path.join(MANUSCRIPTS, "claim-ceiling-grade-map.json")

#: The four GRADE ratings, plus this repository's own NO_EVIDENCE label. Closed on purpose: an
#: invented rung ("Moderate-low", "N/A") is how a standard vocabulary stops being standard, which
#: is the entire benefit the mapping exists to buy.
ALLOWED_CEILINGS = {"HIGH", "MODERATE", "LOW", "VERY_LOW", "NO_EVIDENCE"}

#: A justification shorter than this is an assertion, not a derivation. The row's whole job is to
#: say what the RULE DOES that fixes the ceiling.
MIN_JUSTIFICATION = 120


# ---------------------------------------------------------------------------------------------
# loaders — both take a path so the mutation harness can hand them a copy
# ---------------------------------------------------------------------------------------------

def load_rules(lint_path=LINT_PATH):
    """[(rid, severity, clears_on)] straight from the linter's own RULES table.

    ⚠ Imported and executed, never regex-scraped. A rule added by any means the module supports —
    a literal, a loop, a conditional append — has to appear here, and a scraper would miss it.
    """
    spec = importlib.util.spec_from_file_location("lint_claims_under_test", lint_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [(r.rid, r.severity, r.clears_on) for r in mod.RULES]


def load_map(map_path=MAP_PATH):
    with open(map_path, encoding="utf-8") as fh:
        return json.load(fh)


def _family(rid):
    return rid.split("-", 1)[0]


# ---------------------------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------------------------

def coverage_findings(doc, rules):
    """Every linter rule has a row; every row names a live rule; every family has a note."""
    out = []
    rule_ids = [rid for rid, _, _ in rules]
    row_ids = [r["rule_id"] for r in doc["rows"]]

    dupes = {r for r in row_ids if row_ids.count(r) > 1}
    for rid in sorted(dupes):
        out.append(f"DUPLICATE row for {rid} — two ceilings for one rule is no ceiling")

    for rid in rule_ids:
        if rid not in row_ids:
            out.append(f"UNMAPPED {rid} — lint_claims.py enforces it and no GRADE row explains it")
    for rid in row_ids:
        if rid not in rule_ids:
            out.append(f"STALE row {rid} — no such rule in lint_claims.py; a ceiling for nothing")

    for rid in rule_ids:
        if _family(rid) not in doc["families"]:
            out.append(f"UNDESCRIBED family {_family(rid)} (from {rid}) — a new family arrived "
                       f"with no prose saying what it regulates")
    return out


def drift_findings(doc, rules):
    """The severity and clearer each row was argued against are still the live ones."""
    live = {rid: (sev, clears) for rid, sev, clears in rules}
    out = []
    for row in doc["rows"]:
        if row["rule_id"] not in live:
            continue                      # coverage_findings owns that one
        sev, clears = live[row["rule_id"]]
        if row.get("linter_severity") != sev:
            out.append(f"{row['rule_id']}: row says severity {row.get('linter_severity')!r}, "
                       f"lint_claims.py says {sev!r} — the ceiling was argued against the old one")
        if row.get("linter_clears_on") != clears:
            out.append(f"{row['rule_id']}: row says clears_on {row.get('linter_clears_on')!r}, "
                       f"lint_claims.py says {clears!r} — what clears a rule is part of what it does")
    return out


def vocabulary_findings(doc):
    """Closed rung vocabulary, and applicable/ceiling kept consistent in both directions."""
    out = []
    for name in ALLOWED_CEILINGS:
        if name not in doc["grade_vocabulary"]:
            out.append(f"grade_vocabulary is missing {name} — a rung used but never defined")
    for row in doc["rows"]:
        rid, ceiling, applicable = row["rule_id"], row["grade_ceiling"], row["grade_applicable"]
        if applicable:
            if ceiling not in ALLOWED_CEILINGS:
                out.append(f"{rid}: ceiling {ceiling!r} is not one of {sorted(ALLOWED_CEILINGS)}")
        else:
            if ceiling is not None:
                out.append(f"{rid}: grade_applicable is false but a ceiling {ceiling!r} is given — "
                           f"a rating on a claim GRADE does not rate is the misfit this file refuses")
            if not (row.get("not_applicable_because") or "").strip():
                out.append(f"{rid}: unmappable with no reason given — 'does not fit' unexplained is "
                           f"worse than a forced mapping, because nobody can check it")
        if len((row.get("justification") or "").strip()) < MIN_JUSTIFICATION:
            out.append(f"{rid}: justification is missing or too short to derive anything")
    return out


def independence_findings(lint_path=LINT_PATH, map_path=MAP_PATH):
    """⛔ The linter must not read the map. The enforcement mechanism is unchanged by design."""
    with open(lint_path, encoding="utf-8") as fh:
        src = fh.read()
    out = []
    if os.path.basename(map_path) in src:
        out.append("lint_claims.py names claim-ceiling-grade-map.json — the mapping is a LABEL, "
                   "not an input to the gate; AUT-PROP-037 forbids changing the mechanism")
    return out


def automation_findings(root=ROOT):
    """⛔ No gate may depend on GRADErater: SEARCH-grade, paper unread, accuracy UNKNOWN."""
    scanned = [
        os.path.join(root, "scripts", "preflight.sh"),
        os.path.join(root, "research", "manuscripts", "lint_claims.py"),
        os.path.join(root, ".github", "workflows", "tests.yml"),
    ]
    out = []
    for path in scanned:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            if re.search(r"graderater", fh.read(), re.IGNORECASE):
                out.append(f"{os.path.relpath(path, root)} references GRADErater — a third-party "
                           f"automation with no measured accuracy must not be in any gate")
    return out


# ---------------------------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------------------------

@pytest.mark.committed_artifact
def test_every_lint_claims_rule_has_a_grade_row_and_vice_versa():
    """The join that would have caught R6 arriving silently."""
    findings = coverage_findings(load_map(), load_rules())
    assert not findings, "\n".join(findings)


@pytest.mark.committed_artifact
def test_no_row_was_argued_against_a_severity_or_clearer_that_has_since_changed():
    findings = drift_findings(load_map(), load_rules())
    assert not findings, "\n".join(findings)


@pytest.mark.committed_artifact
def test_the_rung_vocabulary_is_closed_and_the_misfits_are_declared():
    findings = vocabulary_findings(load_map())
    assert not findings, "\n".join(findings)


def test_the_mapping_is_a_label_and_not_an_input_to_the_gate():
    findings = independence_findings()
    assert not findings, "\n".join(findings)


def test_no_gate_depends_on_graderater():
    findings = automation_findings()
    assert not findings, "\n".join(findings)


@pytest.mark.committed_artifact
def test_no_evidence_is_never_presented_as_a_grade_rating():
    """⛔ The one place this mapping could mislead an outside reader, pinned.

    NO_EVIDENCE is this repository's label for an EMPTY body of evidence. GRADE's scale bottoms out
    at very low (Cochrane ch14). If the definition ever loses the disclaimer, a reader sees five
    GRADE rungs where GRADE defines four.
    """
    text = load_map()["grade_vocabulary"]["NO_EVIDENCE"]
    assert "NOT A GRADE RATING" in text, "the NO_EVIDENCE entry must disclaim itself in its own text"
