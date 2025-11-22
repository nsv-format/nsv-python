# Lift Operation

`lift: str → str` - collapses one dimension by encoding all lines as cells of a single row.

## Example

```python
import nsv

# 2D data: 3 rows
original = [["a", "b", "c"], ["d", "e", "f"], ["", "g", ""]]
nsv_str = nsv.dumps(original)  # "a\nb\nc\n\nd\ne\nf\n\n\\\ng\n\\\n\n"

# Lift: 2D → 1D
lifted = nsv.lift(nsv_str)     # "a\nb\nc\n\\\nd\ne\nf\n\\\n\\\\\ng\n\\\\\n\\\n\n"

# Result: 1 row, 12 cells
# ['a', 'b', 'c', '', 'd', 'e', 'f', '', '\\', 'g', '\\', '']

# Unlift: 1D → 2D
unlifted = nsv.unlift(lifted)
recovered = nsv.loads(unlifted)  # Original 3 rows recovered
```

**Key:** Lines → cells, row delimiters → empty cells, `\` → literal `\\`
