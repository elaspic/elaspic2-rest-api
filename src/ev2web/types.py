from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class JobRequest(BaseModel):
    protein_sequence: str
    mutations: str
    ligand_sequence: Optional[str]
    structural_template: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "protein_sequence": "AAA",
                "mutations": "A1G,A1L",
            }
        }


class JobResponse(BaseModel):
    job_id: str
    job_url: str


class JobStatus(BaseModel):
    status: "JobState"


class JobState(Enum):
    pending = "pending"
    running = "running"
    failed = "failed"
    completed = "completed"


class JobResult(BaseModel):
    """The main job class populated throughout the job execution pipeline."""

    # Protein and mutation info
    protein_sequence: str
    mutations: str
    ligand_sequence: Optional[str]

    # Structural template
    query_start_pos: int
    query_end_pos: int
    alignment_query_sequence: str
    alignment_template_sequence: str
    structural_template: str
    homology_model: str

    # Mutation
    # mutation_scores: List["Mutation"]


class Mutation(BaseModel):
    mutation: str
    ev2score: float
    ev2seqscore: float
    ev2iscore: float
    ev2iseqscore: float
    message: Optional[str]
