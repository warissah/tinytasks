from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

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
    client = AsyncIOMotorClient(uri)
    app.state.mongo_client = client
    app.state.mongo_db = _resolve_database(client, settings.mongodb_database)
    logger.info("MongoDB client initialized")


def shutdown_mongo(app: FastAPI) -> None:
    client = getattr(app.state, "mongo_client", None)
    if client is not None:
        client.close()
        app.state.mongo_client = None
        app.state.mongo_db = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    startup_mongo(app)
    yield
    shutdown_mongo(app)
