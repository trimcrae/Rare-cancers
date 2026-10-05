import pathlib,json,urllib.request,hashlib,datetime,concurrent.futures,urllib.parse
B=pathlib.Path(__file__).resolve().parent
p=json.loads((B/'PLAN-FROZEN.json').read_text())
def get(s):
 r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'name':s['name'],'url':s['url'],'cap':s['cap'],'operation':'GET publicannotationmetadata only'}
 try:
  with urllib.request.urlopen(s['url'],timeout=25) as f:
   body=f.read(s['cap']+1);r['status']=f.status;r['final_url']=f.url
  if len(body)>s['cap']:raise ValueError('frozen cap exceeded')
  q=B/'raw-cache'/(s['name']+'.json');q.write_bytes(body);r.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),cache_path=str(q))
 except Exception as e:r['error']=type(e).__name__+': '+str(e)
 return r
if not (B/'ANNOTATION-ACCESS.json').exists():
 a=list(concurrent.futures.ThreadPoolExecutor(2).map(get,p['new_annotation_routes']))
 (B/'ANNOTATION-ACCESS.json').write_text(json.dumps(a,indent=2)+'\n')
else:a=json.loads((B/'ANNOTATION-ACCESS.json').read_text())
out={'stage':'Official annotation metadata, no expression or sequence','source_access':a,'gene_identity':None,'refseq_linkage':None}
if not any(x.get('error') for x in a):
 g=json.loads(pathlib.Path(a[0]['cache_path']).read_text())['result']['10457']
 out['gene_identity']={k:g.get(k) for k in ['uid','name','description','status','organism']}
 # organism contains taxon/name only; do not project genomicInfo/locus/maps.
 l=json.loads(pathlib.Path(a[1]['cache_path']).read_text());sets=l.get('linksets',[])
 if len(sets)==1 and sets[0].get('ids')==['10457']:
  db=[x for x in sets[0].get('linksetdbs',[]) if x.get('linkname')=='gene_nuccore_refseqrna' and x.get('dbto')=='nuccore']
  if len(db)==1:out['refseq_linkage']={'GeneID':'10457','expected_source':'gene','target_database':'nuccore','linkname':'gene_nuccore_refseqrna','uids':db[0].get('links',[])}
 valid=out['gene_identity'].get('name')=='GPNMB' and out['gene_identity'].get('organism',{}).get('taxid')==9606 and out['refseq_linkage'] is not None
 out['identity_link_gate_pass']=valid
 if valid:
  uids=out['refseq_linkage']['uids'];url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=nuccore&id='+urllib.parse.quote(','.join(uids),safe='')+'&retmode=json'
  plan={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_GeneID':'10457','fixed_uids':uids,'url':url,'name':'GPNMB-current-RefSeqRNA-summary','cap':262144,'fields':'UID/accessionversion,title,gene_name,organism/taxon,moltype metadata only; no sequence/expression, no matrixbody','source_hashes':[x['sha256'] for x in a]}
  (B/'ANNOTATION-SUMMARY-ROUTE-FROZEN.json').write_text(json.dumps(plan,indent=2)+'\n')
(B/'OFFICIAL-GENE-LINKAGE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'errors':[x.get('error') for x in a],'gene_identity':out['gene_identity'],'linkage':out['refseq_linkage'],'gate':out.get('identity_link_gate_pass')}))
