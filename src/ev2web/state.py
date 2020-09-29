from collections import deque
from typing import Any, Deque, Mapping

from ev2web.types import Job

engine: Any = None

# Use `deque.append()` and `deque.popleft()` atomic operations.
queues: Mapping[str, Deque[Job]] = dict(pending=deque(), working=deque(), finished=deque())
