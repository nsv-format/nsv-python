import unittest

import nsv
from nsv.ensv import lift, unlift, split, join


class TestSplit(unittest.TestCase):

    def test_basic(self):
        seqseq = [['columns:', 'a', 'b'], [], ['1', '2'], ['3', '4']]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [['columns:', 'a', 'b']])
        self.assertEqual(offset, 2)
        self.assertEqual(data, [['1', '2'], ['3', '4']])

    def test_multiple_meta_rows(self):
        seqseq = [['columns:', 'x'], ['types:', 'int'], [], ['42']]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [['columns:', 'x'], ['types:', 'int']])
        self.assertEqual(offset, 3)
        self.assertEqual(data, [['42']])

    def test_no_empty_row(self):
        seqseq = [['a', 'b'], ['c', 'd']]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [['a', 'b'], ['c', 'd']])
        self.assertEqual(offset, 2)
        self.assertEqual(data, [])

    def test_empty_row_at_start(self):
        seqseq = [[], ['a', 'b']]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [])
        self.assertEqual(offset, 1)
        self.assertEqual(data, [['a', 'b']])

    def test_only_empty_row(self):
        meta, offset, data = split([[]])
        self.assertEqual(meta, [])
        self.assertEqual(offset, 1)
        self.assertEqual(data, [])

    def test_empty_seqseq(self):
        meta, offset, data = split([])
        self.assertEqual(meta, [])
        self.assertEqual(offset, 0)
        self.assertEqual(data, [])

    def test_splits_at_first_empty_row_only(self):
        seqseq = [['meta'], [], ['data1'], [], ['data2']]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [['meta']])
        self.assertEqual(offset, 2)
        self.assertEqual(data, [['data1'], [], ['data2']])

    def test_no_data_after_separator(self):
        seqseq = [['columns:', 'a'], []]
        meta, offset, data = split(seqseq)
        self.assertEqual(meta, [['columns:', 'a']])
        self.assertEqual(offset, 2)
        self.assertEqual(data, [])

    def test_meta_preserved_as_seqseq(self):
        forms = [['columns:', 'name', 'score'], ['types:', 'str', 'int']]
        seqseq = forms + [[]] + [['Alice', '100']]
        meta, _, _ = split(seqseq)
        self.assertEqual(meta, forms)

    def test_nsv_roundtrip(self):
        original = [['columns:', 'x'], [], ['hello']]
        text = nsv.dumps(original)
        recovered = nsv.loads(text)
        meta, offset, data = split(recovered)
        self.assertEqual(meta, [['columns:', 'x']])
        self.assertEqual(data, [['hello']])


class TestJoin(unittest.TestCase):

    def test_basic(self):
        result = join([['columns:', 'a']], [['1'], ['2']])
        self.assertEqual(result, [['columns:', 'a'], [], ['1'], ['2']])

    def test_empty_meta(self):
        result = join([], [['a']])
        self.assertEqual(result, [[], ['a']])

    def test_empty_data(self):
        result = join([['columns:', 'x']], [])
        self.assertEqual(result, [['columns:', 'x'], []])

    def test_roundtrip(self):
        meta = [['columns:', 'a', 'b'], ['types:', 'str', 'int']]
        data = [['x', '1'], ['y', '2']]
        m, _, d = split(join(meta, data))
        self.assertEqual(m, meta)
        self.assertEqual(d, data)


if __name__ == '__main__':
    unittest.main()
