# Multi-Repo Microservice Architecture and CI/CD

## Split service repos
- Each service has its own repo with code, `/docs`, Dockerfile, and config
- Service repos own their lint, test, build, and image push pipelines

## Umbrella (this) repo
- Acts as control plane: Helm chart, K8s manifests, centralized config, and deployment workflows
- Receives repository_dispatch events from service repos to deploy specific images/tags

## End-to-end flow
1) Developer merges PR to a service repo (api/web/scraper)
2) Service repo CI runs lint/tests, builds image, runs containerized tests, pushes image to GHCR
3) Service repo CI triggers repository_dispatch to this repo with { service, tag, optional digest }
4) This repo’s dispatch workflow runs Helm upgrade with the provided image tag/digest for that service
5) K8s performs atomic upgrade and readiness checks; old pods are drained

## Versioning
- Images tagged by git tags (e.g., v1.0.0)
- Helm Deployments/CronJobs annotated with `app.kubernetes.io/version`
- Optional image digests supported for immutable deploys

## Documentation and configuration
- Central config: `config/central-config.yaml`
- Health/readiness probes documented in `docs/operations/health-checks.md`
- Ports/allowed IPs enforced through central-config + middleware

## Testing
- Service repos: unit/integration and container tests before push
- Umbrella repo: fast unit admin tests; optional integration job with Postgres
- Pre-deploy validator script checks health + central-config compliance

## Rollback
- Helm `--atomic` ensures auto-rollback on failure
- Manual `helm rollback` supported