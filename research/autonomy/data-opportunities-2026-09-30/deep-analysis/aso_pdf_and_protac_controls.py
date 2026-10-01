#!/usr/bin/env python3
import argparse,collections,csv,datetime,hashlib,io,json,pathlib,re,sys,urllib.request,zipfile,xml.etree.ElementTree as ET
from pypdf import PdfReader
P=pathlib.Path
ap=argparse.ArgumentParser();ap.add_argument('--primary',default='research/autonomy/data-opportunities-2026-09-30/deep-analysis/outputs/primary-supplements-staged.json');ap.add_argument('--output',default='campaign-output/aso-pdf-and-protac-controls.json');a=ap.parse_args();p=P(a.primary)
if not p.exists():
 xs=list(P('.').rglob('primary-supplements-staged.json'));assert len(xs)==1,[str(x) for x in xs];p=xs[0]
b=p.read_bytes();primary=json.loads(b)
while 'result' in primary and isinstance(primary['result'],dict):primary=primary['result']
out={'schema':'aso-primary-pdf-and-negative-protac-controls/2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipts':[{'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}],'ASOSupplements':[],'errors':[]}
def download(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-measurement-audit'}),timeout=120) as f:b=f.read()
 return b,{'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
u='https://raw.githubusercontent.com/agiani99/ProtacPedia_Reshuffling/45937da04eeace8350958cacbbe744a9923812f3/protacdb_20220210.csv';b,r=download(u);assert hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()=='7937953fc851ba85be9a628c0bc765d8f3c4ff65';out['receipts'].append(r);rows=list(csv.DictReader(io.StringIO(b.decode())));assert len(rows)==1203 and all(len(x)==43 for x in rows);labels=collections.Counter(x['Active/Inactive'] for x in rows);assert labels=={'Active':812,'Inactive':391};fields=['Dc50','Dmax','Ligand PDB','Pubmed','Cells','Time'];controls=['Proteomics Data Available','Tested A Non Binding E3 Control','Tested Competition With Ligand','Tested Engagement In Cells','Tested Proteaseome Inhibitor']
def numeric(s,kind):
 s=s.strip().replace('μ','u').replace('µ','u');m=re.fullmatch(r'([<>~≈]?\s*)(\d+(?:\.\d+)?|\.\d+)\s*(nM|uM|mM|M|%)?',s,re.I)
 if not m:return None
 unit=(m[3] or '').lower();censored=bool(m[1].strip())
 if kind=='Dc50':
  if unit not in ['nm','um','mm','m']:return None
  value=float(m[2])*{'nm':1,'um':1000,'mm':1000000,'m':1000000000}[unit]
 else:
  if unit not in ['','%']:return None
  value=float(m[2])
 return {'reported':s,'value':value,'unit':'nM' if kind=='Dc50' else 'percent','censoredOrApproximate':censored,'qualifier':m[1].strip()}
quant=[]
for x in rows:
 dc=numeric(x['Dc50'],'Dc50');dm=numeric(x['Dmax'],'Dmax')
 if dc and dm:quant.append({'id':x['PROTACDB ID'],'label':x['Active/Inactive'],'dc50':dc,'dmax':dm,'target':x['Target'],'PMID':x['Pubmed'],'cells':x['Cells'],'time':x['Time']})
unc=[x for x in quant if not x['dc50']['censoredOrApproximate'] and not x['dmax']['censoredOrApproximate']];context=['Pubmed','Target','E3 Ligase','Cells','Time','Ligand Name','Ligand PDB'];groups=collections.defaultdict(list);chem=collections.defaultdict(list)
for x in rows:key=tuple(x[k] for k in context);groups[key].append(x);chem[(x['PROTAC SMILES'],)+key[:5]].append(x)
mixed=[]
for key,g in groups.items():
 if len({x['Active/Inactive'] for x in g})<2:continue
 mixed.append({'context':dict(zip(context,key)),'n':len(g),'labels':dict(collections.Counter(x['Active/Inactive'] for x in g)),'allRows':g})
conflicts=[{'context':k,'rows':g} for k,g in chem.items() if len({x['Active/Inactive'] for x in g})>1];censusPDB={'5FQD','5T35','6BN7','6BOY','6HAX','6SIS','6H0F','7Q2J'};overlap=sorted({code.upper() for x in rows for code in re.findall(r'\b[0-9][A-Za-z0-9]{3}\b',x['Ligand PDB'])}&censusPDB)
out['negativePROTACSource']={'source':r,'gitBlob':'7937953fc851ba85be9a628c0bc765d8f3c4ff65','nRows':len(rows),'labels':dict(labels),'nNonemptyPMIDStrings':len({x['Pubmed'] for x in rows if x['Pubmed'].strip()}),'nTargetStrings':len({x['Target'] for x in rows}),'nNR4A3Rows':sum('Q92570' in x['Target'] or 'NR4A3' in x['Target'].upper() for x in rows),'quantitativeFieldAvailability':{k:{'nNonempty':sum(bool(x[k].strip()) for x in rows),'byLabel':dict(collections.Counter(x['Active/Inactive'] for x in rows if x[k].strip()))} for k in fields},'yesControlCounts':{k:sum(x[k].strip().lower()=='yes' for x in rows) for k in controls},'nParsedBothQuantitative':len(quant),'nUncensoredBoth':len(unc),'uncensoredLabels':dict(collections.Counter(x['label'] for x in unc)),'nUncensoredStrictDC50LE100DmaxGE80':sum(x['dc50']['value']<=100 and x['dmax']['value']>=80 for x in unc),'quantitativeBothRows':quant,'mixedMatchedGroups':mixed,'nMixedMatchedGroups':len(mixed),'nMixedGroupsFirstFiveContextFieldsNonempty':sum(all(g['context'][k].strip() for k in context[:5]) for g in mixed),'nMixedGroupsWithBinaryLigandPDB':sum(bool(g['context']['Ligand PDB'].strip()) for g in mixed),'conflictingExactChemicalContexts':conflicts,'literalBinaryPDBOverlapWithDeclaredEightEntrySet':overlap,'declaredEightEntrySet':sorted(censusPDB),'limits':['Curatedlabels heterogeneous, not standardized efficacy truth.','Missing quantitativefields not inactivity/zero.','Strictpotency differentdefinition from curatorActive; disagreements not labelerrors.','BinaryligandPDB not matchedternary; requires sourcelevelmatching.','NoNR4A3/EMCefficacy/newactivityclassifier.','PriorPROTACcuration/ML; METHODScontrols support.']}
for s in primary['sources']:
 if s['id'] not in ['ASO_KAMOLA','ASO_HAGEDORN_TOX','ASO_HAGEDORN_PANEL','ASO_TOEHOLD']:continue
 rec={'id':s['id'],'pmcid':s['pmcid'],'pdfs':[]};out['ASOSupplements'].append(rec)
 try:
  xml,xr=download(s['primarySource']['url']);assert xr['sha256']==s['primarySource']['sha256'];out['receipts'].append(xr);root=ET.fromstring(xml);meta=root.find('./front/article-meta');journal=root.find('./front/journal-meta');tx=lambda node: ''.join(node.itertext()).strip() if node is not None else None
  rec['primaryCitation']={'title':tx(meta.find('./title-group/article-title')),'authors':[{'given':tx(n.find('given-names')),'surname':tx(n.find('surname'))} for n in meta.findall('./contrib-group/contrib/name')],'journal':tx(journal.find('./journal-title-group/journal-title')),'articleIds':{n.attrib.get('pub-id-type'):tx(n) for n in meta.findall('./article-id')},'volume':tx(meta.find('./volume')),'firstPage':tx(meta.find('./fpage')),'lastPage':tx(meta.find('./lpage')),'dates':[{**n.attrib,'year':tx(n.find('year'))} for n in meta.findall('./pub-date')]}
  old=s['supplementArchive']
  if s['id']=='ASO_TOEHOLD':
   zpath=P('campaign-output/aso-toehold-primary-supplements.zip')
   if not zpath.exists():
    xs=list(P('.').rglob(zpath.name));assert len(xs)==1,[str(x) for x in xs];zpath=xs[0]
   zbytes=zpath.read_bytes();receipt={'restoredPath':str(zpath),'bytes':len(zbytes),'sha256':hashlib.sha256(zbytes).hexdigest()}
  else:
   zbytes,receipt=download(old['url']);zpath=P('campaign-output/aso-pdf-sources')/(s['id']+'.zip');zpath.parent.mkdir(parents=True,exist_ok=True);zpath.write_bytes(zbytes)
  rec['archiveReceipt']=receipt;rec['frozenContainerSha256']=old['sha256'];rec['containerDigestMatches']=receipt['sha256']==old['sha256'];out['receipts'].append(receipt)
  with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
   manifest=sorted((x.filename,x.file_size) for x in z.infolist());expected=sorted((x['name'],x['bytes']) for x in s['archiveMembers']);assert manifest==expected,'Fullsupplementmember manifest changed';frozen={x['file']:x['sha256'] for x in s.get('parsedSupplementTables',[]) if x.get('sha256')}
   if s['id']=='ASO_KAMOLA':frozen['supp_gkv857_NAR_OTE_Supplement_rev_3.docx']='7f7bd901a659311cfd79658373ab85a1b36d99c77a4d6a77b09d57c9b0896aa2'
   rec['verifiedFrozenMemberHashes']={}
   for member,expectedsha in frozen.items():
    mb=z.read(member);assert hashlib.sha256(mb).hexdigest()==expectedsha;rec['verifiedFrozenMemberHashes'][member]=expectedsha
   rec['completeMemberManifest']=manifest
   for member,size in manifest:
    if not member.lower().endswith('.pdf'):continue
    mb=z.read(member);reader=PdfReader(io.BytesIO(mb));pages=[];plain=[];layout=[]
    for i,page in enumerate(reader.pages):
     pt=page.extract_text() or ''
     try:lt=page.extract_text(extraction_mode='layout') or ''
     except Exception:lt=pt
     plain.append(pt);layout.append(lt);selected=bool(re.search(r'table|sequence|gapmer|antisense|ASO|mismatch|off.target|RNase|GSE',pt,re.I));pages.append({'page':i+1,'characters':len(pt),'selectedForNumericReview':selected,'plainText':pt if selected else '', 'layoutText':lt if selected else ''})
    base=P('campaign-output/aso-pdf-sources')/s['id'];base.mkdir(parents=True,exist_ok=True);stem=P(member).stem;paths=[]
    for suffix,text in [('plain','\n\f\n'.join(plain)),('layout','\n\f\n'.join(layout))]:
     target=base/(stem+'.'+suffix+'.txt');target.write_text(text);paths.append({'path':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    rec['pdfs'].append({'member':member,'bytes':len(mb),'sha256':hashlib.sha256(mb).hexdigest(),'nPages':len(pages),'allPageTextReceipts':paths,'pages':pages,'nLowTextPages':sum(x['characters']<100 for x in pages),'scope':'Extractioncompleted; numericreview follows, imageonly tables unparsed.'})
 except Exception as ex:out['errors'].append({'source':s['id'],'error':repr(ex)})
P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('ASO_PDF_PROTAC_BEGIN');print(json.dumps(out));print('ASO_PDF_PROTAC_END')
if out['errors']:sys.exit(1)
