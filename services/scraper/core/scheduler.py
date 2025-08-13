import os

def parse_scope(scope: str):
    # format: <tier>:<code|*>:<entity|*>
    # examples: federal:*:daily | provincial:on:representatives | city:toronto:bills
    parts = scope.split(":")
    return (parts + ["*","*","*"])[:3]

def enabled():
    return os.getenv("SCHEDULER_ENABLED","true").lower()=="true"

SCRAPER_HOST = os.getenv("SCRAPER_HOST", "0.0.0.0")
SCRAPER_PORT = int(os.getenv("SCRAPER_PORT", "9003"))