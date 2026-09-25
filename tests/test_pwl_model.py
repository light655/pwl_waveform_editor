import os
import sys
import unittest

# Ensure the project root is in sys.path when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pwl_model import PWLWaveform, sciparse, sciprint


class TestPWLWaveform(unittest.TestCase):
    """Unit tests for the PWLWaveform class, verifying point ordering and integrity."""

    def setUp(self):
        self.waveform = PWLWaveform()

    def assertPointsInOrder(self, waveform: PWLWaveform, strictly_increasing: bool = False):
        """Helper to assert that waveform points are ordered by x-coordinate,
        have matching lengths, and remain lists.
        """
        self.assertIsInstance(waveform.node_x, list, "node_x must be a list")
        self.assertIsInstance(waveform.node_y, list, "node_y must be a list")
        self.assertEqual(
            len(waveform.node_x),
            len(waveform.node_y),
            "node_x and node_y must have identical lengths",
        )

        for i in range(len(waveform.node_x) - 1):
            x_curr = waveform.node_x[i]
            x_next = waveform.node_x[i + 1]
            if strictly_increasing:
                self.assertLess(
                    x_curr,
                    x_next,
                    f"Points not strictly increasing at index {i}: {x_curr} >= {x_next}",
                )
            else:
                self.assertLessEqual(
                    x_curr,
                    x_next,
                    f"Points not sorted at index {i}: {x_curr} > {x_next}",
                )

    # -------------------------------------------------------------------------
    # Initial State Tests
    # -------------------------------------------------------------------------

    def test_initial_state(self):
        """Verify the waveform starts with ordered default points."""
        self.assertEqual(self.waveform.node_x, [0.0])
        self.assertEqual(self.waveform.node_y, [0.0])
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

    # -------------------------------------------------------------------------
    # Add Point Tests
    # -------------------------------------------------------------------------

    def test_add_points_in_ascending_order(self):
        """Points added in ascending x order should remain sorted."""
        points_to_add = [(0.2, 0.5), (0.5, -0.3), (1.0, 1.0), (2.5, 0.0)]
        for x, y in points_to_add:
            self.waveform.add_point(x, y)
            self.assertPointsInOrder(self.waveform, strictly_increasing=True)

        expected_x = [0.0, 0.2, 0.5, 1.0, 2.5]
        expected_y = [0.0, 0.5, -0.3, 1.0, 0.0]
        self.assertEqual(self.waveform.node_x, expected_x)
        self.assertEqual(self.waveform.node_y, expected_y)

    def test_add_points_in_descending_order(self):
        """Points added with decreasing x values should be inserted in front and stay sorted."""
        points_to_add = [(-0.2, 0.4), (-0.5, -0.1), (-1.0, 0.9), (-2.5, -0.8)]
        for x, y in points_to_add:
            self.waveform.add_point(x, y)
            self.assertPointsInOrder(self.waveform, strictly_increasing=True)

        expected_x = [-2.5, -1.0, -0.5, -0.2, 0.0]
        expected_y = [-0.8, 0.9, -0.1, 0.4, 0.0]
        self.assertEqual(self.waveform.node_x, expected_x)
        self.assertEqual(self.waveform.node_y, expected_y)

    def test_add_points_in_random_order(self):
        """Points added in arbitrary / random order must always be sorted after each addition."""
        points_to_add = [
            (0.8, 0.8),
            (-0.4, -0.4),
            (0.3, 0.3),
            (1.5, 1.5),
            (-1.2, -1.2),
            (0.1, 0.1),
            (-0.05, -0.05),
        ]
        for x, y in points_to_add:
            self.waveform.add_point(x, y)
            self.assertPointsInOrder(self.waveform, strictly_increasing=True)

        # Check against Python's canonical sort
        expected = sorted([(0.0, 0.0)] + points_to_add, key=lambda p: p[0])
        expected_x = [p[0] for p in expected]
        expected_y = [p[1] for p in expected]
        self.assertEqual(self.waveform.node_x, expected_x)
        self.assertEqual(self.waveform.node_y, expected_y)

    def test_add_points_insert_between_existing(self):
        """Adding points strictly between existing neighbors preserves order and coordinate pairing."""
        self.waveform.add_point(1.0, 1.0)
        # Currently [0.0, 1.0]
        self.waveform.add_point(0.5, 0.5)
        # Currently [0.0, 0.5, 1.0]
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.0, 0.5, 1.0])
        self.assertEqual(self.waveform.node_y, [0.0, 0.5, 1.0])

        self.waveform.add_point(0.25, 0.25)
        self.waveform.add_point(0.75, 0.75)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.0, 0.25, 0.5, 0.75, 1.0])
        self.assertEqual(self.waveform.node_y, [0.0, 0.25, 0.5, 0.75, 1.0])

    def test_add_duplicate_point_does_not_break_order(self):
        """Attempting to add a duplicate point should not corrupt order or duplicate entries."""
        self.waveform.add_point(1.0, 1.0)
        initial_len = len(self.waveform.node_x)

        # Try adding existing x
        self.waveform.add_point(1.0, 99.0)
        self.assertEqual(len(self.waveform.node_x), initial_len)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

    def test_add_point_to_empty_waveform(self):
        """Adding points after all existing points were removed should maintain sorted order."""
        self.waveform.remove_point(0)
        self.assertEqual(len(self.waveform.node_x), 0)

        self.waveform.add_point(0.5, 1.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.5])
        self.assertEqual(self.waveform.node_y, [1.0])

        self.waveform.add_point(0.2, 0.4)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.2, 0.5])

    # -------------------------------------------------------------------------
    # Update Point Tests
    # -------------------------------------------------------------------------

    def test_update_point_same_relative_order(self):
        """Updating a point within its bounds preserves sorted order and updates coordinates."""
        self.waveform.add_point(1.0, 1.0)
        self.waveform.add_point(2.0, 2.0)
        # points are [0.0, 1.0, 2.0]

        # Update point 1 x from 1.0 to 1.2 (still between 0.0 and 2.0)
        self.waveform.update_point_position(1, 1.2, 5.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.0, 1.2, 2.0])
        self.assertEqual(self.waveform.node_y, [0.0, 5.0, 2.0])

    def test_update_point_move_to_front(self):
        """Updating a point so its new x is less than all others reorders it to the front."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(2.0, 20.0)
        # points: [(0.0, 0.0), (1.0, 10.0), (2.0, 20.0)]

        # Move the last point (index 2) to x = -1.0, y = 99.0
        self.waveform.update_point_position(2, -1.0, 99.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [-1.0, 0.0, 1.0])
        self.assertEqual(self.waveform.node_y, [99.0, 0.0, 10.0])

    def test_update_point_move_to_back(self):
        """Updating a point so its new x is greater than all others reorders it to the back."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(2.0, 20.0)
        # points: [(0.0, 0.0), (1.0, 10.0), (2.0, 20.0)]

        # Move the first point (index 0) to x = 5.0, y = -50.0
        self.waveform.update_point_position(0, 5.0, -50.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [1.0, 2.0, 5.0])
        self.assertEqual(self.waveform.node_y, [10.0, 20.0, -50.0])

    def test_update_point_move_to_middle(self):
        """Updating a point to a position between existing points preserves sorted order."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(3.0, 30.0)
        self.waveform.add_point(4.0, 40.0)
        # points: [(0.0, 0.0), (1.0, 10.0), (3.0, 30.0), (4.0, 40.0)]

        # Move point at index 0 (x=0.0) to x = 2.0, y = 25.0
        self.waveform.update_point_position(0, 2.0, 25.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(self.waveform.node_y, [10.0, 25.0, 30.0, 40.0])

    def test_update_point_consecutive_updates(self):
        """Multiple consecutive updates maintain list type and sorted order throughout."""
        self.waveform.add_point(1.0, 1.0)
        self.waveform.add_point(2.0, 2.0)

        # Successive updates: ensure node_x and node_y stay lists and stay sorted
        self.waveform.update_point_position(0, 3.0, 30.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [1.0, 2.0, 3.0])

        self.waveform.update_point_position(1, 0.5, 5.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.5, 1.0, 3.0])

        self.waveform.update_point_position(2, -0.5, -5.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [-0.5, 0.5, 1.0])

    def test_update_point_invalid_index(self):
        """Updating with an out-of-bounds index does nothing and does not disrupt order."""
        self.waveform.add_point(1.0, 1.0)
        original_x = list(self.waveform.node_x)
        original_y = list(self.waveform.node_y)

        self.waveform.update_point_position(-1, 0.5, 0.5)
        self.waveform.update_point_position(10, 0.5, 0.5)
        self.assertEqual(self.waveform.node_x, original_x)
        self.assertEqual(self.waveform.node_y, original_y)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

    # -------------------------------------------------------------------------
    # Remove Point Tests
    # -------------------------------------------------------------------------

    def test_remove_point_from_front(self):
        """Removing the first point keeps remaining points sorted."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(2.0, 20.0)
        # points: [0.0, 1.0, 2.0]

        self.waveform.remove_point(0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [1.0, 2.0])
        self.assertEqual(self.waveform.node_y, [10.0, 20.0])

    def test_remove_point_from_middle(self):
        """Removing a middle point keeps remaining points sorted."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(2.0, 20.0)
        # points: [0.0, 1.0, 2.0]

        self.waveform.remove_point(1)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.0, 2.0])
        self.assertEqual(self.waveform.node_y, [0.0, 20.0])

    def test_remove_point_from_back(self):
        """Removing the last point keeps remaining points sorted."""
        self.waveform.add_point(1.0, 10.0)
        self.waveform.add_point(2.0, 20.0)
        # points: [0.0, 1.0, 2.0]

        self.waveform.remove_point(2)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.0, 1.0])
        self.assertEqual(self.waveform.node_y, [0.0, 10.0])

    def test_remove_all_points(self):
        """Removing all points results in empty lists and does not raise errors."""
        self.waveform.remove_point(0)
        self.assertEqual(self.waveform.node_x, [])
        self.assertEqual(self.waveform.node_y, [])
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

    def test_remove_point_invalid_index(self):
        """Removing with an out-of-bounds index does nothing and maintains order."""
        self.waveform.add_point(1.0, 1.0)
        original_x = list(self.waveform.node_x)
        original_y = list(self.waveform.node_y)

        self.waveform.remove_point(-1)
        self.waveform.remove_point(10)
        self.assertEqual(self.waveform.node_x, original_x)
        self.assertEqual(self.waveform.node_y, original_y)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

    # -------------------------------------------------------------------------
    # Combined / Interleaved Operations Tests
    # -------------------------------------------------------------------------

    def test_interleaved_add_update_remove(self):
        """Interleaved add, update, and remove operations must maintain sorted order at every step."""
        # 1. Start with initial waveform [0.0]
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

        # 2. Add multiple points
        for x, y in [(0.4, 4.0), (0.8, 8.0), (0.2, 2.0), (0.6, 6.0)]:
            self.waveform.add_point(x, y)
            self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        # Current x: [0.0, 0.2, 0.4, 0.6, 0.8]
        self.assertEqual(self.waveform.node_x, [0.0, 0.2, 0.4, 0.6, 0.8])

        # 3. Update point at index 0 from 0.0 to 0.5 (moves to middle)
        self.waveform.update_point_position(0, 0.5, 5.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.2, 0.4, 0.5, 0.6, 0.8])

        # 4. Remove a middle point (index 2: x=0.5)
        self.waveform.remove_point(2)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.2, 0.4, 0.6, 0.8])

        # 5. Add a point before everything (x = -0.1)
        self.waveform.add_point(-0.1, -1.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [-0.1, 0.2, 0.4, 0.6, 0.8])

        # 6. Update the last point (index 4: x=0.8) to x = 0.3 (moves to middle)
        self.waveform.update_point_position(4, 0.3, 3.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [-0.1, 0.2, 0.3, 0.4, 0.6])

        # 7. Remove the first point (x = -0.1)
        self.waveform.remove_point(0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)
        self.assertEqual(self.waveform.node_x, [0.2, 0.3, 0.4, 0.6])

        # 8. Add a point at the end (x = 1.0)
        self.waveform.add_point(1.0, 10.0)
        self.assertPointsInOrder(self.waveform, strictly_increasing=True)

class TestSciFunctions(unittest.TestCase):
    """Unit tests for sciparse and sciprint helper functions."""

    def test_sciparse_numbers(self):
        self.assertAlmostEqual(sciparse("0"), 0.0)
        self.assertAlmostEqual(sciparse("1.25"), 1.25)
        self.assertAlmostEqual(sciparse("-3.5"), -3.5)

    def test_sciparse_scientific_suffixes(self):
        self.assertAlmostEqual(sciparse("10p"), 10e-12)
        self.assertAlmostEqual(sciparse("2.5n"), 2.5e-9)
        self.assertAlmostEqual(sciparse("100u"), 100e-6)
        self.assertAlmostEqual(sciparse("5m"), 5e-3)
        self.assertAlmostEqual(sciparse("10k"), 10e3)
        self.assertAlmostEqual(sciparse("2M"), 2e6)
        self.assertAlmostEqual(sciparse("1G"), 1e9)

    def test_sciparse_invalid_inputs(self):
        with self.assertRaises(ValueError):
            sciparse("")
        with self.assertRaises(ValueError):
            sciparse("   ")
        with self.assertRaises(ValueError):
            sciparse("abc")
        with self.assertRaises(ValueError):
            sciparse("12xyz")

    def test_sciprint(self):
        self.assertEqual(sciprint(0), "0")
        self.assertEqual(sciprint(5e-13), "0.500p")
        self.assertEqual(sciprint(1.5e-9), "1.500n")
        self.assertEqual(sciprint(1.5e-6), "1.500u")
        self.assertEqual(sciprint(1.5e-3), "1.500m")
        self.assertEqual(sciprint(5.0), "5.000")
        self.assertEqual(sciprint(5000), "5.000k")
        self.assertEqual(sciprint(5000000), "5.000M")


if __name__ == "__main__":
    unittest.main()
