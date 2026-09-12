"""Protect against silently mixing sarcoma cohorts across endpoint group IDs."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('emc_trial_results', Path(__file__).resolve().parents[1] / 'emc_trial_results.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SubgroupTests(unittest.TestCase):
    def test_group_ids_are_endpoint_local_and_missingness_preserved(self):
        outcomes = []
        for target, other in [('OG007', 'OG008'), ('OG008', 'OG007')]:
            outcomes.append({'groups': [{'id': target, 'title': 'Extraskeletal Myxoid Chondrosarcoma'},
                                        {'id': other, 'title': 'Other sarcoma'}],
                             'denoms': [{'counts': [{'groupId': target, 'value': '11'}, {'groupId': other, 'value': '50'}]}],
                             'classes': [{'categories': [{'measurements': [{'groupId': target, 'value': 'NA', 'comment': 'Not reached'},
                                                                           {'groupId': other, 'value': '99'}]}]}]})
        study = {'resultsSection': {'outcomeMeasuresModule': {'outcomeMeasures': outcomes}}}
        extracted = module.extract(study)
        self.assertEqual(len(extracted), 2)
        for record in extracted:
            outcome = record['outcome']
            self.assertEqual([v['value'] for v in outcome['denoms'][0]['counts']], ['11'])
            measurements = outcome['classes'][0]['categories'][0]['measurements']
            self.assertEqual([(v['value'], v['comment']) for v in measurements], [('NA', 'Not reached')])
        self.assertEqual(len(outcomes[0]['groups']), 2)  # original evidence untouched

    def test_eligibility_is_not_enrollment_evidence(self):
        self.assertEqual(module.extract({'protocolSection': {'eligibility': 'Extraskeletal myxoid chondrosarcoma'}}), [])


if __name__ == '__main__':
    unittest.main()
