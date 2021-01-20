from pathlib import Path
from typing import Optional

import jinja2

from elaspic2_rest_api.types import JobRequest

_templates_env: Optional[jinja2.Environment] = None


def get_templates_env() -> jinja2.Environment:
    global _templates_env

    if _templates_env is None:
        templates_dir = Path(__file__).resolve(strict=True).parent.joinpath("templates")
        templates_loader = jinja2.FileSystemLoader(templates_dir)
        _templates_env = jinja2.Environment(
            loader=templates_loader, autoescape=jinja2.select_autoescape(["yaml"])
        )
    return _templates_env


def render_template(job_id: str, request: JobRequest, mutations_per_worker: int = 4) -> str:
    templates_env = get_templates_env()
    gitlab_ci_template = templates_env.get_template(".gitlab-ci.yml.j2")
    gitlab_ci_data = gitlab_ci_template.render(
        job_id=job_id,
        protein_sequence=request.protein_sequence,
        ligand_sequence=request.protein_sequence,
        structural_template=request.structural_template,
    )
    return gitlab_ci_data
