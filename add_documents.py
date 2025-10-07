"""Backward compatible ingestion script.

This wrapper keeps the historical ``add_documents.py`` entry-point functional
while delegating the heavy lifting to :mod:`vector_service`.  Newer workflows
should prefer the richer CLI available via ``python -m vector_service``.
"""

import json
import sys
from typing import Any, Dict

from vector_service import VectorConfig, add_documents, get_config


def _parse_metadata(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        return json.loads(raw)
    metadata: Dict[str, Any] = {}
    for item in raw.split(","):
        if not item:
            continue
        key, _, value = item.partition("=")
        metadata[key.strip()] = value.strip()
    return metadata


if __name__ == "__main__":
    try:
        if len(sys.argv) != 4:
            raise ValueError(
                "Usage: python add_documents.py <document> <metadata> <id>"
            )

        document, metadata_raw, identifier = sys.argv[1:4]
        metadata = _parse_metadata(metadata_raw)
        config: VectorConfig = get_config()
        add_documents([document], [metadata], [identifier], config=config)
        print(
            f"Document '{identifier}' ingested into collection"
            f" '{config.collection_name}'."
        )
    except Exception as exc:
        print(f"Error: {exc}")
