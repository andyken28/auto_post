import os
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, BrowserContext


logger = logging.getLogger(__name__)


def _proxy_dict_from_string(proxy: Optional[str]) -> Optional[Dict[str, Any]]:
    """Convert proxy string to Playwright proxy dict.

    Supported input: "host:port" or "http://user:pass@host:port" or "http://host:port".
    Returns None if proxy is falsy.
    """
    if not proxy:
        return None
    p = proxy.strip()
    # Ensure scheme
    if not p.startswith("http"):
        p = "http://" + p

    # playwright expects dict with key 'server' and optional 'username'/'password'
    # parse manually
    from urllib.parse import urlparse
    u = urlparse(p)
    server = f"{u.scheme}://{u.hostname}:{u.port}" if u.port else f"{u.scheme}://{u.hostname}"
    res = {"server": server}
    if u.username:
        res["username"] = u.username
    if u.password:
        res["password"] = u.password
    return res


class PlaywrightManager:
    """Manage Playwright persistent contexts per account/profile.

    Usage:
        mgr = PlaywrightManager()
        ctx = await mgr.launch_persistent_context(account, profile_dir)
        page = await ctx.new_page()
        ...
        await ctx.close()
    """

    def __init__(self):
        self._pw = None

    async def __aenter__(self):
        self._pw = await async_playwright().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._pw:
            await self._pw.__aexit__(exc_type, exc, tb)

    async def launch_persistent_context(self, profile_dir: str, proxy: Optional[str] = None, user_agent: Optional[str] = None, headless: bool = False, viewport: Optional[Dict[str,int]] = None) -> BrowserContext:
        """Launch a Chromium persistent context using the given profile dir.

        - `profile_dir`: directory path to use for user data (one per account)
        - `proxy`: proxy string (see _proxy_dict_from_string)
        - `user_agent`: custom UA
        - `headless`: False for visible browser as requested
        Returns the BrowserContext; caller is responsible for closing it.
        """
        if not self._pw:
            self._pw = await async_playwright().__aenter__()

        chromium = self._pw.chromium
        os.makedirs(profile_dir, exist_ok=True)

        proxy_obj = _proxy_dict_from_string(proxy)

        launch_kwargs: Dict[str, Any] = {
            "headless": headless,
        }
        if user_agent:
            launch_kwargs["user_agent"] = user_agent
        if viewport:
            launch_kwargs["viewport"] = viewport
        if proxy_obj:
            launch_kwargs["proxy"] = proxy_obj

        # Use persistent context so each account has its own profile folder
        ctx = await chromium.launch_persistent_context(profile_dir, **launch_kwargs)
        logger.info("Launched persistent context at %s (proxy=%s)", profile_dir, proxy is not None)
        return ctx
