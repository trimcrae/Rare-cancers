"""Complete bounded metadata follow-up; no gene/miRNA numerical matrices."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,time,xml.etree.ElementTree as E,shutil
D=Path(__file__).resolve().parent;jobs=[]
for db in ['gds','sra']:
    obj=json.loads((D/(db+'-author-alias-search.json')).read_text())['esearchresult'];ids=obj['idlist'];assert int(obj['count'])==len(ids)
    for a in range(0,len(ids),75):jobs.append((f'{db}-author-summaries-{a//75}.json','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode({'db':db,'id':','.join(ids[a:a+75]),'retmode':'json','version':'2.0'})))
ids=[]
for p in D.glob('sra-summaries-*.json'):
    o=json.loads(p.read_text())['result']
    for u in o['uids']:
        if 'SRP223204'in o[u]['expxml']:ids.append(u)
assert len(ids)==8
jobs.append(('SRP223204-all8-experiments.xml','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'sra','id':','.join(ids),'retmode':'xml'})))
jobs.append(('E-MTAB-7265.sdrf.txt','https://www.ebi.ac.uk/biostudies/files/E-MTAB-7265/E-MTAB-7265.sdrf.txt'))
receipts=[]
for name,url in jobs:
    time.sleep(.4);assert shutil.disk_usage(D).free>=10*1024**3+5242880
    r={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(url,timeout=35)as f:b=f.read(850001);assert len(b)<=850000;r.update(status=f.status,final_url=f.url)
        (D/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:r['error']=str(e)
    receipts.append(r);print(json.dumps({'file':name,'bytes':r.get('bytes'),'error':r.get('error')}))
    (D/'final-candidate-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
