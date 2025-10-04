from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from ..models.user import UserRole
from ..models.user import PyObjectId

class UserBase(BaseModel):
    """
    Base schema with common user fields.
    """
    email: EmailStr
    full_name: str
    username: str

class UserCreate(UserBase):
    """
    Schema used for creating a new user.
    It requires a password and allows setting a role and manager.
    """
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.EMPLOYEE
    manager_id: Optional[str] = None # Manager's ObjectId as a string

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    All fields are optional, so the client only sends what they want to change.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    manager_id: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    """
    Schema for returning user data from the API.
    It **never** includes the password.
    """
    id: PyObjectId = Field(alias="_id")
    company_id: PyObjectId
    role: UserRole
    manager_id: Optional[PyObjectId] = None
    is_active: bool

    class Config:
        # This is needed to handle the mapping from the UserModel object
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str # Convert ObjectId to string in JSON responses
        }

class Token(BaseModel):
    """
    Schema for the authentication token response.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema for the data encoded inside the JWT.
    """
    username: Optional[str] = None