import json, hashlib, datetime
from pathlib import Path
src=Path('C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint05-registry')
out=src.parent/'checkpoint05-registry-oracle'
b=(src/'api-response.json').read_bytes()
assert hashlib.sha256(b).hexdigest()=='d20367d3d14f99716b20309ee8bed1cebe4b6a1270077fc0ac234a4cc5b91fa6'
d=json.loads(b)
eligible={(0,1),(2,2),(3,7),(3,8),(3,9),(5,2),(7,1),(7,5),(8,0)}
reasons={}
def add(s, inds, reason):
 for i in inds: reasons[s,i]=reason
add(0,[0],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(0,[2],'Response duration is a temporal endpoint, not response rate or categorical response distribution.')
add(0,[3],'Progression-free survival is a temporal event endpoint, not response rate or categorical response distribution.')
add(1,[0],'Pain scale deterioration is a symptom endpoint, not tumor/disease response.')
add(1,[1],'Chemotherapy dose reduction measures treatment delivery, not tumor/disease response.')
add(2,[0],'Progression-free survival is a temporal event endpoint despite named Lugano criteria; no response distribution is reported.')
add(2,[1],'Overall survival is a mortality/time endpoint, not tumor/disease response.')
add(2,[3],'Response duration is a temporal endpoint despite named Lugano criteria; no response distribution is reported.')
add(2,[4,5],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(3,[0,1,2],'Progression-free survival is a temporal event endpoint despite named RECIST criteria; no response distribution is reported.')
add(3,[3],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(3,[4,5,6],'Overall survival is a mortality/time endpoint, not tumor/disease response.')
add(3,[10,11,12],'Response duration is a temporal endpoint despite named RECIST criteria; no response distribution is reported.')
add(3,list(range(13,20)),'Drug serum concentration is a pharmacokinetic endpoint, not tumor/disease response.')
add(3,[20],'Antidrug antibody positivity is an immunogenicity endpoint, not tumor/disease response.')
add(3,[21,22,23],'Patient-reported symptom/quality-of-life scale change, not tumor/disease response.')
add(4,[0],'Overall survival is a mortality/time endpoint, not tumor/disease response.')
add(4,[1,2],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(5,[0],'Dose selection based on toxicity; a mention of listing response does not turn this dose endpoint into response results.')
add(5,[1],'Progression-free survival is a temporal endpoint; source additionally reports no Phase II enrollment and unavailable PFS.')
add(5,[3],'Overall survival is a mortality/time endpoint; source additionally reports no Phase II enrollment.')
add(5,[4],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(6,[0],'Continuous lobular Ki67 biomarker change; no tumor/disease response assessment or categorical response distribution.')
add(7,[0,14],'Safety/adverse-event endpoint, not a tumor/disease response distribution.')
add(7,[2],'Response duration is a temporal endpoint, not response rate or categorical response distribution.')
add(7,[3],'Time to response is a temporal endpoint, not response rate or categorical response distribution.')
add(7,[4],'Progression-free survival is a temporal event endpoint, not response rate or categorical response distribution.')
add(7,[6],'Overall survival is a mortality/time endpoint, not tumor/disease response.')
add(7,list(range(7,13)),'Drug exposure/concentration/kinetics endpoint, not tumor/disease response.')
add(7,[13],'Antidrug antibody positivity is an immunogenicity endpoint, not tumor/disease response.')
add(9,list(range(6)),'Cardiovascular/renal physiological change endpoint, not tumor/disease response.')
add(9,[6],'Urinary renal-dysfunction biomarker endpoint, not tumor/disease response.')
rows=[]
def evidence(o,p,field,literal):
 assert literal in o[field],(field,literal)
 start=o[field].index(literal)
 return {'pointer':p+'/'+field,'literal':literal,'decodedStringStart':start,'decodedStringEndExclusive':start+len(literal)}
for s,st in enumerate(d['studies']):
 for i,o in enumerate(st['resultsSection']['outcomeMeasuresModule']['outcomeMeasures']):
  p=f'/studies/{s}/resultsSection/outcomeMeasuresModule/outcomeMeasures/{i}'
  yes=(s,i) in eligible
  row={'nctId':st['protocolSection']['identificationModule']['nctId'],'studyIndex':s,'outcomeIndex':i,'title':o['title'],'sourcePointer':p,'eligibility':'eligible' if yes else 'excluded','reason':'Direct tumor/disease response rate or categorical response distribution.' if yes else reasons[s,i], 'screeningEvidence':[evidence(o,p,'title',o['title'])]}
  if not yes:
   row['familyReviewStatus']='not_evaluated_for_excluded_endpoint'
   rows.append(row); continue
  family={'status':'assigned','family':None,'version':None,'modifier':None,'modifierStatus':'not_explicitly_stated','support':[]}
  if s==0: fam,ver,lit='iwCLL','2018','International Workshop on Chronic Lymphocytic Leukemia (iwCLL) 2018 criteria'
  elif s==2: fam,ver,lit='Lugano','2014','Lugano criteria 2014'
  elif s==3: fam,ver,lit='RECIST','1.1','RECIST v1.1'
  elif s==5: fam,ver,lit='RECIST','1.1','Response Evaluation Criteria in Solid Tumors 1.1'
  elif s==7 and i==1: fam,ver,lit='RECIST','1.1','Response Evaluation Criteria in Solid Tumors (RECIST) Version 1.1'
  elif s==7: fam,ver,lit='RECIST','1.1','RECIST Version 1.1'
  else: fam,ver,lit=None,None,None
  family.update(family=fam,version=ver)
  if lit: family['support']=[evidence(o,p,'description',lit)]
  else:
   family.update(status='unknown',reason='Cystoscopy/cytology definition is explicit, but no named response-criteria family/version is established. Complete Response alone does not imply RECIST.')
  row['family']=family
  row['sourceContext']={k:{'pointer':p+'/'+k,'value':o.get(k)} for k in ['description','timeFrame','populationDescription','paramType','unitOfMeasure','dispersionType','reportingStatus']}
  row['reader']={'status':'not_explicit_in_this_outcome','support':[]}
  if s in [0,2,3] or (s==7 and i==5):
   field='title' if s==3 else 'description'
   literal='Investigator' if s==3 else 'investigator'
   row['reader']={'status':'investigator','support':[evidence(o,p,field,literal)]}
  row['confirmation']={'status':'not_explicit_in_this_outcome','support':[]}
  if s==3:
   row['confirmation']={'status':'confirmed','support':[evidence(o,p,'description','confirmed best overall response (BOR)')]}
  if s==7 and i==5:
   row['confirmation']={'status':'requirement_referenced_but_not_specified','support':[evidence(o,p,'description','taking into account any requirement for confirmation')]}
  row['reportedStructures']={k:{'pointer':p+'/'+k,'value':o.get(k)} for k in ['groups','denoms','classes']}
  row['literalRoles']=[]
  if s==5:
   roles=['complete_response','partial_response','stable_disease','progressive_disease','missing']
   for ci,(cl,role) in enumerate(zip(o['classes'],roles)):
    row['literalRoles'].append({'pointer':p+f'/classes/{ci}/title','literal':cl['title'],'role':role,'mappingScope':'literal label only; no patient reclassification'})
  elif s==8:
   for ci,cat in enumerate(o['classes'][0]['categories']):
    row['literalRoles'].append({'pointer':p+f'/classes/0/categories/{ci}/title','literal':cat['title'],'role':['complete_response','no_response_unspecified'][ci],'mappingScope':'literal label only; No Response not equated with progressive disease'})
  else:
   literals= {'0':['complete response (CR)','complete response with incomplete marrow recovery (CRi)','partial response (PR)'],'2':['complete response (CR)','partial response (PR)'],'3':['complete response (CR)','partial response (PR)'],'7':['complete response','partial response']}[str(s)] if not (s==7 and i==5) else ['CR','PR','stable disease']
   roles=['complete_response','complete_response_incomplete_marrow_recovery','partial_response'] if s==0 else (['complete_response','partial_response','stable_disease'] if s==7 and i==5 else ['complete_response','partial_response'])
   for literal,role in zip(literals,roles):
    row['literalRoles'].append(dict(evidence(o,p,'description',literal),role=role,mappingScope='definition component; no separate category counts reported'))
   row['aggregateRole']={'role':'disease_control_rate' if s==7 and i==5 else 'overall_objective_response_rate','measurementCategoryPointer':p+'/classes/0/categories/0','categoryTitleAbsent':True,'supportPointer':p+'/description','note':'Reported aggregate measurement retained; no reconstruction or sum of components.'}
  row['denominatorPolicy']='Preserve each source group and denominator as reported; no pooling, zero-denominator rate interpretation, or recalculation.'
  row['caveats']=[]
  if s==5:
   row['caveats']=['Source SD prose is malformed/reversed: retain verbatim, do not repair or use to classify patients. Named RECIST 1.1 family and literal class labels remain explicit.', 'Phase II groups have reported denominator zero and no displayed response measurements; do not infer zero response rates. Missing class is preserved separately.']
   row['sourceConflictSupport']=[evidence(o,p,'description','Stable Disease (SD); to enough increase to be PR, nor enough decrease to be PD.')]
  if s==7 and i==1: row['caveats']=['Investigator and confirmed response are stated in other temporal outcomes of this study, but not imported into this outcome as certain reader/confirmation labels.']
  if s==8: row['caveats']=['No named criteria family; local marker-lesion disappearance with negative cystoscopy and cytology is preserved without clinical interpretation.']
  if s==3: row['caveats']=['Source says external-control pooling was planned for PFS/OS, not ORR; preserve this outcome population and denominators.']
  rows.append(row)
assert len(rows)==68 and len([x for x in rows if x['eligibility']=='eligible'])==9
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
oracle={'schema':'blind-source-context-oracle/1','frozenUTC':now,'reviewer':'registry_blind_oracle LLM source-context reviewer','blindness':'Read only AMENDMENT.md, acquisition-receipt.json, and api-response.json. No classifier code, predictions, or historic 575 outcome content read.','sourceSHA256':hashlib.sha256(b).hexdigest(),'selection':'Frozen first page, 10 date-selected studies; no replacement or pagination.','screeningScope':'Direct tumor/disease response proportions or categorical response distributions. Temporal DOR/TTR/PFS and mortality endpoints excluded even when named response criteria occur.','counts':{'outcomes':68,'eligible':9,'excluded':59,'uncertain':0,'eligibleStudies':6,'assignedFamily':8,'unknownFamily':1,'ambiguousFamily':0},'limitations':['Small post-development convenience slice; not independent clinical adjudication or a stable accuracy estimate.','No paired named family conflict observed in eligible contexts; malformed SD definition retained as caveat.','Unknown family is not evidence of no clinical criteria.','Family assignment is semantic source-label extraction, not validation of clinical criteria application.'],'outcomes':rows}
method='''---
id: DOC-CHECKPOINT05-REGISTRY-BLIND-ORACLE-METHOD
title: Frozen blind source-context oracle review method
kind: memo
status: frozen
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Document independent-of-predictions screening and source-label extraction before classifier evaluation.
scope: All 68 returned outcomes in the ten-study registry date slice.
audience: [maintainers, reviewers]
---

The separate LLM reviewer read only the amendment, acquisition receipt, and exact acquired API response. Classifier code, predictions, and historical 575 outcome texts were not inspected. The receipt exposes baseline study identifiers but not their labels. No web, UI, browser automation, new checkout, runtime, or large artifact was used.

Every zero-based outcome was screened in returned order. Eligibility means a direct tumor/disease response proportion or categorical response distribution. DCR qualifies; symptom, safety, drug exposure, immunogenicity, dose selection, continuous Ki67, mortality, and temporal DOR/TTR/PFS endpoints do not. Temporal outcomes remain explicitly excluded even if they mention named response criteria; this boundary is fixed before evaluation. There were nine eligible outcomes in six studies and 59 exclusions. No uncertain eligibility was required, which does not imply uncertainty-free clinical data.

For eligible outcomes, family/version requires explicit source naming. CR/PR alone does not establish RECIST. No named modifier is inferred from confirmation language, disease type, or local assessment. The cystoscopy/cytology tumor-response record remains unknown family. Eight outcomes explicitly name iwCLL 2018 (one), Lugano 2014 (one), or RECIST 1.1 (six). No eligible paired named-family conflict was found. The RECIST distribution's malformed stable-disease prose is retained as a source inconsistency; explicit family and literal category labels are not silently repaired.

The oracle copies exact title, description, timeframe, population, source groups, denominators, and classes. JSON pointers identify fields. Supporting literal spans use zero-based Python Unicode character offsets in decoded field strings, not byte offsets in serialized JSON. Category roles distinguish actual class/category labels from definition components; unnamed aggregate categories are not relabeled as if a literal title existed. No Response is not mapped to progressive disease. Missing and zero-denominator Phase II groups remain explicit. Reader/confirmation labels are taken from the same outcome only; sibling statements are not silently inherited.

No pooling, per-patient classification, clinical response reconstruction, ORR recalculation, or efficacy/safety assertion was performed. This is a small LLM source-context evaluation, not independent clinical adjudication or a stable accuracy estimate. The initial oracle and method are frozen by SHA256 before root classifier execution. Any later correction must be a separately named dated amendment, preserving these bytes.
'''
for name,obj in [('oracle.json',oracle)]:
 path=out/name
 assert not path.exists(),'Immutable oracle already exists'
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'review-method.md').write_text(method,encoding='utf-8')
def rec(path): return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
receipt={'schema':'blind-oracle-freeze-receipt/1','frozenUTC':now,'inputs':[rec(src/x) for x in ['AMENDMENT.md','api-response.json','acquisition-receipt.json']],'outputs':[rec(out/x) for x in ['oracle.json','review-method.md','build-oracle.py']],'counts':oracle['counts'],'classifierOutputsRead':False,'classifierExecutedByReviewer':False,'immutablePolicy':'Never overwrite frozen outputs; corrections require append-only separate amendment.'}
(out/'freeze-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':oracle['counts'],'oracleSHA256':rec(out/'oracle.json')['sha256'],'receiptSHA256':rec(out/'freeze-receipt.json')['sha256']}))
