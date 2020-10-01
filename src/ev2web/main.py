"""

The architecture of the REST API was heavily inspired by:
<http://restalk-patterns.org/long-running-operation-polling.html>.
"""
import asyncio

import sentry_sdk
from fastapi import FastAPI, HTTPException
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from ev2web import config, gitlab, utils
from ev2web.types import JobRequest, JobResponse, JobResult, JobState

app = FastAPI(
    title="ELASPIC v2",
    description="Version 2 of the ELASPIC pipeline (<http://elaspic.kimlab.org>).",
    version="0.1.0",
)


@app.post("/jobs/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, tags=["jobs"])
async def submit_job(*, input: JobRequest, request: Request, response: Response):
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
    if not utils.check_aa_sequence(input.protein_sequence):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Protein sequence is malformed",
        )
    if input.ligand_sequence is not None and not utils.check_aa_sequence(input.ligand_sequence):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ligand sequence is malformed",
        )
    if not utils.check_mutations(input.mutations):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutations are in an unexpected format",
        )
    if not utils.check_mutations_match_sequence(input.protein_sequence, input.mutations):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutation(s) do not match the protein sequence",
        )

    loop = asyncio.get_running_loop()
    job_id = await loop.run_in_executor(None, gitlab.create_job, input)

    web_url = f"{request.url}{job_id}/"
    response.headers["LOCATION"] = web_url
    return {"id": job_id, "web_url": web_url}


@app.get("/jobs/{job_id}", response_model=JobState, tags=["jobs"])
async def get_job_status(job_id: int, request: Request, response: Response):
    """Get the status of a previously-submitted job.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    try:
        job_state = await loop.run_in_executor(None, gitlab.get_job_state, job_id)
    except gitlab.GitlabHttpError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if job_state.status == "success":
        job_state.web_url = f"{request.url}/results"
        response.headers["LOCATION"] = job_state.web_url

    return job_state

    # TODO: Re-evaluate when get_job_result works.
    if job_state.status != "success":
        return job_state
    else:
        return RedirectResponse(url=job_state.web_url, status_code=status.HTTP_303_SEE_OTHER)


@app.delete("/jobs/{job_id}", tags=["jobs"])
async def delete_job(job_id: int):
    """Delete a previously-submitted job, including associated data.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, gitlab.delete_job, job_id)
    except (gitlab.GitlabHttpError, gitlab.GitlabDeleteError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/jobs/{job_id}/results", response_model=JobResult, tags=["jobs"])
async def get_job_result(job_id: int):
    """Get the result of a previously-submitted job.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    try:
        job_result = await loop.run_in_executor(None, gitlab.get_job_result, job_id)
    except gitlab.GitlabHttpError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return job_result


@app.get("/_ah/warmup", include_in_schema=False)
def warmup():
    return {}


@app.on_event("startup")
async def on_startup() -> None:
    pass


@app.on_event("shutdown")
async def on_shutdown() -> None:
    pass


if config.SENTRY_DSN:
    sentry_sdk.init(config.SENTRY_DSN, traces_sample_rate=1.0)
    app = SentryAsgiMiddleware(app)  # type: ignore
