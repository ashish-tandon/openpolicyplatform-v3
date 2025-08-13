# Testing

- Backend: pytest (tests under `backend/tests`)
- Health checks: curl `/api/v1/health` and `/api/v1/health/detailed`
- Scrapers monitoring: validate presence of latest `scraper_test_report_*.json`
- CI: docs link check and OpenAPI export
## Scraper Service Testing
- Unit: normalizers & store (≥95% branch for parsers)
- Contract: source payload fixtures
- Integration: pipeline on fixtures (ephemeral DB)
- E2E (dev): limited real runs under feature flag