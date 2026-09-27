"""Behavioral, network-free checks of the one-record metadata correction."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import repair as r

EXPECTED = json.loads(Path(__file__).with_name('expected-public-record.json').read_text(encoding='utf-8'))


class Fake:
    def __init__(self, fault=None):
        self.public = copy.deepcopy(EXPECTED)
        self.dep = copy.deepcopy(EXPECTED)
        self.dep['metadata'].pop('relations')
        self.dep['metadata'].pop('resource_type')
        self.dep['metadata']['upload_type'] = 'dataset'
        self.dep['metadata']['license'] = 'cc-by-4.0'
        self.dep['metadata']['prereserve_doi'] = {'doi': r.DOI, 'recid': r.RECORD}
        file = self.dep['files'][0]
        file['filename'] = file.pop('key')
        file['filesize'] = file.pop('size')
        file['checksum'] = file['checksum'].removeprefix('md5:')
        self.calls = []
        self.fault = fault
        self.body = None

    def request(self, method, url, body=None, auth=False):
        self.calls.append((method, url, auth))
        if self.fault:
            self.fault(self, method, url, body)
        if method == 'GET':
            return copy.deepcopy(self.dep if url == r.DEP else self.public)
        if url.endswith('/edit'):
            self.dep['state'] = 'inprogress'
        elif method == 'PUT':
            self.body = copy.deepcopy(body)
            self.dep['metadata'] = copy.deepcopy(body['metadata'])
        elif url.endswith('/publish'):
            self.dep['state'] = 'done'
            self.public['metadata']['notes'] = self.dep['metadata']['notes']
        else:
            raise AssertionError('Forbidden operation')
        return copy.deepcopy(self.dep)


class RepairTests(unittest.TestCase):
    def execute(self, client, apply=True):
        with patch.object(r, 'verify_bytes') as checked:
            result = r.run(client, EXPECTED, apply)
        return result, checked.call_count

    def test_success_changes_only_notes_and_uses_same_record(self):
        fake = Fake()
        original = r.editable_metadata(fake.dep['metadata'])
        result, byte_checks = self.execute(fake)
        self.assertEqual(result['status'], 'corrected_and_publicly_verified')
        self.assertEqual(byte_checks, 2)
        intended = {**original, 'notes': r.NEW}
        self.assertEqual(fake.body, {'metadata': intended})
        self.assertEqual([call[:2] for call in fake.calls if call[0] != 'GET'],
            [('POST', r.DEP + '/actions/edit'), ('PUT', r.DEP), ('POST', r.DEP + '/actions/publish')])
        self.assertEqual(fake.public['files'], EXPECTED['files'])

    def test_corrected_noop_still_verifies_state_metadata_and_bytes(self):
        fake = Fake()
        fake.dep['metadata']['notes'] = fake.public['metadata']['notes'] = r.NEW
        result, byte_checks = self.execute(fake)
        self.assertEqual(result['status'], 'verified_noop')
        self.assertEqual(byte_checks, 1)
        self.assertTrue(all(method == 'GET' for method, _, _ in fake.calls))

    def test_inspect_never_mutates(self):
        fake = Fake()
        result, _ = self.execute(fake, False)
        self.assertEqual(result['status'], 'inspected')
        self.assertTrue(all(method == 'GET' for method, _, _ in fake.calls))

    def test_initial_identity_state_note_or_metadata_errors_never_mutate(self):
        mutations = [lambda f: f.dep.update(id=1), lambda f: f.dep.update(conceptrecid='1'),
            lambda f: f.dep.update(doi='wrong'), lambda f: f.dep.update(submitted=False),
            lambda f: f.dep.update(state='inprogress'), lambda f: f.dep.update(files=[]),
            lambda f: f.dep['files'][0].update(checksum='wrong'),
            lambda f: f.dep['files'][0].update(filesize=0),
            lambda f: f.dep['files'][0].update(filename='wrong'),
            lambda f: f.dep['metadata'].update(title='intervening title'),
            lambda f: f.public['metadata'].update(notes='someone else edited this'),
            lambda f: f.public['metadata'].update(keywords=[]),
            lambda f: f.dep['metadata']['prereserve_doi'].update(doi='wrong')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                fake = Fake(); mutate(fake)
                with self.assertRaises(ValueError): self.execute(fake)
                self.assertTrue(all(method == 'GET' for method, _, _ in fake.calls))

    def test_intervening_change_after_edit_prevents_put(self):
        def fault(f, method, url, body):
            if method == 'GET' and url == r.DEP and f.dep['state'] == 'inprogress':
                f.dep['metadata']['description'] = 'intervening edit'
        fake = Fake(fault)
        with self.assertRaisesRegex(ValueError, 'Intervening edit'): self.execute(fake)
        self.assertEqual(len([x for x in fake.calls if x[0] != 'GET']), 1)

    def test_unexpected_put_delta_prevents_publish(self):
        class Altering(Fake):
            def request(self, method, url, body=None, auth=False):
                result = super().request(method, url, body, auth)
                if method == 'PUT': result['metadata']['creators'] = []
                return result
        fake = Altering()
        with self.assertRaisesRegex(ValueError, 'PUT response'): self.execute(fake)
        self.assertFalse(any(url.endswith('/publish') for _, url, _ in fake.calls))

    def test_each_uncertain_mutation_stops_without_retry_or_discard(self):
        for target in [('POST', r.DEP + '/actions/edit'), ('PUT', r.DEP),
                       ('POST', r.DEP + '/actions/publish')]:
            with self.subTest(target=target):
                def fault(f, method, url, body):
                    if (method, url) == target: raise TimeoutError('uncertain response')
                fake = Fake(fault)
                with self.assertRaises(TimeoutError): self.execute(fake)
                self.assertEqual(sum((method, url) == target for method, url, _ in fake.calls), 1)
                self.assertEqual(fake.calls[-1][:2], target)

    def test_unexpected_public_delta_after_publish_is_not_success(self):
        def fault(f, method, url, body):
            if url == r.PUB and f.public['metadata']['notes'] == r.NEW:
                f.public['metadata']['publication_date'] = '2000-01-01'
        with self.assertRaisesRegex(ValueError, 'public metadata delta'): self.execute(Fake(fault))

    def test_changed_archive_bytes_refuse(self):
        class BadBytes:
            def request(self, *args): return b'changed'
        with self.assertRaisesRegex(ValueError, 'bytes changed'): r.verify_bytes(BadBytes())

    def test_forbidden_endpoints_refuse_before_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = r.Client('fake-test-token', Path(tmp))
            for method, url, auth in [('POST', r.DEP + '/actions/newversion', True),
                ('DELETE', r.DEP, True), ('PUT', r.CONTENT, True), ('GET', 'https://example.org', True),
                ('GET', r.PUB, True)]:
                with self.subTest(url=url):
                    with self.assertRaises(ValueError): client.request(method, url, auth=auth)
            self.assertEqual(client.index, 0)

    def test_transport_timeout_not_retried_and_receipt_has_no_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = r.Client('fake-test-token', Path(tmp))
            with patch.object(client.opener, 'open', side_effect=TimeoutError('unknown')) as send:
                with self.assertRaises(TimeoutError): client.request('POST', r.DEP + '/actions/edit', auth=True)
            self.assertEqual(send.call_count, 1)
            for path in Path(tmp).iterdir():
                self.assertNotIn('fake-test-token', path.read_text())
            self.assertFalse(json.loads((Path(tmp) / '01.receipt.json').read_text())['response_observed'])

    def test_redirect_blocked(self):
        self.assertIsNone(r.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.org'))


if __name__ == '__main__':
    unittest.main()
