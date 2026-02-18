"""Tests for the bytes-level API: loads_bytes and dumps_bytes."""

import unittest

import nsv
from nsv.core import dumps_bytes  # not part of the public nsv package API
from nsv._python_impl import loads_bytes as py_loads_bytes, dumps_bytes as py_dumps_bytes
from test_utils import SAMPLES_DATA


def _str_to_bytes(data):
    """Convert List[List[str]] to List[List[bytes]] via UTF-8."""
    return [[cell.encode() for cell in row] for row in data]


def _bytes_to_str(data):
    """Convert List[List[bytes]] to List[List[str]] via UTF-8."""
    return [[cell.decode() for cell in row] for row in data]


class TestLoadsBytesBasic(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(nsv.loads_bytes(b''), [])

    def test_single_row(self):
        result = nsv.loads_bytes(b'a\nb\n\n')
        self.assertEqual(result, [[b'a', b'b']])

    def test_two_rows(self):
        result = nsv.loads_bytes(b'a\nb\n\nc\nd\n\n')
        self.assertEqual(result, [[b'a', b'b'], [b'c', b'd']])

    def test_empty_row(self):
        result = nsv.loads_bytes(b'a\n\n\nb\n\n')
        self.assertEqual(result, [[b'a'], [], [b'b']])

    def test_empty_cell(self):
        # b'\\' is the empty cell token
        result = nsv.loads_bytes(b'\\\n')
        self.assertEqual(result, [[b'']])

    def test_newline_in_cell(self):
        result = nsv.loads_bytes(b'line1\\nline2\n\n')
        self.assertEqual(result, [[b'line1\nline2']])

    def test_backslash_in_cell(self):
        result = nsv.loads_bytes(b'\\\\\n\n')
        self.assertEqual(result, [[b'\\']])

    def test_no_trailing_newline(self):
        # Exhaustive: incomplete row at EOF is included
        result = nsv.loads_bytes(b'a\nb')
        self.assertEqual(result, [[b'a', b'b']])

    def test_non_ascii_bytes(self):
        # Latin-1 bytes — not valid UTF-8, but should round-trip fine
        cell = bytes([0xC0, 0xE9, 0xF1])
        encoded = dumps_bytes([[cell]])
        result = nsv.loads_bytes(encoded)
        self.assertEqual(result, [[cell]])


class TestDumpsBytesBasic(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(dumps_bytes([]), b'')

    def test_single_row(self):
        result = dumps_bytes([[b'a', b'b']])
        self.assertEqual(result, b'a\nb\n\n')

    def test_empty_cell(self):
        result = dumps_bytes([[b'']])
        self.assertEqual(result, b'\\\n\n')

    def test_newline_in_cell(self):
        result = dumps_bytes([[b'line1\nline2']])
        self.assertEqual(result, b'line1\\nline2\n\n')

    def test_backslash_in_cell(self):
        result = dumps_bytes([[b'\\']])
        self.assertEqual(result, b'\\\\\n\n')


class TestRoundtrip(unittest.TestCase):
    def test_roundtrip_simple(self):
        original = [[b'hello', b'world'], [b'foo', b'bar']]
        self.assertEqual(nsv.loads_bytes(dumps_bytes(original)), original)

    def test_roundtrip_empty_rows(self):
        original = [[], [b'a'], [], [b'b', b'c'], []]
        self.assertEqual(nsv.loads_bytes(dumps_bytes(original)), original)

    def test_roundtrip_special_chars(self):
        original = [
            [b'newline\nhere', b'back\\slash'],
            [b'', b'normal'],
        ]
        self.assertEqual(nsv.loads_bytes(dumps_bytes(original)), original)

    def test_roundtrip_non_ascii(self):
        original = [[bytes(range(1, 128))]]  # all non-null, non-LF ASCII bytes
        self.assertEqual(nsv.loads_bytes(dumps_bytes(original)), original)

    def test_roundtrip_arbitrary_bytes(self):
        # All byte values except LF (0x0A) and backslash (0x5C) need no escaping
        cell = bytes([b for b in range(256) if b != 0x0A and b != 0x5C])
        original = [[cell]]
        self.assertEqual(nsv.loads_bytes(dumps_bytes(original)), original)


class TestParityWithStrApi(unittest.TestCase):
    """loads_bytes on UTF-8 bytes must produce the same structure as loads on str."""

    def test_parity_all_samples(self):
        for name, expected_str in SAMPLES_DATA.items():
            with self.subTest(sample=name):
                nsv_bytes = dumps_bytes(_str_to_bytes(expected_str))
                result_bytes = nsv.loads_bytes(nsv_bytes)
                result_str = _bytes_to_str(result_bytes)
                self.assertEqual(result_str, expected_str)

    def test_parity_loads_vs_loads_bytes(self):
        """loads(s) and loads_bytes(s.encode()) must yield the same data."""
        for name, expected in SAMPLES_DATA.items():
            with self.subTest(sample=name):
                s = nsv.dumps(expected)
                from_str = nsv.loads(s)
                from_bytes = _bytes_to_str(nsv.loads_bytes(s.encode()))
                self.assertEqual(from_str, from_bytes)

    def test_parity_dumps_vs_dumps_bytes(self):
        """dumps(data) and dumps_bytes(bytes_data).decode() must be equal."""
        for name, expected in SAMPLES_DATA.items():
            with self.subTest(sample=name):
                bytes_data = _str_to_bytes(expected)
                self.assertEqual(
                    nsv.dumps(expected),
                    dumps_bytes(bytes_data).decode(),
                )


class TestPythonFallbackParity(unittest.TestCase):
    """Python fallback must match the Rust extension output."""

    def test_loads_bytes_parity(self):
        cases = [
            b'',
            b'a\nb\n\n',
            b'\\\n\n',
            b'line1\\nline2\n\n',
            b'\\\\\n\n',
            b'a\n\n\nb\n\n',
            b'a\nb',
        ]
        for data in cases:
            with self.subTest(data=data):
                self.assertEqual(nsv.loads_bytes(data), py_loads_bytes(data))

    def test_dumps_bytes_parity(self):
        cases = [
            [],
            [[b'a', b'b']],
            [[b'']],
            [[b'line1\nline2']],
            [[b'\\']],
            [[], [b'a'], []],
        ]
        for data in cases:
            with self.subTest(data=data):
                self.assertEqual(dumps_bytes(data), py_dumps_bytes(data))


if __name__ == '__main__':
    unittest.main()
