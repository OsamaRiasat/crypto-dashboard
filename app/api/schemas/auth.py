from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    # Enforce sensible bounds; bcrypt_sha256 supports long passwords but we cap for UX
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserPublic(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: str
    role: Optional[str] = None
    created_at: datetime
