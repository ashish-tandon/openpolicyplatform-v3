# Scraper Service

Modular scraping subsystem. Keep existing scrapers via adapters; do not rewrite unless broken.

- Canonical pipeline: fetch → parse → normalize → upsert (idempotent)
- Journaling: every run recorded (scr_runs)
- Metrics: Prometheus counters/gauges/histograms
- Modes: daily, bootstrap (one-time), special
- CLI: `python -m services.scraper.cli --mode <mode> --scope "<scope>" [--since YYYY-MM-DD]`

## Ports
- Default: 9003 for any future long-running worker (env: `SCRAPER_PORT`)

## Inputs
- Env vars: user agent, retries, timeouts; see docs
- Central config: `config/central-config.yaml`
- Upstream sources via adapters

## Outputs
- Normalized entities passed to store upsert
- Audit/metrics as configured

## Pre-deploy Tests
```bash
pytest -q services/scraper/tests
```