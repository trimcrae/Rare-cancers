"""Frozen metadata-frame acquisition; no outcomes and no classifier execution."""
import argparse
import datetime as dt
import hashlib
import http.client
import json
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://clinicaltrials.gov/api/v2/studies'
PARAMS = [('query.cond', 'cancer'), ('query.term', 'AREA[ResultsFirstPostDate]RANGE[2026-09-01,2026-09-30]'), ('pageSize', '10'), ('sort', 'ResultsFirstPostDate:asc'), ('format', 'json'), ('fields', 'IdentificationModule,StatusModule,ConditionsModule')]
PAGES, RECORDS, PAGE_BYTES, TOTAL_BYTES = 20, 200, 65536, 1048576
MODULES = {'identificationModule', 'statusModule', 'conditionsModule'}
LIMITATION = 'Archived acquisition-time metadata frame; not an atomic snapshot or proof of live-population completeness. Undetected insertion/update drift remains possible.'

class Stop(Exception):
    pass

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')

def write(path, obj):
    path.write_bytes(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False).encode('utf-8') + b'\n')

def unique_object(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise Stop('duplicate JSON key: ' + k)
        result[k] = v
    return result

def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=lambda x: (_ for _ in ()).throw(Stop('nonfinite JSON')))

def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r'NCT[0-9]{8}', value) is not None

def query(token=None):
    return BASE + '?' + urllib.parse.urlencode(PARAMS + ([] if token is None else [('pageToken', token)]))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def transport(url):
    """One request, no redirect/retry. Return a streaming response, including HTTP errors."""
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={'Accept': 'application/json', 'Accept-Encoding': 'identity', 'User-Agent': 'EMC-registry-metadata-frame/1'})
    try:
        return opener.open(request, timeout=30)
    except urllib.error.HTTPError as error:
        return error

def inspect_study(study):
    if not isinstance(study, dict) or set(study) - {'protocolSection', 'hasResults'}:
        raise Stop('unexpected study fields; metadata schema drift')
    if 'hasResults' in study and type(study['hasResults']) is not bool:
        raise Stop('invalid hasResults')
    protocol = study.get('protocolSection')
    if not isinstance(protocol, dict) or set(protocol) != MODULES or any(not isinstance(v, dict) for v in protocol.values()):
        raise Stop('missing/unexpected metadata modules')
    nct = protocol['identificationModule'].get('nctId')
    date_struct = protocol['statusModule'].get('resultsFirstPostDateStruct')
    date = date_struct.get('date') if isinstance(date_struct, dict) else None
    if not valid_id(nct) or not isinstance(date, str) or not re.fullmatch(r'2026-09-[0-9]{2}', date):
        raise Stop('invalid identity/date')
    try:
        dt.date.fromisoformat(date)
    except ValueError as error:
        raise Stop('invalid calendar date') from error
    return nct, date, sha(canonical(protocol))

def run(output_dir, exclusion_file, fetch=transport, enforce_headroom=True):
    """Mockable transport. Creates a fresh archive directory; failures retain evidence."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'schema': 'registry-metadata-frame/1', 'status': 'started', 'startedUTC': utc(), 'pages': [], 'observedRecords': [], 'selected': [], 'limitation': LIMITATION, 'outcomeRequests': 0}
    try:
        if enforce_headroom and shutil.disk_usage(output).free < 10 * 1024**3 + 20 * 1024**2:
            raise Stop('headroom: requires 10 GiB free plus 20 MiB archive budget')
        exclusion_raw = Path(exclusion_file).read_bytes()
        if len(exclusion_raw) > 65536:
            raise Stop('exclusion input exceeds 64 KiB')
        excluded_doc = parse(exclusion_raw)
        ids = excluded_doc.get('exclusionTrialIds') if isinstance(excluded_doc, dict) else None
        if not isinstance(ids, list) or any(not valid_id(x) for x in ids) or len(set(ids)) != len(ids):
            raise Stop('invalid exclusion ledger')
        excluded = set(ids)
        (output / 'exclusions.json').write_bytes(exclusion_raw)
        receipt['exclusionSHA256'] = sha(exclusion_raw)
        receipt['implementationSHA256'] = sha(Path(__file__).read_bytes())
        protocol_path = Path(__file__).with_name('protocol.json')
        protocol_raw = protocol_path.read_bytes()
        (output / 'protocol.json').write_bytes(protocol_raw)
        receipt['protocolSHA256'] = sha(protocol_raw)
        token, seen_tokens, seen_ids, previous_date, total = None, set(), set(), None, 0
        projections = {}
        for page_index in range(PAGES):
            if total >= TOTAL_BYTES:
                raise Stop('aggregate byte budget exhausted before cutoff tie completion or pagination exhaustion')
            url = query(token)
            page = {'index': page_index, 'url': url, 'requestToken': token, 'startedUTC': utc(), 'bodyComplete': False}
            receipt['pages'].append(page)
            raw_path = output / ('page-%02d.raw.json' % page_index)
            # Persist the attempted URL before opening the connection.
            write(output / 'receipt.json', receipt)
            response = None
            body = bytearray()
            try:
                response = fetch(url)
                page['status'] = response.status
                page['headers'] = list(response.headers.items())
                page['responseURL'] = response.geturl()
                if response.geturl() != url:
                    raise Stop('redirect/access drift')
                encoding = response.headers.get('Content-Encoding', 'identity').lower()
                if encoding != 'identity':
                    raise Stop('encoded response rejected before body')
                lengths = [v for k, v in page['headers'] if k.lower() == 'content-length']
                capacity = min(PAGE_BYTES, TOTAL_BYTES - total)
                if capacity <= 0:
                    raise Stop('aggregate byte budget exhausted')
                if len(lengths) > 1 or (lengths and not re.fullmatch(r'[0-9]+', lengths[0])):
                    raise Stop('ambiguous/invalid Content-Length')
                declared = int(lengths[0]) if lengths else None
                page['declaredBytes'] = declared
                if declared is not None and declared > capacity:
                    raise Stop('declared response exceeds byte budget; body not acquired')
                limit = capacity if declared is None else declared
                while len(body) < limit:
                    try:
                        chunk = response.read(min(8192, limit - len(body)))
                    except http.client.IncompleteRead as error:
                        body.extend(error.partial)
                        raise Stop('incomplete HTTP body; partial bytes retained') from error
                    if not chunk:
                        if declared is None:
                            break
                        raise Stop('incomplete body')
                    body.extend(chunk)
                if declared is None and len(body) == capacity:
                    raise Stop('undeclared body reached byte cap; diagnostic prefix only')
                page['bodyComplete'] = True
            finally:
                if response is not None:
                    response.close()
                page['endedUTC'] = utc()
                page['bytes'] = len(body)
                page['sha256'] = sha(body)
                total += len(body)
                receipt['rawBytes'] = total
                raw_path.write_bytes(body)
            if page['status'] != 200:
                raise Stop('HTTP access failure: ' + str(page['status']))
            payload = parse(body)
            if not isinstance(payload, dict) or set(payload) - {'studies', 'nextPageToken', 'totalCount'}:
                raise Stop('page schema drift')
            studies = payload.get('studies')
            if not isinstance(studies, list) or len(studies) > 10:
                raise Stop('page record cap/schema failure')
            if len(receipt['observedRecords']) + len(studies) > RECORDS:
                raise Stop('record budget failure')
            for index, study in enumerate(studies):
                nct, date, digest = inspect_study(study)
                if nct in seen_ids:
                    raise Stop('duplicate trial/possible pagination drift: ' + nct)
                if previous_date is not None and date < previous_date:
                    raise Stop('nonmonotone date/possible pagination drift')
                seen_ids.add(nct)
                previous_date = date
                projections[nct] = study['protocolSection']
                receipt['observedRecords'].append({'nctId': nct, 'resultsFirstPostDate': date, 'excluded': nct in excluded, 'pageIndex': page_index, 'studyIndex': index, 'metadataSHA256': digest})
            next_token = payload.get('nextPageToken')
            if 'nextPageToken' in payload and (not isinstance(next_token, str) or not next_token or next_token in seen_tokens):
                raise Stop('invalid/repeated pagination token')
            page['nextPageToken'] = next_token
            candidates = sorted((r for r in receipt['observedRecords'] if not r['excluded']), key=lambda r: (r['resultsFirstPostDate'], r['nctId']))
            cutoff = candidates[9]['resultsFirstPostDate'] if len(candidates) >= 10 else None
            complete = next_token is None or (cutoff is not None and previous_date > cutoff)
            if complete:
                write(output / 'selected-metadata.json', {r['nctId']: projections[r['nctId']] for r in candidates[:10]})
                receipt['selectedMetadataSHA256'] = sha((output / 'selected-metadata.json').read_bytes())
                receipt.update(status='metadata_frame_frozen', selected=candidates[:10], cutoffDate=cutoff, termination='pagination_exhausted' if next_token is None else 'strictly_later_date_observed', candidateCount=len(candidates), cutoffTieComplete=True)
                break
            if next_token is not None:
                seen_tokens.add(next_token)
            token = next_token
        else:
            raise Stop('page budget exhausted before cutoff tie completion or pagination exhaustion')
    except Exception as error:
        receipt.update(status='stopped', selected=[], errorType=type(error).__name__, error=str(error), cutoffTieComplete=False)
    finally:
        receipt['endedUTC'] = utc()
        write(output / 'receipt.json', receipt)
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--exclusion-file', required=True)
    args = parser.parse_args()
    result = run(args.output_dir, args.exclusion_file)
    print(json.dumps({'status': result['status'], 'selectedCount': len(result['selected']), 'error': result.get('error')}))
    return 0 if result['status'] == 'metadata_frame_frozen' else 2

if __name__ == '__main__':
    raise SystemExit(main())
