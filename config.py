import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_path(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_port: str
    postgres_db: str

    openai_api_key: str
    embedding_model: str
    embedding_dimension: int

    chunk_size: int
    chunk_overlap: int

    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_queue: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )


def _load_settings() -> Settings:
    return Settings(
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_server=os.environ["POSTGRES_SERVER"],
        postgres_port=os.environ["POSTGRES_PORT"],
        postgres_db=os.environ["POSTGRES_DB"],
        openai_api_key=os.environ["OPENAI_API_KEY"],
        embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimension=int(os.environ.get("EMBEDDING_DIMENSION", "1536")),
        chunk_size=int(os.environ.get("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", "200")),
        rabbitmq_host=os.environ.get("RABBITMQ_HOST", "localhost"),
        rabbitmq_port=int(os.environ.get("RABBITMQ_PORT", "5672")),
        rabbitmq_user=os.environ.get("RABBITMQ_USER", "rabbitmq"),
        rabbitmq_password=os.environ.get("RABBITMQ_PASSWORD", "rabbitmq123"),
        rabbitmq_queue=os.environ.get("RABBITMQ_QUEUE", "book-ingestion"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT", "http://localhost:9000"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin123"),
        minio_bucket=os.environ.get("MINIO_BUCKET", "lexi-books"),
    )


settings = _load_settings()
