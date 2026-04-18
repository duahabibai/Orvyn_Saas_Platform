"""Encryption utility for storing API keys and tokens securely."""
from cryptography.fernet import Fernet
from config import get_settings

settings = get_settings()

# Derive a valid Fernet key from the ENCRYPTION_KEY setting
# Fernet requires a 32-byte url-safe-base64-encoded key
import base64
import hashlib

_key = base64.urlsafe_b64encode(
    hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
)
_fernet = Fernet(_key)


def encrypt_value(value: str) -> str:
    """Encrypt a string value. Returns base64-encoded encrypted string."""
    if not value:
        return value
    return _fernet.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    """Decrypt a previously encrypted string. Returns empty string if decryption fails."""
    if not value:
        return value
    try:
        return _fernet.decrypt(value.encode()).decode()
    except Exception as e:
        # Fallback for invalid tokens or corrupted data
        import logging
        logging.getLogger(__name__).error(f"Decryption failed: {e}")
        return ""
