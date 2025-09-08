"""Shared models and types for the Reddit Clone Backend."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model."""

    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True


class RegisterRequest(BaseModel):
    """User registration request model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20, regex=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """User login request model."""

    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""

    email: EmailStr
    confirmation_code: str = Field(..., alias="confirmationCode")
    new_password: str = Field(..., min_length=8, alias="newPassword")

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True


class AuthResponse(BaseModel):
    """Authentication response model."""

    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User response model."""

    user_id: str = Field(..., alias="userId")
    email: EmailStr
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True


class LoginResponse(BaseModel):
    """Login response model."""

    user: UserResponse
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    id_token: str = Field(..., alias="idToken")

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True
