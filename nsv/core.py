from typing import Iterable, List

from .reader import Reader
from .writer import Writer

def load(file_obj) -> List[List[str]]:
    """Load NSV data from a file-like object."""
    return loads(file_obj.read())

def loads(s: str) -> List[List[str]]:
    """Load NSV data from a string."""
    data = []
    row = []
    lines = s.split('\n')
    if lines[-1] == '':
        lines.pop()
    for line in lines:
        if line == '':
            data.append(row)
            row = []
        else:
            row.append(Reader.unescape(line))
    if row:
        data.append(row)
    return data

def dump(data: Iterable[Iterable[str]], file_obj):
    """Write elements to an NSV file."""
    Writer(file_obj).write_rows(data)
    return file_obj

def dumps(data: Iterable[Iterable[str]]) -> str:
    """Write elements to an NSV string."""
    lines = []
    for row in data:
        for cell in row:
            lines.append(Writer.escape(cell))
        lines.append('')
    return ''.join(f'{line}\n' for line in lines)

# Try to use fast Rust implementation if available
try:
    from ._rust import loads as _loads_rs, dumps as _dumps_rs
    loads = _loads_rs
    dumps = _dumps_rs
except ImportError:
    pass
