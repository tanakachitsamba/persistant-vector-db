import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Define shared context
def before_scenario(context, scenario):
    context.documents = None
    context.metadatas = None
    context.ids = None

def after_scenario(context, scenario):
    if context.documents:
        # Clean up the collection after the test
        context.openai_collection.remove(ids=context.ids)

# Step Definitions
@given("the OpenAI key is set in the .env file")
def step_impl_load_openai_key(context):
    openai_key = os.environ.get('OPENAI_KEY')
    if not openai_key:
        raise ValueError("OPENAI_KEY is not set in the .env file.")
    context.openai_key = openai_key

@given("an OpenAI Embedding Function is created")
def step_impl_create_openai_ef(context):
    context.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=context.openai_key,
        model_name="text-embedding-ada-002"
    )

@given("a Chroma client with persistence enabled is available")
def step_impl_create_chroma_client(context):
    context.persist_directory = "db"
    context.client = chromadb.PersistentClient(path=context.persist_directory)

@when("documents, metadatas, and ids are provided")
def step_impl_provide_arguments(context):
    # Check if three command-line arguments are provided
    if len(sys.argv) != 4:
        raise ValueError("Usage: python script.py <documents> <metadatas> <ids>")

    # Extract the command-line arguments as strings
    context.documents = sys.argv[1]
    context.metadatas = sys.argv[2]
    context.ids = sys.argv[3]

    # Create or get the Chroma collection
    context.openai_collection = context.client.get_or_create_collection(name="lake")

    # Add documents to the collection
    try:
        context.openai_collection.add(
            documents=context.documents.split(","),
            metadatas=context.metadatas.split(","),
            ids=context.ids.split(",")
        )
    except Exception as e:
        context.error = e

@then("the documents should be added to the collection successfully")
def step_impl_verify_success(context):
    assert context.error is None, f"Error occurred while adding documents: {context.error}"
    assert len(context.openai_collection) == len(context.documents.split(",")), "Number of documents added is incorrect."

    # Additional assertions if required
