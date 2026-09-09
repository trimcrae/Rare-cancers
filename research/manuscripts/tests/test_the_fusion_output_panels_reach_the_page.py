"""The five fusion-output panels are embedded in the PDF, not linked from it.

⛔ WHAT SHIPPED (2026-09-08, read off rasterised pages of both built PDFs). The `fusion-output`
entry did not set `inline_images`, so each of the manuscript's five
`![Figure N](../figures/figN-….png)` lines reached the reader through `inline()`, which has no
image rule: a stray `!` followed by a blue hyperlink to a file that does not travel with the
deposit. Journal pp. 8-9 and manuscript pp. 17-19 printed `!Figure 1` … `!Figure 5` above five
legends describing panels that were not on the page — colours, axes, points and greyed cells the
reader could not see. A legend without its panel is a claim with its evidence removed.

⛔ AND THE PANELS MUST BE IN `stamp_sources`. `_write_build_stamp` hashes the markdown plus
`paper["figures"]`, and this entry's `figures` is legitimately empty (there is no
`## Figure legends` section to splice against). Without the PNGs named in `stamp_sources` a
redrawn panel would leave both PDFs stamped "current" against a list that cannot see it — the
staleness hole the ASO round-15 finding closed.

★ WHAT THIS ASSERTS: every image reference in the manuscript becomes an embedded raster, none
survives as markdown, and every embedded file is stamped.
"""
from __future__ import annotations

import importlib.util
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BUILDER = os.path.join(ROOT, "build_submission_pdf.py")


def _builder():
    spec = importlib.util.spec_from_file_location("build_submission_pdf", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _paper(module):
    return module.PAPERS["fusion-output"]


def test_every_image_reference_becomes_an_embedded_raster():
    module = _builder()
    paper = _paper(module)
    source = open(os.path.join(ROOT, paper["manuscript"]), encoding="utf-8").read()
    refs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", source)
    assert len(refs) == 5, refs
    out = module.inline_raster_images(source, paper)
    assert out.count('<img class="raster" src="data:image/png;base64,') == 5, \
        "a panel did not embed"
    assert not re.search(r"!\[[^\]]*\]\([^)\s]+\)", out), \
        "an image reference survived as markdown and would print as a stray '!' and a dead link"


def test_each_embedded_panel_is_covered_by_the_build_stamp():
    module = _builder()
    paper = _paper(module)
    source = open(os.path.join(ROOT, paper["manuscript"]), encoding="utf-8").read()
    base = os.path.dirname(paper["manuscript"])
    for ref in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", source):
        rel = os.path.normpath(os.path.join(base, ref)).replace("\\", "/")
        stamped = {os.path.normpath(path).replace("\\", "/")
                   for path in paper["stamp_sources"]}
        assert rel in stamped, \
            f"{rel} is rendered into the PDF and is not in stamp_sources"
        assert os.path.exists(os.path.join(ROOT, rel)), rel


def test_the_journal_stylesheet_gives_the_wide_panels_both_columns():
    module = _builder()
    css = module.journal_css(_paper(module))
    #: Every panel is between 1.71 and 3.15 times as wide as it is tall; in one ~88 mm column
    #: Figure 4 prints about 28 mm tall and its per-cell statistics are unreadable.
    assert "column-span: all" in css
    assert ".cols figure.figure img.raster { width: 100%; }" in css
