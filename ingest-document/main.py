import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bootstrap

_use_case = None


def handle(use_case, event, context):
    """Mirrors worker.ingestion_worker.IngestionWorker.run, one message at a
    time — but as an SQS batch handler instead of a poll loop, since the
    event source mapping is what decides how many records arrive per
    invocation (batch_size=1 in lexi-infra-aws, to match the "one book per
    run" semantics the KEDA ScaledJob had).

    Returns batchItemFailures so only the records that actually failed get
    retried/DLQ'd — a bad message doesn't drag good ones in the same batch
    down with it.
    """
    from models.ingestion_message import IngestionMessage

    failures = []
    for record in event.get("Records", []):
        try:
            payload = json.loads(record["body"])
            message = IngestionMessage(book=payload["book"], file_path=payload["file_path"])
            chunks = use_case.execute(message)
            print(f"Ingested {len(chunks)} chunks from '{message.book}'")
        except Exception as exc:  # noqa: BLE001 — one bad record must not sink the rest of the batch
            print(f"failed to ingest record {record.get('messageId')}: {exc}")
            failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": failures}


def handler(event, context):
    global _use_case
    if _use_case is None:
        _use_case = bootstrap.new_use_case()
    return handle(_use_case, event, context)
