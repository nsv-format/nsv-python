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
    """Lift operation: Collapses one dimension by interpreting lines as cells of a single row.

    Takes an NSV string and encodes all its lines as cells of a single row.
    This is a dimension-shifting operation that reduces nesting by one level.

    Semantics: NSV[n] → NSV[n-1] where dimensions collapse but data is preserved.

    Example:
        Input (2D, 2 rows):  "a\\nb\\n\\nc\\nd\\n\\n"
        Output (1D, 1 row):  "a\\nb\\n\\\\\\nc\\nd\\n\\\\\\n\\n"

    Args:
        s: An NSV-encoded string

    Returns:
        An NSV string with lines encoded as a single row
    """
    lines = s.split('\n')[:-1]
    return dumps([lines])

def unlift(s: str) -> str:
    """Unlift operation: Reverses lift by expanding one row into multiple lines.

    This is the inverse of lift, satisfying: unlift(lift(x)) = x

    Args:
        s: An NSV string containing exactly one row

    Returns:
        An NSV string reconstructed from the row's cells

    Raises:
        ValueError: If the input doesn't contain exactly one row
    """
    data = loads(s)
    if len(data) != 1:
        raise ValueError(f"unlift requires exactly one row, got {len(data)}")
    lines = data[0]
    return '\n'.join(lines) + '\n'
