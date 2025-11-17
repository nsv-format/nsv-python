from .reader import Reader
from .writer import Writer

# Try to use fast Rust implementation, fall back to Python
try:
    from nsv_rust_ext import loads, dumps
except ImportError:
    from .core import loads, dumps

def load(file_obj):
    """Load NSV data from a file-like object."""
    return loads(file_obj.read())

def dump(data, file_obj):
    """Write elements to an NSV file."""
    Writer(file_obj).write_rows(data)
    return file_obj

__version__ = "0.2.1"

FEATURES = {}

def patch_pandas():
    """Add NSV support to pandas if available in context."""
    import sys
    if 'pandas' not in sys.modules:
        return
    pd = sys.modules['pandas']

    def read_nsv(filepath_or_buffer, **kwargs):
        if isinstance(filepath_or_buffer, str):
            with open(filepath_or_buffer, 'r') as f:
                data = load(f)
        else:
            data = load(filepath_or_buffer)
        return pd.DataFrame(data)

    def to_nsv(self, path_or_buf=None, **kwargs):
        # TODO: this is naive, pandas can have non-string values
        data = self.values

        if path_or_buf is None:
            return dumps(data)
        elif isinstance(path_or_buf, str):
            with open(path_or_buf, 'w') as f:
                dump(data, f)
        else:
            dump(data, path_or_buf)

    pd.read_nsv = read_nsv
    pd.DataFrame.to_nsv = to_nsv
