"""Whitelist citation/access metadata; mask abstract prose and outcomes."""
import hashlib, json, pathlib
HERE=pathlib.Path(__file__).resolve().parent
OWNER=pathlib.Path('/workspace/emc-r6-radiotherapy/research/autonomy/fresh-discovery-2026-10-05-round9/endocrine/native_model_discovery_refresh')
RAW=OWNER/'raw-cache'
def bind(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(n,d): (HERE/n).write_text(json.dumps(d,indent=2)+'\n')
epmc_path=RAW/'jinno_epmc_core';openalex_path=RAW/'jinno_openalex'
e=json.loads(epmc_path.read_text());assert e['hitCount']==1
r=e['resultList']['result'][0];assert r['id']==r['pmid']=='42456169' and r['doi'].lower()=='10.1158/1535-7163.mct-26-0096'
x=json.loads(openalex_path.read_text());assert x['doi'].lower()=='https://doi.org/10.1158/1535-7163.mct-26-0096'
links=r.get('fullTextUrlList',{}).get('fullTextUrl',[])
assert r['inPMC']=='N' and r['isOpenAccess']=='N'
assert len(links)==1 and links[0]['availability']=='Subscription required'
assert x['open_access']['is_oa'] is False and x['best_oa_location'] is None
assert all(z.get('pdf_url') is None for z in x['locations'])
entities=[s for s in ['extraskeletal myxoid chondrosarcoma','leiomyosarcoma','rhabdomyosarcoma','chondrosarcoma','liposarcoma','synovial sarcoma','undifferentiated pleomorphic sarcoma'] if s in r.get('abstractText','').lower()]
assert entities==['leiomyosarcoma','rhabdomyosarcoma']
receipt_path=OWNER/'JINNO-PUBLISHED-ACCESS-RECEIPTS.json';rec=json.loads(receipt_path.read_text());landing=next(z for z in rec if z['name']=='jinno_publisher_landing')
b=(RAW/'jinno_publisher_landing').read_bytes();assert len(b)==landing['bytes'] and hashlib.sha256(b).hexdigest()==landing['sha256'];assert landing['status']==403
put('INDEPENDENT-CITATION-ACCESS-REPLAY.json',{'source_bindings':[bind(epmc_path),bind(openalex_path),bind(receipt_path),bind(RAW/'jinno_publisher_landing')],'citation':{k:r.get(k) for k in ['id','pmid','pmcid','doi','title','pubYear']},'metadata_fulltext_links':links,'indexed_supplement_flag':r.get('hasSuppl'),'supplement_flag_limit':'Index flag is not proof the primary paper has no supplement.','metadata_repository_data_tags':r.get('dataLinksTagsList'),'openalex':{k:x.get(k) for k in ['id','doi','publication_date','open_access','best_oa_location','content_urls']},'available_metadata_locations':[{'landing_page_url':z.get('landing_page_url'),'pdf_url':z.get('pdf_url'),'is_oa':z.get('is_oa')} for z in x['locations']],'safe_abstract_histology_entity_tokens':entities,'entity_scope':'Abstract mentions are not a full panel roster and cannot authenticate or exclude native EMC.','primary_ordinary_route_status':landing['status'],'actual_primary_model_roster_authenticated':False,'actual_native_EMC_count':None,'null_meaning':'Unknown, not zero or exclusion.','new_abstract_endpoint_or_response_values_read':0,'new_retrieval_requests':0,'assertions_pass':True})
