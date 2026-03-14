import unittest

from nsv.ensv import lift, unlift
from nsv.util import escape_seqseq, spill
from test_utils import SAMPLES_DATA


# All non-empty samples — [] is irrepresentable by lift.
LIFT_SAMPLES = {k: v for k, v in SAMPLES_DATA.items() if v}


class TestLift(unittest.TestCase):

    def test_single_row_single_cell(self):
        self.assertEqual(['a'], lift([['a']]))

    def test_single_row_multiple_cells(self):
        self.assertEqual(['a', 'b', 'c'], lift([['a', 'b', 'c']]))

    def test_multiple_rows(self):
        self.assertEqual(
            ['a', 'b', '', 'c', 'd'],
            lift([['a', 'b'], ['c', 'd']]),
        )

    def test_ragged_rows(self):
        self.assertEqual(
            ['a', 'b', '', 'c'],
            lift([['a', 'b'], ['c']]),
        )

    def test_single_empty_row(self):
        """[[]] lifts to [] — the single empty row becomes an empty sequence."""
        self.assertEqual([], lift([[]]))

    def test_two_empty_rows(self):
        self.assertEqual([''], lift([[], []]))

    def test_three_empty_rows(self):
        self.assertEqual(['', ''], lift([[], [], []]))

    def test_empty_row_between_data(self):
        self.assertEqual(
            ['a', '', '', 'b'],
            lift([['a'], [], ['b']]),
        )

    def test_escaping_backslash(self):
        self.assertEqual(['a\\\\b'], lift([['a\\b']]))

    def test_escaping_newline(self):
        self.assertEqual(['a\\nb'], lift([['a\nb']]))

    def test_escaping_empty_cell(self):
        self.assertEqual(['\\'], lift([['']]))

    def test_escaping_multiple_specials(self):
        result = lift([['a\\b', 'c\nd'], ['', 'e']])
        self.assertEqual(['a\\\\b', 'c\\nd', '', '\\', 'e'], result)


class TestUnlift(unittest.TestCase):

    def test_single_element(self):
        self.assertEqual([['a']], unlift(['a']))

    def test_multiple_elements_single_row(self):
        self.assertEqual([['a', 'b', 'c']], unlift(['a', 'b', 'c']))

    def test_multiple_rows(self):
        self.assertEqual(
            [['a', 'b'], ['c', 'd']],
            unlift(['a', 'b', '', 'c', 'd']),
        )

    def test_empty_input(self):
        """Empty input unlifts to [[]] — terminates the (empty) current row."""
        self.assertEqual([[]], unlift([]))

    def test_single_separator(self):
        """A single empty string produces two empty rows."""
        self.assertEqual([[], []], unlift(['']))

    def test_unescaping_backslash(self):
        self.assertEqual([['a\\b']], unlift(['a\\\\b']))

    def test_unescaping_newline(self):
        self.assertEqual([['a\nb']], unlift(['a\\nb']))

    def test_unescaping_empty_cell(self):
        self.assertEqual([['']], unlift(['\\']))

    def test_trailing_separator(self):
        self.assertEqual([['a'], []], unlift(['a', '']))


class TestLiftUnliftRoundtrip(unittest.TestCase):
    """unlift(lift(x)) == x for all non-empty seqseqs."""

    def test_roundtrip(self):
        for name, seqseq in LIFT_SAMPLES.items():
            with self.subTest(name=name):
                self.assertEqual(seqseq, unlift(lift(seqseq)))

    def test_lift_produces_no_newlines(self):
        for name, seqseq in LIFT_SAMPLES.items():
            with self.subTest(name=name):
                for cell in lift(seqseq):
                    self.assertNotIn('\n', cell)


class TestUnliftLiftRoundtrip(unittest.TestCase):
    """lift(unlift(y)) == y for valid lifted sequences."""

    CASES = [
        ['a'],
        ['a', 'b'],
        ['a', 'b', '', 'c'],
        ['a', '', '', 'b'],
        [''],
        ['', ''],
        ['a', ''],
        ['\\'],
        ['a\\\\b', 'c\\nd'],
        ['a\\\\b', 'c\\nd', '', '\\', 'e'],
    ]

    def test_roundtrip(self):
        for seq in self.CASES:
            with self.subTest(seq=seq):
                self.assertEqual(seq, lift(unlift(seq)))


class TestLiftDecomposition(unittest.TestCase):
    """Verify equivalence: lift = init . spill[String, ''] . map(map(escape))."""

    def test_equivalence(self):
        for name, seqseq in LIFT_SAMPLES.items():
            with self.subTest(name=name):
                via_decomposition = spill(escape_seqseq(seqseq), '')[:-1]
                self.assertEqual(via_decomposition, lift(seqseq))


if __name__ == '__main__':
    unittest.main()
