"""Independent read-only manifest/receipt review; no raw-read fetching."""
from pathlib import Path
import openpyxl,json,csv,collections,hashlib
P=Path(__file__).resolve().parent
M=P.parent/'microenvironment'
manifest=M/'HWT2.0-manifest.xlsx'
w=openpyxl.load_workbook(manifest,read_only=True,data_only=True)
rows=list(next(iter(w)).values)
assert list(rows[0][:5])==['Probe Name','Gene Symbol','Entrez ID','ENSEMBL Gene ID','Probe Sequence']
p=rows[1:];seq=collections.Counter(x[4] for x in p)
rc=lambda s:s.translate(str.maketrans('ACGT','TGCA'))[::-1]
lookup=collections.Counter()
for x in p:lookup[x[4]]+=1;lookup[rc(x[4])]+=1
runs=list(csv.DictReader((M/'PRJNA1357027-runs.tsv').open(),delimiter='\t'))
d=json.loads((M/'mapping-diagnostic-results.json').read_text())
assert {x['run_accession'] for x in runs}=={x['run'] for x in d['runs']}
assert {x['sample_alias'] for x in runs}=={x['sample'] for x in d['runs']}
out={'date':'2026-10-04','reviewer':'functional_models','manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'manifest_probe_rows':len(p),'lengths':dict(collections.Counter(len(x[4]) for x in p)),'forward_duplicate_sequence_count':sum(v>1 for v in seq.values()),'forward_or_reverse_ambiguous_sequences':sum(v>1 for v in lookup.values()),'unique_sample_aliases':len({x['sample_alias'] for x in runs}),'unique_biosamples':len({x['sample_accession'] for x in runs}),'unique_runs':len({x['run_accession'] for x in runs}),'all12_receipt_IDs_match':True,'observed_read_lengths':sorted({k for x in d['runs'] for k in x['lengths']}),'range_full_exact_match':[min(sum(v for k,v in x['counts'].items() if k.startswith('full_'))/x['reads_inspected'] for x in d['runs']),max(sum(v for k,v in x['counts'].items() if k.startswith('full_'))/x['reads_inspected'] for x in d['runs'])],'prespecified_gene_probes':d['manifest']['prespecified_gene_probes'],'judgment':['Independent openpyxl parsing by actual columns supports full50nt manifest extraction; no missing-column shift seen.','Both exact forward and reverse-complement50nt matches are tested; first10000read receipts all50nt. Prefix is not unbiased whole-library QC.','Ambiguous reference sequence matches are excluded explicitly, not assigned arbitrarily.','Processed9500gene matrix absence does not mean absence from22537probe assay or absent EMC expression.','75% is prespecified workflow allocation criterion, not validated assay-invalidity threshold.','Phred/complexity QC, mismatch-aware validated alignment and processed-count concordance remain unperformed; these are method gaps, not negative biology.','Distinct runs/biosamples are not proof of patient independence or a clinical risk/outcome crosswalk.','No additional mapping justified solely to rescue a weak biological contrast; all12 suitable accessible raw libraries remain pending, blocking manuscript promotion.']}
(P/'microenvironment-independent-challenge.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ('prespecified_gene_probes','judgment')},indent=2))
