import json
from pathlib import Path
P=Path(__file__).resolve().parent
src=json.loads((P/'ev5-sheets.json').read_text())
out=[]
for filename,sheets in src.items():
    if not any('FigEV5'+x in filename for x in 'EFG'):continue
    for sheet,rows in sheets.items():
        for i,row in enumerate(rows):
            if not row or not isinstance(row[0],str) or not row[0].startswith('AUC '):continue
            models=[]
            for col,model in enumerate(row[1:12],1):
                models.append({'model':model,'source_total_area':rows[i+1][col],'source_SE':rows[i+2][col],'source_CI':rows[i+3][col]})
            emc=next(x for x in models if x['model']=='USZ-22_EMC2')
            out.append({'source':filename,'sheet':sheet,'condition':row[0],'models':models,'EMC_models_with_lower_area':sum(x['source_total_area']<emc['source_total_area'] for x in models),'caution':'Source-derived AUC summaries of the same curves; source SE/CI are not patient-population uncertainty, no new independent experiment. Integration domains differ by drug; no cross-drug AUC ranking.'})
assert len(out)==9
(P/'ev5-auc-evaluation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps([{'condition':x['condition'],'EMC':next(v for v in x['models'] if v['model']=='USZ-22_EMC2'),'lower_comparators':x['EMC_models_with_lower_area']} for x in out],indent=2))
