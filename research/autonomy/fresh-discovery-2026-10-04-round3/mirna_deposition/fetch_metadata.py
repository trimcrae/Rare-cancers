"""Resolve every returned repository UID to metadata; no assay values."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,time,shutil,collections
D=Path(__file__).resolve().parent;rr=json.loads((D/'entrez-search-receipts.json').read_text());uids=collections.defaultdict(set)
for r in rr:
    obj=r.get('result',{});ids=obj.get('idlist',[])
    assert int(obj.get('count','0'))==len(ids),'Search truncated; requires pagination'
    uids[r['db']].update(ids)
jobs=[]
for db,ids in uids.items():
    ids=sorted(ids,key=int)
    for at in range(0,len(ids),75):
        ss=ids[at:at+75];jobs.append((f'{db}-summaries-{at//75:02d}.json','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode({'db':db,'id':','.join(ss),'retmode':'json','version':'2.0'}),{'db':db,'uids':ss}))
for i,q in enumerate(['"extraskeletal myxoid chondrosarcoma"','chondrosarcoma AND (microRNA OR miRNA OR "small RNA")','Chandhanayingyong','Phimolsarnti','Asavamongkolkul','(Hickernell OR Remotti OR Vundavalli) AND (sarcoma OR microRNA)']):
    jobs.append((f'biostudies-search-{i+1}.json','https://www.ebi.ac.uk/biostudies/api/v1/search?'+urllib.parse.urlencode({'query':q,'pageSize':100}),{'repository':'BioStudies including ArrayExpress','query':q}))
receipts=[]
for name,url,extra in jobs:
    time.sleep(.38);free=shutil.disk_usage(D).free;assert free>=10*1024**3+5242880
    r={'file':name,'url':url,**extra,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_bytes':free}
    try:
        with urllib.request.urlopen(url,timeout=35)as f:b=f.read(900001);assert len(b)<=900000;r.update(status=f.status,content_type=f.headers.get('Content-Type'))
        (D/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest());obj=json.loads(b)
        if 'repository'in extra:r['summary']={k:v for k,v in obj.items()if k in ['totalHits','hits','total','page','pageSize']}
    except Exception as e:r['error']=str(e)
    receipts.append(r);print(json.dumps({'file':name,'bytes':r.get('bytes'),'error':r.get('error'),'totalHits':r.get('summary',{}).get('totalHits')}))
    (D/'metadata-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
