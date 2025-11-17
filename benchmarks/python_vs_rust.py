#!/usr/bin/env python3
"""
Comprehensive benchmark comparing Python and Rust implementations of NSV.

This benchmark suite tests both implementations across various scenarios:
- Simple data (varying sizes)
- Data with special characters (newlines, backslashes)
- Wide tables (many columns)
- Realistic heterogeneous data
- Edge cases (empty cells, empty rows)
"""

import time
import sys
import random
import string
from typing import List, Callable, Tuple

# Import pure Python implementation
import nsv._python_impl as nsv_python

# Try to import Rust implementation
try:
    import nsv_rust_ext as nsv_rust
    RUST_AVAILABLE = True
except ImportError:
    print("WARNING: Rust extension not available. Install with: maturin develop")
    print("Continuing with Python-only benchmarks...")
    RUST_AVAILABLE = False


def generate_simple_data(rows: int, cols: int) -> List[List[str]]:
    """Generate simple tabular data."""
    return [[f"row{i}_col{j}" for j in range(cols)] for i in range(rows)]


def generate_data_with_newlines(rows: int, cols: int) -> List[List[str]]:
    """Generate data with embedded newlines (NSV needs to escape these)."""
    data = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if j % 3 == 0:
                row.append(f"Line1\nLine2\nrow{i}_col{j}")
            else:
                row.append(f"row{i}_col{j}")
        data.append(row)
    return data


def generate_data_with_backslashes(rows: int, cols: int) -> List[List[str]]:
    """Generate data with backslashes (NSV worst case)."""
    patterns = [
        r"C:\Windows\System32\drivers\etc\hosts",
        r"\\network\share\path\to\file.txt",
        r"Regex: \d+\.\d+\.\d+\.\d+",
        r"LaTeX: \textbf{bold} \textit{italic}",
    ]
    data = []
    for i in range(rows):
        row = []
        for j in range(cols):
            pattern = patterns[(i * cols + j) % len(patterns)]
            row.append(f"{pattern} [{i}]")
        data.append(row)
    return data


def generate_mixed_special_chars(rows: int, cols: int) -> List[List[str]]:
    """Generate data with mixed special characters."""
    patterns = [
        "Normal text",
        "Text with\nnewlines",
        r"Text with \backslashes",
        "",  # Empty cell
        "Text with, commas, and stuff",
        'Text with "quotes"',
    ]
    data = []
    for i in range(rows):
        row = []
        for j in range(cols):
            pattern = patterns[(i * cols + j) % len(patterns)]
            row.append(pattern)
        data.append(row)
    return data


def generate_realistic_table(rows: int) -> List[List[str]]:
    """Generate realistic heterogeneous table data."""
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    domains = ["gmail.com", "yahoo.com", "company.com", "email.org"]

    data = []
    for i in range(rows):
        first = first_names[i % len(first_names)]
        last = last_names[(i // 3) % len(last_names)]
        domain = domains[i % len(domains)]
        amount = (i * 12.34) % 10000.0
        year = 2020 + (i % 5)
        month = 1 + (i % 12)
        day = 1 + (i % 28)

        row = [
            f"{i:06d}",  # ID
            f"{first} {last}",  # Name
            f"{first.lower()}.{last.lower()}@{domain}",  # Email
            f"{year:04d}-{month:02d}-{day:02d}",  # Date
            f"{amount:.2f}",  # Amount
            "Active" if i % 3 == 0 else "Inactive",  # Status
            f"Notes for row {i}\nMultiline text here" if i % 5 == 0 else "",  # Notes
        ]
        data.append(row)
    return data


def benchmark_function(
    name: str,
    func: Callable[[str], List[List[str]]],
    data_str: str,
    iterations: int = 5
) -> Tuple[float, float]:
    """
    Benchmark a function and return (mean_time, std_dev).

    Args:
        name: Name of the benchmark
        func: Function to benchmark (takes string, returns parsed data)
        data_str: Input string
        iterations: Number of iterations

    Returns:
        (mean_time, std_dev) in seconds
    """
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(data_str)
        end = time.perf_counter()
        times.append(end - start)

    mean_time = sum(times) / len(times)
    variance = sum((t - mean_time) ** 2 for t in times) / len(times)
    std_dev = variance ** 0.5

    return mean_time, std_dev


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f}ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f}ms"
    else:
        return f"{seconds:.3f}s"


def format_speedup(ratio: float) -> str:
    """Format speedup ratio with color coding."""
    if ratio < 1:
        return f"{ratio:.2f}x (slower)"
    else:
        return f"{ratio:.2f}x faster"


def run_benchmark_suite():
    """Run comprehensive benchmark suite."""
    print("=" * 80)
    print("NSV Python vs Rust Implementation Benchmark")
    print("=" * 80)
    print()

    if not RUST_AVAILABLE:
        print("⚠️  Rust implementation not available - skipping comparison")
        print("   To build: cd rust-ext && maturin develop")
        print()
        return

    # Test cases: (name, data_generator, rows, cols)
    test_cases = [
        ("Small simple table", generate_simple_data, 100, 10),
        ("Medium simple table", generate_simple_data, 1000, 10),
        ("Large simple table", generate_simple_data, 10000, 10),
        ("Very large simple table", generate_simple_data, 100000, 10),
        ("Wide table", generate_simple_data, 1000, 100),
        ("Table with newlines", generate_data_with_newlines, 10000, 10),
        ("Table with backslashes", generate_data_with_backslashes, 10000, 10),
        ("Mixed special chars", generate_mixed_special_chars, 10000, 10),
        ("Realistic table", lambda r, c: generate_realistic_table(r), 10000, 1),
    ]

    results = []

    for test_name, generator, rows, cols in test_cases:
        print(f"Benchmarking: {test_name} ({rows} rows x {cols if cols > 1 else 'varied'} cols)")

        # Generate test data
        if cols == 1:  # Special case for realistic table
            data = generator(rows, cols)
        else:
            data = generator(rows, cols)

        # Encode to NSV string
        nsv_str = nsv_python.dumps(data)
        data_size_mb = len(nsv_str) / (1024 * 1024)

        print(f"  Data size: {len(nsv_str):,} bytes ({data_size_mb:.2f} MB)")

        # Benchmark Python loads
        py_mean, py_std = benchmark_function("Python loads", nsv_python.loads, nsv_str)
        print(f"  Python loads:  {format_time(py_mean)} ± {format_time(py_std)}")

        # Benchmark Rust loads
        rust_mean, rust_std = benchmark_function("Rust loads", nsv_rust.loads, nsv_str)
        print(f"  Rust loads:    {format_time(rust_mean)} ± {format_time(rust_std)}")

        # Calculate speedup
        speedup = py_mean / rust_mean
        print(f"  Speedup:       {format_speedup(speedup)}")

        # Benchmark dumps
        py_dumps_mean, _ = benchmark_function("Python dumps", lambda _: nsv_python.dumps(data), "")
        rust_dumps_mean, _ = benchmark_function("Rust dumps", lambda _: nsv_rust.dumps(data), "")
        dumps_speedup = py_dumps_mean / rust_dumps_mean

        print(f"  Python dumps:  {format_time(py_dumps_mean)}")
        print(f"  Rust dumps:    {format_time(rust_dumps_mean)}")
        print(f"  Dumps speedup: {format_speedup(dumps_speedup)}")
        print()

        results.append({
            'name': test_name,
            'rows': rows,
            'cols': cols,
            'size_bytes': len(nsv_str),
            'py_loads': py_mean,
            'rust_loads': rust_mean,
            'loads_speedup': speedup,
            'py_dumps': py_dumps_mean,
            'rust_dumps': rust_dumps_mean,
            'dumps_speedup': dumps_speedup,
        })

    # Print summary table
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Test Case':<30} {'Size (MB)':<12} {'Loads Speedup':<15} {'Dumps Speedup':<15}")
    print("-" * 80)

    for r in results:
        size_mb = r['size_bytes'] / (1024 * 1024)
        print(f"{r['name']:<30} {size_mb:>11.2f} {r['loads_speedup']:>14.2f}x {r['dumps_speedup']:>14.2f}x")

    print()
    print(f"Average loads speedup: {sum(r['loads_speedup'] for r in results) / len(results):.2f}x")
    print(f"Average dumps speedup: {sum(r['dumps_speedup'] for r in results) / len(results):.2f}x")
    print()

    # Show which test cases benefit most
    print("Top 3 cases with highest loads speedup:")
    sorted_loads = sorted(results, key=lambda x: x['loads_speedup'], reverse=True)
    for i, r in enumerate(sorted_loads[:3], 1):
        print(f"  {i}. {r['name']}: {r['loads_speedup']:.2f}x")

    print()
    print("Top 3 cases with highest dumps speedup:")
    sorted_dumps = sorted(results, key=lambda x: x['dumps_speedup'], reverse=True)
    for i, r in enumerate(sorted_dumps[:3], 1):
        print(f"  {i}. {r['name']}: {r['dumps_speedup']:.2f}x")


if __name__ == "__main__":
    run_benchmark_suite()
