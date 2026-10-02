"""Independent actual-frame validation, standard library only; no source acquisition."""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.parse
import zipfile

HERE=Path(__file__).resolve().parent
ARCHIVE=HERE.parent/'checkpoint08-root'/'registry-fresh-metadata.zip'
EXPECTED='7c6ffad5d0807abcf344b4de1c9a837eaab324f12ea087c63890dc6d6204e99e'
def sha(b): return hashlib.sha256(b).hexdigest()
def pairs(items):
    d={}
    for k,v in items:
        assert k not in d, 'duplicate JSON key'
        d[k]=v
    return d
def parse(b): return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
def canon(o): return json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
raw=ARCHIVE.read_bytes()
assert len(raw)==48075 and sha(raw)==EXPECTED
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    names=z.namelist()
    assert len(names)==len(set(names))
    def b(n): return z.read(n)
    def j(n): return parse(b(n))
    receipt=j('source/receipt.json')
    protocol=j('source/protocol.json')
    freeze=j('freeze.json')
    execution=j('execution.json')
    selected=j('source/selected-metadata.json')
    exclusions=j('source/exclusions.json')
    assert execution['revision']=='ab765336689e46f3dce7870824315545ca6c6c91'
    assert execution['run_id']=='37067615876' and execution['status']=='completed'
    assert all(x['exit_code']==0 and x['forced_stop'] is None for x in execution['steps'])
    for file,key in [('source/exclusions.json','exclusionSHA256'),('source/protocol.json','protocolSHA256'),('source/selected-metadata.json','selectedMetadataSHA256')]:
        assert sha(b(file))==receipt[key]
    assert receipt['exclusionSHA256']=='2058753adf3ceb52050d5e4657f30b3bf39755200a22256d1fa1c93085668bf1'
    frozen={x['path']:x['sha256'] for x in freeze['files']}
    for src,key in [('source/exclusions.json','exposure/exclusion-ledger.json'),('source/protocol.json','acquisition/protocol.json'),('synthetic/checkpoint08-registry-acquisition/acquire_metadata.py','acquisition/acquire_metadata.py')]:
        assert sha(b(src))==frozen[key]
    assert receipt['implementationSHA256']==frozen['acquisition/acquire_metadata.py']
    excluded=exclusions['exclusionTrialIds']
    assert len(excluded)==len(set(excluded))==148
    assert excluded==sorted(set(exclusions['baselineTrialIds'])|set(exclusions['selectedPreviouslyAcquiredTrialIds']))
    assert len(set(exclusions['baselineTrialIds']))==138
    assert len(set(exclusions['selectedPreviouslyAcquiredTrialIds']))==10
    assert all(re.fullmatch(r'NCT[0-9]{8}',v) for v in excluded)
    assert dt.datetime.fromisoformat(freeze['frozenUTC'].replace('Z','+00:00')) < dt.datetime.fromisoformat(receipt['startedUTC'])
    observed=[]; projections={}; dates=[]; token=None; tokens=set(); total=0; pages=[]
    expected_names={f'source/page-{i:02d}.raw.json' for i in range(len(receipt['pages']))}
    assert {n for n in names if re.fullmatch(r'source/page-[0-9]+.raw.json',n)}==expected_names
    for i,p in enumerate(receipt['pages']):
        rawpage=b(f'source/page-{i:02d}.raw.json')
        page=parse(rawpage)
        assert p['index']==i and p['requestToken']==token
        assert p['bodyComplete'] is True and p['status']==200 and p['responseURL']==p['url']
        assert len(rawpage)==p['bytes'] and sha(rawpage)==p['sha256']
        assert len(rawpage)<=65536
        headers={k.lower():v for k,v in p['headers']}
        assert headers.get('content-encoding','identity')=='identity'
        assert 'application/json' in headers['content-type']
        parts=urllib.parse.urlsplit(p['url'])
        assert parts.scheme+'://'+parts.netloc+parts.path==protocol['endpoint']
        query=urllib.parse.parse_qsl(parts.query,keep_blank_values=True)
        assert len(query)==len(dict(query))
        expected=dict(protocol['parameters'])
        if token is not None: expected['pageToken']=token
        assert dict(query)==expected
        assert set(page)<= {'studies','nextPageToken','totalCount'}
        assert isinstance(page['studies'],list) and len(page['studies'])<=10
        page_dates=[]
        for k,study in enumerate(page['studies']):
            assert set(study)=={'protocolSection'}, 'unexpected outcome/nonmetadata module'
            projection=study['protocolSection']
            assert set(projection)=={'identificationModule','statusModule','conditionsModule'}
            assert all(type(v) is dict for v in projection.values())
            nid=projection['identificationModule']['nctId']
            date=projection['statusModule']['resultsFirstPostDateStruct']['date']
            assert type(nid) is str and re.fullmatch(r'NCT[0-9]{8}',nid) and nid not in projections
            assert type(date) is str and dt.date.fromisoformat(date).isoformat()==date
            assert '2026-09-01'<=date<='2026-09-30'
            assert not dates or dates[-1]<=date
            dates.append(date);page_dates.append(date);projections[nid]=projection
            observed.append(dict(nctId=nid,resultsFirstPostDate=date,excluded=nid in excluded,pageIndex=i,studyIndex=k,metadataSHA256=sha(canon(projection))))
        token=page.get('nextPageToken')
        assert token==p['nextPageToken']
        if token is not None:
            assert type(token) is str and token and token not in tokens
            tokens.add(token)
        assert dt.datetime.fromisoformat(p['startedUTC'])<=dt.datetime.fromisoformat(p['endedUTC'])
        total+=len(rawpage)
        candidates=sorted((r for r in observed if not r['excluded']),key=lambda r:(r['resultsFirstPostDate'],r['nctId']))
        cutoff=candidates[9]['resultsFirstPostDate'] if len(candidates)>=10 else None
        complete=token is None or (cutoff is not None and dates[-1]>cutoff)
        assert complete==(i==len(receipt['pages'])-1), 'not first permitted stopping page'
        pages.append(dict(index=i,records=len(page['studies']),bytes=len(rawpage),sha256=sha(rawpage),minDate=min(page_dates),maxDate=max(page_dates)))
    assert len(pages)<=20 and len(observed)<=200 and total<=1048576
    assert observed==receipt['observedRecords']
    assert total==receipt['rawBytes']
    expected=candidates[:10]
    assert expected==receipt['selected'] and len(expected)==10
    assert selected=={r['nctId']:projections[r['nctId']] for r in expected}
    assert receipt['candidateCount']==len(candidates)
    assert receipt['cutoffDate']==cutoff and receipt['cutoffTieComplete'] is True
    assert receipt['termination']=='strictly_later_date_observed' and dates[-1]>cutoff
    assert receipt['outcomeRequests']==0 and receipt['status']=='metadata_frame_frozen'
    result=dict(schema='independent-actual-metadata-frame-review/1',status='passed',completedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),owner='/root/registry_exposure_audit',archiveSHA256=EXPECTED,receiptSHA256=sha(b('source/receipt.json')),scriptSHA256=sha(Path(__file__).read_bytes()),executionRevision=execution['revision'],runId=execution['run_id'],pages=pages,recordsValidated=len(observed),rawBytes=total,exclusions=148,excludedObserved=sum(r['excluded'] for r in observed),candidates=len(candidates),selected=[dict(nctId=r['nctId'],date=r['resultsFirstPostDate']) for r in expected],cutoffDate=cutoff,cutoffTieObservedCount=sum(d==cutoff for d in dates),laterDateEvidence=min(d for d in dates if d>cutoff),allFetchedRecordsValidated=True,metadataProjectionsMatch=True,noOutcomeModulesInActualSource=True,noHTTPCallsByReviewer=True,classifierInvocations=0,scope='Actual archived raw pages independently parsed and selections recomputed; no production acquisition or selection code imported/executed. Source receipt compared to raw bytes, exact archived freeze and exclusions.',limitations=['Observed acquisition-time metadata frame, not atomic database snapshot; undetected insertion/update drift and global completeness cannot be certified.','148-ID disjointness is against the frozen documented exclusion ledger, not all historical retrievals or model training.','Archive and timestamp consistency does not independently authenticate server origin or historical commit time.','No outcomes acquired or examined; no semantic evaluation or classifier accuracy claim.'])
(HERE/'review-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','recordsValidated','rawBytes','excludedObserved','candidates','selected','cutoffDate','cutoffTieObservedCount','laterDateEvidence']}))

