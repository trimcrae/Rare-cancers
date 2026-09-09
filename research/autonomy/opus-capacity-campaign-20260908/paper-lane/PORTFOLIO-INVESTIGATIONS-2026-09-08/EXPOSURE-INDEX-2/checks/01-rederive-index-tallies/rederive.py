import json, collections, hashlib, sys
p="../EXPOSURE-INDEX/emc-patient-exposure-index.json"
raw=open(p,'rb').read()
print("sha256(source index) =", hashlib.sha256(raw).hexdigest())
d=json.loads(raw)
rows=d['rows']
print("rows =", len(rows))
print("retrieval_completeness:", dict(collections.Counter(r['retrieval_completeness'] for r in rows)))
print("n_emc_status:", dict(collections.Counter(r['n_emc_status'] for r in rows)))
print("overlap_unknown:", dict(collections.Counter(r['overlap_unknown'] for r in rows)))
print("headline_n_is_not_emc_n:", dict(collections.Counter(str(r['headline_n_is_not_emc_n']) for r in rows)))
exp={'rows':28,'unread':18,'partial':7,'complete':3,'overlap_unknown_true':24,'n_emc_UNKNOWN':19}
got={'rows':len(rows),
 'unread':sum(1 for r in rows if r['retrieval_completeness']=='unread'),
 'partial':sum(1 for r in rows if r['retrieval_completeness']=='partial'),
 'complete':sum(1 for r in rows if r['retrieval_completeness']=='complete'),
 'overlap_unknown_true':sum(1 for r in rows if r['overlap_unknown'] is True),
 'n_emc_UNKNOWN':sum(1 for r in rows if r['n_emc_status']=='UNKNOWN')}
print("expected:",exp)
print("got     :",got)
ok = exp==got
print("REPRODUCES:", ok)
print()
print("--- UNKNOWN n_emc rows ---")
for r in rows:
    if r['n_emc_status']=='UNKNOWN':
        print(r['row_id'], '| pmcid=', r['identifier'].get('pmcid'), '| pmid=', r['identifier'].get('pmid'), '| rc=', r['retrieval_completeness'])
sys.exit(0 if ok else 1)
