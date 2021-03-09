from unittest.mock import MagicMock

import aiohttp
import pytest

from elaspic2_rest_api import gitlab_monitor
from elaspic2_rest_api.ci_utils import return_on_call


@pytest.mark.asyncio
async def test_retry_failed_jobs_task():
    with return_on_call("elaspic2_rest_api.gitlab_monitor.asyncio.sleep"):
        await gitlab_monitor.retry_failed_jobs_task()


@pytest.mark.asyncio
async def test_get_pipeline_infos():
    async with aiohttp.ClientSession() as session:
        pipeline_infos = await gitlab_monitor.get_pipeline_infos(session, params=[])
    assert len(pipeline_infos) > 0
    print(len(pipeline_infos))


@pytest.mark.asyncio
async def test_retry_pipelines():
    mock_session = MagicMock()
    pipelines = [{"id": 0}, {"id": 1}]
    await gitlab_monitor.retry_pipelines(mock_session, pipelines)
    mock_session.post.assert_called()


@pytest.mark.asyncio
async def test_delete_pipelines():
    mock_session = MagicMock()
    pipelines = [{"id": 0}, {"id": 1}]
    await gitlab_monitor.delete_pipelines(mock_session, pipelines)
    mock_session.delete.assert_called()
