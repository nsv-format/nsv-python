"""ENSV -- metadata layer over NSV."""

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


def split(seqseq):
    """Split a seqseq at the first empty row.

    Returns (meta, offset, data) where meta is the rows before the
    separator, offset is the index of the first data row, and data
    is the rows after.  If no empty row exists, all rows are meta.
    """
    for i, row in enumerate(seqseq):
        if not row:
            return seqseq[:i], i + 1, seqseq[i + 1:]
    return list(seqseq), len(seqseq), []


def join(meta, data):
    """Inverse of split. Concatenates meta + empty row + data."""
    return list(meta) + [[]] + list(data)
