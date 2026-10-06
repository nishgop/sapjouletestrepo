import logging
import os
import re
from typing import Any

import requests
from langchain_core.tools import tool
from PIL import Image

logger = logging.getLogger(__name__)


def _safe_filename(url: str) -> str:
    name = url.split("?")[0].split("/")[-1]
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:128] or "icon"


@tool
def download_icon(url: str, output_dir: str = "icons") -> dict[str, Any]:
    """Download an icon image from a URL to local storage.

    Args:
        url: Image URL to download
        output_dir: Local directory to save the image (default: icons/)

    Returns:
        Dict with keys: success (bool), filepath (str|None), error (str|None)
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = _safe_filename(url)
    filepath = os.path.join(output_dir, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        return {"success": True, "filepath": filepath, "error": None}

    try:
        resp = requests.get(url, timeout=10, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "image" not in content_type and not any(
            url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"]
        ):
            return {"success": False, "filepath": None, "error": f"Not an image: {content_type}"}

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)

        # Validate with Pillow (skip SVGs)
        if not url.lower().endswith(".svg"):
            try:
                with Image.open(filepath) as img:
                    img.verify()
            except Exception as e:
                os.remove(filepath)
                return {"success": False, "filepath": None, "error": f"Invalid image: {e}"}

        logger.info("M3.achieved: icon downloaded to %s", filepath)
        return {"success": True, "filepath": filepath, "error": None}
    except Exception as e:
        logger.warning("M3.missed: download failed for %s: %s", url, e)
        return {"success": False, "filepath": None, "error": str(e)}
