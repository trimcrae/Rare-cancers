from pathlib import Path
import json,hashlib,re,statistics,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
R=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04/functional')
A=Path('C:/Projects/EMC-Research/.cache/aso-full-20260926-temp/claim-ablation-b40dd3oo/research/autonomy/zullow-emc-source-2026-09-06')
# New valid Table S1: all EMC rows, no outcome/gene association tests.
z=json.loads((P/'zullow-tableS1-evaluation.json').read_text());rows=[]
for sh,rr in z['sheets'].items():
 for r in rr:
  if any(re.fullmatch(r'EMC\d+',str(v or '')) for v in r['values']):rows.append({'sheet':sh,**r})
assert len(rows)==11
vals=[r['values'] for r in rows]
summary={'count':11,'IDs':[r[0] for r in vals], 'purity_percent':[int(re.search(r'\d+',str(r[2])).group()) for r in vals], 'tumor_status':[r[8] for r in vals], 'pretreatment_codes':[r[9] for r in vals]}
summary['purity_median']=statistics.median(summary['purity_percent']);summary['pretreatment_nonzero']=sum(v!=0 for v in summary['pretreatment_codes'])
summary['decision']='Metadata eligibility only: article seven RNAs cannot be assigned to11 specimen rows; no fusion/sequence crosswalk. No biological result, no implied independence or batch resolution.'
meta=json.loads((A/'sample-metadata.json').read_text());assert len(meta)==138
reuse={'files':{n:hashlib.sha256((A/n).read_bytes()).hexdigest() for n in ['README.md','sample-metadata.json','GSE179720_family.soft.gz','PRJNA744758-runs.tsv','primary-RNA-crosswalk.tsv','McBride2018.html','SRP052896-runs.tsv']},'records':len(meta),'full_metadata_term_hits':{t:sum(t.lower() in json.dumps(r).lower() for r in meta) for t in ['chondrosarcoma','NR4A3']},'scope':'Verified reused metadata/source-chain evaluation, not RNA values. Newly recoveredTableS1 adds11 EMC specimen labels; existing deposit remains without a linked seven-EMC expression asset.'}
(P/'zullow-eligibility-summary.json').write_text(json.dumps({'new_summary':summary,'all11rows':rows,'verified_prior_evaluation':reuse},indent=2),encoding='utf-8')
# Parse all study cases before classifying molecularly confirmedEMC and ambiguous clustering.
x=E.parse(P/'myoepithelial2025.xml');allrows=[]
for tw in x.iter('table-wrap'):
 if tw.attrib.get('id')=='Tab1':
  for tr in tw.iter('tr'):
   c=[' '.join(v.itertext()).strip() for v in tr if v.tag in ['td','th']]
   if c and re.match(r'^Case \d+(?: [ab])?$' ,c[0]):allrows.append(c)
assert len(allrows)==30
emccandidates=[r for r in allrows if any('EMCS' in v or 'NR4A3' in v for v in r)]
assert {re.match(r'Case \d+',r[0]).group() for r in emccandidates}=={'Case 19','Case 21','Case 30'}
(P/'myoepithelial2025-allcase-eligibility.json').write_text(json.dumps({'doi':'10.1007/s00428-024-03977-4','source_sha256':hashlib.sha256((P/'myoepithelial2025.xml').read_bytes()).hexdigest(),'all30rows':allrows,'candidates':emccandidates,'confirmed_EMC':['Case 21'],'ambiguous_not_counted_as_EMC':['Case 19','Case 30'],'decision':'Case21 TAF15::NR4A3 plus concordant methylation is previously published reclassification;19/30 are hierarchical-clustering neighbors with independent tSNE group/RNAnegative and cannot be counted as EMC. No new disease inference. New study array deposit not recovered; GSE140686 reused reference not independent cohort.'},indent=2),encoding='utf-8')
# All literal compound labels across each published screen; only2 rapalogs found.
b=json.loads((R/'reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json').read_text())
i=json.loads((R/'reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json').read_text())
m=json.loads((R/'mendeley-analysis.json').read_text())
terms=['rapamycin','everolimus','temsirolimus','ridaforolimus','sirolimus','mtor','azd8055','azd2014','ink128','torin','pp242','bez235','gdc0980','dactolisib','apitolisib','sapanisertib','vistusertib']
def hit(n):return any(t in n.lower().replace('-','') for t in terms)
irc=i['tables'][0]['records'];ic=i['tables'][1]['records'];assert len(irc)==221 and len(ic)==24
selected=[r for r in irc if hit(r['drug'])]
assert len(selected)==2
out={'scope':'Frozen MTOR-PLAN; no cross-assay pooling, no genotype-response claim.','source_hashes':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json','reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json','mendeley-analysis.json','reused-authentic-EMC-two-model-genotype-supplements.json']},'Bangerter':{'labels':[r['literal_figure_drug'] for r in b['rows']],'screen_model':'USZ20-EMC1;40 labels','eligible_mTOR':[],'USZ22':'Validated carfilzomib/doxorubicin/venetoclax and combinations; no mTOR compound. TSC2 not reported in mutation-onlytable; not WT proof.'},'Iwata':{'all221labels':[r['drug'] for r in irc],'eligible_rows':selected,'IC50_mTOR_rows':[r for r in ic if hit(r['drug'])],'interpretation':'Two published mean/SD values show no reduction vs source normalized control under unspecified recovered screening conditions. Do not infer proliferation, generalized resistance, clinical response, orTSC2 dependence. No TSC2 genotype reported in inspected model materials. One donor, culturetechnical replicates not independent patients.','methods_gap':i['updated_source_qualification']},'Mendeley2025':{'unique_drug_labels':sorted(set(r['drug'] for r in m['curves'])),'eligible_mTOR':[],'scope':'USZ23 source8drug curves are DDR drugs; no mTOR assay. Finalversion/otherconditions gap retained fromround1.'},'decision':'No authentic TSC2-altered model paired with mTOR pharmacology identified. This cannot corroborate or refute FoundationTSC2 functional importance. Do not advance sensitivity/resistance claim.','clinical_gaps':['Merimsky2008 DOI10.1097/CAD.0b013e328312c0e5 abstract reports combinationresponse inmyxoidchondrosarcoma; fullspecimenidentity/site/fusiongenotype/outcome details unavailable, notauthenticatedEMC.','Quek2011 DOI10.1158/1078-0432.CCR-10-2621 publisherindexedtext includesmyxoidchondrosarcoma amongsome shrinkage; exact count/site/fusion/individualoutcome unavailable403; mixedcombination cannotestablishmTORcausality.','IND206 DOI10.1200/jco.2015.33.15_suppl.2594 reportsoneEMCresponse specificallysunitinib; noEMCtemsirolimusdenominatororindividualoutcome disclosedinabstract. NCT01396408 hasResultsfalse at2026-10-04.','Broadtemsirolimus/cixutumumab2013 includeschondrosarcoma aggregate, subtypeidentity unverified; not assumedEMC. Fulltext retrieval failed. BroadmTOR clinicaloutcomes remain pending/unavailable as distinct from model question.']}
(P/'mtor-model-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
# Explicit rejected retrievals; filenames are not identity proof.
(P/'retrieval-identity-corrections.json').write_text(json.dumps({'NCC-EMC1-C1-cellosaurus.txt':'Wrong guessedaccessionCVCL_E2B4 returns HAP1LIG4 knockout. This is not NCC or EMC, never used as evidence. Retained solely as retrievalfailure receipt.','merimsky2008.html':'Guessed issueURL redirects to unrelated antiDTIgGarticle DOI10.1097/cad.0b013e328310894f. Not Merimsky source; DOI followup403. Do not use returned HTML as EMC evidence.','zullow_table_source_doi':'Draftscript initially.03.007 erroneous; corrected to exactprimary.03.019 and regeneratedbeforefinalization.','clinical_challenge':'Ogura file name full led premature methodsavailabilityinference; worker corrected, receipt regeneratedwithtime-origingap. No numericchanges.'},indent=2),encoding='utf-8')
print(json.dumps({'zullow':summary,'myoepithelial_EMC_candidates':emccandidates,'mTORrows':selected},ensure_ascii=True))

