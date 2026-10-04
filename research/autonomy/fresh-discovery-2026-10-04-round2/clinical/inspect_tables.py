from pathlib import Path
from html.parser import HTMLParser
import json
BASE=Path(__file__).resolve().parent
class Tables(HTMLParser):
 def __init__(self):
  super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None;self.title='';self.intitle=False
 def handle_starttag(self,tag,attrs):
  if tag=='title':self.intitle=True
  if tag=='table':self.table=[]
  if tag=='tr' and self.table is not None:self.row=[]
  if tag in ['td','th'] and self.row is not None:self.cell=[]
 def handle_endtag(self,tag):
  if tag=='title':self.intitle=False
  if tag in ['td','th'] and self.cell is not None:self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
  if tag=='tr' and self.row is not None:self.table.append(self.row);self.row=None
  if tag=='table' and self.table is not None:self.tables.append(self.table);self.table=None
 def handle_data(self,data):
  if self.intitle:self.title+=data
  if self.cell is not None:self.cell.append(data)
for name in ['drilon2008-html','oliveira2000-table2','ogura2012-table1','ogura2012-table2','paioli2021-table1','paioli2021-table2','mri2025-table1','mri2025-table2','mri2025-table3','kandoussi2025-table1','kandoussi2025-table2']:
 p=BASE/(name+'.xml')
 parser=Tables();parser.feed(p.read_text(encoding='utf8'))
 out={'title':parser.title,'tables':parser.tables}
 (BASE/(name+'-tables.json')).write_text(json.dumps(out,indent=2))
 if name.startswith('kandoussi'):print(name, json.dumps(out))
for name in ['kapoor2014','case-series2022','surgical-outcomes2023']:
 j=json.loads((BASE/(name+'-extracted.json')).read_text())
 # Previously inspected; retained extracted JSON is unchanged.
