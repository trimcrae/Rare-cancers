from fetch_sources import BASE, fetch
import urllib.request, json, gzip, hashlib, io, xml.etree.ElementTree as E, zipfile, datetime, shutil, re
rs=[]
url='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE124nnn/GSE124158/matrix/GSE124158_series_matrix.txt.gz'
r={'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'metadata prefix only; expression table never read or used'}
try:
 assert shutil.disk_usage(BASE).free-2*1024**2>=10*1024**3
 with urllib.request.urlopen(url,timeout=45) as response:
  g=gzip.GzipFile(fileobj=response); lines=[]; total=0
  for line in g:
   if line.startswith(b'!series_matrix_table_begin'):break
   total+=len(line)
   if total>1800000:raise RuntimeError('metadata prefix exceeded 1.8MB bound')
   lines.append(line)
  data=b''.join(lines)
 (BASE/'GSE124158-metadata-prefix.txt').write_bytes(data)
 r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),hash_scope='retained decompressed metadata only, not full compressed object')
except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
rs.append(r)
rs.append(fetch('axists2023-supp.pdf','https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41416-023-02416-6/MediaObjects/41416_2023_2416_MOESM1_ESM.pdf',450000))
(BASE/'close-eligibility-receipts.json').write_text(json.dumps(rs,indent=2),encoding='utf8')
from pypdf import PdfReader
if (BASE/'axists2023-supp.pdf').exists():
 text='\n'.join(p.extract_text() for p in PdfReader(BASE/'axists2023-supp.pdf').pages)
 (BASE/'axists2023-supp.txt').write_text(text,encoding='utf8')
 print('AXI supplement',len(text),[s for s in text.splitlines() if any(q in s.lower() for q in ['myxoid','chondro','actg1','biomarker','crp'])])
f=BASE/'GSE124158-metadata-prefix.txt'
if f.exists():
 rows={}
 for line in f.read_text().splitlines():
  vals=line.split('\t'); key=vals[0]
  if key.startswith('!Sample'):rows.setdefault(key,[]).append([v.strip('"') for v in vals[1:]])
 samples=rows.get('!Sample_geo_accession',[[]])[0]; hits=[]
 for i,s in enumerate(samples):
  record={k:[v[i] for v in vs if len(v)>i] for k,vs in rows.items()}
  txt=json.dumps(record)
  if any(q in txt.lower() for q in ['extra','chondro','nr4a3','myxoid']):hits.append({'sample':s,'metadata':record})
 out={'total_samples':len(samples),'hits':hits,'keys':list(rows)}
 (BASE/'asano-eligibility.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print('ASANO samples',len(samples),'hits',len(hits))
 print(json.dumps([{ 'sample':h['sample'],'title':h['metadata'].get('!Sample_title'),'characteristics':h['metadata'].get('!Sample_characteristics_ch1')} for h in hits],indent=2)[:6500])
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(BASE/'joch2025-Supplementary_material-Suppl.1-s1.docx') as z:
 root=E.fromstring(z.read('word/document.xml'));out=[]
 for row in root.findall('.//w:tr',ns):
  if any(q in ''.join(row.itertext()) for q in ['NR4A3','NFAT','myxoid']):
   out.append({'row':' '.join(row.itertext()),'underlined_runs':[''.join(run.itertext()) for run in row.findall('.//w:r',ns) if run.find('w:rPr/w:u',ns) is not None]})
 (BASE/'joch-underlined-eligibility.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('JOCH',json.dumps(out,indent=2))
print(json.dumps(rs,indent=2))
