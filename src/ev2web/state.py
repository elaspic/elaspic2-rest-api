from collections import deque
from typing import Any, Deque, Mapping

engine: Any = None

# Use `deque.append()` and `deque.popleft()` atomic operations.
queues: Mapping[str, Deque[str]] = dict(pending=deque(), working=deque(), finished=deque())
