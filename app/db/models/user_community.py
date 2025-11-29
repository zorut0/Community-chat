from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

# Re-use the PyObjectId helper (or import from a shared utility/model file)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# --- User Community Membership Model ---
class UserCommunitySchema(BaseModel):
    # id field: Maps to MongoDB's _id
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # uid: User ID (The member)
    uid: str = Field(..., description="ID of the user who is a member")
    
    # cid: Community ID (The group they joined)
    cid: str = Field(..., description="ID of the community the user belongs to")
    
    # --- Recommended addition: Add Metadata to justify a separate collection ---
    # joined_at: Tracks when the membership began
    joined_at: datetime = Field(default_factory=datetime.now)
    
    # membership_role: The user's role *within* this specific community
    role: Literal['member', 'moderator', 'owner'] = Field('member', description="User's role within the specific community")


    class Config:
        # Pydantic Configuration
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "uid": "60a7e02a1d2f3c4d5e6f7a8b",
                "cid": "60a7e02a1d2f3c4d5e6f7a8c",
                "role": "member",
            }
        }

# --- Model for creating a new Membership (Input Request Body) ---
class UserCommunityIn(BaseModel):
    uid: str = Field(..., description="ID of the user joining")
    cid: str = Field(..., description="ID of the community to join")
    # Note: joined_at and role are set by default in the DB/Service logic
    