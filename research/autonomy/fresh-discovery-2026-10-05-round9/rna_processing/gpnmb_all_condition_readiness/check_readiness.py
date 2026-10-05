"""GPNMB source/annotation/header readiness only; never parses expression cells."""
import csv,gzip,hashlib,io,json,zipfile,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
BASE=Path('/workspace/Rare-cancers/research/autonomy')
Z=BASE/'atlas-original-array-source-2026-09-06/original-source-recovery.zip'
SOFT=BASE/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
M=BASE/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
TPM=BASE/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
SEQ=Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory/raw-cache/GSE28866_normalized.txt.gz')
SERIES=Path('/workspace/Rare-cancers/research/modalities/geo-gse28866-brunner-series.json')
TARGET='GPNMB'
def write(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
def bind(q,scope):
 b=q.read_bytes();return {'path':str(q),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'scope':scope}
meta=json.loads(M.read_text()); emc=[x for x in meta['samples'] if x['diagnosis']=='Extraskeletal myxoid chondrosarcoma'];assert len(emc)==13
with gzip.open(TPM,'rt') as f:
 hdr=f.readline().rstrip('\n').split('\t'); symbol_rows=0
 for line in f:
  # Inspect row identity before first tab only. Remainder never parsed.
  symbol=line.partition('\t')[0]
  if symbol==TARGET:symbol_rows+=1
columns=set(hdr[1:]);assert all(x['sample_id'] in columns for x in emc)
write('HOFVANDER-SCHEMA.json',{'source_bindings':[bind(TPM,'Header and first-column symbol identity only; no TPM cells'),bind(M,'Source sample diagnosis/condition/overlap metadata')],'symbol':TARGET,'symbol_rows':symbol_rows,'library_columns':len(hdr)-1,'all13_EMC_header_present':True,'EMC_conditions':emc,'comparator_conditions':[{k:x.get(k) for k in ['sample_id','diagnosis','source_label','sequencing_year','known_overlap','patient_group','primary_lesion']} for x in meta['samples'] if x['diagnosis'] in ['Low-grade fibromyxoid sarcoma','Myxoid liposarcoma','Synovial sarcoma']],'units':'Deposited geneTPM; no native protein/malignant-cell source/dependency inferred','finite_gene_values_evaluated':False})
with zipfile.ZipFile(Z) as z:
 roster=json.loads(z.read('sample-rosters.json')); maps={}; ambiguity=[]
 cache=json.loads(z.read('accession-symbol-cache.json'))['by_source'];bridge={}
 for priority in ['remote_lookup','unigene_archive','curated_annotation']:bridge.update(cache[priority])
 for name,platform in [('GPL6244-original-annotation.tsv','GPL6244'),('GPL3290-original-annotation.tsv','GPL3290')]:
  matched=[]
  with io.TextIOWrapper(z.open(name)) as f:
   for r in csv.DictReader(f,delimiter='\t'):
    unmapped=[]
    if platform=='GPL6244':
     syms=set(a.split(' // ')[1] for a in r['gene_assignment'].split(' /// ') if len(a.split(' // '))>1)
    else:
     syms=set()
     for acc in r.get('GB_LIST','').replace(';',',').split(','):
      acc=acc.strip()
      if not acc:continue
      v=bridge.get(acc);sym=v if isinstance(v,str) else (v.get('symbol') or v.get('gene_symbol')) if isinstance(v,dict) else None
      if sym:syms.add(sym)
      else:unmapped.append(acc)
    if TARGET in syms:
     record={'probe':r['ID'],'symbols':sorted(syms),'unmapped_accessions':unmapped,'original_annotation':r,'annotation_status':'single-symbol source annotation' if syms=={TARGET} else 'multiple-symbol ambiguous source annotation'}
     matched.append(record)
     if syms!={TARGET}:ambiguity.append({'platform':platform,**record})
  maps[platform]=matched
 write('ARRAY-PROBE-ANNOTATION.json',{'source':bind(Z,'Original probe annotations, source rosters and accession-symbol cache only'),'GPL6244':maps['GPL6244'],'GPL3290':maps['GPL3290'],'ambiguous_records':ambiguity,'limits':['Mapping is not evaluated GPNMB array measurement','GPL3290 legacy accession bridge provenance reused, not fresh genome-wide crosshybridization validation','Unmapped accessions preserved; no transcript absence inference','Do not silently choose a favorable probe after outcomes']})
 write('ARRAY-CONDITION-ROSTERS.json',{'all58_source_records':roster,'EMC_counts':{ds:sum(r['gse']==ds and 'chondrosarcoma' in r['title'].lower() for r in roster) for ds in ['GSE24369','GSE4303']},'scope':'Disease/source/reference/processing identity only; no value cells','units':'GSE24369 processedRMAlog2; GSE4303 depositedlog2Channel2/Channel1reference ratios. Different reference/capture conditions remain visible.'})
 probes={plat:{r['probe'] for r in entries if r['symbols']==[TARGET]} for plat,entries in maps.items()}
 presence={};sid=None;table=False;head=False
 with gzip.open(SOFT,'rt') as f:
  for line in f:
   if line.startswith('^SAMPLE = '):sid=line.strip().split(' = ')[1];presence[sid]={'probe_ids_present':[],'header':None}
   elif line.strip()=='!sample_table_begin':table=True;head=True
   elif line.strip()=='!sample_table_end':table=False
   elif table:
    if head:presence[sid]['header']=line.rstrip('\n');head=False;continue
    probe=line.partition('\t')[0]
    if probe in probes['GPL6244']:presence[sid]['probe_ids_present'].append(probe)
 with z.open('GSE4303-GPL3290-source-matrix.gz') as b:
  with gzip.open(b,'rt') as f:
   in_table=False;h=None;present=[]
   for line in f:
    if line.startswith('!series_matrix_table_begin'):in_table=True;continue
    if line.startswith('!series_matrix_table_end'):break
    if in_table:
     if h is None:h=next(csv.reader([line],delimiter='\t'));continue
     probe=line.partition('\t')[0].strip('"')
     if probe in probes['GPL3290']:present.append(probe)
   for gsm in h[1:]:presence[gsm]={'probe_ids_present':present,'header':h[0]}
 write('ARRAY-PROBE-INDEX-PRESENCE.json',{'scope':'Only probe-ID row indexes and table headers checked; expression cells never parsed or evaluated','conditions':[{'gse':r['gse'],'gsm':r['gsm'],'title':r['title'],**presence.get(r['gsm'],{'missing_source_index':True})} for r in roster],'finite_or_missing_expression_cells_evaluated':False})
s=json.loads(SERIES.read_text());ids=['GSM715466','GSM715467','GSM715470','GSM715472'];ss=[x for x in s['samples'] if x['accession'] in ids];assert len(ss)==4
with gzip.open(SEQ,'rt') as f:
 sh=f.readline().rstrip('\n').split('\t'); peaks=[]
 for line in f:
  # First six annotation fields only. Published differential-expression field7 and all numeric cells stay closed.
  a=line.rstrip('\n').split('\t',6)[:6]
  if len(a)<6:continue
  if TARGET in (a[4].replace(';',',').split(',')+a[5].replace(';',',').split(',')):
   peaks.append(dict(zip(sh[:6],a)))
sc=[x for x in sh[7:] if x.startswith('EMC_')];assert set(sc)=={'EMC_STT5525','EMC_STT5526','EMC_STT5527','EMC_STT5592'}
write('GSE28866-ASSAY-AND-PEAK-ANNOTATION.json',{'source_bindings':[bind(SERIES,'Exact4GSMsource assay/identity records plus series normalization description'),bind(SEQ,'Header/first6annotationfields only; differential-expression annotations and numeric values uninspected')],'EMC_source_records':ss,'EMC_header_columns':sc,'library_columns':len(sh)-7,'annotation_header':sh[:7],'GPNMB_candidate_peak_annotations':peaks,'comparison_headers':[x for x in sh[7:] if x.startswith(('MLPS_','SS_','LGFMS_'))],'normalized_units':'Sequencing-depth-scaled mean and then square-root-compressed pooled-readstartpeak3SEQ density, hg18 annotations; not geneTPM, cleavage/PASusage or protein. Aggregation must be frozen before outcomes; multi-symbol/discordant peak annotation cannot be silently chosen.','finite_or_missing_peak_values_evaluated':False,'differentially_expressed_cancer_type_field_read':False,'donor_rule':'Four source-described3SEQ conditions; unknown cross-study overlap and direct fusion authentication, distinctSTT aliases notproofindependentdonors.'})
print(json.dumps({'GPNMB_symbol_rows':symbol_rows,'Hof_EMC':len(emc),'array_probes':{k:len(v) for k,v in maps.items()},'array_EMC_counts':{ds:sum(r['gse']==ds and 'chondrosarcoma' in r['title'].lower() for r in roster) for ds in ['GSE24369','GSE4303']},'3SEQ_conditions':sc,'GPNMB_peak_annotations':len(peaks),'new_gene_values':0}))
