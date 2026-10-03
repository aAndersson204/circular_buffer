from typing import Any, Iterator, List, Optional


class IsFullError(Exception):
    """Raised when push() is called on a buffer at capacity.

    We raise rather than silently overwrite so that "push" preserves
    standard queue semantics; overwrite behaviour is requested via the
    explicit push_overwrite(). Keeping the two apart means a caller can
    opt into overwrite deliberately instead of discovering it through
    a silent data loss bug.
    """


class IsEmptyError(Exception):
    """Raised when pop() is called on a buffer with no items."""


class CircularBuffer:
    """Fixed-capacity ring buffer that overwrites the oldest entry when full.

    Design decisions, stated plainly:
      - Capacity is fixed at construction; growable buffers are a different
        problem and we deliberately do not solve it.
      - push() raises IsFullError when full. overwrite() forces an overwrite
        of the oldest item. These are two separate methods so the caller
        chooses the failure mode explicitly; this avoids the classic bug
        where a buffer silently drops data because someone forgot it wraps.
      - Storage is a pre-allocated list of size `capacity`, holding None in
        empty slots. We track count explicitly so __len__ is O(1) and so
        that we never confuse "slot contains None" with "slot is empty".
        (Storing None and checking for it would be ambiguous if callers
        pushed None as a real value; explicit count removes that ambiguity.)
      - Not thread-safe. If you need cross-thread coordination, wrap access
        in a lock at the call site. Adding internal locks would impose cost
        on the common single-threaded use case for a benefit we cannot
        guarantee in every runtime.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self._capacity: int = capacity
        self._buf: List[Optional[Any]] = [None] * capacity
        self._head: int = 0  # index of the oldest item, valid when non-empty
        self._count: int = 0  # number of items currently stored

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return self._count

    def is_empty(self) -> bool:
        return self._count == 0

    def is_full(self) -> bool:
        return self._count == self._capacity

    def push(self, item: Any) -> None:
        """Append item as the newest entry. Raise IsFullError if at capacity."""
        if self._count == self._capacity:
            raise IsFullError("buffer is full")
        tail = (self._head + self._count) % self._capacity
        self._buf[tail] = item
        self._count += 1

    def overwrite(self, item: Any) -> None:
        """Append item, overwriting the oldest entry if the buffer is full.

        When not full this behaves like push(). When full we write at the
        current tail position (which equals head) and advance head, so the
        oldest slot becomes the newest without any data movement.
        """
        if self._count < self._capacity:
            self.push(item)
            return
        self._buf[self._head] = item
        self._head = (self._head + 1) % self._capacity

    def pop(self) -> Any:
        """Remove and return the oldest entry. Raise IsEmptyError if empty."""
        if self._count == 0:
            raise IsEmptyError("buffer is empty")
        item = self._buf[self._head]
        self._buf[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._count -= 1
        return item

    def peek(self) -> Any:
        """Return the oldest entry without removing it. Raise IsEmptyError if empty."""
        if self._count == 0:
            raise IsEmptyError("buffer is empty")
        return self._buf[self._head]

    def clear(self) -> None:
        self._buf = [None] * self._capacity
        self._head = 0
        self._count = 0

    def __iter__(self) -> Iterator[Any]:
        for i in range(self._count):
            yield self._buf[(self._head + i) % self._capacity]
