import unittest
import os
import nsv
from test_utils import SAMPLES_DIR, SAMPLES_DATA, dump_then_load

class TestEdgeCases(unittest.TestCase):
    def test_long_strings(self):
        """Test handling of long string values."""
        long_string = ''.join(chr(x) for x in range(11, 0x110000))
        data = [
            ["normal", long_string],
            [long_string, "normal"]
        ]
        self.assertEqual(data, dump_then_load(data))

    def test_special_characters(self):
        """Test handling of special characters in field values."""
        file_path = os.path.join(SAMPLES_DIR, 'special_chars.nsv')
        with open(file_path, 'r') as f:
            rows = nsv.load(f)
        self.assertEqual(SAMPLES_DATA['special_chars'], rows)

    # def test_numeric_values(self):
    #     """Test handling of numeric values."""
    #     data = [
    #         [1, 2, 3],
    #         [4.5, 6.7, 8.9]
    #     ]
    #     actual = dump_then_load(data)
    #
    #     # Note: We expect strings back since NSV is text-based
    #     self.assertEqual([["1", "2", "3"], ["4.5", "6.7", "8.9"]], actual)


if __name__ == '__main__':
    unittest.main()