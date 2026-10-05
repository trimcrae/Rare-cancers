import pathlib,json,hashlib,xml.etree.ElementTree as E,datetime
P=pathlib.Path(__file__).resolve().parent
B=pathlib.Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/intron_retention_gate')
paths={'BioSample':B/'raw/biosample-current-efetch.xml','SRA':B/'raw/sra-current-efetch.xml','prior23':B/'ALL23-CURRENT-IDENTITY-ASSAY-ROSTER.json','primary':B/'raw/Brenca2019-primary.xml','primary_methods':B/'PRIMARY-LIBRARY-METHOD-OBSERVATIONS.json'}
bs=E.parse(paths['BioSample']).getroot();sr=E.parse(paths['SRA']).getroot();prior=json.loads(paths['prior23'].read_text());pr={r['BioSample']:r for r in prior['all23_source_records']}
by={r.attrib['accession']:r for r in bs};rows=[]
for package in sr:
 ex=package.find('EXPERIMENT');sample=package.find('SAMPLE');acc=sample.findtext("./IDENTIFIERS/EXTERNAL_ID[@namespace='BioSample']");bio=by[acc];attrs={x.attrib['attribute_name']:x.text for x in bio.findall('./Attributes/Attribute')};old=pr[acc]
 ids=[{'attributes':x.attrib,'value':x.text} for x in bio.findall('./Ids/Id')]
 rows.append({'BioSample':acc,'SRA_sample':sample.attrib['accession'],'experiment':ex.attrib['accession'],'runs':[r.attrib['accession'] for r in package.findall('./RUN_SET/RUN')],'sample_name_ids':ids,'isolate':attrs.get('isolate'),'BioSample_attributes':attrs,'title':bio.findtext('./Description/Title'),'Owner_institution':bio.findtext('./Owner/Name'),'BioSample_Comment_count':len(bio.findall('.//Comment')),'all_public_record_links':[{'tag':x.tag,'attributes':x.attrib,'value':x.text} for x in bio.findall('./Links/*')],'library_name':ex.findtext('./DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_NAME'),'design':ex.findtext('./DESIGN/DESIGN_DESCRIPTION'),'library_strategy':ex.findtext('./DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY'),'prior_identity':old['prior_identity'],'native_case_partner_preparation_link':'unknown; genericEMClabel and numeric alias do not assignnative source or case/partner/preservation','reported_sample_unit':'oneexplicitexperiment/sample/run metadata association here, notindependent donor'})
assert len(rows)==23
(P/'ALL23-BIOSAMPLE-SRA-SAFE-METADATA.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[{'key':k,'path':str(v),'bytes':v.stat().st_size,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in paths.items()],'scope':'EveryoriginalBioSample attribute/ID/link andSRAidentity/librarymethod field; no rawfile URLs/readcount/basecount/sequence/outcome fields selected. No duplicate request.','rows':rows,'new_native_mappings':0,'pending':'All15unresolved genericaliases andall5matchedfrozen native-prep source assignments; known8engineered source-author mappings reused, not rederived fromBioSample tissueEMC.'},indent=2)+'\n')
checks={}
checks['23_BioSamples']=len(bs)==23;checks['23_experiments']=len(sr)==23;checks['23_unique_BioSamples']=len({r['BioSample'] for r in rows})==23;checks['23_unique_SRA']=len({r['SRA_sample'] for r in rows})==23;checks['23_unique_runs']=len({x for r in rows for x in r['runs']})==23
checks['exact_five_attribute_schema']=all(set(r['BioSample_attributes'])=={'isolate','age','biomaterial_provider','sex','tissue'} for r in rows)
checks['every_age_sex_missing']=all(r['BioSample_attributes']['age']=='missing' and r['BioSample_attributes']['sex']=='missing' for r in rows)
checks['all_tissueEMC_including_engineered']=all(r['BioSample_attributes']['tissue']=='EMC' for r in rows)
checks['all_providerCRO']=all(r['BioSample_attributes']['biomaterial_provider']=='CRO Aviano' for r in rows)
checks['all_no_comment']=all(r['BioSample_Comment_count']==0 for r in rows)
checks['onlyproject_links']=all(len(r['all_public_record_links'])==1 and r['all_public_record_links'][0]['attributes']=={'type':'entrez','target':'bioproject','label':'PRJNA692081'} for r in rows)
checks['exact_explicit_metadata_ID_join']=all(r['experiment']==pr[r['BioSample']]['experiment'] and r['SRA_sample']==pr[r['BioSample']]['SRA_sample'] and r['library_name']==pr[r['BioSample']]['library_name'] and r['runs']==[pr[r['BioSample']]['run']] for r in rows)
checks['eight_known_engineered_preserved']=sum(r['prior_identity']['status'].startswith('verified engineered') for r in rows)==8
checks['fifteen_unresolved_preserved']=sum(r['prior_identity']['status'].startswith('unresolved') for r in rows)==15
checks['no_native_partners_assigned']=all(r['prior_identity']['native_case_id'] is None and r['prior_identity']['native_partner'] is None and r['prior_identity']['FFPE_frozen'] is None for r in rows)
assert all(checks.values()),checks
(P/'SOURCE-VERIFICATION.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'pass':True,'newRNA_numeric_stage':False,'newsource_requests':0,'newraw_bytes':0},indent=2)+'\n')
print(json.dumps({'pass':True,'checks':len(checks),'all23':23,'new_native_mappings':0,'newrequests':0}))
