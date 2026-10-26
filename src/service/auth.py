import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from src.settings import settings

_SCHEME = "pbkdf2_sha256"


def _pbkdf2(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = settings.password_iterations
    digest = _pbkdf2(password, salt, iterations)
    return "$".join(
        [_SCHEME, str(iterations), base64.b64encode(salt).decode(), base64.b64encode(digest).decode()]
    )


def _is_legacy(password_hash: str) -> bool:
    return not password_hash.startswith(f"{_SCHEME}$")


def password_matches(password: str, password_hash: str) -> bool:
    if _is_legacy(password_hash):
        # Hashes SHA-256 sem salt de versões anteriores; regravados em needs_rehash().
        legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy, password_hash)
    try:
        _, iterations, salt, digest = password_hash.split("$")
        expected = base64.b64decode(digest)
        actual = _pbkdf2(password, base64.b64decode(salt), int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(actual, expected)


def needs_rehash(password_hash: str) -> bool:
    if _is_legacy(password_hash):
        return True
    try:
        return int(password_hash.split("$")[1]) < settings.password_iterations
    except (ValueError, IndexError):
        return True


def _session_key() -> bytes:
    return settings.session_secret.encode("utf-8")


def _sign(encoded: str) -> str:
    return hmac.new(_session_key(), encoded.encode(), hashlib.sha256).hexdigest()


def password_fingerprint(password_hash: str) -> str:
    """Muda quando a senha muda; invalida sessões emitidas antes da troca."""
    return hmac.new(_session_key(), password_hash.encode(), hashlib.sha256).hexdigest()[:16]


def create_session_token(user_id: int, user_type: str, password_hash: str) -> str:
    payload = json.dumps(
        {
            "id": user_id,
            "tipo": user_type,
            "exp": int(time.time()) + settings.session_hours * 3600,
            "pv": password_fingerprint(password_hash),
        },
        separators=(",", ":"),
    ).encode()
    encoded = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"{encoded}.{_sign(encoded)}"


def read_session_token(token: str) -> dict[str, Any] | None:
    try:
        encoded, signature = token.split(".", 1)
        if not hmac.compare_digest(signature, _sign(encoded)):
            return None
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        value = json.loads(payload)
        if (
            not isinstance(value, dict)
            or not isinstance(value.get("id"), int)
            or not isinstance(value.get("exp"), int)
            or value["exp"] < time.time()
        ):
            return None
        return value
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
