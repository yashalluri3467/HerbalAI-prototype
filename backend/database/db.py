"""Async database layer for session-history persistence.

Reads DATABASE_URL from the environment. If it is unset, the database is
disabled and the app runs without persistence (predictions still succeed).
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL")
DB_ENABLED = bool(DATABASE_URL)

# Neon (and most managed Postgres) require TLS. The provided URL carries
# `sslmode=require`; forward that to the asyncpg driver.
connect_args: dict = {}
if DATABASE_URL and "sslmode=" in DATABASE_URL:
    connect_args["ssl"] = True

_metadata = MetaData()


class Base(DeclarativeBase):
    metadata = _metadata


engine = None
SessionLocal = None
if DB_ENABLED:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=2,
        connect_args=connect_args,
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create tables on startup (idempotent). No migrations framework needed."""
    if not DB_ENABLED:
        return
    # Import models so they register on Base.metadata before create_all.
    from database import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async session (or None when disabled)."""
    if SessionLocal is None:
        yield None
        return
    async with SessionLocal() as session:
        yield session
