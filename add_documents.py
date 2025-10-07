import argparse
import json
import os
import sys

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

def load_openai_key():
    # Load variables from .env file into environment
    load_dotenv()
    openai_key = os.environ.get('OPENAI_KEY')
    if not openai_key:
        raise ValueError("OPENAI_KEY is not set in the .env file.")
    return openai_key

def create_openai_ef(api_key):
    # Using OpenAI Embeddings. This assumes you have the openai package installed
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-ada-002"
    )
    return openai_ef

def create_or_get_collection(client):
    # Create a new chroma collection
    collection_name = "lake"
    return client.get_or_create_collection(name=collection_name)

def add_to_openai_collection(collection, documents, metadatas, ids):
    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Documents added to the collection successfully.")
    except Exception as e:
        print(f"Error occurred while adding documents: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Add documents to the persistent Chroma collection."
    )
    parser.add_argument("--documents", required=True, help="JSON encoded list of documents")
    parser.add_argument("--metadatas", required=True, help="JSON encoded list of metadatas")
    parser.add_argument("--ids", required=True, help="JSON encoded list of ids")
    return parser.parse_args()


def load_json_argument(value, argument_name):
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON provided for {argument_name}: {exc}") from exc


if __name__ == "__main__":
    try:
        args = parse_arguments()

        documents = load_json_argument(args.documents, "--documents")
        metadatas = load_json_argument(args.metadatas, "--metadatas")
        ids = load_json_argument(args.ids, "--ids")

        # Create a new Chroma client with persistence enabled.
        persist_directory = "db"  # this path for the db could be an arg
        client = chromadb.PersistentClient(path=persist_directory)

        # Load the OpenAI key
        openai_key = load_openai_key()

        # Create/Open OpenAI Embedding Function
        openai_ef = create_openai_ef(api_key=openai_key)

        # Create or get the Chroma collection
        openai_collection = create_or_get_collection(client)

        # Call the function with the provided arguments
        add_to_openai_collection(openai_collection, documents, metadatas, ids)
    except ValueError as ve:
        print(ve, file=sys.stderr)
        sys.exit(1)
    except chromadb.ChromaDBError as cde:
        print(f"ChromaDBError: {cde}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
