# Comprehensive Testing Plan

## Services Covered
- Backend API
- Web Frontend
- Scraper Service

## Unit Tests
- API: routers, middleware, dependencies (mock DB)
- Web: components/util hooks (JSDOM/dom-testing-library)
- Scraper: normalizers, store, adapters (fixtures)

## Contract Tests
- Scraper source payload schema validation (fixtures)
- API response schema validation (OpenAPI-based where possible)

## Integration Tests
- API: route flows with in-memory or test DB
- Scraper: pipeline on fixtures with ephemeral DB
- Web: API integration via mocked fetch

## End-to-End Tests
- Health endpoints, admin login, dashboard navigation
- Scraper admin run-now flow (feature-flag enabled in test env)

## Performance/Load
- API: basic load and p95 latency thresholds
- Scrapers: rate limiting and concurrency behavior in dry-run mode

## CI Matrix
- Python 3.11, Node 18
- Fast paths for docs-only changes

## Coverage Targets
- API: >=70% lines, critical paths 90%
- Scraper parsers/normalizers: >=95% branches
- Web: >=60% lines on shared libs