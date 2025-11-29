from pydantic import BaseModel, Field, validator
from typing import Optional
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

# --- Message Model for Database and API Response ---
class MessageSchema(BaseModel):
    # id field: Maps to MongoDB's _id
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # uid: User ID (sender) - Stored as a string (the ObjectId of the User)
    uid: str = Field(..., description="ID of the sending user")
    
    # cid: Community ID (chat room) - Stored as a string (the ObjectId of the Community)
    cid: str = Field(..., description="ID of the community/chat room where the message was sent")
    
    # text: The content of the message
    text: str = Field(..., max_length=1000, description="The message content")
    
    # created_at: Timestamp of when the message was sent
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('text')
    def text_not_blank(cls, v):
        if not v or not v.strip():
            raise ValueError('text cannot be empty or only whitespace')
        return v

    @validator('uid', 'cid')
    def valid_objectid_str(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('must be a valid ObjectId string')
        return v

    class Config:
        # Pydantic Configuration
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "uid": "60a7e02a1d2f3c4d5e6f7a8b",
                "cid": "60a7e02a1d2f3c4d5e6f7a8c",
                "text": "Hello everyone, welcome to the new group chat!",
            }
        }

# --- Message Model for Input (Request Body) ---
class MessageIn(BaseModel):
    # uid and cid should be passed in the path or extracted from auth in a real app,
    # but for simple input, we include them here.
    uid: str = Field(..., description="ID of the sending user")
    cid: str = Field(..., description="ID of the community/chat room")
    text: str = Field(..., max_length=1000, description="The message content")

    @validator('text')
    def text_not_blank(cls, v):
        if not v or not v.strip():
            raise ValueError('text cannot be empty or only whitespace')
        return v

    @validator('uid', 'cid')
    def valid_objectid_str(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('must be a valid ObjectId string')
        return v