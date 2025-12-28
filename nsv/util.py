from typing import TypeVar, Iterable, List

from .writer import Writer
from .reader import Reader

T = TypeVar('T')


def escape_seqseq(seqseq: Iterable[Iterable[str]]) -> List[List[str]]:
    """Apply NSV escaping at depth 2: map(map(escape))."""
    return [[Writer.escape(cell) for cell in row] for row in seqseq]


def unescape_seqseq(seqseq: Iterable[Iterable[str]]) -> List[List[str]]:
    """Apply NSV unescaping at depth 2: map(map(unescape))."""
    return [[Reader.unescape(cell) for cell in row] for row in seqseq]


def spill(seqseq: Iterable[Iterable[T]], marker: T) -> List[T]:
    """
    Collapse a dimension of seqseq by spilling termination markers
    into the resulting flat sequence.
    Pure structural operation - does NOT perform escaping.
    encode = spill[Char, '\n'] ∘ spill[String, ''] ∘ escape_seqseq
    """
    seq = []
    for row in seqseq:
        for item in row:
            seq.append(item)
        seq.append(marker)
    return seq


def unspill(seq: Iterable[T], marker: T) -> List[List[T]]:
    """
    Recover a dimension by picking up termination markers from
    the provided sequence.
    Pure structural operation - does NOT perform unescaping.
    decode = unescape_seqseq ∘ unspill[String, ''] ∘ unspill[Char, '\n']
    """
    seqseq = []
    row = []
    for item in seq:
        if item != marker:
            row.append(item)
        else:
            seqseq.append(row)
            row = []
    # Strict: don't append incomplete rows
    return seqseq
