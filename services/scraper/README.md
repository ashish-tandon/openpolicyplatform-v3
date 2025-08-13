# Scraper Service

Modular scraping subsystem. Keep existing scrapers via adapters; do not rewrite unless broken.

- Canonical pipeline: fetch → parse → normalize → upsert (idempotent)
- Journaling: every run recorded (scr_runs)
- Metrics: Prometheus counters/gauges/histograms
- Modes: daily, bootstrap (one-time), special
- CLI: `python -m services.scraper.cli --mode <mode> --scope "<scope>" [--since YYYY-MM-DD]`