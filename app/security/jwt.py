from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWTError
from app.core.config import settings

SECRET_KEY = settings.jwt_secret_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class InvalidTokenError(Exception):
    pass


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")

        return payload

    except PyJWTError:
        raise InvalidTokenError("Invalid or expired token")
