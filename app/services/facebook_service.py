from typing import Optional, Dict, Any
import requests

from app.extensions import db
from database.models import FacebookAccount
from app.utils.encryption import encrypt_text, decrypt_text
from app.utils.validators import validate_proxy
import bleach


def list_accounts(search: Optional[str] = None):
    q = FacebookAccount.query
    if search:
        like = f"%{search}%"
        q = q.filter(FacebookAccount.account_name.ilike(like))
    return q.order_by(FacebookAccount.created_at.desc()).all()


def get_account(account_id: int) -> Optional[FacebookAccount]:
    return FacebookAccount.query.get(account_id)


def create_account(data: Dict[str, Any]) -> FacebookAccount:
    # sanitize user provided strings
    name = bleach.clean((data.get("account_name") or '').strip(), tags=[], strip=True)
    proxy = (data.get("proxy") or '').strip()
    ua = bleach.clean((data.get("user_agent") or '').strip(), tags=[], strip=True)

    acc = FacebookAccount(
        account_name=name,
        proxy=proxy or None,
        user_agent=ua or None,
        status=data.get("status") or "active",
    )
    raw_cookie = data.get("cookie_json")
    if raw_cookie:
        acc.set_encrypted_cookie(raw_cookie, encrypt_text)

    db.session.add(acc)
    db.session.commit()
    return acc


def update_account(account: FacebookAccount, data: Dict[str, Any]) -> FacebookAccount:
    if 'account_name' in data:
        account.account_name = bleach.clean((data.get("account_name") or '').strip(), tags=[], strip=True) or account.account_name
    if 'proxy' in data:
        account.proxy = (data.get("proxy") or '').strip() or None
    if 'user_agent' in data:
        account.user_agent = bleach.clean((data.get("user_agent") or '').strip(), tags=[], strip=True) or account.user_agent
    account.status = data.get("status") or account.status
    raw_cookie = data.get("cookie_json")
    if raw_cookie is not None:
        account.set_encrypted_cookie(raw_cookie, encrypt_text)

    db.session.commit()
    return account


def delete_account(account: FacebookAccount):
    db.session.delete(account)
    db.session.commit()


def toggle_account(account: FacebookAccount, enable: bool):
    account.status = "active" if enable else "inactive"
    db.session.commit()
    return account


def test_proxy_for_account(account: FacebookAccount) -> bool:
    return validate_proxy(account.proxy)


def test_login_for_account(account: FacebookAccount, timeout: int = 8) -> bool:
    """A lightweight login test using the decrypted cookie to request facebook mobile.

    Returns True if we get a 200 response. This is a best-effort check and
    doesn't guarantee full functionality.
    """
    cookie = account.get_decrypted_cookie(decrypt_text)
    if not cookie:
        return False

    headers = {"User-Agent": account.user_agent or "Mozilla/5.0"}
    session = requests.Session()
    # cookie expected to be raw cookie string like 'c_user=...; xs=...'
    session.headers.update(headers)
    proxies = None
    if account.proxy:
        if not account.proxy.startswith("http"):
            proxy = "http://" + account.proxy
        else:
            proxy = account.proxy
        proxies = {"http": proxy, "https": proxy}

    try:
        r = session.get("https://m.facebook.com/", headers=headers, cookies=_cookie_str_to_dict(cookie), proxies=proxies, timeout=timeout)
        return 200 <= r.status_code < 300
    except Exception:
        return False


def _cookie_str_to_dict(cookie_str: str) -> Dict[str, str]:
    result = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result
