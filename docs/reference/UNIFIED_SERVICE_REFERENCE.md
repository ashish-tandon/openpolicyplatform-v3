# Unified Service Reference

## Existing Services

- API (FastAPI)
- Web (React)

## Scraper Service (Authoritative)
- DB: `openpolicy_scrapers` (separate from core & auth)
- Entry: `python -m services.scraper.cli --mode <daily|bootstrap|special> --scope "<tier:code:entity>"`
- Scopes: `federal:*`, `provincial:on:*`, `city:toronto:bills`, etc.
- Frequencies: daily (CronJobs), bootstrap (historical), special (ad-hoc)
- Feature flag: `SCRAPER_SERVICE_ENABLED`
- Adapters: `services/scraper/adapters/*` wrapping upstream repos under `external/`