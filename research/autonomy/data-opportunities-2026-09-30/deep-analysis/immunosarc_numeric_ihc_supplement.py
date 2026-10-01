import csv,hashlib,io,json,math,re,zipfile,xml.etree.ElementTree as E
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
O=Path('campaign-output/immunosarc-numeric-ihc');O.mkdir(parents=True,exist_ok=True);R=dict(schema='immunosarc-numeric-IHC-published-supplement/1',sources=[],errors=[],members=[],candidates=[],limits=['Exact declared S01 TableS1 followthrough only','Numeric positive-cell percentages and published quartiles are distinct measurements','No first-candidate selection, averaging collisions or zero substitution','Source-sample linkage does not imply all84enrolledpatients are covered','No efficacy or independent biomarker-prognosis inference'])
def get(u):
 with urlopen(Request(u,headers={'User-Agent':'Rare-cancers-published-numeric-IHC-audit'}),timeout=60) as x:b=x.read(512*1024*1024+1)
 if len(b)>512*1024*1024:raise ValueError('512MiB response cap')
 R['sources'].append(dict(url=u,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));return b
def norm(x):return re.sub('[^a-z0-9]','',str(x).casefold())
def num(x):
 try:v=float(str(x).strip());return v if math.isfinite(v) else None
 except (ValueError,TypeError):return None
def xlrows(b):
 z=zipfile.ZipFile(io.BytesIO(b));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};s=[]
 if 'xl/sharedStrings.xml' in z.namelist():s=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
 for name in z.namelist():
  if not re.fullmatch('xl/worksheets/sheet[0-9]+[.]xml',name):continue
  rows=[]
  for _,row in E.iterparse(z.open(name),events=('end',)):
   if row.tag.rsplit('}',1)[-1]!='row':continue
   vals=[]
   for cell in row:
    if cell.tag.rsplit('}',1)[-1]!='c':continue
    ref=cell.get('r','A1');letters=re.match('[A-Z]+',ref).group();idx=0
    for c in letters:idx=idx*26+ord(c)-64
    while len(vals)<idx:vals.append('')
    v=cell.find('m:v',ns);t=cell.get('t');text=v.text if v is not None and v.text is not None else ''
    if t=='s':text=s[int(text)] if text else ''
    elif t=='inlineStr':node=cell.find('m:is',ns);text=''.join(node.itertext()) if node is not None else ''
    vals[idx-1]=text
   rows.append(vals);row.clear()
  yield name,rows
FIELD={'patientid':'PatientID','sampletimepoint':'Timepoint','cd8positivecells':'CD8','pd1positivecells':'PD1'}
def candidate(source,rows):
 for i,row in enumerate(rows[:100]):
  hit={FIELD[norm(v)]:j for j,v in enumerate(row) if norm(v) in FIELD}
  if 'PatientID' not in hit or 'Timepoint' not in hit or not({'CD8','PD1'}&set(hit)):continue
  records=[]
  for j,r in enumerate(rows[i+1:],i+2):
   v={k:r[c] if c<len(r) else '' for k,c in hit.items()}
   if not str(v.get('PatientID','')).strip():continue
   records.append(dict(v,sourceRow=j,literalRow=r))
  R['candidates'].append(dict(source=source,headerRow=i+1,literalHeader=row,records=records));break
try:
 md=json.loads(get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+quote('DOI:10.1038/s41467-022-30874-8')+'&format=json&resultType=core'))['resultList']['result'];assert len(md)==1 and md[0].get('pmcid');pmc=md[0]['pmcid'];R['primaryMetadata']=md[0]
 try:
  b=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML');(O/'primary.xml').write_bytes(b);root=E.fromstring(b)
  for tab in root.findall('.//table-wrap'):
   rows=[[' '.join(' '.join(c.itertext()).split()) for c in tr if c.tag.rsplit('}',1)[-1] in ('td','th')] for tr in tab.findall('.//tr')];candidate('primaryXML:'+str(tab.get('id')),rows)
 except Exception as e:R['primaryXMLerror']=dict(type=type(e).__name__,message=str(e))
 b=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/supplementaryFiles');(O/'supplement.zip').write_bytes(b);z=zipfile.ZipFile(io.BytesIO(b))
 for name in z.namelist():
  if name.endswith('/'):continue
  b=z.read(name);rec=dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest());R['members'].append(rec)
  if name.lower().endswith('.xlsx'):
   rec['sheets']=[]
   for sh,rows in xlrows(b):rec['sheets'].append(dict(sheet=sh,rows=len(rows),first12Rows=rows[:12]));candidate(name+':'+sh,rows)
  elif name.lower().endswith(('.txt','.tsv','.csv')):
   text=b.decode('utf-8-sig','replace');rows=list(csv.reader(io.StringIO(text),delimiter=',' if name.lower().endswith('.csv') else '\t'));rec['first12Rows']=rows[:12];candidate(name,rows)
  elif name.lower().endswith('.xls'):
   import xlrd
   w=xlrd.open_workbook(file_contents=b);rec['sheets']=[]
   for sh in w.sheets():rows=[sh.row_values(i) for i in range(sh.nrows)];rec['sheets'].append(dict(sheet=sh.name,rows=len(rows),first12Rows=rows[:12]));candidate(name+':'+sh.name,rows)
  elif name.lower().endswith('.docx'):
   dz=zipfile.ZipFile(io.BytesIO(b));dr=E.fromstring(dz.read('word/document.xml'));wn={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};rec['wordTables']=[]
   for i,tab in enumerate(dr.findall('.//w:tbl',wn)):
    rows=[[' '.join(' '.join(cell.itertext()).split()) for cell in row.findall('w:tc',wn)] for row in tab.findall('w:tr',wn)];rec['wordTables'].append(dict(index=i,rows=len(rows),first12Rows=rows[:12]));candidate(name+':wordtable'+str(i),rows)
  elif name.lower().endswith('.pdf'):
   from pypdf import PdfReader
   text='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(b)).pages);rec['PDFtextCharacters']=len(text);rec['IHCmatchedText']=[line for line in text.splitlines() if re.search(r'Table.?S1|Patient.?ID|Timepoint|CD8|PD.?1|Positive Cells',line,re.I)];(O/(Path(name).name+'.txt')).write_text(text)
 u='https://raw.githubusercontent.com/mskcc/ImmunoSarc/b71c3373bc182f9c647a6f7bc1fbd641d24db917/Figures/data/SampleSourceData.txt';b=get(u);assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='c3d9ee850299eb8930788468c87754b58d5a67f8';ss=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'));assert len(ss)==133;sm={str(x['SampleID']):x for x in ss};assert len(sm)==133
 cells=defaultdict(list);R['unmatchedPublishedRows']=[]
 for c in R['candidates']:
  for x in c['records']:
   key=str(x['PatientID']).strip()+';'+str(x['Timepoint']).strip();source=dict(attachment=c['source'],sourceRow=x['sourceRow'],literalRow=x['literalRow'])
   if key not in sm:R['unmatchedPublishedRows'].append(dict(sampleKey=key,**source));continue
   for f in ('CD8','PD1'):
    if f in x:cells[(key,f)].append(dict(valueLiteral=x[f],numericValue=num(x[f]),**source))
 R['numericCells']=[];available={f:{t:set() for t in ('Baseline','On-Treatment','Progression')} for f in ('CD8','PD1')};pairs={}
 for (key,f),v in sorted(cells.items()):
  values=sorted({x['numericValue'] for x in v if x['numericValue'] is not None});status='one-distinct-numeric-value' if len(values)==1 else 'no-numeric-value' if not values else 'conflicting-numeric-values';x=sm[key];item=dict(sampleKey=key,subject=x['Subject'],timepoint=x['SampleTimepoint'],cohort=x['Cohort'],field=f,sourceValues=v,status=status,distinctNumericValues=values,quartileLiteral=x[{'CD8':'CD8.IHCquart','PD1':'PD-1.IHCquart'}[f]]);R['numericCells'].append(item)
  if len(values)==1:available[f].setdefault(x['SampleTimepoint'],set()).add(x['Subject']);pairs[(x['Subject'],f,x['SampleTimepoint'])]=values[0]
 R['availability']=[];R['pairedChanges']=[]
 for f in ('CD8','PD1'):
  base=available[f]['Baseline'];on=available[f]['On-Treatment'];paired=base&on;R['availability'].append(dict(field=f,baseline=len(base),on=len(on),paired=len(paired),progression=len(available[f]['Progression']),pairedSubjects=sorted(paired,key=int)))
  for k in sorted(paired,key=int):a=pairs[(k,f,'Baseline')];b=pairs[(k,f,'On-Treatment')];R['pairedChanges'].append(dict(subject=k,field=f,baselinePercent=a,onPercent=b,changePercentagePoints=b-a))
 R['cellStatusCounts']=dict(Counter(x['status'] for x in R['numericCells']));R['numericQuartileAvailabilityDiscrepancies']=[x for x in R['numericCells'] if (x['status']=='one-distinct-numeric-value')!=(num(x['quartileLiteral']) is not None)];R['conclusion']='ExactnumericTableS1acquired-and-linked' if R['candidates'] else 'NoexactTableS1headersinparsedattachments;preservedPDF/DOCXandprimarydeclarationsrequireboundedlayoutfollowthrough'
except Exception as e:R['errors'].append(dict(type=type(e).__name__,message=str(e)))
(O/'immunosarc-numeric-ihc-supplement.json').write_text(json.dumps(R,indent=2)+'\n');print(json.dumps(R,separators=(',',':')))
if R['errors']:raise SystemExit(1)
