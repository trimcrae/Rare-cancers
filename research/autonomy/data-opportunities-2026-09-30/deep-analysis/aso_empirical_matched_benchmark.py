import csv,hashlib,importlib.util,io,json,pathlib,re,sys,urllib.request,zipfile
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from scipy.stats import spearmanr
IN=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'research/autonomy/data-opportunities-2026-09-30/deep-analysis/outputs/primary-supplements-staged.json');OUT=pathlib.Path('campaign-output/aso-empirical-matched-benchmark.json');OUT.parent.mkdir(parents=True,exist_ok=True)
source={x['id']:x for x in json.loads(IN.read_text())['sources']};receipts=[];errors=[]
def get(url,limit=96*1024*1024,expected=None):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-ASO-empirical-benchmark'}),timeout=180) as r:raw=r.read(limit+1)
 if len(raw)>limit:raise ValueError('unexpected source size '+url)
 sha=hashlib.sha256(raw).hexdigest()
 if expected and sha!=expected:raise ValueError('frozen SHA256 mismatch '+url)
 receipts.append({'url':url,'bytes':len(raw),'sha256':sha});return raw
raw=get('https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/research/modalities/junction_aso_thermo.py',1024*1024);blob=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
if blob!='500462327ee69b5835ba4d1f798715e71c4765d5':raise ValueError('frozen model mismatch')
receipts[-1]['gitBlob']=blob;path=OUT.parent/'pinned-junction-aso-thermo.py';path.write_bytes(raw);spec=importlib.util.spec_from_file_location('pinned_aso_thermo',path);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model);table,tablemeta=model._nn_table()
if table is None:raise ValueError('Biopython R_DNA_NN1 required; no fallback')
def score(rows):
 reference=rows[0]['RNA5to3'].replace('U','T')
 for r in rows:
  seq=r['RNA5to3'].replace('U','T');runs=[];start=0;mm=[]
  if len(seq)!=len(reference):raise ValueError('RNA length mismatch')
  for i in range(len(seq)+1):
   if i==len(seq) or seq[i]!=reference[i]:
    if i>start:runs.append((seq[start:i],start+1))
    if i<len(seq):mm.append(i+1)
    start=i+1
  run,position=sorted(runs,key=lambda x:(-len(x[0]),x[1]))[0];dh,ds=model.duplex_enthalpy_entropy(run,table);r.update({'mismatchPositionsRNA5to3':mm,'longestPairedRun':len(run),'runRNA5to3':run,'runStartRNA5to3':position,'unmodifiedRunDG37KcalMol':model.delta_g37(dh,ds),'ownTm250nMC':model._tm(dh,ds,conc_nm=250)})
  if r.get('nominalConcentrationNM'):r['ownTmAtPrimaryNominalConcentrationC']=model._tm(dh,ds,conc_nm=r['nominalConcentrationNM'])
 for r in rows:
  r['measuredRelativeTmLossC']=rows[0]['measuredTmC']-r['measuredTmC'];r['modelRelativeTmLoss250nMC']=rows[0]['ownTm250nMC']-r['ownTm250nMC']
  if 'ownTmAtPrimaryNominalConcentrationC' in r:r['modelRelativeTmLossAtPrimaryNominalConcentrationC']=rows[0]['ownTmAtPrimaryNominalConcentrationC']-r['ownTmAtPrimaryNominalConcentrationC']
 return rows
kam=source['ASO_KAMOLA'];sup=next(x for x in kam['parsedSupplementTables'] if 'text' in x);text=sup['text'].split('Supplementary Figure 4')[0];rows=[{'gene':g,'RNA5to3':rna,'measuredTmC':float(tm)} for g,rna,tm in re.findall(r'\b([A-Z][A-Z0-9]+)\s+([ACGU]{16})\s+(\d+\.\d+)',text)]
if len(rows)!=10 or rows[0]['gene']!='BACH1':raise ValueError('expected10 primary S5 duplexes')
if rows[0]['RNA5to3'].replace('U','T')!='TCAGTTTAGCAGTGTA'.translate(str.maketrans('ACGT','TGCA'))[::-1]:raise ValueError('Kamola orientation mismatch')
t4=next(x for x in kam['tables'] if x['id']=='tbl4')
for r in rows:
 q=next(x for x in t4['rows'][1:] if x[0]==r['gene']);m=re.fullmatch(r'(\d+)%',q[2]);r.update({'measuredMaxKnockdownPercent':int(m[1]) if m else None,'measuredEC50MicromolarReported':q[3]})
rows=score(rows);off=rows[1:];kamola={'primarySource':kam['primarySource'],'supplementSource':{'file':sup['file'],'sha256':sup['sha256']},'ASO':'GSK2910546A16mer,5LNAfullyPS','nOffTargetDuplexes':9,'rows':rows,'descriptiveSpearmanNoPValue':{'runTm_vs_measuredTm':float(spearmanr([r['ownTm250nMC'] for r in off],[r['measuredTmC'] for r in off]).statistic),'runTm_vs_maxKnockdown':float(spearmanr([r['ownTm250nMC'] for r in off],[r['measuredMaxKnockdownPercent'] for r in off]).statistic)}};markup=None
try:
 raw=get(kam['primarySource']['url'],1024*1024,kam['primarySource']['sha256']);xml=ET.fromstring(raw);node=next(x for x in xml.iter('table-wrap') if x.get('id')=='tbl1');markup=ET.tostring(node,encoding='unicode')
except Exception as e:errors.append({'step':'Kamola chemistry markup','error':repr(e)})
ths=source['ASO_TOEHOLD'];t2=next(x for x in ths['tables'] if x['id']=='Tab2');rr=[]
for gene in ['ApoB','Copg','Mast2','Hltf']:
 row=next(x for x in t2['rows'] if x[0]==gene);rna=''.join(x[1] for x in row if re.fullmatch(r'r[ACGU]',x));tm=re.fullmatch(r'([\d.]+)\s*±\s*([\d.]+)',row[-1])
 if len(rna)!=13 or not tm:raise ValueError('Toehold Table2 parse '+gene)
 rr.append({'gene':gene,'printedRNA3to5':rna,'RNA5to3':rna[::-1],'measuredTmC':float(tm[1]),'measuredTmSDC':float(tm[2]),'nominalConcentrationNM':4000})
if rr[0]['RNA5to3'].replace('U','T')!='AATGGCCAGCTTG'.translate(str.maketrans('ACGT','TGCA'))[::-1]:raise ValueError('Toehold orientation mismatch')
toehold={'primarySource':ths['primarySource'],'ASO':'hApo1n AAtggccagcTTG,fullyPS2-8-3LNA13mer','nOffTargetDuplexes':3,'rows':score(rr)};workbook=None
try:
 arch=ths['supplementArchive'];raw=get(arch['url'],96*1024*1024);zipfile_path=OUT.parent/'aso-toehold-primary-supplements.zip';zipfile_path.write_bytes(raw)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  observed={i.filename:i.file_size for i in z.infolist() if not i.is_dir()};expected_manifest={i['name']:i['bytes'] for i in ths['archiveMembers'] if not i['name'].endswith('/')};assert observed==expected_manifest,'supplement member manifest changed'
  verified=[]
  for saved in ths['parsedSupplementTables']:
   if saved.get('sha256') and saved['file'].endswith('.xlsx'):
    member=z.read(saved['file']);assert hashlib.sha256(member).hexdigest()==saved['sha256'],saved['file'];verified.append({'file':saved['file'],'sha256':saved['sha256']})
  assert len(verified)==3
  receipts[-1].update(originalArchiveSha256=arch['sha256'],archiveContainerDigestChanged=hashlib.sha256(raw).hexdigest()!=arch['sha256'],originalMemberManifestMatched=True,frozenMemberDigestsVerified=verified)
  hits=[n for n in z.namelist() if n.endswith('41467_2023_43714_MOESM8_ESM.xlsx')]
  if len(hits)!=1:raise ValueError('expected SourceData XLSX')
  info=z.getinfo(hits[0])
  if info.file_size>96*1024*1024:raise ValueError('unexpected workbook size')
  xraw=z.read(hits[0])
 xfile=OUT.parent/'aso-toehold-source-data.xlsx';xfile.write_bytes(xraw);workbook={'archiveSource':arch,'member':hits[0],'bytes':len(xraw),'sha256':hashlib.sha256(xraw).hexdigest(),'savedWorkbook':str(xfile),'sheets':[],'figure6Endpoint':{'state':'raw-values-extracted; match actual headers before endpoint','assay':'Figure6fHuh7,CEM1micromolar24hours,3biologicalreplicates;ssASO,BROC8,BROC9,ApoB/Copg/Mast2/Hltf','noInferenceFromSignificance':True}};ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};S='{'+ns['m']+'}';rel='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id';dest=OUT.parent/'aso-toehold-source-tables';dest.mkdir(exist_ok=True)
 with zipfile.ZipFile(io.BytesIO(xraw)) as xz:
  shared=[]
  if 'xl/sharedStrings.xml' in xz.namelist():
   with xz.open('xl/sharedStrings.xml') as f:
    for _,e in ET.iterparse(f,events=('end',)):
     if e.tag==S+'si':shared.append(''.join(t.text or '' for t in e.iter(S+'t')));e.clear()
  targets={e.get('Id'):e.get('Target') for e in ET.fromstring(xz.read('xl/_rels/workbook.xml.rels'))};sheets=ET.fromstring(xz.read('xl/workbook.xml')).find('m:sheets',ns)
  for index,sh in enumerate(sheets,1):
   name=sh.get('name');target=targets[sh.get(rel)];member=target.lstrip('/') if target.startswith('/') else 'xl/'+target;norm=re.sub(r'[^a-z0-9]','',name.lower());isfig6=norm.startswith('fig6') or norm.startswith('figure6');cfile=dest/('sheet-'+str(index)+'.cells.csv');literal=[];windows=[];previous=[];take=0;nr=0;nc=0
   with cfile.open('w',newline='') as out,xz.open(member) as f:
    writer=csv.writer(out);writer.writerow(['sheet','row','cell','type','value','formula'])
    for _,e in ET.iterparse(f,events=('end',)):
     if e.tag!=S+'row':continue
     vals={};formulas={}
     for cell in e.findall(S+'c'):
      ref=cell.get('r');typ=cell.get('t','n');v=cell.find(S+'v');value=v.text if v is not None else ''
      if typ=='s' and value:value=shared[int(value)]
      if typ=='inlineStr':value=''.join(t.text or '' for t in cell.iter(S+'t'))
      formula=cell.find(S+'f');formula=formula.text if formula is not None else ''
      if value or formula:vals[ref]=value or '';formulas[ref]=formula or '';writer.writerow([name,e.get('r'),ref,typ,value or '',formula or '']);nc+=1
     if vals:
      nr+=1;record={'row':int(e.get('r')),'cells':vals}
      if any(formulas.values()):record['formulas']={k:v for k,v in formulas.items() if v}
      literal.append(record);joined=' '.join(vals.values());hit=bool(re.search(r'fig(?:ure)?[ ._-]*6|ApoB|Copg|Mast2|Hltf',joined,re.I))
      if hit:windows.extend(previous);take=max(take,15)
      if take:windows.append(record);take-=1
      previous=(previous+[record])[-5:]
     e.clear()
   item={'name':name,'member':member,'nNonemptyRows':nr,'nNonemptyCells':nc,'savedAllCellsCSV':str(cfile),'csvSha256':hashlib.sha256(cfile.read_bytes()).hexdigest(),'isFigure6NamedSheet':isfig6}
   if nr<=2500 or isfig6:item['rows']=literal
   else:item.update({'firstRows':literal[:15],'lastRows':literal[-15:]})
   unique={r['row']:r for r in windows};item['figure6OrGeneLabelWindows']=list(unique.values());workbook['sheets'].append(item)
except Exception as e:errors.append({'step':'Toehold full SourceData','error':repr(e)})
doc={'schema':'aso-matched-empirical-qualification/1','completedAt':datetime.now(timezone.utc).isoformat(),'receipts':receipts,'ownModelGitBlob':blob,'modelTableMetadata':tablemeta,'kamola':kamola,'kamolaOriginalChemicalMarkup':markup,'toehold':toehold,'sourceDataWorkbook':workbook,'errors':errors,'limits':['12selectedofftargetduplexeswithin2ASOs/2studies, not12independent ASO validations.','LNA/PS chemistry/salt/strands differ; no absoluteTm calibration/RMSE.','Longest-run omits pairing across mismatch and cannot establish a modified-chemistry binding/separation bound.','No fitted model/Pvalues/newwetlab/EMCknockdown/genomewide safety/therapeutic selectivity.','Figure6 rawvalues require exactgene/arm/control/replicate matching before endpoints.']};OUT.write_text(json.dumps(doc,indent=2)+'\n');print('ASO_MATCHED_EMPIRICAL_BEGIN');print(json.dumps(doc,separators=(',',':')));print('ASO_MATCHED_EMPIRICAL_END')
if errors:sys.exit(1)
