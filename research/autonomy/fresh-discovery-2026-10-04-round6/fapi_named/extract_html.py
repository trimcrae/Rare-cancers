#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parent
class Extract(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.stack=[];self.tables=[];self.paragraphs=[];self.current=None;self.t=None;self.r=None;self.cell=None;self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'href' in a: self.links.append(a['href'])
  if tag=='p' and a.get('id','').startswith('p-'): self.current=[a['id'],[]]
  if tag=='table': self.t={'id':a.get('id'),'rows':[]}
  if tag=='tr' and self.t is not None: self.r=[]
  if tag in ['td','th'] and self.r is not None:self.cell=[]
 def handle_data(self,data):
  if self.current:self.current[1].append(data)
  if self.cell is not None:self.cell.append(data)
 def handle_endtag(self,tag):
  if tag=='p' and self.current:
   self.paragraphs.append({'id':self.current[0],'text':re.sub(r'\s+',' ',' '.join(self.current[1])).strip()});self.current=None
  if tag in ['td','th'] and self.cell is not None:
   self.r.append(re.sub(r'\s+',' ',' '.join(self.cell)).strip());self.cell=None
  if tag=='tr' and self.r is not None:self.t['rows'].append(self.r);self.r=None
  if tag=='table' and self.t is not None:self.tables.append(self.t);self.t=None
for source in ['kessler','lanzafame','kratochwil']:
 f=P/'raw-cache'/f'{source}-jnm-full.html';x=Extract();x.feed(f.read_text());d={'source':source,'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'tables':x.tables,'paragraphs':x.paragraphs,'links':sorted(set(x.links))};(P/'raw-cache'/f'{source}-extracted.json').write_text(json.dumps(d,indent=2)+'\n')
 print(source,'clinical paragraphs extracted',len(x.paragraphs))
