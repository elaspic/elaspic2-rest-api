# elaspic2-rest-api

[![docs](https://img.shields.io/badge/docs-v0.1.5-blue.svg)](https://ostrokach.gitlab.io/elaspic2-rest-api/v0.1.5/)
[![pipeline status](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.5/pipeline.svg)](https://gitlab.com/elaspic/elaspic2-rest-api/commits/v0.1.5/)
[![coverage report](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.5/coverage.svg)](https://elaspic.gitlab.io/elaspic2-rest-api/v0.1.5/htmlcov/)

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

1. Build a Docker image.

    ```bash
    export CONDA_BLD_ARCHIVE_URL="https://gitlab.com/api/v4/projects/21459617/jobs/artifacts/master/download?job=build"

    docker build --build-arg CONDA_BLD_ARCHIVE_URL --tag registry.gitlab.com/elaspic/elaspic2-rest-api:latest .gitlab/docker/
    ```

1. Run the built Docker image.

    ```bash
    docker run --tty --env-file .env --env HOST_USER_ID=9284 \
        --env=GUNICORN_CMD_ARGS="--bind 0.0.0.0:8080 --workers 1" \
        registry.gitlab.com/elaspic/elaspic2-rest-api:latest
    ```
