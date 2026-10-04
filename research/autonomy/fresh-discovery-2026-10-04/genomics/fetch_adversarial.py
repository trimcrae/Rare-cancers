import json,re
from fetch_pilot import OUT,get,STUDY,receipts
receipts.extend(json.loads((OUT/'retrieval_receipts.json').read_text()))
labels=json.loads((OUT/'emc_label_records.json').read_text());ids=sorted({r['sampleId'] for r in labels})
sv=get('/structural-variant/fetch',{'molecularProfileIds':[STUDY+'_structural_variants']})
terms=re.compile(r'\b(?:NR4A3|CHN|TEC)\b',re.I)
relevant=[r for r in sv if terms.search(' '.join(str(r.get(k,'')) for k in ('site1HugoSymbol','site2HugoSymbol','eventInfo','annotation','comments')))]
(OUT/'all_nr4a3_alias_sv.json').write_text(json.dumps(relevant,indent=2))
print('All SV',len(sv),'alias matched',len(relevant),'new samples',sorted({r['sampleId'] for r in relevant}-set(ids)))
for suffix in ('mutations','gistic'):
 data=get('/molecular-profiles/'+STUDY+'_'+suffix+'/gene-panel-data/fetch',{'sampleIds':ids},'gene_panel_data_'+suffix+'.json')
 print(suffix,sorted({r.get('genePanelId') for r in data}))
panels=get('/gene-panels/fetch?projection=DETAILED',['IMPACT341','IMPACT410','IMPACT468'],'gene_panels.json')
# all labels in historical source, independently mapping overlapping IDs, not merging events
old='sarcoma_mskcc_2022'
oldlabels=get('/studies/'+old+'/clinical-data?attributeId=CANCER_TYPE_DETAILED&clinicalDataType=SAMPLE&projection=SUMMARY&pageSize=100000')
oldemc=[r for r in oldlabels if re.search('extraskeletal.*myxoid|EMCHS',r['value'],re.I)]
(OUT/'historical_msk2022_emc_labels.json').write_text(json.dumps(oldemc,indent=2))
print('Historical EMC',len(oldemc),'overlap samples',len(set(ids)&{r['sampleId'] for r in oldemc}),'overlap patients',len({r['patientId'] for r in labels}&{r['patientId'] for r in oldemc}))
print('Historical unique patients',sorted({r['patientId'] for r in oldemc}-{r['patientId'] for r in labels}))
