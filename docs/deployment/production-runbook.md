# Production Runbook (Expanded)

## Deployment Plan
- Environments: development, staging, production
- Artifacts: backend API container, web frontend container, scraper service container
- Steps:
  1) Bump version, update CHANGELOG
  2) CI builds and pushes images to registry
  3) Apply database migrations
  4) Deploy backend and web via Kubernetes manifests/Helm
  5) Keep `SCRAPER_SERVICE_ENABLED=false` until scrapers verified
  6) Gradually enable CronJobs per scope

## CI/CD Plan
- CI: lint, type-check, unit/contract/integration tests; export OpenAPI; upload artifacts
- CD: on tag push, build and push Docker images; apply k8s manifests in staging; manual approval for production

## Kubernetes Plan
- Namespaces: staging, production
- Components:
  - API: Deployment + Service + Ingress
  - Web: Deployment + Service + Ingress
  - Scrapers: CronJobs per scope
- Resource management: set requests/limits per workload; configure HPA for API
- Secrets/Config: use ConfigMap for non-secret env, Secret for credentials

## Resource Management Plan
- API: requests cpu=100m, mem=256Mi; limits cpu=500m, mem=512Mi; HPA: minReplicas=2, maxReplicas=10, targetCPUUtilization=70%
- Web: requests cpu=50m, mem=128Mi; limits cpu=200m, mem=256Mi
- Scraper CronJobs: requests cpu=200m, mem=256Mi; limits cpu=1000m, mem=1Gi; concurrencyPolicy: Forbid; backoffLimit: 2

## Testing Strategy
- Unit tests per service (API, Web utilities, Scraper modules)
- Contract tests for source payloads (scraper)
- Integration tests: API routes, scraper pipeline on fixtures
- End-to-end: health endpoints and key UI flows

## Rollback Plan
- Keep previous image tags
- `kubectl rollout undo deployment/api`
- Disable problematic CronJobs quickly by scaling to 0 or deleting the CronJob