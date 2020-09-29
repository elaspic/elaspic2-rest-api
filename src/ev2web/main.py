from collections import deque
from typing import Any, Deque, Mapping, Optional

import sentry_sdk
from fastapi import FastAPI
from pydantic import BaseModel
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette import status
from starlette.responses import RedirectResponse, Response

from ev2web import config, gitlab, types, utils

tags_metadata = [
    {
        "name": "jobs",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(
    title="ELASPIC v2",
    description="Version 2 of the ELASPIC pipeline (http://elaspic.kimlab.org).",
    version="0.1.0",
    openapi_tags=tags_metadata,
)


@app.post(
    "/jobs/",
    tags=["jobs"],
    response_model=types.JobSubmission,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_job(*, request: types.JobRequest, response: Response):
    # Validation
    if not utils.check_aa_sequence(request.protein_sequence):
        return {"status": "Error", "message": "Protein sequence is malformed."}
    if not utils.check_aa_sequence(request.protein_sequence):
        return {"status": "Error", "message": "Ligand sequence is malformed."}
    if not utils.check_mutations(request.mutations):
        return {"status": "Error", "message": "Mutations are in an unsupported format."}
    if not utils.mutation_matches_sequence(request.protein_sequence, request.mutations):
        return {"status": "Error", "message": "Mutation(s) do not match the protein sequence."}

    job_id = utils.get_job_id(request.protein_sequence, request.ligand_sequence, request.mutations)
    job_location = f"/jobs/{job_id}/"

    # Enqueue job
    job = JobContainer(job_id=job_id, **dict(request))
    queues["pending"].append(job)

    response.headers["Location"] = job_location
    return {"status": "Submitted", "job_id": job_id, "job_location": job_location}


@app.get("/jobs/{job_id}", tags=["jobs"], response_model=types.JobStatus)
async def read_job_status(job_id: str):
    result = dict(
        id=job_id,
        status=["pending", "done"],
        progress="0",
        submitted_utc_time="",
    )
    return RedirectResponse(url=f"/job/{job_id}/result", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/jobs/{job_id}/result", tags=["jobs"], response_model=types.JobStatus)
async def read_job_result(job_id: str):
    result = dict(
        id=job_id,
        status=["pending", "done"],
        progress="0",
        submitted_utc_time="",
    )
    return RedirectResponse(url=f"/job/{job_id}/result", status_code=status.HTTP_302_FOUND)
    pass


@app.delete("/jobs/{job_id}", tags=["jobs"])
async def delete_job_1(job_id: str):
    return gitlab.delete_job(job_id)


@app.delete("/jobs/{job_id}/result", tags=["jobs"])
async def delete_job_2(job_id: str):
    return gitlab.delete_job(job_id)


@app.get("/_ah/warmup", status_code=status.HTTP_200_OK)
def warmup():
    # Handle your warmup logic here, e.g. set up a database connection pool
    return {}


@app.on_event("startup")
async def on_startup() -> None:
    pass


@app.on_event("shutdown")
async def on_shutdown() -> None:
    pass


if config.SENTRY_DSN:
    sentry_sdk.init(config.SENTRY_DSN)
    app = SentryAsgiMiddleware(app)  # typing: ignore
