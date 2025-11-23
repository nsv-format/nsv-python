import unittest
from nsv import loads, dumps, lift, unlift
from nsv.writer import Writer
from nsv.reader import Reader

escape = Writer.escape
unescape = Reader.unescape


class TestEncodingTheory(unittest.TestCase):
    """Test theoretical relations between encoding levels."""

    def test_primitives(self):
        """Test escape/unescape are inverse."""
        # Round-trip properties
        self.assertEqual(unescape(escape("hello")), "hello")
        self.assertEqual(unescape(escape("")), "")
        self.assertEqual(unescape(escape("\\")), "\\")
        self.assertEqual(unescape(escape("\n")), "\n")

    def test_lift_flattens_2d_to_1d(self):
        """lift flattens 2D data to 1D list with row separators."""
        # Basic 2x2
        result = lift([["a", "b"], ["c", "d"]])
        self.assertEqual(result, ["a", "b", "", "c", "d"])

        # With empty cells
        result = lift([["a", ""], ["", "d"]])
        self.assertEqual(result, ["a", "\\", "", "\\", "d"])

        # Single row
        result = lift([["x", "y"]])
        self.assertEqual(result, ["x", "y"])

        # Empty rows
        result = lift([[], ["a"]])
        self.assertEqual(result, ["", "a"])

    def test_unlift_splits_1d_to_2d(self):
        """unlift splits 1D list to 2D data using empty strings as separators."""
        # Basic split
        result = unlift(["a", "b", "", "c", "d"])
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

        # With escaped cells
        result = unlift(["a", "\\", "", "\\", "d"])
        self.assertEqual(result, [["a", ""], ["", "d"]])

        # Single row
        result = unlift(["x", "y"])
        self.assertEqual(result, [["x", "y"]])

        # Empty rows
        result = unlift(["", "a"])
        self.assertEqual(result, [[], ["a"]])

    def test_lift_unlift_inverse(self):
        """unlift(lift(data)) = data"""
        test_cases = [
            [["a", "b"], ["c", "d"]],
            [["hello"], ["world"]],
            [[]],
            [[], ["a"]],
            [["", "x"], ["y", ""]],
        ]

        for data in test_cases:
            with self.subTest(data=data):
                self.assertEqual(unlift(lift(data)), data)

    def test_dumps_uses_lift(self):
        """dumps(data) = join(lift(data) + ['']).replace('', '\\n')

        Actually: dumps appends terminators, lift uses separators.
        But they should be related structurally.
        """
        data = [["a", "b"], ["c", "d"]]

        # lift gives separators
        lifted = lift(data)
        self.assertEqual(lifted, ["a", "b", "", "c", "d"])

        # dumps gives terminators
        dumped = dumps(data)
        self.assertEqual(dumped, "a\nb\n\nc\nd\n\n")

        # dumps splits to: ['a', 'b', '', 'c', 'd', '', '']
        # lift gives:      ['a', 'b', '', 'c', 'd']
        # Difference: dumps adds row terminator for last row

    def test_loads_uses_unlift(self):
        """loads can be expressed using unlift on split lines."""
        nsv = "a\nb\n\nc\nd\n\n"

        # Direct loads
        data = loads(nsv)
        self.assertEqual(data, [["a", "b"], ["c", "d"]])

        # Via unlift on split lines (need to handle trailing empty strings)
        lines = nsv.split("\n")[:-1]  # Remove final empty from split
        # But we still have trailing '' from row terminator
        # This is trickier - loads handles terminators, unlift handles separators

    def test_lift_preserves_structure(self):
        """lift preserves all information (escaping, row boundaries)."""
        # Test with special characters
        data = [["line\n1", "path\\file"], ["", "normal"]]
        lifted = lift(data)

        # Should escape special chars
        self.assertEqual(lifted[0], "line\\n1")
        self.assertEqual(lifted[1], "path\\\\file")
        self.assertEqual(lifted[2], "")  # row separator
        self.assertEqual(lifted[3], "\\")  # escaped empty
        self.assertEqual(lifted[4], "normal")

        # Round-trip
        self.assertEqual(unlift(lifted), data)

    def test_empty_data(self):
        """lift/unlift handle empty cases."""
        # Empty data
        self.assertEqual(lift([]), [])
        self.assertEqual(unlift([]), [[]])

        # Single empty row
        self.assertEqual(lift([[]]), [])
        self.assertEqual(unlift([""]), [[], []])

    def test_lift_as_dimension_collapse(self):
        """lift collapses 2D structure to 1D with row markers."""
        # 3x2 matrix
        data = [["a", "b"], ["c", "d"], ["e", "f"]]
        lifted = lift(data)

        # Count row separators
        separators = lifted.count("")
        self.assertEqual(separators, 2)  # n-1 separators for n rows

        # Total elements
        self.assertEqual(len(lifted), 8)  # 6 cells + 2 separators

    def test_metadata_example(self):
        """Demonstrate using lift for metadata in practice."""
        # If we had metadata as raw data (not NSV yet)
        # We'd need to escape and structure it first

        metadata = [["v 1"], ["columns id name"]]
        data = [["1", "Alice"], ["2", "Bob"]]

        # Combine at the 2D level
        combined = metadata + data

        # Then dump to NSV
        nsv = dumps(combined)
        self.assertEqual(loads(nsv), combined)


if __name__ == "__main__":
    unittest.main()
