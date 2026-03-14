from .core import load, loads, dump, dumps, loads_bytes
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
    from pandas.io.parsers.readers import STR_NA_VALUES

    bool_values = frozenset({'true', 'false'})

    def _infer_column(col):
        na_mask = col.isin(STR_NA_VALUES)
        col_na = col.where(~na_mask)

        converted = pd.to_numeric(col_na, errors='coerce')
        if not (converted.isna() & col_na.notna()).any():
            return converted

        non_na = col_na.dropna()
        if len(non_na) > 0 and non_na.str.lower().isin(bool_values).all():
            as_bool = col_na.map(lambda x: x.lower() == 'true' if pd.notna(x) else x)
            return as_bool if na_mask.any() else as_bool.astype(bool)

        return col_na

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
                df[col] = _infer_column(df[col])
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
