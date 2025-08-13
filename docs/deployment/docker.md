# Docker Deployment (Optional)

## Compose example (to create)
- Services: api, postgres (optional), nginx (optional)
- Volumes: db data, logs, backups, exports
- Networks: internal bridge

## API container
- Command: `uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 2`
- Env: from `.env`
- Healthcheck: curl `/api/v1/health`

## Frontend
- Build image from web app and serve via nginx

## Postgres
- Mount volume; set POSTGRES_* env

## Next steps
- Provide `docker-compose.yml` and `Dockerfile` samples

## Scraper Service Image
- Build: `docker build -t ghcr.io/your-org/scraper:dev -f services/scraper/Dockerfile .`
- Run (daily): `docker run --rm ghcr.io/your-org/scraper:dev --mode daily --scope "federal:*"`
- Run (bootstrap): `docker run --rm ghcr.io/your-org/scraper:dev --mode bootstrap --scope "city:toronto:bills" --since 2010-01-01`