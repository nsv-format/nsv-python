"""ENSV -- metadata layer over NSV."""

import datetime
import uuid
import warnings
from typing import List, Iterable

from .reader import Reader
from .writer import Writer


def lift(seqseq: Iterable[Iterable[str]]) -> List[str]:
    """
    Lift a seqseq into a single row (sequence of strings), removing one
    dimension without losing structural information.

    Escapes every cell and chains them with empty-string separators
    between rows (separator semantics, not terminator).
    """
    result = []
    first = True
    for row in seqseq:
        if not first:
            result.append('')
        for cell in row:
            result.append(Writer.escape(cell))
        first = False
    return result


def unlift(seq: Iterable[str]) -> List[List[str]]:
    """
    Unlift a sequence of strings back into a seqseq, recovering the
    dimension collapsed by lift.

    1. If the current element is non-empty, unescape it and append to the
       current row
    2. If the current element is empty, terminate the current row
    3. At end of input, terminate the current row
    """
    rows = []
    row = []
    for element in seq:
        if element != '':
            row.append(Reader.unescape(element))
        else:
            rows.append(row)
            row = []
    rows.append(row)
    return rows


class UnknownForm:
    def __init__(self, name, args):
        self.name = name
        self.args = list(args)

    def __eq__(self, other):
        return (isinstance(other, UnknownForm)
                and self.name == other.name
                and self.args == other.args)

    def __repr__(self):
        return f"UnknownForm({self.name!r}, {self.args!r})"


_TABLE_INFER = object()


class Metadata:
    KNOWN_TYPES = frozenset({
        'str', 'int', 'float', 'bool', 'date', 'datetime', 'uuid',
    })

    def __init__(self, *, columns=None, types=None, bool_sentinels=None,
                 table=None, unknown=None):
        self.columns = list(columns) if columns is not None else None
        self.types = list(types) if types is not None else None
        self.bool = tuple(bool_sentinels) if bool_sentinels is not None else None
        self.table = table
        self.unknown = list(unknown) if unknown is not None else []
        self._validate_consistency()

    def _validate_consistency(self):
        effective_width = self.table if isinstance(self.table, int) else None

        if self.columns is not None and effective_width is not None:
            if len(self.columns) != effective_width:
                raise ValueError(
                    f"columns: arity ({len(self.columns)}) does not match "
                    f"table width ({effective_width})")
        if self.types is not None and effective_width is not None:
            if len(self.types) != effective_width:
                raise ValueError(
                    f"types: arity ({len(self.types)}) does not match "
                    f"table width ({effective_width})")
        if self.columns is not None and self.types is not None:
            if len(self.columns) != len(self.types):
                raise ValueError(
                    f"columns: arity ({len(self.columns)}) does not match "
                    f"types: arity ({len(self.types)})")
        if self.types is not None and 'bool' in self.types and self.bool is None:
            raise ValueError(
                "types: includes 'bool' but no bool form is present")

    @classmethod
    def from_row(cls, row):
        forms = unlift(row)

        columns = None
        types = None
        bool_sentinels = None
        table = None
        unknown = []

        for form in forms:
            if not form:
                continue
            name = form[0]
            args = form[1:]

            if '/' in name:
                raise ValueError(
                    f"namespaced form {name!r} is reserved for extensions")

            if name == 'columns:':
                columns = args
            elif name == 'types:':
                types = args
            elif name == 'bool':
                if len(args) != 2:
                    raise ValueError(
                        f"bool form requires exactly 2 arguments, "
                        f"got {len(args)}")
                bool_sentinels = (args[0], args[1])
            elif name == 'table':
                if len(args) == 0:
                    table = _TABLE_INFER
                elif len(args) == 1:
                    table = int(args[0])
                else:
                    raise ValueError(
                        f"table form takes 0 or 1 argument, got {len(args)}")
            else:
                unknown.append(UnknownForm(name, args))

        return cls(
            columns=columns,
            types=types,
            bool_sentinels=bool_sentinels,
            table=table,
            unknown=unknown,
        )

    def to_row(self):
        forms = []
        if self.columns is not None:
            forms.append(['columns:'] + self.columns)
        if self.types is not None:
            forms.append(['types:'] + self.types)
        if self.bool is not None:
            forms.append(['bool', self.bool[0], self.bool[1]])
        if self.table is _TABLE_INFER:
            forms.append(['table'])
        elif self.table is not None:
            forms.append(['table', str(self.table)])
        for uf in self.unknown:
            forms.append([uf.name] + uf.args)
        return lift(forms)

    def __eq__(self, other):
        return (isinstance(other, Metadata)
                and self.columns == other.columns
                and self.types == other.types
                and self.bool == other.bool
                and self.table == other.table
                and self.unknown == other.unknown)

    def __repr__(self):
        parts = []
        if self.columns is not None:
            parts.append(f"columns={self.columns!r}")
        if self.types is not None:
            parts.append(f"types={self.types!r}")
        if self.bool is not None:
            parts.append(f"bool={self.bool!r}")
        if self.table is not None:
            parts.append(f"table={self.table!r}")
        if self.unknown:
            parts.append(f"unknown={self.unknown!r}")
        return f"Metadata({', '.join(parts)})"


class ENSVReader:
    def __init__(self, meta):
        self._meta = meta

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    def read(self, rows):
        meta = self._meta
        table_width = meta.table if isinstance(meta.table, int) else None

        for i, row in enumerate(rows):
            if meta.table is not None:
                if table_width is None:
                    table_width = len(row)
                elif len(row) != table_width:
                    raise ValueError(
                        f"row {i}: expected {table_width} columns, "
                        f"got {len(row)}")

            if meta.types is not None:
                converted = []
                for j, cell in enumerate(row):
                    if j < len(meta.types):
                        converted.append(
                            _convert(cell, meta, j, i, j))
                    else:
                        converted.append(cell)
                yield converted
            else:
                yield list(row)


class _ReadResult:
    def __init__(self, meta, iterator):
        self.meta = meta
        self._iterator = iterator

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iterator)


def peel(rows):
    it = iter(rows)
    try:
        meta_row = next(it)
    except StopIteration:
        raise ValueError("ENSV data must have at least a metadata row")
    return Metadata.from_row(meta_row), it


def read(rows):
    meta, tail = peel(rows)
    reader = ENSVReader(meta)
    return _ReadResult(meta, reader.read(tail))


def encode(metadata, data):
    return [metadata.to_row()] + [list(row) for row in data]


def _convert(cell, meta, type_idx, row_idx, col_idx):
    type_name = meta.types[type_idx]

    if type_name == 'str':
        return cell

    if type_name == 'int':
        try:
            return int(cell)
        except ValueError:
            raise ValueError(
                f"row {row_idx}, col {col_idx}: "
                f"cannot convert {cell!r} to int")

    if type_name == 'float':
        try:
            return float(cell)
        except ValueError:
            raise ValueError(
                f"row {row_idx}, col {col_idx}: "
                f"cannot convert {cell!r} to float")

    if type_name == 'bool':
        true_sentinel, false_sentinel = meta.bool
        if cell == true_sentinel:
            return True
        if cell == false_sentinel:
            return False
        raise ValueError(
            f"row {row_idx}, col {col_idx}: "
            f"{cell!r} matches neither true sentinel "
            f"{true_sentinel!r} nor false sentinel "
            f"{false_sentinel!r}")

    if type_name == 'date':
        try:
            return datetime.date.fromisoformat(cell)
        except ValueError:
            raise ValueError(
                f"row {row_idx}, col {col_idx}: "
                f"cannot parse {cell!r} as ISO 8601 date")

    if type_name == 'datetime':
        try:
            return datetime.datetime.fromisoformat(cell)
        except ValueError:
            raise ValueError(
                f"row {row_idx}, col {col_idx}: "
                f"cannot parse {cell!r} as ISO 8601 datetime")

    if type_name == 'uuid':
        try:
            return uuid.UUID(cell)
        except ValueError:
            raise ValueError(
                f"row {row_idx}, col {col_idx}: "
                f"cannot parse {cell!r} as UUID")

    warnings.warn(
        f"unknown type {type_name!r} at col {col_idx}, treating as str")
    return cell
