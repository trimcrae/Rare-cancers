"""One-record administrative correction. No file/new-version operations exist here."""
import argparse
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

RECORD = 22986104
CONCEPT = '22028915'
DOI = '10.5281/zenodo.22986104'
FILE = 'EMC-junction-provenance-data-and-code.zip'
SIZE = 553892
MD5 = '4d150a8714aae8c875d7e93741dc3183'
SHA = 'cde2778bc1673436674c55165f25f2562ba3e7a0191c5c57555628386b16aaf8'
OLD = ('Built by scripts/zenodo_deposit.py from zenodo-manifest.json. '
       'Not published by this run: this invocation only reserves the DOI and refreshes the draft.')
NEW = 'Built by scripts/zenodo_deposit.py from zenodo-manifest.json.'
API = 'https://zenodo.org/api'
DEP = API + '/deposit/depositions/' + str(RECORD)
PUB = API + '/records/' + str(RECORD)
CONTENT = PUB + '/files/' + FILE + '/content'
AUTHORITY = 'research/autonomy/publication-authority.json'
BRANCH = 'refs/heads/codex/aso-notes-20260927'
OWNED_EDIT_RUN = 36298377308
# Canonical JSON digest of the actual authenticated GET saved after this run's
# successful edit (no PUT followed). Only that exact edit may be resumed.
OWNED_EDIT_SHA256 = '1e8064435ad8df966b75be4a08c3132bff08ab142a2bafc4b1e2b56ce3a95b0b'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dump(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, token, out):
        self.token = token
        self.out = out
        self.index = 0
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, method, url, body=None, auth=False):
        allowed = {('GET', DEP, True), ('GET', PUB, False), ('GET', CONTENT, False),
                   ('POST', DEP + '/actions/edit', True), ('PUT', DEP, True),
                   ('POST', DEP + '/actions/publish', True)}
        require((method, url, auth) in allowed, 'Endpoint/method/auth not allowed')
        require(body is None or (method == 'PUT' and url == DEP), 'Unexpected request body')
        self.index += 1
        prefix = self.out / f'{self.index:02d}'
        receipt = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'method': method, 'url': url, 'authenticated': auth,
                   'response_observed': False, 'automatic_retry': False}
        # Save intent before any network operation. A timeout is not replayed.
        dump(prefix.with_suffix('.request.json'), {**receipt, 'body': body})
        headers = {'User-Agent': 'EMC-ASO-notes-correction', 'Accept': 'application/json'}
        if auth:
            headers['Authorization'] = 'Bearer ' + self.token
        data = None if body is None else json.dumps(body).encode('utf-8')
        if data is not None:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, headers=headers, data=data, method=method)
        try:
            with self.opener.open(req, timeout=45) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
                require(len(raw) <= 2 * 1024 * 1024, 'Response exceeds 2 MiB cap')
                receipt.update(response_observed=True, status=response.status,
                               bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                prefix.with_suffix('.response.bin' if url == CONTENT else '.response.json').write_bytes(raw)
                expected = 201 if url.endswith('/edit') else 202 if url.endswith('/publish') else 200
                require(response.status == expected, 'Unexpected HTTP success status')
                return raw if url == CONTENT else json.loads(raw)
        except urllib.error.HTTPError as error:
            receipt.update(response_observed=True, status=error.code, error_type=type(error).__name__)
            prefix.with_suffix('.error.txt').write_bytes(error.read(100000))
            raise RuntimeError(f'HTTP {error.code}; inspect saved state before any further mutation') from None
        except Exception as error:
            receipt['error_type'] = type(error).__name__
            receipt['recovery'] = 'Read provider state; do not blindly retry or discard.'
            raise
        finally:
            dump(prefix.with_suffix('.receipt.json'), receipt)


def identity(record, state=None):
    require(str(record.get('id')) == str(RECORD), 'Wrong record')
    require(str(record.get('conceptrecid')) == CONCEPT, 'Wrong concept')
    require(record.get('doi') == DOI, 'Wrong DOI')
    require(record.get('submitted') is True, 'Record has not been published')
    if state is not None:
        require(record.get('state') == state, 'Foreign or unexpected editing state')
    files = record.get('files', [])
    require(len(files) == 1, 'Wrong file count')
    file = files[0]
    require(file.get('filename', file.get('key')) == FILE, 'Wrong filename')
    require(file.get('filesize', file.get('size')) == SIZE, 'Wrong file size')
    require(file.get('checksum', '').removeprefix('md5:') == MD5, 'Wrong file checksum')


def public_matches(record, expected, note):
    identity(record, 'done')
    metadata = copy.deepcopy(expected['metadata'])
    metadata['notes'] = note
    require(record['metadata'] == metadata, 'Unexpected public metadata delta')
    for key in ('doi', 'conceptdoi', 'conceptrecid', 'id', 'files'):
        require(record.get(key) == expected.get(key), 'Unexpected public ' + key + ' delta')


def editable_metadata(metadata):
    result = copy.deepcopy(metadata)
    # This provider-generated DOI reservation object is a response field, not a
    # request to reserve another DOI. The already registered DOI is retained.
    reserved = result.pop('prereserve_doi', None)
    if reserved is not None:
        require(isinstance(reserved, dict) and reserved.get('doi') == DOI,
                'Unexpected reserved DOI')
        require(str(reserved.get('recid')) == str(RECORD), 'Unexpected reserved record')
    return result


def validate_deposition_metadata(record, expected, note):
    actual = editable_metadata(record['metadata'])
    public = copy.deepcopy(expected['metadata'])
    public.pop('relations')  # Provider-owned public version relationship.
    resource = public.pop('resource_type')
    require(resource['type'] == 'dataset', 'Expected a dataset')
    public['upload_type'] = 'dataset'
    public['license'] = public['license']['id']
    # Observed authenticated representation adds Zenodo's publisher field; it
    # is absent from the public Records JSON. Preserve it in every PUT.
    public['imprint_publisher'] = 'Zenodo'
    public['notes'] = note
    # All remaining fields must match exactly; unfamiliar transformations fail
    # before editing instead of silently dropping scientific/attribution fields.
    require(actual == public, 'Authenticated metadata differs from public baseline')
    return actual


def verify_bytes(client):
    raw = client.request('GET', CONTENT)
    require(len(raw) == SIZE and hashlib.sha256(raw).hexdigest() == SHA,
            'Public archive bytes changed')
    require(hashlib.md5(raw).hexdigest() == MD5, 'Public archive MD5 changed')


def edit_state_digest(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def comparable_files(record):
    files = copy.deepcopy(record['files'])
    for file in files:
        suffix = '/files/' + file['id']
        # Observed edit response changes only this provider self-link prefix.
        # All file IDs, download links, names, sizes and checksums stay compared.
        require(file['links']['self'] in (PUB + suffix, DEP + suffix), 'Unexpected file self link')
        file['links']['self'] = PUB + suffix
    return files


def run(client, expected, apply=False, resume=False):
    require(not resume or apply, 'Owned-edit continuation requires apply mode')
    public_before = client.request('GET', PUB)
    deposition_before = client.request('GET', DEP, auth=True)
    identity(deposition_before, 'inprogress' if resume else 'done')
    if resume:
        require(edit_state_digest(deposition_before) == OWNED_EDIT_SHA256,
                'Editable state differs from the recorded owned edit; refuse continuation')
    note = public_before.get('metadata', {}).get('notes')
    require(note in (OLD, NEW), 'Unexpected note; refuse to overwrite another edit')
    public_matches(public_before, expected, note)
    baseline = validate_deposition_metadata(deposition_before, expected, note)
    verify_bytes(client)
    if note == NEW:
        return {'status': 'verified_noop', 'notes': NEW, 'mutations': 0}
    if not apply:
        return {'status': 'inspected', 'notes': OLD, 'mutations': 0}

    if resume:
        current = deposition_before
    else:
        edited = client.request('POST', DEP + '/actions/edit', auth=True)
        identity(edited, 'inprogress')
        current = client.request('GET', DEP, auth=True)
    identity(current, 'inprogress')
    require(editable_metadata(current['metadata']) == baseline, 'Intervening edit before PUT')
    require(comparable_files(current) == comparable_files(deposition_before), 'Files changed during edit')
    payload = copy.deepcopy(baseline)
    payload['notes'] = NEW
    changed = [key for key in set(payload) | set(baseline) if payload.get(key) != baseline.get(key)]
    require(changed == ['notes'], 'Planned metadata delta is not notes only')
    updated = client.request('PUT', DEP, {'metadata': payload}, auth=True)
    identity(updated, 'inprogress')
    require(editable_metadata(updated['metadata']) == payload, 'Unexpected PUT response metadata')
    current = client.request('GET', DEP, auth=True)
    identity(current, 'inprogress')
    require(editable_metadata(current['metadata']) == payload, 'Unexpected saved metadata')
    require(comparable_files(current) == comparable_files(deposition_before), 'Files changed before publish')
    # The public view must still be the saved baseline while metadata is edited.
    public_matches(client.request('GET', PUB), expected, OLD)
    published = client.request('POST', DEP + '/actions/publish', auth=True)
    identity(published)
    require(editable_metadata(published['metadata']) == payload, 'Unexpected publish metadata')
    # 202 can mean processing; a not-yet-integrated response fails into read-only
    # reconciliation. It never triggers another POST.
    public_after = client.request('GET', PUB)
    public_matches(public_after, expected, NEW)
    verify_bytes(client)
    return {'status': 'corrected_and_publicly_verified', 'notes': NEW, 'mutations': 2 if resume else 3,
            'resumed_edit_from_run': OWNED_EDIT_RUN if resume else None,
            'record': RECORD, 'concept': CONCEPT, 'doi': DOI, 'archive_sha256': SHA,
            'metadata_delta': ['notes'], 'files_changed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['inspect', 'apply', 'resume-owned-edit'], default='inspect')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Receipt directory must be new')
    require(os.environ.get('GITHUB_REF') == BRANCH, 'Wrong workflow branch')
    require(os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch', 'Manual dispatch required')
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    require(sha == os.environ.get('EXPECTED_SHA') == os.environ.get('GITHUB_SHA'), 'Wrong resolved SHA')
    grant = json.loads(Path(AUTHORITY).read_text(encoding='utf-8'))['zenodo_archive_publication']
    require(grant.get('standing_grant') is True and grant.get('approval_is_required_per_publication') is False,
            'Existing standing authority no longer applies')
    require(bool(os.environ.get('AUTHORITY_RECORD')), 'Audit authority attribution required')
    token = os.environ.get('ZENODO_TOKEN')
    require(bool(token), 'Existing CI token unavailable')
    expected = json.loads(Path(__file__).with_name('expected-public-record.json').read_text(encoding='utf-8'))
    args.out.mkdir(parents=True)
    dump(args.out / 'intent.json', {'sha': sha, 'mode': args.mode, 'record': RECORD,
         'old_notes': OLD, 'new_notes': NEW, 'authority': os.environ['AUTHORITY_RECORD'],
         'resumed_edit_from_run': OWNED_EDIT_RUN if args.mode == 'resume-owned-edit' else None,
         'required_owned_edit_sha256': OWNED_EDIT_SHA256 if args.mode == 'resume-owned-edit' else None,
         'authority_file_sha256': hashlib.sha256(Path(AUTHORITY).read_bytes()).hexdigest(),
         'baseline_file_sha256': hashlib.sha256(Path(__file__).with_name('expected-public-record.json').read_bytes()).hexdigest()})
    try:
        result = run(Client(token, args.out), expected, apply=args.mode != 'inspect',
                     resume=args.mode == 'resume-owned-edit')
    except Exception as error:
        dump(args.out / 'outcome.json', {'status': 'stopped_for_reconciliation',
             'error_type': type(error).__name__, 'message': str(error),
             'instruction': 'Inspect receipt and GET provider state before further mutation; no automatic retry or discard.'})
        raise
    dump(args.out / 'outcome.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
