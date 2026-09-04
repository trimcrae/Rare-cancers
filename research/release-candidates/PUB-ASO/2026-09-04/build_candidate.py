#!/usr/bin/env python3
"""Build this unsubmitted candidate with the repository's unchanged NAT geometry.

Requires Python, pypdf and Chromium. Run from anywhere within this checkout:
  python research/release-candidates/PUB-ASO/2026-09-04/build_candidate.py
Use --html-only to inspect the assembled HTML without launching a browser.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys

BUNDLE = Path(__file__).resolve().parent
REPO = BUNDLE.parents[3]
MANUSCRIPTS = REPO / "research" / "manuscripts"
sys.path.insert(0, str(MANUSCRIPTS))
import build_submission_pdf as renderer
from submission_metrics import measure


def relative(path, base=MANUSCRIPTS):
    return os.path.relpath(path, base).replace(os.sep, "/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--chrome", help="Explicit Chromium executable path")
    args = parser.parse_args()
    paper = copy.deepcopy(renderer.PAPERS["aso-journal"])
    paper["manuscript"] = relative(BUNDLE / "manuscript.md")
    paper["tables"] = relative(BUNDLE / "fusion-junction-aso-journal-tables.md")
    paper["references"] = relative(BUNDLE / "fusion-junction-aso-journal-references.md")
    paper["out"] = relative(BUNDLE / "candidate.pdf")
    paper["stamp_sources"] = (
        paper["manuscript"], paper["tables"], paper["references"],
        relative(BUNDLE / "fusion-junction-aso-sequences.csv"),
        relative(BUNDLE / "build_candidate.py"),
    )
    paper["figures"] = {
        "Figure 1.": relative(BUNDLE / "aso-multipartner-seam.svg", MANUSCRIPTS / "figures")
    }
    paper["supplementary_for_review"] = (
        relative(BUNDLE / "fusion-junction-aso-sequences.csv"),
    )
    renderer.FORMATS["journal"] = (
        "[unsubmitted NAT candidate]",
        "Unsubmitted author-review candidate; not deposited or peer reviewed.",
    )
    chrome = args.chrome
    if not chrome and os.name == "nt":
        chrome = next((str(path) for path in (
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        ) if path.is_file()), None)
    if chrome:
        renderer.find_chrome = lambda: chrome

    class PortableWS(renderer.WS):
        def call(self, method, **params):
            if method == "Page.navigate" and params.get("url", "").startswith("file://"):
                params["url"] = Path(params["url"][7:]).resolve().as_uri()
            return super().call(method, **params)

    renderer.WS = PortableWS
    metrics = measure(BUNDLE / "manuscript.md", [BUNDLE / Path(paper[key]).name
                                               for key in ("tables", "references")])
    print(json.dumps({"candidate_metrics": metrics, "geometry": paper["geometry"]}))
    result = renderer.build("aso-nat-candidate", paper, html_only=args.html_only)
    if args.html_only:
        (BUNDLE / "candidate.build.html").replace(BUNDLE / "candidate.html")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
