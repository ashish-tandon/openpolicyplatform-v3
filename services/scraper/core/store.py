import hashlib, json, datetime
from typing import Dict, Tuple
# NOTE: replace with your actual DB layer / SQLAlchemy session

def content_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

def upsert_entity(db, entity: dict) -> Tuple[bool, str]:
    """
    Upsert by (jurisdiction, entity_type, external_id).
    Return (changed, new_hash)
    """
    h = content_hash(entity["data"])
    # Pseudo-logic: check existing hash, upsert if changed, write diff
    # Implement real SQL/ORM here.
    changed = True
    return changed, h

def journal_run(db, run: Dict):
    # Insert a row into scr_runs with status/counters.
    pass