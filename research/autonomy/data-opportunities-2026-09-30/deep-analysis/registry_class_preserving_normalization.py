import argparse,hashlib,json,re
from collections import Counter,defaultdict,deque
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',default='research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/registry-complete-matches-actual.json');p.add_argument('--out',default='campaign-output/registry-class-preserving-normalization.json');args=p.parse_args();raw=Path(args.input).read_bytes();root=json.loads(raw)
def find_payload(x):
 q=deque([x])
 while q:
  v=q.popleft()
  if isinstance(v,dict):
   if isinstance(v.get('literalTables'),list) and 'rows' in v:return v
   q.extend(v.values())
  elif isinstance(v,list):q.extend(v)
  elif isinstance(v,str) and v.lstrip().startswith(('{','[')):
   try:q.append(json.loads(v))
   except ValueError:pass
 raise ValueError('No durable literalTables payload')
x=find_payload(root);tables=x['literalTables'];assert len(tables)==552
words={'CR':['cr','complete response','complete remission'],'PR':['pr','partial response','partial remission'],'SD':['sd','stable disease'],'PD':['pd','progressive disease']}
def alias(title):
 s=' '.join(str(title or '').casefold().split());s=s.rstrip('.')
 for k,w in words.items():
  for a in w:
   if s==a:return dict(category=k,family='unqualified')
   if s==k.casefold()+' '+a and a!=k.casefold():return dict(category=k,family='unqualified')
   m=re.fullmatch(re.escape(a)+r'\s*\((i|ir)?'+k.casefold()+r'\)',s)
   if m:return dict(category=k,family=m.group(1) or 'conventional')
 return None
def integer(v):
 s=str(v).strip();return int(s) if re.fullmatch(r'\d+',s) else None
def class_denoms(fields,gid):
 out=[]
 for d in fields.get('denoms',[]):
  for c in d.get('counts',[]):
   if c.get('groupId')==gid:out.append(dict(units=d.get('units'),valueLiteral=c.get('value'),integerValue=integer(c.get('value'))))
 return out
r=dict(schema='registry-class-preserving-normalization/1',inputArtifact=args.input,inputSHA256=hashlib.sha256(raw).hexdigest(),sourceSchema=x.get('schema'),literalTables=len(tables),compactRows=len(x['rows']),rows=[],limits=['No summing categories or classes whose disjointness is unknown','No silently choosing duplicate aliases','CR/PR fractions are arithmetic under literal labels, not automatically comparable clinical ORR','Arithmetic agreement with a posted denominator does not validate a clinical response partition','Repeated query occurrences retained separately from distinct literal outcome tables'])
for t in tables:
 classes=defaultdict(list)
 for z in t['allCategoryMeasurements']:classes[z['classIndex']].append(z)
 for ci,records in sorted(classes.items()):
  fields=records[0].get('classFields',{});cd=class_denoms(fields,t['groupId']);den=cd if cd else (t.get('postedDenominators',[]) if len(classes)==1 else []);ns=sorted({d['integerValue'] for d in den if str(d.get('units','')).casefold()=='participants' and d.get('integerValue') is not None});n=ns[0] if len(ns)==1 else None
  recognized=defaultdict(list);literal=[]
  for z in records:
   a=alias(z.get('categoryTitle'));v=dict(z);v['exactAlias']=a;literal.append(v)
   if a:recognized[a['category']].append(v)
  complete=all(len(recognized[k])==1 and recognized[k][0].get('integerValue') is not None for k in words);cells={k:recognized[k][0]['integerValue'] for k in words} if complete else None;crpr=all(len(recognized[k])==1 and recognized[k][0].get('integerValue') is not None for k in ('CR','PR'));response=sum(recognized[k][0]['integerValue'] for k in ('CR','PR')) if crpr else None;families=sorted({v['exactAlias']['family'] for v in literal if v['exactAlias']})
  row=dict(tableId=t['tableId'],nctId=t['nctId'],outcomeJSONSha256=t['outcomeJSONSha256'],outcomeTitle=t['outcomeTitle'],outcomeType=t.get('outcomeType'),timeFrame=t.get('timeFrame'),populationDescription=t.get('populationDescription'),groupId=t['groupId'],groupLiteral=t.get('groupLiteral'),classIndex=ci,classFields=fields,numberOfClasses=len(classes),allLiteralMeasurements=literal,classFieldsConsistent=all(z.get('classFields',{})==fields for z in records),sourceOccurrences=t.get('sourceOccurrences',[]),classPostedDenominators=cd,chosenDenominatorScope='class' if cd else ('overall-single-class' if len(classes)==1 else 'none-for-multiple-classes'),candidateParticipantDenominators=ns,participantDenominator=n,exactAliasFamilies=families,duplicateExactAliases={k:v for k,v in recognized.items() if len(v)>1},fourExactCells=cells,status='four-exact-unambiguous-categories' if complete else 'literal-adjudication-required',legacyCompactCells=t['fourCategoryCells'],correctedCellsDifferFromLegacy=(cells!=t['fourCategoryCells']) if cells is not None else None,fourCellSum=sum(cells.values()) if cells else None,fourCellSumEqualsDenominator=(sum(cells.values())==n) if cells is not None and n is not None else None,CRplusPR=response,CRplusPRArithmeticFraction=(response/n) if response is not None and n is not None and n>0 and response<=n else None,excludedLiteralCategories=[z for z in literal if z['exactAlias'] is None]);r['rows'].append(row)
r['summary']=dict(classGroupRows=len(r['rows']),statusCounts=dict(Counter(z['status'] for z in r['rows'])),multiClassTables=len({z['tableId'] for z in r['rows'] if z['numberOfClasses']>1}),multiClassRows=sum(z['numberOfClasses']>1 for z in r['rows']),completeChangedRows=sum(z['correctedCellsDifferFromLegacy'] is True for z in r['rows']),singleClassChangedRows=sum(z['correctedCellsDifferFromLegacy'] is True and z['numberOfClasses']==1 for z in r['rows']),classDenominatorRows=sum(z['chosenDenominatorScope']=='class' for z in r['rows']),missingOrAmbiguousDenominatorRows=sum(z['participantDenominator'] is None for z in r['rows']),exactDuplicateAliasRows=sum(bool(z['duplicateExactAliases']) for z in r['rows']),fourCellArithmeticEqualityRows=sum(z['fourCellSumEqualsDenominator'] is True for z in r['rows']))
out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print('EMC_REGISTRY_CLASS_RESULT_BEGIN');print(json.dumps(r,separators=(',',':')));print('EMC_REGISTRY_CLASS_RESULT_END')
