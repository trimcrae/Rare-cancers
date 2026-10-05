"""Prepare source-only GPNMB wiring. This program never opens expression cells."""
from pathlib import Path
import json,hashlib,datetime,gzip,csv,zipfile,collections
P=Path(__file__).resolve().parent
ROOT=Path('/workspace/Rare-cancers')
SC=Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/gpnmb_all_condition_readiness')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
def take(row):return {k:row.get(k) for k in ['sample_id','source_label','s1_row','diagnosis','sequencing_year','specimen_exception','primary_lesion','known_overlap','patient_group']}
M=ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
assert sha(M)=='2dfb58418fdcbd00970602c1b5b06dde10a2d872e90031032c7427e836449db2'
meta=json.loads(M.read_text())['samples'];hists=['Extraskeletal myxoid chondrosarcoma','Low-grade fibromyxoid sarcoma','Myxoid liposarcoma','Synovial sarcoma']
roster=[take(r) for r in meta if r['diagnosis'] in hists]
counts={h:len([r for r in roster if r['diagnosis']==h]) for h in hists};assert list(counts.values())==[13,13,14,19]
RNA=ROOT/'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
assert sha(RNA)=='0255cd254762c6184a782d5b9a90aba6e545b6b2206e28f283455df2de4d62fc'
with gzip.open(RNA,'rt') as f:header=next(csv.reader([next(f)],delimiter='\t'))
assert len(header[1:])==704 and all(r['sample_id'] in header[1:] for r in roster)
inputs=[{'role':'Hofvander_RNA','path':str(RNA),'sha256':sha(RNA),'bytes':RNA.stat().st_size,'numeric_cells_read':False},{'role':'Hofvander_metadata','path':str(M),'sha256':sha(M),'bytes':M.stat().st_size}]
sc={}
for n in ['HOFVANDER-SCHEMA.json','ARRAY-PROBE-ANNOTATION.json','ARRAY-CONDITION-ROSTERS.json','GSE28866-ASSAY-AND-PEAK-ANNOTATION.json','TEMPO-FILTERED-SCHEMA-ONLY.json']:
 f=SC/n;assert f.exists(),n;sc[n]=json.loads(f.read_text());inputs.append({'role':'readiness:'+n,'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'numeric_cells_read':False})
annotation=sc['ARRAY-PROBE-ANNOTATION.json'];assert [r['probe'] for r in annotation['GPL6244']]==['8131844'];assert set(r['probe'] for r in annotation['GPL3290'])=={'5535','10100','19562'}
arrayrows=sc['ARRAY-CONDITION-ROSTERS.json']['all58_source_records'];assert len(arrayrows)==58
s3=sc['GSE28866-ASSAY-AND-PEAK-ANNOTATION.json'];assert len(s3['EMC_header_columns'])==4;assert {str(r['peak']) for r in s3['GPNMB_candidate_peak_annotations']}=={'10146','10147'}
ZIP=Path(annotation['source']['path']);assert sha(ZIP)==annotation['source']['sha256'];inputs.append({'role':'original_array_zip','path':str(ZIP),'sha256':sha(ZIP),'bytes':ZIP.stat().st_size,'numeric_cells_read':False})
SOFT=ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz';assert sha(SOFT)=='98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37';inputs.append({'role':'GSE24369_SOFT','path':str(SOFT),'sha256':sha(SOFT),'bytes':SOFT.stat().st_size,'numeric_cells_read':False})
# Hash raw source bytes for provenance, without parsing any gene measurements.
for binding in s3['source_bindings']:
 f=Path(binding['path']);assert sha(f)==binding['sha256'];inputs.append({'role':'3SEQ_source','path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'numeric_cells_read':False})
T=ROOT/'research/autonomy/tmem266-tissue-2026-10-03/peerj-source-s009.xlsx';assert sha(T)=='20165fd3ff09ec2d5a24b3c20b78515f42a3309119f248ed055c7484deb45e75';inputs.append({'role':'published_TempO_Log2CPM','path':str(T),'sha256':sha(T),'bytes':T.stat().st_size,'numeric_cells_read':False})
sets={}
for scope in ['all_conditions','primary_lesions','primary_non_known_overlap']:
 selected=roster if scope=='all_conditions' else [r for r in roster if r['primary_lesion'] and (scope!='primary_non_known_overlap' or not r['known_overlap'])]
 sets[scope]={h:[r['sample_id'] for r in selected if r['diagnosis']==h] for h in hists}
assert [len(sets[k][hists[0]]) for k in sets]==[13,12,9]
dump('FROZEN-SPECIMEN-UNITS.json',{'source_meta_sha256':sha(M),'Hofvander':roster,'sets':sets,'ARRAY_SOURCE_RECORDS':arrayrows,'3SEQ_source_conditions':s3['EMC_header_columns'],'3SEQ_comparator_conditions':s3['comparison_headers'],'TempO_context_schema_source':{'path':str(SC/'TEMPO-FILTERED-SCHEMA-ONLY.json'),'sha256':sha(SC/'TEMPO-FILTERED-SCHEMA-ONLY.json')},'not_donor_independence':'Source conditions/specimens, unknown cross-source or undisclosed within-source donor overlap. No pooled inference.'})
dump('INPUT-LOCK.json',{'inputs':inputs,'numeric_cells_read':False,'network_requests':0,'new_raw_retained_bytes':0})
dump('PREPARED-WIRING.json',{'date':'2026-10-05','prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Headers/annotations/condition metadata/hash binding only; outcome extraction disabled','Hofvander':{'matrix_header':header[0],'gene_symbol':'GPNMB','library_columns':704,'selected_condition_counts':counts,'sensitivity_counts':{k:{h:len(v) for h,v in vv.items()} for k,vv in sets.items()}},'arrays':{'GPL6244_features':['8131844'],'GPL3290_features':['5535','10100','19562'],'all_EMC_counts':{'GSE24369':6,'GSE4303':10},'GSE4303_reference_rule':'CRH-mRNA EMC, CRH DFSP and UHR GIST kept separate; no primary LGFMS/MLPS replication or mixed-reference comparison'},'3SEQ':{'features':['10146','10147'],'condition_count':4,'aggregation':'Median of both finite fixed coding-peak values on deposited square-root-density scale, plus every per-peak output; never linear gene-count sum','comparators':'MLPS6 secondary/SS3 contextual; noLGFMS','annotation_only':s3['GPNMB_candidate_peak_annotations']},'TempO':'Published processed all12 Log2CPM conditional native context; noLGFMS comparison, source-unit/condition metadata pending; raw estimator failure irrelevant','finite_cell_completeness':'Not yet evaluated; nozero imputation or premature all-condition completeness','authorization':'Explicit integrating-lead authorization against frozen contract and final dependency hashes required before any numeric cells/statistics. This executable has no numeric extraction mode.'})
print(json.dumps({'metadata_conditions':counts,'EMC_sensitivities':[13,12,9],'unique_array_features':[1,3],'3SEQ_features':2,'new_values_read':0,'raw_retained_bytes':0}))
