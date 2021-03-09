import asyncio
import logging
from urllib.parse import urlencode

import aiohttp
from gitlab import GitlabHttpError

from elaspic2_rest_api import config
from elaspic2_rest_api.gitlab import get_job_state

logger = logging.getLogger(__name__)


GITLAB_PIPELINES_ENDPOINT = (
    f"{config.GITLAB_HOST_URL}/api/v4/projects/{config.GITLAB_PROJECT_ID}/pipelines"
)

KNOWN_REAL_FAILURES = set()


async def retry_failed_jobs_task():
    """Retry jobs that were prematurely marked as failed."""
    async with aiohttp.ClientSession() as session:
        while True:
            pipeline_infos = await get_pipeline_infos(session)
            pipeline_infos = await select_premature_failures(pipeline_infos)
            logger.info("Retrying %s pseudo-failed jobs", len(pipeline_infos))
            await retry_pipelines(session, pipeline_infos)
            await asyncio.sleep(300)


async def get_pipeline_infos(session, params=[("per_page", "100"), ("status", "failed")]):
    next_url = f"{GITLAB_PIPELINES_ENDPOINT}"
    if params:
        next_url += "?" + urlencode(params)
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


async def retry_pipelines(session, pipeline_infos):
    for pipeline_info in pipeline_infos:
        url = f"{GITLAB_PIPELINES_ENDPOINT}/{pipeline_info['id']}/retry"
        async with session.post(
            url, headers=[("PRIVATE-TOKEN", config.GITLAB_AUTH_TOKEN)]
        ) as response:
            assert response.ok


async def delete_pipelines(session, pipeline_infos):
    for pipeline_info in pipeline_infos:
        url = f"{GITLAB_PIPELINES_ENDPOINT}/{pipeline_info['id']}"
        async with session.delete(
            url, headers=[("PRIVATE-TOKEN", config.GITLAB_AUTH_TOKEN)]
        ) as response:
            assert response.ok


async def select_premature_failures(pipeline_infos):
    loop = asyncio.get_running_loop()

    select_pipeline_infos = []
    for pipeline_info in pipeline_infos:
        if pipeline_info["status"] != "failed":
            continue
        if pipeline_info["id"] in KNOWN_REAL_FAILURES:
            continue
        try:
            job_state, _ = await loop.run_in_executor(
                None, get_job_state, pipeline_info["id"], False
            )
        except GitlabHttpError:
            logger.error("Could not find jobs associated with pipeline %s", pipeline_infos["id"])
            continue
        if job_state.status == "failed":
            KNOWN_REAL_FAILURES.add(pipeline_info["id"])
            continue
        select_pipeline_infos.append(pipeline_info)
    return select_pipeline_infos
