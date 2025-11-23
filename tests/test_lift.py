import unittest
import nsv

class TestLiftUnlift(unittest.TestCase):
    def test_basic_lift_2d_to_1d(self):
        original = "a\nb\n\nc\nd\n\n"
        lifted = nsv.lift(original)
        parsed = nsv.loads(lifted)
        self.assertEqual(1, len(parsed))
        self.assertEqual(5, len(parsed[0]))
        self.assertEqual(["a", "b", "", "c", "d"], parsed[0])

    def test_basic_unlift_1d_to_2d(self):
        lifted = "a\nb\n\\\nc\nd\n\n"
        unlifted = nsv.unlift(lifted)
        parsed = nsv.loads(unlifted)
        self.assertEqual(2, len(parsed))
        self.assertEqual(["a", "b"], parsed[0])
        self.assertEqual(["c", "d"], parsed[1])

    def test_roundtrip_property(self):
        test_cases = [
            "a\nb\nc\n\nd\ne\nf\n\n",
            "single\n\n",
            "\\\n\n",
            "a\n\\\nb\n\n",
        ]
        for original in test_cases:
            with self.subTest(original=original):
                lifted = nsv.lift(original)
                unlifted = nsv.unlift(lifted)
                self.assertEqual(original, unlifted)

    def test_double_lift(self):
        original = "a\nb\n\nc\nd\n\n"
        once_lifted = nsv.lift(original)
        twice_lifted = nsv.lift(once_lifted)
        parsed = nsv.loads(twice_lifted)
        self.assertEqual(5, len(parsed[0]))
        once_unlifted = nsv.unlift(twice_lifted)
        twice_unlifted = nsv.unlift(once_unlifted)
        self.assertEqual(original, twice_unlifted)

    def test_no_cascade(self):
        original = "a\nb\n\nc\nd\n\n"
        lift1 = nsv.lift(original)
        lift2 = nsv.lift(lift1)
        lift3 = nsv.lift(lift2)
        self.assertEqual(len(nsv.loads(lift1)[0]), len(nsv.loads(lift2)[0]))
        self.assertEqual(len(nsv.loads(lift2)[0]), len(nsv.loads(lift3)[0]))

    def test_lift_with_empty_cells(self):
        original = "\\\ng\n\\\n\n"
        lifted = nsv.lift(original)
        parsed = nsv.loads(lifted)
        self.assertEqual(["\\", "g", "\\"], parsed[0])
        unlifted = nsv.unlift(lifted)
        self.assertEqual(original, unlifted)

    def test_lift_with_special_chars(self):
        original = nsv.dumps([["line1\nline2", "path\\to\\file"]])
        lifted = nsv.lift(original)
        unlifted = nsv.unlift(lifted)
        self.assertEqual(original, unlifted)

    def test_unlift_requires_one_row(self):
        two_rows = "a\n\nb\n\n"
        with self.assertRaises(ValueError):
            nsv.unlift(two_rows)

    def test_combining_multiple_files(self):
        file1 = "a\nb\n\nc\nd\n\n"
        file2 = "e\nf\n\ng\nh\n\n"
        lifted1 = nsv.lift(file1)
        lifted2 = nsv.lift(file2)
        combined = nsv.dumps([[lifted1, lifted2]])
        parsed = nsv.loads(combined)
        self.assertEqual(2, len(parsed[0]))
        cell1_unlifted = nsv.unlift(parsed[0][0])
        cell2_unlifted = nsv.unlift(parsed[0][1])
        self.assertEqual(file1, cell1_unlifted)
        self.assertEqual(file2, cell2_unlifted)

    def test_3d_encoding(self):
        matrices = [
            [["a", "b"], ["c", "d"]],
            [["e", "f"], ["g", "h"]],
        ]
        lifted = [nsv.lift(nsv.dumps(m)) for m in matrices]
        combined = nsv.dumps([nsv.loads(l)[0] for l in lifted])
        final = nsv.lift(combined)
        rows = nsv.loads(nsv.unlift(final))
        recovered = [nsv.loads('\n'.join(row) + '\n\n') for row in rows]
        self.assertEqual(matrices, recovered)


if __name__ == '__main__':
    unittest.main()
