#!/usr/bin/env python3
"""ADMISSION CONTROL ON THE LEDGER QUEUE: the same IDEA cannot be filed twice (AUT-PROP-035).

⛔⛔ THE FAILURE THIS EXISTS FOR IS NOT A DUPLICATE ID. It is a session, three cycles from now, with
no memory of this one, reading the same survey, reaching the same conclusion, and filing it as
`AUT-PROP-061`. Every id-based check passes, because `ids.py` mints a fresh id by construction, and
`priority.py` faithfully scores the new row and sorts it near the old one. Repeat that and the queue
fills with one idea wearing forty names, while the anti-starvation term keeps promoting all forty.

★★ THE MECHANISM IS NSLS-II's Adjudicator, from `research/method-watch-autonomy-prior-art-2.md` §3:
"meta-agents that consume suggestions from many agents and gatekeep the Queue Server", deduplicating
incoming suggestions against a bounded `DequeSet(maxlen=100)` of suggestion uids so that an agent
which keeps re-proposing the same idea cannot fill the queue with it. The BOUND is copied as-is and
the KEY is not, for the reason above: their uids identify a suggestion, and re-filing here mints a
new one.

★★ WHAT IDENTITY MEANS HERE — THE ONE DESIGN DECISION IN THIS FILE.
    A proposal's identity is the triple **(kind, route, idea-signature)**, where the idea-signature
    is derived from the NORMALIZED TEXT of `what`.

    · WHY NOT THE ID. It is the failure mode itself. Stated first so nobody re-derives it.
    · WHY `kind` AND `route` ARE PART OF IT, WITH THE MEASUREMENT THAT FORCED IT. The ledger already
      contains rows with BYTE-IDENTICAL `what` that are correctly distinct work: "Keep registered for
      automatic re-grade when EMC expression data lands." appears on RT-FAP-RLT (AUT-025) and
      RT-TCRT-CTA (AUT-070); "Nothing. Cite the closure." appears on RT-DBD (AUT-018) and
      RT-FET-LC-LIGAND (AUT-026). These are graph-generated boilerplate, one row per route, and a
      text-only key would suppress 39 of 40 legitimate rows. Route is therefore part of identity.
    · AND THE HOLE THAT LEAVES IS REPORTED, NOT PAPERED OVER. Re-filing the same idea under a
      DIFFERENT route dodges the primary key. That is why `cross_route_echoes()` exists and why the
      CLI prints it: a cross-route near-match is surfaced as a WARNING a human reads, never as a
      silent block, because on this ledger those matches are usually the legitimate boilerplate above.

★ THE SIGNATURE IS TWO-TIER, BECAUSE ONE TIER IS DEFEATED BY ONE WORD.
    · TIER 1 — EXACT: sha256 over the normalized text. Normalization folds NFKC, strips the marker
      glyphs this repository writes prose in (⛔ ⭐ ⚠ ★), strips ledger and cycle ids, ISO dates and
      bare numbers, lowercases, and collapses everything else to single spaces. ⭐ Stripping ids and
      dates is not cosmetic: a re-file characteristically carries a different provenance clause
      ("found by CYC-0044 on 2026-08-27") wrapped around an identical idea, and leaving those in is
      what defeats an exact hash in practice.
    · TIER 2 — NEAR: Jaccard overlap of 5-word shingle sets, within the same (kind, route) bucket.

⭐⭐ AND THE NEAR THRESHOLD IS CALIBRATED AGAINST THIS LEDGER, NOT REMEMBERED (CLAUDE.md §4). Measured
2026-08-28 over the committed `research-ledger.json`, 187 entries:
    · 1,108 in-bucket pairs of GENUINELY DISTINCT rows — the false-positive population — top out at
      **0.111** (the highest is AUT-PROP-040 ~ AUT-PROP-042, two different hardening items on
      RT-ASO-JUNCTION). Nothing distinct in the whole ledger scores higher.
    · The true-positive population, measured by controls on a real row against a modified copy of
      ITSELF: a light rewording scores **0.484** and a 60% truncation **0.602** on AUT-PD-026, the
      longest row in the file, which is what `calibration_probe()` reproduces on every run; an
      independent pass over the longest PROPOSAL row, AUT-PROP-030, gave 0.504 and 0.606. Four
      readings, none below 0.48.
  The two populations are separated by a factor of 4.4 with nothing in between, so the threshold is
  put in the gap: **0.30**, which is 2.7x above every observed false positive and 1.6x below the
  weakest observed true positive. ⚠ It is a calibration on a 187-row corpus, not a law; the number to
  re-measure when the ledger has grown is the in-bucket maximum, and if it ever approaches 0.30 the
  threshold is wrong rather than the corpus. The script that produces both figures is the docstring
  of `calibration_probe()`, so the measurement is repeatable rather than quoted.

⛔⛔ IT IS FALSIFIABLE, AND "SILENTLY DROP" IS STRUCTURALLY IMPOSSIBLE RATHER THAN DISCOURAGED.
    · `consider()` and `admit()` ALWAYS return a `Decision`; there is no path that returns None or a
      bare bool, so a caller cannot fail to receive the reason.
    · `Decision.__post_init__` REFUSES to construct a rejection that lacks a matched id, a matched
      fingerprint and a reason. A future edit that suppresses a row without saying what it collided
      with raises `ValueError` at the point of the bug instead of dropping a row quietly.
    · Every rejection is retained in `Adjudicator.suppressed` and rendered by `--check`, with the
      matched id, the tier, the similarity and both normalized texts' shared-shingle count.
    · The BOUND is honest about what it forgets: `evictions` counts the fingerprints pushed out of
      the deque, and an idea filed more than `DEDUP_MAXLEN` proposals ago is no longer remembered.
      NSLS-II accepts the same limit; the difference is that this one reports it.

⛔ IT DECIDES, IT DOES NOT MUTATE. Nothing here writes `research-ledger.json` (that is `ledger_io`'s
job and the driver's call). `--check` reads the committed ledger and reports the collisions already
in it, which is what makes the rule testable against real data today rather than only against
fixtures.

Usage:
    python3 research/autonomy/proposal_dedup.py --check                # scan the committed ledger
    python3 research/autonomy/proposal_dedup.py --check --all-kinds    # not just `proposal` rows
    python3 research/autonomy/proposal_dedup.py --check --json
    python3 research/autonomy/proposal_dedup.py --check --fail-on-duplicate
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import itertools
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER_PATH = os.path.join("research", "autonomy", "research-ledger.json")

#: NSLS-II's bound, copied as-is. A set that never forgets is a memory leak with a queue attached;
#: a bounded one is a deliberate, statable limit.
DEDUP_MAXLEN = 100

#: The near-duplicate threshold, calibrated in the module docstring against the committed ledger.
#: ⛔ Never edit this without re-running `calibration_probe()` and putting the new figures beside it.
NEAR_DUPLICATE_JACCARD = 0.30

#: Shingle width. 5 words is long enough that ordinary shared phrasing ("the ledger", "CLAUDE.md §4")
#: does not create overlap — visible in the calibration, where 107 of 1,108 distinct in-bucket pairs
#: overlap at all and none exceeds 0.111 — and short enough to survive a reworded sentence.
SHINGLE_WORDS = 5

#: Marker glyphs this repository writes prose in. They carry emphasis, never identity.
_MARKERS = "⛔⭐⚠★✅→←↑↓·—–"
_ID_RE = re.compile(r"\b[A-Z]{2,}-[A-Z0-9]+-\d+\b|\bCYC-\d+[A-Za-z0-9-]*\b|\bPMID\s*\d+\b")
_DATE_RE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
_NUM_RE = re.compile(r"\b\d[\d.,]*\b")
_NONWORD_RE = re.compile(r"[^0-9a-zA-Z]+")


def normalize(text: str | None) -> str:
    """The normalized form both tiers are computed from. One function, so the two tiers can never
    disagree about what the text of a proposal is."""
    out = unicodedata.normalize("NFKC", text or "")
    for marker in _MARKERS:
        out = out.replace(marker, " ")
    out = _ID_RE.sub(" ", out)
    out = _DATE_RE.sub(" ", out)
    out = _NUM_RE.sub(" ", out)
    out = _NONWORD_RE.sub(" ", out.lower())
    return " ".join(out.split())


def shingles(text: str | None, width: int = SHINGLE_WORDS) -> frozenset:
    tokens = normalize(text).split()
    if not tokens:
        return frozenset()
    if len(tokens) < width:
        return frozenset([" ".join(tokens)])
    return frozenset(" ".join(tokens[i:i + width]) for i in range(len(tokens) - width + 1))


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def bucket_of(entry: dict) -> tuple:
    """The (kind, route) bucket a proposal's identity is scoped to. Argued in the module docstring:
    the ledger contains byte-identical `what` on different routes that is correctly distinct work."""
    return (entry.get("kind"), (entry.get("serves") or {}).get("route"))


def fingerprint(entry: dict) -> str:
    """TIER 1. The exact identity of an idea: sha256 over (kind, route, normalized `what`).

    ⛔ `id` is deliberately NOT an input. A fingerprint that included it would be a slower way of
    comparing ids, which is the check that already passes on every real re-file.
    """
    kind, route = bucket_of(entry)
    payload = "\x1f".join([str(kind), str(route), normalize(entry.get("what"))])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Decision:
    """The answer to "may this row be filed?", and the only thing `consider`/`admit` ever return.

    ⛔ A REJECTION THAT CANNOT EXPLAIN ITSELF IS REFUSED AT CONSTRUCTION. This is the mechanism that
    makes "silently drop a row" impossible rather than merely discouraged: an edit that starts
    suppressing rows without recording what they collided with raises here, at the bug.
    """
    entry_id: str
    admitted: bool
    fingerprint: str
    reason: str
    tier: str | None = None                 # "exact" | "near" | None
    matched_id: str | None = None
    matched_fingerprint: str | None = None
    similarity: float | None = None
    shared_shingles: int | None = None
    bucket: tuple | None = None

    def __post_init__(self):
        if self.admitted:
            return
        missing = [name for name in ("reason", "tier", "matched_id", "matched_fingerprint")
                   if not getattr(self, name)]
        if missing:
            raise ValueError(
                f"a suppressed proposal must say what it collided with and why; missing {missing}. "
                f"Reporting is not optional here — see the module docstring's falsifiability clause.")

    def as_dict(self) -> dict:
        return {
            "entry_id": self.entry_id, "admitted": self.admitted, "fingerprint": self.fingerprint,
            "reason": self.reason, "tier": self.tier, "matched_id": self.matched_id,
            "matched_fingerprint": self.matched_fingerprint, "similarity": self.similarity,
            "shared_shingles": self.shared_shingles,
            "bucket": list(self.bucket) if self.bucket else None,
        }


class DequeSet:
    """A bounded, insertion-ordered, deduplicating set — NSLS-II's `DequeSet(maxlen=100)`.

    ⚠ `collections.deque(maxlen=…)` alone is not enough: membership on a deque is O(n) and, worse,
    re-adding an existing key would push a duplicate and evict a DIFFERENT key. The set beside it is
    what makes the bound mean "the last N DISTINCT ideas".
    """

    def __init__(self, maxlen: int = DEDUP_MAXLEN):
        if maxlen < 1:
            raise ValueError("a bound of zero is not a bounded memory, it is no memory")
        self.maxlen = maxlen
        self._deque: collections.deque = collections.deque()
        self._set: set = set()
        self.evictions = 0

    def __contains__(self, key) -> bool:
        return key in self._set

    def __len__(self) -> int:
        return len(self._set)

    def __iter__(self):
        return iter(self._deque)

    def add(self, key) -> None:
        if key in self._set:
            return
        self._deque.append(key)
        self._set.add(key)
        while len(self._deque) > self.maxlen:
            self._set.discard(self._deque.popleft())
            self.evictions += 1


class Adjudicator:
    """Admission control for ledger proposals. Decides; never mutates the ledger."""

    def __init__(self, maxlen: int = DEDUP_MAXLEN,
                 near_threshold: float = NEAR_DUPLICATE_JACCARD):
        self.seen = DequeSet(maxlen)
        self.near_threshold = near_threshold
        #: fingerprint -> (entry_id, bucket, shingles). Kept in step with `seen` so tier 2 can only
        #: ever compare against ideas the BOUNDED memory still holds — an evicted idea is forgotten
        #: by both tiers or by neither.
        self._records: dict = {}
        self.suppressed: list = []
        self.admitted: list = []

    # -- reading -------------------------------------------------------------------------------

    def _prune(self) -> None:
        for key in [k for k in self._records if k not in self.seen]:
            self._records.pop(key, None)

    def consider(self, entry: dict) -> Decision:
        """The decision for `entry`, WITHOUT recording it. Always returns a `Decision`."""
        entry_id = str(entry.get("id") or "<unfiled>")
        key = fingerprint(entry)
        bucket = bucket_of(entry)
        if key in self.seen:
            prior_id = self._records.get(key, ("<evicted>", None, frozenset()))[0]
            return Decision(entry_id=entry_id, admitted=False, fingerprint=key,
                            tier="exact", matched_id=prior_id, matched_fingerprint=key,
                            similarity=1.0, bucket=bucket,
                            reason=(f"byte-identical idea after normalization: same kind, same "
                                    f"route and the same `what` as {prior_id}. Re-filing it under a "
                                    f"new id does not make it a new idea."))
        mine = shingles(entry.get("what"))
        best = (0.0, None, None, 0)
        for other_key, (other_id, other_bucket, other_shingles) in self._records.items():
            if other_bucket != bucket:
                continue
            score = jaccard(mine, other_shingles)
            if score > best[0]:
                best = (score, other_id, other_key, len(mine & other_shingles))
        score, prior_id, prior_key, shared = best
        if prior_id is not None and score >= self.near_threshold:
            return Decision(entry_id=entry_id, admitted=False, fingerprint=key, tier="near",
                            matched_id=prior_id, matched_fingerprint=prior_key,
                            similarity=round(score, 4), shared_shingles=shared, bucket=bucket,
                            reason=(f"near-duplicate of {prior_id} in the same (kind, route) bucket: "
                                    f"Jaccard {score:.3f} over {SHINGLE_WORDS}-word shingles, "
                                    f"threshold {self.near_threshold:.2f}, {shared} shared shingles. "
                                    f"The calibration that pins that threshold is in the module "
                                    f"docstring; if this match is wrong, the number to re-measure is "
                                    f"the in-bucket maximum, not this row."))
        return Decision(entry_id=entry_id, admitted=True, fingerprint=key, bucket=bucket,
                        similarity=round(score, 4) if prior_id else 0.0,
                        matched_id=prior_id if score > 0 else None,
                        reason=(f"no idea in the last {self.seen.maxlen} admitted proposals matches "
                                f"this one (closest {score:.3f} < {self.near_threshold:.2f})."))

    # -- writing -------------------------------------------------------------------------------

    def record(self, entry: dict) -> str:
        """Remember an idea WITHOUT judging it — used to seed the memory from committed history."""
        key = fingerprint(entry)
        self.seen.add(key)
        self._records[key] = (str(entry.get("id") or "<unfiled>"), bucket_of(entry),
                              shingles(entry.get("what")))
        self._prune()
        return key

    def admit(self, entry: dict) -> Decision:
        """Consider `entry` and remember it if admitted. ALWAYS returns the `Decision`.

        ⛔ A REJECTED ENTRY IS NOT RECORDED. Recording it would make the second re-file collide with
        the first re-file rather than with the original, and the report would name the wrong row.
        """
        decision = self.consider(entry)
        if decision.admitted:
            self.record(entry)
            self.admitted.append(decision)
        else:
            self.suppressed.append(decision)
        return decision

    def seed(self, entries) -> "Adjudicator":
        """Fill the bounded memory from committed rows, oldest first."""
        for entry in entries:
            self.record(entry)
        return self


# --------------------------------------------------------------------------------------------
# Reading the committed ledger.
# --------------------------------------------------------------------------------------------


def load_entries(repo: str = REPO, path: str = LEDGER_PATH) -> list:
    with open(os.path.join(repo, path), encoding="utf-8") as fh:
        return json.load(fh).get("entries", [])


def scan(entries, kinds=("proposal",), maxlen: int = DEDUP_MAXLEN,
         near_threshold: float = NEAR_DUPLICATE_JACCARD) -> dict:
    """Replay the ledger through the adjudicator in file order and report what it would refuse.

    ⚠ This is a REPLAY of committed rows, not a judgement on them: a row already in the ledger has
    already been filed. What it answers is "would this rule have refused anything real, and what?",
    which is the only way to tell a working admission gate from one tuned to never fire.
    """
    subject = [e for e in entries if kinds is None or e.get("kind") in kinds]
    adjudicator = Adjudicator(maxlen=maxlen, near_threshold=near_threshold)
    for entry in subject:
        adjudicator.admit(entry)
    return {
        "considered": len(subject), "kinds": list(kinds) if kinds else "all",
        "admitted": len(adjudicator.admitted), "suppressed": adjudicator.suppressed,
        "evictions": adjudicator.seen.evictions, "maxlen": maxlen,
        "near_threshold": near_threshold, "adjudicator": adjudicator,
    }


def cross_route_echoes(entries, kinds=("proposal",),
                       near_threshold: float = NEAR_DUPLICATE_JACCARD) -> list:
    """The hole in the primary key, reported rather than closed: pairs whose text matches across
    DIFFERENT routes. Never a block — on this ledger those are usually graph-generated boilerplate,
    one row per route — always a line a human can read."""
    subject = [e for e in entries if kinds is None or e.get("kind") in kinds]
    sh = [(e, shingles(e.get("what"))) for e in subject]
    out = []
    for (a, sa), (b, sb) in itertools.combinations(sh, 2):
        if bucket_of(a) == bucket_of(b):
            continue
        score = jaccard(sa, sb)
        if score >= near_threshold:
            out.append({"a": a.get("id"), "b": b.get("id"),
                        "a_route": bucket_of(a)[1], "b_route": bucket_of(b)[1],
                        "similarity": round(score, 4)})
    out.sort(key=lambda d: -d["similarity"])
    return out


def calibration_probe(entries) -> dict:
    """RE-RUN THE MEASUREMENT THAT PINS `NEAR_DUPLICATE_JACCARD`, rather than quoting it.

    Returns the false-positive ceiling (the highest similarity between two GENUINELY DISTINCT rows
    in the same bucket) and the true-positive controls (a real row against a lightly reworded and a
    truncated copy of itself). The threshold is only defensible while these stay separated.
    """
    buckets: dict = {}
    for entry in entries:
        buckets.setdefault(bucket_of(entry), []).append(entry)
    worst = (0.0, None, None)
    pairs = 0
    for rows in buckets.values():
        sh = [(e.get("id"), shingles(e.get("what"))) for e in rows]
        for (ia, sa), (ib, sb) in itertools.combinations(sh, 2):
            pairs += 1
            score = jaccard(sa, sb)
            if score > worst[0]:
                worst = (score, ia, ib)
    longest = max(entries, key=lambda e: len(e.get("what") or "")) if entries else {}
    original = longest.get("what") or ""
    reworded = (original.replace("the ", "a ").replace("THE ", "A ")
                        .replace("must", "should").replace("Add", "Introduce"))
    truncated = original[: int(len(original) * 0.6)]
    return {
        "in_bucket_pairs": pairs,
        "false_positive_ceiling": round(worst[0], 4),
        "false_positive_pair": [worst[1], worst[2]],
        "reword_control_id": longest.get("id"),
        "reword_control": round(jaccard(shingles(original), shingles(reworded)), 4),
        "truncation_control": round(jaccard(shingles(original), shingles(truncated)), 4),
        "threshold": NEAR_DUPLICATE_JACCARD,
    }


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="scan the committed ledger")
    parser.add_argument("--all-kinds", action="store_true",
                        help="consider every entry, not just `kind: proposal`")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--path", default=LEDGER_PATH)
    parser.add_argument("--fail-on-duplicate", action="store_true",
                        help="exit 1 if the rule would refuse any row")
    args = parser.parse_args(argv)

    entries = load_entries(args.repo, args.path)
    kinds = None if args.all_kinds else ("proposal",)
    report = scan(entries, kinds=kinds)
    echoes = cross_route_echoes(entries, kinds=kinds)
    probe = calibration_probe(entries)

    if args.json:
        print(json.dumps({
            "considered": report["considered"], "kinds": report["kinds"],
            "admitted": report["admitted"],
            "suppressed": [d.as_dict() for d in report["suppressed"]],
            "evictions": report["evictions"], "maxlen": report["maxlen"],
            "near_threshold": report["near_threshold"],
            "cross_route_echoes": echoes, "calibration": probe,
        }, indent=2))
        return 1 if (args.fail_on_duplicate and report["suppressed"]) else 0

    print(f"   admission: identity = (kind, route, normalized `what`), memory = the last "
          f"{report['maxlen']} DISTINCT ideas")
    print(f"   tier 1 exact sha256 · tier 2 Jaccard >= {report['near_threshold']:.2f} over "
          f"{SHINGLE_WORDS}-word shingles, same bucket only")
    print(f"   considered {report['considered']} row(s) of kind {report['kinds']}: "
          f"{report['admitted']} admitted, {len(report['suppressed'])} refused, "
          f"{report['evictions']} idea(s) evicted from the bounded memory")
    print()
    print(f"   calibration re-measured now, {probe['in_bucket_pairs']} in-bucket pairs:")
    print(f"     distinct rows top out at {probe['false_positive_ceiling']:.3f} "
          f"({probe['false_positive_pair'][0]} ~ {probe['false_positive_pair'][1]})")
    print(f"     reworded control {probe['reword_control']:.3f} · truncated control "
          f"{probe['truncation_control']:.3f} · threshold {probe['threshold']:.2f}")
    if probe["false_positive_ceiling"] >= probe["threshold"]:
        print("   ⛔ THE CALIBRATION NO LONGER SEPARATES: a genuinely distinct pair now scores at or "
              "above the threshold. The threshold is wrong, not the row.")

    if report["suppressed"]:
        print()
        print("   REFUSED (never dropped silently — this is the whole list, with reasons):")
        for decision in report["suppressed"]:
            print(f"     ⛔ {decision.entry_id} -> collides with {decision.matched_id} "
                  f"[{decision.tier}, sim {decision.similarity}]")
            print(f"        {decision.reason}")
    else:
        print()
        print("   No row in the committed ledger would be refused. That is a reading of what is "
              "already filed, not a claim that the rule cannot fire — see the calibration above.")

    if echoes:
        print()
        print("   ⚠ CROSS-ROUTE ECHOES (reported, never blocked — the known hole in the key):")
        for echo in echoes[:15]:
            print(f"     {echo['a']} ({echo['a_route']}) ~ {echo['b']} ({echo['b_route']}) "
                  f"sim {echo['similarity']}")
        if len(echoes) > 15:
            print(f"     … and {len(echoes) - 15} more")

    return 1 if (args.fail_on_duplicate and report["suppressed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
