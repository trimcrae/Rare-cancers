"""Offline patient-aware bounded pilot. Stdlib only, no network."""
import json,csv,hashlib,math,collections,statistics
from pathlib import Path
D=Path(__file__).resolve().parent
L=lambda n:json.loads((D/n).read_text())
labels=L('emc_label_records.json'); mut=L('emc_and_nr4a3_mutations.json');cna=L('emc_and_nr4a3_cna.json');sv=L('all_nr4a3_alias_sv.json');cl=L('emc_and_nr4a3_sample_clinical.json');panels=L('gene_panels.json')
selected=('TP53','RB1','CDKN2A','CDKN2B','CDK4','CCND1','MDM2')
samples={r['sampleId']:r['patientId'] for r in labels}
assert len(samples)==len(labels)
clinical={s:{} for s in samples}
for r in cl:
 assert r['sampleId'] in samples and r['patientId']==samples[r['sampleId']]
 clinical[r['sampleId']][r['clinicalAttributeId']]=r['value']
coverage={p['genePanelId']:{g['hugoGeneSymbol'] for g in p['genes']} for p in panels}
mut_gene=lambda r:r['gene']['hugoGeneSymbol']
bygene=collections.defaultdict(set)
for r in mut:
 assert r['patientId']==samples[r['sampleId']]
 bygene[mut_gene(r)].add(r['patientId'])
struct_supported={r['sampleId'] for r in sv if 'NR4A3' in (r.get('eventInfo','')+' '+r.get('annotation','')) or r.get('site1HugoSymbol')=='NR4A3' or r.get('site2HugoSymbol')=='NR4A3'}
endpoint_supported={r['sampleId'] for r in sv if r.get('site1HugoSymbol')=='NR4A3' or r.get('site2HugoSymbol')=='NR4A3'}
records=[]
for s,p in sorted(samples.items()):
 c=clinical[s];panel=c['GENE_PANEL'];mm=[r for r in mut if r['sampleId']==s];cc=[r for r in cna if r['sampleId']==s and abs(r['value'])==2]
 selm=[r for r in mm if mut_gene(r) in selected];selc=[r for r in cc if mut_gene(r) in selected]
 records.append({'sample_id':s,'patient_id':p,'panel':panel,'cell_cycle_all_genes_in_panel':all(g in coverage[panel] for g in selected),'nr4a3_endpoint':s in endpoint_supported,'nr4a3_event_or_endpoint':s in struct_supported,'sample_type':c.get('SAMPLE_TYPE'),'facets_qc':c.get('FACETS_QC'),'wgd':c.get('FACETS_WGD'),'fga':c.get('FRACTION_GENOME_ALTERED'),'facets_purity':c.get('FACETS_PURITY'),'tmb':c.get('TMB_SCORE'),'all_snv_indels':';'.join(mut_gene(r)+':'+r['proteinChange'] for r in mm),'all_highlevel_cna':';'.join(mut_gene(r)+':'+str(r['value']) for r in cc),'selected_cell_cycle_events':';'.join([mut_gene(r)+':'+r['proteinChange'] for r in selm]+[mut_gene(r)+':'+str(r['value']) for r in selc])})
with (D/'all_emc_samples.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
selected_patients=sorted({r['patient_id'] for r in records if r['selected_cell_cycle_events']})
qc=[r for r in records if r['facets_qc']=='Pass']
confirmed_patients={samples[s] for s in struct_supported}
old=L('historical_msk2022_emc_labels.json');oldp={r['patientId'] for r in old};nowp=set(samples.values())
def wilson(k,n):
 z=1.959963984540054;c=(k/n+z*z/(2*n))/(1+z*z/n);h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n);return [c-h,c+h]
result={'decision':'shelve_standalone_paper','new_surviving_disease_finding':None,'samples':len(samples),'patients':len(nowp),'repeat_patients':{p:sorted(s for s in samples if samples[s]==p) for p,n in collections.Counter(samples.values()).items() if n>1},'nr4a3_endpoint_supported_samples':len(endpoint_supported),'nr4a3_event_or_endpoint_supported_samples':len(struct_supported),'nr4a3_event_or_endpoint_supported_patients':len(confirmed_patients),'endpoint_annotation_discordance':sorted(struct_supported-endpoint_supported),'all_mutation_rows':len(mut),'all_gene_mutation_donor_counts':{g:len(ps) for g,ps in sorted(bygene.items())},'selected_genes':selected,'selected_patients':selected_patients,'selected_patient_fraction_descriptive':len(selected_patients)/len(nowp),'selected_patient_wilson95_descriptive':wilson(len(selected_patients),len(nowp)),'selected_genes_panel_coverage_all_samples':all(r['cell_cycle_all_genes_in_panel'] for r in records),'qc_pass_samples':len(qc),'qc_fail_samples':[r['sample_id'] for r in records if r['facets_qc']!='Pass'],'wgd_true_qc_pass_samples':[r['sample_id'] for r in qc if r['wgd']=='TRUE'],'wgd_true_with_nr4a3_release_support':[r['sample_id'] for r in qc if r['wgd']=='TRUE' and r['nr4a3_event_or_endpoint']],'fga_qc_pass_range':[min(float(r['fga']) for r in qc),max(float(r['fga']) for r in qc)],'all_tmb_range':[min(float(r['tmb']) for r in records),max(float(r['tmb']) for r in records)],'historical_msk2022_patients':len(oldp),'overlapping_patients':sorted(oldp&nowp),'current_not_historical_patients':sorted(nowp-oldp),'historical_not_current_patients':sorted(oldp-nowp),'union_release_patients':len(oldp|nowp),'comparison_note':'No independence inferred from new release. No survival or FGA effect test due two cell-cycle donors, no repeated new gene, and only one QC-pass affected donor. Confidence interval is descriptive ascertainment-conditioned, not EMC population prevalence. No new claim advanced.'}
(D/'results.json').write_text(json.dumps(result,indent=2))
inputs=[D/n for n in ('emc_label_records.json','emc_and_nr4a3_mutations.json','emc_and_nr4a3_cna.json','all_nr4a3_alias_sv.json','emc_and_nr4a3_sample_clinical.json','gene_panels.json','historical_msk2022_emc_labels.json')]
manifest={'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (D/'results.json',D/'all_emc_samples.csv')}}
(D/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(result,indent=2))


