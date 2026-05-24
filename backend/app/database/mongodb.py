from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
from app.core.logger import app_logger
from typing import Optional

_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_database():
    client = get_mongo_client()
    return client[settings.MONGO_DB]


def get_collection(name: str):
    db = get_database()
    return db[name]


def ping_mongo() -> bool:
    try:
        get_mongo_client().admin.command("ping")
        return True
    except ConnectionFailure as e:
        app_logger.error(f"MongoDB connection failed: {e}")
        return False


# ── Collection helpers ─────────────────────────────────────────────────────────

def save_cleaned_data(records: list, job_id: str) -> int:
    col = get_collection("cleaned_data")
    for r in records:
        r["_job_id"] = job_id
    if records:
        result = col.insert_many(records)
        return len(result.inserted_ids)
    return 0


def save_etl_log(log: dict):
    get_collection("etl_logs").insert_one(log)


def save_analytics_log(log: dict):
    get_collection("analytics_logs").insert_one(log)


def get_etl_logs(job_id: str) -> list:
    return list(get_collection("etl_logs").find({"job_id": job_id}, {"_id": 0}))


def save_report_meta(meta: dict):
    get_collection("reports").insert_one(meta)


def get_all_reports() -> list:
    return list(get_collection("reports").find({}, {"_id": 0}))
