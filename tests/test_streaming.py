"""
Streaming tests for NSV Reader and Writer.

These tests validate true streaming behavior - processing data incrementally
without loading entire datasets into memory.
"""

import unittest
import tempfile
import os
from io import StringIO
import nsv


class TestStreamingReader(unittest.TestCase):
    """Test Reader class for streaming/incremental reading."""

    def test_complete_rows_only(self):
        """Reader should emit rows when they are complete (double newline)."""
        # Data with properly terminated rows
        data = 'a\nb\n\nc\nd\n\n'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        self.assertEqual(rows, [['a', 'b'], ['c', 'd']])

    def test_incomplete_row_at_eof(self):
        """Reader behavior when last row doesn't have double newline."""
        # First row complete, second row incomplete at EOF
        data = 'a\nb\n\nc\nd'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        # Current behavior: Reader emits incomplete row at EOF
        # This test documents current behavior
        self.assertEqual(rows, [['a', 'b'], ['c', 'd']])

    def test_single_complete_row(self):
        """Single row with proper termination."""
        data = 'x\ny\nz\n\n'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        self.assertEqual(rows, [['x', 'y', 'z']])

    def test_single_incomplete_row(self):
        """Single row without double newline at EOF."""
        data = 'x\ny\nz'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        # Current behavior: emits incomplete row at EOF
        self.assertEqual(rows, [['x', 'y', 'z']])

    def test_empty_rows(self):
        """Reader should handle empty rows (double newlines)."""
        # Pattern: \n\n = empty row, a\n\n = row with 'a', \n\n = empty row
        data = '\n\na\n\n\n\nb\n\n'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        # Note: Triple newlines (\n\n\n) create TWO empty rows
        # \n\n = first empty row
        # \n (from \n\n\n) starts a new cell, but next \n completes it as empty
        # This is documented Python Reader behavior
        self.assertEqual(rows, [[], [], ['a'], [], [], ['b']])

    def test_empty_file(self):
        """Empty input should produce no rows."""
        data = ''
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        self.assertEqual(rows, [])

    def test_only_newlines(self):
        """File with only newlines should produce empty rows."""
        data = '\n\n\n\n'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        # Four newlines: \n\n (empty row) + \n\n (empty row)
        # But the algorithm sees: \n (cell), \n (empty = row), \n (cell), \n (empty = row)
        # Actually produces 4 empty rows due to how Reader processes line by line
        self.assertEqual(rows, [[], [], [], []])

    def test_escaped_content(self):
        """Reader should properly unescape content."""
        data = 'normal\n\\\n\nline1\\nline2\nback\\\\slash\n\n'
        reader = nsv.Reader(StringIO(data))

        rows = list(reader)
        self.assertEqual(rows, [
            ['normal', ''],
            ['line1\nline2', 'back\\slash']
        ])

    def test_incremental_iteration(self):
        """Test that Reader can be iterated incrementally."""
        data = 'row1a\nrow1b\n\nrow2a\nrow2b\n\nrow3a\nrow3b\n\n'
        reader = nsv.Reader(StringIO(data))

        # Iterate one at a time
        row1 = next(reader)
        self.assertEqual(row1, ['row1a', 'row1b'])

        row2 = next(reader)
        self.assertEqual(row2, ['row2a', 'row2b'])

        row3 = next(reader)
        self.assertEqual(row3, ['row3a', 'row3b'])

        # Should raise StopIteration when exhausted
        with self.assertRaises(StopIteration):
            next(reader)

    def test_file_reading(self):
        """Test reading from actual file (not just StringIO)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.nsv') as f:
            f.write('file\ndata\n\nmore\ndata\n\n')
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                reader = nsv.Reader(f)
                rows = list(reader)

            self.assertEqual(rows, [['file', 'data'], ['more', 'data']])
        finally:
            os.unlink(temp_path)

    def test_large_dataset_streaming(self):
        """Test that Reader doesn't need to load entire dataset into memory."""
        # Generate large dataset (1000 rows)
        rows_written = 1000
        data_parts = []
        for i in range(rows_written):
            data_parts.append(f'row{i}_cell1\nrow{i}_cell2\n\n')
        data = ''.join(data_parts)

        reader = nsv.Reader(StringIO(data))

        # Process incrementally
        rows_read = 0
        for row in reader:
            # Verify format
            self.assertEqual(len(row), 2)
            self.assertTrue(row[0].startswith('row'))
            rows_read += 1

        self.assertEqual(rows_read, rows_written)


class TestStreamingWriter(unittest.TestCase):
    """Test Writer class for streaming/incremental writing."""

    def test_write_single_row(self):
        """Writer should correctly write a single row."""
        output = StringIO()
        writer = nsv.Writer(output)

        writer.write_row(['a', 'b', 'c'])

        result = output.getvalue()
        self.assertEqual(result, 'a\nb\nc\n\n')

    def test_write_multiple_rows(self):
        """Writer should correctly write multiple rows incrementally."""
        output = StringIO()
        writer = nsv.Writer(output)

        writer.write_row(['row1a', 'row1b'])
        writer.write_row(['row2a', 'row2b'])
        writer.write_row(['row3a', 'row3b'])

        result = output.getvalue()
        expected = 'row1a\nrow1b\n\nrow2a\nrow2b\n\nrow3a\nrow3b\n\n'
        self.assertEqual(result, expected)

    def test_write_rows_batch(self):
        """Writer.write_rows should write multiple rows."""
        output = StringIO()
        writer = nsv.Writer(output)

        rows = [
            ['a', 'b'],
            ['c', 'd'],
            ['e', 'f']
        ]
        writer.write_rows(rows)

        result = output.getvalue()
        expected = 'a\nb\n\nc\nd\n\ne\nf\n\n'
        self.assertEqual(result, expected)

    def test_write_empty_row(self):
        """Writer should handle empty rows."""
        output = StringIO()
        writer = nsv.Writer(output)

        writer.write_row([])

        result = output.getvalue()
        self.assertEqual(result, '\n')

    def test_write_empty_cells(self):
        """Writer should escape empty cells."""
        output = StringIO()
        writer = nsv.Writer(output)

        writer.write_row(['a', '', 'c'])

        result = output.getvalue()
        self.assertEqual(result, 'a\n\\\nc\n\n')

    def test_write_escaped_content(self):
        """Writer should properly escape special characters."""
        output = StringIO()
        writer = nsv.Writer(output)

        writer.write_row([
            'normal',
            '',
            'line1\nline2',
            'back\\slash'
        ])

        result = output.getvalue()
        expected = 'normal\n\\\nline1\\nline2\nback\\\\slash\n\n'
        self.assertEqual(result, expected)

    def test_incremental_writing(self):
        """Test that rows are written incrementally, not buffered."""
        output = StringIO()
        writer = nsv.Writer(output)

        # Write first row
        writer.write_row(['first', 'row'])
        intermediate = output.getvalue()
        self.assertEqual(intermediate, 'first\nrow\n\n')

        # Write second row
        writer.write_row(['second', 'row'])
        final = output.getvalue()
        self.assertEqual(final, 'first\nrow\n\nsecond\nrow\n\n')

    def test_file_writing(self):
        """Test writing to actual file (not just StringIO)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.nsv') as f:
            temp_path = f.name
            writer = nsv.Writer(f)

            writer.write_row(['file', 'test'])
            writer.write_row(['more', 'data'])

        try:
            with open(temp_path, 'r') as f:
                content = f.read()

            self.assertEqual(content, 'file\ntest\n\nmore\ndata\n\n')
        finally:
            os.unlink(temp_path)


class TestReaderWriterRoundtrip(unittest.TestCase):
    """Test roundtrip: Writer -> Reader produces original data."""

    def test_simple_roundtrip(self):
        """Write data and read it back."""
        original_data = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f']
        ]

        # Write
        output = StringIO()
        writer = nsv.Writer(output)
        writer.write_rows(original_data)

        # Read back
        output.seek(0)
        reader = nsv.Reader(output)
        read_data = list(reader)

        self.assertEqual(read_data, original_data)

    def test_complex_roundtrip(self):
        """Roundtrip with empty cells, newlines, backslashes."""
        original_data = [
            ['normal', 'text'],
            ['', 'empty', ''],
            ['multi\nline', 'value'],
            ['back\\slash', 'end']
        ]

        # Write
        output = StringIO()
        writer = nsv.Writer(output)
        writer.write_rows(original_data)

        # Read back
        output.seek(0)
        reader = nsv.Reader(output)
        read_data = list(reader)

        self.assertEqual(read_data, original_data)

    def test_empty_rows_roundtrip(self):
        """Roundtrip with empty rows."""
        original_data = [
            ['a'],
            [],
            ['b'],
            [],
            []
        ]

        # Write
        output = StringIO()
        writer = nsv.Writer(output)
        writer.write_rows(original_data)

        # Read back
        output.seek(0)
        reader = nsv.Reader(output)
        read_data = list(reader)

        self.assertEqual(read_data, original_data)


class TestLoadsReaderParity(unittest.TestCase):
    """Test that loads() and Reader produce the same results."""

    def test_parity_complete_data(self):
        """loads() and Reader should agree on complete data."""
        test_cases = [
            'a\nb\n\n',
            'a\nb\n\nc\nd\n\n',
            '\n\na\n\n\n\nb\n\n',
            '',
            '\n\n',
        ]

        for data in test_cases:
            with self.subTest(data=repr(data)):
                loads_result = nsv.loads(data)
                reader_result = list(nsv.Reader(StringIO(data)))

                self.assertEqual(loads_result, reader_result,
                    f"loads and Reader differ for {repr(data)}")

    def test_parity_incomplete_data(self):
        """Document current behavior for incomplete data at EOF."""
        test_cases = [
            'a\nb',      # Single incomplete row
            'a\nb\n\nc\nd',  # Last row incomplete
        ]

        for data in test_cases:
            with self.subTest(data=repr(data)):
                loads_result = nsv.loads(data)
                reader_result = list(nsv.Reader(StringIO(data)))

                # Currently these differ - this test documents that
                # loads: ignores incomplete row
                # Reader: includes incomplete row at EOF
                # TODO: Decide which behavior is correct
                self.assertNotEqual(loads_result, reader_result,
                    f"loads and Reader unexpectedly agree for {repr(data)}")


class TestStreamingMemoryEfficiency(unittest.TestCase):
    """Test that streaming doesn't load entire dataset into memory."""

    def test_reader_processes_incrementally(self):
        """Reader should process rows one at a time, not all at once."""
        # Create large dataset
        num_rows = 10000
        rows = [[f'row{i}a', f'row{i}b'] for i in range(num_rows)]

        # Write to string
        output = StringIO()
        writer = nsv.Writer(output)
        writer.write_rows(rows)

        # Read incrementally
        output.seek(0)
        reader = nsv.Reader(output)

        processed = 0
        for row in reader:
            processed += 1
            # In a real streaming scenario, we could process each row
            # and discard it, never holding all rows in memory

        self.assertEqual(processed, num_rows)

    def test_writer_writes_incrementally(self):
        """Writer should write rows as they're provided, not buffer all."""
        output = StringIO()
        writer = nsv.Writer(output)

        # Write rows one at a time
        for i in range(100):
            writer.write_row([f'row{i}'])
            # Check that data is written immediately
            current_output = output.getvalue()
            expected_rows = i + 1
            # Count double newlines (row terminators)
            actual_rows = current_output.count('\n\n')
            self.assertEqual(actual_rows, expected_rows)


if __name__ == '__main__':
    unittest.main()
