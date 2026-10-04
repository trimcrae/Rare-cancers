from pathlib import Path
import json,csv,io,gzip,zipfile,statistics,hashlib,xml.etree.ElementTree as E
base=Path(__file__).parent
owner=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1')
source=Path('C:/Projects/EMC-Research/research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip')
report=json.loads((owner/'followup-results.json').read_text())
with zipfile.ZipFile(source) as z:
 meta=json.loads(z.read('GSE4303.soft-sample-metadata.json'))
 emc=[r for r in meta if 'chondrosarcoma' in str(r['fields'].get('!Sample_title')).lower()]
 assert len(emc)==10
 assert all(r['fields']['!Sample_platform_id']==['GPL3290'] and r['fields']['!Sample_source_name_ch1']==['CRH-mRNA'] and r['fields']['!Sample_label_ch1']==['Cy3'] and r['fields']['!Sample_label_ch2']==['Cy5'] for r in emc)
 raw=gzip.decompress(z.read('GSE4303-GPL3290-source-matrix.gz')).decode()
 table=raw.split('!series_matrix_table_begin')[1].split('!series_matrix_table_end')[0].strip()
 rows=list(csv.reader(io.StringIO(table),delimiter='\t'));header=rows[0][1:]
 values={r[0]:{s:(None if v=='null' else float(v))for s,v in zip(header,r[1:])}for r in rows[1:]if r[0] in ['19963','21745']}
 emc_values={p:{r['gsm']:vv[r['gsm']]for r in emc}for p,vv in values.items()}
 assert emc_values==report['GSE4303']['all10_emc_probe_values']
 sums={p:{'n':sum(v is not None for v in vv.values()),'median':statistics.median([v for v in vv.values() if v is not None]),'positive_ids':[s for s,v in vv.items()if v is not None and v>0]}for p,vv in emc_values.items()}
 est=E.parse(owner/'dlk1-old-probes.xml');estdesc=[(r.findtext('GBSeq_accession-version'),r.findtext('GBSeq_definition'))for r in est.findall('.//GBSeq')]
 assert len(estdesc)==2 and all('U15981' in d for ac,d in estdesc)
 gene=E.parse(owner/'dlk1-gene.xml');symbol=gene.findtext('.//Gene-ref_locus');geneid=gene.findtext('.//Gene-track_geneid')
 assert symbol=='DLK1' and geneid=='8788'
 accessions={r.text for r in gene.iter('Gene-commentary_accession')}
 assert 'U15981' in accessions
 refseq=sorted(a for a in accessions if a and a.startswith(('NM_','NR_','XM_','XR_')))
 assert refseq==['NM_001317172','NM_003836']
 with gzip.open(owner/'USZ23-RefSeq.quant.sf.gz','rt') as f:
  qs=[r for r in csv.DictReader(f,delimiter='\t')if r['Name'].split('.')[0]in refseq]
 assert qs==report['USZ23']['all_matching_transcripts']
 assert all(float(r['TPM'])==0 and float(r['NumReads'])==0 for r in qs)
files=[source,owner/'dlk1-old-probes.xml',owner/'dlk1-gene.xml',owner/'USZ23-RefSeq.quant.sf.gz',owner/'followup-results.json']
out={'status':'PASS','input_hashes':{str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in files},'GSE4303_values':emc_values,'GSE4303_summary':sums,'source_mapping':{'gene':symbol,'entrez':geneid,'EST_definition':estdesc,'bridge':'U15981 is included in Gene8788 source accessions; EST definitions describe similarity, not this reviewer establishing a unique sequence alignment.'},'USZ23_matching_transcripts':qs,'interpretation':'Both GSE4303 probe candidates have the same single positive specimen, preserved; 3 missing values on probe21745 remain missing. log2(tumor/CRH) cannot establish absolute DLK1 abundance, biological absence or membrane isoform. USZ23 zero transcript estimates are one culture/library, not disease-wide absence.'}
(base/'followup-crosscheck.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'status':'PASS','GSE4303':sums,'USZ23':qs},indent=2))
