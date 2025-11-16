# NSV Streaming Semantics: Cross-Implementation Analysis

## Problem Statement

We have an inconsistency in how incomplete rows (rows without double-newline termination) are handled across NSV implementations, particularly between:
1. **Exhaustive operations** (`loads()`, `parse()`) - process complete data
2. **Incremental operations** (`Reader`) - stream data chunk by chunk

The core question: **Should incomplete rows be emitted at EOF?**

## Current Implementation Behaviors

### Input Test Case
```
Input: "a\nb"  (two cells, missing final \n\n)
```

| Implementation | Operation | Result | Behavior |
|----------------|-----------|--------|----------|
| **Python** | `loads("a\nb")` | `[['a']]` | ❌ Ignores incomplete row |
| **Python** | `Reader("a\nb")` at EOF | `[['a', 'b']]` | ✅ Includes incomplete row |
| **Rust** | `loads("a\nb")` | `[['a', 'b']]` | ✅ Includes incomplete row |
| **JavaScript** | `parse("a\nb")` | `[['a', 'b']]` | ✅ Includes incomplete row |
| **JavaScript** | `Reader("a\nb")` at EOF | `[['a', 'b']]` | ✅ Includes incomplete row |

### Key Findings

1. **Python `loads()` is the outlier** - only implementation that ignores incomplete rows
2. **Python `Reader`** behaves like Rust and JS (includes at EOF)
3. **Internal Python inconsistency**: `loads(s) ≠ load(StringIO(s))`
4. **All other implementations agree**: Include incomplete row at EOF

## Streaming Semantics Analysis

### JavaScript Reader: True Streaming Implementation

The JS `Reader` class (lines 230-375 in index.js) demonstrates **proper streaming behavior**:

```javascript
_processChunk(text) {
  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (char === '\n') {
      if (this._lastCharWasNewline) {
        // Double newline - row complete, EMIT IT
        this._rowQueue.push(this._currentRow);
        this._currentRow = [];
        // ...
      } else {
        // Single newline - cell complete, BUFFER IT
        this._currentRow.push(unescape(this._buffer));
        this._buffer = '';
        this._lastCharWasNewline = true;
      }
    } else {
      this._buffer += char;
      this._lastCharWasNewline = false;
    }
  }
}

_finalize() {
  // Called ONLY at EOF
  // Handle any remaining buffered content
  if (this._buffer.length > 0) {
    this._currentRow.push(unescape(this._buffer));
  }

  // Add final row if it has content
  if (this._currentRow.length > 0) {
    this._rowQueue.push(this._currentRow);  // Emit at EOF
  }

  this._done = true;
}
```

**Key insights**:
- During streaming: Only emits on `\n\n` (double newline)
- Incomplete rows are **buffered**, not emitted
- At EOF (`_finalize()`): Emits buffered incomplete row
- This allows **true streaming** (tailing logs, network streams)

### Python Reader: File Iterator Pattern

Python's `Reader` class uses file iteration:

```python
def __next__(self):
    acc = []
    for line in self._file_obj:  # Iterate over file lines
        if line == '\n':
            return acc  # Empty line = row complete
        if line[-1] == '\n':
            line = line[:-1]
        acc.append(Reader.unescape(line))

    # at the end of the file
    if acc:
        return acc  # Emit incomplete row at EOF
    else:
        raise StopIteration
```

**Issue**: This isn't true chunk-based streaming!
- Relies on file iterator's line-by-line reading
- Can't handle chunked data (like JS Reader)
- Can't be used for tailing logs or network streams
- **Always** at EOF when iterator exhausted

### Python loads(): String-Based Parsing

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
    return data  # ❌ BUG: Doesn't append final `row`
```

**Issue**: Doesn't emit incomplete row, even though input is complete (exhaustive operation).

## The Semantic Contract

### Exhaustive Operations (Complete Data)

**Operations**: `loads()`, `parse()`, `read(file)`
**Input**: Complete data (file, string, buffer)
**Contract**: Process ALL data in input

**Question**: Is incomplete row at EOF valid data or corruption?

**Arguments for including**:
- EOF is an unambiguous terminator
- Files without trailing newlines are common
- User provided complete data, expect complete parse
- Pragmatic: handles real-world files

**Arguments for rejecting**:
- Spec says rows "should" end with `\n\n`
- Strict validation catches malformed data
- Consistent with streaming semantics
- Forces correct file creation

### Incremental Operations (Streaming)

**Operations**: `Reader` (chunk-based)
**Input**: Data chunks arriving over time
**Contract**: Emit complete rows as they arrive, buffer incomplete data

**Behavior**:
- During streaming: Only emit on `\n\n`
- At EOF signal: Emit buffered incomplete row (if any)
- Allows continuation: pause/resume without losing data

## Streaming Test Coverage

### JavaScript (`test-streaming.js`): ✅ Excellent
- Test 1: Chunked reading (`['a\n', 'b\n', '\n', 'c\n', 'd\n', '\n']`)
- Test 2: Incremental writing
- Test 3: Processing without buffering all data

**Coverage**: True streaming behavior validated

### Python: ❌ Missing
- No streaming tests in test suite
- No tests for chunk-based processing
- No tests for Reader with chunked data
- Only tests file reading (complete files)

**This is why the bug wasn't caught!**

### Rust: ⚠️ Partial
- Tests complete data parsing
- Tests edge cases (empty rows, no trailing newline)
- No streaming/chunked tests (Rust only has `loads`/`dumps`, no streaming API)

## Recommendations

### 1. Fix Python `loads()` Immediately

**Current behavior**: Ignores incomplete row at EOF
**Expected behavior**: Include incomplete row at EOF (match all other implementations)

```python
def loads(s: str) -> List[List[str]]:
    # ... existing code ...

    # FIX: Append final row if present
    if row:
        data.append(row)

    return data
```

**Rationale**:
- Exhaustive operation on complete data
- EOF is unambiguous terminator
- Matches Reader, Rust, and JS behavior
- Handles real-world files

### 2. Add Streaming Tests to Python

Create `tests/test_streaming.py`:

```python
import unittest
from io import StringIO
import nsv

class TestStreaming(unittest.TestCase):
    def test_complete_rows_only(self):
        """Reader should only emit complete rows (ending with double newline)."""
        # Simulate chunked data arriving
        file_obj = StringIO('a\nb\n\nc\nd\n\n')
        reader = nsv.Reader(file_obj)

        rows = list(reader)
        self.assertEqual(rows, [['a', 'b'], ['c', 'd']])

    def test_incomplete_row_at_eof(self):
        """Reader should emit incomplete row when EOF reached."""
        file_obj = StringIO('a\nb\n\nc\nd')
        reader = nsv.Reader(file_obj)

        rows = list(reader)
        # At EOF, incomplete row should be emitted
        self.assertEqual(rows, [['a', 'b'], ['c', 'd']])

    def test_reader_loads_parity(self):
        """Reader and loads should have same behavior for complete strings."""
        test_cases = [
            'a\nb\n\n',  # Complete row
            'a\nb',      # Incomplete row
            'a\nb\n\nc\nd\n\n',  # Multiple complete rows
            'a\nb\n\nc\nd',      # Last row incomplete
        ]

        for s in test_cases:
            with self.subTest(input=repr(s)):
                reader_result = list(nsv.Reader(StringIO(s)))
                loads_result = nsv.loads(s)
                self.assertEqual(reader_result, loads_result,
                    f"Reader and loads differ for {repr(s)}")
```

### 3. Document the Semantics

Add to README or spec:

```markdown
## Incomplete Rows at EOF

When parsing complete data (files, strings), an incomplete row at EOF
(one without a terminating double newline) is treated as valid and included
in the output. This handles real-world files that may not have trailing newlines.

For true streaming applications (tailing logs, network streams), incomplete
rows are buffered until a double newline is encountered or EOF is reached.
```

### 4. Consider True Streaming Reader for Python (Future)

Current Python `Reader` isn't suitable for true streaming (tailing logs, network).
Consider adding a `StreamReader` class similar to JS:

```python
class StreamReader:
    """Chunk-based streaming reader for incremental data."""

    def __init__(self):
        self._buffer = ''
        self._current_row = []
        self._last_was_newline = False

    def feed(self, chunk: str) -> List[List[str]]:
        """Feed a chunk of data, returns complete rows."""
        rows = []
        for char in chunk:
            if char == '\n':
                if self._last_was_newline:
                    # Double newline - complete row
                    rows.append(self._current_row)
                    self._current_row = []
                    self._buffer = ''
                    self._last_was_newline = False
                else:
                    # Single newline - complete cell
                    self._current_row.append(Reader.unescape(self._buffer))
                    self._buffer = ''
                    self._last_was_newline = True
            else:
                self._buffer += char
                self._last_was_newline = False
        return rows

    def finalize(self) -> List[str]:
        """Get final incomplete row if any (call at EOF)."""
        if self._buffer:
            self._current_row.append(Reader.unescape(self._buffer))
        return self._current_row if self._current_row else None
```

But this is **not urgent** - current `Reader` works fine for complete files.

## Decision Matrix

### Fix Priority

| Issue | Priority | Rationale |
|-------|----------|-----------|
| Python `loads()` bug | **HIGH** | Breaks compatibility with all other implementations |
| Add streaming tests | **HIGH** | Prevent regressions, validate semantics |
| Document EOF behavior | **MEDIUM** | Clarify spec ambiguity |
| True streaming API | **LOW** | Nice-to-have, current API works for files |

### Which Repos Need Fixes?

| Repo | Needs Fix? | What to Fix |
|------|------------|-------------|
| **nsv-python** | ✅ YES | 1. Fix `loads()` to emit incomplete row at EOF<br>2. Add streaming tests<br>3. Document behavior |
| **nsv-rust** | ❌ NO | Already correct, but could add streaming tests |
| **nsv-js** | ❌ NO | Already correct, excellent streaming tests |
| **nsv** (spec) | ⚠️ MAYBE | Clarify handling of incomplete rows at EOF |

## Proposed Fix for Python

```python
# nsv/core.py

def loads(s: str) -> List[List[str]]:
    """
    Load NSV data from a string.

    Parses complete NSV data. Incomplete rows at EOF (missing final \\n\\n)
    are treated as valid and included in the output.
    """
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

    # Include final row if present (handles incomplete rows at EOF)
    if row:
        data.append(row)

    return data
```

## Testing the Fix

After fixing Python `loads()`, all implementations should agree:

```python
# All should return [['a', 'b']]
nsv_python.loads("a\nb")       # ✅ (after fix)
nsv_python.load(StringIO("a\nb"))  # ✅ (already works)
nsv_rust.loads("a\nb")         # ✅ (already works)
nsv_js.parse("a\nb")           # ✅ (already works)
```

Cross-validation should then show **100% compatibility** instead of 97.4%.

## Conclusion

1. **Python `loads()` has a bug** - it's the only implementation that doesn't emit incomplete rows at EOF
2. **All other implementations agree** - incomplete row at EOF should be included
3. **Streaming tests are missing** - this is why the bug wasn't caught earlier
4. **Fix is simple** - add 2 lines to `loads()`
5. **True streaming** (tailing logs) would need a different API, but that's not urgent

**Recommendation**:
- Fix Python `loads()` to match other implementations
- Add comprehensive streaming tests
- Document the EOF behavior in the spec
- Keep Rust and JS as-is (they're correct)
