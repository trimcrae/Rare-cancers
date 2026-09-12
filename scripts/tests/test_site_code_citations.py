"""Resolve actual site code while retaining dead-code citation detection."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('site_citation_checker', ROOT / 'systems/systems_check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Findings:
    def __init__(self):
        self.warnings = []

    def warn(self, code, text):
        self.warnings.append((code, text))


class SiteCodeCitationTests(unittest.TestCase):
    def test_live_site_file_resolves_and_missing_file_still_fails(self):
        self.assertTrue((ROOT / 'site/build.py').is_file())
        documents = [('site/README.md', 'Run `build.py`.\nRun `nonexistent-site-file-8e81.py`.\n')]
        findings = Findings()
        with patch.object(checker, '_walk_md', return_value=iter(documents)):
            checker.check_code_citations(None, findings)
        self.assertEqual(len(findings.warnings), 1)
        self.assertEqual(findings.warnings[0][0], '[K3]')
        self.assertIn('nonexistent-site-file-8e81.py', findings.warnings[0][1])


if __name__ == '__main__':
    unittest.main()
