from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime

from ..models.expense import ExpenseCategory, ApprovalStatus
from ..models.user import PyObjectId

# --- Schemas for API Responses ---

class ApprovalStepOut(BaseModel):
    """Schema for representing an approval step in an API response."""
    approver_id: str
    status: ApprovalStatus
    comment: Optional[str] = None
    decision_date: Optional[datetime] = None

class ExpenseOut(BaseModel):
    """
    Schema for returning expense data from the API.
    This is the "public" view of an expense.
    """
    id: PyObjectId = Field(alias="_id")
    employee_id: PyObjectId
    amount: float
    currency: str
    category: ExpenseCategory
    description: Optional[str]
    expense_date: date
    status: ApprovalStatus
    receipt_image_url: Optional[str] = None
    approval_steps: List[ApprovalStepOut] = []
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str # Convert ObjectId to string in JSON responses
        }

# --- Schemas for API Requests ---

class ExpenseCreate(BaseModel):
    """Schema for data required to create a new expense."""
    amount: float = Field(..., gt=0)
    currency: str
    category: ExpenseCategory
    description: Optional[str] = None
    expense_date: date

class ApprovalDecision(BaseModel):
    """Schema for an approver (Manager/Admin) to approve or reject an expense."""
    status: ApprovalStatus
    comment: Optional[str] = Field(None, max_length=500)

    @field_validator('status')
    @classmethod
    def check_valid_status(cls, v: ApprovalStatus) -> ApprovalStatus:
        """Ensure the decision is only to approve or reject, not set to pending."""
        if v == ApprovalStatus.PENDING:
            raise ValueError("Approval decision cannot be 'Pending'. Must be 'Approved' or 'Rejected'.")
        return v