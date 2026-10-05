#!/usr/bin/env python3
"""Replay source-only identity, assay and technical-condition fields; never array values."""
import collections,hashlib,json,pathlib,re,sys,xml.etree.ElementTree as E
p=pathlib.Path(__file__).resolve().parent
out=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else p
out.mkdir(parents=True,exist_ok=True)
def dump(n,d): (out/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
s=(p/'raw/GSE9309-brief-family-metadata.txt').read_text()
assert '!sample_table_begin' not in s.lower()
keep={'title','source_name_ch1','source_name_ch2','molecule_ch1','molecule_ch2','extract_protocol_ch1','extract_protocol_ch2','growth_protocol_ch1','growth_protocol_ch2','label_protocol_ch1','hyb_protocol','platform_id','description'}
rows=[]
for b in re.split(r'^\^SAMPLE = ',s,flags=re.M)[1:]:
 gsm=b.splitlines()[0].strip(); fields=collections.defaultdict(list)
 for k,v in re.findall(r'^!Sample_([^ ]+) = (.*)$',b,re.M):
  if k in keep or (k=='characteristics_ch1' and (v.startswith('gender:') or v.startswith('tissue:'))) or (k=='characteristics_ch2' and v.startswith('reference:')): fields[k].append(v)
 rows.append({'GSM':gsm,'fields':dict(fields)})
assert len(rows)==142 and len({r['GSM'] for r in rows})==142
roster={'scope':'All 142 official GSM identities, source histology, tissue preparation, assay and exact technical-buffer descriptions. Receptor-state fields excluded; no expression-table values. Libraries are not independent donors.','series':'GSE9309','count':142,'rows':rows}
dump('GSE9309-SOURCE-IDENTITY-CONDITION-ROSTER.json',roster)
def counts(k): return dict(collections.Counter(v for r in rows for v in r['fields'].get(k,[])))
links=[]
for r in rows:
 for d in r['fields'].get('description',[]):
  m=re.fullmatch(r'Same tissue as sample (\d+) but hybridized with Buffer1',d)
  if m:
   candidates=[x['GSM'] for x in rows if any(t.endswith('_'+m[1]) for t in x['fields']['title'])]
   links.append({'GSM':r['GSM'],'source_statement':d,'source_sample_alias':m[1],'title_suffix_matches':candidates,'interpretation':'Explicit same-tissue technical buffer condition; numeric alias is not an authenticated patient ID.'})
assert len(links)==36 and all(len(x['title_suffix_matches'])==1 for x in links)
rep=collections.Counter(re.search(r'_rep([^_]+)_',r['fields']['title'][0]).group(1) for r in rows)
obs={'source_scope':'Complete 142 GSM metadata records only; no expression matrix.','source_histology_counts':counts('source_name_ch1'),'tissue_and_gender_counts':counts('characteristics_ch1'),'platform_counts':counts('platform_id'),'reference_channel_counts':counts('source_name_ch2'),'preparation_counts':counts('growth_protocol_ch1'),'description_classes':{'Buffer1':70,'Buffer2':36,'explicit_same_tissue_Buffer1':36},'title_rep_token_counts':dict(rep),'explicit_same_tissue_links':links,'authenticated_native_EMC_records':0,'meaning_of_zero':'No author EMC/NR4A3/native EMC identity in these source-labeled breast records; not biological or universal cohort absence.','patient_denominator':None,'patient_denominator_reason':'Per-GSM library and source sample aliases are not a complete patient/case crosswalk; explicit 36 same-tissue links prevent counting 142 independent patients.','alias_disambiguation':{'MC':'Mucinous Carcinoma, explicitly spelled out by source; not myxoid chondrosarcoma.','MCB':'Metaplastic Carcinoma of Breast; not native EMC.','PT':'Phyllodes Tumor; no EMC authentication.','GSE9303':'Distinct accession; no identity or measurements transferred.'}}
dump('COMPLETE-SOURCE-CONDITION-OBSERVATIONS.json',obs)
root=E.parse(p/'raw/PMC3597597.xml').getroot()
paras=[]
for sec in root.iter('sec'):
 t=sec.find('title')
 if t is not None and ''.join(t.itertext()).strip()=='Microarray expression data': paras=[''.join(x.itertext()) for x in sec.findall('p')]
assert len(paras)==1
method={'citation':{'PMID':'23516564','PMCID':'PMC3597597','DOI':'10.1371/journal.pone.0058851','title':'Identifying gene set association enrichment using the coefficient of intrinsic dependence.'},'selected_section':'Microarray expression data','verbatim_selected_method_paragraphs':paras,'evaluated_scope':'Only identity, cohort units, preparation, array/reference assay and deposit linkage; no results/discussion/table cells.','pooled_accessions':['GSE24124','GSE17040','GSE9309'],'pooled_patient_counts':{'tumor_patients':181,'adjacent_nontumor_patients':25},'count_warning':'These patient counts cover the combined primary study and cannot be assigned to GSE9309 alone.','pooled_case_accession_TableS1_crosswalk':'Not inspected; pending.','other_primary_accessions':'Outside fixed source pilot; no evaluation of their enrollment or matrix values.','prior_art_value':'Statistical gene-set association method and technical subgroup standardization, not a native EMC perturbation or a new disease-specific model-fidelity measurement.'}
dump('PRIMARY-SELECTED-METHODS.json',method)
raw=[]
for f in sorted((p/'raw').iterdir()):
 if f.is_file(): raw.append({'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'disposition':'Ignored cache-only original; not exported to Git.'})
dump('SOURCE-HASHES.json',{'originals':raw,'retained_bytes':sum(x['bytes'] for x in raw)})
print(json.dumps({'samples':len(rows),'explicit_same_tissue_links':len(links),'histology':obs['source_histology_counts'],'title_rep_tokens':dict(rep),'original_bytes':sum(x['bytes'] for x in raw)}))
