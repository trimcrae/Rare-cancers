#!/usr/bin/env python3
"""Do not re-ablate a sentence nothing about which has changed.

⛔⛔ THE MEASUREMENT. The ablation sweep is the only instrument that checks whether `covered` is
TRUE rather than merely recorded, and on 2026-09-02 it earned its place: at full depth it found
eleven sentences in the ASO journal article whose credited witnesses never went red. It is also,
measured the same day, **57 minutes of a 70-minute publication gate**:

    the guard's assertions, executed in-process        0.037 s
    one pytest subprocess to run them                  0.43  s
    the sweep, per sentence (its witnesses, cloned)   17.4   s
    x 197 covered sentences                           57     min

★ SO THE VERIFICATION IS MILLISECONDS AND THE CEREMONY AROUND IT IS ~470x THAT, PAID 197 TIMES ON
EVERY RUN WHETHER OR NOT ANYTHING MOVED. The night that produced this module edited about three
sentences and re-verified 197 to check them. A re-run over unchanged inputs carries no information;
it is not a slow job, it is a job doing the wrong amount of work.

★★ WHAT MAKES A CACHED VERDICT SOUND, AND IT IS THE ONLY THING THAT DOES. `ablate` asks: change this
sentence's number, and does any witness the census credits go red? That answer is a function of
exactly three things — the SENTENCE, the WITNESS SET, and the witnesses' own SOURCE. All three are
in the key, hashed, and a miss on any of them re-runs. Nothing is reused across a change to any of
them.

⛔ THE ONE INPUT DELIBERATELY NOT IN THE KEY IS THE ARTIFACT CORPUS, and the reason is an argument
rather than an oversight. A guard typically asserts "the prose figure equals the artifact's". If an
artifact moves so that the guard no longer binds, THE GUARD'S OWN TEST FAILS IN THE ORDINARY
MANUSCRIPTS SUITE — which runs on every commit, ahead of this. The sweep is not the only thing
standing between that regression and a reader, so it need not re-derive it. ⚠ Keying on the corpus
was the first design and it is worse than useless: every artifact regeneration would bust every
entry, and artifacts regenerate constantly here, so the cache would be empty exactly when it was
needed.

⛔ AND IT CANNOT LAUNDER A RED INTO A GREEN. A hit returns the recorded verdict, red or green
alike; a miss re-runs; an unreadable cache is a total miss. There is no path in this module by which
a sentence goes from "no witness noticed" to "covered" without a witness actually being run.

⚠ WHAT IT IS NOT. Not a correctness instrument — it decides only whether the expensive one must
run. Not a way to skip a first sweep: a new paper, a new sentence and a rewritten guard are all
misses by construction, so the depth that found the eleven is paid exactly when it can find
something.

Usage:
    python3 research/manuscripts/claim_ablation_cache.py --stats
    python3 research/manuscripts/claim_ablation_cache.py --prune   # drop entries no sentence maps to
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from claim_quantity_identifiers import orcid_spans  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(HERE, "claim-ablation-cache.json")
SCHEMA = "emc-claim-ablation-cache/1"


# ⛔⛔ EDITING A WITNESS FILE INVALIDATES EVERY KEY BUILT OVER IT — INCLUDING FOR A COMMENT.
# `witness_sources` hashes each guard's SOURCE, which is what makes a rewritten guard a miss; it
# cannot tell a rewritten assertion from a new docstring, and it must not try. ⚠ MEASURED THE HOUR
# THIS MODULE WAS WRITTEN: a comment added to `test_the_ablation_cache_cannot_launder_a_red.py`
# while the populating sweep was still running would have re-keyed all 184 entries mid-flight, for
# prose. ★ SO NOTES ABOUT THE CACHE LIVE HERE, IN A FILE NO KEY IS BUILT OVER, and a guard is
# edited when its ASSERTIONS change — then repopulated on purpose, not incidentally.
#
# ★ ONE SUCH NOTE, KEPT HERE FOR THE SAME REASON. The guard file names two manuscript paths
# literally, which makes it a "guard reading" both documents: `claim_ablation.guards_reading`
# collects every test module whose source contains a document's basename and re-runs it inside each
# ablation clone. Measured 2026-09-02 rather than assumed: the census credits that module to ZERO
# of its 750 sentences, so no `covered` figure leans on it; the cost is ~0.07 s added to a 17.4 s
# ablation. The module `claim_ablation` itself must still never name a manuscript — that one
# recurses, and it once turned a preflight into twenty silent minutes.


#: ⛔⛔ EVERY WITNESS KIND `claim_ablation.guards_reading` EMITS, AND THE FILES EACH ONE ACTUALLY
#: RUNS. There are three, and the first version of this module knew only one — `test:` — and failed
#: closed on the rest. ⚠ THAT MADE THE CACHE A NO-OP AND IT DID SO SILENTLY: `guards_reading`
#: appends `pin:*` to EVERY document's witness set, so `witness_sources` returned None for every
#: sentence in the repository, `key_for` returned None, and `record` dropped the verdict on the
#: floor. Measured 2026-09-02 by an 18-minute populating sweep that ablated all 184 sentences
#: correctly and then wrote a cache holding ZERO entries. Failing closed is right; failing closed on
#: the ordinary case is a cache that costs a run and buys nothing, and the only reason it was caught
#: is that the run printed its own entry count.
#: ★ `pin:*` CARRIES TWO FILES, AND THE SECOND IS THE POINT. `lint_consistency.py` is the enforcer,
#: but the pins it enforces live in `pinned-figures.json` — re-pinning a figure changes what the
#: witness would say without changing a line of its code, and CLAUDE.md rule 1.3 makes re-pinning a
#: routine act. A key over the enforcer alone would hit across exactly the edit the pins exist for.
def _witness_sources_for(witness):
    """Every file a witness's verdict is a function of, or None — which forces a miss.

    ⛔ NONE FOR AN UNRECOGNISED KIND, ALWAYS. A new witness kind added to `guards_reading` must make
    this cache colder, never blinder: an unknown kind whose source we cannot hash is a verdict we
    cannot key, and a verdict we cannot key must be recomputed.
    """
    if not isinstance(witness, str):
        return None
    if witness.startswith("test:"):
        return [os.path.join(HERE, "tests", witness.split(":", 1)[1])]
    if witness.startswith("pin:"):
        return [os.path.join(HERE, "lint_consistency.py"),
                os.path.join(HERE, "pinned-figures.json")]
    if witness.startswith("generator:"):
        return [os.path.join(ROOT, witness.split(":", 1)[1])]
    return None


def _witness_path(witness):
    """The first source file behind a witness, or None. Kept for callers that want one path."""
    paths = _witness_sources_for(witness)
    return paths[0] if paths else None


def witness_sources(witnesses):
    """`[(witness, sha256)]`, or None if ANY witness source cannot be read.

    ⛔ NONE, NOT A PARTIAL LIST. A key built over the witnesses that happened to be readable would
    hit whenever the unreadable one changed — the cache silently narrowing what it is keyed on,
    which is the failure this repository keeps meeting one level up.
    """
    out = []
    for w in sorted(witnesses or []):
        paths = _witness_sources_for(w)
        if not paths:
            return None
        acc = hashlib.sha256()
        for p in paths:
            if not os.path.exists(p):
                return None
            with open(p, "rb") as fh:
                acc.update(os.path.basename(p).encode("utf-8") + b"\0" + fh.read() + b"\n")
        out.append((w, acc.hexdigest()))
    return out


def key_for(paper, sentence, witnesses):
    """The content key, or None when it cannot be built (which the caller must treat as a miss)."""
    srcs = witness_sources(witnesses)
    if srcs is None:
        return None
    acc = hashlib.sha256()
    acc.update(paper.encode("utf-8") + b"\0")
    acc.update(sentence.encode("utf-8") + b"\0")
    # Only rows whose permitted mutation sites changed lose the old verdict.
    # A hit earned by altering an author identifier cannot certify a quantity.
    if orcid_spans(sentence):
        acc.update(b"quantity-sites-exclude-valid-orcid/1\0")
    for w, digest in srcs:
        acc.update(w.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\n")
    return acc.hexdigest()


def load():
    try:
        with open(CACHE, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(doc, dict) or doc.get("_schema") != SCHEMA:
        return {}
    entries = doc.get("entries")
    return entries if isinstance(entries, dict) else {}


WRITE_ENV = "CLAIM_ABLATION_CACHE_WRITE"


def writes_enabled():
    """⛔⛔ THE CACHE IS READ-ONLY UNLESS SOMEBODY ASKED FOR A POPULATE, AND THAT IS NOT TIDINESS.

    The file is TRACKED, and `tracked_tree_guard.assert_tree_unchanged()` fails any pytest run that
    modifies a tracked file (AUT-PD-186). The ablation gate runs inside the manuscripts suite, so a
    cache that wrote itself while grading would redden every suite that missed — a gate failing
    because of its own accelerator, which is the worst possible reason for a red.
    ★ AND THE STRONGER REASON: a grader that edits its own record of what it graded is a shape this
    repository has already been bitten by. Reading is free; writing is an act somebody performs on
    purpose, with `CLAIM_ABLATION_CACHE_WRITE=1`, and commits.
    ⚠ THE COST OF FORGETTING IS SLOWNESS, NEVER A WRONG ANSWER. An unpopulated key is a miss and
    re-ablates in full; the gate is then as slow as it was before this module existed and exactly as
    correct. That is the direction a cache in front of a correctness gate must fail in.
    """
    return os.environ.get(WRITE_ENV) == "1"


def save(entries, note=None):
    if not writes_enabled():
        return False
    doc = {
        "_schema": SCHEMA,
        "_role": "Verdicts of the claim-ablation sweep, keyed on (paper, sentence, witness set, "
                 "witness source digests). A hit skips a 17.4 s re-ablation; a miss re-runs. See "
                 "claim_ablation_cache.py for why the artifact corpus is deliberately not in the key.",
        "_not_a_correctness_instrument": "This decides only whether the expensive check must run. A "
                                         "cached RED is still a RED; there is no path here from 'no "
                                         "witness noticed' to 'covered' without running a witness.",
        "entries": dict(sorted(entries.items())),
    }
    if note:
        doc["_note"] = note
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return True


def lookup(entries, key):
    """The recorded verdict for `key`, or None. A malformed entry is a MISS, never a pass."""
    if key is None:
        return None
    got = entries.get(key)
    if not isinstance(got, dict) or not isinstance(got.get("red"), bool):
        return None
    # ⛔ AN ENTRY WITHOUT A RECORDED `status` PREDATES THAT FIELD AND IS A MISS. Defaulting it to
    # APPLIED would turn every legacy row into a claim that a perturbation was watched, which is the
    # one thing this cache must never invent.
    if not isinstance(got.get("status"), str):
        return None
    return got


def record(entries, key, red, reason, witnesses, status=None, quantity_kind=None, baseline=None):
    """⛔ `status` IS RECORDED WITH THE VERDICT, NOT INFERRED FROM IT. `ablate` distinguishes
    APPLIED (the sentence was perturbed and we watched) from NOT_APPLIED (it could not be perturbed,
    so the run measured nothing). Caching `red` alone would let a NOT_APPLIED come back looking like
    a clean APPLIED — absence read as evidence, one layer down from where this repository usually
    meets it."""
    if key is None:
        return entries
    row = {"red": bool(red), "reason": str(reason)[:400], "witnesses": sorted(witnesses or [])}
    if status is not None:
        row["status"] = status
    if quantity_kind is not None:
        row["quantity_kind"] = quantity_kind
    # ⛔ THE BASELINE RIDES WITH THE VERDICT, because a BLIND is only readable next to it. `ablate`
    # reports how many of a sentence's witnesses were ALREADY red before the perturbation — 25 of 26
    # once meant "these guards were never in a position to notice", which reads identically to "no
    # guard cared" if the number is dropped. A cached verdict that lost it would recreate the exact
    # false-BLIND the subtraction note was written for.
    if baseline is not None:
        row["baseline"] = baseline
    entries[key] = row
    return entries


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--prune", action="store_true")
    a = ap.parse_args(argv)
    entries = load()
    if a.prune:
        sys.path.insert(0, HERE)
        import claim_coverage  # noqa: E402
        live = set()
        for paper in claim_coverage.COVERAGE_FLOOR:
            for row in claim_coverage.census(paper):
                if row.get("covered"):
                    k = key_for(paper, row["sentence"], row.get("read_by"))
                    if k:
                        live.add(k)
        dropped = [k for k in entries if k not in live]
        for k in dropped:
            del entries[k]
        wrote = save(entries, note="pruned %d entry(ies) no live covered sentence maps to"
                                   % len(dropped))
        if not wrote:
            print("REFUSED: %s=1 is required to write the cache. Nothing was changed; %d entry(ies) "
                  "would have been dropped." % (WRITE_ENV, len(dropped)))
            return 1
        print("pruned %d, kept %d" % (len(dropped), len(entries)))
        return 0
    red = sum(1 for e in entries.values() if e.get("red"))
    print("%d cached verdict(s): %d red, %d green" % (len(entries), red, len(entries) - red))
    print("A hit skips ~17.4 s; measured end to end, a hit is 0.005 s. The full sweep of the 184 "
          "covered numbered sentences is 53 min serially and 19 min over four shards — this is what "
          "makes an edit to three of them cost three re-ablations rather than 184.")
    print("writes: %s (set %s=1 to populate; a run without it reads only)"
          % ("ENABLED" if writes_enabled() else "read-only", WRITE_ENV))
    return 0


if __name__ == "__main__":
    sys.exit(main())
