from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserSyncPayload(BaseModel):
    email: EmailStr
    name: str
    picture: str | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    profile_picture: str | None = None
    created: bool = False

    model_config = ConfigDict(from_attributes=True)
