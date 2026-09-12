import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('emc_census', Path(__file__).resolve().parents[1] / 'emc_literature_census.py')
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)

class CensusTests(unittest.TestCase):
    def record(self, links=()):
        return {'id': '123', 'source': 'MED', 'title': 'Extraskeletal myxoid chondrosarcoma',
                'fullTextUrlList': {'fullTextUrl': list(links)}}

    def test_free_abstract_is_not_a_free_article(self):
        p = census.normalize(self.record([{'availability': 'Free', 'documentStyle': 'abs', 'url': 'https://example.org/abstract'}]))
        self.assertEqual(p['access'], 'unresolved')
        self.assertEqual(p['free_links'], [])

    def test_public_repository_pdf_is_retained_without_https_guess(self):
        p = census.normalize(self.record([{'availability': 'Free', 'documentStyle': 'pdf', 'url': 'http://repository.example.org/paper.pdf'}]))
        self.assertEqual(p['access'], 'free_link_indexed')
        self.assertEqual(p['free_links'][0]['url'], 'http://repository.example.org/paper.pdf')

    def test_retrieval_and_reading_are_not_inferred_from_pmc_id(self):
        r = self.record(); r['pmcid'] = 'PMC123'
        p = census.normalize(r)
        self.assertEqual(p['reading_status'], 'not_read')
        self.assertEqual(p['screening_status'], 'not_adjudicated')
        self.assertEqual(p['access'], 'free_link_indexed')

    def test_fulltext_mention_does_not_become_focused_match(self):
        r = self.record(); r['title'] = 'Sarcoma overview'
        self.assertEqual(census.normalize(r)['discovery_scope'], 'full_text_or_index')
        r['abstractText'] = 'Includes extraskeletal myxoid chondrosarcoma.'
        self.assertEqual(census.normalize(r)['discovery_scope'], 'abstract')

if __name__ == '__main__':
    unittest.main()
