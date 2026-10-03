import json,hashlib,datetime,collections
from pathlib import Path
p=Path('C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint05-foundation'); out=p.parent/'checkpoint05-foundation-review'
load=lambda n:json.loads((p/n).read_text(encoding='utf-8-sig'))
ann=load('annotation.json'); prim=load('primary-check.json'); policy=load('frozen-policy.json'); receipt=load('receipt.json')
checks=[]; issues=[]
def ck(name,value):
 checks.append({'check':name,'passed':bool(value)})
 if not value: issues.append(name)
ck('annotation policy SHA',ann['policy_sha256']==hashlib.sha256((p/'frozen-policy.json').read_bytes()).hexdigest())
ck('exact event order',[x['REordinal'] for x in ann['events']]==policy['event_ordinals'])
ck('events copied exactly with only slot classification added',[{k:v for k,v in x.items() if k!='slot_classifications'} for x in ann['events']]==prim['literal_gene_pair_differences'])
ck('exact unique pair order',[[x['source'],x['export']] for x in ann['unique_pairs']]==policy['unique_changed_pairs'])
pair_results=[]
for a in ann['unique_pairs']:
 raw=load('raw/'+a['export']+'.json');docs=raw['response']['docs'];ck(a['export']+' unique approved exact target',len(docs)==1 and docs[0]['symbol']==a['export'] and docs[0]['status']=='Approved')
 r=docs[0]
 ck(a['export']+' selected annotation fields equal raw',all(r.get(k)==v for k,v in a['current_records'][0].items()))
 prev=a['source'] in r.get('prev_symbol',[])
 actual='current_HGNC_prev_symbol' if prev else ('unresolved_numeric_source_cell' if a['source'] in ['44621.0','44812.0'] else 'unresolved_no_exact_symbol_evidence')
 ck(a['source']+' classification matches exact raw evidence',actual==a['classification'])
 pair_results.append({'source':a['source'],'export':a['export'],'hgnc_id':r['hgnc_id'],'source_exact_prev_symbol':prev,'prev_symbol':r.get('prev_symbol'),'classification':actual})
ak=load('raw/AKAP2.json')['response']['docs'][0]; palm=load('raw/PALM2AKAP2.json')['response']['docs'][0]
ck('AKAP2 followup annotation fields equal raw',all(ak.get(k)==v for k,v in ann['exact_source_followup']['records'][0].items()))
ck('distinct current approved HGNC identities',ak['status']==palm['status']=='Approved' and ak['hgnc_id']!=palm['hgnc_id'])
ck('AKAP2 not exact target symbol previous or alias','AKAP2' not in [palm['symbol']]+palm.get('prev_symbol',[])+palm.get('alias_symbol',[]))
classes=collections.Counter(c for ev in ann['events'] for c in ev['slot_classifications'])
supported=[e['REordinal'] for e in ann['events'] if all(c in ['unchanged','missing_token_equivalent','current_HGNC_prev_symbol'] for c in e['slot_classifications'])]
ck('12 fully supported events',len(supported)==12)
ck('13 supported changed slots',classes['current_HGNC_prev_symbol']==13)
ck('9 unique previous-symbol pairs',sum(x['source_exact_prev_symbol'] for x in pair_results)==9)
lookup={(a['source'],a['export']):a['classification'] for a in ann['unique_pairs']}
for ev in ann['events']:
 expected=['unchanged' if a==b else 'missing_token_equivalent' if a=='' and b=='N/A' else lookup[a,b] for a,b in zip(ev['sourceGenePair'],ev['exportGenePairLiteral'])]
 ck(str(ev['REordinal'])+' exact slot order classification',expected==ev['slot_classifications'])
# Validate saved bytes referenced by original receipt; mutable probe script is intentionally outside this read scope.
for name,r in receipt['files'].items():
 if name.endswith('.py'): continue
 ck('receipt '+name,hashlib.sha256((p/name).read_bytes()).hexdigest()==r['sha256'] and (p/name).stat().st_size==r['bytes'])
retr=load('retrieval-receipts.json')+[load('source-followup-receipt.json')]
for r in retr:
 name='_info' if r['url'].endswith('/info') else r['url'].rsplit('/',1)[1]
 rawpath=p/'raw'/f'{name}.json'
 ck('retrieval '+name,r['status']==200 and hashlib.sha256(rawpath.read_bytes()).hexdigest()==r['sha256'] and rawpath.stat().st_size==r['bytes'])
report={'schema':'foundation-independent-saved-source-review/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed_with_limits' if not issues else 'issues_found','checks':checks,'issues':issues,'pairEvidence':pair_results,'counts':{'events':len(ann['events']),'uniquePairs':len(pair_results),'supportedEvents':len(supported),'supportedChangedSlots':classes['current_HGNC_prev_symbol'],'uniqueSupportedPairs':sum(x['source_exact_prev_symbol'] for x in pair_results),'slotClassifications':dict(classes)},'AKAP2Caveat':{'hgnc_id':ak['hgnc_id'],'locus_type':ak['locus_type'],'target_hgnc_id':palm['hgnc_id'],'target_locus_type':palm['locus_type'],'meaning':'Distinct current records and no exact synonym support; not proof of unrelated genes or of the intended source alteration.'},'limits':['No new network query, workbook read, source-era HGNC recovery, or gene/date interpretation.','Primary workbook extraction claims accepted only as supplied receipt; this review independently validates companion consistency with that receipt, not workbook contents.','June 2022 article publication date is asserted in findings but was not independently verified from permitted inputs. Current symbol-change dates themselves match raw records.','Probe result not provided at review; no interpretation of numeric cell format/type performed.','No export file was read or written; unchanged export hashes are reported by primary receipt, not independently rehashed here.']}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
text='''---
id: DOC-CHECKPOINT05-FOUNDATION-INDEPENDENT-SOURCE-REVIEW
title: Independent saved-response review of Foundation gene nomenclature companion
kind: memo
status: complete
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Validate exact current HGNC evidence and event/slot bookkeeping.
scope: Frozen fifteen-event annotation and saved HGNC responses only.
audience: [maintainers, reviewers]
---

The companion passes the bounded saved-source checks. All nine supported source-to-export pairs occur verbatim in the respective approved target record's prev_symbol array. They support 12 events and 13 changed gene slots; event 871 changes both slots. Fifteen events contain 30 slots: 13 previous-symbol supported, 9 unchanged, 5 missing-token convention, 2 unresolved numeric, and 1 unresolved exact-symbol conflict. Exact event order, worksheet rows, source IDs, ordered pairs, classifications, and selected HGNC fields match the supplied primary-check receipt and raw responses. No alias or fuzzy match is needed.

AKAP2 (HGNC:372) and PALM2AKAP2 (HGNC:33529) are distinct Approved current records, and AKAP2 is not an exact symbol/prev_symbol/alias_symbol match in the target record. Preserve the distinction without claiming unrelated biology: the raw AKAP2 locus_type is complex locus constituent, while the target is gene with protein product named PALM2 and AKAP2 fusion. Their shared accession/name context is not exact synonym evidence and does not identify the intended alteration. The existing cautious unresolved classification is appropriate.

The numeric strings 44621.0 and 44812.0 remain unresolved. MARCH1 and SEPT8 in target prev_symbol fields do not establish the numeric cells' intended genes. The new cell-format probe result was not available to this review; no date or source-encoding interpretation is made here.

Current support does not establish source-era nomenclature or validate any rearrangement. Raw symbol-change dates for C22orf46P and BMAL1 agree with the annotation. The findings' June 2022 article date was not independently verified within these permitted inputs; treat its comparison as conditional on the existing primary citation. No inference about intended genes, diagnosis, biological function, or experimental validation follows.

This review checked all saved raw/annotation hashes against the companion and retrieval receipts, excluding executable scripts being updated separately by root. It independently recomputed exact membership and event/slot classifications without calling the companion classifier. It did not reread the XLS or exports, so their preservation and primary extraction results remain receipt-based limits rather than fresh independent workbook/export validation. No input files were modified and no network, UI, runtime, checkout, or publication action occurred.
'''
(out/'review.md').write_text(text,encoding='utf-8')
inputs=[p/n for n in ['frozen-policy.json','primary-check.json','annotation.json','findings.md','receipt.json','retrieval-receipts.json','source-followup-receipt.json']]+sorted((p/'raw').glob('*.json'))
def rec(x):return {'path':str(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()}
r={'utc':report['utc'],'inputs':[rec(x) for x in inputs],'outputs':[rec(out/x) for x in ['review.json','review.md','review_saved.py']]}
(out/'review-receipt.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checkCount':len(checks),'issues':issues,'counts':report['counts'],'reportSHA256':rec(out/'review.json')['sha256']}))
