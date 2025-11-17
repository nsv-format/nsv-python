from typing import Iterable, List

from .reader import Reader
from .writer import Writer

# Try to use fast Rust implementation, fall back to Python
try:
    from nsv_rust_ext import loads, dumps
except ImportError:
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

        # Handle any remaining content after the last newline
        if start < len(s):
            row.append(Reader.unescape(s[start:]))

        # Exhaustive operation: include incomplete row at EOF if present
        if row:
            data.append(row)

        return data

    def dumps(data: Iterable[Iterable[str]]) -> str:
        """Write elements to an NSV string."""
        lines = []
        for i, row in enumerate(data):
            for cell in row:
                lines.append(Writer.escape(cell))
            lines.append('')
        return ''.join(f'{line}\n' for line in lines)

def load(file_obj) -> List[List[str]]:
    """Load NSV data from a file-like object."""
    return loads(file_obj.read())

def dump(data: Iterable[Iterable[str]], file_obj):
    """Write elements to an NSV file."""
    Writer(file_obj).write_rows(data)
    return file_obj
