Feature: Adding documents to the OpenAI collection

  Scenario: Successfully add documents to the collection
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When the following documents are ingested
      | document              | metadata                                 | id    |
      | First lake document   | {"source": "behave", "category": "test"} | doc-1 |
      | Second lake document  | {"source": "behave"}                     | doc-2 |
    Then the documents should be added to the collection successfully

  Scenario: Failing when duplicate ids are provided
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When the following documents are ingested
      | document              | metadata                                 | id    |
      | Duplicate lake entry  | {"source": "behave"}                     | doc-1 |
      | Duplicate lake entry  | {"source": "behave"}                     | doc-1 |
    Then an error should be raised containing "Duplicate ids"

  Scenario: Failing when metadata JSON is invalid
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When the following documents are ingested
      | document             | metadata     | id    |
      | Broken metadata doc  | {not-json}   | doc-3 |
    Then an ingestion error should be raised

  Scenario: Failing when payload JSON is invalid
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When the payload is ingested
      """
      {invalid
      """
    Then an error should be raised containing "Invalid JSON payload provided."

  Scenario: Failing when required payload keys are missing
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When the payload is ingested
      """
      {
        "documents": ["Only document"],
        "metadatas": [{"source": "behave"}]
      }
      """
    Then an error should be raised containing "Payload is missing required keys"

  Scenario: Failing when the OpenAI key is missing
    Given the OpenAI key is not set in the environment
    When I load the OpenAI key
    Then an error should be raised containing "OPENAI_KEY is not set"
