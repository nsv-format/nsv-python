import unittest
import nsv


class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift(self):
        """lift flattens 2D data to 1D list of escaped lines."""
        data = [["a", "b"], ["c"]]
        result = nsv.lift(data)
        # Row 0: 'a', 'b', then separator '', then row 1: 'c'
        self.assertEqual(result, ["a", "b", "", "c"])

    def test_basic_unlift(self):
        """unlift reconstructs 2D data from 1D list."""
        lines = ["a", "b", "", "c"]
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
        self.assertEqual(lifted, ["\\", "g", "\\"])

    def test_lift_with_special_chars(self):
        """lift handles strings with newlines and backslashes."""
        data = [["line1\nline2"], ["path\\to\\file"]]
        lifted = nsv.lift(data)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_empty_rows(self):
        """lift/unlift handle empty rows."""
        data = [[], ["a"], []]
        lifted = nsv.lift(data)
        # Row 0 (empty): nothing
        # Separator: ''
        # Row 1: 'a'
        # Separator: ''
        # Row 2 (empty): nothing
        self.assertEqual(lifted, ["", "a", ""])

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_single_row(self):
        """lift handles single row (no separators)."""
        data = [["x", "y", "z"]]
        lifted = nsv.lift(data)
        self.assertEqual(lifted, ["x", "y", "z"])

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)

    def test_empty_data(self):
        """lift handles completely empty data."""
        # Empty list of rows
        self.assertEqual(nsv.lift([]), [])

        # Single empty row
        self.assertEqual(nsv.lift([[]]), [])

    def test_unlift_empty(self):
        """unlift handles empty input."""
        # Empty list creates single empty row
        result = nsv.unlift([])
        self.assertEqual(result, [[]])

    def test_multiple_rows(self):
        """lift/unlift work with many rows."""
        data = [["a"], ["b"], ["c"], ["d"]]
        lifted = nsv.lift(data)
        # Should have 3 separators (n-1)
        self.assertEqual(lifted.count(""), 3)
        self.assertEqual(len(lifted), 7)  # 4 cells + 3 separators

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, data)


if __name__ == '__main__':
    unittest.main()
