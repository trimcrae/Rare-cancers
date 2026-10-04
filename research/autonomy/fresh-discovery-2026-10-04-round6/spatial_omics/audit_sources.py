import json,re,xml.etree.ElementTree as E,hashlib,html
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self): super().__init__();self.parts=[]
 def handle_data(self,d): self.parts.append(d)
def clean(s):
 p=Text();p.feed(s);return re.sub(r'\s+',' ',' '.join(p.parts))
out={}
x=E.parse(ROOT/'ngo2025.xml')
out['ngo']={'title':''.join(x.find('.//article-title').itertext()),'doi':[e.text for e in x.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi'],'assay_scope':[]}
for p in x.findall('.//p'):
 t=''.join(p.itertext())
 if any(z in t.lower() for z in ['single-cell','single cell','spatial','1,041','1041','deposited']):out['ngo']['assay_scope'].append(t)
for n in ['cassis-report.html','cassis-results.html','cassis-project.html','3ca-sarcoma.html']:
 s=(ROOT/n).read_text(encoding='utf-8');t=clean(s)
 out[n]={'sha256':hashlib.sha256(s.encode()).hexdigest(),'text':t,'links':re.findall(r'href=["\']([^"\']+)',s)}
(ROOT/'source-audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print('Ngo assay-scope paragraphs',len(out['ngo']['assay_scope']))
for n in ['cassis-results.html','3ca-sarcoma.html']:
 t=out[n]['text'];start=t.find('Publications') if n.startswith('cassis') else t.find('Year')
 print(n,t[start:start+8000])
