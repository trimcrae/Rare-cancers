import pathlib,json,urllib.request,hashlib,datetime,xml.etree.ElementTree as ET
D=pathlib.Path(__file__).parent; S=D.parent/'fusion-partial-benchmark-2026-09-05'; (D/'inputs').mkdir(exist_ok=True)
root=ET.parse(S/'inputs/lee2023.xml').getroot()
for f in root.iter('fig'):
 print(f.attrib,[(e.tag,e.attrib) for e in f.iter() if e.tag.endswith('graphic')])
def get(name,url):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(url,timeout=50) as r: b=r.read(); final=r.url; ct=r.headers.get('Content-Type')
  (D/'inputs'/name).write_bytes(b); rec=dict(file=name,url=url,final_url=final,retrieved_utc=t,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content_type=ct)
 except Exception as e: rec=dict(file=name,url=url,retrieved_utc=t,error=str(e))
 p=D/'retrievals.json'; rows=json.loads(p.read_text()) if p.exists() else [];rows.append(rec);p.write_text(json.dumps(rows,indent=2)); print(rec)
if __name__=='__main__':
 for acc in ['NM_058243.2','NM_001284292.2','NM_058243.3','NM_001284292.1']:
  get(acc+'.gb','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id='+acc+'&rettype=gb&retmode=text')
 get('crt-2022-910f2.jpg','https://www.e-crt.org/upload/thumbnails/crt-2022-910f2.jpg')
