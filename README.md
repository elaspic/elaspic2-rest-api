# elaspic2-rest-api

[![docs](https://img.shields.io/badge/docs-v0.1.4-blue.svg)](https://ostrokach.gitlab.io/elaspic2-rest-api/v0.1.4/)
[![pipeline status](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.4/pipeline.svg)](https://gitlab.com/elaspic/elaspic2-rest-api/commits/v0.1.4/)
[![coverage report](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.4/coverage.svg)](https://elaspic.gitlab.io/elaspic2-rest-api/v0.1.4/htmlcov/)

ELASPIC2 web server

## Development

To create a development environment, run the following:

```bash
python scripts/meta_to_env.py -f .gitlab/conda/meta.yaml > environment.yaml
mamba env create -f environment.yaml -p .venv/
mamba env update -f environment-dev.yaml -p .venv/
conda activate .venv/
```

To update the dev environment and the `meta.yaml` file:

```bash
conda activate .env/
conda update --all
./scripts/env_to_meta.py -f .gitlab/conda/meta.yaml
```

To start the web server locally, source all environment variables hidden in the
`env_variables.yaml` configuration file, and then run the following command.

```bash
uvicorn elaspic2_rest_apit_api:app --reload --host 0.0.0.0
```

## Deployment

```bash
gcloud app deploy
```
