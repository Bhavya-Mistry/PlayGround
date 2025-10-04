from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from ..models.approval import ConditionalRuleType
from ..models.user import PyObjectId

# --- Schemas for Conditional Rules ---

class ConditionalRuleBase(BaseModel):
    """Base schema for a conditional approval rule."""
    rule_type: ConditionalRuleType
    percentage: Optional[float] = Field(None, ge=1, le=100)
    specific_approver_id: Optional[str] = None
    
    @model_validator(mode='after')
    def check_fields_for_rule_type(self) -> 'ConditionalRuleBase':
        """Ensure the correct fields are provided for the selected rule type."""
        if self.rule_type in [ConditionalRuleType.PERCENTAGE, ConditionalRuleType.HYBRID]:
            if self.percentage is None:
                raise ValueError("Percentage is required for this rule type.")
        if self.rule_type in [ConditionalRuleType.SPECIFIC_APPROVER, ConditionalRuleType.HYBRID]:
            if self.specific_approver_id is None:
                raise ValueError("Specific approver ID is required for this rule type.")
        return self

class ConditionalRuleCreate(ConditionalRuleBase):
    """Schema for creating a conditional rule."""
    pass

class ConditionalRuleOut(ConditionalRuleBase):
    """Schema for returning a conditional rule in an API response."""
    pass

# --- Schemas for Approval Flows ---

class ApprovalFlowBase(BaseModel):
    """Base schema for an approval flow."""
    name: str
    is_manager_first_approver: bool = True
    approvers: List[str] = [] # List of User ObjectIds as strings
    conditional_rule: Optional[ConditionalRuleCreate] = None

class ApprovalFlowCreate(ApprovalFlowBase):
    """Schema for creating a new approval flow."""
    pass

class ApprovalFlowOut(ApprovalFlowBase):
    """Schema for returning an approval flow from the API."""
    id: PyObjectId = Field(alias="_id")
    company_id: PyObjectId
    conditional_rule: Optional[ConditionalRuleOut] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str
        }