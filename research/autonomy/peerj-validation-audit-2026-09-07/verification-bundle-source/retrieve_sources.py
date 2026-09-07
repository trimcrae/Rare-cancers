"""Retrieve frozen originals separately under their original terms; no relicensing.

Use --plan to inspect URLs/hashes without network access. Existing files are
reused only if their bytes and hashes match; mismatches are never overwritten.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import io
import json
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def require(condition,message):
    if not condition: raise ValueError(message)

def preserve_transport(path,blob):
    if path.exists():
        require(path.read_bytes()==blob,'Existing hash-named transport differs; file left unchanged')
    else:
        with path.open('xb') as stream:
            stream.write(blob)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',default='../local-original-sources',help='Original-source directory outside this supplement')
    parser.add_argument('--plan',action='store_true',help='Validate and print retrieval plan; make no network calls or file writes')
    args=parser.parse_args()
    destination=(ROOT/args.sources).resolve()
    require(not destination.is_relative_to(ROOT),'Original sources must stay outside this supplement directory')
    data=json.loads((ROOT/'retrieval-sources.json').read_text(encoding='utf-8'))
    sources=data['sources']
    require(len(sources)==4 and len({r['file'] for r in sources})==4,'Expected four distinct originals')
    for row in sources:
        require(Path(row['file']).name==row['file'],'Source filename must be a plain basename')
        require(row['url'].startswith('https://'),'Only HTTPS original URLs are supported')
        require(len(row['sha256'])==64 and row['bytes']>0,'Incomplete expected file identity')
    if args.plan:
        print(json.dumps({'mode':'plan_only','network_requests':0,'files_written':0,'sources':sources},indent=2))
        return
    destination.mkdir(parents=True,exist_ok=True)
    receipts=[]
    try:
        for row in sources:
            target=destination/row['file']
            record={'file':row['file'],'url':row['url'],'rights':row['rights'],'started_utc':datetime.now(timezone.utc).isoformat()}
            receipts.append(record)
            if target.exists():
                blob=target.read_bytes()
                require(len(blob)==row['bytes'] and sha(blob)==row['sha256'],'Existing source mismatch; file left unchanged: '+row['file'])
                record.update(status='reused_matching_local_file',bytes=len(blob),sha256=sha(blob))
                continue
            is_container='archive_member' in row
            byte_bound=row['container_download_max_bytes'] if is_container else row['bytes']
            request=urllib.request.Request(row['url'],headers={'User-Agent':'GEO-metadata-reproduction/1.0'})
            with urllib.request.urlopen(request,timeout=60) as response:
                require(response.status==200,'Original source HTTP status is not 200')
                require(response.url.startswith('https://'),'Unexpected non-HTTPS redirect')
                pieces=[];count=0
                while True:
                    chunk=response.read(min(1024*1024,byte_bound+1-count))
                    if not chunk: break
                    count+=len(chunk)
                    require(count<=byte_bound,'Original source exceeds explicit download bound; no source file written')
                    pieces.append(chunk)
                raw=b''.join(pieces)
                record.update(http_status=response.status,final_url=response.url,retrieved_bytes=len(raw),retrieved_sha256=sha(raw))
            if is_container:
                record.update(container_reference_bytes=row['container_reference_bytes'],container_reference_sha256=row['container_reference_sha256'],
                              container_matches_reference=(len(raw)==row['container_reference_bytes'] and sha(raw)==row['container_reference_sha256']),
                              container_download_max_bytes=byte_bound,container_identity_role='Transport provenance; exact named member identity remains mandatory')
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    require(archive.namelist().count(row['archive_member'])==1,'Expected exactly one named Figure S6 member')
                    info=archive.getinfo(row['archive_member'])
                    require(info.file_size==row['bytes'],'Figure member size mismatch')
                    blob=archive.read(info)
                record['archive_member']=row['archive_member']
                record['archive_member_timestamp']=list(info.date_time)
                transport=destination/'transport'
                transport.mkdir(exist_ok=True)
                transport_file=transport/('supplementaryFiles-'+sha(raw)+'.zip')
                preserve_transport(transport_file,raw)
                record['transport_file']='transport/'+transport_file.name
            else:
                require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Original download differs from frozen identity; no source file written')
                blob=raw
            require(len(blob)==row['bytes'] and sha(blob)==row['sha256'],'Original file/member hash mismatch')
            with target.open('xb') as stream:
                stream.write(blob)
            record.update(status='downloaded_and_verified',bytes=len(blob),sha256=sha(blob),finished_utc=datetime.now(timezone.utc).isoformat())
    finally:
        # Receipt lives with downloaded originals, never inside the supplement.
        (destination/'retrieval-receipt.json').write_text(json.dumps({'source_terms_unchanged':True,'records':receipts},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'verified_original_files':len(receipts),'source_terms_unchanged':True},indent=2))

if __name__=='__main__':
    main()
