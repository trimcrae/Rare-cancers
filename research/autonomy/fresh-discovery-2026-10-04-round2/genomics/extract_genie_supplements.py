from pathlib import Path
import zipfile,xml.etree.ElementTree as E,re,json,hashlib
D=Path(__file__).resolve().parent;N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
out=[]
for p in sorted(D.glob('genie-ccr*.xlsx')):
 z=zipfile.ZipFile(p);ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext())for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)]
 rel={x.get('Id'):x.get('Target')for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
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
    vals[c.get('r')]=val
   rows.append({'row':row.get('r'),'cells':vals})
  matches=[r for r in rows if any('extraskeletal myxoid' in str(v).lower()or str(v).upper()=='EMCHS'for v in r['cells'].values())]
  out.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sheet':sh.get('name'),'all_rows':rows,'emc_rows':matches})
(D/'genie-supplement-extraction.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items()if k!='all_rows'}for x in out],indent=2))
