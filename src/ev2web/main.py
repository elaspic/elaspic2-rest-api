from collections import deque
from typing import Any, Deque, Mapping, Optional

import sentry_sdk
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette import status
from starlette.responses import RedirectResponse, Response

from ev2web import config, gitlab, state, types, utils

# tags_metadata = [
#     {
#         "name": "jobs",
#         "description": "Manage items. So _fancy_ they have their own docs.",
#         "externalDocs": {
#             "description": "Items external docs",
#             "url": "https://fastapi.tiangolo.com/",
#         },
#     },
# ]

app = FastAPI(
    title="ELASPIC v2",
    description="Version 2 of the ELASPIC pipeline (<http://elaspic.kimlab.org>).",
    version="0.1.0",
    # openapi_tags=tags_metadata,
)


@app.post(
    "/jobs/",
    response_model=types.JobResponse,
    status_code=202,
    tags=["jobs"],
    summary="Submit a New Job",
)
async def create_job(*, request: types.JobRequest, response: Response):
    """
    Create a new job evaluating the effect of mutation(s) on the stability of a single protein
    for the affinity between two proteins.

    **Arguments:**

    - **protein_sequence**: Amino acid sequence of the protein being mutated.
    - **mutations**: One or more mutations to be evaluated.
        Multiple mutations should be separated with a comma.
    - **ligand_sequence**: Amino acid sequence of the interacting protein.
    - **structural_template**: Structural template to be used for modelling the structure
        of the protein or the interaction between the protein and the ligand. The template should
        be provided as a gzip-compressed, and base64-encoded, PDB or mmCIF file.
    """
    if not utils.check_aa_sequence(request.protein_sequence):
        raise HTTPException(status_code=400, detail="Protein sequence is malformed")
    if request.ligand_sequence is not None and not utils.check_aa_sequence(request.ligand_sequence):
        raise HTTPException(status_code=400, detail="Ligand sequence is malformed")
    if not utils.check_mutations(request.mutations):
        raise HTTPException(status_code=400, detail="Mutations are in an unsupported format")
    if not utils.check_mutations_match_sequence(request.protein_sequence, request.mutations):
        raise HTTPException(status_code=400, detail="Mutation(s) do not match the protein sequence")

    job_id = utils.get_job_id(request.protein_sequence, request.ligand_sequence, request.mutations)
    job_url = f"/jobs/{job_id}/"

    state.queues["pending"].append(job_id)

    response.headers["Location"] = job_url
    return {"job_id": job_id, "job_url": job_url}


@app.get(
    "/jobs/{job_id}",
    response_model=types.JobStatus,
    tags=["jobs"],
    summary="Get Job Status",
)
async def read_job_status(job_id: str):
    result = dict(
        id=job_id,
        status=["pending", "done"],
        progress="0",
        submitted_utc_time="",
    )
    return RedirectResponse(url=f"/job/{job_id}/result", status_code=status.HTTP_303_SEE_OTHER)


@app.delete(
    "/jobs/{job_id}",
    tags=["jobs"],
    summary="Delete Job",
)
async def delete_job(job_id: str):
    """Delete job and data associated with the given `job_id`."""
    gitlab.delete_job(job_id)


@app.get(
    "/jobs/{job_id}/result",
    response_model=types.JobResult,
    tags=["jobs"],
    summary="Get Job Result",
)
async def read_job_status(job_id: str):
    result = dict(
        id=job_id,
        status=["pending", "done"],
        progress="0",
        submitted_utc_time="",
    )
    return RedirectResponse(url=f"/job/{job_id}/result", status_code=status.HTTP_303_SEE_OTHER)


@app.get(
    "/_ah/warmup",
    status_code=200,
    include_in_schema=False,
)
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
