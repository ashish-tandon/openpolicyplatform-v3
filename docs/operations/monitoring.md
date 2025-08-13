# Monitoring and Observability

## Metrics
- Expose `/metrics` from API via Prometheus client
- Scraper metrics counters/histograms in `services/scraper/core/metrics.py`
- Set up Prometheus Operator with ServiceMonitor for API namespace

## Logs
- Structure JSON logs where possible
- Ship logs with Fluent Bit/Vector to log store
- Retention: 14-30 days depending on environment

## Alerts
- Health endpoints failures
- High CPU/memory on API pods
- Scraper job failures/backoff
- No recent scraper runs for daily scopes

## Dashboards
- API latency/throughput, error rates
- Scraper runs per scope, success rate, durations
- DB connections, slow queries