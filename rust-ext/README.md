# NSV Rust Extension

This is a Python extension module that provides high-performance NSV parsing and serialization using the `nsv-rust` library via PyO3 bindings.

## Performance

The Rust implementation is significantly faster than the pure Python implementation:

- **Average parsing speedup: 5.71x**
- **Average serialization speedup: 1.65x**
- **Up to 15.17x faster** for data with backslashes

See [RUST_BENCHMARK_RESULTS.md](../RUST_BENCHMARK_RESULTS.md) for detailed benchmarks.

## Building

### Prerequisites

```bash
pip install maturin
```

### Build Release Wheel

```bash
maturin build --release
```

The wheel will be created in `target/wheels/`.

### Development Mode

For development, you can install in editable mode:

```bash
maturin develop --release
```

## Usage

```python
import nsv_rust_ext

# Parse NSV string
data = nsv_rust_ext.loads("col1\ncol2\n\na\nb\n\nc\nd\n")
# Returns: [['col1', 'col2'], ['a', 'b'], ['c', 'd']]

# Serialize to NSV string
nsv_string = nsv_rust_ext.dumps([['col1', 'col2'], ['a', 'b']])
# Returns: "col1\ncol2\n\na\nb\n\n"
```

## Dependencies

- `pyo3 = "0.20"` - Python bindings for Rust
- `nsv = "0.0.3"` - The Rust NSV implementation

## Implementation Details

The extension provides two main functions:

- `loads(s: str) -> List[List[str]]`: Parse an NSV string into a list of lists
- `dumps(data: List[List[str]]) -> str`: Serialize data to an NSV string

These are drop-in replacements for the Python implementation in `nsv.core`.

### Technical Details

The Rust implementation uses:

1. **SIMD-optimized search**: `memchr` library for fast newline detection
2. **Parallel processing**: `rayon` for multi-threaded parsing of large files (>64KB)
3. **Efficient string handling**: Rust's zero-cost abstractions avoid Python object overhead
4. **Smart thresholding**: Sequential parsing for small files, parallel for large files

## Integration with nsv-python

You can use this as a drop-in replacement:

```python
try:
    from nsv_rust_ext import loads, dumps
except ImportError:
    from nsv import loads, dumps  # Fallback to Python implementation
```

Or integrate it directly into the `nsv` package by modifying `nsv/core.py`.
