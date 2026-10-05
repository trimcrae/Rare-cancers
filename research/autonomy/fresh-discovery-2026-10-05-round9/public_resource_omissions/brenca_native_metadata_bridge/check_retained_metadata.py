"""Verify retained project identity/link schema only; no requests or RNA outcomes."""
import collections, hashlib, json, pathlib, xml.etree.ElementTree as ET
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
RAW=pathlib.Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate/raw')
HERE=pathlib.Path(__file__).resolve().parent

def bind(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(n,d): (HERE/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
roster_path=ROOT/'fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate/ALL23-CURRENT-IDENTITY-ASSAY-ROSTER.json'
native_path=ROOT/'fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate/ALL-NATIVE-CONDITIONS-COVERAGE.json'
bio_path=RAW/'biosample-current-efetch.xml'
d=json.loads(roster_path.read_text());native=json.loads(native_path.read_text());bio=ET.fromstring(bio_path.read_bytes());bs=bio.findall('.//BioSample')
assert len(bs)==23 and len(d['all23_source_records'])==23
byacc={r.get('accession'):r for r in bs};rows=[]
for r in d['all23_source_records']:
 s=byacc[r['BioSample']];attrs={x.get('attribute_name'):x.text for x in s.findall('./Attributes/Attribute')};owner=s.findtext('./Owner/Name');title=s.findtext('./Description/Title');links=[{'type':x.get('type'),'target':x.get('target'),'label':x.get('label'),'identifier':x.text} for x in s.findall('./Links/*')]
 assert attrs==r['BioSample_attributes']
 assert set(attrs)=={'isolate','age','biomaterial_provider','sex','tissue'}
 assert attrs['isolate']=='s_'+r['numeric_alias']
 assert attrs['biomaterial_provider']==owner=='CRO Aviano'
 assert attrs['age']==attrs['sex']=='missing'
 assert attrs['tissue']=='EMC' and title=='Human sample from Homo sapiens'
 assert links==[{'type':'entrez','target':'bioproject','label':'PRJNA692081','identifier':'692081'}]
 assert not s.findall('.//Comment')
 row={k:r[k] for k in ['numeric_alias','SRA_sample','BioSample','experiment','run','library_name','design','strategy','selection','layout','platform']}
 row.update(attributes=attrs,owner_organization=owner,title=title,actual_record_links=links,prior_identity=r['prior_identity'],bridge_from_record=None)
 rows.append(row)
engineered=[r for r in rows if r['prior_identity']['status'].startswith('verified engineered')]
assert len(engineered)==8
assert {r['numeric_alias'] for r in engineered}=={'315','316','317','363','367','385','386','318'}
assert len({r['run'] for r in rows})==23 and len(byacc)==23
cases=[]
for r in native['all12native_published_cases']:
 cases.append({k:r[k] for k in ['published_case','partner','sex','age','site','source_authentication','condition','source_to_run']})
assert len(cases)==12
put('ALL23-RETAINED-METADATA-REPLAY.json',{'source_bindings':[bind(roster_path),bind(bio_path)],'records':rows,'new_case_partner_preparation_bridges':0,'known_engineered_aliases':8,'unresolved_aliases':15,'native_count_from_generic_tissue_label':None,'new_source_requests':0,'RNA_values_or_sequences_read':0,'source_boundary':'Complete23 previously fetched records; no claim of unchanged future metadata or project-wide public absence.'})
put('NATIVE-AND-PREPARATION-SOURCE-REUSE.json',{'source_binding':bind(native_path),'all12_cases':cases,'all5_additional_paired_frozen':native['all5additional_paired_frozen'],'all11_engineered_source_conditions':native['all11engineered_source_conditions'],'additional_targeted_gene_array_conditions':native['additional_targeted_gene_array_conditions'],'unit_rule':'Twelve native cases, five matched preparations and six amplified array conditions are not23 independent native donors; eleven engineered controls remain separate. Neither current23 nor unrelated numeric aliases supply the missing donor/preparation/library crosswalk.','RNA_values_read':0})
put('VERIFICATION.json',{'complete_retained_biosamples':23,'complete_current_roster_records':23,'distinct_retained_runs':23,'generic_title_records':23,'five_generic_attributes_records':23,'repeat_known_project_only_links':23,'owner_provider_CRO_Aviano_records':23,'public_outbound_bridge_links':0,'known_engineered_aliases':8,'unresolved_aliases':15,'all_native_case_records':12,'all_native_partner_and_preparation_mapping_to_runs':'Unresolved','new_network_requests':0,'new_retained_original_bytes':0,'new_RNA_or_sequence_values':0,'assertions_pass':True})
