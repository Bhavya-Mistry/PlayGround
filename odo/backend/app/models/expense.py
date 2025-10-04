from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from .user import PyObjectId

class ExpenseCategory(str, Enum):
    """Enumeration for expense categories."""
    TRAVEL = "Travel"
    FOOD = "Food"
    OFFICE_SUPPLIES = "Office Supplies"
    OTHER = "Other"

class ApprovalStatus(str, Enum):
    """Enumeration for approval statuses."""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class ApprovalStep(BaseModel):
    """A sub-document representing a single step in the approval chain."""
    approver_id: PyObjectId
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    comment: Optional[str] = None
    decision_date: Optional[datetime] = None

class ExpenseModel(BaseModel):
    """Represents an expense document in the MongoDB 'expenses' collection."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    employee_id: PyObjectId
    company_id: PyObjectId
    
    amount: float = Field(..., gt=0) # Amount must be greater than 0
    currency: str = Field(..., max_length=3, min_length=3)
    category: ExpenseCategory
    description: Optional[str] = Field(default=None, max_length=500)
    expense_date: date
    
    # Overall status of the expense claim
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    
    receipt_image_url: Optional[str] = None
    
    # The sequential list of approvers for this expense
    approval_steps: List[ApprovalStep] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('currency')
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        """Ensure the currency code is always uppercase."""
        return v.upper()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "employee_id": "60d5ec49f78f8b8e4f5f5f5f",
                "company_id": "60d5ec49f78f8b8e4f5f5f60",
                "amount": 99.99,
                "currency": "USD",
                "category": "Food",
                "description": "Lunch meeting with client",
                "expense_date": "2025-10-04",
            }
        }