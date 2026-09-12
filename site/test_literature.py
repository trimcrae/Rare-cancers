"""Public-output and catalogue integrity checks; no browser or rendering runtime."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build
import literature_page

class LiteratureTests(unittest.TestCase):
    def test_public_allowlist_and_record_count(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'public'
            build.build(out)
            self.assertEqual({p.name for p in out.iterdir()}, build.OUTPUT_FILES)
            data = json.loads((out / 'literature.json').read_text(encoding='utf-8'))
            html = (out / 'literature.html').read_text(encoding='utf-8')
            self.assertEqual(html.count('class="literature-record"'), len(data['records']))
            self.assertEqual(len(data['records']), data['counts']['deduplicated_records'])
            self.assertEqual(sum(data['counts']['scope_counts'].values()), len(data['records']))
            self.assertNotIn('{{', html)

    def test_foreign_output_file_blocks_build(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'public'
            out.mkdir()
            (out / 'private-notes.txt').write_text('private')
            with self.assertRaises(ValueError):
                build.build(out)
            self.assertEqual((out / 'private-notes.txt').read_text(), 'private')

    def test_links_reject_active_or_credential_urls(self):
        for url in ('javascript:alert(1)', 'file:///C:/secret', 'https://user:password@example.org/a'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                literature_page.safe_url(url)

    def test_titles_are_escaped_and_free_claim_requires_evidence(self):
        source = json.loads((literature_page.HERE / 'literature.json').read_text(encoding='utf-8'))
        p = source['records'][0]
        p['title'] = '<script>alert(1)</script>'
        p['free_links'] = []
        p['access'] = 'unresolved'
        source['records'] = [p]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'literature.json').write_text(json.dumps(source), encoding='utf-8')
            with patch.object(literature_page, 'HERE', path):
                html, _, _ = literature_page.render()
                self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
                self.assertNotIn('<script>alert(1)</script>', html)
                p['access'] = 'free_link_indexed'
                (path / 'literature.json').write_text(json.dumps(source), encoding='utf-8')
                with self.assertRaises(ValueError):
                    literature_page.render()

if __name__ == '__main__':
    unittest.main()
