"""Synthetic unit tests for interval arithmetic; no biological validation."""
import unittest

from interval_ranking import rank_primary_intervals, union_distance


def candidate(ident, lower, upper):
    return {
        "design_id": ident,
        "union_hamming_lower_bound": lower,
        "union_hamming_upper_bound": upper,
    }


class IntervalTests(unittest.TestCase):
    def test_archive_four_resolves_union(self):
        self.assertEqual(union_distance(4, []), (4, 4, 4))

    def test_archive_five_bounds_union(self):
        self.assertEqual(union_distance(5, []), (4, 5, None))

    def test_scanned_exact_minimum(self):
        self.assertEqual(union_distance(5, [3, 2]), (2, 2, 2))
        self.assertEqual(union_distance(3, [3]), (3, 3, 3))
        self.assertEqual(union_distance(0, [0, 2]), (0, 0, 0))

    def test_singleton_censored_choice_resolved(self):
        self.assertEqual(rank_primary_intervals([candidate("a", 4, 5)]), (True, ["a"]))

    def test_censored_candidate_definitely_beats_exact_three(self):
        rows = [candidate("a", 3, 3), candidate("b", 4, 5)]
        self.assertEqual(rank_primary_intervals(rows), (True, ["b"]))
        self.assertEqual(rank_primary_intervals(reversed(rows)), (True, ["b"]))

    def test_overlapping_interval_leaves_tie_membership_unresolved(self):
        self.assertEqual(
            rank_primary_intervals([candidate("a", 4, 4), candidate("b", 4, 5)]),
            (False, []),
        )

    def test_exact_ties_return_all_argmax_sorted(self):
        self.assertEqual(
            rank_primary_intervals([candidate("z", 4, 4), candidate("b", 3, 3), candidate("a", 4, 4)]),
            (True, ["a", "z"]),
        )

    def test_uncertain_ties_are_not_guessed(self):
        self.assertEqual(
            rank_primary_intervals([candidate("a", 4, 5), candidate("b", 4, 5)]),
            (False, []),
        )

    def test_exact_unique_maximum(self):
        self.assertEqual(
            rank_primary_intervals([candidate("a", 2, 2), candidate("b", 3, 3)]),
            (True, ["b"]),
        )

    def test_negative_union_inputs(self):
        cases = [
            (-1, []), (17, []), (True, []), (4.0, []),
            (3, []), (1, [2]), (4, [4]), (4, [-1]),
            (4, [True]), (4, [1.5]),
        ]
        for archive, observed in cases:
            with self.subTest(archive=archive, observed=observed):
                with self.assertRaises(ValueError):
                    union_distance(archive, observed)

    def test_negative_ranking_inputs(self):
        cases = [
            [],
            [candidate("", 4, 5)],
            [candidate("a", 4, 5), candidate("a", 4, 5)],
            [candidate("a", 5, 4)],
            [candidate("a", -1, 4)],
            [candidate("a", 4, 17)],
            [candidate("a", True, 4)],
            [candidate("a", 4, None)],
        ]
        for rows in cases:
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    rank_primary_intervals(rows)


if __name__ == "__main__":
    unittest.main()
