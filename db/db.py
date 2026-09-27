from sqlmodel import Session, SQLModel, create_engine, text

from config import settings
from db import orm_models  # noqa: F401  (registers BookChunkORM on SQLModel.metadata)

engine = create_engine(settings.database_url)


def get_session():
    with Session(engine) as session:
        yield session


def _create_database_if_not_exists() -> None:
    maintenance_url = (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_server}:{settings.postgres_port}/postgres"
    )
    maintenance_engine = create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with maintenance_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db"),
                {"db": settings.postgres_db},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{settings.postgres_db}"'))
    finally:
        maintenance_engine.dispose()


def init_db() -> None:
    _create_database_if_not_exists()

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    SQLModel.metadata.create_all(engine)
