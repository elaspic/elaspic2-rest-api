from typing import List, Optional

from pydantic import BaseModel


class JobRequest(BaseModel):
    protein_structure_url: str
    protein_sequence: str
    mutations: str
    ligand_sequence: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "protein_structure_url": "https://files.rcsb.org/download/1MFG.pdb",
                "protein_sequence": (
                    "GSMEIRVRVEKDPELGFSISGGVGGRGNPFRPDDDGIFVTRVQPEGPASKLLQPGDKIIQA"
                    "NGYSFINIEHGQAVSLLKTFQNTVELIIVREVSS"
                ),
                "mutations": "A1G,A1L",
                "ligand_sequence": "EYLGLDVPV",
            }
        }


class JobResponse(BaseModel):
    id: str
    web_url: str


class JobState(BaseModel):
    id: int
    status: str
    created_at: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]
    web_url: Optional[str]


class Mutation(BaseModel):
    mutation: str
    ev2_score: float
    ev2seq_score: float
    rosetta_score: float
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
