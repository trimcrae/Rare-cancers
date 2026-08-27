"""How many clauses the publish bar has is `len(CLAUSES)`. Nothing may say it in words.

⛔⛔ WHY THIS EXISTS, FOUND 2026-08-27. `clause_7_readable_enough_to_review` landed in commit
648114fb2 at 12:41 PM ET. The count "six" was then wrong in NINE places at once:

    research/autonomy/publish_bar.py                        (docstring + a section header)
    research/autonomy/record_bar_evidence.py
    research/autonomy/publication-authority.json            ← the record of what trimcrae GRANTED
    CLAUDE.md §3
    AGENTS.md
    research/manuscripts/program/emc-autonomy-architecture.md   (four sites)

⭐ NOTHING WAS UNDER-ENFORCED. `evaluate()` derives `n_clauses` from `CLAUSES` at runtime, so the
seventh clause was checked from the moment it existed, and a seventh clause makes the bar STRICTER —
the safe direction, and not something `amendment_guard` forbids. What was wrong is narrower and
worse: **the grant record described a bar with one fewer clause than the code applies.** trimcrae's
authority was given on 2026-08-26 against "the six clauses"; the code changed under that sentence
the next day. CLAUDE.md rule 1 — "a total is DERIVED, never typed" — in the one file where an
outside reader has least ability to check the code themselves.

⛔ AND NO GATE SAW IT. `lint_consistency` governs pinned FIGURES in manuscript targets; this number
lives in Python, in JSON, in two standing-rules files and in an architecture doc. It was found by a
survey seat that had opened `publish_bar.py` to answer an unrelated question — i.e. by luck, which
is the same finding CLAUDE.md §1 records about `subagent_width` governing nothing for a fortnight.

★ THE RULE THIS PINS: a count adjacent to the word "clause", on a line that is talking about the
bar, must equal `len(CLAUSES)` — or must be marked as superseded, because this repository never
silently drops a correction (rule 1.2). The markers are READ from `pinned-figures.json` rather than
restated here, for exactly the reason this file exists.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))

import publish_bar  # noqa: E402

PINNED = os.path.join(REPO, "research", "manuscripts", "pinned-figures.json")

WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
         "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

#: ⛔ A TOTAL, NOT A SUBSET, AND THE DEFINITE ARTICLE IS WHAT SEPARATES THEM. "the six clauses" and
#: "all six clauses" and "three of THE SIX clauses" all assert how many there are; "three clauses
#: read a committed artifact" counts a subset and is true at any bar size. So the count must be
#: introduced by `the`/`all`/`every`, which is also what keeps "§6.1 clauses" from reading as "1
#: clauses" — a section number is not preceded by an article.
#: ⚠ THE FIRST VERSION OF THIS PATTERN MATCHED BARE ADJACENCY AND FLAGGED 19 TRUE SENTENCES across
#: the manuscripts, the skills and two unrelated test files — grammatical clauses, falsifier
#: clauses, template clauses. A linter that flags true statements gets turned off, which is worse
#: than no linter (`lint_claims.py`'s founding lesson), so it was tightened rather than shipped.
COUNT = re.compile(
    r"\b(?:the|all|all of the|every one of the)\s+(" + "|".join(WORDS) + r"|\d{1,2})\s+clauses?\b",
    re.I)

#: …and only in a file that names this bar by identifier. "the bar" and "aiXiv" were in the first
#: version and are far too common in this repository to narrow anything.
NAMES_THE_BAR = re.compile(r"publish_bar|publication-authority|§6\.1", re.I)

#: How close the count must sit to that identifier. Prose wraps, so the window spans the line before
#: and after — AGENTS.md's copy read "clears EVERY clause of\n[`publish_bar.py`]" across a break.
NEAR = 80


def _near_the_identifier(lines: list[str], i: int, m: re.Match) -> bool:
    before = "\n".join(lines[max(0, i - 1):i])
    joined = before + ("\n" if before else "") + "\n".join(lines[i:i + 2])
    at = len(before) + (1 if before else 0) + m.start()
    return any(abs(hit.start() - at) <= NEAR for hit in NAMES_THE_BAR.finditer(joined))



@pytest.fixture(scope="module")
def markers() -> list[str]:
    with open(PINNED, encoding="utf-8") as fh:
        return [m.lower() for m in json.load(fh)["supersession_markers"]]


def _tracked_text_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    keep = (".md", ".py", ".json", ".jsonl", ".sh", ".yml", ".yaml", ".txt")
    return [p for p in out.split("\0") if p and p.endswith(keep)]


def _offences(markers: list[str]) -> list[tuple[str, int, str, int]]:
    """(path, line number, line, the count it typed) for every unmarked disagreement.

    ⛔ PROXIMITY, NOT MERE CO-OCCURRENCE, AND THIS IS WHERE THE HONEST LIMIT OF THE GUARD IS. "the
    three clauses still open are the SHA-PINNED ones" and "the three clauses gating hardening,
    testing and independent review" are both TRUE subset statements sitting in files that also name
    the bar — a file-level scope flagged both. So a count only counts as a claim about the bar's
    SIZE when it sits within `NEAR` characters of the bar's own identifier.

    ⚠ WHAT THAT MISSES, SAID OUT LOUD RATHER THAN LEFT TO BE DISCOVERED: a stale total in a comment
    that never names `publish_bar.py` or §6.1 is invisible here. One existed when this was written
    (`systems/tests/test_autonomy_publish_bar.py`, "THREE OF THE SIX CLAUSES WERE SELF-REPORTS") and
    was fixed by hand in the same commit. This guard is a net under the nine sites that DID carry
    the number, not a proof that no tenth exists.
    """
    n = len(publish_bar.CLAUSES)
    bad = []
    for rel in _tracked_text_files():
        path = os.path.join(REPO, rel)
        try:
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        # ⭐ The file set is DERIVED, not hand-kept: any file that names the bar is in scope, so a
        # tenth copy of the count in a file nobody thought of is caught on the commit that adds it.
        if not NAMES_THE_BAR.search(body):
            continue
        # ⛔ Dated, immutable records of what a past cycle found are not restatements of a current
        # total, and rewriting one to keep a linter quiet would be falsifying the record.
        if rel.startswith("research/autonomy/receipts/") or rel.endswith("amendments.jsonl"):
            continue
        own_file = rel == "research/autonomy/publish_bar.py"
        lines = body.split("\n")
        for i, line in enumerate(lines):
            for m in COUNT.finditer(line):
                tok = m.group(1).lower()
                said = WORDS.get(tok, None)
                if said is None:
                    said = int(tok)
                if said == n:
                    continue
                if not own_file and not _near_the_identifier(lines, i, m):
                    continue
                # Rule 1.2: a superseded value may stand where it is marked as superseded. The
                # window matches lint_consistency's — this line, two above, one below — because
                # prose wraps mid-sentence.
                window = " ".join(lines[max(0, i - 2):i + 2]).lower()
                if any(mk in window for mk in markers):
                    continue
                bad.append((rel, i + 1, line.strip()[:120], said))
    return bad


def test_no_file_types_a_clause_count_that_disagrees_with_the_code(markers):
    n = len(publish_bar.CLAUSES)
    bad = _offences(markers)
    assert not bad, (
        f"publish_bar.CLAUSES has {n} clauses, and these lines say otherwise without marking the "
        f"old value as superseded:\n" + "\n".join(
            f"  {p}:{ln}  (says {said})  {text}" for p, ln, text, said in bad))


def test_evaluate_derives_the_count_rather_than_carrying_one(markers):
    """⭐ THE REASON THE STALE PROSE WAS HARMLESS TO ENFORCEMENT, pinned so it stays that way. If a
    literal ever replaces this derivation, the prose and the code can disagree in the direction that
    DOES under-enforce — a clause that exists and is not counted."""
    src = open(publish_bar.__file__, encoding="utf-8").read()
    assert "len(CLAUSES)" in src, (
        "publish_bar.py no longer derives its clause count from CLAUSES — a typed n_clauses can "
        "silently stop counting a clause that exists")


def test_the_guard_would_catch_the_2026_08_27_wording(markers, tmp_path, monkeypatch):
    """⚠ THE POSITIVE CONTROL. Without it this file passes just as well on a broken matcher — which
    is the failure mode it was written to catch in something else."""
    n = len(publish_bar.CLAUSES)
    wrong = [w for w, v in WORDS.items() if v == n - 1]
    assert wrong, "no word for one-less-than-the-clause-count; extend WORDS"
    line = f"the bar is the {wrong[0]} clauses in research/autonomy/publish_bar.py"
    assert NAMES_THE_BAR.search(line) and COUNT.search(line), (
        "the matcher no longer recognises the exact sentence that was wrong on 2026-08-27")
    assert WORDS[COUNT.search(line).group(1).lower()] != n


def test_a_subset_count_is_not_an_offence(markers):
    """`record_bar_evidence.py` says three of the bar's clauses read a committed artifact. That is a
    true subset, not a total, and a guard that flagged it would be turned off within a week."""
    line = "`publish_bar.py` is the publication permission. Three of its clauses read an artifact"
    assert NAMES_THE_BAR.search(line)
    assert not COUNT.search(line), "a subset phrasing is being read as a total"
