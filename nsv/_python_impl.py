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


def _unescape_bytes(s: bytes) -> bytes:
    """Unescape a single NSV cell at the byte level."""
    if s == b'\\':
        return b''
    if b'\\' not in s:
        return s
    out = bytearray()
    escaped = False
    for byte in s:
        if escaped:
            if byte == 0x6E:    # b'n' -> LF
                out.append(0x0A)
            elif byte == 0x5C:  # b'\\' -> b'\'
                out.append(0x5C)
            else:               # unknown escape: pass through
                out.append(0x5C)
                out.append(byte)
            escaped = False
        elif byte == 0x5C:      # b'\'
            escaped = True
        else:
            out.append(byte)
    return bytes(out)


def _escape_bytes(s: bytes) -> bytes:
    """Escape a single NSV cell at the byte level."""
    if not s:
        return b'\\'
    if b'\n' not in s and b'\\' not in s:
        return s
    out = bytearray()
    for byte in s:
        if byte == 0x5C:    # b'\'
            out.extend(b'\\\\')
        elif byte == 0x0A:  # LF
            out.extend(b'\\n')
        else:
            out.append(byte)
    return bytes(out)


def loads_bytes(b: bytes) -> List[List[bytes]]:
    """Load NSV data from bytes (pure Python implementation)."""
    data = []
    row = []
    start = 0
    n = len(b)
    for pos in range(n):
        if b[pos] == 0x0A:  # LF
            if pos - start >= 1:
                row.append(_unescape_bytes(b[start:pos]))
            else:
                data.append(row)
                row = []
            start = pos + 1

    # Handle any remaining content after the last newline
    if start < n:
        row.append(_unescape_bytes(b[start:]))

    # Exhaustive operation: include incomplete row at EOF if present
    if row:
        data.append(row)

    return data


def dumps_bytes(data: Iterable[Iterable[bytes]]) -> bytes:
    """Write elements to NSV bytes (pure Python implementation)."""
    out = bytearray()
    for row in data:
        for cell in row:
            out.extend(_escape_bytes(cell))
            out.append(0x0A)  # LF after each cell
        out.append(0x0A)      # blank line after each row
    return bytes(out)
