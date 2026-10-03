import unittest

from circular_buffer import CircularBuffer, IsFullError, IsEmptyError


class TestConstruction(unittest.TestCase):
    def test_rejects_zero_capacity(self):
        with self.assertRaises(ValueError):
            CircularBuffer(0)

    def test_rejects_negative_capacity(self):
        with self.assertRaises(ValueError):
            CircularBuffer(-3)

    def test_starts_empty(self):
        b = CircularBuffer(4)
        self.assertTrue(b.is_empty())
        self.assertFalse(b.is_full())
        self.assertEqual(len(b), 0)
        self.assertEqual(b.capacity, 4)


class TestPushPop(unittest.TestCase):
    def test_push_then_pop_preserves_order(self):
        b = CircularBuffer(3)
        b.push("a")
        b.push("b")
        self.assertEqual(b.pop(), "a")
        self.assertEqual(b.pop(), "b")
        self.assertTrue(b.is_empty())

    def test_push_raises_when_full(self):
        b = CircularBuffer(2)
        b.push(1)
        b.push(2)
        with self.assertRaises(IsFullError):
            b.push(3)
        self.assertEqual(len(b), 2)

    def test_pop_raises_when_empty(self):
        b = CircularBuffer(2)
        with self.assertRaises(IsEmptyError):
            b.pop()

    def test_peek_returns_oldest_without_removing(self):
        b = CircularBuffer(2)
        b.push("x")
        b.push("y")
        self.assertEqual(b.peek(), "x")
        self.assertEqual(len(b), 2)
        self.assertEqual(b.peek(), "x")

    def test_peek_raises_when_empty(self):
        b = CircularBuffer(2)
        with self.assertRaises(IsEmptyError):
            b.peek()

    def test_none_is_a_valid_value(self):
        b = CircularBuffer(2)
        b.push(None)
        self.assertEqual(len(b), 1)
        self.assertIs(b.pop(), None)
        self.assertTrue(b.is_empty())

    def test_reuse_after_drain(self):
        b = CircularBuffer(2)
        b.push(1)
        b.push(2)
        b.pop()
        b.push(3)
        self.assertEqual(b.pop(), 2)
        self.assertEqual(b.pop(), 3)
        self.assertTrue(b.is_empty())


class TestOverwrite(unittest.TestCase):
    def test_overwrite_when_full_drops_oldest(self):
        b = CircularBuffer(3)
        b.push("a")
        b.push("b")
        b.push("c")
        b.overwrite("d")
        self.assertEqual(len(b), 3)
        self.assertEqual(b.pop(), "b")
        self.assertEqual(b.pop(), "c")
        self.assertEqual(b.pop(), "d")

    def test_overwrite_when_not_full_acts_like_push(self):
        b = CircularBuffer(3)
        b.push("a")
        b.overwrite("b")
        self.assertEqual(len(b), 2)
        self.assertEqual(b.pop(), "a")
        self.assertEqual(b.pop(), "b")

    def test_overwrite_multiple_wraps(self):
        b = CircularBuffer(2)
        b.overwrite(1)
        b.overwrite(2)
        b.overwrite(3)
        b.overwrite(4)
        self.assertEqual(b.pop(), 3)
        self.assertEqual(b.pop(), 4)
        self.assertTrue(b.is_empty())


class TestIteration(unittest.TestCase):
    def test_iterates_in_insertion_order(self):
        b = CircularBuffer(3)
        for i in (10, 20, 30):
            b.push(i)
        self.assertEqual(list(b), [10, 20, 30])

    def test_iter_after_partial_drain(self):
        b = CircularBuffer(3)
        b.push("a")
        b.push("b")
        b.push("c")
        b.pop()
        b.push("d")
        self.assertEqual(list(b), ["b", "c", "d"])

    def test_iter_empty(self):
        b = CircularBuffer(2)
        self.assertEqual(list(b), [])


class TestClear(unittest.TestCase):
    def test_clear_empties_buffer(self):
        b = CircularBuffer(3)
        b.push(1)
        b.push(2)
        b.clear()
        self.assertTrue(b.is_empty())
        self.assertEqual(len(b), 0)
        with self.assertRaises(IsEmptyError):
            b.pop()

    def test_clear_then_reuse(self):
        b = CircularBuffer(2)
        b.push("a")
        b.push("b")
        b.clear()
        b.push("c")
        self.assertEqual(b.pop(), "c")
        self.assertTrue(b.is_empty())


if __name__ == "__main__":
    unittest.main()
