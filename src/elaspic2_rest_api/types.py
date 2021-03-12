from typing import Optional

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
                "mutations": "G1A,G1C",
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


class MutationResult(BaseModel):
    mutation: Optional[str]
    protbert_core: Optional[float]
    proteinsolver_core: Optional[float]
    el2core: Optional[float]
    protbert_interface: Optional[float]
    proteinsolver_interface: Optional[float]
    el2interface: Optional[float]
    error_message: Optional[str]
