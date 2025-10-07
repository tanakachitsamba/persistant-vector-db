# Persistent Vector DB

## Local development

1. Copy `.env.local.example` to `.env` and update the values with your own credentials.
2. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Behave tests when you need to exercise the existing BDD scenarios:
   ```bash
   behave
   ```

## Container workflow

The repository includes a multi-stage Docker build that compiles the Go launcher and installs the Python dependencies required by the scripts.

### Build the image

```bash
docker build -t persistent-vector-db .
```

### Run with Docker Compose

1. Copy `.env.container.example` to `.env` and set `OPENAI_KEY` (Docker Compose automatically reads `.env`).
2. Start the stack with a persistent Chroma volume:
   ```bash
   docker compose up
   ```

The compose file binds a named volume to `/app/db` so your Chroma collections survive container restarts. The `OPENAI_KEY` environment variable is injected into the container at runtime.

## Environment files

- `.env.local.example` – template for running the scripts directly on your machine.
- `.env.container.example` – template for container-based workflows; copy to `.env` before running `docker compose`.
