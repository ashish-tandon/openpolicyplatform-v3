# Setup

## Local Development (API tests)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/api -q
```

## Docker (when available)
```bash
cp .env.example .env
docker compose up -d --build
```

## Configure Scrapers
- Edit `docker-compose.yml` orchestrator env:
  - `ENABLED_SCRAPERS_PROD`, `ENABLED_SCRAPERS_TEST`
- Optionally override crons with `{SCRAPER}_PROD_CRON`, `{SCRAPER}_TEST_CRON`

## External Repos
```bash
chmod +x scripts/ingest_repos.sh
./scripts/ingest_repos.sh
```

## Initialize Git and Push
```bash
git init
git add .
git commit -m "Initial import: API, web, scrapers, monitoring, docs"
# set your remote
# git remote add origin git@github.com:yourorg/yourrepo.git
# git push -u origin main
```