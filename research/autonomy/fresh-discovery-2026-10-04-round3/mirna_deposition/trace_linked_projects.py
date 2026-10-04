"""Close two concrete BioProject follow-ups through public metadata."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,time,shutil
D=Path(__file__).resolve().parent;receipts=[]
def fetch(name,url):
    assert shutil.disk_usage(D).free>10*1024**3+5242880;time.sleep(.4)
    r={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(url,timeout=35)as f:b=f.read(800001);assert len(b)<=800000;r.update(status=f.status,content_type=f.headers.get('Content-Type'))
        (D/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest());return_value=b
    except Exception as e:r['error']=str(e);return_value=None
    receipts.append(r);(D/'linked-project-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps({'file':name,'bytes':r.get('bytes'),'error':r.get('error')}));return return_value
for acc in ['PRJNA692081','PRJEB110929']:
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':'sra','term':acc,'retmode':'json','retmax':200})
    b=fetch(acc+'-sra-search.json',url)
    if b:
        r=json.loads(b)['esearchresult'];assert int(r['count'])==len(r['idlist']);print(acc,'SRA_count',r['count'])
        if r['idlist']:fetch(acc+'-sra-experiments.xml','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'sra','id':','.join(r['idlist']),'retmode':'xml'}))
    fetch(acc+'-ena-runs.json','https://www.ebi.ac.uk/ena/portal/api/filereport?'+urllib.parse.urlencode({'accession':acc,'result':'read_run','fields':'study_accession,sample_accession,experiment_accession,run_accession,library_strategy,library_source,sample_title,study_title','format':'json'}))
