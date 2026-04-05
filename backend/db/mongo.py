"""MongoDB connection and collection helpers."""

from __future__ import annotations

import logging
from functools import lru_cache

from pymongo import MongoClient, ASCENDING

from config.settings import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)
REGISTERED_USERS_COLLECTION = "registered_users"
LEGACY_USERS_COLLECTION = "users"
ANALYSES_COLLECTION = "analyses"


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Create and cache a single MongoClient for the app process."""
    return MongoClient(MONGODB_URI)


def get_db():
    """Return database handle."""
    return get_client()[MONGODB_DB_NAME]


def init_indexes() -> None:
    """Create essential indexes for auth and history queries."""
    db = get_db()
    db[REGISTERED_USERS_COLLECTION].create_index([("email", ASCENDING)], unique=True)
    db[LEGACY_USERS_COLLECTION].create_index([("email", ASCENDING)], unique=True)
    db[ANALYSES_COLLECTION].create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    logger.info("MongoDB indexes initialized")
