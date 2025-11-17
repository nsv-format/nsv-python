from typing import Iterable, List

from .reader import Reader
from .writer import Writer

# Try to use fast Rust implementation, fall back to Python
try:
    from nsv_rust_ext import loads, dumps
except ImportError:
    from ._python_impl import loads, dumps


def load(file_obj) -> List[List[str]]:
    """Load NSV data from a file-like object."""
    return loads(file_obj.read())


def dump(data: Iterable[Iterable[str]], file_obj):
    """Write elements to an NSV file."""
    Writer(file_obj).write_rows(data)
    return file_obj
