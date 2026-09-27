import io

import boto3
import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from models.document_section import DocumentSection
from ports.document_loader import DocumentLoader


class EpubDocumentLoader(DocumentLoader):
    """Loads an epub straight from the MinIO bucket books are uploaded to.
    ``file_path`` is the object key book-ms stored (e.g. "books/<id>/name.epub"),
    not a filesystem path."""

    def __init__(self, s3_client: "boto3.client", bucket: str):
        self._s3 = s3_client
        self._bucket = bucket

    def load(self, file_path: str) -> list[DocumentSection]:
        response = self._s3.get_object(Bucket=self._bucket, Key=file_path)
        book = epub.read_epub(io.BytesIO(response["Body"].read()))

        sections: list[DocumentSection] = []

        for chapter_index, item in enumerate(
            book.get_items_of_type(ebooklib.ITEM_DOCUMENT), start=1
        ):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(" ", strip=True)

            if not text:
                continue

            heading = soup.find(["h1", "h2", "h3"])
            chapter = (
                heading.get_text(" ", strip=True)
                if heading
                else f"Chapter {chapter_index}"
            )

            sections.append(
                DocumentSection(
                    content=text,
                    chapter=chapter,
                    chapter_index=chapter_index,
                    source=item.get_name(),
                )
            )

        return sections
