import pathlib,json,urllib.request,hashlib,datetime,re,concurrent.futures
B=pathlib.Path(__file__).resolve().parent
plan=json.loads((B/'PLAN-FROZEN.json').read_text())
def get(x):
 rec={**x,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET','no_authentication':True}
 p=B/'raw-cache'/('integration.ipynb' if x['repository_path'].endswith('.ipynb') else 'allcells-export.R')
 try:
  req=urllib.request.Request(x['url'],headers={'User-Agent':'EMC-source-metadata-research/1.0'})
  with urllib.request.urlopen(req,timeout=25) as r:
   data=r.read(x['cap']+1);rec.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'))
  if len(data)>x['cap']:raise ValueError('source exceeds frozen cap')
  p.write_bytes(data);rec.update(cache_path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1_actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
  rec['blob_matches']=rec['git_blob_sha1_actual']==x['git_blob_sha1']
  if not rec['blob_matches']:raise ValueError('actual source changed from frozen git blob')
 except Exception as e:rec['error']=type(e).__name__+': '+str(e)
 return rec
if (B/'ACCESS.json').exists():
 recs=json.loads((B/'ACCESS.json').read_text())
else:
 recs=list(concurrent.futures.ThreadPoolExecutor(2).map(get,plan['branches']))
 (B/'ACCESS.json').write_text(json.dumps(recs,indent=2)+'\n')
# Input source only; notebook outputs and structural/classification content remain unread.
blocked=re.compile(r'numbat|cnv|cna|copy.?num|chromos|FAP|HLA|glycan|gene|protein|expression|malignant|tumou?r|cluster|cell.?type|cell.?class|annotation|clone|assign',re.I)
keep=re.compile(r'gs001|gs002|orig\.ident|\bsample\b|samp\.|patient|donor|barcode|readRDS|write|save|h5ad|read_h5ad|metadata|meta\.data|pat_list|Sarcoma|all_cells_rds|output_h5seurat',re.I)
reports=[]
for rec in recs:
 if rec.get('error'):continue
 p=pathlib.Path(rec['cache_path'])
 if p.suffix=='.ipynb':
  nb=json.loads(p.read_text());parts=[(i,c.get('cell_type'),''.join(c.get('source',[]))) for i,c in enumerate(nb.get('cells',[])) if c.get('cell_type')=='code'];outcells=sum(bool(c.get('outputs')) for c in nb.get('cells',[]));outputs_read=False
 else:parts=[(0,'plain_code',p.read_text())];outcells=0;outputs_read=False
 accepted=[];skipped=0;schema=[];files=[]
 for i,typ,code in parts:
  for ln,line in enumerate(code.splitlines(),1):
   # Record field-name schema only; never associated values/classification assignments.
   if blocked.search(line):skipped+=1;continue
   schema+=re.findall(r'(?:meta\.data\$|obs\[\s*[\'\"])([A-Za-z_][\w.]*)',line)
   if keep.search(line):
    accepted.append({'source_cell':i,'source_line':ln,'text':line})
    if re.search(r'readRDS|read_h5ad|write|save|h5ad',line,re.I):
     files+=re.findall(r'[\'\"]([^\'\"]+)[\'\"]',line)
 reports.append({'source':rec['repository_path'],'source_sha256':rec['sha256'],'git_blob_verified':rec['blob_matches'],'notebook_output_cells_present':outcells,'notebook_outputs_inspected':outputs_read,'safe_source_lines':accepted,'metadata_field_names_schema_only':sorted(set(schema)),'read_save_literal_strings':files,'restricted_or_gene_or_classification_lines_skipped':skipped,'limit':'Metadata field schema is not cell classification validity or diagnosis. Direct path strings/local objects do not prove public files.'})
(B/'SAFE-SOURCE-METADATA-OBSERVATIONS.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps({'requests':len(recs),'errors':[r.get('error') for r in recs],'bytes':sum(r.get('bytes',0) for r in recs),'safe_schema_reports':len(reports)}))
