import unittest
import os
import tempfile
import nsv
from test_utils import SAMPLES_DIR

class TestIncrementalProcessing(unittest.TestCase):
    def test_incremental_reading(self):
        """Test reading elements incrementally."""
        file_path = os.path.join(SAMPLES_DIR, 'basic.nsv')
        with open(file_path, 'r') as f:
            reader = nsv.Reader(f)

            first = next(reader)
            self.assertEqual(first, ["a", "b", "c"])

            second = next(reader)
            self.assertEqual(second, ["d", "e", "f"])

            # third = next(reader)
            # self.assertEqual(third, ["last1", "last2"])

            # Should be at end of the file
            with self.assertRaises(StopIteration):
                next(reader)

    def test_incremental_writing(self):
        """Test writing elements incrementally."""
        data = [["field1", "field2"], ["value1", "value2"], ["last1", "last2"]]
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, 'output_incremental.nsv')

            with open(output_path, 'w') as f:
                writer = nsv.Writer(f)
                for elem in data:
                    writer.write_row(elem)

            with open(output_path, 'r') as f:
                actual = nsv.load(f)

            self.assertEqual(data, actual)


if __name__ == '__main__':
    unittest.main()