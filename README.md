# Circular Buffer

A fixed-capacity ring buffer for Python. Once full, it can either raise on push or overwrite the oldest entry, depending on which method you call.

```python
from circular_buffer import CircularBuffer, IsFullError, IsEmptyError

buf = CircularBuffer(3)
buf.push("a")
buf.push("b")
buf.push("c")

# push() refuses to lose data; overwrite() does it deliberately
try:
    buf.push("d")
except IsFullError:
    buf.overwrite("d")  # drops "a", buffer is now ["b", "c", "d"]

print(buf.peek())   # "b"
print(buf.pop())   # "b"
print(buf.pop())   # "c"
print(buf.pop())   # "d"
```

## Why this exists

The problem is bounded queues: you have a stream of items, you want to keep the most recent N, and you do not want the memory footprint to grow unboundedly. A ring buffer gives you O(1) push and pop at a fixed memory cost.

The trade-off is that data is lost when the buffer wraps. Rather than picking silently between "drop on the floor" and "raise an error", this library exposes both behaviours explicitly: `push()` raises `IsFullError` so a bug that overflows surfaces loudly, and `overwrite()` is the deliberate opt-in to discarding the oldest item. Choose the one that matches your intent.

## Edge case worth knowing

`None` is a perfectly valid value to store. The buffer tracks occupancy with an explicit count rather than by checking slots for `None`, so pushing `None` and popping it back works as you would expect. If you need a sentinel for "no value", use a distinct object you control rather than reusing `None`.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
