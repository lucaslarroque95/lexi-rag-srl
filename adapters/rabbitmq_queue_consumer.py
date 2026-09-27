import json

import pika

from models.ingestion_message import IngestionMessage
from ports.queue_consumer import QueueConsumer


class RabbitMQQueueConsumer(QueueConsumer):
    """Pulls ingestion messages from a RabbitMQ queue. Messages are JSON
    bodies shaped like IngestionMessage: {"book": ..., "file_path": ...}."""

    def __init__(self, host: str, port: int, user: str, password: str, queue: str):
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(user, password),
            # Ingesting one message means embedding every chunk of a book,
            # which can take well over RabbitMQ's default 60s heartbeat with
            # no I/O on this connection in between. A generous heartbeat
            # keeps the broker from dropping us as unresponsive mid-ingest.
            heartbeat=3600,
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=queue, durable=True)

        self._queue = queue
        self._delivery_tags: dict[int, int] = {}

    def poll(self) -> IngestionMessage | None:
        method, _properties, body = self._channel.basic_get(queue=self._queue, auto_ack=False)
        if method is None:
            return None

        payload = json.loads(body)
        message = IngestionMessage(book=payload["book"], file_path=payload["file_path"])
        self._delivery_tags[id(message)] = method.delivery_tag
        return message

    def ack(self, message: IngestionMessage) -> None:
        delivery_tag = self._delivery_tags.pop(id(message), None)
        if delivery_tag is not None:
            self._channel.basic_ack(delivery_tag=delivery_tag)

    def close(self) -> None:
        if self._connection.is_open:
            self._connection.close()
