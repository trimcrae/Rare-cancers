#!/usr/bin/env python3
"""Assert that the two copies of the draft FET-fusion notice have not drifted apart.

WHY THIS EXISTS. `fet-fusion-trial-eligibility-notice.md` carries the draft notice TWICE, and it
has to:

  * section 4 is the copy a future session reads and edits;
  * the copy inside section 5's fenced reviewer block is the ONLY thing the reviewer sees, because
    CLAUDE.md section 3 requires that block to be self-contained and copyable.

That duplication is deliberate and is also a hazard. If section 4 is edited and the block is not,
the review comes back against text that is no longer the draft — and the resulting approval would
attach to a version nobody reviewed, on a document written for patients. The memo states the rule
in prose ("if section 4 changes, the block's copy changes in the same commit"), and this repository
has learned repeatedly that a property asserted in prose about something a human has to remember is
a hope rather than a property (CLAUDE.md section 6, the exempt-census-lane wiring test).

So the rule is executable. The two copies are two RENDERINGS of one text — one markdown, one plain
— so they are compared on words with emphasis markup, list bullets, smart punctuation and trailing
punctuation normalised away. Anything that changes the words fails.

Pure stdlib. Usage:

    python3 research/manuscripts/fet_notice_sync_check.py     # exit 0 in sync, 1 on drift
"""
import difflib
import os
import re
import sys

DOC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "fusion-direct", "fet-fusion-trial-eligibility-notice.md")

# The draft's first line and its sign-off. Both copies must contain both, exactly twice in total.
START = "If you have extraskeletal myxoid chondrosarcoma"
END = "Registry readings taken"


def normalise(text):
    """Words only: markup, bullets and punctuation style are rendering, not content."""
    text = re.sub(r"[*_`>#]", " ", text)
    text = (text.replace("…", "...").replace("—", "-").replace("–", "-")
                .replace("“", '"').replace("”", '"').replace("’", "'"))
    text = re.sub(r"^\s*[\*\-]\s*", " ", text, flags=re.M)
    words = (w.strip(".,;:()\"'") for w in re.split(r"\s+", text.lower()))
    return [w for w in words if w]


def extract(doc_text):
    starts = [m.start() for m in re.finditer(re.escape(START), doc_text)]
    if len(starts) != 2:
        raise SystemExit(
            f"fet_notice_sync_check: expected exactly 2 copies of the draft "
            f"(section 4 and the reviewer block), found {len(starts)}. Either a copy was deleted "
            f"or a third was added; both are drift.")
    out = []
    for s in starts:
        tail = doc_text[s:]
        if END not in tail:
            raise SystemExit("fet_notice_sync_check: a copy of the draft has no "
                             f"'{END}' sign-off, so its extent cannot be determined.")
        out.append(tail.split(END)[0])
    return out


def main():
    with open(DOC, encoding="utf-8") as fh:
        doc_text = fh.read()
    section4, block = (normalise(t) for t in extract(doc_text))
    if section4 == block:
        print(f"fet_notice_sync_check: OK - section 4 and the reviewer block agree "
              f"({len(section4)} words)")
        return 0
    print(f"fet_notice_sync_check: DRIFT - section 4 has {len(section4)} words, the reviewer "
          f"block has {len(block)}. The reviewer would review text that is not the draft.")
    diff = list(difflib.unified_diff(section4, block, "section-4", "reviewer-block", n=2))
    for line in diff[:80]:
        print("   " + line.rstrip())
    if len(diff) > 80:
        print(f"   ... {len(diff) - 80} more diff lines")
    return 1


if __name__ == "__main__":
    sys.exit(main())
