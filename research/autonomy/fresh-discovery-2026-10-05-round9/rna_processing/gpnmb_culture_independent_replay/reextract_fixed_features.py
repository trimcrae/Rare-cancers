import pathlib,json,hashlib,gzip,zipfile,io,decimal,datetime
D=decimal.Decimal
p=pathlib.Path(__file__).parent
paths={'ARCHS4':'/workspace/Rare-cancers/research/autonomy/tmem266-all-cultures-2026-10-04/archs4-subset.zip','USZ22':'/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round9/clinical_measurements/gpnmb_culture_identifier_capture/raw-cache/USZ22-fullcounts.tsv.gz','USZ23':'/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round8/surface_targets/source-cache/USZ23-RefSeq.quant.sf.gz'}
out={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_bindings':[{'context':k,'path':v,'sha256':hashlib.sha256(pathlib.Path(v).read_bytes()).hexdigest()} for k,v in paths.items()],'independent_before_owner_fullrows':True}
# ARCHS4 source header has an explicit blank leading index field; preserve it.
with zipfile.ZipFile(paths['ARCHS4']) as z:
 with io.TextIOWrapper(z.open('matrix.tsv')) as f:
  header=f.readline().rstrip('\n\r').split('\t');hits=[];rows=0
  for lineno,line in enumerate(f,2):
   label=line.split('\t',1)[0];rows+=1
   if label=='GPNMB':
    fields=line.rstrip('\n\r').split('\t');hits.append({'line':lineno,'data_row':lineno-1,'identifier':label,'lexemes':{gsm:fields[header.index(gsm)+(0 if header[0]=='' else 1)] for gsm in ['GSM2113301','GSM6883080']}})
  out['ARCHS4']={'header':header,'source_data_rows':rows,'symbol_hits':hits,'units':'rounded Kallisto estimated counts, no crossculture normalization/TPM/molecule total','unique_symbol':len(hits)==1,'whole_gene_capture_not_proved':True}
# Only the authorized one deposited sample column is converted; other gene/sample cells are not projected.
with gzip.open(paths['USZ22'],'rt') as f:
 header=f.readline().rstrip('\n\r').split('\t');idx=header.index('USZ-22_EMC2');hits=[];total=D(0);rows=0;invalid=[]
 for lineno,line in enumerate(f,2):
  fields=line.rstrip('\n\r').split('\t');rows+=1;val=D(fields[idx])
  if not val.is_finite() or val<0:invalid.append({'line':lineno,'reason':'nonfinite_or_negative'})
  else:total+=val
  if fields[0]=='GPNMB':hits.append({'line':lineno,'data_row':lineno-1,'identifier':fields[0],'column_index_zero_based':idx,'column':header[idx],'lexeme':fields[idx]})
 share=None
 if len(hits)==1 and not invalid and total>0:share=str(D(hits[0]['lexeme'])/total*D(1000000))
 out['USZ22']={'header':header,'source_data_rows':rows,'same_column_finite_nonnegative_rows':rows-len(invalid),'invalid':invalid,'GPNMB_hits':hits,'reported_count_sum_decimal':str(total),'per_million_reported_count_share_decimal':share,'units':'deposited gene count; denominator all reported same-column counts, not TPM/true molecules/read total','same_GSM_as_ARCHS4':'GSM6883080','header_duplicate_control_label':'NMFH-1 duplicate, not repaired/ordered/controltyped; uniqueUSZ22column exact','whole_condition_control_map_not_repaired':True}
fixed=['NM_001005340.2','NM_002510.3','XM_005249578.3','XM_017011678.2'];hits=[]
with gzip.open(paths['USZ23'],'rt') as f:
 header=f.readline().rstrip('\n\r').split('\t');t=header.index('TPM');n=header.index('NumReads')
 for lineno,line in enumerate(f,2):
  name=line.split('\t',1)[0]
  if name in fixed:
   fields=line.rstrip('\n\r').split('\t');hits.append({'line':lineno,'data_row':lineno-1,'Name':name,'TPM_lexeme':fields[t],'NumReads_lexeme':fields[n]})
 by={x['Name']:x for x in hits};valid=len(hits)==4 and len(by)==4 and all(D(x[k]).is_finite() and D(x[k])>=0 for x in hits for k in ['TPM_lexeme','NumReads_lexeme'])
 out['USZ23']={'header':header,'fixed_features_in_prespecified_order':[by.get(n) for n in fixed],'all_four_unique_finite_nonnegative':valid,'partial_TPM_subtotal_decimal':str(sum((D(by[x]['TPM_lexeme']) for x in fixed),D(0))) if valid else None,'partial_NumReads_subtotal_decimal':str(sum((D(by[x]['NumReads_lexeme']) for x in fixed),D(0))) if valid else None,'units':'source Salmon transcriptTPM and NumReads, fixedPARTIALfour-feature subtotal, not whole-gene completeness or geneTPM','no_length_or_effective_length_projection':True}
(p/'INDEPENDENT-RAW-FEATURE-EXTRACTION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
