#!/usr/bin/env python3
"""The publish bar — the six clauses that decide whether a paper may be posted unattended.

⛔⛔ READ THIS FIRST. On 2026-08-26 trimcrae granted a **bar-scoped** standing aiXiv authority
(architecture doc §6.3, decision D1): the loop may post ANY paper that clears this bar, rather than
a named list of papers. **That makes this file the permission.** Every weakness here is a paper
published under his name and ORCID that should not have been.

Two consequences, and they are the whole design:

    1. EVERY CLAUSE IS A BOOLEAN THIS SCRIPT COMPUTES FROM A COMMITTED ARTIFACT.
       A clause the loop grades for itself is not a clause — it is the loop deciding it may publish.

    2. FAIL CLOSED, ALWAYS. A missing artifact, an unreadable file, a crashed linter, a commit
       mismatch — every one of those is a FAILED clause, never a skipped one. CLAUDE.md §4: an
       absent reading is not a reading of absence. `UNVERIFIABLE` and `FAIL` both block the post;
       they are distinguished only so the loop knows whether to go get the evidence or give up.

⛔ AND THE BAR IS NOT SELF-AMENDABLE UNDER PRESSURE. Loosening a clause is a DECLARED change
(architecture §10.4) and may not be made by the cycle the clause just blocked. `amendment_guard.py`
enforces that; this file does not police itself.

USAGE
    python3 research/autonomy/publish_bar.py --paper PUB-ASO --sha <commit>
    python3 research/autonomy/publish_bar.py --paper PUB-ASO --sha <commit> --json
    python3 research/autonomy/publish_bar.py --all --sha <commit>

EXIT CODES
    0  every clause passed AND the authority file permits this act  -> the loop may post
    1  at least one clause failed or could not be verified          -> escalate, do not post
    2  usage error
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
GRAPH = REPO / "systems" / "graph"
MANUSCRIPTS = REPO / "research" / "manuscripts"

AUTHORITY_FILE = HERE / "publication-authority.json"
HARDENING_DIR = HERE / "hardening-state"
PREFLIGHT_DIR = HERE / "preflight-receipts"
SEATS_DIR = HERE / "review-seats"

PASS, FAIL, UNVERIFIABLE = "PASS", "FAIL", "UNVERIFIABLE"


def _clause(key: str, label: str, verdict: str, evidence: str) -> dict:
    return {
        "clause": key,
        "label": label,
        "verdict": verdict,
        "ok": verdict == PASS,
        "evidence": evidence,
    }


def _rel(path: pathlib.Path) -> str:
    """Repo-relative if we can, absolute if we cannot.

    ⚠ `Path.relative_to` RAISES for a path outside the repo, and this helper is only ever called
    from the fail-closed error path — so a naive `relative_to` here turns "the evidence is missing"
    into an uncaught exception, and an uncaught exception in a permission check is not a refusal,
    it is a crash whose meaning depends entirely on the caller. Caught by
    test_a_missing_authority_file_means_no_authority.
    """
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _read_json(path: pathlib.Path):
    """Any failure to read is a failure to verify. Never raises past the caller."""
    try:
        with path.open() as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"absent: {_rel(path)}"
    except Exception as exc:  # unreadable, malformed, permissions
        return None, f"unreadable: {_rel(path)} ({type(exc).__name__})"


def _endpoint(pub_id: str) -> dict | None:
    try:
        for record in json.loads((GRAPH / "publications.json").read_text()):
            if record.get("id") == pub_id:
                return record
    except Exception:
        return None
    return None


# ---------------------------------------------------------------- the six clauses


def clause_1_hardening_converged(pub_id: str, sha: str) -> dict:
    """`paper-hardening`'s convergence test: no blockers AND no P1s, on THIS commit.

    Reviewing a pinned commit is the skill's own rule — round 13's seats hit working-tree drift
    mid-review. So a hardening record for a DIFFERENT commit does not clear this paper; it clears
    the paper as it was.
    """
    record, err = _read_json(HARDENING_DIR / f"{pub_id}.json")
    if record is None:
        return _clause("hardening_converged", "hardening converged (no blockers, no P1s)",
                       UNVERIFIABLE, err + " — run a hardening round and record its result")
    blockers = record.get("blockers")
    p1s = record.get("p1s")
    if blockers is None or p1s is None:
        return _clause("hardening_converged", "hardening converged (no blockers, no P1s)",
                       UNVERIFIABLE, "record lacks `blockers` or `p1s` — absent is not empty")
    if record.get("reviewed_commit") != sha:
        return _clause("hardening_converged", "hardening converged (no blockers, no P1s)", FAIL,
                       f"last round reviewed {record.get('reviewed_commit')!r}, not {sha!r} — "
                       "a review of a different tree is not a review of this one")
    if blockers or p1s:
        return _clause("hardening_converged", "hardening converged (no blockers, no P1s)", FAIL,
                       f"{len(blockers)} blocker(s), {len(p1s)} P1(s) open at round "
                       f"{record.get('last_round')}")
    return _clause("hardening_converged", "hardening converged (no blockers, no P1s)", PASS,
                   f"round {record.get('last_round')} on {sha[:12]}: 0 blockers, 0 P1s")


def clause_2_preflight_full_green(pub_id: str, sha: str) -> dict:
    """`repo-gates`: PREFLIGHT_FULL=1 is required before anything outward-facing, and this is one
    of the only four acts it is for. The receipt must name THIS commit — a green run against a
    different tree says nothing about the one being posted."""
    record, err = _read_json(PREFLIGHT_DIR / f"{sha}.json")
    if record is None:
        return _clause("preflight_full_green", "PREFLIGHT_FULL=1 green on the posted commit",
                       UNVERIFIABLE, err + " — run PREFLIGHT_FULL=1 and record its exit code")
    if record.get("mode") != "FULL":
        return _clause("preflight_full_green", "PREFLIGHT_FULL=1 green on the posted commit", FAIL,
                       f"receipt records mode={record.get('mode')!r}; the scoped run does not "
                       "claim any test passes and cannot clear an outward-facing act")
    if record.get("exit") != 0:
        return _clause("preflight_full_green", "PREFLIGHT_FULL=1 green on the posted commit", FAIL,
                       f"exit={record.get('exit')!r}")
    if record.get("sha") != sha:
        return _clause("preflight_full_green", "PREFLIGHT_FULL=1 green on the posted commit", FAIL,
                       f"receipt is for {record.get('sha')!r}, not {sha!r}")
    return _clause("preflight_full_green", "PREFLIGHT_FULL=1 green on the posted commit", PASS,
                   f"FULL run exit 0 on {sha[:12]} at {record.get('utc')}")


def clause_3_claim_ceiling_honoured(pub_id: str, sha: str) -> dict:
    """lint_claims R1-R5 over the paper itself. Claim STRENGTH — never imply proteome-wide
    selectivity, EMC efficacy, safety, a therapeutic window or clinical readiness."""
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc:
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       UNVERIFIABLE, f"{pub_id} has no document.file in publications.json")
    path = REPO / doc
    if not path.exists():
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       UNVERIFIABLE, f"document {doc} does not exist")
    try:
        proc = subprocess.run(
            [sys.executable, str(MANUSCRIPTS / "lint_claims.py"), str(path)],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )
    except Exception as exc:
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       UNVERIFIABLE, f"lint_claims did not run ({type(exc).__name__})")
    if proc.returncode != 0:
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()
        return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling",
                       FAIL, f"lint_claims exit {proc.returncode}: {tail[-1] if tail else '—'}")
    return _clause("claim_ceiling_honoured", "claim strength within the endpoint's ceiling", PASS,
                   f"lint_claims clean over {doc}")


def clause_4_identifiers_resolvable(pub_id: str, sha: str) -> dict:
    """lint_citations. Orthogonal to clause 3 and BOTH are required: a hedged sentence on a
    fabricated PMID passes the claim linter. That has happened here twice."""
    endpoint = _endpoint(pub_id)
    doc = ((endpoint or {}).get("document") or {}).get("file")
    if not doc or not (REPO / doc).exists():
        return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                       UNVERIFIABLE, f"{pub_id} has no readable document")
    # ⚠ lint_citations takes NO file arguments — it checks the whole tracked corpus and there is no
    # paper-scoped mode. Passing it a path makes argparse exit 2, which reads as a FAILED clause for
    # a paper that may be perfectly clean. That defect was live for one commit and is why this
    # comment exists: a clause that can never pass is as dangerous as one that always does, because
    # an unreachable bar is what invites someone to loosen it.
    #
    # Running it corpus-wide is the conservative reading and we keep it deliberately: an unresolved
    # identifier anywhere in the repository blocks every post until it is fixed.
    try:
        proc = subprocess.run(
            [sys.executable, str(MANUSCRIPTS / "lint_citations.py")],
            capture_output=True, text=True, timeout=600, cwd=str(REPO),
        )
    except Exception as exc:
        return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                       UNVERIFIABLE, f"lint_citations did not run ({type(exc).__name__})")
    if proc.returncode != 0:
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()
        return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                       FAIL, f"lint_citations exit {proc.returncode}: {tail[-1] if tail else '—'} "
                             "(corpus-wide; the defect need not be in this paper)")
    return _clause("identifiers_resolvable", "every identifier traces to a fetch or the ledger",
                   PASS, f"lint_citations clean corpus-wide, covering {doc}")


def clause_5_endpoint_declared(pub_id: str, sha: str) -> dict:
    """The endpoint must exist as ONE falsifiable sentence the paper defends. CLAUDE.md §5: a route
    that cannot name its paper is an activity, not an option — and a paper that cannot name its
    claim is prose, not a result."""
    endpoint = _endpoint(pub_id)
    if endpoint is None:
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim",
                       UNVERIFIABLE, f"{pub_id} is not in systems/graph/publications.json")
    claim = (endpoint.get("what_it_would_claim") or "").strip()
    if len(claim) < 40:
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", FAIL,
                       f"what_it_would_claim is empty or too thin to falsify ({len(claim)} chars)")
    doc = (endpoint.get("document") or {}).get("file")
    if not doc or not (REPO / doc).exists():
        return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", FAIL,
                       f"endpoint names no existing document ({doc!r})")
    return _clause("endpoint_declared", "the endpoint is a declared falsifiable claim", PASS,
                   f"{pub_id} claims: {claim[:90]}...")


def clause_6_independent_adversarial_seat(pub_id: str, sha: str) -> dict:
    """A blind seat, on the pinned commit, reporting the central claim supported by the COMMITTED
    artifacts. `paper-hardening`: refute by default, and a seat that saw the authoring context is
    not independent."""
    record, err = _read_json(SEATS_DIR / f"{pub_id}-{sha}.json")
    if record is None:
        return _clause("independent_adversarial_seat", "a blind adversarial seat finds the claim "
                       "supported", UNVERIFIABLE, err + " — run a blind seat on this commit")
    if not record.get("blind"):
        return _clause("independent_adversarial_seat", "a blind adversarial seat finds the claim "
                       "supported", FAIL, "seat was not blind; it is not independent evidence")
    if record.get("reviewed_commit") != sha:
        return _clause("independent_adversarial_seat", "a blind adversarial seat finds the claim "
                       "supported", FAIL, f"seat reviewed {record.get('reviewed_commit')!r}")
    if record.get("verdict") != "supported":
        return _clause("independent_adversarial_seat", "a blind adversarial seat finds the claim "
                       "supported", FAIL, f"seat verdict: {record.get('verdict')!r}")
    return _clause("independent_adversarial_seat", "a blind adversarial seat finds the claim "
                   "supported", PASS, f"blind seat on {sha[:12]}: supported")


CLAUSES = (
    clause_1_hardening_converged,
    clause_2_preflight_full_green,
    clause_3_claim_ceiling_honoured,
    clause_4_identifiers_resolvable,
    clause_5_endpoint_declared,
    clause_6_independent_adversarial_seat,
)


# ---------------------------------------------------------------- the authority check


def authority_permits(pub_id: str, venue: str, act: str) -> dict:
    """The grant is bar-scoped (D1), but it is still a grant with edges. This checks the edges.

    ⛔ `journal` is not a parameter and no bar reaches it. If this function ever returns True for a
    journal, the amendment that did it is the bug.
    """
    authority, err = _read_json(AUTHORITY_FILE)
    if authority is None:
        return {"ok": False, "why": err + " — no authority file means no authority"}
    if venue == "journal":
        return {"ok": False, "why": "journal submission always escalates (D4); no bar reaches it"}
    if venue != "aixiv":
        return {"ok": False, "why": f"venue {venue!r} was never granted — the grant is aiXiv only"}
    aixiv = authority.get("aixiv") or {}
    if not aixiv.get("standing_grant"):
        return {"ok": False, "why": "standing_grant is not true"}
    if act not in (aixiv.get("scope") or {}).get("acts", []):
        return {"ok": False, "why": f"act {act!r} is outside the granted scope"}
    return {"ok": True, "why": f"granted: {aixiv.get('granted_by')}"}


def evaluate(pub_id: str, sha: str, venue: str = "aixiv", act: str = "submit") -> dict:
    clauses = [fn(pub_id, sha) for fn in CLAUSES]
    grant = authority_permits(pub_id, venue, act)
    all_clauses_pass = all(c["ok"] for c in clauses)
    return {
        "paper": pub_id,
        "commit": sha,
        "venue": venue,
        "act": act,
        "clauses": clauses,
        "authority": grant,
        "may_post": bool(all_clauses_pass and grant["ok"]),
        "n_passed": sum(1 for c in clauses if c["ok"]),
        "n_clauses": len(clauses),
        "_fail_closed": (
            "UNVERIFIABLE and FAIL both block. They differ only in what to do next: go get the "
            "evidence, or stop. Neither is ever treated as a pass."
        ),
    }


def _render(result: dict) -> str:
    lines = [f"{result['paper']} @ {result['commit'][:12]} -> "
             f"{'MAY POST' if result['may_post'] else 'BLOCKED'} "
             f"({result['n_passed']}/{result['n_clauses']} clauses)"]
    for clause in result["clauses"]:
        mark = "OK  " if clause["ok"] else ("FAIL" if clause["verdict"] == FAIL else "????")
        lines.append(f"  [{mark}] {clause['label']}")
        lines.append(f"         {clause['evidence']}")
    lines.append(f"  authority: {'OK' if result['authority']['ok'] else 'NO'} — "
                 f"{result['authority']['why']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--paper", help="publication endpoint id, e.g. PUB-ASO")
    parser.add_argument("--all", action="store_true", help="evaluate every endpoint")
    parser.add_argument("--sha", required=True, help="the commit being posted")
    parser.add_argument("--venue", default="aixiv", choices=["aixiv", "journal"])
    parser.add_argument("--act", default="submit", choices=["submit", "new_version"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.all:
        ids = [p["id"] for p in json.loads((GRAPH / "publications.json").read_text())]
    elif args.paper:
        ids = [args.paper]
    else:
        parser.error("give --paper or --all")

    results = [evaluate(i, args.sha, args.venue, args.act) for i in ids]
    if args.json:
        print(json.dumps(results if args.all else results[0], indent=2))
    else:
        print("\n\n".join(_render(r) for r in results))
    return 0 if all(r["may_post"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
