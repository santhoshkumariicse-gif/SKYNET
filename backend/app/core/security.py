from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None

def generate_audit_hmac(actor: str, action: str, resource_type: str, resource_id: str, timestamp_str: str = "", secret_key: Optional[str] = None) -> str:
    import hmac
    import hashlib
    key = (secret_key or settings.HMAC_SECRET).encode("utf-8")
    payload = f"{actor}:{action}:{resource_type}:{resource_id}".encode("utf-8")
    return hmac.new(key, payload, hashlib.sha256).hexdigest()

def verify_audit_hmac(actor: str, action: str, resource_type: str, resource_id: str, timestamp_str: str = "", signature: str = "", secret_key: Optional[str] = None) -> bool:
    import hmac
    if not signature:
        return False
    expected = generate_audit_hmac(actor, action, resource_type, resource_id, timestamp_str, secret_key)
    return hmac.compare_digest(expected, signature)


