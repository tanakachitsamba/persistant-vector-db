import pathlib
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from add_documents import IngestionError, ingest_documents, parse_ingestion_payload


class DummyCollection:
    def __init__(self):
        self.items = {}

    def add(self, documents, metadatas, ids):
        for doc, metadata, doc_id in zip(documents, metadatas, ids):
            if doc_id in self.items:
                raise ValueError("ID already exists")
            self.items[doc_id] = {"document": doc, "metadata": metadata}

    def remove(self, ids):
        for doc_id in ids:
            self.items.pop(doc_id, None)

    def __len__(self):
        return len(self.items)


@pytest.fixture()
def collection():
    return DummyCollection()


def test_parse_ingestion_payload_success():
    payload = {
        "documents": ["Doc"],
        "metadatas": [{"source": "unit"}],
        "ids": ["doc-1"],
    }

    documents, metadatas, ids = parse_ingestion_payload(payload)

    assert documents == ["Doc"]
    assert metadatas == [{"source": "unit"}]
    assert ids == ["doc-1"]


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ("{invalid", "Invalid JSON payload provided."),
        (
            {"documents": ["Doc"], "metadatas": [{"source": "unit"}]},
            "Payload is missing required keys",
        ),
    ],
)
def test_parse_ingestion_payload_errors(payload, expected_message):
    with pytest.raises(IngestionError) as exc_info:
        parse_ingestion_payload(payload)

    assert expected_message in str(exc_info.value)


def test_ingest_documents_success(collection):
    documents = ["Doc 1", "Doc 2"]
    metadatas = [{"source": "unit"}, {"source": "unit"}]
    ids = ["doc-1", "doc-2"]

    ingested = ingest_documents(collection, documents, metadatas, ids)

    assert ingested == 2
    assert len(collection) == 2


def test_ingest_documents_duplicate_ids(collection):
    documents = ["Doc 1", "Doc 2"]
    metadatas = [{"source": "unit"}, {"source": "unit"}]
    ids = ["doc-1", "doc-1"]

    with pytest.raises(IngestionError) as exc_info:
        ingest_documents(collection, documents, metadatas, ids)

    assert "Duplicate ids" in str(exc_info.value)
