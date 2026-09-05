from pathlib import Path
import json,hashlib,subprocess
r=Path(__file__).resolve().parents[4];w=r
d=json.loads((w/'research/modalities/expression-validation-readiness.json').read_text());expected=json.loads((Path(__file__).with_name('independent-readiness-expected.json')).read_text());docs={}
for key,m in d['source_manifest'].items():
 raw=subprocess.check_output(['git','show',d['base_revision']+':'+m['path']],cwd=r);assert hashlib.sha256(raw).hexdigest()==m['sha256'];docs[m['path']]=json.loads(raw)
for key,s in d['sources'].items():
 x=docs[s['file']]
 for part in s['json_pointer'].split('/')[1:] if s['json_pointer'] else []:
  part=part.replace('~1','/').replace('~0','~');x=x[int(part)] if isinstance(x,list) else x[part]
 assert hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()==s['value_sha256'],key
 if 'value' in s:assert s['value']==x,key
 if 'length' in s:assert len(x)==s['length'],key
 assert s['file_sha256']==next(m['sha256'] for m in d['source_manifest'].values() if m['path']==s['file'])
for name,key in [('GSE24369','GSE24369_series_matrix.txt.gz'),('GSE4303','GSE4303-GPL3290_series_matrix.txt.gz')]:
 c=d['cohorts'][name];e=expected['arrays'][key];counts=c['counts'];assert counts['cached_sample_records']['value']==e['unique_gsm'];assert counts['EMC_sample_records']['value']==e['emc'];assert counts['comparator_sample_records']['value']==e['comparator'];assert counts['class_counts']['value']==e['class_counts'];assert c['CHRNA6']['platform_coverage']['value']=='not_assessed';assert c['CHRNA6']['selected_gene_cache_present']['value'] is False
q=d['cohorts']['PRJNA1357027'];e=expected['fourth'];assert q['counts']['runs']['value']==e['unique_runs'];assert q['counts']['BioSample_records']['value']==e['unique_sample_accessions'];assert q['existing_values']['assigned_probes']['value']==e['single_gene_probes'];assert q['existing_values']['multi_gene_probes']['value']==e['multi_gene_probes'];assert d['array_exact_ID_overlap']['value']==expected['array_exact_gsm_overlap']
assert q['counts']['unique_patients']['value'] is None
assert d['cohorts']['GSE170983']['alias_of']['value']=='GSE28866'
print(json.dumps({'status':'passed','source_pointers_independently_resolved':len(d['sources']),'input_hashes_checked':len(d['source_manifest']),'counts_match_independent_recomputation':True,'unknown_and_alias_handling_checked':True}))
