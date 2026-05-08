from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


def generate_token(data: str, salt: str) -> str:
    """Generate a signed, timed token for the given data."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(data, salt=salt)


def verify_token(token: str, salt: str, max_age: int = 3600) -> str | None:
    """Verify a token and return the original data, or None if invalid/expired."""
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token, salt=salt, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None
