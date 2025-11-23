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
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if line == "":
                    # Append row unless we're on the very last line with empty current
                    if current or i < len(lines) - 1:
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

        # Test with empty row
        result = decode_2("\na\n\n")
        self.assertEqual(result, [[], ["a"]])

    def test_theorem_1_lift_equals_encode_1(self):
        """Theorem 1: lift = encode[1]"""
        def encode_0(s): return escape(s)

        def encode_1(seq):
            return "".join(encode_0(cell) + "\n" for cell in seq) + "\n"

        # Test with raw string sequences
        test_cases = [
            ["a", "b", "c"],
            ["hello", "", "world"],
            ["\\", "\n", "text"],
            [],
        ]

        for seq in test_cases:
            with self.subTest(seq=seq):
                self.assertEqual(lift(seq), encode_1(seq))

    def test_theorem_2_unlift_equals_decode_1(self):
        """Theorem 2: unlift = decode[1]"""
        def decode_0(s): return unescape(s)

        def decode_1(text):
            cells = []
            for line in text.split("\n"):
                if line == "":
                    break
                cells.append(decode_0(line))
            return cells

        # Test with NSV-encoded rows
        test_cases = [
            ("a\nb\nc\n\n", ["a", "b", "c"]),
            ("a\n\\\nc\n\n", ["a", "", "c"]),
            ("a\n\\\\\n\\n\n\n", ["a", "\\", "\n"]),
            ("\n", []),
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                self.assertEqual(unlift(text), decode_1(text))
                self.assertEqual(unlift(text), expected)

    def test_theorem_3_dumps_via_lift(self):
        """Theorem 3: dumps = concat ∘ (map encode[1])"""
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
            with self.subTest(seqseq=seqseq):
                self.assertEqual(dumps(seqseq), dumps_via_encode_1(seqseq))

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
            with self.subTest(seqseq=seqseq):
                self.assertEqual(encode_2_direct(seqseq), encode_2_via_dumps(seqseq))

    def test_theorem_5_dumps_equals_concat_map_lift(self):
        """Theorem 5: dumps(rows) = concat(map(lift, rows))"""
        test_cases = [
            [["a", "b"], ["c", "d"]],
            [["x"], ["y", "z"]],
            [["", "a"], ["b", ""]],
            [[]],
        ]

        for rows in test_cases:
            with self.subTest(rows=rows):
                dumps_result = dumps(rows)
                manual_result = "".join(lift(row) for row in rows)
                self.assertEqual(dumps_result, manual_result)

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

    def test_lift_unlift_inverse(self):
        """Test that lift and unlift are inverses."""
        test_cases = [
            ["a", "b", "c"],
            [""],
            [],
            ["v 1", "bool true false", "", "columns id name"],
        ]

        for seq in test_cases:
            with self.subTest(seq=seq):
                self.assertEqual(unlift(lift(seq)), seq)

    def test_lift_as_quoting(self):
        """Test that lift 'quotes' file lines as NSV cells."""
        # Simulated metadata file content (as lines)
        metadata_lines = ["v 1", "bool true false", "", "columns id name"]

        # Lift these lines into a single NSV row
        lifted = lift(metadata_lines)

        # Should be encoded as cells
        expected = "v 1\nbool true false\n\\\ncolumns id name\n\n"
        self.assertEqual(lifted, expected)

        # Unlift should recover the original lines
        self.assertEqual(unlift(lifted), metadata_lines)

    def test_ensv_metadata_lifting(self):
        """Test lift for combining metadata + data into ENSV."""
        # Metadata as lines
        metadata = ["v 1", "columns id name", "types int str"]

        # Data as 2D
        data = [["1", "Alice"], ["2", "Bob"]]

        # Combine: lift(metadata) + dumps(data)
        ensv = lift(metadata) + dumps(data)

        # Parse back
        all_rows = loads(ensv)

        # First row is lifted metadata
        self.assertEqual(all_rows[0], metadata)

        # Rest is data
        self.assertEqual(all_rows[1:], data)


if __name__ == "__main__":
    unittest.main()
