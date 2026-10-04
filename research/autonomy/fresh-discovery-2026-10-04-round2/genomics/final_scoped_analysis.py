from pathlib import Path
import json,csv,io,zipfile,hashlib,collections,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
f=json.loads((D/'foundation-emc-all-values.json').read_text())
real=[c for c in f['source_labeled_cases'] if c['source_final_emc']]
out={'foundation_cases':len(real),'secondary_event_count':sum(len(c['secondary_events'])for c in real),'secondary_event_cases':sum(bool(c['secondary_events'])for c in real),'foundation_tissues':dict(collections.Counter(c['sample']['tissue']for c in real))}
z=zipfile.ZipFile(D/'foundation-source-data.zip');fig={}
for n in ['src/fig2a-1_data.txt','src/fig5b_data.txt']:
 rows=list(csv.DictReader(io.StringIO(z.read(n).decode()),delimiter='\t'));fig[n]=[r for r in rows if r['Disease']=='EMC']
out['original_published_emc_figure_values']=fig
(D/'foundation-published-figure-emc-rows.json').write_text(json.dumps(fig,indent=2),encoding='utf-8')
print('original TSC2',[r for r in fig['src/fig2a-1_data.txt']if r['Gene']=='TSC2']);print('actionability',fig['src/fig5b_data.txt'])
labels=json.loads((D/'origimed-all-labels.json').read_text());ids=[x['sampleId']for x in labels if x['value'].lower()=='extraskeletal myxoid chondrosarcoma'];assert ids==['P-4093','P-5337']
m=json.loads((D/'origimed-all-eligible-mutations.json').read_text());sv=json.loads((D/'origimed-all-eligible-sv.json').read_text());clin=json.loads((D/'origimed-all-eligible-clinical.json').read_text())
out['origimed']={'all_emc_labeled_ids':ids,'identity_conflict_id':'P-6101','source_cases':[{'sample':id,'clinical':{x['clinicalAttributeId']:x['value']for x in clin if x['sampleId']==id},'mutations':[x for x in m if x['sampleId']==id],'structural_variants':[x for x in sv if x['sampleId']==id]}for id in ids+['P-6101']],'cna_result':json.loads((D/'origimed-all-eligible-cna.json').read_text()),'interpretation':'All source labels evaluated; source matched normal design, unique patient per tumor. No cross-cohort identity crosswalk. P6101 fusion/label discordance retained without reclassification. P5337 lacking called fusion is not automatically misdiagnosed. Empty CNA event list is no reported alteration, not validated copy-neutral every gene.'}
j=json.loads((D/'japan-tables-extracted.json').read_text());em=[row for row in j[0]['rows']if any(v=='EMC'for v in row['cells'].values())]
assert len(em)==6
out['japan_cas70214']={'source_doi':'10.1111/cas.70214','all_six_emc_small_variant_rows':em,'source_limitation':'S7 small-variant columns. Not a complete per-case CNV/fusion table. Aggregate fusion counts six, source donor crosswalk to DOI10.1002/cam4.71098 unavailable. No TSC2/IDH2/ARID1A/NTRK3 small variant in these six rows.'}
svall=json.loads((D/'cbio-nr4a3-sv-all-events.json').read_text());mutall=json.loads((D/'cbio-nr4a3-mutation-all-events.json').read_text());out['cbio_query']={'SV_profiles':223,'SV_events':len(svall),'SV_studies':dict(collections.Counter(x['studyId']for x in svall)),'no_SV_mutation_profiles':320,'NR4A3_mutation_records':len(mutall),'mutation_types':dict(collections.Counter(x['mutationType']for x in mutall)),'interpretation':'No fusion-like mutation record. Gene-selected search is incomplete for unmeasured NR4A3, NR4A2-defined EMC, source-labelled EMC without fusion release, and hidden labels. Not an all-EMC negative search.'}
r=E.parse(D/'clinvar-tsc2-q955.xml').getroot();out['TSC2_Q955_interpretation']={'clinvar_variation_id':821922,'comments':[' '.join(x.itertext())for x in r.findall('.//Comment')],'primary_validation_doi':'10.1002/humu.22951','consequence':'Not two established TSC2 losses. Germline VUS classification and exon-skipping biology do not establish benignity in EMC either; EMC-specific isoform and functional effects unmeasured.'}
(D/'final-scoped-analysis.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print({k:v for k,v in out.items()if k in ['foundation_cases','secondary_event_count','secondary_event_cases','foundation_tissues']})
# Raw read sequences are retained unchanged in the source workbook. Avoid duplicating 65,536 read-like lines into JSON.
x=json.loads((D/'other-published-genomics-tables.json').read_text())
for s in x:
 if s['sheet']=='NGS panel' and len(s['all_rows'])>1:s['omitted_read_like_rows']=len(s['all_rows'])-1;s['all_rows']=s['all_rows'][:1];s['suitability']='Sheet is read-like FASTQ lines without alignment/complete sample library, unsuitable as annotated variant-negative evidence; original XLSX retained.'
(D/'other-published-genomics-tables.json').write_text(json.dumps(x,indent=2),encoding='utf-8')
