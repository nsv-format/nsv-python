# Lift Operation Examples

`lift: str → str` - collapses one dimension by encoding all lines as cells of a single row.

## Example 1: Basic 2D → 1D

```python
data_2d = [["a", "b"], ["c", "d"]]
nsv_2d = nsv.dumps(data_2d)          # 2D: 2 rows

lifted = nsv.lift(nsv_2d)            # 1D: 1 row, 6 cells
# Cells: ['a', 'b', '', 'c', 'd', '']

recovered = nsv.loads(nsv.unlift(lifted))  # Back to 2D
```

## Example 2: Encoding 3D Arrays

A 3D array is a list of 2D matrices. We can encode it using lift:

```python
# 3D array: 2 matrices of 2×2
matrix_0 = [["a", "b"], ["c", "d"]]
matrix_1 = [["e", "f"], ["g", "h"]]

# Encode each matrix as NSV, then lift
lifted_0 = nsv.lift(nsv.dumps(matrix_0))
lifted_1 = nsv.lift(nsv.dumps(matrix_1))

# Store both as cells in one row
combined = nsv.dumps([[lifted_0, lifted_1]])

# Decode: extract and unlift each cell
cells = nsv.loads(combined)[0]
recovered_0 = nsv.loads(nsv.unlift(cells[0]))
recovered_1 = nsv.loads(nsv.unlift(cells[1]))
```

This is how ENSV metadata works: a `.nsvs` file is lifted and stored as row 0.
