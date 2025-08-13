from prometheus_client import Counter, Histogram

scraper_requests_total = Counter("scraper_requests_total", "requests", ["jurisdiction", "entity", "status"])
scraper_items_processed_total = Counter("scraper_items_processed_total", "items", ["jurisdiction", "entity"])
scraper_items_changed_total = Counter("scraper_items_changed_total", "changed", ["jurisdiction", "entity"])
scraper_run_duration_seconds = Histogram("scraper_run_duration_seconds", "duration", ["jurisdiction", "entity", "phase"])