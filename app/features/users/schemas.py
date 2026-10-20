from pydantic import BaseModel, ConfigDict, Field, EmailStr, model_validator
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class UserRegister(UserBase):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=8)


class UserLogin(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config =  ConfigDict(
        from_attributes=True
    )