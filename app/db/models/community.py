from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

# Re-use the PyObjectId helper from the User model (or place it in a shared utility file)
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

# Model for data stored in MongoDB and returned via API
class CommunitySchema(BaseModel):
    # id field: Maps to MongoDB's _id
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # name: Community's display name
    name: str = Field(..., min_length=3, max_length=100)
    
    # description: Optional longer description
    description: Optional[str] = Field(None, max_length=500)
    
    # created_at: Timestamp of creation
    created_at: datetime = Field(default_factory=datetime.now)
    
    # updated_at: Timestamp of last update
    updated_at: datetime = Field(default_factory=datetime.now)
    # owner: user id who created/owns this community
    owner: str = Field(..., description="Owner user id for the community")
    # moderators: users that are moderators in this community
    moderators: Optional[list[str]] = Field(default_factory=list)

    @validator('owner')
    def valid_owner(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('owner must be a valid ObjectId string')
        return v

    class Config:
        # Pydantic Configuration
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Local Devs Group",
                "description": "A place for local Python and FastAPI developers to connect.",
            }
        }

# Model for creating a new Community (input request body)
class CommunityIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    owner: str = Field(..., description="Owner user id who creates the community")

    @validator('owner')
    def valid_owner(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('owner must be a valid ObjectId string')
        return v