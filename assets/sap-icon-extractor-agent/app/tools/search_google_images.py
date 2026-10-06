import logging
import re
from datetime import datetime, timezone
from typing import Any

import requests
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_google_images(query: str, max_results: int = 100) -> list[dict[str, Any]]:
    """Search Google Images for SAP icons and return a list of image URLs.

    Args:
        query: Search query string (e.g. 'SAP icons')
        max_results: Maximum number of image URLs to return (default 100)

    Returns:
        List of dicts with keys: url, query, discovered_at
    """
    url = (
        f"https://www.google.com/search"
        f"?q={requests.utils.quote(query)}&udm=2&tbs=itp:clipart,isz:i"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error("M1.missed: Google Images search failed: %s", e)
        return []

    # Extract image URLs from the raw HTML
    img_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|svg|gif|webp)', resp.text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    results = []
    ts = datetime.now(timezone.utc).isoformat()
    for u in img_urls:
        if u not in seen and "gstatic" not in u and "google" not in u:
            seen.add(u)
            results.append({"url": u, "query": query, "discovered_at": ts})
        if len(results) >= max_results:
            break

    logger.info("M1.achieved: Google Images search completed, %d image URLs discovered", len(results))
    logger.info("M2.achieved: %d image URLs extracted from search results", len(results))
    if not results:
        logger.warning("M2.missed: No valid image URLs could be extracted from search results")
    return results
