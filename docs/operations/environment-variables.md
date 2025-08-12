# Environment Variables Mapping

Source of truth: `env.example` and `backend/api/config.py`

## Database
- `DATABASE_URL` (maps to Settings.database_url) — e.g., `postgresql://user@host:5432/db`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD` — optional granular settings

## API service
- `API_HOST` (Settings.host)
- `API_PORT` (Settings.port)
- `DEBUG` (Settings.environment != production)
- `ALLOWED_ORIGINS` (Settings.allowed_origins) — comma-separated
- `ALLOWED_HOSTS` (Settings.allowed_hosts) — comma-separated

## Security
- `SECRET_KEY` (Settings.secret_key) — required for JWT in production
- `ALGORITHM` (Settings.algorithm)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (Settings.access_token_expire_minutes)

## Redis
- `REDIS_URL` (Settings.redis_url)

## External services
- `OPENAI_API_KEY` (Settings.openai_api_key)

## Scraping
- `SCRAPER_TIMEOUT` (Settings.scraper_timeout)
- `MAX_CONCURRENT_SCRAPERS` (Settings.max_concurrent_scrapers)

## Logging
- `LOG_LEVEL` (Settings.log_level)

## File upload
- `MAX_FILE_SIZE` (Settings.max_file_size)
- `UPLOAD_DIR` (Settings.upload_dir)

## Frontend (Vite)
- `VITE_API_URL`
- `VITE_ENVIRONMENT`
- `VITE_ENABLE_ANALYTICS`
- `VITE_ENABLE_DEBUG`

Notes:
- Define all values in `.env` for local/dev; do not commit secrets
- In production, set env via your orchestrator/secrets manager