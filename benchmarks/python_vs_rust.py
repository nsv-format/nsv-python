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
    func,
    data,
    iterations: int = 5
) -> Tuple[float, float]:
    """
    Benchmark a function and return (mean_time, std_dev).

    Args:
        name: Name of the benchmark
        func: Function to benchmark
        data: Input data passed to func
        iterations: Number of iterations

    Returns:
        (mean_time, std_dev) in seconds
    """
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(data)
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
        data = generator(rows, cols)

        # Encode to NSV string and bytes
        nsv_str = nsv_python.dumps(data)
        nsv_bytes = nsv_str.encode()
        data_bytes = [[cell.encode() for cell in row] for row in data]
        data_size_mb = len(nsv_str) / (1024 * 1024)

        print(f"  Data size: {len(nsv_str):,} bytes ({data_size_mb:.2f} MB)")

        # ── loads ──────────────────────────────────────────────────────────
        py_mean, py_std = benchmark_function("Python loads", nsv_python.loads, nsv_str)
        rust_mean, rust_std = benchmark_function("Rust loads", nsv_rust.loads, nsv_str)
        rust_bytes_mean, rust_bytes_std = benchmark_function(
            "Rust loads_bytes", nsv_rust.loads_bytes, nsv_bytes
        )
        py_bytes_mean, py_bytes_std = benchmark_function(
            "Python loads_bytes", nsv_python.loads_bytes, nsv_bytes
        )

        loads_speedup = py_mean / rust_mean
        loads_bytes_speedup = py_mean / rust_bytes_mean  # bytes vs Python str baseline

        print(f"  Python loads:        {format_time(py_mean)} ± {format_time(py_std)}")
        print(f"  Rust loads (str):    {format_time(rust_mean)} ± {format_time(rust_std)}  [{format_speedup(loads_speedup)}]")
        print(f"  Rust loads_bytes:    {format_time(rust_bytes_mean)} ± {format_time(rust_bytes_std)}  [{format_speedup(loads_bytes_speedup)}]")
        print(f"  Python loads_bytes:  {format_time(py_bytes_mean)} ± {format_time(py_bytes_std)}")

        # ── dumps ──────────────────────────────────────────────────────────
        py_dumps_mean, _ = benchmark_function("Python dumps", lambda _: nsv_python.dumps(data), None)
        rust_dumps_mean, _ = benchmark_function("Rust dumps", lambda _: nsv_rust.dumps(data), None)
        rust_dumps_bytes_mean, _ = benchmark_function(
            "Rust dumps_bytes", lambda _: nsv_rust.dumps_bytes(data_bytes), None
        )
        py_dumps_bytes_mean, _ = benchmark_function(
            "Python dumps_bytes", lambda _: nsv_python.dumps_bytes(data_bytes), None
        )

        dumps_speedup = py_dumps_mean / rust_dumps_mean
        dumps_bytes_speedup = py_dumps_mean / rust_dumps_bytes_mean

        print(f"  Python dumps:        {format_time(py_dumps_mean)}")
        print(f"  Rust dumps (str):    {format_time(rust_dumps_mean)}  [{format_speedup(dumps_speedup)}]")
        print(f"  Rust dumps_bytes:    {format_time(rust_dumps_bytes_mean)}  [{format_speedup(dumps_bytes_speedup)}]")
        print(f"  Python dumps_bytes:  {format_time(py_dumps_bytes_mean)}")
        print()

        results.append({
            'name': test_name,
            'rows': rows,
            'cols': cols,
            'size_bytes': len(nsv_str),
            'py_loads': py_mean,
            'rust_loads': rust_mean,
            'loads_speedup': loads_speedup,
            'rust_loads_bytes': rust_bytes_mean,
            'loads_bytes_speedup': loads_bytes_speedup,
            'py_dumps': py_dumps_mean,
            'rust_dumps': rust_dumps_mean,
            'dumps_speedup': dumps_speedup,
            'rust_dumps_bytes': rust_dumps_bytes_mean,
            'dumps_bytes_speedup': dumps_bytes_speedup,
        })

    # Print summary table
    print("=" * 96)
    print("SUMMARY")
    print("=" * 96)
    print()
    print(f"{'Test Case':<30} {'Size (MB)':<10} {'loads(str)':<13} {'loads_bytes':<13} {'dumps(str)':<13} {'dumps_bytes':<13}")
    print("-" * 96)

    for r in results:
        size_mb = r['size_bytes'] / (1024 * 1024)
        print(
            f"{r['name']:<30} {size_mb:>9.2f} "
            f"{r['loads_speedup']:>11.2f}x "
            f"{r['loads_bytes_speedup']:>11.2f}x "
            f"{r['dumps_speedup']:>11.2f}x "
            f"{r['dumps_bytes_speedup']:>11.2f}x"
        )

    print()
    avg_loads     = sum(r['loads_speedup']       for r in results) / len(results)
    avg_loads_b   = sum(r['loads_bytes_speedup'] for r in results) / len(results)
    avg_dumps     = sum(r['dumps_speedup']       for r in results) / len(results)
    avg_dumps_b   = sum(r['dumps_bytes_speedup'] for r in results) / len(results)
    print(f"Average Rust str  speedup:   loads {avg_loads:.2f}x  dumps {avg_dumps:.2f}x")
    print(f"Average Rust bytes speedup:  loads {avg_loads_b:.2f}x  dumps {avg_dumps_b:.2f}x")
    print()

    # Show which test cases benefit most
    print("Top 3 cases with highest loads_bytes speedup:")
    sorted_loads = sorted(results, key=lambda x: x['loads_bytes_speedup'], reverse=True)
    for i, r in enumerate(sorted_loads[:3], 1):
        print(f"  {i}. {r['name']}: {r['loads_bytes_speedup']:.2f}x")

    print()
    print("Top 3 cases with highest dumps_bytes speedup:")
    sorted_dumps = sorted(results, key=lambda x: x['dumps_bytes_speedup'], reverse=True)
    for i, r in enumerate(sorted_dumps[:3], 1):
        print(f"  {i}. {r['name']}: {r['dumps_bytes_speedup']:.2f}x")


if __name__ == "__main__":
    run_benchmark_suite()
