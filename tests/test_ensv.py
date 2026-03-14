import unittest

from nsv.ensv import lift, unlift, peel


class TestPeel(unittest.TestCase):

    def test_peel_from_list(self):
        meta_row = lift([['types:', 'int']])
        meta, tail = peel([meta_row, ['42']])
        self.assertEqual(meta, [['types:', 'int']])
        self.assertEqual(list(tail), [['42']])

    def test_peel_from_generator(self):
        consumed = []
        def gen():
            consumed.append('meta')
            yield lift([['types:', 'int']])
            consumed.append('row1')
            yield ['42']
            consumed.append('row2')
            yield ['99']

        meta, tail = peel(gen())
        self.assertEqual(consumed, ['meta'])
        self.assertEqual(meta, [['types:', 'int']])
        row1 = next(tail)
        self.assertEqual(consumed, ['meta', 'row1'])
        self.assertEqual(row1, ['42'])

    def test_peel_empty_raises(self):
        with self.assertRaises(ValueError):
            peel([])

    def test_peel_metadata_only(self):
        meta, tail = peel([lift([['columns:', 'a']])])
        self.assertEqual(meta, [['columns:', 'a']])
        self.assertEqual(list(tail), [])

    def test_peel_multiple_forms(self):
        meta_row = lift([
            ['columns:', 'name', 'active'],
            ['types:', 'str', 'bool'],
            ['bool', 'yes', 'no'],
        ])
        meta, tail = peel([meta_row, ['Alice', 'yes']])
        self.assertEqual(meta, [
            ['columns:', 'name', 'active'],
            ['types:', 'str', 'bool'],
            ['bool', 'yes', 'no'],
        ])
        self.assertEqual(list(tail), [['Alice', 'yes']])

    def test_peel_empty_metadata(self):
        meta, tail = peel([[], ['data']])
        self.assertEqual(meta, [[]])
        self.assertEqual(list(tail), [['data']])

    def test_peel_roundtrip_through_lift(self):
        forms = [['columns:', '', 'b'], ['custom', 'x\ny', 'a\\b']]
        meta_row = lift(forms)
        meta, _ = peel([meta_row])
        self.assertEqual(meta, forms)


if __name__ == '__main__':
    unittest.main()
