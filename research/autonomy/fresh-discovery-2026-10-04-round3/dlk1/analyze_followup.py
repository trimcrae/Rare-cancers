"""All GSE4303 EMC source values and source-mapped USZ23 DLK1 transcripts."""
from pathlib import Path
import zipfile,csv,io,gzip,json,re,hashlib,xml.etree.ElementTree as E
import numpy as np
D=Path(__file__).resolve().parent;Z=Path('C:/Projects/EMC-Research/research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip')
z=zipfile.ZipFile(Z);meta=json.loads(z.read('GSE4303.soft-sample-metadata.json'))
emc=[r for r in meta if re.search('chondrosarcoma',str(r['fields'].get('!Sample_title')),re.I)];assert len(emc)==10 and all(r['fields']['!Sample_platform_id']==['GPL3290']for r in emc)
cache=json.loads(z.read('accession-symbol-cache.json'));acs={ac for mp in cache['by_source'].values() for ac,g in mp.items()if g=='DLK1'}
rows=list(csv.DictReader(io.StringIO(z.read('GPL3290-original-annotation.tsv').decode()),delimiter='\t'));probes=[r for r in rows if set(re.split('[,; ]+',r['GB_LIST']))&acs]
assert {r['ID']for r in probes}=={'19963','21745'}
# Historical cache is candidate generation only. Original EST records support both clones
# as homologous to U15981 adrenal-specific30kD protein; explicit accession bridge retained.
est=E.parse(D/'dlk1-old-probes.xml');estmeta=[{'accession':g.findtext('GBSeq_accession-version'),'definition':g.findtext('GBSeq_definition'),'feature_qualifiers':[(q.findtext('GBQualifier_name'),q.findtext('GBQualifier_value'))for q in g.findall('.//GBQualifier')]}for g in est.findall('.//GBSeq')]
matrix=gzip.decompress(z.read('GSE4303-GPL3290-source-matrix.gz')).decode();selected={};inside=False
for line in matrix.splitlines():
    if line=='!series_matrix_table_begin':inside=True;header=None
    elif line=='!series_matrix_table_end':inside=False
    elif inside:
        r=next(csv.reader([line],delimiter='\t'))
        if header is None:header=r[1:];continue
        if r[0]in{'19963','21745'}:selected[r[0]]={s:float(x) if x not in ['null','NA',''] else None for s,x in zip(header,r[1:])}
assert len(selected)==2
sampleids=[r['gsm']for r in emc];ev={p:{s:v[s]for s in sampleids}for p,v in selected.items()}
po=[{'probe':p,'n_measured':sum(x is not None for x in v.values()),'median_log2_ratio':float(np.median([x for x in v.values()if x is not None])),'range_log2_ratio':[min(x for x in v.values()if x is not None),max(x for x in v.values()if x is not None)],'n_above_reference':sum(x>0 for x in v.values()if x is not None)}for p,v in ev.items()]
refs=E.parse(D/'dlk1-gene.xml');refseq=sorted(set(t.text for t in refs.iter('Gene-commentary_accession')if t.text and re.match('[NX][MR]_',t.text)))
with gzip.open(D/'USZ23-RefSeq.quant.sf.gz','rt')as f:rr=list(csv.DictReader(f,delimiter='\t'))
tr=[r for r in rr if r['Name'].split('.')[0]in refseq];assert len(tr)==len(refseq)==2
out={'input_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Z,D/'dlk1-old-probes.xml',D/'dlk1-gene.xml',D/'USZ23-RefSeq.quant.sf.gz']},'GSE4303':{'all_source_samples':len(meta),'all_source_platforms':sorted({r['fields']['!Sample_platform_id'][0]for r in meta}),'all_eligible_emc_metadata':emc,'probe_annotations':probes,'mapping_caveat':'Historical UniGene maps DLK1 candidates; original ESTs identify U15981 homolog, explicit current U15981/DLK1 bridge checked separately. No use as absolute abundance.','original_EST':estmeta,'all_platform_probe_values':selected,'all10_emc_probe_values':ev,'summary':po,'reference_caveat':'All 10 EMC source-labelled CRH-mRNA reference. Other samples have CRH or UHR; exact common-pool equivalence unverified. No cross-histology AUC, cross-reference pooling, absolute abundance or surface-protein inference.'},'USZ23':{'sample':'GSM9037837_USZ23_EMC3','all_source_rows':len(rr),'gene_source_refseq':refseq,'all_matching_transcripts':tr,'summed_TPM_of_mapped_rows':sum(float(r['TPM'])for r in tr),'summed_NumReads_of_mapped_rows':sum(float(r['NumReads'])for r in tr),'limitations':'One cultured library. Both currently mapped DLK1 transcript rows have zero estimates. The original Salmon index annotation version and any retired/older DLK1 accessions are not completely reconciled; this is not categorical gene absence. No protein isoform or cell-surface inference. Donor independence from USZ20 unresolved.'}}
(D/'followup-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'GSE4303':po,'USZ23':out['USZ23']},indent=2))
