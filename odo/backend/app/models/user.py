from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

# Helper class to handle MongoDB's ObjectId within Pydantic models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, *args, **kwargs):
        field_schema.update(type="string")


# Enum for defining user roles
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class UserModel(BaseModel):
    """
    Represents a user document in the MongoDB 'users' collection.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    company_id: PyObjectId = Field(...)
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    full_name: str = Field(..., max_length=100)
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    manager_id: Optional[PyObjectId] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Allows using MongoDB's "_id" field
        populate_by_name = True
        # Allows using ObjectId as a type
        arbitrary_types_allowed = True
        # Config for JSON schema representation in FastAPI docs
        json_schema_extra = {
            "example": {
                "company_id": "60d5ec49f78f8b8e4f5f5f5f",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "role": "employee",
                "manager_id": "60d5ec49f78f8b8e4f5f5f60",
                "is_active": True
            }
        }