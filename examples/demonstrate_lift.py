#!/usr/bin/env python3
import nsv

matrices = [
    [["a", "b"], ["c", "d"]],
    [["e", "f"], ["g", "h"]],
]

print("="*70)
print("3D Array Encoding")
print("="*70)
print("\nOriginal 3D array (2 matrices):")
for i, m in enumerate(matrices):
    print(f"  {m}")

# Step 1: Each matrix as NSV (2D)
print("\n" + "="*70)
print("Step 1: Each matrix as NSV file")
print("="*70)

for i, m in enumerate(matrices):
    nsv_str = nsv.dumps(m)
    with open(f'examples/matrix_{i}.nsv', 'w') as f:
        f.write(nsv_str)
    print(f"\nmatrix_{i}.nsv ({len(nsv_str)} bytes):")
    print(nsv_str)

# Step 2: Lift each matrix (2D → 1D)
print("="*70)
print("Step 2: Lift each matrix (2D → 1D)")
print("="*70)

lifted = []
for i, m in enumerate(matrices):
    nsv_str = nsv.dumps(m)
    lifted_str = nsv.lift(nsv_str)
    lifted.append(lifted_str)
    with open(f'examples/matrix_{i}_lifted.nsv', 'w') as f:
        f.write(lifted_str)
    print(f"\nmatrix_{i}_lifted.nsv ({len(lifted_str)} bytes):")
    print(lifted_str)
    parsed = nsv.loads(lifted_str)
    print(f"Structure: {len(parsed)} row, {len(parsed[0])} cells")

# Step 3: Combine as 2D NSV
print("="*70)
print("Step 3: Combine as 2D NSV (2 rows)")
print("="*70)

combined_2d = nsv.dumps([nsv.loads(l)[0] for l in lifted])
with open('examples/combined_2d.nsv', 'w') as f:
    f.write(combined_2d)

print(f"\ncombined_2d.nsv ({len(combined_2d)} bytes):")
print(combined_2d)
print(f"Structure: {len(nsv.loads(combined_2d))} rows")

# Step 4: Lift to 1D
print("="*70)
print("Step 4: Lift to 1D (everything in one row)")
print("="*70)

final = nsv.lift(combined_2d)
with open('examples/final_1d.nsv', 'w') as f:
    f.write(final)

print(f"\nfinal_1d.nsv ({len(final)} bytes):")
print(final)
parsed = nsv.loads(final)
print(f"Structure: {len(parsed)} row, {len(parsed[0])} cells")

# Decode
print("\n" + "="*70)
print("Decoding back to 3D")
print("="*70)

rows = nsv.loads(nsv.unlift(final))
recovered = [nsv.loads('\n'.join(row) + '\n\n') for row in rows]  # Need row terminator

print(f"\nRecovered: {recovered}")
print(f"Match: {recovered == matrices}")
