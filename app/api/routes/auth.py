from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.api.models.auth import UserCreate, UserLogin, UserPublic
from app.api.models.db import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserPublic)
def signup(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    # Check uniqueness
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with email or username already exists")

    db.refresh(user)
    # Issue JWT via HttpOnly cookie only
    token = create_access_token(subject=user.id)
    # Also set cookie for automatic auth on subsequent requests
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # set True in production behind HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 6000,
    )
    return UserPublic(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )

@router.post("/login", response_model=UserPublic)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Issue JWT via HttpOnly cookie only
    token = create_access_token(subject=user.id)
    # Also set cookie for automatic auth on subsequent requests
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # set True in production behind HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 6000,
    )
    return UserPublic(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )
