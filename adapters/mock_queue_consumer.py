from collections import deque

from models.ingestion_message import IngestionMessage
from ports.queue_consumer import QueueConsumer

from .queue import books


class InFileMockQueueConsumer(QueueConsumer):
    """Stand-in for a real queue (SQS/RabbitMQ/Kafka). Seeded with a fixed
    batch of messages; swap for a real QueueConsumer implementation later
    without touching IngestionWorker or IngestDocumentUseCase."""

    def __init__(self):
        messages = []
        for book in books.queue:
            message = IngestionMessage(book=book["title"], file_path=book["path"])
            messages.append(message)
        
        self._pending: deque[IngestionMessage] = deque(messages)

    def poll(self) -> IngestionMessage | None:
        if not self._pending:
            return None
        return self._pending.popleft()

    def ack(self, message: IngestionMessage) -> None:
        pass
