#!/usr/bin/env python3
"""Snapshot the deposit's machine-checkable invariants, and diff two snapshots.

⛔ WHY THIS EXISTS, AND IT IS COUNTED RATHER THAN FEARED. Over the 2026-08-19 review rounds,
TWELVE defects were introduced by the FIX for a previous defect — enumerated one by one, with the
fix that caused each, in condition 10 of the deposit stopping rule. (A *ratio* is not claimed: the
ledger records what each finding was, not what caused it, so no percentage is derivable from it.)
Four mechanisms, one root cause:

  1. UNBOUNDED MATCH SET. A fix applied by pattern matched more than the defect. An em-dash regex
     intended for a few parentheticals matched sixteen sites, produced `(§6))`, and ate both a
     pinned-figure anchor and a guard's derivation regex. A CSS rule scoped on column count also
     matched five landscape tables and corrupted 93 of 93 sequence cells.
  2. VERIFIED IN THE SOURCE, NOT THE ARTEFACT. The fix was correct in the .md and wrong once
     rendered: a table that overprinted the column beside it, and sequence cells that fused a
     neighbouring digit — both invisible in every source file.
  3. NEW TEXT IS UNREVIEWED TEXT. A fix ADDS a claim or a notation that nothing has ever checked:
     ⚑ put into prose with no key, an inverted numeric mapping, an asymmetric sentence emitted
     symmetrically into two captions.
  4. ONE HOME FIXED, THE OTHERS LEFT. A quantity lives in several places and one was changed.

★ THE ROOT IS THE SAME IN ALL FOUR: each fix was verified against THE DEFECT IT TARGETED and never
against everything it did NOT target. "Is the defect gone?" was asked; "what else moved?" was not.

USAGE — the loop this is for:
    python3 scripts/blast_radius.py snapshot before.json
    …make the fix, regenerate every derived artefact…
    python3 scripts/blast_radius.py compare before.json          # snapshots `after` itself

`compare` prints ONLY what changed and exits 1 if anything did. Every difference must be one you
INTENDED and can name. A difference you cannot name is the next blocker, found before it ships.

Stdlib plus pdfminer.six, which CI installs.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASO = os.path.join(REPO, "research/manuscripts/aso")
ART = os.path.join(ASO, "fusion-junction-aso-research-article.md")
SI = os.path.join(ASO, "fusion-junction-aso-supplementary-information.md")
TABLES = os.path.join(ASO, "fusion-junction-aso-submission-tables.md")
CSV_PATH = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
PDFS = {
    "journal": os.path.join(ASO, "fusion-junction-aso-research-article.pdf"),
    "manuscript": os.path.join(ASO, "fusion-junction-aso-research-article-manuscript.pdf"),
    "si": os.path.join(ASO, "fusion-junction-aso-research-article-supplementary-information.pdf"),
}
#: Markers that carry a VERDICT rather than decoration. A fix that introduces one of these into a
#: document without introducing its key is mechanism 3, and it has happened.
MARKERS = ("⚑", "◆", "†", "‡")

#: The same verdict, carried in words rather than in a glyph. Kept deliberately narrow: each phrase
#: states that the design is NOT to be carried forward, not merely that a number was measured on it.
_VERDICT_IN_PROSE = re.compile(
    r"do-not-order|do not order|must not be ordered|not to be used|is excluded by"
    r"|excluded by an? [a-z-]+ duplex|carries an? [a-z-]+ duplex against wild-type"
    r"|joins the liability class|in the liability class")


def _read(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def _unexplained_sequences(delimited, known, whole):
    """Printed sequences that are neither canonical nor a labelled target-mRNA strand."""
    labelled = re.search(r"target\s+mRNA", whole, re.I) is not None
    rc = str.maketrans("ACGT", "TGCA")
    out = set()
    for q in set(delimited) - set(known):
        if labelled and q.translate(rc)[::-1] in known:
            continue
        out.add(q)
    return out


def _csv_sequences():
    if not os.path.exists(CSV_PATH):
        return {}, set()
    rows = list(csv.DictReader([l for l in open(CSV_PATH, encoding="utf-8")
                                if not l.startswith("#")]))
    return ({r["sequence"]: r.get("do_not_order", "").strip() for r in rows},
            {r["sequence"] for r in rows if r.get("do_not_order", "").strip()})


def _cell_sequence_integrity(path):
    """Sequence cells as a TABLE EXTRACTOR sees them, which is how a reader copies one out.

    ⛔ THE CHECK THAT WOULD HAVE CAUGHT THE WORST DEFECT OF 2026-08-19. A CSS rule meant for one
    inline table also matched five landscape floats; their sequence cells overflowed their columns
    and were overprinted, and the journal build printed truncated 16-mers. Raw text extraction did
    NOT show it — the delimited-sequence count and the distinct-sequence set were both unchanged,
    because the damage is at the CELL boundary. Only cell-level extraction sees it: 3 well-formed
    cells against 93 malformed, where the submission format had 96 and 0.
    """
    try:
        import pdfplumber
    except ImportError:
        return {"_unavailable": "pdfplumber not installed"}
    good = bad = 0
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for tbl in page.extract_tables() or []:
                for row in tbl:
                    for cell in row or []:
                        if not cell:
                            continue
                        c = " ".join(str(cell).split())
                        if "5′-" in c or re.search(r"[ACGT]{12,}", c):
                            if re.fullmatch(r"5′-[ACGT]{14,20}-3′", c):
                                good += 1
                            else:
                                bad += 1
    return {"well_formed": good, "malformed": bad}


def _pdf_facts(path):
    """Facts a source file cannot show you: what the RENDERED page actually contains."""
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextBox
    if not os.path.exists(path):
        return {"_missing": True}
    pages, collisions, texts = 0, 0, []
    for page in extract_pages(path):
        pages += 1
        boxes = [b for b in page if isinstance(b, LTTextBox)]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1:
                    collisions += 1
        texts.append(" ".join(b.get_text() for b in boxes))
    whole = " ".join(texts)
    delimited = re.findall(r"5′-([ACGT]+)-3′", whole)
    known, condemned = _csv_sequences()
    return {
        "pages": pages,
        "text_box_collisions": collisions,
        "delimited_sequences": len(delimited),
        "distinct_sequences": len(set(delimited)),
        # ⛔ THE WRONG-REAGENT SIGNATURE, TWICE OVER: a digit fused into a run of bases, and a
        # printed sequence that matches no row of the canonical file.
        "digit_fused_sequences": len(re.findall(r"5′-[ACGT]*\d[ACGT]*-3′", whole)),
        # ⚠ NOT `set(delimited) - set(known)` — that list can never reach zero, and a baseline
        # that carries a permanent entry cannot tell a NEW wrong sequence from the one it already
        # tolerates. That is the same weak-check shape as the ⚑-only verdict test below. The one
        # standing entry is the TARGET mRNA seam printed in the Figure 1 caption, which the caption
        # itself labels as the target and explicitly warns is NOT the molecule to order; it is
        # allowed BY NAME with that reason, so anything else still trips the invariant at zero.
        # ⚠ NOT `set(delimited) - set(known)` — that list can never reach zero (Figure 1 draws the
        # TARGET mRNA at the seam, whose reverse complement is the reagent), and a baseline carrying
        # a permanent entry cannot tell a NEW wrong sequence from the one it already tolerates. That
        # is the same weak-check shape as the ⚑-only verdict test below.
        # ⛔ THE EXEMPTION IS DERIVED, NOT LISTED, AND IT IS DERIVED THE SAME WAY THE REPOSITORY'S
        # OWN GUARD DERIVES IT (`test_every_sequence_the_pdf_prints_is_in_the_canonical_file`): a
        # printed sequence outside the canonical file is tolerated only where the document says in
        # terms that the drawn letters are target mRNA AND the sequence is exactly the reverse
        # complement of a canonical design. Writing the literal sequence here instead would give one
        # fact two homes, and the worse home — a different legitimate seam would trip it and an
        # altered one would pass.
        "sequences_not_in_csv": sorted(_unexplained_sequences(delimited, known, whole)),
        # A condemned sequence must never print on a page that carries no verdict for it.
        # ⚠ A GLYPH IS NOT THE ONLY VERDICT, and demanding one made this read 2 and 3 against a
        # deposit where both pages state the verdict in WORDS ("is excluded by an eleven-base-pair
        # duplex with wild-type TCF12"). A baseline of 2 is unusable — it cannot tell a real
        # regression from the two it already tolerates — so the check accepts either carrier and
        # the invariant is zero, which is a number a diff can actually police.
        "sequence_cells": _cell_sequence_integrity(path),
        "condemned_pages_without_a_verdict": sum(
            1 for t in texts
            if any(re.search(r"5′-" + s + r"-3′", t) for s in condemned)
            and not any(m in t for m in MARKERS)
            and not _VERDICT_IN_PROSE.search(" ".join(t.split()))),
    }


def _prose_facts():
    art, si, tables = _read(ART), _read(SI), _read(TABLES)
    flat = " ".join(art.split())
    abstract = art.split("## Abstract", 1)[-1].split("\n---\n", 1)[0]
    return {
        "abstract_words": len([w for w in re.sub(r"\*", "", abstract).split() if w.strip()]),
        "article_chars": len(art), "si_chars": len(si), "tables_chars": len(tables),
        # Mechanism 1's signature: a pattern edit that unbalanced the brackets it inserted.
        "paren_balance": art.count("(") - art.count(")"),
        "bracket_balance": art.count("[") - art.count("]"),
        "doubled_close_paren": flat.count("))"),
        # Mechanism 3's signature: a verdict marker used in the body with no key sentence for it.
        "markers_in_body": {m: flat.count(m) for m in MARKERS},
        "em_dashes": art.count("—"),
        "sequences_in_prose": len(set(re.findall(r"5′-([ACGT]+)-3′", flat))),
    }


def _gate_facts():
    out = {}
    for name, cmd in (
        ("lint_consistency", ["python3", "research/manuscripts/lint_consistency.py"]),
        ("lint_claims", ["python3", "research/manuscripts/lint_claims.py"]),
        ("lint_style", ["python3", "research/manuscripts/lint_style.py"]),
        ("lint_citations", ["python3", "research/manuscripts/lint_citations.py"]),
    ):
        try:
            out[name] = subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=600).returncode
        except Exception as e:  # noqa: BLE001
            out[name] = f"error:{type(e).__name__}"
    return out


def snapshot():
    known, condemned = _csv_sequences()
    return {
        "prose": _prose_facts(),
        "pdf": {k: _pdf_facts(v) for k, v in PDFS.items()},
        "csv": {"rows": len(known), "condemned": len(condemned)},
        "gates": _gate_facts(),
    }


def _flatten(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from _flatten(v, f"{p}/{k}")
    else:
        yield p, d


def compare(path):
    before = json.load(open(path, encoding="utf-8"))
    after = snapshot()
    b, a = dict(_flatten(before)), dict(_flatten(after))
    changed = [(k, b.get(k, "<absent>"), a.get(k, "<absent>"))
               for k in sorted(set(b) | set(a)) if b.get(k, "<absent>") != a.get(k, "<absent>")]
    if not changed:
        print("blast radius: NOTHING ELSE MOVED — every invariant is unchanged.")
        return 0
    print(f"blast radius: {len(changed)} invariant(s) moved. Name each one or treat it as the "
          f"next blocker.\n")
    for k, x, y in changed:
        print(f"  {k}\n      before: {x}\n      after:  {y}")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("snapshot", "compare"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "snapshot":
        json.dump(snapshot(), open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"wrote {sys.argv[2]}")
        sys.exit(0)
    sys.exit(compare(sys.argv[2]))
