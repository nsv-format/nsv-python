#!/usr/bin/env python3
"""Demonstrate the lift operation with actual NSV files at each stage."""

import nsv

def main():
    # Original 2D data (3 rows, varying cells)
    original_2d = [
        ["a", "b", "c"],
        ["d", "e", "f"],
        ["", "g", ""]
    ]

    print("="*70)
    print("STEP 0: Original 2D data (3 rows)")
    print("="*70)
    print("Python representation:")
    for i, row in enumerate(original_2d):
        print(f"  Row {i}: {row}")
    print()

    # Write as NSV
    nsv_string = nsv.dumps(original_2d)
    with open('examples/1_original_2d.nsv', 'w') as f:
        f.write(nsv_string)

    print("NSV file (examples/1_original_2d.nsv):")
    print(repr(nsv_string))
    print("\nVisual:")
    print(nsv_string)

    print("="*70)
    print("STEP 1: After lift (2D → 1D)")
    print("="*70)

    # Lift: takes NSV string, returns NSV string with one row
    lifted = nsv.lift(nsv_string)

    with open('examples/2_after_lift.nsv', 'w') as f:
        f.write(lifted)

    print("NSV file (examples/2_after_lift.nsv):")
    print(repr(lifted))
    print("\nVisual:")
    print(lifted)

    parsed_lifted = nsv.loads(lifted)
    print(f"Structure: {len(parsed_lifted)} row(s), {len(parsed_lifted[0])} cell(s)")
    print(f"Cells: {parsed_lifted[0]}")
    print()

    print("="*70)
    print("VERIFICATION: Unlift to recover original")
    print("="*70)

    unlifted = nsv.unlift(lifted)
    print(f"After unlift: {repr(unlifted)}")
    print()

    recovered_2d = nsv.loads(unlifted)
    print("Recovered data:")
    for i, row in enumerate(recovered_2d):
        print(f"  Row {i}: {row}")
    print()

    if recovered_2d == original_2d:
        print("✓ SUCCESS: Recovered data matches original!")
    else:
        print("✗ FAILED: Data mismatch!")

    print("\n" + "="*70)
    print("STEP 2: Double lift (1D → 0D)")
    print("="*70)

    # Lift the already-lifted NSV
    double_lifted = nsv.lift(lifted)

    with open('examples/3_after_double_lift.nsv', 'w') as f:
        f.write(double_lifted)

    print(f"Double-lifted string length: {len(double_lifted)} chars")
    print(f"Preview: {repr(double_lifted[:80])}...")
    print()

    parsed = nsv.loads(double_lifted)
    print(f"Structure: {len(parsed)} row(s), {len(parsed[0])} cell(s)")
    print()

    # Double unlift
    first_unlift = nsv.unlift(double_lifted)
    second_unlift = nsv.unlift(first_unlift)

    if second_unlift == nsv_string:
        print("✓ SUCCESS: Double round-trip worked!")
    else:
        print("✗ FAILED: Double round-trip failed!")

    print("\n" + "="*70)
    print("3D EXAMPLE: Multiple NSV files → Combined")
    print("="*70)

    # Two separate 2D matrices
    matrix_0 = [["a", "b"], ["c", "d"]]
    matrix_1 = [["e", "f"], ["g", "h"]]

    print("Matrix 0:", matrix_0)
    print("Matrix 1:", matrix_1)
    print()

    # Save each as NSV
    nsv_0 = nsv.dumps(matrix_0)
    nsv_1 = nsv.dumps(matrix_1)

    with open('examples/3d_matrix_0.nsv', 'w') as f:
        f.write(nsv_0)
    with open('examples/3d_matrix_1.nsv', 'w') as f:
        f.write(nsv_1)

    # Lift each NSV file
    lifted_0 = nsv.lift(nsv_0)
    lifted_1 = nsv.lift(nsv_1)

    print(f"Lifted matrix 0: {repr(lifted_0)}")
    print(f"Lifted matrix 1: {repr(lifted_1)}")
    print()

    # Combine: store both lifted strings as cells in one row
    combined = nsv.dumps([[lifted_0, lifted_1]])

    with open('examples/3d_combined.nsv', 'w') as f:
        f.write(combined)

    print("Saved combined to examples/3d_combined.nsv")
    parsed = nsv.loads(combined)
    print(f"Structure: {len(parsed)} row(s), {len(parsed[0])} cell(s)")
    print()

    # Lift the combined file
    triple_lifted = nsv.lift(combined)

    with open('examples/3d_triple_lift.nsv', 'w') as f:
        f.write(triple_lifted)

    print(f"Triple-lifted length: {len(triple_lifted)} chars")
    print("Saved to examples/3d_triple_lift.nsv")
    print()

    # Verify 3D round-trip: unlift 3 times
    u1 = nsv.unlift(triple_lifted)
    parsed_u1 = nsv.loads(u1)

    # Extract the two cells
    cell1 = parsed_u1[0][0]
    cell2 = parsed_u1[0][1]

    # Unlift each
    recovered_0 = nsv.unlift(cell1)
    recovered_1 = nsv.unlift(cell2)

    print("Recovered matrices:")
    print("  Matrix 0:", nsv.loads(recovered_0))
    print("  Matrix 1:", nsv.loads(recovered_1))
    print()

    if nsv.loads(recovered_0) == matrix_0 and nsv.loads(recovered_1) == matrix_1:
        print("✓ SUCCESS: 3D round-trip worked!")
    else:
        print("✗ FAILED: 3D round-trip failed!")

if __name__ == "__main__":
    main()
