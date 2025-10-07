import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import vector_service


@pytest.fixture(autouse=True)
def _reset_env(monkeypatch):
    for key in [
        "VECTOR_PERSIST_DIRECTORY",
        "VECTOR_COLLECTION_NAME",
        "VECTOR_EMBEDDING_BACKEND",
        "OPENAI_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_ingest_query_and_delete(tmp_path, monkeypatch):
    persist_dir = tmp_path / "chromadb"
    monkeypatch.setenv("VECTOR_PERSIST_DIRECTORY", str(persist_dir))
    monkeypatch.setenv("VECTOR_COLLECTION_NAME", "integration_tests")
    monkeypatch.setenv("VECTOR_EMBEDDING_BACKEND", "simple")

    docs = ["Chocolate chip cookies", "Freshly baked bread"]
    metadatas = [
        {"category": "dessert", "rating": 5},
        {"category": "bakery", "rating": 4},
    ]
    ids = ["doc_1", "doc_2"]

    vector_service.add_documents(docs, metadatas, ids)

    results = vector_service.query_collection("chocolate", top_k=1)
    assert "metadatas" in results
    assert results["ids"][0][0] == "doc_1"
    assert results["metadatas"][0][0]["category"] == "dessert"

    vector_service.delete_documents(["doc_1"])
    post_delete = vector_service.query_collection("bread", top_k=2)
    remaining_ids = post_delete["ids"][0]
    assert "doc_1" not in remaining_ids
    assert "doc_2" in remaining_ids
