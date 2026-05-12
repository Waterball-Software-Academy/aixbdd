import os
import pathlib
import sys
from types import SimpleNamespace

_root = pathlib.Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.deps import get_db, set_session_factory
from app.main import create_app
from app.models import Base
from tests.features.helpers.jwt_helper import JwtHelper

postgres_container = None
engine = None
SessionLocal = None


def before_all(context):
    global postgres_container, engine, SessionLocal

    postgres_container = PostgresContainer("postgres:15")
    postgres_container.start()

    db_url = postgres_container.get_connection_url().replace(
        "psycopg2", "psycopg"
    )
    os.environ["DATABASE_URL"] = db_url

    engine = create_engine(db_url)

    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")

    SessionLocal = sessionmaker(bind=engine)
    set_session_factory(SessionLocal)


def before_scenario(context, scenario):
    context.last_error = None
    context.last_response = None
    context.query_result = None
    context.ids = {}
    context.memo = {}

    context.db_session = SessionLocal()

    app = create_app()

    def _override_get_db():
        session = context.db_session
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    app.dependency_overrides[get_db] = _override_get_db

    from starlette.testclient import TestClient

    context.api_client = TestClient(app)
    context.jwt_helper = JwtHelper()
    context.repos = SimpleNamespace()
    context.services = SimpleNamespace()


def after_scenario(context, scenario):
    if hasattr(context, "db_session") and context.db_session:
        context.db_session.rollback()
        table_names = ", ".join(
            f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables)
        )
        context.db_session.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )
        context.db_session.commit()
        context.db_session.close()

    context.last_error = None
    context.last_response = None
    context.query_result = None
    context.ids = {}
    context.memo = {}


def after_all(context):
    global engine, postgres_container
    if engine:
        engine.dispose()
    if postgres_container:
        postgres_container.stop()
