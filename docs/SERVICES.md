# Services

This document describes all services, their roles, ports, and key environment variables.

## postgres
- Role: primary data store
- Ports: 5432
- Volumes: `pgdata:/var/lib/postgresql/data`
- Init scripts: `docker/postgres-init/01-init.sql` creates `openpolicy_test`
- Env:
  - POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

## api
- Role: FastAPI backend
- Port: 8000
- Env:
  - DATABASE_URL (and APP_DATABASE_URL, SCRAPERS_DATABASE_URL, AUTH_DATABASE_URL)
  - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  - SECRET_KEY, ENVIRONMENT
- Depends on: postgres

## web
- Role: React frontend
- Port: 5173
- Env:
  - VITE_API_URL
- Depends on: api

## redis
- Role: job queue for scrapers
- Port: 6379

## scrapers-orchestrator
- Role: schedules and enqueues scraper jobs to Redis
- Port: 8010
- Env:
  - REDIS_URL
  - SCRAPER_QUEUE_KEY
  - ENABLED_SCRAPERS_PROD, ENABLED_SCRAPERS_TEST
  - {SCRAPER}_PROD_CRON, {SCRAPER}_TEST_CRON overrides
- Depends on: redis

## scrapers-worker
- Role: consumes jobs and executes scrapers; persists data
- Port: 8011
- Env:
  - REDIS_URL, SCRAPER_QUEUE_KEY
  - DATABASE_URL_MAIN, DATABASE_URL_TEST
  - MCP_ENABLED, MCP_ALLOW_INVALID
- Depends on: redis, postgres

## headless-browser
- Role: browserless Chrome for JS-heavy scrapers
- Port: 9222->3000
- Tuning:
  - MAX_CONCURRENT_SESSIONS, CONNECTION_TIMEOUT

## prometheus
- Role: metrics scraping
- Port: 9090
- Config: `backend/monitoring/prometheus.yml`

## grafana
- Role: dashboards
- Port: 3000
- Env:
  - GF_SECURITY_ADMIN_PASSWORD
- Provisioning: `backend/monitoring/grafana-provisioning` (datasources + dashboards)