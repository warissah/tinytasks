from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel
from pymongo.errors import ConfigurationError, InvalidURI

from app.constants import USERS_COLLECTION
from app.config import get_settings

logger = logging.getLogger(__name__)

_DEFAULT_DB = "adhd_coach"


def _resolve_database(
    client: AsyncIOMotorClient, explicit_name: str | None
) -> AsyncIOMotorDatabase:
    if explicit_name:
        return client[explicit_name]
    default = client.get_default_database()
    if default is not None:
        return default
    logger.warning(
        "No database name in MONGODB_URI and MONGODB_DATABASE unset; using %s",
        _DEFAULT_DB,
    )
    return client[_DEFAULT_DB]


def startup_mongo(app: FastAPI) -> None:
    settings = get_settings()
    uri = (settings.mongodb_uri or "").strip()
    if not uri:
        app.state.mongo_client = None
        app.state.mongo_db = None
        return
    try:
        client = AsyncIOMotorClient(uri)
    except (ConfigurationError, InvalidURI, ValueError) as exc:
        # Bad placeholder URIs (e.g. mongodb:// with no host) crash lifespan and take down the host (e.g. Railway).
        logger.error(
            "MONGODB_URI is set but invalid; Mongo disabled until fixed: %s",
            exc,
        )
        app.state.mongo_client = None
        app.state.mongo_db = None
        return
    app.state.mongo_client = client
    app.state.mongo_db = _resolve_database(client, settings.mongodb_database)
    logger.info("MongoDB client initialized")


def shutdown_mongo(app: FastAPI) -> None:
    client = getattr(app.state, "mongo_client", None)
    if client is not None:
        client.close()
        app.state.mongo_client = None
        app.state.mongo_db = None


async def ensure_indexes(app: FastAPI) -> None:
    db = getattr(app.state, "mongo_db", None)
    if db is None:
        return
    try:
        await db[USERS_COLLECTION].create_indexes(
            [
                IndexModel([("user_id", 1)], unique=True, name="user_id_unique"),
                IndexModel(
                    [("email_normalized", 1)],
                    unique=True,
                    name="email_normalized_unique",
                    partialFilterExpression={"email_normalized": {"$type": "string"}},
                ),
                IndexModel(
                    [("phone_normalized", 1)],
                    unique=True,
                    name="phone_normalized_unique",
                    partialFilterExpression={"phone_normalized": {"$type": "string"}},
                ),
            ]
        )
    except Exception:
        logger.exception("Failed to ensure MongoDB indexes")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    startup_mongo(app)
    await ensure_indexes(app)
    yield
    shutdown_mongo(app)
