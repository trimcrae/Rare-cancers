#!/usr/bin/env python3
"""Official symbol annotation and measured probe-ID metadata only; no values."""
from pathlib import Path
import gzip,hashlib,json
P=Path(__file__).resolve().parent
F=Path('/workspace/Rare-cancers/research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz')
GENES=['GPNMB','LST1','TYROBP','AIF1','CSF1R','CD68','FCER1G','COL1A1','COL1A2','DCN','PDGFRA']
rows={g:[] for g in GENES};samples={};native_meta={};mode=None;sample=None;header=None
with gzip.open(F,'rt') as f:
 for line in f:
  if line.startswith('^SAMPLE ='):
   sample=line.split('=',1)[1].strip();samples[sample]=set();native_meta[sample]={};mode=None
  elif line.startswith('!platform_table_begin'):mode='platform_header'
  elif line.startswith('!platform_table_end'):mode=None
  elif line.startswith('!sample_table_begin'):mode='sample_header'
  elif line.startswith('!sample_table_end'):mode=None
  elif mode=='platform_header':header=line.rstrip('\n').split('\t');mode='platform'
  elif mode=='platform':
   # No coordinate/sequence/gene-description fields accessed.
   v=line.rstrip('\n').split('\t');gene_assignment=v[header.index('gene_assignment')]
   symbols=set()
   for part in gene_assignment.split('///'):
    fields=part.split('//')
    if len(fields)>1:symbols.add(fields[1].strip())
   symbols.discard('---');symbols.discard('')
   for g in GENES:
    if g in symbols:rows[g].append({'probe_id':v[0],'source_gene_symbols':sorted(symbols),'symbol_status':'single_gene' if symbols=={g} else 'ambiguous_multi_gene'})
  elif mode=='sample_header':mode='sample'
  elif mode=='sample':
   # Discard rest of line without parsing the expression-value column.
   samples[sample].add(line.split('\t',1)[0])
  elif sample is not None and line.startswith(('!Sample_title =','!Sample_source_name_ch1 =')):
   k,v=map(str.strip,line.split('=',1));native_meta[sample][k]=v
assert len(samples)==42
common=set.intersection(*samples.values())
for g,rr in rows.items():
 for r in rr:
  r['measured_all42']=r['probe_id'] in common
  r['eligible']=r['symbol_status']=='single_gene' and r['measured_all42']
assert all('GSM'+str(n) in samples for n in range(600934,600940))
b=F.read_bytes();d={'source_path':str(F),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'scope':'OriginalGPL6244gene-symbol assignment + all42first-columnprobeIDs only; no expression columns parsed','all_source_samples':sorted(samples),'all6native_sample_identity':{g:native_meta[g] for g in ['GSM'+str(n) for n in range(600934,600940)]},'fixed_gene_all_probe_statuses':rows,'missing_or_unsupported_single_gene':[g for g,r in rows.items() if not any(x['eligible'] for x in r)],'mapping_rule':'Exactsymbolfield1 in eachoriginal gene_assignment //entry, union across///; allmulti-symbol mappings retained/ambiguous, all42IDmembership required, no modernannotation/alias/imputedzero.'}
(P/'SOURCE-PROBE-READINESS.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'eligible_counts':{g:sum(r['eligible'] for r in rr) for g,rr in rows.items()},'unsupported':d['missing_or_unsupported_single_gene'],'all_source_samples':len(samples),'native_samples':len(d['all6native_sample_identity'])}))
