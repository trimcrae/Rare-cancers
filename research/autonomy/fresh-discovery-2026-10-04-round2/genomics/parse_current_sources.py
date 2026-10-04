import zipfile,xml.etree.ElementTree as E,json,hashlib,re
from pathlib import Path
from pypdf import PdfReader
D=Path(__file__).resolve().parent;N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheets(p):
 z=zipfile.ZipFile(p);ss=[]
 if 'xl/sharedStrings.xml'in z.namelist():ss=[''.join(x.itertext())for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)]
 rel={x.get('Id'):x.get('Target')for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 out=[]
 for sh in E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',N):
  target=rel[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];target=target.lstrip('/')if target.startswith('/')else'xl/'+target
  rows=[]
  for row in E.fromstring(z.read(target)).findall('.//s:row',N):
   vals={}
   for c in row.findall('s:c',N):
    v=c.find('s:v',N)
    if c.get('t')=='inlineStr':val=''.join(c.find('s:is',N).itertext())
    elif v is None:continue
    elif c.get('t')=='s':val=ss[int(v.text)]
    else:val=v.text
    if val:vals[c.get('r')]=val
   if vals:rows.append({'row':row.get('r'),'cells':vals})
  out.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sheet':sh.get('name'),'rows':rows})
 return out
if __name__=='__main__':
 out=sheets(D/'japan-genomics-table7.xlsx')+sheets(D/'japan-panel-table3.xlsx')
 (D/'japan-tables-extracted.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 for sh in out:
  matches=[x for x in sh['rows'] if any('myxoid chond' in str(v).lower() or v in ['EMC','EMCS','TSC2','IDH2','ARID1A','NTRK3'] for v in x['cells'].values())]
  print(sh['file'],sh['sheet'],'nrows',len(sh['rows']),'headers',sh['rows'][:3],'matches',matches)
 z=zipfile.ZipFile(D/'lisbon-supplement.zip');print('Lisbon zip',z.namelist())
 for name in z.namelist():
  if name.lower().endswith('.docx'):
   import io
   zz=zipfile.ZipFile(io.BytesIO(z.read(name)));r=E.fromstring(zz.read('word/document.xml'));t='\n'.join(''.join(x.itertext())for x in r.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'));(D/'lisbon-supplement-text.txt').write_text(t,encoding='utf-8');print(t[:3000])
 r=E.parse(D/'japan2025.xml').getroot();print('Japan articleIDs',[(x.get('pub-id-type'),x.text)for x in r.findall('.//article-id')])
 for t in r.findall('.//p'):
  s=' '.join(t.itertext())
  if 'extraskeletal'in s.lower():print('JP',s)
 b=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round2/clinical/bostongene-sitc2024.pdf')
 t='\n'.join(x.extract_text()or''for x in PdfReader(b).pages);(D/'bostongene-sitc2024-text.txt').write_text(t,encoding='utf-8');print('Boston',t[:17000]);print('BostonHASH',hashlib.sha256(b.read_bytes()).hexdigest())
