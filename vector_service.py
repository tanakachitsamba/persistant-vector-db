"""Utilities for interacting with the local Chroma vector database.

This module centralises the creation of the persistent client, collection
initialization and the high level operations that a consumer of the vector
store will typically perform.  The functions can be imported and reused from
other modules or triggered through the module's command line interface via
``python -m vector_service``.

Environment variables control the behaviour of the service:

``VECTOR_PERSIST_DIRECTORY``
    Filesystem path that stores the persistent database (defaults to ``db``).
``VECTOR_COLLECTION_NAME``
    Name of the collection that operations target (defaults to ``lake``).
``VECTOR_EMBEDDING_BACKEND``
    Embedding backend to use (defaults to ``openai``). ``openai`` requires ``OPENAI_KEY`` to be
    defined, while ``simple`` uses an inexpensive hashing based embedding that
    works well for development and tests. If an invalid value is provided, an error will be raised.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-redef]
        return False

try:
    import chromadb  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - handled at runtime
    chromadb = None  # type: ignore[assignment]
    _CHROMADB_IMPORT_ERROR = exc
else:
    _CHROMADB_IMPORT_ERROR = None


DEFAULT_PERSIST_DIRECTORY = "db"
DEFAULT_COLLECTION_NAME = "lake"
DEFAULT_EMBEDDING_BACKEND = "openai"


class SimpleEmbeddingFunction:
    """Deterministic embedding function suitable for local development.

    Chroma only requires the embedding function to be callable and return a
    numeric vector.  The implementation below uses a very small feature space
    derived from the length of the provided text and the character ordinals in
    order to maintain deterministic behaviour between runs while keeping the
    implementation fully offline.
    """

    def __call__(self, texts: Sequence[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            length = float(len(text))
            checksum = sum(ord(ch) for ch in text) % 997
            vectors.append([length, float(checksum)])
        return vectors


@dataclass
class VectorConfig:
    persist_directory: str = DEFAULT_PERSIST_DIRECTORY
    collection_name: str = DEFAULT_COLLECTION_NAME
    embedding_backend: str = DEFAULT_EMBEDDING_BACKEND


def load_environment() -> None:
    """Load environment variables from a ``.env`` file if present."""

    load_dotenv()


def get_config(
    *,
    persist_directory: Optional[str] = None,
    collection_name: Optional[str] = None,
    embedding_backend: Optional[str] = None,
) -> VectorConfig:
    """Return configuration values derived from environment variables."""

    load_environment()
    return VectorConfig(
        persist_directory=persist_directory
        or os.getenv("VECTOR_PERSIST_DIRECTORY", DEFAULT_PERSIST_DIRECTORY),
        collection_name=collection_name
        or os.getenv("VECTOR_COLLECTION_NAME", DEFAULT_COLLECTION_NAME),
        embedding_backend=embedding_backend
        or os.getenv("VECTOR_EMBEDDING_BACKEND", DEFAULT_EMBEDDING_BACKEND),
    )


def _ensure_chromadb_imported() -> None:
    if chromadb is None:  # pragma: no cover - executed only when dependency missing
        raise ModuleNotFoundError(
            "chromadb is required to use the vector service"
        ) from _CHROMADB_IMPORT_ERROR


def _build_embedding_function(config: VectorConfig):
    from chromadb.utils import embedding_functions  # type: ignore

    backend = config.embedding_backend.lower()
    if backend == "openai":
        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_KEY environment variable must be set when using the"
                " OpenAI embedding backend."
            )
        return embedding_functions.OpenAIEmbeddingFunction(  # type: ignore[attr-defined]
            api_key=api_key,
            model_name=os.getenv("VECTOR_OPENAI_MODEL", "text-embedding-ada-002"),
        )
    if backend == "simple":
        return SimpleEmbeddingFunction()

    raise ValueError(
        f"Unsupported embedding backend '{config.embedding_backend}'."
        " Expected 'openai' or 'simple'."
    )


def get_client(config: Optional[VectorConfig] = None):
    """Instantiate and return the persistent Chroma client."""

    _ensure_chromadb_imported()
    cfg = config or get_config()
    return chromadb.PersistentClient(path=cfg.persist_directory)  # type: ignore[call-arg]


def get_collection(config: Optional[VectorConfig] = None):
    """Return the configured collection, creating it if necessary."""

    cfg = config or get_config()
    client = get_client(cfg)
    embedding_function = _build_embedding_function(cfg)
    return client.get_or_create_collection(  # type: ignore[no-any-return]
        name=cfg.collection_name,
        embedding_function=embedding_function,
    )


def add_documents(
    documents: Sequence[str],
    metadatas: Sequence[Dict[str, Any]],
    ids: Sequence[str],
    *,
    config: Optional[VectorConfig] = None,
) -> None:
    """Add documents to the configured collection."""

    if not (len(documents) == len(metadatas) == len(ids)):
        raise ValueError("documents, metadatas and ids must have the same length")

    collection = get_collection(config)
    collection.add(documents=list(documents), metadatas=list(metadatas), ids=list(ids))


def query_collection(
    query_text: str,
    top_k: int = 5,
    *,
    config: Optional[VectorConfig] = None,
) -> Dict[str, Any]:
    """Query the configured collection and return the raw response."""

    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")

    collection = get_collection(config)
    return collection.query(query_texts=[query_text], n_results=top_k)


def delete_documents(ids: Sequence[str], *, config: Optional[VectorConfig] = None) -> None:
    """Delete documents from the configured collection."""

    if not ids:
        raise ValueError("ids must contain at least one identifier")

    collection = get_collection(config)
    collection.delete(ids=list(ids))


def _parse_metadata(metadata_args: Iterable[str]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for raw in metadata_args:
        raw = raw.strip()
        if not raw:
            parsed.append({})
            continue
        if raw.startswith("{"):
            parsed.append(json.loads(raw))
        else:
            metadata_dict: Dict[str, Any] = {}
            for item in raw.split(","):
                if not item:
                    continue
                key, _, value = item.partition("=")
                metadata_dict[key.strip()] = value.strip()
            parsed.append(metadata_dict)
    return parsed


def _configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the Chroma vector store")
    parser.add_argument(
        "--persist-directory",
        help="Override the persistence directory used for the Chroma client",
    )
    parser.add_argument(
        "--collection-name",
        help="Override the collection name used by the Chroma client",
    )
    parser.add_argument(
        "--embedding-backend",
        choices=["openai", "simple"],
        help="Select the embedding backend (default is environment configuration)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Add documents to the collection")
    ingest.add_argument("--document", action="append", required=True, help="Document text")
    ingest.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Metadata for the document as JSON or key=value pairs",
    )
    ingest.add_argument("--id", action="append", required=True, help="Document identifier")

    query = subparsers.add_parser("query", help="Query the collection")
    query.add_argument("--text", required=True, help="Query text")
    query.add_argument("--top-k", type=int, default=5, help="Number of results to return")

    delete = subparsers.add_parser("delete", help="Delete documents from the collection")
    delete.add_argument("ids", nargs="+", help="Identifiers to delete")

    return parser


def _config_from_args(args: argparse.Namespace) -> VectorConfig:
    return get_config(
        persist_directory=args.persist_directory,
        collection_name=args.collection_name,
        embedding_backend=args.embedding_backend,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _configure_parser()
    args = parser.parse_args(argv)
    config = _config_from_args(args)

    if args.command == "ingest":
        documents = args.document
        ids = args.id
        metadatas = _parse_metadata(args.metadata)
        if len(metadatas) == 0:
            metadatas = [{} for _ in documents]
        elif len(metadatas) == 1 and len(documents) > 1:
            metadatas = [metadatas[0].copy() for _ in documents]
        if not (len(documents) == len(ids) == len(metadatas)):
            raise ValueError("Each document must have a matching id and metadata entry")
        add_documents(documents, metadatas, ids, config=config)
        print(f"Added {len(ids)} document(s) to collection '{config.collection_name}'.")
        return 0

    if args.command == "query":
        results = query_collection(args.text, args.top_k, config=config)
        print(json.dumps(results, indent=2, default=str))
        return 0

    if args.command == "delete":
        delete_documents(args.ids, config=config)
        print(f"Deleted {len(args.ids)} document(s) from collection '{config.collection_name}'.")
        return 0

    parser.error("No command provided")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
