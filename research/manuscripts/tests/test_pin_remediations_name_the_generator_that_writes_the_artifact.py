"""⛔ A PIN'S `regenerate` LINE IS AN INSTRUCTION FOLLOWED UNDER A RED GATE, NOT DECORATION.

`lint_consistency.py` prints `regenerate` as the second line of every finding, so it is the command
a maintainer runs when a pinned figure has drifted. If it names a generator that does not write the
artifact the pin reads, running it changes nothing, the gate stays red, and the obvious next move is
to retype the artifact's value into the prose by hand — which is precisely the ONE FACT, ONE PLACE
violation the pin exists to prevent.

⛔ WHY THIS EXISTS (round 14, 2026-08-22). Fifteen pins were registered against the journal article
by copying the `aso-parent-gap-pairing.json` block and repointing `artifact`, `key` and `context`.
Nine of the fifteen kept the source block's `regenerate` line, so five pins on `aso-parent-null.json`,
two on `nr4a3-fusion-junction-atlas.json` and two on `fusion-junction-aso-reagent-coverage.json` all
instructed the reader to run `aso_parent_gap_pairing.py`. Demonstrated live: under a genuine
`A-figure-not-stated` on `aso_reagent_coverage_with_third_design_journal`, the printed command does
not touch the coverage artifact at all. Their extended-report twins — six lines away in the same
file — every one named the right generator. One-of-a-pair, in the remediation text.

⚠ THE CHECK IS THE OBVIOUS ONE AND THAT IS THE POINT: does the named script mention the artifact it
claims to produce? Nothing subtler is needed, and nothing subtler was being done.
"""
from __future__ import annotations

import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PINS = os.path.join(REPO, "research", "manuscripts", "pinned-figures.json")

#: Only a `python3 <path>` command is claimed to be THE regenerating command. A `regenerate` that
#: says `bash scripts/regenerate_endpoint_chain.sh (and endpoint_corpus.py --extract if …)` names a
#: chain script as the command and a helper parenthetically; binding the parenthetical would be
#: reading the sentence wrong.
_COMMAND = re.compile(r"python3 ([\w./-]+\.py)")


def _pins():
    return json.load(io.open(PINS, encoding="utf-8"))["artifact_figures"]


def test_every_regenerate_command_names_a_script_that_exists():
    missing = []
    for pin in _pins():
        m = _COMMAND.search(pin.get("regenerate") or "")
        if m and not os.path.exists(os.path.join(REPO, m.group(1))):
            missing.append(f"{pin['id']}: regenerate says `python3 {m.group(1)}`, which is not a file")
    assert not missing, (
        "a pin's remediation names a script that does not exist, so a maintainer under a red gate "
        "has nothing to run:\n  " + "\n  ".join(missing))


def test_every_regenerate_command_names_the_generator_that_writes_the_pinned_artifact():
    wrong = []
    for pin in _pins():
        m = _COMMAND.search(pin.get("regenerate") or "")
        if not m:
            continue
        script = os.path.join(REPO, m.group(1))
        if not os.path.exists(script):
            continue  # reported by the test above
        artifact = os.path.basename(pin["artifact"])
        if artifact not in io.open(script, encoding="utf-8", errors="replace").read():
            wrong.append(f"{pin['id']}: reads {artifact} but tells you to run {m.group(1)}, "
                         "which never names that file")
    assert not wrong, (
        "a pin's remediation names a generator that does not write the artifact the pin reads. "
        "Running it leaves the gate red and invites retyping the value by hand:\n  "
        + "\n  ".join(wrong))
