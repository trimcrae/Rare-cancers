import pathlib,json,hashlib,gzip,zipfile,io,datetime,decimal,shutil
P=pathlib.Path(__file__).resolve().parent
plan=json.loads((P/'PLAN-FROZEN.json').read_text());deadline=datetime.datetime.fromisoformat(plan['deadline_utc'])
def guard():
 if datetime.datetime.now(datetime.timezone.utc)>=deadline: raise RuntimeError('Scientific deadline reached; no further quantities')
guard()
if shutil.disk_usage(P).free<10*1024**3: raise RuntimeError('Free storage minimum')
D=decimal.Decimal
sources=plan['fixed_sources']
for s in sources:
 if hashlib.sha256(pathlib.Path(s['path']).read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('Source hash mismatch')
results={'measured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':hashlib.sha256((P/'PLAN-FROZEN.json').read_bytes()).hexdigest(),'network_requests':0,'sources':sources,'conditions':[]}
# Only two fixed columns on the unique fixed symbol row; other quantities stay uninspected.
with zipfile.ZipFile(sources[0]['path']) as z:
 with io.TextIOWrapper(z.open('matrix.tsv')) as f:
  header=f.readline().rstrip('\r\n').split('\t');hits=[]
  for num,line in enumerate(f,2):
   name=line.split('\t',1)[0]
   if name=='GPNMB':
    guard();parts=line.rstrip('\r\n').split('\t');hits.append(num)
    for gsm in ['GSM2113301','GSM6883080']:
     col=header.index(gsm);token=parts[col];value=D(token)
     if not value.is_finite() or value<0:raise RuntimeError('Invalid fixed estimated count')
     results['conditions'].append({'model':'V1-34' if gsm=='GSM2113301' else 'USZ22','GSM':gsm,'assay':'ARCHS4 rounded Kallisto estimated counts','source_row_number':num,'identifier':'GPNMB','source_column':col,'reported_value':token,'units':'rounded estimated count; not aligned reads or TPM','normalized_quantity':None,'capture':'Unique exact symbol; mixed namespace and historical capture limits retained'})
  if hits!=[7248]:raise RuntimeError('Unexpected exact symbol capture')
# Full SAME-column denominator only; no other target/culture quantities exported.
with gzip.open(sources[2]['path'],'rt') as f:
 header=f.readline().rstrip('\r\n').split('\t');col=header.index('USZ-22_EMC2')
 if col!=10 or header.count('USZ-22_EMC2')!=1:raise RuntimeError('Ambiguous EMC source column')
 total=D(0);n=0;invalid=0;target=[]
 for num,line in enumerate(f,2):
  guard();parts=line.rstrip('\r\n').split('\t');n+=1
  try:v=D(parts[col]);valid=v.is_finite() and v>=0
  except (decimal.InvalidOperation,IndexError):valid=False
  if valid:total+=v
  else:invalid+=1
  if parts[0]=='GPNMB':target.append((num,parts[col],v if valid else None))
 if len(target)!=1 or target[0][0]!=9957:raise RuntimeError('Target capture mismatch')
 numerator=target[0][2];share=D(1000000)*numerator/total if invalid==0 and total>0 and numerator is not None else None
 results['conditions'].append({'model':'USZ22','GSM':'GSM6883080','assay':'Deposited Dragen/Salmon tximport raw gene-count column','source_row_number':9957,'identifier':'GPNMB','source_column':10,'reported_gene_count':target[0][1],'full_reported_feature_rows':n,'invalid_or_negative_reported_counts':invalid,'denominator_reported_count_sum':str(total) if invalid==0 else None,'per_million_reported_count_share':str(share) if share is not None else None,'denominator_scope':'Sum of all 54,507 deposited reported gene-count entries in the one USZ22 column; not read total, TPM, molecule fraction or validated detectability','library_reuse':'Same GSM/library as ARCHS4 USZ22, not independent replicate','capture':'Unique symbol; annotation release/scaling options not fully specified; ambiguous other controls not repaired'})
fixed={'NM_001005340.2':1573,'NM_002510.3':45035,'XM_005249578.3':82213,'XM_017011678.2':114704};features=[]
with gzip.open(sources[1]['path'],'rt') as f:
 header=f.readline().rstrip('\r\n').split('\t')
 for num,line in enumerate(f,2):
  name=line.split('\t',1)[0]
  if name in fixed:
   guard();parts=line.rstrip('\r\n').split('\t')
   if num!=fixed[name]:raise RuntimeError('Transcript row changed')
   tpm=parts[header.index('TPM')];count=parts[header.index('NumReads')]
   if any(not D(x).is_finite() or D(x)<0 for x in [tpm,count]):raise RuntimeError('Invalid transcript value')
   features.append({'source_row_number':num,'Name':name,'reported_TPM':tpm,'reported_NumReads':count,'version_status':'exact current NM version' if name.startswith('NM_') else 'historical XM version with source-qualified current accession-base association'})
if len(features)!=4:raise RuntimeError('Fixed partial feature capture incomplete')
results['conditions'].append({'model':'USZ23','GSM':'GSM9037837','assay':'Deposited RefSeq transcript quantification','features':features,'partial_four_feature_TPM_subtotal':str(sum((D(x['reported_TPM']) for x in features),D(0))),'partial_four_feature_NumReads_subtotal':str(sum((D(x['reported_NumReads']) for x in features),D(0))),'capture':'PARTIAL four-feature capture, never complete whole-gene TPM. Three current accession bases unmatched and retired/historical index completeness unresolved; missing is not zero.','normalized_across_contexts':False})
guard();results['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
results['limitations']='No assay pooling, cross-platform magnitude/ranking, culture threshold, tissue replication, protein/compartment/dependency/clinical inference. Other authentic models unlocated processed GPNMB inputs remain pending.'
(P/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
