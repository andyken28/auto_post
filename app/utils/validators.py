import requests


def validate_proxy(proxy: str, timeout: int = 5) -> bool:
    """Validate proxy by attempting a request through it.

    Proxy can be in format http://user:pass@host:port or host:port
    Returns True if the request succeeds and returns a 200-level response.
    """
    if not proxy:
        return False

    # normalize
    if not proxy.startswith("http"):
        proxy = "http://" + proxy

    proxies = {"http": proxy, "https": proxy}
    try:
        r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=timeout)
        return 200 <= r.status_code < 300
    except Exception:
        return False
