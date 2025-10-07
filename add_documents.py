"""Utilities for adding documents to a Chroma collection via the CLI."""

import argparse
import json
import os
import sys
from typing import Any

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

def load_openai_key() -> str:
    """Return the OpenAI API key loaded from the environment.

    The key is sourced from a `.env` file if present. A descriptive error is
    raised if the key cannot be found so the caller can present an actionable
    message to the user.
    """

    # Load variables from .env file into environment
    load_dotenv()
    openai_key = os.environ.get('OPENAI_KEY')
    if not openai_key:
        raise ValueError("OPENAI_KEY is not set in the .env file.")
    return openai_key

def create_openai_ef(api_key: str) -> embedding_functions.OpenAIEmbeddingFunction:
    """Create an OpenAI embedding function instance configured with ``api_key``."""

    # Using OpenAI Embeddings. This assumes you have the openai package installed
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-ada-002"
    )
    return openai_ef

def create_or_get_collection(client: "chromadb.ClientAPI",
                             embedding_function: "embedding_functions.OpenAIEmbeddingFunction"
                             ) -> "chromadb.api.models.Collection.Collection":
    """Return the ``lake`` collection configured with the supplied embedding function."""

    # Create a new chroma collection that uses the OpenAI embedding function.
    collection_name = "lake"
    return client.get_or_create_collection(name=collection_name,
                                           embedding_function=embedding_function)


def load_json_input(value: str, *, argument_name: str) -> Any:
    """Load JSON content from ``value``.

    ``value`` can either be a JSON string or a path to a file containing JSON.
    When parsing fails an actionable ``ValueError`` is raised so the caller can
    surface a helpful error message to the user.
    """

    # If ``value`` refers to a file on disk we read and parse its contents.
    if os.path.isfile(value):
        try:
            with open(value, "r", encoding="utf-8") as file_handle:
                return json.load(file_handle)
        except (OSError, json.JSONDecodeError) as err:
            raise ValueError(
                f"Unable to read JSON from file for `{argument_name}`: {err}"
            ) from err

    # Otherwise treat ``value`` as a JSON string provided directly on the CLI.
    try:
        return json.loads(value)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"Invalid JSON for `{argument_name}`. Provide a JSON string or file path."
        ) from err


def validate_payload(documents: Any, metadatas: Any, ids: Any) -> None:
    """Validate the payload prior to inserting into the collection."""

    if not isinstance(documents, list):
        raise ValueError("`documents` must be a JSON array of strings.")
    if not isinstance(ids, list):
        raise ValueError("`ids` must be a JSON array of strings.")
    if not isinstance(metadatas, list):
        raise ValueError("`metadatas` must be a JSON array of objects.")
    if not all(isinstance(item, dict) for item in metadatas):
        raise ValueError("Each metadata entry must be a JSON object (dictionary).")

    lengths: list[int] = [len(documents), len(metadatas), len(ids)]
    if len(set(lengths)) != 1:
        raise ValueError(
            "`documents`, `metadatas`, and `ids` must contain the same number of entries."
        )

def add_to_openai_collection(
    collection: "chromadb.api.models.Collection.Collection",
    documents: list[str],
    metadatas: list[dict[str, Any]],
    ids: list[str],
) -> None:
    """Insert the provided payload into ``collection`` and report basic failures."""

    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Documents added to the collection successfully.")
    except Exception as e:
        print(f"Error occurred while adding documents: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Add documents to the Chroma 'lake' collection. Arguments accept either "
            "JSON strings or paths to files containing JSON."
        )
    )
    parser.add_argument(
        "--documents",
        required=True,
        help="JSON array or file path for the documents to insert."
    )
    parser.add_argument(
        "--metadatas",
        required=True,
        help="JSON array or file path for the metadata objects accompanying each document."
    )
    parser.add_argument(
        "--ids",
        required=True,
        help="JSON array or file path for the unique identifiers of the documents."
    )

    args = parser.parse_args()

    try:
        # Convert incoming payloads into Python objects. Fail fast with helpful messages.
        documents = load_json_input(args.documents, argument_name="documents")
        metadatas = load_json_input(args.metadatas, argument_name="metadatas")
        ids = load_json_input(args.ids, argument_name="ids")

        validate_payload(documents, metadatas, ids)

        # Create a new Chroma client with persistence enabled.
        persist_directory = "db"  # this path for the db could be an arg
        client = chromadb.PersistentClient(path=persist_directory)

        # Load the OpenAI key
        openai_key = load_openai_key()

        # Create/Open OpenAI Embedding Function
        openai_ef = create_openai_ef(api_key=openai_key)

        # Create or get the Chroma collection
        openai_collection = create_or_get_collection(client, openai_ef)

        # Call the function with the provided arguments
        add_to_openai_collection(openai_collection, documents, metadatas, ids)
    except ValueError as ve:
        print(ve)
        sys.exit(1)
    except chromadb.ChromaDBError as cde:
        print(f"ChromaDBError: {cde}")
        sys.exit(2)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(3)
