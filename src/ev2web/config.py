import os
from collections import deque
from typing import Any, Optional

# Settings
DB_CONNECTION_STRING: Optional[str] = os.getenv("DB_CONNECTION_STRING")
SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

# Global variables
engine: Any = None
