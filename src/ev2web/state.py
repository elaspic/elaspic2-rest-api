import concurrent.futures
from collections import deque
from typing import Deque, Mapping

#: Thread pool for running tasks that may otherwise block the event loop
thread_pool: concurrent.futures.Executor

#: Use `deque.append()` and `deque.popleft()` atomic operations.
queues: Mapping[str, Deque[str]] = dict(pending=deque(), working=deque(), finished=deque())
