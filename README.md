# elaspic2-web

[![conda](https://img.shields.io/conda/dn/ostrokach-forge/elaspic2-web.svg)](https://anaconda.org/ostrokach-forge/elaspic2-web/)
[![docs](https://img.shields.io/badge/docs-vv0.1.0-blue.svg)](https://ostrokach.gitlab.io/elaspic2-web/vv0.1.0/)
[![pipeline status](https://gitlab.com/elaspic/elaspic2-web/badges/vv0.1.0/pipeline.svg)](https://gitlab.com/elaspic/elaspic2-web/commits/vv0.1.0/)
[![coverage report](https://gitlab.com/elaspic/elaspic2-web/badges/vv0.1.0/coverage.svg)](https://elaspic.gitlab.io/elaspic2-web/vv0.1.0/htmlcov/)

ELASPIC2 web server

## Development

To start the web server locally, source all environment variables hidden in the
`env_variables.yaml` configuration file, and then run the following command.

```bash
uvicorn elaspic2web:app --reload --host 0.0.0.0
```
