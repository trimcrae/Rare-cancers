#!/usr/bin/env python3
"""Salvage a TRUNCATED JSON artifact — recover every complete value, and say loudly that it is partial.

★ WHY THIS EXISTS, MEASURED (run 30778084770 -> commit `e02aaf7d1`, `nr4a3-5bt-frame.json`).
`json.dump(doc, open(path, "w"))` STREAMS. When it reached a value it could not serialise — a raw RDKit
`Chem.Mol` parked under `_mol` — it had already written 16 642 bytes of real content, and it raised with the
file open. The workflow's `if: always()` publish step then committed that file. The result is the worst
shape an artifact can have: **it looks committed and it does not parse**, so every reader either crashes with
a `JSONDecodeError` that names no cause, or (worse) treats the whole thing as absent.

⛔ THE FIX FOR THE *CAUSE* IS `nr4a3_5bt_assemble.write_json`, not this file — it refuses unserialisable
values, serialises to a string before opening anything, and replaces atomically. This module exists for the
artifacts that were ALREADY written broken and whose content is real: the bytes before the truncation point
were produced by the real run and are the only surviving record of it.

⛔ WHAT THIS IS NOT ALLOWED TO DO. It never invents, completes or infers a value. It cuts back to the last
position at which the document was complete, closes the containers that were open there, and records exactly
what it dropped. A key that was mid-write is DROPPED and NAMED — never filled with a plausible default,
because a populated field that no run produced is the more dangerous failure (CLAUDE.md §4).
"""
from __future__ import annotations

import json

#: Characters that can legally end a JSON value.
_VALUE_ENDERS = set('"}]0123456789eltn')          # string/obj/array close, digits, true/false/null tails


def scan(text):
    """`(stack, cuts)` for `text`, where `stack` is the container nesting at EOF and `cuts` is every index
    (exclusive) at which the document was one-closer-away from complete: i.e. just past a finished value,
    outside any string.

    Pure, single pass, no regex — a regex over JSON is how a string containing `}` becomes a cut point.
    """
    stack, cuts = [], []
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
                cuts.append((i + 1, tuple(stack)))
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack:
                stack.pop()
            cuts.append((i + 1, tuple(stack)))
        elif ch in _VALUE_ENDERS and (i + 1 == len(text) or text[i + 1] in " \t\r\n,}]"):
            cuts.append((i + 1, tuple(stack)))
    return stack, cuts


def salvage(text):
    """`(doc, report)` — the largest prefix of `text` that closes into valid JSON, plus what was dropped.

    Raises `ValueError` if `text` parses as it stands (nothing to salvage — say so rather than rewrite a
    healthy file) or if no prefix can be recovered at all.
    """
    try:
        json.loads(text)
    except ValueError:
        pass
    else:
        raise ValueError("this document already parses — there is nothing to salvage")

    _stack, cuts = scan(text)
    for cut, open_at_cut in reversed(cuts):
        prefix = text[:cut]
        candidate = prefix + "".join(reversed(open_at_cut))
        try:
            doc = json.loads(candidate)
        except ValueError:
            continue
        dropped = text[cut:]
        return doc, {"recovered_bytes": cut,
                     "total_bytes": len(text),
                     "dropped_bytes": len(text) - cut,
                     "dropped_tail_verbatim": dropped,
                     "closers_added": "".join(reversed(open_at_cut))}
    raise ValueError("no prefix of this document closes into valid JSON — nothing is recoverable")


def _main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    ap.add_argument("--out", default=None, help="write the salvaged document here (default: stdout report)")
    a = ap.parse_args(argv)
    raw = open(a.path, encoding="utf-8").read()
    doc, rep = salvage(raw)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
