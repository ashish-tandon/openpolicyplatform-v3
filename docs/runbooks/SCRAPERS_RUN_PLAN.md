# Scrapers Run Plan

## Categories and Coverage
- Federal
  - Bills (daily)
  - Representatives (daily)
  - Committees (daily)
  - Other Data (as needed)
- Provincial (per province)
  - Bills (daily)
  - Representatives (daily)
  - Committees (daily)
  - Other Data (as needed)
- City (per city)
  - Bills (bootstrap + daily incremental)
  - Representatives (daily)
  - Committees (daily)
  - Other Data (as needed)

## Modes
- Daily: incremental updates via CronJobs
- Bootstrap: one-time historical backfill
- Special: ad-hoc maintenance/migrations

## Triggers and Expected Runtime
- Federal daily: 15–30 min (bills+people+committees)
- Provincial daily: 5–20 min per province
- City bootstrap (Toronto bills 2010+): 30–90 min
- Special: varies (on demand)

## Dependencies and Data Targets
- Dependencies
  - Network access to source domains
  - Respect rate limits (per-domain)
  - Stable external IDs for idempotent upserts
- Data targets (databases)
  - Core/App DB: `DATABASE_URL` (canonical app data)
  - Scrapers DB: `SCRAPERS_DATABASE_URL` (scraper journaling and staging)
  - Auth/User DB: optional logical DB (auth)

## Output Schemas
- CanonicalEntity
  - entity_type: bill|person|committee|event|vote|other
  - jurisdiction: federal|provincial:<code>|city:<name>
  - external_id: string
  - title, summary: optional
  - data: normalized dict (source-specific fields)
  - hash: content hash for idempotency

## Execution
- CLI
  - `python -m services.scraper.cli --mode daily --scope "<tier:code:entity>"`
  - `python -m services.scraper.cli --mode bootstrap --scope "city:toronto:bills" --since 2010-01-01`
- K8s CronJobs
  - Daily federal: 04:00 UTC
  - Daily provincial ON: 05:00 UTC
  - Bootstrap city Toronto bills: weekly Sunday 02:00 UTC

## Journaling and Metrics
- Journal runs in scrapers DB (`scr_runs` planned)
- Prometheus metrics
  - requests, items processed/changed, run durations

## Docker Standards
- Base image: python:3.11-slim
- Non-root user, pinned dependencies
- Healthcheck script (optional)
- Minimal layer count; use pip cache mounts if possible

## Rollout
- Feature flag OFF by default: `SCRAPER_SERVICE_ENABLED=false`
- Enable by scope; start with read-only verification
- Monitor metrics and audit logs