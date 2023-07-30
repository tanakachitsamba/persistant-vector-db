Feature: Adding documents to the OpenAI collection

  Scenario: Successfully add documents to the collection
    Given the OpenAI key is set in the .env file
    And an OpenAI Embedding Function is created
    And a Chroma client with persistence enabled is available
    When documents, metadatas, and ids are provided
    Then the documents should be added to the collection successfully
