# Admin UI: Scrapers and Dashboard

## Scrapers Page
- Lists jobs with id, enabled, last_run
- Actions:
  - Enable/Disable job
  - Run Now: scope, mode (daily/bootstrap/special), optional since for bootstrap
  - Run All Daily: queues daily jobs across scopes
- Feature flag: if `SCRAPER_SERVICE_ENABLED=false`, page indicates disabled

## Dashboard
- Unified Status: `/api/v1/admin/status/unified` summary
- System Metrics: `/api/v1/dashboard/system`
- Scraper Metrics: `/api/v1/dashboard/scrapers`
- Database Metrics: `/api/v1/dashboard/database`
- Scraper Config: shows DB, concurrency, rate limit, UA, timeouts, retries, scheduler
- Toggle Feature Flag: flips `SCRAPER_SERVICE_ENABLED` via admin endpoint
- Quick Actions: Manage Scrapers, Run All Daily, View API Dashboard JSON, View Metrics

## Enhancements
- Stat cards on dashboard for quick overview
- Tabs on scrapers page: Jobs, Status, Logs, Failures
- Run All Daily action and scope/mode/since controls
- Admin Audit page with pagination
- Navigation links to Admin pages
- Analytics: add hooks at page mount (placeholder) and on actions (run-now, toggle)