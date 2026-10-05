"""Header/annotation-only fixed RNA-symbol coverage; never parse expression cells."""
from pathlib import Path
import csv,gzip,io,json,zipfile,hashlib,datetime
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
BASE=Path('/workspace/Rare-cancers/research/autonomy')
GENES=['GPNMB','LST1','TYROBP','AIF1','CSF1R','CD68','FCER1G','COL1A1','COL1A2','DCN','PDGFRA']
LOCK=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/gpnmb_exploratory_analysis_contract/INPUT-LOCK.json')
lock=json.loads(LOCK.read_text()); bindings=[]
for r in lock['inputs']:
 if r['role'] in ['Hofvander_RNA','Hofvander_metadata','original_array_zip','GSE24369_SOFT','published_TempO_Log2CPM'] or (r['role']=='3SEQ_source' and r['path'].endswith('.gz')):
  q=Path(r['path']);b=q.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];bindings.append(r)
meta=json.loads((BASE/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text()); emc=[r['sample_id'] for r in meta['samples'] if r['diagnosis']=='Extraskeletal myxoid chondrosarcoma'];assert len(emc)==13
with gzip.open(BASE/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt') as f:
 h=f.readline().rstrip('\n').split('\t');seen={g:[] for g in GENES}
 for n,line in enumerate(f,2):
  g=line.partition('\t')[0]
  if g in seen:seen[g].append(n)
 assert all(x in h[1:] for x in emc)
with zipfile.ZipFile(BASE/'atlas-original-array-source-2026-09-06/original-source-recovery.zip') as z:
 rosters=json.loads(z.read('sample-rosters.json'));cache=json.loads(z.read('accession-symbol-cache.json'))['by_source'];bridge={}
 for name in ['remote_lookup','unigene_archive','curated_annotation']:bridge.update(cache[name])
 maps={}
 for name,plat in [('GPL6244-original-annotation.tsv','GPL6244'),('GPL3290-original-annotation.tsv','GPL3290')]:
  maps[plat]={g:[] for g in GENES}
  with io.TextIOWrapper(z.open(name)) as f:
   for r in csv.DictReader(f,delimiter='\t'):
    unresolved=[]
    if plat=='GPL6244':syms=set(a.split(' // ')[1] for a in r['gene_assignment'].split(' /// ') if len(a.split(' // '))>1)
    else:
     syms=set()
     for acc in r.get('GB_LIST','').replace(';',',').split(','):
      acc=acc.strip()
      if not acc:continue
      v=bridge.get(acc);s=v if isinstance(v,str) else (v.get('symbol') or v.get('gene_symbol')) if isinstance(v,dict) else None
      if s:syms.add(s)
      else:unresolved.append(acc)
    for g in syms.intersection(GENES):maps[plat][g].append({'probe':r['ID'],'symbols':sorted(syms),'unmapped_accessions':unresolved,'unique_symbol':syms=={g}})
seq=Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory/raw-cache/GSE28866_normalized.txt.gz')
with gzip.open(seq,'rt') as f:
 h3=f.readline().rstrip('\n').split('\t');peaks={g:[] for g in GENES}
 for n,line in enumerate(f,2):
  a=line.rstrip('\n').split('\t',6)[:6]
  if len(a)!=6:continue
  syms=set(a[4].replace(';',',').split(',')+a[5].replace(';',',').split(','))
  for g in syms.intersection(GENES):peaks[g].append({'line_index':n,'annotation':dict(zip(h3[:6],a))})
 emc3=[x for x in h3[7:] if x.startswith('EMC_')];assert len(emc3)==4
# Read XLSX sharedStrings/header/column-A identities only; do not select expression cells.
xlsx=BASE/'tmem266-tissue-2026-10-03/peerj-source-s009.xlsx';ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(xlsx) as z:
 ss=ET.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(x.itertext()) for x in ss.findall('s:si',ns)]
 wb=ET.fromstring(z.read('xl/workbook.xml'));sheets=[x.get('name') for x in wb.findall('s:sheets/s:sheet',ns)]
 assert sheets==['EMC_Gene-expression_Log2CPM']
 data=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));found={g:[] for g in GENES};header=[]
 for row in data.findall('s:sheetData/s:row',ns):
  rn=int(row.get('r'))
  for c in row.findall('s:c',ns):
   ref=c.get('r');v=c.find('s:v',ns)
   if rn!=1 and not ref.startswith('A'):continue
   if v is None:continue
   value=strings[int(v.text)] if c.get('t')=='s' else v.text
   if rn==1:header.append(value)
   elif value in found:found[value].append(rn)
 assert len(header)==13
result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixed_symbols':GENES,'locked_inputs':bindings,'Hofvander':{'all13_conditions':emc,'symbol_row_indices':seen,'units':'Deposited gene TPM','status':'Header/unique-symbol prerequisite only; finite gene measurements unassessed in this new covariation question'},'arrays':{'annotations':maps,'native_conditions':{ds:[{k:r.get(k) for k in ['gse','gsm','title','source_name_ch1','source_name_ch2']} for r in rosters if r['gse']==ds and 'chondrosarcoma' in r['title'].lower()] for ds in ['GSE24369','GSE4303']},'units':'GSE24369 RMAlog2; GSE4303 log2 tumor/CRH reference ratios, not cross-source pooled'},'GSE28866':{'native_conditions':emc3,'fixed_symbol_peak_annotations':peaks,'units':'Four FFPE source-described3SEQ conditions; square-root-compressed sequencing-depth-scaled peak densities','limits':'No expression cells or differential-expression field7 read. All unique and ambiguous/coding/noncoding annotations retained; no silently chosen peaks. Separate assay context could test covariation without LGFMS controls if a full before-value protocol defines capture/composite/missing rules.'},'TempO':{'headers':header,'fixed_symbol_row_indices':found,'units':'Published UQ-normalized Log2CPM','status':'All12 native published processed columns retained. No LGFMS comparator is required for within-EMC covariation; individual Si/donor/clinical condition links and capture/selection still unresolved. Raw-estimator failure does not invalidate this table.'},'new_expression_values_parsed':0,'new_statistics':0,'network_requests':0,'new_originals':0}
(P/'FIXED-MARKER-SCHEMA-AND-CONDITIONS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'Hofvander_unique':{g:len(v) for g,v in seen.items()},'array_unique_probes':{p:{g:sum(r['unique_symbol'] for r in rr) for g,rr in mm.items()} for p,mm in maps.items()},'3SEQ_annotations':{g:len(v) for g,v in peaks.items()},'TempO_symbol_rows':{g:len(v) for g,v in found.items()},'new_values':0}))
