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
    print("STEP 0: Original 2D data")
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

    # The flat sequence is all lines (including empty row delimiters)
    # Split and remove only the final empty element after the last newline
    lines = nsv_string.split('\n')[:-1]
    print("Flat sequence of lines:")
    print(f"  {lines}")
    print(f"  ({len(lines)} lines)")
    print()

    print("="*70)
    print("STEP 1: After lift (flat sequence encoded as single row)")
    print("="*70)

    # Lift the entire flat sequence
    lifted = nsv.lift(lines)

    print(f"Lifted string: {repr(lifted)}")
    print()

    # This is now a single row with one cell
    with open('examples/2_after_lift.nsv', 'w') as f:
        nsv.dump([[lifted]], f)

    print("NSV file (examples/2_after_lift.nsv) - one row, one cell:")
    with open('examples/2_after_lift.nsv', 'r') as f:
        content = f.read()
        print(repr(content))
        print("\nVisual:")
        print(content)

    print("="*70)
    print("VERIFICATION: Unlift and re-parse to recover original")
    print("="*70)

    # Load the lifted file
    with open('examples/2_after_lift.nsv', 'r') as f:
        loaded = nsv.load(f)

    print(f"Loaded: {loaded}")
    print(f"Single cell content: {repr(loaded[0][0])}")
    print()

    # Unlift to get back the flat sequence
    unlifted_lines = nsv.unlift(loaded[0][0])
    print(f"After unlift (flat sequence): {unlifted_lines}")
    print()

    # Re-parse as NSV to get back the 2D structure
    recovered_nsv = '\n'.join(unlifted_lines) + '\n'
    recovered_2d = nsv.loads(recovered_nsv)

    print("After re-parsing as NSV:")
    for i, row in enumerate(recovered_2d):
        print(f"  Row {i}: {row}")
    print()

    if recovered_2d == original_2d:
        print("✓ SUCCESS: Recovered data matches original!")
    else:
        print("✗ FAILED: Data mismatch!")
        print(f"  Original:  {original_2d}")
        print(f"  Recovered: {recovered_2d}")

    print("\n" + "="*70)
    print("DOUBLE LIFT: Lift the lifted data again")
    print("="*70)

    # Now lift the already-lifted NSV file
    with open('examples/2_after_lift.nsv', 'r') as f:
        lifted_nsv_string = f.read()

    lifted_lines = lifted_nsv_string.split('\n')[:-1]
    print(f"Lines from lifted file: {lifted_lines}")
    print()

    # Lift again
    double_lifted = nsv.lift(lifted_lines)
    print(f"Double-lifted string length: {len(double_lifted)} chars")
    print(f"Preview: {repr(double_lifted[:100])}...")
    print()

    # Save as NSV
    with open('examples/3_after_double_lift.nsv', 'w') as f:
        nsv.dump([[double_lifted]], f)

    print("Saved to examples/3_after_double_lift.nsv")
    print()

    # Verify double round-trip
    with open('examples/3_after_double_lift.nsv', 'r') as f:
        loaded = nsv.load(f)

    print(f"Loaded double-lifted: {len(loaded[0][0])} char cell")
    first_unlift = nsv.unlift(loaded[0][0])
    print(f"After first unlift: {len(first_unlift)} lines")

    # The first unlift gives us back the lines of the lifted NSV file
    # Reconstruct the NSV string and parse it to get the single cell
    first_nsv = '\n'.join(first_unlift) + '\n'
    first_parsed = nsv.loads(first_nsv)

    # Now unlift that cell to get the original flat sequence
    second_unlift = nsv.unlift(first_parsed[0][0])
    print(f"After second unlift: {len(second_unlift)} lines")

    recovered_final = nsv.loads('\n'.join(second_unlift) + '\n')
    print(f"After re-parsing: {recovered_final}")

    if recovered_final == original_2d:
        print("✓ SUCCESS: Double round-trip worked!")
    else:
        print("✗ FAILED: Double round-trip failed!")

    print("\n" + "="*70)
    print("3D EXAMPLE: Multiple NSV files → Single lifted file")
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

    # Lift each NSV file (convert to flat sequence and lift)
    lines_0 = nsv_0.split('\n')[:-1]
    lines_1 = nsv_1.split('\n')[:-1]

    lifted_0 = nsv.lift(lines_0)
    lifted_1 = nsv.lift(lines_1)

    print(f"Lifted matrix 0: {repr(lifted_0)}")
    print(f"Lifted matrix 1: {repr(lifted_1)}")
    print()

    # Now we have 2 cells that can be stored as one row
    combined = [[lifted_0, lifted_1]]
    with open('examples/3d_combined.nsv', 'w') as f:
        nsv.dump(combined, f)

    print("Saved combined to examples/3d_combined.nsv (2 cells in 1 row)")
    print()

    # Lift the combined file to get everything in one cell
    combined_nsv = nsv.dumps(combined)
    combined_lines = combined_nsv.split('\n')[:-1]

    triple_lifted = nsv.lift(combined_lines)

    with open('examples/3d_triple_lift.nsv', 'w') as f:
        nsv.dump([[triple_lifted]], f)

    print(f"Triple-lifted length: {len(triple_lifted)} chars")
    print("Saved to examples/3d_triple_lift.nsv (everything in 1 cell)")
    print()

    # Verify 3D round-trip
    with open('examples/3d_triple_lift.nsv', 'r') as f:
        loaded = nsv.load(f)

    # Unlift 3 times
    u1 = nsv.unlift(loaded[0][0])
    u2 = nsv.loads('\n'.join(u1) + '\n')

    recovered_matrices = []
    for cell in u2[0]:
        u3 = nsv.unlift(cell)
        matrix = nsv.loads('\n'.join(u3) + '\n')
        recovered_matrices.append(matrix)

    print("Recovered matrices:")
    print("  Matrix 0:", recovered_matrices[0])
    print("  Matrix 1:", recovered_matrices[1])
    print()

    if recovered_matrices[0] == matrix_0 and recovered_matrices[1] == matrix_1:
        print("✓ SUCCESS: 3D round-trip worked!")
    else:
        print("✗ FAILED: 3D round-trip failed!")

if __name__ == "__main__":
    main()
