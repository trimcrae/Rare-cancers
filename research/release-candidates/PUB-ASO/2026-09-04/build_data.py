#!/usr/bin/env python3
"""Derive corrected release companions without altering the historical archive.

Sequence rows and numeric model results remain identical to their canonical
sources. This release corrects two interpretations: an unmodified-hybrid model
does not establish a temperature bound for LNA/PS chemistry, and exon labels do
not establish the nucleotide breakpoint of the reported USZ cell models.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = REPO / "research/manuscripts/aso"


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one source passage: {old[:80]}")
    return text.replace(old, new, 1)


def main():
    csv_name = "fusion-junction-aso-sequences.csv"
    table_name = "fusion-junction-aso-journal-tables.md"
    source_csv = (SOURCE / csv_name).read_text(encoding="utf-8")
    source_tables = (SOURCE / table_name).read_text(encoding="utf-8")
    old = re.search(r"(?m)^# ⭐ WHAT THEY ARE FOR:.*(?:\n# [^\n]+)*", source_csv)
    if not old or "cancels in the difference" not in old.group(0):
        raise RuntimeError("Historical temperature caveat changed; review the derivation")
    corrected_csv = replace_once(source_csv, old.group(0),
        "# These legacy column names denote unmodified DNA:RNA model outputs in degrees Celsius.\n"
        "# Their difference compares the fusion duplex with the more stable parent half-duplex.\n"
        "# LNA and phosphorothioate effects are not modelled; cancellation is not established.\n"
        "# Neither endpoint nor difference is a validated prediction or bound for the modified\n"
        "# reagent. Sequence rows and numerical model outputs are unchanged from the source.")
    # Non-comment CSV bytes must remain identical, including every numerical field.
    assert [x for x in corrected_csv.splitlines() if not x.startswith("#")] == [
        x for x in source_csv.splitlines() if not x.startswith("#")]
    tables = replace_once(source_tables,
        "Regenerate: python3 research/manuscripts/aso_journal_tables.py",
        "Release interpretation corrected by build_data.py; canonical numeric source: aso_journal_tables.py")
    tables = replace_once(tables,
        "REPORTED at an NR4A3 exon-2 acceptor and match different designs, not these two.",
        "reported at an NR4A3 exon-2 acceptor; correspondence to these reagents requires nucleotide-junction confirmation.")
    tables = replace_once(tables,
        "The separation is a floor rather than an estimate, for the reason Methods gives; absolute melting points are not reported for a locked, phosphorothioate oligonucleotide.",
        "These are differences from the unmodified DNA:RNA model at 250 nM strand concentration. LNA and phosphorothioate effects are unmodelled, so these values are not validated predictions or bounds for the proposed modified reagents.")
    tables = replace_once(tables, "ΔTm floor (°C)", "Model ΔTm (°C)")
    for value in ("26.6", "36.0"):
        tables = replace_once(tables, "| ≥ " + value + " |", "| " + value + " |")
    for name, text in ((csv_name, corrected_csv), (table_name, tables)):
        (HERE / name).write_text(text, encoding="utf-8", newline="\n")
    paths = [SOURCE / csv_name, SOURCE / table_name, HERE / csv_name, HERE / table_name,
             Path(__file__).resolve()]
    stamp = {"schema": "aso-release-companions/1", "sequence_rows_and_numeric_outputs_unchanged": True,
             "files": {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE / "data-build-stamp.json").write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stamp, indent=2))


if __name__ == "__main__":
    main()
