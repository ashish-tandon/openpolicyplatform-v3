# Health Checks and Diagnostics

Service: FastAPI backend (`backend/api`)

## Endpoints
- `/api/v1/health` (liveness)
- `/api/v1/health/detailed` (readiness)

## Kubernetes Probes (API)
```yaml
livenessProbe:
  httpGet: { path: /api/v1/health, port: 9001 }
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /api/v1/health/detailed, port: 9001 }
  initialDelaySeconds: 5
  periodSeconds: 10
```

Service: Scraper CLI jobs (CronJobs)
- Use job completion and exit codes; optional /metrics endpoint if long-running worker is added.

Service: Web
- `/` serves HTML; use HTTP 200 for liveness.
```yaml
livenessProbe:
  httpGet: { path: /, port: 80 }
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /, port: 80 }
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Parameters and interpretations
- Status levels: `healthy`, `