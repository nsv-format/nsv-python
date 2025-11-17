from typing import Iterable, List

from .reader import Reader
from .writer import Writer


def loads(s: str) -> List[List[str]]:
    """Load NSV data from a string (pure Python implementation)."""
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

    # Handle any remaining content after the last newline
    if start < len(s):
        row.append(Reader.unescape(s[start:]))

    # Exhaustive operation: include incomplete row at EOF if present
    if row:
        data.append(row)

    return data


def dumps(data: Iterable[Iterable[str]]) -> str:
    """Write elements to an NSV string (pure Python implementation)."""
    lines = []
    for i, row in enumerate(data):
        for cell in row:
            lines.append(Writer.escape(cell))
        lines.append('')
    return ''.join(f'{line}\n' for line in lines)
