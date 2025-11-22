#!/usr/bin/env python3
"""Demonstrate the lift operation with actual NSV files at each stage."""

import nsv

def main():
    # Original 2D data (3 rows, each with 3 cells)
    original_2d = [
        ["a", "b", "c"],
        ["d", "e", "f"],
        ["", "g", ""]
    ]

    print("="*70)
    print("STEP 0: Original 2D data")
    print("="*70)
    print("Python representation:")
    for i, row in enumerate(original_2d):
        print(f"  Row {i}: {row}")
    print()

    # Write as NSV
    with open('examples/1_original_2d.nsv', 'w') as f:
        nsv.dump(original_2d, f)

    print("NSV file (examples/1_original_2d.nsv):")
    with open('examples/1_original_2d.nsv', 'r') as f:
        content = f.read()
        print(repr(content))
        print()
        print("Visual:")
        print(content)

    print("\n" + "="*70)
    print("STEP 1: After first lift (each row becomes a single cell)")
    print("="*70)

    # First lift: each row becomes a cell
    after_first_lift = [nsv.lift(row) for row in original_2d]

    print("Python representation:")
    for i, cell in enumerate(after_first_lift):
        print(f"  Cell {i}: {repr(cell)}")
    print()

    # This is now 1D data (3 cells in a single row)
    with open('examples/2_after_first_lift.nsv', 'w') as f:
        nsv.dump([after_first_lift], f)

    print("NSV file (examples/2_after_first_lift.nsv):")
    with open('examples/2_after_first_lift.nsv', 'r') as f:
        content = f.read()
        print(repr(content))
        print()
        print("Visual:")
        print(content)

    print("\n" + "="*70)
    print("STEP 2: After second lift (entire structure becomes a single cell)")
    print("="*70)

    # Second lift: the list of cells becomes a single cell
    after_second_lift = nsv.lift(after_first_lift)

    print("Python representation:")
    print(f"  Single cell: {repr(after_second_lift)}")
    print()

    # This is now 0D data (1 cell in 1 row)
    with open('examples/3_after_second_lift.nsv', 'w') as f:
        nsv.dump([[after_second_lift]], f)

    print("NSV file (examples/3_after_second_lift.nsv):")
    with open('examples/3_after_second_lift.nsv', 'r') as f:
        content = f.read()
        print(repr(content))
        print()
        print("Visual:")
        print(content)

    print("\n" + "="*70)
    print("VERIFICATION: Unlift twice to recover original")
    print("="*70)

    # Read the fully lifted version
    with open('examples/3_after_second_lift.nsv', 'r') as f:
        loaded = nsv.load(f)

    print(f"Loaded from file: {loaded}")
    print(f"Extract single cell: {repr(loaded[0][0])}")
    print()

    # First unlift
    first_unlift = nsv.unlift(loaded[0][0])
    print("After first unlift:")
    for i, cell in enumerate(first_unlift):
        print(f"  Cell {i}: {repr(cell)}")
    print()

    # Second unlift
    recovered = [nsv.unlift(cell) for cell in first_unlift]
    print("After second unlift (fully recovered):")
    for i, row in enumerate(recovered):
        print(f"  Row {i}: {row}")
    print()

    if recovered == original_2d:
        print("✓ SUCCESS: Recovered data matches original!")
    else:
        print("✗ FAILED: Data mismatch!")
        print(f"  Original: {original_2d}")
        print(f"  Recovered: {recovered}")

    print("\n" + "="*70)
    print("BONUS: 3D example")
    print("="*70)

    # 3D data: 2 matrices, each 2x2
    data_3d = [
        [["a", "b"], ["c", "d"]],    # First matrix
        [["e", "f"], ["g", "h"]],    # Second matrix
    ]

    print("Original 3D data:")
    for i, matrix in enumerate(data_3d):
        print(f"  Matrix {i}: {matrix}")
    print()

    # Save original as separate NSV files
    for i, matrix in enumerate(data_3d):
        with open(f'examples/3d_matrix_{i}.nsv', 'w') as f:
            nsv.dump(matrix, f)

    # First lift: each row in each matrix
    data_after_lift_1 = [[nsv.lift(row) for row in matrix] for matrix in data_3d]

    print("After lifting each row in each matrix:")
    for i, matrix in enumerate(data_after_lift_1):
        print(f"  Matrix {i}: {matrix}")
        with open(f'examples/3d_matrix_{i}_lift1.nsv', 'w') as f:
            nsv.dump([matrix], f)
    print()

    # Second lift: each matrix becomes a single cell
    data_after_lift_2 = [nsv.lift(matrix) for matrix in data_after_lift_1]

    print("After lifting each matrix to a single cell:")
    for i, cell in enumerate(data_after_lift_2):
        print(f"  Cell {i}: {repr(cell)[:80]}...")

    # Save as a single NSV file with 2 cells in one row
    with open('examples/3d_all_matrices_lift2.nsv', 'w') as f:
        nsv.dump([data_after_lift_2], f)

    print()
    print("Saved to examples/3d_all_matrices_lift2.nsv")

    # Third lift: entire structure becomes one cell
    data_after_lift_3 = nsv.lift(data_after_lift_2)

    with open('examples/3d_all_matrices_lift3.nsv', 'w') as f:
        nsv.dump([[data_after_lift_3]], f)

    print("After lifting all matrices to a single cell:")
    print(f"  Single cell length: {len(data_after_lift_3)} characters")
    print(f"  Preview: {repr(data_after_lift_3)[:100]}...")
    print()
    print("Saved to examples/3d_all_matrices_lift3.nsv")

    # Verify round-trip
    recovered_2 = [nsv.unlift(cell) for cell in nsv.unlift(data_after_lift_3)]
    recovered_3d = [[nsv.unlift(row) for row in matrix] for matrix in recovered_2]

    print()
    if recovered_3d == data_3d:
        print("✓ SUCCESS: 3D round-trip worked!")
    else:
        print("✗ FAILED: 3D data corrupted!")

if __name__ == "__main__":
    main()
