"""`lint_submission_residue` must go RED on the banned shapes and GREEN on the repository's own prose.

⛔ WHY THE NEGATIVE CONTROL IS THE HALF THAT DECIDES WHETHER THIS GUARD SURVIVES. Every string this
gate looks for — TODO, placeholder, "as an AI", `[ ]` — appears legitimately and often in this
repository's working prose: CLAUDE.md, AGENTS.md, the skills and the plans discuss all three
correctly, and plan files are written as `- [ ]` checklists. `lint_claims.py`'s founding lesson is
that a linter which flags true statements gets switched off, and `lint_style.py` paid for it a
second time when a cover letter's "Thank you for considering this manuscript" was reported as a
defect. So the tests below do not merely check that honest prose passes: they check that honest
prose WOULD fire and is protected by SCOPE, because a guard whose safety rests on weak patterns is
one string away from being loud, and a guard whose safety rests on its corpus is not.

⛔ AND EVERY MUTATION IS ON A COPY. The planted-trigger tests write into `tmp_path`, never into the
working tree — `research-loop` §3 added that rule on 2026-08-27 after a mutation window in the
SHARED tree let 13 inverted claims reach origin/main.
"""
import importlib.util
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lsr = _load("lint_submission_residue")


def _hits(text, rel="paper.md"):
    return {rid for rid, _line, _hit, _quote in lsr.scan_text(text, rel)}


def _matches(text, rel="paper.md"):
    return [hit for _rid, _line, hit, _quote in lsr.scan_text(text, rel)]


# ══════════════════════════════════════════════════════════════════════════════════════════
# POSITIVE CONTROL — each trigger class, planted, is caught
# ══════════════════════════════════════════════════════════════════════════════════════════

#: One planted line per shape named in the trigger list, written as it would actually survive a
#: careless paste rather than as a keyword in isolation.
META_COMMENTS = (
    "As an AI language model, I cannot assess the clinical relevance of this finding.",
    "I am an AI assistant and the analysis below reflects my training data.",
    "Certainly! The revised Discussion follows.",
    "Here is the revised Methods section, with the sampling described.",
    "Let me know if you would like the limitations paragraph shortened.",
    "Would you like me to expand the comparison with the paralogue panel?",
    "I hope this helps clarify the design of the screen.",
    "I'm sorry, but I cannot browse the primary record for that accession.",
    "I apologise for the earlier confusion about the exon numbering.",
    "Note: I could not verify the reported cohort size.",
    "Feel free to ask if a different framing of Table 2 would be preferable.",
    "I have revised the section in line with the reviewer's second point.",
)

PLACEHOLDERS = (
    "TODO: check the denominator against the registry.",
    "FIXME rewrite this paragraph once the null lands.",
    "The effect size was TKTK across the three cohorts.",
    "Cases were drawn from XXX consecutive referrals.",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "The construct was described previously [insert citation].",
    "Expression was measured in <placeholder> primary tumours.",
    "Reported in an earlier series REF? and not replicated since.",
    "This mirrors Author et al. (YEAR) in a comparable cohort.",
    "The seam was detected in 4/9 tumours [].",
    "Correspondence to: [Name], [City, Country].",
    "**Date:** [DATE]",
    "The deposit resolves at [ARCHIVE DOI] once minted.",
    "Rendered from {{ cohort_size }} records.",
    "Authors/affiliations TBD.",
    "The mechanism is well established citation needed.",
)


@pytest.mark.parametrize("line", META_COMMENTS)
def test_a_planted_model_meta_comment_is_caught(line):
    """Trigger 2. Each line is the assistant talking about the TASK, not about the science."""
    found = _hits("# Results\n\n%s\n" % line)
    assert found, "a residual model meta-comment passed unseen: %r" % line


@pytest.mark.parametrize("line", PLACEHOLDERS)
def test_a_planted_placeholder_is_caught(line):
    """Trigger 3. Each line is text a drafting pass meant to come back to and did not."""
    found = _hits("# Results\n\n%s\n" % line)
    assert found, "an unremoved placeholder passed unseen: %r" % line


def test_a_planted_trigger_fails_the_whole_gate_and_not_only_the_scanner(tmp_path):
    """⛔ THE SCANNER FINDING IT IS NOT THE GATE FAILING. A guard that detects and then exits 0 is
    the "reports while measuring nothing" defect; this test runs `check()` end to end on a corpus of
    one planted document with an EMPTY baseline, and asserts the exit code."""
    doc = tmp_path / "planted.md"
    doc.write_text("---\ntitle: x\n---\n\n# Results\n\nTODO: finish this.\n"
                   "As an AI language model, I note the following.\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"entries": []}), encoding="utf-8")
    found = lsr.findings(paths=["planted.md"], root=str(tmp_path))
    assert {f[1] for f in found} >= {"todo-marker", "ai-self-reference"}
    assert lsr.check(root=str(tmp_path), baseline_path=str(baseline), paths=["planted.md"]) != 0, \
        "the scanner found the residue and the gate still passed"


def test_the_gate_runs_in_preflight_and_its_failure_sets_rc():
    """⛔ A GUARD NOTHING RUNS IS THE INCIDENT'S SECOND HALF — the shape this repository has now
    recorded three times (`scripts/tests`, `research/autonomy/tests`, `atr_hrd_sarcoma_series
    --check`). Wiring is asserted here, not assumed."""
    sh = open(os.path.join(ROOT, "scripts", "preflight.sh"), encoding="utf-8").read()
    assert "lint_submission_residue.py" in sh, "the gate is in no preflight step"
    body = sh.split('echo "== unverified-output residue', 1)
    assert len(body) > 1, "the gate has no `== ... ==` banner, so it is not counted as a gate"
    step = body[1].split('_preflight_summary_reached', 1)[0]
    assert "rc=1" in step, "a failing residue check must set rc, or the gate reports without gating"


def test_the_gate_is_the_last_one_so_no_existing_ordinal_moved():
    """⚠ Gates 13-15's ordinals are written into `research/autonomy/ids.py`,
    `research/autonomy/priority.py` and committed ledger rows that are immutable history. Appending
    is what keeps those sentences true, and `systems_check.check_preflight_gate_list` fails the
    build on the enumerated list if it ever stops being true."""
    spec = importlib.util.spec_from_file_location(
        "_sc_for_residue", os.path.join(ROOT, "systems", "systems_check.py"))
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    gates = sc._preflight_gates()
    assert "lint_submission_residue.py" in gates[-1][1], "the residue gate is no longer last"
    assert "lint_submission_residue.py" in sc._GATE_TOOLS, \
        "a gate that owns a script must be in _GATE_TOOLS, or its entry is checked for ordinal only"


# ══════════════════════════════════════════════════════════════════════════════════════════
# NEGATIVE CONTROL — the repository's own prose is not flagged, and SCOPE is why
# ══════════════════════════════════════════════════════════════════════════════════════════

#: Documents whose whole job is to discuss TODOs, placeholders and model behaviour, correctly.
REPOSITORY_PROSE = (
    "CLAUDE.md",
    "AGENTS.md",
    "CLAUDE-history.md",
    "research/autonomy/research-ledger.json",
    "research/manuscripts/nr4a3-program-map.md",
    "research/method-watch-autonomy-prior-art-2.md",
    ".claude/skills/repo-gates/SKILL.md",
    ".claude/skills/research-loop/SKILL.md",
    ".claude/skills/paper-hardening/SKILL.md",
    "research/manuscripts/degrader/nr4a3-degrader-preprint-plan.md",
    "research/manuscripts/surface-targets/emc-surface-target-outreach.md",
)


@pytest.mark.parametrize("rel", REPOSITORY_PROSE)
def test_repository_working_prose_is_out_of_scope(rel):
    """The one property that keeps this gate alive: it never opens these files."""
    assert rel not in lsr.targets(), \
        "%s is working prose, not a document that goes out — a gate reading it will be switched off" % rel


@pytest.mark.committed_artifact
def test_the_protection_is_scope_and_not_a_weak_pattern():
    """⛔⛔ THE TEST THAT MAKES THE ONE ABOVE MEAN SOMETHING. If the rules simply did not match this
    repository's prose, the exclusion would be decorative and could be dropped without consequence
    — and the next person to widen the corpus would light up the build. So this asserts the
    opposite: the rules DO fire on working prose, in volume, and scope is the only thing holding
    them off.

    ⚠ MEASURED REPO-WIDE RATHER THAN OVER A HAND-LIST, AND THAT CHANGE IS AN INCIDENT FIX. The first
    version counted how many of `REPOSITORY_PROSE` fired and asserted `>= 5`; an upstream edit to one
    of those eleven files took the count to exactly 5, so the guard's negative control was one
    unrelated commit away from going red for a reason that had nothing to do with the guard. A
    threshold that fragile gets LOWERED, and lowering it is how this assertion becomes decorative.
    Walking every tracked `.md` outside the corpus measures the actual property instead of a sample
    of it, and cannot be moved by one file. ~4.6 s.
    """
    tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "*.md"],
                             capture_output=True, text=True, check=True).stdout.split()
    corpus = set(lsr.targets())
    outside = [f for f in tracked if f not in corpus]
    firing, hits = [], 0
    for rel in outside:
        found = lsr.scan_text(open(os.path.join(ROOT, rel), encoding="utf-8",
                                   errors="replace").read(), rel)
        if found:
            firing.append(rel)
            hits += len(found)
    assert len(outside) > 300, "the corpus swallowed the repository; scope is no longer scoping"
    assert len(firing) >= 50 and hits >= 150, (
        "the rules fire on only %d of %d non-target files (%d matches), so the scoping this gate's "
        "safety rests on now looks optional. Either the rules were weakened until they catch "
        "nothing, or the corpus grew to swallow the working prose. Both are findings."
        % (len(firing), len(outside), hits))


@pytest.mark.committed_artifact
def test_the_outgoing_corpus_carries_no_new_residue():
    """The live gate, against the live tree. NEW findings — not baselined ones — are the failure."""
    assert lsr.check() == 0, "an outgoing document carries residue that is not in the baseline"


@pytest.mark.committed_artifact
def test_the_corpus_is_derived_from_four_committed_sources_and_reaches_the_companions():
    """⛔ A HAND-LIST DRIFTS. Each assertion below names a source that must contribute, so removing
    one narrows the corpus loudly instead of silently — the shape `lint_claims.DEFAULT_TARGETS`
    records three times as "half the submission left the linted set and nothing said so"."""
    corpus = lsr.targets()
    style = _load("lint_style")
    builder = _load("build_submission_pdf")
    metrics = json.load(open(os.path.join(MANUSCRIPTS, "submission-metrics.json"), encoding="utf-8"))

    assert set(style.TARGETS) <= set(corpus), "a declared submission text is not in the corpus"
    for paper in builder.PAPERS.values():
        assert "research/manuscripts/" + paper["manuscript"] in corpus, \
            "a manuscript the PDF builder builds is not in the corpus"
    for row in metrics["rows"]:
        assert "research/manuscripts/" + row["file"] in corpus, \
            "a paper in submission form is not in the corpus"
    pubs = lsr._publication_documents(ROOT)
    assert pubs and set(pubs) <= set(corpus), "a publication endpoint's manuscript is not in the corpus"
    letters = [c for c in corpus if c.endswith("-cover-letter.md")]
    assert len(letters) >= 5, "the cover letters are what an editor reads first: %r" % letters
    assert any(c.endswith("-SI.md") for c in corpus), "no supplementary information reached the corpus"


# ══════════════════════════════════════════════════════════════════════════════════════════
# The two exemptions, each of which is a place a weakening could hide
# ══════════════════════════════════════════════════════════════════════════════════════════

def test_frontmatter_is_exempt_and_the_body_is_not():
    """⚠ Frontmatter is repository metadata the PDF builders strip. Before this exemption the
    `canonical_for: []` and `related: [DOC-…]` keys produced 34 findings across 39 documents, none
    of them prose — the cry-wolf volume that gets a gate switched off."""
    doc = "---\ncanonical_for: []\nrelated: [DOC-THING]\n---\n\n# Results\n\nThe cohort was [].\n"
    assert _matches(doc).count("[]") == 1, "the frontmatter's empty list was counted, or the body's was not"


def test_frontmatter_blanking_does_not_shift_the_reported_line():
    """A finding's value is the line a reader can open at the moment the gate has failed."""
    doc = "---\ntitle: x\nrelated: [DOC-THING]\n---\n\n# H\n\nTODO fix this.\n"
    assert doc.splitlines()[7] == "TODO fix this.", "the fixture moved; re-derive the expected line"
    found = lsr.scan_text(doc, "paper.md")
    assert [f[1] for f in found] == [8], "the line number moved when the frontmatter was blanked"


def test_a_cover_letter_keeps_its_correspondence_conventions():
    """⛔ `lint_style.py` WAS GIVEN THE COVER LETTERS AND TAKEN OFF THEM AGAIN ON MEASUREMENT,
    because it reported "Thank you for considering this manuscript" and "Yours sincerely" as
    defects, "and a gate that reports a salutation as a defect is one its reader learns to skip".
    "Please let me know if you need anything further" is in exactly that class."""
    letter = "Dear Editor,\n\nPlease let me know if you need anything further.\n\nYours sincerely,\n"
    assert not _hits(letter, "paper-cover-letter.md"), "a letter convention was reported as residue"
    assert _hits(letter, "paper.md"), \
        "the same sentence in a MANUSCRIPT is the assistant addressing its requester and must fire"


def test_the_cover_letter_exemption_is_narrow():
    """⚠ THE EXEMPTION IS PER-RULE, NOT PER-FILE. A cover letter is the document an editor reads
    first; exempting it wholesale would put the highest-stakes page outside the gate."""
    assert set(lsr.COVER_LETTER_EXEMPT) == {"handover", "handover-correspondence"}, \
        "the exempt set changed — %r" % (lsr.COVER_LETTER_EXEMPT,)
    letter = ("Dear Editor,\n\nAs an AI language model I summarise the work below.\n"
              "**Date:** [DATE]\nTODO: name the venue.\n")
    assert _hits(letter, "x-cover-letter.md") >= {"ai-self-reference", "todo-marker",
                                                  "bracket-placeholder"}


# ══════════════════════════════════════════════════════════════════════════════════════════
# The ledger — it may only shrink, and it may not be self-served
# ══════════════════════════════════════════════════════════════════════════════════════════

def test_a_baseline_row_is_keyed_to_the_text_and_not_to_a_line():
    """⛔ A LINE-KEYED BASELINE IS AMNESTY FOR WHATEVER DRIFTS ONTO THAT LINE."""
    a = lsr.key("paper.md", "todo-marker", "TODO")
    assert a == lsr.key("paper.md", "todo-marker", "TODO")
    assert a != lsr.key("paper.md", "todo-marker", "TBD")
    assert a != lsr.key("other.md", "todo-marker", "TODO")
    assert "\n" not in a and str(7) not in a.replace("paper.md", "")


def test_a_baselined_string_passes_and_a_different_one_in_the_same_file_does_not(tmp_path):
    """The ledger covers exactly the string it was written for."""
    doc = tmp_path / "paper.md"
    doc.write_text("# H\n\nAuthors TBD.\n", encoding="utf-8")
    baseline = tmp_path / "b.json"
    baseline.write_text(json.dumps({"entries": [
        {"key": lsr.key("paper.md", "todo-marker", "TBD"), "file": "paper.md",
         "rule": "todo-marker", "text": "TBD", "why": "draft author block"}]}), encoding="utf-8")
    assert lsr.check(root=str(tmp_path), baseline_path=str(baseline),
                     paths=["paper.md"]) == 0
    doc.write_text("# H\n\nAuthors TBD. TODO name them.\n", encoding="utf-8")
    assert lsr.check(root=str(tmp_path), baseline_path=str(baseline),
                     paths=["paper.md"]) != 0, \
        "a NEW placeholder in a file that already has a baselined one was waved through"


def test_a_resolved_baseline_row_fails_until_it_is_deleted(tmp_path):
    """⛔ AN UNPRUNED ROW IS STANDING PERMISSION FOR THE STRING TO RETURN. The count is meant to
    fall, and it only falls honestly if the ledger cannot keep rows past their finding."""
    (tmp_path / "paper.md").write_text("# H\n\nAll authors named.\n", encoding="utf-8")
    baseline = tmp_path / "b.json"
    baseline.write_text(json.dumps({"entries": [
        {"key": lsr.key("paper.md", "todo-marker", "TBD"), "file": "paper.md",
         "rule": "todo-marker", "text": "TBD", "why": "draft author block"}]}), encoding="utf-8")
    assert lsr.check(root=str(tmp_path), baseline_path=str(baseline),
                     paths=["paper.md"]) != 0
    baseline.write_text(json.dumps({"entries": []}), encoding="utf-8")
    assert lsr.check(root=str(tmp_path), baseline_path=str(baseline),
                     paths=["paper.md"]) == 0


def test_the_baseline_cannot_be_rewritten_to_clear_a_red_gate(tmp_path):
    """⚠ THE SAME REFUSAL `lint_citations --baseline` CARRIES. A self-service baseline is an
    off-switch with a JSON file in front of it."""
    path = tmp_path / "b.json"
    path.write_text(json.dumps({"entries": []}), encoding="utf-8")
    assert lsr.write_baseline(root=str(tmp_path), path=str(path)) != 0
    assert json.loads(path.read_text())["entries"] == [], "the existing ledger was overwritten"


@pytest.mark.committed_artifact
def test_every_baseline_row_carries_a_reason_a_human_wrote():
    """⛔ A ROW WITHOUT A `why` IS AN AMNESTY, NOT A LEDGER — and `--baseline` stamps every row it
    writes `UNREVIEWED`, so a committed row still carrying that word is one nobody read."""
    doc = lsr.load_baseline()
    assert doc and doc["entries"], "the baseline is the finding; an empty one is not a pass"
    for row in doc["entries"]:
        for field in ("key", "file", "rule", "text", "why"):
            assert str(row.get(field) or "").strip(), "%r has no %s" % (row.get("file"), field)
        assert "UNREVIEWED" not in row["why"], \
            "%s carries the --baseline stamp: nobody read it" % row["file"]
    keys = [row["key"] for row in doc["entries"]]
    assert len(keys) == len(set(keys)), "a duplicate key hides one of the two rows it names"


# ══════════════════════════════════════════════════════════════════════════════════════════
# Trigger 1 is gate 6's, and the honest statement of that is itself checked
# ══════════════════════════════════════════════════════════════════════════════════════════

def test_the_module_does_not_claim_to_cover_hallucinated_references():
    """⚠ AN HONEST UNKNOWN BEATS A SECOND OVERLAPPING GUARD. `lint_citations` (gate 6) owns
    identifier provenance; this module must neither duplicate it nor imply the trigger is closed."""
    src = open(os.path.join(MANUSCRIPTS, "lint_submission_residue.py"), encoding="utf-8").read()
    assert "lint_citations" in src, "the module must name the gate that owns trigger 1"
    gaps = lsr.UNCOVERED_BY_LINT_CITATIONS
    assert len(gaps) >= 6, \
        "the named gaps in identifier provenance are the honest half of this gate's scope"
    for gap in gaps:
        assert gap.strip(), "an empty gap line reports while measuring nothing"

    # ⛔⛔ THE COUNT AND THE NON-EMPTINESS WERE THE WHOLE ASSERTION, AND MUTATION M17 WALKED THROUGH
    # IT (2026-08-28, post-merge run). Corrupting the text of an entry left the length and the
    # `.strip()` both true, so the list could say anything at all — including nothing about the
    # defect it was extended for. A list whose CONTENT nothing reads is documentation wearing an
    # assertion's costume, which is this repository's most-repeated shape.
    # ⚠ THE FIX IS NOT TO ASSERT THE STRINGS, WHICH WOULD BE A TAUTOLOGY. It is to assert that each
    # DISTINCT MECHANISM the list claims to enumerate is still named, so dropping or garbling one
    # family is caught while rewording an entry is not.
    joined = " | ".join(gaps).lower()
    for mechanism, why in (
        ("arxiv", "arXiv identifiers match no pattern in lint_citations.PATTERNS"),
        ("no pmid/pmcid/doi/nct/geo identifier",
         "a reference carrying no machine-readable identifier is never extracted"),
        ("aut-pd-038",
         "a record of a fetch that FAILED still anchors — measured on a submission reference "
         "list, and the one gap in this family with a filed fix"),
    ):
        assert mechanism in joined, (
            "UNCOVERED_BY_LINT_CITATIONS no longer names this gap: %s. Either it was genuinely "
            "closed — in which case say so where the fix landed and remove it deliberately — or "
            "the honest scope statement has been quietly narrowed." % why)


def test_the_policy_is_recorded_as_search_grade_and_never_quoted_as_fact():
    """⛔ §7: NEVER WRITE AN IDENTIFIER OR A QUOTATION FROM RECOLLECTION. The trigger list reached
    this repository through a secondary news item; arxiv.org is refused at this sandbox's egress
    proxy, so the policy's wording, date and scope have been read by nobody here."""
    prov = lsr._POLICY_PROVENANCE
    assert prov["grade"].startswith("SEARCH")
    for field in ("policy_wording", "policy_date", "policy_scope"):
        assert prov[field].startswith("UNKNOWN"), \
            "%s is asserted rather than recorded as unread — that is a fabricated citation" % field
    src = open(os.path.join(MANUSCRIPTS, "lint_submission_residue.py"), encoding="utf-8").read()
    assert "arxiv.org" not in src.lower().replace("arxiv.org is refused", ""), \
        "the module names the venue outside its provenance note"


@pytest.mark.committed_artifact
def test_the_gate_is_cheap_enough_for_the_commit_loop():
    """⚠ THE FAST TIER IS ~75 s AND ITS COST IS A REAL CONSTRAINT (CLAUDE.md §6). A gate that
    quietly grew into a suite is one somebody will move behind a flag."""
    import time
    start = time.time()
    subprocess.run(["python3", os.path.join(MANUSCRIPTS, "lint_submission_residue.py")],
                   cwd=ROOT, capture_output=True, text=True, check=True)
    elapsed = time.time() - start
    assert elapsed < 5.0, "the residue gate took %.2f s; it was 0.6 s when it was written" % elapsed
