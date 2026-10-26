import base64
import hashlib
import hmac
import json
import os
from typing import Any


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def password_matches(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def _session_key() -> bytes:
    return os.getenv("SESSION_SECRET", "dev-only-change-this-secret").encode("utf-8")


def create_session_token(user_id: int, user_type: str) -> str:
    payload = json.dumps({"id": user_id, "tipo": user_type}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = hmac.new(_session_key(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def read_session_token(token: str) -> dict[str, Any] | None:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(_session_key(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        value = json.loads(payload)
        if not isinstance(value, dict) or not isinstance(value.get("id"), int):
            return None
        return value
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
