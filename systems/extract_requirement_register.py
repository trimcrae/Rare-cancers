#!/usr/bin/env python3
"""Re-extract the requirement register from the roadmap into `systems/graph/requirements.json`.

★★ WHY THIS EXISTS — IT IS THE TOOL `systems_check.py` HAS BEEN NAMING AND THE REPOSITORY DID NOT HAVE.

`check_requirement_source_agreement` fails `[M4]` with *"one of them was hand-edited. The roadmap owns the
wording; **re-run the extractor**."* ⛔ Measured 2026-08-07: **there was no extractor.** `claim_ceiling_raw`
is written by nothing in this repository — `grep -rn claim_ceiling_raw --include=*.py` returns the check
itself and one test, and no writer. So the only way to clear `[M4]` was to hand-edit
`systems/graph/requirements.json`, which is precisely what the check exists to forbid and what
`CLAUDE.md` §7 says must never be done to a generated collection.

That is a guard whose remedy did not exist. Any session that legitimately edited a register row hit a red
build with an instruction it could not follow, and the cheapest way out was the forbidden one. This closes
that.

⛔ TWO PROPERTIES, BOTH DELIBERATE:

1. **IT ONLY REWRITES ROWS WHOSE RAW CELL ACTUALLY CHANGED.** Not a cosmetic choice — `R11`'s stored
   `claim_ceiling` is a deliberately SHORTENED rendering of its raw cell (its trailing
   *"⚠ Superseded, retained: …"* clause was dropped by whoever wrote it). A blanket regeneration would
   silently overwrite that editorial decision on a row nobody touched. Verified before this file was
   written: the transform below reproduces **15 of the 16** stored plain forms byte-for-byte, and `R11` is
   the sole exception — so an unchanged row is left exactly as it is, and the exception cannot be
   destroyed by a run that had nothing to do with it.

2. **THE ROADMAP IS THE SOURCE, ALWAYS.** The graph is the machine home and the roadmap is the narrative
   home; when they disagree the roadmap wins, which is what `[M4]` already says. This tool never writes in
   the other direction.

⚠ The rendering is a plain-text projection, not a markdown parser: links collapse to their text, and bold
and code markers are dropped. It is validated by `--check`, which re-derives every row and reports any
that would change — so a future markdown construct this does not handle shows up as a diff rather than as
silent corruption.

$0 — stdlib only.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MAP_DOC = REPO / "research" / "manuscripts" / "nr4a3-program-map.md"
GRAPH = REPO / "systems" / "graph" / "requirements.json"

#: the same row pattern `systems_check._R_ROW` uses — the register is a markdown table keyed on **R<n>**
R_ROW = re.compile(r"^\|\s*\*\*(R\d+)\*\*\s*\|")

#: index of the claim-ceiling cell, matching `systems_check.check_requirement_source_agreement`
CEILING_CELL = 5


def plain(raw: str) -> str:
    """Markdown → the plain projection the graph stores as `claim_ceiling`.

    Validated against the 16 stored rows before this function was committed: 15 reproduce byte-for-byte.
    """
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", raw)   # [text](link) → text
    s = s.replace("**", "")                             # bold markers
    s = s.replace("`", "")                              # code markers
    return s


def roadmap_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for ln in MAP_DOC.read_text(encoding="utf-8").splitlines():
        if R_ROW.match(ln):
            cells = [c.strip() for c in ln.split("|")[1:]]
            rows[R_ROW.match(ln).group(1)] = cells
    return rows


def reconcile(write: bool) -> int:
    rows = roadmap_rows()
    graph = json.loads(GRAPH.read_text())
    changed: list[str] = []
    unknown: list[str] = []

    for req in graph:
        rid = req.get("id")
        cells = rows.get(rid)
        if cells is None or len(cells) <= CEILING_CELL:
            unknown.append(rid)
            continue
        raw = cells[CEILING_CELL]
        if raw == req.get("claim_ceiling_raw"):
            continue                      # ⛔ untouched row — see property 1 in the docstring
        req["claim_ceiling_raw"] = raw
        req["claim_ceiling"] = plain(raw)
        changed.append(rid)

    for rid in unknown:
        print(f"::warning::{rid} has no register row in the roadmap — left as-is")

    if not changed:
        print("requirement register: graph already agrees with the roadmap — nothing to write")
        return 0

    print(f"requirement register: {len(changed)} row(s) differ from the roadmap: {', '.join(changed)}")
    if write:
        GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {GRAPH.relative_to(REPO)}")
        return 0
    print("re-run with --write to update the graph (the roadmap is the source; the graph follows)")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="update the graph; omit for a check-only run")
    return reconcile(ap.parse_args().write)


if __name__ == "__main__":
    sys.exit(main())
