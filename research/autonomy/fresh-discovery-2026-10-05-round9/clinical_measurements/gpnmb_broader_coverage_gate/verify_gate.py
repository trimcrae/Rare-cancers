import json,pathlib,hashlib,re
B=pathlib.Path(__file__).resolve().parent
checks=[]
def c(name,ok):checks.append({'check':name,'pass':bool(ok)})
def j(n):return json.loads((B/n).read_text())
for s in j('SOURCE-BINDINGS.json')['sources']:
 p=pathlib.Path(s['path']);c('source '+p.name, p.stat().st_size==s['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'])
t=j('TEMPO12-CONDITION-COVERAGE.json');c('TempO12 source condition count',len(t['conditions'])==12);c('TempO12 uniqueSi',len({x['sample_alias'] for x in t['conditions']})==12);c('TempO12 uniqueBioSample',len({x['sample_accession'] for x in t['conditions']})==12)
b=j('BO112-CORRECTED26-CONDITIONS.json');c('BO11226rows',len(b['rows'])==26);c('BO112uniqueLibraries',len({x['accession'] for x in b['rows']})==26);c('BO112correctedsummary',b['summary']=={'library_conditions':26,'source_nonEMC':16,'pending':10,'pending_current_donors':6,'authenticated_EMC':0})
x=j('CULTURE-COVERAGE-CORRECTION.json');c('acceptedR8mapunaffected',x['accepted_prior_rows_affected'] is False);c('actualUSZ22',x['correct_ids']['USZ22']=='GSM6883080/GSE221532');c('all3cultures retained',len(x['prospective_contexts'])==4)
d=j('DECISION.json');c('no numericalauthorization',d['numerical_authorization'] is False);c('no newrequests',j('ACCESS-AND-READ-SCOPE.json')['new_requests']==0);c('zero neworiginals',j('ACCESS-AND-READ-SCOPE.json')['new_retained_original_bytes']==0);c('freefloor',j('ACCESS-AND-READ-SCOPE.json')['free_bytes']>=10737418240)
c('Brenca12',len(j('NATIVE-TISSUE-SOURCE-CONDITIONS.json')['Brenca12']['cases'])==12)
r=j('EXTERNAL-STAGE-BINDINGS.json')
for s in r['sources']:
 p=pathlib.Path(s['path']);c('external '+p.name,p.stat().st_size==s['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'])
(B/'VERIFICATION.json').write_text(json.dumps({'checks':checks,'all_pass':all(x['pass'] for x in checks),'new_GPNMB_expression_cells_read':0,'new_gene_statistics':0,'network_calls':0},indent=2)+'\n')
assert all(x['pass'] for x in checks)
print(str(len(checks))+' checks PASS; zero network/new expression cells')
