"""Generate the human-readable catalogue from committed analysis results."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent


def main():
    with (ROOT / 'results/junction-catalogue.tsv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    text = '''---
id: DOC-PUB-ASO-SEQUENCE-CATALOGUE-20260930
title: ASO choices across catalogued EMC junctions
kind: memo
status: live
date: 2026-09-30
last_verified: 2026-09-30
purpose: Provide the tied best choices under an explicit normal-parent sequence comparison.
audience: [maintainers, external reviewers]
scope: Five fixed 16-base positions at each of 43 target junctions and one control.
---

# ASO sequence catalogue

All ASO sequences below run 5′ to 3′. Multiple sequences in a cell are tied;
their order is by binding position, not preference. **These are choices by a
declared sequence screen, not validated therapeutic leads.**

“Gap match” is the longest consecutive exact normal-RNA match covering the
proposed six-base DNA gap; shorter is preferred. Among tied positions, “nearest
RNA differences” is the minimum number of mismatches to any complete normal
16-base window; larger is preferred. The corpus contains 85 reference records
from seven parent genes, not the whole human transcriptome.

A gap-match value of zero means no complete exact six-base-gap match in this
corpus, not absence of other complementarity.

The [method and findings](README.md) explain the scope. The
[complete design table](results/all-designs.tsv) includes all five positions,
primary ties and competing alternatives. The
[junction table](results/junction-catalogue.tsv) gives exact reference context,
source accessions, coordinates and uncertainty. Exon labels below are shorthand
for those pinned sequences, not universal exon numbering.

'''
    groups = [
        ('Junctions matching deposited fusion sequences', 'deposited_sequence_match',
         'Five distinct junctions are supported by seven deposited records. This is not a patient count.\n'),
        ('Reference reconstruction from reported coordinates', 'coordinate_based_reference_reconstruction',
         'The USZ20 model maps to this reference junction. Patient-specific variants or inserted bases remain unresolved.\n'),
        ('Reference reconstruction from a construct description', 'construct_description_reference_reconstruction',
         'This corresponds to the Brenca T-N engineered construct description, not an exact deposited construct or patient RNA consensus.\n'),
        ('Hypothetical exact reference joins', 'hypothetical_exact_reference_join',
         'These exact sequence joins lack resolved source correspondence in the accepted evidence. Some partner or exon labels have appeared in papers; that alone does not establish the exact sequence.\n'),
        ('Annotation-error control', 'annotation_error_control',
         'This historical label-transfer control is excluded from the 43 target-junction and 215-design summaries. It is not assigned to the USZ20 model.\n')]
    for title, evidence_class, note in groups:
        text += '## ' + title + '\n\n' + note + '\n'
        text += '| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |\n'
        text += '| --- | --- | ---: | ---: |\n'
        for row in rows:
            if row['evidence_class'] != evidence_class:
                continue
            label = row['junction'].replace('__', ' / ').replace('_intron2crypticExon', ' cryptic exon').replace('_e', ' exon ')
            choices = '<br>'.join('`' + s + '`' for s in json.loads(row['final_co_winner_ASO_5to3']))
            text += f"| {label} | {choices} | {row['primary_best_gap_run_bp']} | {row['final_min_hamming_bp']} |\n"
        text += '\n'
    (ROOT / 'CATALOGUE.md').write_text(text, encoding='utf-8')
    print('Generated CATALOGUE.md from 44 junction rows.')


if __name__ == '__main__':
    main()
