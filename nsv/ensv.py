from typing import List, Iterable

from .reader import Reader
from .writer import Writer
from .util import spill


def lift(seqseq: Iterable[Iterable[str]]) -> List[str]:
    """
    Lift a seqseq into a single row (sequence of strings), removing one
    dimension without losing structural information.

    lift = init ∘ spill[String, ''] ∘ map(map(escape))

    The result uses separator semantics: empty strings delimit row boundaries,
    and the final terminator is discarded (init) to preserve line numbers.

    This makes [] irrepresentable; a non-empty seqseq is required.
    """
    rows = list(seqseq)
    if not rows:
        raise ValueError("Cannot lift an empty seqseq: [] is irrepresentable")
    escaped = [[Writer.escape(cell) for cell in row] for row in rows]
    spilled = spill(escaped, '')
    return spilled[:-1]  # init: discard trailing terminator


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
