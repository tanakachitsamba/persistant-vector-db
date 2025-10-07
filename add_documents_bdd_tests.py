import json
import os

from behave import given, when, then

from add_documents import (
    IngestionError,
    create_openai_ef,
    create_or_get_collection,
    get_persistent_client,
    ingest_documents,
    load_openai_key,
    parse_ingestion_payload,
)


# Hooks

def before_scenario(context, scenario):
    context.error = None
    context.result = None
    context.documents = []
    context.metadatas = []
    context.ids = []
    context.openai_collection = None


def after_scenario(context, scenario):
    if getattr(context, "openai_collection", None) and context.result:
        context.openai_collection.remove(ids=context.ids)


# Step Definitions


@given("the OpenAI key is set in the .env file")
def step_impl_openai_key_present(context):
    os.environ.setdefault("OPENAI_KEY", "test-key")
    context.openai_key = load_openai_key()


@given("the OpenAI key is not set in the environment")
def step_impl_openai_key_missing(context):
    os.environ.pop("OPENAI_KEY", None)


@given("an OpenAI Embedding Function is created")
def step_impl_create_openai_ef(context):
    context.openai_ef = create_openai_ef(api_key=context.openai_key)


@given("a Chroma client with persistence enabled is available")
def step_impl_create_chroma_client(context):
    context.persist_directory = "db"
    context.client = get_persistent_client(persist_directory=context.persist_directory)
    context.openai_collection = create_or_get_collection(context.client)


@when("I load the OpenAI key")
def step_impl_load_openai_key(context):
    try:
        context.openai_key = load_openai_key()
    except Exception as exc:  # pragma: no cover - behave captures the exception
        context.error = exc


@when("the following documents are ingested")
def step_impl_ingest_documents(context):
    documents, metadatas, ids = [], [], []
    for row in context.table:
        documents.append(row["document"])
        try:
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        except json.JSONDecodeError:
            context.error = IngestionError("Invalid metadata JSON provided.")
            return
        metadatas.append(metadata)
        ids.append(row["id"])

    context.documents = documents
    context.metadatas = metadatas
    context.ids = ids

    try:
        context.result = ingest_documents(
            context.openai_collection, documents, metadatas, ids
        )
    except Exception as exc:  # pragma: no cover - behave captures the exception
        context.error = exc


@when("the payload is ingested")
def step_impl_ingest_payload(context):
    try:
        documents, metadatas, ids = parse_ingestion_payload(context.text)
        context.documents = documents
        context.metadatas = metadatas
        context.ids = ids
        context.result = ingest_documents(
            context.openai_collection, documents, metadatas, ids
        )
    except Exception as exc:  # pragma: no cover - behave captures the exception
        context.error = exc


@then("the documents should be added to the collection successfully")
def step_impl_verify_success(context):
    assert context.error is None, f"Error occurred while adding documents: {context.error}"
    assert context.result == len(context.documents)


@then('an error should be raised containing "{message}"')
def step_impl_verify_error_message(context, message):
    assert context.error is not None, "Expected an error but none was raised."
    assert message in str(context.error)


@then("an ingestion error should be raised")
def step_impl_verify_ingestion_error(context):
    assert isinstance(context.error, IngestionError)
