import json
import logging
import os
from typing import Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

CATALOG_PATH = os.environ.get("ICON_CATALOG_PATH", "icons/catalog.json")


@tool
def read_catalog() -> list[dict[str, Any]]:
    """Read the current icon catalog from disk.

    Returns:
        List of icon entries, each with keys: filename, source_url,
        perceptual_hash, discovered_at, tags
    """
    if not os.path.exists(CATALOG_PATH):
        return []
    try:
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to read catalog: %s", e)
        return []
