import json
import logging
import os
from typing import Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

CATALOG_PATH = os.environ.get("ICON_CATALOG_PATH", "icons/catalog.json")


def _is_duplicate(entry: dict, catalog: list[dict]) -> bool:
    for item in catalog:
        if item.get("source_url") == entry.get("source_url"):
            return True
        h = entry.get("perceptual_hash", "")
        if h and item.get("perceptual_hash") == h:
            return True
    return False


@tool
def update_catalog(
    filename: str,
    source_url: str,
    perceptual_hash: str,
    discovered_at: str,
    tags: list[str] = [],
) -> dict[str, Any]:
    """Add a new unique icon entry to the catalog.

    Args:
        filename: Local filename of the downloaded icon
        source_url: Original URL where the icon was found
        perceptual_hash: Perceptual hash string for deduplication
        discovered_at: ISO timestamp of discovery
        tags: Optional list of tags

    Returns:
        Dict with keys: added (bool), reason (str)
    """
    entry = {
        "filename": filename,
        "source_url": source_url,
        "perceptual_hash": perceptual_hash,
        "discovered_at": discovered_at,
        "tags": tags,
    }

    os.makedirs(os.path.dirname(CATALOG_PATH) or ".", exist_ok=True)

    catalog: list[dict] = []
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r") as f:
                catalog = json.load(f)
        except Exception:
            catalog = []

    if _is_duplicate(entry, catalog):
        logger.info("M4.achieved: deduplication — duplicate skipped for %s", source_url)
        return {"added": False, "reason": "duplicate"}

    catalog.append(entry)
    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)

    total = len(catalog)
    logger.info("M5.achieved: 1 new icon appended to catalog (total: %d)", total)
    return {"added": True, "reason": "added"}
