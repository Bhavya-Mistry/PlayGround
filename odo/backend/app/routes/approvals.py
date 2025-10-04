from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Response

from ..config import get_database, Database
from ..models.approval import ApprovalFlowModel
from ..schemas.approval import ApprovalFlowCreate, ApprovalFlowOut
from ..models.user import UserModel
from .users import get_current_admin_user # Re-using our admin security dependency

router = APIRouter(
    prefix="/approval-flows",
    tags=["Approval Flows"]
)

@router.post("/", response_model=ApprovalFlowOut, status_code=status.HTTP_201_CREATED)
def create_approval_flow(
    flow_data: ApprovalFlowCreate,
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only: Create a new approval flow for the company.
    For simplicity, this system currently supports one flow per company.
    """
    existing_flow = db.approval_flows.find_one({"company_id": admin_user.company_id})
    if existing_flow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An approval flow for this company already exists. Please update the existing one."
        )

    new_flow = ApprovalFlowModel(
        **flow_data.model_dump(),
        company_id=admin_user.company_id
    )

    created_flow = db.approval_flows.insert_one(new_flow.model_dump(by_alias=True))
    flow_doc = db.approval_flows.find_one({"_id": created_flow.inserted_id})
    return flow_doc

@router.get("/", response_model=List[ApprovalFlowOut])
def get_approval_flows_for_company(
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only: Get the approval flow(s) for the admin's company.
    """
    flows = db.approval_flows.find({"company_id": admin_user.company_id})
    return list(flows)

@router.put("/{flow_id}", response_model=ApprovalFlowOut)
def update_approval_flow(
    flow_id: str,
    flow_data: ApprovalFlowCreate,
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only: Update an existing approval flow.
    """
    flow_obj_id = ObjectId(flow_id)
    
    # Ensure the flow exists and belongs to the admin's company
    existing_flow = db.approval_flows.find_one({"_id": flow_obj_id, "company_id": admin_user.company_id})
    if not existing_flow:
        raise HTTPException(status_code=404, detail="Approval flow not found or you don't have permission to edit it.")

    updated_flow = db.approval_flows.find_one_and_update(
        {"_id": flow_obj_id},
        {"$set": flow_data.model_dump()},
        return_document=True
    )
    return updated_flow

@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_approval_flow(
    flow_id: str,
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only: Delete an approval flow.
    """
    delete_result = db.approval_flows.delete_one(
        {"_id": ObjectId(flow_id), "company_id": admin_user.company_id}
    )

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Approval flow not found or you don't have permission to delete it.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)