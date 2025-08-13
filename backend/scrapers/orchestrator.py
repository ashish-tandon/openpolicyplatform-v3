import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.orchestrator")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("SCRAPER_QUEUE_KEY", "scraper_jobs")

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


def schedule_federal_daily():
    payload = {"scraper": "federal_parliament", "tasks": ["bills", "mps", "votes"], "enqueued_at": time.time()}
    enqueue_job(payload)
    JOBS_ENQUEUED.labels(scraper="federal_parliament").inc()
    LAST_ENQUEUE_TS.labels(scraper="federal_parliament").set(time.time())
    logger.info("Enqueued federal_parliament job")


@app.on_event("startup")
def on_startup():
    # Default schedule: every day at 02:00 UTC
    cron = os.getenv("FEDERAL_SCHEDULE_CRON", "0 2 * * *")
    # APScheduler cron: minute hour day month day_of_week
    m, h, dom, mon, dow = cron.split()
    scheduler.add_job(schedule_federal_daily, "cron", minute=m, hour=h, day=dom, month=mon, day_of_week=dow, id="federal_daily", replace_existing=True)
    scheduler.start()
    logger.info("Orchestrator started with schedule %s", cron)


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Orchestrator stopped")