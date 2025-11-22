import unittest
import nsv

class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift(self):
        """Test basic lift operation with simple strings."""
        cells = ["a", "b", "c"]
        result = nsv.lift(cells)
        expected = "a\nb\nc\n\n"
        self.assertEqual(expected, result)

    def test_basic_unlift(self):
        """Test basic unlift operation."""
        row_str = "a\nb\nc\n\n"
        result = nsv.unlift(row_str)
        expected = ["a", "b", "c"]
        self.assertEqual(expected, result)

    def test_lift_with_empty_cell(self):
        """Test lift with empty cells."""
        cells = ["a", "b", "", "d"]
        result = nsv.lift(cells)
        expected = "a\nb\n\\\nd\n\n"
        self.assertEqual(expected, result)

    def test_unlift_with_empty_cell(self):
        """Test unlift with empty cells."""
        row_str = "a\nb\n\\\nd\n\n"
        result = nsv.unlift(row_str)
        expected = ["a", "b", "", "d"]
        self.assertEqual(expected, result)

    def test_lift_with_newlines(self):
        """Test lift with cells containing newlines."""
        cells = ["line1\nline2", "simple", "multi\nline\ntext"]
        result = nsv.lift(cells)
        expected = "line1\\nline2\nsimple\nmulti\\nline\\ntext\n\n"
        self.assertEqual(expected, result)

    def test_unlift_with_newlines(self):
        """Test unlift with escaped newlines."""
        row_str = "line1\\nline2\nsimple\nmulti\\nline\\ntext\n\n"
        result = nsv.unlift(row_str)
        expected = ["line1\nline2", "simple", "multi\nline\ntext"]
        self.assertEqual(expected, result)

    def test_lift_with_backslashes(self):
        """Test lift with cells containing backslashes."""
        cells = ["path\\to\\file", "normal", "c:\\windows"]
        result = nsv.lift(cells)
        expected = "path\\\\to\\\\file\nnormal\nc:\\\\windows\n\n"
        self.assertEqual(expected, result)

    def test_unlift_with_backslashes(self):
        """Test unlift with escaped backslashes."""
        row_str = "path\\\\to\\\\file\nnormal\nc:\\\\windows\n\n"
        result = nsv.unlift(row_str)
        expected = ["path\\to\\file", "normal", "c:\\windows"]
        self.assertEqual(expected, result)

    def test_lift_with_mixed_escapes(self):
        """Test lift with both newlines and backslashes."""
        cells = ["text\\nwith\\backslash", "normal", ""]
        result = nsv.lift(cells)
        expected = "text\\\\nwith\\\\backslash\nnormal\n\\\n\n"
        self.assertEqual(expected, result)

    def test_unlift_with_mixed_escapes(self):
        """Test unlift with both types of escapes."""
        row_str = "text\\\\nwith\\\\backslash\nnormal\n\\\n\n"
        result = nsv.unlift(row_str)
        expected = ["text\\nwith\\backslash", "normal", ""]
        self.assertEqual(expected, result)

    def test_roundtrip_property(self):
        """Test that unlift(lift(x)) = x for various inputs."""
        test_cases = [
            ["a", "b", "c"],
            ["", "", ""],
            ["single"],
            [],
            ["has\nnewline", "has\\backslash", "has\nboth\\things"],
            ["Roses are red\nViolets are blue", "This may be pain", "But CSV would be, too"],
            ["Tab\tseparated\tvalues"],
        ]

        for cells in test_cases:
            with self.subTest(cells=cells):
                lifted = nsv.lift(cells)
                unlifted = nsv.unlift(lifted)
                self.assertEqual(cells, unlifted)

    def test_empty_row(self):
        """Test lift and unlift with empty row."""
        cells = []
        result = nsv.lift(cells)
        expected = "\n"
        self.assertEqual(expected, result)

        # Reverse
        unlifted = nsv.unlift(result)
        self.assertEqual(cells, unlifted)

    def test_single_empty_cell(self):
        """Test lift and unlift with single empty cell."""
        cells = [""]
        result = nsv.lift(cells)
        expected = "\\\n\n"
        self.assertEqual(expected, result)

        # Reverse
        unlifted = nsv.unlift(result)
        self.assertEqual(cells, unlifted)

    def test_multiple_empty_cells(self):
        """Test lift and unlift with multiple empty cells."""
        cells = ["", "", ""]
        result = nsv.lift(cells)
        expected = "\\\n\\\n\\\n\n"
        self.assertEqual(expected, result)

        # Reverse
        unlifted = nsv.unlift(result)
        self.assertEqual(cells, unlifted)

    def test_example_from_spec(self):
        """Test the exact example from the specification."""
        cells = ["a", "b", "", "d"]
        result = nsv.lift(cells)
        # Expected from spec: "a\nb\n\\\nd\n\n"
        expected = "a\nb\n\\\nd\n\n"
        self.assertEqual(expected, result)

        # Verify roundtrip
        unlifted = nsv.unlift(result)
        self.assertEqual(cells, unlifted)

    def test_complex_text(self):
        """Test with complex real-world text."""
        cells = [
            "first",
            "Roses are red\nViolets are blue\nThis may be pain\nBut CSV would be, too",
            "Tab\tseparated\tvalues\n(would be left as-is normally)",
            "Not a newline: \\n"
        ]
        lifted = nsv.lift(cells)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(cells, unlifted)

    def test_unlift_without_trailing_newline(self):
        """Test unlift handles strings without trailing newline."""
        row_str = "a\nb\nc\n"  # Missing the final newline
        result = nsv.unlift(row_str)
        expected = ["a", "b", "c"]
        self.assertEqual(expected, result)

    def test_unicode_characters(self):
        """Test lift and unlift with unicode characters."""
        cells = ["hello", "世界", "🌍", "café"]
        lifted = nsv.lift(cells)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(cells, unlifted)

    def test_lift_preserves_nsv_structure(self):
        """Verify that lift output is a valid single NSV row."""
        cells = ["a", "b", "c"]
        lifted = nsv.lift(cells)

        # Parse it as NSV - should give us a single row
        parsed = nsv.loads(lifted)
        self.assertEqual(1, len(parsed))
        self.assertEqual(cells, parsed[0])


if __name__ == '__main__':
    unittest.main()
