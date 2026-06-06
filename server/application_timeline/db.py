from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVICE_ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE_URL = (
    f"sqlite:///{PROJECT_ROOT / 'data' / 'crossbridge_application_timeline.db'}"
)
ALEMBIC_INI = SERVICE_ROOT / "alembic.ini"

# Env override key is distinct from Functions 1 and 2 so the services never share a DB.
ENV_DATABASE_URL = "CROSSBRIDGE_TIMELINE_DATABASE_URL"


def get_database_url() -> str:
    return os.environ.get(ENV_DATABASE_URL, DEFAULT_DATABASE_URL)


def build_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def run_migrations(database_url: str | None = None) -> None:
    """Run THIS service's Alembic migrations against the given (or default) DB."""
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(SERVICE_ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url or get_database_url())
    command.upgrade(config, "head")
