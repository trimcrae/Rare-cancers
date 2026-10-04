import pathlib,json,hashlib,datetime,xml.etree.ElementTree as E
from pypdf import PdfReader
D=pathlib.Path(__file__).resolve().parent
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pdfs':{},'xmls':{}}
for name in ['pabst2025.pdf','novruzov2026-supp.pdf']:
 p=D/name;r=PdfReader(p);pages=[x.extract_text() or '' for x in r.pages];links=[]
 for i,page in enumerate(r.pages):
  for a in page.get('/Annots',[]):
   z=a.get_object(); act=z.get('/A',{});u=act.get('/URI')
   if u:links.append({'page':i+1,'url':str(u)})
 out['pdfs'][name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':pages,'links':links}
for name in ['koerber2021.xml','novruzov2026.xml','ferdinandus2022.xml']:
 p=D/name;r=E.parse(p).getroot();tables=[]
 for t in r.findall('.//table-wrap'):
  tables.append({'id':t.get('id'),'text':' '.join(t.itertext()),'rows':[[' '.join(c.itertext()) for c in row] for row in t.findall('.//tr')]})
 supp=[E.tostring(x,encoding='unicode') for x in r.findall('.//supplementary-material')]
 meta={x.get('pub-id-type'):x.text for x in r.findall('.//article-id')}
 out['xmls'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metadata':meta,'tables':tables,'supplements':supp}
(D/'source-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for n,v in out['pdfs'].items():
 print(n,'pages',len(v['pages']),'links',v['links'])
 if 'supp' in n: print('\n'.join(v['pages']))
 else:
  for i,t in enumerate(v['pages']):
   if any(q in t.lower() for q in ['data sharing','appendix','histology']):print('PAGE',i+1,t[-1600:])
v=out['xmls']['ferdinandus2022.xml'];print('FERDINANDUS',v['metadata'],v['supplements'])
for t in v['tables']:print(t['id'],t['text'][:11000])
