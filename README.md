to run the scripts make sure you have installed all deps with:
`pip install behave chromadb python-dotenv`

to run tests run:
`behave`

## Running the Go wrapper

The Go program wraps the `add_documents.py` helper and forwards document payloads as JSON. To execute the wrapper with the sample payloads defined in `main.go`, run:

```
go run main.go
```

Ensure that:

- Python 3 is available on your `PATH`.
- The required Python dependencies are installed (`chromadb`, `python-dotenv`, etc.).
- A valid `OPENAI_KEY` environment variable is set so the Python script can initialise the embedding function.
