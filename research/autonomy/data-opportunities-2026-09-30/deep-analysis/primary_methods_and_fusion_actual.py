import os,json,hashlib,urllib.request,re,io,html,xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=Path('campaign-output/proteomics');ROOT.mkdir(parents=True,exist_ok=True)
MR=Path('campaign-output/authentic-screen');MR.mkdir(parents=True,exist_ok=True);receipts=[];methods=[]
def get(name,url,cap=12*1024**2,ext='txt'):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-primary-methods-audit/1'}),timeout=75) as r:b=r.read(cap+1);final=r.geturl();ctype=r.headers.get('Content-Type','')
  if len(b)>cap:raise ValueError('Frozen source cap exceeded')
  rec={'name':name,'status':'completed','url':url,'finalURL':final,'contentType':ctype,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
  (MR/(name+'.'+ext)).write_bytes(b);receipts.append(rec);print('PRIMARY_METHOD_SOURCE '+json.dumps(rec),flush=True);return b
 except Exception as e:
  rec={'name':name,'status':'failed','url':url,'error':type(e).__name__+': '+str(e)};receipts.append(rec);print('PRIMARY_METHOD_SOURCE '+json.dumps(rec),flush=True);return None
def excerpt(name,b,terms):
 if b is None:return {'name':name,'status':'source access failed','excerpts':[]}
 s=b.decode('utf-8',errors='replace');s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
 text=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s)));out=[];seen=set()
 for term in terms:
  for hit in list(re.finditer(term,text,re.I))[:8]:
   key=(max(0,hit.start()-250)//100,term)
   if key in seen:continue
   seen.add(key);out.append({'term':term,'text':text[max(0,hit.start()-250):hit.end()+1200]})
 result={'name':name,'status':'source text retrieved','textCharacters':len(text),'excerpts':out,'scope':'Exact source excerpts, not automatically adjudicated methods or units'}
 print('PRIMARY_METHOD_EXCERPTS '+json.dumps(result),flush=True);return result
def parse_failure(name,e):
 status={'name':name,'status':'parse or identity failed','error':type(e).__name__+': '+str(e)};methods.append(status);print('PRIMARY_METHOD_PARSE_STATUS '+json.dumps(status),flush=True)
terms=[r'drug screening',r'IC.?50',r'viability',r'\b72\b',r'\b96\b',r'CellTiter',r'WST',r'10\s*[µμu]M',r'triplicate',r'DMSO']
ib=get('iwata-publisher-primary','https://link.springer.com/article/10.1007/s13577-025-01250-7',ext='html');methods.append(excerpt('iwata-publisher-primary',ib,terms))
sb=get('iwata-europepmc-record','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1007%2Fs13577-025-01250-7&format=json',ext='json')
if sb is not None:
 try:
  entries=json.loads(sb).get('resultList',{}).get('result',[])
  for entry in entries:
   if entry.get('doi','').lower()!='10.1007/s13577-025-01250-7':continue
   pid=entry.get('pmcid','')
   if re.fullmatch(r'PMC\d+',pid):
    xb=get('iwata-europepmc-primary','https://www.ebi.ac.uk/europepmc/webservices/rest/'+pid+'/fullTextXML',ext='xml');methods.append(excerpt('iwata-europepmc-primary',xb,terms))
 except Exception as e:parse_failure('iwata-europepmc-record',e)
bb=get('bangerter-primary','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML',ext='xml')
if bb is not None:
 try:
  xml=ET.fromstring(bb);dois=[(v.text or '').strip().lower() for v in xml.iter('article-id') if v.attrib.get('pub-id-type')=='doi']
  if '10.1007/s13577-022-00818-x' not in dois:raise ValueError('Bangerter primary DOI identity mismatch: '+str(dois))
  methods.append(excerpt('bangerter-primary',bb,[r'drug screening',r'viability',r'CellTiter',r'day\s*6',r'ATP',r'concentration',r'replicate',r'DMSO']))
 except Exception as e:parse_failure('bangerter-primary',e)
pb=get('procan-primary-growth','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9387775/fullTextXML',ext='xml');methods.append(excerpt('procan-primary-growth',pb,[r'growth',r'DMSO',r'day\s*4',r'day\s*1',r'ln.?IC',r'natural log']))
(MR/'primary-assay-methods-access.json').write_text(json.dumps({'receipts':receipts,'sources':methods},indent=2)+'\n')
source=Path(os.environ.get('PROTEOMICS_MATCHED_SOURCE',str(HERE/'results'/'protein-RNA-matched-measurements.json')))
meta=pd.DataFrame(json.loads(source.read_text())['metadata']).set_index('model_id');meta.loc[meta.Cancer_type.eq('Mesothelioma'),'primarySarcomaTest']=False;primary=meta[meta.primarySarcomaTest].copy()
url='https://ndownloader.figshare.com/files/25843121';fb=get('depmap20q2-fusion-calls',url,cap=16*1024**2,ext='csv')
if fb is None:raise ValueError('Fusion source unavailable; method receipts already retained')
if len(fb)!=7592535 or hashlib.md5(fb).hexdigest()!='94edbf8a431f7c476df9fbdfe28b7257':raise ValueError('Pinned fusion source mismatch')
receipt={'url':url,'bytes':len(fb),'md5':hashlib.md5(fb).hexdigest(),'sha256':hashlib.sha256(fb).hexdigest(),'article':13456373,'fileID':25843121};(ROOT/'fusion-annotation-source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
f=pd.read_csv(io.BytesIO(fb));print('ATR_FUSION_SOURCE_SCHEMA '+json.dumps({'receipt':receipt,'columns':list(f.columns),'rows':len(f),'preview':json.loads(f.head(4).to_json(orient='records'))}),flush=True)
ids=[c for c in f if re.sub(r'[^a-z0-9]','',str(c).lower())=='depmapid'];left=[c for c in f if str(c) in ['LeftGene','Gene5Prime','gene5prime']];right=[c for c in f if str(c) in ['RightGene','Gene3Prime','gene3prime']]
if len(ids)!=1 or len(left)!=1 or len(right)!=1:raise ValueError('Unknown actual fusion schema; header retained')
f['sourceRow']=range(2,len(f)+2);f['BROAD_ID']=f[ids[0]].astype(str);symbol=lambda v:re.sub(r'\s*\([^)]*\)\s*$','',str(v)).strip().upper();f['leftSymbol']=f[left[0]].map(symbol);f['rightSymbol']=f[right[0]].map(symbol)
FET=[('EWSR1','FLI1'),('EWSR1','ERG'),('EWSR1','ETV1'),('EWSR1','ETV4'),('EWSR1','FEV'),('FUS','ERG'),('FUS','FEV'),('FUS','DDIT3'),('EWSR1','DDIT3'),('FUS','CREB3L2'),('FUS','CREB3L1'),('EWSR1','CREB3L1'),('EWSR1','ATF1'),('EWSR1','CREB1'),('EWSR1','NR4A3'),('TAF15','NR4A3'),('EWSR1','WT1')]
OTHER=[('SS18','SSX1'),('SS18','SSX2'),('PAX3','FOXO1'),('PAX7','FOXO1')];fet={frozenset(x) for x in FET};other={frozenset(x) for x in OTHER}
f['frozenFETDriverCall']=[frozenset((a,c)) in fet for a,c in zip(f.leftSymbol,f.rightSymbol)];f['frozenOtherDriverCall']=[frozenset((a,c)) in other for a,c in zip(f.leftSymbol,f.rightSymbol)]
known=set(f.BROAD_ID);fetids=set(f.loc[f.frozenFETDriverCall,'BROAD_ID']);otherids=set(f.loc[f.frozenOtherDriverCall,'BROAD_ID'])
aliases=primary.BROAD_ID.fillna('').astype(str).map(lambda v:[x.strip() for x in v.split(';') if re.fullmatch(r'ACH-\d+',x.strip())])
primary['sourceBroadAliases']=aliases
primary['anyFusionRecordPresent']=aliases.map(lambda v:any(x in known for x in v));primary['observedFETDriver']=aliases.map(lambda v:any(x in fetids for x in v));primary['observedOtherDriver']=aliases.map(lambda v:any(x in otherids for x in v))
primary['aliasCallAudit']=aliases.map(lambda v:[{'BROAD_ID':x,'anySourceRowPresent':x in known,'observedFETDriver':x in fetids,'observedOtherDriver':x in otherids} for x in v])
primary['callCategory']=['observed-FET-and-other' if a and c else 'observed-FET-driver' if a else 'observed-other-driver' if c else 'no-frozen-driver-observed-coverage-unknown' for a,c in zip(primary.observedFETDriver,primary.observedOtherDriver)]
fields=['Cell_line','BROAD_ID','Cancer_type','Cancer_subtype','relatedGroup','sourceBroadAliases','aliasCallAudit','anyFusionRecordPresent','observedFETDriver','observedOtherDriver','callCategory'];matching=f[f.BROAD_ID.isin({x for v in aliases for x in v})&(f.frozenFETDriverCall|f.frozenOtherDriverCall)]
res={'schema':'sarcoma-observed-fusion-call-audit/1','sourceReceipt':receipt,'primaryModels':len(primary),'frozenFETDriverPairs':FET,'frozenOtherDriverPairs':OTHER,'perLineageObservedCategories':primary.groupby(['Cancer_type','callCategory']).size().reset_index(name='n').to_dict('records'),'modelCalls':json.loads(primary[fields].reset_index().to_json(orient='records')),'matchingSourceDriverRows':json.loads(matching.to_json(orient='records')),'limitations':['Positive observed calls support molecular annotation; no row is not assay-negative','RNA fusion calls alone are not orthogonal validation or verified EMC','Fusion and histology effects cannot be separated when positives occupy one lineage','Historical20Q2 overlapping models are not an independent cohort']}
(ROOT/'atr-fusion-annotation-actual.json').write_text(json.dumps(res,indent=2)+'\n');print('PRIMARY_METHOD_FINAL_ACCESS_BEGIN');print(json.dumps({'receipts':receipts,'sources':methods}));print('PRIMARY_METHOD_FINAL_ACCESS_END');print('ATR_FUSION_ACTUAL_RESULT_BEGIN');print(json.dumps(res));print('ATR_FUSION_ACTUAL_RESULT_END',flush=True)
