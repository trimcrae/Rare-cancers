"""Bounded official gene/transcript/source retrieval; no browser automation."""
from pathlib import Path
import urllib.request,json,hashlib,datetime,shutil
D=Path(__file__).resolve().parent
sources={
'dlk1-gene.xml':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=8788&retmode=xml',
'dlk1-old-probes.xml':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=W01204,AA701996&rettype=gb&retmode=xml',
'USZ23-RefSeq.quant.sf.gz':'https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM9037nnn/GSM9037837/suppl/GSM9037837_USZ23_EMC3.RefSeq.quant.sf.gz',
'GSE71119-metadata.txt':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE71119&targ=self&form=text&view=full',
'sjogren2003.txt':'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC1868116/unicode',
}
receipts=[]
for name,url in sources.items():
    out=D/name
    if out.exists():continue
    free=shutil.disk_usage(D).free;assert free>=10*1024**3+3*1024**2
    rec={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free_before':free}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMCResearch/1.0'}),timeout=35)as r:
            b=r.read(3*1024**2+1);assert len(b)<=3*1024**2;rec.update(status=r.status,content_type=r.headers.get('Content-Type'))
        out.write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:rec['error']=str(e)
    receipts.append(rec);print(json.dumps(rec))
    (D/'followup-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
