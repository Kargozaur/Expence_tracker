import hmac
import hashlib
from core.settings import settings


def hash_refresh_token(token: str) -> str:
    return hmac.new(
        key=settings.SECRET_KEY.encode(),
        msg=token.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_refresh_token(token: str, hash_token: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(token), hash_token)
