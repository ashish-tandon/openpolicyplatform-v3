# Changelog

## [1.0.0] - 2025-08-13

### Added
- Scraper Service v1 scaffold: CLI, core modules (types/store/fetcher/metrics/scheduler), runners (daily/bootstrap/special), adapters stub
- Scraper Admin API: jobs list/toggle, run-now (background), service-status, audit logging, rate limiting, effective config endpoint
- Admin UI: Scrapers page (Jobs/Status/Logs/Failures tabs), Run All Daily, toasts; Dashboard StatCards, system/database panels, unified status, analytics hooks; Audit viewer page
- Kubernetes: CronJobs for daily/bootstraps (examples); resource requests/limits; concurrencyPolicy
- Helm chart: API/Web deployments, services, ingress; scraper CronJobs; image repo/tag/digest support; version annotations; imagePullPolicy/secrets
- Central configuration: config/central-config.yaml; loader and startup validation; IP allowlist middleware
- CI/CD: split unit/integration tests; deploy workflow with build/push, pre-deploy validation, atomic helm upgrade, scale-down policy
- Pre-deploy validator script: checks health endpoints and central-config compliance
- Scraper Dockerfile and image build/run docs

### Changed
- Backend API port configured via env (default 9001), documented health/readiness probes
- Tests: SQLite-backed fast unit/admin tests; admin tests cover new endpoints

### Security
- IP allowlist middleware driven by central config
- Admin actions audited to logs

### Documentation
- Deployment control policy and Helm deployment guide
- Scrapers run plan and data flow alignment
- Service readiness checklist and environment variables updates
- Per-service READMEs (API/Web/Scraper)

## [Unreleased]
- Add master execution plan, architecture diagram, data/variable flows
- Create canonical API docs (overview, endpoints, schemas, quick-reference)
- Add CI workflow for docs link check and OpenAPI export
- Implement startup guard (required envs, prod ALLOWED_* checks)
- Add configurable scraper directories and resilient logging
- Expand operations (runbooks, checklists, SLOs) and deployment docs

## 1.0.0 - Initial unified docs and API
- Baseline merge; initial FastAPI service