# CI/CD Guide

## CI (GitHub Actions)
- Workflows:
  - tests.yml: lint, type-check, unit/integration tests, scraper tests, docs link check, OpenAPI export
  - docs-openapi.yml: publish OpenAPI artifacts
- Optional steps: Docker image builds in CI, k8s manifest dry-run validation

## CD (Proposed)
- On tag push (v*):
  - Build and push images to ghcr.io
  - Create a GitHub Release with changelog
  - Deploy to staging (kubectl apply)
  - Manual approval gate
  - Deploy to production

## Environments/Secrets
- Store container registry credentials, database URLs, API keys in GitHub Secrets
- Use environment protection rules for staging/prod

## Versioning
- Semantic versioning
- Automate changelog generation