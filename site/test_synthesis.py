"""Evidence linkage and public rendering checks for the synthesis."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import synthesis_page


class SynthesisTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((synthesis_page.HERE / 'synthesis.json').read_text(encoding='utf-8'))

    def test_unresolved_source_and_missing_counterevidence_fail_closed(self):
        self.data['hypotheses'][0]['source_ids'].append('nonexistent-study')
        with self.assertRaises(ValueError):
            synthesis_page.validate(self.data)
        self.data['hypotheses'][0]['source_ids'].pop()
        self.data['hypotheses'][0]['against'] = ''
        with self.assertRaises(ValueError):
            synthesis_page.validate(self.data)

    def test_all_sources_and_hypotheses_render_and_text_is_escaped(self):
        self.data['sources'][0]['observation'] = '<script>untrusted()</script>'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'synthesis.json').write_text(json.dumps(self.data), encoding='utf-8')
            (path / 'synthesis-check.json').write_bytes((synthesis_page.HERE / 'synthesis-check.json').read_bytes())
            with patch.object(synthesis_page, 'HERE', path):
                html = synthesis_page.render()
            self.assertNotIn('<script>untrusted()</script>', html)
            self.assertIn('&lt;script&gt;untrusted()&lt;/script&gt;', html)
            for h in self.data['hypotheses']:
                self.assertIn('id="' + h['id'] + '"', html)
            for s in self.data['sources']:
                self.assertIn('id="source-' + s['id'] + '"', html)


if __name__ == '__main__':
    unittest.main()
