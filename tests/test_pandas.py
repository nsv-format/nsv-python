import unittest
from io import StringIO

import pandas as pd
import numpy as np

import nsv


def setUpModule():
    nsv.patch_pandas()


class TestReadNsvTypeInference(unittest.TestCase):
    """read_nsv should infer types the same way read_csv does."""

    def _compare_with_csv(self, rows):
        """Assert that read_nsv produces the same dtypes and values as read_csv."""
        nsv_str = nsv.dumps(rows)
        csv_str = '\n'.join(','.join(row) for row in rows) + '\n'

        nsv_df = pd.read_nsv(StringIO(nsv_str))
        csv_df = pd.read_csv(StringIO(csv_str), header=None)

        self.assertEqual(list(nsv_df.dtypes), list(csv_df.dtypes),
                         f"dtype mismatch for rows={rows}")
        pd.testing.assert_frame_equal(nsv_df, csv_df)

    def test_integers(self):
        self._compare_with_csv([['1', '2'], ['3', '4']])

    def test_floats(self):
        self._compare_with_csv([['1.5', '2.5'], ['3.5', '4.5']])

    def test_mixed_int_float(self):
        self._compare_with_csv([['1', '2.5'], ['3', '4.5']])

    def test_strings(self):
        self._compare_with_csv([['hello', 'world'], ['foo', 'bar']])

    def test_mixed_numeric_and_string(self):
        self._compare_with_csv([['123', 'abc'], ['456', 'def']])

    def test_empty_fields_in_numeric_column(self):
        self._compare_with_csv([['1', 'a'], ['', 'b'], ['3', 'c']])

    def test_scientific_notation(self):
        self._compare_with_csv([['1.23e5', '4.56e-2'], ['7.89e1', '0.12e3']])

    def test_negative_numbers(self):
        self._compare_with_csv([['-1', '-2.5'], ['3', '4.5']])

    def test_all_empty(self):
        self._compare_with_csv([['', ''], ['', '']])


class TestReadNsvDtype(unittest.TestCase):
    """read_nsv should support explicit dtype parameter."""

    def test_dtype_str_suppresses_inference(self):
        data = [['123', '456'], ['789', '012']]
        nsv_str = nsv.dumps(data)
        df = pd.read_nsv(StringIO(nsv_str), dtype=str)
        for col in df.columns:
            self.assertFalse(pd.api.types.is_numeric_dtype(df[col]))
        self.assertEqual(df.iloc[0, 0], '123')

    def test_dtype_per_column(self):
        data = [['123', '4.5'], ['789', '6.7']]
        nsv_str = nsv.dumps(data)
        df = pd.read_nsv(StringIO(nsv_str), dtype={0: float, 1: str})
        self.assertTrue(pd.api.types.is_float_dtype(df[0]))
        self.assertFalse(pd.api.types.is_numeric_dtype(df[1]))


class TestToNsv(unittest.TestCase):
    """to_nsv should handle non-string types gracefully."""

    def test_roundtrip_integers(self):
        df = pd.DataFrame({0: [1, 2, 3], 1: [4, 5, 6]})
        nsv_str = df.to_nsv()
        self.assertIsInstance(nsv_str, str)
        df2 = pd.read_nsv(StringIO(nsv_str))
        pd.testing.assert_frame_equal(df, df2)

    def test_roundtrip_floats(self):
        df = pd.DataFrame({0: [1.5, 2.5], 1: [3.5, 4.5]})
        nsv_str = df.to_nsv()
        df2 = pd.read_nsv(StringIO(nsv_str))
        pd.testing.assert_frame_equal(df, df2)

    def test_roundtrip_mixed(self):
        df = pd.DataFrame({0: [1, 2], 1: ['x', 'y']})
        nsv_str = df.to_nsv()
        df2 = pd.read_nsv(StringIO(nsv_str))
        pd.testing.assert_frame_equal(df, df2)

    def test_nan_becomes_empty(self):
        df = pd.DataFrame({'a': [1.0, float('nan'), 3.0]})
        nsv_str = df.to_nsv()
        rows = nsv.loads(nsv_str)
        self.assertEqual(rows[1], [''])


if __name__ == '__main__':
    unittest.main()
