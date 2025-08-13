import os
import json
import time
import logging
from typing import Dict, Any, List

import redis
import requests
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI

from .federal_parliament_scraper import FederalParliamentScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = os.getenv("SCRAPER_QUEUE_KEY", "scraper_jobs")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "2.0"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))
API_BASE = os.getenv("API_BASE", "http://api:8000")

JOBS_CONSUMED = Counter("scraper_jobs_consumed_total", "Jobs consumed", ["scraper"])
TASKS_COMPLETED = Counter("scraper_tasks_completed_total", "Tasks completed", ["scraper", "task"])
TASKS_FAILED = Counter("scraper_tasks_failed_total", "Tasks failed", ["scraper", "task"])
RUN_DURATION = Histogram("scraper_run_seconds", "Duration of a job run in seconds", ["scraper"])
LAST_RUN_TS = Gauge("scraper_last_run_timestamp", "Unix ts of last successful run", ["scraper"]) 

app = FastAPI(title="Scrapers Worker")

@app.get("/metrics")
async def metrics():
    return app.response_class(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}


def process_federal(tasks: List[str]):
    scraper = FederalParliamentScraper()
    if "bills" in tasks:
        try:
            bills = scraper.scrape_bills()
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="bills").inc(len(bills))
            # TODO: persist bills via API or direct DB
        except Exception:
            TASKS_FAILED.labels(scraper="federal_parliament", task="bills").inc()
    if "mps" in tasks:
        try:
            mps = scraper.scrape_mps()
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="mps").inc(len(mps))
        except Exception:
            TASKS_FAILED.labels(scraper="federal_parliament", task="mps").inc()
    if "votes" in tasks:
        try:
            votes = scraper.scrape_votes()
            TASKS_COMPLETED.labels(scraper="federal_parliament", task="votes").inc(len(votes))
        except Exception:
            TASKS_FAILED.labels(scraper="federal_parliament", task="votes").inc()


def run_loop():
    r = redis.from_url(REDIS_URL)
    while True:
        # Blocking pop with timeout to reduce CPU
        item = r.brpop(QUEUE_KEY, timeout=int(POLL_INTERVAL))
        if not item:
            continue
        _, payload_bytes = item
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            logger.warning("Invalid payload: %s", payload_bytes[:200])
            continue
        scraper = payload.get("scraper")
        tasks = payload.get("tasks", [])
        start = time.time()
        try:
            if scraper == "federal_parliament":
                process_federal(tasks)
                JOBS_CONSUMED.labels(scraper="federal_parliament").inc()
                LAST_RUN_TS.labels(scraper="federal_parliament").set(time.time())
        except Exception as e:
            logger.exception("Worker error: %s", e)
        finally:
            RUN_DURATION.labels(scraper=scraper or "unknown").observe(time.time() - start)


@app.on_event("startup")
def on_startup():
    # Run loop in background thread
    import threading
    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
    logger.info("Worker started")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Worker stopped")