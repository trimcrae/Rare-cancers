"""⛔ THE PAPERS SEND A READER TO A ZENODO RECORD. THIS ASKS WHETHER THAT RECORD STILL AGREES.

A Zenodo version is immutable once published and the repository is not, so the two drift apart by
construction. The only question that matters is whether anyone knows by how much.

⛔ NOBODY DID (round 15, 2026-08-22, found independently by three of five reviewers). The record was
published with 473 files; the repository had moved 16 files and added 4, and the changed set included
the extended report itself. Two of its changes were CORRECTIONS — the void-test definition, and a
claim that the dinucleotide-preserving scramble holds the 5′ guanine run — so a reader following the
citation read statements this repository had already retracted. Every gate was green because
`aso_archive_manifest.py --check-archive` compares the manifest to the WORKING TREE, so it goes green
exactly as the tree walks away from the deposit, and `archive_content_digest` lives inside the
manifest that computes it, so it can never disagree with itself.

★ THE THREE STATES THIS GUARD DISTINGUISHES, because collapsing them is what hid the defect:

  SETTLED   the papers cite the published version and the tree matches what was published.
  PENDING   a corrected version has been DRAFTED and the papers cite it. It does not resolve yet.
            This is not a defect — it is the reserve-then-rebuild ordering working: the manuscript
            has to print the identifier the archive will carry BEFORE the files are frozen, because
            a published version cannot be edited. It must be openly tracked, not silent.
  DRIFTED   the tree has moved away from what is published and nothing has been drafted or said.
            This is the defect, and it is the one that shipped.

⚠ WHAT THIS GUARD DOES NOT DO IS DEMAND THE DEPOSIT BE CURRENT. Drift between deposits is normal and
a gate that is red for weeks is a gate that gets switched off. It demands that drift be
ACKNOWLEDGED — by a drafted version, or by an open blocking item in the preprint checklist — and that
the acknowledgement be REMOVED once it is settled. Silence in either direction is the failure.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
STATE = os.path.join(ASO, "deposit-state.json")
CHECKLIST = os.path.join(ASO, "fusion-junction-aso-preprint-checklist.md")
REPO = os.path.abspath(os.path.join(ASO, "..", "..", ".."))

_OPEN_HEADING = "## 3 · Open, and blocking the journal submission"


def _json(path, what):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing, so {what} is unknown")
    return json.load(open(path, encoding="utf-8"))


def _commit_is_present(rev):
    """Is `rev` a commit this checkout can read — fetching it once if the clone is shallow?

    ⛔⛔ AN ABSENT OBJECT IS NOT AN ABSENT COMMIT, AND THIS GUARD COULD NOT TELL THE DIFFERENCE.
    Measured 2026-09-01: it was red on `main` reporting that the published record's revision "is not
    a commit in this repository", while that sha sits on `origin/main` and resolves fine in a full
    clone. `actions/checkout@v4` clones at depth 1, so CI has exactly one commit and every recorded
    revision looks fabricated to it — CLAUDE.md §4, "an absent reading is not a reading of absence",
    inside the guard whose whole job is to tell declared from corroborated.

    ★ AND THE ANSWER IS A $0 FETCH RATHER THAN A DEGRADE. Measured against the real remote before
    this was written: in a fresh `git clone --depth 1`, `git cat-file -e` on the recorded sha fails,
    `git fetch --depth=1 origin <sha>` succeeds, and afterwards both `cat-file` and
    `git show <sha>:…archive-manifest.json` work — the manifest read back at that revision carries
    `archive_content_digest a4d4ad6f1ca0…`, the value `published.manifest_digest` records. So the
    corroboration this file exists for RUNS IN CI instead of being announced as skipped, which is
    what a sibling guard (`test_the_manifest_revision_is_a_commit_a_reader_can_resolve`) has to do
    because it is checking reachability rather than content.

    ⚠ IT RETURNS FALSE RATHER THAN RAISING WHEN THE FETCH CANNOT RUN. Offline, the honest reading is
    still "this checkout cannot produce that commit"; the caller says so, and a genuinely fabricated
    revision fails here for the same reason. Bounded to one attempt — a retry loop in a test is a
    timeout waiting to be blamed on the network.
    """
    def _has():
        return subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"],
                              cwd=REPO, capture_output=True).returncode == 0
    if _has():
        return True
    if subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO,
                      capture_output=True, text=True).stdout.strip() != "true":
        return False          # a full clone that lacks it genuinely lacks it
    subprocess.run(["git", "fetch", "--depth=1", "origin", rev],
                   cwd=REPO, capture_output=True, timeout=180)
    return _has()

def test_the_papers_cite_a_version_the_deposit_state_knows_about():
    """⛔ THE MANIFEST'S DOI IS EITHER WHAT IS PUBLISHED OR WHAT IS DRAFTED — NEVER A THIRD THING."""
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    cited = manifest.get("deposition_doi")
    known = {state["published"]["doi"]}
    pending = state.get("pending")
    if pending:
        known.add(pending["doi"])
    assert cited in known, (
        f"the manifest and the papers cite {cited}, which deposit-state.json neither records as "
        f"published ({state['published']['doi']}) nor as drafted "
        f"({pending['doi'] if pending else 'nothing drafted'}). A DOI in the manuscript that no "
        "deposit state accounts for is an identifier nobody can check.")
    doi_key = cited.split("zenodo.")[-1]
    citing = [n for n in os.listdir(ASO)
              if n.endswith(".md") and doi_key in open(os.path.join(ASO, n), encoding="utf-8").read()]
    assert citing, (f"no document in aso/ cites {cited}, so this guard is watching a record nothing "
                    "points at — re-anchor it or retire it")


def _open_blocking_section(text):
    """§3's slice of the checklist, or "" if that heading is gone."""
    if _OPEN_HEADING not in text:
        return ""
    return re.split(r"(?m)^## ", text.split(_OPEN_HEADING, 1)[1], maxsplit=1)[0]


def _open_blocking_section_declares_the_drift(text):
    """Is the deposit item under the OPEN BLOCKING heading — not merely somewhere in the file?

    ⛔⛔ THIS WAS `_OPEN_HEADING in text and "PUBLISHED DEPOSIT IS BEHIND" in text.upper()`, WHICH
    TESTS ONLY THAT BOTH STRINGS OCCUR SOMEWHERE (round 16 seat 5, 2026-08-22). Moving the entire
    deposit item OUT of "## 3 · Open, and blocking the journal submission" — leaving that section
    reading "*Nothing.*" — and UP into "## 1 · Ready, and needs nothing further" left both
    substrings present and the guard green. The guard's own failure message demands "an open
    blocking item under '## 3 …'"; what it checked was that the heading exists.
    ★ A section is a SLICE, not a substring. The item has to be inside §3's slice, which is the
    only reading under which the message and the check say the same thing.
    """
    return "PUBLISHED DEPOSIT IS BEHIND" in _open_blocking_section(text).upper()


def test_an_unpublished_version_or_a_drifted_tree_is_openly_tracked():
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    pending = state.get("pending")
    drifted = manifest.get("archive_content_digest") != state["published"]["manifest_digest"]

    assert os.path.exists(CHECKLIST), "the preprint checklist is missing; re-anchor this guard"
    text = open(CHECKLIST, encoding="utf-8").read()
    declared = _open_blocking_section_declares_the_drift(text)

    if pending:
        assert declared, (
            f"version {pending['doi']} has been drafted and the papers cite it, but it is NOT "
            "published — so every archive link in both manuscripts currently resolves to nothing. "
            f"That has to be an open blocking item under '{_OPEN_HEADING}' in "
            f"{os.path.basename(CHECKLIST)} until someone publishes it by hand.")
        assert pending["doi"] in text, (
            f"the checklist tracks the deposit as open but never names the drafted version "
            f"{pending['doi']}, so nobody reading it knows what to publish")
        return

    if drifted:
        assert declared, (
            "the published Zenodo record no longer matches what this repository would archive, "
            "nothing has been drafted, and the papers that cite it say nothing about that. Either "
            "draft a corrected version (dispatch deposit-zenodo.yml with new_version=true), or "
            f"record the drift as an open blocking item under '{_OPEN_HEADING}'. A reader "
            "following the DOI is reading superseded text until one of those happens.")
    else:
        assert not declared, (
            "the checklist still carries the deposit-is-behind blocking item, but nothing is "
            "drafted and the manifest matches the digest recorded as published. Close the item — a "
            "checklist that keeps a solved blocker open is one nobody reads.")


def test_a_declared_drift_states_the_size_it_actually_has():
    """⛔⛔ AN ACKNOWLEDGEMENT WHOSE CONTENT IS FALSE SATISFIED THIS FILE FOR FIVE COMMITS.

    ⚠ Measured by three of round 22's five seats independently, 2026-08-30. §3-iv read "★ IT IS
    EXACTLY ONE FILE … No manuscript source, table, figure, sequence file or `.docx` moved" while the
    real figure was FIFTEEN, including the journal article and all four of its PDFs. It was true when
    written at `3df0be6c5` and false from `29a44d203`, which changed the article and did not revisit
    the section.

    ⛔ AND `_open_blocking_section_declares_the_drift` COULD NOT SEE IT, BECAUSE IT ASKS WHETHER THE
    STRING "PUBLISHED DEPOSIT IS BEHIND" APPEARS. Presence of an acknowledgement is not correctness
    of one — the same distinction this file's own docstring already draws twice, at the level of
    WHERE the item sits ("a section is a SLICE, not a substring") and of WHAT VERB it uses ("a report
    that the refresh already happened is not an instruction to perform it"). This is the third
    instance, one level up again: the item said the right words about the wrong number.

    ★ SO THE DECLARATION MUST NAME THE SIZE, AND THE SIZE IS DERIVED FROM GIT RATHER THAN READ FROM
    THE PROSE. A count typed into the checklist that disagrees with the manifests fails here, which
    is the only reading under which "acknowledged" means anything.

    ⚠ WHAT THIS DELIBERATELY DOES NOT DO: demand a particular sentence, a particular wording, or that
    the drift be FIXED. Drift between deposits is normal; a gate that required a current deposit
    would be red for weeks and would get switched off. It requires only that the number in the
    section be the number git computes.
    """
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    if manifest.get("archive_content_digest") == state["published"]["manifest_digest"]:
        pytest.skip("the tree matches the published deposit, so there is no drift to size "
                    "— SKIP IS DELIBERATE and is the settled state between deposits")

    rev = state["published"].get("git_revision")
    # ⛔ THE THIRD SITE OF THE SAME PAIR, AND ITS FAILURE MODE IS A SILENT SKIP RATHER THAN A RED.
    # Two tests in this file resolve a recorded revision and both now fetch it when the clone is
    # shallow; this one read it raw and skipped when it could not. In CI — `actions/checkout@v4`,
    # depth 1 — that meant the drift-size guard NEVER RAN, and a skip reads like a decision somebody
    # took rather than a guard that could not reach its evidence.
    # ★ SCOPED BY THE PROPERTY, NOT BY A LIST (`paper-hardening` §8b.2): every site here that needs
    # a recorded revision now goes through `_commit_is_present` first, so a site added later fails
    # loudly instead of inheriting the raw call. The skip below is kept for the ONE case it should
    # cover — a revision that genuinely cannot be produced even after a targeted fetch — and it now
    # says which of those two things happened.
    if not _commit_is_present(rev):
        pytest.skip(f"the published revision {str(rev)[:12]} cannot be produced by this checkout "
                    "even after a targeted fetch; "
                    "test_the_published_record_is_corroborated_by_git_rather_than_declared owns that")
    shown = subprocess.run(
        ["git", "show", f"{rev}:research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"],
        cwd=REPO, capture_output=True, text=True)
    assert shown.returncode == 0, (
        f"the published revision {str(rev)[:12]} resolves but its archive manifest cannot be read "
        "there. That is a damaged object, not an absent one, and it must not pass as a skip.")
    was = {f["path"]: f["sha256"] for f in json.loads(shown.stdout)["files"]}
    now = {f["path"]: f["sha256"] for f in manifest["files"]}
    changed = sorted(p for p in was if p in now and was[p] != now[p])
    n = len(changed) + len(set(now) - set(was)) + len(set(was) - set(now))

    text = open(CHECKLIST, encoding="utf-8").read()
    section = _open_blocking_section(text)
    #: ⛔⛔ THE LOOKAROUNDS MUST EXCLUDE LETTERS, NOT ONLY DIGITS — MEASURED 2026-08-30, HOURS AFTER
    #: THIS GUARD WAS WRITTEN, AND IT WAS ALREADY HIDING A STALE NUMBER. The first version used
    #: `(?<![\d.])` / `(?![\d.])`, so the `23` inside the git sha `c84bc23d251a` — which the section
    #: quotes as the published revision — satisfied a search for a drift of 23 while the prose said
    #: 22. A hex sha is 40 characters of digit pairs, and the section quotes one BY CONSTRUCTION, so
    #: this guard had a ~1-in-3 chance of passing on any number it was given. ★ That is the exact
    #: failure it was written to catch — an acknowledgement that reads right and measures nothing —
    #: reproduced inside the acknowledgement's own instrument, one commit later.
    assert re.search(rf"(?<![0-9A-Za-z.]){n}(?![0-9A-Za-z.])", section), (
        f"the deposited set has changed in {n} path(s) since the published record's revision "
        f"{str(rev)[:12]}, and '{_OPEN_HEADING}' never states that number.\n\n"
        f"changed: {', '.join(os.path.basename(c) for c in changed[:6])}"
        f"{' …' if len(changed) > 6 else ''}\n\n"
        "An acknowledgement that does not name the size of what it acknowledges is a sentence, not a "
        "reading — it goes stale the next time a deposited file moves and nothing notices. Re-measure "
        "and state the current figure.")


def test_the_drift_figure_is_not_satisfied_by_a_digit_pair_inside_a_sha():
    """⛔⛔ THE HOLE THAT MADE THE GUARD ABOVE VACUOUS, DRIVEN RATHER THAN DESCRIBED.

    Measured 2026-08-30, hours after that guard was written and already hiding a stale number: the
    section it reads quotes the published revision as a git sha BY CONSTRUCTION, a sha is 40
    characters of digit pairs, and digit-only lookarounds let any of them stand in for the figure.
    `c84bc23d251a` satisfied a search for a drift of 23 while the prose said 22.

    ★ SO BOTH DIRECTIONS ARE ASSERTED. A number that appears only inside a sha must NOT count, and a
    number stated in prose must. A guard whose safety rests on a comment is one edit from vacuous.
    """
    n = 23
    pattern = rf"(?<![0-9A-Za-z.]){n}(?![0-9A-Za-z.])"
    sha_only = "the published record's `git_revision` (`c84bc23d251a`, 483 paths)."
    stated = "returns **23 differences: 20 changed, 2 added, 1 removed.**"
    assert not re.search(pattern, sha_only), (
        "a digit pair inside a git sha satisfies the drift figure, so the guard above reports green "
        "on any acknowledgement that quotes a revision — which every one of them does")
    assert re.search(pattern, stated), (
        "the pattern no longer matches the figure stated in prose, so tightening it made the guard "
        "unsatisfiable rather than correct")


def test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared():
    """⛔⛔ A POPULATED FIELD IS NOT A MEASURED ONE, AND THIS ONE COULD BE DECLARED BY HAND.

    Round 16 seat 5: `test_a_pending_draft_still_matches_the_tree_it_was_built_from` returns early
    when `pending.uploaded_manifest_digest` equals the manifest's digest now. **Copying today's
    digest into that field satisfies it** — one JSON edit — after which the checklist's "re-run the
    deposit first" line can be deleted with nothing firing, and the guard whose docstring reads
    "PUBLISHING A DRAFT THAT IS ALREADY BEHIND WOULD FREEZE THE SAME DEFECT AGAIN" has been
    satisfied by an assertion that it would not.

    ★ THE FIELD IS MADE OBSERVABLE BY THE ONE WITNESS THAT CANNOT BE BACK-DATED: git. The state also
    records `uploaded_at_git_revision`, so the digest it claims to have uploaded must be the digest
    the manifest ACTUALLY HELD at that commit. Copying today's value cannot satisfy that, because
    the manifest at an older revision holds an older digest — verified offline, no network, no
    Zenodo call.

    ⚠ This does not prove the bytes reached Zenodo; nothing available here can. It proves the
    recorded digest is a fact about this repository's history rather than a number someone typed.
    """
    state = _json(STATE, "what was deposited")
    pending = state.get("pending")
    if not pending:
        pytest.skip("nothing is drafted, so there is no upload digest to corroborate "
                    "— SKIP IS DELIBERATE: the pending block is absent by design between deposits")

    rev = pending.get("uploaded_at_git_revision")
    recorded = pending.get("uploaded_manifest_digest")
    assert rev and recorded, (
        f"the pending version {pending['doi']} records "
        f"{'no git revision' if not rev else 'no uploaded digest'}, so what it holds cannot be "
        "checked against anything. Both are written by the deposit workflow; if one is missing the "
        "draft's contents are unknown and it must not be published.")

    # ⛔⛔ ONE OF A PAIR, AND THE SECOND HALF WAS LEFT RAW FOR HOURS AFTER THE FIRST WAS FIXED.
    # `_commit_is_present` was written this morning for the PUBLISHED corroboration below, because
    # `actions/checkout@v4` clones at depth 1 and every recorded revision looks fabricated to a
    # one-commit clone. This sibling — the same check, on the PENDING block — kept its raw
    # `cat-file` and went red on `main` at the very next push, reporting that 850edb3358ba "is not
    # a commit in this repository" while that sha sits on origin/main.
    # ⚠ `paper-hardening` §6 is the section about exactly this class, and it was read the same day:
    # "whenever a deliverable gains a second form, enumerate every instrument that names the first
    # and ask whether it should name both." The pair here is not two documents, it is two BLOCKS of
    # one state file — published and pending — and the fix went to one of them.
    assert _commit_is_present(rev), (
        f"deposit-state.json records the draft as built at {rev[:12]}, which this checkout cannot "
        "produce even after a targeted fetch. A revision nobody can resolve cannot corroborate "
        "anything.")

    shown = subprocess.run(
        ["git", "show", f"{rev}:research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"],
        cwd=REPO, capture_output=True, text=True)
    assert shown.returncode == 0, (
        f"the archive manifest cannot be read at {rev[:12]}, so the recorded upload digest has no "
        "witness. Do not publish the draft until the revision it was built from is resolvable.")
    at_revision = json.loads(shown.stdout).get("archive_content_digest")
    assert at_revision == recorded, (
        f"deposit-state.json says the draft was built at {rev[:12]} with digest {recorded[:12]}, "
        f"but the manifest AT that revision recorded {str(at_revision)[:12]}.\n\n"
        "Those disagree, so the digest was not taken from that build — the usual cause is a value "
        "copied in by hand to make a staleness check pass. Re-run the deposit and let the workflow "
        "write both fields, and do not publish the draft in the meantime.")


def test_the_published_record_is_corroborated_by_git_rather_than_declared():
    """⛔⛔ THE SAME WITNESS AS THE PENDING BLOCK, ON THE BLOCK THAT OUTLIVES IT — AND IT WAS MISSING
    WHILE A SENTENCE CLAIMED IT WAS HERE.

    ⚠ Measured by round 21's regression seat, 2026-08-30. `deposit-state.json` `published._provenance`
    ended: "git_revision is the commit at which the manifest held that digest, corroborated out of
    git by tests/test_the_deposit_the_papers_cite_is_current.py rather than declared here." This file
    read `published` for exactly two fields — `doi` and `manifest_digest` — and touched
    `git_revision` nowhere. Its one git-corroboration test is scoped to `pending` and SKIPS when
    nothing is drafted, which is the steady state between deposits. So the field was corroborated by
    nothing, in a sentence asserting the opposite, written in the same commit that moved the block.

    ★ THAT IS THE "RECORDED IS NOT ENFORCED" SHAPE THIS REPOSITORY HAS ALREADY PAID FOR TWICE
    (`subagent_width`, and the census lane wired to a name nothing passed). The remedy is never to
    soften the sentence — it is to make the sentence true, which costs one test.

    ⚠ WHAT THIS PROVES AND WHAT IT DOES NOT. It proves `published.git_revision` names a commit in
    this repository at which the archive manifest recorded `published.manifest_digest` — i.e. that
    the pair is a fact about this history rather than two numbers typed together. It does NOT prove
    those bytes reached Zenodo; nothing available offline can, and `_provenance` cites the
    `record=verify` read-back for that half.
    """
    state = _json(STATE, "what was deposited")
    pub = state["published"]
    rev, recorded = pub.get("git_revision"), pub.get("manifest_digest")
    assert rev and recorded, (
        "deposit-state.json `published` records "
        f"{'no git revision' if not rev else 'no manifest digest'}. Both are needed for the record "
        "to be checkable at all, and `published` is the block every gate reads.")

    assert _commit_is_present(rev), (
        f"`published.git_revision` is {rev[:12]}, which is not a commit in this repository, and a "
        "targeted fetch of that exact sha did not produce it either. A revision nobody can resolve "
        "corroborates nothing — and a reader who follows the DOI is told this is the tree the "
        "archive was hashed from.")

    shown = subprocess.run(
        ["git", "show", f"{rev}:research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"],
        cwd=REPO, capture_output=True, text=True)
    assert shown.returncode == 0, (
        f"the archive manifest cannot be read at {rev[:12]}, so the published digest has no witness.")
    at_revision = json.loads(shown.stdout).get("archive_content_digest")
    assert at_revision == recorded, (
        f"deposit-state.json says the published version was built at {rev[:12]} with digest "
        f"{recorded[:12]}, but the manifest AT that revision recorded {str(at_revision)[:12]}.\n\n"
        "Those disagree, so one of the two was typed rather than taken from the build. The usual "
        "cause is moving `pending` into `published` by hand and carrying the wrong field across.")


def test_a_pending_draft_still_matches_the_tree_it_was_built_from():
    """⛔ PUBLISHING A DRAFT THAT IS ALREADY BEHIND WOULD FREEZE THE SAME DEFECT AGAIN.

    The draft on Zenodo holds one specific build. Publishing is irreversible, so if the repository
    moves after the upload and nobody re-runs the deposit, the click freezes an archive that is
    already stale — which is exactly the defect this file exists to prevent, one step earlier in the
    process and with the same irreversibility.

    ⚠ THIS CANNOT SEE ZENODO, and does not claim to. It compares the digest recorded at upload time
    against the manifest's digest now. That answers the question that actually matters — "has the
    tree moved since the draft was built?" — without a network call, which is what makes it a gate
    rather than a note.
    """
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    pending = state.get("pending")
    if not pending:
        return
    recorded = pending.get("uploaded_manifest_digest")
    assert recorded, (
        f"deposit-state.json records a pending version ({pending['doi']}) without the digest of "
        "what was uploaded into it, so nothing can tell whether the draft still matches this tree")
    if recorded == manifest.get("archive_content_digest"):
        return

    # ⛔⛔ A STALE DRAFT BETWEEN COMMITS IS NORMAL, AND THE FIRST VERSION OF THIS ASSERTION MADE IT
    # A HARD FAILURE — which turned every commit that touches the archive into a red gate with a
    # CIRCULAR dependency: refreshing the draft uploads from the pushed branch, and pushing needs
    # this gate green. It went red on its own first full run, three commits after being written.
    # ⚠ A GATE THAT IS RED FOR WEEKS IS A GATE THAT GETS SWITCHED OFF, and this repository has the
    # scars. The question worth asking is not "is the draft current?" — between commits it is not,
    # and should not have to be. It is "will the person about to publish be TOLD to refresh it?",
    # because that is the moment the staleness would be frozen.
    text = open(CHECKLIST, encoding="utf-8").read()
    # ⛔⛔ ANYWHERE IN THE FILE IS NOT THE SAME AS IN THE BLOCKING ITEM (round 16 seat 5, M16). This
    # searched the whole checklist, so the refresh instruction could be demoted to a "superseded,
    # retained" note further down while the blocking item itself said publish as it stands — every
    # phrase still present, the gate still green, and the person about to perform an IRREVERSIBLE
    # publish reading the opposite of what this guard believes they were told. Same shape as M10,
    # in the neighbouring assertion.
    section = _open_blocking_section(text)
    # ⛔⛔ AND A REPORT THAT THE REFRESH ALREADY HAPPENED IS NOT AN INSTRUCTION TO PERFORM IT — the
    # pattern here used to be `re-?run the deposit|new_version=false|refresh the draft`, and at
    # b53290b37e71 it was satisfied by the blocking item's own sentence "Dispatched
    # `deposit-zenodo.yml` with `new_version=false` at `f6e313d98`", i.e. by the claim that the
    # draft was ALREADY CURRENT. The tree had moved one commit later (round 19's cover-letter
    # repair), the draft was stale, and this guard — the one instrument whose whole job is to warn
    # the publisher — read the stale-denying sentence as its own warning and went green.
    # ⚠ Found by the round-20 `citations-and-instruments` seat. It is the same shape as the M16
    # defect above: the phrase was present, in the right section, and meant the opposite.
    # ★ SO THE VERB MUST BE IMPERATIVE. `\b` after the stem does the work: "Dispatched" and
    # "Refreshed" are not matched by `\bdispatch\b` / `\brefresh\b`, in any case, because the
    # following character is a word character and there is no boundary there.
    assert re.search(r"\b(?:dispatch|refresh|re-?run)\b[^\n]{0,200}?"
                     r"(?:deposit-zenodo\.yml|new_version=false|draft)", section, re.I), (
        f"the draft {pending['doi']} was built at archive digest {recorded[:16]}… and this tree is "
        f"at {str(manifest.get('archive_content_digest'))[:16]}…, which is expected between "
        "commits — but nothing in the preprint checklist tells whoever publishes it to refresh the "
        "draft first.\n\nPublishing a stale draft freezes an archive that is already behind, which "
        "is the defect this whole file exists to prevent, one step later and irreversibly. Add the "
        "instruction to the blocking item: dispatch deposit-zenodo.yml with new_version=false "
        "(it UPDATES the draft rather than making a second one), then update "
        "`uploaded_manifest_digest` here.")
