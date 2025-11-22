# NSV Lift Operation Examples

Demonstrates `lift: str → str` - collapses one dimension by encoding all lines as cells of a single row.

## Example 1: 2D → 1D

### Original (3 rows)
**File:** `1_original_2d.nsv` (21 bytes)

```
a
b
c

d
e
f

\
g
\

```

Data: `[["a", "b", "c"], ["d", "e", "f"], ["", "g", ""]]`

### After `lift()` (1 row, 12 cells)
**File:** `2_after_lift.nsv` (30 bytes)

```
a
b
c
\
d
e
f
\
\\
g
\\
\

```

Data: `[["a", "b", "c", "", "d", "e", "f", "", "\\", "g", "\\", ""]]`

Each line from the original became a cell. Empty lines (row delimiters) became empty cells `""`, and the `\` (empty cell marker) became literal `\\`.

### After `unlift()` → Original recovered ✓

## Example 2: 1D → "0D" (still 1 row, more cells)

**File:** `3_after_double_lift.nsv` (36 bytes)

Lifting the already-lifted file takes its 13 lines (12 cells + row terminator) and makes them cells.

Result: 1 row, 13 cells

## Example 3: Combining Multiple Files

Two 2×2 matrices:
- `3d_matrix_0.nsv` → `lift()` → 1 row, 6 cells
- `3d_matrix_1.nsv` → `lift()` → 1 row, 6 cells

Store both lifted strings as cells: `3d_combined.nsv` (1 row, 2 cells)

Lift again: `3d_triple_lift.nsv` (1 row, 3 cells)

Each cell can be `unlift()`ed to recover the original matrix.

## Key Points

- **`lift(nsv_string) → nsv_string`** - string in, string out
- Collapses exactly **one dimension** per call
- Lines become cells; row delimiters become empty cells
- Perfect round-trip: `unlift(lift(x)) == x`
