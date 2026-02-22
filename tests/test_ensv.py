import datetime
import unittest
import uuid
import warnings

import nsv
from nsv.ensv import (
    Metadata, UnknownForm, ENSVReader, _TABLE_INFER, _ReadResult,
    peel, read, encode, lift,
)


def _read(meta, data):
    return list(ENSVReader(meta).read(data))


# ===================================================================
# Metadata parsing
# ===================================================================

class TestColumnsForm(unittest.TestCase):

    def test_columns_basic(self):
        m = Metadata.from_row(lift([['columns:', 'name', 'age', 'city']]))
        self.assertEqual(m.columns, ['name', 'age', 'city'])

    def test_columns_single(self):
        m = Metadata.from_row(lift([['columns:', 'x']]))
        self.assertEqual(m.columns, ['x'])

    def test_columns_with_spaces(self):
        m = Metadata.from_row(lift([['columns:', 'col 1', 'col 2', 'col 3']]))
        self.assertEqual(m.columns, ['col 1', 'col 2', 'col 3'])

    def test_columns_no_args(self):
        m = Metadata.from_row(lift([['columns:']]))
        self.assertEqual(m.columns, [])

    def test_columns_with_empty_names(self):
        m = Metadata.from_row(lift([['columns:', '', '', '']]))
        self.assertEqual(m.columns, ['', '', ''])


class TestTypesForm(unittest.TestCase):

    def test_types_basic(self):
        m = Metadata.from_row(lift([['types:', 'str', 'int', 'float']]))
        self.assertEqual(m.types, ['str', 'int', 'float'])

    def test_types_all_known(self):
        m = Metadata.from_row(lift([
            ['types:', 'str', 'int', 'float', 'date', 'datetime', 'uuid'],
        ]))
        self.assertEqual(
            m.types,
            ['str', 'int', 'float', 'date', 'datetime', 'uuid'])

    def test_types_single(self):
        m = Metadata.from_row(lift([['types:', 'int']]))
        self.assertEqual(m.types, ['int'])


class TestBoolForm(unittest.TestCase):

    def test_bool_basic(self):
        m = Metadata.from_row(lift([['bool', 'yes', 'no']]))
        self.assertEqual(m.bool, ('yes', 'no'))

    def test_bool_true_false(self):
        m = Metadata.from_row(lift([['bool', 'true', 'false']]))
        self.assertEqual(m.bool, ('true', 'false'))

    def test_bool_wrong_arity(self):
        with self.assertRaises(ValueError):
            Metadata.from_row(lift([['bool', 'yes']]))
        with self.assertRaises(ValueError):
            Metadata.from_row(lift([['bool', 'a', 'b', 'c']]))
        with self.assertRaises(ValueError):
            Metadata.from_row(lift([['bool']]))


class TestTableForm(unittest.TestCase):

    def test_table_explicit_width(self):
        m = Metadata.from_row(lift([['table', '5']]))
        self.assertEqual(m.table, 5)

    def test_table_infer(self):
        m = Metadata.from_row(lift([['table']]))
        self.assertIs(m.table, _TABLE_INFER)

    def test_table_zero_width(self):
        m = Metadata.from_row(lift([['table', '0']]))
        self.assertEqual(m.table, 0)

    def test_table_too_many_args(self):
        with self.assertRaises(ValueError):
            Metadata.from_row(lift([['table', '3', '4']]))

    def test_no_table_form(self):
        m = Metadata.from_row(lift([['columns:', 'a', 'b']]))
        self.assertIsNone(m.table)


class TestUnknownForms(unittest.TestCase):

    def test_unknown_stashed(self):
        m = Metadata.from_row(lift([['custom', 'arg1', 'arg2']]))
        self.assertEqual(len(m.unknown), 1)
        self.assertEqual(m.unknown[0], UnknownForm('custom', ['arg1', 'arg2']))

    def test_multiple_unknown(self):
        m = Metadata.from_row(lift([['foo', 'a'], ['bar', 'b', 'c']]))
        self.assertEqual(len(m.unknown), 2)
        self.assertEqual(m.unknown[0].name, 'foo')
        self.assertEqual(m.unknown[1].name, 'bar')

    def test_namespaced_form_raises(self):
        with self.assertRaises(ValueError) as cm:
            Metadata.from_row(lift([['foo/bar', 'x']]))
        self.assertIn('reserved', str(cm.exception))

    def test_namespaced_deep_raises(self):
        with self.assertRaises(ValueError):
            Metadata.from_row(lift([['a/b/c']]))


class TestAllFormsTogether(unittest.TestCase):

    def test_all_forms(self):
        m = Metadata.from_row(lift([
            ['columns:', 'name', 'active', 'score'],
            ['types:', 'str', 'bool', 'int'],
            ['bool', 'Y', 'N'],
            ['table', '3'],
        ]))
        self.assertEqual(m.columns, ['name', 'active', 'score'])
        self.assertEqual(m.types, ['str', 'bool', 'int'])
        self.assertEqual(m.bool, ('Y', 'N'))
        self.assertEqual(m.table, 3)

    def test_all_forms_with_unknown(self):
        m = Metadata.from_row(lift([
            ['columns:', 'a'], ['types:', 'str'], ['bool', 't', 'f'],
            ['table', '1'], ['version', '2'],
        ]))
        self.assertEqual(len(m.unknown), 1)
        self.assertEqual(m.unknown[0].name, 'version')

    def test_partial_columns(self):
        m = Metadata(columns=['a', 'b'])
        self.assertEqual(_read(m, [['x', 'y', 'z']]), [['x', 'y', 'z']])

    def test_partial_types(self):
        m = Metadata(types=['int'])
        self.assertEqual(_read(m, [['42', 'hello']]), [[42, 'hello']])


# ===================================================================
# Arity agreement
# ===================================================================

class TestArityAgreement(unittest.TestCase):

    def test_columns_types_mismatch(self):
        with self.assertRaises(ValueError) as cm:
            Metadata(columns=['a', 'b'], types=['str'])
        self.assertIn('columns:', str(cm.exception))
        self.assertIn('types:', str(cm.exception))

    def test_columns_table_mismatch(self):
        with self.assertRaises(ValueError) as cm:
            Metadata(columns=['a', 'b'], table=3)
        self.assertIn('columns:', str(cm.exception))
        self.assertIn('table', str(cm.exception))

    def test_types_table_mismatch(self):
        with self.assertRaises(ValueError) as cm:
            Metadata(types=['str', 'int'], table=3)
        self.assertIn('types:', str(cm.exception))
        self.assertIn('table', str(cm.exception))

    def test_all_three_agree(self):
        m = Metadata(columns=['a', 'b'], types=['str', 'int'], table=2)
        self.assertEqual(m.columns, ['a', 'b'])

    def test_columns_table_infer_no_error(self):
        m = Metadata(columns=['a', 'b'], table=_TABLE_INFER)
        self.assertEqual(m.columns, ['a', 'b'])


# ===================================================================
# Type conversion (via ENSVReader)
# ===================================================================

class TestTypeConversionInt(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(_read(Metadata(types=['int']), [['42']]), [[42]])

    def test_negative(self):
        self.assertEqual(_read(Metadata(types=['int']), [['-7']]), [[-7]])

    def test_zero(self):
        self.assertEqual(_read(Metadata(types=['int']), [['0']]), [[0]])

    def test_invalid(self):
        with self.assertRaises(ValueError) as cm:
            _read(Metadata(types=['int']), [['abc']])
        self.assertIn('row 0', str(cm.exception))
        self.assertIn('col 0', str(cm.exception))


class TestTypeConversionFloat(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(_read(Metadata(types=['float']), [['3.14']]), [[3.14]])

    def test_negative(self):
        self.assertEqual(_read(Metadata(types=['float']), [['-2.5']]), [[-2.5]])

    def test_zero(self):
        self.assertEqual(_read(Metadata(types=['float']), [['0.0']]), [[0.0]])

    def test_scientific(self):
        self.assertEqual(_read(Metadata(types=['float']), [['1.5e10']]), [[1.5e10]])

    def test_negative_scientific(self):
        result = _read(Metadata(types=['float']), [['-3.2e-4']])
        self.assertAlmostEqual(result[0][0], -3.2e-4)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _read(Metadata(types=['float']), [['not_a_float']])


class TestTypeConversionBool(unittest.TestCase):

    def test_true_sentinel(self):
        m = Metadata(types=['bool'], bool_sentinels=('yes', 'no'))
        self.assertEqual(_read(m, [['yes']]), [[True]])

    def test_false_sentinel(self):
        m = Metadata(types=['bool'], bool_sentinels=('yes', 'no'))
        self.assertEqual(_read(m, [['no']]), [[False]])

    def test_non_matching(self):
        m = Metadata(types=['bool'], bool_sentinels=('yes', 'no'))
        with self.assertRaises(ValueError) as cm:
            _read(m, [['maybe']])
        self.assertIn('matches neither', str(cm.exception))

    def test_case_sensitive(self):
        m = Metadata(types=['bool'], bool_sentinels=('Yes', 'No'))
        with self.assertRaises(ValueError):
            _read(m, [['yes']])

    def test_exact_match(self):
        m = Metadata(types=['bool'], bool_sentinels=('Yes', 'No'))
        with self.assertRaises(ValueError):
            _read(m, [['Yes ']])


class TestTypeConversionDate(unittest.TestCase):

    def test_valid(self):
        m = Metadata(types=['date'])
        self.assertEqual(_read(m, [['2024-03-15']]), [[datetime.date(2024, 3, 15)]])

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _read(Metadata(types=['date']), [['not-a-date']])

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            _read(Metadata(types=['date']), [['03/15/2024']])


class TestTypeConversionDatetime(unittest.TestCase):

    def test_without_timezone(self):
        m = Metadata(types=['datetime'])
        self.assertEqual(
            _read(m, [['2024-03-15T10:30:00']]),
            [[datetime.datetime(2024, 3, 15, 10, 30, 0)]])

    def test_with_timezone(self):
        m = Metadata(types=['datetime'])
        result = _read(m, [['2024-03-15T10:30:00+05:00']])
        expected = datetime.datetime(
            2024, 3, 15, 10, 30, 0,
            tzinfo=datetime.timezone(datetime.timedelta(hours=5)))
        self.assertEqual(result[0][0], expected)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _read(Metadata(types=['datetime']), [['not-a-datetime']])


class TestTypeConversionUUID(unittest.TestCase):

    def test_valid(self):
        m = Metadata(types=['uuid'])
        self.assertEqual(
            _read(m, [['12345678-1234-5678-1234-567812345678']]),
            [[uuid.UUID('12345678-1234-5678-1234-567812345678')]])

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _read(Metadata(types=['uuid']), [['not-a-uuid']])


class TestTypeConversionStr(unittest.TestCase):

    def test_identity(self):
        self.assertEqual(_read(Metadata(types=['str']), [['hello']]), [['hello']])

    def test_empty_string(self):
        self.assertEqual(_read(Metadata(types=['str']), [['']]), [['']])


class TestTypeConversionUnknown(unittest.TestCase):

    def test_unknown_type_treated_as_str(self):
        m = Metadata(types=['widget'])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _read(m, [['hello']])
            self.assertEqual(result, [['hello']])
            self.assertEqual(len(w), 1)
            self.assertIn('unknown type', str(w[0].message))
            self.assertIn('widget', str(w[0].message))


# ===================================================================
# Table validation (via ENSVReader)
# ===================================================================

class TestTableValidation(unittest.TestCase):

    def test_explicit_width_correct(self):
        m = Metadata(table=3)
        self.assertEqual(
            _read(m, [['a', 'b', 'c'], ['d', 'e', 'f']]),
            [['a', 'b', 'c'], ['d', 'e', 'f']])

    def test_explicit_width_incorrect(self):
        with self.assertRaises(ValueError) as cm:
            _read(Metadata(table=3), [['a', 'b']])
        self.assertIn('row 0', str(cm.exception))

    def test_explicit_width_second_row_wrong(self):
        with self.assertRaises(ValueError):
            _read(Metadata(table=2), [['a', 'b'], ['c']])

    def test_infer_from_first_row(self):
        m = Metadata(table=_TABLE_INFER)
        self.assertEqual(
            _read(m, [['a', 'b'], ['c', 'd']]),
            [['a', 'b'], ['c', 'd']])

    def test_infer_reject_ragged(self):
        with self.assertRaises(ValueError):
            _read(Metadata(table=_TABLE_INFER), [['a', 'b'], ['c']])

    def test_no_table_ragged_ok(self):
        self.assertEqual(
            _read(Metadata(), [['a', 'b'], ['c']]),
            [['a', 'b'], ['c']])

    def test_infer_empty_data(self):
        self.assertEqual(_read(Metadata(table=_TABLE_INFER), []), [])


# ===================================================================
# Bool form interaction
# ===================================================================

class TestBoolInteraction(unittest.TestCase):

    def test_types_bool_without_bool_form_errors(self):
        with self.assertRaises(ValueError) as cm:
            Metadata(types=['bool'])
        self.assertIn('bool', str(cm.exception))

    def test_bool_form_without_bool_type_ok(self):
        m = Metadata(types=['str'], bool_sentinels=('y', 'n'))
        self.assertIsNotNone(m.bool)

    def test_bool_sentinels_exact(self):
        m = Metadata(types=['bool'], bool_sentinels=('1', '0'))
        self.assertEqual(_read(m, [['1']]), [[True]])
        self.assertEqual(_read(m, [['0']]), [[False]])
        with self.assertRaises(ValueError):
            _read(m, [['1 ']])


# ===================================================================
# ENSVReader
# ===================================================================

class TestENSVReader(unittest.TestCase):

    def test_basic(self):
        r = ENSVReader(Metadata(types=['int', 'str']))
        self.assertEqual(
            list(r.read([['1', 'a'], ['2', 'b']])),
            [[1, 'a'], [2, 'b']])

    def test_shared_schema_two_iterables(self):
        r = ENSVReader(Metadata(types=['int']))
        self.assertEqual(list(r.read([['1'], ['2']])), [[1], [2]])
        self.assertEqual(list(r.read([['3'], ['4']])), [[3], [4]])

    def test_replace_meta_between_reads(self):
        r = ENSVReader(Metadata(types=['int']))
        self.assertEqual(list(r.read([['42']])), [[42]])
        r.meta = Metadata(types=['float'])
        self.assertEqual(list(r.read([['3.14']])), [[3.14]])

    def test_meta_property(self):
        m = Metadata(types=['str'])
        r = ENSVReader(m)
        self.assertIs(r.meta, m)

    def test_width_resets_between_reads(self):
        r = ENSVReader(Metadata(table=_TABLE_INFER))
        self.assertEqual(list(r.read([['a', 'b']])), [['a', 'b']])
        self.assertEqual(list(r.read([['x', 'y', 'z']])), [['x', 'y', 'z']])

    def test_no_types_passthrough(self):
        r = ENSVReader(Metadata())
        self.assertEqual(list(r.read([['a', 'b']])), [['a', 'b']])


# ===================================================================
# peel
# ===================================================================

class TestPeel(unittest.TestCase):

    def test_peel_from_list(self):
        meta_row = lift([['types:', 'int']])
        meta, tail = peel([meta_row, ['42']])
        self.assertEqual(meta.types, ['int'])
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
        self.assertEqual(meta.types, ['int'])
        row1 = next(tail)
        self.assertEqual(consumed, ['meta', 'row1'])
        self.assertEqual(row1, ['42'])

    def test_peel_empty_raises(self):
        with self.assertRaises(ValueError):
            peel([])

    def test_peel_metadata_only(self):
        meta, tail = peel([lift([['columns:', 'a']])])
        self.assertEqual(meta.columns, ['a'])
        self.assertEqual(list(tail), [])


# ===================================================================
# ensv.read (one-shot)
# ===================================================================

class TestRead(unittest.TestCase):

    def test_one_shot(self):
        meta_row = lift([['types:', 'int', 'str']])
        result = read([meta_row, ['1', 'a'], ['2', 'b']])
        self.assertEqual(list(result), [[1, 'a'], [2, 'b']])

    def test_meta_accessible(self):
        meta_row = lift([['columns:', 'x', 'y']])
        result = read([meta_row, ['1', '2']])
        self.assertEqual(result.meta.columns, ['x', 'y'])
        self.assertEqual(list(result), [['1', '2']])

    def test_usable_in_for_loop(self):
        meta_row = lift([['types:', 'int']])
        rows = []
        for row in read([meta_row, ['1'], ['2']]):
            rows.append(row)
        self.assertEqual(rows, [[1], [2]])

    def test_is_iterator(self):
        result = read([lift([['columns:', 'a']]), ['x']])
        self.assertIs(iter(result), result)

    def test_empty_data(self):
        result = read([lift([['types:', 'int']])])
        self.assertEqual(list(result), [])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            read([])


# ===================================================================
# Laziness
# ===================================================================

class TestLaziness(unittest.TestCase):

    def test_reader_read_is_lazy(self):
        consumed = []
        def gen():
            for i in range(5):
                consumed.append(i)
                yield [str(i)]

        r = ENSVReader(Metadata(types=['int']))
        it = r.read(gen())
        self.assertEqual(consumed, [])
        self.assertEqual(next(it), [0])
        self.assertEqual(consumed, [0])
        self.assertEqual(next(it), [1])
        self.assertEqual(consumed, [0, 1])

    def test_read_is_lazy(self):
        consumed = []
        def gen():
            consumed.append('meta')
            yield lift([['types:', 'int']])
            for i in range(3):
                consumed.append(i)
                yield [str(i)]

        result = read(gen())
        self.assertEqual(consumed, ['meta'])
        self.assertEqual(next(result), [0])
        self.assertEqual(consumed, ['meta', 0])

    def test_peel_consumes_exactly_one(self):
        consumed = []
        def gen():
            for i in range(3):
                consumed.append(i)
                yield [str(i)]

        meta, tail = peel(gen())
        self.assertEqual(len(consumed), 1)


# ===================================================================
# Round-trip
# ===================================================================

class TestRoundTrip(unittest.TestCase):

    def _roundtrip(self, meta):
        self.assertEqual(Metadata.from_row(meta.to_row()), meta)

    def test_empty_metadata(self):
        self._roundtrip(Metadata())

    def test_columns_only(self):
        self._roundtrip(Metadata(columns=['a', 'b', 'c']))

    def test_types_only(self):
        self._roundtrip(Metadata(types=['str', 'int', 'float']))

    def test_bool_only(self):
        self._roundtrip(Metadata(bool_sentinels=('yes', 'no')))

    def test_table_explicit(self):
        self._roundtrip(Metadata(table=5))

    def test_table_infer(self):
        self._roundtrip(Metadata(table=_TABLE_INFER))

    def test_unknown_forms(self):
        self._roundtrip(Metadata(unknown=[UnknownForm('custom', ['x', 'y'])]))

    def test_all_forms(self):
        self._roundtrip(Metadata(
            columns=['a', 'b'], types=['str', 'int'],
            bool_sentinels=('t', 'f'), table=2,
            unknown=[UnknownForm('extra', ['val'])],
        ))

    def test_columns_with_special_chars(self):
        self._roundtrip(Metadata(columns=['hello world', 'a,b', 'x\ny']))

    def test_columns_with_empty_names(self):
        self._roundtrip(Metadata(columns=['', 'b', '']))

    def test_bool_sentinels_with_empty_string(self):
        self._roundtrip(Metadata(bool_sentinels=('', 'no')))

    def test_unknown_form_with_empty_args(self):
        self._roundtrip(Metadata(unknown=[UnknownForm('nullable', ['', 'NULL'])]))

    def test_nsv_full_roundtrip(self):
        meta = Metadata(columns=['name', 'score'], types=['str', 'int'], table=2)
        data = [['Alice', '100'], ['Bob', '200']]

        ensv_seqseq = encode(meta, data)
        nsv_string = nsv.dumps(ensv_seqseq)
        recovered_seqseq = nsv.loads(nsv_string)

        result = read(recovered_seqseq)
        self.assertEqual(result.meta, meta)
        self.assertEqual(list(result), [['Alice', 100], ['Bob', 200]])


# ===================================================================
# Sidecared metadata
# ===================================================================

class TestSidecaredMetadata(unittest.TestCase):

    def test_sidecar_same_as_self_descriptive(self):
        meta = Metadata(
            columns=['id', 'name', 'active'],
            types=['int', 'str', 'bool'],
            bool_sentinels=('Y', 'N'), table=3,
        )
        data = [['1', 'Alice', 'Y'], ['2', 'Bob', 'N']]
        result = _read(meta, data)
        self.assertEqual(result, [[1, 'Alice', True], [2, 'Bob', False]])

        ensv_seqseq = [meta.to_row()] + data
        result2 = list(read(ensv_seqseq))
        self.assertEqual(result, result2)

    def test_sidecar_types_only(self):
        m = Metadata(types=['float', 'float'])
        self.assertEqual(
            _read(m, [['1.5', '2.5'], ['3.0', '4.0']]),
            [[1.5, 2.5], [3.0, 4.0]])

    def test_sidecar_table_validation(self):
        with self.assertRaises(ValueError):
            _read(Metadata(table=2), [['a', 'b', 'c']])

    def test_sidecar_no_metadata(self):
        self.assertEqual(
            _read(Metadata(), [['a', 'b'], ['c']]),
            [['a', 'b'], ['c']])


# ===================================================================
# encode
# ===================================================================

class TestEncode(unittest.TestCase):

    def test_encode_produces_valid_seqseq(self):
        meta = Metadata(columns=['x'])
        seqseq = encode(meta, [['1'], ['2']])
        self.assertEqual(len(seqseq), 3)

    def test_full_pipeline(self):
        meta = Metadata(types=['str', 'int', 'float', 'date'], table=4)
        data = [
            ['hello', '42', '3.14', '2024-01-01'],
            ['world', '-1', '0.0', '2024-12-31'],
        ]
        ensv_seqseq = encode(meta, data)
        nsv_string = nsv.dumps(ensv_seqseq)
        recovered = nsv.loads(nsv_string)
        result = read(recovered)

        self.assertEqual(result.meta, meta)
        rows = list(result)
        self.assertEqual(rows[0][0], 'hello')
        self.assertEqual(rows[0][1], 42)
        self.assertAlmostEqual(rows[0][2], 3.14)
        self.assertEqual(rows[0][3], datetime.date(2024, 1, 1))


# ===================================================================
# Edge cases
# ===================================================================

class TestEdgeCases(unittest.TestCase):

    def test_empty_metadata_row(self):
        meta = Metadata.from_row([])
        self.assertIsNone(meta.columns)
        self.assertIsNone(meta.types)
        self.assertIsNone(meta.bool)
        self.assertIsNone(meta.table)
        self.assertEqual(meta.unknown, [])

    def test_multiple_type_conversions_per_row(self):
        m = Metadata(types=['int', 'float', 'str'], bool_sentinels=('t', 'f'))
        self.assertEqual(_read(m, [['10', '2.5', 'hello']]), [[10, 2.5, 'hello']])

    def test_conversion_error_includes_indices(self):
        m = Metadata(types=['str', 'int', 'str'])
        with self.assertRaises(ValueError) as cm:
            _read(m, [['ok', 'bad', 'ok']])
        msg = str(cm.exception)
        self.assertIn('row 0', msg)
        self.assertIn('col 1', msg)

    def test_bool_sentinels_can_be_empty_string(self):
        m = Metadata(types=['bool'], bool_sentinels=('', 'n'))
        self.assertEqual(_read(m, [['']]), [[True]])
        self.assertEqual(_read(m, [['n']]), [[False]])


if __name__ == '__main__':
    unittest.main()
