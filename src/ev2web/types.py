from typing import List, Optional

from pydantic import BaseModel


class Job(BaseModel):
    """The main job class populated throughout the job execution pipeline."""

    # Protein and mutation info
    job_id: str
    protein_sequence: str
    ligand_sequence: Optional[str]
    mutations: str

    # Structural template
    query_start_pos: int
    query_end_pos: int
    alignment_query_sequence: str
    alignment_template_sequence: str
    template_structure: str
    model_stricture: str

    # Mutation
    mutation_scores: List["Mutation"]


class Mutation(BaseModel):
    mutation: str
    ev2score: float
    ev2seqscore: float
    ev2iscore: float
    ev2iseqscore: float


class JobRequest(BaseModel):
    protein_sequence: str
    ligand_sequence: Optional[str]
    mutations: str
    template_structure: Optional[str]


class JobSubmission(BaseModel):
    status: str
    job_id: Optional[str]
    job_url: Optional[str]
    message: Optional[str]


class JobStatus(BaseModel):
    job_id: str
    status: str
