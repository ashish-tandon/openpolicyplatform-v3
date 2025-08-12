# Docker Compose Deployment

Compose file: `infrastructure/docker/docker-compose.yml`

Usage
- Copy `.env` to production location with required variables
- Run: `docker compose -f infrastructure/docker/docker-compose.yml up -d --build`

Services
- api: FastAPI service (port 8000)
- db: PostgreSQL 14 (port 5432)
- (optional) web: placeholder for building/serving the frontend

Volumes
- db-data: PostgreSQL data
- logs: app logs directory (if mounted)

Notes
- Adjust `ALLOWED_ORIGINS` and `ALLOWED_HOSTS` for production
- Add `SCRAPER_REPORTS_DIR` and `SCRAPER_LOGS_DIR` volume mounts if needed