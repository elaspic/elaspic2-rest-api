import asyncio
from functools import partial
from unittest.mock import patch

import pytest

import elaspic2_rest_api
from elaspic2_rest_api.ci_utils import return_on_call


@pytest.mark.asyncio
@patch("elaspic2_rest_api.tasks.monitor_tasks")
async def test_start_and_monitor_tasks(mock_monitor_tasks):
    with patch("elaspic2_rest_api.tasks.task_coros", {"test_coro": partial(asyncio.sleep, 10)}):
        await elaspic2_rest_api.tasks.start_and_monitor_tasks()
        mock_monitor_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_monitor_tasks():
    async def test_coro_bad():
        raise ValueError("Test exception!")

    async def test_coro_good():
        return "done!"

    tasks = {"test_coro": asyncio.create_task(test_coro_bad(), name="test_coro")}
    await asyncio.sleep(0.1)

    with patch("elaspic2_rest_api.tasks.task_coros", {"test_coro": test_coro_good}), return_on_call(
        "elaspic2_rest_api.gitlab_monitor.asyncio.sleep"
    ):
        await elaspic2_rest_api.tasks.monitor_tasks(tasks)
    await asyncio.sleep(0.1)

    task = tasks["test_coro"]
    result = task.result()
    task.cancel()
    assert result == "done!"
