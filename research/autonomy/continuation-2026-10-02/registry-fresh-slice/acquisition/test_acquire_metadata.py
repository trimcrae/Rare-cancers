"""Synthetic transport tests only. No network or real registry payloads."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from email.message import Message
import acquire_metadata as a

def study(i, day=1):
    return {'protocolSection': {'identificationModule': {'nctId': 'NCT%08d' % i}, 'statusModule': {'resultsFirstPostDateStruct': {'date': '2026-09-%02d' % day}}, 'conditionsModule': {'conditions': ['synthetic cancer']}}}

def page(records, token=None):
    p = {'studies': records}
    if token is not None:
        p['nextPageToken'] = token
    return json.dumps(p).encode()

class Response(io.BytesIO):
    def __init__(self, body, url, status=200, declare=True):
        super().__init__(body)
        self.url, self.status = url, status
        self.headers = Message()
        if declare:
            self.headers['Content-Length'] = str(len(body))
        self.headers['Content-Type'] = 'application/json'
    def geturl(self):
        return self.url

class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.ledger = self.base / 'ledger.json'
        self.ledger.write_text('{"exclusionTrialIds": []}')
        self.urls = []

    def execute(self, pages, excluded=(), declare=True, status=200):
        self.ledger.write_text(json.dumps({'exclusionTrialIds': list(excluded)}))
        def fetch(url):
            self.urls.append(url)
            return Response(pages[len(self.urls)-1], url, status=status, declare=declare)
        return a.run(self.base / 'archive', self.ledger, fetch, enforce_headroom=False)

    def test_cutoff_tie_requires_next_page_and_reorders_members(self):
        r = self.execute([page([study(i) for i in range(11, 21)], 'abc'), page([study(1), study(2, 2)], 'unused')])
        self.assertEqual('metadata_frame_frozen', r['status'])
        self.assertEqual(['NCT%08d' % i for i in [1] + list(range(11, 20))], [x['nctId'] for x in r['selected']])
        self.assertEqual(2, len(self.urls))
        self.assertEqual(a.query('abc'), self.urls[1])
        self.assertEqual('strictly_later_date_observed', r['termination'])
        projection = json.loads((self.base / 'archive/selected-metadata.json').read_bytes())
        self.assertEqual(study(1)['protocolSection'], projection['NCT00000001'])

    def test_exclusion_and_exhausted_small_frame(self):
        r = self.execute([page([study(1), study(2)])], ['NCT00000001'])
        self.assertEqual(['NCT00000002'], [x['nctId'] for x in r['selected']])
        self.assertTrue(r['observedRecords'][0]['excluded'])

    def test_empty_pages_can_continue_then_valid_empty_frame(self):
        r = self.execute([page([], 'next'), page([])])
        self.assertEqual('metadata_frame_frozen', r['status'])
        self.assertEqual([], r['selected'])
        self.assertEqual(2, len(self.urls))

    def test_duplicate_even_after_tie_boundary_rejects_entire_frame(self):
        r = self.execute([page([study(i) for i in range(1, 11)], 'next'), page([study(11, 2), study(1, 2)])])
        self.assertEqual('stopped', r['status'])
        self.assertEqual([], r['selected'])
        self.assertIn('duplicate trial', r['error'])
        self.assertTrue((self.base / 'archive/page-01.raw.json').exists())

    def test_date_drift_rejects(self):
        r = self.execute([page([study(1, 2)], 'next'), page([study(2, 1)])])
        self.assertIn('nonmonotone', r['error'])

    def test_missing_or_bad_date_rejects(self):
        s = study(1, 31)
        r = self.execute([page([s])])
        self.assertIn('calendar', r['error'])

    def test_outcome_module_schema_drift_rejects(self):
        s = study(1)
        s['resultsSection'] = {'outcomeMeasuresModule': {}}
        r = self.execute([page([s])])
        self.assertIn('metadata schema drift', r['error'])

    def test_incomplete_tie_at_twenty_pages_has_no_selection(self):
        r = self.execute([page([study(p*10+i) for i in range(1, 11)], str(p)) for p in range(20)])
        self.assertEqual(20, len(self.urls))
        self.assertEqual([], r['selected'])
        self.assertIn('page budget', r['error'])
        self.assertEqual(200, len(r['observedRecords']))

    def test_declared_oversize_rejects_before_read(self):
        r = self.execute([b'x' * (a.PAGE_BYTES + 1)])
        self.assertEqual(0, r['rawBytes'])
        self.assertFalse(r['pages'][0]['bodyComplete'])
        self.assertIn('byte budget', r['error'])

    def test_unknown_oversize_preserves_bounded_incomplete_prefix(self):
        r = self.execute([b'x' * (a.PAGE_BYTES + 1)], declare=False)
        self.assertEqual(a.PAGE_BYTES, r['rawBytes'])
        self.assertFalse(r['pages'][0]['bodyComplete'])
        self.assertEqual(b'x' * a.PAGE_BYTES, (self.base / 'archive/page-00.raw.json').read_bytes())

    def test_aggregate_budget_stops_without_retry(self):
        pages = []
        for i in range(20):
            raw = page([study(i+1)], str(i))
            pages.append(raw + b' ' * (a.PAGE_BYTES-len(raw)))
        r = self.execute(pages)
        self.assertEqual(a.TOTAL_BYTES, r['rawBytes'])
        self.assertEqual([], r['selected'])
        self.assertIn('budget', r['error'])
        self.assertLessEqual(len(self.urls), 17)

    def test_access_failure_archives_body_and_stops(self):
        r = self.execute([b'{"error":"synthetic forbidden"}'], status=403)
        self.assertIn('HTTP access failure', r['error'])
        self.assertEqual(1, len(self.urls))
        self.assertTrue(r['pages'][0]['bodyComplete'])

    def test_transport_failure_retains_attempt_receipt(self):
        def fail(url):
            raise OSError('synthetic connection failure')
        r = a.run(self.base / 'archive', self.ledger, fail, False)
        self.assertEqual('stopped', r['status'])
        self.assertEqual(a.query(), r['pages'][0]['url'])
        self.assertFalse(r['pages'][0]['bodyComplete'])
        self.assertTrue((self.base / 'archive/receipt.json').exists())

    def test_repeated_token_stops(self):
        r = self.execute([page([], 'same'), page([], 'same')])
        self.assertIn('repeated pagination token', r['error'])

    def test_truncated_body_retains_partial_evidence(self):
        def fetch(url):
            response = Response(b'{"studies":', url)
            response.headers.replace_header('Content-Length', '999')
            return response
        r = a.run(self.base / 'archive', self.ledger, fetch, False)
        self.assertEqual('stopped', r['status'])
        self.assertFalse(r['pages'][0]['bodyComplete'])
        self.assertEqual(b'{"studies":', (self.base / 'archive/page-00.raw.json').read_bytes())

    def test_duplicate_json_key_cannot_hide_identity(self):
        r = self.execute([b'{"studies":[],"studies":[]}'])
        self.assertIn('duplicate JSON key', r['error'])

    def test_reused_destination_never_overwrites(self):
        r = self.execute([page([])])
        before = (self.base / 'archive/receipt.json').read_bytes()
        with self.assertRaises(FileExistsError):
            a.run(self.base / 'archive', self.ledger, lambda _: self.fail('network'), False)
        self.assertEqual(before, (self.base / 'archive/receipt.json').read_bytes())

if __name__ == '__main__':
    unittest.main()
