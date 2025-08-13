# Kubernetes Operations

## Workloads
- API: Deployment, Service, Ingress
- Web: Deployment, Service, Ingress
- Scraper: CronJobs by scope (daily/bootstrap/special)

## Resources
- Use requests/limits per workload:
  - API: requests 100m/256Mi; limits 500m/512Mi; HPA 2-10, 70% CPU target
  - Web: requests 50m/128Mi; limits 200m/256Mi
  - Scrapers: requests 200m/256Mi; limits 1000m/1Gi

## Example: API Deployment (snippet)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 2
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/your-org/api:latest
          ports: [{ containerPort: 8000 }]
          envFrom:
            - secretRef: { name: openpolicy-secrets }
            - configMapRef: { name: openpolicy-config }
          resources:
            requests: { cpu: "100m", memory: "256Mi" }
            limits: { cpu: "500m", memory: "512Mi" }
```

## Example: Scraper CronJob (with limits)
```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: scrapers-daily-federal }
spec:
  schedule: "0 4 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: runner
              image: ghcr.io/your-org/scraper:dev
              args: ["python","-m","services.scraper.cli","--mode","daily","--scope","federal:*"]
              envFrom:
                - secretRef: { name: openpolicy-secrets }
                - configMapRef: { name: openpolicy-config }
              resources:
                requests: { cpu: "200m", memory: "256Mi" }
                limits: { cpu: "1000m", memory: "1Gi" }
```

## Secrets and Config
- ConfigMap: non-sensitive env (feature flags, timeouts)
- Secret: DATABASE_URL, tokens, credentials

## Observability
- Probes: readiness/liveness on `/api/v1/health`
- Metrics: expose `/metrics` via ServiceMonitor (Prometheus)
- Logs: ship with Fluent Bit/Vector to centralized store