from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,shutil
B=Path(__file__).resolve().parent
def fetch(name,url,limit=2*1024**2):
 assert shutil.disk_usage(B).free-limit>=10*1024**3
 assert sum(p.stat().st_size for p in B.rglob('*') if p.is_file())+limit<=10*1024**2
 r={'url':url,'name':name,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=35) as resp:
   d=resp.read(limit+1)
   if len(d)>limit:raise RuntimeError('download bound exceeded')
   r.update(status=resp.status,final_url=resp.url,bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
  (B/name).write_bytes(d)
 except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
 return r
if __name__ == "__main__":
 rs=[]
 for name,pmid in [('smed2010','20212452'),('subramanian2008','17922033')]:
  u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:'+pmid+'&format=json'
  rs.append(fetch(name+'-metadata.json',u,100000))
  data=json.loads((B/(name+'-metadata.json')).read_text())['resultList']['result'][0]
  print(name,data.get('pmcid'),data.get('title'))
  if data.get('pmcid'):rs.append(fetch(name+'.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+data['pmcid']+'/fullTextXML'))
 for name,url,limit in [('smed2010.pdf','https://www.oncomir.umn.edu/SMED.pdf',2*1024**2),('smed-faq.html','https://www.oncomir.umn.edu/SMED/FAQ.php',100000),('smed-index.html','https://www.oncomir.umn.edu/SMED/',200000),('GSE69524-series.txt','https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE69524&targ=self&form=text&view=brief',150000),('neural2003.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1868116/fullTextXML',250000),('lms2023.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9856933/fullTextXML',300000)]:rs.append(fetch(name,url,limit))
 (B/'gate-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8');print(json.dumps(rs,indent=2))
 from pypdf import PdfReader
 if (B/'smed2010.pdf').exists():
  s='\n'.join(p.extract_text() for p in PdfReader(B/'smed2010.pdf').pages);(B/'smed2010.txt').write_text(s,encoding='utf8'); print('SMED subtype lines',[x for x in s.splitlines() if any(q in x.lower() for q in ['chondro','myxoid','table 1','geo'])])
 if (B/'GSE69524-series.txt').exists():print('\n'.join(x for x in (B/'GSE69524-series.txt').read_text().splitlines() if any(q in x for q in ['SubSeries','Series_relation','Series_title','Series_summary'])))
