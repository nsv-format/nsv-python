import unittest
import nsv


class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift(self):
        """lift flattens 2D data with row terminators."""
        data = [["a", "b"], ["c"]]
        result = nsv.lift(data)
        # Row 0: 'a', 'b', terminator ''
        # Row 1: 'c', terminator ''
        self.assertEqual(result, ["a", "b", "", "c", ""])

    def test_basic_unlift(self):
        """unlift reconstructs 2D data from terminated 1D list."""
        lines = ["a", "b", "", "c", ""]
        result = nsv.unlift(lines)
        self.assertEqual(result, [["a", "b"], ["c"]])

    def test_roundtrip_property(self):
        """unlift(lift(data)) = data"""
        test_cases = [
            [["a", "b", "c"]],
            [["hello"], ["world"]],
            [[""]],
            [[], ["a"]],
            [["", "x"], ["y", ""]],
        ]
        for data in test_cases:
            with self.subTest(data=data):
                self.assertEqual(nsv.unlift(nsv.lift(data)), data)

    def test_lift_with_empty_cells(self):
        """lift escapes empty cells as backslash."""
        data = [["", "g", ""]]
        lifted = nsv.lift(data)
        # Empty cells escaped, plus terminator
        self.assertEqual(lifted, ["\\", "g", "\\", ""])

    def test_lift_with_special_chars(self):
        """lift handles strings with newlines and backslashes."""
        data = [["line1\nline2"], ["path\\to\\file"]]
        lifted = nsv.lift(data)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_empty_rows(self):
        """lift/unlift handle empty rows (just terminators)."""
        # Single empty row
        data = [[]]
        lifted = nsv.lift(data)
        self.assertEqual(lifted, [""])

        # Multiple empty rows
        data = [[], ["a"], []]
        lifted = nsv.lift(data)
        # Row 0 (empty): terminator
        # Row 1: 'a', terminator
        # Row 2 (empty): terminator
        self.assertEqual(lifted, ["", "a", "", ""])

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_single_row(self):
        """lift handles single row (one terminator)."""
        data = [["x", "y", "z"]]
        lifted = nsv.lift(data)
        self.assertEqual(lifted, ["x", "y", "z", ""])

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_terminators_not_separators(self):
        """lift uses n terminators for n rows, not n-1 separators."""
        # 1 row -> 1 terminator
        self.assertEqual(nsv.lift([["a"]]).count(""), 1)

        # 2 rows -> 2 terminators
        self.assertEqual(nsv.lift([["a"], ["b"]]).count(""), 2)

        # 3 rows -> 3 terminators
        self.assertEqual(nsv.lift([["a"], ["b"], ["c"]]).count(""), 3)

    def test_unlift_incomplete_sequence(self):
        """unlift drops incomplete final row (unterminated)."""
        # Properly terminated
        result = nsv.unlift(["a", "b", ""])
        self.assertEqual(result, [["a", "b"]])

        # Missing terminator - incomplete row dropped
        result = nsv.unlift(["a", "b", "", "c"])
        self.assertEqual(result, [["a", "b"]])  # Only first row

    def test_empty_data(self):
        """lift handles empty data."""
        # Empty list of rows
        self.assertEqual(nsv.lift([]), [])

        # Single empty row
        self.assertEqual(nsv.lift([[]]), [""])


if __name__ == '__main__':
    unittest.main()
