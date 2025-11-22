#!/usr/bin/env python3
import nsv

# Example 1: Basic lift (2D → 1D)
print("="*70)
print("Example 1: Basic 2D → 1D")
print("="*70)

data_2d = [["a", "b"], ["c", "d"]]
nsv_2d = nsv.dumps(data_2d)
print(f"Original 2D: {data_2d}")
print(f"NSV: {repr(nsv_2d)}\n")

lifted = nsv.lift(nsv_2d)
parsed = nsv.loads(lifted)
print(f"After lift: {len(parsed)} row, {len(parsed[0])} cells")
print(f"Cells: {parsed[0]}\n")

recovered = nsv.loads(nsv.unlift(lifted))
print(f"After unlift: {recovered}")
print(f"✓ Round-trip: {recovered == data_2d}\n")

# Example 2: 3D array (list of 2D matrices)
print("="*70)
print("Example 2: Encode/decode 3D array")
print("="*70)

# Two 2D matrices (this is our 3D array: 2 matrices of 2×2)
matrix_0 = [["a", "b"], ["c", "d"]]
matrix_1 = [["e", "f"], ["g", "h"]]
data_3d = [matrix_0, matrix_1]

print(f"Original 3D array (2 matrices):")
print(f"  Matrix 0: {matrix_0}")
print(f"  Matrix 1: {matrix_1}\n")

# Encode each 2D matrix as NSV
nsv_m0 = nsv.dumps(matrix_0)
nsv_m1 = nsv.dumps(matrix_1)

# Lift each matrix (2D → 1D)
lifted_m0 = nsv.lift(nsv_m0)
lifted_m1 = nsv.lift(nsv_m1)

print(f"After lifting each matrix:")
print(f"  Matrix 0: {len(nsv.loads(lifted_m0)[0])} cells")
print(f"  Matrix 1: {len(nsv.loads(lifted_m1)[0])} cells\n")

# Store both lifted matrices as cells in one NSV row
combined = nsv.dumps([[lifted_m0, lifted_m1]])
print(f"Combined NSV: 1 row, {len(nsv.loads(combined)[0])} cells\n")

# Decode: extract cells and unlift each
cells = nsv.loads(combined)[0]
recovered_0 = nsv.loads(nsv.unlift(cells[0]))
recovered_1 = nsv.loads(nsv.unlift(cells[1]))

print(f"Recovered 3D array:")
print(f"  Matrix 0: {recovered_0}")
print(f"  Matrix 1: {recovered_1}")
print(f"\n✓ Round-trip: {[recovered_0, recovered_1] == data_3d}")
