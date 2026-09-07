"""Public, unpaid API retrieval. Run from any directory; outputs stay beside this script.
Python standard library only. Re-running resumes only hash-verified completed queries.
Use --analyze for deterministic offline summary without network access.
"""
import argparse, datetime, gzip, hashlib, json, pathlib, time, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = ROOT / 'sources'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def raw(path): return gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
def read(path): return json.loads(raw(path).decode('utf-8'))
def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'EMCResearch-bounded-discoverability-audit/1.0'}), timeout=45) as r:
                return r.read(), dict(r.headers)
        except Exception:
            if attempt == 2: raise
            time.sleep(2*(attempt+1))
def expression(terms):
    return ' OR '.join('('+x+')' if ' AND ' in x else '"'+x+'"' for x in terms)
def queries(selection):
    for d in selection['diagnoses']:
        for mode, field, terms in [('condition','query.cond',d['synonyms']),('ordinary','query.term',d['synonyms']),('molecular','query.term',d['molecular_terms'])]:
            yield d['id']+'_'+mode, {field:expression(terms)}
    yield 'parent_sarcoma', {'query.term':'sarcoma'}
    yield 'historical_anchors', {'filter.ids':','.join(selection['historical_anchors'])}
    for d in selection['diagnoses']:
        yield d['id']+'_eligibility_ordinary', {'query.term':'AREA[EligibilitySearch]('+expression(d['synonyms'])+')'}
        yield d['id']+'_eligibility_molecular', {'query.term':'AREA[EligibilitySearch]('+expression(d['molecular_terms'])+')'}
    yield 'parent_eligibility_sarcoma', {'query.term':'AREA[EligibilitySearch]sarcoma'}
    # Sensitivity check: identical frozen terms with phrase quotes removed.
    for d in selection['diagnoses']:
        expr=' OR '.join('('+s+')' for s in d['synonyms'])
        yield d['id']+'_unquoted_ordinary', {'query.term':expr}
        yield d['id']+'_unquoted_eligibility', {'query.term':'AREA[EligibilitySearch]('+expr+')'}
def load_queries():
    result={}
    for p in sorted(SOURCES.glob('*/manifest.json')):
        m=read(p)
        if not m.get('complete'): continue
        studies={}
        for page in m['pages']:
            b=raw(ROOT/page['file'])
            assert sha(b)==page['sha256'], page['file']
            for s in json.loads(b)['studies']:
                studies[s['protocolSection']['identificationModule']['nctId']]=s
        assert sorted(studies)==m['ids'] and len(studies)==m['total_count']
        result[m['query_id']]=(m,studies)
    return result
def analyze():
    q=load_queries(); result={'generated_at_utc':now(),'scope':'Query retrieval counts, not eligibility or recall','queries':{},'comparisons':{}}
    for name,(m,studies) in q.items():
        result['queries'][name]={'count':len(studies),'pages':len(m['pages']),'total_count':m['total_count'],'ids':sorted(studies)}
    for d in read(ROOT/'selection.json')['diagnoses']:
        k=d['id']; c=set(q[k+'_condition'][1]); o=set(q[k+'_ordinary'][1]); molecular=set(q[k+'_molecular'][1]); p=set(q['parent_sarcoma'][1])
        result['comparisons'][k]={'condition_count':len(c),'ordinary_count':len(o),'molecular_count':len(molecular),'ordinary_not_condition':sorted(o-c),'molecular_not_ordinary':sorted(molecular-o),'molecular_not_ordinary_in_parent':sorted((molecular-o)&p),'molecular_not_ordinary_not_parent':sorted(molecular-o-p)}
    union={n:s for _,ss in q.values() for n,s in ss.items()}
    result['unique_union_count']=len(union)
    save(ROOT/'retrieval-summary.json',result)
    rows=[]
    for n,s in sorted(union.items()):
        ps=s['protocolSection']; status=ps['statusModule']['overallStatus']; design=ps.get('designModule',{})
        rows.append({'nct_id':n,'status':status,'study_type':design.get('studyType'),'title':ps['identificationModule']['briefTitle'],'query_ids':[k for k,(_,ss) in q.items() if n in ss]})
    save(ROOT/'corpus-index.json',rows)
    print(json.dumps({k:{kk:len(vv) if isinstance(vv,list) else vv for kk,vv in v.items()} for k,v in result['comparisons'].items()},indent=2),flush=True)
def main():
    args=argparse.ArgumentParser(); args.add_argument('--analyze',action='store_true'); opts=args.parse_args()
    if opts.analyze: analyze(); return
    selection=read(ROOT/'selection.json'); SOURCES.mkdir(exist_ok=True)
    for qid,params in queries(selection):
        dest=SOURCES/qid; dest.mkdir(exist_ok=True); mp=dest/'manifest.json'
        if mp.exists() and read(mp).get('complete'):
            print(qid,'cached',flush=True); continue
        m={'query_id':qid,'parameters':params,'started_at_utc':now(),'selection_sha256':sha((ROOT/'selection.json').read_bytes()),'pages':[],'complete':False}
        ids=[]; token=None; seen=set(); total=None
        try:
            while True:
                pp={**params,'format':'json','pageSize':selection['page_size'],'countTotal':'true'}
                if token: pp['pageToken']=token
                url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(pp)
                b,h=get(url); fn=dest/f'page-{len(m["pages"])+1:04d}.json'; fn.write_bytes(b); obj=json.loads(b)
                pageids=[s['protocolSection']['identificationModule']['nctId'] for s in obj.get('studies',[])]
                if total is None: total=obj.get('totalCount')
                assert obj.get('totalCount',total)==total,'count drift'
                m['pages'].append({'file':fn.relative_to(ROOT).as_posix(),'url':url,'retrieved_at_utc':now(),'sha256':sha(b),'bytes':len(b),'count':len(pageids),'request_page_token':token,'next_page_token':obj.get('nextPageToken'),'headers':h})
                ids.extend(pageids); token=obj.get('nextPageToken'); save(mp,m)
                print(qid,len(ids),total,flush=True)
                if not token: break
                assert token not in seen,'token loop'; seen.add(token)
            assert len(ids)==len(set(ids))==total,(len(ids),len(set(ids)),total)
            m.update(complete=True,ids=sorted(ids),total_count=total,finished_at_utc=now()); save(mp,m)
        except Exception as exc:
            m.update(error=repr(exc),finished_at_utc=now()); save(mp,m); raise
    analyze()
if __name__=='__main__': main()
