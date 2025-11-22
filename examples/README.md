# NSV Lift Operation Examples

This directory contains concrete examples of the `lift` operation applied to NSV data, showing how data transforms at each stage.

## 2D Example: Progressive Lifting

### Stage 0: Original 2D Data
**File:** `1_original_2d.nsv`

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

This is a standard NSV file with 3 rows:
- Row 0: `["a", "b", "c"]`
- Row 1: `["d", "e", "f"]`
- Row 2: `["", "g", ""]` (note the empty cells encoded as `\`)

### Stage 1: After First Lift (3 cells in 1 row)
**File:** `2_after_first_lift.nsv`

```
a\nb\nc\n\n
d\ne\nf\n\n
\\\ng\n\\\n\n

```

Each original row has been "lifted" into a single cell:
- Cell 0: `"a\nb\nc\n\n"` (the literal characters, not actual newlines!)
- Cell 1: `"d\ne\nf\n\n"`
- Cell 2: `"\\\ng\n\\\n\n"`

Notice how:
- Newlines are escaped as `\n`
- Empty cells (`\`) are escaped as `\\\` (backslash becomes `\\`, then the `\` for empty)

### Stage 2: After Second Lift (1 cell in 1 row)
**File:** `3_after_second_lift.nsv`

```
a\\nb\\nc\\n\\n\nd\\ne\\nf\\n\\n\n\\\\\\ng\\n\\\\\\n\\n\n\n

```

The entire structure is now a single cell. Notice the **exponential escape growth**:
- Original `\n` → `\\n` (escaped once)
- That `\\n` → `\\\\n` (escaped again!)
- Original `\` → `\\` → `\\\\` → `\\\\\\` (empty cell marker, double-escaped)

**Character count:** 61 bytes (from original 21 bytes)

## 3D Example: Two Matrices

### Original Matrices
**Files:** `3d_matrix_0.nsv`, `3d_matrix_1.nsv`

Matrix 0:
```
a
b

c
d

```
Represents: `[["a", "b"], ["c", "d"]]`

Matrix 1 (similar structure): `[["e", "f"], ["g", "h"]]`

### After First Lift (per matrix)
**Files:** `3d_matrix_0_lift1.nsv`, `3d_matrix_1_lift1.nsv`

Matrix 0 after lifting each row:
```
a\nb\n\n
c\nd\n\n

```

Now it's 2 cells in 1 row, where each cell represents a lifted row.

### After Second Lift (all matrices in one row)
**File:** `3d_all_matrices_lift2.nsv`

```
a\\nb\\n\\n\nc\\nd\\n\\n\n\n
e\\nf\\n\\n\ng\\nh\\n\\n\n\n

```

Two cells, one row. Each cell is a fully lifted matrix.

### After Third Lift (single cell)
**File:** `3d_all_matrices_lift3.nsv`

```
a\\\\nb\\\\n\\\\n\\nc\\\\nd\\\\n\\\\n\\n\\n\ne\\\\nf\\\\n\\\\n\\ng\\\\nh\\\\n\\\\n\\n\\n\n\n

```

The entire 3D structure encoded as **one cell in one row**.

**Character count:** 94 bytes (from original 10 bytes per matrix)

## Key Observations

1. **Valid NSV at every stage**: Each intermediate file is a valid NSV document
2. **Exponential growth**: Escapes double at each lift level
3. **Perfect round-trip**: `unlift(unlift(...(lift(lift(...)))))` always recovers the original
4. **Fractal structure**: The same encoding rules apply at every nesting level

## Running the Demo

```bash
PYTHONPATH=/home/user/nsv-python python examples/demonstrate_lift.py
```

This will regenerate all example files and verify round-trip properties.
