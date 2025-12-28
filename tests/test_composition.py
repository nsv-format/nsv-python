import unittest

import nsv
from nsv.util import spill, unspill, escape_seqseq, unescape_seqseq
from test_utils import SAMPLES_DATA


class TestComposition(unittest.TestCase):
    """Test that dumps/loads match their decomposition."""

    def test_encode_decomposition(self):
        """Test dumps = spill[Char, '\n'] ∘ spill[String, ''] ∘ escape_seqseq."""
        for name, seqseq in SAMPLES_DATA.items():
            with self.subTest(sample=name):
                expected = nsv.dumps(seqseq)

                escaped = escape_seqseq(seqseq)
                spilled_structure = spill(escaped, '')
                actual = ''.join(spill(spilled_structure, '\n'))

                self.assertEqual(expected, actual)

    def test_decode_decomposition(self):
        """Test loads = unescape_seqseq ∘ unspill[String, ''] ∘ unspill[Char, '\n']."""
        for name, seqseq in SAMPLES_DATA.items():
            with self.subTest(sample=name):
                encoded = nsv.dumps(seqseq)
                expected = nsv.loads(encoded)

                deserialized = [''.join(chars) for chars in unspill(encoded, '\n')]
                unspilled_structure = unspill(deserialized, '')
                actual = unescape_seqseq(unspilled_structure)

                self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
