# Backend API Service

## Purpose
FastAPI-based backend providing REST endpoints for policies, scrapers admin, dashboard, and health.

## Ports
- Default: 9001 (override with `API_PORT`)

## Endpoints
- `/api/v1/health`, `/api/v1/health/detailed`
- `/api/v1/scrapers/*` (monitoring + admin service endpoints)
- `/api/v1/dashboard/*`
- `/api/v1/admin/*`

## Inputs
- Env vars: see `docs/operations/environment-variables.md`
- Central config: `config/central-config.yaml`

## Outputs
- JSON REST responses
- Audit logs under `backend/logs/admin_audit.log`

## Tests
```bash
# Fast unit tests
cd backend && pytest -q tests
# Admin API tests
pytest -q backend/tests/api/test_scraper_admin.py
```

## Run (dev)
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 9001 --reload
```