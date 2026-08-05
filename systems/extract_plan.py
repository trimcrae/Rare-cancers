#!/usr/bin/env python3
"""One-time: lift THE ORDERED PLAN + the money/ladder/spine block into systems/graph/plan.json.

LOSSLESS BY CONSTRUCTION AND PROVEN BY ROUND TRIP. Every line is stored either as a verbatim raw
block or as an item whose marker is the ONLY thing pulled out into a field. Rendering concatenates
them back; the script refuses to write unless the render is byte-identical to the source slice.

Why the marker specifically: it is the one thing that must be machine-settable, because once the
view is generated, ticking an item happens here rather than in the Markdown.
"""
import json
import re

SRC = "research/manuscripts/nr4a3-program-map.md"
OUT = "systems/graph/plan.json"

# Two contiguous blocks. Bounds are resolved from headings, never hardcoded, so an edit above
# them cannot silently shift what gets moved.
BLOCK_STARTS = ['THE ORDERED PLAN (spend-gated)', '11 · Money, authorization and gates']
BLOCK_ENDS = ['★★ WHAT THE LANDED RESULTS CHANGE', '12 · Findings that belong to other documents']

SEC = re.compile(r'^##\s+(.*)$')
SUB = re.compile(r'^###\s+(.*)$')
ITEM = re.compile(r'^(\s*)- \*\*`\[([ x~!–-])\]`(.*)$', re.S)


def slice_bounds(lines):
    heads = [(i, SEC.match(l).group(1)) for i, l in enumerate(lines) if SEC.match(l)]
    out = []
    for s, e in zip(BLOCK_STARTS, BLOCK_ENDS):
        i = next(i for i, h in heads if h.startswith(s))
        j = next(i2 for i2, h in heads if h.startswith(e))
        out.append((i, j))
    return out


def main():
    with open(SRC, encoding="utf-8") as fh:
        lines = fh.readlines()
    bounds = slice_bounds(lines)

    blocks, items, n = [], 0, 0
    for bi, (start, end) in enumerate(bounds):
        rung = None
        buf = []
        for ln in lines[start:end]:
            if SUB.match(ln):
                rung = SUB.match(ln).group(1).strip()
            m = ITEM.match(ln)
            if m:
                if buf:
                    blocks.append({"kind": "raw", "text": "".join(buf)})
                    buf = []
                n += 1
                blocks.append({
                    "kind": "item",
                    "id": f"PI-{n:03d}",
                    "block": bi,
                    "rung": rung,
                    "indent": m.group(1),
                    "marker": m.group(2),
                    "text": m.group(3),
                })
                items += 1
            else:
                buf.append(ln)
        if buf:
            blocks.append({"kind": "raw", "text": "".join(buf)})
        blocks.append({"kind": "block_end", "block": bi})

    doc = {
        "_schema": "emc-plan/1",
        "_role": ("THE ORDERED PLAN and the money/ladder/spine block, lifted out of the roadmap. "
                  "THIS FILE IS THE SOURCE: systems/views/plan.md is generated from it and a hand-edit "
                  "to the view fails the build. Ticking an item happens HERE."),
        "_lossless": ("Every line is a verbatim `raw` block or an `item` whose ONLY extracted field is "
                      "its marker. The extractor refuses to write unless rendering reproduces the source "
                      "slice byte for byte."),
        "_marker_note": ("⚠ THE SKIPPED MARKER IS AN EN DASH (U+2013), NOT AN ASCII HYPHEN. Matching "
                         "only `-` reclassifies every skipped item as pending and fills the board with "
                         "work nobody owes."),
        "_notation_note": ("⛔ `Cum. ~$N` (the ordered plan) and `Cum ~$N` (the dependency spine) are "
                           "DELIBERATELY different and must both stay in this one file. "
                           "pinned-figures.json `subset_checks/strategy_spine_cum` asserts the second is a "
                           "subset of the first WITHIN A SINGLE FILE, so separating them breaks it as "
                           "'pattern found nothing' — which reads like a broken regex, not a broken move."),
        "blocks": blocks,
    }

    rendered = render(doc)
    original = "".join(lines[bounds[0][0]:bounds[0][1]]) + "".join(lines[bounds[1][0]:bounds[1][1]])
    if rendered != original:
        import difflib
        d = list(difflib.unified_diff(original.splitlines(), rendered.splitlines(), lineterm="", n=1))
        raise SystemExit("ROUND TRIP FAILED — refusing to write.\n" + "\n".join(d[:40]))

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    from collections import Counter
    marks = Counter(b["marker"] for b in blocks if b["kind"] == "item")
    print(f"round trip: BYTE-IDENTICAL ({len(original)} chars)")
    print(f"blocks: {len(blocks)} | items: {items} | markers: {dict(marks)}")
    print(f"rungs: {sorted({b['rung'] for b in blocks if b['kind']=='item' and b['rung']})}")


def render(doc):
    out = []
    for b in doc["blocks"]:
        if b["kind"] == "raw":
            out.append(b["text"])
        elif b["kind"] == "item":
            out.append(f"{b['indent']}- **`[{b['marker']}]`{b['text']}")
    return "".join(out)


if __name__ == "__main__":
    main()
