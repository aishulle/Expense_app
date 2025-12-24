from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserResponse


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class GroupCreate(GroupBase):
    pass


class GroupMemberResponse(BaseModel):
    user_id: UUID
    joined_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime
    members: List[GroupMemberResponse] = []
    
    class Config:
        from_attributes = True


class GroupMemberCreate(BaseModel):
    user_id: UUID

