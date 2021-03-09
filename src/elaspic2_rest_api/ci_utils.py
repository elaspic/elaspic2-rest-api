import asyncio
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def return_on_call(function_path: str):
    """Exit called process when function defined by "function_path" is called."""

    class CustomException(Exception):
        pass

    def return_on_call_(unused_duration):
        raise CustomException()

    with patch(function_path, return_on_call_):
        try:
            yield
        except CustomException:
            pass


def mock_await(*args, **kwargs):
    f = asyncio.Future()
    f.set_result(1)
    return f
