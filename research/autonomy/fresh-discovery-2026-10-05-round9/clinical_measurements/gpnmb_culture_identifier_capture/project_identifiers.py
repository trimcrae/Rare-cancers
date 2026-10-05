import pathlib,json,hashlib,datetime,urllib.request,zipfile,gzip,re
B=pathlib.Path(__file__).resolve().parent
P=json.loads((B/'PLAN-FROZEN.json').read_text())
D=datetime.datetime.fromisoformat(P['deadline_utc'])
def now():return datetime.datetime.now(datetime.timezone.utc)
def stop():
 if now()>=D:raise RuntimeError('Scientific deadline reached')
def put(n,j):(B/n).write_text(json.dumps(j,indent=2)+'\n')
rec={'utc':now().isoformat(),'url':P['sources'][2]['url'],'operation':'single ordinary GET declared publicgzip','cap':1048576}
q=B/'raw-cache/USZ22-fullcounts.tsv.gz'
if not (B/'USZ22-SOURCE-ACCESS.json').exists():
 try:
  stop()
  with urllib.request.urlopen(rec['url'],timeout=25) as f:
   body=f.read(1048577);rec.update(status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
  if len(body)>1048576:raise ValueError('cap exceeded')
  if not body.startswith(b'\x1f\x8b'):raise ValueError('not authentic gzip; no identifiers accepted')
  q.write_bytes(body);rec.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),cache_path=str(q))
 except Exception as e:rec['error']=type(e).__name__+': '+str(e)
 put('USZ22-SOURCE-ACCESS.json',rec)
else:rec=json.loads((B/'USZ22-SOURCE-ACCESS.json').read_text())
# Numeric columns are never split/parsed/converted or exported. Only first delimiter field.
accessions=P['fixed_current_GPNMB_accessions'];bases={x.split('.')[0]:x for x in accessions}
def kind(s):
 if re.fullmatch(r'ENSG\d+(?:\.\d+)?',s):return 'Ensembl_gene'
 if re.fullmatch(r'[NX][MR]_\d+(?:\.\d+)?',s):return 'RefSeq_RNA'
 if s.isdigit():return 'numeric_ID'
 return 'symbol_or_other'
def project(label,stream,source,limit=8388608):
 stop();header=stream.readline(4096).decode('utf-8').rstrip('\r\n').split('\t');path=B/'identifier-cache'/(label+'.first-column-identifiers.txt');rows=0;written=0;types={};hits=[]
 with path.open('wb') as out:
  for line in stream:
   stop();identifier=line.partition(b'\t')[0].rstrip(b'\r\n').decode('utf-8');rows+=1
   bs=(identifier+'\n').encode();written+=len(bs)
   if written>limit:raise ValueError('derived identifier catalogue cap')
   out.write(bs);types[kind(identifier)]=types.get(kind(identifier),0)+1
   base=identifier.split('.')[0]
   if identifier=='GPNMB' or identifier=='10457' or base in bases:
    hits.append({'source_row_number':rows+1,'identifier':identifier,'matching_rule':'exactofficialsymbol' if identifier=='GPNMB' else 'exactGeneID' if identifier=='10457' else 'currentRefSeqaccessionbase','current_accession':bases.get(base),'exact_current_version':identifier in accessions if base in bases else None})
 return {'label':label,'source':source,'header':header,'identifier_rows':rows,'identifier_namespace_counts':types,'identifier_projection_bytes':written,'identifier_catalogue_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'identifier_catalogue_cache_only':str(path),'matched_fixed_GPNMB_identifiers':hits,'numeric_fields_inspected':0,'scope':'Firstcolumn/Nameidentifiers only; no numeric fields or expression interpretation. Missingmatchnotgeneabsence.'}
res=[]
a=pathlib.Path(P['sources'][0]['path']);assert hashlib.sha256(a.read_bytes()).hexdigest()==P['sources'][0]['sha256']
with zipfile.ZipFile(a) as z:
 with z.open('matrix.tsv') as f:res.append(project('ARCHS4',f,{'path':str(a),'sha256':P['sources'][0]['sha256'],'condition_columns':['GSM2113301','GSM6883080']}))
u=pathlib.Path(P['sources'][1]['path']);assert hashlib.sha256(u.read_bytes()).hexdigest()==P['sources'][1]['sha256']
with gzip.open(u,'rb') as f:res.append(project('USZ23',f,{'path':str(u),'sha256':P['sources'][1]['sha256'],'condition':'GSM9037837'}))
if not rec.get('error'):
 with gzip.open(q,'rb') as f:res.append(project('USZ22',f,{'path':str(q),'sha256':rec['sha256'],'condition':'GSM6883080','actual_compressed_bytes':rec['bytes']}))
put('IDENTIFIER-PROJECTION.json',{'utc':now().isoformat(),'sources':res,'expression_values_inspected':0,'not_complete_historical_gene_capture':'Onlycurrentsevenofficialbases/symbol/GeneID evaluated; historicalretiredaccessions and quantificationindex remainunresolved withoutsourcesupportedmapping.'})
print(json.dumps([{k:x[k] for k in ['label','header','identifier_rows','identifier_namespace_counts','identifier_projection_bytes','matched_fixed_GPNMB_identifiers']} for x in res],indent=2))
