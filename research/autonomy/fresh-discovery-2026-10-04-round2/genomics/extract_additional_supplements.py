from pathlib import Path
import zipfile,xml.etree.ElementTree as E,re,json,hashlib
D=Path(__file__).resolve().parent;N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
G={'TSC2','TSC1','IDH2','ARID1A','NTRK3','PTEN','AKT1','PIK3CA','MTOR','RICTOR','RPTOR','FGFR1','KDM5C','KMT2C','CD36'}
out=[]
for p in sorted(list(D.glob('zou-table*.xlsx'))+list(D.glob('heterogeneity-table*.xlsx'))):
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
    if val:vals[c.get('r')]=val
   if vals:rows.append({'row':row.get('r'),'cells':vals})
  matches=[r for r in rows if any(set(re.split(r'[;,| ]+',str(v)))&G for v in r['cells'].values())]
  rec={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sheet':sh.get('name'),'all_rows':rows,'candidate_rows':matches}
  out.append(rec)
  print(p.name,sh.get('name'),len(rows),'header',rows[:2],'candidate_rows',matches[:10])
(D/'other-published-genomics-tables.json').write_text(json.dumps(out,indent=2)+'\n')
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for name in ['genie-agnostic-supplement.docx','heterogeneity-table1.docx']:
 z=zipfile.ZipFile(D/name);r=E.fromstring(z.read('word/document.xml'));txt='\n'.join(''.join(x.itertext()) for x in r.findall('.//w:p',W));(D/(name+'.txt')).write_text(txt);print(name,txt[:10000])
