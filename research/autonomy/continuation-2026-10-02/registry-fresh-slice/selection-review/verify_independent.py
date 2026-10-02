"""Sealed synthetic cases only. Hard-disable sockets before importing target."""
import hashlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from email.message import Message

HERE = Path(__file__).parent
TARGET = HERE.parent / 'checkpoint08-registry-acquisition'
network_attempts = []
def no_network(*args, **kwargs):
    network_attempts.append('blocked')
    raise AssertionError('Live network forbidden during independent verification')
socket.create_connection = no_network
socket.socket.connect = no_network
socket.socket.connect_ex = no_network
sys.path.insert(0, str(TARGET))
import acquire_metadata as a

class Response(io.BytesIO):
    def __init__(self, body, url, declared, status):
        super().__init__(body)
        self.url, self.status, self.read_calls = url, status, 0
        self.headers = Message()
        if declared is not None:
            self.headers['Content-Length'] = str(declared)
    def geturl(self):
        return self.url
    def read(self, count=-1):
        self.read_calls += 1
        return super().read(count)

fixture_path = HERE / 'independent-cases.json'
assert hashlib.sha256(fixture_path.read_bytes()).hexdigest() == '69106630850218ebe6bc39aae0cd447a43da733b6104ca1d752bc2bf1d370a82'
fixture = json.loads(fixture_path.read_bytes())
checks = []
for case in fixture['cases']:
    if case.get('stage'):
        checks.append({'id': case['id'], 'status': 'deferred', 'reason': 'Future selected-record acquisition is absent from metadata-only implementation; protocol projection-equality rule reviewed, not executed.'})
        continue
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:
        base = Path(tmp)
        ledger = base / 'ledger.json'
        ledger.write_text(json.dumps({'exclusionTrialIds': case['exclusions']}))
        calls, responses = [], []
        def fetch(url):
            index = len(calls)
            calls.append(url)
            page = case['pages'][index]
            records = [{'protocolSection': {'identificationModule': {'nctId': r['nctId']}, 'statusModule': {'resultsFirstPostDateStruct': {'date': r['resultsFirstPostDate']}}, 'conditionsModule': {'conditions': ['synthetic cancer']}}} for r in page['records']]
            payload = {'studies': records}
            if page['nextPageToken'] is not None:
                payload['nextPageToken'] = page['nextPageToken']
            body = json.dumps(payload).encode()
            transport = page['transport']
            declared = len(body)
            if 'contentLength' in transport:
                declared = transport['contentLength']
                body = b'x' * transport.get('actualBodyBytes', 0)
            response = Response(body, url, declared, transport['status'])
            responses.append(response)
            return response
        result = a.run(base / 'archive', ledger, fetch=fetch, enforce_headroom=False)
        expected = case['expected']
        wanted = 'metadata_frame_frozen' if expected['status'] == 'selected' else 'stopped'
        assert result['status'] == wanted, (case['id'], result)
        assert [r['nctId'] for r in result['selected']] == expected['selectedNctIds'], case['id']
        assert result['outcomeRequests'] == 0
        assert len(calls) <= 20
        assert result['rawBytes'] <= 1048576
        for index, url in enumerate(calls):
            assert url == a.query(None if index == 0 else case['pages'][index-1]['nextPageToken'])
        if 'pagesRead' in expected:
            assert len(calls) == expected['pagesRead'], case['id']
        if 'cutoffDate' in expected:
            assert result['cutoffDate'] == expected['cutoffDate']
        if expected.get('completeSource') is False:
            assert result['pages'][0]['bodyComplete'] is False
        if 'bodyBytesRead' in expected:
            assert result['rawBytes'] == expected['bodyBytesRead']
            assert responses[0].read_calls == 0
        if 'maxRetainedBodyBytes' in expected:
            assert result['rawBytes'] <= expected['maxRetainedBodyBytes']
        checks.append({'id': case['id'], 'status': 'passed', 'mockRequests': len(calls), 'observedStatus': result['status'], 'selectedNctIds': [r['nctId'] for r in result['selected']]})

suite = unittest.defaultTestLoader.discover(str(TARGET), pattern='test_acquire_metadata.py')
unit_result = unittest.TextTestRunner(verbosity=1).run(suite)
assert unit_result.wasSuccessful()
assert not network_attempts
report = {'sealedFixtureSHA256': hashlib.sha256(fixture_path.read_bytes()).hexdigest(), 'implementationSHA256': hashlib.sha256((TARGET / 'acquire_metadata.py').read_bytes()).hexdigest(), 'protocolSHA256': hashlib.sha256((TARGET / 'protocol.json').read_bytes()).hexdigest(), 'authorTestsSHA256': hashlib.sha256((TARGET / 'test_acquire_metadata.py').read_bytes()).hexdigest(), 'independentCases': checks, 'authorUnitTestsRun': unit_result.testsRun, 'authorUnitTestsPassed': unit_result.wasSuccessful(), 'networkAttempts': len(network_attempts), 'guard': 'socket.create_connection, socket.socket.connect/connect_ex hard-disabled before target import; all acquisition runs injected synthetic fetch', 'scope': 'No live CT.gov compatibility/network/headroom execution claim; selected future record drift test deferred until later separately authorized implementation exists.'}
(HERE / 'focused-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'independentPassed': sum(x['status'] == 'passed' for x in checks), 'independentDeferred': sum(x['status'] == 'deferred' for x in checks), 'authorTests': unit_result.testsRun, 'networkAttempts': len(network_attempts)}))
