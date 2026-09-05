#!/usr/bin/env python3
"""Render the revision note supplied beside the corrected sequence CSV."""
import hashlib
import html
import json
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

HERE = Path(__file__).resolve().parent
OUT = HERE / "submission"


def render(source, target, anonymous=False):
    text = source.read_text(encoding="utf-8").split("---", 2)[2].strip()
    if anonymous:
        text = text.replace("doi:10.5281/zenodo.22229096", "the historical archive identified in the unblinded submission")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("NoteBody", fontName="Times-Roman", fontSize=11,
                             leading=14, spaceAfter=5, alignment=TA_LEFT))
    for name in ("Title", "Heading2"):
        styles[name].fontName = "Times-Bold"
        styles[name].textColor = colors.black
    styles["Title"].fontSize = 16
    styles["Heading2"].fontSize = 12
    styles["Title"].spaceAfter = 10
    styles["Heading2"].spaceBefore = 8
    styles["Heading2"].spaceAfter = 5
    story = []
    for block in re.split(r"\n\s*\n", text):
        if block.startswith("# "):
            style, block = styles["Title"], block[2:]
        elif block.startswith("## "):
            style, block = styles["Heading2"], block[3:]
        else:
            style = styles["NoteBody"]
        story.append(Paragraph(html.escape(block).replace("\n", " "), style))
    def footer(canvas, doc):
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(22*mm, 13*mm, "Supplementary File 2 | Revision dated 4 September 2026")
        canvas.drawRightString(188*mm, 13*mm, str(doc.page))
    doc = SimpleDocTemplate(str(target), pagesize=(210*mm, 297*mm),
                            leftMargin=22*mm, rightMargin=22*mm, topMargin=20*mm,
                            bottomMargin=22*mm, title="ASO submission revision and data provenance",
                            author="" if anonymous else "Tristan D. McRae")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    source = OUT / "revision-note.md"
    outputs = []
    for anonymous in (False, True):
        target = OUT / ("supplementary-file-2-anonymized.pdf" if anonymous else "supplementary-file-2.pdf")
        render(source, target, anonymous)
        outputs.append(target)
    paths = [source, Path(__file__).resolve(), *outputs]
    stamp = {"schema": "aso-revision-note-build/1", "files": {
        p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUT / "revision-note-build-stamp.json").write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stamp, indent=2))


if __name__ == "__main__":
    main()
