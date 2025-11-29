from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Literal, List
from datetime import datetime
from bson import ObjectId

# --- 1. PyObjectId Helper ---
# This class is crucial for handling MongoDB's BSON ObjectId
# and serializing it correctly as a string 'id' in the API.
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

# --- 2. Nested Location Model ---
class LastSyncedLocation(BaseModel):
    # Latitude and Longitude should typically be floats, 
    # but based on your request (x:str, y:str) we'll use strings.
    x: str = Field(..., description="Latitude or X-coordinate as string")
    y: str = Field(..., description="Longitude or Y-coordinate as string")

# --- 3. Main User Schema ---
class UserSchema(BaseModel):
    # id field: Maps to MongoDB's _id (PyObjectId handles the BSON type)
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # name: Must be a string (str)
    name: str = Field(..., min_length=3, max_length=100)
    # email + password and approval / secret token
    email: EmailStr = Field(..., description="User email (unique)")
    password: str = Field(..., min_length=8, description="Hashed password")
    secret: Optional[dict] = Field(None, description="Optional secret token info {token, expiry}")
    approved: bool = Field(False, description="Whether user is approved")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # address: Optional string
    address: Optional[str] = None
    
    # gender: Optional string
    gender: Optional[str] = None
    
    # last_synced_location: Uses the nested model
    last_synced_location: Optional[LastSyncedLocation] = None
    
    # role: Uses Literal for type-checked enumeration
    role: Literal['user', 'organiser', 'bussiness', 'admin'] = Field('user', description="User role in the system")

    class Config:
        # Pydantic Configuration
        allow_population_by_field_name = True # Allows mapping of '_id' to 'id'
        arbitrary_types_allowed = True        # Necessary for PyObjectId
        json_encoders = {ObjectId: str}       # Encodes all ObjectIds as strings for API response
        
        # Example data for documentation (Swagger/OpenAPI)
        schema_extra = {
            "example": {
                "name": "Alex Johnson",
                "email": "alex@example.com",
                "password": "<hashed-password>",
                "address": "123 Main St, City",
                "gender": "Male",
                "last_synced_location": {"x": "28.6139", "y": "77.2090"},
                "role": "user"
            }
        }