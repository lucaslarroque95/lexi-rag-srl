"""Wires the real Postgres/S3/OpenAI-backed use case once per Lambda cold
start. The handler calls new_use_case() and hands it to handle(); tests
build an IngestDocumentUseCase by hand around fakes instead, so this never
runs in a test process (importing config already reads POSTGRES_*/
OPENAI_API_KEY eagerly — see conftest.py's dummy values for why that's still
import-safe under pytest).

Unlike the gin/FastAPI pilots, there's no queue consumer to build here: SQS
+ the Lambda event source mapping replaces the RabbitMQ poll loop in
worker/ingestion_worker.py entirely — this file only wires the same
loader/splitter/embedder/repository worker/main.py wires for that loop.
"""

import os


def new_use_case():
    from adapters.epub_document_loader import EpubDocumentLoader
    from adapters.langchain_text_splitter import LangchainTextSplitterAdapter
    from adapters.openai_embedding_provider import OpenAIEmbeddingProvider
    from config import settings
    from db.db import engine, init_db
    from repositories.postgres_chunk_repository import PostgresChunkRepository
    from sqlmodel import Session
    from use_cases.ingest_document_use_case import IngestDocumentUseCase

    init_db()

    s3_client = _build_s3_client(settings)
    bucket = os.environ.get("S3_BUCKET") or settings.minio_bucket

    loader = EpubDocumentLoader(s3_client=s3_client, bucket=bucket)
    splitter = LangchainTextSplitterAdapter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    embedder = OpenAIEmbeddingProvider(
        model=settings.embedding_model, api_key=settings.openai_api_key, dimension=settings.embedding_dimension
    )
    repository = PostgresChunkRepository(Session(engine))

    return IngestDocumentUseCase(loader, splitter, embedder, repository)


def _build_s3_client(settings):
    import boto3

    # With MINIO_ENDPOINT set (local dev via docker-compose), talk to MinIO
    # with its static credentials, same as worker/main.py. Without it
    # (Lambda in AWS), talk to real S3 using the execution role's
    # credentials via the default AWS credential chain.
    if os.environ.get("MINIO_ENDPOINT"):
        return boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
        )
    return boto3.client("s3")
