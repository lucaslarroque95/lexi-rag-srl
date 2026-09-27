import json

from models.document_section import DocumentSection
from ports.document_loader import DocumentLoader
from ports.embedding_provider import EmbeddingProvider
from ports.text_splitter import TextSplitter
from repositories.chunk_repository import ChunkRepository
from use_cases.ingest_document_use_case import IngestDocumentUseCase

from conftest import load_sibling_main

main = load_sibling_main(__file__)


class FakeLoader(DocumentLoader):
    def __init__(self, sections=None, error=None):
        self.sections = sections or []
        self.error = error
        self.requested_paths = []

    def load(self, file_path):
        self.requested_paths.append(file_path)
        if self.error:
            raise self.error
        return self.sections


class FakeSplitter(TextSplitter):
    def split(self, sections):
        return sections  # identity: one section in, one chunk out


class FakeEmbedder(EmbeddingProvider):
    def embed(self, text):
        return [float(len(text))]

    @property
    def dimension(self):
        return 1


class FakeChunkRepository(ChunkRepository):
    def __init__(self):
        self.saved = []

    def save_many(self, chunks):
        self.saved.extend(chunks)
        return chunks


def make_use_case(loader):
    repository = FakeChunkRepository()
    use_case = IngestDocumentUseCase(loader, FakeSplitter(), FakeEmbedder(), repository)
    return use_case, repository


def sqs_event(*bodies):
    return {
        "Records": [
            {"messageId": f"msg-{i}", "body": json.dumps(body)} for i, body in enumerate(bodies)
        ]
    }


def test_ingests_a_single_message():
    loader = FakeLoader(sections=[DocumentSection(content="hello", chapter="Ch1", chapter_index=1, source="a.xhtml")])
    use_case, repository = make_use_case(loader)

    event = sqs_event({"book": "Eldest", "file_path": "books/1/eldest.epub"})
    resp = main.handle(use_case, event, {})

    assert resp == {"batchItemFailures": []}
    assert loader.requested_paths == ["books/1/eldest.epub"]
    assert len(repository.saved) == 1
    assert repository.saved[0].book == "Eldest"


def test_batch_of_two_processes_both():
    loader = FakeLoader(sections=[DocumentSection(content="x", chapter="Ch1", chapter_index=1, source="a.xhtml")])
    use_case, repository = make_use_case(loader)

    event = sqs_event(
        {"book": "Eragon", "file_path": "books/1/eragon.epub"},
        {"book": "Eldest", "file_path": "books/2/eldest.epub"},
    )
    resp = main.handle(use_case, event, {})

    assert resp == {"batchItemFailures": []}
    assert loader.requested_paths == ["books/1/eragon.epub", "books/2/eldest.epub"]
    assert len(repository.saved) == 2


def test_failed_record_is_reported_without_failing_the_whole_batch():
    loader = FakeLoader(error=RuntimeError("bucket unreachable"))
    use_case, repository = make_use_case(loader)

    event = sqs_event({"book": "Eragon", "file_path": "books/1/eragon.epub"})
    resp = main.handle(use_case, event, {})

    assert resp == {"batchItemFailures": [{"itemIdentifier": "msg-0"}]}
    assert repository.saved == []


def test_malformed_body_is_reported_as_a_failure():
    use_case, _ = make_use_case(FakeLoader())

    event = {"Records": [{"messageId": "msg-0", "body": "not-json"}]}
    resp = main.handle(use_case, event, {})

    assert resp == {"batchItemFailures": [{"itemIdentifier": "msg-0"}]}
