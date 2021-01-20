# elaspic2-rest-api

[![docs](https://img.shields.io/badge/docs-v0.1.2-blue.svg)](https://ostrokach.gitlab.io/elaspic2-rest-api/v0.1.2/)
[![pipeline status](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.2/pipeline.svg)](https://gitlab.com/elaspic/elaspic2-rest-api/commits/v0.1.2/)
[![coverage report](https://gitlab.com/elaspic/elaspic2-rest-api/badges/v0.1.2/coverage.svg)](https://elaspic.gitlab.io/elaspic2-rest-api/v0.1.2/htmlcov/)

ELASPIC2 web server

## Development

To start the web server locally, source all environment variables hidden in the
`env_variables.yaml` configuration file, and then run the following command.

```bash
uvicorn elaspic2_rest_apit_api:app --reload --host 0.0.0.0
```

## Deployment

```bash
gcloud app deploy
```
