# NSV Lift Operation Examples

This directory contains concrete examples of the `lift` operation, demonstrating how it encodes a **flat sequence of lines** as a single NSV row.

## Key Concept

**`lift`** takes a sequence of strings (e.g., all lines from an NSV file) and encodes them as cells of a single row.

The inverse **`unlift`** extracts those strings back, allowing you to reconstruct the original structure.

## Example 1: Lifting a 2D NSV File

### Stage 0: Original 2D Data (3 rows)
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

This represents: `[["a", "b", "c"], ["d", "e", "f"], ["", "g", ""]]`

**Flat sequence of lines:** `['a', 'b', 'c', '', 'd', 'e', 'f', '', '\\', 'g', '\\', '']` (12 lines)

Notice the empty strings (`''`) marking row boundaries, and `'\\'` representing empty cells.

### Stage 1: After Lift (1 row, 1 cell)
**File:** `2_after_lift.nsv` (49 bytes)

```
a\nb\nc\n\\\nd\ne\nf\n\\\n\\\\\ng\n\\\\\n\\\n\n

```

The entire flat sequence is now encoded in a **single cell**. When you load this NSV file, you get:
- 1 row with 1 cell
- Cell contains: `"a\nb\nc\n\\\nd\ne\nf\n\\\n\\\\\ng\n\\\\\n\\\n\n"`

**Key observation:**
- Line `''` (empty) → encoded as `\\\` (backslash becomes `\\`, then `\` for empty)
- Line `'\\'` (backslash char) → encoded as `\\\\\\` (four backslashes!)

### Stage 2: After Double Lift (1 row, 1 cell)
**File:** `3_after_double_lift.nsv` (138 bytes)

```
a\\\\nb\\\\nc\\\\n\\\\\\\\\\\\nd\\\\ne\\\\nf\\\\n\\\\\\\\\\\\n\\\\\\\\\\\\\\\\\\\\ng\\\\n\\\\\\\\\\\\\\\\\\\\n\\\\\\\\\\\\n\\\\n\n\\\n\n

```

We lifted the *lifted file itself*. The flat sequence from `2_after_lift.nsv` was:
- `['a\\nb\\nc\\n...', '']` (the cell content + row terminator)

Now **that** sequence is encoded as one cell with exponentially growing escapes.

**Recovery:** `unlift → parse → unlift → parse` gets back the original 3 rows.

## Example 2: Combining Multiple NSV Files (3D)

### Original: Two 2×2 Matrices
**Files:** `3d_matrix_0.nsv`, `3d_matrix_1.nsv` (10 bytes each)

Matrix 0:
```
a
b

c
d

```
Represents: `[["a", "b"], ["c", "d"]]`

Matrix 1 (similar): `[["e", "f"], ["g", "h"]]`

### After Lifting Each Matrix
Each matrix file's flat sequence is lifted to create one cell:
- Matrix 0 → cell: `"a\nb\n\\\nc\nd\n\\\n\n"`
- Matrix 1 → cell: `"e\nf\n\\\ng\nh\n\\\n\n"`

### Combined File (2 cells in 1 row)
**File:** `3d_combined.nsv` (47 bytes)

```
a\nb\n\\\nc\nd\n\\\n\n
e\nf\n\\\ng\nh\n\\\n\n

```

Two lifted matrices stored as two cells in one row!

### Triple Lift (1 cell)
**File:** `3d_triple_lift.nsv` (122 bytes)

```
a\\\\nb\\\\n\\\\\\\\\\\\nc\\\\nd\\\\n\\\\\\\\\\\\n\\\\n\ne\\\\nf\\\\n\\\\\\\\\\\\ng\\\\nh\\\\n\\\\\\\\\\\\n\\\\n\n\\\n\n

```

The entire combined file is lifted again, encoding **both 2×2 matrices in a single cell**.

**Recovery:** `unlift → parse → unlift each cell → parse each` recovers both original matrices.

## Summary

| File | Structure | Size | Escaping Level |
|------|-----------|------|----------------|
| `1_original_2d.nsv` | 3 rows × 3 cells | 21 B | Original |
| `2_after_lift.nsv` | 1 row × 1 cell | 49 B | Single lift (2×) |
| `3_after_double_lift.nsv` | 1 row × 1 cell | 138 B | Double lift (4×) |
| `3d_combined.nsv` | 1 row × 2 cells | 47 B | Single lift |
| `3d_triple_lift.nsv` | 1 row × 1 cell | 122 B | Triple lift |

**Key Properties:**
1. ✓ Perfect round-trip: `unlift(lift(x)) = x`
2. ✓ Every intermediate file is valid NSV
3. ✓ Escapes grow exponentially (but predictably)
4. ✓ Enables arbitrary nesting depth

## Running the Demo

```bash
PYTHONPATH=. python examples/demonstrate_lift.py
```

This regenerates all example files and verifies round-trip properties.
