# Data Flow Plan

## Sources
- Scrapers (reports/logs, optional DB writes)
- PostgreSQL (canonical persisted data)

## Ingestion
- Scrapers collect data → write to staging (files) and/or DB tables
- Reports/logs: `scraper_test_report_*.json`, `collection_report_*.json`, `*.log`

## Storage
- PostgreSQL schema (key tables): `core_politician`, `bills_bill`, `hansards_statement`, `core_organization`, `core_membership`, `bills_membervote`

## Serving
- FastAPI reads from DB for policies/data endpoints
- FastAPI reads reports/logs for scrapers/monitoring endpoints
- Frontend consumes API only (`VITE_API_URL`)

## Flows
1. Scrape run → report generated → API `/api/v1/scrapers/*` reflects status
2. Data load/migration → DB updated → API `/api/v1/*` surfaces data
3. Admin operations (backup/restart) → logs/files → API returns confirmation and log info

## Contracts
- API contract: `docs/api/endpoints.md` + `docs/api/schemas.md`
- Report shapes: fields used by API (`summary`, `detailed_results` with `name`, `category`, `status`, `timestamp`, `records_collected`, `error_count`)

## SLAs
- Health endpoints available 99.9%
- Policy list/search P95 < 500ms (with caching)

## Observability
- Health: `/api/v1/health/*`
- Logs: `/api/v1/admin/logs`, `/api/v1/scrapers/logs`

## Failure modes & handling
- DB unavailable → `detailed` health shows `unhealthy`, API returns 5xx for DB-backed routes
- Missing reports → scraper health returns `warning` with last known info
- High CPU/memory/disk → health escalates to `warning`/`unhealthy`