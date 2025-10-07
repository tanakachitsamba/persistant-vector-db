## Vector database utilities

This project provides a tiny toolkit for managing a [Chroma](https://docs.trychroma.com/)
vector store.  The utilities support persisting embeddings locally, executing
semantic search queries and cleaning up stored documents.

### Installation

Install the required Python dependencies:

```bash
pip install chromadb python-dotenv pytest
```

### Configuration

The behaviour of the service can be tuned through environment variables or CLI
flags:

| Variable | Description | Default |
| --- | --- | --- |
| `VECTOR_PERSIST_DIRECTORY` | Directory that stores the Chroma database | `db` |
| `VECTOR_COLLECTION_NAME` | Target collection name | `lake` |
| `VECTOR_EMBEDDING_BACKEND` | `openai` (requires `OPENAI_KEY`) or `simple` | `openai` |
| `VECTOR_OPENAI_MODEL` | Optional override of the OpenAI embedding model | `text-embedding-ada-002` |

Create a `.env` file if you prefer storing the configuration locally.  For
example:

```
VECTOR_PERSIST_DIRECTORY=./db
VECTOR_COLLECTION_NAME=my_collection
VECTOR_EMBEDDING_BACKEND=simple
```

### Command line usage

All features are exposed via the `vector_service` CLI:

```bash
# Ingest a document
python -m vector_service ingest \
  --document "Chocolate chip cookies" \
  --metadata '{"category": "dessert", "rating": 5}' \
  --id recipe-1

# Run a semantic query
python -m vector_service query --text "cookie recipe" --top-k 3

# Delete stored documents
python -m vector_service delete recipe-1 recipe-2
```

Metadata values can be provided as JSON (shown above) or as comma separated
`key=value` pairs such as `--metadata category=dessert,rating=5`.

The legacy ingestion entry-point still exists for compatibility:

```bash
python add_documents.py "Chocolate chip cookies" '{"category": "dessert"}' recipe-1
```

### Programmatic usage

The `vector_service` module exposes helpers that can be imported from Python
code:

```python
from vector_service import add_documents, query_collection, delete_documents

add_documents(
    ["Chocolate chip cookies"],
    [{"category": "dessert"}],
    ["recipe-1"],
)
results = query_collection("cookies", top_k=2)
delete_documents(["recipe-1"])
```

### Tests

Run the integration tests with:

```bash
pytest
```