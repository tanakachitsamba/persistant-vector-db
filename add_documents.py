"""Utilities for ingesting documents into a Chroma collection."""

from __future__ import annotations

import json
from typing import Any, Iterable, List, Sequence
import os


class IngestionError(ValueError):
    """Raised when the ingestion payload is invalid."""


def load_openai_key() -> str:
    """Load the OpenAI API key from the environment."""

    from dotenv import load_dotenv

    load_dotenv()
    openai_key = os.environ.get("OPENAI_KEY")
    if not openai_key:
        raise ValueError("OPENAI_KEY is not set in the .env file.")
    return openai_key

def create_openai_ef(api_key):
    from chromadb.utils import embedding_functions

    # Using OpenAI Embeddings. This assumes you have the openai package installed
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-ada-002"
    )
    return openai_ef

def get_persistent_client(persist_directory: str = "db") -> Any:
    """Return a persistent Chroma client for the provided directory."""

    import chromadb

    return chromadb.PersistentClient(path=persist_directory)


def create_or_get_collection(client: Any, name: str = "lake") -> Any:
    """Create a new chroma collection or return an existing one."""

    return client.get_or_create_collection(name=name)


def _ensure_sequence(data: Sequence, expected_length: int, label: str) -> List:
    if isinstance(data, (str, bytes)) or not isinstance(data, Sequence):
        raise IngestionError(f"{label} must be a sequence of values.")

    values = list(data)
    if len(values) != expected_length:
        raise IngestionError(
            f"Expected {expected_length} {label}, received {len(values)}."
        )
    return values


def ingest_documents(
    collection,
    documents: Sequence[str],
    metadatas: Sequence[dict],
    ids: Sequence[str],
) -> int:
    """Add the provided documents to the collection.

    Args:
        collection: A Chroma collection (or any object exposing an ``add`` method).
        documents: Sequence of textual documents.
        metadatas: Sequence of metadata dictionaries.
        ids: Sequence of unique document identifiers.

    Returns:
        The number of documents ingested.

    Raises:
        IngestionError: If the provided payload is invalid.
    """

    document_list = list(documents)
    metadata_list = _ensure_sequence(metadatas, len(document_list), "metadatas")
    id_list = _ensure_sequence(ids, len(document_list), "ids")

    if not all(isinstance(doc, str) for doc in document_list):
        raise IngestionError("All documents must be strings.")

    if not all(isinstance(meta, dict) for meta in metadata_list):
        raise IngestionError("All metadatas must be dictionaries.")

    if not all(isinstance(id_value, str) for id_value in id_list):
        raise IngestionError("All ids must be strings.")

    if len(set(id_list)) != len(id_list):
        raise IngestionError("Duplicate ids detected in payload.")

    collection.add(documents=document_list, metadatas=metadata_list, ids=id_list)
    return len(document_list)


def parse_ingestion_payload(payload: str | dict) -> tuple[List[str], List[dict], List[str]]:
    """Parse a JSON payload into document, metadata, and id lists."""

    if isinstance(payload, str):
        try:
            payload_data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise IngestionError("Invalid JSON payload provided.") from exc
    elif isinstance(payload, dict):
        payload_data = payload
    else:
        raise IngestionError("Payload must be a JSON string or dictionary.")

    required_keys = {"documents", "metadatas", "ids"}
    missing_keys = required_keys.difference(payload_data)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise IngestionError(f"Payload is missing required keys: {missing}.")

    documents = payload_data["documents"]
    metadatas = payload_data["metadatas"]
    ids = payload_data["ids"]

    if not isinstance(documents, list):
        raise IngestionError("Payload field 'documents' must be a list.")
    if not isinstance(metadatas, list):
        raise IngestionError("Payload field 'metadatas' must be a list.")
    if not isinstance(ids, list):
        raise IngestionError("Payload field 'ids' must be a list.")

    return documents, metadatas, ids


def run_ingestion(
    documents: Iterable[str],
    metadatas: Iterable[dict],
    ids: Iterable[str],
    *,
    persist_directory: str = "db",
    collection_name: str = "lake",
) -> int:
    """Convenience helper to ingest a batch of documents."""

    client = get_persistent_client(persist_directory=persist_directory)
    collection = create_or_get_collection(client, name=collection_name)
    return ingest_documents(collection, documents, metadatas, ids)


__all__ = [
    "IngestionError",
    "create_openai_ef",
    "create_or_get_collection",
    "get_persistent_client",
    "ingest_documents",
    "load_openai_key",
    "parse_ingestion_payload",
    "run_ingestion",
]
