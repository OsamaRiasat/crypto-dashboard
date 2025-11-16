from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from app.core.config import settings
from app.core.db import get_db
from app.api.models.db import User

# Use Argon2 (modern and no 72-byte limitation)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT and current user helpers

def create_access_token(subject: int, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES * 6000
    )
    to_encode = {"sub": str(subject), "exp": expire, "iat": datetime.utcnow()}
    token = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token: Optional[str] = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Normalize token (strip spaces, optional quotes, optional Bearer prefix)
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:]
    if token.startswith('"') and token.endswith('"'):
        token = token[1:-1]

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_sub": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token signature")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Malformed token")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e.__class__.__name__}")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token: subject must be integer")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
