from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,re
from openpyxl import load_workbook
D=Path(__file__).resolve().parent
class Text(HTMLParser):
    def __init__(self):super().__init__();self.out=[];self.skip=0
    def handle_starttag(self,t,a):
        if t in ['script','style']:self.skip+=1
        if t in ['p','tr','h1','h2','h3','h4']:self.out.append('\n')
        if t in ['td','th']:self.out.append('\t')
    def handle_endtag(self,t):
        if t in ['script','style']:self.skip=max(0,self.skip-1)
        if t in ['p','tr','h1','h2','h3','h4']:self.out.append('\n')
    def handle_data(self,s):
        if not self.skip:self.out.append(s)
out={}
for name in ['alt2015.html','telomeric-content2023.html','methylation2021.html']:
    p=Text();p.feed((D/name).read_text(encoding='utf8'));s=''.join(p.out)
    (D/name.replace('.html','-text.txt')).write_text(s,encoding='utf8')
    out[name]={'EMC_context':[line for line in s.splitlines() if re.search('extraskeletal|EMCS|EMC',line,re.I)],
               'data_context':[line for line in s.splitlines() if re.search('data availability|transfer agreement|data transfer|Supplementary Data',line,re.I)]}
for name in ['41467_2020_20603_MOESM4_ESM.xlsx','41467_2020_20603_MOESM6_ESM.xlsx','tert2014-supplement.xlsx']:
    w=load_workbook(D/name,read_only=True,data_only=True)
    allhits=[]
    for sh in w:
        rows=list(sh.values)
        for i,row in enumerate(rows):
            if any('extraskeletal myxoid chondrosarcoma' in str(c).lower() or str(c).strip()=='EMCS' for c in row):
                allhits.append({'sheet':sh.title,'row':i+1,'values':row})
    out[name]={'EMC_rows':allhits}
    if name=='tert2014-supplement.xlsx':
        out[name]['legend_rows']=[r for r in allhits if not isinstance(r['values'][0],(int,float))]
        out[name]['EMC_rows']=[r for r in allhits if isinstance(r['values'][0],(int,float))]
        assert len(out[name]['EMC_rows'])==8
assert len(out['41467_2020_20603_MOESM4_ESM.xlsx']['EMC_rows'])==10
assert len(out['41467_2020_20603_MOESM6_ESM.xlsx']['EMC_rows'])==1
receipts=json.loads((D/'receipts.json').read_text())
for r in receipts:
    if 'sha256' in r:assert hashlib.sha256((D/r['name']).read_bytes()).hexdigest()==r['sha256']
out['verification']={'hash_receipts_pass':len([r for r in receipts if 'sha256' in r]),'status':'PASS'}
(D/'feasibility-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,default=str),encoding='utf8')
print(json.dumps({'methylation_reference_EMC':10,'validation_EMC_label':1,'TERT_EMC_rows':len(out['tert2014-supplement.xlsx']['EMC_rows']),'status':'PASS'}))
