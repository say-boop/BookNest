from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
