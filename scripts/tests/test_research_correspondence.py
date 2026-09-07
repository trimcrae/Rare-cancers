import concurrent.futures
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('correspondence', Path(__file__).resolve().parents[1] / 'research_correspondence.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.authority = self.directory / 'authority.json'
        self.authority.write_text(json.dumps({'research_correspondence': {'standing_grant': True}}))
        (self.directory / 'mailbox.json').write_text(json.dumps({
            'provider': 'test', 'sender': 'research@example.org', 'send_verified': True,
            'receive_verified': True, 'verification_evidence': 'synthetic test fixture'}))
        self.ledger = module.Ledger(self.directory, self.authority)

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def queue(self, request_id='one', body='Please clarify the published method.'):
        return {'_schema': 'emc-research-correspondence-queue/1', 'requests': [{
            'request_id': request_id, 'recipients': ['author@example.org'],
            'subject': 'Published methods question', 'body': body,
            'scientific_dependency': 'resolve interpretation', 'source_doi': '10.test/fixture'}]}

    def test_duplicate_import_and_conflicting_id(self):
        self.assertEqual(self.ledger.import_queue(self.queue()), 1)
        self.assertEqual(self.ledger.import_queue(self.queue()), 0)
        self.assertEqual(self.ledger.import_queue(self.queue('renamed')), 0)
        with self.assertRaises(ValueError):
            self.ledger.import_queue(self.queue(body='Different text'))

    def test_concurrent_reservation_only_one_winner(self):
        self.ledger.import_queue(self.queue())
        def reserve():
            ledger = module.Ledger(self.directory, self.authority)
            try:
                return ledger.reserve('one')
            except ValueError:
                return None
            finally:
                ledger.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: reserve(), range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)

    def test_uncertainty_survives_restart_and_requires_evidence(self):
        self.ledger.import_queue(self.queue())
        token = self.ledger.reserve('one')
        self.ledger.close()
        self.ledger = module.Ledger(self.directory, self.authority)
        self.assertEqual(self.ledger.status()['requests'][0]['status'], 'send_uncertain')
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')
        with self.assertRaises(ValueError):
            self.ledger.reconcile('one', token, 'absent', '')
        with self.assertRaises(ValueError):
            self.ledger.reconcile('one', 'wrong-token', 'absent', 'verified absence')
        self.ledger.reconcile('one', token, 'absent', 'verified complete provider search: absent')
        new_token = self.ledger.reserve('one')
        self.assertNotEqual(token, new_token)
        with self.assertRaises(ValueError):
            self.ledger.reconcile('one', new_token, 'sent', 'provider receipt')
        self.ledger.reconcile('one', new_token, 'sent', 'provider receipt', 'provider-id-1')
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')

    def test_unresolved_request_blocks_second_writer(self):
        self.ledger.import_queue(self.queue())
        self.ledger.import_queue(self.queue('two', 'Different scientific question.'))
        self.ledger.reserve('one')
        with self.assertRaises(ValueError):
            self.ledger.reserve('two')

    def test_refusal_suppresses_existing_and_future_requests(self):
        self.ledger.import_queue(self.queue())
        self.ledger.refuse('AUTHOR@example.org', 'recipient explicitly declined')
        self.ledger.import_queue(self.queue('two', 'Another question'))
        self.assertTrue(all(r['status'] == 'closed' for r in self.ledger.status()['requests']))
        with self.assertRaises(ValueError):
            self.ledger.reserve('two')

    def test_refusal_preserves_send_uncertainty(self):
        self.ledger.import_queue(self.queue())
        token = self.ledger.reserve('one')
        self.ledger.refuse('author@example.org', 'refused')
        self.assertEqual(self.ledger.status()['requests'][0]['status'], 'send_uncertain')
        self.ledger.reconcile('one', token, 'absent', 'verified absent')
        self.assertEqual(self.ledger.status()['requests'][0]['status'], 'closed')

    def test_missing_authority_blocks(self):
        self.ledger.import_queue(self.queue())
        self.authority.unlink()
        self.assertFalse(self.ledger.readiness()['ready_to_reserve'])
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')

    def test_missing_or_unverified_mailbox_blocks(self):
        self.ledger.import_queue(self.queue())
        mailbox = self.directory / 'mailbox.json'
        mailbox.unlink()
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')
        mailbox.write_text(json.dumps({'provider': 'test', 'sender': 'test@example.org',
            'send_verified': True, 'receive_verified': False, 'verification_evidence': 'fixture'}))
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')
        self.assertFalse(self.ledger.status()['transport_implemented'])

    def test_placeholders_block(self):
        self.ledger.import_queue(self.queue(body='Dear [AUTHOR], please provide methods.'))
        with self.assertRaises(ValueError):
            self.ledger.reserve('one')

    def test_show_recovers_exact_reserved_content_and_token_after_restart(self):
        queue = self.queue()
        self.ledger.import_queue(queue)
        token = self.ledger.reserve('one')
        self.ledger.close()
        self.ledger = module.Ledger(self.directory, self.authority)
        shown = self.ledger.show('one')
        self.assertEqual(shown['token'], token)
        self.assertEqual(shown['payload'], queue['requests'][0])
        self.assertEqual(shown['status'], 'send_uncertain')
        self.assertEqual(len(shown['digest']), 64)
        self.assertEqual([event['event'] for event in shown['events']],
                         ['imported', 'reserved_send_uncertain'])

    def test_incoming_context_preserves_evidence_without_reopening(self):
        self.ledger.import_queue(self.queue())
        token = self.ledger.reserve('one')
        self.ledger.record_event('one', 'reply', 'provider thread T1 message M2', 'Review method clarification')
        shown = self.ledger.show('one')
        self.assertEqual(shown['status'], 'send_uncertain')
        context = json.loads(shown['events'][-1]['evidence'])
        self.assertEqual(context['evidence'], 'provider thread T1 message M2')
        self.assertEqual(context['next_action'], 'Review method clarification')
        self.ledger.reconcile('one', token, 'absent', 'provider confirms absent')
        self.ledger.refuse('author@example.org', 'declined')
        self.ledger.record_event('one', 'followup_context', 'private/reply.txt', 'No further contact')
        self.assertEqual(self.ledger.show('one')['status'], 'closed')
        with self.assertRaises(ValueError):
            self.ledger.record_event('unknown', 'reply', 'receipt', 'Review')


if __name__ == '__main__':
    unittest.main()
