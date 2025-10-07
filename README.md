# Persistent Vector DB

Welcome! This repository is a lightweight playground for wiring together a Go-based launcher, a Python ingestion script, and a persisted [Chroma](https://www.trychroma.com/) vector store. The goal is to make it easy to drop in text, generate OpenAI embeddings, and keep everything queryable across restarts without a mountain of setup.

## Architecture at a Glance

- **Go launcher (`main.go`)** – sanity-checks your local environment and kicks off the ingestion flow.
- **Python ingestion (`add_documents.py`)** – loads environment variables, talks to Chroma, and pushes documents with OpenAI embeddings.
- **Persistent storage (`db/`)** – a Chroma-managed directory that keeps your vectors and metadata safe between runs.

Together they let you add documents, store them in Chroma with OpenAI embeddings, and (soon) plug in custom querying or API layers on top.

## Feature Highlights

- Quick-start ingestion pipeline for text + metadata using OpenAI embeddings.
- Persistent Chroma client so you can stop/restart without losing data.
- Behavior-driven tests (`behave`) to validate ingestion happy paths.
- Friendly Go wrapper for teams that prefer compiled entrypoints.

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | Needed for `add_documents.py` and tests. Use [pyenv](https://github.com/pyenv/pyenv) or your OS package manager.
| Go | 1.19 | Matches `go.mod`. Install from [go.dev](https://go.dev/dl/).
| pip | Latest | Required for Python dependencies.

### Environment Variables

Create a `.env` file in the project root (same folder as `add_documents.py`) with at least:

```env
OPENAI_KEY=sk-your-openai-key
```

The ingestion script loads this automatically. If you prefer exporting variables manually, run `export OPENAI_KEY=...` in your shell before launching.

### Python Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# Install dependencies directly:
pip install behave chromadb python-dotenv openai
```

(We will consolidate these into a `requirements.txt` shortly.)

### Go Modules

The Go launcher uses modules, so ensure dependencies are synced:

```bash
go mod tidy
```

## Ingesting Documents (Step-by-Step)

1. Activate your virtual environment and ensure `OPENAI_KEY` is set.
2. Prepare your payload. The script expects JSON-encoded strings for documents, metadata, and IDs. For example:

   ```bash
   python add_documents.py \
     '["Tomatoes", "Jollof rice"]' \
     '[{"topic": "ingredients"}, {"topic": "recipes"}]' \
     '["doc-1", "doc-2"]'
   ```

3. Check the console for a success message. If you peek into the `db/` directory, you’ll see the persisted Chroma files.

## Querying the Vector Store

We’re iterating on a dedicated query script. In the meantime, you can explore the stored vectors directly inside a Python REPL:

```python
import chromadb
client = chromadb.PersistentClient(path="db")
collection = client.get_collection("lake")
results = collection.query(
    query_texts=["What ingredients do I need for jollof?"],
    n_results=3,
)
print(results)
```

## Running Tests

We use `behave` for end-to-end ingestion scenarios:

```bash
behave
```

The feature files live in `bdd_tests.feature`, and supporting steps are in `add_documents_bdd_tests.py`.

## Operating with Go

Once your Python environment is ready, you can drive ingestion from Go:

```bash
go run .
```

`main.go` will verify that `python3` is available and invoke the Python script with sample payloads. Customize the command arguments in `main.go` to wire in your own document sources.

## Docker & CI (Roadmap)

Container images and CI workflows are on the roadmap. When they land, the workflow will look like:

1. Build the image: `docker build -t persistent-vector-db .`
2. Run ingestion: `docker run --env OPENAI_KEY=... persistent-vector-db`
3. Add a CI job that executes `behave` and any Go unit tests.

We’ll update this section with concrete commands and sample GitHub Actions once the infrastructure lands.

## Troubleshooting

- **"OPENAI_KEY is not set"** – Make sure your `.env` file exists and contains the key, or export it in your shell. Restart your terminal so `python-dotenv` can find it.
- **Chroma connection errors** – Confirm the `db/` directory is writable. You can delete it to reset the store (`rm -rf db/`) if you’re experimenting.
- **Go launcher can’t find Python** – Install Python 3.10+ and ensure it’s on your `PATH` (`python3 --version`).
- **Embedding model errors** – The default is `text-embedding-ada-002`. Verify your OpenAI account has access, or update the model name in `add_documents.py` if needed.

## What’s Next?

- A polished query CLI and API examples.
- Requirements and Docker files for one-command setup.
- Expanded test coverage, including CI configuration.

Thanks for exploring! If you run into rough edges or have feature ideas, open an issue—we’d love the feedback.
