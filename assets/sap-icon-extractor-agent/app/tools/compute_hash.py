import logging
from typing import Any

import imagehash
from langchain_core.tools import tool
from PIL import Image

logger = logging.getLogger(__name__)


@tool
def compute_hash(filepath: str) -> dict[str, Any]:
    """Compute a perceptual hash of an image file for deduplication.

    Args:
        filepath: Path to the image file

    Returns:
        Dict with keys: hash (str), filepath (str)
    """
    try:
        with Image.open(filepath) as img:
            h = str(imagehash.phash(img))
        return {"hash": h, "filepath": filepath}
    except Exception as e:
        logger.warning("compute_hash failed for %s: %s", filepath, e)
        return {"hash": "", "filepath": filepath}
