from typing import Dict, List

# Registry of all known scrapers and their default tasks and schedules
# Cron format: minute hour day month day_of_week (UTC)
SCRAPER_REGISTRY: Dict[str, Dict] = {
    "federal_parliament": {
        "tasks": ["bills", "mps", "votes"],
        "prod_cron": "0 2 * * *",   # daily at 02:00 UTC
        "test_cron": "0 * * * *",   # hourly
    },
    # Open Civic Data scrapers for Canadian provinces (external adapter planned)
    "ocd_provinces": {
        "tasks": ["people", "bills", "organizations"],
        "prod_cron": "30 3 * * *",
        "test_cron": "15 * * * *",
    },
    # Municipal-level scrapers (external adapter planned)
    "ocd_municipal": {
        "tasks": ["people", "events", "organizations"],
        "prod_cron": "0 4 * * *",
        "test_cron": "30 * * * *",
    },
    # Historical import via openparliament (external adapter planned)
    "openparliament_historic": {
        "tasks": ["import"],
        "prod_cron": "0 5 * * 0",   # weekly
        "test_cron": "45 * * * *",
    },
    # External reference normalization from Open North Represent API
    "represent_opennorth_ref": {
        "tasks": ["jurisdictions", "districts"],
        "prod_cron": "0 6 * * *",
        "test_cron": "0 */6 * * *",
    },
}