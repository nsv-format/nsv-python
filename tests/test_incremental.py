import unittest
import io
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

            # Should be at end of the file
            with self.assertRaises(StopIteration):
                next(reader)

    def test_incomplete_trailing_row_buffered(self):
        """A resumable Reader buffers an incomplete trailing row instead of emitting it."""
        reader = nsv.Reader(io.StringIO('a\nb\n\nc\nd'))
        self.assertEqual(next(reader), ['a', 'b'])
        with self.assertRaises(StopIteration):
            next(reader)

        reader = nsv.Reader(io.StringIO('a\nb\n\nc\nd\n'))
        self.assertEqual(next(reader), ['a', 'b'])
        with self.assertRaises(StopIteration):
            next(reader)

    def test_reading_resumes_after_eof(self):
        """Reading continues across EOF once more data is appended (tailing)."""
        with tempfile.TemporaryDirectory() as output_dir:
            file_path = os.path.join(output_dir, 'tail.nsv')
            with open(file_path, 'w') as f:
                f.write('a\nb')
                f.flush()

                with open(file_path, 'r') as rf:
                    reader = nsv.Reader(rf)
                    with self.assertRaises(StopIteration):
                        next(reader)

                    f.write('c\nd\n\n')
                    f.flush()
                    self.assertEqual(next(reader), ['a', 'bc', 'd'])

    def test_load_emits_incomplete_trailing_row(self):
        """Non-resumable loads keeps emitting the incomplete tail."""
        self.assertEqual(nsv.loads('a\nb\n\nc\nd'), [['a', 'b'], ['c', 'd']])

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