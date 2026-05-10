import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


async def save_page_screenshot(page, prefix: str = "error") -> str:
    """Save a screenshot of the given Playwright `page`.

    Returns the file path of the saved screenshot.
    """
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    screenshots_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "screenshots")
    ensure_dir(screenshots_dir)
    filename = f"{prefix}-{ts}.png"
    path = os.path.join(screenshots_dir, filename)
    try:
        await page.screenshot(path=path, full_page=True)
        logger.info("Saved screenshot %s", path)
    except Exception as e:
        logger.exception("Failed to save screenshot: %s", e)
    return path
