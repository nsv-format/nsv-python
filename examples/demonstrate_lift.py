#!/usr/bin/env python3
import nsv

original = [["a", "b", "c"], ["d", "e", "f"], ["", "g", ""]]

print("Original (3 rows):")
for row in original:
    print(f"  {row}")

nsv_str = nsv.dumps(original)
print(f"\nNSV string ({len(nsv_str)} bytes):\n{repr(nsv_str)}\n")

lifted = nsv.lift(nsv_str)
print(f"After lift ({len(lifted)} bytes):\n{repr(lifted)}\n")

parsed = nsv.loads(lifted)
print(f"Parsed: {len(parsed)} row, {len(parsed[0])} cells")
print(f"Cells: {parsed[0]}\n")

unlifted = nsv.unlift(lifted)
recovered = nsv.loads(unlifted)

print("After unlift:")
for row in recovered:
    print(f"  {row}")

print(f"\n✓ Round-trip: {recovered == original}")
