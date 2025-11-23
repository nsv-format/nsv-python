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
        encode_0 = escape
        decode_0 = unescape

        # Round-trip properties
        self.assertEqual(decode_0(encode_0("hello")), "hello")
        self.assertEqual(decode_0(encode_0("")), "")
        self.assertEqual(decode_0(encode_0("\\")), "\\")
        self.assertEqual(decode_0(encode_0("\n")), "\n")

    def test_encode_1(self):
        """Test encode_1 encodes Seq[String] → String."""
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        # Test basic sequence
        result = encode_1(["a", "b", "c"])
        self.assertEqual(result, "a\nb\nc\n\n")

        # Test with empty cell
        result = encode_1(["a", "", "c"])
        self.assertEqual(result, "a\n\\\nc\n\n")

        # Test with special characters
        result = encode_1(["a", "\\", "\n"])
        self.assertEqual(result, "a\n\\\\\n\\n\n\n")

    def test_decode_1(self):
        """Test decode_1 decodes String → Seq[String] (first row)."""
        def decode_0(s): return unescape(s)

        def decode_1(text):
            cells = []
            for line in text.split("\n"):
                if line == "":
                    break
                cells.append(decode_0(line))
            return cells

        # Test basic sequence
        result = decode_1("a\nb\nc\n\n")
        self.assertEqual(result, ["a", "b", "c"])

        # Test with empty cell
        result = decode_1("a\n\\\nc\n\n")
        self.assertEqual(result, ["a", "", "c"])

        # Test with special characters
        result = decode_1("a\n\\\\\n\\n\n\n")
        self.assertEqual(result, ["a", "\\", "\n"])

    def test_encode_2(self):
        """Test encode_2 encodes Seq[Seq[String]] → String."""
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        def encode_2(seqseq):
            return "".join(encode_1(row) for row in seqseq)

        # Test 2x2 matrix
        result = encode_2([["a", "b"], ["c", "d"]])
        self.assertEqual(result, "a\nb\n\nc\nd\n\n")

        # Test with empty cells
        result = encode_2([["a", ""], ["", "d"]])
        self.assertEqual(result, "a\n\\\n\n\\\nd\n\n")

    def test_decode_2(self):
        """Test decode_2 decodes String → Seq[Seq[String]]."""
        def decode_0(s): return unescape(s)

        def decode_2(text):
            rows = []
            current = []
            for line in text.split("\n"):
                if line == "":
                    if current:
                        rows.append([decode_0(cell) for cell in current])
                        current = []
                else:
                    current.append(line)
            return rows

        # Test 2x2 matrix
        result = decode_2("a\nb\n\nc\nd\n\n")
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

        # Test with empty cells
        result = decode_2("a\n\\\n\n\\\nd\n\n")
        self.assertEqual(result, [["a", ""], ["", "d"]])

    def test_theorem_1_lift_equals_encode_1(self):
        """Theorem 1: lift = encode[1]

        lift treats NSV lines (already escaped) as raw data and re-encodes them.
        So lift(nsv) = encode_1(lines) where lines are the RAW line strings from nsv.
        """
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        # Test: lift treats NSV lines as data
        # If we have NSV "a\n\\\nc\n\n" (representing ["a", "", "c"])
        # The raw lines are ["a", "\\", "c"]
        # lift re-encapes these: ["a", "\\", "c"] -> "a\n\\\\\nc\n\n"

        nsv_input = "a\n\\\nc\n\n"
        # Raw lines (not unescaped, just split):
        raw_lines = nsv_input.split("\n")[:-1]  # ['a', '\\', 'c', '']
        if raw_lines and raw_lines[-1] == '':
            raw_lines = raw_lines[:-1]  # ['a', '\\', 'c']

        lifted = lift(nsv_input)
        expected = encode_1(raw_lines)

        self.assertEqual(lifted, expected)

    def test_theorem_2_unlift_equals_decode_1(self):
        """Theorem 2: unlift ∘ encode_1 = join_lines

        unlift decodes a single-row NSV and outputs the raw lines joined.
        This is the inverse of lift which encoded raw lines as cells.
        """
        def decode_0(s): return unescape(s)

        def decode_1(text):
            cells = []
            for line in text.split("\n"):
                if line == "":
                    break
                cells.append(decode_0(line))
            return cells

        # Test: if we encode ["a", "\\", "c"] at depth 1, we get "a\n\\\\\nc\n\n"
        # unlift should decode this and output the raw lines: "a\n\\\nc\n\n"

        encoded = "a\n\\\\\nc\n\n"  # This is encode_1(["a", "\\", "c"])
        unlifted = unlift(encoded)  # Should give us the raw lines back

        # The cells were ["a", "\\", "c"]
        # When joined as lines, we get "a\n\\\nc\n\n"
        expected_cells = decode_1(encoded)  # ["a", "\\", "c"]
        expected_output = "\n".join(expected_cells) + "\n\n"

        self.assertEqual(unlifted, expected_output)

    def test_theorem_3_dumps_via_lift(self):
        """Theorem 3: dumps = concat ∘ (map encode[1])

        This shows that encoding at depth 2 is the same as encoding each row at depth 1
        and concatenating the results.
        """
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        def dumps_via_encode_1(seqseq):
            """dumps = concat ∘ (map encode_1)"""
            return "".join(encode_1(row) for row in seqseq)

        # Test various 2D arrays
        test_cases = [
            [["a", "b"], ["c", "d"]],
            [["hello"], ["world"]],
            [["", "x"], ["y", ""]],
            [[]],
            [["single"]],
        ]

        for seqseq in test_cases:
            direct = dumps(seqseq)
            via_encode_1 = dumps_via_encode_1(seqseq)

            self.assertEqual(direct, via_encode_1,
                           f"dumps != dumps_via_encode_1 for {seqseq}")

    def test_theorem_4_encode_composition(self):
        """Theorem 4: encode[n+1] = concat ∘ (map encode[n])"""
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        def encode_2_direct(seqseq):
            return "".join(encode_1(row) for row in seqseq)

        def encode_2_via_dumps(seqseq):
            return dumps(seqseq)

        # Test that both definitions agree
        test_cases = [
            [["a", "b"], ["c", "d"]],
            [["x"]],
            [["", ""], ["", ""]],
        ]

        for seqseq in test_cases:
            direct = encode_2_direct(seqseq)
            via_dumps = encode_2_via_dumps(seqseq)

            self.assertEqual(direct, via_dumps,
                           f"encode_2 composition failed for {seqseq}")

    def test_roundtrip_at_all_levels(self):
        """Test decode ∘ encode = id at all levels."""
        def encode_0(s): return escape(s)
        def decode_0(s): return unescape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        def decode_1(text):
            cells = []
            for line in text.split("\n"):
                if line == "":
                    break
                cells.append(decode_0(line))
            return cells

        # Level 0
        for s in ["hello", "", "\\", "\n"]:
            self.assertEqual(decode_0(encode_0(s)), s)

        # Level 1
        for seq in [["a", "b"], [""], ["\\", "\n"]]:
            self.assertEqual(decode_1(encode_1(seq)), seq)

        # Level 2 (via dumps/loads)
        for seqseq in [[["a", "b"], ["c", "d"]], [[""]], [["\\", "\n"]]]:
            self.assertEqual(loads(dumps(seqseq)), seqseq)

    def test_lift_unlift_composition(self):
        """Test that lift/unlift compose correctly with dumps/loads."""
        # Start with 2D data
        data_2d = [["a", "b"], ["c", "d"]]

        # Encode to 2D NSV string
        nsv_2d = dumps(data_2d)

        # Lift to 1D (single row)
        nsv_1d = lift(nsv_2d)

        # Should be single row
        rows = loads(nsv_1d)
        self.assertEqual(len(rows), 1)

        # Unlift back to 2D
        nsv_2d_restored = unlift(nsv_1d)

        # Should match original
        self.assertEqual(nsv_2d_restored, nsv_2d)

        # Decode back to data
        data_2d_restored = loads(nsv_2d_restored)
        self.assertEqual(data_2d_restored, data_2d)

    def test_lift_as_quoting(self):
        """Test that lift 'quotes' structure by treating it as data."""
        # Start with data ["a", "\\", "c"] (where \\ is a backslash)
        data_1d = ["a", "\\", "c"]

        # Encode at depth 1: this creates NSV with escaped backslash
        nsv_1d = "a\n\\\\\nc\n\n"  # \\ becomes \\\\
        self.assertEqual(nsv_1d, dumps([data_1d]))

        # Now lift this: treats the NSV lines as raw data
        nsv_lifted = lift(nsv_1d)

        # The lines were ["a", "\\\\", "c"] (raw, including the escaping)
        # After lift, these become cells, so \\\\ gets escaped to \\\\\\\\
        expected = "a\n\\\\\\\\\nc\n\n"
        self.assertEqual(nsv_lifted, expected)

        # Verify round-trip
        self.assertEqual(unlift(nsv_lifted), nsv_1d)


if __name__ == "__main__":
    unittest.main()
