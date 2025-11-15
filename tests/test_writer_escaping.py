import unittest
from nsv.writer import Writer
from nsv import dumps, loads


class TestWriterEscaping(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(Writer.escape(""), "\\")

    def test_no_special_chars(self):
        self.assertEqual(Writer.escape("hello"), "hello")

    def test_single_backslash(self):
        self.assertEqual(Writer.escape("\\"), "\\\\")

    def test_single_newline(self):
        self.assertEqual(Writer.escape("\n"), "\\n")

    def test_backslash_in_middle(self):
        self.assertEqual(Writer.escape("a\\b"), "a\\\\b")

    def test_newline_in_middle(self):
        self.assertEqual(Writer.escape("a\nb"), "a\\nb")

    def test_backslash_then_letter_n(self):
        self.assertEqual(Writer.escape("\\n"), "\\\\n")

    def test_backslash_then_newline(self):
        self.assertEqual(Writer.escape("\\\n"), "\\\\\\n")

    def test_multiple_backslashes(self):
        self.assertEqual(Writer.escape("\\\\"), "\\\\\\\\")
        self.assertEqual(Writer.escape("\\\\\\"), "\\\\\\\\\\\\")

    def test_multiple_newlines(self):
        self.assertEqual(Writer.escape("\n\n"), "\\n\\n")
        self.assertEqual(Writer.escape("\n\n\n"), "\\n\\n\\n")

    def test_alternating_backslash_newline(self):
        self.assertEqual(Writer.escape("\\\n\\\n"), "\\\\\\n\\\\\\n")

    def test_complex_combinations(self):
        self.assertEqual(Writer.escape("\\a\nb\\"), "\\\\a\\nb\\\\")
        self.assertEqual(Writer.escape("\n\\\n\\"), "\\n\\\\\\n\\\\")

    def test_roundtrip_with_backslash_and_newline(self):
        test_cases = [
            "",
            "\\",
            "\n",
            "\\n",
            "\\\n",
            "a\\b\nc",
            "\\\\\\",
            "\n\n\n",
            "test\\ \n end",
        ]
        for original in test_cases:
            with self.subTest(original=repr(original)):
                encoded = dumps([[original]])
                decoded = loads(encoded)
                self.assertEqual(decoded[0][0], original)


if __name__ == '__main__':
    unittest.main()
