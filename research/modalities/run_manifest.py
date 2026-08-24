#!/usr/bin/env python3
"""Which artifacts did THIS run actually write? Print it, and publish it beside the results.

⛔ WHY THIS EXISTS. Every compute step in `modalities-run.yml` is `continue-on-error: true`, which is
deliberate — one generator failing must not stop the other twenty. The cost is that a step which
CRASHES still shows a green tick, and the only signal is an artifact that is missing or stale on the
cache branch. Measured 2026-08-23, run 32656882121: `junction_transcript_sensitivity.py` ran 565 s,
raised, wrote nothing, and the step reported success. Four unrelated files were published and nothing
anywhere said the analysis had failed. It was found by noticing the file absent from the branch.

⚠ THIS DOES NOT FAIL THE RUN, AND THAT IS NOT TIMIDITY. Failing would break the very property the
continue-on-error design buys. What it does instead is make the failure IMPOSSIBLE TO MISS: an
`::error` annotation per missing artifact, a summary line, and a committed `run-manifest.json` so the
published record itself says which generators produced output on this run and which did not.

⛔ MTIME, NOT EXISTENCE. A file left over from a previous run exists. The question this answers is
whether THIS run wrote it, so every artifact is compared against the run's own start time; anything
older is reported as STALE, which is the same defect wearing a different mask.

Usage: run_manifest.py <epoch-seconds-of-run-start>
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

#: Artifacts the vaccine and degrader lanes depend on. A generator whose output is not listed here is
#: not watched — add it in the same commit that adds the step, or the step joins the silent ones.
EXPECTED = [
    "fusion-breakpoint-neoantigens.json", "hla-coverage.json", "epitope-allele-matrix.json",
    "coverage-curve.json", "coverage-threshold-curve.json", "epitope-allele-loose-matrix.json",
    "epitope-allele-matrix-mhcnuggets.json", "predictor-concordance.json",
    "junction-proteome-novelty.json", "junction-selfsimilarity.json",
    "junction-frameshift-peptides.json", "junction-transcript-sensitivity.json",
    "coverage-uncertainty.json", "novelty-seam-test.json",
    "patient-cd4-demo.json", "vaccine-construct.json",
]


def main(argv):
    started = float(argv[0]) if argv else 0.0
    rows, missing, stale, failed = [], [], [], []
    for name in EXPECTED:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            rows.append({"artifact": name, "state": "MISSING"})
            missing.append(name)
            continue
        mtime = os.path.getmtime(path)
        fresh = mtime >= started
        state = "written" if fresh else "STALE"
        # ⚠ A generator that wrote a WITHDRAWAL is fresh but carries no result — a third state, and
        # collapsing it into "written" would report a failure as a success.
        try:
            with open(path) as fh:
                head = json.load(fh)
            if isinstance(head, dict) and any(k.startswith("⛔_STATUS") for k in head):
                state = "FAILED (artifact carries a withdrawal)"
                failed.append(name)
        except (OSError, ValueError) as e:
            state = f"UNREADABLE: {e}"
            failed.append(name)
        rows.append({"artifact": name, "state": state,
                     "age_s_at_check": round(time.time() - mtime, 1)})
        if not fresh and state == "STALE":
            stale.append(name)

    for name in missing:
        print(f"::error::{name} was NOT written by this run — its generator failed silently "
              f"(the step is continue-on-error, so it reported success)")
    for name in stale:
        print(f"::error::{name} is STALE — it predates this run, so this run's copy is a leftover")
    for name in failed:
        print(f"::error::{name} carries a withdrawal or is unreadable — the generator ran and failed")

    ok = len(EXPECTED) - len(missing) - len(stale) - len(failed)
    manifest = {
        "_what": ("Which expected artifacts THIS run wrote. Every compute step in the workflow is "
                  "continue-on-error, so a green step is not evidence its generator produced "
                  "anything; this is."),
        "run_started_epoch": started,
        "n_expected": len(EXPECTED), "n_written": ok,
        "missing": missing, "stale": stale, "failed": failed,
        "artifacts": rows,
    }
    json.dump(manifest, open(os.path.join(HERE, "run-manifest.json"), "w"), indent=2)
    print(f"  run manifest: {ok}/{len(EXPECTED)} written this run; "
          f"{len(missing)} missing, {len(stale)} stale, {len(failed)} failed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
