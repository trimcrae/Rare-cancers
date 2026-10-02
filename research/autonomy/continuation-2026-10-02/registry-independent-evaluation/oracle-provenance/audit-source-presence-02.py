from pathlib import Path
import json,hashlib,datetime,copy
p=Path('C:/Users/mcrae/.codex/private/emc-continuation-20261002'); dest=p/'checkpoint05-registry-oracle'
sourcepath=p/'checkpoint05-registry/api-response.json'; oraclepath=dest/'oracle.json'; priorpath=dest/'offset-amendment-01.json'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(sourcepath)=='d20367d3d14f99716b20309ee8bed1cebe4b6a1270077fc0ac234a4cc5b91fa6'
assert sha(oraclepath)=='302ba913bdebe23f312f7cdb674b34af79ed4b7a4b8c0b57f3695c8794e6af6e'
assert sha(priorpath)=='8977179a2c54afefa75e05e8a1fba87fa965526dd36998b6609833a67109bcb3'
s=json.loads(sourcepath.read_text(encoding='utf-8'));orig=json.loads(oraclepath.read_text(encoding='utf-8'));o=copy.deepcopy(orig);prior=json.loads(priorpath.read_text(encoding='utf-8'))
def parts(path):return [t.replace('~1','/').replace('~0','~') for t in path.lstrip('/').split('/')]
def get(doc,path):
 for t in parts(path):doc=doc[int(t)] if isinstance(doc,list) else doc[t]
 return doc
def parent(doc,path):
 par,leaf=path.rsplit('/',1);return get(doc,par),leaf.replace('~1','/').replace('~0','~')
for ch in prior['changes']:
 pa,leaf=parent(o,ch['oraclePointer']);assert pa[leaf]==ch['old'];pa[leaf]=ch['new']
changes=[];evidence_count=0;reference_count=0;present_null=[];affected=[]
def walk(x,path=''):
 global evidence_count,reference_count
 if isinstance(x,dict):
  for key,val in x.items():
   if (key=='sourcePointer' or key=='measurementCategoryPointer' or key=='supportPointer') and isinstance(val,str):
    get(s,val);reference_count+=1
  if 'pointer' in x and ('value' in x or 'literal' in x):
   evidence_count+=1;pa,leaf=parent(s,x['pointer'])
   exists=(0<=int(leaf)<len(pa)) if isinstance(pa,list) else leaf in pa
   if not exists:
    assert isinstance(pa,dict) and x.get('value','NOT_NULL') is None and 'literal' not in x
    assert 'sourceFieldPresent' not in x
    changes.append({'operation':'add','oraclePointer':path+'/sourceFieldPresent','oldAbsent':True,'new':False})
    affected.append({'oracleEvidenceObjectPointer':path,'sourcePointer':x['pointer'],'sourceParentExists':True,'sourceLeafExists':False,'oracleValueIsNullPlaceholder':True})
   else:
    val=pa[int(leaf)] if isinstance(pa,list) else pa[leaf]
    if 'value' in x:assert val==x['value'],path
    if 'literal' in x:
     assert isinstance(val,str)
     if 'decodedStringStart' in x:
      start,end=x['decodedStringStart'],x['decodedStringEndExclusive'];assert 0<=start<=end<=len(val);assert val[start:end]==x['literal'],path
     else:assert val==x['literal'],path
    if val is None:present_null.append(path)
  for key,val in list(x.items()):walk(val,path+'/'+key)
 elif isinstance(x,list):
  for i,val in enumerate(x):walk(val,path+'/'+str(i))
walk(o)
assert len(changes)==2
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
audit={'evidenceObjectsChecked':evidence_count,'additionalSourceReferencesChecked':reference_count,'missingLeafEvidenceObjects':len(changes),'missingParentPointers':0,'presentNullEvidenceObjects':present_null,'literalAndValueMismatchesAfterPriorOffsetAmendment':0,'affectedPointers':affected,'classifiersReadOrExecuted':False}
am={'schema':'blind-oracle-source-presence-amendment/1','createdUTC':now,'originalOracleSHA256':sha(oraclepath),'priorAmendmentSHA256':sha(priorpath),'sourceSHA256':sha(sourcepath),'reason':'Pre-prediction binding audit distinguishes absent optional source fields from actual null fields. Original values were null placeholders; only explicit absence metadata is added. All semantic labels and reasons remain unchanged.','changes':changes,'semanticLabelsChanged':False,'audit':audit}
for ch in changes:
 pa,leaf=parent(o,ch['oraclePointer']);assert leaf not in pa;pa[leaf]=ch['new']
# Verify every absent marker is justified, including no accidental value or semantic changes.
for a in affected:
 ev=get(o,a['oracleEvidenceObjectPointer']);pa,leaf=parent(s,ev['pointer']);assert isinstance(pa,dict) and leaf not in pa and ev['sourceFieldPresent'] is False and ev['value'] is None
reverted=copy.deepcopy(o)
for ch in changes:
 pa,leaf=parent(reverted,ch['oraclePointer']);del pa[leaf]
for ch in prior['changes']:
 pa,leaf=parent(reverted,ch['oraclePointer']);pa[leaf]=ch['old']
assert reverted==orig
ap=dest/'source-presence-amendment-02.json';assert not ap.exists();ap.write_text(json.dumps(am,indent=2)+'\n',encoding='utf-8')
r={'schema':'blind-oracle-mechanical-amendment-receipt/1','createdUTC':now,'inputs':[{'path':str(v),'sha256':sha(v),'bytes':v.stat().st_size} for v in [sourcepath,oraclepath,priorpath]],'outputs':[{'path':str(ap),'sha256':sha(ap),'bytes':ap.stat().st_size}],'audit':audit,'originalOracleUnchanged':sha(oraclepath)==am['originalOracleSHA256'],'priorOffsetAmendmentUnchanged':sha(priorpath)==am['priorAmendmentSHA256']}
rp=dest/'source-presence-amendment-02-receipt.json';assert not rp.exists();rp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'amendmentSHA256':sha(ap),'receiptSHA256':sha(rp),'audit':audit},indent=2))
