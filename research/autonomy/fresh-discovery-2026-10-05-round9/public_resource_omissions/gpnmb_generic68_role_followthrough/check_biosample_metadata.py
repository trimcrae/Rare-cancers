import sys
if '--fetch' not in sys.argv:
    raise SystemExit('Acquisition is disabled by default. Use validate_cached_sources.py for offline replay; do not repeat unchanged official requests.')
import json,pathlib,datetime,hashlib,urllib.request,urllib.error,xml.etree.ElementTree as ET,collections
P=pathlib.Path(__file__).resolve().parent
route=json.loads((P/'BIOSAMPLE-ROUTE-FROZEN.json').read_text())
source=json.loads((P/'ALL68-DECLARED-BIOSAMPLE-METADATA-LINKS.json').read_text())
assert hashlib.sha256((P/'ALL68-DECLARED-BIOSAMPLE-METADATA-LINKS.json').read_bytes()).hexdigest()==route['source_link_file_sha256']
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-05T22:15:00+00:00')
receipt={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':route['url'],'timeout_seconds':10,'call_number':2}
raw=None
try:
 with urllib.request.urlopen(urllib.request.Request(route['url'],headers={'User-Agent':'EMC-public-metadata-audit/1.0'}),timeout=10) as r:
  receipt['http_status']=r.status; receipt['content_type']=r.headers.get('Content-Type'); raw=r.read(67108865)
 if len(raw)>67108864: raise ValueError('raw budget exceeded; no input accepted')
 (P/'raw-cache').mkdir(exist_ok=True)
 (P/'raw-cache'/'GSE299349-BioSample-all68.xml').write_bytes(raw)
 receipt.update({'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'accepted_original':'raw-cache/GSE299349-BioSample-all68.xml'})
except Exception as e:
 receipt.update({'failure_type':type(e).__name__,'error':str(e)})
receipt['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(P/'BIOSAMPLE-ACCESS-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
if raw is None or 'accepted_original' not in receipt:
 print(json.dumps(receipt)); raise SystemExit()
root=ET.fromstring(raw)
allowed={s.casefold() for s in route['allowed_attribute_names']}
rows=[]; schema=collections.Counter()
for b in root.findall('.//BioSample'):
 accession=b.attrib.get('accession')
 attrs=[]; excluded=[]
 for a in b.findall('./Attributes/Attribute'):
  key=a.attrib.get('harmonized_name') or a.attrib.get('attribute_name') or ''
  schema[key]+=1
  if key.casefold() in allowed:
   attrs.append({'attribute_name':a.attrib.get('attribute_name'),'harmonized_name':a.attrib.get('harmonized_name'),'value':a.text or ''})
  else: excluded.append(key)
 links=[]
 for l in b.findall('./Links/Link'):
  # Explicit outward link values only, no surrounding scientific body.
  links.append({'type':l.attrib.get('type'),'target':l.attrib.get('target'),'label':l.attrib.get('label'),'value':l.text or ''})
 rows.append({'BioSample':accession,'identity_condition_attributes':attrs,'excluded_attribute_keys_only':excluded,'outward_metadata_links':links})
by={r['BioSample']:r for r in rows}
assert len(by)==len(rows)
out={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':receipt['sha256'],'returned_biosamples':len(rows),'requested_records':68,'requested_accessions_missing':[r['BioSample'] for r in source['actual_links'] if r['BioSample'] not in by],'extra_accessions':[a for a in by if a not in {r['BioSample'] for r in source['actual_links']}],'attribute_schema_counts':dict(schema),'records':[{**s,**by.get(s['BioSample'],{'identity_condition_attributes':[],'missing_requested_biosample':True})} for s in source['actual_links']], 'exposure':'Only whitelisted identity/condition attributes, attribute-key schema and outward metadata links projected. No Title, Description, protocol, mechanism, RNA or response quantities.'}
(P/'ALL68-BIOSAMPLE-IDENTITY-CONDITION-FIELDS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'receipt':receipt,'returned':len(rows),'schema_names':dict(schema),'missing':out['requested_accessions_missing'],'safe_attribute_value_counts':dict(collections.Counter((a['harmonized_name'] or a['attribute_name'],a['value']) for r in rows for a in r['identity_condition_attributes'])) if False else [{'key':k,'value':v,'records':n} for (k,v),n in collections.Counter((a['harmonized_name'] or a['attribute_name'],a['value']) for r in rows for a in r['identity_condition_attributes']).items()]},indent=2))
