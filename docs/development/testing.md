# Testing

- Backend: pytest (tests under `backend/tests`)
- Health checks: curl `/api/v1/health` and `/api/v1/health/detailed`
- Scrapers monitoring: validate presence of latest `scraper_test_report_*.json`
- CI: docs link check and OpenAPI export