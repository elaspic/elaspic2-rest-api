import asyncio
import logging

import aiohttp

from elaspic2_rest_api import config
from elaspic2_rest_api.gitlab import get_job_state

logger = logging.getLogger(__name__)


async def retry_failed_jobs_task():
    """Retry jobs that were prematurely marked as failed."""
    async with aiohttp.ClientSession() as session:
        while True:
            pipeline_infos = await get_pipeline_infos(session)
            pipeline_infos = await select_premature_failures(pipeline_infos)
            logger.info("Retrying %s pseudo-failed jobs", len(pipeline_infos))
            await retry_pipelines(session, pipeline_infos)
            await asyncio.sleep(300)


async def get_pipeline_infos(session):
    next_url = (
        f"{config.GITLAB_HOST_URL}/api/v4/projects/{config.GITLAB_PROJECT_ID}/pipelines"
        "?per_page=100&status=failed"
    )
    pipeline_infos = []
    while next_url is not None:
        async with session.get(
            next_url, headers=[("PRIVATE-TOKEN", config.GITLAB_AUTH_TOKEN)]
        ) as response:
            pipeline_infos += await response.json()
            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                next_url = None
    return pipeline_infos


async def select_premature_failures(pipeline_infos):
    select_pipeline_infos = []
    for pipeline_info in pipeline_infos:
        if pipeline_info["status"] != "failed":
            continue
        job_state, _ = await get_job_state(pipeline_info["id"], collect_results=False)
        if job_state.status == "failed":
            continue
        select_pipeline_infos.append(select_pipeline_infos)
    return select_pipeline_infos


async def retry_pipelines(session, pipeline_infos):
    for pipeline_info in pipeline_infos:
        url = (
            f"https://gitlab.com/api/v4/projects/{config.GITLAB_PROJECT_ID}/pipelines/"
            f"{pipeline_info['id']}/retry"
        )
        async with session.post(
            url, headers=[("PRIVATE-TOKEN", config.GITLAB_AUTH_TOKEN)]
        ) as response:
            assert response.ok


async def delete_pipelines(session, pipeline_infos):
    for pipeline_info in pipeline_infos:
        url = (
            f"https://gitlab.com/api/v4/projects/{config.GITLAB_PROJECT_ID}/pipelines/"
            f"{pipeline_info['id']}"
        )
        async with session.delete(
            url, headers=[("PRIVATE-TOKEN", config.GITLAB_AUTH_TOKEN)]
        ) as response:
            assert response.ok
