import io
import unittest

from nsv.ensv import Reader, Writer


class TestReader(unittest.TestCase):

    def _make(self, text):
        return Reader(io.StringIO(text))

    def test_meta_and_data(self):
        # meta: [columns: a b] [types: str int], separator, data: [Alice 100] [Bob 200]
        r = self._make('columns:\na\nb\n\ntypes:\nstr\nint\n\n\nAlice\n100\n\nBob\n200\n\n')
        self.assertEqual(r.meta, [['columns:', 'a', 'b'], ['types:', 'str', 'int']])
        self.assertEqual(list(r), [['Alice', '100'], ['Bob', '200']])

    def test_single_meta_row(self):
        r = self._make('columns:\nx\n\n\nhello\n\n')
        self.assertEqual(r.meta, [['columns:', 'x']])
        self.assertEqual(list(r), [['hello']])

    def test_no_data(self):
        r = self._make('columns:\na\n\n\n')
        self.assertEqual(r.meta, [['columns:', 'a']])
        self.assertEqual(list(r), [])

    def test_empty_meta(self):
        # empty row right away = no meta forms
        r = self._make('\nhello\n\n')
        self.assertEqual(r.meta, [])
        self.assertEqual(list(r), [['hello']])

    def test_meta_preserved_for_later(self):
        r = self._make('columns:\nname\n\ntypes:\nstr\n\n\nAlice\n\n')
        meta = r.meta
        _ = list(r)
        self.assertEqual(meta, [['columns:', 'name'], ['types:', 'str']])
        self.assertIs(r.meta, meta)

    def test_streaming(self):
        r = self._make('columns:\nx\n\n\n1\n\n2\n\n3\n\n')
        self.assertEqual(r.meta, [['columns:', 'x']])
        self.assertEqual(next(r), ['1'])
        self.assertEqual(next(r), ['2'])
        self.assertEqual(next(r), ['3'])

    def test_no_separator_all_meta(self):
        # no empty row separator = everything is meta
        r = self._make('a\nb\n\nc\nd\n\n')
        self.assertEqual(r.meta, [['a', 'b'], ['c', 'd']])
        self.assertEqual(list(r), [])


class TestWriter(unittest.TestCase):

    def _write(self, meta, data):
        buf = io.StringIO()
        w = Writer(buf)
        w.write_meta(meta)
        w.write_rows(data)
        return buf.getvalue()

    def test_meta_and_data(self):
        text = self._write(
            [['columns:', 'a', 'b']],
            [['1', '2'], ['3', '4']],
        )
        r = Reader(io.StringIO(text))
        self.assertEqual(r.meta, [['columns:', 'a', 'b']])
        self.assertEqual(list(r), [['1', '2'], ['3', '4']])

    def test_multiple_meta_rows(self):
        text = self._write(
            [['columns:', 'x'], ['types:', 'int']],
            [['42']],
        )
        r = Reader(io.StringIO(text))
        self.assertEqual(r.meta, [['columns:', 'x'], ['types:', 'int']])
        self.assertEqual(list(r), [['42']])

    def test_empty_data(self):
        text = self._write([['columns:', 'a']], [])
        r = Reader(io.StringIO(text))
        self.assertEqual(r.meta, [['columns:', 'a']])
        self.assertEqual(list(r), [])

    def test_write_row_by_row(self):
        buf = io.StringIO()
        w = Writer(buf)
        w.write_meta([['columns:', 'x']])
        w.write_row(['a'])
        w.write_row(['b'])
        r = Reader(io.StringIO(buf.getvalue()))
        self.assertEqual(r.meta, [['columns:', 'x']])
        self.assertEqual(list(r), [['a'], ['b']])


class TestRoundTrip(unittest.TestCase):

    def test_roundtrip(self):
        meta = [['columns:', 'name', 'score'], ['types:', 'str', 'int']]
        data = [['Alice', '100'], ['Bob', '200']]
        buf = io.StringIO()
        w = Writer(buf)
        w.write_meta(meta)
        w.write_rows(data)
        r = Reader(io.StringIO(buf.getvalue()))
        self.assertEqual(r.meta, meta)
        self.assertEqual(list(r), data)


if __name__ == '__main__':
    unittest.main()
