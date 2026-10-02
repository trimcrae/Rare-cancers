"""Explicitly synthetic arithmetic tests; no biological corpus execution."""
import unittest
from protein_lineage import describe, decompose

class SyntheticTests(unittest.TestCase):
    def test_average_ties_known_rho(self):
        # Average ranks: [1.5,1.5,3,4] and [1,2.5,2.5,4].
        self.assertAlmostEqual(describe([1,1,2,3], [1,2,2,3])['rho'], 5/6)

    def test_singleton_stratum(self):
        result = decompose([1,2,3,4], [4,2,3,1], ['a','a','a','b'])
        singleton = next(s for s in result['strata'] if s['histology']=='b')
        self.assertEqual(singleton['n'], 1)
        self.assertEqual(singleton['withinContribution'], 0)
        self.assertAlmostEqual(result['withinComponent']+result['betweenComponent'], result['rho'])

    def test_all_singletons(self):
        result = decompose([1,2,3], [3,2,1], ['a','b','c'])
        self.assertEqual(result['withinComponent'], 0)
        self.assertAlmostEqual(result['betweenComponent'], -1)

    def test_one_stratum(self):
        result = decompose([1,1,3,4], [4,2,2,1], ['a']*4)
        self.assertEqual(result['betweenComponent'], 0)
        self.assertAlmostEqual(result['withinComponent'], result['rho'])

    def test_opposite_components(self):
        result = decompose([1,2,3,4,5,6], [3,2,1,6,5,4], ['a']*3+['b']*3)
        self.assertLess(result['withinComponent'], 0)
        self.assertGreater(result['betweenComponent'], 0)
        self.assertAlmostEqual(result['rho'], 19/35)
        self.assertAlmostEqual(result['sumError'], 0)

    def test_sparse_and_empty(self):
        for x,y in [([],[]), ([1],[2]), ([1,2],[2,1])]:
            self.assertIsNone(describe(x,y)['rho'])
            self.assertEqual(describe(x,y)['undefinedReason'], 'fewer_than_three_pairs')

    def test_constant(self):
        result = decompose([1,1,1], [2,3,4], ['a','a','b'])
        self.assertIsNone(result['rho'])
        self.assertIsNone(result['withinComponent'])
        self.assertIsNone(result['betweenComponent'])

    def test_invalid_pairs(self):
        with self.assertRaises(ValueError): describe([1,2,3], [1,2])
        with self.assertRaises(ValueError): describe([1,2,float('nan')], [1,2,3])
        with self.assertRaises(ValueError): decompose([1,2,3], [1,2,3], ['a'])

if __name__ == '__main__': unittest.main()
