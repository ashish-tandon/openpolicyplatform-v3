# Data Flow Alignment & Validation

## Flow Map
- Scraper → Store Upsert (scrapers DB staging) → Core Upsert (app DB) → API Routers → UI Pages

## Endpoints and Schemas
- Scrapers Admin API: `/api/v1/scrapers/*`
  - Status, jobs list/toggle, run-now
- Dashboard API: `/api/v1/dashboard/*`
  - overview, system, scrapers, database
- Admin: `/api/v1/admin/*`
  - dashboard, status/unified, config/scraper, audit

## Environment
- `SCRAPER_SERVICE_ENABLED`
- `SCRAPERS_DATABASE_URL`
- Timeouts, retries, concurrency, scheduler defaults

## Alignment Checklist (10 passes)
1. Env vars present and documented
2. CLI arguments align with runners and K8s args
3. Runners fan out to registered scopes
4. Store upsert keys match canonical IDs (jurisdiction, entity_type, external_id)
5. API routers expose status/config with correct fields
6. UI calls endpoints and renders all fields
7. K8s CronJobs schedules map to scopes and modes
8. Metrics counters/histograms registered and labeled
9. Audit logs recorded for admin actions
10. CI validates k8s manifests and runs scraper tests

## Variable/Config Dependency Matrix
- If `SCRAPER_SERVICE_ENABLED` flips:
  - Admin endpoints enabled/disabled
  - UI displays enabled state and controls
- If `SCRAPERS_DATABASE_URL` changes:
  - Store/journal targets update
  - Documented in env and helm values

## Gateways and Health
- Health checks: `/api/v1/health`, `/api/v1/health/detailed`
- Ingress routes: `/` → web, `/api` → API

## Actions
- Keep this doc updated as new scopes/entities are registered
- Cross-reference services in `UNIFIED_SERVICE_REFERENCE.md` and `SERVICES_MATRIX.md`