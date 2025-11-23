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

def lift(s: str) -> str:
    """Encodes NSV lines as cells of a single row (dimension collapse)."""
    lines = s.split('\n')[:-1]
    if lines and lines[-1] == '':
        lines = lines[:-1]
    return dumps([lines])

def unlift(s: str) -> str:
    """Inverse of lift. Requires exactly one row."""
    data = loads(s)
    if len(data) != 1:
        raise ValueError(f"unlift requires exactly one row, got {len(data)}")
    lines = data[0]
    lines.append('')
    return '\n'.join(lines) + '\n'
