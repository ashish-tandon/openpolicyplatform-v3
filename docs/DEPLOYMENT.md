# Deployment Guide

This document describes how to deploy the Open Policy Platform services and scrapers.

## Prerequisites
- Docker and Docker Compose
- A host with at least 4 CPU, 8 GB RAM
- Outbound internet access (for scrapers and monitoring)

## Environment Variables
Copy `.env.example` to `.env` and adjust values.

Key variables:
- SECRET_KEY
- DATABASE_URL (Postgres connection)
- REDIS_URL
- ENABLED_SCRAPERS_PROD / ENABLED_SCRAPERS_TEST
- DATABASE_URL_MAIN / DATABASE_URL_TEST

## Services

- postgres
- api
- web
- redis
- scrapers-orchestrator
- scrapers-worker
- headless-browser (optional)
- prometheus
- grafana

## First Run

1) Initialize repository
```bash
git clone <your_repo>
cd <repo>
cp .env.example .env
```

2) Start the stack
```bash
docker compose up -d --build
```

3) Verify health
- API: http://localhost:8000/health
- Orchestrator: http://localhost:8010/health
- Worker: http://localhost:8011/health
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

## Scraper Modes and Databases
- Production: persists to `openpolicy`
- Test: persists to `openpolicy_test` (auto-created)
- Orchestrator enqueues jobs with `mode` flag; worker routes DB accordingly.

## Enabling Scrapers
- Edit docker-compose (or env) to set:
```
ENABLED_SCRAPERS_PROD=federal_parliament
ENABLED_SCRAPERS_TEST=federal_parliament,represent_opennorth_ref
```
- Override schedules via env, e.g. `FEDERAL_PARLIAMENT_TEST_CRON="*/30 * * * *"`.

## Observability
- Prometheus scrapes metrics from API, orchestrator, and worker.
- Grafana is pre-provisioned with a Prometheus datasource and a sample scrapers dashboard.

## Security
- Change `SECRET_KEY` for production.
- Put Grafana behind authentication and change admin password.
- Add rate limits and IP allowlists as needed at the reverse proxy.

## Backups
- Mount `pgdata` to persistent storage.
- Use pg_dump or logical backups on a schedule.

## Upgrades
- Pull latest images, re-run `docker compose up -d --build`.

## Troubleshooting
- Check service logs: `docker compose logs -f <service>`
- Verify Redis connectivity for scrapers
- Confirm DB URLs and credentials