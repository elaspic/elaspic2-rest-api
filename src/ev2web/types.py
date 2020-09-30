from enum import Enum
from typing import Any, List, Optional

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
    id: str
    location: str


class JobStatus(Enum):
    pending = "pending"
    running = "running"
    failed = "failed"
    succeeded = "succeeded"


class JobState(BaseModel):
    status: JobStatus
    submitted_utc_time: Optional[str]


class Mutation(BaseModel):
    mutation: str
    ev2score: float
    ev2seqscore: float
    ev2iscore: float
    ev2iseqscore: float
    errors: Optional[str]


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
    mutation_scores: List[Mutation]
