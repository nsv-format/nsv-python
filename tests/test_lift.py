import unittest
import nsv

class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift_2d_to_1d(self):
        """Test lift collapses 2D to 1D."""
        # 2 rows, 2 cells each
        original = "a\nb\n\nc\nd\n\n"
        lifted = nsv.lift(original)

        # Should be 1 row with 5 cells (terminator stripped)
        parsed = nsv.loads(lifted)
        self.assertEqual(1, len(parsed))  # One row
        self.assertEqual(5, len(parsed[0]))  # 5 cells (no trailing terminator)
        self.assertEqual(["a", "b", "", "c", "d"], parsed[0])

    def test_basic_unlift_1d_to_2d(self):
        """Test unlift expands 1D to 2D."""
        # 1 row with 5 cells (produced by lift, no trailing terminator)
        lifted = "a\nb\n\\\nc\nd\n\n"
        unlifted = nsv.unlift(lifted)

        # Should be back to 2 rows
        parsed = nsv.loads(unlifted)
        self.assertEqual(2, len(parsed))
        self.assertEqual(["a", "b"], parsed[0])
        self.assertEqual(["c", "d"], parsed[1])

    def test_roundtrip_property(self):
        """Test that unlift(lift(x)) = x."""
        test_cases = [
            "a\nb\nc\n\nd\ne\nf\n\n",  # 2 rows
            "single\n\n",  # 1 row, 1 cell
            "\\\n\n",  # 1 row, 1 empty cell
            "a\n\\\nb\n\n",  # 1 row with empty cell
        ]

        for original in test_cases:
            with self.subTest(original=original):
                lifted = nsv.lift(original)
                unlifted = nsv.unlift(lifted)
                self.assertEqual(original, unlifted)

    def test_double_lift_2d_to_0d(self):
        """Test double lift: 2D → 1D → repeated lift."""
        # Start with 2D
        original = "a\nb\n\nc\nd\n\n"

        # First lift: 2D → 1D (5 cells, terminator stripped)
        once_lifted = nsv.lift(original)
        parsed = nsv.loads(once_lifted)
        self.assertEqual(1, len(parsed))  # One row
        self.assertEqual(5, len(parsed[0]))  # 5 cells (no cascade)

        # Second lift: same 5 cells (no growth from terminator)
        twice_lifted = nsv.lift(once_lifted)
        parsed = nsv.loads(twice_lifted)
        self.assertEqual(1, len(parsed))  # One row
        self.assertEqual(5, len(parsed[0]))  # Still 5 cells (no cascade!)

        # Double unlift to recover
        once_unlifted = nsv.unlift(twice_lifted)
        twice_unlifted = nsv.unlift(once_unlifted)
        self.assertEqual(original, twice_unlifted)

    def test_lift_with_empty_cells(self):
        """Test lift handles empty cells correctly."""
        original = "\\\ng\n\\\n\n"  # One row: ["", "g", ""]
        lifted = nsv.lift(original)

        parsed = nsv.loads(lifted)
        self.assertEqual(1, len(parsed))
        # Should be 3 cells: "\\", "g", "\\" (terminator stripped)
        self.assertEqual(["\\", "g", "\\"], parsed[0])

        # Round-trip
        unlifted = nsv.unlift(lifted)
        self.assertEqual(original, unlifted)

    def test_lift_with_special_chars(self):
        """Test lift with newlines and backslashes in cells."""
        # Row with cells containing newlines and backslashes
        original = nsv.dumps([["line1\nline2", "path\\to\\file"]])

        lifted = nsv.lift(original)
        unlifted = nsv.unlift(lifted)

        self.assertEqual(original, unlifted)

    def test_unlift_requires_one_row(self):
        """Test unlift fails with multiple rows."""
        # 2 rows
        two_rows = "a\n\nb\n\n"

        with self.assertRaises(ValueError):
            nsv.unlift(two_rows)

    def test_one_row_lift(self):
        """Test lifting a 1D NSV (one row)."""
        # 1 row, 3 cells
        original = "a\nb\nc\n\n"

        lifted = nsv.lift(original)
        parsed = nsv.loads(lifted)

        # Should be 1 row with 3 cells (terminator stripped)
        self.assertEqual(1, len(parsed))
        self.assertEqual(["a", "b", "c"], parsed[0])

        # Round-trip
        unlifted = nsv.unlift(lifted)
        self.assertEqual(original, unlifted)

    def test_triple_lift(self):
        """Test lifting three times."""
        original = "a\nb\n\nc\nd\n\n"  # 2 rows

        lift1 = nsv.lift(original)  # 2D → 1D
        lift2 = nsv.lift(lift1)     # 1D → 0D
        lift3 = nsv.lift(lift2)     # 0D → more escaped

        # Triple unlift
        unlift1 = nsv.unlift(lift3)
        unlift2 = nsv.unlift(unlift1)
        unlift3 = nsv.unlift(unlift2)

        self.assertEqual(original, unlift3)

    def test_combining_multiple_files(self):
        """Test the ENSV use case: multiple NSV files → lifted → combined."""
        # Two separate 2D files
        file1 = "a\nb\n\nc\nd\n\n"
        file2 = "e\nf\n\ng\nh\n\n"

        # Lift each (2D → 1D)
        lifted1 = nsv.lift(file1)
        lifted2 = nsv.lift(file2)

        # Parse to verify each is 1 row
        self.assertEqual(1, len(nsv.loads(lifted1)))
        self.assertEqual(1, len(nsv.loads(lifted2)))

        # To combine them, we put both lifted NSV strings as cells in one row
        # Each lifted string should be stored as a cell
        combined = nsv.dumps([[lifted1, lifted2]])

        # The combined file has 2 cells
        parsed = nsv.loads(combined)
        self.assertEqual(1, len(parsed))
        self.assertEqual(2, len(parsed[0]))

        # Each cell contains a lifted NSV string that can be unlifted
        cell1_content = parsed[0][0]
        cell2_content = parsed[0][1]

        # Unlift each to get back the original files
        cell1_unlifted = nsv.unlift(cell1_content)
        cell2_unlifted = nsv.unlift(cell2_content)

        self.assertEqual(file1, cell1_unlifted)
        self.assertEqual(file2, cell2_unlifted)

    def test_dimension_collapsing(self):
        """Verify lift collapses exactly one dimension per application."""
        # 3D: 3 rows
        nsv_3d = "a\nb\n\nc\nd\n\ne\nf\n\n"
        data_3d = nsv.loads(nsv_3d)
        self.assertEqual(3, len(data_3d))  # 3 rows

        # 2D: 1 row with 8 cells (terminator stripped)
        nsv_2d = nsv.lift(nsv_3d)
        data_2d = nsv.loads(nsv_2d)
        self.assertEqual(1, len(data_2d))  # 1 row
        self.assertEqual(8, len(data_2d[0]))  # 8 cells (no trailing terminator)

        # 1D: lift again - same cell count (no cascade!)
        nsv_1d = nsv.lift(nsv_2d)
        data_1d = nsv.loads(nsv_1d)
        self.assertEqual(1, len(data_1d))  # Still 1 row
        self.assertEqual(8, len(data_1d[0]))  # Still 8 cells (no growth)

        # Reverse
        recovered_2d = nsv.unlift(nsv_1d)
        self.assertEqual(nsv_2d, recovered_2d)

        recovered_3d = nsv.unlift(recovered_2d)
        self.assertEqual(nsv_3d, recovered_3d)


if __name__ == '__main__':
    unittest.main()
