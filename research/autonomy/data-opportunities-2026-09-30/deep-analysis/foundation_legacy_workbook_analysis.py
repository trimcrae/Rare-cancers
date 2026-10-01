#!/usr/bin/env python3
import csv,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
CAP=512*1024*1024;OUT=Path('campaign-output/foundation-original');OUT.mkdir(parents=True,exist_ok=True)
TARGETS=('NR4A3','NR4A2','EWSR1','TAF15','RET','ALK','CDKN2A','MTAP');rx={g:re.compile(r'(?<![A-Z0-9])'+g+r'(?![A-Z0-9])') for g in TARGETS}
R=dict(schema='foundation-legacy-workbook-analysis/1',startedUtc=datetime.now(timezone.utc).isoformat(),sources=[],errors=[],sheets=[],limits=['Gene/CNV literals not pathogenicity, callability or negative prevalence','No ID/ordinal mapping before source headers/values','Nominal EMC labels not confirmed EMC','Primary genomic reclassification not reconfirmed by expert pathology'])
def get(url,data=None,headers=None):
 h={'User-Agent':'Rare-cancers-original-workbook-analysis'};h.update(headers or {})
 with urlopen(Request(url,data=data,headers=h),timeout=90) as r:b=r.read(CAP+1)
 if len(b)>CAP:raise ValueError('source cap')
 return b
def canon(v):return str(int(v)) if isinstance(v,float) and v.is_integer() else str(v)
def load_sheets(raw):
 if raw.lstrip().startswith(b'<?xml') or raw.lstrip().startswith(b'<Workbook'):
  root=ET.fromstring(raw);ns={'s':'urn:schemas-microsoft-com:office:spreadsheet'};a='{'+ns['s']+'}'
  for sh in root.findall('s:Worksheet',ns):
   rows=[]
   for row in sh.findall('s:Table/s:Row',ns):
    vals=[]
    for cell in row.findall('s:Cell',ns):
     while len(vals)<int(cell.get(a+'Index',str(len(vals)+1)))-1:vals.append('')
     d=cell.find('s:Data',ns);vals.append(''.join(d.itertext()) if d is not None else '')
    rows.append(vals)
   yield sh.get(a+'Name'),rows,'SpreadsheetML'
 else:
  import xlrd
  w=xlrd.open_workbook(file_contents=raw)
  for sh in w.sheets():yield sh.name,[sh.row_values(i) for i in range(sh.nrows)],'xlrd'
def lfs(oid,n):
 q=dict(operation='download',transfers=['basic'],objects=[dict(oid=oid,size=n)]);x=json.loads(get('https://nsssw8k94d.execute-api.us-east-1.amazonaws.com/objects/batch',json.dumps(q).encode(),{'Content-Type':'application/vnd.git-lfs+json','Accept':'application/vnd.git-lfs+json'}))['objects'][0]
 if x.get('error'):raise ValueError(x['error'])
 a=x['actions']['download'];b=get(a['href'],headers=a.get('header',{}));assert len(b)==n and hashlib.sha256(b).hexdigest()==oid
 R['sources'].append(dict(source='cBioPortalLFS',bytes=n,sha256=oid));return list(csv.DictReader(io.StringIO('\n'.join(l for l in b.decode('utf-8-sig').splitlines() if l and not l.startswith('#'))),delimiter='\t'))
try:
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9200814/supplementaryFiles';b=get(url);R['priorArchiveSHA256']='28a1e9dc628918927429df358989774bea066a345b9c305c477a0959ac60e204';R['archiveMatchesPrior']=hashlib.sha256(b).hexdigest()==R['priorArchiveSHA256'];R['sources'].append(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));z=zipfile.ZipFile(io.BytesIO(b));raw=z.read('41467_2022_30496_MOESM2_ESM.xls');assert len(raw)==4812800;p=OUT/'41467_2022_30496_MOESM2_ESM.xls';p.write_bytes(raw);R['workbook']=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),first16Hex=raw[:16].hex())
 for name,rows,reader in load_sheets(raw):
  score=lambda r:sum(bool(re.search(r'gene|sample|specimen|histolog|diagnos|variant|alteration|\bage\b|\bsex\b|\btmb\b|\bmsi\b',str(v),re.I)) for v in r)
  hi=max(range(min(20,len(rows))),key=lambda i:score(rows[i])) if rows else 0;headers=[canon(v) for v in rows[hi]] if rows else [];hc=[re.sub(r'[^a-z0-9]','',h.lower()) for h in headers];diagcols=[i for i,h in enumerate(headers) if re.search(r'histolog|diagnos|subtype|sarcoma',h,re.I)];idcols=[i for i,h in enumerate(hc) if h in ('sample','sampleid','specimenid','patientid','fmisampleid','sampleidentifier')];counts={i:Counter() for i in diagcols};hits=[];tc=Counter();cnv=0;chondro=[];nr=[]
  for i,row in enumerate(rows[hi+1:],start=hi+1):
   vals=[canon(v) for v in row];joined=' '.join(vals).upper();genes=[g for g in TARGETS if rx[g].search(joined)];tc.update(genes);iscnv=bool(re.search(r'COPY.?NUMBER|\bCNV\b|\bAMPLIFICATION\b|\bDELETION\b',joined));cnv+=iscnv
   for k in diagcols:counts[k][vals[k] if k<len(vals) else '']+=1
   record=dict(excelRow=i+1,cells=vals,literalTargetGenes=genes,CNVLikeLiteral=iscnv,identifierCandidateValues={headers[k]:vals[k] for k in idcols if k<len(vals)})
   if genes and len(hits)<200:hits.append(record)
   if 'CHONDROSARCOMA' in joined and len(chondro)<500:chondro.append(record)
   if 'NR4A3' in genes and len(nr)<500:nr.append(record)
  R['sheets'].append(dict(sheet=name,reader=reader,physicalRows=len(rows),candidateHeaderExcelRow=hi+1,candidateHeaders=headers,firstTenRawRows=rows[:10],diagnosisColumnCounts=[dict(columnIndex=k,header=headers[k],counts=dict(counts[k])) for k in diagcols],identifierColumnCandidates=[dict(columnIndex=k,header=headers[k]) for k in idcols],targetGeneRowCounts=dict(tc),CNVLikeLiteralRowCount=cnv,targetLiteralRepresentativeRows=hits,chondrosarcomaLiteralRows=chondro,nr4a3LiteralRows=nr))
except Exception as e:R['errors'].append(dict(stage='originalWorkbook',type=type(e).__name__,message=str(e)))
try:
 sv=lfs('d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701',180393);genes=Counter();partners=Counter();nr=[]
 for row in sv:
  a=row.get('Site1_Hugo_Symbol','');b=row.get('Site2_Hugo_Symbol','');genes.update(g for g in (a,b) if g not in ('','N/A','NA'));partners['::'.join(sorted((a,b)))]+=1
  if 'NR4A3' in (a,b) or 'NR4A2' in (a,b):nr.append(row)
 R['allExportedSV']=dict(rows=len(sv),distinctSampleIds=len({r.get('Sample_Id') for r in sv}),columns=list(sv[0]) if sv else [],targetLiteralSiteCounts={g:genes[g] for g in TARGETS},nr4aLiteralRows=nr,topGeneSiteCounts=genes.most_common(30),topUnorientedPartnerCounts=partners.most_common(40),scope='All exported rows; observed entries not callable negative prevalences')
except Exception as e:R['errors'].append(dict(stage='allExportedSV',type=type(e).__name__,message=str(e)))
R['finishedUtc']=datetime.now(timezone.utc).isoformat();Path('campaign-output/foundation-legacy-workbook-analysis.json').write_text(json.dumps(R,indent=2)+'\n');print('EMC_FOUNDATION_LEGACY_RESULT_BEGIN');print(json.dumps(R,separators=(',',':')));print('EMC_FOUNDATION_LEGACY_RESULT_END')
