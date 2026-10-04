"""Public deposition metadata queries only; no expression payloads."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,time,shutil
D=Path(__file__).resolve().parent
queries=[
('gds','"extraskeletal myxoid chondrosarcoma"'),
('gds','chondrosarcoma AND (microRNA OR miRNA OR "small RNA")'),
('gds','Chandhanayingyong OR Phimolsarnti OR Asavamongkolkul'),
('gds','(Hickernell OR Remotti OR Vundavalli) AND (sarcoma OR microRNA OR miRNA)'),
('sra','"extraskeletal myxoid chondrosarcoma"'),
('sra','chondrosarcoma AND (microRNA OR miRNA OR "small RNA")'),
('sra','Chandhanayingyong OR Phimolsarnti OR Asavamongkolkul'),
('sra','(Hickernell OR Remotti OR Vundavalli) AND (sarcoma OR microRNA OR miRNA)'),
('bioproject','"extraskeletal myxoid chondrosarcoma"'),
('bioproject','chondrosarcoma AND (microRNA OR miRNA OR "small RNA")'),
('bioproject','Chandhanayingyong OR Phimolsarnti OR Asavamongkolkul'),
('bioproject','(Hickernell OR Remotti OR Vundavalli) AND (sarcoma OR microRNA OR miRNA)'),
]
results=[]
for n,(db,q)in enumerate(queries,1):
    time.sleep(.38);url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':db,'term':q,'retmode':'json','retmax':250})
    free=shutil.disk_usage(D).free;assert free>=10*1024**3+5242880
    r={'number':n,'db':db,'query':q,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_bytes':free}
    try:
        with urllib.request.urlopen(url,timeout=35)as f:b=f.read(500001);assert len(b)<=500000
        (D/f'entrez-search-{n:02d}.json').write_bytes(b);obj=json.loads(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),result=obj.get('esearchresult',obj))
    except Exception as e:r['error']=str(e)
    results.append(r);print(json.dumps({'n':n,'db':db,'count':r.get('result',{}).get('count'),'error':r.get('error')}))
    (D/'entrez-search-receipts.json').write_text(json.dumps(results,indent=2)+'\n')
