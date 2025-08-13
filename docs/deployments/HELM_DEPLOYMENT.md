# Helm Deployment for OpenPolicy

## Prerequisites
- Kubernetes cluster with Ingress controller
- Container registry access for images

## Values
- image.api, image.web, image.scraper
- resources.api, resources.web, resources.scraper
- scraper.enabled and scraper.schedules
- ingress.enabled, ingress.host, ingress.apiPath

## Install
```bash
helm upgrade --install openpolicy deploy/helm/openpolicy \
  --set image.api=ghcr.io/your-org/api:latest \
  --set image.web=ghcr.io/your-org/web:latest \
  --set image.scraper=ghcr.io/your-org/scraper:dev \
  --set ingress.enabled=true --set ingress.host=example.com
```

## Notes
- Set `SCRAPER_SERVICE_ENABLED=true` via ConfigMap/Secret for API when ready
- Apply scraper CronJobs by enabling `scraper.enabled=true` and configuring schedules

## Images and Versions
- Values support repo (`image.*`), tag (`imageTag.*`) and optional digest (`imageDigest.*`)
- Deployments/CronJobs annotate `app.kubernetes.io/version` for observability
- Use git tags to set `imageTag.*` in the deploy workflow