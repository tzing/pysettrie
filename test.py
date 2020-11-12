import unittest
from settrie import SetTrie, SetTrieDict


class TestSetTrie(unittest.TestCase):
    """
    UnitTest for SetTrie class
    """

    def setUp(self):
        self.t = SetTrie([(1, 3), (1, 3, 5), (1, 4), (1, 2, 4), (2, 4), (2, 3, 5)])

    def test_iter(self):
        self.assertCountEqual(
            list(self.t),
            [
                (1, 2, 4),
                (1, 3),
                (1, 3, 5),
                (1, 4),
                (2, 3, 5),
                (2, 4),
            ],
        )

    def test_iter2(self):
        it = iter(self.t)
        for s in it:
            pass
        self.assertRaises(StopIteration, it.__next__)

    def test_iter3(self):
        t2 = SetTrie()
        it = iter(t2)
        self.assertRaises(StopIteration, it.__next__)

    def test_repr(self):
        self.assertEqual(repr(self.t), "<SetTrie with 6 sets>")

    def test_contains(self):
        self.assertIn((1, 3), self.t)
        self.assertNotIn((1,), self.t)
        self.assertIn((1, 3, 5), self.t)
        self.assertNotIn((1, 3, 5, 7), self.t)

    def test_has_superset(self):
        self.assertTrue(self.t.has_superset((3, 5)))
        self.assertFalse(self.t.has_superset((6,)))
        self.assertTrue(self.t.has_superset((1, 2, 4)))
        self.assertFalse(self.t.has_superset((2, 4, 5)))

    def test_supersets(self):
        self.assertCountEqual(self.t.iter_supersets((3, 5)), [(1, 3, 5), (2, 3, 5)])
        self.assertCountEqual(self.t.iter_supersets((1, 4)), [(1, 2, 4), (1, 4)])
        self.assertCountEqual(self.t.iter_supersets((1, 3, 5)), [(1, 3, 5)])
        self.assertCountEqual(
            self.t.iter_supersets((2,)), [(1, 2, 4), (2, 3, 5), (2, 4)]
        )
        self.assertCountEqual(
            self.t.iter_supersets((1,)), [(1, 2, 4), (1, 3), (1, 3, 5), (1, 4)]
        )
        self.assertCountEqual(self.t.iter_supersets((1, 2, 5)), [])
        self.assertCountEqual(self.t.iter_supersets((1, 2, 4, 5)), [])
        self.assertCountEqual(self.t.iter_supersets((6,)), [])

    def test_has_subset(self):
        self.assertTrue(self.t.has_subset((1, 2, 3)))
        self.assertTrue(self.t.has_subset((2, 3, 4, 5)))
        self.assertTrue(self.t.has_subset((1, 4)))
        self.assertTrue(self.t.has_subset((2, 3, 5)))
        self.assertFalse(self.t.has_subset((3, 4, 5)))
        self.assertFalse(self.t.has_subset((6, 7, 8, 9, 1000)))

    def test_subsets(self):
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 4, 11)),
            [(1, 2, 4), (1, 4), (2, 4)],
        )
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 4)), [(1, 2, 4), (1, 4), (2, 4)]
        )
        self.assertCountEqual(self.t.iter_subsets((1, 2)), [])
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 3, 4, 5)),
            [(1, 2, 4), (1, 3), (1, 3, 5), (1, 4), (2, 3, 5), (2, 4)],
        )
        self.assertCountEqual(self.t.iter_subsets((0, 1, 3, 5)), [(1, 3), (1, 3, 5)])
        self.assertCountEqual(self.t.iter_subsets((1, 2, 5)), [])
        self.assertCountEqual(self.t.iter_subsets((1, 4)), [(1, 4)])  # :)
        self.assertCountEqual(self.t.iter_subsets((1, 3, 5)), [(1, 3), (1, 3, 5)])
        self.assertCountEqual(
            self.t.iter_subsets((1, 3, 5, 111)),
            [(1, 3), (1, 3, 5)],
        )
        self.assertCountEqual(self.t.iter_subsets((1, 4, 8)), [(1, 4)])
        self.assertCountEqual(self.t.iter_subsets((2, 3, 4, 5)), [(2, 3, 5), (2, 4)])
        self.assertCountEqual(self.t.iter_subsets((2, 3, 5, 6)), [(2, 3, 5)])

    def test_discard(self):
        self.assertIn([1, 3], self.t)
        self.t.discard((1, 3))
        self.assertIn([1, 3, 5], self.t)
        self.assertNotIn([1, 3], self.t)


class TestSetTrieDict(unittest.TestCase):
    """
    UnitTest for SetTrieMap class
    """

    def setUp(self):
        self.t: "SetTrieDict[int, str]" = SetTrieDict(
            [
                ((1, 3), "A"),
                ((1, 3, 5), "B"),
                ((1, 4), "C"),
                ((1, 2, 4), "D"),
                ((2, 4), "E"),
                ((2, 3, 5), "F"),
            ]
        )

    def test_in(self):
        self.assertTrue((1, 3) in self.t)
        self.assertFalse((1,) in self.t)
        self.assertTrue((1, 3, 5) in self.t)
        self.assertFalse((1, 3, 5, 7) in self.t)

    def test_get(self):
        self.assertEqual(self.t.get((1, 3)), "A")
        self.assertEqual(self.t.get((1, 3, 5)), "B")
        self.assertEqual(self.t.get((1, 4)), "C")
        self.assertEqual(self.t.get((1, 2, 4)), "D")
        self.assertEqual(self.t.get((2, 4)), "E")
        self.assertEqual(self.t.get((2, 3, 5)), "F")
        self.assertEqual(self.t.get((1, 2, 3)), None)
        self.assertEqual(
            self.t.get(
                (100, 101, 102),
                0xDEADBEEF,
            ),
            0xDEADBEEF,
        )
        self.assertEqual(self.t.get({}), None)

    def test_set(self):
        self.assertEqual(self.t.get((1, 3)), "A")
        self.t[1, 3] = "AAA"
        self.assertEqual(self.t.get((1, 3)), "AAA")
        self.assertEqual(self.t.get((100, 200)), None)
        self.t[(100, 200)] = "FOO"
        self.assertEqual(self.t.get((100, 200)), "FOO")

    def test_has_superset(self):
        self.assertTrue(self.t.has_superset((3, 5)))
        self.assertFalse(self.t.has_superset((6,)))
        self.assertTrue(self.t.has_superset((1, 2, 4)))
        self.assertFalse(self.t.has_superset((2, 4, 5)))

    def test_supersets(self):
        self.assertCountEqual(
            self.t.iter_supersets((3, 5)), [((1, 3, 5), "B"), ((2, 3, 5), "F")]
        )
        self.assertCountEqual(
            self.t.iter_supersets((1,)),
            [((1, 2, 4), "D"), ((1, 3), "A"), ((1, 3, 5), "B"), ((1, 4), "C")],
        )
        self.assertCountEqual(self.t.iter_supersets((1, 2, 5)), [])

    def test_has_subset(self):
        self.assertTrue(self.t.has_subset((1, 2, 3)))
        self.assertTrue(self.t.has_subset((2, 3, 4, 5)))
        self.assertTrue(self.t.has_subset((1, 4)))
        self.assertTrue(self.t.has_subset((2, 3, 5)))
        self.assertFalse(self.t.has_subset((3, 4, 5)))
        self.assertFalse(self.t.has_subset((6, 7, 8, 9, 1000)))

    def test_subsets(self):
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 4, 11)),
            [((1, 2, 4), "D"), ((1, 4), "C"), ((2, 4), "E")],
        )
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 4)),
            [((1, 2, 4), "D"), ((1, 4), "C"), ((2, 4), "E")],
        )
        self.assertCountEqual(self.t.iter_subsets((1, 2)), [])
        self.assertCountEqual(
            self.t.iter_subsets((1, 2, 3, 4, 5)),
            [
                ((1, 2, 4), "D"),
                ((1, 3), "A"),
                ((1, 3, 5), "B"),
                ((1, 4), "C"),
                ((2, 3, 5), "F"),
                ((2, 4), "E"),
            ],
        )
        self.assertCountEqual(
            self.t.iter_subsets((0, 1, 3, 5)), [((1, 3), "A"), ((1, 3, 5), "B")]
        )
        self.assertCountEqual(self.t.iter_subsets((1, 2, 5)), [])
        self.assertCountEqual(self.t.iter_subsets((1, 4)), [((1, 4), "C")])
        self.assertCountEqual(
            self.t.iter_subsets((1, 3, 5)), [((1, 3), "A"), ((1, 3, 5), "B")]
        )
        self.assertCountEqual(
            self.t.iter_subsets((1, 3, 5, 111)), [((1, 3), "A"), ((1, 3, 5), "B")]
        )
        self.assertCountEqual(self.t.iter_subsets((1, 4, 8)), [((1, 4), "C")])
        self.assertCountEqual(
            self.t.iter_subsets((2, 3, 4, 5)), [((2, 3, 5), "F"), ((2, 4), "E")]
        )
        self.assertCountEqual(self.t.iter_subsets((2, 3, 5, 6)), [((2, 3, 5), "F")])

    def test_iters(self):
        self.assertCountEqual(
            list(self.t.items()),
            [
                ((1, 2, 4), "D"),
                ((1, 3), "A"),
                ((1, 3, 5), "B"),
                ((1, 4), "C"),
                ((2, 3, 5), "F"),
                ((2, 4), "E"),
            ],
        )
        self.assertCountEqual(
            list(self.t.keys()),
            [
                (1, 2, 4),
                (1, 3),
                (1, 3, 5),
                (1, 4),
                (2, 3, 5),
                (2, 4),
            ],
        )
        self.assertCountEqual(self.t.values(), ["D", "A", "B", "C", "F", "E"])

    def test_pop(self):
        self.assertEqual(self.t.pop([1, 3]), "A")
        self.assertIn([1, 3, 5], self.t)
        self.assertNotIn([1, 3], self.t)


if __name__ == "__main__":
    unittest.main()
