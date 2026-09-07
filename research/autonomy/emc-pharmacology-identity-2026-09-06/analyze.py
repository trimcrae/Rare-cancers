"""Deterministic within-screen descriptive ranks; no drug discovery or uncertainty inference."""
import bisect,collections,csv,hashlib,html,json,pathlib,re
P=pathlib.Path(__file__).parent; S=P.parent/'ncc-screen-source-2026-09-06'
def dump(name,x):(P/name).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def midranks(values):
 ordered=sorted(enumerate(values),key=lambda x:x[1]);out=[None]*len(values);i=0
 while i<len(ordered):
  j=i+1
  while j<len(ordered) and ordered[j][1]==ordered[i][1]:j+=1
  for k in range(i,j):out[ordered[k][0]]=(i+1+j)/2
  i=j
 return out
freeze=json.loads((P/'analysis-freeze.json').read_text())
for path,digest in freeze['files'].items():assert hashlib.sha256((P.parent/path).read_bytes()).hexdigest()==digest,path
rows=list(csv.DictReader((S/'screen.csv').open(encoding='utf-8-sig')));annotations=json.loads((P/'identity-roster.json').read_text());ann={r['cas']:r for r in annotations}
assert len(rows)==len(ann)==221 and len({r['cas'] for r in rows})==221
ic=list(csv.DictReader((S/'ic50.csv').open(encoding='utf-8-sig')));assert len(ic)==24;icmap={r['cas']:r for r in ic};assert set(icmap)<=set(ann)
means=[float(r['cell_viability_percent']) for r in rows];stress=[float(r['cell_viability_percent'])+float(r['reported_sd_percent']) for r in rows]
rank=midranks(means);srank=midranks(stress)
# Independent rank identity: count observations strictly below, then half the tie size.
for values,rr in [(means,rank),(stress,srank)]:
 for x,r in zip(values,rr):assert r==1+sum(v<x for v in values)+(sum(v==x for v in values)-1)/2
assert midranks([2,1,2,0])==[3.5,2,3.5,1]
for r,mrk,srk,sv in zip(rows,rank,srank,stress):
 r.update(mean_midrank=mrk,mean_plus_sd=sv,mean_plus_sd_midrank=srk,rank_denominator=221,role=ann[r['cas']]['role'],active_moiety=ann[r['cas']]['active_moiety'],chemical_family=ann[r['cas']]['chemical_family'],reported_ic50_nM=icmap.get(r['cas'],{}).get('ic50_nM'),ic50_source_name=icmap.get(r['cas'],{}).get('source_name'))
with (P/'ranked-screen.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Preserve the original complete response tables byte for byte for reviewers.
(P/'source-screen.csv').write_bytes((S/'screen.csv').read_bytes());(P/'source-ic50.csv').write_bytes((S/'ic50.csv').read_bytes())
confirmed=[r for r in rows if r['role'].startswith('confirmed_proteasome')];unknown=[r for r in rows if r['role'].startswith('unresolved_proteasome')];candidates=confirmed+unknown
cutoff=221/4
moieties=[]
for name in sorted({r['active_moiety'] for r in confirmed}):
 members=[r for r in confirmed if r['active_moiety']==name]
 moieties.append(dict(active_moiety=name,preparations=[r['cas'] for r in members],worst_mean_rank=max(r['mean_midrank'] for r in members),worst_stress_rank=max(r['mean_plus_sd_midrank'] for r in members),all_preparations_lowest_quartile=all(r['mean_midrank']<=cutoff for r in members)))
families=[]
for name in sorted({r['chemical_family'] for r in confirmed}):
 members=[r for r in confirmed if r['chemical_family']==name];remaining=[r for r in confirmed if r['chemical_family']!=name]
 families.append(dict(chemical_family=name,cas=[r['cas'] for r in members],active_moieties=sorted({r['active_moiety'] for r in members}),worst_rank=max(r['mean_midrank'] for r in members),leave_family_out_remaining_moieties=sorted({r['active_moiety'] for r in remaining}),leave_family_out_remaining_low_quartile=sum(r['mean_midrank']<=cutoff for r in remaining)))
checks=dict(all_confirmed_moiety_worst_ranks_in_lowest_quartile=all(r['all_preparations_lowest_quartile'] for r in moieties),at_least_two_confirmed_chemical_families=len(families)>=2,no_unresolved_candidate_identity_affecting_complete_membership=not unknown,leave_each_family_out_retains_lowest_quartile_observation=all(f['leave_family_out_remaining_low_quartile']>0 for f in families))
result=dict(denominator_preparations=221,biological_models=1,reported_followup_ic50_entries=24,confirmed_proteasome_preparations=len(confirmed),confirmed_active_moieties=len(moieties),confirmed_chemical_families=len(families),unresolved_candidates=len(unknown),quartile_midrank_cutoff=cutoff,proteasome_candidates=candidates,active_moieties=moieties,chemical_families=families,stop_rule_checks=checks,descriptive_complete_family_claim_supported=all(checks.values()),stop_reason='Unresolved exact identity for CAS1201902-80-8 prevents a complete identity-resolved class claim; known-subset low-rank consistency remains observable.',sensitivity=dict(assign_ambiguous_entry_to_ixazomib_all_lowest_quartile=all(r['mean_midrank']<=cutoff for r in candidates),keep_ambiguous_entry_separate_all_lowest_quartile=all(r['mean_midrank']<=cutoff for r in candidates),confirmed_mean_plus_sd_all_lowest_quartile=all(r['mean_plus_sd_midrank']<=cutoff for r in confirmed),all_named_candidates_mean_plus_sd_lowest_quartile=all(r['mean_plus_sd_midrank']<=cutoff for r in candidates)),followup=dict(candidate_cas_present=[r['cas'] for r in candidates if r['cas'] in icmap],candidate_cas_absent=[r['cas'] for r in candidates if r['cas'] not in icmap],note='Selected follow-up table; not independent validation. Names retained next to CAS to expose the MLN9708/Ixazomib mismatch.'),rows_outside_zero_to_100=sum(m<0 or m>100 for m in means),limits=['NCC assay exposure and replicate definition unknown','SD stress is not a confidence bound','No biological replicate, target engagement, selectivity or clinical efficacy inference','No quantitative Zurich comparison','Retrospective selected-family description; no novel target discovery claim'])
dump('result.json',result)
# Regulatory excerpts are short and checked verbatim after HTML tag removal/whitespace normalization.
quotes=[('velcade.html','Bortezomib is a modified dipeptidyl boronic acid.'),('kyprolis.html','Carfilzomib is a tetrapeptide epoxyketone proteasome inhibitor'),('ninlaro.html','Ixazomib citrate, a prodrug, rapidly hydrolyzes under physiological conditions to its biologically active form, ixazomib.')]
qc=[]
for name,q in quotes:
 txt=html.unescape(re.sub('<[^>]+>',' ',(P/'sources'/name).read_text(encoding='utf-8')));txt=' '.join(txt.split());assert q in txt,(name,q);qc.append(dict(source=name,quote=q,locator='Description or Mechanism of action',verified=True))
dump('source-quote-checks.json',qc)
# Identity structure contrast is computed from archived authoritative registry responses.
a=json.loads((P/'sources/pubchem-56844015.json').read_text())['PropertyTable']['Properties'][0];b=json.loads((P/'sources/pubchem-49867936.json').read_text())['PropertyTable']['Properties'][0]
assert a['InChIKey'].split('-')[0]!=b['InChIKey'].split('-')[0]
dump('checks.json',dict(all_221_rows_retained=True,all_24_ic50_rows_retained=True,original_response_csv_bytes_identical=True,independent_midrank_identity=True,midrank_tie_fixture=True,all_frozen_input_hashes_match=True,all_3_regulatory_quotes_match=True,distinct_registry_connectivity_blocks=[a['InChIKey'],b['InChIKey']],scope='Arithmetic and source integrity only; no independent scientific reviewer'))
print(json.dumps({k:result[k] for k in ['confirmed_proteasome_preparations','confirmed_active_moieties','confirmed_chemical_families','stop_rule_checks','sensitivity','rows_outside_zero_to_100']},indent=2));print('\n'.join(f"{r['cas']} {r['source_name']}: mean rank {r['mean_midrank']}, stress rank {r['mean_plus_sd_midrank']}, IC50 {r['reported_ic50_nM']}" for r in candidates))
