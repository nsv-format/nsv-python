import unittest
import nsv


class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift(self):
        """lift encodes a list of strings as a single NSV row."""
        seq = ["a", "b", "c"]
        lifted = nsv.lift(seq)
        self.assertEqual(lifted, "a\nb\nc\n\n")

        parsed = nsv.loads(lifted)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0], seq)

    def test_basic_unlift(self):
        """unlift decodes a single NSV row to a list of strings."""
        nsv_row = "a\nb\nc\n\n"
        result = nsv.unlift(nsv_row)
        self.assertEqual(result, ["a", "b", "c"])

    def test_roundtrip_property(self):
        """unlift(lift(seq)) = seq"""
        test_cases = [
            ["a", "b", "c"],
            ["hello", "world"],
            [""],
            ["", "empty", ""],
            ["\\", "\n", "special"],
            [],
        ]
        for seq in test_cases:
            with self.subTest(seq=seq):
                lifted = nsv.lift(seq)
                unlifted = nsv.unlift(lifted)
                self.assertEqual(unlifted, seq)

    def test_lift_with_empty_strings(self):
        """lift handles empty strings correctly."""
        seq = ["", "g", ""]
        lifted = nsv.lift(seq)
        self.assertEqual(lifted, "\\\ng\n\\\n\n")

        parsed = nsv.loads(lifted)
        self.assertEqual(parsed[0], seq)

    def test_lift_with_special_chars(self):
        """lift handles strings with newlines and backslashes."""
        seq = ["line1\nline2", "path\\to\\file", "both\n\\"]
        lifted = nsv.lift(seq)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, seq)

    def test_unlift_requires_one_row(self):
        """unlift raises ValueError if input has multiple rows."""
        two_rows = "a\n\nb\n\n"
        with self.assertRaises(ValueError):
            nsv.unlift(two_rows)

    def test_combining_sequences(self):
        """lift can encode multiple sequences as cells of a row."""
        seq1 = ["a", "b"]
        seq2 = ["c", "d"]

        # Lift each sequence
        lifted1 = nsv.lift(seq1)
        lifted2 = nsv.lift(seq2)

        # Combine as cells of a single row
        combined = nsv.dumps([[lifted1, lifted2]])

        # Parse and verify
        parsed = nsv.loads(combined)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]), 2)

        # Unlift each cell
        recovered1 = nsv.unlift(parsed[0][0])
        recovered2 = nsv.unlift(parsed[0][1])

        self.assertEqual(recovered1, seq1)
        self.assertEqual(recovered2, seq2)

    def test_3d_encoding(self):
        """Demonstrate 3D encoding via lift composition."""
        # 3D data: two 2x2 matrices
        matrices = [
            [["a", "b"], ["c", "d"]],
            [["e", "f"], ["g", "h"]],
        ]

        # Step 1: Encode each matrix as 2D NSV
        nsv_2d_list = [nsv.dumps(m) for m in matrices]

        # Step 2: Treat each NSV as lines and lift to get single rows
        # But wait - we need to think of the NSV string as lines
        # Actually, with new signature, we need to pass lists

        # Let's think differently: we want to combine the 2D NSVs as rows
        # Then lift the combined result

        # Encode each matrix as 2D, get the cell sequences
        row_sequences = [nsv.loads(nsv.dumps(m)) for m in matrices]

        # Flatten to create input for double-lift
        # Each matrix's rows become cells in a meta-structure

        # Actually, let's use a simpler approach:
        # Encode each matrix, then lift the list of NSV strings
        encoded_matrices = [nsv.dumps(m) for m in matrices]

        # Lift: treat the NSV strings as raw data
        lifted = nsv.lift(encoded_matrices)

        # Verify it's a single row
        parsed = nsv.loads(lifted)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]), 2)

        # Unlift to recover encoded matrices
        recovered_nsv = nsv.unlift(lifted)
        self.assertEqual(len(recovered_nsv), 2)

        # Decode each to recover original matrices
        recovered_matrices = [nsv.loads(nsv_str) for nsv_str in recovered_nsv]
        self.assertEqual(recovered_matrices, matrices)

    def test_no_double_encoding(self):
        """lift treats strings as raw data, even if they look like NSV."""
        # These strings happen to contain backslashes and newlines
        seq = ["\\\\", "\\n", "regular"]
        lifted = nsv.lift(seq)
        unlifted = nsv.unlift(lifted)

        # Should recover exactly what we put in
        self.assertEqual(unlifted, seq)

    def test_empty_sequence(self):
        """lift handles empty sequence."""
        lifted = nsv.lift([])
        self.assertEqual(lifted, "\n")

        unlifted = nsv.unlift(lifted)
        self.assertEqual(unlifted, [])


if __name__ == '__main__':
    unittest.main()
