import datetime,hashlib,json,pathlib,urllib.parse,urllib.request
import search_sources as s
B=s.BASE
base=json.loads((B/'FOCUSED-SEARCH-RECEIPTS.json').read_text());rec=next(r for r in base if r['key']=='MESENCHYMAL_FERROSTUDIES');q=rec['query'];cursor=rec.get('next_cursor');allrows=json.loads((B/'FOCUSED-SEARCH-CANDIDATES.json').read_text())['MESENCHYMAL_FERROSTUDIES'];receipts=[]
for page in range(2,6):
 if len(allrows)>=rec['hit_count']:break
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':'100','resultType':'core','cursorMark':cursor})
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-pilot/1.0'}),timeout=45) as r:b=r.read(8*1024*1024+1)
 assert len(b)<8*1024*1024;used=sum(p.stat().st_size for p in B.rglob('*') if p.is_file());assert used+len(b)<s.MAX and s.shutil.disk_usage(B).free-len(b)>10*1024**3
 p=B/'raw'/('mesenchymal-page'+str(page)+'.json');p.write_bytes(b);o=json.loads(b);rows=o.get('resultList',{}).get('result',[]);cursor=o.get('nextCursorMark');receipts.append({'page':page,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'returned':len(rows),'hit_count':o.get('hitCount'),'cache_path':'raw/'+p.name})
 for x in rows:allrows.append({k:x.get(k) for k in ['id','source','pmid','pmcid','doi','title','pubYear','authorString','isOpenAccess']})
 if not rows:break
(B/'MESENCHYMAL-COMPLETE-METADATA.json').write_text(json.dumps({'query':q,'hit_count':rec['hit_count'],'returned':len(allrows),'unique_source_ids':len({str(x['source'])+str(x['id']) for x in allrows}),'complete':len(allrows)>=rec['hit_count'],'rows':allrows},indent=2)+'\n');(B/'PAGINATION-RECEIPTS.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('returned',len(allrows),'of',rec['hit_count'])
for x in allrows:
 t=x['title'].lower()
 if 'therapy-resistant state' in t or 'drug-tolerant persister' in t or 'sarcoma' in t:print(x['id'],x.get('pmcid'),x.get('doi'),x['title'])
