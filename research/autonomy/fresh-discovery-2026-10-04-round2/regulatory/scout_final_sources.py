"""Bounded primary source retrieval; no biological value selection."""
import urllib.request, json, hashlib, pathlib, xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent
sources={
 'h19-2026.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12790950/fullTextXML',
 'tang2024.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10869728/fullTextXML',
 'sarquarium2024.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10883282/fullTextXML',
 'procan2021-poster.pdf':'https://www.sarcoma.org.au/web/public/media/Elizabeth%20Connolly%20-%20ANZSA21%20poster%282%29.pdf',
 'pride-pan-atlas.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD054790',
}
receipts=[]
for name,url in sources.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-research/1.0'})
  with urllib.request.urlopen(req,timeout=35) as r:
   raw=r.read(5_000_001); typ=r.headers.get('Content-Type'); final=r.url
  if len(raw)>5_000_000: raise ValueError('5 MB scoped limit')
  (P/name).write_bytes(raw)
  receipts.append(dict(file=name,url=url,final_url=final,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),content_type=typ))
  if name.endswith('.xml'):
   root=ET.fromstring(raw)
   snippets=[]
   for e in root.iter():
    if e.tag in ['p','table-wrap','supplementary-material','data-title','title']:
     txt=' '.join(' '.join(e.itertext()).split())
     if any(x in txt.lower() for x in ['extraskeletal','myxoid chondro','emc','mug-emcs','supplementary','data availability','cell line']):
      snippets.append({'tag':e.tag,'id':e.get('id'),'text':txt,'links':[a.attrib for a in e.iter() if a.tag in ['ext-link','media']]})
   (P/name.replace('.xml','-scout.json')).write_text(json.dumps(snippets,indent=2),encoding='utf8')
  print(name,len(raw))
 except Exception as e:
  receipts.append(dict(file=name,url=url,error=str(e)));print(name,str(e))
(P/'final-source-retrievals.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
