from pathlib import Path
from html.parser import HTMLParser
import json,re
BASE=Path(__file__).resolve().parent
class Body(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.active=False;self.current=[]
 def handle_starttag(self,tag,attrs):
  if tag=='p':self.active=True;self.current=[]
 def handle_endtag(self,tag):
  if tag=='p' and self.active:self.parts.append(' '.join(''.join(self.current).split()));self.active=False
 def handle_data(self,data):
  if self.active:self.current.append(data)
for key in ['oliveira2000-full','drilon2008-html','ogura2012-full','paioli2021-full','mri2025-full','kandoussi2025-full']:
 parser=Body();parser.feed((BASE/(key+'.xml')).read_text(encoding='utf8'))
 (BASE/(key+'-paragraphs.json')).write_text(json.dumps(parser.parts,indent=2))
 print(key)
 for p in parser.parts:
  if key=='kandoussi2025-full' and re.search('follow.up|surviv|retriev|recurr|metasta|selected|database|availab',p,re.I) and len(p)<3500:print(p)
j=json.loads((BASE/'all2014-metadata.json').read_text())
