#!/usr/bin/env python3
"""THE DECOY NULL'S EVIDENCE CHAIN, END TO END FROM COMMITTED FILES. ($0, pure stdlib)

⭐ WHY (roadmap §10.1a `Q17`, §6d, `paper-framing-options.md` must-fix 1 and 4). `V20` -- single-snapshot
MM-GBSA `margin > 0` as a selectivity verdict -- is the program's most load-bearing negative and the
headline of the recommended `P1`/`P5` framings. Until 2026-08-07 its PRIMARY RUN OUTPUT lived only in S3;
what was committed was the 38-margin constant `selectivity_calibration.DECOY_2026_06_30` and the paper's
prose. The roadmap said so in its own words: *"the weakest evidence chain in §6a, and the only row here
whose refutation is not readable end-to-end from a committed artifact."*

⛔ THAT IS THE AUDIT'S OWN RULE FAILED BY THE AUDIT'S OWN HEADLINE. `paper-framing-options.md` states the
prophylactic as two rules, and rule (b) is **persist the primary artifact**.

★ CLOSED 2026-08-07. `archive-results-aws.yml mode=archive prefixes=nr4a3-decoy` mirrored the surviving
S3 objects into `results/nr4a3-decoy/`, and this module VERIFIES the chain rather than asserting it: it
reads the archived per-drug records and the committed constant and checks they are the same 38 numbers.

⚠ THE VERIFICATION IS THE POINT, NOT THE COPY. Three MM-GBSA arms were archived and only ONE of them is
the run the constant came from -- the single-snapshot arm. The two multi-snapshot arms return DIFFERENT
margins from the same docked poses (that difference IS the §2.7 de-noising result), so an artifact merely
sitting in `results/` would not have told anyone which file the paper's number is. A committed file whose
correspondence to the quoted number is unverified is not an evidence chain; it is a second place to look.

⚠ AND IT DOES NOT RE-DERIVE THE VERDICT. `V20` is ✕ REFUTED in the roadmap and stays there; this module
adds no grade, recomputes no conclusion, and quotes no percentile the roadmap does not already own.

Usage:
    python3 research/modalities/decoy_null_provenance.py            # regenerate the artifact
    python3 research/modalities/decoy_null_provenance.py --check    # fail if it has drifted
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(ROOT, "results", "nr4a3-decoy")
OUT = os.path.join(HERE, "decoy-null-provenance.json")

#: The three archived MM-GBSA arms, and what each one is. Only the first is the run `DECOY_2026_06_30`
#: was taken from; the others are recorded so nobody has to guess later which file the paper quotes.
ARMS = (
    ("-mmgbsa",           "single-snapshot, release NR4A3 + metad-opened paralogues -- THE canonical null"),
    ("-mmgbsa-ms",        "MULTI-snapshot de-noising of the same docked poses (paper §2.7)"),
    ("-mmgbsa-metad-ms",  "MULTI-snapshot on the metad-opened NR4A3 receptor"),
)
MARGIN_FIELD = "mm_min_margin"


def _read_arm(sub):
    p = os.path.join(RESULTS, sub, "nr4a3-mmgbsa.json")
    if not os.path.exists(p):
        return None, "MISSING: %s" % os.path.relpath(p, ROOT)
    return json.load(open(p, encoding="utf-8")), None


def build():
    sys.path.insert(0, HERE)
    from selectivity_calibration import DECOY_2026_06_30 as CONST

    want = sorted((round(float(v), 2) for v in CONST), reverse=True)
    arms = []
    for sub, what in ARMS:
        j, why = _read_arm(sub)
        if j is None:
            # ⚠ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). A missing arm is reported as
            # unread, never as a mismatch and never as a match.
            arms.append({"arm": sub, "what": what, "read": False, "why": why})
            continue
        cands = j.get("candidates") or []
        got = sorted((round(float(c[MARGIN_FIELD]), 2) for c in cands if MARGIN_FIELD in c), reverse=True)
        arms.append({
            "arm": sub,
            "what": what,
            "read": True,
            "artifact": os.path.relpath(os.path.join(RESULTS, sub, "nr4a3-mmgbsa.json"), ROOT),
            "n_candidates": len(cands),
            "n_margins": len(got),
            "n_positive_margin": sum(1 for v in got if v > 0),
            "verdict_census": j.get("verdict_census"),
            "scheme": (j.get("method") or {}).get("scheme"),
            "reproduces_DECOY_2026_06_30": got == want,
            "margins_desc": got,
        })

    matching = [a["arm"] for a in arms if a.get("reproduces_DECOY_2026_06_30")]
    doc = {
        "_what": ("The evidence chain for `V20` (single-snapshot MM-GBSA `margin > 0` refuted by a 38-drug "
                  "non-NR4A decoy null), read end to end from COMMITTED files."),
        "_generated_by": "research/modalities/decoy_null_provenance.py",
        "_closes": ("roadmap §10.1a `Q17` / §6d 'the only row here whose refutation is not readable "
                    "end-to-end from a committed artifact'; paper-framing-options.md must-fix 1 and 4"),
        "_how_the_primary_output_reached_git": (
            "archive-results-aws.yml mode=archive prefixes=nr4a3-decoy, 2026-08-07 8:02 AM ET, run "
            "31176492466 -> results/nr4a3-decoy/. A mode=diagnose pass first (run 31176409308) confirmed "
            "the objects had survived S3 lifecycle: 25 archivable objects under the prefix."),
        "_rule": ("The roadmap owns `V20`'s verdict and every percentile quoted from this null. This "
                  "artifact adds no grade -- it records WHICH committed file the quoted numbers come from "
                  "and CHECKS that it reproduces them."),
        "constant": {
            "name": "selectivity_calibration.DECOY_2026_06_30",
            "n": len(want),
            "source_of_truth_for_the_values": "research/modalities/selectivity_calibration.py",
        },
        "arms": arms,
        "_derived": {
            "arms_read": sum(1 for a in arms if a.get("read")),
            "arms_reproducing_the_constant": matching,
            "chain_is_end_to_end": len(matching) == 1,
            "n_arms": len(arms),
            "⚠": ("EXACTLY ONE arm may reproduce the constant. Zero means the committed constant has no "
                  "committed primary output after all; more than one means the constant does not identify "
                  "a run, and every sentence that cites it is ambiguous about which."),
        },
    }
    return doc


def main(argv):
    doc = build()
    js = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv:
        try:
            have = open(OUT, encoding="utf-8").read()
        except OSError:
            print("decoy_null_provenance --check FAILED: %s is MISSING" % os.path.relpath(OUT, ROOT))
            return 1
        if have != js:
            print("decoy_null_provenance --check FAILED: %s has DRIFTED -- regenerate it"
                  % os.path.relpath(OUT, ROOT))
            return 1
        print("decoy_null_provenance --check: OK (chain_is_end_to_end=%s)"
              % doc["_derived"]["chain_is_end_to_end"])
        return 0
    open(OUT, "w", encoding="utf-8").write(js)
    print(json.dumps(doc["_derived"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
