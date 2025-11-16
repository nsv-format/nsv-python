#!/usr/bin/env python3
"""
Cross-validation test suite: Python vs Rust implementation

This script runs all test cases from the nsv-python test suite against both
the pure Python implementation and the Rust implementation via PyO3 bindings,
ensuring semantic compatibility.
"""

import sys
import os
import unittest
from io import StringIO
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import both implementations
import nsv as nsv_python

try:
    import nsv_rust_ext as nsv_rust
    RUST_AVAILABLE = True
except ImportError:
    print("ERROR: Rust extension not available!")
    print("Build it with: cd rust-ext && maturin develop --release")
    sys.exit(1)

# Import test utilities
from tests.test_utils import SAMPLES_DIR, SAMPLES_DATA


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_pass(msg):
    print(f"{Colors.GREEN}✓ PASS{Colors.END} {msg}")


def print_fail(msg):
    print(f"{Colors.RED}✗ FAIL{Colors.END} {msg}")


def print_section(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")


class CrossValidationTests:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_equal(self, expected, actual, test_name):
        """Compare expected vs actual and track results."""
        if expected == actual:
            self.passed += 1
            print_pass(test_name)
            return True
        else:
            self.failed += 1
            print_fail(test_name)
            self.errors.append({
                'test': test_name,
                'expected': expected,
                'actual': actual
            })
            return False

    def test_loads_on_samples(self):
        """Test loads() on all sample files."""
        print_section("Testing loads() on Sample Files")

        for name in sorted(SAMPLES_DATA.keys()):
            file_path = os.path.join(SAMPLES_DIR, f'{name}.nsv')
            with open(file_path, 'r') as f:
                nsv_string = f.read()

            # Parse with both implementations
            python_result = nsv_python.loads(nsv_string)
            rust_result = nsv_rust.loads(nsv_string)

            # Also check against expected data
            expected = SAMPLES_DATA[name]

            test_name = f"loads('{name}.nsv')"

            # First verify Python matches expected
            if python_result != expected:
                print(f"{Colors.YELLOW}⚠ WARNING{Colors.END} Python impl doesn't match expected for {name}")
                print(f"  Expected: {expected}")
                print(f"  Got:      {python_result}")

            # Then verify Rust matches Python
            self.assert_equal(python_result, rust_result, test_name)

            if python_result != rust_result:
                print(f"  Python: {python_result}")
                print(f"  Rust:   {rust_result}")

    def test_dumps_on_samples(self):
        """Test dumps() on all sample data."""
        print_section("Testing dumps() on Sample Data")

        for name in sorted(SAMPLES_DATA.keys()):
            data = SAMPLES_DATA[name]

            # Serialize with both implementations
            python_result = nsv_python.dumps(data)
            rust_result = nsv_rust.dumps(data)

            test_name = f"dumps(SAMPLES_DATA['{name}'])"
            self.assert_equal(python_result, rust_result, test_name)

            if python_result != rust_result:
                print(f"  Python output ({len(python_result)} bytes):")
                print(f"    {repr(python_result)}")
                print(f"  Rust output ({len(rust_result)} bytes):")
                print(f"    {repr(rust_result)}")

    def test_roundtrip_loads_dumps(self):
        """Test roundtrip: data -> dumps -> loads -> data."""
        print_section("Testing Roundtrip: dumps() -> loads()")

        for name in sorted(SAMPLES_DATA.keys()):
            data = SAMPLES_DATA[name]

            # Python roundtrip
            python_encoded = nsv_python.dumps(data)
            python_decoded = nsv_python.loads(python_encoded)

            # Rust roundtrip
            rust_encoded = nsv_rust.dumps(data)
            rust_decoded = nsv_rust.loads(rust_encoded)

            # Cross roundtrip: Python dumps, Rust loads
            cross_pr = nsv_rust.loads(python_encoded)

            # Cross roundtrip: Rust dumps, Python loads
            cross_rp = nsv_python.loads(rust_encoded)

            test_name = f"roundtrip('{name}')"

            # All should produce the original data
            success = True
            if python_decoded != data:
                print_fail(f"{test_name} - Python roundtrip")
                print(f"  Original: {data}")
                print(f"  After roundtrip: {python_decoded}")
                success = False

            if rust_decoded != data:
                print_fail(f"{test_name} - Rust roundtrip")
                print(f"  Original: {data}")
                print(f"  After roundtrip: {rust_decoded}")
                success = False

            if cross_pr != data:
                print_fail(f"{test_name} - Python dumps, Rust loads")
                print(f"  Original: {data}")
                print(f"  After roundtrip: {cross_pr}")
                success = False

            if cross_rp != data:
                print_fail(f"{test_name} - Rust dumps, Python loads")
                print(f"  Original: {data}")
                print(f"  After roundtrip: {cross_rp}")
                success = False

            if success:
                self.passed += 1
                print_pass(test_name)
            else:
                self.failed += 1

    def test_edge_cases(self):
        """Test edge cases from test_edge_cases.py."""
        print_section("Testing Edge Cases")

        # Test 1: Long Unicode strings (valid UTF-8 only)
        # Note: Skipping surrogates (0xD800-0xDFFF) as they're invalid in UTF-8
        # Rust strings must be valid UTF-8, Python can handle invalid Unicode
        print(f"{Colors.YELLOW}⚠ NOTE{Colors.END} Skipping invalid Unicode surrogates test (not valid UTF-8)")
        print(f"  This is expected - Rust strings enforce valid UTF-8")

        # Test with valid Unicode instead
        long_string = ''.join(chr(x) for x in range(0x20, 0x7F))  # ASCII printable
        long_string += ''.join(chr(x) for x in range(0x100, 0x200))  # Latin Extended
        long_string += ''.join(chr(x) for x in range(0x4E00, 0x4F00))  # CJK
        long_string += ''.join(chr(x) for x in range(0x1F600, 0x1F650))  # Emoji

        data = [
            ["normal", long_string],
            [long_string, "normal"]
        ]

        python_encoded = nsv_python.dumps(data)
        rust_encoded = nsv_rust.dumps(data)

        python_decoded = nsv_python.loads(python_encoded)
        rust_decoded = nsv_rust.loads(rust_encoded)

        test_name = "long_valid_unicode_strings"
        success = (python_decoded == data and rust_decoded == data and
                   python_encoded == rust_encoded)

        if success:
            self.passed += 1
            print_pass(test_name)
        else:
            self.failed += 1
            print_fail(test_name)
            if python_decoded != data:
                print(f"  Python roundtrip failed")
            if rust_decoded != data:
                print(f"  Rust roundtrip failed")
            if python_encoded != rust_encoded:
                print(f"  Encoded outputs differ")

        # Test 2: Special characters
        file_path = os.path.join(SAMPLES_DIR, 'special_chars.nsv')
        with open(file_path, 'r') as f:
            nsv_string = f.read()

        python_result = nsv_python.loads(nsv_string)
        rust_result = nsv_rust.loads(nsv_string)

        test_name = "special_chars_file"
        self.assert_equal(SAMPLES_DATA['special_chars'], python_result, f"{test_name} (Python)")
        self.assert_equal(SAMPLES_DATA['special_chars'], rust_result, f"{test_name} (Rust)")
        self.assert_equal(python_result, rust_result, f"{test_name} (Python vs Rust)")

        # Test 3: Trailing backslash
        expected_trailing = [
            ['yo', 'shouln\'ta', 'be', 'doing', 'this'],
            ['', 'or', '', 'should', '', 'ya'],
        ]
        file_path = os.path.join(SAMPLES_DIR, 'trailing_backslash.nsv')
        with open(file_path, 'r') as f:
            nsv_string = f.read()

        python_result = nsv_python.loads(nsv_string)
        rust_result = nsv_rust.loads(nsv_string)

        test_name = "trailing_backslash"
        self.assert_equal(expected_trailing, python_result, f"{test_name} (Python)")
        self.assert_equal(expected_trailing, rust_result, f"{test_name} (Rust)")
        self.assert_equal(python_result, rust_result, f"{test_name} (Python vs Rust)")

    def test_escape_sequences(self):
        """Test specific escape sequence handling."""
        print_section("Testing Escape Sequences")

        test_cases = [
            # (description, input_data, expected_encoding)
            ("empty_cell", [["", "b"]], "\\\nb\n\n"),
            ("backslash", [["a\\b"]], "a\\\\b\n\n"),
            ("newline", [["a\nb"]], "a\\nb\n\n"),
            ("backslash_n", [["\\n"]], "\\\\n\n\n"),
            ("double_backslash", [["\\\\"]], "\\\\\\\\\n\n"),
            ("mixed", [["a\\b\nc"]], "a\\\\b\\nc\n\n"),
        ]

        for desc, data, expected_encoding in test_cases:
            python_encoded = nsv_python.dumps(data)
            rust_encoded = nsv_rust.dumps(data)

            test_name = f"escape_{desc}_encoding"
            if python_encoded == expected_encoding and rust_encoded == expected_encoding:
                self.passed += 1
                print_pass(test_name)
            else:
                self.failed += 1
                print_fail(test_name)
                print(f"  Expected: {repr(expected_encoding)}")
                print(f"  Python:   {repr(python_encoded)}")
                print(f"  Rust:     {repr(rust_encoded)}")

            # Also test decoding
            python_decoded = nsv_python.loads(expected_encoding)
            rust_decoded = nsv_rust.loads(expected_encoding)

            test_name = f"escape_{desc}_decoding"
            if python_decoded == data and rust_decoded == data:
                self.passed += 1
                print_pass(test_name)
            else:
                self.failed += 1
                print_fail(test_name)
                print(f"  Input:    {repr(expected_encoding)}")
                print(f"  Expected: {data}")
                print(f"  Python:   {python_decoded}")
                print(f"  Rust:     {rust_decoded}")

    def test_empty_cases(self):
        """Test various empty cases."""
        print_section("Testing Empty Cases")

        test_cases = [
            ("empty_string", "", []),
            ("single_newline", "\n", [[]]),
            ("double_newline", "\n\n", [[], []]),
            ("triple_newline", "\n\n\n", [[], [], []]),
            ("empty_row", "\n\na\n", [[], [], ["a"]]),
        ]

        for desc, input_str, expected in test_cases:
            python_result = nsv_python.loads(input_str)
            rust_result = nsv_rust.loads(input_str)

            test_name = f"empty_{desc}"
            self.assert_equal(expected, python_result, f"{test_name} (Python)")
            self.assert_equal(expected, rust_result, f"{test_name} (Rust)")
            self.assert_equal(python_result, rust_result, f"{test_name} (Python vs Rust)")

    def print_summary(self):
        """Print test summary."""
        print_section("Test Summary")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"Pass rate: {pass_rate:.1f}%")

        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}FAILURE DETAILS:{Colors.END}")
            for error in self.errors:
                print(f"\n{Colors.RED}Test: {error['test']}{Colors.END}")
                print(f"  Expected: {error['expected']}")
                print(f"  Actual:   {error['actual']}")

        return self.failed == 0


def main():
    print(f"{Colors.BOLD}NSV Cross-Validation: Python vs Rust Implementation{Colors.END}")
    print(f"Python implementation: nsv (pure Python)")
    print(f"Rust implementation: nsv_rust_ext (PyO3 bindings to nsv-rust)\n")

    validator = CrossValidationTests()

    # Run all test suites
    validator.test_loads_on_samples()
    validator.test_dumps_on_samples()
    validator.test_roundtrip_loads_dumps()
    validator.test_edge_cases()
    validator.test_escape_sequences()
    validator.test_empty_cases()

    # Print summary
    success = validator.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
