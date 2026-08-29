from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
import secrets

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password:str, hashed_password:str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id:int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': str(user_id), 'exp':expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token() -> tuple[str, str, str]:
    token_id = secrets.token_urlsafe(16)
    secret = secrets.token_urlsafe(32)
    raw_token = f'{token_id}.{secret}'
    return token_id, secret, raw_token

def hash_refresh_token(token: str) -> str:
    return password_hash.hash(token)

def verify_refresh_token(token: str, hashed_token: str) -> bool:
    return password_hash.verify(token, hashed_token)

def hash_refresh_secret(secret: str) -> str:
    return password_hash.hash(secret)

def verify_refresh_secret(secret: str, token_hash: str) -> bool:
    return password_hash.verify(secret, token_hash)