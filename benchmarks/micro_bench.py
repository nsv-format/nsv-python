#!/usr/bin/env python3
"""
Micro-benchmark: sub-64KB files (sequential fast path in nsv-rust).

Tests where Rust overhead (PyO3, FFI) vs raw speed crossover happens.
"""

import time
import nsv._python_impl as nsv_python
import nsv_rust_ext as nsv_rust


def generate_simple_data(rows, cols):
    """Generate simple tabular data."""
    return [[f"row{i}_col{j}" for j in range(cols)] for i in range(rows)]


def benchmark(name, func, data, iterations=10):
    """Benchmark with more iterations for small data."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(data)
        end = time.perf_counter()
        times.append(end - start)

    mean = sum(times) / len(times)
    variance = sum((t - mean) ** 2 for t in times) / len(times)
    std_dev = variance ** 0.5
    return mean, std_dev


def format_time(seconds):
    """Format time in human-readable units."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f}ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f}ms"
    else:
        return f"{seconds:.3f}s"


def run_micro_benchmarks():
    """Test small file performance below 64KB parallel threshold."""

    print("=" * 80)
    print("Micro-benchmark: Sub-64KB files (sequential fast path)")
    print("=" * 80)
    print()

    # Test cases: (rows, cols) tuples designed to hit specific sizes
    test_cases = [
        # ~1KB
        (10, 10, "~1 KB"),
        (20, 10, "~2 KB"),
        # ~4KB
        (40, 10, "~4 KB"),
        # ~8KB
        (80, 10, "~8 KB"),
        # ~16KB
        (160, 10, "~16 KB"),
        # ~32KB
        (320, 10, "~32 KB"),
        # Just under 64KB threshold
        (600, 10, "~60 KB"),
        # Just over 64KB threshold
        (650, 10, "~65 KB"),
    ]

    results = []

    for rows, cols, label in test_cases:
        data = generate_simple_data(rows, cols)

        # Encode with Python
        nsv_str = nsv_python.dumps(data)
        nsv_bytes = nsv_str.encode()
        data_bytes = [[cell.encode() for cell in row] for row in data]

        actual_size_kb = len(nsv_str) / 1024

        print(f"{label:<10} ({rows:>4} rows, {actual_size_kb:>6.2f} KB actual)")

        # Benchmark loads
        py_mean, py_std = benchmark("Python loads", nsv_python.loads, nsv_str)
        rust_mean, rust_std = benchmark("Rust loads", nsv_rust.loads, nsv_str)
        loads_speedup = py_mean / rust_mean

        print(f"  Python loads:      {format_time(py_mean):>10} ± {format_time(py_std)}")
        print(f"  Rust loads:        {format_time(rust_mean):>10} ± {format_time(rust_std)}  [{loads_speedup:.2f}x]")

        # Benchmark loads_bytes
        py_bytes_mean, _ = benchmark("Python loads_bytes", nsv_python.loads_bytes, nsv_bytes)
        rust_bytes_mean, _ = benchmark("Rust loads_bytes", nsv_rust.loads_bytes, nsv_bytes)
        loads_bytes_speedup = py_bytes_mean / rust_bytes_mean

        print(f"  Python loads_bytes:{format_time(py_bytes_mean):>10}")
        print(f"  Rust loads_bytes:  {format_time(rust_bytes_mean):>10}  [{loads_bytes_speedup:.2f}x]")

        # Benchmark dumps
        py_dumps_mean, _ = benchmark("Python dumps", lambda _: nsv_python.dumps(data), None)
        rust_dumps_mean, _ = benchmark("Rust dumps", lambda _: nsv_rust.dumps(data), None)
        dumps_speedup = py_dumps_mean / rust_dumps_mean

        print(f"  Python dumps:      {format_time(py_dumps_mean):>10}")
        print(f"  Rust dumps:        {format_time(rust_dumps_mean):>10}  [{dumps_speedup:.2f}x]")
        print()

        results.append({
            'label': label,
            'rows': rows,
            'size_kb': actual_size_kb,
            'loads_speedup': loads_speedup,
            'loads_bytes_speedup': loads_bytes_speedup,
            'dumps_speedup': dumps_speedup,
        })

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Size':<12} {'Rows':<8} {'KB':<8} {'loads':<10} {'loads_bytes':<12} {'dumps':<10}")
    print("-" * 80)

    for r in results:
        print(f"{r['label']:<12} {r['rows']:<8} {r['size_kb']:<8.2f} "
              f"{r['loads_speedup']:<10.2f} {r['loads_bytes_speedup']:<12.2f} "
              f"{r['dumps_speedup']:<10.2f}")

    print()

    # Find the crossover point where Rust becomes faster
    print("Crossover analysis:")
    for r in results:
        if r['loads_speedup'] < 1.0:
            print(f"  loads: Python faster at {r['label']} ({r['size_kb']:.2f} KB)")
            break
    else:
        print(f"  loads: Rust faster at all tested sizes")

    for r in results:
        if r['dumps_speedup'] < 1.0:
            print(f"  dumps: Python faster at {r['label']} ({r['size_kb']:.2f} KB)")
            break
    else:
        print(f"  dumps: Rust faster at all tested sizes (though margin is small)")


if __name__ == "__main__":
    run_micro_benchmarks()
