import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def password_matches(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
