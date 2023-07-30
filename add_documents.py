import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
import sys

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

if __name__ == "__main__":
    try:
        # Check if three command-line arguments are provided
        if len(sys.argv) != 4:
            raise ValueError("Usage: python script.py <documents> <metadatas> <ids>")

        # Extract the command-line arguments as strings
        documents = sys.argv[1]
        metadatas = sys.argv[2]
        ids = sys.argv[3]

        # Create a new Chroma client with persistence enabled.
        persist_directory = "db"
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
        print(ve)
    except chromadb.ChromaDBError as cde:
        print(f"ChromaDBError: {cde}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
