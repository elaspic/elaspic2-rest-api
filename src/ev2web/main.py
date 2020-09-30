"""

The architecture of the REST API was heavily inspired by:
<http://restalk-patterns.org/long-running-operation-polling.html>.
"""
import asyncio

import sentry_sdk
from fastapi import FastAPI, HTTPException
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette import status
from starlette.responses import RedirectResponse, Response

from ev2web import config, gitlab, utils
from ev2web.types import JobRequest, JobResponse, JobResult, JobState, JobStatus

app = FastAPI(
    title="ELASPIC v2",
    description="Version 2 of the ELASPIC pipeline (<http://elaspic.kimlab.org>).",
    version="0.1.0",
)


@app.post("/jobs/", response_model=JobResponse, status_code=202, tags=["jobs"])
async def submit_job(*, request: JobRequest, response: Response):
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
        raise HTTPException(status_code=400, detail="Mutations are in an unexpected format")
    if not utils.check_mutations_match_sequence(request.protein_sequence, request.mutations):
        raise HTTPException(status_code=400, detail="Mutation(s) do not match the protein sequence")

    job_id = utils.get_job_id(request.protein_sequence, request.ligand_sequence, request.mutations)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, gitlab.create_job, job_id, request)

    job_url = f"/jobs/{job_id}/"
    response.headers["LOCATION"] = job_url
    return {"id": job_id, "location": job_url}


@app.get("/jobs/{job_id}", response_model=JobState, tags=["jobs"])
async def get_job_status(job_id: str, response: Response):
    """Get the status of a previously-submitted job.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    job_state = await loop.run_in_executor(None, gitlab.get_job_state, job_id)
    if job_state.status != JobStatus.succeeded:
        return job_state
    else:
        redirect_url = f"/job/{job_id}/result"
        response.headers["Location"] = redirect_url
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.delete("/jobs/{job_id}", status_code=204, tags=["jobs"])
async def delete_job(job_id: str):
    """Delete a previously-submitted job, including associated data.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, gitlab.delete_job, job_id)


@app.get("/jobs/{job_id}/result", response_model=JobResult, tags=["jobs"])
async def get_job_result(job_id: str):
    """Get the result of a previously-submitted job.

    **Arguments:**

    - **job_id**: Identifier of the submitted job, as returned by the "Submit Job" endpoint.
    """
    loop = asyncio.get_running_loop()
    job_result = await loop.run_in_executor(None, gitlab.get_job_result, job_id)
    return job_result


@app.get("/_ah/warmup", include_in_schema=False)
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
    app = SentryAsgiMiddleware(app)  # type: ignore
