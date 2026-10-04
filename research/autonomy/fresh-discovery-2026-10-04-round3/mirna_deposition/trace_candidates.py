"""Bounded candidate cohort metadata and author-alias follow-through."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,time,shutil
D=Path(__file__).resolve().parent;todo=[]
for g in ['GSE28866','GSE87054','GSE59331','GSE70065','GSE48396','GSE49545','GSE220150']:
    todo.append((g+'-metadata.txt','https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?'+urllib.parse.urlencode({'acc':g,'targ':'self','form':'text','view':'full'})))
todo.append(('GSE87054-samples.txt','https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE87054&targ=gsm&form=text&view=full'))
todo.append(('E-MTAB-7265.json','https://www.ebi.ac.uk/biostudies/api/v1/studies/E-MTAB-7265'))
for study in ['SRP223204','ERP111275']:
    # ENA public experiment metadata, no FASTQ/quantification access.
    todo.append((study+'-samples.json','https://www.ebi.ac.uk/ena/portal/api/search?'+urllib.parse.urlencode({'result':'sample','query':f'study_accession="{study}"','fields':'sample_accession,sample_title,sample_alias,sample_description,scientific_name,center_name','format':'json','limit':0})))
for db in ['gds','sra','bioproject']:
    q='("Francis Lee" OR "Francis Y Lee" OR "Li Song" OR Chandhanarat OR Phimolsarnti OR Phimolsarn) AND (chondrosarcoma OR sarcoma OR microRNA OR miRNA)'
    todo.append((db+'-author-alias-search.json','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':db,'term':q,'retmode':'json','retmax':200})))
receipts=[]
for name,url in todo:
    time.sleep(.4);free=shutil.disk_usage(D).free;assert free>10*1024**3+2*1024**2
    r={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_bytes':free}
    try:
        with urllib.request.urlopen(url,timeout=35)as f:b=f.read(500001);assert len(b)<=500000;r.update(status=f.status,content_type=f.headers.get('Content-Type'))
        (D/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:r['error']=str(e)
    receipts.append(r);print(json.dumps({'file':name,'bytes':r.get('bytes'),'error':r.get('error')}))
    (D/'candidate-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
