"""All-gene source reuse and all-six-patient Davis table evaluation."""
from pathlib import Path
import json,hashlib,collections
D=Path(__file__).resolve().parent
R=D.parents[1]/'fresh-discovery-2026-10-04'/'genomics'
if not R.exists():R=Path(r'C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04/genomics')
files=['emc_and_nr4a3_mutations.json','emc_and_nr4a3_cna.json','gene_panels.json','gene_panel_data_mutations.json','gene_panel_data_gistic.json','historical_msk2022_emc_mutations.json','historical_msk2022_emc_cna.json']
data={f:json.loads((R/f).read_text())for f in files}
mut=data[files[0]];cna=data[files[1]];genes=['IDH2','ARID1A','NTRK3','TSC2','KDM5C','KMT2C','CD36']
def symbol(r):return r.get('gene',{}).get('hugoGeneSymbol',r.get('hugoGeneSymbol'))
msk={}
for gene in genes:
 panel={p['genePanelId']:any(g['hugoGeneSymbol']==gene for g in p['genes'])for p in data['gene_panels.json']}
 c=[r for r in cna if symbol(r)==gene]
 m=[r for r in mut if symbol(r)==gene]
 msk[gene]={'panel_membership':panel,'mutation_rows':m,'CNA_record_count':len(c),'CNA_sample_ids':sorted({x['sampleId']for x in c}),'CNA_value_counts':dict(collections.Counter(str(x['value'])for x in c)),'nonzero_CNA_rows':[x for x in c if x['value']!=0]}
dt=json.loads((D/'davis-extracted-tables.json').read_text())['tables']
mapping={'MO_1023':[2,3],'MO_1088':[9],'MO_1180':[17,18],'MO_1222':[24],'MO_1381':[32],'MO_1582':[38]}
davis=[]
for patient,indices in mapping.items():
 vals=[]
 for i in indices:
  t=dt[i]['rows'];head=t[0]
  for row in t[1:]:vals.append({'table_index':i,'cells':dict(zip(head,row))})
 genehits={g:[x for x in vals if g in x['cells'].values()]for g in genes}
 davis.append({'patient':patient,'somatic_table_indices':indices,'all_somatic_source_rows':vals,'selected_gene_hits':genehits,'limitations':'Source tables include provisional/VUS calls and MO_1023 technical/specimen replication; no inferred actionability.'})
germline=[{'table_index':t['table_index'],'row_index':i,'cells':dict(zip(t['rows'][0],row))}for t in dt for i,row in enumerate(t['rows'][1:],1)if any(g in row for g in genes)and t['table_index']not in sum(mapping.values(),[])]
out={'date':'2026-10-04','round1_sources':{f:{'relative_location':'../../fresh-discovery-2026-10-04/genomics/'+f,'bytes':(R/f).stat().st_size,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest()}for f in files},'all_MSK_mutation_rows':mut,'MSK_selected_gene_measurements':msk,'historical_MSK_all_mutations':data['historical_msk2022_emc_mutations.json'],'davis_all_six_patients':davis,'davis_other_tables_with_selected_genes':germline,'limits':['GENIE v12/v20 patient-level authentication unavailable; aggregate supplements cannot identify the NTRK fusion or prove overlap.','Current and historical MSK samples are not independent; round1 ID crosswalk remains authoritative.','Missing fusion calls are not diagnostic exclusions.','Davis TSC2W477C occurs in a germline variation table with similar normal/tumor allele fractions, not independent somatic TSC2-loss validation.','MSK RNA/structural assay coverage is not equivalent to coding-gene panel membership.']}
(D/'crosscohort-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'MSK':{g:{'panel_membership':v['panel_membership'],'mutation_rows':len(v['mutation_rows']),'CNA_records':v['CNA_record_count'],'CNA_values':v['CNA_value_counts']}for g,v in msk.items()},'Davis':[{'patient':x['patient'],'somatic_rows':len(x['all_somatic_source_rows']),'gene_hit_counts':{g:len(q)for g,q in x['selected_gene_hits'].items()}}for x in davis],'Davis_other_table_hits':germline},indent=2))
