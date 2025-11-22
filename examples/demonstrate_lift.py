#!/usr/bin/env python3
import nsv

matrices = [
    [["a", "b"], ["c", "d"]],
    [["e", "f"], ["g", "h"]],
]

print("Original 3D array:")
for i, m in enumerate(matrices):
    print(f"  Matrix {i}: {m}")

# Encode each matrix as NSV
nsv_files = [nsv.dumps(m) for m in matrices]

# Lift each (2D → 1D)
lifted = [nsv.lift(f) for f in nsv_files]

# Combine as 2D NSV (2 rows, each with 6 cells)
combined_2d = nsv.dumps([nsv.loads(l)[0] for l in lifted])
print(f"\nCombined: {len(nsv.loads(combined_2d))} rows")

# Lift again (2D → 1D)
final = nsv.lift(combined_2d)
print(f"Final: {len(nsv.loads(final))} row, {len(nsv.loads(final)[0])} cells\n")

# Decode: unlift → rows → reconstruct NSV from each row → parse
rows = nsv.loads(nsv.unlift(final))
recovered = [nsv.loads('\n'.join(row) + '\n') for row in rows]

print("Recovered:")
for i, m in enumerate(recovered):
    print(f"  Matrix {i}: {m}")

print(f"\n✓ {recovered == matrices}")
