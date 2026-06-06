from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    settings_json: Optional[str] = None

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class SettingsUpdateRequest(BaseModel):
    font_size: str = Field(default="normal", pattern="^(normal|large|xlarge)$")


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    email: Optional[str] = None
    role: str = Field(default="user", pattern="^(admin|user)$")
