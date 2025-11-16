# NSV Rust Backend: Benchmarks and Integration

## Performance Benchmarks

### Methodology

**Test Suite**: `benchmarks/python_vs_rust.py`
- 9 test scenarios covering varied data patterns
- Each test runs 5 iterations, measures mean and std dev
- Tests both parsing (`loads`) and serialization (`dumps`)
- Data sizes: 11 KB to 13.34 MB

**Scenarios Tested**:
1. Simple tables (varying sizes: 100 to 100k rows)
2. Wide tables (many columns)
3. Special characters (newlines, backslashes, mixed)
4. Realistic heterogeneous data

**Environment**: Single-threaded, measuring wall-clock time

### Results Summary

| Metric | Average | Best Case |
|--------|---------|-----------|
| Parsing speedup | **5.71x** | 15.17x (backslash-heavy) |
| Serialization speedup | **1.65x** | 2.01x (wide tables) |

**Why Rust is faster**:
- SIMD-optimized search (`memchr`) for row boundaries
- Parallel processing (`rayon`) for files >64KB
- Zero-cost abstractions vs Python object overhead

**See**: Full results in benchmark output when running `benchmarks/python_vs_rust.py`

---

## Cross-Validation

### Methodology

**Test Suite**: `tests/cross_validate.py`
- Validates semantic compatibility across all Python test samples
- Tests: loads(), dumps(), roundtrips, edge cases, escape sequences, empty cases
- Compares Python vs Rust output for identical inputs

**Coverage**: 76 test cases across 6 categories

### Results

- **Compatibility**: 100% (76/76 tests pass)
- **Python-Rust parity**: Perfect match on all test cases
- **Edge cases**: All handled identically

---

## Streaming Semantics

### Design Decision

**Exhaustive operations** (loads/load): Include incomplete rows at EOF
- Pragmatic for complete data (files, strings)
- EOF is unambiguous terminator

**Incremental operations** (Reader): Never emit incomplete rows
- Proper streaming semantics
- Critical for tailing logs, network streams
- Python's file iterator can't distinguish "pause" from "EOF"

### Validation

**Test Suite**: `tests/test_streaming.py` (26 tests)
- Reader: Verified to never emit incomplete rows
- loads/load: Verified to include incomplete rows
- Memory efficiency validated (1000+ row streaming)

---

## Integration Strategy

### Current Status

**Rust Extension**: `rust-ext/` (PyO3 bindings to nsv-rust v0.0.3)
- Exposes `loads()` and `dumps()`
- Drop-in replacement for Python implementation

**Hybrid Approach**:
```python
try:
    from nsv_rust_ext import loads, dumps
except ImportError:
    from nsv.core import loads, dumps  # Pure Python fallback
```

### Distribution

**CI Workflow**: `.github/workflows/wheels.yml`
- Builds wheels for Linux (x86_64, aarch64), macOS (x86_64, ARM64), Windows (x64)
- Manual triggering (no automatic publishing)
- Artifacts available for download

**For Publishing**:
```bash
# Build wheels locally or download from CI
maturin build --release

# Publish manually
twine upload dist/*.whl
```

### Installation (Users)

```bash
pip install nsv
# Gets pre-compiled wheel (Rust backend)
# Falls back to pure Python on exotic platforms
```

**Zero runtime dependencies** - PyO3 is build-time only.

---

## Implementation Scope

**Rust Accelerates**:
- `loads(s: str)` - Parse complete NSV string (5.71x faster)
- `dumps(data)` - Serialize to NSV string (1.65x faster)

**Pure Python Remains**:
- `Reader(file)` - Incremental/streaming reader
- `Writer(file)` - Incremental/streaming writer
- Rationale: Streaming is I/O bound, Rust gains modest

**Future**: Could add Rust streaming if it becomes a bottleneck.
