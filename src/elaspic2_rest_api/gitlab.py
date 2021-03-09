import json
import math
from typing import List, Optional, Tuple

import gitlab
from gitlab import GitlabDeleteError, GitlabHttpError  # noqa
from gitlab.exceptions import GitlabGetError
from requests.exceptions import ChunkedEncodingError

from elaspic2_rest_api import config
from elaspic2_rest_api.types import JobRequest, JobState, MutationResult


def batch_mutations(mutations: str, batch_size: int = 4, max_chunks: int = 50) -> List[str]:
    mutation_list = mutations.split(",")
    batch_size = max(batch_size, math.ceil(len(mutation_list) / max_chunks))

    mutation_batches: List[str] = []
    for mutation in mutation_list:
        if len(mutation_batches) == 0 or len(mutation_batches[-1].split(",")) >= batch_size:
            mutation_batches.append(mutation)
        else:
            mutation_batches[-1] += f",{mutation}"
    return mutation_batches


def create_job(request: JobRequest) -> int:
    # mutation_batches = batch_mutations(request.mutations)
    # mutation_variables = [
    #     {"key": f"MUTATIONS_{i}", "value": request.mutations}
    #     for i, mutations in enumerate(mutation_batches)
    # ]
    variables = [
        {"key": "PROTEIN_STRUCTURE_URL", "value": request.protein_structure_url},
        {"key": "PROTEIN_SEQUENCE", "value": request.protein_sequence},
        {"key": "MUTATIONS", "value": request.mutations},
        {"key": "LIGAND_SEQUENCE", "value": request.ligand_sequence},
    ]
    with gitlab.Gitlab(config.GITLAB_HOST_URL, config.GITLAB_AUTH_TOKEN) as gl:
        project = gl.projects.get(config.GITLAB_PROJECT_ID)
        pipeline = project.pipelines.create({"ref": "master", "variables": variables})
    return pipeline.id


def delete_job(job_id: int) -> None:
    with gitlab.Gitlab(config.GITLAB_HOST_URL, config.GITLAB_AUTH_TOKEN) as gl:
        project = gl.projects.get(config.GITLAB_PROJECT_ID)
        project.pipelines.delete(job_id)


def get_job_state(
    job_id: int, collect_results: bool = False
) -> Tuple[JobState, Optional[List[MutationResult]]]:
    with gitlab.Gitlab(config.GITLAB_HOST_URL, config.GITLAB_AUTH_TOKEN) as gl:
        project = gl.projects.get(config.GITLAB_PROJECT_ID)
        pipeline = project.pipelines.get(job_id)

        try:
            pipeline_job = next(
                (
                    j
                    for j in pipeline.jobs.list()
                    if j.name == "predict-mutation-effect" and j.status == pipeline.status
                )
            )
        except StopIteration:
            raise GitlabHttpError

        job = project.jobs.get(pipeline_job.id, lazy=True)

        try:
            input_data = job.artifact("result/input.json")
        except GitlabGetError:
            input_data = None

        if collect_results:
            try:
                output_data = job.artifact("results/results.jsonl")
            except ChunkedEncodingError:
                raise GitlabHttpError

    job_state = JobState(
        id=pipeline.id,
        status="pending" if pipeline.status == "failed" and not input_data else pipeline.status,
        created_at=pipeline.created_at,
        started_at=pipeline.started_at,
        finished_at=pipeline.finished_at,
    )
    job_result = (
        [json.loads(line) for line in output_data.strip().split(b"\n") if line.strip()]
        if collect_results
        else None
    )

    return job_state, job_result
