"""Small frozen-symbol HGNC capture and annotation; never rewrites exports."""
import datetime, hashlib, json, re, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
policy=json.loads((ROOT/'frozen-policy.json').read_text())
rawdir=ROOT/'raw';rawdir.mkdir(exist_ok=True)
receipts=[]
def fetch(symbol):
    url='https://rest.genenames.org/'+('info' if symbol=='_info' else 'fetch/symbol/'+symbol)
    path=rawdir/(symbol+'.json')
    if path.exists(): raise ValueError('Refuse silent overwrite of captured metadata')
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'application/json'}),timeout=20) as response:
            body=response.read(65537)
            if len(body)>65536:raise ValueError('Response cap exceeded')
            item={'url':url,'status':response.status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':dict(response.headers)}
        path.write_bytes(body);receipts.append(item)
        return json.loads(body)
    except Exception as e:
        receipts.append({'url':url,'error':repr(e)});return None

info=fetch('_info'); records={}
for symbol in sorted({b for a,b in policy['unique_changed_pairs']}):
    records[symbol]=fetch(symbol)
pairs=[]
for source,target in policy['unique_changed_pairs']:
    response=records[target];docs=response.get('response',{}).get('docs',[]) if response else []
    exact=[d for d in docs if d.get('symbol')==target and d.get('status')=='Approved']
    entry={'source':source,'export':target,'hgnc_url':'https://rest.genenames.org/fetch/symbol/'+target}
    if re.fullmatch(r'\d+\.0',source):
        entry['classification']='unresolved_numeric_source_cell'
    elif len(exact)!=1:
        entry['classification']='unresolved_missing_or_ambiguous_current_record'
    else:
        d=exact[0];fields=[f for f in ['prev_symbol','alias_symbol'] if source in d.get(f,[])]
        entry['classification']='current_HGNC_'+fields[0] if fields else 'unresolved_no_exact_symbol_evidence'
        entry['matching_fields']=fields
    entry['current_records']=[{k:d.get(k) for k in ['hgnc_id','symbol','name','status','locus_type','prev_symbol','alias_symbol','date_approved_reserved','date_symbol_changed','date_modified']} for d in exact]
    pairs.append(entry)
events=json.loads((ROOT/'primary-check.json').read_text())['literal_gene_pair_differences']
lookup={(p['source'],p['export']):p['classification'] for p in pairs}
annotated=[]
for event in events:
    slots=[]
    for source,target in zip(event['sourceGenePair'],event['exportGenePairLiteral']):
        slots.append('unchanged' if source==target else 'missing_token_equivalent' if not source and target=='N/A' else lookup[source,target])
    annotated.append(dict(event,slot_classifications=slots))
(ROOT/'annotation.json').write_text(json.dumps({'policy_sha256':hashlib.sha256((ROOT/'frozen-policy.json').read_bytes()).hexdigest(),'unique_pairs':pairs,'events':annotated},indent=2)+'\n')
(ROOT/'retrieval-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(pairs,indent=2))
