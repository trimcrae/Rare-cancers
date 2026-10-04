"""Complete source-ID-level EMC extraction from original Foundation XLS."""
from pathlib import Path
import sys,json,hashlib,collections
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D/'xlrd-2.0.2-py2.py3-none-any.whl'))
import xlrd
p=D/'foundation-supplement2.xls';raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475'
w=xlrd.open_workbook(file_contents=raw)
def rows(sheet):
 s=w.sheet_by_name(sheet);head=s.row_values(0)
 return [dict(zip(head,s.row_values(i)),source_excel_row=i+1) for i in range(1,s.nrows)]
s=rows('samples_table_final_for_supplem');v=rows('variants_table_final_for_supple')
def emc(x):return 'extraskeletal myxoid' in str(x).lower()
labelled=[r for r in s if emc(r['initial_diagnosis']) or emc(r['final_diagnosis'])]
nr4=[r for r in v if any(str(r[k]).upper() in ['NR4A3','CHN','TEC'] for k in ['gene','partner_gene'])]
ids={r['de-identified ID'] for r in labelled}|{r['de-identified ID'] for r in nr4}
case=[]
for r in s:
 if r['de-identified ID'] not in ids:continue
 events=[x for x in v if x['de-identified ID']==r['de-identified ID']]
 defining=[x for x in events if x in nr4]
 case.append({'source_id':int(r['de-identified ID']),'sample':r,'source_final_emc':emc(r['final_diagnosis']),'source_initial_emc':emc(r['initial_diagnosis']),'NR4A3_support':defining,'all_events':events,'secondary_events':[x for x in events if x not in defining]})
final=[x for x in case if x['source_final_emc']]
assert len(final)==75
g=collections.defaultdict(set);gt=collections.defaultdict(set)
for x in final:
 for e in x['secondary_events']:
  g[e['gene']].add(x['source_id']);gt[(e['gene'],e['alteration_type'])].add(x['source_id'])
report={'date':'2026-10-04','source_doi':'10.1038/s41467-022-30496-0','source_sha256':hashlib.sha256(raw).hexdigest(),'source_profiles_total':len(s),'all_variant_rows':len(v),'final_emc_profiles':len(final),'initial_emc_profiles':sum(x['source_initial_emc'] for x in case),'NR4A3_supported_final_emc_profiles':sum(bool(x['NR4A3_support']) for x in final),'NR4A3_source_records_all':len(nr4),'cases_selected_by_either_label_or_defining_gene':len(case),'source_labeled_cases':case,'gene_source_id_counts':{k:{'count':len(q),'source_ids':sorted(q)}for k,q in sorted(g.items(),key=lambda z:(-len(z[1]),z[0]))},'gene_event_type_counts':[{'gene':k[0],'source_alteration_type':k[1],'count':len(q),'source_ids':sorted(q)}for k,q in sorted(gt.items(),key=lambda z:(-len(z[1]),z[0]))],'limits':['Source IDs are profiles; repeat-donor crosswalk not provided. Counts are not independently validated donor recurrence.','Panel coverage per source profile is unavailable in this workbook; absence of a row is not a validated event-class-negative measurement.','SV in this table denotes short variant; RE denotes rearrangement.','Literal source classification is retained; no diagnosis or actionability adjudication is performed by this extraction.']}
(D/'foundation-emc-all-values.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['source_labeled_cases','gene_event_type_counts']},indent=2))
