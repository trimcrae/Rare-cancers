#!/usr/bin/env python3
"""Build a paper's aiXiv submission metadata FROM the manuscript, so the two cannot disagree.

⛔ WHY A GENERATOR RATHER THAN A HAND-WRITTEN JSON. The metadata is what a third party publishes as
the version of record; the manuscript is what a reader is told. Retyping a title or an abstract into
a submission form is a number typed twice (CLAUDE.md §1), and the drift is invisible until someone
reads both.

⚠ THE MARKDOWN-TO-PLAIN-TEXT TRANSFORM IS THE PART THAT ACTUALLY BREAKS, and it broke twice on the
first attempt (2026-08-22, caught in a dry run before any submission):

  * Stripping a citation marker `[9]` left the space in front of it -> "resected melanoma , which".
  * The manuscript escapes HLA asterisks as `HLA-B\\*15:01`. Removing markdown emphasis by deleting
    `*` took the asterisk and left the backslash -> "HLA-B\\15:01", a corrupted allele name in the
    published abstract of a paper whose subject IS allele coverage.

⛔ SO EMPHASIS IS UNWRAPPED, NEVER DELETED, AND ESCAPES ARE RESOLVED FIRST. The order below is
load-bearing; `tests/test_vaccine_path_aixiv_metadata.py` asserts the OUTPUT PROPERTIES (no residual
markers, no stray backslash, no doubled space) rather than re-running this same regex, because a test
that re-implements the transform validates nothing about it.

    python3 research/manuscripts/build_aixiv_metadata.py --paper vaccine-path
    python3 research/manuscripts/build_aixiv_metadata.py --paper vaccine-path --check
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PAPERS = {
    "vaccine-path": {
        "manuscript": "neoantigen/emc-vaccine-development-path.md",
        "out": "neoantigen/emc-vaccine-path-aixiv-metadata.json",
        # ⚠ Fields aiXiv cannot derive from the prose. Everything else is READ from the manuscript.
        "authorship_type": "human",
        "authors": ["Tristan D. McRae"],
        "corresponding_author": "trimcrae@gmail.com",
        # ⛔ EXACTLY THREE, AND THEY ARE A PATH THROUGH aiXiv'S OWN TREE, NOT FREE TEXT.
        # `POST /api/agent/submit` answered a two-element list with HTTP 400:
        # "category must be a list of exactly 3 strings: [main_category, subcategory,
        # specialization]" (run 32584081278). The tree is served unauthenticated at
        # /api/categories and captured in literature/aixiv-live-stats-2026-08-22/; it has no
        # "Cancer Biology" node, so the earlier ["Life Sciences", "Cancer Biology"] was wrong on
        # both counts. This paper's claims are epitope presentation and allele coverage, which is
        # where Immunology sits; the methods are computational but the conclusions are immunological.
        "category": ["Natural Sciences", "Biology", "Immunology"],
        "keywords": ["extraskeletal myxoid chondrosarcoma", "EWSR1::NR4A3", "fusion neoantigen",
                     "cancer vaccine", "HLA coverage", "rare sarcoma"],
        "license": "CC-BY-4.0",
        "doc_type": "paper",
        "submitter_type": "agent",
    },
}


def markdown_to_plain(md):
    """Unwrap markdown emphasis and drop citation markers, without eating the text underneath."""
    # 1. Resolve backslash escapes FIRST, parking the character so emphasis handling cannot see it.
    #    `\*` in the source is a literal asterisk (an HLA allele), not an emphasis delimiter.
    md = md.replace(r"\*", "\x00").replace(r"\_", "\x01").replace(r"\[", "\x02")
    # 2. Unwrap emphasis by keeping the captured group — never a bare deletion of the delimiter.
    for pat in (r"\*\*\*(.+?)\*\*\*", r"\*\*(.+?)\*\*", r"\*(.+?)\*", r"`(.+?)`"):
        md = re.sub(pat, r"\1", md, flags=re.S)
    # 3. Citation markers, WITH any whitespace in front, so no orphaned space is left behind.
    md = re.sub(r"[ \t]*\[[0-9]+(?:[,\-–][0-9]+)*\]", "", md)
    # 4. Restore the parked literals and normalise runs of whitespace.
    md = md.replace("\x00", "*").replace("\x01", "_").replace("\x02", "[")
    md = re.sub(r"\s+", " ", md)
    return re.sub(r"\s+([,.;:])", r"\1", md).strip()


def build(paper):
    spec = PAPERS[paper]
    path = os.path.join(HERE, spec["manuscript"])
    with open(path) as fh:
        lines = fh.read().split("\n")

    titles = [l for l in lines if l.startswith("# ")]
    if not titles:
        raise SystemExit(f"{spec['manuscript']}: no level-1 heading to take a title from")
    title = markdown_to_plain(titles[0][2:])

    try:
        i = lines.index("## Abstract")
    except ValueError:
        raise SystemExit(f"{spec['manuscript']}: no '## Abstract' section")
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
    abstract = markdown_to_plain(" ".join(x for x in lines[i + 1:j] if x.strip()))

    meta = {k: v for k, v in spec.items() if k not in ("manuscript", "out")}
    meta["title"] = title
    meta["abstract"] = abstract
    return meta, os.path.join(HERE, spec["out"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(PAPERS), required=True)
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed file differs from what this would write")
    args = ap.parse_args(argv)

    meta, out = build(args.paper)
    rendered = json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.check:
        if not os.path.exists(out):
            print(f"{out} does not exist", file=sys.stderr)
            return 1
        with open(out) as fh:
            if fh.read() != rendered:
                print(f"{out} is STALE — rerun without --check", file=sys.stderr)
                return 1
        print(f"{os.path.basename(out)}: up to date")
        return 0
    with open(out, "w") as fh:
        fh.write(rendered)
    print(f"wrote {out} ({len(meta['abstract'])} abstract chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
