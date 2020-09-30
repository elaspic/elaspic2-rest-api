import os
from typing import Optional

HOST_URL: str = os.getenv("HOST_URL", "")

GITLAB_HOST_URL: str = os.getenv("GITLAB_HOST_URL", "https://gitlab.com")

GITLAB_PROJECT_ID: int = int(os.getenv("GITLAB_PROJECT_ID", "21481523"))

GITLAB_AUTH_TOKEN: Optional[str] = os.getenv("GITLAB_CI_TOKEN")

SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
