from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .user import PyObjectId

class ConditionalRuleType(str, Enum):
    """Enumeration for the type of conditional approval rule."""
    PERCENTAGE = "percentage"
    SPECIFIC_APPROVER = "specific_approver"
    HYBRID = "hybrid"

class ConditionalRuleModel(BaseModel):
    """A sub-document defining a conditional approval rule."""
    rule_type: ConditionalRuleType
    
    # Required for 'percentage' and 'hybrid' rules (value from 1 to 100)
    percentage: Optional[float] = Field(None, ge=1, le=100)
    
    # Required for 'specific_approver' and 'hybrid' rules
    specific_approver_id: Optional[PyObjectId] = None

    @field_validator('percentage')
    @classmethod
    def check_percentage(cls, v, values):
        rule_type = values.data.get('rule_type')
        if rule_type in [ConditionalRuleType.PERCENTAGE, ConditionalRuleType.HYBRID] and v is None:
            raise ValueError("Percentage is required for this rule type.")
        return v
    
    @field_validator('specific_approver_id')
    @classmethod
    def check_specific_approver(cls, v, values):
        rule_type = values.data.get('rule_type')
        if rule_type in [ConditionalRuleType.SPECIFIC_APPROVER, ConditionalRuleType.HYBRID] and v is None:
            raise ValueError("Specific approver ID is required for this rule type.")
        return v


class ApprovalFlowModel(BaseModel):
    """
    Represents an approval flow document in the 'approval_flows' collection.
    This defines the entire workflow for an expense.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    company_id: PyObjectId
    name: str = Field(..., max_length=100)
    
    # A fixed, ordered list of approvers for the sequential flow
    approvers: List[PyObjectId] = []
    
    # If true, the submitting employee's direct manager is added as the first approver
    is_manager_first_approver: bool = Field(default=True)
    
    # Optional complex rule that can run in parallel or override the sequential flow
    conditional_rule: Optional[ConditionalRuleModel] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "name": "Standard Expenses under $1000",
                "company_id": "60d5ec49f78f8b8e4f5f5f60",
                "is_manager_first_approver": True,
                "approvers": ["60d5ec49f78f8b8e4f5f5f61", "60d5ec49f78f8b8e4f5f5f62"],
                "conditional_rule": {
                    "rule_type": "hybrid",
                    "percentage": 50.0,
                    "specific_approver_id": "60d5ec49f78f8b8e4f5f5f63"
                }
            }
        }