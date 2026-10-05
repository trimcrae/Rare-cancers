"""Bind and check frozen reciprocal addenda without downloads or source mutation."""
import csv, gzip, hashlib, json, pathlib, statistics
import xml.etree.ElementTree as ET
from scipy.stats import rankdata
BASE=pathlib.Path(__file__).resolve().parent
PEER=pathlib.Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def bindfreeze(p,h):
 assert sha(p)==h
 d=load(p)
 for n,r in d['files'].items():assert sha(p.parent/n)==r['sha256'] and (p.parent/n).stat().st_size==r['bytes'],n
 return d
def a(x,y):
 r=rankdata(x+y);return float((sum(r[:len(x)])-len(x)*(len(x)+1)/2)/(len(x)*len(y)))
def main():
 old=bindfreeze(PEER/'SCIENCE-FREEZE.json','3d40abe761af9aa9148db207600c225f3803b9462c67d21cec40c11d9f477fdf')
 mf=bindfreeze(PEER/'MODEL-ADDENDUM-FREEZE.json','b53393ee18ac6cafb16cee907a889b59f155f38164c07ed6417bc876546381c9')
 model=load(PEER/'MODEL-ADDENDUM.json');xmlpath=PEER/'raw-cache/transporter-current-Gene.xml';qp=BASE/'source-cache/USZ23-RefSeq.quant.sf.gz'
 assert sha(xmlpath)==mf['raw_source_hashes']['current_GeneXML'] and sha(qp)==mf['raw_source_hashes']['USZ23_quant']
 genemap={}
 for gene in ET.parse(xmlpath).getroot().iter('Entrezgene'):
  name=gene.findtext('.//Gene-ref_locus');gid=gene.findtext('.//Gene-track_geneid');assert {'SLC6A2':'6530','SLC18A1':'6570','SLC18A2':'6571'}[name]==gid
  genemap[name]=sorted({e.text for e in gene.iter('Gene-commentary_accession') if e.text and e.text.startswith(('NM_','NR_','XM_','XR_'))})
 with gzip.open(qp,'rt') as f:quants=list(csv.DictReader(f,delimiter='\t'))
 previous=load(BASE/'NEUROSECRETORY-INDEPENDENT-REVIEW.json');mr=[]
 for name,accessions in genemap.items():
  rows=[r for r in quants if r['Name'].split('.')[0] in accessions];result=model['rows'][name]
  assert result['USZ23_current_accessions']==accessions and result['USZ23_rows']==rows
  tpm=sum(float(r['TPM']) for r in rows) if rows else None;assert result['USZ23_mapped_sum_TPM']==tpm
  assert result['ARCHS4_exact_symbol_rows']==previous['additional_model_context_not_in_peer_freeze']['fixed_panel_symbol_rows'][name]
  mr.append({'gene':name,'USZ23_current_identifier_rows':len(rows),'USZ23_mapped_sum_TPM':tpm,'ARCHS4_rows':result['ARCHS4_exact_symbol_rows']})
 assert model['ARCHS4_allrow_denominators']=={'GSM2113301':40794510,'GSM6883080':28727977}
 rf=bindfreeze(PEER/'peer_review/FREEZE.json','c9b7d236802c774869705cfae3be8ddb90bc7bb00a49d7c28bb3dfdae682037c')
 addon=load(PEER/'peer_review/SURFACE-3SEQ-ADDENDUM.json');src=pathlib.Path(addon['source_path']);assert sha(src)==addon['source_sha256']
 selected={g:[] for g in addon['panel']}
 with gzip.open(src,'rt') as f:
  reader=csv.DictReader(f,delimiter='\t');columns=reader.fieldnames[7:]
  for row in reader:
   if row['gene_symbol'] in selected:selected[row['gene_symbol']].append(row)
 for g,value in addon['genes'].items():
  assert len(selected[g])==value['exact_symbol_peaks']
  for source_row,projected in zip(selected[g],value['peaks']):
   assert source_row['peak']==projected['peak']
   assert all(float(source_row[sid])==v for sid,v in projected['values'].items())
  if selected[g]:
   emcs={s:sum(float(row[s]) for row in selected[g]) for s in addon['all_EMC_conditions']};assert value['EMC_sums']==emcs
   for label,prefix in [('MLPS','MLPS_'),('SS','SS_'),('normal_context',None)]:
    ids=[s for s in columns if s.startswith(prefix)] if prefix else [s for s in columns if '_normal_' in s]
    vs=[sum(float(row[s]) for row in selected[g]) for s in ids];c=value['comparators'][label]
    assert c['n']==len(vs) and c['median']==statistics.median(vs) and c['A']==a(list(emcs.values()),vs)
  else:assert not value['EMC_sums'] and not value['comparators']
 review={'original_neurosecretory_freeze_sha256':sha(PEER/'SCIENCE-FREEZE.json'),'model_addendum_freeze_sha256':sha(PEER/'MODEL-ADDENDUM-FREEZE.json'),'model_addendum_files':mf['files'],'raw_source_hashes':mf['raw_source_hashes'],'all_three_culture_panel_rows_verified':mr,'status':'PASS source-bound additive completeness and unchanged shelving decision','limits':['Current RefSeq mapping does not reconcile retired identifiers; mapped zeros are not gene/protein absence.','One cultured library per model, USZ23 donor independence unresolved; counts/TPM not pooled.','No transporter uptake, storage, treatment benefit or source exhaustion inferred.'],'original_science_files_reverified':len(old['files'])}
 (BASE/'NEUROSECRETORY-MODEL-ADDENDUM-REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
 coverage={'original_surface_commit':'ba6f0841b4adbc50d768d73ccbfc7db5b496235d','original_surface_freeze_sha256':sha(BASE/'FREEZE.json'),'own_amendment':'AMENDMENT-02.txt','peer_review_freeze_path':'research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory/peer_review/FREEZE.json','peer_review_freeze_sha256':sha(PEER/'peer_review/FREEZE.json'),'peer_artifact_bindings':rf['files'],'source_sha256':addon['source_sha256'],'source_storage':'Read-only zero-copy source in peer ignored raw-cache; no duplicate or raw export.','source':'GSE28866/3SEQ','all_EMC_conditions':addon['all_EMC_conditions'],'condition_count':4,'target_peaks':{g:v['exact_symbol_peaks'] for g,v in addon['genes'].items()},'EMC_source_normalized_peak_sums':{g:v['EMC_sums'] for g,v in addon['genes'].items()},'comparators':{g:v['comparators'] for g,v in addon['genes'].items()},'status':'Evaluated additive all-four-condition source, independently projected by peer and exact rows/contrasts source-checked here.','gene_absence_policy':'DLL3 has no exact source peak; this is unavailable coverage, not RNA/protein absence. SEZ6 and NCAM1 measured peaks preserved including zeros.','decision':'Original SHELVE unchanged; SEZ6 A0.25 versus synovial in this assay, NCAM1 remains nonspecific; no biological/clinical rescue.','still_pending':'All named pending tissue, historical prior-art, model and donor/assay gaps in original COVERAGE.json remain; this adds one source only. No full public EMC coverage or global exhaustion.'}
 (BASE/'COVERAGE-AMENDMENT-02.json').write_text(json.dumps(coverage,indent=2)+'\n')
 print(json.dumps({'model_review':mr,'surface3SEQ_genes':coverage['EMC_source_normalized_peak_sums'],'decision':'Both shelving decisions unchanged.'},indent=2))
if __name__=='__main__':main()
