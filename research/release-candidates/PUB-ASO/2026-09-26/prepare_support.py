from pathlib import Path
import json, hashlib, shutil
ROOT=Path(__file__).resolve().parent
ORIGINAL=Path(r"C:/Users/mcrae/Documents/Codex/2026-09-07/emc-research-orchestrator/work/aso-documented-junctions-20260926")
text=(ORIGINAL/'SUPPORTING.md').read_text(encoding='utf-8')
text=text[text.index('## 2. Primary-source investigation'):]
text=text[:text.index('No researcher was contacted and no publication action was taken.')]
text=text.replace('## 2.', '## S1.').replace('## 3.', '## S2.').replace('## 4.', '## S3.').replace('## 5.', '## S4.').replace('## 6.', '## S5.')
intro="""# Supplementary methods for transcript provenance and antisense comparisons in EMC

Tristan D. McRae

This supplement documents source recovery, coordinate reconstruction and the 35-design source-linked analysis. Five hypothetical annotation-error controls are reported separately. Main-text and supplementary section numbers are independent. The complete preceding 190-design screen is historical context, not a newly screened cohort.

The investigation was completed on 26 September 2026 using public papers and sequence records. Prior catalogue inputs were captured from repository revision 3d550114538a1545e1eab03e1a93f69566da47de. Supplementary Data includes the exact copied inputs and their original hashes. This targeted investigation does not claim an exhaustive survey of all EMC cases.

"""
outro="""## S6. Reproduction and file definitions

Unzip Supplementary Data and run Python 3.11 or later from its evidence directory:

```text
python analyze.py
```

The script uses only the Python standard library and makes no network requests. It checks the copied input hashes, annotation relationships, reconstructed sequence agreement, deposited anchors, antisense orientation and agreement of two matching implementations. It regenerates all eleven results files in results/. An output-checksum manifest enables comparison with the released results. Source retrieval URLs, dates, versions and checksums are in retrieval.jsonl; unsuccessful retrieval routes are preserved.

junction-evidence.tsv distinguishes each source observation and reconstruction. design-comparisons.tsv contains 40 rows, of which five have control_only=true and are excluded from the main 35-design summaries. The legacy_metric_reused column distinguishes accepted metrics from newly calculated cryptic-exon baseline comparisons. longest-normal-match-locations.tsv preserves every tied maximum, normal reference identifier, zero-based window start, complete normal window and one-based mismatch positions. displayed-transcript-exons.tsv uses one-based inclusive genomic coordinates. normal-reference-transcripts.fasta and its manifest contain the precise normal corpus. model-crosswalk.json separates USZ20 inference from unresolved USZ22 observations. literal-label-error-control.tsv, cutoff-sensitivity.tsv and normal-isoform-corroboration.json support the corresponding comparisons. summary.json records derived counts and check scope.

Large compressed read prefixes are not duplicated in the journal supplement. Their saved outputs and receipts are included. They can be retrieved and searched with the following command; this downloads a fixed 64 MiB from each of two runs and requires at least 128 MiB plus temporary working space:

```text
python read_prefix_probe.py --fetch --mib 64
```

Compare fetched prefix hashes to the original .receipt.json records before interpreting a rerun. Whole-file ENA MD5 values do not verify partial files. Offline replay with the original saved prefixes reproduced the reported complete-record counts and zero anchors. The probe is optional for reproducing the positive coordinate and parent-isoform findings; those depend only on the included reference inputs.

The original fusion-junction-aso-sequences.csv in inputs/ retains 782 non-comment rows spanning the preceding primary catalogue, extensions and controls. It is a historical input, not the current 40-row comparison table. Historical orderable or do_not_order fields encode computational rules and are not biological or clinical recommendations. The preceding artificial-junction result is not recomputed using the expanded corpus.

## S7. Interpretation corrections and remaining evidence

The USZ20 crosswalk replaces the earlier interpretation that the paper lacked information sufficient to assess catalogue correspondence. It does not supply a patient consensus. The alternative NR4A3 transcript explains the reported exon-2 label, and the displayed EWSR1 annotation also changes exon rank. The original six-transcript match lengths remain correct for that corpus; they must not be presented as all-isoform results.

A previous explanation that a primer in retained NR4A3 exon 3 could never recover an upstream cryptic-exon fusion is withdrawn. A reverse primer in retained exon 3 can amplify such a transcript with a suitable upstream donor primer. Exclusion would require the actual primer sequences and orientation. This correction does not change the present sequence calculations.

USZ20 needs a mature-RNA consensus or a fully specified original directional call, including genome build, coordinate convention and inserted bases. USZ22 needs the actual donor end, acceptor start and direction. Brenca constructs need attributable spanning reads or the physical construct sequence. A complete transcriptome/pre-mRNA search and tissue expression context would be needed before selecting experimental leads; the current parent-isoform audit does not provide those data. Cleavage, accessibility, potency and normal-transcript effects require experiments.

"""
(ROOT/'supplementary-methods.md').write_text(intro+text+outro,encoding='utf-8')
source_receipts=[]
for p in sorted((ROOT/'evidence').rglob('*')):
    if p.is_file():
        source_receipts.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
(ROOT/'evidence-manifest.json').write_text(json.dumps(source_receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'evidence_files':len(source_receipts),'bytes':sum(r['bytes'] for r in source_receipts)}))

