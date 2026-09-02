"""⛔⛔ A CAP NOTHING READS IS NOT A CAP, AND A COUNT FROM A LOWER BOUND IS NOT A COUNT.

⚠ MEASURED 2026-09-02. `publication-authority.json` has declared
`scope.max_versions_per_paper: 3` since the standing grant was written on 2026-08-26, with the
measurement beside it: ELEVEN versions of `aixiv.260822.000005` never moved its rating above 6 and
it trended DOWN as the paper improved, so an uncapped loop would put ten near-identical versions
under trimcrae's ORCID. `grep -rn max_versions_per_paper` over the whole repository returned three
hits — the JSON that defines it, one line of architecture prose, and one test asserting it is
`>= 1`. **No code read it.** `authority_permits('PUB-VACCINE-PATH', 'aixiv', 'new_version')`
returned `ok=True` for that eleven-version paper.

★ THIRD INSTANCE OF ONE SHAPE. `subagent_width` was a governed number `grep` proved no code read
(CLAUDE.md §1); `autonomy-state.json`'s `_ENFORCEMENT_IS_NOT_THIS_FIELD` records this cap as the
second; `gpu_spend_prohibited` is the third. RECORDED IS NOT ENFORCED.

⛔⛔ AND THE COUNT IS THE HARD HALF, WHICH IS WHY HALF THIS FILE IS ABOUT IT. There is no machine
record of any aiXiv posting anywhere in `systems/graph/` — `PUB-VACCINE-PATH` is `state: drafted`
with no `posted` block while eleven of its versions are live. The only trace on disk is the
filenames under `research/literature/aixiv-reviews/`, and a review file exists only where a `fetch`
RAN. Counting those is a LOWER BOUND, and a lower bound used as a cap check reads as enforcement
while silently permitting. So the register is written by the posting act, and every way of failing
to establish the count REFUSES.

WHAT EACH GROUP HOLDS DOWN
  1-6    the cap itself: refused at and above it, permitted below, and unreadable-cap fails closed.
  7-13   the register's own integrity — a malformed row, an unknown source, a fabricated posting
         time on a backfilled row, an ambiguous attribution, and an absent file are each a refusal
         rather than a smaller number.
  14-17  the reconciliation, in the one direction that is sound: a review file with no row proves
         the register incomplete; the reverse is NEVER used to raise a count.
  18-20  the committed state: the backfill matches the review files, every backfilled row is marked
         and dateless, and the live cap check answers what it should for the real papers.
  21-23  clauses 3 and 4 read at the pinned sha, and `_tree_at` is a no-op when the sha IS the
         working tree — the property that makes this change safe rather than merely correct.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUT))
sys.path.insert(0, AUT)

import posting_register as PR   # noqa: E402
import publish_bar as PB        # noqa: E402


def _row(pub_id="PUB-X", aixiv_id="aixiv.260822.000005", version="1.0", act="submit",
         source=PR.RECORDED, posted="2026-08-22T10:00:00Z", **over):
    row = {"pub_id": pub_id, "aixiv_id": aixiv_id, "version_label": version, "act": act,
           "source": source, "posted_utc": posted, "recorded_utc": "2026-09-02T18:00:00Z"}
    row.update(over)
    return row


def _register(tmp_path, rows, name="aixiv-postings.jsonl"):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""), encoding="utf-8")
    return p


def _reviews(tmp_path, names):
    d = tmp_path / "reviews"
    d.mkdir(exist_ok=True)
    for n in names:
        (d / n).write_text('{"code": 200, "review_list": []}', encoding="utf-8")
    return d


@pytest.fixture
def authority(tmp_path, monkeypatch):
    """The real authority file, with the register and review dir redirected into a tmp tree."""
    def _use(rows, review_names, cap=3):
        reg = _register(tmp_path, rows)
        rev = _reviews(tmp_path, review_names)
        monkeypatch.setattr(PR, "REGISTER", reg)
        monkeypatch.setattr(PR, "REVIEWS_DIR", rev)
        real, err = PB._read_json(PB.AUTHORITY_FILE)
        assert real is not None, err
        doc = copy.deepcopy(real)
        if cap is not ...:
            doc["aixiv"]["scope"]["max_versions_per_paper"] = cap
        path = tmp_path / "publication-authority.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        monkeypatch.setattr(PB, "AUTHORITY_FILE", path)
        return path
    return _use


# ── 1-6 · the cap ────────────────────────────────────────────────────────────────────────────────

def test_the_cap_refuses_a_new_version_at_the_cap(authority):
    """⛔ THE DEFECT ITSELF, AT ITS BOUNDARY. Three recorded versions against a cap of three."""
    authority([_row(version=v, act="submit" if v == "1.0" else "new_version")
               for v in ("1.0", "1.1", "1.2")],
              ["aixiv.260822.000005-1.0-reviews.json", "aixiv.260822.000005-1.1-reviews.json",
               "aixiv.260822.000005-1.2-reviews.json"])
    r = PB.authority_permits("PUB-X", "aixiv", "new_version")
    assert r["ok"] is False
    assert "3 posted version(s)" in r["why"] and "= 3" in r["why"]


def test_the_cap_refuses_a_submit_too(authority):
    """The cap counts VERSIONS OF A PAPER. A second `submit` adds one exactly as `new_version` does."""
    authority([_row(version=v, act="submit" if v == "1.0" else "new_version")
               for v in ("1.0", "1.1", "1.2")],
              ["aixiv.260822.000005-1.0-reviews.json", "aixiv.260822.000005-1.1-reviews.json",
               "aixiv.260822.000005-1.2-reviews.json"])
    assert PB.authority_permits("PUB-X", "aixiv", "submit")["ok"] is False


def test_below_the_cap_is_still_permitted(authority):
    """⛔ THE GUARD MUST NOT BECOME A BLANKET REFUSAL. A fix that blocks everything is not a fix."""
    authority([_row(version="1.0")], ["aixiv.260822.000005-1.0-reviews.json"])
    r = PB.authority_permits("PUB-X", "aixiv", "new_version")
    assert r["ok"] is True and "1 of 3" in r["why"]


def test_a_paper_with_no_postings_is_unaffected(authority):
    """A first post of a never-posted paper is what the grant is FOR — count 0, cap 3."""
    authority([_row(version="1.0")], ["aixiv.260822.000005-1.0-reviews.json"])
    assert PB.authority_permits("PUB-NEVER-POSTED", "aixiv", "submit")["ok"] is True


@pytest.mark.parametrize("cap", [None, 0, -1, "3", 3.5, True, [3]])
def test_an_unreadable_cap_is_a_refusal_not_an_absent_limit(authority, cap):
    """⛔ FAIL CLOSED. A cap this function cannot read is not permission (CLAUDE.md §4)."""
    authority([_row(version="1.0")], ["aixiv.260822.000005-1.0-reviews.json"], cap=cap)
    r = PB.authority_permits("PUB-X", "aixiv", "new_version")
    assert r["ok"] is False and "max_versions_per_paper" in r["why"]


def test_the_exclusion_is_still_checked_before_the_cap(authority):
    """PUB-ASO's exclusion is trimcrae's and the cap must not displace or dilute it."""
    authority([], [])
    r = PB.authority_permits("PUB-ASO", "aixiv", "new_version")
    assert r["ok"] is False and "excluded from the aiXiv grant" in r["why"]


# ── 7-13 · the register cannot be trusted quietly ────────────────────────────────────────────────

def test_an_absent_register_refuses_rather_than_counting_zero(authority, tmp_path, monkeypatch):
    """⛔⛔ THE SENTENCE THIS WHOLE MODULE TURNS ON. An absent record is not a record of zero."""
    monkeypatch.setattr(PR, "REGISTER", tmp_path / "does-not-exist.jsonl")
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, []))
    out = PR.versions_posted("PUB-X")
    assert out["ok"] is False and out["count"] is None
    assert "absent" in out["why"]


def test_a_malformed_line_is_a_problem_not_a_skipped_line(authority, tmp_path, monkeypatch):
    p = tmp_path / "aixiv-postings.jsonl"
    p.write_text(json.dumps(_row(version="1.0")) + "\nnot json at all\n", encoding="utf-8")
    monkeypatch.setattr(PR, "REGISTER", p)
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


@pytest.mark.parametrize("field", PR.REQUIRED_FIELDS)
def test_a_row_missing_any_required_field_refuses(tmp_path, monkeypatch, field):
    row = _row(version="1.0")
    row[field] = ""
    monkeypatch.setattr(PR, "REGISTER", _register(tmp_path, [row]))
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


@pytest.mark.parametrize("source", ["", "guessed", "probably", "recorded", None])
def test_an_unknown_source_refuses(tmp_path, monkeypatch, source):
    """⛔ The two sources carry different weight and a third would collapse the distinction."""
    monkeypatch.setattr(PR, "REGISTER", _register(tmp_path, [_row(version="1.0", source=source)]))
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


def test_a_backfilled_row_may_not_carry_a_posting_time(tmp_path, monkeypatch):
    """⛔ NOTHING ON DISK RECORDS WHEN A VERSION WAS POSTED. A review file records when the REVIEW
    was fetched. A plausible date here is a fabricated reading, which CLAUDE.md §4 calls more
    dangerous than an empty one — and it would let a backfilled row pass for a recorded one."""
    monkeypatch.setattr(PR, "REGISTER", _register(
        tmp_path, [_row(version="1.0", source=PR.BACKFILLED, posted="2026-08-22T10:00:00Z")]))
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


@pytest.mark.parametrize("posted", [None, "", "tuesday", "2026-08-22", "2026-08-22T10:00:00",
                                    "2026-08-22T10:00:00+02:00"])
def test_a_recorded_row_without_a_readable_posting_time_refuses(tmp_path, monkeypatch, posted):
    monkeypatch.setattr(PR, "REGISTER", _register(tmp_path, [_row(version="1.0", posted=posted)]))
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


def test_one_version_attributed_to_two_papers_refuses(tmp_path, monkeypatch):
    """⛔ An ambiguous attribution makes every count on that aiXiv id unreliable, in both directions."""
    monkeypatch.setattr(PR, "REGISTER", _register(tmp_path, [
        _row(pub_id="PUB-X", version="1.0"), _row(pub_id="PUB-Y", version="1.0")]))
    monkeypatch.setattr(PR, "REVIEWS_DIR", _reviews(tmp_path, ["aixiv.260822.000005-1.0-reviews.json"]))
    assert PR.versions_posted("PUB-X")["ok"] is False


# ── 14-17 · reconciliation, one direction only ───────────────────────────────────────────────────

def test_a_review_file_with_no_row_proves_the_register_incomplete(authority):
    """⛔⛔ THE FORWARD-LOOKING GUARD, AND THE REASON BACKFILLING DOES NOT MAKE IT VACUOUS. From
    here on, a version posted without `record()` produces a review file the next fetch cycle whose
    (aixiv_id, version) matches no row — and every aiXiv act is refused until it is appended."""
    authority([_row(version="1.0")],
              ["aixiv.260822.000005-1.0-reviews.json", "aixiv.260822.000005-1.1-reviews.json"])
    r = PB.authority_permits("PUB-X", "aixiv", "new_version")
    assert r["ok"] is False
    assert "cannot be established" in r["why"] and "1.1" in r["why"]


def test_the_lower_bound_is_never_used_to_RAISE_a_count(authority):
    """⛔⛔ THE DESIGN DECISION, PINNED. Eleven review files against one recorded row must REFUSE,
    never silently answer 11 — counting from review filenames cannot see a post nobody fetched, so
    'take the larger' is the same silent under-count one layer down. The refusal is the honest
    answer and it costs one appended line to clear."""
    authority([_row(version="1.0")],
              [f"aixiv.260822.000005-1.{i}-reviews.json" for i in range(11)])
    out = PR.versions_posted("PUB-X")
    assert out["ok"] is False and out["count"] is None, (
        "an incomplete register answered with a number instead of refusing")


def test_an_unparseable_review_filename_refuses_rather_than_being_ignored(authority):
    """An unreadable filename is not an absent posting."""
    authority([_row(version="1.0")],
              ["aixiv.260822.000005-1.0-reviews.json", "something-else.json"])
    assert PB.authority_permits("PUB-X", "aixiv", "new_version")["ok"] is False


def test_a_register_that_covers_every_review_file_reconciles(authority):
    authority([_row(version="1.0"), _row(version="1.1", act="new_version")],
              ["aixiv.260822.000005-1.0-reviews.json", "aixiv.260822.000005-1.1-reviews.json"])
    assert PR.reconcile()["ok"] is True
    assert PR.versions_posted("PUB-X") == {"ok": True, "count": 2,
                                           "why": PR.versions_posted("PUB-X")["why"]}


# ── 18-20 · the committed state ──────────────────────────────────────────────────────────────────

def test_the_committed_register_reconciles_with_the_review_files_on_disk():
    """⛔ THE GATE ON THE REAL FILES. If this reddens, a version was posted and not recorded."""
    state = PR.reconcile()
    assert state["ok"], "; ".join(state["problems"][:6])


def test_every_backfilled_row_is_marked_and_dateless():
    """⛔ AN OBSERVATION IS NOT A RECORD, AND THE FILE MUST SAY WHICH IT IS ON EVERY ROW."""
    rows, problems = PR.load()
    assert not problems, problems
    assert rows, "the register is empty — this test would then be measuring nothing"
    for row in rows:
        assert row["source"] in PR.SOURCES
        if row["source"] == PR.BACKFILLED:
            assert row.get("posted_utc") is None
            assert row.get("evidence"), f"{row['aixiv_id']} v{row['version_label']} names no evidence"


def test_the_live_cap_check_answers_for_the_real_papers():
    """⛔ THE END-TO-END READING, ON THE COMMITTED ARTIFACTS, AND IT IS THE POINT OF THE CHANGE.

    ⚠ Before this: `ok=True` for PUB-VACCINE-PATH `new_version` at eleven versions against a cap of
    three. PUB-FUSION-OUTPUT is the control — one version, still permitted — so this asserts a cap
    rather than a blanket refusal.
    """
    over = PB.authority_permits("PUB-VACCINE-PATH", "aixiv", "new_version")
    assert over["ok"] is False and "11 posted version(s)" in over["why"]
    under = PB.authority_permits("PUB-FUSION-OUTPUT", "aixiv", "new_version")
    assert under["ok"] is True, under["why"]


# ── 21-23 · clauses 3 and 4 read at the pinned sha ───────────────────────────────────────────────

def _head():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=REPO).stdout.strip()


def _clean():
    return not subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                              cwd=REPO).stdout.strip()


def test_tree_at_takes_the_fast_path_EXACTLY_when_the_working_tree_IS_the_sha():
    """⭐ THE PROPERTY THAT MAKES THIS CHANGE A NO-OP IN THE NORMAL CASE, ASSERTED IN BOTH STATES.

    Clean tree at HEAD: `REPO` itself, because materialising would quietly drop clause 4's view of
    UNTRACKED files — `lint_citations` passes `--others` deliberately so a fabricated citation in a
    not-yet-`git add`ed draft is caught before the commit, and losing that would be a loosening
    dressed as a correctness fix.
    Dirty tree: NOT `REPO`, because then the working tree is not the sha and reading it would be the
    original defect. ⛔ Written this way rather than as a `skip` on a dirty tree: a test that skips
    in every sandbox and runs only in CI is one nobody sees fail.
    """
    with PB._tree_at(_head()) as (root, err):
        assert err is None, err
        if _clean():
            assert root == PB.REPO, "a clean tree at HEAD IS the sha; materialising it drops --others"
        else:
            assert root != PB.REPO, "a dirty tree is not the sha and must not be read as one"
            assert (root / "research" / "autonomy" / "publish_bar.py").exists()


def test_tree_at_refuses_a_sha_it_cannot_resolve():
    """⛔ FAIL CLOSED: a bar that cannot read what it is grading has not passed it."""
    with PB._tree_at("0" * 40) as (root, err):
        assert root is None and "does not resolve" in err


@pytest.mark.parametrize("clause", [PB.clause_3_claim_ceiling_honoured,
                                    PB.clause_4_identifiers_resolvable])
def test_a_paper_clause_refuses_an_unresolvable_sha_instead_of_reading_the_working_tree(clause):
    """⛔⛔ THE DEFECT, ASSERTED FROM THE OUTSIDE. Before this, clause 3 read `REPO / doc` and
    clause 4 shelled `lint_citations.py` with no arguments, so BOTH returned a verdict about the
    working tree no matter what sha they were handed — including a sha that does not exist."""
    row = clause("PUB-VACCINE-PATH", "0" * 40)
    assert row["verdict"] == PB.UNVERIFIABLE, (
        f"{row['clause']} answered {row['verdict']} for a sha that does not resolve, so it did not "
        "read at the sha at all")


def test_every_clause_that_takes_a_sha_actually_reads_at_it():
    """⛔ ONE OF A PAIR, GENERALISED. The two clauses that ignored `sha` looked exactly like the
    five that honoured it — same signature, same arguments — and nothing asserted the difference.
    Every clause is handed an unresolvable sha; any clause that returns a PASS or a FAIL from it has
    read something other than that commit.
    """
    for fn in PB.CLAUSES:
        row = fn("PUB-VACCINE-PATH", "0" * 40)
        assert row["verdict"] == PB.UNVERIFIABLE, (
            f"{row['clause']} returned {row['verdict']} for a sha that does not exist — it is "
            "grading a tree rather than a commit")
