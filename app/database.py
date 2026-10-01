import os
from functools import lru_cache

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

load_dotenv()


@lru_cache
def get_client() -> MongoClient:
    """Creates one shared connection to MongoDB Atlas."""
    uri = os.getenv("MONGODB_URI")
    # Atlas (mongodb+srv) needs certifi's certificates. A local MongoDB, like the one in CI, doesn't use TLS.
    options = {"tlsCAFile": certifi.where()} if uri and uri.startswith("mongodb+srv://") else {}
    return MongoClient(uri, **options)


def get_db():
    return get_client()[os.getenv("MONGODB_DB_NAME", "simple_bank")]


def next_id(sequence_name: str) -> int:
    """Hands out auto-incrementing integer IDs, like AUTO_INCREMENT in SQL."""
    counter = get_db().counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["value"]


def reset_counter(sequence_name: str):
    get_db().counters.delete_one({"_id": sequence_name})
