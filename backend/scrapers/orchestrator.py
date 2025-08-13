import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis

from .registry import SCRAPER_REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.orchestrator")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("SCRAPER_QUEUE_KEY", "scraper_jobs")

# Comma-separated list of enabled scrapers per mode
ENABLED_SCRAPERS_PROD = [s.strip() for s in os.getenv("ENABLED_SCRAPERS_PROD", "federal_parliament").split(",") if s.strip()]
ENABLED_SCRAPERS_TEST = [s.strip() for s in os.getenv("ENABLED_SCRAPERS_TEST", "federal_parliament").split(",") if s.strip()]

app = FastAPI(title="Scrapers Orchestrator")

JOBS_ENQUEUED = Counter("scraper_jobs_enqueued_total", "Jobs enqueued", ["scraper"])
LAST_ENQUEUE_TS = Gauge("scraper_last_enqueue_timestamp", "Unix ts of last enqueue", ["scraper"])

redis_client = redis.from_url(REDIS_URL)
scheduler = BackgroundScheduler(timezone="UTC")


def enqueue_job(payload: Dict[str, Any]):
    redis_client.lpush(QUEUE_KEY, json.dumps(payload))


@app.get("/metrics")
async def metrics():
    return app.response_class(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


def enqueue_scraper(name: str, mode: str):
    config = SCRAPER_REGISTRY.get(name)
    if not config:
        logger.warning("Unknown scraper %s", name)
        return
    payload = {
        "scraper": name,
        "mode": mode,
        "tasks": config.get("tasks", []),
        "enqueued_at": time.time(),
    }
    enqueue_job(payload)
    JOBS_ENQUEUED.labels(scraper=name).inc()
    LAST_ENQUEUE_TS.labels(scraper=name).set(time.time())
    logger.info("Enqueued %s (mode=%s)", name, mode)


def _schedule_for(name: str, mode: str, cron: str):
    m, h, dom, mon, dow = cron.split()
    job_id = f"{name}_{mode}"
    scheduler.add_job(lambda: enqueue_scraper(name, mode), "cron", minute=m, hour=h, day=dom, month=mon, day_of_week=dow, id=job_id, replace_existing=True)


@app.on_event("startup")
def on_startup():
    # Per-scraper overrides via env: {SCRAPER}_PROD_CRON / {SCRAPER}_TEST_CRON
    for name, cfg in SCRAPER_REGISTRY.items():
        if name in ENABLED_SCRAPERS_PROD:
            env_key = f"{name.upper()}_PROD_CRON"
            cron = os.getenv(env_key, cfg.get("prod_cron", "0 2 * * *"))
            _schedule_for(name, "prod", cron)
        if name in ENABLED_SCRAPERS_TEST:
            env_key = f"{name.upper()}_TEST_CRON"
            cron = os.getenv(env_key, cfg.get("test_cron", "0 * * * *"))
            _schedule_for(name, "test", cron)
    scheduler.start()
    logger.info("Orchestrator started. Enabled prod=%s test=%s", ENABLED_SCRAPERS_PROD, ENABLED_SCRAPERS_TEST)


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Orchestrator stopped")