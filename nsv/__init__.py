from .core import load, loads, dump, dumps
from .reader import Reader
from .writer import Writer

__version__ = "0.2.2"

FEATURES = {}

def patch_pandas():
    """Add NSV support to pandas if available in context."""
    import sys
    if 'pandas' not in sys.modules:
        return
    pd = sys.modules['pandas']

    def read_nsv(filepath_or_buffer, dtype=None, **kwargs):
        if isinstance(filepath_or_buffer, str):
            with open(filepath_or_buffer, 'r') as f:
                data = load(f)
        else:
            data = load(filepath_or_buffer)
        df = pd.DataFrame(data)
        if dtype is not None:
            df = df.astype(dtype)
        else:
            for col in df.columns:
                converted = pd.to_numeric(df[col], errors='coerce')
                # Keep only if no non-empty values were coerced to NaN
                lost = converted.isna() & (df[col] != '') & df[col].notna()
                if not lost.any():
                    df[col] = converted
        return df

    def to_nsv(self, path_or_buf=None, **kwargs):
        data = [['' if pd.isna(v) else str(v) for v in row] for row in self.values]

        if path_or_buf is None:
            return dumps(data)
        elif isinstance(path_or_buf, str):
            with open(path_or_buf, 'w') as f:
                dump(data, f)
        else:
            dump(data, path_or_buf)

    pd.read_nsv = read_nsv
    pd.DataFrame.to_nsv = to_nsv
