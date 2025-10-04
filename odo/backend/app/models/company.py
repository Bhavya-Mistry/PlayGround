from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .user import PyObjectId

class CompanyModel(BaseModel):
    """
    Represents a company document in the MongoDB 'companies' collection.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., max_length=100)
    # The default currency for the company, e.g., "USD", "INR"
    default_currency: str = Field(..., max_length=3, min_length=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('default_currency')
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        """Ensure the currency code is always uppercase."""
        return v.upper()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "name": "Tech Solutions Inc.",
                "default_currency": "USD"
            }
        }