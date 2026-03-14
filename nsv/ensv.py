"""ENSV -- metadata layer over NSV."""

from typing import List, Iterable

from .reader import Reader as NSVReader
from .writer import Writer as NSVWriter


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
            result.append(NSVWriter.escape(cell))
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
            row.append(NSVReader.unescape(element))
        else:
            rows.append(row)
            row = []
    rows.append(row)
    return rows


class Reader:
    def __init__(self, file_obj):
        self._inner = NSVReader(file_obj)
        self.meta = []
        for row in self._inner:
            if not row:
                break
            self.meta.append(row)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._inner)


class Writer:
    def __init__(self, file_obj):
        self._inner = NSVWriter(file_obj)

    def write_meta(self, meta):
        self._inner.write_rows(meta)
        self._inner.write_row([])

    def write_row(self, row):
        self._inner.write_row(row)

    def write_rows(self, rows):
        self._inner.write_rows(rows)
