import unittest

from nsv.util import spill, unspill, escape_seqseq, unescape_seqseq


class TestGenericSpill(unittest.TestCase):

    def test_spill_invertibility(self):
        """Test unspill ∘ spill = id for properly terminated sequences."""
        cases = [
            ([], ''),                  # Empty seqseq
            ([[]], ''),                # Single empty row
            ([[], []], ''),            # Two empty rows
            ([['a']], ''),             # Single element
            ([['a', 'b'], ['c']], ''), # Multiple rows
            ([['a'], [], ['b']], ''),  # Mixed empty/non-empty
        ]

        for seqseq, marker in cases:
            with self.subTest(seqseq=seqseq, marker=marker):
                spilled = spill(seqseq, marker)
                recovered = unspill(spilled, marker)
                self.assertEqual(list(map(list, seqseq)), recovered)

    def test_unspill_invertibility(self):
        """Test spill ∘ unspill = id for properly terminated sequences."""
        cases = [
            ([], ''),                      # Empty sequence
            ([''], ''),                    # Single terminator (one empty row)
            (['', ''], ''),                # Two empty rows
            (['a', ''], ''),               # Single element, one row
            (['a', 'b', '', 'c', ''], ''), # Multiple rows
            (['a', '', '', 'b', ''], ''),  # Empty row in middle
        ]

        for seq, marker in cases:
            with self.subTest(seq=seq, marker=marker):
                unspilled = unspill(seq, marker)
                recovered = spill(unspilled, marker)
                self.assertEqual(seq, recovered)

    def test_spill_with_different_types(self):
        """Test spill[T, marker] works with different types."""
        # spill[String, '']
        strings_2d = [['a', 'b'], ['c']]
        result = spill(strings_2d, '')
        expected = ['a', 'b', '', 'c', '']
        self.assertEqual(expected, result)

        # spill[Char, '\n']
        strings = ['hello', 'world']
        result = spill(strings, '\n')
        expected = ['h', 'e', 'l', 'l', 'o', '\n', 'w', 'o', 'r', 'l', 'd', '\n']
        self.assertEqual(expected, result)

        # spill[Int, -1]
        ints = [[1, 2], [3]]
        result = spill(ints, -1)
        expected = [1, 2, -1, 3, -1]
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
