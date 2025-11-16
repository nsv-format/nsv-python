# NSV Rust Backend Integration Plan

## Executive Summary

This document outlines the plan to integrate the Rust-backed NSV implementation as an optional performance backend for the nsv-python library.

## Key Decisions

### 1. Fix Python `loads()` Bug

**Issue**: Python's `loads()` function doesn't match `Reader` class behavior for unterminated rows.

**Evidence**:
```python
content = 'field1\nfield2\nfield3\n\nvalue1\nvalue2\nvalue3'
# (two rows, second row missing final newline)

# Python Reader (load):  [['field1', 'field2', 'field3'], ['value1', 'value2', 'value3']] ✓
# Rust loads:            [['field1', 'field2', 'field3'], ['value1', 'value2', 'value3']] ✓
# Python loads:          [['field1', 'field2', 'field3']] ✗ MISSING SECOND ROW!
```

**Root Cause**: `loads()` in `nsv/core.py` line 23 doesn't append the final row if the string doesn't end with `\n\n`.

**Fix**:
```python
def loads(s: str) -> List[List[str]]:
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

    # FIX: Append final row if present
    if row:
        data.append(row)

    return data
```

**Justification**:
- NSV spec says rows "should" end with double newline, but doesn't mandate it
- Files without trailing newlines at EOF are common in practice
- Python's own `Reader` class handles this case (includes final row)
- Rust implementation matches `Reader` behavior
- Consistency: `loads()` should behave like `load()`

**Priority**: HIGH - affects correctness

### 2. Rust Backend Scope

**What Rust Accelerates**:
- ✅ `loads(s: str) -> List[List[str]]` - Parse complete NSV string
- ✅ `dumps(data) -> str` - Serialize complete data to NSV string

**What Stays Pure Python**:
- ✅ `Reader(file_obj)` - Incremental/streaming reader for files
- ✅ `Writer(file_obj)` - Incremental/streaming writer for files

**Rationale**:
- Most use cases work with complete data (Rust gives 5.71x speedup)
- Streaming is I/O bound anyway (less benefit from Rust)
- Reader/Writer are simple, mature, and handle edge cases well
- Infinite streams require iterator protocol, complex to expose via PyO3
- Can add Rust streaming later if needed

### 3. Integration Strategy

**Hybrid Approach with Automatic Fallback**:

```python
# In nsv/__init__.py or nsv/core.py

try:
    from nsv_rust_ext import loads as _rust_loads, dumps as _rust_dumps
    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False

# Keep existing Python implementations as fallback
def _python_loads(s: str) -> List[List[str]]:
    # ... existing loads() code (after bug fix)
    ...

def _python_dumps(data: Iterable[Iterable[str]]) -> str:
    # ... existing dumps() code
    ...

# Public API with automatic backend selection
def loads(s: str) -> List[List[str]]:
    """Load NSV data from a string."""
    if _RUST_AVAILABLE:
        return _rust_loads(s)
    return _python_loads(s)

def dumps(data: Iterable[Iterable[str]]) -> str:
    """Serialize data to NSV string."""
    if _RUST_AVAILABLE:
        return _rust_dumps(data)
    return _python_dumps(data)

# Reader/Writer stay pure Python
# load() and dump() use Reader/Writer (unchanged)
```

**Benefits**:
- ✅ Users on common platforms get 5.71x speedup automatically
- ✅ Users on exotic platforms still work (pure Python fallback)
- ✅ No code changes for users
- ✅ No installation complexity (pre-built wheels)
- ✅ Zero runtime dependencies

### 4. Distribution Strategy

**Pre-built Binary Wheels via GitHub Actions**:
- Automated builds on every release tag (`v*`)
- Uses PyO3/maturin-action for reliable wheel building
- Covers major platforms and architectures:
  - **Linux**: x86_64, aarch64 (ARM)
  - **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)
  - **Windows**: x64
  - **Python**: 3.8, 3.9, 3.10, 3.11, 3.12

**User Installation**:
```bash
pip install nsv
# Downloads pre-compiled wheel for your platform
# NO Rust toolchain needed!
# NO compilation!
# Just works™
```

**For Exotic Platforms**:
- Source distribution (sdist) still available
- Falls back to pure Python if Rust extension fails to import
- Users never blocked from using the library

### 5. CI/CD Pipeline

**GitHub Actions Workflow** (`.github/workflows/wheels.yml`):

1. **Build Phase**:
   - Linux wheels (x86_64, aarch64)
   - macOS wheels (x86_64, aarch64)
   - Windows wheels (x64)
   - Source distribution

2. **Test Phase**:
   - Install wheels on all platforms
   - Test import works
   - Run cross-validation suite (Python 3.11)
   - Ensures compatibility before release

3. **Release Phase** (only on version tags):
   - Upload all wheels to PyPI
   - Upload source distribution
   - Uses `PYPI_API_TOKEN` secret

**Triggering**:
```bash
# Create release
git tag v0.3.0
git push origin v0.3.0

# GitHub Actions automatically:
# 1. Builds wheels for all platforms
# 2. Tests them
# 3. Publishes to PyPI
```

Or trigger manually via GitHub Actions UI for testing.

## Performance Impact

Based on comprehensive benchmarks:

| Metric | Speedup |
|--------|---------|
| Average parsing (loads) | 5.71x faster |
| Average serialization (dumps) | 1.65x faster |
| Best case (backslash-heavy data) | 15.17x faster parsing |

See `RUST_BENCHMARK_RESULTS.md` for detailed analysis.

## Semantic Compatibility

Cross-validation results: **97.4% compatible** (74/76 tests pass)

The 2 failing tests expose the bug in Python `loads()` - after fixing, we expect **100% compatibility**.

See `CROSS_VALIDATION_REPORT.md` for detailed analysis.

## Implementation Checklist

### Phase 1: Bug Fix (can do independently)
- [ ] Fix `loads()` in `nsv/core.py` to handle unterminated rows
- [ ] Add regression test for the bug
- [ ] Verify all existing tests still pass
- [ ] Release as v0.2.2 (patch fix)

### Phase 2: Rust Backend Integration
- [ ] Move Rust extension to proper location (decide: separate package or submodule?)
- [ ] Implement hybrid backend in `nsv/__init__.py` or `nsv/core.py`
- [ ] Add environment variable for forcing backend choice (for testing)
- [ ] Update tests to run against both backends
- [ ] Set up PyPI API token in GitHub Secrets
- [ ] Test wheel building workflow manually
- [ ] Update README with performance notes
- [ ] Release as v0.3.0 (minor - new optional feature)

### Phase 3: Documentation & Polish
- [ ] Add "Performance" section to README
- [ ] Document Reader/Writer vs loads/dumps trade-offs
- [ ] Add migration guide (if any breaking changes)
- [ ] Create CHANGELOG entry
- [ ] Update examples if needed

## Versioning

| Version | Changes |
|---------|---------|
| 0.2.1 | Current version |
| 0.2.2 | Fix `loads()` bug (pure Python) |
| 0.3.0 | Add Rust backend with fallback |

## Open Questions

1. **Package structure**: Should `nsv_rust_ext` be:
   - A. Part of the main `nsv` package wheel?
   - B. Separate optional package (`pip install nsv[rust]`)?
   - **Recommendation**: Part of main package (simpler, automatic)

2. **Backend selection**: Allow users to force backend?
   ```python
   # For testing or debugging
   import os
   os.environ['NSV_FORCE_PYTHON'] = '1'  # Disable Rust
   ```
   **Recommendation**: Yes, helpful for debugging

3. **Deprecation path**: Should we ever deprecate pure Python?
   **Recommendation**: No, keep it forever as fallback

## Testing Strategy

```bash
# Test both backends
pytest tests/                           # Pure Python
NSV_FORCE_RUST=1 pytest tests/          # Force Rust
python tests/cross_validate.py         # Both compared
```

CI runs all three on every push.

## Rollout Plan

**Conservative Approach**:
1. Release v0.2.2 with bug fix (pure Python)
2. Let it bake for a week, ensure no issues
3. Release v0.3.0 with Rust backend
4. Monitor PyPI download stats and issue reports
5. If issues arise, easy to debug (pure Python still works)

**Aggressive Approach**:
1. Combine bug fix + Rust backend in v0.3.0
2. Release immediately
3. Faster time to performance improvements

**Recommendation**: Conservative - the bug fix is important and should be tested independently.

## Success Metrics

After v0.3.0 release:
- [ ] PyPI download stats show wheel adoption (vs sdist)
- [ ] No new issues related to Rust backend
- [ ] Performance improvements confirmed in real-world usage
- [ ] Positive community feedback

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Wheel build failures | Test builds before tagging release |
| Platform-specific bugs | Cross-validation runs on all platforms in CI |
| Import failures | Automatic fallback to pure Python |
| Breaking changes | Comprehensive test suite + cross-validation |
| PyPI publishing issues | `skip-existing: true` in workflow prevents overwrites |

## Dependencies

**Build-time** (only for you as publisher):
- Rust toolchain (handled by GitHub Actions)
- maturin (handled by PyO3/maturin-action)
- PyO3 (specified in rust-ext/Cargo.toml)

**Runtime** (for end users):
- NONE! Pre-compiled wheels have no dependencies

**Development**:
- Python 3.8+ for testing
- pytest for running tests
- maturin for local wheel building (optional)

## Timeline Estimate

| Task | Time Estimate |
|------|---------------|
| Fix Python bug | 1 hour |
| Test bug fix | 1 hour |
| Implement hybrid backend | 2 hours |
| Test wheel building workflow | 2 hours |
| Documentation updates | 2 hours |
| Release v0.2.2 | 1 hour |
| Monitor + iterate | 1 week |
| Release v0.3.0 | 1 hour |
| **Total** | ~2 weeks |

## Conclusion

The Rust backend integration is **low-risk, high-reward**:
- **5.71x performance improvement** for most users
- **Zero installation complexity** (pre-built wheels)
- **Automatic fallback** for edge cases
- **No breaking changes** to API
- **Well-tested** (97.4% cross-validation compatibility)

The main work is setting up CI infrastructure, which has been designed and is ready to deploy.

**Recommendation**: Proceed with integration following the conservative rollout plan.
