# 3D Array Encoding with Lift

Shows how to encode a 3D array (list of 2D matrices) using repeated lift operations.

## Process

```python
matrices = [[["a", "b"], ["c", "d"]], [["e", "f"], ["g", "h"]]]

# 1. Encode each 2D matrix as NSV
nsv_files = [nsv.dumps(m) for m in matrices]

# 2. Lift each (2D → 1D)  
lifted = [nsv.lift(f) for f in nsv_files]

# 3. Combine as 2D NSV (2 rows with 6 cells each)
combined = nsv.dumps([nsv.loads(l)[0] for l in lifted])

# 4. Lift again (2D → 1D, everything in one row)
final = nsv.lift(combined)  # 1 row, 14 cells

# Decode
rows = nsv.loads(nsv.unlift(final))  # 2 rows
recovered = [nsv.loads('\n'.join(row) + '\n') for row in rows]
```

Each lift collapses one dimension: 3D → 2D → 1D
