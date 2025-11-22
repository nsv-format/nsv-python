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

def lift(cells: List[str]) -> str:
    """Lift operation: Takes a sequence of strings and interprets them as cells of a single row.

    Semantics: lift: Seq[String] → Row — dimension-shifting operation that nests data one level deeper.
    Mechanism: Encodes newlines as \\n, backslashes as \\\\, empty lines as \\

    Example:
        ["a", "b", "", "d"] → "a\\nb\\n\\\\nd\\n\\n"

    Args:
        cells: A sequence of strings to encode as a single NSV row

    Returns:
        A string containing the NSV-encoded representation of the row
    """
    lines = [Writer.escape(cell) for cell in cells]
    lines.append('')  # Empty line to mark end of row
    return ''.join(f'{line}\n' for line in lines)

def unlift(row_str: str) -> List[str]:
    """Unlift operation: Reverses the lift operation, extracting cells from an NSV row string.

    This is the inverse of lift, satisfying the property: unlift(lift(x)) = x

    Args:
        row_str: An NSV-encoded row string (as produced by lift)

    Returns:
        A list of strings representing the decoded cells

    Example:
        "a\\nb\\n\\\\nd\\n\\n" → ["a", "b", "", "d"]
    """
    # Remove the final newline if present
    if row_str.endswith('\n'):
        row_str = row_str[:-1]

    # Split by newlines
    lines = row_str.split('\n')

    # The last line should be empty (row terminator)
    if lines and lines[-1] == '':
        lines = lines[:-1]

    # Unescape each line
    return [Reader.unescape(line) for line in lines]
