from typing import Iterable, List

from .reader import Reader
from .writer import Writer

def load(file_obj) -> List[List[str]]:
    """Load NSV data from a file-like object."""
    return list(Reader(file_obj))

def loads(s: str) -> List[List[str]]:
    """Load NSV data from a string."""
    data = []
    row = []
    start = 0
    for pos, c in enumerate(s):
        if c == '\n':
            if pos - start >= 1:
                row.append(Reader.unescape(s[start:pos]))
            else:
                data.append(row)
                row = []
            start = pos + 1
    return data

def dump(data: Iterable[Iterable[str]], file_obj):
    """Write elements to an NSV file."""
    Writer(file_obj).write_rows(data)
    return file_obj

def dumps(data: Iterable[Iterable[str]]) -> str:
    """Write elements to an NSV string."""
    lines = []
    for i, row in enumerate(data):
        for cell in row:
            lines.append(Writer.escape(cell))
        lines.append('')
    return ''.join(f'{line}\n' for line in lines)

def lift(seqseq: List[List[str]]) -> List[str]:
    seq = []
    for i, row in enumerate(seqseq):
        if i:
            seq.append('')
        for cell in row:
            seq.append(Writer.escape(cell))
    return seq

def unlift(seq: List[str]) -> List[List[str]]:
    seqseq = []
    row = []
    for line in seq:
        if line:
            row.append(Reader.unescape(line))
        else:
            seqseq.append(row)
            row = []
    seqseq.append(row)
    return seqseq
