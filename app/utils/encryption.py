import os
from cryptography.fernet import Fernet, InvalidToken

KEY_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "encryption.key")


def load_or_create_key():
    key = os.environ.get("ENCRYPTION_KEY")
    if key:
        return key.encode()

    # Try file
    try:
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "rb") as f:
                return f.read()
        # generate and save
        k = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(k)
        return k
    except Exception:
        # fallback to generating in-memory key (not persisted)
        return Fernet.generate_key()


_KEY = load_or_create_key()
_FERNET = Fernet(_KEY)


def encrypt_text(plaintext: str) -> str:
    """Encrypt plaintext string and return as utf-8 string."""
    if plaintext is None:
        return None
    return _FERNET.encrypt(plaintext.encode()).decode("utf-8")


def decrypt_text(token: str) -> str:
    """Decrypt token string; raises InvalidToken if not valid."""
    if not token:
        return None
    try:
        return _FERNET.decrypt(token.encode()).decode("utf-8")
    except InvalidToken:
        return None
