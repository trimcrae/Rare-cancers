"""Offline source-only builder/verifier. Never imports original code or reads label members."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'trial-frozen-baseline-package-2026-09-06'
ARCHIVE_SHA = '85c2083921ad6050c48da1f54fbe7849104ed7d1f90da6ecf85d477e7140ba5b'
MANIFEST_SHA = '40145d75f2b5f6060525df0c5d4687bc8be018b4273bc52176d0edac30d5965c'
BASE = 'b094175bb81d08b436f002720695401a3f640f00'
F = 'trial-frozen-baseline-2026-09-06/'
S = 'trial-discoverability-2026-09-05/'
GENERIC = 'trial-reference-adjudication-2026-09-05/reading-label-protocol.json'
SEED = 'EMC-difference-2026-09-06-source-only-v1'
NAMED = {F+x for x in ['rankings-EMC.json', 'baseline.py', 'protocol.md',
                      'amendment-2026-09-06.md', 'freeze.json', 'version-audit.json']}
NAMED |= {S+'corpus-index.json', GENERIC}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

def pretty(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2)+'\n').encode('utf-8')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def version_key(study, page):
    date = study['protocolSection'].get('statusModule', {}).get('lastUpdatePostDateStruct', {}).get('date', '')
    retrieved = page.get('retrieved_at_utc', '')
    require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', date)), 'Missing/invalid record version date')
    datetime.fromisoformat(date)
    parsed = datetime.fromisoformat(retrieved.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0, 'Non-UTC retrieval key')
    return date, retrieved

def select_version(candidates):
    best = max(version_key(s,p) for s,p,*_ in candidates)
    tied = [c for c in candidates if version_key(c[0],c[1]) == best]
    return min(tied, key=lambda c:(c[1]['file'], sha(canonical(c[0]))))

def check_ranks(rows, method):
    """Validate stored rank fields using stored scores, without computing any scores."""
    order = sorted(rows, key=lambda r:(-r['methods'][method]['score'], r['nct_id']))
    i = 0
    while i < len(order):
        j = i+1
        while j < len(order) and order[j]['methods'][method]['score'] == order[i]['methods'][method]['score']:
            j += 1
        for pos in range(i,j):
            m = order[pos]['methods'][method]
            require((m['rank'],m['rank_min'],m['rank_max'],m['midrank']) ==
                    (pos+1,i+1,j,(i+1+j)/2), 'Archived rank/tie inconsistency')
        i = j
    return order

def study_slices(raw):
    """Decode top-level studies array and return exact character spans of its objects."""
    text = raw.decode('utf-8'); decoder = json.JSONDecoder()
    def ws(i):
        while i < len(text) and text[i].isspace():
            i += 1
        return i
    i = ws(0); require(text[i] == '{', 'Page must be object'); i += 1
    while True:
        i = ws(i)
        if text[i] == '}':
            raise ValueError('No top-level studies array')
        key,i = decoder.raw_decode(text,i); i = ws(i)
        require(text[i] == ':','Invalid page'); i = ws(i+1)
        if key == 'studies':
            require(text[i] == '[','studies must be array'); i += 1; index = 0
            while True:
                i = ws(i)
                if text[i] == ']':
                    return
                start = i; study,i = decoder.raw_decode(text,i)
                yield index,study,text,start,i
                index += 1; i = ws(i)
                if text[i] == ',':
                    i += 1
                else:
                    require(text[i] == ']','Invalid array'); return
        _,i = decoder.raw_decode(text,i); i = ws(i)
        require(text[i] == ',','studies absent'); i += 1

def yield_difference(h, a, labels):
    return sum(labels[n] for n in a-h)-sum(labels[n] for n in h-a)

def difference_bounds(h, a, bounds):
    needed = h^a
    for n in needed:
        require(n in bounds and bounds[n] in [(0,0),(0,1),(1,1)], 'Missing/invalid bounds')
    return (sum(bounds[n][0] for n in a-h)-sum(bounds[n][1] for n in h-a),
            sum(bounds[n][1] for n in a-h)-sum(bounds[n][0] for n in h-a))

def prepare():
    archive = PACKAGE/'frozen-experiment.zip'; manifest_path = PACKAGE/'archive-manifest.json'
    require(sha(archive.read_bytes()) == ARCHIVE_SHA, 'ZIP hash mismatch')
    mb = manifest_path.read_bytes(); require(sha(mb) == MANIFEST_SHA,'Archive manifest hash mismatch')
    manifest = json.loads(mb)
    require(manifest['archive_sha256'] == ARCHIVE_SHA and archive.stat().st_size == manifest['archive_size'], 'Container mismatch')
    dependencies = {}
    with zipfile.ZipFile(archive) as z:
        require(len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP member')
        def read_member(name):
            allowed = name in NAMED or bool(re.fullmatch(re.escape(S)+r'sources/[^/]+/(manifest\.json|page-\d+\.json\.gz)',name))
            require(allowed, 'Forbidden member access: '+name)
            raw = z.read(name); expected = manifest['entries'][name]
            require(len(raw) == expected['size'] and sha(raw) == expected['sha256'], 'Archive member mismatch: '+name)
            dependencies[name] = dict(expected)
            return raw
        freeze = json.loads(read_member(F+'freeze.json'))
        for n in [F+'baseline.py',F+'protocol.md',F+'amendment-2026-09-06.md',GENERIC]:
            b = read_member(n); require(sha(b) == freeze['hashes'][n], 'Freeze mismatch: '+n)
        generic = read_member(GENERIC)
        rows = json.loads(read_member(F+'rankings-EMC.json'))
        by_id = {r['nct_id']:r for r in rows}
        require(len(rows) == len(by_id) == 6182, 'Rank population mismatch')
        ordered = {m:check_ranks(rows,m) for m in ['H','A']}
        tops = {m:{r['nct_id'] for r in ordered[m][:100]} for m in ordered}
        h,a = tops['H'],tops['A']; target = h^a
        require((len(h&a),len(a-h),len(h-a)) == (83,17,17), 'Unexpected comparison membership')
        boundary = {m:[{'nct_id':r['nct_id'], **r['methods'][m]} for r in ordered[m][99:101]] for m in ordered}
        require(all(r['rank_min'] == r['rank_max'] for rows_ in boundary.values() for r in rows_), 'Cutoff tie changed')
        promotions = sum(r['methods']['A']['rank_max']<=100 and r['methods']['H']['rank_min']>200 for r in rows)
        require(promotions == 13, 'Original screen statistic mismatch')
        index_raw = read_member(S+'corpus-index.json')
        require(sha(index_raw) == freeze['hashes'][S+'corpus-index.json'], 'Index freeze mismatch')
        index = json.loads(index_raw); expected_ids = {r['nct_id'] for r in index}
        require(len(index) == len(expected_ids) == 6182 and expected_ids == set(by_id), 'Index/rank mismatch')
        version_audit = json.loads(read_member(F+'version-audit.json'))
        candidates = defaultdict(list); union = set(); page_total=0; query_total=0
        manifests = sorted(n for n in z.namelist() if n.startswith(S+'sources/') and n.endswith('/manifest.json'))
        require(bool(manifests), 'No source manifests')
        for name in manifests:
            query_total += 1; raw = read_member(name)
            require(sha(raw) == freeze['hashes'][name], 'Source manifest freeze mismatch')
            m = json.loads(raw); require(m.get('complete') is True, 'Incomplete source query'); ids=[]
            for page in m['pages']:
                page_total += 1; member = S+page['file']; stored = read_member(member)
                require(sha(stored) == freeze['hashes'][member] == page['stored_sha256'], 'Stored page hash mismatch')
                require(len(stored) == page['stored_bytes'], 'Stored page length mismatch')
                raw = gzip.decompress(stored)
                require(sha(raw) == page['sha256'] and len(raw) == page['bytes'], 'Raw page mismatch')
                count = 0
                for ix,study,text,start,end in study_slices(raw):
                    count += 1; n = study['protocolSection']['identificationModule']['nctId']; ids.append(n); union.add(n)
                    if n in target:
                        version_key(study,page)
                        begin = len(text[:start].encode('utf-8')); finish = begin+len(text[start:end].encode('utf-8'))
                        record_raw = raw[begin:finish]
                        require(json.loads(record_raw) == study, 'Raw record extraction mismatch')
                        candidates[n].append((study,page,record_raw,{'archive_member':member,'json_pointer':'/studies/'+str(ix),
                            'byte_start':begin,'byte_end':finish,'page_raw_sha256':sha(raw),
                            'page_stored_sha256':sha(stored),'manifest_member':name}))
                require(count == page['count'], 'Page count mismatch')
            require(len(ids) == len(set(ids)) == m['total_count'] and sorted(ids) == m['ids'], 'Query IDs/count mismatch')
        require(union == expected_ids and set(candidates) == target, 'Source union/target mismatch')
        work = sorted(target,key=lambda n:(sha((SEED+'\n'+n).encode()),n))
        outputs = {'reader/reading-label-protocol.json':generic}; reader_rows=[]; mappings=[]
        for position,n in enumerate(work,1):
            cs = candidates[n]; study,page,raw,origin = select_version(cs)
            audit = {'selected_page':page['file'],'selected_record_sha256':sha(canonical(study)),
                'selected_version_key':list(version_key(study,page)),
                'distinct_record_sha256':sorted({sha(canonical(c[0])) for c in cs}),
                'source_pages':sorted({c[1]['file'] for c in cs})}
            require(audit == version_audit[n], 'Version audit mismatch: '+n)
            case = f'case-{position:03d}'; file = 'reader/records/'+case+'.json'; outputs[file] = raw
            reader_rows.append({'case_id':case,'file':'records/'+case+'.json','nct_id':n,'bytes':len(raw),
                'raw_sha256':sha(raw),'canonical_sha256':sha(canonical(study)),
                'registry_last_update_date':version_key(study,page)[0]})
            mappings.append({'case_id':case,'nct_id':n,'group':'entrant' if n in a-h else 'displaced',
                'H':by_id[n]['methods']['H'],'A':by_id[n]['methods']['A'],'selected_source':origin,
                'selected_raw_sha256':sha(raw),'selected_retrieved_at_utc':page['retrieved_at_utc'],
                'version_audit':audit,'candidate_occurrences':[{'page':c[1]['file'],
                    'version_key':list(version_key(c[0],c[1])),'canonical_sha256':sha(canonical(c[0])),
                    'raw_sha256':sha(c[2])} for c in sorted(cs,key=lambda c:c[1]['file'])]})
        reader_manifest = {'kind':'source-only-reader-packet','disease':'extraskeletal myxoid chondrosarcoma',
            'count':34,'records':reader_rows,'labels_present':False,
            'protocol_sha256':sha((HERE/'protocol.md').read_bytes()),
            'generic_protocol_sha256':sha(generic),'source_form':'complete exact raw archived study JSON objects'}
        outputs['reader/manifest.json'] = pretty(reader_manifest)
        packet = {'base_revision':BASE,'archive_path':'../trial-frozen-baseline-package-2026-09-06/frozen-experiment.zip',
            'archive_sha256':ARCHIVE_SHA,'archive_bytes':archive.stat().st_size,'archive_manifest_sha256':MANIFEST_SHA,
            'protocol_sha256':sha((HERE/'protocol.md').read_bytes()),'builder_sha256':sha(Path(__file__).read_bytes()),
            'generic_protocol_sha256':sha(generic),'reader_manifest_sha256':sha(outputs['reader/manifest.json']),
            'counts':{'corpus':6182,'hierarchy_top100':100,'augmented_top100':100,'common':83,'entrants':17,'displaced':17,'symmetric_difference':34},
            'original_screen':{'replacements':17,'replacement_threshold':20,'robust_200_to_100':13,
                'promotion_threshold':10,'conjunctive_pass':False,'pilot_opened':False},
            'tie_boundaries':boundary,'common_ids':sorted(h&a),'hierarchy_top100_ids':sorted(h),
            'augmented_top100_ids':sorted(a),'shuffle':{'seed':SEED,'rule':'sort (SHA256(UTF8(seed+newline+nct_id)), nct_id)'},
            'membership_and_provenance':mappings,'decoded_archive_members':dependencies,
            'checks':{'source_queries':query_total,'source_pages':page_total,'source_union_ids':len(union),
                'selected_versions_reconciled':34,'rank_methods_checked':['H','A'],'label_members_decoded':0},
            'outputs':{path:{'bytes':len(raw),'sha256':sha(raw)} for path,raw in outputs.items()}}
        outputs['coordinator/packet-manifest.json'] = pretty(packet)
        return outputs,packet

def build():
    outputs,packet = prepare()
    for rel,raw in outputs.items():
        dest = HERE/rel
        if dest.exists():
            require(dest.read_bytes() == raw, 'Refuse overwrite of changed frozen output: '+rel)
        else:
            dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw)
    receipt_path = HERE/'integrity-receipt.json'
    inventory = {p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
        for p in sorted(HERE.rglob('*')) if p.is_file() and p != receipt_path and '__pycache__' not in p.parts}
    receipt = {'status':'PREPARED_AWAITING_INDEPENDENT_METHODS_REVIEW_NO_READER_AUTHORIZATION',
        'created_utc':datetime.now(timezone.utc).isoformat(),'base_revision':BASE,'protocol_sha256':packet['protocol_sha256'],
        'packet_manifest_sha256':sha(outputs['coordinator/packet-manifest.json']),
        'files':inventory,'archive_sha256':ARCHIVE_SHA,'new_judgments':0,'label_outcomes_read':0,
        'original_pilot_run':False,'network_refresh':False,'scoring_or_reranking_run':False,
        'model':'gpt-6-astra inherited; exact backend not independently exposed','reasoning_effort':'inherited; not independently exposed',
        'scientific_seconds':None,'usage':None,'processes_left_running':False}
    if receipt_path.exists():
        verify()
    else:
        receipt_path.write_bytes(pretty(receipt))
    print(json.dumps({'status':'prepared','protocol_sha256':packet['protocol_sha256'],
        'packet_manifest_sha256':sha(outputs['coordinator/packet-manifest.json']),'checks':packet['checks']}))

def verify():
    receipt = json.loads((HERE/'integrity-receipt.json').read_bytes())
    actual_paths = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()
                    and p.name != 'integrity-receipt.json' and '__pycache__' not in p.parts}
    require(actual_paths == set(receipt['files']), 'Output inventory changed')
    for rel,meta in receipt['files'].items():
        raw = (HERE/rel).read_bytes()
        require(len(raw) == meta['bytes'] and sha(raw) == meta['sha256'], 'Frozen file mismatch: '+rel)
    outputs,packet = prepare()
    for rel,raw in outputs.items():
        require((HERE/rel).read_bytes() == raw, 'Non-reproducible output: '+rel)
    require(receipt['protocol_sha256'] == packet['protocol_sha256'] and
        receipt['packet_manifest_sha256'] == sha(outputs['coordinator/packet-manifest.json']), 'Receipt mismatch')
    print(json.dumps({'status':'PASS','reproduced_outputs':len(outputs),'frozen_files':len(receipt['files']),
        'checks':packet['checks'],'protocol_sha256':packet['protocol_sha256']}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['build','verify']); args=parser.parse_args()
    {'build':build,'verify':verify}[args.command]()
