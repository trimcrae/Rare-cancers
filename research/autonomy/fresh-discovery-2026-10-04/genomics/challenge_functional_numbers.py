"""Independent XML-level extraction, not the worker openpyxl implementation."""
from pathlib import Path
import zipfile,io,xml.etree.ElementTree as E,json,math,hashlib,re
D=Path(__file__).resolve().parent
F=D.parent/'functional'
if not F.exists(): F=Path(r'C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04/functional')
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
source=F/'planaspaz2023-publisher-fig5.zip';saved=F/'ddr-results.json'
out=json.loads(saved.read_text());z=zipfile.ZipFile(source)
checked=[]
def ci(ref):
 r=0
 for c in re.match('[A-Z]+',ref).group():r=26*r+ord(c)-64
 return r
for curve in out['EMC_curves']:
 b=z.read(curve['source_member']);w=zipfile.ZipFile(io.BytesIO(b));ss=[]
 if 'xl/sharedStrings.xml' in w.namelist():ss=[''.join(x.itertext()) for x in E.fromstring(w.read('xl/sharedStrings.xml')).findall('s:si',N)]
 cells={}
 for c in E.fromstring(w.read('xl/worksheets/sheet1.xml')).findall('.//s:c',N):
  v=c.find('s:v',N);raw=v.text if v is not None else None
  if c.get('t')=='s':val=ss[int(raw)]
  elif c.get('t')=='inlineStr':val=''.join(c.find('s:is',N).itertext())
  elif raw is not None:val=float(raw)
  else:val=None
  cells[c.get('r')]=val
 header=[(ci(k),v) for k,v in cells.items() if re.search(r'\D1$',k)]
 cols=[col for col,v in header if v=='USZ-22_EMC2'];assert len(cols)==1
 col=cols[0]
 for p in curve['points']:
  row=p['excel_row'];vs=[v for k,v in cells.items() if int(re.search(r'\d+',k).group())==row and col<=ci(k)<col+3 and isinstance(v,float)]
  assert len(vs)==len(p['reported_replicate_values'])==3
  a=cells.get('A'+str(row));assert a==p['log10_dose_uM']
  avg=math.fsum(vs)/3;err=abs(avg-p['mean']);assert err<1e-10
  if a is not None:assert abs(10**a-p['dose_uM'])<1e-10
  checked.append({'drug':curve['drug'],'row':row,'mean':avg,'difference':err,'dose_labelled':a is not None})
r={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reviewed_output_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'implementation':'stdlib XLSX XML extraction independent of openpyxl worker parser','emc_curves':len(out['EMC_curves']),'checked_points':len(checked),'checked_replicate_cells':3*len(checked),'max_mean_difference':max(x['difference'] for x in checked),'unlabelled_source_rows':sum(not x['dose_labelled'] for x in checked),'points':checked,'conclusion':'Numeric extraction passes for these6 EMC curves. Not approval of drug-class generalization, donor replication or novelty.'}
(D/'functional-numeric-challenge.json').write_text(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in r.items() if k!='points'},indent=2))

