import json,pathlib,hashlib,re,datetime
P=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
SOURCES={
'bangerter40':ROOT/'fresh-discovery-2026-10-04/functional/reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json',
'iwata221_24':ROOT/'fresh-discovery-2026-10-04/functional/reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json',
'functional_coverage':ROOT/'fresh-discovery-2026-10-04/functional/COVERAGE.txt',
'r8_model_context':ROOT/'fresh-discovery-2026-10-05-round8/surface_targets/MODEL-CONTEXT.json',
'bangerter_primary_receipt':ROOT/'fresh-discovery-2026-10-04-round2/regulatory/bangerter2022-mtor-eligibility.json'}
def dump(n,v): (P/n).write_text(json.dumps(v,indent=2)+'\n')
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
b=json.loads(SOURCES['bangerter40'].read_text()); iw=json.loads(SOURCES['iwata221_24'].read_text())
# Explicit outcome-field exclusion. Reading only identities, chemistry identifiers, method labels and source receipts.
br=[{k:r.get(k) for k in ('source_model','source_figure','source_panel','panel_row','literal_figure_drug','source_CAS','chemical_identity_verified')} for r in b['rows']]
ir=[[{k:r.get(k) for k in ('source_row','sheet','drug','cas')} for r in t['records']] for t in iw['tables']]
mask={'bangerter40':br,'iwata221':ir[0],'iwata24_IC50_names_only':ir[1]}
dump('ALL-CANONICAL-COMPOUND-NAMES.json',{'scope':'All40+221+24 source rows projected with no ordinal/viability/SD/IC50 fields. Rows are conditions, not donors.','data':mask})
al=json.loads((P/'ALIAS-AUDIT-FROZEN.json').read_text())
audit=[]
for fam,aliases in al['finite_alias_sets'].items():
 matches={}
 for title,rows in mask.items():
  rr=[]
  for r in rows:
   drug=r.get('literal_figure_drug',r.get('drug',''))
   tokens=[a for a in aliases if norm(a) in norm(drug)]
   if tokens:rr.append({'source_row':r.get('source_row'), 'panel':r.get('source_panel'),'panel_row':r.get('panel_row'),'drug':drug,'cas':r.get('cas',r.get('source_CAS')),'matched_aliases':tokens})
  matches[title]=rr
 audit.append({'candidate_family_for_source_gate_only':fam,'matches':matches})
dump('ALIAS-AUDIT-RESULTS.json',{'scope':'Finite known direct-family name/alias audit, not complete pharmacology universe or chemical-binding proof; incidental downstream/offtarget BCL2 effects do not create selective comparators.','families':audit,'numerical_stage':False})
vc=b['validation_context']; vcm={k:vc[k] for k in ('selected_drugs','models','source','format','exposure','no_80_row_matrix') if k in vc}
dump('ASSAY-AND-MODEL-CONTEXT.json',{'canonical_screen_models':{'Bangerter40':'USZ20-EMC1','Iwata221_and24':'NCC-EMC1-C1'},'Bangerter_screen':b['screen_context'],'Bangerter_selected_validation_method_only':vcm,'Iwata_method_qualification':iw['updated_source_qualification'],'Iwata_source_files':[t['source'] for t in iw['tables']],'limits':['Bangerter selected validation includes USZ22-EMC2, not another40-row screen; selected published validation is prior art.','USZ20/USZ22 different male/female donors per verified primary coverage, USZ22 reused later; USZ23 donor crosswalk unknown.','NCC one donor/passages and screen rows not new patients; no pooled potency/statistical independence.','NCC full primary screening methods/raw replicates not acquired in reused source gate; nominal screening concentration/duration cannot be inferred from IC50 nM header.','Bangerter ordinal source categories are not comparable continuous IC50/AUC values; no outcome/category read here.','NCC24 IC50 is a selected subset without venetoclax and cannot supply its missing dose response.']})
dump('REUSED-SOURCE-HASHES.json',{'sources':[{'key':k,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'access':'read-only reused existing file; no source retrieval'} for k,p in SOURCES.items()],'new_raw_bytes':0,'inspection':'Fixed name/CAS/model/method/source receipt projection only. Entire JSON parsed but no new numerical outcome field selected or displayed; this is not full-team blindness.'})
checks={}
checks['all40']=len(br)==40; checks['all221']=len(ir[0])==221;checks['all24']=len(ir[1])==24
checks['screen_model']=b['screen_context']['model']=='USZ20-EMC1';checks['NCC_model']=iw['model']=='NCC-EMC1-C1'
checks['USZ_only_one_venetoclax']=sum(norm('Venetoclax') in norm(r['literal_figure_drug']) for r in br)==1
vv=[r for r in ir[0] if norm('Venetoclax') in norm(r['drug'])];checks['NCC_source_row_CAS']=len(vv)==1 and vv[0]['source_row']==217 and vv[0]['cas']=='1257044-40-8'
checks['no_venetoclax_IC50']=not any(norm('Venetoclax') in norm(r['drug']) for r in ir[1])
checks['no_other_fixed_family_name_match']=all(not any(f['matches'][label] for label in mask) for f in audit if f['candidate_family_for_source_gate_only']!='BCL2_selective_candidates')
for title,rows in mask.items():
 checks[title+'_no_outcome_fields']=not any(set(r)&{'ordinal_source_category','viability_percent','sd_percentage_points','ic50_nM'} for r in rows)
assert all(checks.values()),checks
dump('VERIFICATION.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'pass':all(checks.values()),'numerical_outcome_fields_selected':0,'new_network_requests':0})
print(json.dumps({'checks':len(checks),'pass':all(checks.values()),'new_outcome_fields':0,'new_raw_bytes':0}))
