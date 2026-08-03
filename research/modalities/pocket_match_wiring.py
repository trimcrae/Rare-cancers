#!/usr/bin/env python3
"""Which fpocket lanes actually SAY which site-identity rule they used — a live census, not a memory.

★★ WHY THIS EXISTS (2026-08-03, out of the `R3` generation-frame audit).

`pocket_tracking.match_mode()` reads `POCKET_MATCH` and **defaults to LEGACY** — the retired,
outcome-selected site rule (pick the highest-**druggability** cavity in a window that is essentially the
whole LBD) that the harmonized tracker was built to replace. That default is invisible: a workflow that
sets nothing produces a manifest that LOOKS like every other manifest and carries a number nobody can
attribute to a rule.

It has already cost the program its most load-bearing structure. `release-druggable-aws.yml` set no
`POCKET_MATCH`, so STEP 0 selected the generation receptor's site under LEGACY and recorded **0.667** on
2026-06-29. The same PDB, scored under the harmonized rule with the same pinned fpocket, is **0.259** —
below D* = 0.53 (`r3-generation-frame-harmonized.json`). Under CLAUDE.md §4 that is the *populated field
that was never measured* failure: the record's PRESENCE was mistaken for its provenance.

⚠ AND IT WAS NEVER ONE WORKFLOW. Five lanes run code that calls `match_mode()`; the audit that found the
first one found four more with exactly the same silence. So the fix cannot be a one-line edit plus a
memory — it needs something that FAILS when a sixth appears. That is this module plus
`tests/test_pocket_match_wiring.py`.

WHAT THIS IS NOT. It is not an exemption list, and it must never become one. `WIRED_REQUIRED` names the
lanes whose wiring is *asserted*; every other lane is reported as `unwired` with its reason, and the test
pins the unwired SET exactly — so an unwired lane that gets fixed, or a new one that appears, both turn
the test red and force a deliberate edit. A silent baseline bump is the failure this replaces.

Pure-stdlib, no fpocket, no network: it reads workflow YAML as text and the entry/submitter scripts as
text, because the question is literally "does this string appear on this path".
"""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")

MATCH_ENV = "POCKET_MATCH"

# The lanes whose chain reaches `pocket_tracking.match_mode()`. `driver` is the module that calls it;
# `chain` are every file the rule must survive between the workflow and that driver — a workflow that sets
# the env is worthless if the SageMaker entry script does not forward it into the child process, which is
# precisely the shape of this bug.
LANES = {
    "release-druggable-aws.yml": {
        "driver": "nr4a3_release_druggable.py",
        "chain": ["research/modalities/nr4a3_release_druggable_sagemaker.py",
                  "research/modalities/sagemaker_src/entry_release_druggable.py"],
        "why_it_matters": ("STEP 0 — writes the manifest naming the receptor `denovo_401` was generated "
                           "into. This is the lane that produced the 0.667/0.259 discrepancy."),
    },
    "gpu-mdpocket-aws.yml": {
        "driver": "nr4a3_mdpocket.py",
        "chain": ["research/modalities/sagemaker_src/entry_mdpocket.py"],
        "why_it_matters": ("per-frame release druggability — the CANDIDATE POOL STEP 0 selects from, so a "
                           "legacy pool can hand a harmonized selector the wrong frames"),
    },
    "gpu-calibration-aws.yml": {
        "driver": "nr4a3_calibration.py",
        "chain": ["research/modalities/sagemaker_src/entry_calibration.py"],
        "why_it_matters": "the drug-bound calibration band that D* = 0.53 itself is derived from",
    },
    "gpu-8xtt-benchmark-aws.yml": {
        "driver": "nr4a3_8xtt_benchmark.py",
        "chain": ["research/modalities/sagemaker_src/entry_8xtt.py"],
        "why_it_matters": "the crystal-anchored benchmark the detector is validated against",
    },
    "fpocket-enumerate-aws.yml": {
        "driver": "nr4a3_fpocket_enumerate.py",
        "chain": ["research/modalities/sagemaker_src/entry_fpocket.py"],
        "why_it_matters": "the af2_static row of the committed harmonized table",
    },
    "metad-replica-pocket-aws.yml": {
        "driver": "nr4a3_mdpocket.py",
        "chain": ["research/modalities/sagemaker_src/entry_metad_replica_pocket.py"],
        "why_it_matters": "the biased metadynamics ensemble rows",
    },
    "gpu-pocket-reharmonize-aws.yml": {
        "driver": "nr4a3_pocket_reharmonize.py",
        "chain": ["research/modalities/sagemaker_src/entry_pocket_reharmonize.py"],
        "why_it_matters": "the harmonized rerun itself — the table every other row is compared against",
    },
    "r3-generation-frame-audit.yml": {
        "driver": "r3_score_generation_frame.py",
        "chain": [],
        "why_it_matters": ("the Gate-A score of the generation receptor; its driver ALSO hard-aborts "
                           "unless the mode is harmonized, which is the strongest form of this guard"),
    },
}

# Lanes whose wiring is ASSERTED by the test. Adding a lane here without wiring it turns the test red.
WIRED_REQUIRED = ("release-druggable-aws.yml", "r3-generation-frame-audit.yml",
                  "gpu-pocket-reharmonize-aws.yml", "metad-replica-pocket-aws.yml")

# ⛔ THE OPEN DEFECT, NAMED. These four lanes still run LEGACY-by-default. They are recorded — not
# exempted — because they belong to other lanes' owners and silently rewiring a lane whose artifacts are
# already published would change what a committed number MEANS without anybody deciding to. The test pins
# this set EXACTLY: fixing one, or gaining a fifth, both go red.
KNOWN_UNWIRED = ("fpocket-enumerate-aws.yml", "gpu-8xtt-benchmark-aws.yml",
                 "gpu-calibration-aws.yml", "gpu-mdpocket-aws.yml")


def _read(path):
    try:
        with open(os.path.join(REPO, path)) as fh:
            return fh.read()
    except OSError:
        return None


def mentions_match_env(text, env=MATCH_ENV):
    """Does this file reference the site-rule env var at all? PURE.

    Deliberately a substring test rather than a YAML parse: the variable can arrive as a job `env:`, a
    step `env:`, an `-e` docker flag, an argparse dest, or an `os.environ` write, and every one of those
    counts. A parser that understood only one shape would report a wired lane as unwired."""
    return bool(text) and env in text


def lane_status(name, spec, reader=_read):
    """One lane's wiring status. `missing_files` is reported, never assumed to mean 'unwired' —
    CLAUDE.md §4: an absent reading is not a reading of absence."""
    wf = reader(os.path.join(".github", "workflows", name))
    driver = reader(os.path.join("research", "modalities", spec["driver"]))
    missing = []
    if wf is None:
        missing.append(f".github/workflows/{name}")
    if driver is None:
        missing.append(f"research/modalities/{spec['driver']}")
    chain = {}
    for path in spec["chain"]:
        text = reader(path)
        if text is None:
            missing.append(path)
        chain[path] = mentions_match_env(text)
    wf_sets = mentions_match_env(wf)
    chain_ok = all(chain.values()) if chain else True
    return {
        "lane": name,
        "driver": spec["driver"],
        "why_it_matters": spec["why_it_matters"],
        "workflow_sets_pocket_match": wf_sets,
        "chain_forwards_pocket_match": chain,
        "chain_complete": chain_ok,
        "wired": bool(wf_sets and chain_ok),
        "missing_files": missing,
        "defaults_to_retired_legacy_rule": not bool(wf_sets and chain_ok),
    }


def census(lanes=None, reader=_read):
    """Every lane's status + the two lists the test pins. PURE given `reader`."""
    lanes = LANES if lanes is None else lanes
    rows = [lane_status(n, s, reader=reader) for n, s in sorted(lanes.items())]
    return {
        "_what": ("which fpocket lanes state their site-identity rule. `pocket_tracking.match_mode()` "
                  "defaults to LEGACY, so an unwired lane silently scores under the RETIRED "
                  "outcome-selected rule and its manifest cannot be attributed to a rule."),
        "env": MATCH_ENV,
        "n_lanes": len(rows),
        "rows": rows,
        "wired": sorted(r["lane"] for r in rows if r["wired"]),
        "unwired": sorted(r["lane"] for r in rows if not r["wired"]),
    }


def format_census(c):
    out = [f"{c['n_lanes']} lanes reach pocket_tracking.match_mode(); {MATCH_ENV} default = LEGACY",
           f"  wired   ({len(c['wired'])}): " + (", ".join(c["wired"]) or "—"),
           f"  UNWIRED ({len(c['unwired'])}): " + (", ".join(c["unwired"]) or "—")]
    for r in c["rows"]:
        if not r["wired"]:
            out.append(f"    ⛔ {r['lane']} -> {r['driver']} — {r['why_it_matters']}")
    return "\n".join(out)


if __name__ == "__main__":
    import json
    import sys
    c = census()
    print(format_census(c))
    if "--json" in sys.argv:
        print(json.dumps(c, indent=2))
