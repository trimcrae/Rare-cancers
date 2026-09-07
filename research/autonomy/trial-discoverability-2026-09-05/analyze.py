"""Offline deterministic audit tables, source pointers, and reviewer packet."""
import re
import retrieve as r
q=r.load_queries(); selection=r.read(r.ROOT/'selection.json')
union={n:s for _,ss in q.values() for n,s in ss.items()}
parent=set(q['parent_sarcoma'][1])|set(q['parent_eligibility_sarcoma'][1])
current={'RECRUITING','NOT_YET_RECRUITING','ENROLLING_BY_INVITATION'}
def normal(s):return ' '.join(re.sub(r'[^a-z0-9 ]',' ',s.lower()).replace('extra skeletal','extraskeletal').split())
result={'queries':{k:{'count':len(ss),'pages':len(m['pages']),'manifest':'sources/'+k+'/manifest.json'} for k,(m,ss) in q.items()},'parent_union_count':len(parent),'corpus_union_count':len(union),'comparisons':{},'anchors':{}}
candidates=set(selection['historical_anchors'])
for d in selection['diagnoses']:
 k=d['id']; c=set(q[k+'_condition'][1]);b=set(q[k+'_ordinary'][1]);e=set(q[k+'_eligibility_ordinary'][1]);o=b|e;m=set(q[k+'_molecular'][1])|set(q[k+'_eligibility_molecular'][1]);extra=m-o
 literal={n for n,s in union.items() if any(' '+normal(term)+' ' in ' '+normal(' '.join(s['protocolSection'].get('conditionsModule',{}).get('conditions',[])))+' ' for term in d['synonyms'])}
 result['comparisons'][k]={'condition_api_count':len(c),'literal_conditions_in_bounded_corpus_count':len(literal),'basic_ordinary_count':len(b),'eligibility_ordinary_count':len(e),'ordinary_union_count':len(o),'molecular_union_count':len(m),'molecular_only_ids':sorted(extra),'molecular_only_current_ids':sorted(n for n in extra if union[n]['protocolSection']['statusModule']['overallStatus'] in current),'molecular_only_outside_parent_ids':sorted(extra-parent)}
 candidates|=extra
 for n in selection['historical_anchors']:
  result['anchors'].setdefault(n,{})[k]={'condition_api':n in c,'literal_condition_phrase':n in literal,'basic_ordinary':n in b,'eligibility_ordinary':n in e,'ordinary_union':n in o,'molecular_union':n in m,'parent_union':n in parent}
r.save(r.ROOT/'corrected-comparison.json',result)
pointer_index={}
for k,(manifest,ss) in q.items():
 for page in manifest['pages']:
  for i,record in enumerate(r.read(r.ROOT/page['file']).get('studies',[])):
   n=record['protocolSection']['identificationModule']['nctId']
   if n in candidates:
    pointer_index.setdefault(n,[]).append({'query_id':k,'file':page['file'],'sha256':page['sha256'],'json_pointer':f'/studies/{i}/protocolSection/eligibilityModule/eligibilityCriteria'})
packet=[]
for n in sorted(candidates):
 s=union[n];ps=s['protocolSection']; sources=[]
 sources=pointer_index[n]
 packet.append({'nct_id':n,'url':'https://clinicaltrials.gov/study/'+n,'title':ps['identificationModule']['briefTitle'],'status':ps['statusModule']['overallStatus'],'last_update':ps['statusModule'].get('lastUpdatePostDateStruct'),'study_type':ps.get('designModule',{}).get('studyType'),'conditions':ps.get('conditionsModule',{}).get('conditions',[]),'eligibility':ps.get('eligibilityModule',{}).get('eligibilityCriteria',''),'source_pointers':sources,'molecular_only_for':[k for k,v in result['comparisons'].items() if n in v['molecular_only_ids']]})
r.save(r.ROOT/'review-packet.json',packet)
print({k:{a:len(b) if isinstance(b,list) else b for a,b in v.items()} for k,v in result['comparisons'].items()})
print('parent union',len(parent),'all union',len(union),'review records',len(packet))
sens={'scope':'Sensitivity strengthens ordinary baseline; initial results above retained','diagnoses':{}}
for d in selection['diagnoses']:
 k=d['id']; initial=set(q[k+'_ordinary'][1])|set(q[k+'_eligibility_ordinary'][1]); strong=initial|set(q[k+'_unquoted_ordinary'][1])|set(q[k+'_unquoted_eligibility'][1]);m=set(q[k+'_molecular'][1])|set(q[k+'_eligibility_molecular'][1]);extra=m-strong
 sens['diagnoses'][k]={'ordinary_strong_count':len(strong),'molecular_only_ids':sorted(extra),'current_molecular_only_ids':sorted(n for n in extra if union[n]['protocolSection']['statusModule']['overallStatus'] in current),'removed_by_unquoted_ids':sorted((m-initial)-extra),'outside_parent_ids':sorted(extra-parent),'all_strong_ordinary_ids':sorted(strong),'all_molecular_ids':sorted(m)}
sens['anchor_membership']={n:{k:n in v['all_strong_ordinary_ids'] for k,v in sens['diagnoses'].items()} for n in selection['historical_anchors']}
r.save(r.ROOT/'sensitivity-results.json',sens)
print('sensitivity', {k:{a:len(b) if isinstance(b,list) else b for a,b in v.items()} for k,v in sens['diagnoses'].items()})
