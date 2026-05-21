import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-change-before-deploy")
TOKEN_TTL_SECONDS = 60 * 60 * 24


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{_b64url_encode(salt)}.{_b64url_encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_b64, digest_b64 = stored_hash.split(".", 1)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = _b64url_encode(payload_json)
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    return f"{payload_b64}.{_b64url_encode(signature)}"


def decode_token(token: str) -> Optional[dict]:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
        expected_signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
        actual_signature = _b64url_decode(signature_b64)
        if not hmac.compare_digest(expected_signature, actual_signature):
            return None
        payload = json.loads(_b64url_decode(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
