# Architecture Overview

## Components
- API (FastAPI): business logic, authentication, REST API, metrics
- Web (React): user interfaces
- Postgres: primary data store (plus test database for scrapers)
- Redis: job queue
- Orchestrator: schedules and enqueues scraper jobs
- Worker: executes scrapers, validates (MCP), persists, emits metrics
- Monitoring: Prometheus + Grafana

## Data Flow
1. Orchestrator enqueues jobs to `SCRAPER_QUEUE_KEY` (Redis) with `mode` and `tasks`.
2. Worker consumes jobs, selects DB engine based on `mode`.
3. Worker runs scraper implementations:
   - Validates results via MCP stub (toggleable).
   - Writes via idempotent upserts to Postgres.
   - Emits Prometheus metrics for jobs, tasks, and durations.
4. API serves data and emits metrics for Prometheus.
5. Grafana visualizes metrics using Prometheus datasource.

## Scrapers
- Registered in `scrapers/registry.py` with default tasks and cron schedules.
- Implementations:
  - `federal_parliament`: internal scraper (requests + bs4)
  - `represent_opennorth_ref`: external API adapter
  - Planned: `opencivicdata/scrapers-ca`, `openparliament` historic import

## Dual-DB Strategy
- Test mode writes to `openpolicy_test` to allow safe validation and load testing.
- Prod mode writes to `openpolicy`.
- Orchestrator schedules both modes independently.

## Configuration
- Centralized via `.env` and `docker-compose.yml`.
- Per-scraper cron overrides supported via env.

## Observability
- Prometheus scrapes API, orchestrator, worker.
- Grafana dashboard provided for scraper KPIs.